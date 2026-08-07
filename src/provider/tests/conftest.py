import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

REVIEW_RESP = '{"dimension_alignments":[{"dimension_title":"情感表达","alignment_score":0.35,"deviations":[{"location":"他推开门","explanation":"缺少欲说还休","suggested_alignment":"他犹豫了一下才推开门"}]}],"overall_summary":"文本偏离风格。"}'
ANALYZE_RESP = '{"original_pattern":{"description":"动作直接","example":"他推开门"},"expected_pattern":{"description":"欲说还休","example":"让我请你吃顿饭吧"},"gap_analysis":{"root_cause":"缺少犹豫","impact":"失去暧昧感"},"fix_strategies":[{"strategy":"添加犹豫","example":"他犹豫了一下"}],"suggested_next_steps":"在动作前加入心理活动。"}'
INSPIRE_RESP = '{"inspirations":[{"id":"insp_001","title":"加入犹豫","description":"在动作前加心理活动","suggested_snippet":"他犹豫了一下才推开门","applies_to":"第一句","target_dimension":"情感表达","alignment_impact":{"情感表达":0.85}}]}'

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
    m.side_effect = lambda prompt, **kw: REVIEW_RESP if "风格分析助手" in prompt else ANALYZE_RESP if "写作诊断专家" in prompt else INSPIRE_RESP

    yield
    for p in reversed(patchers):
        p.stop()

@pytest.fixture
def client():
    return TestClient(app)

STYLE = {
    "title": "校园轻甜",
    "description": "轻快的双向奔赴",
    "dimensions": [
        {"title": "情感表达", "description": "半直球路线", "confidence": 0.85, "clues": ["心尖像是被羽毛轻轻挠了一下"]},
        {"title": "语言风格", "description": "句式活泼", "confidence": 0.85, "clues": ["好啦"]},
    ],
    "excerpts": [
        {"paragraph": "让我请你吃顿饭吧？", "dimension": "情感表达", "note": "欲说还休"},
    ],
}

TEXT = "他推开门走了出去。第二天，她又来了。"
