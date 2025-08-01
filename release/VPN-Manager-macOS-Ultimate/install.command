#!/bin/bash
echo "🚀 Instalando VPN Manager en Applications..."
echo ""

# Verificar si la aplicación ya existe
if [ -d "/Applications/VPN Manager.app" ]; then
    echo "⚠️  VPN Manager ya existe en Applications"
    read -p "¿Deseas reemplazarlo? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Instalación cancelada."
        exit 0
    fi
    echo "🗑️  Eliminando versión anterior..."
    rm -rf "/Applications/VPN Manager.app"
fi

# Copiar la aplicación
echo "📁 Copiando VPN Manager.app a Applications..."
if [ -w "/Applications" ]; then
    cp -R "VPN Manager.app" /Applications/
else
    echo "⚠️  Se necesitan permisos de administrador..."
    sudo cp -R "VPN Manager.app" /Applications/
    sudo chown -R $(whoami):staff "/Applications/VPN Manager.app"
fi

# Quitar atributos de cuarentena
echo "🔓 Configurando permisos de seguridad..."
sudo xattr -rd com.apple.quarantine "/Applications/VPN Manager.app" 2>/dev/null || true

echo ""
echo "✅ ¡VPN Manager instalado exitosamente!"
echo ""
echo "Puedes ejecutarlo desde:"
echo "  • Launchpad → VPN Manager"
echo "  • Finder → Applications → VPN Manager"
echo "  • Spotlight (Cmd+Space) → 'VPN Manager'"
echo ""
echo "Si aparece un aviso de seguridad al ejecutar:"
echo "  System Preferences → Security & Privacy → General → 'Allow Anyway'"
echo ""
read -p "¿Deseas abrir VPN Manager ahora? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    open "/Applications/VPN Manager.app"
fi
