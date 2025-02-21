from PyQt6.QtWidgets import QMenuBar, QMenu, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from editor.code_editor import CodeEditor
import os

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_menus()

    def init_menus(self):
        file_menu = self.addMenu("&File")
        file_menu.addAction("New", self.new_file).setShortcut("Ctrl+N")
        file_menu.addAction("Open", self.open_file).setShortcut("Ctrl+O")
        file_menu.addAction("Save", self.save_file).setShortcut("Ctrl+S")
        file_menu.addAction("Save As", self.save_file_as).setShortcut("Ctrl+Shift+S")
        file_menu.addAction("Close Tab", self.close_current_tab).setShortcut("Ctrl+W")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.parent().close).setShortcut("Ctrl+Q")

        edit_menu = self.addMenu("&Edit")
        edit_menu.addAction("Undo", self.undo).setShortcut("Ctrl+Z")
        edit_menu.addAction("Redo", self.redo).setShortcut("Ctrl+Y")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut", self.cut).setShortcut("Ctrl+X")
        edit_menu.addAction("Copy", self.copy).setShortcut("Ctrl+C")
        edit_menu.addAction("Paste", self.paste).setShortcut("Ctrl+V")

        view_menu = self.addMenu("&View")
        view_menu.addAction("Toggle File Browser", self.parent().toggle_file_browser).setShortcut("Ctrl+B")
        view_menu.addAction("Toggle Input/Output", self.parent().toggle_io_view).setShortcut("Ctrl+I")

    def new_file(self):
        new_editor = CodeEditor()
        self.parent().tab_widget.addTab(new_editor, "Untitled")
        self.parent().tab_widget.setCurrentWidget(new_editor)
        new_editor.setFocus()

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*.*)"
        )
        if file_name:
            self.parent().open_file(file_name)

    def save_file(self):
        current_editor = self.parent().get_current_editor()
        current_file = self.parent().get_current_file()
        
        if current_editor:
            if current_file:
                self._save_to_file(current_file)
            else:
                self.save_file_as()

    def save_file_as(self):
        current_editor = self.parent().get_current_editor()
        if current_editor:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "",
                "All Files (*.*)"
            )
            if file_name:
                self._save_to_file(file_name)
                # Update tab name and tooltip
                current_index = self.parent().tab_widget.currentIndex()
                self.parent().tab_widget.setTabText(current_index, os.path.basename(file_name))
                self.parent().tab_widget.setTabToolTip(current_index, file_name)

    def _save_to_file(self, file_name):
        current_editor = self.parent().get_current_editor()
        try:
            with open(file_name, 'w') as file:
                file.write(current_editor.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def close_current_tab(self):
        current_index = self.parent().tab_widget.currentIndex()
        if current_index >= 0:
            self.parent().tab_widget.removeTab(current_index)

    def undo(self):
        current_editor = self.parent().get_current_editor()
        if current_editor:
            current_editor.undo()

    def redo(self):
        current_editor = self.parent().get_current_editor()
        if current_editor:
            current_editor.redo()

    def cut(self):
        current_editor = self.parent().get_current_editor()
        if current_editor:
            current_editor.cut()

    def copy(self):
        current_editor = self.parent().get_current_editor()
        if current_editor:
            current_editor.copy()

    def paste(self):
        current_editor = self.parent().get_current_editor()
        if current_editor:
            current_editor.paste() 