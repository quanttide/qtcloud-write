"""POST /inspire tests."""

from tests.conftest import STYLE, TEXT


class TestInspire:
    def test_basic_inspire(self, client):
        resp = client.post("/inspire", json={"text": TEXT, "style": STYLE})
        assert resp.status_code == 200
        assert "inspirations" in resp.json()

    def test_with_target(self, client):
        body = {"text": TEXT, "style": STYLE, "target_dimensions": ["情感表达"]}
        resp = client.post("/inspire", json=body)
        assert resp.status_code == 200

    def test_with_variety(self, client):
        body = {"text": TEXT, "style": STYLE, "variety": "creative"}
        resp = client.post("/inspire", json=body)
        assert resp.status_code == 200
