#!/bin/bash
echo "🗑️  Desinstalador de VPN Manager"
echo "==============================="
echo ""
echo "⚠️  ATENCIÓN: Esto eliminará VPN Manager y todos sus datos"
echo ""
read -p "¿Estás seguro de que deseas continuar? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Desinstalación cancelada."
    exit 0
fi

echo ""
echo "🧹 Eliminando VPN Manager..."

# Cerrar la aplicación si está ejecutándose
killall "VPN Manager" 2>/dev/null || true

# Eliminar aplicación
if [ -d "/Applications/VPN Manager.app" ]; then
    echo "📱 Eliminando aplicación..."
    sudo rm -rf "/Applications/VPN Manager.app"
fi

# Eliminar datos de usuario (opcional)
echo ""
read -p "¿Deseas eliminar también los datos de usuario (conexiones, logs, etc.)? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📁 Eliminando datos de usuario..."
    rm -rf ~/VPN-Manager/ 2>/dev/null || true
    rm -rf ~/.vpn-manager/ 2>/dev/null || true
fi

echo ""
echo "✅ VPN Manager desinstalado completamente"
echo ""
echo "Nota: Las dependencias del sistema (OpenVPN, StrongSwan) no se han eliminado."
echo "Si deseas eliminarlas también:"
echo "  brew uninstall openvpn strongswan"
echo ""
read -p "Presiona Enter para continuar..."
