#!/usr/bin/env python3
"""
Script para generar ejecutables multiplataforma de VPN Manager
"""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

def get_current_platform():
    """Detecta la plataforma actual"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        raise ValueError(f"Plataforma no soportada: {system}")

def create_spec_file(platform_name):
    """Crea un archivo .spec personalizado para PyInstaller"""
    spec_content = {
        "macos": '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VPN Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='VPN Manager.app',
    icon=None,
    bundle_identifier='com.vpnmanager.app',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleDisplayName': 'VPN Manager',
        'CFBundleName': 'VPN Manager',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
)
''',
        "linux": '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VPN-Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
''',
        "windows": '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
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
    ],
    hiddenimports=[
        'PyQt5.sip',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'win32api',
        'win32con',
        'win32gui',
        'requests',
        'cryptography',
        'packaging',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VPN-Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    }
    
    return spec_content.get(platform_name, spec_content["linux"])

def build_executable():
    """Construye el ejecutable para la plataforma actual"""
    print("🔨 Iniciando construcción del ejecutable...")
    
    # Detectar plataforma
    current_platform = get_current_platform()
    print(f"📱 Plataforma detectada: {current_platform}")
    
    # Crear directorio de distribución
    dist_dir = Path("dist")
    build_dir = Path("build")
    
    # Limpiar directorios anteriores
    if dist_dir.exists():
        print("🧹 Limpiando directorio dist anterior...")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print("🧹 Limpiando directorio build anterior...")
        shutil.rmtree(build_dir)
    
    # Crear archivo .spec
    spec_filename = f"vpn-manager-{current_platform}.spec"
    spec_content = create_spec_file(current_platform)
    
    print(f"📝 Creando archivo spec: {spec_filename}")
    with open(spec_filename, 'w') as f:
        f.write(spec_content)
    
    try:
        # Ejecutar PyInstaller
        print("⚙️  Ejecutando PyInstaller...")
        cmd = [sys.executable, "-m", "PyInstaller", spec_filename, "--noconfirm"]
        
        print(f"Comando: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ PyInstaller completado exitosamente")
        print("STDOUT:", result.stdout[-500:])  # Últimas 500 líneas
        
        # Verificar que el ejecutable se creó
        if current_platform == "macos":
            app_path = dist_dir / "VPN Manager.app"
            if app_path.exists():
                print(f"✅ Aplicación macOS creada: {app_path}")
                print("📋 Para firmar la aplicación (opcional):")
                print(f"   codesign --deep --force --verify --verbose --sign 'Developer ID Application: Tu Nombre' '{app_path}'")
            else:
                print("❌ No se encontró la aplicación .app")
                return False
                
        elif current_platform == "linux":
            exe_path = dist_dir / "VPN-Manager"
            if exe_path.exists():
                print(f"✅ Ejecutable Linux creado: {exe_path}")
                # Hacer ejecutable
                exe_path.chmod(0o755)
                print("✅ Permisos de ejecución configurados")
            else:
                print("❌ No se encontró el ejecutable")
                return False
                
        elif current_platform == "windows":
            exe_path = dist_dir / "VPN-Manager.exe"
            if exe_path.exists():
                print(f"✅ Ejecutable Windows creado: {exe_path}")
            else:
                print("❌ No se encontró el ejecutable .exe")
                return False
        
        # Crear paquete final
        create_distribution_package(current_platform)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando PyInstaller: {e}")
        print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def create_distribution_package(platform_name):
    """Crea un paquete de distribución final"""
    print("📦 Creando paquete de distribución...")
    
    dist_dir = Path("dist")
    package_dir = Path("release") / f"VPN-Manager-{platform_name}"
    
    # Crear directorio de release
    package_dir.mkdir(parents=True, exist_ok=True)
    
    if platform_name == "macos":
        app_path = dist_dir / "VPN Manager.app"
        if app_path.exists():
            # Copiar la aplicación
            shutil.copytree(app_path, package_dir / "VPN Manager.app", dirs_exist_ok=True)
            
            # Crear script de instalación
            install_script = package_dir / "install.sh"
            install_content = '''#!/bin/bash
echo "🚀 Instalando VPN Manager..."
cp -R "VPN Manager.app" /Applications/
echo "✅ VPN Manager instalado en /Applications/"
echo "Puedes ejecutarlo desde Launchpad o Finder"
'''
            with open(install_script, 'w') as f:
                f.write(install_content)
            install_script.chmod(0o755)
            
    elif platform_name == "linux":
        exe_path = dist_dir / "VPN-Manager"
        if exe_path.exists():
            # Copiar el ejecutable
            shutil.copy2(exe_path, package_dir / "VPN-Manager")
            
            # Crear desktop file
            desktop_content = '''[Desktop Entry]
Version=1.0
Type=Application
Name=VPN Manager
Comment=Gestiona conexiones VPN
Exec=/opt/vpn-manager/VPN-Manager
Icon=/opt/vpn-manager/vpn-manager.png
Terminal=false
StartupNotify=true
Categories=Network;Security;
'''
            with open(package_dir / "vpn-manager.desktop", 'w') as f:
                f.write(desktop_content)
            
            # Crear script de instalación
            install_script = package_dir / "install.sh"
            install_content = '''#!/bin/bash
echo "🚀 Instalando VPN Manager..."
sudo mkdir -p /opt/vpn-manager
sudo cp VPN-Manager /opt/vpn-manager/
sudo chmod +x /opt/vpn-manager/VPN-Manager
sudo cp vpn-manager.desktop /usr/share/applications/
echo "✅ VPN Manager instalado"
echo "Puedes ejecutarlo desde el menú de aplicaciones o ejecutando: /opt/vpn-manager/VPN-Manager"
'''
            with open(install_script, 'w') as f:
                f.write(install_content)
            install_script.chmod(0o755)
            
    elif platform_name == "windows":
        exe_path = dist_dir / "VPN-Manager.exe"
        if exe_path.exists():
            # Copiar el ejecutable
            shutil.copy2(exe_path, package_dir / "VPN-Manager.exe")
            
            # Crear script de instalación
            install_script = package_dir / "install.bat"
            install_content = '''@echo off
echo 🚀 Instalando VPN Manager...
if not exist "%ProgramFiles%\\VPN Manager" mkdir "%ProgramFiles%\\VPN Manager"
copy "VPN-Manager.exe" "%ProgramFiles%\\VPN Manager\\"
echo ✅ VPN Manager instalado en %ProgramFiles%\\VPN Manager
echo Puedes ejecutarlo desde el menú de inicio o el acceso directo
pause
'''
            with open(install_script, 'w') as f:
                f.write(install_content)
    
    # Agregar archivos adicionales
    readme_content = f'''# VPN Manager - {platform_name.title()}

## Instalación

### {platform_name.title()}:
'''
    
    if platform_name == "macos":
        readme_content += '''
1. Ejecuta `install.sh` o arrastra "VPN Manager.app" a la carpeta Applications
2. Si aparece un aviso de seguridad, ve a System Preferences → Security & Privacy y permite la ejecución
3. Ejecuta VPN Manager desde Launchpad

### Requisitos:
- macOS 10.14 o superior
- OpenVPN y StrongSwan (se instalan automáticamente con Homebrew)
'''
    elif platform_name == "linux":
        readme_content += '''
1. Ejecuta `sudo ./install.sh` o copia manualmente el ejecutable
2. Asegúrate de tener OpenVPN y StrongSwan instalados:
   ```bash
   sudo apt-get install openvpn strongswan
   ```
3. Ejecuta desde el menú de aplicaciones o terminal

### Requisitos:
- Ubuntu 20.04+ / Debian 11+ (o distribución compatible)
- OpenVPN y StrongSwan
- Qt5 libraries
'''
    elif platform_name == "windows":
        readme_content += '''
1. Ejecuta `install.bat` como administrador o copia manualmente el ejecutable
2. Instala OpenVPN desde https://openvpn.net/community-downloads/
3. Ejecuta VPN Manager desde el menú de inicio

### Requisitos:
- Windows 10 o superior
- OpenVPN Community Edition
- Permisos de administrador para conexiones VPN
'''
    
    readme_content += '''

## Uso

1. **Configurar conexiones**: Haz clic en "Configurar" para agregar conexiones OpenVPN o IPSec
2. **Conectar**: Haz clic en el botón "Conectar" junto a la conexión deseada
3. **Sistema tray**: La aplicación funciona desde el área de notificaciones
4. **Actualizaciones**: Verifica actualizaciones desde el menú del sistema tray

## Soporte

Para soporte técnico, contacta: yesod3d@gmail.com
'''
    
    with open(package_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Paquete creado en: {package_dir}")
    
    # Crear archivo ZIP final
    try:
        import zipfile
        zip_path = Path("release") / f"VPN-Manager-{platform_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(package_dir.parent)
                    zipf.write(file_path, arc_path)
        
        print(f"📦 ZIP creado: {zip_path}")
        print(f"📊 Tamaño: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
        
    except Exception as e:
        print(f"⚠️  No se pudo crear el ZIP: {e}")

def main():
    """Función principal"""
    print("🏗️  VPN Manager - Generador de Ejecutables")
    print("=" * 50)
    
    # Verificar dependencias
    print("🔍 Verificando dependencias...")
    
    try:
        import PyQt5
        print("✅ PyQt5 disponible")
    except ImportError:
        print("❌ PyQt5 no encontrado. Instala con: pip install PyQt5")
        return 1
    
    try:
        import PyInstaller
        print("✅ PyInstaller disponible")
    except ImportError:
        print("❌ PyInstaller no encontrado. Instala con: pip install PyInstaller")
        return 1
    
    # Verificar archivos necesarios
    required_files = ["Main.py", "version.py", "auto_updater.py", "requirements.txt"]
    for file_name in required_files:
        if not Path(file_name).exists():
            print(f"❌ Archivo requerido no encontrado: {file_name}")
            return 1
    
    print("✅ Todos los archivos requeridos encontrados")
    
    # Construir ejecutable
    if build_executable():
        print("\n🎉 ¡Ejecutable generado exitosamente!")
        print("\n📋 Próximos pasos:")
        print("1. Prueba el ejecutable en el directorio 'dist/'")
        print("2. Distribúye el paquete desde el directorio 'release/'")
        print("3. Para otras plataformas, ejecuta este script en esos sistemas")
        return 0
    else:
        print("\n❌ Error generando el ejecutable")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
