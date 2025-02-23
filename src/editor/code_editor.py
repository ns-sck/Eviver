from PyQt6.QtWidgets import QWidget
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from .custom_lexer import LexerCPP
from utils.snippet_manager import SnippetManager
from ui.snippet_picker import SnippetPicker
from utils.properties import *
# from .syntax_highlighter import PythonSyntaxHighlighter

class CodeEditor(QsciScintilla):
    def __init__(self):
        super().__init__()
        self.init_editor()
        self.init_custom_behavior()
        self.snippet_manager = SnippetManager()

    def init_editor(self):
        self.setFont(EDITOR_FONT)

        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(Qt.GlobalColor.darkGray)

        self.setAutoIndent(False)
        self.setIndentationGuides(True)
        self.setTabWidth(EDITOR_TAB_WIDTH)
        self.setIndentationsUseTabs(EDITOR_USE_TABS)

        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)

        self.setColor(EDITOR_TEXT_COLOR)
        self.setPaper(EDITOR_BACKGROUND_COLOR)
        self.setIndentationGuides(False)
       
        self.setCaretWidth(EDITOR_CARET_WIDTH)
        self.setCaretForegroundColor(EDITOR_CARET_COLOR)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(EDITOR_CARET_LINE_COLOR)

        self.lexer = LexerCPP(self)
        self.setLexer(self.lexer)

        self.setMarginsBackgroundColor(EDITOR_MARGIN_BACKGROUND_COLOR)
        self.setMarginWidth(0, "000")
        self.setMarginWidth(1, "0")

    def init_custom_behavior(self):
        self.keyPressEvent = self.custom_key_press_event

    def show_snippet_picker(self):
        dialog = SnippetPicker(self.snippet_manager, self)
        dialog.snippetSelected.connect(self.insert_snippet)
        dialog.exec()

    def insert_snippet(self, prefix):
        snippet_body = self.snippet_manager.get_snippet_body(prefix)
        if snippet_body:
            # Get current indentation
            line, _ = self.getCursorPosition()
            current_line = self.text(line)
            current_indent = len(current_line) - len(current_line.lstrip())
            indent_str = " " * current_indent

            # Insert the snippet with proper indentation
            indented_snippet = "\n".join(indent_str + line for line in snippet_body.split("\n"))
            self.insert(indented_snippet)

    def custom_key_press_event(self, event):
        # Check for snippet picker shortcut (Ctrl+J)
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_J:
            self.show_snippet_picker()
            return

        if event.text() in {"(", "[", "{", '"', "'"}:
            pairs = {
                "(": ")",
                "[": "]",
                "{": "}",
                '"': '"',
                "'": "'"
            }
            line, index = self.getCursorPosition()
            self.insert(event.text())
            self.setCursorPosition(line, index + 1)
            self.insert(pairs[event.text()])
            
        elif event.key() == Qt.Key.Key_Return:
            line, index = self.getCursorPosition()
            current_line = self.text(line)

            if (index > 0 and index < len(current_line) and 
                current_line[index-1] == "{" and current_line[index] == "}"):

                indent = len(current_line) - len(current_line.lstrip())
                indent_str = "\t" * indent
                
                total_position = self.positionFromLineIndex(line, index)  # Get current caret position
                self.SendScintilla(self.SCI_DELETERANGE, total_position, 1)
                fixup = "\n" + indent_str + "\t" + "\n" + indent * "\t" + "}"
                self.insert(fixup)
                self.setCursorPosition(line + 1, self.lineLength(line + 1) - 1)
            else:
                indent = len(current_line) - len(current_line.lstrip())
                QsciScintilla.keyPressEvent(self, event)
                self.insert("\t" * (indent // 2))
                self.setCursorPosition(line + 1, (indent // 2))
            
        elif event.key() == Qt.Key.Key_Tab:
            line, index = self.getCursorPosition()
            self.insert("\t")
            self.setCursorPosition(line, index + 1)
            
        else:
            QsciScintilla.keyPressEvent(self, event)

        # Set syntax highlighting
        # self.syntax_highlighter = PythonSyntaxHighlighter(self) 