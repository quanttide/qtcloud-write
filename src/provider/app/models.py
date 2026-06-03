from pydantic import BaseModel, Field
from typing import Optional

MAX_INPUT_LENGTH = 8000


class TextIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)


class StyleSample(BaseModel):
    name: str
    paragraphs: list[str]


class ReviewOptions(BaseModel):
    include_suggestions: bool = True
    max_paragraphs_to_compare: Optional[int] = None


class Comparison(BaseModel):
    type: str  # "good" | "bad" | "pass" | "no_style"
    issue: Optional[str] = None
    demo: Optional[str] = None


class ParagraphReview(BaseModel):
    index: int
    original: str
    analysis: str
    tag: str  # "起" | "承" | "转" | "合"
    comparison: Optional[Comparison] = None


class Suggestion(BaseModel):
    priority: int
    action: str
    detail: str
    paragraph_index: Optional[int] = None


class StyleUsage(BaseModel):
    samples_used: list[str]
    confidence: float


class ReviewOut(BaseModel):
    article_title: str
    summary: str
    paragraphs: list[ParagraphReview]
    suggestions: list[Suggestion] = Field(default_factory=list)
    style_usage: Optional[StyleUsage] = None

    model_config = {"exclude_none": True}


class Review3ROut(BaseModel):
    genre: str
    intent: str
    stage: str
    summary: str


class Location(BaseModel):
    start_char: int = 0
    end_char: int = 0
    text_snippet: str = ""


class GapAnalysis(BaseModel):
    gap_id: str
    gap_type: str
    location: Location = Field(default_factory=Location)
    detail: str
    multi_dimensions: dict = Field(default_factory=dict)
    craft: str  # "有意识留白" | "无意识忽略"
    root_cause: str
    suggested_fix: str = ""


class RewriteRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    gaps_to_fix: list[str] | None = None
    respect_intentional: bool = True
    style_preserve: float = 0.8


class Change(BaseModel):
    gap_id: str
    original_snippet: str
    replaced_with: str
    start_char: int = 0
    end_char: int = 0


class RewriteOut(BaseModel):
    text: str
    length: int
    changes: list[Change] = Field(default_factory=list)
    unfixed_gaps: list[str] = Field(default_factory=list)
