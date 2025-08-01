#!/usr/bin/env python3
"""
VPN Manager - Generador de ejecutables multiplataforma
Crea ejecutables para macOS, Linux y Windows desde macOS
"""

import os
import sys
import subprocess
import platform
import shutil
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime

class MultiPlatformBuilder:
    def __init__(self):
        self.workspace = Path.cwd()
        self.date = datetime.now().strftime("%Y.%m.%d")
        self.release_dir = self.workspace / "release"
        self.release_dir.mkdir(exist_ok=True)
        
    def log(self, message, level="INFO"):
        """Imprimir mensaje con formato"""
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARN": "⚠️"}
        print(f"{symbols.get(level, 'ℹ️')} {message}")
        
    def check_dependencies(self):
        """Verificar dependencias necesarias"""
        self.log("Verificando dependencias...")
        
        try:
            import PyQt5
            self.log("PyQt5 encontrado", "SUCCESS")
        except ImportError:
            self.log("PyQt5 no encontrado, instalando...", "WARN")
            subprocess.run([sys.executable, "-m", "pip", "install", "PyQt5==5.15.9"])
            
        try:
            import PyInstaller
            self.log("PyInstaller encontrado", "SUCCESS")
        except ImportError:
            self.log("PyInstaller no encontrado, instalando...", "WARN")
            subprocess.run([sys.executable, "-m", "pip", "install", "PyInstaller==6.14.1"])
            
    def create_spec_file(self, platform_name="universal"):
        """Crear archivo .spec para PyInstaller"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
app_name = "VPN-Manager-{platform_name}"

# Archivos a incluir
added_files = [
    ('dialogs', 'dialogs'),
    ('threads', 'threads'),
]

# Archivos Python individuales
python_files = [
    'license.py',
    'license_storage.py', 
    'license_encryptor.py',
    'license_generator.py',
    'models.py',
]

for py_file in python_files:
    if os.path.exists(py_file):
        added_files.append((py_file, '.'))

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

# Módulos a excluir
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
    hooksconfig={{}},
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
'''
        
        spec_file = self.workspace / f"vpn_manager_{platform_name}.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
            
        return spec_file
        
    def build_macos(self):
        """Construir ejecutable para macOS"""
        if platform.system() != "Darwin":
            self.log("Build de macOS solo disponible en macOS", "WARN")
            return False
            
        self.log("🍎 Construyendo ejecutable para macOS...")
        
        # Limpiar builds anteriores
        for dir_name in ["build", "dist"]:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                
        # Crear spec file
        spec_file = self.create_spec_file("macOS")
        
        # Ejecutar PyInstaller
        cmd = ["pyinstaller", "--clean", "--noconfirm", str(spec_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Crear paquete
            app_dir = self.workspace / "dist" / "VPN-Manager-macOS"
            if app_dir.exists():
                # Crear ZIP
                zip_name = f"VPN-Manager-macOS-{self.date}.zip"
                zip_path = self.release_dir / zip_name
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(app_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, app_dir.parent)
                            zipf.write(file_path, arc_name)
                
                self.log(f"Ejecutable macOS creado: {zip_name}", "SUCCESS")
                return True
        
        self.log(f"Error en build macOS: {result.stderr}", "ERROR")
        return False
        
    def build_linux(self):
        """Construir ejecutable para Linux (requiere Docker o máquina Linux)"""
        self.log("🐧 Preparando build para Linux...")
        
        # Como estamos en macOS, crear script de build para Linux
        linux_script = self.workspace / "build_linux_cross.sh"
        with open(linux_script, 'w') as f:
            f.write(f"""#!/bin/bash
# Script para construir ejecutable Linux desde macOS usando Docker

echo "🐧 Construyendo VPN Manager para Linux..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no encontrado. Instala Docker Desktop para macOS"
    exit 1
fi

# Crear Dockerfile
cat > Dockerfile.linux-cross << 'EOF'
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-venv \\
    python3-dev \\
    build-essential \\
    qt5-qmake \\
    qtbase5-dev \\
    qttools5-dev-tools \\
    libqt5gui5 \\
    libqt5core5a \\
    libqt5widgets5 \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN python3 -m pip install --upgrade pip
RUN pip3 install PyQt5==5.15.9 PyInstaller==6.14.1 pexpect requests cryptography packaging urllib3 certifi

RUN pyinstaller --clean --noconfirm --onedir --windowed \\
    --add-data "dialogs:dialogs" \\
    --add-data "threads:threads" \\
    --hidden-import "PyQt5.sip" \\
    --name "VPN-Manager-Linux" \\
    Main.py

CMD ["cp", "-r", "dist/VPN-Manager-Linux", "/output/"]
EOF

echo "🔨 Construyendo imagen Docker..."
docker build -f Dockerfile.linux-cross -t vpn-manager-linux-builder .

echo "📦 Ejecutando build..."
mkdir -p release/VPN-Manager-Linux-x64
docker run --rm -v "$(pwd)/release/VPN-Manager-Linux-x64:/output" vpn-manager-linux-builder

