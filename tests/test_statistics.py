"""Tests for TextStatistics."""

from src.features.statistics import TextStatistics


class TestTextStatistics:
    def test_empty(self):
        stats = TextStatistics.compute("")
        assert stats["lines"] == 0
        assert stats["words"] == 0
        assert stats["chars"] == 0

    def test_single_line(self):
        stats = TextStatistics.compute("Hello world")
        assert stats["lines"] == 1
        assert stats["words"] == 2
        assert stats["chars"] == 11

    def test_multi_line(self):
        stats = TextStatistics.compute("Line one\nLine two\nLine three")
        assert stats["lines"] == 3
        assert stats["words"] == 6

    def test_summary_format(self):
        summary = TextStatistics.summary("Hello world")
        assert "Words: 2" in summary
        assert "Chars: 11" in summary
