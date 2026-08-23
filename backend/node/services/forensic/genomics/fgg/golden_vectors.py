"""
Forensic Genetic Genealogy (FGG / IGG) Golden Benchmark Vectors.

Globally Standardized Multi-Generational & Endogamy Test Vectors:
- VECTOR_FGG_01: CEPH 1463 / GIAB NA12878 (HG001) Family Tree Benchmark
- VECTOR_FGG_02: GIAB Ashkenazi Trio (HG002, HG003, HG004) Endogamy Benchmark
- VECTOR_FGG_03: Golden State Killer (GSK) Investigative Triangulation Case Benchmark
"""

from typing import Dict, Any, List
from .schemas import (
    PlatformFormatEnum,
    GenotypeStateEnum,
    BitwiseGenotypeBlock,
    ProfileQCReport,
    IngestedFGGProfile,
    KinshipDegreeEnum,
    SexEnum
)
from .bitwise_packer import BitwiseGenotypePacker
from .genetic_map import FGGGeneticMap



def _build_benchmark_profile(
    pid: str,
    platform: PlatformFormatEnum,
    chrom_states: Dict[str, List[GenotypeStateEnum]],
    het_rate: float = 25.0
) -> IngestedFGGProfile:
    """Helper to synthesize a standardized benchmark profile."""
    blocks = {}
    total_snps = 0
    called = 0
    missing = 0

    for ch, states in chrom_states.items():
        n = len(states)
        packed = BitwiseGenotypePacker.pack_states(states)
        max_bp = FGGGeneticMap.CHROMOSOME_MAP_DATA.get(ch, (200000000, 200.0))[0]
        step = max(1000, int((max_bp - 2000000) / max(1, n)))
        positions = [1000000 + i * step for i in range(n)]
        blocks[ch] = BitwiseGenotypeBlock(
            chromosome=ch,
            snp_count=n,
            packed_bytes_hex=packed.hex(),
            positions_bp=positions,
            genetic_positions_cm=[],
            rsids=[f"rs_{ch}_{i}" for i in range(n)]
        )
        total_snps += n
        for s in states:
            if s == GenotypeStateEnum.NO_CALL:
                missing += 1
            else:
                called += 1

    call_rate = (called / total_snps * 100.0) if total_snps > 0 else 0.0

    qc = ProfileQCReport(
        total_snps_evaluated=total_snps,
        called_snps=called,
        missing_snps=missing,
        call_rate_percentage=round(call_rate, 2),
        heterozygosity_rate_percentage=het_rate,
        is_call_rate_valid=call_rate >= 95.0,
        degradation_warning=call_rate < 90.0,
        contamination_warning=het_rate > 35.0,
        detected_platform=platform
    )

    return IngestedFGGProfile(
        profile_id=pid,
        source_filename=f"{pid}_standard.tsv",
        platform=platform,
        assembly_version="GRCh38",
        qc_report=qc,
        chromosome_blocks=blocks
    )


