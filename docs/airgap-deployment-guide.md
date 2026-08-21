# FORENZA: Air-Gapped Workstation Deployment & Operations Guide

<p align="center">
  <strong>Enterprise Multi-Omic Forensic Intelligence Operating System</strong><br />
  ISO/IEC 17025:2017 Aligned • Standalone Air-Gapped Docker Architecture • Zero External Cloud Telemetry
</p>

---

## Table of Contents

1. [Executive Summary & Air-Gap Threat Model](#1-executive-summary--air-gap-threat-model)
2. [Hardware & System Sizing Matrix](#2-hardware--system-sizing-matrix)
3. [End-to-End Offline Deployment Workflow](#3-end-to-end-offline-deployment-workflow)
   - [Phase A: Package Assembly on Internet-Connected Build Host](#phase-a-package-assembly-on-internet-connected-build-host)
   - [Phase B: Secure USB Flash Drive Transfer](#phase-b-secure-usb-flash-drive-transfer)
   - [Phase C: One-Click Launch on Air-Gapped Workstation](#phase-c-one-click-launch-on-air-gapped-workstation)
4. [Container Architecture & Service Network](#4-container-architecture--service-network)
5. [SSL/TLS 1.3 Certificate & Browser Trust Management](#5-ssltls-13-certificate--browser-trust-management)
6. [Data Persistence, Backup & Snapshot Protocol](#6-data-persistence-backup--snapshot-protocol)
7. [Operations & Troubleshooting Manual](#7-operations--troubleshooting-manual)
8. [ISO/IEC 17025:2017 Offline Quality Assurance & Audit Protocol](#8-isoiec-170252017-offline-quality-assurance--audit-protocol)

---

## 1. Executive Summary & Air-Gap Threat Model

In accredited criminal justice institutions, police forensic departments, and national forensic medicine institutes (e.g., Forensic Science Laboratories, Gendarmerie Criminal Laboratories, Adli Tıp Kurumu), biometric and genomic casework profiles must never leave an isolated, physically segregated network (**Air-Gapped Network**).

**FORENZA Air-Gap Package** provides a 100% self-contained multi-container deployment designed to run indefinitely without any outbound internet access:
* **Embedded Reference Standards:** Master frequency matrices (NIST 1036 4-population, YHRD R68, EMPOP R15, 55-AIMs, HIrisPlex-S, VISAGE 5-CpG, precipitation isoscapes) are baked directly into the backend container image.
* **Zero Telemetry / Zero Cloud Phoning:** All telemetry, analytics, and font/script CDNs are severed; all UI scripts, icons, WebAssembly snarkjs verifiers, and CSS are bundled locally.
* **Cryptographic Local Custody:** Binary Merkle Trees and HMAC-SHA256 audit ledgers anchor immutable chain of custody locally into PostgreSQL 16.

---

## 2. Hardware & System Sizing Matrix

| Deployment Profile | Target Environment | Minimum CPU | Minimum RAM | Storage | Operating System |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Field Investigation Laptop** | Crime scene mobile van / Portable forensic unit | 4 Cores (x86_64) | **4 GB** (8 GB recommended) | 20 GB SSD | Windows 10/11 Pro, Ubuntu 22.04 LTS |
| **Forensic Laboratory Workstation** | DNA / Serology / Ballistics casework bench | 8 Cores (x86_64) | **16 GB** | 100 GB NVMe | Windows 11 Pro / Enterprise, Debian 12 |
| **Central Institute Rack Server** | Institutional LIMS & Multi-Analyst Network | 16+ Cores | **32 GB – 64 GB** | 500 GB RAID-10 NVMe | Ubuntu Server 22.04/24.04, RHEL 9 |

---

## 3. End-to-End Offline Deployment Workflow

```
[Online Build Machine] ────────> [USB Flash Drive] ────────> [Air-Gapped Forensic Machine]
  Run package-airgap.sh           Copy forenza-airgap.tar.gz   Run start-airgap.sh
  Builds & exports Docker images  (ISO 17025 SHA-256 Check)    Spins up 5 containers in 15s
```

### Phase A: Package Assembly on Internet-Connected Build Host

On an internet-connected workstation with Docker installed, clone the repository and execute the packaging script:

#### Linux / macOS:
```bash
# Clone the repository
git clone https://github.com/yusufcalisir/FORENZA.git
cd FORENZA

# Build and package all container images and configs
./scripts/package-airgap.sh
```

#### Windows (PowerShell):
```powershell
git clone https://github.com/yusufcalisir/FORENZA.git
cd FORENZA

# Execute packager
powershell -ExecutionPolicy Bypass -File .\scripts\package-airgap.ps1
```

The packager builds `forenza-backend:latest` and `forenza-frontend:latest`, pulls `nginx:1.25-alpine`, `postgres:16-alpine`, `redis:7-alpine`, exports them to a unified tarball (`forenza-airgap-images.tar.gz`), and produces `dist/forenza-airgap-v2.0.0.tar.gz` (or `.zip` on Windows).

---

### Phase B: Secure USB Flash Drive Transfer

1. Copy `dist/forenza-airgap-v2.0.0.tar.gz` (or `.zip`) to an authorized forensic USB storage device.
2. Record the **SHA-256 Checksum** in the laboratory intake log for ISO 17025 traceability:
   ```bash
   sha256sum forenza-airgap-v2.0.0.tar.gz
   ```
3. Transfer the media to the air-gapped target machine and extract the archive:
   ```bash
   tar -xzf forenza-airgap-v2.0.0.tar.gz
   cd forenza-airgap-v2.0.0
   ```

---

### Phase C: One-Click Launch on Air-Gapped Workstation

#### On Linux / macOS:
```bash
chmod +x ./scripts/start-airgap.sh
./scripts/start-airgap.sh
```

#### On Windows:
Double-click `start-airgap.bat` or run in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-airgap.ps1
```

The script will automatically:
1. Validate Docker Engine and Compose runtime.
2. Check host RAM.
3. Generate local TLS 1.3 self-signed certificates in `infra/airgap/certs/`.
4. Load container images from the offline tarball into the local Docker daemon.
5. Initialize the PostgreSQL LIMS schema (`init.sql`).
6. Launch all 5 containers in detached mode (`docker compose up -d`).
7. Poll health checks and launch default browser at **`https://localhost:8443`**.

---

## 4. Container Architecture & Service Network

```
+-----------------------------------------------------------------------------------------+
|                                    HOST MACHINE                                         |
|                                                                                         |
|   https://localhost:8443 (Workstation UI & API)          http://localhost:8080 (HTTP)   |
|                             |                                         |                 |
+─────────────────────────────┼─────────────────────────────────────────┼─────────────────+
                              |                                         |
                              v                                         v
+─────────────────────────────────────────────────────────────────────────────────────────+
|   CONTAINER 1: forenza-airgap-gateway (Nginx 1.25 Alpine)                               |
|   • TLS 1.3 SSL Termination • Reverse Proxy • Security Headers • WebSocket Upgrades     |
+──────────────────────────────────────────┬──────────────────────────────────────────────+
                                           |
                    +──────────────────────┴──────────────────────+
                    |                                             |
                    v (Internal: 3000)                            v (Internal: 8000)
+─────────────────────────────────────────+   +───────────────────────────────────────────+
| CONTAINER 2: forenza-airgap-frontend    |   | CONTAINER 3: forenza-airgap-backend       |
| • Next.js 16 Standalone Workstation UI  |   | • FastAPI Microservices Engine            |
| • 35 Subsystem Analysis Dashboards      |   | • 35 Biocomputational Modules (Pillars 1-7|
| • Offline Asset Cache (Tailwind/React)  |   | • Embedded Reference Datasets (NIST 1036) |
+─────────────────────────────────────────+   +─────────────────────┬─────────────────────+
                                                                    |
                                        +───────────────────────────┴───────────────────────────+
                                        |                                                       |
                                        v (Internal: 5432)                                      v (Internal: 6379)
+─────────────────────────────────────────────────────────+   +─────────────────────────────────+
| CONTAINER 4: forenza-airgap-postgres (PostgreSQL 16)    |   | CONTAINER 5: forenza-airgap-redis
| • Persistent LIMS & Custody Ledger Data (Volume Mount)  |   | • Redis 7 In-Memory Cache       |
| • Merkle Root Hashes & ZKP Verification Signatures      |   | • Asynchronous MCMC Task Queue  |
+─────────────────────────────────────────────────────────+   +─────────────────────────────────+
```

---

## 5. SSL/TLS 1.3 Certificate & Browser Trust Management

When connecting to `https://localhost:8443`, the browser may display a self-signed certificate notice (`NET::ERR_CERT_AUTHORITY_INVALID`).

### Installing Certificate into Local System Trust Store:

* **Google Chrome / Edge (Windows):**
  1. Navigate to `https://localhost:8443` $\to$ Click *"Not Secure"* in address bar $\to$ *"Certificate is not valid"*.
  2. Click Details $\to$ *"Export..."* (Save as `forenza-local.crt`).
  3. Double-click `forenza-local.crt` $\to$ *"Install Certificate..."* $\to$ *"Local Machine"* $\to$ Select *"Trusted Root Certification Authorities"* $\to$ Finish.
  4. Restart browser. The padlock icon will show **Secure Connection (HTTPS)**.

* **Linux (Ubuntu/Debian):**
  ```bash
  sudo cp infra/airgap/certs/server.crt /usr/local/share/ca-certificates/forenza-local.crt
  sudo update-ca-certificates
  ```

---

## 6. Data Persistence, Backup & Snapshot Protocol

All case files, LIMS accession records, Merkle inclusion hashes, and analytical reports are stored in named Docker volumes on the host system:
* `forenza_airgap_postgres_data` $\to$ Relational database records
* `forenza_airgap_backend_data` $\to$ Raw uploaded EPG/VCF data files
* `forenza_airgap_redis_data` $\to$ Queue state

### Creating a Snapshot Backup:

Execute on the host terminal:
```bash
# 1. Export relational database snapshot
docker exec -t forenza-airgap-postgres pg_dump -U forenza forenza_lims > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Export full evidence volume archive
docker run --rm -v forenza_airgap_backend_data:/data -v $(pwd):/backup alpine tar -czf /backup/evidence_data_$(date +%Y%m%d).tar.gz /data
```

### Restoring from a Snapshot:

```bash
docker exec -i forenza-airgap-postgres psql -U forenza forenza_lims < backup_20260821_120000.sql
```

---

## 7. Operations & Troubleshooting Manual

### Essential CLI Commands

```bash
# View live logs of all containers in real time
docker compose -f infra/airgap/docker-compose.yml logs -f

# View logs of specific service
docker compose -f infra/airgap/docker-compose.yml logs -f backend

# Check operational container status and healthchecks
docker compose -f infra/airgap/docker-compose.yml ps

# Gracefully stop the platform (data is preserved in volumes)
docker compose -f infra/airgap/docker-compose.yml down

# Restart the gateway after updating TLS certificates
docker compose -f infra/airgap/docker-compose.yml restart gateway
```

### Common Troubleshooting Scenarios

| Symptom | Probable Root Cause | Resolution |
| :--- | :--- | :--- |
| **Port 8443 / 8080 Conflict** | Another local service (e.g. Apache, IIS, VMware) uses port 8443/8080. | Edit `.env.airgap` and change `GATEWAY_HTTPS_PORT=9443`, `GATEWAY_HTTP_PORT=9080`, then run `docker compose up -d`. |
| **MCMC Memory OOM** | Insufficient RAM allocated to Docker Desktop. | Open Docker Desktop Settings $\to$ *Resources* $\to$ Allocate at least **6 GB RAM** and **4 CPUs**. |
| **Backend Healthcheck Unhealthy** | PostgreSQL container took longer than 20s to initialize. | Wait 30 seconds; backend will automatically reconnect once PostgreSQL completes initialization. |

---

## 8. ISO/IEC 17025:2017 Offline Quality Assurance & Audit Protocol

When operating in offline air-gapped environments, the system maintains strict conformity with ISO/IEC 17025:2017 and FBI QAS standards:

1. **Deterministic Verification Vector Execution:**  
   Analyst can navigate to **Validation Lab Panel** (`/analysis/validation-lab`) in the UI or execute:
   ```bash
   docker exec -t forenza-airgap-backend pytest node/services/forensic/test_forensic_engine.py -v
   ```
2. **Immutable Forensic Ledger Hashing:**  
   Every computation automatically hashes input parameters with SHA-256 and records an inclusion leaf into the local binary Merkle tree.
3. **Formal Export Integrity:**  
   Generated ISO 17025 PDF reports include cryptographic SHA-256 checksums, expanded measurement uncertainty budgets ($U_{95} = 2.00 \cdot u_c$), and active Prosecutor's Fallacy shields in bilingual English and Turkish formats.
