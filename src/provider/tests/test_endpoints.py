"""Tests for review/analyze/inspire endpoints."""

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


class TestAnalyze:
    def test_analyze_with_criterion(self, client):
        body = {
            "text": SAMPLE_TEXT,
            "criterion": SAMPLE_CRITERIA[0],
            "deviation_description": "动作后缺少环境反馈",
        }
        resp = client.post("/analyze", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["criterion_id"] == "c1"
        assert "original_pattern" in data
        assert "fix_strategies" in data


class TestInspire:
    def test_basic_inspire(self, client):
        body = {
            "text": SAMPLE_TEXT,
            "criteria": SAMPLE_CRITERIA,
        }
        resp = client.post("/inspire", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert "inspirations" in data
        assert "usage_note" in data

    def test_inspire_with_options(self, client):
        body = {
            "text": SAMPLE_TEXT,
            "criteria": SAMPLE_CRITERIA,
            "inspiration_count": 2,
            "variety": "creative",
            "focus_areas": ["过渡", "细节"],
        }
        resp = client.post("/inspire", json=body)
        assert resp.status_code == 200

    def test_inspire_without_criteria(self, client):
        resp = client.post("/inspire", json={"text": SAMPLE_TEXT, "criteria": []})
        assert resp.status_code == 200
