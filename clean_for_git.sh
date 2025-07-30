#!/bin/bash

# Script para limpiar el proyecto antes de subirlo a GIT
# Este script elimina archivos de build, caché y otros archivos no necesarios

echo "🧹 Limpiando proyecto VPN Manager para GIT..."

# Eliminar archivos de caché de Python
echo "🗑️  Eliminando caché de Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true

# Eliminar directorios de build
echo "🗑️  Eliminando directorios de build..."
rm -rf build/ 2>/dev/null || true
rm -rf dist/ 2>/dev/null || true
rm -rf release/ 2>/dev/null || true
rm -rf deb_build/ 2>/dev/null || true
rm -rf linux-native-build/ 2>/dev/null || true
rm -rf windows-build-kit/ 2>/dev/null || true

# Eliminar archivos de configuración específicos
echo "🗑️  Eliminando archivos de configuración sensibles..."
rm -f connections.json 2>/dev/null || true
rm -f *.ovpn 2>/dev/null || true
rm -f *.log 2>/dev/null || true
rm -f vpn_setup.log 2>/dev/null || true

# Eliminar archivos de desarrollo y testing
echo "🗑️  Eliminando archivos de desarrollo..."
rm -f test_*.py 2>/dev/null || true
rm -f simulate_*.py 2>/dev/null || true
rm -f RESUMEN_FINAL.sh 2>/dev/null || true
rm -f PROYECTO_COMPLETADO.md 2>/dev/null || true
rm -f UPDATE_SYSTEM_SUMMARY.md 2>/dev/null || true
rm -f GUIA_USUARIO_FINAL.md 2>/dev/null || true

# Eliminar la mayoría de scripts de build (mantener solo los limpios)
echo "🗑️  Eliminando scripts de build antiguos..."
rm -f build_all_platforms.sh 2>/dev/null || true
rm -f build_deb.sh 2>/dev/null || true
rm -f build_executable.py 2>/dev/null || true
rm -f build_linux_ultimate_fixed.sh 2>/dev/null || true
rm -f build_linux_ultimate.sh 2>/dev/null || true
rm -f build_linux.sh 2>/dev/null || true
rm -f build_macos_fixed.sh 2>/dev/null || true
rm -f build_macos_simple.sh 2>/dev/null || true
rm -f build_macos_ultimate.sh 2>/dev/null || true
rm -f build_macos.sh 2>/dev/null || true
rm -f build_multiplatform.py 2>/dev/null || true
rm -f build_windows_ultimate.bat 2>/dev/null || true
rm -f build_windows.bat 2>/dev/null || true
rm -f build-ubuntu-native.sh 2>/dev/null || true
rm -f create_windows_executable.py 2>/dev/null || true
rm -f package_all_final.sh 2>/dev/null || true
rm -f Dockerfile.linux-build 2>/dev/null || true

# Eliminar archivos spec de PyInstaller
echo "🗑️  Eliminando archivos .spec..."
rm -f *.spec 2>/dev/null || true

# Eliminar archivos temporales del sistema
echo "🗑️  Eliminando archivos temporales..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true

# Reemplazar archivos con versiones limpias
echo "📝 Actualizando archivos principales..."
if [ -f "README_CLEAN.md" ]; then
    mv README_CLEAN.md README.md
    echo "   ✅ README actualizado"
fi

if [ -f "CHANGELOG_CLEAN.md" ]; then
    mv CHANGELOG_CLEAN.md CHANGELOG.md
    echo "   ✅ CHANGELOG actualizado"
fi

# Hacer ejecutables los scripts de build limpios
chmod +x build_linux_clean.sh 2>/dev/null || true

echo ""
echo "✅ Limpieza completada!"
echo ""
echo "📋 Archivos principales del proyecto:"
echo "   - Main.py (aplicación principal)"
echo "   - models.py (modelos de datos)"
echo "   - version.py (información de versión)"
echo "   - requirements.txt (dependencias)"
echo "   - dialogs/ (diálogos de UI)"
echo "   - threads/ (hilos de VPN)"
echo "   - services/ (servicios del sistema)"
echo "   - auto_updater.py (actualizaciones)"
echo "   - license*.py (sistema de licencias)"
echo ""
echo "📁 Scripts de build disponibles:"
echo "   - build_linux_clean.sh"
echo "   - build_windows_clean.bat"
echo ""
echo "📖 Documentación:"
echo "   - README.md"
echo "   - CHANGELOG.md"
echo "   - CONTRIBUTING.md"
echo "   - LICENSE"
echo ""
echo "🚀 El proyecto está listo para subir a GIT!"
echo "   Comandos sugeridos:"
echo "   git add ."
echo "   git commit -m 'Initial commit: VPN Manager v1.0.0'"
echo "   git push origin main"
