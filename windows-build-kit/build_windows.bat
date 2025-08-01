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
