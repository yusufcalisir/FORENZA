# FORENZA Agent Operating Guidelines & Mandatory Research Rules

This repository contains the **FORENZA: Forensic Evidence Operating System**. All AI agents, subagents, and automated systems operating on this repository must strictly adhere to the rules outlined below.

---

## 🔒 Master Rule: Absolute Research Fidelity & Mathematical Integrity

### 1. Source of Truth
Every implementation across all 30 biocomputational modules **MUST derive exclusively and verbatim from the 6 research specifications** in the `research/` directory:
- [`pillar_1_probabilistic_genotyping_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_1_probabilistic_genotyping_research.md): Autosomal STR (24 Loci), Continuous MCMC Mixture Deconvolution (EuroForMix Gamma & STRmix Log-Normal), LTDNA Stochastic Dropout/Drop-in, Dirichlet PopGen $F_{st}$, Tippett ROC Calibration.
- [`pillar_2_lineage_kinship_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_2_lineage_kinship_research.md): Y-FILER Plus 27 Loci Clopper-Pearson 95% Bound, Argus X-12 Linkage & PHS Kinship, mtDNA EMPOP rCRS/RSRS Alignment, Interpol DVI Joint Likelihood, aDNA MapDamage Kinetics.
- [`pillar_3_phenotype_ancestry_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_3_phenotype_ancestry_research.md): HIrisPlex-S 41-SNP Multinomial Logistic Regression & Softmax Sum-to-One Invariant, 55-SNP AIM Continental Centroid GIS Projection, 3D Craniofacial Morphology, Hair Texture & Balding PRS, MC1R Epistasis.
- [`pillar_4_epigenetics_aging_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_4_epigenetics_aging_research.md): Horvath / VISAGE Multi-Tissue Elastic Net Age Clock ($y_0=20.0$), tDMR 6-Tissue Origin QDA/NNLS Deconvolution, Lifestyle AHRR Pack-Years, Telomere $T/S$ Decay, Bisulfite QC & BMIQ Normalization.
- [`pillar_5_physical_evidence_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_5_physical_evidence_research.md): 3D Bloodstain Pattern Analysis (BPA) Area of Origin Least-Squares Optimization, SEM-EDX GSR Pb-Ba-Sb & CMC 3D Striations, Entomology Thermal Summation (ADD/ADH), MSI/ATR-FTIR HQI, Post-Mortem Toxicology PMR $C/P$ Ratios.
- [`pillar_6_lims_zkp_reporting_research.md`](file:///c:/Users/Yusuf/str-analysis/research/pillar_6_lims_zkp_reporting_research.md): Binary Merkle Tree Chain of Custody Ledger & $O(\log_2 N)$ Inclusion Proofs, Circom/Groth16 ZKP Blind Auditor (BN254 Pairings), ISO/IEC 17025:2017 GUM Expanded Uncertainty ($U_{95\%} = 2.00 \cdot u_c$), Dynamic ENFSI 2017 7-Tier Verbal Reporting Scale, 3D Spatial Juror Visualizer.

---

### 2. Implementation Execution Protocol
* **No Approximations:** Use exact constants (e.g., $N=1036, p_{\min}=0.00241$, $\mu=10^{-3}, r=0.10$, Horvath $y_0=20.0$, $k=2.00$).
* **Complete Coverage:** Implement all subheadings and mathematical formulations without skipping any topic or edge case.
* **Mandatory Unit Testing:** Every module must have corresponding `pytest` unit test classes and must pass all **Golden Benchmark Test Vectors** (`VECTOR_01` to `VECTOR_P6_03`).
* **Product Rule & Invariants:** Verify mathematical invariants (such as $|\log_{10} LR - \sum \log_{10} LR_l| < 10^{-6}$ and $|\sum P - 1.0| \le 10^{-6}$).
* **Legal & Verbal Reporting:** Translate numerical LRs into standardized 7-tier ENFSI (2017) statements in English and Turkish with active Prosecutor's Fallacy shields.
