# Y-STR 27-Locus (Yfiler Plus) & mtDNA (EMPOP / Control Region) Lineage & Haplotype Forensics Research Specification

## FORENZA Biocomputational Engine: ISO/IEC 17025 Architecture Specification for Y-STR 27-Locus Multiplexing & mtDNA Control Region Phylogenetics

---

## 1. Y-STR 27-Locus Master Registry, Panel Physics & Mutation Dynamics

### 1.1 27 Loci Master Specification Table (Thermo Fisher Yfiler Plus)
The FORENZA Forensic Evidence Operating System incorporates the Thermo Fisher Scientific Yfiler Plus 27-locus multiplex panel. This multiplex system combines core forensic Y-STR loci with seven Rapidly Mutating Y-STR (RM Y-STR) markers designed to improve discrimination between patrilineally related male individuals. Physical genomic coordinates are aligned with the GRCh38 human genome assembly across the male-specific non-recombining region of the Y chromosome (MSY). Electrophoretic amplicon size ranges reflect standard 6-dye capillary electrophoresis (CE) chemistry utilizing 6-FAM, VIC, NED, TAZ, SID, and the LIZ size standard. Germline mutation rates ($\mu_l$) represent father-son transmission events established through pedigree and population studies.

| Locus Name | Cytogenetic Band | GRCh38 Coordinates (bp) | Repeat Unit (bp) | Canonical Repeat Motif Sequence | CE Dye / Amplicon Range (bp) | Mutation Rate $\mu_l$ (mut/gen) | Stepwise Param ($r_l$) | Mutation Class |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DYS19** | Yp11.2 | 9,471,048–9,471,430 | 4 | `[TAGA]` | 6-FAM / 170–210 | $2.3 \times 10^{-3}$ | 0.95 | Standard |
| **DYS389I** | Yq11.221 | 12,423,733–12,424,100 | 4 | `[TCTG] [TCTA]` | VIC / 140–180 | $2.6 \times 10^{-3}$ | 0.94 | Standard |
| **DYS389II** | Yq11.221 | 12,423,600–12,424,100 | 4 | `[TCTG] [TCTA] ... [TCTG] [TCTA]` | VIC / 250–310 | $4.2 \times 10^{-3}$ | 0.92 | Standard |
| **DYS390** | Yq11.221 | 17,281,230–17,281,600 | 4 | `[TCTG] [TCTA]` | NED / 190–240 | $2.1 \times 10^{-3}$ | 0.95 | Standard |
| **DYS391** | Yq11.221 | 13,887,400–13,887,700 | 4 | `[TCTA]` | NED / 95–135 | $1.0 \times 10^{-3}$ | 0.98 | Standard |
| **DYS392** | Yq11.221 | 22,589,100–22,589,450 | 3 | `[TAT]` | TAZ / 280–340 | $3.75 \times 10^{-4}$ | 0.99 | Standard |
| **DYS393** | Yp11.2 | 3,110,200–3,110,500 | 4 | `[AGAT]` | 6-FAM / 110–150 | $1.1 \times 10^{-3}$ | 0.97 | Standard |
| **DYS385a/b** | Yq11.223 | 20,850,100–20,851,200 | 4 | `[GAAA]` | VIC / 240–330 | $2.2 \times 10^{-3}$ | 0.93 | Multi-Copy |
| **DYS437** | Yq11.221 | 14,451,100–14,451,400 | 4 | `[TATC]` | VIC / 180–220 | $1.2 \times 10^{-3}$ | 0.96 | Standard |
| **DYS438** | Yq11.221 | 14,910,200–14,910,500 | 5 | `[TTTTC]` | TAZ / 200–250 | $3.75 \times 10^{-4}$ | 0.99 | Standard |
| **DYS439** | Yq11.221 | 14,352,100–14,352,450 | 4 | `[AGAT]` | 6-FAM / 210–250 | $2.4 \times 10^{-3}$ | 0.94 | Standard |
| **DYS448** | Yq11.223 | 24,420,100–24,420,600 | 6 | `[AGAGAT]` | VIC / 280–350 | $1.4 \times 10^{-3}$ | 0.96 | Standard |
| **DYS456** | Yq11.221 | 16,112,000–16,112,350 | 4 | `[AGAT]` | 6-FAM / 130–170 | $3.8 \times 10^{-3}$ | 0.91 | Standard |
| **DYS458** | Yq11.221 | 7,901,100–7,901,500 | 4 | `[GAAA]` | NED / 130–180 | $8.7 \times 10^{-3}$ | 0.88 | Standard |
| **DYS635** | Yq11.221 | 14,212,100–14,212,500 | 4 | `[TCTA] [TCTG]` | TAZ / 200–260 | $2.5 \times 10^{-3}$ | 0.94 | Standard |
| **YGATAH4** | Yq11.221 | 18,720,100–18,720,400 | 4 | `[AGAT]` | TAZ / 120–160 | $1.8 \times 10^{-3}$ | 0.96 | Standard |
| **DYS460** | Yq11.221 | 11,811,200–11,811,500 | 4 | `[ATAG]` | VIC / 100–140 | $2.1 \times 10^{-3}$ | 0.95 | Standard |
| **DYS481** | Yq11.221 | 8,502,100–8,502,500 | 3 | `[CTT]` | SID / 100–150 | $2.8 \times 10^{-3}$ | 0.93 | Standard |
| **DYS533** | Yq11.221 | 15,201,100–15,201,400 | 4 | `[ATCT]` | SID / 160–200 | $1.5 \times 10^{-3}$ | 0.96 | Standard |
| **DYS570** | Yq11.221 | 6,812,100–6,812,500 | 4 | `[TTTC]` | SID / 210–260 | $1.2 \times 10^{-2}$ | 0.82 | Rapidly Mutating |
| **DYS576** | Yq11.221 | 6,911,200–6,911,600 | 4 | `[AAAG]` | SID / 270–330 | $1.4 \times 10^{-2}$ | 0.80 | Rapidly Mutating |
| **DYS627** | Yq11.221 | 21,210,100–21,210,600 | 4 | `[AAAG] [AGAG]` | SID / 340–410 | $1.3 \times 10^{-2}$ | 0.81 | Rapidly Mutating |
| **DYS518** | Yq11.223 | 20,410,200–20,410,800 | 4 | `[AAAG]` | TAZ / 360–440 | $1.8 \times 10^{-2}$ | 0.75 | Rapidly Mutating |
| **DYS449** | Yq11.221 | 11,210,100–11,210,600 | 4 | `[TTTC]` | NED / 290–370 | $1.2 \times 10^{-2}$ | 0.83 | Rapidly Mutating |
| **DYF387S1a/b** | Yq11.221 | 22,100,100–22,102,500 | 4 | `[AAAG]` | 6-FAM / 280–360 | $1.6 \times 10^{-2}$ | 0.78 | RM / Multi-Copy |

