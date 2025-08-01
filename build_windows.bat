@echo off
REM Script para generar ejecutable en Windows

echo 🪟 Generando ejecutable para Windows...
echo =====================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instala Python desde python.org
    pause
    exit /b 1
)

REM Activar entorno virtual si existe
if exist ".venv\" (
    echo 🔧 Activando entorno virtual...
    call .venv\Scripts\activate.bat
)

REM Verificar PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando PyInstaller...
    pip install PyInstaller
)

REM Verificar PyQt5
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando PyQt5...
    pip install PyQt5==5.15.11
)

REM Verificar pywin32
python -c "import win32api" >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando pywin32...
    pip install pywin32
)

REM Limpiar builds anteriores
echo 🧹 Limpiando builds anteriores...
if exist "build\" rmdir /s /q "build\"
if exist "dist\" rmdir /s /q "dist\"
if exist "*.spec" del "*.spec"

REM Crear archivo spec personalizado para Windows
echo 📝 Creando archivo .spec personalizado...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['Main.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[
echo         ^('dialogs', 'dialogs'^),
echo         ^('threads', 'threads'^),
echo         ^('version.py', '.'^),
echo         ^('auto_updater.py', '.'^),
echo         ^('license.py', '.'^),
echo         ^('license_storage.py', '.'^),
echo         ^('license_encryptor.py', '.'^),
echo         ^('license_generator.py', '.'^),
echo         ^('models.py', '.'^),
echo     ],
echo     hiddenimports=[
echo         'PyQt5.sip',
echo         'PyQt5.QtCore',
echo         'PyQt5.QtGui',
echo         'PyQt5.QtWidgets',
echo         'win32api',
echo         'win32con',
echo         'win32gui',
echo         'requests',
echo         'cryptography',
echo         'packaging',
echo         'urllib3',
echo         'certifi',
echo         'charset_normalizer',
echo         'idna',
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='VPN-Manager',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     version='version_info.txt',
echo ^)
) > vpn-manager-windows.spec

REM Crear archivo de información de versión
echo 📋 Creando información de versión...
(
echo VSVersionInfo^(
echo   ffi=FixedFileInfo^(
echo     filevers=^(1, 0, 0, 0^),
echo     prodvers=^(1, 0, 0, 0^),
echo     mask=0x3f,
echo     flags=0x0,
echo     OS=0x40004,
echo     fileType=0x1,
echo     subtype=0x0,
echo     date=^(0, 0^)
echo   ^),
echo   kids=[
echo     StringFileInfo^(
echo       [
echo         StringTable^(
echo           u'040904B0',
echo           [StringStruct^(u'CompanyName', u'VPN Manager'^),
echo            StringStruct^(u'FileDescription', u'VPN Manager - Gestión de conexiones VPN'^),
echo            StringStruct^(u'FileVersion', u'1.0.0.0'^),
echo            StringStruct^(u'InternalName', u'VPN-Manager'^),
echo            StringStruct^(u'LegalCopyright', u'Copyright ^(C^) 2025'^),
echo            StringStruct^(u'OriginalFilename', u'VPN-Manager.exe'^),
echo            StringStruct^(u'ProductName', u'VPN Manager'^),
echo            StringStruct^(u'ProductVersion', u'1.0.0.0'^)]
echo         ^)
echo       ]
echo     ^),
echo     VarFileInfo^([VarStruct^(u'Translation', [1033, 1200]^)]^)
echo   ]
echo ^)
) > version_info.txt

REM Ejecutar PyInstaller
echo 🔨 Ejecutando PyInstaller...
python -m PyInstaller vpn-manager-windows.spec --noconfirm --clean

