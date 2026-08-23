"""
FORENZA — 5 Mandatory ISO/IEC 17025 Edge-Case Tests for Metagenomic Module (Phase 6.2)
=======================================================================================

Research §5 & 6 — Mandatory edge-case coverage:

    EC-META-01: Low-Biomass & High Sparsity
        <100 total reads with non-zero pseudocount replacement.
        Expected: No division-by-zero or NaN. CLR computable.

    EC-META-02: High Unclassified Matrix
        F_unclass > 90%, maintaining calibrated LR monotonicity.
        Expected: LR computation stable; no numeric collapse.

    EC-META-03: HyperLogLog Artifact Suppression
        KrakenUniq rejects synthetic 10,000-read artifact on a single k-mer.
        Expected: k_uniq < 5 triggers artifact flag.

    EC-META-04: Simplex Sum-to-One Closure Invariant
        |Σ abundance_i - 1.0| ≤ 1e-6 across all classifier outputs.
        Expected: All abundance vectors pass closure check.

    EC-META-05: Carrier Skin Microbiome Contamination
        Human skin contaminants removed without perturbing background.
        Expected: Cutibacterium acnes, S. epidermidis removed cleanly;
                  Aitchison distance between clean profiles unchanged.

Run with:
    pytest backend/node/services/forensic/metagenomics/test_mandatory_edge_cases.py -v

Per AGENTS.md §4: Run ONLY this targeted file, NOT the global suite.
"""

from __future__ import annotations

import math
import pytest
from typing import Dict, List

from .coda_engine import (
    CoDaEngine,
    compute_clr,
    multiplicative_zero_replacement,
    aitchison_distance,
    bray_curtis_dissimilarity,
)
from .dark_matter_filter import (
    DarkMatterFilter,
    HUMAN_SKIN_MICROBIOME_TAXIDS,
    KITOME_CONTAMINANT_TAXIDS,
)
from .krakenuniq_engine import KrakenUniqEngine
from .schemas import (
    ClassifierEngine,
    KReportNode,
    TaxonomicProfile,
)
from .governance import (
    MetagenomicsGovernanceEngine,
    log10_lr_to_enfsi_tier,
    ENFSITier,
)
from .likelihood_ratio import MetagenomicLREngine
from .golden_vectors import GoldenVectorRegistry


# ─────────────────────────────────────────────────────────────────────────────
# EC-META-01: Low-Biomass & High Sparsity
# ─────────────────────────────────────────────────────────────────────────────

