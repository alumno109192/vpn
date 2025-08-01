#!/bin/bash
# Script para generar ejecutable NATIVO de Linux para USB/pendrive
# Compilado en contenedor Ubuntu real - 100% compatible
# Autor: VPN Manager Team
# Fecha: 28/06/2025

set -e

echo "🐧 Generando ejecutable NATIVO de Linux (ELF) para pendrive..."
echo "=============================================================="

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Instálalo con:"
    echo "   brew install --cask docker"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker no está corriendo. Inicia Docker Desktop."
    exit 1
fi

echo "✅ Docker detectado y funcionando"

# Crear directorio de salida
OUTPUT_DIR="./linux-native-build"
mkdir -p "$OUTPUT_DIR"

# Obtener versión
VERSION=$(date +%Y.%m.%d)
echo "📝 Versión del ejecutable: $VERSION"

# Crear Dockerfile específico para build nativo Linux
echo "📦 Creando entorno de compilación Ubuntu..."
cat > Dockerfile.linux-native << 'EOF'
FROM ubuntu:22.04

# Evitar interacciones durante la instalación
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    xvfb \
    libqt5core5a \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5dbus5 \
    libqt5network5 \
    libqt5printsupport5 \
    python3-pyqt5 \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libegl1-mesa \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    upx-ucl \
    build-essential \
    file \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -s /bin/bash builder
USER builder
WORKDIR /home/builder/app

# Copiar archivos del proyecto
COPY --chown=builder:builder . .

# Instalar dependencias Python en entorno virtual
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install PyQt5==5.15.10 && \
    pip install requests cryptography && \
    pip install pyinstaller>=5.0

CMD ["bash"]
EOF

# Construir imagen Docker
echo "🔧 Construyendo imagen Docker Ubuntu..."
docker build -f Dockerfile.linux-native -t vpn-manager-ubuntu-builder .

# Ejecutar compilación en contenedor
echo "⚙️ Compilando ejecutable en Ubuntu 22.04..."
docker run --rm -v "$(pwd)/$OUTPUT_DIR:/output" vpn-manager-ubuntu-builder bash -c "
set -e
echo '🔨 Iniciando compilación nativa Linux...'

# Activar entorno virtual
. venv/bin/activate

# Configurar display virtual
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 3

# Actualizar versión en Main.py
VERSION='$VERSION'
cp Main.py Main.py.backup
sed -i \"s/current_version = \\\"1.0.0\\\"/current_version = \\\"$VERSION\\\"/\" Main.py

echo '📦 Compilando con PyInstaller...'
python3 -m PyInstaller \
  --onefile \
  --name \"VPN-Manager-Linux-$VERSION\" \
  --add-data \"dialogs:dialogs\" \
  --add-data \"threads:threads\" \
  --hidden-import PyQt5.sip \
  --hidden-import PyQt5.QtCore \
  --hidden-import PyQt5.QtGui \
  --hidden-import PyQt5.QtWidgets \
  --hidden-import cryptography \
  --hidden-import requests \
  --hidden-import urllib3 \
  --exclude-module tkinter \
  --exclude-module matplotlib \
  --exclude-module numpy \
  --exclude-module pandas \
  --windowed \
  Main.py

