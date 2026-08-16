r"""
FORENZA Forensic Entomology & Calliphoridae Minimum PMI Engine — Module 23.

Implements verbatim from Pillar 5 Research §3 & §6:
  - §3.1 Accumulated Thermal Energy Models (ADD / ADH)
  - §3.2 Dipteran Species Calibration Parameters (*L. sericata*, *C. vicina*, *C. albiceps*, *P. regina*)
  - §3.2 Larval Mass Thermal Self-Heating Correction (+1.5°C to +3.5°C)
  - Backward Hourly Temperature Integration for Minimum PMI ($PMI_{\min}$)
"""


import math
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta


# ── Dipteran Species Thermal Calibration Database (Research §3.2 & §6) ────────

DIPTERAN_SPECIES_DATABASE: Dict[str, Dict[str, Any]] = {
    "Lucilia sericata": {
        "common_name": "Common Green Bottle Fly",
        "t_base": 9.0,
        "stages_adh": {
            "Egg": 240.0,
            "1st Instar": 480.0,
            "2nd Instar": 800.0,
            "3rd Instar Feeding": 1254.5,
            "3rd Instar Post-Feeding": 2200.0,
            "Pupae": 5000.0,
            "Adult": 10174.5,
        }
    },
    "Calliphora vicina": {
        "common_name": "European Blue Bottle Fly",
        "t_base": 3.0,
        "stages_adh": {
            "Egg": 450.0,
            "1st Instar": 1170.0,
            "2nd Instar": 2250.0,
            "3rd Instar Feeding": 4050.0,
            "3rd Instar Post-Feeding": 6450.0,
            "Pupae": 9300.0,
            "Adult": 23670.0,
        }
    },
    "Chrysomya albiceps": {
        "common_name": "Banded Blowfly",
        "t_base": 10.2,
        "stages_adh": {
            "Egg": 260.0,
            "1st Instar": 740.0,
            "2nd Instar": 1340.0,
            "3rd Instar Feeding": 2440.0,
            "3rd Instar Post-Feeding": 4540.0,
            "Pupae": 8440.0,
            "Adult": 17760.0,
        }
    },
    "Phormia regina": {
        "common_name": "Black Blowfly",
        "t_base": 10.0,
        "stages_adh": {
            "Egg": 300.0,
            "1st Instar": 800.0,
            "2nd Instar": 1500.0,
            "3rd Instar Feeding": 2900.0,
            "3rd Instar Post-Feeding": 5100.0,
            "Pupae": 9200.0,
            "Adult": 19800.0,
        }
    }
}


