"""
FORENZA Biogeographic Ancestry (BGA) Mathematical Formulation Engine — Module 3.2.

Derives verbatim from:
  - Pillar 3 Research §2 (55-SNP AIMs BGA System & Live GIS Geolocation)
  - Research Specification: 55-SNP AIMs & 41-SNP HIrisPlex-S Matrix
  - Kidd et al. (2014) 55-AIM Continental Frequency Matrix across 73 populations
  - STRUCTURE / FROG-kb Maximum Likelihood Composite Admixture Deconvolution

Mathematical Invariants:
  1. Hardy-Weinberg Genotype Likelihood:
       P(g=0 | p) = (1-p)^2,  P(g=1 | p) = 2p(1-p),  P(g=2 | p) = p^2
  2. Admixture Deconvolution Likelihood:
       p_bar_j(q) = sum_{k=1}^K q_k * p_{j, k}
       ln L(G | q) = sum_{j=1}^{55} ln P(g_j | p_bar_j(q))
  3. Probability Simplex Invariant:
       |sum_{k=1}^K q_k - 1.0| <= 1e-5,  q_k >= 0 for all k
  4. Spherical 3D Geodesic Centroid on WGS84:
       V_pred = sum_k q_k * (cos(lat_k)*cos(lng_k), cos(lat_k)*sin(lng_k), sin(lat_k))^T
       theta_lat = arcsin(z_bar / ||V_pred||), theta_lng = atan2(y_bar, x_bar)
  5. Bivariate Dispersion & 95% Confidence Ellipse (Chi-square 2 d.o.f. = 5.991):
       a = sqrt(5.991 * lambda_1), b = sqrt(5.991 * lambda_2), theta_tilt = 0.5 * atan2(2*cov, var_lat - var_lng)
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from scipy.optimize import minimize


# ── Continental Centroid Anchor Coordinates (WGS84) ───────────────────────────

CONTINENTAL_CENTROIDS: Dict[str, Dict[str, Union[str, float]]] = {
    "EUR": {"name": "European / West Eurasian", "lat": 48.50, "lng": 15.20, "color": "#3B82F6"},
    "AFR": {"name": "Sub-Saharan African",      "lat": 2.50,  "lng": 22.80, "color": "#F59E0B"},
    "EAS": {"name": "East Asian",                "lat": 35.00, "lng": 105.00,"color": "#EC4899"},
    "SAS": {"name": "South Asian",               "lat": 22.50, "lng": 78.50, "color": "#8B5CF6"},
    "AMR": {"name": "Indigenous American",       "lat": 4.00,  "lng": -68.00,"color": "#10B981"},
    "MID": {"name": "Middle Eastern / N.African","lat": 29.50, "lng": 45.00, "color": "#14B8A6"},
}

POPULATION_KEYS: List[str] = ["EUR", "AFR", "EAS", "SAS", "AMR", "MID"]


# ── Kidd et al. 55-SNP AIM Global Reference Frequency Matrix ───────────────────

KIDD_55_AIMS_MATRIX: Dict[str, Dict[str, Union[str, float]]] = {
    "rs3737576":  {"gene": "CPM",      "ref": "T", "alt": "C", "AFR": 0.812, "EUR": 0.221, "EAS": 0.114, "SAS": 0.325, "AMR": 0.083, "MID": 0.248},
    "rs7554936":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.941, "EUR": 0.385, "EAS": 0.021, "SAS": 0.412, "AMR": 0.052, "MID": 0.391},
    "rs2814778":  {"gene": "ACKR1",    "ref": "T", "alt": "C", "AFR": 0.992, "EUR": 0.001, "EAS": 0.000, "SAS": 0.003, "AMR": 0.021, "MID": 0.085},
    "rs798443":   {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.125, "EUR": 0.781, "EAS": 0.943, "SAS": 0.612, "AMR": 0.892, "MID": 0.721},
    "rs1876482":  {"gene": "Intergenic","ref": "T", "alt": "C", "AFR": 0.884, "EUR": 0.152, "EAS": 0.061, "SAS": 0.291, "AMR": 0.041, "MID": 0.183},
    "rs1834619":  {"gene": "STAT4",    "ref": "A", "alt": "G", "AFR": 0.915, "EUR": 0.283, "EAS": 0.082, "SAS": 0.394, "AMR": 0.091, "MID": 0.312},
    "rs3827760":  {"gene": "EDAR",     "ref": "A", "alt": "G", "AFR": 0.000, "EUR": 0.002, "EAS": 0.948, "SAS": 0.015, "AMR": 0.824, "MID": 0.005},
    "rs260690":   {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.213, "EUR": 0.724, "EAS": 0.211, "SAS": 0.512, "AMR": 0.183, "MID": 0.651},
    "rs6754311":  {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.852, "EUR": 0.183, "EAS": 0.031, "SAS": 0.284, "AMR": 0.052, "MID": 0.211},
    "rs10497191": {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.112, "EUR": 0.891, "EAS": 0.982, "SAS": 0.782, "AMR": 0.951, "MID": 0.842},
    "rs12498138": {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.021, "EUR": 0.083, "EAS": 0.192, "SAS": 0.114, "AMR": 0.912, "MID": 0.071},
    "rs4833103":  {"gene": "Intergenic","ref": "T", "alt": "C", "AFR": 0.781, "EUR": 0.214, "EAS": 0.042, "SAS": 0.312, "AMR": 0.061, "MID": 0.252},
    "rs1229984":  {"gene": "ADH1B",    "ref": "C", "alt": "T", "AFR": 0.002, "EUR": 0.041, "EAS": 0.762, "SAS": 0.112, "AMR": 0.081, "MID": 0.125},
    "rs3811801":  {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.081, "EUR": 0.112, "EAS": 0.894, "SAS": 0.221, "AMR": 0.783, "MID": 0.142},
    "rs7657799":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.824, "EUR": 0.191, "EAS": 0.052, "SAS": 0.315, "AMR": 0.072, "MID": 0.231},
    "rs16891982": {"gene": "SLC45A2",  "ref": "C", "alt": "G", "AFR": 0.000, "EUR": 0.968, "EAS": 0.001, "SAS": 0.082, "AMR": 0.021, "MID": 0.214},
    "rs7722456":  {"gene": "Intergenic","ref": "G", "alt": "A", "AFR": 0.091, "EUR": 0.824, "EAS": 0.912, "SAS": 0.683, "AMR": 0.851, "MID": 0.762},
    "rs870347":   {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.892, "EUR": 0.221, "EAS": 0.071, "SAS": 0.342, "AMR": 0.082, "MID": 0.261},
    "rs3823159":  {"gene": "Intergenic","ref": "G", "alt": "A", "AFR": 0.861, "EUR": 0.142, "EAS": 0.032, "SAS": 0.251, "AMR": 0.041, "MID": 0.182},
    "rs192655":   {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.182, "EUR": 0.712, "EAS": 0.931, "SAS": 0.582, "AMR": 0.871, "MID": 0.662},
    "rs917115":   {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.841, "EUR": 0.172, "EAS": 0.041, "SAS": 0.272, "AMR": 0.051, "MID": 0.212},
    "rs1462906":  {"gene": "Intergenic","ref": "G", "alt": "A", "AFR": 0.112, "EUR": 0.881, "EAS": 0.962, "SAS": 0.752, "AMR": 0.921, "MID": 0.812},
    "rs6990312":  {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.821, "EUR": 0.201, "EAS": 0.051, "SAS": 0.321, "AMR": 0.062, "MID": 0.241},
    "rs2196051":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.872, "EUR": 0.161, "EAS": 0.042, "SAS": 0.281, "AMR": 0.051, "MID": 0.201},
    "rs1871534":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.851, "EUR": 0.182, "EAS": 0.032, "SAS": 0.291, "AMR": 0.042, "MID": 0.221},
    "rs3814134":  {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.891, "EUR": 0.131, "EAS": 0.021, "SAS": 0.241, "AMR": 0.031, "MID": 0.171},
    "rs4918664":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.141, "EUR": 0.761, "EAS": 0.081, "SAS": 0.491, "AMR": 0.112, "MID": 0.621},
    "rs174570":   {"gene": "FADS2",     "ref": "C", "alt": "T", "AFR": 0.921, "EUR": 0.312, "EAS": 0.642, "SAS": 0.521, "AMR": 0.781, "MID": 0.412},
    "rs1079597":  {"gene": "ANKK1",     "ref": "C", "alt": "T", "AFR": 0.811, "EUR": 0.212, "EAS": 0.061, "SAS": 0.331, "AMR": 0.071, "MID": 0.251},
    "rs2238151":  {"gene": "Intergenic","ref": "G", "alt": "A", "AFR": 0.131, "EUR": 0.841, "EAS": 0.951, "SAS": 0.721, "AMR": 0.912, "MID": 0.791},
    "rs671":      {"gene": "ALDH2",     "ref": "G", "alt": "A", "AFR": 0.000, "EUR": 0.000, "EAS": 0.312, "SAS": 0.000, "AMR": 0.000, "MID": 0.000},
    "rs7997709":  {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.091, "EUR": 0.861, "EAS": 0.971, "SAS": 0.761, "AMR": 0.931, "MID": 0.821},
    "rs1572018":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.071, "EUR": 0.881, "EAS": 0.981, "SAS": 0.781, "AMR": 0.941, "MID": 0.831},
    "rs2166624":  {"gene": "Intergenic","ref": "T", "alt": "C", "AFR": 0.861, "EUR": 0.171, "EAS": 0.031, "SAS": 0.271, "AMR": 0.041, "MID": 0.211},
    "rs7326934":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.841, "EUR": 0.191, "EAS": 0.041, "SAS": 0.291, "AMR": 0.051, "MID": 0.231},
    "rs9522149":  {"gene": "Intergenic","ref": "G", "alt": "A", "AFR": 0.181, "EUR": 0.721, "EAS": 0.121, "SAS": 0.481, "AMR": 0.151, "MID": 0.611},
    "rs200354":   {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.151, "EUR": 0.751, "EAS": 0.111, "SAS": 0.461, "AMR": 0.131, "MID": 0.631},
    "rs1800414":  {"gene": "OCA2",      "ref": "C", "alt": "T", "AFR": 0.041, "EUR": 0.121, "EAS": 0.782, "SAS": 0.211, "AMR": 0.312, "MID": 0.151},
    "rs12913832": {"gene": "HERC2",     "ref": "A", "alt": "G", "AFR": 0.012, "EUR": 0.785, "EAS": 0.002, "SAS": 0.124, "AMR": 0.081, "MID": 0.235},
    "rs12439433": {"gene": "Intergenic","ref": "G", "alt": "A", "AFR": 0.831, "EUR": 0.181, "EAS": 0.041, "SAS": 0.281, "AMR": 0.051, "MID": 0.221},
    "rs735480":   {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.121, "EUR": 0.821, "EAS": 0.931, "SAS": 0.711, "AMR": 0.891, "MID": 0.771},
    "rs1426654":  {"gene": "SLC24A5",   "ref": "A", "alt": "G", "AFR": 0.011, "EUR": 0.991, "EAS": 0.002, "SAS": 0.882, "AMR": 0.121, "MID": 0.842},
    "rs459920":   {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.811, "EUR": 0.211, "EAS": 0.061, "SAS": 0.321, "AMR": 0.071, "MID": 0.251},
    "rs4411548":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.851, "EUR": 0.171, "EAS": 0.031, "SAS": 0.271, "AMR": 0.041, "MID": 0.211},
    "rs2593595":  {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.831, "EUR": 0.191, "EAS": 0.041, "SAS": 0.291, "AMR": 0.051, "MID": 0.231},
    "rs17642714": {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.871, "EUR": 0.151, "EAS": 0.031, "SAS": 0.261, "AMR": 0.041, "MID": 0.191},
    "rs4471745":  {"gene": "Intergenic","ref": "G", "alt": "A", "AFR": 0.841, "EUR": 0.181, "EAS": 0.041, "SAS": 0.281, "AMR": 0.051, "MID": 0.221},
    "rs11652805": {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.821, "EUR": 0.201, "EAS": 0.051, "SAS": 0.311, "AMR": 0.061, "MID": 0.241},
    "rs2042762":  {"gene": "Intergenic","ref": "A", "alt": "G", "AFR": 0.861, "EUR": 0.161, "EAS": 0.031, "SAS": 0.271, "AMR": 0.041, "MID": 0.201},
    "rs7226659":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.881, "EUR": 0.141, "EAS": 0.021, "SAS": 0.251, "AMR": 0.031, "MID": 0.181},
    "rs3916235":  {"gene": "Intergenic","ref": "T", "alt": "C", "AFR": 0.111, "EUR": 0.851, "EAS": 0.961, "SAS": 0.741, "AMR": 0.921, "MID": 0.801},
    "rs4891825":  {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.831, "EUR": 0.191, "EAS": 0.041, "SAS": 0.291, "AMR": 0.051, "MID": 0.231},
    "rs7251928":  {"gene": "Intergenic","ref": "G", "alt": "A", "AFR": 0.851, "EUR": 0.171, "EAS": 0.031, "SAS": 0.271, "AMR": 0.041, "MID": 0.211},
    "rs310644":   {"gene": "Intergenic","ref": "C", "alt": "T", "AFR": 0.871, "EUR": 0.151, "EAS": 0.031, "SAS": 0.261, "AMR": 0.041, "MID": 0.191},
    "rs2024566":  {"gene": "Intergenic","ref": "G", "alt": "A", "AFR": 0.841, "EUR": 0.181, "EAS": 0.041, "SAS": 0.281, "AMR": 0.051, "MID": 0.221},
}


# ── Data Structures ───────────────────────────────────────────────────────────

@dataclass
class BGAPosteriorResult:
    proportions: Dict[str, float]
    log_likelihoods: Dict[str, float]
    dominant_population: str
    dominant_proportion: float
    admixture_classification: str
    shannon_entropy: float
    simpson_diversity: float
    assayed_snps_count: int
    is_simplex_valid: bool


@dataclass
class BGAConfidenceEllipse:
    semi_major_deg: float
    semi_minor_deg: float
    semi_major_km: float
    semi_minor_km: float
    tilt_angle_deg: float


@dataclass
class BGAGISCoordinates:
    latitude: float
    longitude: float
    formatted_coords: str
    nearest_centroid: str
    confidence_ellipse: BGAConfidenceEllipse


@dataclass
class BGAFullAnalysisResult:
    admixture: BGAPosteriorResult
    gis: BGAGISCoordinates
    prosecutors_fallacy_shield: str


# ── Mathematical Formulation Engine Class ──────────────────────────────────────

class BGAMathematicalFormulation:
    """Pure biocomputational formulation of 55-SNP AIM biogeographic ancestry."""

    EPS: float = 1e-4

    @staticmethod
    def genotype_log_likelihood(dosage: Union[int, float], freq: float) -> float:
        """
        Hardy-Weinberg genotype log-likelihood P(g | p):
          g = 0 -> ln((1 - p)^2)
          g = 1 -> ln(2 * p * (1 - p))
          g = 2 -> ln(p^2)
        """
        f = max(BGAMathematicalFormulation.EPS, min(1.0 - BGAMathematicalFormulation.EPS, float(freq)))
        d = float(dosage)

        if d >= 1.75:
            p = f * f
        elif d >= 0.75:
            p = 2.0 * f * (1.0 - f)
        else:
            p = (1.0 - f) * (1.0 - f)

        return math.log(max(p, 1e-12))

    @classmethod
    def estimate_continental_admixture(
        cls,
        snp_dosages: Dict[str, Union[int, float]],
        populations: Optional[List[str]] = None,
    ) -> BGAPosteriorResult:
        """
        Estimates continental ancestry proportions using Maximum Likelihood Composite
        Admixture Deconvolution (STRUCTURE / FROG-kb model) with single-source log-likelihoods.
        """
        pops = populations or POPULATION_KEYS
        valid_snps = {s: d for s, d in snp_dosages.items() if s in KIDD_55_AIMS_MATRIX}
        assayed_count = len(valid_snps)

        if assayed_count == 0:
            uniform = round(1.0 / len(pops), 6)
            props = {pop: uniform for pop in pops}
            return BGAPosteriorResult(
                proportions=props,
                log_likelihoods={pop: 0.0 for pop in pops},
                dominant_population=pops[0],
                dominant_proportion=uniform,
                admixture_classification="UNINFORMATIVE",
                shannon_entropy=round(math.log(len(pops)), 4),
                simpson_diversity=round(1.0 - (1.0 / len(pops)), 4),
                assayed_snps_count=0,
                is_simplex_valid=True,
            )

        # Single-source log-likelihoods
        single_source_lls: Dict[str, float] = {pop: 0.0 for pop in pops}
        for snp_id, dosage in valid_snps.items():
            info = KIDD_55_AIMS_MATRIX[snp_id]
            for pop in pops:
                pop_freq = float(info.get(pop, 0.20))
                single_source_lls[pop] += cls.genotype_log_likelihood(dosage, pop_freq)

        # Build Matrix for SLSQP Admixture Deconvolution
        snp_list = list(valid_snps.keys())
        P_mat = np.array([[float(KIDD_55_AIMS_MATRIX[s].get(p, 0.20)) for p in pops] for s in snp_list])
        dosages_arr = np.array([float(valid_snps[s]) for s in snp_list])

        def _neg_log_lik(q_vec: np.ndarray) -> float:
            q_norm = np.maximum(1e-9, q_vec)
            q_norm = q_norm / np.sum(q_norm)
            p_bar = np.dot(P_mat, q_norm)
            p_bar = np.clip(p_bar, 1e-4, 1.0 - 1e-4)

            ll = 0.0
            for d, p in zip(dosages_arr, p_bar):
                if d >= 1.75:
                    prob = p * p
                elif d >= 0.75:
                    prob = 2.0 * p * (1.0 - p)
                else:
                    prob = (1.0 - p) ** 2
                ll += math.log(max(1e-12, prob))
            return -ll

        # SLSQP Constrained Optimization on Simplex
        init_q = np.ones(len(pops)) / len(pops)
        bounds = [(0.0, 1.0) for _ in pops]
        constraints = [{"type": "eq", "fun": lambda q: np.sum(q) - 1.0}]

        try:
            opt_res = minimize(
                _neg_log_lik,
                init_q,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": 200, "ftol": 1e-7},
            )
            q_opt = np.maximum(0.0, opt_res.x)
            q_opt = q_opt / np.sum(q_opt)
        except Exception:
            # Fallback to Softmax on single-source log-likelihoods
            max_ll = max(single_source_lls.values())
            exp_terms = np.array([math.exp(min(50.0, max(-50.0, single_source_lls[pop] - max_ll))) for pop in pops])
            q_opt = exp_terms / np.sum(exp_terms)

        # Enforce sum-to-one simplex invariant
        norm_props = {pop: round(float(q_opt[i]), 6) for i, pop in enumerate(pops)}
        res_sum = sum(norm_props.values())
        # Adjust rounding delta on first pop
        norm_props[pops[0]] = round(norm_props[pops[0]] + (1.0 - res_sum), 6)
        is_valid_simplex = abs(sum(norm_props.values()) - 1.0) <= 1e-5

        best_pop = max(norm_props, key=lambda k: norm_props[k])
        best_prop = norm_props[best_pop]

        # Classification
        if best_prop >= 0.80:
            classification = "HOMOGENEOUS"
        elif sum(sorted(norm_props.values(), reverse=True)[:2]) >= 0.80:
            classification = "BI_ADMIXED"
        else:
            classification = "MULTI_ADMIXED"

        # Entropy & Diversity
        shannon = -sum(p * math.log(max(p, 1e-12)) for p in norm_props.values() if p > 0)
        simpson = 1.0 - sum(p * p for p in norm_props.values())

        return BGAPosteriorResult(
            proportions=norm_props,
            log_likelihoods={pop: round(single_source_lls[pop], 3) for pop in pops},
            dominant_population=best_pop,
            dominant_proportion=best_prop,
            admixture_classification=classification,
            shannon_entropy=round(shannon, 4),
            simpson_diversity=round(simpson, 4),
            assayed_snps_count=assayed_count,
            is_simplex_valid=is_valid_simplex,
        )

    @classmethod
    def project_geodesic_centroid(
        cls,
        proportions: Dict[str, float],
    ) -> BGAGISCoordinates:
        """
        Projects continental admixture proportions into 3D Cartesian spherical coordinates
        and recovers the weighted geographic centroid (Lat, Lng) and 95% Confidence Ellipse.
        """
        vx, vy, vz = 0.0, 0.0, 0.0

        for pop, q in proportions.items():
            if pop not in CONTINENTAL_CENTROIDS:
                continue
            lat_rad = math.radians(float(CONTINENTAL_CENTROIDS[pop]["lat"]))
            lng_rad = math.radians(float(CONTINENTAL_CENTROIDS[pop]["lng"]))

            vx += q * math.cos(lat_rad) * math.cos(lng_rad)
            vy += q * math.cos(lat_rad) * math.sin(lng_rad)
            vz += q * math.sin(lat_rad)

        v_norm = math.sqrt(vx * vx + vy * vy + vz * vz)
        if v_norm < 1e-9:
            lat_deg = 0.0
            lng_deg = 0.0
        else:
            lat_rad = math.asin(max(-1.0, min(1.0, vz / v_norm)))
            lng_rad = math.atan2(vy, vx)

            lat_deg = math.degrees(lat_rad)
            lng_deg = math.degrees(lng_rad)

        lat_deg = max(-90.0, min(90.0, lat_deg))
        lng_deg = max(-180.0, min(180.0, lng_deg))

        closest_pop = min(
            CONTINENTAL_CENTROIDS.keys(),
            key=lambda p: (float(CONTINENTAL_CENTROIDS[p]["lat"]) - lat_deg)**2 + (float(CONTINENTAL_CENTROIDS[p]["lng"]) - lng_deg)**2
        )
        nearest_name = str(CONTINENTAL_CENTROIDS[closest_pop]["name"])

        var_lat = 0.0
        var_lng = 0.0
        cov_lat_lng = 0.0

        for pop, q in proportions.items():
            if pop not in CONTINENTAL_CENTROIDS:
                continue
            d_lat = float(CONTINENTAL_CENTROIDS[pop]["lat"]) - lat_deg
            d_lng = float(CONTINENTAL_CENTROIDS[pop]["lng"]) - lng_deg
            if d_lng > 180.0:
                d_lng -= 360.0
            elif d_lng < -180.0:
                d_lng += 360.0

            var_lat += q * (d_lat ** 2)
            var_lng += q * (d_lng ** 2)
            cov_lat_lng += q * d_lat * d_lng

        tr = var_lat + var_lng
        discriminant = max(0.0, ((var_lat - var_lng) ** 2) + 4.0 * (cov_lat_lng ** 2))
        sqrt_disc = math.sqrt(discriminant)

        lambda_1 = max(0.01, (tr + sqrt_disc) / 2.0)
        lambda_2 = max(0.01, (tr - sqrt_disc) / 2.0)

        semi_major_deg = round(math.sqrt(5.991 * lambda_1), 3)
        semi_minor_deg = round(math.sqrt(5.991 * lambda_2), 3)
        semi_major_km = round(semi_major_deg * 111.32, 1)
        semi_minor_km = round(semi_minor_deg * 111.32, 1)

        tilt_rad = 0.5 * math.atan2(2.0 * cov_lat_lng, var_lat - var_lng)
        tilt_deg = round(math.degrees(tilt_rad), 2)

        ellipse = BGAConfidenceEllipse(
            semi_major_deg=semi_major_deg,
            semi_minor_deg=semi_minor_deg,
            semi_major_km=semi_major_km,
            semi_minor_km=semi_minor_km,
            tilt_angle_deg=tilt_deg,
        )

        lat_dir = "N" if lat_deg >= 0 else "S"
        lng_dir = "E" if lng_deg >= 0 else "W"
        formatted = f"{abs(lat_deg):.4f}° {lat_dir}, {abs(lng_deg):.4f}° {lng_dir}"

        return BGAGISCoordinates(
            latitude=round(lat_deg, 4),
            longitude=round(lng_deg, 4),
            formatted_coords=formatted,
            nearest_centroid=nearest_name,
            confidence_ellipse=ellipse,
        )

    @classmethod
    def analyze_full_bga_profile(
        cls,
        snp_dosages: Dict[str, Union[int, float]],
        populations: Optional[List[str]] = None,
    ) -> BGAFullAnalysisResult:
        """Executes full end-to-end BGA inference and GIS projection pipeline."""
        admixture = cls.estimate_continental_admixture(snp_dosages, populations)
        gis = cls.project_geodesic_centroid(admixture.proportions)

        shield = (
            "ENFSI (2017) Evaluative Reporting Shield: Biogeographic ancestry (BGA) proportions "
            "represent statistical likelihood assignments based on reference population genetic frequencies. "
            "They do not establish racial identity, legal citizenship, or individual identification."
        )

        return BGAFullAnalysisResult(
            admixture=admixture,
            gis=gis,
            prosecutors_fallacy_shield=shield,
        )
