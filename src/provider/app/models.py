from pydantic import BaseModel, Field
from typing import Optional

MAX_INPUT_LENGTH = 8000


class ArticleIn(BaseModel):
    title: str
    paragraphs: list[str]
    author: str
    tag: str  # "good" | "bad" | "external"


class TextIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)


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


class Review3ROut(BaseModel):
    genre: str
    intent: str
    stage: str
    summary: str


class GapAnalysis(BaseModel):
    gap_type: str
    location: str
    line: int = 0
    detail: str
    structure: str
    psychology: str
    reader: str
    craft: str
    root_cause: str


class RewriteOut(BaseModel):
    text: str
    length: int


class CycleOut(BaseModel):
    review: Review3ROut
    reflect: list[GapAnalysis]
    rewrite: RewriteOut


class Article(BaseModel):
    id: str
    title: str
    paragraphs: list[str]
    author: str
    tag: str
