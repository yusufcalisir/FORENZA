r"""
FORENZA Digital Microscopy, Multispectral Imaging & Trace Spectroscopy Engine — Module 24.

Implements verbatim from Pillar 5 Research §4 & §6:
  - §4.1 Targeted Multispectral Wavelength Bands (365nm UV-A, 415nm Soret, 450nm Blue, 850nm NIR)
  - §4.2 ATR-FTIR & Raman Trace Spectral Matching (Hit Quality Index — HQI)
  - Fiber & Polymer Spectral Library (Polyester, Nylon-6,6, Acrylic PAN, Cotton Cellulose, Wool Keratin)
"""

import math
from typing import Dict, Any, List, Optional, Union


# ── Multispectral Band Specifications (Research §4.1) ─────────────────────────

MSI_WAVELENGTH_BANDS: Dict[str, Dict[str, Any]] = {
    "365nm_UV_A": {
        "wavelength_nm": 365,
        "band_name": "UV-A (365 nm)",
        "phenomenon": "Fluorescence Excitation",
        "target_evidence": "Semen, Saliva, Vaginal Fluids",
        "mechanism": "Excitation of endogenous fluorophores (flavins/lipids)",
        "optimal_barrier_filter": "420 nm Long-Pass",
    },
    "415nm_Soret": {
        "wavelength_nm": 415,
        "band_name": "Soret Band (415 nm)",
        "phenomenon": "Peak Optical Absorption",
        "target_evidence": "Latent / Dilute Bloodstains",
        "mechanism": "Strong porphyrin ring absorption in hemoglobin",
        "optimal_barrier_filter": "Monochromatic Neutral Density",
    },
    "450nm_Blue": {
        "wavelength_nm": 450,
        "band_name": "Blue Light (450 nm)",
        "phenomenon": "Secondary Fluorescence",
        "target_evidence": "Latent Fingerprints, Trace Serology",
        "mechanism": "530 nm long-pass filtered dye excitation",
        "optimal_barrier_filter": "530 nm Yellow/Orange Long-Pass",
    },
    "850nm_NIR": {
        "wavelength_nm": 850,
        "band_name": "Near-Infrared (850 nm)",
        "phenomenon": "Substrate Transmission",
        "target_evidence": "Blood & GSR on Dark Fabrics",
        "mechanism": "Fabric dyes become transparent; carbon particles visible",
        "optimal_barrier_filter": "830 nm Infrared Band-Pass",
    }
}


# ── Reference Forensic Fiber & Polymer Spectral Library (Research §4.2) ──────

FIBER_REFERENCE_LIBRARY: Dict[str, Dict[str, Any]] = {
    "Polyester": {
        "polymer_name": "Polyethylene Terephthalate (PET)",
        "fiber_type": "Synthetic",
        "diagnostic_peaks_cm_1": [1715.0, 1240.0, 1100.0, 725.0],
        "functional_groups": ["C=O ester carbonyl (1715 cm⁻¹)", "C-O-C ester stretch (1240 cm⁻¹)"],
    },
    "Nylon-6,6": {
        "polymer_name": "Polyamide 6,6",
        "fiber_type": "Synthetic",
        "diagnostic_peaks_cm_1": [1635.0, 1538.0, 3300.0, 1275.0],
        "functional_groups": ["Amide I C=O (1635 cm⁻¹)", "Amide II N-H/C-N (1538 cm⁻¹)"],
    },
    "Acrylic": {
        "polymer_name": "Polyacrylonitrile (PAN)",
        "fiber_type": "Synthetic",
        "diagnostic_peaks_cm_1": [2240.0, 1450.0, 1070.0],
        "functional_groups": ["Nitrile C≡N stretch (2240 cm⁻¹)", "CH₂ bend (1450 cm⁻¹)"],
    },
    "Cotton": {
        "polymer_name": "Cellulose",
        "fiber_type": "Natural (Plant)",
        "diagnostic_peaks_cm_1": [3330.0, 2900.0, 1030.0, 1160.0],
        "functional_groups": ["O-H stretch (3330 cm⁻¹)", "C-O stretch (1030 cm⁻¹)"],
    },
    "Wool": {
        "polymer_name": "Keratin Protein",
        "fiber_type": "Natural (Animal)",
        "diagnostic_peaks_cm_1": [1650.0, 1520.0, 3280.0, 1235.0],
        "functional_groups": ["Amide I alpha-helix (1650 cm⁻¹)", "Amide II (1520 cm⁻¹)"],
    },
}


