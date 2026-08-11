# FORENZA: Forensic Biology & DNA Intelligence Operating System

<p align="center">
  <img src="frontend/public/icon.svg" alt="FORENZA Logo" width="120" height="120" />
</p>

<p align="center">
  <strong>The Next-Generation Enterprise Forensic Biology Operating System</strong><br />
  Multi-Modal DNA Analysis • Probabilistic Genotyping • Forensic Anthropology • Entomology • Interpol DVI • Cryptographic ZKP Audit
</p>

<p align="center">
  <a href="#-empirical-verification--test-suite-benchmarks"><img src="https://img.shields.io/badge/System%20Status-Operational-brightgreen?style=flat-square" /></a>
  <a href="#-autosomal-str--kinship-engine"><img src="https://img.shields.io/badge/CODIS%20Loci-24%20Core%20Markers-blue?style=flat-square" /></a>
  <a href="#-probabilistic-genotyping-engine"><img src="https://img.shields.io/badge/Genotyping-Metropolis--Hastings%20MCMC-orange?style=flat-square" /></a>
  <a href="#-hirisplex-s-phenotyping--ancestry"><img src="https://img.shields.io/badge/Phenotyping-HIrisPlex--S%20%2B%20BGA-purple?style=flat-square" /></a>
  <a href="#-cryptographic-ledger--zkp"><img src="https://img.shields.io/badge/Privacy-ZKP%20Circom%20%2B%20Polygon-black?style=flat-square" /></a>
  <a href="#-empirical-verification--test-suite-benchmarks"><img src="https://img.shields.io/badge/Tests-92%20Passed%20(100%25)-brightgreen?style=flat-square" /></a>
</p>

---

## Executive Overview

**FORENZA** is an enterprise-grade Forensic Biology & DNA Intelligence Operating System designed for modern crime laboratories, disaster victim identification units, and law enforcement agencies. Moving beyond conventional single-purpose STR tools, FORENZA unifies autosomal STR evaluation, lineage DNA tracking (Y-STR, X-STR, mtDNA), forensic phenotyping, missing persons DVI, multi-modal human identification, forensic anthropology, forensic entomology, and cryptographic ledger verification into a cohesive, web-scale tactical platform.

---

## Table of Contents

