import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from utils.properties import WINDOW_TITLE

# Disable Python's module caching in development mode
if os.environ.get('DEV_MODE', '0') == '1':
    sys.dont_write_bytecode = True  # Prevents creation of .pyc files
    # Force reload of modules
    for module in list(sys.modules.keys()):
        if module not in sys.builtin_module_names and module != '__main__':
            if module in sys.modules:
                del sys.modules[module]

class CustomMainWindow(MainWindow):
    def __init__(self):
        super().__init__()
        self.is_fullscreen = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            if self.is_fullscreen:
                self.showNormal()
            else:
                self.showFullScreen()
            self.is_fullscreen = not self.is_fullscreen
        super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    
    # Set application name and window title for the entire application
    app.setApplicationName(WINDOW_TITLE)
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = CustomMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 