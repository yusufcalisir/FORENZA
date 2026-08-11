# PHASE 0.1 — Core Research Question & Scope

**Project:** FORENZA (Forensic Biology & DNA Intelligence Platform)  
**Author:** Yusuf Çalışır  
**Date:** August 2026  
**Status:** Active Academic Specification  

---

## 1. Primary Research Question

> **"How reliably can probabilistic inference model identity, kinship relationships, and physical phenotype traits from incomplete, low-template, or complex mixture forensic DNA profiles while rigorously quantifying uncertainty under population substructure constraints?"**

---

## 2. Problem Definition & Operational Context

Forensic DNA profiling remains the gold standard for human identification in legal proceedings. However, modern casework increasingly encounters complex DNA samples that deviate from pristine single-source profiles:

1. **Low-Template / Touch DNA:** Incomplete profiles exhibiting stochastic effects such as allele dropout (loss of an allele during PCR), drop-in (sporadic background contamination), and severe peak height imbalance.
2. **Complex DNA Mixtures:** Samples containing biological material from two or more individuals in varying proportion ratios, often with overlapping allele calls across core loci.
3. **Population Substructure & Linkage:** Deviations from Hardy-Weinberg Equilibrium (HWE) and Linkage Equilibrium (LE) caused by ancestral subpopulation structuring ($\theta$ / $F_{ST}$ correction).
4. **Legal Admissibility & Explainability:** The requirement for objective, statistically sound Likelihood Ratio (LR) metrics that comply with NRC II recommendations, SWGDAM guidelines, and the PCAST 2016 criteria for scientific validity in courtrooms.

---

## 3. Core Hypotheses

* **Hypothesis 1 (Statistical Reliability):** A continuous probabilistic genotyping engine integrating peak height distribution and locus-specific stutter models yields LR calculations that maintain calibration (Tippett plot slope) even in the presence of 50% allele dropout.
* **Hypothesis 2 (Kinship Resolution):** Applying the Balding-Nichols model with population-specific allele frequency arrays enables robust differentiation between true first-degree relatives and unrelated individuals across CODIS 20 core loci with false inclusion rates $< 10^{-6}$.
* **Hypothesis 3 (Explainable Evidence):** Natural language synthesis over structured Bayesian LR and posterior probability metrics provides court-admissible, non-overstating evidence summaries without altering the underlying mathematical results.

---

## 4. Methodological Scope & Boundaries

### In Scope
* CODIS 20 core STR loci + Amelogenin + Y-STR locus evaluation.
* Balding-Nichols $\theta$-correction (NRC II Recommendation 4.10b).
* Continuous & semi-continuous Likelihood Ratio ($LR$) calculation models.
* Probabilistic Kinship Index ($KI$) calculation (Parent-Child, Full-Sibling, Half-Sibling, Unrelated).
* Forensic DNA Phenotyping (FDP) using SNP-based multinomial logistic regression (IrisPlex / HIrisPlex models).
* Immutable audit trails and zero-knowledge cryptographic match proofs.

### Out of Scope (Explicit Exclusions)
* Replacement of certified human forensic examiners (FORENZA is an expert decision-support tool).
* Direct primary sequencing (NGS raw FASTQ alignment is assumed pre-processed into variant calls/allele tables).
* Non-human or species-identification genetics.

---

## 5. Success Criteria & Validation Targets

| Metric | Target Standard | Benchmark Source |
|---|---|---|
| Single-Source LR Accuracy | Identical to SWGDAM validation baselines | SWGDAM / NIST |
| Mixture Deconvolution Limit | 2-person & 3-person mixtures ($>1:10$ ratio) | EuroForMix / STRmix |
| False Inclusion Rate ($FIR$) | $< 10^{-6}$ across 10,000 simulated profiles | Empirical Simulation |
| Uncertainty Interval | 95% Markov Chain Monte Carlo (MCMC) HPD interval | Bayesian Inference |
| Legal Auditability | Full audit log chain of custody satisfying FRE 901/902 | Federal Rules of Evidence |

---

## 6. References & Standards Framework
- **NRC II (1996):** *The Evaluation of Forensic DNA Evidence*, National Research Council.
- **PCAST (2016):** *Forensic Science in Criminal Courts: Ensuring Scientific Validity of Feature-Comparison Methods*, Executive Office of the President.
- **SWGDAM (2020):** *Interpretation Guidelines for Autosomal STR Typing by Forensic DNA Laboratories*.
- **OSAC (2023):** *Standards for Forensic DNA Analysis and Interpretation*.
