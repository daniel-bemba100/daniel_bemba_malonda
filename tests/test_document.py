"""Tests for the Document model."""

import pytest
from src.core.document import Document


class TestDocument:
    def test_default_state(self):
        doc = Document()
        assert doc.path is None
        assert doc.filename == "Untitled"
        assert doc.encoding == "utf-8"
        assert doc.is_modified is False
        assert doc.language == "plain"

    def test_with_path(self):
        doc = Document(path="/home/user/test.py")
        assert doc.filename == "test.py"
        assert doc.language == "python"

    def test_title_unmodified(self):
        doc = Document(path="/tmp/hello.txt")
        assert doc.title == "hello.txt"

    def test_title_modified(self):
        doc = Document(path="/tmp/hello.txt")
        doc.is_modified = True
        assert doc.title == "● hello.txt"

    def test_language_detection(self):
        cases = {
            "/a/b.py": "python",
            "/a/b.json": "json",
            "/a/b.html": "html",
            "/a/b.css": "css",
            "/a/b.js": "javascript",
            "/a/b.md": "markdown",
            "/a/b.sql": "sql",
            "/a/b.unknown": "plain",
        }
        for path, expected in cases.items():
            assert Document(path=path).language == expected
