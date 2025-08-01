#!/bin/bash

# Script robusto para crear ejecutable Linux de VPN Manager
# Funciona desde cualquier sistema con Docker o Linux nativo

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$PWD"
PROJECT_NAME="VPN-Manager-Linux"
ARCH=$(uname -m)
ARCH_NAME=""

case $ARCH in
    x86_64)
        ARCH_NAME="x64"
        ;;
    aarch64|arm64)
        ARCH_NAME="ARM64"
        ;;
    *)
        ARCH_NAME="Unknown"
        echo "⚠️  Arquitectura no reconocida: $ARCH"
        ;;
esac

echo "🐧 Script para crear ejecutable Linux"
echo "===================================="
echo "📋 Arquitectura detectada: $ARCH ($ARCH_NAME)"

# Crear directorio temporal
TEMP_DIR="/tmp/vpn-manager-linux-build-$$"
echo "📁 Creando directorio temporal: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Copiar archivos del proyecto
echo "📋 Copiando archivos del proyecto..."
rsync -av --progress "$SCRIPT_DIR/" "$TEMP_DIR/" \
    --exclude='.git' \
    --exclude='build' \
    --exclude='dist' \
    --exclude='release' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    --exclude='*_venv' \
    --exclude='venv'

cd "$TEMP_DIR"

echo "🔧 Configurando entorno Python..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no encontrado"
    exit 1
fi

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv linux_venv
source linux_venv/bin/activate

# Actualizar pip
echo "📦 Instalando dependencias..."
pip install --upgrade pip

# Instalar PyQt5 específica para Linux
pip install PyQt5==5.15.9

# Instalar PyInstaller
pip install PyInstaller==6.14.1

# Instalar otras dependencias
pip install pexpect requests cryptography urllib3 certifi

# Verificar PyQt5
echo "🔍 Verificando PyQt5..."
python -c "import PyQt5.QtWidgets; print('PyQt5 OK')" || {
    echo "❌ Error: PyQt5 no funciona correctamente"
    exit 1
}

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist

# Crear archivo spec personalizado
echo "📝 Creando archivo spec personalizado..."
cat > vpn_manager_linux.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, os.getcwd())

