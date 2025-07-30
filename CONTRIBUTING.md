# 🤝 Contribuir a VPN Manager

¡Gracias por tu interés en contribuir a VPN Manager! Este documento proporciona pautas para contribuir al proyecto.

## 🚀 Cómo contribuir

### 1. Fork y clonar el repositorio

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/tu-usuario/vpn-manager.git
cd vpn-manager
```

### 2. Configurar el entorno de desarrollo

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias adicionales para desarrollo (opcional)
pip install black flake8 pytest
```

### 3. Crear una rama para tu feature

```bash
git checkout -b feature/nueva-funcionalidad
# o
git checkout -b bugfix/corregir-problema
```

### 4. Realizar cambios

- Mantén el código limpio y bien documentado
- Sigue las convenciones de estilo de Python (PEP 8)
- Añade comentarios cuando sea necesario
- Actualiza la documentación si es relevante

### 5. Probar los cambios

```bash
# Ejecutar la aplicación para probar
python Main.py

# Ejecutar tests (si existen)
python -m pytest

# Verificar estilo de código (si tienes flake8 instalado)
flake8 *.py
```

### 6. Commit y push

```bash
git add .
git commit -m "Descripción clara del cambio"
git push origin feature/nueva-funcionalidad
```

### 7. Crear Pull Request

1. Ve a tu fork en GitHub
2. Haz clic en "New Pull Request"
3. Describe claramente los cambios realizados
4. Incluye capturas de pantalla si es relevante

## 📝 Pautas de contribución

### Código

- **Estilo:** Sigue PEP 8 para el estilo de código Python
- **Documentación:** Documenta funciones y clases importantes
- **Compatibilidad:** Asegúrate de que el código funcione en Python 3.8+
- **Dependencias:** Evita añadir dependencias innecesarias

### Commits

- Usa mensajes de commit descriptivos
- Usa el presente: "Añade función" en lugar de "Añadió función"
- Limita la primera línea a 50 caracteres
- Añade detalles en líneas adicionales si es necesario

### Pull Requests

- **Título claro:** Describe brevemente qué hace tu PR
- **Descripción detallada:** Explica los cambios y por qué son necesarios
- **Referencias:** Menciona issues relacionados usando `#numero`
- **Tests:** Incluye capturas de pantalla o videos si es relevante

## 🐛 Reportar bugs

### Antes de reportar

1. Busca en los issues existentes
2. Asegúrate de usar la versión más reciente
3. Reproduce el problema en un entorno limpio

### Al reportar

Incluye la siguiente información:

- **Versión:** Versión de VPN Manager y Python
- **Sistema operativo:** macOS, Linux, Windows (incluye versión)
- **Descripción:** Descripción clara del problema
- **Pasos para reproducir:** Lista detallada de pasos
- **Comportamiento esperado:** Qué esperabas que pasara
- **Comportamiento actual:** Qué está pasando realmente
- **Logs:** Incluye mensajes de error relevantes

## 💡 Sugerir mejoras

Para sugerir nuevas funcionalidades:

1. Abre un issue con la etiqueta "enhancement"
2. Describe claramente la funcionalidad propuesta
3. Explica por qué sería útil
4. Proporciona ejemplos de uso si es posible

## 🔧 Áreas donde necesitamos ayuda

- **Documentación:** Mejorar README, comentarios de código
- **Tests:** Añadir tests automatizados
- **UI/UX:** Mejorar la interfaz de usuario
- **Compatibilidad:** Probar en diferentes sistemas operativos
- **Traducción:** Añadir soporte para múltiples idiomas
- **Performance:** Optimizar la aplicación
- **Seguridad:** Revisar código por vulnerabilidades

## 📚 Recursos útiles

- [Documentación de PyQt5](https://doc.qt.io/qtforpython/)
- [Guía de PyInstaller](https://pyinstaller.readthedocs.io/)
- [PEP 8 - Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## ❓ ¿Necesitas ayuda?

Si tienes preguntas sobre el código o cómo contribuir:

1. Revisa la documentación existente
2. Busca en issues cerrados
3. Abre un nuevo issue con la etiqueta "question"
4. Sé específico sobre lo que necesitas ayuda

¡Gracias por contribuir a VPN Manager! 🎉
