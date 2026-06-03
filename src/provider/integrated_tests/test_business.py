"""业务逻辑集成测试：风格匹配度验证。

校园言情成稿 × 校园言情风格 → 分数应显著高于 × 职场言情风格
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from integrated_tests.fixtures import (
    CAMPUS_STYLE, CAMPUS_FINAL,
    URBAN_STYLE, URBAN_FINAL,
)

# 文科生的自白：一个与校园言情和职场言情都不匹配的风格
NEUTRAL_TEXT = """今天天气很好，我去超市买了些东西。回来的路上遇到了邻居，聊了几句。她说最近物价涨了不少，我说是啊。回家后我把东西放好，打开电脑开始工作。"""


def avg_score(data: dict) -> float:
    scores = [da["alignment_score"] for da in data["dimension_alignments"]]
    return sum(scores) / len(scores) if scores else 0.0


class TestCampusRomance:
    """校园言情：自己的风格应该匹配，职场言情风格应该不匹配。"""

    def test_campus_final_matches_campus_style(self, client):
        resp = client.post("/review", json={"text": CAMPUS_FINAL, "style": CAMPUS_STYLE})
        assert resp.status_code == 200
        data = resp.json()
        score = avg_score(data)
        assert score > 0.5, f"校园言情成稿配校园风格，平均分 {score:.2f} 应 > 0.5"

    def test_campus_final_does_not_match_urban_style(self, client):
        resp = client.post("/review", json={"text": CAMPUS_FINAL, "style": URBAN_STYLE})
        assert resp.status_code == 200
        data = resp.json()
        score = avg_score(data)
        assert score < 0.6, f"校园言情成稿配职场风格，平均分 {score:.2f} 应 < 0.6"


class TestUrbanRomance:
    """职场言情同。"""

    def test_urban_final_matches_urban_style(self, client):
        resp = client.post("/review", json={"text": URBAN_FINAL, "style": URBAN_STYLE})
        assert resp.status_code == 200
        data = resp.json()
        score = avg_score(data)
        assert score > 0.5, f"职场言情成稿配职场风格，平均分 {score:.2f} 应 > 0.5"

    def test_urban_final_does_not_match_campus_style(self, client):
        resp = client.post("/review", json={"text": URBAN_FINAL, "style": CAMPUS_STYLE})
        assert resp.status_code == 200
        data = resp.json()
        score = avg_score(data)
        assert score < 0.6, f"职场言情成稿配校园风格，平均分 {score:.2f} 应 < 0.6"


class TestNeutralBaseline:
    """中性文本（非文学创作）无论配哪种风格，分数都应该低。"""

    def test_neutral_vs_campus(self, client):
        resp = client.post("/review", json={"text": NEUTRAL_TEXT, "style": CAMPUS_STYLE})
        assert resp.status_code == 200
        score = avg_score(resp.json())
        assert score < 0.5, f"中性文本配校园风格，平均分 {score:.2f} 应 < 0.5"

    def test_neutral_vs_urban(self, client):
        resp = client.post("/review", json={"text": NEUTRAL_TEXT, "style": URBAN_STYLE})
        assert resp.status_code == 200
        score = avg_score(resp.json())
        assert score < 0.5, f"中性文本配职场风格，平均分 {score:.2f} 应 < 0.5"
