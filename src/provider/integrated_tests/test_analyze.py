"""业务逻辑集成测试：/analyze 深度分析。

对匹配风格最差的维度进行深度分析，验证分析质量。
"""

from fastapi.testclient import TestClient
from app.main import app
from integrated_tests.fixtures import (
    CAMPUS_STYLE, CAMPUS_FINAL,
    URBAN_STYLE, URBAN_FINAL,
)


class TestCampusAnalyze:
    """校园言情文本 vs 职场言情风格：分析预期最不匹配的维度。"""

    def test_analyze_dimension_with_low_alignment(self, client):
        """先 review 找出最低分维度，再 analyze。"""
        # 1. Review：校园文本 × 职场风格 → 分数低
        resp = client.post("/review", json={"text": CAMPUS_FINAL, "style": URBAN_STYLE})
        dims = resp.json()["dimension_alignments"]
        worst = min(dims, key=lambda d: d["alignment_score"])
        dim_title = worst["dimension_title"]

        # 2. Analyze：对最低分维度做深度分析
        resp = client.post("/analyze", json={
            "text": CAMPUS_FINAL,
            "style": URBAN_STYLE,
            "dimension_title": dim_title,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["dimension_title"] == dim_title
        assert data["original_pattern"].get("description")
        assert data["expected_pattern"].get("description")
        # original_pattern 和 expected_pattern 应该不同
        assert data["original_pattern"]["description"] != data["expected_pattern"]["description"]
        assert len(data["fix_strategies"]) > 0, "应提供至少一个修复策略"

    def test_analyze_with_deviation_description(self, client):
        """传入 deviation_description 应增强分析相关性。"""
        resp = client.post("/analyze", json={
            "text": CAMPUS_FINAL,
            "style": URBAN_STYLE,
            "dimension_title": "情感表达",
            "deviation_description": "文本的情感表达偏向明快直球，而风格期望的是克制含蓄",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "fix_strategies" in data
        assert len(data["fix_strategies"]) > 0


class TestUrbanAnalyze:
    """职场言情文本 vs 校园言情风格。"""

    def test_analyze_lowest_dimension(self, client):
        resp = client.post("/review", json={"text": URBAN_FINAL, "style": CAMPUS_STYLE})
        dims = resp.json()["dimension_alignments"]
        worst = min(dims, key=lambda d: d["alignment_score"])

        resp = client.post("/analyze", json={
            "text": URBAN_FINAL,
            "style": CAMPUS_STYLE,
            "dimension_title": worst["dimension_title"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_pattern"]["description"] != data["expected_pattern"]["description"]