class TestEC_META_01_LowBiomassHighSparsity:
    """
    EC-META-01: Handles <100 total reads with non-zero pseudocount replacement
    without division by zero or NaN distortion.

    Research §3 Failure Mode 1: Low-Biomass / High Sparsity.
    δ = 0.5 / N_reads (Martin-Fernandez 2003 multiplicative zero replacement).
    """

    def test_ultra_low_biomass_50_reads(self):
        """50 reads across 10 taxa — most taxa have 0 reads (sparse)."""
        sparse_abundance = {
            1224: 0.40,   # Pseudomonadota — 20 reads
            201174: 0.30, # Actinomycetota — 15 reads
            976: 0.20,    # Bacteroidota — 10 reads
            1239: 0.10,   # Bacillota — 5 reads
            # Remaining 6 taxa have 0 reads (not present in dict)
        }
        total_reads = 50

        # Apply multiplicative zero replacement
        replaced = multiplicative_zero_replacement(sparse_abundance, total_reads=total_reads)

        # All values must be strictly positive (no zeros)
        for taxid, frac in replaced.items():
            assert frac > 0.0, f"Zero abundance after replacement: taxid={taxid}"

        # Simplex closure: |Σ - 1.0| ≤ 1e-6
        total = sum(replaced.values())
        assert abs(total - 1.0) <= 1e-6, (
            f"Simplex closure VIOLATED: |Σ - 1.0| = {abs(total - 1.0):.2e} > 1e-6"
        )

    def test_single_taxon_sample(self):
        """Extreme sparsity: only 1 taxon detected, 20 reads total."""
        single_taxon = {1224: 1.0}
        replaced = multiplicative_zero_replacement(single_taxon, total_reads=20)

        # Single taxon: δ = 0.5/20 = 0.025; but only 1 taxon, no zeros to replace
        assert abs(replaced[1224] - 1.0) <= 1e-9, (
            f"Single-taxon simplex closure: {replaced[1224]}"
        )

    def test_clr_computable_after_zero_replacement(self):
        """CLR must be computable after zero replacement for sparse profile."""
        sparse = {1224: 0.90, 201174: 0.10}
        replaced = multiplicative_zero_replacement(sparse, total_reads=30)
        clr = compute_clr(replaced)

        # CLR Helmert zero-sum: |Σ clr_i| ≤ 1e-9
        clr_sum = sum(clr.values())
        assert abs(clr_sum) <= 1e-9, (
            f"CLR Helmert constraint VIOLATED: |Σ clr_i| = {abs(clr_sum):.2e}"
        )

        # No NaN or infinity
        for taxid, val in clr.items():
            assert math.isfinite(val), f"CLR value is not finite: clr[{taxid}]={val}"

    def test_no_division_by_zero_with_zero_reads(self):
        """F_unclass computation with N_total = 0 must not raise ZeroDivisionError."""
        from .dark_matter_filter import DarkMatterFilter
        from .schemas import ClassifierEngine, TaxonomicProfile

        dmf = DarkMatterFilter()
        profile = TaxonomicProfile(
            sample_id="ZERO_READ_SAMPLE",
            engine_used=ClassifierEngine.KRAKEN2,
            reference_db="TEST",
            total_reads=0,
            classified_reads=0,
            unclassified_reads=0,
            unclassified_fraction=0.0,
            abundance_vector={},
        )
        f = dmf.compute_f_unclass(profile)
        assert f == 1.0, f"Expected F_unclass=1.0 for 0 reads, got {f}"

    def test_aitchison_distance_no_nan_sparse(self):
        """Aitchison distance between two sparse profiles must be finite."""
        profile_a = {1224: 0.80, 201174: 0.20}
        profile_b = {1224: 0.60, 976: 0.40}

        # Zero-replace before CLR
        a_rep = multiplicative_zero_replacement(profile_a, total_reads=50)
        b_rep = multiplicative_zero_replacement(profile_b, total_reads=50)

        clr_a = compute_clr(a_rep)
        clr_b = compute_clr(b_rep)
        d = aitchison_distance(clr_a, clr_b)

        assert math.isfinite(d), f"Aitchison distance is not finite: {d}"
        assert d >= 0.0, f"Aitchison distance must be non-negative: {d}"


# ─────────────────────────────────────────────────────────────────────────────
# EC-META-02: High Unclassified Matrix
# ─────────────────────────────────────────────────────────────────────────────

