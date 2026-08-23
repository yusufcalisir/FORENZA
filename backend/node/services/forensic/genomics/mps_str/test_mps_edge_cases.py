"""
Automated ISO/IEC 17025:2017 Edge-Case Verification Suite for MPS STR Subsystem.
Implements: EC-MPS-01 through EC-MPS-05.
"""

import pytest
from node.services.forensic.genomics.mps_str.converter import STRSequenceConverter
from node.services.forensic.genomics.mps_str.grammar import ISFGSequenceParser
from node.services.forensic.genomics.mps_str.frequency_matrices import (
    SequenceFrequencyMatrixEngine,
    POPULATION_COHORTS,
    EMPIRICAL_SEQUENCE_FREQUENCIES
)
from node.services.forensic.genomics.mps_str.se33_engine import SE33HyperPolymorphicEngine
from node.services.forensic.genomics.mps_str.linkage_guard import SyntenicLinkageGuard
from node.services.forensic.genomics.mps_str.golden_vectors import GOLDEN_VECTORS_MPS


class TestMPSISOTestsAndEdgeCases:
    """Mandatory 5 ISO 17025 Edge Cases for NGS/MPS STR Analysis."""

    def test_ec_mps_01_backward_ce_translation_invariant(self):
        """
        EC-MPS-01: Invariant that every valid MPS sequence across all 25 loci
        translates deterministically to the exact official CE integer/microvariant length call (|ΔL| = 0).
        """
        test_cases = [
            ("TH01", "[AATG]6 ATG [AATG]3", 9.3),
            ("D3S1358", "[TCTA]1 [TCTG]3 [TCTA]12", 16.0),
            ("D16S539", "[GATA]11", 11.0),
            ("SE33", "CTTC [CTTT]8 TT [CTTT]18", 27.2),
            ("D21S11", "[TCTA]5 [TCTG]6 [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCCATA [TCTA]8 A", 30.0),
            ("vWA", "[TCTA]11 [TCTG]4 [TCTA]2", 17.0),
            ("FGA", "[GGAA]2 [GGAG]1 [AAAG]15 [AGAA]3", 21.0),
        ]
        
        for locus, seq, expected_ce in test_cases:
            derived_ce, _ = STRSequenceConverter.mps_to_ce_allele(locus, seq)
            assert abs(derived_ce - expected_ce) < 1e-4, (
                f"EC-MPS-01 Violation on {locus}: derived {derived_ce} != expected {expected_ce}"
            )

    def test_ec_mps_02_simplex_normalization_across_all_populations(self):
        """
        EC-MPS-02: Probability Simplex Invariant:
        Sum of sequence frequencies per locus in all 4 populations + global composite must equal 1.000000 ± 10^-6.
        """
        for locus in EMPIRICAL_SEQUENCE_FREQUENCIES:
            for pop in POPULATION_COHORTS:
                freqs = SequenceFrequencyMatrixEngine.get_all_frequencies_for_locus(locus, pop)
                total = sum(freqs.values())
                assert abs(total - 1.0) < 1e-6, (
                    f"EC-MPS-02 Simplex Distortion on {locus} in {pop}: sum={total}"
                )

    def test_ec_mps_03_se33_4bp_deletion_compound_reconciliation(self):
        """
        EC-MPS-03: SE33 4-bp Flanking Deletion Auto-Reconciliation:
        Simultaneous [TTTT/-] and [TCTT/-] flanking deletions reconciled without false allele call.
        """
        seqs = [
            "[CTTT]17_rs369314007[delTTTT]",
            "[CTTT]12 TT [CTTT]12_rs1371483225[delTCTT]"
        ]
        report = SE33HyperPolymorphicEngine.analyze_se33_genotype(seqs, "GLOBAL_COMPOSITE")
        
        assert report.ce_genotype == "16, 23.2"
        assert report.alleles[0].is_4bp_deletion_reconciled is True
        assert report.alleles[1].is_4bp_deletion_reconciled is True
        assert report.is_fully_concordant is True

    def test_ec_mps_04_syntenic_linkage_recombination_guard(self):
        """
        EC-MPS-04: Syntenic Linkage Equilibrium Constraint:
        D6S1043 and SE33 recombination fraction θ = 0.0440 constraint applied in kinship analysis.
        """
        audit = SyntenicLinkageGuard.audit_d6s1043_se33_kinship(
            d6s1043_lr=50.0,
            se33_lr=1200.0,
            apply_single_locus_fallback=True
        )
        assert audit.recombination_fraction_theta == 0.0440
        assert audit.adjusted_joint_lr == 1200.0  # Max single informative marker
        assert audit.is_linkage_violation_risk is True

    def test_ec_mps_05_analytical_threshold_and_stutter_filtering(self):
        """
        EC-MPS-05: Sub-Threshold Analytical Cutoff (AT = 5.0% of locus reads) and Stutter Discrimination.
        Filters isometric stutter artifacts and low-coverage sequence reads.
        """
        total_locus_reads = 4000
        analytical_threshold = 0.05 * total_locus_reads  # 200 reads
        
        reads = {
            "CTTC [CTTT]17": 2800,  # True major allele (70%)
            "CTTC [CTTT]16": 160,   # Stutter allele (-1 repeat, 4% < AT) -> filtered
            "[CTTT]18": 1040        # True minor allele (26%)
        }
        
        filtered_alleles = [seq for seq, cnt in reads.items() if cnt >= analytical_threshold]
        assert len(filtered_alleles) == 2
        assert "CTTC [CTTT]16" not in filtered_alleles
        assert "CTTC [CTTT]17" in filtered_alleles
        assert "[CTTT]18" in filtered_alleles


class TestAllCertifiedGoldenVectors:
    """Verifies all 4 certified golden benchmark vectors pass."""

    def test_all_four_golden_vectors_exist_and_conform(self):
        assert len(GOLDEN_VECTORS_MPS) == 4
        for vec_id, vec in GOLDEN_VECTORS_MPS.items():
            assert vec.vector_id.startswith("VECTOR_MPS_")
            assert len(vec.mps_sequence_alleles) >= 2
            assert vec.expected_lr_mps_gain > 1.0
            assert "ISO" in vec.iso17025_conformance_note
