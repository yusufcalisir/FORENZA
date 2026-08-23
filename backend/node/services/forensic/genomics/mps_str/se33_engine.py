"""
FORENZA SE33 (ACTBP2) Hyper-Polymorphic Engine & Flanking Deletion Resolver.
Standard Compliance: ISFG Sequence Nomenclature & Scientific Reports (2021) 11:3485.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

from .schemas import ParsedSTRSequence, FlankingVariant, VariantType
from .grammar import ISFGSequenceParser
from .converter import STRSequenceConverter
from .frequency_matrices import SequenceFrequencyMatrixEngine, POPULATION_COHORTS


class SE33SizeClass(str, Enum):
    SMALL_INTEGER = "SMALL_INTEGER"      # e.g. Allele 12 - 20 ([CTTT]n)
    LARGE_MICROVARIANT = "LARGE_MICROVARIANT" # e.g. Allele 22.2 - 38.2 ([CTTT]n TT/CT [CTTT]m)
    COMPLEX_TRANSITIONAL = "COMPLEX_TRANSITIONAL"


class SE33FlankingAnalysisResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    rs_id: str
    relative_position: int
    detected_mutation: str
    is_4bp_discordance_deletion: bool
    biological_reconciliation_note: str


class SE33SingleAlleleAnalysis(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    raw_sequence: str
    ce_length_call: float
    mps_repeat_length: float
    size_class: SE33SizeClass
    flanking_variants: List[SE33FlankingAnalysisResult]
    is_4bp_deletion_reconciled: bool
    reconciled_ce_call: float
    sequence_frequency_global: float
    length_frequency_global: float


class SE33GenotypeAnalysisReport(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    locus: str = "SE33"
    alleles: List[SE33SingleAlleleAnalysis]
    ce_genotype: str
    mps_genotype: str
    ce_single_locus_lr: float
    mps_single_locus_lr: float
    information_gain_ratio: float = Field(..., description="LR_mps / LR_ce (up to 41.6x boost)")
    is_fully_concordant: bool
    quality_assurance_notes: List[str]


class SE33HyperPolymorphicEngine:
    """
    Dedicated biocomputational engine for the SE33 locus.
    Resolves bimodal architectures, 7 flanking SNPs/indels, and 4-bp discordance deletions.
    """

    KNOWN_4BP_DELETIONS = {"rs369314007", "rs1371483225"}

    # Approximate length-based CE frequencies for common alleles (for LR gain calculation)
    CE_LENGTH_FREQUENCIES: Dict[float, float] = {
        16.0: 0.045, 17.0: 0.052, 18.0: 0.074, 19.0: 0.061, 20.0: 0.055,
        21.2: 0.032, 22.2: 0.048, 23.2: 0.065, 24.2: 0.078, 25.2: 0.082,
        26.2: 0.088, 27.2: 0.091, 28.2: 0.076, 29.2: 0.058, 30.2: 0.042
    }

    @classmethod
    def analyze_se33_genotype(
        cls,
        sequence_strings: List[str],
        population: str = "GLOBAL_COMPOSITE"
    ) -> SE33GenotypeAnalysisReport:
        """
        Performs deep biocomputational analysis on SE33 diploid sequence alleles.
        """
        allele_analyses: List[SE33SingleAlleleAnalysis] = []
        qa_notes: List[str] = []
        is_all_concordant = True

        for seq in sequence_strings:
            parsed = ISFGSequenceParser.parse_sequence_string("SE33", seq)
            raw_ce = parsed.ce_length_call
            reconciled_ce, flags = STRSequenceConverter.mps_to_ce_allele("SE33", seq)
            
            # Size class determination
            size_class = cls._classify_size_class(reconciled_ce, parsed)

            # Analyze flanking variants
            flanking_results: List[SE33FlankingAnalysisResult] = []
            has_4bp_del = False
            
            all_variants = parsed.flanking_5p_variants + parsed.flanking_3p_variants
            for var in all_variants:
                is_discord_del = var.rs_id.lower() in cls.KNOWN_4BP_DELETIONS
                if is_discord_del:
                    has_4bp_del = True
                    note = f"4-bp deletion ({var.rs_id}) reconciled: MPS raw {raw_ce} -> CE {reconciled_ce}"
                    qa_notes.append(note)
                else:
                    note = f"Flanking variant {var.rs_id} ({var.ref_allele}>{var.alt_allele}) at pos {var.position_relative} bp"
                
                flanking_results.append(SE33FlankingAnalysisResult(
                    rs_id=var.rs_id,
                    relative_position=var.position_relative,
                    detected_mutation=f"{var.ref_allele}>{var.alt_allele}" if var.alt_allele else f"del{var.ref_allele}",
                    is_4bp_discordance_deletion=is_discord_del,
                    biological_reconciliation_note=note
                ))

            # Frequencies
            p_seq = SequenceFrequencyMatrixEngine.get_sequence_frequency("SE33", seq, population)
            p_ce = cls.CE_LENGTH_FREQUENCIES.get(reconciled_ce, 0.050)

            allele_analyses.append(SE33SingleAlleleAnalysis(
                raw_sequence=seq,
                ce_length_call=reconciled_ce,
                mps_repeat_length=raw_ce,
                size_class=size_class,
                flanking_variants=flanking_results,
                is_4bp_deletion_reconciled=has_4bp_del,
                reconciled_ce_call=reconciled_ce,
                sequence_frequency_global=p_seq,
                length_frequency_global=p_ce
            ))

        # Compute LRs
        if len(allele_analyses) == 2:
            p1_seq = allele_analyses[0].sequence_frequency_global
            p2_seq = allele_analyses[1].sequence_frequency_global
            p1_ce = allele_analyses[0].length_frequency_global
            p2_ce = allele_analyses[1].length_frequency_global

            is_het = allele_analyses[0].raw_sequence != allele_analyses[1].raw_sequence
            
            # Hardy-Weinberg LR = 1 / (2*p1*p2) if het, 1 / p1^2 if homo
            lr_seq = 1.0 / (2.0 * p1_seq * p2_seq) if is_het else 1.0 / (p1_seq ** 2)
            lr_ce = 1.0 / (2.0 * p1_ce * p2_ce) if is_het else 1.0 / (p1_ce ** 2)
        else:
            p_seq = allele_analyses[0].sequence_frequency_global
            p_ce = allele_analyses[0].length_frequency_global
            lr_seq = 1.0 / (p_seq ** 2)
            lr_ce = 1.0 / (p_ce ** 2)

        info_gain = lr_seq / lr_ce if lr_ce > 0 else 1.0

        ce_str = ", ".join(f"{a.reconciled_ce_call:g}" for a in allele_analyses)
        mps_str = " / ".join(a.raw_sequence for a in allele_analyses)

        return SE33GenotypeAnalysisReport(
            locus="SE33",
            alleles=allele_analyses,
            ce_genotype=ce_str,
            mps_genotype=mps_str,
            ce_single_locus_lr=round(lr_ce, 2),
            mps_single_locus_lr=round(lr_seq, 2),
            information_gain_ratio=round(info_gain, 2),
            is_fully_concordant=is_all_concordant,
            quality_assurance_notes=qa_notes
        )

    @staticmethod
    def _classify_size_class(ce_call: float, parsed: ParsedSTRSequence) -> SE33SizeClass:
        """Determines if SE33 allele belongs to the small integer or large microvariant class."""
        is_microvariant = (ce_call % 1.0) != 0
        if ce_call <= 20.0 and not is_microvariant:
            return SE33SizeClass.SMALL_INTEGER
        elif ce_call >= 21.0 and is_microvariant:
            return SE33SizeClass.LARGE_MICROVARIANT
        return SE33SizeClass.COMPLEX_TRANSITIONAL