if [ -d "release/VPN-Manager-Linux-x64/VPN-Manager-Linux" ]; then
    echo "✅ Ejecutable Linux creado exitosamente!"
    
    # Crear script de ejecución
    cat > release/VPN-Manager-Linux-x64/run.sh << 'RUNEOF'
#!/bin/bash
echo "🚀 Ejecutando VPN Manager..."
cd "$(dirname "$0")"
./VPN-Manager-Linux/VPN-Manager-Linux
RUNEOF
    chmod +x release/VPN-Manager-Linux-x64/run.sh
    
    # Crear archivo tar.gz
    cd release
    tar -czf VPN-Manager-Linux-x64-{self.date}.tar.gz VPN-Manager-Linux-x64/
    cd ..
    
    echo "📁 Paquete Linux: release/VPN-Manager-Linux-x64-{self.date}.tar.gz"
else
    echo "❌ Error al crear ejecutable Linux"
fi
""")
        
        linux_script.chmod(0o755)
        self.log(f"Script de build Linux creado: {linux_script.name}", "SUCCESS")
        return True
        
    def show_status(self):
        """Mostrar estado de los ejecutables"""
        self.log("📊 Estado actual de los ejecutables:")
        print("=" * 50)
        
        # macOS
        macos_zip = self.release_dir / f"VPN-Manager-macOS-{self.date}.zip"
        if macos_zip.exists():
            self.log(f"macOS: {macos_zip.name} (LISTO)", "SUCCESS")
        else:
            self.log("macOS: No encontrado", "WARN")
            
        # Linux  
        linux_tar = self.release_dir / f"VPN-Manager-Linux-x64-{self.date}.tar.gz"
        if linux_tar.exists():
            self.log(f"Linux: {linux_tar.name} (LISTO)", "SUCCESS")
        else:
            self.log("Linux: No encontrado", "WARN")
            
        # Windows
        windows_zip = self.release_dir / f"VPN-Manager-Windows-x64-{self.date}.zip"
        if windows_zip.exists():
            self.log(f"Windows: {windows_zip.name} (LISTO)", "SUCCESS")
        else:
            self.log("Windows: Kit de build disponible en windows-build-kit/", "WARN")
            
    def create_windows_kit(self):
        """Crear kit de build para Windows"""
        self.log("🪟 Creando kit de build para Windows...")
        
        kit_dir = self.workspace / "windows-build-kit"
        kit_dir.mkdir(exist_ok=True)
        
        # Copiar archivos del proyecto
        files_to_copy = ["Main.py", "license.py", "license_storage.py", 
                        "license_encryptor.py", "license_generator.py", "models.py"]
        
        for file_name in files_to_copy:
            file_path = self.workspace / file_name
            if file_path.exists():
                shutil.copy2(file_path, kit_dir)
                
        # Copiar directorios
        for dir_name in ["dialogs", "threads"]:
            src_dir = self.workspace / dir_name
            dst_dir = kit_dir / dir_name
            if src_dir.exists():
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
                
        # Crear spec file específico para Windows
        spec_file = kit_dir / "vpn_manager_windows.spec"
        with open(spec_file, 'w') as f:
            f.write('''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
app_name = "VPN-Manager-Windows"

added_files = [
    ('dialogs', 'dialogs'),
    ('threads', 'threads'),
]

hidden_imports = [
    'PyQt5.sip', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
    'pexpect', 'requests', 'cryptography', 'packaging', 'urllib3', 'certifi'
]

a = Analysis(['Main.py'], datas=added_files, hiddenimports=hidden_imports)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=app_name, 
          debug=False, bootloader_ignore_signals=False, strip=False, 
          upx=True, console=False)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, 
               upx=True, name=app_name)
''')
        
        self.log(f"Kit de Windows creado en: {kit_dir}", "SUCCESS")
        return True
        
    def run(self):
        """Ejecutar el builder"""
        self.log("🌍 VPN Manager - Generador multiplataforma")
        print("=" * 60)
        
        self.check_dependencies()
        self.show_status()
        
        print("\n🔧 Opciones disponibles:")
        print("1. Construir ejecutable macOS")
        print("2. Preparar build Linux (Docker)")
        print("3. Crear kit Windows")
        print("4. Mostrar estado")
        print("5. Salir")
        
        while True:
            try:
                choice = input("\n👉 Selecciona una opción (1-5): ").strip()
                
                if choice == "1":
                    self.build_macos()
                elif choice == "2":
                    self.build_linux()
                elif choice == "3":
                    self.create_windows_kit()
                elif choice == "4":
                    self.show_status()
                elif choice == "5":
                    self.log("¡Hasta luego!", "SUCCESS")
                    break
                else:
                    self.log("Opción no válida", "WARN")
                    
            except KeyboardInterrupt:
                self.log("\n¡Hasta luego!", "SUCCESS")
                break

if __name__ == "__main__":
    builder = MultiPlatformBuilder()
    builder.run()
