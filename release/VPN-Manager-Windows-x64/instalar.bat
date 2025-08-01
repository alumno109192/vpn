@echo off
REM Instalador VPN Manager para Windows
REM ===================================

title Instalador VPN Manager

echo.
echo    📦 Instalador VPN Manager
echo    ========================
echo.

REM Crear directorio en Archivos de programa
set "INSTALL_DIR=%PROGRAMFILES%\VPN Manager"
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
xcopy /E /I /Q /Y "%~dp0*" "%INSTALL_DIR%\" >nul

REM Crear acceso directo en el escritorio
echo 🔗 Creando acceso directo...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\VPN Manager.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\VPN-Manager-Windows.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

REM Crear entrada en menú inicio
mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\VPN Manager" 2>nul
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\VPN Manager\VPN Manager.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\VPN-Manager-Windows.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo ✅ Instalación completada!
echo.
echo 🚀 Formas de ejecutar VPN Manager:
echo    • Acceso directo en el escritorio
echo    • Menú Inicio ^> VPN Manager
echo    • Directamente: "%INSTALL_DIR%\VPN-Manager-Windows.bat"
echo.
pause
