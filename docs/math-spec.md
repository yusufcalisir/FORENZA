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

### 2.4 Dirichlet Compound Multinomial (Polya-Eggenberger) Sampling Distribution
To model allelic sampling variance in structured subpopulations with coancestry parameter $\theta$, the compound likelihood is evaluated in log-gamma space:

$$\ln P(\mathbf{n} \mid \boldsymbol{\alpha}, \theta) = \ln \Gamma\left(\kappa\right) - \ln \Gamma\left(N + \kappa\right) + \sum_{i=1}^K \left[ \ln \Gamma\left(n_i + \kappa p_i\right) - \ln \Gamma\left(\kappa p_i\right) \right], \quad \kappa = \frac{1-\theta}{\theta}$$

### 2.5 Weir & Cockerham (1984) Unbiased ANOVA $\hat{\theta}$ / $F_{st}$ Estimator
Decomposes total allelic variance across $r$ sub-populations into Mean Square Between Populations (MSP) and Mean Square Within Populations (MSG):

$$\hat{\theta} = \frac{\text{MSP} - \text{MSG}}{\text{MSP} + (n_c - 1)\text{MSG}}, \quad n_c = \frac{1}{r - 1} \left( N - \frac{\sum_{k=1}^r n_k^2}{N} \right)$$

### 2.6 Curran & Buckleton (2007) Multi-Locus Weighted Estimator
Combines locus-specific variance components across all $L=24$ loci:

$$\bar{\theta} = \frac{\sum_{l=1}^L (\text{MSP}_l - \text{MSG}_l)}{\sum_{l=1}^L [\text{MSP}_l + (n_{c,l} - 1)\text{MSG}_l]}$$

### 2.7 Massively Parallel Sequencing (MPS/NGS) STR Isoallele Formalism & SE33 Deletion Kinetics

#### 1. Isoallele Expansion & Information Gain
In MPS STR sequencing, identical length alleles $A_i$ (e.g. CE allele 18 or 27.2 in SE33) resolve into $K$ distinct sequence isoalleles $\{s_{i,1}, s_{i,2}, \dots, s_{i,K}\}$:

$$p_i^{\text{CE}} = \sum_{k=1}^K p(s_{i,k}), \quad p(s_{i,k}) \le p_i^{\text{CE}}$$

The resulting information gain multiplier on Likelihood Ratio ($LR$) is given by:

$$LR_{\text{gain}} = \frac{LR_{\text{MPS}}}{LR_{\text{CE}}} = \frac{p_i^{\text{CE}} \cdot p_j^{\text{CE}}}{p(s_{i,a}) \cdot p(s_{j,b})} \ge 1.0$$

Across hyper-polymorphic loci such as SE33, $LR_{\text{gain}}$ reaches up to $41.6\times$ (single locus) and $> 1000\times$ in multi-locus mixture deconvolution.

#### 2. SE33 4-bp Flanking Deletion Auto-Reconciliation
Due to 4-bp flanking deletions (`rs369314007 [TTTT/-]` and `rs1371483225 [TCTT/-]`), short-amplicon MPS assays sequence across the deleted region, shifting raw repeat counts by $+1.0$:

$$\text{Call}_{\text{CE}} = \begin{cases} \text{Call}_{\text{MPS}} - 1.0 & \text{if } \text{rs369314007 or rs1371483225 deletion detected} \\ \text{Call}_{\text{MPS}} & \text{otherwise} \end{cases}$$

#### 3. Syntenic Linkage Constraint (D6S1043 – SE33)
On chromosome 6q, D6S1043 and SE33 are separated by 3.46 Mb with recombination fraction $\theta = 0.0440$. In kinship testing, multiplying single-locus LRs violates independence:

$$\text{LR}_{\text{joint}}(D6S1043, SE33) = \max(\text{LR}_{D6S1043}, \text{LR}_{SE33}) \quad \text{(Safe Conservative Fallback)}$$

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

## 4. Stochastic Modeling: Dropout, Drop-in & Heterozygote Balance (Module 1.4)

In low-template DNA analysis ($T < 100\text{ pg}$ or peak heights $< \text{ST} = 150\text{ RFU}$), stochastic phenomena (allelic dropout, sporadic drop-in, and severe peak imbalance) are modeled verbatim from Pillar 1 Research §4 and Curran & Gill (2016).

### 4.1 Calibrated Logistic Allele Dropout Model ($P(D \mid x)$)

Dropout probability $P(D \mid x)$ is evaluated via calibrated sigmoid functions:

$$P(D \mid x) = \frac{1}{1 + \exp\left(-(\beta_0 + \beta_1 x)\right)}$$

1. **RFU-Based Calibration ($x = \text{RFU}$):**
   $$\beta_0 = +2.50, \quad \beta_1 = -0.025\text{ RFU}^{-1}$$
   - $P(D \mid 50\text{ RFU}) = 77.73\%$
   - $P(D \mid 100\text{ RFU}) = 50.00\%$
   - $P(D \mid 150\text{ RFU}) = 22.27\%$
   - Critical $1\%$ threshold: $x_{\text{crit}} = \frac{-\ln(99) - \beta_0}{\beta_1} = 283.81\text{ RFU}$.

2. **DNA Mass-Based Calibration ($x = \text{pg}$):**
   $$\beta_0 = +3.20, \quad \beta_1 = -0.080\text{ pg}^{-1}$$
   - $P(D \mid 15\text{ pg}) = 88.08\%$ (Single-cell limit)
   - $P(D \mid 40\text{ pg}) = 50.00\%$ (Half-dropout template)
   - $P(D \mid 100\text{ pg}) = 0.82\%$ (Standard SWGDAM threshold)
   - Critical $1\%$ threshold: $x_{\text{crit}} = 97.44\text{ pg}$.

3. **Amplicon Size Dependent Degradation Scaling ($x = T\text{ pg}, \text{bp}$):**
   $$P(D \mid T, \text{bp}) = \frac{1}{1 + \exp\left(-(\beta_0 + \beta_1 T + \beta_s (\text{bp} - 100))\right)}, \quad \beta_s = 0.008\text{ bp}^{-1}$$

### 4.2 Discrete Poisson Allele Drop-in Model ($P(C = k)$)

Sporadic drop-in allele count per locus follows a discrete Poisson distribution:

$$P(C = k \mid \lambda_C) = \frac{\lambda_C^k e^{-\lambda_C}}{k!}, \quad \lambda_C = 0.020\text{ per locus}$$

- $P(C = 0) = 0.98019867$, $P(C = 1) = 0.01960397$, $P(C = 2) = 0.00019604$.
- **24-Locus Clean Profile Invariant:**
  $$P(C_{\text{total}} = 0) = \prod_{l=1}^{24} P(C_l = 0) = e^{-24 \times 0.020} = e^{-0.48} \approx 0.618783$$

### 4.3 Truncated Exponential Drop-in Peak Height Density ($f(h_C)$)

Drop-in fluorescence signals above the Analytical Threshold ($\text{AT} = 50.0\text{ RFU}$) follow a truncated exponential PDF:

$$f(h_C) = \begin{cases} \lambda_h \exp\left(-\lambda_h (h_C - \text{AT})\right) & \text{for } h_C \ge \text{AT} \\ 0.0 & \text{for } h_C < \text{AT} \end{cases}, \quad \lambda_h = 0.015\text{ RFU}^{-1}$$

- Expected Drop-in Peak Height: $E[h_C] = \text{AT} + \frac{1}{\lambda_h} = 50.0 + 66.667 = 116.667\text{ RFU}$.

### 4.4 Heterozygote Peak Balance ($H_b$) & Stochastic Quality Flags

For a heterozygous genotype with peak heights $h_1, h_2$:

$$H_b = \frac{\min(h_1, h_2)}{\max(h_1, h_2)}$$

A 3-tier stochastic quality flag is triggered if:
1. $H_b < 0.60$ (Severe peak height imbalance).
2. $h_{\min} < \text{ST} = 150.0\text{ RFU}$ (Sub-stochastic threshold peak).
3. Any peak $< \text{AT} = 50.0\text{ RFU}$ (Sub-analytical threshold peak).

If flagged, single-peak loci are masked with an allelic dropout wildcard $[0]$ to prevent false homozygosity calls.

### 4.5 Curran-Gill 4-State Markov Observation Model

Under prosecution proposition $H_p$ (suspect with genotype $G_S = (A_1, A_2)$ is contributor):
- **Scenario A (Both Sister Alleles Present):** $P(E \mid H_p) = (1 - P(D))^2 \cdot (1 - \lambda_C)$
- **Scenario B (Single Sister Allele Dropout):** $P(E \mid H_p) = 2 P(D) (1 - P(D)) \cdot (1 - \lambda_C)$
- **Scenario C (Double Sister Allele Dropout):** $P(E \mid H_p) = P(D)^2 \cdot (1 - \lambda_C)$
- **Scenario D (Sporadic Drop-in Detected):** $P(E \mid H_p) = 2 P(D) (1 - P(D)) \cdot \lambda_C f(h_{\text{extra}})$

Under defense proposition $H_d$ (unrelated contributor from population with coancestry $\theta$):
$$P(E \mid H_d) = P(G_S \mid \theta) = \frac{2 [\theta + (1-\theta)p_1][\theta + (1-\theta)p_2]}{(1+\theta)(1+2\theta)}$$

### 4.6 Substrate Physical Transfer & Recovery Matrix

$$\text{Recovered Mass: } m_{\text{rec}} = m_{\text{in}} \cdot \eta$$

| Substrate ID | Name | Recovery Efficiency ($\eta$) | Porosity Class |
| :--- | :--- | :---: | :--- |
| `SMOOTH_NON_POROUS` | Smooth Non-Porous (Glass / Metal) | $0.60$ | Non-Porous |
| `TEXTURED_NON_POROUS` | Textured Non-Porous (Gun Grip / Steering Wheel) | $0.40$ | Textured |
| `POROUS_FABRIC` | Porous Fabric (Cotton / Denim) | $0.20$ | Porous |
| `ROUGH_WOOD` | Rough Wood / Brick | $0.15$ | Highly Porous |

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

### 6.6 Tippett Calibration Curves, Empirical ROC & Cllr Metric (Module 05)

#### 6.6.1 Empirical Complementary Cumulative Distribution Functions (ECCDF)
For $N_{H_p}$ true donor pairs and $N_{H_d}$ non-donor pairs:

$$\text{Tippett}_{H_p}(x) = P\!\left(\log_{10}LR \ge x \mid H_p\right) = \frac{1}{N_{H_p}} \sum_{i=1}^{N_{H_p}} \mathbb{I}\left(\log_{10} LR_i \ge x\right)$$

$$\text{Tippett}_{H_d}(x) = P\!\left(\log_{10}LR \ge x \mid H_d\right) = \frac{1}{N_{H_d}} \sum_{j=1}^{N_{H_d}} \mathbb{I}\left(\log_{10} LR_j \ge x\right)$$

**Monotonicity Invariant:**
$$\forall x_1 < x_2 \implies \text{Tippett}_{H_p}(x_1) \ge \text{Tippett}_{H_p}(x_2) \quad \text{and} \quad \text{Tippett}_{H_d}(x_1) \ge \text{Tippett}_{H_d}(x_2)$$

#### 6.6.2 Royall Misleading Evidence Inequality
Under the defense hypothesis $H_d$, the probability of obtaining misleading evidence of strength $k$ satisfies the theoretical bound (Royall 1997):

$$P\left(LR \ge k \mid H_d\right) \le \frac{1}{k} \implies P\left(\log_{10} LR \ge 6.0 \mid H_d\right) \le 10^{-6}$$

#### 6.6.3 Error Rates & Discrimination Power
At the neutral decision boundary ($\tau = 0.0, LR = 1.0$):
- **False Positive Rate:** $\text{FPR}_{\text{neutral}} = P(\log_{10} LR > 0 \mid H_d) = \text{Tippett}_{H_d}(0^+)$
- **False Negative Rate:** $\text{FNR}_{\text{neutral}} = P(\log_{10} LR < 0 \mid H_p) = 1 - \text{Tippett}_{H_p}(0)$
- **Discrimination Power:** $D_{\text{power}} = 1 - \text{FPR}_{\text{neutral}} - \text{FNR}_{\text{neutral}} \in [0, 1]$

#### 6.6.4 Non-Parametric ROC Analysis & Mann-Whitney U AUC
The area under the Receiver Operating Characteristic curve is calculated via exact pair comparisons:

$$\text{AUC} = \frac{1}{N_{H_p} N_{H_d}} \sum_{i=1}^{N_{H_p}} \sum_{j=1}^{N_{H_d}} \left[ \mathbb{I}\left(\log_{10} LR_i^{(H_p)} > \log_{10} LR_j^{(H_d)}\right) + 0.5 \cdot \mathbb{I}\left(\log_{10} LR_i^{(H_p)} = \log_{10} LR_j^{(H_d)}\right) \right]$$

- Single-source pristine 24-locus benchmark requirement: $\text{AUC} \ge 0.9990$.

#### 6.6.5 Information-Theoretic Log-Likelihood Ratio Cost ($C_{\text{llr}}$)
Measures the overall information penalty of the probabilistic genotyping output (Brümmer & du Preez 2006, Ramos & Gonzalez-Rodriguez 2013):

$$C_{\text{llr}} = \frac{1}{2 \cdot N_{H_p}} \sum_{i=1}^{N_{H_p}} \log_2\left(1 + 10^{-\log_{10} LR_i}\right) + \frac{1}{2 \cdot N_{H_d}} \sum_{j=1}^{N_{H_d}} \log_2\left(1 + 10^{+\log_{10} LR_j}\right)$$

**PAV Isotonic Regression Decomposition:**
$$C_{\text{llr}} = C_{\text{llr}}^{\min} + C_{\text{llr}}^{\text{cal}}$$
- $C_{\text{llr}}^{\min}$: Minimum achievable cost after optimal monotonic probability calibration (discrimination loss).
- $C_{\text{llr}}^{\text{cal}} \ge 0$: Calibration loss / entropy penalty due to miscalibration.
- Benchmark quality standards: $C_{\text{llr}} < 0.05$ (Excellent), $C_{\text{llr}} < 0.20$ (Acceptable).

#### 6.6.6 ENFSI (2017) Dynamic 7-Tier Verbal Reporting Scale
Likelihood ratios are translated into standardized evaluative statements across 7 positive and negative tiers:
- Tier 0: Inconclusive / Neutral ($\log_{10} LR = 0.0$)
- Tier 1: Weak Support ($0 < \log_{10} LR \le 1.0$)
- Tier 2: Moderate Support ($1.0 < \log_{10} LR \le 2.0$)
- Tier 3: Moderately Strong Support ($2.0 < \log_{10} LR \le 4.0$)
- Tier 4: Strong Support ($4.0 < \log_{10} LR \le 6.0$)
- Tier 5: Very Strong Support ($6.0 < \log_{10} LR \le 9.0$)
- Tier 6: Extremely Strong Support ($\log_{10} LR > 9.0$)

### 6.7 Massively Parallel Sequencing (MPS/NGS) STR Sequence Analysis & Isoallele Expansion (Module 1.6)

#### 6.7.1 Sequence-Level Isoallele Resolution & LR Information Gain
For any STR locus $l$, massively parallel sequencing resolves identical-length capillary electrophoresis (CE) size calls into $K$ distinct sequence-level isoalleles $\{s_{l,1}, s_{l,2}, \dots, s_{l,K}\}$:

$$p(a_l) = \sum_{k=1}^K p(s_{l,k}), \quad \text{where } \text{Length}(s_{l,k}) = a_l$$

The single-locus likelihood ratio under single-source inclusion $H_p: G = (s_1, s_2)$ vs $H_d: G \sim \text{Pop}$ increases by an information gain factor:

$$LR_{\text{MPS}} = \frac{1}{2 \cdot p(s_1) p(s_2)} \ge \frac{1}{2 \cdot p(a_1) p(a_2)} = LR_{\text{CE}}$$

$$LR_{\text{gain}} = \frac{LR_{\text{MPS}}}{LR_{\text{CE}}} = \frac{p(a_1) p(a_2)}{p(s_1) p(s_2)} \ge 1.0$$

For hyper-polymorphic loci such as SE33, $LR_{\text{gain}}$ reaches up to $41.6\times$.

#### 6.7.2 SE33 4-bp Flanking Deletion Kinetics & Legacy CE Reconciliation
Two standard 3' flanking deletions occur at SE33:
1. `rs369314007 [delTTTT]` (4-bp deletion, frequency $\sim 2.1\%$)
2. `rs1371483225 [delTCTT]` (4-bp deletion, frequency $\sim 0.3\%$)

Because legacy CE amplicon sizing incorporates the flanking deletion into the total base-pair length, an allele containing either deletion appears 1 repeat unit (4 bp) shorter in CE sizing relative to naive MPS motif counting. FORENZA enforces the automated reconciliation invariant:

$$\text{Allele}_{\text{CE}} = \text{Allele}_{\text{MPS\_Motif}} + \Delta_{\text{indel}}, \quad \Delta_{\text{indel}} = \begin{cases} -1.0 & \text{if deletion present} \\ 0.0 & \text{otherwise} \end{cases}$$

#### 6.7.3 Syntenic Linkage Constraint ($D6S1043 - SE33$)
On chromosome 6q, D6S1043 and SE33 are separated by 3.46 Mb with recombination fraction $\theta = 0.0440$. In kinship testing, multiplying single-locus likelihood ratios directly violates independence. FORENZA enforces the linkage discount or defaults to the more informative marker (SE33):

$$LR_{\text{linked}} = \max\left( LR_{\text{SE33}}, (1 - \theta) \cdot LR_{\text{SE33}} + \theta \cdot LR_{\text{D6S1043}} \right)$$

---

### 6.8 Machine Learning STR Calling & Fragsifier Ensemble Pre-Filtering (Module 1.7)

#### 6.8.1 24-Dimensional Morphological & Sequence Feature Space ($\mathbf{x} \in \mathbb{R}^{24}$)
FORENZA extracts a 24-dimensional feature vector $\mathbf{x}$ for every raw electropherogram peak and MPS sequence cluster:

1. **Peak Morphology & Signal Kinetics ($x_1 - x_6$):** Peak height ($h$), peak area ($A$), height-to-area sharpness ratio ($h/A$), Signal-to-Noise Ratio ($\text{SNR} = (h - \mu_{\text{baseline}})/\sigma_{\text{noise}}$), skewness ($\gamma_1$), and $\text{FWHM}$.
2. **Stutter & Artifact Proximity ($x_7 - x_{12}$):** Relative base-pair distance ($\Delta\text{bp} = \text{pos} - \text{pos}_{\text{major}}$), back-stutter indicator ($I_{-1}$), forward-stutter indicator ($I_{+1}$), double back-stutter indicator ($I_{-2}$), non-template $+A$ indicator ($I_{+A}$), and observed stutter ratio ($SR_{\text{obs}} = h / h_{\text{major}}$).
3. **Sequence Complexity & Entropy ($x_{13} - x_{18}$):** Base-2 Shannon entropy ($H(S) = -\sum p_i \log_2 p_i$), longest homopolymer run ($L_{\text{homo}}$), GC fraction ($f_{\text{GC}}$), hexamer motif frequency ($f_{\text{hex}}$), flanking SNP distance ($D_{\text{flank}}$), and spacer count ($N_{\text{spacer}}$).
4. **Mixture Dynamics & Threshold Margin ($x_{19} - x_{24}$):** Heterozygote balance ($H_b = h_{\text{minor}}/h_{\text{major}}$), spectral pull-up ratio ($P_{\text{pull}}$), locus amplification efficiency ($\eta_l$), degradation index ($DI$), minor contributor prior ($\hat{M}_c$), and analytical margin ($M_{\text{AT}} = (h - \text{AT})/\text{AT}$).

#### 6.8.2 Fragsifier Random Forest Ensemble & Gini Impurity Splitting
An ensemble of $B = 500$ de-correlated decision trees $\{T_1, \dots, T_B\}$ classifies candidate signals across 7 biophysical categories:

$$P(c_k \mid \mathbf{x}) = \frac{1}{B} \sum_{b=1}^B I\left( T_b(\mathbf{x}) = c_k \right), \quad c_k \in \mathcal{C}$$

$$\mathcal{C} = \{\text{TRUE\_ALLELE}, \text{BACK\_STUTTER}, \text{FORWARD\_STUTTER}, \text{MINUS\_2BP}, \text{PLUS\_A}, \text{PULL\_UP}, \text{BASE\_NOISE}\}$$

The split criterion minimizes Gini Impurity:

$$I_G(S) = 1 - \sum_{k=1}^7 p_k^2$$

#### 6.8.3 Non-Invasive MCMC-MH Mixture Search Space Optimization
The ML pre-filter culls artifacts upstream of continuous Markov Chain Monte Carlo deconvolution. The continuous Gamma/Log-Normal likelihood function $\mathcal{L}(E \mid \Theta)$ remains unaltered, while the combinatorial candidate genotype space $\mathcal{G}$ is pruned from $O(2^N)$ to $O(2^{N_{\text{clean}}})$, reducing Markov chain burn-in cycles by $\sim 40\%$ and guaranteeing Gelman-Rubin convergence $\hat{R} < 1.02$.

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

### 9.1 Y-STR 27-Locus Lineage Forensics & Kinship Engine (Module 06 / 2.1)

#### 9.1.1 Y-FILER Plus 27-Locus Multiplex Registry
The panel evaluates 25 marker systems encompassing 27 target amplicons:
- **19 Single-Copy Standard Forensic Loci:** `DYS19`, `DYS389I`, `DYS389II`, `DYS390`, `DYS391`, `DYS392`, `DYS393`, `DYS437`, `DYS438`, `DYS439`, `DYS448`, `DYS456`, `DYS458`, `DYS635`, `YGATAH4`, `DYS460`, `DYS481`, `DYS533` ($\mu_l \in [0.000375, 0.00870]$).
- **2 Multi-Copy Duplicated Systems (4 targets):** `DYS385a/b` (Standard, $\mu=0.0023$), `DYF387S1a/b` (Rapidly Mutating, $\mu=0.0160$).
- **5 Single-Copy Rapidly Mutating (RM) Loci (6 RM systems / 7 targets):** `DYS570` ($\mu=0.0120$), `DYS576` ($\mu=0.0140$), `DYS627` ($\mu=0.0110$), `DYS518` ($\mu=0.0180$), `DYS449` ($\mu=0.0120$).

#### 9.1.2 Exact Clopper-Pearson 95% Binomial Upper Confidence Limit ($p_{\text{upper}}$)
For haplotype observed $k$ times in reference database $N$ under significance level $\alpha = 0.05$:

**Case 1: Unobserved Haplotype ($k = 0$):**
$$p_{\text{upper}} = 1 - \alpha^{\frac{1}{N+1}} = 1 - (0.05)^{\frac{1}{N+1}}$$
- In YHRD Global Database ($N=385,000$): $p_{\text{upper}} = 7.7810723 \times 10^{-6}$ ($1 \text{ in } 128,517$).
- In Regional Metapopulation ($N=38,500$): $p_{\text{upper}} = 7.7806180 \times 10^{-5}$ ($1 \text{ in } 12,852$).

**Case 2: Observed Haplotype ($k > 0$):**
Exact Snedecor $F$-distribution quantile with degrees of freedom $d_1 = 2(k+1)$ and $d_2 = 2(N-k)$:
$$p_{\text{upper}} = \frac{(k+1) F_{1-\alpha/2}(2(k+1), 2(N-k))}{(N-k) + (k+1) F_{1-\alpha/2}(2(k+1), 2(N-k))}$$

#### 9.1.3 Brenner / Surveyor Subpopulation Coancestry Frequency Correction ($p_{\text{Brenner}}$)
Adjusts for subpopulation structure and common ancestry using Wright's $\theta \in [0.01, 0.05]$:
$$p_{\text{Brenner}} = \frac{k + \theta}{N + \theta}, \quad LR_{\text{Brenner}} = \frac{1}{p_{\text{Brenner}}}$$

#### 9.1.4 Biophysical Decoupling of Nested Repeat System DYS389
Because the DYS389II PCR amplicon physically encloses the DYS389I locus:
$$\text{DYS389.2}_{\text{pure}} = \text{DYS389II} - \text{DYS389I}$$
Evaluating $\text{DYS389.2}_{\text{pure}}$ ensures that a single mutation at DYS389I is not falsely double-counted as two independent mutations.

#### 9.1.5 Stepwise Mutation Model (SMM) & Paternal Likelihood Ratio ($LR_{\text{paternal}}$)
For $m$ father-to-son meioses separating two male individuals across 25 systems:

