# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('data', 'data'), ('tools\\alloy', 'tools\\alloy')]
binaries = []
hiddenimports = ['tkinter', 'tkinter.ttk', 'tkinter.font', 'PIL', 'PIL._tkinter_finder', 'pystray', 'pystray._win32', 'numpy', 'scipy', 'asteval', 'alloy', 'alloy.core', 'alloy.core.ecs', 'alloy.core.game_loop', 'alloy.core.event_bus', 'alloy.core.data_library', 'alloy.core.serializable', 'alloy.core.deps', 'alloy.core.paths', 'alloy.systems', 'alloy.systems.save_load', 'alloy.ai', 'alloy.ai.decision', 'alloy.ai.decision.behavior_tree', 'alloy.ai.decision.brain', 'alloy.ai.decision.difference_engine', 'alloy.fx', 'alloy.fx.particle', 'alloy.render', 'alloy.utils', 'alloy.utils.json_loader', 'alloy.utils.logger']
tmp_ret = collect_all('tkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PIL')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='LazyFishTank',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LazyFishTank',
)
