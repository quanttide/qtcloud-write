"""Tests for app/services/reflect.py — gap analysis."""

import json
from app.services.reflect import cmd_reflect


class TestCmdReflect:
    def test_returns_list_of_gaps(self):
        gaps = cmd_reflect("test text", genre="重逢", intent="营造氛围", stage="初稿")
        assert isinstance(gaps, list)
