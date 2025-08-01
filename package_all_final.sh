#!/bin/bash

# Script final para generar y empaquetar ejecutables para todas las plataformas
# ===========================================================================

echo "🎯 VPN Manager - Empaquetado Final Multiplataforma"
echo "=================================================="

# Variables
DATE=$(date +%Y.%m.%d)
WORKSPACE_DIR=$(pwd)
RELEASE_DIR="$WORKSPACE_DIR/release"

# Crear directorio de release si no existe
mkdir -p "$RELEASE_DIR"

echo "📅 Fecha: $DATE"
echo "📁 Workspace: $WORKSPACE_DIR"
echo "📦 Release: $RELEASE_DIR"
echo ""

# Función para mostrar tamaño de archivo
get_file_size() {
    if [ -f "$1" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            stat -f%z "$1" | awk '{printf "%.1f MB", $1/1024/1024}'
        else
            # Linux
            stat -c%s "$1" | awk '{printf "%.1f MB", $1/1024/1024}'
        fi
    else
        echo "N/A"
    fi
}

# Función para crear el paquete Windows
create_windows_package() {
    echo "🪟 Empaquetando kit de build para Windows..."
    
    if [ -d "windows-build-kit" ]; then
        cd "$WORKSPACE_DIR"
        
        # Crear archivo ZIP del kit de Windows
        WINDOWS_KIT_ZIP="$RELEASE_DIR/VPN-Manager-Windows-BuildKit-$DATE.zip"
        
        echo "📦 Creando: $(basename "$WINDOWS_KIT_ZIP")"
        zip -r "$WINDOWS_KIT_ZIP" windows-build-kit/ -x "*.pyc" "*/__pycache__/*" > /dev/null 2>&1
        
        if [ -f "$WINDOWS_KIT_ZIP" ]; then
            echo "✅ Kit Windows creado: $(basename "$WINDOWS_KIT_ZIP") ($(get_file_size "$WINDOWS_KIT_ZIP"))"
            
            # Crear instrucciones rápidas
            cat > "$RELEASE_DIR/INSTRUCCIONES-WINDOWS.txt" << 'EOF'
VPN Manager - Instrucciones para Windows
========================================

1. DESCARGAR: VPN-Manager-Windows-BuildKit-[FECHA].zip

2. EXTRAER: Extrae el ZIP en una máquina Windows

3. EJECUTAR: Abre Command Prompt y ejecuta:
   cd windows-build-kit
   build_windows.bat

4. RESULTADO: El ejecutable estará en dist\VPN-Manager-Windows\

5. DISTRIBUIR: Comprime la carpeta dist\VPN-Manager-Windows\ para distribuir

NOTA: Necesitas Python 3.8+ instalado en Windows
EOF
            echo "📋 Instrucciones creadas: INSTRUCCIONES-WINDOWS.txt"
        else
            echo "❌ Error al crear kit Windows"
        fi
    else
        echo "⚠️  Directorio windows-build-kit no encontrado"
    fi
}

# Función para generar reporte final
generate_final_report() {
    echo ""
    echo "📊 REPORTE FINAL - EJECUTABLES VPN MANAGER"
    echo "=========================================="
    
    echo ""
    echo "🍎 macOS:"
    echo "--------"
    MACOS_ZIP="$RELEASE_DIR/VPN-Manager-macOS-$DATE.zip"
    if [ -f "$MACOS_ZIP" ]; then
        echo "✅ $(basename "$MACOS_ZIP") ($(get_file_size "$MACOS_ZIP"))"
        echo "   📁 Tipo: Ejecutable nativo macOS"
        echo "   🚀 Instalación: Extraer ZIP y ejecutar"
        echo "   💻 Compatibilidad: macOS 10.14+"
    else
        echo "❌ No encontrado"
    fi
    
    echo ""
    echo "🐧 Linux:"
    echo "--------"
    LINUX_TAR="$RELEASE_DIR/VPN-Manager-Linux-x64-$DATE.tar.gz"
    if [ -f "$LINUX_TAR" ]; then
        echo "✅ $(basename "$LINUX_TAR") ($(get_file_size "$LINUX_TAR"))"
        echo "   📁 Tipo: Ejecutable nativo Linux x64"
        echo "   🚀 Instalación: tar -xzf archivo.tar.gz && ./run.sh"
        echo "   💻 Compatibilidad: Ubuntu 18.04+, CentOS 7+, Debian 9+"
    else
        echo "❌ No encontrado"
    fi
    
    echo ""
    echo "🪟 Windows:"
    echo "----------"
    WINDOWS_KIT="$RELEASE_DIR/VPN-Manager-Windows-BuildKit-$DATE.zip"
    if [ -f "$WINDOWS_KIT" ]; then
        echo "✅ $(basename "$WINDOWS_KIT") ($(get_file_size "$WINDOWS_KIT"))"
        echo "   📁 Tipo: Kit de build (requiere compilación en Windows)"
        echo "   🚀 Instalación: Extraer y ejecutar build_windows.bat"
        echo "   💻 Compatibilidad: Windows 10/11 + Python 3.8+"
    else
        echo "❌ No encontrado"
    fi
    
    echo ""
    echo "📈 ESTADÍSTICAS:"
    echo "==============="
    
    total_files=0
    total_size=0
    
    for file in "$RELEASE_DIR"/*.zip "$RELEASE_DIR"/*.tar.gz; do
        if [ -f "$file" ]; then
            ((total_files++))
            if [[ "$OSTYPE" == "darwin"* ]]; then
                size=$(stat -f%z "$file")
            else
                size=$(stat -c%s "$file")
            fi
            ((total_size+=size))
        fi
    done
    
    echo "📦 Total de paquetes: $total_files"
    echo "💾 Tamaño total: $(echo "$total_size" | awk '{printf "%.1f MB", $1/1024/1024}')"
    
    echo ""
    echo "🎯 PRÓXIMOS PASOS:"
    echo "=================="
    echo "1. ✅ macOS y Linux están listos para distribución"
    echo "2. 🔄 Para Windows: usar el BuildKit en una máquina Windows"
    echo "3. 📤 Subir archivos a GitHub Releases o servidor de descarga"
    echo "4. 📝 Actualizar documentación con enlaces de descarga"
    
    echo ""
    echo "🌐 ENLACES DE DISTRIBUCIÓN:"
    echo "=========================="
    echo "• macOS: $(basename "$MACOS_ZIP")"
    echo "• Linux: $(basename "$LINUX_TAR")"
    echo "• Windows: $(basename "$WINDOWS_KIT")"
}

# Función para crear script de distribución
create_distribution_script() {
    cat > "$RELEASE_DIR/upload_releases.sh" << 'EOF'
#!/bin/bash
# Script para subir releases a GitHub (requiere gh CLI)

echo "🚀 Subiendo releases a GitHub..."

# Verificar gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI no encontrado. Instala con: brew install gh"
    exit 1
fi

# Variables
REPO="tu-usuario/vpn-manager"  # Cambia esto por tu repo
TAG="v$(date +%Y.%m.%d)"
TITLE="VPN Manager $TAG"

echo "📦 Creando release $TAG..."

# Crear release
gh release create "$TAG" \
    --title "$TITLE" \
    --notes "VPN Manager - Ejecutables para todas las plataformas" \
    VPN-Manager-*.zip \
    VPN-Manager-*.tar.gz

echo "✅ Release creado: https://github.com/$REPO/releases/tag/$TAG"
EOF

    chmod +x "$RELEASE_DIR/upload_releases.sh"
    echo "📤 Script de distribución creado: upload_releases.sh"
}

# EJECUCIÓN PRINCIPAL
echo "🚀 Iniciando empaquetado final..."

# Crear paquete Windows
create_windows_package

# Crear script de distribución
create_distribution_script

# Generar reporte final
generate_final_report

echo ""
echo "✨ ¡EMPAQUETADO COMPLETADO!"
echo "========================="
echo "📁 Todos los archivos están en: release/"
echo "📋 Revisa INSTRUCCIONES-WINDOWS.txt para completar Windows"
echo ""
