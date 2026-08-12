"""
FORENZA Automated Analytical Instrument Parser Gateway.

Ingests raw instrument outputs from:
- CE Capillary Electrophoresis (GeneMapper HID peak tables)
- qPCR Quantifiers (Quantifiler Trio Cq & Degradation Index DI = [SA]/[LA])
- NGS Sequencers (Illumina MiSeq FGx FASTQ / VCF variant calls)
- LC-MS/MS Toxicology Mass Spectrometers
- Digital Microscopy Analyzers
"""

import csv
import json
import io
from typing import Dict, Any, List, Optional


class InstrumentParserGateway:
    """
    Automated Analytical Instrument Parser Gateway.
    """

    def parse_ce_genemapper(self, raw_csv_content: str) -> Dict[str, Any]:
        """Parses Capillary Electrophoresis (CE) GeneMapper HID peak table CSV content."""
        if not raw_csv_content.strip():
            raise ValueError("CE raw content cannot be empty.")

        reader = csv.DictReader(io.StringIO(raw_csv_content.strip()))
        peaks: List[Dict[str, Any]] = []

        for row in reader:
            sample_id = row.get("Sample Name", row.get("Sample_ID", "UNKNOWN_SAMPLE"))
            locus = row.get("Locus", row.get("Marker", "UNKNOWN_LOCUS"))
            allele1 = row.get("Allele 1", row.get("Allele1", "0"))
            allele2 = row.get("Allele 2", row.get("Allele2", "0"))
            height1 = float(row.get("Height 1", row.get("Height1", 500)))
            height2 = float(row.get("Height 2", row.get("Height2", 500)))

            peaks.append({
                "sample_id": sample_id,
                "locus": locus.strip().upper(),
                "alleles": [allele1, allele2],
                "peak_heights_rfu": [height1, height2],
                "mean_rfu": round((height1 + height2) / 2.0, 1),
            })

        return {
            "instrument_type": "CAPILLARY_ELECTROPHORESIS_CE",
            "parsed_peaks": peaks,
            "total_loci_parsed": len(peaks),
            "qc_flag": "PASS" if len(peaks) >= 16 else "WARNING_PARTIAL_PROFILE"
        }

    def parse_qpcr_quantifiler(
        self,
        small_autosomal_conc_ng_ul: float,
        large_autosomal_conc_ng_ul: float,
        male_y_conc_ng_ul: float
    ) -> Dict[str, Any]:
        """Parses qPCR Quantifiler Trio concentration data and computes Degradation Index (DI)."""
        sa = float(small_autosomal_conc_ng_ul)
        la = float(large_autosomal_conc_ng_ul)
        y_conc = float(male_y_conc_ng_ul)

        if sa < 0.0 or la < 0.0 or y_conc < 0.0:
            raise ValueError("qPCR concentrations must be non-negative.")

        # Degradation Index DI = [SA] / max(1e-6, [LA])
        di = round(sa / max(1e-6, la), 2)

        if di <= 1.5:
            degradation_assessment = "INTACT_NO_DEGRADATION"
        elif di <= 4.0:
            degradation_assessment = "MODERATELY_DEGRADED"
        else:
            degradation_assessment = "SEVERELY_DEGRADED"

        return {
            "instrument_type": "QPCR_QUANTIFICATION",
            "small_autosomal_conc_ng_ul": sa,
            "large_autosomal_conc_ng_ul": la,
            "male_y_conc_ng_ul": y_conc,
            "degradation_index_di": di,
            "degradation_assessment": degradation_assessment,
            "recommended_pcr_input_pg": round(min(1000.0, max(100.0, sa * 1000.0)), 1)
        }

    def parse_ngs_vcf(self, raw_vcf_content: str) -> Dict[str, Any]:
        """Parses Illumina MiSeq FGx VCF variant call format content."""
        if not raw_vcf_content.strip():
            raise ValueError("VCF raw content cannot be empty.")

        variants: List[Dict[str, Any]] = []
        for line in raw_vcf_content.strip().splitlines():
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) >= 5:
                chrom, pos, var_id, ref, alt = parts[:5]
                variants.append({
                    "chromosome": chrom,
                    "position": int(pos),
                    "variant_id": var_id,
                    "ref": ref,
                    "alt": alt,
                })

        return {
            "instrument_type": "NGS_ILLUMINA_MISEQ",
            "parsed_variants": variants,
            "total_snps_parsed": len(variants),
        }
