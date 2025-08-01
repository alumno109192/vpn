#!/usr/bin/env python3
"""
Simulación del sistema de auto-actualización para VPN Manager
"""
import platform
from auto_updater import UpdateDownloadThread

# Simular datos de release como los que devuelve la API de GitHub
release_data = {
    'tag_name': 'v1.0.1',
    'assets': [
        {'name': 'vpn-manager-linux-v1.0.1.tar.gz', 'browser_download_url': 'http://test.com/linux.tar.gz'},
        {'name': 'vpn-manager-linux-v1.0.1.deb', 'browser_download_url': 'http://test.com/linux.deb'},
        {'name': 'vpn-manager-windows-v1.0.1.zip', 'browser_download_url': 'http://test.com/windows.zip'},
        {'name': 'vpn-manager-macos-v1.0.1.zip', 'browser_download_url': 'http://test.com/macos.zip'},
        {'name': 'vpn-manager-ubuntu-v1.0.1.AppImage', 'browser_download_url': 'http://test.com/ubuntu.AppImage'},
        {'name': 'vpn-manager-windows-v1.0.1.msi', 'browser_download_url': 'http://test.com/windows.msi'},
        {'name': 'vpn-manager-macos-v1.0.1.dmg', 'browser_download_url': 'http://test.com/macos.dmg'},
        {'name': 'vpn-manager-linux-v1.0.1.rpm', 'browser_download_url': 'http://test.com/linux.rpm'},
    ]
}

print("=== Simulación del sistema de auto-actualización ===")
print(f"Sistema detectado: {platform.system()} {platform.machine()}")

thread = UpdateDownloadThread(release_data)
asset_url = thread._get_asset_url()

if asset_url:
    print(f"Asset seleccionado para descarga: {asset_url}")
else:
    print("No se encontró un asset compatible para este sistema.")
print("=== Fin de la simulación ===")
