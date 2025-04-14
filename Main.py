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
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("network-vpn"), self)
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
            layout.addWidget(self.configure_button)
            layout.addWidget(self.list_widget)

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

    def show_library_check_progress(self):
        """Show a progress dialog while checking for required libraries"""
        progress_dialog = QProgressDialog(
            "Comprobando librerías necesarias...", None, 0, 100, self
        )
        progress_dialog.setWindowTitle("Por favor, espere")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setValue(0)
        progress_dialog.show()
        QApplication.processEvents()

        try:
            required_libraries = {
                "openvpn": ["openvpn", "/usr/local/opt/openvpn/sbin/openvpn", "/opt/homebrew/opt/openvpn/sbin/openvpn"],
                "strongswan": ["strongswan", "/usr/local/opt/strongswan/bin/charon-cmd", "/opt/homebrew/opt/strongswan/bin/charon-cmd"]
            }

            step = 100 // len(required_libraries)
            current_progress = 0

            for lib, paths in required_libraries.items():
                progress_dialog.setLabelText(f"Verificando {lib}...")
                QApplication.processEvents()

                if not self.is_library_installed(paths):
                    logging.warning(f"{lib} no encontrado. Intentando instalar...")
                    progress_dialog.setLabelText(f"Instalando {lib}...")
                    QApplication.processEvents()
                    self.install_library(f"brew install {lib}")

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

    def is_library_installed(self, paths):
        """Check if a library is installed by searching in multiple paths"""
        try:
            for path in paths:
                if os.path.isfile(path) and os.access(path, os.X_OK):
                    logging.info(f"Librería encontrada en: {path}")
                    return True
            logging.warning(f"Librería no encontrada en las rutas: {paths}")
            return False
        except Exception as e:
            logging.error(f"Error checking library paths: {e}")
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
        try:
            if not button:
                logging.error("Invalid button object")
                return

            if not hasattr(button, 'observer'):
                logging.info("Creating new observer for button")
                button.observer = ConnectionObserver(button, self.tray_icon)

            # Handle connection or disconnection
            if button.observer.state != ConnectionState.CONNECTED:
                logging.info(f"Connecting VPN: {config_path}")
                button.observer.set_state(ConnectionState.CONNECTING)
                self.update_connections_menu()

                # Get sudo password if needed
                sudo_password = self.get_sudo_password()
                if not sudo_password:
                    button.observer.set_state(ConnectionState.DISCONNECTED)
                    return

                try:
                    if connection_type == 'ipsec':
                        self.connect_ipsec(config_path, username, password, extra_data, sudo_password)
                    else:
                        self.connect_openvpn(config_path, username, password, sudo_password)
                    
                    # Store active VPN connection
                    self.active_vpns[config_path] = {
                        'type': connection_type,
                        'username': username,
                        'process': None  # Will be set by connect methods
                    }
                    
                    button.observer.set_state(ConnectionState.CONNECTED)
                    
                except Exception as e:
                    logging.error(f"Failed to connect VPN: {e}")
                    button.observer.set_state(ConnectionState.DISCONNECTED)
                    QMessageBox.critical(self, "Error", f"Failed to connect VPN: {e}")
                    
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
                    QMessageBox.critical(self, "Error", f"Failed to disconnect VPN: {e}")
                
            self.update_connections_menu()
        except Exception as e:
            logging.error(f"Error in toggle_vpn: {e}")

    def connect_openvpn(self, config_path, username, password, sudo_password):
        try:
            # Create a temporary file for credentials
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
                temp.write(f"{username}\n{password}")
                auth_file = temp.name

            # Prepare OpenVPN command
            cmd = [
                'sudo', '-S',
                'openvpn',
                '--config', config_path,
                '--auth-user-pass', auth_file,
                '--daemon'
            ]

            # Start OpenVPN process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Send sudo password
            process.stdin.write(f"{sudo_password}\n")
            process.stdin.flush()

            # Store process reference
            if config_path in self.active_vpns:
                self.active_vpns[config_path]['process'] = process

            # Clean up credentials file
            os.unlink(auth_file)

            logging.info(f"OpenVPN connection started for {config_path}")
            return True

        except Exception as e:
            logging.error(f"Error connecting OpenVPN: {e}")
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
            
            active_connection = None
            
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


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Critical error in main: {e}")
