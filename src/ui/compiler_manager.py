from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QProcess
from utils.properties import *
import os
import shlex

class CompilerManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.process = None
        os.makedirs(BIN_DIR, exist_ok=True)

    def get_executable_path(self, source_file):
        """Get path for executable with unique name based on source file"""
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        return os.path.join(BIN_DIR, base_name)

    def compile_and_run(self, source_path, debug=False):
        if not source_path:
            QMessageBox.warning(self.parent, "Warning", "No file is currently open")
            return
        if not source_path.endswith('.cpp'):
            QMessageBox.warning(self.parent, "Warning", "Not a C++ file")
            return

        working_dir = os.path.dirname(source_path)
        executable = self.get_executable_path(source_path)
        
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.process.waitForFinished()
            self.process = None

        compile_cmd = COMPILE_DEBUG_CMD if debug else COMPILE_RELEASE_CMD
        compile_cmd = compile_cmd.format(
            executable=executable,
            source=source_path
        )

        compile_process = QProcess()
        compile_process.setWorkingDirectory(working_dir)
        compile_process.start('/bin/sh', ['-c', compile_cmd])
        compile_process.waitForFinished()

        if compile_process.exitCode() != 0:
            error = compile_process.readAllStandardError().data().decode()
            
            # Write compilation error to output.txt instead of showing popup
            self.parent.io_manager.output_editor.setText(error)
            try:
                with open(OUTPUT_PATH, 'w') as f:
                    f.write(error)
            except Exception as e:
                QMessageBox.critical(self.parent, "Error", f"Could not save output: {str(e)}")
            
            # Make sure the IO widget is visible to show the error
            if not self.parent.io_manager.io_widget.isVisible():
                self.parent.io_manager.toggle_view()
                
            return

        if self.parent.io_manager.io_widget.isVisible():
            self.run_with_io(executable, working_dir)
        else:
            self.run_in_terminal(executable, working_dir)

    def run_with_io(self, executable, working_dir):
        self.parent.io_manager.output_editor.clear()
        
        self.parent.io_manager.save_files()
        
        self.process = QProcess()
        self.process.setWorkingDirectory(working_dir)
        
        self.process.setStandardInputFile(INPUT_PATH)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        
        self.process.readyReadStandardOutput.connect(
            lambda: self.handle_output(self.process.readAllStandardOutput())
        )
        
        self.process.start(executable)
        
    def run_in_terminal(self, executable, working_dir):
        self.parent.terminal_handler.toggle_terminal(working_dir, f"{executable}")
        
    def handle_output(self, data):
        output = data.data().decode()
        self.parent.io_manager.output_editor.setText(output)
        try:
            with open(OUTPUT_PATH, 'w') as f:
                f.write(output)
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Could not save output: {str(e)}") 