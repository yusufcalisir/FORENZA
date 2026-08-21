# FORENZA — Module Validation Status

**Purpose:** This file is the single source of truth for which modules are real (validated against external reference data and tools) vs. simulated/prototype. Update this table every time a module's validation status changes. The UI's "Verified" / "Research Preview" badges should be generated from this file (or a machine-readable version of it), not hand-set per component.

**Rule:** A module only moves to `VERIFIED` when all three items in its checklist entry (see `VALIDATION_CHECKLIST.md`) are complete: (1) at least one known reference dataset run through it, (2) at least one cross-check against an independent external tool, (3) at least 5 documented edge-case tests passing. No partial credit — a module is either `VERIFIED` or it isn't.

**Statuses:** `NOT_STARTED` · `IN_PROGRESS` · `VERIFIED`

Last updated: 2026-08-20 (1.4.7 LTDNA Stochastic Low-Template Modeling Fully Validated & Verified)

---

## Pillar 1 — Probabilistic Genotyping

| ID | Module | Status | Reference Dataset | Cross-Check Tool | Edge Cases Passing | Notes |
|---|---|---|---|---|---|---|
| STR-24 | Autosomal STR & Kinship Engine | VERIFIED | NIST SRM 2391d / PowerPlex Fusion 24 / ForenSeq MainstAY | NIST 1036 PopGen / FragalyseQt / GeneMarker HID | 5/5 | 24-Locus expanded CODIS + SE33 + Penta D/E, Balding-Nichols theta, SMM mutation kinship |
| MCMC-MH | MCMC Mixture Deconvoluter | VERIFIED | Zenodo BTSC 349/268 & PROVEDIt (synthetic EPG via BiophysicalPeakModel) | STRmix Log-Normal LL / EuroForMix Gamma LL (both engines implemented) | 5/5 | 5 edge-case tests passing: Convergence R̂≤1.10, 1:19 imbalance, 1:1 MLE symmetry, back-stutter discrimination, adaptive acceptance [0.10,0.55]; 10 API integration tests passing |
| NRC-II | Dirichlet Fst Population Genetics | VERIFIED | NIST 1036 4-Populations (N=1036), 1000 Genomes Phase 3, SRM 2391d A/B/C | NRC II (1996) Rec 4.4 Tables 4.1/4.2, Curran & Buckleton (2007) Weighted ANOVA, Familias 3 / EuroForMix PopGen | 5/5 | 5 edge cases passing: Zero-theta HWE reduction, theta=0.15 endogamy stress, 24-locus diploid simplex unity sum, demographic cross-comparison ratio, reciprocal balance symmetry; 47 module tests passing |
| LTDNA | Touch DNA & Low-Template Modeling | VERIFIED | Peter Gill LCN Dilution Series (15-1000pg), 4-Substrate Matrix, Golden Casework VECTOR_03 & VECTOR_TERM_06, NIST SRM 2391d A | LikeLTD Semi-Continuous Logistic Grid (18/18 concordant), EuroForMix Gamma Continuous Integral (R²=0.9952), Curran-Gill 4-State Closed Forms (|P_computed - P_analytical| < 10⁻⁴), STRmix Inverse Variance Scaling | 5/5 | 5 edge cases passing: EC-01 Pristine 1000pg asymptote, EC-02 Single-cell 15pg bound (P(D)=88.08%), EC-03 Exact Poisson drop-in & 24-locus clean product (61.88%), EC-04 Sub-AT RFU culling (AT=50RFU), EC-05 Hb peak imbalance & false homozygote mask; 106 module tests passing |
| TIPPETT | Tippett Calibration & Validation | VERIFIED | 10k Monte Carlo True Donor & Non-Donor Vectors (NIST 1036), Pristine 24L, LTDNA Touch 40% Dropout, NIST SRM 2391d Comp A | FoCal / Ramos & Gonzalez-Rodriguez (2013) Cllr benchmark (|Cllr_computed - Cllr_FoCal| < 10⁻⁵), EuroForMix 24-Locus Separation (AUC ≥ 0.9990), STRmix Misleading Evidence Standard (P(LR ≥ 10⁶ | Hd) ≤ 10⁻⁶, 0 false positives), ENFSI 2017 7-Tier Scale & Prosecutor's Fallacy Shield | 5/5 | 5 edge cases passing: EC-TIP-01 Dense 500-pt monotonicity invariant, EC-TIP-02 Zero false positives in 10,000 trials, EC-TIP-03 AUC=1.000000 pristine separation, EC-TIP-04 P(D)=0.60 shift without negative bias, EC-TIP-05 Symmetrical neutral decision intersection; 104 module tests passing |

## Pillar 2 — Lineage Forensics & Kinship

