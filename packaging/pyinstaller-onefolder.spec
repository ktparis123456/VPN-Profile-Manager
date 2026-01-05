# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the VPN Profile Manager one-folder build.

This configuration collects the GUI application and copies optional
OpenConnect/OpenVPN client binaries into ``bin`` so the installer can
ship them under ``Program Files\\VPNProfileManager\\bin``.
"""
from pathlib import Path
import sys

block_cipher = None

spec_path = Path(globals().get("__file__", Path.cwd()))
project_root = spec_path.resolve().parent.parent

bin_payloads = [
    (str(project_root / "vendor" / "windows" / "openconnect.exe"), "bin"),
    (str(project_root / "vendor" / "windows" / "openvpn.exe"), "bin"),
]


a = Analysis(
    ['src/main.py'],
    pathex=[str(project_root / 'src')],
    binaries=[],
    datas=bin_payloads,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='VPNProfileManager',
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
    name='VPNProfileManager',
)
