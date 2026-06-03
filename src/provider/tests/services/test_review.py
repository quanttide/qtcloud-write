"""Tests for app/services/review.py — article review orchestration."""

from app.services.review import review_article


class TestReviewArticle:
    def test_returns_reviews_and_suggestions(self):
        reviews, suggestions = review_article(["第一段", "第二段"])
        assert len(reviews) == 2
        assert isinstance(suggestions, list)
        for r in reviews:
            assert r.index >= 0
