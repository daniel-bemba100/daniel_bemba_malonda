"""Persistent settings manager using SQLite."""

import logging
from pathlib import Path
from typing import Any

from src.config.constants import AppConstants
from src.core.database import DatabaseManager

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manages application settings with SQLite persistence."""

    _DEFAULT_SETTINGS = {
        "theme": AppConstants.DEFAULT_THEME,
        "font_family": AppConstants.DEFAULT_FONT_FAMILY,
        "font_size": AppConstants.DEFAULT_FONT_SIZE,
        "auto_save_enabled": True,
        "auto_save_interval_ms": AppConstants.AUTO_SAVE_INTERVAL_MS,
        "recent_files": [],
        "window_geometry": None,
        "window_state": None,
        "word_wrap": True,
        "show_line_numbers": True,
        "highlight_current_line": True,
        "tts_locale": AppConstants.TTS_LOCALE,
        "tts_rate": AppConstants.TTS_RATE,
        "tts_volume": AppConstants.TTS_VOLUME,
    }

    def __init__(self, db_manager: DatabaseManager = None):
        self._db = db_manager or DatabaseManager()

    # ── Public API ──────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Return a setting value, falling back to built-in defaults."""
        fallback = self._DEFAULT_SETTINGS.get(key, default)
        return self._db.get_setting(key, fallback)

    def set(self, key: str, value: Any) -> None:
        """Set a value and persist to SQLite immediately."""
        self._db.set_setting(key, value)

    def add_recent_file(self, file_path: str) -> None:
        """Prepend *file_path* to recent files, removing duplicates."""
        recent: list[str] = self.get("recent_files", [])
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        recent = recent[: AppConstants.MAX_RECENT_FILES]
        self.set("recent_files", recent)

    def clear_recent_files(self) -> None:
        self.set("recent_files", [])
