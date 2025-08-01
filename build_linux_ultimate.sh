#!/bin/bash

# Script para crear ejecutable Linux multiplataforma
echo "🐧 Script para crear ejecutable Linux"
echo "===================================="

# Detectar arquitectura
ARCH=$(uname -m)
if [[ "$ARCH" == "x86_64" ]]; then
    ARCH_NAME="x64"
elif [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    ARCH_NAME="arm64"
else
    ARCH_NAME="$ARCH"
fi

echo "📋 Arquitectura detectada: $ARCH ($ARCH_NAME)"

# Crear directorio temporal
TEMP_DIR="/tmp/vpn-manager-linux-build-$(date +%s)"
CURRENT_DIR="$(pwd)"

echo "📁 Creando directorio temporal: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo "📋 Copiando archivos del proyecto..."
rsync -av --exclude='.venv' --exclude='__pycache__' --exclude='build' --exclude='dist' --exclude='*.spec' --exclude='release' . "$TEMP_DIR/" 2>/dev/null || cp -R . "$TEMP_DIR/"

# Cambiar al directorio temporal
cd "$TEMP_DIR"

echo "🔧 Configurando entorno Python..."
# Verificar si Python3 está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Instalando..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip
    else
        echo "❌ No se pudo instalar Python3 automáticamente"
        exit 1
    fi
fi

# Crear entorno virtual limpio
echo "📦 Creando entorno virtual..."
python3 -m venv linux_venv
source linux_venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install PyQt5==5.15.9
pip install PyInstaller==6.14.1
pip install pexpect requests cryptography packaging urllib3 certifi

# Verificar PyQt5
echo "🔍 Verificando PyQt5..."
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')" || {
    echo "❌ Error con PyQt5, intentando alternativa..."
    pip uninstall -y PyQt5
    pip install PyQt5==5.15.7
}

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build/ dist/ *.spec

# Crear archivo spec personalizado
echo "📝 Creando archivo spec personalizado..."
cat > vpn_manager_linux.spec << 'SPEC_EOF'
# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None
app_name = "VPN-Manager-Linux"

# Archivos a incluir
added_files = [
    ('dialogs', 'dialogs'),
    ('threads', 'threads'),
    ('version.py', '.'),
    ('auto_updater.py', '.'),
    ('license.py', '.'),
    ('license_storage.py', '.'),
    ('license_encryptor.py', '.'),
    ('license_generator.py', '.'),
    ('models.py', '.'),
]

# Imports ocultos
hidden_imports = [
    'PyQt5.sip',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'pexpect',
    'requests',
    'cryptography',
    'packaging',
    'urllib3',
    'certifi',
    'json',
    'threading',
    'subprocess',
    'os',
    'sys',
    'platform',
    'pathlib',
]

# Módulos a excluir
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'PIL',
    'cv2',
    'torch',
    'tensorflow',
]

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
SPEC_EOF

echo "🔨 Ejecutando PyInstaller..."
pyinstaller --clean --noconfirm vpn_manager_linux.spec

# Verificar resultado
if [ -d "dist/VPN-Manager-Linux" ]; then
    echo "✅ Ejecutable Linux creado exitosamente!"
    
    # Volver al directorio original
    cd "$CURRENT_DIR"
    
    # Crear directorio de distribución
    echo "📦 Creando paquete de distribución..."
    mkdir -p "release/VPN-Manager-Linux-$ARCH_NAME"
    
    # Copiar el resultado
    cp -R "$TEMP_DIR/dist/VPN-Manager-Linux" "release/VPN-Manager-Linux-$ARCH_NAME/"
    
    # Obtener información del ejecutable
    APP_SIZE=$(du -sh "release/VPN-Manager-Linux-$ARCH_NAME/VPN-Manager-Linux" | cut -f1)
    echo "📊 Tamaño de la aplicación: $APP_SIZE"
    
    # Crear script de ejecución
    cat > "release/VPN-Manager-Linux-$ARCH_NAME/run.sh" << 'RUN_EOF'
