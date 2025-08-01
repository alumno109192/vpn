#!/bin/bash

# Script simple para crear un release compatible con el sistema de actualizaciones
set -e

VERSION="1.0.1"  # Versión superior a la actual (1.0.0)
RELEASE_DIR="release_simple"

echo "🚀 Creando release simple v${VERSION} para pruebas..."

# Limpiar y crear directorio
rm -rf "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}"

# Crear directorio del proyecto
PROJECT_DIR="${RELEASE_DIR}/VPN-Manager-Linux-x64-${VERSION}"
mkdir -p "${PROJECT_DIR}"

echo "📂 Copiando archivos principales..."

# Copiar archivos esenciales
cp Main.py "${PROJECT_DIR}/"
cp -r dialogs/ "${PROJECT_DIR}/" 2>/dev/null || echo "⚠️ dialogs/ no encontrado"
cp -r threads/ "${PROJECT_DIR}/" 2>/dev/null || echo "⚠️ threads/ no encontrado"
cp -r services/ "${PROJECT_DIR}/" 2>/dev/null || echo "⚠️ services/ no encontrado"
cp models.py "${PROJECT_DIR}/" 2>/dev/null || echo "⚠️ models.py no encontrado"
cp auto_updater.py "${PROJECT_DIR}/" 2>/dev/null || echo "⚠️ auto_updater.py no encontrado"
cp license*.py "${PROJECT_DIR}/" 2>/dev/null || echo "⚠️ license*.py no encontrado"
cp requirements.txt "${PROJECT_DIR}/" 2>/dev/null || echo "⚠️ requirements.txt no encontrado"

# Crear version.py actualizada
cat > "${PROJECT_DIR}/version.py" << EOF
#!/usr/bin/env python3
"""
Configuración de versión para VPN Manager
"""

# Versión actual de la aplicación (formato semver)
__version__ = "${VERSION}"
__version_info__ = tuple(int(i) for i in __version__.split('.'))

# Información de la aplicación
APP_NAME = "VPN Manager"
APP_DESCRIPTION = "Una aplicación multiplataforma para gestionar conexiones VPN"
APP_AUTHOR = "VPN Manager Team"
APP_EMAIL = "contact@vpnmanager.example.com"

# Configuración del repositorio
GITHUB_REPO = "alumno109192/vpn"
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"

# URLs de la API
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"
RELEASES_API_URL = f"{GITHUB_API_BASE}/releases/latest"

# Configuración de actualización
AUTO_UPDATE_ENABLED = True
UPDATE_CHECK_INTERVAL = 24 * 60 * 60  # 24 horas en segundos
SILENT_UPDATE_CHECK = True  # Verificar actualizaciones silenciosamente al inicio

def get_version():
    """Retorna la versión actual como string"""
    return __version__

def get_version_info():
    """Retorna la información de versión como tupla"""
    return __version_info__

def get_app_info():
    """Retorna información completa de la aplicación"""
    return {
        "name": APP_NAME,
        "version": __version__,
        "description": APP_DESCRIPTION,
        "author": APP_AUTHOR,
        "email": APP_EMAIL
    }
EOF

# Crear script de instalación
cat > "${PROJECT_DIR}/install.sh" << 'EOF'
#!/bin/bash
echo "🚀 Actualizando VPN Manager..."

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado."
    exit 1
fi

# Instalar/actualizar dependencias
echo "📦 Verificando dependencias..."
python3 -m pip install --user -r requirements.txt 2>/dev/null || echo "⚠️ Algunas dependencias pueden faltar"

# Hacer ejecutable
chmod +x Main.py

echo "✅ Actualización completada!"
echo "Versión instalada: v1.0.1"
EOF

chmod +x "${PROJECT_DIR}/install.sh"

# Crear README
cat > "${PROJECT_DIR}/README.md" << EOF
# VPN Manager v${VERSION}

Esta es una actualización del VPN Manager.

## Cambios en esta versión:
- Mejoras en el sistema de actualizaciones
- Corrección de errores menores
- Mejor compatibilidad con Ubuntu

## Instalación:
\`\`\`bash
chmod +x install.sh
./install.sh
\`\`\`

## Ejecución:
\`\`\`bash
python3 Main.py
\`\`\`
EOF

# Crear archivo comprimido
cd "${RELEASE_DIR}"
tar -czf "VPN-Manager-Linux-x64-${VERSION}.tar.gz" "VPN-Manager-Linux-x64-${VERSION}/"

# Crear checksum
sha256sum "VPN-Manager-Linux-x64-${VERSION}.tar.gz" > "VPN-Manager-Linux-x64-${VERSION}.tar.gz.sha256"

cd ..

echo ""
echo "✅ Release simple creado exitosamente!"
echo "📁 Archivo generado: ${RELEASE_DIR}/VPN-Manager-Linux-x64-${VERSION}.tar.gz"
echo ""
echo "📋 Próximos pasos:"
echo "1. Crear tag de Git: git tag v${VERSION}"
echo "2. Push tag: git push origin v${VERSION}"
echo "3. Crear release en GitHub: https://github.com/alumno109192/vpn/releases/new"
echo "4. Subir el archivo: VPN-Manager-Linux-x64-${VERSION}.tar.gz"
echo ""
echo "🔍 Para probar:"
echo "   cd ${RELEASE_DIR}/VPN-Manager-Linux-x64-${VERSION}/"
echo "   python3 Main.py"