---

### 1.2 Multi-Copy & Duplicated Loci Modeling
The Thermo Fisher Yfiler Plus panel includes two multi-copy, duplicated STR systems: **DYS385a/b** and **DYF387S1a/b**. Unlike single-copy Y-STR loci that yield one allele per single-source male sample, multi-copy loci simultaneously amplify two distinct genomic locations on the Y chromosome.

1. **Homozygous Calls ($a = b$):**
   When both duplicated copies possess identical allele lengths, a single electrophoretic peak is observed. The signal intensity (Relative Fluorescence Units, RFU) represents the additive amplification of both chromosomal sites:
   $$\text{RFU}_{\text{homozygous}} = \text{RFU}_a + \text{RFU}_b$$

2. **Heterozygous Calls ($a \neq b$):**
   When repeat lengths differ, two distinct peaks are observed. For single-source male profiles, the signal balance between these peaks is evaluated using the Peak Height Ratio (PHR):
   $$\text{PHR} = \frac{\min(\text{RFU}_a, \text{RFU}_b)}{\max(\text{RFU}_a, \text{RFU}_b)}$$
   The analytical threshold for confirming a single-source male donor at multi-copy loci requires $\text{PHR} \ge 0.50$. Values below $0.50$ flag potential multi-donor DNA mixtures or copy-number alterations.

3. **Tri-Allelic Duplications:**
   Locus duplication events and inter-locus gene conversions can alter expected copy numbers. Tri-allelic patterns (such as alleles 11, 12, 13 at DYS385a/b or 35, 36, 37 at DYF387S1a/b) occur when one locus undergoes segmental duplication. When evaluating tri-allelic calls, an imbalance ratio ($\text{PHR} < 0.35$ for one peak relative to a 2:1 cumulative area ratio among the remaining peaks) triggers automated system flags to distinguish gene duplications from minor contributor signals in mixture deconvolution.

---

### 1.3 Complex Nested Repeats & Intermediate Alleles
The **DYS389I** and **DYS389II** loci represent a nested repeat system where the forward primer for DYS389II binds upstream of the DYS389I region. Consequently, the amplicon generated at DYS389II physically includes the entire DYS389I repeat block along with an adjacent, independent variable repeat block designated DYS389.2:
$$\text{DYS389II}_{\text{total}} = \text{DYS389I} + \text{DYS389.2}$$

To calculate genetic distances or evaluate population match probabilities without double-counting alleles, the FORENZA engine decouples DYS389II into its pure variable component:
$$\text{DYS389.2}_{\text{pure}} = \text{DYS389II}_{\text{total}} - \text{DYS389I}$$

Mutations observed at DYS389I automatically alter the absolute allele designation of DYS389II. The computational core evaluates haplotype comparisons using the decoupled allele pair $[\text{DYS389I}, \text{DYS389.2}_{\text{pure}}]$.

#### Micro-Variants & Off-Ladder Alleles
- **DYS458.2 Micro-Variants:** Common in Western Eurasian and Middle Eastern lineages, these variants stem from a 2-bp insertion within the flanking region of the `[GAAA]` motif, creating fractional calls such as `16.2` or `17.2`.
- **DYS385a/b Intermediate Alleles:** Non-integer repeats (e.g., `11.1`, `13.3`) caused by single-base insertions within the variable flanking sequence.
- **DYS448 Partial Micro-Deletions:** The canonical DYS448 repeat motif `[AGAGAT]` features a non-repeat 6-bp deletion site. Loss of this structural block produces allele shifts (such as allele `19.2`) or localized partial null alleles.

---

## 2. Y-STR Population Genetics, YHRD Match Probabilities & Haplogroup Prediction

### 2.1 YHRD Haplotype Frequency Estimation & Non-Recombining Lineage Statistics
Because the male-specific region of the Y chromosome does not undergo meiotic recombination, alleles across all 27 Y-STR loci are transmitted as a single non-recombining haplotype block. Consequently, the product rule used in autosomal STR analysis cannot be applied to Y-STR loci. Frequency estimates rely on population databases such as the Y-Chromosome Haplotype Reference Database (YHRD).

#### Exact Clopper-Pearson 95% Binomial Confidence Bounds
For an unobserved haplotype ($k = 0$) in a reference database of size $N$, the exact upper 95% confidence bound ($\hat{p}_{\text{upper}}$) is calculated as:
$$\hat{p}_{\text{upper}} = 1 - (0.05)^{\frac{1}{N+1}}$$

For observed haplotypes where $k > 0$ matches are present in a database size $N$, the upper bound of the Clopper-Pearson interval is derived using the Snedecor $F$-distribution at significance level $\alpha = 0.05$:
$$\hat{p}_{\text{upper}} = \frac{(k+1) F_{2(k+1), 2(N-k); 1-\alpha/2}}{(N-k) + (k+1) F_{2(k+1), 2(N-k); 1-\alpha/2}}$$

| Database Size ($N$) | Observed Matches ($k$) | Point Estimate ($k/N$) | Upper 95% Clopper-Pearson Bound ($\hat{p}_{\text{upper}}$) | Equivalent Match Ratio |
| :--- | :--- | :--- | :--- | :--- |
| **35,000** | 0 | 0.0000000 | $8.56 \times 10^{-5}$ | 1 in 11,682 |
| **35,000** | 1 | 0.0000286 | $1.59 \times 10^{-4}$ | 1 in 6,281 |
| **35,000** | 2 | 0.0000571 | $2.19 \times 10^{-4}$ | 1 in 4,570 |
| **35,000** | 5 | 0.0001429 | $3.33 \times 10^{-4}$ | 1 in 2,999 |
| **35,000** | 10 | 0.0002857 | $5.12 \times 10^{-4}$ | 1 in 1,953 |

#### Brenner Subpopulation Correction
To account for population sub-structure and shared ancestry in non-recombining lineages, the Brenner formulation incorporates the co-ancestry coefficient $\theta$ ($F_{st}$):
$$p_{\text{Brenner}} = \frac{k + \theta}{N + \theta}$$
where $\theta$ is typically assigned values between $0.01$ and $0.03$ based on regional subpopulation dynamics.

