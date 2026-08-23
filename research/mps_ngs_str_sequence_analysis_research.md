# FORENZA Research Specification: Massively Parallel Sequencing (MPS/NGS) STR Analysis & Sequence-Level Biocomputation

**Document ID:** `FORENZA-RESEARCH-MPS-STR-01`  
**Standard Compliance:** ISO/IEC 17025:2017 • ISFG Commission on STR Sequence Nomenclature (2016, 2021) • SWGDAM NGS Guidelines  
**Source Literature:**  
- *Scientific Reports* (2021) 11:3485 — *Sequence-based analysis of 25 autosomal STR loci including SE33 using an in-house massively parallel sequencing (MPS) panel* (doi:10.1038/s41598-021-82814-z)  
- Gettings et al. (2016, 2018) Forensic STR Sequence Structure Guide v5  
- Borsuk et al. (2018) *SE33 sequence variation and flanking region polymorphisms*  
- Parson et al. (2016) *ISFG recommendations for STR sequence nomenclature*  

---

## 1. Executive Summary & The Sequence-Level Paradigm Shift

For three decades, forensic DNA profiling has relied exclusively on **Capillary Electrophoresis (CE)**, which measures short tandem repeat (STR) variation based strictly on **amplicon length (electrophoretic mobility)**. However, length-based measurement creates an analytical blind spot: alleles of identical length (same base pair size) often contain distinct internal repeat motifs, sequence interruptions, or flanking region single nucleotide polymorphisms (SNPs) and insertion/deletions (indels).

**Massively Parallel Sequencing (MPS)**, also known as Next-Generation Sequencing (NGS), directly sequences each DNA molecule at single-nucleotide resolution. This technology expands the biocomputational capabilities of forensic intelligence in several critical dimensions:

1. **Massive Allele Expansion (Isoallele Deconvolution):** Across 25 autosomal STR loci in 4 major populations ($N=350$), sequence-based MPS increases the total observed allele count from **332 (CE length)** to **725 (MPS sequence)** — a **2.18-fold overall expansion**.
2. **SE33 Hyper-Polymorphic Sequence Architecture:** In the highly polymorphic `SE33` locus, sequence analysis uncovers **129 additional unique isoalleles**, yielding a **4.15-fold allele increase** (from 41 CE length alleles to 170 MPS sequence alleles) and the highest expected heterozygosity in the human genome ($H_{\text{exp}} = 97.3\%$).
3. **Flanking Region Mutations as Linkage Anchors:** Identification of 31 flanking region SNPs and indels across 9 loci, explaining electrophoretic anomalies such as 4-bp flanking deletions (rs369314007 `[TTTT/-]`, rs1371483225 `[TCTT/-]`) and African-specific primer binding site mutations (vWA rs771794429).
4. **Mixture Deconvolution & Low-Template Sensitivity:** Isoalleles separate overlapping contributors in 2-, 3-, and 4-person DNA mixtures without mathematical ambiguity, substantially reducing false exclusions and elevating Likelihood Ratios ($LR$).
5. **Universal Backward Compatibility:** Every MPS sequence string can be deterministically converted into its corresponding CE length-based integer or microvariant allele call, preserving complete interoperability with legacy national DNA databases (CODIS, NDIS, ENFSI, Interpol).

---

## 2. 25-Autosomal STR Locus Registry & Multiplex Structure

The FORENZA MPS-STR engine standardizes the 28-marker multiplex (25 Autosomal STRs + 3 Sex Typing Markers):

