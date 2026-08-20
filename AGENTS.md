# FORENZA Agent Operating Guidelines & Mandatory Research Rules

This repository contains the **FORENZA: Forensic Evidence Operating System**. All AI agents, subagents, and automated systems operating on this repository must strictly adhere to the rules outlined below.

---

## 🔒 Master Rule 1: Absolute Research Fidelity & Mathematical Integrity

### 1. Source of Truth
Every formula, equation, constant, algorithm, threshold, benchmark vector, and biophysical model across all 30 biocomputational modules **MUST derive exclusively and verbatim from the 6 research specifications** in the `research/` directory:
- [`pillar_1_probabilistic_genotyping_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_1_probabilistic_genotyping_research.md): Autosomal STR (24 Loci), Continuous MCMC Mixture Deconvolution (EuroForMix Gamma & STRmix Log-Normal), LTDNA Stochastic Dropout/Drop-in ($P(D), P(C), H_b$), Dirichlet PopGen $F_{st}$, Tippett ROC Calibration.
- [`pillar_2_lineage_kinship_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_2_lineage_kinship_research.md): Y-FILER Plus 27 Loci Clopper-Pearson 95% Bound, Argus X-12 Linkage & PHS Kinship, mtDNA EMPOP rCRS/RSRS Alignment, Interpol DVI Joint Likelihood, aDNA MapDamage Kinetics & Briggs Deamination.
- [`pillar_3_phenotype_ancestry_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_3_phenotype_ancestry_research.md): HIrisPlex-S 41-SNP Multinomial Logistic Regression & Softmax Sum-to-One Invariant, 55-SNP AIM Continental Centroid GIS Projection, 3D Craniofacial Morphology, Hair Texture & Balding PRS, MC1R Epistasis.
- [`pillar_4_epigenetics_aging_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_4_epigenetics_aging_research.md): Horvath / VISAGE Multi-Tissue Elastic Net Age Clock ($y_0=20.0$), tDMR 6-Tissue Origin QDA/NNLS Deconvolution, Lifestyle AHRR Pack-Years, Telomere $T/S$ Decay, Bisulfite QC & BMIQ Normalization.
- [`pillar_5_physical_evidence_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_5_physical_evidence_research.md): 3D Bloodstain Pattern Analysis (BPA) Area of Origin Least-Squares Optimization, SEM-EDX GSR Pb-Ba-Sb & CMC 3D Striations, Entomology Thermal Summation (ADD/ADH), MSI/ATR-FTIR HQI, Post-Mortem Toxicology PMR $C/P$ Ratios.
- [`pillar_6_lims_zkp_reporting_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_6_lims_zkp_reporting_research.md): Binary Merkle Tree Chain of Custody Ledger & $O(\log_2 N)$ Inclusion Proofs, Circom/Groth16 ZKP Blind Auditor (BN254 Pairings), ISO/IEC 17025:2017 GUM Expanded Uncertainty ($U_{95\%} = 2.00 \cdot u_c$), Dynamic ENFSI 2017 7-Tier Verbal Reporting Scale, 3D Spatial Juror Visualizer.

---

### 2. Implementation Execution Protocol
* **Zero Arbitrary Constants / No Approximations:** Use exact research constants (e.g., $N=1036, p_{\min}=0.00241$, $\beta_0=+2.50, \beta_1=-0.025$, $\lambda_C=0.020, \text{AT}=50.0\text{ RFU}, \lambda_h=0.015$, $\mu=10^{-3}, r=0.10$, Horvath $y_0=20.0$, $k=2.00$). Never invent heuristic formulas.
* **Complete Coverage:** Implement all mathematical formulations and edge cases without skipping steps.
* **Mandatory Unit Testing:** Every module must have corresponding `pytest` unit test classes and must pass all **Golden Benchmark Test Vectors** (`VECTOR_01` to `VECTOR_P6_03`).
* **Mathematical Invariants:** Enforce strict invariants across all calculations:
  - Additivity of log-likelihoods: $|\log_{10} LR - \sum \log_{10} LR_l| < 10^{-6}$
  - Probability simplex normalization: $|\sum P_i - 1.0| \le 10^{-6}$
  - Reciprocal balance and non-negativity across all physical and genetic parameters.
* **Legal & Verbal Reporting:** Translate numerical LRs into standardized 7-tier ENFSI (2017) statements in English and Turkish with active Prosecutor's Fallacy shields.
* **Pydantic v2 Namespaces:** When defining fields starting with `model_` on Pydantic `BaseModel` schemas, always configure `model_config = ConfigDict(protected_namespaces=())` to eliminate runtime warnings.

---

## 🎨 Master Rule 2: Frontend Design & Full Responsive Parity (Mobile & Desktop)

### 1. Cross-Device Responsiveness (Mobile-First & Ultra-Wide)
Every UI component, analysis panel, chart, data table, and modal **MUST be fully functional, aesthetically polished, and responsive across all viewports**:
* **Mobile (320px – 640px):** Single-column layouts (`grid-cols-1`), touch-friendly targets ($\ge 44\text{px}$ touch targets), no horizontal text cutoff (`min-w-0`, `truncate`, or `break-words`), scrollable tables with sticky headers.
* **Tablet (641px – 1024px):** Two-column balanced layouts (`sm:grid-cols-2`, `md:grid-cols-3`).
* **Desktop & Ultra-Wide (1025px – 4K):** Multi-column dashboard grids (`lg:grid-cols-2`, `xl:grid-cols-4`, `2xl:grid-cols-6`), expanded telemetry views, high-resolution SVG and 3D visualizers.

### 2. CSS Flexbox & Height Calculation Rules
* **No Collapsed Heights:** In Flexbox layouts where children use percentage heights (e.g. histogram bars `height: X%`), **always set `h-full` and `justify-end` on the immediate parent container** to prevent the browser from computing zero-height bars.
* **Aspect Ratios for SVG / 3D Canvas:** SVG and Three.js containers must have explicit responsive heights (e.g., `h-44 sm:h-52`) with `preserveAspectRatio="none"` or responsive camera viewports.

### 3. Tactical Visual Aesthetics & Micro-Interactions
* **Curated Dark Palette:** High-contrast tactical theme with subtle glowing borders (`border-tactical-border/60`), background glassmorphism (`bg-tactical-surface/50`), and vibrant accent colors (Emerald for inclusion/Hp, Rose/Red for exclusion/Hd, Purple for MCMC posteriors, Amber for thresholds/warnings).
* **Monospace Tabular Alignment:** All biometric figures, RFU values, base pairs, and LRs must use monospace typography with tabular figures (`font-mono tabular-nums`).
* **Interactive Dual-Mode (Touch + Mouse):** All hover tooltips, sliders, and chart points must seamlessly support both mouse hover and mobile tap gestures.
* **No Hollow / Fake Mock Buttons:** Buttons such as *"Execute MCMC Sampler"*, *"Run Analysis"*, or *"Synthesize Proof"* must never be idle mock timers. They must dispatch real API calls or execute mathematically faithful client-side simulations that update dynamic state, calculate true posterior statistics, and trigger smooth UI animations (%0–%100 progress bars).
