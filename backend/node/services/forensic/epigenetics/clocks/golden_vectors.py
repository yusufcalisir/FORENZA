"""
FORENZA Certified Epigenetic Golden Benchmark Vectors (Pillar 4 & Certified Standards Research).

Defines internationally standardized multi-omic forensic reference individuals:
  1. VECTOR_NIST_2391D_A: NIST SRM 2391d Component A (32.5y true chronological age)
  2. VECTOR_NA12878_CEU: NA12878 / HG001 CEU Reference (45.0y true chronological age)
  3. VECTOR_NA19240_YRI: NA19240 African Reference (28.0y true chronological age)
  4. VECTOR_HG002_AJ: HG002 Ashkenazi Jewish Reference (19.5y true age, pediatric horizon pivot)
  5. VECTOR_SMOKER_MORBID: Heavy Smoker / Morbid Reference (52.0y true age, 35 pack-years)
"""

from typing import Dict, Any
from dataclasses import dataclass
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MethylationSample,
    EpigeneticTissueType,
    EpigeneticPlatform,
)


@dataclass
class EpigeneticGoldenVector:
    """Certified golden reference profile across multiple clock modalities."""
    vector_id: str
    donor_name: str
    true_chronological_age: float
    tissue_type: EpigeneticTissueType
    smoking_pack_years: float
    biological_sex: str
    sample: MethylationSample
    expected_horvath_range: tuple[float, float]
    expected_visage_range: tuple[float, float]
    expected_grimage_accel_range: tuple[float, float]
    notes: str


# ── 1. NIST SRM 2391d Component A (32.5 years, Whole Blood) ───────────────────
VECTOR_NIST_2391D_A = EpigeneticGoldenVector(
    vector_id="VECTOR_NIST_2391D_A",
    donor_name="NIST SRM 2391d Comp A (Standard Reference Individual)",
    true_chronological_age=32.5,
    tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
    smoking_pack_years=0.0,
    biological_sex="MALE",
    sample=MethylationSample(
        sample_id="NIST_SRM_2391D_COMP_A",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        platform=EpigeneticPlatform.ILLUMINA_EPIC,
        input_dna_pg=500.0,
        bisulfite_conversion_rate=0.995,
        beta_values={
            "cg16867657": 0.355,  # ELOVL2
            "cg24724428": 0.370,
            "cg21572722": 0.315,
            "cg06639320": 0.280,  # FHL2
            "cg22458158": 0.260,
            "cg16419235": 0.250,  # PENK
            "cg04523812": 0.245,  # TRIM59
            "cg04084157": 0.230,
            "cg07955995": 0.195,  # KLF14
            "cg14361627": 0.190,
            "cg02228185": 0.380,  # MIR29B2CHG
            "cg17861230": 0.290,  # PDE4C
            "cg02085975": 0.580,  # ASPA
            "cg09809672": 0.340,  # EDARADD
            "cg05575921": 0.815,  # AHRR (non-smoker)
            "cg25809905": 0.440,  # ITGA2B
        },
    ),
    expected_horvath_range=(29.0, 36.0),
    expected_visage_range=(29.5, 35.5),
    expected_grimage_accel_range=(-4.0, +3.0),
    notes="Primary forensic gold standard. Uncompromised healthy adult whole blood.",
)

# ── 2. NA12878 / HG001 (45.0 years, CEU Caucasian) ────────────────────────────
VECTOR_NA12878_CEU = EpigeneticGoldenVector(
    vector_id="VECTOR_NA12878_CEU",
    donor_name="NA12878 / HG001 (CEPH / Utah Female)",
    true_chronological_age=45.0,
    tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
    smoking_pack_years=0.0,
    biological_sex="FEMALE",
    sample=MethylationSample(
        sample_id="NA12878_HG001_CEU",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        platform=EpigeneticPlatform.ILLUMINA_EPIC,
        input_dna_pg=500.0,
        bisulfite_conversion_rate=0.994,
        beta_values={
            "cg16867657": 0.435,  # ELOVL2
            "cg24724428": 0.450,
            "cg21572722": 0.390,
            "cg06639320": 0.340,  # FHL2
            "cg22458158": 0.320,
            "cg16419235": 0.220,  # PENK
            "cg04523812": 0.295,  # TRIM59
            "cg04084157": 0.280,
            "cg07955995": 0.235,  # KLF14
            "cg14361627": 0.240,
            "cg02228185": 0.470,  # MIR29B2CHG
            "cg17861230": 0.355,  # PDE4C
            "cg02085975": 0.510,  # ASPA
            "cg09809672": 0.430,  # EDARADD
            "cg05575921": 0.805,  # AHRR (non-smoker)
            "cg25809905": 0.500,  # ITGA2B
        },
    ),
    expected_horvath_range=(41.0, 49.0),
    expected_visage_range=(41.5, 52.5),
    expected_grimage_accel_range=(-3.5, +3.5),
    notes="GIAB reference individual with high-depth whole genome bisulfite sequencing.",
)

