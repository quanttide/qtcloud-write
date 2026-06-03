import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.models import Comparison


REVIEW_3R_RESP = '{"genre":"重逢场景","intent":"营造暧昧氛围","stage":"初稿","summary":"他推门看到她坐在窗边"}'
REFLECT_RESP = '[{"gap_type":"action_gap","location":"开门后","detail":"缺少过渡","structure":"叙事断裂","psychology":"人物反应缺失","reader":"期待落空","craft":"无意识忽略","root_cause":"动作描写不完整"}]'
REWRITE_RESP = "他推开门，看到她坐在窗边。阳光透过窗帘洒在她的脸上。"


@pytest.fixture(autouse=True)
def mock_llm():
    patchers = []

    # Mock get_settings to bypass env check
    gs = patch("app.services.llm.get_settings")
    patchers.append(gs)
    mock_gs = gs.start()
    mock_settings = mock_gs.return_value
    mock_settings.llm_api_key = "sk-test"
    mock_settings.llm_base_url = "https://api.deepseek.com"

    ap = patch("app.services.review.analyze_paragraph")
    patchers.append(ap)
    mock_ap = ap.start()
    mock_ap.return_value = {"original": "", "analysis": "段落承接上文继续叙事。", "tag": "承"}

    cp = patch("app.services.review.compare_with_style")
    patchers.append(cp)
    mock_cp = cp.start()
    mock_cp.return_value = Comparison(type="bad", issue="风格不一致", demo="应以个人困境出发")

    # Mock call_llm at each usage site
    for mod in ["app.services.reflect", "app.services.rewrite", "app.main"]:
        p = patch(f"{mod}.call_llm")
        patchers.append(p)
        m = p.start()
        m.side_effect = (
            lambda prompt, **kw: REVIEW_3R_RESP
            if "阅读下面的文章" in prompt
            else (
                REFLECT_RESP
                if "写作诊断" in prompt or "空隙" in prompt
                else REWRITE_RESP
            )
        )
    yield
    for p in reversed(patchers):
        p.stop()


@pytest.fixture
def client():
    return TestClient(app)
