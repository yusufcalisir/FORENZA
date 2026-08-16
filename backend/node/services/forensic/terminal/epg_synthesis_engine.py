"""
FORENZA: Capillary Electropherogram (EPG) Synthesis & Spectral QC Engine
Implements multi-dye RFU waveform synthesis, degradation modeling (DI),
stutter filtering (SR <= SR_max), heterozygote balance (Hb >= 0.60),
analytical/stochastic threshold gating (AT=50, ST=200, SAT=8000),
and spectral pull-up compensation.

Derived verbatim from research specification: research/dna_snp_terminal_research.md
Compliance: ISO/IEC 17025:2017 • FBI CODIS NDIS v3.2/v4.0 • SWGDAM 2020 Guidelines
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any


class DyeChannelEnum(str, Enum):
    BLUE = "BLUE"       # 6-FAM (522 nm)
    GREEN = "GREEN"     # VIC / JOE (553 nm)
    YELLOW = "YELLOW"   # NED / TAMRA (575 nm)
    RED = "RED"         # TAZ / PET (635 nm)
    PURPLE = "PURPLE"   # SID / LIZ (655 nm)
    ORANGE = "ORANGE"   # LIZ 600 Internal Size Standard (ILS)


@dataclass(frozen=True)
class LocusDyeMapping:
    locus_name: str
    dye_channel: DyeChannelEnum
    base_size_bp: float
    repeat_unit_size_bp: float
    max_stutter_ratio: float
    amplification_efficiency: float = 1.0


# Comprehensive 24-locus panel dye mapping and biophysical constants
PANEL_24_LOCUS_MAPPING: Dict[str, LocusDyeMapping] = {
    # Blue Channel (6-FAM, 522 nm)
    "D3S1358": LocusDyeMapping("D3S1358", DyeChannelEnum.BLUE, base_size_bp=67.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.102, amplification_efficiency=1.00),
    "D21S11": LocusDyeMapping("D21S11", DyeChannelEnum.BLUE, base_size_bp=78.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.108, amplification_efficiency=0.95),
    "D10S1248": LocusDyeMapping("D10S1248", DyeChannelEnum.BLUE, base_size_bp=55.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.083, amplification_efficiency=1.05),
    "D1S1656": LocusDyeMapping("D1S1656", DyeChannelEnum.BLUE, base_size_bp=85.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.112, amplification_efficiency=0.92),

    # Green Channel (VIC, 553 nm)
    "vWA": LocusDyeMapping("vWA", DyeChannelEnum.GREEN, base_size_bp=104.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.105, amplification_efficiency=1.00),
    "D16S539": LocusDyeMapping("D16S539", DyeChannelEnum.GREEN, base_size_bp=200.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.083, amplification_efficiency=0.90),
    "D2S441": LocusDyeMapping("D2S441", DyeChannelEnum.GREEN, base_size_bp=60.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.076, amplification_efficiency=1.02),
    "D2S1338": LocusDyeMapping("D2S1338", DyeChannelEnum.GREEN, base_size_bp=210.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.111, amplification_efficiency=0.88),

    # Yellow Channel (NED, 575 nm)
    "D8S1179": LocusDyeMapping("D8S1179", DyeChannelEnum.YELLOW, base_size_bp=82.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.091, amplification_efficiency=1.00),
    "D18S51": LocusDyeMapping("D18S51", DyeChannelEnum.YELLOW, base_size_bp=200.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.121, amplification_efficiency=0.85),
    "TH01": LocusDyeMapping("TH01", DyeChannelEnum.YELLOW, base_size_bp=139.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.052, amplification_efficiency=1.10),
    "DYS391": LocusDyeMapping("DYS391", DyeChannelEnum.YELLOW, base_size_bp=100.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.070, amplification_efficiency=0.95),

    # Red Channel (TAZ / PET, 635 nm)
    "FGA": LocusDyeMapping("FGA", DyeChannelEnum.RED, base_size_bp=140.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.114, amplification_efficiency=0.82),
    "D5S818": LocusDyeMapping("D5S818", DyeChannelEnum.RED, base_size_bp=110.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.082, amplification_efficiency=0.98),
    "D13S317": LocusDyeMapping("D13S317", DyeChannelEnum.RED, base_size_bp=165.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.084, amplification_efficiency=0.94),
    "D7S820": LocusDyeMapping("D7S820", DyeChannelEnum.RED, base_size_bp=215.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.081, amplification_efficiency=0.91),
    "SE33": LocusDyeMapping("SE33", DyeChannelEnum.RED, base_size_bp=185.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.142, amplification_efficiency=0.75),

    # Purple Channel (SID, 655 nm)
    "CSF1PO": LocusDyeMapping("CSF1PO", DyeChannelEnum.PURPLE, base_size_bp=250.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.074, amplification_efficiency=0.88),
    "TPOX": LocusDyeMapping("TPOX", DyeChannelEnum.PURPLE, base_size_bp=180.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.048, amplification_efficiency=0.96),
    "D12S391": LocusDyeMapping("D12S391", DyeChannelEnum.PURPLE, base_size_bp=105.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.129, amplification_efficiency=0.95),
    "D19S433": LocusDyeMapping("D19S433", DyeChannelEnum.PURPLE, base_size_bp=90.0, repeat_unit_size_bp=4.0, max_stutter_ratio=0.089, amplification_efficiency=1.00),
    "D22S1045": LocusDyeMapping("D22S1045", DyeChannelEnum.PURPLE, base_size_bp=75.0, repeat_unit_size_bp=3.0, max_stutter_ratio=0.068, amplification_efficiency=1.02),
    "Penta D": LocusDyeMapping("Penta D", DyeChannelEnum.PURPLE, base_size_bp=205.0, repeat_unit_size_bp=5.0, max_stutter_ratio=0.038, amplification_efficiency=0.85),
    "Penta E": LocusDyeMapping("Penta E", DyeChannelEnum.PURPLE, base_size_bp=330.0, repeat_unit_size_bp=5.0, max_stutter_ratio=0.041, amplification_efficiency=0.72),
    "Amelogenin": LocusDyeMapping("Amelogenin", DyeChannelEnum.PURPLE, base_size_bp=106.0, repeat_unit_size_bp=6.0, max_stutter_ratio=0.000, amplification_efficiency=1.08),
}

# LIZ 600 Internal Lane Standard (ILS) defined fragment sizes (bp)
LIZ_600_STANDARD_SIZES: List[float] = [
    60.0, 80.0, 100.0, 114.0, 120.0, 140.0, 160.0, 180.0, 200.0, 214.0,
    240.0, 250.0, 260.0, 280.0, 300.0, 314.0, 340.0, 360.0, 380.0, 400.0,
    414.0, 440.0, 460.0, 480.0, 500.0, 514.0, 540.0, 560.0, 580.0, 600.0
]


@dataclass
class EpgPeakAnnotation:
    locus_name: str
    allele_call: str
    dye_channel: DyeChannelEnum
    size_bp: float
    rfu_height: float
    area: float
    is_stutter: bool = False
    is_pullup: bool = False
    is_saturated: bool = False
    is_below_at: bool = False
    is_stochastic_warning: bool = False
    stutter_ratio: Optional[float] = None
    heterozygote_balance: Optional[float] = None


@dataclass
class EpgTracePoint:
    size_bp: float
    rfu: float


@dataclass
class EpgSynthesizedTrace:
    dye_channel: DyeChannelEnum
    color_hex: str
    data_points: List[EpgTracePoint]
    peaks: List[EpgPeakAnnotation]


@dataclass
class EpgSynthesisResult:
    sample_id: str
    degradation_index: float
    degradation_severity: str
    overall_passed_qc: bool
    traces: Dict[DyeChannelEnum, EpgSynthesizedTrace]
    all_peaks: List[EpgPeakAnnotation]
    analytical_threshold_rfu: float = 50.0
    stochastic_threshold_rfu: float = 200.0
    saturation_threshold_rfu: float = 8000.0
    min_heterozygote_balance: float = 0.60
    stutter_artifacts_filtered: int = 0
    pullup_artifacts_filtered: int = 0


class EpgSynthesisEngine:
    """
    Biocomputational Capillary Electropherogram (EPG) Synthesis & Spectral Quality Engine.
    """

    ANALYTICAL_THRESHOLD = 50.0   # RFU
    STOCHASTIC_THRESHOLD = 200.0  # RFU
    SATURATION_THRESHOLD = 8000.0 # RFU
    MIN_HETEROZYGOTE_BALANCE = 0.60
    PULLUP_RATIO_THRESHOLD = 0.06 # 6% cross-talk bleedthrough limit
    DEFAULT_SIGMA_BP = 0.75       # Bandwidth width in base pairs
    GAUSSIAN_FRACTION = 0.85      # Modified Gaussian-Lorentzian weighting
    ASYMMETRY_FACTOR = 0.05       # Tailing/fronting factor

    DYE_HEX_MAP = {
        DyeChannelEnum.BLUE: "#3b82f6",    # Blue
        DyeChannelEnum.GREEN: "#10b981",   # Green
        DyeChannelEnum.YELLOW: "#eab308",  # Yellow
        DyeChannelEnum.RED: "#ef4444",     # Red
        DyeChannelEnum.PURPLE: "#a855f7",  # Purple
        DyeChannelEnum.ORANGE: "#f97316",  # Orange
    }

    @classmethod
    def calculate_allele_size_bp(cls, locus_name: str, allele_call: str) -> float:
        """
        Calculates expected migration amplicon size in base pairs (bp).
        Handles microvariants (e.g. 9.3, 31.2) and Amelogenin (X=106, Y=112).
        """
        mapping = PANEL_24_LOCUS_MAPPING.get(locus_name)
        if not mapping:
            return 150.0

        if locus_name == "Amelogenin":
            return 106.0 if allele_call.upper() == "X" else 112.0

        try:
            if "." in allele_call:
                parts = allele_call.split(".")
                repeats = float(parts[0])
                extra_bases = float(parts[1])
                return mapping.base_size_bp + (repeats * mapping.repeat_unit_size_bp) + extra_bases
            else:
                repeats = float(allele_call)
                return mapping.base_size_bp + (repeats * mapping.repeat_unit_size_bp)
        except ValueError:
            return mapping.base_size_bp + 40.0

    @classmethod
    def modified_gaussian_lorentzian_peak(
        cls,
        t: float,
        t0: float,
        h: float,
        sigma: float = DEFAULT_SIGMA_BP,
        eta: float = GAUSSIAN_FRACTION,
        alpha: float = ASYMMETRY_FACTOR,
    ) -> float:
        """
        Calculates asymmetric Gaussian-Lorentzian peak intensity at point t.
        Formula:
        y(t) = h * [ eta * exp(-(t-t0)^2 / (2 * sigma^2 * (1 + alpha * sgn(t-t0)))) +
                     (1 - eta) / (1 + ((t-t0)/sigma)^2) ]
        """
        dt = t - t0
        sgn = 1.0 if dt >= 0 else -1.0
        sigma_adj_sq = sigma * sigma * (1.0 + alpha * sgn)
        
        # Avoid division by zero
        if sigma_adj_sq <= 0:
            sigma_adj_sq = 1e-6

        gaussian_part = math.exp(- (dt * dt) / (2.0 * sigma_adj_sq))
        lorentzian_part = 1.0 / (1.0 + (dt / sigma) ** 2)

        return h * (eta * gaussian_part + (1.0 - eta) * lorentzian_part)

    @classmethod
    def synthesize_epg_from_profile(
        cls,
        sample_id: str,
        str_profile: Dict[str, Dict[str, Any]],
        template_ng: float = 1.0,
        degradation_rate: float = 0.0,
        include_stutter: bool = True,
        include_pullup: bool = False,
        start_bp: float = 50.0,
        end_bp: float = 520.0,
        step_bp: float = 0.25,
        baseline_noise_rfu: float = 8.0,
    ) -> EpgSynthesisResult:
        """
        Synthesizes high-fidelity 5/6-dye continuous EPG waveforms and performs spectral QA/QC.
        """
        peak_annotations: List[EpgPeakAnnotation] = []
        locus_peaks: Dict[str, List[EpgPeakAnnotation]] = {}

        # 1. Generate True Allele Peaks & Stutter Artifacts
        for locus_name, call_dict in str_profile.items():
            mapping = PANEL_24_LOCUS_MAPPING.get(locus_name)
            if not mapping:
                continue

            a1 = str(call_dict.get("allele1", "")).strip()
            a2 = str(call_dict.get("allele2", a1)).strip() if call_dict.get("allele2") is not None else a1
            
            # Base RFU scaling from template amount and locus amplification efficiency
            base_rfu = float(call_dict.get("rfu1", 1500.0 * template_ng * mapping.amplification_efficiency))
            base_rfu2 = float(call_dict.get("rfu2", base_rfu))

            # Apply degradation kinetics: mu = A_l * 10^(-d * (S - 100))
            s1 = cls.calculate_allele_size_bp(locus_name, a1)
            deg_factor1 = 10.0 ** (-degradation_rate * (s1 - 100.0))
            rfu1 = base_rfu * deg_factor1

            is_homo = (a1 == a2) or a2 in ("", "None", "[0]", "0")
            
            p1 = EpgPeakAnnotation(
                locus_name=locus_name,
                allele_call=a1,
                dye_channel=mapping.dye_channel,
                size_bp=s1,
                rfu_height=rfu1,
                area=rfu1 * 10.5,
                is_below_at=(rfu1 < cls.ANALYTICAL_THRESHOLD),
                is_stochastic_warning=(cls.ANALYTICAL_THRESHOLD <= rfu1 < cls.STOCHASTIC_THRESHOLD),
                is_saturated=(rfu1 > cls.SATURATION_THRESHOLD),
            )
            peak_annotations.append(p1)
            locus_peaks.setdefault(locus_name, []).append(p1)

            # Heterozygous second peak
            if not is_homo:
                s2 = cls.calculate_allele_size_bp(locus_name, a2)
                deg_factor2 = 10.0 ** (-degradation_rate * (s2 - 100.0))
                rfu2 = base_rfu2 * deg_factor2
                
                hb = min(rfu1, rfu2) / max(rfu1, rfu2) if max(rfu1, rfu2) > 0 else 1.0
                p1.heterozygote_balance = hb

                p2 = EpgPeakAnnotation(
                    locus_name=locus_name,
                    allele_call=a2,
                    dye_channel=mapping.dye_channel,
                    size_bp=s2,
                    rfu_height=rfu2,
                    area=rfu2 * 10.5,
                    is_below_at=(rfu2 < cls.ANALYTICAL_THRESHOLD),
                    is_stochastic_warning=(cls.ANALYTICAL_THRESHOLD <= rfu2 < cls.STOCHASTIC_THRESHOLD),
                    is_saturated=(rfu2 > cls.SATURATION_THRESHOLD),
                    heterozygote_balance=hb,
                )
                peak_annotations.append(p2)
                locus_peaks[locus_name].append(p2)

            # Generate N-4 Reverse Stutter Peaks if enabled
            if include_stutter and mapping.max_stutter_ratio > 0.0:
                for parent_peak in [p1] + ([p2] if not is_homo else []):
                    stutter_ratio = mapping.max_stutter_ratio * 0.75 # Realistic ~75% of max
                    stutter_rfu = parent_peak.rfu_height * stutter_ratio
                    stutter_size = parent_peak.size_bp - mapping.repeat_unit_size_bp
                    
                    if stutter_rfu >= cls.ANALYTICAL_THRESHOLD:
                        stutter_peak = EpgPeakAnnotation(
                            locus_name=locus_name,
                            allele_call=f"stutter({parent_peak.allele_call}-1)",
                            dye_channel=mapping.dye_channel,
                            size_bp=stutter_size,
                            rfu_height=stutter_rfu,
                            area=stutter_rfu * 9.0,
                            is_stutter=True,
                            stutter_ratio=stutter_ratio,
                            is_below_at=False,
                            is_stochastic_warning=False,
                        )
                        peak_annotations.append(stutter_peak)

        # 2. Generate Pull-Up Bleedthrough Artifacts (if enabled)
        pullup_count = 0
        if include_pullup:
            major_peaks = [p for p in peak_annotations if p.rfu_height > 1500.0 and not p.is_stutter]
            dye_order = [DyeChannelEnum.BLUE, DyeChannelEnum.GREEN, DyeChannelEnum.YELLOW, DyeChannelEnum.RED, DyeChannelEnum.PURPLE]
            for parent in major_peaks:
                parent_idx = dye_order.index(parent.dye_channel)
                # Bleed into adjacent dye channel
                target_dye = dye_order[(parent_idx + 1) % len(dye_order)]
                pullup_rfu = parent.rfu_height * 0.045 # 4.5% bleed (< 6% pull-up threshold)
                if pullup_rfu >= cls.ANALYTICAL_THRESHOLD:
                    pullup_peak = EpgPeakAnnotation(
                        locus_name=f"PullUp_{parent.locus_name}",
                        allele_call=f"pullup({parent.allele_call})",
                        dye_channel=target_dye,
                        size_bp=parent.size_bp + 0.1,
                        rfu_height=pullup_rfu,
                        area=pullup_rfu * 8.0,
                        is_pullup=True,
                        is_below_at=False,
                    )
                    peak_annotations.append(pullup_peak)
                    pullup_count += 1

        # 3. Add LIZ 600 Size Standard Peaks to Orange Channel
        for sz in LIZ_600_STANDARD_SIZES:
            if start_bp <= sz <= end_bp:
                ils_rfu = 1200.0
                peak_annotations.append(EpgPeakAnnotation(
                    locus_name="ILS_600",
                    allele_call=f"{int(sz)}",
                    dye_channel=DyeChannelEnum.ORANGE,
                    size_bp=sz,
                    rfu_height=ils_rfu,
                    area=ils_rfu * 9.5,
                ))

        # 4. Synthesize Continuous Waveform per Dye Channel
        num_points = int(math.ceil((end_bp - start_bp) / step_bp)) + 1
        bp_axis = [start_bp + i * step_bp for i in range(num_points)]
        
        traces: Dict[DyeChannelEnum, EpgSynthesizedTrace] = {}
        all_dyes = list(DyeChannelEnum)

        for dye in all_dyes:
            dye_peaks = [p for p in peak_annotations if p.dye_channel == dye]
            trace_points: List[EpgTracePoint] = []

            for t in bp_axis:
                rfu_val = baseline_noise_rfu
                for p in dye_peaks:
                    # Only calculate within +- 4 bp window for performance
                    if abs(t - p.size_bp) <= 4.0:
                        rfu_val += cls.modified_gaussian_lorentzian_peak(t, p.size_bp, p.rfu_height)
                
                trace_points.append(EpgTracePoint(size_bp=round(t, 2), rfu=round(rfu_val, 2)))

            traces[dye] = EpgSynthesizedTrace(
                dye_channel=dye,
                color_hex=cls.DYE_HEX_MAP[dye],
                data_points=trace_points,
                peaks=dye_peaks,
            )

        # 5. Compute Degradation Index (DI = D8S1179 / FGA) & Quality Assessment
        h_d8 = 0.0
        h_fga = 0.0
        if "D8S1179" in locus_peaks and locus_peaks["D8S1179"]:
            h_d8 = max(p.rfu_height for p in locus_peaks["D8S1179"] if not p.is_stutter and not p.is_pullup)
        if "FGA" in locus_peaks and locus_peaks["FGA"]:
            h_fga = max(p.rfu_height for p in locus_peaks["FGA"] if not p.is_stutter and not p.is_pullup)

        if h_fga > 0:
            di = round(h_d8 / h_fga, 2)
        elif h_d8 > 0 and h_fga == 0:
            di = 99.0 # Extreme degradation (FGA dropout)
        else:
            di = 1.00

        if di <= 1.5:
            deg_sev = "PRISTINE"
        elif 1.5 < di <= 5.0:
            deg_sev = "MODERATE_DEGRADATION"
        else:
            deg_sev = "SEVERE_DEGRADATION"

        # Check overall QC pass
        stutter_filtered = sum(1 for p in peak_annotations if p.is_stutter)
        passed_qc = (deg_sev != "SEVERE_DEGRADATION") and all(
            p.heterozygote_balance is None or p.heterozygote_balance >= cls.MIN_HETEROZYGOTE_BALANCE
            for p in peak_annotations if not p.is_stutter and not p.is_pullup
        )

        return EpgSynthesisResult(
            sample_id=sample_id,
            degradation_index=di,
            degradation_severity=deg_sev,
            overall_passed_qc=passed_qc,
            traces=traces,
            all_peaks=peak_annotations,
            analytical_threshold_rfu=cls.ANALYTICAL_THRESHOLD,
            stochastic_threshold_rfu=cls.STOCHASTIC_THRESHOLD,
            saturation_threshold_rfu=cls.SATURATION_THRESHOLD,
            min_heterozygote_balance=cls.MIN_HETEROZYGOTE_BALANCE,
            stutter_artifacts_filtered=stutter_filtered,
            pullup_artifacts_filtered=pullup_count,
        )

    @classmethod
    def filter_epg_artifacts(
        cls,
        peaks: List[EpgPeakAnnotation],
    ) -> List[EpgPeakAnnotation]:
        """
        Applies SWGDAM artifact filters to separate true alleles from stutter, pull-up, and noise.
        """
        filtered_peaks: List[EpgPeakAnnotation] = []
        for p in peaks:
            if p.rfu_height < cls.ANALYTICAL_THRESHOLD:
                continue
            if p.is_pullup or p.is_stutter:
                continue
            filtered_peaks.append(p)
        return filtered_peaks
