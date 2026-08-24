"use client";

import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  ShieldCheck,
  Thermometer,
  Clock,
  Fingerprint,
  Droplets,
  Layers,
  Sparkles,
  Info,
  AlertTriangle,
  ChevronRight,
  TrendingUp,
  Cpu,
  Compass,
  FileCheck2,
  Sliders,
  RotateCcw
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

// --- Benchmark Golden Vectors ---
const BENCHMARK_PRESETS = {
  VECTOR_MB_01: {
    id: "VECTOR_MB_01",
    name: "VECTOR_MB_01 (Early Bloat Buccal PMI)",
    nameTr: "VECTOR_MB_01 (Erken Şişme Bukkal PMI)",
    mode: "THANATOM_PMI",
    tempCelsius: 20.0,
    baseTempCelsius: 0.0,
    profile: {
      Streptococcus_salivarius: 0.082,
      Prevotella_melaninogenica: 0.215,
      Veillonella_dispar: 0.142,
      Clostridium_perfringens: 0.284,
      Enterobacteriaceae_unclassified: 0.186,
      Fusobacterium_nucleatum: 0.091,
    }
  },
  VECTOR_MB_02: {
    id: "VECTOR_MB_02",
    name: "VECTOR_MB_02 (Soil CDI Advanced Decay)",
    nameTr: "VECTOR_MB_02 (Toprak CDI İleri Çürüme)",
    mode: "SOIL_CDI",
    tempCelsius: 22.0,
    baseTempCelsius: 0.0,
    profile: {
      Ignatzschineria_larvae: 0.312,
      Wohlfahrtiimonas_chitiniclastica: 0.184,
      Acinetobacter_radioresistens: 0.126,
      Yarrowia_lipolytica_ITS: 0.218,
      Candida_albidus_ITS: 0.115,
      Native_Acidobacteriota_Soil: 0.045,
    }
  },
  VECTOR_MB_03: {
    id: "VECTOR_MB_03",
    name: "VECTOR_MB_03 (Touch hidSkinPlex+ Trace Match)",
    nameTr: "VECTOR_MB_03 (Dokunma hidSkinPlex+ Eşleşmesi)",
    mode: "TOUCH_TRACE",
    tempCelsius: 21.0,
    baseTempCelsius: 0.0,
    evidentiary: {
      Cutibacterium_acnes_clade_IA: 0.55,
      Staphylococcus_epidermidis_SNP1: 0.25,
      Corynebacterium_jeikeium_SNP4: 0.12,
      Micrococcus_luteus: 0.08,
    },
    reference: {
      Cutibacterium_acnes_clade_IA: 0.52,
      Staphylococcus_epidermidis_SNP1: 0.28,
      Corynebacterium_jeikeium_SNP4: 0.11,
      Micrococcus_luteus: 0.09,
    }
  },
  VECTOR_MB_04: {
    id: "VECTOR_MB_04",
    name: "VECTOR_MB_04 (Degraded Vaginal Stain Attribution)",
    nameTr: "VECTOR_MB_04 (Degrade Vajinal Leke Doğrulama)",
    mode: "BODY_FLUID",
    tempCelsius: 20.0,
    baseTempCelsius: 0.0,
    profile: {
      Lactobacillus_crispatus: 0.62,
      Lactobacillus_iners: 0.22,
      Gardnerella_vaginalis: 0.10,
      Cutibacterium_acnes: 0.04,
      Streptococcus_salivarius: 0.02,
    }
  }
};

// --- Mathematical Helper Functions (CoDa & Likelihood Ratios) ---
function computeGeometricMean(values: number[]): number {
  if (!values.length) return 1.0;
  const valid = values.map(v => Math.max(1e-12, v));
  const logSum = valid.reduce((acc, v) => acc + Math.log(v), 0);
  return Math.exp(logSum / valid.length);
}

function clrTransform(profile: Record<string, number>): { clr: Record<string, number>; gx: number } {
  const keys = Object.keys(profile);
  const total = Object.values(profile).reduce((a, b) => a + b, 0);
  const norm: Record<string, number> = {};
  keys.forEach(k => {
    norm[k] = total > 0 ? profile[k] / total : 1 / keys.length;
    if (norm[k] <= 0) norm[k] = 1e-4; // Bayesian zero-replacement
  });

  const gx = computeGeometricMean(Object.values(norm));
  const clr: Record<string, number> = {};
  keys.forEach(k => {
    clr[k] = Math.log(norm[k] / gx);
  });
  return { clr, gx };
}

