from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                            QLabel, QToolBar, QHBoxLayout)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, Qt
from utils.properties import DEFAULT_WORKSPACE_DIR
import os

class FileBrowser(QWidget):
    fileSelected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Create default workspace directory if it doesn't exist
        os.makedirs(DEFAULT_WORKSPACE_DIR, exist_ok=True)
        self.current_path = DEFAULT_WORKSPACE_DIR
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.path_label = QLabel()
        self.path_label.setStyleSheet("background-color: #2B2B2B; color: white; padding: 5px;")
        layout.addWidget(self.path_label)

        toolbar = QToolBar()
        toolbar.setStyleSheet("background-color: #2B2B2B;")

        self.up_action = toolbar.addAction("⬆ Up")
        self.up_action.triggered.connect(self.go_to_parent_directory)
        self.up_action.setShortcut("Alt+Up")
        
        self.home_action = toolbar.addAction("🏠 Home")
        self.home_action.triggered.connect(lambda: self.change_directory(os.path.expanduser("~")))
        
        self.refresh_action = toolbar.addAction("🔄 Refresh")
        self.refresh_action.triggered.connect(lambda: self.change_directory(self.current_path))
        
        layout.addWidget(toolbar)

        # Create file list
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                color: white;
                border: none;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #3e3e3e;
            }
        """)
        self.file_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.file_list.setAlternatingRowColors(True)
        layout.addWidget(self.file_list)

        # Status bar
        self.status_bar = QLabel()
        self.status_bar.setStyleSheet("background-color: #2B2B2B; color: white; padding: 5px;")
        layout.addWidget(self.status_bar)

        self.change_directory(self.current_path)

    def change_directory(self, path):
        try:
            os.chdir(path)
            self.current_path = path
            self.path_label.setText(f" 📁 {path}")
            self.refresh_file_list()
        except Exception as e:
            self.status_bar.setText(f"Error: {str(e)}")

    def refresh_file_list(self):
        self.file_list.clear()
        try:
            parent_item = QListWidgetItem("..")
            parent_item.setData(Qt.ItemDataRole.UserRole, os.path.dirname(self.current_path))
            self.file_list.addItem(parent_item)

            items = os.listdir(self.current_path)
            
            dirs = []
            files = []
            for item in items:
                full_path = os.path.join(self.current_path, item)
                if os.path.isdir(full_path):
                    dirs.append(item)
                else:
                    files.append(item)

            for dir_name in sorted(dirs):
                item = QListWidgetItem(f"📁 {dir_name}")
                item.setData(Qt.ItemDataRole.UserRole, os.path.join(self.current_path, dir_name))
                self.file_list.addItem(item)

            for file_name in sorted(files):
                item = QListWidgetItem(f"📄 {file_name}")
                item.setData(Qt.ItemDataRole.UserRole, os.path.join(self.current_path, file_name))
                self.file_list.addItem(item)

            self.status_bar.setText(f"{len(dirs)} directories, {len(files)} files")

        except Exception as e:
            self.status_bar.setText(f"Error: {str(e)}")

    def _on_item_double_clicked(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if os.path.isdir(path):
            self.change_directory(path)
        else:
            self.fileSelected.emit(path)

    def go_to_parent_directory(self):
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir != self.current_path:
            self.change_directory(parent_dir)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            current_item = self.file_list.currentItem()
            if current_item:
                self._on_item_double_clicked(current_item)
        elif event.key() == Qt.Key.Key_Backspace:
            self.go_to_parent_directory()
        else:
            super().keyPressEvent(event)
