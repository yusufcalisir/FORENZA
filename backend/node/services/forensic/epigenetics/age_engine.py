"""
FORENZA Forensic Epigenetic Age Estimation Engine (VISAGE 5-CpG & Multi-Tissue Models) — Module 16.

Implements verbatim from VISAGE Research (research/visage_5_cpg_epigenetic_aging_research.md & research/pillar_4_epigenetics_aging_research.md):
  - §1. Core 5-CpG Matrix (ELOVL2, FHL2, PENK, TRIM59, KLF14) & Supplementary Loci (EDARADD, MIR29B2CHG, PDE4C, ASPA)
  - §2. Piecewise Log-Linear Elastic Net Model (Horvath Link Architecture, y0 = 20.0 pivot boundary)
  - §3. Direct Multiple Linear Regression (MLR) with Non-Linear Power Transformations (Zbieć-Piekarska et al.)
  - §4. Dedicated Tissue-Specific Models (Buccal, Semen, Bone/Teeth) & Tissue Calibration Offsets
  - §5. ISO/IEC 17025 Dynamic Mahalanobis Metrological Uncertainty Budget with (X^T X)^-1 Covariance Matrix
  - §6. Standardized ENFSI Evaluative Reporting Court Statements (English & Turkish)
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union


# ── 1. Master 5-CpG & 10-CpG Genomic Metadata ──────────────────────────────────

CPG_MARKER_METADATA: Dict[str, Dict[str, Any]] = {
    "cg16867657": {
        "gene": "ELOVL2",
        "chrom": "chr6",
        "pos_grch37": 11044631,
        "pos_grch38": 11044634,
        "amplicon_bp": 267,
        "elastic_net_weight": 2.850000,
        "mlr_power_exp": 2.366,
        "mlr_weight": 120.3520,
        "mean_calibration_beta": 0.3850,
        "default_beta": 0.25,
        "legacy_weight": 102.45,
    },
    "cg06639320": {
        "gene": "FHL2",
        "chrom": "chr2",
        "pos_grch37": 106015741,
        "pos_grch38": 105399282,
        "amplicon_bp": 167,
        "elastic_net_weight": 1.920000,
        "mlr_power_exp": 1.0,
        "mlr_weight": 38.2140,
        "mean_calibration_beta": 0.3120,
        "default_beta": 0.20,
        "legacy_weight": 74.30,
    },
    "cg16419235": {
        "gene": "PENK",
        "chrom": "chr8",
        "pos_grch37": 57358322,
        "pos_grch38": 56419985,
        "amplicon_bp": 142,
        "elastic_net_weight": 0.950000,
        "mlr_power_exp": 1.0,
        "mlr_weight": 21.8040,
        "mean_calibration_beta": 0.2450,
        "default_beta": 0.30,
        "legacy_weight": -45.20,
    },
    "cg04523812": {
        "gene": "TRIM59",
        "chrom": "chr3",
        "pos_grch37": 160202320,
        "pos_grch38": 160450202,
        "amplicon_bp": 141,
        "elastic_net_weight": 0.880000,
        "mlr_power_exp": 1.0,
        "mlr_weight": 18.9410,
        "mean_calibration_beta": 0.2810,
        "default_beta": 0.25,
        "legacy_weight": 56.80,
    },
    "cg04084157": {
        "gene": "TRIM59",
        "chrom": "chr3",
        "pos_grch37": 160202320,
        "pos_grch38": 160450202,
        "amplicon_bp": 141,
        "elastic_net_weight": 0.880000,
        "mlr_power_exp": 1.0,
        "mlr_weight": 18.9410,
        "mean_calibration_beta": 0.2810,
        "default_beta": 0.25,
        "legacy_weight": 56.80,
    },
    "cg07955995": {
        "gene": "KLF14",
        "chrom": "chr7",
        "pos_grch37": 130418180,
        "pos_grch38": 130734375,
        "amplicon_bp": 128,
        "elastic_net_weight": 1.150000,
        "mlr_power_exp": 1.0,
        "mlr_weight": 26.1030,
        "mean_calibration_beta": 0.2100,
        "default_beta": 0.25,
        "legacy_weight": 62.15,
    },
    "cg08097417": {
        "gene": "KLF14",
        "chrom": "chr7",
        "pos_grch37": 130418180,
        "pos_grch38": 130734375,
        "amplicon_bp": 128,
        "elastic_net_weight": 1.150000,
        "mlr_power_exp": 1.0,
        "mlr_weight": 26.1030,
        "mean_calibration_beta": 0.2100,
        "default_beta": 0.25,
        "legacy_weight": 62.15,
    },
    # Supplementary / Extension Markers
    "cg21572722": {
        "gene": "ELOVL2_C2",
        "chrom": "chr6",
        "pos_grch37": 11044680,
        "pos_grch38": 11044655,
        "amplicon_bp": 267,
        "default_beta": 0.25,
        "legacy_weight": 88.12,
    },
    "cg09809672": {
        "gene": "EDARADD",
        "chrom": "chr1",
        "pos_grch37": 236539634,
        "pos_grch38": 236394383,
        "amplicon_bp": 193,
        "default_beta": 0.20,
        "legacy_weight": 41.90,
    },
    "cg02088308": {
        "gene": "MIR29B2CHG",
        "chrom": "chr1",
        "pos_grch37": 207819301,
        "pos_grch38": 207823681,
        "amplicon_bp": 146,
        "default_beta": 0.22,
        "legacy_weight": 38.75,
    },
    "cg17861230": {
        "gene": "PDE4C",
        "chrom": "chr19",
        "pos_grch37": 18228810,
        "pos_grch38": 18233127,
        "amplicon_bp": 215,
        "default_beta": 0.22,
        "legacy_weight": 49.10,
    },
    "cg02228185": {
        "gene": "ASPA",
        "chrom": "chr17",
        "pos_grch37": 3382901,
        "pos_grch38": 3476273,
        "amplicon_bp": 108,
        "default_beta": 0.28,
        "legacy_weight": -32.40,
    },
}

GENE_NAME_TO_CGID = {
    "ELOVL2": "cg16867657",
    "ELOVL2_2": "cg21572722",
    "ELOVL2_C2": "cg21572722",
    "FHL2": "cg06639320",
    "PENK": "cg16419235",
    "TRIM59": "cg04523812",
    "KLF14": "cg07955995",
    "EDARADD": "cg09809672",
    "MIR29B2CHG": "cg02088308",
    "C1ORF132": "cg02088308",
    "PDE4C": "cg17861230",
    "ASPA": "cg02228185",
}

# ── 2. Matrix & Model Parameters ───────────────────────────────────────────────

VISAGE_5CPG_ORDER = ["cg16867657", "cg06639320", "cg16419235", "cg04523812", "cg07955995"]

LEGACY_10CPG_ORDER = [
    "cg16867657",
    "cg21572722",
    "cg06639320",
    "cg16419235",
    "cg04084157",
    "cg08097417",
    "cg09809672",
    "cg02088308",
    "cg17861230",
    "cg02228185",
]

VISAGE_5CPG_CENTROID = [0.3850, 0.3120, 0.2450, 0.2810, 0.2100]

VISAGE_XTX_INV_5CPG = [
    [ 0.01245, -0.00312, -0.00185, -0.00210, -0.00142],
    [-0.00312,  0.00892, -0.00115, -0.00154, -0.00098],
    [-0.00185, -0.00115,  0.01540, -0.00245, -0.00120],
    [-0.00210, -0.00154, -0.00245,  0.01120, -0.00085],
    [-0.00142, -0.00098, -0.00120, -0.00085,  0.00965]
]

# Tissue calibration dictionaries
VISAGE_TISSUE_CALIBRATION: Dict[str, Dict[str, Any]] = {
    "BLOOD": {"delta_years": 0.00, "mae": 3.15, "rmse": 3.98, "se_pred": 1.95, "pi95_bound": 3.82},
    "WHOLE_BLOOD": {"delta_years": 0.00, "mae": 3.15, "rmse": 3.98, "se_pred": 1.95, "pi95_bound": 3.82},
    "SALIVA": {"delta_years": 2.45, "mae": 3.68, "rmse": 4.52, "se_pred": 2.25, "pi95_bound": 4.41},
    "BUCCAL": {"delta_years": 2.45, "mae": 3.68, "rmse": 4.52, "se_pred": 2.25, "pi95_bound": 4.41},
    "SALIVA_BUCCAL": {"delta_years": 2.45, "mae": 3.68, "rmse": 4.52, "se_pred": 2.25, "pi95_bound": 4.41},
    "SEMEN": {"delta_years": 18.60, "mae": 4.12, "rmse": 5.20, "se_pred": 2.60, "pi95_bound": 5.10},
    "SEMINAL_FLUID": {"delta_years": 18.60, "mae": 4.12, "rmse": 5.20, "se_pred": 2.60, "pi95_bound": 5.10},
    "BONE": {"delta_years": 1.15, "mae": 4.85, "rmse": 6.10, "se_pred": 3.05, "pi95_bound": 5.98},
    "TEETH": {"delta_years": 1.15, "mae": 4.85, "rmse": 6.10, "se_pred": 3.05, "pi95_bound": 5.98},
    "SKELETAL_BONE": {"delta_years": 1.15, "mae": 4.85, "rmse": 6.10, "se_pred": 3.05, "pi95_bound": 5.98},
    "TISSUE": {"delta_years": 0.50, "mae": 3.50, "rmse": 4.20, "se_pred": 2.10, "pi95_bound": 4.12},
}

LEGACY_10CPG_TISSUE_CONSTANTS: Dict[str, Dict[str, Any]] = {
    "BLOOD": {"intercept": -0.6542, "offset": 0.00, "mae": 3.2, "rmse": 3.9, "se_pred": 3.90, "ci95_bound": 7.64},
    "WHOLE_BLOOD": {"intercept": -0.6542, "offset": 0.00, "mae": 3.2, "rmse": 3.9, "se_pred": 3.90, "ci95_bound": 7.64},
    "SALIVA": {"intercept": -0.6137, "offset": 0.85, "mae": 3.7, "rmse": 4.4, "se_pred": 4.40, "ci95_bound": 8.62},
    "BUCCAL": {"intercept": -0.6137, "offset": 0.85, "mae": 3.7, "rmse": 4.4, "se_pred": 4.40, "ci95_bound": 8.62},
    "SALIVA_BUCCAL": {"intercept": -0.6137, "offset": 0.85, "mae": 3.7, "rmse": 4.4, "se_pred": 4.40, "ci95_bound": 8.62},
    "SEMEN": {"intercept": -0.8541, "offset": -4.20, "mae": 3.5, "rmse": 4.2, "se_pred": 4.20, "ci95_bound": 8.23},
    "SEMINAL_FLUID": {"intercept": -0.8541, "offset": -4.20, "mae": 3.5, "rmse": 4.2, "se_pred": 4.20, "ci95_bound": 8.23},
    "BONE": {"intercept": -0.6018, "offset": 1.10, "mae": 3.4, "rmse": 4.1, "se_pred": 4.10, "ci95_bound": 8.04},
    "TEETH": {"intercept": -0.6018, "offset": 1.10, "mae": 3.4, "rmse": 4.1, "se_pred": 4.10, "ci95_bound": 8.04},
    "SKELETAL_BONE": {"intercept": -0.6018, "offset": 1.10, "mae": 3.4, "rmse": 4.1, "se_pred": 4.10, "ci95_bound": 8.04},
    "TISSUE": {"intercept": -0.6018, "offset": 0.50, "mae": 3.5, "rmse": 4.2, "se_pred": 4.20, "ci95_bound": 8.23},
}

ENFSI_CATEGORY_MAP_TR = {
    "Child / Minor": "Çocuk / Reşit Olmayan",
    "Young Adult": "Genç Yetişkin",
    "Adult": "Yetişkin",
    "Middle-Aged Adult": "Orta Yaşlı Yetişkin",
    "Senior / Elderly": "Yaşlı",
    "Adult (Buccal Matrix)": "Yetişkin (Ağız Mukozası)",
}


# ── 3. Data Classes ────────────────────────────────────────────────────────────

@dataclass
class CpgContributionDetail:
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
    developmental_stage: str
    prediction_interval_lower: float
    prediction_interval_upper: float
    standard_error_years: float
    expanded_uncertainty_95: float
    mahalanobis_distance_squared: float
    tissue_type: str
    tissue_offset_applied: float
    age_acceleration_delta: Optional[float]
    aging_status: str
    cpg_locus_contributions: List[Dict[str, Any]]
    model_mode: str
    model_provenance: str
    enfsi_statement_en: str
    enfsi_statement_tr: str
    enfsi_demographic_category: str
    prosecutors_fallacy_shield: str


# ── 4. Biocomputational Engine ─────────────────────────────────────────────────

class EpigeneticClockEngine:
    """
    FORENZA Multi-Tissue Epigenetic Age Clock Engine conforming to ISO/IEC 17025:2017
    and VISAGE Consortium specifications.
    """

    Y0_PIVOT_AGE: float = 20.0
    HORVATH_MULTIPLIER: float = 21.0
    T_CRITICAL_95: float = 1.96366  # t(0.025, df=644)
    N_CALIBRATION: int = 650
    RSE_BLOOD: float = 3.821

    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        self.custom_weights = custom_weights

    @staticmethod
    def _normalize_cpg_map(cpg_input: Dict[str, Union[int, float]]) -> Dict[str, float]:
        """Normalizes locus names and aliases, ensuring beta in [0.0, 1.0]."""
        normalized: Dict[str, float] = {}
        for key, val in cpg_input.items():
            key_clean = key.strip()
            beta_val = float(val)
            if not (0.0 <= beta_val <= 1.0):
                raise ValueError(f"CpG beta value for '{key}' must be within [0.0, 1.0], got {beta_val}.")
            normalized[key_clean] = beta_val
            # Map canonical gene names
            cgid = GENE_NAME_TO_CGID.get(key_clean.upper())
            if cgid and cgid not in normalized:
                normalized[cgid] = beta_val
            # Cross-map aliases
            if key_clean == "cg04084157" and "cg04523812" not in normalized:
                normalized["cg04523812"] = beta_val
            elif key_clean == "cg04523812" and "cg04084157" not in normalized:
                normalized["cg04084157"] = beta_val
            elif key_clean == "cg08097417" and "cg07955995" not in normalized:
                normalized["cg07955995"] = beta_val
            elif key_clean == "cg07955995" and "cg08097417" not in normalized:
                normalized["cg08097417"] = beta_val
        return normalized

    @classmethod
    def calculate_mahalanobis_distance_sq(cls, betas_5cpg: List[float]) -> float:
        """Computes d^T (X^T X)^-1 d against the 5-CpG calibration centroid."""
        d = [betas_5cpg[i] - VISAGE_5CPG_CENTROID[i] for i in range(5)]
        d_sq = 0.0
        for i in range(5):
            for j in range(5):
                d_sq += d[i] * VISAGE_XTX_INV_5CPG[i][j] * d[j]
        return max(0.0, d_sq)

    @classmethod
    def get_enfsi_demographic_category(cls, age: float) -> str:
        if age < 15.0:
            return "Child / Minor"
        elif age <= 28.0:
            return "Young Adult"
        elif age <= 45.0:
            return "Adult"
        elif age <= 65.0:
            return "Middle-Aged Adult"
        else:
            return "Senior / Elderly"

    @classmethod
    def generate_enfsi_statements(
        cls,
        predicted_age: float,
        pi_lower: float,
        pi_upper: float,
        category_en: str,
        tissue: str
    ) -> tuple[str, str]:
        category_tr = ENFSI_CATEGORY_MAP_TR.get(category_en, category_en)
        en_stmt = (
            f"The DNA methylation profile ({tissue}) indicates a predicted chronological age of {predicted_age:.2f} years "
            f"(95% PI: {pi_lower:.2f} to {pi_upper:.2f} years). The physical evidence strongly supports the proposition "
            f"that the donor belonged to the {category_en} demographic group."
        )
        tr_stmt = (
            f"DNA metilasyon profili ({tissue}), {predicted_age:.2f} yıllık bir tahmini kronolojik yaşa işaret etmektedir "
            f"(%95 GB: {pi_lower:.2f} ila {pi_upper:.2f} yıl). Elde edilen deliller, vericinin {category_tr} "
            f"demografik grubunda yer aldığı hipotezini güçlü bir şekilde desteklemektedir."
        )
        return en_stmt, tr_stmt

    def predict_age_visage_5cpg(
        self,
        cpg_betas: Dict[str, float],
        tissue_type: str = "BLOOD",
        chronological_age_known: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes the VISAGE 5-CpG Elastic Net Piecewise Log-Linear Model with Horvath link (y0=20.0).
        """
        b_elovl2 = cpg_betas.get("cg16867657", CPG_MARKER_METADATA["cg16867657"]["default_beta"])
        b_fhl2   = cpg_betas.get("cg06639320", CPG_MARKER_METADATA["cg06639320"]["default_beta"])
        b_penk   = cpg_betas.get("cg16419235", CPG_MARKER_METADATA["cg16419235"]["default_beta"])
        b_trim59 = cpg_betas.get("cg04523812", CPG_MARKER_METADATA["cg04523812"]["default_beta"])
        b_klf14  = cpg_betas.get("cg07955995", CPG_MARKER_METADATA["cg07955995"]["default_beta"])

        beta_vec = [b_elovl2, b_fhl2, b_penk, b_trim59, b_klf14]

        # Elastic Net linear score x
        beta_0 = -1.250000
        w_elovl2 = 2.850000
        w_fhl2   = 1.920000
        w_penk   = 0.950000
        w_trim59 = 0.880000
        w_klf14  = 1.150000

        linear_score_x = (
            beta_0
            + w_elovl2 * b_elovl2
            + w_fhl2 * b_fhl2
            + w_penk * b_penk
            + w_trim59 * b_trim59
            + w_klf14 * b_klf14
        )

        # Piecewise Link Function (y0 = 20.0)
        y0 = self.Y0_PIVOT_AGE
        mult = self.HORVATH_MULTIPLIER
        if linear_score_x < 0.0:
            model_age = mult * math.exp(linear_score_x) - 1.0
            dev_stage = "PEDIATRIC (<20 yrs)"
        else:
            model_age = mult * linear_score_x + y0
            dev_stage = "ADULT (>=20 yrs)"

        # Tissue Matrix Calibration Offset
        tissue_clean = tissue_type.strip().upper()
        t_info = VISAGE_TISSUE_CALIBRATION.get(tissue_clean, VISAGE_TISSUE_CALIBRATION["BLOOD"])
        delta_tissue = t_info["delta_years"]
        final_age = max(0.0, model_age + delta_tissue)

        # Dynamic ISO 17025 Uncertainty Budget
        d_sq = self.calculate_mahalanobis_distance_sq(beta_vec)
        if linear_score_x < 0.0 and tissue_clean in ["BLOOD", "WHOLE_BLOOD"]:
            # Pediatric calibrated bounds per VISAGE benchmark
            se_pred = 3.10
            pi_half = 6.08
            pred_lower = max(0.0, round(final_age - pi_half, 2))
            pred_upper = round(final_age + pi_half, 2)
        else:
            se_pred = t_info["se_pred"]
            uncertainty_mult = math.sqrt(1.0 + (1.0 / self.N_CALIBRATION) + d_sq)
            pi_half = self.T_CRITICAL_95 * se_pred * uncertainty_mult
            pred_lower = max(0.0, round(final_age - pi_half, 2))
            pred_upper = round(final_age + pi_half, 2)

        contributions = [
            {"locus": "cg16867657", "gene": "ELOVL2", "methylation_beta": round(b_elovl2, 4), "weight": w_elovl2, "contribution_years": round(w_elovl2 * b_elovl2 * mult, 2)},
            {"locus": "cg06639320", "gene": "FHL2", "methylation_beta": round(b_fhl2, 4), "weight": w_fhl2, "contribution_years": round(w_fhl2 * b_fhl2 * mult, 2)},
            {"locus": "cg16419235", "gene": "PENK", "methylation_beta": round(b_penk, 4), "weight": w_penk, "contribution_years": round(w_penk * b_penk * mult, 2)},
            {"locus": "cg04523812", "gene": "TRIM59", "methylation_beta": round(b_trim59, 4), "weight": w_trim59, "contribution_years": round(w_trim59 * b_trim59 * mult, 2)},
            {"locus": "cg07955995", "gene": "KLF14", "methylation_beta": round(b_klf14, 4), "weight": w_klf14, "contribution_years": round(w_klf14 * b_klf14 * mult, 2)},
        ]

        # Biological Age Acceleration
        age_acceleration_delta = None
        aging_status = "NORMAL_AGING"
        if chronological_age_known is not None:
            age_acceleration_delta = round(final_age - float(chronological_age_known), 2)
            if age_acceleration_delta > 5.0:
                aging_status = "ACCELERATED_BIOLOGICAL_AGING"
            elif age_acceleration_delta < -5.0:
                aging_status = "DECELERATED_BIOLOGICAL_AGING"

        category = self.get_enfsi_demographic_category(final_age)
        if tissue_clean in ["SALIVA", "BUCCAL", "SALIVA_BUCCAL"]:
            category = "Adult (Buccal Matrix)"
        stmt_en, stmt_tr = self.generate_enfsi_statements(final_age, pred_lower, pred_upper, category, tissue_clean)

        return {
            "estimated_age_years": round(final_age, 2),
            "model_age_before_offset": round(model_age, 2),
            "linear_predictor_x": round(linear_score_x, 4),
            "developmental_stage": dev_stage,
            "prediction_interval_lower": pred_lower,
            "prediction_interval_upper": pred_upper,
            "standard_error_years": se_pred,
            "expanded_uncertainty_95": round(pi_half, 2),
            "mahalanobis_distance_squared": round(d_sq, 6),
            "tissue_type": tissue_clean,
            "tissue_offset_applied": delta_tissue,
            "age_acceleration_delta": age_acceleration_delta,
            "aging_status": aging_status,
            "cpg_locus_contributions": contributions,
            "model_mode": "VISAGE_5CPG_ELASTIC_NET",
            "model_provenance": "VISAGE 5-CpG Elastic Net Piecewise Log-Linear Epigenetic Age Clock (Horvath Link)",
            "enfsi_statement_en": stmt_en,
            "enfsi_statement_tr": stmt_tr,
            "enfsi_demographic_category": category,
            "prosecutors_fallacy_shield": (
                "IMPORTANT (Forensic Epigenetics Legal Shield): Epigenetic DNA methylation age estimates reflect biological "
                "and chronological aging trajectories subject to multi-tissue variance (MAE ±3.15 to 3.68 years). "
                "Predictions must always be presented with the 95% prediction interval (ISO/IEC 17025:2017) and must NOT "
                "be interpreted as exact date-of-birth determinations."
            ),
        }

    def predict_age_visage_mlr_power(
        self,
        cpg_betas: Dict[str, float],
        tissue_type: str = "BLOOD",
        chronological_age_known: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes the classical VISAGE 5-marker Direct Multiple Linear Regression (MLR) model
        with non-linear power law transformation on ELOVL2 (Zbieć-Piekarska et al.).
        """
        b_elovl2 = cpg_betas.get("cg16867657", CPG_MARKER_METADATA["cg16867657"]["default_beta"])
        b_fhl2   = cpg_betas.get("cg06639320", CPG_MARKER_METADATA["cg06639320"]["default_beta"])
        b_penk   = cpg_betas.get("cg16419235", CPG_MARKER_METADATA["cg16419235"]["default_beta"])
        b_trim59 = cpg_betas.get("cg04523812", CPG_MARKER_METADATA["cg04523812"]["default_beta"])
        b_klf14  = cpg_betas.get("cg07955995", CPG_MARKER_METADATA["cg07955995"]["default_beta"])

        elovl2_pow = math.pow(b_elovl2, 2.366)
        raw_age = (
            -14.2815
            + 120.3520 * elovl2_pow
            + 38.2140 * b_fhl2
            + 21.8040 * b_penk
            + 18.9410 * b_trim59
            + 26.1030 * b_klf14
        )

        tissue_clean = tissue_type.strip().upper()
        t_info = VISAGE_TISSUE_CALIBRATION.get(tissue_clean, VISAGE_TISSUE_CALIBRATION["BLOOD"])
        delta_tissue = t_info["delta_years"]
        final_age = max(0.0, raw_age + delta_tissue)

        pi_bound = t_info["pi95_bound"]
        pred_lower = max(0.0, round(final_age - pi_bound, 2))
        pred_upper = round(final_age + pi_bound, 2)

        contributions = [
            {"locus": "cg16867657", "gene": "ELOVL2 (Power 2.366)", "methylation_beta": round(b_elovl2, 4), "weight": 120.3520, "contribution_years": round(120.3520 * elovl2_pow, 2)},
            {"locus": "cg06639320", "gene": "FHL2", "methylation_beta": round(b_fhl2, 4), "weight": 38.2140, "contribution_years": round(38.2140 * b_fhl2, 2)},
            {"locus": "cg16419235", "gene": "PENK", "methylation_beta": round(b_penk, 4), "weight": 21.8040, "contribution_years": round(21.8040 * b_penk, 2)},
            {"locus": "cg04523812", "gene": "TRIM59", "methylation_beta": round(b_trim59, 4), "weight": 18.9410, "contribution_years": round(18.9410 * b_trim59, 2)},
            {"locus": "cg07955995", "gene": "KLF14", "methylation_beta": round(b_klf14, 4), "weight": 26.1030, "contribution_years": round(26.1030 * b_klf14, 2)},
        ]

        category = self.get_enfsi_demographic_category(final_age)
        stmt_en, stmt_tr = self.generate_enfsi_statements(final_age, pred_lower, pred_upper, category, tissue_clean)

        return {
            "estimated_age_years": round(final_age, 2),
            "model_age_before_offset": round(raw_age, 2),
            "linear_predictor_x": round(raw_age, 4),
            "developmental_stage": "ADULT (>=20 yrs)" if final_age >= 20.0 else "PEDIATRIC (<20 yrs)",
            "prediction_interval_lower": pred_lower,
            "prediction_interval_upper": pred_upper,
            "standard_error_years": t_info["se_pred"],
            "expanded_uncertainty_95": pi_bound,
            "mahalanobis_distance_squared": 0.0,
            "tissue_type": tissue_clean,
            "tissue_offset_applied": delta_tissue,
            "age_acceleration_delta": round(final_age - chronological_age_known, 2) if chronological_age_known else None,
            "aging_status": "NORMAL_AGING",
            "cpg_locus_contributions": contributions,
            "model_mode": "VISAGE_5CPG_MLR_POWER",
            "model_provenance": "VISAGE 5-CpG Direct MLR Model with ELOVL2 Power Transformation (Zbieć-Piekarska et al.)",
            "enfsi_statement_en": stmt_en,
            "enfsi_statement_tr": stmt_tr,
            "enfsi_demographic_category": category,
            "prosecutors_fallacy_shield": (
                "IMPORTANT (Forensic Epigenetics Legal Shield): Direct MLR age estimates reflect standard linear regression "
                "calibrated for blood traces (MAE ±3.15 years). Results must be interpreted with ISO 17025 prediction bounds."
            ),
        }

    def predict_age_extended_10cpg(
        self,
        cpg_betas: Dict[str, float],
        tissue_type: str = "BLOOD",
        chronological_age_known: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes the Extended 10-CpG Pan-Tissue Elastic Net Clock (Pillar 4 Baseline Model).
        """
        tissue_clean = tissue_type.strip().upper()
        t_info = LEGACY_10CPG_TISSUE_CONSTANTS.get(tissue_clean, LEGACY_10CPG_TISSUE_CONSTANTS["BLOOD"])
        beta_0 = t_info["intercept"]
        delta_tissue = t_info["offset"]
        se = t_info["se_pred"]
        ci95 = t_info["ci95_bound"]

        weighted_sum = 0.0
        contributions: List[Dict[str, Any]] = []

        for cgid in LEGACY_10CPG_ORDER:
            meta = CPG_MARKER_METADATA[cgid]
            weight = self.custom_weights.get(cgid, meta["legacy_weight"]) if self.custom_weights else meta["legacy_weight"]
            beta = cpg_betas.get(cgid, meta["default_beta"])
            contrib = weight * beta
            weighted_sum += contrib
            contributions.append({
                "locus": cgid,
                "gene": meta["gene"],
                "methylation_beta": round(beta, 4),
                "weight": round(weight, 2),
                "contribution_years": round(contrib, 2),
            })

        linear_predictor_x = beta_0 + (weighted_sum / 100.0)
        y0 = self.Y0_PIVOT_AGE
        if linear_predictor_x < 0.0:
            model_age = (y0 + 1.0) * math.exp(linear_predictor_x) - 1.0
            dev_stage = "PEDIATRIC (<20 yrs)"
        else:
            model_age = (y0 + 1.0) * linear_predictor_x + y0
            dev_stage = "ADULT (>=20 yrs)"

        final_age = max(0.0, model_age + delta_tissue)
        final_age_rounded = round(final_age, 1)

        pred_lower = max(0.0, round(final_age - ci95, 1))
        pred_upper = round(final_age + ci95, 1)

        age_acceleration_delta = None
        aging_status = "NORMAL_AGING"
        if chronological_age_known is not None:
            age_acceleration_delta = round(final_age - float(chronological_age_known), 1)
            if age_acceleration_delta > 5.0:
                aging_status = "ACCELERATED_BIOLOGICAL_AGING"
            elif age_acceleration_delta < -5.0:
                aging_status = "DECELERATED_BIOLOGICAL_AGING"

        category = self.get_enfsi_demographic_category(final_age)
        stmt_en, stmt_tr = self.generate_enfsi_statements(final_age, pred_lower, pred_upper, category, tissue_clean)

        return {
            "estimated_age_years": final_age_rounded,
            "model_age_before_offset": round(model_age, 1),
            "linear_predictor_x": round(linear_predictor_x, 4),
            "developmental_stage": dev_stage,
            "prediction_interval_lower": pred_lower,
            "prediction_interval_upper": pred_upper,
            "standard_error_years": se,
            "expanded_uncertainty_95": round(ci95, 2),
            "mahalanobis_distance_squared": 0.0,
            "tissue_type": tissue_clean,
            "tissue_offset_applied": delta_tissue,
            "age_acceleration_delta": age_acceleration_delta,
            "aging_status": aging_status,
            "cpg_locus_contributions": contributions,
            "model_mode": "EXTENDED_10CPG_CLOCK",
            "model_provenance": "Horvath / VISAGE Multi-Tissue Elastic Net Epigenetic Clock (10-CpG Standard)",
            "enfsi_statement_en": stmt_en,
            "enfsi_statement_tr": stmt_tr,
            "enfsi_demographic_category": category,
            "prosecutors_fallacy_shield": (
                "IMPORTANT (Forensic Epigenetics Legal Shield): Epigenetic DNA methylation age estimates reflect biological "
                "and chronological aging trajectories subject to multi-tissue variance. Predictions must always be presented "
                "with the 95% prediction interval (ISO/IEC 17025:2017)."
            ),
        }

    def predict_age(
        self,
        cpg_methylation: Dict[str, Union[int, float]],
        tissue_type: str = "BLOOD",
        chronological_age_known: Optional[float] = None,
        model_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unified prediction router supporting VISAGE 5-CpG Elastic Net, VISAGE 5-CpG MLR Power Model,
        and Extended 10-CpG Pan-Tissue Clock.
        """
        if not cpg_methylation:
            raise ValueError("cpg_methylation dictionary cannot be empty.")

        normalized_betas = self._normalize_cpg_map(cpg_methylation)
        mode_clean = (model_mode or "EXTENDED_10CPG_CLOCK").strip().upper()

        if mode_clean in ["VISAGE_5CPG_ELASTIC_NET", "VISAGE_5CPG", "VISAGE"]:
            return self.predict_age_visage_5cpg(
                normalized_betas,
                tissue_type=tissue_type,
                chronological_age_known=chronological_age_known
            )
        elif mode_clean in ["VISAGE_5CPG_MLR_POWER", "VISAGE_MLR", "MLR"]:
            return self.predict_age_visage_mlr_power(
                normalized_betas,
                tissue_type=tissue_type,
                chronological_age_known=chronological_age_known
            )
        else:
            return self.predict_age_extended_10cpg(
                normalized_betas,
                tissue_type=tissue_type,
                chronological_age_known=chronological_age_known
            )
