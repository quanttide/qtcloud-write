from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    ArticleIn, TextIn, Article,
    ReviewOut, Review3ROut, GapAnalysis, RewriteOut, CycleOut,
    ParagraphReview, Suggestion,
)
from app.store import style_store
from app.services.review import review_article
from app.services.reflect import cmd_reflect as reflect_cmd
from app.services.rewrite import cmd_rewrite as rewrite_cmd
from app.services.llm import call_llm

app = FastAPI(title="写作云 Provider", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    import json
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


@app.post("/review", response_model=ReviewOut)
def review(article_in: ArticleIn):
    try:
        art = Article(
            id="",
            title=article_in.title,
            paragraphs=article_in.paragraphs,
            author=article_in.author,
            tag=article_in.tag,
        )
        if article_in.tag == "good":
            style_store.add_good(art)

        is_style = style_store.is_available
        para_reviews, raw_suggestions = review_article(art, is_style, style_store.good_articles)
        suggestions = [Suggestion(**s) for s in raw_suggestions]

        if article_in.tag == "good":
            summary = "好文章，叙事结构清晰。"
        elif not is_style:
            summary = "风格还在积累中，暂无法对比好/坏。"
        else:
            summary = "根本问题不是'写得不好'，而是用了另一套写作引擎——好的文章从个人困境出发推演，本文从外部热点出发分析。"

        return ReviewOut(
            article_title=article_in.title,
            author=article_in.author,
            tag=article_in.tag,
            summary=summary,
            paragraphs=para_reviews,
            is_style_available=is_style,
            suggestions=suggestions,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/reflect", response_model=list[GapAnalysis])
def reflect(body: TextIn):
    try:
        review_3r = cmd_review_3r(body.text)
        gaps = reflect_cmd(body.text, review_3r.genre, review_3r.intent, review_3r.stage)
        return [GapAnalysis(**g) for g in gaps]
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/rewrite", response_model=RewriteOut)
def rewrite(body: TextIn):
    try:
        review_3r = cmd_review_3r(body.text)
        gaps = reflect_cmd(body.text, review_3r.genre, review_3r.intent, review_3r.stage)
        result = rewrite_cmd(body.text, review_3r.genre, review_3r.intent, gaps)
        return RewriteOut(text=result, length=len(result))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/cycle", response_model=CycleOut)
def cycle(body: TextIn):
    try:
        review_3r = cmd_review_3r(body.text)
        gaps = reflect_cmd(body.text, review_3r.genre, review_3r.intent, review_3r.stage)
        rewritten = rewrite_cmd(body.text, review_3r.genre, review_3r.intent, gaps)
        return CycleOut(
            review=review_3r,
            reflect=[GapAnalysis(**g) for g in gaps],
            rewrite=RewriteOut(text=rewritten, length=len(rewritten)),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
