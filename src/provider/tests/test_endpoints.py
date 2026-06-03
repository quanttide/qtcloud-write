"""Tests for review/reflect/rewrite endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


SAMPLE_TEXT = "他推开门走了出去。第二天，她又来了。"
SAMPLE_CRITERIA = [
    {"id": "c1", "type": "positive_example", "content": "他推开门，冷风扑面，他不禁缩了缩脖子。"},
    {"id": "c2", "type": "constraint", "description": "避免时间跳跃过大，需要过渡句。"},
]


class TestReview:
    def test_basic_review(self, client):
        resp = client.post("/review", json={"text": SAMPLE_TEXT, "criteria": SAMPLE_CRITERIA})
        assert resp.status_code == 200
        data = resp.json()
        assert "criteria_analysis" in data
        assert len(data["criteria_analysis"]) > 0
        assert data["criteria_analysis"][0]["criterion_id"] == "c1"
        assert "alignment_score" in data["criteria_analysis"][0]
        assert "overall_summary" in data

    def test_review_empty_criteria(self, client):
        resp = client.post("/review", json={"text": SAMPLE_TEXT, "criteria": []})
        assert resp.status_code == 200
        assert "criteria_analysis" in resp.json()


class TestReflect:
    def test_reflect_with_criterion(self, client):
        body = {
            "text": SAMPLE_TEXT,
            "criterion": SAMPLE_CRITERIA[0],
        }
        resp = client.post("/reflect", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["criterion_id"] == "c1"
        assert "analysis" in data
        assert "specific_issues" in data


class TestRewrite:
    def test_basic_rewrite(self, client):
        body = {
            "text": SAMPLE_TEXT,
            "criteria": SAMPLE_CRITERIA,
        }
        resp = client.post("/rewrite", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert "rewritten_text" in data
        assert "alignment_scores" in data
        assert "changes" in data

    def test_rewrite_with_strategy(self, client):
        body = {
            "text": SAMPLE_TEXT,
            "criteria": SAMPLE_CRITERIA,
            "strategy": "prioritize_first",
            "preserve_original_length": True,
        }
        resp = client.post("/rewrite", json=body)
        assert resp.status_code == 200

    def test_rewrite_without_criteria(self, client):
        resp = client.post("/rewrite", json={"text": SAMPLE_TEXT, "criteria": []})
        assert resp.status_code == 200