#### Discrete Laplace Mixture Smoothing Model
To evaluate high-dimensional 27-locus Y-STR profiles that are absent from available reference databases, FORENZA implements the Discrete Laplace Mixture Model:
$$P(H) = \sum_{c=1}^C w_c \prod_{l=1}^{27} f_l(y_l \mid \mu_{cl}, \lambda_{cl})$$
where $w_c$ represents the mixture weight of cluster $c$ ($\sum w_c = 1$), $\mu_{cl}$ is the modal allele count of locus $l$ in cluster $c$, and $f_l(y_l \mid \mu_{cl}, \lambda_{cl})$ is the marginal probability defined by:
$$f_l(y_l \mid \mu_{cl}, \lambda_{cl}) = \frac{1 - \lambda_{cl}}{1 + \lambda_{cl}} \lambda_{cl}^{|y_l - \mu_{cl}|}$$
Here, $\lambda_{cl} = e^{-\beta_{cl}}$ governs the dispersion parameter reflecting the localized mutation scale.

---

### 2.2 Y-DNA Haplogroup Prediction Engine
The system predicts major Y-DNA haplogroups directly from 27-locus Y-STR vectors using a Bayesian decision framework combined with genetic distance metrics relative to verified Y-SNP modal profiles.

The posterior probability $P(\text{Hg}_i \mid V)$ for haplogroup $\text{Hg}_i$ given an input Y-STR vector $V = (y_1, y_2, \dots, y_{27})$ is computed as:
$$P(\text{Hg}_i \mid V) = \frac{P(\text{Hg}_i) \prod_{l=1}^{27} P(y_l \mid \text{Hg}_i)}{\sum_{j} P(\text{Hg}_j) \prod_{l=1}^{27} P(y_l \mid \text{Hg}_j)}$$

| Target Haplogroup | Diagnostic Y-STR Modal Signature Key Markers | Primary SNP Marker | Population Distribution |
| :--- | :--- | :--- | :--- |
| **R1b** | DYS393=13, DYS390=24, DYS19=14, DYS391=11, DYS438=12, DYS481=22 | M269 / P312 / U106 | Western Europe, Eurasia |
| **R1a** | DYS393=13, DYS390=25, DYS19=16, DYS391=10, DYS439=10, DYS458=15 | M198 / M417 | Eastern Europe, South Asia |
| **I1** | DYS393=13, DYS390=22, DYS19=14, DYS391=10, DYS437=16, DYS460=11 | M253 | Northern Europe, Scandinavia |
| **I2** | DYS393=15, DYS390=24, DYS19=16, DYS391=10, DYS437=15, DYS458=15 | M438 / L621 | Balkans, Eastern Europe |
| **J1** | DYS393=12, DYS390=23, DYS19=14, DYS458=18, DYS385a/b=14-17 | M267 | Middle East, North Africa |
| **J2** | DYS393=12, DYS390=23, DYS19=15, DYS391=10, DYS438=10, DYS385a/b=13-15 | M172 | Mediterranean, Anatolia |
| **E1b1b** | DYS393=13, DYS390=24, DYS19=13, DYS391=10, DYS439=12, DYS385a/b=11-12 | M215 / M35 | North/East Africa, Southern Europe |
| **E1b1a** | DYS393=15, DYS390=21, DYS19=15, DYS391=10, DYS439=11, DYS385a/b=15-16 | V38 / M2 | Sub-Saharan Africa |
| **G2a** | DYS393=14, DYS390=22, DYS19=15, DYS391=10, DYS438=10, DYS385a/b=13-15 | P15 / L30 | Caucasus, Southern Europe |
| **N** | DYS393=14, DYS390=23, DYS19=14, DYS391=11, DYS392=14 | M231 / Tat | North Eurasia, Fennoscandia |
| **O** | DYS393=12, DYS390=24, DYS19=15, DYS391=10, DYS438=11, DYS385a/b=12-18 | M175 | East Asia, Southeast Asia |
| **Q** | DYS393=13, DYS390=24, DYS19=13, DYS391=10, DYS385a/b=12-13 | M242 / M3 | Americas, North/Central Asia |
| **T** | DYS393=13, DYS390=24, DYS19=15, DYS391=10, DYS438=11, DYS385a/b=11-14 | M184 | Horn of Africa, South Asia |
| **L** | DYS393=12, DYS390=23, DYS19=14, DYS438=10 | M20 | South Asia, Middle East |
| **C** | DYS393=13, DYS390=25, DYS19=15, DYS391=10, DYS385a/b=12-13 | M130 / P39 | Oceania, East Asia, Americas |
| **D** | DYS393=14, DYS390=23, DYS19=16, DYS391=10, DYS385a/b=13-14 | CTS11577 | Tibet, Japan, Andaman |

---

### 2.3 Paternal Kinship Likelihood & RM Y-STR Differentiation

#### Stepwise Mutation Model Kinship Calculations
To evaluate paternal kinship hypotheses ($H_1$: Related by $m$ meioses vs $H_2$: Unrelated male), the system applies the Single-Step Mutation Model (SMM). For a pair of male profiles $Y_A$ and $Y_B$ across 27 loci:
$$P(Y_B \mid Y_A, m) = \prod_{l=1}^{27} P(y_{B,l} \mid y_{A,l}, m, \mu_l)$$

Under single-step mutations, the transmission transition probability across $m$ meioses for a single-copy locus with mutation rate $\mu_l$ is given by:
$$P(y_{B,l} \mid y_{A,l}, m, \mu_l) = \begin{cases} (1 - \mu_l)^m & \text{if } y_{B,l} = y_{A,l} \\ \frac{m \mu_l (1-\mu_l)^{m-1}}{2} & \text{if } |y_{B,l} - y_{A,l}| = 1 \\ \frac{\binom{m}{2} \mu_l^2 (1-\mu_l)^{m-2}}{4} & \text{if } |y_{B,l} - y_{A,l}| = 2 \end{cases}$$

The overall Combined Kinship Index ($\text{CPI}_{\text{Y-STR}}$) comparing $H_1$ to $H_2$ is formulated as:
$$\text{CPI}_{\text{Y-STR}} = \frac{P(Y_B \mid Y_A, m)}{P(Y_B)}$$

#### RM Y-STR Discriminative Power
Standard Y-STRs (with mutation rates $\mu \approx 10^{-3}$) often yield identical 17- to 23-locus haplotypes across close patrilineal relatives, such as brothers, father-son pairs, or cousins. The inclusion of seven RM Y-STRs (DYS570, DYS576, DYS627, DYS518, DYS449, DYF387S1a/b), each exhibiting mutation rates $\mu \ge 1.0 \times 10^{-2}$, increases the probability of observing mutational differences across generations.

| Separation Degree ($m$ Meioses) | Relationship Pair Type | Standard 20 Y-STR Panel Differentiation Rate | Yfiler Plus (27 Loci incl. 7 RM Y-STRs) Differentiation Rate |
| :--- | :--- | :--- | :--- |
| **1 Meiosis** | Father - Son | ~2.5% | **~14.8%** |
| **2 Meioses** | Brothers / Paternal Grandfather - Grandson | ~5.1% | **~27.4%** |
| **4 Meioses** | Paternal First Cousins | ~10.2% | **~48.7%** |
| **6 Meioses** | Paternal Second Cousins | ~15.0% | **~64.2%** |

