"""业务逻辑集成测试：/analyze 深度分析。

仅保留稳定的断言：响应结构正确、非空。LLM 输出内容不设数值阈值。
"""

from fastapi.testclient import TestClient
from app.main import app
from integrated_tests.fixtures import CAMPUS_STYLE, CAMPUS_FINAL, URBAN_STYLE


NEUTRAL_TEXT = "今天天气很好，我去超市买了些东西。"


class TestAnalyzeStructure:
    """验证 analyze 返回结构完整。"""

    def test_analyze_matching_style(self, client):
        resp = client.post("/review", json={"text": CAMPUS_FINAL, "style": CAMPUS_STYLE})
        dim = max(resp.json()["dimension_alignments"], key=lambda d: d["alignment_score"])["dimension_title"]

        resp = client.post("/analyze", json={
            "text": CAMPUS_FINAL, "style": CAMPUS_STYLE, "dimension_title": dim,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_pattern"].get("description")
        assert data["expected_pattern"].get("description")
        assert len(data["fix_strategies"]) >= 1

    def test_analyze_non_matching_style(self, client):
        resp = client.post("/review", json={"text": CAMPUS_FINAL, "style": URBAN_STYLE})
        dim = min(resp.json()["dimension_alignments"], key=lambda d: d["alignment_score"])["dimension_title"]

        resp = client.post("/analyze", json={
            "text": CAMPUS_FINAL, "style": URBAN_STYLE, "dimension_title": dim,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_pattern"].get("description")
        assert data["expected_pattern"].get("description")
        assert len(data["fix_strategies"]) >= 1

    def test_analyze_neutral_text(self, client):
        resp = client.post("/review", json={"text": NEUTRAL_TEXT, "style": CAMPUS_STYLE})
        dim = resp.json()["dimension_alignments"][0]["dimension_title"]

        resp = client.post("/analyze", json={
            "text": NEUTRAL_TEXT, "style": CAMPUS_STYLE, "dimension_title": dim,
        })
        assert resp.status_code == 200
        assert len(resp.json()["fix_strategies"]) >= 1
