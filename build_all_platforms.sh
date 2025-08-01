#!/bin/bash

# Script maestro para generar ejecutables en todas las plataformas
# ================================================================

echo "🌍 VPN Manager - Build Script para Todas las Plataformas"
echo "========================================================="

# Obtener la fecha actual
DATE=$(date +%Y.%m.%d)
WORKSPACE_DIR=$(pwd)

echo "📅 Fecha de build: $DATE"
echo "📁 Directorio de trabajo: $WORKSPACE_DIR"

# Función para mostrar el estado de los ejecutables
show_status() {
    echo ""
    echo "📊 Estado actual de los ejecutables:"
    echo "===================================="
    
    # macOS
    if [ -f "release/VPN-Manager-macOS-$DATE.zip" ]; then
        echo "✅ macOS: VPN-Manager-macOS-$DATE.zip (LISTO)"
    else
        echo "❌ macOS: No encontrado"
    fi
    
    # Linux
    if [ -f "release/VPN-Manager-Linux-x64-$DATE.tar.gz" ]; then
        echo "✅ Linux: VPN-Manager-Linux-x64-$DATE.tar.gz (LISTO)"
    else
        echo "❌ Linux: No encontrado"
    fi
    
    # Windows
    if [ -f "release/VPN-Manager-Windows-x64-$DATE.zip" ]; then
        echo "✅ Windows: VPN-Manager-Windows-x64-$DATE.zip (LISTO)"
    else
        echo "⚠️  Windows: Necesita ser generado en máquina Windows"
    fi
}

