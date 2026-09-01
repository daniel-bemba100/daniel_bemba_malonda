"""Main window — assembles all components into the application shell."""

import logging
import os

from PyQt6.QtCore import QDate, QDateTime, QTime, Qt, QTimer
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtPrintSupport import QPrintDialog
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QInputDialog, QMainWindow,
    QMessageBox, QToolBar, QVBoxLayout, QWidget,
)

from src.config.constants import AppConstants
from src.config.settings import SettingsManager
from src.editor.tab_manager import TabManager
from src.features.find_replace import FindReplaceBar
from src.features.screenshot import ScreenshotCapture
from src.features.statistics import TextStatistics
from src.features.tts_engine import TTSEngine
from src.ui.statusbar import EnhancedStatusBar
from src.ui.themes import ThemeManager
from src.utils.paths import icon_path

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """The main application window."""

    def __init__(self, settings: SettingsManager) -> None:
        super().__init__()
        self._settings = settings
        self._theme_mgr = ThemeManager(settings)
        self._tts = TTSEngine(self)

        self._setup_window()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_menus_and_toolbars()
        self._setup_auto_save()
        self._connect_signals()
        self._theme_mgr.apply()
        self._restore_geometry()

    # ══════════════════════════════════════════════════════════
    #  SETUP
    # ══════════════════════════════════════════════════════════

    def _setup_window(self) -> None:
        self.setWindowTitle(AppConstants.APP_NAME)
        self.setMinimumSize(800, 600)
        self.setAcceptDrops(True)

        icon_file = icon_path()
        if icon_file.exists():
            self.setWindowIcon(QIcon(str(icon_file)))

    def _setup_central_widget(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._tabs = TabManager()
        self._find_bar = FindReplaceBar()
        self._find_bar.setObjectName("findReplaceBar")

        layout.addWidget(self._tabs, 1)
        layout.addWidget(self._find_bar)

        self.setCentralWidget(central)

    def _setup_status_bar(self) -> None:
        self._status = EnhancedStatusBar()
        self.setStatusBar(self._status)

    def _setup_auto_save(self) -> None:
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.timeout.connect(self._auto_save)
        if self._settings.get("auto_save_enabled", True):
            interval = self._settings.get(
                "auto_save_interval_ms", AppConstants.AUTO_SAVE_INTERVAL_MS
            )
            self._auto_save_timer.start(interval)

    def _connect_signals(self) -> None:
        self._tabs.active_document_changed.connect(self._on_doc_changed)
        self._tabs.document_modified_changed.connect(self._update_title)
        self._tabs.currentChanged.connect(self._on_tab_switched)
        # Connect to current editor signals
        self._connect_editor_signals()

    def _connect_editor_signals(self) -> None:
        editor = self._tabs.current_editor
        if editor:
            editor.cursorPositionChanged.connect(self._update_cursor_info)
            editor.textChanged.connect(self._update_statistics)
            self._find_bar.set_editor(editor)
            self._update_cursor_info()
            self._update_statistics()

    # ══════════════════════════════════════════════════════════
    #  MENUS & TOOLBARS
    # ══════════════════════════════════════════════════════════

    def _setup_menus_and_toolbars(self) -> None:
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_snippets_menu()
        self._create_audio_menu()

    def _create_file_menu(self) -> None:
        menu = self.menuBar().addMenu("&File")
        toolbar = QToolBar("File")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        actions = [
            ("New", "Ctrl+N", "New file", self._file_new),
            ("Open", "Ctrl+O", "Open file", self._file_open),
            (None, None, None, None),  # separator
            ("Save", "Ctrl+S", "Save file", self._file_save),
            ("Save As", "Ctrl+Shift+S", "Save file as", self._file_save_as),
            (None, None, None, None),
            ("Print", "Ctrl+P", "Print document", self._file_print),
            (None, None, None, None),
            ("Close Tab", "Ctrl+W", "Close current tab", self._file_close_tab),
        ]
        for name, shortcut, tip, slot in actions:
            if name is None:
                menu.addSeparator()
                continue
            action = QAction(name, self)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            if tip:
                action.setStatusTip(tip)
            action.triggered.connect(slot)
            menu.addAction(action)
            if name in ("New", "Open", "Save", "Print"):
                toolbar.addAction(action)

        # Recent files submenu
        menu.addSeparator()
        self._recent_menu = menu.addMenu("Recent Files")
        self._update_recent_menu()

        menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

    def _create_snippets_menu(self) -> None:
        menu = self.menuBar().addMenu("&Snippets")
        
        save_action = QAction("Save Current as Snippet", self)
        save_action.triggered.connect(self._save_snippet)
        menu.addAction(save_action)
        
        load_action = QAction("Load Snippet...", self)
        load_action.triggered.connect(self._load_snippet)
        menu.addAction(load_action)

    def _create_edit_menu(self) -> None:
        menu = self.menuBar().addMenu("&Edit")
        toolbar = QToolBar("Edit")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        actions = [
            ("Undo", "Ctrl+Z", self._edit_undo),
            ("Redo", "Ctrl+Y", self._edit_redo),
            (None, None, None),
            ("Cut", "Ctrl+X", self._edit_cut),
            ("Copy", "Ctrl+C", self._edit_copy),
            ("Paste", "Ctrl+V", self._edit_paste),
            ("Select All", "Ctrl+A", self._edit_select_all),
            (None, None, None),
            ("Find", "Ctrl+F", self._show_find),
            ("Replace", "Ctrl+H", self._show_replace),
            ("Go to Line", "Ctrl+G", self._go_to_line),
            (None, None, None),
            ("Duplicate Line", "Ctrl+D", self._duplicate_line),
            ("Toggle Comment", "Ctrl+/", self._toggle_comment),
            (None, None, None),
            ("Insert Date", None, self._insert_date),
            ("Insert Time", None, self._insert_time),
            ("Insert DateTime", None, self._insert_datetime),
        ]
        for item in actions:
            if item[0] is None:
                menu.addSeparator()
                toolbar.addSeparator()
                continue
            name, shortcut, slot = item
            action = QAction(name, self)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(slot)
            menu.addAction(action)
            if name in ("Undo", "Redo", "Cut", "Copy", "Paste", "Find"):
                toolbar.addAction(action)

    def _create_view_menu(self) -> None:
        menu = self.menuBar().addMenu("&View")

        # Zoom
        zi = QAction("Zoom In", self)
        zi.setShortcut(QKeySequence("Ctrl++"))
        zi.triggered.connect(self._zoom_in)
        menu.addAction(zi)

        zo = QAction("Zoom Out", self)
        zo.setShortcut(QKeySequence("Ctrl+-"))
        zo.triggered.connect(self._zoom_out)
        menu.addAction(zo)

        zr = QAction("Reset Zoom", self)
        zr.setShortcut(QKeySequence("Ctrl+0"))
        zr.triggered.connect(self._zoom_reset)
        menu.addAction(zr)

        menu.addSeparator()

        # Word wrap toggle
        wrap = QAction("Word Wrap", self)
        wrap.setCheckable(True)
        wrap.setChecked(True)
        wrap.triggered.connect(self._toggle_wrap)
        menu.addAction(wrap)

        menu.addSeparator()

        # Theme toggle
        theme = QAction("Toggle Theme", self)
        theme.setShortcut(QKeySequence("Ctrl+T"))
        theme.triggered.connect(self._toggle_theme)
        menu.addAction(theme)

        menu.addSeparator()

        # Screenshot
        ss = QAction("Screenshot", self)
        ss.triggered.connect(self._take_screenshot)
        menu.addAction(ss)

    def _create_audio_menu(self) -> None:
        menu = self.menuBar().addMenu("&Audio")
        toolbar = QToolBar("Audio")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        actions = [
            ("▶ Read Aloud", self._tts_read),
            ("⏹ Stop", self._tts_stop),
            ("🔁 Restart", self._tts_restart),
            ("📋 Read Selection", self._tts_read_selection),
            (None, None),
            ("💾 Export Audio", self._tts_export),
        ]
        for item in actions:
            if item[0] is None:
                menu.addSeparator()
                toolbar.addSeparator()
                continue
            name, slot = item
            action = QAction(name, self)
            action.triggered.connect(slot)
            menu.addAction(action)
            toolbar.addAction(action)

    # ══════════════════════════════════════════════════════════
    #  FILE ACTIONS
    # ══════════════════════════════════════════════════════════

    def _file_new(self) -> None:
        self._tabs.new_tab()

    def _file_open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", AppConstants.FILE_FILTER
        )
        if path:
            self._tabs.open_file_in_tab(path)
            self._settings.add_recent_file(path)
            self._update_recent_menu()

    def _file_save(self) -> None:
        doc = self._tabs.current_document
        if doc and doc.path:
            self._tabs.save_current()
            self._status.flash_message(f"Saved: {doc.filename}")
        else:
            self._file_save_as()

    def _file_save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", AppConstants.FILE_FILTER
        )
        if path:
            self._tabs.save_current_as(path)
            self._settings.add_recent_file(path)
            self._update_recent_menu()
            self._status.flash_message(f"Saved: {os.path.basename(path)}")

    def _file_print(self) -> None:
        dlg = QPrintDialog(self)
        if dlg.exec():
            editor = self._tabs.current_editor
            if editor:
                editor.print(dlg.printer())

    def _file_close_tab(self) -> None:
        self._tabs.close_tab(self._tabs.currentIndex())

    # ══════════════════════════════════════════════════════════
    #  EDIT ACTIONS
    # ══════════════════════════════════════════════════════════

    def _edit_undo(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.undo()

    def _edit_redo(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.redo()

    def _edit_cut(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.cut()

    def _edit_copy(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.copy()

    def _edit_paste(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.paste()

    def _edit_select_all(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.selectAll()

    def _show_find(self) -> None:
        self._find_bar.show_find()

    def _show_replace(self) -> None:
        self._find_bar.show_replace()

    def _go_to_line(self) -> None:
        editor = self._tabs.current_editor
        if not editor:
            return
        max_line = editor.document().blockCount()
        line, ok = QInputDialog.getInt(
            self, "Go to Line", f"Line number (1–{max_line}):",
            editor.current_line, 1, max_line,
        )
        if ok:
            editor.go_to_line(line)

    def _duplicate_line(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.duplicate_line()

    def _toggle_comment(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.toggle_comment()

    def _insert_date(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.textCursor().insertText(
                QDate.currentDate().toString("yyyy-MM-dd")
            )

    def _insert_time(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.textCursor().insertText(
                QTime.currentTime().toString("HH:mm:ss")
            )

    def _insert_datetime(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.textCursor().insertText(
                QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            )

    # ══════════════════════════════════════════════════════════
    #  VIEW ACTIONS
    # ══════════════════════════════════════════════════════════

    def _zoom_in(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.zoom_in()

    def _zoom_out(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.zoom_out()

    def _zoom_reset(self) -> None:
        e = self._tabs.current_editor
        if e:
            e.reset_zoom()

    def _toggle_wrap(self, checked: bool) -> None:
        from PyQt6.QtWidgets import QPlainTextEdit
        e = self._tabs.current_editor
        if e:
            mode = (
                QPlainTextEdit.LineWrapMode.WidgetWidth
                if checked
                else QPlainTextEdit.LineWrapMode.NoWrap
            )
            e.setLineWrapMode(mode)

    def _toggle_theme(self) -> None:
        new = self._theme_mgr.toggle()
        self._status.flash_message(f"Theme: {new.title()}")

    def _take_screenshot(self) -> None:
        path = ScreenshotCapture.capture(self)
        if path:
            self._status.flash_message(f"Screenshot saved: {os.path.basename(path)}")

    # ══════════════════════════════════════════════════════════
    #  AUDIO ACTIONS
    # ══════════════════════════════════════════════════════════

    def _tts_read(self) -> None:
        e = self._tabs.current_editor
        if e:
            text = e.toPlainText().strip()
            if text:
                self._tts.say(text)
            else:
                self._status.flash_message("No text to read")

    def _tts_stop(self) -> None:
        self._tts.stop()

    def _tts_restart(self) -> None:
        self._tts.stop()
        self._tts_read()

    def _tts_read_selection(self) -> None:
        e = self._tabs.current_editor
        if e:
            sel = e.textCursor().selectedText()
            if sel:
                self._tts.say(sel)

    def _tts_export(self) -> None:
        e = self._tabs.current_editor
        if e:
            try:
                self._tts.export_to_mp3(e.toPlainText())
            except Exception as ex:
                QMessageBox.critical(self, "Export Error", str(ex))

    # ══════════════════════════════════════════════════════════
    #  STATUS BAR UPDATES
    # ══════════════════════════════════════════════════════════

    def _update_cursor_info(self) -> None:
        e = self._tabs.current_editor
        if e:
            self._status.update_cursor(e.current_line, e.current_column)

    def _update_statistics(self) -> None:
        e = self._tabs.current_editor
        if e:
            stats = TextStatistics.compute(e.toPlainText())
            self._status.update_statistics(stats["words"], stats["chars"])

    def _on_doc_changed(self, doc) -> None:
        if doc:
            self._status.update_encoding(doc.encoding)
            self._status.update_language(doc.language)
        self._update_title()

    def _on_tab_switched(self, _idx: int) -> None:
        self._connect_editor_signals()
        doc = self._tabs.current_document
        if doc:
            self._status.update_encoding(doc.encoding)
            self._status.update_language(doc.language)
        self._update_title()

    def _update_title(self) -> None:
        doc = self._tabs.current_document
        if doc:
            self.setWindowTitle(
                AppConstants.WINDOW_TITLE_TEMPLATE.format(
                    filename=doc.title, app_name=AppConstants.APP_NAME
                )
            )
        else:
            self.setWindowTitle(AppConstants.APP_NAME)

    # ══════════════════════════════════════════════════════════
    #  RECENT FILES
    # ══════════════════════════════════════════════════════════

    def _update_recent_menu(self) -> None:
        self._recent_menu.clear()
        recent = self._settings.get("recent_files", [])
        if not recent:
            no_recent = QAction("(No recent files)", self)
            no_recent.setEnabled(False)
            self._recent_menu.addAction(no_recent)
            return
        for path in recent:
            action = QAction(os.path.basename(path), self)
            action.setStatusTip(path)
            action.setData(path)
            action.triggered.connect(
                lambda checked, p=path: self._open_recent(p)
            )
            self._recent_menu.addAction(action)
        self._recent_menu.addSeparator()
        clear = QAction("Clear Recent Files", self)
        clear.triggered.connect(self._clear_recent)
        self._recent_menu.addAction(clear)

    def _open_recent(self, path: str) -> None:
        if os.path.exists(path):
            self._tabs.open_file_in_tab(path)
        else:
            QMessageBox.warning(self, "File Not Found", f"Cannot find:\n{path}")

    def _clear_recent(self) -> None:
        self._settings.clear_recent_files()
        self._update_recent_menu()

    # ══════════════════════════════════════════════════════════
    #  SNIPPETS ACTIONS
    # ══════════════════════════════════════════════════════════

    def _save_snippet(self) -> None:
        editor = self._tabs.current_editor
        doc = self._tabs.current_document
        if not editor or not doc:
            return
        
        content = editor.toPlainText().strip()
        if not content:
            self._status.flash_message("Cannot save empty snippet")
            return

        title, ok = QInputDialog.getText(self, "Save Snippet", "Snippet Title:", text=doc.filename)
        if ok and title:
            # We access the _db instance from settings since it's instantiated there
            db = self._settings._db
            snippet_id = db.add_snippet(title, content, doc.language)
            if snippet_id != -1:
                self._status.flash_message(f"Snippet '{title}' saved to database.")
            else:
                QMessageBox.critical(self, "Database Error", "Failed to save snippet.")

    def _load_snippet(self) -> None:
        db = self._settings._db
        snippets = db.get_all_snippets()
        
        if not snippets:
            QMessageBox.information(self, "Snippets", "No snippets found in the database.")
            return

        items = [f"{s['id']}: {s['title']} ({s['language']})" for s in snippets]
        item, ok = QInputDialog.getItem(self, "Load Snippet", "Select Snippet:", items, 0, False)
        
        if ok and item:
            snippet_id = int(item.split(':')[0])
            snippet = next((s for s in snippets if s['id'] == snippet_id), None)
            if snippet:
                self._tabs.new_tab()
                editor = self._tabs.current_editor
                doc = self._tabs.current_document
                if editor and doc:
                    editor.setPlainText(snippet['content'])
                    doc.language = snippet['language']
                    editor.set_language(snippet['language'])
                    doc.path = None
                    self._tabs.setTabText(self._tabs.currentIndex(), snippet['title'])
                    self._status.flash_message(f"Loaded snippet '{snippet['title']}'")

    # ══════════════════════════════════════════════════════════
    #  AUTO-SAVE
    # ══════════════════════════════════════════════════════════

    def _auto_save(self) -> None:
        doc = self._tabs.current_document
        if doc and doc.path and doc.is_modified:
            self._tabs.save_current()
            self._status.flash_message("Auto-saved", 2000)

    # ══════════════════════════════════════════════════════════
    #  DRAG & DROP
    # ══════════════════════════════════════════════════════════

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path and os.path.isfile(path):
                self._tabs.open_file_in_tab(path)
                self._settings.add_recent_file(path)
        self._update_recent_menu()

    # ══════════════════════════════════════════════════════════
    #  WINDOW STATE PERSISTENCE
    # ══════════════════════════════════════════════════════════

    def _restore_geometry(self) -> None:
        geo = self._settings.get("window_geometry")
        if geo:
            from PyQt6.QtCore import QByteArray
            self.restoreGeometry(QByteArray.fromHex(geo.encode()))
        else:
            self.showMaximized()

    def closeEvent(self, event) -> None:
        self._settings.set(
            "window_geometry",
            bytes(self.saveGeometry().toHex()).decode()
        )
        # Check all tabs for unsaved changes
        for i in range(self._tabs.count() - 1, -1, -1):
            doc = self._tabs._documents[i] if i < len(self._tabs._documents) else None
            if doc and doc.is_modified:
                self._tabs.setCurrentIndex(i)
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    f"'{doc.filename}' has unsaved changes. Save?",
                    QMessageBox.StandardButton.Save
                    | QMessageBox.StandardButton.Discard
                    | QMessageBox.StandardButton.Cancel,
                )
                if reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
                if reply == QMessageBox.StandardButton.Save:
                    if doc.path:
                        self._tabs.save_current()
                    else:
                        self._file_save_as()
        event.accept()
