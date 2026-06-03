"""Consumer-driven pact contract — simulates Flutter making HTTP calls to provider.

Generates pacts/qtcloud_write_provider.json which the provider must satisfy.
"""

import requests
from pact import Pact
from pact.match import each_like, like, regex

PACT_DIR = "pacts"


class TestReviewEndpoint:
    """POST /review — Flutter's DeepReview.fromJson 依赖的字段。"""

    def test_review_response_shape(self):
        pact = Pact("qtcloud_write_studio", "qtcloud_write_provider")

        (
            pact.upon_receiving("a request to review an article")
            .given("provider is running with valid API key")
            .with_request("POST", "/review")
            .with_header("Content-Type", "application/json")
            .with_body(
                {
                    "title": "测试文章",
                    "paragraphs": ["第一段", "第二段"],
                    "author": "test",
                    "tag": "bad",
                }
            )
            .will_respond_with(200)
            .with_header("Content-Type", "application/json")
            .with_body(
                {
                    "article_title": like("测试文章"),
                    "author": like("test"),
                    "tag": regex(regex=r"good|bad|external"),
                    "summary": like("分析结果摘要"),
                    "paragraphs": each_like(
                        {
                            "original": like("第一段"),
                            "analysis": like("开篇引入"),
                            "tag": regex(regex=r"起|承|转|合"),
                        }
                    ),
                    "is_style_available": regex(regex=r"true|false"),
                    "suggestions": [],
                }
            )
        )

        with pact.serve(raises=False) as server:
            resp = requests.post(
                f"{server.url}/review",
                json={
                    "title": "测试文章",
                    "paragraphs": ["第一段", "第二段"],
                    "author": "test",
                    "tag": "bad",
                },
                timeout=5,
            )

        assert resp.status_code == 200
        pact.write_file(PACT_DIR, overwrite=True)


class TestReflectEndpoint:
    """POST /reflect — Flutter 依赖的 GapAnalysis 字段。"""

    def test_reflect_response_shape(self):
        pact = Pact("qtcloud_write_studio", "qtcloud_write_provider")

        (
            pact.upon_receiving("a request to reflect on text")
            .given("provider is running with valid API key")
            .with_request("POST", "/reflect")
            .with_header("Content-Type", "application/json")
            .with_body({"text": like("他推开门走了出去。")})
            .will_respond_with(200)
            .with_header("Content-Type", "application/json")
            .with_body(
                each_like(
                    {
                        "gap_type": regex(
                            regex=r"time_jump|dialog_gap|action_gap|perspective_shift|transition"
                        ),
                        "location": like("开门后"),
                        "detail": like("缺少过渡"),
                        "structure": like("叙事断裂"),
                        "psychology": like("人物反应缺失"),
                        "reader": like("期待落空"),
                        "craft": regex(regex=r"有意识留白|无意识忽略"),
                        "root_cause": like("动作描写不完整"),
                    }
                )
            )
        )

        with pact.serve(raises=False) as server:
            resp = requests.post(
                f"{server.url}/reflect",
                json={"text": "他推开门走了出去。"},
                timeout=5,
            )

        assert resp.status_code == 200
        pact.write_file(PACT_DIR, overwrite=True)
