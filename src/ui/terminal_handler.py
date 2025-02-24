from PyQt6.QtWidgets import QMessageBox
from utils.properties import *
import os
import subprocess
import shlex

class TerminalHandler:
    def __init__(self, parent=None):
        self.parent = parent

    def toggle_terminal(self, working_dir=None, command=None):
        if working_dir is None or not os.path.isdir(working_dir):
            working_dir = os.getcwd()
        
        # Get the main window's geometry for bottom positioning
        window_x = self.parent.x()
        window_y = self.parent.y() + self.parent.height()
        
        # Prepare the command to run in terminal
        if command:
            shell_cmd = f"cd {shlex.quote(working_dir)} && {command} && exec $SHELL"
        else:
            shell_cmd = f"cd {shlex.quote(working_dir)} && exec $SHELL"
        
        # Try to detect the default terminal
        if os.system("which gnome-terminal > /dev/null") == 0:
            # For GNOME Terminal
            cmd = ["gnome-terminal", "--geometry", f"{TERMINAL_WIDTH}x{TERMINAL_HEIGHT}+{window_x}+{window_y}"]
            if working_dir:
                cmd.extend(["--working-directory", working_dir])
            if command:
                cmd.extend(["--", "bash", "-c", shell_cmd])
            subprocess.Popen(cmd)
            
        elif os.system("which konsole > /dev/null") == 0:
            # For Konsole
            cmd = ["konsole"]
            if working_dir:
                cmd.extend(["--workdir", working_dir])
            if command:
                cmd.extend(["-e", "bash", "-c", shell_cmd])
            subprocess.Popen(cmd)
            
        elif os.system("which xterm > /dev/null") == 0:
            # For XTerm
            geometry = f"{TERMINAL_WIDTH}x{TERMINAL_HEIGHT}+{window_x}+{window_y}"
            cmd = ["xterm", "-geometry", geometry, "-e", shell_cmd]
            subprocess.Popen(cmd)
            
        else:
            QMessageBox.warning(self.parent, "Warning", "Could not detect a supported terminal emulator")