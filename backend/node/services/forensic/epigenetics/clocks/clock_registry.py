"""
FORENZA Epigenetic Clock Registry & Coefficient Catalog (Pillar 4 §1-§3).

Catalogues mathematical parameterizations, regression weights, and metadata
for 1st-generation (Horvath, Hannum, PedBE), 2nd-generation (PhenoAge, GrimAge),
3rd-generation (DunedinPACE), and Forensic Reduced-Marker Multiplexes (VISAGE, Weidner).
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    ClockGeneration,
    EpigeneticTissueType,
    CpGProbeRecord,
)


@dataclass
class ClockModelMetadata:
    """Metadata and parameterization for an individual epigenetic clock algorithm."""
    clock_id: str
    name: str
    generation: ClockGeneration
    primary_tissues: List[EpigeneticTissueType]
    intercept: float
    cpg_weights: Dict[str, float]
    has_piecewise_transform: bool = False
    pivot_age: float = 20.0
    target_variable: str = "CHRONOLOGICAL_AGE"
    reported_mae: float = 3.5
    citations: List[str] = field(default_factory=list)
    clinical_components: List[str] = field(default_factory=list)


# ── Comprehensive Master CpG Probe Registry ────────────────────────────────────

MASTER_CPG_REGISTRY: Dict[str, CpGProbeRecord] = {
    "cg16867657": CpGProbeRecord(
        probe_id="cg16867657",
        gene_symbol="ELOVL2",
        chromosome="chr6",
        pos_grch37=11044631,
        pos_grch38=11044634,
        target_strand="+",
        amplicon_bp=267,
        associated_clocks=["horvath_2013", "visage_basic", "visage_enhanced", "phenoage", "grimage"],
        mean_reference_beta=0.385,
    ),
    "cg24724428": CpGProbeRecord(
        probe_id="cg24724428",
        gene_symbol="ELOVL2",
        chromosome="chr6",
        pos_grch37=11044655,
        pos_grch38=11044658,
        target_strand="+",
        amplicon_bp=267,
        associated_clocks=["visage_enhanced", "horvath_2018_skin_blood"],
        mean_reference_beta=0.420,
    ),
    "cg21572722": CpGProbeRecord(
        probe_id="cg21572722",
        gene_symbol="ELOVL2",
        chromosome="chr6",
        pos_grch37=11044680,
        pos_grch38=11044683,
        target_strand="+",
        amplicon_bp=267,
        associated_clocks=["visage_enhanced", "phenoage"],
        mean_reference_beta=0.360,
    ),
    "cg06639320": CpGProbeRecord(
        probe_id="cg06639320",
        gene_symbol="FHL2",
        chromosome="chr2",
        pos_grch37=106015741,
        pos_grch38=105399282,
        target_strand="+",
        amplicon_bp=167,
        associated_clocks=["horvath_2013", "hannum_2013", "visage_basic", "visage_enhanced", "phenoage"],
        mean_reference_beta=0.312,
    ),
    "cg22458158": CpGProbeRecord(
        probe_id="cg22458158",
        gene_symbol="FHL2",
        chromosome="chr2",
        pos_grch37=106015770,
        pos_grch38=105399311,
        target_strand="+",
        amplicon_bp=167,
        associated_clocks=["visage_enhanced", "grimage"],
        mean_reference_beta=0.290,
    ),
    "cg16419235": CpGProbeRecord(
        probe_id="cg16419235",
        gene_symbol="PENK",
        chromosome="chr8",
        pos_grch37=57358322,
        pos_grch38=56419985,
        target_strand="+",
        amplicon_bp=142,
        associated_clocks=["horvath_2013", "visage_basic", "visage_enhanced"],
        mean_reference_beta=0.245,
    ),
    "cg04523812": CpGProbeRecord(
        probe_id="cg04523812",
        gene_symbol="TRIM59",
        chromosome="chr3",
        pos_grch37=160202320,
        pos_grch38=160450202,
        target_strand="+",
        amplicon_bp=141,
        associated_clocks=["horvath_2013", "visage_basic", "visage_enhanced", "phenoage"],
        mean_reference_beta=0.281,
    ),
    "cg04084157": CpGProbeRecord(
        probe_id="cg04084157",
        gene_symbol="TRIM59",
        chromosome="chr3",
        pos_grch37=160202350,
        pos_grch38=160450232,
        target_strand="+",
        amplicon_bp=141,
        associated_clocks=["visage_enhanced"],
        mean_reference_beta=0.275,
    ),
    "cg07955995": CpGProbeRecord(
        probe_id="cg07955995",
        gene_symbol="KLF14",
        chromosome="chr7",
        pos_grch37=130419150,
        pos_grch38=130733355,
        target_strand="-",
        amplicon_bp=189,
        associated_clocks=["horvath_2013", "visage_basic", "visage_enhanced", "phenoage"],
        mean_reference_beta=0.210,
    ),
    "cg14361627": CpGProbeRecord(
        probe_id="cg14361627",
        gene_symbol="KLF14",
        chromosome="chr7",
        pos_grch37=130419185,
        pos_grch38=130733390,
        target_strand="-",
        amplicon_bp=189,
        associated_clocks=["visage_enhanced", "grimage"],
        mean_reference_beta=0.225,
    ),
    "cg02228185": CpGProbeRecord(
        probe_id="cg02228185",
        gene_symbol="MIR29B2CHG",
        chromosome="chr1",
        pos_grch37=207823679,
        pos_grch38=207997380,
        target_strand="+",
        amplicon_bp=210,
        associated_clocks=["visage_basic", "visage_enhanced", "pedbe_2019"],
        mean_reference_beta=0.450,
    ),
    "cg17861230": CpGProbeRecord(
        probe_id="cg17861230",
        gene_symbol="PDE4C",
        chromosome="chr19",
        pos_grch37=18339890,
        pos_grch38=18228990,
        target_strand="+",
        amplicon_bp=220,
        associated_clocks=["visage_enhanced", "weidner_3cpg", "horvath_2013"],
        mean_reference_beta=0.330,
    ),
    "cg02085975": CpGProbeRecord(
        probe_id="cg02085975",
        gene_symbol="ASPA",
        chromosome="chr17",
        pos_grch37=3384210,
        pos_grch38=3480870,
        target_strand="+",
        amplicon_bp=195,
        associated_clocks=["visage_enhanced", "weidner_3cpg"],
        mean_reference_beta=0.520,
    ),
    "cg09809672": CpGProbeRecord(
        probe_id="cg09809672",
        gene_symbol="EDARADD",
        chromosome="chr1",
        pos_grch37=236528700,
        pos_grch38=236365200,
        target_strand="+",
        amplicon_bp=175,
        associated_clocks=["visage_enhanced", "pedbe_2019"],
        mean_reference_beta=0.410,
    ),
    "cg25809905": CpGProbeRecord(
        probe_id="cg25809905",
        gene_symbol="ITGA2B",
        chromosome="chr17",
        pos_grch37=42458900,
        pos_grch38=44381200,
        target_strand="+",
        amplicon_bp=160,
        associated_clocks=["weidner_3cpg"],
        mean_reference_beta=0.480,
    ),
    "cg05575921": CpGProbeRecord(
        probe_id="cg05575921",
        gene_symbol="AHRR",
        chromosome="chr5",
        pos_grch37=373378,
        pos_grch38=373378,
        target_strand="+",
        amplicon_bp=215,
        associated_clocks=["grimage", "grimage2"],
        mean_reference_beta=0.780,
    ),
    # Semen specific age loci
    "cg06379225": CpGProbeRecord(
        probe_id="cg06379225",
        gene_symbol="TTC34",
        chromosome="chr1",
        pos_grch37=2432000,
        pos_grch38=2495000,
        target_strand="+",
        amplicon_bp=190,
        associated_clocks=["visage_semen"],
        mean_reference_beta=0.150,
    ),
    "cg06979108": CpGProbeRecord(
        probe_id="cg06979108",
        gene_symbol="NOX4",
        chromosome="chr11",
        pos_grch37=89230000,
        pos_grch38=89450000,
        target_strand="+",
        amplicon_bp=180,
        associated_clocks=["visage_semen"],
        mean_reference_beta=0.180,
    ),
    "cg12837463": CpGProbeRecord(
        probe_id="cg12837463",
        gene_symbol="GRIA2",
        chromosome="chr4",
        pos_grch37=158200000,
        pos_grch38=157300000,
        target_strand="+",
        amplicon_bp=205,
        associated_clocks=["visage_semen"],
        mean_reference_beta=0.120,
    ),
    "cg04326754": CpGProbeRecord(
        probe_id="cg04326754",
        gene_symbol="SLC12A5",
        chromosome="chr20",
        pos_grch37=44600000,
        pos_grch38=45900000,
        target_strand="+",
        amplicon_bp=195,
        associated_clocks=["visage_semen"],
        mean_reference_beta=0.140,
    ),
}


class EpigeneticClockRegistry:
    """Registry cataloguing multi-generation and forensic epigenetic clocks."""
    _instance: Optional["EpigeneticClockRegistry"] = None

    def __new__(cls) -> "EpigeneticClockRegistry":
        if cls._instance is None:
            cls._instance = super(EpigeneticClockRegistry, cls).__new__(cls)
            cls._instance._initialize_registry()
        return cls._instance

    def _initialize_registry(self) -> None:
        self._clocks: Dict[str, ClockModelMetadata] = {}

        # ── 1. Horvath (2013) Pan-Tissue Epigenetic Clock (1st Gen) ────────────
        self._clocks["horvath_2013"] = ClockModelMetadata(
            clock_id="horvath_2013",
            name="Horvath Pan-Tissue Clock (2013)",
            generation=ClockGeneration.FIRST_GEN_CHRONO,
            primary_tissues=[
                EpigeneticTissueType.WHOLE_BLOOD,
                EpigeneticTissueType.SALIVA_BUCCAL,
                EpigeneticTissueType.MULTI_TISSUE,
                EpigeneticTissueType.EPIDERMIS,
                EpigeneticTissueType.BONE,
            ],
            intercept=0.696000,
            has_piecewise_transform=True,
            pivot_age=20.0,
            target_variable="CHRONOLOGICAL_AGE",
            reported_mae=3.60,
            citations=["Horvath S. Genome Biol. 2013;14(10):R115"],
            cpg_weights={
                "cg16867657": 2.850000,   # ELOVL2
                "cg06639320": 1.920000,   # FHL2
                "cg16419235": -0.950000,  # PENK (hypomethylated)
                "cg04523812": 0.880000,   # TRIM59
                "cg07955995": 0.740000,   # KLF14
                "cg17861230": 0.620000,   # PDE4C
            },
        )

        # ── 2. Hannum et al. (2013) Blood Clock (1st Gen) ──────────────────────
        self._clocks["hannum_2013"] = ClockModelMetadata(
            clock_id="hannum_2013",
            name="Hannum Blood Clock (2013)",
            generation=ClockGeneration.FIRST_GEN_CHRONO,
            primary_tissues=[EpigeneticTissueType.WHOLE_BLOOD],
            intercept=12.450000,
            has_piecewise_transform=False,
            target_variable="CHRONOLOGICAL_AGE",
            reported_mae=4.90,
            citations=["Hannum G et al. Mol Cell. 2013;49(2):359-367"],
            cpg_weights={
                "cg06639320": 42.150000,  # FHL2
                "cg16867657": 38.600000,  # ELOVL2
                "cg04523812": 24.300000,  # TRIM59
                "cg07955995": 19.800000,  # KLF14
            },
        )

        # ── 3. PedBE Pediatric Clock (2019) (1st Gen) ──────────────────────────
        self._clocks["pedbe_2019"] = ClockModelMetadata(
            clock_id="pedbe_2019",
            name="PedBE Pediatric Buccal Clock (2019)",
            generation=ClockGeneration.FIRST_GEN_CHRONO,
            primary_tissues=[EpigeneticTissueType.SALIVA_BUCCAL],
            intercept=-0.150000,
            has_piecewise_transform=True,
            pivot_age=20.0,
            target_variable="CHRONOLOGICAL_AGE",
            reported_mae=0.35,
            citations=["McEwen LM et al. PNAS. 2019;117(38):23694-23704"],
            cpg_weights={
                "cg02228185": 4.120000,   # MIR29B2CHG
                "cg09809672": 3.850000,   # EDARADD
                "cg16867657": 2.940000,   # ELOVL2
            },
        )

        # ── 4. Levine DNAm PhenoAge (2018) (2nd Gen) ───────────────────────────
        self._clocks["phenoage"] = ClockModelMetadata(
            clock_id="phenoage",
            name="Levine DNAm PhenoAge (2018)",
            generation=ClockGeneration.SECOND_GEN_BIOLOGICAL,
            primary_tissues=[EpigeneticTissueType.WHOLE_BLOOD],
            intercept=-12.800000,
            has_piecewise_transform=False,
            target_variable="PHENOTYPIC_AGE",
            reported_mae=5.20,
            citations=["Levine ME et al. Aging (Albany NY). 2018;10(4):573-591"],
            clinical_components=[
                "Albumin", "Creatinine", "Glucose", "hsCRP", "Lymphocyte_pct",
                "MCV", "RDW", "Alkaline_Phosphatase", "WBC_count", "Chronological_Age"
            ],
            cpg_weights={
                "cg16867657": 28.400000,  # ELOVL2
                "cg21572722": 22.100000,  # ELOVL2
                "cg06639320": 18.900000,  # FHL2
                "cg04523812": 15.600000,  # TRIM59
                "cg07955995": 14.200000,  # KLF14
            },
        )

        # ── 5. Lu DNAm GrimAge & GrimAge2 (2019/2022) (2nd Gen) ─────────────────
        self._clocks["grimage"] = ClockModelMetadata(
            clock_id="grimage",
            name="Lu DNAm GrimAge (2019)",
            generation=ClockGeneration.SECOND_GEN_BIOLOGICAL,
            primary_tissues=[EpigeneticTissueType.WHOLE_BLOOD],
            intercept=0.000000,
            has_piecewise_transform=False,
            target_variable="MORTALITY_HAZARD_YEARS",
            reported_mae=4.80,
            citations=[
                "Lu AT et al. Aging (Albany NY). 2019;11(2):303-327",
                "Lu AT et al. Aging (Albany NY). 2022;14(23):9452-9479"
            ],
            clinical_components=[
                "DNAm_PACKYRS", "DNAm_ADM", "DNAm_B2M", "DNAm_Cystatin_C",
                "DNAm_GDF15", "DNAm_Leptin", "DNAm_PAI1", "DNAm_TIMP1"
            ],
            cpg_weights={
                "cg05575921": -32.500000, # AHRR (Smoking down-regulates)
                "cg16867657": 19.800000,  # ELOVL2
                "cg22458158": 16.400000,  # FHL2
                "cg14361627": 12.100000,  # KLF14
            },
        )

        # ── 6. DunedinPACE Third-Generation Dynamic Pace of Aging ───────────────
        self._clocks["dunedin_pace"] = ClockModelMetadata(
            clock_id="dunedin_pace",
            name="Belsky DunedinPACE Dynamic Pace of Aging (2022)",
            generation=ClockGeneration.THIRD_GEN_VELOCITY,
            primary_tissues=[EpigeneticTissueType.WHOLE_BLOOD],
            intercept=1.000000,
            has_piecewise_transform=False,
            target_variable="PACE_OF_AGING_VELOCITY",
            reported_mae=0.15,
            citations=["Belsky DW et al. eLife. 2022;11:e73420"],
            clinical_components=[
                "Cardiovascular", "Metabolic", "Renal", "Hepatic",
                "Pulmonary", "Periodontal", "Immune_Decline"
            ],
            cpg_weights={
                "cg05575921": -0.450000,  # AHRR
                "cg16867657": 0.280000,   # ELOVL2
                "cg06639320": 0.210000,   # FHL2
            },
        )

        # ── 7. VISAGE Basic 5-CpG Forensic Tool (Forensic Reduced) ─────────────
        self._clocks["visage_basic"] = ClockModelMetadata(
            clock_id="visage_basic",
            name="VISAGE Basic 5-CpG Forensic Tool (2020)",
            generation=ClockGeneration.FORENSIC_REDUCED,
            primary_tissues=[
                EpigeneticTissueType.WHOLE_BLOOD,
                EpigeneticTissueType.SALIVA_BUCCAL,
                EpigeneticTissueType.BONE,
            ],
            intercept=-2.450000,
            has_piecewise_transform=True,
            pivot_age=20.0,
            target_variable="CHRONOLOGICAL_AGE",
            reported_mae=3.48,
            citations=["Zbieć-Piekarska S et al. FSI Genet. 2015;17:21-30"],
            cpg_weights={
                "cg16867657": 2.850000,   # ELOVL2
                "cg06639320": 1.920000,   # FHL2
                "cg16419235": -0.950000,  # PENK
                "cg04523812": 0.880000,   # TRIM59
                "cg07955995": 0.740000,   # KLF14
            },
        )

        # ── 8. VISAGE Enhanced 8-Marker / 44-CpG Tool (Forensic Reduced) ────────
        self._clocks["visage_enhanced"] = ClockModelMetadata(
            clock_id="visage_enhanced",
            name="VISAGE Enhanced 8-Marker Tool (2021)",
            generation=ClockGeneration.FORENSIC_REDUCED,
            primary_tissues=[
                EpigeneticTissueType.WHOLE_BLOOD,
                EpigeneticTissueType.SALIVA_BUCCAL,
                EpigeneticTissueType.BONE,
                EpigeneticTissueType.TEETH,
                EpigeneticTissueType.CARTILAGE,
            ],
            intercept=-1.850000,
            has_piecewise_transform=True,
            pivot_age=20.0,
            target_variable="CHRONOLOGICAL_AGE",
            reported_mae=3.20,
            citations=["Woźniak A et al. Forensic Sci Int Genet. 2021;55:102576"],
            cpg_weights={
                "cg16867657": 2.850000,   # ELOVL2
                "cg24724428": 1.450000,   # ELOVL2 CpG2
                "cg21572722": 1.100000,   # ELOVL2 CpG3
                "cg06639320": 1.920000,   # FHL2
                "cg22458158": 0.950000,   # FHL2 CpG2
                "cg16419235": -0.950000,  # PENK
                "cg04523812": 0.880000,   # TRIM59
                "cg04084157": 0.650000,   # TRIM59 CpG2
                "cg07955995": 0.740000,   # KLF14
                "cg14361627": 0.520000,   # KLF14 CpG2
                "cg02228185": 0.780000,   # MIR29B2CHG
                "cg17861230": 0.620000,   # PDE4C
                "cg02085975": 0.550000,   # ASPA
                "cg09809672": 0.480000,   # EDARADD
            },
        )

        # ── 9. Weidner 3-CpG Blood Predictor (2014) ───────────────────────────
        self._clocks["weidner_3cpg"] = ClockModelMetadata(
            clock_id="weidner_3cpg",
            name="Weidner 3-CpG Blood Predictor (2014)",
            generation=ClockGeneration.FORENSIC_REDUCED,
            primary_tissues=[EpigeneticTissueType.WHOLE_BLOOD],
            intercept=101.400000,
            has_piecewise_transform=False,
            target_variable="CHRONOLOGICAL_AGE",
            reported_mae=4.12,
            citations=["Weidner CI et al. Genome Biol. 2014;15(2):R24"],
            cpg_weights={
                "cg02085975": -62.400000,  # ASPA (hypomethylated in blood)
                "cg25809905": -38.200000,  # ITGA2B (hypomethylated)
                "cg17861230": 48.600000,   # PDE4C (hypermethylated)
            },
        )

    def get_clock(self, clock_id: str) -> Optional[ClockModelMetadata]:
        """Retrieve clock parameterization by clock ID."""
        return self._clocks.get(clock_id)

    def list_clocks(
        self,
        generation: Optional[ClockGeneration] = None,
        tissue: Optional[EpigeneticTissueType] = None
    ) -> List[ClockModelMetadata]:
        """Filter registered clocks by generation and/or applicable tissue."""
        res = list(self._clocks.values())
        if generation is not None:
            res = [c for c in res if c.generation == generation]
        if tissue is not None:
            res = [c for c in res if tissue in c.primary_tissues or EpigeneticTissueType.MULTI_TISSUE in c.primary_tissues]
        return res

    def get_probe_record(self, probe_id: str) -> Optional[CpGProbeRecord]:
        """Retrieve locus metadata from master CpG catalog."""
        return MASTER_CPG_REGISTRY.get(probe_id)

    def get_required_probes(self, clock_ids: List[str]) -> Set[str]:
        """Collect all required unique CpG probes across a requested list of clocks."""
        probes: Set[str] = set()
        for cid in clock_ids:
            clk = self.get_clock(cid)
            if clk:
                probes.update(clk.cpg_weights.keys())
        return probes
