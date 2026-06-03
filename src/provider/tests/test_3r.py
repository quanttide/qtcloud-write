import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


SAMPLE_TEXT = "他推开门，看到她坐在窗边。阳光透过窗帘洒在她的脸上。"


class TestReflectEndpoint:
    def test_reflect_returns_gaps(self, client):
        resp = client.post("/reflect", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestRewriteEndpoint:
    def test_rewrite_returns_text(self, client):
        resp = client.post("/rewrite", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        data = resp.json()
        assert "text" in data
        assert "length" in data
        assert data["length"] > 0


class TestCycleEndpoint:
    def test_cycle_returns_all_three(self, client):
        resp = client.post("/cycle", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        data = resp.json()
        assert "review" in data
        assert "reflect" in data
        assert "rewrite" in data
        assert data["review"]["genre"]
        assert data["review"]["intent"]
