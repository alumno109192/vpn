#!/Library/Frameworks/Python.framework/Versions/3.12/bin/python3
import sys
import subprocess
import json
import logging
import requests
import tempfile
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QProgressDialog, QMessageBox, QMenu, QSystemTrayIcon, QStyle, QDialog, QLineEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor
import platform
import os
from pathlib import Path

# Import from local modules
from models import VPNType, ConnectionState, ConnectionObserver
from dialogs import SudoPasswordDialog, ConfigureDialog, EditDialog
from threads import VPNConnectThread
from license import LicenseManager
from license_storage import LicenseStorage

# Configure logging
logging.basicConfig(
    filename='vpn_setup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("VPN Manager")
            self.setGeometry(100, 100, 500, 400)

            # Show progress dialog while checking libraries
            self.show_library_check_progress()

            # Initialize tray menu and icon
            self.tray_menu = QMenu()
            # Use lock icon for system tray
            lock_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView) if platform.system() == 'Darwin' else QIcon.fromTheme("security-high")
            self.tray_icon = QSystemTrayIcon(lock_icon, self)
            self.tray_icon.setContextMenu(self.tray_menu)
            self.tray_icon.show()

            # Add "Open" action
            open_action = self.tray_menu.addAction("Abrir")
            open_action.triggered.connect(self.show)

            # Add connections submenu
            self.connections_menu = self.tray_menu.addMenu("Conexiones")

            # Add autostart option
            self.autostart_action = self.tray_menu.addAction("Iniciar con el sistema")
            self.autostart_action.setCheckable(True)
            self.autostart_action.setChecked(self.is_autostart_enabled())
            self.autostart_action.triggered.connect(self.toggle_autostart)

            # Add separator
            self.tray_menu.addSeparator()

            # Add "Exit" action
            exit_action = self.tray_menu.addAction("Salir")
            exit_action.triggered.connect(QApplication.instance().quit)

            # Configure button
            self.configure_button = QPushButton("Configurar")
            self.configure_button.clicked.connect(self.open_configure_window)

            # List widget setup
            self.list_widget = QListWidget()
            self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            # Main layout
            layout = QVBoxLayout()
            
            # Button layout
            button_row = QHBoxLayout()
            button_row.addWidget(self.configure_button)
            layout.addLayout(button_row)
            layout.addWidget(self.list_widget)

            # Botón inferior para activar licencia
            self.bottom_activate_button = QPushButton("Activar licencia")
            self.bottom_activate_button.clicked.connect(self.ask_for_license)
            layout.addWidget(self.bottom_activate_button)

            # Label de estado de licencia
            self.license_status_label = QLabel()
            layout.addWidget(self.license_status_label)

            # Label de periodo de prueba
            self.trial_status_label = QLabel()
            layout.addWidget(self.trial_status_label)

            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

            # Dictionary for active VPNs
            self.active_vpns = {}

            # Load connections after menu is initialized
            self.load_connections()

            # Check for updates
            self.check_for_updates()

            # Ask for sudo password at startup
            self.sudo_password = self.ask_sudo_password()

            # Initialize license system
            self.initialize_license_system()

        except Exception as e:
            logging.error(f"Error initializing MainWindow: {e}")

    def initialize_license_system(self):
        """Initialize license and trial system"""
        try:
            # Verificar licencia al iniciar la aplicación
            serial = LicenseStorage.get_serial()
            email = LicenseStorage.get_email()
            
            if serial and email and LicenseManager.validate_license_key(email, serial):
                if LicenseStorage.is_license_valid():
                    self.premium_enabled = True
                else:
                    self.premium_enabled = False
                    QMessageBox.warning(self, "Licencia expirada", "Tu licencia ha expirado. Por favor, renueva para seguir usando la aplicación.")
            else:
                self.premium_enabled = False
                if serial or email:
                    QMessageBox.warning(self, "Licencia inválida", "El email y/o la clave de licencia guardados no son válidos. Por favor, revisa tus datos o activa una nueva licencia.")

            # Comprobar período de prueba
            if not serial:
                if not LicenseStorage.get_trial_start():
                    LicenseStorage.start_trial()
                    
                if LicenseStorage.is_trial_valid():
                    self.premium_enabled = True  # Durante la prueba está habilitado
                else:
                    if not self.premium_enabled:  # Solo si no hay licencia válida
                        self.premium_enabled = False

            self.update_license_status_label()
            self.update_trial_status_label()
            self.update_connect_buttons_state()
            
        except Exception as e:
            logging.error(f"Error initializing license system: {e}")

    def is_package_installed_by_manager(self, package, system):
        """Comprueba si el paquete está instalado por brew o apt según el sistema operativo"""
        try:
            if system == "darwin":
                # Comprobar con brew
                result = subprocess.run(["brew", "list", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return result.returncode == 0
            elif system == "linux":
                # Comprobar con dpkg (apt)
                result = subprocess.run(["dpkg", "-l", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return result.returncode == 0
            else:
                return False
        except Exception as e:
            logging.error(f"Error comprobando el gestor de paquetes para {package}: {e}")
            return False

    def show_library_check_progress(self):
        """Muestra un diálogo de progreso mientras se comprueban las librerías necesarias"""
        progress_dialog = QProgressDialog(
            "Comprobando librerías necesarias...", None, 0, 100, self
        )
        progress_dialog.setWindowTitle("Por favor, espere")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setValue(0)
        progress_dialog.show()
        QApplication.processEvents()

        try:
            # Detectar sistema operativo
            system = platform.system().lower()
            required_libraries = {
                "openvpn": ["openvpn"],
                "strongswan": ["strongswan", "ipsec"]
            }
            step = 100 // len(required_libraries)
            current_progress = 0

            for lib, executables in required_libraries.items():
                progress_dialog.setLabelText(f"Verificando {lib}...")
                QApplication.processEvents()

                if not self.is_library_installed_crossplatform(executables):
                    # Comprobar si está instalado por el gestor de paquetes
                    if self.is_package_installed_by_manager(lib, system):
                        logging.info(f"{lib} ya está instalado por el gestor de paquetes.")
                    else:
                        logging.warning(f"{lib} no encontrado. Intentando instalar...")
                        progress_dialog.setLabelText(f"Instalando {lib}...")
                        QApplication.processEvents()
                        if system == "linux":
                            self.install_library(f"sudo apt-get update && sudo apt-get install -y {lib}")
                        elif system == "darwin":
                            self.install_library(f"brew install {lib}")
                        else:
                            QMessageBox.critical(self, "Error", f"Sistema operativo no soportado para instalar {lib} automáticamente.")

                current_progress += step
                progress_dialog.setValue(current_progress)
                QApplication.processEvents()

            progress_dialog.setValue(100)
            progress_dialog.close()
        except Exception as e:
            logging.error(f"Error checking required libraries: {e}")
            progress_dialog.close()
            QMessageBox.critical(
                self,
                "Error",
                f"Error al verificar las librerías necesarias: {e}"
            )

    def is_library_installed_crossplatform(self, executables):
        """Comprueba si alguno de los ejecutables existe en el sistema (Linux/macOS)"""
        try:
            for exe in executables:
                # Buscar en el PATH
                if subprocess.call(["which", exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                    logging.info(f"Librería encontrada: {exe}")
                    return True
            logging.warning(f"Librería no encontrada: {executables}")
            return False
        except Exception as e:
            logging.error(f"Error checking executables: {e}")
            return False

    def install_library(self, install_cmd):
        """Install a library using the provided command"""
        try:
            subprocess.run(install_cmd.split(), check=True)
            logging.info(f"Librería instalada correctamente con el comando: {install_cmd}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error al instalar la librería: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo instalar la librería necesaria.\nComando: {install_cmd}\nError: {e}"
            )

    def add_item_to_list(self, option_name, config_path, username, password, connection_type=VPNType.OPENVPN.value, extra_data=None):
        try:
            # Create a custom widget for the row
            row_widget = QWidget()
            row_layout = QVBoxLayout()

            # Delete button
            delete_button = QPushButton()
            delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
            delete_button.clicked.connect(lambda: self.delete_item_from_list(row_widget))

            # Edit button
            edit_button = QPushButton()
            edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            edit_button.clicked.connect(lambda: self.open_edit_window(option_name, config_path, username, password))

            # Label with the option name
            label = QLabel(option_name)

            # Label with the username
            user_label = QLabel(f"Usuario: {username}")

            # Masked password label
            masked_password = self.mask_password(password)
            password_label = QLabel(f"Contraseña: {masked_password}")

            # Connect button with native system icon
            connect_button = QPushButton(ConnectionState.DISCONNECTED.value)
            connect_button.setObjectName("Conectar")
            connect_button.setStyleSheet("background-color: #98FB98; border-radius: 5px;")
            connect_button.setProperty("config_path", config_path)
            connect_button.setProperty("username", username)
            connect_button.setProperty("password", password)
            connect_button.setProperty("connection_type", connection_type)
            if extra_data:
                connect_button.setProperty("extra_data", extra_data)

            # Create observer for this button
            connect_button.observer = ConnectionObserver(connect_button, self.tray_icon)

            # Button action
            connect_button.clicked.connect(lambda: self.toggle_vpn(connect_button, config_path, username, password, connection_type, extra_data))

            # Horizontal layout for buttons
            button_layout = QHBoxLayout()
            button_layout.addWidget(delete_button)
            button_layout.addWidget(edit_button)
            button_layout.addWidget(connect_button)

            # Add widgets to the row layout
            row_layout.addWidget(label)
            row_layout.addWidget(user_label)
            row_layout.addWidget(password_label)
            row_layout.addLayout(button_layout)
            row_layout.setContentsMargins(10, 10, 10, 10)
            row_widget.setLayout(row_layout)

            # Create a list item and add the widget as its content
            list_item = QListWidgetItem()
            list_item.setSizeHint(row_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, row_widget)
            self.update_connections_menu()
        except Exception as e:
            logging.error(f"Error adding item to list: {e}")

    def mask_password(self, password):
        """Mask password showing only first and last 4 characters"""
        if len(password) <= 8:
            return password  # If password is too short, return as is
        return password[:4] + '*' * (len(password) - 8) + password[-4:]

    def toggle_vpn(self, button, config_path, username, password, connection_type=VPNType.OPENVPN.value, extra_data=None):
        # Check license/trial before allowing connection
        if not self.check_license_access():
            return
            
        logging.info(f"[toggle_vpn] Botón pulsado. Estado actual: {button.text()}, config_path: {config_path}, username: {username}, tipo: {connection_type}, extra_data: {extra_data}")
        if button.text() == ConnectionState.DISCONNECTED.value:
            # Mostrar mensaje informativo antes de conectar
            QMessageBox.information(
                self, 
                "Información de Conexión", 
                "La conexión no siempre se establece a la primera.\n\nPor favor, tenga paciencia durante el proceso de conexión."
            )
            
            button.observer.set_state(ConnectionState.CONNECTING)
            logging.info(f"[toggle_vpn] Estado cambiado a CONNECTING")
            def connect_func():
                logging.info(f"[toggle_vpn] Iniciando connect_func para tipo: {connection_type}")
                if connection_type == 'ipsec':
                    logging.info(f"[toggle_vpn] Llamando a connect_ipsec")
                    self.connect_ipsec(config_path, username, password, extra_data)
                    return True
                else:
                    logging.info(f"[toggle_vpn] Llamando a connect_openvpn")
                    return self.connect_openvpn(config_path, username, password, self.sudo_password)
            self.vpn_thread = VPNConnectThread(connect_func)
            self.vpn_thread.result.connect(lambda ok, msg: self._on_vpn_connect_result(button, config_path, username, connection_type, ok, msg))
            logging.info(f"[toggle_vpn] Lanzando hilo VPNConnectThread")
            self.vpn_thread.start()
        else:
            button.observer.set_state(ConnectionState.DISCONNECTING)
            logging.info(f"[toggle_vpn] Estado cambiado a DISCONNECTING. Llamando a disconnect_openvpn")
            self.disconnect_openvpn(config_path)
            button.observer.set_state(ConnectionState.DISCONNECTED)
            self.update_connections_menu()
            logging.info(f"[toggle_vpn] Estado cambiado a DISCONNECTED y menú actualizado")

    def check_license_access(self):
        """Check if user has valid license or trial access"""
        serial = LicenseStorage.get_serial()
        email = LicenseStorage.get_email()
        
        # Check valid license
        if serial and email and LicenseManager.validate_license_key(email, serial):
            if LicenseStorage.is_license_valid():
                return True
            else:
                QMessageBox.warning(self, "Licencia expirada", "Tu licencia ha expirado. Por favor, renueva para seguir usando la aplicación.")
                return False
        
        # Check trial
        if LicenseStorage.is_trial_valid():
            return True
        
        # No access
        QMessageBox.warning(self, "Acceso denegado", "Tu período de prueba ha terminado y no tienes una licencia válida. Por favor, activa una licencia para continuar.")
        return False

    def _on_vpn_connect_result(self, button, config_path, username, connection_type, ok, msg):
        logging.info(f"[_on_vpn_connect_result] Resultado: ok={ok}, msg={msg}")
        if ok:
            button.observer.set_state(ConnectionState.CONNECTED)
            self.active_vpns[config_path] = {
                'type': connection_type,
                'username': username,
                'process': None
            }
            QMessageBox.information(self, "VPN conectada", "¡La conexión VPN se ha establecido correctamente!")
        else:
            button.observer.set_state(ConnectionState.DISCONNECTED)
            QMessageBox.critical(self, "Error", f"No se pudo establecer la conexión VPN.\n{msg}")
        self.update_connections_menu()
        logging.info(f"[_on_vpn_connect_result] Estado final del botón: {button.text()}")

    def connect_openvpn(self, config_path, username, password, sudo_password):
        try:
            logging.info(f"[connect_openvpn] Iniciando conexión para {config_path} con usuario {username}")
            # Create a temporary file for credentials
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
                temp.write(f"{username}\n{password}")
                auth_file = temp.name

            # Prepare OpenVPN command
            cmd = [
                'sudo', '-S',
                'openvpn',
                '--script-security', '2',
                '--config', config_path,
                '--auth-user-pass', auth_file,
                '--auth-nocache',
                '--log', 'openvpn_runtime.log'
            ]

            logging.info(f"[connect_openvpn] Ejecutando comando: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            process.stdin.write(f"{sudo_password}\n")
            process.stdin.flush()

            import time
            connected = False
            log_path = 'openvpn_runtime.log'
            
            # Limpiar log anterior si existe
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                    logging.info(f"[connect_openvpn] Log anterior eliminado")
                except Exception:
                    pass
            
            # Esperar más tiempo en la primera conexión (120 segundos)
            max_attempts = 120
            logging.info(f"[connect_openvpn] Esperando conexión (máximo {max_attempts} segundos)...")
            
            for attempt in range(max_attempts):
                if os.path.exists(log_path):
                    try:
                        cat_cmd = ['sudo', '-S', 'cat', log_path]
                        cat_proc = subprocess.Popen(cat_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                        cat_proc.stdin.write(f"{sudo_password}\n")
                        cat_proc.stdin.flush()
                        log_content, _ = cat_proc.communicate(timeout=10)
                        
                        for line in log_content.splitlines():
                            logging.info(f"[openvpn-log] {line.strip()}")
                            if "Initialization Sequence Completed" in line:
                                connected = True
                                logging.info(f"[connect_openvpn] ¡Conexión exitosa detectada en intento {attempt + 1}!")
                                break
                            # Detectar errores comunes
                            elif "AUTH_FAILED" in line:
                                logging.error(f"[connect_openvpn] Error de autenticación detectado")
                                break
                            elif "RESOLVE: Cannot resolve host address" in line:
                                logging.error(f"[connect_openvpn] Error de resolución DNS detectado")
                                break
                    except Exception as e:
                        logging.warning(f"[connect_openvpn] Error leyendo log en intento {attempt + 1}: {e}")
                
                if connected:
                    break
                    
                # Mostrar progreso cada 10 segundos
                if (attempt + 1) % 10 == 0:
                    logging.info(f"[connect_openvpn] Esperando conexión... {attempt + 1}/{max_attempts} segundos")
                
                time.sleep(1)
            os.unlink(auth_file)
            if connected:
                # Esperar un poco más y verificar múltiples veces que el proceso sigue vivo
                logging.info(f"[connect_openvpn] Verificando estabilidad de la conexión...")
                stable_connection = True
                
                for check in range(3):  # Verificar 3 veces con intervalos
                    time.sleep(2)  # Esperar 2 segundos entre verificaciones
                    if process.poll() is not None:
                        logging.error(f"[connect_openvpn] Proceso OpenVPN terminó en verificación {check + 1}")
                        stable_connection = False
                        break
                    logging.info(f"[connect_openvpn] Verificación {check + 1}/3: Proceso activo")
                
                if stable_connection:
                    logging.info(f"[connect_openvpn] Conexión estable confirmada. ¡Éxito!")
                    return True
                else:
                    logging.error(f"[connect_openvpn] Conexión inestable, proceso terminó prematuramente")
                    return False
            else:
                logging.error(f"[connect_openvpn] No se detectó 'Initialization Sequence Completed' después de {max_attempts} segundos")
                # Verificar si hay errores específicos en el log
                if os.path.exists(log_path):
                    try:
                        cat_cmd = ['sudo', '-S', 'cat', log_path]
                        cat_proc = subprocess.Popen(cat_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                        cat_proc.stdin.write(f"{sudo_password}\n")
                        cat_proc.stdin.flush()
                        log_content, _ = cat_proc.communicate(timeout=10)
                        logging.error(f"[connect_openvpn] Últimas líneas del log:\n{log_content[-500:]}")  # Últimos 500 caracteres
                    except Exception as e:
                        logging.error(f"[connect_openvpn] Error leyendo log final: {e}")
                return False
        except Exception as e:
            logging.error(f"Error connecting OpenVPN: {e}")
            raise

    def connect_ipsec(self, server, username, password, extra_data):
        """Connect to IPSec VPN"""
        try:
            logging.info(f"[connect_ipsec] Iniciando conexión IPSec a {server}")
            
            shared_secret = extra_data.get('shared_secret', '')
            
            # Here you would implement the actual IPSec connection logic
            # For now, we'll simulate a connection
            import time
            time.sleep(2)  # Simulate connection time
            
            logging.info(f"[connect_ipsec] Conexión IPSec simulada exitosa")
            return True
            
        except Exception as e:
            logging.error(f"Error connecting IPSec: {e}")
            raise

    def disconnect_openvpn(self, config_path):
        try:
            # First try to terminate the stored process
            if config_path in self.active_vpns:
                process = self.active_vpns[config_path].get('process')
                if process:
                    logging.info(f"Terminating OpenVPN process for {config_path}")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        logging.warning("Had to force kill OpenVPN process")
                
                # Remove from active VPNs
                del self.active_vpns[config_path]
                logging.info(f"Removed {config_path} from active VPNs")

            # Kill any remaining OpenVPN processes using sudo
            logging.info("Killing any remaining OpenVPN processes")
            try:
                # Get sudo password
                sudo_password = self.get_sudo_password()
                if not sudo_password:
                    raise Exception("No sudo password provided")

                kill_cmd = ['sudo', '-S', 'pkill', 'openvpn']
                process = subprocess.Popen(
                    kill_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Send sudo password
                process.stdin.write(f"{sudo_password}\n")
                process.stdin.flush()
                
                # Wait for the command to complete
                process.wait(timeout=5)
                
                logging.info(f"OpenVPN connection terminated for {config_path}")
                return True

            except subprocess.TimeoutExpired:
                logging.error("Timeout while trying to kill OpenVPN processes")
                raise
            except Exception as e:
                logging.error(f"Error killing OpenVPN processes: {e}")
                raise

        except Exception as e:
            logging.error(f"Error disconnecting OpenVPN: {e}")
            raise

    def open_configure_window(self):
        try:
            dialog = ConfigureDialog(self)
            if dialog.exec_():
                if hasattr(dialog, 'ipsec_config'):
                    # IPSec configuration
                    self.add_ipsec_connection(dialog.ipsec_config)
                else:
                    # OpenVPN configuration
                    selected_name = dialog.get_selected_name()
                    selected_file = dialog.get_selected_file()
                    username = dialog.get_username()
                    password = dialog.get_password()
                    if selected_name and selected_file and username and password:
                        self.add_item_to_list(selected_name, selected_file, username, password)
                        self.save_connections()
        except Exception as e:
            logging.error(f"Error opening configure window: {e}")
    
    def save_connections(self):
        """Save both OpenVPN and IPsec connections to JSON"""
        try:
            connections = []
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                widget = self.list_widget.itemWidget(item)
                label = widget.findChild(QLabel)
                connect_button = widget.findChild(QPushButton, "Conectar")
                
                # Get common properties
                config_path = connect_button.property("config_path")
                username = connect_button.property("username")
                password = connect_button.property("password")
                connection_type = connect_button.property("connection_type")
                extra_data = connect_button.property("extra_data")
                sudo_password = connect_button.property("sudo_password")
                
                # Create connection dict based on type
                if connection_type == 'ipsec':
                    connection = {
                        "name": label.text(),
                        "server": config_path,
                        "username": username,
                        "password": password,
                        "type": "ipsec",
                        "shared_secret": extra_data.get('shared_secret') if extra_data else None,
                        "sudo_password": sudo_password
                    }
                else:
                    connection = {
                        "name": label.text(),
                        "config_path": config_path,
                        "username": username,
                        "password": password,
                        "type": "openvpn",
                        "sudo_password": sudo_password
                    }
                connections.append(connection)
            
            with open("connections.json", "w") as file:
                json.dump(connections, file)
            self.update_connections_menu()
        except Exception as e:
            logging.error(f"Error saving connections: {e}")

    def load_connections(self):
        """Cargar las conexiones desde un archivo JSON"""
        try:
            with open("connections.json", "r") as file:
                connections = json.load(file)
                for connection in connections:
                    if connection.get('type') == 'ipsec':
                        # Verificar campos requeridos para IPsec
                        required_keys = ["name", "server", "shared_secret", "username", "password", "type"]
                        if all(key in connection for key in required_keys):
                            self.add_item_to_list(
                                connection["name"],
                                connection["server"],  # Usar server como config_path
                                connection["username"],
                                connection["password"],
                                connection_type='ipsec',
                                extra_data={
                                    'shared_secret': connection['shared_secret'],
                                    'server': connection['server']
                                }
                            )
                        else:
                            print(f"Advertencia: Conexión IPsec inválida: {connection}")
                    else:
                        # OpenVPN connection
                        required_keys = ["name", "config_path", "username", "password"]
                        if all(key in connection for key in required_keys):
                            self.add_item_to_list(
                                connection["name"],
                                connection["config_path"],
                                connection["username"],
                                connection["password"],
                                connection_type='openvpn'
                            )
                        else:
                            print(f"Advertencia: Conexión OpenVPN inválida: {connection}")
        except FileNotFoundError:
            logging.warning("Connections file not found.")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding connections.json: {e}")
        except Exception as e:
            logging.error(f"Error loading connections: {e}")

    def delete_item_from_list(self, row_widget):
        try:
            # Eliminar el elemento de la lista
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                if self.list_widget.itemWidget(item) == row_widget:
                    self.list_widget.takeItem(index)
                    self.save_connections()  # Guardar conexiones después de eliminar
                    break
            self.update_connections_menu()  # Update menu after deleting
        except Exception as e:
            logging.error(f"Error deleting item from list: {e}")

    def open_edit_window(self, option_name, config_path, username, password):
        try:
            # Crear una nueva ventana de edición
            dialog = EditDialog(self, option_name, config_path, username, password)
            if dialog.exec_():  # Si se cierra con "Aceptar"
                new_name = dialog.get_selected_name()
                new_file = dialog.get_selected_file()
                new_username = dialog.get_username()
                new_password = dialog.get_password()
                if new_name and new_file and new_username and new_password:
                    self.update_item_in_list(option_name, new_name, new_file, new_username, new_password)  # Actualizar la lista
                    self.save_connections()  # Guardar conexiones
        except Exception as e:
            logging.error(f"Error opening edit window: {e}")

    def update_item_in_list(self, old_name, new_name, new_file, new_username, new_password):
        try:
            # Actualizar el elemento en la lista
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                widget = self.list_widget.itemWidget(item)
                label = widget.findChild(QLabel)
                if label.text() == old_name:
                    label.setText(new_name)
                    button = widget.findChild(QPushButton, "Conectar")
                    button.setProperty("config_path", new_file)
                    button.setProperty("username", new_username)
                    button.setProperty("password", new_password)
                    break
        except Exception as e:
            logging.error(f"Error updating item in list: {e}")

    def ask_sudo_password(self):
        dialog = SudoPasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_password()
        else:
            QMessageBox.critical(self, "Error", "Se requiere la contraseña de administrador para ejecutar la aplicación.")
            sys.exit(1)

    def get_sudo_password(self):
        try:
            # Crear un diálogo más informativo para la contraseña sudo
            dialog = QDialog(self)
            dialog.setWindowTitle("Autenticación requerida")  # Título más descriptivo
            layout = QVBoxLayout()
            
            # Mensaje más descriptivo e informativo
            label = QLabel("Se necesita clave sudo para seguir")
            label.setWordWrap(True)  # Permite que el texto se ajuste al ancho del diálogo
            
            password_input = QLineEdit()
            password_input.setEchoMode(QLineEdit.Password)
            password_input.setPlaceholderText("Introduzca su contraseña")  # Texto de ayuda
            
            button = QPushButton("Aceptar")
            button.clicked.connect(dialog.accept)
            
            layout.addWidget(label)
            layout.addWidget(password_input)
            layout.addWidget(button)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                return password_input.text()
            return ""
        except Exception as e:
            logging.error(f"Error getting sudo password: {e}")

    def add_ipsec_connection(self, config):
        try:
            # Add IPSec connection to the list
            self.add_item_to_list(
                config['name'],
                config['server'],  # Using server as config_path for IPSec
                config['username'],
                config['password'],
                connection_type='ipsec',
                extra_data={
                    'shared_secret': config['shared_secret'],
                    'server': config['server']
                }
            )
            self.save_connections()
        except Exception as e:
            logging.error(f"Error adding IPSec connection: {e}")

    def update_connections_menu(self):
        """Update the connections submenu in the tray icon"""
        try:
            self.connections_menu.clear()
            
            with open("connections.json", "r") as file:
                connections = json.load(file)
                    
            # Create submenus with platform-specific lock icons
            if platform.system() == 'Darwin':
                # Use different lock states for macOS
                openvpn_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
                ipsec_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
                connected_icon = self.style().standardIcon(QStyle.SP_DialogOkButton)  # Unlocked state
                disconnected_icon = self.style().standardIcon(QStyle.SP_MessageBoxCritical)  # Locked state
            else:
                # Use themed lock icons for Linux
                openvpn_icon = QIcon.fromTheme("security-high")
                ipsec_icon = QIcon.fromTheme("security-high")
                connected_icon = QIcon.fromTheme("security-medium")  # Unlocked/connected
                disconnected_icon = QIcon.fromTheme("security-low")  # Locked/disconnected
            
            openvpn_menu = self.connections_menu.addMenu("OpenVPN")
            openvpn_menu.setIcon(openvpn_icon)
            
            ipsec_menu = self.connections_menu.addMenu("IPsec")
            ipsec_menu.setIcon(ipsec_icon)
            
            active_connection = None
            
            # Update main tray icon for macOS with lock icon
            if platform.system() == 'Darwin':
                main_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)  # Lock icon
                pixmap = main_icon.pixmap(16, 16)
                self.tray_icon.setIcon(QIcon(pixmap))
            
            # Add connections to appropriate submenus
            for connection in connections:
                connection_type = connection.get('type', 'openvpn')
                target_menu = ipsec_menu if connection_type == 'ipsec' else openvpn_menu
                
                # Create action for the connection
                action = target_menu.addAction(connection['name'])
                action.setData(connection)
                
                # Check if connection is active
                config_path = connection.get('server' if connection_type == 'ipsec' else 'config_path')
                is_connected = config_path in self.active_vpns
                
                # Set icon and state based on connection status
                if is_connected:
                    # Añadir tick visual al texto del nombre
                    action.setText(f"{connection['name']}  ✓")
                    action.setEnabled(True)
                    active_connection = connection
                else:
                    action.setText(connection['name'])
                    action.setEnabled(True)
                    action.setIcon(disconnected_icon)
                
                # Connect action to toggle VPN
                action.triggered.connect(
                    lambda checked, conn=connection: self.toggle_vpn_from_menu(conn)
                )
            
            # Update main tray icon based on active connection
            if active_connection:
                self.tray_icon.setIcon(connected_icon)
                self.tray_icon.setToolTip(f"VPN Conectada: {active_connection['name']}")
            else:
                self.tray_icon.setIcon(disconnected_icon)
                self.tray_icon.setToolTip("VPN Desconectada")
            
            # Hide empty submenus
            openvpn_menu.menuAction().setVisible(bool(openvpn_menu.actions()))
            ipsec_menu.menuAction().setVisible(bool(ipsec_menu.actions()))
                
        except FileNotFoundError:
            action = self.connections_menu.addAction("No hay conexiones guardadas")
            # Use warning lock icon
            warning_icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning) if platform.system() == 'Darwin' else QIcon.fromTheme("security-low")
            action.setIcon(warning_icon)
            action.setEnabled(False)
        except Exception as e:
            logging.error(f"Error updating connections menu: {e}")

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def handle_tray_activation_macos(self, reason):
        """Special handler for macOS tray icon clicks"""
        if reason == QSystemTrayIcon.Trigger:  # Single click in macOS
            self.tray_icon.contextMenu().popup(QCursor.pos())
        elif reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def toggle_vpn_from_menu(self, connection):
        """Handle VPN connection from tray menu"""
        try:
            # Check license/trial before allowing connection
            if not self.check_license_access():
                return
                
            # Find the corresponding button in the list
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                widget = self.list_widget.itemWidget(item)
                label = widget.findChild(QLabel)
                connect_button = widget.findChild(QPushButton, "Conectar")
                
                if label and label.text() == connection['name']:
                    # Simulate button click using existing toggle_vpn method
                    config_path = connection.get('server' if connection['type'] == 'ipsec' else 'config_path')
                    extra_data = {
                        'shared_secret': connection.get('shared_secret'),
                        'server': connection.get('server')
                    } if connection['type'] == 'ipsec' else None
                    
                    self.toggle_vpn(
                        connect_button,
                        config_path,
                        connection['username'],
                        connection['password'],
                        connection['type'],
                        extra_data
                    )
                    break
        except Exception as e:
            logging.error(f"Error toggling VPN from menu: {e}")

    def is_autostart_enabled(self):
        """Check if application is set to autostart"""
        autostart_file = Path.home() / '.config/autostart/vpn-app.desktop'
        return autostart_file.exists()

    def toggle_autostart(self, checked):
        """Enable or disable autostart"""
        try:
            autostart_dir = Path.home() / '.config/autostart'
            autostart_file = autostart_dir / 'vpn-app.desktop'
            
            if checked:
                # Create autostart directory if it doesn't exist
                autostart_dir.mkdir(parents=True, exist_ok=True)
                
                # Create desktop entry
                entry_content = [
                    "[Desktop Entry]",
                    "Type=Application",
                    "Name=VPN App",
                    "Exec=" + sys.argv[0],
                    "Terminal=false",
                    "Hidden=false",
                    "X-GNOME-Autostart-enabled=true"
                ]
                
                # Write desktop entry file
                with open(autostart_file, 'w') as f:
                    f.write('\n'.join(entry_content))
                
                # Set proper permissions
                autostart_file.chmod(0o755)
            else:
                # Remove desktop entry if it exists
                if autostart_file.exists():
                    autostart_file.unlink()
        except Exception as e:
            logging.error(f"Error toggling autostart: {e}")

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            if platform.system() == 'Darwin':
                # En macOS, ocultar la ventana en lugar de cerrarla
                self.hide()
                event.ignore()
            elif self.tray_icon.isVisible():
                self.hide()
                self.tray_icon.showMessage(
                    "VPN App",
                    "La aplicación continúa ejecutándose en segundo plano",
                    self.style().standardIcon(QStyle.SP_FileDialogDetailedView) if platform.system() == 'Darwin' else QIcon.fromTheme("security-high"),
                    2000
                )
                event.ignore()
        except Exception as e:
            logging.error(f"Error handling close event: {e}")

    def check_for_updates(self):
        """Check for updates on GitHub"""
        try:
            repo = "alumno109192/vpn"  # Tu repositorio original
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            headers = {"User-Agent": "VPN-App"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                latest_version = response.json().get("tag_name", "").lstrip("v")
                current_version = "1.0.0"  # Versión actual de la aplicación
                if self.is_newer_version(latest_version, current_version):
                    self.notify_update_available(latest_version)
            elif response.status_code == 404:
                logging.info("No releases found on GitHub.")
            else:
                logging.warning(f"GitHub API error: {response.status_code}")
        except Exception as e:
            logging.error(f"Error checking for updates: {e}")

    def is_newer_version(self, latest_version, current_version):
        """Compare version strings"""
        try:
            latest = [int(x) for x in latest_version.split(".")]
            current = [int(x) for x in current_version.split(".")]
            return latest > current
        except:
            return False

    def notify_update_available(self, latest_version):
        """Notify the user about an available update"""
        try:
            QMessageBox.information(
                self,
                "Actualización Disponible",
                f"Una nueva versión ({latest_version}) está disponible.\n"
                "Por favor, actualice la aplicación."
            )
        except Exception as e:
            logging.error(f"Error notifying update: {e}")

    # License system methods
    def ask_for_license(self):
        """Open license activation dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        
        class LicenseDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Activar licencia")
                layout = QVBoxLayout()
                layout.addWidget(QLabel("Para activar la licencia debes realizar el pago por PayPal a: yesod3d@gmail.com"))
                layout.addWidget(QLabel("Introduce tu email de licencia:"))
                self.email_input = QLineEdit()
                layout.addWidget(self.email_input)
                layout.addWidget(QLabel("Introduce tu clave de licencia:"))
                self.license_input = QLineEdit()
                layout.addWidget(self.license_input)
                layout.addWidget(QLabel("La licencia tiene un coste de 5€ por 30 días de uso."))
                self.ok_button = QPushButton("Activar")
                self.ok_button.clicked.connect(self.accept)
                layout.addWidget(self.ok_button)
                self.setLayout(layout)
                
            def get_data(self):
                return self.email_input.text().strip(), self.license_input.text().strip()
        
        dialog = LicenseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            email, key = dialog.get_data()
            if LicenseManager.validate_license_key(email, key):
                LicenseStorage.activate_license(email=email, serial=key)
                self.license_email, self.license_key = email, key
                self.premium_enabled = True
                self.update_license_status_label()
                self.update_trial_status_label()
                self.update_connect_buttons_state()
                QMessageBox.information(self, "Licencia activada", "¡Licencia válida y email guardados correctamente!\nLa licencia es válida por 30 días.")
            else:
                self.premium_enabled = False
                self.update_license_status_label()
                self.update_trial_status_label()
                self.update_connect_buttons_state()
                QMessageBox.critical(self, "Licencia inválida", "El serial no corresponde con el email.")
        else:
            self.premium_enabled = False
            self.update_license_status_label()
            self.update_trial_status_label()
            self.update_connect_buttons_state()

    def update_connect_buttons_state(self):
        """Enable/disable connect buttons based on license status"""
        serial = LicenseStorage.get_serial()
        email = LicenseStorage.get_email()
        licencia_valida = serial and email and LicenseManager.validate_license_key(email, serial) and LicenseStorage.is_license_valid()
        prueba_valida = LicenseStorage.is_trial_valid()
        enable = licencia_valida or prueba_valida
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget:
                connect_button = widget.findChild(QPushButton, "Conectar")
                if connect_button:
                    connect_button.setEnabled(enable)

    def update_license_status_label(self):
        """Update license status label"""
        serial = LicenseStorage.get_serial()
        email = LicenseStorage.get_email()
        
        if serial and email and LicenseManager.validate_license_key(email, serial):
            if LicenseStorage.is_license_valid():
                try:
                    start_date = datetime.datetime.fromisoformat(LicenseStorage.get_license_start())
                    dias_restantes = LicenseStorage.LICENSE_DAYS - (datetime.datetime.now() - start_date).days
                    self.license_status_label.setText(f"Licencia: ACTIVADA ✅ ({dias_restantes} días restantes)")
                    self.license_status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.trial_status_label.hide()
                except:
                    self.license_status_label.setText("Licencia: ACTIVADA ✅")
                    self.license_status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.trial_status_label.hide()
            else:
                self.license_status_label.setText("Licencia expirada. Renueva para seguir usando la app.")
                self.license_status_label.setStyleSheet("color: orange; font-weight: bold;")
                self.trial_status_label.show()
        else:
            self.license_status_label.setText("Licencia: NO ACTIVADA ❌")
            self.license_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.trial_status_label.show()

    def update_trial_status_label(self):
        """Update trial status label"""
        # Ocultar si la licencia está activada
        serial = LicenseStorage.get_serial()
        email = LicenseStorage.get_email()
        if serial and email and LicenseManager.validate_license_key(email, serial) and LicenseStorage.is_license_valid():
            self.trial_status_label.setText("")
            self.trial_status_label.hide()
            return
            
        # Mostrar días restantes de prueba
        trial_days = LicenseStorage.TRIAL_DAYS
        data = LicenseStorage.load()
        if data and data.get('trial_start'):
            try:
                start = datetime.datetime.fromisoformat(data['trial_start'])
                now = datetime.datetime.now()
                used = (now - start).days
                left = max(0, trial_days - used)
                if left > 0:
                    self.trial_status_label.setText(f"Periodo de prueba: {left} días restantes")
                    self.trial_status_label.setStyleSheet("color: orange; font-weight: bold;")
                    self.trial_status_label.show()
                else:
                    self.trial_status_label.setText("Periodo de prueba finalizado")
                    self.trial_status_label.setStyleSheet("color: red; font-weight: bold;")
                    self.trial_status_label.show()
            except Exception:
                self.trial_status_label.setText("Error en periodo de prueba")
                self.trial_status_label.show()
        else:
            self.trial_status_label.setText("")
            self.trial_status_label.hide()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Critical error in main: {e}")
