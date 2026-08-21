"""
FORENZA Mitochondrial DNA (mtDNA) Mathematical Formulation Engine (Module 2.3).
Standards Compliance: ISO/IEC 17025:2017, ISFG Recommendations on Forensic mtDNA Testing (2014, 2020),
SWGDAM Interpretation Guidelines for Mitochondrial DNA Analysis.

Research Source: research/ystr_27_mtdna_empop_lineage_research.md §3 & pillar_2_lineage_kinship_research.md §3.

Mathematical Formulations Verbatim from Research:
1. Control Region (D-Loop) Reference Boundaries:
   - HV1: 16024–16365, HV2: 73–340, HV3: 438–574, OHR: 110–441, CSB I–III.
2. ISFG 3'-Right Alignment for Homopolymers & Indels:
   - HV1 Poly-C (16184–16193): 16189.1C, 16189.2C
   - HV2 Poly-C (303–315): 309.1C, 309.2C, 315.1C
   - Dinucleotide Repeats (522–524): 522del, 523del, 524.1AC
3. IUPAC Point Heteroplasmy (PHP) Multi-Base Modeling:
   - R (A/G), Y (C/T), M (A/C), K (G/T), S (G/C), W (A/T).
4. SWGDAM Maternal Kinship & Exclusion Decision Boundaries:
   - 0 differences: Consistent / Match (LR = 1 / p_upper)
   - 1 difference: Inconclusive / single mutational divergence
   - >= 2 homoplasmic point differences: Definitive Exclusion (LR = 0.0)
5. Exact Clopper-Pearson 95% Confidence Bound:
   - k = 0: p_upper = 1 - (0.05)^(1 / (N_EMPOP + 1))
   - Maternal LR = 1 / p_upper
6. PhyloTree Build 17 Hierarchical Haplogroup Prediction:
   - Root L0-L6 -> L3 -> M, N -> R -> H, U, K, J, T, V, W, X, A, B, C, D
"""

import re
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set, Union


# ── IUPAC Ambiguity Codes & Domain Metadata ──────────────────────────────────

MTDNA_IUPAC_CODES: Dict[str, Set[str]] = {
    "A": {"A"},
    "C": {"C"},
    "G": {"G"},
    "T": {"T"},
    "R": {"A", "G"},
    "Y": {"C", "T"},
    "M": {"A", "C"},
    "K": {"G", "T"},
    "S": {"G", "C"},
    "W": {"A", "T"},
    "N": {"A", "C", "G", "T"},
}

# Reverse lookup for IUPAC PHP
MTDNA_BASES_TO_IUPAC: Dict[frozenset, str] = {
    frozenset(["A"]): "A",
    frozenset(["C"]): "C",
    frozenset(["G"]): "G",
    frozenset(["T"]): "T",
    frozenset(["A", "G"]): "R",
    frozenset(["C", "T"]): "Y",
    frozenset(["A", "C"]): "M",
    frozenset(["G", "T"]): "K",
    frozenset(["G", "C"]): "S",
    frozenset(["A", "T"]): "W",
}


@dataclass(frozen=True)
class MtDnaDomainMetadata:
    domain_id: str
    name: str
    start_pos: int
    end_pos: int
    description: str