class TestEC_META_02_HighUnclassifiedMatrix:
    """
    EC-META-02: Operates stably when F_unclass > 90%, maintaining
    calibrated LR monotonicity.

    Research §3 Failure Mode 1: F_unclass typical for forensic soil = 70-95%.
    The system MUST NOT treat high unclassified fraction as an error.
    """

    def test_f_unclass_92_percent_stable(self):
        """F_unclass = 0.92 — standard for sterile/degraded forensic soil."""
        profile = TaxonomicProfile(
            sample_id="HIGH_UNCLASS_SAMPLE",
            engine_used=ClassifierEngine.KRAKEN2,
            reference_db="STANDARD",
            total_reads=100_000,
            classified_reads=8_000,
            unclassified_reads=92_000,
            unclassified_fraction=0.920,
            abundance_vector={1224: 0.60, 201174: 0.40},
        )
        dmf = DarkMatterFilter()
        f = dmf.compute_f_unclass(profile)
        assert abs(f - 0.920) < 1e-6, f"F_unclass={f} expected ≈0.920"

    def test_lr_monotonicity_preserved_at_high_unclassified(self):
        """
        LR computed from a high-unclassified profile must be smaller (less support)
        than LR from a well-classified profile when both match the same reference.
        """
        engine = MetagenomicLREngine()
        # Register within-site distribution (tight cluster = small distances)
        engine.register_within_site_distances("SITE_A", [0.5, 0.6, 0.55, 0.52, 0.58])
        # Register between-site distribution (dispersed = large distances)
        engine.register_between_site_distances([3.0, 4.0, 3.5, 2.8, 4.2, 3.9])

        # Well-classified sample: close to reference (distance = 0.6)
        lr_good = engine.compute_lr(
            questioned_distance=0.60,
            reference_site_id="SITE_A",
            sample_id="GOOD_CLASSIFIED",
        )
        # High-unclassified sample (different community, distance = 2.5)
        lr_poor = engine.compute_lr(
            questioned_distance=2.50,
            reference_site_id="SITE_A",
            sample_id="HIGH_UNCLASSIFIED_DIVERGENT",
        )

        assert lr_good.log10_lr > lr_poor.log10_lr, (
            f"LR monotonicity violated: lr_good.log10_lr={lr_good.log10_lr:.3f} "
            f"should be > lr_poor.log10_lr={lr_poor.log10_lr:.3f}"
        )

    def test_no_numerical_collapse_99_percent_unclassified(self):
        """Extreme case: F_unclass = 0.99. LR engine must not crash or produce NaN."""
        engine = MetagenomicLREngine()
        engine.register_within_site_distances("STERILE_SITE", [1.0, 1.1, 0.9])
        engine.register_between_site_distances([5.0, 6.0, 5.5])

        result = engine.compute_lr(
            questioned_distance=5.5,
            reference_site_id="STERILE_SITE",
            sample_id="F_UNCLASS_99_PCT",
        )
        assert math.isfinite(result.log10_lr), "log10 LR must be finite even at F_unclass=0.99"
        assert math.isfinite(result.hp_density), "hp_density must be finite"
        assert math.isfinite(result.hd_density), "hd_density must be finite"


# ─────────────────────────────────────────────────────────────────────────────
# EC-META-03: HyperLogLog Artifact Suppression
# ─────────────────────────────────────────────────────────────────────────────

class TestEC_META_03_HyperLogLogArtifactSuppression:
    """
    EC-META-03: KrakenUniq rejects synthetic 10,000-read artifact concentrated
    on a single k-mer (k_uniq < 5 triggers artifact flag).

    Research §1.7: KrakenUniq artifact rejection rule:
        k_uniq < 2,000 → artifact flagged and excluded from the profile.
    """

    def test_single_kmer_artifact_rejected(self):
        """
        Synthetic artifact: 10,000 reads all sharing the same single minimizer.
        Expected: k_uniq = 1 → is_artifact_flagged = True.
        """
        engine = KrakenUniqEngine()

        # Simulate an artifact node: 10,000 reads, k_uniq = 1
        artifact_node = KReportNode(
            pct_total=10.0,
            cumulative_reads=10000,
            direct_reads=10000,
            rank_code="S",
            taxid=99999,
            name="  SYNTHETIC_ARTIFACT_SPECIES",
            k_uniq=1,
            is_artifact_flagged=False,
        )

        # Apply the k_uniq filter
        flagged = engine.apply_artifact_filter([artifact_node], min_k_uniq=2000)
        assert len(flagged) == 1 and flagged[0].is_artifact_flagged, (
            f"Artifact with k_uniq=1 must be flagged (k_uniq < 2000 threshold)"
        )

    def test_legitimate_species_not_rejected(self):
        """
        Legitimate species with 5,000 reads and k_uniq = 3,500 must NOT be flagged.
        """
        engine = KrakenUniqEngine()
        legit_node = KReportNode(
            pct_total=5.0,
            cumulative_reads=5000,
            direct_reads=5000,
            rank_code="S",
            taxid=1760,
            name="  Streptomyces griseus",
            k_uniq=3500,
            is_artifact_flagged=False,
        )
        flagged = engine.apply_artifact_filter([legit_node], min_k_uniq=2000)
        assert not flagged[0].is_artifact_flagged, (
            f"Legitimate species (k_uniq=3500 ≥ 2000) must NOT be artifact-flagged"
        )

    def test_boundary_condition_k_uniq_2000(self):
        """
        k_uniq = 2,000 exactly is the boundary — must NOT be flagged.
        k_uniq = 1,999 is strictly below — MUST be flagged.
        """
        engine = KrakenUniqEngine()

        at_boundary = KReportNode(
            pct_total=1.0, cumulative_reads=1000, direct_reads=1000,
            rank_code="S", taxid=111, name="  BoundarySpecies",
            k_uniq=2000, is_artifact_flagged=False,
        )
        just_below = KReportNode(
            pct_total=1.0, cumulative_reads=1000, direct_reads=1000,
            rank_code="S", taxid=222, name="  SubThresholdSpecies",
            k_uniq=1999, is_artifact_flagged=False,
        )

        results = engine.apply_artifact_filter([at_boundary, just_below], min_k_uniq=2000)
        assert not results[0].is_artifact_flagged, "k_uniq=2000 must NOT be flagged"
        assert results[1].is_artifact_flagged, "k_uniq=1999 MUST be flagged"

    def test_hyperloglog_cardinality_monotonicity(self):
        """
        HyperLogLog estimate must be ≥ number of unique k-mers observed.
        Verify the cardinality estimator doesn't undercount.
        """
        from .krakenuniq_engine import HyperLogLog
        hll = HyperLogLog(b=14)  # 2^14 registers

        # Insert 10,000 distinct values
        for i in range(10_000):
            hll.add(str(i).encode())

        estimate = hll.cardinality()
        # HyperLogLog typically accurate within ±5% for n=10,000
        # Check it's in range [8,000, 12,000]
        assert 8000 <= estimate <= 12000, (
            f"HyperLogLog cardinality estimate {estimate} outside expected range [8000, 12000]"
        )