REM Verificar que se creó el ejecutable
if exist "dist\VPN-Manager.exe" (
    echo ✅ Ejecutable Windows creado exitosamente!
    
    REM Crear paquete de distribución
    echo 📦 Creando paquete de distribución...
    if not exist "release\" mkdir "release\"
    if not exist "release\VPN-Manager-Windows\" mkdir "release\VPN-Manager-Windows\"
    copy "dist\VPN-Manager.exe" "release\VPN-Manager-Windows\"
    
    REM Crear script de instalación
    echo 📝 Creando script de instalación...
    (
    echo @echo off
    echo echo 🚀 Instalando VPN Manager...
    echo.
    echo REM Crear directorio de instalación
    echo if not exist "%%ProgramFiles%%\VPN Manager\" mkdir "%%ProgramFiles%%\VPN Manager\"
    echo.
    echo REM Copiar ejecutable
    echo copy "VPN-Manager.exe" "%%ProgramFiles%%\VPN Manager\"
    echo.
    echo REM Crear acceso directo en el escritorio
    echo powershell "$s=^(New-Object -COM WScript.Shell^).CreateShortcut^('%%USERPROFILE%%\Desktop\VPN Manager.lnk'^); $s.TargetPath='%%ProgramFiles%%\VPN Manager\VPN-Manager.exe'; $s.Save^(^)"
    echo.
    echo REM Crear acceso directo en el menú inicio
    echo powershell "$s=^(New-Object -COM WScript.Shell^).CreateShortcut^('%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\VPN Manager.lnk'^); $s.TargetPath='%%ProgramFiles%%\VPN Manager\VPN-Manager.exe'; $s.Save^(^)"
    echo.
    echo echo ✅ VPN Manager instalado en %%ProgramFiles%%\VPN Manager
    echo echo ✅ Accesos directos creados en escritorio y menú inicio
    echo echo.
    echo echo ⚠️  IMPORTANTE: Instala OpenVPN desde https://openvpn.net/community-downloads/
    echo echo.
    echo pause
    ) > "release\VPN-Manager-Windows\install.bat"
    
    REM Crear script de ejecución directo
    (
    echo @echo off
    echo echo 🚀 Ejecutando VPN Manager...
    echo echo.
    echo echo ⚠️  Asegúrate de tener OpenVPN instalado antes de usar la aplicación
    echo echo    Descarga desde: https://openvpn.net/community-downloads/
    echo echo.
    echo pause
    echo start VPN-Manager.exe
    ) > "release\VPN-Manager-Windows\run.bat"
    
    REM Crear README
    (
    echo # VPN Manager para Windows
    echo.
    echo ## Instalación
    echo.
    echo ### Opción 1: Instalación automática ^(recomendado^)
    echo 1. Ejecuta `install.bat` como administrador
    echo 2. Sigue las instrucciones en pantalla
    echo.
    echo ### Opción 2: Ejecución portable
    echo 1. Haz doble clic en `run.bat`
    echo 2. La aplicación se ejecutará sin instalación
    echo.
    echo ## Requisitos
    echo.
    echo - Windows 10 o superior
    echo - OpenVPN Community Edition ^(obligatorio^)
    echo   - Descarga: https://openvpn.net/community-downloads/
    echo - Permisos de administrador para conexiones VPN
    echo.
    echo ## Primera ejecución
    echo.
    echo 1. **Instalar OpenVPN**: Si no lo tienes, la aplicación no funcionará
    echo 2. **Permisos**: Acepta los permisos de administrador cuando se soliciten
    echo 3. **Configurar**: Añade conexiones VPN desde el botón "Configurar"
    echo.
    echo ## Uso
    echo.
    echo 1. **Configurar conexiones**: Botón "Configurar" → Seleccionar archivos .ovpn
    echo 2. **Conectar**: Seleccionar conexión → Botón "Conectar"
    echo 3. **Sistema tray**: Acceder desde el icono en la bandeja del sistema
    echo 4. **Desconectar**: Botón "Desconectar" o menú del sistema tray
    echo.
    echo ## Solución de problemas
    echo.
    echo ### "No se puede conectar"
    echo - Verifica que OpenVPN esté instalado
    echo - Ejecuta como administrador
    echo - Revisa los archivos de configuración .ovpn
    echo.
    echo ### "Aplicación no inicia"
    echo - Ejecuta como administrador
    echo - Verifica antivirus ^(puede bloquear el ejecutable^)
    echo - Reinstala OpenVPN
    echo.
    echo ## Desinstalación
    echo.
    echo 1. Elimina la carpeta de instalación: `%%ProgramFiles%%\VPN Manager`
    echo 2. Elimina accesos directos del escritorio y menú inicio
    echo.
    echo ## Soporte
    echo.
    echo - Email: yesod3d@gmail.com
    echo - GitHub: https://github.com/alumno109192/vpn
    echo.
    echo ## Licencia
    echo.
    echo Período de prueba: 30 días gratuitos
    echo Licencia completa: 5€/mes
    ) > "release\VPN-Manager-Windows\README.md"
    
    REM Crear archivo de descarga de OpenVPN
    (
    echo @echo off
    echo echo 📥 Descargando OpenVPN...
    echo echo.
    echo echo Se abrirá la página de descarga de OpenVPN
    echo echo Descarga e instala "OpenVPN Community"
    echo echo.
    echo start https://openvpn.net/community-downloads/
    echo pause
    ) > "release\VPN-Manager-Windows\download-openvpn.bat"
    
    REM Crear ZIP con PowerShell
    echo 🗜️  Creando archivo ZIP...
    powershell "Compress-Archive -Path 'release\VPN-Manager-Windows\*' -DestinationPath 'release\VPN-Manager-Windows.zip' -Force"
    
    echo.
    echo 🎉 ¡Proceso completado exitosamente!
    echo.
    echo 📋 Archivos generados:
    echo    - dist\VPN-Manager.exe ^(ejecutable Windows^)
    echo    - release\VPN-Manager-Windows\ ^(paquete de distribución^)
    echo    - release\VPN-Manager-Windows.zip ^(archivo final para distribución^)
    echo.
    echo 🧪 Para probar:
    echo    dist\VPN-Manager.exe
    echo.
    echo 📤 Para distribuir:
    echo    Comparte el archivo: release\VPN-Manager-Windows.zip
    echo.
    
) else (
    echo ❌ Error: No se pudo crear el ejecutable Windows
    echo Revisa los logs anteriores para más detalles
)

pause
