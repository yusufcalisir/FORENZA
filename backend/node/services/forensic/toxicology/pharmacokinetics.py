"""
FORENZA Ethanol Widmark Pharmacokinetic & Postmortem Redistribution Auditor.
Calculates Blood Alcohol Concentration (BAC) clearance: BAC_t = BAC_0 - beta * t
Audits Postmortem Redistribution (PMR) ratio R_PMR = C_cardiac / C_peripheral.

Reference:
  Widmark EMP (1932) Die theoretischen Grundlagen und die praktische Verwendbarkeit der gerichtlich-medizinischen Alkoholbestimmung.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class WidmarkBacResult:
    sample_id: str
    bac_initial_g_per_dl: float
    elapsed_hours: float
    elimination_rate_beta: float       # Standard beta = 0.015 g/dL per hour
    bac_current_g_per_dl: float
    time_to_sobriety_hours: float
    pmr_ratio: float                    # C_cardiac / C_peripheral ratio
    pmr_interpretation: str
    widmark_summary: str


class EthanolWidmarkAuditor:
    """
    Audits ethanol clearance rates and postmortem redistribution ratios.
    """

    def calculate_widmark_bac(
        self,
        sample_id: str,
        bac_initial: float,
        elapsed_hours: float,
        beta: float = 0.015,
        c_cardiac: Optional[float] = None,
        c_peripheral: Optional[float] = None
    ) -> WidmarkBacResult:
        # BAC_t = BAC_0 - beta * t
        bac_current = max(0.0, bac_initial - (beta * elapsed_hours))
        sobriety_hours = round(bac_initial / beta, 2) if beta > 0 else 0.0

        # PMR Ratio = C_cardiac / C_peripheral
        if c_cardiac is not None and c_peripheral is not None and c_peripheral > 0:
            pmr = round(c_cardiac / c_peripheral, 2)
            if pmr > 1.5:
                pmr_desc = "HIGH_PMR_ELEVATION: Significant postmortem cardiac diffusion artifact. Peripheral blood concentration represents true antemortem BAC."
            elif pmr < 0.8:
                pmr_desc = "SEQUESTRATION: Cardiac blood ethanol depleted relative to femoral blood."
            else:
                pmr_desc = "STABLE_PMR: Minimal postmortem redistribution artifact (PMR ~ 1.0)."
        else:
            pmr = 1.00
            pmr_desc = "PMR_UNAUDITED: Peripheral/cardiac paired blood specimens not available."

        summary = f"Widmark BAC Analysis for {sample_id}: Current BAC = {bac_current:.3f} g/dL (Elapsed = {elapsed_hours}h). Sobriety in {sobriety_hours}h. PMR = {pmr}."

        return WidmarkBacResult(
            sample_id=sample_id,
            bac_initial_g_per_dl=round(bac_initial, 3),
            elapsed_hours=elapsed_hours,
            elimination_rate_beta=beta,
            bac_current_g_per_dl=round(bac_current, 3),
            time_to_sobriety_hours=sobriety_hours,
            pmr_ratio=pmr,
            pmr_interpretation=pmr_desc,
            widmark_summary=summary
        )
