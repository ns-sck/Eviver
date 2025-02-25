from PyQt6.QtWidgets import QTabWidget, QMessageBox
from editor.code_editor import CodeEditor
import os

class TabManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.setup_tab_widget()
        
    def setup_tab_widget(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

    def open_file(self, file_path):
        try:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabToolTip(i) == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    return True

            with open(file_path, 'r') as file:
                new_editor = CodeEditor()
                new_editor.setText(file.read())
                tab_name = os.path.basename(file_path)
                self.tab_widget.addTab(new_editor, tab_name)
                self.tab_widget.setTabToolTip(self.tab_widget.count() - 1, file_path)
                self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
                new_editor.setFocus()
                return True
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Could not open file: {str(e)}")
            return False

    def close_tab(self, index):
        self.tab_widget.removeTab(index)

    def get_current_editor(self):
        return self.tab_widget.currentWidget() if self.tab_widget.count() > 0 else None

    def get_current_file(self):
        if self.tab_widget.count() > 0:
            return self.tab_widget.tabToolTip(self.tab_widget.currentIndex())
        return None

    def get_widget(self):
        return self.tab_widget

    def count(self):
        return self.tab_widget.count() 