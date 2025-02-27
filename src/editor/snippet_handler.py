from PyQt6.QtWidgets import QDialog, QVBoxLayout
from ui.snippet_manager import SnippetManager

class SnippetHandler:
    def __init__(self, editor):
        self.editor = editor
        self.dialog = None

    def show_snippet_picker(self):
        self.dialog = QDialog(self.editor)
        self.dialog.setWindowTitle("Snippets")
        layout = QVBoxLayout(self.dialog)
        
        snippet_manager = SnippetManager()
        layout.addWidget(snippet_manager)
        snippet_manager.snippetSelected.connect(self.insert_snippet)
        
        self.dialog.resize(600, 400)
        self.dialog.exec()

    def insert_snippet(self, snippet_body):
        if not snippet_body:
            return
            
        if not self.editor:
            return
            
        try:
            line, index = self.editor.getCursorPosition()
            current_line = self.editor.text(line)
            indent = len(current_line.expandtabs(self.editor.tabWidth())) - len(current_line.expandtabs(self.editor.tabWidth()).lstrip())
            indent_str = "\t" * (indent // self.editor.tabWidth())

            lines = snippet_body.split("\n")
            indented_lines = []
            if lines:
                indented_lines.append(lines[0])  # First line uses existing indentation
                indented_lines.extend([indent_str + line if line.strip() else line for line in lines[1:]])
            
            indented_snippet = "\n".join(indented_lines)
            self.editor.insert(indented_snippet)
            
            if self.dialog:
                self.dialog.accept()
        except:
            pass 