| ID | Module | Status | Reference Dataset | Cross-Check Tool | Edge Cases Passing | Notes |
|---|---|---|---|---|---|---|
| Y-STR | Y-Chromosome STR Lineage | VERIFIED | YHRD Release 68 ($N=385,000$ global + 5 regional partitions), Certified Reference Standards NIST SRM 2391d Comp A (R1b), HG002 (J2a), NA18507 (O2a), female negative controls NA12878/NA19240, 4 Casework Cohorts | YHRD Online Engine & Surveying Method concordance ($|\hat{p}_{\text{computed}} - \hat{p}_{\text{YHRD}}| < 10^{-6}$), Applied Biosystems YFiler Plus developmental validation, Ballantyne & Kayser (2012) RM Y-STR model ($3.02\times$ father-son differentiation boost), ISFG (2020) patrilineal reporting shield | 5/5 | 27 Loci (21 standard + 6 RM markers / 7 targets), Clopper-Pearson 95% Snedecor F bound ($k=0, N=385,000 \implies p_{\text{upper}} = 7.7811 \times 10^{-6}$), Brenner theta coancestry, DYS389 pure decoupling, SMM $m$-meioses paternal LR, Bayesian haplogroups (16 modal clades), 63 module tests passing |
| X-STR | X-Chromosome STR Kinship | VERIFIED | Tillmar et al. (2017) Argus X-12 European & Asian populations, Certified Standards NA12878 (46,XX), NA19240 (46,XX), SRM 2391d Comp A (46,XY), HG002 (46,XY), Benchmark VECTOR_P2_02 | Familias 3 X-STR Linkage Module, Kling et al. linkage disequilibrium cluster formulas, Kosambi mapping function ($|\Delta r| < 10^{-6}$), ISFG (2012) & ENFSI (2017) evaluative reporting shield | 5/5 | 12 Loci across 4 Linkage Groups (LG1–LG4), Kosambi mapping function $r = \frac{1}{2}\tanh(2d/100)$ & inverse, hemizygous male diallelic validation, PHS $KI_X \approx 1.854 \times 10^5$, Father-Daughter Duo, PGM-GD deficiency, 68 tests passing |
| mtDNA | Mitochondrial DNA Lineage | VERIFIED | EMPOP Release 15 ($N=48,500$ mitogenomes), Certified Standards NIST SRM 2391d Comp A (H1a1), NA12878 (H1), NA19240 (L2a1), HG002 (T2b), NA18507 (D4a1), 5 Casework Cohorts | EMPOP SAM 2, HaploSearch, HaploGrep 3 / PhyloTree Build 17, ISFG (2014, 2020) & SWGDAM guidelines | 5/5 | rCRS NC_012920.1 (16,569 bp), HV1/HV2/HV3, ISFG 3'-right alignment normalizer (309.1C, 315.1C, 16189.1C, 524.1AC), IUPAC point heteroplasmy (R,Y,M,K,S,W), Clopper-Pearson 95% bound ($k=0, N=48,500 \implies p_{\text{upper}}=6.1764 \times 10^{-5}, LR=16,190.7$), SWGDAM $\ge 2$ difference maternal exclusion, 56 tests passing |
| DVI-PED | Interpol DVI Pedigree Matching | NOT_STARTED | Interpol DVI Standard | Familias 3 DVI Engine | 0/5 | Joint Pedigree Likelihood |
| aDNA-SNP | Degraded/Ancient DNA SNP Panel | NOT_STARTED | Columbus / Briggs Deamination | mapDamage 2.0 Kinetics | 0/5 | Terminal C->T overhang decay |

## Pillar 3 — Phenotyping & Ancestry

| ID | Module | Status | Reference Dataset | Cross-Check Tool | Edge Cases Passing | Notes |
|---|---|---|---|---|---|---|
| HIRISPLEX | HIrisPlex-S Eye/Hair/Skin | NOT_STARTED | Walsh 2018 (N=632) | Erasmus MC HIrisPlex-S | 0/5 | 41-SNP Multinomial Logistic |
| BGA-55 | 55-SNP Biogeographic Ancestry | NOT_STARTED | Kidd 2014 (73 Pops) | FROG-kb / STRUCTURE | 0/5 | 55-SNP AIM GIS Centroids |
| CRANIO-3D | 3D Craniofacial Morphology | NOT_STARTED | Claes 2014 (20 Landmarks)| 3D Procrustes Superposition| 0/5 | Sexual dimorphism & craniometry |
| HAIR-TEX | Hair Texture Prediction | NOT_STARTED | Medland 2009 / Adhikari | Polygenic Risk Score (PRS) | 0/5 | EDAR V370A / TCHH / AR Balding |
| MC1R-UV | MC1R Epistasis / UV Sensitivity | NOT_STARTED | Sulem 2007 MC1R Cohort | Red Hair Color (RHC) Model | 0/5 | Loss-of-function epistasis |

## Pillar 4 — Epigenetics & Aging

