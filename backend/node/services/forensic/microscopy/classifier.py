"""
FORENZA Microscopy Intelligence & Forensic Hair Analysis Engine.
Analyzes microscopic cell morphometry (sperm head length/width, acrosome ratio) and hair microstructures.
Calculates Hair Medullary Index: I_medulla = d_medulla / D_hair
Discriminates Human (I < 0.33) vs. Animal (I >= 0.50) hair evidence, and audits follicular root sheath presence
to route samples for Nuclear 24-locus STR profiling vs. Mitochondrial DNA (HV1/HV2) sequencing.

References:
  Deedrick DW (2004) Hairs, Fibers, Crime, and Evidence. FBI Forensic Science Communications.
  SWGMAT (2005) Forensic Human Hair Examination Guidelines.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CellMorphometry:
    cell_id: str
    cell_type: str                     # 'Spermatozoa', 'Epithelial', 'Leukocyte'
    head_length_um: float
    head_width_um: float
    acrosome_coverage_pct: float
    normal_morphology: bool


@dataclass
class HairMorphologyResult:
    hair_id: str
    hair_diameter_um: float
    medulla_diameter_um: float
    medullary_index: float
    species_origin: str                # 'HUMAN', 'NON_HUMAN_ANIMAL'
    root_status: str                   # 'ANAGEN_WITH_SHEATH', 'CATAGEN_WITH_SHEATH', 'TELOGEN_NO_SHEATH', 'SHAFT_ONLY'
    dna_routing: str                   # 'NUCLEAR_STR_OPTIMAL', 'MITOCHONDRIAL_HV1_HV2'
    microscopy_summary: str


class MicroscopyIntelligenceEngine:
    """
    Evaluates microscopic cell morphometry and hair microstructures for species origin and DNA routing.
    """

    def classify_sperm_cell(
        self,
        cell_id: str,
        head_length_um: float,
        head_width_um: float,
        acrosome_coverage_pct: float
    ) -> CellMorphometry:
        # Standard human sperm head: length 3.0-5.0 um, width 2.0-3.0 um, acrosome 40-70%
        normal = (3.0 <= head_length_um <= 5.5) and (2.0 <= head_width_um <= 3.5) and (40.0 <= acrosome_coverage_pct <= 70.0)
        return CellMorphometry(
            cell_id=cell_id,
            cell_type="Spermatozoa",
            head_length_um=head_length_um,
            head_width_um=head_width_um,
            acrosome_coverage_pct=acrosome_coverage_pct,
            normal_morphology=normal
        )

    def analyze_hair_morphology(
        self,
        hair_id: str,
        hair_diameter_um: float,
        medulla_diameter_um: float,
        root_status: str
    ) -> HairMorphologyResult:
        if hair_diameter_um <= 0:
            raise ValueError("Hair diameter must be greater than zero.")

        # Medullary Index I = d_medulla / D_hair
        i_medulla = round(medulla_diameter_um / hair_diameter_um, 4)

        if i_medulla < 0.33:
            species = "HUMAN"
        elif i_medulla >= 0.50:
            species = "NON_HUMAN_ANIMAL"
        else:
            species = "INDETERMINATE_SPECIES"

        # DNA Extraction Routing
        if "WITH_SHEATH" in root_status.upper():
            dna_route = "NUCLEAR_STR_OPTIMAL"
        else:
            dna_route = "MITOCHONDRIAL_HV1_HV2"

        summary = (
            f"Hair Microscopy for {hair_id}: Medullary Index = {i_medulla:.2f} ({species}). "
            f"Root = {root_status}. Recommended DNA Strategy: {dna_route}."
        )

        return HairMorphologyResult(
            hair_id=hair_id,
            hair_diameter_um=hair_diameter_um,
            medulla_diameter_um=medulla_diameter_um,
            medullary_index=i_medulla,
            species_origin=species,
            root_status=root_status.upper(),
            dna_routing=dna_route,
            microscopy_summary=summary
        )
