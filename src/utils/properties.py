from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
import os

# Window Properties
WINDOW_TITLE = "CP Code Editor"
WINDOW_INITIAL_GEOMETRY = (100, 100, 1200, 800)

# Editor Properties
EDITOR_FONT = QFont('Consolas', 10)
EDITOR_TAB_WIDTH = 2
EDITOR_USE_TABS = False

# Colors
EDITOR_TEXT_COLOR = QColor("#FFFFFF")
EDITOR_BACKGROUND_COLOR = QColor("#2B2B2B")
EDITOR_CARET_COLOR = QColor("#FFFFFF")
EDITOR_CARET_LINE_COLOR = QColor("#2A2A2A")
EDITOR_MARGIN_BACKGROUND_COLOR = QColor("#111111")

# Brace Matching Colors
EDITOR_BRACE_MATCHED_BG_COLOR = QColor("#404040")  # Dark gray background
EDITOR_BRACE_MATCHED_FG_COLOR = QColor("#00FF00")  # Green text
EDITOR_BRACE_UNMATCHED_BG_COLOR = QColor("#802020")  # Dark red background
EDITOR_BRACE_UNMATCHED_FG_COLOR = QColor("#FF0000")  # Red text

# Syntax Highlighting Colors
SYNTAX_DEFAULT = QColor("#d7d7d7")
SYNTAX_COMMENT = QColor("#FFFF7F")
SYNTAX_DOUBLE_SLASH_COMMENT = QColor("#37743f")  # Green color for // comments
SYNTAX_KEYWORD = QColor("#50B0FF")
SYNTAX_STRING = QColor("#FFFF7F")
SYNTAX_NUMBER = QColor("#EDFFAF")
SYNTAX_PREPROCESSOR = QColor("#C586C0")  # Purple color for preprocessor directives
SYNTAX_OPERATOR = QColor("#FFFF7F")
SYNTAX_IDENTIFIER = QColor("#FFFF7F")
SYNTAX_TYPE = QColor("#50B0FF")
SYNTAX_SYMBOL = QColor("#50B0FF")
SYNTAX_PARANTHESES = QColor("#50B0FF")
SYNTAX_BACKGROUND = QColor("#111111")

# Margins and Spacing
IO_WIDGET_TOP_MARGIN = 30
EDITOR_CARET_WIDTH = 2

# File Paths
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"
EVIVER_DIR = os.path.expanduser("~/.eviver")  # Base directory
IO_DIR = os.path.join(EVIVER_DIR, "io")  # Store IO files
BIN_DIR = os.path.join(EVIVER_DIR, "bin")  # Store executables
INPUT_PATH = os.path.join(IO_DIR, INPUT_FILE)
OUTPUT_PATH = os.path.join(IO_DIR, OUTPUT_FILE)

# Compilation Commands
COMPILE_RELEASE_CMD = 'g++ -std=c++17 -Wshadow -Wall -o "{executable}" "{source}" -O2 -Wno-unused-result'
COMPILE_DEBUG_CMD = 'g++ -std=c++17 -Wshadow -Wall -o "{executable}" "{source}" -g -D_GLIBCXX_DEBUG'

# Keyboard Shortcuts
SHORTCUT_NEW_FILE = "Ctrl+N"
SHORTCUT_OPEN_FILE = "Ctrl+O"
SHORTCUT_SAVE_FILE = "Ctrl+S"
SHORTCUT_SAVE_AS = "Ctrl+Shift+S"
SHORTCUT_CLOSE_TAB = "Ctrl+W"
SHORTCUT_EXIT = "Ctrl+Q"
SHORTCUT_TOGGLE_FILE_BROWSER = "Ctrl+B"
SHORTCUT_TOGGLE_IO = "Ctrl+I"
SHORTCUT_TOGGLE_TERMINAL = "Ctrl+`"
SHORTCUT_SNIPPET_PICKER = "Ctrl+J"
SHORTCUT_COMPILE_RUN = "Ctrl+Alt+N"
SHORTCUT_COMPILE_DEBUG = "F9"
SHORTCUT_CYCLE_EDITORS = "F3"

# Terminal Properties
TERMINAL_WIDTH = 80
TERMINAL_HEIGHT = 32

# Default Workspace Directory
DEFAULT_WORKSPACE_DIR = os.path.expanduser("~/Desktop/Competitive-Programming")  # Default directory for file browser 