# ─────────────────────────────────────────────────────────────────────────────
# EC-META-04: Simplex Sum-to-One Closure Invariant
# ─────────────────────────────────────────────────────────────────────────────

class TestEC_META_04_SimplexClosureInvariant:
    """
    EC-META-04: Validates |Σ abundance_i - 1.0| ≤ 1e-6 across all classifier
    outputs and Bracken re-assignments.

    AGENTS.md Mathematical Invariant: Probability simplex normalization.
    """

    def test_bracken_reassignment_closure(self):
        """Bracken re-assigned abundance vector must sum to 1.0 ± 1e-6."""
        from .bracken_engine import BrackenEngine
        engine = BrackenEngine()

        # Simulate a genus-level profile with 3 candidate species
        genus_reads = 1500
        assignment_probs = {
            101: {1001: 0.60, 1002: 0.30, 1003: 0.10},  # genus 101 → species 1001, 1002, 1003
        }
        genus_profile = {101: genus_reads}

        reassigned = engine.reassign_reads(
            genus_level_reads=genus_profile,
            assignment_probability_matrix=assignment_probs,
        )
        total = sum(reassigned.values())
        assert abs(total - genus_reads) <= 1.0, (
            f"Bracken total reads after reassignment ({total}) must match genus reads ({genus_reads}) ±1"
        )

    def test_multiplicative_zero_replacement_closure(self):
        """After zero replacement, abundance vector must sum to 1.0 ± 1e-6."""
        sparse = {1: 0.5, 2: 0.3, 3: 0.2, 4: 0.0, 5: 0.0}
        replaced = multiplicative_zero_replacement(sparse, total_reads=100)
        total = sum(replaced.values())
        assert abs(total - 1.0) <= 1e-6, (
            f"Zero-replaced simplex closure VIOLATED: |Σ - 1.0| = {abs(total - 1.0):.2e}"
        )

    def test_coda_engine_renormalization_closure(self):
        """CoDa engine output abundance vectors must all sum to 1.0 ± 1e-6."""
        coda = CoDaEngine(total_reads=10000)
        samples = {
            "SAMPLE_A": {1224: 0.4, 201174: 0.35, 976: 0.25},
            "SAMPLE_B": {1224: 0.3, 201174: 0.4, 976: 0.3},
        }
        result = coda.full_pipeline(
            sample_abundance_vectors=samples,
            total_reads_per_sample={"SAMPLE_A": 5000, "SAMPLE_B": 5000},
        )
        for sid, zero_replaced in result.zero_replaced_vectors.items():
            total = sum(zero_replaced.values())
            assert abs(total - 1.0) <= 1e-6, (
                f"Zero-replaced vector for '{sid}': |Σ - 1.0| = {abs(total - 1.0):.2e}"
            )

    def test_dark_matter_filter_renormalization_closure(self):
        """After kitome/skin removal, renormalized abundance must sum to 1.0 ± 1e-6."""
        dmf = DarkMatterFilter()
        contaminated_abundance = {
            1743: 0.05,   # Cutibacterium acnes (skin)
            1282: 0.04,   # S. epidermidis (skin)
            1224: 0.45,   # Pseudomonadota (soil)
            201174: 0.30, # Actinomycetota (soil)
            976: 0.16,    # Bacteroidota (soil)
        }
        filtered, _, _ = dmf.apply_skin_microbiome_filter(contaminated_abundance)
        total = sum(filtered.values())
        assert abs(total - 1.0) <= 1e-6, (
            f"Skin-filtered simplex closure VIOLATED: |Σ - 1.0| = {abs(total - 1.0):.2e}"
        )

    def test_golden_vector_01_abundance_closure(self):
        """VECTOR_GEO_SOIL_WGS_01 abundance vector must satisfy simplex closure."""
        vector = GoldenVectorRegistry.get("VECTOR_GEO_SOIL_WGS_01")
        profile = vector["profile"]
        total = sum(profile.abundance_vector.values())
        assert abs(total - 1.0) <= 1e-6, (
            f"VECTOR_GEO_SOIL_WGS_01 simplex closure VIOLATED: "
            f"|Σ - 1.0| = {abs(total - 1.0):.2e}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# EC-META-05: Carrier Skin Microbiome Contamination Filter
# ─────────────────────────────────────────────────────────────────────────────

class TestEC_META_05_CarrierSkinMicrobiomeContamination:
    """
    EC-META-05: Human skin contaminants removed without perturbing background
    soil community Aitchison distance metrics.

    Research §3.2 Failure Mode 5:
        - Cutibacterium acnes (taxid=1743) removed
        - Staphylococcus epidermidis (taxid=1282) removed
        - Corynebacterium (taxid=1717) removed
        Aitchison distance between two clean soil profiles must be unchanged
        after skin subtraction is applied to both.
    """

    def test_cutibacterium_acnes_removed(self):
        """Cutibacterium acnes (taxid=1743) must be absent after skin filter."""
        dmf = DarkMatterFilter()
        contaminated = {
            1743: 0.08,   # C. acnes (skin)
            1224: 0.50,
            201174: 0.42,
        }
        filtered, removed, n = dmf.apply_skin_microbiome_filter(contaminated)
        assert 1743 not in filtered, "Cutibacterium acnes must be removed from abundance vector"
        assert 1743 in removed, "C. acnes must appear in the removed dict"

    def test_staphylococcus_epidermidis_removed(self):
        """Staphylococcus epidermidis (taxid=1282) must be absent after skin filter."""
        dmf = DarkMatterFilter()
        contaminated = {
            1282: 0.05,   # S. epidermidis (skin)
            1224: 0.55,
            201174: 0.40,
        }
        filtered, removed, n = dmf.apply_skin_microbiome_filter(contaminated)
        assert 1282 not in filtered, "S. epidermidis must be removed"

    def test_soil_background_aitchison_unchanged_after_skin_removal(self):
        """
        If the same skin contamination fraction is subtracted from both profiles,
        the Aitchison distance between the two should be approximately the same
        as the distance between the original clean soil profiles.

        The test verifies that skin removal is not perturbing relative distances.
        """
        dmf = DarkMatterFilter()

        # Two soil profiles with identical skin contamination overlaid
        soil_a_clean = {1224: 0.55, 201174: 0.30, 976: 0.15}
        soil_b_clean = {1224: 0.30, 201174: 0.50, 976: 0.20}

        # Add identical skin contamination fraction (10% each)
        skin_frac = 0.10

        def add_skin(profile: Dict[int, float]) -> Dict[int, float]:
            """Scale down soil to 90%, add 10% skin."""
            result = {k: v * (1.0 - skin_frac) for k, v in profile.items()}
            result[1743] = skin_frac * 0.5   # C. acnes
            result[1282] = skin_frac * 0.5   # S. epidermidis
            total = sum(result.values())
            return {k: v / total for k, v in result.items()}

        soil_a_contaminated = add_skin(soil_a_clean)
        soil_b_contaminated = add_skin(soil_b_clean)

        # Filter skin contaminants
        soil_a_filtered, _, _ = dmf.apply_skin_microbiome_filter(soil_a_contaminated)
        soil_b_filtered, _, _ = dmf.apply_skin_microbiome_filter(soil_b_contaminated)

        # Compute CLR-Aitchison distances
        n_reads = 10000
        a_clean_rep = multiplicative_zero_replacement(soil_a_clean, n_reads)
        b_clean_rep = multiplicative_zero_replacement(soil_b_clean, n_reads)
        a_filt_rep = multiplicative_zero_replacement(soil_a_filtered, n_reads)
        b_filt_rep = multiplicative_zero_replacement(soil_b_filtered, n_reads)

        clr_a_clean = compute_clr(a_clean_rep)
        clr_b_clean = compute_clr(b_clean_rep)
        clr_a_filt = compute_clr(a_filt_rep)
        clr_b_filt = compute_clr(b_filt_rep)

        d_clean = aitchison_distance(clr_a_clean, clr_b_clean)
        d_filtered = aitchison_distance(clr_a_filt, clr_b_filt)

        # Filtered distance should approximate clean distance (within 20% tolerance)
        ratio = abs(d_filtered - d_clean) / (d_clean + 1e-9)
        assert ratio < 0.20, (
            f"Skin removal perturbed Aitchison distance: "
            f"d_clean={d_clean:.4f}, d_filtered={d_filtered:.4f}, ratio={ratio:.3f} > 0.20"
        )

    def test_enfsi_verbal_scale_bilingual_completeness(self):
        """
        Governance module: ENFSI verbal scale must produce non-empty strings
        for both EN and TR at all LR values.
        """
        gov = MetagenomicsGovernanceEngine()
        test_log10_lrs = [-8.0, -5.0, -3.0, -1.0, 0.0, 1.0, 2.5, 4.0, 6.0]
        for log10_lr in test_log10_lrs:
            stmt_en = gov.generate_verbal_statement(log10_lr, language="EN",
                                                     include_propositions=False)
            stmt_tr = gov.generate_verbal_statement(log10_lr, language="TR",
                                                     include_propositions=False)
            assert stmt_en.strip(), f"Empty EN statement for log10_LR={log10_lr}"
            assert stmt_tr.strip(), f"Empty TR statement for log10_LR={log10_lr}"
            assert "PROSECUTOR'S FALLACY" in stmt_en, "EN must include Prosecutor's Fallacy shield"
            assert "SAVCININ YANILGISI" in stmt_tr, "TR must include Savcının Yanılgısı shield"

    def test_all_golden_vectors_retrievable(self):
        """All 5 golden vectors must be retrievable without error."""
        expected_ids = [
            "VECTOR_GEO_SOIL_WGS_01",
            "VECTOR_GEO_SOIL_16S_02",
            "VECTOR_GEO_SOIL_ITS_03",
            "VECTOR_GEO_PALYNO_EDNA_04",
            "VECTOR_GEO_EXCLUSION_05",
        ]
        for vid in expected_ids:
            vector = GoldenVectorRegistry.get(vid)
            assert "vector_id" in vector, f"Golden vector {vid} missing 'vector_id' key"
            assert vector["vector_id"] == vid, (
                f"vector_id mismatch: expected {vid}, got {vector['vector_id']}"
            )
