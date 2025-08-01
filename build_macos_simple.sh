#!/bin/bash

# Script simplificado para generar ejecutable en macOS
echo "🍎 Generando ejecutable simplificado para macOS..."
echo "================================================="

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    echo "🔧 Activando entorno virtual..."
    source .venv/bin/activate
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build/ dist/ *.spec

# Crear ejecutable con parámetros básicos pero efectivos
echo "🔨 Ejecutando PyInstaller con configuración simplificada..."
pyinstaller \
    --name="VPN Manager" \
    --windowed \
    --onefile \
    --noconfirm \
    --clean \
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
if [ -f "dist/VPN Manager" ]; then
    echo "✅ Ejecutable macOS creado exitosamente!"
    
    # Obtener información del ejecutable
    EXE_SIZE=$(du -sh "dist/VPN Manager" | cut -f1)
    echo "📊 Tamaño del ejecutable: $EXE_SIZE"
    
    # Hacer ejecutable
    chmod +x "dist/VPN Manager"
    
    # Crear paquete de distribución
    echo "📦 Creando paquete de distribución..."
    mkdir -p release/VPN-Manager-macOS-Simple
    cp "dist/VPN Manager" "release/VPN-Manager-macOS-Simple/"
    
    # Crear script de ejecución
    cat > "release/VPN-Manager-macOS-Simple/run.command" << 'RUN_EOF'
#!/bin/bash
echo "🚀 Ejecutando VPN Manager..."
cd "$(dirname "$0")"
./VPN\ Manager
RUN_EOF
    chmod +x "release/VPN-Manager-macOS-Simple/run.command"
    
    # Crear README
    cat > "release/VPN-Manager-macOS-Simple/README.md" << 'README_EOF'
# VPN Manager para macOS (Versión Simplificada)

## Ejecución

### Opción 1: Doble clic
1. Haz doble clic en `run.command`
2. Si aparece un aviso de seguridad, sigue los pasos de abajo

### Opción 2: Terminal
```bash
./VPN\ Manager
```

## Primera ejecución

Si aparece "No se puede abrir porque proviene de un desarrollador no identificado":

1. **Permitir ejecución**:
   - Ve a System Preferences → Security & Privacy → General
   - Haz clic en "Allow Anyway" junto a VPN Manager
   - Intenta ejecutar nuevamente

2. **Método alternativo**:
   ```bash
   # En Terminal, navega al directorio y ejecuta:
   sudo spctl --master-disable  # Desactivar Gatekeeper temporalmente
   ./VPN\ Manager
   sudo spctl --master-enable   # Reactivar Gatekeeper
   ```

## Dependencias

El ejecutable incluye todas las dependencias Python necesarias.
OpenVPN y StrongSwan se instalarán automáticamente si no están presentes.

## Uso

1. **Primera vez**: La aplicación verificará dependencias del sistema
2. **Configurar**: Botón "Configurar" → Añadir archivos .ovpn
3. **Conectar**: Seleccionar conexión → "Conectar"
4. **Sistema tray**: Icono en la barra de menú superior

## Soporte

- Email: yesod3d@gmail.com
- GitHub: https://github.com/alumno109192/vpn

## Nota

Esta es una versión simplificada que evita problemas de compilación complejos.
Funciona igual que la versión completa pero es un ejecutable único.
README_EOF
    
    # Crear ZIP final
    echo "🗜️  Creando archivo ZIP..."
    cd release
    zip -r "VPN-Manager-macOS-Simple.zip" "VPN-Manager-macOS-Simple/"
    cd ..
    
    ZIP_SIZE=$(du -sh "release/VPN-Manager-macOS-Simple.zip" | cut -f1)
    echo "✅ ZIP creado: release/VPN-Manager-macOS-Simple.zip ($ZIP_SIZE)"
    
    echo ""
    echo "🎉 ¡Proceso completado exitosamente!"
    echo ""
    echo "📋 Archivos generados:"
    echo "   - dist/VPN Manager (ejecutable macOS)"
    echo "   - release/VPN-Manager-macOS-Simple/ (paquete de distribución)"
    echo "   - release/VPN-Manager-macOS-Simple.zip (archivo final para distribución)"
    echo ""
    echo "🧪 Para probar:"
    echo "   ./dist/VPN\\ Manager"
    echo ""
    echo "📤 Para distribuir:"
    echo "   Comparte el archivo: release/VPN-Manager-macOS-Simple.zip"
    
else
    echo "❌ Error: No se pudo crear el ejecutable macOS"
    echo "Revisa los logs anteriores para más detalles"
    exit 1
fi
