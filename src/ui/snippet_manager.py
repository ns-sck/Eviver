from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from utils.properties import *
import json
import os

class SnippetManager(QWidget):
    snippetSelected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.snippets = {}
        self.load_snippets()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Snippets")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 5px;
            }
        """)
        layout.addWidget(title)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search snippets...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
            }
        """)
        self.search_input.textChanged.connect(self.filter_snippets)
        self.search_input.returnPressed.connect(self.insert_selected)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Snippet list
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-radius: 4px;
                color: #FFFFFF;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 2px;
            }
            QListWidget::item:selected {
                background-color: #4A90E2;
            }
            QListWidget::item:hover {
                background-color: #3A3A3A;
            }
        """)
        self.list_widget.itemDoubleClicked.connect(self.on_snippet_selected)
        self.list_widget.installEventFilter(self)
        layout.addWidget(self.list_widget)
        
        # Insert button
        self.insert_button = QPushButton("Insert Snippet")
        self.insert_button.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: #4A90E2;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2A609A;
            }
        """)
        self.insert_button.clicked.connect(self.insert_selected)
        layout.addWidget(self.insert_button)
        
        # Set window style
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
            }
        """)
        
        self.update_list()
        
        # Set focus to search input
        self.search_input.setFocus()

    def eventFilter(self, obj, event):
        if obj == self.list_widget and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return:
                self.insert_selected()
                return True
            elif event.key() == Qt.Key.Key_Up and self.list_widget.currentRow() == 0:
                self.search_input.setFocus()
                return True
        return super().eventFilter(obj, event)

    def load_snippets(self):
        user_snippet_file = os.path.expanduser("~/.eviver/snippets.json")
        os.makedirs(os.path.dirname(user_snippet_file), exist_ok=True)
        
        # Load from resources/snippets.json
        try:
            with open(SNIPPETS_FILE, 'r') as f:
                vscode_snippets = json.load(f)
                # Convert VSCode snippets to our format
                self.snippets = {}
                for name, snippet_data in vscode_snippets.items():
                    if isinstance(snippet_data, dict) and 'body' in snippet_data:
                        if isinstance(snippet_data['body'], list):
                            content = '\n'.join(snippet_data['body'])
                        else:
                            content = snippet_data['body']
                        self.snippets[name] = content
        except Exception as e:
            self.snippets = {}
            
        # Load and merge user's custom snippets if they exist
        if os.path.exists(user_snippet_file):
            try:
                with open(user_snippet_file, 'r') as f:
                    user_snippets = json.load(f)
                    # Convert user snippets if they're in VSCode format
                    converted_snippets = {}
                    for name, snippet_data in user_snippets.items():
                        if isinstance(snippet_data, dict) and 'body' in snippet_data:
                            if isinstance(snippet_data['body'], list):
                                content = '\n'.join(snippet_data['body'])
                            else:
                                content = snippet_data['body']
                            converted_snippets[name] = content
                        else:
                            converted_snippets[name] = snippet_data
                    self.snippets.update(converted_snippets)
            except:
                pass
                
    def update_list(self, filter_text=""):
        self.list_widget.clear()
        for name, content in self.snippets.items():
            if filter_text.lower() in name.lower():
                self.list_widget.addItem(name)
                
    def filter_snippets(self, text):
        self.update_list(text)
        # Select first item if available
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            
    def insert_selected(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            self.on_snippet_selected(current_item)
            
    def on_snippet_selected(self, item):
        name = item.text()
        if name in self.snippets:
            snippet_data = self.snippets[name]
            if isinstance(snippet_data, dict):
                content = snippet_data.get('content', '')
            else:
                content = snippet_data
            self.snippetSelected.emit(content)
            
    def get_snippet(self, name):
        return self.snippets.get(name, "") 