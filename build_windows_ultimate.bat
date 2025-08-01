@echo off
REM Script para crear ejecutable Windows
echo 🪟 Script para crear ejecutable Windows
echo ====================================

REM Detectar arquitectura
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set ARCH_NAME=x64
) else if "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
    set ARCH_NAME=arm64
) else (
    set ARCH_NAME=x86
)

echo 📋 Arquitectura detectada: %PROCESSOR_ARCHITECTURE% (%ARCH_NAME%)

REM Crear directorio temporal
set TEMP_DIR=%TEMP%\vpn-manager-windows-build-%RANDOM%
set CURRENT_DIR=%CD%

echo 📁 Creando directorio temporal: %TEMP_DIR%
mkdir "%TEMP_DIR%"

echo 📋 Copiando archivos del proyecto...
xcopy /E /I /Q "%CURRENT_DIR%" "%TEMP_DIR%" >nul 2>&1

REM Cambiar al directorio temporal
cd /d "%TEMP_DIR%"

echo 🔧 Configurando entorno Python...
REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor, instala Python 3.8+ desde python.org
    pause
    exit /b 1
)

REM Crear entorno virtual limpio
echo 📦 Creando entorno virtual...
python -m venv windows_venv
call windows_venv\Scripts\activate.bat

REM Instalar dependencias
echo 📦 Instalando dependencias...
python -m pip install --upgrade pip
pip install PyQt5==5.15.9
pip install PyInstaller==6.14.1
pip install pexpect requests cryptography packaging urllib3 certifi

REM Verificar PyQt5
echo 🔍 Verificando PyQt5...
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')" 2>nul
if errorlevel 1 (
    echo ❌ Error con PyQt5, intentando alternativa...
    pip uninstall -y PyQt5
    pip install PyQt5==5.15.7
)

REM Limpiar builds anteriores
echo 🧹 Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

