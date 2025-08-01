#!/bin/bash
# Instrucciones para crear Release v1.3.1 en GitHub

echo "🚀 GUÍA PARA CREAR RELEASE v1.3.1 EN GITHUB"
echo "============================================="
echo
echo "📍 PASO 1: Acceder a GitHub"
echo "   → Ir a: https://github.com/alumno109192/vpn/releases"
echo "   → Click en 'Create a new release'"
echo
echo "📍 PASO 2: Configurar Release"
echo "   → Tag version: v1.3.1 (seleccionar de la lista)"
echo "   → Release title: VPN Manager v1.3.1 - Multi-format packages"
echo
echo "📍 PASO 3: Descripción del Release"
echo "   → Copiar el siguiente texto en la descripción:"
echo
cat << 'EOF'
## 🚀 VPN Manager v1.3.1 - Multi-format packages with enhanced auto-updater

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
- Método `_get_asset_url()` mejorado con coincidencia de patrones
- Mejores mensajes de error y orientación al usuario
- Soporte para extracción e instalación de tar.gz

### 📋 Instalación:

#### Para sistemas Debian/Ubuntu:
```bash
sudo dpkg -i vpn-manager_1.3.1_amd64.deb
sudo apt-get install -f  # Solucionar dependencias si es necesario
```

#### Para otras distribuciones Linux:
```bash
tar -xzf VPN-Manager-Linux-x64-v1.3.1.tar.gz
cd VPN-Manager-Linux-x64-v1.3.1
python3 Main.py
```

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
EOF
echo
echo "📍 PASO 4: Subir archivos"
echo "   → Arrastar y soltar los siguientes archivos:"
echo "     • vpn-manager_1.3.1_amd64.deb (45K)"
echo "     • VPN-Manager-Linux-x64-v1.3.1.tar.gz (37K)"
echo
echo "📍 PASO 5: Opciones adicionales"
echo "   → ☑️ Marcar como 'Latest release'"
echo "   → ☐ NO marcar como 'Pre-release'"
echo
echo "📍 PASO 6: Publicar"
echo "   → Click en 'Publish release'"
echo
echo "============================================="
echo "📂 Archivos disponibles en: $(pwd)/release/"
echo "🌐 URL del repositorio: https://github.com/alumno109192/vpn"
echo "============================================="
