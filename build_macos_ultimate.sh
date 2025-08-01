#!/bin/bash

# Script final para crear ejecutable macOS solucionando todos los problemas conocidos
echo "🍎 Script Ultimate para construir ejecutable macOS"
echo "=================================================="

# Crear directorio temporal sin caracteres especiales
TEMP_DIR="/tmp/vpn-manager-build-$(date +%s)"
CURRENT_DIR="$(pwd)"

echo "📁 Creando directorio temporal: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo "📋 Copiando archivos del proyecto..."
# Copiar todos los archivos necesarios, excluyendo directorios problemáticos
rsync -av --exclude='.venv' --exclude='__pycache__' --exclude='build' --exclude='dist' --exclude='*.spec' . "$TEMP_DIR/" 2>/dev/null || cp -R . "$TEMP_DIR/"

# Cambiar al directorio temporal
cd "$TEMP_DIR"

echo "🔧 Configurando entorno Python..."
# Crear un nuevo entorno virtual limpio
python3 -m venv clean_venv
source clean_venv/bin/activate

# Instalar dependencias básicas
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install PyQt5==5.15.9
pip install PyInstaller==6.14.1
pip install pexpect requests cryptography packaging urllib3 certifi

# Verificar instalación de PyQt5
echo "🔍 Verificando PyQt5..."
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')" || {
    echo "❌ Error con PyQt5, intentando alternativa..."
    pip uninstall -y PyQt5
    pip install PyQt5==5.15.7
}

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build/ dist/ *.spec

# Crear archivo spec personalizado para evitar problemas de plugins
echo "📝 Creando archivo spec personalizado..."
cat > vpn_manager.spec << 'SPEC_EOF'
# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Configurar rutas
block_cipher = None
app_name = "VPN Manager"

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

# Imports ocultos específicos para evitar problemas
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

# Módulos a excluir para reducir tamaño
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

app = BUNDLE(
    coll,
    name=f'{app_name}.app',
    icon=None,
    bundle_identifier='com.yesod.vpnmanager',
    info_plist={
        'CFBundleName': app_name,
        'CFBundleDisplayName': app_name,
        'CFBundleIdentifier': 'com.yesod.vpnmanager',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
    },
)
SPEC_EOF

echo "🔨 Ejecutando PyInstaller con spec personalizado..."
pyinstaller --clean --noconfirm vpn_manager.spec

# Verificar resultado
if [ -d "dist/VPN Manager.app" ]; then
    echo "✅ Aplicación macOS creada exitosamente!"
    
    # Volver al directorio original
    cd "$CURRENT_DIR"
    
    # Crear directorio de distribución en ubicación original
    echo "📦 Creando paquete de distribución final..."
    mkdir -p release/VPN-Manager-macOS-Ultimate
    
    # Copiar el resultado
    cp -R "$TEMP_DIR/dist/VPN Manager.app" "release/VPN-Manager-macOS-Ultimate/"
    
    # Obtener información de la aplicación
    APP_SIZE=$(du -sh "release/VPN-Manager-macOS-Ultimate/VPN Manager.app" | cut -f1)
    echo "📊 Tamaño de la aplicación: $APP_SIZE"
    
    # Crear script de instalación
    cat > "release/VPN-Manager-macOS-Ultimate/install.command" << 'INSTALL_EOF'
#!/bin/bash
echo "🚀 Instalando VPN Manager en Applications..."
echo ""

# Verificar si la aplicación ya existe
if [ -d "/Applications/VPN Manager.app" ]; then
    echo "⚠️  VPN Manager ya existe en Applications"
    read -p "¿Deseas reemplazarlo? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Instalación cancelada."
        exit 0
    fi
    echo "🗑️  Eliminando versión anterior..."
    rm -rf "/Applications/VPN Manager.app"
fi

# Copiar la aplicación
echo "📁 Copiando VPN Manager.app a Applications..."
if [ -w "/Applications" ]; then
    cp -R "VPN Manager.app" /Applications/
else
    echo "⚠️  Se necesitan permisos de administrador..."
    sudo cp -R "VPN Manager.app" /Applications/
    sudo chown -R $(whoami):staff "/Applications/VPN Manager.app"
fi

# Quitar atributos de cuarentena
echo "🔓 Configurando permisos de seguridad..."
sudo xattr -rd com.apple.quarantine "/Applications/VPN Manager.app" 2>/dev/null || true

