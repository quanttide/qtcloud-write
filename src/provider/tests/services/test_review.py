"""Tests for app/services/review.py — article review orchestration."""

from app.models import Article
from app.services.review import review_article


class TestReviewArticle:
    def test_returns_reviews_and_suggestions(self):
        article = Article(
            id="", title="Test", paragraphs=["第一段", "第二段"], author="me", tag="bad"
        )
        reviews, suggestions = review_article(article, is_style_available=False)
        assert len(reviews) == 2
        assert isinstance(suggestions, list)
