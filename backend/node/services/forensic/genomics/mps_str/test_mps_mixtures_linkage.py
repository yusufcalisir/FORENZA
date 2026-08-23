"""
Unit and Integration Tests for FORENZA MPS STR Mixture Deconvolution & Linkage Guard (Phase 4).
Validates Golden Vectors VECTOR_MPS_03 and VECTOR_MPS_04.
"""

import pytest
from node.services.forensic.genomics.mps_str.mixture_deconvolution import (
    MPSMixtureDeconvolutionEngine,
    DeconvolvedContributor
)
from node.services.forensic.genomics.mps_str.linkage_guard import (
    SyntenicLinkageGuard,
    SyntenicPairKinshipAudit,
    FlankingRescueReport
)


class TestMPSMixtureDeconvolution:
    """Tests isoallele deconvolution across complex mixtures (VECTOR_MPS_03)."""

    def test_vector_mps_03_mixture_isoallele_separation(self):
        # VECTOR_MPS_03: D3S1358 3-Person mixture
        # CE sees only alleles 15 and 16 (inconclusive collapsed 2-peak profile)
        # MPS uncovers 6 distinct isoalleles: 15a, 15b, 15c, 16a, 16b, etc.
        d3_seqs = [
            "[TCTA]1 [TCTG]3 [TCTA]11",  # 15a (Contrib 1)
            "[TCTA]1 [TCTG]2 [TCTA]12",  # 15b (Contrib 2)
            "[TCTA]2 [TCTG]3 [TCTA]10",  # 15c (Contrib 3)
            "[TCTA]1 [TCTG]3 [TCTA]12",  # 16a (Contrib 1)
            "[TCTA]1 [TCTG]4 [TCTA]11",  # 16b (Contrib 2)
        ]
        res = MPSMixtureDeconvolutionEngine.deconvolve_locus_mixture(
            "D3S1358",
            d3_seqs,
            population="GLOBAL_COMPOSITE"
        )
        
        assert res.ce_masked_state is True
        assert len(res.observed_ce_alleles) == 2  # Only CE calls 15, 16
        assert len(res.observed_sequence_alleles) == 5  # 5 distinct sequence alleles
        assert res.isoallele_expansion_count == 3  # +3 isoalleles beyond CE
        assert res.locus_log10_lr_mps > res.locus_log10_lr_ce

    def test_multi_locus_mixture_deconvolution_report(self):
        locus_map = {
            "D3S1358": [
                "[TCTA]1 [TCTG]3 [TCTA]11",
                "[TCTA]1 [TCTG]3 [TCTA]12"
            ],
            "TH01": [
                "[AATG]6",
                "[AATG]7",
                "[AATG]6 ATG [AATG]3"  # 9.3
            ]
        }
        contribs = [
            DeconvolvedContributor(
                contributor_id="CONTRIBUTOR_A",
                mixture_proportion=0.60,
                assigned_alleles=["[TCTA]1 [TCTG]3 [TCTA]11", "[AATG]6"],
                ce_equivalent_alleles=[15.0, 6.0]
            ),
            DeconvolvedContributor(
                contributor_id="CONTRIBUTOR_B",
                mixture_proportion=0.40,
                assigned_alleles=["[TCTA]1 [TCTG]3 [TCTA]12", "[AATG]7"],
                ce_equivalent_alleles=[16.0, 7.0]
            )
        ]
        rep = MPSMixtureDeconvolutionEngine.deconvolve_multi_locus_mixture(
            "MIXTURE_CASEWORK_991",
            locus_map,
            contribs,
            "GLOBAL_COMPOSITE"
        )
        
        assert rep.sample_id == "MIXTURE_CASEWORK_991"
        assert rep.num_contributors == 2
        assert len(rep.loci_deconvolutions) == 2
        assert "ENFSI" in rep.prosecutors_fallacy_shield_en
        assert "Savcının Yanılgısı" in rep.prosecutors_fallacy_shield_tr


class TestSyntenicLinkageGuard:
    """Tests D6S1043 - SE33 linkage audit and vWA mutation rescue (VECTOR_MPS_04)."""

    def test_d6s1043_se33_linkage_audit_fallback(self):
        # D6S1043 LR=150, SE33 LR=3200
        audit = SyntenicLinkageGuard.audit_d6s1043_se33_kinship(150.0, 3200.0, apply_single_locus_fallback=True)
        
        assert audit.is_linkage_violation_risk is True
        assert audit.recombination_fraction_theta == 0.0440
        assert audit.adjusted_joint_lr == 3200.0  # Falls back to more informative SE33
        assert "FALLBACK_TO_MORE_INFORMATIVE_LOCUS" in audit.action_taken

    def test_d6s1043_se33_linkage_audit_recombination_discount(self):
        audit = SyntenicLinkageGuard.audit_d6s1043_se33_kinship(100.0, 200.0, apply_single_locus_fallback=False)
        
        # Naive multiplication = 20,000. With discount, should be lower than naive product
        assert audit.adjusted_joint_lr < 20000.0
        assert "APPLIED_RECOMBINATION_DISCOUNT" in audit.action_taken

    def test_vector_mps_04_vwa_african_primer_mutation_rescue(self):
        # VECTOR_MPS_04: African-American vWA false homozygote rescue (rs771794429)
        apparent_ce = 14.0
        seqs = ["[TCTA]11 [TCTG]4 [TCTA]1"]  # Allele 14
        
        report = SyntenicLinkageGuard.rescue_vwa_african_primer_mutation(
            "AFRICAN_CASEWORK_SAMPLE_04",
            seqs,
            apparent_ce
        )
        
        assert report.is_rescued is True
        assert report.was_false_homozygote is True
        assert "rs771794429[G>A]" in report.detected_flanking_snp
        assert "AFRICAN_VWA_MUTATION_RESCUED" in report.qa_recommendation
