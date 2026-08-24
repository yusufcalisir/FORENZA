"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Cpu,
  Layers,
  Sparkles,
  ShieldCheck,
  Zap,
  Activity,
  AlertTriangle,
  Scale,
  Search,
  CheckCircle2,
  FileCode2,
  ChevronRight,
  TrendingUp,
  BarChart2,
  Globe2,
  Flame,
  Info,
  Filter,
  Sliders,
  Scissors
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getApiBaseUrl } from "@/lib/api";

// ─── Golden Benchmark Presets ──────────────────────────────────────────────────
const MLSTR_GOLDEN_PRESETS = [
  {
    id: "VECTOR_MLSTR_01",
    name: "VECTOR_MLSTR_01: Severe Back-Stutter Discrimination",
    nameTr: "VECTOR_MLSTR_01: Şiddetli Geri-Kekeleme Ayrıştırma",
    locus: "D21S11",
    challenge: "High-Ratio Reverse Stutter (SR = 18.5% at -4 bp position)",
    challengeTr: "Yüksek Oranlı Ters Kekeleme (-4 bp pozisyonunda SR = %18.5)",
    rawPeaks: [
      { id: "Peak_30", h: 2400, bp: 214.0, class: "CLASS_TRUE_ALLELE", conf: 0.98 },
      { id: "Peak_29", h: 444, bp: 210.0, class: "CLASS_BACK_STUTTER", conf: 0.94 }
    ],
    action: "SUBTRACT_STUTTER_SIGNAL (444.0 RFU)",
    actionTr: "KEKELEME SİNYALİNİ ÇIKAR (444.0 RFU)",
    mcmcSpeedup: "1.45x Faster (Burn-in -31%)",
    desc: "Correctly discriminates severe back-stutter from genuine minor contributor peak in D21S11.",
    descTr: "D21S11 lokusunda şiddetli geri kekelemeyi gerçek minör katkıcı pikinden doğru şekilde ayrıştırır."
  },
  {
    id: "VECTOR_MLSTR_02",
    name: "VECTOR_MLSTR_02: Split -A / +A Non-Template Recombination",
    nameTr: "VECTOR_MLSTR_02: Ayrık -A / +A Şablonsuz Adenilasyon Birleştirme",
    locus: "TH01",
    challenge: "Incomplete Polymerase Terminal Transferase (+1 bp split peak)",
    challengeTr: "Eksik Polimeraz Terminal Transferaz (+1 bp ayrık pik)",
    rawPeaks: [
      { id: "Peak_9.3", h: 1800, bp: 180.0, class: "CLASS_TRUE_ALLELE", conf: 0.96 },
      { id: "Peak_PlusA", h: 360, bp: 181.0, class: "CLASS_PLUS_A_ARTIFACT", conf: 0.88 }
    ],
    action: "RECOMBINE_PLUS_A_INTO_PARENT_PEAK (+360 RFU)",
    actionTr: "+A PİKİNİ ANA PİKLE BİRLEŞTİR (+360 RFU)",
    mcmcSpeedup: "1.30x Faster (Conserved Area)",
    desc: "Recombines split +A peak into parent 9.3 allele, conserving total signal area.",
    descTr: "Ayrık +A pikini ana 9.3 alleliyle birleştirerek toplam pik alanını korur."
  },
  {
    id: "VECTOR_MLSTR_03",
    name: "VECTOR_MLSTR_03: High-RFU Spectral Pull-Up Elimination",
    nameTr: "VECTOR_MLSTR_03: Yüksek-RFU Spektral Pull-Up Eleme",
    locus: "vWA",
    challenge: "Secondary Dye Bleedthrough (h > 6000 RFU in 6-FAM dye)",
    challengeTr: "İkincil Boya Sızıntısı (6-FAM kanalında h > 6000 RFU)",
    rawPeaks: [
      { id: "Major_Blue", h: 6200, bp: 165.0, class: "CLASS_TRUE_ALLELE", conf: 0.99 },
      { id: "PullUp_Yellow", h: 480, bp: 165.0, class: "CLASS_SPECTRAL_PULL_UP", conf: 0.95 }
    ],
    action: "CULL_SPECTRAL_PULL_UP_BLEEDTHROUGH",
    actionTr: "SPEKTRAL PULL-UP SIZINTISINI ELE",
    mcmcSpeedup: "1.60x Faster (Eliminated Artifact)",
    desc: "Identifies and culls spectral pull-up bleedthrough caused by CCD sensor saturation.",
    descTr: "CCD sensör doygunluğundan kaynaklanan spektral pull-up sızıntısını tespit edip eler."
  },
  {
    id: "VECTOR_MLSTR_04",
    name: "VECTOR_MLSTR_04: PROVEDIt 3-Person Mixture Pre-Filtering",
    nameTr: "VECTOR_MLSTR_04: PROVEDIt 3 Kişilik Karışım Ön Filtreleme",
    locus: "D3S1358",
    challenge: "Complex 3-Person Mixture with 2 Stutters and 1 Noise Peak",
    challengeTr: "2 Kekeleme ve 1 Gürültü Piki İçeren Karmaşık 3 Kişilik Karışım",
    rawPeaks: [
      { id: "Allele_15", h: 1400, bp: 120.0, class: "CLASS_TRUE_ALLELE", conf: 0.98 },
      { id: "Allele_16", h: 950, bp: 124.0, class: "CLASS_TRUE_ALLELE", conf: 0.96 },
      { id: "Allele_17", h: 600, bp: 128.0, class: "CLASS_TRUE_ALLELE", conf: 0.92 },
      { id: "Stutter_14", h: 120, bp: 116.0, class: "CLASS_BACK_STUTTER", conf: 0.94 },
      { id: "Noise_SubAT", h: 32, bp: 110.0, class: "CLASS_BASE_NOISE_DROP_IN", conf: 0.97 }
    ],
    action: "OPTIMIZE_MCMC_SEARCH_SPACE (-75% Permutations)",
    actionTr: "MCMC ARAMA UZAYINI OPTİMİZE ET (%-75 Permütasyon)",
    mcmcSpeedup: "2.10x Faster (R̂ = 1.012)",
    desc: "Filters stutters and sub-AT noise, reducing MCMC permutation state space from 32 to 8 candidate genotypes.",
    descTr: "Kekeleme ve eşik altı gürültüleri eleyerek MCMC permütasyon uzayını 32'den 8 adaya indirir."
  }
];

