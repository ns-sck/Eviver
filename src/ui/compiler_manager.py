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
        
        # Kill any existing process
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.process.waitForFinished()
            self.process = None

        # Prepare compilation command
        compile_cmd = COMPILE_DEBUG_CMD if debug else COMPILE_RELEASE_CMD
        compile_cmd = compile_cmd.format(
            executable=executable,
            source=source_path
        )

        # Run compilation in shell
        compile_process = QProcess()
        compile_process.setWorkingDirectory(working_dir)
        compile_process.start('/bin/sh', ['-c', compile_cmd])
        compile_process.waitForFinished()

        if compile_process.exitCode() != 0:
            error = compile_process.readAllStandardError().data().decode()
            QMessageBox.critical(self.parent, "Compilation Error", error)
            return

        # Check if IO panel is visible
        if self.parent.io_manager.io_widget.isVisible():
            # Run with IO redirection
            self.run_with_io(executable, working_dir)
        else:
            # Run in terminal
            self.run_in_terminal(executable, working_dir)

    def run_with_io(self, executable, working_dir):
        # Clear the output editor
        self.parent.io_manager.output_editor.clear()
        
        # Save input to file
        self.parent.io_manager.save_files()
        
        # Create process for running with IO redirection
        self.process = QProcess()
        self.process.setWorkingDirectory(working_dir)
        
        # Set up IO redirection
        self.process.setStandardInputFile(INPUT_PATH)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        
        # Connect output signal
        self.process.readyReadStandardOutput.connect(
            lambda: self.handle_output(self.process.readAllStandardOutput())
        )
        
        # Start the executable
        self.process.start(executable)
        
    def run_in_terminal(self, executable, working_dir):
        # Launch terminal and run the executable
        self.parent.terminal_handler.toggle_terminal(working_dir, f"{executable}")
        
    def handle_output(self, data):
        output = data.data().decode()
        # Write to output editor
        self.parent.io_manager.output_editor.setText(output)
        # Also save to output file
        try:
            with open(OUTPUT_PATH, 'w') as f:
                f.write(output)
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Could not save output: {str(e)}") 