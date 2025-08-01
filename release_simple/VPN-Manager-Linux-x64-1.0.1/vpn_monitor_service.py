#!/usr/bin/env python3

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal


class VPNMonitorService(QThread):
    """Servicio para monitorear el estado de las conexiones VPN activas"""
    connection_lost = pyqtSignal(str, str, str, str, str, object)  # config_path, username, password, connection_type, extra_data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.monitoring = True
        self.check_interval = 10  # Verificar cada 10 segundos
        
    def run(self):
        """Monitorear las conexiones activas"""
        while self.monitoring:
            if self.parent_window and hasattr(self.parent_window, 'active_vpns'):
                self.check_active_connections()
            time.sleep(self.check_interval)
    
    def check_active_connections(self):
        """Verificar el estado de todas las conexiones activas"""
        try:
            connections_to_remove = []
            for config_path, vpn_info in self.parent_window.active_vpns.items():
                if not self.is_connection_active(config_path, vpn_info['type']):
                    logging.warning(f"[VPNMonitor] Conexión perdida detectada: {config_path}")
                    
                    # Esperar un poco antes de confirmar la desconexión para evitar falsos positivos
                    time.sleep(3)
                    
                    # Verificar nuevamente
                    if not self.is_connection_active(config_path, vpn_info['type']):
                        logging.error(f"[VPNMonitor] Desconexión confirmada: {config_path}")
                        # Buscar los datos de la conexión para reconectar
                        connection_data = self.find_connection_data(config_path)
                        if connection_data:
                            self.connection_lost.emit(
                                config_path,
                                connection_data['username'],
                                connection_data['password'],
                                connection_data['type'],
                                connection_data.get('extra_data')
                            )
                        connections_to_remove.append(config_path)
                    else:
                        logging.info(f"[VPNMonitor] Falsa alarma, conexión activa: {config_path}")
            
            # Remover conexiones perdidas del diccionario
            for config_path in connections_to_remove:
                if config_path in self.parent_window.active_vpns:
                    del self.parent_window.active_vpns[config_path]
                    
        except Exception as e:
            logging.error(f"[VPNMonitor] Error checking connections: {e}")
    
    def is_connection_active(self, config_path, connection_type):
        """Verificar si una conexión específica está activa"""
        try:
            if connection_type == 'openvpn':
                # Método 1: Verificar procesos OpenVPN activos con el archivo de configuración
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                if result.returncode == 0 and config_path in result.stdout:
                    # Verificar también el log de OpenVPN para asegurar que está conectado
                    log_path = 'openvpn_runtime.log'
                    if os.path.exists(log_path):
                        try:
                            with open(log_path, 'r') as f:
                                log_content = f.read()
                                # Si hay un "Initialization Sequence Completed" reciente y no hay errores críticos
                                if "Initialization Sequence Completed" in log_content:
                                    # Verificar que no haya errores recientes
                                    lines = log_content.split('\n')
                                    recent_lines = lines[-20:]  # Últimas 20 líneas
                                    for line in recent_lines:
                                        if any(error in line for error in ["SIGTERM", "process exiting", "AUTH_FAILED", "Connection reset"]):
                                            return False
                                    return True
                        except Exception as e:
                            logging.warning(f"[VPNMonitor] Error reading OpenVPN log: {e}")
                
                # Método 2: Verificar interfaz de red VPN (tun/tap)
                try:
                    result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
                    if result.returncode == 0:
                        # Buscar interfaces tun o tap activas
                        for line in result.stdout.split('\n'):
                            if ('tun' in line or 'tap' in line) and 'UP' in line:
                                return True
                except Exception as e:
                    logging.warning(f"[VPNMonitor] Error checking network interfaces: {e}")
                
                return False
            elif connection_type == 'ipsec':
                # Para IPSec, verificar el estado de la conexión
                try:
                    result = subprocess.run(['ipsec', 'status'], capture_output=True, text=True)
                    return result.returncode == 0 and 'ESTABLISHED' in result.stdout
                except Exception:
                    return True  # Placeholder por ahora
            return False
        except Exception as e:
            logging.error(f"[VPNMonitor] Error checking connection status: {e}")
            return False
    
    def find_connection_data(self, config_path):
        """Buscar los datos de una conexión específica"""
        try:
            import os
            import sys
            
            # Obtener directorio de configuración
            def get_config_dir():
                config_dir = os.path.expanduser("~/.config/vpn-manager")
                if sys.platform == "win32":
                    config_dir = os.path.join(os.environ.get("APPDATA", ""), "VPN Manager")
                os.makedirs(config_dir, exist_ok=True)
                return config_dir
            
            connections_file = os.path.join(get_config_dir(), "connections.json")
            with open(connections_file, "r") as file:
                connections = json.load(file)
                if isinstance(connections, dict):
                    connections = [connections]
                
                for connection in connections:
                    connection_path = connection.get('server' if connection.get('type') == 'ipsec' else 'config_path')
                    if connection_path == config_path:
                        extra_data = None
                        if connection.get('type') == 'ipsec':
                            extra_data = {
                                'shared_secret': connection.get('shared_secret'),
                                'server': connection.get('server')
                            }
                        return {
                            'username': connection['username'],
                            'password': connection['password'],
                            'type': connection.get('type', 'openvpn'),
                            'extra_data': extra_data
                        }
        except Exception as e:
            logging.error(f"[VPNMonitor] Error finding connection data: {e}")
        return None
    
    def stop_monitoring(self):
        """Detener el monitoreo"""
        self.monitoring = False
        logging.info("[VPNMonitor] Servicio de monitoreo detenido")


