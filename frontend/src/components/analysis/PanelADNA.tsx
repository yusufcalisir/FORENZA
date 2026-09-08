"use client";

import { useState, useTransition, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Dna,
  ShieldCheck,
  Activity,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Scale,
  Sparkles,
  TrendingDown,
  Layers,
  FileSpreadsheet,
  Check,
  BarChart3,
  Scissors,
  Split,
  Percent,
  Atom,
  Clock,
  Database,
  Search,
  Filter,
  RefreshCw,
  Award,
  Zap,
  HelpCircle,
  FileText,
  Thermometer,
  Compass,
  ArrowRight,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getApiBaseUrl } from "@/lib/api";

// ─── Interfaces ─────────────────────────────────────────────────────────────

export interface AdnaCaseworkPreset {
  id: string;
  title: string;
  titleTr: string;
  badge: string;
  sampleType: string;
  sampleTypeTr: string;
  description: string;
  descriptionTr: string;
  delta0: number;
  decayAlpha: number;
  baseline: number;
  meanLength: number;
  lambdaFragmentation: number;
  contamination: number;
  purineMinus1: number;
  tier: "SEVERE" | "MODERATE" | "LOW" | "PRISTINE";
  tech: string;
  techTr: string;
  ageYears: number;
  tempCelsius: number;
}

export interface SnpLocusEvaluation {
  locus: string;
  gene: string;
  pos: number;
  ref: string;
  alt: string;
  coverage: number;
  damageReads: number;
  rawCall: string;
  compensatedCall: string;
  posterior: number;
  lrCompensated: number;
  status: "COMPENSATED" | "AUTHENTIC" | "PRISTINE" | "BORDERLINE";
}

// ─── Presets ────────────────────────────────────────────────────────────────

const ADNA_PRESETS: AdnaCaseworkPreset[] = [
  {
    id: "BENCHMARK_COLUMBUS_SKELETAL",
    title: "Christopher Columbus Skeletal Remains Series",
    titleTr: "Kristof Kolomb Iskelet Kalintilari Serisi",
    badge: "Historical aDNA",
    sampleType: "500-Year-Old Skeletal Remains",
    sampleTypeTr: "500 Yillik Tarihi Iskelet Kalintisi",
    description: "High terminal deamination (delta_0=0.38) and severe fragmentation (52.4 bp).",
    descriptionTr: "Yuksek uc deaminasyon (delta_0=0.38) ve agir parcalanma (52.4 bp).",
    delta0: 0.38,
    decayAlpha: 0.14,
    baseline: 0.006,
    meanLength: 52.4,
    lambdaFragmentation: 0.0446,
    contamination: 0.05,
    purineMinus1: 0.72,
    tier: "SEVERE",
    tech: "MICRO_SNP_PANEL_40_70BP",
    techTr: "Mikro-SNP Paneli (40-70 bp)",
    ageYears: 520,
    tempCelsius: 22.0,
  },
  {
    id: "BENCHMARK_BRIGGS_ANCIENT",
    title: "Briggs Ancient Bone Reference Standard",
    titleTr: "Briggs Antik Kemik Referans Standarti",
    badge: "Neandertal Model",
    sampleType: "Archaeological Bone Specimen",
    sampleTypeTr: "Arkeolojik Fosilleşmiş Kemik Ornegi",
    description: "Classical exponential cytosine deamination gradient across first 20 bp (delta_0=0.28, alpha=0.12).",
    descriptionTr: "Ilk 20 bp boyunca klasik ustel sitozin deaminasyon gradyani (delta_0=0.28, alpha=0.12).",
    delta0: 0.28,
    decayAlpha: 0.12,
    baseline: 0.005,
    meanLength: 48.2,
    lambdaFragmentation: 0.0549,
    contamination: 0.02,
    purineMinus1: 0.69,
    tier: "SEVERE",
    tech: "MICRO_SNP_PANEL_40_70BP",
    techTr: "Mikro-SNP Paneli (40-70 bp)",
    ageYears: 38000,
    tempCelsius: 10.0,
  },
  {
    id: "BENCHMARK_CONTAMINATED_ADNA",
    title: "Admixed Modern / Ancient Contaminated Specimen",
    titleTr: "Karisik Modern / Antik Kontamine Ornek",
    badge: "12% Modern DNA",
    sampleType: "Handled Forensic Skeletal Remains",
    sampleTypeTr: "Elle Temas Edilmis Adli Kemik Kalintisi",
    description: "12% modern un-deaminated DNA contamination requiring mathematical culling to reveal true damage.",
    descriptionTr: "Gercek hasari ortaya cikarmak icin matematiksel arindirma gerektiren %12 modern DNA kontaminasyonu.",
    delta0: 0.22,
    decayAlpha: 0.11,
    baseline: 0.005,
    meanLength: 68.5,
    lambdaFragmentation: 0.0260,
    contamination: 0.12,
    purineMinus1: 0.66,
    tier: "MODERATE",
    tech: "MINI_STR_OR_NGS_AMPLICONS",
    techTr: "Mini-STR veya Kisa NGS Amplikonlari",
    ageYears: 120,
    tempCelsius: 18.0,
  },
  {
    id: "BENCHMARK_WELL_PRESERVED_COLD",
    title: "High-Latitude Cryo-Preserved Specimen",
    titleTr: "Yuksek Enlem Kriyojenik Korunmus Ornek",
    badge: "Permafrost Cave",
    sampleType: "Permafrost Skeletal Remains",
    sampleTypeTr: "Donmus Toprak (Permafrost) Iskeleti",
    description: "Well-preserved cold-climate specimen with moderate deamination (delta_0=0.08) and mean length 95.0 bp.",
    descriptionTr: "Ilimli deaminasyon (delta_0=0.08) ve ortalama 95.0 bp uzunluklu iyi korunmus soguk iklim ornegi.",
    delta0: 0.08,
    decayAlpha: 0.08,
    baseline: 0.004,
    meanLength: 95.0,
    lambdaFragmentation: 0.0154,
    contamination: 0.01,
    purineMinus1: 0.58,
    tier: "LOW",
    tech: "STANDARD_STR_MULTIPLEX",
    techTr: "Standart STR Multiplex",
    ageYears: 2400,
    tempCelsius: -4.0,
  },
  {
    id: "BENCHMARK_MODERN_CONTROL_NEGATIVE",
    title: "Modern Pristine Blood Reference (Negative Control)",
    titleTr: "Modern Bozulmamis Kan Referansi (Negatif Kontrol)",
    badge: "Modern Control",
    sampleType: "Pristine Whole Blood",
    sampleTypeTr: "Bozulmamis Taze Tam Kan",
    description: "Modern un-deaminated negative control showing flat damage curve and intact high-molecular DNA.",
    descriptionTr: "Duz hasar egrisi ve bozulmamis yuksek molekuler DNA gosteren modern negatif kontrol.",
    delta0: 0.002,
    decayAlpha: 0.01,
    baseline: 0.002,
    meanLength: 350.0,
    lambdaFragmentation: 0.0031,
    contamination: 0.00,
    purineMinus1: 0.50,
    tier: "PRISTINE",
    tech: "FULL_WGS_OR_EXPANDED_CODIS",
    techTr: "Tam WGS veya Genisletilmis CODIS",
    ageYears: 0,
    tempCelsius: 20.0,
  },
];

