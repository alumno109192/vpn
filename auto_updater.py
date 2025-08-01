#!/usr/bin/env python3
"""
Sistema de actualización automática para VPN Manager
"""
import hashlib
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QProgressDialog

# Importar configuración de versión
from version import get_version, GITHUB_REPO, RELEASES_API_URL

# Configurar logging para el updater en directorio de usuario
def setup_updater_logging():
    """Configurar logging para el auto-updater en directorio de usuario"""
    # Crear directorio de logs en home del usuario
    log_dir = Path.home() / '.config' / 'vpn-manager' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'vpn_updater.log'
    
    # Configurar logger
    updater_logger = logging.getLogger(__name__)
    updater_logger.setLevel(logging.INFO)
    
    # Evitar duplicar handlers
    if not updater_logger.handlers:
        # Handler para archivo
        file_handler = logging.FileHandler(str(log_file))
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        updater_logger.addHandler(file_handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s'
        ))
        updater_logger.addHandler(console_handler)
    
    return updater_logger

# Configurar logging al cargar el módulo
logger = setup_updater_logging()


class UpdaterConfig:
    """Configuración del actualizador"""
    GITHUB_REPO = GITHUB_REPO
    CURRENT_VERSION = get_version()
    UPDATE_CHECK_URL = RELEASES_API_URL
    GITHUB_API_HEADERS = {"User-Agent": "VPN-Manager-Updater"}
    
    # Archivos críticos que no se deben eliminar durante la actualización
    PRESERVE_FILES = [
        "connections.json",
        "license_storage.json", 
        "vpn_setup.log",
        ".venv",
        "__pycache__",
        "backup_update",
        "*.log"
    ]


