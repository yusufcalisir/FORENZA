"""
FORENZA Forensic Evidence Operating System
Module: mtDNA Control Region (D-Loop), EMPOP 3'-Right Alignment & PhyloTree 17 Biocomputational Engine
Standards Compliance: ISO/IEC 17025:2017, SWGDAM Lineage Guidelines (2020), EMPOP Forensic mtDNA Guidelines, ENFSI (2017)
Research Source: research/ystr_27_mtdna_empop_lineage_research.md
"""

from dataclasses import dataclass, field
from enum import Enum
import math
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from scipy.stats import f as f_dist


class MtdnaRegion(str, Enum):
    HV1 = "HV1 (16024-16365)"
    HV2 = "HV2 (73-340)"
    HV3 = "HV3 (438-574)"
    OHR = "OHR (110-441)"
    CONTROL_REGION = "Control Region (16024-576)"
    CODING_REGION = "Coding Region (577-16023)"


class IUPACAmbiguityCode(str, Enum):
    R = "R"  # A or G (Purine)
    Y = "Y"  # C or T (Pyrimidine)
    M = "M"  # A or C (Amino)
    K = "K"  # G or T (Keto)
    S = "S"  # C or G (Strong)
    W = "W"  # A or T (Weak)
    N = "N"  # Any base


IUPAC_BASES: Dict[str, Set[str]] = {
    "R": {"A", "G"},
    "Y": {"C", "T"},
    "M": {"A", "C"},
    "K": {"G", "T"},
    "S": {"C", "G"},
    "W": {"A", "T"},
    "A": {"A"},
    "C": {"C"},
    "G": {"G"},
    "T": {"T"},
}


@dataclass
class MtdnaVariant:
    position: int
    ref_base: str
    alt_base: str
    variant_type: str  # "SNP", "INS", "DEL", "PHP" (Point Heteroplasmy), "LHP" (Length Heteroplasmy)
    raw_notation: str
    empop_normalized_notation: str
    minor_allele_fraction: Optional[float] = None
    region: MtdnaRegion = MtdnaRegion.CONTROL_REGION


@dataclass
class MtdnaHaplogroupPrediction:
    predicted_haplogroup: str
    macro_haplogroup: str
    confidence_score: float
    matched_motifs: List[str]
    missing_motifs: List[str]
    private_mutations: List[str]
    description: str
    geographic_origin: str


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PHYLOTREE BUILD 17 DIAGNOSTIC MOTIFS CATALOG
# ═══════════════════════════════════════════════════════════════════════════════

