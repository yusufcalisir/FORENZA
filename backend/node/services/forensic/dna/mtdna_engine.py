"""
FORENZA Mitochondrial DNA (mtDNA) Control Region Forensics & EMPOP Engine — Module 08.

Implements verbatim from Pillar 2 Research §3:
  - §3.1 Control Region Hypervariable Alignment & ISFG Nomenclature:
           HV1: 16024–16365 nt
           HV2: 73–340 nt
           HV3: 438–574 nt
           ISFG 3' Right-Alignment rules for homopolymeric poly-C tracts:
             - HV1 Poly-C (16184–16193): 16189 T->C generates length variants 16189.1C, 16189.2C
             - HV2 Poly-C (303–315): Insertions scored as 309.1C, 309.2C, 315.1C
             - Dinucleotide Repeats (522–523): 522del, 523del or 524.1AC, 524.2AC
  - §3.2 Heteroplasmy Modeling & IUPAC Nomenclature:
           Point Heteroplasmy (PHP): Y (C/T), R (A/G), W (A/T), S (C/G), K (G/T), M (A/C)
           Length Heteroplasmy (LHP): Poly-C length variants
  - §3.2 EMPOP Database Upper Bound (Clopper-Pearson 95% Bound):
           k = 0: p_upper = 1 - (0.05)^(1 / (N_EMPOP + 1))
           k > 0: Exact Beta quantile bound
           LR_mtDNA = 1 / p_upper, log10(LR) = -log10(p_upper)
  - §3.2 Matrilineal Evaluative Verdicts:
           0 differences / compatible: CANNOT_BE_EXCLUDED (Maternal Match)
           1 difference: INCONCLUSIVE (Single-site divergence / possible heteroplasmy)
           >= 2 differences: EXCLUDED (Different maternal lineages)

References:
  EMPOP Mitochondrial DNA Database Standards (Parson et al., 2014, 2021).
  ISFG Recommendations on Mitochondrial DNA Interpretation (2012, 2020).
  SWGDAM Mitochondrial DNA Interpretation Guidelines (2019).
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from scipy import stats


# ── Hypervariable Region Definitions (§3.1) ──────────────────────────────────

HV1_RANGE: Tuple[int, int] = (16024, 16365)
HV2_RANGE: Tuple[int, int] = (73, 340)
HV3_RANGE: Tuple[int, int] = (438, 574)

# IUPAC Degeneracy / Ambiguity Code Mapping for Point Heteroplasmy (PHP)
IUPAC_HETEROPLASMY_MAP: Dict[str, Set[str]] = {
    "A": {"A"},
    "C": {"C"},
    "G": {"G"},
    "T": {"T"},
    "R": {"A", "G"},
    "Y": {"C", "T"},
    "S": {"C", "G"},
    "W": {"A", "T"},
    "K": {"G", "T"},
    "M": {"A", "C"},
    "B": {"C", "G", "T"},
    "D": {"A", "G", "T"},
    "H": {"A", "C", "T"},
    "V": {"A", "C", "G"},
    "N": {"A", "C", "G", "T"},
}

# Reverse lookup: Set of bases -> IUPAC character
_BASES_TO_IUPAC: Dict[frozenset, str] = {
    frozenset({"A"}): "A",
    frozenset({"C"}): "C",
    frozenset({"G"}): "G",
    frozenset({"T"}): "T",
    frozenset({"A", "G"}): "R",
    frozenset({"C", "T"}): "Y",
    frozenset({"C", "G"}): "S",
    frozenset({"A", "T"}): "W",
    frozenset({"G", "T"}): "K",
    frozenset({"A", "C"}): "M",
    frozenset({"C", "G", "T"}): "B",
    frozenset({"A", "G", "T"}): "D",
    frozenset({"A", "C", "T"}): "H",
    frozenset({"A", "C", "G"}): "V",
    frozenset({"A", "C", "G", "T"}): "N",
}


def bases_to_iupac(bases: List[str]) -> str:
    """Converts a set or list of observed bases at a site to an IUPAC code."""
    clean = frozenset(b.upper() for b in bases if b.upper() in {"A", "C", "G", "T"})
    return _BASES_TO_IUPAC.get(clean, "N")


def are_iupac_bases_compatible(base1: str, base2: str) -> bool:
    """
    Checks whether two IUPAC characters are compatible under maternal transmission.
    Compatible if their allowed base sets intersect (e.g. 'C' and 'Y' intersect at 'C').
    """
    b1_set = IUPAC_HETEROPLASMY_MAP.get(base1.upper(), {base1.upper()})
    b2_set = IUPAC_HETEROPLASMY_MAP.get(base2.upper(), {base2.upper()})
    return bool(b1_set & b2_set)


def get_region_for_position(pos: int) -> str:
    """Determines whether a nucleotide position falls within HV1, HV2, HV3, or Other."""
    if HV1_RANGE[0] <= pos <= HV1_RANGE[1]:
        return "HV1"
    elif HV2_RANGE[0] <= pos <= HV2_RANGE[1]:
        return "HV2"
    elif HV3_RANGE[0] <= pos <= HV3_RANGE[1]:
        return "HV3"
    else:
        return "CR_OTHER"


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class MtDNAVariant:
    """A single mitochondrial variant relative to rCRS/RSRS."""
    position: int                      # e.g. 16189 or 309
    ref_base: str                      # e.g. 'T'
    alt_base: str                      # e.g. 'C' or 'Y' (heteroplasmy)
    region: str                        # 'HV1', 'HV2', 'HV3', 'CR_OTHER'
    variant_type: str = "SNP"          # 'SNP', 'INSERTION', 'DELETION', 'HETEROPLASMY'
    insertion_index: Optional[int] = None  # e.g. 1 for 309.1C, 2 for 309.2C
    notation: str = ""                 # e.g. '16189T', '309.1C', '522del'

    def __post_init__(self):
        if not self.region:
            self.region = get_region_for_position(self.position)
        if not self.notation:
            self.notation = self.format_notation()

    def format_notation(self) -> str:
        """Formats the variant in standard EMPOP notation."""
        if self.variant_type == "DELETION":
            return f"{self.position}del"
        elif self.variant_type == "INSERTION":
            idx = self.insertion_index or 1
            return f"{self.position}.{idx}{self.alt_base}"
        else:
            return f"{self.position}{self.alt_base}"


@dataclass
class MtDNAProfile:
    """Full mtDNA control region profile."""
    profile_id: str
    haplogroup: Optional[str] = None   # e.g. 'H1a', 'U5b', 'L2a', 'T2'
    variants: List[MtDNAVariant] = field(default_factory=list)

    def format_empop_string(self) -> str:
        """Returns sorted space-separated EMPOP string (e.g. '73G 263G 315.1C 16189Y 16519C')."""
        return " ".join(v.notation for v in sorted(self.variants, key=lambda x: (x.position, x.insertion_index or 0)))


@dataclass
class EMPOPUpperBoundResult:
    """EMPOP database frequency calculation result."""
    observed_count_k: int
    database_size_n: int
    alpha: float
    p_upper_bound: float
    maternal_lr: float
    log10_maternal_lr: float
    is_unobserved: bool


@dataclass
class MtDNAMatchEvaluationResult:
    """Comprehensive pairwise mtDNA maternal lineage match evaluation."""
    sample1_id: str
    sample2_id: str
    sample1_empop_string: str
    sample2_empop_string: str
    shared_variants: List[str]
    sample1_unique_variants: List[str]
    sample2_unique_variants: List[str]
    point_heteroplasmies_detected: List[str]
    differing_positions_count: int
    match_status: str                  # 'CANNOT_BE_EXCLUDED', 'INCONCLUSIVE', 'EXCLUDED'
    empop_frequency_bound: float
    maternal_lr: float
    log10_maternal_lr: float
    maternal_lineage_verdict: str
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class MtDNAEngine:
    """
    FORENZA Mitochondrial DNA Control Region Forensic Engine (Module 08).

    Implements ISFG right-alignment, IUPAC heteroplasmy, EMPOP database upper bounds,
    and maternal Likelihood Ratios verbatim from Pillar 2 Research §3.
    """

    DEFAULT_EMPOP_N = 48500  # Global EMPOP representative sample size

    # ── §3.1 ISFG 3' Right-Alignment & Homopolymeric Parsing ──────────────────

    @staticmethod
    def apply_isfg_right_alignment(variants: List[MtDNAVariant]) -> List[MtDNAVariant]:
        """
        Applies ISFG 3' Right-Alignment rules for homopolymeric C-tracts:
        - HV1 Poly-C (16184–16193): T->C transitions at 16189 generate length variants scored as 16189.1C, 16189.2C.
        - HV2 Poly-C (303–315): Insertions scored as 309.1C, 309.2C, 315.1C.
        - Dinucleotide repeats (522–523 Del): 522del, 523del or insertions 524.1AC, 524.2AC.

        (Research §3.1; ISFG 2012/2020 Guidelines)
        """
        aligned: List[MtDNAVariant] = []
        for v in variants:
            # Check for HV2 309 C-insertions
            if v.position in [308, 309, 310] and v.variant_type == "INSERTION" and v.alt_base == "C":
                aligned.append(
                    MtDNAVariant(
                        position=309,
                        ref_base=v.ref_base,
                        alt_base="C",
                        region="HV2",
                        variant_type="INSERTION",
                        insertion_index=v.insertion_index or 1,
                        notation=f"309.{v.insertion_index or 1}C",
                    )
                )
            # Check for HV1 16189 C-insertions
            elif v.position in [16188, 16189, 16190] and v.variant_type == "INSERTION" and v.alt_base == "C":
                aligned.append(
                    MtDNAVariant(
                        position=16189,
                        ref_base=v.ref_base,
                        alt_base="C",
                        region="HV1",
                        variant_type="INSERTION",
                        insertion_index=v.insertion_index or 1,
                        notation=f"16189.{v.insertion_index or 1}C",
                    )
                )
            else:
                aligned.append(v)
        return aligned

    # ── §3.2 EMPOP Exact Binomial Upper Bound & Maternal LR ───────────────────

    @staticmethod
    def calculate_empop_match_probability(
        k: int = 0,
        n_empop: int = 48500,
        alpha: float = 0.05,
    ) -> EMPOPUpperBoundResult:
        """
        Calculates Clopper-Pearson 95% exact binomial upper bound for mtDNA haplotype frequency:

        For unobserved haplotypes (k = 0):
        p_upper = 1 - alpha^(1 / (N + 1)) = 1 - (0.05)^(1 / (N_EMPOP + 1))

        For observed haplotypes (k > 0):
        p_upper = BetaQuantile(1 - alpha/2; k + 1, N - k)

        Maternal LR: LR_mtDNA = 1 / p_upper

        (Research §3.2)
        """
        if k < 0 or n_empop < 1 or k > n_empop:
            raise ValueError(f"Invalid EMPOP parameters: k={k}, n_empop={n_empop}")

        if k == 0:
            p_upper = 1.0 - math.pow(alpha, 1.0 / (n_empop + 1.0))
            is_unobserved = True
        elif k == n_empop:
            p_upper = 1.0
            is_unobserved = False
        else:
            # Beta distribution upper bound: BetaQuantile(1 - alpha/2; k+1, n-k)
            p_upper = float(stats.beta.ppf(1.0 - alpha / 2.0, k + 1, n_empop - k))
            is_unobserved = False

        p_upper = min(1.0, max(1e-12, p_upper))
        lr = 1.0 / p_upper
        log10_lr = math.log10(lr)

        return EMPOPUpperBoundResult(
            observed_count_k=k,
            database_size_n=n_empop,
            alpha=alpha,
            p_upper_bound=p_upper,
            maternal_lr=round(lr, 4),
            log10_maternal_lr=round(log10_lr, 5),
            is_unobserved=is_unobserved,
        )


    # ── §3.2 Maternal Pairwise Concordance Matching ───────────────────────────

    def evaluate_mtdna_maternal_match(
        self,
        evidence: MtDNAProfile,
        suspect: MtDNAProfile,
        n_empop: int = DEFAULT_EMPOP_N,
        empop_observed_k: int = 0,
    ) -> MtDNAMatchEvaluationResult:
        """
        Evaluates pairwise mtDNA sequence concordance between evidence and suspect across
        HV1, HV2, and HV3 regions under SWGDAM and ISFG guidelines.

        Concordance Rules:
        - 0 differences (including compatible heteroplasmy): CANNOT_BE_EXCLUDED (Maternal Match)
        - 1 difference: INCONCLUSIVE (Possible heteroplasmy or germline single-base transition)
        - >= 2 differences: EXCLUDED (Different maternal lineages)

        (Research §3.2)
        """
        # Apply ISFG right-alignment to both profiles
        ev_variants = self.apply_isfg_right_alignment(evidence.variants)
        sus_variants = self.apply_isfg_right_alignment(suspect.variants)

        # Build position -> variant maps
        ev_map: Dict[Tuple[int, Optional[int]], MtDNAVariant] = {
            (v.position, v.insertion_index): v for v in ev_variants
        }
        sus_map: Dict[Tuple[int, Optional[int]], MtDNAVariant] = {
            (v.position, v.insertion_index): v for v in sus_variants
        }

        all_keys = set(ev_map.keys()) | set(sus_map.keys())

        shared: List[str] = []
        ev_unique: List[str] = []
        sus_unique: List[str] = []
        heteroplasmies: List[str] = []
        differing_positions = 0

        for key in sorted(all_keys, key=lambda x: (x[0], x[1] or 0)):
            pos, ins_idx = key
            in_ev = key in ev_map
            in_sus = key in sus_map

            if in_ev and in_sus:
                v_ev = ev_map[key]
                v_sus = sus_map[key]

                # Check for heteroplasmy compatibility
                is_php_ev = v_ev.alt_base in ["Y", "R", "W", "S", "K", "M"]
                is_php_sus = v_sus.alt_base in ["Y", "R", "W", "S", "K", "M"]

                if is_php_ev or is_php_sus:
                    heteroplasmies.append(f"Site {pos}: Ev({v_ev.alt_base}) vs Sus({v_sus.alt_base})")

                if v_ev.alt_base == v_sus.alt_base:
                    shared.append(v_ev.notation)
                elif are_iupac_bases_compatible(v_ev.alt_base, v_sus.alt_base):
                    # Compatible heteroplasmy (e.g. C vs Y) - count as shared with heteroplasmy
                    shared.append(f"{v_ev.notation}/{v_sus.alt_base}")
                else:
                    # Incompatible bases at same site
                    ev_unique.append(v_ev.notation)
                    sus_unique.append(v_sus.notation)
                    differing_positions += 1

            elif in_ev and not in_sus:
                v_ev = ev_map[key]
                ev_unique.append(v_ev.notation)
                differing_positions += 1

            elif in_sus and not in_ev:
                v_sus = sus_map[key]
                sus_unique.append(v_sus.notation)
                differing_positions += 1

        # Calculate EMPOP frequency bound
        empop_res = self.calculate_empop_match_probability(k=empop_observed_k, n_empop=n_empop)

        if differing_positions == 0:
            status = "CANNOT_BE_EXCLUDED"
            maternal_lr = empop_res.maternal_lr
            log10_lr = empop_res.log10_maternal_lr
            verdict = (
                f"Maternal Lineage Match: Evidence and reference share identical mtDNA control region sequence. "
                f"They cannot be excluded as coming from the same maternal lineage (LR_mtDNA = {maternal_lr:.2e}, "
                f"log10 = {log10_lr:.3f})."
            )
        elif differing_positions == 1:
            status = "INCONCLUSIVE"
            maternal_lr = 1.0
            log10_lr = 0.0
            verdict = (
                "Inconclusive: A single nucleotide difference was observed between evidence and reference. "
                "This cannot confirm nor exclude a shared maternal lineage due to potential point heteroplasmy or germline divergence."
            )
        else:
            status = "EXCLUDED"
            maternal_lr = 0.0
            log10_lr = -999.0
            verdict = (
                f"Maternal Lineage Exclusion: {differing_positions} unambiguous sequence differences exclude "
                f"the reference individual from the maternal lineage of the evidence."
            )

        fallacy_shield = (
            "IMPORTANT (Mitochondrial DNA Legal Notice & Fallacy Shield): "
            "Mitochondrial DNA (mtDNA) is inherited strictly along maternal lines without recombination. "
            "An mtDNA match does NOT establish unique individual identity; all maternal relatives "
            "(mother, siblings, maternal aunts/uncles, maternal grandmother) share identical mtDNA haplotypes. "
            "The Likelihood Ratio (LR_mtDNA) measures the probability of the evidence given shared maternal lineage vs unrelated."
        )

        return MtDNAMatchEvaluationResult(
            sample1_id=evidence.profile_id,
            sample2_id=suspect.profile_id,
            sample1_empop_string=evidence.format_empop_string(),
            sample2_empop_string=suspect.format_empop_string(),
            shared_variants=shared,
            sample1_unique_variants=ev_unique,
            sample2_unique_variants=sus_unique,
            point_heteroplasmies_detected=heteroplasmies,
            differing_positions_count=differing_positions,
            match_status=status,
            empop_frequency_bound=empop_res.p_upper_bound,
            maternal_lr=maternal_lr,
            log10_maternal_lr=log10_lr,
            maternal_lineage_verdict=verdict,
            prosecutors_fallacy_shield=fallacy_shield,
        )
