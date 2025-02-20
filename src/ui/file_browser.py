from PyQt6.QtWidgets import QTreeView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir, pyqtSignal

class FileBrowser(QTreeView):
    fileSelected = pyqtSignal(str)  # Signal for when a file is selected

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        self.setModel(self.model)
        self.setRootIndex(self.model.index(QDir.currentPath()))
        
        # Hide unnecessary columns
        for i in range(1, 4):
            self.hideColumn(i)

        # Connect double click signal
        self.doubleClicked.connect(self._on_double_click)

    def _on_double_click(self, index):
        file_path = self.model.filePath(index)
        if not self.model.isDir(index):  # Only emit if it's a file
            self.fileSelected.emit(file_path)
