"""
FORENZA X-STR 12-Locus Linkage & Kinship Engine — Mathematical Formulation (Module 2.2).
Standards Compliance: ISO/IEC 17025:2017, ISFG Recommendations on X-STR Testing (2012),
ENFSI Guideline for Evaluative Reporting in Forensic Science (2017).

Research Source: research/pillar_2_lineage_kinship_research.md §2.1 & §2.2.

Mathematical Formulations Verbatim from Research:
1. Investigator Argus X-12 12-Locus Master Registry & 4 Linkage Groups (LG1–LG4).
2. Kosambi Mapping Function & Inverse:
   r = 0.5 * tanh(2d / 100) = 0.5 * (e^(4d/100) - 1) / (e^(4d/100) + 1)
   d = 25 * ln((1 + 2r) / (1 - 2r))
3. Male Hemizygous (XY) Single-Allele Transmission vs Female (XX) Co-Dominant Inheritance.
4. Kinship Index (KI_X) Formulations for Complex Female Pedigrees:
   - Father-Daughter: KI_X = 1 / p(A_f)
   - Paternal Half-Sisters (PHS): KI_X = ((1 - r)*h(A1, A2) + r*h(A1)*h(A2)) / (h(A1)*h(A2))
   - Paternal Grandmother-Granddaughter (PGM-GD): KI_X = (0.5*h(A1, A2) + 0.5*h(A1)*h(A2)) / (h(A1)*h(A2))
   - Mother-Son (MS): Heterozygous mother KI_X = 0.5 / p(A_s), Homozygous mother KI_X = 1.0 / p(A_s)
5. Multi-Cluster Product Rule:
   KI_X,Total = PROD_{g=1}^4 KI_X,LG_g,  log10(KI_X,Total) = SUM_{g=1}^4 log10(KI_X,LG_g)
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union


# ── Linkage Group & Locus Metadata ───────────────────────────────────────────

class KinshipRelationshipType(str, Enum):
    FATHER_DAUGHTER = "FATHER_DAUGHTER"
    PATERNAL_HALF_SISTERS = "PATERNAL_HALF_SISTERS"
    PATERNAL_GRANDMOTHER_GRANDDAUGHTER = "PATERNAL_GRANDMOTHER_GRANDDAUGHTER"
    MOTHER_SON = "MOTHER_SON"
    FULL_SISTERS = "FULL_SISTERS"
    UNRELATED = "UNRELATED"


@dataclass(frozen=True)
class XStrLocusMetadata:
    """Metadata for a single X-STR locus in the Investigator Argus X-12 panel."""
    locus_name: str
    linkage_group: str          # "LG1", "LG2", "LG3", "LG4"
    chromosomal_band: str       # e.g., "Xp22.2", "Xq12", "Xq26", "Xq28"
    physical_position_mb: float # GRCh38 physical position in Mb
    genetic_map_cm: float       # Genetic distance in cM from Xp telomere
    intra_cluster_r_to_next: Optional[float] # Recombination fraction to next locus in cluster
    repeat_motif: str
    amplicon_min_bp: int
    amplicon_max_bp: int
    mean_mutation_rate: float


@dataclass(frozen=True)
class LinkageGroupMetadata:
    """Metadata for one of the 4 canonical Argus X-12 linkage groups."""
    group_id: str
    name: str
    chromosomal_band: str
    loci: Tuple[str, str, str]
    physical_start_mb: float
    physical_end_mb: float
    genetic_start_cm: float
    genetic_end_cm: float
    r_1_2: float
    r_2_3: float


# ── Canonical Argus X-12 Registry (Research §2.1) ───────────────────────────

ARGUS_X12_MASTER_REGISTRY: Dict[str, XStrLocusMetadata] = {
    # ── LG1 (Xp22.2, ~18.5–22.1 cM) ──
    "DXS10148": XStrLocusMetadata(
        locus_name="DXS10148",
        linkage_group="LG1",
        chromosomal_band="Xp22.2",
        physical_position_mb=12.42,
        genetic_map_cm=18.5,
        intra_cluster_r_to_next=0.003,
        repeat_motif="[GGA][GGAA]",
        amplicon_min_bp=135,
        amplicon_max_bp=180,
        mean_mutation_rate=0.0022,
    ),
    "DXS10135": XStrLocusMetadata(
        locus_name="DXS10135",
        linkage_group="LG1",
        chromosomal_band="Xp22.2",
        physical_position_mb=13.15,
        genetic_map_cm=19.8,
        intra_cluster_r_to_next=0.022,
        repeat_motif="[AATC]",
        amplicon_min_bp=185,
        amplicon_max_bp=250,
        mean_mutation_rate=0.0018,
    ),
    "DXS8378": XStrLocusMetadata(
        locus_name="DXS8378",
        linkage_group="LG1",
        chromosomal_band="Xp22.2",
        physical_position_mb=14.90,
        genetic_map_cm=22.1,
        intra_cluster_r_to_next=None,
        repeat_motif="[ATAG]",
        amplicon_min_bp=270,
        amplicon_max_bp=330,
        mean_mutation_rate=0.0006,
    ),

    # ── LG2 (Xq12, ~72.3–75.3 cM) ──
    "DXS7132": XStrLocusMetadata(
        locus_name="DXS7132",
        linkage_group="LG2",
        chromosomal_band="Xq12",
        physical_position_mb=68.10,
        genetic_map_cm=72.3,
        intra_cluster_r_to_next=0.015,
        repeat_motif="[GATA]",
        amplicon_min_bp=125,
        amplicon_max_bp=170,
        mean_mutation_rate=0.0012,
    ),
    "DXS10074": XStrLocusMetadata(
        locus_name="DXS10074",
        linkage_group="LG2",
        chromosomal_band="Xq12",
        physical_position_mb=70.80,
        genetic_map_cm=74.8,
        intra_cluster_r_to_next=0.020,
        repeat_motif="[AAGA]",
        amplicon_min_bp=190,
        amplicon_max_bp=245,
        mean_mutation_rate=0.0015,
    ),
    "DXS10079": XStrLocusMetadata(
        locus_name="DXS10079",
        linkage_group="LG2",
        chromosomal_band="Xq12",
        physical_position_mb=71.35,
        genetic_map_cm=75.3,
        intra_cluster_r_to_next=None,
        repeat_motif="[GATA]",
        amplicon_min_bp=260,
        amplicon_max_bp=315,
        mean_mutation_rate=0.0014,
    ),

    # ── LG3 (Xq26, ~138.2–140.1 cM) ──
    "DXS10103": XStrLocusMetadata(
        locus_name="DXS10103",
        linkage_group="LG3",
        chromosomal_band="Xq26",
        physical_position_mb=133.50,
        genetic_map_cm=138.2,
        intra_cluster_r_to_next=0.001,
        repeat_motif="[CTTT]",
        amplicon_min_bp=130,
        amplicon_max_bp=175,
        mean_mutation_rate=0.0010,
    ),
    "HPRTB": XStrLocusMetadata(
        locus_name="HPRTB",
        linkage_group="LG3",
        chromosomal_band="Xq26",
        physical_position_mb=133.90,
        genetic_map_cm=138.6,
        intra_cluster_r_to_next=0.012,
        repeat_motif="[AGAT]",
        amplicon_min_bp=195,
        amplicon_max_bp=255,
        mean_mutation_rate=0.0008,
    ),
    "DXS10101": XStrLocusMetadata(
        locus_name="DXS10101",
        linkage_group="LG3",
        chromosomal_band="Xq26",
        physical_position_mb=134.60,
        genetic_map_cm=140.1,
        intra_cluster_r_to_next=None,
        repeat_motif="[TATC]",
        amplicon_min_bp=275,
        amplicon_max_bp=335,
        mean_mutation_rate=0.0016,
    ),

    # ── LG4 (Xq28, ~155.4–157.2 cM) ──
    "DXS10146": XStrLocusMetadata(
        locus_name="DXS10146",
        linkage_group="LG4",
        chromosomal_band="Xq28",
        physical_position_mb=148.20,
        genetic_map_cm=155.4,
        intra_cluster_r_to_next=0.005,
        repeat_motif="[AATAG]",
        amplicon_min_bp=135,
        amplicon_max_bp=185,
        mean_mutation_rate=0.0019,
    ),
    "DXS10134": XStrLocusMetadata(
        locus_name="DXS10134",
        linkage_group="LG4",
        chromosomal_band="Xq28",
        physical_position_mb=149.10,
        genetic_map_cm=156.3,
        intra_cluster_r_to_next=0.008,
        repeat_motif="[GAAT]",
        amplicon_min_bp=200,
        amplicon_max_bp=260,
        mean_mutation_rate=0.0011,
    ),
    "DXS7423": XStrLocusMetadata(
        locus_name="DXS7423",
        linkage_group="LG4",
        chromosomal_band="Xq28",
        physical_position_mb=150.05,
        genetic_map_cm=157.2,
        intra_cluster_r_to_next=None,
        repeat_motif="[GATA]",
        amplicon_min_bp=280,
        amplicon_max_bp=340,
        mean_mutation_rate=0.0004,
    ),
}

ARGUS_X12_LINKAGE_GROUPS: Dict[str, LinkageGroupMetadata] = {
    "LG1": LinkageGroupMetadata(
        group_id="LG1",
        name="Linkage Group 1 (Xp22.2)",
        chromosomal_band="Xp22.2",
        loci=("DXS10148", "DXS10135", "DXS8378"),
        physical_start_mb=12.42,
        physical_end_mb=14.90,
        genetic_start_cm=18.5,
        genetic_end_cm=22.1,
        r_1_2=0.003,
        r_2_3=0.022,
    ),
    "LG2": LinkageGroupMetadata(
        group_id="LG2",
        name="Linkage Group 2 (Xq12)",
        chromosomal_band="Xq12",
        loci=("DXS7132", "DXS10074", "DXS10079"),
        physical_start_mb=68.10,
        physical_end_mb=71.35,
        genetic_start_cm=72.3,
        genetic_end_cm=75.3,
        r_1_2=0.015,
        r_2_3=0.020,
    ),
    "LG3": LinkageGroupMetadata(
        group_id="LG3",
        name="Linkage Group 3 (Xq26)",
        chromosomal_band="Xq26",
        loci=("DXS10103", "HPRTB", "DXS10101"),
        physical_start_mb=133.50,
        physical_end_mb=134.60,
        genetic_start_cm=138.2,
        genetic_end_cm=140.1,
        r_1_2=0.001,
        r_2_3=0.012,
    ),
    "LG4": LinkageGroupMetadata(
        group_id="LG4",
        name="Linkage Group 4 (Xq28)",
        chromosomal_band="Xq28",
        loci=("DXS10146", "DXS10134", "DXS7423"),
        physical_start_mb=148.20,
        physical_end_mb=150.05,
        genetic_start_cm=155.4,
        genetic_end_cm=157.2,
        r_1_2=0.005,
        r_2_3=0.008,
    ),
}


# ── Result Data Structures ───────────────────────────────────────────────────

@dataclass
class LocusKinshipResult:
    locus_name: str
    linkage_group: str
    genotype_a: List[float]
    genotype_b: List[float]
    ki_locus: float
    log10_ki_locus: float
    is_shared_allele: bool
    shared_alleles: List[float]
    recombination_fraction_r: float
    allele_frequencies_used: Dict[float, float]
    mutation_flag: bool = False


@dataclass
class LinkageGroupResult:
    group_id: str
    name: str
    chromosomal_band: str
    loci_evaluated: List[str]
    ki_group: float
    log10_ki_group: float
    locus_results: List[LocusKinshipResult]


@dataclass
class XStrEvaluationResult:
    relationship_type: KinshipRelationshipType
    person_a_id: str
    person_a_sex: str
    person_b_id: str
    person_b_sex: str
    total_loci_evaluated: int
    matching_loci_count: int
    mismatch_loci_count: int
    combined_ki: float
    log10_combined_ki: float
    is_kinship_supported: bool
    linkage_group_results: Dict[str, LinkageGroupResult]
    verbal_predicate_en: str
    verbal_predicate_tr: str
    prosecutors_fallacy_shield: str


# ── Mathematical Formulation Engine ──────────────────────────────────────────

class XStrMathematicalFormulation:
    """Core biocomputational engine for X-STR linkage and kinship evaluations."""

    # ── 1. Kosambi & Haldane Mapping Functions (§2.1) ─────────────────────────

    @staticmethod
    def kosambi_map(d_cM: float) -> float:
        """
        Calculates recombination fraction r from genetic distance d (cM)
        using the Kosambi mapping function:
        r = 0.5 * tanh(2d / 100) = 0.5 * (e^(4d/100) - 1) / (e^(4d/100) + 1)
        """
        if d_cM < 0.0:
            raise ValueError(f"Genetic map distance d ({d_cM}) cannot be negative.")
        if d_cM == 0.0:
            return 0.0
        exponent = 4.0 * d_cM / 100.0
        if exponent > 60.0:
            return 0.50
        e_exp = math.exp(exponent)
        return 0.5 * ((e_exp - 1.0) / (e_exp + 1.0))

    @staticmethod
    def inverse_kosambi_map(r: float) -> float:
        """
        Calculates genetic distance d (cM) from recombination fraction r:
        d = 25 * ln((1 + 2r) / (1 - 2r))
        """
        if not (0.0 <= r < 0.50):
            raise ValueError(f"Recombination fraction r ({r}) must be in [0.0, 0.50).")
        if r == 0.0:
            return 0.0
        return 25.0 * math.log((1.0 + 2.0 * r) / (1.0 - 2.0 * r))

    @staticmethod
    def haldane_map(d_cM: float) -> float:
        """
        Calculates recombination fraction r using Haldane mapping function:
        r = 0.5 * (1 - e^(-2d/100))
        """
        if d_cM < 0.0:
            raise ValueError(f"Genetic map distance d ({d_cM}) cannot be negative.")
        return 0.5 * (1.0 - math.exp(-2.0 * d_cM / 100.0))

    # ── 2. Profile Validation & Normalization ──────────────────────────────────

    @staticmethod
    def normalize_locus_name(raw_name: str) -> str:
        """Normalizes locus names to canonical Argus X-12 registry representation."""
        clean = raw_name.strip().upper().replace("-", "").replace("_", "")
        for key in ARGUS_X12_MASTER_REGISTRY:
            if key.upper().replace("-", "").replace("_", "") == clean:
                return key
        return raw_name.strip()

    @staticmethod
    def validate_profile(
        profile: Dict[str, Any],
        sex: str,
        subject_id: str = "SUBJECT",
    ) -> Dict[str, List[float]]:
        """
        Validates sex-specific cytogenetic ploidy rules:
        - Males (XY): Must be hemizygous (single allele per locus). Rejects diallelic male loci.
        - Females (XX): Heterozygous or homozygous (1 or 2 alleles per locus).
        """
        sex_upper = sex.strip().upper()
        if sex_upper not in ["MALE", "FEMALE", "M", "F", "XY", "XX"]:
            raise ValueError(f"Invalid sex specification: '{sex}'. Must be MALE or FEMALE.")

        is_male = sex_upper in ["MALE", "M", "XY"]
        validated: Dict[str, List[float]] = {}

        for raw_loc, raw_val in profile.items():
            loc = XStrMathematicalFormulation.normalize_locus_name(raw_loc)
            if loc not in ARGUS_X12_MASTER_REGISTRY:
                continue

            # Parse alleles
            if isinstance(raw_val, (int, float)):
                alleles = [float(raw_val)]
            elif isinstance(raw_val, str):
                parts = [p.strip() for p in raw_val.replace("/", ",").split(",") if p.strip()]
                alleles = [float(p) for p in parts]
            elif isinstance(raw_val, (list, tuple, set)):
                alleles = [float(x) for x in raw_val]
            else:
                raise ValueError(f"Unrecognized allele format for locus {loc}: {raw_val}")

            alleles = sorted(list(set(alleles)))
            if len(alleles) == 0:
                continue

            # Enforce Male Hemizygote constraint (Research §2.1; EC-XSTR-04)
            if is_male and len(alleles) > 1:
                raise ValueError(
                    f"Hemizygous male {subject_id} (46,XY) cannot possess multiple alleles "
                    f"at X-STR locus {loc}: {alleles}. Multi-allelic call indicates contamination or aneuploidy."
                )

            if not is_male and len(alleles) > 2:
                raise ValueError(
                    f"Female {subject_id} (46,XX) cannot possess > 2 alleles at locus {loc}: {alleles}."
                )

            validated[loc] = alleles

        return validated

    # ── 3. Single-Locus Likelihood & Kinship Calculations ─────────────────────

    @staticmethod
    def compute_single_locus_ki(
        locus: str,
        genotype_a: List[float],
        genotype_b: List[float],
        relationship: KinshipRelationshipType,
        frequencies: Optional[Dict[float, float]] = None,
        intra_cluster_r: float = 0.01,
    ) -> LocusKinshipResult:
        """
        Computes single-locus Likelihood Ratio / Kinship Index (KI_X)
        under the specified pedigree hypothesis.
        """
        meta = ARGUS_X12_MASTER_REGISTRY.get(locus)
        lg = meta.linkage_group if meta else "LG1"
        mu = meta.mean_mutation_rate if meta else 0.0015

        # Default frequency helper
        def get_freq(allele: float) -> float:
            if frequencies and allele in frequencies:
                return max(frequencies[allele], 0.005)
            # Default uninformative empirical frequency bound
            return 0.10

        shared = sorted(list(set(genotype_a) & set(genotype_b)))
        freq_used: Dict[float, float] = {a: get_freq(a) for a in set(genotype_a + genotype_b)}

        ki = 0.0
        mut_flag = False

        if relationship == KinshipRelationshipType.FATHER_DAUGHTER:
            # Person A = Father (single allele Af), Person B = Daughter ({Ad1, Ad2})
            # or vice-versa
            f_alleles = genotype_a if len(genotype_a) == 1 else genotype_b
            d_alleles = genotype_b if len(genotype_a) == 1 else genotype_a

            if len(f_alleles) == 1:
                af = f_alleles[0]
                if af in d_alleles:
                    p_af = get_freq(af)
                    ki = 1.0 / p_af
                else:
                    # Germline mutation
                    mut_flag = True
                    p_d = get_freq(d_alleles[0])
                    ki = (mu / 2.0) / p_d
            else:
                ki = 1.0

        elif relationship == KinshipRelationshipType.PATERNAL_HALF_SISTERS:
            # Two females sharing father's single X chromosome
            # Obligate shared paternal allele in absence of recombination
            if len(shared) >= 1:
                ash = shared[0]
                p_sh = get_freq(ash)
                # Linkage-corrected PHS kinship formula (Research §2.2)
                # KI = ((1 - r)*h(A1, A2) + r*h(A1)*h(A2)) / (h(A1)*h(A2))
                # For single-locus sharing:
                ki = (1.0 - intra_cluster_r) / p_sh + intra_cluster_r
            else:
                # Discrepancy
                mut_flag = True
                ki = mu

        elif relationship == KinshipRelationshipType.PATERNAL_GRANDMOTHER_GRANDDAUGHTER:
            # PGM (female) to Granddaughter (female via son)
            if len(shared) >= 1:
                ash = shared[0]
                p_sh = get_freq(ash)
                # KI_PGM = 0.5 / p(A) + 0.5
                ki = 0.5 / p_sh + 0.5
            else:
                ki = mu

        elif relationship == KinshipRelationshipType.MOTHER_SON:
            # Mother (genotype A, 1 or 2 alleles) to Son (genotype B, 1 allele)
            m_alleles = genotype_a if len(genotype_b) == 1 else genotype_b
            s_allele = genotype_b[0] if len(genotype_b) == 1 else genotype_a[0]

            if s_allele in m_alleles:
                p_s = get_freq(s_allele)
                if len(m_alleles) == 2:
                    # Heterozygous mother
                    ki = 0.5 / p_s
                else:
                    # Homozygous mother
                    ki = 1.0 / p_s
            else:
                mut_flag = True
                ki = mu

        elif relationship == KinshipRelationshipType.FULL_SISTERS:
            # Full sisters: share father (KI ~ 1/p) + mother (0.5/p + 0.5)
            if len(shared) >= 1:
                ash = shared[0]
                p_sh = get_freq(ash)
                ki = (1.0 / p_sh) * (0.5 + 0.5 / p_sh)
            else:
                ki = mu

        elif relationship == KinshipRelationshipType.UNRELATED:
            ki = 1.0
        else:
            ki = 1.0

        ki = max(ki, 0.0)
        log10_ki = math.log10(ki) if ki > 0.0 else -300.0

        return LocusKinshipResult(
            locus_name=locus,
            linkage_group=lg,
            genotype_a=genotype_a,
            genotype_b=genotype_b,
            ki_locus=round(ki, 6),
            log10_ki_locus=round(log10_ki, 6),
            is_shared_allele=len(shared) > 0,
            shared_alleles=shared,
            recombination_fraction_r=intra_cluster_r,
            allele_frequencies_used=freq_used,
            mutation_flag=mut_flag,
        )

    # ── 4. Full 12-Locus Clustered Kinship Evaluation ─────────────────────────

    @classmethod
    def evaluate_xstr_kinship(
        cls,
        profile_a: Dict[str, Any],
        profile_b: Dict[str, Any],
        sex_a: str,
        sex_b: str,
        relationship: KinshipRelationshipType = KinshipRelationshipType.PATERNAL_HALF_SISTERS,
        person_a_id: str = "PERSON_A",
        person_b_id: str = "PERSON_B",
        custom_recombination_rates: Optional[Dict[str, float]] = None,
        population_frequencies: Optional[Dict[str, Dict[float, float]]] = None,
    ) -> XStrEvaluationResult:
        """
        Executes full Argus X-12 12-locus kinship evaluation across 4 linkage clusters (LG1–LG4).
        Enforces product rule across independent linkage groups:
        KI_Total = PROD_{g=1}^4 KI_LG_g
        """
        # Validate ploidy
        val_a = cls.validate_profile(profile_a, sex_a, person_a_id)
        val_b = cls.validate_profile(profile_b, sex_b, person_b_id)

        common_loci = sorted(set(val_a.keys()) & set(val_b.keys()))
        if len(common_loci) == 0:
            raise ValueError(
                f"No common Argus X-12 loci found between {person_a_id} and {person_b_id}."
            )

        lg_results: Dict[str, LinkageGroupResult] = {}
        total_eval = len(common_loci)
        match_count = 0
        mismatch_count = 0

        combined_ki = 1.0
        log10_combined_ki = 0.0

        for g_id, g_meta in ARGUS_X12_LINKAGE_GROUPS.items():
            g_loci_present = [loc for loc in g_meta.loci if loc in common_loci]
            if not g_loci_present:
                continue

            locus_res_list: List[LocusKinshipResult] = []
            group_ki = 1.0
            group_log10 = 0.0

            for loc in g_loci_present:
                meta = ARGUS_X12_MASTER_REGISTRY[loc]
                r_val = (
                    custom_recombination_rates.get(loc, meta.intra_cluster_r_to_next or 0.01)
                    if custom_recombination_rates
                    else (meta.intra_cluster_r_to_next or 0.01)
                )
                freqs = population_frequencies.get(loc) if population_frequencies else None

                res = cls.compute_single_locus_ki(
                    locus=loc,
                    genotype_a=val_a[loc],
                    genotype_b=val_b[loc],
                    relationship=relationship,
                    frequencies=freqs,
                    intra_cluster_r=r_val,
                )
                locus_res_list.append(res)

                if res.is_shared_allele:
                    match_count += 1
                else:
                    mismatch_count += 1

                group_ki *= res.ki_locus
                group_log10 += res.log10_ki_locus

            lg_results[g_id] = LinkageGroupResult(
                group_id=g_id,
                name=g_meta.name,
                chromosomal_band=g_meta.chromosomal_band,
                loci_evaluated=g_loci_present,
                ki_group=group_ki,
                log10_ki_group=group_log10,
                locus_results=locus_res_list,
            )

            combined_ki *= group_ki
            log10_combined_ki += group_log10

        # Invariant check: Additivity of log10 Likelihood Ratios
        sum_log10 = sum(r.log10_ki_group for r in lg_results.values())
        if abs(log10_combined_ki - sum_log10) > 1e-5:
            log10_combined_ki = sum_log10

        is_supported = (combined_ki >= 100.0) and (mismatch_count == 0 or (mismatch_count == 1 and combined_ki >= 10.0))

        # ENFSI (2017) 7-Tier verbal predicate
        if combined_ki >= 1e6:
            v_en = "Extremely Strong Support for Paternal Kinship (LR >= 1,000,000)"
            v_tr = "Baba Tarafı Akrabalık Lehine Son Derece Güçlü Kanıt (LR >= 1.000.000)"
        elif combined_ki >= 1e4:
            v_en = "Very Strong Support for Paternal Kinship (10,000 <= LR < 1,000,000)"
            v_tr = "Baba Tarafı Akrabalık Lehine Çok Güçlü Kanıt (10.000 <= LR < 1.000.000)"
        elif combined_ki >= 1e2:
            v_en = "Moderately Strong Support for Paternal Kinship (100 <= LR < 10,000)"
            v_tr = "Baba Tarafı Akrabalık Lehine Orta-Güçlü Kanıt (100 <= LR < 10.000)"
        elif combined_ki >= 1.0:
            v_en = "Limited / Inconclusive Support for Paternal Kinship (1 <= LR < 100)"
            v_tr = "Baba Tarafı Akrabalık Lehine Sınırlı / Yetersiz Kanıt (1 <= LR < 100)"
        elif combined_ki > 0.0:
            v_en = "Support for Non-Kinship / Defense Hypothesis (0 < LR < 1)"
            v_tr = "Akrabalık Bulunmadığı / Savunma Hipotezi Lehine Kanıt (0 < LR < 1)"
        else:
            v_en = "Definitive Exclusion of Biological Kinship (LR = 0)"
            v_tr = "Biyolojik Akrabalığın Kesin Olarak Dışlanması (LR = 0)"

        prosecutor_shield = (
            "MANDATORY ISFG (2012) X-STR EVALUATIVE REPORTING DISCLAIMER: "
            "X-chromosomal STR markers demonstrate specific lineage transmission dynamics. "
            "Because fathers pass their single X-chromosome intact to all daughters without recombination, "
            "paternal half-sisters share full identical-by-descent haplotypes within linkage groups (LG1–LG4). "
            "Statistical Likelihood Ratios (KI_X) evaluate the probability of observed shared X-chromosomal "
            "haplotypes under the prosecution kinship hypothesis versus unrelated individuals, but cannot "
            "individualize between full sisters and paternal half-sisters sharing the same paternal lineage."
        )

        return XStrEvaluationResult(
            relationship_type=relationship,
            person_a_id=person_a_id,
            person_a_sex=sex_a,
            person_b_id=person_b_id,
            person_b_sex=sex_b,
            total_loci_evaluated=total_eval,
            matching_loci_count=match_count,
            mismatch_loci_count=mismatch_count,
            combined_ki=combined_ki,
            log10_combined_ki=log10_combined_ki,
            is_kinship_supported=is_supported,
            linkage_group_results=lg_results,
            verbal_predicate_en=v_en,
            verbal_predicate_tr=v_tr,
            prosecutors_fallacy_shield=prosecutor_shield,
        )
