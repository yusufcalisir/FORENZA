"""
FORENZA Biogeographic Ancestry (BGA) & Live GIS Geolocation Engine — Module 12.

Implements verbatim from Pillar 3 Research §2:
  - §2.1 55-SNP Reference Allele Frequency Matrix (EUR, AFR, EAS, SAS, AMR)
  - §2.2 Bayesian Posterior Admixture Estimation under Dirichlet Prior (Sum-to-Unity Invariant)
  - §2.3 3D Spherical Geographic Coordinate Projection & 95% Confidence Ellipse Geometry
  - Shannon Entropy & Simpson Diversity Index for Admixture Complexity Classification
  - ENFSI (2017) Evaluative Legal Shield for BGA Evidence
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union


# ── Continental Population Centroids (Pillar 3 Research §2.3) ─────────────────

CONTINENTAL_CENTROIDS = {
    "EUR": {"name": "European", "lat": 48.50, "lng": 15.20, "color": "#3B82F6"},
    "AFR": {"name": "African", "lat": 2.50, "lng": 22.80, "color": "#F59E0B"},
    "EAS": {"name": "East Asian", "lat": 35.00, "lng": 105.00, "color": "#EC4899"},
    "SAS": {"name": "South Asian", "lat": 22.50, "lng": 78.50, "color": "#8B5CF6"},
    "AMR": {"name": "Admixed/Indigenous American", "lat": 4.00, "lng": -68.00, "color": "#10B981"},
}

POPULATIONS = ["EUR", "AFR", "EAS", "SAS", "AMR"]


# ── 55-AIM Panel Reference Allele Frequency Matrix (Kidd / Seldin Panels) ─────

AIM_55_REFERENCE_PANEL: Dict[str, Dict[str, Any]] = {
    # Key Diagnostic AIMs from Research §2.1
    "rs2814778":  {"gene": "DARC (Duffy Null)", "allele": "C", "EUR": 0.001, "AFR": 0.992, "EAS": 0.000, "SAS": 0.002, "AMR": 0.015},
    "rs1426654":  {"gene": "SLC24A5",           "allele": "A", "EUR": 0.998, "AFR": 0.021, "EAS": 0.000, "SAS": 0.885, "AMR": 0.115},
    "rs3827072":  {"gene": "EDAR (370Ala)",     "allele": "C", "EUR": 0.000, "AFR": 0.000, "EAS": 0.945, "SAS": 0.012, "AMR": 0.821},
    "rs1800414":  {"gene": "OCA2 (His615Arg)",   "allele": "C", "EUR": 0.000, "AFR": 0.000, "EAS": 0.725, "SAS": 0.005, "AMR": 0.041},
    "rs16891982": {"gene": "SLC45A2 (Phe374Leu)","allele": "G", "EUR": 0.984, "AFR": 0.008, "EAS": 0.000, "SAS": 0.124, "AMR": 0.032},
    "rs1042602":  {"gene": "TYR",                "allele": "A", "EUR": 0.452, "AFR": 0.051, "EAS": 0.012, "SAS": 0.312, "AMR": 0.084},
    "rs1800407":  {"gene": "OCA2",               "allele": "T", "EUR": 0.085, "AFR": 0.002, "EAS": 0.000, "SAS": 0.021, "AMR": 0.010},
    "rs26722":    {"gene": "SLC24A4",            "allele": "A", "EUR": 0.215, "AFR": 0.012, "EAS": 0.005, "SAS": 0.145, "AMR": 0.031},
    "rs12203592": {"gene": "IRF4",               "allele": "T", "EUR": 0.182, "AFR": 0.005, "EAS": 0.000, "SAS": 0.042, "AMR": 0.012},
    "rs3340":     {"gene": "F13A1",              "allele": "T", "EUR": 0.850, "AFR": 0.180, "EAS": 0.720, "SAS": 0.650, "AMR": 0.450},
    "rs6119471":  {"gene": "COL11A1",            "allele": "A", "EUR": 0.050, "AFR": 0.780, "EAS": 0.030, "SAS": 0.040, "AMR": 0.220},
    "rs2065160":  {"gene": "OCA2",               "allele": "G", "EUR": 0.420, "AFR": 0.080, "EAS": 0.850, "SAS": 0.550, "AMR": 0.650},
    "rs3957351":  {"gene": "ASIP",               "allele": "G", "EUR": 0.250, "AFR": 0.720, "EAS": 0.180, "SAS": 0.300, "AMR": 0.400},
    "rs4988235":  {"gene": "LCT (Lactase)",      "allele": "T", "EUR": 0.720, "AFR": 0.040, "EAS": 0.010, "SAS": 0.220, "AMR": 0.150},
    "rs1834619":  {"gene": "SLC24A5",            "allele": "G", "EUR": 0.080, "AFR": 0.820, "EAS": 0.120, "SAS": 0.150, "AMR": 0.350},
    "rs10007810": {"gene": "MYO5A",              "allele": "A", "EUR": 0.720, "AFR": 0.220, "EAS": 0.480, "SAS": 0.550, "AMR": 0.600},
    "rs1799971":  {"gene": "OPRM1",              "allele": "G", "EUR": 0.150, "AFR": 0.020, "EAS": 0.650, "SAS": 0.400, "AMR": 0.380},
    "rs174537":   {"gene": "FADS1",              "allele": "T", "EUR": 0.600, "AFR": 0.150, "EAS": 0.420, "SAS": 0.500, "AMR": 0.520},
    "rs2065200":  {"gene": "HERC2",              "allele": "C", "EUR": 0.180, "AFR": 0.680, "EAS": 0.220, "SAS": 0.250, "AMR": 0.450},
    "rs4778138":  {"gene": "OCA2",               "allele": "G", "EUR": 0.450, "AFR": 0.880, "EAS": 0.320, "SAS": 0.550, "AMR": 0.620},
    "rs2470102":  {"gene": "CYP1A2",             "allele": "A", "EUR": 0.350, "AFR": 0.820, "EAS": 0.280, "SAS": 0.420, "AMR": 0.550},
    "rs7561684":  {"gene": "KITLG",              "allele": "G", "EUR": 0.780, "AFR": 0.120, "EAS": 0.550, "SAS": 0.620, "AMR": 0.600},
    "rs10491":    {"gene": "TYRP1",              "allele": "T", "EUR": 0.220, "AFR": 0.650, "EAS": 0.400, "SAS": 0.350, "AMR": 0.480},
    "rs12913832": {"gene": "HERC2",              "allele": "C", "EUR": 0.720, "AFR": 0.010, "EAS": 0.005, "SAS": 0.100, "AMR": 0.080},
    "rs10424031": {"gene": "MFSD12",             "allele": "A", "EUR": 0.020, "AFR": 0.850, "EAS": 0.010, "SAS": 0.050, "AMR": 0.150},
    "rs1805007":  {"gene": "MC1R (R151C)",       "allele": "T", "EUR": 0.120, "AFR": 0.001, "EAS": 0.000, "SAS": 0.010, "AMR": 0.020},
    "rs885479":   {"gene": "MC1R (R163Q)",       "allele": "G", "EUR": 0.080, "AFR": 0.050, "EAS": 0.680, "SAS": 0.120, "AMR": 0.250},
    "rs12821256": {"gene": "KITLG",              "allele": "C", "EUR": 0.180, "AFR": 0.005, "EAS": 0.002, "SAS": 0.025, "AMR": 0.040},
    "rs1015362":  {"gene": "ASIP",               "allele": "G", "EUR": 0.750, "AFR": 0.150, "EAS": 0.620, "SAS": 0.480, "AMR": 0.550},
    "rs10756819": {"gene": "BNC2",               "allele": "A", "EUR": 0.680, "AFR": 0.120, "EAS": 0.450, "SAS": 0.520, "AMR": 0.480},
    "rs75570604": {"gene": "MC1R (R142H)",       "allele": "A", "EUR": 0.020, "AFR": 0.000, "EAS": 0.000, "SAS": 0.005, "AMR": 0.010},
    "rs1805008":  {"gene": "MC1R (R160W)",       "allele": "T", "EUR": 0.100, "AFR": 0.001, "EAS": 0.000, "SAS": 0.008, "AMR": 0.015},
    "rs1805009":  {"gene": "MC1R (D294H)",       "allele": "C", "EUR": 0.040, "AFR": 0.000, "EAS": 0.000, "SAS": 0.002, "AMR": 0.010},
    "rs35264875": {"gene": "TYRP1",              "allele": "T", "EUR": 0.350, "AFR": 0.050, "EAS": 0.020, "SAS": 0.150, "AMR": 0.080},
    "rs1393350":  {"gene": "TYR",                "allele": "A", "EUR": 0.420, "AFR": 0.080, "EAS": 0.050, "SAS": 0.280, "AMR": 0.120},
    "rs12896399": {"gene": "SLC24A4",            "allele": "T", "EUR": 0.480, "AFR": 0.060, "EAS": 0.150, "SAS": 0.320, "AMR": 0.220},
    "rs11803731": {"gene": "TCHH",               "allele": "T", "EUR": 0.450, "AFR": 0.080, "EAS": 0.020, "SAS": 0.250, "AMR": 0.150},
    "rs7349332":  {"gene": "WNT10A",             "allele": "A", "EUR": 0.320, "AFR": 0.040, "EAS": 0.010, "SAS": 0.180, "AMR": 0.110},
    "rs6152":     {"gene": "AR (Balding)",       "allele": "G", "EUR": 0.650, "AFR": 0.350, "EAS": 0.420, "SAS": 0.550, "AMR": 0.520},
    "rs2180439":  {"gene": "20p11 (Balding)",    "allele": "T", "EUR": 0.420, "AFR": 0.180, "EAS": 0.250, "SAS": 0.380, "AMR": 0.320},
    "rs1160312":  {"gene": "20p11 (Balding)",    "allele": "A", "EUR": 0.380, "AFR": 0.150, "EAS": 0.220, "SAS": 0.350, "AMR": 0.280},
    "rs756853":   {"gene": "HDAC9 (Balding)",    "allele": "G", "EUR": 0.520, "AFR": 0.280, "EAS": 0.350, "SAS": 0.450, "AMR": 0.420},
    "rs974448":   {"gene": "PAX3 (Craniofacial)","allele": "T", "EUR": 0.580, "AFR": 0.220, "EAS": 0.450, "SAS": 0.520, "AMR": 0.480},
    "rs12882923": {"gene": "PAX9 (Midface)",     "allele": "C", "EUR": 0.620, "AFR": 0.310, "EAS": 0.480, "SAS": 0.550, "AMR": 0.520},
    "rs11130635": {"gene": "PRDM16 (Nasal)",     "allele": "A", "EUR": 0.450, "AFR": 0.180, "EAS": 0.350, "SAS": 0.420, "AMR": 0.380},
    "rs13289":    {"gene": "DCHS2 (Nasal Tip)",  "allele": "G", "EUR": 0.380, "AFR": 0.650, "EAS": 0.280, "SAS": 0.420, "AMR": 0.450},
    "rs7559252":  {"gene": "PCDH15 (Chin)",      "allele": "C", "EUR": 0.520, "AFR": 0.250, "EAS": 0.420, "SAS": 0.480, "AMR": 0.450},
    "rs28777":    {"gene": "SLC45A2",            "allele": "A", "EUR": 0.950, "AFR": 0.020, "EAS": 0.005, "SAS": 0.180, "AMR": 0.080},
    "rs1667394":  {"gene": "OCA2",               "allele": "T", "EUR": 0.480, "AFR": 0.080, "EAS": 0.050, "SAS": 0.280, "AMR": 0.180},
    "rs7183877":  {"gene": "SLC24A4",            "allele": "C", "EUR": 0.550, "AFR": 0.120, "EAS": 0.220, "SAS": 0.380, "AMR": 0.300},
    "rs2228479":  {"gene": "MC1R (V92M)",        "allele": "A", "EUR": 0.120, "AFR": 0.010, "EAS": 0.250, "SAS": 0.080, "AMR": 0.100},
    "rs1805005":  {"gene": "MC1R (V60L)",        "allele": "T", "EUR": 0.150, "AFR": 0.005, "EAS": 0.000, "SAS": 0.020, "AMR": 0.040},
    "rs11547464": {"gene": "MC1R (R151C syn)",   "allele": "A", "EUR": 0.050, "AFR": 0.000, "EAS": 0.000, "SAS": 0.005, "AMR": 0.010},
    "rs3212355":  {"gene": "SLC24A5",            "allele": "C", "EUR": 0.080, "AFR": 0.850, "EAS": 0.100, "SAS": 0.150, "AMR": 0.380},
    "rs683":      {"gene": "TYRP1",              "allele": "C", "EUR": 0.650, "AFR": 0.180, "EAS": 0.420, "SAS": 0.520, "AMR": 0.480},
}


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class ConfidenceEllipse:
    semi_major_deg: float      # a = sqrt(5.991 * lambda_1)
    semi_minor_deg: float      # b = sqrt(5.991 * lambda_2)
    semi_major_km: float       # a * 111.32 km/deg
    semi_minor_km: float       # b * 111.32 km/deg
    tilt_angle_deg: float      # theta_tilt orientation in degrees


@dataclass
class GISCoordinates:
    latitude: float            # In decimal degrees [-90, +90]
    longitude: float           # In decimal degrees [-180, +180]
    formatted_coords: str      # e.g. "48.5000° N, 15.2000° E"
    nearest_centroid: str      # Name of closest continental cluster
    confidence_ellipse: ConfidenceEllipse


@dataclass
class AIMAdmixtureResult:
    proportions: Dict[str, float]       # Continental proportions {EUR, AFR, EAS, SAS, AMR}, sum = 1.0
    dominant_population: str            # Continent with highest proportion
    dominant_proportion: float          # Max proportion
    admixture_classification: str       # "HOMOGENEOUS", "BI_ADMIXED", or "MULTI_ADMIXED"
    shannon_entropy: float              # H(q) = -sum q_j * ln(q_j)
    simpson_diversity: float            # D = 1 - sum q_j^2
    assayed_snps_count: int             # Number of informative SNPs utilized
    gis_projection: GISCoordinates      # Projected 3D spherical centroid & uncertainty ellipse
    prosecutors_fallacy_shield: str     # ENFSI Evaluative Reporting Legal Warning


# ── Engine ─────────────────────────────────────────────────────────────────────

class AIMBGAEngine:
    """
    FORENZA 55-SNP AIM Biogeographic Ancestry & Live GIS Geolocation Engine.
    
    Derives verbatim from Pillar 3 Research §2.
    """

    def __init__(self, eps: float = 1e-4):
        self.eps = eps
        self.centroids = CONTINENTAL_CENTROIDS
        self.ref_panel = AIM_55_REFERENCE_PANEL

    # ── §2.2 Bayesian Posterior Admixture Estimator ───────────────────────────

    def _genotype_log_likelihood(self, dosage: Union[int, float], freq: float) -> float:
        """
        Hardy-Weinberg genotype log-likelihood P(dosage | freq):
          dosage 0 -> (1 - f)^2
          dosage 1 -> 2 * f * (1 - f)
          dosage 2 -> f^2
        """
        f = max(self.eps, min(1.0 - self.eps, float(freq)))
        d = float(dosage)

        if d >= 1.75:
            # Homozygous Alt (2)
            prob = f * f
        elif d >= 0.75:
            # Heterozygous (1)
            prob = 2.0 * f * (1.0 - f)
        else:
            # Homozygous Ref (0)
            prob = (1.0 - f) * (1.0 - f)

        return math.log(max(prob, 1e-12))

    def estimate_admixture(
        self,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> Tuple[Dict[str, float], int]:
        """
        Calculates normalized Bayesian posterior admixture proportions across
        5 continental populations under uniform Dirichlet prior (alpha_j = 1.0).

        ln L(G | C_j) = sum_m ln P(g_m | p_m,j)
        q_j = exp(ln L_j - max ln L) / sum exp(ln L_l - max ln L)
        """
        log_likelihoods = {pop: 0.0 for pop in POPULATIONS}
        assayed_count = 0

        for snp_id, dosage in snp_dosages.items():
            if snp_id not in self.ref_panel:
                continue

            info = self.ref_panel[snp_id]
            for pop in POPULATIONS:
                pop_freq = info[pop]
                log_likelihoods[pop] += self._genotype_log_likelihood(dosage, pop_freq)

            assayed_count += 1

        if assayed_count == 0:
            # Uniform prior baseline
            uniform_p = 1.0 / len(POPULATIONS)
            return {pop: uniform_p for pop in POPULATIONS}, 0

        # Numerically stable Softmax transformation (max subtraction)
        max_ll = max(log_likelihoods.values())
        exp_ll = {pop: math.exp(log_likelihoods[pop] - max_ll) for pop in POPULATIONS}
        total_exp = sum(exp_ll.values())

        raw_proportions = {pop: exp_ll[pop] / total_exp for pop in POPULATIONS}

        # Enforce sum-to-unity invariant: |sum q_j - 1.0| <= 1e-6
        sum_q = sum(raw_proportions.values())
        if sum_q > 0:
            norm_proportions = {pop: raw_proportions[pop] / sum_q for pop in POPULATIONS}
        else:
            norm_proportions = raw_proportions

        rounded_props = {pop: round(norm_proportions[pop], 6) for pop in POPULATIONS}
        # Exact residual adjustment on EUR
        res_sum = sum(rounded_props.values())
        rounded_props["EUR"] = round(rounded_props["EUR"] + (1.0 - res_sum), 6)

        return rounded_props, assayed_count

    # ── §2.3 Geographic Coordinate Projection & 95% Confidence Ellipse ───────

    def project_gis_coordinates(
        self,
        proportions: Dict[str, float],
    ) -> GISCoordinates:
        """
        Projects continental admixture proportions into 3D Cartesian spherical coordinates
        and recovers the weighted geographic centroid (Lat, Lng) and 95% Confidence Ellipse.

        V_pred = sum_j q_j * (cos(Lat_j)cos(Lng_j), cos(Lat_j)sin(Lng_j), sin(Lat_j))^T
        theta_Lat = arcsin(z_bar / ||V_pred||)
        theta_Lng = atan2(y_bar, x_bar)
        """
        vx, vy, vz = 0.0, 0.0, 0.0

        for pop in POPULATIONS:
            q = proportions.get(pop, 0.0)
            lat_rad = math.radians(self.centroids[pop]["lat"])
            lng_rad = math.radians(self.centroids[pop]["lng"])

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

        # Nearest continental centroid identification
        closest_pop = min(
            POPULATIONS,
            key=lambda p: (self.centroids[p]["lat"] - lat_deg)**2 + (self.centroids[p]["lng"] - lng_deg)**2
        )
        nearest_name = self.centroids[closest_pop]["name"]

        # Bivariate Spatial Dispersion & 95% Confidence Ellipse (Chi-square 2 d.o.f. = 5.991)
        var_lat = 0.0
        var_lng = 0.0
        cov_lat_lng = 0.0

        for pop in POPULATIONS:
            q = proportions.get(pop, 0.0)
            d_lat = self.centroids[pop]["lat"] - lat_deg
            d_lng = self.centroids[pop]["lng"] - lng_deg
            # Handle longitude wrap-around for angular difference
            if d_lng > 180.0:
                d_lng -= 360.0
            elif d_lng < -180.0:
                d_lng += 360.0

            var_lat += q * (d_lat ** 2)
            var_lng += q * (d_lng ** 2)
            cov_lat_lng += q * d_lat * d_lng

        # Eigenvalue decomposition of 2x2 covariance matrix
        tr = var_lat + var_lng
        det = (var_lat * var_lng) - (cov_lat_lng ** 2)
        discriminant = max(0.0, ((var_lat - var_lng) ** 2) + 4.0 * (cov_lat_lng ** 2))
        sqrt_disc = math.sqrt(discriminant)

        lambda_1 = max(0.01, (tr + sqrt_disc) / 2.0)
        lambda_2 = max(0.01, (tr - sqrt_disc) / 2.0)

        # 95% ellipse axes in degrees (chi2 critical value = 5.991)
        semi_major_deg = round(math.sqrt(5.991 * lambda_1), 3)
        semi_minor_deg = round(math.sqrt(5.991 * lambda_2), 3)
        semi_major_km = round(semi_major_deg * 111.32, 1)
        semi_minor_km = round(semi_minor_deg * 111.32, 1)

        # Orientation angle theta_tilt = 0.5 * atan2(2 * cov, var_lat - var_lng)
        tilt_rad = 0.5 * math.atan2(2.0 * cov_lat_lng, var_lat - var_lng)
        tilt_deg = round(math.degrees(tilt_rad), 2)

        ellipse = ConfidenceEllipse(
            semi_major_deg=semi_major_deg,
            semi_minor_deg=semi_minor_deg,
            semi_major_km=semi_major_km,
            semi_minor_km=semi_minor_km,
            tilt_angle_deg=tilt_deg,
        )

        lat_dir = "N" if lat_deg >= 0 else "S"
        lng_dir = "E" if lng_deg >= 0 else "W"
        formatted = f"{abs(lat_deg):.4f}° {lat_dir}, {abs(lng_deg):.4f}° {lng_dir}"

        return GISCoordinates(
            latitude=round(lat_deg, 4),
            longitude=round(lng_deg, 4),
            formatted_coords=formatted,
            nearest_centroid=nearest_name,
            confidence_ellipse=ellipse,
        )

    # ── §2.4 Full Admixture Analysis Pipeline ─────────────────────────────────

    def analyze_bga_profile(
        self,
        snp_dosages: Dict[str, Union[int, float]],
    ) -> AIMAdmixtureResult:
        """
        Executes end-to-end 55-AIM Biogeographic Ancestry estimation, GIS projection,
        and complexity classification.
        """
        proportions, assayed_count = self.estimate_admixture(snp_dosages)
        gis_coords = self.project_gis_coordinates(proportions)

        # Dominant Population
        dom_pop = max(POPULATIONS, key=lambda p: proportions[p])
        dom_prop = proportions[dom_pop]

        # Shannon Entropy H(q) = -sum q_j * ln(q_j)
        shannon = 0.0
        for p_val in proportions.values():
            if p_val > 1e-9:
                shannon -= p_val * math.log(p_val)
        shannon = round(shannon, 4)

        # Simpson Diversity Index D = 1 - sum q_j^2
        simpson = 1.0 - sum(p_val * p_val for p_val in proportions.values())
        simpson = round(simpson, 4)

        # Admixture Complexity Classification
        sorted_props = sorted(proportions.values(), reverse=True)
        if sorted_props[0] >= 0.85:
            classification = "HOMOGENEOUS"
        elif (sorted_props[0] + sorted_props[1]) >= 0.85:
            classification = "BI_ADMIXED"
        else:
            classification = "MULTI_ADMIXED"

        shield_statement = (
            "IMPORTANT (BGA Evaluative Legal Shield): Biogeographic ancestry estimates "
            "represent statistical continental admixture proportions derived from Ancestry Informative Markers (AIMs). "
            "They indicate geographic lineage probabilities and must NEVER be conflated with social race, "
            "cultural identity, or individual identification."
        )

        return AIMAdmixtureResult(
            proportions=proportions,
            dominant_population=dom_pop,
            dominant_proportion=dom_prop,
            admixture_classification=classification,
            shannon_entropy=shannon,
            simpson_diversity=simpson,
            assayed_snps_count=assayed_count,
            gis_projection=gis_coords,
            prosecutors_fallacy_shield=shield_statement,
        )