# Configuración del análisis
a = Analysis(
    ['Main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ('dialogs', 'dialogs'),
        ('threads', 'threads'),
        ('*.py', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'pexpect',
        'requests',
        'cryptography',
        'auto_updater',
        'version',
        'license',
        'license_storage',
        'license_generator',
        'license_encryptor',
        'models',
        'dialogs.config_dialog',
        'dialogs.edit_dialog', 
        'dialogs.sudo_dialog',
        'threads.vpn_thread',
        'threads.file_thread'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VPN-Manager-Linux',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Ejecutar PyInstaller
echo "🔨 Ejecutando PyInstaller..."
pyinstaller vpn_manager_linux.spec --clean --noconfirm

# Verificar que se creó el ejecutable
if [ -f "dist/VPN-Manager-Linux" ]; then
    echo "✅ Ejecutable creado exitosamente"
    
    # Crear directorio de release
    RELEASE_DIR="$SCRIPT_DIR/release/VPN-Manager-Linux-$ARCH_NAME"
    mkdir -p "$RELEASE_DIR"
    
    # Copiar ejecutable
    echo "📦 Empaquetando release..."
    cp "dist/VPN-Manager-Linux" "$RELEASE_DIR/"
    chmod +x "$RELEASE_DIR/VPN-Manager-Linux"
    
    # Crear script de ejecución
    cat > "$RELEASE_DIR/run.sh" << 'RUNEOF'
#!/bin/bash
# Script para ejecutar VPN Manager Linux

cd "$(dirname "$0")"

# Configurar variables de entorno
export QT_QPA_PLATFORM_PLUGIN_PATH="$(pwd)"
export QT_PLUGIN_PATH="$(pwd)"

# Ejecutar aplicación
./VPN-Manager-Linux "$@"
RUNEOF
    
    chmod +x "$RELEASE_DIR/run.sh"
    
    # Crear instalador
    cat > "$RELEASE_DIR/install.sh" << 'INSTEOF'
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
INSTEOF
    
    chmod +x "$RELEASE_DIR/install.sh"
    
    # Crear desinstalador
    cat > "$RELEASE_DIR/uninstall.sh" << 'UNINSTEOF'
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
UNINSTEOF
    
    chmod +x "$RELEASE_DIR/uninstall.sh"
    
    # Crear README
    cat > "$RELEASE_DIR/README.md" << 'READMEEOF'
# VPN Manager para Linux

## 🚀 Ejecución Rápida

Para ejecutar la aplicación directamente:
```bash
./run.sh
```

## 📥 Instalación en el Sistema

Para instalar VPN Manager en el sistema:
```bash
sudo ./install.sh
```

Después de la instalación, puedes ejecutar:
```bash
vpn-manager
```

O buscar "VPN Manager" en el menú de aplicaciones.

## 🗑️ Desinstalación

Para desinstalar completamente:
```bash
sudo ./uninstall.sh
```

## 📋 Requisitos

- Linux con entorno gráfico (GNOME, KDE, XFCE, etc.)
- OpenVPN (para conexiones OpenVPN)
- StrongSwan (para conexiones IPSec) - opcional

## 🔧 Instalación de Dependencias

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install openvpn strongswan
```

### CentOS/RHEL/Fedora:
```bash
sudo yum install openvpn strongswan
# o para Fedora:
sudo dnf install openvpn strongswan
```

## 🔐 Permisos

La aplicación requiere permisos de administrador para:
- Configurar conexiones VPN
- Modificar rutas de red
- Acceder a interfaces de red

## 🛠️ Solución de Problemas

### Error de Qt Platform Plugin:
```bash
export QT_QPA_PLATFORM=xcb
./run.sh
```

### Error de permisos:
```bash
chmod +x VPN-Manager-Linux
chmod +x run.sh
```

## 📞 Soporte

Para soporte técnico, contacta: yesod3d@gmail.com

---
**VPN Manager** - Gestiona tus conexiones VPN de forma sencilla
READMEEOF
    
    # Crear archivo comprimido
    echo "🗜️  Creando archivo comprimido..."
    cd "$SCRIPT_DIR/release"
    tar -czf "VPN-Manager-Linux-$ARCH_NAME-$(date +%Y.%m.%d).tar.gz" "VPN-Manager-Linux-$ARCH_NAME"
    
    echo ""
    echo "🎉 ¡Build de Linux completado exitosamente!"
    echo ""
    echo "📁 Archivos generados:"
    echo "   ├── release/VPN-Manager-Linux-$ARCH_NAME/"
    echo "   │   ├── VPN-Manager-Linux    (ejecutable principal)"
    echo "   │   ├── run.sh               (script de ejecución)"
    echo "   │   ├── install.sh           (instalador del sistema)"
    echo "   │   ├── uninstall.sh         (desinstalador)"
    echo "   │   └── README.md            (instrucciones)"
    echo "   └── release/VPN-Manager-Linux-$ARCH_NAME-$(date +%Y.%m.%d).tar.gz"
    echo ""
    echo "🧪 Para probar:"
    echo "   cd release/VPN-Manager-Linux-$ARCH_NAME && ./run.sh"
    echo ""
    echo "💻 Para instalar en el sistema:"
    echo "   cd release/VPN-Manager-Linux-$ARCH_NAME && sudo ./install.sh"
    echo ""
    echo "📤 Para distribuir:"
    echo "   Comparte el archivo: release/VPN-Manager-Linux-$ARCH_NAME-$(date +%Y.%m.%d).tar.gz"
    
    # Limpiar directorio temporal
    cd "$CURRENT_DIR"
    rm -rf "$TEMP_DIR"
    
else
    echo "❌ Error: No se pudo crear el ejecutable Linux"
    cd "$CURRENT_DIR"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "✅ ¡Build Linux completado exitosamente!"
