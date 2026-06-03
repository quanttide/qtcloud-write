"""Integration conftest — no autouse mocks, only DeepSeek HTTP is mocked."""

import json
import pytest
import os
from fastapi.testclient import TestClient
from app.main import app


# 默认 mock DeepSeek HTTP 响应，避免需要真实 API key
DEEPSEEK_RESPONSE = {
    "choices": [{
        "message": {
            "content": '{"dimension_alignments":[{"dimension_title":"情感表达","alignment_score":0.35,"deviations":[{"location":"他推开门","explanation":"缺少欲说还休","suggested_alignment":"他犹豫了一下才推开门"}]}],"overall_summary":"文本偏离风格。"}',
        },
        "finish_reason": "stop",
    }],
    "usage": {"prompt_tokens": 100, "completion_tokens": 50},
}


@pytest.fixture(autouse=True)
def mock_deepseek(httpx_mock):
    """Mock DeepSeek HTTP endpoint. call_llm → LLM.complete() → httpx → mock."""
    httpx_mock.add_response(
        url="https://api.deepseek.com/chat/completions",
        method="POST",
        json=DEEPSEEK_RESPONSE,
        is_optional=True,
    )


@pytest.fixture
def client():
    os.environ["LLM_API_KEY"] = "sk-test-key"
    return TestClient(app)
