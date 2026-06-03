import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

REVIEW_RESP = '{"criteria_analysis":[{"criterion_id":"c1","alignment_score":0.35,"deviations":[{"location":"他推开门走了出去。","explanation":"缺少环境反馈","suggested_alignment":"他推开门，冷风扑面。"}]}],"overall_summary":"文本偏离正面范例。"}'
REFLECT_RESP = '{"analysis":{"patterns_found":["动作-结束"],"patterns_expected":["动作-环境-反应"],"gap_description":"缺少环境反馈","sample_illustration":"范例文本"},"specific_issues":[{"location":"他推开门走了出去。","issue":"动作后直接结束","fix_suggestion":"添加环境描写"}]}'
REWRITE_RESP = '{"rewritten_text":"他推开门，冷风扑面。","alignment_scores":{"c1":0.85},"changes":[{"criterion_id":"c1","original_snippet":"他推开门走了出去。","new_snippet":"他推开门，冷风扑面。"}]}'


@pytest.fixture(autouse=True)
def mock_llm():
    patchers = []

    gs = patch("app.services.llm.get_settings")
    patchers.append(gs)
    mock_gs = gs.start()
    mock_settings = mock_gs.return_value
    mock_settings.llm_api_key = "sk-test"
    mock_settings.llm_base_url = "https://api.deepseek.com"

    p = patch("app.main.call_llm")
    patchers.append(p)
    m = p.start()
    m.side_effect = (
        lambda prompt, **kw: REVIEW_RESP if "文本对比助手" in prompt
        else REFLECT_RESP if "写作诊断专家" in prompt
        else REWRITE_RESP
    )

    yield
    for p in reversed(patchers):
        p.stop()


@pytest.fixture
def client():
    return TestClient(app)
