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


# ── Reflect ────────────────────────────────────────────

class ReflectRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    criterion: Criterion


class ReflectIssue(BaseModel):
    location: str = ""
    issue: str = ""
    fix_suggestion: str = ""


class ReflectResponse(BaseModel):
    criterion_id: str = ""
    analysis: dict = Field(default_factory=dict)
    specific_issues: list[ReflectIssue] = Field(default_factory=list)


# ── Rewrite ────────────────────────────────────────────

class RewriteRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH)
    criteria: list[Criterion] = Field(default_factory=list)
    strategy: str = "weighted_sum"  # "weighted_sum" | "prioritize_first" | "avoid_negative"
    preserve_original_length: bool = False


class RewriteChange(BaseModel):
    criterion_id: str = ""
    original_snippet: str = ""
    new_snippet: str = ""


class RewriteResponse(BaseModel):
    original_text: str = ""
    rewritten_text: str = ""
    alignment_scores: dict[str, float] = Field(default_factory=dict)
    changes: list[RewriteChange] = Field(default_factory=list)