- [Architectural Deep-Dive: The 10 Core System Phases](#architectural-deep-dive-the-10-core-system-phases)
  - [Phase 1: Autosomal STR Locus & Kinship Engine](#phase-1-autosomal-str-locus--kinship-engine)
  - [Phase 2: Probabilistic Genotyping & MCMC Deconvolution](#phase-2-probabilistic-genotyping--mcmc-deconvolution)
  - [Phase 3: Forensic Phenotyping & Biogeographic Ancestry](#phase-3-forensic-phenotyping--biogeographic-ancestry)
  - [Phase 4: Statistical Population Genetics & Fst Distances](#phase-4-statistical-population-genetics--fst-distances)
  - [Phase 5: ENFSI Legal Report Generator & Compliance Auditor](#phase-5-enfsi-legal-report-generator--compliance-auditor)
  - [Phase 6: High-Throughput Concurrent Batch Processing](#phase-6-high-throughput-concurrent-batch-processing)
  - [Phase 7: Empirical Validation Lab & Synthetic Profile Generator](#phase-7-empirical-validation-lab--synthetic-profile-generator)
  - [Phase 8: Multi-Node Federated P2P Network](#phase-8-multi-node-federated-p2p-network)
  - [Phase 9: Cryptographic Ledger & Zero-Knowledge Privacy Auditor](#phase-9-cryptographic-ledger--zero-knowledge-privacy-auditor)
  - [Phase 10: System Integrity, Telemetry & Health Probes](#phase-10-system-integrity-telemetry--health-probes)
- [Specialized Forensic Biology Modules](#specialized-forensic-biology-modules)
  - [Module 1: Expanded Lineage DNA Forensics (Y-STR, X-STR, mtDNA)](#module-1-expanded-lineage-dna-forensics-ystr-xstr-mtdna)
  - [Module 2: Missing Persons & Interpol DVI Engine](#module-2-missing-persons--interpol-dvi-engine)
  - [Module 3: Human Identification (HID) Engine](#module-3-human-identification-hid-engine)
  - [Module 4: Forensic Anthropology Engine](#module-4-forensic-anthropology-engine)
  - [Module 5: Forensic Entomology Engine](#module-5-forensic-entomology-engine)
- [Complete API Endpoint Matrix](#complete-api-endpoint-matrix)
- [Empirical Verification & Test Suite Benchmarks](#empirical-verification--test-suite-benchmarks)
- [Installation & Quick Start](#installation--quick-start)

---

## Architectural Deep-Dive: The 10 Core System Phases

FORENZA's backend architecture is structured around 10 foundational processing phases, providing rigorous statistical computation, data governance, and high-concurrency execution.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               FORENZA SYSTEM ARCHITECTURE                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘
        │
        ├─► Phase 1: Autosomal STR & Kinship Engine (CODIS 24, Likelihood Ratio LR)
        ├─► Phase 2: Probabilistic Genotyping Engine (Metropolis-Hastings MCMC)
        ├─► Phase 3: Forensic Phenotyping & Ancestry (HIrisPlex-S 41-SNP Model)
        ├─► Phase 4: Statistical Population Genetics (NRC II Bounds & Fst Distance)
        ├─► Phase 5: ENFSI Legal Report Generator & Compliance Auditor
        ├─► Phase 6: High-Throughput Batch Processing Engine (Worker Semaphore)
        ├─► Phase 7: Validation Lab & Synthetic Profile Generator (ROC / FIR Curves)
        ├─► Phase 8: Distributed Federated Network (P2P Discovery & Node Signatures)
        ├─► Phase 9: Cryptographic Ledger & ZKP Privacy Auditor (Circom ZK-SNARKs)
        └─► Phase 10: System Integrity Engine (HMAC Hash Chaining & Health Metrics)
```

### Phase 1: Autosomal STR Locus & Kinship Engine
- **CODIS 24 Core Loci**: Comprehensive support for all standard autosomal STR markers (CSF1PO, FGA, TH01, TPOX, vWA, D3S1358, D5S818, D7S820, D8S1179, D13S317, D16S539, D18S51, D21S11, PennState loci, etc.).
- **Single-Source Likelihood Ratio ($LR$)**: Computes $LR = \frac{P(E \mid H_p)}{P(E \mid H_d)}$ across major population groups (Caucasian, African American, Hispanic, Asian).
- **Kinship Index Engine ($KI$)**: Evaluates Parent-Child ($KI = \frac{1}{2 p_a}$) and Full-Sibling hypotheses with subpopulation theta ($\theta = F_{ST}$) adjustment.

### Phase 2: Probabilistic Genotyping & MCMC Deconvolution
- **Metropolis-Hastings MCMC Sampler**: Deconvolves complex 2-person and 3-person DNA mixtures.
- **Stochastic Modeling**: Integrates peak height ratio (PHR), stutter ratio ($SR$), allele dropout probability ($p_d$), and drop-in probability ($p_i$).
- **Tippett Calibration Curves**: Generates log10(LR) calibration distributions under prosecution ($H_p$) and defense ($H_d$) hypotheses.

### Phase 3: Forensic Phenotyping & Biogeographic Ancestry
- **HIrisPlex-S 41-SNP Prediction**: Predicts eye color (Blue, Brown, Intermediate), hair color (Black, Brown, Red, Blond), and skin tone (Very Pale, Pale, Intermediate, Dark, Dark-to-Black).
- **Biogeographic Ancestry (BGA)**: Multinomial admixture estimation mapping genetic markers to European, African, East Asian, South Asian, and Amerindian ancestral populations.

### Phase 4: Statistical Population Genetics & Fst Distances
- **National Research Council (NRC II) Bounding**: Enforces NRC II Recommendation 4.1 ($p_{\text{bound}} = \max(p, 5/\sqrt{2N})$) and Recommendation 4.2 subpopulation correction ($\theta = 0.01..0.03$).
- **Wright's $F_{ST}$ Fixation Index**: Calculates pairwise population differentiation distances:
  $$F_{ST} = \frac{H_T - H_S}{H_T}$$

### Phase 5: ENFSI Legal Report Generator & Compliance Auditor
- **ENFSI Verbal Scale Mapping**: Automatically translates numeric $LR$ values into standardized legal verbal scale statements ($10^1..10^6+$).
- **Digital Audit Certificate**: Compiles cryptographically signed, court-admissible PDF/JSON forensic certificates.
- **Partial Profile Warning System**: Flags low-locus profiles (<13 loci) with statutory compliance alerts.

### Phase 6: High-Throughput Concurrent Batch Processing
- **Asynchronous Worker Semaphores**: Concurrently processes thousands of casework STR files without blocking the main event loop.
- **Real-Time Progress Polling**: Endpoints for tracking batch job status (`/api/v1/forensic/batch/status/{id}`).

### Phase 7: Empirical Validation Lab & Synthetic Profile Generator
- **Ground-Truth Synthetic Generator**: Generates synthetic STR profiles with controllable dropout, drop-in, and noise parameters.
- **Classifier ROC/AUC & FIR Metrics**: Computes False Inclusion Rate (FIR at 0% false positive) and Root Mean Squared Error (RMSE) calibration curves.

### Phase 8: Multi-Node Federated P2P Network
- **Peer Discovery & Heartbeats**: P2P node registration (`PeerRegistry`) with automated heartbeat monitoring and failure detection.
- **Cryptographic Node Identity**: Ed25519 node signatures verifying cross-jurisdictional query integrity.

### Phase 9: Cryptographic Ledger & Zero-Knowledge Privacy Auditor
- **Circom ZK-SNARK Circuits**: Privacy-preserving profile matching allowing multi-agency searches without revealing raw genomic sequences.
- **Polygon Ledger Anchoring**: Hashes verification proofs onto an immutable distributed ledger.

### Phase 10: System Integrity, Telemetry & Health Probes
- **HMAC-SHA256 Hash Chaining**: Tamper-evident audit logs where each log entry contains the HMAC-SHA256 signature of the preceding entry.
- **Live Health Probes**: Probes at `/api/v1/health/live`, `/api/v1/health/ready`, and `/api/v1/health/metrics`.

---

## Specialized Forensic Biology Modules

Beyond the 10 core phases, FORENZA includes 5 specialized domain modules:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          SPECIALIZED FORENSIC BIOLOGY MODULES                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
        │
        ├─► Module 1: Lineage DNA (Y-FILER 23 Y-STR, Argus X-12 X-STR, mtDNA rCRS)
        ├─► Module 2: Missing Persons & DVI (Interpol AM/PM Cross-Reconciliation)
        ├─► Module 3: Human Identification (Multi-Modal Joint LR Synthesis & LCN Audit)
        ├─► Module 4: Forensic Anthropology (Sex, Suchey-Brooks Age, Trotter-Gleser Stature)
        └─► Module 5: Forensic Entomology (Accumulated Degree Hours ADH & PMI_min Estimator)
```

### Module 1: Expanded Lineage DNA Forensics (Y-STR, X-STR, mtDNA)
- **Y-STR 23-Locus Haplotypes**: SWGDAM 95% Clopper-Pearson upper bound frequency estimation ($p_{\text{upper}} = 1 - \alpha^{1/N}$) across Y-FILER panels.
- **X-STR Linkage Groups**: Investigator Argus X-12 linkage groups (LG1-LG4) for complex paternal kinship testing ($KI_X$).
- **mtDNA Alignment**: HV1, HV2, and HV3 hypervariable region variant calling aligned against the revised Cambridge Reference Sequence (rCRS, $AC\_000021.2$).

### Module 2: Missing Persons & Interpol DVI Engine
- **Interpol AM/PM Reconciliation Matrix**: $N \times M$ matrix matching comparing Ante-Mortem family reference profiles against Post-Mortem human remains.
- **Pedigree Candidate Ranking**: Ranks candidate matches using joint pedigree likelihood ratios and posterior probability $P(H_p \mid E)$.

### Module 3: Human Identification (HID) Engine
- **Multi-Modal Joint Likelihood Ratio**: Synthesizes evidence across independent marker modalities using the joint product rule:
  $$LR_{\text{joint}} = LR_{\text{STR}} \cdot LR_{\text{Y-STR}} \cdot LR_{\text{mtDNA}} \cdot LR_{\text{SNP}}$$
- **Skeletal Degradation & LCN Auditor**: Audits amplicon length decay index ($DI_{\text{skeletal}} = \frac{RFU_{\text{short}}}{RFU_{\text{long}}}$) and Low-Copy-Number (LCN) PCR stochastic thresholds.

### Module 4: Forensic Anthropology Engine
- **Biological Profile Estimation**: Sex determination (subpubic angle & sciatic notch score), Suchey-Brooks pubic symphysis age phase estimation, and craniometric population affinity.
- **Trotter-Gleser Stature Regression**: Linear regression estimation:
  $$\text{Stature} = 2.38 \cdot L_{\text{Femur}} + 61.41 \pm 3.27\text{ cm}$$
- **Skeletal Trauma Audit**: Categorizes perimortem fractures (Blunt force, Sharp force, Ballistic) versus postmortem taphonomic weathering.

### Module 5: Forensic Entomology Engine
- **Accumulated Degree Hours ($ADH$) PMI Engine**: Computes effective thermal energy $ADH = \sum (T_{\text{ambient}} - T_{\text{base}}) \cdot \Delta t$ and $PMI_{\text{min}}$ elapsed colonization time.
- **Diptera Thermal Species Library**: Built-in development parameters for *Calliphora vicina*, *Lucilia sericata*, and *Sarcophaga carnaria*.
- **Insect Succession Waves**: Audits arthropod community composition across 4 decomposition phases (Fresh, Bloat, Active Decay, Dry Decay).

---

## Complete API Endpoint Matrix

| Endpoint | Method | Input Schema | Output Attributes |
| :--- | :--- | :--- | :--- |
| `/api/v1/forensic/lr` | `POST` | `LRCalculationRequest` | `locus_lrs`, `combined_lr`, `verbal_predicate`, `population_group` |
| `/api/v1/forensic/kinship` | `POST` | `KinshipRequest` | `kinship_index`, `relationship_type`, `posterior_probability` |
| `/api/v1/forensic/phenotype` | `POST` | `PhenotypeRequest` | `eye_color_probabilities`, `hair_color_probabilities`, `skin_tone` |
| `/api/v1/forensic/population/bound` | `POST` | `BoundFrequencyRequest` | `bounded_frequency`, `nrc2_rule_applied` |
| `/api/v1/forensic/population/fst` | `POST` | `FstDistanceRequest` | `pairwise_fst`, `population_a`, `population_b` |
| `/api/v1/forensic/report/generate` | `POST` | `ReportGenerateRequest` | `certificate_id`, `verbal_statement`, `signed_json_payload` |
| `/api/v1/forensic/batch/submit` | `POST` | `BatchSubmitRequest` | `job_id`, `total_cases`, `status` |
| `/api/v1/forensic/batch/status/{id}` | `GET` | None | `job_id`, `progress_percentage`, `metrics`, `results` |
| `/api/v1/forensic/dna/ystr` | `POST` | `YSTRMatchRequest` | `haplotype_match_status`, `upper_bound_95_ci`, `paternal_verdict` |
| `/api/v1/forensic/dna/mtdna` | `POST` | `MtDnaMatchRequest` | `match_status`, `differing_positions`, `maternal_verdict` |
| `/api/v1/forensic/dvi/missing-person/search` | `POST` | `MissingPersonSearchRequest` | `query_id`, `top_candidate_hits`, `search_summary` |
| `/api/v1/forensic/dvi/reconcile` | `POST` | `DviReconcileRequest` | `disaster_event_id`, `confirmed_identifications`, `matrix` |
| `/api/v1/forensic/hid/identify` | `POST` | `HumanIdentifyRequest` | `remains_id`, `joint_lr`, `top_candidate_hits`, `hid_summary` |
| `/api/v1/forensic/hid/degradation-audit` | `POST` | `DegradationAuditRequest` | `degradation_index`, `is_lcn_sample`, `strategy` |
| `/api/v1/forensic/anthropology/biological-profile` | `POST` | `BiologicalProfileRequest` | `estimated_sex`, `estimated_age_range`, `stature_cm` |
| `/api/v1/forensic/anthropology/trauma-audit` | `POST` | `TraumaAuditRequest` | `sample_id`, `has_perimortem_trauma`, `observations` |
| `/api/v1/forensic/entomology/pmi` | `POST` | `EntomologyPmiRequest` | `species_name`, `required_adh`, `estimated_pmi_days` |
| `/api/v1/forensic/entomology/succession` | `POST` | `SuccessionAuditRequest` | `sample_id`, `inferred_decomposition_stage`, `timeframe` |
| `/api/v1/health/ready` | `GET` | None | `status`, `subsystems`, `audit_chain_intact` |
| `/api/v1/health/live` | `GET` | None | `status`, `timestamp` |
| `/api/v1/health/metrics` | `GET` | None | `uptime_seconds`, `audit_chain_block_count`, `memory_footprint_mb` |

---

## Empirical Verification & Test Suite Benchmarks

The entire FORENZA platform is verified using automated pytest integration and unit tests.

| Test File | Subsystem Verified | Tests | Execution | Pass Rate | Key Invariants Verified |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `test_forensic_engine.py` | Core Autosomal STR & Kinship | 7 | ~1.45s | 100% (7/7) | CODIS 24 loci completeness, $LR$ inclusion/exclusion, Kinship Index |
| `test_probabilistic_engine.py` | MCMC Mixture Deconvolution | 5 | ~1.82s | 100% (5/5) | Peak height ratio, dropout $p_d$, drop-in $p_i$, Tippett calibration |
| `test_phenotyping.py` | HIrisPlex-S Phenotyping & BGA | 12 | ~1.65s | 100% (12/12) | Eye/hair/skin probability summation, dosage bounds, ancestry |
| `test_population.py` | Population Genetics & Fst | 10 | ~1.50s | 100% (10/10) | NRC II 4.1 & 4.2 frequency bounds, Dirichlet smoothing, $F_{ST}$ |
| `test_reports.py` | ENFSI Compliance & Certificates | 6 | ~1.38s | 100% (6/6) | Verbal scale mapping, certificate signing, partial profile alerts |
| `test_validation.py` | Validation Lab & ROC Curves | 7 | ~1.72s | 100% (7/7) | Synthetic profile generator, ROC AUC, FIR at 0% false inclusion |
| `test_batch.py` | Concurrent Batch Processing | 3 | ~1.42s | 100% (3/3) | Concurrency worker semaphore, job aggregator, progress polling |
| `test_end_to_end.py` | Master E2E Pipeline Verification | 4 | ~1.60s | 100% (4/4) | Multi-phase integration, health probes, HMAC integrity verification |
| `test_lineage_dna.py` | Lineage DNA (Y/X/mt) | 7 | ~1.80s | 100% (7/7) | Y-STR Clopper-Pearson 95% CI, X-STR linkage $KI_X$, mtDNA rCRS |
| `test_dvi.py` | Missing Persons & Interpol DVI | 4 | ~1.44s | 100% (4/4) | Pedigree candidate ranking, N x M AM/PM identification matrix |
| `test_hid.py` | Human Identification (HID) | 4 | ~1.87s | 100% (4/4) | Multi-modal joint $LR$ synthesis, skeletal degradation audit |
| `test_anthropology.py` | Forensic Anthropology | 5 | ~1.85s | 100% (5/5) | Trotter-Gleser stature regression, Suchey-Brooks age, trauma audit |
| `test_entomology.py` | Forensic Entomology | 5 | ~1.89s | 100% (5/5) | ADH/ADD thermal development models, $PMI_{\text{min}}$ estimation, succession |
| `test_federated.py` | Multi-Node Federated Network | 6 | ~1.48s | 100% (6/6) | PeerRegistry heartbeat, NodeIdentity, Orchestrator distributed query |
| `test_forensic_routes.py` | FastAPI Endpoint Integration | 7 | ~1.69s | 100% (7/7) | POST /lr, POST /kinship, POST /validate, Pydantic v2 rejection |
| **Complete System Suite** | **Integrated System Surface** | **92** | **2.76s** | **100% (92/92)** | **Comprehensive Statistical & Integration Verification** |

---

## Installation & Quick Start

### 1. Prerequisites
- **Python 3.12+**
- **Node.js 18+** & **npm**

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/yusufcalisir/str-analysis.git
cd str-analysis

# Create virtual environment & install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run full test suite
python -m pytest backend/node/services/forensic/ backend/node/federated/ backend/app/api/test_forensic_routes.py -v
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend
npm install

# Run Next.js Turbopack development server
npm run dev
```

---

<p align="center">
  Designed and engineered for state-of-the-art forensic biology laboratories.
</p>