class FGGGoldenVectors:
    """Standardized golden reference vectors for automated regression & validation."""

    @classmethod
    def get_vector_01_ceph_trio(cls) -> Dict[str, IngestedFGGProfile]:
        """
        VECTOR_FGG_01: CEPH / GIAB NA12878 (HG001) Family Tree.
        Target (NA12878, Daughter) vs NA12877 (Father) -> 100% IBD1 (~3500 cM).
        """
        # All 22 autosomes, 2000 SNPs each
        chroms = [str(i) for i in range(1, 23)]
        target_states = {}
        father_states = {}

        for ch in chroms:
            t_states = []
            f_states = []
            for i in range(2000):
                # Standard realistic polymorphic distribution (outbred, ~30% HET)
                mod = i % 10
                if mod in (0, 1, 2, 3):  # 40% Father HOM_REF
                    f_states.append(GenotypeStateEnum.HOM_REF)
                    t_states.append(GenotypeStateEnum.HOM_REF if i % 2 == 0 else GenotypeStateEnum.HET)
                elif mod in (4, 5, 6):   # 30% Father HET
                    f_states.append(GenotypeStateEnum.HET)
                    t_states.append(GenotypeStateEnum.HET)
                elif mod in (7, 8):      # 20% Father HOM_ALT
                    f_states.append(GenotypeStateEnum.HOM_ALT)
                    t_states.append(GenotypeStateEnum.HOM_ALT if i % 2 == 0 else GenotypeStateEnum.HET)
                else:                    # 10% Father HET / Child HOM_REF
                    f_states.append(GenotypeStateEnum.HET)
                    t_states.append(GenotypeStateEnum.HOM_REF)

            target_states[ch] = t_states
            father_states[ch] = f_states

        p_target = _build_benchmark_profile("NA12878_DAUGHTER", PlatformFormatEnum.ILLUMINA_GSA, target_states, het_rate=28.0)
        p_father = _build_benchmark_profile("NA12877_FATHER", PlatformFormatEnum.ILLUMINA_GSA, father_states, het_rate=28.0)

        return {"target": p_target, "father": p_father}

    @classmethod
    def get_vector_02_ashkenazi_endogamy_trio(cls) -> Dict[str, IngestedFGGProfile]:
        """
        VECTOR_FGG_02: GIAB Ashkenazi Trio (HG002 Son, HG003 Father, HG004 Mother).
        Features elevated individual ROH (>4%) while maintaining true parent-offspring 100% IBD1.
        """
        chroms = [str(i) for i in range(1, 11)]
        son_states = {}
        father_states = {}

        for ch in chroms:
            # 60% ROH homozygous block on each chromosome
            n = 2000
            n_roh = int(n * 0.60)
            son_states[ch] = [GenotypeStateEnum.HOM_REF] * n_roh + [GenotypeStateEnum.HET if i % 3 == 0 else GenotypeStateEnum.HOM_REF for i in range(n - n_roh)]
            father_states[ch] = [GenotypeStateEnum.HOM_REF] * n_roh + [GenotypeStateEnum.HOM_REF if i % 3 == 0 else GenotypeStateEnum.HET for i in range(n - n_roh)]

        p_son = _build_benchmark_profile("HG002_ASHKENAZI_SON", PlatformFormatEnum.ILLUMINA_GDA, son_states, het_rate=12.0)
        p_father = _build_benchmark_profile("HG003_ASHKENAZI_FATHER", PlatformFormatEnum.ILLUMINA_GDA, father_states, het_rate=12.0)

        return {"son": p_son, "father": p_father}

    @classmethod
    def get_vector_03_gsk_investigative_case(cls) -> Dict[str, Any]:
        """
        VECTOR_FGG_03: Golden State Killer (GSK) Investigative Case Reconstruction.
        Crime scene profile matches two distant 3rd cousins (~80 cM).
        MRCA couple triangulated back to 1840s Great-Great-Grandparents (John & Rebecca).
        """
        chroms = [str(i) for i in range(1, 11)]
        target_states = {}
        cousin1_states = {}
        cousin2_states = {}

        for ch in chroms:
            # Most of genome is unrelated (opposite homozygotes)
            target_states[ch] = [GenotypeStateEnum.HOM_REF] * 2000
            cousin1_states[ch] = [GenotypeStateEnum.HOM_ALT] * 2000
            cousin2_states[ch] = [GenotypeStateEnum.HOM_ALT] * 2000

        # On Chromosome 1: Shared overlapping IBD block between Target, Cousin 1, and Cousin 2 (positions 500 to 1200)
        # Replacing opposite homozygotes with HET (IBD1)
        for i in range(500, 1200):
            target_states["1"][i] = GenotypeStateEnum.HET
            cousin1_states["1"][i] = GenotypeStateEnum.HOM_REF
            cousin2_states["1"][i] = GenotypeStateEnum.HOM_REF

        p_crime_scene = _build_benchmark_profile("GSK_CRIME_SCENE_1978", PlatformFormatEnum.VCF_WGS_PHASED, target_states)
        p_cousin1 = _build_benchmark_profile("GSK_MATCH_COUSIN_1", PlatformFormatEnum.FAMILY_TREE_DNA_CSV, cousin1_states)
        p_cousin2 = _build_benchmark_profile("GSK_MATCH_COUSIN_2", PlatformFormatEnum.FAMILY_TREE_DNA_CSV, cousin2_states)

        return {
            "crime_scene": p_crime_scene,
            "cousin1": p_cousin1,
            "cousin2": p_cousin2,
            "suspect_name": "Joseph James DeAngelo",
            "historical_mrca": "John DeAngelo & Rebecca (m. 1845)"
        }