#!/bin/bash
echo "🚀 Ejecutando VPN Manager..."
cd "$(dirname "$0")"
./VPN-Manager-Linux/VPN-Manager-Linux
RUN_EOF
    chmod +x "release/VPN-Manager-Linux-$ARCH_NAME/run.sh"
    
    # Crear archivo desktop
    cat > "release/VPN-Manager-Linux-$ARCH_NAME/vpn-manager.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=VPN Manager
Comment=Gestor de conexiones VPN
Exec=VPN-Manager-Linux
Icon=network-vpn
Terminal=false
Categories=Network;Security;
StartupNotify=true
EOF
    
    # Crear script de instalación
    cat > "release/VPN-Manager-Linux-$ARCH_NAME/install.sh" << 'INSTALL_EOF'
#!/bin/bash
echo "🚀 Instalando VPN Manager..."
echo ""

INSTALL_DIR="/opt/vpn-manager"
DESKTOP_FILE="/usr/share/applications/vpn-manager.desktop"
BIN_LINK="/usr/local/bin/vpn-manager"

# Verificar permisos de root
if [[ $EUID -ne 0 ]]; then
   echo "⚠️  Este script debe ejecutarse como root (usa sudo)"
   exit 1
fi

# Crear directorio de instalación
echo "📁 Creando directorio de instalación..."
mkdir -p "$INSTALL_DIR"

