#!/bin/bash

# Script para preparar y subir el proyecto VPN Manager a Git
# Autor: Generado automáticamente
# Fecha: $(date)

echo "🚀 Preparando VPN Manager para Git..."

# Verificar que estamos en el directorio correcto
if [ ! -f "Main.py" ]; then
    echo "❌ Error: No se encontró Main.py. Ejecuta este script desde el directorio del proyecto."
    exit 1
fi

echo "📁 Directorio del proyecto verificado"

# Limpiar archivos temporales si existen
echo "🧹 Limpiando archivos temporales..."
rm -f vpn_setup.log openvpn_runtime.log test_*.py *_test.py
rm -rf __pycache__ .pytest_cache

# Verificar que .gitignore existe
if [ ! -f ".gitignore" ]; then
    echo "❌ Error: No se encontró .gitignore"
    exit 1
fi

echo "✅ .gitignore verificado"

# Mostrar archivos que se incluirán
echo "📋 Archivos que se incluirán en Git:"
echo "----------------------------------------"
find . -type f \( \
    ! -path "./.venv/*" \
    ! -path "./__pycache__/*" \
    ! -path "./.git/*" \
    ! -name "*.pyc" \
    ! -name "*.log" \
    ! -name "*.ovpn" \
    ! -name "connections.json" \
    ! -name "*_backup.py" \
    ! -name "test_*.py" \
    ! -name ".DS_Store" \
    ! -name "up-vpn.sh" \
    ! -name "license.json" \
    ! -name "*.enc" \
    ! -name "*.key" \
\) | sort | sed 's|^\./||'

echo "----------------------------------------"

# Preguntar al usuario si desea continuar
read -p "¿Deseas continuar con la inicialización de Git? (s/N): " respuesta

if [[ ! "$respuesta" =~ ^[Ss]$ ]]; then
    echo "❌ Operación cancelada"
    exit 0
fi

# Inicializar repositorio Git si no existe
if [ ! -d ".git" ]; then
    echo "🔧 Inicializando repositorio Git..."
    git init
    echo "✅ Repositorio Git inicializado"
else
    echo "ℹ️  Repositorio Git ya existe"
fi

# Añadir archivos
echo "📤 Añadiendo archivos al staging area..."
git add .

# Mostrar estado
echo "📊 Estado del repositorio:"
git status --short

# Crear commit inicial
echo "💾 Creando commit..."
commit_message="Versión inicial: VPN Manager con sistema de licencias

- Aplicación VPN Manager fusionada con sistema de licencias
- Soporte para OpenVPN e IPSec
- Sistema de licencias con período de prueba
- Interfaz modularizada (dialogs, threads)
- Iconos de candado en zona de notificaciones
- Documentación completa incluida
- Scripts de ejecución y configuración"

git commit -m "$commit_message"

echo "✅ Commit creado exitosamente"

# Mostrar resumen
echo ""
echo "🎉 ¡Proyecto preparado para Git!"
echo "📚 Archivos de documentación incluidos:"
echo "   - README.md"
echo "   - ARCHIVOS_PARA_GIT.md"
echo "   - FUSION_SUMMARY.md"
echo "   - ESTADO_FINAL.md"
echo "   - INSTRUCCIONES_EJECUCION.md"
echo "   - CAMBIOS_ICONOS_CANDADO.md"
echo ""
echo "🔗 Para subir a GitHub:"
echo "   1. Crear repositorio en GitHub"
echo "   2. git remote add origin <URL_DEL_REPOSITORIO>"
echo "   3. git branch -M main"
echo "   4. git push -u origin main"
echo ""
echo "✨ ¡Listo para compartir!"