---

### 2.4 Male Mixture Deconvolution ($N_{\text{male}}$)
In complex forensic evidence containing multi-donor male DNA, the minimum number of male contributors ($N_{\text{male}}$) is calculated using peak count criteria across single-copy and double-copy loci:
$$N_{\text{male}} = \max \left( \max_{l \in \text{Single}} \left\lceil \frac{n_{\text{alleles}, l}}{1} \right\rceil, \max_{d \in \text{Multi}} \left\lceil \frac{n_{\text{alleles}, d}}{2} \right\rceil \right)$$

- **Single-copy loci:** Yield a maximum of one allele per male donor. Observing $n$ distinct alleles at any single-copy locus (e.g., 4 alleles at DYS458) establishes at least $N_{\text{male}} = 4$ contributors.
- **Multi-copy loci:** DYS385a/b and DYF387S1a/b possess two chromosomal sites per male donor, allowing up to 2 distinct alleles per single source. Observing $>4$ alleles (e.g., 5 or 6 distinct peak calls) at DYF387S1a/b establishes $N_{\text{male}} \ge \lceil 5 / 2 \rceil = 3$ male contributors.

---

## 3. mtDNA Control Region (D-Loop), EMPOP Alignment & Phylogenetics

### 3.1 Reference Sequence Standards & Control Region Domains

#### Reference Sequence Standards
- **Revised Cambridge Reference Sequence (rCRS):** Derived from GenBank accession number `NC_012920.1` (Andrews et al., 1999). It is the standard reference sequence used in forensic casework. All reported mutations represent substitutions, insertions, or deletions relative to this 16,569-bp sequence.
- **Reconstructed Sapiens Reference Sequence (RSRS):** Formulated by Behar et al. (2012), RSRS bases its coordinates on the estimated ancestral root of the human mtDNA phylogenetic tree. While RSRS helps distinguish ancestral states from derived mutations, the FORENZA system defaults to rCRS for forensic alignment and reporting, per SWGDAM and ISFG guidelines.

#### Control Region Structural Domains
The mitochondrial control region (D-Loop) spans nucleotide positions 16024 through 576.

| Domain Name | Coordinate Boundaries (rCRS) | Biological Function & Diagnostic Relevance |
| :--- | :--- | :--- |
| **HV1 (Hypervariable Region 1)** | 16024–16365 | High mutation rate region; diagnostic for major macro-haplogroups. |
| **HV2 (Hypervariable Region 2)** | 73–340 | Contains primary homopolymeric C-tracts and insertion/deletion hotspots. |
| **HV3 (Hypervariable Region 3)** | 438–574 | Contains variable dinucleotide AC repeat elements and localized lineage markers. |
| **OHR (Origin of Heavy-Strand Repl.)** | 110–441 | Structural origin of heavy-strand replication; spans CSB regions. |
| **CSB I (Conserved Sequence Block I)** | 214–232 | Regulates RNA primer processing and replication initiation. |
| **CSB II (Conserved Sequence Block II)** | 299–315 | Transcription termination site; features the 309/315 poly-C tract. |
| **CSB III (Conserved Sequence Block III)** | 346–363 | Sequence-specific binding site for mitochondrial transcription factors. |

---

### 3.2 ISFG (2014, 2020) & EMPOP Standard Forensic Nomenclature

#### Transitions & Transversions
- **Transitions:** Purine-to-purine ($A \leftrightarrow G$) or pyrimidine-to-pyrimidine ($C \leftrightarrow T$) changes. Examples include `263G` ($A \to G$), `73G` ($A \to G$), and `16519C` ($T \to C$).
- **Transversions:** Purine-to-pyrimidine or pyrimidine-to-purine changes. Examples include `16183C` ($A \to C$) and `145G` ($C \to G$).

#### Insertions & Deletions (Indels)
- **HV1 Poly-C Tract (16184–16193):** The standard rCRS sequence contains a T at position 16189 interrupting a poly-C stretch. A transition at 16189C creates an uninterrupted homopolymeric C-tract, which can cause DNA polymerase slipping and length heteroplasmy. Insertions in this region are designated as `16189.1C`, `16189.2C`.
- **HV2 Poly-C Tract (303–315):** The rCRS reference sequence contains a poly-C tract interrupted by a T at position 310. Insertions are placed after position 309 or 315 according to EMPOP right-alignment rules. Standard insertion designations include `309.1C`, `309.2C`, and `315.1C`.
- **Dinucleotide AC Repeat Region (522–523):** Deletions within the 522–523 AC repeat tract are designated as `522del` and `523del`. Insertions are placed at the 3' boundary as `524.1A` and `524.2C` (or collectively `524.1AC`).

---

### 3.3 EMPOP Alignment & Right-Alignment Normalization Algorithm
To ensure consistency across laboratories and prevent artificial profile discrepancies caused by different indel placements, FORENZA implements the EMPOP alignment algorithm. This module enforces 3'-most right-alignment on the light strand ($5' \to 3'$) for all insertion and deletion events.

| Sequence Strand Context | Unaligned / 5'-Shifted Raw Alignment | EMPOP Right-Aligned Standardized Call | Computational Rule Applied |
| :--- | :--- | :--- | :--- |
| **HV2 Poly-C Tract (303–315)** | Insertion placed at position 308.1C | Insertion assigned as **309.1C** | Shift insertion 3' to end of homopolymer block |
| **HV2 Extended C-Tract** | Dual insertions at 308.1C, 308.2C | Insertions assigned as **309.1C, 309.2C** | Cumulative 3' right-alignment shift |
| **HV3 AC Repeat (522–524)** | Insertion placed at position 522.1A | Insertion assigned as **524.1A** | Shift dinucleotide repeat to 3' terminus |

---

### 3.4 Heteroplasmy Modeling & Evidentiary Rules
Heteroplasmy describes the co-existence of multiple mitochondrial DNA genomes within an individual or sample.

#### Point Heteroplasmy (PHP)
Point heteroplasmy occurs when two different nucleotides are present at a single position, denoted using IUPAC ambiguity codes:
$$\text{PHP Codes: } R = \text{A/G}, \quad Y = \text{C/T}, \quad M = \text{A/C}, \quad K = \text{G/T}, \quad S = \text{G/C}, \quad W = \text{A/T}$$

- **Sanger Sequencing:** Analytical detection thresholds require a minor peak area or height $\ge 20\%$ of total peak height.
- **Next-Generation Sequencing (NGS):** Minor allele frequency (MAF) threshold of $\ge 10\%$ with a minimum coverage depth of 100x per strand is enforced.

