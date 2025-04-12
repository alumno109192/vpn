import requests
import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

class UpdateDialog(QDialog):
    def __init__(self, current_version, latest_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Actualización Disponible")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout()
        
        # Message
        message = QLabel(f"Hay una nueva versión disponible!\n\n"
                        f"Versión actual: {current_version}\n"
                        f"Nueva versión: {latest_version}")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.update_button = QPushButton("Actualizar")
        self.update_button.clicked.connect(self.accept)
        
        self.postpone_button = QPushButton("Aplazar")
        self.postpone_button.clicked.connect(self.reject)
        
        self.never_button = QPushButton("No volver a preguntar")
        self.never_button.clicked.connect(self.never_update)
        
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.postpone_button)
        button_layout.addWidget(self.never_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.never_clicked = False
    
    def never_update(self):
        self.never_clicked = True
        self.reject()

class UpdateChecker:
    def __init__(self):
        self.current_version = "1.0.0"
        self.github_repo = "alumno109192/vpn"
        self.config_file = "update_config.json"

    def check_for_updates(self):
        try:
            # Load update configuration
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if config.get('never_update', False):
                        return None
            except FileNotFoundError:
                config = {}
            
            # Check GitHub releases with minimal headers
            headers = {
                'User-Agent': 'VPN-App-Updater'
            }
            
            response = requests.get(
                f"https://api.github.com/repos/{self.github_repo}/releases/latest",
                headers=headers
            )
            
            if response.status_code == 200:
                latest_version = response.json()['tag_name'].lstrip('v')
                if self._version_is_newer(latest_version):
                    return latest_version
            elif response.status_code == 403:
                print("DEBUG: GitHub API rate limit exceeded, intente más tarde")
            elif response.status_code == 404:
                print("DEBUG: No se encontraron versiones publicadas en GitHub")
                
        except Exception as e:
            print(f"DEBUG: Error al buscar actualizaciones: {e}")
        return None
    
    def _version_is_newer(self, latest_version):
        current = [int(x) for x in self.current_version.split('.')]
        latest = [int(x) for x in latest_version.split('.')]
        return latest > current
    
    def save_config(self, never_update=False):
        config = {'never_update': never_update}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)