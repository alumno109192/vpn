# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere al [Versionado Semántico](https://semver.org/lang/es/).

## [No liberado]

### Planeado
- Mejoras en la interfaz de usuario
- Optimizaciones de rendimiento

## [1.3.7] - 2025-08-01

### Agregado
- Organización completa del proyecto en estructura de directorios lógica
- Documentación mejorada con CLEANUP_SUMMARY.md

### Cambiado
- Limpieza masiva de archivos obsoletos (más de 50 archivos eliminados)
- Estructura del proyecto reorganizada en carpetas: docs/, release/, dialogs/, threads/
- Eliminación de scripts de construcción redundantes y archivos temporales
- Reducción significativa del tamaño del proyecto (de ~150MB a ~230KB)

### Eliminado
- Scripts de construcción obsoletos (build_*.sh, build_*.py)
- Archivos de instalación temporal (install_*.sh, launch_vpn*.sh)
- Documentación obsoleta (RELEASE_*.md, BUGFIX_*.md)
- Directorios cache (__pycache__, .venv)
- Artefactos de construcción antiguos

### Técnico
- Proyecto listo para producción con estructura limpia
- Paquete .deb funcional verificado (vpn-manager_1.3.6_amd64.deb)
- Código esencial preservado y organizado

## [1.3.6] - 2025-06-29

### Agregado
- Sistema completo de actualización automática
- Verificación automática de nuevas versiones al iniciar la aplicación
- Descarga e instalación automática de actualizaciones
- Preservación de datos durante las actualizaciones (configuraciones, licencias, logs)
- Menú "Buscar actualizaciones" en el sistema tray
- Diálogo "Acerca de" con información de la aplicación y opción para buscar actualizaciones
- Sistema de versionado centralizado en `version.py`
- Script de pruebas para el sistema de actualización (`test_updater.py`)
- Soporte multiplataforma para actualizaciones (Windows .exe, macOS .dmg, Linux .zip)
- Hilos separados para verificación y descarga de actualizaciones (no bloquea la UI)
- Barras de progreso durante la descarga de actualizaciones
- Manejo robusto de errores durante el proceso de actualización

### Cambiado
- Título de la ventana ahora incluye el número de versión
- Mejorado el sistema de configuración de Qt para macOS
- Estructura modular mejorada con separación de responsabilidades

### Técnico
- Agregado módulo `auto_updater.py` con clases:
  - `UpdateCheckThread`: Verificación de actualizaciones en segundo plano
  - `UpdateDownloadThread`: Descarga e instalación de actualizaciones
  - `AutoUpdater`: Clase principal del sistema de actualización
- Agregado módulo `version.py` para gestión centralizada de versiones
- Mejorado manejo de dependencias y configuración de entorno

## [1.0.0] - 2025-06-28

### Agregado
- Gestión de conexiones VPN (OpenVPN y StrongSwan/IPSec)
- Sistema de licencias con período de prueba
- Interfaz gráfica con PyQt5
- Soporte multiplataforma (Windows, macOS, Linux)
- Sistema de logs para diagnóstico
- Integración con GitHub Actions para builds automáticos
- Menú del sistema tray para acceso rápido
- Configuración de inicio automático con el sistema

### Seguridad
- Cifrado de datos de licencia
- Validación de licencias mediante algoritmos criptográficos
- Manejo seguro de credenciales VPN
