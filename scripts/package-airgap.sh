#!/usr/bin/env bash
# ==============================================================================
# FORENZA: Forensic Evidence Operating System
# Offline Air-Gap Distribution Packager (Run on Online Build Machine)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
PKG_VERSION="2.0.0"
PKG_NAME="forenza-airgap-v${PKG_VERSION}"
PKG_WORK_DIR="${DIST_DIR}/${PKG_NAME}"

# Color Codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${CYAN}${BOLD}=== FORENZA Air-Gap Distribution Packager ===${NC}"
echo "Building full standalone offline bundle for USB / air-gapped installation..."
echo ""

mkdir -p "${DIST_DIR}"
rm -rf "${PKG_WORK_DIR}"
mkdir -p "${PKG_WORK_DIR}/infra/airgap" "${PKG_WORK_DIR}/scripts" "${PKG_WORK_DIR}/docs"

# 1. Pull Third-Party Base Images
echo -e "${CYAN}[1/4] Pulling Base Images...${NC}"
docker pull nginx:1.25-alpine
docker pull postgres:16-alpine
docker pull redis:7-alpine

# 2. Build FORENZA Production Images
echo -e "${CYAN}[2/4] Building FORENZA Microservices & Workstation Images...${NC}"
docker build -t forenza-backend:latest -f "${ROOT_DIR}/backend/Dockerfile" "${ROOT_DIR}"
docker build -t forenza-frontend:latest -f "${ROOT_DIR}/frontend/Dockerfile" "${ROOT_DIR}/frontend"

# 3. Export Docker Images to Compressed Tarball
echo -e "${CYAN}[3/4] Exporting and Compressing Container Images (~350 MB)...${NC}"
TAR_PATH="${PKG_WORK_DIR}/forenza-airgap-images.tar.gz"

docker save \
    forenza-backend:latest \
    forenza-frontend:latest \
    nginx:1.25-alpine \
    postgres:16-alpine \
    redis:7-alpine | gzip -c > "${TAR_PATH}"

echo -e "  ${GREEN}✓ Exported container images to ${TAR_PATH}${NC}"

# 4. Assemble Offline Package Assets
echo -e "${CYAN}[4/4] Assembling Distribution Archive...${NC}"
cp -r "${ROOT_DIR}/infra/airgap/"* "${PKG_WORK_DIR}/infra/airgap/"
cp "${ROOT_DIR}/scripts/start-airgap.sh" "${PKG_WORK_DIR}/scripts/"
cp "${ROOT_DIR}/scripts/start-airgap.ps1" "${PKG_WORK_DIR}/scripts/"
cp "${ROOT_DIR}/scripts/start-airgap.bat" "${PKG_WORK_DIR}/"
cp "${ROOT_DIR}/docs/airgap-deployment-guide.md" "${PKG_WORK_DIR}/docs/"

# Make scripts executable
chmod +x "${PKG_WORK_DIR}/scripts/start-airgap.sh"

# Create root-level start script link
cat << 'EOF' > "${PKG_WORK_DIR}/start.sh"
#!/usr/bin/env bash
./scripts/start-airgap.sh
EOF
chmod +x "${PKG_WORK_DIR}/start.sh"

# Compress into final distribution zip and tar.gz
cd "${DIST_DIR}"
tar -czf "${PKG_NAME}.tar.gz" "${PKG_NAME}"

# Compute SHA-256 Checksum for ISO/IEC 17025 Chain-of-Custody verification
CHECKSUM=$(sha256sum "${PKG_NAME}.tar.gz" | awk '{print $1}')

echo ""
echo -e "${GREEN}${BOLD}========================================================================${NC}"
echo -e "${GREEN}${BOLD}🎉 Air-Gapped Package Created Successfully!${NC}"
echo -e "${GREEN}${BOLD}========================================================================${NC}"
echo -e "  ${BOLD}Distribution Archive:${NC} ${DIST_DIR}/${PKG_NAME}.tar.gz"
echo -e "  ${BOLD}Size:${NC}                 $(du -h "${DIST_DIR}/${PKG_NAME}.tar.gz" | awk '{print $1}')"
echo -e "  ${BOLD}SHA-256 Checksum:${NC}     ${CYAN}${CHECKSUM}${NC}"
echo ""
echo -e "  ${BOLD}Air-Gap Deployment Instructions:${NC}"
echo "  1. Copy ${PKG_NAME}.tar.gz to an approved forensic USB drive."
echo "  2. Transfer and extract onto the air-gapped forensic workstation."
echo "  3. Execute: cd ${PKG_NAME} && ./start.sh (or double-click start-airgap.bat on Windows)."
echo ""
