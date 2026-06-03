"""Tests for app/services/llm.py — prompt builders and parsers."""

import json
from app.services.llm import _parse_analyze_response, _parse_compare_response
from app.models import Comparison


class TestParseAnalyzeResponse:
    def test_parses_valid_json(self):
        result = _parse_analyze_response(
            '{"analysis": "开篇引入场景", "tag": "起"}',
            "原文段落",
        )
        assert result["original"] == "原文段落"
        assert result["analysis"] == "开篇引入场景"
        assert result["tag"] == "起"

    def test_defaults_to_承_on_invalid_json(self):
        result = _parse_analyze_response("not json", "原文")
        assert result["tag"] == "承"
        assert result["analysis"] == ""

    def test_defaults_to_承_on_invalid_tag(self):
        result = _parse_analyze_response(
            '{"analysis": "test", "tag": "invalid"}',
            "原文",
        )
        assert result["tag"] == "承"


class TestParseCompareResponse:
    def test_parses_good(self):
        result = _parse_compare_response('{"type": "good"}')
        assert isinstance(result, Comparison)
        assert result.type == "good"

    def test_parses_bad_with_fields(self):
        result = _parse_compare_response(
            '{"type": "bad", "issue": "问题", "demo": "示范"}'
        )
        assert result.type == "bad"
        assert result.issue == "问题"
        assert result.demo == "示范"

    def test_returns_none_for_invalid(self):
        assert _parse_compare_response("not json") is None
        assert _parse_compare_response('{"type": "unknown"}') is None
