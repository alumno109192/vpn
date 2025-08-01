#!/bin/bash

# Script para crear ejecutable moviendo temporalmente a ruta sin caracteres especiales
echo "🍎 Solucionando problema de caracteres especiales en ruta..."
echo "============================================================"

# Crear directorio temporal sin caracteres especiales
TEMP_DIR="/tmp/vpn-manager-build-$(date +%s)"
CURRENT_DIR="$(pwd)"

echo "📁 Creando directorio temporal: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo "📋 Copiando archivos del proyecto..."
# Copiar todos los archivos necesarios
cp -R . "$TEMP_DIR/" 2>/dev/null || true

# Cambiar al directorio temporal
cd "$TEMP_DIR"

echo "🔧 Activando entorno virtual..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️  No se encontró entorno virtual, usando Python del sistema"
fi

# Verificar dependencias
echo "📦 Verificando PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "Instalando PyInstaller..."
    pip install PyInstaller
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build/ dist/ *.spec

echo "🔨 Ejecutando PyInstaller desde ruta limpia..."
pyinstaller \
    --name="VPN Manager" \
    --windowed \
    --onedir \
    --noconfirm \
    --clean \
    --exclude-module tkinter \
    --hidden-import=PyQt5.sip \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtGui \
    --hidden-import=PyQt5.QtWidgets \
    --hidden-import=pexpect \
    --hidden-import=requests \
    --hidden-import=cryptography \
    --hidden-import=packaging \
    --hidden-import=urllib3 \
    --hidden-import=certifi \
    --add-data="dialogs:dialogs" \
    --add-data="threads:threads" \
    --add-data="version.py:." \
    --add-data="auto_updater.py:." \
    --add-data="license.py:." \
    --add-data="license_storage.py:." \
    --add-data="license_encryptor.py:." \
    --add-data="license_generator.py:." \
    --add-data="models.py:." \
    Main.py

# Verificar resultado
if [ -d "dist/VPN Manager" ]; then
    echo "✅ Ejecutable macOS creado exitosamente!"
    
    # Volver al directorio original
    cd "$CURRENT_DIR"
    
    # Crear directorio de distribución en ubicación original
    echo "📦 Creando paquete de distribución en ubicación original..."
    mkdir -p release/VPN-Manager-macOS-Fixed
    
    # Copiar el resultado
    cp -R "$TEMP_DIR/dist/VPN Manager" "release/VPN-Manager-macOS-Fixed/"
    
    # Obtener información del ejecutable
    APP_SIZE=$(du -sh "release/VPN-Manager-macOS-Fixed/VPN Manager" | cut -f1)
    echo "📊 Tamaño de la aplicación: $APP_SIZE"
    
    # Crear script de ejecución
    cat > "release/VPN-Manager-macOS-Fixed/run.command" << 'RUN_EOF'
#!/bin/bash
echo "🚀 Ejecutando VPN Manager..."
cd "$(dirname "$0")"
open "VPN Manager"
RUN_EOF
    chmod +x "release/VPN-Manager-macOS-Fixed/run.command"
    
    # Crear script de ejecución en terminal
    cat > "release/VPN-Manager-macOS-Fixed/run-terminal.command" << 'TERM_EOF'
#!/bin/bash
echo "🚀 Ejecutando VPN Manager en terminal..."
cd "$(dirname "$0")"
"./VPN Manager/VPN Manager"
TERM_EOF
    chmod +x "release/VPN-Manager-macOS-Fixed/run-terminal.command"
    
    # Crear README
    cat > "release/VPN-Manager-macOS-Fixed/README.md" << 'README_EOF'
# VPN Manager para macOS

## Instalación

### Opción 1: Arrastrar a Applications (recomendado)
1. Arrastra la carpeta "VPN Manager" a /Applications/
2. Ejecuta desde Launchpad o Finder

### Opción 2: Ejecutar en lugar actual
1. Doble clic en `run.command` (ejecuta la aplicación)
2. O doble clic en `run-terminal.command` (ejecuta en terminal)

## Primera ejecución

Si aparece "No se puede abrir porque proviene de un desarrollador no identificado":

