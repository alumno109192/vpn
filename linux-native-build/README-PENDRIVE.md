# 🐧 VPN Manager - Ejecutable Portable para Ubuntu

## 📦 Contenido del pendrive:
- `VPN-Manager-Linux-YYYY.MM.DD` - Ejecutable principal (ELF nativo)
- `VPN-Manager-Linux-YYYY.MM.DD.sha256` - Checksum de verificación
- `EJECUTAR-EN-UBUNTU.sh` - Script de ejecución automática
- `README-PENDRIVE.md` - Este archivo

## 🚀 Uso rápido:
```bash
# Método 1: Script automático
./EJECUTAR-EN-UBUNTU.sh

# Método 2: Ejecución directa
chmod +x VPN-Manager-Linux-*
./VPN-Manager-Linux-*
```

## 📋 Requisitos:
- Ubuntu 18.04+ / Debian 10+ / Linux x86_64
- Python3 (se instala automáticamente si no está)
- PyQt5 (se instala automáticamente si no está)

## ✅ Compatibilidad verificada:
- ✅ Ubuntu 22.04 LTS
- ✅ Ubuntu 20.04 LTS
- ✅ Ubuntu 18.04 LTS
- ✅ Debian 11
- ✅ Linux Mint 21
- ✅ Pop!_OS 22.04

## 🔧 Si hay problemas de dependencias:
```bash
sudo apt-get update
sudo apt-get install python3-pyqt5 libqt5widgets5 libqt5core5a libqt5gui5
```

## 🔐 Verificar integridad:
```bash
sha256sum -c VPN-Manager-Linux-*.sha256
```

## 💡 Notas importantes:
- Este ejecutable es completamente portable
- No requiere instalación previa
- Incluye todas las librerías necesarias
- Compilado nativamente en Ubuntu 22.04

¡Listo para usar en cualquier Ubuntu! 🎉
