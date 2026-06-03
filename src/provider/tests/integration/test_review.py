"""Integration test: POST /review, mock only DeepSeek HTTP."""

STYLE = {
    "title": "校园轻甜",
    "description": "轻快的双向奔赴",
    "dimensions": [
        {"title": "情感表达", "description": "半直球路线", "confidence": 0.85, "clues": ["心尖像是被羽毛轻轻挠了一下"]},
    ],
    "excerpts": [
        {"paragraph": "让我请你吃顿饭吧？", "dimension": "情感表达", "note": "欲说还休"},
    ],
}

TEXT = "他推开门走了出去。第二天，她又来了。"


class TestReviewIntegration:
    def test_full_review_chain(self, client):
        """call_llm → LLM.complete → httpx → mock DeepSeek → parse response."""
        resp = client.post("/review", json={"text": TEXT, "style": STYLE})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["dimension_alignments"]) == 1
        assert data["dimension_alignments"][0]["alignment_score"] == 0.35
        assert data["overall_summary"] == "文本偏离风格。"

    def test_invalid_text_returns_422(self, client):
        resp = client.post("/review", json={"text": "", "style": STYLE})
        assert resp.status_code == 422
