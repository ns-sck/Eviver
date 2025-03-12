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
        
        # Apply custom styling to the tab widget
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                background-color: #1E1E1E;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #2D2D2D;
                color: #CCCCCC;
                border: none;
                height: 24px;
                padding-left: 10px;
                padding-right: 25px; /* Make room for close button */
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3C3C3C;
                color: #FFFFFF;
            }
            QTabBar::tab:hover:!selected {
                background-color: #353535;
            }
            QTabBar::close-button {
                /* Use an explicit X character for better compatibility */
                background-color: transparent;
                color: #AAAAAA;
                border-radius: 2px;
                margin: 2px;
                subcontrol-origin: padding;
                subcontrol-position: right;
                width: 16px;
                height: 16px;
            }
            QTabBar::close-button:hover {
                background-color: #AA0000;
                color: white;
            }
            QTabBar::close-button:pressed {
                background-color: #E81123;
            }
        """)

    def open_file(self, file_path):
        try:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabToolTip(i) == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    return True

            with open(file_path, 'r') as file:
                new_editor = CodeEditor()
                new_editor.setText(file.read())
                new_editor.set_file_path(file_path)  # Set the file path to apply appropriate lexer
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