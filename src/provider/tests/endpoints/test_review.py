"""POST /review tests."""

from tests.conftest import STYLE, TEXT


class TestReview:
    def test_basic_review(self, client):
        resp = client.post("/review", json={"text": TEXT, "style": STYLE})
        assert resp.status_code == 200
        data = resp.json()
        assert "dimension_alignments" in data
        assert len(data["dimension_alignments"]) > 0
        assert "overall_summary" in data

    def test_shows_dimension_scores(self, client):
        resp = client.post("/review", json={"text": TEXT, "style": STYLE})
        assert resp.status_code == 200
        for da in resp.json()["dimension_alignments"]:
            assert "dimension_title" in da
            assert "alignment_score" in da
