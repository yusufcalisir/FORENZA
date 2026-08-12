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

## 2. Single-Source Genotype Olasılıkları & Substructure ($\theta$)

### 2.1 Hardy-Weinberg Genotype Probabilities ($\theta = 0$)
For a locus with allele $A_i$ of frequency $p_i$ and allele $A_j$ of frequency $p_j$:

$$P(A_i A_i) = p_i^2$$

$$P(A_i A_j) = 2 p_i p_j \quad (i \neq j)$$

### 2.2 Balding-Nichols $\theta$-Correction (NRC II Recommendation 4.10b)
To account for population substructure with coancestry coefficient $\theta$:

#### Homozygote ($A_i A_i$):
$$P(A_i A_i \mid \theta) = \frac{\left[2\theta + (1-\theta)p_i\right] \left[\theta + (1-\theta)p_i\right]}{(1+\theta)(1+2\theta)}$$

#### Heterozygote ($A_i A_j$, $i \neq j$):
$$P(A_i A_j \mid \theta) = \frac{2 \left[\theta + (1-\theta)p_i\right] \left[\theta + (1-\theta)p_j\right]}{(1+\theta)(1+2\theta)}$$

---

## 3. Kinship Index ($KI$) Formulations

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

## 5. Continuous Peak Height Model

Let $h_{l,a}$ be the observed peak height for allele $a$ at locus $l$. The expected peak height $\mu_{l,a}$ is modeled based on mass fraction $w_k$ of contributor $k$, locus amplification efficiency $e_l$, and degradation slope $d_l$:

$$\mu_{l,a} = e_l \sum_{k=1}^{K} w_k \cdot f_k(a) \cdot 10^{-d_l \cdot \text{size}(a)}$$

Observed peak height $h_{l,a}$ follows a log-normal distribution centered at expected height $\mu_{l,a}$ with variance $\sigma^2$:

$$\ln(h_{l,a}) \sim \mathcal{N}\left(\ln(\mu_{l,a}), \frac{\sigma^2}{\mu_{l,a}^\gamma}\right)$$

where $\gamma$ is the peak height variance power parameter.

### 5.1 Stutter Model ($S_{n-1}$)
Expected $n-1$ stutter height $h_{\text{stutter}}$ for parent allele height $h_{\text{parent}}$:

$$h_{\text{stutter}} = R_{l} \cdot h_{\text{parent}}$$

where $R_{l}$ is the locus-specific linear stutter ratio slope.

---

## 6. MCMC & Uncertainty Quantification

### 6.1 Posterior Distribution
Using Metropolis-Hastings / MCMC sampling, parameter vector $\boldsymbol{\theta} = \{w_1, \dots, w_K, e_1, \dots, e_L, d_1, \dots, d_L, \sigma^2\}$ is sampled from the posterior distribution:

$$P(\boldsymbol{\theta} \mid E) \propto P(E \mid \boldsymbol{\theta}) \cdot P(\boldsymbol{\theta})$$

### 6.2 95% Highest Posterior Density (HPD) Interval
The 95% HPD interval $[LR_{\text{low}}, LR_{\text{high}}]$ for the estimated $LR$ is calculated from the $M$ MCMC post-burn-in iterations:

$$\int_{LR_{\text{low}}}^{LR_{\text{high}}} P(LR \mid E) \, dLR = 0.95$$

The lower bound $LR_{\text{low}}$ is reported in court proceedings as the conservative statistical weight of evidence.

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






















