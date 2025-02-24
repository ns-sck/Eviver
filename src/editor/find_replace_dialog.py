from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox

class FindReplaceDialog(QDialog):
    def __init__(self, editor, parent=None, replace=False):
        super().__init__(parent)
        self.editor = editor
        self.replace = replace
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Find section
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Replace section (if replace dialog)
        if self.replace:
            replace_layout = QHBoxLayout()
            replace_layout.addWidget(QLabel("Replace with:"))
            self.replace_input = QLineEdit()
            replace_layout.addWidget(self.replace_input)
            layout.addLayout(replace_layout)
        
        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("Case sensitive")
        self.whole_words = QCheckBox("Whole words")
        self.regex = QCheckBox("Regular expression")
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.whole_words)
        options_layout.addWidget(self.regex)
        layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        find_next_btn = QPushButton("Find Next")
        find_next_btn.clicked.connect(self.find_next)
        button_layout.addWidget(find_next_btn)
        
        if self.replace:
            replace_btn = QPushButton("Replace")
            replace_btn.clicked.connect(self.replace_current)
            replace_all_btn = QPushButton("Replace All")
            replace_all_btn.clicked.connect(self.replace_all)
            button_layout.addWidget(replace_btn)
            button_layout.addWidget(replace_all_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def find_next(self):
        text = self.find_input.text()
        self.editor.findFirst(text, self.regex.isChecked(), self.case_sensitive.isChecked(),
                            self.whole_words.isChecked(), True)
    
    def replace_current(self):
        if not self.replace:
            return
        if self.editor.hasSelectedText():
            self.editor.replace(self.replace_input.text())
            self.find_next()
    
    def replace_all(self):
        if not self.replace:
            return
        text = self.find_input.text()
        replacement = self.replace_input.text()

        self.editor.setCursorPosition(0, 0)
        
        count = 0
        self.editor.beginUndoAction()
        while self.editor.findFirst(text, self.regex.isChecked(), self.case_sensitive.isChecked(),
                                  self.whole_words.isChecked(), True):
            self.editor.replace(replacement)
            count += 1
        self.editor.endUndoAction() 