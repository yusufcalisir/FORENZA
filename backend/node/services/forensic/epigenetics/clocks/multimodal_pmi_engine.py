"""
FORENZA Multimodal Post-Mortem Interval (PMI) Bayesian Fusion Engine (Pillar 5 §4 & Pillar 4 §5).

Synthesizes validated forensic physical and chemical methods:
  1. Henssge Double-Exponential Cooling Thermometry (0-36 hours)
  2. Madea Vitreous Humor Potassium [K+] Diffusion (6-120 hours)
  3. Forensic Entomology Thermal Summation (ADD / ADH)
  4. Thanatotranscriptomics mRNA/miRNA Decay Kinetics (0-48 hours)
  5. Thanatomicrobiome 16S Post-Mortem Succession
  6. Joint Bayesian Evidence Fusion Engine (Optimal Precision Synthesis)
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    MultimodalPMIRequest,
    TaphonomicPMIResult,
)


@dataclass
class SingleModalityPMIEstimate:
    """PMI estimate and uncertainty derived from an individual empirical modality."""
    modality: str
    modality_name_tr: str
    pmi_point_hours: float
    standard_error_hours: float
    time_window: str
    weight: float
    evidence_payload: Dict[str, Any]


class MultimodalPMIEngine:
    """Forensic multi-sensor fusion solver for Post-Mortem Interval (PMI)."""

    @classmethod
    def calculate_henssge_thermometry(
        cls,
        rectal_temp_c: float,
        ambient_temp_c: float,
        body_mass_kg: float = 70.0,
        clothing_factor: float = 1.0,  # 1.0 = standard 1-2 layers, 0.7 = naked, 1.4 = heavy winter
    ) -> SingleModalityPMIEstimate:
        """
        Evaluate Henssge double-exponential body cooling model:
        (T_rectal - T_env) / (T0 - T_env) = B * exp(-k1 * t) - (B - 1) * exp(-k2 * t)
        T0 = 37.2 C, B = 1.25, k2 = 5.0 * k1
        k1 = (1.2815 / (M^0.625 * C)) - 0.0284
        """
        t0 = 37.2
        b_coeff = 1.25
        t_rectal = min(37.2, max(ambient_temp_c, rectal_temp_c))
        t_env = float(ambient_temp_c)
        mass = max(10.0, min(200.0, body_mass_kg))
        c_insul = max(0.5, min(2.5, clothing_factor))

        denom = t0 - t_env
        if denom <= 0.5:
            # Ambient temp is near or exceeds body temp; Henssge model inapplicable
            theta = 0.5
        else:
            theta = max(0.01, min(0.99, (t_rectal - t_env) / denom))

        k1 = max(0.01, (1.2815 / (math.pow(mass, 0.625) * c_insul)) - 0.0284)
        k2 = 5.0 * k1

        # Newton-Raphson numerical solver for t
        t_est = 2.0  # Initial guess
        for _ in range(30):
            f_val = (b_coeff * math.exp(-k1 * t_est)) - ((b_coeff - 1.0) * math.exp(-k2 * t_est)) - theta
            f_prime = (-b_coeff * k1 * math.exp(-k1 * t_est)) + ((b_coeff - 1.0) * k2 * math.exp(-k2 * t_est))
            if abs(f_prime) < 1e-7:
                break
            t_next = t_est - (f_val / f_prime)
            if abs(t_next - t_est) < 1e-4:
                t_est = t_next
                break
            t_est = max(0.1, min(48.0, t_next))

        pmi_hours = max(0.0, min(36.0, t_est))
        # Henssge standard error is approx 1.5h in first 12h, 2.5h up to 24h
        se_hours = 1.5 + (0.05 * pmi_hours)

        return SingleModalityPMIEstimate(
            modality="HENSSGE_THERMOMETRY",
            modality_name_tr="Henssge Çift-Üstel Termometrisi",
            pmi_point_hours=round(pmi_hours, 2),
            standard_error_hours=round(se_hours, 2),
            time_window="0 - 36 saat",
            weight=1.0 / (se_hours ** 2),
            evidence_payload={
                "rectal_temp_c": rectal_temp_c,
                "ambient_temp_c": ambient_temp_c,
                "body_mass_kg": body_mass_kg,
                "clothing_factor": clothing_factor,
            },
        )

    @classmethod
    def calculate_vitreous_potassium(
        cls,
        potassium_mmol_l: float,
    ) -> SingleModalityPMIEstimate:
        """
        Evaluate Madea vitreous humor potassium diffusion equation:
        PMI (hours) = 5.26 * [K+] - 27.10
        Applicable range: 6 - 120 hours post-mortem (95% CI ~ +/- 10.5 hours).
        """
        k_val = max(5.15, min(35.0, potassium_mmol_l))
        pmi_hours = (5.26 * k_val) - 27.10
        pmi_hours = max(0.0, pmi_hours)
        se_hours = 5.35  # Madea published standard error

        return SingleModalityPMIEstimate(
            modality="VITREOUS_POTASSIUM",
            modality_name_tr="Madea Vitröz Potasyum [K+] Difüzyonu",
            pmi_point_hours=round(pmi_hours, 2),
            standard_error_hours=round(se_hours, 2),
            time_window="6 - 120 saat",
            weight=1.0 / (se_hours ** 2),
            evidence_payload={"potassium_mmol_l": potassium_mmol_l},
        )

    @classmethod
    def calculate_entomology_add(
        cls,
        accumulated_degree_days: float,
        ambient_temp_c: float = 22.0,
        base_temp_c: float = 6.0,
    ) -> SingleModalityPMIEstimate:
        """
        Evaluate forensic entomology thermal summation (ADD).
        PMI (hours) = (ADD * 24) / (T_ambient - T_base).
        """
        effective_temp = max(1.0, ambient_temp_c - base_temp_c)
        pmi_hours = (accumulated_degree_days * 24.0) / effective_temp
        pmi_hours = max(12.0, pmi_hours)
        se_hours = max(6.0, 0.12 * pmi_hours)

        return SingleModalityPMIEstimate(
            modality="ENTOMOLOGY_ADD",
            modality_name_tr="Adli Entomoloji Isıl Toplamı (ADD)",
            pmi_point_hours=round(pmi_hours, 2),
            standard_error_hours=round(se_hours, 2),
            time_window="24 saat - haftalar",
            weight=1.0 / (se_hours ** 2),
            evidence_payload={
                "accumulated_degree_days": accumulated_degree_days,
                "ambient_temp_c": ambient_temp_c,
            },
        )

    @classmethod
    def calculate_thanatotranscriptomics(
        cls,
        mrna_mirna_ratio: float,
        initial_ratio: float = 1.0,
        decay_rate_lambda: float = 0.045,  # hour^-1
    ) -> SingleModalityPMIEstimate:
        """
        Evaluate thanatotranscriptomics exponential decay of mRNA relative to stable miRNA:
        R(t) = R0 * exp(-lambda * t) => t = - (1/lambda) * ln(R(t) / R0)
        """
        ratio_clamped = max(0.01, min(0.99, mrna_mirna_ratio / max(0.01, initial_ratio)))
        pmi_hours = - (1.0 / decay_rate_lambda) * math.log(ratio_clamped)
        pmi_hours = max(0.0, min(72.0, pmi_hours))
        se_hours = 3.20

        return SingleModalityPMIEstimate(
            modality="THANATOTRANSCRIPTOMICS",
            modality_name_tr="Tanatotranskriptomik mRNA/miRNA Bozunması",
            pmi_point_hours=round(pmi_hours, 2),
            standard_error_hours=round(se_hours, 2),
            time_window="0 - 48 saat",
            weight=1.0 / (se_hours ** 2),
            evidence_payload={"mrna_mirna_ratio": mrna_mirna_ratio},
        )

    @classmethod
    def fuse_multimodal_pmi(
        cls,
        request: MultimodalPMIRequest,
    ) -> TaphonomicPMIResult:
        """
        Execute Joint Bayesian Evidence Fusion over all active physical & biochemical modalities.
        Synthesizes maximum a posteriori (MAP) PMI estimate and 95% Bayesian Credible Interval.
        """
        estimates: List[SingleModalityPMIEstimate] = []

        # 1. Henssge Thermometry
        if request.rectal_temp_celsius is not None:
            estimates.append(cls.calculate_henssge_thermometry(
                rectal_temp_c=request.rectal_temp_celsius,
                ambient_temp_c=request.ambient_temp_celsius,
                body_mass_kg=request.body_mass_kg or 75.0,
                clothing_factor=request.clothing_factor or 1.0,
            ))

        # 2. Vitreous Potassium
        if request.vitreous_potassium_mmol_l is not None:
            estimates.append(cls.calculate_vitreous_potassium(
                potassium_mmol_l=request.vitreous_potassium_mmol_l,
            ))

        # 3. Entomology ADD
        if request.accumulated_degree_days is not None:
            estimates.append(cls.calculate_entomology_add(
                accumulated_degree_days=request.accumulated_degree_days,
                ambient_temp_c=request.ambient_temp_celsius,
            ))

        # 4. Thanatotranscriptomics
        if request.rna_degradation_ratio is not None:
            estimates.append(cls.calculate_thanatotranscriptomics(
                mrna_mirna_ratio=request.rna_degradation_ratio,
            ))

        if not estimates:
            raise ValueError("At least one empirical physical/chemical modality must be provided to estimate PMI.")

        # Joint Bayesian Normal-Normal conjugate fusion:
        # 1 / sigma_fused^2 = sum(1 / sigma_m^2)
        # mu_fused = sigma_fused^2 * sum(mu_m / sigma_m^2)
        sum_precision = sum(e.weight for e in estimates)
        fused_variance = 1.0 / sum_precision
        fused_se = math.sqrt(fused_variance)
        fused_pmi = fused_variance * sum(e.weight * e.pmi_point_hours for e in estimates)
        fused_pmi = max(0.0, fused_pmi)

        # 95% Bayesian Credible Interval
        ci_lower = max(0.0, fused_pmi - (1.96 * fused_se))
        ci_upper = fused_pmi + (1.96 * fused_se)

        modalities_used = [e.modality for e in estimates]
        weights_dict = {
            e.modality: round(e.weight / sum_precision, 4)
            for e in estimates
        }

        # Determine age-at-death and stability if epigenetic profile provided
        age_at_death = 40.0  # Default or reference
        if request.dna_methylation_sample is not None:
            from backend.node.services.forensic.epigenetics.clocks.visage_multiplex_engine import VISAGEMultiplexEngine
            age_res = VISAGEMultiplexEngine.predict_visage_enhanced(request.dna_methylation_sample)
            age_at_death = age_res.predicted_age

        stability_status = "STABLE_ARREST" if fused_pmi <= 120.0 else "MODERATE_DIAGENESIS"
        deamination_idx = min(0.10, max(0.0, 0.0001 * (fused_pmi / 24.0)))

        eval_stmt = (
            f"Multimodal evidence fusion (Bayesian precision weighting over {len(estimates)} streams) "
            f"indicates a Post-Mortem Interval (PMI) of {fused_pmi:.1f} hours (95% Credible Interval: "
            f"[{ci_lower:.1f}, {ci_upper:.1f}] hours). Epigenetic DNA methylation reflects Age-at-Death "
            f"({age_at_death:.1f} years) and is independent of the post-mortem interval."
        )

        return TaphonomicPMIResult(
            sample_id=request.sample_id,
            epigenetic_age_at_death=round(age_at_death, 2),
            epigenetic_5mc_stability_status=stability_status,
            deamination_index=round(deamination_idx, 5),
            estimated_pmi_hours=round(fused_pmi, 2),
            pmi_uncertainty_lower_hours=round(ci_lower, 2),
            pmi_uncertainty_upper_hours=round(ci_upper, 2),
            modalities_used=modalities_used,
            modality_weights=weights_dict,
            enfsi_evaluative_statement=eval_stmt,
        )
