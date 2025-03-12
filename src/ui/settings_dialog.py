from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QWidget, QLabel, QSpinBox, QComboBox, QPushButton,
                             QColorDialog, QFontComboBox, QCheckBox, QScrollArea, QMessageBox,
                             QLineEdit, QGroupBox, QFormLayout, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeySequence
from editor.custom_lexer import LexerCPP
from utils.properties import *
import json
import os

DEFAULT_SETTINGS = {
    "WINDOW_TITLE": "Eviver Code Editor",
    "WINDOW_INITIAL_GEOMETRY": (100, 100, 1200, 800),
    "EDITOR_FONT_FAMILY": "Consolas",
    "EDITOR_FONT_SIZE": 10,
    "EDITOR_TAB_WIDTH": 2,
    "EDITOR_USE_TABS": False,
    "EDITOR_TEXT_COLOR": "#FFFFFF",
    "EDITOR_BACKGROUND_COLOR": "#2B2B2B",
    "EDITOR_CARET_COLOR": "#FFFFFF",
    "EDITOR_CARET_LINE_COLOR": "#2A2A2A",
    "EDITOR_MARGIN_BACKGROUND_COLOR": "#111111",
    "EDITOR_SELECTION_BG_COLOR": "#214283",
    "EDITOR_SELECTION_FG_COLOR": "#FFFFFF",
    "EDITOR_BRACE_MATCHED_BG_COLOR": "#404040",
    "EDITOR_BRACE_MATCHED_FG_COLOR": "#00FF00",
    "EDITOR_BRACE_UNMATCHED_BG_COLOR": "#802020",
    "EDITOR_BRACE_UNMATCHED_FG_COLOR": "#FF0000",
    "SYNTAX_DEFAULT": "#d7d7d7",
    "SYNTAX_COMMENT": "#FFFF7F",
    "SYNTAX_DOUBLE_SLASH_COMMENT": "#37743f",
    "SYNTAX_KEYWORD": "#50B0FF",
    "SYNTAX_STRING": "#FFFF7F",
    "SYNTAX_NUMBER": "#EDFFAF",
    "SYNTAX_PREPROCESSOR": "#C586C0",
    "SYNTAX_OPERATOR": "#FFFF7F",
    "SYNTAX_IDENTIFIER": "#FFFF7F",
    "SYNTAX_TYPE": "#50B0FF",
    "SYNTAX_SYMBOL": "#CC0099",
    "SYNTAX_PARANTHESES": "#50B0FF",
    "SYNTAX_BACKGROUND": "#111111",
    "IO_WIDGET_TOP_MARGIN": 30,
    "EDITOR_CARET_WIDTH": 2,
    "TERMINAL_WIDTH": 80,
    "TERMINAL_HEIGHT": 32,
    # Additional settings that were previously only in properties.py
    "COMPILE_RELEASE_CMD": 'g++ -DLOCAL -std=c++17 -Wshadow -Wall -o "{executable}" "{source}" -O2 -Wno-unused-result',
    "COMPILE_DEBUG_CMD": 'g++ -DLOCAL -std=c++17 -Wshadow -Wall -o "{executable}" "{source}" -g -D_GLIBCXX_DEBUG',
    "SHORTCUT_NEW_FILE": "Ctrl+N",
    "SHORTCUT_OPEN_FILE": "Ctrl+O",
    "SHORTCUT_SAVE_FILE": "Ctrl+S",
    "SHORTCUT_SAVE_AS": "Ctrl+Shift+S",
    "SHORTCUT_CLOSE_TAB": "Ctrl+W",
    "SHORTCUT_EXIT": "Ctrl+Q",
    "SHORTCUT_TOGGLE_FILE_BROWSER": "Ctrl+B",
    "SHORTCUT_TOGGLE_IO": "Ctrl+I",
    "SHORTCUT_TOGGLE_TERMINAL": "Ctrl+`",
    "SHORTCUT_SNIPPET_PICKER": "Ctrl+J",
    "SHORTCUT_COMPILE_RUN": "Ctrl+Alt+N",
    "SHORTCUT_COMPILE_DEBUG": "F9",
    "SHORTCUT_CYCLE_EDITORS": "F3",
    "DEFAULT_WORKSPACE_DIR": os.path.expanduser("~/Desktop/algo"),
}

