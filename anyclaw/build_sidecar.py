#!/usr/bin/env python3
"""
PyInstaller build script - Package AnyClaw Sidecar as standalone executable

Usage:
    python build_sidecar.py [--platform PLATFORM] [--output DIR]

Platforms:
    macos-x64      - macOS Intel
    macos-arm64    - macOS Apple Silicon (M1/M2)
    windows-x64    - Windows 64-bit
    linux-x64      - Linux 64-bit
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# PyInstaller hidden imports - dynamically loaded modules need explicit declaration
HIDDEN_IMPORTS = [
    # uvicorn
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    # fastapi/starlette
    "starlette",
    "starlette.responses",
    "starlette.routing",
    "starlette.middleware",
    "starlette.staticfiles",
    # litellm
    "litellm",
    "litellm.integrations",
    # pydantic
    "pydantic",
    "pydantic_settings",
    # openai
    "openai",
    "httpx",
    "httpcore",
    "h11",
    "anyio",
    "anyio._backends._asyncio",
    # SSE
    "sse_starlette",
    # Common
    "json",
    "logging",
    "logging.config",
    "asyncio",
    "concurrent.futures",
    "multiprocessing",
    # datetime
    "dateutil",
    "dateutil.parser",
    # crypto
    "cryptography",
    # config
    "tomllib",
    # CLI (may be imported)
    "typer",
    "rich",
    "rich.console",
    "rich.progress",
]

# Packages to collect data from
COLLECT_DATA = [
    "litellm",
]

# Modules to exclude (reduce size)
EXCLUDE_MODULES = [
    "tkinter",
    "matplotlib",
    "numpy.f2py",
    "scipy.weave",
    "IPython",
    "jupyter",
    "notebook",
    "pytest",
    "black",
    "ruff",
    "mypy",
    "sphinx",
    "docutils",
]

# Platform to Tauri target triple mapping
PLATFORM_TARGETS = {
    "macos-x64": "x86_64-apple-darwin",
    "macos-arm64": "aarch64-apple-darwin",
    "windows-x64": "x86_64-pc-windows-msvc",
    "linux-x64": "x86_64-unknown-linux-gnu",
}


def get_current_platform() -> str:
    """Detect current platform"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        if machine in ("arm64", "aarch64"):
            return "macos-arm64"
        return "macos-x64"
    elif system == "windows":
        return "windows-x64"
    elif system == "linux":
        return "linux-x64"

    raise RuntimeError(f"Unsupported platform: {system} {machine}")


def get_executable_name(target: str) -> str:
    """Get executable name for platform"""
    if "windows" in target:
        return f"anyclaw-sidecar-{target}.exe"
    return f"anyclaw-sidecar-{target}"


def build_sidecar(target_platform: str, output_dir: Path) -> Path:
    """Build Sidecar executable"""

    # Get absolute paths
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.resolve()
    anyclaw_pkg = script_dir / "anyclaw"

    # Resolve output directory to absolute path
    output_dir = output_dir.resolve()
    binaries_dir = output_dir / "binaries"
    binaries_dir.mkdir(parents=True, exist_ok=True)

    # Get target triple
    target = PLATFORM_TARGETS.get(target_platform)
    if not target:
        raise ValueError(f"Unknown platform: {target_platform}")

    # Executable name
    exe_name = get_executable_name(target)
    output_path = binaries_dir / exe_name

    print(f"\n{'='*60}")
    print(f"Building AnyClaw Sidecar")
    print(f"  Platform: {target_platform}")
    print(f"  Target: {target}")
    print(f"  Script dir: {script_dir}")
    print(f"  Project root: {project_root}")
    print(f"  Output: {output_path}")
    print(f"{'='*60}\n")

    # Build PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(anyclaw_pkg / "__main__.py"),
        "--name=anyclaw-sidecar",
        "--onefile",
        "--console",
        "--clean",
        "--noconfirm",
        f"--distpath={binaries_dir}",
        f"--workpath={project_root / 'build' / 'sidecar_work'}",
        f"--specpath={project_root / 'build'}",
    ]

    # Add hidden imports
    for module in HIDDEN_IMPORTS:
        cmd.append(f"--hidden-import={module}")

    # Add data collection
    for package in COLLECT_DATA:
        cmd.append(f"--collect-data={package}")

    # Add excluded modules
    for module in EXCLUDE_MODULES:
        cmd.append(f"--exclude-module={module}")

    # Add runtime hook
    runtime_hook = project_root / "build" / "sidecar_hook.py"
    runtime_hook.parent.mkdir(parents=True, exist_ok=True)
    runtime_hook.write_text('''
# Sidecar runtime hook
import sys
import os

# Set default sidecar command
if len(sys.argv) == 1:
    sys.argv = [sys.argv[0], "sidecar", "--port", "62601"]
''', encoding='utf-8')
    cmd.append(f"--runtime-hook={runtime_hook}")

    # Run PyInstaller
    print(f"Running PyInstaller...")
    print(f"  Working directory: {project_root}")
    print(f"  Command: {' '.join(cmd[:8])}...")

    result = subprocess.run(cmd, cwd=str(project_root))

    if result.returncode != 0:
        raise RuntimeError(f"PyInstaller failed with exit code {result.returncode}")

    # Rename output file (PyInstaller outputs without platform suffix)
    temp_output = binaries_dir / "anyclaw-sidecar.exe" if "windows" in target else binaries_dir / "anyclaw-sidecar"

    print(f"\nLooking for PyInstaller output...")
    print(f"  Expected temp file: {temp_output}")

    if temp_output.exists():
        print(f"  Found temp file, renaming to: {output_path}")
        if output_path.exists():
            output_path.unlink()
        temp_output.rename(output_path)
    else:
        # Search for the generated file
        print(f"  Temp file not found, searching in: {binaries_dir}")
        found = False
        for f in binaries_dir.iterdir():
            if f.name.startswith("anyclaw-sidecar") and not f.name.endswith(".gitkeep"):
                print(f"  Found: {f}")
                if output_path.exists():
                    output_path.unlink()
                f.rename(output_path)
                found = True
                break
        if not found:
            # List directory contents for debugging
            print(f"  Directory contents:")
            for f in binaries_dir.iterdir():
                print(f"    {f.name}")

    if not output_path.exists():
        raise RuntimeError(f"Build output not found at {output_path}")

    # Set executable permission
    if "windows" not in target:
        output_path.chmod(0o755)

    # Check file size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Build successful!")
    print(f"  Output: {output_path}")
    print(f"  Size: {size_mb:.1f} MB")

    if size_mb > 100:
        print(f"  [WARN] File size exceeds 100MB target")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Build AnyClaw Sidecar executable with PyInstaller"
    )
    parser.add_argument(
        "--platform",
        choices=list(PLATFORM_TARGETS.keys()),
        help="Target platform (default: auto-detect)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tauri-app/src-tauri"),
        help="Output directory (default: tauri-app/src-tauri)",
    )

    args = parser.parse_args()

    # Auto-detect platform
    target_platform = args.platform or get_current_platform()

    try:
        output_path = build_sidecar(target_platform, args.output)
        print(f"\n[DONE] Sidecar build complete: {output_path}")
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
