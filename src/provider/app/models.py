from pydantic import BaseModel, Field
from typing import Optional

MAX_INPUT_LENGTH = 16000

# ── Criterion ──────────────────────────────────────────

class Criterion(BaseModel):
    id: str
    type: str  # "positive_example" | "negative_example" | "constraint"
    name: str = ""
    content: str = ""    # for positive/negative_example
    description: str = ""  # for constraint
    weight: float = 1.0


# ── Review ─────────────────────────────────────────────

class ReviewRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    criteria: list[Criterion] = Field(default_factory=list)


class Deviation(BaseModel):
    location: str = ""
    explanation: str = ""
    suggested_alignment: str = ""


class CriterionAnalysis(BaseModel):
    criterion_id: str
    alignment_score: float = 0.0
    deviations: list[Deviation] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    criteria_analysis: list[CriterionAnalysis] = Field(default_factory=list)
    overall_summary: str = ""


# ── Analyze ────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    criterion: Criterion
    deviation_description: str = ""
    focus: str = "root_cause"  # "root_cause" | "pattern_contrast" | "fix_suggestions"


class FixStrategy(BaseModel):
    strategy: str = ""
    example: str = ""


class AnalyzeResponse(BaseModel):
    criterion_id: str = ""
    analysis_type: str = ""
    original_pattern: dict = Field(default_factory=dict)
    expected_pattern: dict = Field(default_factory=dict)
    gap_analysis: dict = Field(default_factory=dict)
    fix_strategies: list[FixStrategy] = Field(default_factory=list)
    suggested_next_steps: str = ""


# ── Inspire ────────────────────────────────────────────

class InspirationImpact(BaseModel):
    alignment_impact: dict[str, float] = Field(default_factory=dict)


class Inspiration(BaseModel):
    id: str = ""
    title: str = ""
    description: str = ""
    suggested_snippet: str = ""
    applies_to: str = ""
    changes_summary: str = ""
    alignment_impact: dict[str, float] = Field(default_factory=dict)


class InspireRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    criteria: list[Criterion] = Field(default_factory=list)
    inspiration_count: int = 3
    variety: str = "balanced"  # "conservative" | "balanced" | "creative"
    focus_areas: list[str] = Field(default_factory=list)
    temperature: float = 0.8


class InspireResponse(BaseModel):
    original_text: str = ""
    inspirations: list[Inspiration] = Field(default_factory=list)
    usage_note: str = ""
