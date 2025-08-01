#!/usr/bin/env python3
"""
Script para simular una nueva versión y probar el sistema de actualización
"""
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar módulos locales
sys.path.insert(0, str(Path(__file__).parent))

def simulate_new_version():
    """Simula una nueva versión cambiando temporalmente la versión actual"""
    print("🧪 Simulando nueva versión para probar actualizaciones...")
    
    try:
        # Leer el archivo version.py actual
        version_file = Path("version.py")
        with open(version_file, 'r') as f:
            content = f.read()
        
        # Crear backup
        backup_file = Path("version.py.backup")
        with open(backup_file, 'w') as f:
            f.write(content)
        
        print("✅ Backup creado: version.py.backup")
        
        # Cambiar temporalmente la versión a una más baja
        new_content = content.replace('__version__ = "1.0.0"', '__version__ = "0.9.0"')
        
        with open(version_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Versión cambiada temporalmente a 0.9.0")
        print("🔍 Ahora al ejecutar la aplicación debería detectar que v1.1 está disponible")
        print("")
        print("Para probar:")
        print("1. Ejecuta: python Main.py")
        print("2. Usa el menú del sistema → 'Buscar actualizaciones'")
        print("3. O ve a 'Acerca de' y presiona 'Buscar actualizaciones'")
        print("")
        print("Para restaurar la versión original:")
        print("python restore_version.py")
        
        # Crear script de restauración
        restore_script = '''#!/usr/bin/env python3
"""Script para restaurar la versión original"""
import shutil
from pathlib import Path

backup_file = Path("version.py.backup")
version_file = Path("version.py")

if backup_file.exists():
    shutil.copy2(backup_file, version_file)
    backup_file.unlink()
    print("✅ Versión original restaurada")
    print("✅ Backup eliminado")
else:
    print("❌ No se encontró el archivo de backup")
'''
        
        with open("restore_version.py", 'w') as f:
            f.write(restore_script)
        
        os.chmod("restore_version.py", 0o755)
        
        return True
        
    except Exception as e:
        print(f"❌ Error simulando nueva versión: {e}")
        return False

def main():
    print("🎭 Simulador de nueva versión para pruebas de actualización")
    print("=" * 60)
    
    if simulate_new_version():
        print("\n🎯 Simulación exitosa!")
        print("La aplicación ahora debería detectar actualizaciones disponibles.")
    else:
        print("\n❌ Error en la simulación")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
