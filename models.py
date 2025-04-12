from enum import Enum
from PyQt5.QtWidgets import QPushButton, QSystemTrayIcon, QStyle
from PyQt5.QtGui import QIcon
import platform

class VPNType(Enum):
    OPENVPN = "OpenVPN"
    IPSEC = "IPSec"

class ConnectionState(Enum):
    DISCONNECTED = "Conectar"
    CONNECTING = "Conectando..."
    AUTHENTICATING = "Autenticando..."
    CONNECTED = "Desconectar"

class ConnectionObserver:
    def __init__(self, button, tray_icon):
        self.button = button
        self.tray_icon = tray_icon
        self.state = ConnectionState.DISCONNECTED
        self._update_ui()

    def set_state(self, state: ConnectionState):
        self.state = state
        self._update_ui()

    def _update_ui(self):
        self.button.setText(self.state.value)
        
        if self.state == ConnectionState.DISCONNECTED:
            self.button.setStyleSheet("background-color: #98FB98; border-radius: 5px;")
            self.tray_icon.setToolTip("VPN Desconectada")
        elif self.state == ConnectionState.CONNECTING:
            self.button.setStyleSheet("background-color: #FFD700; border-radius: 5px;")
            self.tray_icon.setToolTip("Conectando VPN...")
        elif self.state == ConnectionState.AUTHENTICATING:
            self.button.setStyleSheet("background-color: #FFD700; border-radius: 5px;")
            self.tray_icon.setToolTip("Autenticando VPN...")
        elif self.state == ConnectionState.CONNECTED:
            self.button.setStyleSheet("background-color: #FF6B6B; border-radius: 5px;")
            self.tray_icon.setToolTip("VPN Conectada")