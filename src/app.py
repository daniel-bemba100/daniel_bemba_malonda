"""Application bootstrap and entry point."""

import sys
import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.config.constants import AppConstants
from src.config.settings import SettingsManager
from src.main_window import MainWindow
from src.utils.logger import setup_logging
from src.utils.paths import icon_path

logger = logging.getLogger(__name__)


def create_app() -> tuple[QApplication, MainWindow]:
    """Create and configure the application and main window."""
    setup_logging()
    logger.info("Starting %s v%s", AppConstants.APP_NAME, AppConstants.APP_VERSION)

    app = QApplication(sys.argv)
    app.setApplicationName(AppConstants.APP_NAME)
    app.setApplicationVersion(AppConstants.APP_VERSION)
    app.setOrganizationName(AppConstants.ORG_NAME)

    # Set application icon
    icon_file = icon_path()
    if icon_file.exists():
        app.setWindowIcon(QIcon(str(icon_file)))

    settings = SettingsManager()
    window = MainWindow(settings)

    return app, window


def main() -> int:
    """Application entry point."""
    app, window = create_app()
    window.show()
    return app.exec()
