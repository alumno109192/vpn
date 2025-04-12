from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QSystemTrayIcon,
    QMenu, QStyle, QApplication
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import platform

from vpn_manager import VPNManager
from config_manager import ConfigManager
from dialogs import ConfigureDialog, EditDialog
from models import ConnectionState, ConnectionObserver
from update_checker import UpdateChecker, UpdateDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VPN Manager")
        self.setGeometry(100, 100, 500, 400)
        
        self.vpn_manager = VPNManager()
        self.config_manager = ConfigManager()
        self.update_checker = UpdateChecker()
        
        # Initialize system tray
        self.setup_tray()
        
        # Set up the main UI
        self.setup_ui()
        
        # Load saved connections
        self.load_connections()
        
        # Check for updates
        self.check_for_updates()
        
        # Add close event handling
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def setup_tray(self):
        self.tray_menu = QMenu()
        self.tray_icon = QSystemTrayIcon(self)
        
        # Add menu items
        show_action = self.tray_menu.addAction("Mostrar")
        show_action.triggered.connect(self.show)
        
        # Add separator
        self.tray_menu.addSeparator()
        
        # Add connections submenu
        self.connections_menu = QMenu("Conexiones VPN")
        self.tray_menu.addMenu(self.connections_menu)
        
        # Add separator
        self.tray_menu.addSeparator()
        
        quit_action = self.tray_menu.addAction("Salir")
        quit_action.triggered.connect(self.quit_application)
        
        if platform.system() == 'Darwin':
            tray_icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        else:
            tray_icon = self.style().standardIcon(QStyle.SP_DriveNetIcon)
            
        self.tray_icon.setIcon(QIcon(tray_icon.pixmap(16, 16)))
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def update_tray_connections(self):
        """Update the connections in the tray menu"""
        self.connections_menu.clear()
        connections = self.config_manager.load_connections()
        
        if not connections:
            no_vpn_action = self.connections_menu.addAction("No hay VPNs configuradas")
            no_vpn_action.setEnabled(False)
        else:
            for conn in connections:
                vpn_action = self.connections_menu.addAction(conn['name'])
                vpn_action.setData(conn)
                vpn_action.triggered.connect(
                    lambda checked, c=conn: self.toggle_vpn_from_tray(c)
                )

    def toggle_vpn_from_tray(self, connection):
        """Toggle VPN connection from tray menu"""
        for i in range(self.vpn_list.count()):
            item = self.vpn_list.item(i)
            widget = self.vpn_list.itemWidget(item)
            if widget.findChild(QLabel).text() == connection['name']:
                connect_button = widget.findChild(QPushButton, "Conectar")
                if connect_button:
                    self.toggle_vpn(connect_button)
                break

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Add VPN button
        add_button = QPushButton("Añadir VPN")
        add_button.clicked.connect(self.show_configure_dialog)
        layout.addWidget(add_button)
        
        # VPN list
        self.vpn_list = QListWidget()
        layout.addWidget(self.vpn_list)
        
        central_widget.setLayout(layout)

    def show_configure_dialog(self):
        dialog = ConfigureDialog(self)
        if dialog.exec_():
            name = dialog.name_input.text()
            config_path = dialog.config_path_input.text()
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            
            if name and config_path and username and password:
                self.add_item_to_list(name, config_path, username, password)
                
                # Save to connections.json
                connections = self.config_manager.load_connections()
                connections.append({
                    'name': name,
                    'config_path': config_path,
                    'username': username,
                    'password': password
                })
                # Save connections with existing sudo password
                self.config_manager.save_connections(connections)
                self.update_tray_connections()

    def load_connections(self):
        connections = self.config_manager.load_connections()
        for conn in connections:
            self.add_item_to_list(
                conn['name'],
                conn['config_path'],
                conn['username'],
                conn['password']
            )
        self.update_tray_connections()  # Update tray menu after loading connections

    def mask_password(self, password):
        """Mask password showing only first and last 4 characters"""
        if len(password) <= 8:
            return password
        return password[:4] + '*' * (len(password) - 8) + password[-4:]

    def add_item_to_list(self, option_name, config_path, username, password):
        # Create row widget
        row_widget = QWidget()
        row_layout = QVBoxLayout()
        
        # Delete button
        delete_button = QPushButton()
        delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_button.clicked.connect(lambda: self.delete_item(option_name, config_path))
        
        # Edit button
        edit_button = QPushButton()
        edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        edit_button.clicked.connect(lambda: self.show_edit_dialog(option_name, config_path, username, password))
        
        # Connect button
        connect_button = QPushButton(ConnectionState.DISCONNECTED.value)
        connect_button.setObjectName("Conectar")
        connect_button.setStyleSheet("background-color: #98FB98; border-radius: 5px;")
        
        if platform.system() == 'Darwin':
            connect_icon = self.style().standardIcon(QStyle.SP_CommandLink)
        else:
            connect_icon = self.style().standardIcon(QStyle.SP_DriveNetIcon)
        
        connect_button.setIcon(connect_icon)
        connect_button.setProperty("config_path", config_path)
        connect_button.setProperty("username", username)
        connect_button.setProperty("password", password)
        
        # Create observer for this button
        connect_button.observer = ConnectionObserver(connect_button, self.tray_icon)
        connect_button.clicked.connect(lambda: self.toggle_vpn(connect_button))
        
        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(delete_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(connect_button)
        
        # Labels
        label = QLabel(option_name)
        user_label = QLabel(f"Usuario: {username}")
        password_label = QLabel(f"Contraseña: {self.mask_password(password)}")  # Add masked password
        
        row_layout.addWidget(label)
        row_layout.addWidget(user_label)
        row_layout.addWidget(password_label)  # Add password label
        row_layout.addLayout(button_layout)
        
        row_widget.setLayout(row_layout)
        
        # Add to list
        item = QListWidgetItem()
        item.setSizeHint(row_widget.sizeHint())
        self.vpn_list.addItem(item)
        self.vpn_list.setItemWidget(item, row_widget)

    def delete_item(self, option_name, config_path):
        for i in range(self.vpn_list.count()):
            item = self.vpn_list.item(i)
            widget = self.vpn_list.itemWidget(item)
            if widget.findChild(QLabel).text() == option_name:
                self.vpn_list.takeItem(i)
                break
        
        # Update connections.json
        connections = self.config_manager.load_connections()
        connections = [c for c in connections if c['config_path'] != config_path]
        self.config_manager.save_connections(connections)
        self.update_tray_connections()  # Update tray menu after deleting connection

    def show_edit_dialog(self, option_name, config_path, username, password):
        dialog = EditDialog(self, option_name, config_path, username, password)
        if dialog.exec_():
            new_name = dialog.name_input.text()
            new_config_path = dialog.config_path_input.text()
            new_username = dialog.username_input.text()
            new_password = dialog.password_input.text()
            
            if new_name and new_config_path and new_username and new_password:
                # Update list item
                self.delete_item(option_name, config_path)
                self.add_item_to_list(new_name, new_config_path, new_username, new_password)
                
                # Update connections.json
                connections = self.config_manager.load_connections()
                for conn in connections:
                    if conn['config_path'] == config_path:
                        conn.update({
                            'name': new_name,
                            'config_path': new_config_path,
                            'username': new_username,
                            'password': new_password
                        })
                        break
                self.config_manager.save_connections(connections)
                self.update_tray_connections()

    def toggle_vpn(self, button):
        config_path = button.property("config_path")
        username = button.property("username")
        password = button.property("password")
        
        if button.observer.state != ConnectionState.CONNECTED:
            sudo_password = self.config_manager.get_sudo_password()
            if sudo_password:
                self.vpn_manager.connect(button, config_path, username, password, sudo_password)
        else:
            sudo_password = self.config_manager.get_sudo_password()
            if sudo_password:
                if self.vpn_manager.disconnect(config_path, sudo_password):
                    button.observer.set_state(ConnectionState.DISCONNECTED)

    def check_for_updates(self):
        latest_version = self.update_checker.check_for_updates()
        if latest_version:
            dialog = UpdateDialog(
                self.update_checker.current_version,
                latest_version,
                self
            )
            result = dialog.exec_()
            
            if dialog.never_clicked:
                self.update_checker.save_config(never_update=True)

    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "VPN Manager",
            "La aplicación sigue ejecutándose en segundo plano",
            QSystemTrayIcon.Information,
            2000
        )

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()

    def quit_application(self):
        """Properly quit the application"""
        # Disconnect any active VPNs
        if self.vpn_manager.active_vpns:
            sudo_password = self.config_manager.get_sudo_password()
            if sudo_password:
                for config_path in list(self.vpn_manager.active_vpns.keys()):
                    self.vpn_manager.disconnect(config_path, sudo_password)
        
        self.tray_icon.hide()
        QApplication.quit()