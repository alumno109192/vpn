#!/bin/bash

# Script para generar ejecutable en Linux
echo "🐧 Generando ejecutable para Linux..."
echo "===================================="

# Verificar que estamos en Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Este script solo funciona en Linux"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    echo "🔧 Activando entorno virtual..."
    source .venv/bin/activate
fi

# Instalar dependencias del sistema si es necesario
echo "📦 Verificando dependencias del sistema..."
if ! dpkg -l | grep -q python3-dev; then
    echo "Instalando dependencias del sistema..."
    sudo apt-get update
    sudo apt-get install -y python3-dev python3-pip
fi

# Verificar PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install PyInstaller
fi

# Verificar PyQt5
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "📦 Instalando PyQt5..."
    sudo apt-get install -y python3-pyqt5 python3-pyqt5.qtwidgets
    pip3 install PyQt5==5.15.11
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build/ dist/ *.spec

# Crear archivo spec personalizado para Linux
echo "📝 Creando archivo .spec personalizado..."
cat > vpn-manager-linux.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('dialogs', 'dialogs'),
        ('threads', 'threads'),
        ('version.py', '.'),
        ('auto_updater.py', '.'),
        ('license.py', '.'),
        ('license_storage.py', '.'),
        ('license_encryptor.py', '.'),
        ('license_generator.py', '.'),
        ('models.py', '.'),
    ],
    hiddenimports=[
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
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VPN-Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Ejecutar PyInstaller
echo "🔨 Ejecutando PyInstaller..."
python3 -m PyInstaller vpn-manager-linux.spec --noconfirm --clean

# Verificar que se creó el ejecutable
if [ -f "dist/VPN-Manager" ]; then
    echo "✅ Ejecutable Linux creado exitosamente!"
    
    # Hacer ejecutable
    chmod +x "dist/VPN-Manager"
    
    # Obtener información del ejecutable
    EXE_SIZE=$(du -sh "dist/VPN-Manager" | cut -f1)
    echo "📊 Tamaño del ejecutable: $EXE_SIZE"
    
    # Crear paquete de distribución
    echo "📦 Creando paquete de distribución..."
    mkdir -p release/VPN-Manager-Linux
    cp "dist/VPN-Manager" "release/VPN-Manager-Linux/"
    
    # Crear archivo desktop
    cat > "release/VPN-Manager-Linux/vpn-manager.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=VPN Manager
Comment=Gestiona conexiones VPN
Exec=/opt/vpn-manager/VPN-Manager
Icon=/opt/vpn-manager/vpn-manager.png
Terminal=false
StartupNotify=true
Categories=Network;Security;
DESKTOP_EOF
    
    # Crear script de instalación
    cat > "release/VPN-Manager-Linux/install.sh" << 'INSTALL_EOF'
#!/bin/bash
echo "🚀 Instalando VPN Manager..."

# Verificar permisos de root
if [[ $EUID -ne 0 ]]; then
   echo "Este script debe ejecutarse como root (sudo ./install.sh)"
   exit 1
fi

# Crear directorio de instalación
mkdir -p /opt/vpn-manager

# Copiar ejecutable
cp VPN-Manager /opt/vpn-manager/
chmod +x /opt/vpn-manager/VPN-Manager

# Instalar entrada de escritorio
cp vpn-manager.desktop /usr/share/applications/

# Instalar dependencias del sistema
echo "📦 Instalando dependencias del sistema..."
apt-get update
apt-get install -y openvpn strongswan python3-pyqt5

# Crear enlace simbólico
ln -sf /opt/vpn-manager/VPN-Manager /usr/local/bin/vpn-manager

echo "✅ VPN Manager instalado exitosamente!"
echo ""
echo "Puedes ejecutarlo desde:"
echo "  - Menú de aplicaciones (Network → VPN Manager)"
echo "  - Terminal: vpn-manager"
echo "  - Directamente: /opt/vpn-manager/VPN-Manager"
INSTALL_EOF
    chmod +x "release/VPN-Manager-Linux/install.sh"
    
    # Crear script de desinstalación
    cat > "release/VPN-Manager-Linux/uninstall.sh" << 'UNINSTALL_EOF'
#!/bin/bash
echo "🗑️  Desinstalando VPN Manager..."

# Verificar permisos de root
if [[ $EUID -ne 0 ]]; then
   echo "Este script debe ejecutarse como root (sudo ./uninstall.sh)"
   exit 1
fi

# Eliminar archivos
rm -rf /opt/vpn-manager
rm -f /usr/share/applications/vpn-manager.desktop
rm -f /usr/local/bin/vpn-manager

echo "✅ VPN Manager desinstalado exitosamente"
UNINSTALL_EOF
    chmod +x "release/VPN-Manager-Linux/uninstall.sh"
    
    # Crear README
    cat > "release/VPN-Manager-Linux/README.md" << 'README_EOF'
# VPN Manager para Linux

## Instalación

### Instalación automática (recomendado)
```bash
sudo ./install.sh
```

### Instalación manual
1. Copia `VPN-Manager` a `/opt/vpn-manager/`
2. Instala dependencias: `sudo apt-get install openvpn strongswan python3-pyqt5`
3. Copia `vpn-manager.desktop` a `/usr/share/applications/`

## Dependencias del sistema

Antes de ejecutar, asegúrate de tener instalado:
```bash
sudo apt-get install openvpn strongswan python3-pyqt5
```

## Ejecución

Después de la instalación:
- Desde el menú: Network → VPN Manager
- Desde terminal: `vpn-manager`
- Ejecutable directo: `/opt/vpn-manager/VPN-Manager`

## Uso

1. **Primera ejecución**: Introducir contraseña de sudo cuando se solicite
2. **Configurar**: Añadir conexiones VPN desde el botón "Configurar"
3. **Conectar**: Seleccionar conexión y hacer clic en "Conectar"
4. **Sistema tray**: Acceder a funciones desde el icono de la bandeja

## Desinstalación

```bash
sudo ./uninstall.sh
```

## Soporte

- Email: yesod3d@gmail.com
- GitHub: https://github.com/alumno109192/vpn

## Compatibilidad

- Ubuntu 20.04+
- Debian 11+
- Otras distribuciones basadas en Debian

## Licencia

Período de prueba: 30 días gratuitos
Licencia completa: 5€/mes
README_EOF
    
    # Crear archivo de lanzamiento directo
    cat > "release/VPN-Manager-Linux/run.sh" << 'RUN_EOF'
#!/bin/bash
# Script para ejecutar VPN Manager sin instalación
echo "🚀 Ejecutando VPN Manager..."

# Verificar dependencias mínimas
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no encontrado. Instala con: sudo apt-get install python3"
    exit 1
fi

# Verificar PyQt5
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "❌ PyQt5 no encontrado. Instala con: sudo apt-get install python3-pyqt5"
    exit 1
fi

# Ejecutar VPN Manager
./VPN-Manager
RUN_EOF
    chmod +x "release/VPN-Manager-Linux/run.sh"
    
    # Crear ZIP final
    echo "🗜️  Creando archivo ZIP..."
    cd release
    zip -r "VPN-Manager-Linux.zip" "VPN-Manager-Linux/"
    cd ..
    
    ZIP_SIZE=$(du -sh "release/VPN-Manager-Linux.zip" | cut -f1)
    echo "✅ ZIP creado: release/VPN-Manager-Linux.zip ($ZIP_SIZE)"
    
    echo ""
    echo "🎉 ¡Proceso completado exitosamente!"
    echo ""
    echo "📋 Archivos generados:"
    echo "   - dist/VPN-Manager (ejecutable Linux)"
    echo "   - release/VPN-Manager-Linux/ (paquete de distribución)"
    echo "   - release/VPN-Manager-Linux.zip (archivo final para distribución)"
    echo ""
    echo "🧪 Para probar:"
    echo "   ./dist/VPN-Manager"
    echo ""
    echo "📤 Para distribuir:"
    echo "   Comparte el archivo: release/VPN-Manager-Linux.zip"
    
else
    echo "❌ Error: No se pudo crear el ejecutable Linux"
    echo "Revisa los logs anteriores para más detalles"
    exit 1
fi
