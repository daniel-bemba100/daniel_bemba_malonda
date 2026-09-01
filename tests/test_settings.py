"""Tests for SettingsManager and DatabaseManager."""

import pytest
from src.config.settings import SettingsManager
from src.core.database import DatabaseManager


class TestSettingsManager:
    @pytest.fixture
    def db_manager(self, tmp_path):
        db_path = tmp_path / "test_app_data.db"
        return DatabaseManager(db_path)

    def test_defaults(self, db_manager):
        sm = SettingsManager(db_manager)
        assert sm.get("theme") == "dark"
        assert sm.get("font_size") == 13
        assert sm.get("recent_files") == []

    def test_set_and_get(self, db_manager):
        sm = SettingsManager(db_manager)
        sm.set("theme", "light")
        assert sm.get("theme") == "light"
        # Verify persistence using the same DB path (new instance)
        db2 = DatabaseManager(db_manager._path)
        sm2 = SettingsManager(db2)
        assert sm2.get("theme") == "light"

    def test_recent_files(self, db_manager):
        sm = SettingsManager(db_manager)
        sm.add_recent_file("/a.txt")
        sm.add_recent_file("/b.txt")
        sm.add_recent_file("/a.txt")  # duplicate
        recent = sm.get("recent_files")
        assert recent == ["/a.txt", "/b.txt"]

    def test_clear_recent(self, db_manager):
        sm = SettingsManager(db_manager)
        sm.add_recent_file("/a.txt")
        sm.clear_recent_files()
        assert sm.get("recent_files") == []