#### Evidentiary Interpretation Rules for Heteroplasmy Matches
- **Shared Heteroplasmy:** If both a questioned sample and a reference sample exhibit the same point heteroplasmy (e.g., `16093Y`), this provides strong evidence of a shared maternal lineage.
- **Heteroplasmy vs. Homoplasmy:** If Sample A exhibits a point heteroplasmy (`16093Y`) and Sample B exhibits a homoplasmic variant (`16093C`), the sample pair cannot be excluded as originating from the same maternal lineage.
- **Exclusion Threshold:** A minimum of two or more homoplasmic point differences between questioned and reference samples is required for a definitive exclusion under SWGDAM guidelines.

---

### 3.5 EMPOP / PhyloTree Build 17 Haplogroup Classification Engine
Maternal haplogroups are assigned based on the hierarchical phylogenetic tree structure of PhyloTree (Build 17). The classification hierarchy branches from root macro-haplogroup `L0` into `L1-6`, giving rise to `L3`, which splits into non-African lineages `M` and `N`. `N` subsequently divides into `R` and non-`R` clades (`A`, `S`, `W`, `X`, `Y`), with `R` giving rise to major European and global haplogroups (`H`, `U`, `K`, `J`, `T`, `V`, `B`, `F`).

The prediction engine scores candidate haplogroups by evaluating diagnostic mutation motifs:
$$\text{Score}(\text{Hg}) = \sum_{m \in \text{Motif}(\text{Hg})} w_m \cdot I(m \in \text{Profile}) - \sum_{p \in \text{Private}} w_p - \sum_{b \in \text{BackMut}} w_b$$

| Macro-Haplogroup | Core Diagnostic Mutation Motif (rCRS Coordinates) | Primary Geographic Distribution |
| :--- | :--- | :--- |
| **L0** | 146C, 182C, 186C, 247G, 523del, 524del, 16093C, 16129C, 16223C, 16230G, 16278C | Southern/Eastern Africa |
| **L1** | 182C, 185T, 247G, 357G, 16126C, 16187C, 16223C, 16264T, 16278C | Central/West Africa |
| **L2** | 146C, 152C, 182C, 198C, 263G, 309.1C, 315.1C, 16129C, 16223C, 16278C, 16390C | Sub-Saharan Africa |
| **L3** | 182C, 263G, 315.1C, 750G, 16223C, 16311C | Africa, Ancestral to Out-of-Africa |
| **M** | 489C, 10400C, 14783T, 15043A, 16223C | South/East Asia, Indigenous Americas |
| **N** | 8701A, 9540C, 10398A, 10873T, 15301A | Eurasia, Oceania, Americas |
| **R** | 12705C, 16223C (ancestral reversion), 16183C, 16189C | West/South Eurasia, Americas |
| **H** | 2706A, 7028C, 263G, 315.1C (Lacks 16223C and 16519C in core H) | Western/Northern Europe |
| **U** | 11467G, 12308AG, 12372A, 16270T | Europe, North Africa, South Asia |
| **K** | 10550A, 11251G, 12308AG, 16224C, 16311C (Subclade of U8b) | Europe, Near East |
| **J** | 295C, 489C, 12612AG, 13708A, 16069T, 16126C | Europe, Middle East |
| **T** | 709A, 1888G, 4917G, 8697A, 10463C, 13368A, 14905A, 15607AG, 16126C, 16294T | Europe, Near East |
| **V** | 4580T, 15904C, 16298C | Western/Northern Europe |
| **W** | 195C, 204C, 207A, 1243A, 3505AG, 8994G, 11719A, 14305GA, 16292T | Eurasia, Europe |
| **X** | 153G, 195C, 225C, 1719A, 6221C, 12705C, 13966AG, 14470C, 16189C, 16278C | Near East, North America, Europe |
| **A** | 663G, 1736AG, 4248C, 4824AG, 8794T, 16290T, 16319GA | East Asia, Americas |
| **B** | 8281-8289del (9-bp deletion), 16183C, 16189C, 16217C | East Asia, Southeast Asia, Americas |
| **C** | 1438A, 4883T, 5178A, 13263AG, 14318C, 16223C, 16298C, 16327T | North/East Asia, Americas |
| **D** | 2092T, 3635GA, 4883T, 5178A, 16223C, 16362C | East Asia, Americas |

---

### 3.6 EMPOP Haplotype Match Probability & Likelihood Ratio

#### Database Frequency Bounds
For an observed mtDNA control region haplotype in an EMPOP database of size $N_{\text{EMPOP}}$, the upper 95% Clopper-Pearson bound $\hat{p}_{\text{mtDNA, upper}}$ for $k=0$ unobserved haplotypes is:
$$\hat{p}_{\text{mtDNA, upper}} = 1 - (0.05)^{\frac{1}{N_{\text{EMPOP}}+1}}$$

The corresponding Likelihood Ratio ($LR_{\text{mtDNA}}$) is:
$$LR_{\text{mtDNA}} = \frac{1}{\hat{p}_{\text{mtDNA, upper}}}$$

#### ENFSI 7-Tier Verbal Scale Mapping
| Likelihood Ratio ($LR$) Range | ENFSI Verbal Equivalent Standard Reporting Language |
| :--- | :--- |
| **$1 < LR < 10$** | Weak support for the proposition |
| **$10 \le LR < 100$** | Moderate support for the proposition |
| **$100 \le LR < 1,000$** | Moderately strong support for the proposition |
| **$1,000 \le LR < 10,000$** | Strong support for the proposition |
| **$10,000 \le LR < 100,000$** | Very strong support for the proposition |
| **$100,000 \le LR < 1,000,000$** | Extremely strong support for the proposition |
| **$LR \ge 1,000,000$** | Absolute/Overwhelming support for the proposition |

---

## 4. Multi-Omic Lineage Case Presets & Golden Benchmark Vectors

### 4.1 Benchmark LINEAGE-A (European Reference / EUR)
- **Population Ancestry:** European / Caucasian Reference (EUR)
- **Autosomal STR Summary:** Fully heterozygous 24-locus CODIS profile.
- **55-SNP Ancestry Vector:** $P(\text{EUR}) = 0.9842, P(\text{AFR}) = 0.0012, P(\text{EAS}) = 0.0081, P(\text{AMR}) = 0.0065$.
- **Y-STR 27-Locus Vector (Thermo Fisher Yfiler Plus):**
  `DYS19: 14`, `DYS389I: 13`, `DYS389II: 29`, `DYS390: 24`, `DYS391: 11`, `DYS392: 13`, `DYS393: 13`, `DYS385a/b: 11-14`, `DYS437: 15`, `DYS438: 12`, `DYS439: 12`, `DYS448: 19`, `DYS456: 15`, `DYS458: 17`, `DYS635: 23`, `YGATAH4: 12`, `DYS460: 11`, `DYS481: 22`, `DYS533: 12`, `DYS570: 17`, `DYS576: 18`, `DYS627: 15`, `DYS518: 38`, `DYS449: 30`, `DYF387S1a/b: 35-37`.
  - **Expected Y-DNA Haplogroup:** `R1b-M269`
  - **YHRD Database Match Count ($k$ in $N=35,000$):** $k = 0$
  - **$\hat{p}_{\text{Y-STR, upper}}$ (Clopper-Pearson 95%):** $8.56 \times 10^{-5}$
  - **$LR_{\text{Y-STR}}$:** $11,682$ (ENFSI: Very strong support)
