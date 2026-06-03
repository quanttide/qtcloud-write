"""业务逻辑集成测试：/inspire 启发建议。

验证建议生成的质量、多样性、以及对特定维度的聚焦能力。
"""

from fastapi.testclient import TestClient
from app.main import app
from integrated_tests.fixtures import (
    CAMPUS_STYLE, CAMPUS_FINAL,
)


class TestInspireBasics:
    """启发建议的基本功能。"""

    def test_returns_multiple_inspirations(self, client):
        resp = client.post("/inspire", json={
            "text": CAMPUS_FINAL,
            "style": CAMPUS_STYLE,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["inspirations"]) >= 2, f"应返回至少 2 条建议，实际 {len(data['inspirations'])}"
        assert data["usage_note"] != ""
        for insp in data["inspirations"]:
            assert insp["suggested_snippet"] != ""
            assert insp["applies_to"] != ""

    def test_each_inspiration_has_impact_estimation(self, client):
        """每个建议应预估对齐影响。"""
        resp = client.post("/inspire", json={
            "text": CAMPUS_FINAL,
            "style": CAMPUS_STYLE,
        })
        assert resp.status_code == 200
        for insp in resp.json()["inspirations"]:
            assert insp.get("alignment_impact"), f"建议 {insp['id']} 缺少 alignment_impact"
            assert len(insp["alignment_impact"]) > 0


class TestInspireTargeting:
    """聚焦特定维度的能力。"""

    def test_target_dimensions_respected(self, client):
        """指定 target_dimensions 后，至少半数建议应关联该维度。"""
        resp = client.post("/inspire", json={
            "text": CAMPUS_FINAL,
            "style": CAMPUS_STYLE,
            "target_dimensions": ["情感表达"],
        })
        assert resp.status_code == 200
        inspirations = resp.json()["inspirations"]
        matching = sum(1 for i in inspirations if i["target_dimension"] == "情感表达")
        assert matching >= len(inspirations) / 2, \
            f"13条中仅 {matching} 条目标维度为 情感表达"


class TestInspireVariety:
    """不同 variety 参数应影响建议的多样性。"""

    def test_conservative_vs_creative_different(self, client):
        """保守和创意模式应给出不同建议。"""
        body = {"text": CAMPUS_FINAL, "style": CAMPUS_STYLE}
        resp_c = client.post("/inspire", json={**body, "variety": "conservative"})
        resp_v = client.post("/inspire", json={**body, "variety": "creative"})
        assert resp_c.status_code == 200
        assert resp_v.status_code == 200
        snippets_c = [i["suggested_snippet"] for i in resp_c.json()["inspirations"]]
        snippets_v = [i["suggested_snippet"] for i in resp_v.json()["inspirations"]]
        # 保守和创意应该给出不完全一样的建议
        common = set(snippets_c) & set(snippets_v)
        assert len(common) < len(snippets_c), "保守和创意模式应产出不同的建议，但全部相同"
