from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import platform
import subprocess
import shutil

class SetupThread(QThread):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(bool, str)

    def run(self):
        try:
            self.progress.emit("Comprobando sistema operativo...", 10)
            system = platform.system()

            if system == "Darwin":  # macOS
                self._setup_macos()
            elif system == "Linux":
                self._setup_linux()
            elif system == "Windows":
                self._setup_windows()
            else:
                self.finished.emit(False, "Sistema operativo no soportado")
                return

            self.progress.emit("Verificando instalación...", 90)
            if self._verify_installation():
                self.finished.emit(True, "Instalación completada")
            else:
                self.finished.emit(False, "Error en la verificación")

        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

    def _setup_macos(self):
        self.progress.emit("Comprobando Homebrew...", 20)
        if not shutil.which("brew"):
            self.progress.emit("Instalando Homebrew...", 30)
            subprocess.run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', shell=True, check=True)

        self.progress.emit("Actualizando Homebrew...", 40)
        subprocess.run(['brew', 'update'], check=True)

        self.progress.emit("Instalando OpenVPN...", 60)
        subprocess.run(['brew', 'install', 'openvpn'], check=True)

        self.progress.emit("Instalando StrongSwan...", 70)
        subprocess.run(['brew', 'install', 'strongswan'], check=True)

    def _setup_linux(self):
        self.progress.emit("Actualizando repositorios...", 30)
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)

        self.progress.emit("Instalando OpenVPN...", 50)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'openvpn'], check=True)

        self.progress.emit("Instalando StrongSwan...", 70)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'strongswan'], check=True)

    def _setup_windows(self):
        self.progress.emit("Comprobando Chocolatey...", 20)
        try:
            subprocess.run(['choco', '--version'], check=True)
        except:
            self.progress.emit("Instalando Chocolatey...", 30)
            subprocess.run('powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://chocolatey.org/install.ps1\'))"', shell=True, check=True)

        self.progress.emit("Instalando OpenVPN...", 50)
        subprocess.run(['choco', 'install', 'openvpn', '-y'], check=True)

        self.progress.emit("Instalando StrongSwan...", 70)
        subprocess.run(['choco', 'install', 'strongswan', '-y'], check=True)

    def _verify_installation(self):
        required_tools = ['openvpn', 'strongswan']
        for tool in required_tools:
            if not shutil.which(tool):
                return False
        return True

class SetupWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración Inicial")
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Preparando la instalación...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        self.setup_thread = SetupThread()
        self.setup_thread.progress.connect(self.update_progress)
        self.setup_thread.finished.connect(self.setup_finished)
        
        # Start the setup process
        self.setup_thread.start()
    
    def update_progress(self, status, value):
        self.status_label.setText(status)
        self.progress_bar.setValue(value)
    
    def setup_finished(self, success, message):
        if success:
            self.accept()
        else:
            self.status_label.setText(f"Error: {message}")
            self.progress_bar.setValue(0)