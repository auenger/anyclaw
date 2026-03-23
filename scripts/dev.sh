#!/bin/bash
# AnyClaw Development Script
# 开发模式启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TAURI_DIR="$PROJECT_ROOT/tauri-app"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查依赖
check_deps() {
    # 检查 npm 依赖
    if [[ ! -d "$TAURI_DIR/node_modules" ]]; then
        log_info "Installing npm dependencies..."
        cd "$TAURI_DIR" && npm install
    fi
}

# 启动开发模式
start_dev() {
    log_info "Starting AnyClaw in development mode..."
    log_info "This will start Tauri which will automatically launch the sidecar using poetry/python"
    echo ""

    cd "$TAURI_DIR"
    npm run tauri:dev
}

# 显示帮助
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help       Show this help"
    echo ""
    echo "This script starts AnyClaw in development mode."
    echo "The sidecar will be launched automatically by Tauri using poetry/python."
}

# 主函数
main() {
    case "${1:-}" in
        --help)
            show_help
            exit 0
            ;;
    esac

    echo ""
    echo "============================================"
    echo "  AnyClaw Development Mode"
    echo "============================================"
    echo ""

    check_deps
    start_dev
}

main "$@"