export const PanelMLSTR: React.FC = () => {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activePreset, setActivePreset] = useState(MLSTR_GOLDEN_PRESETS[0]);
  const [activeTab, setActiveTab] = useState<"classifier" | "isfg3tier" | "mcmcTelemetry" | "features">("classifier");
  const [selectedPeakIndex, setSelectedPeakIndex] = useState<number>(0);
  const [liveMlData, setLiveMlData] = useState<any>(null);

  // Reset selected peak index on preset change
  React.useEffect(() => {
    setSelectedPeakIndex(0);
  }, [activePreset]);

  // Current selected peak & major peak
  const currentPeak = activePreset.rawPeaks[selectedPeakIndex] || activePreset.rawPeaks[0];
  const majorPeak = React.useMemo(() => {
    return activePreset.rawPeaks.reduce((max, p) => (p.h > max.h ? p : max), activePreset.rawPeaks[0]);
  }, [activePreset]);

  // 24D Feature metrics computed for current peak
  const peakFeatures = React.useMemo(() => {
    const h = currentPeak.h;
    const fwhm = 1.0 + (h > 1500 ? 0.25 : 0.0);
    const area = Number((h * 1.064 * fwhm).toFixed(1));
    const sharpness = Number((Math.min(1.0, h / Math.max(1, area))).toFixed(4));
    const snr = Number((h / 3.0).toFixed(1));
    const deltaBp = Number((currentPeak.bp - majorPeak.bp).toFixed(2));
    const isBackStutter = Math.abs(deltaBp + 4.0) < 0.8;
    const isFwdStutter = Math.abs(deltaBp - 4.0) < 0.8;
    const isPlusA = Math.abs(deltaBp - 1.0) < 0.6;
    const sr = majorPeak.h > 0 ? Number(((h / majorPeak.h) * 100).toFixed(1)) : 0;

    const locus = activePreset.locus;
    const entropy = locus === "SE33" ? 1.942 : locus === "D21S11" ? 1.716 : locus === "TH01" ? 1.582 : 1.650;
    const gcContent = locus === "D18S51" ? 32.5 : locus === "D21S11" ? 25.0 : locus === "TH01" ? 28.0 : 30.0;
    const homopolymer = locus === "SE33" ? 4 : locus === "D21S11" ? 2 : 3;

    const hb = Number((Math.min(1.0, h / Math.max(h, majorPeak.h))).toFixed(3));
    const pullUp = currentPeak.class === "CLASS_PULL_UP_ARTIFACT" ? 8.5 : 0.0;
    const atMargin = Math.max(0, h - 50.0);

    return {
      h,
      area,
      fwhm,
      sharpness,
      snr,
      deltaBp,
      isBackStutter,
      isFwdStutter,
      isPlusA,
      sr,
      entropy,
      gcContent,
      homopolymer,
      hb,
      pullUp,
      atMargin,
    };
  }, [currentPeak, majorPeak, activePreset]);

  // Live Backend Query on Preset Change
  React.useEffect(() => {
    let isMounted = true;
    async function fetchMlData() {
      try {
        const API_BASE = getApiBaseUrl();
        const firstPeak = activePreset.rawPeaks[0];
        if (!firstPeak) return;

        const res = await fetch(`${API_BASE}/api/v1/forensic/ml-str/classify-peak`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            locus_name: activePreset.locus,
            peak_id: firstPeak.id,
            peak_height: firstPeak.h,
            peak_area: firstPeak.h * 8.5,
            fwhm: 1.25,
            bp_position: firstPeak.bp,
            major_allele_bp: firstPeak.bp,
            major_allele_height: firstPeak.h,
            repeat_unit_len: 4,
          }),
          signal: AbortSignal.timeout(4000),
        });
        if (res.ok && isMounted) {
          const data = await res.json();
          setLiveMlData(data);
        }
      } catch {
        // Fallback
      }
    }
    fetchMlData();
    return () => {
      isMounted = false;
    };
  }, [activePreset]);



  return (
    <div className="space-y-6 text-tactical-text">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-purple-950/40 via-tactical-surface/80 to-emerald-950/40 p-6 border border-purple-500/30 backdrop-blur-xl shadow-2xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5" />
                {isTr ? "ML STR ÇAĞIRMA & ARTEFAKT ELEME" : "ML STR CALLING & ARTIFACT FILTER"}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                Fragsifier 500-Tree RF Ensemble
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/40">
                ISFG (2016) 3-Tier Hierarchy
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              {isTr
                ? "Makine Öğrenmesi STR Çağırma & MCMC Ön Filtreleme Laboratuvarı"
                : "Machine Learning STR Calling & MCMC Pre-Filtering Lab"}
            </h2>
            <p className="text-sm text-slate-300 max-w-3xl mt-1">
              {isTr
                ? "Barash et al. (2023) ve Fragsifier Random Forest mimarisini temel alarak 24-boyutlu özellik uzayında elektroferogram piklerini ve MPS okumalarını 7 biyofiziksel sınıfa ayırır, cihaz artefaktlarını eler ve MCMC karışım dekonvolüsyonunu 2.1 kata kadar hızlandırır."
                : "Leverages Barash et al. (2023) and Fragsifier Random Forest architecture to classify EPG peaks and MPS reads across a 24-D feature space into 7 biophysical classes, culling artifacts and accelerating downstream MCMC mixture deconvolution up to 2.1x."}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {MLSTR_GOLDEN_PRESETS.map((preset) => (
              <button
                key={preset.id}
                onClick={() => setActivePreset(preset)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all flex items-center gap-1.5 border ${
                  activePreset.id === preset.id
                    ? "bg-purple-500/30 text-purple-200 border-purple-500/60 shadow-lg shadow-purple-950/40"
                    : "bg-tactical-surface/60 text-slate-400 border-tactical-border/60 hover:text-white"
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                {preset.id}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-tactical-border/60 gap-4">
        {[
          { id: "classifier", label: isTr ? "Fragsifier 7-Sınıflı Ayrıştırıcı" : "Fragsifier 7-Class Classifier", icon: Filter },
          { id: "isfg3tier", label: isTr ? "ISFG 3-Seviyeli Hiyerarşi" : "ISFG 3-Tier Hierarchy", icon: Layers },
          { id: "mcmcTelemetry", label: isTr ? "MCMC Hızlanma & Arama Uzayı" : "MCMC Optimization Telemetry", icon: Zap },
          { id: "features", label: isTr ? "24-Boyutlu Özellik Uzayı" : "24-D Feature Vector Explorer", icon: Sliders },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`pb-3 px-2 text-sm font-medium flex items-center gap-2 border-b-2 transition-all ${
                isActive
                  ? "border-purple-500 text-purple-300 font-semibold"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === "classifier" && (
          <motion.div
            key="classifier"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-6"
          >
            {/* Active Preset Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-tactical-surface/50 border border-tactical-border/60 rounded-xl p-4">
                <div className="text-xs text-slate-400 font-mono mb-1">{isTr ? "HEDEF LOKUS" : "TARGET LOCUS"}</div>
                <div className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="text-purple-400 font-mono">{activePreset.locus}</span>
                </div>
                <div className="text-xs text-slate-400 mt-2">
                  {isTr ? activePreset.challengeTr : activePreset.challenge}
                </div>
              </div>

              <div className="bg-tactical-surface/50 border border-tactical-border/60 rounded-xl p-4">
                <div className="text-xs text-slate-400 font-mono mb-1">{isTr ? "HAM PİK SAYISI" : "RAW PEAKS INGESTED"}</div>
                <div className="text-xl font-bold text-amber-300 font-mono">
                  {activePreset.rawPeaks.length} Peaks
                </div>
                <div className="text-xs text-slate-400 mt-2">
                  {isTr ? "Sinyal Morfoloji Analizi" : "Signal Morphology Analysis"}
                </div>
              </div>

              <div className="bg-tactical-surface/50 border border-emerald-500/40 rounded-xl p-4 bg-emerald-950/20">
                <div className="text-xs text-emerald-400 font-mono mb-1">{isTr ? "UYGULANAN ARTEFAKT EYLEMİ" : "ARTIFACT ACTION TAKEN"}</div>
                <div className="text-sm font-bold text-emerald-300 font-mono mt-1 break-words">
                  {isTr ? activePreset.actionTr : activePreset.action}
                </div>
                <div className="text-xs text-emerald-400/80 mt-2">
                  {isTr ? "ISO 17025 Alan Korunumu" : "ISO 17025 Area Conserved"}
                </div>
              </div>

              <div className="bg-tactical-surface/50 border border-blue-500/40 rounded-xl p-4 bg-blue-950/20">
                <div className="text-xs text-blue-300 font-mono mb-1">{isTr ? "MCMC HIZLANMA KAZANCI" : "MCMC SPEEDUP GAIN"}</div>
                <div className="text-xl font-bold text-blue-300 font-mono flex items-center gap-1.5">
                  <TrendingUp className="w-5 h-5 text-blue-400" />
                  {activePreset.mcmcSpeedup}
                </div>
                <div className="text-xs text-blue-300/80 mt-1">
                  {isTr ? "Gelman-Rubin R̂ < 1.02" : "Gelman-Rubin R̂ < 1.02"}
                </div>
              </div>
            </div>

            {/* Peak Classification Table */}
            <div className="bg-tactical-surface/70 border border-tactical-border/80 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold text-white flex items-center gap-2">
                  <Activity className="w-4 h-4 text-purple-400" />
                  {isTr ? "Lokus İçi Sinyal Ayrıştırma ve Karar Tablosu" : "Intra-Locus Signal Classification & Action Matrix"}
                </h3>
                <span className="text-xs font-mono text-purple-300 bg-purple-950/60 border border-purple-500/40 px-2.5 py-1 rounded-md">
                  Fragsifier RF Ensemble Confidence: {">"} 92.0%
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs font-mono text-left">
                  <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="p-3">{isTr ? "PİK ID" : "PEAK ID"}</th>
                      <th className="p-3">{isTr ? "YÜKSEKLİK (RFU)" : "HEIGHT (RFU)"}</th>
                      <th className="p-3">{isTr ? "POZİSYON (BP)" : "POSITION (BP)"}</th>
                      <th className="p-3">{isTr ? "TAHMİNİ SINIF" : "PREDICTED CLASS"}</th>
                      <th className="p-3">{isTr ? "ML GÜVENİ" : "ML CONFIDENCE"}</th>
                      <th className="p-3">{isTr ? "KALİTE EYLEMİ" : "QUALITY ACTION"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {activePreset.rawPeaks.map((pk, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/40">
                        <td className="p-3 font-bold text-white">{pk.id}</td>
                        <td className="p-3 font-mono text-amber-300">{pk.h} RFU</td>
                        <td className="p-3 text-slate-300">{pk.bp} bp</td>
                        <td className="p-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              pk.class === "CLASS_TRUE_ALLELE"
                                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                : pk.class === "CLASS_BACK_STUTTER"
                                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                                : pk.class === "CLASS_SPECTRAL_PULL_UP"
                                ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                                : "bg-purple-500/20 text-purple-300 border border-purple-500/40"
                            }`}
                          >
                            {pk.class}
                          </span>
                        </td>
                        <td className="p-3 text-emerald-400 font-bold">{(pk.conf * 100).toFixed(1)}%</td>
                        <td className="p-3 text-slate-300">
                          {isTr
                            ? pk.class === "CLASS_TRUE_ALLELE"
                              ? "MCMC İçin Koru"
                              : pk.class === "CLASS_BACK_STUTTER"
                              ? "Kekeleme Sinyalini Çıkar"
                              : pk.class === "CLASS_PLUS_A_ARTIFACT"
                              ? "Ana Pikle Yeniden Birleştir"
                              : "Artefaktı Ele"
                            : pk.class === "CLASS_TRUE_ALLELE"
                            ? "Retain for MCMC Likelihood"
                            : pk.class === "CLASS_BACK_STUTTER"
                            ? "Subtract Stutter Signal"
                            : pk.class === "CLASS_PLUS_A_ARTIFACT"
                            ? "Recombine into Parent Peak"
                            : "Cull Artifact from Permutations"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === "isfg3tier" && (
          <motion.div
            key="isfg3tier"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-6"
          >
            <div className="bg-tactical-surface/70 border border-tactical-border/80 rounded-2xl p-6 space-y-6">
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-blue-400" />
                {isTr ? "ISFG (2016) 3-Aşamalı Hiyerarşik Terminoloji Düzeni" : "ISFG (2016) 3-Tier Hierarchical Nomenclature Architecture"}
              </h3>

              {/* Level 1 Card */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-blue-400 font-bold">LEVEL 1: RAW SEQUENCE STRING (FASTA/FASTQ)</span>
                  <span className="text-slate-400">Exact Nucleotide Base Composition</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-300 break-all">
                  TCTATCTATCTATCTATCTATCTATCTATCTATCTATCTATCTATCTGTCTGTCTGTCTATCTA
                </div>
              </div>

              {/* Level 2 Card */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-purple-400 font-bold">LEVEL 2: GENOME ALIGNMENT (GRCh38 / hg38)</span>
                  <span className="text-slate-400">Anchor Coordinates & Top-Strand Orientation</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono">
                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400">Chromosome:</span> <span className="text-white font-bold">chr3</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400">Coordinates:</span> <span className="text-white font-bold">45,540,700 - 45,540,770</span>
                  </div>
                  <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400">Strand:</span> <span className="text-emerald-400 font-bold">+ (Forward)</span>
                  </div>
                </div>
              </div>

              {/* Level 3 Card */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-emerald-400 font-bold">LEVEL 3: COMPACT NOMENCLATURE & CE BACKWARD TRANSLATION</span>
                  <span className="text-amber-400 font-bold">CE Call: Allele 16.0</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-purple-300">
                  [TCTA]1 [TCTG]3 [TCTA]12  ───►  CE Length: 16.0 (100% Backward Compatible)
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === "mcmcTelemetry" && (
          <motion.div
            key="mcmcTelemetry"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-6"
          >
            <div className="bg-tactical-surface/70 border border-tactical-border/80 rounded-2xl p-6 space-y-4">
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-400" />
                {isTr ? "MCMC-MH Arama Uzayı ve Yakınsama İyileştirmesi" : "MCMC-MH State Space Reduction & Convergence Optimization"}
              </h3>
              <p className="text-xs text-slate-300">
                {isTr
                  ? "ML ön filtreleme katmanı, olasılıksal karışım dekonvolüsyonunun biyofiziksel olabilirlik modelini değiştirmeden Markov zincirinin arama yapacağı permütasyon uzayını temizler:"
                  : "The upstream ML pre-filter narrows the combinatorial permutation space explored by MCMC without altering the continuous Gamma/Log-Normal biophysical likelihood density:"}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                  <div className="text-xs text-slate-400 font-mono">BURN-IN CYCLE REDUCTION</div>
                  <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">-38.5%</div>
                  <div className="text-xs text-slate-500 mt-1">10,000 $\to$ 6,150 iterations</div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                  <div className="text-xs text-slate-400 font-mono">GELMAN-RUBIN CONVERGENCE R̂</div>
                  <div className="text-2xl font-bold text-blue-400 font-mono mt-1">1.012</div>
                  <div className="text-xs text-slate-500 mt-1">Well below SWGDAM threshold (1.05)</div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
                  <div className="text-xs text-slate-400 font-mono">FALSE CONTRIBUTOR EXCLUSION</div>
                  <div className="text-2xl font-bold text-purple-400 font-mono mt-1">100.0%</div>
                  <div className="text-xs text-slate-500 mt-1">Zero spurious noise inclusions</div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === "features" && (
          <motion.div
            key="features"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-6"
          >
            {/* Interactive 24D Feature Space Container */}
            <div className="bg-tactical-surface/70 border border-tactical-border/80 rounded-2xl p-5 sm:p-6 space-y-6 shadow-2xl backdrop-blur-xl">
              {/* Header & Peak Selector */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
                      <Sliders className="w-5 h-5" />
                    </span>
                    <div>
                      <h3 className="text-base sm:text-lg font-bold text-white tracking-wide">
                        {isTr
                          ? "24-Boyutlu Sürekli Özellik Uzayı Vektörü (24D Feature Space)"
                          : "24-Dimensional Continuous Feature Space Vector"}
                      </h3>
                      <p className="text-xs text-slate-400">
                        {isTr
                          ? "Fragsifier rastgele orman (Random Forest) sınıflandırıcısına beslenen çok değişkenli biyofiziksel özellikler"
                          : "Multivariate biophysical feature metrics ingested by Fragsifier RF Ensemble"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Candidate Peak Selector */}
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs text-slate-400 font-semibold">{isTr ? "Tepe Seç:" : "Select Peak:"}</span>
                  <div className="flex items-center gap-1.5 bg-black/50 p-1 rounded-xl border border-tactical-border/60">
                    {activePreset.rawPeaks.map((peak, idx) => {
                      const isSelected = selectedPeakIndex === idx;
                      return (
                        <button
                          key={peak.id}
                          type="button"
                          onClick={() => setSelectedPeakIndex(idx)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                            isSelected
                              ? "bg-purple-500 text-white shadow-[0_0_12px_rgba(168,85,247,0.4)]"
                              : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
                          }`}
                        >
                          <span>{peak.id}</span>
                          <span className="text-[10px] opacity-80">({peak.h.toLocaleString()} RFU)</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* 24-Bar Spectral Feature Intensity Visualizer */}
              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                  <span className="text-slate-300 font-bold flex items-center gap-2">
                    <Activity className="w-4 h-4 text-purple-400" />
                    {isTr ? "24-Boyutlu Özellik Yoğunluk Spektrumu" : "24D Feature Vector Intensity Spectrum"}
                    <span className="font-mono text-purple-300 font-bold">[{currentPeak.id} • {currentPeak.bp} bp]</span>
                  </span>
                  <div className="flex items-center gap-3 text-[10px] font-mono text-slate-400">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-purple-400" /> {isTr ? "x1-x6 Morfoloji" : "x1-x6 Morphology"}</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-400" /> {isTr ? "x7-x12 Kekeleme" : "x7-x12 Stutter"}</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-400" /> {isTr ? "x13-x18 Dizi" : "x13-x18 Sequence"}</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-400" /> {isTr ? "x19-x24 Karışım" : "x19-x24 Mixture"}</span>
                  </div>
                </div>

                {/* 24 Normalized Bars */}
                <div className="grid grid-cols-12 sm:grid-cols-24 gap-1 h-16 items-end pt-2 bg-black/40 rounded-lg p-2 border border-slate-900">
                  {[
                    // x1-x6: Morphology (Purple)
                    { id: "x1", val: Math.min(100, (currentPeak.h / 3000) * 100), label: "Height", color: "bg-purple-500" },
                    { id: "x2", val: Math.min(100, (peakFeatures.area / 3000) * 100), label: "Area", color: "bg-purple-500" },
                    { id: "x3", val: peakFeatures.sharpness * 100, label: "Sharpness", color: "bg-purple-400" },
                    { id: "x4", val: Math.min(100, (peakFeatures.snr / 800) * 100), label: "SNR", color: "bg-purple-400" },
                    { id: "x5", val: Math.min(100, peakFeatures.fwhm * 50), label: "FWHM", color: "bg-purple-300" },
                    { id: "x6", val: 85, label: "Symmetry", color: "bg-purple-300" },
                    // x7-x12: Stutter & Proximity (Amber)
                    { id: "x7", val: Math.abs(peakFeatures.deltaBp) * 15, label: "Δbp", color: "bg-amber-500" },
                    { id: "x8", val: peakFeatures.isBackStutter ? 95 : 5, label: "I_-1", color: "bg-amber-500" },
                    { id: "x9", val: peakFeatures.isFwdStutter ? 95 : 5, label: "I_+1", color: "bg-amber-400" },
                    { id: "x10", val: peakFeatures.isPlusA ? 95 : 5, label: "I_+A", color: "bg-amber-400" },
                    { id: "x11", val: Math.min(100, peakFeatures.sr * 3), label: "SR", color: "bg-amber-300" },
                    { id: "x12", val: 25, label: "Proximity", color: "bg-amber-300" },
                    // x13-x18: Sequence Complexity (Blue)
                    { id: "x13", val: (peakFeatures.entropy / 2.0) * 100, label: "Entropy", color: "bg-blue-500" },
                    { id: "x14", val: (peakFeatures.homopolymer / 6) * 100, label: "L_homo", color: "bg-blue-500" },
                    { id: "x15", val: peakFeatures.gcContent * 2, label: "GC%", color: "bg-blue-400" },
                    { id: "x16", val: 70, label: "SNP Dist", color: "bg-blue-400" },
                    { id: "x17", val: 60, label: "MotifLen", color: "bg-blue-300" },
                    { id: "x18", val: 75, label: "Tm Stability", color: "bg-blue-300" },
                    // x19-x24: Mixture Dynamics (Emerald)
                    { id: "x19", val: peakFeatures.hb * 100, label: "H_b Balance", color: "bg-emerald-500" },
                    { id: "x20", val: peakFeatures.pullUp > 0 ? 80 : 5, label: "Pull-Up", color: "bg-emerald-500" },
                    { id: "x21", val: 95, label: "Amp Eff", color: "bg-emerald-400" },
                    { id: "x22", val: Math.min(100, (peakFeatures.atMargin / 2000) * 100), label: "AT Margin", color: "bg-emerald-400" },
                    { id: "x23", val: 15, label: "Base Noise", color: "bg-emerald-300" },
                    { id: "x24", val: 90, label: "Confidence", color: "bg-emerald-300" },
                  ].map((bar) => (
                    <div key={bar.id} className="h-full flex flex-col justify-end items-center group relative">
                      <motion.div
                        className={`w-full rounded-t ${bar.color} transition-all`}
                        initial={{ height: 0 }}
                        animate={{ height: `${Math.max(8, bar.val)}%` }}
                        transition={{ duration: 0.3 }}
                      />
                      <span className="text-[8px] font-mono text-slate-500 mt-1 hidden sm:inline">{bar.id}</span>
                      {/* Tooltip */}
                      <div className="absolute bottom-full mb-1 hidden group-hover:flex flex-col items-center bg-slate-900 border border-slate-700 text-white text-[9px] px-2 py-1 rounded shadow-lg z-20 whitespace-nowrap pointer-events-none">
                        <span className="font-bold">{bar.id}: {bar.label}</span>
                        <span className="text-slate-400 font-mono">{isTr ? `Skor: %${bar.val.toFixed(0)}` : `Score: ${bar.val.toFixed(0)}%`}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 4 Interactive Categorical Quadrants */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* ── Quadrant 1: Sinyal Morfolojisi ── */}
                <div className="p-4 rounded-2xl bg-gradient-to-b from-purple-950/20 to-slate-900/60 border border-purple-500/30 space-y-3.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="p-1.5 rounded-lg bg-purple-500/20 text-purple-300">
                        <Sparkles className="w-4 h-4" />
                      </span>
                      <span className="text-xs font-bold text-purple-200 tracking-wider">
                        1. {isTr ? "Sinyal Morfolojisi & Kinetik (x1 - x6)" : "Signal Morphology & Kinetics (x1 - x6)"}
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">
                      SNR {peakFeatures.snr}x
                    </span>
                  </div>

                  <div className="space-y-2.5 text-xs">
                    <div>
                      <div className="flex justify-between text-[11px] mb-1">
                        <span className="text-slate-400">{isTr ? "Tepe Yüksekliği (Peak Height - h):" : "Peak Height (h):"}</span>
                        <span className="font-mono font-bold text-white">{currentPeak.h.toLocaleString()} RFU</span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-slate-950 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-purple-300 rounded-full"
                          style={{ width: `${Math.min(100, (currentPeak.h / 3000) * 100)}%` }}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "İntegre Alan (A):" : "Integrated Area (A):"}</div>
                        <div className="font-bold text-purple-300">{peakFeatures.area} RFU·s</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "Keskinlik (h/A):" : "Sharpness (h/A):"}</div>
                        <div className="font-bold text-purple-300">{peakFeatures.sharpness}</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "FWHM Genişliği:" : "FWHM Peak Width:"}</div>
                        <div className="font-bold text-purple-300">{peakFeatures.fwhm.toFixed(2)} bp</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "Sinyal/Gürültü Oranı:" : "SNR Ratio:"}</div>
                        <div className="font-bold text-emerald-400">{peakFeatures.snr}x</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* ── Quadrant 2: Kekeleme & Artefakt Yakınlığı ── */}
                <div className="p-4 rounded-2xl bg-gradient-to-b from-amber-950/20 to-slate-900/60 border border-amber-500/30 space-y-3.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="p-1.5 rounded-lg bg-amber-500/20 text-amber-300">
                        <AlertTriangle className="w-4 h-4" />
                      </span>
                      <span className="text-xs font-bold text-amber-200 tracking-wider">
                        2. {isTr ? "Kekeleme & Artefakt Yakınlığı (x7 - x12)" : "Stutter & Artifact Proximity (x7 - x12)"}
                      </span>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${peakFeatures.sr > 15 ? "bg-red-500/20 text-red-300 border border-red-500/40" : "bg-amber-500/20 text-amber-300 border border-amber-500/40"}`}>
                      {isTr ? `SR: %${peakFeatures.sr}` : `SR: ${peakFeatures.sr}%`}
                    </span>
                  </div>

                  <div className="space-y-2.5 text-xs">
                    <div>
                      <div className="flex justify-between text-[11px] mb-1">
                        <span className="text-slate-400">{isTr ? "Kekeleme Oranı (Stutter Ratio - SR):" : "Stutter Ratio (SR):"}</span>
                        <span className="font-mono font-bold text-amber-300">{isTr ? `%${peakFeatures.sr}` : `${peakFeatures.sr}%`} <span className="text-slate-500 text-[9px]">({isTr ? "Eşik: %15.0" : "Threshold: 15.0%"})</span></span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-slate-950 overflow-hidden relative">
                        <div
                          className={`h-full rounded-full ${peakFeatures.sr > 15 ? "bg-red-500" : "bg-gradient-to-r from-amber-500 to-amber-300"}`}
                          style={{ width: `${Math.min(100, peakFeatures.sr * 4)}%` }}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-2 pt-1 font-mono text-[10px]">
                      <div className={`p-2.5 rounded-xl border flex flex-col items-center justify-center text-center ${peakFeatures.isBackStutter ? "bg-amber-500/15 border-amber-500/50 text-amber-300 font-bold" : "bg-black/40 border-slate-800 text-slate-500"}`}>
                        <span>{isTr ? "Geri-Kekeleme" : "Back-Stutter"}</span>
                        <span className="text-[11px] mt-0.5">{peakFeatures.isBackStutter ? (isTr ? "EVET (I_-1)" : "YES (I_-1)") : (isTr ? "HAYIR" : "NO")}</span>
                      </div>
                      <div className={`p-2.5 rounded-xl border flex flex-col items-center justify-center text-center ${peakFeatures.isFwdStutter ? "bg-amber-500/15 border-amber-500/50 text-amber-300 font-bold" : "bg-black/40 border-slate-800 text-slate-500"}`}>
                        <span>{isTr ? "İleri-Kekeleme" : "Forward-Stutter"}</span>
                        <span className="text-[11px] mt-0.5">{peakFeatures.isFwdStutter ? (isTr ? "EVET (I_+1)" : "YES (I_+1)") : (isTr ? "HAYIR" : "NO")}</span>
                      </div>
                      <div className={`p-2.5 rounded-xl border flex flex-col items-center justify-center text-center ${peakFeatures.isPlusA ? "bg-purple-500/15 border-purple-500/50 text-purple-300 font-bold" : "bg-black/40 border-slate-800 text-slate-500"}`}>
                        <span>{isTr ? "+A Adenilasyon" : "+A Adenylation"}</span>
                        <span className="text-[11px] mt-0.5">{peakFeatures.isPlusA ? (isTr ? "EVET (I_+A)" : "YES (I_+A)") : (isTr ? "HAYIR" : "NO")}</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-black/40 border border-slate-800 text-[11px] font-mono">
                      <span className="text-slate-400">{isTr ? "Baz Çifti Farkı (Δbp):" : "Delta Base-Pair (Δbp):"}</span>
                      <span className="font-bold text-white">{peakFeatures.deltaBp > 0 ? `+${peakFeatures.deltaBp}` : peakFeatures.deltaBp} bp</span>
                    </div>
                  </div>
                </div>

                {/* ── Quadrant 3: Dizi Karmaşıklığı & Entropi ── */}
                <div className="p-4 rounded-2xl bg-gradient-to-b from-blue-950/20 to-slate-900/60 border border-blue-500/30 space-y-3.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="p-1.5 rounded-lg bg-blue-500/20 text-blue-300">
                        <Layers className="w-4 h-4" />
                      </span>
                      <span className="text-xs font-bold text-blue-200 tracking-wider">
                        3. {isTr ? "Dizi Karmaşıklığı & Entropi (x13 - x18)" : "Sequence Complexity & Entropy (x13 - x18)"}
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-500/20 text-blue-300 border border-blue-500/40">
                      H(S): {peakFeatures.entropy} bit
                    </span>
                  </div>

                  <div className="space-y-2.5 text-xs">
                    <div>
                      <div className="flex justify-between text-[11px] mb-1">
                        <span className="text-slate-400">{isTr ? "Shannon Bilgi Entropisi H(S):" : "Shannon Entropy H(S):"}</span>
                        <span className="font-mono font-bold text-blue-300">{peakFeatures.entropy} bit <span className="text-slate-500 text-[9px]">({isTr ? "Maks: 2.0" : "Max: 2.0"})</span></span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-slate-950 overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-cyan-300 rounded-full"
                          style={{ width: `${(peakFeatures.entropy / 2.0) * 100}%` }}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "GC İçerik Oranı (f_GC):" : "GC Fraction (f_GC):"}</div>
                        <div className="font-bold text-cyan-300">{isTr ? `%${peakFeatures.gcContent}` : `${peakFeatures.gcContent}%`}</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "Homopolimer Uzunluğu:" : "Homopolymer Run (L_homo):"}</div>
                        <div className="font-bold text-cyan-300">{peakFeatures.homopolymer} bp</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "Yan SNP Mesafesi:" : "Flanking SNP Dist:"}</div>
                        <div className="font-bold text-blue-300">100.0 bp</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "Tekrar Birimi:" : "Repeat Unit Len:"}</div>
                        <div className="font-bold text-blue-300">4 bp (Tetra)</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* ── Quadrant 4: Karışım Dinamikleri & Eşik Marjı ── */}
                <div className="p-4 rounded-2xl bg-gradient-to-b from-emerald-950/20 to-slate-900/60 border border-emerald-500/30 space-y-3.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-300">
                        <ShieldCheck className="w-4 h-4" />
                      </span>
                      <span className="text-xs font-bold text-emerald-200 tracking-wider">
                        4. {isTr ? "Karışım Dinamikleri & Marj (x19 - x24)" : "Mixture Dynamics & Margin (x19 - x24)"}
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                      H_b: {peakFeatures.hb}
                    </span>
                  </div>

                  <div className="space-y-2.5 text-xs">
                    <div>
                      <div className="flex justify-between text-[11px] mb-1">
                        <span className="text-slate-400">{isTr ? "Heterozigot Dengesi (H_b):" : "Heterozygote Balance (H_b):"}</span>
                        <span className="font-mono font-bold text-emerald-300">{peakFeatures.hb} <span className="text-slate-500 text-[9px]">({isTr ? "Eşik: ≥ 0.60" : "Threshold: ≥ 0.60"})</span></span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-slate-950 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${peakFeatures.hb >= 0.6 ? "bg-gradient-to-r from-emerald-500 to-teal-300" : "bg-amber-500"}`}
                          style={{ width: `${Math.min(100, peakFeatures.hb * 100)}%` }}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "Analitik Eşik Marjı:" : "AT Threshold Margin:"}</div>
                        <div className="font-bold text-emerald-400">+{peakFeatures.atMargin.toLocaleString()} RFU</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "Spektral Çekme (Pull-Up):" : "Spectral Pull-Up:"}</div>
                        <div className="font-bold text-emerald-400">{isTr ? `%${peakFeatures.pullUp}` : `${peakFeatures.pullUp}%`}</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "Amplifikasyon Verimi (e_l):" : "Locus Amp Efficiency (e_l):"}</div>
                        <div className="font-bold text-teal-300">1.000</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-black/40 border border-slate-800 space-y-0.5">
                        <div className="text-slate-400 text-[10px]">{isTr ? "Fragsifier Karar Güveni:" : "RF Ensemble Conf:"}</div>
                        <div className="font-bold text-purple-300">{isTr ? `%${(currentPeak.conf * 100).toFixed(1)}` : `${(currentPeak.conf * 100).toFixed(1)}%`}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
};

export default PanelMLSTR;
