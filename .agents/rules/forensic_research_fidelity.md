# Strict Research-Driven Forensic Biocomputation & Mathematical Integrity Rule

> **Applicability:** All agents, subagents, and automated pipelines developing or modifying the FORENZA codebase.  
> **Authority:** ISO/IEC 17025:2017 • SWGDAM (2020) • ENFSI Evaluative Reporting (2017) • ISFG Recommendations

---

## 1. Absolute Fidelity to the 6 Research Pillars
All biocomputational algorithms, mathematical models, statistical likelihoods, population frequency matrices, calibration budgets, and judicial reporting scales **MUST strictly and verbatim derive from the 6 canonical research specifications** located in `research/`:
1. `research/pillar_1_probabilistic_genotyping_research.md` (Modules 01–05)
2. `research/pillar_2_lineage_kinship_research.md` (Modules 06–10)
3. `research/pillar_3_phenotype_ancestry_research.md` (Modules 11–15)
4. `research/pillar_4_epigenetics_aging_research.md` (Modules 16–20)
5. `research/pillar_5_physical_evidence_research.md` (Modules 21–25)
6. `research/pillar_6_lims_zkp_reporting_research.md` (Modules 26–30)

---

## 2. Zero Approximation / Zero Hallucination Policy
Agents must never approximate, invent, or truncate scientific formulas, constants, or empirical data matrices:
* **Allele Frequencies & Bounds:** Use the full NIST 1036 matrices across all 24 loci and 4 ethnic groups, enforcing the exact NRC II Rule 4.1 minimum floor:
  $$p_{\min} = \max\left(\frac{5}{2N}, 0.001\right) = \frac{5}{2072} \approx 0.002413$$
* **Population Substructure:** Implement exact 4-state Balding-Nichols formulas ($\theta \in [0.01, 0.03, 0.05]$).
* **Kinship & Pedigree Mutations:** Implement exact IBD $(k_0, k_1, k_2)$ equations and Stepwise Mutation Models ($SMM$):
  $$P(m \to n) = \begin{cases} 1 - \mu & m = n \\ \frac{\mu}{2}(1-r)r^{|m-n|-1} & m \neq n \end{cases} \quad (\mu = 10^{-3}, r = 0.10)$$
* **Epigenetic Aging:** Apply the exact Horvath piecewise linear-logarithmic link function ($y_0 = 20.0$ years pivot).
* **Cryptographic & Metrological Governance:** Enforce Groth16 BN254 bilinear pairing verification and ISO/IEC 17025 GUM expanded uncertainty ($U_{95\%} = 2.00 \cdot u_c$).

---

## 3. Mandatory Golden Test Vector Validation
No module implementation or modification is considered complete until it passes all automated unit tests (`pytest`) matching its designated **Golden Ground-Truth Benchmark Test Vectors** (`VECTOR_01` to `VECTOR_P6_03`):
* Single-source pristine profile matching $\log_{10}(LR)$ bounds
* SMM 1-step repeat discrepancy mutation rescue ($KI > 0, W > 50\%$)
* Full-sibling vs. unrelated discrimination ($KI_{\text{FS}} > KI_{\text{Unrelated}} = 1.0$)
* Merkle tree root tamper detection ($P_{\text{detection}} = 100\%$)
* Product rule invariant in log-space: $|\log_{10} LR - \sum \log_{10} LR_l| < 10^{-6}$

---

## 4. Subheading & Mathematical Completeness Requirement
When implementing or upgrading any module:
* **Never skip any subheading, formula, or edge-case handling.**
* Ensure all models include explicit assumptions, limitations, and 95% confidence intervals.
* Ensure bilingual ENFSI (2017) 7-tier evaluative reporting (English & Turkish) with strict defense proposition symmetry and active Prosecutor's Fallacy shields.
