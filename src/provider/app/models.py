from pydantic import BaseModel, Field
from typing import Optional


class ArticleIn(BaseModel):
    title: str
    paragraphs: list[str]
    author: str
    tag: str  # "good" | "bad" | "external"


class Comparison(BaseModel):
    type: str  # "good" | "bad" | "pass"
    issue: Optional[str] = None
    demo: Optional[str] = None


class ParagraphReview(BaseModel):
    original: str
    analysis: str
    tag: str  # "起" | "承" | "转" | "合"
    comparison: Optional[Comparison] = None


class Suggestion(BaseModel):
    priority: int
    action: str
    detail: str


class ReviewOut(BaseModel):
    article_title: str
    author: str
    tag: str
    summary: str
    paragraphs: list[ParagraphReview]
    is_style_available: bool
    suggestions: list[Suggestion] = Field(default_factory=list)


class Article(BaseModel):
    id: str
    title: str
    paragraphs: list[str]
    author: str
    tag: str