- **mtDNA Control Region Haplotype Vector:** `263G, 315.1C, 750G, 16519C`.
  - **Expected mtDNA Haplogroup:** `H1`
  - **EMPOP Database Match Count ($k$ in $N=48,200$):** $k = 1,420$
  - **$\hat{p}_{\text{mtDNA, upper}}$ (Clopper-Pearson 95%):** $0.0304$
  - **$LR_{\text{mtDNA}}$:** $32.89$ (ENFSI: Moderate support)

---

### 4.2 Benchmark LINEAGE-B (African American Reference / AFR)
- **Population Ancestry:** African American / Sub-Saharan African Reference (AFR)
- **Autosomal STR Summary:** Highly polymorphic 24-locus CODIS profile.
- **55-SNP Ancestry Vector:** $P(\text{AFR}) = 0.9910, P(\text{EUR}) = 0.0042, P(\text{AMR}) = 0.0031, P(\text{EAS}) = 0.0017$.
- **Y-STR 27-Locus Vector (Thermo Fisher Yfiler Plus):**
  `DYS19: 15`, `DYS389I: 14`, `DYS389II: 31`, `DYS390: 21`, `DYS391: 10`, `DYS392: 11`, `DYS393: 15`, `DYS385a/b: 15-16`, `DYS437: 16`, `DYS438: 10`, `DYS439: 11`, `DYS448: 20`, `DYS456: 15`, `DYS458: 16`, `DYS635: 21`, `YGATAH4: 11`, `DYS460: 11`, `DYS481: 25`, `DYS533: 13`, `DYS570: 19`, `DYS576: 16`, `DYS627: 18`, `DYS518: 40`, `DYS449: 34`, `DYF387S1a/b: 38-39`.
  - **Expected Y-DNA Haplogroup:** `E1b1a-V38`
  - **YHRD Database Match Count ($k$ in $N=35,000$):** $k = 0$
  - **$\hat{p}_{\text{Y-STR, upper}}$ (Clopper-Pearson 95%):** $8.56 \times 10^{-5}$
  - **$LR_{\text{Y-STR}}$:** $11,682$ (ENFSI: Very strong support)
- **mtDNA Control Region Haplotype Vector:** `146C, 152C, 182C, 198C, 263G, 309.1C, 315.1C, 750G, 16129C, 16223C, 16278C, 16390C, 16519C`.
  - **Expected mtDNA Haplogroup:** `L2a1`
  - **EMPOP Database Match Count ($k$ in $N=48,200$):** $k = 12$
  - **$\hat{p}_{\text{mtDNA, upper}}$ (Clopper-Pearson 95%):** $0.000397$
  - **$LR_{\text{mtDNA}}$:** $2,518.8$ (ENFSI: Strong support)

---

### 4.3 Benchmark LINEAGE-C (Hispanic Reference / HIS with Amelogenin Y-Null)
- **Population Ancestry:** Hispanic Reference (HIS) exhibiting an Amelogenin Y-null mutation.
- **Autosomal & Sex Markers:** Amelogenin `(X, X)` paired with `DYS391 = 11` and full 27 Y-STR amplification, confirming male biological sex despite the Y-chromosomal Amelogenin gene deletion.
- **55-SNP Ancestry Vector:** $P(\text{AMR}) = 0.6420, P(\text{EUR}) = 0.3110, P(\text{AFR}) = 0.0310, P(\text{EAS}) = 0.0160$.
- **Y-STR 27-Locus Vector (Thermo Fisher Yfiler Plus):**
  `DYS19: 13`, `DYS389I: 13`, `DYS389II: 30`, `DYS390: 24`, `DYS391: 11`, `DYS392: 14`, `DYS393: 13`, `DYS385a/b: 12-13`, `DYS437: 14`, `DYS438: 10`, `DYS439: 12`, `DYS448: 20`, `DYS456: 15`, `DYS458: 17.2`, `DYS635: 23`, `YGATAH4: 11`, `DYS460: 10`, `DYS481: 22`, `DYS533: 11`, `DYS570: 16`, `DYS576: 17`, `DYS627: 20.2`, `DYS518: 36`, `DYS449: 28`, `DYF387S1a/b: 36-37`.
  - **Expected Y-DNA Haplogroup:** `Q-M3` (Native American patrilineal origin)
  - **YHRD Database Match Count ($k$ in $N=35,000$):** $k = 0$
  - **$\hat{p}_{\text{Y-STR, upper}}$ (Clopper-Pearson 95%):** $8.56 \times 10^{-5}$
  - **$LR_{\text{Y-STR}}$:** $11,682$ (ENFSI: Very strong support)
- **mtDNA Control Region Haplotype Vector:** `64T, 146C, 153G, 235G, 263G, 309.1C, 315.1C, 522del, 523del, 16111T, 16223C, 16290T, 16319GA, 16362C, 16519C`.
  - **Expected mtDNA Haplogroup:** `A2` (Native American matrilineal origin)
  - **EMPOP Database Match Count ($k$ in $N=48,200$):** $k = 3$
  - **$\hat{p}_{\text{mtDNA, upper}}$ (Clopper-Pearson 95%):** $0.000161$
  - **$LR_{\text{mtDNA}}$:** $6,211.1$ (ENFSI: Strong support)

---

### 4.4 Benchmark PEDIGREE-01 (Father-Son RM Y-STR Mutation Verification)
- **Case Context:** Direct father-son pair across 27 Y-STR loci. The profiles are identical across 26 loci, with a single 1-step repeat mutation observed at the rapidly mutating locus DYS570 (Father 17, Son 18).
- **Single-Step Transition Probability at DYS570 ($\mu_{\text{DYS570}} = 0.012$):**
  $$P(18 \mid 17, m=1) = \frac{1 \cdot (0.012) \cdot (1 - 0.012)^0}{2} = 0.0060$$
- **Unmutated Loci Transmission Probability ($26 \text{ Loci}$):**
  $$P(\text{Match} \mid m=1) = \prod_{l \neq \text{DYS570}} (1 - \mu_l)^1 \approx 0.8841$$
