"""
FORENZA Multi-Layered Forensic Genomics Architecture Engine.

Synthesizes genomic evidence across 5 hierarchical tiers:
1. Autosomal STR (Expanded 24-locus panel: 20 FBI CODIS core + ESS SE33, Penta D, Penta E)
2. Forensic SNP (HIrisPlex-S phenotyping & ancestry)
3. Lineage mtDNA (rCRS HV1/HV2/HV3 hypervariable regions)
4. Lineage Y-Chromosome (Y-FILER 23-locus haplotype)
5. Whole-Genome Sequencing / WGS (Indels, CNVs, deep WGS variants)

Computes synthesized joint likelihood ratios (LR_joint), composite exclusion probabilities (PE_joint),
and maps verdicts to ISO 17025 / ENFSI verbal scale predicates.
"""

import math
from typing import Dict, Any, List, Optional, Tuple


class MultiLayerGenomicsEngine:
    """
    Multi-Layered Forensic Genomics Evidence Synthesizer.
    """

    ENFSI_VERBAL_SCALE: List[Tuple[float, str]] = [
        (1e6, "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION"),
        (1e4, "VERY_STRONG_SUPPORT_FOR_INCLUSION"),
        (1e2, "STRONG_SUPPORT_FOR_INCLUSION"),
        (10.0, "MODERATE_SUPPORT_FOR_INCLUSION"),
        (1.0, "LIMITED_SUPPORT_FOR_INCLUSION"),
        (0.1, "INCONCLUSIVE_SUPPORT"),
        (0.001, "STRONG_SUPPORT_FOR_EXCLUSION"),
        (0.0, "EXTREMELY_STRONG_SUPPORT_FOR_EXCLUSION"),
    ]

    def synthesize_genomic_layers(
        self,
        lr_str: float = 1.0e12,
        lr_snp: float = 1.0e3,
        lr_mtdna: float = 1.0e2,
        lr_y_str: float = 1.0e4,
        lr_wgs: float = 1.0e5,
        pe_str: float = 0.999999,
        pe_snp: float = 0.995,
        pe_mtdna: float = 0.990,
        pe_y_str: float = 0.998,
        pe_wgs: float = 0.9999,
    ) -> Dict[str, Any]:
        """
        Synthesizes likelihood ratios and exclusion probabilities across 5 genomic evidence layers.

        :param lr_str: Likelihood Ratio for Autosomal STR.
        :param lr_snp: Likelihood Ratio for Forensic SNP.
        :param lr_mtdna: Likelihood Ratio for mtDNA.
        :param lr_y_str: Likelihood Ratio for Y-STR.
        :param lr_wgs: Likelihood Ratio for Whole-Genome Sequencing.
        :param pe_str: Probability of Exclusion for STR.
        :param pe_snp: Probability of Exclusion for SNP.
        :param pe_mtdna: Probability of Exclusion for mtDNA.
        :param pe_y_str: Probability of Exclusion for Y-STR.
        :param pe_wgs: Probability of Exclusion for WGS.
        :return: Dict containing synthesized joint LR, log10 LR, joint PE, and verbal scale verdict.
        """
        layers = [
            ("AUTOSOMAL_STR", float(lr_str), float(pe_str)),
            ("FORENSIC_SNP", float(lr_snp), float(pe_snp)),
            ("MATERNAL_MTDNA", float(lr_mtdna), float(pe_mtdna)),
            ("PATERNAL_Y_STR", float(lr_y_str), float(pe_y_str)),
            ("WHOLE_GENOME_WGS", float(lr_wgs), float(pe_wgs)),
        ]

        log10_lr_joint = 0.0
        pe_non_exclusion_prod = 1.0
        layer_breakdown: List[Dict[str, Any]] = []

        for name, lr, pe in layers:
            if lr <= 0.0:
                lr = 1e-10  # Protection against log(0)
            
            log10_lr = math.log10(lr)
            log10_lr_joint += log10_lr
            
            pe_clamped = min(1.0, max(0.0, pe))
            pe_non_exclusion_prod *= (1.0 - pe_clamped)

            layer_breakdown.append({
                "layer_name": name,
                "likelihood_ratio": lr,
                "log10_lr": round(log10_lr, 2),
                "exclusion_probability": pe_clamped,
                "status": "ACTIVE_EVIDENCE" if lr != 1.0 else "UNOBSERVED"
            })

        # Calculate joint LR
        lr_joint = math.pow(10.0, min(log10_lr_joint, 300.0))  # Overflow protection
        log10_lr_joint_rounded = round(log10_lr_joint, 2)
        pe_joint = round(1.0 - pe_non_exclusion_prod, 6)

        # Determine ENFSI Verbal Scale Predicate
        verbal_predicate = "INCONCLUSIVE_SUPPORT"
        for threshold, predicate in self.ENFSI_VERBAL_SCALE:
            if lr_joint >= threshold:
                verbal_predicate = predicate
                break

        return {
            "joint_likelihood_ratio": lr_joint,
            "log10_joint_likelihood_ratio": log10_lr_joint_rounded,
            "joint_exclusion_probability": pe_joint,
            "enfsi_verbal_predicate": verbal_predicate,
            "active_layer_count": sum(1 for l in layer_breakdown if l["likelihood_ratio"] != 1.0),
            "genomic_layers": layer_breakdown,
            "architecture_provenance": "FORENZA 5-Tier Multi-Omic Genomic Synthesizer"
        }
