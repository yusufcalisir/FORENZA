# PHASE 0.3 — Formal Mathematical Specification

**Project:** FORENZA (Forensic Biology & DNA Intelligence Platform)  
**Author:** Yusuf Çalışır  
**Date:** August 2026  
**Status:** Mathematical & Statistical Formalization  

---

## 1. Likelihood Ratio ($LR$) Formalism

Let $E$ represent the observed forensic DNA evidence (allele calls or capillary electropherogram peak heights across $L$ loci). Let $H_p$ be the prosecution hypothesis and $H_d$ be the defense hypothesis.

The total Likelihood Ratio across $L$ independent loci is the product of locus-specific LRs:

$$LR = \frac{P(E \mid H_p)}{P(E \mid H_d)} = \prod_{l=1}^{L} LR_l = \prod_{l=1}^{L} \frac{P(E_l \mid H_p)}{P(E_l \mid H_d)}$$

---

## 2. Single-Source Genotype Probabilities & Substructure ($\theta$)

### 2.1 Hardy-Weinberg Genotype Probabilities ($\theta = 0$)
For a locus with allele $A_i$ of frequency $p_i$ and allele $A_j$ of frequency $p_j$:

$$P(A_i A_i) = p_i^2$$

$$P(A_i A_j) = 2 p_i p_j \quad (i \neq j)$$

### 2.2 Balding-Nichols $\theta$-Correction (NRC II Recommendation 4.10b)
To account for population substructure with coancestry coefficient $\theta \in [0.01, 0.03, 0.05]$, the 4 matching configurations are:

#### 1. Homozygous Match ($A_i A_i \mid A_i A_i$):
$$P(A_i A_i \mid A_i A_i, \theta) = \frac{\left[2\theta + (1-\theta)p_i\right] \left[3\theta + (1-\theta)p_i\right]}{(1+\theta)(1+2\theta)}$$

#### 2. Heterozygous Match ($A_i A_j \mid A_i A_j, i \neq j$):
$$P(A_i A_j \mid A_i A_j, \theta) = \frac{2 \left[\theta + (1-\theta)p_i\right] \left[\theta + (1-\theta)p_j\right]}{(1+\theta)(1+2\theta)}$$

#### 3. Partial Match with Single Shared Allele ($A_i A_j \mid A_i A_k, j \neq k$):
$$P(A_i A_j \mid A_i A_k, \theta) = \frac{\left[\theta + (1-\theta)p_i\right] \left[(1-\theta)p_j\right]}{(1+\theta)(1+2\theta)}$$

#### 4. Zero Shared Alleles ($A_i A_j \mid A_k A_l, i,j,k,l \text{ distinct}$):
$$P(A_i A_j \mid A_k A_l, \theta) = \frac{2 \left[(1-\theta)p_i\right] \left[(1-\theta)p_j\right]}{(1+\theta)(1+2\theta)}$$

### 2.3 NRC II Rule 4.1 Minimum Allele Frequency Bound ($p_{\min}$)
To prevent zero-division singularities, minimum frequency floor is strictly enforced:

$$p_{\min} = \max\left(\frac{5}{2N}, 0.001\right) \approx 0.00241 \quad (N = 1036 \text{ individuals in NIST 1036})$$

---

## 3. Kinship Index ($KI$) Formulations & Stepwise Mutation Model (SMM)

### 3.1 General Identity-by-Descent (IBD) Formulation
$$\text{KI} = \frac{k_2 P(G_C, G_A \mid \text{IBD}=2) + k_1 P(G_C, G_A \mid \text{IBD}=1) + k_0 P(G_C, G_A \mid \text{IBD}=0)}{P(G_C \mid \theta) \cdot P(G_A \mid \theta)}$$

### 3.2 Stepwise Mutation Model (SMM) for Germline Discrepancies
For repeat lengths $m$ and $n$ with locus mutation rate $\mu \approx 10^{-3}$ and geometric parameter $r = 0.10$:

$$P(m \to n) = \begin{cases} 1 - \mu & \text{if } m = n \\ \frac{\mu}{2} (1-r) r^{|m-n|-1} & \text{if } m \neq n \end{cases}$$

Let $G_m$ be the mother's genotype, $G_c$ be the child's genotype, and $G_f$ be the alleged father's genotype.

### 3.1 Parent-Child Trio Index ($KI_{PC}$)

$$KI_{PC} = \frac{P(G_c \mid G_m, G_f)}{P(G_c \mid G_m, \text{Unrelated})}$$

Assuming alleles $G_m = \{A_i, A_j\}$, $G_c = \{A_i, A_k\}$, and $G_f = \{A_k, A_l\}$:

* **Child inherits $A_k$ from alleged father:**
  
  $$KI_l = \frac{1}{2 p_k}$$

* **With Balding-Nichols $\theta$-correction:**

  $$KI_l(\theta) = \frac{1}{2 \left[\theta + (1-\theta)p_k\right]}$$

### 3.2 Full-Sibling Index ($KI_{FS}$)
Using Ito-Donnelly $k$-coefficients ($k_0 = 0.25, k_1 = 0.50, k_2 = 0.25$ for sharing 0, 1, or 2 alleles Identical By Descent):

$$P(G_1, G_2 \mid \text{Full Sibs}) = k_0 P(G_1)P(G_2) + k_1 P(G_1, G_2 \mid \text{IBD}=1) + k_2 P(G_1, G_2 \mid \text{IBD}=2)$$

$$KI_{FS} = \frac{P(G_1, G_2 \mid \text{Full Sibs})}{P(G_1) P(G_2)}$$

---

## 4. Stochastic Modeling: Dropout & Drop-in

In low-template DNA analysis ($< 100\text{ pg}$), stochastic effects are modeled probabilistically:

### 4.1 Dropout Probability ($P(D)$)
Dropout probability $P(D)$ is modeled as a logistic function of peak height or DNA concentration $x$:

$$P(D \mid x) = \frac{1}{1 + e^{\beta_0 + \beta_1 x}}$$

Where $\beta_0, \beta_1$ are empirically calibrated parameters per locus.

### 4.2 Drop-in Probability ($P(C)$)
Drop-in is modeled as a Poisson process with rate parameter $\lambda_C$:

$$P(C = k) = \frac{\lambda_C^k e^{-\lambda_C}}{k!}$$

Drop-in allele height $h_c$ follows an exponential distribution:

$$f(h_c) = \lambda_h e^{-\lambda_h (h_c - AT)}$$

where $AT$ is the analytical threshold (e.g., 50 RFU).

---

## 5. Continuous Peak Height Models — Module 02

### 5.1 Biophysical Expected Peak Height ($\mu_{l,a}$)

For a K-contributor mixture at locus $l$, allele $a$, the expected RFU height incorporates
template quantity $T_l$, per-locus amplification efficiency $A_l$, contributor mixture weight
$w_k$, molecular-size degradation, and $n-1$ back-stutter:

$$\mu_{l,a} = T_l \cdot A_l \cdot \sum_{k=1}^{K} w_k \cdot 10^{-d_k(S_{l,a} - S_0)} \cdot n_{k,l,a} + SR_l \cdot \mu_{l, a+1}$$

Where:
- $S_{l,a}$ — molecular size (bp) of allele $a$ at locus $l$
- $S_0 = 100$ bp — reference molecular size
- $d_k \ge 0$ — exponential degradation slope for contributor $k$
- $n_{k,l,a} \in \{0, 1, 2\}$ — dosage (allele count) of contributor $k$ at allele $a$
- $SR_l$ — locus-specific SWGDAM 2020 back-stutter ratio (e.g., $SR_{\text{TH01}}=0.025$, $SR_{\text{SE33}}=0.110$)
- $S_0 = 100$ bp reference ensures degradation factor $= 1$ for the smallest fragments

### 5.2 EuroForMix Gamma Likelihood ($§2.1$ Research)

Peak height $h_{l,a}$ follows a Gamma distribution parameterized by the
coefficient-of-variation $\omega$ (CV, 0.20–0.40):

$$h_{l,a} \sim \text{Gamma}\!\left(\alpha = \frac{1}{\omega^2},\; \beta = \mu_{l,a} \cdot \omega^2\right)$$

$$\ln \mathcal{L}_{\text{Gamma}} = \sum_{l}\sum_{a} \left[ -\ln\Gamma\!\left(\frac{1}{\omega^2}\right) - \frac{\ln(\mu_{l,a}\omega^2)}{\omega^2} + \left(\frac{1}{\omega^2}-1\right)\ln h_{l,a} - \frac{h_{l,a}}{\mu_{l,a}\omega^2} \right]$$

**Golden Vector VECTOR_02_MCMC_A:** Numerical precision verified: $|\ln\mathcal{L}_{\text{computed}} - \ln\mathcal{L}_{\text{analytical}}| < 10^{-8}$.

### 5.3 STRmix Log-Normal Likelihood ($§2.2$ Research)

Peak height log-likelihood with heteroscedastic variance ($\gamma \approx 1.0$, STRmix default):

$$\ln(h_{l,a}) \sim \mathcal{N}\!\left(\ln\mu_{l,a},\; \frac{\sigma^2}{\mu_{l,a}^\gamma}\right)$$

$$\ln\mathcal{L}_{\text{LogNorm}} = \sum_{l}\sum_{a} \left[ -\frac{1}{2}\ln\!\left(2\pi\frac{\sigma^2}{\mu_{l,a}^\gamma}\right) - \frac{(\ln h_{l,a} - \ln\mu_{l,a})^2}{2\sigma^2/\mu_{l,a}^\gamma} \right]$$

**Golden Vector VECTOR_02_MCMC_B:** $|\sigma^2_{l,a,\text{computed}} - \sigma^2/\mu^\gamma| < 10^{-10}$.

### 5.4 24-Locus Back-Stutter Ratios ($SR_l$)

Locus-specific $n-1$ stutter slope from SWGDAM 2020:

| Locus | $SR_l$ | Locus | $SR_l$ |
|:---|:---:|:---|:---:|
| TH01 | 0.025 | SE33 | 0.110 |
| D21S11 | 0.085 | D12S391 | 0.112 |
| FGA | 0.088 | D18S51 | 0.092 |
| D1S1656 | 0.095 | D3S1358 | 0.082 |
| PENTA E/D | 0.038–0.040 | AMEL | 0.000 |

---

## 6. MCMC & Uncertainty Quantification — Module 02

### 6.1 3-Chain Metropolis-Hastings Algorithm

Parameter vector $\Theta = \{w_1,\ldots,w_K, d_1,\ldots,d_K, G_1,\ldots,G_K\}$ is sampled
from the posterior $P(\Theta|E) \propto \mathcal{L}(E|\Theta) \cdot P(\Theta)$ via acceptance ratio:

