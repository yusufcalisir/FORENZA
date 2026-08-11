"""
FORENZA Evidence Image Analysis & Bloodstain Pattern Analysis (BPA) Engine.
Extracts stain morphometry (width W, length L), calculates trigonometric impact angle alpha = arcsin(W/L),
classifies spatter patterns, and enforces human-in-the-loop analyst verification protocols.

References:
  MacDonell MC (1971) Flight Characteristics and Stain Patterns of Human Blood.
  IABPA (2021) Scientific Working Group on Bloodstain Pattern Analysis Guidelines.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class BloodstainMorphometry:
    stain_id: str
    width_mm: float
    length_mm: float
    ellipse_aspect_ratio: float
    impact_angle_deg: float


@dataclass
class AnalystVerificationRecord:
    analyst_id: str
    verification_timestamp_utc: float
    decision: str                      # 'VERIFIED_BY_ANALYST', 'REJECTED'
    final_pattern_classification: str
    analyst_notes: str


@dataclass
class BpaAnalysisResult:
    stain_id: str
    morphometry: BloodstainMorphometry
    predicted_pattern: str             # 'PASSIVE_DROP', 'HIGH_VELOCITY_SPATTER', 'LOW_VELOCITY_SPATTER', 'CAST_OFF', 'WIPE_TRANSFER'
    review_status: str                 # 'PENDING_HUMAN_REVIEW', 'VERIFIED_BY_ANALYST', 'REJECTED'
    verification_record: Optional[AnalystVerificationRecord] = None
    bpa_summary: str = ""


class BloodstainPatternAnalyzer:
    """
    Computes trigonometric bloodstain impact angles and manages human analyst verification workflows.
    """

    def analyze_stain(self, stain_id: str, width_mm: float, length_mm: float) -> BpaAnalysisResult:
        if length_mm <= 0 or width_mm <= 0:
            raise ValueError("Stain dimensions width and length must be positive non-zero values.")

        w = min(width_mm, length_mm)
        l = max(width_mm, length_mm)

        aspect_ratio = round(w / l, 4)

        # Impact Angle alpha = arcsin(W / L) in degrees
        alpha_rad = math.asin(w / l)
        alpha_deg = round(math.degrees(alpha_rad), 2)

        morph = BloodstainMorphometry(
            stain_id=stain_id,
            width_mm=w,
            length_mm=l,
            ellipse_aspect_ratio=aspect_ratio,
            impact_angle_deg=alpha_deg
        )

        # Pattern classification heuristics
        if aspect_ratio >= 0.90:
            pattern = "PASSIVE_DROP"
        elif w < 1.5 and l < 3.0:
            pattern = "HIGH_VELOCITY_SPATTER"
        elif alpha_deg < 30.0:
            pattern = "CAST_OFF"
        else:
            pattern = "MEDIUM_VELOCITY_SPATTER"

        summary = (
            f"BPA Morphometry for {stain_id}: W={w}mm, L={l}mm -> "
            f"Impact Angle = {alpha_deg} deg ({pattern}). Status: PENDING_HUMAN_REVIEW."
        )

        return BpaAnalysisResult(
            stain_id=stain_id,
            morphometry=morph,
            predicted_pattern=pattern,
            review_status="PENDING_HUMAN_REVIEW",
            verification_record=None,
            bpa_summary=summary
        )

    def verify_analysis(
        self,
        analysis_result: BpaAnalysisResult,
        analyst_id: str,
        decision: str,
        final_pattern: str,
        analyst_notes: str,
        timestamp_utc: float
    ) -> BpaAnalysisResult:
        rec = AnalystVerificationRecord(
            analyst_id=analyst_id,
            verification_timestamp_utc=timestamp_utc,
            decision=decision,
            final_pattern_classification=final_pattern,
            analyst_notes=analyst_notes
        )

        analysis_result.review_status = decision
        analysis_result.predicted_pattern = final_pattern
        analysis_result.verification_record = rec
        analysis_result.bpa_summary = (
            f"BPA Analysis Certified by {analyst_id}: Status={decision}, "
            f"Final Pattern={final_pattern}."
        )

        return analysis_result
