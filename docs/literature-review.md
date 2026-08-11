# PHASE 0.2 — Academic Literature Review

**Project:** FORENZA (Forensic Biology & DNA Intelligence Platform)  
**Author:** Yusuf Çalışır  
**Date:** August 2026  
**Status:** Comprehensive Survey & State of the Art  

---

## Executive Overview

This document provides a systematic review of foundational literature, statistical guidelines, and court-validated frameworks in forensic genetics, probabilistic genotyping, kinship inference, and forensic DNA phenotyping (FDP). The review establishes the theoretical underpinnings for the **FORENZA** core computational engine.

---

## 1. Forensic Short Tandem Repeat (STR) Analysis

### 1.1 Biological Mechanism & CODIS Panel
Short Tandem Repeats (STRs) consist of repetitive DNA sequences (typically 2–6 base pairs in length) located at specific polymorphic loci across the human genome. The Federal Bureau of Investigation (FBI) expanded the core Combined DNA Index System (CODIS) from 13 to **20 core loci** in 2017 to enhance discrimination power and reduce accidental matching probabilities in international database searches:
* **Core Loci:** CSF1PO, FGA, TH01, TPOX, vWA, D3S1358, D5S818, D7S820, D8S1179, D13S317, D16S539, D18S51, D21S11, D1S1656, D2S1338, D10S1248, D12S391, D19S433, D22S1045, and Amelogenin (sex determination).

### 1.2 Polymerase Chain Reaction (PCR) Artifacts
Capillary electrophoresis (CE) electropherograms (EPGs) display peak heights measured in Relative Fluorescence Units (RFUs). Real-world forensic EPG interpretation is complicated by three main biological/technical artifacts:
* **Stutter:** Minor peaks typically one repeat unit shorter ($n-1$) or longer ($n+1$) than the main allele peak, caused by strand slippage during PCR amplification.
* **Allele Dropout ($D$):** Failure of an allele to amplify above the analytical threshold (AT), prevalent in low-template DNA ($< 100\text{ pg}$).
* **Drop-in ($C$):** Appearance of isolated, low-level non-replicate peak artifacts stemming from trace background contamination or PCR noise.

---

## 2. Statistical Framework: Likelihood Ratios (LR)

### 2.1 The Bayesian LR Principle
The evaluation of forensic DNA evidence ($E$) under two mutually exclusive hypotheses—Prosecution Hypothesis ($H_p$) and Defense Hypothesis ($H_d$)—is expressed via Bayes' Theorem in odds form:

$$\frac{P(H_p \mid E)}{P(H_d \mid E)} = \frac{P(E \mid H_p)}{P(E \mid H_d)} \times \frac{P(H_p)}{P(H_d)}$$

Where the ratio of conditional probabilities constitutes the **Likelihood Ratio (LR)**:

$$LR = \frac{P(E \mid H_p)}{P(E \mid H_d)}$$

* **$LR > 1$:** Evidence supports the prosecution hypothesis ($H_p$).
* **$LR = 1$:** Neutral evidence; no statistical weight.
* **$LR < 1$:** Evidence supports the defense hypothesis ($H_d$).

### 2.2 Key References
* **Evett & Weir (1998):** *Interpreting DNA Evidence: Statistical Genetics for Forensic Scientists*. Established standard LR formulations across autosomal marker sets.
* **Gill et al. (2006):** ISFG recommendations on the interpretation of complex DNA profiles, establishing guidelines for semi-continuous and continuous models.

---

## 3. Probabilistic Genotyping Systems (PGS)

### 3.1 Semi-Continuous vs. Continuous Models
* **Semi-Continuous Models (e.g., Lab Retriever, LikeLTD):** Utilize allele presence/absence calls and model probability of dropout ($P(D)$) and drop-in ($P(C)$), but ignore peak height intensities.
* **Continuous Models (e.g., STRmix, TrueAllele, EuroForMix):** Fully model quantitative EPG peak height signals, stutter ratios, mass fraction ratios ($\text{Mx}$), degradation slopes, and thermal noise using Markov Chain Monte Carlo (MCMC) sampling.

