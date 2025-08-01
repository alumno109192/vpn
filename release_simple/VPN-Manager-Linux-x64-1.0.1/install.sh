#!/bin/bash
echo "🚀 Actualizando VPN Manager..."

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado."
    exit 1
fi

# Instalar/actualizar dependencias
echo "📦 Verificando dependencias..."
python3 -m pip install --user -r requirements.txt 2>/dev/null || echo "⚠️ Algunas dependencias pueden faltar"

# Hacer ejecutable
chmod +x Main.py

echo "✅ Actualización completada!"
echo "Versión instalada: v1.0.1"
