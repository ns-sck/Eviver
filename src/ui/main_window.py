from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QDockWidget, 
                             QStackedWidget, QMessageBox, QTabWidget, QSplitter)
from PyQt6.QtCore import Qt, QEvent, QProcess, QTimer
from PyQt6.QtGui import QFont
from .menubar import MenuBar
from .io_manager import IOManager
from .tab_manager import TabManager
from .terminal_handler import TerminalHandler
from .compiler_manager import CompilerManager
from .file_browser_manager import FileBrowserManager
from utils.properties import *
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_filesystem()
        self.init_managers()
        self.init_ui()

    def init_filesystem(self):
        os.makedirs(IO_DIR, exist_ok=True)
        os.makedirs(BIN_DIR, exist_ok=True)
        if not os.path.exists(INPUT_PATH):
            with open(INPUT_PATH, 'w') as f:
                f.write("")
        if not os.path.exists(OUTPUT_PATH):
            with open(OUTPUT_PATH, 'w') as f:
                f.write("")

    def init_managers(self):
        self.io_manager = IOManager(self)
        self.tab_manager = TabManager(self)
        self.terminal_handler = TerminalHandler(self)
        self.compiler_manager = CompilerManager(self)
        self.file_browser_manager = FileBrowserManager(self)
        
        self.file_browser_manager.connect_file_selected(self.tab_manager.open_file)

    def init_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(*WINDOW_INITIAL_GEOMETRY)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)

        self.stacked_widget = QStackedWidget()
        self.main_splitter.addWidget(self.stacked_widget)

        self.stacked_widget.addWidget(self.file_browser_manager.get_widget())

        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_widget)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(0)
        
        self.editor_layout.addWidget(self.tab_manager.get_widget())
        
        self.stacked_widget.addWidget(self.editor_widget)

        self.main_splitter.addWidget(self.io_manager.get_widget())
        
        self.main_splitter.setSizes([3 * self.width() // 4, self.width() // 4])

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        self.installEventFilter(self)
        
        self.stacked_widget.setCurrentWidget(self.file_browser_manager.get_widget())

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                current_editor = self.tab_manager.get_current_editor()
                if current_editor:
                    current_editor.setFocus()
                return True
            # Ctrl+B to toggle file browser
            elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_B:
                self.file_browser_manager.toggle_view()
                return True
            # Ctrl+I to toggle IO view
            elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_I:
                self.io_manager.toggle_view()
                return True
            # Ctrl+` to toggle terminal
            elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_QuoteLeft:
                current_file = self.tab_manager.get_current_file()
                working_dir = os.path.dirname(current_file) if current_file else os.getcwd()
                self.terminal_handler.toggle_terminal(working_dir)
                return True
            # Ctrl+Alt+N to compile and run
            elif event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier) and event.key() == Qt.Key.Key_N:
                self.compiler_manager.compile_and_run(self.tab_manager.get_current_file(), debug=False)
                return True
            # F9 to compile with debug flags and run
            elif event.key() == Qt.Key.Key_F9:
                self.compiler_manager.compile_and_run(self.tab_manager.get_current_file(), debug=True)
                return True
            # F3 to cycle between editors
            elif event.key() == Qt.Key.Key_F3:
                self.cycle_editors()
                return True
        return super().eventFilter(obj, event)

    def cycle_editors(self):
        if not self.io_manager.io_widget.isVisible():
            return

        current_editor = self.tab_manager.get_current_editor()
        input_editor = self.io_manager.input_editor
        output_editor = self.io_manager.output_editor
        
        if not current_editor:
            input_editor.setFocus()
            return
            
        editors = [current_editor, input_editor, output_editor]
        
        focused = None
        for i, editor in enumerate(editors):
            if editor.hasFocus():
                focused = i
                break
        
        if focused is None:
            editors[0].setFocus()
            return
            
        next_editor = editors[(focused + 1) % len(editors)]
        next_editor.setFocus()
        
        if next_editor == current_editor:
            self.stacked_widget.setCurrentWidget(self.editor_widget)

    def closeEvent(self, event):
        self.io_manager.save_files()
        super().closeEvent(event)