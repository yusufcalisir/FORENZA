"""
FORENZA HIrisPlex-S Reference Standards & Casework Cohorts (Module 3.1).
Standards Compliance: Walsh et al. (2018) Global Validation Cohort (N=632),
Spanish MDPI Genes (2024) Population Study (N=450), and Certified Multi-Omic Golden Vectors.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class PhenotypeGoldenStandard:
    standard_id: str
    name: str
    population: str
    description: str
    genotype_dosages: Dict[str, float]
    expected_eye_class: str
    min_eye_confidence: float
    expected_hair_class: str
    min_hair_confidence: float
    expected_skin_class: str
    min_skin_confidence: float
    expected_morphology: str


HIRISPLEX_GOLDEN_STANDARDS: Dict[str, PhenotypeGoldenStandard] = {
    "NA12878_CEU_EUROPEAN": PhenotypeGoldenStandard(
        standard_id="NA12878_CEU_EUROPEAN",
        name="NIST RM 8398 / NA12878 (CEU European Fair Phototype)",
        population="Utah European (CEU)",
        description="Classical northern European light pigmentation standard: Blue eyes, blond hair, pale skin (Fitzpatrick Type II).",
        genotype_dosages={
            "rs12913832": 2.0,  # HERC2 Blue (C/C)
            "rs16891982": 2.0,  # SLC45A2 Light (G/G)
            "rs1426654": 2.0,   # SLC24A5 Light (A/A)
            "rs1805007": 1.0,   # MC1R R151C (Het)
            "rs12821256": 2.0,  # KITLG Blond (C/C)
            "rs12203592": 1.0,  # IRF4 Freckling / Light
            "rs1800407": 0.0,   # OCA2 WT
            "rs12896399": 0.0,  # SLC24A4
            "rs1393350": 0.0,   # TYR
            "rs35264875": 2.0,  # TYRP1
            "rs3827760": 0.0,   # EDAR Ancestral
            "rs11803731": 0.0,  # TCHH
        },
        expected_eye_class="Blue",
        min_eye_confidence=0.85,
        expected_hair_class="Blond",
        min_hair_confidence=0.60,
        expected_skin_class="Pale",
        min_skin_confidence=0.85,
        expected_morphology="Straight",
    ),
    "NA19240_YRI_AFRICAN": PhenotypeGoldenStandard(
        standard_id="NA19240_YRI_AFRICAN",
        name="1000G NA19240 (YRI Sub-Saharan African Dark Phototype)",
        population="Yoruba in Ibadan, Nigeria (YRI)",
        description="Sub-Saharan African ancestral dark pigmentation standard: Dark brown eyes, black hair, dark-to-black skin (Fitzpatrick Type VI).",
        genotype_dosages={
            "rs12913832": 0.0,  # HERC2 Ancestral Brown (A/A)
            "rs1800407": 0.0,   # OCA2
            "rs12896399": 0.0,  # SLC24A4
            "rs16891982": 0.0,  # SLC45A2 Ancestral (C/C)
            "rs1393350": 0.0,   # TYR
            "rs12203592": 0.0,  # IRF4
            "rs1426654": 0.0,   # SLC24A5 Ancestral Dark (G/G)
            "rs10424031": 2.0,  # MFSD12 African Dark Allele (A/A)
            "rs2814778": 2.0,   # ACKR1 Duffy Null (C/C)
            "rs1805007": 0.0,   # MC1R WT
            "rs12821256": 0.0,  # KITLG
            "rs35264875": 0.0,  # TYRP1
            "rs3827760": 0.0,   # EDAR WT
            "rs11803731": 2.0,  # TCHH Curly (A/A)
        },
        expected_eye_class="Brown",
        min_eye_confidence=0.70,
        expected_hair_class="Black",
        min_hair_confidence=0.85,
        expected_skin_class="DarkToBlack",
        min_skin_confidence=0.90,
        expected_morphology="Curly_Coily",
    ),
    "CELTIC_RED_HAIR_STANDARD": PhenotypeGoldenStandard(
        standard_id="CELTIC_RED_HAIR_STANDARD",
        name="Celtic Red Hair & High-Freckling Reference Standard",
        population="North-West European (Celtic)",
        description="Homozygous compound MC1R loss-of-function (R151C + R160W) yielding red hair and very pale skin (Fitzpatrick Type I).",
        genotype_dosages={
            "rs12913832": 2.0,  # HERC2 Blue
            "rs1805007": 2.0,   # MC1R R151C (T/T)
            "rs1805008": 2.0,   # MC1R R160W (T/T)
            "rs1426654": 2.0,   # SLC24A5 Light
            "rs16891982": 2.0,  # SLC45A2 Light
            "rs12203592": 2.0,  # IRF4 High Freckling
        },
        expected_eye_class="Blue",
        min_eye_confidence=0.80,
        expected_hair_class="Red",
        min_hair_confidence=0.88,
        expected_skin_class="VeryPale",
        min_skin_confidence=0.85,
        expected_morphology="Straight",
    ),
    "NA18507_CHB_EAST_ASIAN": PhenotypeGoldenStandard(
        standard_id="NA18507_CHB_EAST_ASIAN",
        name="1000G NA18507 (CHB Han Chinese Pigmentation & EDAR Standard)",
        population="Han Chinese in Beijing (CHB)",
        description="East Asian pigmentation standard: Dark brown eyes, thick straight black hair (EDAR 370Ala G/G), intermediate skin.",
        genotype_dosages={
            "rs12913832": 0.0,  # HERC2 Brown
            "rs16891982": 0.0,  # SLC45A2 Ancestral
            "rs1426654": 0.0,   # SLC24A5 Ancestral
            "rs3827760": 2.0,   # EDAR 370Ala Homozygous (G/G)
            "rs1800414": 2.0,   # OCA2 His615Arg East Asian Light Skin
        },
        expected_eye_class="Brown",
        min_eye_confidence=0.90,
        expected_hair_class="Black",
        min_hair_confidence=0.85,
        expected_skin_class="Intermediate",
        min_skin_confidence=0.60,
        expected_morphology="Straight",
    ),
    "HG002_AJ_MEDITERRANEAN": PhenotypeGoldenStandard(
        standard_id="HG002_AJ_MEDITERRANEAN",
        name="GIAB HG002 / NA24385 (Ashkenazi Jewish Intermediate Phototype)",
        population="Ashkenazi Jewish / Mediterranean",
        description="Intermediate Mediterranean phototype: Brown/Hazel eyes, dark brown/black hair, intermediate skin (Fitzpatrick Type III).",
        genotype_dosages={
            "rs12913832": 1.0,  # HERC2 Heterozygous (C/A) -> Intermediate/Brown
            "rs1426654": 2.0,   # SLC24A5 Light
            "rs16891982": 1.0,  # SLC45A2 Het
            "rs12896399": 1.0,  # SLC24A4 Het
        },
        expected_eye_class="Intermediate",
        min_eye_confidence=0.45,
        expected_hair_class="Brown",
        min_hair_confidence=0.60,
        expected_skin_class="Intermediate",
        min_skin_confidence=0.55,
        expected_morphology="Wavy",
    ),
}


class HIrisPlexReferenceDatasets:
    """Service for retrieving certified HIrisPlex-S reference standards and cohorts."""

    @staticmethod
    def list_standards() -> List[PhenotypeGoldenStandard]:
        return list(HIRISPLEX_GOLDEN_STANDARDS.values())

    @staticmethod
    def get_standard(standard_id: str) -> Optional[PhenotypeGoldenStandard]:
        return HIRISPLEX_GOLDEN_STANDARDS.get(standard_id)
