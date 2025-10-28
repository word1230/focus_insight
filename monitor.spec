# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['D:\\projects\\focus_insight'],
    binaries=[],
    datas=[('data', 'data')],
    hiddenimports=[
        'matplotlib.backends.backend_tkagg',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'matplotlib.patches',
        'matplotlib.dates',
        'matplotlib.font_manager',
        'pynput',
        'win32gui',
        'win32process',
        'win32api',
        'win32con',
    ],
    hookspath=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FocusInsight-Monitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 监控程序需要控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FocusInsight-Monitor',
    debug=False,
    console=True,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)