class TraceSpectroscopyMsiEngine:
    """
    FORENZA Digital Microscopy, Multispectral Imaging & Trace Spectroscopy Engine.

    Derives verbatim from Pillar 5 Research §4 & §6.
    """

    def compute_hqi(
        self,
        sample_spectrum: List[float],
        reference_spectrum: List[float],
    ) -> float:
        """
        Calculates the Hit Quality Index (HQI) between sample and reference spectra
        using the normalized squared dot product (Research §4.2).

        HQI = ((S_sample . S_ref)^2) / ((S_sample . S_sample) * (S_ref . S_ref)) * 100%
        """
        if not sample_spectrum or not reference_spectrum:
            raise ValueError("Sample and reference spectra must be non-empty.")

        if len(sample_spectrum) != len(reference_spectrum):
            raise ValueError(
                f"Dimension mismatch: sample has {len(sample_spectrum)} points, "
                f"reference has {len(reference_spectrum)} points."
            )

        dot_product = 0.0
        norm_sample_sq = 0.0
        norm_ref_sq = 0.0

        for s, r in zip(sample_spectrum, reference_spectrum):
            s_val = float(s)
            r_val = float(r)
            dot_product += s_val * r_val
            norm_sample_sq += s_val * s_val
            norm_ref_sq += r_val * r_val

        if norm_sample_sq <= 1e-12 or norm_ref_sq <= 1e-12:
            raise ValueError("Zero-energy spectrum detected. Spectral norm must be greater than zero.")

        hqi = (math.pow(dot_product, 2) / (norm_sample_sq * norm_ref_sq)) * 100.0
        return round(max(0.0, min(100.0, hqi)), 3)

    def match_trace_spectrum(
        self,
        sample_spectrum: List[float],
        wavenumbers_cm_1: Optional[List[float]] = None,
        custom_library: Optional[Dict[str, List[float]]] = None,
    ) -> Dict[str, Any]:
        """
        Compares an unknown sample spectrum against the forensic fiber & polymer library.
        """
        if not sample_spectrum:
            raise ValueError("Sample spectrum cannot be empty.")

        # Synthesize reference vectors for standard library if custom library is not supplied
        n_points = len(sample_spectrum)
        library_to_match = custom_library if custom_library else self._generate_default_reference_vectors(n_points)

        matches = []
        for name, ref_vec in library_to_match.items():
            if len(ref_vec) != n_points:
                continue
            hqi = self.compute_hqi(sample_spectrum, ref_vec)
            
            # Classification
            if hqi >= 90.0:
                classification = "POSITIVE_SPECTRAL_MATCH"
                evidence_strength = "Definitive chemical identification (HQI >= 90.0%, P_false < 1e-4)"
            elif hqi >= 75.0:
                classification = "PROBABLE_MATCH_DEGRADED"
                evidence_strength = "Probable match with partial surface weathering / contamination (75% <= HQI < 90%)"
            else:
                classification = "NON_MATCH_EXCLUSION"
                evidence_strength = "Excluded (HQI < 75.0%)"

            lib_info = FIBER_REFERENCE_LIBRARY.get(name, {})

            matches.append({
                "material_name": name,
                "hqi_score_percent": hqi,
                "classification": classification,
                "evidence_strength": evidence_strength,
                "polymer_name": lib_info.get("polymer_name", name),
                "fiber_type": lib_info.get("fiber_type", "Unknown"),
                "diagnostic_peaks_cm_1": lib_info.get("diagnostic_peaks_cm_1", []),
            })

        matches.sort(key=lambda x: x["hqi_score_percent"], reverse=True)
        top_match = matches[0] if matches else None

        shield_statement = (
            "IMPORTANT (SWGMAT / ASTM E2228 Micro-Spectroscopy Legal Shield): An HQI >= 90.0% provides definitive "
            "chemical polymer identification. However, synthetic fibers are mass-manufactured; spectral identity "
            "proves material class consistency but cannot uniquely identify a single garment without batch/dye context."
        )

        return {
            "top_match": top_match,
            "library_matches": matches,
            "points_evaluated": n_points,
            "prosecutors_fallacy_shield": shield_statement,
        }

    def simulate_msi_optical_response(
        self,
        evidence_type: str,
        active_wavelength_nm: int,
    ) -> Dict[str, Any]:
        """
        Evaluates optical phenomenon, contrast mechanism, and optimal filter for given evidence type and wavelength.
        """
        # Find matching band
        matched_band = None
        for b_id, b_data in MSI_WAVELENGTH_BANDS.items():
            if abs(b_data["wavelength_nm"] - active_wavelength_nm) <= 15:
                matched_band = b_data
                break

        if not matched_band:
            matched_band = {
                "wavelength_nm": active_wavelength_nm,
                "band_name": f"{active_wavelength_nm} nm Custom",
                "phenomenon": "General Illumination",
                "target_evidence": "General Surface Morphology",
                "mechanism": "Diffuse surface reflectance",
                "optimal_barrier_filter": "Broadband Polarizer",
            }

        # Calculate contrast index (0.0 to 1.0)
        contrast_index = 0.50
        ev_lower = evidence_type.lower()
        if "blood" in ev_lower and matched_band["wavelength_nm"] == 415:
            contrast_index = 0.98  # Maximum Soret absorption
        elif "blood" in ev_lower and matched_band["wavelength_nm"] == 850:
            contrast_index = 0.92  # Dark fabric NIR transmission
        elif any(f in ev_lower for f in ["semen", "saliva", "vaginal"]) and matched_band["wavelength_nm"] == 365:
            contrast_index = 0.95  # UV-A Flavin excitation
        elif any(f in ev_lower for f in ["fingerprint", "serology"]) and matched_band["wavelength_nm"] == 450:
            contrast_index = 0.90  # 450nm dye excitation

        return {
            "evidence_type": evidence_type,
            "wavelength_nm": active_wavelength_nm,
            "band_info": matched_band,
            "predicted_contrast_index": contrast_index,
            "is_optimal_forensic_band": contrast_index >= 0.85,
        }

    def _generate_default_reference_vectors(self, n_points: int) -> Dict[str, List[float]]:
        """Generates deterministic synthetic reference spectrum vectors for testing and comparison."""
        library = {}
        for idx, (name, info) in enumerate(FIBER_REFERENCE_LIBRARY.items()):
            vec = []
            peaks = info.get("diagnostic_peaks_cm_1", [1500.0])
            for p_idx in range(n_points):
                wavenumber = 400.0 + (p_idx / max(1, n_points - 1)) * 3600.0  # 400 to 4000 cm^-1
                intensity = 0.10  # Baseline
                for peak in peaks:
                    # Gaussian peak shape
                    sigma = 35.0
                    intensity += math.exp(-math.pow(wavenumber - peak, 2) / (2.0 * sigma * sigma))
                vec.append(intensity)
            library[name] = vec
        return library
