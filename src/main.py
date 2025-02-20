import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow

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
    window = CustomMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 