| Locus Name | Chromosomal Location | Repeat Type | CE Amplicon Range (bp) | In-House MPS Amplicon Range (bp) | CE Length Alleles ($N=350$) | MPS Sequence Alleles ($N=350$) | Fold Increase | Sequence Heterozygosity ($H_{\text{exp}}$) |
|---|---|---|---|---|---|---|---|---|
| **D1S1656** | 1q42.2 | Compound / Micro | 120–185 | 120–185 | 15 | 29 | $1.93\times$ | 0.898 |
| **TPOX** | 2p25.3 | Simple | 220–250 | 140–180 | 7 | 7 | $1.00\times$ | 0.690 |
| **D2S441** | 2p14 | Compound | 75–125 | 90–135 | 11 | 18 | $1.64\times$ | 0.782 |
| **D2S1338** | 2q35 | Compound | 290–360 | 140–210 | 12 | 44 | $3.67\times$ | 0.924 |
| **D3S1358** | 3p21.31 | Compound | 110–145 | 110–150 | 8 | 21 | $2.63\times$ | 0.916 |
| **FGA** | 4q31.3 | Compound / Complex | 215–350 | 170–258 | 20 | 38 | $1.90\times$ | 0.884 |
| **D4S2408** | 4q35.2 | Simple | 150–190 | 130–170 | 9 | 12 | $1.33\times$ | 0.795 |
| **D5S818** | 5q23.2 | Simple / Flanking | 135–175 | 120–165 | 9 | 15 | $1.67\times$ | 0.778 |
| **CSF1PO** | 5q33.1 | Simple | 290–335 | 150–195 | 9 | 11 | $1.22\times$ | 0.745 |
| **D6S1043** | 6q15 | Compound | 280–340 | 140–205 | 16 | 28 | $1.75\times$ | 0.875 |
| **SE33** | 6q14.2 | Complex / Micro | 307–438 | 120–258 | 41 | 170 | $\mathbf{4.15\times}$ | $\mathbf{0.973}$ |
| **D7S820** | 7q21.11 | Simple / Flanking | 215–255 | 130–175 | 10 | 25 | $2.50\times$ | 0.842 |
| **D8S1179** | 8q24.13 | Compound | 125–170 | 130–180 | 11 | 22 | $2.00\times$ | 0.865 |
| **D10S1248** | 10q26.3 | Simple | 85–130 | 100–145 | 8 | 8 | $1.00\times$ | 0.768 |
| **TH01** | 11p15.5 | Simple / Micro | 165–200 | 120–160 | 7 | 7 | $1.00\times$ | 0.742 |
| **vWA** | 12p13.31 | Compound / Flanking | 155–200 | 130–180 | 11 | 24 | $2.18\times$ | 0.835 |
| **D12S391** | 12p13.2 | Compound / Complex | 205–265 | 125–185 | 16 | 54 | $3.38\times$ | 0.902 |
| **D13S317** | 13q31.1 | Simple / Flanking | 195–240 | 120–170 | 8 | 21 | $2.63\times$ | 0.825 |
| **Penta E** | 15q26.2 | Simple | 375–475 | 160–250 | 18 | 23 | $1.28\times$ | 0.923 |
| **D16S539** | 16q24.1 | Simple / Flanking | 250–295 | 130–180 | 8 | 19 | $2.38\times$ | 0.812 |
| **D18S51** | 18q21.33 | Simple | 260–345 | 140–225 | 19 | 27 | $1.42\times$ | 0.895 |
| **D19S433** | 19q12 | Compound / Micro | 100–150 | 110–160 | 15 | 24 | $1.60\times$ | 0.840 |
| **D21S11** | 21q21.1 | Complex / Micro | 190–255 | 140–210 | 21 | 67 | $3.19\times$ | 0.930 |
| **Penta D** | 21q22.3 | Simple / Flanking | 150–220 | 130–200 | 13 | 20 | $1.54\times$ | 0.865 |
| **D22S1045** | 22q12.3 | Simple | 85–130 | 95–140 | 11 | 11 | $1.00\times$ | 0.780 |
| **Amelogenin** | Xp22.2 / Yp11.2 | Sex Marker (6 bp Indel) | 106 / 112 | 106 / 112 | 2 | 3 (Y-rs375383821) | $1.50\times$ | — |
| **DYS391** | Yq11.221 | Y-STR Simple | 140–170 | 120–160 | 6 | 6 | $1.00\times$ | — |
| **Y-M175** | Yq11.223 | East Asian Y-SNP | — | 110 | 2 | 2 | $1.00\times$ | — |
| **TOTALS** | — | — | — | — | **332** | **725** | $\mathbf{2.18\times}$ | — |

---

## 3. ISFG Standard Sequence String Grammar & Nomenclature

FORENZA implements the **ISFG (International Society for Forensic Genetics)** sequence-based nomenclature. STR alleles are represented as formal structural strings with explicit 5' flanking, repeat motif, and 3' flanking blocks.

