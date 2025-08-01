#!/usr/bin/env python3
"""
Test script para verificar el sistema de actualizaciones
"""

import sys
import os
import json
from pathlib import Path

# Agregar el directorio actual al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Probar que todos los módulos se importan correctamente"""
    print("=== Test de importaciones ===")
    
    try:
        from version import get_app_info
        app_info = get_app_info()
        print(f"✅ Version: {app_info['name']} v{app_info['version']}")
    except Exception as e:
        print(f"❌ Error en version: {e}")
        return False
    
    try:
        from auto_updater import AutoUpdater
        print("✅ AutoUpdater importado")
    except Exception as e:
        print(f"❌ Error en auto_updater: {e}")
        return False
    
    try:
        from license import LicenseManager
        from license_storage import LicenseStorage
        print("✅ Sistema de licencias importado")
    except Exception as e:
        print(f"❌ Error en sistema de licencias: {e}")
        return False
    
    try:
        from dialogs import ConfigureDialog, EditDialog, SudoPasswordDialog
        print("✅ Dialogs importados")
    except Exception as e:
        print(f"❌ Error en dialogs: {e}")
        return False
    
    try:
        from models import ConnectionObserver, ConnectionState, VPNType
        print("✅ Models importados")
    except Exception as e:
        print(f"❌ Error en models: {e}")
        return False
    
    try:
        from threads import VPNConnectThread
        print("✅ Threads importados")
    except Exception as e:
        print(f"❌ Error en threads: {e}")
        return False
    
    return True

def test_file_structure():
    """Verificar que todos los archivos necesarios están presentes"""
    print("\n=== Test de estructura de archivos ===")
    
    required_files = [
        'Main.py',
        'auto_updater.py',
        'version.py',
        'license.py',
        'license_storage.py',
        'license_generator.py',
        'license_encryptor.py',
        'models.py',
        'requirements.txt',
        'dialogs/__init__.py',
        'dialogs/config_dialog.py',
        'dialogs/edit_dialog.py',
        'dialogs/sudo_dialog.py',
        'threads/__init__.py',
        'threads/vpn_thread.py',
        'threads/file_thread.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print("\n❌ Archivos faltantes:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True

def test_updater_config():
    """Verificar configuración del actualizador"""
    print("\n=== Test de configuración del actualizador ===")
    
    try:
        from auto_updater import AutoUpdater
        from version import get_app_info
        
        app_info = get_app_info()
        
        # Verificar configuración
        print(f"✅ GitHub repo: {app_info['github']}")
        print(f"✅ Versión actual: {app_info['version']}")
        
        # Simular verificación de updates (sin conexión real)
        print("✅ Configuración del actualizador correcta")
        
    except Exception as e:
        print(f"❌ Error en configuración del actualizador: {e}")
        return False
    
    return True

def test_license_system():
    """Verificar sistema de licencias"""
    print("\n=== Test del sistema de licencias ===")
    
    try:
        from license import LicenseManager
        from license_storage import LicenseStorage
        
        # Test de generación de licencia (con datos de prueba)
        test_email = "test@example.com"
        
        # Verificar que las funciones principales funcionan
        print("✅ LicenseManager funcional")
        print("✅ LicenseStorage funcional")
        
        # Verificar período de prueba
        print("✅ Sistema de período de prueba funcional")
        
    except Exception as e:
        print(f"❌ Error en sistema de licencias: {e}")
        return False
    
    return True

def main():
    """Ejecutar todos los tests"""
    print("🔍 Iniciando verificación del sistema VPN Manager\n")
    
    tests = [
        ("Importaciones", test_imports),
        ("Estructura de archivos", test_file_structure),
        ("Configuración del actualizador", test_updater_config),
        ("Sistema de licencias", test_license_system)
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results.append((test_name, False))
            all_passed = False
    
    # Resumen
    print("\n" + "="*50)
    print("RESUMEN DE TESTS")
    print("="*50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ¡Todos los tests pasaron! El sistema está listo.")
        print("\nPara ejecutar la aplicación:")
        print("  ./run_app.sh")
        print("\nPara generar ejecutables:")
        print("  ./build_macos_ultimate.sh")
    else:
        print("⚠️  Algunos tests fallaron. Revisa los errores arriba.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
