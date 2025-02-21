from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QDockWidget, 
                             QStackedWidget, QMessageBox, QTabWidget, QSplitter)
from PyQt6.QtCore import Qt, QEvent
from .menubar import MenuBar
from .file_browser import FileBrowser
from editor.code_editor import CodeEditor
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("CP Code Editor")
        self.setGeometry(100, 100, 1200, 800)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Create file browser as a dock widget
        self.file_browser_dock = QDockWidget("File Browser", self)
        self.file_browser = FileBrowser()
        self.file_browser_dock.setWidget(self.file_browser)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_browser_dock)

        # Create tab widget for main editors
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.main_splitter.addWidget(self.tab_widget)

        # Create right side widget with input/output editors
        self.io_widget = QWidget()
        self.io_layout = QVBoxLayout(self.io_widget)
        self.io_layout.setContentsMargins(0, 30, 0, 0)  # Add top margin to prevent overlap with tabs
        
        # Create input editor
        self.input_editor = CodeEditor()
        self.input_editor.setWindowTitle("input.txt")
        self.io_layout.addWidget(self.input_editor)

        # Create output editor
        self.output_editor = CodeEditor()
        self.output_editor.setWindowTitle("output.txt")
        self.io_layout.addWidget(self.output_editor)

        # Add io_widget to main splitter
        self.main_splitter.addWidget(self.io_widget)
        
        # Set initial sizes (2:1 ratio)
        self.main_splitter.setSizes([2 * self.width() // 3, self.width() // 3])
        
        # Hide IO widget by default
        self.io_widget.hide()

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.file_browser.fileSelected.connect(self.open_file)
        
        # Install event filter for keyboard shortcuts
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            # Escape key to focus on editor
            if event.key() == Qt.Key.Key_Escape:
                if self.tab_widget.count() > 0:
                    current_editor = self.tab_widget.currentWidget()
                    if current_editor:
                        current_editor.setFocus()
                return True
        return super().eventFilter(obj, event)

    def toggle_io_view(self):
        if self.io_widget.isVisible():
            self.io_widget.hide()
        else:
            self.io_widget.show()
            # Create vertical splitter for input/output if not exists
            if not hasattr(self, 'io_splitter'):
                self.io_splitter = QSplitter(Qt.Orientation.Vertical)
                self.io_splitter.addWidget(self.input_editor)
                self.io_splitter.addWidget(self.output_editor)
                self.io_layout.addWidget(self.io_splitter)
            # Load input.txt and output.txt if they exist
            self.load_io_files()

    def load_io_files(self):
        try:
            # Load input.txt
            if os.path.exists("input.txt"):
                with open("input.txt", 'r') as f:
                    self.input_editor.setText(f.read())
            
            # Load output.txt
            if os.path.exists("output.txt"):
                with open("output.txt", 'r') as f:
                    self.output_editor.setText(f.read())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load I/O files: {str(e)}")

    def save_io_files(self):
        try:
            # Save input.txt
            with open("input.txt", 'w') as f:
                f.write(self.input_editor.text())
            
            # Save output.txt
            with open("output.txt", 'w') as f:
                f.write(self.output_editor.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save I/O files: {str(e)}")

    def open_file(self, file_path):
        try:
            # Check if file is already open
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabToolTip(i) == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    return

            # Create new editor for the file
            with open(file_path, 'r') as file:
                new_editor = CodeEditor()
                new_editor.setText(file.read())
                tab_name = os.path.basename(file_path)
                self.tab_widget.addTab(new_editor, tab_name)
                self.tab_widget.setTabToolTip(self.tab_widget.count() - 1, file_path)
                self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
                new_editor.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def close_tab(self, index):
        self.tab_widget.removeTab(index)

    def get_current_editor(self):
        return self.tab_widget.currentWidget() if self.tab_widget.count() > 0 else None

    def get_current_file(self):
        if self.tab_widget.count() > 0:
            return self.tab_widget.tabToolTip(self.tab_widget.currentIndex())
        return None

    def toggle_file_browser(self):
        if self.file_browser_dock.isVisible():
            self.file_browser_dock.hide()
        else:
            self.file_browser_dock.show()

    def closeEvent(self, event):
        # Save IO files before closing
        if self.io_widget.isVisible():
            self.save_io_files()
        super().closeEvent(event)