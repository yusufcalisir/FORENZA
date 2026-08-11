"""
FORENZA Plant Geographic Association & Habitat Origin Auditor.
Infers ecological habitat origin, geographic association, and seasonal bloom windows from botanical assemblages.

Reference:
  Mildenhall et al. (2006) Forensic Palynology: Why do it and how it works.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PlantAssemblageEntry:
    species_name: str
    abundance_percentage: float        # Relative pollen/seed count percentage


@dataclass
class HabitatInferenceResult:
    sample_id: str
    inferred_habitat_type: str         # 'MONTANE_CONIFEROUS', 'RIPARIAN_WETLAND', 'URBAN_RUDERAL', 'COASTAL_DUNE'
    geographic_association: str        # e.g. 'Northern Temperate Woodland Zone'
    seasonal_bloom_window: str         # e.g. 'April - June (Spring Bloom)'
    habitat_match_lr: float            # Likelihood ratio of crime scene origin match
    habitat_summary: str


class PlantHabitatAuditor:
    """
    Audits botanical assemblage compositions to infer geographic scene origin.
    """

    def infer_habitat(self, sample_id: str, assemblage: List[PlantAssemblageEntry]) -> HabitatInferenceResult:
        species_list = [p.species_name for p in assemblage]
        spec_set = set(species_list)

        if "Pinus sylvestris" in spec_set:
            habitat = "MONTANE_CONIFEROUS"
            geo = "Boreal / Subalpine Coniferous Forest Biome"
            season = "May - July (Late Spring / Early Summer)"
            lr = 240.0
        elif "Taraxacum officinale" in spec_set:
            habitat = "URBAN_RUDERAL"
            geo = "Anthropogenic Urban & Disturbed Ruderal Habitat"
            season = "March - October (Multi-season Bloom)"
            lr = 45.0
        else:
            habitat = "RIPARIAN_WETLAND"
            geo = "Temperate Riparian & Floodplain Marshland"
            season = "April - August (Spring / Summer)"
            lr = 110.0

        summary = f"Botanical Habitat Inference for {sample_id}: Inferred {habitat} ({geo}) with LR_habitat = {lr}."

        return HabitatInferenceResult(
            sample_id=sample_id,
            inferred_habitat_type=habitat,
            geographic_association=geo,
            seasonal_bloom_window=season,
            habitat_match_lr=lr,
            habitat_summary=summary
        )
