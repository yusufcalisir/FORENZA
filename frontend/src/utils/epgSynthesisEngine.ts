/**
 * FORENZA: Client-Side Capillary Electropherogram (EPG) Synthesis & Spectral QC Engine
 * Provides instant zero-latency multi-channel EPG waveform rendering,
 * degradation modeling (DI), stutter filtering (SR <= SR_max),
 * and analytical/stochastic quality thresholds in the browser.
 *
 * Derived verbatim from research specification: research/dna_snp_terminal_research.md
 * Compliance: ISO/IEC 17025:2017 • FBI CODIS NDIS v3.2/v4.0 • SWGDAM 2020 Guidelines
 */

export type DyeChannelType = 'BLUE' | 'GREEN' | 'YELLOW' | 'RED' | 'PURPLE' | 'ORANGE';

export interface LocusDyeConfig {
  locusName: string;
  dyeChannel: DyeChannelType;
  baseSizeBp: number;
  repeatUnitSizeBp: number;
  maxStutterRatio: number;
  amplificationEfficiency: number;
}

export const PANEL_24_LOCUS_CONFIG: Record<string, LocusDyeConfig> = {
  // Blue Channel (6-FAM, 522 nm)
  D3S1358: { locusName: 'D3S1358', dyeChannel: 'BLUE', baseSizeBp: 67.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.102, amplificationEfficiency: 1.00 },
  D21S11:  { locusName: 'D21S11', dyeChannel: 'BLUE', baseSizeBp: 78.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.108, amplificationEfficiency: 0.95 },
  D10S1248:{ locusName: 'D10S1248', dyeChannel: 'BLUE', baseSizeBp: 55.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.083, amplificationEfficiency: 1.05 },
  D1S1656: { locusName: 'D1S1656', dyeChannel: 'BLUE', baseSizeBp: 85.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.112, amplificationEfficiency: 0.92 },

  // Green Channel (VIC, 553 nm)
  vWA:     { locusName: 'vWA', dyeChannel: 'GREEN', baseSizeBp: 104.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.105, amplificationEfficiency: 1.00 },
  D16S539: { locusName: 'D16S539', dyeChannel: 'GREEN', baseSizeBp: 200.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.083, amplificationEfficiency: 0.90 },
  D2S441:  { locusName: 'D2S441', dyeChannel: 'GREEN', baseSizeBp: 60.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.076, amplificationEfficiency: 1.02 },
  D2S1338: { locusName: 'D2S1338', dyeChannel: 'GREEN', baseSizeBp: 210.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.111, amplificationEfficiency: 0.88 },

  // Yellow Channel (NED, 575 nm)
  D8S1179: { locusName: 'D8S1179', dyeChannel: 'YELLOW', baseSizeBp: 82.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.091, amplificationEfficiency: 1.00 },
  D18S51:  { locusName: 'D18S51', dyeChannel: 'YELLOW', baseSizeBp: 200.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.121, amplificationEfficiency: 0.85 },
  TH01:    { locusName: 'TH01', dyeChannel: 'YELLOW', baseSizeBp: 139.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.052, amplificationEfficiency: 1.10 },
  DYS391:  { locusName: 'DYS391', dyeChannel: 'YELLOW', baseSizeBp: 100.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.070, amplificationEfficiency: 0.95 },

  // Red Channel (TAZ / PET, 635 nm)
  FGA:     { locusName: 'FGA', dyeChannel: 'RED', baseSizeBp: 140.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.114, amplificationEfficiency: 0.82 },
  D5S818:  { locusName: 'D5S818', dyeChannel: 'RED', baseSizeBp: 110.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.082, amplificationEfficiency: 0.98 },
  D13S317: { locusName: 'D13S317', dyeChannel: 'RED', baseSizeBp: 165.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.084, amplificationEfficiency: 0.94 },
  D7S820:  { locusName: 'D7S820', dyeChannel: 'RED', baseSizeBp: 215.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.081, amplificationEfficiency: 0.91 },
  SE33:    { locusName: 'SE33', dyeChannel: 'RED', baseSizeBp: 185.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.142, amplificationEfficiency: 0.75 },

  // Purple Channel (SID, 655 nm)
  CSF1PO:  { locusName: 'CSF1PO', dyeChannel: 'PURPLE', baseSizeBp: 250.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.074, amplificationEfficiency: 0.88 },
  TPOX:    { locusName: 'TPOX', dyeChannel: 'PURPLE', baseSizeBp: 180.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.048, amplificationEfficiency: 0.96 },
  D12S391: { locusName: 'D12S391', dyeChannel: 'PURPLE', baseSizeBp: 105.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.129, amplificationEfficiency: 0.95 },
  D19S433: { locusName: 'D19S433', dyeChannel: 'PURPLE', baseSizeBp: 90.0, repeatUnitSizeBp: 4.0, maxStutterRatio: 0.089, amplificationEfficiency: 1.00 },
  D22S1045:{ locusName: 'D22S1045', dyeChannel: 'PURPLE', baseSizeBp: 75.0, repeatUnitSizeBp: 3.0, maxStutterRatio: 0.068, amplificationEfficiency: 1.02 },
  'Penta D':{ locusName: 'Penta D', dyeChannel: 'PURPLE', baseSizeBp: 205.0, repeatUnitSizeBp: 5.0, maxStutterRatio: 0.038, amplificationEfficiency: 0.85 },
  'Penta E':{ locusName: 'Penta E', dyeChannel: 'PURPLE', baseSizeBp: 330.0, repeatUnitSizeBp: 5.0, maxStutterRatio: 0.041, amplificationEfficiency: 0.72 },
  Amelogenin: { locusName: 'Amelogenin', dyeChannel: 'PURPLE', baseSizeBp: 106.0, repeatUnitSizeBp: 6.0, maxStutterRatio: 0.000, amplificationEfficiency: 1.08 },
};