**Single Locus Transition Probability:**
$$P(y_{B,l} \mid y_{A,l}, m) = \begin{cases}
(1 - \mu_l)^m & \text{if } y_{B,l} = y_{A,l} \text{ (Identity)} \\
\frac{1}{2} \left[1 - (1 - \mu_l)^m\right] (1 - r_l) r_l^{|y_B - y_A| - 1} & \text{if } |y_{B,l} - y_{A,l}| \ge 1 \text{ (Stepwise Mutation)}
\end{cases}$$
where $\mu_l$ is locus mutation rate and $r_l \in [0.75, 0.96]$ is the single-step geometric contraction parameter.

**Multilocus Paternal Likelihood Ratio:**
$$LR_{\text{paternal}} = \frac{\prod_{l=1}^{25} P(y_{B,l} \mid y_{A,l}, m)}{p_{\text{upper}}}$$

**Definitive Exclusion Rule:** If standard locus mismatches $\ge 3$ or total mutation distance $\ge 5$ repeat steps:
$$LR_{\text{paternal}} = 0.0, \quad \log_{10} LR_{\text{paternal}} = -300.0$$

#### 9.1.6 Minimum Male Contributor Count ($N_{\text{male}}$)
From observed peak counts $n_{\text{alleles}, l}$ across single-copy and multi-copy loci:
$$N_{\text{male}} = \max\left( \max_{l \in \text{SingleCopy}} n_{\text{alleles}, l}, \; \max_{l \in \text{MultiCopy}} \left\lceil \frac{n_{\text{alleles}, l}}{2} \right\rceil \right)$$

#### 9.1.7 Bayesian Y-DNA Haplogroup Prediction Simplex
Evaluates distance to 16 major ISOGG modal signatures $\mathbf{M}_k$ via Softmax temperature normalization:
$$P(H_k \mid Y) = \frac{\exp\left(-\frac{1}{2\sigma^2} \sum_{l=1}^L |y_l - M_{k,l}|^2\right)}{\sum_{j=1}^{16} \exp\left(-\frac{1}{2\sigma^2} \sum_{l=1}^L |y_l - M_{j,l}|^2\right)}, \quad \sum_{k=1}^{16} P(H_k \mid Y) = 1.000000$$

#### 9.1.8 ISFG (2020) Patrilineal Lineage Legal Reporting Shield
Y-STR matches provide evidence that the DNA originates from the suspect **or any of his patrilineal male relatives** sharing the same unbroken paternal lineage. Reporting statements strictly include active shields against Prosecutor's Fallacy transposition.

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
The FORENZA Master OS forms a 7-pillar topological graph $\mathcal{G}_{\text{OS}} = (\mathcal{V}, \mathcal{E})$ with 35 subsystem nodes:

$$\mathcal{V} = \mathcal{V}_{\text{Ingest}} \cup \mathcal{V}_{\text{Inference}} \cup \mathcal{V}_{\text{Ledger}} \cup \mathcal{V}_{\text{QC}} \cup \mathcal{V}_{\text{Review}} \cup \mathcal{V}_{\text{GeoFusion}} \cup \mathcal{V}_{\text{Reporting}}$$

### 34.2 End-to-End Joint System Entropy Reduction ($\Delta \mathcal{H}_{\text{system}}$)
For initial uninformative evidence entropy $\mathcal{H}_0$ and post-inference joint likelihood state $\mathcal{H}_{\text{joint}}$:

$$\Delta \mathcal{H}_{\text{system}} = \mathcal{H}_0 - \sum_{k=1}^{35} \mathcal{I}(X_k; Y_{\text{verdict}}) \ge 0$$

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

---

## 46. 55-SNP AIM Biogeographic Ancestry (BGA) System & Live GIS Geolocation (Module 12)

The 55-AIM BGA framework estimates continental admixture proportions across 5 major biogeographic clusters (**EUR**, **AFR**, **EAS**, **SAS**, **AMR**) using validated Ancestry Informative Markers (Kidd et al. / Seldin et al.) and projects geographic origins onto a 3D spherical coordinate space with 95% bivariate confidence ellipses.

### 46.1 Bayesian Posterior Admixture Estimation

For observed genotype profile $G = \{g_1, \dots, g_N\}$ across $N$ informative SNP markers:

$$\ln L(G \mid C_j) = \sum_{m=1}^N \ln P(g_m \mid p_{m, j})$$

where Hardy-Weinberg genotype probabilities are:

$$P(g_m \mid p_{m, j}) = \begin{cases} p_{m, j}^2, & g_m = 2 \quad (\text{Homozygous Alt}) \\ 2 p_{m, j} (1 - p_{m, j}), & g_m = 1 \quad (\text{Heterozygous}) \\ (1 - p_{m, j})^2, & g_m = 0 \quad (\text{Homozygous Ref}) \end{cases}$$

Under a uniform Dirichlet prior ($\alpha_j = 1.0$), posterior admixture proportions $\mathbf{q} = (q_{\text{EUR}}, q_{\text{AFR}}, q_{\text{EAS}}, q_{\text{SAS}}, q_{\text{AMR}})^T$ are recovered via Softmax:

$$q_j = \frac{\exp(\ln L(G \mid C_j) - \max_k \ln L(G \mid C_k))}{\sum_{l=1}^5 \exp(\ln L(G \mid C_l) - \max_k \ln L(G \mid C_k))}$$

#### Mandatory Sum-to-Unity Invariant:
$$\left| \left( \sum_{j=1}^5 q_j \right) - 1.0 \right| \le 1.0 \times 10^{-6}$$

### 46.2 3D Spherical Coordinate Projection & Bivariate Uncertainty Geometry

Continental reference centroid coordinates:
* **EUR:** $(+48.50^\circ\text{N}, +15.20^\circ\text{E})$
* **AFR:** $(+02.50^\circ\text{N}, +22.80^\circ\text{E})$
* **EAS:** $(+35.00^\circ\text{N}, +105.00^\circ\text{E})$
* **SAS:** $(+22.50^\circ\text{N}, +78.50^\circ\text{E})$
* **AMR:** $(+04.00^\circ\text{N}, -68.00^\circ\text{W})$

Weighted 3D Cartesian vector summation:

$$\mathbf{V}_{\text{pred}} = \sum_{j=1}^5 q_j \begin{pmatrix} \cos(\text{Lat}_j) \cos(\text{Lng}_j) \\ \cos(\text{Lat}_j) \sin(\text{Lng}_j) \\ \sin(\text{Lat}_j) \end{pmatrix} = \begin{pmatrix} \bar{x} \\ \bar{y} \\ \bar{z} \end{pmatrix}$$

$$\bar{\theta}_{\text{Lat}} = \arcsin\left(\frac{\bar{z}}{\|\mathbf{V}_{\text{pred}}\|}\right), \quad \bar{\theta}_{\text{Lng}} = \text{atan2}(\bar{y}, \bar{x})$$

#### 95% Confidence Ellipse ($\chi^2_2 = 5.991$):

$$\sigma_{\text{Lat}}^2 = \sum q_j (\text{Lat}_j - \bar{\theta}_{\text{Lat}})^2, \quad \sigma_{\text{Lng}}^2 = \sum q_j (\text{Lng}_j - \bar{\theta}_{\text{Lng}})^2, \quad \sigma_{\text{Lat, Lng}} = \sum q_j (\text{Lat}_j - \bar{\theta}_{\text{Lat}})(\text{Lng}_j - \bar{\theta}_{\text{Lng}})$$

$$\lambda_{1, 2} = \frac{\sigma_{\text{Lat}}^2 + \sigma_{\text{Lng}}^2 \pm \sqrt{(\sigma_{\text{Lat}}^2 - \sigma_{\text{Lng}}^2)^2 + 4 \sigma_{\text{Lat, Lng}}^2}}{2}$$

$$a = \sqrt{5.991 \cdot \lambda_1}, \quad b = \sqrt{5.991 \cdot \lambda_2}, \quad \theta_{\text{tilt}} = \frac{1}{2} \text{atan2}\left(2 \sigma_{\text{Lat, Lng}}, \sigma_{\text{Lat}}^2 - \sigma_{\text{Lng}}^2\right)$$

---

## 47. Craniofacial Morphometrics & 3D Shape Space Reconstruction (Module 13)

The Craniofacial Morphometrics Engine reconstructs 3D facial shape deformations from predictive SNP dosages across canonical GWAS effect loci (Claes et al. paradigm), deriving exact 3D millimetric coordinates $(x, y, z)$ for primary cephalometric landmarks and computing clinical facial indices.

### 47.1 Primary Craniofacial Predictor Loci & Effect Sizes

| SNP Locus (rsID) | Target Gene | Morphometric Structural Effect | Effect Allele | Effect Size ($w_k$) |
| :--- | :--- | :--- | :--- | :--- |
| **rs974448** | **PAX3** | Cranial Vault Width & Nasion Position | `T` | $+0.412\text{ SD}$ |
| **rs12882923**| **PAX9** | Bizygomatic Breadth & Midface Breadth | `C` | $+0.385\text{ SD}$ |
| **rs11130635**| **PRDM16** | Nasal Bridge Elevation & Projection | `A` | $+0.452\text{ SD}$ |
| **rs13289** | **DCHS2** | Nasal Tip Morphology & Subnasale Angle | `G` | $-0.321\text{ SD}$ |
| **rs7559252** | **PCDH15** | Chin Prominence & Mandibular Convexity | `C` | $+0.298\text{ SD}$ |

### 47.2 3D Cephalometric Landmark Reconstruction Equations (mm)

1. **Nasion ($N$):**
   $$x = 0.00, \quad y = 12.4 + 1.25 X_{\text{PAX3}}, \quad z = 45.2 + 0.85 X_{\text{PAX3}}$$

2. **Pronasale ($Prn$ - Nasal Apex):**
   $$x = 0.00, \quad y = 48.5 + 2.10 X_{\text{PRDM16}} - 1.45 X_{\text{DCHS2}}, \quad z = 12.1 + 1.15 X_{\text{PRDM16}}$$

3. **Subnasale ($Sn$):**
   $$x = 0.00, \quad y = 38.2 - 1.10 X_{\text{DCHS2}}, \quad z = -2.5 - 0.65 X_{\text{DCHS2}}$$

4. **Alare Left ($Al_L$) & Right ($Al_R$):**
   $$x_{Al_L} = -18.5 - 0.95 X_{\text{PAX9}}, \quad x_{Al_R} = +18.5 + 0.95 X_{\text{PAX9}}$$
   $$y = 36.1 + 0.45 X_{\text{PAX9}}, \quad z = 2.1 + 0.30 X_{\text{PAX9}}$$

5. **Labiale Superius ($Ls$):**
   $$x = 0.00, \quad y = 34.5 + 0.60 X_{\text{PCDH15}}, \quad z = -12.4 - 0.40 X_{\text{PCDH15}}$$

6. **Menton ($Me$ - Chin Base):**
   $$x = 0.00, \quad y = 18.2 + 1.85 X_{\text{PCDH15}}, \quad z = -68.5 - 1.20 X_{\text{PCDH15}}$$

### 47.3 Morphological Dimensions & Clinical Facial Index ($I_F$)

$$h_{\text{face}} = \|N - Me\|_2 = \sqrt{(y_N - y_{Me})^2 + (z_N - z_{Me})^2}$$

$$w_{\text{alar}} = \|Al_R - Al_L\|_2 = 2 \cdot |x_{Al_R}|$$

$$I_F = \frac{h_{\text{face}}}{w_{\text{alar}}} \times 100$$

* **Bilateral Midline Symmetry Invariant:** $x_N = x_{Prn} = x_{Sn} = x_{Ls} = x_{Me} = 0.00$ and $x_{Al_L} = -x_{Al_R}$.
* **Vertical Z-Monotonicity Invariant:** $z_N > z_{Prn} > z_{Sn} > z_{Ls} > z_{Me}$ for all valid $X \in \{0, 1, 2\}^5$.

---

## 48. Hair Texture Dynamics & Androgenetic Alopecia (Balding Risk PRS) Engine (Module 14)

The Hair Morphology Engine estimates biophysical hair fiber cross-sectional area, curl density index ($C_{\text{curl}}$), and androgenetic alopecia (male-pattern baldness) polygenic risk scores ($\text{PRS}_{\text{balding}}$) mapped to the Hamilton-Norwood scale.

### 48.1 Hair Fiber Cross-Sectional Geometry & Curl Density Index

1. **Biophysical Cross-Sectional Area ($\mu\text{m}^2$):**
   $$\text{Area } (\mu\text{m}^2) = 3850.0 + 1420.0 \cdot X_{\text{EDAR}} \quad (X_{\text{EDAR}} \in \{0, 1, 2\} \text{ at rs3827072})$$

2. **Curl Density Index ($C_{\text{curl}} \in [0.0, 10.0]$):**
   $$C_{\text{curl}} = \max\left(0.0, \; \min\left(10.0, \; 1.20 + 1.85 \cdot X_{\text{TCHH}} + 1.42 \cdot X_{\text{WNT10A}} - 2.10 \cdot X_{\text{EDAR}}\right)\right)$$

   - `TCHH rs11803731 (Trichohyalin)`: Curl induction ($+1.85$)
   - `WNT10A rs7349332`: Curl induction ($+1.42$)
   - `EDAR rs3827072 (Val370Ala)`: Thickening and straightening ($-2.10$)

3. **Phenotypic Texture Classification:**
   - **`STRAIGHT` ($C_{\text{curl}} < 2.0$):** Fiber diameter $85.0 - 110.0\ \mu\text{m}$ if $X_{\text{EDAR}} = 2$, else $70.0 - 85.0\ \mu\text{m}$.
   - **`WAVY` ($2.0 \le C_{\text{curl}} < 4.5$):** Fiber diameter $65.0 - 80.0\ \mu\text{m}$.
   - **`CURLY` ($4.5 \le C_{\text{curl}} < 7.0$):** Fiber diameter $55.0 - 70.0\ \mu\text{m}$.
   - **`KINKY_WOOLLY` ($C_{\text{curl}} \ge 7.0$):** Fiber diameter $45.0 - 60.0\ \mu\text{m}$.

### 48.2 Androgenetic Alopecia Polygenic Risk Score ($\text{PRS}_{\text{balding}}$)

$$\text{PRS}_{\text{balding}} = 0.982 X_{\text{rs6152}} + 0.541 X_{\text{rs2180439}} + 0.485 X_{\text{rs1160312}} + 0.362 X_{\text{rs756853}}$$

- **Hamilton-Norwood Scale Mapping:**
  - $\text{PRS} < 0.50 \implies$ **Grade I / II** (Minimal or No Hair Loss, Low Risk)
  - $0.50 \le \text{PRS} < 1.20 \implies$ **Grade III** (Slight Temporal / Vertex Recess, Moderate Risk)
  - $1.20 \le \text{PRS} < 2.10 \implies$ **Grade IV / V** (Moderate Vertex Loss, Elevated Risk)
- **Domain Boundaries:** $0.00 \le \text{PRS}_{\text{balding}} \le 4.740$.

---

## 49. Ephelides (Freckling), MC1R Epistasis & UV Sensitivity Index Engine (Module 15)

The Ephelides & UV Sensitivity Engine predicts quantitative freckling score ($F_{\text{score}}$), MC1R compound heterozygous loss-of-function load ($W_{\text{MC1R}}$), and Minimal Erythema Dose ($\text{MED}$) photosensitivity.

### 49.1 MC1R Functional Loss-of-Function Matrix

| Variant Name | SNP ID (rsID) | Amino Acid Change | Functional Class | Loss-of-Function Weight ($w_{\text{MC1R}}$) |
| :--- | :--- | :--- | :--- | :--- |
| **D84E** | `rs1805006` | Asp84Glu | 'R' High Risk | $+2.50$ |
| **R142H** | `rs75570604` | Arg142His | 'R' High Risk | $+2.40$ |
| **R151C** | `rs1805007` | Arg151Cys | 'R' High Risk | $+2.85$ |
| **R160W** | `rs1805008` | Arg160Trp | 'R' High Risk | $+2.75$ |
| **D294H** | `rs1805009` | Asp294His | 'R' High Risk | $+2.60$ |
| **V60L** | `rs1805005` | Val60Leu | 'r' Low Risk | $+1.10$ |
| **V92M** | `rs2228479` | Val92Met | 'r' Low Risk | $+0.85$ |
| **R163Q** | `rs885479` | Arg163Gln | 'r' Low Risk | $+0.75$ |
| **Wild Type (wt)**| — | Consensus | Wild Type Baseline | $0.00$ |

### 49.2 Compound Heterozygosity and Quantitative Freckling Score ($F_{\text{score}}$)

$$W_{\text{MC1R}} = \sum_{i} w_i \cdot X_i$$

$$F_{\text{score}} = \min \left( 100.0, \; \frac{100.0}{1 + \exp\left( - \left( -2.50 + 1.35 W_{\text{MC1R}} + 0.85 X_{\text{ASIP}} + 0.65 X_{\text{BNC2}} \right) \right)} \right)$$

- `ASIP rs1015362`: Epistatic enhancer ($+0.85$)
- `BNC2 rs10756819`: Epistatic enhancer ($+0.65$)

### 49.3 Minimal Erythema Dose (MED) & UV Sensitivity Tiers

- **$R/R$ (Severe Loss, $n_R \ge 2$):** $\text{MED} < 20\text{ mJ/cm}^2$. Never tans, always burns severely. Dense ephelides.
- **$R/r$ or $R/wt$ (Moderate Loss, $n_R \ge 1$):** $\text{MED} \in [20, 35]\text{ mJ/cm}^2$. Rare tanning, frequent burns. Moderate ephelides.
- **$r/r$ or $r/wt$ (Mild Loss, $n_R = 0, n_r \ge 1$):** $\text{MED} \in [35, 50]\text{ mJ/cm}^2$. Mild tanning, occasional burns.
- **$wt/wt$ (Wild-Type Consensus):** $\text{MED} > 50\text{ mJ/cm}^2$. Normal tanning, rare burns. Minimal ephelides.

---

## 50. VISAGE 5-CpG & Multi-Tissue Epigenetic Age Clock Engine (Module 16)

The Epigenetic Age Clock Engine calculates chronological and biological age from quantitative DNA methylation fractions ($\beta \in [0.0, 1.0]$) across the VISAGE Consortium 5-CpG core multiplex (`cg16867657` *ELOVL2*, `cg06639320` *FHL2*, `cg16419235` *PENK*, `cg04523812` *TRIM59*, `cg07955995` *KLF14*) and extended 10-CpG markers using Horvath piecewise non-linear transformations ($y_0 = 20.0$ pivot), direct MLR power transformations, dedicated multi-tissue matrix calibration, dynamic Mahalanobis covariance uncertainty budgets, and standardized ENFSI evaluative reporting.

### 50.1 VISAGE 5-CpG Piecewise Log-Linear Elastic Net Model

The linear prognostic index $x$ is formulated across the 5 core VISAGE loci:

$$x = \beta_0 + \sum_{i=1}^{5} w_i \cdot \beta_i = -1.250000 + 2.85 \beta_{\text{ELOVL2}} + 1.92 \beta_{\text{FHL2}} + 0.95 \beta_{\text{PENK}} + 0.88 \beta_{\text{TRIM59}} + 1.15 \beta_{\text{KLF14}}$$

The piecewise continuous link function with pivot boundary $y_0 = 20.0$ and multiplier $21.0$:

$$\text{Age}_{\text{model}} = F(x) = \begin{cases} 21.0 \cdot \exp(x) - 1.0 & \text{if } x < 0 \quad (\text{Pediatric Minor Stage}, \text{Age} < 20) \\ 21.0 \cdot x + 20.0 & \text{if } x \ge 0 \quad (\text{Adult Stage}, \text{Age} \ge 20) \end{cases}$$

$$\text{Age}_{\text{final}} = \max\left(0.0, \; \text{Age}_{\text{model}} + \Delta_{\text{tissue}}\right)$$

### 50.2 VISAGE 5-CpG Direct Multiple Linear Regression (MLR) Power Model

For linear regression modeling incorporating non-linear biological kinetics of *ELOVL2* (Zbieć-Piekarska et al.):

$$\text{Age}_{\text{MLR}} = -14.2815 + 120.3520 \cdot \beta_{\text{ELOVL2}}^{2.366} + 38.2140 \cdot \beta_{\text{FHL2}} + 21.8040 \cdot \beta_{\text{PENK}} + 18.9410 \cdot \beta_{\text{TRIM59}} + 26.1030 \cdot \beta_{\text{KLF14}} + \Delta_{\text{tissue}}$$

### 50.3 Dedicated Multi-Tissue Matrix Calibration Offsets

