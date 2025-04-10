# VPN App

Una aplicación multiplataforma para gestionar conexiones VPN.

## Requisitos de desarrollo

- Python 3.9 o superior
- PyQt5
- pexpect (solo para Unix)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tuusuario/vpn-app.git
cd vpn-app
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Unix
.\venv\Scripts\activate  # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

```bash
python Main.py
```

## Generar ejecutables

Los ejecutables se generan automáticamente mediante GitHub Actions cuando:
- Se crea un tag con formato `v*` (ejemplo: v1.0.0)
- Se activa manualmente el workflow desde GitHub

Los ejecutables generados estarán disponibles como artefactos en la acción de GitHub.