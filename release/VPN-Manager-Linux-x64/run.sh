#!/bin/bash
# Script para ejecutar VPN Manager Linux

cd "$(dirname "$0")"

# Configurar variables de entorno
export QT_QPA_PLATFORM_PLUGIN_PATH="$(pwd)"
export QT_PLUGIN_PATH="$(pwd)"

# Ejecutar aplicación
./VPN-Manager-Linux "$@"
