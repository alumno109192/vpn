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

# Configurar logging para el updater
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vpn_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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
        ".git",
        ".gitignore"
    ]


class UpdateCheckThread(QThread):
    """Hilo para verificar actualizaciones sin bloquear la UI"""
    update_available = pyqtSignal(dict)  # Emite los datos de la nueva versión
    no_update = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def run(self):
        try:
            response = requests.get(
                UpdaterConfig.UPDATE_CHECK_URL,
                headers=UpdaterConfig.GITHUB_API_HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get("tag_name", "").lstrip("v")
                
                if self._is_newer_version(latest_version, UpdaterConfig.CURRENT_VERSION):
                    self.update_available.emit(release_data)
                else:
                    self.no_update.emit()
            elif response.status_code == 404:
                self.error_occurred.emit("No se encontraron releases en GitHub")
            else:
                self.error_occurred.emit(f"Error de GitHub API: {response.status_code}")
                
        except Exception as e:
            self.error_occurred.emit(f"Error verificando actualizaciones: {str(e)}")
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compara versiones usando semver"""
        try:
            latest_parts = [int(x) for x in latest.split(".")]
            current_parts = [int(x) for x in current.split(".")]
            
            # Normalizar a 3 partes (major.minor.patch)
            while len(latest_parts) < 3:
                latest_parts.append(0)
            while len(current_parts) < 3:
                current_parts.append(0)
                
            return latest_parts > current_parts
        except Exception:
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
            # Sistema no reconocido, intentar patrones genéricos
            return self._find_generic_asset(assets)
        
        # Búsqueda por prioridades
        # 1. Buscar por patrones primarios + arquitectura
        for asset in assets:
            name = asset["name"].lower()
            if any(pattern in name for pattern in patterns["primary"]) and arch in name:
                if any(name.endswith(ext) for ext in patterns["extensions"]):
                    logging.info(f"Asset encontrado (primario + arch): {asset['name']}")
                    return asset["browser_download_url"]
        
        # 2. Buscar por patrones primarios sin arquitectura específica
        for asset in assets:
            name = asset["name"].lower()
            if any(pattern in name for pattern in patterns["primary"]):
                if any(name.endswith(ext) for ext in patterns["extensions"]):
                    logging.info(f"Asset encontrado (primario): {asset['name']}")
                    return asset["browser_download_url"]
        
        # 3. Buscar por patrones secundarios
        for asset in assets:
            name = asset["name"].lower()
            if any(pattern in name for pattern in patterns["secondary"]):
                if any(name.endswith(ext) for ext in patterns["extensions"]):
                    logging.info(f"Asset encontrado (secundario): {asset['name']}")
                    return asset["browser_download_url"]
        
        # 4. Búsqueda fallback: cualquier archivo compatible
        for asset in assets:
            name = asset["name"].lower()
            if any(name.endswith(ext) for ext in patterns["extensions"]):
                logging.info(f"Asset encontrado (fallback): {asset['name']}")
                return asset["browser_download_url"]
        
        # 5. Último recurso: buscar genérico
        return self._find_generic_asset(assets)
    
    def _find_generic_asset(self, assets) -> Optional[str]:
        """Busca assets genéricos como último recurso"""
        # Extensiones genéricas en orden de preferencia
        generic_extensions = [".zip", ".tar.gz", ".7z", ".rar"]
        
        for ext in generic_extensions:
            for asset in assets:
                if asset["name"].lower().endswith(ext):
                    logging.info(f"Asset genérico encontrado: {asset['name']}")
                    return asset["browser_download_url"]
        
        # Si no se encuentra nada, tomar el primer asset disponible
        if assets:
            logging.warning(f"Usando primer asset disponible: {assets[0]['name']}")
            return assets[0]["browser_download_url"]
                
        return None
    
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
                    
                    # Hacer backup del archivo original si existe
                    if destination.exists():
                        backup_dest = backup_dir / relative_path
                        backup_dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(destination, backup_dest)
                    
                    # Copiar archivo nuevo
                    shutil.copy2(item, destination)
                    
            return True
        except Exception as e:
            logging.error(f"Error copying update files: {e}")
            return False
    
    def _download_file(self, url: str) -> Optional[str]:
        """Descarga un archivo con barra de progreso"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Crear archivo temporal
            temp_dir = tempfile.mkdtemp(prefix="vpn_update_")
            filename = url.split("/")[-1]
            download_path = os.path.join(temp_dir, filename)
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress_updated.emit(progress)
            
            self.download_path = download_path
            return download_path
            
        except Exception as e:
            self.error_occurred.emit(f"Error descargando: {str(e)}")
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
    
    def _install_from_zip(self, zip_path: str, current_dir: Path, backup_dir: Path) -> bool:
        """Instala desde archivo ZIP"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extraer a directorio temporal
                temp_extract = Path(tempfile.mkdtemp(prefix="vpn_extract_"))
                zip_ref.extractall(temp_extract)
                
                # Encontrar el directorio raíz del proyecto en el ZIP
                project_root = self._find_project_root(temp_extract)
                if not project_root:
                    return False
                
                # Copiar archivos nuevos/actualizados
                for item in project_root.rglob("*"):
                    if item.is_file():
                        relative_path = item.relative_to(project_root)
                        
                        # Saltar archivos que deben preservarse
                        if any(preserve in str(relative_path) for preserve in UpdaterConfig.PRESERVE_FILES):
                            continue
                        
                        dest_path = current_dir / relative_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest_path)
                
                # Limpiar
                shutil.rmtree(temp_extract)
                return True
                
        except Exception as e:
            logging.error(f"Error installing from ZIP: {e}")
            return False
    
    def _install_from_dmg(self, dmg_path: str, current_dir: Path) -> bool:
        """Instala desde archivo DMG (macOS)"""
        # En macOS, los DMG normalmente contienen aplicaciones .app
        # Por simplicidad, asumimos que el usuario debe hacer la instalación manualmente
        self.status_updated.emit("Por favor, monta el DMG e instala manualmente la aplicación")
        return True
    
    def _install_from_exe(self, exe_path: str) -> bool:
        """Ejecuta instalador EXE (Windows)"""
        try:
            subprocess.run([exe_path, '/S'], check=True)  # /S para instalación silenciosa
            return True
        except Exception as e:
            logging.error(f"Error running EXE installer: {e}")
            return False
    
    def _find_project_root(self, extract_dir: Path) -> Optional[Path]:
        """Encuentra el directorio raíz del proyecto en el ZIP extraído"""
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
            lambda error: self._handle_error(error, silent)
        )
        
        self.check_thread.start()
    
    def _handle_update_available(self, release_data: dict, silent: bool):
        """Maneja cuando hay una actualización disponible"""
        version = release_data.get("tag_name", "").lstrip("v")
        release_notes = release_data.get("body", "")
        
        if silent:
            # En modo silencioso, solo registrar en el log
            logging.info(f"Update available: {version}")
            return
        
        # Mostrar diálogo de confirmación
        msg = QMessageBox(self.parent_widget)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Actualización Disponible")
        msg.setText(f"¡Nueva versión disponible: {version}!")
        
        if release_notes:
            msg.setDetailedText(f"Notas de la versión:\n{release_notes}")
        
        msg.setInformativeText("¿Deseas descargar e instalar la actualización ahora?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec_() == QMessageBox.Yes:
            self._start_update_process(release_data)
    
    def _handle_no_update(self, silent: bool):
        """Maneja cuando no hay actualizaciones"""
        if not silent:
            QMessageBox.information(
                self.parent_widget,
                "Sin Actualizaciones",
                "Ya tienes la versión más reciente de VPN Manager."
            )
    
    def _handle_error(self, error: str, silent: bool):
        """Maneja errores durante la verificación"""
        logging.error(f"Update check error: {error}")
        if not silent:
            QMessageBox.warning(
                self.parent_widget,
                "Error de Actualización",
                f"No se pudo verificar actualizaciones:\n{error}"
            )
    
    def _start_update_process(self, release_data: dict):
        """Inicia el proceso de descarga e instalación"""
        # Crear diálogo de progreso
        progress_dialog = QProgressDialog(
            "Preparando descarga...",
            "Cancelar",
            0, 100,
            self.parent_widget
        )
        progress_dialog.setWindowTitle("Actualizando VPN Manager")
        progress_dialog.setModal(True)
        progress_dialog.show()
        
        # Configurar hilo de descarga
        self.download_thread = UpdateDownloadThread(release_data)
        
        # Conectar señales
        self.download_thread.progress_updated.connect(progress_dialog.setValue)
        self.download_thread.status_updated.connect(progress_dialog.setLabelText)
        self.download_thread.download_completed.connect(
            lambda path: logging.info(f"Download completed: {path}")
        )
        self.download_thread.installation_completed.connect(
            lambda: self._handle_installation_completed(progress_dialog)
        )
        self.download_thread.error_occurred.connect(
            lambda error: self._handle_download_error(error, progress_dialog)
        )
        
        # Manejar cancelación
        progress_dialog.canceled.connect(self.download_thread.terminate)
        
        # Iniciar descarga
        self.download_thread.start()
    
    def _handle_installation_completed(self, progress_dialog):
        """Maneja la finalización exitosa de la instalación"""
        progress_dialog.close()
        
        msg = QMessageBox(self.parent_widget)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Actualización Completada")
        msg.setText("¡Actualización instalada exitosamente!")
        msg.setInformativeText("La aplicación se reiniciará para aplicar los cambios.")
        msg.setStandardButtons(QMessageBox.Ok)
        
        if msg.exec_() == QMessageBox.Ok:
            self._restart_application()
    
    def _handle_download_error(self, error: str, progress_dialog):
        """Maneja errores durante la descarga/instalación"""
        progress_dialog.close()
        
        QMessageBox.critical(
            self.parent_widget,
            "Error de Actualización",
            f"Error durante la actualización:\n{error}"
        )
    
    def _restart_application(self):
        """Reinicia la aplicación"""
        try:
            # Obtener el ejecutable actual
            if getattr(sys, 'frozen', False):
                # Ejecutable de PyInstaller
                executable = sys.executable
            else:
                # Script Python
                executable = sys.executable
                args = [sys.argv[0]] + sys.argv[1:]
            
            # Reiniciar
            if platform.system() == "Windows":
                subprocess.Popen([executable] + (args if not getattr(sys, 'frozen', False) else []))
            else:
                os.execv(executable, [executable] + (args if not getattr(sys, 'frozen', False) else []))
                
        except Exception as e:
            logging.error(f"Error restarting application: {e}")
            QMessageBox.warning(
                self.parent_widget,
                "Reinicio Manual Requerido",
                "Por favor, reinicia la aplicación manualmente para completar la actualización."
            )

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

    def _copy_update_files(self, source_dir: Path, current_dir: Path, backup_dir: Path) -> bool:
        """Copia archivos de actualización de forma segura"""
        try:
            for item in source_dir.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(source_dir)
                    destination = current_dir / relative_path
                    
                    # Crear directorio padre si no existe
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copiar archivo
                    shutil.copy2(item, destination)
            
            return True
        except Exception as e:
            logging.error(f"Error copying update files: {e}")
            return False
