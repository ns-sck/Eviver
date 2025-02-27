from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QWidget, QLabel, QSpinBox, QComboBox, QPushButton,
                             QColorDialog, QFontComboBox, QCheckBox, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from editor.custom_lexer import LexerCPP
from utils.properties import *
import json
import os

DEFAULT_SETTINGS = {
    "WINDOW_TITLE": "CP Code Editor",
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
}

class ColorButton(QPushButton):
    def __init__(self, color, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.setColor(color)
        self.clicked.connect(self.pickColor)
        
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
            callback = lambda color, s=setting: self.update_editor_color(s, color)
            color_button = ColorButton(DEFAULT_SETTINGS[setting], callback=callback)
            self.color_buttons[setting] = color_button
            color_layout.addWidget(color_button)
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
            callback = lambda color, s=setting: self.update_editor_color(s, color)
            color_button = ColorButton(DEFAULT_SETTINGS[setting], callback=callback)
            self.color_buttons[setting] = color_button
            syntax_layout.addWidget(color_button)
            syntax_layout.addStretch()
            editor_scroll_layout.addWidget(syntax_group)
            
        editor_scroll_layout.addStretch()
        editor_scroll.setWidget(editor_scroll_content)
        editor_layout.addWidget(editor_scroll)
        
        tab_widget.addTab(editor_tab, "Editor")
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
        
    def load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
        
    def load_current_settings(self):
        current_settings = {}
        
        for key in DEFAULT_SETTINGS:
            if key in globals():
                if isinstance(globals()[key], QColor):
                    current_settings[key] = globals()[key].name()
                else:
                    current_settings[key] = globals()[key]
        
        self.font_family.setCurrentText(current_settings.get("EDITOR_FONT_FAMILY"))
        self.font_size.setValue(current_settings.get("EDITOR_FONT_SIZE"))
        
        self.tab_width.setValue(current_settings.get("EDITOR_TAB_WIDTH"))
        self.use_tabs.setChecked(current_settings.get("EDITOR_USE_TABS"))
        
        for setting, button in self.color_buttons.items():
            if setting in current_settings:
                button.setColor(current_settings[setting])
            else:
                button.setColor(DEFAULT_SETTINGS[setting])
                
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