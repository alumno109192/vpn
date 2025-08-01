#!/usr/bin/env python3

import os
import sys
from pathlib import Path


def get_config_dir():
    """Obtener el directorio de configuración de la aplicación"""
    try:
        # Linux/macOS
        config_dir = os.path.expanduser("~/.config/vpn-manager")
        if sys.platform == "win32":
            # Windows
            config_dir = os.path.join(os.environ.get("APPDATA", ""), "VPN Manager")
        
        # Crear directorio si no existe
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    except:
        # Fallback al directorio actual
        return os.path.dirname(os.path.abspath(__file__))
