from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, 
                             QListWidget, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal

class SnippetPicker(QDialog):
    snippetSelected = pyqtSignal(str)  # Signal emitted when a snippet is selected

    def __init__(self, snippet_manager, parent=None):
        super().__init__(parent)
        self.snippet_manager = snippet_manager
        self.init_ui()
        self.setWindowTitle("Insert Snippet")

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.filter_snippets)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Snippet list
        self.snippet_list = QListWidget()
        self.snippet_list.itemDoubleClicked.connect(self.on_snippet_selected)
        layout.addWidget(self.snippet_list)

        # Populate initial list
        self.populate_snippets()

        # Set size
        self.resize(400, 300)
        
        # Set focus on search box
        self.search_box.setFocus()

    def populate_snippets(self, filter_text=""):
        self.snippet_list.clear()
        for prefix in self.snippet_manager.get_all_prefixes():
            snippet = self.snippet_manager.get_snippet(prefix)
            if filter_text.lower() in prefix.lower() or \
               filter_text.lower() in snippet.get('description', '').lower():
                item_text = f"{prefix} - {snippet.get('description', '')}"
                self.snippet_list.addItem(item_text)

    def filter_snippets(self, text):
        self.populate_snippets(text)

    def on_snippet_selected(self, item):
        # Extract prefix from the item text (prefix - description)
        prefix = item.text().split(' - ')[0]
        self.snippetSelected.emit(prefix)
        self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and self.snippet_list.count() > 0:
            # If Enter is pressed and there are items, select the first one
            prefix = self.snippet_list.item(0).text().split(' - ')[0]
            self.snippetSelected.emit(prefix)
            self.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event) 