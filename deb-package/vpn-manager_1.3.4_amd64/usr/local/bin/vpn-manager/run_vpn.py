#!/usr/bin/env python3
"""
Script de inicio para VPN Manager que configura correctamente las variables de entorno de Qt.
"""
import os
import sys
from pathlib import Path

def setup_qt_environment():
    """Configura las variables de entorno necesarias para Qt en macOS."""
    # Obtener la ruta base de PyQt5
    try:
        import PyQt5
        pyqt5_path = Path(PyQt5.__file__).parent
        qt5_path = pyqt5_path / "Qt5"
        
        # Configurar variables de entorno de Qt
        os.environ["QT_PLUGIN_PATH"] = str(qt5_path / "plugins")
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(qt5_path / "plugins" / "platforms")
        
        # En macOS, también configuramos la biblioteca Qt
        qt_lib_path = qt5_path / "lib"
        if qt_lib_path.exists():
            if "DYLD_LIBRARY_PATH" in os.environ:
                os.environ["DYLD_LIBRARY_PATH"] = f"{qt_lib_path}:{os.environ['DYLD_LIBRARY_PATH']}"
            else:
                os.environ["DYLD_LIBRARY_PATH"] = str(qt_lib_path)
        
        print(f"Qt Plugin Path configurado: {os.environ['QT_PLUGIN_PATH']}")
        print(f"Qt Platform Plugin Path configurado: {os.environ['QT_QPA_PLATFORM_PLUGIN_PATH']}")
        
    except ImportError as e:
        print(f"Error importando PyQt5: {e}")
        sys.exit(1)

def main():
    """Función principal que configura el entorno y ejecuta la aplicación."""
    print("Configurando entorno Qt para macOS...")
    setup_qt_environment()
    
    print("Iniciando VPN Manager...")
    
    # Importar y ejecutar la aplicación principal
    try:
        from Main import main as main_app
        main_app()
    except ImportError:
        # Si Main no tiene una función main, ejecutamos directamente
        import subprocess
        import sys
        result = subprocess.run([sys.executable, "Main.py"], cwd=Path(__file__).parent)
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
