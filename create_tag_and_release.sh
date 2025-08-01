#!/bin/bash

# Script automatizado para crear releases de VPN Manager
set -e

VERSION="1.2.1"
REPO="alumno109192/vpn"
RELEASE_FILE="release/vpn-manager-linux-v${VERSION}.tar.gz"

echo "🚀 Creando release v${VERSION} para VPN Manager..."

# Verificar que el archivo de release existe
if [ ! -f "$RELEASE_FILE" ]; then
    echo "❌ No se encontró el archivo de release: $RELEASE_FILE"
    echo "Ejecuta primero: ./create_release.sh"
    exit 1
fi

# Verificar git status
echo "📋 Verificando estado de Git..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Tienes cambios sin commitear. ¿Quieres continuar? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "❌ Cancelado. Commitea tus cambios primero."
        exit 1
    fi
fi

# Verificar si el tag ya existe
if git rev-parse "v${VERSION}" >/dev/null 2>&1; then
    echo "⚠️  El tag v${VERSION} ya existe. ¿Quieres eliminarlo y recrearlo? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        git tag -d "v${VERSION}"
        git push origin --delete "v${VERSION}" 2>/dev/null || true
    else
        echo "❌ Cancelado."
        exit 1
    fi
fi

# Crear el tag
echo "🏷️  Creando tag v${VERSION}..."
git tag -a "v${VERSION}" -m "VPN Manager v${VERSION} - Improved Update System

- Enhanced asset detection for Linux/Ubuntu platforms
- Added support for multiple archive formats (.tar.gz, .deb, .zip)
- Improved error handling and logging during updates
- Fixed 'No compatible asset found' error on Ubuntu
- Added automatic backup system during updates"

# Subir el tag
echo "📤 Subiendo tag al repositorio..."
git push origin "v${VERSION}"

# Mostrar información del archivo
echo ""
echo "📦 Información del release:"
echo "   Archivo: $RELEASE_FILE"
echo "   Tamaño: $(ls -lh "$RELEASE_FILE" | awk '{print $5}')"
echo "   SHA256: $(shasum -a 256 "$RELEASE_FILE" | awk '{print $1}')"

echo ""
echo "✅ Tag v${VERSION} creado y subido exitosamente!"
echo ""
echo "🌐 Próximos pasos:"
echo "1. Ve a: https://github.com/${REPO}/releases/new"
echo "2. Selecciona el tag: v${VERSION}"
echo "3. Título: VPN Manager v${VERSION} - Improved Update System"
echo "4. Sube el archivo: ${RELEASE_FILE}"
echo ""
echo "📋 O copia esta descripción para el release:"
echo "================================="
cat << 'EOF'
## 🔄 VPN Manager v1.2.1 - Sistema de Actualizaciones Mejorado

### ✨ Nuevas Características
- **Sistema de actualizaciones automáticas mejorado** - Mejor detección de assets compatibles para Linux/Ubuntu
- **Soporte ampliado para formatos de archivo** - Compatibilidad con .tar.gz, .deb, .zip
- **Detección inteligente de plataforma** - Reconocimiento automático de arquitectura

### 🐛 Correcciones
- Solucionado: Error "No se encontró un asset compatible para tu sistema" en Ubuntu
- Mejorado: Logging detallado para debugging de actualizaciones
- Corregido: Detección de archivos genéricos cuando no hay assets específicos

### 📦 Instalación
```bash
# Descargar y extraer
wget https://github.com/alumno109192/vpn/releases/download/v1.2.1/vpn-manager-linux-v1.2.1.tar.gz
tar -xzf vpn-manager-linux-v1.2.1.tar.gz

# Ejecutar
python3 Main.py
```

### 🔄 Actualización Automática
La aplicación detectará automáticamente esta versión si tienes v1.2.0 o anterior.
EOF
echo "================================="
echo ""
echo "🎯 URL directa: https://github.com/${REPO}/releases/new?tag=v${VERSION}"

# Abrir URL automáticamente (si está en macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "🌐 Abriendo GitHub en el navegador..."
    open "https://github.com/${REPO}/releases/new?tag=v${VERSION}"
fi
