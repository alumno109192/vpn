#!/usr/bin/env python3
"""
VPN Manager - Simulador de ejecutable Windows
Crea un ejecutable Windows funcional usando técnicas cross-platform
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_windows_executable():
    """Crear un pseudo-ejecutable para Windows"""
    print("🪟 Creando ejecutable simulado para Windows...")
    
    workspace = Path.cwd()
    release_dir = workspace / "release"
    date = datetime.now().strftime("%Y.%m.%d")
    
    # Crear directorio para Windows
    windows_dir = release_dir / f"VPN-Manager-Windows-x64"
    windows_dir.mkdir(exist_ok=True)
    
    # Copiar todos los archivos Python
    print("📋 Copiando archivos del proyecto...")
    
    files_to_copy = [
        "Main.py", "license.py", "license_storage.py", 
        "license_encryptor.py", "license_generator.py", 
        "models.py", "version.py", "auto_updater.py"
    ]
    
    for file_name in files_to_copy:
        src_file = workspace / file_name
        if src_file.exists():
            shutil.copy2(src_file, windows_dir)
            print(f"   ✓ {file_name}")
    
    # Copiar directorios
    for dir_name in ["dialogs", "threads"]:
        src_dir = workspace / dir_name
        dst_dir = windows_dir / dir_name
        if src_dir.exists():
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f"   ✓ {dir_name}/")
    
    # Crear ejecutable batch principal
    batch_content = '''@echo off
REM VPN Manager para Windows
REM ========================

title VPN Manager

echo.
echo    🚀 VPN Manager para Windows
echo    ==========================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado.
    echo.
    echo 📥 Por favor instala Python 3.8+ desde:
    echo    https://www.python.org/downloads/
    echo.
    echo ⚠️  IMPORTANTE: Marca "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)

REM Verificar e instalar dependencias si es necesario
echo 🔍 Verificando dependencias...
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo 📦 Instalando PyQt5...
    pip install PyQt5==5.15.9
)

python -c "import requests" 2>nul
if errorlevel 1 (
    echo 📦 Instalando dependencias adicionales...
    pip install requests cryptography pexpect urllib3 certifi packaging
)

REM Ejecutar la aplicación
echo.
echo 🚀 Iniciando VPN Manager...
echo.

python Main.py

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar VPN Manager
    echo 📧 Contacta soporte: yesod3d@gmail.com
    echo.
    pause
)
'''
    
    with open(windows_dir / "VPN-Manager-Windows.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    # Crear ejecutable PowerShell alternativo
    ps_content = '''# VPN Manager para Windows (PowerShell)
# ====================================

Write-Host ""
Write-Host "    🚀 VPN Manager para Windows" -ForegroundColor Green
Write-Host "    ==========================" -ForegroundColor Green
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado." -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Por favor instala Python 3.8+ desde:" -ForegroundColor Yellow
    Write-Host "   https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE: Marca 'Add Python to PATH' durante la instalación" -ForegroundColor Yellow
    Read-Host "Presiona Enter para continuar"
    exit 1
}

# Verificar dependencias
Write-Host "🔍 Verificando dependencias..." -ForegroundColor Cyan

try {
    python -c "import PyQt5" 2>$null
} catch {
    Write-Host "📦 Instalando PyQt5..." -ForegroundColor Yellow
    pip install PyQt5==5.15.9
}

try {
    python -c "import requests" 2>$null
} catch {
    Write-Host "📦 Instalando dependencias adicionales..." -ForegroundColor Yellow
    pip install requests cryptography pexpect urllib3 certifi packaging
}

# Ejecutar aplicación
Write-Host ""
Write-Host "🚀 Iniciando VPN Manager..." -ForegroundColor Green
Write-Host ""

try {
    python Main.py
} catch {
    Write-Host ""
    Write-Host "❌ Error al ejecutar VPN Manager" -ForegroundColor Red
    Write-Host "📧 Contacta soporte: yesod3d@gmail.com" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
}
'''
    
    with open(windows_dir / "VPN-Manager-Windows.ps1", "w", encoding="utf-8") as f:
        f.write(ps_content)
    
    # Crear instalador automático
    installer_content = '''@echo off
REM Instalador VPN Manager para Windows
REM ===================================

title Instalador VPN Manager

echo.
echo    📦 Instalador VPN Manager
echo    ========================
echo.

REM Crear directorio en Archivos de programa
set "INSTALL_DIR=%PROGRAMFILES%\\VPN Manager"
echo 📁 Directorio de instalación: "%INSTALL_DIR%"

REM Verificar permisos de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ Se requieren permisos de administrador
    echo 🔐 Haz clic derecho y selecciona "Ejecutar como administrador"
    pause
    exit /b 1
)

REM Crear directorio
mkdir "%INSTALL_DIR%" 2>nul

REM Copiar archivos
echo 📋 Copiando archivos...
xcopy /E /I /Q /Y "%~dp0*" "%INSTALL_DIR%\\" >nul

REM Crear acceso directo en el escritorio
echo 🔗 Creando acceso directo...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\VPN Manager.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\VPN-Manager-Windows.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

REM Crear entrada en menú inicio
mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\VPN Manager" 2>nul
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\VPN Manager\\VPN Manager.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\VPN-Manager-Windows.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo ✅ Instalación completada!
echo.
echo 🚀 Formas de ejecutar VPN Manager:
echo    • Acceso directo en el escritorio
echo    • Menú Inicio ^> VPN Manager
echo    • Directamente: "%INSTALL_DIR%\\VPN-Manager-Windows.bat"
echo.
pause
'''
    
    with open(windows_dir / "instalar.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)
    
    # Crear desinstalador
    uninstaller_content = '''@echo off
REM Desinstalador VPN Manager
REM =========================

title Desinstalador VPN Manager

echo.
echo    🗑️  Desinstalador VPN Manager
echo    ============================
echo.

set "INSTALL_DIR=%PROGRAMFILES%\\VPN Manager"

REM Verificar permisos de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ Se requieren permisos de administrador
    echo 🔐 Haz clic derecho y selecciona "Ejecutar como administrador"
    pause
    exit /b 1
)

echo ⚠️  Esto eliminará completamente VPN Manager del sistema
set /p confirm="¿Continuar? (S/N): "
if /i not "%confirm%"=="S" (
    echo ❌ Desinstalación cancelada
    pause
    exit /b 0
)

echo.
echo 🗑️  Eliminando archivos...

REM Eliminar accesos directos
del "%USERPROFILE%\\Desktop\\VPN Manager.lnk" 2>nul
rmdir /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\VPN Manager" 2>nul

REM Eliminar directorio de instalación
rmdir /s /q "%INSTALL_DIR%" 2>nul

echo.
echo ✅ VPN Manager desinstalado correctamente
echo.
pause
'''
    
    with open(windows_dir / "desinstalar.bat", "w", encoding="utf-8") as f:
        f.write(uninstaller_content)
    
    # Crear requirements.txt
    requirements = """PyQt5==5.15.9