### Formal Extended Backus-Naur Form (EBNF) Grammar:

```ebnf
SequenceAllele    ::= [Flanking5Prime "_"] RepeatRegion ["_" Flanking3Prime]
Flanking5Prime    ::= VariantList
Flanking3Prime    ::= VariantList
VariantList       ::= Variant {";" Variant}
Variant           ::= rsID "[" Ref ">" Alt "]" | rsID "[" ("del" | "ins") Seq "]"
RepeatRegion      ::= MotifBlock {" " MotifBlock}
MotifBlock        ::= "[" Nucleotides "]" RepeatCount
Nucleotides       ::= ("A" | "C" | "G" | "T")+
RepeatCount       ::= Integer | Float
```

### Representative Structural Examples:

1. **D3S1358 (Allele 16):**
   - CE Length Call: `16`
   - Sequence Call 1: `[TCTA]1 [TCTG]3 [TCTA]12` (Common Caucasian/Korean)
   - Sequence Call 2: `[TCTA]1 [TCTG]2 [TCTA]13` (African-American Variant)
   - Sequence Call 3: `[TCTA]2 [TCTG]3 [TCTA]11` (Rare Isoallele)
2. **D21S11 (Allele 30):**
   - CE Length Call: `30`
   - Sequence Call 1: `[TCTA]5 [TCTG]6 [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCCATA [TCTA]10`
   - Sequence Call 2: `[TCTA]6 [TCTG]5 [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCCATA [TCTA]10`
   - Sequence Call 3: `[TCTA]4 [TCTG]7 [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCCATA [TCTA]10`
3. **vWA (Allele 17 with Flanking SNP):**
   - CE Length Call: `17`
   - Sequence Call: `[TCTA]11 [TCTG]4 [TCTA]2_rs771794429[G>A]`

---

## 4. Deep-Dive: SE33 Complex Structural Architecture

`SE33` (ACTBP2) is located on chromosome 6q14.2. Its repeat structure consists of complex tetranucleotide `[CTTT]` blocks interrupted by `TT`, `CT`, or `CTTC` transitions.

### Repeat Structure Progression by Size Class:

1. **Small Alleles (Integer Size, e.g. Allele 14 to Allele 20):**
   - Dominant Motif: Simple `[CTTT]n` with single terminal or internal substitution.
   - Example (Allele 18): `CTTC [CTTT]17` or `[CTTT]18`.
2. **Large Alleles (0.2 Microvariants, e.g. Allele 22.2 to Allele 38.2):**
   - Dominant Motif: Bipartite `[CTTT]n TT [CTTT]m` or `[CTTT]n CT [CTTT]m`.
   - Example (Allele 27.2): `CTTC [CTTT]8 TT [CTTT]18` vs `CTTC [CTTT]10 TT [CTTT]16` vs `[CTTT]12 TT [CTTT]15`.

### 7 Flanking Region Polymorphisms in SE33:

| Variant rsID | Mutation Type | Position Relative to Repeat | Affected Alleles | Population Bias |
|---|---|---|---|---|
| **rs9362477** | C > T (SNP) | 5' Flanking (-42 bp) | Alleles 12 to 34 | Global (48.5% frequency) |
| **rs536914220** | C > T (SNP) | 5' Flanking (-18 bp) | Alleles 16.2 to 28.2 | Korean / East Asian |
| **rs1429028170** | C > T (SNP) | 5' Flanking (-8 bp) | Alleles 24.2, 26.2 | African-American |
| **rs1391198277** | delTTCT (4 bp Del) | 3' Flanking (+14 bp) | Alleles 19.2 to 31.2 | Global |
| **rs1452632862** | delT (1 bp Del) | 3' Flanking (+28 bp) | Alleles 15 to 22.2 | Caucasian / Hispanic |
| **rs151261950** | delCTTT (4 bp Del) | 3' Flanking (+45 bp) | Alleles 20.2 to 29.2 | African-American |
| **rs1277875566** | T > C (SNP) | 3' Flanking (+62 bp) | Alleles 27.2 to 36.2 | Global |

### 4-bp Deletions Causing CE vs MPS Discordance (rs369314007 & rs1371483225):