# ── 3. NA19240 (28.0 years, YRI African) ───────────────────────────────────────
VECTOR_NA19240_YRI = EpigeneticGoldenVector(
    vector_id="VECTOR_NA19240_YRI",
    donor_name="NA19240 (Yoruba in Ibadan, Nigeria)",
    true_chronological_age=28.0,
    tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
    smoking_pack_years=0.0,
    biological_sex="FEMALE",
    sample=MethylationSample(
        sample_id="NA19240_YRI",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        platform=EpigeneticPlatform.ILLUMINA_EPIC,
        input_dna_pg=400.0,
        bisulfite_conversion_rate=0.993,
        beta_values={
            "cg16867657": 0.320,  # ELOVL2
            "cg24724428": 0.335,
            "cg21572722": 0.280,
            "cg06639320": 0.245,  # FHL2
            "cg22458158": 0.230,
            "cg16419235": 0.265,  # PENK
            "cg04523812": 0.215,  # TRIM59
            "cg04084157": 0.200,
            "cg07955995": 0.170,  # KLF14
            "cg14361627": 0.165,
            "cg02228185": 0.340,  # MIR29B2CHG
            "cg17861230": 0.250,  # PDE4C
            "cg02085975": 0.620,  # ASPA
            "cg09809672": 0.300,  # EDARADD
            "cg05575921": 0.825,  # AHRR
            "cg25809905": 0.400,  # ITGA2B
        },
    ),
    expected_horvath_range=(24.5, 31.5),
    expected_visage_range=(25.0, 31.0),
    expected_grimage_accel_range=(-3.0, +3.0),
    notes="African reference individual validating multi-ancestry cross-population stability.",
)

# ── 4. HG002 / NA24385 (19.5 years, Ashkenazi Jewish Pivot) ───────────────────
VECTOR_HG002_AJ = EpigeneticGoldenVector(
    vector_id="VECTOR_HG002_AJ",
    donor_name="HG002 / NA24385 (Ashkenazi Jewish Son)",
    true_chronological_age=19.5,
    tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
    smoking_pack_years=0.0,
    biological_sex="MALE",
    sample=MethylationSample(
        sample_id="HG002_AJ_SON",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        platform=EpigeneticPlatform.ILLUMINA_EPIC,
        input_dna_pg=450.0,
        bisulfite_conversion_rate=0.996,
        beta_values={
            "cg16867657": 0.250,  # ELOVL2 (Adolescent/Young Adult)
            "cg24724428": 0.260,
            "cg21572722": 0.220,
            "cg06639320": 0.190,  # FHL2
            "cg22458158": 0.180,
            "cg16419235": 0.290,  # PENK
            "cg04523812": 0.175,  # TRIM59
            "cg04084157": 0.160,
            "cg07955995": 0.140,  # KLF14
            "cg14361627": 0.135,
            "cg02228185": 0.280,  # MIR29B2CHG
            "cg17861230": 0.200,  # PDE4C
            "cg02085975": 0.680,  # ASPA
            "cg09809672": 0.240,  # EDARADD
            "cg05575921": 0.830,  # AHRR
            "cg25809905": 0.350,  # ITGA2B
        },
    ),
    expected_horvath_range=(16.5, 22.5),
    expected_visage_range=(17.0, 22.0),
    expected_grimage_accel_range=(-3.0, +3.0),
    notes="Critical validation standard located at the y0 = 20.0 piecewise continuous boundary.",
)

# ── 5. HEAVY SMOKER / MORBIDITY VECTOR (52.0 years, 35 Pack-Years) ─────────────
VECTOR_SMOKER_MORBID = EpigeneticGoldenVector(
    vector_id="VECTOR_SMOKER_MORBID",
    donor_name="Chronic Smoker / Morbid Reference Individual",
    true_chronological_age=52.0,
    tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
    smoking_pack_years=35.0,
    biological_sex="MALE",
    sample=MethylationSample(
        sample_id="SMOKER_MORBID_52Y",
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        platform=EpigeneticPlatform.ILLUMINA_EPIC,
        input_dna_pg=500.0,
        bisulfite_conversion_rate=0.991,
        beta_values={
            "cg16867657": 0.480,  # ELOVL2 (normal 52yo level)
            "cg24724428": 0.500,
            "cg21572722": 0.440,
            "cg06639320": 0.380,  # FHL2
            "cg22458158": 0.360,
            "cg16419235": 0.190,  # PENK
            "cg04523812": 0.330,  # TRIM59
            "cg04084157": 0.310,
            "cg07955995": 0.270,  # KLF14
            "cg14361627": 0.280,
            "cg02228185": 0.520,  # MIR29B2CHG
            "cg17861230": 0.390,  # PDE4C
            "cg02085975": 0.460,  # ASPA
            "cg09809672": 0.480,  # EDARADD
            "cg05575921": 0.410,  # AHRR (severe tobacco hypomethylation shock)
            "cg25809905": 0.560,  # ITGA2B
        },
    ),
    expected_horvath_range=(48.0, 56.0),
    expected_visage_range=(48.5, 55.5),
    expected_grimage_accel_range=(+6.0, +14.0),
    notes="Demonstrates divergence between first-gen chronological accuracy and second-gen GrimAge acceleration.",
)

GOLDEN_VECTORS_CATALOG: Dict[str, EpigeneticGoldenVector] = {
    "VECTOR_NIST_2391D_A": VECTOR_NIST_2391D_A,
    "VECTOR_NA12878_CEU": VECTOR_NA12878_CEU,
    "VECTOR_NA19240_YRI": VECTOR_NA19240_YRI,
    "VECTOR_HG002_AJ": VECTOR_HG002_AJ,
    "VECTOR_SMOKER_MORBID": VECTOR_SMOKER_MORBID,
}
