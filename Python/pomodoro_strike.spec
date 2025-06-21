# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pomodoro_strike.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('settings.json', '.'),
        ('todos.json', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'pystray',
        'CTkToolTip',
        'tkinter',
        'json',
        'threading',
        'time',
        'datetime',
        'winsound',
        'platform',
        'math',
        'random',
        'csv',
        'collections',
        'sys',
        'os'
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PomodoroStrike',
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
