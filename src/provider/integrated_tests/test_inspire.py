"""业务逻辑集成测试：/inspire 启发建议。

核心模式：
- 匹配风格 → 建议是微调（snippet 长度 ≈ 原文片段长度）
- 不匹配风格 → 建议是改写（snippet 长度 > 原文片段长度）
- 保守 ≈ 微调、创意 ≈ 重写
"""

from fastapi.testclient import TestClient
from app.main import app
from integrated_tests.fixtures import CAMPUS_STYLE, CAMPUS_FINAL, URBAN_STYLE, URBAN_FINAL

NEUTRAL_TEXT = "今天天气很好，我去超市买了些东西。"


class TestMatchInspire:
    """匹配风格 + inspire → 建议应是微调，不是全文重写。"""

    CAMPUS_SNIPPET = "火锅的热气沸腾，逐渐模糊了视线"

    def test_campus_inspire_suggestions_modify_not_replace(self, client):
        """建议应修改原文片段，不是凭空生成。"""
        resp = client.post("/inspire", json={
            "text": CAMPUS_FINAL,
            "style": CAMPUS_STYLE,
        })
        assert resp.status_code == 200
        for insp in resp.json()["inspirations"]:
            snippet = insp["suggested_snippet"]
            # 建议应包含至少 5 个与原文相同的字符（证明是基于原文修改）
            common = sum(1 for c in snippet if c in CAMPUS_FINAL)
            assert common >= 5, f"建议 '{snippet[:30]}...' 与原文共享字符少于 5 个"

    def test_campus_inspire_conservative_suggestions_are_snippets(self, client):
        """保守模式下，每条建议应是片段级修改（不是完整重写）。"""
        resp = client.post("/inspire", json={
            "text": CAMPUS_FINAL,
            "style": CAMPUS_STYLE,
            "variety": "conservative",
        })
        data = resp.json()
        for insp in data["inspirations"]:
            snippet = insp["suggested_snippet"]
            assert len(snippet) < len(CAMPUS_FINAL), \
                f"建议长度 {len(snippet)} 不应超过原文 {len(CAMPUS_FINAL)}"


    """维度聚焦能力。"""

    def test_target_dimension_at_least_one_match(self, client):
        """指定 target_dimensions 后，至少应有一条建议对应。"""
        resp = client.post("/inspire", json={
            "text": CAMPUS_FINAL,
            "style": CAMPUS_STYLE,
            "target_dimensions": ["情感表达"],
        })
        assert resp.status_code == 200
        items = resp.json()["inspirations"]
        match = sum(1 for i in items if i["target_dimension"] == "情感表达")
        assert match >= 1, f"5条建议中无一条目标维度为 情感表达"


class TestInspireVariety:
    """不同 variety 应产生不同效果。"""

    def test_conservative_shorter_than_creative(self, client):
        """保守模式建议应比创意模式短（改动小）。"""
        body = {"text": CAMPUS_FINAL, "style": CAMPUS_STYLE}
        resp_c = client.post("/inspire", json={**body, "variety": "conservative"})
        resp_v = client.post("/inspire", json={**body, "variety": "creative"})
        avg_c = sum(len(i["suggested_snippet"]) for i in resp_c.json()["inspirations"]) / 3
        avg_v = sum(len(i["suggested_snippet"]) for i in resp_v.json()["inspirations"]) / 3
        assert avg_v > avg_c, f"创意模式建议平均长度 {avg_v:.0f} 应大于保守模式 {avg_c:.0f}"

    def test_conservative_snippets_overlap_more_with_original(self, client):
        """保守模式建议应与原文重叠更多（更贴近原文）。"""
        body = {"text": CAMPUS_FINAL, "style": CAMPUS_STYLE}
        resp_c = client.post("/inspire", json={**body, "variety": "conservative"})
        resp_v = client.post("/inspire", json={**body, "variety": "creative"})
        def overlap_ratio(inspirations):
            total = 0
            for i in inspirations:
                common = sum(1 for c in i["suggested_snippet"] if c in CAMPUS_FINAL)
                total += common / max(len(i["suggested_snippet"]), 1)
            return total / len(inspirations)
        assert overlap_ratio(resp_c.json()["inspirations"]) > overlap_ratio(resp_v.json()["inspirations"]), \
            "保守模式建议与原文重叠比例应高于创意模式"
