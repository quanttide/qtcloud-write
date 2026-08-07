import os
import pytest
from fastapi.testclient import TestClient
from app.main import app


def pytest_configure(config):
    """Skip all tests in this directory if no API key configured."""
    key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("LLM_API_KEY")
    if not key:
        pytest.skip("需要 DEEPSEEK_API_KEY 或 LLM_API_KEY 环境变量", allow_module_level=True)


@pytest.fixture
def client():
    return TestClient(app)