Between legacy CE primers (GlobalFiler: 307–438 bp; Euplex-13: 171–321 bp) and optimized short-amplicon MPS primers (120–258 bp), two 4-bp deletions reside in the 3' flanking region:
1. **rs369314007 (`[TTTT/-]`):** 4 bp deleted in MPS amplicon $\implies$ MPS sequence is assigned 1 repeat larger (e.g. CE allele 16 appears as MPS allele 17).
2. **rs1371483225 (`[TCTT/-]`):** 4 bp deleted in MPS amplicon $\implies$ MPS sequence is assigned 1 repeat larger (e.g. CE allele 23.2 appears as MPS allele 24.2).

When both deletions occur simultaneously in a heterozygote sample, both alleles shift by exactly +1 repeat. Compensating for these two flanking deletions yields **100.00% true biological concordance**.

---

## 5. 4-Population Empirical Allele Frequency Matrices ($N=350$)

FORENZA ingests calibrated sequence-based frequency matrices across 4 global populations:

1. **African-American (AfAm, $N=83$):** 166 chromosomes. High sequence diversity at D2S1338, D3S1358, and SE33. Specific presence of vWA flanking SNP rs771794429.
2. **Caucasian (Cauc, $N=82$):** 164 chromosomes. High D12S391 sequence polymorphism; dominant `[TCTA]n [TCTG]m` D3S1358 structures.
3. **Hispanic (Hisp, $N=82$):** 164 chromosomes. Distinct D2S441 motif frequencies (`[TCTA]n TCTG TCTA`).
4. **Korean (Kor, $N=103$):** 206 chromosomes. Elevated SE33 repeat region variation rate; specific rs536914220 5' flanking SNP.

---

## 6. Forensic Biostatistics: Power of Discrimination & Kinship Gain

### 6.1 Power of Discrimination ($PD$) Formulation

For locus $l$ with $K$ sequence-based alleles having frequencies $p_1, p_2, \dots, p_K$:

$$PD_l = 1 - \sum_{i=1}^K p_i^4 - \sum_{i=1}^{K-1} \sum_{j=i+1}^K 4 p_i^2 p_j^2 = 1 - P M_l$$

Where $P M_l$ is the Match Probability. Across all 25 loci:

$$PD_{\text{combined}} = 1 - \prod_{l=1}^{25} P M_l \approx 1 - 10^{-32} \quad (\text{vs } 1 - 10^{-24} \text{ in CE})$$

### 6.2 Expected Heterozygosity ($H_{\text{exp}}$)

$$H_{\text{exp}} = 1 - \sum_{i=1}^K p_i^2$$

In MPS, 7 loci achieve $H_{\text{exp}} > 0.90$ (SE33: 0.973, D21S11: 0.930, D2S1338: 0.924, Penta E: 0.923, D3S1358: 0.916, D12S391: 0.902, D1S1656: 0.898), compared to only 2 loci in CE.

### 6.3 Syntenic Linkage & Genetic Recombination (D6S1043 – SE33)

- Physical Chromosomal Distance: $3.46\text{ Mb}$ on chromosome 6q.
- Recombination Fraction: $\theta = 0.0440$.
- **Kinship Invariant:** In parentage/kinship likelihood calculations, D6S1043 and SE33 must not be multiplied as independent unlinked loci without applying the Kosambi/Haldane linkage disequilibrium transition matrix. If linkage is unmodeled, the engine must flag a warning and default to evaluating only the more informative locus (SE33).

---

## 7. Golden Benchmark Vectors (`VECTOR_MPS_01` to `VECTOR_MPS_04`)

### `VECTOR_MPS_01` — SE33 Bimodal Isoallele Deconvolution & Flanking SNP
- **Sample ID:** `MPS_GOLDEN_01_SE33_CAUCASIAN`
- **CE Length Profile:** `SE33 18 / 27.2`
- **MPS Sequence Profile:**
  - Allele A: `CTTC [CTTT]17_rs9362477[C>T]` (Length 18, Sequence Tag `18a`)
  - Allele B: `CTTC [CTTT]10 TT [CTTT]16_rs1277875566[T>C]` (Length 27.2, Sequence Tag `27.2c`)
