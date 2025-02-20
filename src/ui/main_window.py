from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDockWidget, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from .menubar import MenuBar
from .file_browser import FileBrowser
from editor.code_editor import CodeEditor
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("CP Code Editor")
        self.setGeometry(100, 100, 1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.file_browser = FileBrowser()
        self.stacked_widget.addWidget(self.file_browser)

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        self.code_editor = CodeEditor()
        editor_layout.addWidget(self.code_editor)
        self.stacked_widget.addWidget(editor_container)

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.file_browser.fileSelected.connect(self.open_file)

    def open_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self.code_editor.setText(file.read())
                self.menu_bar.current_file = file_path
                self.setWindowTitle(f"CP Code Editor - {os.path.basename(file_path)}")
                self.stacked_widget.setCurrentIndex(1)  # Switch to editor view
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def show_file_browser(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_editor(self):
        self.stacked_widget.setCurrentIndex(1)