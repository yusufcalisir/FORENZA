"""
FORENZA Craniofacial Reference Standards & Anthropological Casework Cohorts.
Module 3.3 — Pillar 3: Phenotyping, Biogeographic Ancestry & Morphometrics.

Contains certified reference individuals and standard benchmark cohorts:
  - NA12878 (CEU European Reference - Leptorrhine Nasal Morphology)
  - NA19240 (YRI Sub-Saharan African Reference - Platyrrhine Nasal Morphology)
  - NA18507 (CHB Han Chinese Reference - Mesorrhine Nasal Morphology)
  - MALE_HIGH_DIMORPHISM_STANDARD (Robust Male Mandibular Standard)
  - FEMALE_GRACILE_STANDARD (Gracile Female Harmonious Standard)
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class CraniofacialReferenceStandard:
    standard_id: str
    sample_name: str
    population: str
    sex: str
    age_years: float
    snp_dosages: Dict[str, int]
    expected_nasal_typology_prefix: str
    expected_max_nasal_index: float
    expected_min_nasal_index: float
    description: str


# ── 5 Certified Reference Standards ───────────────────────────────────────────

CRANIOFACIAL_STANDARDS: Dict[str, CraniofacialReferenceStandard] = {
    "NA12878_CEU_EUROPEAN": CraniofacialReferenceStandard(
        standard_id="NA12878_CEU_EUROPEAN",
        sample_name="NIST RM 8398 / GIAB NA12878 (Utah CEPH)",
        population="EUR",
        sex="FEMALE",
        age_years=35.0,
        snp_dosages={
            "rs974448": 1,    # PAX3 T
            "rs12882923": 0,  # PAX9 (low alar breadth)
            "rs11130635": 2,  # PRDM16 A (high bridge projection)
            "rs13289": 0,     # DCHS2
            "rs7559252": 1,   # PCDH15
        },
        expected_nasal_typology_prefix="LEPTORRHINE",
        expected_min_nasal_index=0.0,
        expected_max_nasal_index=70.0,
        description="European female standard with pronounced nasal bridge elevation and narrow leptorrhine aperture.",
    ),
    "NA19240_YRI_AFRICAN": CraniofacialReferenceStandard(
        standard_id="NA19240_YRI_AFRICAN",
        sample_name="HapMap NA19240 (Yoruba in Ibadan, Nigeria)",
        population="AFR",
        sex="FEMALE",
        age_years=30.0,
        snp_dosages={
            "rs974448": 0,    # PAX3
            "rs12882923": 2,  # PAX9 C (broad alar base)
            "rs11130635": 0,  # PRDM16
            "rs13289": 2,     # DCHS2 G (subnasale angle recession)
            "rs7559252": 2,   # PCDH15 C
        },
        expected_nasal_typology_prefix="PLATYRRHINE",
        expected_min_nasal_index=75.0,
        expected_max_nasal_index=150.0,
        description="Sub-Saharan African standard with expanded alar breadth, flatter nasal dorsum, and platyrrhine aperture.",
    ),
    "NA18507_CHB_EAST_ASIAN": CraniofacialReferenceStandard(
        standard_id="NA18507_CHB_EAST_ASIAN",
        sample_name="HapMap NA18507 / HG005 (Han Chinese, Beijing)",
        population="EAS",
        sex="MALE",
        age_years=28.0,
        snp_dosages={
            "rs974448": 1,    # PAX3
            "rs12882923": 1,  # PAX9
            "rs11130635": 1,  # PRDM16
            "rs13289": 1,     # DCHS2
            "rs7559252": 1,   # PCDH15
        },
        expected_nasal_typology_prefix="MESORRHINE",
        expected_min_nasal_index=70.0,
        expected_max_nasal_index=84.9,
        description="East Asian male standard with intermediate mesorrhine nasal dimensions and prominent zygomatic arches.",
    ),
    "MALE_HIGH_DIMORPHISM": CraniofacialReferenceStandard(
        standard_id="MALE_HIGH_DIMORPHISM",
        sample_name="Standard Male High-Dimorphism Cohort",
        population="EUR",
        sex="MALE",
        age_years=40.0,
        snp_dosages={
            "rs974448": 2,    # PAX3 (broad cranial vault)
            "rs12882923": 2,  # PAX9 (wide midface)
            "rs11130635": 2,  # PRDM16 (high projection)
            "rs13289": 0,     # DCHS2
            "rs7559252": 2,   # PCDH15 (prominent chin)
        },
        expected_nasal_typology_prefix="LEPTORRHINE",
        expected_min_nasal_index=0.0,
        expected_max_nasal_index=85.0,
        description="Male craniometric profile showing robust supraorbital arches, +8.4 mm mandibular expansion, and large facial height.",
    ),
    "FEMALE_GRACILE_STANDARD": CraniofacialReferenceStandard(
        standard_id="FEMALE_GRACILE_STANDARD",
        sample_name="Standard Female Gracile Morphology Cohort",
        population="EUR",
        sex="FEMALE",
        age_years=24.0,
        snp_dosages={
            "rs974448": 0,    # PAX3
            "rs12882923": 0,  # PAX9
            "rs11130635": 1,  # PRDM16
            "rs13289": 0,     # DCHS2
            "rs7559252": 0,   # PCDH15
        },
        expected_nasal_typology_prefix="LEPTORRHINE",
        expected_min_nasal_index=0.0,
        expected_max_nasal_index=80.0,
        description="Gracile female morphology with slender facial breadth, smooth mandibular contours, and harmonious proportions.",
    ),
}
