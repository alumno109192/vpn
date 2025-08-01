#!/bin/bash
# Desinstalador de VPN Manager para Linux

INSTALL_DIR="/opt/vpn-manager"
DESKTOP_FILE="/usr/share/applications/vpn-manager.desktop"
BIN_LINK="/usr/local/bin/vpn-manager"

echo "🗑️  Desinstalador de VPN Manager"
echo "==============================="

# Verificar permisos de root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: Este script debe ejecutarse como root (sudo ./uninstall.sh)"
    exit 1
fi

echo "🧹 Eliminando archivos..."

# Eliminar directorio de instalación
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "✅ Directorio de instalación eliminado"
fi

# Eliminar enlace simbólico
if [ -L "$BIN_LINK" ]; then
    rm "$BIN_LINK"
    echo "✅ Enlace simbólico eliminado"
fi

# Eliminar entrada de escritorio
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "✅ Entrada de escritorio eliminada"
fi

echo "🔄 Actualizando base de datos de aplicaciones..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications
fi

echo ""
echo "✅ VPN Manager desinstalado completamente"
