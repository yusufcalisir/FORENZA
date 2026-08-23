"""
Unit Tests for Liftover Normalization and Quality Control.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import (
    GenotypeStateEnum,
    PlatformFormatEnum
)
from backend.node.services.forensic.genomics.fgg.liftover_normalizer import LiftoverNormalizer
from backend.node.services.forensic.genomics.fgg.qc_engine import FGGQCEngine


class TestFGGLiftoverAndQC:
    """Tests coordinate mapping and quality control metrics."""

    def test_chromosome_normalization(self):
        assert LiftoverNormalizer.normalize_chromosome("chr1") == "1"
        assert LiftoverNormalizer.normalize_chromosome("CHR22") == "22"
        assert LiftoverNormalizer.normalize_chromosome("chrX") == "X"
        assert LiftoverNormalizer.normalize_chromosome("23") == "X"
        assert LiftoverNormalizer.normalize_chromosome("chrY") == "Y"
        assert LiftoverNormalizer.normalize_chromosome("chrM") == "MT"
        assert LiftoverNormalizer.normalize_chromosome("invalid_chr") is None

    def test_genotype_call_normalization(self):
        assert LiftoverNormalizer.normalize_genotype_call("AA") == ("A", "A", "AA")
        assert LiftoverNormalizer.normalize_genotype_call("TC") == ("C", "T", "CT") # Alphabetically sorted
        assert LiftoverNormalizer.normalize_genotype_call("A/G") == ("A", "G", "AG")
        assert LiftoverNormalizer.normalize_genotype_call("--") == ("-", "-", "--")
        assert LiftoverNormalizer.normalize_genotype_call("00") == ("-", "-", "--")
        assert LiftoverNormalizer.normalize_genotype_call("./.") == ("-", "-", "--")

    def test_qc_engine_pristine_profile(self):
        # 98 called (20 het), 2 missing -> 98% call rate (Valid >= 95%)
        states = [GenotypeStateEnum.HOM_REF] * 78 + [GenotypeStateEnum.HET] * 20 + [GenotypeStateEnum.NO_CALL] * 2
        qc = FGGQCEngine.evaluate_profile_qc(states, PlatformFormatEnum.ILLUMINA_GSA)
        assert qc.total_snps_evaluated == 100
        assert qc.called_snps == 98
        assert qc.missing_snps == 2
        assert qc.call_rate_percentage == 98.0
        assert qc.is_call_rate_valid is True
        assert qc.degradation_warning is False
        assert qc.contamination_warning is False

    def test_qc_engine_degraded_touch_profile(self):
        # 85 called, 15 missing -> 85% call rate (Degraded < 90%)
        states = [GenotypeStateEnum.HOM_REF] * 65 + [GenotypeStateEnum.HET] * 20 + [GenotypeStateEnum.NO_CALL] * 15
        qc = FGGQCEngine.evaluate_profile_qc(states, PlatformFormatEnum.ILLUMINA_GDA)
        assert qc.call_rate_percentage == 85.0
        assert qc.is_call_rate_valid is False
        assert qc.degradation_warning is True

    def test_qc_engine_contamination_warning(self):
        # Excess heterozygosity (> 35%)
        states = [GenotypeStateEnum.HOM_REF] * 40 + [GenotypeStateEnum.HET] * 60
        qc = FGGQCEngine.evaluate_profile_qc(states, PlatformFormatEnum.TWENTY_THREE_AND_ME_V5)
        assert qc.heterozygosity_rate_percentage == 60.0
        assert qc.contamination_warning is True
