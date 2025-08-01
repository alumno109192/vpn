# VPN Manager para Linux

## 🚀 Ejecución Rápida

Para ejecutar la aplicación directamente:
```bash
./run.sh
```

## 📥 Instalación en el Sistema

Para instalar VPN Manager en el sistema:
```bash
sudo ./install.sh
```

Después de la instalación, puedes ejecutar:
```bash
vpn-manager
```

O buscar "VPN Manager" en el menú de aplicaciones.

## 🗑️ Desinstalación

Para desinstalar completamente:
```bash
sudo ./uninstall.sh
```

## 📋 Requisitos

- Linux con entorno gráfico (GNOME, KDE, XFCE, etc.)
- OpenVPN (para conexiones OpenVPN)
- StrongSwan (para conexiones IPSec) - opcional

## 🔧 Instalación de Dependencias

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install openvpn strongswan
```

### CentOS/RHEL/Fedora:
```bash
sudo yum install openvpn strongswan
# o para Fedora:
sudo dnf install openvpn strongswan
```

## 🔐 Permisos

La aplicación requiere permisos de administrador para:
- Configurar conexiones VPN
- Modificar rutas de red
- Acceder a interfaces de red

## 🛠️ Solución de Problemas

### Error de Qt Platform Plugin:
```bash
export QT_QPA_PLATFORM=xcb
./run.sh
```

### Error de permisos:
```bash
chmod +x VPN-Manager-Linux
chmod +x run.sh
```

## 📞 Soporte

Para soporte técnico, contacta: yesod3d@gmail.com

---
**VPN Manager v1.0.0** - Gestiona tus conexiones VPN de forma sencilla
