#!/bin/bash
# Script para subir releases a GitHub (requiere gh CLI)

echo "🚀 Subiendo releases a GitHub..."

# Verificar gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI no encontrado. Instala con: brew install gh"
    exit 1
fi

# Variables
REPO="tu-usuario/vpn-manager"  # Cambia esto por tu repo
TAG="v$(date +%Y.%m.%d)"
TITLE="VPN Manager $TAG"

echo "📦 Creando release $TAG..."

# Crear release
gh release create "$TAG" \
    --title "$TITLE" \
    --notes "VPN Manager - Ejecutables para todas las plataformas" \
    VPN-Manager-*.zip \
    VPN-Manager-*.tar.gz

echo "✅ Release creado: https://github.com/$REPO/releases/tag/$TAG"
