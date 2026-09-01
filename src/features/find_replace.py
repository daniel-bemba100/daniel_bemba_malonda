"""Find & Replace dialog — non-modal, inline search bar."""

import logging
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor, QTextDocument
from PyQt6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)

logger = logging.getLogger(__name__)


class FindReplaceBar(QWidget):
    """A non-modal find/replace bar that sits below the tab widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._editor = None
        self._build_ui()
        self.hide()

    def set_editor(self, editor) -> None:
        self._editor = editor

    def show_find(self) -> None:
        self._replace_row.hide()
        self.show()
        self._find_input.setFocus()
        self._find_input.selectAll()

    def show_replace(self) -> None:
        self._replace_row.show()
        self.show()
        self._find_input.setFocus()
        self._find_input.selectAll()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        # Find row
        find_row = QHBoxLayout()
        find_row.addWidget(QLabel("Find:"))
        self._find_input = QLineEdit()
        self._find_input.setPlaceholderText("Search…")
        self._find_input.returnPressed.connect(self._find_next)
        find_row.addWidget(self._find_input, 1)

        self._case_cb = QCheckBox("Aa")
        self._case_cb.setToolTip("Case Sensitive")
        find_row.addWidget(self._case_cb)

        self._whole_cb = QCheckBox("W")
        self._whole_cb.setToolTip("Whole Word")
        find_row.addWidget(self._whole_cb)

        btn_next = QPushButton("▼ Next")
        btn_next.clicked.connect(self._find_next)
        find_row.addWidget(btn_next)

        btn_prev = QPushButton("▲ Prev")
        btn_prev.clicked.connect(self._find_prev)
        find_row.addWidget(btn_prev)

        btn_close = QPushButton("✕")
        btn_close.setFixedWidth(28)
        btn_close.clicked.connect(self.hide)
        find_row.addWidget(btn_close)

        layout.addLayout(find_row)

        # Replace row
        self._replace_row = QWidget()
        rep_layout = QHBoxLayout(self._replace_row)
        rep_layout.setContentsMargins(0, 0, 0, 0)
        rep_layout.addWidget(QLabel("Replace:"))
        self._replace_input = QLineEdit()
        self._replace_input.setPlaceholderText("Replace with…")
        rep_layout.addWidget(self._replace_input, 1)

        btn_replace = QPushButton("Replace")
        btn_replace.clicked.connect(self._replace)
        rep_layout.addWidget(btn_replace)

        btn_all = QPushButton("All")
        btn_all.clicked.connect(self._replace_all)
        rep_layout.addWidget(btn_all)

        layout.addWidget(self._replace_row)

    def _find_flags(self) -> QTextDocument.FindFlag:
        flags = QTextDocument.FindFlag(0)
        if self._case_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self._whole_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
        return flags

    def _find_next(self) -> None:
        if not self._editor:
            return
        text = self._find_input.text()
        if not text:
            return
        if not self._editor.find(text, self._find_flags()):
            # Wrap around
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self._editor.setTextCursor(cursor)
            self._editor.find(text, self._find_flags())

    def _find_prev(self) -> None:
        if not self._editor:
            return
        text = self._find_input.text()
        if not text:
            return
        flags = self._find_flags() | QTextDocument.FindFlag.FindBackward
        if not self._editor.find(text, flags):
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self._editor.setTextCursor(cursor)
            self._editor.find(text, flags)

    def _replace(self) -> None:
        if not self._editor:
            return
        cursor = self._editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self._find_input.text():
            cursor.insertText(self._replace_input.text())
        self._find_next()

    def _replace_all(self) -> None:
        if not self._editor:
            return
        text = self._find_input.text()
        replacement = self._replace_input.text()
        if not text:
            return
        cursor = self._editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self._editor.setTextCursor(cursor)
        count = 0
        while self._editor.find(text, self._find_flags()):
            tc = self._editor.textCursor()
            tc.insertText(replacement)
            count += 1
        logger.info("Replaced %d occurrences", count)
