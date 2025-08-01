@echo off
REM Desinstalador VPN Manager
REM =========================

title Desinstalador VPN Manager

echo.
echo    🗑️  Desinstalador VPN Manager
echo    ============================
echo.

set "INSTALL_DIR=%PROGRAMFILES%\VPN Manager"

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
del "%USERPROFILE%\Desktop\VPN Manager.lnk" 2>nul
rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\VPN Manager" 2>nul

REM Eliminar directorio de instalación
rmdir /s /q "%INSTALL_DIR%" 2>nul

echo.
echo ✅ VPN Manager desinstalado correctamente
echo.
pause
