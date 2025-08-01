# VPN Manager para macOS

Gestor de conexiones VPN multiplataforma con interfaz gráfica moderna.

## 🚀 Instalación Rápida

### Método 1: Instalación Automática (Recomendado)
1. Doble clic en `install.command`
2. Seguir las instrucciones en pantalla
3. La aplicación se instalará en `/Applications/`

### Método 2: Instalación Manual
1. Arrastra `VPN Manager.app` a la carpeta `/Applications/`
2. Ejecuta desde Launchpad o Finder

## 🔐 Configuración de Seguridad

macOS puede mostrar un aviso de seguridad la primera vez que ejecutes la aplicación:

### Si aparece "No se puede abrir porque proviene de un desarrollador no identificado"

**Opción A: System Preferences**
1. Ve a `System Preferences` → `Security & Privacy` → `General`
2. Busca el mensaje sobre VPN Manager
3. Haz clic en `Open Anyway`
4. Confirma con `Open`

**Opción B: Terminal (Avanzado)**
```bash
sudo xattr -rd com.apple.quarantine "/Applications/VPN Manager.app"
```

**Opción C: Desde Finder**
1. Haz clic derecho en `VPN Manager.app`
2. Selecciona `Open`
3. En el diálogo, haz clic en `Open`

## 📱 Uso de la Aplicación

### Primera Ejecución
1. **Verificación de dependencias**: La app verificará e instalará automáticamente OpenVPN y StrongSwan
2. **Configuración inicial**: Se creará la estructura de directorios necesaria

### Gestión de Conexiones
1. **Añadir conexión**: Botón `Configurar` → `Añadir` → Seleccionar archivo `.ovpn`
2. **Conectar**: Seleccionar conexión → Botón `Conectar`
3. **Desconectar**: Botón `Desconectar` o desde el icono del sistema

### Icono del Sistema
- **Ubicación**: Barra de menú superior (junto al reloj)
- **Estados**:
  - 🔴 Desconectado
  - 🟡 Conectando
  - 🟢 Conectado
- **Menú contextual**: Clic derecho para opciones rápidas

## 🛠️ Dependencias del Sistema

La aplicación instalará automáticamente:

### Homebrew (si no está instalado)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### OpenVPN
```bash
brew install openvpn
```

### StrongSwan (para conexiones IKEv2)
```bash
brew install strongswan
```

## 📁 Estructura de Archivos

```
~/VPN-Manager/
├── connections/          # Archivos .ovpn
├── logs/                # Logs de conexión
├── license/             # Información de licencia
└── config/              # Configuración de la app
```

## 🔧 Solución de Problemas

### La aplicación no inicia
1. **Verificar permisos**: Seguir pasos de configuración de seguridad
2. **Terminal**: Abrir Terminal y ejecutar:
   ```bash
   "/Applications/VPN Manager.app/Contents/MacOS/VPN Manager"
   ```
3. **Logs**: Revisar Console.app para errores del sistema

### Error "No se pueden instalar dependencias"
1. **Instalar Homebrew manualmente**:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Instalar dependencias**:
   ```bash
   brew install openvpn strongswan
   ```
3. **Reiniciar VPN Manager**

### Problemas de conexión
1. **Verificar archivo .ovpn**: Asegurar que el archivo está completo y es válido
2. **Permisos de red**: Verificar que la app tiene permisos de red
3. **Firewall**: Revisar configuración del firewall de macOS
4. **Logs**: Revisar logs en `~/VPN-Manager/logs/`

### Error "Command not found: openvpn"
```bash
# Añadir Homebrew al PATH
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# O crear symlink
sudo ln -sf /opt/homebrew/bin/openvpn /usr/local/bin/openvpn
```

## ⚡ Características

- ✅ **Interfaz gráfica moderna** con PyQt5
- ✅ **Sistema de bandeja** siempre disponible
- ✅ **Gestión automática de dependencias**
- ✅ **Soporte para múltiples conexiones VPN**
- ✅ **Sistema de licencias** (30 días gratis)
- ✅ **Actualizaciones automáticas**
- ✅ **Logs detallados** para debugging
- ✅ **Compatibilidad total con macOS**

## 📄 Licencia

- **Período de prueba**: 30 días gratuitos
- **Licencia completa**: 5€/mes
- **Gestión de licencias**: Integrada en la aplicación

## 📞 Soporte

- **Email**: yesod3d@gmail.com
- **GitHub**: https://github.com/alumno109192/vpn
- **Documentación**: Incluida en la aplicación

## 📋 Requisitos del Sistema

- **macOS**: 10.14 (Mojave) o superior
- **Arquitectura**: Intel x64 / Apple Silicon (M1/M2/M3)
- **RAM**: 512 MB mínimo, 1 GB recomendado
- **Espacio**: 200 MB para la aplicación + dependencias
- **Permisos**: Administrador para instalar dependencias del sistema

---

**Versión**: 1.0.0  
**Fecha**: $(date +%Y-%m-%d)  
**Desarrollador**: Yesod Development
