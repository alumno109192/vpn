#!/bin/bash
# VPN Manager - Release Generator Script
# Automatiza la creación de releases con múltiples formatos de paquete

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes coloreados
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar dependencias
check_dependencies() {
    print_status "Verificando dependencias..."
    
    local missing_deps=()
    
    if ! command -v dpkg-deb &> /dev/null; then
        missing_deps+=("dpkg-deb")
    fi
    
    if ! command -v tar &> /dev/null; then
        missing_deps+=("tar")
    fi
    
    if ! command -v gzip &> /dev/null; then
        missing_deps+=("gzip")
    fi
    
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Faltan dependencias: ${missing_deps[*]}"
        print_error "Instala las dependencias faltantes y vuelve a ejecutar el script"
        exit 1
    fi
    
    print_success "Todas las dependencias están disponibles"
}

# Función para obtener la versión actual
get_current_version() {
    if [ -f "version.py" ]; then
        grep "__version__" version.py | sed 's/.*"\(.*\)".*/\1/'
    else
        print_error "No se encuentra version.py"
        exit 1
    fi
}

# Función para incrementar versión
increment_version() {
    local version=$1
    local type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $type in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            print_error "Tipo de incremento inválido: $type"
            print_error "Usa: major, minor, o patch"
            exit 1
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Función para actualizar version.py
update_version_file() {
    local new_version=$1
    print_status "Actualizando version.py a $new_version..."
    
    sed -i "s/__version__ = \".*\"/__version__ = \"$new_version\"/" version.py
    
    print_success "version.py actualizado"
}

# Función para limpiar directorios anteriores
cleanup_build_dirs() {
    print_status "Limpiando directorios de construcción anteriores..."
    
    rm -rf deb-package/vpn-manager_*_amd64
    rm -rf release/
    mkdir -p release/
    
    print_success "Directorios limpiados"
}

# Función para crear estructura del paquete .deb
create_deb_structure() {
    local version=$1
    local deb_dir="deb-package/vpn-manager_${version}_amd64"
    
    print_status "Creando estructura del paquete .deb..."
    
    # Crear directorios
    mkdir -p "$deb_dir/DEBIAN"
    mkdir -p "$deb_dir/usr/local/bin/vpn-manager"
    mkdir -p "$deb_dir/usr/share/applications"
    mkdir -p "$deb_dir/usr/share/doc/vpn-manager"
    
    # Crear archivo control
    cat > "$deb_dir/DEBIAN/control" << EOF
Package: vpn-manager
Version: $version
Section: net
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.8), python3-pyqt5, openvpn, python3-requests, python3-cryptography
Maintainer: Jorge Felix <jorge.felix@kuik.tech>
Description: VPN Manager Application v$version
 A comprehensive VPN management application with enhanced auto-update capabilities,
 license management, and user-friendly interface. Supports OpenVPN connections
 with advanced configuration options and automatic updates.
 .
 Features in v$version:
  - Enhanced auto-updater system with flexible asset detection
  - Support for multiple package formats (.deb, .tar.gz, .zip)
  - Improved error handling and user feedback
  - Better platform compatibility detection
  - Debian package with proper dependencies
  - Secure configuration handling
  - License management system
  - System tray integration
Homepage: https://github.com/alumno109192/vpn
EOF

    # Crear script postinst
    cat > "$deb_dir/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Make the main executable script executable
chmod +x /usr/local/bin/vpn-manager/vpn-manager

# Create symbolic link in PATH
if [ ! -L /usr/local/bin/vpn-manager-app ]; then
    ln -sf /usr/local/bin/vpn-manager/vpn-manager /usr/local/bin/vpn-manager-app
fi

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

echo "VPN Manager installation completed successfully!"
echo "You can run the application with: vpn-manager-app"
echo "Or find it in your applications menu as 'VPN Manager'."

exit 0
EOF

    # Crear script prerm
    cat > "$deb_dir/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Stop any running VPN connections
if command -v pkill >/dev/null 2>&1; then
    pkill -f "vpn-manager" || true
    pkill -f "openvpn" || true
fi

# Remove symbolic link
if [ -L /usr/local/bin/vpn-manager-app ]; then
    rm -f /usr/local/bin/vpn-manager-app
fi

echo "VPN Manager pre-removal completed."

exit 0
EOF

    # Crear script postrm
    cat > "$deb_dir/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications || true
fi

# Clean up any remaining configuration files (optional)
if [ "$1" = "purge" ]; then
    # Remove user configuration files if purging
    rm -rf /home/*/.config/vpn-manager/ 2>/dev/null || true
    echo "VPN Manager configuration files removed."
fi

echo "VPN Manager removal completed."

exit 0
EOF

    # Crear archivo .desktop
    cat > "$deb_dir/usr/share/applications/vpn-manager.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=VPN Manager
Comment=Manage VPN connections with enhanced auto-update capabilities (v$version)
Exec=/usr/local/bin/vpn-manager/vpn-manager
Icon=network-vpn
Terminal=false
Categories=Network;Security;
Keywords=VPN;OpenVPN;Network;Security;Connection;Manager;
StartupNotify=true
EOF

    # Crear script ejecutable principal
    cat > "$deb_dir/usr/local/bin/vpn-manager/vpn-manager" << EOF
#!/usr/bin/env python3
"""
VPN Manager v$version - Main executable script for .deb package
Enhanced auto-updater with flexible asset detection and multi-format support
"""

import sys
import os

# Add the application directory to Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

# Import and run the main application
try:
    from Main import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error importing main application: {e}")
    print("Please ensure all dependencies are installed:")
    print("sudo apt-get install python3-pyqt5 python3-requests python3-cryptography openvpn")
    sys.exit(1)
except Exception as e:
    print(f"Error running VPN Manager v$version: {e}")
    sys.exit(1)
EOF

    # Copiar archivos de la aplicación
    cp -r *.py dialogs/ threads/ CHANGELOG.md README.md requirements.txt "$deb_dir/usr/local/bin/vpn-manager/"
    
    # Crear archivo copyright
    cat > "$deb_dir/usr/share/doc/vpn-manager/copyright" << EOF
This package was debianized by Jorge Felix <jorge.felix@kuik.tech> on
$(date -R).

It was downloaded from:
https://github.com/alumno109192/vpn

Upstream Author(s):
Jorge Felix <jorge.felix@kuik.tech>

Copyright:
Copyright (C) 2025 Jorge Felix

License:
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

On Debian systems, the complete text of the GNU General
Public License can be found in \`/usr/share/common-licenses/GPL-2'.
EOF

    # Copiar y comprimir changelog
    cp CHANGELOG.md "$deb_dir/usr/share/doc/vpn-manager/changelog"
    gzip -9 "$deb_dir/usr/share/doc/vpn-manager/changelog"
    
    # Establecer permisos
    chmod 755 "$deb_dir/DEBIAN/postinst" "$deb_dir/DEBIAN/prerm" "$deb_dir/DEBIAN/postrm"
    chmod +x "$deb_dir/usr/local/bin/vpn-manager/vpn-manager"
    
    print_success "Estructura del paquete .deb creada"
}

# Función para construir el paquete .deb
build_deb_package() {
    local version=$1
    local deb_dir="deb-package/vpn-manager_${version}_amd64"
    
    print_status "Construyendo paquete .deb..."
    
    cd deb-package
    dpkg-deb --build "vpn-manager_${version}_amd64"
    mv "vpn-manager_${version}_amd64.deb" "../release/"
    cd ..
    
    local deb_size=$(ls -lh "release/vpn-manager_${version}_amd64.deb" | awk '{print $5}')
    print_success "Paquete .deb creado: vpn-manager_${version}_amd64.deb ($deb_size)"
}

# Función para crear paquete tar.gz
create_tar_package() {
    local version=$1
    
    print_status "Creando paquete tar.gz..."
    
    tar -czf "release/VPN-Manager-Linux-x64-v${version}.tar.gz" \
        --exclude='.git*' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.log' \
        --exclude='deb-package' \
        --exclude='build' \
        --exclude='linux-native-build' \
        --exclude='windows-build-kit' \
        --exclude='release' \
        *.py dialogs/ threads/ CHANGELOG.md README.md requirements.txt
    
    local tar_size=$(ls -lh "release/VPN-Manager-Linux-x64-v${version}.tar.gz" | awk '{print $5}')
    print_success "Paquete tar.gz creado: VPN-Manager-Linux-x64-v${version}.tar.gz ($tar_size)"
}

# Función para crear tag de git
create_git_tag() {
    local version=$1
    local tag_name="v$version"
    
    print_status "Creando tag de git: $tag_name..."
    
    # Verificar si hay cambios sin commit
    if ! git diff-index --quiet HEAD --; then
        print_warning "Hay cambios sin commit. Commiteando automáticamente..."
        git add .
        git commit -m "Release v$version - Auto-generated release packages"
    fi
    
    # Eliminar tag si ya existe
    if git tag -l | grep -q "^$tag_name$"; then
        print_warning "Tag $tag_name ya existe. Eliminando y recreando..."
        git tag -d "$tag_name"
        git push origin --delete "$tag_name" 2>/dev/null || true
    fi
    
    # Crear tag con mensaje detallado
    git tag -a "$tag_name" -m "Release v$version - Enhanced VPN Manager

Features:
- Enhanced auto-updater with flexible asset detection
- Improved error handling and user feedback
- Support for multiple package formats (tar.gz, .deb, zip, etc.)
- Better platform compatibility detection

Package formats:
- tar.gz: General Linux distribution package
- .deb: Debian/Ubuntu package with proper dependencies

Auto-updater improvements:
- Flexible file type detection with fallback options
- Enhanced _get_asset_url() method with pattern matching
- Better error messages and user guidance
- Support for tar.gz extraction and installation

Installation:
- .deb package: sudo dpkg -i vpn-manager_${version}_amd64.deb
- tar.gz package: Extract and run with Python 3.8+

Dependencies:
- Python 3.8+
- PyQt5
- OpenVPN
- python3-requests
- python3-cryptography"

    # Push tag
    git push origin "$tag_name"
    
    print_success "Tag $tag_name creado y subido a GitHub"
}

# Función para generar instrucciones de release
generate_release_instructions() {
    local version=$1
    local instructions_file="RELEASE_INSTRUCTIONS_v${version}.md"
    
    print_status "Generando instrucciones de release..."
    
    cat > "$instructions_file" << EOF
# Instrucciones para crear Release v$version en GitHub

## 📦 Archivos generados:
- \`vpn-manager_${version}_amd64.deb\` - Paquete Debian/Ubuntu
- \`VPN-Manager-Linux-x64-v${version}.tar.gz\` - Paquete Linux general

## 🚀 Pasos para crear la release:

### 1. Acceder a GitHub
- URL: https://github.com/alumno109192/vpn/releases/new?tag=v$version

### 2. Configurar Release
- **Tag version:** v$version (preseleccionado)
- **Release title:** VPN Manager v$version - Enhanced auto-updater

### 3. Descripción del Release
Copiar el siguiente texto:

\`\`\`markdown
## 🚀 VPN Manager v$version - Enhanced auto-updater

### ✨ Nuevas características:
- **Auto-updater mejorado** con detección flexible de archivos
- **Soporte multi-formato** (.deb, .tar.gz, .zip, etc.)
- **Mejor manejo de errores** y retroalimentación al usuario
- **Paquete Debian** con dependencias adecuadas
- **Compatibilidad mejorada** entre plataformas

### 📦 Formatos de paquete:
- **tar.gz**: Paquete general para distribuciones Linux
- **.deb**: Paquete Debian/Ubuntu con dependencias automáticas

### 🔧 Mejoras del auto-updater:
- Detección flexible de tipos de archivo con opciones de respaldo
- Método \`_get_asset_url()\` mejorado con coincidencia de patrones
- Mejores mensajes de error y orientación al usuario
- Soporte para extracción e instalación de tar.gz

### 📋 Instalación:

#### Para sistemas Debian/Ubuntu:
\`\`\`bash
sudo dpkg -i vpn-manager_${version}_amd64.deb
sudo apt-get install -f  # Solucionar dependencias si es necesario
\`\`\`

#### Para otras distribuciones Linux:
\`\`\`bash
tar -xzf VPN-Manager-Linux-x64-v${version}.tar.gz
cd VPN-Manager-Linux-x64-v${version}
python3 Main.py
\`\`\`

### 🔧 Dependencias:
- Python 3.8+
- PyQt5
- OpenVPN
- python3-requests
- python3-cryptography

### 📝 Notas:
- El auto-updater ahora detecta automáticamente el mejor formato de paquete
- Soporte mejorado para actualizaciones automáticas
- Interfaz de usuario más robusta
\`\`\`

### 4. Subir archivos
Arrastra los siguientes archivos:
- \`release/vpn-manager_${version}_amd64.deb\`
- \`release/VPN-Manager-Linux-x64-v${version}.tar.gz\`

### 5. Publicar
- ☑️ Marcar como "Latest release"
- ☐ NO marcar como "Pre-release"
- Click en "Publish release"

## ✅ Verificación post-release:
1. Verificar que ambos archivos están disponibles en la release
2. Probar la descarga de ambos paquetes
3. Verificar que el auto-updater detecta la nueva versión

## 📊 Estadísticas de la release:
- Versión anterior: $(git describe --tags --abbrev=0 HEAD~1 2>/dev/null || echo "N/A")
- Nueva versión: v$version
- Archivos incluidos: 2 (deb + tar.gz)
- Tag de git: Creado y subido
EOF

    print_success "Instrucciones generadas: $instructions_file"
}

# Función principal
main() {
    local version_type=""
    local new_version=""
    local current_version=""
    local auto_increment=false
    
    echo "=========================================="
    echo "    VPN Manager - Release Generator"
    echo "=========================================="
    echo
    
    # Procesar argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version)
                new_version="$2"
                shift 2
                ;;
            --increment)
                version_type="$2"
                auto_increment=true
                shift 2
                ;;
            --help|-h)
                echo "Uso: $0 [opciones]"
                echo
                echo "Opciones:"
                echo "  --version <version>     Especificar versión manualmente (ej: 1.4.0)"
                echo "  --increment <type>      Incrementar automáticamente: major, minor, patch"
                echo "  --help, -h             Mostrar esta ayuda"
                echo
                echo "Ejemplos:"
                echo "  $0 --version 1.4.0"
                echo "  $0 --increment patch"
                echo "  $0 --increment minor"
                exit 0
                ;;
            *)
                print_error "Opción desconocida: $1"
                echo "Usa --help para ver las opciones disponibles"
                exit 1
                ;;
        esac
    done
    
    # Verificar dependencias
    check_dependencies
    
    # Obtener versión actual
    current_version=$(get_current_version)
    print_status "Versión actual: $current_version"
    
    # Determinar nueva versión
    if [ "$auto_increment" = true ]; then
        new_version=$(increment_version "$current_version" "$version_type")
        print_status "Nueva versión (auto-incrementada): $new_version"
    elif [ -z "$new_version" ]; then
        echo
        print_warning "No se especificó versión. Opciones:"
        echo "1. Incrementar patch: $(increment_version "$current_version" "patch")"
        echo "2. Incrementar minor: $(increment_version "$current_version" "minor")"
        echo "3. Incrementar major: $(increment_version "$current_version" "major")"
        echo "4. Especificar manualmente"
        echo
        read -p "Selecciona opción (1-4): " choice
        
        case $choice in
            1) new_version=$(increment_version "$current_version" "patch") ;;
            2) new_version=$(increment_version "$current_version" "minor") ;;
            3) new_version=$(increment_version "$current_version" "major") ;;
            4) 
                read -p "Introduce la nueva versión: " new_version
                if [[ ! $new_version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                    print_error "Formato de versión inválido. Usa formato: X.Y.Z"
                    exit 1
                fi
                ;;
            *)
                print_error "Opción inválida"
                exit 1
                ;;
        esac
    fi
    
    print_success "Generando release v$new_version"
    echo
    
    # Actualizar version.py
    update_version_file "$new_version"
    
    # Limpiar directorios
    cleanup_build_dirs
    
    # Crear estructura .deb
    create_deb_structure "$new_version"
    
    # Construir paquete .deb
    build_deb_package "$new_version"
    
    # Crear paquete tar.gz
    create_tar_package "$new_version"
    
    # Crear tag de git
    create_git_tag "$new_version"
    
    # Generar instrucciones
    generate_release_instructions "$new_version"
    
    echo
    echo "=========================================="
    print_success "🎉 Release v$new_version generada exitosamente!"
    echo "=========================================="
    echo
    echo "📦 Archivos creados:"
    ls -lh release/
    echo
    echo "🚀 Próximos pasos:"
    echo "1. Lee las instrucciones: RELEASE_INSTRUCTIONS_v${new_version}.md"
    echo "2. Ve a: https://github.com/alumno109192/vpn/releases/new?tag=v$new_version"
    echo "3. Sube los archivos de la carpeta release/"
    echo "4. Publica la release"
    echo
}

# Ejecutar función principal con todos los argumentos
main "$@"
