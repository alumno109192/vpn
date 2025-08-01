#!/bin/bash
#
# Instalador manual de VPN Manager (alternativa al .deb)
# Instala la aplicación directamente sin paquete
#

set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# Función de instalación
install_vpn_manager() {
    log "=== Instalación manual de VPN Manager v1.3.4 ==="
    
    # Verificar dependencias
    log "Verificando dependencias del sistema..."
    
    if ! dpkg -l | grep -q python3-pyqt5; then
        info "Instalando PyQt5..."
        sudo apt update
        sudo apt install -y python3-pyqt5 python3-requests python3-cryptography openvpn strongswan
    fi
    
    # Crear directorio de instalación
    INSTALL_DIR="/opt/vpn-manager"
    log "Creando directorio de instalación: $INSTALL_DIR"
    sudo mkdir -p "$INSTALL_DIR"
    
    # Copiar archivos de la aplicación
    log "Copiando archivos de aplicación..."
    sudo cp -r . "$INSTALL_DIR/"
    sudo chown -R root:root "$INSTALL_DIR"
    
    # Crear script ejecutable en /usr/local/bin
    log "Creando script ejecutable..."
    sudo tee /usr/local/bin/vpn-manager-app > /dev/null << 'EOF'
#!/bin/bash
#
# VPN Manager v1.3.4 - Script de ejecución
#

cd /opt/vpn-manager

# Limpiar variables que pueden causar conflictos
unset LD_LIBRARY_PATH
unset LD_PRELOAD

# Verificar PyQt5
if ! /usr/bin/python3 -c "import PyQt5.QtWidgets" 2>/dev/null; then
    echo "Error: PyQt5 no está instalado"
    echo "Ejecuta: sudo apt install python3-pyqt5"
    exit 1
fi

# Ejecutar la aplicación
exec /usr/bin/python3 Main.py "$@"
EOF
    
    sudo chmod +x /usr/local/bin/vpn-manager-app
    
    # Crear entrada de menú de aplicaciones
    log "Creando entrada en menú de aplicaciones..."
    sudo tee /usr/share/applications/vpn-manager.desktop > /dev/null << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=VPN Manager
Comment=Una aplicación multiplataforma para gestionar conexiones VPN
Exec=vpn-manager-app
Icon=network-vpn
Terminal=false
StartupNotify=true
Categories=Network;Security;
Keywords=vpn;network;security;openvpn;ipsec;
EOF
    
    # Actualizar base de datos de aplicaciones
    if command -v update-desktop-database >/dev/null 2>&1; then
        sudo update-desktop-database /usr/share/applications
    fi
    
    log "✓ Instalación completada"
    info "Puedes ejecutar la aplicación con: vpn-manager-app"
    info "O buscarla en el menú de aplicaciones como 'VPN Manager'"
}

# Función de desinstalación
uninstall_vpn_manager() {
    log "=== Desinstalación de VPN Manager ==="
    
    # Detener procesos
    pkill -f "vpn-manager" 2>/dev/null || true
    
    # Remover archivos
    sudo rm -rf /opt/vpn-manager
    sudo rm -f /usr/local/bin/vpn-manager-app
    sudo rm -f /usr/share/applications/vpn-manager.desktop
    
    # Actualizar base de datos de aplicaciones
    if command -v update-desktop-database >/dev/null 2>&1; then
        sudo update-desktop-database /usr/share/applications
    fi
    
    log "✓ Desinstalación completada"
}

# Verificar estado
check_installation() {
    if [ -f "/usr/local/bin/vpn-manager-app" ] && [ -d "/opt/vpn-manager" ]; then
        log "VPN Manager está instalado"
        info "Comando: vpn-manager-app"
        info "Directorio: /opt/vpn-manager"
        return 0
    else
        error "VPN Manager no está instalado"
        return 1
    fi
}

# Función principal
case "${1:-install}" in
    install)
        install_vpn_manager
        ;;
    uninstall)
        uninstall_vpn_manager
        ;;
    check)
        check_installation
        ;;
    *)
        echo "Uso: $0 [install|uninstall|check]"
        echo "  install   - Instalar VPN Manager (por defecto)"
        echo "  uninstall - Desinstalar VPN Manager"
        echo "  check     - Verificar instalación"
        exit 1
        ;;
esac