### Método 1: System Preferences
1. Ve a System Preferences → Security & Privacy → General
2. Haz clic en "Allow Anyway" junto a VPN Manager
3. Intenta ejecutar nuevamente

### Método 2: Terminal
```bash
# Navega al directorio de VPN Manager y ejecuta:
sudo xattr -rd com.apple.quarantine "VPN Manager"
open "VPN Manager"
```

### Método 3: Gatekeeper (temporal)
```bash
sudo spctl --master-disable  # Desactivar Gatekeeper
# Ejecutar VPN Manager
sudo spctl --master-enable   # Reactivar Gatekeeper
```

## Estructura de archivos

- `VPN Manager/` - Directorio de la aplicación
- `run.command` - Script para ejecutar la aplicación
- `run-terminal.command` - Script para ejecutar en terminal
- `README.md` - Este archivo

## Uso

1. **Primera vez**: La aplicación verificará e instalará dependencias
2. **Configurar**: Botón "Configurar" → Añadir archivos .ovpn
3. **Conectar**: Seleccionar conexión → "Conectar"  
4. **Sistema tray**: Icono en la barra de menú superior

## Dependencias del sistema

- OpenVPN (se instala automáticamente con Homebrew si no existe)
- StrongSwan (se instala automáticamente con Homebrew si no existe)

## Solución de problemas

### Aplicación no inicia
- Ejecuta `run-terminal.command` para ver errores
- Verifica permisos de ejecución
- Permite en Security & Privacy

### Error de dependencias
- Instala Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Instala dependencias: `brew install openvpn strongswan`

## Soporte

- Email: yesod3d@gmail.com
- GitHub: https://github.com/alumno109192/vpn

## Licencia

Período de prueba: 30 días gratuitos
Licencia completa: 5€/mes
README_EOF
    
    # Crear script de instalación automática
    cat > "release/VPN-Manager-macOS-Fixed/install.command" << 'INSTALL_EOF'
#!/bin/bash
echo "🚀 Instalando VPN Manager en Applications..."

# Verificar permisos
if [ ! -w "/Applications" ]; then
    echo "⚠️  Se necesitan permisos de administrador"
    sudo cp -R "VPN Manager" /Applications/
else
    cp -R "VPN Manager" /Applications/
fi

echo "✅ VPN Manager instalado en /Applications/"
echo ""
echo "Puedes ejecutarlo desde:"
echo "  - Launchpad → VPN Manager"
echo "  - Finder → Applications → VPN Manager"
echo ""
echo "Si aparece un aviso de seguridad:"
echo "  System Preferences → Security & Privacy → General → Allow"
echo ""
read -p "Presiona Enter para continuar..."
INSTALL_EOF
    chmod +x "release/VPN-Manager-macOS-Fixed/install.command"
    
    # Crear ZIP final
    echo "🗜️  Creando archivo ZIP..."
    cd release
    zip -r "VPN-Manager-macOS-Fixed.zip" "VPN-Manager-macOS-Fixed/"
    cd ..
    
    ZIP_SIZE=$(du -sh "release/VPN-Manager-macOS-Fixed.zip" | cut -f1)
    echo "✅ ZIP creado: release/VPN-Manager-macOS-Fixed.zip ($ZIP_SIZE)"
    
    # Limpiar directorio temporal
    echo "🧹 Limpiando directorio temporal..."
    rm -rf "$TEMP_DIR"
    
    echo ""
    echo "🎉 ¡Proceso completado exitosamente!"
    echo ""
    echo "📋 Archivos generados:"
    echo "   - release/VPN-Manager-macOS-Fixed/VPN Manager/ (aplicación macOS)"
    echo "   - release/VPN-Manager-macOS-Fixed.zip (archivo final para distribución)"
    echo ""
    echo "🧪 Para probar:"
    echo "   cd release/VPN-Manager-macOS-Fixed && ./run.command"
    echo ""
    echo "📤 Para distribuir:"
    echo "   Comparte el archivo: release/VPN-Manager-macOS-Fixed.zip"
    
else
    echo "❌ Error: No se pudo crear el ejecutable macOS"
    cd "$CURRENT_DIR"
    rm -rf "$TEMP_DIR"
    exit 1
fi