# Función para generar archivos para Windows
generate_windows_files() {
    echo ""
    echo "🪟 Generando archivos para Windows..."
    echo "===================================="
    
    # Crear directorio para Windows
    mkdir -p "windows-build-kit"
    
    # Copiar archivos necesarios
    echo "📋 Copiando archivos del proyecto..."
    cp Main.py windows-build-kit/
    cp -r dialogs windows-build-kit/
    cp -r threads windows-build-kit/
    cp *.py windows-build-kit/ 2>/dev/null || true
    cp requirements.txt windows-build-kit/ 2>/dev/null || true
    
    # Crear archivo spec para PyInstaller
    cat > windows-build-kit/vpn_manager_windows.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
app_name = "VPN-Manager-Windows"

# Archivos a incluir
added_files = [
    ('dialogs', 'dialogs'),
    ('threads', 'threads'),
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
    icon=None,
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
EOF

    # Crear script de build para Windows
    cat > windows-build-kit/build_windows.bat << 'EOF'
@echo off
REM Script para crear ejecutable Windows - VPN Manager
echo 🪟 Generando ejecutable para Windows...
echo ====================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instala Python 3.8+ desde python.org
    pause
    exit /b 1
)

REM Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv venv_windows
call venv_windows\Scripts\activate.bat

REM Instalar dependencias
echo 📦 Instalando dependencias...
python -m pip install --upgrade pip
pip install PyQt5==5.15.9
pip install PyInstaller==6.14.1
pip install pexpect requests cryptography packaging urllib3 certifi

REM Limpiar builds anteriores
echo 🧹 Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Ejecutar PyInstaller
echo 🔨 Ejecutando PyInstaller...
pyinstaller --clean --noconfirm vpn_manager_windows.spec

REM Verificar resultado
if exist "dist\VPN-Manager-Windows" (
    echo ✅ Ejecutable Windows creado exitosamente!
    echo 📁 Ubicación: dist\VPN-Manager-Windows\
    
    REM Crear script de ejecución
    echo @echo off > dist\VPN-Manager-Windows\run.bat
    echo echo 🚀 Ejecutando VPN Manager... >> dist\VPN-Manager-Windows\run.bat
    echo start "" "VPN-Manager-Windows.exe" >> dist\VPN-Manager-Windows\run.bat
    
    echo.
    echo 🎉 ¡Build completado! Para ejecutar:
    echo    1. Ve a la carpeta: dist\VPN-Manager-Windows\
    echo    2. Haz doble clic en: VPN-Manager-Windows.exe
    echo    3. O ejecuta: run.bat
    
) else (
    echo ❌ Error al crear el ejecutable
    echo Revisa los mensajes de error arriba
)

pause
EOF

    # Crear requirements.txt específico para Windows
    cat > windows-build-kit/requirements.txt << 'EOF'
PyQt5==5.15.9
PyInstaller==6.14.1
pexpect
requests
cryptography
packaging
urllib3
certifi
EOF

    # Crear instrucciones
    cat > windows-build-kit/README-WINDOWS.md << 'EOF'
# VPN Manager - Build para Windows

## Instrucciones para generar el ejecutable en Windows

### Requisitos:
- Windows 10/11
- Python 3.8 o superior
- Git (opcional)

### Pasos:

1. **Copiar archivos**: Copia toda la carpeta `windows-build-kit` a una máquina Windows

2. **Abrir terminal**: Abre Command Prompt o PowerShell como administrador

3. **Navegar a la carpeta**:
   ```cmd
   cd path\to\windows-build-kit
   ```

4. **Ejecutar el build**:
   ```cmd
   build_windows.bat
   ```

5. **Resultado**: El ejecutable se creará en `dist\VPN-Manager-Windows\`

### Archivos generados:
- `VPN-Manager-Windows.exe` - Ejecutable principal
- `run.bat` - Script para ejecutar fácilmente
- Carpetas con dependencias necesarias

### Distribución:
Para distribuir, comprime toda la carpeta `dist\VPN-Manager-Windows\` en un ZIP.

### Solución de problemas:

**Error de Python no encontrado:**
- Instala Python desde https://python.org
- Asegúrate de marcar "Add Python to PATH" durante la instalación

**Error de PyQt5:**
- Ejecuta: `pip install PyQt5==5.15.7` si la versión 5.15.9 falla

**Error de permisos:**
- Ejecuta el Command Prompt como administrador

**Antivirus bloquea el ejecutable:**
- Añade excepción para la carpeta del proyecto
- Es normal que algunos antivirus marquen ejecutables de PyInstaller como sospechosos
EOF

    echo "✅ Kit de build para Windows creado en: windows-build-kit/"
    echo "📋 Archivos incluidos:"
    echo "   - vpn_manager_windows.spec (configuración PyInstaller)"
    echo "   - build_windows.bat (script de build)"
    echo "   - requirements.txt (dependencias)"
    echo "   - README-WINDOWS.md (instrucciones)"
    echo "   - Todos los archivos Python del proyecto"
}

# Función principal
main() {
    echo "🚀 Iniciando proceso de build..."
    
    # Mostrar estado actual
    show_status
    
    # Generar archivos para Windows
    generate_windows_files
    
    echo ""
    echo "📦 Resumen de ejecutables disponibles:"
    echo "======================================"
    
    if [ -f "release/VPN-Manager-macOS-$DATE.zip" ]; then
        echo "✅ macOS: release/VPN-Manager-macOS-$DATE.zip"
    fi
    
    if [ -f "release/VPN-Manager-Linux-x64-$DATE.tar.gz" ]; then
        echo "✅ Linux: release/VPN-Manager-Linux-x64-$DATE.tar.gz"
    fi
    
    echo "📁 Windows: windows-build-kit/ (listo para build en Windows)"
    
    echo ""
    echo "🎯 Para completar el build de Windows:"
    echo "1. Copia la carpeta 'windows-build-kit' a una máquina Windows"
    echo "2. Ejecuta 'build_windows.bat' en esa máquina"
    echo "3. El ejecutable se generará en 'dist/VPN-Manager-Windows/'"
    
    echo ""
    echo "✨ ¡Build script completado!"
}

# Ejecutar función principal
main
