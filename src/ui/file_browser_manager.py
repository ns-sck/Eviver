from PyQt6.QtWidgets import QWidget
from .file_browser import FileBrowser

class FileBrowserManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.file_browser = FileBrowser()
        self.file_browser.fileSelected.connect(self._on_file_selected)
        
    def toggle_view(self):
        if self.parent.stacked_widget.currentWidget() == self.file_browser:
            self.parent.stacked_widget.setCurrentWidget(self.parent.editor_widget)
        else:
            self.parent.stacked_widget.setCurrentWidget(self.file_browser)
            
    def get_widget(self):
        return self.file_browser
        
    def connect_file_selected(self, slot):
        self.file_browser.fileSelected.connect(slot)
        
    def _on_file_selected(self, file_path):
        self.parent.stacked_widget.setCurrentWidget(self.parent.editor_widget) 