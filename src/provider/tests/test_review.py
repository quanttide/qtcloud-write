import pytest
from app.main import app
from app.store import style_store


@pytest.fixture(autouse=True)
def reset_store():
    """Reset style accumulation between tests."""
    style_store._good_articles.clear()
    yield


GOOD_ARTICLE = {
    "title": "构建游戏启发了我的产品设计理念",
    "paragraphs": [
        "最近一段时间的产品研发让我总是陷入一种'不知道自己在做什么的僵局'。",
        "小说已经无法满足我精确地验证建模思路的需求了。所以我又转向了游戏。先是模拟经营游戏，找到了一个合适的视角和叙事方式。",
        "可玩的游戏需要具备两个基本特征。一个特征是要有具备良好反馈的游戏机制或者游戏玩法，一个是要具备意义感和叙事能力。",
        "这套方法无痛地验证和迁移了元方法，通过不断提纯和反应提高元方法的质量，从而让正式的研发工作变得异常顺利。不过可以肯定地是，让工作变好玩的目标又近了一步。",
    ],
    "author": "founder",
    "tag": "good",
}

BAD_ARTICLE = {
    "title": "千问送20亿奶茶",
    "paragraphs": [
        "这两天，你的朋友圈大概率被千问的'免费奶茶券'刷屏了。",
        "作为吃瓜群众，我们关心的是怎么薅到这杯羊毛；但作为计算机专业大学生，更该看透这场30亿大促背后的商业逻辑。",
        "千问的规则很简单：老用户邀请新用户，双方各得一张25元无门槛免单卡，成功邀请1次，激励成本就是50元。",
        "短期来看，单用户的佣金收益微乎其微，LTV远低于50元的CAC。如果想深入学习……关注公众号，回复'数据科学'加入交流群。",
    ],
    "author": "new_media",
    "tag": "bad",
}


class TestReviewBadWithoutStyle:
    """Bad article review when no style accumulated yet."""

    def test_bare_analysis_without_style(self, client):
        resp = client.post("/review", json=BAD_ARTICLE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_style_available"] is False
        assert len(data["suggestions"]) == 0
        for p in data["paragraphs"]:
            assert p["comparison"] is None


class TestReviewGood:
    """Good article review adds to style."""

    def test_good_article_analysis(self, client):
        resp = client.post("/review", json=GOOD_ARTICLE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tag"] == "good"
        assert len(data["paragraphs"]) == 4
        assert style_store.count == 1


class TestReviewBadWithStyle:
    """Bad article review after style accumulation."""

    def test_full_review_after_style(self, client):
        # First: accumulate style
        client.post("/review", json=GOOD_ARTICLE)
        assert style_store.count == 1

        # Then: review bad article
        resp = client.post("/review", json=BAD_ARTICLE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_style_available"] is True
        assert len(data["suggestions"]) > 0

        # Check that bad paragraphs have comparison
        bad_count = sum(
            1 for p in data["paragraphs"]
            if p.get("comparison") and p["comparison"]["type"] == "bad"
        )
        assert bad_count > 0, "Expected at least one bad comparison"


class TestStyleAccumulation:
    """Style grows with more good articles."""

    def test_style_evolves(self, client):
        # No style initially
        assert style_store.count == 0

        # After first good article
        client.post("/review", json=GOOD_ARTICLE)
        assert style_store.count == 1

        # After second good article
        a2 = dict(GOOD_ARTICLE, paragraphs=GOOD_ARTICLE["paragraphs"][:2])
        client.post("/review", json=a2)
        assert style_store.count == 2
