# Release Notes v1.3 - Mejoras significativas en la experiencia de usuario

## 🚀 Nuevas características

### Mensaje automático de licencia/período de prueba
- **Implementación automática** del mensaje de licencia/período de prueba al inicio de la aplicación
- Muestra automáticamente "Periodo de prueba (7 días)" cuando corresponde
- Información clara sobre el estado de la licencia para el usuario

### Sistema "Abrir" mejorado
- **Mejora significativa** del sistema 'Abrir' para traer la aplicación al primer plano
- Agregado `WindowStaysOnTopHint` temporal para mejor visibilidad de la ventana
- Implementación de múltiples métodos de activación de ventana (`raise_`, `activateWindow`, `setFocus`)
- **Compatibilidad mejorada** con entornos Wayland

### Funcionalidades adicionales
- Agregado `force_window_attention()` con métodos adicionales para llamar la atención del usuario
- Eliminación automática del flag 'always on top' después de 100ms
- Notificación en el system tray cuando se abre la aplicación

## 🔧 Mejoras técnicas

### Optimizaciones de código
- Eliminación de archivos obsoletos (Main2.py)
- Comentarios temporales en servicios de monitoreo VPN para evitar errores de import
- Mejor manejo de estados de ventana en diferentes entornos de escritorio

### Compatibilidad
- Soporte mejorado para entornos Wayland
- Mejor integración con system tray en diferentes distribuciones Linux
- Optimización para macOS y Linux

## 🐛 Correcciones

- Solucionados problemas de activación de ventana en Wayland
- Mejorada la respuesta del botón "Abrir" desde el system tray
- Eliminados imports problemáticos que causaban errores al inicio

## 📋 Archivos modificados

- `Main.py` - Mejoras principales en UI y funcionalidad
- `.gitignore` - Actualizado para mejor limpieza del repositorio
- Eliminado `Main2.py` (versión obsoleta)

## 🎯 Para usuarios

Esta versión mejora significativamente la experiencia de uso:

1. **Inicio más informativo**: Sabrás inmediatamente el estado de tu licencia/período de prueba
2. **Mejor accesibilidad**: El botón "Abrir" funciona de manera más efectiva
3. **Compatibilidad mejorada**: Funciona mejor en diferentes entornos de escritorio Linux

## 📥 Instalación

1. Descarga el código fuente desde el tag v1.3
2. Asegúrate de tener Python 3.x y PyQt5 instalados
3. Instala las dependencias: `pip install -r requirements.txt`
4. Ejecuta: `python Main.py`

## ⚠️ Requisitos del sistema

- Python 3.x
- PyQt5
- OpenVPN (para conexiones OpenVPN)
- StrongSwan (para conexiones IPSec)

---

**Fecha de lanzamiento**: 1 de agosto de 2025  
**Versión anterior**: v1.2  
**Repositorio**: https://github.com/alumno109192/vpn
