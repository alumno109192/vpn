# Instalación del paquete .deb de VPN Manager v1.3.4

## 📦 Paquete generado:
- **Archivo**: `vpn-manager_1.3.4_amd64.deb`
- **Tamaño**: 46K
- **Arquitectura**: amd64 (x86_64)
- **Versión**: 1.3.4

## 🚀 Instalación

### Método 1: Instalación directa con dpkg
```bash
sudo dpkg -i vpn-manager_1.3.4_amd64.deb
sudo apt-get install -f  # Resolver dependencias si es necesario
```

### Método 2: Instalación con apt (recomendado)
```bash
sudo apt install ./vpn-manager_1.3.4_amd64.deb
```

## 📋 Dependencias requeridas:
- `python3` (>= 3.8)
- `python3-pyqt5`
- `openvpn`
- `python3-requests`
- `python3-cryptography`

Las dependencias se instalarán automáticamente si usas `apt install`.

## 🔧 Ejecución después de la instalación:

### Desde terminal:
```bash
vpn-manager-app
```

### Desde el menú de aplicaciones:
Busca "VPN Manager" en tu menú de aplicaciones o lanzador.

## 📂 Ubicación de archivos instalados:
- **Ejecutable principal**: `/usr/local/bin/vpn-manager/vpn-manager`
- **Archivos de aplicación**: `/usr/local/bin/vpn-manager/`
- **Archivo .desktop**: `/usr/share/applications/vpn-manager.desktop`
- **Documentación**: `/usr/share/doc/vpn-manager/`
- **Enlace simbólico**: `/usr/local/bin/vpn-manager-app`

## ✨ Características incluidas:
- ✅ Sistema de actualización automática
- ✅ Soporte para conexiones OpenVPN e IPSec
- ✅ Gestión de licencias y período de prueba
- ✅ Integración con el sistema de iconos
- ✅ Scripts de instalación y desinstalación automáticos
- ✅ Configuración del menú de aplicaciones

## 🗑️ Desinstalación:
```bash
sudo apt remove vpn-manager
# o
sudo dpkg -r vpn-manager
```

Para remover completamente incluyendo archivos de configuración:
```bash
sudo apt purge vpn-manager
```

## 🛠️ Verificación de la instalación:
```bash
# Verificar que el paquete está instalado
dpkg -l | grep vpn-manager

# Verificar el ejecutable
which vpn-manager-app

# Ejecutar la aplicación
vpn-manager-app --version
```

## 📝 Notas importantes:
- El paquete .deb está optimizado para sistemas Debian/Ubuntu
- Incluye scripts de post-instalación para configurar enlaces y menús
- Mantiene compatibilidad con actualizaciones automáticas
- Los archivos de configuración del usuario se preservan durante actualizaciones

---

**¡La instalación está completa! Ahora puedes usar VPN Manager desde tu menú de aplicaciones o terminal.**
