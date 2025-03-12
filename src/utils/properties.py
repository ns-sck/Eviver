from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
import os
import json

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_FILE = os.path.join(PROJECT_DIR, "settings.json")

# Default values for settings that can be overridden by settings.json
WINDOW_TITLE = "Eviver Code Editor"
WINDOW_INITIAL_GEOMETRY = (100, 100, 1200, 800)

EDITOR_FONT_FAMILY = "Consolas"
EDITOR_FONT_SIZE = 10
EDITOR_TAB_WIDTH = 2
EDITOR_USE_TABS = False
EDITOR_INDENTATION = "\t" if EDITOR_USE_TABS else " " * EDITOR_TAB_WIDTH

EDITOR_TEXT_COLOR = QColor("#FFFFFF")
EDITOR_BACKGROUND_COLOR = QColor("#2B2B2B")
EDITOR_CARET_COLOR = QColor("#FFFFFF")
EDITOR_CARET_LINE_COLOR = QColor("#2A2A2A")
EDITOR_MARGIN_BACKGROUND_COLOR = QColor("#111111")

EDITOR_SELECTION_BG_COLOR = QColor("#214283")
EDITOR_SELECTION_FG_COLOR = QColor("#FFFFFF")

EDITOR_BRACE_MATCHED_BG_COLOR = QColor("#404040")
EDITOR_BRACE_MATCHED_FG_COLOR = QColor("#00FF00")
EDITOR_BRACE_UNMATCHED_BG_COLOR = QColor("#802020")
EDITOR_BRACE_UNMATCHED_FG_COLOR = QColor("#FF0000")

SYNTAX_DEFAULT = QColor("#d7d7d7")
SYNTAX_COMMENT = QColor("#FFFF7F")
SYNTAX_DOUBLE_SLASH_COMMENT = QColor("#37743f")
SYNTAX_KEYWORD = QColor("#50B0FF")
SYNTAX_STRING = QColor("#FFFF7F")
SYNTAX_NUMBER = QColor("#EDFFAF")
SYNTAX_PREPROCESSOR = QColor("#C586C0")
SYNTAX_OPERATOR = QColor("#FFFF7F")
SYNTAX_IDENTIFIER = QColor("#FFFF7F")
SYNTAX_TYPE = QColor("#50B0FF")
SYNTAX_SYMBOL = QColor("#CC0099")
SYNTAX_PARANTHESES = QColor("#50B0FF")
SYNTAX_BACKGROUND = QColor("#111111")

IO_WIDGET_TOP_MARGIN = 30
EDITOR_CARET_WIDTH = 2

TERMINAL_WIDTH = 80
TERMINAL_HEIGHT = 32

# Default values for settings that can now be overridden by settings.json
COMPILE_RELEASE_CMD = 'g++ -DLOCAL -std=c++17 -Wshadow -Wall -o "{executable}" "{source}" -O2 -Wno-unused-result'
COMPILE_DEBUG_CMD = 'g++ -DLOCAL -std=c++17 -Wshadow -Wall -o "{executable}" "{source}" -g -D_GLIBCXX_DEBUG'

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

DEFAULT_WORKSPACE_DIR = os.path.expanduser("~/Desktop/algo")

# These paths are not configurable via settings.json
EVIVER_DIR = os.path.expanduser("~/eviver")
IO_DIR = os.path.join(EVIVER_DIR, "io")
BIN_DIR = os.path.join(EVIVER_DIR, "bin")
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"
INPUT_PATH = os.path.join(IO_DIR, INPUT_FILE)
OUTPUT_PATH = os.path.join(IO_DIR, OUTPUT_FILE)
SNIPPETS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "snippets.json")

for directory in [EVIVER_DIR, IO_DIR, BIN_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def load_settings_from_json():
    global EDITOR_FONT, EDITOR_INDENTATION
    
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                
                for key, value in settings.items():
                    if key in globals():
                        if key.endswith('_COLOR') or key.startswith('SYNTAX_'):
                            globals()[key] = QColor(value)
                        elif key == "DEFAULT_WORKSPACE_DIR" and isinstance(value, str) and '~' in value:
                            globals()[key] = os.path.expanduser(value)
                        else:
                            globals()[key] = value
                
                EDITOR_FONT = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
                
                EDITOR_INDENTATION = "\t" if EDITOR_USE_TABS else " " * EDITOR_TAB_WIDTH
                
                return True
    except Exception as e:
        print(f"Error loading settings: {e}")
    return False

EDITOR_FONT = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)

load_settings_from_json()