- **Calculated Properties:**
  - Length-based frequency: $p_{\text{CE}}(18)=0.074, p_{\text{CE}}(27.2)=0.091 \implies LR_{\text{CE}} = \frac{1}{2 \cdot 0.074 \cdot 0.091} = 74.2$
  - Sequence-based frequency: $p_{\text{MPS}}(18a)=0.018, p_{\text{MPS}}(27.2c)=0.009 \implies LR_{\text{MPS}} = \frac{1}{2 \cdot 0.018 \cdot 0.009} = 3,086.4$
  - **Information Gain ($LR_{\text{MPS}} / LR_{\text{CE}}$):** $\mathbf{41.6\times}$ boost in single-locus probative power.

### `VECTOR_MPS_02` — SE33 4-bp Flanking Deletion Resolution (rs369314007)
- **Sample ID:** `MPS_GOLDEN_02_SE33_DISCORDANCE_RESOLVER`
- **CE Apparent Call:** `16 / 23.2`
- **MPS Raw Alignment Call:** `17 / 24.2`
- **Underlying Flanking Variant:** `rs369314007[delTTTT]` on 16-allele, `rs1371483225[delTCTT]` on 23.2-allele.
- **Engine Resolution:** Flag `FLANKING_DELETION_DETECTED`, map sequence coordinates to CE standard `16` and `23.2` with full sequence preservation. Concordance status: `100% RECONCILED`.

### `VECTOR_MPS_03` — D3S1358 & D21S11 3-Person Mixture Isoallele Separation
- **Sample ID:** `MPS_GOLDEN_03_MIXTURE_ISOALLELE`
- **Locus D3S1358:**
  - CE Profile: Allele `15` (Huge peak), Allele `16` (Huge peak) $\implies$ Inconclusive 2-allele mask.
  - MPS Profile:
    - Contributor 1 (50%): `[TCTA]1 [TCTG]3 [TCTA]11` (15a) / `[TCTA]1 [TCTG]3 [TCTA]12` (16a)
    - Contributor 2 (30%): `[TCTA]1 [TCTG]2 [TCTA]12` (15b) / `[TCTA]1 [TCTG]4 [TCTA]11` (16b)
    - Contributor 3 (20%): `[TCTA]2 [TCTG]3 [TCTA]10` (15c) / `[TCTA]1 [TCTG]3 [TCTA]12` (16a)
  - Result: 6 distinct sequence alleles recovered from 2 length peaks. Total mixture Likelihood Ratio elevated by $>10^6$.

### `VECTOR_MPS_04` — vWA African Primer Binding Site Dropout Mask (rs771794429)
- **Sample ID:** `MPS_GOLDEN_04_VWA_AFRICAN_FLANKING`
- **Sample Type:** African-American Buccal DNA
- **CE Length Profile:** `vWA 14 / 15` (Heterozygous)
- **Raw MPS Profile:** `vWA 14` (Apparent False Homozygote due to dropout of 15)
- **Engine Diagnostics:** Detects rs771794429 [G>A] in primer binding footprint, applies stochastic dropout correction $P(D \mid \text{SNP}) = 1.0$, restores heterozygous genotype state `vWA 14 / [15_rs771794429]`, flags quality assurance tag `AFRICAN_VWA_MUTATION_RESCUED`.

---

## 8. 5 Mandatory ISO/IEC 17025 Edge-Case Tests

1. **`EC-MPS-01` (Backward CE Translation Invariant):** Every valid MPS sequence across all 25 loci must translate to the exact integer/microvariant length call ($|\Delta L| = 0$).
2. **`EC-MPS-02` (Simplex Normalization Invariant):** Sum of sequence-based allele frequencies per locus in each of the 4 population matrices must equal $1.000000 \pm 10^{-6}$.
3. **`EC-MPS-03` (4-bp Flanking Deletion Auto-Reconciliation):** Automated detection of rs369314007 and rs1371483225 in SE33 without false allele calling.
4. **`EC-MPS-04` (D6S1043 – SE33 Linkage Warning):** Recombination fraction $\theta = 0.0440$ constraint validation in kinship inference.
5. **`EC-MPS-05` (Sub-Threshold Analytical Cutoff & Stutter Discrimination):** Sequence reads below Analytical Threshold ($\text{AT} = 5.0\%$ of locus total reads) filtered, with forward/reverse isometric PCR stutter subtraction.
