#!/bin/bash
# AnyClaw Sidecar-only Build Script
# 只构建 Sidecar（用于测试或跨平台构建）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 检测平台
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

# 显示帮助
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --platform PLATFORM   Target platform (macos-arm64, macos-x64, windows-x64, linux-x64)"
    echo "  --output DIR          Output directory (default: tauri-app/src-tauri)"
    echo "  --help                Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                              # Build for current platform"
    echo "  $0 --platform macos-arm64       # Build for macOS Apple Silicon"
    echo "  $0 --platform windows-x64       # Build for Windows"
}

# 解析参数
PLATFORM=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# 自动检测平台
if [[ -z "$PLATFORM" ]]; then
    PLATFORM=$(detect_platform)
fi

# 默认输出目录
if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="$PROJECT_ROOT/tauri-app/src-tauri"
fi

log_info "Building sidecar for $PLATFORM..."
log_info "Output directory: $OUTPUT_DIR"

cd "$PROJECT_ROOT/anyclaw"

# 构建
python3 build_sidecar.py --platform "$PLATFORM" --output "$OUTPUT_DIR"

log_success "Sidecar build complete!"
