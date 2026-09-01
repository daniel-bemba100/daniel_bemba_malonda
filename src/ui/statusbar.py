"""Enhanced status bar with line/col, word count, encoding, and language."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QStatusBar, QWidget


class EnhancedStatusBar(QStatusBar):
    """Status bar showing cursor position, statistics, encoding, and language."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._message_label = QLabel("")
        self._cursor_label = QLabel("Ln 1, Col 1")
        self._stats_label = QLabel("Words: 0  │  Chars: 0")
        self._encoding_label = QLabel("UTF-8")
        self._language_label = QLabel("Plain Text")

        # Permanent widgets on the right side
        self.addPermanentWidget(self._stats_label)
        self.addPermanentWidget(self._separator())
        self.addPermanentWidget(self._cursor_label)
        self.addPermanentWidget(self._separator())
        self.addPermanentWidget(self._encoding_label)
        self.addPermanentWidget(self._separator())
        self.addPermanentWidget(self._language_label)

    def update_cursor(self, line: int, col: int) -> None:
        self._cursor_label.setText(f"Ln {line}, Col {col}")

    def update_statistics(self, words: int, chars: int) -> None:
        self._stats_label.setText(f"Words: {words}  │  Chars: {chars}")

    def update_encoding(self, encoding: str) -> None:
        self._encoding_label.setText(encoding.upper())

    def update_language(self, language: str) -> None:
        self._language_label.setText(language.replace("_", " ").title())

    def flash_message(self, message: str, timeout_ms: int = 5000) -> None:
        self.showMessage(message, timeout_ms)

    @staticmethod
    def _separator() -> QLabel:
        sep = QLabel("│")
        sep.setStyleSheet("color: rgba(255,255,255,0.3); padding: 0 2px;")
        return sep
