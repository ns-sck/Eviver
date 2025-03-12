from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QMessageBox
from PyQt6.QtCore import Qt
from editor.code_editor import CodeEditor
from utils.properties import *
import os

class IOManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.setup_io_widget()
        
    def setup_io_widget(self):
        self.io_widget = QWidget()
        self.io_layout = QVBoxLayout(self.io_widget)
        self.io_layout.setContentsMargins(0, 30, 0, 0)
        self.io_layout.setSpacing(0)
        
        self.io_splitter = QSplitter(Qt.Orientation.Vertical)
        self.io_layout.addWidget(self.io_splitter)
        
        self.input_editor = CodeEditor()
        self.input_editor.setWindowTitle(INPUT_FILE)
        self.input_editor.set_file_path(INPUT_PATH)
        self.io_splitter.addWidget(self.input_editor)

        self.output_editor = CodeEditor()
        self.output_editor.setWindowTitle(OUTPUT_FILE)
        self.output_editor.set_file_path(OUTPUT_PATH)
        self.io_splitter.addWidget(self.output_editor)

        self.io_widget.hide()

    def toggle_view(self):
        if self.io_widget.isVisible():
            self.io_widget.hide()
        else:
            self.io_widget.show()
            self.load_files()

    def load_files(self):
        try:
            if os.path.exists(INPUT_PATH):
                with open(INPUT_PATH, 'r') as f:
                    self.input_editor.setText(f.read())
                self.input_editor.set_file_path(INPUT_PATH)
            
            if os.path.exists(OUTPUT_PATH):
                with open(OUTPUT_PATH, 'r') as f:
                    self.output_editor.setText(f.read())
                self.output_editor.set_file_path(OUTPUT_PATH)
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Could not load I/O files: {str(e)}")

    def save_files(self):
        try:
            with open(INPUT_PATH, 'w') as f:
                f.write(self.input_editor.text())
            
            with open(OUTPUT_PATH, 'w') as f:
                f.write(self.output_editor.text())
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Could not save I/O files: {str(e)}")

    def get_widget(self):
        return self.io_widget 