class ForensicEntomologyEngine:
    """
    FORENZA Forensic Entomology & Minimum PMI Thermal Summation Engine.

    Derives verbatim from Pillar 5 Research §3 & §6.
    """

    def get_species_info(self, species_name: str) -> Dict[str, Any]:
        """Returns thermal calibration parameters for a supported dipteran species."""
        if species_name not in DIPTERAN_SPECIES_DATABASE:
            available = list(DIPTERAN_SPECIES_DATABASE.keys())
            raise ValueError(f"Unsupported species '{species_name}'. Available: {available}")
        return DIPTERAN_SPECIES_DATABASE[species_name]

    def calculate_adh_for_stage(
        self,
        species_name: str,
        development_stage: str,
    ) -> float:
        """Returns required cumulative ADH threshold for species development stage."""
        info = self.get_species_info(species_name)
        stages = info["stages_adh"]
        if development_stage not in stages:
            raise ValueError(
                f"Unknown development stage '{development_stage}' for {species_name}. "
                f"Valid stages: {list(stages.keys())}"
            )
        return float(stages[development_stage])

    def estimate_pmi_min(
        self,
        species_name: str,
        development_stage: str,
        hourly_temperatures: List[Dict[str, Any]],
        delta_t_mass: float = 0.0,
        sampling_time_iso: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Estimates Minimum Post-Mortem Interval (PMI_min) by integrating backwards through
        hourly ambient temperatures until cumulative ADH threshold is satisfied.
        """
        if not hourly_temperatures:
            raise ValueError("Hourly temperatures list cannot be empty for entomology PMI estimation.")

        if delta_t_mass < 0.0 or delta_t_mass > 5.0:
            raise ValueError(f"Larval mass thermal self-heating delta_t_mass must be between 0.0°C and 5.0°C, got {delta_t_mass}.")

        species_info = self.get_species_info(species_name)
        t_base = float(species_info["t_base"])
        target_adh = self.calculate_adh_for_stage(species_name, development_stage)

        # Parse and ensure temperatures are processed backwards from sampling time
        # Assuming list is chronologically ascending (latest at end)
        accumulated_adh = 0.0
        hours_counted = 0
        hourly_breakdown = []

        for idx in range(len(hourly_temperatures) - 1, -1, -1):
            h_entry = hourly_temperatures[idx]
            raw_temp = float(h_entry.get("temperature_c", 0.0))
            eff_temp = raw_temp + delta_t_mass
            adh_increment = max(0.0, eff_temp - t_base)

            accumulated_adh += adh_increment
            hours_counted += 1

            hourly_breakdown.append({
                "hours_before_sampling": hours_counted,
                "ambient_temp_c": raw_temp,
                "effective_temp_c": eff_temp,
                "adh_increment": round(adh_increment, 3),
                "cumulative_adh": round(accumulated_adh, 3),
            })

            if accumulated_adh >= target_adh:
                # Target ADH met! Calculate exact fractional hour interpolation
                excess_adh = accumulated_adh - target_adh
                if adh_increment > 0.0:
                    fraction = 1.0 - (excess_adh / adh_increment)
                    exact_hours = (hours_counted - 1) + max(0.0, min(1.0, fraction))
                else:
                    exact_hours = float(hours_counted)

                pmi_days = exact_hours / 24.0

                colonisation_time_str = None
                if sampling_time_iso:
                    try:
                        sampling_dt = datetime.fromisoformat(sampling_time_iso.replace("Z", "+00:00"))
                        colonisation_dt = sampling_dt - timedelta(hours=exact_hours)
                        colonisation_time_str = colonisation_dt.isoformat()
                    except Exception:
                        colonisation_time_str = None

                shield_statement = (
                    "IMPORTANT (EAFE / NAFEA Forensic Entomology Legal Shield): The estimated minimum PMI "
                    "(PMI_min) represents the Minimum Insect Colonisation Interval (MICI). It reflects the earliest "
                    "time blowfly eggs could have been deposited under recorded thermal regimes. Nocturnal oviposition "
                    "suppression, indoor delayed access, and maggot mass self-heating must be evaluated."
                )

                return {
                    "species": species_name,
                    "development_stage": development_stage,
                    "t_base_c": t_base,
                    "target_adh": target_adh,
                    "accumulated_adh": round(accumulated_adh, 2),
                    "pmi_min_hours": round(exact_hours, 2),
                    "pmi_min_days": round(pmi_days, 2),
                    "colonisation_timestamp": colonisation_time_str,
                    "delta_t_mass_applied_c": delta_t_mass,
                    "is_target_adh_satisfied": True,
                    "hours_integrated": hours_counted,
                    "prosecutors_fallacy_shield": shield_statement,
                }

        # If temperature history is exhausted before meeting target ADH:
        pmi_days = float(hours_counted) / 24.0
        return {
            "species": species_name,
            "development_stage": development_stage,
            "t_base_c": t_base,
            "target_adh": target_adh,
            "accumulated_adh": round(accumulated_adh, 2),
            "pmi_min_hours": round(float(hours_counted), 2),
            "pmi_min_days": round(pmi_days, 2),
            "colonisation_timestamp": None,
            "delta_t_mass_applied_c": delta_t_mass,
            "is_target_adh_satisfied": False,
            "hours_integrated": hours_counted,
            "warning": f"Insufficient historical weather data. Accumulated {accumulated_adh:.1f} ADH out of required {target_adh:.1f} ADH.",
            "prosecutors_fallacy_shield": (
                "WARNING: Insufficient weather history to reach full developmental ADH. "
                "The reported PMI_min is a lower bound based solely on available data."
            ),
        }
