#!/usr/bin/env python3
"""
PyInstaller 打包脚本 - 将 AnyClaw Sidecar 打包成独立可执行文件

用法:
    python build_sidecar.py [--platform PLATFORM] [--output DIR]

平台:
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

# PyInstaller 隐藏导入 - 这些模块动态加载，需要显式声明
HIDDEN_IMPORTS = [
    # uvicorn 相关
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
    # litellm 相关
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
    # 其他常用库
    "json",
    "logging",
    "logging.config",
    "asyncio",
    "concurrent.futures",
    "multiprocessing",
    # 日期时间
    "dateutil",
    "dateutil.parser",
    # 加密/安全
    "cryptography",
    # 配置
    "tomllib",
    # CLI 相关 (虽然 sidecar 不需要，但可能被导入)
    "typer",
    "rich",
    "rich.console",
    "rich.progress",
]

# 需要收集数据的包
COLLECT_DATA = [
    "litellm",
]

# 需要排除的模块（减小体积）
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

# 平台到 Tauri target triple 的映射
PLATFORM_TARGETS = {
    "macos-x64": "x86_64-apple-darwin",
    "macos-arm64": "aarch64-apple-darwin",
    "windows-x64": "x86_64-pc-windows-msvc",
    "linux-x64": "x86_64-unknown-linux-gnu",
}


def get_current_platform() -> str:
    """检测当前平台"""
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
    """根据平台获取可执行文件名"""
    if "windows" in target:
        return f"anyclaw-sidecar-{target}.exe"
    return f"anyclaw-sidecar-{target}"


def build_sidecar(target_platform: str, output_dir: Path) -> Path:
    """构建 Sidecar 可执行文件"""

    # 获取项目根目录
    # 脚本位于: anyclaw/build_sidecar.py
    # 项目根目录: anyclaw/.. (AnyClaw)
    # Python 包: anyclaw/anyclaw/
    script_dir = Path(__file__).parent
    project_root = script_dir.parent  # AnyClaw/
    anyclaw_pkg = script_dir / "anyclaw"  # anyclaw/anyclaw/ 包目录

    # 确定输出目录
    output_dir = output_dir / "binaries"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取 target triple
    target = PLATFORM_TARGETS.get(target_platform)
    if not target:
        raise ValueError(f"Unknown platform: {target_platform}")

    # 可执行文件名
    exe_name = get_executable_name(target)
    output_path = output_dir / exe_name

    print(f"\n{'='*60}")
    print(f"Building AnyClaw Sidecar")
    print(f"  Platform: {target_platform}")
    print(f"  Target: {target}")
    print(f"  Output: {output_path}")
    print(f"{'='*60}\n")

    # 构建 PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(anyclaw_pkg / "__main__.py"),
        "--name=anyclaw-sidecar",
        "--onefile",  # 打包成单个文件
        "--console",  # 保留控制台窗口（用于调试）
        "--clean",
        "--noconfirm",
        f"--distpath={output_dir}",
        f"--workpath={project_root / 'build' / 'sidecar_work'}",
        f"--specpath={project_root / 'build'}",
    ]

    # 添加隐藏导入
    for module in HIDDEN_IMPORTS:
        cmd.append(f"--hidden-import={module}")

    # 添加数据收集
    for package in COLLECT_DATA:
        cmd.append(f"--collect-data={package}")

    # 添加排除模块
    for module in EXCLUDE_MODULES:
        cmd.append(f"--exclude-module={module}")

    # 添加运行时钩子 - 确保 sidecar 模式
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

    # 平台特定配置
    if "windows" in target:
        # Windows 不显示控制台窗口（但保留用于调试）
        # cmd.append("--noconsole")  # 取消注释以隐藏控制台
        pass
    elif "macos" in target:
        # macOS 特定配置
        pass

    # 运行 PyInstaller
    print(f"Running PyInstaller...")
    print(f"  {' '.join(cmd[:10])}...")  # 只显示部分命令

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode != 0:
        raise RuntimeError(f"PyInstaller failed with exit code {result.returncode}")

    # 重命名输出文件（PyInstaller 输出文件名不带平台后缀）
    temp_output = output_dir / "anyclaw-sidecar"
    if "windows" in target:
        temp_output = output_dir / "anyclaw-sidecar.exe"

    if temp_output.exists():
        if temp_output != output_path:
            temp_output.rename(output_path)
    elif not output_path.exists():
        # 查找 PyInstaller 生成的文件
        for f in output_dir.iterdir():
            if f.name.startswith("anyclaw-sidecar") and not f.name.endswith(".gitkeep"):
                if f != output_path:
                    f.rename(output_path)
                break

    if not output_path.exists():
        # 如果还是没有找到，检查是否有不带后缀的文件
        fallback = output_dir / "anyclaw-sidecar"
        if fallback.exists():
            fallback.rename(output_path)
        else:
            raise RuntimeError(f"Build output not found at {output_path}")

    # 设置可执行权限
    if "windows" not in target:
        output_path.chmod(0o755)

    # 检查文件大小
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

    # 自动检测平台
    target_platform = args.platform or get_current_platform()

    try:
        output_path = build_sidecar(target_platform, args.output)
        print(f"\n[DONE] Sidecar build complete: {output_path}")
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
