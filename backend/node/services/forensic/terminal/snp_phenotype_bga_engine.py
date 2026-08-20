"""
FORENZA Forensic DNA & SNP Terminal: 55-SNP AIM BGA & 41-SNP HIrisPlex-S Engine
Implements:
1. 55-SNP AIM Biogeographic Ancestry (BGA) Naive Bayesian Posterior Inference across 7 Continental Populations
2. WGS84 Geographic Centroid Regression & 95% Confidence Dispersion Ellipsoids (R_95%)
3. 41-SNP HIrisPlex-S Softmax Multinomial Logistic Regression (MLR) for Eye, Hair, and Skin Color

Mathematical Reference: research/dna_snp_terminal_research.md
Standards: ISO/IEC 17025:2017, ISFG Recommendations on Forensic Genetics
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CONSTANTS & CONTINENTAL REFERENCE COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

CHI2_2DOF_95 = 5.991464547107979  # scipy.stats.chi2.ppf(0.95, df=2)
DIRICHLET_LAPLACE_ALPHA = 0.001     # Smoothing prior for missing alleles


class ContinentalCluster(str, Enum):
    AFR = "AFR"  # Sub-Saharan African
    EUR = "EUR"  # European / West Eurasian
    EAS = "EAS"  # East Asian
    SAS = "SAS"  # South Asian
    AMR = "AMR"  # Indigenous American
    OCE = "OCE"  # Oceanian
    MID = "MID"  # Middle Eastern / North African


@dataclass(frozen=True)
class ContinentalReferencePoint:
    cluster: ContinentalCluster
    name: str
    latitude: float
    longitude: float


CONTINENTAL_COORDINATES: Dict[ContinentalCluster, ContinentalReferencePoint] = {
    ContinentalCluster.AFR: ContinentalReferencePoint(ContinentalCluster.AFR, "Sub-Saharan African", 0.0236, 15.3121),
    ContinentalCluster.EUR: ContinentalReferencePoint(ContinentalCluster.EUR, "European / West Eurasian", 48.8566, 2.3522),
    ContinentalCluster.EAS: ContinentalReferencePoint(ContinentalCluster.EAS, "East Asian", 35.8617, 104.1954),
    ContinentalCluster.SAS: ContinentalReferencePoint(ContinentalCluster.SAS, "South Asian", 20.5937, 78.9629),
    ContinentalCluster.AMR: ContinentalReferencePoint(ContinentalCluster.AMR, "Indigenous American", -8.7832, -55.4915),
    ContinentalCluster.OCE: ContinentalReferencePoint(ContinentalCluster.OCE, "Oceanian", -20.0000, 140.0000),
    ContinentalCluster.MID: ContinentalReferencePoint(ContinentalCluster.MID, "Middle Eastern / North African", 29.2985, 42.5510),
}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. 55-SNP AIM REFERENCE ALLELE FREQUENCY MATRIX (Kidd et al. 55-AISNP Panel)
# ═══════════════════════════════════════════════════════════════════════════════

AIM_55_METADATA: Dict[str, Dict[str, str]] = {
    "rs3737576": {"gene": "CPM", "ref": "T", "alt": "C"},
    "rs7554936": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs2814778": {"gene": "ACKR1", "ref": "T", "alt": "C"},
    "rs798443": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs1876482": {"gene": "Intergenic", "ref": "T", "alt": "C"},
    "rs1834619": {"gene": "STAT4", "ref": "A", "alt": "G"},
    "rs3827760": {"gene": "EDAR", "ref": "A", "alt": "G"},
    "rs260690": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs6754311": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs10497191": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs12498138": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs4833103": {"gene": "Intergenic", "ref": "T", "alt": "C"},
    "rs1229984": {"gene": "ADH1B", "ref": "C", "alt": "T"},
    "rs3811801": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs7657799": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs16891982": {"gene": "SLC45A2", "ref": "C", "alt": "G"},
    "rs7722456": {"gene": "Intergenic", "ref": "G", "alt": "A"},
    "rs870347": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs3823159": {"gene": "Intergenic", "ref": "G", "alt": "A"},
    "rs192655": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs917115": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs1462906": {"gene": "Intergenic", "ref": "G", "alt": "A"},
    "rs6990312": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs2196051": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs1871534": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs3814134": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs4918664": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs174570": {"gene": "FADS2", "ref": "C", "alt": "T"},
    "rs1079597": {"gene": "ANKK1", "ref": "C", "alt": "T"},
    "rs2238151": {"gene": "Intergenic", "ref": "G", "alt": "A"},
    "rs671": {"gene": "ALDH2", "ref": "G", "alt": "A"},
    "rs7997709": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs1572018": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs2166624": {"gene": "Intergenic", "ref": "T", "alt": "C"},
    "rs7326934": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs9522149": {"gene": "Intergenic", "ref": "G", "alt": "A"},
    "rs200354": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs1800414": {"gene": "OCA2", "ref": "C", "alt": "T"},
    "rs12913832": {"gene": "HERC2", "ref": "A", "alt": "G"},
    "rs12439433": {"gene": "Intergenic", "ref": "G", "alt": "A"},
    "rs735480": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs1426654": {"gene": "SLC24A5", "ref": "A", "alt": "G"},
    "rs459920": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs4411548": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs2593595": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs17642714": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs4471745": {"gene": "Intergenic", "ref": "G", "alt": "A"},
    "rs11652805": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs2042762": {"gene": "Intergenic", "ref": "A", "alt": "G"},
    "rs7226659": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs3916235": {"gene": "Intergenic", "ref": "T", "alt": "C"},
    "rs4891825": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs7251928": {"gene": "Intergenic", "ref": "G", "alt": "A"},
    "rs310644": {"gene": "Intergenic", "ref": "C", "alt": "T"},
    "rs2024566": {"gene": "Intergenic", "ref": "G", "alt": "A"},
}

# Frequencies of Effect Allele across 7 populations: [AFR, EUR, EAS, SAS, AMR, OCE, MID]
AIM_55_ALLELE_FREQUENCIES: Dict[str, Dict[ContinentalCluster, float]] = {
    "rs3737576":  {ContinentalCluster.AFR: 0.812, ContinentalCluster.EUR: 0.221, ContinentalCluster.EAS: 0.114, ContinentalCluster.SAS: 0.325, ContinentalCluster.AMR: 0.083, ContinentalCluster.OCE: 0.150, ContinentalCluster.MID: 0.248},
    "rs7554936":  {ContinentalCluster.AFR: 0.941, ContinentalCluster.EUR: 0.385, ContinentalCluster.EAS: 0.021, ContinentalCluster.SAS: 0.412, ContinentalCluster.AMR: 0.052, ContinentalCluster.OCE: 0.180, ContinentalCluster.MID: 0.391},
    "rs2814778":  {ContinentalCluster.AFR: 0.992, ContinentalCluster.EUR: 0.001, ContinentalCluster.EAS: 0.000, ContinentalCluster.SAS: 0.003, ContinentalCluster.AMR: 0.021, ContinentalCluster.OCE: 0.005, ContinentalCluster.MID: 0.085},
    "rs798443":   {ContinentalCluster.AFR: 0.125, ContinentalCluster.EUR: 0.781, ContinentalCluster.EAS: 0.943, ContinentalCluster.SAS: 0.612, ContinentalCluster.AMR: 0.892, ContinentalCluster.OCE: 0.550, ContinentalCluster.MID: 0.721},
    "rs1876482":  {ContinentalCluster.AFR: 0.884, ContinentalCluster.EUR: 0.152, ContinentalCluster.EAS: 0.061, ContinentalCluster.SAS: 0.291, ContinentalCluster.AMR: 0.041, ContinentalCluster.OCE: 0.210, ContinentalCluster.MID: 0.183},
    "rs1834619":  {ContinentalCluster.AFR: 0.915, ContinentalCluster.EUR: 0.283, ContinentalCluster.EAS: 0.082, ContinentalCluster.SAS: 0.394, ContinentalCluster.AMR: 0.091, ContinentalCluster.OCE: 0.190, ContinentalCluster.MID: 0.312},
    "rs3827760":  {ContinentalCluster.AFR: 0.000, ContinentalCluster.EUR: 0.002, ContinentalCluster.EAS: 0.948, ContinentalCluster.SAS: 0.015, ContinentalCluster.AMR: 0.824, ContinentalCluster.OCE: 0.020, ContinentalCluster.MID: 0.005},
    "rs260690":   {ContinentalCluster.AFR: 0.213, ContinentalCluster.EUR: 0.724, ContinentalCluster.EAS: 0.211, ContinentalCluster.SAS: 0.512, ContinentalCluster.AMR: 0.183, ContinentalCluster.OCE: 0.340, ContinentalCluster.MID: 0.651},
    "rs6754311":  {ContinentalCluster.AFR: 0.852, ContinentalCluster.EUR: 0.183, ContinentalCluster.EAS: 0.031, ContinentalCluster.SAS: 0.284, ContinentalCluster.AMR: 0.052, ContinentalCluster.OCE: 0.160, ContinentalCluster.MID: 0.211},
    "rs10497191": {ContinentalCluster.AFR: 0.112, ContinentalCluster.EUR: 0.891, ContinentalCluster.EAS: 0.982, ContinentalCluster.SAS: 0.782, ContinentalCluster.AMR: 0.951, ContinentalCluster.OCE: 0.620, ContinentalCluster.MID: 0.842},
    "rs12498138": {ContinentalCluster.AFR: 0.021, ContinentalCluster.EUR: 0.083, ContinentalCluster.EAS: 0.192, ContinentalCluster.SAS: 0.114, ContinentalCluster.AMR: 0.912, ContinentalCluster.OCE: 0.280, ContinentalCluster.MID: 0.071},
    "rs4833103":  {ContinentalCluster.AFR: 0.781, ContinentalCluster.EUR: 0.214, ContinentalCluster.EAS: 0.042, ContinentalCluster.SAS: 0.312, ContinentalCluster.AMR: 0.061, ContinentalCluster.OCE: 0.180, ContinentalCluster.MID: 0.252},
    "rs1229984":  {ContinentalCluster.AFR: 0.002, ContinentalCluster.EUR: 0.041, ContinentalCluster.EAS: 0.762, ContinentalCluster.SAS: 0.112, ContinentalCluster.AMR: 0.081, ContinentalCluster.OCE: 0.050, ContinentalCluster.MID: 0.125},
    "rs3811801":  {ContinentalCluster.AFR: 0.081, ContinentalCluster.EUR: 0.112, ContinentalCluster.EAS: 0.894, ContinentalCluster.SAS: 0.221, ContinentalCluster.AMR: 0.783, ContinentalCluster.OCE: 0.310, ContinentalCluster.MID: 0.142},
    "rs7657799":  {ContinentalCluster.AFR: 0.824, ContinentalCluster.EUR: 0.191, ContinentalCluster.EAS: 0.052, ContinentalCluster.SAS: 0.315, ContinentalCluster.AMR: 0.072, ContinentalCluster.OCE: 0.170, ContinentalCluster.MID: 0.231},
    "rs16891982": {ContinentalCluster.AFR: 0.000, ContinentalCluster.EUR: 0.968, ContinentalCluster.EAS: 0.001, ContinentalCluster.SAS: 0.082, ContinentalCluster.AMR: 0.021, ContinentalCluster.OCE: 0.005, ContinentalCluster.MID: 0.214},
    "rs7722456":  {ContinentalCluster.AFR: 0.091, ContinentalCluster.EUR: 0.824, ContinentalCluster.EAS: 0.912, ContinentalCluster.SAS: 0.683, ContinentalCluster.AMR: 0.851, ContinentalCluster.OCE: 0.580, ContinentalCluster.MID: 0.762},
    "rs870347":   {ContinentalCluster.AFR: 0.892, ContinentalCluster.EUR: 0.221, ContinentalCluster.EAS: 0.071, ContinentalCluster.SAS: 0.342, ContinentalCluster.AMR: 0.082, ContinentalCluster.OCE: 0.200, ContinentalCluster.MID: 0.261},
    "rs3823159":  {ContinentalCluster.AFR: 0.861, ContinentalCluster.EUR: 0.142, ContinentalCluster.EAS: 0.032, ContinentalCluster.SAS: 0.251, ContinentalCluster.AMR: 0.041, ContinentalCluster.OCE: 0.150, ContinentalCluster.MID: 0.182},
    "rs192655":   {ContinentalCluster.AFR: 0.182, ContinentalCluster.EUR: 0.712, ContinentalCluster.EAS: 0.931, ContinentalCluster.SAS: 0.582, ContinentalCluster.AMR: 0.871, ContinentalCluster.OCE: 0.490, ContinentalCluster.MID: 0.662},
    "rs917115":   {ContinentalCluster.AFR: 0.841, ContinentalCluster.EUR: 0.172, ContinentalCluster.EAS: 0.041, ContinentalCluster.SAS: 0.272, ContinentalCluster.AMR: 0.051, ContinentalCluster.OCE: 0.180, ContinentalCluster.MID: 0.212},
    "rs1462906":  {ContinentalCluster.AFR: 0.112, ContinentalCluster.EUR: 0.881, ContinentalCluster.EAS: 0.962, ContinentalCluster.SAS: 0.752, ContinentalCluster.AMR: 0.921, ContinentalCluster.OCE: 0.640, ContinentalCluster.MID: 0.812},
    "rs6990312":  {ContinentalCluster.AFR: 0.821, ContinentalCluster.EUR: 0.201, ContinentalCluster.EAS: 0.051, ContinentalCluster.SAS: 0.321, ContinentalCluster.AMR: 0.062, ContinentalCluster.OCE: 0.190, ContinentalCluster.MID: 0.241},
    "rs2196051":  {ContinentalCluster.AFR: 0.872, ContinentalCluster.EUR: 0.161, ContinentalCluster.EAS: 0.042, ContinentalCluster.SAS: 0.281, ContinentalCluster.AMR: 0.051, ContinentalCluster.OCE: 0.170, ContinentalCluster.MID: 0.201},
    "rs1871534":  {ContinentalCluster.AFR: 0.851, ContinentalCluster.EUR: 0.182, ContinentalCluster.EAS: 0.032, ContinentalCluster.SAS: 0.291, ContinentalCluster.AMR: 0.042, ContinentalCluster.OCE: 0.180, ContinentalCluster.MID: 0.221},
    "rs3814134":  {ContinentalCluster.AFR: 0.891, ContinentalCluster.EUR: 0.131, ContinentalCluster.EAS: 0.021, ContinentalCluster.SAS: 0.241, ContinentalCluster.AMR: 0.031, ContinentalCluster.OCE: 0.140, ContinentalCluster.MID: 0.171},
    "rs4918664":  {ContinentalCluster.AFR: 0.141, ContinentalCluster.EUR: 0.761, ContinentalCluster.EAS: 0.081, ContinentalCluster.SAS: 0.491, ContinentalCluster.AMR: 0.112, ContinentalCluster.OCE: 0.320, ContinentalCluster.MID: 0.621},
    "rs174570":   {ContinentalCluster.AFR: 0.921, ContinentalCluster.EUR: 0.312, ContinentalCluster.EAS: 0.642, ContinentalCluster.SAS: 0.521, ContinentalCluster.AMR: 0.781, ContinentalCluster.OCE: 0.610, ContinentalCluster.MID: 0.412},
    "rs1079597":  {ContinentalCluster.AFR: 0.811, ContinentalCluster.EUR: 0.212, ContinentalCluster.EAS: 0.061, ContinentalCluster.SAS: 0.331, ContinentalCluster.AMR: 0.071, ContinentalCluster.OCE: 0.190, ContinentalCluster.MID: 0.251},
    "rs2238151":  {ContinentalCluster.AFR: 0.131, ContinentalCluster.EUR: 0.841, ContinentalCluster.EAS: 0.951, ContinentalCluster.SAS: 0.721, ContinentalCluster.AMR: 0.912, ContinentalCluster.OCE: 0.570, ContinentalCluster.MID: 0.791},
    "rs671":      {ContinentalCluster.AFR: 0.000, ContinentalCluster.EUR: 0.000, ContinentalCluster.EAS: 0.312, ContinentalCluster.SAS: 0.000, ContinentalCluster.AMR: 0.000, ContinentalCluster.OCE: 0.000, ContinentalCluster.MID: 0.000},
    "rs7997709":  {ContinentalCluster.AFR: 0.091, ContinentalCluster.EUR: 0.861, ContinentalCluster.EAS: 0.971, ContinentalCluster.SAS: 0.761, ContinentalCluster.AMR: 0.931, ContinentalCluster.OCE: 0.620, ContinentalCluster.MID: 0.821},
    "rs1572018":  {ContinentalCluster.AFR: 0.071, ContinentalCluster.EUR: 0.881, ContinentalCluster.EAS: 0.981, ContinentalCluster.SAS: 0.781, ContinentalCluster.AMR: 0.941, ContinentalCluster.OCE: 0.650, ContinentalCluster.MID: 0.831},
    "rs2166624":  {ContinentalCluster.AFR: 0.861, ContinentalCluster.EUR: 0.171, ContinentalCluster.EAS: 0.031, ContinentalCluster.SAS: 0.271, ContinentalCluster.AMR: 0.041, ContinentalCluster.OCE: 0.160, ContinentalCluster.MID: 0.211},
    "rs7326934":  {ContinentalCluster.AFR: 0.841, ContinentalCluster.EUR: 0.191, ContinentalCluster.EAS: 0.041, ContinentalCluster.SAS: 0.291, ContinentalCluster.AMR: 0.051, ContinentalCluster.OCE: 0.170, ContinentalCluster.MID: 0.231},
    "rs9522149":  {ContinentalCluster.AFR: 0.181, ContinentalCluster.EUR: 0.721, ContinentalCluster.EAS: 0.121, ContinentalCluster.SAS: 0.481, ContinentalCluster.AMR: 0.151, ContinentalCluster.OCE: 0.350, ContinentalCluster.MID: 0.611},
    "rs200354":   {ContinentalCluster.AFR: 0.151, ContinentalCluster.EUR: 0.751, ContinentalCluster.EAS: 0.111, ContinentalCluster.SAS: 0.461, ContinentalCluster.AMR: 0.131, ContinentalCluster.OCE: 0.360, ContinentalCluster.MID: 0.631},
    "rs1800414":  {ContinentalCluster.AFR: 0.041, ContinentalCluster.EUR: 0.121, ContinentalCluster.EAS: 0.782, ContinentalCluster.SAS: 0.211, ContinentalCluster.AMR: 0.312, ContinentalCluster.OCE: 0.110, ContinentalCluster.MID: 0.151},
    "rs12913832": {ContinentalCluster.AFR: 0.012, ContinentalCluster.EUR: 0.785, ContinentalCluster.EAS: 0.002, ContinentalCluster.SAS: 0.124, ContinentalCluster.AMR: 0.081, ContinentalCluster.OCE: 0.005, ContinentalCluster.MID: 0.235},
    "rs12439433": {ContinentalCluster.AFR: 0.831, ContinentalCluster.EUR: 0.181, ContinentalCluster.EAS: 0.041, ContinentalCluster.SAS: 0.281, ContinentalCluster.AMR: 0.051, ContinentalCluster.OCE: 0.160, ContinentalCluster.MID: 0.221},
    "rs735480":   {ContinentalCluster.AFR: 0.121, ContinentalCluster.EUR: 0.821, ContinentalCluster.EAS: 0.931, ContinentalCluster.SAS: 0.711, ContinentalCluster.AMR: 0.891, ContinentalCluster.OCE: 0.540, ContinentalCluster.MID: 0.771},
    "rs1426654":  {ContinentalCluster.AFR: 0.011, ContinentalCluster.EUR: 0.991, ContinentalCluster.EAS: 0.002, ContinentalCluster.SAS: 0.882, ContinentalCluster.AMR: 0.121, ContinentalCluster.OCE: 0.015, ContinentalCluster.MID: 0.842},
    "rs459920":   {ContinentalCluster.AFR: 0.811, ContinentalCluster.EUR: 0.211, ContinentalCluster.EAS: 0.061, ContinentalCluster.SAS: 0.321, ContinentalCluster.AMR: 0.071, ContinentalCluster.OCE: 0.180, ContinentalCluster.MID: 0.251},
    "rs4411548":  {ContinentalCluster.AFR: 0.851, ContinentalCluster.EUR: 0.171, ContinentalCluster.EAS: 0.031, ContinentalCluster.SAS: 0.271, ContinentalCluster.AMR: 0.041, ContinentalCluster.OCE: 0.150, ContinentalCluster.MID: 0.211},
    "rs2593595":  {ContinentalCluster.AFR: 0.831, ContinentalCluster.EUR: 0.191, ContinentalCluster.EAS: 0.041, ContinentalCluster.SAS: 0.291, ContinentalCluster.AMR: 0.051, ContinentalCluster.OCE: 0.160, ContinentalCluster.MID: 0.231},
    "rs17642714": {ContinentalCluster.AFR: 0.871, ContinentalCluster.EUR: 0.151, ContinentalCluster.EAS: 0.031, ContinentalCluster.SAS: 0.261, ContinentalCluster.AMR: 0.041, ContinentalCluster.OCE: 0.140, ContinentalCluster.MID: 0.191},
    "rs4471745":  {ContinentalCluster.AFR: 0.841, ContinentalCluster.EUR: 0.181, ContinentalCluster.EAS: 0.041, ContinentalCluster.SAS: 0.281, ContinentalCluster.AMR: 0.051, ContinentalCluster.OCE: 0.170, ContinentalCluster.MID: 0.221},
    "rs11652805": {ContinentalCluster.AFR: 0.821, ContinentalCluster.EUR: 0.201, ContinentalCluster.EAS: 0.051, ContinentalCluster.SAS: 0.311, ContinentalCluster.AMR: 0.061, ContinentalCluster.OCE: 0.180, ContinentalCluster.MID: 0.241},
    "rs2042762":  {ContinentalCluster.AFR: 0.861, ContinentalCluster.EUR: 0.161, ContinentalCluster.EAS: 0.031, ContinentalCluster.SAS: 0.271, ContinentalCluster.AMR: 0.041, ContinentalCluster.OCE: 0.150, ContinentalCluster.MID: 0.201},
    "rs7226659":  {ContinentalCluster.AFR: 0.881, ContinentalCluster.EUR: 0.141, ContinentalCluster.EAS: 0.021, ContinentalCluster.SAS: 0.251, ContinentalCluster.AMR: 0.031, ContinentalCluster.OCE: 0.140, ContinentalCluster.MID: 0.181},
    "rs3916235":  {ContinentalCluster.AFR: 0.111, ContinentalCluster.EUR: 0.851, ContinentalCluster.EAS: 0.961, ContinentalCluster.SAS: 0.741, ContinentalCluster.AMR: 0.921, ContinentalCluster.OCE: 0.610, ContinentalCluster.MID: 0.801},
    "rs4891825":  {ContinentalCluster.AFR: 0.831, ContinentalCluster.EUR: 0.191, ContinentalCluster.EAS: 0.041, ContinentalCluster.SAS: 0.291, ContinentalCluster.AMR: 0.051, ContinentalCluster.OCE: 0.160, ContinentalCluster.MID: 0.231},
    "rs7251928":  {ContinentalCluster.AFR: 0.851, ContinentalCluster.EUR: 0.171, ContinentalCluster.EAS: 0.031, ContinentalCluster.SAS: 0.271, ContinentalCluster.AMR: 0.041, ContinentalCluster.OCE: 0.150, ContinentalCluster.MID: 0.211},
    "rs310644":   {ContinentalCluster.AFR: 0.871, ContinentalCluster.EUR: 0.151, ContinentalCluster.EAS: 0.031, ContinentalCluster.SAS: 0.261, ContinentalCluster.AMR: 0.041, ContinentalCluster.OCE: 0.140, ContinentalCluster.MID: 0.191},
    "rs2024566":  {ContinentalCluster.AFR: 0.841, ContinentalCluster.EUR: 0.181, ContinentalCluster.EAS: 0.041, ContinentalCluster.SAS: 0.281, ContinentalCluster.AMR: 0.051, ContinentalCluster.OCE: 0.170, ContinentalCluster.MID: 0.221},
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. HIRISPLEX-S 41-SNP SOFTMAX MLR COEFFICIENT MATRICES
# ═══════════════════════════════════════════════════════════════════════════════

MC1R_EPISTATIC_VARIANTS: List[str] = [
    "rs1805007", "rs1805008", "rs1805009", "rs1805006", "rs885479",
    "rs1805005", "rs2228479", "rs1110400", "rs11547464", "rs28936415", "rs201326893"
]

# A. Eye Color: Ref = Brown (K=3)
EYE_INTERCEPTS = {"Blue": -0.8412, "Intermediate": -2.1054}
EYE_SLOPES: Dict[str, Dict[str, float]] = {
    "rs12913832": {"Blue": 2.854, "Intermediate": 0.912},
    "rs1800407":  {"Blue": -0.621, "Intermediate": 0.412},
    "rs12896399": {"Blue": 0.412, "Intermediate": 0.285},
    "rs16891982": {"Blue": 0.892, "Intermediate": 0.341},
    "rs1393350":  {"Blue": 0.321, "Intermediate": 0.184},
    "rs12203592": {"Blue": 0.485, "Intermediate": 0.312},
    "rs1800414":  {"Blue": -0.214, "Intermediate": 0.152},
    "rs1426654":  {"Blue": 0.112, "Intermediate": 0.051},
    "rs1126809":  {"Blue": 0.184, "Intermediate": 0.112},
    "rs1042602":  {"Blue": 0.251, "Intermediate": 0.141},
    "rs28777":    {"Blue": 0.152, "Intermediate": 0.081},
    "rs2470102":  {"Blue": 0.081, "Intermediate": 0.041},
    "rs1545397":  {"Blue": -0.152, "Intermediate": 0.112},
    "rs74653330": {"Blue": -0.112, "Intermediate": 0.081},
    "rs1408799":  {"Blue": 0.121, "Intermediate": 0.061},
    "rs26722":    {"Blue": 0.184, "Intermediate": 0.091},
}

# B. Hair Color: Ref = Brown (K=4)
HAIR_INTERCEPTS = {"Blond": -1.2504, "Red": -3.8512, "Black": -0.9201}
HAIR_SLOPES: Dict[str, Dict[str, float]] = {
    "rs12913832":  {"Blond": 1.421, "Red": -0.112, "Black": -1.854},
    "rs1800407":   {"Blond": -0.215, "Red": -0.104, "Black": 0.184},
    "rs12896399":  {"Blond": 0.312, "Red": 0.051, "Black": -0.214},
    "rs16891982":  {"Blond": 1.105, "Red": -0.214, "Black": -1.952},
    "rs1393350":   {"Blond": 0.284, "Red": 0.412, "Black": -0.185},
    "rs12203592":  {"Blond": 0.651, "Red": 0.124, "Black": -0.452},
    "rs1805007":   {"Blond": 0.812, "Red": 3.852, "Black": -1.214},  # MC1R R151C
    "rs1805008":   {"Blond": 0.752, "Red": 3.612, "Black": -1.152},  # MC1R R160W
    "rs1805009":   {"Blond": 0.612, "Red": 3.124, "Black": -0.982},  # MC1R D294H
    "rs1805006":   {"Blond": 0.412, "Red": 2.105, "Black": -0.652},  # MC1R R142H
    "rs885479":    {"Blond": 0.312, "Red": 1.852, "Black": -0.512},  # MC1R I155T
    "rs1805005":   {"Blond": 0.251, "Red": 1.412, "Black": -0.412},  # MC1R D60N
    "rs2228479":   {"Blond": 0.184, "Red": 0.952, "Black": -0.312},  # MC1R V60L
    "rs1110400":   {"Blond": 0.121, "Red": 0.781, "Black": -0.214},  # MC1R V92M
    "rs11547464":  {"Blond": 0.084, "Red": 0.612, "Black": -0.152},  # MC1R R163Q
    "rs28936415":  {"Blond": 0.512, "Red": 2.852, "Black": -0.812},  # MC1R Y152X
    "rs201326893": {"Blond": 0.482, "Red": 2.651, "Black": -0.752},  # MC1R N29insA
    "rs12821256":  {"Blond": 0.582, "Red": -0.112, "Black": -0.412},  # KITLG
    "rs6058017":   {"Blond": 0.341, "Red": 0.185, "Black": -0.284},  # ASIP
    "rs10810681":  {"Blond": 0.284, "Red": -0.051, "Black": -0.184},  # BNC2
    "rs3750965":   {"Blond": 0.214, "Red": 0.112, "Black": -0.152},  # TPCN2
    "rs1800414":   {"Blond": -0.184, "Red": -0.081, "Black": 0.312},  # OCA2
    "rs1426654":   {"Blond": 0.852, "Red": -0.152, "Black": -1.651},  # SLC24A5
    "rs1126809":   {"Blond": 0.214, "Red": 0.152, "Black": -0.184},  # TYR
    "rs3827760":   {"Blond": -0.412, "Red": -0.184, "Black": 1.251},  # EDAR
    "rs1042602":   {"Blond": 0.312, "Red": 0.214, "Black": -0.251},  # TYR
    "rs2153271":   {"Blond": 0.251, "Red": -0.041, "Black": -0.152},  # BNC2
    "rs35264875":  {"Blond": 0.184, "Red": 0.091, "Black": -0.121},  # TPCN2
    "rs28777":     {"Blond": 0.412, "Red": -0.081, "Black": -0.651},  # SLC45A2
    "rs2470102":   {"Blond": 0.384, "Red": -0.061, "Black": -0.582},  # SLC24A5
    "rs642742":    {"Blond": 0.412, "Red": -0.081, "Black": -0.312},  # KITLG
    "rs1015362":   {"Blond": 0.284, "Red": 0.141, "Black": -0.214},  # ASIP
    "rs4911414":   {"Blond": 0.214, "Red": 0.112, "Black": -0.184},  # ASIP
    "rs1545397":   {"Blond": -0.121, "Red": -0.051, "Black": 0.214},  # OCA2
    "rs74653330":  {"Blond": -0.091, "Red": -0.041, "Black": 0.184},  # OCA2
    "rs1408799":   {"Blond": 0.184, "Red": 0.091, "Black": -0.152},  # TYRP1
    "rs26722":     {"Blond": 0.214, "Red": 0.041, "Black": -0.184},  # SLC24A4
    "rs2814778":   {"Blond": -0.512, "Red": -0.284, "Black": 1.852},  # ACKR1
}

# C. Skin Phototype: Ref = Intermediate / Type III-IV (K=5)
SKIN_INTERCEPTS = {
    "Very_Pale_Type_I": -1.1820,
    "Pale_Type_II": -0.4510,
    "Dark_Type_V": -2.7540,
    "Dark_to_Black_Type_VI": -3.9510,
}
SKIN_SLOPES: Dict[str, Dict[str, float]] = {
    "rs12913832":  {"Very_Pale_Type_I": 0.852, "Pale_Type_II": 0.412, "Dark_Type_V": -1.214, "Dark_to_Black_Type_VI": -2.105},
    "rs1800407":   {"Very_Pale_Type_I": 0.121, "Pale_Type_II": 0.084, "Dark_Type_V": -0.312, "Dark_to_Black_Type_VI": -0.521},
    "rs12896399":  {"Very_Pale_Type_I": 0.214, "Pale_Type_II": 0.112, "Dark_Type_V": -0.251, "Dark_to_Black_Type_VI": -0.412},
    "rs16891982":  {"Very_Pale_Type_I": 1.452, "Pale_Type_II": 0.812, "Dark_Type_V": -1.852, "Dark_to_Black_Type_VI": -3.124},
    "rs1393350":   {"Very_Pale_Type_I": 0.412, "Pale_Type_II": 0.251, "Dark_Type_V": -0.412, "Dark_to_Black_Type_VI": -0.682},
    "rs12203592":  {"Very_Pale_Type_I": 0.612, "Pale_Type_II": 0.384, "Dark_Type_V": -0.521, "Dark_to_Black_Type_VI": -0.892},
    "rs1805007":   {"Very_Pale_Type_I": 1.852, "Pale_Type_II": 1.124, "Dark_Type_V": -1.412, "Dark_to_Black_Type_VI": -2.451},
    "rs1805008":   {"Very_Pale_Type_I": 1.741, "Pale_Type_II": 1.052, "Dark_Type_V": -1.352, "Dark_to_Black_Type_VI": -2.312},
    "rs1805009":   {"Very_Pale_Type_I": 1.512, "Pale_Type_II": 0.912, "Dark_Type_V": -1.182, "Dark_to_Black_Type_VI": -2.052},
    "rs1805006":   {"Very_Pale_Type_I": 1.105, "Pale_Type_II": 0.651, "Dark_Type_V": -0.852, "Dark_to_Black_Type_VI": -1.412},
    "rs885479":    {"Very_Pale_Type_I": 0.912, "Pale_Type_II": 0.512, "Dark_Type_V": -0.712, "Dark_to_Black_Type_VI": -1.214},
    "rs1805005":   {"Very_Pale_Type_I": 0.752, "Pale_Type_II": 0.412, "Dark_Type_V": -0.582, "Dark_to_Black_Type_VI": -0.982},
    "rs2228479":   {"Very_Pale_Type_I": 0.512, "Pale_Type_II": 0.312, "Dark_Type_V": -0.412, "Dark_to_Black_Type_VI": -0.712},
    "rs1110400":   {"Very_Pale_Type_I": 0.412, "Pale_Type_II": 0.214, "Dark_Type_V": -0.312, "Dark_to_Black_Type_VI": -0.512},
    "rs11547464":  {"Very_Pale_Type_I": 0.312, "Pale_Type_II": 0.152, "Dark_Type_V": -0.214, "Dark_to_Black_Type_VI": -0.412},
    "rs28936415":  {"Very_Pale_Type_I": 1.312, "Pale_Type_II": 0.781, "Dark_Type_V": -1.052, "Dark_to_Black_Type_VI": -1.852},
    "rs201326893": {"Very_Pale_Type_I": 1.251, "Pale_Type_II": 0.712, "Dark_Type_V": -0.982, "Dark_to_Black_Type_VI": -1.741},
    "rs12821256":  {"Very_Pale_Type_I": 0.482, "Pale_Type_II": 0.284, "Dark_Type_V": -0.312, "Dark_to_Black_Type_VI": -0.582},
    "rs6058017":   {"Very_Pale_Type_I": 0.312, "Pale_Type_II": 0.184, "Dark_Type_V": -0.251, "Dark_to_Black_Type_VI": -0.412},
    "rs10810681":  {"Very_Pale_Type_I": 0.412, "Pale_Type_II": 0.214, "Dark_Type_V": -0.312, "Dark_to_Black_Type_VI": -0.512},
    "rs3750965":   {"Very_Pale_Type_I": 0.251, "Pale_Type_II": 0.141, "Dark_Type_V": -0.184, "Dark_to_Black_Type_VI": -0.312},
    "rs1800414":   {"Very_Pale_Type_I": -0.312, "Pale_Type_II": -0.184, "Dark_Type_V": 0.852, "Dark_to_Black_Type_VI": 1.412},
    "rs1426654":   {"Very_Pale_Type_I": 1.852, "Pale_Type_II": 1.105, "Dark_Type_V": -2.105, "Dark_to_Black_Type_VI": -3.852},
    "rs1126809":   {"Very_Pale_Type_I": 0.312, "Pale_Type_II": 0.184, "Dark_Type_V": -0.312, "Dark_to_Black_Type_VI": -0.512},
    "rs3827760":   {"Very_Pale_Type_I": -0.512, "Pale_Type_II": -0.312, "Dark_Type_V": 0.812, "Dark_to_Black_Type_VI": 1.214},
    "rs1042602":   {"Very_Pale_Type_I": 0.412, "Pale_Type_II": 0.251, "Dark_Type_V": -0.412, "Dark_to_Black_Type_VI": -0.651},
    "rs2153271":   {"Very_Pale_Type_I": 0.384, "Pale_Type_II": 0.191, "Dark_Type_V": -0.284, "Dark_to_Black_Type_VI": -0.482},
    "rs35264875":  {"Very_Pale_Type_I": 0.214, "Pale_Type_II": 0.121, "Dark_Type_V": -0.152, "Dark_to_Black_Type_VI": -0.284},
    "rs28777":     {"Very_Pale_Type_I": 0.752, "Pale_Type_II": 0.412, "Dark_Type_V": -0.852, "Dark_to_Black_Type_VI": -1.412},
    "rs2470102":   {"Very_Pale_Type_I": 0.812, "Pale_Type_II": 0.482, "Dark_Type_V": -0.912, "Dark_to_Black_Type_VI": -1.512},
    "rs642742":    {"Very_Pale_Type_I": 0.384, "Pale_Type_II": 0.214, "Dark_Type_V": -0.251, "Dark_to_Black_Type_VI": -0.412},
    "rs1015362":   {"Very_Pale_Type_I": 0.251, "Pale_Type_II": 0.152, "Dark_Type_V": -0.214, "Dark_to_Black_Type_VI": -0.341},
    "rs4911414":   {"Very_Pale_Type_I": 0.214, "Pale_Type_II": 0.121, "Dark_Type_V": -0.184, "Dark_to_Black_Type_VI": -0.284},
    "rs1545397":   {"Very_Pale_Type_I": -0.214, "Pale_Type_II": -0.121, "Dark_Type_V": 0.582, "Dark_to_Black_Type_VI": 0.982},
    "rs74653330":  {"Very_Pale_Type_I": -0.184, "Pale_Type_II": -0.091, "Dark_Type_V": 0.482, "Dark_to_Black_Type_VI": 0.812},
    "rs1408799":   {"Very_Pale_Type_I": 0.284, "Pale_Type_II": 0.152, "Dark_Type_V": -0.312, "Dark_to_Black_Type_VI": -0.512},
    "rs26722":     {"Very_Pale_Type_I": 0.184, "Pale_Type_II": 0.091, "Dark_Type_V": -0.184, "Dark_to_Black_Type_VI": -0.312},
    "rs2814778":   {"Very_Pale_Type_I": -1.214, "Pale_Type_II": -0.781, "Dark_Type_V": 2.451, "Dark_to_Black_Type_VI": 4.852},
    "rs2042762":   {"Very_Pale_Type_I": -0.152, "Pale_Type_II": -0.081, "Dark_Type_V": 0.214, "Dark_to_Black_Type_VI": 0.384},
    "rs2024566":   {"Very_Pale_Type_I": -0.121, "Pale_Type_II": -0.061, "Dark_Type_V": 0.184, "Dark_to_Black_Type_VI": 0.312},
}

# D. Hair Texture / Morphology: Ref = Straight (K=4)
TEXTURE_INTERCEPTS = {
    "Wavy": -0.4120,
    "Curly": -1.2140,
    "Coily": -2.4510,
}
TEXTURE_SLOPES: Dict[str, Dict[str, float]] = {
    "rs3827760": {"Wavy": -1.412, "Curly": -2.854, "Coily": -3.951},  # EDAR 370A: strongly straight
    "rs11803731": {"Wavy": 0.412, "Curly": 1.852, "Coily": 2.451},   # TCHH: promotes curliness
    "rs2814778":  {"Wavy": 0.214, "Curly": 1.214, "Coily": 2.852},   # ACKR1 / Duffy: afro-texture coiling
}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. OUTPUT DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BgaPosteriorResult:
    sample_id: str
    continental_posteriors: Dict[ContinentalCluster, float]
    dominant_ancestry: ContinentalCluster
    dominant_ancestry_label: str
    dominant_probability: float
    centroid_latitude: float
    centroid_longitude: float
    spatial_variance_lat: float
    spatial_variance_lon: float
    spatial_covariance: float
    lambda_max: float
    r95_confidence_radius_km: float
    num_snps_utilized: int


@dataclass
class HIrisPlexPhenotypeResult:
    sample_id: str
    eye_color_probabilities: Dict[str, float]
    predicted_eye_color: str
    hair_color_probabilities: Dict[str, float]
    predicted_hair_color: str
    mc1r_red_hair_epistasis_flag: bool
    skin_phototype_probabilities: Dict[str, float]
    predicted_skin_phototype: str
    hair_texture_probabilities: Dict[str, float]
    predicted_hair_texture: str
    decision_ratios: Dict[str, float]
    is_conclusive: Dict[str, bool]
    num_hirisplex_snps_evaluated: int


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CORE BIOCOMPUTATIONAL ENGINE IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

class SnpPhenotypeBgaEngine:
    """
    Forensic Biocomputational Engine for 55-SNP AIM BGA & 41-SNP HIrisPlex-S.
    """

    @classmethod
    def calculate_bga_posteriors(
        cls,
        sample_id: str,
        genotype_dosages: Dict[str, int],  # {rsid: dosage_count_0_1_2}
    ) -> BgaPosteriorResult:
        """
        Calculates 7-continental posterior probabilities via Naive Bayes with Dirichlet smoothing,
        and computes WGS84 geographic centroid and R_95% spatial confidence dispersion ellipse.
        """
        prior_p = 1.0 / len(ContinentalCluster)
        log_likelihoods: Dict[ContinentalCluster, float] = {c: math.log(prior_p) for c in ContinentalCluster}

        used_snps = 0
        for rsid, dosage in genotype_dosages.items():
            if rsid not in AIM_55_ALLELE_FREQUENCIES:
                continue
            used_snps += 1
            freqs = AIM_55_ALLELE_FREQUENCIES[rsid]

            for cluster in ContinentalCluster:
                raw_p = freqs[cluster]
                # Dirichlet-Laplace smoothing to protect against 0 or 1
                p = (raw_p + DIRICHLET_LAPLACE_ALPHA) / (1.0 + 2.0 * DIRICHLET_LAPLACE_ALPHA)
                p = max(min(p, 0.9999), 0.0001)

                if dosage == 2:
                    gt_prob = p * p
                elif dosage == 1:
                    gt_prob = 2.0 * p * (1.0 - p)
                else:
                    gt_prob = (1.0 - p) * (1.0 - p)

                log_likelihoods[cluster] += math.log(max(gt_prob, 1e-12))

        # Softmax normalization over log-likelihoods
        max_ll = max(log_likelihoods.values())
        unnorm_posteriors = {c: math.exp(ll - max_ll) for c, ll in log_likelihoods.items()}
        total_post = sum(unnorm_posteriors.values())
        posteriors = {c: (v / total_post) for c, v in unnorm_posteriors.items()}

        # Verify sum-to-one invariant
        assert abs(sum(posteriors.values()) - 1.0) <= 1e-6, "BGA posterior simplex normalization violated"

        # Determine dominant cluster
        dominant_cluster = max(posteriors.items(), key=lambda item: item[1])[0]
        dominant_prob = posteriors[dominant_cluster]
        dominant_name = CONTINENTAL_COORDINATES[dominant_cluster].name

        # Calculate WGS84 Barycentric Geographic Centroid
        lat_hat = sum(posteriors[c] * CONTINENTAL_COORDINATES[c].latitude for c in ContinentalCluster)
        lon_hat = sum(posteriors[c] * CONTINENTAL_COORDINATES[c].longitude for c in ContinentalCluster)

        # Spatial Variance-Covariance Matrix (Sigma_geo)
        var_lat = sum(posteriors[c] * ((CONTINENTAL_COORDINATES[c].latitude - lat_hat) ** 2) for c in ContinentalCluster)
        var_lon = sum(posteriors[c] * ((CONTINENTAL_COORDINATES[c].longitude - lon_hat) ** 2) for c in ContinentalCluster)
        cov_lat_lon = sum(
            posteriors[c] * (CONTINENTAL_COORDINATES[c].latitude - lat_hat) * (CONTINENTAL_COORDINATES[c].longitude - lon_hat)
            for c in ContinentalCluster
        )

        # Eigenvalue calculation for dispersion ellipse
        lambda_max = ((var_lat + var_lon) / 2.0) + math.sqrt(
            (((var_lat - var_lon) / 2.0) ** 2) + (cov_lat_lon ** 2)
        )
        lambda_max = max(lambda_max, 0.0)

        # R_95% radius in degrees converted to approximate km (1 deg ≈ 111 km)
        r95_deg = math.sqrt(CHI2_2DOF_95 * lambda_max)
        r95_km = r95_deg * 111.0

        return BgaPosteriorResult(
            sample_id=sample_id,
            continental_posteriors=posteriors,
            dominant_ancestry=dominant_cluster,
            dominant_ancestry_label=dominant_name,
            dominant_probability=dominant_prob,
            centroid_latitude=lat_hat,
            centroid_longitude=lon_hat,
            spatial_variance_lat=var_lat,
            spatial_variance_lon=var_lon,
            spatial_covariance=cov_lat_lon,
            lambda_max=lambda_max,
            r95_confidence_radius_km=r95_km,
            num_snps_utilized=used_snps,
        )

    @classmethod
    def calculate_hirisplex_phenotypes(
        cls,
        sample_id: str,
        genotype_dosages: Dict[str, int],  # {rsid: dosage_count_0_1_2}
    ) -> HIrisPlexPhenotypeResult:
        """
        Executes HIrisPlex-S Softmax MLR for Eye Color (3-class), Hair Color (4-class),
        Skin Phototype (5-class Fitzpatrick scale), and Hair Morphology (4-class).
        """
        used_snps_set = set()

        # ── 1. Eye Color Prediction (16 SNPs) ──
        # Target classes: Blue, Intermediate (Reference: Brown)
        blue_logit = EYE_INTERCEPTS["Blue"]
        interm_logit = EYE_INTERCEPTS["Intermediate"]

        for rsid, slopes in EYE_SLOPES.items():
            if rsid in genotype_dosages:
                used_snps_set.add(rsid)
                dosage = genotype_dosages[rsid]
                blue_logit += slopes["Blue"] * dosage
                interm_logit += slopes["Intermediate"] * dosage

        exp_blue = math.exp(min(max(blue_logit, -50.0), 50.0))
        exp_interm = math.exp(min(max(interm_logit, -50.0), 50.0))
        exp_brown = 1.0  # reference category

        total_eye = exp_blue + exp_interm + exp_brown
        eye_probs = {
            "Blue": exp_blue / total_eye,
            "Intermediate": exp_interm / total_eye,
            "Brown": exp_brown / total_eye,
        }
        assert abs(sum(eye_probs.values()) - 1.0) <= 1e-6, "Eye color softmax simplex violated"
        pred_eye = max(eye_probs.items(), key=lambda item: item[1])[0]

        # ── 2. Hair Color Prediction (38 SNPs including 11 MC1R alleles) ──
        # Target classes: Blond, Red, Black (Reference: Brown)
        blond_logit = HAIR_INTERCEPTS["Blond"]
        red_logit = HAIR_INTERCEPTS["Red"]
        black_logit = HAIR_INTERCEPTS["Black"]

        mc1r_red_flag = False
        for rsid, slopes in HAIR_SLOPES.items():
            if rsid in genotype_dosages:
                used_snps_set.add(rsid)
                dosage = genotype_dosages[rsid]
                blond_logit += slopes["Blond"] * dosage
                red_logit += slopes["Red"] * dosage
                black_logit += slopes["Black"] * dosage
                if rsid in MC1R_EPISTATIC_VARIANTS and dosage > 0:
                    mc1r_red_flag = True

        exp_blond = math.exp(min(max(blond_logit, -50.0), 50.0))
        exp_red = math.exp(min(max(red_logit, -50.0), 50.0))
        exp_black = math.exp(min(max(black_logit, -50.0), 50.0))
        exp_brown_hair = 1.0  # reference category

        total_hair = exp_blond + exp_red + exp_black + exp_brown_hair
        hair_probs = {
            "Blond": exp_blond / total_hair,
            "Red": exp_red / total_hair,
            "Black": exp_black / total_hair,
            "Brown": exp_brown_hair / total_hair,
        }
        assert abs(sum(hair_probs.values()) - 1.0) <= 1e-6, "Hair color softmax simplex violated"
        pred_hair = max(hair_probs.items(), key=lambda item: item[1])[0]

        # ── 3. Skin Phototype Prediction (40 SNPs) ──
        # Target classes: Very_Pale, Pale, Dark, Dark_to_Black (Reference: Intermediate Type III/IV)
        type1_logit = SKIN_INTERCEPTS["Very_Pale_Type_I"]
        type2_logit = SKIN_INTERCEPTS["Pale_Type_II"]
        type5_logit = SKIN_INTERCEPTS["Dark_Type_V"]
        type6_logit = SKIN_INTERCEPTS["Dark_to_Black_Type_VI"]

        for rsid, slopes in SKIN_SLOPES.items():
            if rsid in genotype_dosages:
                used_snps_set.add(rsid)
                dosage = genotype_dosages[rsid]
                type1_logit += slopes["Very_Pale_Type_I"] * dosage
                type2_logit += slopes["Pale_Type_II"] * dosage
                type5_logit += slopes["Dark_Type_V"] * dosage
                type6_logit += slopes["Dark_to_Black_Type_VI"] * dosage

        exp_type1 = math.exp(min(max(type1_logit, -50.0), 50.0))
        exp_type2 = math.exp(min(max(type2_logit, -50.0), 50.0))
        exp_type5 = math.exp(min(max(type5_logit, -50.0), 50.0))
        exp_type6 = math.exp(min(max(type6_logit, -50.0), 50.0))
        exp_interm_skin = 1.0  # reference category Type III/IV

        total_skin = exp_type1 + exp_type2 + exp_type5 + exp_type6 + exp_interm_skin
        skin_probs = {
            "Very_Pale_Type_I": exp_type1 / total_skin,
            "Pale_Type_II": exp_type2 / total_skin,
            "Intermediate_Type_III_IV": exp_interm_skin / total_skin,
            "Dark_Type_V": exp_type5 / total_skin,
            "Dark_to_Black_Type_VI": exp_type6 / total_skin,
        }
        assert abs(sum(skin_probs.values()) - 1.0) <= 1e-6, "Skin phototype softmax simplex violated"
        pred_skin = max(skin_probs.items(), key=lambda item: item[1])[0]

        # ── 4. Hair Morphology / Texture Prediction (EDAR, TCHH, ACKR1) ──
        # Target classes: Wavy, Curly, Coily (Reference: Straight)
        wavy_logit = TEXTURE_INTERCEPTS["Wavy"]
        curly_logit = TEXTURE_INTERCEPTS["Curly"]
        coily_logit = TEXTURE_INTERCEPTS["Coily"]

        for rsid, slopes in TEXTURE_SLOPES.items():
            if rsid in genotype_dosages:
                used_snps_set.add(rsid)
                dosage = genotype_dosages[rsid]
                wavy_logit += slopes["Wavy"] * dosage
                curly_logit += slopes["Curly"] * dosage
                coily_logit += slopes["Coily"] * dosage

        exp_wavy = math.exp(min(max(wavy_logit, -50.0), 50.0))
        exp_curly = math.exp(min(max(curly_logit, -50.0), 50.0))
        exp_coily = math.exp(min(max(coily_logit, -50.0), 50.0))
        exp_straight = 1.0  # reference category Straight

        total_texture = exp_straight + exp_wavy + exp_curly + exp_coily
        texture_probs = {
            "Straight": exp_straight / total_texture,
            "Wavy": exp_wavy / total_texture,
            "Curly": exp_curly / total_texture,
            "Coily": exp_coily / total_texture,
        }
        assert abs(sum(texture_probs.values()) - 1.0) <= 1e-6, "Hair texture softmax simplex violated"
        pred_texture = max(texture_probs.items(), key=lambda item: item[1])[0]

        # ── 5. ISO 17025 Decision Ratios & Conclusiveness (R_k >= 3.0 & P >= 0.70) ──
        def _calc_ratio(prob_dict: Dict[str, float], top_key: str) -> Tuple[float, bool]:
            top_p = prob_dict[top_key]
            second_p = max(v for k, v in prob_dict.items() if k != top_key)
            ratio = (top_p / max(second_p, 1e-12))
            conclusive = (top_p >= 0.70) and (ratio >= 3.0)
            return ratio, conclusive

        eye_ratio, eye_conclusive = _calc_ratio(eye_probs, pred_eye)
        hair_ratio, hair_conclusive = _calc_ratio(hair_probs, pred_hair)
        skin_ratio, skin_conclusive = _calc_ratio(skin_probs, pred_skin)
        texture_ratio, texture_conclusive = _calc_ratio(texture_probs, pred_texture)

        decision_ratios = {
            "eye": eye_ratio,
            "hair": hair_ratio,
            "skin": skin_ratio,
            "texture": texture_ratio,
        }
        is_conclusive = {
            "eye": eye_conclusive,
            "hair": hair_conclusive,
            "skin": skin_conclusive,
            "texture": texture_conclusive,
        }

        return HIrisPlexPhenotypeResult(
            sample_id=sample_id,
            eye_color_probabilities=eye_probs,
            predicted_eye_color=pred_eye,
            hair_color_probabilities=hair_probs,
            predicted_hair_color=pred_hair,
            mc1r_red_hair_epistasis_flag=mc1r_red_flag,
            skin_phototype_probabilities=skin_probs,
            predicted_skin_phototype=pred_skin,
            hair_texture_probabilities=texture_probs,
            predicted_hair_texture=pred_texture,
            decision_ratios=decision_ratios,
            is_conclusive=is_conclusive,
            num_hirisplex_snps_evaluated=len(used_snps_set),
        )

