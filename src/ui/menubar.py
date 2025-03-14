from PyQt6.QtWidgets import QMenuBar, QMenu, QFileDialog, QMessageBox, QDialog
from PyQt6.QtCore import Qt
from editor.code_editor import CodeEditor
from utils.properties import *
import os

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_menus()

    def init_menus(self):
        file_menu = self.addMenu("&File")
        file_menu.addAction("New", self.new_file).setShortcut(SHORTCUT_NEW_FILE)
        file_menu.addAction("Open", self.open_file).setShortcut(SHORTCUT_OPEN_FILE)
        file_menu.addAction("Save", self.save_file).setShortcut(SHORTCUT_SAVE_FILE)
        file_menu.addAction("Save As", self.save_file_as).setShortcut(SHORTCUT_SAVE_AS)
        file_menu.addAction("Close Tab", self.close_current_tab).setShortcut(SHORTCUT_CLOSE_TAB)
        file_menu.addSeparator()
        file_menu.addAction("Settings", self.show_settings).setShortcut("Ctrl+,")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.parent().close).setShortcut(SHORTCUT_EXIT)

        edit_menu = self.addMenu("&Edit")
        edit_menu.addAction("Undo", self.undo).setShortcut("Ctrl+Z")
        edit_menu.addAction("Redo", self.redo).setShortcut("Ctrl+Y")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut", self.cut).setShortcut("Ctrl+X")
        edit_menu.addAction("Copy", self.copy).setShortcut("Ctrl+C")
        edit_menu.addAction("Paste", self.paste).setShortcut("Ctrl+V")

        view_menu = self.addMenu("&View")
        view_menu.addAction("Toggle File Browser", self.toggle_file_browser).setShortcut(SHORTCUT_TOGGLE_FILE_BROWSER)
        view_menu.addAction("Toggle Input/Output", self.toggle_io_view).setShortcut(SHORTCUT_TOGGLE_IO)
        view_menu.addAction("Toggle Terminal", self.toggle_terminal).setShortcut(SHORTCUT_TOGGLE_TERMINAL)

        build_menu = self.addMenu("&Build")
        build_menu.addAction("Compile and Run", self.compile_and_run).setShortcut(SHORTCUT_COMPILE_RUN)
        build_menu.addAction("Compile and Debug", self.compile_and_debug).setShortcut(SHORTCUT_COMPILE_DEBUG)

    def new_file(self):
        new_editor = CodeEditor()
        self.parent().tab_manager.get_widget().addTab(new_editor, "Untitled")
        self.parent().tab_manager.get_widget().setCurrentWidget(new_editor)
        new_editor.setFocus()

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*.*)"
        )
        if file_name:
            self.parent().tab_manager.open_file(file_name)

    def save_file(self):
        current_editor = self.parent().tab_manager.get_current_editor()
        current_file = self.parent().tab_manager.get_current_file()
        
        if current_editor:
            if current_file:
                self._save_to_file(current_file)
            else:
                self.save_file_as()

    def save_file_as(self):
        current_editor = self.parent().tab_manager.get_current_editor()
        if current_editor:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "",
                "All Files (*.*)"
            )
            if file_name:
                self._save_to_file(file_name)
                current_editor.set_file_path(file_name)
                current_index = self.parent().tab_manager.get_widget().currentIndex()
                self.parent().tab_manager.get_widget().setTabText(current_index, os.path.basename(file_name))
                self.parent().tab_manager.get_widget().setTabToolTip(current_index, file_name)

    def _save_to_file(self, file_name):
        current_editor = self.parent().tab_manager.get_current_editor()
        try:
            with open(file_name, 'w') as file:
                file.write(current_editor.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def close_current_tab(self):
        current_index = self.parent().tab_manager.get_widget().currentIndex()
        if current_index >= 0:
            self.parent().tab_manager.close_tab(current_index)

    def toggle_io_view(self):
        self.parent().io_manager.toggle_view()

    def toggle_terminal(self):
        current_file = self.parent().tab_manager.get_current_file()
        working_dir = os.path.dirname(current_file) if current_file else os.getcwd()
        self.parent().terminal_handler.toggle_terminal(working_dir)

    def compile_and_run(self):
        self.parent().compiler_manager.compile_and_run(
            self.parent().tab_manager.get_current_file(), 
            debug=False
        )

    def compile_and_debug(self):
        self.parent().compiler_manager.compile_and_run(
            self.parent().tab_manager.get_current_file(), 
            debug=True
        )

    def undo(self):
        current_editor = self.parent().tab_manager.get_current_editor()
        if current_editor:
            current_editor.undo()

    def redo(self):
        current_editor = self.parent().tab_manager.get_current_editor()
        if current_editor:
            current_editor.redo()

    def cut(self):
        current_editor = self.parent().tab_manager.get_current_editor()
        if current_editor:
            current_editor.cut()

    def copy(self):
        current_editor = self.parent().tab_manager.get_current_editor()
        if current_editor:
            current_editor.copy()

    def paste(self):
        current_editor = self.parent().tab_manager.get_current_editor()
        if current_editor:
            current_editor.paste()

    def toggle_file_browser(self):
        self.parent().file_browser_manager.toggle_view()

    def show_settings(self):
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Settings", "Settings saved. Please restart the application for changes to take effect.") 