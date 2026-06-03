"""Tests for app/services/rewrite.py — text rewrite."""

from app.services.rewrite import cmd_rewrite


class TestCmdRewrite:
    def test_returns_original_when_no_analysis(self):
        text, changes, unfixed = cmd_rewrite("hello world", genre="test", intent="test", analysis=None)
        assert text == "hello world"
        assert changes == []

    def test_returns_original_when_empty_analysis(self):
        text, changes, unfixed = cmd_rewrite("hello world", genre="test", intent="test", analysis=[])
        assert text == "hello world"
        assert changes == []

    def test_returns_rewritten_text_with_analysis(self):
        analysis = [
            {
                "gap_id": "gap_001",
                "gap_type": "action_gap",
                "detail": "缺少动作衔接",
                "craft": "无意识忽略",
                "suggested_fix": "补充动作描写",
            }
        ]
        text, changes, unfixed = cmd_rewrite("hello world", genre="test", intent="test", analysis=analysis)
        assert isinstance(text, str)
        assert len(text) > 0
