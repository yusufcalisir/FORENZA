"""
Multi-Vendor Genotype Parser for Forensic AIMs & Microhaplotype Datasets.

Ingests and normalizes:
- Microarray raw tabular text (23andMe, AncestryDNA, FamilyTreeDNA)
- Massively Parallel Sequencing (MPS) VCF 4.2 / ForenSeq / AmpliSeq
- Capillary Electrophoresis SNaPshot multiplex call tables
"""

import re
from typing import Dict, List, Optional, Tuple
from backend.node.services.forensic.genomics.bga.schemas import (
    PlatformFormatEnum,
    AIMPanelTypeEnum,
    GenomicAssemblyEnum,
    GenotypeCall,
    IngestedBGASample
)
from backend.node.services.forensic.genomics.bga.panel_registry import AIMPanelRegistry
from backend.node.services.forensic.genomics.bga.liftover_normalizer import BGALiftoverNormalizer


class BGAGenotypeParser:
    """Auto-detects and parses multi-platform forensic genotype data."""

    @classmethod
    def detect_format(cls, raw_content: str) -> Tuple[PlatformFormatEnum, GenomicAssemblyEnum]:
        """Inspects file headers to classify vendor format and assembly build."""
        lines = [line.strip() for line in raw_content.splitlines() if line.strip()][:30]

        # 23andMe detection
        if any("23andme" in l.lower() or l.startswith("# rsid\tchromosome") for l in lines):
            assembly = GenomicAssemblyEnum.GRCH37 if any("build 37" in l.lower() for l in lines) else GenomicAssemblyEnum.GRCH38
            return PlatformFormatEnum.MICROARRAY_23ANDME, assembly

        # AncestryDNA detection
        if any("ancestrydna" in l.lower() or "rsid\tchromosome\tposition\tallele1\tallele2" in l.lower() for l in lines):
            return PlatformFormatEnum.MICROARRAY_ANCESTRYDNA, GenomicAssemblyEnum.GRCH37

        # FTDNA CSV detection
        if any("family tree dna" in l.lower() or '"rsid","chromosome","position","result"' in l.lower().replace(" ", "") for l in lines):
            return PlatformFormatEnum.MICROARRAY_FTDNA, GenomicAssemblyEnum.GRCH37

        # VCF detection
        if any(l.startswith("##fileformat=VCF") for l in lines) or any(l.startswith("#CHROM\tPOS\tID") for l in lines):
            assembly = GenomicAssemblyEnum.GRCH38 if any("grch38" in l.lower() or "hg38" in l.lower() for l in lines) else GenomicAssemblyEnum.GRCH37
            if any("forenseq" in l.lower() or "ampliseq" in l.lower() for l in lines):
                return PlatformFormatEnum.FORENSEQ_VCF, assembly
            return PlatformFormatEnum.WGS_VCF_4_2, assembly

        # AmpliSeq / SNaPshot TSV detection
        if any("\t" in l and ("rs" in l or "mh" in l) for l in lines):
            return PlatformFormatEnum.AMPLISEQ_TSV, GenomicAssemblyEnum.GRCH38

        return PlatformFormatEnum.UNKNOWN, GenomicAssemblyEnum.GRCH38

    @classmethod
    def parse_raw_text(
        cls,
        raw_text: str,
        sample_id: str = "SAMPLE_BGA",
        force_panel: Optional[AIMPanelTypeEnum] = None
    ) -> IngestedBGASample:
        """Parses raw text payload into standardized IngestedBGASample."""
        platform, assembly = cls.detect_format(raw_text)
        genotypes: Dict[str, GenotypeCall] = {}

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        if platform == PlatformFormatEnum.MICROARRAY_23ANDME:
            genotypes = cls._parse_23andme(lines)
        elif platform == PlatformFormatEnum.MICROARRAY_ANCESTRYDNA:
            genotypes = cls._parse_ancestrydna(lines)
        elif platform == PlatformFormatEnum.MICROARRAY_FTDNA:
            genotypes = cls._parse_ftdna(lines)
        elif platform in (PlatformFormatEnum.WGS_VCF_4_2, PlatformFormatEnum.FORENSEQ_VCF):
            genotypes = cls._parse_vcf(lines)
        else:
            # General tab-delimited or SNaPshot parser
            genotypes = cls._parse_generic_tsv(lines)

        # Detect primary panel membership
        kidd_count = sum(1 for loc in AIMPanelRegistry.get_panel_loci(AIMPanelTypeEnum.KIDD_55) if loc.rs_id in genotypes)
        visage_count = sum(1 for loc in AIMPanelRegistry.get_panel_loci(AIMPanelTypeEnum.VISAGE_BASIC_153) if loc.rs_id in genotypes)

        assigned_panel = force_panel or (
            AIMPanelTypeEnum.VISAGE_BASIC_153 if visage_count >= 20 else AIMPanelTypeEnum.KIDD_55
        )

        expected_loci = len(AIMPanelRegistry.get_panel_loci(assigned_panel)) or 55
        called_count = sum(1 for g in genotypes.values() if g.allele_1 not in ("-", "0", ".", "N"))
        call_rate = (called_count / max(1, expected_loci)) * 100.0
        het_count = sum(1 for g in genotypes.values() if g.is_heterozygous)
        het_rate = (het_count / max(1, called_count)) * 100.0

        return IngestedBGASample(
            sample_id=sample_id,
            detected_platform=platform,
            primary_panel=assigned_panel,
            assembly=assembly,
            genotypes=genotypes,
            total_loci_assayed=expected_loci,
            called_loci_count=called_count,
            call_rate=min(100.0, call_rate),
            heterozygosity_rate=round(het_rate, 2)
        )

    @classmethod
    def _parse_23andme(cls, lines: List[str]) -> Dict[str, GenotypeCall]:
        results = {}
        for line in lines:
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 4:
                rs_id = parts[0].strip()
                gt_str = parts[3].strip().upper()
                if len(gt_str) == 2:
                    a1, a2 = gt_str[0], gt_str[1]
                elif len(gt_str) == 1:
                    a1, a2 = gt_str[0], gt_str[0]
                else:
                    a1, a2 = "-", "-"

                norm_a1, norm_a2, dosage = BGALiftoverNormalizer.normalize_genotype_strand(rs_id, a1, a2)
                results[rs_id] = GenotypeCall(
                    locus_id=rs_id,
                    allele_1=norm_a1,
                    allele_2=norm_a2,
                    is_heterozygous=(norm_a1 != norm_a2 and norm_a1 != "-"),
                    dosage_alt=dosage
                )
        return results

    @classmethod
    def _parse_ancestrydna(cls, lines: List[str]) -> Dict[str, GenotypeCall]:
        results = {}
        for line in lines:
            if line.startswith("#") or "allele1" in line.lower():
                continue
            parts = line.split("\t")
            if len(parts) >= 5:
                rs_id = parts[0].strip()
                a1 = parts[3].strip().upper()
                a2 = parts[4].strip().upper()
                norm_a1, norm_a2, dosage = BGALiftoverNormalizer.normalize_genotype_strand(rs_id, a1, a2)
                results[rs_id] = GenotypeCall(
                    locus_id=rs_id,
                    allele_1=norm_a1,
                    allele_2=norm_a2,
                    is_heterozygous=(norm_a1 != norm_a2 and norm_a1 != "-"),
                    dosage_alt=dosage
                )
        return results

    @classmethod
    def _parse_ftdna(cls, lines: List[str]) -> Dict[str, GenotypeCall]:
        results = {}
        for line in lines:
            if line.startswith("#") or "rsid" in line.lower():
                continue
            cleaned = line.replace('"', '')
            parts = cleaned.split(",")
            if len(parts) >= 4:
                rs_id = parts[0].strip()
                gt_str = parts[3].strip().upper()
                if len(gt_str) == 2:
                    a1, a2 = gt_str[0], gt_str[1]
                elif len(gt_str) == 1:
                    a1, a2 = gt_str[0], gt_str[0]
                else:
                    a1, a2 = "-", "-"

                norm_a1, norm_a2, dosage = BGALiftoverNormalizer.normalize_genotype_strand(rs_id, a1, a2)
                results[rs_id] = GenotypeCall(
                    locus_id=rs_id,
                    allele_1=norm_a1,
                    allele_2=norm_a2,
                    is_heterozygous=(norm_a1 != norm_a2 and norm_a1 != "-"),
                    dosage_alt=dosage
                )
        return results

    @classmethod
    def _parse_vcf(cls, lines: List[str]) -> Dict[str, GenotypeCall]:
        results = {}
        for line in lines:
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 10:
                rs_id = parts[2].strip()
                ref = parts[3].strip().upper()
                alt = parts[4].strip().upper()
                gt_field = parts[9].split(":")[0]  # e.g. "0/1" or "1|1"

                alleles_pool = [ref] + alt.split(",")
                match = re.match(r"(\.|\d+)[\/\|](\.|\d+)", gt_field)
                if match:
                    idx1, idx2 = match.group(1), match.group(2)
                    if idx1 != "." and idx2 != ".":
                        a1 = alleles_pool[int(idx1)]
                        a2 = alleles_pool[int(idx2)]
                    else:
                        a1, a2 = "-", "-"
                else:
                    a1, a2 = "-", "-"

                norm_a1, norm_a2, dosage = BGALiftoverNormalizer.normalize_genotype_strand(rs_id, a1, a2)
                results[rs_id] = GenotypeCall(
                    locus_id=rs_id,
                    allele_1=norm_a1,
                    allele_2=norm_a2,
                    is_heterozygous=(norm_a1 != norm_a2 and norm_a1 != "-"),
                    dosage_alt=dosage
                )
        return results

    @classmethod
    def _parse_generic_tsv(cls, lines: List[str]) -> Dict[str, GenotypeCall]:
        results = {}
        for line in lines:
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                rs_id = parts[0].strip()
                call_str = parts[1].strip().upper()
                if len(parts) >= 3 and len(parts[1]) == 1 and len(parts[2]) == 1:
                    a1, a2 = parts[1].strip().upper(), parts[2].strip().upper()
                elif len(call_str) == 2:
                    a1, a2 = call_str[0], call_str[1]
                elif len(call_str) == 1:
                    a1, a2 = call_str[0], call_str[0]
                elif "/" in call_str:
                    split_call = call_str.split("/")
                    a1, a2 = split_call[0], split_call[1]
                else:
                    a1, a2 = call_str, call_str

                norm_a1, norm_a2, dosage = BGALiftoverNormalizer.normalize_genotype_strand(rs_id, a1, a2)
                results[rs_id] = GenotypeCall(
                    locus_id=rs_id,
                    allele_1=norm_a1,
                    allele_2=norm_a2,
                    is_heterozygous=(norm_a1 != norm_a2 and norm_a1 != "-"),
                    dosage_alt=dosage
                )
        return results
