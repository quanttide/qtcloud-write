from app.models import Article, ParagraphReview, Comparison
from app.services.llm import analyze_paragraph, compare_with_style


def review_article(
    article: Article,
    is_style_available: bool,
    style_examples: list[Article] | None = None,
) -> tuple[list[ParagraphReview], list[dict]]:
    """
    评审文章，核心逻辑委托给 LLM。
    """
    reviews = []
    suggestions = []
    style_examples = style_examples or []

    for i, para in enumerate(article.paragraphs):
        # 用 LLM 分析段落
        result = analyze_paragraph(
            paragraph=para,
            position=i,
            total=len(article.paragraphs),
            article_tag=article.tag,
        )

        # 用 LLM 对比风格
        comparison = None
        if is_style_available and article.tag != "good":
            comparison = compare_with_style(para, result["tag"], style_examples)

        reviews.append(ParagraphReview(
            original=result["original"],
            analysis=result["analysis"],
            tag=result["tag"],
            comparison=comparison,
        ))

    # 生成建议（保持原有逻辑）
    if is_style_available and article.tag != "good":
        bad_count = sum(1 for r in reviews if r.comparison and r.comparison.type == "bad")
        if bad_count > 0:
            suggestions.append({"priority": 1, "action": "换起点", "detail": "从'我为什么关注这件事'开始，而非外部热点"})
            suggestions.append({"priority": 2, "action": "补锚点", "detail": "加入你与这件事的真实交集"})
        if any("CTA" in r.analysis for r in reviews):
            suggestions.append({"priority": 3, "action": "换收束", "detail": "去掉产品CTA，以认知收束结尾"})

    return reviews, suggestions
