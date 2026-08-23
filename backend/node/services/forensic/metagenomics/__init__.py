"""
FORENZA — Metagenomic Taxonomic Classifiers Module
===================================================

Subsystems:
    - Pillar 7 §35: Forensic Soil Pedology & Geochemical CoDa (SOIL-CODA)
    - Pillar 7 §36: Forensic Palynology & Environmental eDNA (PALYNOLOGY)
    - Pillar 7 §38: Multi-Criteria Bayesian Evidence Fusion (FUSION)
    - Pillar 4 §23: Forensic Microbiome & Thanatometagenomics (MICROBIOME)

Research Source of Truth:
    research/metagenomic_taxonomic_classifiers_soil_palynology_research.md
"""

from .schemas import (
    TaxonomicRank,
    TaxonNode,
    MetagenomicRead,
    KmerHashEntry,
    ClassifierEngine,
    ClassifierConfig,
    KReportNode,
    TaxonomicProfile,
    ASVTaxonomicAssignment,
    ASVFeatureTable,
)
from .kraken2_engine import Kraken2Engine
from .krakenuniq_engine import KrakenUniqEngine

__all__ = [
    "TaxonomicRank",
    "TaxonNode",
    "MetagenomicRead",
    "KmerHashEntry",
    "ClassifierEngine",
    "ClassifierConfig",
    "KReportNode",
    "TaxonomicProfile",
    "ASVTaxonomicAssignment",
    "ASVFeatureTable",
    "Kraken2Engine",
    "KrakenUniqEngine",
]