echo ""
echo "✅ ¡VPN Manager instalado exitosamente!"
echo ""
echo "Puedes ejecutarlo desde:"
echo "  • Launchpad → VPN Manager"
echo "  • Finder → Applications → VPN Manager"
echo "  • Spotlight (Cmd+Space) → 'VPN Manager'"
echo ""
echo "Si aparece un aviso de seguridad al ejecutar:"
echo "  System Preferences → Security & Privacy → General → 'Allow Anyway'"
echo ""
read -p "¿Deseas abrir VPN Manager ahora? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    open "/Applications/VPN Manager.app"
fi
INSTALL_EOF
    chmod +x "release/VPN-Manager-macOS-Ultimate/install.command"
    
    # Crear README específico para macOS
    cat > "release/VPN-Manager-macOS-Ultimate/README.md" << 'README_EOF'
# VPN Manager para macOS

Gestor de conexiones VPN multiplataforma con interfaz gráfica moderna.

## 🚀 Instalación Rápida

### Método 1: Instalación Automática (Recomendado)
1. Doble clic en `install.command`
2. Seguir las instrucciones en pantalla
3. La aplicación se instalará en `/Applications/`

### Método 2: Instalación Manual
1. Arrastra `VPN Manager.app` a la carpeta `/Applications/`
2. Ejecuta desde Launchpad o Finder

## 🔐 Configuración de Seguridad

macOS puede mostrar un aviso de seguridad la primera vez que ejecutes la aplicación:

### Si aparece "No se puede abrir porque proviene de un desarrollador no identificado"

**Opción A: System Preferences**
1. Ve a `System Preferences` → `Security & Privacy` → `General`
2. Busca el mensaje sobre VPN Manager
3. Haz clic en `Open Anyway`
4. Confirma con `Open`

**Opción B: Terminal (Avanzado)**
```bash
sudo xattr -rd com.apple.quarantine "/Applications/VPN Manager.app"
```

**Opción C: Desde Finder**
1. Haz clic derecho en `VPN Manager.app`
2. Selecciona `Open`
3. En el diálogo, haz clic en `Open`

## 📱 Uso de la Aplicación

### Primera Ejecución
1. **Verificación de dependencias**: La app verificará e instalará automáticamente OpenVPN y StrongSwan
2. **Configuración inicial**: Se creará la estructura de directorios necesaria

### Gestión de Conexiones
1. **Añadir conexión**: Botón `Configurar` → `Añadir` → Seleccionar archivo `.ovpn`
2. **Conectar**: Seleccionar conexión → Botón `Conectar`
3. **Desconectar**: Botón `Desconectar` o desde el icono del sistema

### Icono del Sistema
- **Ubicación**: Barra de menú superior (junto al reloj)
- **Estados**:
  - 🔴 Desconectado
  - 🟡 Conectando
  - 🟢 Conectado
- **Menú contextual**: Clic derecho para opciones rápidas

## 🛠️ Dependencias del Sistema

La aplicación instalará automáticamente:

### Homebrew (si no está instalado)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### OpenVPN
```bash
brew install openvpn
```

### StrongSwan (para conexiones IKEv2)
```bash
brew install strongswan
```

## 📁 Estructura de Archivos

```
~/VPN-Manager/
├── connections/          # Archivos .ovpn
├── logs/                # Logs de conexión
├── license/             # Información de licencia
└── config/              # Configuración de la app
```

## 🔧 Solución de Problemas

### La aplicación no inicia
1. **Verificar permisos**: Seguir pasos de configuración de seguridad
2. **Terminal**: Abrir Terminal y ejecutar:
   ```bash
   "/Applications/VPN Manager.app/Contents/MacOS/VPN Manager"
   ```
3. **Logs**: Revisar Console.app para errores del sistema

### Error "No se pueden instalar dependencias"
1. **Instalar Homebrew manualmente**:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Instalar dependencias**:
   ```bash
   brew install openvpn strongswan
   ```
3. **Reiniciar VPN Manager**

### Problemas de conexión
1. **Verificar archivo .ovpn**: Asegurar que el archivo está completo y es válido
2. **Permisos de red**: Verificar que la app tiene permisos de red
3. **Firewall**: Revisar configuración del firewall de macOS
4. **Logs**: Revisar logs en `~/VPN-Manager/logs/`

### Error "Command not found: openvpn"
```bash
# Añadir Homebrew al PATH
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# O crear symlink
sudo ln -sf /opt/homebrew/bin/openvpn /usr/local/bin/openvpn
```

## ⚡ Características