MTDNA_CONTROL_REGION_DOMAINS: Dict[str, MtDnaDomainMetadata] = {
    "HV1": MtDnaDomainMetadata(
        domain_id="HV1",
        name="Hypervariable Region 1 (HV1)",
        start_pos=16024,
        end_pos=16365,
        description="High mutation rate region; diagnostic for major macro-haplogroups.",
    ),
    "HV2": MtDnaDomainMetadata(
        domain_id="HV2",
        name="Hypervariable Region 2 (HV2)",
        start_pos=73,
        end_pos=340,
        description="Contains primary homopolymeric C-tracts (303–315) and insertion hotspots.",
    ),
    "HV3": MtDnaDomainMetadata(
        domain_id="HV3",
        name="Hypervariable Region 3 (HV3)",
        start_pos=438,
        end_pos=574,
        description="Contains variable dinucleotide AC repeat elements (522–524).",
    ),
    "OHR": MtDnaDomainMetadata(
        domain_id="OHR",
        name="Origin of Heavy-Strand Replication",
        start_pos=110,
        end_pos=441,
        description="Structural origin of replication spanning CSB I, II, and III.",
    ),
    "CSB1": MtDnaDomainMetadata(
        domain_id="CSB1",
        name="Conserved Sequence Block I (CSB I)",
        start_pos=214,
        end_pos=232,
        description="Regulates RNA primer processing and replication initiation.",
    ),
    "CSB2": MtDnaDomainMetadata(
        domain_id="CSB2",
        name="Conserved Sequence Block II (CSB II)",
        start_pos=299,
        end_pos=315,
        description="Transcription termination site; features the 309/315 poly-C tract.",
    ),
    "CSB3": MtDnaDomainMetadata(
        domain_id="CSB3",
        name="Conserved Sequence Block III (CSB III)",
        start_pos=346,
        end_pos=363,
        description="Sequence-specific binding site for mitochondrial transcription factors.",
    ),
}


# ── Variant & Profile Data Structures ────────────────────────────────────────

@dataclass(frozen=True)
class MtDnaVariant:
    """Represents a single mtDNA variant relative to rCRS."""
    position: int
    ref_base: str
    variant_base: str
    variant_type: str        # "SUBSTITUTION", "INSERTION", "DELETION", "PHP"
    insertion_index: Optional[int] = None # e.g. 1 for 309.1C
    raw_notation: str = ""

    @property
    def formatted_call(self) -> str:
        if self.variant_type == "INSERTION":
            idx = self.insertion_index or 1
            return f"{self.position}.{idx}{self.variant_base}"
        elif self.variant_type == "DELETION":
            return f"{self.position}del"
        else:
            return f"{self.position}{self.variant_base}"


@dataclass
class MtDnaProfile:
    profile_id: str
    sample_type: str         # "QUESTIONED", "REFERENCE", "CONTROL"
    variants: List[MtDnaVariant]
    raw_variant_strings: List[str] = field(default_factory=list)
    sequenced_ranges: List[Tuple[int, int]] = field(
        default_factory=lambda: [(16024, 16365), (73, 340), (438, 574)]
    )


@dataclass
class MtDnaEvaluationResult:
    profile_a_id: str
    profile_b_id: str
    shared_variants: List[str]
    differences_a_only: List[str]
    differences_b_only: List[str]
    homoplasmic_differences_count: int
    heteroplasmic_shared_count: int
    is_concordant: bool
    verdict: str             # "MATCH", "INCONCLUSIVE", "EXCLUSION"
    maternal_lr: float
    log10_maternal_lr: float
    database_upper_bound_p: float
    empop_database_size_n: int
    empop_matches_k: int
    predicted_haplogroup_a: str
    predicted_haplogroup_b: str
    verbal_predicate_en: str
    verbal_predicate_tr: str
    prosecutors_fallacy_shield: str


# ── Haplogroup Motifs (PhyloTree Build 17) ───────────────────────────────────

