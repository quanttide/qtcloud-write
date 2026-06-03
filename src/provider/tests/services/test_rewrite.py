"""Tests for app/services/rewrite.py — text rewrite."""

from app.services.rewrite import cmd_rewrite


class TestCmdRewrite:
    def test_returns_original_when_no_analysis(self):
        result = cmd_rewrite("hello world", genre="test", intent="test", analysis=None)
        assert result == "hello world"

    def test_returns_original_when_empty_analysis(self):
        result = cmd_rewrite("hello world", genre="test", intent="test", analysis=[])
        assert result == "hello world"

    def test_returns_rewritten_text_with_analysis(self):
        analysis = [
            {
                "gap_type": "action_gap",
                "detail": "缺少动作衔接",
                "structure": "断裂",
                "psychology": "缺失",
                "reader": "落空",
                "craft": "无意识忽略",
                "root_cause": "描写不完整",
            }
        ]
        result = cmd_rewrite("hello world", genre="test", intent="test", analysis=analysis)
        assert isinstance(result, str)
        assert len(result) > 0
