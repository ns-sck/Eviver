from PyQt6.QtWidgets import QMenuBar, QMenu, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QKeyCombination
import os

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_menus()
        self.current_file = None

    def init_menus(self):
        file_menu = self.addMenu("&File")
        file_menu.addAction("New", self.new_file).setShortcut("Ctrl+N")
        file_menu.addAction("Open", self.open_file).setShortcut("Ctrl+O")
        file_menu.addAction("Save", self.save_file).setShortcut("Ctrl+S")
        file_menu.addAction("Save As", self.save_file_as).setShortcut("Ctrl+Shift+S")
        file_menu.addSeparator()
        file_menu.addAction("Back to Browser", self.show_browser).setShortcut("Ctrl+B")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.parent().close).setShortcut("Ctrl+Q")

        edit_menu = self.addMenu("&Edit")
        edit_menu.addAction("Undo", self.undo).setShortcut("Ctrl+Z")
        edit_menu.addAction("Redo", self.redo).setShortcut("Ctrl+Y")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut", self.cut).setShortcut("Ctrl+X")
        edit_menu.addAction("Copy", self.copy).setShortcut("Ctrl+C")
        edit_menu.addAction("Paste", self.paste).setShortcut("Ctrl+V")

    def new_file(self):
        if self.parent().code_editor:
            self.parent().code_editor.clear()
            self.current_file = None
            self.parent().setWindowTitle("CP Code Editor - Untitled")

    def open_file(self):
        if self.parent().code_editor:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Open File",
                "",
                "C++ Files (*.cpp *.h);;All Files (*.*)"
            )
            if file_name:
                try:
                    with open(file_name, 'r') as file:
                        self.parent().code_editor.setText(file.read())
                        self.current_file = file_name
                        self.parent().setWindowTitle(f"CP Code Editor - {os.path.basename(file_name)}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_file(self):
        if self.parent().code_editor:
            if self.current_file:
                self._save_to_file(self.current_file)
            else:
                self.save_file_as()

    def save_file_as(self):
        if self.parent().code_editor:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "",
                "C++ Files (*.cpp *.h);;All Files (*.*)"
            )
            if file_name:
                self._save_to_file(file_name)

    def _save_to_file(self, file_name):
        try:
            with open(file_name, 'w') as file:
                file.write(self.parent().code_editor.text())
            self.current_file = file_name
            self.parent().setWindowTitle(f"CP Code Editor - {os.path.basename(file_name)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def undo(self):
        if self.parent().code_editor:
            self.parent().code_editor.undo()

    def redo(self):
        if self.parent().code_editor:
            self.parent().code_editor.redo()

    def cut(self):
        if self.parent().code_editor:
            self.parent().code_editor.cut()

    def copy(self):
        if self.parent().code_editor:
            self.parent().code_editor.copy()

    def paste(self):
        if self.parent().code_editor:
            self.parent().code_editor.paste()

    def show_browser(self):
        self.parent().show_file_browser() 