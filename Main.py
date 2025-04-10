import sys
import subprocess
import json
import pexpect
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QFileDialog, QDialog, QLineEdit,
    QTabWidget, QSystemTrayIcon, QMenu, QStyle, QMessageBox  # Add QStyle, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QCursor  # Add QCursor
import platform
from enum import Enum
import os
from pathlib import Path

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
        # Update button text and style
        self.button.setText(self.state.value)
        
        if platform.system() == 'Darwin':
            # Use system icons for macOS
            if self.state == ConnectionState.DISCONNECTED:
                icon = self.button.style().standardIcon(QStyle.SP_DialogApplyButton)
                tray_icon = self.button.style().standardIcon(QStyle.SP_ComputerIcon)
            elif self.state == ConnectionState.CONNECTING:
                icon = self.button.style().standardIcon(QStyle.SP_BrowserReload)
                tray_icon = self.button.style().standardIcon(QStyle.SP_BrowserReload)
            elif self.state == ConnectionState.AUTHENTICATING:
                icon = self.button.style().standardIcon(QStyle.SP_DialogApplyButton)
                tray_icon = self.button.style().standardIcon(QStyle.SP_DialogApplyButton)
            else:  # CONNECTED
                icon = self.button.style().standardIcon(QStyle.SP_DialogCancelButton)
                tray_icon = self.button.style().standardIcon(QStyle.SP_DialogApplyButton)
                
            # Convert to QPixmap and scale for menu bar
            tray_pixmap = tray_icon.pixmap(16, 16)
            self.tray_icon.setIcon(QIcon(tray_pixmap))
            self.button.setIcon(icon)
        else:
            # Original icon logic for other platforms
            if self.state == ConnectionState.DISCONNECTED:
                self.button.setStyleSheet("background-color: #98FB98; border-radius: 5px;")
                self.button.setIcon(QIcon.fromTheme("network-vpn"))
                self.tray_icon.setIcon(QIcon.fromTheme("network-vpn"))
                self.tray_icon.setToolTip("VPN Desconectada")
            elif self.state == ConnectionState.CONNECTING:
                self.button.setStyleSheet("background-color: #FFD700; border-radius: 5px;")
                self.button.setIcon(QIcon.fromTheme("network-transmit"))
                self.tray_icon.setIcon(QIcon.fromTheme("network-transmit"))
                self.tray_icon.setToolTip("Conectando VPN...")
            elif self.state == ConnectionState.AUTHENTICATING:
                self.button.setStyleSheet("background-color: #FFD700; border-radius: 5px;")
                self.button.setIcon(QIcon.fromTheme("dialog-password"))
                self.tray_icon.setIcon(QIcon.fromTheme("dialog-password"))
                self.tray_icon.setToolTip("Autenticando VPN...")
            else:  # CONNECTED
                self.button.setStyleSheet("background-color: #FF7F7F; border-radius: 5px;")
                self.button.setIcon(QIcon.fromTheme("network-transmit-receive"))
                self.tray_icon.setIcon(QIcon.fromTheme("network-transmit-receive"))
                self.tray_icon.setToolTip("VPN Conectada")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz Gráfica con Botones en la Lista")
        self.setGeometry(100, 100, 500, 400)

        # Check and install OpenVPN if needed
        self.check_and_install_openvpn()

        # Initialize tray menu and icon
        self.tray_menu = QMenu()
        
        if platform.system() == 'Darwin':
            # Use macOS system icon that works well in dark/light mode
            icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
            # Convert to QPixmap and scale specifically for macOS menu bar
            pixmap = icon.pixmap(16, 16)  # macOS menu bar icons work best at 16x16
            self.tray_icon = QSystemTrayIcon(QIcon(pixmap), self)
            
            # Set icon size policy for better macOS display
            self.tray_icon.setToolTip("VPN App")
        else:
            # Original icon for other platforms
            self.tray_icon = QSystemTrayIcon(QIcon.fromTheme("network-vpn"), self)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
        # Handle tray icon clicks for macOS specifically
        if platform.system() == 'Darwin':
            self.tray_icon.activated.connect(self.handle_tray_activation_macos)
        else:
            self.tray_icon.activated.connect(self.tray_icon_activated)

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
        
    def check_and_install_openvpn(self):
        """Check if OpenVPN is installed and install it if needed"""
        progress_dialog = QMessageBox(self)
        progress_dialog.setIcon(QMessageBox.Information)
        progress_dialog.setWindowTitle("Instalación de Requisitos")
        progress_dialog.setText("Comprobando requisitos...")
        progress_dialog.setStandardButtons(QMessageBox.NoButton)
        progress_dialog.show()
        QApplication.processEvents()

        try:
            # Update PATH with Homebrew locations
            homebrew_paths = [
                '/opt/homebrew/bin',      # M1/M2 Macs
                '/usr/local/bin',         # Intel Macs
                '/opt/homebrew/sbin',     # Additional M1/M2 paths
                '/usr/local/sbin'         # Additional Intel paths
            ]
            
            # Add Homebrew paths to PATH
            os.environ['PATH'] = ':'.join(homebrew_paths + [os.environ.get('PATH', '')])
            
            # Check if OpenVPN is already installed
            try:
                openvpn_path = subprocess.check_output(['which', 'openvpn']).decode().strip()
                print(f"DEBUG: OpenVPN found at {openvpn_path}")
                progress_dialog.hide()
                return True
            except subprocess.CalledProcessError:
                print("DEBUG: OpenVPN not found, installing...")
                progress_dialog.setText("Instalando OpenVPN...")
                QApplication.processEvents()

                try:
                    # Update Homebrew first
                    subprocess.run(['brew', 'update'], check=True)
                    
                    # Install OpenVPN
                    subprocess.run(['brew', 'install', 'openvpn'], check=True)
                    
                    # Verify installation
                    openvpn_path = subprocess.check_output(['which', 'openvpn']).decode().strip()
                    if openvpn_path:
                        print(f"DEBUG: OpenVPN installed successfully at {openvpn_path}")
                        progress_dialog.hide()
                        return True
                    else:
                        raise Exception("OpenVPN installation verified but binary not found")

                except Exception as e:
                    print(f"ERROR: Failed to install OpenVPN: {e}")
                    progress_dialog.hide()
                    self.show_error_dialog(
                        "Error",
                        f"No se pudo instalar OpenVPN. Error: {str(e)}\n\n"
                        "Por favor, instálelo manualmente usando:\nbrew install openvpn"
                    )
                    return False

        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            progress_dialog.hide()
            self.show_error_dialog(
                "Error",
                f"Error inesperado: {str(e)}"
            )
            return False
        finally:
            if progress_dialog:
                progress_dialog.hide()

    def show_error_dialog(self, title, message):
        """Show error dialog with custom title and message"""
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()

    def add_item_to_list(self, option_name, config_path, username, password, connection_type='openvpn', extra_data=None):
        # Crear un widget personalizado para la fila
        row_widget = QWidget()
        row_layout = QVBoxLayout()  # Cambiar a QVBoxLayout para mostrar elementos en vertical

        # Botón "Eliminar"
        delete_button = QPushButton()
        delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_button.clicked.connect(lambda: self.delete_item_from_list(row_widget))

        # Botón "Editar"
        edit_button = QPushButton()
        edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        edit_button.clicked.connect(lambda: self.open_edit_window(option_name, config_path, username, password))

        # Etiqueta con el nombre de la opción
        label = QLabel(option_name)

        # Etiqueta con el usuario
        user_label = QLabel(f"Usuario: {username}")

        # Etiqueta con la contraseña enmascarada
        masked_password = self.mask_password(password)
        password_label = QLabel(f"Contraseña: {masked_password}")

        # Botón "Conectar" con icono nativo del sistema
        connect_button = QPushButton(ConnectionState.DISCONNECTED.value)
        connect_button.setObjectName("Conectar")
        connect_button.setStyleSheet("background-color: #98FB98; border-radius: 5px;")
        
        # Usar iconos nativos del sistema
        if platform.system() == 'Darwin':  # macOS
            connect_icon = self.style().standardIcon(QStyle.SP_CommandLink)
        elif platform.system() == 'Windows':
            connect_icon = self.style().standardIcon(QStyle.SP_DriveNetIcon)
        else:  # Linux
            connect_icon = self.style().standardIcon(QStyle.SP_DriveNetIcon)
        
        connect_button.setIcon(connect_icon)
        
        connect_button.setProperty("config_path", config_path)
        connect_button.setProperty("username", username)
        connect_button.setProperty("password", password)
        connect_button.setProperty("connection_type", connection_type)
        if extra_data:
            connect_button.setProperty("extra_data", extra_data)
        
        # Create observer for this button
        connect_button.observer = ConnectionObserver(connect_button, self.tray_icon)

        # Acción del botón
        connect_button.clicked.connect(lambda: self.toggle_vpn(connect_button, config_path, username, password, connection_type, extra_data))

        # Layout horizontal para los botones
        button_layout = QHBoxLayout()
        button_layout.addWidget(delete_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(connect_button)

        # Añadir widgets al layout de la fila
        row_layout.addWidget(label)
        row_layout.addWidget(user_label)
        row_layout.addWidget(password_label)
        row_layout.addLayout(button_layout)
        row_layout.setContentsMargins(10, 10, 10, 10)  # Ajustar márgenes
        row_widget.setLayout(row_layout)

        # Crear un elemento de lista y añadir el widget como contenido
        list_item = QListWidgetItem()
        list_item.setSizeHint(row_widget.sizeHint())  # Ajustar tamaño del elemento
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, row_widget)
        self.update_connections_menu()  # Update menu after adding item

    def mask_password(self, password):
        """Mask password showing only first and last 4 characters"""
        if len(password) <= 8:
            return password  # If password is too short, return as is
        return password[:4] + '*' * (len(password) - 8) + password[-4:]

    def toggle_vpn(self, button, config_path, username, password, connection_type='openvpn', extra_data=None):
        if not button:
            print("DEBUG: Error - Invalid button object")
            return

        if not hasattr(button, 'observer'):
            print("DEBUG: Creating new observer for button")
            button.observer = ConnectionObserver(button, self.tray_icon)

        # Obtener la contraseña sudo del archivo connections.json
        try:
            with open("connections.json", "r") as file:
                connections = json.load(file)
                sudo_password = None
                # Buscar la conexión correspondiente
                for connection in connections:
                    if (connection.get('config_path') == config_path or 
                        connection.get('server') == config_path):
                        sudo_password = connection.get('sudo_password')
                        break
                
                if not sudo_password:
                    print("DEBUG: No se encontró la contraseña sudo en connections.json")
                    # Si no existe, pedirla una vez y guardarla
                    sudo_password = self.get_sudo_password()
                    if sudo_password:
                        # Actualizar el archivo connections.json con la nueva contraseña sudo
                        for connection in connections:
                            if (connection.get('config_path') == config_path or 
                                connection.get('server') == config_path):
                                connection['sudo_password'] = sudo_password
                                break
                        with open("connections.json", "w") as f:
                            json.dump(connections, f)
                    else:
                        print("DEBUG: No se proporcionó contraseña sudo")
                        button.observer.set_state(ConnectionState.DISCONNECTED)
                        return
        except Exception as e:
            print(f"DEBUG: Error al leer/escribir connections.json: {str(e)}")
            button.observer.set_state(ConnectionState.DISCONNECTED)
            return

        # Resto del código de toggle_vpn con la contraseña sudo obtenida...
        if button.observer.state != ConnectionState.CONNECTED:
            try:
                print(f"DEBUG: Initiating connection with config: {config_path}")
                button.observer.set_state(ConnectionState.CONNECTING)
                self.update_connections_menu()

                if connection_type == 'openvpn':
                    # Get full path to OpenVPN
                    try:
                        openvpn_path = subprocess.check_output(['which', 'openvpn']).decode().strip()
                        print(f"DEBUG: Using OpenVPN at {openvpn_path}")
                    except subprocess.CalledProcessError:
                        print("DEBUG: OpenVPN not found")
                        if not self.check_and_install_openvpn():
                            button.observer.set_state(ConnectionState.DISCONNECTED)
                            return
                        try:
                            openvpn_path = subprocess.check_output(['which', 'openvpn']).decode().strip()
                        except subprocess.CalledProcessError:
                            print("DEBUG: OpenVPN still not found after installation")
                            button.observer.set_state(ConnectionState.DISCONNECTED)
                            return

                    # Create temporary auth file
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as auth_file:
                        auth_file.write(f"{username}\n{password}")
                        auth_file_path = auth_file.name
                        print(f"DEBUG: Created auth file at: {auth_file_path}")

                    try:
                        command = [
                            "sudo", "-S",
                            openvpn_path,
                            "--config", config_path,
                            "--auth-user-pass", auth_file_path,
                            "--verb", "4"
                        ]
                        
                        print(f"DEBUG: Executing command: {' '.join(command)}")
                        # Añadir justo antes de ejecutar el comando OpenVPN
                        try:
                            with open(config_path, 'r') as f:
                                print(f"DEBUG: Config file is readable")
                                config_content = f.read()
                                print("DEBUG: Config file content:")
                                print(config_content)
                        except Exception as e:
                            print(f"DEBUG: Error reading config file: {e}")
                            button.observer.set_state(ConnectionState.DISCONNECTED)
                            return

                        # Obtener la ruta completa de OpenVPN
                        openvpn_path = subprocess.check_output(['which', 'openvpn']).decode().strip()
                        
                        command = [
                            "sudo", "-S",
                            openvpn_path,  # Usar la ruta completa
                            "--config", config_path,
                            "--auth-user-pass", auth_file_path,
                            "--verb", "4"  # Aumentar el nivel de verbosidad
                        ]
                        
                        print(f"DEBUG: Executing command: {' '.join(command)}")
                        
                        process = subprocess.Popen(
                            command,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True,
                            bufsize=1
                        )
                        
                        # Enviar la contraseña sudo
                        process.stdin.write(f"{sudo_password}\n")
                        process.stdin.flush()
                        
                        print("DEBUG: Process started with PID:", process.pid)

                        # Monitor process output with timeout
                        import select
                        import time
                        
                        timeout = 30  # 30 segundos de timeout
                        start_time = time.time()
                        
                        while True:
                            # Check if process has ended
                            if process.poll() is not None:
                                print(f"DEBUG: Process ended with return code: {process.poll()}")
                                # Leer cualquier error final
                                stderr_output = process.stderr.read()
                                if stderr_output:
                                    print(f"ERROR: {stderr_output}")
                                break
                            
                            # Check for timeout
                            if time.time() - start_time > timeout:
                                print("DEBUG: Connection timeout")
                                process.terminate()
                                break
                            
                            # Check for output
                            reads = [process.stdout.fileno(), process.stderr.fileno()]
                            ret = select.select(reads, [], [], 0.5)
                            
                            for fd in ret[0]:
                                if fd == process.stdout.fileno():
                                    line = process.stdout.readline()
                                    if line:
                                        print(f"OpenVPN: {line.strip()}")
                                        # Detect connection states
                                        if "Attempting to establish TCP connection" in line:
                                            print("DEBUG: State - Connecting")
                                            button.observer.set_state(ConnectionState.CONNECTING)
                                        elif "PENDING" in line:
                                            print("DEBUG: State - Authenticating")
                                            button.observer.set_state(ConnectionState.AUTHENTICATING)
                                        elif "Initialization Sequence Completed" in line:
                                            print("DEBUG: State - Connected")
                                            self.active_vpns[config_path] = process
                                            button.observer.set_state(ConnectionState.CONNECTED)
                                            return
                                elif fd == process.stderr.fileno():
                                    error = process.stderr.readline()
                                    if error:
                                        print(f"ERROR: {error.strip()}")
                                        if "permission denied" in error.lower():
                                            print("DEBUG: Sudo permission denied")
                                            button.observer.set_state(ConnectionState.DISCONNECTED)
                                            return
                        
                    except Exception as e:
                        print(f"DEBUG: Error during process execution: {str(e)}")
                        button.observer.set_state(ConnectionState.DISCONNECTED)
                        raise
                        
                    finally:
                        # Clean up auth file
                        try:
                            os.unlink(auth_file_path)
                            print("DEBUG: Auth file cleaned up")
                        except Exception as e:
                            print(f"DEBUG: Error cleaning up auth file: {str(e)}")

                elif connection_type == 'ipsec':
                    print("DEBUG: IPsec connection not implemented yet")
                    pass

            except Exception as e:
                print(f"DEBUG: Critical error in toggle_vpn: {str(e)}")
                button.observer.set_state(ConnectionState.DISCONNECTED)
                self.update_connections_menu()

        else:  # Disconnection
            try:
                print("DEBUG: Initiating disconnection")
                process = self.active_vpns.get(config_path)
                if process:
                    print(f"DEBUG: Found active VPN process for {config_path}")
                    if connection_type == 'openvpn':
                        try:
                            sudo_password = self.get_sudo_password()
                            if sudo_password:
                                # Usar echo para proporcionar la contraseña sudo
                                subprocess.run(
                                    f'echo {sudo_password} | sudo -S killall openvpn',
                                    shell=True,
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE
                                )
                                print("DEBUG: OpenVPN processes killed")
                            
                            process.terminate()
                            try:
                                process.wait(timeout=3)
                            except subprocess.TimeoutExpired:
                                process.kill()
                            
                            process.stdout.close()
                            process.stderr.close()
                            
                        except Exception as e:
                            print(f"DEBUG: Error during process termination: {str(e)}")
                        
                        del self.active_vpns[config_path]
                        print("DEBUG: Removed from active VPNs")
                    
                    button.observer.set_state(ConnectionState.DISCONNECTED)
                    self.update_connections_menu()
                    print("DEBUG: Disconnection complete")
            except Exception as e:
                print(f"DEBUG: Error during disconnection: {str(e)}")

    def open_configure_window(self):
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
    
    def save_connections(self):
        """Save both OpenVPN and IPsec connections to JSON"""
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
            print("No se encontró el archivo de conexiones.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")
        except Exception as e:
            print(f"Error al cargar las conexiones: {str(e)}")

    def delete_item_from_list(self, row_widget):
        # Eliminar el elemento de la lista
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if self.list_widget.itemWidget(item) == row_widget:
                self.list_widget.takeItem(index)
                self.save_connections()  # Guardar conexiones después de eliminar
                break
        self.update_connections_menu()  # Update menu after deleting

    def open_edit_window(self, option_name, config_path, username, password):
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

    def update_item_in_list(self, old_name, new_name, new_file, new_username, new_password):
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


    def get_sudo_password(self):
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

    def add_ipsec_connection(self, config):
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

    def update_connections_menu(self):
        """Update the connections submenu in the tray icon"""
        self.connections_menu.clear()
        
        try:
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
            print(f"Error al actualizar el menú: {str(e)}")

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

    def is_autostart_enabled(self):
        """Check if application is set to autostart"""
        autostart_file = Path.home() / '.config/autostart/vpn-app.desktop'
        return autostart_file.exists()

    def toggle_autostart(self, checked):
        """Enable or disable autostart"""
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

    def closeEvent(self, event):
        """Handle window close event"""
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

class ConfigureDialog(QDialog):
    def __init__(self, parent=None):
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

    def setup_openvpn_tab(self):
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

    def setup_ipsec_tab(self):
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

    def save_ipsec(self):
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

    def open_file_explorer(self):
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

    def open_file_explorer(self):
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

    def get_selected_file(self):
        return self.selected_file

    def get_selected_name(self):
        return self.name_input.text().strip()

    def get_username(self):
        return self.username_input.text().strip()

    def get_password(self):
        return self.password_input.text().strip()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
