"""
Forensic DNA & SNP Terminal: Ingestion, Multi-Format Parsing & Biophysical Quality Engine.
Compliant with ISO/IEC 17025:2017, FBI CODIS NDIS v3.2/v4.0, and SWGDAM 2020 Guidelines.
"""

from .dna_terminal_parser import (
    DnaTerminalParser,
    ParsedForensicProfile,
    LocusSTRCall,
    SnpGenotypeCall,
    QualityAssessmentResult,
    SexDeterminationResult,
    SexClassificationEnum,
    PopGenMatchProbabilityResult,
    STR_PANEL_24_CATALOG,
    NIST_1036_SAMPLE_COUNT,
    NRC_II_P_MIN,
)

from .snp_phenotype_bga_engine import (
    SnpPhenotypeBgaEngine,
    ContinentalCluster,
    ContinentalReferencePoint,
    BgaPosteriorResult,
    HIrisPlexPhenotypeResult,
    CONTINENTAL_COORDINATES,
    AIM_55_ALLELE_FREQUENCIES,
)

from .epg_synthesis_engine import (
    EpgSynthesisEngine,
    DyeChannelEnum,
    LocusDyeMapping,
    EpgPeakAnnotation,
    EpgTracePoint,
    EpgSynthesizedTrace,
    EpgSynthesisResult,
    PANEL_24_LOCUS_MAPPING,
    LIZ_600_STANDARD_SIZES,
)

from .casework_presets import (
    CaseworkPresetExporter,
    CaseworkPresetItem,
    GOLDEN_CASEWORK_PRESETS,
    CERTIFIED_GLOBAL_REFERENCE_PRESETS,
    PRESET_NIST_SRM_2391D,
    PRESET_NA12878_CEU,
    PRESET_HG002_AJ,
    PRESET_NA19240_YRI,
    PRESET_NA18507_CHB,
    ForensicMultiOmicValidator,
)

from .cli_batch_parser import (
    ForensicCliBatchParser,
    ForensicCliLexer,
    CliSyntaxError,
    ExecutionMode,
    DomainPrefix,
    ParsedCommand,
)

__all__ = [
    "DnaTerminalParser",
    "ParsedForensicProfile",
    "LocusSTRCall",
    "SnpGenotypeCall",
    "QualityAssessmentResult",
    "SexDeterminationResult",
    "SexClassificationEnum",
    "PopGenMatchProbabilityResult",
    "STR_PANEL_24_CATALOG",
    "NIST_1036_SAMPLE_COUNT",
    "NRC_II_P_MIN",
    "SnpPhenotypeBgaEngine",
    "ContinentalCluster",
    "ContinentalReferencePoint",
    "BgaPosteriorResult",
    "HIrisPlexPhenotypeResult",
    "CONTINENTAL_COORDINATES",
    "AIM_55_ALLELE_FREQUENCIES",
    "EpgSynthesisEngine",
    "DyeChannelEnum",
    "LocusDyeMapping",
    "EpgPeakAnnotation",
    "EpgTracePoint",
    "EpgSynthesizedTrace",
    "EpgSynthesisResult",
    "PANEL_24_LOCUS_MAPPING",
    "LIZ_600_STANDARD_SIZES",
    "CaseworkPresetExporter",
    "CaseworkPresetItem",
    "GOLDEN_CASEWORK_PRESETS",
    "CERTIFIED_GLOBAL_REFERENCE_PRESETS",
    "PRESET_NIST_SRM_2391D",
    "PRESET_NA12878_CEU",
    "PRESET_HG002_AJ",
    "PRESET_NA19240_YRI",
    "PRESET_NA18507_CHB",
    "ForensicMultiOmicValidator",
    "ForensicCliBatchParser",
    "ForensicCliLexer",
    "CliSyntaxError",
    "ExecutionMode",
    "DomainPrefix",
    "ParsedCommand",
]


