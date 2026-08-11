"""
FORENZA Forensic Entomology Minimum Postmortem Interval (PMI_min) Engine.
Estimates elapsed time since colonization (PMI_min) using Accumulated Degree Hours (ADH) thermal models:
  ADH = (T_ambient - T_base) * t_hours

Reference:
  Amendt et al. (2011) Best practice in forensic entomology: Standards and guidelines.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SpeciesDevelopmentData:
    species_name: str                  # e.g. 'Calliphora vicina', 'Lucilia sericata'
    base_temp_celsius: float           # T_base development threshold
    adh_instar_1: float                # ADH required to reach 1st instar
    adh_instar_2: float                # ADH required to reach 2nd instar
    adh_instar_3: float                # ADH required to reach 3rd instar
    adh_pupa: float                    # ADH required to reach pupation
    adh_adult: float                   # ADH required to reach adult emergence


SPECIES_CATALOGUE: Dict[str, SpeciesDevelopmentData] = {
    "Calliphora vicina": SpeciesDevelopmentData(
        species_name="Calliphora vicina",
        base_temp_celsius=6.0,
        adh_instar_1=350.0,
        adh_instar_2=850.0,
        adh_instar_3=2200.0,
        adh_pupa=4500.0,
        adh_adult=9200.0
    ),
    "Lucilia sericata": SpeciesDevelopmentData(
        species_name="Lucilia sericata",
        base_temp_celsius=9.0,
        adh_instar_1=280.0,
        adh_instar_2=720.0,
        adh_instar_3=1950.0,
        adh_pupa=4100.0,
        adh_adult=8500.0
    ),
    "Sarcophaga carnaria": SpeciesDevelopmentData(
        species_name="Sarcophaga carnaria",
        base_temp_celsius=8.0,
        adh_instar_1=300.0,
        adh_instar_2=780.0,
        adh_instar_3=2050.0,
        adh_pupa=4300.0,
        adh_adult=8900.0
    )
}


@dataclass
class EntomologyPmiResult:
    species_name: str
    development_stage: str             # 'INSTAR_1', 'INSTAR_2', 'INSTAR_3', 'PUPA', 'ADULT_EMERGENCE'
    mean_ambient_temp_celsius: float
    effective_temp_celsius: float      # T_ambient - T_base
    required_adh: float                # Required ADH to reach observed stage
    estimated_pmi_hours: float         # Minimum elapsed time in hours
    estimated_pmi_days: float          # Minimum elapsed time in days
    pmi_formatted_range: str
    entomology_summary: str


class EntomologyPmiEstimator:
    """
    Computes minimum Postmortem Interval (PMI_min) from thermal accumulation models.
    """

    def estimate_pmi(
        self,
        species_name: str,
        stage: str,
        mean_ambient_temp_celsius: float
    ) -> EntomologyPmiResult:
        data = SPECIES_CATALOGUE.get(species_name, SPECIES_CATALOGUE["Calliphora vicina"])

        effective_temp = max(0.1, mean_ambient_temp_celsius - data.base_temp_celsius)

        stage_upper = stage.upper()
        if "INSTAR_1" in stage_upper or "1" in stage_upper:
            req_adh = data.adh_instar_1
        elif "INSTAR_2" in stage_upper or "2" in stage_upper:
            req_adh = data.adh_instar_2
        elif "INSTAR_3" in stage_upper or "3" in stage_upper:
            req_adh = data.adh_instar_3
        elif "PUPA" in stage_upper:
            req_adh = data.adh_pupa
        else:
            req_adh = data.adh_adult

        # PMI_hours = ADH / (T_ambient - T_base)
        pmi_hours = round(req_adh / effective_temp, 1)
        pmi_days = round(pmi_hours / 24.0, 1)

        # Margin of error +/- 10%
        min_days = round(pmi_days * 0.9, 1)
        max_days = round(pmi_days * 1.1, 1)
        pmi_range = f"{min_days} - {max_days} days ({pmi_hours} hours)"

        summary = f"Forensic Entomology PMI_min Estimate for {data.species_name} ({stage}): {pmi_days} days ({pmi_range}) based on ADH={req_adh}."

        return EntomologyPmiResult(
            species_name=data.species_name,
            development_stage=stage,
            mean_ambient_temp_celsius=mean_ambient_temp_celsius,
            effective_temp_celsius=round(effective_temp, 1),
            required_adh=req_adh,
            estimated_pmi_hours=pmi_hours,
            estimated_pmi_days=pmi_days,
            pmi_formatted_range=pmi_range,
            entomology_summary=summary
        )
