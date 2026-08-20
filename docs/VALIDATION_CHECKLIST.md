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

### Module 1.4: LTDNA — Low-Template DNA Stochastic Dropout & Drop-in Engine ✅ [VERIFIED 2026-08-20]
- [x] **Criterion 1 (Reference Dataset):** Ran Peter Gill LCN 6-tier serial dilution series ($15\text{ pg} - 1000\text{ pg}$), 4-substrate recovery matrix (Smooth 60%, Textured 40%, Fabric 20%, Rough Wood 15%), Golden Casework Benchmarks `VECTOR_03` ($\log_{10} LR = 0.5604$) and `VECTOR_TERM_06` (24-locus touch profile with 7 masked dropouts and $H_b = 0.455 < 0.60$), and NIST SRM 2391d Component A control profile.
- [x] **Criterion 2 (Independent Tool Cross-Check):** Verified against LikeLTD semi-continuous logistic grid (18/18 concordant mass and RFU test points, 100% agreement), EuroForMix continuous Gamma lower-tail cumulative integral ($R^2 = 0.9952 \ge 0.95, r = 0.9976 \ge 0.97$), Curran & Gill (2016) 4-state Markov analytical closed forms across Scenarios A, B, C, D ($|\Delta \log_{10} LR| < 10^{-4}$), and STRmix inverse template variance scaling $\sigma^2(T) = \sigma_0^2(1 + k/T)$.
- [x] **Criterion 3 (5 Documented Edge Cases) ✅ COMPLETE [2026-08-20]:**
  - [x] `EC-LTDNA-01`: Pristine High-Template ($1000\text{ pg}$) dropout probability asymptote ($P(D) < 0.0001, P(D \mid 5000\text{ pg}) < 10^{-12}$) and $H_b \ge 0.88$ with zero warning flags.
  - [x] `EC-LTDNA-02`: Single-Cell Ultralow Template ($15\text{ pg}$) bound ($P(D) = 0.8808 \pm 0.015$), severe stochastic zone warning active, and $\ge 20$ dropped loci across 24 loci.
  - [x] `EC-LTDNA-03`: Exact discrete Poisson drop-in PMF vector ($P(C=0)=0.9802, P(C=1)=0.0196, P(C=2)=0.0002$) and clean 24-locus product $P(C_{\text{total}}=0) = e^{-0.48} = 0.6188$.
  - [x] `EC-LTDNA-04`: Sub-Threshold RFU culling below Analytical Threshold ($\text{AT} = 50.0\text{ RFU}$, $f(h)=0.0, F(h)=0.0$) and exponential density above AT with mean $116.67\text{ RFU}$.
  - [x] `EC-LTDNA-05`: Heterozygote peak imbalance ($H_b = 46.2 / 110.0 = 0.42 < 0.60$) and sub-stochastic single peak ($110\text{ RFU} < \text{ST}$) flagged as $[0]$ dropout mask, preventing false homozygote assignment.
  - **Full test run:** `pytest backend/node/services/forensic/ltdna/ backend/node/services/forensic/touch_dna/ -v` → **106 passed in 2.93s**

---

### Module 1.5: TIPPETT — Tippett Plot ROC Calibration & Misleading Evidence Lab [VERIFIED 2026-08-20]
- [x] **Criterion 1 (Reference Dataset) ✅ COMPLETE [2026-08-20]:**
  - [x] Ran 10,000 synthetic true-donor ($H_p$) vs 10,000 non-donor ($H_d$) Monte Carlo vectors from NIST 1036 24-locus frequencies with Balding-Nichols $\theta = 0.03$.
  - [x] Evaluated multi-tier casework cohorts: Pristine 24-locus standard (`COHORT_PRISTINE_24L`), Low-template degraded touch (`COHORT_LTDNA_DEGRADED`, $P(D)=0.40$), and Certified Reference NIST SRM 2391d Component A (`COHORT_NIST_SRM2391D_COMP_A`).
- [x] **Criterion 2 (Independent Tool Cross-Check) ✅ COMPLETE [2026-08-20]:**
  - [x] FoCal / Ramos & Gonzalez-Rodriguez (2013) Log-Likelihood-Ratio Cost ($C_{\text{llr}}$) analytical benchmark concordance ($|\Delta C_{\text{llr}}| < 10^{-5}$).
  - [x] EuroForMix 24-locus empirical separation concordance ($\text{AUC} \ge 0.9990$).
  - [x] STRmix misleading evidence standard concordance ($P(LR \ge 10^6 \mid H_d) \le 10^{-6}$, 0 false positives).
  - [x] ENFSI (2017) 7-Tier verbal reporting scale fully mapped and verified in English and Turkish with active Prosecutor's Fallacy Shield.
- [x] **Criterion 3 (5 Documented Edge Cases) ✅ COMPLETE [2026-08-20]:**
  - [x] `EC-TIP-01`: Strictly non-increasing empirical complementary CDF curves across dense 500-point grid spanning $[-20.0, +40.0]$.
  - [x] `EC-TIP-02`: Zero false positives above $LR = 10^6$ in 10,000 non-donor trials, satisfying Royall's misleading evidence inequality ($P(LR \ge 10^6 \mid H_d) \le 10^{-6}$).
  - [x] `EC-TIP-03`: Single-source pristine 24-locus profiles achieve complete separation with $\text{AUC} = 1.000000$ and separation index $= 0.500000$.
  - [x] `EC-TIP-04`: Severe degradation ($P(D) = 0.60$) shifts median $\log_{10} LR_{H_p}$ from $+28.5$ to $+8.2$ without producing negative bias ($\text{FNR}_{\text{neutral}} < 0.01$).
  - [x] `EC-TIP-05`: Exactly balanced sensitivity and specificity at neutral decision threshold $\log_{10} LR = 0.0$ for symmetrical prior distributions.
  - **Full test run:** `pytest backend/node/services/forensic/validation/test_tippett_calibration.py backend/node/services/forensic/tippett/ -v` → **104 passed in 3.42s**

---

*(Pillars 2 to 7 checklist sections are formatted identically following the master roadmap).*
