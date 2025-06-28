# Archivos para Git - VPN Manager

## Archivos Principales del Proyecto

### Archivo Principal
- `Main.py` - Aplicación principal fusionada con VPN y sistema de licencias

### Módulos y Componentes
- `models.py` - Modelos de datos (VPNType, ConnectionState, ConnectionObserver)
- `license.py` - Gestor de licencias principal
- `license_storage.py` - Almacenamiento y persistencia de licencias
- `license_encryptor.py` - Encriptación de datos de licencia
- `license_generator.py` - Generador de claves de licencia

### Directorios de Módulos
- `dialogs/` - Módulos de diálogos de la aplicación
  - `__init__.py`
  - `config_dialog.py` - Diálogo de configuración
  - `edit_dialog.py` - Diálogo de edición
  - `sudo_dialog.py` - Diálogo de contraseña sudo
  
- `threads/` - Módulos de hilos para operaciones asíncronas
  - `__init__.py`
  - `vpn_thread.py` - Hilo para conexiones VPN
  - `file_thread.py` - Hilo para operaciones de archivos

### Archivos de Configuración
- `requirements.txt` - Dependencias de Python
- `.gitignore` - Archivos excluidos de Git

### Scripts de Utilidad
- `run_vpn_manager.sh` - Script de lanzamiento de la aplicación

### Documentación
- `README.md` - Documentación principal del proyecto
- `FUSION_SUMMARY.md` - Resumen de la fusión de archivos Main
- `MODULARIZATION_SUMMARY.md` - Resumen de la modularización
- `ESTADO_FINAL.md` - Estado final del proyecto
- `INSTRUCCIONES_EJECUCION.md` - Instrucciones de ejecución
- `CAMBIOS_ICONOS_CANDADO.md` - Documentación de cambios de iconos
- `ARCHIVOS_PARA_GIT.md` - Este archivo

### Archivos de Prueba (para desarrollo)
- `test_modularization.py` - Pruebas de modularización

## Archivos Excluidos de Git (.gitignore)

### Archivos Sensibles/Personales
- `connections.json` - Conexiones VPN del usuario (contiene credenciales)
- `*.ovpn` - Archivos de configuración VPN (pueden contener datos sensibles)
- `license.json` - Datos de licencia del usuario
- `*.enc`, `*.key` - Archivos de encriptación

### Archivos Temporales/Sistema
- `vpn_setup.log` - Logs de la aplicación
- `openvpn_runtime.log` - Logs de OpenVPN
- `__pycache__/` - Cache de Python
- `.venv/` - Entorno virtual
- `.DS_Store` - Archivos del sistema macOS

### Archivos de Desarrollo
- `test_*.py` - Archivos de prueba temporales
- `*_backup.py` - Archivos de respaldo
- Shell scripts potencialmente sensibles

## Estructura Final para Git

```
proyecto/
├── Main.py                          ✅ Principal
├── models.py                        ✅ Módulos
├── license.py                       ✅
├── license_storage.py               ✅
├── license_encryptor.py             ✅
├── license_generator.py             ✅
├── dialogs/                         ✅ Diálogos
│   ├── __init__.py
│   ├── config_dialog.py
│   ├── edit_dialog.py
│   └── sudo_dialog.py
├── threads/                         ✅ Hilos
│   ├── __init__.py
│   ├── vpn_thread.py
│   └── file_thread.py
├── requirements.txt                 ✅ Configuración
├── .gitignore                       ✅
├── run_vpn_manager.sh               ✅ Scripts
├── README.md                        ✅ Documentación
├── FUSION_SUMMARY.md                ✅
├── MODULARIZATION_SUMMARY.md        ✅
├── ESTADO_FINAL.md                  ✅
├── INSTRUCCIONES_EJECUCION.md       ✅
├── CAMBIOS_ICONOS_CANDADO.md        ✅
├── ARCHIVOS_PARA_GIT.md             ✅
└── test_modularization.py           ✅ Tests
```

## Comandos Git Recomendados

### Inicial
```bash
git init
git add .
git commit -m "Versión inicial: VPN Manager con sistema de licencias y modularización completa"
```

### Para actualizaciones
```bash
git add .
git commit -m "Descripción del cambio"
git push origin main
```

## Notas Importantes

1. **Seguridad**: Los archivos de configuración personal del usuario (connections.json, *.ovpn) están excluidos para proteger credenciales.

2. **Licencias**: Los archivos relacionados con licencias de usuario específicas están excluidos del repositorio.

3. **Portabilidad**: El código incluido es portable y no contiene rutas absolutas o configuraciones específicas del desarrollador.

4. **Dependencias**: Todas las dependencias están listadas en requirements.txt para fácil instalación.

5. **Documentación**: Incluye documentación completa del proceso de desarrollo y uso.

El proyecto está listo para ser subido a Git con una estructura limpia y profesional.
