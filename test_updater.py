#!/usr/bin/env python3
"""
Script de prueba para el sistema de actualización automática de VPN Manager
"""
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar módulos locales
sys.path.insert(0, str(Path(__file__).parent))

def test_version_module():
    """Prueba el módulo de versión"""
    print("🔍 Probando módulo de versión...")
    try:
        from version import get_version, get_app_info, GITHUB_REPO
        
        print(f"✅ Versión actual: {get_version()}")
        print(f"✅ Repositorio: {GITHUB_REPO}")
        
        app_info = get_app_info()
        print(f"✅ Información de la aplicación:")
        for key, value in app_info.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error probando módulo de versión: {e}")
        return False
    
    return True

def test_updater_module():
    """Prueba el módulo de actualización"""
    print("\n🔍 Probando módulo de actualización...")
    try:
        from auto_updater import UpdaterConfig, AutoUpdater
        
        print(f"✅ Configuración del actualizador:")
        print(f"   Repositorio: {UpdaterConfig.GITHUB_REPO}")
        print(f"   Versión actual: {UpdaterConfig.CURRENT_VERSION}")
        print(f"   URL de verificación: {UpdaterConfig.UPDATE_CHECK_URL}")
        
    except Exception as e:
        print(f"❌ Error probando módulo de actualización: {e}")
        return False
    
    return True

def test_github_api():
    """Prueba la conectividad con la API de GitHub"""
    print("\n🔍 Probando conectividad con GitHub API...")
    try:
        import requests
        from auto_updater import UpdaterConfig
        
        response = requests.get(
            UpdaterConfig.UPDATE_CHECK_URL,
            headers=UpdaterConfig.GITHUB_API_HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conectividad exitosa con GitHub")
            print(f"   Última release: {data.get('tag_name', 'N/A')}")
            print(f"   Fecha: {data.get('published_at', 'N/A')}")
            print(f"   Assets disponibles: {len(data.get('assets', []))}")
        elif response.status_code == 404:
            print("⚠️  No se encontraron releases en el repositorio")
        else:
            print(f"⚠️  Respuesta inesperada de GitHub: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error conectando con GitHub: {e}")
        return False
    
    return True

def test_qt_integration():
    """Prueba la integración con Qt (solo si está disponible)"""
    print("\n🔍 Probando integración con Qt...")
    try:
        # Verificar si Qt está disponible
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QThread
        
        print("✅ PyQt5 está disponible")
        print("✅ QThread está disponible para hilos de descarga")
        
        # Solo importar la clase, no inicializar QApplication aquí
        # ya que causaría el error de cocoa
        from auto_updater import AutoUpdater, UpdateCheckThread, UpdateDownloadThread
        print("✅ Clases de AutoUpdater importadas correctamente")
        
        return True
        
    except ImportError as e:
        print(f"⚠️  PyQt5 no está disponible: {e}")
        return False
    except Exception as e:
        print(f"❌ Error probando integración Qt: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 Iniciando pruebas del sistema de actualización automática")
    print("=" * 60)
    
    tests = [
        ("Módulo de versión", test_version_module),
        ("Módulo de actualización", test_updater_module),
        ("Conectividad GitHub", test_github_api),
        ("Integración Qt", test_qt_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando prueba '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n📊 Resumen de pruebas:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado final: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema de actualización está listo.")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores anteriores.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
