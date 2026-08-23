# Machine Learning for Forensic STR Calling, Artifact Filtering & ISFG Massively Parallel Sequencing Minimal Nomenclature

**Document ID:** `FORENZA-RESEARCH-ML-STR-01`  
**Standard Compliance:** ISFG DNA Commission (2016, 2021) • SWGDAM (2020) • Forensic Science International: Genetics (Parson et al., Barash et al.)  
**Mathematical & Computational Classification:** Random Forest / Gradient Boosted Tree Ensembles • Gini Impurity • Shannon Entropy • 24-Dimensional Peak Morphology Vector Space • 3-Tier ISFG Hierarchical Nomenclature  

---

## 1. Executive Scientific Foundation

### 1.1 Academic References & Scope
This specification synthesizes the foundational guidelines and machine learning breakthroughs in forensic STR allele calling and massively parallel sequencing (MPS):
1. **ISFG DNA Commission Guidelines:** Parson W. et al. *"Massively parallel sequencing of forensic STRs: Considerations of the DNA commission of the International Society for Forensic Genetics (ISFG) on minimal nomenclature requirements"* **Forensic Science International: Genetics** (2016) 22:54–63 ([doi:10.1016/j.fsigen.2016.01.009](https://doi.org/10.1016/j.fsigen.2016.01.009)).
2. **Machine Learning in Forensic STR Profiling:** Barash M. et al. *"Machine learning in forensic genetics: Review and future perspectives"* **Forensic Science International: Genetics** (2023).
3. **Fragsifier Architecture:** Random Forest ensemble classification for repeat pattern recognition, isometric artifact discrimination, and sub-threshold noise filtering.

---

## 2. The 3-Tier ISFG Hierarchical Information Framework

Forensic STR sequence data must be stored, processed, and reported across three strictly defined hierarchical levels to guarantee 100% backward compatibility with legacy capillary electrophoresis (CE) national databases (CODIS, NDIS, NDNAD, Interpol):

```
+---------------------------------------------------------------------------------------------------+
| LEVEL 1: SEQUENCE (TEXT STRING)                                                                   |
| Raw FASTA/FASTQ nucleotide sequence capturing full repeat region + flanking boundaries            |
| Example: TCTATCTATCTATCTATCTATCTATCTATCTATCTATCTATCTA [11 repeats of TCTA]                      |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
| LEVEL 2: SEQUENCE ALIGNMENT (REFERENCE MAPPING)                                                   |
| Aligned against standard human genome reference assembly (GRCh38 / hg38), top-strand orientation  |
| Enforces strict anchor definitions, 5' / 3' flanking boundaries, and indel coordinate rules       |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
| LEVEL 3: STR ALLELE NOMENCLATURE & CE TRANSLATION                                                 |
| Compact bracketed repeat representation with rsID flanking annotations                            |
| Example: [TCTA]11 [TCTG]4 [TCTA]2_rs771794429[G>A]  ───(Deterministic Translation)───►  CE: 17.0  |
+---------------------------------------------------------------------------------------------------+
```

### 2.1 Formal EBNF String Grammar for ISFG Level 3
```ebnf
ISFG_Sequence_String  ::= [ Flanking5Prime "_" ] MotifBlockList [ "_" Flanking3Prime ]
MotifBlockList        ::= MotifBlock { (" " | "-") MotifBlock }
MotifBlock            ::= BracketedMotif | NonCanonicalSpacer
BracketedMotif        ::= "[" NucleotideSequence "]" RepeatCount
NonCanonicalSpacer    ::= NucleotideSequence
RepeatCount           ::= Integer
Flanking5Prime        ::= VariantList
Flanking3Prime        ::= VariantList
VariantList           ::= Variant { "," Variant }
Variant               ::= rsID "[" MutationDescription "]"
MutationDescription  ::= ( RefBase ">" AltBase ) | ( "del" DeletedSequence ) | ( "ins" InsertedSequence )
```

---

## 3. 24-Dimensional Machine Learning Feature Space ($\mathbf{x} \in \mathbb{R}^{24}$)

To distinguish true biological alleles from stutter slips, incomplete adenylation, spectral pull-up, and baseline stochastic noise, FORENZA maps every electropherogram (EPG) peak and MPS read cluster to a 24-dimensional feature vector $\mathbf{x}$:

$$\mathbf{x} = \left[ x_1, x_2, \dots, x_{24} \right]^T \in \mathbb{R}^{24}$$

### 3.1 Peak Morphology & Signal Kinetics ($x_1 - x_6$)
1. **$x_1$ (Peak Height $h$):** Relative Fluorescence Units (RFU) or Read Depth ($DP$).
2. **$x_2$ (Peak Area $A$):** Integrated signal envelope area.
3. **$x_3$ (Height-to-Area Ratio $h/A$):** Quantifies peak sharpness; true peaks maintain tight $h/A \in [0.12, 0.18]$.
4. **$x_4$ (Signal-to-Noise Ratio $\text{SNR}$):** 
   $$\text{SNR} = \frac{h - \mu_{\text{baseline}}}{\sigma_{\text{noise}}}$$
5. **$x_5$ (Peak Skewness $\gamma_1$):** Third standardized moment measuring tail asymmetry.
6. **$x_6$ (Full Width at Half Maximum $\text{FWHM}$):** Peak width at $50\%$ height in data points/bp.

### 3.2 STR Locus Stutter & Artifact Proximity ($x_7 - x_{12}$)
7. **$x_7$ (Relative Base-Pair Distance $\Delta \text{bp}$):** $\Delta \text{bp} = \text{pos}_{\text{candidate}} - \text{pos}_{\text{major\_allele}}$.
8. **$x_8$ (Back-Stutter Position Flag $I_{-1}$):** Boolean indicator if $\Delta \text{bp} = -k_{\text{motif}}$ (e.g. $-4\text{ bp}$).
9. **$x_9$ (Forward-Stutter Position Flag $I_{+1}$):** Boolean indicator if $\Delta \text{bp} = +k_{\text{motif}}$ (e.g. $+4\text{ bp}$).
10. **$x_{10}$ (Double Back-Stutter Flag $I_{-2}$):** Boolean indicator if $\Delta \text{bp} = -2 \cdot k_{\text{motif}}$ (e.g. $-8\text{ bp}$).
11. **$x_{11}$ (Non-Template Plus-A Addition Flag $I_{+A}$):** Boolean indicator if $\Delta \text{bp} = +1\text{ bp}$.
12. **$x_{12}$ (Stutter Ratio Observed $SR_{\text{obs}}$):** $SR_{\text{obs}} = h_{\text{candidate}} / h_{\text{major\_allele}}$.

### 3.3 Sequence Complexity, Entropy & K-mer Dynamics ($x_{13} - x_{18}$)
13. **$x_{13}$ (Shannon Sequence Entropy $H(S)$):**
    $$H(S) = -\sum_{i \in \{A, C, G, T\}} p_i \log_2 p_i, \quad p_i = \frac{n_i}{N_{\text{bases}}}$$
14. **$x_{14}$ (Longest Homopolymer Run $L_{\text{homo}}$):** Maximum consecutive identical nucleotides (slippage propensity).
15. **$x_{15}$ (GC-Content Fraction $f_{\text{GC}}$):** GC content across the repeat core.
16. **$x_{16}$ (K-mer Motif Hexamer Frequency $f_{\text{hex}}$):** Divergence from canonical motif library.
17. **$x_{17}$ (Flanking SNP Proximity Score $D_{\text{flank}}$):** Distance to nearest known flanking variant.
18. **$x_{18}$ (Interspersed Spacer Count $N_{\text{spacer}}$):** Number of non-canonical intervening base pairs (e.g. `TA`, `TCA`).

### 3.4 Multi-Contributor Mixture & Amplification Dynamics ($x_{19} - x_{24}$)
19. **$x_{19}$ (Heterozygote Balance Ratio $H_b$):** $H_b = h_{\text{minor\_allele}} / h_{\text{major\_allele}} \in [0.0, 1.0]$.
20. **$x_{20}$ (Spectral Bleedthrough / Pull-Up Metric $P_{\text{pull}}$):** Co-eluting peak height in adjacent dye channels.
21. **$x_{21}$ (Locus Amplification Efficiency $\eta_l$):** Total locus RFU / Mean profile RFU.
22. **$x_{22}$ (Template Mass Degradation Index $DI$):** Ratio of small amplicon to large amplicon yield.
23. **$x_{23}$ (Estimated Contributor Proportion $\hat{M}_c$):** Prior mixture proportion assigned to peak cluster.
24. **$x_{24}$ (Analytical Threshold Margin $M_{\text{AT}}$):** $(h - \text{AT}) / \text{AT}$, normalized distance from analytical cutoff.

---

## 4. Multi-Class Artifact Taxonomy & Random Forest Classification

The ML classification layer categorizes each candidate signal into 7 mutually exclusive biophysical classes:

$$\mathcal{C} = \{c_1, c_2, c_3, c_4, c_5, c_6, c_7\}$$

| Class ID | Class Label | Description & Physical Cause | Action in FORENZA Pipeline |
|---|---|---|---|
| $c_1$ | `CLASS_TRUE_ALLELE` | True biological allele contributed by DNA donor | Retained as active candidate for MCMC-MH / MPS |
| $c_2$ | `CLASS_BACK_STUTTER` | Polymerase slippage loop out during PCR ($-1$ repeat) | Subtracted using sequence-specific stutter model |
| $c_3$ | `CLASS_FORWARD_STUTTER` | Forward template slippage during PCR ($+1$ repeat) | Subtracted using forward stutter threshold |
| $c_4$ | `CLASS_MINUS_2BP_STUTTER` | Dinucleotide deletion slippage in tetranucleotide STR | Filtered out of candidate allele set |
| $c_5$ | `CLASS_PLUS_A_ARTIFACT` | Incomplete terminal deoxynucleotidyl transferase ($-A$) | Recombined into parent peak height |
| $c_6$ | `CLASS_SPECTRAL_PULL_UP` | Incomplete spectral matrix deconvolution / dye cross-talk | Culled as instrumental optical artifact |
| $c_7$ | `CLASS_BASE_NOISE_DROP_IN` | Stochastic baseline fluctuation or minor environmental drop-in | Culled below analytical reliability boundary |

### 4.1 Ensemble Random Forest Mathematical Formulation
A collection of $B = 500$ de-correlated decision trees $\{T_1, T_2, \dots, T_B\}$ are trained with bootstrap sampling and random feature subspacing ($m = \lfloor \sqrt{24} \rfloor = 4$ features per split):

For candidate feature vector $\mathbf{x}$, the class posterior probability is the ensemble average:

$$P(c_k \mid \mathbf{x}) = \frac{1}{B} \sum_{b=1}^B I\left( T_b(\mathbf{x}) = c_k \right)$$

$$\hat{y} = \arg\max_{c_k \in \mathcal{C}} P(c_k \mid \mathbf{x})$$

The split criterion minimizes Gini Impurity:

$$I_G(S) = 1 - \sum_{k=1}^7 p_k^2, \quad \Delta I_G = I_G(S) - \frac{|S_L|}{|S|} I_G(S_L) - \frac{|S_R|}{|S|} I_G(S_R)$$

---

## 5. Non-Invasive ML Pre-Filtering Layer for MCMC Mixture Deconvolution

```
                      ┌──────────────────────────────────────────────┐
                      │ RAW FORENSIC DATA INGESTION                  │
                      │ (CE FSA/HID Files & MPS FASTQ/BAM Sequences) │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │ 24-DIMENSIONAL FEATURE EXTRACTION            │
                      │ Signal Morphology, Entropy, Stutter Proximity │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │ FRAGSIFIER ML ENSEMBLE CLASSIFIER            │
                      │ Random Forest (500 Trees) + Artifact Scoring │
                      └──────────────────────┬───────────────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │                                           │
                       ▼                                           ▼
         [ARTIFACTS CULLED & RESCUED]                [HIGH-CONFIDENCE CANDIDATES]
         • Back-stutter subtracted                   • True Alleles flagged
         • Pull-up & Drop-in culled                  • Probability weights P(True)
         • Plus-A re-integrated                      • Cleaned candidate genotypes
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │ MCMC-MH CONTINUOUS MIXTURE DECONVOLUTION     │
                      │ (EuroForMix Gamma & STRmix Log-Normal)       │
                      │ *Mathematical Likelihood Unaltered*          │
                      │ *Chain Burn-in Cut by 40%, Gelman R̂ < 1.02*  │
                      └──────────────────────┬───────────────────────┘
                                             │
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │ ISO/IEC 17025 VERIFIED EVALUATIVE REPORT     │
                      │ (ENFSI 2017 Verbal Scale + LR Shield)        │
                      └──────────────────────────────────────────────┘
```

---

## 6. Certified Benchmark Datasets & Golden Test Vectors

1. **PROVEDIt Dataset (Boston University / NIST):** 1-person to 5-person mixtures, 0.005 ng to 0.50 ng template mass, dynamic dilution ratios (1:1 to 1:19), CE 3500xL & MiSeq FGx platforms.
2. **ISFG MPS Collaborative Exercise Cohort:** 25 Autosomal STR loci across 20 global forensic laboratories evaluating stutter rates and isoallele calling accuracy.
3. **Synthetic High-Stress Artifact EPG Suite:** 1,000 synthetic multi-dye electropherograms with high pull-up ($>15\%$), severe back-stutter ($>25\%$), and tri-allelic microvariants.

---

## 7. Mandatory 5 ISO/IEC 17025 Edge-Case Invariants

- **`EC-MLSTR-01` (False Negative Resistance Invariant):** Zero true biological alleles ($h \ge \text{AT}$) misclassified as stutter or pull-up ($\text{FNR} = 0.000000$ on single-source reference standards).
- **`EC-MLSTR-02` (High-Stutter Discrimination Invariant):** Severe back-stutter in D21S11 / SE33 ($SR = 18.5\%$) correctly identified as `CLASS_BACK_STUTTER` ($P(\text{Stutter}) \ge 0.98$).
- **`EC-MLSTR-03` (Non-Template +A Recombination Invariant):** Split $-A/+A$ peaks at TH01 ($9.3 / 10.3$) re-integrated into single allele call with total mass conservation ($|A_{\text{total}} - (A_{-A} + A_{+A})| = 0$).
- **`EC-MLSTR-04` (Spectral Pull-Up Elimination Invariant):** High RFU peak ($h > 6000\text{ RFU}$) causing bleedthrough in secondary dye correctly rejected ($P(\text{PullUp}) \ge 0.99$).
- **`EC-MLSTR-05` (ISFG 3-Tier Reversibility Invariant):** Every ML-called sequence converts reversibly through Level 1 $\leftrightarrow$ Level 2 $\leftrightarrow$ Level 3 with zero character drift.
