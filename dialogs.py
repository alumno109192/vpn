from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                           QPushButton, QLabel, QFileDialog, QComboBox, QWidget)
from PyQt5.QtCore import Qt
from models import VPNType

class ConfigureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Nueva VPN")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # VPN Type selection
        self.vpn_type = QComboBox()
        self.vpn_type.addItems([t.value for t in VPNType])
        layout.addWidget(QLabel("Tipo de VPN:"))
        layout.addWidget(self.vpn_type)
        
        # Name field
        self.name_input = QLineEdit()
        layout.addWidget(QLabel("Nombre de la conexión:"))
        layout.addWidget(self.name_input)
        
        # Config file selection (for OpenVPN)
        self.config_container = QWidget()
        config_layout = QHBoxLayout()
        self.config_path_input = QLineEdit()
        config_layout.addWidget(self.config_path_input)
        browse_button = QPushButton("Buscar")
        browse_button.clicked.connect(self.browse_config)
        config_layout.addWidget(browse_button)
        self.config_container.setLayout(config_layout)
        
        layout.addWidget(QLabel("Archivo de configuración:"))
        layout.addWidget(self.config_container)
        
        # Server address (for IPSec)
        self.server_input = QLineEdit()
        layout.addWidget(QLabel("Dirección del servidor:"))
        layout.addWidget(self.server_input)
        
        # Username field
        self.username_input = QLineEdit()
        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.username_input)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.password_input)
        
        # Shared Secret (for IPSec)
        self.shared_secret_input = QLineEdit()
        self.shared_secret_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Shared Secret (solo IPSec):"))
        layout.addWidget(self.shared_secret_input)
        
        # Connect type selection change
        self.vpn_type.currentTextChanged.connect(self.on_vpn_type_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Guardar")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.on_vpn_type_changed(self.vpn_type.currentText())

    def on_vpn_type_changed(self, vpn_type):
        is_openvpn = vpn_type == VPNType.OPENVPN.value
        self.config_container.setVisible(is_openvpn)
        self.server_input.setVisible(not is_openvpn)
        self.shared_secret_input.setVisible(not is_openvpn)

    def browse_config(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de configuración",
            "",
            "Archivos OpenVPN (*.ovpn);;Todos los archivos (*)"
        )
        if file_name:
            self.config_path_input.setText(file_name)

class EditDialog(QDialog):
    def __init__(self, parent=None, name="", config_path="", username="", password=""):
        super().__init__(parent)
        self.setWindowTitle("Editar VPN")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Name field
        self.name_input = QLineEdit(name)
        layout.addWidget(QLabel("Nombre de la conexión:"))
        layout.addWidget(self.name_input)
        
        # Config file selection
        self.config_path_input = QLineEdit(config_path)
        layout.addWidget(QLabel("Archivo de configuración:"))
        config_layout = QHBoxLayout()
        config_layout.addWidget(self.config_path_input)
        browse_button = QPushButton("Buscar")
        browse_button.clicked.connect(self.browse_config)
        config_layout.addWidget(browse_button)
        layout.addLayout(config_layout)
        
        # Username field
        self.username_input = QLineEdit(username)
        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.username_input)
        
        # Password field
        self.password_input = QLineEdit(password)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Guardar")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def browse_config(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de configuración",
            "",
            "Archivos OpenVPN (*.ovpn);;Todos los archivos (*)"
        )
        if file_name:
            self.config_path_input.setText(file_name)