"""
FORENZA tDMR-Based Body Fluid & Tissue Provenance Identification Engine — Module 17.

Implements verbatim from Pillar 4 Research §2 & §6:
  - §2.1 Diagnostic Loci Reference Methylation Distribution Matrix (12 tDMR CpG loci across 6 core body fluid classes)
  - §2.2 Bayesian Quadratic Discriminant Analysis (QDA) / Gaussian Mixture Log-Likelihoods
  - Tissue Likelihood Ratios (LR_tissue) and Court-Admissible Evaluative Statements
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple, Union


# ── 12 Diagnostic tDMR Loci & 6 Body Fluid Reference Distributions (Research §2.1 & §6 Artifact A) ──

TDMR_REFERENCE_DISTRIBUTIONS: Dict[str, Dict[str, Dict[str, float]]] = {
    "blood": {
        "cg09652652": {"mean": 0.12, "std": 0.03, "gene": "Endothelial"},
        "cg19406367": {"mean": 0.15, "std": 0.04, "gene": "Hematopoietic"},
        "cg17610929": {"mean": 0.91, "std": 0.03, "gene": "Germ Cell"},
        "cg23521140": {"mean": 0.85, "std": 0.04, "gene": "DACT1"},
        "cg26763284": {"mean": 0.89, "std": 0.03, "gene": "PRMT12"},
        "cg23576855": {"mean": 0.84, "std": 0.04, "gene": "Oral Epithelial"},
        "cg00399818": {"mean": 0.82, "std": 0.05, "gene": "Salivary Gland"},
        "cg04382942": {"mean": 0.88, "std": 0.03, "gene": "Cervicovaginal"},
        "cg11624633": {"mean": 0.86, "std": 0.04, "gene": "MYO1G"},
        "cg00854446": {"mean": 0.82, "std": 0.05, "gene": "Endometrial"},
        "cg18063373": {"mean": 0.80, "std": 0.05, "gene": "Endometrial Stroma"},
        "cg07823520": {"mean": 0.90, "std": 0.03, "gene": "Epidermis"},
    },
    "semen": {
        "cg09652652": {"mean": 0.88, "std": 0.04, "gene": "Endothelial"},
        "cg19406367": {"mean": 0.92, "std": 0.03, "gene": "Hematopoietic"},
        "cg17610929": {"mean": 0.04, "std": 0.01, "gene": "Germ Cell"},
        "cg23521140": {"mean": 0.08, "std": 0.02, "gene": "DACT1"},
        "cg26763284": {"mean": 0.05, "std": 0.02, "gene": "PRMT12"},
        "cg23576855": {"mean": 0.89, "std": 0.03, "gene": "Oral Epithelial"},
        "cg00399818": {"mean": 0.86, "std": 0.04, "gene": "Salivary Gland"},
        "cg04382942": {"mean": 0.91, "std": 0.03, "gene": "Cervicovaginal"},
        "cg11624633": {"mean": 0.89, "std": 0.03, "gene": "MYO1G"},
        "cg00854446": {"mean": 0.94, "std": 0.02, "gene": "Endometrial"},
        "cg18063373": {"mean": 0.92, "std": 0.03, "gene": "Endometrial Stroma"},
        "cg07823520": {"mean": 0.95, "std": 0.02, "gene": "Epidermis"},
    },
    "saliva": {
        "cg09652652": {"mean": 0.85, "std": 0.05, "gene": "Endothelial"},
        "cg19406367": {"mean": 0.89, "std": 0.04, "gene": "Hematopoietic"},
        "cg17610929": {"mean": 0.88, "std": 0.04, "gene": "Germ Cell"},
        "cg23521140": {"mean": 0.82, "std": 0.05, "gene": "DACT1"},
        "cg26763284": {"mean": 0.86, "std": 0.04, "gene": "PRMT12"},
        "cg23576855": {"mean": 0.10, "std": 0.03, "gene": "Oral Epithelial"},
        "cg00399818": {"mean": 0.12, "std": 0.03, "gene": "Salivary Gland"},
        "cg04382942": {"mean": 0.72, "std": 0.06, "gene": "Cervicovaginal"},
        "cg11624633": {"mean": 0.70, "std": 0.05, "gene": "MYO1G"},
        "cg00854446": {"mean": 0.85, "std": 0.04, "gene": "Endometrial"},
        "cg18063373": {"mean": 0.83, "std": 0.05, "gene": "Endometrial Stroma"},
        "cg07823520": {"mean": 0.81, "std": 0.05, "gene": "Epidermis"},
    },
    "vaginal": {
        "cg09652652": {"mean": 0.82, "std": 0.06, "gene": "Endothelial"},
        "cg19406367": {"mean": 0.86, "std": 0.05, "gene": "Hematopoietic"},
        "cg17610929": {"mean": 0.90, "std": 0.03, "gene": "Germ Cell"},
        "cg23521140": {"mean": 0.84, "std": 0.04, "gene": "DACT1"},
        "cg26763284": {"mean": 0.88, "std": 0.04, "gene": "PRMT12"},
        "cg23576855": {"mean": 0.78, "std": 0.06, "gene": "Oral Epithelial"},
        "cg00399818": {"mean": 0.75, "std": 0.07, "gene": "Salivary Gland"},
        "cg04382942": {"mean": 0.15, "std": 0.04, "gene": "Cervicovaginal"},
        "cg11624633": {"mean": 0.18, "std": 0.05, "gene": "MYO1G"},
        "cg00854446": {"mean": 0.52, "std": 0.09, "gene": "Endometrial"},
        "cg18063373": {"mean": 0.55, "std": 0.08, "gene": "Endometrial Stroma"},
        "cg07823520": {"mean": 0.85, "std": 0.04, "gene": "Epidermis"},
    },
    "menstrual": {
        "cg09652652": {"mean": 0.22, "std": 0.05, "gene": "Endothelial"},
        "cg19406367": {"mean": 0.31, "std": 0.06, "gene": "Hematopoietic"},
        "cg17610929": {"mean": 0.89, "std": 0.04, "gene": "Germ Cell"},
        "cg23521140": {"mean": 0.83, "std": 0.05, "gene": "DACT1"},
        "cg26763284": {"mean": 0.87, "std": 0.04, "gene": "PRMT12"},
        "cg23576855": {"mean": 0.81, "std": 0.05, "gene": "Oral Epithelial"},
        "cg00399818": {"mean": 0.79, "std": 0.06, "gene": "Salivary Gland"},
        "cg04382942": {"mean": 0.35, "std": 0.08, "gene": "Cervicovaginal"},
        "cg11624633": {"mean": 0.38, "std": 0.07, "gene": "MYO1G"},
        "cg00854446": {"mean": 0.14, "std": 0.04, "gene": "Endometrial"},
        "cg18063373": {"mean": 0.16, "std": 0.04, "gene": "Endometrial Stroma"},
        "cg07823520": {"mean": 0.86, "std": 0.04, "gene": "Epidermis"},
    },
    "skin": {
        "cg09652652": {"mean": 0.91, "std": 0.03, "gene": "Endothelial"},
        "cg19406367": {"mean": 0.88, "std": 0.04, "gene": "Hematopoietic"},
        "cg17610929": {"mean": 0.94, "std": 0.02, "gene": "Germ Cell"},
        "cg23521140": {"mean": 0.89, "std": 0.03, "gene": "DACT1"},
        "cg26763284": {"mean": 0.92, "std": 0.03, "gene": "PRMT12"},
        "cg23576855": {"mean": 0.82, "std": 0.05, "gene": "Oral Epithelial"},
        "cg00399818": {"mean": 0.85, "std": 0.04, "gene": "Salivary Gland"},
        "cg04382942": {"mean": 0.86, "std": 0.04, "gene": "Cervicovaginal"},
        "cg11624633": {"mean": 0.84, "std": 0.04, "gene": "MYO1G"},
        "cg00854446": {"mean": 0.90, "std": 0.03, "gene": "Endometrial"},
        "cg18063373": {"mean": 0.88, "std": 0.04, "gene": "Endometrial Stroma"},
        "cg07823520": {"mean": 0.11, "std": 0.03, "gene": "Epidermis"},
    },
}

# Alias mapping for backwards compatibility with legacy mock keys
LEGACY_MOCK_TO_CGID = {
    "TDMR_BLOOD_01": "cg09652652",
    "TDMR_HEM_01": "cg19406367",
    "TDMR_SEMEN_01": "cg17610929",
    "TDMR_GERM_01": "cg23521140",
    "TDMR_SALIVA_01": "cg23576855",
    "TDMR_BUCCAL_01": "cg00399818",
    "TDMR_VAGINAL_01": "cg04382942",
    "TDMR_MENSTRUAL_01": "cg00854446",
    "TDMR_EPITHELIAL_01": "cg07823520",
    "TDMR_SKIN_01": "cg07823520",
    "TDMR_BONE_01": "cg09652652",
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class TissueProbabilityDetail:
    tissue_class: str
    probability: float
    log_likelihood: float
    z_scores: Dict[str, float]


@dataclass
class TissueDeconvolutionResult:
    top_predicted_tissue: str
    top_tissue_probability: float
    tissue_probabilities: Dict[str, float]
    log_likelihoods: Dict[str, float]
    lr_tissue: float
    log10_lr_tissue: float
    tdmr_loci_evaluated: int
    deconvolution_method: str
    prosecutors_fallacy_shield: str


# ── Engine ─────────────────────────────────────────────────────────────────────

class TissueDeconvolutionEngine:
    """
    FORENZA Forensic Tissue-of-Origin Epigenetic Deconvolution Engine.

    Derives verbatim from Pillar 4 Research §2.
    """

    TISSUE_DB = TDMR_REFERENCE_DISTRIBUTIONS
    LEGACY_MAP = LEGACY_MOCK_TO_CGID

    def __init__(self, custom_tdmr_db: Optional[Dict[str, Any]] = None):
        self.tdmr_db = custom_tdmr_db if custom_tdmr_db is not None else self.TISSUE_DB

    def deconvolve_sample(
        self,
        tdmr_methylation: Dict[str, Union[int, float]],
    ) -> Dict[str, Any]:
        """
        Deconvolves a tDMR methylation profile across 6 core forensic body fluids
        using Bayesian Quadratic Discriminant Analysis (QDA).
        """
        if not tdmr_methylation:
            raise ValueError("tdmr_methylation dictionary cannot be empty.")

        # Normalize and validate beta values in [0.0, 1.0]
        validated_betas: Dict[str, float] = {}
        for key, val in tdmr_methylation.items():
            key_clean = key.strip()
            # Map legacy mock keys to cgIDs if needed
            cgid = self.LEGACY_MAP.get(key_clean.upper(), key_clean)
            beta_val = float(val)
            if not (0.0 <= beta_val <= 1.0):
                raise ValueError(f"tDMR beta value for '{key}' must be within [0.0, 1.0], got {beta_val}.")
            validated_betas[cgid] = beta_val

        # Compute Bayesian QDA Gaussian Log-Likelihoods (Research §2.2)
        log_likelihoods: Dict[str, float] = {}

        for tissue_class, cpg_map in self.tdmr_db.items():
            ll = 0.0
            for cgid, stats in cpg_map.items():
                if cgid in validated_betas:
                    val = validated_betas[cgid]
                    mean = stats["mean"]
                    std = stats["std"]
                    variance = max(1e-6, std ** 2)
                    # Gaussian log-likelihood term: -0.5*ln(2*pi*var) - (val - mean)^2 / (2*var)
                    term = -0.5 * math.log(2.0 * math.pi * variance) - ((val - mean) ** 2) / (2.0 * variance)
                    ll += term
            log_likelihoods[tissue_class] = ll

        # Softmax Transformation to Posterior Probabilities
        max_ll = max(log_likelihoods.values())
        exp_ll = {t: math.exp(ll - max_ll) for t, ll in log_likelihoods.items()}
        sum_exp = sum(exp_ll.values())

        if sum_exp <= 0.0:
            sum_exp = 1.0

        posteriors: Dict[str, float] = {
            t: round(exp_ll[t] / sum_exp, 4) for t in log_likelihoods
        }

        # Rank Tissues
        sorted_tissues = sorted(
            posteriors.items(), key=lambda item: item[1], reverse=True
        )
        top_tissue, top_prob = sorted_tissues[0]
        second_tissue, second_prob = sorted_tissues[1]

        # Compute Tissue Likelihood Ratio: LR_tissue = P(top) / P(second)
        denom = max(second_prob, 0.0001)
        lr_tissue = round(top_prob / denom, 2)
        log10_lr = round(math.log10(max(1.0, lr_tissue)), 2)

        shield_statement = (
            "IMPORTANT (Body Fluid Tissue Provenance Legal Shield): Epigenetic tDMR classifications reflect cellular "
            "methylation signatures of biological fluid origins (Venous Blood, Semen, Saliva, Vaginal Fluid, "
            "Menstrual Blood, Skin). Predictions quantify tissue probabilities and likelihood ratios under Bayesian QDA. "
            "In forensic evidence evaluation, degraded stains, microbial contamination, or compound biological mixtures "
            "must be evaluated in conjunction with serological and morphological confirmation."
        )

        return {
            "top_predicted_tissue": top_tissue.upper(),
            "top_tissue_probability": top_prob,
            "tissue_probabilities": {k.upper(): v for k, v in posteriors.items()},
            "log_likelihoods": {k.upper(): round(v, 2) for k, v in log_likelihoods.items()},
            "lr_tissue": lr_tissue,
            "log10_lr_tissue": log10_lr,
            "tdmr_loci_evaluated": len(validated_betas),
            "deconvolution_method": "Bayesian Quadratic Discriminant Analysis (QDA 12-tDMR Gaussian Mixture)",
            "prosecutors_fallacy_shield": shield_statement,
        }
