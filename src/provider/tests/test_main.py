"""Endpoint tests for all API routes."""

import pytest
from app.main import app


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)


SAMPLE_REVIEW = {
    "title": "测试文章",
    "paragraphs": ["第一段", "第二段"],
}


class TestReview:
    def test_basic_review(self, client):
        resp = client.post("/review", json=SAMPLE_REVIEW)
        assert resp.status_code == 200
        data = resp.json()
        assert "article_title" in data
        assert "paragraphs" in data
        assert "suggestions" in data
        assert "summary" in data
        assert "style_usage" not in data  # 无风格样本时不返回

    def test_review_with_style(self, client):
        body = {
            **SAMPLE_REVIEW,
            "style_samples": [
                {"name": "好风格", "paragraphs": ["这是很好的风格段落。"]},
            ],
        }
        resp = client.post("/review", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["style_usage"] is not None
        assert len(data["style_usage"]["samples_used"]) == 1

    def test_paragraphs_have_index(self, client):
        resp = client.post("/review", json=SAMPLE_REVIEW)
        assert resp.status_code == 200
        for i, p in enumerate(resp.json()["paragraphs"]):
            assert p["index"] == i

    def test_suggestions_off(self, client):
        body = {**SAMPLE_REVIEW, "options": {"include_suggestions": False}}
        resp = client.post("/review", json=body)
        assert resp.status_code == 200
        assert resp.json()["suggestions"] == []


class TestReflect:
    def test_returns_gaps(self, client):
        resp = client.post("/reflect", json={"text": "测试文本"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestRewrite:
    def test_returns_text(self, client):
        resp = client.post("/rewrite", json={"text": "测试文本"})
        assert resp.status_code == 200
        data = resp.json()
        assert "text" in data
        assert "length" in data
        assert data["length"] > 0


