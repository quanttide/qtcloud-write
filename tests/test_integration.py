import httpx


class TestEndToEnd:
    """前后端联调：真实 Provider + Flutter Web 客户端"""

    def test_provider_serves_docs(self, provider):
        r = httpx.get(f"http://localhost:8002/docs", timeout=5)
        assert r.status_code == 200

    def test_flutter_client_serves_html(self, studio_server):
        r = httpx.get("http://localhost:8080", timeout=5)
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")

    def test_flutter_build_injects_provider_url(self, studio_server):
        r = httpx.get("http://localhost:8080/main.dart.js", timeout=10)
        assert r.status_code == 200
        assert "localhost:8002" in r.text, "--dart-define=API_URL 未注入到 Flutter 构建产物"

    def test_style_accumulation_between_good_and_bad(self, provider):
        good = {
            "title": "好文章",
            "paragraphs": ["我最近陷入了一个困境", "然后我发现了突破口", "本质就是认知升级", "近了一步"],
            "author": "founder",
            "tag": "good",
        }
        bad = {
            "title": "坏文章",
            "paragraphs": ["最近朋友圈被刷屏了", "作为吃瓜群众", "规则很简单", "关注公众号回复xxx"],
            "author": "new_media",
            "tag": "bad",
        }
        c = httpx.Client(base_url="http://localhost:8002")
        c.post("/review", json=good)
        r = c.post("/review", json=bad)
        assert r.status_code == 200
        data = r.json()
        assert data["is_style_available"] is True
        assert len(data["suggestions"]) >= 1
