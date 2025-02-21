from PyQt6.QtWidgets import QTreeView, QWidget, QVBoxLayout, QToolBar
from PyQt6.QtGui import QFileSystemModel, QAction, QIcon
from PyQt6.QtCore import QDir, pyqtSignal, Qt
import os

class FileBrowser(QWidget):
    fileSelected = pyqtSignal(str)  # Signal for when a file is selected

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create toolbar
        toolbar = QToolBar()
        go_up_action = QAction("⬆ Go Up", self)
        go_up_action.setStatusTip("Go to parent directory")
        go_up_action.triggered.connect(self.go_to_parent_directory)
        go_up_action.setShortcut("Alt+Up")
        toolbar.addAction(go_up_action)
        layout.addWidget(toolbar)

        # Create tree view
        self.tree_view = QTreeView()
        layout.addWidget(self.tree_view)

        # Setup file system model
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(QDir.currentPath()))
        
        # Hide unnecessary columns
        for i in range(1, 4):
            self.tree_view.hideColumn(i)

        # Connect double click signal
        self.tree_view.doubleClicked.connect(self._on_double_click)

    def _on_double_click(self, index):
        file_path = self.model.filePath(index)
        if self.model.isDir(index):  # If it's a directory
            self.tree_view.setRootIndex(index)  # Set it as the new root
        else:  # If it's a file
            self.fileSelected.emit(file_path)

    def go_to_parent_directory(self):
        current_index = self.tree_view.rootIndex()
        parent_index = current_index.parent()
        if parent_index.isValid():  # Check if parent exists (not at root)
            self.tree_view.setRootIndex(parent_index)
            self.tree_view.setCurrentIndex(current_index)  # Select the previous directory