class ColorButton(QPushButton):
    def __init__(self, color, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.setColor(color)
        self.clicked.connect(self.pickColor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
    def setColor(self, color):
        if isinstance(color, str):
            color = QColor(color)
        self.color = color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: 2px solid #555555;
                border-radius: 5px;
                min-width: 60px;
                min-height: 25px;
            }}
            QPushButton:hover {{
                border: 2px solid #777777;
            }}
        """)
        if self.callback:
            self.callback(self.color)
        
    def pickColor(self):
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.setColor(color)
            
    def getColor(self):
        return self.color.name()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.resize(800, 600)
        self.settings = self.load_settings()
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        tab_widget = QTabWidget()
        
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)
        editor_scroll = QScrollArea()
        editor_scroll.setWidgetResizable(True)
        editor_scroll_content = QWidget()
        editor_scroll_layout = QVBoxLayout(editor_scroll_content)
        
        font_group = QWidget()
        font_layout = QHBoxLayout(font_group)
        font_layout.addWidget(QLabel("Font:"))
        self.font_family = QFontComboBox()
        font_layout.addWidget(self.font_family)
        font_layout.addWidget(QLabel("Size:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        font_layout.addWidget(self.font_size)
        font_layout.addStretch()
        editor_scroll_layout.addWidget(font_group)
        
        tab_group = QWidget()
        tab_layout = QHBoxLayout(tab_group)
        tab_layout.addWidget(QLabel("Tab Width:"))
        self.tab_width = QSpinBox()
        self.tab_width.setRange(1, 8)
        tab_layout.addWidget(self.tab_width)
        self.use_tabs = QCheckBox("Use Tabs")
        tab_layout.addWidget(self.use_tabs)
        
        # Add a label to show the current indentation preview
        tab_layout.addWidget(QLabel("Preview:"))
        self.indentation_preview = QLabel()
        self.indentation_preview.setStyleSheet("background-color: #333; padding: 2px 5px; border-radius: 3px;")
        tab_layout.addWidget(self.indentation_preview)
        
        # Connect signals to update the preview
        self.tab_width.valueChanged.connect(self.update_indentation_preview)
        self.use_tabs.stateChanged.connect(self.update_indentation_preview)
        
        tab_layout.addStretch()
        editor_scroll_layout.addWidget(tab_group)
        
        editor_scroll_layout.addWidget(QLabel("Editor Colors:"))
        self.color_buttons = {}
        
        color_settings = [
            ("Text Color", "EDITOR_TEXT_COLOR"),
            ("Background Color", "EDITOR_BACKGROUND_COLOR"),
            ("Caret Color", "EDITOR_CARET_COLOR"),
            ("Caret Line Color", "EDITOR_CARET_LINE_COLOR"),
            ("Selection Background", "EDITOR_SELECTION_BG_COLOR"),
            ("Selection Text", "EDITOR_SELECTION_FG_COLOR"),
            ("Margin Background", "EDITOR_MARGIN_BACKGROUND_COLOR"),
            ("Matched Brace Background", "EDITOR_BRACE_MATCHED_BG_COLOR"),
            ("Matched Brace Text", "EDITOR_BRACE_MATCHED_FG_COLOR"),
            ("Unmatched Brace Background", "EDITOR_BRACE_UNMATCHED_BG_COLOR"),
            ("Unmatched Brace Text", "EDITOR_BRACE_UNMATCHED_FG_COLOR"),
        ]
        
        for label, setting in color_settings:
            color_group = QWidget()
            color_layout = QHBoxLayout(color_group)
            color_layout.addWidget(QLabel(label + ":"))
            
            # Create color button with current setting value
            callback = lambda color, s=setting: self.update_editor_color(s, color)
            color_button = ColorButton(self.settings.get(setting, DEFAULT_SETTINGS[setting]), callback=callback)
            self.color_buttons[setting] = color_button
            color_layout.addWidget(color_button)
            
            # Add hex input field
            hex_input = QLineEdit()
            hex_input.setFixedWidth(80)
            hex_input.setText(self.settings.get(setting, DEFAULT_SETTINGS[setting]).upper())
            hex_input.setPlaceholderText("#RRGGBB")
            hex_input.textChanged.connect(lambda text, b=color_button: self.update_color_from_text(text, b))
            color_layout.addWidget(hex_input)
            
            color_layout.addStretch()
            editor_scroll_layout.addWidget(color_group)
            
        editor_scroll_layout.addWidget(QLabel("Syntax Highlighting:"))
        
        syntax_settings = [
            ("Default Text", "SYNTAX_DEFAULT"),
            ("Comments", "SYNTAX_COMMENT"),
            ("// Comments", "SYNTAX_DOUBLE_SLASH_COMMENT"),
            ("Keywords", "SYNTAX_KEYWORD"),
            ("Strings", "SYNTAX_STRING"),
            ("Numbers", "SYNTAX_NUMBER"),
            ("Preprocessor", "SYNTAX_PREPROCESSOR"),
            ("Operators", "SYNTAX_OPERATOR"),
            ("Identifiers", "SYNTAX_IDENTIFIER"),
            ("Types", "SYNTAX_TYPE"),
            ("Symbols", "SYNTAX_SYMBOL"),
            ("Parentheses", "SYNTAX_PARANTHESES"),
        ]
        
        for label, setting in syntax_settings:
            syntax_group = QWidget()
            syntax_layout = QHBoxLayout(syntax_group)
            syntax_layout.addWidget(QLabel(label + ":"))
            
            # Create color button with current setting value
            callback = lambda color, s=setting: self.update_editor_color(s, color)
            color_button = ColorButton(self.settings.get(setting, DEFAULT_SETTINGS[setting]), callback=callback)
            self.color_buttons[setting] = color_button
            syntax_layout.addWidget(color_button)
            
            # Add hex input field
            hex_input = QLineEdit()
            hex_input.setFixedWidth(80)
            hex_input.setText(self.settings.get(setting, DEFAULT_SETTINGS[setting]).upper())
            hex_input.setPlaceholderText("#RRGGBB")
            hex_input.textChanged.connect(lambda text, b=color_button: self.update_color_from_text(text, b))
            syntax_layout.addWidget(hex_input)
            
            syntax_layout.addStretch()
            editor_scroll_layout.addWidget(syntax_group)
            
        editor_scroll_layout.addStretch()
        editor_scroll.setWidget(editor_scroll_content)
        editor_layout.addWidget(editor_scroll)
        
        tab_widget.addTab(editor_tab, "Editor")
        
        # Add Compilation tab
        compilation_tab = QWidget()
        compilation_layout = QVBoxLayout(compilation_tab)
        compilation_scroll = QScrollArea()
        compilation_scroll.setWidgetResizable(True)
        compilation_scroll_content = QWidget()
        compilation_scroll_layout = QVBoxLayout(compilation_scroll_content)
        
        # Compilation commands
        compile_group = QGroupBox("Compilation Commands")
        compile_form = QFormLayout(compile_group)
        
        self.compile_release_cmd = QLineEdit()
        compile_form.addRow("Release Build:", self.compile_release_cmd)
        
        self.compile_debug_cmd = QLineEdit()
        compile_form.addRow("Debug Build:", self.compile_debug_cmd)
        
        compilation_scroll_layout.addWidget(compile_group)
        
        # Default workspace directory
        workspace_group = QGroupBox("Workspace")
        workspace_layout = QHBoxLayout(workspace_group)
        workspace_layout.addWidget(QLabel("Default Workspace Directory:"))
        self.default_workspace_dir = QLineEdit()
        workspace_layout.addWidget(self.default_workspace_dir)
        
        compilation_scroll_layout.addWidget(workspace_group)
        compilation_scroll_layout.addStretch()
        
        compilation_scroll.setWidget(compilation_scroll_content)
        compilation_layout.addWidget(compilation_scroll)
        
        tab_widget.addTab(compilation_tab, "Compilation")
        
        # Add Shortcuts tab
        shortcuts_tab = QWidget()
        shortcuts_layout = QVBoxLayout(shortcuts_tab)
        shortcuts_scroll = QScrollArea()
        shortcuts_scroll.setWidgetResizable(True)
        shortcuts_scroll_content = QWidget()
        shortcuts_scroll_layout = QFormLayout(shortcuts_scroll_content)
        
        # Create shortcut input fields
        self.shortcut_fields = {}
        shortcut_settings = [
            ("New File", "SHORTCUT_NEW_FILE"),
            ("Open File", "SHORTCUT_OPEN_FILE"),
            ("Save File", "SHORTCUT_SAVE_FILE"),
            ("Save As", "SHORTCUT_SAVE_AS"),
            ("Close Tab", "SHORTCUT_CLOSE_TAB"),
            ("Exit", "SHORTCUT_EXIT"),
            ("Toggle File Browser", "SHORTCUT_TOGGLE_FILE_BROWSER"),
            ("Toggle IO Panel", "SHORTCUT_TOGGLE_IO"),
            ("Toggle Terminal", "SHORTCUT_TOGGLE_TERMINAL"),
            ("Snippet Picker", "SHORTCUT_SNIPPET_PICKER"),
            ("Compile & Run", "SHORTCUT_COMPILE_RUN"),
            ("Compile Debug", "SHORTCUT_COMPILE_DEBUG"),
            ("Cycle Editors", "SHORTCUT_CYCLE_EDITORS"),
        ]
        
        for label, setting in shortcut_settings:
            shortcut_field = QLineEdit()
            shortcuts_scroll_layout.addRow(f"{label}:", shortcut_field)
            self.shortcut_fields[setting] = shortcut_field
        
        shortcuts_scroll_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        shortcuts_scroll.setWidget(shortcuts_scroll_content)
        shortcuts_layout.addWidget(shortcuts_scroll)
        
        tab_widget.addTab(shortcuts_tab, "Shortcuts")
        
        layout.addWidget(tab_widget)
        
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def update_indentation_preview(self):
        use_tabs = self.use_tabs.isChecked()
        tab_width = self.tab_width.value()
        
        if use_tabs:
            preview_text = "→" * 1  # Unicode character for tab
        else:
            preview_text = "·" * tab_width  # Unicode character for space
            
        self.indentation_preview.setText(preview_text)
        
    def load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
        
    def load_current_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                current_settings = json.load(f)
        except:
            current_settings = DEFAULT_SETTINGS.copy()
        
        self.font_family.setCurrentText(current_settings.get("EDITOR_FONT_FAMILY", DEFAULT_SETTINGS["EDITOR_FONT_FAMILY"]))
        self.font_size.setValue(current_settings.get("EDITOR_FONT_SIZE", DEFAULT_SETTINGS["EDITOR_FONT_SIZE"]))
        
        self.tab_width.setValue(current_settings.get("EDITOR_TAB_WIDTH", DEFAULT_SETTINGS["EDITOR_TAB_WIDTH"]))
        self.use_tabs.setChecked(current_settings.get("EDITOR_USE_TABS", DEFAULT_SETTINGS["EDITOR_USE_TABS"]))
        
        # Update the indentation preview
        self.update_indentation_preview()
        
        # Update color buttons with current settings
        for setting, button in self.color_buttons.items():
            color = current_settings.get(setting, DEFAULT_SETTINGS[setting])
            button.setColor(color)
            # Update the hex input field next to the button
            button.parent().layout().itemAt(2).widget().setText(color.upper())
        
        # Set compilation settings
        self.compile_release_cmd.setText(current_settings.get("COMPILE_RELEASE_CMD", DEFAULT_SETTINGS["COMPILE_RELEASE_CMD"]))
        self.compile_debug_cmd.setText(current_settings.get("COMPILE_DEBUG_CMD", DEFAULT_SETTINGS["COMPILE_DEBUG_CMD"]))
        self.default_workspace_dir.setText(current_settings.get("DEFAULT_WORKSPACE_DIR", DEFAULT_SETTINGS["DEFAULT_WORKSPACE_DIR"]))
        
        # Set shortcut settings
        for setting, field in self.shortcut_fields.items():
            field.setText(current_settings.get(setting, DEFAULT_SETTINGS[setting]))
                
        self.settings = current_settings
        
    def save_settings(self):
        settings = DEFAULT_SETTINGS.copy()
        
        settings.update({
            "EDITOR_FONT_FAMILY": self.font_family.currentText(),
            "EDITOR_FONT_SIZE": self.font_size.value(),
            "EDITOR_TAB_WIDTH": self.tab_width.value(),
            "EDITOR_USE_TABS": self.use_tabs.isChecked(),
        })
        
        for setting, button in self.color_buttons.items():
            settings[setting] = button.getColor()
            
        # Save compilation settings
        settings["COMPILE_RELEASE_CMD"] = self.compile_release_cmd.text()
        settings["COMPILE_DEBUG_CMD"] = self.compile_debug_cmd.text()
        settings["DEFAULT_WORKSPACE_DIR"] = self.default_workspace_dir.text()
        
        # Save shortcut settings
        for setting, field in self.shortcut_fields.items():
            settings[setting] = field.text()
            
        try:
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
            
            load_settings_from_json()
            
            editors = []
            tab_widget = self.parent.parent().tab_manager.get_widget()
            for i in range(tab_widget.count()):
                editor = tab_widget.widget(i)
                if editor:
                    editors.append(editor)
            
            if self.parent.parent().io_manager:
                editors.extend([
                    self.parent.parent().io_manager.input_editor,
                    self.parent.parent().io_manager.output_editor
                ])
            
            for editor in editors:
                if editor:
                    editor.refresh_settings()
            
            self.accept()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings: {str(e)}")
            return False
            
    def update_editor_color(self, setting, color):
        editors = []
        tab_widget = self.parent.parent().tab_manager.get_widget()
        for i in range(tab_widget.count()):
            editor = tab_widget.widget(i)
            if editor:
                editors.append(editor)
        
        if self.parent.parent().io_manager:
            editors.extend([
                self.parent.parent().io_manager.input_editor,
                self.parent.parent().io_manager.output_editor
            ])

        if not hasattr(self, 'settings'):
            self.settings = DEFAULT_SETTINGS.copy()

        self.settings[setting] = color.name()

        try:
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
                
            load_settings_from_json()
            
            for editor in editors:
                if not editor:
                    continue
                editor.refresh_settings()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings: {str(e)}")
            return 

    def update_color_from_text(self, text, color_button):
        """Update color button when hex input changes"""
        if text.startswith('#') and len(text) == 7:
            try:
                color = QColor(text)
                if color.isValid():
                    color_button.setColor(color)
            except:
                pass 