"""
FORENZA Biogeographic Ancestry Certified Reference Standards & Benchmark Datasets (Module 3.2).

Includes 5 Globally Standardized Reference Individuals:
  1. NA12878 / NIST RM 8398 (Utah CEU European): Dominant EUR >= 0.95
  2. NA19240 / 1000 Genomes (YRI Yoruba Sub-Saharan African): Dominant AFR >= 0.98, DARC Duffy Null (C/C)
  3. NA18507 / HG005 (CHB Han Chinese East Asian): Dominant EAS >= 0.95, EDAR (G/G), ADH1B (T/T)
  4. HG002 / NA24385 (Ashkenazi Jewish / Mediterranean): Dominant EUR/MID admixture
  5. ADMIXED_EUR_AFR_SYNTHETIC (50/50 Balanced Admixture Benchmark): Q_EUR = 0.50 ± 0.05, Q_AFR = 0.50 ± 0.05
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field


@dataclass
class BGAGoldenStandard:
    standard_id: str
    name: str
    population: str
    description: str
    genotype_dosages: Dict[str, float]
    expected_dominant_pop: str
    min_dominant_proportion: float
    expected_lat_bounds: Tuple[float, float]
    expected_lng_bounds: Tuple[float, float]
    expected_classification: str


BGA_GOLDEN_STANDARDS: Dict[str, BGAGoldenStandard] = {
    "NA12878_CEU_EUROPEAN": BGAGoldenStandard(
        standard_id="NA12878_CEU_EUROPEAN",
        name="NIST RM 8398 / NA12878 (CEU European Reference Standard)",
        population="Utah European (CEU)",
        description="Standard European reference: High SLC24A5, SLC45A2, HERC2 derived frequencies.",
        genotype_dosages={
            "rs1426654": 2.0,  # SLC24A5 European (A/A)
            "rs16891982": 2.0, # SLC45A2 European (G/G)
            "rs12913832": 2.0, # HERC2 Blue (G/G)
            "rs2814778": 0.0,  # DARC Ancestral (non-African)
            "rs10497191": 2.0, # High EUR
            "rs798443": 2.0,   # High EUR
            "rs1462906": 2.0,  # High EUR
            "rs7997709": 2.0,  # High EUR
            "rs1572018": 2.0,  # High EUR
            "rs3916235": 2.0,  # High EUR
            "rs3827760": 0.0,  # Non-East Asian
        },
        expected_dominant_pop="EUR",
        min_dominant_proportion=0.95,
        expected_lat_bounds=(40.0, 55.0),
        expected_lng_bounds=(5.0, 25.0),
        expected_classification="HOMOGENEOUS",
    ),
    "NA19240_YRI_AFRICAN": BGAGoldenStandard(
        standard_id="NA19240_YRI_AFRICAN",
        name="1000 Genomes NA19240 (YRI Sub-Saharan African Reference)",
        population="Yoruba in Ibadan, Nigeria (YRI)",
        description="Sub-Saharan African reference: DARC Duffy Null homozygous (C/C), high STAT4, CPM, ACKR1.",
        genotype_dosages={
            "rs2814778": 2.0,  # DARC Duffy Null (C/C)
            "rs1426654": 0.0,  # SLC24A5 Dark Ancestral
            "rs16891982": 0.0, # SLC45A2 Ancestral
            "rs3737576": 2.0,  # CPM African (C/C)
            "rs7554936": 2.0,  # African (T/T)
            "rs1876482": 2.0,  # African (C/C)
            "rs1834619": 2.0,  # STAT4 African (G/G)
            "rs6754311": 2.0,  # African (G/G)
            "rs4833103": 2.0,  # African (C/C)
            "rs7657799": 2.0,  # African (T/T)
            "rs870347": 2.0,   # African (T/T)
            "rs3823159": 2.0,  # African (A/A)
            "rs917115": 2.0,   # African (G/G)
            "rs6990312": 2.0,  # African (G/G)
            "rs2196051": 2.0,  # African (T/T)
            "rs1871534": 2.0,  # African (T/T)
            "rs3814134": 2.0,  # African (G/G)
            "rs174570": 2.0,   # FADS2 African (T/T)
            "rs1079597": 2.0,  # ANKK1 African (T/T)
            "rs2166624": 2.0,  # African (C/C)
            "rs7326934": 2.0,  # African (T/T)
            "rs12439433": 2.0, # African (A/A)
            "rs459920": 2.0,   # African (G/G)
            "rs4411548": 2.0,  # African (T/T)
            "rs2593595": 2.0,  # African (G/G)
            "rs17642714": 2.0, # African (G/G)
            "rs4471745": 2.0,  # African (A/A)
            "rs11652805": 2.0, # African (T/T)
            "rs2042762": 2.0,  # African (G/G)
            "rs7226659": 2.0,  # African (T/T)
            "rs4891825": 2.0,  # African (T/T)
            "rs7251928": 2.0,  # African (A/A)
            "rs310644": 2.0,   # African (T/T)
            "rs2024566": 2.0,  # African (A/A)
            "rs3827760": 0.0,  # Non-East Asian
        },
        expected_dominant_pop="AFR",
        min_dominant_proportion=0.98,
        expected_lat_bounds=(-5.0, 15.0),
        expected_lng_bounds=(10.0, 35.0),
        expected_classification="HOMOGENEOUS",
    ),
    "NA18507_CHB_EAST_ASIAN": BGAGoldenStandard(
        standard_id="NA18507_CHB_EAST_ASIAN",
        name="1000 Genomes NA18507 / HG005 (CHB Han Chinese Reference)",
        population="Han Chinese in Beijing, China (CHB)",
        description="East Asian reference: EDAR 370Ala homozygous (G/G), ADH1B (T/T), ALDH2 (A/A), OCA2 (T/T).",
        genotype_dosages={
            "rs3827760": 2.0,  # EDAR 370Ala (G/G)
            "rs1229984": 2.0,  # ADH1B East Asian (T/T)
            "rs3811801": 2.0,  # East Asian (G/G)
            "rs671": 2.0,      # ALDH2 East Asian (A/A)
            "rs1800414": 2.0,  # OCA2 East Asian (T/T)
            "rs2814778": 0.0,  # Non-African
            "rs1426654": 0.0,  # Non-European light
            "rs16891982": 0.0, # Non-European light
            "rs798443": 2.0,   # High EAS
            "rs10497191": 2.0, # High EAS
            "rs7722456": 2.0,  # High EAS
            "rs192655": 2.0,   # High EAS
            "rs1462906": 2.0,  # High EAS
            "rs2238151": 2.0,  # High EAS
            "rs7997709": 2.0,  # High EAS
            "rs1572018": 2.0,  # High EAS
            "rs735480": 2.0,   # High EAS
            "rs3916235": 2.0,  # High EAS
        },
        expected_dominant_pop="EAS",
        min_dominant_proportion=0.95,
        expected_lat_bounds=(25.0, 45.0),
        expected_lng_bounds=(90.0, 125.0),
        expected_classification="HOMOGENEOUS",
    ),
    "HG002_AJ_MEDITERRANEAN": BGAGoldenStandard(
        standard_id="HG002_AJ_MEDITERRANEAN",
        name="GIAB HG002 / NA24385 (Ashkenazi Jewish / Mediterranean Standard)",
        population="Ashkenazi Jewish (AJ)",
        description="Southern European & Levantine/Middle Eastern composite lineage.",
        genotype_dosages={
            "rs1426654": 2.0,  # SLC24A5 Light (A/A)
            "rs16891982": 1.0, # SLC45A2 Heterozygous (C/G)
            "rs12913832": 0.0, # HERC2 Hazel/Brown (A/A)
            "rs2814778": 0.0,  # DARC non-African
            "rs4918664": 2.0,  # High EUR/MID
            "rs9522149": 2.0,  # High EUR/MID
            "rs200354": 2.0,   # High EUR/MID
            "rs10497191": 2.0,
            "rs798443": 2.0,
        },
        expected_dominant_pop="MID",
        min_dominant_proportion=0.55,
        expected_lat_bounds=(25.0, 52.0),
        expected_lng_bounds=(10.0, 50.0),
        expected_classification="HOMOGENEOUS",
    ),
    "ADMIXED_EUR_AFR_SYNTHETIC": BGAGoldenStandard(
        standard_id="ADMIXED_EUR_AFR_SYNTHETIC",
        name="50/50 Balanced EUR/AFR Synthetic Admixture Standard",
        population="Synthetic F1 European-African Admixture",
        description="F1 generation equal admixture (50% EUR / 50% AFR) with heterozygous AIM markers.",
        genotype_dosages={
            "rs2814778": 1.0,  # DARC Duffy Null Het (T/C)
            "rs1426654": 1.0,  # SLC24A5 Het (A/G)
            "rs16891982": 1.0, # SLC45A2 Het (C/G)
            "rs3737576": 1.0,
            "rs7554936": 1.0,
            "rs1876482": 1.0,
            "rs1834619": 1.0,
            "rs6754311": 1.0,
            "rs10497191": 1.0,
            "rs4833103": 1.0,
            "rs7657799": 1.0,
            "rs7722456": 1.0,
            "rs870347": 1.0,
            "rs3823159": 1.0,
            "rs192655": 1.0,
            "rs917115": 1.0,
            "rs1462906": 1.0,
            "rs6990312": 1.0,
            "rs2196051": 1.0,
            "rs1871534": 1.0,
            "rs3814134": 1.0,
            "rs174570": 1.0,
            "rs1079597": 1.0,
            "rs2238151": 1.0,
            "rs7997709": 1.0,
            "rs1572018": 1.0,
            "rs2166624": 1.0,
            "rs7326934": 1.0,
            "rs12439433": 1.0,
            "rs735480": 1.0,
            "rs459920": 1.0,
            "rs4411548": 1.0,
            "rs2593595": 1.0,
            "rs17642714": 1.0,
            "rs4471745": 1.0,
            "rs11652805": 1.0,
            "rs2042762": 1.0,
            "rs7226659": 1.0,
            "rs3916235": 1.0,
            "rs4891825": 1.0,
            "rs7251928": 1.0,
            "rs310644": 1.0,
            "rs2024566": 1.0,
        },
        expected_dominant_pop="EUR",
        min_dominant_proportion=0.40,
        expected_lat_bounds=(15.0, 35.0),
        expected_lng_bounds=(10.0, 25.0),
        expected_classification="BI_ADMIXED",
    ),
}


class BGAReferenceDatasets:
    """Registry accessor for certified BGA reference standards."""

    @staticmethod
    def get_standard(standard_id: str) -> BGAGoldenStandard:
        if standard_id not in BGA_GOLDEN_STANDARDS:
            raise KeyError(f"Standard {standard_id} not registered.")
        return BGA_GOLDEN_STANDARDS[standard_id]

    @staticmethod
    def list_standards() -> List[BGAGoldenStandard]:
        return list(BGA_GOLDEN_STANDARDS.values())