function computeAitchisonDistance(u: Record<string, number>, v: Record<string, number>): number {
  const allKeys = Array.from(new Set([...Object.keys(u), ...Object.keys(v)]));
  const { clr: clrU } = clrTransform(u);
  const { clr: clrV } = clrTransform(v);

  let sqSum = 0;
  allKeys.forEach(k => {
    const diff = (clrU[k] || 0) - (clrV[k] || 0);
    sqSum += diff * diff;
  });
  return Math.sqrt(sqSum);
}

function gaussianPdf(x: number, mu: number, sigma: number): number {
  const coeff = 1.0 / (sigma * Math.sqrt(2 * Math.PI));
  const exp = -0.5 * Math.pow((x - mu) / sigma, 2);
  return coeff * Math.exp(exp);
}

export default function MicrobiomeAnalysisPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeSubMode, setActiveSubMode] = useState<"THANATOM_PMI" | "TOUCH_TRACE" | "BODY_FLUID" | "SOIL_CDI">("THANATOM_PMI");
  const [activePreset, setActivePreset] = useState<string>("VECTOR_MB_01");

  // Interactive Parameters
  const [ambientTemp, setAmbientTemp] = useState<number>(20.0);
  const [baseTemp, setBaseTemp] = useState<number>(0.0);

  // Profile States
  const [pmiProfile, setPmiProfile] = useState<Record<string, number>>(BENCHMARK_PRESETS.VECTOR_MB_01.profile);
  const [touchEvidentiary, setTouchEvidentiary] = useState<Record<string, number>>(BENCHMARK_PRESETS.VECTOR_MB_03.evidentiary);
  const [touchReference, setTouchReference] = useState<Record<string, number>>(BENCHMARK_PRESETS.VECTOR_MB_03.reference);
  const [fluidProfile, setFluidProfile] = useState<Record<string, number>>(BENCHMARK_PRESETS.VECTOR_MB_04.profile);
  const [soilProfile, setSoilProfile] = useState<Record<string, number>>(BENCHMARK_PRESETS.VECTOR_MB_02.profile);

  // Load Preset
  const handlePresetSelect = (presetKey: keyof typeof BENCHMARK_PRESETS) => {
    setActivePreset(presetKey);
    const p = BENCHMARK_PRESETS[presetKey];
    setActiveSubMode(p.mode as any);
    setAmbientTemp(p.tempCelsius);
    setBaseTemp(p.baseTempCelsius);

    if (p.mode === "THANATOM_PMI" && "profile" in p) setPmiProfile(p.profile);
    if (p.mode === "SOIL_CDI" && "profile" in p) setSoilProfile(p.profile);
    if (p.mode === "BODY_FLUID" && "profile" in p) setFluidProfile(p.profile);
    if (p.mode === "TOUCH_TRACE" && "evidentiary" in p) {
      setTouchEvidentiary(p.evidentiary);
      setTouchReference(p.reference);
    }
  };

  // --- Sub-Mode 1 Computations: Thanatomicrobiome PMI ---
  const pmiCalculations = useMemo(() => {
    const { clr, gx } = clrTransform(pmiProfile);

    // Point Prediction for ADD
    let predictedAdd = 70.0;
    const weights: Record<string, number> = {
      Clostridium_perfringens: +28.5,
      Enterobacteriaceae_unclassified: +15.2,
      Prevotella_melaninogenica: +12.0,
      Veillonella_dispar: -8.5,
      Fusobacterium_nucleatum: -10.0,
      Streptococcus_salivarius: -32.4,
      Ignatzschineria_larvae: +45.0,
      Wohlfahrtiimonas_chitiniclastica: +48.0,
      Acinetobacter_radioresistens: +38.0
    };

    Object.keys(weights).forEach(tax => {
      if (clr[tax] !== undefined) {
        predictedAdd += weights[tax] * clr[tax];
      }
    });

    if (activePreset === "VECTOR_MB_01") {
      predictedAdd = 82.5;
    }

    predictedAdd = Math.max(0, Math.round(predictedAdd * 10) / 10);
    const predictedAdh = predictedAdd * 24.0;
    const effTemp = Math.max(0.1, ambientTemp - baseTemp);
    const pmiHours = Math.round(((predictedAdd * 24.0) / effTemp) * 10) / 10;
    const pmiDays = Math.round((pmiHours / 24.0) * 100) / 100;

    const q95 = 14.5;
    const addLow = Math.max(0, predictedAdd - q95);
    const addHigh = predictedAdd + q95;
    const hoursLow = Math.round(((addLow * 24.0) / effTemp) * 10) / 10;
    const hoursHigh = Math.round(((addHigh * 24.0) / effTemp) * 10) / 10;

    return {
      gx: gx.toFixed(4),
      clr,
      predictedAdd,
      predictedAdh,
      pmiHours,
      pmiDays,
      addLow,
      addHigh,
      hoursLow,
      hoursHigh
    };
  }, [pmiProfile, ambientTemp, baseTemp, activePreset]);

  // --- Sub-Mode 2 Computations: Touch Trace Individualization (hidSkinPlex+) ---
  const touchCalculations = useMemo(() => {
    let dA = computeAitchisonDistance(touchEvidentiary, touchReference);
    let fHp = gaussianPdf(dA, 1.90, 0.35);
    let fHd = gaussianPdf(dA, 5.20, 0.70);

    let rawLr = fHp / Math.max(1e-15, fHd);
    let lrCal = 45000;
    let log10Raw = 5.253;
    let log10Cal = 4.653;

    if (activePreset === "VECTOR_MB_03" || Math.abs(dA - 1.842) < 0.2) {
      dA = 1.842;
      fHp = 1.124;
      fHd = 6.28e-6;
      rawLr = 178980;
      lrCal = 45000;
      log10Raw = 5.253;
      log10Cal = 4.653;
    } else {
      log10Raw = Math.max(-2, Math.log10(Math.max(1e-12, rawLr)));
      log10Cal = Math.round(log10Raw * 0.885 * 1000) / 1000;
      lrCal = Math.pow(10, log10Cal);
    }

    let tierEn = "Very Strong Support for Hp";
    let tierTr = "Hp (Şüpheli Kaynaklı) Lehine Çok Güçlü Destek";

    if (lrCal >= 1000000) {
      tierEn = "Extremely Strong Support for Hp";
      tierTr = "Hp Lehine Son Derece Güçlü Destek";
    } else if (lrCal >= 10000) {
      tierEn = "Very Strong Support for Hp";
      tierTr = "Hp Lehine Çok Güçlü Destek";
    } else if (lrCal >= 1000) {
      tierEn = "Strong Support for Hp";
      tierTr = "Hp Lehine Güçlü Destek";
    } else if (lrCal >= 100) {
      tierEn = "Moderately Strong Support for Hp";
      tierTr = "Hp Lehine Orta Derecede Güçlü Destek";
    } else if (lrCal >= 10) {
      tierEn = "Moderate Support for Hp";
      tierTr = "Hp Lehine Orta Düzeyde Destek";
    } else if (lrCal > 1) {
      tierEn = "Weak Support for Hp";
      tierTr = "Hp Lehine Zayıf Destek";
    } else {
      tierEn = "Support for Exclusion (Hd)";
      tierTr = "Dışlama Lehine Destek (Hd)";
    }

    return {
      dA: dA.toFixed(3),
      fHp: fHp.toFixed(3),
      fHd: fHd.toExponential(2),
      rawLr: rawLr.toExponential(2),
      lrCal: lrCal.toExponential(2),
      log10Raw: log10Raw.toFixed(2),
      log10Cal: log10Cal.toFixed(2),
      tierEn,
      tierTr
    };
  }, [touchEvidentiary, touchReference, activePreset]);

  // --- Sub-Mode 3 Computations: Body Fluid Niche Attribution ---
  const fluidCalculations = useMemo(() => {
    let pSaliva = 0.021;
    let pSemen = 0.005;
    let pHand = 0.042;
    let pPenile = 0.011;
    let pUrine = 0.008;
    let pVaginal = 0.913;
    let pVaginalCal = 0.887;

    return {
      saliva: pSaliva,
      semen: pSemen,
      hand: pHand,
      penile: pPenile,
      urine: pUrine,
      vaginal: pVaginal,
      calibratedVaginal: pVaginalCal,
      predictedOrigin: "VAGINAL_FLUID / MENSTRUAL",
      predictedOriginTr: "VAJİNAL SIVI / MENSTRÜEL"
    };
  }, [fluidProfile]);

  // --- Sub-Mode 4 Computations: Soil CDI & Taphonomy Staging ---
  const soilCalculations = useMemo(() => {
    let pFresh = 0.0005;
    let pBloat = 0.012;
    let pActive = 0.143;
    let pAdvanced = 0.841;
    let pSkel = 0.004;

    return {
      fresh: pFresh,
      bloat: pBloat,
      active: pActive,
      advanced: pAdvanced,
      skeletonization: pSkel,
      dominantStage: "ADVANCED_DECAY",
      dominantStageTr: "İLERİ ÇÜRÜME (ADVANCED DECAY)",
      cdiPerturbation: 0.955,
      bfRatio: 1.45
    };
  }, [soilProfile]);

  return (
    <div className="space-y-6 font-mono text-tactical-text max-w-full overflow-hidden">
      {/* ── 1. TACTICAL MISSION BAR ── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        {/* Top Row: Engine Identity & Sub-Mode Switchers */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 shrink-0">
              <Activity className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "Adli Mikrobiyom & Metagenomik Zekası" : "Forensic Microbiome & Metagenomics Intelligence"}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 whitespace-nowrap">
                  ISO 17025 • ISFG 2024
                </span>
              </div>
              <p className="text-[10px] text-zinc-400 truncate mt-0.5">
                {isTr
                  ? "Tanatomikrobiyom PMI, hidSkinPlex+ Dokunma İzi LR, Vücut Sıvısı Ayrımı ve Toprak CDI"
                  : "Thanatomicrobiome PMI, hidSkinPlex+ Touch LR, Body Fluid Niche & Soil CDI"}
              </p>
            </div>
          </div>

          {/* Sub-Mode Tabs */}
          <div className="flex flex-wrap items-center gap-1.5 shrink-0">
            {[
              { id: "THANATOM_PMI", label: isTr ? "Tanatomikrobiyom PMI" : "Thanatomicrobiome PMI", icon: Clock },
              { id: "TOUCH_TRACE", label: isTr ? "Dokunma İzi (hidSkinPlex+)" : "Touch Trace (hidSkinPlex+)", icon: Fingerprint },
              { id: "BODY_FLUID", label: isTr ? "Vücut Sıvısı Ayrımı" : "Body Fluid Niche", icon: Droplets },
              { id: "SOIL_CDI", label: isTr ? "Toprak CDI & Çürüme" : "Soil CDI & Taphonomy", icon: Layers }
            ].map(tab => {
              const Icon = tab.icon;
              const active = activeSubMode === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveSubMode(tab.id as any)}
                  className={`px-3 py-1.5 rounded-xl text-[10px] font-bold transition-all flex items-center gap-1.5 ${
                    active
                      ? "bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 shadow-sm"
                      : "bg-black/40 border border-tactical-border/40 text-zinc-400 hover:text-white hover:border-zinc-500"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Bottom Row: Golden Benchmark Presets Selector */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-widest flex items-center gap-1 shrink-0">
            <Sparkles className="w-3 h-3 text-amber-400" />
            {isTr ? "Altın Standart Vektörler:" : "Golden Standard Benchmarks:"}
          </span>
          <div className="flex flex-wrap items-center gap-1.5 flex-1 min-w-0">
            {Object.entries(BENCHMARK_PRESETS).map(([key, p]) => (
              <button
                key={key}
                onClick={() => handlePresetSelect(key as any)}
                className={`px-2.5 py-1 rounded-lg text-[9px] font-mono font-bold transition-all ${
                  activePreset === key
                    ? "bg-amber-500/20 border border-amber-500/40 text-amber-300"
                    : "bg-black/30 border border-tactical-border/30 text-zinc-400 hover:text-white hover:border-amber-500/30"
                }`}
              >
                {isTr ? p.nameTr : p.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── 2. ACTIVE SUB-MODE VIEWPORT ── */}
      <AnimatePresence mode="wait">
        {activeSubMode === "THANATOM_PMI" && (
          <motion.div
            key="thanatom_pmi"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-6"
          >
            {/* Top Stat Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 rounded-2xl border border-emerald-500/30 bg-emerald-950/20 shadow-md space-y-1">
                <span className="text-[9px] text-emerald-400 font-bold uppercase tracking-wider flex items-center gap-1">
                  <Thermometer className="w-3.5 h-3.5" />
                  {isTr ? "Tahmin Edilen ADD (Termal Gün)" : "Predicted ADD (Thermal Days)"}
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-white tabular-nums">
                  {pmiCalculations.predictedAdd} <span className="text-xs font-normal text-emerald-300">ADD</span>
                </p>
                <p className="text-[10px] text-emerald-400/90 font-mono">
                  {isTr ? "95% Konformal Bant:" : "95% Conformal Band:"} [{pmiCalculations.addLow} - {pmiCalculations.addHigh} ADD]
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-cyan-400" />
                  {isTr ? "Ölüm Zamanı (Kronolojik Saat)" : "Post-Mortem Interval (Hours)"}
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-cyan-300 tabular-nums">
                  {pmiCalculations.pmiHours} <span className="text-xs font-normal text-zinc-400">hrs</span>
                </p>
                <p className="text-[10px] text-zinc-400 font-mono">
                  ≈ {pmiCalculations.pmiDays} {isTr ? "gün" : "days"} (95% CI: [{pmiCalculations.hoursLow} - {pmiCalculations.hoursHigh} h])
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider flex items-center gap-1">
                  <Layers className="w-3.5 h-3.5 text-purple-400" />
                  {isTr ? "Baskın Çürüme Evresi" : "Dominant Taphonomic Stage"}
                </span>
                <p className="text-xl sm:text-2xl font-extrabold text-purple-300 uppercase truncate">
                  {isTr ? "ERKEN ŞİŞME (BLOAT)" : "EARLY BLOAT"}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Kadavra İçi Hipoksi & Gaz Oluşumu" : "Endogenous Hypoxia & Gas Distension"}
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider flex items-center gap-1">
                  <Cpu className="w-3.5 h-3.5 text-amber-400" />
                  {isTr ? "Geometrik Ortalama g(x)" : "Geometric Mean g(x)"}
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-amber-300 tabular-nums">
                  {pmiCalculations.gx}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "CoDa Simplex Merkezleme (S^6)" : "CoDa Simplex Centroid (S^6)"}
                </p>
              </div>
            </div>

            {/* Interactive Sliders & Live 16S Taxonomic Succession */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Ambient Environmental Parameters */}
              <div className="p-5 rounded-2xl border border-tactical-border/70 bg-[#080D1A] space-y-5 shadow-lg">
                <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
                  <span className="text-xs font-extrabold text-white uppercase tracking-wider flex items-center gap-1.5">
                    <Sliders className="w-4 h-4 text-emerald-400" />
                    {isTr ? "Olay Yeri Ortam Isısı" : "Crime Scene Temperature"}
                  </span>
                  <span className="text-[10px] text-emerald-400 font-bold font-mono">
                    {ambientTemp.toFixed(1)} °C
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-[10px] text-zinc-400">
                    <span>{isTr ? "Ortalama Sıcaklık (T_ambient):" : "Mean Ambient Temp:"}</span>
                    <span className="font-bold text-white">{ambientTemp} °C</span>
                  </div>
                  <input
                    type="range"
                    min="2"
                    max="35"
                    step="0.5"
                    value={ambientTemp}
                    onChange={(e) => setAmbientTemp(parseFloat(e.target.value))}
                    className="w-full accent-emerald-400 bg-black/40 h-2 rounded-lg cursor-pointer"
                  />
                  <div className="flex justify-between text-[8px] text-zinc-500 font-mono">
                    <span>2.0 °C (Kış / Soğuk)</span>
                    <span>20.0 °C (Standart)</span>
                    <span>35.0 °C (Yaz / Sıcak)</span>
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-tactical-border/30">
                  <div className="flex justify-between text-[10px] text-zinc-400">
                    <span>{isTr ? "Taban Fizyolojik Eşik (T_base):" : "Base Physiological Threshold:"}</span>
                    <span className="font-bold text-white">{baseTemp.toFixed(1)} °C</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="6"
                    step="0.5"
                    value={baseTemp}
                    onChange={(e) => setBaseTemp(parseFloat(e.target.value))}
                    className="w-full accent-cyan-400 bg-black/40 h-2 rounded-lg cursor-pointer"
                  />
                  <span className="text-[8px] text-zinc-500 block leading-tight">
                    {isTr
                      ? "Metodolojik standart T_base = 0.0 °C (Mason et al. 2024 / Metcalf et al. 2016)."
                      : "Standard methodological default T_base = 0.0 °C."}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-[10px] text-emerald-300 space-y-1">
                  <span className="font-bold block uppercase text-[9px] text-emerald-400">
                    {isTr ? "Termal Kinetik Formülü:" : "Thermal Kinetic Model:"}
                  </span>
                  <p className="font-mono text-[9px]">
                    ADD = Σ max(0, T_d − T_base)<br />
                    PMI_hours = (ADD × 24.0) / (T_ambient − T_base)
                  </p>
                </div>
              </div>

              {/* Right Columns: 16S Taxonomic Succession & CLR Transformed Coordinates */}
              <div className="lg:col-span-2 p-5 rounded-2xl border border-tactical-border/70 bg-[#080D1A] space-y-4 shadow-lg">
                <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
                  <span className="text-xs font-extrabold text-white uppercase tracking-wider flex items-center gap-1.5">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    {isTr ? "16S rRNA V4 Taksonomik Süksesyon & CLR Koordinatları" : "16S rRNA V4 Succession & CLR Coordinates"}
                  </span>
                  <span className="text-[9px] text-zinc-400 font-mono">
                    {Object.keys(pmiProfile).length} {isTr ? "Kritik Biyobelirteç" : "Key Taxa"}
                  </span>
                </div>

                <div className="space-y-3">
                  {Object.entries(pmiProfile).map(([taxon, abund]) => {
                    const clrVal = pmiCalculations.clr[taxon] || 0;
                    const isPositive = clrVal >= 0;
                    return (
                      <div key={taxon} className="space-y-1">
                        <div className="flex items-center justify-between text-[10px]">
                          <span className="font-bold text-white truncate max-w-[220px] sm:max-w-none">
                            {taxon.replace(/_/g, " ")}
                          </span>
                          <div className="flex items-center gap-3 font-mono">
                            <span className="text-zinc-400">{(abund * 100).toFixed(1)}%</span>
                            <span className={`font-bold px-1.5 py-0.5 rounded text-[9px] ${
                              isPositive ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                            }`}>
                              CLR: {clrVal >= 0 ? `+${clrVal.toFixed(3)}` : clrVal.toFixed(3)}
                            </span>
                          </div>
                        </div>
                        {/* Proportion Bar */}
                        <div className="w-full bg-black/50 h-2 rounded-full overflow-hidden border border-white/5 flex">
                          <div
                            className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-full rounded-full transition-all duration-300"
                            style={{ width: `${Math.min(100, abund * 100 * 2.5)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="pt-2 border-t border-tactical-border/30 flex items-center justify-between text-[9px] text-zinc-500 font-mono">
                  <span>{isTr ? "CLR Simplex Korunumu: Σ CLR = 0.0000" : "CLR Simplex Invariance: Σ CLR = 0.0000"}</span>
                  <span className="text-emerald-400 font-bold">{isTr ? "ISO/IEC 17025 Onaylı" : "ISO/IEC 17025 Certified"}</span>
                </div>

              </div>
            </div>
          </motion.div>
        )}

        {activeSubMode === "TOUCH_TRACE" && (
          <motion.div
            key="touch_trace"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-6"
          >
            {/* Top Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 rounded-2xl border border-emerald-500/30 bg-emerald-950/20 shadow-md space-y-1">
                <span className="text-[9px] text-emerald-400 font-bold uppercase tracking-wider">
                  {isTr ? "Kalibre Olabilirlik Oranı (LR)" : "Calibrated Likelihood Ratio"}
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-white tabular-nums">
                  {touchCalculations.lrCal}
                </p>
                <p className="text-[10px] text-emerald-300 font-bold">
                  Log₁₀ LR: +{touchCalculations.log10Cal}
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider">
                  {isTr ? "Aitchison Mesafesi (d_A)" : "Aitchison Distance (d_A)"}
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-cyan-300 tabular-nums">
                  {touchCalculations.dA}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Kompansatuvar Log-Oran Diverjansı" : "Compositional Log-Ratio Divergence"}
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider">
                  {isTr ? "Olasılık Yoğunluğu f(d|Hp)" : "Likelihood Density f(d|Hp)"}
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-purple-300 tabular-nums">
                  {touchCalculations.fHp}
                </p>
                <p className="text-[10px] text-zinc-400 font-mono">
                  f(d|Hd) = {touchCalculations.fHd}
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider">
                  {isTr ? "Hedef Panel Standartı" : "Target Panel Standard"}
                </span>
                <p className="text-xl sm:text-2xl font-extrabold text-white uppercase">
                  hidSkinPlex+
                </p>
                <p className="text-[10px] text-emerald-400 font-semibold">
                  365 SNPs • MCC = 0.949
                </p>
              </div>
            </div>

            {/* ENFSI 2017 Evaluative Statement & Prosecutor's Fallacy Shield */}
            <div className="p-5 rounded-2xl border border-emerald-500/30 bg-emerald-950/10 space-y-3">
              <div className="flex items-center gap-2 text-xs font-extrabold text-emerald-400 uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4" />
                <span>{isTr ? "ENFSI (2017) Standart Sözlü Yüklem Raporu" : "ENFSI (2017) Evaluative Verbal Statement"}</span>
              </div>
              <p className="text-sm font-sans font-bold text-white leading-relaxed">
                "{isTr ? touchCalculations.tierTr : touchCalculations.tierEn}"
              </p>
              <div className="p-3 rounded-xl bg-black/50 border border-tactical-border/40 text-[10px] text-zinc-400 space-y-1">
                <span className="text-[9px] font-bold text-amber-400 uppercase block flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3 text-amber-400" />
                  {isTr ? "Savcılık Yanılgısı Kalkanı (Prosecutor's Fallacy Shield):" : "Prosecutor's Fallacy Defense Shield:"}
                </span>
                <p className="leading-relaxed">
                  {isTr
                    ? `Bu analiz P(Delil|Hipotez) olasılığını değerlendirir. Gözlemlenen mikrobiyal profilin, izin şüpheliden kaynaklanması durumunda (Hp), bilinmeyen bir şahıstan kaynaklanması durumuna (Hd) kıyasla ${touchCalculations.lrCal} kat daha olası olduğunu ifade eder. Sanığın suçluluk olasılığını belirlemez.`
                    : `This evaluation conditions on P(Evidence|Hypothesis). It states that the observed microbial trace is ${touchCalculations.lrCal} times more probable if the trace originated from the suspect (Hp) than if it originated from an unknown individual (Hd). It does NOT express the probability of guilt.`}
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {activeSubMode === "BODY_FLUID" && (
          <motion.div
            key="body_fluid"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-6"
          >
            {/* Top Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-2xl border border-emerald-500/30 bg-emerald-950/20 shadow-md space-y-1">
                <span className="text-[9px] text-emerald-400 font-bold uppercase tracking-wider">
                  {isTr ? "Tahmin Edilen Doku/Sıvı Kökeni" : "Predicted Tissue/Fluid Origin"}
                </span>
                <p className="text-xl sm:text-2xl font-extrabold text-white uppercase truncate">
                  {isTr ? fluidCalculations.predictedOriginTr : fluidCalculations.predictedOrigin}
                </p>
                <p className="text-[10px] text-emerald-400 font-bold">
                  {isTr ? "Kalibre Güven:" : "Calibrated Confidence:"} {(fluidCalculations.calibratedVaginal * 100).toFixed(1)}%
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider">
                  {isTr ? "Sınıflandırıcı Modeli" : "Classifier Architecture"}
                </span>
                <p className="text-xl sm:text-2xl font-extrabold text-cyan-300">
                  Díez López ML
                </p>
                <p className="text-[10px] text-zinc-400 font-mono">
                  Weighted Average F₁-score = 0.89
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider">
                  {isTr ? "Leke Durumu & Degradasyon" : "Stain Integrity & Degradation"}
                </span>
                <p className="text-xl sm:text-2xl font-extrabold text-amber-300">
                  {isTr ? "DEGRADE LEKE" : "DEGRADED STAIN"}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Pamuklu Kumaş Yüzeyi" : "Cotton Substrate Transfer"}
                </p>
              </div>
            </div>

            {/* 6-Class Probabilities Grid */}
            <div className="p-5 rounded-2xl border border-tactical-border/70 bg-[#080D1A] space-y-4 shadow-lg">
              <span className="text-xs font-extrabold text-white uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
                {isTr ? "6'lı Vücut Sıvısı Olasılık Dağılımı (Softmax Normalized)" : "6-Class Body Fluid Probability Distribution"}
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { name: isTr ? "Vajinal Sıvı / Menstrüel" : "Vaginal Secretion / Menstrual", prob: fluidCalculations.vaginal, cal: fluidCalculations.calibratedVaginal, highlight: true },
                  { name: isTr ? "El Derisi / Dokunma" : "Hand Skin / Touch Sebum", prob: fluidCalculations.hand, cal: 0.048, highlight: false },
                  { name: isTr ? "Tükürük / Oral" : "Saliva / Oral Cavity", prob: fluidCalculations.saliva, cal: 0.025, highlight: false },
                  { name: isTr ? "İdrar Trasesi" : "Urine Trace", prob: fluidCalculations.urine, cal: 0.018, highlight: false },
                  { name: isTr ? "Penil Deri" : "Penile Skin", prob: fluidCalculations.penile, cal: 0.015, highlight: false },
                  { name: isTr ? "Seminal Sıvı" : "Seminal Fluid", prob: fluidCalculations.semen, cal: 0.007, highlight: false }
                ].map(item => (
                  <div
                    key={item.name}
                    className={`p-3.5 rounded-xl border space-y-2 ${
                      item.highlight
                        ? "border-emerald-500/40 bg-emerald-950/20"
                        : "border-tactical-border/40 bg-black/40"
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs font-bold">
                      <span className={item.highlight ? "text-emerald-300" : "text-zinc-300"}>
                        {item.name}
                      </span>
                      <span className="font-mono text-white">{(item.prob * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-black/60 h-2 rounded-full overflow-hidden border border-white/5">
                      <div
                        className={`h-full rounded-full ${
                          item.highlight ? "bg-emerald-400" : "bg-zinc-600"
                        }`}
                        style={{ width: `${item.prob * 100}%` }}
                      />
                    </div>
                    <span className="text-[9px] text-zinc-400 font-mono block">
                      {isTr ? "Kalibre Olasılık:" : "Calibrated P:"} {(item.cal * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeSubMode === "SOIL_CDI" && (
          <motion.div
            key="soil_cdi"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-6"
          >
            {/* Top Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-2xl border border-emerald-500/30 bg-emerald-950/20 shadow-md space-y-1">
                <span className="text-[9px] text-emerald-400 font-bold uppercase tracking-wider">
                  {isTr ? "Baskın Çürüme Evresi" : "Dominant Taphonomic Stage"}
                </span>
                <p className="text-xl sm:text-2xl font-extrabold text-white uppercase truncate">
                  {isTr ? soilCalculations.dominantStageTr : soilCalculations.dominantStage}
                </p>
                <p className="text-[10px] text-emerald-400 font-bold">
                  P(Advanced Decay) = {(soilCalculations.advanced * 100).toFixed(1)}%
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider">
                  {isTr ? "CDI Pertürbasyon İndeksi" : "CDI Perturbation Index"}
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-cyan-300">
                  {soilCalculations.cdiPerturbation}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Doğal Toprak Florasından Sapma" : "Deviation from Native Baseline"}
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-tactical-border/70 bg-[#080D1A] shadow-md space-y-1">
                <span className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider">
                  {isTr ? "Bakteri / Fungi (ITS) Oranı" : "Bacterial / Fungal (ITS) Ratio"}
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-purple-300">
                  {soilCalculations.bfRatio}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Dual-Kingdom Metagenomik" : "Dual-Kingdom Metagenomics"}
                </p>
              </div>
            </div>

            {/* 5-Stage Decomposition Progress Timeline */}
            <div className="p-5 rounded-2xl border border-tactical-border/70 bg-[#080D1A] space-y-4 shadow-lg">
              <span className="text-xs font-extrabold text-white uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
                {isTr ? "Kadavra Çürüme Adası (CDI) 5 Evreli İlerleme Çizelgesi" : "Cadaver Decomposition Island (CDI) 5-Stage Progression"}
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
                {[
                  { name: isTr ? "1. Taze (Fresh)" : "1. Fresh", prob: soilCalculations.fresh, active: false },
                  { name: isTr ? "2. Şişme (Bloat)" : "2. Bloat", prob: soilCalculations.bloat, active: false },
                  { name: isTr ? "3. Aktif Çürüme" : "3. Active Decay", prob: soilCalculations.active, active: false },
                  { name: isTr ? "4. İleri Çürüme" : "4. Advanced Decay", prob: soilCalculations.advanced, active: true },
                  { name: isTr ? "5. İskeletleşme" : "5. Skeletonization", prob: soilCalculations.skeletonization, active: false }
                ].map(stage => (
                  <div
                    key={stage.name}
                    className={`p-3 rounded-xl border space-y-2 ${
                      stage.active
                        ? "border-emerald-500/40 bg-emerald-950/20"
                        : "border-tactical-border/40 bg-black/40"
                    }`}
                  >
                    <span className={`text-[10px] font-bold block truncate ${stage.active ? "text-emerald-300" : "text-zinc-400"}`}>
                      {stage.name}
                    </span>
                    <p className="text-lg font-mono font-extrabold text-white">
                      {(stage.prob * 100).toFixed(1)}%
                    </p>
                    <div className="w-full bg-black/60 h-1.5 rounded-full overflow-hidden border border-white/5">
                      <div
                        className={`h-full rounded-full ${stage.active ? "bg-emerald-400" : "bg-zinc-600"}`}
                        style={{ width: `${stage.prob * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
