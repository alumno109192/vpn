# Instrucciones para crear Release v1.3.2 en GitHub

## 📦 Archivos generados:
- `vpn-manager_1.3.2_amd64.deb` - Paquete Debian/Ubuntu
- `VPN-Manager-Linux-x64-v1.3.2.tar.gz` - Paquete Linux general

## 🚀 Pasos para crear la release:

### 1. Acceder a GitHub
- URL: https://github.com/alumno109192/vpn/releases/new?tag=v1.3.2

### 2. Configurar Release
- **Tag version:** v1.3.2 (preseleccionado)
- **Release title:** VPN Manager v1.3.2 - Enhanced auto-updater

### 3. Descripción del Release
Copiar el siguiente texto:

```markdown
## 🚀 VPN Manager v1.3.2 - Enhanced auto-updater

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
sudo dpkg -i vpn-manager_1.3.2_amd64.deb
sudo apt-get install -f  # Solucionar dependencias si es necesario
```

#### Para otras distribuciones Linux:
```bash
tar -xzf VPN-Manager-Linux-x64-v1.3.2.tar.gz
cd VPN-Manager-Linux-x64-v1.3.2
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
```

### 4. Subir archivos
Arrastra los siguientes archivos:
- `release/vpn-manager_1.3.2_amd64.deb`
- `release/VPN-Manager-Linux-x64-v1.3.2.tar.gz`

### 5. Publicar
- ☑️ Marcar como "Latest release"
- ☐ NO marcar como "Pre-release"
- Click en "Publish release"

## ✅ Verificación post-release:
1. Verificar que ambos archivos están disponibles en la release
2. Probar la descarga de ambos paquetes
3. Verificar que el auto-updater detecta la nueva versión

## 📊 Estadísticas de la release:
- Versión anterior: v1.3.1
- Nueva versión: v1.3.2
- Archivos incluidos: 2 (deb + tar.gz)
- Tag de git: Creado y subido
