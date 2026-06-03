"""集成测试：调真实 DeepSeek API，验证端到端链路。

需要设置环境变量 DEEPSEEK_API_KEY 或 LLM_API_KEY。
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app


STYLE = {
    "title": "校园轻甜",
    "description": "轻快的双向奔赴，学生气的直球暧昧。温柔、礼貌、明快。",
    "dimensions": [
        {"title": "情感表达", "description": "半直球路线——欲说还休的写法介于含蓄和直白之间。", "confidence": 0.85, "clues": ["心尖像是被羽毛轻轻挠了一下"]},
        {"title": "语言风格", "description": "句式活泼，大量口语和语气词。", "confidence": 0.85, "clues": ["好啦！请你开始表演吧。"]},
        {"title": "时间结构", "description": "线性推进，没有回忆闪回，时间跨度短。", "confidence": 0.85, "clues": ["没有倒叙、没有二手文本"]},
    ],
    "excerpts": [
        {"paragraph": "逸神：\"林栀同学，抱歉。我没想到随手发的帖子会引发这么多关注……希望没有给你带来困扰。\"", "dimension": "情感表达", "note": "半直球"},
        {"paragraph": "林栀：\"其实是想问'能不能加个微信方便答谢'，结果脑子一空，说出口就变成了'有缘再见'……\"", "dimension": "语言风格", "note": "欲说还休"},
    ],
}

TEXT = "他推开门走了出去。第二天，她又来了。"


class TestReviewEndToEnd:
    """真实 DeepSeek API 调用，验证输出结构。"""

    def test_review_returns_valid_structure(self, client):
        resp = client.post("/review", json={"text": TEXT, "style": STYLE})
        assert resp.status_code == 200
        data = resp.json()
        assert "dimension_alignments" in data
        assert len(data["dimension_alignments"]) > 0
        assert "overall_summary" in data
        for da in data["dimension_alignments"]:
            assert "dimension_title" in da
            assert "alignment_score" in da
            assert 0 <= da["alignment_score"] <= 1

    def test_review_dimensions_match_style(self, client):
        resp = client.post("/review", json={"text": TEXT, "style": STYLE})
        assert resp.status_code == 200
        titles = [d["title"] for d in STYLE["dimensions"]]
        for da in resp.json()["dimension_alignments"]:
            assert da["dimension_title"] in titles

    def test_review_deviations_have_locations(self, client):
        resp = client.post("/review", json={"text": TEXT, "style": STYLE})
        assert resp.status_code == 200
        for da in resp.json()["dimension_alignments"]:
            for d in da.get("deviations", []):
                assert "location" in d
                assert "explanation" in d
