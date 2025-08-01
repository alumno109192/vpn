"""Sudo password dialog module."""

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout


class SudoPasswordDialog(QDialog):
    """Dialog for requesting sudo password."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Contraseña de administrador requerida (sudo)")
        self.setModal(True)
        layout = QVBoxLayout()
        label = QLabel("Introduce la contraseña de administrador (sudo):")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(label)
        layout.addWidget(self.password_input)
        button_box = QHBoxLayout()
        ok_button = QPushButton("Aceptar")
        cancel_button = QPushButton("Cancelar")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)
        self.setLayout(layout)

    def get_password(self):
        """Get the entered password."""
        return self.password_input.text()
