from PyQt6.QtWidgets import QWidget
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from .custom_lexer import LexerCPP
# from .syntax_highlighter import PythonSyntaxHighlighter

class CodeEditor(QsciScintilla):
    def __init__(self):
        super().__init__()
        self.init_editor()
        self.init_custom_behavior()

    def init_editor(self):
        # font = QFont('Consolas', 20)
        # self.setFont(font)

        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(Qt.GlobalColor.darkGray)

        self.setAutoIndent(False)
        self.setIndentationGuides(True)
        self.setTabWidth(2)
        self.setIndentationsUseTabs(False)

        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)

        self.setColor(QColor("#FFFFFF"))
        self.setPaper(QColor("#2B2B2B"))
        self.setIndentationGuides(False)
       
        self.setCaretWidth(2)
        self.setCaretForegroundColor(QColor("#FFFFFF"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#2A2A2A"))

        self.lexer = LexerCPP(self)
        self.setLexer(self.lexer)

        self.setMarginsBackgroundColor(QColor("#111111"))
        self.setMarginWidth(0, "000")
        self.setMarginWidth(1, "0")

    def init_custom_behavior(self):
        self.keyPressEvent = self.custom_key_press_event

    def custom_key_press_event(self, event):
        pairs = {
            "(": ")",
            "[": "]",
            "{": "}",
            '"': '"',
            "'": "'"
        }
        
        if event.text() in pairs:
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