PHYLOTREE_17_MOTIFS: Dict[str, Dict[str, Any]] = {
    "H": {
        "macro": "H",
        "description": "European / Near Eastern Core Lineage (rCRS baseline)",
        "geo": "Europe, Near East, North Africa (40-50% in West Eurasia)",
        "motifs": ["73A", "263G", "750G", "16519C"],
        "negative_motifs": ["16223T", "73G"],
    },
    "H1": {
        "macro": "H",
        "description": "Western European Iberian / Franco-Cantabrian Lineage",
        "geo": "Western Europe (Basques, Iberia, Scandinavia)",
        "motifs": ["73A", "263G", "750G", "3010A", "16519C"],
        "negative_motifs": ["16223T", "73G"],
    },
    "H2": {
        "macro": "H",
        "description": "European Lineage with 16291C",
        "geo": "Central / Eastern Europe",
        "motifs": ["73A", "263G", "750G", "16291C", "16519C"],
        "negative_motifs": ["16223T", "73G"],
    },
    "U5": {
        "macro": "U",
        "description": "European Hunter-Gatherer / Mesolithic Ancient Lineage",
        "geo": "Europe (High in Saami, Finns, Basques)",
        "motifs": ["73G", "263G", "750G", "16192T", "16270T", "16519C"],
        "negative_motifs": [],
    },
    "U6": {
        "macro": "U",
        "description": "North African / Berber Lineage",
        "geo": "North Africa, Maghreb, Canary Islands",
        "motifs": ["73G", "263G", "750G", "16172C", "16219G", "16519C"],
        "negative_motifs": [],
    },
    "K": {
        "macro": "U",
        "description": "Western Eurasian / Ashkenazi & Alpine Lineage (Subclade of U8b)",
        "geo": "Europe, Near East, Ashkenazi Jewish",
        "motifs": ["73G", "263G", "750G", "16224C", "16311C", "16519C"],
        "negative_motifs": [],
    },
    "J1": {
        "macro": "J",
        "description": "Near Eastern / Neolithic Agricultural Expansion Lineage",
        "geo": "Near East, Anatolia, Southern Europe",
        "motifs": ["73G", "263G", "295T", "462T", "750G", "16069T", "16126C", "16519C"],
        "negative_motifs": [],
    },
    "T2": {
        "macro": "T",
        "description": "European / Mediterranean Lineage",
        "geo": "Europe, Near East",
        "motifs": ["73G", "263G", "709A", "750G", "16126C", "16294T", "16296T", "16519C"],
        "negative_motifs": [],
    },
    "V": {
        "macro": "HV",
        "description": "Western European / Saami & Basque Lineage",
        "geo": "Europe (Saami, Cantabria, Scandinavia)",
        "motifs": ["72C", "73A", "263G", "750G", "16298C", "16519C"],
        "negative_motifs": ["16223T"],
    },
    "W": {
        "macro": "N",
        "description": "Northern / Eastern European & South Asian Lineage",
        "geo": "Europe, South Asia",
        "motifs": ["73G", "195C", "204C", "207A", "263G", "750G", "16223T", "16292T", "16519C"],
        "negative_motifs": [],
    },
    "X2": {
        "macro": "N",
        "description": "Near Eastern, Mediterranean & Native American (Algonquian) Lineage",
        "geo": "Near East, North America, Caucasus",
        "motifs": ["73G", "153G", "195C", "225A", "263G", "750G", "16189C", "16223T", "16278T", "16519C"],
        "negative_motifs": [],
    },
    "L0": {
        "macro": "L",
        "description": "Basal African Khoisan / Southern African Lineage",
        "geo": "Southern Africa (San, Khoisan)",
        "motifs": ["73G", "146C", "152C", "182C", "186G", "247A", "263G", "750G", "16187T", "16189C", "16223T", "16230G", "16278T", "16311C"],
        "negative_motifs": [],
    },
    "L1": {
        "macro": "L",
        "description": "Central African / Mbuti & Biaka Pygmy Lineage",
        "geo": "Central / West Africa",
        "motifs": ["73G", "146C", "182C", "185T", "188G", "247A", "263G", "750G", "16187T", "16189C", "16223T", "16278T", "16293G", "16311C"],
        "negative_motifs": [],
    },
    "L2a1": {
        "macro": "L",
        "description": "Sub-Saharan African / Bantu Expansion & African American Lineage",
        "geo": "West / Central / South Africa, African Diaspora",
        "motifs": ["73G", "146C", "152C", "182C", "185T", "195C", "247A", "263G", "315.1C", "750G", "16189C", "16209C", "16223T", "16278T", "16390A"],
        "negative_motifs": [],
    },
    "L3": {
        "macro": "L",
        "description": "East African Ancestor of Eurasian Out-of-Africa Lineages (M & N)",
        "geo": "East Africa",
        "motifs": ["73G", "150T", "195C", "263G", "750G", "16189C", "16223T", "16278T", "16362C"],
        "negative_motifs": [],
    },
    "M": {
        "macro": "M",
        "description": "Eurasian Macro-Haplogroup M (Southern Route Out of Africa)",
        "geo": "South Asia, East Asia, Indigenous Americans",
        "motifs": ["73G", "263G", "489C", "750G", "16223T"],
        "negative_motifs": [],
    },
    "A2": {
        "macro": "N",
        "description": "Indigenous American / Pan-American Founding Lineage",
        "geo": "Americas (Indigenous populations), East Asia",
        "motifs": ["73G", "146C", "153G", "235G", "263G", "315.1C", "663G", "750G", "16111T", "16223T", "16290T", "16319A", "16362C"],
        "negative_motifs": [],
    },
    "B2": {
        "macro": "R",
        "description": "Indigenous American / 9-bp Deletion Lineage",
        "geo": "Americas, East Asia, Polynesia",
        "motifs": ["73G", "263G", "750G", "16183C", "16189C", "16217C", "16519C"],
        "negative_motifs": [],
    },
    "C1": {
        "macro": "M",
        "description": "Indigenous American & Siberian Lineage",
        "geo": "Americas, North / East Asia (Siberia)",
        "motifs": ["73G", "263G", "290del", "291del", "489C", "750G", "16223T", "16298C", "16325C", "16327T"],
        "negative_motifs": [],
    },
    "D1": {
        "macro": "M",
        "description": "Indigenous American & East Asian Lineage",
        "geo": "Americas, East Asia",
        "motifs": ["73G", "263G", "489C", "750G", "16223T", "16325C", "16362C"],
        "negative_motifs": [],
    },
};


