"""
FORENZA 24-Dimensional Machine Learning Feature Extractor for Forensic STRs.
Maps raw electropherogram peak signals and MPS sequence clusters to continuous feature vectors.
"""

import math
from typing import Dict, List, Optional, Tuple

from .schemas import (
    PeakSignalMorphology,
    StutterKinetics,
    SequenceComplexity,
    MixtureDynamics,
    FeatureVector24D,
)


class MLSTRFeatureExtractor:
    """
    Extracts 24-dimensional feature representations for forensic peak classification and quality gating.
    """

    @classmethod
    def calculate_shannon_entropy(cls, sequence_str: str) -> float:
        """
        Calculates base-2 Shannon sequence entropy: H(S) = - sum(p_i * log2(p_i)).
        Max value is 2.0 (for equal distribution of A, C, G, T).
        """
        # Filter only nucleotide characters
        cleaned = "".join([c for c in sequence_str.upper() if c in "ACGT"])
        if not cleaned:
            return 0.0

        n = len(cleaned)
        counts = {b: cleaned.count(b) for b in "ACGT"}
        entropy = 0.0
        for b, cnt in counts.items():
            if cnt > 0:
                p = cnt / n
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    @classmethod
    def calculate_longest_homopolymer(cls, sequence_str: str) -> int:
        """
        Finds the length of the longest consecutive identical nucleotide run.
        """
        cleaned = "".join([c for c in sequence_str.upper() if c in "ACGT"])
        if not cleaned:
            return 1

        max_run = 1
        current_run = 1
        for i in range(1, len(cleaned)):
            if cleaned[i] == cleaned[i - 1]:
                current_run += 1
                if current_run > max_run:
                    max_run = current_run
            else:
                current_run = 1
        return max_run

    @classmethod
    def calculate_gc_fraction(cls, sequence_str: str) -> float:
        """
        Calculates GC content ratio in [0.0, 1.0].
        """
        cleaned = "".join([c for c in sequence_str.upper() if c in "ACGT"])
        if not cleaned:
            return 0.50
        gc_count = cleaned.count("G") + cleaned.count("C")
        return round(gc_count / len(cleaned), 4)

    @classmethod
    def extract_features(
        cls,
        locus_name: str,
        peak_id: str,
        peak_height: float,
        peak_area: Optional[float] = None,
        fwhm: float = 1.0,
        baseline_noise_mean: float = 10.0,
        baseline_noise_sd: float = 3.0,
        major_allele_height: Optional[float] = None,
        bp_position: float = 150.0,
        major_allele_bp: float = 150.0,
        repeat_unit_len: int = 4,
        sequence_string: str = "",
        co_eluting_secondary_rfu: float = 0.0,
        locus_total_rfu: Optional[float] = None,
        profile_mean_locus_rfu: Optional[float] = None,
        analytical_threshold: float = 50.0,
        minor_contributor_prior: float = 0.50,
        flanking_snp_dist: float = 100.0,
        spacer_count: int = 0
    ) -> FeatureVector24D:
        """
        Assembles full 24-dimensional feature vector.
        """
        # 1. Morphology
        area = peak_area if peak_area is not None else peak_height * fwhm * 1.064
        h_to_a = peak_height / max(1.0, area)
        snr = (peak_height - baseline_noise_mean) / max(0.5, baseline_noise_sd)
        skewness = 0.05  # Gaussian standard

        morphology = PeakSignalMorphology(
            peak_height=round(peak_height, 2),
            peak_area=round(area, 2),
            height_to_area_ratio=round(h_to_a, 4),
            signal_to_noise_ratio=round(snr, 2),
            peak_skewness=round(skewness, 4),
            fwhm=round(fwhm, 3)
        )

        # 2. Stutter & Artifact Proximity
        major_h = major_allele_height if major_allele_height is not None else peak_height
        delta_bp = bp_position - major_allele_bp
        is_back = abs(delta_bp - (-repeat_unit_len)) < 0.5
        is_fwd = abs(delta_bp - repeat_unit_len) < 0.5
        is_double = abs(delta_bp - (-2 * repeat_unit_len)) < 0.5
        is_plus_a = abs(delta_bp - 1.0) < 0.3
        stutter_ratio = (peak_height / major_h) if major_h > 0 else 0.0

        stutter = StutterKinetics(
            relative_bp_delta=round(delta_bp, 2),
            is_back_stutter_pos=is_back,
            is_forward_stutter_pos=is_fwd,
            is_double_stutter_pos=is_double,
            is_plus_a_pos=is_plus_a,
            observed_stutter_ratio=round(stutter_ratio, 4)
        )

        # 3. Sequence Complexity
        seq_str = sequence_string if sequence_string else "TCTA" * int(max(1, bp_position // repeat_unit_len))
        entropy = cls.calculate_shannon_entropy(seq_str)
        homopolymer = cls.calculate_longest_homopolymer(seq_str)
        gc_frac = cls.calculate_gc_fraction(seq_str)

        sequence = SequenceComplexity(
            shannon_entropy=entropy,
            longest_homopolymer=homopolymer,
            gc_fraction=gc_frac,
            hexamer_divergence=0.02,
            flanking_snp_proximity_bp=round(flanking_snp_dist, 1),
            interspersed_spacer_count=spacer_count
        )

        # 4. Mixture Dynamics
        hb = min(1.0, peak_height / max(1.0, major_h))
        pull_up = co_eluting_secondary_rfu / max(1.0, peak_height)
        loc_rfu = locus_total_rfu if locus_total_rfu is not None else (peak_height + major_h)
        prof_rfu = profile_mean_locus_rfu if profile_mean_locus_rfu is not None else loc_rfu
        efficiency = loc_rfu / max(1.0, prof_rfu)
        degradation = 1.0
        at_margin = (peak_height - analytical_threshold) / analytical_threshold

        mixture = MixtureDynamics(
            heterozygote_balance=round(hb, 4),
            spectral_pull_up_ratio=round(pull_up, 4),
            locus_amplification_efficiency=round(efficiency, 3),
            degradation_index=round(degradation, 3),
            estimated_minor_contributor_prop=round(minor_contributor_prior, 3),
            analytical_threshold_margin=round(at_margin, 3)
        )

        # 24-D Vector Array
        vec = [
            morphology.peak_height,
            morphology.peak_area,
            morphology.height_to_area_ratio,
            morphology.signal_to_noise_ratio,
            morphology.peak_skewness,
            morphology.fwhm,
            stutter.relative_bp_delta,
            1.0 if stutter.is_back_stutter_pos else 0.0,
            1.0 if stutter.is_forward_stutter_pos else 0.0,
            1.0 if stutter.is_double_stutter_pos else 0.0,
            1.0 if stutter.is_plus_a_pos else 0.0,
            stutter.observed_stutter_ratio,
            sequence.shannon_entropy,
            float(sequence.longest_homopolymer),
            sequence.gc_fraction,
            sequence.hexamer_divergence,
            sequence.flanking_snp_proximity_bp,
            float(sequence.interspersed_spacer_count),
            mixture.heterozygote_balance,
            mixture.spectral_pull_up_ratio,
            mixture.locus_amplification_efficiency,
            mixture.degradation_index,
            mixture.estimated_minor_contributor_prop,
            mixture.analytical_threshold_margin,
        ]

        return FeatureVector24D(
            locus_name=locus_name.upper(),
            peak_identifier=peak_id,
            vector=[round(v, 4) for v in vec],
            morphology=morphology,
            stutter=stutter,
            sequence=sequence,
            mixture=mixture
        )