- ✅ **Interfaz gráfica moderna** con PyQt5
- ✅ **Sistema de bandeja** siempre disponible
- ✅ **Gestión automática de dependencias**
- ✅ **Soporte para múltiples conexiones VPN**
- ✅ **Sistema de licencias** (30 días gratis)
- ✅ **Actualizaciones automáticas**
- ✅ **Logs detallados** para debugging
- ✅ **Compatibilidad total con macOS**

## 📄 Licencia

- **Período de prueba**: 30 días gratuitos
- **Licencia completa**: 5€/mes
- **Gestión de licencias**: Integrada en la aplicación

## 📞 Soporte

- **Email**: yesod3d@gmail.com
- **GitHub**: https://github.com/alumno109192/vpn
- **Documentación**: Incluida en la aplicación

## 📋 Requisitos del Sistema

- **macOS**: 10.14 (Mojave) o superior
- **Arquitectura**: Intel x64 / Apple Silicon (M1/M2/M3)
- **RAM**: 512 MB mínimo, 1 GB recomendado
- **Espacio**: 200 MB para la aplicación + dependencias
- **Permisos**: Administrador para instalar dependencias del sistema

---

**Versión**: 1.0.0  
**Fecha**: $(date +%Y-%m-%d)  
**Desarrollador**: Yesod Development
README_EOF
    
    # Crear script de desinstalación
    cat > "release/VPN-Manager-macOS-Ultimate/uninstall.command" << 'UNINSTALL_EOF'
#!/bin/bash
echo "🗑️  Desinstalador de VPN Manager"
echo "==============================="
echo ""
echo "⚠️  ATENCIÓN: Esto eliminará VPN Manager y todos sus datos"
echo ""
read -p "¿Estás seguro de que deseas continuar? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Desinstalación cancelada."
    exit 0
fi

echo ""
echo "🧹 Eliminando VPN Manager..."

# Cerrar la aplicación si está ejecutándose
killall "VPN Manager" 2>/dev/null || true

# Eliminar aplicación
if [ -d "/Applications/VPN Manager.app" ]; then
    echo "📱 Eliminando aplicación..."
    sudo rm -rf "/Applications/VPN Manager.app"
fi

# Eliminar datos de usuario (opcional)
echo ""
read -p "¿Deseas eliminar también los datos de usuario (conexiones, logs, etc.)? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📁 Eliminando datos de usuario..."
    rm -rf ~/VPN-Manager/ 2>/dev/null || true
    rm -rf ~/.vpn-manager/ 2>/dev/null || true
fi

echo ""
echo "✅ VPN Manager desinstalado completamente"
echo ""
echo "Nota: Las dependencias del sistema (OpenVPN, StrongSwan) no se han eliminado."
echo "Si deseas eliminarlas también:"
echo "  brew uninstall openvpn strongswan"
echo ""
read -p "Presiona Enter para continuar..."
UNINSTALL_EOF
    chmod +x "release/VPN-Manager-macOS-Ultimate/uninstall.command"
    
    # Crear ZIP final
    echo "🗜️  Creando archivo ZIP para distribución..."
    cd release
    zip -r "VPN-Manager-macOS-$(date +%Y.%m.%d).zip" "VPN-Manager-macOS-Ultimate/"
    cd ..
    
    ZIP_SIZE=$(du -sh "release/VPN-Manager-macOS-$(date +%Y.%m.%d).zip" | cut -f1)
    echo "✅ ZIP creado: release/VPN-Manager-macOS-$(date +%Y.%m.%d).zip ($ZIP_SIZE)"
    
    # Limpiar directorio temporal
    echo "🧹 Limpiando directorio temporal..."
    rm -rf "$TEMP_DIR"
    
    echo ""
    echo "🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!"
    echo "=================================="
    echo ""
    echo "📦 Archivos generados:"
    echo "   ├── release/VPN-Manager-macOS-Ultimate/"
    echo "   │   ├── VPN Manager.app"
    echo "   │   ├── install.command"
    echo "   │   ├── uninstall.command"
    echo "   │   └── README.md"
    echo "   └── release/VPN-Manager-macOS-$(date +%Y.%m.%d).zip"
    echo ""
    echo "🧪 Para probar la aplicación:"
    echo "   cd release/VPN-Manager-macOS-Ultimate && ./install.command"
    echo ""
    echo "📤 Para distribuir:"
    echo "   Comparte el archivo: release/VPN-Manager-macOS-$(date +%Y.%m.%d).zip"
    echo ""
    echo "✨ La aplicación está lista para uso en macOS!"
    
else
    echo "❌ Error: No se pudo crear la aplicación macOS"
    cd "$CURRENT_DIR"
    rm -rf "$TEMP_DIR"
    exit 1
fi
