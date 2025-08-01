# 🚀 Script Generador de Releases - VPN Manager

## 📋 Descripción
El script `generate_release.sh` automatiza completamente el proceso de creación de releases para VPN Manager, incluyendo:

- ✅ Actualización automática del archivo `version.py`
- ✅ Creación del paquete `.deb` para Debian/Ubuntu
- ✅ Creación del paquete `.tar.gz` para distribuciones Linux generales
- ✅ Creación y subida automática del tag de Git
- ✅ Generación de instrucciones detalladas para GitHub Release

## 🛠️ Uso

### Opciones disponibles:

#### 1. Incremento automático (recomendado)
```bash
# Incrementar versión patch (1.3.1 → 1.3.2)
./generate_release.sh --increment patch

# Incrementar versión minor (1.3.1 → 1.4.0)
./generate_release.sh --increment minor

# Incrementar versión major (1.3.1 → 2.0.0)
./generate_release.sh --increment major
```

#### 2. Versión manual
```bash
# Especificar versión exacta
./generate_release.sh --version 1.5.0
```

#### 3. Modo interactivo
```bash
# Ejecutar sin parámetros para menú interactivo
./generate_release.sh
```

## 📦 Lo que hace el script:

### 1. **Verificación de dependencias**
- Verifica que estén instalados: `dpkg-deb`, `tar`, `gzip`, `git`

### 2. **Actualización de versión**
- Modifica automáticamente `version.py` con la nueva versión

### 3. **Creación del paquete .deb**
- Estructura completa de paquete Debian
- Scripts de instalación/desinstalación automáticos
- Archivo `.desktop` para integración con el sistema
- Dependencias automáticas declaradas

### 4. **Creación del paquete .tar.gz**
- Paquete comprimido con todos los archivos necesarios
- Excluye archivos temporales y directorios de build

### 5. **Gestión de Git**
- Commit automático de cambios pendientes
- Creación de tag con mensaje detallado
- Subida del tag a GitHub

### 6. **Documentación automática**
- Genera `RELEASE_INSTRUCTIONS_vX.X.X.md` con pasos detallados
- Incluye texto listo para copiar en GitHub Release

## 📁 Archivos generados:

```
release/
├── vpn-manager_X.X.X_amd64.deb      # Paquete Debian/Ubuntu
└── VPN-Manager-Linux-x64-vX.X.X.tar.gz  # Paquete Linux general

RELEASE_INSTRUCTIONS_vX.X.X.md       # Instrucciones para GitHub
```

## 🔧 Características del paquete .deb:

### Scripts automáticos incluidos:
- **postinst**: Configuración tras instalación
  - Crea enlace simbólico en PATH
  - Actualiza base de datos de aplicaciones
- **prerm**: Limpieza antes de desinstalación
  - Detiene procesos VPN activos
  - Elimina enlaces simbólicos
- **postrm**: Limpieza final
  - Opción de purga de configuraciones

### Integración del sistema:
- Archivo `.desktop` para menú de aplicaciones
- Instalación en `/usr/local/bin/vpn-manager/`
- Comando `vpn-manager-app` disponible en PATH

## 🎯 Flujo de trabajo completo:

1. **Ejecutar el script**:
   ```bash
   ./generate_release.sh --increment patch
   ```

2. **Verificar archivos generados**:
   ```bash
   ls -la release/
   ```

3. **Seguir instrucciones**:
   ```bash
   cat RELEASE_INSTRUCTIONS_v*.md
   ```

4. **Crear release en GitHub**:
   - El script abre automáticamente la URL correcta
   - Subir archivos de `release/`
   - Copiar descripción del archivo de instrucciones

## ⚠️ Requisitos previos:

- Git configurado con permisos de push
- Repositorio limpio (o cambios que puedan ser commiteados automáticamente)
- Dependencias del sistema instaladas

## 🐛 Resolución de problemas:

### Error: "Faltan dependencias"
```bash
# En Ubuntu/Debian:
sudo apt-get install dpkg-dev tar gzip git

# En otras distribuciones, instala los paquetes equivalentes
```

### Error: "No se puede push el tag"
- Verifica que tengas permisos de push en el repositorio
- Verifica tu configuración de Git: `git remote -v`

### Error: "Formato de versión inválido"
- Usa formato semver: `X.Y.Z` (ejemplo: `1.4.0`)
- Solo números enteros separados por puntos

## 📈 Ejemplo de salida exitosa:

```
==========================================
    VPN Manager - Release Generator
==========================================

[INFO] Verificando dependencias...
[SUCCESS] Todas las dependencias están disponibles
[INFO] Versión actual: 1.3.1
[INFO] Nueva versión (auto-incrementada): 1.3.2
[SUCCESS] Generando release v1.3.2

[INFO] Actualizando version.py a 1.3.2...
[SUCCESS] version.py actualizado
[INFO] Limpiando directorios de construcción anteriores...
[SUCCESS] Directorios limpiados
[INFO] Creando estructura del paquete .deb...
[SUCCESS] Estructura del paquete .deb creada
[INFO] Construyendo paquete .deb...
[SUCCESS] Paquete .deb creado: vpn-manager_1.3.2_amd64.deb (44K)
[INFO] Creando paquete tar.gz...
[SUCCESS] Paquete tar.gz creado: VPN-Manager-Linux-x64-v1.3.2.tar.gz (37K)
[INFO] Creando tag de git: v1.3.2...
[SUCCESS] Tag v1.3.2 creado y subido a GitHub
[INFO] Generando instrucciones de release...
[SUCCESS] Instrucciones generadas: RELEASE_INSTRUCTIONS_v1.3.2.md

==========================================
🎉 Release v1.3.2 generada exitosamente!
==========================================

📦 Archivos creados:
-rw-r--r-- 1 user user 44K fecha vpn-manager_1.3.2_amd64.deb
-rw-rw-r-- 1 user user 37K fecha VPN-Manager-Linux-x64-v1.3.2.tar.gz

🚀 Próximos pasos:
1. Lee las instrucciones: RELEASE_INSTRUCTIONS_v1.3.2.md
2. Ve a: https://github.com/alumno109192/vpn/releases/new?tag=v1.3.2
3. Sube los archivos de la carpeta release/
4. Publica la release
```

## 🎉 ¡Disfruta de tus releases automatizadas! 

Este script te ahorra tiempo y reduce errores al automatizar todo el proceso de release de principio a fin.
