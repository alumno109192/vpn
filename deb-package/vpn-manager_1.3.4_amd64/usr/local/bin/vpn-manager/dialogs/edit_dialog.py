"""Edit dialog module."""

import logging

from PyQt5.QtWidgets import QDialog, QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout


class EditDialog(QDialog):
    """Dialog for editing existing VPN connections."""

    def __init__(self, parent=None, name="", config_path="", username="", password=""):
        try:
            super().__init__(parent)
            self.setWindowTitle("Editar Configuración")
            self.setGeometry(150, 150, 400, 200)

            self.selected_file = config_path  # Ruta del archivo seleccionado

            # Label y campo de texto para el nombre
            self.name_label = QLabel("Nombre:")
            self.name_input = QLineEdit()
            self.name_input.setText(name)

            # Label y campo de texto para el usuario
            self.username_label = QLabel("Usuario:")
            self.username_input = QLineEdit()
            self.username_input.setText(username)

            # Label y campo de texto para la contraseña
            self.password_label = QLabel("Contraseña:")
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setText(password)

            # Botón "+"
            self.add_file_button = QPushButton("+")
            self.add_file_button.clicked.connect(self.open_file_explorer)

            # Botón "Guardar"
            self.save_button = QPushButton("Guardar")
            self.save_button.clicked.connect(self.accept)

            # Etiqueta para mostrar archivo seleccionado
            self.file_label = QLabel(f"Seleccionado: {config_path}" if config_path else "Ningún archivo seleccionado")

            # Layout principal
            layout = QVBoxLayout()
            layout.addWidget(self.name_label)
            layout.addWidget(self.name_input)
            layout.addWidget(self.username_label)
            layout.addWidget(self.username_input)
            layout.addWidget(self.password_label)
            layout.addWidget(self.password_input)
            layout.addWidget(self.add_file_button)
            layout.addWidget(self.file_label)
            layout.addWidget(self.save_button)
            self.setLayout(layout)
        except Exception as e:
            logging.error(f"Error initializing EditDialog: {e}")

    def open_file_explorer(self):
        """Open file explorer to select .ovpn file."""
        try:
            # Abrir el explorador de archivos para seleccionar un archivo .ovpn
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar archivo .ovpn", "", "Archivos OVPN (*.ovpn);;Todos los archivos (*)", options=options
            )

            # Mostrar la ruta del archivo seleccionado
            if file_path:
                self.selected_file = file_path
                self.file_label.setText(f"Seleccionado: {file_path}")
        except Exception as e:
            logging.error(f"Error opening file explorer: {e}")

    def get_selected_file(self):
        """Get the selected file path."""
        return self.selected_file

    def get_selected_name(self):
        """Get the entered connection name."""
        return self.name_input.text().strip()

    def get_username(self):
        """Get the entered username."""
        return self.username_input.text().strip()

    def get_password(self):
        """Get the entered password."""
        return self.password_input.text().strip()
