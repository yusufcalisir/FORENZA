"""
FORENZA Somatic Mosaicism, Telomere Length Decay & Post-Mortem Epigenetic Interval Engine — Module 19.

Implements verbatim from Pillar 4 Research §4 & §6:
  - §4.1 Relative Telomere Length (T/S Ratio) Decay Kinetics (T/S = 1.420 - 0.0085 * Age)
  - §4.2 Post-Mortem Epigenetic Decay Kinetics & Thermal Summation (PMI / ADH)
  - §4.3 Somatic Mosaicism & Intra-Individual Epigenetic Drift Index (M)
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, Optional, Union, List


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class TelomereResult:
    relative_ts_ratio: float
    estimated_telomere_age_years: float
    telomere_age_group: str
    annual_shortening_rate: float


@dataclass
class PmiEpigeneticResult:
    observed_cpg_beta: float
    baseline_beta_0: float
    decay_constant_lambda: float
    accumulated_degree_hours: float
    ambient_temperature_celsius: float
    estimated_pmi_hours: float
    estimated_pmi_days: float
    pmi_confidence_interval_hours: Optional[List[float]] = None



@dataclass
class SomaticMosaicismResult:
    mosaicism_index_m: float
    mosaicism_classification: str
    loci_evaluated: int
    locus_deltas: Dict[str, float]


# ── Engine ─────────────────────────────────────────────────────────────────────

class TelomerePmiEngine:
    """
    FORENZA Forensic Telomere Length, Post-Mortem Epigenetic Decay, and Somatic Mosaicism Engine.

    Derives verbatim from Pillar 4 Research §4.
    """

    # Telomere length parameters (Research §4.1)
    TELOMERE_INTERCEPT = 1.420
    TELOMERE_SLOPE = 0.0085  # T/S units per year

    # Post-mortem epigenetic decay kinetics parameters (Research §4.2)
    PMI_LAMBDA_DECAY = 0.00045  # per ADH
    PMI_DEFAULT_BETA_0 = 0.85
    PMI_BETA_FLOOR = 0.05
    PMI_BASE_TEMP = 0.0  # Celsius

    def estimate_telomere_age(
        self,
        ts_ratio: Optional[float] = None,
        delta_delta_ct: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates biological age from relative telomere length T/S ratio (2^-ddCt).
        """
        if ts_ratio is None and delta_delta_ct is None:
            raise ValueError("Either ts_ratio or delta_delta_ct must be provided.")

        if ts_ratio is None:
            ddct = float(delta_delta_ct)
            ts = 2.0 ** (-ddct)
        else:
            ts = float(ts_ratio)

        if ts <= 0.0:
            raise ValueError(f"T/S ratio must be strictly positive, got {ts}.")

        # Estimated Age = max(0.0, (1.420 - T/S) / 0.0085)
        est_age = max(0.0, (self.TELOMERE_INTERCEPT - ts) / self.TELOMERE_SLOPE)
        est_age_rounded = round(est_age, 1)

        if ts >= 1.35:
            age_group = "NEWBORN_INFANT"
        elif ts >= 1.15:
            age_group = "YOUNG_ADULT"
        elif ts >= 0.90:
            age_group = "MIDDLE_AGED"
        else:
            age_group = "ELDERLY"

        return {
            "relative_ts_ratio": round(ts, 4),
            "estimated_telomere_age_years": est_age_rounded,
            "telomere_age_group": age_group,
            "annual_shortening_rate": self.TELOMERE_SLOPE,
        }

    def estimate_post_mortem_interval(
        self,
        observed_beta: float,
        ambient_temperature_celsius: float = 20.0,
        baseline_beta_0: Optional[float] = None,
        decay_constant_lambda: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates Post-Mortem Epigenetic Interval (PMI) from residual CpG methylation
        under Accumulated Degree-Hours (ADH) thermal summation.
        """
        obs_beta = float(observed_beta)
        if not (0.0 <= obs_beta <= 1.0):
            raise ValueError(f"Observed CpG beta must be within [0.0, 1.0], got {obs_beta}.")

        temp = float(ambient_temperature_celsius)
        b0 = float(baseline_beta_0) if baseline_beta_0 is not None else self.PMI_DEFAULT_BETA_0
        lam = float(decay_constant_lambda) if decay_constant_lambda is not None else self.PMI_LAMBDA_DECAY

        # Effective temperature above base
        effective_temp = max(0.1, temp - self.PMI_BASE_TEMP)

        # ADH calculation: ADH = (1/lambda) * ln(beta_0 / max(1e-4, beta - beta_floor))
        effective_beta = max(1e-4, obs_beta - self.PMI_BETA_FLOOR)
        if effective_beta >= b0:
            adh_est = 0.0
        else:
            adh_est = (1.0 / lam) * math.log(b0 / effective_beta)

        adh_rounded = round(adh_est, 1)
        pmi_hours = round(adh_est / effective_temp, 1)
        pmi_days = round(pmi_hours / 24.0, 1)

        # 95% Confidence Interval for PMI estimation (+- 15% thermal variance)
        ci_lower = max(0.0, round(pmi_hours * 0.85, 1))
        ci_upper = round(pmi_hours * 1.15, 1)

        return {
            "observed_cpg_beta": obs_beta,
            "baseline_beta_0": b0,
            "decay_constant_lambda": lam,
            "accumulated_degree_hours": adh_rounded,
            "ambient_temperature_celsius": temp,
            "estimated_pmi_hours": pmi_hours,
            "estimated_pmi_days": pmi_days,
            "pmi_confidence_interval_hours": [ci_lower, ci_upper],
        }

    def compute_somatic_mosaicism_index(
        self,
        tissue1_betas: Dict[str, float],
        tissue2_betas: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Calculates Somatic Mosaicism & Intra-Individual Epigenetic Drift Index (M)
        between two tissue profiles or replicates.
        """
        if not tissue1_betas or not tissue2_betas:
            raise ValueError("Both tissue methylation dictionaries must be non-empty.")

        common_loci = set(tissue1_betas.keys()) & set(tissue2_betas.keys())
        if not common_loci:
            raise ValueError("No common CpG loci found between compared tissue profiles.")

        deltas: Dict[str, float] = {}
        sum_sq = 0.0
        for locus in common_loci:
            b1 = float(tissue1_betas[locus])
            b2 = float(tissue2_betas[locus])
            if not (0.0 <= b1 <= 1.0) or not (0.0 <= b2 <= 1.0):
                raise ValueError(f"CpG beta values for locus '{locus}' must be within [0.0, 1.0].")
            diff = b1 - b2
            deltas[locus] = round(diff, 4)
            sum_sq += diff * diff

        m_index = round(math.sqrt(sum_sq / len(common_loci)), 4)

        if m_index < 0.05:
            classification = "CLONAL_HOMOGENEITY"
        elif m_index <= 0.15:
            classification = "LOW_SOMATIC_DRIFT"
        else:
            classification = "HIGH_SOMATIC_MOSAICISM"

        return {
            "mosaicism_index_m": m_index,
            "mosaicism_classification": classification,
            "loci_evaluated": len(common_loci),
            "locus_deltas": deltas,
        }

    def analyze_comprehensive_profile(
        self,
        ts_ratio: Optional[float] = None,
        observed_pmi_beta: Optional[float] = None,
        ambient_temperature_celsius: float = 20.0,
        tissue1_betas: Optional[Dict[str, float]] = None,
        tissue2_betas: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Runs comprehensive telomere, PMI, and somatic mosaicism analysis.
        """
        telomere_data = None
        if ts_ratio is not None:
            telomere_data = self.estimate_telomere_age(ts_ratio=ts_ratio)

        pmi_data = None
        if observed_pmi_beta is not None:
            pmi_data = self.estimate_post_mortem_interval(
                observed_beta=observed_pmi_beta,
                ambient_temperature_celsius=ambient_temperature_celsius,
            )

        mosaicism_data = None
        if tissue1_betas is not None and tissue2_betas is not None:
            mosaicism_data = self.compute_somatic_mosaicism_index(
                tissue1_betas=tissue1_betas,
                tissue2_betas=tissue2_betas,
            )

        shield_statement = (
            "IMPORTANT (Telomere Length & Post-Mortem Epigenetics Legal Shield): Relative telomere length (T/S) and "
            "post-mortem CpG de-methylation kinetics (ADH) quantify biological wear and post-mortem thermal exposure. "
            "PMI estimates must be cross-validated with forensic entomology and pathology findings."
        )

        return {
            "telomere": telomere_data,
            "pmi": pmi_data,
            "mosaicism": mosaicism_data,
            "prosecutors_fallacy_shield": shield_statement,
        }
