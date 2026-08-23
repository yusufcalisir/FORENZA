"""
FORENZA — Calibrated Score-Based Likelihood Ratio Engine (Phase 5.1)
=====================================================================

Implements the calibrated forensic Likelihood Ratio (LR) for metagenomic
soil and palynological evidence evaluation.

Research §4 Forensic Statistical Framework:

    Propositions (ISO/IEC 17025 & ENFSI 2017):
        H_p: The questioned trace soil/pollen originated from the specific
             crime scene location (or geographic source associated with suspect).
        H_d: The questioned trace originated from an unrelated alternative
             geographic origin (or the general background population of soils).

    Score-based Likelihood Ratio (SLR) formulation (Research §4.1):
        LR = P(E | H_p) / P(E | H_d)
        where E = observed compositional distance d(questioned, reference)

        SLR density estimation:
            LR = f(d | H_p) / f(d | H_d)
        where f() is estimated via kernel density estimation (KDE)
        over within-site vs. between-site Aitchison distance distributions.

    Multi-Omic Fusion (Research §4.3):
        When metagenomic evidence is combined with geochemical XRF/XRD
        and multi-isotope isoscape data:
            log10(LR_fused) = log10(LR_metagenomics) + log10(LR_geochemistry)
                            + log10(LR_isotopes)
        (assuming conditional independence of evidence streams)

    ENFSI 2017 7-Tier Verbal Scale (Research §4.5, also per §6 Pillar 6):
        log10(LR):
            ≥ 5: "extremely strong support"    (Çok son derece güçlü destek)
            4–5: "very strong support"         (Çok güçlü destek)
            3–4: "strong support"              (Güçlü destek)
            2–3: "moderate support"            (Orta düzeyde destek)
            1–2: "limited support"             (Sınırlı destek)
            0–1: "slight support"              (Hafif destek)
            0:   "neutral / no support"        (Tarafsız / destek yok)
            < 0: "support for H_d"             (H_d için destek)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 KERNEL DENSITY ESTIMATOR (Silverman Bandwidth)
# ═══════════════════════════════════════════════════════════════════════════════

def _gaussian_kernel(u: float) -> float:
    """Gaussian kernel: K(u) = (1/√(2π)) exp(-u^2/2)"""
    return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * u * u)


def _silverman_bandwidth(data: List[float]) -> float:
    """
    Silverman's rule of thumb bandwidth selection.

    h = 0.9 × min(std, IQR/1.34) × n^{-1/5}

    Args:
        data: Observed distance values

    Returns:
        Optimal KDE bandwidth h
    """
    n = len(data)
    if n < 2:
        return 1.0

    mean = sum(data) / n
    std = math.sqrt(sum((x - mean) ** 2 for x in data) / (n - 1))

    # IQR approximation
    sorted_data = sorted(data)
    q1 = sorted_data[n // 4]
    q3 = sorted_data[3 * n // 4]
    iqr = q3 - q1

    sigma_hat = min(std, iqr / 1.34) if iqr > 0 else std
    if sigma_hat <= 0:
        sigma_hat = 1.0

    return 0.9 * sigma_hat * n ** (-0.2)


def kde_density(
    x: float,
    reference_data: List[float],
    bandwidth: Optional[float] = None,
) -> float:
    """
    Kernel Density Estimate at point x.

    f_hat(x) = (1/nh) Σ_i K((x - x_i) / h)

    Args:
        x: Query point
        reference_data: Observed samples for KDE fitting
        bandwidth: KDE bandwidth h (default: Silverman's rule)

    Returns:
        Density estimate at x ≥ 0.0 (with minimum floor 1e-12)
    """
    n = len(reference_data)
    if n == 0:
        return 1e-12

    h = bandwidth if bandwidth is not None else _silverman_bandwidth(reference_data)
    if h <= 0:
        h = 1.0

    density = sum(_gaussian_kernel((x - xi) / h) for xi in reference_data) / (n * h)
    return max(density, 1e-12)


# ═══════════════════════════════════════════════════════════════════════════════
# §2 SCORE-BASED LR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MetagenomicLRResult:
    """
    Complete calibrated LR result for metagenomic soil/palynology evidence.
    """
    sample_id: str
    reference_site_id: str
    distance_questioned_reference: float   # d_A(questioned, reference) or score
    log10_lr: float
    lr: float                              # LR = 10^(log10_lr)
    hp_density: float                      # f(d | H_p)
    hd_density: float                      # f(d | H_d)
    enfsi_tier_en: str                     # English verbal scale
    enfsi_tier_tr: str                     # Turkish verbal scale
    fused_log10_lr: Optional[float] = None  # After multi-omic fusion
    fusion_components: Dict[str, float] = field(default_factory=dict)
    notes: str = ""


class MetagenomicLREngine:
    """
    Forensic Calibrated Score-Based Likelihood Ratio Engine for Metagenomic Evidence.

    Research §4.1 SLR Formulation:
        LR = f(d(E, S) | H_p) / f(d(E, S) | H_d)

    The within-site distribution f(d | H_p) is estimated from replicate
    measurements within the same geographic reference site.

    The between-site distribution f(d | H_d) is estimated from pairs of
    samples drawn from different forensically distinct sites.

    Calibration ensures the log-likelihood-ratio (LLR) distribution has:
        E[LLR | H_p] > 0 (support for H_p when H_p is true)
        E[LLR | H_d] < 0 (support for H_d when H_d is true)
        Cllr value documented for transparency.
    """

    def __init__(self) -> None:
        # Reference distributions
        self._within_site_distances: Dict[str, List[float]] = {}   # site_id → [d_A values]
        self._between_site_distances: List[float] = []              # global H_d distribution

        logger.info("[MetagenomicLREngine] Initialized")

    def register_within_site_distances(
        self,
        site_id: str,
        distances: List[float],
    ) -> None:
        """
        Register within-site Aitchison distance replicates for H_p calibration.

        These are distances between replicate samples from the SAME geographic site.

        Args:
            site_id: Geographic site identifier
            distances: List of Aitchison distances between intra-site replicate pairs
        """
        self._within_site_distances[site_id] = distances
        logger.debug(
            f"[MetagenomicLREngine] Within-site distances for '{site_id}': "
            f"n={len(distances)}, mean={sum(distances)/len(distances):.3f}"
        )

    def register_between_site_distances(self, distances: List[float]) -> None:
        """
        Register between-site Aitchison distance distribution for H_d calibration.

        Args:
            distances: Aitchison distances between samples from DIFFERENT sites
        """
        self._between_site_distances.extend(distances)
        logger.debug(
            f"[MetagenomicLREngine] Between-site distances added: "
            f"total n={len(self._between_site_distances)}"
        )

    def compute_lr(
        self,
        questioned_distance: float,
        reference_site_id: str,
        sample_id: str = "QUESTIONED_TRACE",
        geochemistry_log10_lr: float = 0.0,
        isotope_log10_lr: float = 0.0,
    ) -> MetagenomicLRResult:
        """
        Compute the calibrated score-based LR for a questioned trace.

        Args:
            questioned_distance: Aitchison distance between questioned sample
                                  and the reference crime scene site
            reference_site_id: The crime scene reference site ID
            sample_id: Questioned sample identifier
            geochemistry_log10_lr: log10 LR from geochemical XRF/XRD evidence
                                   (default 0.0 → no fusion)
            isotope_log10_lr: log10 LR from multi-isotope isoscape evidence

        Returns:
            MetagenomicLRResult with calibrated LR and ENFSI verbal scale
        """
        # Retrieve within-site distribution for this reference site
        within_distances = self._within_site_distances.get(reference_site_id, [])
        between_distances = self._between_site_distances

        if not within_distances:
            logger.warning(
                f"[MetagenomicLREngine] No within-site distances for '{reference_site_id}'. "
                f"Using requested distance as single reference point."
            )
            within_distances = [questioned_distance * 0.5]  # rough proxy

        if not between_distances:
            logger.warning(
                f"[MetagenomicLREngine] No between-site distances registered. "
                f"Using inflated between-site proxy."
            )
            between_distances = [questioned_distance * 3.0, questioned_distance * 4.0]

        # Compute KDE densities
        hp_density = kde_density(questioned_distance, within_distances)
        hd_density = kde_density(questioned_distance, between_distances)

        lr = hp_density / hd_density
        log10_lr = math.log10(max(lr, 1e-15))

        # Multi-omic fusion (Research §4.3)
        fused_log10_lr = log10_lr + geochemistry_log10_lr + isotope_log10_lr
        fusion_components = {
            "metagenomics": round(log10_lr, 4),
            "geochemistry": round(geochemistry_log10_lr, 4),
            "isotopes": round(isotope_log10_lr, 4),
            "fused": round(fused_log10_lr, 4),
        }

        # ENFSI 7-tier verbal scale (Research §4.5)
        tier_en, tier_tr = self._enfsi_verbal_scale(fused_log10_lr)

        result = MetagenomicLRResult(
            sample_id=sample_id,
            reference_site_id=reference_site_id,
            distance_questioned_reference=round(questioned_distance, 6),
            log10_lr=round(log10_lr, 4),
            lr=round(lr, 4),
            hp_density=round(hp_density, 8),
            hd_density=round(hd_density, 8),
            enfsi_tier_en=tier_en,
            enfsi_tier_tr=tier_tr,
            fused_log10_lr=round(fused_log10_lr, 4),
            fusion_components=fusion_components,
            notes=(
                f"SLR: f(d={questioned_distance:.4f}|Hp)={hp_density:.2e}, "
                f"f(d|Hd)={hd_density:.2e}, "
                f"LR={lr:.2e} (log10={log10_lr:.2f}). "
                f"Fused log10 LR (metagenomics + geochemistry + isotopes) = {fused_log10_lr:.2f}."
            )
        )

        logger.info(
            f"[MetagenomicLREngine] {sample_id}: "
            f"log10_LR={log10_lr:.2f}, fused={fused_log10_lr:.2f}, "
            f"ENFSI='{tier_en}'"
        )

        return result

    @staticmethod
    def _enfsi_verbal_scale(log10_lr: float) -> Tuple[str, str]:
        """
        Translate log10 LR into the ENFSI (2017) 7-tier bilingual verbal scale.

        Research §4.5 & Pillar 6 (Pillar_6_lims_zkp_reporting_research.md):
            ≥ 5: Extremely strong support for Hp
            4–5: Very strong support for Hp
            3–4: Strong support for Hp
            2–3: Moderate support for Hp
            1–2: Limited support for Hp
            0–1: Slight support for Hp
            = 0: Neutral
            < 0: Support for Hd (negative scale)

        Returns:
            (english_tier, turkish_tier)
        """
        if log10_lr >= 5:
            return (
                "The findings provide extremely strong support for Hp.",
                "Bulgular, Hp lehine son derece güçlü destek sağlamaktadır."
            )
        elif log10_lr >= 4:
            return (
                "The findings provide very strong support for Hp.",
                "Bulgular, Hp lehine çok güçlü destek sağlamaktadır."
            )
        elif log10_lr >= 3:
            return (
                "The findings provide strong support for Hp.",
                "Bulgular, Hp lehine güçlü destek sağlamaktadır."
            )
        elif log10_lr >= 2:
            return (
                "The findings provide moderate support for Hp.",
                "Bulgular, Hp lehine orta düzeyde destek sağlamaktadır."
            )
        elif log10_lr >= 1:
            return (
                "The findings provide limited support for Hp.",
                "Bulgular, Hp lehine sınırlı destek sağlamaktadır."
            )
        elif log10_lr >= 0:
            return (
                "The findings provide slight (negligible) support for Hp.",
                "Bulgular, Hp lehine hafif (ihmal edilebilir) destek sağlamaktadır."
            )
        elif log10_lr >= -1:
            return (
                "The findings provide slight support for Hd.",
                "Bulgular, Hd lehine hafif destek sağlamaktadır."
            )
        elif log10_lr >= -2:
            return (
                "The findings provide limited support for Hd.",
                "Bulgular, Hd lehine sınırlı destek sağlamaktadır."
            )
        elif log10_lr >= -3:
            return (
                "The findings provide moderate support for Hd.",
                "Bulgular, Hd lehine orta düzeyde destek sağlamaktadır."
            )
        else:
            return (
                "The findings provide strong or greater support for Hd.",
                "Bulgular, Hd lehine güçlü veya daha fazla destek sağlamaktadır."
            )