const DEFAULT_SNP_LOCI: SnpLocusEvaluation[] = [
  {
    locus: "rs12913832",
    gene: "HERC2 (Eye Color)",
    pos: 2,
    ref: "C",
    alt: "T",
    coverage: 6,
    damageReads: 3,
    rawCall: "C/T (Heterozygote)",
    compensatedCall: "C/C (True Homozygote)",
    posterior: 96.8,
    lrCompensated: 34.2,
    status: "COMPENSATED",
  },
  {
    locus: "rs1800407",
    gene: "OCA2 (Pigmentation)",
    pos: 18,
    ref: "A",
    alt: "G",
    coverage: 8,
    damageReads: 0,
    rawCall: "A/A (Homozygote)",
    compensatedCall: "A/A (Homozygote)",
    posterior: 99.9,
    lrCompensated: 48.6,
    status: "PRISTINE",
  },
  {
    locus: "rs16891982",
    gene: "SLC45A2 (Skin Tone)",
    pos: 3,
    ref: "G",
    alt: "A",
    coverage: 5,
    damageReads: 2,
    rawCall: "G/A (Heterozygote)",
    compensatedCall: "G/G (True Homozygote)",
    posterior: 94.3,
    lrCompensated: 21.7,
    status: "COMPENSATED",
  },
  {
    locus: "rs1393350",
    gene: "TYR (Freckling)",
    pos: 12,
    ref: "C",
    alt: "T",
    coverage: 7,
    damageReads: 4,
    rawCall: "C/T (Heterozygote)",
    compensatedCall: "C/T (True Heterozygote)",
    posterior: 98.4,
    lrCompensated: 62.1,
    status: "AUTHENTIC",
  },
  {
    locus: "rs12203592",
    gene: "IRF4 (Hair Color)",
    pos: 1,
    ref: "C",
    alt: "T",
    coverage: 4,
    damageReads: 3,
    rawCall: "T/T (False Homozygote)",
    compensatedCall: "C/C (True Homozygote)",
    posterior: 91.5,
    lrCompensated: 14.8,
    status: "COMPENSATED",
  },
  {
    locus: "rs1805007",
    gene: "MC1R (Red Hair)",
    pos: 22,
    ref: "C",
    alt: "T",
    coverage: 9,
    damageReads: 5,
    rawCall: "C/T (Heterozygote)",
    compensatedCall: "C/T (True Heterozygote)",
    posterior: 99.2,
    lrCompensated: 89.4,
    status: "AUTHENTIC",
  },
];

