# 🚀 VPN Manager

Una aplicación multiplataforma para gestionar conexiones VPN con interfaz gráfica moderna y sistema de licencias.

## 📱 Características

### 🔧 Gestión de Conexiones VPN
- Soporte para OpenVPN y StrongSwan/IPSec
- Gestión de múltiples conexiones
- Configuración mediante interfaz gráfica intuitiva
- Monitoreo en tiempo real del estado de conexión

### 🔐 Sistema de Licencias
- Período de prueba gratuito
- Activación mediante código de licencia
- Validación offline con encriptación segura

### 🔄 Actualizaciones Automáticas
- Verificación automática de nuevas versiones
- Descarga e instalación silenciosa
- Respaldo de configuraciones durante actualizaciones

### 🖥️ Multiplataforma
- **macOS** (10.14+)
- **Linux** (Ubuntu, Debian, CentOS)
- **Windows** (10+)

## 🚀 Instalación

### Requisitos del Sistema
- Python 3.8 o superior
- PyQt5
- Permisos de administrador (para configuración VPN)

### Instalación desde el código fuente

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/vpn-manager.git
cd vpn-manager

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python Main.py
```

### Construir ejecutables

Para generar ejecutables independientes:

```bash
# macOS
chmod +x build_macos.sh
./build_macos.sh

# Linux
chmod +x build_linux.sh
./build_linux.sh

# Windows (en PowerShell)
.\build_windows.bat
```

## 📖 Uso

1. **Configurar VPN:** Añade tus conexiones VPN mediante la interfaz gráfica
2. **Conectar:** Selecciona una conexión y haz clic en "Conectar"
3. **Monitorear:** Observa el estado de la conexión en tiempo real
4. **Desconectar:** Termina la conexión cuando sea necesario

### Tipos de VPN soportados

- **OpenVPN:** Archivos `.ovpn` con configuración completa
- **IPSec/StrongSwan:** Configuración PSK y certificados

## 🔧 Configuración

La aplicación almacena sus configuraciones en:
- **macOS:** `~/Library/Application Support/VPNManager/`
- **Linux:** `~/.config/vpn-manager/`
- **Windows:** `%APPDATA%\VPNManager\`

## 🛠️ Desarrollo

### Estructura del proyecto

```
vpn-manager/
├── Main.py              # Aplicación principal
├── models.py            # Modelos de datos
├── version.py           # Información de versión
├── requirements.txt     # Dependencias Python
├── dialogs/            # Diálogos de la interfaz
├── threads/            # Hilos para operaciones VPN
├── services/           # Servicios del sistema
├── auto_updater.py     # Sistema de actualizaciones
├── license.py          # Gestión de licencias
└── license_storage.py  # Almacenamiento de licencias
```

### Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa los [Issues existentes](https://github.com/tu-usuario/vpn-manager/issues)
2. Crea un nuevo Issue si es necesario
3. Incluye información del sistema y logs relevantes

## 🔒 Seguridad

Para reportar vulnerabilidades de seguridad, por favor contacta directamente al mantenedor del proyecto en lugar de crear un Issue público.