REM Crear archivo spec personalizado
echo 📝 Creando archivo spec personalizado...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo import sys
echo import os
echo.
echo block_cipher = None
echo app_name = "VPN-Manager-Windows"
echo.
echo # Archivos a incluir
echo added_files = [
echo     ('dialogs', 'dialogs'^),
echo     ('threads', 'threads'^),
echo     ('version.py', '.'^),
echo     ('auto_updater.py', '.'^),
echo     ('license.py', '.'^),
echo     ('license_storage.py', '.'^),
echo     ('license_encryptor.py', '.'^),
echo     ('license_generator.py', '.'^),
echo     ('models.py', '.'^),
echo ]
echo.
echo # Imports ocultos
echo hidden_imports = [
echo     'PyQt5.sip',
echo     'PyQt5.QtCore',
echo     'PyQt5.QtGui',
echo     'PyQt5.QtWidgets',
echo     'pexpect',
echo     'requests',
echo     'cryptography',
echo     'packaging',
echo     'urllib3',
echo     'certifi',
echo     'json',
echo     'threading',
echo     'subprocess',
echo     'os',
echo     'sys',
echo     'platform',
echo     'pathlib',
echo ]
echo.
echo # Módulos a excluir
echo excludes = [
echo     'tkinter',
echo     'matplotlib',
echo     'numpy',
echo     'scipy',
echo     'pandas',
echo     'PIL',
echo     'cv2',
echo     'torch',
echo     'tensorflow',
echo ]
echo.
echo a = Analysis(
echo     ['Main.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=added_files,
echo     hiddenimports=hidden_imports,
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=excludes,
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE(
echo     pyz,
echo     a.scripts,
echo     [],
echo     exclude_binaries=True,
echo     name=app_name,
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     icon=None,
echo ^)
echo.
echo coll = COLLECT(
echo     exe,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     name=app_name,
echo ^)
) > vpn_manager_windows.spec

echo 🔨 Ejecutando PyInstaller...
pyinstaller --clean --noconfirm vpn_manager_windows.spec

REM Verificar resultado
if exist "dist\VPN-Manager-Windows" (
    echo ✅ Ejecutable Windows creado exitosamente!
    
    REM Volver al directorio original
    cd /d "%CURRENT_DIR%"
    
    REM Crear directorio de distribución
    echo 📦 Creando paquete de distribución...
    if not exist "release\VPN-Manager-Windows-%ARCH_NAME%" mkdir "release\VPN-Manager-Windows-%ARCH_NAME%"
    
    REM Copiar el resultado
    xcopy /E /I /Q "%TEMP_DIR%\dist\VPN-Manager-Windows" "release\VPN-Manager-Windows-%ARCH_NAME%\VPN-Manager-Windows" >nul
    
    REM Crear script de ejecución
    (
    echo @echo off
    echo echo 🚀 Ejecutando VPN Manager...
    echo cd /d "%%~dp0"
    echo start "" "VPN-Manager-Windows\VPN-Manager-Windows.exe"
    ) > "release\VPN-Manager-Windows-%ARCH_NAME%\run.bat"
    
    REM Crear script de instalación
    (
    echo @echo off
    echo title Instalador VPN Manager
    echo echo 🚀 Instalando VPN Manager...
    echo echo.
    echo.
    echo set INSTALL_DIR=%%ProgramFiles%%\VPN Manager
    echo set DESKTOP_LINK=%%USERPROFILE%%\Desktop\VPN Manager.lnk
    echo set START_MENU_LINK=%%ProgramData%%\Microsoft\Windows\Start Menu\Programs\VPN Manager.lnk
    echo.
    echo REM Verificar permisos de administrador
    echo net session ^>nul 2^>^&1
    echo if %%errorlevel%% neq 0 ^(
    echo     echo ⚠️  Este script debe ejecutarse como Administrador
    echo     echo Haz clic derecho y selecciona "Ejecutar como administrador"
    echo     pause
    echo     exit /b 1
    echo ^)
    echo.
    echo REM Crear directorio de instalación
    echo echo 📁 Creando directorio de instalación...
    echo if not exist "%%INSTALL_DIR%%" mkdir "%%INSTALL_DIR%%"
    echo.
    echo REM Copiar archivos
    echo echo 📋 Copiando archivos...
    echo xcopy /E /I /Q "VPN-Manager-Windows" "%%INSTALL_DIR%%" ^>nul
    echo.
    echo REM Crear acceso directo en el escritorio
    echo echo 🖥️  Creando acceso directo en el escritorio...
    echo powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%%DESKTOP_LINK%%'^); $Shortcut.TargetPath = '%%INSTALL_DIR%%\VPN-Manager-Windows.exe'; $Shortcut.WorkingDirectory = '%%INSTALL_DIR%%'; $Shortcut.Save(^)"
    echo.
    echo REM Crear acceso directo en el menú inicio
    echo echo 📱 Creando acceso directo en el menú inicio...
    echo powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%%START_MENU_LINK%%'^); $Shortcut.TargetPath = '%%INSTALL_DIR%%\VPN-Manager-Windows.exe'; $Shortcut.WorkingDirectory = '%%INSTALL_DIR%%'; $Shortcut.Save(^)"
    echo.
    echo echo.
    echo echo ✅ VPN Manager instalado exitosamente!
    echo echo.
    echo echo Puedes ejecutarlo desde:
    echo echo   • Escritorio → VPN Manager
    echo echo   • Menú Inicio → VPN Manager
    echo echo   • Directorio: %%INSTALL_DIR%%
    echo echo.
    echo set /p "OPEN_NOW=¿Deseas abrir VPN Manager ahora? (Y/n): "
    echo if /i "%%OPEN_NOW%%"=="n" goto :end
    echo if /i "%%OPEN_NOW%%"=="no" goto :end
    echo start "" "%%INSTALL_DIR%%\VPN-Manager-Windows.exe"
    echo :end
    echo pause
    ) > "release\VPN-Manager-Windows-%ARCH_NAME%\install.bat"
    
    REM Crear README específico para Windows
    (
    echo # VPN Manager para Windows
    echo.
    echo Gestor de conexiones VPN multiplataforma con interfaz gráfica.
    echo.
    echo ## 🚀 Instalación
    echo.
    echo ### Opción 1: Instalación del Sistema ^(Recomendado^)
    echo 1. Haz clic derecho en `install.bat`
    echo 2. Selecciona "Ejecutar como administrador"
    echo 3. Sigue las instrucciones en pantalla
    echo.
    echo ### Opción 2: Ejecución Portable
    echo 1. Doble clic en `run.bat`
    echo 2. O ejecuta directamente `VPN-Manager-Windows\VPN-Manager-Windows.exe`
    echo.
    echo ## 📋 Requisitos del Sistema
    echo.
    echo ### Versiones de Windows Soportadas
    echo - Windows 10 ^(versión 1903 o superior^)
    echo - Windows 11 ^(todas las versiones^)
    echo - Windows Server 2019/2022
    echo.
    echo ### Dependencias del Sistema
    echo - Microsoft Visual C++ Redistributable 2015-2022
    echo - OpenVPN ^(se descarga automáticamente si no está instalado^)
    echo - TAP-Windows Adapter ^(incluido con OpenVPN^)
    echo.
    echo ## 🖥️ Uso
    echo.
    echo ### Primera Ejecución
    echo 1. La aplicación verificará las dependencias del sistema
    echo 2. Descargará e instalará OpenVPN si no está presente
    echo 3. Configurará el adaptador TAP-Windows
    echo.
    echo ### Gestión de Conexiones
    echo 1. **Añadir conexión**: Botón `Configurar` → Seleccionar archivo `.ovpn`
    echo 2. **Conectar**: Seleccionar conexión → Botón `Conectar`
    echo 3. **Desconectar**: Botón `Desconectar`
    echo.
    echo ### Icono del Sistema
    echo - **Ubicación**: Bandeja del sistema ^(junto al reloj^)
    echo - **Estados**:
    echo   - 🔴 Desconectado
    echo   - 🟡 Conectando
    echo   - 🟢 Conectado
    echo - **Menú**: Clic derecho para opciones rápidas
    echo.
    echo ## 🔧 Configuración
    echo.
    echo ### Archivos de Configuración
    echo ```
    echo %%APPDATA%%\VPN-Manager\
    echo ├── connections\          # Archivos .ovpn
    echo ├── logs\                # Logs de conexión
    echo ├── license\             # Información de licencia
    echo └── config\              # Configuración de la app
    echo ```
    echo.
    echo ### Variables de Entorno
    echo - `VPN_MANAGER_CONFIG`: Directorio de configuración personalizado
    echo - `VPN_MANAGER_LOG_LEVEL`: Nivel de logging ^(DEBUG, INFO, WARNING, ERROR^)
    echo.
    echo ## 🛠️ Solución de Problemas
    echo.
    echo ### Error "No se puede ejecutar la aplicación"
    echo 1. **Verificar arquitectura**: Descargar la versión correcta ^(x64/x86^)
    echo 2. **Instalar Visual C++ Redistributable**:
    echo    - Descargar desde Microsoft
    echo    - Instalar versión 2015-2022
    echo.
    echo ### Error "OpenVPN no encontrado"
    echo 1. **Instalación manual**:
    echo    - Descargar OpenVPN desde openvpn.net
    echo    - Instalar con permisos de administrador
    echo    - Reiniciar VPN Manager
    echo.
    echo ### Error "TAP-Windows Adapter"
    echo 1. **Reinstalar adaptador**:
    echo    - Panel de Control → Programas → OpenVPN
    echo    - Reparar instalación
    echo    - O reinstalar completamente
    echo.
    echo ### Error de permisos
    echo 1. **Ejecutar como administrador**:
    echo    - Clic derecho en VPN-Manager-Windows.exe
    echo    - "Ejecutar como administrador"
    echo.
    echo ### Problemas con el firewall
    echo 1. **Configurar Windows Defender**:
    echo    - Añadir excepción para VPN Manager
    echo    - Permitir comunicación de OpenVPN
    echo.
    echo ## 📁 Estructura del Paquete
    echo.
    echo ```
    echo VPN-Manager-Windows-%ARCH_NAME%\
    echo ├── VPN-Manager-Windows\         # Aplicación principal
    echo │   ├── VPN-Manager-Windows.exe  # Ejecutable
    echo │   ├── _internal\               # Librerías Python
    echo │   └── ...
    echo ├── run.bat                      # Script de ejecución
    echo ├── install.bat                  # Script de instalación
    echo └── README.md                    # Este archivo
    echo ```
    echo.
    echo ## ⚡ Características
    echo.
    echo - ✅ **Interfaz gráfica moderna** con Qt5
    echo - ✅ **Sistema de bandeja** siempre disponible
    echo - ✅ **Gestión automática de dependencias**
    echo - ✅ **Soporte para múltiples conexiones VPN**
    echo - ✅ **Sistema de licencias** ^(30 días gratis^)
    echo - ✅ **Actualizaciones automáticas**
    echo - ✅ **Logs detallados** para debugging
    echo - ✅ **Compatibilidad con Windows 10/11**
    echo.
    echo ## 📄 Licencia
    echo.
    echo - **Período de prueba**: 30 días gratuitos
    echo - **Licencia completa**: 5€/mes
    echo - **Gestión de licencias**: Integrada en la aplicación
    echo.
    echo ## 📞 Soporte
    echo.
    echo - **Email**: yesod3d@gmail.com
    echo - **GitHub**: https://github.com/alumno109192/vpn
    echo - **Documentación**: Incluida en la aplicación
    echo.
    echo ---
    echo.
    echo **Versión**: 1.0.0  
    echo **Fecha**: %DATE%  
    echo **Arquitectura**: %ARCH_NAME%  
    echo **Desarrollador**: Yesod Development
    ) > "release\VPN-Manager-Windows-%ARCH_NAME%\README.md"
    
    REM Crear script de desinstalación
    (
    echo @echo off
    echo title Desinstalador VPN Manager
    echo echo 🗑️  Desinstalador de VPN Manager
    echo echo ===============================
    echo echo.
    echo.
    echo REM Verificar permisos de administrador
    echo net session ^>nul 2^>^&1
    echo if %%errorlevel%% neq 0 ^(
    echo     echo ⚠️  Este script debe ejecutarse como Administrador
    echo     pause
    echo     exit /b 1
    echo ^)
    echo.
    echo echo ⚠️  ATENCIÓN: Esto eliminará VPN Manager del sistema
    echo echo.
    echo set /p "CONFIRM=¿Estás seguro de que deseas continuar? (y/N): "
    echo if /i not "%%CONFIRM%%"=="y" if /i not "%%CONFIRM%%"=="yes" ^(
    echo     echo Desinstalación cancelada.
    echo     pause
    echo     exit /b 0
    echo ^)
    echo.
    echo echo.
    echo echo 🧹 Eliminando VPN Manager...
    echo.
    echo set INSTALL_DIR=%%ProgramFiles%%\VPN Manager
    echo set DESKTOP_LINK=%%USERPROFILE%%\Desktop\VPN Manager.lnk
    echo set START_MENU_LINK=%%ProgramData%%\Microsoft\Windows\Start Menu\Programs\VPN Manager.lnk
    echo.
    echo REM Cerrar la aplicación si está ejecutándose
    echo taskkill /f /im "VPN-Manager-Windows.exe" ^>nul 2^>^&1
    echo.
    echo REM Eliminar directorio de instalación
    echo if exist "%%INSTALL_DIR%%" ^(
    echo     echo 📁 Eliminando directorio de instalación...
    echo     rmdir /s /q "%%INSTALL_DIR%%"
    echo ^)
    echo.
    echo REM Eliminar accesos directos
    echo if exist "%%DESKTOP_LINK%%" ^(
    echo     echo 🖥️  Eliminando acceso directo del escritorio...
    echo     del /q "%%DESKTOP_LINK%%"
    echo ^)
    echo.
    echo if exist "%%START_MENU_LINK%%" ^(
    echo     echo 📱 Eliminando acceso directo del menú inicio...
    echo     del /q "%%START_MENU_LINK%%"
    echo ^)
    echo.
    echo echo.
    echo echo ✅ VPN Manager desinstalado completamente
    echo echo.
    echo echo Nota: Los datos de usuario se mantienen en %%APPDATA%%\VPN-Manager\
    echo set /p "DELETE_DATA=¿Deseas eliminar también los datos de usuario? (y/N): "
    echo if /i "%%DELETE_DATA%%"=="y" if /i "%%DELETE_DATA%%"=="yes" ^(
    echo     if exist "%%APPDATA%%\VPN-Manager" ^(
    echo         rmdir /s /q "%%APPDATA%%\VPN-Manager"
    echo         echo Datos de usuario eliminados.
    echo     ^)
    echo ^)
    echo echo.
    echo pause
    ) > "release\VPN-Manager-Windows-%ARCH_NAME%\uninstall.bat"
    
    REM Crear archivo ZIP
    echo 🗜️  Creando archivo ZIP...
    cd release
    powershell -Command "Compress-Archive -Path 'VPN-Manager-Windows-%ARCH_NAME%' -DestinationPath 'VPN-Manager-Windows-%ARCH_NAME%-%DATE:~6,4%.%DATE:~3,2%.%DATE:~0,2%.zip' -Force"
    cd ..
    
    echo ✅ ZIP creado: release\VPN-Manager-Windows-%ARCH_NAME%-%DATE:~6,4%.%DATE:~3,2%.%DATE:~0,2%.zip
    
    REM Limpiar directorio temporal
    echo 🧹 Limpiando directorio temporal...
    rmdir /s /q "%TEMP_DIR%"
    
    echo.
    echo 🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!
    echo ==================================
    echo.
    echo 📦 Archivos generados:
    echo    ├── release\VPN-Manager-Windows-%ARCH_NAME%\
    echo    │   ├── VPN-Manager-Windows\ ^(aplicación^)
    echo    │   ├── run.bat
    echo    │   ├── install.bat
    echo    │   ├── uninstall.bat
    echo    │   └── README.md
    echo    └── release\VPN-Manager-Windows-%ARCH_NAME%-%DATE:~6,4%.%DATE:~3,2%.%DATE:~0,2%.zip
    echo.
    echo 🧪 Para probar:
    echo    cd release\VPN-Manager-Windows-%ARCH_NAME% ^&^& run.bat
    echo.
    echo 💻 Para instalar en el sistema:
    echo    cd release\VPN-Manager-Windows-%ARCH_NAME% ^&^& install.bat ^(como Admin^)
    echo.
    echo 📤 Para distribuir:
    echo    Comparte el archivo: release\VPN-Manager-Windows-%ARCH_NAME%-%DATE:~6,4%.%DATE:~3,2%.%DATE:~0,2%.zip
    
) else (
    echo ❌ Error: No se pudo crear el ejecutable Windows
    cd /d "%CURRENT_DIR%"
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

pause
