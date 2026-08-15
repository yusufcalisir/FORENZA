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
* CODIS 20 core STR loci + European Standard Set (ESS SE33) + Penta D + Penta E + Amelogenin (24 Autosomal STR Multiplex) + Y-STR & X-STR locus evaluation.
* Balding-Nichols $\theta$-correction (NRC II Recommendation 4.10b) with subpopulation $F_{st} = 0.01 / 0.03$.
* Continuous & semi-continuous Likelihood Ratio ($LR$) calculation models with MCMC deconvolution.
* Probabilistic Kinship Index ($KI$) calculation (Parent-Child, Full-Sibling, Half-Sibling, Avuncular, Unrelated).
* Forensic DNA Phenotyping (FDP) using Walsh et al. (2018) HIrisPlex-S 24-SNP multinomial logistic regression with strict sum-to-unity distribution integrity validation.
* 55-SNP AIM Biogeographic Ancestry (BGA) with live GIS geospatial mapping.
* Horvath 5-CpG DNA Methylation Epigenetic Age Clock with $\pm 2.8$ year mean absolute error.
* ISO/IEC 17025:2017 and ENFSI 2017 / SWGDAM 2020 aligned automated evaluative report compilation.
* Immutable audit trails with HMAC-SHA256 hash chaining and Circom Groth16 zero-knowledge match proofs.

### Out of Scope (Explicit Exclusions)
* Replacement of certified human forensic examiners (FORENZA is an expert decision-support operating system).
* Direct primary wet-lab sequencing (NGS raw FASTQ alignment is assumed pre-processed into variant calls/allele tables).
* Non-human or species-identification genetics.

---

## 5. Success Criteria & Validation Targets

| Metric | Target Standard | Benchmark Source |
|---|---|---|
| Single-Source LR Accuracy | Identical to SWGDAM validation baselines | SWGDAM / NIST |
| Mixture Deconvolution Limit | 2-person, 3-person & 4-person mixtures ($>1:10$ ratio) | EuroForMix / STRmix |
| False Inclusion Rate ($FIR$) | $< 10^{-6}$ across 10,000 simulated profiles | Empirical Simulation |
| Uncertainty Interval | 95% Markov Chain Monte Carlo (MCMC) HPD interval | Bayesian Inference |
| Phenotype Distribution Integrity | Normalization error $\epsilon \le 1.0\%$ across all categories | Walsh et al. (2018) |
| Legal Auditability & Chain of Custody | Full audit log chain of custody satisfying FRE 901/902 & ISO 17025 | Federal Rules of Evidence |

---

## 6. References & Standards Framework
- **NRC II (1996):** *The Evaluation of Forensic DNA Evidence*, National Research Council.
- **PCAST (2016):** *Forensic Science in Criminal Courts: Ensuring Scientific Validity of Feature-Comparison Methods*, Executive Office of the President.
- **SWGDAM (2020):** *Interpretation Guidelines for Autosomal STR Typing by Forensic DNA Laboratories*.
- **ENFSI (2017):** *Guideline for Evaluative Reporting in Forensic Science*, European Network of Forensic Science Institutes.
- **ISO/IEC 17025 (2017):** *General requirements for the competence of testing and calibration laboratories*.
- **OSAC (2023):** *Standards for Forensic DNA Analysis and Interpretation*.
- **Walsh et al. (2018):** *The HIrisPlex-S system for simultaneous prediction of hair, eye and skin colour from DNA*, FSI: Genetics.
