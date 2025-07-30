#!/bin/bash

# Script de lanzamiento para VPN Manager en macOS
# Este script configura las variables de entorno necesarias para Qt

echo "🚀 Iniciando VPN Manager..."

# Obtener la ruta del directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

# Verificar que el entorno virtual existe
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Error: Entorno virtual no encontrado en $VENV_PYTHON"
    echo "Por favor, asegúrate de que el entorno virtual esté configurado correctamente."
    exit 1
fi

# Configurar variables de entorno de Qt
echo "🔧 Configurando entorno Qt..."

# Obtener la ruta de PyQt5
PYQT5_PATH=$("$VENV_PYTHON" -c "import PyQt5; import os; print(os.path.dirname(PyQt5.__file__))" 2>/dev/null)

if [ -n "$PYQT5_PATH" ]; then
    export QT_PLUGIN_PATH="$PYQT5_PATH/Qt5/plugins"
    export QT_QPA_PLATFORM_PLUGIN_PATH="$PYQT5_PATH/Qt5/plugins/platforms"
    
    # Configurar DYLD_LIBRARY_PATH para macOS
    QT_LIB_PATH="$PYQT5_PATH/Qt5/lib"
    if [ -d "$QT_LIB_PATH" ]; then
        if [ -n "$DYLD_LIBRARY_PATH" ]; then
            export DYLD_LIBRARY_PATH="$QT_LIB_PATH:$DYLD_LIBRARY_PATH"
        else
            export DYLD_LIBRARY_PATH="$QT_LIB_PATH"
        fi
    fi
    
    echo "✅ Qt configurado correctamente"
    echo "   Plugin Path: $QT_PLUGIN_PATH"
    echo "   Platform Plugin Path: $QT_QPA_PLATFORM_PLUGIN_PATH"
else
    echo "⚠️  Advertencia: No se pudo determinar la ruta de PyQt5"
fi

# Ejecutar la aplicación
echo "🎯 Ejecutando VPN Manager..."
cd "$SCRIPT_DIR"
exec "$VENV_PYTHON" Main.py "$@"