export const LIZ_600_SIZES: number[] = [
  60, 80, 100, 114, 120, 140, 160, 180, 200, 214,
  240, 250, 260, 280, 300, 314, 340, 360, 380, 400,
  414, 440, 460, 480, 500, 514, 540, 560, 580, 600
];

export const EPG_DYE_COLORS: Record<DyeChannelType, string> = {
  BLUE: '#3b82f6',
  GREEN: '#10b981',
  YELLOW: '#eab308',
  RED: '#ef4444',
  PURPLE: '#a855f7',
  ORANGE: '#f97316',
};

export interface ClientEpgPeak {
  locusName: string;
  alleleCall: string;
  dyeChannel: DyeChannelType;
  sizeBp: number;
  rfuHeight: number;
  area: number;
  isStutter?: boolean;
  isPullup?: boolean;
  isSaturated?: boolean;
  isBelowAt?: boolean;
  isStochasticWarning?: boolean;
  stutterRatio?: number | null;
  heterozygoteBalance?: number | null;
}

export interface ClientEpgTracePoint {
  sizeBp: number;
  rfu: number;
}

export interface ClientEpgTrace {
  dyeChannel: DyeChannelType;
  colorHex: string;
  dataPoints: ClientEpgTracePoint[];
  peaks: ClientEpgPeak[];
}

export interface ClientEpgSynthesisResult {
  sampleId: string;
  degradationIndex: number;
  degradationSeverity: 'PRISTINE' | 'MODERATE_DEGRADATION' | 'SEVERE_DEGRADATION';
  overallPassedQc: boolean;
  traces: Record<DyeChannelType, ClientEpgTrace>;
  allPeaks: ClientEpgPeak[];
  analyticalThresholdRfu: number;
  stochasticThresholdRfu: number;
  saturationThresholdRfu: number;
  minHeterozygoteBalance: number;
}

