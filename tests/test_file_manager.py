"""Tests for the FileManager."""

import tempfile
import os
import pytest
from src.core.file_manager import FileManager


class TestFileManager:
    def test_write_and_read(self, tmp_path):
        path = str(tmp_path / "test.txt")
        FileManager.write_file(path, "Hello, World!")
        content, encoding = FileManager.read_file(path)
        assert content == "Hello, World!"
        assert encoding == "utf-8"

    def test_read_nonexistent(self):
        with pytest.raises(FileNotFoundError):
            FileManager.read_file("/nonexistent/path/file.txt")

    def test_write_creates_dirs(self, tmp_path):
        path = str(tmp_path / "a" / "b" / "c" / "file.txt")
        FileManager.write_file(path, "nested")
        content, _ = FileManager.read_file(path)
        assert content == "nested"

    def test_detect_language(self):
        assert FileManager.detect_language("test.py") == "python"
        assert FileManager.detect_language("data.json") == "json"
        assert FileManager.detect_language("readme.txt") == "plain"