class AutoReconnectService:
    """Servicio para manejar la reconexión automática de VPN"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.enabled = True
        logging.info("[AutoReconnect] Servicio de reconexión automática inicializado")
    
    def set_enabled(self, enabled):
        """Habilitar o deshabilitar la reconexión automática"""
        self.enabled = enabled
        status = "habilitada" if enabled else "deshabilitada"
        logging.info(f"[AutoReconnect] Reconexión automática {status}")
    
    def is_enabled(self):
        """Verificar si la reconexión automática está habilitada"""
        return self.enabled
    
    def handle_connection_lost(self, config_path, username, password, connection_type, extra_data):
        """Manejar cuando se pierde una conexión VPN"""
        try:
            if not self.enabled:
                logging.info(f"[AutoReconnect] Reconexión automática deshabilitada para: {config_path}")
                return
                
            logging.warning(f"[AutoReconnect] Intentando reconectar: {config_path}")
            
            # Buscar el botón correspondiente y actualizarlo
            button = self._find_connection_button(config_path)
            if button:
                from models import ConnectionState
                button.observer.set_state(ConnectionState.CONNECTING)
                logging.info(f"[AutoReconnect] Reconectando automáticamente: {config_path}")
                
                # Crear función de reconexión
                def reconnect_func():
                    if connection_type == 'ipsec':
                        return self.main_window.connect_ipsec(config_path, username, password, extra_data)
                    else:
                        return self.main_window.connect_openvpn(config_path, username, password, self.main_window.sudo_password)
                
                # Lanzar hilo de reconexión
                from threads.vpn_thread import VPNConnectThread
                self.main_window.reconnect_thread = VPNConnectThread(reconnect_func)
                self.main_window.reconnect_thread.result.connect(
                    lambda ok, msg: self._on_reconnect_result(button, config_path, username, connection_type, ok, msg)
                )
                self.main_window.reconnect_thread.start()
        except Exception as e:
            logging.error(f"[AutoReconnect] Error handling connection lost: {e}")
    
    def _find_connection_button(self, config_path):
        """Encontrar el botón correspondiente a una conexión específica"""
        try:
            from PyQt5.QtWidgets import QPushButton
            for index in range(self.main_window.list_widget.count()):
                item = self.main_window.list_widget.item(index)
                widget = self.main_window.list_widget.itemWidget(item)
                if widget:
                    connect_button = widget.findChild(QPushButton, "Conectar")
                    if connect_button and connect_button.property("config_path") == config_path:
                        return connect_button
        except Exception as e:
            logging.error(f"[AutoReconnect] Error finding connection button: {e}")
        return None
    
    def _on_reconnect_result(self, button, config_path, username, connection_type, ok, msg):
        """Manejar el resultado de la reconexión automática"""
        try:
            from models import ConnectionState
            from PyQt5.QtWidgets import QSystemTrayIcon
            
            if ok:
                button.observer.set_state(ConnectionState.CONNECTED)
                self.main_window.active_vpns[config_path] = {'type': connection_type, 'username': username, 'process': None}
                logging.info(f"[AutoReconnect] Reconexión exitosa: {config_path}")
                
                # Mostrar notificación de reconexión exitosa
                if hasattr(self.main_window, 'tray_icon') and self.main_window.tray_icon.isVisible():
                    self.main_window.tray_icon.showMessage(
                        "VPN Reconectada",
                        f"Conexión automáticamente restablecida",
                        QSystemTrayIcon.Information,
                        3000
                    )
            else:
                button.observer.set_state(ConnectionState.DISCONNECTED)
                logging.error(f"[AutoReconnect] Falló la reconexión: {config_path} - {msg}")
                
                # Mostrar notificación de fallo en reconexión
                if hasattr(self.main_window, 'tray_icon') and self.main_window.tray_icon.isVisible():
                    self.main_window.tray_icon.showMessage(
                        "Error de Reconexión",
                        f"No se pudo restablecer la conexión automáticamente",
                        QSystemTrayIcon.Warning,
                        3000
                    )
            
            self.main_window.update_connections_menu()
        except Exception as e:
            logging.error(f"[AutoReconnect] Error handling reconnect result: {e}")