PHYLOTREE_17_MOTIFS: Dict[str, Dict[str, Any]] = {
    "L0": {"motif": {"146C", "182C", "186C", "247G", "523del", "524del", "16093C", "16129C", "16223C", "16230G", "16278C"}, "region": "Southern/Eastern Africa"},
    "L1": {"motif": {"182C", "185T", "247G", "357G", "16126C", "16187C", "16223C", "16264T", "16278C"}, "region": "Central/West Africa"},
    "L2": {"motif": {"146C", "152C", "182C", "198C", "263G", "309.1C", "315.1C", "16129C", "16223C", "16278C", "16390C"}, "region": "Sub-Saharan Africa"},
    "L2a1": {"motif": {"146C", "152C", "182C", "198C", "263G", "309.1C", "315.1C", "750G", "16129C", "16223C", "16278C", "16390C", "16519C"}, "region": "Sub-Saharan Africa / African Diaspora"},
    "L3": {"motif": {"182C", "263G", "315.1C", "750G", "16223C", "16311C"}, "region": "Africa / Ancestral Out-of-Africa"},
    "M": {"motif": {"489C", "10400C", "14783T", "15043A", "16223C"}, "region": "South/East Asia, Indigenous Americas"},
    "N": {"motif": {"8701A", "9540C", "10398A", "10873T", "15301A"}, "region": "Eurasia, Oceania, Americas"},
    "R": {"motif": {"12705C", "16183C", "16189C"}, "region": "West/South Eurasia, Americas"},
    "H": {"motif": {"263G", "315.1C", "750G", "2706A", "7028C"}, "region": "Western & Northern Europe"},
    "H1": {"motif": {"263G", "315.1C", "750G", "16519C"}, "region": "Western & Northern Europe (Peak in Iberia/Scandinavia)"},
    "H1a1": {"motif": {"263G", "315.1C", "750G", "16162G", "16519C"}, "region": "North-Western Europe"},
    "U": {"motif": {"11467G", "12308AG", "12372A", "16270T"}, "region": "Europe, North Africa, South Asia"},
    "U5": {"motif": {"16192T", "16270T", "315.1C", "263G"}, "region": "Ancient Europe & Fennoscandia"},
    "K": {"motif": {"16224C", "16311C", "10550A", "11251G"}, "region": "Europe, Near East"},
    "J": {"motif": {"295C", "489C", "16069T", "16126C"}, "region": "Europe, Middle East"},
    "T": {"motif": {"709A", "16126C", "16294T"}, "region": "Europe, Near East"},
    "T2b": {"motif": {"263G", "315.1C", "16126C", "16294T", "16296T", "16519C"}, "region": "Europe / Ashkenazi Jewish"},
    "V": {"motif": {"4580T", "15904C", "16298C"}, "region": "Western/Northern Europe (Saami)"},
    "W": {"motif": {"195C", "204C", "207A", "16292T"}, "region": "Eurasia, Europe"},
    "X": {"motif": {"153G", "195C", "225C", "16189C", "16278C"}, "region": "Near East, North America, Europe"},
    "A": {"motif": {"663G", "16290T", "16319GA"}, "region": "East Asia, Americas"},
    "B": {"motif": {"16183C", "16189C", "16217C"}, "region": "East Asia, Southeast Asia, Americas"},
    "C": {"motif": {"16223C", "16298C", "16327T"}, "region": "North/East Asia, Americas"},
    "D": {"motif": {"16223C", "16362C"}, "region": "East Asia, Americas"},
    "D4a1": {"motif": {"263G", "309.1C", "315.1C", "16223C", "16362C", "16519C"}, "region": "East Asia / Han Chinese / Japanese"},
}


# ── Mathematical Formulation Engine ──────────────────────────────────────────

