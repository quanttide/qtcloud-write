from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import ArticleIn, Article, ReviewOut, ParagraphReview, Suggestion
from app.store import style_store
from app.services.review import review_article

app = FastAPI(title="写作云 Provider", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/review", response_model=ReviewOut)
async def review(article_in: ArticleIn):
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
