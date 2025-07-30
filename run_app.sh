#!/bin/bash

# Script para ejecutar VPN Manager en modo desarrollo
# Para usar: ./run_app.sh

cd "$(dirname "$0")"

# Verificar que existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "❌ Error: No se encontró el entorno virtual"
    echo "Por favor, ejecuta primero: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Verificar que existe Main.py
if [ ! -f "Main.py" ]; then
    echo "❌ Error: No se encontró Main.py"
    exit 1
fi

echo "🚀 Iniciando VPN Manager..."
echo "📁 Directorio: $(pwd)"

# Activar el entorno virtual y ejecutar la aplicación
source .venv/bin/activate
python Main.py

echo "✅ VPN Manager cerrado"