$$\alpha = \min\!\left(1,\; \frac{\mathcal{L}(E|\Theta^*) \cdot P(\Theta^*) \cdot q(\Theta^{(t)}|\Theta^*)}{\mathcal{L}(E|\Theta^{(t)}) \cdot P(\Theta^{(t)}) \cdot q(\Theta^*|\Theta^{(t)})}\right)$$

**Sampling Constants:**
- $N_{\text{burn}} = 10{,}000$ (discard warm-up iterations)
- $N_{\text{sample}} = 50{,}000$ (production) / $100{,}000$ (high-confidence casework)
- $K_{\text{thin}} = 10$ (retain every 10th sample)
- $N_{\text{chains}} = 3$ (parallel independent chains)

**Mixture Weight Proposals** via symmetric Dirichlet: $\mathbf{w}^* \sim \text{Dir}(c \cdot \mathbf{w}^{(t)})$
with concentration $c=50$ for fine-tuned local proposals.

**Degradation Proposals** via truncated Gaussian: $d_k^* = \mathcal{N}(d_k^{(t)}, 0.0005^2)|_{d \ge 0}$.

### 6.2 Gelman-Rubin $\hat{R}$ Convergence Diagnostic

For $M$ chains each of length $N$:

$$\hat{R} = \sqrt{\frac{\hat{\text{var}}}{W}} = \sqrt{\frac{\frac{N-1}{N}W + \frac{1}{N}B}{W}}$$

Where $W = \text{mean}(s_m^2)$ (within-chain variance) and $B = N \cdot \text{var}(\bar{\theta}_m)$ (between-chain variance).

**Convergence criterion:** $\hat{R} < 1.05$ for all parameters.

### 6.3 Effective Sample Size (ESS)

$$\text{ESS} = \frac{N_{\text{total}}}{1 + 2\sum_{k=1}^{\infty} \rho_k}$$

where $\rho_k$ is the lag-$k$ autocorrelation. Truncated at first negative $\rho_k$ (initial positive sequence estimator).

**Minimum threshold:** $\text{ESS} > 1{,}000$ for reliable posterior inference.

### 6.4 Integrated Likelihood Ratio in Log-Space

H_p and H_d posteriors are integrated via log-sum-exp:

$$\ln P(E|H) \approx \ln\frac{1}{M}\sum_{m=1}^{M} e^{\ln\mathcal{L}(E|\Theta_m)} = \max_m + \ln\sum_m e^{\ln\mathcal{L}_m - \max_m} - \ln M$$

$$\log_{10}LR = \frac{\ln P(E|H_p) - \ln P(E|H_d)}{\ln 10}$$

### 6.5 95% HPD Conservative Lower Bound

From the empirical $\log_{10}LR$ distribution across all pooled samples:

$$\log_{10}LR_{\text{HPD},95} = \bar{\log_{10}LR} - 1.96 \cdot \frac{s_{\log_{10}LR}}{\sqrt{M}}$$

