import json
import logging
import logging.handlers
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.models import (
    Criterion, ReviewRequest, ReviewResponse, CriterionAnalysis, Deviation,
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


def _format_criteria(criteria: list[Criterion]) -> str:
    parts = []
    for c in criteria:
        if c.type == "positive_example":
            parts.append(f"正面范例「{c.name or c.id}」：{c.content}")
        elif c.type == "negative_example":
            parts.append(f"反面范例「{c.name or c.id}」：{c.content}")
        elif c.type == "constraint":
            parts.append(f"约束「{c.name or c.id}」：{c.description or c.content}")
    return "\n\n".join(parts)


REVIEW_PROMPT = """你是一个文本对比助手。用户提供一篇文本（TEXT）和若干准则（CRITERIA）。

每个准则可能是正面范例（positive_example）、反面范例（negative_example）或约束（constraint）。

对于每个准则：
- positive_example：评估 TEXT 在多大程度上体现了该范例的风格/特征。给出 0-1 分数（1=完全一致），指出具体偏差位置和建议。
- negative_example：评估 TEXT 在多大程度上避免了该范例的特征。分数越高越好（1=完全不相似）。指出哪里仍然像反面范例。
- constraint：评估 TEXT 是否满足约束，若不满足指出位置和建议。

输出 JSON，格式如下，不要额外文字：
{{
  "criteria_analysis": [
    {{
      "criterion_id": "c1",
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
  "overall_summary": "一句话总结"
}}

TEXT：
{text}

CRITERIA：
{criteria}"""


ANALYZE_PROMPT = """你是一个写作诊断专家。用户提供一个文本片段和一个准则，请进行深度分析。

输出 JSON，格式如下，不要额外文字：
{{
  "analysis_type": "pattern_contrast",
  "original_pattern": {{
    "description": "当前文本的模式描述",
    "example_from_text": "文本中的具体例子"
  }},
  "expected_pattern": {{
    "description": "准则期望的模式描述",
    "example_from_criterion": "准则中的示范"
  }},
  "gap_analysis": {{
    "root_cause": "根本原因分析",
    "psychological_impact": "对读者的心理影响",
    "structural_role": "在文中的结构作用"
  }},
  "fix_strategies": [
    {{
      "strategy": "策略名称",
      "example": "具体的修改示例"
    }}
  ],
  "suggested_next_steps": "下一步建议"
}}

偏差描述：{deviation_desc}

准则：
{name}（{type}）
{content_desc}

文本：
{text}"""


INSPIRE_PROMPT = """你是一个写作创意助手。用户提供一篇原文和若干准则，请生成多个不同的启发式修改建议。

每个建议应是一个具体的改写片段，不是全文替换。用户会自行选择、组合或修改这些建议。

多样性要求：{variety_text}
关注领域：{focus_text}

输出 JSON，格式如下，不要额外文字：
{{
  "inspirations": [
    {{
      "id": "insp_001",
      "title": "简短标题",
      "description": "建议说明",
      "suggested_snippet": "具体的改写片段",
      "applies_to": "适用于原文的位置说明",
      "changes_summary": "修改内容摘要",
      "alignment_impact": {{
        "c1": 0.85
      }}
    }}
  ]
}}

原文：
{text}

准则：
{criteria}"""


# ── 辅助 ────────────────────────────────────────────────

def _criteria_text(criteria: list[Criterion]) -> str:
    lines = []
    for c in criteria:
        if c.type == "positive_example":
            lines.append(f"  - {c.id} (正面范例, weight={c.weight}): {c.content}")
        elif c.type == "negative_example":
            lines.append(f"  - {c.id} (反面范例, weight={c.weight}): 避免类似 {c.content}")
        elif c.type == "constraint":
            lines.append(f"  - {c.id} (约束, weight={c.weight}): {c.description or c.content}")
    return "\n".join(lines)


# ── 端点 ────────────────────────────────────────────────

@app.post("/review", response_model=ReviewResponse)
def review(body: ReviewRequest):
    try:
        prompt = REVIEW_PROMPT.format(
            text=body.text,
            criteria=_format_criteria(body.criteria),
        )
        raw = call_llm(prompt, system="你是一个文本对比分析助手。", temperature=0.3)
        data = json.loads(raw)

        analyses = []
        for a in data.get("criteria_analysis", []):
            deviations = [Deviation(**d) for d in a.get("deviations", [])]
            analyses.append(CriterionAnalysis(
                criterion_id=a.get("criterion_id", ""),
                alignment_score=a.get("alignment_score", 0.0),
                deviations=deviations,
            ))

        return ReviewResponse(
            criteria_analysis=analyses,
            overall_summary=data.get("overall_summary", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest):
    try:
        c = body.criterion
        content_desc = c.content if c.type != "constraint" else c.description
        prompt = ANALYZE_PROMPT.format(
            name=c.name or c.id,
            type=c.type,
            content_desc=content_desc,
            deviation_desc=body.deviation_description or "未提供",
            text=body.text,
        )
        raw = call_llm(prompt, system="你是一个写作诊断专家。", temperature=0.3)
        data = json.loads(raw)

        return AnalyzeResponse(
            criterion_id=c.id,
            analysis_type=data.get("analysis_type", "pattern_contrast"),
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
        focus_text = "、".join(body.focus_areas) if body.focus_areas else "无特定限制"

        prompt = INSPIRE_PROMPT.format(
            text=body.text,
            criteria=_criteria_text(body.criteria),
            variety_text=variety_text,
            focus_text=focus_text,
        )
        raw = call_llm(prompt, system="你是一个写作创意助手。", temperature=body.temperature)
        data = json.loads(raw)

        inspirations = [Inspiration(**i) for i in data.get("inspirations", [])]
        return InspireResponse(
            original_text=body.text,
            inspirations=inspirations,
            usage_note="这些是启发建议，你可以直接使用、组合或修改其中元素。最终文本请自行整合。",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
