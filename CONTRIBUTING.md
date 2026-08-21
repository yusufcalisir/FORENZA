# Contributing to FORENZA

Welcome to the **FORENZA: Forensic Evidence Operating System** contributor community. FORENZA is an enterprise multi-omic biocomputational forensic intelligence platform engineered to ISO/IEC 17025:2017 standards across 35 specialized subsystems grouped into 7 analytical pillars.

We welcome contributions from forensic geneticists, computational biologists, software engineers, biostatisticians, and security researchers.

---

## Table of Contents

1. [Forensic Scientific Integrity & Core Principles](#1-forensic-scientific-integrity--core-principles)
2. [Architecture Overview & Codebase Structure](#2-architecture-overview--codebase-structure)
3. [Local Development Environment Setup](#3-local-development-environment-setup)
   - [Prerequisites](#prerequisites)
   - [Backend Setup (FastAPI & Biocomputational Engine)](#backend-setup-fastapi--biocomputational-engine)
   - [Frontend Setup (Next.js 16 Workstation)](#frontend-setup-nextjs-16-workstation)
   - [Desktop App Setup (Electron Shell)](#desktop-app-setup-electron-shell)
   - [Air-Gapped Containerized Stack (Docker Compose)](#air-gapped-containerized-stack-docker-compose)
4. [Empirical Validation & Module Grounding Directive](#4-empirical-validation--module-grounding-directive)
   - [The 3 Mandatory Verification Criteria](#the-3-mandatory-verification-criteria)
   - [Mathematical Invariants](#mathematical-invariants)
5. [Testing & Quality Assurance Protocol](#5-testing--quality-assurance-protocol)
   - [Targeted Backend Testing](#targeted-backend-testing)
   - [Frontend & TypeScript Checks](#frontend--typescript-checks)
6. [Code Style & Engineering Standards](#6-code-style--engineering-standards)
   - [Python Standards](#python-standards)
   - [TypeScript & Frontend Guidelines](#typescript--frontend-guidelines)
   - [PowerShell & Automation Scripts](#powershell--automation-scripts)
7. [Git Workflow & Commit Conventions](#7-git-workflow--commit-conventions)
8. [Pull Request & Review Checklist](#8-pull-request--review-checklist)

---

## 1. Forensic Scientific Integrity & Core Principles

Because FORENZA produces courtroom-admissible forensic evaluations and expert witness reports (aligned with SWGDAM 2020 and ENFSI 2017 guidelines), all contributors must adhere to strict mathematical and scientific fidelity:

1. **Source of Truth:** Every equation, constant, algorithm, threshold, and biophysical model must derive verbatim from the scientific specifications in the `research/` directory.
2. **Zero Heuristics / Zero Invented Approximations:** Never invent arbitrary heuristic formulas or synthetic constants. Use standard empirical parameters (e.g. NIST 1036 population frequencies, Horvath $y_0 = 20.0$, GUM coverage factors $k=2.00$, etc.).
3. **Anti-Rubber-Stamping Directive:** Never declare a module or computation "VERIFIED" or "COMPLETE" without passing authentic empirical benchmarks. If there is a genuine mathematical discrepancy or theoretical boundary, document it transparently with exact error residuals (e.g., $|P_{\text{computed}} - P_{\text{analytical}}| < 10^{-4}$).
4. **Active Prosecutor's Fallacy Shields:** Numerical Likelihood Ratios ($LR$) must always be translated into balanced, conditional propositions adhering to the 7-tier ENFSI verbal scale in both English and Turkish.

---

## 2. Architecture Overview & Codebase Structure

```text
FORENZA/
├── backend/                  # Python 3.12+ FastAPI Biocomputational Microservices
│   ├── app/                  # REST API routers, models, and lifespan supervisor
│   │   ├── api/v1/           # Modular endpoints for 35 forensic subsystems
│   │   └── core/             # Configuration, CORS, middleware, and security
│   ├── node/services/        # Scientific implementations across all 7 Pillars
│   │   └── forensic/         # Probabilistic genotyping, kinship, phenotyping, etc.
│   └── tests/                # Pytest suites and Golden Benchmark Vectors
│
├── frontend/                 # Next.js 16 (App Router) + React 19 Workstation
│   ├── src/
│   │   ├── app/              # Dashboard pages and route handlers
│   │   ├── components/       # Tactical UI widgets, charts, 3D visualizers, maps
│   │   ├── lib/              # State management (Zustand), API clients, utilities
│   │   └── translations/     # Bilingual localization (saasTranslations.ts)
│   └── public/               # Static assets, SVG glyphs, and reference tables
│
├── desktop/                  # Native Electron 34+ Desktop Shell
│   ├── main.js               # Main process & Python sidecar supervisor
│   ├── preload.js            # Secure context-isolated IPC bridge
│   └── assets/               # Desktop icons and application metadata
│
├── infra/                    # Deployment & Air-Gap Infrastructure
│   └── airgap/               # Multi-container Docker Compose, Nginx TLS 1.3, init.sql
│
├── research/                 # 14 Definitive Scientific Research Specifications
├── docs/                     # Validation status matrices, math specs, deployment guides
└── scripts/                  # Cross-platform automation scripts (.ps1, .bat, .sh)
```

---

## 3. Local Development Environment Setup

### Prerequisites
- **Python:** `3.12` or newer (with `pip` and `venv`)
- **Node.js:** `20.x` or newer (LTS recommended) and `npm`
- **Docker & Docker Compose:** Optional for local dev; required for air-gapped stack
- **Git:** Latest version

### Backend Setup (FastAPI & Biocomputational Engine)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate a Python virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 4. Start the FastAPI development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API documentation (Swagger UI) is available at: `http://localhost:8000/docs`

### Frontend Setup (Next.js 16 Workstation)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Launch the Next.js development server with Turbopack
npm run dev
```
The workstation interface is available at: `http://localhost:3000`

### Desktop App Setup (Electron Shell)

```bash
# 1. Ensure backend Python environment and frontend are available
# 2. Run the one-click PowerShell launcher from repository root:
powershell -ExecutionPolicy Bypass -File .\scripts\start-desktop.ps1

# Or start manually:
cd desktop
npm install
npm run dev
```

### Air-Gapped Containerized Stack (Docker Compose)

```powershell
# From repository root:
powershell -ExecutionPolicy Bypass -File .\scripts\start-airgap.ps1
```
Workstation URL: `https://localhost:8443` (HTTP Gateway: `http://localhost:8080`)

---

## 4. Empirical Validation & Module Grounding Directive

When creating or modifying any of FORENZA's 35 biocomputational modules, you must satisfy the **3 Mandatory Verification Criteria** before the module status can be marked `VERIFIED` in `docs/VALIDATION_STATUS.md`:

### The 3 Mandatory Verification Criteria
1. **Criterion 1 (Standard Reference Ground Truth):** Verify analytical accuracy against authoritative reference datasets (e.g. NIST SRM 2391d, PROVEDIt, GIAB/1000 Genomes, EMPOP, EDNAP, or Zenodo FTIR libraries).
2. **Criterion 2 (Independent Tool Cross-Validation):** Results must be cross-checked against independent benchmark software (e.g. EuroForMix, STRmix, Familias 3, HaploSearch, HIrisPlex-S, VISAGE/Horvath DNAm models).
3. **Criterion 3 (5 Automated Edge-Case Tests):** Implement at least 5 distinct automated unit and integration tests covering:
   - High degradation / extreme drop-out ($P(D) > 0.60$)
   - Multi-contributor complex mixtures ($N \ge 3$)
   - Rare micro-variants and mutational steps
   - Zero-variance or singular numerical matrices
   - Boundary condition handling and non-zero simplex constraints

### Mathematical Invariants
All biocomputational code must enforce:
- **Probability Simplex:** $|\sum_{i} P_i - 1.0| \le 10^{-6}$
- **Log-Likelihood Additivity:** $|\log_{10} LR - \sum_l \log_{10} LR_l| < 10^{-6}$
- **Non-Negativity:** Variance $\sigma^2 \ge 0$, Peak Heights $\ge 0$, Frequencies $p_i \ge p_{\min}$.

---

## 5. Testing & Quality Assurance Protocol

### Targeted Backend Testing
To keep development fast and prevent timeout issues, **do not run global test suites indiscriminately**. Execute targeted tests for the specific module you are working on:

```bash
# Activate your backend virtual environment first
cd backend

# Example: Run tests for a specific forensic module
pytest node/services/forensic/test_probabilistic_genotyping.py -v

# Example: Run tests for lineage & kinship
pytest node/services/forensic/test_lineage_kinship.py -v
```

### Frontend & TypeScript Checks

```bash
cd frontend

# Linting
npm run lint

# TypeScript compilation check
npx tsc --noEmit
```

---

## 6. Code Style & Engineering Standards

### Python Standards
- **Formatting:** Format code with `black` (line length 100) and check with `flake8` / `ruff`.
- **Type Annotations:** Use full Python type annotations on all function signatures (`typing`, `pydantic`).
- **Pydantic v2 Protected Namespaces:** When defining fields starting with `model_` on Pydantic `BaseModel` schemas, always configure:
  ```python
  model_config = ConfigDict(protected_namespaces=())
  ```
- **Error Handling:** Use structured HTTP exceptions with clear forensic diagnostic detail.

### TypeScript & Frontend Guidelines
- **Responsive Parity:** All UI views must work across **Mobile (320px–640px)**, **Tablet (641px–1024px)**, and **Desktop/4K (1025px+)**.
- **Tactical Dark Aesthetic:** Use FORENZA's high-contrast theme (`bg-tactical-surface`, `border-tactical-border/60`, emerald for inclusion/Hp, red/rose for exclusion/Hd, amber for warnings).
- **Monospace Tabular Alignment:** Numbers, alleles, RFU values, and LRs must use `font-mono tabular-nums`.
- **No Mock Action Buttons:** Buttons like *"Run MCMC Sampler"* or *"Synthesize Proof"* must trigger genuine biocomputational calls, not idle timers.
- **Bilingual Support:** Add all new user-facing strings to `frontend/src/translations/saasTranslations.ts` in both English and Turkish.

### PowerShell & Automation Scripts
- **Portability:** Never hardcode absolute file paths, usernames, or drive letters. Derive paths dynamically via `$MyInvocation.MyCommand.Path`.
- **Character Encoding:** Use pure 7-bit ASCII characters in `.ps1` files to maintain 100% compatibility with Windows PowerShell 5.1+.
- **Process Safety:** Use `try / finally` blocks with `taskkill /PID <id> /T /F` to ensure child processes (like Next.js development servers) are cleanly terminated.

---

## 7. Git Workflow & Commit Conventions

We follow the **Conventional Commits** specification:

```text
<type>(<scope>): <short description>
```

### Allowed Types
- `feat`: A new forensic capability, endpoint, or UI component.
- `fix`: A bug fix in computation, launcher, or interface.
- `docs`: Documentation updates, validation status updates, research notes.
- `test`: Adding or updating unit tests and golden benchmark vectors.
- `refactor`: Code restructuring without changing mathematical results.
- `chore`: Dependency updates, tooling, or build configuration.

### Examples
```text
feat(pillar1): implement continuous mcmc gamma mixture deconvolution
fix(desktop): fix powershell launcher process tree termination
test(epigenetics): add 5 visage 5-cpg gold standard edge-case tests
docs(validation): update pillar 2 kinship status matrix
```

---

## 8. Pull Request & Review Checklist

Before opening a Pull Request, verify the following:

- [ ] **Branching:** Created a focused branch (e.g. `feat/pillar3-hirisplex`, `fix/bpa-area-of-origin`).
- [ ] **Research Alignment:** Math and algorithms align with the appropriate specification in `research/`.
- [ ] **Unit Tests:** Targeted `pytest` test suite passes with zero failures.
- [ ] **Lint & Types:** `npm run lint` and `npx tsc --noEmit` pass with zero errors.
- [ ] **No Hardcoded Secrets:** No API keys, JWT secrets, or local credentials committed.
- [ ] **Documentation:** If module status changed, `docs/VALIDATION_STATUS.md` and `README.md` are updated.
- [ ] **Clean Git History:** Commits follow Conventional Commits and are logically organized.

Thank you for helping advance open, reproducible, and verifiable forensic intelligence!
