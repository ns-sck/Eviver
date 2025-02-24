from ui.snippet_picker import SnippetPicker
from utils.snippet_manager import SnippetManager

class SnippetHandler:
    def __init__(self, editor):
        self.editor = editor
        self.snippet_manager = SnippetManager()

    def show_snippet_picker(self):
        dialog = SnippetPicker(self.snippet_manager, self.editor)
        dialog.snippetSelected.connect(self.insert_snippet)
        dialog.exec()

    def insert_snippet(self, prefix):
        snippet_body = self.snippet_manager.get_snippet_body(prefix)
        if snippet_body:
            line, _ = self.editor.getCursorPosition()
            current_line = self.editor.text(line)
            current_indent = len(current_line) - len(current_line.lstrip())
            indent_str = " " * current_indent

            indented_snippet = "\n".join(indent_str + line for line in snippet_body.split("\n"))
            self.editor.insert(indented_snippet) 