class UpdateCheckThread(QThread):
    """Hilo para verificar actualizaciones en segundo plano"""
    update_available = pyqtSignal(dict)  # Datos de la nueva versión
    no_update = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def run(self):
        try:
            response = requests.get(
                UpdaterConfig.UPDATE_CHECK_URL,
                headers=UpdaterConfig.GITHUB_API_HEADERS,
                timeout=10
            )
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data["tag_name"].lstrip("v")
            current_version = UpdaterConfig.CURRENT_VERSION
            
            logging.info(f"Versión actual: {current_version}")
            logging.info(f"Última versión: {latest_version}")
            
            if self._is_newer_version(latest_version, current_version):
                self.update_available.emit(release_data)
            else:
                self.no_update.emit()
                
        except Exception as e:
            logging.error(f"Error checking for updates: {e}")
            self.error_occurred.emit(str(e))
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compara versiones semánticamente"""
        try:
            def version_tuple(v):
                return tuple(map(int, v.split('.')))
            
            return version_tuple(latest) > version_tuple(current)
        except ValueError:
            logging.warning(f"Error comparing versions: {latest} vs {current}")
            return False


class UpdateDownloadThread(QThread):
    """Hilo para descargar e instalar actualizaciones"""
    progress_updated = pyqtSignal(int)  # Progreso de descarga (0-100)
    status_updated = pyqtSignal(str)   # Estado actual
    download_completed = pyqtSignal(str)  # Ruta del archivo descargado
    installation_completed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, release_data: dict):
        super().__init__()
        self.release_data = release_data
        self.download_path = None
        
    def run(self):
        try:
            # Información de diagnóstico
            system_info = {
                "platform": platform.system(),
                "architecture": platform.machine(),
                "version": platform.version(),
                "python_version": sys.version
            }
            logging.info(f"Información del sistema: {system_info}")
            
            assets = self.release_data.get("assets", [])
            logging.info(f"Assets disponibles: {[asset['name'] for asset in assets]}")
            
            # 1. Determinar el asset correcto para la plataforma
            self.status_updated.emit("Analizando archivos disponibles...")
            asset_url = self._get_asset_url()
            
            if not asset_url:
                available_assets = [asset['name'] for asset in assets]
                error_msg = (
                    f"No se encontró un archivo compatible para tu sistema.\n\n"
                    f"Sistema: {platform.system()} {platform.machine()}\n"
                    f"Archivos disponibles: {', '.join(available_assets)}\n\n"
                    f"Contacta al desarrollador si necesitas soporte para tu plataforma."
                )
                self.error_occurred.emit(error_msg)
                return
            
            logging.info(f"Asset seleccionado: {asset_url}")
            
            # 2. Descargar el archivo
            self.status_updated.emit("Descargando actualización...")
            download_path = self._download_file(asset_url)
            if not download_path:
                return
                
            self.download_completed.emit(download_path)
            
            # 3. Instalar la actualización
            self.status_updated.emit("Instalando actualización...")
            if self._install_update(download_path):
                self.installation_completed.emit()
            else:
                self.error_occurred.emit("Error durante la instalación")
                
        except Exception as e:
            error_msg = f"Error durante la actualización: {str(e)}"
            logging.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)
    
    def _get_asset_url(self) -> Optional[str]:
        """Determina qué asset descargar según la plataforma con detección mejorada"""
        assets = self.release_data.get("assets", [])
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        # Normalizar arquitectura
        if arch in ['x86_64', 'amd64']:
            arch = 'x64'
        elif arch in ['i386', 'i686']:
            arch = 'x32'
        elif arch in ['aarch64', 'arm64']:
            arch = 'arm64'
        
        # Patrones de búsqueda mejorados con prioridades
        platform_patterns = {
            "darwin": {
                "primary": ["vpn-manager-macos", "macos", "darwin"],
                "secondary": ["mac", "osx"],
                "extensions": [".zip", ".dmg", ".tar.gz"]
            },
            "linux": {
                "primary": ["vpn-manager-linux", "linux"],
                "secondary": ["ubuntu", "debian", "fedora", "centos"],
                "extensions": [".tar.gz", ".deb", ".rpm", ".zip", ".AppImage"]
            },
            "windows": {
                "primary": ["vpn-manager-windows", "windows"],
                "secondary": ["win", "win32", "win64"],
                "extensions": [".zip", ".exe", ".msi"]
            }
        }
        
        patterns = platform_patterns.get(system)
        if not patterns:
            logging.warning(f"Plataforma no soportada: {system}")
            return self._find_generic_asset(assets)
        
        # Buscar con patrones primarios
        for pattern in patterns["primary"]:
            for ext in patterns["extensions"]:
                for asset in assets:
                    name = asset["name"].lower()
                    if pattern in name and name.endswith(ext):
                        logging.info(f"Asset encontrado (primario): {asset['name']}")
                        return asset["browser_download_url"]
        
        # Buscar con patrones secundarios
        for pattern in patterns["secondary"]:
            for ext in patterns["extensions"]:
                for asset in assets:
                    name = asset["name"].lower()
                    if pattern in name and name.endswith(ext):
                        logging.info(f"Asset encontrado (secundario): {asset['name']}")
                        return asset["browser_download_url"]
        
        # Buscar por extensión únicamente
        for ext in patterns["extensions"]:
            for asset in assets:
                if asset["name"].lower().endswith(ext):
                    logging.info(f"Asset encontrado (por extensión): {asset['name']}")
                    return asset["browser_download_url"]
        
        # Última opción: buscar genérico
        return self._find_generic_asset(assets)
    
    def _find_generic_asset(self, assets) -> Optional[str]:
        """Busca un asset genérico como último recurso"""
        generic_patterns = ["linux", "x64", "amd64", "universal", "all"]
        
        for pattern in generic_patterns:
            for asset in assets:
                if pattern in asset["name"].lower():
                    logging.warning(f"Usando asset genérico: {asset['name']}")
                    return asset["browser_download_url"]
        
        # Si no se encuentra nada, tomar el primer asset disponible
        if assets:
            logging.warning(f"Usando primer asset disponible: {assets[0]['name']}")
            return assets[0]["browser_download_url"]
                
        return None

    def _download_file(self, url: str) -> Optional[str]:
        """Descarga el archivo de actualización con barra de progreso"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            filename = url.split('/')[-1]
            
            # Crear directorio temporal
            temp_dir = Path(tempfile.mkdtemp(prefix="vpn_update_"))
            download_path = temp_dir / filename
            
            downloaded_size = 0
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Emitir progreso
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress_updated.emit(progress)
            
            logging.info(f"Descarga completada: {download_path}")
            return str(download_path)
            
        except Exception as e:
            logging.error(f"Error downloading file: {e}")
            self.error_occurred.emit(f"Error descargando actualización: {str(e)}")
            return None
    
    def _install_update(self, download_path: str) -> bool:
        """Instala la actualización con soporte mejorado para múltiples formatos"""
        try:
            current_dir = Path.cwd()
            file_extension = Path(download_path).suffix.lower()
            
            # Crear backup de archivos importantes
            backup_dir = self._create_backup()
            
            # Determinar método de instalación según el tipo de archivo
            if file_extension == '.zip':
                return self._install_from_zip(download_path, current_dir, backup_dir)
            elif file_extension == '.gz' and download_path.endswith('.tar.gz'):
                return self._install_from_tar_gz(download_path, current_dir, backup_dir)
            elif file_extension == '.deb':
                return self._install_from_deb(download_path)
            elif file_extension == '.rpm':
                return self._install_from_rpm(download_path)
            elif file_extension == '.dmg':
                return self._install_from_dmg(download_path, current_dir)
            elif file_extension == '.exe':
                return self._install_from_exe(download_path)
            elif file_extension == '.msi':
                return self._install_from_msi(download_path)
            elif file_extension == '.appimage':
                return self._install_from_appimage(download_path, current_dir)
            else:
                # Intentar como archivo comprimido genérico
                return self._install_generic_archive(download_path, current_dir, backup_dir)
                
        except Exception as e:
            logging.error(f"Error installing update: {e}", exc_info=True)
            self.error_occurred.emit(f"Error durante la instalación: {str(e)}")
            return False
    
    def _create_backup(self) -> Path:
        """Crea backup de archivos importantes"""
        backup_dir = Path.cwd() / "backup_update" / f"backup_{self.release_data['tag_name']}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for preserve_file in UpdaterConfig.PRESERVE_FILES:
            source = Path.cwd() / preserve_file
            if source.exists():
                if source.is_file():
                    shutil.copy2(source, backup_dir / preserve_file)
                elif source.is_dir():
                    shutil.copytree(source, backup_dir / preserve_file, dirs_exist_ok=True)
        
        return backup_dir

    def _install_from_tar_gz(self, download_path: str, current_dir: Path, backup_dir: Path) -> bool:
        """Instala desde archivo tar.gz"""
        import tarfile
        try:
            with tarfile.open(download_path, 'r:gz') as tar:
                # Extraer en directorio temporal
                temp_extract_dir = Path(tempfile.mkdtemp(prefix="vpn_extract_"))
                tar.extractall(temp_extract_dir)
                
                # Buscar la carpeta principal
                extracted_items = list(temp_extract_dir.iterdir())
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    source_dir = extracted_items[0]
                else:
                    source_dir = temp_extract_dir
                
                # Copiar archivos
                return self._copy_update_files(source_dir, current_dir, backup_dir)
        except Exception as e:
            logging.error(f"Error installing from tar.gz: {e}")
            return False

    def _copy_update_files(self, source_dir: Path, current_dir: Path, backup_dir: Path) -> bool:
        """Copia archivos de actualización de forma segura"""
        try:
            for item in source_dir.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(source_dir)
                    
                    # Saltar archivos que deben preservarse
                    if any(preserve in str(relative_path) for preserve in UpdaterConfig.PRESERVE_FILES):
                        continue
                    
                    destination = current_dir / relative_path
                    
                    # Crear directorio padre si no existe
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copiar archivo
                    shutil.copy2(item, destination)
            
            return True
        except Exception as e:
            logging.error(f"Error copying update files: {e}")
            return False

    def _install_from_zip(self, zip_path: str, current_dir: Path, backup_dir: Path) -> bool:
        """Instala desde archivo ZIP"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extraer en directorio temporal
                temp_extract_dir = Path(tempfile.mkdtemp(prefix="vpn_extract_"))
                zip_ref.extractall(temp_extract_dir)
                
                # Buscar carpeta raíz del proyecto
                project_root = self._find_project_root(temp_extract_dir)
                if not project_root:
                    project_root = temp_extract_dir
                
                # Copiar archivos
                return self._copy_update_files(project_root, current_dir, backup_dir)
                
        except Exception as e:
            logging.error(f"Error installing from ZIP: {e}")
            return False

    def _install_from_deb(self, download_path: str) -> bool:
        """Instala paquete .deb en sistemas Linux"""
        try:
            if platform.system().lower() != 'linux':
                self.error_occurred.emit("Los archivos .deb solo son compatibles con Linux")
                return False
            
            # Intentar instalación con dpkg
            result = subprocess.run(['sudo', 'dpkg', '-i', download_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                # Si falla, intentar con apt para resolver dependencias
                subprocess.run(['sudo', 'apt-get', 'install', '-f', '-y'], 
                             capture_output=True)
                return True
        except Exception as e:
            logging.error(f"Error installing .deb: {e}")
            return False

    def _install_from_rpm(self, download_path: str) -> bool:
        """Instala paquete .rpm en sistemas Linux"""
        try:
            if platform.system().lower() != 'linux':
                self.error_occurred.emit("Los archivos .rpm solo son compatibles con Linux")
                return False
            
            # Intentar con rpm
            result = subprocess.run(['sudo', 'rpm', '-i', download_path], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Error installing .rpm: {e}")
            return False

    def _install_from_dmg(self, dmg_path: str, current_dir: Path) -> bool:
        """Instala desde archivo .dmg en macOS"""
        try:
            if platform.system().lower() != 'darwin':
                self.error_occurred.emit("Los archivos .dmg solo son compatibles con macOS")
                return False
            
            # Implementar lógica de instalación DMG
            logging.info("Instalación DMG no implementada completamente")
            return False
        except Exception as e:
            logging.error(f"Error installing .dmg: {e}")
            return False

    def _install_from_exe(self, exe_path: str) -> bool:
        """Instala archivo .exe en Windows"""
        try:
            if platform.system().lower() != 'windows':
                self.error_occurred.emit("Los archivos .exe solo son compatibles con Windows")
                return False
            
            result = subprocess.run([exe_path, '/silent'], capture_output=True)
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Error installing .exe: {e}")
            return False

    def _install_from_msi(self, download_path: str) -> bool:
        """Instala archivo .msi en Windows"""
        try:
            if platform.system().lower() != 'windows':
                self.error_occurred.emit("Los archivos .msi solo son compatibles con Windows")
                return False
            
            result = subprocess.run(['msiexec', '/i', download_path, '/quiet'], 
                                  capture_output=True)
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Error installing .msi: {e}")
            return False

    def _install_from_appimage(self, download_path: str, current_dir: Path) -> bool:
        """Instala AppImage en Linux"""
        try:
            if platform.system().lower() != 'linux':
                self.error_occurred.emit("Los archivos AppImage solo son compatibles con Linux")
                return False
            
            # Hacer ejecutable
            os.chmod(download_path, 0o755)
            
            # Mover a directorio de aplicación
            app_name = "vpn-manager.AppImage"
            destination = current_dir / app_name
            shutil.move(download_path, destination)
            
            return True
        except Exception as e:
            logging.error(f"Error installing AppImage: {e}")
            return False

    def _install_generic_archive(self, download_path: str, current_dir: Path, backup_dir: Path) -> bool:
        """Intenta instalar archivo comprimido genérico"""
        try:
            temp_extract_dir = Path(tempfile.mkdtemp(prefix="vpn_extract_"))
            
            # Intentar diferentes métodos de extracción
            if self._try_extract_archive(download_path, temp_extract_dir):
                # Buscar carpeta principal
                extracted_items = list(temp_extract_dir.iterdir())
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    source_dir = extracted_items[0]
                else:
                    source_dir = temp_extract_dir
                
                return self._copy_update_files(source_dir, current_dir, backup_dir)
            else:
                self.error_occurred.emit("No se pudo extraer el archivo de actualización")
                return False
                
        except Exception as e:
            logging.error(f"Error installing generic archive: {e}")
            return False

    def _try_extract_archive(self, archive_path: str, extract_dir: Path) -> bool:
        """Intenta extraer archivo con diferentes métodos"""
        import tarfile
        
        try:
            # Intentar ZIP
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                return True
        except:
            pass
        
        try:
            # Intentar TAR.GZ
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
                return True
        except:
            pass
        
        try:
            # Intentar TAR
            with tarfile.open(archive_path, 'r') as tar:
                tar.extractall(extract_dir)
                return True
        except:
            pass
        
        return False

    def _find_project_root(self, extract_dir: Path) -> Optional[Path]:
        """Encuentra el directorio raíz del proyecto en el archivo extraído"""
        # Buscar Main.py o requirements.txt como indicadores del proyecto
        for root in extract_dir.rglob("*"):
            if root.is_dir():
                if (root / "Main.py").exists() or (root / "requirements.txt").exists():
                    return root
        
        # Si no se encuentra, asumir que es el directorio raíz
        return extract_dir


class AutoUpdater(QObject):
    """Clase principal del sistema de actualización automática"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.check_thread = None
        self.download_thread = None
        
    def check_for_updates(self, silent: bool = False):
        """Verifica si hay actualizaciones disponibles"""
        if self.check_thread and self.check_thread.isRunning():
            return
        
        self.check_thread = UpdateCheckThread()
        self.check_thread.update_available.connect(
            lambda data: self._handle_update_available(data, silent)
        )
        self.check_thread.no_update.connect(
            lambda: self._handle_no_update(silent)
        )
        self.check_thread.error_occurred.connect(
            lambda error: self._handle_check_error(error, silent)
        )
        self.check_thread.start()
    
    def _handle_update_available(self, release_data: dict, silent: bool):
        """Maneja cuando hay una actualización disponible"""
        version = release_data["tag_name"]
        name = release_data.get("name", f"Release {version}")
        body = release_data.get("body", "No hay notas de actualización disponibles.")
        
        # Truncar descripción si es muy larga
        if len(body) > 300:
            body = body[:300] + "..."
        
        message = (
            f"¡Nueva versión disponible!\n\n"
            f"Versión actual: {UpdaterConfig.CURRENT_VERSION}\n"
            f"Nueva versión: {version}\n\n"
            f"Descripción:\n{body}\n\n"
            f"¿Deseas descargar e instalar la actualización ahora?"
        )
        
        if not silent:
            reply = QMessageBox.question(
                self.parent_widget,
                "Actualización Disponible",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self._start_download(release_data)
    
    def _handle_no_update(self, silent: bool):
        """Maneja cuando no hay actualizaciones disponibles"""
        logging.info("No hay actualizaciones disponibles")
        if not silent:
            QMessageBox.information(
                self.parent_widget,
                "Sin actualizaciones",
                f"Ya tienes la versión más reciente ({UpdaterConfig.CURRENT_VERSION})"
            )
    
    def _handle_check_error(self, error: str, silent: bool):
        """Maneja errores al verificar actualizaciones"""
        logging.error(f"Error checking for updates: {error}")
        if not silent:
            QMessageBox.warning(
                self.parent_widget,
                "Error de conexión",
                f"No se pudo verificar actualizaciones:\n{error}"
            )
    
    def _start_download(self, release_data: dict):
        """Inicia la descarga de la actualización"""
        if self.download_thread and self.download_thread.isRunning():
            return
        
        # Crear diálogo de progreso
        self.progress_dialog = QProgressDialog(
            "Preparando descarga...", "Cancelar", 0, 100, self.parent_widget
        )
        self.progress_dialog.setWindowTitle("Descargando actualización")
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()
        
        # Crear y configurar hilo de descarga
        self.download_thread = UpdateDownloadThread(release_data)
        self.download_thread.progress_updated.connect(
            self.progress_dialog.setValue
        )
        self.download_thread.status_updated.connect(
            self.progress_dialog.setLabelText
        )
        self.download_thread.installation_completed.connect(
            self._handle_installation_completed
        )
        self.download_thread.error_occurred.connect(
            self._handle_download_error
        )
        
        # Conectar cancelación
        self.progress_dialog.canceled.connect(self.download_thread.terminate)
        
        self.download_thread.start()
    
    def _handle_installation_completed(self):
        """Maneja la instalación completada"""
        self.progress_dialog.close()
        
        reply = QMessageBox.question(
            self.parent_widget,
            "Actualización Completada",
            "La actualización se ha instalado correctamente.\n\n"
            "¿Deseas reiniciar la aplicación ahora para aplicar los cambios?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self._restart_application()
    
    def _handle_download_error(self, error: str):
        """Maneja errores durante la descarga"""
        self.progress_dialog.close()
        
        QMessageBox.critical(
            self.parent_widget,
            "Error de actualización",
            f"No se pudo completar la actualización:\n\n{error}"
        )
    
    def _restart_application(self):
        """Reinicia la aplicación"""
        try:
            # Obtener el ejecutable actual
            if getattr(sys, 'frozen', False):
                # Aplicación compilada
                executable = sys.executable
                args = []
            else:
                # Script de Python
                executable = sys.executable
                args = [sys.argv[0]]
                
            # Reiniciar aplicación
            if self.parent_widget:
                self.parent_widget.close()
                
            os.execv(executable, [executable] + args)
                
        except Exception as e:
            logging.error(f"Error restarting application: {e}")
            QMessageBox.warning(
                self.parent_widget,
                "Reinicio Manual Requerido",
                "Por favor, reinicia la aplicación manualmente para completar la actualización."
            )
