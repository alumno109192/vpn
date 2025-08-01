#!/bin/bash
# Script para completar el empaquetado .deb de VPN Manager
set -e

# Variables
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_EXEC="$PROJECT_DIR/dist/VPN-Manager"
DEB_ROOT="$PROJECT_DIR/deb_build/vpn-manager-ubuntu"
BIN_DIR="$DEB_ROOT/usr/local/bin"
ICON_SRC="$PROJECT_DIR/icon.png"
ICON_DST="$DEB_ROOT/usr/share/icons/hicolor/64x64/apps/vpn-manager.png"
DESKTOP_FILE="$DEB_ROOT/usr/share/applications/vpn-manager.desktop"

# Copiar ejecutable
if [ -f "$DIST_EXEC" ]; then
    cp "$DIST_EXEC" "$BIN_DIR/vpn-manager"
    chmod 755 "$BIN_DIR/vpn-manager"
else
    echo "ERROR: Ejecutable no encontrado en $DIST_EXEC. Ejecuta PyInstaller primero."
    exit 1
fi

# Copiar icono si existe
if [ -f "$ICON_SRC" ]; then
    cp "$ICON_SRC" "$ICON_DST"
else
    echo "ADVERTENCIA: No se encontró icon.png. El .deb no tendrá icono personalizado."
fi

# Asegurar permisos
chmod 755 "$BIN_DIR/vpn-manager"
chmod 644 "$DESKTOP_FILE"

# Empaquetar .deb
cd "$PROJECT_DIR/deb_build"
dpkg-deb --build vpn-manager-ubuntu

# Mensaje final
echo "\nPaquete .deb generado en: $PROJECT_DIR/deb_build/vpn-manager-ubuntu.deb"
echo "Para instalar: sudo dpkg -i $PROJECT_DIR/deb_build/vpn-manager-ubuntu.deb"