| ID | Module | Status | Reference Dataset | Cross-Check Tool | Edge Cases Passing | Notes |
|---|---|---|---|---|---|---|
| HORVATH | Horvath/VISAGE Methylation Clock | NOT_STARTED | VISAGE Consortium / PMC11988829 | Horvath DNAmAge / VISAGE R | 0/5 | 5-CpG Elastic Net (y0=20.0) |
| tDMR-FLUID | Tissue-Specific DMR Deconvolution | NOT_STARTED | VISAGE Enhanced (Blood/Bone/Semen)| NNLS / QDA Deconvolution | 0/5 | 6-Tissue Epigenetic Calling |
| AHRR | AHRR Smoking/Lifestyle Biomarker | NOT_STARTED | Philibert 2015 (N=850) | cg05575921 Regression | 0/5 | Pack-Years & Alcohol Index |
| TELO-CHRONO | Telomere Length Age Estimation | NOT_STARTED | Cawthon 2002 qPCR Curve | Delta-Delta Ct Formula | 0/5 | T/S ratio & Post-Mortem PMI |
| miRNA | microRNA Body Fluid Profiling | NOT_STARTED | Zubakov 2010 miRNA Set | BMIQ Normalization | 0/5 | Bisulfite QC & miRNA fluids |

## Pillar 5 — Physical Evidence & Trace

| ID | Module | Status | Reference Dataset | Cross-Check Tool | Edge Cases Passing | Notes |
|---|---|---|---|---|---|---|
| BPA-3D | 3D Bloodstain Pattern Analysis | NOT_STARTED | SWGSTAIN Test Cards | Least-Squares Origin RK4 | 0/5 | Impact angle & 3D convergence |
| GSR-CMC | Gunshot Residue SEM-EDX | NOT_STARTED | ASTM E1588-20 GSR Data | Congruent Matching Cells | 0/5 | Pb-Ba-Sb & 3D striations |
| ENTO-PMI | Entomological Post-Mortem Interval | NOT_STARTED | Greenberg & Kunich PMI | Thermal Summation (ADH) | 0/5 | Degree-Hours post-mortem clock |
| MSI-FTIR | Fiber/Trace Spectroscopy Classifier | NOT_STARTED | Zenodo FTIR-Plastics & Arch Lib | Hit Quality Index (HQI) | 0/5 | ATR-FTIR & Raman Spectral Angle |
| TOX-PMR | Toxicology / Postmortem Redistribution | NOT_STARTED | SOFT/AAFS Case Database | Widmark BAC & C/P Ratio | 0/5 | Morphine fatal & PMR models |

## Pillar 6 — Governance, LIMS & ZKP

| ID | Module | Status | Reference Dataset | Cross-Check Tool | Edge Cases Passing | Notes |
|---|---|---|---|---|---|---|
| MERKLE-COC | Merkle Tree Chain of Custody | NOT_STARTED | NIST SP 800-106 / fsagen | RFC 6962 Merkle Verifier | 0/5 | Immutable binary hash ledger |
| ZKP-BN254 | Circom Groth16 ZK Proof Engine | NOT_STARTED | SnarkJS BN254 Vectors | Ethereum Groth16 Contract | 0/5 | Zero-Knowledge Blind Auditor |
| ISO-17025 | ISO 17025 Report/Uncertainty Compiler | NOT_STARTED | JCGM 100:2008 / FBI QAS 2025 | GUM Uncertainty Budget | 0/5 | Expanded uncertainty U95 (k=2) |
| COURT-MODE | Court/Expert-Witness Report Generator | NOT_STARTED | ENFSI 2017 Benchmarks | ENFSI 7-Tier Bilingual | 0/5 | Evaluative reporting & shield |
| JUROR-3D | 3D Juror Spatial Visualizer | NOT_STARTED | NIST Demonstrative Set | Three.js Spatial Transform | 0/5 | WebGL crime scene raycasting |

## Pillar 7 — Geo-Forensic Intelligence

| ID | Module | Status | Reference Dataset | Cross-Check Tool | Edge Cases Passing | Notes |
|---|---|---|---|---|---|---|
| ISOTOPES | Multi-Isotope Isoscape Sourcing | NOT_STARTED | IAEA/GNIP Global Grids | EPA IsoMAP Bivariate PDF | 0/5 | O-H & Strontium 87/86 |
| SOIL-CODA | Soil QXRD Compositional Analysis | NOT_STARTED | USGS Soil Database | Aitchison CLR / Mahalanobis | 0/5 | Mineralogy & trace chemistry |
| PALYNO | Palynology (Pollen) Biome Matching | NOT_STARTED | European Pollen Database | Bray-Curtis Dissimilarity | 0/5 | Pollen taxon assemblages |
| ROSSMO | Rossmo Geographic Profiling | NOT_STARTED | Rossmo 1999 Benchmark | Rossmo CGT Formula | 0/5 | Distance decay & buffer zone |
| FUSION | 2D Adaptive KDE Geo-Fusion | NOT_STARTED | Multi-Omic Casework Vector | 2D Adaptive Gaussian KDE | 0/5 | Joint Bayesian spatial surface |

---

## Summary counters

- Verified: 4 / 35
- In Progress: 0 / 35
- Not Started: 31 / 35

## UI integration rule

The workstation UI must read this file's status (or a machine-readable version of it, e.g. generated by a small script that parses this table) to decide whether a module gets a `VERIFIED` badge or a `RESEARCH PREVIEW` badge. Never hand-set a badge to `ACTIVE`/`VERIFIED` in a component without a corresponding `VERIFIED` row here.
