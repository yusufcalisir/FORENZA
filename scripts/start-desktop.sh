#!/usr/bin/env bash
# ==============================================================================
# FORENZA: Forensic Evidence Operating System
# One-Click Desktop Workstation Launcher (Linux / macOS)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DESKTOP_DIR="${ROOT_DIR}/desktop"
FRONTEND_DIR="${ROOT_DIR}/frontend"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'
BOLD='\033[1m'

clear

echo -e "${PURPLE}${BOLD}"
echo "  ███████╗ ██████╗ ██████╗ ███████╗███╗   ██╗███████╗ █████╗ "
echo "  ██╔════╝██╔═══██╗██╔══██╗██╔════╝████╗  ██║╚══███╔╝██╔══██╗"
echo "  █████╗  ██║   ██║██████╔╝█████╗  ██╔██╗ ██║  ███╔╝ ███████║"
echo "  ██╔══╝  ██║   ██║██╔══██╗██╔══╝  ██║╚██╗██║ ███╔╝  ██╔══██║"
echo "  ██║     ╚██████╔╝██║  ██║███████╗██║ ╚████║███████╗██║  ██║"
echo "  ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝"
echo -e "${NC}"
echo -e "${CYAN}${BOLD}  FORENZA Native Forensic Desktop Workstation${NC}"
echo -e "  ISO/IEC 17025:2017 Aligned • Standalone Desktop Process Engine"
echo "  ──────────────────────────────────────────────────────────────────────────"
echo ""

# 1. Prerequisite Checks
echo -e "${CYAN}[1/3] Checking Node.js and Python Runtime...${NC}"
command -v node >/dev/null 2>&1 || { echo -e "${RED}[ERROR] Node.js is required.${NC}"; exit 1; }
command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || { echo -e "${RED}[ERROR] Python 3.12+ is required.${NC}"; exit 1; }
echo -e "  ${GREEN}✓ Node $(node --version) and Python detected.${NC}"

# 2. Dependencies
echo -e "${CYAN}[2/3] Verifying Desktop Dependencies...${NC}"
if [ ! -d "${DESKTOP_DIR}/node_modules" ]; then
    echo -e "  ${YELLOW}Installing desktop Electron dependencies...${NC}"
    cd "${DESKTOP_DIR}"
    npm install --prefer-offline --no-audit
fi
echo -e "  ${GREEN}✓ Desktop dependencies ready.${NC}"

# 3. Launch
echo -e "${CYAN}[3/3] Launching FORENZA Forensic Desktop Environment...${NC}"
cd "${DESKTOP_DIR}"
npx electron .