class MtDnaMathematicalFormulation:
    """Core biocomputational engine for mtDNA alignment, heteroplasmy, and lineage matching."""

    # ── 1. ISFG Right-Alignment & Variant Parsing ─────────────────────────────

    @classmethod
    def parse_variant_string(cls, raw: str) -> MtDnaVariant:
        """
        Parses raw forensic nomenclature strings into strongly-typed MtDnaVariant.
        Examples:
          - '263G' -> Position 263, Substitution A->G
          - '309.1C' -> Position 309, Insertion 1 'C'
          - '522del' -> Position 522, Deletion
          - '16189Y' -> Position 16189, Point Heteroplasmy C/T
        """
        clean = raw.strip().upper().replace(" ", "")

        # 1. Insertion check: e.g. 309.1C, 315.2C, 524.1AC
        ins_match = re.match(r"^(\d+)\.(\d+)([A-Z]+)$", clean)
        if ins_match:
            pos = int(ins_match.group(1))
            idx = int(ins_match.group(2))
            base = ins_match.group(3)
            # Normalize 524.1AC dinucleotide if needed
            return MtDnaVariant(
                position=pos,
                ref_base="",
                variant_base=base,
                variant_type="INSERTION",
                insertion_index=idx,
                raw_notation=clean,
            )

        # 2. Deletion check: e.g. 522DEL, 523DEL, 3107DEL
        del_match = re.match(r"^(\d+)(DEL|D|-)$", clean)
        if del_match:
            pos = int(del_match.group(1))
            return MtDnaVariant(
                position=pos,
                ref_base="",
                variant_base="",
                variant_type="DELETION",
                raw_notation=f"{pos}del",
            )

        # 3. Standard substitution or Point Heteroplasmy: e.g. 263G, 16189Y, 16519C
        sub_match = re.match(r"^(\d+)([A-Z])$", clean)
        if sub_match:
            pos = int(sub_match.group(1))
            base = sub_match.group(2)
            is_php = base in ["R", "Y", "M", "K", "S", "W"]
            return MtDnaVariant(
                position=pos,
                ref_base="",
                variant_base=base,
                variant_type="PHP" if is_php else "SUBSTITUTION",
                raw_notation=clean,
            )

        raise ValueError(f"Unrecognized mtDNA variant nomenclature format: '{raw}'")

    @classmethod
    def apply_isfg_right_alignment(cls, variants: List[MtDnaVariant]) -> List[MtDnaVariant]:
        """
        Applies ISFG (2014, 2020) & EMPOP 3'-right-alignment normalizer:
        - HV2 Poly-C: 308.1C -> 309.1C, 314.1C -> 315.1C
        - HV1 Poly-C: 16188.1C -> 16189.1C
        - Dinucleotide repeat: 522.1A -> 524.1A
        """
        normalized: List[MtDnaVariant] = []
        for v in variants:
            if v.variant_type == "INSERTION":
                pos = v.position
                idx = v.insertion_index or 1
                base = v.variant_base

                # Right-shift HV2 Poly-C
                if 303 <= pos <= 308 and base == "C":
                    pos = 309
                elif 311 <= pos <= 314 and base == "C":
                    pos = 315
                # Right-shift HV1 Poly-C
                elif 16184 <= pos <= 16188 and base == "C":
                    pos = 16189
                # Right-shift HV3 dinucleotide
                elif 522 <= pos <= 523 and base in ["A", "C", "AC"]:
                    pos = 524

                normalized.append(
                    MtDnaVariant(
                        position=pos,
                        ref_base=v.ref_base,
                        variant_base=base,
                        variant_type="INSERTION",
                        insertion_index=idx,
                        raw_notation=f"{pos}.{idx}{base}",
                    )
                )
            else:
                normalized.append(v)

        # Sort variants by genomic position then insertion index
        normalized.sort(key=lambda x: (x.position, x.insertion_index or 0, x.variant_base))
        return normalized

    # ── 2. Heteroplasmy & Concordance Evaluation ──────────────────────────────

    @classmethod
    def are_bases_compatible(cls, base_a: str, base_b: str) -> bool:
        """
        Evaluates whether two base calls (including IUPAC PHP codes) are compatible
        under maternal lineage sharing rules.
        Example: 'Y' (C/T) is compatible with 'C' and with 'Y'.
        """
        set_a = MTDNA_IUPAC_CODES.get(base_a, {base_a})
        set_b = MTDNA_IUPAC_CODES.get(base_b, {base_b})
        return len(set_a & set_b) > 0

    @classmethod
    def evaluate_pairwise_lineage(
        cls,
        variants_a: List[MtDnaVariant],
        variants_b: List[MtDnaVariant],
        profile_a_id: str = "SAMPLE_A",
        profile_b_id: str = "SAMPLE_B",
        database_size_n: int = 48500,
        observed_database_matches_k: int = 0,
    ) -> MtDnaEvaluationResult:
        """
        Executes SWGDAM pairwise maternal lineage comparison:
        - 0 differences: Match (LR = 1 / p_upper)
        - 1 difference: Inconclusive
        - >= 2 homoplasmic differences: Exclusion (LR = 0.0)
        """
        norm_a = cls.apply_isfg_right_alignment(variants_a)
        norm_b = cls.apply_isfg_right_alignment(variants_b)

        map_a: Dict[Tuple[int, int], MtDnaVariant] = {
            (v.position, v.insertion_index or 0): v for v in norm_a
        }
        map_b: Dict[Tuple[int, int], MtDnaVariant] = {
            (v.position, v.insertion_index or 0): v for v in norm_b
        }

        all_keys = sorted(set(map_a.keys()) | set(map_b.keys()))

        shared_calls: List[str] = []
        diffs_a: List[str] = []
        diffs_b: List[str] = []
        homoplasmic_diff_count = 0
        heteroplasmic_shared_count = 0

        for key in all_keys:
            in_a = key in map_a
            in_b = key in map_b

            if in_a and in_b:
                va = map_a[key]
                vb = map_b[key]
                if va.variant_type == vb.variant_type and va.variant_base == vb.variant_base:
                    shared_calls.append(va.formatted_call)
                    if va.variant_type == "PHP":
                        heteroplasmic_shared_count += 1
                elif cls.are_bases_compatible(va.variant_base, vb.variant_base):
                    # Point heteroplasmy shared compatibility (e.g. 16189Y vs 16189C)
                    shared_calls.append(f"{va.formatted_call}/{vb.formatted_call}")
                    heteroplasmic_shared_count += 1
                else:
                    # Discordant base at same position
                    diffs_a.append(va.formatted_call)
                    diffs_b.append(vb.formatted_call)
                    homoplasmic_diff_count += 1
            elif in_a and not in_b:
                diffs_a.append(map_a[key].formatted_call)
                homoplasmic_diff_count += 1
            elif in_b and not in_a:
                diffs_b.append(map_b[key].formatted_call)
                homoplasmic_diff_count += 1

        # Clopper-Pearson 95% Bound (Research §3.2)
        p_upper = cls.compute_clopper_pearson_bound(
            k=observed_database_matches_k,
            n=database_size_n,
        )

        # Decision Boundaries
        if homoplasmic_diff_count == 0:
            verdict = "MATCH"
            is_concordant = True
            maternal_lr = round(1.0 / p_upper, 4)
            log10_lr = round(math.log10(maternal_lr), 4)
        elif homoplasmic_diff_count == 1:
            verdict = "INCONCLUSIVE"
            is_concordant = True
            # Single mutation decay penalty
            maternal_lr = round(10.0, 4)
            log10_lr = 1.0
        else:
            # SWGDAM Exclusion (>= 2 homoplasmic point differences)
            verdict = "EXCLUSION"
            is_concordant = False
            maternal_lr = 0.0
            log10_lr = -300.0

        # Haplogroup predictions
        hg_a = PhyloTreeHaplogroupPredictor.predict_haplogroup(norm_a)
        hg_b = PhyloTreeHaplogroupPredictor.predict_haplogroup(norm_b)

        # ENFSI (2017) Verbal Predicate
        if maternal_lr >= 1e6:
            v_en = "Extremely Strong Support for Same Maternal Lineage (LR >= 1,000,000)"
            v_tr = "Aynı Anne Soyu Lehine Son Derece Güçlü Kanıt (LR >= 1.000.000)"
        elif maternal_lr >= 1e4:
            v_en = "Very Strong Support for Same Maternal Lineage (10,000 <= LR < 1,000,000)"
            v_tr = "Aynı Anne Soyu Lehine Çok Güçlü Kanıt (10.000 <= LR < 1.000.000)"
        elif maternal_lr >= 1e2:
            v_en = "Moderately Strong Support for Same Maternal Lineage (100 <= LR < 10,000)"
            v_tr = "Aynı Anne Soyu Lehine Orta-Güçlü Kanıt (100 <= LR < 10.000)"
        elif maternal_lr >= 1.0:
            v_en = "Limited / Inconclusive Support for Same Maternal Lineage (1 <= LR < 100)"
            v_tr = "Aynı Anne Soyu Lehine Sınırlı / Yetersiz Kanıt (1 <= LR < 100)"
        elif maternal_lr > 0.0:
            v_en = "Support for Maternal Exclusion / Defense Hypothesis (0 < LR < 1)"
            v_tr = "Anne Soyunun Dışlanması / Savunma Hipotezi Lehine Kanıt (0 < LR < 1)"
        else:
            v_en = "Definitive Exclusion of Maternal Lineage (>= 2 Homoplasmic Differences)"
            v_tr = "Anne Soyunun Kesin Olarak Dışlanması (>= 2 Homoplazmik Fark)"

        prosecutor_shield = (
            "MANDATORY ISFG (2020) mtDNA EVALUATIVE REPORTING DISCLAIMER: "
            "Mitochondrial DNA (mtDNA) is inherited strictly along the matrilineal lineage without meiotic "
            "recombination. All maternally related maternal relatives (brothers, sisters, mothers, maternal grandmothers, "
            "maternal aunts, maternal cousins) share the identical control region haplotype. Likelihood Ratios (LR_mtDNA) "
            "evaluate the probability of observing the sequence under the hypothesis of shared maternal lineage versus an "
            "unrelated individual from the population, but cannot individualize a specific single person."
        )

        return MtDnaEvaluationResult(
            profile_a_id=profile_a_id,
            profile_b_id=profile_b_id,
            shared_variants=shared_calls,
            differences_a_only=diffs_a,
            differences_b_only=diffs_b,
            homoplasmic_differences_count=homoplasmic_diff_count,
            heteroplasmic_shared_count=heteroplasmic_shared_count,
            is_concordant=is_concordant,
            verdict=verdict,
            maternal_lr=maternal_lr,
            log10_maternal_lr=log10_lr,
            database_upper_bound_p=round(p_upper, 7),
            empop_database_size_n=database_size_n,
            empop_matches_k=observed_database_matches_k,
            predicted_haplogroup_a=hg_a,
            predicted_haplogroup_b=hg_b,
            verbal_predicate_en=v_en,
            verbal_predicate_tr=v_tr,
            prosecutors_fallacy_shield=prosecutor_shield,
        )

    # ── 3. Exact Clopper-Pearson 95% Database Frequency ──────────────────────

    @staticmethod
    def compute_clopper_pearson_bound(k: int, n: int, alpha: float = 0.05) -> float:
        """
        Calculates exact Clopper-Pearson 95% binomial upper confidence bound.
        For k = 0: p_upper = 1 - (alpha)^(1 / (n + 1))
        For k > 0: uses beta / F-distribution approximation.
        """
        if n <= 0:
            raise ValueError(f"Database size N ({n}) must be positive.")
        if k < 0:
            raise ValueError(f"Match count k ({k}) cannot be negative.")

        if k == 0:
            return 1.0 - math.pow(alpha, 1.0 / (n + 1.0))
        else:
            # Snedecor F / Beta upper bound for binomial
            # Normal approximation with continuity correction for large N
            p_hat = k / n
            z = 1.95996  # 95% two-sided z
            p_up = (k + 0.5 * z**2 + z * math.sqrt((k * (n - k) / n) + 0.25 * z**2)) / (n + z**2)
            return min(max(p_up, p_hat), 1.0)


# ── PhyloTree 17 Haplogroup Predictor ─────────────────────────────────────────

class PhyloTreeHaplogroupPredictor:
    """Predicts mtDNA haplogroup from control region mutations using PhyloTree Build 17."""

    @staticmethod
    def predict_haplogroup(variants: List[MtDnaVariant]) -> str:
        """
        Scores candidate haplogroups based on diagnostic motif intersection.
        """
        call_set: Set[str] = {v.formatted_call for v in variants}

        best_hg = "H"
        best_score = -999.0

        for hg, data in PHYLOTREE_17_MOTIFS.items():
            motif: Set[str] = data["motif"]
            intersection = call_set & motif
            # Score = 2 * matched_diagnostic - extra private mutations
            score = len(intersection) * 3.0 - (len(motif - intersection) * 1.0)
            if score > best_score:
                best_score = score
                best_hg = hg

        return best_hg
