from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QDockWidget, 
                             QStackedWidget, QMessageBox, QTabWidget, QSplitter)
from PyQt6.QtCore import Qt, QEvent, QProcess, QTimer
from PyQt6.QtGui import QFont
from .menubar import MenuBar
from .file_browser import FileBrowser
from editor.code_editor import CodeEditor
from utils.properties import *
import os
import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Ensure directories exist
        os.makedirs(IO_DIR, exist_ok=True)
        os.makedirs(BIN_DIR, exist_ok=True)
        # Create empty input and output files if they don't exist
        if not os.path.exists(INPUT_PATH):
            with open(INPUT_PATH, 'w') as f:
                f.write("")
        if not os.path.exists(OUTPUT_PATH):
            with open(OUTPUT_PATH, 'w') as f:
                f.write("")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(*WINDOW_INITIAL_GEOMETRY)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create stacked widget to switch between file browser and editor
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create vertical splitter for main area and terminal
        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Create main horizontal splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.vertical_splitter.addWidget(self.main_splitter)

        # Create file browser
        self.file_browser = FileBrowser()
        self.stacked_widget.addWidget(self.file_browser)

        # Create editor widget container
        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_widget)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(0)
        
        # Create tab widget for main editors
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.editor_layout.addWidget(self.tab_widget)

        # Add editor widget to main splitter
        self.main_splitter.addWidget(self.editor_widget)

        # Create right side widget with input/output editors
        self.io_widget = QWidget()
        self.io_layout = QVBoxLayout(self.io_widget)
        self.io_layout.setContentsMargins(0, IO_WIDGET_TOP_MARGIN, 0, 0)
        
        # Create input editor
        self.input_editor = CodeEditor()
        self.input_editor.setWindowTitle(INPUT_FILE)
        self.io_layout.addWidget(self.input_editor)

        # Create output editor
        self.output_editor = CodeEditor()
        self.output_editor.setWindowTitle(OUTPUT_FILE)
        self.io_layout.addWidget(self.output_editor)

        # Add io_widget to main splitter
        self.main_splitter.addWidget(self.io_widget)
        
        # Set initial sizes (2:1 ratio)
        self.main_splitter.setSizes([2 * self.width() // 3, self.width() // 3])
        
        # Hide IO widget by default
        self.io_widget.hide()

        # Add vertical splitter to stacked widget
        self.stacked_widget.addWidget(self.vertical_splitter)

        # Set initial widget to file browser
        self.stacked_widget.setCurrentWidget(self.file_browser)

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
            # Ctrl+B to toggle file browser
            elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_B:
                self.toggle_file_browser()
                return True
            # Ctrl+` to toggle terminal
            elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_QuoteLeft:
                self.toggle_terminal()
                return True
            # F8 to compile and run
            elif event.key() == Qt.Key.Key_F8:
                self.compile_and_run()
                return True
            # F9 to compile with debug flags and run
            elif event.key() == Qt.Key.Key_F9:
                self.compile_and_run_debug()
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
            if os.path.exists(INPUT_PATH):
                with open(INPUT_PATH, 'r') as f:
                    self.input_editor.setText(f.read())
            
            # Load output.txt
            if os.path.exists(OUTPUT_PATH):
                with open(OUTPUT_PATH, 'r') as f:
                    self.output_editor.setText(f.read())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load I/O files: {str(e)}")

    def save_io_files(self):
        try:
            # Save input.txt
            with open(INPUT_PATH, 'w') as f:
                f.write(self.input_editor.text())
            
            # Save output.txt
            with open(OUTPUT_PATH, 'w') as f:
                f.write(self.output_editor.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save I/O files: {str(e)}")

    def toggle_file_browser(self):
        if self.stacked_widget.currentWidget() == self.file_browser:
            if self.tab_widget.count() > 0:
                self.stacked_widget.setCurrentWidget(self.vertical_splitter)
        else:
            self.stacked_widget.setCurrentWidget(self.file_browser)

    def open_file(self, file_path):
        try:
            # Check if file is already open
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabToolTip(i) == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    self.stacked_widget.setCurrentWidget(self.vertical_splitter)
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
                
                # Switch to editor view
                self.stacked_widget.setCurrentWidget(self.vertical_splitter)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def close_tab(self, index):
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.stacked_widget.setCurrentWidget(self.file_browser)

    def get_current_editor(self):
        return self.tab_widget.currentWidget() if self.tab_widget.count() > 0 else None

    def get_current_file(self):
        if self.tab_widget.count() > 0:
            return self.tab_widget.tabToolTip(self.tab_widget.currentIndex())
        return None

    def toggle_terminal(self):
        current_file = self.get_current_file()
        working_dir = os.path.dirname(current_file) if current_file else os.getcwd()
        
        # Get the main window's geometry for bottom positioning
        window_x = self.x()  # Same x as the main window
        window_y = self.y() + self.height()  # Bottom of the main window
        
        # Try to detect the default terminal
        if os.system("which gnome-terminal > /dev/null") == 0:
            # For GNOME Terminal: WIDTHxHEIGHT+X+Y
            geometry = f"{TERMINAL_WIDTH}x{TERMINAL_HEIGHT}+{window_x}+{window_y}"
            subprocess.Popen(["gnome-terminal", "--geometry", geometry, "--working-directory", working_dir])
        elif os.system("which konsole > /dev/null") == 0:
            # For Konsole: use --geometry but also remember it doesn't always work reliably
            subprocess.Popen(["konsole", "--workdir", working_dir, 
                            "--geometry", f"{window_x},{window_y}"])
        elif os.system("which xterm > /dev/null") == 0:
            # For XTerm: WIDTHxHEIGHT+X+Y
            geometry = f"{TERMINAL_WIDTH}x{TERMINAL_HEIGHT}+{window_x}+{window_y}"
            subprocess.Popen(["xterm", "-geometry", geometry, 
                            "-e", f"cd {working_dir} && $SHELL"])
        else:
            QMessageBox.warning(self, "Warning", "Could not detect a supported terminal emulator")

    def get_executable_path(self, source_file):
        """Get path for executable with unique name based on source file"""
        base_name = os.path.splitext(source_file)[0]
        return os.path.join(BIN_DIR, base_name)

    def compile_and_run(self):
        current_file = self.get_current_file()
        if not current_file:
            QMessageBox.warning(self, "Warning", "No file is currently open")
            return
        if not current_file.endswith('.cpp'):
            QMessageBox.warning(self, "Warning", "Not a C++ file")
            return
            
        working_dir = os.path.dirname(current_file)
        source_file = os.path.basename(current_file)
        executable = self.get_executable_path(source_file)
        
        # Format the compilation command
        compile_cmd = COMPILE_RELEASE_CMD.format(
            executable=executable,
            source=source_file
        )
        
        # Save the file before compiling
        self.menu_bar.save_file()
        
        # Save IO files if IO panel is visible
        if self.io_widget.isVisible():
            self.save_io_files()
            # Clear output before running
            with open(OUTPUT_PATH, 'w') as f:
                f.write("")
            self.output_editor.clear()
            
            # Run in current shell to better handle IO redirection
            cmd = f'cd "{working_dir}" && {compile_cmd} && "{executable}" < "{INPUT_PATH}" > "{OUTPUT_PATH}"'
            try:
                subprocess.run(cmd, shell=True, check=True)
                # Wait a bit longer and reload output file
                QTimer.singleShot(100, self.load_io_files)
                QTimer.singleShot(500, self.load_io_files)  # Second attempt in case of slow execution
            except subprocess.CalledProcessError:
                QMessageBox.warning(self, "Error", "Compilation or execution failed")
        else:
            # Open terminal for interactive use
            if os.system("which gnome-terminal > /dev/null") == 0:
                cmd = f'gnome-terminal --working-directory="{working_dir}" -- bash -c "{compile_cmd} && "{executable}"; read -p \'Press Enter to continue...\'"'
                subprocess.Popen(cmd, shell=True)
            elif os.system("which konsole > /dev/null") == 0:
                cmd = f'konsole --workdir="{working_dir}" -e bash -c "{compile_cmd} && "{executable}"; read -p \'Press Enter to continue...\'"'
                subprocess.Popen(cmd, shell=True)
            elif os.system("which xterm > /dev/null") == 0:
                cmd = f'xterm -e "cd {working_dir} && {compile_cmd} && "{executable}"; read -p \'Press Enter to continue...\'"'
                subprocess.Popen(cmd, shell=True)
            else:
                QMessageBox.warning(self, "Warning", "Could not detect a supported terminal emulator")

    def compile_and_run_debug(self):
        current_file = self.get_current_file()
        if not current_file:
            QMessageBox.warning(self, "Warning", "No file is currently open")
            return
        if not current_file.endswith('.cpp'):
            QMessageBox.warning(self, "Warning", "Not a C++ file")
            return
            
        working_dir = os.path.dirname(current_file)
        source_file = os.path.basename(current_file)
        executable = self.get_executable_path(source_file)
        
        # Format the compilation command
        compile_cmd = COMPILE_DEBUG_CMD.format(
            executable=executable,
            source=source_file
        )
        
        # Save the file before compiling
        self.menu_bar.save_file()
        
        # Save IO files if IO panel is visible
        if self.io_widget.isVisible():
            self.save_io_files()
            # Clear output before running
            with open(OUTPUT_PATH, 'w') as f:
                f.write("")
            self.output_editor.clear()
            
            # Run in current shell to better handle IO redirection
            cmd = f'cd "{working_dir}" && {compile_cmd} && "{executable}" < "{INPUT_PATH}" > "{OUTPUT_PATH}"'
            try:
                subprocess.run(cmd, shell=True, check=True)
                # Wait a bit longer and reload output file
                QTimer.singleShot(100, self.load_io_files)
                QTimer.singleShot(500, self.load_io_files)  # Second attempt in case of slow execution
            except subprocess.CalledProcessError:
                QMessageBox.warning(self, "Error", "Compilation or execution failed")
        else:
            # Open terminal for interactive use
            if os.system("which gnome-terminal > /dev/null") == 0:
                cmd = f'gnome-terminal --working-directory="{working_dir}" -- bash -c "{compile_cmd} && "{executable}"; read -p \'Press Enter to continue...\'"'
                subprocess.Popen(cmd, shell=True)
            elif os.system("which konsole > /dev/null") == 0:
                cmd = f'konsole --workdir="{working_dir}" -e bash -c "{compile_cmd} && "{executable}"; read -p \'Press Enter to continue...\'"'
                subprocess.Popen(cmd, shell=True)
            elif os.system("which xterm > /dev/null") == 0:
                cmd = f'xterm -e "cd {working_dir} && {compile_cmd} && "{executable}"; read -p \'Press Enter to continue...\'"'
                subprocess.Popen(cmd, shell=True)
            else:
                QMessageBox.warning(self, "Warning", "Could not detect a supported terminal emulator")

    def closeEvent(self, event):
        # Save IO files before closing
        if self.io_widget.isVisible():
            self.save_io_files()
        # Clean up old executables
        try:
            for file in os.listdir(BIN_DIR):
                file_path = os.path.join(BIN_DIR, file)
                try:
                    os.remove(file_path)
                except:
                    pass
        except:
            pass
        super().closeEvent(event)