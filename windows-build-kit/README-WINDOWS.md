# VPN Manager - Build para Windows

## Instrucciones para generar el ejecutable en Windows

### Requisitos:
- Windows 10/11
- Python 3.8 o superior
- Git (opcional)

### Pasos:

1. **Copiar archivos**: Copia toda la carpeta `windows-build-kit` a una máquina Windows

2. **Abrir terminal**: Abre Command Prompt o PowerShell como administrador

3. **Navegar a la carpeta**:
   ```cmd
   cd path\to\windows-build-kit
   ```

4. **Ejecutar el build**:
   ```cmd
   build_windows.bat
   ```

5. **Resultado**: El ejecutable se creará en `dist\VPN-Manager-Windows\`

### Archivos generados:
- `VPN-Manager-Windows.exe` - Ejecutable principal
- `run.bat` - Script para ejecutar fácilmente
- Carpetas con dependencias necesarias

### Distribución:
Para distribuir, comprime toda la carpeta `dist\VPN-Manager-Windows\` en un ZIP.

### Solución de problemas:

**Error de Python no encontrado:**
- Instala Python desde https://python.org
- Asegúrate de marcar "Add Python to PATH" durante la instalación

**Error de PyQt5:**
- Ejecuta: `pip install PyQt5==5.15.7` si la versión 5.15.9 falla

**Error de permisos:**
- Ejecuta el Command Prompt como administrador

**Antivirus bloquea el ejecutable:**
- Añade excepción para la carpeta del proyecto
- Es normal que algunos antivirus marquen ejecutables de PyInstaller como sospechosos
