"""
FORENZA Multi-Tissue Epigenetic Calibration Engine (Pillar 4 §2.1 & §4).

Manages tissue-specific baseline calibration offsets (Delta_tissue) and dedicated models
across Whole Blood, Saliva/Buccal, Semen, Bone, Dental Pulp, and Cartilage.
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from backend.node.services.forensic.epigenetics.clocks.schemas import (
    EpigeneticTissueType,
    MethylationSample,
    EpigeneticAgeResult,
    ClockGeneration,
)


@dataclass
class TissueCalibrationProfile:
    """Tissue-specific calibration offset and baseline precision profile."""
    tissue_type: EpigeneticTissueType
    baseline_offset_years: float
    reference_mae_years: float
    description: str
    description_tr: str
    biological_rationale: str


TISSUE_CALIBRATION_REGISTRY: Dict[EpigeneticTissueType, TissueCalibrationProfile] = {
    EpigeneticTissueType.WHOLE_BLOOD: TissueCalibrationProfile(
        tissue_type=EpigeneticTissueType.WHOLE_BLOOD,
        baseline_offset_years=0.00,
        reference_mae_years=3.20,
        description="Whole Blood & Evidentiary Bloodstains",
        description_tr="Tam Kan & Adli Kan Lekeleri",
        biological_rationale="Gold standard reference tissue for forensic epigenetic age calibration.",
    ),
    EpigeneticTissueType.SALIVA_BUCCAL: TissueCalibrationProfile(
        tissue_type=EpigeneticTissueType.SALIVA_BUCCAL,
        baseline_offset_years=2.45,
        reference_mae_years=3.80,
        description="Saliva & Buccal Epithelial Swabs",
        description_tr="Tükürük & Bukkal Epitel Sürüntüleri",
        biological_rationale="Buccal cells exhibit slight hypermethylation relative to leukocytes, requiring a +2.45y offset.",
    ),
    EpigeneticTissueType.SEMEN: TissueCalibrationProfile(
        tissue_type=EpigeneticTissueType.SEMEN,
        baseline_offset_years=18.60,
        reference_mae_years=4.50,
        description="Seminal Fluid & Sperm Fractions",
        description_tr="Semen & Sperm Fraksiyonları",
        biological_rationale="Germline sperm DNA undergoes profound global hypomethylation during spermatogenesis, necessitating a +18.60y offset.",
    ),
    EpigeneticTissueType.BONE: TissueCalibrationProfile(
        tissue_type=EpigeneticTissueType.BONE,
        baseline_offset_years=1.15,
        reference_mae_years=3.70,
        description="Skeletal Remains & Cortical Bone",
        description_tr="İskelet Kalıntıları & Kortikal Kemik",
        biological_rationale="Osteocytes in dense cortical bone display slight baseline elevation (+1.15y) with high stability.",
    ),
    EpigeneticTissueType.TEETH: TissueCalibrationProfile(
        tissue_type=EpigeneticTissueType.TEETH,
        baseline_offset_years=0.80,
        reference_mae_years=4.80,
        description="Dental Pulp & Odontoblasts",
        description_tr="Diş Pulpası & Odontoblastlar",
        biological_rationale="Dental pulp yields excellent trauma-protected DNA, exhibiting +0.80y baseline shift.",
    ),
    EpigeneticTissueType.CARTILAGE: TissueCalibrationProfile(
        tissue_type=EpigeneticTissueType.CARTILAGE,
        baseline_offset_years=0.50,
        reference_mae_years=4.30,
        description="Post-Mortem Articular Cartilage",
        description_tr="Ölüm Sonrası Eklem Kıkırdağı",
        biological_rationale="Chondrocytes preserve intact DNA in decomposed remains lacking soft tissue (+0.50y offset).",
    ),
    EpigeneticTissueType.EPIDERMIS: TissueCalibrationProfile(
        tissue_type=EpigeneticTissueType.EPIDERMIS,
        baseline_offset_years=-1.20,
        reference_mae_years=3.90,
        description="Epidermal Skin & Contact Touch DNA",
        description_tr="Epidermal Deri & Temas DNA'sı",
        biological_rationale="Keratinocyte rapid turnover results in a slight downward baseline offset (-1.20y).",
    ),
    EpigeneticTissueType.MULTI_TISSUE: TissueCalibrationProfile(
        tissue_type=EpigeneticTissueType.MULTI_TISSUE,
        baseline_offset_years=0.00,
        reference_mae_years=3.60,
        description="Generic Multi-Tissue Consensus",
        description_tr="Genel Çoklu Doku Konsensüsü",
        biological_rationale="Unconstrained pan-tissue baseline with zero net offset.",
    ),
}


class TissueCalibrationEngine:
    """Engine providing tissue-specific calibration offsets and corrections."""

    @classmethod
    def get_calibration_profile(cls, tissue_type: EpigeneticTissueType) -> TissueCalibrationProfile:
        """Retrieve tissue calibration profile."""
        return TISSUE_CALIBRATION_REGISTRY.get(
            tissue_type,
            TISSUE_CALIBRATION_REGISTRY[EpigeneticTissueType.MULTI_TISSUE]
        )

    @classmethod
    def get_offset_for_tissue(cls, tissue_type: EpigeneticTissueType) -> float:
        """Get calibrated baseline offset Delta_tissue in years."""
        return cls.get_calibration_profile(tissue_type).baseline_offset_years

    @classmethod
    def calibrate_predicted_age(
        cls,
        uncalibrated_age: float,
        tissue_type: EpigeneticTissueType,
    ) -> Tuple[float, float, str]:
        """
        Apply tissue baseline calibration offset to raw predicted age.
        Returns: (calibrated_age, offset_applied, rationale).
        """
        profile = cls.get_calibration_profile(tissue_type)
        calibrated_age = max(0.0, uncalibrated_age + profile.baseline_offset_years)
        return round(calibrated_age, 2), profile.baseline_offset_years, profile.biological_rationale