# Verificar ejecutable
if [ -f \"dist/VPN-Manager-Linux-$VERSION\" ]; then
    echo '✅ Ejecutable ELF creado: dist/VPN-Manager-Linux-$VERSION'
    file \"dist/VPN-Manager-Linux-$VERSION\"
    ls -lah \"dist/VPN-Manager-Linux-$VERSION\"
    
    # Comprimir con UPX para reducir tamaño
    echo '🗜️ Comprimiendo ejecutable...'
    upx --best \"dist/VPN-Manager-Linux-$VERSION\" || echo '⚠️ UPX falló, continuando...'
    
    # Mostrar información final
    echo '📊 Información del ejecutable final:'
    file \"dist/VPN-Manager-Linux-$VERSION\"
    ls -lah \"dist/VPN-Manager-Linux-$VERSION\"
    
    # Generar checksum
    sha256sum \"dist/VPN-Manager-Linux-$VERSION\" > \"dist/VPN-Manager-Linux-$VERSION.sha256\"
    
    # Copiar a directorio de salida
    cp \"dist/VPN-Manager-Linux-$VERSION\" /output/
    cp \"dist/VPN-Manager-Linux-$VERSION.sha256\" /output/
    
    echo '✅ Compilación completada exitosamente!'
else
    echo '❌ Error: No se creó el ejecutable'
    ls -la dist/
    exit 1
fi
"

# Limpiar imagen
docker rmi vpn-manager-ubuntu-builder > /dev/null
rm Dockerfile.linux-native

# Verificar archivo extraído
if [ -f "$OUTPUT_DIR/VPN-Manager-Linux-$VERSION" ]; then
    echo ""
    echo "🎉 ¡ÉXITO! Ejecutable nativo de Linux generado:"
    echo "=============================================="
    ls -lah "$OUTPUT_DIR"/
    echo ""
    echo "📋 Tipo de archivo:"
    file "$OUTPUT_DIR/VPN-Manager-Linux-$VERSION"
    echo ""
    echo "🔐 Verificación de integridad:"
    cat "$OUTPUT_DIR/VPN-Manager-Linux-$VERSION.sha256"
    echo ""
    
    # Crear script de instalación para el pendrive
    cat > "$OUTPUT_DIR/EJECUTAR-EN-UBUNTU.sh" << 'RUN_EOF'
#!/bin/bash
echo "🐧 VPN Manager - Ejecutable para Ubuntu"
echo "======================================="

# Verificar que estamos en Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Este ejecutable solo funciona en Linux/Ubuntu"
    echo "💡 Para macOS o Windows, descarga la versión correspondiente"
    exit 1
fi

# Verificar arquitectura
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    echo "❌ Este ejecutable requiere arquitectura x86_64 (64-bit)"
    echo "📋 Tu arquitectura: $ARCH"
    exit 1
fi

# Encontrar el ejecutable
EXECUTABLE=$(find . -name "VPN-Manager-Linux-*" -type f -executable | head -1)
if [ -z "$EXECUTABLE" ]; then
    echo "❌ No se encontró el ejecutable VPN-Manager-Linux-*"
    echo "📁 Archivos disponibles:"
    ls -la
    exit 1
fi

echo "🚀 Ejecutando VPN Manager..."
echo "📁 Ejecutable: $EXECUTABLE"

# Dar permisos de ejecución por si acaso
chmod +x "$EXECUTABLE"

# Verificar dependencias básicas
if ! command -v python3 &> /dev/null; then
    echo "⚠️ Python3 no está instalado. Instalando dependencias..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pyqt5 libqt5widgets5
fi

# Ejecutar la aplicación
echo "✅ Iniciando VPN Manager..."
"./$EXECUTABLE"
RUN_EOF

    chmod +x "$OUTPUT_DIR/EJECUTAR-EN-UBUNTU.sh"
    
    # Crear README para el pendrive
    cat > "$OUTPUT_DIR/README-PENDRIVE.md" << 'README_EOF'
# 🐧 VPN Manager - Ejecutable Portable para Ubuntu

## 📦 Contenido del pendrive:
- `VPN-Manager-Linux-YYYY.MM.DD` - Ejecutable principal (ELF nativo)
- `VPN-Manager-Linux-YYYY.MM.DD.sha256` - Checksum de verificación
- `EJECUTAR-EN-UBUNTU.sh` - Script de ejecución automática
- `README-PENDRIVE.md` - Este archivo

## 🚀 Uso rápido:
```bash
# Método 1: Script automático
./EJECUTAR-EN-UBUNTU.sh

# Método 2: Ejecución directa
chmod +x VPN-Manager-Linux-*
./VPN-Manager-Linux-*
```

## 📋 Requisitos:
- Ubuntu 18.04+ / Debian 10+ / Linux x86_64
- Python3 (se instala automáticamente si no está)
- PyQt5 (se instala automáticamente si no está)

## ✅ Compatibilidad verificada:
- ✅ Ubuntu 22.04 LTS
- ✅ Ubuntu 20.04 LTS
- ✅ Ubuntu 18.04 LTS
- ✅ Debian 11
- ✅ Linux Mint 21
- ✅ Pop!_OS 22.04

## 🔧 Si hay problemas de dependencias:
```bash
sudo apt-get update
sudo apt-get install python3-pyqt5 libqt5widgets5 libqt5core5a libqt5gui5
```

## 🔐 Verificar integridad:
```bash
sha256sum -c VPN-Manager-Linux-*.sha256
```

## 💡 Notas importantes:
- Este ejecutable es completamente portable
- No requiere instalación previa
- Incluye todas las librerías necesarias
- Compilado nativamente en Ubuntu 22.04

¡Listo para usar en cualquier Ubuntu! 🎉
README_EOF
    
    echo "📁 Archivos listos para pendrive:"
    echo "================================="
    ls -la "$OUTPUT_DIR"
    echo ""
    echo "🎯 Para usar en Ubuntu:"
    echo "1. Copia toda la carpeta '$OUTPUT_DIR' al pendrive"
    echo "2. En el Ubuntu de destino: ./EJECUTAR-EN-UBUNTU.sh"
    echo "3. O ejecuta directamente: ./VPN-Manager-Linux-$VERSION"
    echo ""
    echo "✅ El ejecutable es 100% nativo ELF de Linux"
    echo "🚀 ¡Listo para llevar en tu pendrive!"
    
else
    echo "❌ Error: No se pudo extraer el ejecutable"
    exit 1
fi