# importing required libraries
from PyQt6.QtGui import * 
from PyQt6.QtWidgets import (QMainWindow,
                              QVBoxLayout, 
                              QWidget, 
                              QPlainTextEdit,
                              QStatusBar, 
                              QToolBar,
                              QFileDialog, 
                              QMessageBox, 
                              QApplication,
                              )
from PyQt6.QtCore import * 
from PyQt6.QtPrintSupport import * 
from PyQt6.QtTextToSpeech import QTextToSpeech
import os
import sys
import json
import datetime

# Creating main window class
class MainWindow(QMainWindow):

    # constructor
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # creating a layout
        layout = QVBoxLayout()

        # creating a QPlainTextEdit object
        self.editor = QPlainTextEdit()

        #setting the editor properties

        font = QFont("Courier New", 20)  # Set a monospaced font for better readability
        self.editor.setFont(font)
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)  # Wrap text to the widget width
        self.editor.setPlaceholderText("Start typing here...")

        #initializing the QTextToSpeech object
        self.speech = QTextToSpeech()
        self.speech.setLocale(QLocale("en_US"))
        self.speech.setRate(0.1)  # Set the speech rate
        self.speech.setVolume(1.0)  # Set the volume
        self.speech.setPitch(0.9)  # Set the pitch

        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

        # adding editor to the layout
        layout.addWidget(self.editor)

        # creating a QWidget layout container
        container = QWidget()

        # setting layout to the container
        container.setLayout(layout)

        # making container as central widget
        self.setCentralWidget(container)

        # creating a status bar object
        self.status = QStatusBar()

        # setting status bar to the window
        self.setStatusBar(self.status)

        # creating a file tool bar
        file_toolbar = QToolBar("File")

        # adding file tool bar to the window
        self.addToolBar(file_toolbar)

        # creating a file menu
        file_menu = self.menuBar().addMenu("&File")

        # creating actions to add in the file menu
        # creating a open file action
        open_file_action = QAction("Open file", self)

        # setting status tip
        open_file_action.setStatusTip("Open file")

        # adding action to the open file
        open_file_action.triggered.connect(self.file_open)

        # adding this to file menu
        file_menu.addAction(open_file_action)

        # adding this to tool bar
        file_toolbar.addAction(open_file_action)

        # similarly creating a save action
        save_file_action = QAction("Save", self)
        save_file_action.setStatusTip("Save current page")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)

        # similarly creating save action
        saveas_file_action = QAction("Save As", self)
        saveas_file_action.setStatusTip("Save current page to specified file")
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)
        file_toolbar.addAction(saveas_file_action)

        # for print action
        print_action = QAction("Print", self)
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)
        file_toolbar.addAction(print_action)

        # creating another tool bar for editing text
        edit_toolbar = QToolBar("Edit")

        # adding this tool bar to the main window
        self.addToolBar(edit_toolbar)

        # creating a edit menu bar
        edit_menu = self.menuBar().addMenu("&Edit")

        # adding actions to the tool bar and menu bar

        # undo action
        undo_action = QAction("Undo", self)
        # adding status tip
        undo_action.setStatusTip("Undo last change")

        # when triggered undo the editor
        undo_action.triggered.connect(self.editor.undo)

        # adding this to tool and menu bar
        edit_toolbar.addAction(undo_action)
        edit_menu.addAction(undo_action)

        # redo action
        redo_action = QAction("Redo", self)
        redo_action.setStatusTip("Redo last change")

        # when triggered redo the editor
        redo_action.triggered.connect(self.editor.redo)

        # adding this to menu and tool bar
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)
        # copy action
        copy_action = QAction("Copy", self)
        copy_action.setStatusTip("Copy selected text")

        # when triggered copy the editor text
        copy_action.triggered.connect(self.editor.copy)

        # adding this to menu and tool bar
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        # paste action
        paste_action = QAction("Paste", self)
        paste_action.setStatusTip("Paste from clipboard")

        # when triggered paste the copied text
        paste_action.triggered.connect(self.editor.paste)

        # adding this to menu and tool bar
        edit_toolbar.addAction(paste_action)

        edit_menu.addAction(paste_action)

        # cut action
        cut_action = QAction("Cut", self)
        cut_action.setStatusTip("Cut selected text")

        # when triggered cut the editor text
        cut_action.triggered.connect(self.editor.cut)

        # adding this to menu and tool bar
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        # Clear action
        clear_action = QAction("Clear", self)
        clear_action.setToolTip("Clear editor text")
        # when triggered cut the editor text
        clear_action.triggered.connect(self.editor.clear)

        # adding this to menu and tool bar
        edit_toolbar.addAction(clear_action)
        edit_menu.addAction(clear_action)

        # select all action
        select_action = QAction("Select *", self)
        select_action.setStatusTip("Select all text")

        # when this triggered select the whole text
        select_action.triggered.connect(self.editor.selectAll)

        # adding this to menu and tool bar
        edit_toolbar.addAction(select_action)
        edit_menu.addAction(select_action)

        # read action

        remove_action = QAction("Remove", self)
        remove_action.setStatusTip("Remove selected text")
        # when triggered read the editor text
        remove_action.triggered.connect(self.remove_action)
        # adding this to menu and tool bar
        edit_toolbar.addAction(remove_action)

        edit_menu.addAction(remove_action)

        # insert date action
        insert_date_action = QAction("Date", self)
        insert_date_action.setToolTip("Insert date")
        # when triggered insert the current date
        insert_date_action.triggered.connect(self.insert_date)
        # adding this to menu and tool bar
        edit_toolbar.addAction(insert_date_action)
        edit_menu.addAction(insert_date_action)

        # insert time action
        insert_time_action = QAction("Time", self)
        insert_time_action.setToolTip("Insert time")
        # when triggered insert the current time
        insert_time_action.triggered.connect(self.insert_time)
        # adding this to menu and tool bar
        edit_toolbar.addAction(insert_time_action)
        edit_menu.addAction(insert_time_action)
        # inster date time action
        insert_datetime_action = QAction("Date_Time", self)
        insert_datetime_action.setToolTip("Insert date and time")
        # when triggered insert the current date and time
        insert_datetime_action.triggered.connect(self.insert_date_time)
        # adding this to menu and tool bar
        edit_toolbar.addAction(insert_datetime_action)
        edit_menu.addAction(insert_datetime_action)
        # take screenshot action
        take_screenshot_action = QAction("Screenshot", self)
        take_screenshot_action.setToolTip("Take screenshot")
        # when triggered take screenshot
        take_screenshot_action.triggered.connect(self.take_screenshot)
        # toggle theme action
        toggle_theme_action = QAction("Themes", self)
        toggle_theme_action.setToolTip("Toggle between light and dark theme")
        # when triggered toggle the theme
        toggle_theme_action.triggered.connect(self.toggle_theme)
        # adding this to menu and tool bar      
        edit_toolbar.addAction(toggle_theme_action)
        edit_menu.addAction(toggle_theme_action)
        # adding this to menu and tool bar
        edit_toolbar.addAction(take_screenshot_action)
        edit_menu.addAction(take_screenshot_action)
        audio_toolbar = QToolBar("Audio")

        # adding this tool bar to the main window
        self.addToolBar(audio_toolbar)

        # creating a edit menu bar
        audio_menu = self.menuBar().addMenu("&Audio")

        # read aloud action
        read_aloud_action = QAction("Read", self)
        read_aloud_action.setToolTip("Read text aloud")
        # when triggered read the text aloud
        read_aloud_action.triggered.connect(self.read_aloud)
        # adding this to menu and tool bar
        audio_toolbar.addAction(read_aloud_action)
        audio_menu.addAction(read_aloud_action)
        # stop reading action
        stop_reading_action = QAction("Stop", self)
        stop_reading_action.setToolTip("Stop reading text aloud")
        # when triggered stop reading the text aloud
        stop_reading_action.triggered.connect(self.stop_reading)
        # adding this to menu and tool bar
        audio_toolbar.addAction(stop_reading_action)
        audio_menu.addAction(stop_reading_action)
        # restart reading action
        restart_reading_action = QAction("Restart", self)
        restart_reading_action.setToolTip("Restart reading text aloud")
        # when triggered restart reading the text aloud
        restart_reading_action.triggered.connect(self.restart_reading)
        # adding this to menu and tool bar
        audio_toolbar.addAction(restart_reading_action)
        audio_menu.addAction(restart_reading_action)
        # read selected text action
        read_selected_text_action = QAction("Read Selected", self)
        read_selected_text_action.setToolTip("Read selected text aloud")
        # when triggered read the selected text aloud
        read_selected_text_action.triggered.connect(self.read_selected_text)
        # adding this to menu and tool bar
        audio_toolbar.addAction(read_selected_text_action)
        audio_menu.addAction(read_selected_text_action)
        # wrap action
        wrap_action = QAction("Wrap text to window", self)
        wrap_action.setStatusTip("Check to wrap text to window")

        # making it checkable
        wrap_action.setCheckable(True)

        # making it checked
        wrap_action.setChecked(True)

        # adding action
        wrap_action.triggered.connect(self.edit_toggle_wrap)

        # adding it to edit menu not to the tool bar
        edit_menu.addAction(wrap_action)

        # calling update title method
        self.update_title()

        # showing all the components
        self.show()

    # creating dialog critical method
    # to show errors
    def dialog_critical(self, s):

        # creating a QMessageBox object
        dlg = QMessageBox(self)

        # setting text to the dlg
        dlg.setText(s)

        # setting icon to it
        dlg.setIcon(QMessageBox.Icon.Critical)

        # showing it
        dlg.show()

    # action called by file open action
    def file_open(self):

        # getting path and bool value
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", 
                             "Text documents (*.txt);All files (*.*)")

        # if path is true
        if path:
            # try opening path
            try:
                with open(path,"r+") as f:
                    # read the file
                    text = f.read()

            # if some error occurred
            except Exception as e:

                # show error using critical method
                self.dialog_critical(str(e))
            # else
            else:
                # update path value
                self.path = path

                # update the text
                self.editor.setPlainText(text)

                # update the title
                self.update_title()

    # action called by file save action
    def file_save(self):

        # if there is no save path
        if self.path is None:

            # call save as method
            return self.file_saveas()

        # else call save to path method
        self._save_to_path(self.path)

    # action called by save as action
    def file_saveas(self):

        # opening path
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", 
                             "Text documents (*.txt);All files (*.*)")

        # if dialog is cancelled i.e no path is selected
        if not path:
            # return this method
            # i.e no action performed
            return

        # else call save to path method
        self._save_to_path(path)

    # save to path method
    def _save_to_path(self, path):

        # get the text
        text = self.editor.toPlainText()

        # try catch block
        try:

            # opening file to write
            with open(path, "w+") as f:

                # write text in the file
                f.write(text)

        # if error occurs
        except Exception as e:

            # show error using critical
            self.dialog_critical(str(e))

        # else do this
        else:
            # change path
            self.path = path
            # update the title
            self.update_title()

    # action called by print
    def file_print(self):

        # creating a QPrintDialog
        dlg = QPrintDialog()

        dlg.setWindowIcon(QIcon("./icon/upc.png") if os.path.exists("./icon/upc.png") else QIcon())

        # if executed
        if dlg.exec():

            # print the text
            self.editor.print(dlg.printer())

    # update title method
    def update_title(self):

        # setting window title with prefix as file name
        # suffix as PyQt5 Notepad
        self.setWindowTitle("%s - UPC Notepad" %(os.path.basename(self.path) 
                                                  if self.path else "Untitled"))

    # action called by edit toggle
    def edit_toggle_wrap(self):

        # chaining line wrap mode
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0 )

    def clear_action(self):
        # clear the editor text
        self.editor.clear()

    def remove_action(self):
        # get the text from editor
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        else:
            pass
    def insert_date(self):
        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        cursor = self.editor.textCursor()  # Get current cursor position
        cursor.insertText(current_date)  # Insert at cursor position

    def insert_time(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        cursor = self.editor.textCursor()
        cursor.insertText(current_time)

    def insert_date_time(self):
        current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        cursor = self.editor.textCursor()
        cursor.insertText(current_datetime)

    def take_screenshot(self):
        """Takes a screenshot of the primary screen and allows the user to save it."""
        screenshots_dir = "./screenshots"
        os.makedirs(screenshots_dir, exist_ok=True) # Ensure directory exists

        # Provide a default filename for convenience
        default_filename = os.path.join(screenshots_dir, f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot",
                                                   default_filename,
                                                "PNG Image (*.png);JPEG Image (*.jpg);All Files (*.*)")
        if file_path:
            screen = QApplication.primaryScreen()
            # Grabs the entire screen. For just the window, use screen.grabWindow(self.winId())
            screenshot = screen.grabWindow(0)

            if screenshot.save(file_path):
                self.status.showMessage(f"Screenshot saved as {os.path.basename(file_path)}", 5000)
            else:
                self.status.showMessage("Failed to save screenshot.", 5000)

    def read_aloud(self):
        text = self.editor.toPlainText()
        if text:
            self.speech.say(text)       

    def stop_reading(self):
        if hasattr(self, 'speech'):
            self.speech.stop()

    def restart_reading(self):
        if hasattr(self, 'speech'):
            text = self.editor.toPlainText()
            self.speech.say(text)
    # Toggle between light and dark mode
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

    def load_theme(self):
        """Loads the theme from the config.json file"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as file:
                    config = json.load(file)
                    return config.get("theme", "dark")  # Default to dark mode if not set
            except json.JSONDecodeError:
                return "dark"  # Retour au mode sombre si erreur
        return "dark"

    def save_theme(self, theme):
        """Saves the user's selected theme to config.json"""
        config = {"theme": theme}
        with open(self.CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)  # Indentation pour lisibilité

    def apply_theme(self, editor):
        """Applies the saved theme on startup"""
        theme = self.load_theme()
        if theme == "dark":
            self.editor.setStyleSheet("background-color: black; color: white;")
        else:
            self.editor.setStyleSheet("background-color: white; color: black;")

    def toggle_theme(self, editor):
        """Switches between dark and light mode"""
        current_theme = self.load_theme()
        new_theme = "light" if current_theme == "dark" else "dark"
        self.save_theme(new_theme)
        self.apply_theme(editor)

    def read_selected_text(self):
        selected_text = self.editor.textCursor().selectedText()
        if selected_text:
            self.speech = QTextToSpeech()
            self.speech.say(selected_text)

# drivers code
if __name__ == '__main__':

    # creating PyQt5 application
    app = QApplication(sys.argv)

    # setting application name
    app.setApplicationName("PyQt6-Note")

    # creating a main window object
    window = MainWindow()

    window.showMaximized()

    if os.path.exists("./icon/upc.png"):
        icon_path = os.path.join(os.path.dirname(__file__), "./icon/upc.png")
        window.setWindowIcon(QIcon(icon_path))
    else:
        pass

    window.setWindowOpacity(1.0)

    # loop
    sys.exit(app.exec())  # exit the application