### 3.2 Key References
* **Perlin et al. (2011):** *Validating TrueAllele DNA Mixture Interpretation*. Demonstrated automated Bayesian deconvolution of 2-person and 3-person mixtures.
* **Taylor, Bright, & Buckleton (2013):** *The interpretation of complex DNA profiles using empirical continuous models*. Laid the mathematical groundwork for MCMC peak-height mixture interpretation.

---

## 4. Kinship & Pedigree Indexing

### 4.1 Kinship Index ($KI$) Formulation
Kinship analysis calculates the weight of evidence supporting a specific biological relationship versus unrelated individuals:

$$KI = \frac{P(E \mid H_{\text{related}})}{P(E \mid H_{\text{unrelated}})}$$

Common relationship hypotheses evaluated over CODIS profiles:
* **Parent-Child ($PC$):** Requires sharing at least one obligatory allele per locus (barring mutation).
* **Full-Siblings ($FS$):** Evaluates sharing of 0, 1, or 2 alleles IBD (Identical By Descent) with probabilities $k_0 = 0.25, k_1 = 0.50, k_2 = 0.25$.
* **Half-Siblings / Avuncular ($HS$):** Evaluates IBD probabilities $k_0 = 0.50, k_1 = 0.50, k_2 = 0$.

### 4.2 Population Substructure Correction ($\theta$)
To prevent overestimating LR/KI values due to shared ancestral subpopulation alleles, the **Balding-Nichols (1995)** model and **NRC II (1996) Recommendation 4.10b** apply the coancestry coefficient $\theta$ (typically set to $0.01 - 0.03$):

$$P(A_i A_i \mid A_i) = \theta + (1 - \theta) p_i$$

---

## 5. Forensic DNA Phenotyping (FDP) & Geo-Ancestry

### 5.1 FDP Panels
Forensic DNA Phenotyping predicts physical appearance traits from single nucleotide polymorphisms (SNPs):
* **IrisPlex (Walsh et al., 2011):** 6 SNP markers predicting blue and brown eye color with ROC AUC $> 0.94$.
* **HIrisPlex-S (Walsh et al., 2018):** 41 SNP panel predicting eye color, hair color (blonde, brown, red, black), and skin pigmentation (5 categories) simultaneously.

### 5.2 Biogeographic Ancestry (BGA)
BGA estimation utilizes Ancestry Informative Markers (AIMs) or high-density SNP matrices mapped against reference populations (1000 Genomes Project, HGDP) using principal component analysis (PCA) and Dirichlet-multinomial distribution models.

---

## 6. Judicial Validation & Legal Standards

### 6.1 The PCAST Report (2016)
The President's Council of Advisors on Science and Technology (PCAST) evaluated forensic feature-comparison methods and highlighted critical requirements for DNA mixture analysis:
1. **Foundational Validity:** Demonstrated empirical accuracy, sensitivity, and false-positive rates over simulated and real casework samples.
2. **Validity as Applied:** Rigorous quality assurance, objective software algorithms, and transparent reporting of uncertainty intervals.

### 6.2 SWGDAM & OSAC Guidelines
* **SWGDAM (2020):** Mandates internal validation of probabilistic genotyping software across minimum sample sizes, mixture ratios, and degradation levels.
* **OSAC (2023):** Defines standards for reporting likelihood ratios, requiring clear statements of assumptions, proposition pairs, and population database choices.

---

## 7. Implications for FORENZA Engine Architecture

Based on this review, the FORENZA platform will adhere to the following principles:
1. **Continuous LR Engine:** Implement probabilistic genotyping using quantitative peak-height modeling and MCMC sampling.
2. **Balding-Nichols Integration:** Apply NRC II $\theta$-correction dynamically across all kinship and match calculations.
3. **Transparent Uncertainty:** Report LR values alongside 95% Bayesian highest posterior density (HPD) intervals and explicit assumption logs.
4. **Court-Admissible AI Summaries:** Enforce a strict boundary where LLM modules only explain and format calculated results without performing statistical inference.
