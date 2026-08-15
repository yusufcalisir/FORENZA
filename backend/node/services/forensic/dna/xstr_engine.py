"""
FORENZA X-STR Familial Kinship & Linkage Analysis Engine — Module 07.

Implements verbatim from Pillar 2 Research §2 (X-STR Linkage Groups & Complex Female Kinship Likelihood Ratios):
  - §2.1 X-STR Marker Clusters & Linkage Equilibrium (Investigator Argus X-12 Panel):
           LG1 (Xp22.2): DXS10148, DXS10135, DXS8378 (r_1-2 = 0.003, r_2-3 = 0.022)
           LG2 (Xq12):   DXS7132, DXS10074, DXS10079 (r_1-2 = 0.015, r_2-3 = 0.020)
           LG3 (Xq26):   DXS10103, HPRTB, DXS10101   (r_1-2 = 0.001, r_2-3 = 0.012)
           LG4 (Xq28):   DXS10146, DXS10134, DXS7423 (r_1-2 = 0.005, r_2-3 = 0.008)
  - §2.1 Kosambi Mapping Function:
           r = 0.5 * tanh(2d / 100) = 0.5 * (e^(4d/100) - 1) / (e^(4d/100) + 1)
  - §2.2 Complex Female Pedigree Kinship Formulations (KI_X):
           1. Father-Daughter (Duo): KI_X = 1 / p(A_1)
           2. Paternal Half-Sisters (PHS):
              KI_X,PHS = ((1-r) * (1 / p_a)) + r
              KI_X,Total = PROD_{g=1}^4 KI_X,LG_g
           3. Paternal Grandmother - Granddaughter (PGM-GD):
              KI_X,PGM-GD = 0.5 * (1 / p_a) + 0.5
           4. Mother - Son (MS):
              Heterozygous mother: KI = 0.5 / p(A_1); Homozygous: KI = 1.0 / p(A_1)
           5. Full Sisters (FS)

Golden Benchmark Vector:
  VECTOR_P2_02 — Paternal Half-Sisters (PHS) Analysis (Argus X-12):
                 Obligate paternal allele sharing across LG1–LG4, mean intra-LG r = 0.01
                 Combined KI_X ≈ 1.854e5, log10(KI_X) ≈ 5.268

References:
  ISFG Recommendations on Forensic Interpretation of X-Chromosomal Markers (2012, 2020).
  Tillmar AO, Phillips C, et al. (2017) Guidelines for the forensic use of X-STR markers.
  Kosambi DD (1944) The estimation of map distances from recombination values. Ann Eugen.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ── Investigator Argus X-12 Panel & Linkage Clusters (§2.1) ─────────────────

@dataclass(frozen=True)
class XSTRLocusMetadata:
    """Metadata for a single X-STR locus in the Argus X-12 panel."""
    locus_name: str
    linkage_group: str          # 'LG1', 'LG2', 'LG3', 'LG4'
    chromosomal_band: str       # e.g. 'Xp22.2', 'Xq12', 'Xq26', 'Xq28'
    physical_position_mb: float # Physical position in Mb
    genetic_map_cm: float       # Genetic map distance in cM
    intra_cluster_r: Optional[float]  # Recombination rate to next locus in cluster


@dataclass(frozen=True)
class LinkageGroupMetadata:
    """Metadata for an Argus X-12 linkage group cluster."""
    group_id: str
    chromosomal_band: str
    loci: List[str]
    recombination_rates: List[float]  # [r_1-2, r_2-3]
    genetic_distances_cm: List[float] # [cM_1, cM_2, cM_3]


# Canonical Argus X-12 panel verbatim from Pillar 2 Research §2.1 & §6 Artifact A
ARGUS_X12_LINKAGE_GROUPS: Dict[str, LinkageGroupMetadata] = {
    "LG1": LinkageGroupMetadata(
        group_id="LG1",
        chromosomal_band="Xp22.2",
        loci=["DXS10148", "DXS10135", "DXS8378"],
        recombination_rates=[0.003, 0.022],
        genetic_distances_cm=[18.5, 19.8, 22.1],
    ),
    "LG2": LinkageGroupMetadata(
        group_id="LG2",
        chromosomal_band="Xq12",
        loci=["DXS7132", "DXS10074", "DXS10079"],
        recombination_rates=[0.015, 0.020],
        genetic_distances_cm=[72.3, 74.8, 75.3],
    ),
    "LG3": LinkageGroupMetadata(
        group_id="LG3",
        chromosomal_band="Xq26",
        loci=["DXS10103", "HPRTB", "DXS10101"],
        recombination_rates=[0.001, 0.012],
        genetic_distances_cm=[138.2, 138.6, 140.1],
    ),
    "LG4": LinkageGroupMetadata(
        group_id="LG4",
        chromosomal_band="Xq28",
        loci=["DXS10146", "DXS10134", "DXS7423"],
        recombination_rates=[0.005, 0.008],
        genetic_distances_cm=[155.4, 156.3, 157.2],
    ),
}

# Individual 12 loci lookup
ARGUS_X12_LOCI: Dict[str, XSTRLocusMetadata] = {
    "DXS10148": XSTRLocusMetadata("DXS10148", "LG1", "Xp22.2", 12.42, 18.5, 0.003),
    "DXS10135": XSTRLocusMetadata("DXS10135", "LG1", "Xp22.2", 13.15, 19.8, 0.022),
    "DXS8378":   XSTRLocusMetadata("DXS8378",   "LG1", "Xp22.2", 14.90, 22.1, None),
    "DXS7132":   XSTRLocusMetadata("DXS7132",   "LG2", "Xq12",   68.10, 72.3, 0.015),
    "DXS10074":  XSTRLocusMetadata("DXS10074",  "LG2", "Xq12",   70.80, 74.8, 0.020),
    "DXS10079":  XSTRLocusMetadata("DXS10079",  "LG2", "Xq12",   71.35, 75.3, None),
    "DXS10103":  XSTRLocusMetadata("DXS10103",  "LG3", "Xq26",  133.50, 138.2, 0.001),
    "HPRTB":     XSTRLocusMetadata("HPRTB",     "LG3", "Xq26",  133.90, 138.6, 0.012),
    "DXS10101":  XSTRLocusMetadata("DXS10101",  "LG3", "Xq26",  134.60, 140.1, None),
    "DXS10146":  XSTRLocusMetadata("DXS10146",  "LG4", "Xq28",  148.20, 155.4, 0.005),
    "DXS10134":  XSTRLocusMetadata("DXS10134",  "LG4", "Xq28",  149.10, 156.3, 0.008),
    "DXS7423":   XSTRLocusMetadata("DXS7423",   "LG4", "Xq28",  150.05, 157.2, None),
}

# Locus synonyms (e.g. DXS10074 vs DXS10079 order or DXS10108 / DXS10147)
_XSTR_SYNONYMS: Dict[str, str] = {
    "DXS10108": "DXS10101",
    "DXS10147": "DXS7423",
}


def normalize_xstr_locus_name(name: str) -> str:
    """Normalizes X-STR locus name to canonical Argus X-12 standard."""
    clean = name.strip().upper().replace("-", "").replace("_", "")
    for syn, canon in _XSTR_SYNONYMS.items():
        if clean == syn.upper().replace("-", "").replace("_", ""):
            return canon
    for canon in ARGUS_X12_LOCI:
        if clean == canon.upper().replace("_", ""):
            return canon
    return name.strip().upper()


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class XSTRGenotype:
    """Genotype for a single X-STR locus."""
    locus: str
    allele1: float
    allele2: Optional[float] = None   # None for hemizygous males

    @property
    def alleles(self) -> List[float]:
        if self.allele2 is None or self.allele2 == self.allele1:
            return [self.allele1]
        return [self.allele1, self.allele2]

    @property
    def is_hemizygous(self) -> bool:
        return self.allele2 is None

    @property
    def is_homozygous(self) -> bool:
        return self.allele2 is None or self.allele1 == self.allele2


@dataclass
class XSTRProfile:
    """Full X-STR profile for an individual."""
    profile_id: str
    is_male: bool
    loci: Dict[str, XSTRGenotype]


@dataclass
class LinkageGroupKinshipResult:
    """Kinship calculation result for a single linkage group cluster."""
    group_id: str
    chromosomal_band: str
    evaluated_loci: List[str]
    locus_ki_values: Dict[str, float]
    recombination_rates: List[float]
    group_ki: float
    log10_group_ki: float


@dataclass
class XSTRKinshipEvaluationResult:
    """Full Argus X-12 kinship evaluation report across all 4 linkage groups."""
    profile1_id: str
    profile2_id: str
    profile1_male: bool
    profile2_male: bool
    relationship_tested: str           # 'FATHER_DAUGHTER', 'PATERNAL_HALF_SISTERS', 'PGM_GD', 'MOTHER_SON', 'FULL_SISTERS'
    combined_ki_x: float
    log10_combined_ki_x: float
    evaluated_loci_count: int
    evaluated_clusters_count: int
    linkage_group_results: List[LinkageGroupKinshipResult]
    is_excluded: bool
    kinship_verdict: str
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class XSTREngine:
    """
    FORENZA X-STR Linkage & Female Kinship Engine (Module 07).

    All formulas verbatim from Pillar 2 Research §2.
    """

    def __init__(self, default_allele_frequency: float = 0.10):
        self.default_p = default_allele_frequency
        self.linkage_groups = ARGUS_X12_LINKAGE_GROUPS
        self.loci_metadata = ARGUS_X12_LOCI

    # ── §2.1 Kosambi Mapping Function ─────────────────────────────────────────

    @staticmethod
    def kosambi_map_function(genetic_distance_cm: float) -> float:
        """
        Transforms genetic distance d (in cM) into recombination fraction r using
        the Kosambi mapping function:

        r = 0.5 * tanh(2d / 100) = 0.5 * (e^(4d/100) - 1) / (e^(4d/100) + 1)

        (Kosambi 1944; Research §2.1)
        """
        if genetic_distance_cm < 0:
            raise ValueError("Genetic distance cannot be negative.")
        d = genetic_distance_cm
        val = (2.0 * d) / 100.0
        r = 0.5 * math.tanh(val)
        return min(0.50, max(0.0, r))

    # ── §2.2 Single-Locus Kinship Formulations ────────────────────────────────

    def calculate_father_daughter_ki(
        self,
        father_genotype: XSTRGenotype,
        daughter_genotype: XSTRGenotype,
        p_allele: Optional[float] = None,
    ) -> float:
        """
        Father-Daughter (Duo) Kinship Index:
        Father passes his single intact X chromosome to daughter.
        KI_X,Duo = 1 / p(A_father) if father's allele is present in daughter, else 0.0.

        (Research §2.2)
        """
        p = p_allele if p_allele is not None and p_allele > 0 else self.default_p
        p = max(0.001, min(1.0, p))

        f_allele = father_genotype.allele1
        d_alleles = daughter_genotype.alleles

        if f_allele in d_alleles:
            return round(1.0 / p, 6)
        else:
            return 0.0

    def calculate_mother_son_ki(
        self,
        mother_genotype: XSTRGenotype,
        son_genotype: XSTRGenotype,
        p_allele: Optional[float] = None,
    ) -> float:
        """
        Mother-Son Kinship Index:
        - Heterozygous mother (A_1 A_2): KI = 0.5 / p(A_son)
        - Homozygous mother (A_1 A_1):   KI = 1.0 / p(A_son)
        If son's allele is not in mother's alleles => KI = 0.0 (Exclusion).

        (Research §2.2)
        """
        p = p_allele if p_allele is not None and p_allele > 0 else self.default_p
        p = max(0.001, min(1.0, p))

        son_allele = son_genotype.allele1
        m_alleles = mother_genotype.alleles

        if son_allele not in m_alleles:
            return 0.0

        if mother_genotype.is_homozygous:
            return round(1.0 / p, 6)
        else:
            return round(0.5 / p, 6)

    def calculate_pgm_gd_ki(
        self,
        pgm_genotype: XSTRGenotype,
        gd_genotype: XSTRGenotype,
        p_allele: Optional[float] = None,
    ) -> float:
        """
        Paternal Grandmother - Granddaughter (PGM-GD) Kinship Index:
        KI_X,PGM-GD = 0.5 * (1 / p_a) + 0.5 if shared paternal allele, else 0.5.

        (Research §2.2)
        """
        p = p_allele if p_allele is not None and p_allele > 0 else self.default_p
        p = max(0.001, min(1.0, p))

        pgm_alleles = pgm_genotype.alleles
        gd_alleles = gd_genotype.alleles

        shared = set(pgm_alleles) & set(gd_alleles)
        if shared:
            return round(0.5 * (1.0 / p) + 0.5, 6)
        else:
            return 0.5

    def calculate_phs_locus_ki(
        self,
        sister1_genotype: XSTRGenotype,
        sister2_genotype: XSTRGenotype,
        recombination_r: float = 0.01,
        p_allele: Optional[float] = None,
    ) -> float:
        """
        Paternal Half-Sisters (PHS) single-locus Kinship Index with linkage correction:

        KI_X,PHS = ((1 - r) * (1 / p_a)) + r

        (Research §2.2; VECTOR_P2_02)
        """
        p = p_allele if p_allele is not None and p_allele > 0 else self.default_p
        p = max(0.001, min(1.0, p))
        r = max(0.0, min(0.50, recombination_r))

        s1_alleles = sister1_genotype.alleles
        s2_alleles = sister2_genotype.alleles

        shared = set(s1_alleles) & set(s2_alleles)
        if shared:
            ki = ((1.0 - r) * (1.0 / p)) + r
            return round(ki, 6)
        else:
            # Without shared allele, kinship under H_p with recombination is r
            return round(r, 6)

    # ── Full Argus X-12 Kinship Evaluation ───────────────────────────────────

    def evaluate_xstr_kinship(
        self,
        profile1: XSTRProfile,
        profile2: XSTRProfile,
        relationship: str = "PATERNAL_HALF_SISTERS",
        population_frequencies: Optional[Dict[str, float]] = None,
        custom_intra_r: Optional[float] = None,
    ) -> XSTRKinshipEvaluationResult:
        """
        Full 12-locus Argus X-12 Kinship Evaluation across 4 Linkage Groups.

        Implements product rule across independent linkage groups:
        KI_X,Total = PROD_{g=1}^4 KI_X,LG_g

        (Research §2.2; VECTOR_P2_02)
        """
        rel = relationship.upper().replace("-", "_").replace(" ", "_")
        pop_freqs = population_frequencies or {}

        # Normalize locus keys in profiles
        p1_norm: Dict[str, XSTRGenotype] = {}
        for k, v in profile1.loci.items():
            canon = normalize_xstr_locus_name(k)
            p1_norm[canon] = XSTRGenotype(canon, v.allele1, v.allele2)

        p2_norm: Dict[str, XSTRGenotype] = {}
        for k, v in profile2.loci.items():
            canon = normalize_xstr_locus_name(k)
            p2_norm[canon] = XSTRGenotype(canon, v.allele1, v.allele2)

        lg_results: List[LinkageGroupKinshipResult] = []
        combined_ki = 1.0
        total_eval_loci = 0
        is_excluded = False

        for group_id, lg_meta in self.linkage_groups.items():
            group_ki = 1.0
            locus_ki_map: Dict[str, float] = {}
            eval_loci_in_group: List[str] = []

            for i, loc in enumerate(lg_meta.loci):
                canon_loc = normalize_xstr_locus_name(loc)
                if canon_loc in p1_norm and canon_loc in p2_norm:
                    eval_loci_in_group.append(canon_loc)
                    total_eval_loci += 1
                    g1 = p1_norm[canon_loc]
                    g2 = p2_norm[canon_loc]
                    p_a = pop_freqs.get(canon_loc, self.default_p)

                    # Determine intra-cluster recombination rate r
                    if custom_intra_r is not None:
                        r = custom_intra_r
                    elif i < len(lg_meta.recombination_rates):
                        r = lg_meta.recombination_rates[i]
                    else:
                        r = 0.01

                    if rel in ["FATHER_DAUGHTER", "DUO"]:
                        if profile1.is_male and not profile2.is_male:
                            ki_l = self.calculate_father_daughter_ki(g1, g2, p_a)
                        elif profile2.is_male and not profile1.is_male:
                            ki_l = self.calculate_father_daughter_ki(g2, g1, p_a)
                        else:
                            ki_l = self.calculate_father_daughter_ki(g1, g2, p_a)

                    elif rel in ["PATERNAL_HALF_SISTERS", "PHS", "HALF_SISTERS"]:
                        ki_l = self.calculate_phs_locus_ki(g1, g2, r, p_a)

                    elif rel in ["PGM_GD", "PATERNAL_GRANDMOTHER_GRANDDAUGHTER"]:
                        ki_l = self.calculate_pgm_gd_ki(g1, g2, p_a)

                    elif rel in ["MOTHER_SON", "MS"]:
                        if not profile1.is_male and profile2.is_male:
                            ki_l = self.calculate_mother_son_ki(g1, g2, p_a)
                        elif not profile2.is_male and profile1.is_male:
                            ki_l = self.calculate_mother_son_ki(g2, g1, p_a)
                        else:
                            ki_l = self.calculate_mother_son_ki(g1, g2, p_a)

                    elif rel in ["FULL_SISTERS", "FS"]:
                        # Full sisters share paternal X (100%) + maternal X (50%)
                        ki_l = 0.5 * self.calculate_phs_locus_ki(g1, g2, r, p_a) + 0.5

                    else:
                        ki_l = 1.0

                    locus_ki_map[canon_loc] = ki_l
                    group_ki *= ki_l

                    if ki_l == 0.0:
                        is_excluded = True

            log10_grp = math.log10(group_ki) if group_ki > 0 else -float("inf")
            lg_results.append(
                LinkageGroupKinshipResult(
                    group_id=group_id,
                    chromosomal_band=lg_meta.chromosomal_band,
                    evaluated_loci=eval_loci_in_group,
                    locus_ki_values=locus_ki_map,
                    recombination_rates=lg_meta.recombination_rates,
                    group_ki=round(group_ki, 6),
                    log10_group_ki=round(log10_grp, 5) if group_ki > 0 else -999.0,
                )
            )
            combined_ki *= group_ki

        log10_combined = math.log10(combined_ki) if combined_ki > 0 else -float("inf")

        if is_excluded or combined_ki == 0.0:
            verdict = f"Excluded: X-STR allele incompatibility eliminates {rel} relationship hypothesis."
            status = "EXCLUSION"
        elif combined_ki > 10000.0:
            verdict = f"Extremely Strong Support for {rel} (Combined KI_X = {combined_ki:.2e}, log10 = {log10_combined:.3f})."
            status = "EXTREMELY_STRONG_SUPPORT"
        elif combined_ki > 100.0:
            verdict = f"Strong Support for {rel} (Combined KI_X = {combined_ki:.2f}, log10 = {log10_combined:.3f})."
            status = "STRONG_SUPPORT"
        elif combined_ki > 1.0:
            verdict = f"Moderate Support for {rel} (Combined KI_X = {combined_ki:.2f})."
            status = "MODERATE_SUPPORT"
        else:
            verdict = f"Neutral or uninformative evidence (Combined KI_X = {combined_ki:.2f})."
            status = "UNINFORMATIVE"

        fallacy_shield = (
            "IMPORTANT (X-STR Kinship Legal Shield): The Combined X-Kinship Index (KI_X) "
            "evaluates the likelihood of the evidence under the specified kinship proposition "
            "relative to unrelated individuals. In female lineage testing, shared paternal X chromosomes "
            "are identical-by-descent across all daughters of the same biological father."
        )

        return XSTRKinshipEvaluationResult(
            profile1_id=profile1.profile_id,
            profile2_id=profile2.profile_id,
            profile1_male=profile1.is_male,
            profile2_male=profile2.is_male,
            relationship_tested=rel,
            combined_ki_x=round(combined_ki, 6) if combined_ki > 0 else 0.0,
            log10_combined_ki_x=round(log10_combined, 5) if combined_ki > 0 else -999.0,
            evaluated_loci_count=total_eval_loci,
            evaluated_clusters_count=len(lg_results),
            linkage_group_results=lg_results,
            is_excluded=is_excluded,
            kinship_verdict=verdict,
            prosecutors_fallacy_shield=fallacy_shield,
        )
