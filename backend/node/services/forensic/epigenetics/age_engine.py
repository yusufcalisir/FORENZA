"""
FORENZA Forensic Epigenetic Age Estimation Engine (Multi-Tissue Elastic Net Model) — Module 16.

Implements verbatim from Pillar 4 Research §1 & §6:
  - §1.1 Horvath Piecewise Non-Linear Transformation Function (y0 = 20.0 pivot boundary)
  - §1.2 10 Key Predictive Forensic CpG Markers (ELOVL2, FHL2, PENK, TRIM59, KLF14, EDARADD, MIR29B2CHG, PDE4C, ASPA)
  - §1.3 Multi-Tissue Calibration Offsets (Blood, Saliva/Buccal, Semen, Bone/Teeth) & ISO 17025 95% Confidence Intervals
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union


# ── 10 Key Forensic CpG Markers & Empirical Weights (Research §1.2 & §6 Artifact A) ──

CPG_MARKER_METADATA = {
    "cg16867657": {"gene": "ELOVL2",     "weight": 102.45, "chrom": "chr6",  "pos": 11044631,  "default_beta": 0.25},
    "cg21572722": {"gene": "ELOVL2_2",   "weight": 88.12,  "chrom": "chr6",  "pos": 11044680,  "default_beta": 0.25},
    "cg06639320": {"gene": "FHL2",       "weight": 74.30,  "chrom": "chr2",  "pos": 106015741, "default_beta": 0.20},
    "cg16419235": {"gene": "PENK",       "weight": -45.20, "chrom": "chr8",  "pos": 57358322,  "default_beta": 0.30},
    "cg04084157": {"gene": "TRIM59",     "weight": 56.80,  "chrom": "chr3",  "pos": 160202320, "default_beta": 0.25},
    "cg08097417": {"gene": "KLF14",      "weight": 62.15,  "chrom": "chr7",  "pos": 130418180, "default_beta": 0.25},
    "cg09809672": {"gene": "EDARADD",    "weight": 41.90,  "chrom": "chr1",  "pos": 236539634, "default_beta": 0.20},
    "cg02088308": {"gene": "MIR29B2CHG", "weight": 38.75,  "chrom": "chr1",  "pos": 207819301, "default_beta": 0.22},
    "cg17861230": {"gene": "PDE4C",      "weight": 49.10,  "chrom": "chr19", "pos": 18228810,  "default_beta": 0.22},
    "cg02228185": {"gene": "ASPA",       "weight": -32.40, "chrom": "chr17", "pos": 3382901,   "default_beta": 0.28},
}

GENE_NAME_TO_CGID = {
    "ELOVL2": "cg16867657",
    "ELOVL2_2": "cg21572722",
    "FHL2": "cg06639320",
    "PENK": "cg16419235",
    "TRIM59": "cg04084157",
    "KLF14": "cg08097417",
    "EDARADD": "cg09809672",
    "MIR29B2CHG": "cg02088308",
    "PDE4C": "cg17861230",
    "ASPA": "cg02228185",
}

TISSUE_SPECIFIC_CONSTANTS = {
    "BLOOD": {
        "intercept": -0.6542,
        "offset": 0.00,
        "mae": 3.2,
        "rmse": 3.9,
        "standard_error": 3.90,
        "ci95_bound": 7.64,
    },
    "SALIVA": {
        "intercept": -0.6137,
        "offset": 0.85,
        "mae": 3.7,
        "rmse": 4.4,
        "standard_error": 4.40,
        "ci95_bound": 8.62,
    },
    "BUCCAL": {
        "intercept": -0.6137,
        "offset": 0.85,
        "mae": 3.7,
        "rmse": 4.4,
        "standard_error": 4.40,
        "ci95_bound": 8.62,
    },
    "SEMEN": {
        "intercept": -0.8541,
        "offset": -4.20,
        "mae": 3.5,
        "rmse": 4.2,
        "standard_error": 4.20,
        "ci95_bound": 8.23,
    },
    "BONE": {
        "intercept": -0.6018,
        "offset": 1.10,
        "mae": 3.4,
        "rmse": 4.1,
        "standard_error": 4.10,
        "ci95_bound": 8.04,
    },
    "TEETH": {
        "intercept": -0.6018,
        "offset": 1.10,
        "mae": 3.4,
        "rmse": 4.1,
        "standard_error": 4.10,
        "ci95_bound": 8.04,
    },
    "TISSUE": {
        "intercept": -0.6018,
        "offset": 0.50,
        "mae": 3.5,
        "rmse": 4.2,
        "standard_error": 4.20,
        "ci95_bound": 8.23,
    },
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class LocusContribution:
    locus: str
    gene: str
    methylation_beta: float
    weight: float
    contribution_years: float


@dataclass
class EpigeneticAgeResult:
    estimated_age_years: float
    model_age_before_offset: float
    linear_predictor_x: float
    developmental_stage: str             # "PEDIATRIC (<20 yrs)" or "ADULT (>=20 yrs)"
    prediction_interval_lower: float
    prediction_interval_upper: float
    standard_error_years: float
    expanded_uncertainty_95: float
    tissue_type: str
    tissue_offset_applied: float
    age_acceleration_delta: Optional[float]
    aging_status: str
    cpg_locus_contributions: List[Dict[str, Any]]
    model_provenance: str
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class EpigeneticClockEngine:
    """
    FORENZA Multi-Tissue Epigenetic Age Clock Engine based on Horvath / VISAGE Elastic Net models.

    Derives verbatim from Pillar 4 Research §1.
    """

    Y0_PIVOT_AGE: float = 20.0
    MARKERS = CPG_MARKER_METADATA
    GENE_MAP = GENE_NAME_TO_CGID
    TISSUES = TISSUE_SPECIFIC_CONSTANTS

    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        self.custom_weights = custom_weights

    def predict_age(
        self,
        cpg_methylation: Dict[str, Union[int, float]],
        tissue_type: str = "BLOOD",
        chronological_age_known: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates estimated chronological age, non-linear Horvath transformation,
        tissue calibration offsets, and ISO 17025 95% prediction intervals.
        """
        if not cpg_methylation:
            raise ValueError("cpg_methylation dictionary cannot be empty.")

        # Normalize and validate CpG beta values in [0.0, 1.0]
        validated_betas: Dict[str, float] = {}
        for key, val in cpg_methylation.items():
            key_clean = key.strip()
            # Map gene name alias to cgID if necessary
            cgid = self.GENE_MAP.get(key_clean.upper(), key_clean)
            beta_val = float(val)
            if not (0.0 <= beta_val <= 1.0):
                raise ValueError(f"CpG beta value for '{key}' must be within [0.0, 1.0], got {beta_val}.")
            validated_betas[cgid] = beta_val

        # Get tissue constants
        tissue_clean = tissue_type.strip().upper()
        tissue_info = self.TISSUES.get(tissue_clean, self.TISSUES["BLOOD"])
        beta_0 = tissue_info["intercept"]
        delta_tissue = tissue_info["offset"]
        se = tissue_info["standard_error"]
        ci95 = tissue_info["ci95_bound"]

        # Calculate weighted sum and per-locus breakdown
        weighted_sum = 0.0
        contributions: List[Dict[str, Any]] = []

        for cgid, meta in self.MARKERS.items():
            weight = self.custom_weights.get(cgid, meta["weight"]) if self.custom_weights else meta["weight"]
            beta = validated_betas.get(cgid, meta["default_beta"])
            contrib = weight * beta
            weighted_sum += contrib
            contributions.append({
                "locus": cgid,
                "gene": meta["gene"],
                "methylation_beta": round(beta, 4),
                "weight": round(weight, 2),
                "contribution_years": round(contrib, 2),
            })

        # Linear predictor x (Research §1.1)
        linear_predictor_x = beta_0 + (weighted_sum / 100.0)

        # Horvath Piecewise Non-Linear Transformation (y0 = 20.0)
        y0 = self.Y0_PIVOT_AGE
        if linear_predictor_x < 0.0:
            model_age = (y0 + 1.0) * math.exp(linear_predictor_x) - 1.0
            dev_stage = "PEDIATRIC (<20 yrs)"
        else:
            model_age = (y0 + 1.0) * linear_predictor_x + y0
            dev_stage = "ADULT (>=20 yrs)"

        # Apply tissue calibration offset
        final_age = max(0.0, model_age + delta_tissue)
        final_age_rounded = round(final_age, 1)

        # ISO 17025 95% Confidence Bounds (k = 1.96)
        pred_lower = max(0.0, round(final_age - ci95, 1))
        pred_upper = round(final_age + ci95, 1)

        # Biological Age Acceleration Delta
        age_acceleration_delta: Optional[float] = None
        aging_status = "NORMAL_AGING"
        if chronological_age_known is not None:
            age_acceleration_delta = round(final_age - float(chronological_age_known), 1)
            if age_acceleration_delta > 5.0:
                aging_status = "ACCELERATED_BIOLOGICAL_AGING"
            elif age_acceleration_delta < -5.0:
                aging_status = "DECELERATED_BIOLOGICAL_AGING"

        shield_statement = (
            "IMPORTANT (Forensic Epigenetics Legal Shield): Epigenetic DNA methylation age estimates reflect biological "
            "and chronological aging trajectories subject to multi-tissue variance (MAE ±3.2 to 3.7 years). "
            "Predictions must always be presented with the 95% prediction interval (ISO/IEC 17025:2017) and must NOT "
            "be interpreted as exact date-of-birth determinations."
        )

        return {
            "estimated_age_years": final_age_rounded,
            "model_age_before_offset": round(model_age, 1),
            "linear_predictor_x": round(linear_predictor_x, 4),
            "developmental_stage": dev_stage,
            "prediction_interval_lower": pred_lower,
            "prediction_interval_upper": pred_upper,
            "standard_error_years": se,
            "expanded_uncertainty_95": round(ci95, 2),
            "tissue_type": tissue_clean,
            "tissue_offset_applied": delta_tissue,
            "age_acceleration_delta": age_acceleration_delta,
            "aging_status": aging_status,
            "cpg_locus_contributions": contributions,
            "model_provenance": "Horvath / VISAGE Multi-Tissue Elastic Net Epigenetic Clock (10-CpG Standard)",
            "prosecutors_fallacy_shield": shield_statement,
        }