requests>=2.25.0
cryptography>=3.0.0
pexpect>=4.8.0
urllib3>=1.26.0
certifi>=2021.0.0
packaging>=20.0"""
    
    with open(windows_dir / "requirements.txt", "w") as f:
        f.write(requirements)
    
    # Crear README
    readme_content = """# VPN Manager para Windows

## 🚀 Inicio Rápido

### Opción 1: Ejecución Directa
1. Haz doble clic en `VPN-Manager-Windows.bat`
2. La aplicación instalará dependencias automáticamente
3. ¡Listo para usar!

### Opción 2: Instalación Completa
1. Haz clic derecho en `instalar.bat` → "Ejecutar como administrador"
2. Sigue las instrucciones del instalador
3. Usa los accesos directos creados

## 📋 Requisitos

- Windows 10/11
- Python 3.8 o superior
- Conexión a Internet (para instalar dependencias)

## 🔧 Instalación de Python

Si no tienes Python instalado:
1. Ve a https://www.python.org/downloads/
2. Descarga Python 3.8+
3. **IMPORTANTE**: Marca "Add Python to PATH" durante la instalación

## 🆘 Soporte

Si tienes problemas:
- Email: yesod3d@gmail.com
- Asegúrate de tener Python instalado correctamente
- Ejecuta como administrador si hay problemas de permisos

## 🗑️ Desinstalación

Para desinstalar completamente:
1. Ejecuta `desinstalar.bat` como administrador
2. Confirma la eliminación
"""
    
    with open(windows_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ Ejecutable Windows creado exitosamente!")
    print(f"📁 Ubicación: {windows_dir}")
    
    # Crear archivo ZIP
    zip_path = release_dir / f"VPN-Manager-Windows-x64-{date}.zip"
    print(f"📦 Creando: {zip_path.name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(windows_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, windows_dir.parent)
                zipf.write(file_path, arc_name)
    
    print(f"✅ Paquete Windows creado: {zip_path.name}")
    return zip_path

if __name__ == "__main__":
    try:
        print("🌍 VPN Manager - Generador de ejecutable Windows")
        print("=" * 50)
        
        zip_file = create_windows_executable()
        
        print("\n🎉 ¡EJECUTABLE WINDOWS COMPLETADO!")
        print("=" * 40)
        print(f"📦 Archivo: {zip_file.name}")
        print("🚀 Instrucciones:")
        print("   1. Envía el ZIP a una máquina Windows")
        print("   2. Extrae el contenido")
        print("   3. Ejecuta VPN-Manager-Windows.bat")
        print("   4. ¡La app funcionará directamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
