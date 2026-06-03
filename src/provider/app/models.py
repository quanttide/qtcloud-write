from pydantic import BaseModel, Field
from typing import Optional

MAX_INPUT_LENGTH = 16000

# ── StyleSample ─────────────────────────────────────────

class Dimension(BaseModel):
    title: str
    description: str = ""
    confidence: float = 0.0
    clues: list[str] = Field(default_factory=list)


class StyleExcerpt(BaseModel):
    paragraph: str = ""
    dimension: str = ""
    note: str = ""


class StyleSample(BaseModel):
    title: str
    description: str = ""
    dimensions: list[Dimension] = Field(default_factory=list)
    excerpts: list[StyleExcerpt] = Field(default_factory=list)


# ── Review ─────────────────────────────────────────────

class ReviewRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    style: StyleSample


class Deviation(BaseModel):
    location: str = ""
    explanation: str = ""
    suggested_alignment: str = ""


class DimensionAlignment(BaseModel):
    dimension_title: str
    alignment_score: float = 0.0
    deviations: list[Deviation] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    dimension_alignments: list[DimensionAlignment] = Field(default_factory=list)
    overall_summary: str = ""


# ── Analyze ────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    style: StyleSample
    dimension_title: str = ""
    deviation_description: str = ""


class FixStrategy(BaseModel):
    strategy: str = ""
    example: str = ""


class AnalyzeResponse(BaseModel):
    dimension_title: str = ""
    original_pattern: dict = Field(default_factory=dict)
    expected_pattern: dict = Field(default_factory=dict)
    gap_analysis: dict = Field(default_factory=dict)
    fix_strategies: list[FixStrategy] = Field(default_factory=list)
    suggested_next_steps: str = ""


# ── Inspire ────────────────────────────────────────────

class InspireRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    style: StyleSample
    target_dimensions: list[str] = Field(default_factory=list)
    inspiration_count: int = 3
    variety: str = "balanced"
    temperature: float = 0.8


class Inspiration(BaseModel):
    id: str = ""
    title: str = ""
    description: str = ""
    suggested_snippet: str = ""
    applies_to: str = ""
    target_dimension: str = ""
    alignment_impact: dict[str, float] = Field(default_factory=dict)


class InspireResponse(BaseModel):
    original_text: str = ""
    inspirations: list[Inspiration] = Field(default_factory=list)
    usage_note: str = ""
