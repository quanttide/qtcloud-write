from app.models import ParagraphReview, Comparison, StyleSample
from app.services.llm import analyze_paragraph, compare_with_style


def review_article(
    paragraphs: list[str],
    style_samples: list[StyleSample] | None = None,
    max_compare: int | None = None,
) -> tuple[list[ParagraphReview], list[dict]]:
    reviews = []
    suggestions = []
    style_samples = style_samples or []

    for i, para in enumerate(paragraphs):
        result = analyze_paragraph(para, i, len(paragraphs), "none")

        comparison = None
        if style_samples and (max_compare is None or i < max_compare):
            comparison = compare_with_style(para, result["tag"], style_samples)

        reviews.append(ParagraphReview(
            index=i,
            original=result["original"],
            analysis=result["analysis"],
            tag=result["tag"],
            comparison=comparison,
        ))

        if comparison and comparison.type == "bad":
            suggestions.append({
                "priority": 1,
                "action": "对比差异",
                "detail": comparison.issue or "风格不一致",
                "paragraph_index": i,
            })

    return reviews, suggestions
