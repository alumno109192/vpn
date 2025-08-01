#!/usr/bin/env python3
"""
Configuración de versión para VPN Manager
"""

# Versión actual de la aplicación (formato semver)
__version__ = "1.3.0"
__version_info__ = tuple(int(i) for i in __version__.split('.'))

# Información de la aplicación
APP_NAME = "VPN Manager"
APP_DESCRIPTION = "Una aplicación multiplataforma para gestionar conexiones VPN"
APP_AUTHOR = "Tu Nombre"
APP_EMAIL = "yesod3d@gmail.com"

# Configuración del repositorio
GITHUB_REPO = "alumno109192/vpn"
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"

# URLs de la API
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"
RELEASES_API_URL = f"{GITHUB_API_BASE}/releases/latest"

# Configuración de actualización
AUTO_UPDATE_ENABLED = True
UPDATE_CHECK_INTERVAL = 24 * 60 * 60  # 24 horas en segundos
SILENT_UPDATE_CHECK = True  # Verificar actualizaciones silenciosamente al inicio

def get_version():
    """Retorna la versión actual como string"""
    return __version__

def get_version_info():
    """Retorna la información de versión como tupla"""
    return __version_info__

def get_app_info():
    """Retorna información completa de la aplicación"""
    return {
        "name": APP_NAME,
        "version": __version__,
        "description": APP_DESCRIPTION,
        "author": APP_AUTHOR,
        "email": APP_EMAIL
    }
