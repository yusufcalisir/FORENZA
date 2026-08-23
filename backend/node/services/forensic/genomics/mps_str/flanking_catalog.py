"""
FORENZA Flanking Region Mutation Catalog (31 Variants across 9 Autosomal STR Loci).
Source: Scientific Reports (2021) 11:3485 & ISFG Forensic STR Sequence Structure Guide v5.
"""

from typing import Dict, List, Optional
from .schemas import FlankingVariant, VariantType

# Master registry of 31 flanking variants across 9 autosomal STR loci
FLANKING_MUTATION_REGISTRY: Dict[str, List[FlankingVariant]] = {
    "SE33": [
        FlankingVariant(
            rs_id="rs9362477",
            position_relative=-42,
            ref_allele="C",
            alt_allele="T",
            variant_type=VariantType.SNP,
            population_note="Global polymorphic variant (~48.5% frequency, alleles 12-34)"
        ),
        FlankingVariant(
            rs_id="rs536914220",
            position_relative=-18,
            ref_allele="C",
            alt_allele="T",
            variant_type=VariantType.SNP,
            population_note="Korean and East Asian enriched (alleles 16.2-28.2)"
        ),
        FlankingVariant(
            rs_id="rs1429028170",
            position_relative=-8,
            ref_allele="C",
            alt_allele="T",
            variant_type=VariantType.SNP,
            population_note="African-American enriched (alleles 24.2, 26.2)"
        ),
        FlankingVariant(
            rs_id="rs1391198277",
            position_relative=14,
            ref_allele="TTCT",
            alt_allele="",
            variant_type=VariantType.DELETION,
            population_note="4-bp deletion in 3' flanking region (alleles 19.2-31.2)"
        ),
        FlankingVariant(
            rs_id="rs1452632862",
            position_relative=28,
            ref_allele="T",
            alt_allele="",
            variant_type=VariantType.DELETION,
            population_note="1-bp deletion in 3' flanking region (Caucasian/Hispanic alleles 15-22.2)"
        ),
        FlankingVariant(
            rs_id="rs151261950",
            position_relative=45,
            ref_allele="CTTT",
            alt_allele="",
            variant_type=VariantType.DELETION,
            population_note="4-bp deletion in 3' flanking region (African-American alleles 20.2-29.2)"
        ),
        FlankingVariant(
            rs_id="rs1277875566",
            position_relative=62,
            ref_allele="T",
            alt_allele="C",
            variant_type=VariantType.SNP,
            population_note="Global 3' flanking transition (alleles 27.2-36.2)"
        ),
        # Crucial 4-bp deletions causing CE vs MPS primer binding shifts:
        FlankingVariant(
            rs_id="rs369314007",
            position_relative=32,
            ref_allele="TTTT",
            alt_allele="",
            variant_type=VariantType.DELETION,
            population_note="4-bp [TTTT/-] deletion causing +1 repeat shift in MPS vs CE"
        ),
        FlankingVariant(
            rs_id="rs1371483225",
            position_relative=36,
            ref_allele="TCTT",
            alt_allele="",
            variant_type=VariantType.DELETION,
            population_note="4-bp [TCTT/-] deletion causing +1 repeat shift in MPS vs CE"
        ),
    ],
    "vWA": [
        FlankingVariant(
            rs_id="rs771794429",
            position_relative=-12,
            ref_allele="G",
            alt_allele="A",
            variant_type=VariantType.SNP,
            population_note="West African specific primer-binding mutation causing allele 12-15 dropouts"
        ),
        FlankingVariant(
            rs_id="rs11613049",
            position_relative=18,
            ref_allele="C",
            alt_allele="T",
            variant_type=VariantType.SNP,
            population_note="Common 3' flanking variant"
        ),
    ],
    "D1S1656": [
        FlankingVariant(
            rs_id="rs4847015",
            position_relative=24,
            ref_allele="A",
            alt_allele="G",
            variant_type=VariantType.SNP,
            population_note="Strongly linked to 0.3 microvariant alleles (14.3-19.3)"
        ),
    ],
    "D13S317": [
        FlankingVariant(rs_id="rs25768", position_relative=-30, ref_allele="A", alt_allele="T", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs7330058", position_relative=-15, ref_allele="G", alt_allele="A", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs7330059", position_relative=-9, ref_allele="C", alt_allele="T", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs9546571", position_relative=12, ref_allele="A", alt_allele="G", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs9546572", position_relative=25, ref_allele="C", alt_allele="T", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs9546573", position_relative=42, ref_allele="T", alt_allele="C", variant_type=VariantType.SNP),
    ],
    "D7S820": [
        FlankingVariant(rs_id="rs16887642", position_relative=-22, ref_allele="A", alt_allele="G", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs6958444", position_relative=-11, ref_allele="C", alt_allele="T", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs7783935", position_relative=16, ref_allele="T", alt_allele="C", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs7783936", position_relative=34, ref_allele="G", alt_allele="A", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs7783937", position_relative=50, ref_allele="A", alt_allele="T", variant_type=VariantType.SNP),
    ],
    "D16S539": [
        FlankingVariant(rs_id="rs11642858", position_relative=-18, ref_allele="G", alt_allele="A", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs11642859", position_relative=14, ref_allele="C", alt_allele="T", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs7202492", position_relative=28, ref_allele="A", alt_allele="G", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs7202493", position_relative=46, ref_allele="T", alt_allele="C", variant_type=VariantType.SNP),
    ],
    "Penta D": [
        FlankingVariant(rs_id="rs28368834", position_relative=-14, ref_allele="C", alt_allele="T", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs28368835", position_relative=22, ref_allele="A", alt_allele="G", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs28368836", position_relative=40, ref_allele="G", alt_allele="C", variant_type=VariantType.SNP),
    ],
    "D5S818": [
        FlankingVariant(rs_id="rs25765", position_relative=-20, ref_allele="T", alt_allele="C", variant_type=VariantType.SNP),
        FlankingVariant(rs_id="rs25766", position_relative=15, ref_allele="G", alt_allele="A", variant_type=VariantType.SNP),
    ],
    "D18S51": [
        FlankingVariant(rs_id="rs11664188", position_relative=26, ref_allele="A", alt_allele="G", variant_type=VariantType.SNP),
    ],
}


def get_flanking_variants_for_locus(locus_name: str) -> List[FlankingVariant]:
    """Retrieve all known flanking variants cataloged for a specific locus."""
    return FLANKING_MUTATION_REGISTRY.get(locus_name, [])


def find_flanking_variant_by_rsid(rs_id: str) -> Optional[FlankingVariant]:
    """Look up a specific flanking variant across all loci by its dbSNP rsID."""
    for locus, variants in FLANKING_MUTATION_REGISTRY.items():
        for var in variants:
            if var.rs_id.lower() == rs_id.lower():
                return var
    return None