# ═══════════════════════════════════════════════════════════════════════════════
# 2. BIOCOMPUTATIONAL HELPER ENGINE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class MtdnaEmpopEngine:
    """
    Core Biocomputational Engine for mtDNA Control Region Forensics:
    - rCRS vs RSRS coordinate alignment
    - EMPOP 3'-Right-Alignment Normalization Algorithm on Light Strand
    - IUPAC Point Heteroplasmy (PHP) & Length Heteroplasmy (LHP) parser
    - PhyloTree Build 17 Macro-Haplogroup Bayesian Classifier
    - EMPOP Clopper-Pearson 95% upper bound & Likelihood Ratio (LR_mtDNA)
    - ENFSI 2017 7-tier verbal scale translation
    """

    @classmethod
    def get_region_for_position(cls, pos: int) -> MtdnaRegion:
        """Determines the mtDNA domain of a given genomic coordinate (1..16569)."""
        if 16024 <= pos <= 16365:
            return MtdnaRegion.HV1
        elif 73 <= pos <= 340:
            return MtdnaRegion.HV2
        elif 438 <= pos <= 574:
            return MtdnaRegion.HV3
        elif 110 <= pos <= 441:
            return MtdnaRegion.OHR
        elif pos <= 576 or pos >= 16024:
            return MtdnaRegion.CONTROL_REGION
        else:
            return MtdnaRegion.CODING_REGION

    @classmethod
    def parse_variant(cls, variant_str: str) -> Optional[MtdnaVariant]:
        """
        Parses raw mtDNA variant notation (e.g., '16519C', '315.1C', '16193.1C', '524.1A', '524.2C', '290del', '16093Y')
        into structured MtdnaVariant dataclass.
        """
        raw = variant_str.strip()
        if not raw:
            return None

        # Point Heteroplasmy (e.g. 16093Y, 16189R)
        php_match = re.match(r"^(\d+)([RYMKSW])$", raw, re.IGNORECASE)
        if php_match:
            pos = int(php_match.group(1))
            code = php_match.group(2).upper()
            return MtdnaVariant(
                position=pos,
                ref_base="",
                alt_base=code,
                variant_type="PHP",
                raw_notation=raw,
                empop_normalized_notation=raw,
                region=cls.get_region_for_position(pos),
            )

        # Insertion notation (e.g., 315.1C, 315.2C, 16193.1C, 524.1A)
        ins_match = re.match(r"^(\d+)\.(\d+)([ACGTN]+)$", raw, re.IGNORECASE)
        if ins_match:
            pos = int(ins_match.group(1))
            sub = int(ins_match.group(2))
            alt = ins_match.group(3).upper()
            norm = cls.normalize_empop_insertion(pos, sub, alt)
            return MtdnaVariant(
                position=pos,
                ref_base="",
                alt_base=alt,
                variant_type="INS" if sub == 1 else "LHP",
                raw_notation=raw,
                empop_normalized_notation=norm,
                region=cls.get_region_for_position(pos),
            )

        # Deletion notation (e.g., 290del, 291del, 524del)
        del_match = re.match(r"^(\d+)del([ACGT]*)$", raw, re.IGNORECASE)
        if del_match:
            pos = int(del_match.group(1))
            norm = cls.normalize_empop_deletion(pos)
            return MtdnaVariant(
                position=pos,
                ref_base="",
                alt_base="del",
                variant_type="DEL",
                raw_notation=raw,
                empop_normalized_notation=norm,
                region=cls.get_region_for_position(pos),
            )

        # Substitution SNP (e.g., 16519C, 73G, 263G, 750G, A16519C)
        snp_match = re.match(r"^([ACGT]?)(\d+)([ACGT])$", raw, re.IGNORECASE)
        if snp_match:
            ref = snp_match.group(1).upper()
            pos = int(snp_match.group(2))
            alt = snp_match.group(3).upper()
            norm = f"{pos}{alt}"
            return MtdnaVariant(
                position=pos,
                ref_base=ref,
                alt_base=alt,
                variant_type="SNP",
                raw_notation=raw,
                empop_normalized_notation=norm,
                region=cls.get_region_for_position(pos),
            )

        return None

    @classmethod
    def normalize_empop_insertion(cls, pos: int, sub_index: int, inserted_base: str) -> str:
        """
        Applies EMPOP 3'-right-alignment rule on light strand for homopolymeric insertions:
        - HV1 Poly-C (16184-16193): an extra C inserted anywhere in 16184-16193 -> 16193.1C, 16193.2C
        - HV2 Poly-C (303-315): an extra C inserted anywhere in 303-315 -> 315.1C, 315.2C
        - HV3 AC-repeat (522-524): extra AC -> 524.1A, 524.2C
        """
        # HV1 Homopolymer C-tract
        if 16184 <= pos <= 16193 and inserted_base.upper() == "C":
            return f"16193.{sub_index}C"

        # HV2 Homopolymer C-tract
        if 303 <= pos <= 315 and inserted_base.upper() == "C":
            return f"315.{sub_index}C"

        # HV3 AC Repeat
        if 522 <= pos <= 524:
            return f"524.{sub_index}{inserted_base.upper()}"

        return f"{pos}.{sub_index}{inserted_base.upper()}"

    @classmethod
    def normalize_empop_deletion(cls, pos: int) -> str:
        """
        Applies EMPOP 3'-right-alignment rule on light strand for homopolymeric/tandem deletions:
        - HV2 290-291 CA deletion -> 291del
        - HV3 522-524 AC deletion -> 524del
        """
        if pos in (290, 291):
            return "291del"
        if 522 <= pos <= 524:
            return "524del"
        return f"{pos}del"

    @classmethod
    def normalize_profile(cls, raw_mutations: List[str]) -> List[str]:
        """
        Normalizes a full list of raw mutation strings according to EMPOP guidelines,
        removes duplicates, and sorts by genomic coordinate.
        """
        parsed: List[MtdnaVariant] = []
        for raw in raw_mutations:
            v = cls.parse_variant(raw)
            if v:
                parsed.append(v)

        # Deduplicate and sort by position then sub-index
        seen: Set[str] = set()
        normalized_list: List[str] = []

        # Sort by position
        parsed.sort(key=lambda x: (x.position, x.raw_notation))

        for item in parsed:
            norm_str = item.empop_normalized_notation
            if norm_str not in seen:
                seen.add(norm_str)
                normalized_list.append(norm_str)

        return normalized_list

    @classmethod
    def classify_haplogroup(cls, normalized_mutations: List[str]) -> MtdnaHaplogroupPrediction:
        """
        Classifies macro- and sub-haplogroups against PhyloTree Build 17 diagnostic motifs
        using weighted motif matching and penalty metrics.
        """
        mut_set = set(normalized_mutations)
        scores: Dict[str, float] = {}
        matches_dict: Dict[str, List[str]] = {}
        missing_dict: Dict[str, List[str]] = {}
        private_dict: Dict[str, List[str]] = {}

        for hg_name, hg_data in PHYLOTREE_17_MOTIFS.items():
            motifs = hg_data["motifs"]
            neg_motifs = hg_data.get("negative_motifs", [])

            matched = [m for m in motifs if m in mut_set]
            missing = [m for m in motifs if m not in mut_set]
            negative_hits = [m for m in neg_motifs if m in mut_set]

            # All mutations not in the lineage motif are considered private
            private = [m for m in normalized_mutations if m not in motifs]

            # Weighted match score
            score = (len(matched) * 3.0) - (len(missing) * 1.5) - (len(negative_hits) * 5.0) - (len(private) * 0.2)

            scores[hg_name] = score
            matches_dict[hg_name] = matched
            missing_dict[hg_name] = missing
            private_dict[hg_name] = private

        # Softmax normalization for confidence
        max_score = max(scores.values()) if scores else 0.0
        exp_sum = sum(math.exp(max(s - max_score, -50.0)) for s in scores.values())
        posteriors = {k: (math.exp(max(v - max_score, -50.0)) / exp_sum) for k, v in scores.items()}

        best_hg = max(posteriors, key=posteriors.get) if posteriors else "H"
        best_data = PHYLOTREE_17_MOTIFS[best_hg]

        return MtdnaHaplogroupPrediction(
            predicted_haplogroup=best_hg,
            macro_haplogroup=best_data["macro"],
            confidence_score=posteriors.get(best_hg, 0.50),
            matched_motifs=matches_dict[best_hg],
            missing_motifs=missing_dict[best_hg],
            private_mutations=private_dict[best_hg],
            description=best_data["description"],
            geographic_origin=best_data["geo"],
        )

    @classmethod
    def calculate_empop_95_upper(cls, k: int, n: int = 48500, alpha: float = 0.05) -> float:
        """
        Computes exact 95% Clopper-Pearson Binomial Upper Bound (p_upper) for mtDNA matching:
        For k = 0: p_upper = 1 - alpha^(1 / (N + 1))
        For k > 0: derived via Snedecor F-distribution.
        """
        if n <= 0:
            return 1.0
        if k == 0:
            return 1.0 - math.pow(alpha, 1.0 / (n + 1.0))

        df1 = 2 * (k + 1)
        df2 = 2 * (n - k)
        f_crit = f_dist.ppf(1.0 - (alpha / 2.0), df1, df2)
        numerator = (k + 1) * f_crit
        denominator = (n - k) + (k + 1) * f_crit
        return float(numerator / denominator)

    @classmethod
    def evaluate_lineage_match(
        cls,
        mutations_a: List[str],
        mutations_b: List[str],
        empop_count_k: int = 0,
        empop_database_size: int = 48500,
    ) -> Dict[str, Any]:
        """
        Compares two mtDNA profiles (accounting for heteroplasmy IUPAC codes and homopolymer shifts)
        and computes EMPOP Likelihood Ratio and 7-tier ENFSI Verbal Scale.
        """
        norm_a = cls.normalize_profile(mutations_a)
        norm_b = cls.normalize_profile(mutations_b)

        set_a = set(norm_a)
        set_b = set(norm_b)

        shared = sorted(list(set_a.intersection(set_b)))
        diff_a = sorted(list(set_a.difference(set_b)))
        diff_b = sorted(list(set_b.difference(set_b)))

        # Evaluate heteroplasmy compatibility
        php_compatible = True
        for d in diff_a:
            v_a = cls.parse_variant(d)
            if v_a and v_a.variant_type == "PHP":
                # Check if set_b contains compatible base at same position
                pos = v_a.position
                b_match = [x for x in norm_b if cls.parse_variant(x) and cls.parse_variant(x).position == pos]
                if b_match:
                    alt_b = cls.parse_variant(b_match[0]).alt_base
                    allowed = IUPAC_BASES.get(v_a.alt_base, set())
                    if alt_b not in allowed:
                        php_compatible = False

        is_exclusion = (len(diff_a) > 0 or len(diff_b) > 0) and not php_compatible

        p_upper = cls.calculate_empop_95_upper(empop_count_k, empop_database_size)
        lr = (1.0 / p_upper) if not is_exclusion and p_upper > 0 else 0.0
        log10_lr = math.log10(lr) if lr > 0 else -99.0

        # ENFSI (2017) 7-Tier Verbal Scale
        if is_exclusion or lr == 0.0:
            enfsi_verbal = "Exclusion / Complete Discordance with Maternal Lineage"
        elif log10_lr >= 6.0:
            enfsi_verbal = "Extremely Strong Support for Same Maternal Lineage (Hp)"
        elif log10_lr >= 4.0:
            enfsi_verbal = "Strong Support for Same Maternal Lineage (Hp)"
        elif log10_lr >= 3.0:
            enfsi_verbal = "Moderately Strong Support for Same Maternal Lineage (Hp)"
        elif log10_lr >= 2.0:
            enfsi_verbal = "Moderate Support for Same Maternal Lineage (Hp)"
        elif log10_lr >= 1.0:
            enfsi_verbal = "Limited / Weak Support for Same Maternal Lineage (Hp)"
        else:
            enfsi_verbal = "Inconclusive / Neutral Evidence"

        hg_a = cls.classify_haplogroup(norm_a)
        hg_b = cls.classify_haplogroup(norm_b)

        return {
            "normalized_profile_a": norm_a,
            "normalized_profile_b": norm_b,
            "shared_mutations": shared,
            "profile_a_specific": diff_a,
            "profile_b_specific": diff_b,
            "is_exclusion": is_exclusion,
            "is_match": not is_exclusion,
            "empop_count_k": empop_count_k,
            "empop_database_size": empop_database_size,
            "p_upper_95": p_upper,
            "lr_mtdna": lr,
            "log10_lr": log10_lr,
            "enfsi_verbal_scale": enfsi_verbal,
            "haplogroup_a": hg_a,
            "haplogroup_b": hg_b,
        }

    # Method aliases
    evaluate_maternal_kinship = evaluate_lineage_match
    evaluateMaternalKinship = evaluate_lineage_match



# Aliases for naming compatibility
MtDnaMutationCall = MtdnaVariant
MtdnaMutationCall = MtdnaVariant
MtDnaHaplogroupResult = MtdnaHaplogroupPrediction
MtdnaHaplogroupResult = MtdnaHaplogroupPrediction

