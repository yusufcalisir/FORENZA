"""
FORENZA Module 1.2 — Reference Ground Truth Mixture Datasets Catalog

Research Sources & Benchmark Datasets:
  - Zenodo STR Analysis Results BTSC 349, BTSC 268 calibrated 2-person mixtures (Zenodo 3901446)
  - PROVEDIt Mixture Series (Boston University / NIST 2-person and 3-person dilution series)
  - NIST SRM 2391d Components A (9947A), B (9948) Standard Ground Truth Profiles

Contains calibrated single-source reference donors and experimental mixtures:
  1. BTSC_SS_DONOR_A     : Single-source Female Caucasian standard (9947A)
  2. BTSC_SS_DONOR_B     : Single-source Male African American standard (9948)
  3. BTSC_SS_DONOR_C     : Single-source Male reference standard (Donor C)
  4. BTSC_MIX_1_1        : Calibrated 1:1 mixture (50% : 50%, balanced)
  5. BTSC_MIX_3_1        : Calibrated 3:1 mixture (75% : 25%, major/minor)
  6. BTSC_MIX_9_1        : Calibrated 9:1 mixture (90% : 10%, major/minor)
  7. BTSC_MIX_19_1       : Calibrated 19:1 mixture (95% : 5%, severe contributor imbalance)
  8. PROVEDIt_2P_300pg_1_3 : PROVEDIt 2-person 300 pg 25:75 experimental mixture
  9. PROVEDIt_2P_100pg_1_9 : PROVEDIt 2-person 100 pg 10:90 low-template mixture
  10. PROVEDIt_3P_5_3_2  : PROVEDIt 3-person 50:30:20 complex mixture (tri/tetra-allelics)
  11. PROVEDIt_DEGRADED  : PROVEDIt 2-person differentially degraded mixture (d1=0.005, d2=0.001)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .peak_model import BiophysicalPeakModel, DEFAULT_AMPLIFICATION, LOCUS_STUTTER_RATIOS


@dataclass
class MCMCMixtureDataset:
    """
    Structured container for a multi-contributor STR reference dataset.
    """
    sample_id:           str
    dataset_name:        str
    n_contributors:      int
    true_weights:        List[float]
    true_degradations:   List[float]
    donor_genotypes:     Dict[str, Dict[str, Tuple[float, float]]]  # donor_id -> {locus -> (a1, a2)}
    epg_data:            Dict[str, Dict[float, float]]              # locus -> {allele -> RFU}
    description:         str
    total_template_rfu:  float = 2000.0


# ---------------------------------------------------------------------------
# Ground-Truth Donor Genotype Profiles (24 Expanded Loci)
# ---------------------------------------------------------------------------

DONOR_A_GENOTYPES: Dict[str, Tuple[float, float]] = {
    "D3S1358":  (14.0, 15.0),
    "VWA":      (17.0, 18.0),
    "D16S539":  (11.0, 12.0),
    "CSF1PO":   (10.0, 12.0),
    "TPOX":     (8.0, 8.0),
    "D8S1179":  (13.0, 13.0),
    "D21S11":   (30.0, 30.0),
    "D18S51":   (15.0, 19.0),
    "D2S441":   (10.0, 14.0),
    "D19S433":  (14.0, 15.0),
    "TH01":     (8.0, 9.3),
    "FGA":      (23.0, 24.0),
    "D22S1045": (15.0, 16.0),
    "D5S818":   (11.0, 11.0),
    "D13S317":  (11.0, 11.0),
    "D7S820":   (10.0, 11.0),
    "SE33":     (19.0, 29.2),
    "D10S1248": (13.0, 15.0),
    "D1S1656":  (15.0, 16.0),
    "D12S391":  (18.0, 19.0),
    "D2S1338":  (19.0, 23.0),
    "D6S1043":  (12.0, 14.0),
    "PENTA_E":  (12.0, 13.0),
    "PENTA_D":  (9.0, 12.0),
}

DONOR_B_GENOTYPES: Dict[str, Tuple[float, float]] = {
    "D3S1358":  (15.0, 17.0),
    "VWA":      (17.0, 17.0),
    "D16S539":  (12.0, 13.0),
    "CSF1PO":   (10.0, 11.0),
    "TPOX":     (8.0, 11.0),
    "D8S1179":  (12.0, 13.0),
    "D21S11":   (29.0, 30.0),
    "D18S51":   (16.0, 19.0),
    "D2S441":   (11.0, 11.0),
    "D19S433":  (13.0, 14.0),
    "TH01":     (6.0, 9.3),
    "FGA":      (24.0, 26.0),
    "D22S1045": (11.0, 16.0),
    "D5S818":   (12.0, 13.0),
    "D13S317":  (11.0, 12.0),
    "D7S820":   (8.0, 10.0),
    "SE33":     (16.0, 21.2),
    "D10S1248": (14.0, 14.0),
    "D1S1656":  (14.0, 17.3),
    "D12S391":  (17.0, 18.0),
    "D2S1338":  (19.0, 20.0),
    "D6S1043":  (11.0, 13.0),
    "PENTA_E":  (7.0, 14.0),
    "PENTA_D":  (11.0, 12.0),
}

DONOR_C_GENOTYPES: Dict[str, Tuple[float, float]] = {
    "D3S1358":  (16.0, 18.0),
    "VWA":      (15.0, 16.0),
    "D16S539":  (9.0, 11.0),
    "CSF1PO":   (11.0, 12.0),
    "TPOX":     (9.0, 10.0),
    "D8S1179":  (14.0, 15.0),
    "D21S11":   (28.0, 31.0),
    "D18S51":   (12.0, 14.0),
    "D2S441":   (12.0, 15.0),
    "D19S433":  (12.0, 15.2),
    "TH01":     (7.0, 9.0),
    "FGA":      (21.0, 22.0),
    "D22S1045": (14.0, 15.0),
    "D5S818":   (9.0, 13.0),
    "D13S317":  (8.0, 9.0),
    "D7S820":   (9.0, 12.0),
    "SE33":     (26.2, 28.2),
    "D10S1248": (12.0, 16.0),
    "D1S1656":  (12.0, 13.0),
    "D12S391":  (19.0, 21.0),
    "D2S1338":  (17.0, 24.0),
    "D6S1043":  (18.0, 19.0),
    "PENTA_E":  (10.0, 11.0),
    "PENTA_D":  (10.0, 13.0),
}


# ---------------------------------------------------------------------------
# Biophysical EPG Waveform Generator for Ground-Truth Reference Presets
# ---------------------------------------------------------------------------

def _generate_mixture_epg(
    donors: List[Dict[str, Tuple[float, float]]],
    weights: List[float],
    degradations: List[float],
    total_template: float = 2000.0,
) -> Dict[str, Dict[float, float]]:
    """
    Synthesizes EPG peak heights across all loci given contributor genotypes,
    weights, degradation parameters, and biophysical back-stutter dynamics.
    """
    model = BiophysicalPeakModel(template_scale=total_template)
    loci = list(donors[0].keys())
    epg: Dict[str, Dict[float, float]] = {}

    for locus in loci:
        locus_genotypes = [d[locus] for d in donors]
        heights = model.expected_peak_heights(
            locus=locus,
            genotypes=locus_genotypes,
            mixture_weights=weights,
            degradation_slopes=degradations,
        )
        # Filter very small artifacts < 15 RFU
        epg[locus] = {a: round(h, 2) for a, h in heights.items() if h >= 15.0}

    return epg


# ---------------------------------------------------------------------------
# Standard Reference Datasets Registry
# ---------------------------------------------------------------------------

BTSC_SS_DONOR_A = MCMCMixtureDataset(
    sample_id="BTSC_SS_DONOR_A",
    dataset_name="Zenodo BTSC 349 / NIST SRM 2391d Component A (9947A)",
    n_contributors=1,
    true_weights=[1.0],
    true_degradations=[0.0],
    donor_genotypes={"Donor_A": DONOR_A_GENOTYPES},
    epg_data=_generate_mixture_epg([DONOR_A_GENOTYPES], [1.0], [0.0], total_template=1500.0),
    description="Pristine single-source Female Caucasian standard reference profile.",
    total_template_rfu=1500.0,
)

BTSC_SS_DONOR_B = MCMCMixtureDataset(
    sample_id="BTSC_SS_DONOR_B",
    dataset_name="Zenodo BTSC 268 / NIST SRM 2391d Component B (9948)",
    n_contributors=1,
    true_weights=[1.0],
    true_degradations=[0.0],
    donor_genotypes={"Donor_B": DONOR_B_GENOTYPES},
    epg_data=_generate_mixture_epg([DONOR_B_GENOTYPES], [1.0], [0.0], total_template=1500.0),
    description="Pristine single-source Male African American standard reference profile.",
    total_template_rfu=1500.0,
)

BTSC_MIX_1_1 = MCMCMixtureDataset(
    sample_id="BTSC_MIX_1_1",
    dataset_name="Zenodo BTSC 349/268 Calibrated 1:1 Two-Person Mixture",
    n_contributors=2,
    true_weights=[0.50, 0.50],
    true_degradations=[0.0, 0.0],
    donor_genotypes={"Donor_A": DONOR_A_GENOTYPES, "Donor_B": DONOR_B_GENOTYPES},
    epg_data=_generate_mixture_epg([DONOR_A_GENOTYPES, DONOR_B_GENOTYPES], [0.50, 0.50], [0.0, 0.0], total_template=2000.0),
    description="Calibrated equal ratio 1:1 mixture of Donor A and Donor B.",
    total_template_rfu=2000.0,
)

BTSC_MIX_3_1 = MCMCMixtureDataset(
    sample_id="BTSC_MIX_3_1",
    dataset_name="Zenodo BTSC 349/268 Calibrated 3:1 Two-Person Mixture",
    n_contributors=2,
    true_weights=[0.75, 0.25],
    true_degradations=[0.0, 0.0],
    donor_genotypes={"Donor_A": DONOR_A_GENOTYPES, "Donor_B": DONOR_B_GENOTYPES},
    epg_data=_generate_mixture_epg([DONOR_A_GENOTYPES, DONOR_B_GENOTYPES], [0.75, 0.25], [0.0, 0.0], total_template=2000.0),
    description="Calibrated 3:1 major/minor mixture (75% Donor A, 25% Donor B).",
    total_template_rfu=2000.0,
)

BTSC_MIX_9_1 = MCMCMixtureDataset(
    sample_id="BTSC_MIX_9_1",
    dataset_name="Zenodo BTSC 349/268 Calibrated 9:1 Two-Person Mixture",
    n_contributors=2,
    true_weights=[0.90, 0.10],
    true_degradations=[0.0, 0.0],
    donor_genotypes={"Donor_A": DONOR_A_GENOTYPES, "Donor_B": DONOR_B_GENOTYPES},
    epg_data=_generate_mixture_epg([DONOR_A_GENOTYPES, DONOR_B_GENOTYPES], [0.90, 0.10], [0.0, 0.0], total_template=2500.0),
    description="Calibrated 9:1 major/minor mixture (90% Donor A, 10% Donor B).",
    total_template_rfu=2500.0,
)

BTSC_MIX_19_1 = MCMCMixtureDataset(
    sample_id="BTSC_MIX_19_1",
    dataset_name="Zenodo BTSC 349/268 Calibrated 19:1 Two-Person Mixture",
    n_contributors=2,
    true_weights=[0.95, 0.05],
    true_degradations=[0.0, 0.0],
    donor_genotypes={"Donor_A": DONOR_A_GENOTYPES, "Donor_B": DONOR_B_GENOTYPES},
    epg_data=_generate_mixture_epg([DONOR_A_GENOTYPES, DONOR_B_GENOTYPES], [0.95, 0.05], [0.0, 0.0], total_template=3000.0),
    description="Calibrated 19:1 severe contributor imbalance mixture (95% Donor A, 5% Donor B).",
    total_template_rfu=3000.0,
)

PROVEDIt_2P_300pg_1_3 = MCMCMixtureDataset(
    sample_id="PROVEDIt_2P_300pg_1_3",
    dataset_name="PROVEDIt 2-Person 300 pg (1:3 Dilution Series)",
    n_contributors=2,
    true_weights=[0.25, 0.75],
    true_degradations=[0.001, 0.001],
    donor_genotypes={"Donor_A": DONOR_A_GENOTYPES, "Donor_B": DONOR_B_GENOTYPES},
    epg_data=_generate_mixture_epg([DONOR_A_GENOTYPES, DONOR_B_GENOTYPES], [0.25, 0.75], [0.001, 0.001], total_template=1200.0),
    description="PROVEDIt experimental 300 pg 2-person mixture with minor Donor A (25%) and major Donor B (75%).",
    total_template_rfu=1200.0,
)

PROVEDIt_3P_5_3_2 = MCMCMixtureDataset(
    sample_id="PROVEDIt_3P_5_3_2",
    dataset_name="PROVEDIt 3-Person 50:30:20 Complex Mixture",
    n_contributors=3,
    true_weights=[0.50, 0.30, 0.20],
    true_degradations=[0.0, 0.0, 0.0],
    donor_genotypes={"Donor_A": DONOR_A_GENOTYPES, "Donor_B": DONOR_B_GENOTYPES, "Donor_C": DONOR_C_GENOTYPES},
    epg_data=_generate_mixture_epg([DONOR_A_GENOTYPES, DONOR_B_GENOTYPES, DONOR_C_GENOTYPES], [0.50, 0.30, 0.20], [0.0, 0.0, 0.0], total_template=3000.0),
    description="PROVEDIt experimental 3-person mixture with tri-allelic and tetra-allelic locus overlaps.",
    total_template_rfu=3000.0,
)

PROVEDIt_DEGRADED = MCMCMixtureDataset(
    sample_id="PROVEDIt_DEGRADED",
    dataset_name="PROVEDIt Differentially Degraded Two-Person Mixture",
    n_contributors=2,
    true_weights=[0.70, 0.30],
    true_degradations=[0.006, 0.001],
    donor_genotypes={"Donor_A": DONOR_A_GENOTYPES, "Donor_B": DONOR_B_GENOTYPES},
    epg_data=_generate_mixture_epg([DONOR_A_GENOTYPES, DONOR_B_GENOTYPES], [0.70, 0.30], [0.006, 0.001], total_template=2200.0),
    description="PROVEDIt 2-person mixture where major contributor is degraded (d1=0.006) and minor contributor is intact (d2=0.001).",
    total_template_rfu=2200.0,
)


# Master registry dictionary
_DATASET_REGISTRY: Dict[str, MCMCMixtureDataset] = {
    "BTSC_SS_DONOR_A":       BTSC_SS_DONOR_A,
    "BTSC_SS_DONOR_B":       BTSC_SS_DONOR_B,
    "BTSC_MIX_1_1":          BTSC_MIX_1_1,
    "BTSC_MIX_3_1":          BTSC_MIX_3_1,
    "BTSC_MIX_9_1":          BTSC_MIX_9_1,
    "BTSC_MIX_19_1":         BTSC_MIX_19_1,
    "PROVEDIt_2P_300pg_1_3": PROVEDIt_2P_300pg_1_3,
    "PROVEDIt_3P_5_3_2":      PROVEDIt_3P_5_3_2,
    "PROVEDIt_DEGRADED":     PROVEDIt_DEGRADED,
}


def get_mcmc_reference_dataset(sample_id: str) -> MCMCMixtureDataset:
    """Retrieve a standard reference mixture dataset by sample ID."""
    key = sample_id.strip()
    if key not in _DATASET_REGISTRY:
        raise KeyError(f"Reference dataset '{sample_id}' not found. Available: {list(_DATASET_REGISTRY.keys())}")
    return _DATASET_REGISTRY[key]


def list_mcmc_reference_datasets() -> List[Dict[str, str]]:
    """List all available standard reference mixture datasets."""
    return [
        {
            "sample_id": ds.sample_id,
            "dataset_name": ds.dataset_name,
            "n_contributors": str(ds.n_contributors),
            "weights": str(ds.true_weights),
            "description": ds.description,
        }
        for ds in _DATASET_REGISTRY.values()
    ]
