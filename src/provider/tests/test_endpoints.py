"""Tests for review/analyze/inspire endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


STYLE = {
    "title": "校园轻甜",
    "description": "轻快的双向奔赴，学生气的直球暧昧。",
    "dimensions": [
        {"title": "情感表达", "description": "半直球路线", "confidence": 0.85, "clues": ["心尖像是被羽毛轻轻挠了一下"]},
        {"title": "语言风格", "description": "句式活泼", "confidence": 0.85, "clues": ["好啦"]},
    ],
    "excerpts": [
        {"paragraph": "让我请你吃顿饭吧？", "dimension": "情感表达", "note": "欲说还休"},
    ],
}

SAMPLE_TEXT = "他推开门走了出去。第二天，她又来了。"


class TestReview:
    def test_basic_review(self, client):
        resp = client.post("/review", json={"text": SAMPLE_TEXT, "style": STYLE})
        assert resp.status_code == 200
        data = resp.json()
        assert "dimension_alignments" in data
        assert len(data["dimension_alignments"]) > 0
        assert "overall_summary" in data

    def test_review_shows_dimension_scores(self, client):
        resp = client.post("/review", json={"text": SAMPLE_TEXT, "style": STYLE})
        assert resp.status_code == 200
        data = resp.json()
        for da in data["dimension_alignments"]:
            assert "dimension_title" in da
            assert "alignment_score" in da


class TestAnalyze:
    def test_analyze_dimension(self, client):
        body = {
            "text": SAMPLE_TEXT,
            "style": STYLE,
            "dimension_title": "情感表达",
        }
        resp = client.post("/analyze", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["dimension_title"] == "情感表达"
        assert "original_pattern" in data
        assert "fix_strategies" in data


class TestInspire:
    def test_basic_inspire(self, client):
        body = {"text": SAMPLE_TEXT, "style": STYLE}
        resp = client.post("/inspire", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert "inspirations" in data

    def test_inspire_with_target(self, client):
        body = {"text": SAMPLE_TEXT, "style": STYLE, "target_dimensions": ["情感表达"]}
        resp = client.post("/inspire", json=body)
        assert resp.status_code == 200

    def test_inspire_with_variety(self, client):
        body = {"text": SAMPLE_TEXT, "style": STYLE, "variety": "creative"}
        resp = client.post("/inspire", json=body)
        assert resp.status_code == 200
