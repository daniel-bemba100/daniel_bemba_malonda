"""Enhanced code editor with line numbers, current-line highlight, and zoom."""

import logging

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import (
    QColor, QFont, QKeyEvent, QPainter, QPaintEvent,
    QResizeEvent, QTextCursor, QWheelEvent,
)
from PyQt6.QtWidgets import QPlainTextEdit, QWidget

from src.config.constants import AppConstants
from src.editor.highlighter import SyntaxHighlighter
from src.editor.line_number_area import LineNumberArea

logger = logging.getLogger(__name__)


class CodeEditor(QPlainTextEdit):
    """Professional plain-text editor with line numbers, highlight, zoom, smart indent."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._font_size = AppConstants.DEFAULT_FONT_SIZE
        self._apply_font()
        self._line_number_area = LineNumberArea(self)
        self._highlighter = SyntaxHighlighter(self.document(), "plain")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setPlaceholderText("Start typing here…")
        self.setTabStopDistance(
            self.fontMetrics().horizontalAdvance(" ") * AppConstants.TAB_STOP_SPACES
        )
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self._update_line_number_area_width(0)
        self._highlight_current_line()

    def set_language(self, language: str) -> None:
        self._highlighter.set_language(language)

    def zoom_in(self, increment: int = 1) -> None:
        new = min(self._font_size + increment, AppConstants.MAX_FONT_SIZE)
        if new != self._font_size:
            self._font_size = new
            self._apply_font()

    def zoom_out(self, decrement: int = 1) -> None:
        new = max(self._font_size - decrement, AppConstants.MIN_FONT_SIZE)
        if new != self._font_size:
            self._font_size = new
            self._apply_font()

    def reset_zoom(self) -> None:
        self._font_size = AppConstants.DEFAULT_FONT_SIZE
        self._apply_font()

    @property
    def current_line(self) -> int:
        return self.textCursor().blockNumber() + 1

    @property
    def current_column(self) -> int:
        return self.textCursor().columnNumber() + 1

    def go_to_line(self, line: int) -> None:
        block = self.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            self.setTextCursor(cursor)
            self.centerCursor()

    def duplicate_line(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        text = cursor.selectedText()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        cursor.insertText("\n" + text)
        self.setTextCursor(cursor)

    def toggle_comment(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        text = cursor.selectedText()
        stripped = text.lstrip()
        indent = text[: len(text) - len(stripped)]
        if stripped.startswith("# "):
            new = indent + stripped[2:]
        elif stripped.startswith("#"):
            new = indent + stripped[1:]
        else:
            new = indent + "# " + stripped
        cursor.insertText(new)

    # ── Line number area ──────────────────────────────────

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        return 16 + self.fontMetrics().horizontalAdvance("9") * digits

    def line_number_area_paint_event(self, event: QPaintEvent) -> None:
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor("#2d2d2d"))
        painter.setPen(QColor("#858585"))
        block = self.firstVisibleBlock()
        num = block.blockNumber()
        offset = self.contentOffset()
        top = int(self.blockBoundingGeometry(block).translated(offset).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawText(
                    0, top, self._line_number_area.width() - 8,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, str(num + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            num += 1
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            block_text = cursor.block().text()
            indent = ""
            for ch in block_text:
                if ch in (" ", "\t"):
                    indent += ch
                else:
                    break
            if block_text.rstrip().endswith(":"):
                indent += "    "
            super().keyPressEvent(event)
            self.insertPlainText(indent)
        else:
            super().keyPressEvent(event)

    def _apply_font(self) -> None:
        font = QFont(AppConstants.DEFAULT_FONT_FAMILY, self._font_size)
        if not font.exactMatch():
            font = QFont(AppConstants.FALLBACK_FONT_FAMILY, self._font_size)
        self.setFont(font)
        self.setTabStopDistance(
            self.fontMetrics().horizontalAdvance(" ") * AppConstants.TAB_STOP_SPACES
        )
        self._update_line_number_area_width(0)

    def _update_line_number_area_width(self, _: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def _highlight_current_line(self) -> None:
        if self.isReadOnly():
            return
        from PyQt6.QtWidgets import QTextEdit
        sel = QTextEdit.ExtraSelection()
        sel.format.setBackground(QColor("#363636"))
        sel.cursor = self.textCursor()
        sel.cursor.clearSelection()
        self.setExtraSelections([sel])
