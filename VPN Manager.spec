# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=[('dialogs', 'dialogs'), ('threads', 'threads'), ('version.py', '.'), ('auto_updater.py', '.'), ('license.py', '.'), ('license_storage.py', '.'), ('license_encryptor.py', '.'), ('license_generator.py', '.'), ('models.py', '.')],
    hiddenimports=['PyQt5.sip', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'pexpect', 'requests', 'cryptography', 'packaging', 'urllib3', 'certifi'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VPN Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='VPN Manager.app',
    icon=None,
    bundle_identifier=None,
)
