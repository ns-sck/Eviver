from PyQt6.QtWidgets import QWidget
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtGui import QFont, QColor, QKeyEvent
from PyQt6.QtCore import Qt, QEvent
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
        self.file_path = None
        
        # Enable focus and keyboard tracking
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def init_editor(self):
        self.setFont(EDITOR_FONT)
        
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginsForegroundColor(Qt.GlobalColor.darkGray)

        self.setAutoIndent(False)
        self.setIndentationGuides(True)
        self.setTabWidth(EDITOR_TAB_WIDTH)
        self.setIndentationsUseTabs(EDITOR_USE_TABS)

        # self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)
        self.setMatchedBraceBackgroundColor(EDITOR_BRACE_MATCHED_BG_COLOR)
        self.setMatchedBraceForegroundColor(EDITOR_BRACE_MATCHED_FG_COLOR)
        self.setUnmatchedBraceBackgroundColor(EDITOR_BRACE_UNMATCHED_BG_COLOR)
        self.setUnmatchedBraceForegroundColor(EDITOR_BRACE_UNMATCHED_FG_COLOR)

        self.setColor(EDITOR_TEXT_COLOR)
        self.setPaper(EDITOR_BACKGROUND_COLOR)
        self.setIndentationGuides(False)
        self.setSelectionBackgroundColor(EDITOR_SELECTION_BG_COLOR)
        self.setSelectionForegroundColor(EDITOR_SELECTION_FG_COLOR)
        
        self.setCaretWidth(EDITOR_CARET_WIDTH)
        self.setCaretForegroundColor(EDITOR_CARET_COLOR)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(EDITOR_CARET_LINE_COLOR)

        self.SendScintilla(QsciScintilla.SCI_SETYCARETPOLICY, QsciScintilla.CARET_SLOP | QsciScintilla.CARET_STRICT | QsciScintilla.CARET_EVEN, 5)

        self.setMarginsBackgroundColor(EDITOR_MARGIN_BACKGROUND_COLOR)
        self.setMarginWidth(0, "000")
        self.setMarginWidth(1, "00")
        
        self.lexer = None

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
        indent_level = indent // self.tabWidth()
        
        if current_line.rstrip().endswith('{'):
            indent_level += 1
            
        indent_str = EDITOR_INDENTATION * indent_level
    
        self.setCursorPosition(line, len(current_line) - 1)
        self.insert("\n" + indent_str)
        self.setCursorPosition(line + 1, len(indent_str))

    def move_line_up(self):
        if self.hasSelectedText():
            # Get the selection range
            line_from, index_from, line_to, index_to = self.getSelection()
            if line_from > line_to:
                line_from, line_to = line_to, line_from
                
            if line_from > 0:  
                self.beginUndoAction()
                
                line_above = self.text(line_from - 1)
                
                selected_lines = []
                for line in range(line_from, line_to + 1):
                    selected_lines.append(self.text(line))
                
                self.setSelection(line_from - 1, 0, line_to, len(self.text(line_to)))
                self.removeSelectedText()
                
                cursor_pos = self.positionFromLineIndex(line_from - 1, 0)
                self.insertAt(line_above + "\n", line_to - 1, 0)
                self.insertAt("".join(selected_lines), line_from - 1, 0)
                
                self.setSelection(line_from - 1, index_from, line_to - 1, index_to)
                
                self.endUndoAction()
        else:
            line, index = self.getCursorPosition()
            if line > 0: 
                self.beginUndoAction()
                
                current_line = self.text(line)
                line_above = self.text(line - 1)
                
                self.setSelection(line - 1, 0, line, len(current_line))
                self.removeSelectedText()
                self.insertAt(current_line + line_above, line - 1, 0)
                
                self.setCursorPosition(line - 1, index)
                
                self.endUndoAction()

    def move_line_down(self):
        if self.hasSelectedText():
            line_from, index_from, line_to, index_to = self.getSelection()
            if line_from > line_to:
                line_from, line_to = line_to, line_from
                
            if line_to < self.lines() - 1:
                self.beginUndoAction()
                
                line_below = self.text(line_to + 1)
                
                selected_lines = []
                for line in range(line_from, line_to + 1):
                    selected_lines.append(self.text(line))
                
                self.setSelection(line_from, 0, line_to + 1, len(line_below))
                self.removeSelectedText()
                
                self.insertAt("".join(selected_lines), line_from, 0)
                self.insertAt(line_below + "\n", line_from, 0)
                
                self.setSelection(line_from + 1, index_from, line_to + 1, index_to)
                
                self.endUndoAction()
        else:
            line, index = self.getCursorPosition()
            if line < self.lines() - 1:  # Can't move down if at last line
                self.beginUndoAction()
                
                current_line = self.text(line)
                line_below = self.text(line + 1)
                
                self.setSelection(line, 0, line + 1, len(line_below))
                self.removeSelectedText()
                self.insertAt(line_below + current_line, line, 0)
                
                self.setCursorPosition(line + 1, index)
                
                self.endUndoAction()

    def decrease_indentation(self):
        """Decrease the indentation of the current line by one tab width"""
        line, index = self.getCursorPosition()
        current_line = self.text(line)
        
        if not current_line.strip():
            return
            
        stripped = current_line.lstrip()
        
        if current_line == stripped:
            return
            
        if EDITOR_USE_TABS:
            if current_line.startswith('\t'):
                new_text = current_line[1:]
                spaces_removed = 1
            else:
                leading_spaces = len(current_line) - len(stripped)
                tab_width = self.tabWidth()
                tabs_equivalent = leading_spaces // tab_width
                
                if tabs_equivalent > 0:
                    new_leading_spaces = '\t' * (tabs_equivalent - 1)
                    new_text = new_leading_spaces + stripped
                    spaces_removed = tab_width
                else:
                    new_text = stripped
                    spaces_removed = leading_spaces
        else:
            leading_spaces = len(current_line) - len(stripped)
            tab_width = self.tabWidth()
            spaces_to_remove = min(leading_spaces, tab_width)
            new_text = current_line[spaces_to_remove:]
            spaces_removed = spaces_to_remove
        
        self.beginUndoAction()
        self.setSelection(line, 0, line, len(current_line))
        self.replaceSelectedText(new_text)
        
        new_index = max(0, index - spaces_removed)
        self.setCursorPosition(line, new_index)
        
        self.endUndoAction()

    def delete_current_line(self):
        """Delete the current line and its newline character if not the last line."""
        line, _ = self.getCursorPosition()
        self.beginUndoAction()
        lineLength = len(self.text(line))
        self.setSelection(line, 0, line, lineLength)
        self.removeSelectedText()
        if line < self.lines() - 1:  # If not the last line
            self.removeSelectedText()  # Remove the newline
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
            elif event.key() == Qt.Key.Key_X:
                self.delete_current_line()
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
            elif event.key() == Qt.Key.Key_J:
                self.decrease_indentation()
                return
        
        if event.key() == Qt.Key.Key_Tab and not event.modifiers():
            line, index = self.getCursorPosition()
            current_line = self.text(line)
        
            if current_line.strip() == "":
                self.beginUndoAction()
                if index < len(current_line) - 1:
                    self.setSelection(line, 0, line, len(current_line) - 1)
                    self.removeSelectedText()
                    if EDITOR_USE_TABS:
                        self.insert('\t')
                    else:
                        self.insert(' ' * self.tabWidth())
                    if EDITOR_USE_TABS:
                        self.setCursorPosition(line, 1) 
                    else:
                        self.setCursorPosition(line, self.tabWidth())  # After one tab width of spaces
                else:
                    if EDITOR_USE_TABS:
                        self.insert('\t')
                    else:
                        self.insert(' ' * self.tabWidth())
                    
                    self.setCursorPosition(line, index + self.tabWidth())
                
                self.endUndoAction()
                return
            else:
                QsciScintilla.keyPressEvent(self, event)
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
                    "'": "'",
                }
                char_before = text[index - 1]
                if char_before in pairs:
                    if index < len(text) and text[index] == pairs[char_before]:
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
                "'": "'",
            }
            
            if self.hasSelectedText():
                line_from, index_from, line_to, index_to = self.getSelection()
                
                selected_text = self.selectedText()
                
                wrapped_text = event.text() + selected_text + pairs[event.text()]
                
                self.beginUndoAction()
                self.replaceSelectedText(wrapped_text)
                
                self.setSelection(line_from, index_from, line_to, index_to + 2)
                self.endUndoAction()
                return
            else:
                line, index = self.getCursorPosition()
                current_line = self.text(line)
                
                text_to_right = current_line[index:] if index < len(current_line) else ""
                has_text_to_right = text_to_right.strip() != ""
                
                self.insert(event.text())
                self.setCursorPosition(line, index + 1)
                
                if not has_text_to_right:
                    self.insert(pairs[event.text()])
                    self.setCursorPosition(line, index + 1)
                
                return
            
        elif event.key() == Qt.Key.Key_Return:
            line, index = self.getCursorPosition()
            current_line = self.text(line)

            if (index > 0 and index < len(current_line) and 
                current_line[index-1] == "{"):
                if (current_line[index] == "}"):
                    indent = len(current_line.expandtabs(self.tabWidth())) - len(current_line.expandtabs(self.tabWidth()).lstrip())
                    indent_level = indent // self.tabWidth()
                    indent_str = EDITOR_INDENTATION * indent_level
                    
                    total_position = self.positionFromLineIndex(line, index)
                    self.SendScintilla(self.SCI_DELETERANGE, total_position, 1)
                    fixup = "\n" + indent_str + EDITOR_INDENTATION + "\n" + indent_str + "}"
                    self.insert(fixup)
                    self.setCursorPosition(line + 1, len(indent_str) + len(EDITOR_INDENTATION))
                else:
                    indent = len(current_line.expandtabs(self.tabWidth())) - len(current_line.expandtabs(self.tabWidth()).lstrip())
                    indent_level = indent // self.tabWidth()
                    QsciScintilla.keyPressEvent(self, event)
                    self.insert(EDITOR_INDENTATION * (indent_level + 1))
                    self.setCursorPosition(line + 1, len(EDITOR_INDENTATION) * (indent_level + 1))
            else:
                indent = len(current_line.expandtabs(self.tabWidth())) - len(current_line.expandtabs(self.tabWidth()).lstrip())
                indent_level = indent // self.tabWidth()
                QsciScintilla.keyPressEvent(self, event)
                self.insert(EDITOR_INDENTATION * indent_level)
                self.setCursorPosition(line + 1, len(EDITOR_INDENTATION) * indent_level)       
        else:
            QsciScintilla.keyPressEvent(self, event)

    def refresh_settings(self):
        """Refresh all editor settings from global properties"""
        self.setFont(EDITOR_FONT)
        
        self.setTabWidth(EDITOR_TAB_WIDTH)
        self.setIndentationsUseTabs(EDITOR_USE_TABS)
        
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
        
        if self.lexer:
            self.lexer.init_colors()
            self.lexer.setDefaultPaper(EDITOR_BACKGROUND_COLOR)
            self.lexer.setDefaultColor(EDITOR_TEXT_COLOR)
            self.lexer.setDefaultFont(EDITOR_FONT)
            for i in range(len(self.lexer.styles)):
                self.lexer.setFont(EDITOR_FONT, i)

    def set_file_path(self, file_path):
        """Set the file path and apply appropriate lexer based on file extension"""
        self.file_path = file_path
        
        if self.lexer:
            self.setLexer(None)
            self.lexer = None
        
        if file_path and file_path.lower().endswith('.cpp'):
            self.lexer = LexerCPP(self)
            self.setLexer(self.lexer)
            self.lexer.setDefaultPaper(EDITOR_BACKGROUND_COLOR)
            if hasattr(self.lexer, 'init_colors'):
                self.lexer.init_colors()