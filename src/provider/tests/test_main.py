"""Endpoint tests for all API routes (review, reflect, rewrite, cycle)."""

import pytest
from app.main import app
from app.store import style_store


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    style_store._good_articles.clear()
    yield


GOOD_ARTICLE = {
    "title": "构建游戏启发了我的产品设计理念",
    "paragraphs": [
        "最近一段时间的产品研发让我总是陷入一种'不知道自己在做什么的僵局'。",
        "小说已经无法满足我精确地验证建模思路的需求了。所以我又转向了游戏。",
        "可玩的游戏需要具备两个基本特征。",
        "这套方法无痛地验证和迁移了元方法。",
    ],
    "author": "founder",
    "tag": "good",
}

BAD_ARTICLE = {
    "title": "千问送20亿奶茶",
    "paragraphs": [
        "这两天，你的朋友圈大概率被千问的'免费奶茶券'刷屏了。",
        "作为吃瓜群众，我们关心的是怎么薅到羊毛。",
        "千问的规则很简单：老用户邀请新用户。",
        "短期来看，单用户的佣金收益微乎其微。",
    ],
    "author": "new_media",
    "tag": "bad",
}

SAMPLE_TEXT = "他推开门，看到她坐在窗边。阳光透过窗帘洒在她的脸上。"


class TestReview:
    def test_bare_analysis_without_style(self, client):
        resp = client.post("/review", json=BAD_ARTICLE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_style_available"] is False
        assert len(data["suggestions"]) == 0
        for p in data["paragraphs"]:
            assert p["comparison"] is None

    def test_good_article_analysis(self, client):
        resp = client.post("/review", json=GOOD_ARTICLE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tag"] == "good"
        assert len(data["paragraphs"]) == 4
        assert style_store.count == 1

    def test_full_review_after_style(self, client):
        client.post("/review", json=GOOD_ARTICLE)
        resp = client.post("/review", json=BAD_ARTICLE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_style_available"] is True
        assert len(data["suggestions"]) > 0
        bad_count = sum(
            1 for p in data["paragraphs"]
            if p.get("comparison") and p["comparison"]["type"] == "bad"
        )
        assert bad_count > 0

    def test_style_evolves(self, client):
        assert style_store.count == 0
        client.post("/review", json=GOOD_ARTICLE)
        assert style_store.count == 1
        a2 = dict(GOOD_ARTICLE, paragraphs=GOOD_ARTICLE["paragraphs"][:2])
        client.post("/review", json=a2)
        assert style_store.count == 2


class TestReflect:
    def test_returns_gaps(self, client):
        resp = client.post("/reflect", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestRewrite:
    def test_returns_text(self, client):
        resp = client.post("/rewrite", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        data = resp.json()
        assert "text" in data
        assert "length" in data
        assert data["length"] > 0


class TestCycle:
    def test_returns_all_three(self, client):
        resp = client.post("/cycle", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        data = resp.json()
        assert "review" in data
        assert "reflect" in data
        assert "rewrite" in data
        assert data["review"]["genre"]
        assert data["review"]["intent"]
