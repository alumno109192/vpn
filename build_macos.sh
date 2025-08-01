#!/bin/bash

# Script específico para generar ejecutable en macOS
# Maneja las configuraciones específicas de Qt y PyQt5

echo "🍎 Generando ejecutable para macOS..."
echo "=================================="

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script solo funciona en macOS"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    echo "🔧 Activando entorno virtual..."
    source .venv/bin/activate
fi

# Verificar PyInstaller
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip install PyInstaller
fi

# Verificar PyQt5
if ! python -c "import PyQt5" 2>/dev/null; then
    echo "📦 Instalando PyQt5..."
    pip install PyQt5==5.15.11
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build/ dist/ *.spec

# Configurar variables de entorno para PyQt5
echo "⚙️  Configurando entorno Qt..."
export QT_PLUGIN_PATH=$(python -c "import PyQt5; import os; print(os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins'))")
export QT_QPA_PLATFORM_PLUGIN_PATH="$QT_PLUGIN_PATH/platforms"

echo "Qt Plugin Path: $QT_PLUGIN_PATH"

# Crear archivo spec personalizado para macOS
echo "📝 Creando archivo .spec personalizado..."
cat > vpn-manager-macos.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

import os
import PyQt5

block_cipher = None

# Obtener ruta de PyQt5
pyqt5_path = os.path.dirname(PyQt5.__file__)
qt5_path = os.path.join(pyqt5_path, 'Qt5')

# Binarios de Qt para incluir
qt_binaries = []
if os.path.exists(qt5_path):
    # Incluir plugins de Qt
    plugins_path = os.path.join(qt5_path, 'plugins')
    if os.path.exists(plugins_path):
        for root, dirs, files in os.walk(plugins_path):
            for file in files:
                if file.endswith('.dylib'):
                    src = os.path.join(root, file)
                    dst = os.path.relpath(src, qt5_path)
                    qt_binaries.append((src, dst))

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=qt_binaries,
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
        (os.path.join(qt5_path, 'plugins'), 'PyQt5/Qt5/plugins'),
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
    [],
    exclude_binaries=True,
    name='VPN Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
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
    name='VPN Manager',
)

app = BUNDLE(
    coll,
    name='VPN Manager.app',
    icon=None,
    bundle_identifier='com.vpnmanager.app',
    version='1.0.0',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleDisplayName': 'VPN Manager',
        'CFBundleName': 'VPN Manager',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'NSAppleEventsUsageDescription': 'Esta aplicación necesita permisos para gestionar conexiones VPN.',
        'NSSystemAdministrationUsageDescription': 'Esta aplicación necesita permisos de administrador para configurar conexiones VPN.',
    },
)
EOF

# Ejecutar PyInstaller
echo "🔨 Ejecutando PyInstaller..."
pyinstaller vpn-manager-macos.spec --noconfirm --clean

# Verificar que se creó la aplicación
if [ -d "dist/VPN Manager.app" ]; then
    echo "✅ Aplicación macOS creada exitosamente!"
    
    # Obtener información de la aplicación
    APP_SIZE=$(du -sh "dist/VPN Manager.app" | cut -f1)
    echo "📊 Tamaño de la aplicación: $APP_SIZE"
    
    # Verificar estructura interna
    echo "🔍 Verificando estructura de la aplicación..."
    if [ -f "dist/VPN Manager.app/Contents/MacOS/VPN Manager" ]; then
        echo "✅ Ejecutable principal encontrado"
    else
        echo "❌ Ejecutable principal no encontrado"
    fi
    
    if [ -d "dist/VPN Manager.app/Contents/Resources" ]; then
        echo "✅ Directorio Resources encontrado"
    else
        echo "❌ Directorio Resources no encontrado"
    fi
    
    # Hacer la aplicación ejecutable
    chmod +x "dist/VPN Manager.app/Contents/MacOS/VPN Manager"
    
    # Crear paquete de distribución
    echo "📦 Creando paquete de distribución..."
    mkdir -p release/VPN-Manager-macOS
    cp -R "dist/VPN Manager.app" "release/VPN-Manager-macOS/"
    
    # Crear script de instalación
    cat > "release/VPN-Manager-macOS/install.command" << 'INSTALL_EOF'
#!/bin/bash
echo "🚀 Instalando VPN Manager..."
cp -R "VPN Manager.app" /Applications/
echo "✅ VPN Manager instalado en /Applications/"
echo "Puedes ejecutarlo desde Launchpad o Finder"
echo "Si aparece un aviso de seguridad, ve a:"
echo "System Preferences → Security & Privacy → General"
echo "Y permite la ejecución de VPN Manager"
read -p "Presiona Enter para continuar..."
INSTALL_EOF
    chmod +x "release/VPN-Manager-macOS/install.command"
    
    # Crear README
    cat > "release/VPN-Manager-macOS/README.md" << 'README_EOF'
# VPN Manager para macOS

## Instalación

### Opción 1: Script automático
1. Haz doble clic en `install.command`
2. Sigue las instrucciones en pantalla

### Opción 2: Manual
1. Arrastra "VPN Manager.app" a la carpeta Applications
2. Ejecuta desde Launchpad o Finder

## Primera ejecución

Si aparece un aviso de seguridad:
1. Ve a System Preferences → Security & Privacy → General
2. Haz clic en "Allow Anyway" junto a VPN Manager
3. Ejecuta la aplicación nuevamente

## Requisitos

- macOS 10.14 o superior
- OpenVPN y StrongSwan (se instalan automáticamente)
- Permisos de administrador para conexiones VPN

## Uso

1. **Primera vez**: La aplicación verificará e instalará dependencias necesarias
2. **Configurar**: Haz clic en "Configurar" para agregar conexiones VPN
3. **Conectar**: Selecciona una conexión y haz clic en "Conectar"
4. **Menú del sistema**: Accede a funciones desde el icono en la barra de menú

## Soporte

- Email: yesod3d@gmail.com
- GitHub: https://github.com/alumno109192/vpn

## Licencia

Esta aplicación requiere licencia para uso completo.
Período de prueba: 30 días gratuitos.
README_EOF
    
    # Crear ZIP final
    echo "🗜️  Creando archivo ZIP..."
    cd release
    zip -r "VPN-Manager-macOS.zip" "VPN-Manager-macOS/"
    cd ..
    
    ZIP_SIZE=$(du -sh "release/VPN-Manager-macOS.zip" | cut -f1)
    echo "✅ ZIP creado: release/VPN-Manager-macOS.zip ($ZIP_SIZE)"
    
    echo ""
    echo "🎉 ¡Proceso completado exitosamente!"
    echo ""
    echo "📋 Archivos generados:"
    echo "   - dist/VPN Manager.app (aplicación macOS)"
    echo "   - release/VPN-Manager-macOS/ (paquete de distribución)"
    echo "   - release/VPN-Manager-macOS.zip (archivo final para distribución)"
    echo ""
    echo "🧪 Para probar:"
    echo "   open 'dist/VPN Manager.app'"
    echo ""
    echo "📤 Para distribuir:"
    echo "   Comparte el archivo: release/VPN-Manager-macOS.zip"
    
else
    echo "❌ Error: No se pudo crear la aplicación macOS"
    echo "Revisa los logs anteriores para más detalles"
    exit 1
fi
