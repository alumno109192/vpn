#!/bin/bash
#
# Lanzador para VPN Manager optimizado para Ubuntu
#

# Directorio de la aplicación
APP_DIR="/home/jorge-kuik/GIT/vpn/vpn2"

# Cambiar al directorio
cd "$APP_DIR" || exit 1

echo "=== Lanzador VPN Manager v1.3.4 ==="

# Verificar que PyQt5 está instalado
if ! /usr/bin/python3 -c "import PyQt5.QtWidgets" 2>/dev/null; then
    echo "Error: PyQt5 no está instalado"
    echo "Por favor ejecuta: sudo apt install python3-pyqt5"
    exit 1
fi

echo "✓ PyQt5 verificado"

# Verificar conectividad X11
if [ -z "$DISPLAY" ]; then
    echo "Error: Variable DISPLAY no está configurada"
    exit 1
fi

echo "✓ Display configurado: $DISPLAY"

# Limpiar solo las variables problemáticas pero mantener X11
unset LD_LIBRARY_PATH
unset LD_PRELOAD

# Ejecutar la aplicación
echo "Iniciando VPN Manager..."
/usr/bin/python3 Main.py "$@"