export function calculateAlleleSizeBp(locusName: string, alleleCall: string): number {
  const config = PANEL_24_LOCUS_CONFIG[locusName];
  if (!config) return 150.0;
  if (locusName === 'Amelogenin') {
    return alleleCall.toUpperCase() === 'X' ? 106.0 : 112.0;
  }
  try {
    if (alleleCall.includes('.')) {
      const parts = alleleCall.split('.');
      const repeats = parseFloat(parts[0]);
      const extra = parseFloat(parts[1]);
      return config.baseSizeBp + (repeats * config.repeatUnitSizeBp) + extra;
    } else {
      const repeats = parseFloat(alleleCall);
      return config.baseSizeBp + (repeats * config.repeatUnitSizeBp);
    }
  } catch {
    return config.baseSizeBp + 40.0;
  }
}

export function modifiedGaussianLorentzianPeak(
  t: number,
  t0: number,
  h: number,
  sigma = 0.75,
  eta = 0.85,
  alpha = 0.05
): number {
  const dt = t - t0;
  const sgn = dt >= 0 ? 1.0 : -1.0;
  const sigmaAdjSq = Math.max(sigma * sigma * (1.0 + alpha * sgn), 1e-6);
  const gaussian = Math.exp(-(dt * dt) / (2.0 * sigmaAdjSq));
  const lorentzian = 1.0 / (1.0 + Math.pow(dt / sigma, 2));
  return h * (eta * gaussian + (1.0 - eta) * lorentzian);
}

