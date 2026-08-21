#!/usr/bin/env bash
# ==============================================================================
# FORENZA: Forensic Evidence Operating System
# Desktop Distribution Installer Builder (Linux / macOS)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DESKTOP_DIR="${ROOT_DIR}/desktop"
FRONTEND_DIR="${ROOT_DIR}/frontend"
DIST_DIR="${ROOT_DIR}/dist/desktop"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${CYAN}${BOLD}=== FORENZA Standalone Desktop Installer Builder ===${NC}"
echo "Compiling native desktop installers (.AppImage / .deb / .dmg)..."
echo ""

# 1. Build Frontend
echo -e "${CYAN}[1/3] Building Next.js Frontend Bundle...${NC}"
cd "${FRONTEND_DIR}"
npm run build

# 2. Desktop Dependencies
echo -e "${CYAN}[2/3] Preparing Desktop Builder...${NC}"
cd "${DESKTOP_DIR}"
npm install --prefer-offline --no-audit

# 3. Compile Native Binaries
echo -e "${CYAN}[3/3] Executing Electron Builder...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    npx electron-builder --mac
else
    npx electron-builder --linux AppImage deb
fi

echo ""
echo -e "${GREEN}${BOLD}========================================================================${NC}"
echo -e "${GREEN}${BOLD}🎉 FORENZA Desktop Executables Built Successfully!${NC}"
echo -e "${GREEN}${BOLD}========================================================================${NC}"
echo -e "  ${BOLD}Output Directory:${NC} ${DIST_DIR}"
ls -lh "${DIST_DIR}" 2>/dev/null || true
echo ""
