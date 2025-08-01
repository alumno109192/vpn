#!/bin/bash
echo "🚀 Instalando VPN Manager..."
sudo mkdir -p /opt/vpn-manager
sudo cp VPN-Manager /opt/vpn-manager/
sudo chmod +x /opt/vpn-manager/VPN-Manager
sudo cp vpn-manager.desktop /usr/share/applications/
echo "✅ VPN Manager instalado"
echo "Puedes ejecutarlo desde el menú de aplicaciones o ejecutando: /opt/vpn-manager/VPN-Manager"
