import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

REVIEW_RESP = '{"criteria_analysis":[{"criterion_id":"c1","alignment_score":0.35,"deviations":[{"location":"他推开门走了出去。","explanation":"缺少环境反馈","suggested_alignment":"他推开门，冷风扑面。"}]}],"overall_summary":"文本偏离正面范例。"}'
ANALYZE_RESP = '{"criterion_id":"c1","analysis_type":"pattern_contrast","original_pattern":{"description":"动作-结束","example_from_text":"他推开门走了出去。"},"expected_pattern":{"description":"动作-环境-反应","example_from_criterion":"范例文本"},"gap_analysis":{"root_cause":"缺少感官细节","psychological_impact":"读者无法感知环境","structural_role":"场景入口缺乏锚点"},"fix_strategies":[{"strategy":"添加环境刺激","example":"冷风如刀割在脸上。"}],"suggested_next_steps":"尝试以上策略。"}'
INSPIRE_RESP = '{"inspirations":[{"id":"insp_001","title":"增加环境反馈","description":"加入冷风描写","suggested_snippet":"他推开门，冷风扑面。","applies_to":"第一句","changes_summary":"增加了环境细节","alignment_impact":{"c1":0.85}}],"usage_note":"这些是启发建议。"}'


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
        else ANALYZE_RESP if "写作诊断专家" in prompt
        else INSPIRE_RESP
    )

    yield
    for p in reversed(patchers):
        p.stop()


@pytest.fixture
def client():
    return TestClient(app)
