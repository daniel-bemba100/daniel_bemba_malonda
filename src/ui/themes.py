"""Theme manager — loads and applies QSS stylesheets."""

import logging
from PyQt6.QtWidgets import QApplication
from src.config.settings import SettingsManager
from src.utils.paths import theme_path

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application themes (dark/light) via QSS stylesheets."""

    def __init__(self, settings: SettingsManager) -> None:
        self._settings = settings

    @property
    def current_theme(self) -> str:
        return self._settings.get("theme", "dark")

    def apply(self) -> None:
        """Apply the current theme to the entire application."""
        theme = self.current_theme
        qss_path = theme_path(theme)
        try:
            stylesheet = qss_path.read_text(encoding="utf-8")
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
            logger.info("Applied '%s' theme", theme)
        except FileNotFoundError:
            logger.warning("Theme file not found: %s", qss_path)
        except Exception as e:
            logger.error("Failed to apply theme: %s", e)

    def toggle(self) -> str:
        """Toggle between dark and light, apply, and return the new theme name."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self._settings.set("theme", new_theme)
        self.apply()
        return new_theme
