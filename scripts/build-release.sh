#!/bin/bash
# AnyClaw Release Build Script
# 构建 Sidecar 和 Tauri 应用

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TAURI_DIR="$PROJECT_ROOT/tauri-app"
BINARIES_DIR="$TAURI_DIR/src-tauri/binaries"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测当前平台
detect_platform() {
    case "$(uname -s)" in
        Darwin*)
            if [[ "$(uname -m)" == "arm64" ]]; then
                echo "macos-arm64"
            else
                echo "macos-x64"
            fi
            ;;
        Linux*)     echo "linux-x64" ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows-x64" ;;
        *)          echo "unknown" ;;
    esac
}

# 检查依赖
check_dependencies() {
    log_info "Checking dependencies..."

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.11+."
        exit 1
    fi

    # 检查 PyInstaller
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        log_warn "PyInstaller not found. Installing..."
        pip install pyinstaller
    fi

    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found. Please install Node.js 18+."
        exit 1
    fi

    # 检查 npm 依赖
    if [[ ! -d "$TAURI_DIR/node_modules" ]]; then
        log_info "Installing npm dependencies..."
        cd "$TAURI_DIR" && npm install
    fi

    log_success "All dependencies checked."
}

# 构建 Sidecar
build_sidecar() {
    local platform="$1"
    log_info "Building sidecar for $platform..."

    cd "$PROJECT_ROOT/anyclaw"

    # 运行 PyInstaller 打包
    python3 build_sidecar.py --platform "$platform" --output "$TAURI_DIR/src-tauri"

    # 验证输出
    local target_name
    case "$platform" in
        macos-arm64) target_name="anyclaw-sidecar-aarch64-apple-darwin" ;;
        macos-x64)   target_name="anyclaw-sidecar-x86_64-apple-darwin" ;;
        windows-x64) target_name="anyclaw-sidecar-x86_64-pc-windows-msvc.exe" ;;
        linux-x64)   target_name="anyclaw-sidecar-x86_64-unknown-linux-gnu" ;;
    esac

    if [[ -f "$BINARIES_DIR/$target_name" ]]; then
        local size=$(du -h "$BINARIES_DIR/$target_name" | cut -f1)
        log_success "Sidecar built: $BINARIES_DIR/$target_name ($size)"
    else
        log_error "Sidecar build failed: $BINARIES_DIR/$target_name not found"
        exit 1
    fi
}

# 构建 Tauri 应用
build_tauri() {
    log_info "Building Tauri application..."

    cd "$TAURI_DIR"

    # 运行 Tauri 构建
    npm run tauri:build

    log_success "Tauri build complete."
}

# 主函数
main() {
    local platform=$(detect_platform)

    echo ""
    echo "============================================"
    echo "  AnyClaw Release Build"
    echo "============================================"
    echo "  Platform: $platform"
    echo "  Project:  $PROJECT_ROOT"
    echo "============================================"
    echo ""

    # 检查依赖
    check_dependencies

    # 构建 Sidecar
    build_sidecar "$platform"

    # 构建 Tauri
    build_tauri

    echo ""
    log_success "🎉 Build complete!"
    echo ""
    echo "Release artifacts:"
    ls -la "$TAURI_DIR/src-tauri/target/release/bundle/" 2>/dev/null || true
}

main "$@"
