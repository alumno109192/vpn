"""File dialog thread module."""

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path


class FileDialogThread(QThread):
    """Thread for handling file selection dialog without blocking the UI."""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
    def run(self):
        """Open file dialog in a separate thread."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Seleccionar archivo .ovpn",
            str(Path.home()),
            "Archivos OVPN (*.ovpn);;Todos los archivos (*)",
            options=options
        )
        if file_path:
            self.file_selected.emit(file_path)
