#!/bin/bash

# VPN Manager Installation Script v1.3
# Para sistemas Linux x86_64

set -e

echo "=== VPN Manager v1.3 - Script de Instalación ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Error: No ejecutes este script como root/sudo.${NC}"
   echo "El script solicitará permisos cuando sea necesario."
   exit 1
fi

# Check system architecture
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    echo -e "${RED}Error: Este paquete es solo para sistemas x86_64.${NC}"
    echo "Tu sistema es: $ARCH"
    exit 1
fi

# Check Python 3
echo -e "${YELLOW}Verificando Python 3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 no está instalado.${NC}"
    echo "Instala Python 3 con: sudo apt install python3 python3-pip"
    exit 1
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 no está instalado.${NC}"
    echo "Instala pip3 con: sudo apt install python3-pip"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 encontrado${NC}"

# Check PyQt5
echo -e "${YELLOW}Verificando PyQt5...${NC}"
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo -e "${YELLOW}PyQt5 no encontrado. Instalando...${NC}"
    pip3 install PyQt5 --user
fi

echo -e "${GREEN}✓ PyQt5 disponible${NC}"

# Check OpenVPN
echo -e "${YELLOW}Verificando OpenVPN...${NC}"
if ! command -v openvpn &> /dev/null; then
    echo -e "${YELLOW}OpenVPN no encontrado. Instalando...${NC}"
    sudo apt update
    sudo apt install -y openvpn
fi

echo -e "${GREEN}✓ OpenVPN disponible${NC}"

# Check StrongSwan (optional)
echo -e "${YELLOW}Verificando StrongSwan (opcional para IPSec)...${NC}"
if ! command -v ipsec &> /dev/null; then
    echo -e "${YELLOW}StrongSwan no encontrado. ¿Deseas instalarlo? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        sudo apt install -y strongswan
        echo -e "${GREEN}✓ StrongSwan instalado${NC}"
    else
        echo -e "${YELLOW}! StrongSwan omitido (las conexiones IPSec no funcionarán)${NC}"
    fi
else
    echo -e "${GREEN}✓ StrongSwan disponible${NC}"
fi

# Install directory
INSTALL_DIR="$HOME/.local/share/vpn-manager"
echo -e "${YELLOW}Instalando en: $INSTALL_DIR${NC}"

# Create install directory
mkdir -p "$INSTALL_DIR"

# Copy files (assuming they're extracted here)
echo -e "${YELLOW}Copiando archivos...${NC}"
cp -r * "$INSTALL_DIR/"

# Make main script executable
chmod +x "$INSTALL_DIR/Main.py"

# Create desktop entry
echo -e "${YELLOW}Creando entrada de escritorio...${NC}"
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_DIR/vpn-manager.desktop" << EOF
[Desktop Entry]
Type=Application
Name=VPN Manager
Comment=Gestor de conexiones VPN
Exec=python3 "$INSTALL_DIR/Main.py"
Icon=security-high
Terminal=false
Categories=Network;Security;
StartupNotify=true
EOF

# Create symbolic link in PATH (optional)
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/vpn-manager" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 Main.py "\$@"
EOF

chmod +x "$BIN_DIR/vpn-manager"

echo ""
echo -e "${GREEN}=== Instalación Completada ===${NC}"
echo ""
echo "La aplicación se ha instalado en: $INSTALL_DIR"
echo ""
echo "Puedes ejecutarla de las siguientes maneras:"
echo "1. Desde el menú de aplicaciones: 'VPN Manager'"
echo "2. Desde terminal: vpn-manager"
echo "3. Directamente: python3 $INSTALL_DIR/Main.py"
echo ""
echo -e "${YELLOW}Nota: La primera vez que ejecutes la aplicación, necesitarás introducir tu contraseña sudo.${NC}"
echo ""
echo -e "${GREEN}¡Disfruta de VPN Manager v1.3!${NC}"
