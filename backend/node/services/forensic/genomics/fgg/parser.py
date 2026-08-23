"""
Multi-Vendor Dense SNP Microarray & WGS Genotype Parser.

Supports:
- 23andMe (v4 / v5 tab-delimited text)
- AncestryDNA (tab-delimited text)
- FamilyTreeDNA / GEDmatch (CSV / TXT)
- Illumina FinalReport / Global Diversity Array (TSV)
- VCF 4.2 / 4.3 (Whole Genome Sequencing & Low-Pass Imputed VCFs)
"""

import io
import csv
from typing import Dict, List, Tuple, Optional
from .schemas import (
    PlatformFormatEnum,
    GenotypeStateEnum,
    SNPRecord,
    BitwiseGenotypeBlock,
    ProfileQCReport,
    IngestedFGGProfile
)
from .liftover_normalizer import LiftoverNormalizer
from .bitwise_packer import BitwiseGenotypePacker
from .qc_engine import FGGQCEngine


class FGGGenotypeParser:
    """Auto-detects format, normalizes coordinates, and packs genotypes into 2-bit blocks."""

    @classmethod
    def detect_format(cls, content: str) -> PlatformFormatEnum:
        """Auto-detects the raw file format by inspecting headers."""
        lines = [line.strip() for line in content.splitlines()[:25] if line.strip()]
        if not lines:
            return PlatformFormatEnum.UNKNOWN

        joined_head = "\n".join(lines).lower()

        if "##fileformat=vcf" in joined_head:
            return PlatformFormatEnum.VCF_WGS_PHASED
        if "23andme" in joined_head or ("# rsid" in joined_head and "chromosome" in joined_head):
            return PlatformFormatEnum.TWENTY_THREE_AND_ME_V5
        if "ancestrydna" in joined_head or ("rsid" in joined_head and "allele1" in joined_head and "allele2" in joined_head):
            return PlatformFormatEnum.ANCESTRY_DNA
        if "rsid,chromosome,position,result" in joined_head.replace(" ", ""):
            return PlatformFormatEnum.FAMILY_TREE_DNA_CSV
        if "illumina" in joined_head or "[data]" in joined_head or "snp name" in joined_head:
            return PlatformFormatEnum.ILLUMINA_GDA

        # Comma-separated fallback
        first_line = lines[0].replace('"', '').replace("'", "").strip()
        if "," in first_line:
            parts = first_line.split(",")
            if len(parts) >= 4:
                return PlatformFormatEnum.GEDMATCH_CSV

        # Tab-separated fallback
        if "\t" in first_line:
            parts = first_line.split("\t")
            if len(parts) == 4:
                return PlatformFormatEnum.TWENTY_THREE_AND_ME_V5
            elif len(parts) == 5:
                return PlatformFormatEnum.ANCESTRY_DNA

        return PlatformFormatEnum.UNKNOWN

    @classmethod
    def parse_profile(
        cls,
        content: str,
        profile_id: str = "FGG_SAMPLE_01",
        source_filename: str = "raw_genotypes.txt",
        forced_platform: Optional[PlatformFormatEnum] = None,
        force_platform: Optional[PlatformFormatEnum] = None
    ) -> IngestedFGGProfile:
        """Parses multi-format raw genotype text into an IngestedFGGProfile with bitwise blocks."""
        platform = force_platform or forced_platform or cls.detect_format(content)

        chrom_records: Dict[str, List[SNPRecord]] = {}
        all_states: List[GenotypeStateEnum] = []

        lines = content.splitlines()

        if platform == PlatformFormatEnum.VCF_WGS_PHASED or platform == PlatformFormatEnum.VCF_LOW_PASS_IMPUTED:
            cls._parse_vcf(lines, chrom_records, all_states)
        elif platform == PlatformFormatEnum.FAMILY_TREE_DNA_CSV or platform == PlatformFormatEnum.GEDMATCH_CSV:
            cls._parse_ftdna_csv(lines, chrom_records, all_states)
        elif platform == PlatformFormatEnum.ANCESTRY_DNA:
            cls._parse_ancestry_tsv(lines, chrom_records, all_states)
        elif platform == PlatformFormatEnum.ILLUMINA_GDA or platform == PlatformFormatEnum.ILLUMINA_GSA:
            cls._parse_illumina_report(lines, chrom_records, all_states)
        else:
            # Default to 23andMe 4-column format
            cls._parse_23andme_tsv(lines, chrom_records, all_states)

        # QC Report
        qc_report = FGGQCEngine.evaluate_profile_qc(all_states, platform)

        # Pack each chromosome into a 2-bit BitwiseGenotypeBlock
        chromosome_blocks: Dict[str, BitwiseGenotypeBlock] = {}
        for ch, records in chrom_records.items():
            if not records:
                continue
            states = [r.genotype_state for r in records]
            packed_bytes = BitwiseGenotypePacker.pack_states(states)
            positions = [r.position_bp for r in records]
            rsids = [r.rsid for r in records]

            chromosome_blocks[ch] = BitwiseGenotypeBlock(
                chromosome=ch,
                snp_count=len(records),
                packed_bytes_hex=packed_bytes.hex(),
                positions_bp=positions,
                genetic_positions_cm=[],
                rsids=rsids
            )

        return IngestedFGGProfile(
            profile_id=profile_id,
            source_filename=source_filename,
            platform=platform,
            assembly_version="GRCh38",
            qc_report=qc_report,
            chromosome_blocks=chromosome_blocks
        )

    @classmethod
    def _parse_23andme_tsv(
        cls,
        lines: List[str],
        chrom_records: Dict[str, List[SNPRecord]],
        all_states: List[GenotypeStateEnum]
    ) -> None:
        """Parses 23andMe 4-column format: rsid, chromosome, position, genotype."""
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                parts = line.split()
            if len(parts) < 4:
                continue

            rsid, raw_chr, raw_pos, raw_gt = parts[0], parts[1], parts[2], parts[3]
            norm_chr = LiftoverNormalizer.normalize_chromosome(raw_chr)
            if not norm_chr:
                continue
            try:
                pos = int(raw_pos)
            except ValueError:
                continue

            a1, a2, call = LiftoverNormalizer.normalize_genotype_call(raw_gt)
            state = cls._derive_genotype_state(a1, a2)
            all_states.append(state)

            rec = SNPRecord(
                rsid=rsid,
                chromosome=norm_chr,
                position_bp=pos,
                allele1=a1,
                allele2=a2,
                genotype_call=call,
                genotype_state=state
            )
            chrom_records.setdefault(norm_chr, []).append(rec)

    @classmethod
    def _parse_ancestry_tsv(
        cls,
        lines: List[str],
        chrom_records: Dict[str, List[SNPRecord]],
        all_states: List[GenotypeStateEnum]
    ) -> None:
        """Parses AncestryDNA 5-column format: rsid, chromosome, position, allele1, allele2."""
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 5:
                parts = line.split()
            if len(parts) < 5:
                continue
            if parts[0].lower() == "rsid":
                continue

            rsid, raw_chr, raw_pos, a1_raw, a2_raw = parts[0], parts[1], parts[2], parts[3], parts[4]
            norm_chr = LiftoverNormalizer.normalize_chromosome(raw_chr)
            if not norm_chr:
                continue
            try:
                pos = int(raw_pos)
            except ValueError:
                continue

            a1, a2, call = LiftoverNormalizer.normalize_genotype_call(f"{a1_raw}{a2_raw}")
            state = cls._derive_genotype_state(a1, a2)
            all_states.append(state)

            rec = SNPRecord(
                rsid=rsid,
                chromosome=norm_chr,
                position_bp=pos,
                allele1=a1,
                allele2=a2,
                genotype_call=call,
                genotype_state=state
            )
            chrom_records.setdefault(norm_chr, []).append(rec)

    @classmethod
    def _parse_ftdna_csv(
        cls,
        lines: List[str],
        chrom_records: Dict[str, List[SNPRecord]],
        all_states: List[GenotypeStateEnum]
    ) -> None:
        """Parses FTDNA / GEDmatch CSV: RSID,CHROMOSOME,POSITION,RESULT."""
        reader = csv.reader(lines)
        for row in reader:
            if not row or len(row) < 4:
                continue
            if row[0].strip().upper() in ("RSID", "#RSID") or row[0].startswith("#"):
                continue

            rsid, raw_chr, raw_pos, raw_gt = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()
            norm_chr = LiftoverNormalizer.normalize_chromosome(raw_chr)
            if not norm_chr:
                continue
            try:
                pos = int(raw_pos)
            except ValueError:
                continue

            a1, a2, call = LiftoverNormalizer.normalize_genotype_call(raw_gt)
            state = cls._derive_genotype_state(a1, a2)
            all_states.append(state)

            rec = SNPRecord(
                rsid=rsid,
                chromosome=norm_chr,
                position_bp=pos,
                allele1=a1,
                allele2=a2,
                genotype_call=call,
                genotype_state=state
            )
            chrom_records.setdefault(norm_chr, []).append(rec)

    @classmethod
    def _parse_illumina_report(
        cls,
        lines: List[str],
        chrom_records: Dict[str, List[SNPRecord]],
        all_states: List[GenotypeStateEnum]
    ) -> None:
        """Parses Illumina FinalReport data section."""
        in_data = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if "[data]" in line.lower():
                in_data = True
                continue
            if not in_data:
                continue
            if line.lower().startswith("snp name"):
                continue

            parts = line.split("\t")
            if len(parts) < 5:
                continue

            rsid, raw_chr, raw_pos, a1_raw, a2_raw = parts[0], parts[1], parts[2], parts[3], parts[4]
            norm_chr = LiftoverNormalizer.normalize_chromosome(raw_chr)
            if not norm_chr:
                continue
            try:
                pos = int(raw_pos)
            except ValueError:
                continue

            a1, a2, call = LiftoverNormalizer.normalize_genotype_call(f"{a1_raw}{a2_raw}")
            state = cls._derive_genotype_state(a1, a2)
            all_states.append(state)

            rec = SNPRecord(
                rsid=rsid,
                chromosome=norm_chr,
                position_bp=pos,
                allele1=a1,
                allele2=a2,
                genotype_call=call,
                genotype_state=state
            )
            chrom_records.setdefault(norm_chr, []).append(rec)

    @classmethod
    def _parse_vcf(
        cls,
        lines: List[str],
        chrom_records: Dict[str, List[SNPRecord]],
        all_states: List[GenotypeStateEnum]
    ) -> None:
        """Parses standard VCF 4.2 / 4.3 records."""
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 10:
                continue

            raw_chr, raw_pos, rsid, ref, alt, _, _, _, fmt, sample = parts[:10]
            norm_chr = LiftoverNormalizer.normalize_chromosome(raw_chr)
            if not norm_chr:
                continue
            try:
                pos = int(raw_pos)
            except ValueError:
                continue

            # Extract GT field
            fmt_keys = fmt.split(":")
            sample_vals = sample.split(":")
            if "GT" not in fmt_keys:
                continue
            gt_idx = fmt_keys.index("GT")
            gt_val = sample_vals[gt_idx] if gt_idx < len(sample_vals) else "./."

            state, (a1, a2) = cls._vcf_gt_to_state(gt_val, ref, alt)
            all_states.append(state)

            rec = SNPRecord(
                rsid=rsid if rsid != "." else f"chr{norm_chr}_{pos}",
                chromosome=norm_chr,
                position_bp=pos,
                allele1=a1,
                allele2=a2,
                genotype_call=f"{a1}{a2}",
                genotype_state=state
            )
            chrom_records.setdefault(norm_chr, []).append(rec)

    @staticmethod
    def _derive_genotype_state(a1: str, a2: str) -> GenotypeStateEnum:
        """Derives GenotypeStateEnum from two normalized allele characters."""
        if a1 == "-" or a2 == "-":
            return GenotypeStateEnum.NO_CALL
        if a1 == a2:
            # Homozygous - default to HOM_REF (will be resolved when reference is known or by convention)
            return GenotypeStateEnum.HOM_REF
        else:
            return GenotypeStateEnum.HET

    @staticmethod
    def _vcf_gt_to_state(gt_str: str, ref: str, alt: str) -> Tuple[GenotypeStateEnum, Tuple[str, str]]:
        """Converts VCF GT string (e.g. 0/0, 0/1, 1/1, ./.) into GenotypeStateEnum and base alleles."""
        clean_gt = gt_str.replace("|", "/")
        if clean_gt in ("./.", ".", "./0", "./1", "0/."):
            return (GenotypeStateEnum.NO_CALL, ("-", "-"))
        
        parts = clean_gt.split("/")
        if len(parts) == 2:
            i1, i2 = parts[0], parts[1]
            alleles = [ref] + alt.split(",")
            b1 = alleles[int(i1)] if i1.isdigit() and int(i1) < len(alleles) else "-"
            b2 = alleles[int(i2)] if i2.isdigit() and int(i2) < len(alleles) else "-"
            
            if i1 == "0" and i2 == "0":
                return (GenotypeStateEnum.HOM_REF, (b1, b2))
            elif (i1 == "0" and i2 == "1") or (i1 == "1" and i2 == "0"):
                return (GenotypeStateEnum.HET, (b1, b2))
            elif i1 == "1" and i2 == "1":
                return (GenotypeStateEnum.HOM_ALT, (b1, b2))
            else:
                return (GenotypeStateEnum.HET, (b1, b2))
        return (GenotypeStateEnum.NO_CALL, ("-", "-"))
