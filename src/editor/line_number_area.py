"""Line number gutter widget for the code editor."""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QColor, QPainter, QPaintEvent
from PyQt6.QtWidgets import QWidget


class LineNumberArea(QWidget):
    """A gutter widget that displays line numbers alongside the editor.

    This widget is sized and painted by the parent ``CodeEditor``.
    It delegates all painting to ``CodeEditor.line_number_area_paint_event``.
    """

    def __init__(self, editor: "QWidget") -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:
        self._editor.line_number_area_paint_event(event)
