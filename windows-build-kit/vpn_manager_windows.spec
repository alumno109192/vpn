# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
app_name = "VPN-Manager-Windows"

# Archivos a incluir
added_files = [
    ('dialogs', 'dialogs'),
    ('threads', 'threads'),
]

# Imports ocultos
hidden_imports = [
    'PyQt5.sip',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'pexpect',
    'requests',
    'cryptography',
    'packaging',
    'urllib3',
    'certifi',
    'json',
    'threading',
    'subprocess',
    'os',
    'sys',
    'platform',
    'pathlib',
]

# Módulos a excluir para reducir tamaño
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'PIL',
    'cv2',
    'torch',
    'tensorflow',
]

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
