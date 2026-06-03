import json
import logging
import logging.handlers
from pathlib import Path

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.models import (
    TextIn, ReviewOut, Review3ROut, GapAnalysis, RewriteRequest, RewriteOut,
    ParagraphReview, Comparison, Suggestion, StyleUsage,
    StyleSample, ReviewOptions, Location,
)
from app.services.llm import call_llm
from app.services.reflect import cmd_reflect as reflect_cmd
from app.services.rewrite import cmd_rewrite as rewrite_cmd
from app.services.review import review_article


class ReviewRequest(BaseModel):
    title: str
    paragraphs: list[str]
    style_samples: list[StyleSample] | None = None
    options: ReviewOptions | None = None

# 日志配置
settings = get_settings()
log_dir = Path(settings.data_dir)
log_dir.mkdir(parents=True, exist_ok=True)
handler = logging.handlers.TimedRotatingFileHandler(
    str(log_dir / "provider.log"), when="midnight", backupCount=7, encoding="utf-8"
)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

app = FastAPI(title="写作云 Provider", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


REVIEW_PROMPT = """请阅读下面的文章片段，从写作意图的角度分析它。

输出 JSON：
{{
  "summary": "一句话总结这段文本在干什么（30字以内）"
}}

文章：
{text}"""

REVIEW_WITH_STYLE_PROMPT = """请阅读下面的文章片段，从写作意图的角度分析它，并与提供的风格样本进行对比。

风格样本：
{styles}

输出 JSON：
{{
  "summary": "一句话总结这段文本在干什么，包括与风格的对比结论（50字以内）"
}}

文章：
{text}"""


def _format_styles(style_samples: list[StyleSample]) -> str:
    return "\n\n".join(
        f"样本「{s.name}」：\n" + "\n".join(s.paragraphs)
        for s in style_samples
    )


def cmd_review(text: str, style_samples: list[StyleSample] | None = None) -> tuple[str, StyleUsage | None]:
    if style_samples:
        styles_text = _format_styles(style_samples)
        prompt = REVIEW_WITH_STYLE_PROMPT.format(text=text, styles=styles_text)
        usage = StyleUsage(
            samples_used=[s.name for s in style_samples],
            confidence=0.8,
        )
    else:
        prompt = REVIEW_PROMPT.format(text=text)
        usage = None

    raw = call_llm(prompt, system="你是一个写作意图分析专家。", temperature=0.3)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    return data.get("summary", ""), usage


# ── 请求模型（不在 models.py 中，因为是与端点绑定的输入格式）──

class ReviewRequest(BaseModel):
    title: str
    paragraphs: list[str]
    style_samples: list[StyleSample] | None = None
    options: ReviewOptions | None = None


@app.post("/review", response_model=ReviewOut, response_model_exclude_none=True)
def review(body: ReviewRequest):
    try:
        opts = body.options or ReviewOptions()
        summary, style_usage = cmd_review(
            "\n".join(body.paragraphs),
            body.style_samples or None,
        )

        para_reviews, raw_suggestions = review_article(
            body.paragraphs,
            body.style_samples,
            opts.max_paragraphs_to_compare,
        )
        suggestions = [Suggestion(**s) for s in raw_suggestions] if opts.include_suggestions else []

        return ReviewOut(
            article_title=body.title,
            summary=summary,
            paragraphs=para_reviews,
            suggestions=suggestions,
            style_usage=style_usage,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/reflect", response_model=list[GapAnalysis])
def reflect(body: TextIn):
    try:
        review_3r = cmd_review_3r(body.text)
        gaps = reflect_cmd(body.text, review_3r.genre, review_3r.intent, review_3r.stage)
        return [
            GapAnalysis(
                gap_id=g.get("gap_id", f"gap_{i:03d}"),
                gap_type=g.get("gap_type", "unknown"),
                location=Location(
                    start_char=g.get("location", {}).get("start_char", 0),
                    end_char=g.get("location", {}).get("end_char", 0),
                    text_snippet=g.get("location", {}).get("text_snippet", ""),
                ),
                detail=g.get("detail", ""),
                multi_dimensions=g.get("multi_dimensions", {}),
                craft=g.get("craft", "无意识忽略"),
                root_cause=g.get("root_cause", ""),
                suggested_fix=g.get("suggested_fix", ""),
            )
            for i, g in enumerate(gaps)
        ]
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/rewrite", response_model=RewriteOut)
def rewrite(body: RewriteRequest):
    try:
        review_3r = cmd_review_3r(body.text)
        all_gaps = reflect_cmd(body.text, review_3r.genre, review_3r.intent, review_3r.stage)

        # 如果 gaps_to_fix 未指定，默认修复所有非有意留白
        if body.gaps_to_fix is None:
            body.gaps_to_fix = [g.get("gap_id", f"gap_{i:03d}") for i, g in enumerate(all_gaps) if g.get("craft") != "有意识留白"]

        new_text, changes, unfixed = rewrite_cmd(
            body.text,
            review_3r.genre,
            review_3r.intent,
            all_gaps,
            body.gaps_to_fix,
        )
        return RewriteOut(text=new_text, length=len(new_text), changes=changes, unfixed_gaps=unfixed)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


REVIEW_3R_PROMPT = """请阅读下面的文章片段，从写作意图的角度分析它。

不需要找问题。只需要理解这段文本在做什么。

输出 JSON：
{{
  "genre": "场景体裁分类（如：重逢场景/日常对话/情感释放/事件驱动），10字以内",
  "intent": "作者的创作意图（如：营造暧昧氛围/推进人物关系/展示角色性格），20字以内",
  "stage": "根据文本呈现出来的完成度，判断这是初稿还是成稿，以及一句话依据",
  "summary": "一句话总结这段文本在干什么（30字以内）"
}}

文章：
{text}"""


def cmd_review_3r(text: str) -> Review3ROut:
    prompt = REVIEW_3R_PROMPT.format(text=text)
    raw = call_llm(prompt, system="你是一个写作意图分析专家。", temperature=0.3)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    return Review3ROut(
        genre=data.get("genre", "未知"),
        intent=data.get("intent", "未知"),
        stage=data.get("stage", "未知"),
        summary=data.get("summary", ""),
    )
