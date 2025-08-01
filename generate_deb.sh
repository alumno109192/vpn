#!/bin/bash
#
# Script para generar paquete .deb de VPN Manager
# Genera automáticamente un paquete Debian listo para instalar
#

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Obtener información de la aplicación
get_app_info() {
    # Extraer versión del archivo version.py
    VERSION=$(python3 -c "
import sys
sys.path.append('.')
from version import __version__
print(__version__)
")
    
    if [ -z "$VERSION" ]; then
        error "No se pudo obtener la versión de la aplicación"
        exit 1
    fi
    
    APP_NAME="vpn-manager"
    PACKAGE_NAME="vpn-manager"
    DESCRIPTION="Una aplicación multiplataforma para gestionar conexiones VPN"
    MAINTAINER="Jorge Kuik <yesod3d@gmail.com>"
    HOMEPAGE="https://github.com/alumno109192/vpn"
    
    log "Información de la aplicación:"
    info "  Nombre: $APP_NAME"
    info "  Versión: $VERSION"
    info "  Descripción: $DESCRIPTION"
}

# Verificar dependencias necesarias
check_dependencies() {
    log "Verificando dependencias..."
    
    local missing_deps=()
    
    # Verificar herramientas de empaquetado
    if ! command -v dpkg-deb >/dev/null 2>&1; then
        missing_deps+=("dpkg-deb")
    fi
    
    if ! command -v fakeroot >/dev/null 2>&1; then
        missing_deps+=("fakeroot")
    fi
    
    # Verificar Python y dependencias
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        error "Faltan las siguientes dependencias:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        info "Instala las dependencias con:"
        info "  sudo apt update && sudo apt install -y ${missing_deps[*]}"
        exit 1
    fi
    
    log "Todas las dependencias están disponibles"
}

# Crear estructura del paquete .deb
create_package_structure() {
    log "Creando estructura del paquete..."
    
    # Crear directorios base
    DEB_DIR="debian-package"
    BUILD_DIR="$DEB_DIR/${PACKAGE_NAME}_${VERSION}_amd64"
    
    # Limpiar construcción anterior si existe
    if [ -d "$DEB_DIR" ]; then
        rm -rf "$DEB_DIR"
    fi
    
    mkdir -p "$BUILD_DIR"
    
    # Crear estructura de directorios del paquete
    mkdir -p "$BUILD_DIR/DEBIAN"
    mkdir -p "$BUILD_DIR/usr/local/bin/vpn-manager"
    mkdir -p "$BUILD_DIR/usr/share/applications"
    mkdir -p "$BUILD_DIR/usr/share/doc/vpn-manager"
    mkdir -p "$BUILD_DIR/usr/share/man/man1"
    mkdir -p "$BUILD_DIR/etc/vpn-manager"
    
    log "Estructura de directorios creada en $BUILD_DIR"
}

# Generar archivo de control DEBIAN
generate_control_file() {
    log "Generando archivo de control..."
    
    cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: net
Priority: optional
Architecture: amd64
Essential: no
Depends: python3 (>= 3.6), python3-pyqt5, openvpn, strongswan
Recommends: network-manager
Suggests: network-manager-openvpn
Installed-Size: $(du -sk . | cut -f1)
Maintainer: $MAINTAINER
Description: $DESCRIPTION
 VPN Manager es una aplicación gráfica que permite gestionar conexiones
 VPN de manera sencilla. Soporta OpenVPN e IPSec/StrongSwan.
 .
 Características principales:
  - Interfaz gráfica intuitiva con PyQt5
  - Soporte para múltiples conexiones VPN
  - Gestión desde el área de notificaciones
  - Reconexión automática
  - Sistema de licencias y períodos de prueba
  - Actualizaciones automáticas
Homepage: $HOMEPAGE
EOF
    
    info "Archivo control generado con dependencias: python3-pyqt5, openvpn, strongswan"
}

# Generar scripts de instalación
generate_install_scripts() {
    log "Generando scripts de instalación..."
    
    # Script post-instalación
    cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Configurar permisos
chown -R root:root /usr/local/bin/vpn-manager
chmod +x /usr/local/bin/vpn-manager/vpn-manager
chmod +x /usr/local/bin/vpn-manager-app

# Crear enlace simbólico si no existe
if [ ! -e /usr/local/bin/vpn-manager-app ]; then
    ln -sf /usr/local/bin/vpn-manager/vpn-manager /usr/local/bin/vpn-manager-app
fi

# Actualizar base de datos de aplicaciones
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Mostrar mensaje de instalación exitosa
echo "VPN Manager instalado correctamente."
echo "Puedes ejecutarlo desde el menú de aplicaciones o con el comando: vpn-manager-app"

exit 0
EOF

    # Script pre-eliminación
    cat > "$BUILD_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Detener cualquier proceso de VPN Manager que esté ejecutándose
pkill -f "python.*Main.py" || true
pkill -f "vpn-manager" || true

exit 0
EOF

    # Script post-eliminación
    cat > "$BUILD_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

case "$1" in
    remove|purge)
        # Remover enlace simbólico
        rm -f /usr/local/bin/vpn-manager-app
        
        # Actualizar base de datos de aplicaciones
        if command -v update-desktop-database >/dev/null 2>&1; then
            update-desktop-database /usr/share/applications
        fi
        
        # En purge, remover configuración de usuario
        if [ "$1" = "purge" ]; then
            # Remover configuraciones de sistema (pero no de usuarios individuales)
            rm -rf /etc/vpn-manager 2>/dev/null || true
        fi
        ;;
esac

exit 0
EOF

    # Hacer scripts ejecutables
    chmod 755 "$BUILD_DIR/DEBIAN/postinst"
    chmod 755 "$BUILD_DIR/DEBIAN/prerm"
    chmod 755 "$BUILD_DIR/DEBIAN/postrm"
    
    info "Scripts de instalación creados y configurados"
}

