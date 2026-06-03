"""POST /analyze tests."""

from tests.conftest import STYLE, TEXT


class TestAnalyze:
    def test_analyze_dimension(self, client):
        body = {"text": TEXT, "style": STYLE, "dimension_title": "情感表达"}
        resp = client.post("/analyze", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["dimension_title"] == "情感表达"
        assert "original_pattern" in data
        assert "fix_strategies" in data
