#!/bin/bash
# AnyClaw Clean Build Script
# 清理所有构建产物

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${YELLOW}[CLEAN]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[DONE]${NC} $1"
}

echo "Cleaning build artifacts..."

# Python 构建产物
log_info "Removing Python build artifacts..."
rm -rf "$PROJECT_ROOT/anyclaw/build"
rm -rf "$PROJECT_ROOT/build"
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true

# PyInstaller 产物
log_info "Removing PyInstaller artifacts..."
rm -rf "$PROJECT_ROOT/anyclaw/dist"
rm -f "$PROJECT_ROOT/anyclaw/*.spec"

# Sidecar binaries
log_info "Removing sidecar binaries..."
rm -rf "$PROJECT_ROOT/tauri-app/src-tauri/binaries"

# Tauri 构建产物
log_info "Removing Tauri build artifacts..."
rm -rf "$PROJECT_ROOT/tauri-app/src-tauri/target"
rm -rf "$PROJECT_ROOT/tauri-app/dist"

# npm 产物
log_info "Removing npm artifacts..."
rm -rf "$PROJECT_ROOT/tauri-app/node_modules"

log_success "Clean complete!"
