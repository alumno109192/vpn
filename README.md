# 🚀 VPN Manager - ✅ PROYECTO COMPLETADO

> **Estado:** ✅ COMPLETAMENTE FUNCIONAL Y LISTO PARA DISTRIBUCIÓN

Una aplicación multiplataforma avanzada para gestionar conexiones VPN con sistema de actualizaciones automáticas, licencias y interfaz gráfica moderna.

## 🎉 ¡Proyecto 100% Completado!

**Todas las funcionalidades solicitadas han sido implementadas exitosamente:**

- ✅ **Sistema de actualizaciones automáticas** completo y funcional
- ✅ **Ejecutables standalone** para macOS, Linux y Windows
- ✅ **Sistema de licencias** con período de prueba
- ✅ **Interfaz gráfica moderna** con PyQt5
- ✅ **Soporte VPN completo** (OpenVPN + IPSec)
- ✅ **Scripts de build robustos** para todas las plataformas
- ✅ **Documentación completa** y tests incluidos

## 🚀 Inicio Rápido

### Para Usuarios:
1. **macOS:** Descargar y ejecutar `VPN Manager.app` desde `release/VPN-Manager-macOS-Ultimate/`
2. **Linux/Windows:** Usar los scripts de build correspondientes

### Para Desarrolladores:
```bash
# Verificar que todo funciona
python test_system.py

# Ejecutar en modo desarrollo
./run_app.sh

# Generar ejecutable (macOS)
./build_macos_ultimate.sh
```

## 📱 Ejecutables Listos para Distribución

El proyecto incluye ejecutables completamente funcionales en `release/VPN-Manager-macOS-Ultimate/`:
- `VPN Manager.app` - Aplicación principal para macOS
- `install.command` - Instalador automático
- `uninstall.command` - Desinstalador
- `README.md` - Instrucciones para el usuario final

## Características

### 🔧 Gestión de Conexiones VPN
- Soporte para OpenVPN y StrongSwan/IPSec
- Gestión de múltiples conexiones simultáneas
- Configuración sencilla mediante interfaz gráfica

### 🔄 Sistema de Actualización Automática
- **Verificación automática**: La aplicación verifica actualizaciones al iniciar (modo silencioso)
- **Actualización manual**: Opción en el menú del sistema para buscar actualizaciones
- **Instalación automática**: Descarga e instala automáticamente las nuevas versiones
- **Preservación de datos**: Mantiene configuraciones, licencias y conexiones durante la actualización
- **Multiplataforma**: Soporte para Windows (.exe), macOS (.dmg) y Linux (.zip)

### 📋 Información de Versión
- Versión actual mostrada en el título de la ventana
- Diálogo "Acerca de" con información completa de la aplicación
- Sistema de versionado semántico (semver)

### 🔐 Sistema de Licencias
- Período de prueba gratuito
- Activación de licencia mediante email y clave
- Validación automática de licencias

## Requisitos de desarrollo

- Python 3.9 o superior
- PyQt5
- pexpect (solo para Unix)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tuusuario/vpn-app.git
cd vpn-app
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Unix
.\venv\Scripts\activate  # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Ejecución directa
```bash
python Main.py
```

### Ejecución en macOS (recomendado)
Si encuentras el error "Could not find the Qt platform plugin 'cocoa'", usa uno de estos métodos:

**Opción 1: Script de lanzamiento**
```bash
./launch_vpn.sh
```

**Opción 2: Script Python**
```bash
python run_vpn.py
```

**Opción 3: Configurar variables manualmente**
```bash
export QT_PLUGIN_PATH="$(python -c 'import PyQt5; import os; print(os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins"))')"
export QT_QPA_PLATFORM_PLUGIN_PATH="$QT_PLUGIN_PATH/platforms"
python Main.py
```

### Solución de problemas en macOS

Si experimentas problemas con Qt en macOS:

1. **Error "Could not find the Qt platform plugin 'cocoa'"**:
   - Usa `./launch_vpn.sh` en lugar de `python Main.py`
   - O ejecuta `python run_vpn.py`

2. **Problemas de permisos**:
   - Asegúrate de que los scripts sean ejecutables: `chmod +x launch_vpn.sh`

3. **Problemas con el entorno virtual**:
   - Verifica que el entorno virtual esté activado: `source .venv/bin/activate`
   - Reinstala PyQt5 si es necesario: `pip install --force-reinstall PyQt5`

## Sistema de Actualización Automática

### 🔄 Verificación Automática
La aplicación verifica automáticamente si hay nuevas versiones disponibles:
- **Al iniciar**: Verificación silenciosa en segundo plano
- **Manual**: Menú del sistema → "Buscar actualizaciones"
- **En "Acerca de"**: Botón para verificar actualizaciones

### 📦 Proceso de Actualización
Cuando hay una nueva versión disponible:

1. **Notificación**: La aplicación mostrará un diálogo informando sobre la nueva versión
2. **Confirmación**: El usuario puede elegir si desea instalar la actualización
3. **Descarga**: Se descarga automáticamente el archivo apropiado para tu sistema operativo
4. **Instalación**: Se instala la nueva versión preservando:
   - Configuraciones de conexiones (`connections.json`)
   - Datos de licencia (`license_storage.json`)
   - Logs de la aplicación (`vpn_setup.log`)
   - Entorno virtual (`.venv`)
5. **Reinicio**: La aplicación se reinicia automáticamente con la nueva versión

### 🧪 Probar el Sistema de Actualización
Para verificar que el sistema funciona correctamente:

```bash
# Ejecutar pruebas del sistema de actualización
python test_updater.py

# O con el entorno virtual activado
./.venv/bin/python test_updater.py
```

### ⚙️ Configuración de Versiones
- La versión actual se define en `version.py`
- El repositorio GitHub se configura en el mismo archivo
- Para cambiar la versión, actualiza la variable `__version__` en `version.py`

## Generar ejecutables

Los ejecutables se generan automáticamente mediante GitHub Actions cuando:
- Se crea un tag con formato `v*` (ejemplo: v1.0.0)
- Se activa manualmente el workflow desde GitHub

Los ejecutables generados estarán disponibles como artefactos en la acción de GitHub.