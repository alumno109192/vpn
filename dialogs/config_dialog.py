"""Configuration dialog module."""

import logging
import threading
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTabWidget, QWidget, QMessageBox
)
from PyQt5.QtCore import QMetaObject, Qt, Q_ARG


class ConfigureDialog(QDialog):
    """Dialog for configuring new VPN connections (OpenVPN and IPSec)."""
    
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle("Configurar")
            self.setGeometry(150, 150, 400, 300)

            # Create tab widget
            self.tab_widget = QTabWidget()
            
            # Create tabs
            self.openvpn_tab = QWidget()
            self.ipsec_tab = QWidget()
            
            # Add tabs to widget
            self.tab_widget.addTab(self.openvpn_tab, "OpenVPN")
            self.tab_widget.addTab(self.ipsec_tab, "IPSec")
            
            # Setup OpenVPN tab
            self.setup_openvpn_tab()
            
            # Setup IPSec tab
            self.setup_ipsec_tab()
            
            # Main layout
            main_layout = QVBoxLayout()
            main_layout.addWidget(self.tab_widget)
            self.setLayout(main_layout)
        except Exception as e:
            logging.error(f"Error initializing ConfigureDialog: {e}")

    def setup_openvpn_tab(self):
        """Setup the OpenVPN configuration tab."""
        try:
            layout = QVBoxLayout()
            
            # Original OpenVPN widgets
            self.name_label = QLabel("Nombre:")
            self.name_input = QLineEdit()
            
            self.username_label = QLabel("Usuario:")
            self.username_input = QLineEdit()
            
            self.password_label = QLabel("Contraseña:")
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            
            self.add_file_button = QPushButton("+")
            self.add_file_button.clicked.connect(self.open_file_explorer)
            
            self.file_label = QLabel("Ningún archivo seleccionado")
            
            self.save_button = QPushButton("Guardar")
            self.save_button.clicked.connect(self.accept)
            
            # Add widgets to layout
            layout.addWidget(self.name_label)
            layout.addWidget(self.name_input)
            layout.addWidget(self.username_label)
            layout.addWidget(self.username_input)
            layout.addWidget(self.password_label)
            layout.addWidget(self.password_input)
            layout.addWidget(self.add_file_button)
            layout.addWidget(self.file_label)
            layout.addWidget(self.save_button)
            
            self.openvpn_tab.setLayout(layout)
        except Exception as e:
            logging.error(f"Error setting up OpenVPN tab: {e}")

    def setup_ipsec_tab(self):
        """Setup the IPSec configuration tab."""
        try:
            layout = QVBoxLayout()
            
            # IPSec specific widgets
            self.ipsec_name_label = QLabel("Nombre:")
            self.ipsec_name_input = QLineEdit()
            
            self.server_label = QLabel("Servidor:")
            self.server_input = QLineEdit()
            
            self.shared_secret_label = QLabel("Secreto Compartido:")
            self.shared_secret_input = QLineEdit()
            self.shared_secret_input.setEchoMode(QLineEdit.Password)
            
            self.ipsec_username_label = QLabel("Usuario:")
            self.ipsec_username_input = QLineEdit()
            
            self.ipsec_password_label = QLabel("Contraseña:")
            self.ipsec_password_input = QLineEdit()
            self.ipsec_password_input.setEchoMode(QLineEdit.Password)
            
            self.ipsec_save_button = QPushButton("Guardar")
            self.ipsec_save_button.clicked.connect(self.save_ipsec)
            
            # Add widgets to layout
            layout.addWidget(self.ipsec_name_label)
            layout.addWidget(self.ipsec_name_input)
            layout.addWidget(self.server_label)
            layout.addWidget(self.server_input)
            layout.addWidget(self.shared_secret_label)
            layout.addWidget(self.shared_secret_input)
            layout.addWidget(self.ipsec_username_label)
            layout.addWidget(self.ipsec_username_input)
            layout.addWidget(self.ipsec_password_label)
            layout.addWidget(self.ipsec_password_input)
            layout.addWidget(self.ipsec_save_button)
            
            self.ipsec_tab.setLayout(layout)
        except Exception as e:
            logging.error(f"Error setting up IPSec tab: {e}")

    def save_ipsec(self):
        """Save IPSec configuration."""
        try:
            # Get IPSec configuration
            config = {
                'name': self.ipsec_name_input.text().strip(),
                'server': self.server_input.text().strip(),
                'shared_secret': self.shared_secret_input.text().strip(),
                'username': self.ipsec_username_input.text().strip(),
                'password': self.ipsec_password_input.text().strip(),
                'type': 'ipsec'
            }
            
            # Validate required fields
            if all(config.values()):
                self.ipsec_config = config
                self.accept()
            else:
                # Show error message if fields are empty
                error_dialog = QDialog(self)
                error_dialog.setWindowTitle("Error")
                layout = QVBoxLayout()
                label = QLabel("Por favor, complete todos los campos")
                button = QPushButton("Aceptar")
                button.clicked.connect(error_dialog.accept)
                layout.addWidget(label)
                layout.addWidget(button)
                error_dialog.setLayout(layout)
                error_dialog.exec_()
        except Exception as e:
            logging.error(f"Error saving IPSec configuration: {e}")

    def open_file_explorer(self):
        """Open file explorer to select .ovpn file."""
        try:
            def select_file():
                from tkinter import Tk, filedialog
                root = Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(
                    title="Seleccionar archivo .ovpn",
                    filetypes=[("Archivos OVPN", "*.ovpn"), ("Todos los archivos", "*.*")]
                )
                root.destroy()
                if file_path:
                    # Actualiza la UI de Qt en el hilo principal
                    QMetaObject.invokeMethod(
                        self.file_label, "setText", Qt.QueuedConnection,
                        Q_ARG(str, f"Seleccionado: {file_path}")
                    )
                    self.selected_file = file_path
            threading.Thread(target=select_file).start()
        except Exception as e:
            logging.error(f"Error abriendo el selector de archivos con Tkinter: {e}")
            QMessageBox.critical(
                self, "Error",
                f"Error abriendo el selector de archivos con Tkinter:\n{e}"
            )

    def get_selected_file(self):
        """Get the selected file path."""
        return getattr(self, 'selected_file', '')

    def get_selected_name(self):
        """Get the entered connection name."""
        return self.name_input.text().strip()

    def get_username(self):
        """Get the entered username."""
        return self.username_input.text().strip()

    def get_password(self):
        """Get the entered password."""
        return self.password_input.text().strip()