# Copiar archivos de la aplicación
copy_application_files() {
    log "Copiando archivos de la aplicación..."
    
    # Lista de archivos Python principales
    local python_files=(
        "Main.py"
        "version.py"
        "auto_updater.py"
        "license.py"
        "license_generator.py"
        "license_encryptor.py"
        "license_storage.py"
        "models.py"
        "run_vpn.py"
    )
    
    # Copiar archivos Python principales
    for file in "${python_files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$BUILD_DIR/usr/local/bin/vpn-manager/"
            info "  Copiado: $file"
        else
            warning "  Archivo no encontrado: $file"
        fi
    done
    
    # Copiar directorios adicionales
    local directories=(
        "dialogs"
        "threads"
    )
    
    for dir in "${directories[@]}"; do
        if [ -d "$dir" ]; then
            cp -r "$dir" "$BUILD_DIR/usr/local/bin/vpn-manager/"
            info "  Copiado directorio: $dir"
        else
            warning "  Directorio no encontrado: $dir"
        fi
    done
    
    # Copiar requirements.txt si existe
    if [ -f "requirements.txt" ]; then
        cp "requirements.txt" "$BUILD_DIR/usr/share/doc/vpn-manager/"
        info "  Copiado: requirements.txt"
    fi
    
    # Copiar archivos de documentación
    local doc_files=(
        "README.md"
        "CHANGELOG.md"
        "GUIA_USUARIO_FINAL.md"
    )
    
    for file in "${doc_files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$BUILD_DIR/usr/share/doc/vpn-manager/"
            info "  Copiado doc: $file"
        fi
    done
}

# Crear script ejecutable principal
create_executable_script() {
    log "Creando script ejecutable principal..."
    
    cat > "$BUILD_DIR/usr/local/bin/vpn-manager/vpn-manager" << 'EOF'
#!/bin/bash
#
# Script ejecutable para VPN Manager
# Este script lanza la aplicación Python con el entorno correcto
#

# Directorio de la aplicación
APP_DIR="/usr/local/bin/vpn-manager"

# Cambiar al directorio de la aplicación
cd "$APP_DIR"

# Usar el Python del sistema para evitar conflictos con Homebrew
SYSTEM_PYTHON="/usr/bin/python3"

# Verificar que Python3 del sistema esté disponible
if [ ! -f "$SYSTEM_PYTHON" ]; then
    echo "Error: Python3 del sistema no está instalado" >&2
    exit 1
fi

# Verificar PyQt5
if ! $SYSTEM_PYTHON -c "import PyQt5" 2>/dev/null; then
    echo "Error: PyQt5 no está instalado. Instálalo con: sudo apt install python3-pyqt5" >&2
    exit 1
fi

# Ejecutar la aplicación principal con el Python del sistema
exec $SYSTEM_PYTHON "$APP_DIR/Main.py" "$@"
EOF

    # Hacer el script ejecutable
    chmod +x "$BUILD_DIR/usr/local/bin/vpn-manager/vpn-manager"
    
    # Crear enlace simbólico en /usr/local/bin
    cat > "$BUILD_DIR/usr/local/bin/vpn-manager-app" << 'EOF'
#!/bin/bash
exec /usr/local/bin/vpn-manager/vpn-manager "$@"
EOF
    chmod +x "$BUILD_DIR/usr/local/bin/vpn-manager-app"
    
    info "Script ejecutable creado"
}