# Copiar archivos
echo "📋 Copiando archivos..."
cp -R VPN-Manager-Linux/* "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/VPN-Manager-Linux"

# Crear enlace en bin
echo "🔗 Creando enlace ejecutable..."
ln -sf "$INSTALL_DIR/VPN-Manager-Linux" "$BIN_LINK"

# Crear archivo desktop
echo "🖥️  Creando entrada de menú..."
cat > "$DESKTOP_FILE" << 'DESKTOP_EOF2'
[Desktop Entry]
Version=1.0
Type=Application
Name=VPN Manager
Comment=Gestor de conexiones VPN
Exec=/opt/vpn-manager/VPN-Manager-Linux
Icon=network-vpn
Terminal=false
Categories=Network;Security;
StartupNotify=true
DESKTOP_EOF2

# Actualizar base de datos de aplicaciones
echo "🔄 Actualizando base de datos de aplicaciones..."
update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo ""
echo "✅ VPN Manager instalado exitosamente!"
echo ""
echo "Puedes ejecutarlo:"
echo "  • Desde el menú de aplicaciones → VPN Manager"
echo "  • Desde terminal: vpn-manager"
echo "  • Desde directorio: $INSTALL_DIR/VPN-Manager-Linux"
echo ""
echo "Para desinstalar:"
echo "  sudo rm -rf $INSTALL_DIR"
echo "  sudo rm -f $BIN_LINK"
echo "  sudo rm -f $DESKTOP_FILE"
INSTALL_EOF
    chmod +x "release/VPN-Manager-Linux-$ARCH_NAME/install.sh"
    
    # Crear README específico para Linux
    cat > "release/VPN-Manager-Linux-$ARCH_NAME/README.md" << 'README_EOF'
# VPN Manager para Linux

Gestor de conexiones VPN multiplataforma con interfaz gráfica.

## 🚀 Instalación

### Opción 1: Instalación del Sistema (Recomendado)
```bash
sudo ./install.sh
```

### Opción 2: Ejecución Portable
```bash
./run.sh
```

### Opción 3: Ejecución Manual
```bash
cd VPN-Manager-Linux
./VPN-Manager-Linux
```

## 📋 Requisitos del Sistema

### Distribuciones Soportadas
- Ubuntu 18.04+
- Debian 9+
- CentOS 7+
- Fedora 30+
- openSUSE Leap 15+
- Arch Linux
- Otras distribuciones con glibc 2.17+

### Dependencias del Sistema
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install openvpn strongswan python3 python3-pyqt5

# CentOS/RHEL/Fedora
sudo yum install openvpn strongswan python3 python3-qt5
# o con dnf:
sudo dnf install openvpn strongswan python3 python3-qt5

# Arch Linux
sudo pacman -S openvpn strongswan python python-pyqt5

# openSUSE
sudo zypper install openvpn strongswan python3 python3-qt5
```

## 🖥️ Uso

### Primera Ejecución
1. La aplicación verificará las dependencias del sistema
2. Solicitará permisos de administrador (sudo)
3. Instalará automáticamente las dependencias faltantes

### Gestión de Conexiones
1. **Añadir conexión**: Botón `Configurar` → Seleccionar archivo `.ovpn`
2. **Conectar**: Seleccionar conexión → Botón `Conectar`
3. **Desconectar**: Botón `Desconectar`

### Icono del Sistema
- **Ubicación**: Bandeja del sistema (system tray)
- **Estados**:
  - 🔴 Desconectado
  - 🟡 Conectando
  - 🟢 Conectado
- **Menú**: Clic derecho para opciones rápidas

## 🔧 Configuración

### Archivos de Configuración
```
~/.vpn-manager/
├── connections/          # Archivos .ovpn
├── logs/                # Logs de conexión
├── license/             # Información de licencia
└── config/              # Configuración de la app
```

### Variables de Entorno
```bash
export VPN_MANAGER_CONFIG=~/.vpn-manager
export VPN_MANAGER_LOG_LEVEL=INFO
```

## 🛠️ Solución de Problemas

### Error "No se puede ejecutar"
```bash
# Verificar permisos
chmod +x VPN-Manager-Linux

# Verificar dependencias
ldd VPN-Manager-Linux
```

### Error "Qt platform plugin not found"
```bash
# Instalar Qt5
sudo apt-get install qt5-default  # Ubuntu/Debian
sudo yum install qt5-qtbase       # CentOS/RHEL
```

### Error "OpenVPN not found"
```bash
# Verificar instalación
which openvpn

# Instalar si no existe
sudo apt-get install openvpn      # Ubuntu/Debian
sudo yum install openvpn          # CentOS/RHEL
```

### Error de permisos de red
```bash
# Añadir usuario al grupo necesario
sudo usermod -a -G dialout $USER
sudo usermod -a -G netdev $USER

# Logout y login nuevamente
```

### Problemas con el entorno gráfico
```bash
# Verificar DISPLAY
echo $DISPLAY

# Para uso remoto con SSH
ssh -X usuario@servidor
# o
ssh -Y usuario@servidor
```

## 📁 Estructura del Paquete

```
VPN-Manager-Linux-x64/
├── VPN-Manager-Linux/           # Aplicación principal
│   ├── VPN-Manager-Linux        # Ejecutable
│   ├── _internal/               # Librerías Python
│   └── ...
├── run.sh                       # Script de ejecución
├── install.sh                   # Script de instalación
├── vpn-manager.desktop          # Archivo desktop
└── README.md                    # Este archivo
```

## ⚡ Características

- ✅ **Interfaz gráfica moderna** con Qt5
- ✅ **Sistema de bandeja** siempre disponible
- ✅ **Gestión automática de dependencias**
- ✅ **Soporte para múltiples conexiones VPN**
- ✅ **Sistema de licencias** (30 días gratis)
- ✅ **Actualizaciones automáticas**
- ✅ **Logs detallados** para debugging
- ✅ **Compatibilidad multiplataforma**

## 📄 Licencia

- **Período de prueba**: 30 días gratuitos
- **Licencia completa**: 5€/mes
- **Gestión de licencias**: Integrada en la aplicación

## 📞 Soporte

- **Email**: yesod3d@gmail.com
- **GitHub**: https://github.com/alumno109192/vpn
- **Documentación**: Incluida en la aplicación

## 🔧 Desarrollo

### Compilar desde fuente
```bash
git clone https://github.com/alumno109192/vpn.git
cd vpn
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python Main.py
```

### Crear paquete
```bash
./build_linux.sh
```

---

**Versión**: 1.0.0  
**Fecha**: $(date +%Y-%m-%d)  
**Arquitectura**: $ARCH_NAME  
**Desarrollador**: Yesod Development
README_EOF
    
    # Crear script de desinstalación
    cat > "release/VPN-Manager-Linux-$ARCH_NAME/uninstall.sh" << 'UNINSTALL_EOF'
#!/bin/bash
echo "🗑️  Desinstalador de VPN Manager"
echo "==============================="
echo ""

# Verificar permisos de root
if [[ $EUID -ne 0 ]]; then
   echo "⚠️  Este script debe ejecutarse como root (usa sudo)"
   exit 1
fi

echo "⚠️  ATENCIÓN: Esto eliminará VPN Manager del sistema"
echo ""
read -p "¿Estás seguro de que deseas continuar? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Desinstalación cancelada."
    exit 0
fi

echo ""
echo "🧹 Eliminando VPN Manager..."

INSTALL_DIR="/opt/vpn-manager"
DESKTOP_FILE="/usr/share/applications/vpn-manager.desktop"
BIN_LINK="/usr/local/bin/vpn-manager"

# Eliminar directorio de instalación
if [ -d "$INSTALL_DIR" ]; then
    echo "📁 Eliminando directorio de instalación..."
    rm -rf "$INSTALL_DIR"
fi

# Eliminar enlace ejecutable
if [ -L "$BIN_LINK" ]; then
    echo "🔗 Eliminando enlace ejecutable..."
    rm -f "$BIN_LINK"
fi

# Eliminar archivo desktop
if [ -f "$DESKTOP_FILE" ]; then
    echo "🖥️  Eliminando entrada de menú..."
    rm -f "$DESKTOP_FILE"
fi

# Actualizar base de datos de aplicaciones
echo "🔄 Actualizando base de datos de aplicaciones..."
update-desktop-database /usr/share/applications/ 2>/dev/null || true

echo ""
echo "✅ VPN Manager desinstalado completamente"
echo ""
echo "Nota: Los datos de usuario se mantienen en ~/.vpn-manager/"
echo "Si deseas eliminarlos también:"
echo "  rm -rf ~/.vpn-manager/"
echo ""
UNINSTALL_EOF
    chmod +x "release/VPN-Manager-Linux-$ARCH_NAME/uninstall.sh"
    
    # Crear tarball
    echo "🗜️  Creando archivo tarball..."
    cd release
    tar -czf "VPN-Manager-Linux-$ARCH_NAME-$(date +%Y.%m.%d).tar.gz" "VPN-Manager-Linux-$ARCH_NAME/"
    cd ..
    
    TAR_SIZE=$(du -sh "release/VPN-Manager-Linux-$ARCH_NAME-$(date +%Y.%m.%d).tar.gz" | cut -f1)
    echo "✅ Tarball creado: release/VPN-Manager-Linux-$ARCH_NAME-$(date +%Y.%m.%d).tar.gz ($TAR_SIZE)"
    
    # Limpiar directorio temporal
    echo "🧹 Limpiando directorio temporal..."
    rm -rf "$TEMP_DIR"
    
    echo ""
    echo "🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!"
    echo "=================================="
    echo ""
    echo "📦 Archivos generados:"
    echo "   ├── release/VPN-Manager-Linux-$ARCH_NAME/"
    echo "   │   ├── VPN-Manager-Linux/ (aplicación)"
    echo "   │   ├── run.sh"
    echo "   │   ├── install.sh"
    echo "   │   ├── uninstall.sh"
    echo "   │   └── README.md"
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