The lower bound is reported in court proceedings as the conservative statistical weight of evidence (Prosecutor's Fallacy shield).

### 6.6 Tippett Calibration Curve

$$\text{True Donor Curve:}\quad P\!\left(\log_{10}LR \ge x \mid H_p\right) = \frac{|\{LR_i \ge 10^x\}|}{n_{H_p}}$$

$$\text{Non-Donor Curve:}\quad P\!\left(\log_{10}LR \ge x \mid H_d\right) = \frac{|\{LR_j \ge 10^x\}|}{n_{H_d}}$$

**Calibration metric — Cllr (Log-Likelihood Ratio Cost):**

$$C_{\text{llr}} = \frac{1}{2}\left[\frac{1}{n_{H_p}}\sum_{i}\log_2\!\left(1 + \frac{1}{LR_i}\right) + \frac{1}{n_{H_d}}\sum_{j}\log_2(1 + LR_j)\right]$$

- $C_{\text{llr}} = 0$: Perfect discrimination
- $C_{\text{llr}} = 1$: Uninformative system (all $LR = 1$)

---

## 7. Population Genetics & Substructure Metrics

### 7.1 Wright's Fixation Index ($F_{ST}$)
To quantify population substructure differentiation between subpopulations $P_1$ and $P_2$:

$$F_{ST} = \frac{H_T - H_S}{H_T}$$

where $H_S = \frac{H_{S1} + H_{S2}}{2}$ is average subpopulation heterozygosity, and $H_T = 1 - \sum \bar{p}_i^2$ is total pooled population heterozygosity.

Nei's standard genetic distance $D$ is calculated as:

$$D = -\ln(1 - F_{ST})$$

### 7.2 NRC II Recommendation 4.1 Rare Allele Bounding
For rare or unobserved alleles in database of size $N$ individuals ($2N$ alleles):

$$p_{\min} = \frac{5}{2N}$$

If raw frequency $p < p_{\min}$, bounded frequency $p_{\text{bounded}} = p_{\min}$ is applied to prevent extreme overestimation of rarity.

Dirichlet Laplace pseudo-count smoothing across $K$ allele categories with prior parameter $\alpha$:

$$p_i = \frac{c_i + \alpha}{N_{\text{total}} + \alpha \cdot K}$$

---

## 8. ENFSI Evaluative Verbal Scale Mapping

Continuous $LR$ and $\log_{10}(LR)$ values are mapped to the 7-tier ENFSI 2015 evaluative scale:

$$V(LR) = \begin{cases} 
\text{Extremely Strong Support for } H_p & \text{if } \log_{10}(LR) \ge 6 \\
\text{Very Strong Support for } H_p & \text{if } 4 \le \log_{10}(LR) < 6 \\
\text{Strong Support for } H_p & \text{if } 2 \le \log_{10}(LR) < 4 \\
\text{Moderately Strong Support for } H_p & \text{if } 1 \le \log_{10}(LR) < 2 \\
\text{Uninformative / Inconclusive} & \text{if } -1 < \log_{10}(LR) < 1 \\
\text{Support for } H_d \text{ (Exclusion)} & \text{if } \log_{10}(LR) \le -1
\end{cases}$$

---

## 9. Expanded Lineage DNA Forensics (Y-STR, X-STR, mtDNA)

### 9.1 Y-STR Clopper-Pearson 95% Confidence Upper Bound
For haplotype count $x$ observed in database of size $N$ with confidence $1 - \alpha = 0.95$:
If $x = 0$ (unobserved haplotype):

$$p_{\text{upper}} = 1 - \alpha^{1/N}$$

For $N = 2500$ and $\alpha = 0.05$:

$$p_{\text{upper}} = 1 - 0.05^{1/2500} \approx 0.001198$$

### 9.2 X-STR Kinship Index ($KI_X$)
For father-daughter pair at locus $l$ where father possesses allele $A_f$ and daughter possesses alleles $\{A_{d1}, A_{d2}\}$:

$$KI_X = \begin{cases} \frac{1}{2 p_f} & \text{if } A_f \in \{A_{d1}, A_{d2}\} \\ 0 & \text{if } A_f \notin \{A_{d1}, A_{d2}\} \end{cases}$$

### 9.3 mtDNA rCRS Distance & Decision Rule
Let $E$ and $S$ be sets of hypervariable variants $(pos, alt)$ in HV1 (16024–16365), HV2 (73–340), and HV3 (438–574) relative to rCRS ($AC\_000021.2$).
Symmetric difference count $d = |E \Delta S|$:

$$\text{Verdict} = \begin{cases} \text{Cannot Be Excluded (Maternal Match)} & \text{if } d = 0 \\ \text{Inconclusive (Heteroplasmy / Mutation)} & \text{if } d = 1 \\ \text{Excluded (Different Lineages)} & \text{if } d \ge 2 \end{cases}$$

---

## 10. Missing Persons Candidate Ranking & Interpol DVI Reconciliation

### 10.1 Pedigree Candidate Posterior Probability
For a missing person target query $Q$ evaluated against database candidate $C_i$ with prior probability $P(H_p)$ (default $0.50$):

$$P(H_p \mid E, C_i) = \frac{LR(Q, C_i) \cdot P(H_p)}{LR(Q, C_i) \cdot P(H_p) + (1 - P(H_p))}$$

where $LR(Q, C_i) = \max \left( LR_{\text{Parent-Child}}, LR_{\text{Full-Sibling}} \right)$.

### 10.2 Interpol DVI AM/PM Identification Thresholds
For Ante-Mortem family reference $AM_i$ compared against Post-Mortem human remain $PM_j$:

$$\text{Status}(AM_i, PM_j) = \begin{cases} 
\text{CONFIRMED\_IDENTIFICATION} & \text{if } \log_{10} LR \ge 4.0 \\
\text{PROBABLE\_IDENTIFICATION} & \text{if } 1.0 \le \log_{10} LR < 4.0 \\
\text{EXCLUDED} & \text{if } \log_{10} LR \le -1.0 \\
\text{INCONCLUSIVE} & \text{otherwise}
\end{cases}$$

---

## 11. Human Identification (HID) Multi-Modal Joint Likelihood Ratio

### 11.1 Joint Likelihood Ratio Product Rule
For unlinked genomic markers across independent modalities (Autosomal STR, Y-STR, mtDNA, and Phenotype SNPs) for unidentified human remains $R$ and candidate $C$:

$$LR_{\text{joint}} = LR_{\text{Autosomal STR}} \cdot LR_{\text{Y-STR}} \cdot LR_{\text{mtDNA}} \cdot LR_{\text{SNP}}$$

Assuming logarithmic additivity:

$$\log_{10}(LR_{\text{joint}}) = \log_{10}(LR_{\text{STR}}) + \log_{10}(LR_{\text{Y-STR}}) + \log_{10}(LR_{\text{mtDNA}}) + \log_{10}(LR_{\text{SNP}})$$

### 11.2 Skeletal Amplicon Degradation Index
Let $RFU_{\text{short}}$ be the average peak height for short locus amplicons (<200bp) and $RFU_{\text{long}}$ be the average peak height for long locus amplicons (>300bp: FGA, D18S51, D21S11):

$$DI_{\text{skeletal}} = \frac{RFU_{\text{short}}}{RFU_{\text{long}}}$$

Risk classification:

$$\text{Risk}_{\text{dropout}} = \begin{cases} 
\text{HIGH (MiniSTR Recommended)} & \text{if } DI_{\text{skeletal}} \ge 2.50 \\
\text{MODERATE (Partial Long Loci Dropout)} & \text{if } 1.25 \le DI_{\text{skeletal}} < 2.50 \\
\text{LOW (Standard Multiplex Protocol)} & \text{if } DI_{\text{skeletal}} < 1.25
\end{cases}$$

---

## 12. Forensic Anthropology Osteological Morphometrics

### 12.1 Trotter-Gleser Stature Regression
For maximum femur length $L_{\text{femur}}$ (cm):

$$\text{Stature}_{\text{est}} = 2.38 \cdot L_{\text{femur}} + 61.41 \pm 3.27 \text{ cm}$$

For maximum tibia length $L_{\text{tibia}}$ (cm):

$$\text{Stature}_{\text{est}} = 2.52 \cdot L_{\text{tibia}} + 78.62 \pm 3.37 \text{ cm}$$

### 12.2 Craniometric Index & Population Affinity Classification
Let $B_{\text{cranial}}$ be maximum cranial breadth (XCB) and $L_{\text{cranial}}$ be maximum cranial length (GOL):

$$CI = \frac{B_{\text{cranial}}}{L_{\text{cranial}}} \times 100$$

Affinity classification:

$$\text{Affinity}_{\text{craniometric}} = \begin{cases} 
\text{Dolichocephalic (African / Long-Headed Affinity)} & \text{if } CI < 75.0 \\
\text{Mesocephalic (European / Medium-Headed Affinity)} & \text{if } 75.0 \le CI \le 80.0 \\
\text{Brachycephalic (Asian / Broad-Headed Affinity)} & \text{if } CI > 80.0
\end{cases}$$

---

## 13. Forensic Entomology ADH Thermal Development Models

### 13.1 Accumulated Degree Hours ($ADH$)
For mean ambient temperature $T_{\text{ambient}}$ and species-specific base development threshold $T_{\text{base}}$:

$$T_{\text{effective}} = \max(0, T_{\text{ambient}} - T_{\text{base}})$$

Accumulated Degree Hours ($ADH$) over time $t$ (hours):

$$ADH = \int_{0}^{t} (T(\tau) - T_{\text{base}}) \, d\tau \approx T_{\text{effective}} \cdot t$$

### 13.2 Minimum Postmortem Interval ($PMI_{\text{min}}$)
Given species development threshold $ADH_{\text{stage}}$ required to reach developmental stage $S$:

$$PMI_{\text{min, hours}} = \frac{ADH_{\text{stage}}}{T_{\text{effective}}}$$

$$PMI_{\text{min, days}} = \frac{PMI_{\text{min, hours}}}{24}$$

Species base development thresholds ($T_{\text{base}}$):
- *Calliphora vicina*: $T_{\text{base}} = 6.0^\circ\text{C}$
- *Lucilia sericata*: $T_{\text{base}} = 9.0^\circ\text{C}$
- *Sarcophaga carnaria*: $T_{\text{base}} = 8.0^\circ\text{C}$

---

## 14. Forensic Palynology & Plant DNA Barcoding Distance Metrics

### 14.1 Plant DNA Barcode Sequence Alignment Similarity ($S_{\text{DNA}}$)
For query plant DNA barcode sequence $Q$ (rbcL, matK, trnL-trnF intergenic spacer) aligned against reference sequence $R$ of length $L$:

$$S_{\text{DNA}} = \frac{1}{L} \sum_{i=1}^{L} \delta(Q_i, R_i)$$

where $\delta(Q_i, R_i) = 1$ if nucleotide $Q_i = R_i$, and $0$ otherwise.

### 14.2 Geographic Habitat Association Likelihood Ratio ($LR_{\text{habitat}}$)
For botanical assemblage $A = \{s_1, s_2, \dots, s_k\}$ recovered from evidence compared against suspected outdoor scene habitat $H_{\text{scene}}$ versus background habitat $H_{\text{bg}}$:

$$LR_{\text{habitat}} = \frac{P(A \mid H_{\text{scene}})}{P(A \mid H_{\text{bg}})} = \prod_{m=1}^{k} \frac{P(s_m \mid H_{\text{scene}})}{P(s_m \mid H_{\text{bg}})}$$

---

## 15. Forensic Microbiology 16S rRNA Abundance & Bray-Curtis Dissimilarity Metrics

### 15.1 Shannon Diversity Index ($H'$)
For microbial community relative abundance profile $\mathbf{p} = (p_1, p_2, \dots, p_S)$ across $S$ species:

$$H' = -\sum_{i=1}^{S} p_i \ln(p_i)$$

### 15.2 Bray-Curtis Dissimilarity ($D_{\text{Bray-Curtis}}$)
For two microbial community relative abundance vectors $\mathbf{u}$ and $\mathbf{v}$ across common genera:

$$D_{\text{Bray-Curtis}} = 1 - \frac{2 \sum_{i} \min(u_i, v_i)}{\sum_{i} (u_i + v_i)}$$

### 15.3 Human Body Site Origin Likelihood Ratio ($LR_{\text{microbiome}}$)
For trace microbial evidence $E$ compared against body site hypothesis $H_{\text{site}}$ (e.g. Skin, Oral, Vaginal, Gut) versus random background site $H_{\text{bg}}$:

$$LR_{\text{microbiome}} = \frac{P(E \mid H_{\text{site}})}{P(E \mid H_{\text{bg}})}$$

---

## 16. mRNA Expression Profiling & Multinomial Body Fluid Identification

### 16.1 Multinomial Softmax Fluid Probability ($P(\text{Fluid}_k \mid \mathbf{X})$)
Given relative transcript expression intensities $\mathbf{X} = (X_1, X_2, \dots, X_M)$ across cell-type specific mRNA markers ($HBA1, PRM1, HTN3, CYP2B7P1, MMP7, SLC14A2$), the posterior probability for body fluid category $k \in \{\text{Venous Blood}, \text{Semen}, \text{Saliva}, \text{Vaginal Secretion}, \text{Menstrual Blood}, \text{Urine}\}$ is:

$$P(\text{Fluid}_k \mid \mathbf{X}) = \frac{e^{\beta_{k0} + \sum_{m=1}^{M} \beta_{km} X_m}}{\sum_{j=1}^{K} e^{\beta_{j0} + \sum_{m=1}^{M} \beta_{jm} X_m}}$$

### 16.2 RNA Ribosomal Integrity Ratio ($R_{28S/18S}$)
For electrophoretic peak heights of $28\text{S}$ and $18\text{S}$ ribosomal RNA subunits:

$$R_{28S/18S} = \frac{RFU_{28S}}{RFU_{18S}}$$

---

## 18. Forensic Serology Antigen Frequencies & Dual Serology-DNA Likelihood Ratio Synthesis

### 18.1 Serological Population Frequency ($f_{\text{serology}}$)
For blood group antigen phenotypes across ABO, Rh D, and Kell systems:

$$f_{\text{serology}} = f_{\text{ABO}} \cdot f_{\text{Rh}} \cdot f_{\text{Kell}}$$

Single-locus serological Likelihood Ratio ($LR_{\text{serology}}$):

$$LR_{\text{serology}} = \frac{1}{f_{\text{serology}}}$$

### 18.2 Combined Dual Serology + DNA Likelihood Ratio ($LR_{\text{combined}}$)
Synthesizes classical serological evidence with 24-locus autosomal STR profiles using the independent product rule:

$$LR_{\text{combined}} = LR_{\text{serology}} \cdot LR_{\text{STR}}$$

$$\log_{10}(LR_{\text{combined}}) = \log_{10}(LR_{\text{serology}}) + \log_{10}(LR_{\text{STR}})$$

---

## 19. Forensic Knowledge Graph Relational Adjacency Matrix & Traversal Metrics

### 19.1 Adjacency Matrix & Multi-Hop Path Count ($A_{ij}^k$)
For a directed forensic knowledge graph $G = (V, E)$ with $|V| = N$ nodes across types $\{\text{Case}, \text{Person}, \text{Evidence}, \text{Sample}, \text{DnaProfile}, \text{Reference}, \text{Scene}, \text{Report}\}$, the binary adjacency matrix $\mathbf{A} \in \{0,1\}^{N \times N}$ is defined as:

$$A_{ij} = \begin{cases} 1 & \text{if } (v_i, v_j) \in E \\ 0 & \text{otherwise} \end{cases}$$

The element $(A^k)_{ij}$ in the $k$-th matrix power yields the exact number of relational paths of length $k$ between node $v_i$ and node $v_j$.

### 19.2 Shortest Path Distance ($d(u,v)$)
The geodesic distance $d(u,v)$ between evidence node $u \in V$ and person/scene node $v \in V$ is:

$$d(u,v) = \min \{ k \mid (A^k)_{uv} > 0 \}$$

---

## 20. Crime Scene Evidence Spatial Coordinate Transformation & Cryptographic Chain of Custody Hashing

### 20.1 Spatial Euclidean Distance ($d_{\text{spatial}}$)
For two biological evidence items $E_A, E_B$ recovered at 3D spatial coordinates $(x_A, y_A, z_A)$ and $(x_B, y_B, z_B)$ within a crime scene:

$$d_{\text{spatial}}(E_A, E_B) = \sqrt{(x_A - x_B)^2 + (y_A - y_B)^2 + (z_A - z_B)^2}$$

### 20.2 Cryptographic Chain of Custody Hash Ledger ($H_k$)
For custody transfer step $k \ge 1$ with previous ledger hash $H_{k-1}$, sender $S_k$, receiver $R_k$, and UTC timestamp $t_k$:

$$H_0 = \text{SHA-256}(\text{EvidenceID} \parallel \text{SceneID} \parallel \text{CollectorID} \parallel \text{SealCode} \parallel t_0)$$

$$H_k = \text{SHA-256}(H_{k-1} \parallel S_k \parallel R_k \parallel \text{Reason}_k \parallel t_k)$$

---

## 21. Bloodstain Pattern Morphometry & Trigonometric Impact Angle Estimation

### 21.1 Ellipse Aspect Ratio ($\epsilon$)
For fitted bloodstain ellipse with minor axis width $W$ and major axis length $L$ ($W \le L$):

$$\epsilon = \frac{W}{L}$$

### 21.2 Trigonometric Impact Angle ($\alpha$)
The impact angle $\alpha$ relative to the target surface plane is:

$$\alpha = \arcsin\left(\frac{W}{L}\right) \quad (\text{radians})$$

$$\alpha_{\text{deg}} = \frac{180}{\pi} \cdot \arcsin\left(\frac{W}{L}\right) \quad (\text{degrees})$$

---

## 22. Microscopic Hair Medullary Index & Follicular Root DNA Routing

### 22.1 Hair Medullary Index ($I_{\text{medulla}}$)
For microscopic hair evidence with inner medulla shaft diameter $d_{\text{medulla}}$ and total hair shaft diameter $D_{\text{hair}}$:

$$I_{\text{medulla}} = \frac{d_{\text{medulla}}}{D_{\text{hair}}}$$

Species Origin Decision Boundary:

$$\text{Species} = \begin{cases} \text{Human} & \text{if } I_{\text{medulla}} < 0.33 \\ \text{Non-Human Animal} & \text{if } I_{\text{medulla}} \ge 0.50 \end{cases}$$

### 22.2 Follicular Root Sheath DNA Routing Protocol
Given root morphology $R \in \{\text{Anagen With Sheath}, \text{Catagen With Sheath}, \text{Telogen Without Sheath}, \text{Shaft Only}\}$:

$$\text{DNA Strategy} = \begin{cases} \text{Nuclear 24-Locus STR Profiling} & \text{if } R \text{ contains Sheath} \\ \text{Mitochondrial DNA (HV1/HV2) Sequencing} & \text{otherwise} \end{cases}$$

---

## 23. Low-Template Touch DNA Stochastic Dropout Modeling & Substrate Efficiency

### 23.1 Substrate Recovered DNA Mass ($m_{\text{recovered}}$)
For input Touch DNA mass $m_{\text{input}}$ (pg) deposited on substrate $S$ with physical recovery efficiency $\eta(S)$:

$$m_{\text{recovered}} = \eta(S) \cdot m_{\text{input}}$$

where $\eta(\text{Smooth Non-Porous}) = 0.60$, $\eta(\text{Textured Non-Porous}) = 0.40$, $\eta(\text{Porous Fabric}) = 0.20$.

### 23.2 Low-Template Allele Dropout Probability ($P(D)$)
The stochastic allele dropout probability $P(D \mid m_{\text{recovered}})$ as a function of locus sensitivity parameter $\lambda$:

$$P(D \mid m_{\text{recovered}}) = \exp\left(-\lambda \cdot m_{\text{recovered}}\right)$$

### 23.3 Allele Drop-in Rate ($P(C)$)
The drop-in probability $P(C)$ accounts for background exogenous contamination:

$$P(C) = 0.01 + 0.05 \cdot P(D)$$

---

## 24. HIrisPlex-S Multi-Class Logistic Regression & Population-Calibrated Uncertainty

### 24.1 Population-Calibrated Posterior Phenotype Probability ($P(C_i \mid S, A)$)
Given target phenotype class $C_i$, SNP dosage vector $S$, and Biogeographic Ancestry prior distribution $P(A)$:

$$P(C_i \mid S, A) = \frac{P(S \mid C_i) \cdot P(C_i \mid A)}{\sum_{j} P(S \mid C_j) \cdot P(C_j \mid A)}$$

### 24.2 ISO 17025 Expanded Measurement Uncertainty ($U_{95\%}$)
For predicted class probability $P_i \in [0, 1]$ across $N=100$ reference calibration samples:

$$u_c = \sqrt{\frac{P_i (1 - P_i)}{N}}$$

$$U_{95\%} = k \cdot u_c \quad (k=2, \quad 95\% \text{ confidence level})$$

$$\text{Confidence Interval} = \left[ \max(0, P_i - U_{95\%}), \min(1, P_i + U_{95\%}) \right]$$

---

## 25. Forensic DNA Epigenetic Clock & Epigenomic Age Estimation

### 25.1 ElasticNet CpG Methylation Age Prediction ($\text{Age}_{\text{raw}}$)
Given target CpG site methylation ratios $\beta_k \in [0, 1]$ across $M=5$ forensic markers (*ELOVL2*, *FHL2*, *TRIM59*, *KLF14*, *MIR29B2CHG*):

$$\text{Age}_{\text{raw}} = \beta_0 + \sum_{k=1}^{M} w_k \cdot \beta_{\text{CpG}, k}$$

where baseline intercept $\beta_0 = 14.8$, $w_{\text{ELOVL2}} = 52.4$, $w_{\text{FHL2}} = 38.6$, $w_{\text{TRIM59}} = 29.8$, $w_{\text{KLF14}} = -18.5$, $w_{\text{MIR29B2CHG}} = 24.1$.

### 25.2 Tissue Intercept Calibration & Estimated Age ($\text{Age}_{\text{est}}$)
With tissue offset $\delta_{\text{tissue}}$ ($\text{Blood} = +0.0$, $\text{Buccal} = +1.2$, $\text{Saliva} = -0.8$, $\text{Bone} = +2.1$ years):

$$\text{Age}_{\text{est}} = \text{Age}_{\text{raw}} + \delta_{\text{tissue}}$$

### 25.3 ISO 17025 Expanded Measurement Uncertainty & 95% Prediction Interval
For standard error of estimation $S_E = 3.20$ years and coverage factor $k=2$:

$$U_{95\%} = k \cdot S_E = 2 \cdot 3.20 = 6.40 \text{ years}$$

$$\text{Prediction Interval}_{95\%} = \left[ \max(0, \text{Age}_{\text{est}} - U_{95\%}), \text{Age}_{\text{est}} + U_{95\%} \right]$$

### 25.4 Biological Age Acceleration Delta ($\Delta_{\text{age}}$)
For known chronological age $A_{\text{chrono}}$:

$$\Delta_{\text{age}} = \text{Age}_{\text{est}} - A_{\text{chrono}}$$

---

## 26. Epigenetic Tissue-of-Origin Deconvolution & Environmental Biomarkers

### 26.1 Dirichlet-Multinomial Tissue Mixture Deconvolution ($\mathbf{p}_{\text{tissue}}$)
Given sample tDMR methylation vector $\mathbf{\beta}_{\text{sample}} = (\beta_1, \dots, \beta_K)$ across $K$ tissue-specific loci and reference profile matrix $\mathbf{M}$:

$$D_j = \sum_{k=1}^{K} \left( \beta_{k, \text{sample}} - M_{k, j} \right)^2$$

$$L_j = \exp\left( -\lambda \cdot D_j \right) \quad (\lambda = 10.0)$$

$$p_{\text{tissue}, j} = \frac{L_j}{\sum_{m=1}^{T} L_m}$$

### 26.2 Tissue Likelihood Ratio ($LR_{\text{tissue}}$)
For top predicted tissue $T_1$ and secondary tissue hypothesis $T_2$:

$$LR_{\text{tissue}} = \frac{p_{\text{tissue}, 1}}{\max(\epsilon, p_{\text{tissue}, 2})} \quad (\epsilon = 10^{-4})$$

### 26.3 AHRR Smoking Biomarker Classification
For cg05575921 methylation ratio $\beta_{\text{AHRR}} \in [0, 1]$:

$$\text{Status} = \begin{cases} \text{Current Heavy Smoker}, & \beta_{\text{AHRR}} < 0.55 \\ \text{Former / Light Smoker}, & 0.55 \le \beta_{\text{AHRR}} < 0.80 \\ \text{Non-Smoker}, & \beta_{\text{AHRR}} \ge 0.80 \end{cases}$$

---

## 27. Multi-Layered Forensic Genomics Architecture & Joint Likelihood Synthesis

### 27.1 Synthesized Multi-Omic Joint Likelihood Ratio ($LR_{\text{joint}}$)
Given non-linked genomic evidence layers $k \in \{\text{STR}, \text{SNP}, \text{mtDNA}, \text{Y}, \text{WGS}\}$:

$$LR_{\text{joint}} = \prod_{k=1}^{5} LR_k$$

$$\log_{10} LR_{\text{joint}} = \sum_{k=1}^{5} \log_{10} LR_k$$

### 27.2 Composite Probability of Exclusion ($PE_{\text{joint}}$)
For individual layer exclusion probabilities $PE_k \in [0, 1]$:

$$PE_{\text{joint}} = 1 - \prod_{k=1}^{5} \left( 1 - PE_k \right)$$

---

## 28. LIMS Audit Hash Chaining & Instrument Degradation Index

### 28.1 HMAC-SHA256 Workflow Chaining ($H_n$)
For sample workflow step $n$ with previous hash $H_{n-1}$, sample ID $S$, step name $W$, operator $O$, instrument $I$, reagent lot $L$, timestamp $T$, and step result $R$:

$$H_n = \text{HMAC-SHA256}_{K_{\text{secret}}}\left( H_{n-1} \parallel S \parallel W \parallel O \parallel I \parallel L \parallel T \parallel R \right)$$

### 28.2 qPCR Quantifiler Degradation Index ($DI$)
Given Small Autosomal concentration $[\text{SA}]$ and Large Autosomal concentration $[\text{LA}]$ in ng/µL:

$$DI = \frac{[\text{SA}]}{\max(\epsilon, [\text{LA}])} \quad (\epsilon = 10^{-6})$$

---

## 29. Forensic Quality Assurance & Heterozygote Balance Math

### 29.1 Heterozygote Peak Height Ratio ($Hb$)
For heterozygous locus alleles with peak heights $H_1, H_2 \ge AT$ ($AT = 50\text{ RFU}$):

$$Hb = \frac{\min(H_1, H_2)}{\max(H_1, H_2)}$$

$$\text{Status} = \begin{cases} \text{PASS}, & Hb \ge 0.60 \\ \text{ALLELE\_IMBALANCE\_WARNING}, & Hb < 0.60 \end{cases}$$

### 29.2 Stochastic Thresholding ($T_{\text{stoch}}$)
For locus minimum peak height $H_{\min} = \min(H_1, H_2)$:

$$\text{Stochastic Status} = \begin{cases} \text{PASS}, & H_{\min} \ge 150\text{ RFU} \\ \text{STOCHASTIC\_THRESHOLD\_WARNING}, & H_{\min} < 150\text{ RFU} \end{cases}$$

---

## 30. Human Review Audit Chaining & Decision Concordance Metrics

### 30.1 Court Admissibility Dual-Sign-Off Hash ($R_m$)
For human analyst review decision block $m$ with previous hash $R_{m-1}$, sample ID $S$, AI recommendation $A$, human decision $D$, primary analyst $P$, technical reviewer $V$, timestamp $T$, and override justification $J$:

$$R_m = \text{HMAC-SHA256}_{K_{\text{court}}}\left( R_{m-1} \parallel S \parallel A \parallel D \parallel P \parallel V \parallel T \parallel J \right)$$

### 30.2 Decision Concordance Index ($C_{\text{analyst}}$)
For $N$ reviewed forensic cases with $N_{\text{approved}}$ concordant approvals:

$$C_{\text{analyst}} = \frac{N_{\text{approved}}}{N}$$

---

## 31. ISO 17025 Report Hash Integrity & Mathematical Immutability Invariant

### 31.1 ISO 17025 Cryptographic Certificate Hash ($H_{\text{cert}}$)
For 8-section ISO certificate with Case ID $C$, Sample ID $S$, calculated $\log_{10} LR$, ENFSI scale predicate $E$, primary analyst $P$, technical reviewer $V$, and timestamp $T$:

$$H_{\text{cert}} = \text{HMAC-SHA256}_{K_{\text{iso}}}\left( C \parallel S \parallel \log_{10} LR \parallel E \parallel P \parallel V \parallel T \right)$$

### 31.2 Mathematical Immutability Invariant ($\mathcal{I}_{\text{math}}$)
For narrative text engine $\mathcal{N}$ and mathematical statistical engine $\mathcal{M}$:

$$\mathcal{I}_{\text{math}} = \begin{cases} 1 \quad (\text{IMMUTABLE}), & \mathcal{N}(LR) \equiv \mathcal{M}(LR) \\ 0 \quad (\text{VIOLATION}), & \mathcal{N}(LR) \neq \mathcal{M}(LR) \end{cases}$$

---

## 32. Expert Witness Likelihood Ratio & Transposed Conditional Fallacy Prevention

### 32.1 Evidence Likelihood Ratio ($LR$) vs Posterior Odds ($O_{\text{post}}$)
By Bayes' Theorem:

$$\underbrace{\frac{P(H_p \mid E)}{P(H_d \mid E)}}_{\text{Posterior Odds } O_{\text{post}}} = \underbrace{\frac{P(E \mid H_p)}{P(E \mid H_d)}}_{\text{Likelihood Ratio } LR} \times \underbrace{\frac{P(H_p)}{P(H_d)}}_{\text{Prior Odds } O_{\text{prior}}}$$

### 32.2 Transposed Conditional Fallacy Prevention Invariant
The expert witness evaluates exclusively $LR = \frac{P(E \mid H_p)}{P(E \mid H_d)}$, NEVER equating $LR$ to $P(H_p \mid E)$:

$$LR \neq P(H_p \mid E) \quad (\text{Prosecutor's Fallacy Prevention Shield Active})$$

---

## 33. Synthetic Case Stochastic Mixture Generation & Ground-Truth Validation Metrics

### 33.1 Stochastic Peak Height Synthesis ($H_{a,l}$)
For allele $a$ at locus $l$ across $K$ synthetic contributors with mixture proportions $m_k$, degradation factor $d_k$, and baseline RFU $H_0 = 2000$:

$$H_{a,l} = \sum_{k=1}^K \mathbb{I}(a \in G_{k,l}) \cdot m_k \cdot H_0 \cdot (1 - d_k \cdot 0.5) + \epsilon \quad (\epsilon \sim \mathcal{N}(0, \sigma^2))$$

### 33.2 Log-LR Root Mean Square Error ($RMSE_{\text{log10LR}}$)
For $N$ synthetic benchmark scenarios with true likelihood ratio $\log_{10} LR_{\text{true}, i}$ and engine output $\log_{10} LR_{\text{calc}, i}$:

$$RMSE_{\text{log10LR}} = \sqrt{\frac{1}{N} \sum_{i=1}^N \left( \log_{10} LR_{\text{calc}, i} - \log_{10} LR_{\text{true}, i} \right)^2}$$

---

## 34. Forensic Evidence OS Directed Acyclic Graph & End-to-End Pipeline Entropy Reduction

### 34.1 Evidence OS Directed Acyclic Graph ($\mathcal{G}_{\text{OS}}$)
The FORENZA Master OS forms a 6-layer topological graph $\mathcal{G}_{\text{OS}} = (\mathcal{V}, \mathcal{E})$ with 30 subsystem nodes:

$$\mathcal{V} = \mathcal{V}_{\text{Ingest}} \cup \mathcal{V}_{\text{Inference}} \cup \mathcal{V}_{\text{Ledger}} \cup \mathcal{V}_{\text{QC}} \cup \mathcal{V}_{\text{Review}} \cup \mathcal{V}_{\text{Reporting}}$$

### 34.2 End-to-End Joint System Entropy Reduction ($\Delta \mathcal{H}_{\text{system}}$)
For initial uninformative evidence entropy $\mathcal{H}_0$ and post-inference joint likelihood state $\mathcal{H}_{\text{joint}}$:

$$\Delta \mathcal{H}_{\text{system}} = \mathcal{H}_0 - \sum_{k=1}^{30} \mathcal{I}(X_k; Y_{\text{verdict}}) \ge 0$$

---

## 35. Multinomial Probability Distribution Normalization & Sum-to-One Invariant

### 35.1 Generalized Multinomial Distribution Invariant ($\mathcal{I}_{\text{prob}}$)
Let $\mathcal{D} = \{p_1, p_2, \dots, p_K\}$ represent the set of discrete posterior phenotype or biogeographic probabilities generated by a multinomial logistic regression model across $K$ mutually exclusive categories.

The law of total probability requires that the sum of all probability components across the sample space equals exactly unity (or $100\%$ in percentage representation):

$$\sum_{k=1}^K p_k = 1.0 \quad \left(\text{or } \sum_{k=1}^K P_k\% = 100.0\%\right)$$

### 35.2 Numerical Floating-Point Tolerance Boundary ($\epsilon$)
Under IEEE 754 floating-point arithmetic and discrete rounding operations, the forensic validation function $\mathcal{V}_{\text{dist}}(\mathcal{D}, \epsilon)$ enforces a strict bounded tolerance interval:

$$\left| \sum_{k=1}^K p_k - S_{\text{target}} \right| \le \epsilon$$

where $S_{\text{target}} = 100.0$ for percentage-scaled distributions and $S_{\text{target}} = 1.0$ for unit-scaled distributions.

The system enforces calibrated domain-specific tolerances:
* **Eye Colour ($K=3$ categories: Blue, Intermediate/Hazel, Brown):** $\epsilon = 1.0\%$
* **Hair Pigmentation ($K=4$ categories: Blond, Brown, Red, Black):** $\epsilon = 1.0\%$
* **Fitzpatrick Skin Phototype ($K=3$ collapsed ordinal groups from 6 classes):** $\epsilon = 1.5\%$

$$\text{Validation Status} = \begin{cases} \text{NORMALIZED (PASS)}, & \left| \sum_{k=1}^K P_k\% - 100.0\% \right| \le \epsilon \\ \text{DISTRIBUTION\_ERROR (FAIL)}, & \left| \sum_{k=1}^K P_k\% - 100.0\% \right| > \epsilon \end{cases}$$

---

## 36. Dynamic ENFSI Evaluative Reporting Verbal Scale Partitioning Functions

### 36.1 Piecewise Evaluative Verbal Mapping Function ($\mathcal{S}_{\text{ENFSI}}$)
Let $LR$ denote the combined multi-locus Likelihood Ratio. The ENFSI 2017 / SWGDAM 2020 evaluative reporting guideline maps the base-10 logarithmic likelihood ratio $\log_{10}(LR)$ to standardized expert witness verbal qualifiers via the surjective step function $\mathcal{S}_{\text{ENFSI}}: \mathbb{R} \to \mathcal{V}$:

$$\mathcal{S}_{\text{ENFSI}}(\log_{10} LR) = \begin{cases} 
\text{"Extremely / Astronomically Strong Support for Prosecution Hypothesis"}, & \log_{10} LR \ge 18 \\
\text{"Extremely Strong Support for Prosecution Hypothesis"}, & 6 \le \log_{10} LR < 18 \\
\text{"Very Strong Support for Prosecution Hypothesis"}, & 4 \le \log_{10} LR < 6 \\
\text{"Strong Support for Prosecution Hypothesis"}, & 3 \le \log_{10} LR < 4 \\
\text{"Moderately Strong Support for Prosecution Hypothesis"}, & 2 \le \log_{10} LR < 3 \\
\text{"Moderate Support for Prosecution Hypothesis"}, & 1 \le \log_{10} LR < 2 \\
\text{"Limited / Weak Support for Prosecution Hypothesis"}, & 0 < \log_{10} LR < 1 \\
\text{"Inconclusive / Neutral Evidence ($LR = 1$)"}, & \log_{10} LR = 0 \\
\text{"Support for Defense Hypothesis / Exclusion"}, & \log_{10} LR < 0 
\end{cases}$$

### 36.2 ISO/IEC 17025:2017 Evaluative Certificate Conformity Assertion
The formal automated Certificate of Analysis ($\mathcal{C}_{\text{ISO}}$) guarantees that the quantitative numeric Likelihood Ratio and the qualitative verbal predicate are mathematically isomorphic:

$$\mathcal{S}_{\text{ENFSI}}(\log_{10} LR_{\text{calculated}}) \equiv \text{Textual Report Narrative Predicate}$$

This prevents human clerical transcription errors and strictly enforces the judicial **Prosecutor's Fallacy Prevention Shield**.

---

## 37. Population Genetics: Bayesian Dirichlet Prior Smoothing, HWE Exact Testing, Linkage Equilibrium & $F_{st}$ Matrix (Module 03)

### 37.1 Dirichlet Conjugate Prior Posterior Mean Allele Frequency Smoothing
For allele $i$ at locus $l$ with reference prior frequency $p_i^0$, observed database count $n_i$, total database sample size $N$, and subpopulation coancestry $\theta \in [0.01, 0.05]$:

$$\kappa = \frac{1 - \theta}{\theta} \quad (\text{Concentration Parameter / Total Prior Pseudo-count Mass})$$

$$\alpha_i = p_i^0 \cdot \kappa = p_i^0 \cdot \left(\frac{1-\theta}{\theta}\right)$$

$$\tilde{p}_i = \mathbb{E}[p_i \mid n] = \frac{n_i + \alpha_i}{N + \kappa} = \frac{n_i + p_i^0 \cdot \frac{1-\theta}{\theta}}{N + \frac{1-\theta}{\theta}}$$

$$\tilde{p}_{\text{final}, i} = \max\left(\tilde{p}_i, p_{\min}\right) \quad \text{where } p_{\min} = \max\left(\frac{5}{2N}, 0.001\right) \approx 0.00241 \text{ for NIST 1036}$$

### 37.2 Guo & Thompson (1992) Hardy-Weinberg Equilibrium (HWE) Exact Test
For observed genotype configuration $\{N_{ij}\}$ with sample size $N_{\text{total}}$ and marginal allele counts $\{n_i\}$:

$$P\left(\{N_{ij}\} \mid \{n_i\}\right) = \frac{\prod_i n_i! \cdot 2^{N_{\text{total}} - \sum_i N_{ii}}}{N_{\text{total}}! \cdot \prod_{i \le j} N_{ij}!}$$

$$\alpha_{\text{Bonferroni}} = \frac{\alpha_{\text{overall}}}{L} = \frac{0.05}{24} \approx 0.002083 \quad (\text{CODIS-24 Panel Decision Threshold})$$

$$\text{Wright's Inbreeding Coefficient (Wahlund Effect Detect): } F_{IS} = 1 - \frac{H_{\text{obs}}}{H_{\text{exp}}} = 1 - \frac{N_{\text{het}} / N_{\text{total}}}{1 - \sum_i p_i^2}$$

### 37.3 Linkage Equilibrium Pearson $r^2$ Correlation & Product Rule Admissibility
For pairwise loci $L_1$ and $L_2$ across all $C(24, 2) = 276$ locus pairs:

$$D = p_{AB} - p_A \cdot q_B$$

$$r^2 = \frac{D^2}{p_A (1 - p_A) \cdot q_B (1 - q_B)}$$

$$\text{Product Rule Admissibility Condition: } \forall (i, j) \in \text{CODIS-24 Pairs}, \quad r_{ij}^2 < 0.01 \implies LR = \prod_{l=1}^{24} LR_l \text{ is Court-Admissible}$$

### 37.4 Weir & Cockerham (1984) $\hat{\theta}$ / $F_{st}$ Multi-Population Fixation Matrix
For $K$ reference populations:

$$F_{st} = \frac{H_T - H_S}{H_T}, \quad \text{Nei's Distance: } D_{\text{Nei}} = -\ln(1 - F_{st})$$

$$\theta\text{-Corrected Match Probability (NRC II Rec 4.10b): } \pi_a = \frac{\left[\theta + (1-\theta)p_a\right] \left[2\theta + (1-\theta)p_a\right]}{(1+\theta)(1+2\theta)}$$

---

## 38. Low-Template DNA (LTDNA) Stochastic Phenomenon Modeling (Module 04)

### 38.1 Logistic Allele Dropout Probability $P(D \mid x)$
For signal input $x$ (RFU peak height or DNA mass in pg):

$$P(D \mid x) = \frac{1}{1 + \exp\left(-(\beta_0 + \beta_1 \cdot x)\right)}$$

| Calibration Model | $\beta_0$ | $\beta_1$ | $P(D)$ @ 50 units | $P(D)$ @ 150 units | $P(D) < 1\%$ threshold |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **RFU-based** ($x = \text{RFU}$) | $+2.50$ | $-0.025\text{ RFU}^{-1}$ | $77.73\%$ | $22.27\%$ | $> 285\text{ RFU}$ |
| **Mass-based** ($x = \text{pg DNA}$) | $+3.20$ | $-0.080\text{ pg}^{-1}$ | $31.00\%$ | $\approx 0.015\%$ | $> 97\text{ pg}$ |

**Logistic symmetry invariant:** $P(D \mid x_1) + P(D \mid x_2) = 1.0$ when $x_2 = x_1 + 2|\beta_0| / |\beta_1|$ (e.g., RFU: $P(D \mid 50) + P(D \mid 150) = 1.0$).

### 38.2 Poisson Allele Drop-in Model $P(C = k)$ and Exponential Height PDF
- **Poisson Count Distribution** (spurious artefact allele count per locus):
  $$P(C = k) = \frac{\lambda_C^k \cdot e^{-\lambda_C}}{k!} \quad \lambda_C = 0.020 \text{ per locus}$$
  Normalization invariant: $\sum_{k=0}^{\infty} P(C=k) = 1.0$; practical: $\sum_{k=0}^{10} P(C=k) \approx 1 - 10^{-25}$.

- **Exponential Drop-in Peak Height PDF** (height of any artefact allele above AT):
  $$f_{\text{dropin}}(h_c) = \lambda_h \cdot \exp\left(-\lambda_h (h_c - \text{AT})\right), \quad h_c \ge \text{AT} = 50.0\text{ RFU}, \quad \lambda_h = 0.015\text{ RFU}^{-1}$$
  Normalization: $\int_{\text{AT}}^{\infty} f_{\text{dropin}}(h_c)\,dh_c = 1.0$ (unit exponential PDF above AT).

### 38.3 Heterozygote Balance ($H_b$) and Stochastic Quality Flags
$$H_b = \frac{\min(h_1, h_2)}{\max(h_1, h_2)} \quad (\text{Peak height ratio of two alleles at same locus})$$

Stochastic flag triggered (STOCHASTIC\_FLAGS\_ACTIVE) if **any** of:
$$H_b < 0.60 \quad \text{OR} \quad h_{\min} < \text{ST} = 150.0\text{ RFU} \quad \text{OR} \quad \text{any peak} < \text{AT} = 50.0\text{ RFU}$$

### 38.4 Curran-Gill Stochastic Single-Source LTDNA Likelihood Ratio
For suspect genotype $(A_i, A_j)$ and observed low-template EPG evidence, the four allele-state scenarios are:

| Scenario | Numerator Likelihood $P(E \mid H_p)$ |
| :--- | :--- |
| Both alleles present | $(1 - P(D))^2$ |
| Single dropout | $2 \cdot P(D) \cdot (1 - P(D))$ |
| Both alleles dropped | $P(D)^2$ |
| Spurious drop-in | $P(C=1) \cdot f_{\text{dropin}}(h_c)$ |

$$LR_{\text{stochastic}} = \frac{P(E \mid H_p)}{P(G_{E} \mid \theta)} \quad \text{where } P(G_E \mid \theta) = \text{Balding-Nichols } \theta\text{-corrected genotype probability}$$

$$\log_{10}(LR) \in [-300, +300] \quad (\text{IEEE 754 precision clamp enforced})$$

---

## 39. Tippett Calibration Curves, ROC Analysis, $C_{\text{llr}}$ Cost, 95% HPD Lower Bound & ENFSI Evaluative Reporting (Module 05)

### 39.1 Tippett Calibration Curves — Empirical Complementary CDF (ECCDF)

$$\text{Hp Curve: } T_{H_p}(x) = P\left(\log_{10}(\text{LR}) \ge x \mid H_p\right) = \frac{1}{N_{H_p}} \sum_{i=1}^{N_{H_p}} \mathbf{1}\left[\log_{10}(\text{LR}_i) \ge x\right]$$

$$\text{Hd Curve: } T_{H_d}(x) = P\left(\log_{10}(\text{LR}) \ge x \mid H_d\right) = \frac{1}{N_{H_d}} \sum_{j=1}^{N_{H_d}} \mathbf{1}\left[\log_{10}(\text{LR}_j) \ge x\right]$$

**Diagnostic Rates at $\log_{10}(\text{LR}) = 0$ (Neutral Threshold $\text{LR}=1$):**

$$\text{FPR} = P\left(\log_{10}(\text{LR}) > 0 \mid H_d\right) \quad \text{(Misleading Evidence Rate vs. } H_d\text{)}$$

$$\text{FNR} = P\left(\log_{10}(\text{LR}) < 0 \mid H_p\right) \quad \text{(Misleading Evidence Rate vs. } H_p\text{)}$$

$$\text{Discrimination Power} = 1 - \text{FPR} - \text{FNR} \in [0, 1]$$

**Invariants:** $T_{H_p}(x)$ and $T_{H_d}(x)$ are monotone non-increasing; $T(x) \in [0, 1]$ for all $x$.

### 39.2 Empirical ROC Analysis and AUC (Trapezoidal Integration)

At threshold $t$: $\text{TPR}(t) = T_{H_p}(t)$, $\text{FPR}(t) = T_{H_d}(t)$.

$$\text{AUC} = \int_0^1 \text{TPR}(\text{FPR}) \, d(\text{FPR}) \approx \sum_{k=1}^{K} \frac{\text{FPR}_k - \text{FPR}_{k-1}}{2} \cdot (\text{TPR}_k + \text{TPR}_{k-1})$$

**SWGDAM 2020 Target:** $\text{AUC} \ge 0.999$ for court-admissible STR probabilistic genotyping systems.

$$\text{MER}_{\text{upper}} = \max\left(\text{FPR}_{\text{LR}=1},\ \text{FNR}_{\text{LR}=1}\right) \quad \text{(Maximum Misleading Evidence Rate)}$$

### 39.3 Log-Likelihood-Ratio Cost ($C_{\text{llr}}$) — Calibration Score

$$C_{\text{llr}} = \frac{1}{2 N_{H_p}} \sum_{i=1}^{N_{H_p}} \log_2\!\left(1 + \frac{1}{\text{LR}_i}\right) + \frac{1}{2 N_{H_d}} \sum_{j=1}^{N_{H_d}} \log_2\!\left(1 + \text{LR}_j\right) \quad \text{(Brümmer \& du Preez 2006)}$$

**Properties:**
- $C_{\text{llr}} \ge 0$ always.
- $C_{\text{llr}}^{\min} \le C_{\text{llr}}$ (ideal PAV-calibrated system lower bound).
- Calibration loss $= C_{\text{llr}} - C_{\text{llr}}^{\min} \ge 0$.

| Calibration Quality | $C_{\text{llr}}$ Threshold |
| :--- | :--- |
| **Excellent** | $C_{\text{llr}} < 0.05$ |
| **Acceptable** | $C_{\text{llr}} < 0.20$ |
| **Poor** | $C_{\text{llr}} \ge 0.20$ |

### 39.4 Conservative 95% HPD Lower Bound ($\text{LR}_{\text{court}}$)

$$\text{LR}_{\text{court}} = \text{Percentile}_{5\%}\!\left(\left\{ \log_{10}(\text{LR}^{(m)}) \right\}_{m=1}^M\right)$$

The true $\log_{10}(\text{LR})$ exceeds $\text{LR}_{\text{court}}$ with **95% posterior probability** over the MCMC chain. This conservative bound is court-admissible per SWGDAM 2020 and ENFSI 2017 guidelines.

### 39.5 ENFSI 2017 Dynamic 7-Tier Verbal Reporting Scale

| Tier | $\log_{10}(\text{LR})$ Range | English Verbal Predicate | Turkish Verbal Predicate |
| :--- | :--- | :--- | :--- |
| **Tier 5** | $> 6$ | Extremely strong support for prosecution | Son derece güçlü destek (iddianame) |
| **Tier 4** | $4 < x \le 6$ | Very strong support for prosecution | Çok güçlü destek (iddianame) |
| **Tier 3** | $2 < x \le 4$ | Strong support for prosecution | Güçlü destek (iddianame) |
| **Tier 2** | $1 < x \le 2$ | Moderate support for prosecution | Orta düzeyde destek (iddianame) |
| **Tier 1** | $0 < x \le 1$ | Limited support for prosecution | Sınırlı destek (iddianame) |
| **Tier 0** | $x = 0$ | Neutral — no support for either | Tarafsız |
| **Tier −1..−5** | $x < 0$ | Symmetric defence tiers | Savunma katmanları (simetrik) |

**Prosecutor's Fallacy Shield (mandatory in all reports):**
$$P(E \mid H_p) \neq P(H_p \mid E) \quad \text{(Transposed Conditional — inadmissible)}$$

The LR measures $P(\text{Evidence} \mid \text{Hypothesis})$, **NOT** $P(\text{Hypothesis} \mid \text{Evidence})$.

---

## 40. Y-STR Haplotype Forensics, Clopper-Pearson 95% Exact Bounds, Brenner $\theta$ & SMM Paternity Discrepancy Modeling (Module 06)

### 40.1 Database Frequency & Random Match Probability (Y-HRD Standards)

Because the non-recombining portion of the Y chromosome (NRY) is inherited as a single linked haplotype block, frequencies cannot be calculated using the Hardy-Weinberg independent product rule. Estimations rely on exact binomial confidence bounds.

#### Clopper-Pearson 95% Exact Binomial Confidence Interval ($\hat{p}_{\text{upper}}$):

For unobserved rare haplotypes ($k = 0$ in database of size $N$):

$$\hat{p}_{\text{upper}} = 1 - \alpha^{\frac{1}{N+1}} \quad \xrightarrow{\alpha=0.05} \quad \hat{p}_{\text{upper}} = 1 - (0.05)^{\frac{1}{N+1}}$$

For observed haplotypes ($k > 0$):

$$\hat{p}_{\text{upper}} = \frac{(k+1) F_{2(k+1), 2(N-k); 1-\alpha/2}}{(N-k) + (k+1) F_{2(k+1), 2(N-k); 1-\alpha/2}} = I^{-1}_{1-\alpha/2}(k+1, N-k)$$

$$\text{LR}_{\text{Y-STR}} = \frac{1}{\hat{p}_{\text{upper}}}, \quad \log_{10}(\text{LR}_{\text{Y-STR}}) = -\log_{10}(\hat{p}_{\text{upper}})$$

#### Brenner / Surveyor Subpopulation Correction ($\theta / F_{st}$):

$$p_{\text{Brenner}} = \frac{k + \theta}{N + \theta}, \quad \text{LR}_{\text{Brenner}} = \frac{N + \theta}{k + \theta}$$

### 40.2 Discrete Laplace Clonal Clustering Model

For $C$ clonal clusters with weights $w_c$, cluster centers $\mu_{cl}$, and scale parameters $\lambda_{cl}$:

$$P(H) = \sum_{c=1}^C w_c \prod_{l=1}^L f_l(y_l \mid \mu_{cl}, \lambda_{cl})$$

$$f_l(y \mid \mu, \lambda) = \frac{1 - e^{-\lambda}}{1 + e^{-\lambda}} e^{-\lambda |y - \mu|}$$

### 40.3 Minimum Male Contributor Count ($N_{\text{male}}$)

$$N_{\text{male}} = \max_l \left\lceil \frac{n_{\text{alleles}, l}}{2} \right\rceil$$

For multi-copy loci (`DYS385a/b`, `DYF387S1a/b`):
- $> 4$ alleles observed $\implies N_{\text{male}} \ge 3$ contributors.

### 40.4 Stepwise Mutation Model (SMM) for Paternity Discrepancies

$$P(a_s \mid a_f, \mu_l) = \begin{cases} 1 - \mu_l, & a_s = a_f \\ \frac{\mu_l}{2} p^{m-1} (1-p), & |a_s - a_f| = m \ge 1 \end{cases} \quad (p \approx 0.10)$$

- **Standard Loci:** $\mu_l \in [3.5 \times 10^{-4}, 6.2 \times 10^{-3}]$
- **Rapidly Mutating (RM) Loci:** $\mu_l \in [1.1 \times 10^{-2}, 1.8 \times 10^{-2}]$ (`DYS570`, `DYS576`, `DYS627`, `DYS518`, `DYS449`, `DYF387S1a/b`)

---

## 41. X-STR Linkage Groups (Investigator Argus X-12), Kosambi Map Function, and Complex Female Kinship Likelihood Ratios ($KI_X$) (Module 07)

### 41.1 Argus X-12 Linkage Clusters & Kosambi Mapping Function

The X chromosome undergoes meiosis recombination in females (XX) but is passed intact without recombination from father to daughter (XY $\to$ XX). The 12 X-STR markers in the Investigator Argus X-12 multiplex are structured into 4 tightly linked clusters:

| Linkage Group | Locus Name | Band | Position (Mb) | Map (cM) | Intra-Cluster Recombination ($r$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LG1** | **DXS10148** / **DXS10135** / **DXS8378** | Xp22.2 | 12.42 / 13.15 / 14.90 | 18.5 / 19.8 / 22.1 | $r_{1-2} = 0.003, r_{2-3} = 0.022$ |
| **LG2** | **DXS7132** / **DXS10074** / **DXS10079** | Xq12 | 68.10 / 70.80 / 71.35 | 72.3 / 74.8 / 75.3 | $r_{1-2} = 0.015, r_{2-3} = 0.020$ |
| **LG3** | **DXS10103** / **HPRTB** / **DXS10101** | Xq26 | 133.50 / 133.90 / 134.60 | 138.2 / 138.6 / 140.1 | $r_{1-2} = 0.001, r_{2-3} = 0.012$ |
| **LG4** | **DXS10146** / **DXS10134** / **DXS7423** | Xq28 | 148.20 / 149.10 / 150.05 | 155.4 / 156.3 / 157.2 | $r_{1-2} = 0.005, r_{2-3} = 0.008$ |

#### Kosambi Mapping Function:

The conversion between genetic distance $d$ (cM) and recombination fraction $r$ satisfies:

$$r = \frac{1}{2} \tanh\left(\frac{2d}{100}\right) = \frac{1}{2} \frac{e^{4d/100} - 1}{e^{4d/100} + 1}$$

- Invariant: $\lim_{d \to 0} r(d) = 0$, $\lim_{d \to \infty} r(d) = 0.50$.

### 41.2 Complex Female Kinship Index Formulations ($KI_X$)

1. **Father-Daughter (Duo):**
   $$KI_{X, \text{Duo}} = \begin{cases} \frac{1}{p(A_{\text{father}})}, & A_{\text{father}} \in \{A_{d1}, A_{d2}\} \\ 0.0, & \text{otherwise (Exclusion)} \end{cases}$$

2. **Paternal Half-Sisters (PHS):**
   $$KI_{X, \text{PHS}, l} = (1-r) \frac{1}{p_a} + r = \frac{(1-r) h(A_1, A_2) + r \cdot h(A_1) h(A_2)}{h(A_1) h(A_2)}$$
   Combined Kinship Index across all 4 independent linkage groups:
   $$KI_{X, \text{Total}} = \prod_{g=1}^4 KI_{X, \text{LG}_g}, \quad \log_{10} KI_{X, \text{Total}} = \sum_{g=1}^4 \log_{10} KI_{X, \text{LG}_g}$$

3. **Paternal Grandmother - Granddaughter (PGM-GD):**
   $$KI_{X, \text{PGM-GD}} = \frac{1}{2} \frac{1}{p_a} + \frac{1}{2}$$

4. **Mother - Son (MS):**
   $$KI_{X, \text{MS}} = \begin{cases} \frac{0.5}{p(A_{\text{son}})}, & \text{Heterozygous mother } (A_1 A_2) \\ \frac{1.0}{p(A_{\text{son}})}, & \text{Homozygous mother } (A_1 A_1) \\ 0.0, & A_{\text{son}} \notin \{A_{m1}, A_{m2}\} \text{ (Exclusion)} \end{cases}$$

---

## 42. Mitochondrial DNA (mtDNA) Control Region Forensics, ISFG 3' Right-Alignment, IUPAC Heteroplasmy & EMPOP Match Probabilities (Module 08)

### 42.1 Hypervariable Regions & ISFG Right-Alignment Standard

Mitochondrial DNA haplotypes are reported relative to the Revised Cambridge Reference Sequence (**rCRS**, GenBank `NC_012920.1` / `AC_000021.2`) across three hypervariable segments:
- **HV1:** Nucleotide positions 16024–16365 nt
- **HV2:** Nucleotide positions 73–340 nt
- **HV3:** Nucleotide positions 438–574 nt

#### ISFG 3' Right-Alignment Rules for Homopolymeric Tracts:
- **HV1 Poly-C (16184–16193):** T $\to$ C transitions at 16189 generate length variants scored at the 3' extremity as `16189.1C, 16189.2C`.
- **HV2 Poly-C (303–315):** Insertions scored as `309.1C, 309.2C, 315.1C`.
- **Dinucleotide Repeats (522–523):** Scored as `522del, 523del` or `524.1AC, 524.2AC`.

### 42.2 Point Heteroplasmy (PHP) & IUPAC Degeneracy

Site heteroplasmy is classified using standard IUPAC ambiguity codes:
- $Y = \{C, T\}, \quad R = \{A, G\}, \quad W = \{A, T\}, \quad S = \{C, G\}, \quad K = \{G, T\}, \quad M = \{A, C\}$
- Maternal compatibility is satisfied if $S_1 \cap S_2 \neq \emptyset$.

### 42.3 EMPOP Database Frequency & Maternal Likelihood Ratio ($LR_{\text{mtDNA}}$)

For unobserved haplotypes ($k = 0$ in EMPOP reference database of size $N_{\text{EMPOP}}$):

$$\hat{p}_{\text{mtDNA, upper}} = 1 - \alpha^{\frac{1}{N_{\text{EMPOP}}+1}} \quad \xrightarrow{\alpha=0.05} \quad \hat{p}_{\text{mtDNA, upper}} = 1 - (0.05)^{\frac{1}{N_{\text{EMPOP}}+1}}$$

For observed haplotypes ($k > 0$):

$$\hat{p}_{\text{mtDNA, upper}} = I^{-1}_{1-\alpha/2}(k+1, N_{\text{EMPOP}}-k)$$

$$\text{LR}_{\text{mtDNA}} = \frac{1}{\hat{p}_{\text{mtDNA, upper}}}, \quad \log_{10}(\text{LR}_{\text{mtDNA}}) = -\log_{10}(\hat{p}_{\text{mtDNA, upper}})$$

### 42.4 Pairwise Concordance Decision Boundaries (SWGDAM 2019)

$$\text{Status} = \begin{cases} \text{CANNOT\_BE\_EXCLUDED (Maternal Match)}, & \Delta_{\text{positions}} = 0 \\ \text{INCONCLUSIVE (Possible heteroplasmy / germline transition)}, & \Delta_{\text{positions}} = 1 \\ \text{EXCLUDED (Different maternal lineages)}, & \Delta_{\text{positions}} \ge 2 \end{cases}$$

---

## 43. Interpol DVI (Disaster Victim Identification) Multi-Omic Joint Likelihood Ratios & Mass Disaster Decision Boundaries (Module 09)

### 43.1 Multi-Omic Joint Likelihood Ratio ($LR_{\text{Joint}}$)

In mass casualty incidents, Post-Mortem (PM) unidentified remains are reconciled against Ante-Mortem (AM) missing person family pedigrees in compliance with **Interpol DVI Guide Section 4**.

Independent genetic systems are combined via the Generalized Multi-Omic Product Rule:

$$LR_{\text{DVI, Total}} = LR_{\text{Autosomal STR}} \times LR_{\text{Y-STR}}^{\delta_y} \times LR_{\text{mtDNA}}^{\delta_m} \times LR_{\text{SNP}}^{\delta_s}$$

$$LR_{\text{Joint}} = \left( \prod_{l=1}^{L_{\text{auto}}} \frac{P(G_{\text{PM}, l}, G_{\text{AM}, l} \mid H_p)}{P(G_{\text{PM}, l}, G_{\text{AM}, l} \mid H_d)} \right) \times \left( \frac{1}{\hat{p}_{\text{Y-STR, upper}}} \right)^{\delta_y} \times \left( \frac{1}{\hat{p}_{\text{mtDNA, upper}}} \right)^{\delta_m} \times \left( LR_{\text{SNP}} \right)^{\delta_s}$$

$$\log_{10}(LR_{\text{Joint}}) = \log_{10}(LR_{\text{Auto}}) + \delta_y \log_{10}\left(\frac{1}{\hat{p}_{\text{Y-STR}}}\right) + \delta_m \log_{10}\left(\frac{1}{\hat{p}_{\text{mtDNA}}}\right) + \delta_s \log_{10}(LR_{\text{SNP}})$$

where $\delta_y, \delta_m, \delta_s \in \{0, 1\}$ are binary data availability indicator variables.

### 43.2 Interpol DVI Standing Committee Decision Boundaries & Judicial Criteria

$$\text{Decision Tier} = \begin{cases} \text{DEFINITIVE\_IDENTIFICATION}, & LR_{\text{Joint}} \ge 10^6 \quad (\log_{10} LR \ge 6.0) \\ \text{PROBABLE\_MATCH}, & 10^4 \le LR_{\text{Joint}} < 10^6 \quad (4.0 \le \log_{10} LR < 6.0) \\ \text{INCONCLUSIVE}, & 10^{-2} < LR_{\text{Joint}} < 10^4 \quad (-2.0 < \log_{10} LR < 4.0) \\ \text{EXCLUSION}, & LR_{\text{Joint}} \le 10^{-2} \quad (\log_{10} LR \le -2.0) \end{cases}$$

#### Statutory Judicial Action Criteria:
1. **Definitive Identification ($LR \ge 10^6$):** Sufficient forensic proof for standalone legal identification in court.
2. **Probable Match ($10^4 \le LR < 10^6$):** Mandates secondary corroboration (forensic odontology, surgical serial numbers, physical marks).
3. **Inconclusive ($10^{-2} < LR < 10^4$):** Insufficient data; requires additional STR amplification or NGS SNP panel testing.
4. **Exclusion ($LR \le 10^{-2}$):** Definite exclusion from the missing person reference pedigree.

### 43.3 $N \times M$ Cross-Reconciliation Matrix & Posterior Ranking

$$\text{Odds} = LR_{\text{Joint}} \times \frac{P(H_p)}{1 - P(H_p)}, \quad P(H_p \mid E) = \frac{\text{Odds}}{1 + \text{Odds}}$$

---

## 44. Ancient DNA & Degraded Forensic SNP Damage Kinetics / Human ID (HID) Engine (Module 10)

For heavily degraded skeletal remains where STR amplification fails due to extensive fragmentation ($> 100\text{ bp}$ dropout), short-amplicon ($40–70\text{ bp}$) SNP micro-multiplex panels are employed.

### 44.1 Post-Mortem DNA Damage Kinetics (MapDamage / Briggs Model)

Cytosine deamination ($C \to T$ on 5' single-stranded overhangs, $G \to A$ on 3' overhangs) damage probability at distance $k$ from termini:

$$\delta_k = \delta_0 (1 - \delta_0)^{k-1} \quad \text{or} \quad \delta_k = \delta_0 \exp(-\alpha (k - 1))$$

where $\delta_0 \in [0.15, 0.35]$ is the terminal overhang deamination fraction (default $\delta_0 = 0.25$) and $\alpha = 0.10\text{ bp}^{-1}$.

Exponential fragmentation length distribution:

$$P(L) = \lambda e^{-\lambda (L - L_{\min})} \quad \text{for } L \ge L_{\min}$$

$$F(L) = 1 - e^{-\lambda (L - L_{\min})}$$

$$\bar{L} = \frac{1}{\lambda} + L_{\min}$$

where $L_{\min} = 30.0\text{ bp}$, $\lambda = 0.025 \implies \bar{L} = 70.0\text{ bp}$. The amplicon dropout risk at $100\text{ bp}$ is:

$$\text{CDF}(100\text{ bp}) = 1 - e^{-0.025 \times (100 - 30)} = 1 - e^{-1.75} \approx 0.8262 \quad (82.6\%)$$

### 44.2 Low-Coverage Forensic SNP Genotype Likelihood ($GL$)

For an assayed SNP locus with $R$ read observations $D = \{(b_r, k_r)\}_{r=1}^R$:

$$P(D \mid G) = \prod_{r=1}^R \left[ \sum_{g \in G} P(g \mid G) \cdot \left( (1 - e_r - d_r) I(b_r = g) + (e_r + d_r) I(b_r \neq g) \right) \right]$$

where $e_r$ is the base sequencing error rate ($0.01$) and $d_r = \delta_{k_r}$ is the position-dependent MapDamage deamination probability.

Posterior genotype probability:

$$P(G \mid D) = \frac{P(D \mid G) P(G)}{\sum_{G' \in \{AA, AB, BB\}} P(D \mid G') P(G')}$$

Cumulative micro-multiplex Forensic Likelihood Ratio across $M$ loci:

$$LR_{\text{SNP}} = \prod_{m=1}^M \frac{P(D_m \mid G_{S, m})}{\sum_{G \in \{AA, AB, BB\}} P(D_m \mid G) P(G)}$$

$$\log_{10} LR_{\text{SNP}} = \sum_{m=1}^M \log_{10} LR_m$$

### 44.3 Skeletal Remains Degradation Index ($DI$) & LCN Stochastic Thresholds

$$DI = \frac{\text{RFU}_{\text{small}}}{\text{RFU}_{\text{large}}}$$

$$\text{Technology Recommendation} = \begin{cases} \text{MICRO\_SNP\_PANEL\_40\_70BP}, & DI \ge 2.5 \quad (\text{Severe degradation, complete }>300\text{ bp dropout}) \\ \text{MINI\_STR}, & 1.5 \le DI < 2.5 \quad (\text{Moderate degradation}) \\ \text{STANDARD\_STR}, & DI < 1.5 \quad (\text{Low degradation}) \end{cases}$$

$$\text{LCN Stochastic Warning Active} \iff \text{DNA Input} < 100\text{ pg} \quad \lor \quad \text{Mean RFU} < 150$$

---

## 45. HIrisPlex-S 41-SNP DNA Pigmentation Forensics & Multinomial Softmax MLR (Module 11)

The HIrisPlex-S system (VISAGE Consortium / Erasmus MC) simultaneously predicts eye color (3 classes), hair color (4 classes + shade intensity), and skin phototype (5 ordinal Fitzpatrick classes) via Multinomial Logistic Regression (MLR) with Softmax normalization.

### 45.1 Multinomial Logistic Regression & Softmax Normalization

For a phenotype trait $Y$ with $K$ mutually exclusive categories ($K$ being reference):

$$\ln \left( \frac{P(Y = k \mid \mathbf{X})}{P(Y = K \mid \mathbf{X})} \right) = \beta_{k0} + \sum_{i=1}^p \beta_{ki} X_i \quad \text{for } k \in \{1, \dots, K-1\}$$

$$P(Y = k \mid \mathbf{X}) = \frac{\exp \left( \beta_{k0} + \sum_{i=1}^p \beta_{ki} X_i \right)}{1 + \sum_{l=1}^{K-1} \exp \left( \beta_{l0} + \sum_{i=1}^p \beta_{li} X_i \right)}$$

$$P(Y = K \mid \mathbf{X}) = \frac{1}{1 + \sum_{l=1}^{K-1} \exp \left( \beta_{l0} + \sum_{i=1}^p \beta_{li} X_i \right)}$$

#### Mandatory Sum-to-Unity Invariant:
$$\left| \left( \sum_{k=1}^K P(Y = k \mid \mathbf{X}) \right) - 1.0 \right| \le 1.0 \times 10^{-6}$$

### 45.2 Tri-Trait Mathematical Parameterization

1. **IrisPlex (Eye Color - 6 Loci):**
   - Reference: Brown ($K=3$).
   - Intercepts: $\beta_{\text{Blue}, 0} = -2.815, \beta_{\text{Interm}, 0} = -1.412$.
   - Primary Loci: `HERC2 rs12913832` (C: $+4.512 / +1.895$), `OCA2 rs1800407` (T: $-0.812 / +0.341$), `SLC24A4 rs12896399`, `SLC45A2 rs16891982`, `TYR rs1393350`, `IRF4 rs12203592`.

2. **HIrisPlex (Hair Color - 22 Loci):**
   - Reference: Brown ($K=4$).
   - Intercepts: $\beta_{\text{Blond}, 0} = -1.920, \beta_{\text{Red}, 0} = -3.450, \beta_{\text{Black}, 0} = -2.110, \beta_{\text{Shade}, 0} = +0.125$.
   - Primary Loci: `MC1R rs1805007` (T: Red $+4.820$), `MC1R rs1805008` (T: Red $+4.650$), `MC1R rs1805009` (C: Red $+4.120$), `HERC2 rs12913832` (C: Blond $+2.850$, Black $-3.100$).

3. **HIrisPlex-S (Skin Phototype - 36 Loci):**
   - Reference: Intermediate Type III/IV ($K=5$).
   - Intercepts: $\beta_{\text{VeryPale}, 0} = -2.150, \beta_{\text{Pale}, 0} = -1.100, \beta_{\text{Dark}, 0} = -2.850, \beta_{\text{DarkBlack}, 0} = -5.200$.
   - Primary Loci: `SLC24A5 rs1426654` (A: VeryPale $+2.450$, Dark $-3.950$), `SLC45A2 rs16891982` (G: VeryPale $+2.120$, Dark $-3.120$), `MFSD12 rs10424031` (A: Dark $+2.150$, DarkBlack $+4.850$).

### 45.3 Missingness Imputation & Uncertainty Scaling Penalty

For degraded forensic profiles with missing loci count $N_{\text{missing}}$ ($M = N_{\text{missing}} / N_{\text{total}}$):

$$X_i^* = 2 \cdot p_i \quad (\text{Global mean dosage imputation})$$

$$P_{\text{adjusted}}(Y = k) = \frac{\exp \left( \frac{\hat{L}_k}{\sqrt{1 + \lambda \cdot M}} \right)}{\sum_{l=1}^K \exp \left( \frac{\hat{L}_l}{\sqrt{1 + \lambda \cdot M}} \right)} \quad (\lambda = 0.35)$$