# Crear archivo .desktop para el menú de aplicaciones
create_desktop_file() {
    log "Creando archivo .desktop..."
    
    cat > "$BUILD_DIR/usr/share/applications/vpn-manager.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=VPN Manager
Comment=$DESCRIPTION
Exec=vpn-manager-app
Icon=network-vpn
Terminal=false
StartupNotify=true
Categories=Network;Security;
Keywords=vpn;network;security;openvpn;ipsec;
StartupWMClass=vpn-manager
EOF
    
    info "Archivo .desktop creado para integración en el menú"
}

# Crear página de manual
create_man_page() {
    log "Creando página de manual..."
    
    cat > "$BUILD_DIR/usr/share/man/man1/vpn-manager.1" << EOF
.TH VPN-MANAGER 1 "$(date +'%B %Y')" "vpn-manager $VERSION" "User Commands"
.SH NAME
vpn-manager \- Una aplicación multiplataforma para gestionar conexiones VPN
.SH SYNOPSIS
.B vpn-manager
.SH DESCRIPTION
VPN Manager es una aplicación gráfica que permite gestionar conexiones VPN de manera sencilla.
Soporta OpenVPN e IPSec/StrongSwan con una interfaz intuitiva.
.PP
La aplicación proporciona:
.IP \(bu 2
Interfaz gráfica intuitiva con PyQt5
.IP \(bu 2
Soporte para múltiples conexiones VPN
.IP \(bu 2
Gestión desde el área de notificaciones
.IP \(bu 2
Reconexión automática
.IP \(bu 2
Sistema de licencias y períodos de prueba
.IP \(bu 2
Actualizaciones automáticas
.SH FILES
.TP
.B /usr/local/bin/vpn-manager/
Directorio de instalación de la aplicación
.TP
.B ~/.config/vpn-manager/
Directorio de configuración del usuario
.SH AUTHOR
Jorge Kuik <yesod3d@gmail.com>
.SH "SEE ALSO"
.BR openvpn (8),
.BR ipsec (8)
EOF

    # Comprimir la página del manual
    gzip "$BUILD_DIR/usr/share/man/man1/vpn-manager.1"
    
    info "Página de manual creada y comprimida"
}

# Construir el paquete .deb
build_deb_package() {
    log "Construyendo paquete .deb..."
    
    # Calcular el tamaño instalado (en KB)
    INSTALLED_SIZE=$(du -sk "$BUILD_DIR" | cut -f1)
    
    # Actualizar el tamaño en el archivo control
    sed -i "s/Installed-Size: .*/Installed-Size: $INSTALLED_SIZE/" "$BUILD_DIR/DEBIAN/control"
    
    # Construir el paquete usando fakeroot para permisos correctos
    cd "$DEB_DIR"
    
    DEB_FILE="${PACKAGE_NAME}_${VERSION}_amd64.deb"
    
    if command -v fakeroot >/dev/null 2>&1; then
        fakeroot dpkg-deb --build "${PACKAGE_NAME}_${VERSION}_amd64" "$DEB_FILE"
    else
        dpkg-deb --build "${PACKAGE_NAME}_${VERSION}_amd64" "$DEB_FILE"
    fi
    
    cd ..
    
    # Mover el paquete al directorio release
    mkdir -p release
    mv "$DEB_DIR/$DEB_FILE" "release/"
    
    # Mostrar información del paquete generado
    log "Paquete .deb generado exitosamente:"
    info "  Archivo: release/$DEB_FILE"
    info "  Tamaño: $(ls -lh "release/$DEB_FILE" | awk '{print $5}')"
    
    # Verificar el paquete
    if command -v dpkg-deb >/dev/null 2>&1; then
        log "Verificando paquete..."
        dpkg-deb --info "release/$DEB_FILE"
        echo
        log "Contenido del paquete:"
        dpkg-deb --contents "release/$DEB_FILE"
    fi
}

# Crear instrucciones de instalación
create_installation_instructions() {
    log "Creando instrucciones de instalación..."
    
    cat > "release/INSTRUCCIONES_INSTALACION_DEB.md" << EOF
# Instrucciones de Instalación - VPN Manager v$VERSION

## Instalación del paquete .deb

### Método 1: Instalación directa con apt
\`\`\`bash
sudo apt update
sudo apt install ./vpn-manager_${VERSION}_amd64.deb
\`\`\`

### Método 2: Instalación con dpkg
\`\`\`bash
sudo dpkg -i vpn-manager_${VERSION}_amd64.deb
sudo apt install -f  # Instalar dependencias si faltan
\`\`\`

## Dependencias requeridas

El paquete instalará automáticamente las siguientes dependencias:
- python3 (>= 3.6)
- python3-pyqt5
- openvpn
- strongswan

## Uso de la aplicación

### Ejecutar desde terminal
\`\`\`bash
vpn-manager-app
\`\`\`

### Ejecutar desde el menú de aplicaciones
Busca "VPN Manager" en el menú de aplicaciones de tu escritorio.

## Archivos instalados

- **Ejecutable principal:** \`/usr/local/bin/vpn-manager/vpn-manager\`
- **Comando del sistema:** \`/usr/local/bin/vpn-manager-app\`
- **Archivos de la aplicación:** \`/usr/local/bin/vpn-manager/\`
- **Entrada del menú:** \`/usr/share/applications/vpn-manager.desktop\`
- **Documentación:** \`/usr/share/doc/vpn-manager/\`
- **Manual:** \`/usr/share/man/man1/vpn-manager.1.gz\`

## Configuración

La aplicación creará su configuración en:
- **Configuración del usuario:** \`~/.config/vpn-manager/\`
- **Conexiones guardadas:** \`~/.config/vpn-manager/connections.json\`

## Desinstalación

### Remover la aplicación
\`\`\`bash
sudo apt remove vpn-manager
\`\`\`

### Remover completamente (incluyendo configuración)
\`\`\`bash
sudo apt purge vpn-manager
\`\`\`

## Soporte

Para soporte técnico, contacta a: yesod3d@gmail.com
Repositorio: https://github.com/alumno109192/vpn

## Notas importantes

1. **Permisos sudo:** La aplicación requiere permisos de administrador para gestionar conexiones VPN
2. **Primera ejecución:** Al ejecutar por primera vez, se solicitará la contraseña sudo
3. **Dependencias VPN:** Asegúrate de que OpenVPN y/o StrongSwan estén correctamente configurados
4. **Licencia:** La aplicación incluye un período de prueba y sistema de licencias

## Solución de problemas

### Error: PyQt5 no encontrado
\`\`\`bash
sudo apt install python3-pyqt5
\`\`\`

### Error: OpenVPN no encontrado
\`\`\`bash
sudo apt install openvpn
\`\`\`

### Error: StrongSwan no encontrado
\`\`\`bash
sudo apt install strongswan
\`\`\`

### Verificar instalación
\`\`\`bash
dpkg -l | grep vpn-manager
which vpn-manager-app
\`\`\`
EOF

    info "Instrucciones de instalación creadas en release/INSTRUCCIONES_INSTALACION_DEB.md"
}

# Limpiar archivos temporales
cleanup() {
    log "Limpiando archivos temporales..."
    
    if [ -d "$DEB_DIR" ]; then
        rm -rf "$DEB_DIR"
        info "Directorio temporal $DEB_DIR eliminado"
    fi
}

# Función principal
main() {
    log "=== Generador de paquetes .deb para VPN Manager ==="
    echo
    
    # Verificar que estamos en el directorio correcto
    if [ ! -f "Main.py" ]; then
        error "Este script debe ejecutarse desde el directorio raíz del proyecto VPN Manager"
        exit 1
    fi
    
    # Ejecutar pasos de construcción
    get_app_info
    check_dependencies
    create_package_structure
    generate_control_file
    generate_install_scripts
    copy_application_files
    create_executable_script
    create_desktop_file
    create_man_page
    build_deb_package
    create_installation_instructions
    cleanup
    
    echo
    log "=== ¡Paquete .deb generado exitosamente! ==="
    info "Archivo generado: release/vpn-manager_${VERSION}_amd64.deb"
    info "Instrucciones: release/INSTRUCCIONES_INSTALACION_DEB.md"
    echo
    info "Para instalar ejecuta:"
    info "  sudo apt install ./release/vpn-manager_${VERSION}_amd64.deb"
    echo
}

# Ejecutar función principal
main "$@"
