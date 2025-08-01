@echo off
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
