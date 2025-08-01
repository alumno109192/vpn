#!/bin/bash
# Script para crear releases compatibles con el sistema de actualizaciones
set -e

# Variables
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RELEASE_DIR="$PROJECT_DIR/release"
VERSION="1.0.1"  # Cambiar según la versión actual

echo "🚀 Generando releases para la versión $VERSION..."

# Crear directorio de releases si no existe
mkdir -p "$RELEASE_DIR"

# 1. Linux Release (.deb)
if [ -f "$PROJECT_DIR/deb_build/vpn-manager-ubuntu.deb" ]; then
    echo "📦 Creando release para Linux..."
    cp "$PROJECT_DIR/deb_build/vpn-manager-ubuntu.deb" "$RELEASE_DIR/vpn-manager-linux-v$VERSION.deb"
    
    # Crear también un tar.gz con el ejecutable
    if [ -f "$PROJECT_DIR/dist/VPN-Manager" ]; then
        mkdir -p "$RELEASE_DIR/temp-linux"
        cp "$PROJECT_DIR/dist/VPN-Manager" "$RELEASE_DIR/temp-linux/vpn-manager"
        chmod +x "$RELEASE_DIR/temp-linux/vpn-manager"
        
        # Crear README para Linux
        cat > "$RELEASE_DIR/temp-linux/README.md" << EOF
# VPN Manager v$VERSION - Linux

## Instalación desde .deb (Recomendado)
\`\`\`bash
sudo dpkg -i vpn-manager-linux-v$VERSION.deb
sudo apt-get install -f  # Si hay dependencias faltantes
\`\`\`

## Ejecución directa
\`\`\`bash
chmod +x vpn-manager
./vpn-manager
\`\`\`

## Dependencias requeridas
- python3
- python3-pyqt5
- openvpn
- strongswan

## Instalar dependencias manualmente
\`\`\`bash
sudo apt-get update
sudo apt-get install python3 python3-pyqt5 openvpn strongswan
\`\`\`
EOF
        
        cd "$RELEASE_DIR"
        tar -czf "vpn-manager-linux-v$VERSION.tar.gz" -C temp-linux .
        rm -rf temp-linux
        echo "✅ Linux release creado: vpn-manager-linux-v$VERSION.tar.gz"
        echo "✅ Linux .deb creado: vpn-manager-linux-v$VERSION.deb"
    else
        echo "⚠️  No se encontró el ejecutable dist/VPN-Manager"
    fi
else
    echo "❌ No se encontró vpn-manager-ubuntu.deb. Ejecuta build_deb.sh primero."
fi

# 2. Windows Release (si existe)
if [ -d "$PROJECT_DIR/release/VPN-Manager-Windows-x64" ]; then
    echo "📦 Creando release para Windows..."
    cd "$PROJECT_DIR/release"
    zip -r "$RELEASE_DIR/vpn-manager-windows-v$VERSION.zip" VPN-Manager-Windows-x64/
    echo "✅ Windows release creado: vpn-manager-windows-v$VERSION.zip"
else
    echo "⚠️  No se encontró build de Windows"
fi

# 3. macOS Release (si existe)
if [ -d "$PROJECT_DIR/release/VPN-Manager-macOS-Ultimate" ]; then
    echo "📦 Creando release para macOS..."
    cd "$PROJECT_DIR/release"
    zip -r "$RELEASE_DIR/vpn-manager-macos-v$VERSION.zip" VPN-Manager-macOS-Ultimate/
    echo "✅ macOS release creado: vpn-manager-macos-v$VERSION.zip"
else
    echo "⚠️  No se encontró build de macOS"
fi

# Mostrar resumen
echo ""
echo "🎉 Releases generados en: $RELEASE_DIR"
echo "📋 Archivos creados:"
ls -la "$RELEASE_DIR"/vpn-manager-*-v$VERSION.*

echo ""
echo "📤 Para subir a GitHub:"
echo "1. Ve a: https://github.com/alumno109192/vpn/releases/new"
echo "2. Tag version: v$VERSION"
echo "3. Release title: VPN Manager v$VERSION"
echo "4. Sube los archivos generados"
echo ""
echo "🔗 Comandos Git (opcional):"
echo "git tag v$VERSION"
echo "git push origin v$VERSION"
