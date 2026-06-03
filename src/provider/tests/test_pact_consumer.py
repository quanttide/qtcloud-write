"""Consumer-driven pact contract — simulates Flutter making HTTP calls to provider.

Generates pacts/qtcloud_write_provider.json which the provider must satisfy.
"""

import requests
from pact import Pact

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
                    "article_title": "测试文章",
                    "author": "test",
                    "tag": "bad",
                    "summary": "分析结果摘要",
                    "paragraphs": [
                        {"original": "第一段", "analysis": "开篇引入", "tag": "起"},
                        {"original": "第二段", "analysis": "承接发展", "tag": "承"},
                    ],
                    "is_style_available": False,
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
            .with_body({"text": "他推开门走了出去。"})
            .will_respond_with(200)
            .with_header("Content-Type", "application/json")
        )

        with pact.serve(raises=False) as server:
            resp = requests.post(
                f"{server.url}/reflect",
                json={"text": "他推开门走了出去。"},
                timeout=5,
            )

        assert resp.status_code == 200
        pact.write_file(PACT_DIR, overwrite=True)
