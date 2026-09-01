"""Multi-tab document manager using QTabWidget."""

import logging
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QTabWidget, QWidget, QMessageBox

from src.core.document import Document
from src.core.file_manager import FileManager
from src.editor.code_editor import CodeEditor

logger = logging.getLogger(__name__)


class TabManager(QTabWidget):
    """Manages multiple editor tabs, each with its own Document and CodeEditor."""

    # Emitted whenever the active document changes
    active_document_changed = pyqtSignal(object)  # Document or None
    # Emitted when any document's modified state changes
    document_modified_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_tab_changed)
        self._documents: list[Document] = []
        # Create initial empty tab
        self.new_tab()

    @property
    def current_editor(self) -> CodeEditor | None:
        w = self.currentWidget()
        return w if isinstance(w, CodeEditor) else None

    @property
    def current_document(self) -> Document | None:
        idx = self.currentIndex()
        if 0 <= idx < len(self._documents):
            return self._documents[idx]
        return None

    def new_tab(self, path: str | None = None) -> int:
        """Create a new tab. If *path* is given, load the file."""
        editor = CodeEditor()
        doc = Document(path=path)

        if path:
            try:
                content, encoding = FileManager.read_file(path)
                editor.setPlainText(content)
                doc.encoding = encoding
                doc.is_modified = False
                editor.set_language(doc.language)
            except Exception as e:
                logger.error("Failed to open %s: %s", path, e)
                QMessageBox.critical(None, "Error", str(e))
                return -1

        editor.modificationChanged.connect(
            lambda modified, d=doc: self._on_modification_changed(d, modified)
        )

        self._documents.append(doc)
        idx = self.addTab(editor, doc.title)
        self.setCurrentIndex(idx)
        return idx

    def open_file_in_tab(self, path: str) -> int:
        """Open a file. If already open, switch to its tab."""
        for i, doc in enumerate(self._documents):
            if doc.path == path:
                self.setCurrentIndex(i)
                return i
        return self.new_tab(path)

    def close_tab(self, index: int) -> bool:
        """Close a tab, prompting to save if modified. Returns False if cancelled."""
        if index < 0 or index >= len(self._documents):
            return False

        doc = self._documents[index]
        if doc.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                f"'{doc.filename}' has unsaved changes.\nDo you want to save before closing?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return False
            if reply == QMessageBox.StandardButton.Save:
                if not self.save_current():
                    return False

        self._documents.pop(index)
        self.removeTab(index)

        # Always keep at least one tab
        if self.count() == 0:
            self.new_tab()

        return True

    def save_current(self) -> bool:
        """Save the current tab's document. Returns True on success."""
        doc = self.current_document
        editor = self.current_editor
        if not doc or not editor:
            return False

        if doc.path is None:
            return False  # Caller should use save_as

        try:
            FileManager.write_file(doc.path, editor.toPlainText(), doc.encoding)
            doc.is_modified = False
            self._update_tab_title(self.currentIndex())
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))
            return False

    def save_current_as(self, path: str) -> bool:
        """Save the current document to a new path."""
        doc = self.current_document
        editor = self.current_editor
        if not doc or not editor:
            return False

        try:
            FileManager.write_file(path, editor.toPlainText())
            doc.path = path
            doc.is_modified = False
            editor.set_language(doc.language)
            self._update_tab_title(self.currentIndex())
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))
            return False

    def _on_tab_changed(self, index: int) -> None:
        doc = self._documents[index] if 0 <= index < len(self._documents) else None
        self.active_document_changed.emit(doc)

    def _on_modification_changed(self, doc: Document, modified: bool) -> None:
        doc.is_modified = modified
        idx = self._documents.index(doc) if doc in self._documents else -1
        if idx >= 0:
            self._update_tab_title(idx)
        self.document_modified_changed.emit()

    def _update_tab_title(self, index: int) -> None:
        if 0 <= index < len(self._documents):
            self.setTabText(index, self._documents[index].title)
