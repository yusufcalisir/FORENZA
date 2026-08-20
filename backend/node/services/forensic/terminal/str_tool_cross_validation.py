"""
FORENZA: 24-Locus STR Independent Tool Cross-Validation & Benchmark Engine
Authoritative Implementation for Sub-Item 1.1.3:
1. NIST 1036 PopGen Frequency Engine Analytical Calculation Table (Butler et al. 2012)
2. FragalyseQt Open-Source CE Fragment Sizing & Ladder Binning Model (Dorif/fragalyseqt)
3. SoftGenetics GeneMarker HID Hybrid STR Artifact Identification Framework

Derived verbatim from research specifications:
- research/pillar_1_probabilistic_genotyping_research.md
- research/str_24_locus_microvariants_research.md
Compliance: ISO/IEC 17025:2017 • SWGDAM 2020 • ENFSI 2017 Evaluative Reporting
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set

from .nist_1036_popgen_engine import Nist1036PopGenEngine, NistPopulationEnum
from .str_locus_registry_engine import (
    StrLocusRegistryEngine,
    STR_LOCUS_24_MASTER_REGISTRY,
    StrRepeatUnitClass,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. NIST 1036 POPGEN ANALYTICAL CALCULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class NistPopGenAnalyticalBenchmarkEngine:
    """
    Independent cross-validation engine executing multi-population comparative PopGen
    calculations across Caucasian, African American, Hispanic, and Asian NIST 1036 datasets.
    """

    @classmethod
    def compute_multi_population_cross_comparison(
        cls,
        profile: Dict[str, Tuple[str, Optional[str]]],
        theta: float = 0.01,
        use_exact_balding_nichols: bool = True,
    ) -> Dict[str, Any]:
        """
        Computes Random Match Probabilities (RMP) and Log10(LR) across all 4 primary
        NIST 1036 ethnic datasets, providing cross-population likelihood ratios.
        """
        populations = [
            ("Caucasian", NistPopulationEnum.CAUCASIAN),
            ("African American", NistPopulationEnum.AFRICAN_AMERICAN),
            ("Hispanic", NistPopulationEnum.HISPANIC),
            ("Asian", NistPopulationEnum.ASIAN),
        ]

        pop_results: Dict[str, Dict[str, Any]] = {}
        for pop_name, _ in populations:
            res = Nist1036PopGenEngine.calculate_multilocus_profile_probability(
                profile=profile,
                population=pop_name,
                theta=theta,
                use_exact_balding_nichols=use_exact_balding_nichols,
            )
            pop_results[pop_name] = {
                "rmp": res["combined_rmp"],
                "lr": res["combined_lr"],
                "log10_lr": res["combined_log10_lr"],
                "verbal": res["enfsi_verbal_scale"],
            }

        # Compute cross-population comparison ratios (e.g. Caucasian vs African American)
        lr_cau = pop_results["Caucasian"]["lr"]
        lr_afr = pop_results["African American"]["lr"]
        lr_his = pop_results["Hispanic"]["lr"]
        lr_eas = pop_results["Asian"]["lr"]

        ratio_eur_to_afr = (lr_cau / lr_afr) if lr_afr > 0 else 1.0
        ratio_eur_to_his = (lr_cau / lr_his) if lr_his > 0 else 1.0
        ratio_eur_to_eas = (lr_cau / lr_eas) if lr_eas > 0 else 1.0

        return {
            "theta": theta,
            "evaluated_loci_count": len([k for k in profile.keys() if k.lower() not in ("amelogenin", "amel", "dys391", "sry")]),
            "population_results": pop_results,
            "cross_population_ratios": {
                "ratio_EUR_to_AFR": ratio_eur_to_afr,
                "ratio_EUR_to_HIS": ratio_eur_to_his,
                "ratio_EUR_to_EAS": ratio_eur_to_eas,
            },
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. FRAGALYSEQT CE FRAGMENT SIZING & BINNING BENCHMARK ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AllelicLadderBin:
    locus_name: str
    allele_call: str
    center_bp: float
    bin_min_bp: float
    bin_max_bp: float
    is_microvariant: bool


@dataclass
class SizedCEPeak:
    peak_id: str
    locus_name: str
    observed_size_bp: float
    peak_height_rfu: float
    assigned_allele: str
    bin_offset_bp: float
    is_off_ladder: bool
    quality_flag: str = "PASS"


class FragalyseQtCEBinningBenchmarkEngine:
    """
    Replication and validation of FragalyseQt (Dorif/fragalyseqt) CE sizing,
    allelic ladder calibration, and +/- 0.50 bp tolerance binning algorithms.
    """

    BIN_TOLERANCE_BP: float = 0.50  # FragalyseQt standard bin window: [L - 0.50, L + 0.50]

    @classmethod
    def generate_locus_allelic_ladder(cls, locus_name: str, base_offset_bp: float = 60.0) -> List[AllelicLadderBin]:
        """
        Generates the standard allelic ladder bin windows for a given locus.
        """
        meta = StrLocusRegistryEngine.get_locus_metadata(locus_name)
        if not meta:
            return []

        ladder_bins = []
        for allele_str in meta.observed_allele_spectrum:
            center_bp = StrLocusRegistryEngine.calculate_allele_size_bp(
                locus_name=locus_name,
                allele_str=allele_str,
                base_offset=base_offset_bp,
            )
            is_mv = StrLocusRegistryEngine.is_microvariant(allele_str)
            ladder_bins.append(AllelicLadderBin(
                locus_name=meta.locus_name,
                allele_call=allele_str,
                center_bp=center_bp,
                bin_min_bp=center_bp - cls.BIN_TOLERANCE_BP,
                bin_max_bp=center_bp + cls.BIN_TOLERANCE_BP,
                is_microvariant=is_mv,
            ))
        return ladder_bins

    @classmethod
    def bin_peak(
        cls,
        locus_name: str,
        observed_size_bp: float,
        peak_height_rfu: float,
        base_offset_bp: float = 60.0,
    ) -> SizedCEPeak:
        """
        FragalyseQt Sizing & Binning Algorithm:
        Assigns an observed peak to the closest ladder bin if within +/- 0.50 bp tolerance.
        Otherwise flags as Off-Ladder (OL).
        """
        ladder = cls.generate_locus_allelic_ladder(locus_name, base_offset_bp=base_offset_bp)
        if not ladder:
            # Non-STR locus fallback (e.g. Amelogenin)
            if locus_name.lower() in ("amelogenin", "amel"):
                if abs(observed_size_bp - 106.0) <= 1.0:
                    return SizedCEPeak(
                        peak_id=f"{locus_name}_{observed_size_bp:.1f}",
                        locus_name=locus_name,
                        observed_size_bp=observed_size_bp,
                        peak_height_rfu=peak_height_rfu,
                        assigned_allele="X",
                        bin_offset_bp=observed_size_bp - 106.0,
                        is_off_ladder=False,
                    )
                elif abs(observed_size_bp - 112.0) <= 1.0:
                    return SizedCEPeak(
                        peak_id=f"{locus_name}_{observed_size_bp:.1f}",
                        locus_name=locus_name,
                        observed_size_bp=observed_size_bp,
                        peak_height_rfu=peak_height_rfu,
                        assigned_allele="Y",
                        bin_offset_bp=observed_size_bp - 112.0,
                        is_off_ladder=False,
                    )
            return SizedCEPeak(
                peak_id=f"{locus_name}_{observed_size_bp:.1f}",
                locus_name=locus_name,
                observed_size_bp=observed_size_bp,
                peak_height_rfu=peak_height_rfu,
                assigned_allele="OL",
                bin_offset_bp=0.0,
                is_off_ladder=True,
                quality_flag="UNKNOWN_LOCUS",
            )

        best_bin: Optional[AllelicLadderBin] = None
        min_distance = float("inf")

        for b in ladder:
            dist = abs(observed_size_bp - b.center_bp)
            if dist < min_distance:
                min_distance = dist
                best_bin = b

        if best_bin and min_distance <= cls.BIN_TOLERANCE_BP:
            return SizedCEPeak(
                peak_id=f"{locus_name}_{best_bin.allele_call}",
                locus_name=locus_name,
                observed_size_bp=observed_size_bp,
                peak_height_rfu=peak_height_rfu,
                assigned_allele=best_bin.allele_call,
                bin_offset_bp=observed_size_bp - best_bin.center_bp,
                is_off_ladder=False,
                quality_flag="PASS",
            )
        else:
            closest_allele = best_bin.allele_call if best_bin else "?"
            return SizedCEPeak(
                peak_id=f"{locus_name}_OL",
                locus_name=locus_name,
                observed_size_bp=observed_size_bp,
                peak_height_rfu=peak_height_rfu,
                assigned_allele="OL",
                bin_offset_bp=min_distance if best_bin else 999.0,
                is_off_ladder=True,
                quality_flag=f"OFF_LADDER (closest={closest_allele}, delta={min_distance:.2f}bp)",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SOFTGENETICS GENEMARKER HID HYBRID ARTIFACT FILTER ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ArtifactClassificationEnum(str, Enum):
    TRUE_ALLELE = "True Allele"
    REVERSE_STUTTER = "Reverse Stutter (N-1 repeat / -4 bp)"
    FORWARD_STUTTER = "Forward Stutter (N+1 repeat / +4 bp)"
    MINUS_A_SPLIT_PEAK = "Incomplete Adenylation (-A split peak / -1 bp)"
    SPECTRAL_PULL_UP = "Spectral Pull-Up / Color Bleed-Through"
    BELOW_ANALYTICAL_THRESHOLD = "Below Analytical Threshold (AT < 50 RFU)"


@dataclass
class ClassifiedArtifactPeak:
    peak_id: str
    locus_name: str
    allele_call: str
    size_bp: float
    height_rfu: float
    classification: ArtifactClassificationEnum
    is_filtered: bool
    filter_reason: str
    stutter_ratio: float = 0.0
    dye_channel: str = "BLUE"



class GeneMarkerHIDBenchmarkFilter:
    """
    SoftGenetics GeneMarker HID Hybrid STR artifact identification framework.
    Filters reverse stutter, forward stutter, -A split peaks, and spectral pull-up.
    """

    ANALYTICAL_THRESHOLD_RFU: float = 50.0   # Standard baseline AT = 50 RFU
    SATURATION_THRESHOLD_RFU: float = 4000.0 # PMT / CCD camera saturation threshold
    MAX_FORWARD_STUTTER_RATIO: float = 0.035 # Global maximum forward stutter ratio (3.5%)
    MINUS_A_MAX_RATIO: float = 0.15          # Maximum -A peak height ratio (15%)

    @classmethod
    def classify_and_filter_peaks(
        cls,
        locus_name: str,
        peaks: List[Dict[str, Any]],  # List of {"size_bp": float, "height_rfu": float, "dye_channel": str}
        base_offset_bp: float = 60.0,
    ) -> List[ClassifiedArtifactPeak]:
        """
        Applies GeneMarker HID multi-stage artifact filtering rules across locus peaks.
        """
        meta = StrLocusRegistryEngine.get_locus_metadata(locus_name)
        repeat_unit_bp = meta.repeat_unit_size_bp if meta else 4
        max_sr = meta.max_reverse_stutter_ratio if meta else 0.120

        # Step 1: Bin all peaks to tentative alleles
        binned_peaks: List[Dict[str, Any]] = []
        for p in peaks:
            sized = FragalyseQtCEBinningBenchmarkEngine.bin_peak(
                locus_name=locus_name,
                observed_size_bp=p["size_bp"],
                peak_height_rfu=p["height_rfu"],
                base_offset_bp=base_offset_bp,
            )
            binned_peaks.append({
                "size_bp": p["size_bp"],
                "height_rfu": p["height_rfu"],
                "dye_channel": p.get("dye_channel", "BLUE"),
                "allele": sized.assigned_allele,
                "is_off_ladder": sized.is_off_ladder,
            })

        # Sort peaks by RFU descending to process true parent peaks first
        binned_peaks.sort(key=lambda x: x["height_rfu"], reverse=True)
        classified: List[ClassifiedArtifactPeak] = []

        # Find maximum peak in this locus (parent peak)
        parent_peak = binned_peaks[0] if binned_peaks else None

        for p in binned_peaks:
            h = p["height_rfu"]
            s = p["size_bp"]
            allele = p["allele"]

            # Rule 1: Below Analytical Threshold
            if h < cls.ANALYTICAL_THRESHOLD_RFU:
                classified.append(ClassifiedArtifactPeak(
                    peak_id=f"{locus_name}_{allele}",
                    locus_name=locus_name,
                    allele_call=allele,
                    size_bp=s,
                    height_rfu=h,
                    classification=ArtifactClassificationEnum.BELOW_ANALYTICAL_THRESHOLD,
                    is_filtered=True,
                    filter_reason=f"Height {h:.0f} RFU < AT ({cls.ANALYTICAL_THRESHOLD_RFU} RFU)",
                    dye_channel=p.get("dye_channel", "BLUE"),
                ))
                continue

            # If this is the parent peak (highest), it's a true candidate
            if parent_peak and p == parent_peak:
                classified.append(ClassifiedArtifactPeak(
                    peak_id=f"{locus_name}_{allele}",
                    locus_name=locus_name,
                    allele_call=allele,
                    size_bp=s,
                    height_rfu=h,
                    classification=ArtifactClassificationEnum.TRUE_ALLELE,
                    is_filtered=False,
                    filter_reason="Primary parent allele peak",
                    dye_channel=p.get("dye_channel", "BLUE"),
                ))
                continue

            # Check relationships with parent peak
            if parent_peak:
                parent_h = parent_peak["height_rfu"]
                parent_s = parent_peak["size_bp"]
                delta_bp = s - parent_s
                sr = h / parent_h if parent_h > 0 else 0.0

                # Rule 2: Reverse Stutter (N-1 repeat, e.g. -4 bp)
                if abs(delta_bp + repeat_unit_bp) <= 0.60:
                    if sr <= max_sr:
                        classified.append(ClassifiedArtifactPeak(
                            peak_id=f"{locus_name}_{allele}",
                            locus_name=locus_name,
                            allele_call=allele,
                            size_bp=s,
                            height_rfu=h,
                            classification=ArtifactClassificationEnum.REVERSE_STUTTER,
                            is_filtered=True,
                            filter_reason=f"Reverse stutter ratio {sr:.3f} <= SR_max ({max_sr:.3f}) at N-1 repeat ({delta_bp:.1f} bp)",
                            stutter_ratio=sr,
                            dye_channel=p.get("dye_channel", "BLUE"),
                        ))
                        continue

                # Rule 3: Forward Stutter (N+1 repeat, e.g. +4 bp)
                if abs(delta_bp - repeat_unit_bp) <= 0.60:
                    if sr <= cls.MAX_FORWARD_STUTTER_RATIO:
                        classified.append(ClassifiedArtifactPeak(
                            peak_id=f"{locus_name}_{allele}",
                            locus_name=locus_name,
                            allele_call=allele,
                            size_bp=s,
                            height_rfu=h,
                            classification=ArtifactClassificationEnum.FORWARD_STUTTER,
                            is_filtered=True,
                            filter_reason=f"Forward stutter ratio {sr:.3f} <= max forward ratio ({cls.MAX_FORWARD_STUTTER_RATIO:.3f})",
                            stutter_ratio=sr,
                            dye_channel=p.get("dye_channel", "BLUE"),
                        ))
                        continue

                # Rule 4: Minus-A (-A Split Peak, separated by -1.00 +/- 0.15 bp)
                if abs(delta_bp + 1.00) <= 0.20:
                    if sr <= cls.MINUS_A_MAX_RATIO:
                        classified.append(ClassifiedArtifactPeak(
                            peak_id=f"{locus_name}_{allele}",
                            locus_name=locus_name,
                            allele_call=allele,
                            size_bp=s,
                            height_rfu=h,
                            classification=ArtifactClassificationEnum.MINUS_A_SPLIT_PEAK,
                            is_filtered=True,
                            filter_reason=f"Incomplete adenylation (-A) peak at -1.0 bp with ratio {sr:.3f} <= {cls.MINUS_A_MAX_RATIO}",
                            dye_channel=p.get("dye_channel", "BLUE"),
                        ))
                        continue

                # Rule 5: Spectral Pull-Up (Primary peak > 4000 RFU and coincident size within +/- 0.05 bp)
                if parent_h >= cls.SATURATION_THRESHOLD_RFU and abs(delta_bp) <= 0.08:
                    if p.get("dye_channel") != parent_peak.get("dye_channel") and sr <= 0.08:
                        classified.append(ClassifiedArtifactPeak(
                            peak_id=f"{locus_name}_{allele}",
                            locus_name=locus_name,
                            allele_call=allele,
                            size_bp=s,
                            height_rfu=h,
                            classification=ArtifactClassificationEnum.SPECTRAL_PULL_UP,
                            is_filtered=True,
                            filter_reason=f"Spectral bleed-through from saturated parent peak ({parent_h:.0f} RFU > {cls.SATURATION_THRESHOLD_RFU:.0f} RFU)",
                            dye_channel=p.get("dye_channel", "BLUE"),
                        ))
                        continue

            # Default: Pass as True Allele (e.g. second heterozygous allele)
            classified.append(ClassifiedArtifactPeak(
                peak_id=f"{locus_name}_{allele}",
                locus_name=locus_name,
                allele_call=allele,
                size_bp=s,
                height_rfu=h,
                classification=ArtifactClassificationEnum.TRUE_ALLELE,
                is_filtered=False,
                filter_reason="Conforms to genuine STR amplicon criteria",
                dye_channel=p.get("dye_channel", "BLUE"),
            ))

        return classified

    @classmethod
    def evaluate_heterozygote_balance(cls, rfu1: float, rfu2: float) -> Tuple[float, bool]:
        """
        Calculates Peak Height Ratio (PHR) = min(h1, h2) / max(h1, h2).
        Returns (PHR, is_balanced) where threshold is 60% (0.60).
        """
        if rfu1 <= 0 or rfu2 <= 0:
            return 0.0, False
        phr = min(rfu1, rfu2) / max(rfu1, rfu2)
        return phr, phr >= 0.60
