import json
from pathlib import Path
from PyQt5.QtWidgets import QInputDialog, QLineEdit

class ConfigManager:
    def __init__(self):
        self.config_file = "connections.json"
        self._sudo_password = None

    def save_connections(self, connections, sudo_password=None):
        try:
            data = {
                'connections': connections,
                'sudo_password': sudo_password if sudo_password else self._sudo_password
            }
            with open(self.config_file, "w") as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving connections: {e}")
            return False

    def load_connections(self):
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self._sudo_password = data.get('sudo_password')
                    return data.get('connections', [])
            return []
        except Exception as e:
            print(f"Error loading connections: {e}")
            return []

    def get_sudo_password(self):
        if self._sudo_password:
            return self._sudo_password
            
        password, ok = QInputDialog.getText(
            None, 
            "Contraseña Sudo",
            "Ingrese su contraseña sudo:",
            QLineEdit.Password
        )
        if ok:
            self._sudo_password = password
            # Update the stored configuration with the new sudo password
            connections = self.load_connections()
            self.save_connections(connections, password)
            return password
        return None