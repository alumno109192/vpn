"""VPN connection thread module."""

from PyQt5.QtCore import QThread, pyqtSignal


class VPNConnectThread(QThread):
    """Thread for handling VPN connections without blocking the UI."""
    
    result = pyqtSignal(bool, str)
    
    def __init__(self, connect_func):
        super().__init__()
        self.connect_func = connect_func
        
    def run(self):
        """Execute the VPN connection function in a separate thread."""
        try:
            ok = self.connect_func()
            self.result.emit(ok, "" if ok else "Error de conexión")
        except Exception as e:
            self.result.emit(False, str(e))