- **Combined Kinship Index ($\text{CPI}_{\text{Y-STR}}$):**
  $$\text{CPI}_{\text{Y-STR}} = \frac{0.0060 \times 0.8841}{P(H_{\text{Son}})} = \frac{0.005305}{8.56 \times 10^{-5}} = 61.97$$
- **Evidentiary Conclusion:** Single mutation at DYS570 does not exclude paternity. The likelihood ratio confirms paternal relationship ($H_1$) over an unobserved random male match ($H_2$) with moderate-to-strong support ($LR = 61.97$).

---

### 4.5 Benchmark MATERNAL-01 (Mother-Child Shared Point Heteroplasmy)
- **Case Context:** Questioned mother-child relationship. Direct sequencing of the mtDNA Control Region reveals a shared point heteroplasmy at nucleotide coordinate 16093 (Mother `16093Y` with ~45% T / ~55% C; Child `16093Y` with ~25% T / ~75% C), alongside standard mutations `263G, 315.1C, 16519C`.
- **Point Heteroplasmy Call:** IUPAC code `Y` (Cytosine / Thymine).
- **Interpretation Rule:** Shared point heteroplasmy at position `16093Y` provides strong evidence supporting a shared maternal lineage. Both profiles fall within Haplogroup `H`.
- **Match Probability Adjustment:** Reduces database frequency bound by a factor proportional to the rarity of the heteroplasmy event ($\approx 1.2 \times 10^{-3}$).
- **ENFSI Conclusion:** "The mitochondrial sequence data from the child and the alleged mother share a point heteroplasmy at position 16093Y alongside matching haplotype motifs. These results strongly support the proposition that the child shares a maternal lineage with the alleged mother rather than an unrelated individual."

---

## 5. Data Schemas, State Stores & Software Architecture

### 5.1 TypeScript Data Interfaces
```typescript
/**
 * FORENZA DNA & SNP Terminal - Lineage & Biocomputational Engine Schemas
 * Standardized data structure for Y-STR (27 Loci) and mtDNA D-Loop analysis.
 */

export type YStrDye = '6-FAM' | 'VIC' | 'NED' | 'TAZ' | 'SID' | 'LIZ';

export interface YStrLocusMetadata {
  locusName: string;
  cytogeneticBand: string;
  grch38Start: number;
  grch38End: number;
  repeatUnitBp: number;
  canonicalMotif: string;
  ceDye: YStrDye;
  ampliconRangeBp: [number, number];
  mutationRate: number;
  stepwiseParam: number;
  isRapidlyMutating: boolean;
  isMultiCopy: boolean;
}

export interface YStrLocusResult {
  locusName: string;
  alleles: string[]; // e.g., ["14"] or ["11", "14"] for DYS385a/b
  rfuValues: number[];
  peakHeightRatio?: number; // Calculated for multi-copy/heterozygous calls
  isMicrovariant: boolean;
  isOffLadder: boolean;
  flags?: string[];
}

export type YStrProfileMap = Record<string, YStrLocusResult>;

export interface YStrHaplogroupPrediction {
  predictedHaplogroup: string; // e.g., "R1b-M269"
  confidenceScore: number; // 0.0 - 1.0
  bayesianPosteriors: Record<string, number>;
  distanceToModal: number;
  primarySnpMarker: string;
}

export interface MtDnaMutation {
  position: number; // e.g., 16189
  refBase: string; // e.g., "T"
  observedBase: string; // e.g., "C" or IUPAC "Y"
  mutationType: 'transition' | 'transversion' | 'insertion' | 'deletion' | 'heteroplasmy';
  formattedNotation: string; // e.g., "16189.1C", "309.1C", "16093Y"
  heteroplasmyFrequency?: number; // e.g., 0.25 for 25% minor allele
}

export interface HeteroplasmyCall {
  position: number;
  iupacCode: 'R' | 'Y' | 'M' | 'K' | 'S' | 'W';
  majorBase: 'A' | 'C' | 'G' | 'T';
  minorBase: 'A' | 'C' | 'G' | 'T';
  minorAlleleFrequency: number;
  platform: 'Sanger' | 'NGS';
}

export interface MtDnaHaplotypeMap {
  rangeSequenced: string; // e.g., "16024-576"
  mutationsVsRcrs: MtDnaMutation[];
  heteroplasmyCalls: HeteroplasmyCall[];
  rawLightStrandSequence?: string;
}

export interface MtDnaHaplogroupResult {
  predictedHaplogroup: string; // e.g., "H1", "L2a1"
  macroHaplogroup: string; // e.g., "H", "L2"
  phyloTreeBuild: number; // e.g., 17
  definingMotifMatches: number;
  missingDiagnosticPositions: number[];
  backMutations: string[];
}

export interface LineageAnalysisReport {
  caseId: string;
  sampleId: string;
  timestamp: string;
  yStrProfile?: {
    loci: YStrProfileMap;
    haplogroup: YStrHaplogroupPrediction;
    yhrdMatchCount: number;
    yhrdDatabaseSize: number;
    matchProbabilityUpper: number;
    likelihoodRatio: number;
  };
  mtDnaProfile?: {
    haplotype: MtDnaHaplotypeMap;
    haplogroup: MtDnaHaplogroupResult;
    empopMatchCount: number;
    empopDatabaseSize: number;
    matchProbabilityUpper: number;
    likelihoodRatio: number;
    enfsiVerbalScale: string;
  };
}
```

---

