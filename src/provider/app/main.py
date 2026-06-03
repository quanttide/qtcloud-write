import json
import logging
import logging.handlers
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.models import (
    Criterion, ReviewRequest, ReviewResponse, CriterionAnalysis, Deviation,
    ReflectRequest, ReflectResponse, ReflectIssue,
    RewriteRequest, RewriteResponse, RewriteChange,
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


REFLECT_PROMPT = """你是一个写作诊断专家。用户提供一个文本片段和一个准则，请深入分析该文本与准则的差异。

输出 JSON，格式如下，不要额外文字：
{{
  "analysis": {{
    "patterns_found": ["当前文本的模式"],
    "patterns_expected": ["准则中期望的模式"],
    "gap_description": "差异描述",
    "sample_illustration": "准则中的示范"
  }},
  "specific_issues": [
    {{
      "location": "问题位置",
      "issue": "问题描述",
      "fix_suggestion": "修改建议"
    }}
  ]
}}

准则：
{name}（{type}）
{content_desc}

文本：
{text}"""


REWRITE_PROMPT = """你是一个文本改写助手。用户提供一篇文本、若干准则（含权重）和一个改写策略。

请修改文本以更好地满足所有准则，保留原意。

策略说明：
- weighted_sum：按权重综合考虑所有准则，权重越高的准则优先满足
- prioritize_first：优先满足第一个准则，在不违背原意的前提下尽量兼顾其他
- avoid_negative：首要目标是避免与反面范例相似，其次才是接近正面范例

输出 JSON，格式如下，不要额外文字：
{{
  "rewritten_text": "修改后的完整文本",
  "alignment_scores": {{
    "c1": 0.85,
    "c2": 0.72
  }},
  "changes": [
    {{
      "criterion_id": "c1",
      "original_snippet": "原文中被替换的部分",
      "new_snippet": "替换后的文本"
    }}
  ]
}}

原文：
{text}

准则（含权重）：
{criteria}

策略：{strategy}
{length_note}"""


# ── 辅助 ────────────────────────────────────────────────

def _criteria_for_prompt(criteria: list[Criterion]) -> tuple[str, str]:
    """返回 (review格式的文本, rewrite格式的文本)"""
    lines = []
    for c in criteria:
        if c.type == "positive_example":
            lines.append(f"  - {c.id} ({c.type}, weight={c.weight}): {c.content}")
        elif c.type == "negative_example":
            lines.append(f"  - {c.id} ({c.type}, weight={c.weight}): 避免类似 {c.content}")
        elif c.type == "constraint":
            lines.append(f"  - {c.id} ({c.type}, weight={c.weight}): {c.description or c.content}")
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


@app.post("/reflect", response_model=ReflectResponse)
def reflect(body: ReflectRequest):
    try:
        c = body.criterion
        content_desc = c.content if c.type != "constraint" else c.description
        prompt = REFLECT_PROMPT.format(
            name=c.name or c.id,
            type=c.type,
            content_desc=content_desc,
            text=body.text,
        )
        raw = call_llm(prompt, system="你是一个写作诊断专家。", temperature=0.3)
        data = json.loads(raw)

        issues = [ReflectIssue(**i) for i in data.get("specific_issues", [])]
        return ReflectResponse(
            criterion_id=c.id,
            analysis=data.get("analysis", {}),
            specific_issues=issues,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/rewrite", response_model=RewriteResponse)
def rewrite(body: RewriteRequest):
    try:
        criteria_text = _criteria_for_prompt(body.criteria)
        length_note = "尽量保持原文长度不变。" if body.preserve_original_length else ""

        prompt = REWRITE_PROMPT.format(
            text=body.text,
            criteria=criteria_text,
            strategy=body.strategy,
            length_note=length_note,
        )
        raw = call_llm(prompt, system="你是一个文本改写助手。", temperature=0.4)
        data = json.loads(raw)

        changes = [RewriteChange(**c) for c in data.get("changes", [])]
        return RewriteResponse(
            original_text=body.text,
            rewritten_text=data.get("rewritten_text", body.text),
            alignment_scores=data.get("alignment_scores", {}),
            changes=changes,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