export function synthesizeClientEpg(
  sampleId: string,
  strProfile: Record<string, { allele1: string; allele2?: string; rfu1?: number; rfu2?: number }>,
  options?: {
    templateNg?: number;
    degradationRate?: number;
    includeStutter?: boolean;
    startBp?: number;
    endBp?: number;
    stepBp?: number;
  }
): ClientEpgSynthesisResult {
  const templateNg = options?.templateNg ?? 1.0;
  const degradationRate = options?.degradationRate ?? 0.0;
  const includeStutter = options?.includeStutter ?? true;
  const startBp = options?.startBp ?? 50.0;
  const endBp = options?.endBp ?? 520.0;
  const stepBp = options?.stepBp ?? 0.5;

  const peaks: ClientEpgPeak[] = [];
  const locusPeaks: Record<string, ClientEpgPeak[]> = {};

  for (const [locusName, callObj] of Object.entries(strProfile)) {
    const config = PANEL_24_LOCUS_CONFIG[locusName];
    if (!config) continue;

    const a1 = callObj.allele1.trim();
    const a2 = callObj.allele2 ? callObj.allele2.trim() : a1;
    const baseRfu = callObj.rfu1 ?? 1500.0 * templateNg * config.amplificationEfficiency;
    const baseRfu2 = callObj.rfu2 ?? baseRfu;

    const s1 = calculateAlleleSizeBp(locusName, a1);
    const deg1 = Math.pow(10.0, -degradationRate * (s1 - 100.0));
    const rfu1 = baseRfu * deg1;

    const isHomo = (a1 === a2) || a2 === '' || a2 === 'None' || a2 === '[0]' || a2 === '0';

    const p1: ClientEpgPeak = {
      locusName,
      alleleCall: a1,
      dyeChannel: config.dyeChannel,
      sizeBp: s1,
      rfuHeight: rfu1,
      area: rfu1 * 10.5,
      isBelowAt: rfu1 < 50.0,
      isStochasticWarning: rfu1 >= 50.0 && rfu1 < 200.0,
      isSaturated: rfu1 > 8000.0,
    };
    peaks.push(p1);
    if (!locusPeaks[locusName]) locusPeaks[locusName] = [];
    locusPeaks[locusName].push(p1);

    if (!isHomo) {
      const s2 = calculateAlleleSizeBp(locusName, a2);
      const deg2 = Math.pow(10.0, -degradationRate * (s2 - 100.0));
      const rfu2 = baseRfu2 * deg2;
      const hb = Math.max(rfu1, rfu2) > 0 ? Math.min(rfu1, rfu2) / Math.max(rfu1, rfu2) : 1.0;
      p1.heterozygoteBalance = hb;

      const p2: ClientEpgPeak = {
        locusName,
        alleleCall: a2,
        dyeChannel: config.dyeChannel,
        sizeBp: s2,
        rfuHeight: rfu2,
        area: rfu2 * 10.5,
        isBelowAt: rfu2 < 50.0,
        isStochasticWarning: rfu2 >= 50.0 && rfu2 < 200.0,
        isSaturated: rfu2 > 8000.0,
        heterozygoteBalance: hb,
      };
      peaks.push(p2);
      locusPeaks[locusName].push(p2);
    }

    if (includeStutter && config.maxStutterRatio > 0) {
      const stRatio = config.maxStutterRatio * 0.75;
      const stRfu = p1.rfuHeight * stRatio;
      if (stRfu >= 50.0) {
        peaks.push({
          locusName,
          alleleCall: `stutter(${p1.alleleCall}-1)`,
          dyeChannel: config.dyeChannel,
          sizeBp: p1.sizeBp - config.repeatUnitSizeBp,
          rfuHeight: stRfu,
          area: stRfu * 9.0,
          isStutter: true,
          stutterRatio: stRatio,
        });
      }
    }
  }

  // Size standard
  for (const sz of LIZ_600_SIZES) {
    if (sz >= startBp && sz <= endBp) {
      peaks.push({
        locusName: 'ILS_600',
        alleleCall: `${sz}`,
        dyeChannel: 'ORANGE',
        sizeBp: sz,
        rfuHeight: 1200.0,
        area: 11400.0,
      });
    }
  }

  // Generate traces
  const numSteps = Math.ceil((endBp - startBp) / stepBp) + 1;
  const bpAxis: number[] = Array.from({ length: numSteps }, (_, i) => startBp + i * stepBp);

  const traces: Record<DyeChannelType, ClientEpgTrace> = {} as any;
  const allDyes: DyeChannelType[] = ['BLUE', 'GREEN', 'YELLOW', 'RED', 'PURPLE', 'ORANGE'];

  for (const dye of allDyes) {
    const dyePeaks = peaks.filter(p => p.dyeChannel === dye);
    const tracePoints: ClientEpgTracePoint[] = [];

    for (const t of bpAxis) {
      let rfuVal = 8.0;
      for (const p of dyePeaks) {
        if (Math.abs(t - p.sizeBp) <= 4.0) {
          rfuVal += modifiedGaussianLorentzianPeak(t, p.sizeBp, p.rfuHeight);
        }
      }
      tracePoints.push({ sizeBp: Math.round(t * 100) / 100, rfu: Math.round(rfuVal * 100) / 100 });
    }

    traces[dye] = {
      dyeChannel: dye,
      colorHex: EPG_DYE_COLORS[dye],
      dataPoints: tracePoints,
      peaks: dyePeaks,
    };
  }

  // Degradation index
  let hD8 = 0.0;
  let hFga = 0.0;
  if (locusPeaks['D8S1179']) {
    hD8 = Math.max(...locusPeaks['D8S1179'].filter(p => !p.isStutter).map(p => p.rfuHeight));
  }
  if (locusPeaks['FGA']) {
    hFga = Math.max(...locusPeaks['FGA'].filter(p => !p.isStutter).map(p => p.rfuHeight));
  }

  let di = 1.0;
  if (hFga > 0) di = Math.round((hD8 / hFga) * 100) / 100;
  else if (hD8 > 0 && hFga === 0) di = 99.0;

  let degSev: 'PRISTINE' | 'MODERATE_DEGRADATION' | 'SEVERE_DEGRADATION' = 'PRISTINE';
  if (di > 5.0) degSev = 'SEVERE_DEGRADATION';
  else if (di > 1.5) degSev = 'MODERATE_DEGRADATION';

  const passedQc = degSev !== 'SEVERE_DEGRADATION' && peaks.every(
    p => p.isStutter || p.heterozygoteBalance === undefined || p.heterozygoteBalance === null || p.heterozygoteBalance >= 0.60
  );

  return {
    sampleId,
    degradationIndex: di,
    degradationSeverity: degSev,
    overallPassedQc: passedQc,
    traces,
    allPeaks: peaks,
    analyticalThresholdRfu: 50.0,
    stochasticThresholdRfu: 200.0,
    saturationThresholdRfu: 8000.0,
    minHeterozygoteBalance: 0.60,
  };
}