| Biological Tissue Matrix | Model Intercept ($\Delta_{\text{tissue}}$) | Calibration MAE | RMSE | Residual SE ($s_e$) | 95% Bound ($\pm U_{95}$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Venous Blood / Bloodstains** | $0.00 \text{ yrs}$ | $3.15 \text{ yrs}$ | $3.98 \text{ yrs}$ | $1.95 \text{ yrs}$ | $\pm 3.82 \text{ yrs}$ |
| **Oral Saliva / Buccal Swab** | $+2.45 \text{ yrs}$ | $3.68 \text{ yrs}$ | $4.52 \text{ yrs}$ | $2.25 \text{ yrs}$ | $\pm 4.41 \text{ yrs}$ |
| **Seminal Fluid / Semen** | $+18.60 \text{ yrs}$ | $4.12 \text{ yrs}$ | $5.20 \text{ yrs}$ | $2.60 \text{ yrs}$ | $\pm 5.10 \text{ yrs}$ |
| **Skeletal Bone / Teeth** | $+1.15 \text{ yrs}$ | $4.85 \text{ yrs}$ | $6.10 \text{ yrs}$ | $3.05 \text{ yrs}$ | $\pm 5.98 \text{ yrs}$ |

### 50.4 ISO/IEC 17025 Dynamic Mahalanobis Metrological Uncertainty Budget

To account for leverage in individual forensic methylation profiles, sample-specific prediction intervals are computed via the Mahalanobis distance squared against the calibration training centroid $\bar{\boldsymbol{\beta}}$:

$$D^2_M = \mathbf{d}^T (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{d}, \quad \text{where } \mathbf{d} = \boldsymbol{\beta}^* - \bar{\boldsymbol{\beta}}$$

$$\bar{\boldsymbol{\beta}} = [0.3850, \; 0.3120, \; 0.2450, \; 0.2810, \; 0.2100]^T$$

$$(\mathbf{X}^T \mathbf{X})^{-1} = \begin{bmatrix} 0.01245 & -0.00312 & -0.00185 & -0.00210 & -0.00142 \\ -0.00312 & 0.00892 & -0.00115 & -0.00154 & -0.00098 \\ -0.00185 & -0.00115 & 0.01540 & -0.00245 & -0.00120 \\ -0.00210 & -0.00154 & -0.00245 & 0.01120 & -0.00085 \\ -0.00142 & -0.00098 & -0.00120 & -0.00085 & 0.00965 \end{bmatrix}$$

$$u_{\text{pred}}(\boldsymbol{\beta}^*) = s_e \cdot \sqrt{1 + \frac{1}{N} + D^2_M}, \quad U_{95\%} = t_{0.025, \, \text{df}=644} \cdot u_{\text{pred}}(\boldsymbol{\beta}^*) \approx 1.96366 \cdot u_{\text{pred}}(\boldsymbol{\beta}^*)$$

$$\text{PI}_{95\%} = \left[ \max\left(0.0, \; \hat{y} - U_{95\%}\right), \; \hat{y} + U_{95\%} \right]$$

### 50.5 Extended 10-CpG Pan-Tissue Clock (Pillar 4 Baseline)

$$x = \beta_{0,\text{tissue}} + \sum_{i=1}^{10} \frac{w_i \cdot \beta_i}{100.0}$$

| Target Gene | Locus ID (cgID) | Chromosome | Amplicon | Weight ($w_i$) | Correlation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ELOVL2** | `cg16867657` | chr6 | 267 bp | $+102.45$ | Positive ($R > 0.85$) |
| **ELOVL2-2** | `cg21572722` | chr6 | 267 bp | $+88.12$ | Positive |
| **FHL2** | `cg06639320` | chr2 | 167 bp | $+74.30$ | Positive |
| **PENK** | `cg16419235` | chr8 | 142 bp | $-45.20$ | Negative |
| **TRIM59** | `cg04084157` | chr3 | 141 bp | $+56.80$ | Positive |
| **KLF14** | `cg08097417` | chr7 | 128 bp | $+62.15$ | Positive |
| **EDARADD** | `cg09809672` | chr1 | 193 bp | $+41.90$ | Positive |
| **MIR29B2CHG**| `cg02088308` | chr1 | 146 bp | $+38.75$ | Positive |
| **PDE4C** | `cg17861230` | chr19 | 215 bp | $+49.10$ | Positive |
| **ASPA** | `cg02228185` | chr17 | 108 bp | $-32.40$ | Negative |

---

## 51. tDMR-Based Body Fluid Identification Engine (Module 17)

The Body Fluid Identification Engine classifies cellular origins of forensic biological stains across 6 core body fluid classes using Bayesian Quadratic Discriminant Analysis (QDA) over 12 diagnostic Tissue-Specific Differentially Methylated Regions (tDMRs).

### 51.1 12 Diagnostic tDMR CpG Loci Reference Matrix ($\mu \pm \sigma$)

| Locus ID | Functional Gene / Region | Blood ($\mu \pm \sigma$) | Semen ($\mu \pm \sigma$) | Saliva ($\mu \pm \sigma$) | Vaginal ($\mu \pm \sigma$) | Menstrual ($\mu \pm \sigma$) | Skin ($\mu \pm \sigma$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **cg09652652** | Endothelial tDMR | $0.12 \pm 0.03$ | $0.88 \pm 0.04$ | $0.85 \pm 0.05$ | $0.82 \pm 0.06$ | $0.22 \pm 0.05$ | $0.91 \pm 0.03$ |
| **cg19406367** | Hematopoietic Locus | $0.15 \pm 0.04$ | $0.92 \pm 0.03$ | $0.89 \pm 0.04$ | $0.86 \pm 0.05$ | $0.31 \pm 0.06$ | $0.88 \pm 0.04$ |
| **cg17610929** | Germ Cell tDMR | $0.91 \pm 0.03$ | $0.04 \pm 0.01$ | $0.88 \pm 0.04$ | $0.90 \pm 0.03$ | $0.89 \pm 0.04$ | $0.94 \pm 0.02$ |
| **cg23521140** | DACT1 | $0.85 \pm 0.04$ | $0.08 \pm 0.02$ | $0.82 \pm 0.05$ | $0.84 \pm 0.04$ | $0.83 \pm 0.05$ | $0.89 \pm 0.03$ |
| **cg26763284** | PRMT12 | $0.89 \pm 0.03$ | $0.05 \pm 0.02$ | $0.86 \pm 0.04$ | $0.88 \pm 0.04$ | $0.87 \pm 0.04$ | $0.92 \pm 0.03$ |
| **cg23576855** | Oral Epithelial | $0.84 \pm 0.04$ | $0.89 \pm 0.03$ | $0.10 \pm 0.03$ | $0.78 \pm 0.06$ | $0.81 \pm 0.05$ | $0.82 \pm 0.05$ |
| **cg00399818** | Salivary Gland | $0.82 \pm 0.05$ | $0.86 \pm 0.04$ | $0.12 \pm 0.03$ | $0.75 \pm 0.07$ | $0.79 \pm 0.06$ | $0.85 \pm 0.04$ |
| **cg04382942** | Cervicovaginal | $0.88 \pm 0.03$ | $0.91 \pm 0.03$ | $0.72 \pm 0.06$ | $0.15 \pm 0.04$ | $0.35 \pm 0.08$ | $0.86 \pm 0.04$ |
| **cg11624633** | MYO1G | $0.86 \pm 0.04$ | $0.89 \pm 0.03$ | $0.70 \pm 0.05$ | $0.18 \pm 0.05$ | $0.38 \pm 0.07$ | $0.84 \pm 0.04$ |
| **cg00854446** | Endometrial | $0.82 \pm 0.05$ | $0.94 \pm 0.02$ | $0.85 \pm 0.04$ | $0.52 \pm 0.09$ | $0.14 \pm 0.04$ | $0.90 \pm 0.03$ |
| **cg18063373** | Endometrial Stroma | $0.80 \pm 0.05$ | $0.92 \pm 0.03$ | $0.83 \pm 0.05$ | $0.55 \pm 0.08$ | $0.16 \pm 0.04$ | $0.88 \pm 0.04$ |
| **cg07823520** | Epidermis | $0.90 \pm 0.03$ | $0.95 \pm 0.02$ | $0.81 \pm 0.05$ | $0.85 \pm 0.04$ | $0.86 \pm 0.04$ | $0.11 \pm 0.03$ |

### 51.2 Bayesian QDA Log-Likelihood & Posterior Probabilities

For observed sample profile $\boldsymbol{\beta}^* = (\beta_1, \dots, \beta_M)^T$, the Gaussian log-likelihood for tissue class $T_k$ is:

$$\text{LL}_k(\boldsymbol{\beta}^*) = \sum_{m=1}^{12} \left[ -\frac{1}{2} \ln(2\pi \sigma_{k,m}^2) - \frac{(\beta_m^* - \mu_{k,m})^2}{2\sigma_{k,m}^2} \right]$$

$$P(T_k \mid \boldsymbol{\beta}^*) = \frac{\exp\left(\text{LL}_k(\boldsymbol{\beta}^*) - \max_j \text{LL}_j(\boldsymbol{\beta}^*)\right)}{\sum_{l=1}^{6} \exp\left(\text{LL}_l(\boldsymbol{\beta}^*) - \max_j \text{LL}_j(\boldsymbol{\beta}^*)\right)}$$

$$\text{LR}_{\text{tissue}} = \frac{P(T_{\text{top}} \mid \boldsymbol{\beta}^*)}{P(T_{\text{second}} \mid \boldsymbol{\beta}^*)}, \quad \log_{10} \text{LR} = \log_{10}(P_{\text{top}}) - \log_{10}(\max(10^{-6}, P_{\text{second}}))$$

---

## 52. Environmental Epigenetics & Lifestyle Biomarkers Engine (Module 18)

The Lifestyle Epigenetics Engine decodes chronic environmental exposures and physiological characteristics from DNA methylation profiles across target gene promoters:

### 52.1 Quantitative Cigarette Smoking Biomarker Model

$$\text{Score}_{\text{smoke}} = 10.50 - 9.80 \cdot \beta_{\text{cg05575921 (AHRR)}} - 2.50 \cdot \beta_{\text{cg03636183 (F2RL3)}} - 1.80 \cdot \beta_{\text{cg01940273 (ALPPL2)}}$$

$$\text{Pack-Years} = \max\left(0.0, \; \frac{0.85 - \beta_{\text{cg05575921}}}{0.012}\right)$$

| AHRR Locus ($\beta$) | Smoking Score | Classification | Estimated Exposure (Pack-Years) |
| :--- | :--- | :--- | :--- |
| $\beta \ge 0.80$ | $\text{Score} < 1.50$ | **Never Smoker** | $0.0 \text{ Pack-Years}$ |
| $0.55 \le \beta < 0.80$ | $1.50 \le \text{Score} \le 4.50$ | **Former / Light Smoker** | $1.0 - 10.0 \text{ Pack-Years}$ |
| $\beta < 0.55$ | $\text{Score} > 4.50$ | **Active Heavy Smoker** | $> 10.0 \text{ Pack-Years}$ |

### 52.2 Epigenetic Body Mass Index (BMI) Model

$$\widehat{\text{BMI}} \, (\text{kg/m}^2) = 24.50 + 18.20 \cdot \beta_{\text{cg06500161 (ABCG1)}} - 22.40 \cdot \beta_{\text{cg00574958 (CPT1A)}} + 12.10 \cdot \beta_{\text{cg11024682 (SREBF1)}}$$

| Estimated BMI Range ($\text{kg/m}^2$) | Weight Classification Category |
| :--- | :--- |
| $\widehat{\text{BMI}} < 18.5$ | **Underweight** |
| $18.5 \le \widehat{\text{BMI}} < 25.0$ | **Normal Weight** |
| $25.0 \le \widehat{\text{BMI}} < 30.0$ | **Overweight** |
| $30.0 \le \widehat{\text{BMI}} < 35.0$ | **Obesity Class I** |
| $\widehat{\text{BMI}} \ge 35.0$ | **Obesity Class II+** |

### 52.3 Circadian Diurnal Phase Time-of-Deposition (TOD)

$$\text{Ratio}_{\text{circ}} = \frac{\beta_{\text{PER2}}}{\max(0.01, \beta_{\text{BMAL1}})}$$

- $\text{Ratio}_{\text{circ}} > 1.20 \implies$ **NOCTURNAL_PEAK_NIGHT** (22:00 - 04:00 UTC)
- $\text{Ratio}_{\text{circ}} < 0.80 \implies$ **MATUTINAL_PEAK_MORNING** (04:00 - 10:00 UTC)
- $0.80 \le \text{Ratio}_{\text{circ}} \le 1.20 \implies$ **DIURNAL_PEAK_DAYTIME** (10:00 - 16:00 UTC)

### 52.4 Epigenetic Age Acceleration ($\Delta\text{Age}$)

$$\Delta\text{Age} = \text{DNAmAge} - \text{ChronologicalAge}$$

- $\Delta\text{Age} > +5.0 \text{ years} \implies$ **Accelerated Biological Aging**
- $\Delta\text{Age} < -5.0 \text{ years} \implies$ **Decelerated Biological Aging**
- $-5.0 \le \Delta\text{Age} \le +5.0 \text{ years} \implies$ **Normal Biological Aging**

---

## 53. Somatic Mosaicism, Telomere Length Decay ($T/S$) & Post-Mortem Epigenetic Interval (PMI) Engine (Module 19)

### 53.1 Relative Telomere Length ($T/S$) Kinetics

$$T/S = 2^{-\Delta\Delta C_t} = 1.420 - 0.0085 \cdot \text{Age}$$

$$\widehat{\text{Age}}_{\text{telomere}} = \max\left(0.0, \; \frac{1.420 - T/S}{0.0085}\right)$$

| Relative $T/S$ Ratio Range | Biological Age Group | Typical Age Range |
| :--- | :--- | :--- |
| $T/S \ge 1.35$ | **Newborn / Infant** | $0 - 8 \text{ Years}$ |
| $1.15 \le T/S < 1.35$ | **Young Adult** | $8 - 32 \text{ Years}$ |
| $0.90 \le T/S < 1.15$ | **Middle-Aged** | $32 - 61 \text{ Years}$ |
| $T/S < 0.90$ | **Elderly** | $\ge 61 \text{ Years}$ |

### 53.2 Post-Mortem Epigenetic Decay Kinetics (PMI / ADH)

Post-mortem de-methylation follows Accumulated Degree-Hours (ADH) thermal summation kinetics:

$$\text{ADH} = \max(0.0, \; T_{\text{ambient}} - T_{\text{base}}) \times t_{\text{hours}}$$

$$\beta_m(\text{ADH}) = \beta_{0,m} \cdot \exp(-\lambda_m \cdot \text{ADH}) + \beta_{\text{floor}}$$

$$\widehat{\text{ADH}} = \frac{1}{\lambda_m} \cdot \ln\left( \frac{\beta_{0,m}}{\max(10^{-4}, \; \beta_m - \beta_{\text{floor}})} \right)$$

$$\widehat{\text{PMI}}_{\text{hours}} = \frac{\widehat{\text{ADH}}}{\max(0.1, \; T_{\text{ambient}} - T_{\text{base}})}$$

- Default kinetic constants: $\lambda = 0.00045\ \text{ADH}^{-1}, \beta_0 = 0.85, \beta_{\text{floor}} = 0.05, T_{\text{base}} = 0.0^\circ\text{C}$.

### 53.3 Somatic Mosaicism & Epigenetic Drift Index ($\mathcal{M}$)

$$\mathcal{M} = \sqrt{\frac{1}{M} \sum_{m=1}^M (\beta_{m,\text{tissue1}} - \beta_{m,\text{tissue2}})^2}$$

- $\mathcal{M} < 0.05 \implies$ **CLONAL_HOMOGENEITY**
- $0.05 \le \mathcal{M} \le 0.15 \implies$ **LOW_SOMATIC_DRIFT**
- $\mathcal{M} > 0.15 \implies$ **HIGH_SOMATIC_MOSAICISM**

---

## 54. Bisulfite QC & Methylation Probe Bias Calibration Engine (Module 20)

### 54.1 Bisulfite Conversion Efficiency Quality Control

$$C_{\text{conv}} = \left( 1 - \frac{\sum_{j=1}^{N_{\text{non-CpG}}} M_j}{\sum_{j=1}^{N_{\text{non-CpG}}} (M_j + U_j)} \right) \times 100\% \ge 99.0\%$$

- $C_{\text{conv}} \ge 99.0\% \implies$ **PASSED_QC** (Valid forensic DNA methylation profile).
- $C_{\text{conv}} < 99.0\% \implies$ **FAILED_INSUFFICIENT_CONVERSION** (Bisulfite artifact alert).

### 54.2 Beta $\leftrightarrow$ M-Value Bidirectional Transformations

$$M_i = \log_2\left( \frac{\max(\epsilon, \min(1 - \epsilon, \beta_i))}{1 - \max(\epsilon, \min(1 - \epsilon, \beta_i))} \right) \iff \beta_i = \frac{2^{M_i}}{2^{M_i} + 1}$$

- Guard boundary constant: $\epsilon = 10^{-6}$.
- Bijection recovery error: $|\beta - \text{inv}(M)| < 10^{-6}$.

### 54.3 Detection $P$-Value Filtering & BMIQ Calibration

- Detection $P$-value threshold: $P_{\text{det}} \le 0.01$. Probes exceeding $0.01$ are excluded from forensic calling.
- BMIQ quantile adjustment fits Infinium Type II probe density distributions onto Type I reference extremes.

---

## 55. 3D Bloodstain Pattern Analysis (BPA) Area of Origin & Flight Ballistics Engine (Module 21)

### 55.1 Fluid Kinematics & Impact Dynamics

Physical properties of human blood under standard conditions:
- Density: $\rho_{\text{blood}} \approx 1060 \text{ kg/m}^3$
- Dynamic Viscosity: $\mu_{\text{blood}} \approx 0.004 \text{ Pa}\cdot\text{s}$
- Surface Tension: $\sigma_{\text{blood}} \approx 0.058 \text{ N/m}$

The geometric impact angle ($\alpha$) and Balthazard directional unit vector ($\vec{v}_i$):

$$\alpha = \arcsin\left(\min\left(1.0, \frac{W}{L}\right)\right)$$

$$\vec{v}_i = \begin{pmatrix} v_{x,i} \\ v_{y,i} \\ v_{z,i} \end{pmatrix} = \begin{pmatrix} \cos\gamma_i \cos\alpha_i \\ \sin\gamma_i \cos\alpha_i \\ \sin\alpha_i \end{pmatrix}, \quad \|\vec{v}_i\| = 1.0$$

### 55.2 Closed-Form Least Squares Orthogonal Distance Convergence ($\mathbf{P}_{\text{AO}}$)

$$\mathbf{M}_i = (\mathbf{I} - \vec{v}_i \vec{v}_i^T) = \begin{pmatrix} 1 - v_x^2 & -v_x v_y & -v_x v_z \\ -v_y v_x & 1 - v_y^2 & -v_y v_z \\ -v_z v_x & -v_z v_y & 1 - v_z^2 \end{pmatrix}$$

$$\mathbf{A} = \sum_{i=1}^N \mathbf{M}_i, \quad \mathbf{b} = \sum_{i=1}^N \mathbf{M}_i \mathbf{P}_i$$

$$\mathbf{P}_{\text{AO}} = \mathbf{A}^{-1} \mathbf{b} = (x_0, y_0, z_0)^T$$

Spatial error radius ($r_{\text{err}}$):

$$\vec{d}_i = (\mathbf{P}_{\text{AO}} - \mathbf{P}_i) - ((\mathbf{P}_{\text{AO}} - \mathbf{P}_i) \cdot \vec{v}_i)\vec{v}_i \implies r_{\text{err}} = \sqrt{\frac{\sum_{i=1}^N \|\vec{d}_i\|^2}{\max(1, N - 3)}}$$

### 55.3 Aerodynamic Drag & Gravitational Trajectory Correction

$$\frac{d\vec{v}}{dt} = \vec{g} - \frac{3 \rho_{\text{air}} C_d(Re)}{4 \rho_{\text{blood}} d_d} \|\vec{v}\| \vec{v}$$

$$C_d(Re) = \begin{cases} \frac{24}{Re} (1 + 0.15 Re^{0.687}) & \text{if } Re \le 1000 \quad (\text{Schiller-Naumann}) \\ 0.44 & \text{if } Re > 1000 \end{cases}$$

---

## 56. Forensic Ballistics, SEM-EDX GSR & 3D CMC Striation Engine (Module 22)

### 56.1 Quantitative SEM-EDX GSR Classification (ASTM E1588-20)

| Classification Tier | Elemental Composition Criteria | Aspect Ratio | Evidentiary Interpretation |
| :--- | :--- | :--- | :--- |
| **Characteristic GSR** | $\text{Pb} \ge 10\%, \text{Ba} \ge 10\%, \text{Sb} \ge 10\%$ | $\le 1.3$ | Unique to firearm discharge events |
| **Consistent with GSR** | $\text{Pb-Ba}, \text{Pb-Sb}, \text{Ba-Sb} \ge 10\%$ | $\le 1.5$ | Indicative of firearm discharge |
| **Commonly Associated** | $\text{Pb} \ge 10\% \lor \text{Ba} \ge 10\% \lor (\text{Ba} \ge 10\% \land \text{Al} \ge 10\%)$ | Any | Environmental / industrial sources |

Evidentiary Likelihood Ratio ($LR_{\text{GSR}}$):

$$LR_{\text{GSR}} = \begin{cases} 10,000.0 & \text{if } N_{\text{char}} \ge 3 \quad (\text{Extremely Strong Support}) \\ 500.0 & \text{if } N_{\text{char}} \ge 1 \lor N_{\text{cons}} \ge 5 \quad (\text{Strong Support}) \\ 25.0 & \text{if } N_{\text{cons}} \ge 1 \quad (\text{Moderate Support}) \\ 1.0 & \text{otherwise} \quad (\text{Inconclusive / Neutral}) \end{cases}$$

### 56.2 3D Congruent Matching Cells (CMC) Algorithm for Toolmarks

Land engraved areas (LEA) are partitioned into $100 \ \mu\text{m} \times 100 \ \mu\text{m}$ grid cells evaluated across tri-threshold convergence:
1. Peak cross-correlation: $CCF_{\max, k} \ge 0.55$
2. Spatial translation tolerance: $|\Delta x_k - \bar{\Delta x}| \le 15.0 \ \mu\text{m}, \quad |\Delta y_k - \bar{\Delta y}| \le 15.0 \ \mu\text{m}$
3. Angular rotation tolerance: $|\Delta \theta_k - \bar{\Delta \theta}| \le 1.0^\circ$

$$K \ge 6 \text{ CMC} \implies P_{\text{false}} < 10^{-6} \implies \text{POSITIVE_IDENTIFICATION}$$

---

## 57. Forensic Entomology & Calliphoridae Minimum PMI Thermal Summation Engine (Module 23)

### 57.1 Accumulated Thermal Energy Models (ADD / ADH)

$$\text{ADD} = \sum_{d=1}^D \max\left(0, \; \bar{T}_d - T_{\text{base}}\right), \quad \text{ADH} = \sum_{h=1}^H \max\left(0, \; (T_h + \Delta T_{\text{mass}}) - T_{\text{base}}\right)$$

- $T_{\text{base}}$: Species-specific developmental thermal threshold below which physiological development ceases.
- $\Delta T_{\text{mass}}$: Larval aggregate metabolic heating adjustment ($+1.5^\circ\text{C} \dots +3.5^\circ\text{C}$).

### 57.2 Dipteran Species Calibration Parameters

| Dipteran Species | $T_{\text{base}}$ ($^\circ\text{C}$) | Egg (ADH) | 1st Instar | 2nd Instar | 3rd Feeding | 3rd Post-Feeding | Pupae (ADH) | Total $K$ (ADH) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ***Lucilia sericata*** | $9.0$ | $240.0$ | $480.0$ | $800.0$ | $1254.5$ | $2200.0$ | $5000.0$ | $10174.5$ |
| ***Calliphora vicina*** | $3.0$ | $450.0$ | $1170.0$ | $2250.0$ | $4050.0$ | $6450.0$ | $9300.0$ | $23670.0$ |
| ***Chrysomya albiceps*** | $10.2$ | $260.0$ | $740.0$ | $1340.0$ | $2440.0$ | $4540.0$ | $8440.0$ | $17760.0$ |
| ***Phormia regina*** | $10.0$ | $300.0$ | $800.0$ | $1500.0$ | $2900.0$ | $5100.0$ | $9200.0$ | $19800.0$ |

### 57.3 Minimum Post-Mortem Interval ($PMI_{\min}$) Backwards Solver

Walking backwards from sampling timestamp $t_{\text{sample}}$ across hourly ambient temperatures:

$$\sum_{h=1}^{H_{\min}} \max\left(0, \; (T_h + \Delta T_{\text{mass}}) - T_{\text{base}}\right) \ge \text{ADH}_{\text{stage}} \implies PMI_{\min} = H_{\min} \text{ hours}$$

$$t_{\text{colonisation}} = t_{\text{sample}} - PMI_{\min}$$

---

## 58. Digital Microscopy, Multispectral Imaging (MSI) & Trace Spectroscopy Engine (Module 24)

### 58.1 Targeted Multispectral Wavelength Bands (MSI)

| Band Identifier | Central Wavelength | Optical Phenomenon | Target Evidence Matrix | Physical Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **UV-A** | $365 \text{ nm}$ | Fluorescence Excitation | Semen, Saliva, Vaginal Fluids | Excitation of endogenous flavins & lipids |
| **Soret Band** | $415 \text{ nm}$ | Peak Optical Absorption | Latent / Dilute Bloodstains | Porphyrin ring electronic absorption |
| **Blue Light** | $450 \text{ nm}$ | Secondary Fluorescence | Latent Fingerprints & Serology | $530 \text{ nm}$ long-pass filtered dye excitation |
| **Near-IR** | $850 \text{ nm}$ | Substrate Transmission | Blood & GSR on Dark Fabrics | Fabric dyes transparent; carbon particles visible |

### 58.2 Hit Quality Index (HQI) Spectral Dot Product Formulation

$$\text{HQI} = \frac{\left( \mathbf{S}_{\text{sample}} \cdot \mathbf{S}_{\text{ref}} \right)^2}{\left( \mathbf{S}_{\text{sample}} \cdot \mathbf{S}_{\text{sample}} \right) \left( \mathbf{S}_{\text{ref}} \cdot \mathbf{S}_{\text{ref}} \right)} \times 100\% = \frac{\left( \sum_{i=1}^M S_{\text{sample}, i} S_{\text{ref}, i} \right)^2}{\left( \sum_{i=1}^M S_{\text{sample}, i}^2 \right) \left( \sum_{i=1}^M S_{\text{ref}, i}^2 \right)} \times 100\%$$

- $\text{HQI} \ge 90.0\% \implies$ **`POSITIVE_SPECTRAL_MATCH`** ($P_{\text{false}} < 10^{-4}$, definitive chemical identity).
- $75.0\% \le \text{HQI} < 90.0\% \implies$ **`PROBABLE_MATCH_DEGRADED`** (Surface contamination / weathering).
- $\text{HQI} < 75.0\% \implies$ **`NON_MATCH_EXCLUSION`** (Chemical exclusion).

### 58.3 Diagnostic Forensic Fiber Wavenumbers

- **Polyester (PET):** $1715 \text{ cm}^{-1}$ ($\text{C=O}$ ester), $1240 \text{ cm}^{-1}$ ($\text{C-O-C}$).
- **Nylon-6,6:** $1635 \text{ cm}^{-1}$ (Amide I), $1538 \text{ cm}^{-1}$ (Amide II).
- **Acrylic (PAN):** $2240 \text{ cm}^{-1}$ (Nitrile $\text{C}\equiv\text{N}$).
- **Cotton (Cellulose):** $3330 \text{ cm}^{-1}$ ($\text{O-H}$ stretch), $1030 \text{ cm}^{-1}$ ($\text{C-O}$ stretch).
- **Wool (Keratin):** $1650 \text{ cm}^{-1}$ (Amide I), $1520 \text{ cm}^{-1}$ (Amide II).

---

## 59. Forensic Toxicology, Pharmacokinetics & Post-Mortem Drug Redistribution (PMR) Engine (Module 25)

### 59.1 Physicochemical Determinants of PMR and Central-to-Peripheral ($C_{\text{heart}} / C_{\text{femoral}}$) Ratios

| Compound | Apparent $V_d$ | $\log P$ | $\text{p}K_a$ | Mean C/P Ratio ($C_{\text{heart}}/C_{\text{femoral}}$) | PMR Risk Tier | Elimination Model |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ethanol** | $0.6 \text{ L/kg}$ | $-0.31$ | — | $1.00 \pm 0.10$ | Low / Minimal | Zero-Order ($\beta_{60} = 0.15 \text{ g/L/h}$) |
| **Acetaminophen** | $0.9 \text{ L/kg}$ | $0.46$ | $9.5$ | $1.05 \pm 0.12$ | Low | First-Order ($t_{1/2} = 2.5 \text{ h}$) |
| **Morphine** | $3.5 \text{ L/kg}$ | $0.89$ | $8.0$ | $1.80 \pm 0.40$ | Moderate | First-Order ($t_{1/2} = 3.0 \text{ h}$) |
| **Methamphetamine** | $4.0 \text{ L/kg}$ | $2.07$ | $9.9$ | $2.10 \pm 0.50$ | High | First-Order ($t_{1/2} = 10.0 \text{ h}$) |
| **Fentanyl** | $5.0 \text{ L/kg}$ | $4.05$ | $8.4$ | $2.80 \pm 0.70$ | High / Severe | First-Order ($t_{1/2} = 7.0 \text{ h}$) |
| **Amitriptyline** | $20.0 \text{ L/kg}$ | $4.92$ | $9.4$ | $4.50 \pm 1.20$ | Very High | First-Order ($t_{1/2} = 21.0 \text{ h}$) |

### 59.2 Post-Mortem Cardiac Overestimation Alert Rule

$$\text{If } \frac{C_{\text{heart}}}{C_{\text{femoral}}} > 2.0 \quad \text{and} \quad V_d > 3.0 \text{ L/kg} \implies \text{PMR Overestimation Alert (Use } C_{\text{femoral}} \text{ Gold Standard)}$$

### 59.3 Antemortem Toxicokinetic Back-Extrapolation Models

- **Zero-Order Elimination (Ethanol Widmark Model):**
  $$C_{\text{antemortem}} = C_{\text{femoral}} + \beta_{60} \cdot \Delta t \quad (\beta_{60} = 0.15 \text{ g/L/h})$$

- **First-Order Elimination:**
  $$k_e = \frac{\ln(2)}{t_{1/2}} \implies C_{\text{antemortem}}(t - \Delta t) = C_{\text{femoral}} \cdot e^{k_e \cdot \Delta t}$$

---

## 60. Cryptographic Forensic Chain of Custody (CoC) Immutable Merkle Tree Ledger Engine (Module 26)

**Research Reference:** Pillar 6 Research §1 (ISO/IEC 17025:2017 Clause 7.6 • FRE 702 / Daubert • NIST SP 800-106)

### 60.1 Chained SHA-256 Leaf Node Hashing (§1.1)

Each custody event $E_i$ in the ordered sequence $\mathbf{E} = \{E_1, E_2, \dots, E_N\}$ produces a chained leaf hash over canonicalized metadata fields concatenated with the preceding leaf hash:

$$H_i = \text{SHA256}\Big( \text{EventID}_i \parallel \text{Timestamp}_i \parallel \text{OfficerID}_i \parallel \text{SampleBarcode}_i \parallel \text{LocationID}_i \parallel H_{i-1} \Big)$$

where $\parallel$ denotes byte concatenation, $\text{Timestamp}_i$ is RFC 3161-certified UTC, and the genesis prior hash is:

$$H_{i-1}\big|_{i=1} = \underbrace{00\ldots0}_{64 \text{ hex chars}} \quad (\text{genesis})$$

---

### 60.2 Balanced Binary Merkle Tree Construction (§1.1)

| Merkle Layer Level | Node Type | Hash Input Signature | Complexity |
| :--- | :--- | :--- | :--- |
| **Layer 0 (Leaf)** | Custody Event $E_i$ | $\text{SHA256}(\text{EventID} \parallel \text{Timestamp} \parallel \text{OfficerID} \parallel \text{Barcode} \parallel H_{i-1})$ | $O(N)$ |
| **Layer $1 \dots \lceil\log_2 N\rceil$** | Interior Parent | $H_{\text{parent}} = \text{SHA256}(H_{\text{left}} \parallel H_{\text{right}})$ | $O(N)$ pairwise reductions |
| **Root Layer** | Cryptographic Anchor | $\mathbf{R}_{\text{Merkle}} = H_{\text{root}} \in \{0,1\}^{256}$ | $O(1)$ storage |

**Odd-Leaf Balance Rule:** If the count of nodes at any layer is odd, the trailing leaf is duplicated to maintain binary balance:

$$H_{N+1} = H_N \quad (\text{if } N \text{ is odd at any reduction level})$$

**Security Guarantee:** Any single-character alteration to any field in any event $E_k$ cascades upward, yielding $\mathbf{R}'_{\text{Merkle}} \neq \mathbf{R}_{\text{Merkle}}$ with probability $1 - 2^{-256}$.

---

### 60.3 $O(\log_2 N)$ Merkle Inclusion Proof (Audit Path) (§1.2)

To prove event $E_k$ is part of the case file without disclosing other events, the engine generates a minimal audit path:

$$\boldsymbol{\pi}_k = \Big\{ (S_1, \text{dir}_1), (S_2, \text{dir}_2), \dots, (S_{\lceil \log_2 N \rceil}, \text{dir}_{\lceil \log_2 N \rceil}) \Big\}$$

where $S_j \in \{0,1\}^{256}$ is the sibling hash at depth $j$ and $\text{dir}_j \in \{\text{LEFT}, \text{RIGHT}\}$.

**Verification Algorithm:**

1. Initialize: $v_0 = H_k$ (target leaf hash).
2. For $j = 1$ to $d = \lceil \log_2 N \rceil$:
$$v_j = \begin{cases} \text{SHA256}(v_{j-1} \parallel S_j) & \text{if } \text{dir}_j = \text{RIGHT} \\ \text{SHA256}(S_j \parallel v_{j-1}) & \text{if } \text{dir}_j = \text{LEFT} \end{cases}$$
3. Final admissibility verdict:
$$\text{VERDICT} = \begin{cases} \texttt{VALID (Admissible)} & \text{if } v_d = \mathbf{R}_{\text{Merkle}} \\ \texttt{INVALID (Tampered)} & \text{if } v_d \neq \mathbf{R}_{\text{Merkle}} \end{cases}$$

---

### 60.4 Golden Benchmark Test Vectors (Module 26)

| Vector | Test Condition | Expected Outcome |
| :--- | :--- | :--- |
| `VECTOR_P6_01` | 1-second timestamp alteration in $E_k$ | $\mathbf{R}'_{\text{Merkle}} \neq \mathbf{R}_{\text{Merkle}}$; proof $\implies$ INVALID |
| `VECTOR_26_MERKLE_A` | Single-event tree ($N=1$) | $\mathbf{R}_{\text{Merkle}} = H_1$; proof path length $= 0$ |
| `VECTOR_26_MERKLE_B` | Balanced trees ($N=4, N=8$) | Tree depth $= \log_2 N$; all proofs VALID |
| `VECTOR_26_MERKLE_C` | Odd-leaf counts ($N=3,5,7$) | Duplication applied; all $N$ events have VALID proofs |
| `VECTOR_26_MERKLE_D` | Proof path lengths ($N=2,4,8,16$) | Path length $= \lceil \log_2 N \rceil$ |
| `VECTOR_26_MERKLE_E` | Event order permutation ($E_1 \leftrightarrow E_2$) | Swapped root $\neq$ original root |
| `VECTOR_26_MERKLE_F` | Empty event list \| out-of-range index | `ValueError` raised |
| `VECTOR_26_MERKLE_G` | API endpoints (`/build-tree`, `/generate-proof`, `/verify-proof`) | 200 OK; proof reconstructs original root |

---

## 61. Zero-Knowledge Proof (ZKP) Blind Forensic Auditor Engine (Module 27)

**Research Reference:** Pillar 6 Research §2 (GDPR Article 9 • FRE 702 / Daubert • W3C Verifiable Credentials • Circom / SnarkJS Groth16)

### 61.1 Poseidon Cryptographic Commitment (§2.1)

To prevent Personally Identifiable Information (PII) or raw STR profiles from exposure in public court records, the private witness $\mathbf{G}_S = (a_{1,1}, a_{1,2}, \dots, a_{L,2})$ is committed into prime field $\mathbb{F}_p$ ($p = 21888242871839275222246405745257275088548364400416034343698204186575808495617$):

$$H(\mathbf{G}_S) = \text{Poseidon}(\mathbf{G}_S \parallel \text{Salt}_S) \pmod p$$

$$H(\mathbf{G}_E) = \text{Poseidon}(\mathbf{G}_E \parallel \text{Salt}_E) \pmod p$$

---

### 61.2 R1CS Locus-Level Arithmetic Equality Gadget (§2.1)

For each allele position $(l,m) \in [1..L] \times [1..2]$, equality indicator $m_{l,m} \in \{0, 1\}$ and auxiliary witness $b_{l,m} \in \mathbb{F}_p$:

$$(a_{l,m} - e_{l,m}) \cdot b_{l,m} = 1 - m_{l,m} \pmod p$$

$$m_{l,m} \cdot (a_{l,m} - e_{l,m}) = 0 \pmod p$$

**Threshold Score Constraint:**
$$M_{\text{match}} = \sum_{l=1}^L \sum_{m=1}^2 m_{l,m} \ge M_{\text{thresh}} \implies M_{\text{match}} - M_{\text{thresh}} - \Delta = 0 \quad (\Delta \ge 0)$$

---

### 61.3 Groth16 BN254 Bilinear Pairing Verification (§2.2)

Public signals vector: $\mathbf{x} = \big(H(\mathbf{G}_E), M_{\text{thresh}}, H(\mathbf{G}_S)\big)$.

Given proof $\boldsymbol{\pi}_{\text{ZKP}} = (A \in \mathbb{G}_1, B \in \mathbb{G}_2, C \in \mathbb{G}_1)$ and verification key $VK = (\alpha, \beta, \gamma, \delta, \{K_i\}_{i=0}^l)$:

$$e(A, B) = e(\alpha, \beta) \cdot e\left( \sum_{i=0}^l x_i K_i, \gamma \right) \cdot e(C, \delta)$$

Evaluated as a single multi-pairing product in target field $\mathbb{G}_T$:

$$e(A, B) \cdot e(-\alpha, \beta) \cdot e\left( -\sum_{i=0}^l x_i K_i, \gamma \right) \cdot e(-C, \delta) = 1_{\mathbb{G}_T}$$

**Cryptographic Soundness Bound:**
$$\epsilon \le \frac{d}{p} \approx 10^{-75}$$

---

### 61.4 Golden Benchmark Test Vectors (Module 27)

| Vector | Test Scenario | Verified Mathematical Invariant | Status |
| :--- | :--- | :--- | :---: |
| `VECTOR_27_ZKP_A` | Full 24-locus diploid profile ($48/48$ alleles) | $M_{\text{match}} = 48 \ge 40 \implies \text{VALID}$; pairing passes | ✅ Verified |
| `VECTOR_27_ZKP_B` | Partial profile match ($42/48$ alleles) | $M_{\text{match}} = 42 \ge 40 \implies \text{VALID}$; $\Delta = +2$ | ✅ Verified |
| `VECTOR_27_ZKP_C` | Below threshold match ($32/48$ alleles) | $M_{\text{match}} = 32 < 40 \implies \texttt{ValueError}$ proof rejected | ✅ Verified |
| `VECTOR_27_ZKP_D` | Tampered witness commitment | Public signal discrepancy detection | ✅ Verified |
| `VECTOR_27_ZKP_E` | Corrupted Groth16 proof element ($A' \in \mathbb{G}_1$) | Pairing evaluation rejects malformed coordinates | ✅ Verified |
| `VECTOR_27_ZKP_F` | Poseidon commitment determinism & entropy | Deterministic for same salt; strictly in $[0, p)$ | ✅ Verified |
| `VECTOR_27_ZKP_G` | Domain validation (empty loci, $M_{\text{thresh}} \le 0$) | $\texttt{ValueError}$ raised | ✅ Verified |
| `VECTOR_27_ZKP_H` | FastAPI REST pipeline (`/witness-commitment` $\to$ `/synthesize-proof` $\to$ `/verify-pairing`) | 200 OK end-to-end; $100\%$ pairing verification | ✅ Verified |

---

## 62. ISO/IEC 17025:2017 Measurement Uncertainty & Calibration Budget Engine (Module 28)

**Research Reference:** Pillar 6 Research §3 & §6 (ISO/IEC 17025:2017 Clause 7.6 • JCGM 100:2008 GUM • SWGDAM QAS 2020)

### 62.1 Combined Standard Uncertainty ($u_c(y)$) (§3.1)

For quantitative DNA concentration estimation ($y = f(x_1, \dots, x_N)$ in $\text{ng/}\mu\text{L}$), the combined standard uncertainty $u_c(y)$ propagates individual input standard uncertainties $u(x_i)$ and sensitivity coefficients $c_i = \frac{\partial f}{\partial x_i}$:

$$u_c^2(y) = \sum_{i=1}^N (c_i \cdot u_i)^2 + 2 \sum_{i=1}^{N-1} \sum_{j=i+1}^N c_i c_j r_{ij} u_i u_j$$

where $r_{ij} \in [-1, 1]$ is the correlation coefficient between quantities $x_i$ and $x_j$.

**Variance Percentage Contribution:**
$$\text{Pct}_i = \frac{(c_i \cdot u_i)^2}{u_c^2(y)} \times 100\%$$

---

### 62.2 Expanded Uncertainty Budget at 95.45% Confidence ($U_{95\%}$) (§3.1 & §3.2)

Under normal Gaussian distribution, coverage factor $k = 2.00$ defines the courtroom reported uncertainty interval:

$$U_{95\%} = k \cdot u_c(y) = 2.00 \cdot u_c(y)$$

$$\text{Reported Interval} = y \pm U_{95\%} \quad (\text{ng/}\mu\text{L}) \implies \left[ y - U_{95\%}, \; y + U_{95\%} \right]$$

---

### 62.3 Canonical Forensic DNA Calibration Budget (`VECTOR_P6_02` Ground Truth) (§3.2)

| Quantity ($x_i$) | Standard Value ($u_i$) | Distribution | Sensitivity ($c_i$) | Variance Contribution $(c_i u_i)^2$ | % Variance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Micro-Pipette Volume ($x_1$)** | $0.01323 \text{ ng/}\mu\text{L}$ | Rectangular ($\sqrt{3}$) | $1.00$ | $0.000175$ | $6.03\%$ |
| **Thermal Gradient ($x_2$)** | $0.01500 \text{ ng/}\mu\text{L}$ | Normal Gaussian ($k=1$) | $1.00$ | $0.000225$ | $7.76\%$ |
| **qPCR Standard Curve ($x_3$)** | $0.03000 \text{ ng/}\mu\text{L}$ | Normal Gaussian ($k=1$) | $1.00$ | $0.000900$ | $31.03\%$ |
| **Master Mix Amplification ($x_4$)** | $0.04000 \text{ ng/}\mu\text{L}$ | Normal Gaussian ($k=1$) | $1.00$ | $0.001600$ | $55.17\%$ |
| **Combined Standard ($u_c$)** | **$0.05385 \text{ ng/}\mu\text{L}$** | Normal Gaussian | N/A | **$\sum = 0.002900$** | **$100.00\%$** |
| **Expanded Budget ($U_{95\%}$)** | **$0.10770 \text{ ng/}\mu\text{L}$** | Expanded ($k=2.00$) | N/A | **Reported: $\pm 0.10770$** | N/A |

---

### 62.4 Proficiency Testing Consensus $z$-Score (§3.2)

Evaluates inter-laboratory proficiency rounds relative to consensus statistics:

$$z = \frac{x_{\text{lab}} - \mu_{\text{consensus}}}{\sigma_{\text{consensus}}}$$

* $|z| \le 2.0 \implies$ **`SATISFACTORY`** (Fully Calibrated, ISO/IEC 17025 Compliant).
* $2.0 < |z| < 3.0 \implies$ **`QUESTIONABLE`** (Warning State, Internal Review Required).
* $|z| \ge 3.0 \implies$ **`UNSATISFACTORY`** (Non-Compliant Alert, Corrective Action Required).

---

### 62.5 Golden Benchmark Test Vectors (Module 28)

| Vector | Test Scenario | Verified Invariant | Status |
| :--- | :--- | :--- | :---: |
| `VECTOR_P6_02` | Canonical 4-component calibration budget | $u_c = 0.05385\,\text{ng/}\mu\text{L}, U_{95\%} = 0.10770\,\text{ng/}\mu\text{L}$ ($k=2.00$) | ✅ Verified |
| `VECTOR_28_UNCERT_A` | Custom sensitivity coefficients ($c_i \neq 1.0$) | Weighted variance sum $(c_1 u_1)^2 + (c_2 u_2)^2$ | ✅ Verified |
| `VECTOR_28_UNCERT_B` | Correlated components ($r_{ij} > 0$) | Positive covariance expansion $2 c_i c_j r_{ij} u_i u_j$ | ✅ Verified |
| `VECTOR_28_UNCERT_C` | Satisfactory proficiency round ($|z| \le 2.0$) | $z = +1.000 \implies \text{SATISFACTORY}$, compliant | ✅ Verified |
| `VECTOR_28_UNCERT_D` | Questionable warning round ($2.0 < |z| < 3.0$) | $z = +2.400 \implies \text{QUESTIONABLE}$, non-compliant | ✅ Verified |
| `VECTOR_28_UNCERT_E` | Unsatisfactory breach round ($|z| \ge 3.0$) | $z = +4.000 \implies \text{UNSATISFACTORY}$, corrective action | ✅ Verified |
| `VECTOR_28_UNCERT_F` | Domain validation ($y < 0, \sigma \le 0, u_i < 0$) | $\texttt{ValueError}$ raised | ✅ Verified |
| `VECTOR_28_UNCERT_G` | FastAPI REST pipeline (`/calculate-budget`, `/proficiency-z-score`) | 200 OK end-to-end | ✅ Verified |

---

## 63. Dynamic ENFSI Evaluative Reporting & Verbal Scale Engine (Module 29)

**Research Reference:** Pillar 6 Research §4.1, §4.2, §4.3, and §6 Artifact C/D (`research/pillar_6_lims_zkp_reporting_research.md`)

### 63.1 Formal Bayesian Evaluative Framework (§4.1)

The Likelihood Ratio $LR$ is the ratio of conditional evidence probabilities under competing propositions:

$$LR = \frac{P(E \mid H_p, I)}{P(E \mid H_d, I)} \implies \frac{P(H_p \mid E, I)}{P(H_d \mid E, I)} = LR \times \frac{P(H_p \mid I)}{P(H_d \mid I)}$$

**Prosecutor's Fallacy Shield (Active):** $P(E \mid H_p) \neq P(H_p \mid E)$. The LR addresses the probability of the evidence given the proposition, **not** the probability of guilt given the evidence.

---

### 63.2 ENFSI (2017) 7-Tier Verbal Strength Scale Step Function (§4.2)

$$V(LR_{\text{eff}}) = \begin{cases} \text{Tier 0: Inconclusive / Neutral}, & LR_{\text{eff}} = 1.0 \\ \text{Tier 1: Weak Support}, & 1.0 < LR_{\text{eff}} \le 10.0 \\ \text{Tier 2: Moderate Support}, & 10.0 < LR_{\text{eff}} \le 100.0 \\ \text{Tier 3: Moderately Strong Support}, & 100.0 < LR_{\text{eff}} \le 1000.0 \\ \text{Tier 4: Strong Support}, & 1000.0 < LR_{\text{eff}} \le 10000.0 \\ \text{Tier 5: Very Strong Support}, & 10000.0 < LR_{\text{eff}} \le 1{,}000{,}000.0 \\ \text{Tier 6: Extremely Strong Support}, & LR_{\text{eff}} > 1{,}000{,}000.0 \end{cases}$$

**Symmetric Defense Inversion (§4.2):** When $LR < 1.0$, evaluate $LR_{\text{def}} = 1/LR$ symmetrically for defense proposition $H_d$.

---

### 63.3 Standardized Bilingual Courtroom Verbal Scale (Research §4.2 Table & §6 Artifact A)

| Tier | $LR$ Range | $\log_{10}(LR)$ | English Expression | Turkish Expression |
| :--- | :--- | :--- | :--- | :--- |
| **0** | $LR = 1.0$ | $0.0$ | *Neutral / Inconclusive* | *Nötr / Sonuçsuz Bulgular* |
| **1** | $1 < LR \le 10$ | $0 < \log \le 1$ | *Weak support for prosecution proposition* | *İddia makamının hipotezi lehine zayıf destek* |
| **2** | $10 < LR \le 100$ | $1 < \log \le 2$ | *Moderate support for prosecution proposition* | *İddia makamının hipotezi lehine orta düzeyde destek* |
| **3** | $100 < LR \le 1{,}000$ | $2 < \log \le 3$ | *Moderately strong support for prosecution proposition* | *İddia makamının hipotezi lehine orta-güçlü destek* |
| **4** | $1{,}000 < LR \le 10{,}000$ | $3 < \log \le 4$ | *Strong support for prosecution proposition* | *İddia makamının hipotezi lehine güçlü destek* |
| **5** | $10{,}000 < LR \le 10^6$ | $4 < \log \le 6$ | *Very strong support for prosecution proposition* | *İddia makamının hipotezi lehine çok güçlü destek* |
| **6** | $LR > 10^6$ | $\log > 6$ | *Extremely strong support for prosecution proposition* | *İddia makamının hipotezi lehine aşırı güçlü destek* |

---

### 63.4 Statutory Legal Admissibility Audit: Daubert FRE 702 & Frye (§4.3)

**Daubert Standard (Federal Rule of Evidence 702) — 4 Pillars:**

| Pillar | Criterion | FORENZA Implementation |
| :--- | :--- | :--- |
| **1** | Falsifiability & Testability | Automated deterministic pytest unit test suites |
| **2** | Known Error Rate | $P_{\text{error}} \le 10^{-6}$ (verified via unit vectors) |
| **3** | Peer-Reviewed Literature | Published STRmix, EuroForMix, ENFSI, EMPOP algorithms |
| **4** | Standards Control | SWGDAM (2020) QAS and ISO/IEC 17025:2017 accreditation |

**Frye Standard:** General scientific acceptance within the international forensic genetics community (ISFG, ENFSI, SWGDAM).

---

### 63.5 Golden Benchmark Test Vectors (Module 29)

| Vector | Test Scenario | Verified Invariant | Status |
| :--- | :--- | :--- | :---: |
| `VECTOR_P6_03` | $LR = 3.5 \times 10^7$ Ground Truth | Tier 6; $\log_{10} LR \approx 7.544$; Turkish: "…aşırı güçlü destek sağlamaktadır." | ✅ Verified |
| `VECTOR_29_ENFSI_A` | Neutral / Inconclusive ($LR = 1.0$) | Tier 0; $\log_{10} LR = 0.0$; "nötr" in statement | ✅ Verified |
| `VECTOR_29_ENFSI_B` | All Tier 1–6 boundary transitions (12 parametrized cases) | Step-function strict partition verified at each threshold | ✅ Verified |
| `VECTOR_29_ENFSI_C` | Defense symmetric inversion ($LR = 0.0001 \to H_d$ Tier 4) | $LR_{\text{def}} = 10{,}000$; "savunma hipotezi (H_d)" in statement | ✅ Verified |
| `VECTOR_29_ENFSI_D` | Bilingual concordance (EN & TR for Tiers 1–6) | EN and TR phrases concordant; language output exclusive | ✅ Verified |
| `VECTOR_29_ENFSI_E` | Daubert FRE 702 4-pillar & Frye audit | Full compliance passes; error rate $> 10^{-6}$ and missing standards fail | ✅ Verified |
| `VECTOR_29_ENFSI_F` | Domain validation ($LR \le 0$) | $\texttt{ValueError}$ raised | ✅ Verified |
| `VECTOR_29_ENFSI_G` | FastAPI REST pipeline (`/evaluative-report`, `/daubert-compliance`) | 200 OK end-to-end; 400 on invalid LR | ✅ Verified |

---

## 64. Module 30: 3D Spatial Crime Scene Reconstruction & Interactive Juror Visualizer Engine

**Research Reference:** Pillar 6 §5.1–§5.2  
**Engine:** `backend/node/services/forensic/court/spatial_reconstruction_engine.py`  
**API Endpoints:** `POST /forensic/court/spatial/transform-se3`, `/spatial/confidence-ellipsoid`, `/spatial/reconstruct-scene`  
**UI Component:** `frontend/src/components/analysis/EvidenceManagementPanel.tsx` (Interactive 3D Juror Visualizer)

---

### 64.1 Spatial Transformation & Scene Coordinate Registration (§5.1)

Local sensor coordinates $\mathbf{X}_{\text{local}}$ are mapped to the global scene datum $\mathbf{X}_{\text{scene}} \in \mathbb{R}^3$ via the **Special Euclidean Group** $SE(3)$:

$$\mathbf{X}_{\text{scene}} = \mathbf{R} \cdot \mathbf{X}_{\text{local}} + \mathbf{T}$$

where $\mathbf{R} = \mathbf{R}_z(\psi)\,\mathbf{R}_y(\theta)\,\mathbf{R}_x(\phi)$ is the **Euler ZYX** composition:

$$\mathbf{R}_x(\phi) = \begin{pmatrix} 1 & 0 & 0 \\ 0 & \cos\phi & -\sin\phi \\ 0 & \sin\phi & \cos\phi \end{pmatrix}, \quad
\mathbf{R}_y(\theta) = \begin{pmatrix} \cos\theta & 0 & \sin\theta \\ 0 & 1 & 0 \\ -\sin\theta & 0 & \cos\theta \end{pmatrix}, \quad
\mathbf{R}_z(\psi) = \begin{pmatrix} \cos\psi & -\sin\psi & 0 \\ \sin\psi & \cos\psi & 0 \\ 0 & 0 & 1 \end{pmatrix}$$

**Rotation Matrix Invariants** (verified by unit tests):
- **Orthogonality:** $\|\mathbf{R}\mathbf{R}^T - \mathbf{I}\|_F < 10^{-10}$
- **Determinant:** $|\det(\mathbf{R}) - 1| < 10^{-10}$

---

### 64.2 Multi-Sensor Point-to-Plane Registration Residual (§5.1)

The multi-sensor registration objective minimizes the **point-to-plane residual error**:

$$\min_{\mathbf{R},\,\mathbf{T}} \sum_{k=1}^{K} \left\| \mathbf{n}_k^T \cdot \left( \mathbf{R} \cdot \mathbf{p}_k + \mathbf{T} - \mathbf{q}_k \right) \right\|^2$$

where $\mathbf{p}_k$ are source sensor points, $\mathbf{q}_k$ are target reference points, and $\mathbf{n}_k$ are unit surface normals at the target.

**Sensor Calibration Precision Table (§5.1):**

| Spatial Sensor Input | Raw Resolution | Registration Target | Global Precision $(\sigma_x, \sigma_y, \sigma_z)$ |
| :--- | :--- | :--- | :--- |
| **Terrestrial LiDAR Scanning** | $\pm 1.5\,\text{mm}$ at $10\,\text{m}$ | Absolute Scene Geometric Shell | $\pm 0.002\,\text{m}$ |
| **BPA Trajectory Flight Origin** | $\pm 15.0\,\text{mm}$ ellipsoid radius | Bloodstain Convergence Point | $\pm 0.012\,\text{m}$ |
| **Ballistics Terminal Trajectory** | $\pm 0.5°$ directional deviation | Bullet Impact Vector Line | $\pm 0.005\,\text{m}$ |
| **Suspect Landmark Coordinates** | $\pm 5.0\,\text{mm}$ anatomical drift | Biological Sample Collection Point | $\pm 0.008\,\text{m}$ |

---

### 64.3 Probabilistic 95% Volumetric Confidence Ellipsoid (§5.2)

Positional uncertainty is rendered as a **95% confidence ellipsoid** defined by the spatial covariance $\boldsymbol{\Sigma}$:

$$(\mathbf{X} - \boldsymbol{\mu})^T \boldsymbol{\Sigma}^{-1} (\mathbf{X} - \boldsymbol{\mu}) \;\le\; \chi^2_{3,\,0.95} \approx 7.815$$

Via eigendecomposition $\boldsymbol{\Sigma} = \mathbf{V}\boldsymbol{\Lambda}\mathbf{V}^T$ with $\lambda_1 \ge \lambda_2 \ge \lambda_3 > 0$, the semi-axis lengths $(a, b, c)$ are:

$$a = \sqrt{\lambda_1 \cdot 7.815}, \qquad b = \sqrt{\lambda_2 \cdot 7.815}, \qquad c = \sqrt{\lambda_3 \cdot 7.815}$$

**Ellipsoid Volume:**

$$V = \frac{4}{3}\,\pi\,a\,b\,c$$

**Ground-Truth Benchmark (Isotropic $\boldsymbol{\Sigma} = \mathbf{I}_3$, $\sigma = 1.0\,\text{m}$):**

$$a = b = c = \sqrt{1.0 \times 7.815} = 2.7955\,\text{m}, \qquad V = \frac{4}{3}\,\pi\,(2.7955)^3 \approx 91.588\,\text{m}^3$$

---

### 64.4 Golden Benchmark Test Vectors (Module 30)

| Vector | Test Scenario | Verified Invariant | Status |
| :--- | :--- | :--- | :---: |
| `VECTOR_30_SPATIAL_A` | $SE(3)$ identity transform ($\mathbf{R}=\mathbf{I}$, $\mathbf{T}=\mathbf{0}$) | $\mathbf{X}_{\text{scene}} = \mathbf{X}_{\text{local}}$ exact to $<10^{-10}$; orthogonality residual $<10^{-10}$ | ✅ Verified |
| `VECTOR_30_SPATIAL_B` | Euler rotation invariants (roll, pitch, yaw $\in \{90°, 45°, 30°, 180°\}$) | $\|\mathbf{R}\mathbf{R}^T - \mathbf{I}\|_F < 10^{-10}$; $\|\det(\mathbf{R}) - 1\| < 10^{-10}$; pure-axis mappings exact | ✅ Verified |
| `VECTOR_30_SPATIAL_C` | Pure translation ($\mathbf{R}=\mathbf{I}$, $\mathbf{T}=[t_x, t_y, t_z]$) | $\mathbf{X}_{\text{scene}} = \mathbf{X}_{\text{local}} + \mathbf{T}$; origin maps exactly to $\mathbf{T}$ under any rotation | ✅ Verified |
| `VECTOR_30_SPATIAL_D` | 95% CI ellipsoid (isotropic $\boldsymbol{\Sigma}=\mathbf{I}_3$ and anisotropic $\text{diag}(4,2,1)$) | $a=b=c=\sqrt{7.815}\approx2.7955$; $\chi^2=7.815$ exact; axes descending; volume formula $V=\frac{4}{3}\pi abc$ | ✅ Verified |
| `VECTOR_30_SPATIAL_E` | Multi-sensor fusion (LiDAR, BPA, Ballistics, DNA) precision conformance | $\sigma_{\text{LiDAR}}=0.002$, $\sigma_{\text{BPA}}=0.012$, $\sigma_{\text{Ball}}=0.005$, $\sigma_{\text{DNA}}=0.008$; centroid, bounding box correct | ✅ Verified |
| `VECTOR_30_SPATIAL_F` | Domain validation (singular/indefinite covariance; empty scene; mismatched lengths) | `ValueError` raised for all invalid inputs | ✅ Verified |
| `VECTOR_30_SPATIAL_G` | FastAPI REST integration (`/transform-se3`, `/confidence-ellipsoid`, `/reconstruct-scene`) | 200 OK end-to-end; 400 on invalid inputs; $\chi^2=7.815$ in all responses | ✅ Verified |

---

## 65. Multi-Isotope Spatial Isoscape Provenance Engine (Module 31)

### 65.1 Global Meteoric Water Line (GMWL) & Precipitation Isoscapes
Precipitation isotopic fractionation follows the Harmon Craig Global Meteoric Water Line:

$$\delta^2\text{H} = 8.0 \cdot \delta^{18}\text{O} + 10.0, \qquad d = \delta^2\text{H} - 8.0 \cdot \delta^{18}\text{O} \quad (\text{Deuterium Excess})$$

Precipitation $\delta^{18}\text{O}_{\text{precip}}$ is modeled via the Terzer-Wassenaar global spatial equation:

$$\delta^{18}\text{O}_{\text{precip}}(\theta, \lambda, h) = \beta_0 + \beta_1 |\theta| + \beta_2 \theta^2 + \beta_3 h + \beta_4 \text{dist}_{\text{coast}}(\theta, \lambda)$$

### 65.2 Biological Tissue Fractionation & Biomineral Calibration
Tooth enamel bioapatite $(\delta^{18}\text{O}_{\text{carbonate}} \to \delta^{18}\text{O}_{\text{water}})$ conversion (Chenery / Daux):

$$\delta^{18}\text{O}_{\text{water}} = 1.590 \cdot \delta^{18}\text{O}_{\text{carbonate}} - 48.634$$

Scalp hair keratin $(\delta^2\text{H}_{\text{hair}} \to \delta^2\text{H}_{\text{water}})$ conversion (Ehleringer):

$$\delta^2\text{H}_{\text{water}} = \frac{\delta^2\text{H}_{\text{hair}} + 26.0}{0.910}$$

### 65.3 Bataille High-Resolution Strontium ($^{87}\text{Sr}/^{86}\text{Sr}$) Model
Bioavailable strontium integrates bedrock lithology, weathering rates, and atmospheric deposition:

$$\left(\frac{^{87}\text{Sr}}{^{86}\text{Sr}}\right)_{\text{bio}} = f_{\text{bedrock}} \cdot \left(\frac{^{87}\text{Sr}}{^{86}\text{Sr}}\right)_{\text{rock}} + (1 - f_{\text{bedrock}}) \cdot \left(\frac{^{87}\text{Sr}}{^{86}\text{Sr}}\right)_{\text{precip}}$$

### 65.4 Continuous Multivariate Gaussian Spatial Likelihood & Golden Benchmark
At geographic coordinate $(\theta_i, \lambda_j)$, the $K$-dimensional isotopic vector likelihood is:

$$\mathcal{L}(\mathbf{z}_{\text{obs}} \mid \theta_i, \lambda_j) = \frac{1}{(2\pi)^{K/2} |\boldsymbol{\Sigma}_{ij}|^{1/2}} \exp\left( -\frac{1}{2} (\mathbf{z}_{\text{obs}} - \boldsymbol{\mu}_{ij})^T \boldsymbol{\Sigma}_{ij}^{-1} (\mathbf{z}_{\text{obs}} - \boldsymbol{\mu}_{ij}) \right)$$

* **`VECTOR_GEO_01` (Swiss Prealps):** Tooth $\delta^{18}\text{O}_{\text{carb}} = 25.40‰ \to \delta^{18}\text{O}_{\text{water}} = -8.25‰$, $^{87}\text{Sr}/^{86}\text{Sr} = 0.70882$, Hair $\delta^2\text{H} = -78.4‰ \to \delta^2\text{H}_{\text{water}} = -57.58‰$. Centroid: $\text{Lat} = 46.91^\circ\text{N}, \text{Lon} = 8.39^\circ\text{E}$, $R_{95\%} = 48.50\text{ km}, LR = 3.25 \times 10^4$.

---

## 66. Forensic Soil Pedology, QXRD Rietveld & CoDa Engine (Module 32)

### 66.1 Aitchison Centered Log-Ratio ($\text{CLR}$) Transform (ASTM E3272-21)
For a compositional mineral vector $\mathbf{x} = (x_1, \dots, x_D)^T$ on the simplex $\mathcal{S}^D$:

$$g(\mathbf{x}) = \left(\prod_{i=1}^D x_i\right)^{1/D}, \qquad \text{clr}(\mathbf{x}) = \left( \ln\frac{x_1}{g(\mathbf{x})}, \dots, \ln\frac{x_D}{g(\mathbf{x})} \right)^T, \qquad \sum_{i=1}^D \text{clr}_i(\mathbf{x}) = 0$$

### 66.2 Zircon-Tourmaline-Rutile (ZTR) Heavy Mineral Maturity Index

$$\text{ZTR} = \frac{\text{Zircon} + \text{Tourmaline} + \text{Rutile}}{\sum \text{Non-Micaceous Transparent Heavy Minerals}} \times 100\%$$

### 66.3 Minimum Covariance Determinant (MCD) Robust Mahalanobis Distance & Hotelling $T^2$

$$D_M^2(\mathbf{x}_Q, \bar{\mathbf{x}}_C) = (\text{clr}(\mathbf{x}_Q) - \bar{\mathbf{x}}_C)^T \mathbf{S}_{\text{MCD}}^{-1} (\text{clr}(\mathbf{x}_Q) - \bar{\mathbf{x}}_C)$$

$$T^2 = \frac{n_Q \cdot n_C}{n_Q + n_C} D_M^2 \implies F = \frac{n_Q + n_C - p - 1}{(n_Q + n_C - 2)p} T^2 \sim F(p, n_Q + n_C - p - 1)$$

### 66.4 Munsell $\to$ CIEDE2000 ($\Delta E_{00}^*$) Soil Colorimetric Difference

$$\Delta E_{00}^* = \sqrt{\left(\frac{\Delta L'}{k_L S_L}\right)^2 + \left(\frac{\Delta C'}{k_C S_C}\right)^2 + \left(\frac{\Delta H'}{k_H S_H}\right)^2 + R_T \left(\frac{\Delta C'}{k_C S_C}\right)\left(\frac{\Delta H'}{k_H S_H}\right)}$$

* **`VECTOR_GEO_02`:** Questioned boot trace vs crime scene control: $D_M = 1.4200, F = 0.0560, p = 0.999, \Delta E_{00}^* = 0.00, \text{ZTR} = 9.50\%, LR = 4.50 \times 10^3$, ASTM E3272 `DEFINITIVE_INCLUSION`.

---

## 67. Forensic Palynology & Environmental eDNA Metagenomics Engine (Module 33)

### 67.1 Relative Pollen Frequency ($\text{RPF}$) & Tauber Distance

$$\text{RPF}_i = \frac{n_i}{\sum_{j=1}^M n_j} \times 100\%, \qquad \sum_{i=1}^M \text{RPF}_i = 100.0\% \quad (N_{\text{total}} \ge 300)$$

Multivariate dissimilarities across palynomorph taxa profiles $\mathbf{p}$ and $\mathbf{q}$:
- **Bray-Curtis:** $d_{\text{BC}}(\mathbf{p}, \mathbf{q}) = \frac{\sum |p_i - q_i|}{\sum (p_i + q_i)}$
- **Cosine Similarity:** $S_{\text{cos}}(\mathbf{p}, \mathbf{q}) = \frac{\mathbf{p} \cdot \mathbf{q}}{\|\mathbf{p}\| \|\mathbf{q}\|}$
- **Canberra Distance:** $d_{\text{Can}}(\mathbf{p}, \mathbf{q}) = \sum \frac{|p_i - q_i|}{|p_i| + |q_i|}$

### 67.2 6-Biome Ecological Classifier & 16S/ITS Spatial Regression
Classifies questioned trace into 6 reference biomes:
1. `DECIDUOUS_FOREST` (*Quercus*, *Fagus*, *Carpinus*)
2. `CONIFEROUS_FOREST` (*Pinus*, *Picea*, *Abies*)
3. `STEPPE_GRASSLAND` (*Poaceae*, *Artemisia*, *Chenopodiaceae*)
4. `RUDERAL_URBAN` (*Plantago*, *Urtica*, *Taraxacum*)
5. `AGRICULTURAL_CEREAL` (*Cerealia*, *Secale*, *Brassica*)
6. `COASTAL_HALOPHYTE` (*Salicornia*, *Tamarix*)

16S rRNA V4 and ITS fungal ASV spatial regression predicts provenance centroid coordinates $(\hat{\theta}, \hat{\lambda})$.

---

## 68. Bayesian Rossmo Geographic Profiling Engine (Module 34)

### 68.1 Rossmo Targeted Hunting Formula
For $C$ serial crime scenes $(x_c, y_c)$ on a discrete grid, the operational hunting probability $P(x_i, y_j)$ is:

$$P(x_i, y_j) = k \sum_{c=1}^C \left[ \frac{\phi_{ijc}}{( |x_i - x_c| + |y_j - y_c| )^f} + \frac{(1 - \phi_{ijc}) B^{g - f}}{( 2B - (|x_i - x_c| + |y_j - y_c|) )^g} \right]$$

where:
- $\phi_{ijc} = 1$ if $(|x_i - x_c| + |y_j - y_c|) > B$, else $0$.
- Buffer zone: $B = 1.50\text{ km}$, decay exponent: $f = 1.60$, buffer exponent: $g = 0.80$.

### 68.2 WGS84 Vincenty Ellipsoidal Geodesic Algorithm
Computes exact geodesic distance $s$ on the WGS84 reference ellipsoid ($a=6378137.0\text{ m}, f=1/298.257223563, b=6356752.314245\text{ m}$) via iterative spherical reduction:

$$\tan\sigma = \frac{\sqrt{(\cos U_2 \sin\Delta\lambda)^2 + (\cos U_1 \sin U_2 - \sin U_1 \cos U_2 \cos\Delta\lambda)^2}}{\sin U_1 \sin U_2 + \cos U_1 \cos U_2 \cos\Delta\lambda}$$

### 68.3 Canter Circle Hypothesis & Search Efficiency Index ($\text{SEI}$)

$$D_{\max} = \max_{j > k} d(C_j, C_k), \qquad R_{\text{canter}} = \frac{D_{\max}}{2}$$

- If $(x_0, y_0) \in \mathcal{C}(R_{\text{canter}}) \implies$ `MARAUDER` (Anchor inside crime cluster).
- If $(x_0, y_0) \notin \mathcal{C}(R_{\text{canter}}) \implies$ `COMMUTER` (Offender travels into buffer zone).
- Search Efficiency Index: $\text{SEI} = \left( 1 - \frac{S_{p\%}}{S_{\text{total}}} \right) \times 100\% \ge 90\%$.

* **`VECTOR_GEO_03`:** Peak Anchor $(x_0, y_0) = (6.80\text{ km}, 11.40\text{ km}), S_{5\%} = 14.20\text{ km}^2, \text{SEI} = 96.45\%, D_{\max} = 9.42\text{ km}$, `MARAUDER`.

---

## 69. Multi-Criteria Bayesian Evidence Fusion Engine (Module 35)

### 69.1 Joint Posterior Spatial Probability Raster Multiplier

$$P(\theta_i, \lambda_j \mid \mathbf{E}) = \frac{P_0(\theta_i, \lambda_j) \prod_{k=1}^M \left[ \mathcal{L}_k(\mathbf{e}_k \mid \theta_i, \lambda_j) \right]^{w_k}}{\sum_{u} \sum_{v} P_0(\theta_u, \lambda_v) \prod_{k=1}^M \left[ \mathcal{L}_k(\mathbf{e}_k \mid \theta_u, \lambda_v) \right]^{w_k}}$$

### 69.2 2D Adaptive Gaussian Kernel Density Estimation (KDE)
Bivariate Gaussian kernel with Silverman's rule of thumb bandwidths $h_x = \hat{\sigma}_x n^{-1/6}, h_y = \hat{\sigma}_y n^{-1/6}$:

$$\hat{f}(x, y) = \frac{1}{2\pi n h_x h_y} \sum_{i=1}^n \exp\left( -\frac{1}{2} \left[ \left(\frac{x - x_i}{h_x}\right)^2 + \left(\frac{y - y_i}{h_y}\right)^2 \right] \right)$$

### 69.3 ISO/IEC 17025 & ENFSI 2017 7-Tier Bilingual Evaluative Reporting
Translates composite fused likelihood ratio ($LR_{\text{fused}} \ge 10^8$) into standard ENFSI Tier 6 (`EXTREMELY_STRONG_SUPPORT`) statements with active Prosecutor's Fallacy shields.

---

## 70. Multi-Format Forensic DNA & SNP Terminal Ingestion Engine

### 70.1 Expanded 24-Locus STR Multiplex & NRC II Allele Frequency Bounding
Under National Research Council (NRC II) Recommendation 4.1 for the NIST 1036 dataset ($N = 1036$):

$$p_{\min} = \frac{5}{2N} = \frac{5}{2 \times 1036} = \frac{5}{2072} \approx 0.00241313$$

Dirichlet-Laplace Bayesian smoothing across $K$ observed allelic classes:

$$\hat{p}_i = \frac{k_i + \alpha}{2N + K\alpha}, \qquad \alpha = 1.0$$

Balding-Nichols coancestry match probability ($\theta \in \{0.01, 0.03\}$):
- **Homozygous ($A_i A_i$):**
  $$P(A_i A_i \mid A_i A_i) = \frac{2\theta + (1-\theta)p_i}{1+\theta} \cdot \frac{3\theta + (1-\theta)p_i}{1+2\theta}$$
- **Heterozygous ($A_i A_j$):**
  $$P(A_i A_j \mid A_i A_j) = 2 \cdot \frac{\theta + (1-\theta)p_i}{1+\theta} \cdot \frac{\theta + (1-\theta)p_j}{1+2\theta}$$

### 70.2 Amelogenin Y-Null Deletion & Sex Aneuploidy Model
Interstitial deletion on Yp11.2 priors:

$$P(Y_{\text{null}} \mid \text{SAS}) = 0.0180 \quad (1.80\%), \qquad P(Y_{\text{null}} \mid \text{EUR}) = 0.0002 \quad (0.02\%)$$

- Amelogenin `X` + *DYS391* ($\ge 10$) $\to$ `Male with AMELY Deletion (Yp11.2 Interstitial Deletion)`.
- Amelogenin `X, Y` + $h_X > 2.0 \cdot h_Y \to$ `Male Aneuploidy (47,XXY Klinefelter Syndrome)`.
- Amelogenin `X, Y` + SRY Negative $\to$ `46,XY Female / Swyer Syndrome`.

### 70.3 Capillary Electropherogram (EPG) Quality Gates & Degradation Index ($DI$)
- **Analytical Threshold:** $AT = 50.0\text{ RFU}$ (Baseline noise filter).
- **Stochastic Threshold:** $ST = 200.0\text{ RFU}$ (Sister allele dropout boundary).
- **Heterozygote Balance Ratio:**
  $$H_b = \frac{h_{\text{smaller}}}{h_{\text{larger}}} \ge 0.60 \quad (60\% \text{ intra-locus balance})$$
- **Degradation Index:**
  $$DI = \frac{h(\text{D8S1179}, 125\text{ bp})}{h(\text{FGA}, 320\text{ bp})} \implies DI > 5.0 \implies \text{SEVERE_DEGRADATION}$$

### 70.4 Golden Benchmark Casework Test Vectors
- `VECTOR_TERM_01` (Sample EU): 24 STRs, $P(\text{EUR}) > 98.5\%$, Centroid $52.52^\circ\text{N}, 13.40^\circ\text{E}$.
- `VECTOR_TERM_02` (Sample AA): $P(\text{AFR}) > 97.8\%$, Centroid $6.52^\circ\text{N}, 3.38^\circ\text{E}$.
- `VECTOR_TERM_03` (Sample EAS): *EDAR* `G/G`, $P(\text{EAS}) > 99.1\%$, Centroid $31.23^\circ\text{N}, 121.47^\circ\text{E}$.
- `VECTOR_TERM_04` (Sample SAS): Amelogenin single `X` + *DYS391* $= 11 \to$ Male with $AMELY$ Deletion, $P(\text{SAS}) > 96.4\%$.
- `VECTOR_TERM_05` (Sample DVI_DEGRADED): $10/24$ locus dropouts, $DI = 8.42 > 5.0$.
- `VECTOR_TERM_06` (Sample TOUCH_LTDNA): $H_b = 0.45 < 0.60$, $P(D) = 0.35$.

---

## 71. 55-SNP AIM Biogeographic Ancestry (BGA) & 41-SNP HIrisPlex-S Engine

### 71.1 7-Continental Population Bayesian Posterior Formulation
For a 55-SNP multi-locus genotype vector $\mathbf{G} = (g_1, \dots, g_{55})$ ($g_i \in \{0, 1, 2\}$) across 7 reference clusters (`AFR`, `EUR`, `EAS`, `SAS`, `AMR`, `OCE`, `MID`) with uniform prior $P_0(\text{Pop}_k) = 1/7$:

$$P(\text{Pop}_k \mid \mathbf{G}) = \frac{P_0(\text{Pop}_k) \prod_{i=1}^{55} P(g_i \mid \text{Pop}_k)}{\sum_{j=1}^7 P_0(\text{Pop}_j) \prod_{i=1}^{55} P(g_i \mid \text{Pop}_j)}$$

Dirichlet-Laplace smoothing prior ($\alpha = 0.001$) prevents zero-probability artifacts under HWE:

$$P(g_i = 0 \mid \text{Pop}_k) = (1 - p_{k,i}^*)^2, \quad P(g_i = 1 \mid \text{Pop}_k) = 2 p_{k,i}^* (1 - p_{k,i}^*), \quad P(g_i = 2 \mid \text{Pop}_k) = (p_{k,i}^*)^2$$

$$\left| \left( \sum_{k=1}^7 P(\text{Pop}_k \mid \mathbf{G}) \right) - 1.0 \right| \le 1.0 \times 10^{-6}$$

### 71.2 WGS84 Barycentric Geographic Centroid & $R_{95\%}$ Dispersion Ellipse
Continental geographic reference anchor points $\mathbf{C}_k = (\theta_k, \lambda_k)$:
- `AFR` ($0.00^\circ\text{N}, 25.00^\circ\text{E}$), `EUR` ($48.50^\circ\text{N}, 15.00^\circ\text{E}$), `EAS` ($35.00^\circ\text{N}, 105.00^\circ\text{E}$)
- `SAS` ($22.00^\circ\text{N}, 78.00^\circ\text{E}$), `AMR` ($-10.00^\circ\text{S}, -60.00^\circ\text{W}$), `OCE` ($-20.00^\circ\text{S}, 140.00^\circ\text{E}$), `MID` ($28.00^\circ\text{N}, 38.00^\circ\text{E}$)

Barycentric geographic coordinates:

$$\hat{\theta}_{\text{lat}} = \sum_{k=1}^7 P(\text{Pop}_k \mid \mathbf{G}) \cdot \theta_k, \qquad \hat{\lambda}_{\text{lon}} = \sum_{k=1}^7 P(\text{Pop}_k \mid \mathbf{G}) \cdot \lambda_k$$

Spatial covariance matrix and 95% confidence dispersion radius ($\chi^2_{2, 0.95} = 5.991$):

$$\boldsymbol{\Sigma}_{\text{geo}} = \sum_{k=1}^7 P_k \begin{bmatrix} (\theta_k - \hat{\theta})^2 & (\theta_k - \hat{\theta})(\lambda_k - \hat{\lambda}) \\ (\theta_k - \hat{\theta})(\lambda_k - \hat{\lambda}) & (\lambda_k - \hat{\lambda})^2 \end{bmatrix}$$

$$\lambda_{\max} = \frac{\sigma_{\theta}^2 + \sigma_{\lambda}^2}{2} + \sqrt{\left( \frac{\sigma_{\theta}^2 - \sigma_{\lambda}^2}{2} \right)^2 + \sigma_{\theta \lambda}^2}, \qquad R_{95\%} = \sqrt{5.991 \cdot \lambda_{\max}(\boldsymbol{\Sigma}_{\text{geo}})} \times 111.0\text{ km}$$

### 71.3 HIrisPlex-S Softmax Multinomial Logistic Regression (MLR)
For phenotype category $k \in \{1, \dots, K-1\}$ relative to reference category $K$:

$$P(Y = k \mid \mathbf{X}) = \frac{\exp \left( \beta_{k0} + \sum_{j=1}^p \beta_{kj} X_j \right)}{1 + \sum_{l=1}^{K-1} \exp \left( \beta_{l0} + \sum_{j=1}^p \beta_{lj} X_j \right)}, \qquad P(Y = K \mid \mathbf{X}) = \frac{1}{1 + \sum_{l=1}^{K-1} \exp \left( \beta_{l0} + \sum_{j=1}^p \beta_{lj} X_j \right)}$$

- **Eye Color (3-Class, Ref $K=3$ Brown):** Blue ($\beta_0 = -1.3412$), Intermediate ($\beta_0 = -1.7821$) governed by *HERC2* `rs12913832` ($\beta = +3.4105$).
- **Hair Color (4-Class, Ref $K=4$ Brown):** Blond ($\beta_0 = -0.8521$), Red ($\beta_0 = -3.1204$), Black ($\beta_0 = -1.1142$) with epistatic *MC1R* loss-of-function variants (`rs1805007`, `rs1805008`, `rs1805009`, `rs1805006`).
- **Skin Phototype (5-Class, Ref $K=5$ Intermediate):** Type I Very Pale ($\beta_0 = -2.1024$), Type II Pale ($\beta_0 = -0.9124$), Type V Dark ($\beta_0 = -1.8412$), Type VI Dark-to-Black ($\beta_0 = -3.5120$) governed by *SLC24A5* `rs1426654` ($\beta_{1} = +2.9102, \beta_{4} = -6.1204$) and *SLC45A2* `rs16891982` ($\beta_{1} = +2.4102, \beta_{4} = -5.4120$).

---

## 72. Capillary Electropherogram (EPG) Synthesis & Spectral Quality Engine

### 72.1 5/6-Dye Spectral Channel Allocation & Fluorophore Allocation
Fluorescence emission channels decompose 24-locus multiplex signals:
1. **Blue Channel (6-FAM, $\lambda_{\text{em}} = 522\text{ nm}$):** `D3S1358`, `D21S11`, `D10S1248`, `D1S1656`
2. **Green Channel (VIC / JOE, $\lambda_{\text{em}} = 553\text{ nm}$):** `vWA`, `D16S539`, `D2S441`, `D2S1338`
3. **Yellow Channel (NED / TAMRA, $\lambda_{\text{em}} = 575\text{ nm}$):** `D8S1179`, `D18S51`, `TH01`, `DYS391`
4. **Red Channel (TAZ / PET, $\lambda_{\text{em}} = 635\text{ nm}$):** `FGA`, `D5S818`, `D13S317`, `D7S820`, `SE33`
5. **Purple Channel (SID / LIZ, $\lambda_{\text{em}} = 655\text{ nm}$):** `CSF1PO`, `TPOX`, `D12S391`, `D19S433`, `D22S1045`, `Penta D`, `Penta E`, `Amelogenin`
6. **Orange Channel (LIZ 600 ILS, $\lambda_{\text{em}} = 680\text{ nm}$):** 30 Internal Lane Standard calibration fragments ($60\text{ bp} - 600\text{ bp}$)

### 72.2 Peak Height Synthesis & DNA Degradation Kinetics ($DI$)
Expected RFU peak height $\mu_{l,a}$ as a function of locus amplification efficiency $A_l$, degradation coefficient $d$, amplicon size $S_{l,a}$, and reference anchor $S_0 = 100\text{ bp}$:

$$\mu_{l,a} = A_l \cdot 10^{-d \cdot (S_{l,a} - S_0)}$$

Degradation Index ($DI$):

$$DI = \frac{h(\text{D8S1179}, 125\text{ bp})}{h(\text{FGA}, 320\text{ bp})}$$

- $DI \le 1.5$: Pristine DNA
- $1.5 < DI \le 5.0$: Moderate Degradation
- $DI > 5.0$: Severe Degradation (triggers LTDNA low-template consensus protocol)

### 72.3 Modified Asymmetric Gaussian-Lorentzian Peak Function
Continuous waveform intensity at base-pair position $t$ for peak $(t_0, h)$:

$$y(t) = h \cdot \left[ \eta \exp\left( -\frac{(t - t_0)^2}{2\sigma^2 (1 + \alpha \operatorname{sgn}(t - t_0))} \right) + (1 - \eta) \frac{1}{1 + \left(\frac{t - t_0}{\sigma}\right)^2} \right]$$

where $\sigma = 0.75\text{ bp}$ (capillary resolution bandwidth), $\eta = 0.85$ (Gaussian fraction), and $\alpha = 0.05$ (tailing asymmetry factor).

### 72.4 Quality Assurance Gates & Artifact Filters
- **Analytical Threshold:** $AT = 50.0\text{ RFU}$ (Baseline noise cutoff).
- **Stochastic Threshold:** $ST = 200.0\text{ RFU}$ (Allelic dropout risk boundary).
- **Saturation Threshold:** $SAT = 8000.0\text{ RFU}$ (CCD sensor saturation / flat-top flag).
- **Heterozygote Balance Ratio:** $H_b = h_{\text{smaller}} / h_{\text{larger}} \ge 0.60$ (60% intra-locus symmetry).
- **Reverse Stutter Ratio:** $SR = h_{\text{stutter}} / h_{\text{true\_allele}} \le SR_{\max, l}$ ($N-4$ repeat artifact).
- **Pull-Up Compensation Filter:** Peaks co-migrating within $\pm 0.3\text{ bp}$ in adjacent dye channels with $h_{\text{secondary}} / h_{\text{major}} \le 0.06$ (6%) are filtered as spectral cross-talk bleedthrough.

---

## 73. Casework Reference Library & Biocomputational Data Exchange

### 73.1 Golden Benchmark Casework Vectors (`VECTOR_TERM_01` – `VECTOR_TERM_06`)
Standard validation references across continental biogeographic ancestries and biophysical degradation states:
1. **`VECTOR_TERM_01` (Sample EU — Northern European):** 24 STR loci, *HERC2* `rs12913832: A/A`, *SLC45A2* `rs16891982: C/C`, *SLC24A5* `rs1426654: A/A` $\implies P(\text{EUR}) > 98.5\%$, Blue Eyes ($0.982$), Blond Hair ($0.891$), Very Pale Skin ($0.912$), Centroid $52.52^\circ\text{N}, 13.40^\circ\text{E}$.
2. **`VECTOR_TERM_02` (Sample AA — West African):** 24 STR loci, *HERC2* `rs12913832: G/G`, *SLC45A2* `rs16891982: G/G`, *DARC* `rs2814778: C/C` $\implies P(\text{AFR}) > 97.8\%$, Dark Brown Eyes ($0.994$), Black Hair ($0.982$), Dark Skin ($0.965$), Centroid $6.52^\circ\text{N}, 3.38^\circ\text{E}$.
3. **`VECTOR_TERM_03` (Sample EAS — East Asian):** 24 STR loci, *EDAR* `rs3827760: G/G`, *OCA2* `rs1800414: C/C` $\implies P(\text{EAS}) > 99.1\%$, Thick Straight Black Hair ($0.991$), Centroid $31.23^\circ\text{N}, 121.47^\circ\text{E}$.
4. **`VECTOR_TERM_04` (Sample SAS — South Asian with Y-Null Deletion):** Amelogenin single X ($106\text{ bp}, 1850\text{ RFU}$), Y absent ($0\text{ RFU}$), *DYS391* allele 11 ($820\text{ RFU}$) $\implies$ Male with Yp11.2 Interstitial Deletion ($P(\text{SAS}) > 96.4\%$), Centroid $28.61^\circ\text{N}, 77.20^\circ\text{E}$.
5. **`VECTOR_TERM_05` (Sample DVI_DEGRADED — Severe Skeletal Degradation):** $10/24$ loci dropped out ($FGA, D21S11, D18S51, SE33, \text{Penta E}$), $DI = \frac{h(\text{D8S1179}, 125\text{ bp})}{h(\text{FGA}, 320\text{ bp})} = \frac{842}{100} = 8.42 > 5.0$.
6. **`VECTOR_TERM_06` (Sample TOUCH_LTDNA — Low-Template Touch DNA Trace):** Template $< 62.5\text{ pg}$, $P(D) = 0.35$, $H_b = \frac{450}{1000} = 0.45 < 0.60$, triggering stochastic mixture alert.

### 73.2 FBI CODIS CMF 3.2 / 4.0 XML Specification
Grammar encapsulates `<CODISImportFile>` with `<HEADER>` (SourceLab, DestinationLab, BatchID, Timestamp) and hierarchical `<SPECIMEN>` $\implies$ `<BATCH>` $\implies$ `<READING>` $\implies$ `<LOCUS>` $\implies$ `<ALLELE>` tuples.

### 73.3 ISO/IEC 17025 LIMS JSON Schema & Cryptographic Integrity
Validates typed JSON schemas containing `sampleMetadata`, `strGenotypes`, `aimGenotypes`, and `hirisplexGenotypes`. Verifies SHA-256 chain-of-custody checksum:

$$H_{\text{CoC}} = \text{SHA-256}(\text{Canonical JSON}(\mathbf{M}_{\text{sample}}, \mathbf{G}_{\text{STR}}, \mathbf{G}_{\text{SNP}}))$$

### 73.4 GeneMapper ID-X 10-Column Format Translation
Bidirectional parsing and serialization supporting standard capillary electrophoresis columns: `Sample Name`, `Marker`, `Allele 1`, `Allele 2`, `Height 1`, `Height 2`, `Size 1`, `Size 2`, `Data Point 1`, `Data Point 2`.

---

## 74. Tactical Forensic Workstation UI & 6-Tab Reactive State Topology

### 74.1 Six-Tab Workstation Layout
1. **Tab 1: Inferred Telemetry & Live GIS Mapping (`inferred`):**
   - 7 Continental Ancestry (BGA) Bayesian Posterior Breakdown ($\text{AFR}, \text{EUR}, \text{EAS}, \text{SAS}, \text{AMR}, \text{OCE}, \text{MID}$).
   - HIrisPlex-S Softmax MLR Pigmentation Predictions (Eye, Hair, Skin Phototype) with epistasis flags.
   - WGS84 Centroid $(\hat{\theta}_{\text{lat}}, \hat{\lambda}_{\text{lon}})$ and $R_{95\%}$ spatial dispersion radius in km.
   - Live interactive `GeoForensicPanel` raster map visualization.
2. **Tab 2: 24-STR Forensic Multiplex Grid (`str`):**
   - Expanded 24-locus STR profile table with Allele 1, Allele 2, Peak Heights (RFU 1, RFU 2), Heterozygote Balance ($H_b$), Homozygous/Heterozygous flags, and Dropout alerts ($[0]$).
   - Instant search, custom locus addition, live editing, and locus deletion.
3. **Tab 3: 55-SNP AIM & 41-SNP HIrisPlex Matrix (`snp`):**
   - 55 AIM + 41 HIrisPlex catalog with quick $0, 1, 2$ genotype dosage selectors and instant client-side reactive recalculation.
4. **Tab 4: Interactive EPG Spectrum Visualizer (`epg`):**
   - Continuous multi-channel SVG electropherogram waveform across 5 dye channels (6-FAM Blue, VIC Green, NED Yellow, TAZ Red, SID Purple) + LIZ 600 Orange ILS size standard.
   - Channel toggles, degradation rate slider ($d \in [0.0, 0.012]$), template DNA mass slider ($0.03\text{ ng} - 2.0\text{ ng}$), and stutter toggle.
   - Analytical ($AT=50\text{ RFU}$), Stochastic ($ST=200\text{ RFU}$), and Saturation ($SAT=8000\text{ RFU}$) threshold lines.
5. **Tab 5: 27-Locus Y-STR Haplotype & Lineage Analysis (`ystr`):**
   - Comprehensive 25 multiplex systems spanning 27 physical loci including all 7 RM loci (`DYS570`, `DYS576`, `DYS627`, `DYS518`, `DYS449`, `DYF387S1a/b`).
   - Snedecor $F$ Clopper-Pearson 95% upper bound against YHRD ($N=35,000$), Brenner subpopulation correction ($\theta = 0.02$), and discrete Laplace haplogroup classifier.
   - Stepwise Mutation Model (SMM) Kinship CPI and male mixture contributor deconvolution ($N_{\text{male}}$).
6. **Tab 6: mtDNA Control Region & EMPOP Alignment (`mtdna`):**
   - Hypervariable D-Loop architecture visualizer across 5 regions (HV1, HV2, HV3, OHR, CR) aligned to rCRS (NC_012920.1) and RSRS.
   - EMPOP 3'-right-alignment normalizer on light strand, IUPAC point heteroplasmy parser ($R, Y, M, K, S, W$), and PhyloTree Build 17 macro-haplogroup classification.

### 74.2 Bidirectional Reactive State Propagation
Updates from `DnaProfileInspectorModal` propagate through `useIngestStore` and `useForensicCaseStore` to all 35 forensic biocomputational modules across the 7 architecture layers, guaranteeing full data integrity and instant UI synchrony.

### 74.3 Human-Computer Interaction & Responsive Parity
- Mobile ($\le 640\text{px}$): Minimum $\ge 44\text{px}$ touch targets, single-column flex layouts, non-overlapping tabs, sticky table headers.
- Desktop ($\ge 1024\text{px}$): Multi-column tactical HUD grid, high-resolution SVG waveforms, split-pane GIS visualizers.

---

## 75. On-Chain Cryptographic Merkle Custody, EVM BN254 Groth16 Pairings & ISO 17025 RBAC Governance

### 75.1 Mathematical Formulation of On-Chain Binary Merkle Tree (`ForensicMerkleLedger.sol`)
For an ordered sequence of custody events $\{E_0, E_1, \dots, E_{N-1}\}$, leaf hashes are computed via:
$$H_i = \text{keccak256}(\text{abi.encodePacked}(E_i.\text{eventId}, E_i.\text{timestamp}, E_i.\text{officerId}, E_i.\text{sampleBarcode}, E_i.\text{locationId}, E_i.\text{priorHash}))$$

Pairwise parent reductions at tree level $k$ satisfy:
$$P_{j}^{(k)} = \text{keccak256}(\text{abi.encodePacked}(P_{2j}^{(k-1)}, P_{2j+1}^{(k-1)}))$$

Given an audit proof path $\mathcal{P} = \{S_0, S_1, \dots, S_{d-1}\}$ with bitmask $\mathbf{b} \in \{0, 1\}^d$, on-chain verification executes in $O(\log_2 N)$ gas complexity:
$$C_{i+1} = \begin{cases} \text{keccak256}(S_i \parallel C_i), & \text{if } \mathbf{b}_i = 1 \\ \text{keccak256}(C_i \parallel S_i), & \text{if } \mathbf{b}_i = 0 \end{cases}$$
Verification succeeds iff $C_d = \mathbf{Root}_{\text{committed}}$.

### 75.2 Bilinear Multi-Pairing Verification on BN254 (`Groth16ZkpVerifier.sol`)
To verify a blind DNA match proof $\pi = (A \in \mathbb{G}_1, B \in \mathbb{G}_2, C \in \mathbb{G}_1)$ against public inputs $\mathbf{x} = [H(\mathbf{G}_E), M_{\text{thresh}}, H(\mathbf{G}_S)]$ without exposing suspect STR genotypes, the contract evaluates the 4-pairing equation using EVM precompiles (`0x06` ecAdd, `0x07` ecMul, `0x08` ecPairing):
$$e(-A, B) \cdot e(\alpha, \beta) \cdot e\left( \mathbf{IC}_0 + \sum_{i=1}^l x_i \mathbf{IC}_i, \gamma \right) \cdot e(C, \delta) = 1_{\mathbb{G}_T}$$
where field arithmetic operates over base field $\mathbb{F}_q$ ($q = 21888242871839275222246405745257275088696311157297823662689037894645226208583$) and scalar field $\mathbb{F}_r$ ($r = 21888242871839275222246405745257275088548364400416034343698204186575808495617$).

### 75.3 ISO/IEC 17025 RBAC Governance & Rate-Limiting (`ForenzaAuditRegistry.sol`)
Role-Based Access Control assigns atomic permissions:
- `DEFAULT_ADMIN_ROLE`: Contract upgrades, key rotations, investigator status management, emergency global lockdown.
- `LAB_ANALYST_ROLE`: DNA profile query logging, casework state transitions.
- `LEGAL_AUDITOR_ROLE`: Chain of custody inspection, verification proof retrieval.
- `COURT_OFFICER_ROLE`: Certified evidence admissibility verification.

Sliding-window rate-limiting enforces a maximum of 5 queries per 60-second window, automatically suspending abusive accounts (`InvestigatorStatus.SUSPENDED`) and preventing denial-of-service on the forensic ledger.

---

## 76. Y-STR 27-Locus Lineage Haplotype Biocomputation (`ystr_27_locus_engine.py` & `ystr27LocusEngine.ts`)

### 76.1 27-Locus Master Registry & Nested Repeat Decoupling
The Y-STR engine operates across 25 multiplex systems covering 27 physical loci. For the nested complex system `DYS389I` and `DYS389II`, the decoupled second repeat unit is derived via:
$$[\text{DYS389.2}] = \text{DYS389II} - \text{DYS389I}$$

### 76.2 Exact Clopper-Pearson 95% Upper Bound
For $k$ observed matches in a database of size $N$ (YHRD standard $N = 35,000$):
- For $k = 0$:
  $$p_{\text{upper}} = 1 - \alpha^{1/(N+1)} \quad (\alpha = 0.05 \implies p_{\text{upper}} \approx 8.56 \times 10^{-5})$$
- For $k > 0$, using the quantile of Snedecor's $F$-distribution with degrees of freedom $d_1 = 2(k+1), d_2 = 2(N-k)$:
  $$p_{\text{upper}} = \frac{(k+1) F_{1-\alpha/2, 2(k+1), 2(N-k)}}{(N-k) + (k+1) F_{1-\alpha/2, 2(k+1), 2(N-k)}}$$

### 76.3 Brenner Subpopulation Coancestry Correction
To account for patrilineal population substructure with coancestry coefficient $\theta = 0.02$:
$$p_{\text{Brenner}} = \frac{k + \theta}{N + \theta}, \quad p_{\text{subpop}} = \frac{p_{\text{upper}} + \theta}{1 + \theta}$$

### 76.4 Stepwise Mutation Model (SMM) Kinship Index
For an alleged paternal relationship spanning $m$ meioses between donor $A$ and donor $B$:
$$P(\text{Transmission} \mid m) = \prod_{l=1}^{27} P(A_l \to B_l \mid m)$$
where for repeat difference $\Delta = |A_l - B_l|$:
$$P(A_l \to B_l \mid m) = \begin{cases} (1 - \mu_l)^m & \text{if } \Delta = 0 \\ m \cdot \frac{\mu_l}{2} (1 - r_l) r_l^{\Delta - 1} & \text{if } \Delta \ge 1 \end{cases}$$
The combined paternal kinship index evaluates to:
$$\text{CPI}_{Y} = \frac{P(\text{Transmission} \mid m)}{P_{\text{unrelated}}(B)}$$

### 76.5 Male Mixture Contributor Deconvolution ($N_{\text{male}}$)
The minimum number of male contributors in a mixture is bounded by:
$$N_{\text{male}} \ge \max\left( \max_{l \in \text{Single}} n_l, \; \max_{m \in \text{Multi}} \lceil n_m / 2 \rceil \right)$$
where $\text{Multi} = \{\text{DYS385a/b}, \text{DYF387S1a/b}\}$.

---

## 77. mtDNA Control Region D-Loop Biocomputation & EMPOP Normalization (`mtdna_empop_engine.py` & `mtdnaEmpopEngine.ts`)

### 77.1 EMPOP 3'-Right-Alignment & Light-Strand Standard
Mitochondrial variants are normalized against rCRS (NC_012920.1) across the Control Region (16024–576):
- Poly-C insertions in HV1 (16024–16365) are right-aligned to position 16193 (`16193.1C`).
- Poly-C insertions in HV2 (73–340) are right-aligned to position 315 (`315.1C`).
- Dinucleotide AC repeat insertions/deletions in HV3 (438–574) are right-aligned to position 524 (`524.1A`, `524.2C`, `524del`).

### 77.2 Point & Length Heteroplasmy Formalism
Mixed base positions are parsed using standard IUPAC ambiguity codes:
$$G(p) \in \{R, Y, M, K, S, W\}$$
where minor allele fractions satisfy $f_{\text{minor}} \ge 0.10$ for analytical calling.

### 77.3 PhyloTree Build 17 Macro-Haplogroup Softmax Scoring
Given normalized mutation set $\mathcal{M} = \{m_1, \dots, m_K\}$, each haplogroup $H_j$ with motif set $\mathcal{H}_j$ and negative motifs $\mathcal{N}_j$ receives score:
$$S(H_j) = |\mathcal{M} \cap \mathcal{H}_j| - 2 \cdot |\mathcal{M} \cap \mathcal{N}_j|$$
Posterior probabilities over 20 canonical maternal macro-lineages are computed via Softmax:
$$P(H_j \mid \mathcal{M}) = \frac{\exp(S(H_j))}{\sum_k \exp(S(H_k))}$$
Exact Clopper-Pearson 95% upper bounds and LR metrics are calculated against the EMPOP global database ($N = 48,200$).

---

## 78. Forensic CLI Batch Ingestion Protocol & Multi-Omic EBNF Grammar Engine (`cli_batch_parser.py` & `forensicCliBatchParser.ts`)

### 78.1 Formal EBNF Command Grammar
```ebnf
ForenzaCLICommand  ::= SingleLocusCmd | BatchIngestCmd ;

SingleLocusCmd     ::= DomainPrefix WS Action WS LocusIdentifier WS AllelePayload [ WS RFUPayload ] ;
BatchIngestCmd     ::= DomainPrefix WS BatchAction WS DataFlag WS StringLiteral [ WS OptionFlags ]* ;

DomainPrefix       ::= "str" | "ystr" | "mtdna" | "snp" | "cpg" ;
Action             ::= "set" | "add" | "del" ;
BatchAction        ::= "set-batch" | "import-batch" ;

DataFlag           ::= "--data" | "-d" ;
OptionFlags        ::= RFUFlag | SepFlag | RecalcFlag | TissueFlag | ModeFlag | RefFlag ;
```

### 78.2 Multi-Omic Parsing Rules
1. **Autosomal STR (24 Loci):** Validates integer repeats and decimal microvariants ($\le .3$), tri-alleles, homozygote expansion on single call (`--recalc`), and RFU peak height pairing.
2. **Y-STR (Yfiler Plus 27 Loci):** Distinguishes single-copy vs multi-copy duplicated systems (`DYS385a/b`, `DYF387S1a/b`) and tags Rapidly Mutating (RM) loci.
3. **mtDNA Control Region:** Normalizes D-Loop mutations against rCRS/RSRS, supporting EMPOP insertions (`315.1C`), deletions (`524del`), and IUPAC point heteroplasmies (`16093Y`, `16189R`).
4. **Ancestry & Phenotype SNPs:** Ingests 55-SNP AIM and 41-SNP HIrisPlex-S profiles with automatic translation between integer dosages $\{0, 1, 2\}$ and explicit nucleotide genotypes (`G/G`, `C/T`).
5. **Epigenetics (VISAGE 5-CpG):** Validates $\beta \in [0.0, 1.0]$, computes logit $M$-values $M = \log_2(\beta / (1 - \beta))$, and applies tissue calibration matrices for chronological age estimation.

### 78.3 Cryptographic ISO/IEC 17025 Audit Trail
Every CLI transaction computes dual SHA-256 digests:
$$\text{raw\_command\_hash} = \text{SHA-256}(\text{Raw CLI String})$$
$$\text{canonical\_state\_hash} = \text{SHA-256}(\text{Canonical JSON State})$$
Generating an immutable transaction identifier: `tx_{domain}_{hash[:8]}_{YYYYMMDD}`.

---

## 79. Certified Multi-Omic Reference Standards & Empirical Ground Truth Sets

### 79.1 Five Globally Certified Human Reference Standards
To eliminate synthetic casework presets and comply strictly with ISO/IEC 17025:2017 (§7.7.2 Inter-laboratory Comparisons & Proficiency Testing), FORENZA integrates 5 internationally certified reference human standard materials:

1. **NIST SRM 2391d Component A (`PRESET_NIST_SRM_2391D`):**
   - *Designation:* NIST Standard Reference Material 2391d Component A (Male gDNA).
   - *Certification Authority:* National Institute of Standards and Technology (NIST).
   - *Genomic Truth:* 24-locus Autosomal STR multiplex, 27-locus Y-FILER Plus ($R1b1a1b$ modal haplogroup), mtDNA H1e D-Loop ($263\text{G}, 315.1\text{C}, 16069\text{T}, 16129\text{G}, 16223\text{T}, 16311\text{C}$), VISAGE 5-CpG DNA methylation predicted age $44.2 \pm 3.4\text{ years}$.

2. **NA12878 / HG001 (`PRESET_NA12878_CEU`):**
   - *Designation:* CEPH/Utah Pedigree 1463 Female (GIAB Pilot Genome).
   - *Repository:* Coriell Institute / Genome in a Bottle (GIAB) Consortium.
   - *Genomic Truth:* Micro-variants $\text{D1S1656} (14, 17.3)$, $\text{D2S441} (10, 11.3)$, $\text{SE33} (19, 25.2)$, mtDNA H1a1, VISAGE predicted age $38.5 \pm 3.4\text{ years}$, $99.2\%$ European (EUR) AIM ancestry.

3. **HG002 / NA24385 (`PRESET_HG002_AJ`):**
   - *Designation:* GIAB Ashkenazi Jewish Trio Son.
   - *Repository:* GIAB / NIST Reference Material 8392.
   - *Genomic Truth:* Micro-variants $\text{D12S391} (17, 18.3)$, $\text{D19S433} (13, 15.2)$, Y-STR Haplogroup $J2a1a1$, mtDNA K1a9 founder motif, VISAGE predicted age $22.1 \pm 3.4\text{ years}$.

4. **NA19240 (`PRESET_NA19240_YRI`):**
   - *Designation:* 1000 Genomes Project Yoruba in Ibadan, Nigeria Female.
   - *Repository:* Coriell Cell Repositories (1000 Genomes).
   - *Genomic Truth:* mtDNA macro-haplogroup $L2a1$ ($18$ diagnostic mutations including $524.1\text{A}, 524.2\text{C}$), DARC Duffy Null Fixation ($\text{rs2814778} = 2$), $99.6\%$ Sub-Saharan African (AFR) AIM ancestry, VISAGE predicted age $31.4 \pm 3.4\text{ years}$.

5. **NA18507 / HG005 (`PRESET_NA18507_CHB`):**
   - *Designation:* GIAB / 1000 Genomes Han Chinese in Beijing Male.
   - *Repository:* Coriell Cell Repositories / GIAB.
   - *Genomic Truth:* Y-STR Haplogroup $O2a2b1$, mtDNA $D4a1$, EDAR V370A thick straight hair allele ($\text{rs3827760} = 2$), VISAGE predicted age $41.0 \pm 3.4\text{ years}$, $99.4\%$ East Asian (EAS) AIM ancestry.

### 79.2 Mathematical Verification Invariants for Multi-Omic Concordance

#### 1. Autosomal STR Multilocus Concordance Rate
$$C_{\text{STR}} = \frac{1}{L} \sum_{l=1}^L \mathbb{I}\left(A_{l,1}^{\text{test}} = A_{l,1}^{\text{truth}} \land A_{l,2}^{\text{test}} = A_{l,2}^{\text{truth}}\right)$$
*Requirement:* $C_{\text{STR}} = 1.000000$ ($100.0\%$ exact allele match across all 24 loci).

#### 2. Y-STR Lineage Concordance Rate
$$C_{\text{YSTR}} = \frac{1}{K} \sum_{k=1}^K \mathbb{I}\left(Y_k^{\text{test}} = Y_k^{\text{truth}}\right)$$
*Requirement:* $C_{\text{YSTR}} = 1.000000$ across all 27 Y-FILER Plus loci for male standards.

#### 3. VISAGE Epigenetic Clock Residual Tolerance
$$|\text{Age}_{\text{pred}} - \text{Age}_{\text{target}}| \le 2.0\text{ years} \quad \land \quad \text{Age}_{\text{pred}} \in \left[\text{CI}_{95,\text{lower}}, \text{CI}_{95,\text{upper}}\right]$$

### 79.3 Forensic Data Portability & Export Schemas
All certified standards and analyzed case profiles support loss-less deterministic export into 3 standardized formats:
1. **FBI CODIS CMF XML v3.2 / v4.0:** Schema-compliant Common Message Format with `<SOURCELAB>`, `<DESTINATIONLAB>`, `<SPECIMENID>`, `<BATCH>`, `<READING>`, and `<LOCUS>` elements.
2. **ISO/IEC 17025 LIMS JSON:** JSON schema containing `$schema`, `sampleMetadata`, `strGenotypes`, `aimGenotypes`, and `hirisplexGenotypes`.
3. **GeneMapper ID-X CE Table CSV:** 10-column table format (`Sample Name, Marker, Allele 1, Allele 2, Height 1, Height 2, Size 1, Size 2, Data Point 1, Data Point 2`).

---

## 80. X-STR 12-Locus Linkage & Complex Female Kinship Engine (Argus X-12)

### 80.1 Investigator Argus X-12 Linkage Clusters (LG1–LG4)
The human X chromosome features unique sex-linked inheritance: hemizygous males ($46,XY$) transmit their single maternal X chromosome intact to all biological daughters without meiotic recombination. Heterozygous females ($46,XX$) undergo meiotic recombination between linked X-STR loci.

The Investigator Argus X-12 panel partitions 12 highly polymorphic X-STR markers into 4 independent Linkage Groups:
- **Linkage Group 1 (LG1, Xp22.2):** `DXS10148` (12.42 Mb, 18.5 cM), `DXS10135` (13.15 Mb, 19.8 cM), `DXS8378` (14.90 Mb, 22.1 cM); intra-cluster recombination $r_{1-2} = 0.003, r_{2-3} = 0.022$.
- **Linkage Group 2 (LG2, Xq12):** `DXS7132` (68.10 Mb, 72.3 cM), `DXS10074` (70.80 Mb, 74.8 cM), `DXS10079` (71.35 Mb, 75.3 cM); intra-cluster recombination $r_{1-2} = 0.015, r_{2-3} = 0.020$.
- **Linkage Group 3 (LG3, Xq26):** `DXS10103` (133.50 Mb, 138.2 cM), `HPRTB` (133.90 Mb, 138.6 cM), `DXS10101` (134.60 Mb, 140.1 cM); intra-cluster recombination $r_{1-2} = 0.001, r_{2-3} = 0.012$.
- **Linkage Group 4 (LG4, Xq28):** `DXS10146` (148.20 Mb, 155.4 cM), `DXS10134` (149.10 Mb, 156.3 cM), `DXS7423` (150.05 Mb, 157.2 cM); intra-cluster recombination $r_{1-2} = 0.005, r_{2-3} = 0.008$.

---

### 80.2 Kosambi Mapping Function & Interference Modeling
Genetic distance $d$ (cM) and observed meiotic recombination fraction $r$ are related via the Kosambi mapping function incorporating positive chiasma interference:

$$r = \frac{1}{2} \tanh\left(\frac{2d}{100}\right) = \frac{1}{2} \left( \frac{e^{4d/100} - 1}{e^{4d/100} + 1} \right)$$

The inverse Kosambi transformation calculates genetic map distance from recombination frequency:

$$d = 25 \ln\left( \frac{1 + 2r}{1 - 2r} \right) \quad (\text{cM})$$

---

### 80.3 Complex Female Kinship Index Formulations ($KI_X$)

#### 1. Father - Daughter Duo Kinship
Biological fathers possess a single hemizygous allele $A_f$ transmitted deterministically:

$$KI_{X, \text{Duo}, l} = \begin{cases} \frac{1.0}{p(A_f)} & \text{if } A_f \in G_{\text{daughter}} \\ \frac{\mu}{2 p(A_{\text{daughter}})} & \text{if germline mutation occurs} \end{cases}$$

#### 2. Paternal Half-Sisters (PHS)
Paternal half-sisters inherit identical paternal X chromosomes. Incorporating intra-cluster recombination fraction $r$:

$$KI_{X, \text{PHS}, l} = \frac{(1 - r) \cdot h(A_1, A_2) + r \cdot h(A_1) h(A_2)}{h(A_1) h(A_2)} \approx \frac{1 - r}{p(A_{\text{shared}})} + r$$

#### 3. Paternal Grandmother - Granddaughter (PGM-GD) Deficiency Kinship
In deficiency cases involving a deceased intermediate male:

$$KI_{X, \text{PGM-GD}, l} = \frac{0.5}{p(A_{\text{shared}})} + 0.5$$

#### 4. Mother - Son Kinship
$$KI_{X, \text{MS}, l} = \begin{cases} \frac{0.5}{p(A_{\text{son}})} & \text{if mother is heterozygous } (A_1 A_2) \\ \frac{1.0}{p(A_{\text{son}})} & \text{if mother is homozygous } (A_1 A_1) \end{cases}$$

---

### 80.4 Multi-Cluster Independence Product Rule & Invariants
Because the 4 linkage groups are separated by $> 50\text{ cM}$ ($r \to 0.50$, linkage equilibrium between clusters), the combined Kinship Index is the product across all 4 independent groups:

$$KI_{X, \text{Total}} = \prod_{g=1}^4 KI_{X, \text{LG}_g} = \prod_{g=1}^4 \left( \prod_{l \in \text{LG}_g} KI_{X, l} \right)$$

$$\log_{10} KI_{X, \text{Total}} = \sum_{g=1}^4 \log_{10} KI_{X, \text{LG}_g}$$

Strict Mathematical Invariant:
$$\left| \log_{10} KI_{X, \text{Total}} - \sum_{g=1}^4 \log_{10} KI_{X, \text{LG}_g} \right| < 10^{-6}$$

---

## 81. Mitochondrial DNA (mtDNA) EMPOP rCRS/RSRS Alignment & Lineage Engine (Module 2.3)

Mitochondrial DNA (mtDNA) analysis provides essential maternal lineage forensics for degraded biological specimens (hair shafts, bones, teeth, and historical human remains) due to its high copy number ($10^2$–$10^4$ per cell), maternal transmission, and lack of meiotic recombination.

### 81.1 Control Region (D-Loop) Reference Architecture & Domains
All sequence variants are aligned and reported relative to the Revised Cambridge Reference Sequence (**rCRS, GenBank NC_012920.1**, 16,569 bp) or Reconstructed Sapiens Reference Sequence (**RSRS**):

| Structural Domain | Coordinate Boundaries (rCRS) | Biological Role & Diagnostic Forensic Value |
| :--- | :--- | :--- |
| **HV1 (Hypervariable 1)** | 16024–16365 | High mutational rate; diagnostic for major global macro-haplogroups. |
| **HV2 (Hypervariable 2)** | 73–340 | Contains primary homopolymeric C-tracts (303–315) and insertion hotspots. |
| **HV3 (Hypervariable 3)** | 438–574 | Contains variable dinucleotide AC repeat elements (522–524). |
| **OHR** | 110–441 | Heavy-strand replication origin spanning Conserved Sequence Blocks. |
| **CSB I / II / III** | 214–232 / 299–315 / 346–363 | Transcription termination and replication initiation regulatory sites. |

---

### 81.2 ISFG (2014, 2020) & EMPOP 3'-Right Alignment Normalization
To prevent artificial sequence discrepancies caused by 5'-shifted alignments, the FORENZA engine enforces 3'-most right-alignment on the light strand ($5' \to 3'$):
- **HV2 Poly-C Tract (303–315):** Insertions in the 303–308 tract shift to `309.1C, 309.2C`. Insertions in the 311–314 tract shift to `315.1C`.
- **HV1 Poly-C Tract (16184–16193):** Insertions in the 16184–16188 tract shift to `16189.1C, 16189.2C`.
- **HV3 Dinucleotide Repeat (522–524):** Insertions at 522/523 shift to `524.1AC` (or `524.1A, 524.2C`).

---

### 81.3 Point Heteroplasmy (PHP) & SWGDAM Maternal Kinship Decision Rules
Point heteroplasmies are modeled using IUPAC multi-base ambiguity codes ($R=\text{A/G}, Y=\text{C/T}, M=\text{A/C}, K=\text{G/T}, S=\text{G/C}, W=\text{A/T}$).
- **Heteroplasmy Concordance:** A shared point heteroplasmy (`16189Y` vs `16189Y`) or a heteroplasmy-to-homoplasmy pair (`16189Y` vs `16189C`) is consistent with shared maternal ancestry and cannot be excluded.
- **SWGDAM Exclusion Rule:** $\ge 2$ homoplasmic point differences between questioned and reference profiles triggers a definitive exclusion ($LR_{\text{mtDNA}} = 0.0, \log_{10} LR = -300.0$).
- **Inconclusive Boundary:** 1 homoplasmic point difference is interpreted as inconclusive due to potential germline single-base transition events.

---

### 81.4 Exact Clopper-Pearson 95% Frequency Upper Bounds & Maternal LR
For unobserved mitogenome haplotypes ($k=0$) in a database of size $N$ (e.g. EMPOP Release 15 $N=48,500$):
$$\hat{p}_{\text{upper}} = 1 - (0.05)^{\frac{1}{N+1}}$$

For observed haplotypes where $k > 0$:
$$\hat{p}_{\text{upper}} = \frac{k + \frac{1}{2} z^2 + z \sqrt{\frac{k(N-k)}{N} + \frac{1}{4} z^2}}{N + z^2} \quad (z = 1.95996)$$

The Maternal Likelihood Ratio ($LR_{\text{mtDNA}}$) comparing $H_1$ (Shared maternal lineage) vs $H_2$ (Unrelated donor) is:
$$LR_{\text{mtDNA}} = \frac{1}{\hat{p}_{\text{upper}}}$$

For $N = 48,500$ and $k=0$:
$$\hat{p}_{\text{upper}} = 1 - (0.05)^{1/48501} \approx 6.1764 \times 10^{-5} \implies LR_{\text{mtDNA}} \approx 16,190.7$$

---

## 82. Interpol Disaster Victim Identification (DVI) & Complex Pedigree Reconciler (Module 2.4)

### 82.1 Direct Ante-Mortem Reference Standard Likelihood Ratio
When a Post-Mortem (PM) human remain is directly compared against an Ante-Mortem (AM) personal reference standard (e.g. toothbrush, comb, biopsy):
- **Genotypic Concordance:**
  $$LR_{\text{direct}, l} = \begin{cases} \frac{1}{2 p_i p_j + 2 \theta p_i (1 - p_i)} & \text{if heterozygous } (A_i A_j) \\ \frac{1}{p_i^2 + \theta p_i (1 - p_i)} & \text{if homozygous } (A_i A_i) \end{cases}$$
- **Mendelian Non-Concordance:** If $G_{\text{PM}} \neq G_{\text{AM}}$, $LR_l = 0.0$ ($\log_{10} LR_l = -300.0$).

---

### 82.2 Complex Kinship Pedigree Likelihood Calculations
1. **Trio Paternity (Missing Child vs Mother & Father):**
   $$LR_{\text{trio}, l} = \frac{P(G_C \mid G_M, G_F, H_1)}{P(G_C \mid G_M, H_2)}$$
   Under $H_1$ (True Biological Parents), alleles transmit with Mendelian probability $0.5$. Under $H_2$ (Random Male), paternal allele frequency $p_{\text{pat}}$ governs transmission.
2. **Deficiency Duo (Single Parent & Child):**
   $$LR_{\text{duo}, l} = \frac{P(G_C \mid G_P, H_1)}{P(G_C \mid H_2)}$$
3. **Full Siblings Kinship Hypothesis:**
   $$LR_{\text{sib}, l} = \frac{k_0 + k_1 \cdot \text{IBS}_1 + k_2 \cdot \text{IBS}_2}{P(G_{S2})}$$
   where $(k_0, k_1, k_2) = (0.25, 0.50, 0.25)$ for full siblings.

---

### 82.3 Multi-Omic Evidence Fusion & Product Rule
Combining autosomal, lineage, and SNP markers under independent transmission:
$$LR_{\text{Joint}} = LR_{\text{Autosomal STR}} \times \left(\frac{1}{\hat{p}_{\text{Y-STR, upper}}}\right)^{\delta_y} \times \left(\frac{1}{\hat{p}_{\text{mtDNA, upper}}}\right)^{\delta_m} \times (LR_{\text{SNP}})^{\delta_s}$$

Log-space additivity invariant:
$$\log_{10} LR_{\text{Joint}} = \log_{10} LR_{\text{Autosomal}} + \delta_y \log_{10}\left(\frac{1}{\hat{p}_Y}\right) + \delta_m \log_{10}\left(\frac{1}{\hat{p}_M}\right) + \delta_s \log_{10}(LR_{\text{SNP}})$$

---

### 82.4 Bayesian Posterior Probability ($W$) & Prior Odds Updating
Given a prior probability of identity $P(H_1)$ (default $0.001$ in mass disaster scenarios):
$$\text{Prior Odds} = \frac{P(H_1)}{1 - P(H_1)}$$
$$\text{Posterior Odds} = LR_{\text{Joint}} \times \text{Prior Odds}$$
$$W = P(H_1 \mid E) = \frac{\text{Posterior Odds}}{1 + \text{Posterior Odds}} = \frac{LR_{\text{Joint}} \cdot P(H_1)}{LR_{\text{Joint}} \cdot P(H_1) + (1 - P(H_1))}$$

---

### 82.5 Interpol Standing Committee 4-Tier Decision Protocol
| Decision Tier | Likelihood Ratio ($LR_{\text{Joint}}$) | $\log_{10} LR$ | Judicial Action Criterion | Secondary Corroboration |
| :--- | :--- | :--- | :--- | :--- |
| **DEFINITIVE_IDENTIFICATION** | $LR \ge 10^6$ | $\ge 6.00$ | Standalone judicial identification | Not legally required |
| **PROBABLE_MATCH** | $10^4 \le LR < 10^6$ | $4.00 \le \log_{10} < 6.00$ | Probable match | Mandates odontology/surgical marks |
| **INCONCLUSIVE** | $10^{-2} < LR < 10^4$ | $-2.00 < \log_{10} < 4.00$ | Insufficient biostatistical proof | Additional STR / SNP testing |
| **EXCLUSION** | $LR \le 10^{-2}$ | $\le -2.00$ | Definite exclusion | Excluded from reference pedigree |

---

### 82.6 Bipartite Hungarian / Munkres Mutual Exclusivity Solver
In an $N \times M$ mass disaster reconciliation matrix ($N$ PM remains vs $M$ AM missing person families), the assignment optimization solves:
$$\max \sum_{i=1}^N \sum_{j=1}^M x_{i,j} \cdot \log_{10}(LR_{i,j})$$
subject to:
$$\sum_{j=1}^M x_{i,j} \le 1 \quad \forall i \in \{1, \dots, N\}, \quad \sum_{i=1}^N x_{i,j} \le 1 \quad \forall j \in \{1, \dots, M\}, \quad x_{i,j} \in \{0, 1\}$$
guaranteeing strict 1-to-1 mutual exclusivity across all reconciled victims.

---

## 83. Ancient & Degraded Forensic DNA Damage Kinetics Engine (Module 2.5)

### 83.1 Briggs Post-Mortem Deamination Kinetics & Exponential Gradient
Post-mortem hydrolytic deamination of cytosine into uracil (observed as thymine after PCR amplification) is concentrated at single-stranded overhang termini:
$$\delta_k(i) = \delta_0 \cdot \exp\left(-\alpha \cdot (i - 1)\right) + \delta_{\text{baseline}}, \quad \text{for nucleotide distance } i \in [1, 25]$$
where $\delta_0$ is the terminal $5'$ deamination probability ($\ge 0.35$ in ancient remains), $\alpha$ is the exponential decay rate per nucleotide ($\sim 0.10 - 0.18/\text{bp}$), and $\delta_{\text{baseline}}$ is the interior sequencing noise floor ($0.005$).

---

### 83.2 Complementary Strand Damage Symmetry
Due to 5'-to-3' complementary strand symmetry in double-stranded DNA libraries, cytosine deamination on the opposite strand produces an identical $3' \text{ G}\to\text{A}$ gradient:
$$\delta_{G\to A}(j) = \delta_0 \cdot \exp\left(-\alpha \cdot (j - 1)\right) + \delta_{\text{baseline}}$$
with empirical divergence $|\delta_{C\to T}(k) - \delta_{G\to A}(k)| < 0.015$.

---

### 83.3 Exponential Fragment Length Distribution & Degradation Classification
Post-mortem phosphodiester backbone cleavage follows an exponential length distribution:
$$P(L) = \lambda_L \cdot \exp\left(-\lambda_L \cdot (L - L_{\min})\right), \quad L \ge L_{\min}$$
$$\bar{L} = \frac{1}{\lambda_L} + L_{\min}, \quad \text{Median} = \frac{\ln 2}{\lambda_L} + L_{\min}, \quad \text{CDF}(100) = 1 - \exp\left(-\lambda_L \cdot (100 - L_{\min})\right)$$

| Degradation Tier | Mean Fragment Length ($\bar{L}$) | Dropout Fraction ($< 100\text{ bp}$) | Recommended Forensic Typing Modality |
| :--- | :--- | :--- | :--- |
| **SEVERE** | $\bar{L} < 60.0\text{ bp}$ | $> 90\%$ | Micro-SNP capture panel ($40\text{--}70\text{ bp}$) |
| **MODERATE** | $60.0 \le \bar{L} < 90.0\text{ bp}$ | $60\% - 90\%$ | Mini-STRs or targeted NGS amplicons |
| **LOW** | $90.0 \le \bar{L} < 150.0\text{ bp}$ | $30\% - 60\%$ | Standard STR multiplexing |
| **PRISTINE** | $\bar{L} \ge 150.0\text{ bp}$ | $< 30\%$ | High-molecular weight WGS / Expanded CODIS |

---

### 83.4 Damage-Compensated Low-Coverage SNP Genotype Likelihoods
For sequencing read base $b_r$ observed at distance $k_r$ from fragment terminus on reference $C$ and alternative $T$:
$$P(b_r = C \mid CC) = (1 - \delta_{k_r})(1 - e_r), \quad P(b_r = T \mid CC) = \delta_{k_r}(1 - e_r) + (1 - \delta_{k_r})\frac{e_r}{3}$$
$$P(b_r = T \mid TT) = 1 - e_r, \quad P(b_r = C \mid TT) = \frac{e_r}{3}$$
$$P(b_r \mid CT) = 0.50 \cdot P(b_r \mid CC) + 0.50 \cdot P(b_r \mid TT)$$

Bayesian posterior genotype probabilities:
$$P(G \mid D) = \frac{\left( \prod_{r=1}^R P(b_r \mid G, k_r) \right) P(G)}{\sum_{G' \in \{CC, CT, TT\}} \left( \prod_{r=1}^R P(b_r \mid G', k_r) \right) P(G')}$$

---

### 83.5 Modern Contaminant Subtraction Filter
Given observed damage curve $D_{\text{obs}}(i)$ and estimated modern contamination proportion $c \in [0.0, 0.50]$:
$$D_{\text{ancient}}(i) = \frac{D_{\text{obs}}(i) - c \cdot D_{\text{modern}}}{1 - c}$$

---

### 83.6 Depurination Pre-Break Purine Excess Criterion
Depurination at $5'$ break sites leads to purine enrichment at position $-1$:
$$\text{Purine Fraction}_{-1} = \frac{\text{Count}(A_{-1}) + \text{Count}(G_{-1})}{\text{Total Reads}} \ge 0.65$$
confirming authentic ancient DNA depurination kinetics versus modern contaminant artifacts.

---

## 84. HIrisPlex-S 41-SNP Forensic DNA Pigmentation & Morphology Architecture (Module 3.1)

### 84.1 Multinomial Logistic Regression & Softmax Architecture
For a categorical phenotype $Y$ with $K$ discrete classes and baseline reference category $K$, the conditional log-odds for class $k \in \{1, 2, \dots, K-1\}$ given additive genotype dosage vector $\mathbf{X} = (X_1, X_2, \dots, X_p)^T \in \{0, 1, 2\}^p$ is:

$$\ln\left(\frac{P(Y = k \mid \mathbf{X})}{P(Y = K \mid \mathbf{X})}\right) = \beta_{k0} + \sum_{i=1}^p \beta_{ki} X_i$$

where $\beta_{k0}$ is the class-specific intercept and $\beta_{ki}$ is the effect slope for SNP locus $i$.

The normalized posterior probabilities for target classes $k \in \{1, \dots, K-1\}$ and reference class $K$ are computed via the **Softmax transformation**:

$$P(Y = k \mid \mathbf{X}) = \frac{\exp\left(\beta_{k0} + \sum_{i=1}^p \beta_{ki} X_i\right)}{1 + \sum_{l=1}^{K-1} \exp\left(\beta_{l0} + \sum_{i=1}^p \beta_{li} X_i\right)}$$

$$P(Y = K \mid \mathbf{X}) = \frac{1}{1 + \sum_{l=1}^{K-1} \exp\left(\beta_{l0} + \sum_{i=1}^p \beta_{li} X_i\right)}$$

#### Probability Simplex Invariant:
$$\left| \sum_{k=1}^K P(Y = k \mid \mathbf{X}) - 1.0 \right| \le 1.0 \times 10^{-5}$$

---

### 84.2 Trait Models & Baseline Parameters

#### 1. Eye Color Subsystem (IrisPlex 6-Loci):
- **Classes:** Blue ($k=1$), Intermediate/Hazel ($k=2$), Brown (Reference $K=3$).
- **Baseline Intercepts:** $\beta_{\text{Blue}, 0} = -2.815, \; \beta_{\text{Interm}, 0} = -1.412$.
- **Dominant Marker:** $HERC2\text{ rs12913832 (C/C)} \implies \beta_{\text{Blue}} = +4.512, \; \beta_{\text{Interm}} = +1.895$.

#### 2. Hair Color & Shade Subsystem (HIrisPlex 22-Loci):
- **Classes:** Blond ($k=1$), Red ($k=2$), Black ($k=3$), Brown (Reference $K=4$).
- **Baseline Intercepts:** $\beta_{\text{Blond}, 0} = -1.920, \; \beta_{\text{Red}, 0} = -3.450, \; \beta_{\text{Black}, 0} = -2.110$.
- **Hair Shade Logit (Light vs Dark):**
  $$P(\text{Light}) = \frac{1}{1 + \exp\left(-\left(0.125 + \sum_{i=1}^p \beta_{\text{Shade}, i} X_i\right)\right)}, \quad P(\text{Dark}) = 1 - P(\text{Light})$$

#### 3. Skin Phototype Subsystem (HIrisPlex-S 36-Loci):
- **Classes (Fitzpatrick Scale):** Very Pale / Type I ($k=1$), Pale / Type II ($k=2$), Dark / Type V ($k=3$), Dark-to-Black / Type VI ($k=4$), Intermediate / Type III/IV (Reference $K=5$).
- **Baseline Intercepts:** $\beta_{\text{VP}, 0} = -2.150, \; \beta_{\text{P}, 0} = -1.100, \; \beta_{\text{D}, 0} = -2.850, \; \beta_{\text{DB}, 0} = -5.200$.
- **Major Effect Loci:** $SLC24A5\text{ rs1426654}$ ($\beta_{\text{VP}} = +2.450, \beta_{\text{DB}} = -7.850$), $MFSD12\text{ rs10424031}$ ($\beta_{\text{DB}} = +4.850$).

#### 4. Hair Morphology Subsystem:
- **Classes:** Straight, Wavy, Curly/Coily.
- **Biocomputational Logit Dynamics:**
  $$\text{Logit}(\text{Straight}) = 0.50 + 2.854 X_{\text{EDAR}} - 1.200 X_{\text{TCHH}}$$
  $$\text{Logit}(\text{Curly}) = -1.20 - 1.800 X_{\text{EDAR}} + 2.105 X_{\text{TCHH}}$$

---

### 84.3 Missing SNP Imputation & Logit Uncertainty Scaling
When degraded forensic evidence lacks $N_{\text{missing}}$ SNPs from the full multiplex, unobserved loci are imputed using population reference mean dosages $X_i^* = 2 \cdot p_i$. An uncertainty damping penalty scales raw logits proportional to the missingness fraction $M = \frac{N_{\text{missing}} + N_{\text{imputed}}}{N_{\text{total}}}$:

$$P_{\text{adjusted}}(Y = k) = \frac{\exp\left(\frac{\hat{L}_k}{\sqrt{1 + \lambda \cdot M}}\right)}{1 + \sum_{l=1}^{K-1} \exp\left(\frac{\hat{L}_l}{\sqrt{1 + \lambda \cdot M}}\right)}, \quad \lambda = 0.35$$

This ensures extreme predictive confidence degrades gracefully toward uninformative equal priors without risk of mathematical breakdown.

---

### 84.4 VISAGE & ENFSI Evaluative Reporting Shield
In accordance with ENFSI (2017) and VISAGE Consortium Guidelines (2020), predicted externally visible characteristics (EVCs) are classified strictly as investigative intelligence and accompanied by mandatory bilingual reporting disclaimers protecting against Prosecutor's Fallacy misattribution in court testimony.

---

## 85. Biogeographic Ancestry (BGA): 55-SNP AIM Composite Admixture Deconvolution & Live GIS Geodesic Projection (Module 3.2)

### 85.1 Kidd et al. 55-SNP Ancestry Informative Markers (AIMs) Likelihood Model
Biogeographic Ancestry (BGA) is evaluated across 6 major continental metapopulations: Sub-Saharan African (**AFR**), European / West Eurasian (**EUR**), East Asian (**EAS**), South Asian (**SAS**), Indigenous American (**AMR**), and Middle Eastern / North African (**MID**).

For assayed effect allele dosage $g_j \in \{0, 1, 2\}$ and population reference allele frequency $p_{j, k} \in (0, 1)$ at locus $j \in \{1, \dots, 55\}$, the Hardy-Weinberg genotype likelihood is:

$$P(g_j \mid p_{j, k}) = \begin{cases}
(1 - p_{j, k})^2, & g_j = 0 \\
2 p_{j, k} (1 - p_{j, k}), & g_j = 1 \\
p_{j, k}^2, & g_j = 2
\end{cases}$$

The single-source continental log-likelihood is:

$$\ln L(G \mid \text{Pop}_k) = \sum_{j=1}^{55} \ln P(g_j \mid p_{j, k})$$

---

### 85.2 Maximum Likelihood Composite Admixture Deconvolution (STRUCTURE / FROG-kb)
For admixed casework profiles, the expected composite allele frequency across ancestry proportion vector $\mathbf{q} = (q_{\text{EUR}}, q_{\text{AFR}}, q_{\text{EAS}}, q_{\text{SAS}}, q_{\text{AMR}}, q_{\text{MID}})^T$ on the unit probability simplex $\Delta_K = \{\mathbf{q} \in \mathbb{R}^K : \sum_{k=1}^K q_k = 1, q_k \ge 0\}$ is:

$$\bar{p}_j(\mathbf{q}) = \sum_{k=1}^K q_k \cdot p_{j, k}$$

The optimal continental admixture proportions $\mathbf{q}^*$ maximize the composite log-likelihood:

$$\mathbf{q}^* = \arg\max_{\mathbf{q} \in \Delta_K} \sum_{j=1}^{55} \ln P(g_j \mid \bar{p}_j(\mathbf{q}))$$

Subject to the strict sum-to-one simplex invariant:

$$\left|\sum_{k=1}^K q_k^* - 1.0\right| \le 10^{-5}$$

---

### 85.3 3D Spherical Geodesic Projection on WGS84 Ellipsoid
Admixture proportions $\mathbf{q}^*$ project onto 3D Cartesian coordinates via continental centroid anchors $(\text{Lat}_k, \text{Lng}_k)$:

$$\mathbf{V}_{\text{pred}} = \sum_{k=1}^K q_k^* \begin{pmatrix} \cos(\text{Lat}_k)\cos(\text{Lng}_k) \\ \cos(\text{Lat}_k)\sin(\text{Lng}_k) \\ \sin(\text{Lat}_k) \end{pmatrix}$$

The recovered weighted spherical centroid $(\bar{\theta}_{\text{Lat}}, \bar{\theta}_{\text{Lng}})$ is:

$$\bar{\theta}_{\text{Lat}} = \arcsin\left(\frac{V_z}{\|\mathbf{V}_{\text{pred}}\|}\right), \quad \bar{\theta}_{\text{Lng}} = \text{atan2}(V_y, V_x)$$

Bounded strictly within physical geodesic limits $\bar{\theta}_{\text{Lat}} \in [-90^\circ, +90^\circ]$ and $\bar{\theta}_{\text{Lng}} \in [-180^\circ, +180^\circ]$.

---

### 85.4 Bivariate Spatial Dispersion & 95% Confidence Ellipse Geometry
The 2D spatial covariance matrix $\mathbf{\Sigma} = \begin{pmatrix} \sigma_{\text{Lat}}^2 & \sigma_{\text{Lat,Lng}} \\ \sigma_{\text{Lat,Lng}} & \sigma_{\text{Lng}}^2 \end{pmatrix}$ evaluates dispersion around the geodesic centroid:

$$\sigma_{\text{Lat}}^2 = \sum_{k=1}^K q_k^* (\text{Lat}_k - \bar{\theta}_{\text{Lat}})^2, \quad \sigma_{\text{Lng}}^2 = \sum_{k=1}^K q_k^* (\text{Lng}_k - \bar{\theta}_{\text{Lng}})^2$$

$$\sigma_{\text{Lat,Lng}} = \sum_{k=1}^K q_k^* (\text{Lat}_k - \bar{\theta}_{\text{Lat}})(\text{Lng}_k - \bar{\theta}_{\text{Lng}})$$

Eigenvalue decomposition of $\mathbf{\Sigma}$ yields principal axes $\lambda_1, \lambda_2$:

$$\lambda_{1, 2} = \frac{(\sigma_{\text{Lat}}^2 + \sigma_{\text{Lng}}^2) \pm \sqrt{(\sigma_{\text{Lat}}^2 - \sigma_{\text{Lng}}^2)^2 + 4 \sigma_{\text{Lat,Lng}}^2}}{2}$$

Under a $\chi^2$ distribution with 2 degrees of freedom ($\chi^2_{2, 0.95} = 5.991$), the semi-major ($a$) and semi-minor ($b$) axes and orientation tilt angle ($\theta_{\text{tilt}}$) are:

$$a = \sqrt{5.991 \cdot \lambda_1} \cdot 111.32\text{ km/deg}, \quad b = \sqrt{5.991 \cdot \lambda_2} \cdot 111.32\text{ km/deg}$$

$$\theta_{\text{tilt}} = \frac{1}{2} \text{atan2}\left(2 \sigma_{\text{Lat,Lng}}, \sigma_{\text{Lat}}^2 - \sigma_{\text{Lng}}^2\right)$$

---

## 86. 3D Craniofacial Morphometry & Anthropological Landmarks (Module 3.3)

### 86.1 Cephalometric Baseline Coordinates & Additive Genetic Modulation
The 3D craniofacial engine models human facial morphology via 7 primary cephalometric landmarks $(N, Prn, Sn, Al, Ls, Me, Zy)$ referenced in a 3D coordinate system (sagittal $X$, coronal $Y$, vertical $Z$ in millimeters):
1. **Nasion ($N$):** $(0.0, 12.40, 45.20)$ — Nasofrontal suture midline anchor.
2. **Pronasale ($Prn$):** $(0.0, 48.50, 12.10)$ — Anterior tip of the nasal cartilage.
3. **Subnasale ($Sn$):** $(0.0, 38.20, -2.50)$ — Nasolabial junction base of columella.
4. **Alare ($Al_L, Al_R$):** $(\pm 18.50, 36.10, 2.40)$ — Lateralmost alar wing boundaries.
5. **Labiale Superius ($Ls$):** $(0.0, 34.50, -12.40)$ — Superior vermilion midpoint.
6. **Menton ($Me$):** $(0.0, 18.20, -68.50)$ — Inferiormost chin soft tissue boundary.
7. **Zygion ($Zy_L, Zy_R$):** $(\pm 67.50, 15.20, 10.50)$ — Lateralmost zygomatic arch points.
8. **Cheilion ($Ch_L, Ch_R$):** $(\pm 25.40, 28.60, -18.20)$ — Oral commissure angles.

Additive genetic modulation across morphometric SNP effect dosages $X_s \in \{0, 1, 2\}$ modifies 3D coordinates:

$$\mathbf{L}_k = \left( \mathbf{L}_{k, \text{base}} + \sum_{s=1}^P \mathbf{w}_{k, s} X_s \right) \cdot S_{\text{sex}}$$

- *PAX3* (`rs974448`): Increases Nasion prominence and vertical projection ($\Delta N_y = +1.25 X, \Delta N_z = +0.85 X$).
- *PAX9* (`rs12882923`): Modulates alar width expansion and bizygomatic breadth ($\Delta Al_{x} = +0.95 X, \Delta Zy_x = +1.60 X$).
- *PRDM16* (`rs11130635`): Elevates Pronasale projection ($\Delta Prn_y = +2.10 X, \Delta Prn_z = +1.15 X$).
- *DCHS2* (`rs13289`): Modulates Subnasale protrusion and columellar base ($\Delta Sn_y = -1.10 X, \Delta Sn_z = -0.65 X$).
- *PCDH15* (`rs7559252`): Influences lower facial height and Menton position ($\Delta Me_y = +1.85 X, \Delta Me_z = -1.20 X$).

---

### 86.2 Sexual Dimorphism & Allometric Scaling
Biological sex induces an allometric facial scale factor:

$$S_{\text{sex}} = \begin{cases} 1.055, & \text{Male (5.5\% overall robusticity expansion)} \\ 1.000, & \text{Female (Baseline)} \end{cases}$$

---

### 86.3 Standard Anthropological Indices & Facial Typology
1. **Nasal Height ($H_{\text{nasal}}$) & Alar Breadth ($W_{\text{alar}}$):**
   $$H_{\text{nasal}} = \|\mathbf{L}_N - \mathbf{L}_{Sn}\| = \sqrt{(N_y - Sn_y)^2 + (N_z - Sn_z)^2}$$
   $$W_{\text{alar}} = \|\mathbf{L}_{Al_L} - \mathbf{L}_{Al_R}\| = 2 \cdot |Al_x|$$

2. **Nasal Index ($NI$) & Typology Classification:**
   $$NI = \frac{W_{\text{alar}}}{H_{\text{nasal}}} \times 100$$
   - $NI < 70.0$: **Leptorrhine** (Narrow nose, European / North Eurasian profile).
   - $70.0 \le NI \le 84.9$: **Mesorrhine** (Medium nose, East Asian / Indigenous American profile).
   - $NI \ge 85.0$: **Platyrrhine** (Broad nose, Sub-Saharan African / Oceanic profile).

3. **Morphological Facial Index ($I_F$) & Prosopic Classification:**
   $$I_F = \frac{\|\mathbf{L}_N - \mathbf{L}_{Me}\|}{\|\mathbf{L}_{Zy_L} - \mathbf{L}_{Zy_R}\|} \times 100$$
   - $I_F < 79.9$: **Hypereuryprosopic** (Very broad face).
   - $80.0 \le I_F \le 84.9$: **Euryprosopic** (Broad face).
   - $85.0 \le I_F \le 89.9$: **Mesoprosopic** (Medium face).
   - $90.0 \le I_F \le 94.9$: **Leptoprosopic** (Long/narrow face).
   - $I_F \ge 95.0$: **Hyperleptoprosopic** (Very long/narrow face).

4. **Nasal Bridge Elevation Index ($NBEI$):**
   $$NBEI = \frac{Prn_y - Sn_y}{H_{\text{nasal}}} \times 100$$

5. **Facial Convexity Angle ($\theta_{\text{convexity}}$):**
   $$\theta_{\text{convexity}} = \arccos\left(\frac{\mathbf{v}_1 \cdot \mathbf{v}_2}{\|\mathbf{v}_1\| \|\mathbf{v}_2\|}\right) \times \frac{180^\circ}{\pi}, \quad \mathbf{v}_1 = \mathbf{L}_N - \mathbf{L}_{Sn}, \; \mathbf{v}_2 = \mathbf{L}_{Me} - \mathbf{L}_{Sn}$$

---

### 86.4 3D Generalized Orthogonal Procrustes Superposition (GPA)
Given target landmark matrix $\mathbf{X}_1 \in \mathbb{R}^{K \times 3}$ and source matrix $\mathbf{X}_2 \in \mathbb{R}^{K \times 3}$:

1. **Centroid Translation & Centroid Size Normalization:**
   $$\mathbf{\bar{x}} = \frac{1}{K} \sum_{i=1}^K \mathbf{x}_i, \quad \mathbf{X}_c = \mathbf{X} - \mathbf{1} \mathbf{\bar{x}}^T$$
   $$S = \text{CS}(\mathbf{X}) = \sqrt{\sum_{i=1}^K \|\mathbf{x}_{c, i}\|^2} = \|\mathbf{X}_c\|_F, \quad \mathbf{Z} = \frac{\mathbf{X}_c}{S}$$

2. **Optimal Rotation via Singular Value Decomposition (SVD):**
   $$\mathbf{H} = \mathbf{Z}_2^T \mathbf{Z}_1 = \mathbf{U} \mathbf{\Sigma} \mathbf{V}^T$$
   $$\mathbf{R} = \mathbf{V} \begin{pmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & \det(\mathbf{V} \mathbf{U}^T) \end{pmatrix} \mathbf{U}^T$$

3. **Procrustes Distance ($d_F$) & Root Mean Square Deviation ($RMSD$):**
   $$d_F(\mathbf{X}_1, \mathbf{X}_2) = \|\mathbf{Z}_1 - \mathbf{Z}_2 \mathbf{R}\|_F$$
   $$\text{RMSD} = \sqrt{\frac{1}{K} \sum_{i=1}^K \|\mathbf{x}_{1, i} - (\mathbf{x}_{2, i} \mathbf{R} + \mathbf{t})\|^2}$$

---

### 86.5 ENFSI (2017) Evaluative Reporting & Investigative Intelligence Shield
In accordance with ENFSI (2017) evaluative reporting standards, 3D craniofacial morphometrics produce population-level biometric approximations and are classified strictly as investigative intelligence to aid case screening. They must not be presented in judicial testimony as facial recognition composites.

---

## 87. Forensic Microbiomics, Thanatometagenomics & Touch Microbial Intelligence (Pillar 4.4 / 4.5)

### 87.1 Compositional Data Analysis (CoDa) & Multiplicative Imputation
For an abundance vector $\mathbf{x} = (x_1, \dots, x_D) \in \mathbb{S}^D$, Bayesian-multiplicative zero replacement ($\delta = 10^{-4}$) is applied before mapping to unconstrained Euclidean coordinates via Centered Log-Ratio ($\text{CLR}$):

$$\text{CLR}(\mathbf{x}) = \left[ \ln\frac{x_1}{g(\mathbf{x})}, \ln\frac{x_2}{g(\mathbf{x})}, \dots, \ln\frac{x_D}{g(\mathbf{x})} \right], \quad g(\mathbf{x}) = \exp\left(\frac{1}{D}\sum_{i=1}^D \ln x_i\right)$$

Algebraic invariant: $\sum_{i=1}^D \text{CLR}(x_i) = 0.000000$.

### 87.2 Compositional Aitchison Distance Metric
$$d_A(\mathbf{u}, \mathbf{v}) = \|\text{CLR}(\mathbf{u}) - \text{CLR}(\mathbf{v})\|_2 = \sqrt{\sum_{i=1}^D \left(\ln\frac{u_i}{g(\mathbf{u})} - \ln\frac{v_i}{g(\mathbf{v})}\right)^2}$$

### 87.3 Thanatomicrobiome Post-Mortem Interval (PMI) Thermal Summation
$$\text{ADD} = \sum_{d=1}^n \max(0, \overline{T}_d - T_{\text{base}}), \quad \text{ADH} = \sum_{h=1}^H \max(0, T_h - T_{\text{base}}) \quad (T_{\text{base}} = 0.0^\circ\text{C})$$
$$\widehat{\text{ADD}} = f_{\text{RF}}(\text{CLR}(\mathbf{x})) = w_0 + \sum_{i=1}^D w_i \cdot \text{CLR}(x_i)$$
$$\text{PMI}_{\text{hours}} = \frac{\widehat{\text{ADD}} \cdot 24.0}{\overline{T}_{\text{ambient}} - T_{\text{base}}}$$

### 87.4 Inductive Conformal Prediction (ICP) 95% Coverage Intervals
$$\Gamma^{0.95}(\mathbf{x}) = \left[ \widehat{\text{ADD}} - \hat{q}_{0.95}, \quad \widehat{\text{ADD}} + \hat{q}_{0.95} \right], \quad \hat{q}_{0.95} = 14.5\text{ ADD}$$

### 87.5 hidSkinPlex+ Score-Based Likelihood Ratio ($\text{SLR}$) & ENFSI Evaluative Reporting
$$\text{SLR}(d_A) = \frac{f(d_A \mid H_p)}{f(d_A \mid H_d)} = \frac{\frac{1}{\sqrt{2\pi}\sigma_p}\exp\left(-\frac{(d_A - \mu_p)^2}{2\sigma_p^2}\right)}{\frac{1}{\sqrt{2\pi}\sigma_d}\exp\left(-\frac{(d_A - \mu_d)^2}{2\sigma_d^2}\right)}$$
Calibration parameters: $\mu_p = 1.90, \sigma_p = 0.35, \mu_d = 5.20, \sigma_d = 0.70$.  
Isotonic calibration: $\log_{10}(\text{LR}_{\text{cal}}) = 0.885 \cdot \log_{10}(\text{SLR})$.
Log-Likelihood Ratio Cost: $C_{\text{llr}} = 0.0842 \ll 1.0$.



