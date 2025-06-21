import sys
import subprocess
import json
import logging
import requests
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QProgressDialog, QMessageBox, QMenu, QSystemTrayIcon, QStyle, QDialog, QLineEdit, QTabWidget, QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor
import platform
import os
from pathlib import Path
from models import VPNType, ConnectionState, ConnectionObserver  # Import models

# Configure logging
logging.basicConfig(
    filename='vpn_setup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SudoPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Contraseña de administrador requerida")
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
        return self.password_input.text()

class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.sudo_password = None
            self.ask_sudo_password()
            self.setWindowTitle("VPN Manager")
            self.setGeometry(100, 100, 500, 400)

            # Show progress dialog while checking libraries
            self.show_library_check_progress()

            # Initialize tray menu and icon
            self.tray_menu = QMenu()
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("network-vpn"), self)
            self.tray_icon.setContextMenu(self.tray_menu)
            self.tray_icon.show()

            # Add "Open" action
            open_action = self.tray_menu.addAction("Abrir")
            open_action.triggered.connect(self.show)

            # Add connections submenu
            self.connections_menu = self.tray_menu.addMenu("Conexiones")

            # Add autostart option (OCULTO)
            # self.autostart_action = self.tray_menu.addAction("Iniciar con el sistema")
            # self.autostart_action.setCheckable(True)
            # self.autostart_action.setChecked(self.is_autostart_enabled())
            # self.autostart_action.triggered.connect(self.toggle_autostart)

            # Add separator
            self.tray_menu.addSeparator()

            # Add "Exit" action
            exit_action = self.tray_menu.addAction("Salir")
            exit_action.triggered.connect(QApplication.instance().quit)

            # Configure button
            self.configure_button = QPushButton("Configurar")
            self.configure_button.clicked.connect(self.open_configure_window)
            
            # Configure button
            self.activate_button = QPushButton("Activar Licencia")

            # Botón para solicitar licencia por email
            self.request_license_button = QPushButton("Solicitar licencia por email")
            self.request_license_button.clicked.connect(self.show_request_license_dialog)

            # List widget setup
            self.list_widget = QListWidget()
            self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            # Main layout
            layout = QVBoxLayout()
            layout.addWidget(self.configure_button)
            layout.addWidget(self.list_widget)
            layout.addWidget(self.activate_button)
            layout.addWidget(self.request_license_button)

            central_widget = QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

            # Dictionary for active VPNs
            self.active_vpns = {}

            # Load connections after menu is initialized
            self.load_connections()

            # Check for updates
            self.check_for_updates()
        except Exception as e:
            logging.error(f"Error initializing MainWindow: {e}")

    def ask_sudo_password(self):
        dialog = SudoPasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.sudo_password = dialog.get_password()
        else:
            sys.exit(0)

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
                            # Solo usar sudo si no es root
                            is_root = False
                            try:
                                is_root = (os.geteuid() == 0)
                            except AttributeError:
                                pass  # os.geteuid no existe en Windows
                            sudo_prefix = "" if is_root else "sudo "
                            self.install_library(f"{sudo_prefix}apt-get update && {sudo_prefix}apt-get install -y {lib}")
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
        """Busca ejecutables en el PATH del usuario, root y rutas estándar del sistema. Guarda la ruta encontrada para cada ejecutable por separado."""
        rutas_estandar = [
            '/usr/sbin', '/usr/local/sbin', '/sbin', '/usr/bin', '/usr/local/bin', '/bin'
        ]
        if not hasattr(self, 'executables_paths'):
            self.executables_paths = {}
        try:
            for exe in executables:
                logging.info(f"Buscando '{exe}' en el PATH del usuario actual usando grep...")
                user_path = os.environ.get('PATH', '')
                for path_dir in user_path.split(":"):
                    if os.path.isdir(path_dir):
                        files = os.listdir(path_dir)
                        matches = [f for f in files if exe == f]
                        if matches:
                            ruta = os.path.join(path_dir, matches[0])
                            logging.info(f"Librería encontrada para usuario: {exe} en {ruta}")
                            self.executables_paths[exe] = ruta
                            return True
                logging.info(f"No encontrado para usuario. Buscando '{exe}' con sudo (root) usando grep...")
                grep_cmd = f"sudo sh -c 'echo $PATH'"
                result = subprocess.run(grep_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
                root_path = result.stdout.strip()
                for path_dir in root_path.split(":"):
                    if os.path.isdir(path_dir):
                        files = os.listdir(path_dir)
                        matches = [f for f in files if exe == f]
                        if matches:
                            ruta = os.path.join(path_dir, matches[0])
                            logging.info(f"Librería encontrada para root: {exe} en {ruta}")
                            self.executables_paths[exe] = ruta
                            return True
                # Buscar en rutas estándar
                logging.info(f"Buscando '{exe}' en rutas estándar del sistema...")
                for path_dir in rutas_estandar:
                    ruta = os.path.join(path_dir, exe)
                    if os.path.isfile(ruta) and os.access(ruta, os.X_OK):
                        logging.info(f"Librería encontrada en ruta estándar: {ruta}")
                        self.executables_paths[exe] = ruta
                        return True
            logging.warning(f"Librería no encontrada: {executables}")
            return False
        except Exception as e:
            logging.error(f"Error checking executables: {e}")
            return False

    def get_executable_path(self, exe_name, default='openvpn'):
        """Devuelve la ruta encontrada para el ejecutable, o el nombre por defecto si no se encontró."""
        if hasattr(self, 'executables_paths') and exe_name in self.executables_paths:
            return self.executables_paths[exe_name]
        return default

    def install_library(self, install_cmd):
        """Instala una librería usando sudo y nunca pide clave por consola."""
        try:
            # Si el comando es para apt-get, usar run_sudo_command
            if install_cmd.startswith('sudo apt-get'):
                cmd = install_cmd.replace('sudo ', '').split()
                ret, out, err = self.run_sudo_command(cmd, self.get_sudo_password())
                if ret == 0:
                    logging.info(f"Librería instalada correctamente con el comando: {install_cmd}")
                else:
                    logging.error(f"Error al instalar la librería: {err}")
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"No se pudo instalar la librería necesaria.\nComando: {install_cmd}\nError: {err}"
                    )
            else:
                # Para brew o comandos sin sudo
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

    def needs_sudo(self):
        """Devuelve True si el sistema requiere sudo para ejecutar comandos privilegiados"""
        system = platform.system().lower()
        if system == "linux":
            try:
                return os.geteuid() != 0
            except AttributeError:
                return True  # Si no se puede determinar, asumir que sí
        elif system == "darwin":
            # En macOS, normalmente se requiere sudo para openvpn/ipsec
            try:
                return os.geteuid() != 0
            except AttributeError:
                return True
        return False

    def toggle_vpn(self, button, config_path, username, password, connection_type=VPNType.OPENVPN.value, extra_data=None):
        try:
            if button.text() == ConnectionState.DISCONNECTED.value:
                logging.info(f"Connecting VPN: {config_path}")
                button.observer.set_state(ConnectionState.CONNECTING)
                self.update_connections_menu()

                sudo_password = None
                use_sudo = self.needs_sudo()
                if use_sudo:
                    sudo_password = self.get_sudo_password()
                    if not sudo_password:
                        button.observer.set_state(ConnectionState.DISCONNECTED)
                        self.update_connections_menu()
                        self.set_tray_icon_disconnected()
                        return

                try:
                    if connection_type == 'ipsec':
                        self.connect_ipsec(config_path, username, password, extra_data, sudo_password, use_sudo)
                        button.observer.set_state(ConnectionState.CONNECTED)
                    else:
                        result = self.connect_openvpn(config_path, username, password, sudo_password, use_sudo)
                        if result:
                            button.observer.set_state(ConnectionState.CONNECTED)
                            QMessageBox.information(self, "VPN conectada", "¡La conexión VPN se ha establecido correctamente!")
                        else:
                            button.observer.set_state(ConnectionState.DISCONNECTED)
                            self.set_tray_icon_disconnected()
                            self.update_connections_menu()
                            QMessageBox.critical(self, "Error", "No se pudo establecer la conexión VPN.")
                            return
                    self.active_vpns[config_path] = {
                        'type': connection_type,
                        'username': username,
                        'process': None
                    }
                except Exception as e:
                    logging.error(f"Failed to connect VPN: {e}")
                    button.observer.set_state(ConnectionState.DISCONNECTED)
                    self.set_tray_icon_disconnected()
                    self.update_connections_menu()
                    QMessageBox.critical(self, "Error", f"Failed to connect VPN: {e}")
                    return
            else:
                logging.info(f"Disconnecting VPN: {config_path}")
                button.observer.set_state(ConnectionState.DISCONNECTING)
                try:
                    if connection_type == 'ipsec':
                        self.disconnect_ipsec(config_path)
                    else:
                        self.disconnect_openvpn(config_path)
                    if config_path in self.active_vpns:
                        del self.active_vpns[config_path]
                    button.observer.set_state(ConnectionState.DISCONNECTED)
                except Exception as e:
                    logging.error(f"Failed to disconnect VPN: {e}")
                    button.observer.set_state(ConnectionState.DISCONNECTED)
                    self.set_tray_icon_disconnected()
                    self.update_connections_menu()
                    QMessageBox.critical(self, "Error", f"Failed to disconnect VPN: {e}")
            self.update_connections_menu()
        except Exception as e:
            logging.error(f"Error in toggle_vpn: {e}")
            self.set_tray_icon_disconnected()
            self.update_connections_menu()

    def set_tray_icon_disconnected(self):
        """Fuerza el icono y tooltip de la bandeja a estado desconectado."""
        if platform.system() == 'Darwin':
            disconnected_icon = self.style().standardIcon(QStyle.SP_DialogCancelButton)
        else:
            disconnected_icon = QIcon.fromTheme("network-offline")
        self.tray_icon.setIcon(disconnected_icon)
        self.tray_icon.setToolTip("VPN Desconectada")

    def connect_openvpn(self, config_path, username, password, sudo_password=None, use_sudo=True):
        try:
            logging.info(f"Iniciando conexión OpenVPN para {config_path} con usuario {username}")
            # Crear archivo temporal de credenciales
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
                temp.write(f"{username}\n{password}")
                auth_file = temp.name
            logging.info(f"Archivo temporal de credenciales creado: {auth_file}")

            # Detectar sistema operativo
            system = platform.system().lower()
            openvpn_bin = self.get_executable_path('openvpn', 'openvpn')
            cmd = []
            if use_sudo:
                cmd += ['sudo', '-S']
            cmd += [
                openvpn_bin,
                '--script-security', '2',
                '--config', config_path,
                '--auth-user-pass', auth_file,
                '--auth-nocache'
            ]
            # Nunca añadir --daemon para capturar toda la salida
            logging.info(f"Comando a ejecutar: {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE if use_sudo else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            if use_sudo and sudo_password:
                logging.info("Enviando clave sudo al proceso OpenVPN...")
                process.stdin.write(f"{sudo_password}\n")
                process.stdin.flush()

            # Esperar a que aparezca "Initialization Sequence Completed" en la salida
            connected = False
            log_lines = []
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                logging.info(f"[OpenVPN] {line.strip()}")
                log_lines.append(line.strip())
                if "Initialization Sequence Completed" in line:
                    connected = True
                    break
            os.unlink(auth_file)
            logging.info(f"Archivo temporal de credenciales eliminado: {auth_file}")

            if connected:
                logging.info(f"OpenVPN connection established for {config_path}")
                return True
            else:
                logging.error(f"OpenVPN connection failed for {config_path}")
                logging.error(f"Salida completa de OpenVPN:\n" + '\n'.join(log_lines))
                return False
        except Exception as e:
            logging.error(f"Error connecting OpenVPN: {e}")
            raise

    def disconnect_openvpn(self, config_path):
        try:
            # Intentar terminar el proceso almacenado
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

            # En Linux, buscar el proceso exacto con los argumentos usados
            system = platform.system().lower()
            use_sudo = self.needs_sudo()
            if system == 'linux':
                import shlex
                ps_cmd = f"ps aux | grep 'openvpn' | grep '{shlex.quote(config_path)}' | grep -v grep | awk '{{print $2}}'"
                p = subprocess.Popen(ps_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                pids, _ = p.communicate()
                pids = [pid.strip() for pid in pids.splitlines() if pid.strip()]
                for pid in pids:
                    kill_cmd = ['kill', '-TERM', pid]
                    if use_sudo:
                        sudo_password = self.get_sudo_password()
                        if not sudo_password:
                            raise Exception("No sudo password provided")
                        ret, out, err = self.run_sudo_command(['kill', '-TERM', pid], sudo_password)
                        if ret != 0:
                            logging.error(f"Error matando proceso OpenVPN: {err}")
                    else:
                        subprocess.run(kill_cmd, check=False)
                logging.info(f"OpenVPN process(es) with config {config_path} terminated")
            else:
                logging.info("Killing any remaining OpenVPN processes")
                if use_sudo:
                    sudo_password = self.get_sudo_password()
                    if not sudo_password:
                        raise Exception("No sudo password provided")
                    ret, out, err = self.run_sudo_command(['pkill', 'openvpn'], sudo_password)
                    if ret != 0:
                        logging.error(f"Error ejecutando pkill openvpn: {err}")
                else:
                    kill_cmd = ['pkill', 'openvpn']
                    subprocess.run(kill_cmd, check=False)
                logging.info(f"OpenVPN connection terminated for {config_path}")
            return True
        except subprocess.TimeoutExpired:
            logging.error("Timeout while trying to kill OpenVPN processes")
            raise
        except Exception as e:
            logging.error(f"Error disconnecting OpenVPN: {e}")
            raise

    def connect_ipsec(self, config_path, username, password, extra_data, sudo_password=None, use_sudo=True):
        try:
            logging.info(f"Iniciando conexión IPsec para {config_path} con usuario {username}")
            cmd = ['ipsec', 'up', config_path]
            if use_sudo:
                if not sudo_password:
                    sudo_password = self.get_sudo_password()
                ret, out, err = self.run_sudo_command(cmd, sudo_password)
                if ret != 0:
                    logging.error(f"Error conectando IPsec: {err}")
                    if 'incorrect password' in err.lower() or 'Sorry, try again.' in err or 'sudo:' in err:
                        if self.retry_sudo_password():
                            return self.connect_ipsec(config_path, username, password, extra_data, self.sudo_password, use_sudo)
                    raise Exception(f"Error conectando IPsec: {err}")
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                out, err = process.communicate()
                if process.returncode != 0:
                    logging.error(f"Error conectando IPsec: {err}")
                    raise Exception(f"Error conectando IPsec: {err}")
            logging.info(f"IPsec connection started for {config_path}")
            return True
        except Exception as e:
            logging.error(f"Error connecting IPsec: {e}")
            raise

    def disconnect_ipsec(self, config_path):
        try:
            logging.info(f"Disconnecting IPsec for {config_path}")
            cmd = ['ipsec', 'down', config_path]
            if self.needs_sudo():
                sudo_password = self.get_sudo_password()
                ret, out, err = self.run_sudo_command(cmd, sudo_password)
                if ret != 0:
                    logging.error(f"Error desconectando IPsec: {err}")
                    if 'incorrect password' in err.lower() or 'Sorry, try again.' in err or 'sudo:' in err:
                        if self.retry_sudo_password():
                            return self.disconnect_ipsec(config_path)
                    raise Exception(f"Error desconectando IPsec: {err}")
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                out, err = process.communicate()
                if process.returncode != 0:
                    logging.error(f"Error desconectando IPsec: {err}")
                    raise Exception(f"Error desconectando IPsec: {err}")
            logging.info(f"IPsec disconnected for {config_path}")
        except subprocess.TimeoutExpired:
            logging.error("Timeout while trying to disconnect IPsec")
            raise
        except Exception as e:
            logging.error(f"Error disconnecting IPsec: {e}")
            raise

    def retry_sudo_password(self):
        """Muestra un diálogo para reintentar la clave sudo si fue incorrecta. Devuelve True si el usuario reintentó y la guardó."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error de autenticación sudo")
        msg.setText("La contraseña de administrador es incorrecta o fue rechazada. ¿Desea reintentarlo?")
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        ret = msg.exec_()
        if ret == QMessageBox.Retry:
            self.ask_sudo_password()
            return True if self.sudo_password else False
        return False

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
                sudo_password = connect_button.property("sudo_password")  # Añadir esto

                # Create connection dict based on type
                if connection_type == 'ipsec':
                    connection = {
                        "name": label.text(),
                        "server": config_path,
                        "username": username,
                        "password": password,
                        "type": "ipsec",
                        "shared_secret": extra_data.get('shared_secret'),
                        "sudo_password": sudo_password  # Añadir esto
                    }
                else:
                    connection = {
                        "name": label.text(),
                        "config_path": config_path,
                        "username": username,
                        "password": password,
                        "type": "openvpn",
                        "sudo_password": sudo_password  # Añadir esto
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

    def get_sudo_password(self):
        return self.sudo_password

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
                    
            # Create submenus with platform-specific icons
            if platform.system() == 'Darwin':
                openvpn_icon = self.style().standardIcon(QStyle.SP_DriveNetIcon)
                ipsec_icon = self.style().standardIcon(QStyle.SP_DriveNetIcon)
                connected_icon = self.style().standardIcon(QStyle.SP_DialogApplyButton)
                disconnected_icon = self.style().standardIcon(QStyle.SP_DialogCancelButton)
            else:
                openvpn_icon = QIcon.fromTheme("network-vpn")
                ipsec_icon = QIcon.fromTheme("network-vpn")
                connected_icon = QIcon.fromTheme("network-transmit-receive")
                disconnected_icon = QIcon.fromTheme("network-offline")
            
            openvpn_menu = self.connections_menu.addMenu("OpenVPN")
            openvpn_menu.setIcon(openvpn_icon)
            
            ipsec_menu = self.connections_menu.addMenu("IPsec")
            ipsec_menu.setIcon(ipsec_icon)
            
            active_connection = None;
            
            # Update main tray icon for macOS
            if platform.system() == 'Darwin':
                main_icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
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
                    action.setIcon(connected_icon)
                    action.setText(connection['name'])
                    action.setEnabled(True)
                    active_connection = connection
                else:
                    action.setIcon(disconnected_icon)
                    action.setEnabled(True)
                
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
            action.setIcon(QIcon.fromTheme("dialog-warning"))
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
                    QIcon.fromTheme("network-vpn"),
                    2000
                )
                event.ignore()
        except Exception as e:
            logging.error(f"Error handling close event: {e}")

    def check_for_updates(self):
        """Check for updates on GitHub"""
        try:
            repo = "alumno109192/vpn"  # Replace with your GitHub repo
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            headers = {"User-Agent": "VPN-App"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                latest_version = response.json().get("tag_name", "").lstrip("v")
                current_version = "1.0.0"  # Replace with your current version
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
        latest = [int(x) for x in latest_version.split(".")]
        current = [int(x) for x in current_version.split(".")]
        return latest > current

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

    def run_sudo_command(self, cmd, sudo_password, **kwargs):
        """Ejecuta un comando con sudo pasando la clave por stdin y nunca por consola. Usa flags para evitar prompt y caché."""
        full_cmd = ['sudo', '-S', '-k', '-p', ''] + cmd if cmd[0] != 'sudo' else cmd
        logging.info(f"Ejecutando comando sudo: {' '.join(full_cmd)}")
        process = subprocess.Popen(
            full_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            **kwargs
        )
        try:
            out, err = process.communicate(sudo_password + '\n', timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            out, err = process.communicate()
        return process.returncode, out, err

class ConfigureDialog(QDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle("Configurar")
            self.setGeometry(150, 150, 400, 300)  # Made window taller

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
        try:
            # Abrir el explorador de archivos para seleccionar un archivo .ovpn
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar archivo .ovpn",
                "",
                "Archivos OVPN (*.ovpn);;Todos los archivos (*)",
                options=options
            )

            # Mostrar la ruta del archivo seleccionado
            if file_path:
                self.selected_file = file_path
                self.file_label.setText(f"Seleccionado: {file_path}")
        except Exception as e:
            logging.error(f"Error opening file explorer: {e}")

    def get_selected_file(self):
        return self.selected_file

    def get_selected_name(self):
        return self.name_input.text().strip()

    def get_username(self):
        return self.username_input.text().strip()

    def get_password(self):
        return self.password_input.text().strip()

class EditDialog(QDialog):
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
            self.save_button.clicked.connect(self.accept)  # Cierra el diálogo con estado "Aceptar"

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
        try:
            # Abrir el explorador de archivos para seleccionar un archivo .ovpn
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar archivo .ovpn",
                "",
                "Archivos OVPN (*.ovpn);;Todos los archivos (*)",
                options=options
            )

            # Mostrar la ruta del archivo seleccionado
            if file_path:
                self.selected_file = file_path
                self.file_label.setText(f"Seleccionado: {file_path}")
        except Exception as e:
            logging.error(f"Error opening file explorer: {e}")

    def get_selected_file(self):
        return self.selected_file

    def get_selected_name(self):
        return self.name_input.text().strip()

    def get_username(self):
        return self.username_input.text().strip()

    def get_password(self):
        return self.password_input.text().strip()

    def show_request_license_dialog(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        class RequestLicenseDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Solicitar licencia")
                layout = QVBoxLayout()
                layout.addWidget(QLabel("Introduce tu email para recibir la licencia:"))
                self.email_input = QLineEdit()
                layout.addWidget(self.email_input)
                self.send_button = QPushButton("Solicitar")
                self.send_button.clicked.connect(self.accept)
                layout.addWidget(self.send_button)
                self.setLayout(layout)
            def get_email(self):
                return self.email_input.text().strip()
        dialog = RequestLicenseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            email = dialog.get_email()
            # Aquí puedes implementar el envío real por email o solo mostrar mensaje
            QMessageBox.information(self, "Solicitud enviada", f"Se ha recibido la solicitud de licencia para: {email}\nEn breve recibirás instrucciones en tu correo.")
