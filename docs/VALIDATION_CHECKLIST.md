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

### Module 1.2: MCMC-MH — Continuous Metropolis-Hastings Mixture Deconvoluter ✅ [VERIFIED 2026-08-20]
- [x] **Criterion 1 (Reference Dataset):** Zenodo BTSC 349/268 calibrated genotype profiles (DONOR_A = NIST SRM 2391d Comp A 9947A, DONOR_B = NIST SRM 2391d Comp B 9948) at true weight ratios 1:1, 3:1, 9:1, 19:1 and PROVEDIt 1:3 experimental degraded mixture.
- [x] **Criterion 2 (Independent Tool Cross-Check):** STRmix Log-Normal (σ=0.35) and EuroForMix Gamma likelihood engines both implemented and producing concordant log-likelihoods; Gelman-Rubin R̂ metric concordant with published SWGDAM 2020 convergence standard.
- [x] **Criterion 3 (5 Documented Edge Cases) ✅ COMPLETE [2026-08-20]:**
  - [x] `EC-MCMC-01`: 4-chain Gelman-Rubin convergence R̂ ≤ 1.10 (SWGDAM 2020 floor); overdispersed chains reach consensus. `test_4_chain_gelman_rubin_below_swgdam_threshold` + `test_overdispersed_initializations_reach_consensus` PASSED.
  - [x] `EC-MCMC-02`: Extreme contributor imbalance (1:19, 5% minor) — major weight ≥ 0.88 recovered without allele swapping; structural non-collapse verified. `test_btsc_19_1_major_minor_separation` + `test_no_allele_swapping_under_severe_imbalance` PASSED.
  - [x] `EC-MCMC-03`: Equal 1:1 mixture — STRmix LL([0.5,0.5]) > LL([0.9,0.1]) by > 1.0 nats (MLE symmetry invariant). `test_btsc_1_1_symmetric_posterior_weights` PASSED. Dirichlet mean = 0.50 ± 0.03. `test_symmetric_dirichlet_prior_invariance` PASSED.
  - [x] `EC-MCMC-04`: Back-stutter at allele b−1 present in expected_peak_heights dict with amplitude SR_l × parent_height (±0.001 rel); LL(modeled) > LL(unmodeled). `test_back_stutter_peak_present_in_expected_dict` + `test_stutter_log_likelihood_dominance` PASSED.
  - [x] `EC-MCMC-05`: Adaptive MH acceptance rate in [0.10, 0.55] after n_burn=4000; Dirichlet asymmetry correction |Δ| < 10.0 (well-conditioned). `test_adaptive_mcmc_acceptance_rate_within_band` + `test_dirichlet_proposal_asymmetry_correction_invariance` PASSED.
  - **Full test run:** `pytest backend/node/services/forensic/probabilistic/test_mcmc_edge_cases.py -v` → **10 passed in 157.40s**

---

### Module 1.3: NRC-II — Dirichlet $F_{st}$ / Balding-Nichols Subpopulation Corrections ✅ [VERIFIED 2026-08-20]
- [x] **Criterion 1 (Reference Dataset):** Ran NIST 1036 4-population stratified dataset ($N_{\text{Caucasian}}=361, N_{\text{AfricanAmerican}}=342, N_{\text{Hispanic}}=236, N_{\text{Asian}}=97$, Total $N=1036$), 1000 Genomes Phase 3 (5 superpopulations), and standard reference individuals NIST SRM 2391d Components A/B/C and GIAB NA12878.
- [x] **Criterion 2 (Independent Tool Cross-Check):** Verified against NRC II (1996) Recommendation 4.4 analytical tables (Chapter 4, Tables 4.1 & 4.2 grid across all frequencies and $\theta \in [0.00, 0.05]$ with $|\Delta| < 10^{-7}$), Curran & Buckleton (2007) multi-locus weighted ANOVA $\bar{\theta}$ estimator, and Familias 3 / EuroForMix PopGen coancestry models.
- [x] **Criterion 3 (5 Documented Edge Cases) ✅ COMPLETE [2026-08-20]:**
  - [x] `EC-NRC-01`: Zero $\theta$ boundary ($HWE$) exact reduction: $\lim_{\theta \to 0} P(E \mid S, \theta) = p_i^2, 2p_i p_j$ with $|\Delta| < 10^{-12}$.
  - [x] `EC-NRC-02`: High inbreeding stress $\theta=0.1500$ numerical stability without underflow, negative probabilities, or simplex distortion.
  - [x] `EC-NRC-03`: Complete probability simplex normalization ($\sum_{i \le j} P(A_i A_j \mid \theta) = 1.00000000 \pm 10^{-6}$) verified across > 700 diploid genotypes on all 24 loci.
  - [x] `EC-NRC-04`: Subpopulation demographic stratification cross-comparison ratio ($|\Delta \log_{10} LR| > 0.5$) for NIST SRM 2391d Component B across demographic databases.
  - [x] `EC-NRC-05`: Reciprocal hypothesis balance invariant ($LR(H_p/H_d) \times LR(H_d/H_p) = 1.0000000 \pm 10^{-6}$) and exact log-space multi-locus additivity.
  - **Full test run:** `pytest backend/node/services/forensic/population/test_nrc_*.py backend/node/services/forensic/kinship/test_nrc.py -v` → **47 passed in 6.41s**

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
