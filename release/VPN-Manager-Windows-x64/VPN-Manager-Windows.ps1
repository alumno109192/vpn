# VPN Manager para Windows (PowerShell)
# ====================================

Write-Host ""
Write-Host "    🚀 VPN Manager para Windows" -ForegroundColor Green
Write-Host "    ==========================" -ForegroundColor Green
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado." -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Por favor instala Python 3.8+ desde:" -ForegroundColor Yellow
    Write-Host "   https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE: Marca 'Add Python to PATH' durante la instalación" -ForegroundColor Yellow
    Read-Host "Presiona Enter para continuar"
    exit 1
}

# Verificar dependencias
Write-Host "🔍 Verificando dependencias..." -ForegroundColor Cyan

try {
    python -c "import PyQt5" 2>$null
} catch {
    Write-Host "📦 Instalando PyQt5..." -ForegroundColor Yellow
    pip install PyQt5==5.15.9
}

try {
    python -c "import requests" 2>$null
} catch {
    Write-Host "📦 Instalando dependencias adicionales..." -ForegroundColor Yellow
    pip install requests cryptography pexpect urllib3 certifi packaging
}

# Ejecutar aplicación
Write-Host ""
Write-Host "🚀 Iniciando VPN Manager..." -ForegroundColor Green
Write-Host ""

try {
    python Main.py
} catch {
    Write-Host ""
    Write-Host "❌ Error al ejecutar VPN Manager" -ForegroundColor Red
    Write-Host "📧 Contacta soporte: yesod3d@gmail.com" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
}
