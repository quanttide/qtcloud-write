import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.models import Comparison


@pytest.fixture(autouse=True)
def mock_llm():
    ap = patch("app.services.review.analyze_paragraph")
    mock_ap = ap.start()
    mock_ap.return_value = {
        "original": "",
        "analysis": "段落承接上文继续叙事。",
        "tag": "承",
    }
    cp = patch("app.services.review.compare_with_style")
    mock_cp = cp.start()
    mock_cp.return_value = Comparison(type="bad", issue="风格不一致", demo="应以个人困境出发")
    yield
    ap.stop()
    cp.stop()


@pytest.fixture
def client():
    return TestClient(app)
