#!/usr/bin/env python3
# xj_build.py —— 一键编译 fishtank.epf
"""
XJ380 EPF 构建脚本。
用法: python xj_build.py [--clean]

依赖:
  clang++ / ld.lld : C:\\Users\\13122\\.workbuddy\\binaries\\llvm\\bin\\
  XJ380 SDK        : G:\\soft\\XJ380_XACT_2026v4_windows\\depend\\
  Python 3.14      : C:\\Users\\13122\\AppData\\Local\\Programs\\Python\\Python314\\python.exe
"""

import os, sys, subprocess, glob, shutil
from pathlib import Path

# ── 路径配置 ──────────────────────────────────────────────────
PROJECT_ROOT = Path(r"G:\fish\xj380")
LLVM_BIN    = Path(r"C:\Users\13122\.workbuddy\binaries\llvm\bin")
SDK_DEPEND  = Path(r"G:\soft\XJ380_XACT_2026v4_windows\depend")
SDK_INCLUDE = SDK_DEPEND / "include"
SDK_OBJ_GUI = SDK_DEPEND / "obj-gui"

CLANGPP = LLVM_BIN / "clang++.exe"
LD_LLD  = LLVM_BIN / "ld.lld.exe"

OUT_EPF = PROJECT_ROOT / "fishtank.epf"
BUILD_DIR = PROJECT_ROOT / "build_epf"

# ── 编译标志 ──────────────────────────────────────────────────
CFLAGS = [
    "--target=x86_64-unknown-elf",
    "-Wall",
    "-ffreestanding",
    "-fno-builtin",
    "-m64",
    "-std=c++11",
    "-fno-stack-protector",
    "-fno-exceptions",
    "-fshort-wchar",
    "-nostdinc",
    f"-I{SDK_INCLUDE}",
    f"-I{PROJECT_ROOT / 'src' / 'core'}",
    f"-I{PROJECT_ROOT / 'src' / 'gui'}",
    "-Wno-writable-strings",
    "-D", "__XJ380_OS__",
    "-ffp-contract=off",
]

def find_cpp_files():
    """收集 src/core/ 和 src/gui/ 下所有 .cpp"""
    files = []
    for sub in ["src/core", "src/gui"]:
        pattern = str(PROJECT_ROOT / sub / "*.cpp")
        files.extend(glob.glob(pattern))
    return sorted(files)

def compile_one(src: Path) -> Path:
    """编译单个 .cpp → .o"""
    obj = BUILD_DIR / (src.stem + ".o")
    cmd = [str(CLANGPP)] + CFLAGS + ["-c", str(src), "-o", str(obj)]
    print(f"  CC  {src.name}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        sys.exit(1)
    if result.stderr.strip():
        print(f"  WARN: {result.stderr.strip()}")
    return obj

def collect_obj_gui():
    """收集 SDK obj-gui 下所有 .o（排除 start.cpp.o，它在链接时手动置首）"""
    objs = []
    for root, dirs, files in os.walk(str(SDK_OBJ_GUI)):
        for f in files:
            if f.endswith(".o") and f != "start.cpp.o":
                objs.append(Path(root) / f)
    return sorted(objs)

def link_epf(my_objs, sdk_objs):
    """链接所有 .o → fishtank.epf"""
    ld_script = ["-flavor", "gnu", "-m", "elf_x86_64", "-Ttext=0x200000"]

    # start.cpp.o 置首
    start_o = SDK_OBJ_GUI / "start.cpp.o"
    objs = [str(start_o)] + [str(o) for o in my_objs] + [str(o) for o in sdk_objs]

    # liballoc-x86_64.a
    liballoc = SDK_OBJ_GUI / "liballoc-x86_64.a"

    cmd = [str(LD_LLD)] + ld_script + objs + [str(liballoc), "-o", str(OUT_EPF)]
    print(f"\n  LINK → {OUT_EPF.name}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print(f"  LINK ERROR: {result.stderr}")
        sys.exit(1)
    if result.stderr.strip():
        print(f"  LINK WARN: {result.stderr.strip()}")

def verify_epf():
    """验证 EPF 产物：ELF 头 + 节表 + 符号"""
    import subprocess as sp

    size = os.path.getsize(OUT_EPF)
    print(f"\n  → {OUT_EPF} ({size} bytes)")

    # llvm-nm 符号
    llvm_nm = LLVM_BIN / "llvm-nm.exe"
    if llvm_nm.exists():
        print(f"\n  === llvm-nm symbols (fish/painter/offline) ===")
        r = sp.run([str(llvm_nm), str(OUT_EPF)], capture_output=True, text=True)
        lines = r.stdout.splitlines()
        for line in lines:
            if any(k in line for k in ["fish", "settle_offline", "economy", "painter", "geometry"]):
                print(f"    {line}")
        print(f"  (total symbols: {len(lines)})")

    # objdump 节表
    llvm_objdump = LLVM_BIN / "llvm-objdump.exe"
    if llvm_objdump.exists():
        print(f"\n  === llvm-objdump -h (sections) ===")
        r = sp.run([str(llvm_objdump), "-h", str(OUT_EPF)], capture_output=True, text=True)
        for line in r.stdout.splitlines()[:20]:
            print(f"    {line}")

def main():
    if not CLANGPP.exists():
        print(f"FATAL: clang++ not found at {CLANGPP}")
        sys.exit(1)
    if not SDK_INCLUDE.exists():
        print(f"FATAL: SDK include not found at {SDK_INCLUDE}")
        sys.exit(1)

    if "--clean" in sys.argv:
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
        if OUT_EPF.exists():
            os.remove(OUT_EPF)
        print("Clean OK")
        return

    BUILD_DIR.mkdir(exist_ok=True)
    print(f"=== xj_build: fishtank.epf ===")
    print(f"  clang++: {CLANGPP}")
    print(f"  SDK:     {SDK_INCLUDE}")

    # 1. 收集源文件
    cpp_files = find_cpp_files()
    print(f"\n  Found {len(cpp_files)} .cpp files")

    # 2. 编译
    my_objs = []
    for cpp in cpp_files:
        obj = compile_one(cpp)
        my_objs.append(obj)
    print(f"\n  All {len(my_objs)} source files compiled OK")

    # 3. 收集 SDK .o
    sdk_objs = collect_obj_gui()
    print(f"  SDK .o files: {len(sdk_objs)}")

    # 4. 链接
    link_epf(my_objs, sdk_objs)

    # 5. 验证
    verify_epf()

    print(f"\n=== BUILD SUCCESS ===")

if __name__ == "__main__":
    main()