### 5.2 Python Pydantic v2 Schemas
```python
"""
FORENZA Forensic Evidence Operating System - Lineage Engine PyBackend Models
Pydantic v2 Data Validation Schemas for Y-STR & mtDNA Engine Integration.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class YStrDyeEnum(str, Enum):
    FAM = "6-FAM"
    VIC = "VIC"
    NED = "NED"
    TAZ = "TAZ"
    SID = "SID"
    LIZ = "LIZ"


class MutationTypeEnum(str, Enum):
    TRANSITION = "transition"
    TRANSVERSION = "transversion"
    INSERTION = "insertion"
    DELETION = "deletion"
    HETEROPLASMY = "heteroplasmy"


class YStrLocusResultSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus_name: str = Field(..., description="Y-STR locus identifier")
    alleles: List[str] = Field(..., description="Observed allele designations")
    rfu_values: List[float] = Field(..., description="Peak heights in RFU")
    peak_height_ratio: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_microvariant: bool = Field(default=False)
    is_off_ladder: bool = Field(default=False)
    flags: List[str] = Field(default_factory=list)


class YStrHaplogroupPredictionSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    predicted_haplogroup: str = Field(..., example="R1b-M269")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    bayesian_posteriors: Dict[str, float]
    distance_to_modal: float
    primary_snp_marker: str


class MtDnaMutationSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    position: int = Field(..., ge=1, le=16569)
    ref_base: str = Field(..., regex="^[ACGT]$")
    observed_base: str = Field(..., regex="^[ACGTRYMKSW]$")
    mutation_type: MutationTypeEnum
    formatted_notation: str = Field(..., example="16189.1C")
    heteroplasmy_frequency: Optional[float] = Field(None, ge=0.0, le=1.0)


class HeteroplasmyCallSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    position: int = Field(..., ge=1, le=16569)
    iupac_code: str = Field(..., regex="^[RYMKSW]$")
    major_base: str = Field(..., regex="^[ACGT]$")
    minor_base: str = Field(..., regex="^[ACGT]$")
    minor_allele_frequency: float = Field(..., ge=0.05, le=0.50)
    platform: str = Field(..., example="NGS")


class MtDnaHaplogroupResultSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    predicted_haplogroup: str = Field(..., example="H1")
    macro_haplogroup: str = Field(..., example="H")
    phylotree_build: int = Field(default=17)
    defining_motif_matches: int
    missing_diagnostic_positions: List[int] = Field(default_factory=list)
    back_mutations: List[str] = Field(default_factory=list)


class LineageAnalysisReportSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    case_id: str
    sample_id: str
    timestamp: str
    y_str_profile: Optional[Dict[str, YStrLocusResultSchema]] = None
    y_str_haplogroup: Optional[YStrHaplogroupPredictionSchema] = None
    yhrd_match_count: Optional[int] = Field(None, ge=0)
    yhrd_lr: Optional[float] = Field(None, ge=0.0)
    mtdna_mutations: Optional[List[MtDnaMutationSchema]] = None
    mtdna_haplogroup: Optional[MtDnaHaplogroupResultSchema] = None
    empop_match_count: Optional[int] = Field(None, ge=0)
    empop_lr: Optional[float] = Field(None, ge=0.0)
    enfsi_verbal_scale: Optional[str] = None
```

---

## 6. UI/UX & Terminal CLI Integration Design

### 6.1 DNA Profile Inspector Modal (`DnaProfileInspectorModal.tsx`) Tab Extensions
The FORENZA React inspection interface incorporates two dedicated diagnostic tabs:

1. **`Y-STR (27 Loci)` Tab Layout & Interaction Specifications:**
   - **Interactive Locus Matrix:** A 27-row data grid displaying locus name, dye channel color code, GRCh38 location, peak height (RFU), and called allele(s).
   - **RM Y-STR Visual Badging:** The 7 Rapidly Mutating loci (`DYS570`, `DYS576`, `DYS627`, `DYS518`, `DYS449`, `DYF387S1a/b`) display high-contrast amber tags with hover tooltips indicating locus-specific mutation rates ($\mu \ge 1.0 \times 10^{-2}$).
   - **Multi-Copy Allele Editors:** Specialized allele entry cells for `DYS385a/b` and `DYF387S1a/b` that dynamically calculate the Peak Height Ratio ($\text{PHR} = \frac{\min(\text{RFU}_1, \text{RFU}_2)}{\max(\text{RFU}_1, \text{RFU}_2)}$) and flag potential mixture or duplication events if $\text{PHR} < 0.50$.
   - **Y-DNA Haplogroup Card:** Displays the predicted paternal lineage (e.g., `R1b-M269`), Bayesian posterior probability bar, modal genetic distance metric, and an interactive lineage branch diagram.
   - **YHRD RMP / LR Summary Bar:** Live calculation bar presenting the database match count ($k$), Clopper-Pearson 95% upper bound ($\hat{p}_{\text{upper}}$), Discrete Laplace frequency estimate, and Likelihood Ratio ($LR_{\text{Y-STR}}$).

2. **`mtDNA (Control Region)` Tab Layout & Interaction Specifications:**
   - **Interactive HV1/HV2/HV3 Sequence Grid:** Horizontal sequence viewer highlighting HV1 (16024–16365), HV2 (73–340), and HV3 (438–574) domains with region boundary markers.
   - **Poly-C Tract & Homopolymer Toggle:** Visual warning indicators for length heteroplasmy regions around positions 16189 and 309/315.
   - **Heteroplasmy Editor Controls:** Dedicated UI toggles for assigning IUPAC ambiguity codes (`R`, `Y`, `M`, `K`, `S`, `W`), specifying minor allele fractions (NGS $\ge 10\%$, Sanger $\ge 20\%$), and logging single-site point heteroplasmy.
   - **Alignment Normalization Viewer:** Dual alignment track showing raw sequence alignment vs EMPOP 3'-right-aligned normalized calls to prevent synthetic match errors.
   - **Maternal Haplogroup & EMPOP Summary Card:** Displays the assigned PhyloTree Build 17 haplogroup (e.g., `H1`), diagnostic motif match stats, database match bound ($\hat{p}_{\text{mtDNA, upper}}$), calculated $LR_{\text{mtDNA}}$, and the corresponding ENFSI verbal scale statement.

---

### 6.2 CLI Shell Command Architecture
The FORENZA Command Line Interface (CLI) provides interactive terminal commands for lineage calculations and multi-omic data processing:
- `forenza ystr list --sample <sample_id>`: Lists all 27 Y-STR allele calls, peak heights, and flags for a given sample.
- `forenza ystr calc --sample <sample_id> --database yhrd_v60 --theta 0.02`: Computes Clopper-Pearson bounds, Brenner subpopulation corrections, and Discrete Laplace frequency estimates.
- `forenza ystr haplogroup --sample <sample_id> --engine bayesian`: Runs Bayesian haplogroup prediction on the 27-locus Y-STR profile.
- `forenza ystr mix --sample <sample_id> --phr-threshold 0.50`: Deconvolutes male mixtures and calculates $N_{\text{male}}$ across single- and multi-copy loci.
- `forenza mtdna list --sample <sample_id>`: Displays mitochondrial Control Region variants vs rCRS.
- `forenza mtdna align --sample <sample_id> --reference rcrs --right-align`: Enforces EMPOP 3'-most right-alignment normalization on light-strand sequences.
- `forenza mtdna haplogroup --sample <sample_id> --phylotree b17`: Classifies maternal haplogroups based on PhyloTree Build 17 motifs.
- `forenza mtdna heteroplasmy --sample <sample_id> --platform ngs --min-maf 0.10`: Filters and reports point and length heteroplasmy calls.
- `forenza lineage compare --sample-a <id_1> --sample-b <id_2> --mode kinship --meioses 1`: Computes SMM likelihood ratios for comparative patrilineal or matrilineal kinship testing.
- `forenza benchmark lineage --preset <a|b|c> --export-json <output_path>`: Generates complete ground-truth benchmark profiles across all genetic systems.