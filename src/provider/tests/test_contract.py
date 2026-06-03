"""Contract verification: provider responses match expected shapes."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


SAMPLE = {"title": "测试文章", "paragraphs": ["第一段", "第二段"]}


class TestReviewResponseShape:
    def test_response_has_all_required_fields(self, client):
        resp = client.post("/review", json=SAMPLE)
        assert resp.status_code == 200
        data = resp.json()
        assert "article_title" in data
        assert "summary" in data
        assert "paragraphs" in data
        assert "suggestions" in data

    def test_paragraphs_have_index_and_tag(self, client):
        resp = client.post("/review", json=SAMPLE)
        assert resp.status_code == 200
        for p in resp.json()["paragraphs"]:
            assert "index" in p
            assert "original" in p
            assert "analysis" in p
            assert "tag" in p
            assert p["tag"] in ("起", "承", "转", "合")

    def test_comparison_when_style_provided(self, client):
        body = {
            **SAMPLE,
            "style_samples": [{"name": "风格1", "paragraphs": ["好文章段落。"]}],
        }
        resp = client.post("/review", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert "style_usage" in data
        assert data["style_usage"]["samples_used"] == ["风格1"]
        # 至少有一段有 comparison
        has_comparison = any(p.get("comparison") for p in data["paragraphs"])
        assert has_comparison
