#!/bin/bash
# Instalador de VPN Manager para Linux

set -e

APP_NAME="VPN Manager"
INSTALL_DIR="/opt/vpn-manager"
DESKTOP_FILE="/usr/share/applications/vpn-manager.desktop"
BIN_LINK="/usr/local/bin/vpn-manager"

echo "🐧 Instalador de VPN Manager para Linux"
echo "======================================="

# Verificar permisos de root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: Este script debe ejecutarse como root (sudo ./install.sh)"
    exit 1
fi

echo "📁 Creando directorio de instalación..."
mkdir -p "$INSTALL_DIR"

echo "📋 Copiando archivos..."
cp VPN-Manager-Linux "$INSTALL_DIR/"
cp run.sh "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/VPN-Manager-Linux"
chmod +x "$INSTALL_DIR/run.sh"

echo "🔗 Creando enlace simbólico..."
ln -sf "$INSTALL_DIR/run.sh" "$BIN_LINK"

echo "🖥️  Creando entrada de escritorio..."
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=VPN Manager
Comment=Gestiona conexiones VPN de forma sencilla
Exec=$INSTALL_DIR/run.sh
Icon=network-vpn
Terminal=false
Categories=Network;
EOF

echo "🔄 Actualizando base de datos de aplicaciones..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications
fi

echo ""
echo "✅ ¡VPN Manager instalado exitosamente!"
echo ""
echo "🚀 Para ejecutar:"
echo "   vpn-manager"
echo "   O desde el menú de aplicaciones: '$APP_NAME'"
echo ""
echo "🗑️  Para desinstalar:"
echo "   sudo ./uninstall.sh"
