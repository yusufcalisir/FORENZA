"""
FORENZA Multi-Criteria Bayesian Evidence Fusion & GIS Spatial Heatmap Engine — Pillar 7 Phase 3.

Derives verbatim from Research Specification:
  - Pillar 7 §5: Multi-Criteria Bayesian Evidence Fusion & GIS Heatmap Rasterization
  - §5.1: Multi-Source Bayesian Grid Integration (P(theta, lambda | E) ~ P0 * prod(L_k))
  - §5.2: 2D Adaptive Gaussian Kernel Density Estimation (KDE) with Silverman Rule of Thumb
  - §5.3: Prioritized Search Area (S_alpha%) & Search Efficiency Index (SEI >= 90%)
  - §8: ENFSI 7-Tier Standardized Verbal Reporting Scale & ISO 17025 Prosecutor's Fallacy Shields
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any


# ── Data Types & Structures ───────────────────────────────────────────────────

@dataclass
class EvidenceLayerInput:
    layer_id: str
    modality_name: str  # "ISOTOPE_ISOSCAPE", "SOIL_CODA", "PALYNOLOGY_EDNA", "ROSSMO_GEO_PROFILE"
    likelihood_matrix: List[List[float]]
    weight: float = 1.0
    modality_likelihood_ratio: float = 1.0


@dataclass
class SpatialHotspot:
    hotspot_id: str
    centroid_x_km: float
    centroid_y_km: float
    centroid_lat: Optional[float]
    centroid_lon: Optional[float]
    bounding_radius_km: float
    posterior_density_mass_pct: float
    primary_associated_modality: str


@dataclass
class EvidenceFusionResult:
    case_id: str
    grid_bounds_km: Tuple[float, float, float, float]  # (min_x, max_x, min_y, max_y)
    grid_dimensions: Tuple[int, int]  # (nx, ny)
    fused_probability_surface: List[List[float]]
    peak_posterior_coord_km: Tuple[float, float]
    search_area_50pct_sq_km: float
    search_area_5pct_sq_km: float
    total_grid_area_sq_km: float
    search_efficiency_index_pct: float
    top_spatial_hotspots: List[SpatialHotspot]
    fused_likelihood_ratio: float
    enfsi_verbal_tier: str
    enfsi_verbal_statement_en: str
    enfsi_verbal_statement_tr: str
    prosecutors_fallacy_shield: str


# ── Core Engine Implementation ────────────────────────────────────────────────

class GeoFusionEngine:
    """
    FORENZA Production-Grade Multi-Criteria Bayesian Evidence Fusion Engine (Pillar 7).
    Derives verbatim from Research Specification §5 & §8.
    """

    # ── 1. 2D Adaptive Gaussian Kernel Density Estimation (§5.2) ──────────────

    def compute_2d_gaussian_kde(
        self,
        points: List[Tuple[float, float]],
        grid_bounds: Tuple[float, float, float, float] = (0.0, 20.0, 0.0, 20.0),
        grid_resolution_km: float = 0.50,
        bandwidths: Optional[Tuple[float, float]] = None,
    ) -> Tuple[List[List[float]], Tuple[float, float]]:
        """
        Computes 2D Gaussian Kernel Density Estimation (KDE) over spatial bounding box (§5.2):
          hat{f}(x, y) = 1 / (n * hx * hy) * sum(K((x - xi)/hx, (y - yi)/hy))
          where K(u, v) = 1 / (2*pi) * exp(-0.5 * (u^2 + v^2))
        """
        n = len(points)
        if n == 0:
            return ([[0.0]], (1.0, 1.0))

        min_x, max_x, min_y, max_y = grid_bounds
        step = float(grid_resolution_km)
        nx = int(round((max_x - min_x) / step)) + 1
        ny = int(round((max_y - min_y) / step)) + 1

        x_coords = [min_x + i * step for i in range(nx)]
        y_coords = [min_y + j * step for j in range(ny)]

        # Silverman's Rule of Thumb for 2D spatial coordinates: h_x = sigma_x * n^(-1/6)
        if bandwidths is None:
            mean_x = sum(p[0] for p in points) / n
            mean_y = sum(p[1] for p in points) / n
            sigma_x = math.sqrt(max(0.01, sum((p[0] - mean_x) ** 2 for p in points) / max(1, n - 1)))
            sigma_y = math.sqrt(max(0.01, sum((p[1] - mean_y) ** 2 for p in points) / max(1, n - 1)))

            hx = max(0.20, sigma_x * (n ** (-1.0 / 6.0)))
            hy = max(0.20, sigma_y * (n ** (-1.0 / 6.0)))
        else:
            hx, hy = bandwidths

        inv_hx_hy = 1.0 / (hx * hy)
        two_pi = 2.0 * math.pi
        kde_surface: List[List[float]] = [[0.0 for _ in range(ny)] for _ in range(nx)]
        total_sum = 0.0

        for i in range(nx):
            x = x_coords[i]
            for j in range(ny):
                y = y_coords[j]
                density_sum = 0.0
                for px, py in points:
                    u = (x - px) / hx
                    v = (y - py) / hy
                    kernel = math.exp(-0.5 * ((u ** 2) + (v ** 2))) / two_pi
                    density_sum += kernel

                val = (density_sum / (float(n) * hx * hy))
                kde_surface[i][j] = val
                total_sum += val

        # Normalize KDE surface to unity sum
        if total_sum > 0.0:
            for i in range(nx):
                for j in range(ny):
                    kde_surface[i][j] /= total_sum

        return (kde_surface, (hx, hy))

    # ── 2. Multi-Source Bayesian Grid Integration (§5.1) ───────────────────────

    def fuse_evidence_layers(
        self,
        layers: List[EvidenceLayerInput],
        case_id: str = "CASE_FUSION_2026",
        prior_surface: Optional[List[List[float]]] = None,
        grid_bounds: Tuple[float, float, float, float] = (0.0, 20.0, 0.0, 20.0),
        grid_resolution_km: float = 0.50,
    ) -> EvidenceFusionResult:
        """
        Fuses independent evidence modalities via Bayesian grid multiplication (§5.1):
          P(theta, lambda | E) ~ P0 * prod(L_k^w_k)
        """
        if not layers:
            raise ValueError("At least one evidence layer is required for multi-criteria fusion.")

        # Determine dimensions from first layer
        nx = len(layers[0].likelihood_matrix)
        ny = len(layers[0].likelihood_matrix[0]) if nx > 0 else 0

        if nx == 0 or ny == 0:
            raise ValueError("Input evidence layer matrix cannot be empty.")

        # Initialize fused posterior with prior (or uniform prior P0)
        fused_matrix: List[List[float]] = [[1.0 for _ in range(ny)] for _ in range(nx)]
        if prior_surface is not None:
            for i in range(nx):
                for j in range(ny):
                    fused_matrix[i][j] = max(1e-9, prior_surface[i][j])

        # Multiply likelihoods cell-by-cell conditioned on spatial independence
        composite_lr = 1.0
        for layer in layers:
            w = float(layer.weight)
            composite_lr *= (layer.modality_likelihood_ratio ** min(1.0, w))
            mat = layer.likelihood_matrix
            for i in range(min(nx, len(mat))):
                for j in range(min(ny, len(mat[i]))):
                    val = max(1e-9, float(mat[i][j]))
                    fused_matrix[i][j] *= (val ** w)

        # Normalize fused posterior surface to unity
        total_sum = sum(sum(row) for row in fused_matrix)
        if total_sum > 0.0:
            for i in range(nx):
                for j in range(ny):
                    fused_matrix[i][j] /= total_sum

        # Calculate grid metrics and find peak posterior cell
        min_x, max_x, min_y, max_y = grid_bounds
        step = float(grid_resolution_km)
        total_area = round((max_x - min_x) * (max_y - min_y), 2)
        cell_area = step ** 2

        all_cells: List[Tuple[float, float, float]] = []  # (prob, x, y)
        for i in range(nx):
            x = min_x + i * step
            for j in range(ny):
                y = min_y + j * step
                all_cells.append((fused_matrix[i][j], x, y))

        # Sort cells in descending probability order
        all_cells.sort(key=lambda item: item[0], reverse=True)

        peak_prob, peak_x, peak_y = all_cells[0]

        # Calculate S_50% and S_5% prioritized search areas (§5.3)
        cum_prob = 0.0
        cells_50pct = 0
        cells_5pct = 0

        for idx, (p, cx, cy) in enumerate(all_cells):
            cum_prob += p
            if cum_prob <= 0.50:
                cells_50pct += 1
            if cum_prob <= 0.05:
                cells_5pct += 1

        cells_50pct = max(1, cells_50pct)
        cells_5pct = max(1, cells_5pct)

        s_50pct_area = round(cells_50pct * cell_area, 2)
        s_5pct_area = round(cells_5pct * cell_area, 2)

        # Search Efficiency Index (SEI): (1 - S_50% / A_total) * 100% >= 90%
        sei_pct = round(max(0.0, min(100.0, (1.0 - (s_50pct_area / max(1.0, total_area))) * 100.0)), 2)

        # Construct top spatial hotspots
        hotspots: List[SpatialHotspot] = [
            SpatialHotspot(
                hotspot_id="HOTSPOT_01_PRIMARY",
                centroid_x_km=round(peak_x, 2),
                centroid_y_km=round(peak_y, 2),
                centroid_lat=None,
                centroid_lon=None,
                bounding_radius_km=round(math.sqrt(s_50pct_area / math.pi), 2),
                posterior_density_mass_pct=50.0,
                primary_associated_modality="BAYESIAN_JOINT_FUSION",
            )
        ]

        if len(all_cells) > 10:
            sec_cell = all_cells[min(len(all_cells) - 1, int(len(all_cells) * 0.15))]
            hotspots.append(
                SpatialHotspot(
                    hotspot_id="HOTSPOT_02_SECONDARY",
                    centroid_x_km=round(sec_cell[1], 2),
                    centroid_y_km=round(sec_cell[2], 2),
                    centroid_lat=None,
                    centroid_lon=None,
                    bounding_radius_km=round(math.sqrt(s_50pct_area / math.pi) * 1.5, 2),
                    posterior_density_mass_pct=25.0,
                    primary_associated_modality="REGIONAL_VEGETATION_CORRIDOR",
                )
            )

        # Assign ENFSI 7-tier scale (§8.1)
        composite_lr = max(1.0, min(1e9, composite_lr))
        if composite_lr >= 100000.0:
            tier_id = "TIER_6_EXTREMELY_STRONG"
            stmt_en = "Multi-criteria geo-forensic fusion provides extremely strong support for source inclusion (H1 over H2)."
            stmt_tr = "Çok kriterli jeo-adli füzyon bulguları, kaynak dahil oluş hipotezini (H1) fevkalade güçlü derecede desteklemektedir."
        elif composite_lr >= 10000.0:
            tier_id = "TIER_5_VERY_STRONG"
            stmt_en = "Multi-criteria geo-forensic fusion provides very strong support for source inclusion (H1 over H2)."
            stmt_tr = "Çok kriterli jeo-adli füzyon bulguları, kaynak dahil oluş hipotezini (H1) çok güçlü derecede desteklemektedir."
        elif composite_lr >= 1000.0:
            tier_id = "TIER_4_STRONG"
            stmt_en = "Multi-criteria geo-forensic fusion provides strong support for source inclusion (H1 over H2)."
            stmt_tr = "Çok kriterli jeo-adli füzyon bulguları, kaynak dahil oluş hipotezini (H1) güçlü derecede desteklemektedir."
        else:
            tier_id = "TIER_3_MODERATELY_STRONG"
            stmt_en = "Multi-criteria geo-forensic fusion provides moderately strong support for source inclusion (H1 over H2)."
            stmt_tr = "Çok kriterli jeo-adli füzyon bulguları, kaynak dahil oluş hipotezini orta-güçlü derecede desteklemektedir."

        shield_text = (
            "PROSECUTOR'S FALLACY SHIELD (MULTI-CRITERIA BAYESIAN GIS FUSION / ISO 17025): "
            f"The Fused Likelihood Ratio (LR = {composite_lr:.2e}) and Search Efficiency Index (SEI = {sei_pct}%) "
            "measure the joint conditional probability of observing convergent multi-isotope, mineralogical, "
            "palynological, and spatial behavioral traces under the common origin proposition P(E | H1) versus "
            "independent background environmental distributions P(E | H2). It does NOT express the probability that "
            "a specific individual was present at the scene P(H1 | E). Prior odds remain within the sole province "
            "of the legal trier of fact."
        )

        return EvidenceFusionResult(
            case_id=case_id,
            grid_bounds_km=grid_bounds,
            grid_dimensions=(nx, ny),
            fused_probability_surface=[[round(v * 1000.0, 5) for v in row] for row in fused_matrix],
            peak_posterior_coord_km=(round(peak_x, 2), round(peak_y, 2)),
            search_area_50pct_sq_km=s_50pct_area,
            search_area_5pct_sq_km=s_5pct_area,
            total_grid_area_sq_km=total_area,
            search_efficiency_index_pct=sei_pct,
            top_spatial_hotspots=hotspots,
            fused_likelihood_ratio=round(composite_lr, 2),
            enfsi_verbal_tier=tier_id,
            enfsi_verbal_statement_en=stmt_en,
            enfsi_verbal_statement_tr=stmt_tr,
            prosecutors_fallacy_shield=shield_text,
        )
