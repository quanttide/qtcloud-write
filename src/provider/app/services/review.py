from app.models import Article, ParagraphReview, Comparison

UNIT_LABELS = ["起", "承", "转", "合"]


def review_article(article: Article, is_style_available: bool) -> tuple[list[ParagraphReview], list[dict]]:
    results = _discern(article)
    reviews = []
    suggestions = []

    for r in results:
        comparison = None
        if is_style_available and article.tag != "good":
            comparison = _compare_against_style(r)

        reviews.append(ParagraphReview(
            original=r["original"],
            analysis=r["analysis"],
            tag=r["tag"],
            comparison=comparison,
        ))

    if is_style_available and article.tag != "good":
        bad_count = sum(1 for r in reviews if r.comparison and r.comparison.type == "bad")
        if bad_count > 0:
            suggestions.append({"priority": 1, "action": "换起点", "detail": "从'我为什么关注这件事'开始，而非外部热点"})
            suggestions.append({"priority": 2, "action": "补锚点", "detail": "加入你与这件事的真实交集"})
        if any("CTA" in r.analysis for r in reviews):
            suggestions.append({"priority": 3, "action": "换收束", "detail": "去掉产品CTA，以认知收束结尾"})

    return reviews, suggestions


def _discern(article: Article) -> list[dict]:
    n = len(article.paragraphs)
    results = []
    for i, para in enumerate(article.paragraphs):
        label = _assign_label(i, n, para)
        analysis = _analyze(label, para)
        results.append({"original": para, "tag": label, "analysis": analysis})
    return results


def _assign_label(i: int, n: int, text: str) -> str:
    if n == 1:
        return "起"
    if i == 0:
        return "起"
    if i == n - 1:
        return "合"
    if i == 1 or (n > 3 and i == n - 2):
        return "承"
    return "转"


def _analyze(label: str, text: str) -> str:
    if label == "起":
        if "我" in text and any(w in text for w in ["不知道", "困惑", "僵局", "困境", "问题"]):
            return "以个人困境为起点，引出要推演的问题"
        if any(w in text for w in ["最近", "这两年", "昨天"]):
            return "以时间锚点定位，建立叙事现场感"
        return "以外部现象为起点，缺少个人困境驱动"

    if label == "承":
        if any(w in text for w in ["发现", "意识到", "原来"]):
            return "承接上文，展示认知转折或深化"
        return "推进叙事，引入新信息"

    if label == "转":
        if "=" in text or "就是" in text or "本质" in text:
            return "建立底层连接，用等式焊住逻辑跳跃"
        if any(w in text for w in ["但", "不过", "然而"]):
            return "制造认知翻转，推动叙事转折"
        return "转换视角或论域，推入深层"

    if label == "合":
        if any(w in text for w in ["关注", "回复", "报名", "课程", "扫码"]):
            return "以CTA收束，认知闭合未完成"
        if any(w in text for w in ["近了一步", "终于", "回头来看"]):
            return "回到开头的问题，完成认知闭环"
        return "收束全文，给出结论或态度确认"
    return ""


def _compare_against_style(result: dict) -> Comparison | None:
    text = result["original"]
    tag = result["tag"]
    bad = []
    good = []

    if tag == "起":
        if "朋友圈" in text or ("最近" in text and "我" not in text[:10]):
            bad.append("起点是外部热点而非个人困境")
            good.append("从'我遇到了一个问题'开始，而非'最近发生了什么'")

    if "我" not in text and len(text) > 40:
        bad.append("全文无'我'，缺少个人物质锚点")
        good.append("加入你亲身经历的具体事物——一个对话、一个场景、一个工具")

    if tag == "合" and any(w in text for w in ["关注", "回复", "报名"]):
        bad.append("结尾跳转到产品推广，破坏叙事完整性")
        good.append("以认知收束——回到最初的问题，用新认知回答")

    if any(w in text for w in ["精准", "战略", "底层密码", "天花板", "赢麻了"]):
        bad.append("使用营销黑话替代实质论证")
        good.append("换成具体的判断或数据支撑")

    if bad:
        return Comparison(type="bad", issue="；".join(bad), demo="；".join(good) if good else None)
    return Comparison(type="pass")