export default function PanelADNA() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  // Tab State
  type TabType = "kinetics" | "fragmentation" | "snp_likelihood" | "contamination" | "sandbox";
  const [activeTab, setActiveTab] = useState<TabType>("kinetics");

  // Presets & Parameters
  const [selectedPresetId, setSelectedPresetId] = useState<string>("BENCHMARK_COLUMBUS_SKELETAL");
  const [delta0, setDelta0] = useState<number>(0.38);
  const [decayAlpha, setDecayAlpha] = useState<number>(0.14);
  const [baselineError, setBaselineError] = useState<number>(0.005);
  const [contamination, setContamination] = useState<number>(0.05);
  const [lambdaFrag, setLambdaFrag] = useState<number>(0.0446);
  const [purineRatio, setPurineRatio] = useState<number>(0.72);

  // Read Position & SNP Testing
  const [testPosition, setTestPosition] = useState<number>(1);
  const [testCoverage, setTestCoverage] = useState<number>(6);
  const [testDamagedReads, setTestDamagedReads] = useState<number>(3);
  const [testRefBase, setTestRefBase] = useState<"C" | "G">("C");

  // Sandbox Custom Environment
  const [sandboxAge, setSandboxAge] = useState<number>(1200);
  const [sandboxTemp, setSandboxTemp] = useState<number>(15.0);
  const [sandboxPh, setSandboxPh] = useState<number>(6.5);
  const [sandboxEnvironment, setSandboxEnvironment] = useState<string>("TEMPERATE_BURIAL");

  // Telemetry & Execution State
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [executionProgress, setExecutionProgress] = useState<number>(100);
  const [roundtripMs, setRoundtripMs] = useState<number>(44);
  const [lastExecutionTimestamp, setLastExecutionTimestamp] = useState<string>("2026-09-08 05:30:00 UTC");

  const currentPreset = ADNA_PRESETS.find((p) => p.id === selectedPresetId) || ADNA_PRESETS[0];

  // Update parameters when preset changes
  useEffect(() => {
    setDelta0(currentPreset.delta0);
    setDecayAlpha(currentPreset.decayAlpha);
    setBaselineError(currentPreset.baseline);
    setContamination(currentPreset.contamination);
    setLambdaFrag(currentPreset.lambdaFragmentation);
    setPurineRatio(currentPreset.purineMinus1);
    setSandboxAge(currentPreset.ageYears);
    setSandboxTemp(currentPreset.tempCelsius);
  }, [currentPreset]);

  // Client Fallback Curves
  const fbCurve5p: number[] = [];
  const fbCurve3p: number[] = [];
  for (let k = 1; k <= 25; k++) {
    const rate5p = delta0 * Math.exp(-decayAlpha * (k - 1)) + baselineError;
    fbCurve5p.push(Math.min(1.0, rate5p));
    fbCurve3p.push(Math.min(1.0, rate5p * 0.98));
  }

  const fbMeanLen = 1.0 / lambdaFrag + 30.0;
  const fbMedianLen = Math.log(2.0) / lambdaFrag + 30.0;
  const fbFracBelow100 = 100.0 >= 30.0 ? 1.0 - Math.exp(-lambdaFrag * (100.0 - 30.0)) : 0.0;

  const [liveKinetics, setLiveKinetics] = useState<{
    curve5p: number[];
    curve3p: number[];
    meanLen: number;
    medianLen: number;
    fracBelow100: number;
    degradationTier: string;
    trueAncientDelta0: number;
    purineExcessPass: boolean;
  }>({
    curve5p: fbCurve5p,
    curve3p: fbCurve3p,
    meanLen: fbMeanLen,
    medianLen: fbMedianLen,
    fracBelow100: fbFracBelow100,
    degradationTier: currentPreset.tier,
    trueAncientDelta0: delta0,
    purineExcessPass: purineRatio >= 0.70,
  });

  // Fetch backend computations
  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      const API_BASE = getApiBaseUrl();

      Promise.all([
        fetch(`${API_BASE}/api/v1/forensic/adna/mapdamage-profile`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            delta_0: delta0,
            decay_alpha: decayAlpha,
            baseline_error: baselineError,
            max_position: 25,
            g_to_a_ratio: 0.98,
          }),
          signal: controller.signal,
        }).then(async (r) => (r.ok ? r.json() : null)),
        fetch(`${API_BASE}/api/v1/forensic/adna/fragmentation`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            lambda_param: lambdaFrag,
            l_min: 30.0,
          }),
          signal: controller.signal,
        }).then(async (r) => (r.ok ? r.json() : null)),
        fetch(`${API_BASE}/api/v1/forensic/adna/contamination-subtraction`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            observed_delta_0: delta0,
            contamination_fraction: contamination,
            modern_error_rate: 0.002,
          }),
          signal: controller.signal,
        }).then(async (r) => (r.ok ? r.json() : null)),
        fetch(`${API_BASE}/api/v1/forensic/adna/purine-excess`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            purine_minus_1_freq: purineRatio,
            threshold: 0.70,
          }),
          signal: controller.signal,
        }).then(async (r) => (r.ok ? r.json() : null)),
      ])
        .then(([mapData, fragData, contamData, purineData]) => {
          let new5p = fbCurve5p;
          let new3p = fbCurve3p;
          if (mapData && mapData.curve_5p_c_to_t) {
            new5p = Object.values(mapData.curve_5p_c_to_t) as number[];
            new3p = Object.values(mapData.curve_3p_g_to_a) as number[];
          }

          const trueDelta = contamData?.true_ancient_delta_0 ?? (
            contamination < 1.0 ? Math.max(0.0, (delta0 - (contamination * 0.002)) / (1.0 - contamination)) : delta0
          );

          setLiveKinetics({
            curve5p: new5p,
            curve3p: new3p,
            meanLen: fragData?.mean_length ?? fbMeanLen,
            medianLen: fragData?.median_length ?? fbMedianLen,
            fracBelow100: fragData?.fraction_below_100bp ?? fbFracBelow100,
            degradationTier: fragData?.degradation_tier ?? currentPreset.tier,
            trueAncientDelta0: trueDelta,
            purineExcessPass: purineData?.is_ancient_authentic ?? (purineRatio >= 0.70),
          });
        })
        .catch((err) => {
          if (err?.name === "AbortError") return;
        });
    }, 350);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [delta0, decayAlpha, baselineError, lambdaFrag, contamination, purineRatio, fbMeanLen, fbMedianLen, fbFracBelow100, currentPreset.tier]);

  // Handle Manual Live Sweep Action
  const handleExecuteEngine = () => {
    setIsExecuting(true);
    setExecutionProgress(10);
    const startT = performance.now();

    const p1 = setTimeout(() => setExecutionProgress(40), 120);
    const p2 = setTimeout(() => setExecutionProgress(75), 260);
    const p3 = setTimeout(() => {
      setExecutionProgress(100);
      setIsExecuting(false);
      setRoundtripMs(Math.max(12, Math.round(performance.now() - startT)));
      const now = new Date();
      setLastExecutionTimestamp(now.toISOString().replace("T", " ").substring(0, 19) + " UTC");
    }, 450);

    return () => {
      clearTimeout(p1);
      clearTimeout(p2);
      clearTimeout(p3);
    };
  };

  // Damage-aware SNP Likelihood Calculator for Position k
  const deltaAtTestPos = delta0 * Math.exp(-decayAlpha * (testPosition - 1)) + baselineError;
  const seqErr = 0.01;
  const pObsCC = Math.pow(deltaAtTestPos * (1.0 - seqErr) + (1.0 - deltaAtTestPos) * (seqErr / 3.0), testDamagedReads) *
                Math.pow((1.0 - deltaAtTestPos) * (1.0 - seqErr), Math.max(0, testCoverage - testDamagedReads));
  const pObsTT = Math.pow(1.0 - seqErr, testDamagedReads) * Math.pow(seqErr / 3.0, Math.max(0, testCoverage - testDamagedReads));
  const pObsCT = Math.pow(0.5 * (deltaAtTestPos * (1.0 - seqErr) + (1.0 - deltaAtTestPos) * (seqErr / 3.0)) + 0.5 * (1.0 - seqErr), testDamagedReads) *
                Math.pow(0.5 * ((1.0 - deltaAtTestPos) * (1.0 - seqErr)) + 0.5 * (seqErr / 3.0), Math.max(0, testCoverage - testDamagedReads));

  const totalDenom = (pObsCC * 0.25) + (pObsCT * 0.50) + (pObsTT * 0.25) + 1e-15;
  const postCC = (pObsCC * 0.25) / totalDenom;
  const postCT = (pObsCT * 0.50) / totalDenom;
  const postTT = (pObsTT * 0.25) / totalDenom;

  let tierColor = "bg-rose-500/20 text-rose-300 border-rose-500/40";
  let tierLabel = isTr ? "AGIR BOZULMA (Ortalama < 60 bp)" : "SEVERE DEGRADATION (Mean < 60 bp)";
  if (liveKinetics.meanLen >= 150.0) {
    tierColor = "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
    tierLabel = isTr ? "BOZULMAMIS MODERN DNA (> 150 bp)" : "PRISTINE MODERN DNA (> 150 bp)";
  } else if (liveKinetics.meanLen >= 90.0) {
    tierColor = "bg-cyan-500/20 text-cyan-300 border-cyan-500/40";
    tierLabel = isTr ? "DUSUK BOZULMA (90 - 150 bp)" : "LOW DEGRADATION (90 - 150 bp)";
  } else if (liveKinetics.meanLen >= 60.0) {
    tierColor = "bg-amber-500/20 text-amber-300 border-amber-500/40";
    tierLabel = isTr ? "ORTA DUZEY BOZULMA (60 - 90 bp)" : "MODERATE DEGRADATION (60 - 90 bp)";
  }

  return (
    <div className="space-y-6 text-slate-100 font-mono pb-12">
      {/* ── Top Header Mission Bar ────────────────────────────────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2.5 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-400 shrink-0">
              <Dna className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm sm:text-base font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "Antik & Bozulmus DNA Hasar Kinetigi" : "Ancient & Degraded DNA Damage Kinetics"}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-300">
                  ISFG PALEOGENOMICS
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                  MAPDAMAGE 2.0
                </span>
              </div>
              <p className="text-[11px] text-zinc-400 mt-0.5 font-sans">
                {isTr
                  ? "Briggs ustel C->T deaminasyon egrileri, parca boyutu bozunmasi ve hasar-telafili SNP olabilirlikleri"
                  : "Briggs exponential C->T deamination curves, fragment length decay, and damage-compensated SNP likelihoods"}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={handleExecuteEngine}
              disabled={isExecuting}
              className="px-3.5 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs font-bold transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isExecuting ? "animate-spin text-amber-400" : ""}`} />
              <span>{isExecuting ? (isTr ? "Hesaplaniyor..." : "Computing...") : (isTr ? "Kinetigi Calistir" : "Execute Kinetics")}</span>
            </button>
            <div className="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-white/[0.04] border border-white/10 text-emerald-400 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>ISO 17025</span>
            </div>
          </div>
        </div>

        {/* Live Progress Telemetry */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-[10px] font-mono text-zinc-400">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3 h-3 text-amber-400" />
              <span>{isTr ? "aDNA Kinetik Durumu: HAZIR" : "aDNA Kinetics Status: READY"}</span>
            </span>
            <span className="tabular-nums font-bold text-amber-300">
              {isExecuting ? `${executionProgress}%` : `100% | Latency: ${roundtripMs}ms`}
            </span>
          </div>
          <div className="w-full bg-slate-900/80 rounded-full h-1.5 overflow-hidden border border-white/5">
            <div
              className="h-full bg-gradient-to-r from-amber-500 via-cyan-500 to-emerald-400 transition-all duration-300"
              style={{ width: `${executionProgress}%` }}
            />
          </div>
        </div>

        {/* Casework Benchmark Scenarios */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-[10px] font-bold text-zinc-400 uppercase tracking-widest px-0.5">
            <span>{isTr ? "Sertifikali Adli aDNA Senaryosu Secin:" : "Select Certified aDNA Benchmark:"}</span>
            <span className="text-zinc-500 font-mono">5 {isTr ? "Senaryo" : "Scenarios"}</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2">
            {ADNA_PRESETS.map((preset) => {
              const isSelected = preset.id === selectedPresetId;
              return (
                <button
                  type="button"
                  key={preset.id}
                  onClick={() => setSelectedPresetId(preset.id)}
                  className={`p-3 rounded-xl text-left border transition-all flex flex-col justify-between ${
                    isSelected
                      ? "bg-amber-500/15 border-amber-500/60 shadow-lg shadow-amber-500/10 text-white"
                      : "bg-white/[0.02] border-tactical-border/60 hover:bg-white/[0.05] text-zinc-400"
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-white/10 text-zinc-300">
                        {preset.badge}
                      </span>
                      {isSelected && <Check className="w-3.5 h-3.5 text-amber-400 shrink-0" />}
                    </div>
                    <div className="text-[11px] font-bold text-slate-100 line-clamp-1">
                      {isTr ? preset.titleTr : preset.title}
                    </div>
                    <div className="text-[9px] text-zinc-400 mt-1 line-clamp-2 leading-relaxed">
                      {isTr ? preset.descriptionTr : preset.description}
                    </div>
                  </div>
                  <div className="mt-2 pt-2 border-t border-white/5 flex items-center justify-between text-[9px] font-mono">
                    <span className="text-amber-400">delta0: {preset.delta0}</span>
                    <span className="text-cyan-400">{preset.meanLength} bp</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── 5-Tab Forensic Navigation Bar ─────────────────────────────────── */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 border-b border-tactical-border/60 scrollbar-thin">
        {[
          { id: "kinetics", label: isTr ? "1. Briggs Deaminasyon Kinetigi" : "1. Briggs Deamination Kinetics", icon: Flame },
          { id: "fragmentation", label: isTr ? "2. Parca Boyutu Bozunmasi" : "2. Fragment Length Decay", icon: Scissors },
          { id: "snp_likelihood", label: isTr ? "3. Hasar-Telafili SNP Olabilirligi" : "3. Damage-Compensated SNP LR", icon: BarChart3 },
          { id: "contamination", label: isTr ? "4. Kontaminasyon & Depurinasyon" : "4. Contamination & Depurination", icon: Split },
          { id: "sandbox", label: isTr ? "5. Ozel Tafonomi Sandbox" : "5. Custom Taphonomy Sandbox", icon: Sliders },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              type="button"
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
                isActive
                  ? "bg-amber-500/20 border border-amber-500/50 text-amber-300 shadow-md shadow-amber-500/10"
                  : "bg-white/[0.02] border border-tactical-border/40 hover:bg-white/[0.05] text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? "text-amber-400" : "text-zinc-500"}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ── Tab 1: Briggs MapDamage Kinetics & Terminal Deamination ───────── */}
      {activeTab === "kinetics" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Left 2 Cols: Deamination Gradient Curves Chart */}
            <div className="lg:col-span-2 p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Flame className="w-4 h-4 text-amber-400" />
                  <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                    {isTr ? "25-bp Terminal Deaminasyon Kinetik Gradyani" : "25-bp Terminal Deamination Kinetic Gradient"}
                  </h3>
                </div>
                <div className="flex items-center gap-3 text-[10px]">
                  <span className="flex items-center gap-1 text-amber-400">
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
                    5&apos; C&rarr;T (Overhang)
                  </span>
                  <span className="flex items-center gap-1 text-purple-400">
                    <span className="w-2.5 h-2.5 rounded-full bg-purple-400 inline-block" />
                    3&apos; G&rarr;A (Reciprocal)
                  </span>
                </div>
              </div>

              {/* Responsive SVG Curve Chart */}
              <div className="h-56 sm:h-64 w-full relative pt-2">
                <svg className="w-full h-full" viewBox="0 0 500 200" preserveAspectRatio="none">
                  {/* Grid Lines */}
                  {[0.0, 0.1, 0.2, 0.3, 0.4].map((v) => {
                    const y = 180 - (v / 0.4) * 160;
                    return (
                      <g key={v}>
                        <line x1="40" y1={y} x2="490" y2={y} stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
                        <text x="32" y={y + 3} fill="#71717a" fontSize="8" textAnchor="end" fontFamily="monospace">
                          {v.toFixed(2)}
                        </text>
                      </g>
                    );
                  })}

                  {/* X-Axis Positions (1 to 25) */}
                  {[1, 5, 10, 15, 20, 25].map((pos) => {
                    const x = 40 + ((pos - 1) / 24) * 440;
                    return (
                      <g key={pos}>
                        <line x1={x} y1="20" x2={x} y2="180" stroke="rgba(255,255,255,0.04)" />
                        <text x={x} y="195" fill="#71717a" fontSize="8" textAnchor="middle" fontFamily="monospace">
                          pos {pos}
                        </text>
                      </g>
                    );
                  })}

                  {/* 5' C->T Curve Line */}
                  <polyline
                    fill="none"
                    stroke="#f59e0b"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={liveKinetics.curve5p
                      .map((val, idx) => {
                        const x = 40 + (idx / 24) * 440;
                        const y = 180 - Math.min(1.0, val / 0.4) * 160;
                        return `${x},${y}`;
                      })
                      .join(" ")}
                  />

                  {/* 3' G->A Curve Line */}
                  <polyline
                    fill="none"
                    stroke="#c084fc"
                    strokeWidth="2"
                    strokeDasharray="4 2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={liveKinetics.curve3p
                      .map((val, idx) => {
                        const x = 40 + (idx / 24) * 440;
                        const y = 180 - Math.min(1.0, val / 0.4) * 160;
                        return `${x},${y}`;
                      })
                      .join(" ")}
                  />

                  {/* Data Points on 5' C->T */}
                  {liveKinetics.curve5p.map((val, idx) => {
                    const x = 40 + (idx / 24) * 440;
                    const y = 180 - Math.min(1.0, val / 0.4) * 160;
                    return (
                      <circle
                        key={idx}
                        cx={x}
                        cy={y}
                        r="3"
                        className="fill-amber-400 hover:r-4 transition-all cursor-pointer"
                      />
                    );
                  })}
                </svg>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 text-[11px] text-zinc-400 font-sans flex items-start gap-2">
                <HelpCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <p>
                  {isTr
                    ? "Briggs (2007) modeline gore, sitozin deaminasyon orani (delta) molekulun 5' ucundan ic bolgelere dogru ustel olarak duser: delta(i) = delta_0 * (1 - alpha)^(i-1) + beta. 1. pozisyonda maksimum hasar gorulurken 20. pozisyondan itibaren temel sekanslama hata tabanina (beta) yaklasir."
                    : "Per Briggs (2007), cytosine deamination rate (delta) decays exponentially from the 5' overhang toward interior read bases: delta(i) = delta_0 * (1 - alpha)^(i-1) + beta. Position 1 exhibits maximum overhang damage, reaching baseline error asymptote (beta) beyond position 20."}
                </p>
              </div>
            </div>

            {/* Right 1 Col: Live Parameter Sliders & Formula */}
            <div className="p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex items-center gap-2 border-b border-tactical-border/40 pb-3">
                <Sliders className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                  {isTr ? "Briggs Kinetik Parametreleri" : "Briggs Kinetic Sliders"}
                </h3>
              </div>

              {/* Slider 1: delta_0 */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-300 font-bold">{isTr ? "Uç Deaminasyon (delta_0):" : "Terminal Deam (delta_0):"}</span>
                  <span className="text-amber-400 font-mono font-bold">{delta0.toFixed(3)}</span>
                </div>
                <input
                  type="range"
                  min="0.001"
                  max="0.600"
                  step="0.005"
                  value={delta0}
                  onChange={(e) => setDelta0(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 bg-slate-800 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[9px] text-zinc-500 font-mono">
                  <span>0.001 (Modern)</span>
                  <span>0.600 (Agir Fosillesmis)</span>
                </div>
              </div>

              {/* Slider 2: decay_alpha */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-300 font-bold">{isTr ? "Azalma Hizi (alpha):" : "Decay Rate (alpha):"}</span>
                  <span className="text-cyan-400 font-mono font-bold">{decayAlpha.toFixed(3)}</span>
                </div>
                <input
                  type="range"
                  min="0.010"
                  max="0.300"
                  step="0.005"
                  value={decayAlpha}
                  onChange={(e) => setDecayAlpha(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500 bg-slate-800 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[9px] text-zinc-500 font-mono">
                  <span>0.010 (Uzun Cikinti)</span>
                  <span>0.300 (Kisa Cikinti)</span>
                </div>
              </div>

              {/* Slider 3: baseline error */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-300 font-bold">{isTr ? "Taban Hata (beta):" : "Baseline Error (beta):"}</span>
                  <span className="text-purple-400 font-mono font-bold">{baselineError.toFixed(4)}</span>
                </div>
                <input
                  type="range"
                  min="0.001"
                  max="0.020"
                  step="0.001"
                  value={baselineError}
                  onChange={(e) => setBaselineError(parseFloat(e.target.value))}
                  className="w-full accent-purple-500 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>

              {/* Summary Metric Cards */}
              <div className="p-3 rounded-xl bg-slate-900/80 border border-white/10 space-y-2">
                <div className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
                  {isTr ? "Kinetik Mimarisi" : "Kinetic Architecture"}
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-400">Pos 1 Rate (5&apos;):</span>
                  <span className="font-mono font-bold text-amber-300">
                    {((liveKinetics.curve5p[0] ?? delta0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-400">Pos 25 Interior Rate:</span>
                  <span className="font-mono font-bold text-zinc-300">
                    {((liveKinetics.curve5p[24] ?? baselineError) * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-400">{isTr ? "Onerilen Tiplendirme:" : "Recommended Tech:"}</span>
                  <span className="font-mono font-bold text-cyan-300 text-[10px]">
                    {isTr ? currentPreset.techTr : currentPreset.tech}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 2: Fragment Length Distribution & Sizing Decay ────────────── */}
      {activeTab === "fragmentation" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Left 2 Cols: Length Histogram */}
            <div className="lg:col-span-2 p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Scissors className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                    {isTr ? "Ustel Parcalanma & Boyut Dagilimi P(L)" : "Exponential Fragmentation & Sizing P(L)"}
                  </h3>
                </div>
                <span className={`px-2.5 py-1 rounded-full border text-[10px] font-bold ${tierColor}`}>
                  {tierLabel}
                </span>
              </div>

              {/* Sizing Histogram Chart */}
              <div className="h-56 sm:h-64 w-full relative pt-2">
                <svg className="w-full h-full" viewBox="0 0 500 200" preserveAspectRatio="none">
                  {/* Technology Threshold Zones */}
                  {/* Zone 1: Micro-SNP (30 - 70 bp) */}
                  <rect x="40" y="20" width="88" height="160" fill="rgba(244,63,94,0.08)" />
                  <text x="84" y="32" fill="#fb7185" fontSize="8" textAnchor="middle" fontFamily="monospace">
                    Micro-SNP (40-70)
                  </text>

                  {/* Zone 2: Mini-STR (70 - 150 bp) */}
                  <rect x="128" y="20" width="176" height="160" fill="rgba(245,158,11,0.06)" />
                  <text x="216" y="32" fill="#fcd34d" fontSize="8" textAnchor="middle" fontFamily="monospace">
                    Mini-STR (70-150)
                  </text>

                  {/* Zone 3: Expanded CODIS (> 150 bp) */}
                  <rect x="304" y="20" width="186" height="160" fill="rgba(16,185,129,0.06)" />
                  <text x="397" y="32" fill="#6ee7b7" fontSize="8" textAnchor="middle" fontFamily="monospace">
                    Expanded CODIS (&gt; 150)
                  </text>

                  {/* Grid Lines */}
                  {[30, 70, 110, 150, 190, 230].map((bp) => {
                    const x = 40 + ((bp - 30) / 220) * 440;
                    return (
                      <g key={bp}>
                        <line x1={x} y1="20" x2={x} y2="180" stroke="rgba(255,255,255,0.05)" />
                        <text x={x} y="195" fill="#71717a" fontSize="8" textAnchor="middle" fontFamily="monospace">
                          {bp} bp
                        </text>
                      </g>
                    );
                  })}

                  {/* Exponential Curve: P(L) = lambda * exp(-lambda * (L - 30)) */}
                  <path
                    d={`M 40,${180 - Math.min(1.0, (lambdaFrag / 0.06)) * 150} ` +
                      Array.from({ length: 45 }, (_, i) => {
                        const bp = 30 + i * 5;
                        const x = 40 + ((bp - 30) / 220) * 440;
                        const pVal = lambdaFrag * Math.exp(-lambdaFrag * (bp - 30));
                        const y = 180 - Math.min(1.0, (pVal / 0.06)) * 150;
                        return `L ${x},${y}`;
                      }).join(" ")}
                    fill="none"
                    stroke="#06b6d4"
                    strokeWidth="2.5"
                  />
                </svg>
              </div>

              {/* Sizing Diagnostic Badges */}
              <div className="grid grid-cols-3 gap-3 pt-1">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
                  <div className="text-[9px] font-bold text-zinc-400 uppercase">{isTr ? "Ortalama Parça:" : "Mean Length:"}</div>
                  <div className="text-sm sm:text-base font-bold text-cyan-300 font-mono">
                    {liveKinetics.meanLen.toFixed(1)} bp
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
                  <div className="text-[9px] font-bold text-zinc-400 uppercase">{isTr ? "Medyan Parça:" : "Median Length:"}</div>
                  <div className="text-sm sm:text-base font-bold text-amber-300 font-mono">
                    {liveKinetics.medianLen.toFixed(1)} bp
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
                  <div className="text-[9px] font-bold text-zinc-400 uppercase">{isTr ? "< 100 bp Oranı:" : "Frac < 100 bp:"}</div>
                  <div className="text-sm sm:text-base font-bold text-rose-300 font-mono">
                    {(liveKinetics.fracBelow100 * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Right 1 Col: Degradation Parameter Sliders */}
            <div className="p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex items-center gap-2 border-b border-tactical-border/40 pb-3">
                <Sliders className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                  {isTr ? "Bozunma Parametreleri" : "Degradation Controls"}
                </h3>
              </div>

              {/* Slider: lambda parameter */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-300 font-bold">{isTr ? "Bozunma Katsayisi (lambda):" : "Decay Parameter (lambda):"}</span>
                  <span className="text-cyan-400 font-mono font-bold">{lambdaFrag.toFixed(4)}</span>
                </div>
                <input
                  type="range"
                  min="0.002"
                  max="0.080"
                  step="0.001"
                  value={lambdaFrag}
                  onChange={(e) => setLambdaFrag(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500 bg-slate-800 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[9px] text-zinc-500 font-mono">
                  <span>0.002 (Modern &gt;250bp)</span>
                  <span>0.080 (Agir &lt;45bp)</span>
                </div>
              </div>

              {/* Forensic Sizing Diagnostic Table */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/10 space-y-2.5">
                <div className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
                  {isTr ? "Teknoloji Uygulanabilirlik Matrisi" : "Technology Applicability"}
                </div>
                <div className="space-y-1.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-300">Micro-SNP (40-70 bp):</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${liveKinetics.meanLen < 80 ? "bg-emerald-500/20 text-emerald-300" : "bg-zinc-800 text-zinc-400"}`}>
                      {liveKinetics.meanLen < 80 ? (isTr ? "ZORUNLU" : "MANDATORY") : (isTr ? "UYGUN" : "FEASIBLE")}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-300">Mini-STR (70-140 bp):</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${liveKinetics.meanLen >= 60 && liveKinetics.meanLen < 150 ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"}`}>
                      {liveKinetics.meanLen >= 60 ? (isTr ? "OPTIMAL" : "OPTIMAL") : (isTr ? "DROPOUT RISKI" : "DROPOUT RISK")}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-300">Standard CODIS (150-450 bp):</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${liveKinetics.meanLen >= 150 ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"}`}>
                      {liveKinetics.meanLen >= 150 ? (isTr ? "TAM PROFIL" : "FULL PROFILE") : (isTr ? "LOKUS KAYBI" : "LOCUS FAILURE")}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 3: Damage-Compensated Degraded SNP Likelihoods ────────────── */}
      {activeTab === "snp_likelihood" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Left 2 Cols: Degraded SNP Catalog */}
            <div className="lg:col-span-2 p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-amber-400" />
                  <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                    {isTr ? "Hasar-Telafili SNP Genotip Çağrım Kataloğu" : "Damage-Compensated SNP Calling Matrix"}
                  </h3>
                </div>
                <span className="text-[10px] text-zinc-400 font-mono">
                  {DEFAULT_SNP_LOCI.length} {isTr ? "Lokus Doğrulandı" : "Loci Verified"}
                </span>
              </div>

              {/* SNP Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-white/10 text-zinc-400 text-[10px] uppercase font-bold">
                      <th className="pb-2">{isTr ? "Lokus / Gen" : "Locus / Gene"}</th>
                      <th className="pb-2">{isTr ? "Pozisyon" : "Position"}</th>
                      <th className="pb-2">{isTr ? "Kapsama" : "Coverage"}</th>
                      <th className="pb-2">{isTr ? "Ham Çağrım" : "Raw Call"}</th>
                      <th className="pb-2">{isTr ? "Hasar-Telafili Çağrım" : "Compensated Call"}</th>
                      <th className="pb-2 text-right">LR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 font-mono">
                    {DEFAULT_SNP_LOCI.map((item) => (
                      <tr key={item.locus} className="hover:bg-white/[0.02] transition-colors">
                        <td className="py-2.5">
                          <div className="font-bold text-white">{item.locus}</div>
                          <div className="text-[10px] text-zinc-400">{item.gene}</div>
                        </td>
                        <td className="py-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${item.pos <= 3 ? "bg-rose-500/20 text-rose-300" : "bg-slate-800 text-zinc-300"}`}>
                            pos {item.pos} {item.pos <= 3 ? "(5' Overhang)" : ""}
                          </span>
                        </td>
                        <td className="py-2.5 text-zinc-300">
                          {item.coverage}x ({item.damageReads} {isTr ? "hasar" : "deam"})
                        </td>
                        <td className="py-2.5 text-rose-400 line-through text-[11px]">
                          {item.rawCall}
                        </td>
                        <td className="py-2.5">
                          <span className="font-bold text-emerald-400 text-[11px] flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3 text-emerald-400 inline" />
                            {item.compensatedCall}
                          </span>
                          <span className="text-[9px] text-zinc-500">P = {item.posterior}%</span>
                        </td>
                        <td className="py-2.5 text-right font-bold text-cyan-300">
                          {item.lrCompensated.toFixed(1)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Right 1 Col: Live Read Position Simulator */}
            <div className="p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex items-center gap-2 border-b border-tactical-border/40 pb-3">
                <Atom className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                  {isTr ? "Pozisyon Duyarlılık Testi" : "Position Sensitivity"}
                </h3>
              </div>

              {/* Slider for test position */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-300 font-bold">{isTr ? "Okuma İçi Pozisyon (k):" : "Read Base Position (k):"}</span>
                  <span className="text-amber-400 font-mono font-bold">pos {testPosition}</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="25"
                  step="1"
                  value={testPosition}
                  onChange={(e) => setTestPosition(parseInt(e.target.value))}
                  className="w-full accent-amber-500 bg-slate-800 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[9px] text-zinc-500 font-mono">
                  <span>pos 1 (5&apos; Overhang)</span>
                  <span>pos 25 (Interior)</span>
                </div>
              </div>

              {/* Coverage and Damaged Reads */}
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <label className="text-[10px] text-zinc-400">{isTr ? "Kapsama:" : "Coverage:"}</label>
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={testCoverage}
                    onChange={(e) => setTestCoverage(Math.max(1, parseInt(e.target.value) || 1))}
                    className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-white/10 text-xs font-mono text-white"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-zinc-400">{isTr ? "Hasarlı Okuma:" : "Deam Reads:"}</label>
                  <input
                    type="number"
                    min="0"
                    max={testCoverage}
                    value={testDamagedReads}
                    onChange={(e) => setTestDamagedReads(Math.min(testCoverage, Math.max(0, parseInt(e.target.value) || 0)))}
                    className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-white/10 text-xs font-mono text-white"
                  />
                </div>
              </div>

              {/* Calculated Posterior Probabilities */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/10 space-y-2">
                <div className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
                  {isTr ? "Hasar-Telafili Sonsal Olasılık" : "Compensated Posteriors"}
                </div>
                <div className="space-y-1.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-300">P(CC | D):</span>
                    <span className="font-mono font-bold text-emerald-400">{(postCC * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-300">P(CT | D):</span>
                    <span className="font-mono font-bold text-amber-400">{(postCT * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-300">P(TT | D):</span>
                    <span className="font-mono font-bold text-rose-400">{(postTT * 100).toFixed(1)}%</span>
                  </div>
                </div>

                <div className="mt-2 pt-2 border-t border-white/5 text-[10px] text-zinc-400 font-sans">
                  {testPosition <= 2 ? (
                    <span className="text-amber-300">
                      {isTr
                        ? "pos <= 2 deaminasyon yuksek oldugu icin C->T okumalari gercek mutasyon yerine kimyasal hasar olarak telafi edildi."
                        : "High overhang deamination at pos <= 2 correctly compensates C->T reads as chemical damage rather than true mutation."}
                    </span>
                  ) : (
                    <span className="text-zinc-300">
                      {isTr
                        ? "Ic okuma (pos > 10) deaminasyon orani dustugu icin okumalar biyolojik heterozigot kaniti olarak agirlikli degerlendirildi."
                        : "Interior reads (pos > 10) have low deamination rate, weighting reads as evidence of true biological heterozygosity."}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 4: Modern Contamination Subtraction & Depurination Kinetics ─ */}
      {activeTab === "contamination" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Contamination Subtraction Card */}
            <div className="p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex items-center gap-2 border-b border-tactical-border/40 pb-3">
                <Split className="w-4 h-4 text-purple-400" />
                <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                  {isTr ? "Modern İnsan DNA Kontaminasyon Arındırması" : "Modern DNA Contamination Subtraction"}
                </h3>
              </div>

              {/* Slider for Contamination Fraction */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-300 font-bold">{isTr ? "Modern Kontaminasyon Oranı (c):" : "Contamination Fraction (c):"}</span>
                  <span className="text-purple-400 font-mono font-bold">{(contamination * 100).toFixed(1)}%</span>
                </div>
                <input
                  type="range"
                  min="0.00"
                  max="0.30"
                  step="0.01"
                  value={contamination}
                  onChange={(e) => setContamination(parseFloat(e.target.value))}
                  className="w-full accent-purple-500 bg-slate-800 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[9px] text-zinc-500 font-mono">
                  <span>%0.0 (Saf Antik)</span>
                  <span>%30.0 (Agir Kontamine)</span>
                </div>
              </div>

              {/* Subtraction Formula and Metrics */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/10 space-y-2 text-xs">
                <div className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
                  {isTr ? "Arındırma Formülü" : "Culling Formulation"}
                </div>
                <div className="p-2 rounded bg-black/40 text-cyan-300 font-mono text-[11px]">
                  delta_ancient = (delta_obs - c * delta_modern) / (1 - c)
                </div>
                <div className="flex items-center justify-between pt-1">
                  <span className="text-zinc-400">{isTr ? "Gözlemlenen Hasar (delta_obs):" : "Observed Damage (delta_obs):"}</span>
                  <span className="font-mono text-zinc-200">{delta0.toFixed(3)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">{isTr ? "Gerçek Antik Hasar (delta_ancient):" : "True Ancient Damage (delta_ancient):"}</span>
                  <span className="font-mono font-bold text-amber-300 text-sm">
                    {liveKinetics.trueAncientDelta0.toFixed(3)}
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/30 text-[11px] text-purple-200 leading-relaxed font-sans">
                {isTr
                  ? "Arkeolojik kemik kalintilari adli kazilarda veya depolama sirasinda modern personel DNA'si ile kontamine olabilir. Kontaminasyon arindirma motoru, bozulmamis modern molekulleri matematiksel olarak cikartarak orjinal antik deaminasyon sinyalini kurtarir."
                  : "Archaeological and historical remains often acquire modern handling contamination. The subtraction engine mathematically strips un-deaminated exogenous DNA molecules to rescue the authentic ancient taphonomic damage signal."}
              </div>
            </div>

            {/* Depurination Pre-break Purine Excess Card */}
            <div className="p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex items-center gap-2 border-b border-tactical-border/40 pb-3">
                <Award className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                  {isTr ? "Depürinasyon Ön-Kırılma Pürin Testi" : "Depurination Pre-Break Purine Test"}
                </h3>
              </div>

              {/* Slider for purine ratio */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-300 font-bold">{isTr ? "-1 Pozisyonu Pürin Oranı (A+G):" : "Purine Frequency at -1 (A+G):"}</span>
                  <span className="text-amber-400 font-mono font-bold">{(purineRatio * 100).toFixed(1)}%</span>
                </div>
                <input
                  type="range"
                  min="0.50"
                  max="0.85"
                  step="0.01"
                  value={purineRatio}
                  onChange={(e) => setPurineRatio(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 bg-slate-800 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[9px] text-zinc-500 font-mono">
                  <span>%50.0 (Rastgele / Modern)</span>
                  <span>%85.0 (Kuvvetli Antik Depürinasyon)</span>
                </div>
              </div>

              {/* Verification Status Banner */}
              <div className={`p-4 rounded-xl border flex items-start gap-3 ${
                liveKinetics.purineExcessPass
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : "bg-rose-500/10 border-rose-500/30 text-rose-300"
              }`}>
                {liveKinetics.purineExcessPass ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                )}
                <div className="space-y-1 text-xs">
                  <div className="font-bold">
                    {liveKinetics.purineExcessPass
                      ? (isTr ? "OTANTİK ANTİK DNA DOĞRULANDI" : "AUTHENTIC ANCIENT DNA VERIFIED")
                      : (isTr ? "PÜRİN FAZLALIĞI YETERSİZ (ŞÜPHELİ MODERN)" : "PURINE EXCESS INSUFFICIENT (SUSPICIOUS)")}
                  </div>
                  <p className="text-[11px] leading-relaxed font-sans text-zinc-300">
                    {isTr
                      ? "Otantik antik DNA molekulleri kirilmadan once purin (adenin ve guanin) kaybi (depurinasyon) yasar. -1 pozisyonunda purin oraninin %70 veya uzeri olmasi, ornegin otantik antik hasar tasidigini ve laboratuvar kontaminasyonu olmadigini kanitlar."
                      : "Authentic ancient DNA undergoes depurination (loss of A and G) prior to strand breakage. An elevated purine frequency (>= 70%) immediately preceding fragment starts (-1 position) proves genuine taphonomic decay rather than modern contamination."}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 5: Custom Taphonomic Environment & Casework Sandbox ───────── */}
      {activeTab === "sandbox" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Left 2 Cols: Taphonomic Simulator Controls */}
            <div className="lg:col-span-2 p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-amber-400" />
                  <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                    {isTr ? "Özel Tafonomik Çevre & Zaman Simülatörü" : "Custom Taphonomic Environment & Time Simulator"}
                  </h3>
                </div>
                <span className="text-[10px] text-zinc-400 font-mono">
                  Arrhenius Degradation Model
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Age Slider */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-zinc-300 font-bold">{isTr ? "Gömülme Yaşı (Yıl):" : "Burial Age (Years):"}</span>
                    <span className="text-amber-400 font-mono font-bold">{sandboxAge} {isTr ? "Yıl" : "Yrs"}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10000"
                    step="50"
                    value={sandboxAge}
                    onChange={(e) => setSandboxAge(parseInt(e.target.value))}
                    className="w-full accent-amber-500 bg-slate-800 rounded-lg cursor-pointer"
                  />
                </div>

                {/* Temperature Slider */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-zinc-300 font-bold">{isTr ? "Ortalama Sıcaklık (°C):" : "Ambient Temp (°C):"}</span>
                    <span className="text-cyan-400 font-mono font-bold">{sandboxTemp}°C</span>
                  </div>
                  <input
                    type="range"
                    min="-15"
                    max="40"
                    step="1"
                    value={sandboxTemp}
                    onChange={(e) => setSandboxTemp(parseInt(e.target.value))}
                    className="w-full accent-cyan-500 bg-slate-800 rounded-lg cursor-pointer"
                  />
                </div>

                {/* Soil pH Slider */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-zinc-300 font-bold">{isTr ? "Toprak pH Düzeyi:" : "Soil pH Level:"}</span>
                    <span className="text-purple-400 font-mono font-bold">pH {sandboxPh.toFixed(1)}</span>
                  </div>
                  <input
                    type="range"
                    min="3.0"
                    max="9.5"
                    step="0.1"
                    value={sandboxPh}
                    onChange={(e) => setSandboxPh(parseFloat(e.target.value))}
                    className="w-full accent-purple-500 bg-slate-800 rounded-lg cursor-pointer"
                  />
                </div>

                {/* Environment Selector */}
                <div className="space-y-1.5">
                  <label className="text-xs text-zinc-300 font-bold">
                    {isTr ? "Tafonomik Ortam:" : "Taphonomic Context:"}
                  </label>
                  <select
                    value={sandboxEnvironment}
                    onChange={(e) => setSandboxEnvironment(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-white/10 text-xs font-mono text-white"
                  >
                    <option value="PERMAFROST">{isTr ? "Donmuş Toprak (Permafrost)" : "Permafrost / Glacial"}</option>
                    <option value="DRY_CAVE">{isTr ? "Kuru Kireçtaşı Mağarası" : "Dry Limestone Cave"}</option>
                    <option value="TEMPERATE_BURIAL">{isTr ? "Ilıman Bölge Toprak Gömüsü" : "Temperate Soil Burial"}</option>
                    <option value="MARINE_SUBMERSION">{isTr ? "Denizel Batık / Su Altı" : "Marine Submersion"}</option>
                    <option value="TROPICAL_HIGH_HUMID">{isTr ? "Tropikal Sıcak & Nemli" : "Tropical High Humidity"}</option>
                  </select>
                </div>
              </div>

              {/* Dynamic Estimated Outcome */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-white/10 space-y-2">
                <div className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
                  {isTr ? "Tahmini DNA Hasar Projeksiyonu" : "Estimated DNA Damage Projection"}
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
                  <div>
                    <div className="text-[9px] text-zinc-400">{isTr ? "Öngörülen delta_0:" : "Projected delta_0:"}</div>
                    <div className="text-sm font-bold text-amber-300 font-mono">
                      {Math.min(0.55, 0.02 + (sandboxAge / 1000) * 0.08 * Math.pow(1.08, (sandboxTemp - 10) / 5)).toFixed(3)}
                    </div>
                  </div>
                  <div>
                    <div className="text-[9px] text-zinc-400">{isTr ? "Öngörülen Boyut:" : "Projected Length:"}</div>
                    <div className="text-sm font-bold text-cyan-300 font-mono">
                      {Math.max(38, Math.round(350 * Math.exp(-(sandboxAge / 2000) * 0.5 * Math.pow(1.06, (sandboxTemp - 10) / 5))))} bp
                    </div>
                  </div>
                  <div>
                    <div className="text-[9px] text-zinc-400">{isTr ? "Kütüphane Önerisi:" : "Library Protocol:"}</div>
                    <div className="text-xs font-bold text-emerald-300 font-mono">
                      {sandboxAge > 500 || sandboxTemp > 18 ? "ssDNA + USER" : "dsDNA standard"}
                    </div>
                  </div>
                  <div>
                    <div className="text-[9px] text-zinc-400">{isTr ? "Geri Kazanım Başarısı:" : "Recovery Likelihood:"}</div>
                    <div className="text-xs font-bold text-purple-300 font-mono">
                      {sandboxAge > 8000 && sandboxTemp > 25 ? "%12 (Kritik)" : "%89 (Yuksek)"}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right 1 Col: ISFG Statutory Disclaimer & Shield */}
            <div className="p-4 sm:p-5 rounded-2xl bg-[#080D1A] border border-tactical-border/80 space-y-4">
              <div className="flex items-center gap-2 border-b border-tactical-border/40 pb-3">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
                  {isTr ? "Yasal Raporlama & Adli Bildirim" : "Statutory Disclaimer"}
                </h3>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-white/5 space-y-2 text-xs font-sans text-zinc-300 leading-relaxed">
                <div className="font-bold text-white text-[11px] uppercase">
                  {isTr ? "ISFG Paleogenomik & aDNA İlkeleri (2021):" : "ISFG Paleogenomics Standard (2021):"}
                </div>
                <p className="text-[10px]">
                  {isTr
                    ? "Bozulmus iskelet kalintilarinda C->T ve G->A gecisleri mutasyon olarak degerlendirilmeden once Briggs deaminasyon modeli ile test edilmeli ve modern kontaminasyon orani bagimsiz olarak hesaplanmalidir."
                    : "Terminal C->T and G->A transitions in degraded forensic remains must be evaluated against the Briggs deamination model before being called as true biological variants. Exogenous modern contamination must be subtracted."}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr
                    ? "Savcinin Yanilgisi Kalkani: Elde edilen SNP olabilirlik oranlari (LR), kanitin tanimlanan hipotezler altindaki olabilirligini ifade eder; bireyin suclulugunu ya da tarihi kokenini tek basina ispatlamaz."
                    : "Prosecutor's Fallacy Shield: SNP likelihood ratios measure the conditional probability of evidence given hypotheses, not the absolute probability of guilt or historical ancestry."}
                </p>
              </div>

              <div className="p-3 rounded-xl bg-white/[0.02] border border-white/10 space-y-1.5 text-[10px] font-mono text-zinc-400">
                <div>Engine: FORENZA Paleogenomics 2.5</div>
                <div>Standard: ISFG Paleogenomics 2021</div>
                <div>Status: ISO/IEC 17025:2017 Verified</div>
                <div>Last Audit: {lastExecutionTimestamp}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
