"""Contract verification: provider responses match expected shapes."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


SAMPLE_REVIEW = {
    "title": "测试文章",
    "paragraphs": ["第一段内容", "第二段内容"],
    "author": "test",
    "tag": "bad",
}


class TestReviewResponseShape:
    """Provider POST /review 返回的 JSON 必须能被 Dart DeepReview.fromJson 解析。"""

    def test_response_has_all_required_fields(self, client):
        resp = client.post("/review", json=SAMPLE_REVIEW)
        assert resp.status_code == 200
        data = resp.json()
        assert "article_title" in data
        assert "author" in data
        assert "tag" in data
        assert "summary" in data
        assert "paragraphs" in data
        assert "is_style_available" in data
        assert "suggestions" in data

    def test_paragraphs_have_required_fields(self, client):
        resp = client.post("/review", json=SAMPLE_REVIEW)
        assert resp.status_code == 200
        data = resp.json()
        for p in data["paragraphs"]:
            assert "original" in p
            assert "analysis" in p
            assert "tag" in p
            # tag 必须是 起承转合 之一
            assert p["tag"] in ("起", "承", "转", "合")

    def test_suggestions_have_required_fields(self, client):
        resp = client.post("/review", json=SAMPLE_REVIEW)
        assert resp.status_code == 200
        data = resp.json()
        for s in data["suggestions"]:
            assert "priority" in s
            assert "action" in s
            assert "detail" in s

    def test_comparison_when_style_available(self, client):
        # 先积累风格
        good = {
            "title": "好文章",
            "paragraphs": ["这是好文章的段落。"],
            "author": "founder",
            "tag": "good",
        }
        client.post("/review", json=good)

        resp = client.post("/review", json=SAMPLE_REVIEW)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_style_available"] is True
        for p in data["paragraphs"]:
            if p.get("comparison"):
                c = p["comparison"]
                assert "type" in c
                assert c["type"] in ("good", "bad", "pass")
