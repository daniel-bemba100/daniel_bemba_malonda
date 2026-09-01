"""Screenshot capture utility."""

import datetime
import logging
import os
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QWidget

from src.utils.paths import resource_path

logger = logging.getLogger(__name__)


class ScreenshotCapture:
    """Captures screenshots and saves them to a user-chosen location."""

    SCREENSHOTS_DIR = resource_path("screenshots")

    @staticmethod
    def capture(parent: QWidget) -> str | None:
        """Capture the primary screen and prompt the user to save.

        Returns the saved file path, or None if cancelled.
        """
        screen = QApplication.primaryScreen()
        if not screen:
            logger.error("No primary screen available")
            return None

        pixmap = screen.grabWindow(0)
        if pixmap.isNull():
            logger.error("Screenshot capture returned null pixmap")
            return None

        # Ensure screenshots dir exists
        Path(ScreenshotCapture.SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = str(
            ScreenshotCapture.SCREENSHOTS_DIR / f"screenshot_{timestamp}.png"
        )

        path, _ = QFileDialog.getSaveFileName(
            parent, "Save Screenshot", default_name,
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)",
        )
        if path:
            if pixmap.save(path):
                logger.info("Screenshot saved: %s", path)
                return path
            else:
                logger.error("Failed to save screenshot to %s", path)

        return None
