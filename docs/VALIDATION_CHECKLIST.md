# FORENZA — Validation Checklist & Audit Template

This document provides the mandatory 3-item checklist and 5-edge-case audit log for every module. A module status in `docs/VALIDATION_STATUS.md` is only changed to `VERIFIED` when all checkboxes for that module are checked `[x]`.

---

## Pillar 1: Probabilistic Genotyping & Population Genetics

### Module 1.1: STR-24 — Autosomal STR & Kinship Engine
- [x] **Criterion 1 (Reference Dataset):** Ran NIST SRM 2391d (Components A–E), Promega PowerPlex Fusion 24, and QIAGEN Verogen ForenSeq MainstAY; verified genotype calls & peak heights.
- [x] **Criterion 2 (Independent Tool Cross-Check):** Concordance verified with NIST 1036 PopGen frequency calculation table, FragalyseQt CE fragment sizing, and GeneMarker HID hybrid filters.
- [x] **Criterion 3 (5 Documented Edge Cases):**
  - [x] `EC-STR-01`: Rare/Unseen allele minimum frequency floor ($p_{\min} = 0.00241$).
  - [x] `EC-STR-02`: Homozygote Balding-Nichols $\theta$ scaling invariance across $\theta \in [0.00, 0.05]$.
  - [x] `EC-STR-03`: Tri-allelic pattern (Type 1 duplication / Type 2 mosaicism) graceful handling.
  - [x] `EC-STR-04`: Microvariant decimal repeat parsing (`TH01 9.3`, `SE33 25.2`, `D1S1656 17.3`, `D21S11 31.2`).
  - [x] `EC-STR-05`: Additivity & Multiplicative Invariant ($\log_{10} LR_{\text{total}} = \sum \log_{10} LR_l, LR_{\text{total}} = \prod LR_l, LR(H_p/H_d) = 1/LR(H_d/H_p)$).

---

### Module 1.2: MCMC-MH — Continuous Metropolis-Hastings Mixture Deconvoluter
- [ ] **Criterion 1 (Reference Dataset):** Ran PROVEDIt 2-person and 3-person experimental mixture series (300 pg, 100 pg, 1:3, 1:9 ratios).
- [ ] **Criterion 2 (Independent Tool Cross-Check):** Concordance verified against EuroForMix (Gamma model) and STRmix published benchmarks.
- [ ] **Criterion 3 (5 Documented Edge Cases):**
  - [ ] `EC-MCMC-01`: Gelman-Rubin convergence $\hat{R} < 1.05$ across 4 parallel MCMC chains.
  - [ ] `EC-MCMC-02`: Extreme contributor imbalance ($1:19$, $5\%$ minor donor) deconvolution stability.
  - [ ] `EC-MCMC-03`: Equal 1:1 mixture posterior symmetry invariant under unconstrained priors.
  - [ ] `EC-MCMC-04`: Forward ($N+1$) and reverse ($N-1$) stutter filter threshold enforcement ($SR < 0.15$).
  - [ ] `EC-MCMC-05`: Metropolis-Hastings proposal acceptance rate bounded in $[0.20, 0.45]$.

---

### Module 1.3: NRC-II — Dirichlet $F_{st}$ / Balding-Nichols Subpopulation Corrections
- [ ] **Criterion 1 (Reference Dataset):** Ran NIST 1036 4-population stratified dataset.
- [ ] **Criterion 2 (Independent Tool Cross-Check):** Verified against NRC II (1996) Recommendation 4.4 equations and Curran & Buckleton empirical tables.
- [ ] **Criterion 3 (5 Documented Edge Cases):**
  - [ ] `EC-NRC-01`: Zero $\theta$ boundary ($HWE$) identity verification.
  - [ ] `EC-NRC-02`: High inbreeding coefficient $\theta=0.10$ numerical stability.
  - [ ] `EC-NRC-03`: Complete probability simplex normalization ($\sum P_i = 1.000000 \pm 10^{-6}$).
  - [ ] `EC-NRC-04`: Uncharacterized rare allele dynamic frequency assignment.
  - [ ] `EC-NRC-05`: Reciprocal LR balance ($LR_{Hp/Hd} \cdot LR_{Hd/Hp} = 1.0$).

---

### Module 1.4: LTDNA — Low-Template DNA Stochastic Dropout & Drop-in Engine
- [ ] **Criterion 1 (Reference Dataset):** Ran Peter Gill LTDNA 15 pg to 100 pg single-cell sensitivity series.
- [ ] **Criterion 2 (Independent Tool Cross-Check):** Verified against LikeLTD logistic model ($\beta_0=+2.50, \beta_1=-0.025$).
- [ ] **Criterion 3 (5 Documented Edge Cases):**
  - [ ] `EC-LTDNA-01`: High template mass ($1000\text{ pg}$) dropout probability asymptote ($P(D) \to 0.0$).
  - [ ] `EC-LTDNA-02`: Single-cell ultralow template ($15\text{ pg}$) dropout bound ($P(D) \ge 0.88$).
  - [ ] `EC-LTDNA-03`: Poisson drop-in count rate ($\lambda_C = 0.020$) across $k \in \{0, 1, 2, 3\}$.
  - [ ] `EC-LTDNA-04`: Exponential drop-in peak height PDF non-negativity ($h_C \ge \text{AT}$).
  - [ ] `EC-LTDNA-05`: Heterozygote balance stochastic zone detection ($H_b < 0.60$).

---

### Module 1.5: TIPPETT — Tippett Plot ROC Calibration & Misleading Evidence Lab
- [ ] **Criterion 1 (Reference Dataset):** Ran 10,000 synthetic true-donor ($H_p$) vs 10,000 non-donor ($H_d$) Monte Carlo vectors.
- [ ] **Criterion 2 (Independent Tool Cross-Check):** Verified against ENFSI (2017) Evaluative Reporting calibration criteria.
- [ ] **Criterion 3 (5 Documented Edge Cases):**
  - [ ] `EC-TIP-01`: Monotonic decreasing empirical CDF curves for $H_p$ and $H_d$.
  - [ ] `EC-TIP-02`: Rate of misleading evidence bound ($P(LR > 10^6 | H_d) \le 10^{-6}$).
  - [ ] `EC-TIP-03`: Separation area under curve $\text{AUC} \ge 0.999$ on single-source profiles.
  - [ ] `EC-TIP-04`: Degraded template leftward curve shift under simulated dropout.
  - [ ] `EC-TIP-05`: Neutral LR threshold calibration at $\log_{10} LR = 0.0$.

---

*(Pillars 2 to 7 checklist sections are formatted identically following the master roadmap).*
