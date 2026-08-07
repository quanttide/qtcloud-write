import json
import logging
import logging.handlers
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.models import (
    Style, ReviewRequest, ReviewResponse, DimensionAlignment, Deviation,
    AnalyzeRequest, AnalyzeResponse, FixStrategy,
    InspireRequest, InspireResponse, Inspiration,
)
from app.services.llm import call_llm

settings = get_settings()
log_dir = Path(settings.data_dir)
log_dir.mkdir(parents=True, exist_ok=True)
handler = logging.handlers.TimedRotatingFileHandler(
    str(log_dir / "provider.log"), when="midnight", backupCount=7, encoding="utf-8"
)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

app = FastAPI(title="写作云 Provider", version="0.2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _dimensions_text(style: Style) -> str:
    lines = []
    for d in style.dimensions:
        lines.append(f"## {d.title}")
        lines.append(d.description)
        lines.append(f"  置信度: {d.confidence}")
        if d.clues:
            lines.append("  线索:")
            for c in d.clues:
                lines.append(f"    - {c}")
    return "\n".join(lines)


def _excerpts_text(style: Style) -> str:
    lines = []
    for ex in style.excerpts:
        lines.append(f"[{ex.dimension}] {ex.paragraph}")
        if ex.note:
            lines.append(f"  注: {ex.note}")
    return "\n".join(lines)


REVIEW_PROMPT = """你是一个风格分析助手。用户提供一篇文本和一个风格模型（含多个维度），请评估文本在每一个维度上与风格的对齐程度。

输出 JSON，格式如下，不要额外文字：
{{
  "dimension_alignments": [
    {{
      "dimension_title": "情感表达",
      "alignment_score": 0.35,
      "deviations": [
        {{
          "location": "原文片段",
          "explanation": "偏差解释",
          "suggested_alignment": "建议的改写"
        }}
      ]
    }}
  ],
  "overall_summary": "一句话总结整体对齐情况"
}}

风格模型：
标题：{style_title}
{style_desc}

维度：
{dimensions}

风格范例：
{excerpts}

待评估文本：
{text}"""


ANALYZE_PROMPT = """你是一个写作诊断专家。用户提供文本、风格模型，以及需要深度分析的具体维度。请分析该维度上文本与风格的差距。

输出 JSON，格式如下，不要额外文字：
{{
  "original_pattern": {{
    "description": "文本当前的模式",
    "example": "文本中的具体例子"
  }},
  "expected_pattern": {{
    "description": "风格期望的模式",
    "example": "风格范例中的示范"
  }},
  "gap_analysis": {{
    "root_cause": "根本原因",
    "impact": "对读者的影响"
  }},
  "fix_strategies": [
    {{"strategy": "策略名称", "example": "具体示例"}}
  ],
  "suggested_next_steps": "建议"
}}

待分析维度：{dim_title}
维度描述：{dim_desc}

风格范例：
{excerpts}

文本：
{text}"""


INSPIRE_PROMPT = """你是一个写作创意助手。用户提供原文和一个风格模型，请生成多个启发式修改建议，使原文更好地对齐该风格的特定维度。

每个建议应是一个具体的改写片段，不是全文替换。

多样性要求：{variety_text}

输出 JSON，格式如下，不要额外文字：
{{
  "inspirations": [
    {{
      "id": "insp_001",
      "title": "建议标题",
      "description": "建议说明",
      "suggested_snippet": "具体的改写片段",
      "applies_to": "适用于原文的位置",
      "target_dimension": "对齐的目标维度",
      "alignment_impact": {{"维度名": 0.85}}
    }}
  ]
}}

目标维度：{target_dims}

风格模型：
{style_desc}

风格范例：
{excerpts}

原文：
{text}"""


@app.post("/review", response_model=ReviewResponse)
def review(body: ReviewRequest):
    try:
        prompt = REVIEW_PROMPT.format(
            style_title=body.style.title,
            style_desc=body.style.description or "",
            dimensions=_dimensions_text(body.style),
            excerpts=_excerpts_text(body.style),
            text=body.text,
        )
        raw = call_llm(prompt, system="你是一个风格分析助手。", temperature=0.3)
        data = json.loads(raw)

        alignments = []
        for a in data.get("dimension_alignments", []):
            deviations = [Deviation(**d) for d in a.get("deviations", [])]
            alignments.append(DimensionAlignment(
                dimension_title=a.get("dimension_title", ""),
                alignment_score=a.get("alignment_score", 0.0),
                deviations=deviations,
            ))

        return ReviewResponse(
            dimension_alignments=alignments,
            overall_summary=data.get("overall_summary", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest):
    try:
        dim = next((d for d in body.style.dimensions if d.title == body.dimension_title), None)
        dim_desc = dim.description if dim else body.dimension_title

        prompt = ANALYZE_PROMPT.format(
            dim_title=body.dimension_title,
            dim_desc=dim_desc,
            excerpts=_excerpts_text(body.style),
            text=body.text,
        )
        raw = call_llm(prompt, system="你是一个写作诊断专家。", temperature=0.3)
        data = json.loads(raw)

        return AnalyzeResponse(
            dimension_title=body.dimension_title,
            original_pattern=data.get("original_pattern", {}),
            expected_pattern=data.get("expected_pattern", {}),
            gap_analysis=data.get("gap_analysis", {}),
            fix_strategies=[FixStrategy(**s) for s in data.get("fix_strategies", [])],
            suggested_next_steps=data.get("suggested_next_steps", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/inspire", response_model=InspireResponse)
def inspire(body: InspireRequest):
    try:
        variety_map = {"conservative": "贴近原文，小幅调整", "balanced": "平衡创新与保留", "creative": "大胆改写，探索多种可能性"}
        variety_text = variety_map.get(body.variety, "平衡创新与保留")
        target_dims = "、".join(body.target_dimensions) if body.target_dimensions else "所有维度"

        prompt = INSPIRE_PROMPT.format(
            style_desc=_dimensions_text(body.style),
            excerpts=_excerpts_text(body.style),
            target_dims=target_dims,
            variety_text=variety_text,
            text=body.text,
        )
        raw = call_llm(prompt, system="你是一个写作创意助手。", temperature=body.temperature)
        data = json.loads(raw)

        inspirations = [Inspiration(**i) for i in data.get("inspirations", [])]
        return InspireResponse(
            original_text=body.text,
            inspirations=inspirations,
            usage_note="这些是启发建议，你可以直接使用、组合或修改其中元素。",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
