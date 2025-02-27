from PyQt6.QtWidgets import QWidget
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from .custom_lexer import LexerCPP
from utils.properties import *
from .find_replace_dialog import FindReplaceDialog
from .snippet_handler import SnippetHandler

class CodeEditor(QsciScintilla):
    def __init__(self):
        super().__init__()
        self.init_editor()
        self.init_custom_behavior()
        self.find_dialog = None
        self.replace_dialog = None
        self.snippet_handler = SnippetHandler(self)
        
        # Enable focus and keyboard tracking
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def init_editor(self):
        # Set font
        self.setFont(EDITOR_FONT)
        
        # Set margins
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(Qt.GlobalColor.darkGray)

        # Set indentation
        self.setAutoIndent(False)
        self.setIndentationGuides(True)
        self.setTabWidth(EDITOR_TAB_WIDTH)
        self.setIndentationsUseTabs(EDITOR_USE_TABS)

        # Set brace matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setMatchedBraceBackgroundColor(EDITOR_BRACE_MATCHED_BG_COLOR)
        self.setMatchedBraceForegroundColor(EDITOR_BRACE_MATCHED_FG_COLOR)
        self.setUnmatchedBraceBackgroundColor(EDITOR_BRACE_UNMATCHED_BG_COLOR)
        self.setUnmatchedBraceForegroundColor(EDITOR_BRACE_UNMATCHED_FG_COLOR)

        # Set colors
        self.setColor(EDITOR_TEXT_COLOR)
        self.setPaper(EDITOR_BACKGROUND_COLOR)
        self.setIndentationGuides(False)
        self.setSelectionBackgroundColor(EDITOR_SELECTION_BG_COLOR)
        self.setSelectionForegroundColor(EDITOR_SELECTION_FG_COLOR)
        
        # Set caret
        self.setCaretWidth(EDITOR_CARET_WIDTH)
        self.setCaretForegroundColor(EDITOR_CARET_COLOR)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(EDITOR_CARET_LINE_COLOR)

        # Set lexer
        self.lexer = LexerCPP(self)
        self.setLexer(self.lexer)
        self.lexer.setDefaultPaper(EDITOR_BACKGROUND_COLOR)

        # Set margins
        self.setMarginsBackgroundColor(EDITOR_MARGIN_BACKGROUND_COLOR)
        self.setMarginWidth(0, "000")
        self.setMarginWidth(1, "00")

    def init_custom_behavior(self):
        self.keyPressEvent = self.custom_key_press_event

    def show_snippet_picker(self):
        self.snippet_handler.show_snippet_picker()

    def toggle_comment(self):

        has_selection = self.hasSelectedText()
        if has_selection:

            line_from, index_from, line_to, index_to = self.getSelection()
            
            if line_from > line_to:
                line_from, line_to = line_to, line_from
            
            all_commented = True
            for line in range(line_from, line_to + 1):
                text = self.text(line).strip()
                if text:
                    if not text.startswith('//'):
                        all_commented = False
                        break
            
            self.beginUndoAction()
            

            for line in range(line_from, line_to + 1):
                text = self.text(line)
                stripped = text.lstrip()
                
                if not stripped and not all_commented:
                    continue
                    
                leading_spaces = len(text) - len(stripped)
                spaces = text[:leading_spaces]
                
                if all_commented and stripped.startswith('//'):
                    new_text = spaces + stripped[2:].lstrip()
                elif stripped:

                    new_text = spaces + '// ' + stripped
                else:
                    new_text = text
                
                self.setSelection(line, 0, line, len(text))
                self.replaceSelectedText(new_text)
            
            self.setSelection(line_from, index_from, line_to, index_to)
            
            self.endUndoAction()
        else:
            line, _ = self.getCursorPosition()
            text = self.text(line)
            stripped = text.lstrip()
            
            if not stripped:
                return
                
            leading_spaces = len(text) - len(stripped)
            spaces = text[:leading_spaces]
            
            self.beginUndoAction()
            
            if stripped.startswith('//'):
                new_text = spaces + stripped[2:].lstrip()
            else:
                new_text = spaces + '// ' + stripped
            
            self.setSelection(line, 0, line, len(text))
            self.replaceSelectedText(new_text)
            
            self.setCursorPosition(line, len(new_text))
            
            self.endUndoAction()

    def show_find_dialog(self):
        if not self.find_dialog:
            self.find_dialog = FindReplaceDialog(self, self)
        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()

    def show_replace_dialog(self):
        if not self.replace_dialog:
            self.replace_dialog = FindReplaceDialog(self, self, replace=True)
        self.replace_dialog.show()
        self.replace_dialog.raise_()
        self.replace_dialog.activateWindow()

    def insert_line_below(self):

        line, _ = self.getCursorPosition()
        current_line = self.text(line)

        indent = len(current_line.expandtabs(self.tabWidth())) - len(current_line.expandtabs(self.tabWidth()).lstrip())
        indent_str = "\t" * (indent // self.tabWidth())
    
        self.setCursorPosition(line, len(current_line) - 1)
        self.insert("\n" + indent_str)
        self.setCursorPosition(line + 1, (indent // self.tabWidth()))

    def move_line_up(self):
        if self.hasSelectedText():
            # Get the selection range
            line_from, index_from, line_to, index_to = self.getSelection()
            if line_from > line_to:
                line_from, line_to = line_to, line_from
                
            if line_from > 0:  # Can't move up if at first line
                self.beginUndoAction()
                
                # Get the line above the selection
                line_above = self.text(line_from - 1)
                
                # Store all selected lines
                selected_lines = []
                for line in range(line_from, line_to + 1):
                    selected_lines.append(self.text(line))
                
                # Remove the selected lines and insert them one line above
                self.setSelection(line_from - 1, 0, line_to, len(self.text(line_to)))
                self.removeSelectedText()
                
                cursor_pos = self.positionFromLineIndex(line_from - 1, 0)
                self.insertAt(line_above + "\n", line_to - 1, 0)
                self.insertAt("".join(selected_lines), line_from - 1, 0)
                
                # Restore selection one line up
                self.setSelection(line_from - 1, index_from, line_to - 1, index_to)
                
                self.endUndoAction()
        else:
            line, index = self.getCursorPosition()
            if line > 0:  # Can't move up if at first line
                self.beginUndoAction()
                
                # Get current line and the line above
                current_line = self.text(line)
                line_above = self.text(line - 1)
                
                # Swap the lines
                self.setSelection(line - 1, 0, line, len(current_line))
                self.removeSelectedText()
                self.insertAt(current_line + line_above, line - 1, 0)
                
                # Move cursor up
                self.setCursorPosition(line - 1, index)
                
                self.endUndoAction()

    def move_line_down(self):
        if self.hasSelectedText():
            # Get the selection range
            line_from, index_from, line_to, index_to = self.getSelection()
            if line_from > line_to:
                line_from, line_to = line_to, line_from
                
            if line_to < self.lines() - 1:  # Can't move down if at last line
                self.beginUndoAction()
                
                # Get the line below the selection
                line_below = self.text(line_to + 1)
                
                # Store all selected lines
                selected_lines = []
                for line in range(line_from, line_to + 1):
                    selected_lines.append(self.text(line))
                
                # Remove the selected lines and insert them one line below
                self.setSelection(line_from, 0, line_to + 1, len(line_below))
                self.removeSelectedText()
                
                self.insertAt("".join(selected_lines), line_from, 0)
                self.insertAt(line_below + "\n", line_from, 0)
                
                # Restore selection one line down
                self.setSelection(line_from + 1, index_from, line_to + 1, index_to)
                
                self.endUndoAction()
        else:
            line, index = self.getCursorPosition()
            if line < self.lines() - 1:  # Can't move down if at last line
                self.beginUndoAction()
                
                # Get current line and the line below
                current_line = self.text(line)
                line_below = self.text(line + 1)
                
                # Swap the lines
                self.setSelection(line, 0, line + 1, len(line_below))
                self.removeSelectedText()
                self.insertAt(line_below + current_line, line, 0)
                
                # Move cursor down
                self.setCursorPosition(line + 1, index)
                
                self.endUndoAction()

    def custom_key_press_event(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Slash:
                self.toggle_comment()
                return
            elif event.key() == Qt.Key.Key_J: 
                self.show_snippet_picker()
                return
            elif event.key() == Qt.Key.Key_F:
                self.show_find_dialog()
                return
            elif event.key() == Qt.Key.Key_H: 
                self.show_replace_dialog()
                return
            elif event.key() == Qt.Key.Key_Return:
                self.insert_line_below()
                return
            elif event.key() == Qt.Key.Key_E:
                event.ignore()
                return
        elif event.modifiers() == Qt.KeyboardModifier.AltModifier:
            if event.key() == Qt.Key.Key_Up:
                self.move_line_up()
                return
            elif event.key() == Qt.Key.Key_Down:
                self.move_line_down()
                return
                
        if event.key() == Qt.Key.Key_Backspace:
            line, index = self.getCursorPosition()
            text = self.text(line)
            if index > 0 and index < len(text):
                pairs = {
                    "(": ")",
                    "[": "]",
                    "{": "}",
                    '"': '"',
                    "'": "'"
                }
                # Check if character before cursor is an opening character
                char_before = text[index - 1]
                if char_before in pairs:
                    # Check if character at cursor is the matching closing character
                    if index < len(text) and text[index] == pairs[char_before]:
                        # Delete both characters
                        self.beginUndoAction()
                        self.setSelection(line, index - 1, line, index + 1)
                        self.removeSelectedText()
                        self.endUndoAction()
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
                current_line[index-1] == "{"):
                if (current_line[index] == "}"):
                    indent = len(current_line.expandtabs(self.tabWidth())) - len(current_line.expandtabs(self.tabWidth()).lstrip())
                    indent_str = "\t" * (indent // self.tabWidth())
                    
                    total_position = self.positionFromLineIndex(line, index)
                    self.SendScintilla(self.SCI_DELETERANGE, total_position, 1)
                    fixup = "\n" + indent_str + "\t" + "\n" + (indent // self.tabWidth()) * "\t" + "}"
                    self.insert(fixup)
                    self.setCursorPosition(line + 1, self.lineLength(line + 1) - 1)
                else:
                    indent = len(current_line.expandtabs(self.tabWidth())) - len(current_line.expandtabs(self.tabWidth()).lstrip())
                    QsciScintilla.keyPressEvent(self, event)
                    self.insert("\t" * ((indent // self.tabWidth()) + 1))
                    self.setCursorPosition(line + 1, ((indent // self.tabWidth()) + 1))
            else:
                indent = len(current_line.expandtabs(self.tabWidth())) - len(current_line.expandtabs(self.tabWidth()).lstrip())
                QsciScintilla.keyPressEvent(self, event)
                self.insert("\t" * (indent // self.tabWidth()))
                self.setCursorPosition(line + 1, (indent // self.tabWidth()))
            
        elif event.key() == Qt.Key.Key_Tab:
            line, index = self.getCursorPosition()
            self.insert("\t")
            self.setCursorPosition(line, index + 1)
            
        else:
            QsciScintilla.keyPressEvent(self, event)

    def refresh_settings(self):
        """Refresh all editor settings from global properties"""
        # Update font
        self.setFont(EDITOR_FONT)
        
        # Update indentation
        self.setTabWidth(EDITOR_TAB_WIDTH)
        self.setIndentationsUseTabs(EDITOR_USE_TABS)
        
        # Update colors
        self.setColor(EDITOR_TEXT_COLOR)
        self.setPaper(EDITOR_BACKGROUND_COLOR)
        self.setSelectionBackgroundColor(EDITOR_SELECTION_BG_COLOR)
        self.setSelectionForegroundColor(EDITOR_SELECTION_FG_COLOR)
        self.setCaretForegroundColor(EDITOR_CARET_COLOR)
        self.setCaretLineBackgroundColor(EDITOR_CARET_LINE_COLOR)
        self.setMarginsBackgroundColor(EDITOR_MARGIN_BACKGROUND_COLOR)
        self.setMatchedBraceBackgroundColor(EDITOR_BRACE_MATCHED_BG_COLOR)
        self.setMatchedBraceForegroundColor(EDITOR_BRACE_MATCHED_FG_COLOR)
        self.setUnmatchedBraceBackgroundColor(EDITOR_BRACE_UNMATCHED_BG_COLOR)
        self.setUnmatchedBraceForegroundColor(EDITOR_BRACE_UNMATCHED_FG_COLOR)
        
        # Update lexer colors
        if self.lexer:
            self.lexer.init_colors()
            self.lexer.setDefaultPaper(EDITOR_BACKGROUND_COLOR)
            self.lexer.setDefaultColor(EDITOR_TEXT_COLOR)
            self.lexer.setDefaultFont(EDITOR_FONT)
            for i in range(len(self.lexer.styles)):
                self.lexer.setFont(EDITOR_FONT, i)