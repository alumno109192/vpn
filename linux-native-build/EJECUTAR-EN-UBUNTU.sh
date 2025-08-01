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
