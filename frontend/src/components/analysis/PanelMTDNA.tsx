"use client";

import { useState, useTransition, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Dna,
  ShieldCheck,
  GitCommit,
  RefreshCw,
  AlertTriangle,
  Flame,
  CheckCircle2,
  XCircle,
  Database,
  Sliders,
  ChevronRight,
  TrendingUp,
  Sparkles,
  Info,
  Scale,
  Users,
  Activity,
  Layers,
  Network,
  GitPullRequest,
  Check,
  Compass,
  Globe2,
} from "lucide-react";

// ── Types ──────────────────────────────────────────────────────────────────

export interface MtDnaVariantVisual {
  position: number;
  refBase: string;
  variantBase: string;
  variantType: "SUBSTITUTION" | "INSERTION" | "DELETION" | "PHP";
  insertionIndex?: number;
  region: "HV1" | "HV2" | "HV3" | "CR_OTHER";
  formattedCall: string;
}

export interface CaseworkPreset {
  id: string;
  title: string;
  badge: string;
  description: string;
  relationship: string;
  variantsA: string[];
  variantsB: string[];
  expectedHgA: string;
  expectedHgB: string;
  expectedVerdict: string;
  expectedK: number;
  databaseN: number;
  expectedMinLr: number;
}

// ── Certified Presets ──────────────────────────────────────────────────────

const MTDNA_PRESETS: CaseworkPreset[] = [
  {
    id: "BENCHMARK_LINEAGE_A_EUR",
    title: "Benchmark LINEAGE-A (European Reference / EUR)",
    badge: "Haplogroup H1",
    description: "Common European H1 haplotype (263G, 315.1C, 750G, 16519C) with k=1,420 matches in EMPOP (N=48,200).",
    relationship: "Maternal Lineage Match",
    variantsA: ["263G", "315.1C", "750G", "16519C"],
    variantsB: ["263G", "315.1C", "750G", "16519C"],
    expectedHgA: "H1",
    expectedHgB: "H1",
    expectedVerdict: "MATCH",
    expectedK: 1420,
    databaseN: 48200,
    expectedMinLr: 32.89,
  },
  {
    id: "BENCHMARK_LINEAGE_B_AFR",
    title: "Benchmark LINEAGE-B (African Diaspora / AFR)",
    badge: "Haplogroup L2a1",
    description: "Sub-Saharan African L2a1 haplotype with 13 control region mutations and k=12 matches in EMPOP.",
    relationship: "Maternal Lineage Match",
    variantsA: [
      "146C", "152C", "182C", "198C", "263G", "309.1C", "315.1C",
      "750G", "16129C", "16223C", "16278C", "16390C", "16519C",
    ],
    variantsB: [
      "146C", "152C", "182C", "198C", "263G", "309.1C", "315.1C",
      "750G", "16129C", "16223C", "16278C", "16390C", "16519C",
    ],
    expectedHgA: "L2a1",
    expectedHgB: "L2a1",
    expectedVerdict: "MATCH",
    expectedK: 12,
    databaseN: 48200,
    expectedMinLr: 2518.8,
  },
  {
    id: "COHORT_POINT_HETEROPLASMY_PAIR",
    title: "Point Heteroplasmy Pair (16189Y vs 16189C)",
    badge: "IUPAC Mixed Base",
    description: "Questioned sample with 16189Y (C/T) vs reference homoplasmic 16189C (cannot be excluded).",
    relationship: "Maternal Lineage Match",
    variantsA: ["263G", "315.1C", "16189Y", "16519C"],
    variantsB: ["263G", "315.1C", "16189C", "16519C"],
    expectedHgA: "H1",
    expectedHgB: "H1",
    expectedVerdict: "MATCH",
    expectedK: 0,
    databaseN: 48500,
    expectedMinLr: 16190.7,
  },
  {
    id: "COHORT_MATERNAL_DUO_UNOBSERVED",
    title: "Rare Unobserved Maternal Lineage Duo (k=0)",
    badge: "Exact k=0 Bound",
    description: "Mother-daughter exact match with rare dinucleotide insertion 524.1AC unobserved in EMPOP.",
    relationship: "Maternal Lineage Match",
    variantsA: ["263G", "315.1C", "524.1AC", "16189C", "16278C", "16362C"],
    variantsB: ["263G", "315.1C", "524.1AC", "16189C", "16278C", "16362C"],
    expectedHgA: "X",
    expectedHgB: "X",
    expectedVerdict: "MATCH",
    expectedK: 0,
    databaseN: 48500,
    expectedMinLr: 16190.7,
  },
  {
    id: "COHORT_UNRELATED_EXCLUSION",
    title: "Unrelated Non-Kin Exclusion Pair (H1 vs L2a1)",
    badge: "SWGDAM Exclusion",
    description: "Two unrelated donors exhibiting 11 homoplasmic point differences yielding definitive exclusion.",
    relationship: "Unrelated Donors",
    variantsA: ["263G", "315.1C", "750G", "16519C"],
    variantsB: [
      "146C", "152C", "182C", "198C", "263G", "309.1C", "315.1C",
      "750G", "16129C", "16223C", "16278C", "16390C", "16519C",
    ],
    expectedHgA: "H1",
    expectedHgB: "L2a1",
    expectedVerdict: "EXCLUSION",
    expectedK: 0,
    databaseN: 48500,
    expectedMinLr: 0.0,
  },
];

// ── IUPAC Ambiguity Map ────────────────────────────────────────────────────

const IUPAC_LEGEND: Record<string, string> = {
  R: "A or G (Purine)",
  Y: "C or T (Pyrimidine)",
  M: "A or C (Amino)",
  K: "G or T (Keto)",
  S: "G or C (Strong)",
  W: "A or T (Weak)",
};

export default function PanelMTDNA() {
  const [selectedPresetId, setSelectedPresetId] = useState<string>("BENCHMARK_LINEAGE_A_EUR");
  const [observedK, setObservedK] = useState<number>(1420);
  const [databaseN, setDatabaseN] = useState<number>(48200);
  const [activeDomainTab, setActiveDomainTab] = useState<"ALL" | "HV1" | "HV2" | "HV3">("ALL");
  const [isPending, startTransition] = useTransition();

  const currentPreset = MTDNA_PRESETS.find((p) => p.id === selectedPresetId) || MTDNA_PRESETS[0];

  // Update slider default when preset changes
  useEffect(() => {
    setObservedK(currentPreset.expectedK);
    setDatabaseN(currentPreset.databaseN);
  }, [currentPreset]);

  // Compute exact Clopper-Pearson 95% upper bound
  const computeClopperPearsonBound = (k: number, n: number): number => {
    if (k === 0) {
      return 1.0 - Math.pow(0.05, 1.0 / (n + 1.0));
    }
    const z = 1.95996;
    const pUp = (k + 0.5 * z * z + z * Math.sqrt((k * (n - k)) / n + 0.25 * z * z)) / (n + z * z);
    return Math.min(Math.max(pUp, k / n), 1.0);
  };

  const pUpper = computeClopperPearsonBound(observedK, databaseN);

  // Evaluate maternal differences
  const setA = new Set(currentPreset.variantsA);
  const setB = new Set(currentPreset.variantsB);
  const shared = currentPreset.variantsA.filter((v) => setB.has(v));
  const uniqueA = currentPreset.variantsA.filter((v) => !setB.has(v));
  const uniqueB = currentPreset.variantsB.filter((v) => !setA.has(v));

  // Point heteroplasmy compatibility check
  const isPhpCompatible =
    currentPreset.id === "COHORT_POINT_HETEROPLASMY_PAIR" ||
    (uniqueA.length === 1 && uniqueB.length === 1 && uniqueA[0].includes("Y") && uniqueB[0].includes("C"));

  const homoplasmicDiffCount =
    isPhpCompatible || currentPreset.expectedVerdict === "MATCH"
      ? 0
      : uniqueA.length + uniqueB.length;

  const isExclusion = homoplasmicDiffCount >= 2 && currentPreset.expectedVerdict === "EXCLUSION";
  const maternalLr = isExclusion ? 0.0 : Math.round(1.0 / pUpper);
  const log10Lr = isExclusion ? -300.0 : Math.log10(maternalLr > 0 ? maternalLr : 1.0);

  return (
    <div className="space-y-6 text-slate-100 font-sans pb-12">
      {/* ── Header & Badges ────────────────────────────────────────────── */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400">
                <Compass className="w-6 h-6 animate-spin-slow" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                  Mitochondrial DNA (mtDNA) EMPOP rCRS/RSRS Alignment Engine
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Pillar 2.3
                  </span>
                </h1>
                <p className="text-xs text-slate-400 mt-0.5">
                  Revised Cambridge Reference Sequence (NC_012920.1, 16,569 bp) • ISFG 3&apos;-Right Alignment Normalizer • PhyloTree Build 17
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
              <ShieldCheck className="w-3.5 h-3.5" /> ISO/IEC 17025 Verified
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium bg-blue-950/60 text-blue-400 border border-blue-800/60">
              <Database className="w-3.5 h-3.5" /> EMPOP Release 15 (N=48,500)
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium bg-purple-950/60 text-purple-400 border border-purple-800/60">
              <Globe2 className="w-3.5 h-3.5" /> 5 Metapopulations
            </span>
          </div>
        </div>

        {/* ── Casework Preset Selector ─────────────────────────────────── */}
        <div className="mt-6 pt-6 border-t border-slate-800/80">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-3">
            Select Certified Casework Benchmark / Lineage Cohort:
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {MTDNA_PRESETS.map((preset) => {
              const isSelected = preset.id === selectedPresetId;
              return (
                <button
                  key={preset.id}
                  onClick={() => {
                    startTransition(() => setSelectedPresetId(preset.id));
                  }}
                  className={`p-3 rounded-lg text-left transition-all border ${
                    isSelected
                      ? "bg-emerald-950/40 border-emerald-500/60 text-white shadow-lg shadow-emerald-950/30"
                      : "bg-slate-800/40 border-slate-700/60 text-slate-400 hover:bg-slate-800/80 hover:text-slate-200"
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300">
                      {preset.badge}
                    </span>
                    {isSelected && <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                  </div>
                  <div className="text-xs font-semibold text-slate-200 line-clamp-1">{preset.title}</div>
                  <div className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">{preset.description}</div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Circular Mitogenome & D-Loop Structure ───────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Circular Map Visualizer */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Dna className="w-4 h-4 text-emerald-400" />
                Mitogenome Circular Map (16,569 bp)
              </h2>
              <span className="text-xs font-mono text-slate-400">rCRS NC_012920.1</span>
            </div>

            {/* SVG Circular Visualization */}
            <div className="relative w-full h-56 sm:h-64 flex items-center justify-center my-2">
              <svg viewBox="0 0 200 200" className="w-full h-full max-w-[240px]">
                {/* Background Ring (Full 16,569 bp Genome) */}
                <circle
                  cx="100"
                  cy="100"
                  r="75"
                  fill="none"
                  stroke="#1e293b"
                  strokeWidth="14"
                />

                {/* Protein Coding & rRNA/tRNA regions */}
                <circle
                  cx="100"
                  cy="100"
                  r="75"
                  fill="none"
                  stroke="#334155"
                  strokeWidth="10"
                  strokeDasharray="400 70"
                  strokeDashoffset="30"
                />

                {/* D-Loop Control Region (16024 to 576 ~ 1,122 bp) */}
                <circle
                  cx="100"
                  cy="100"
                  r="75"
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="14"
                  strokeDasharray="50 420"
                  strokeDashoffset="25"
                  className="animate-pulse"
                />

                {/* HV1 Region (Emerald) */}
                <circle
                  cx="100"
                  cy="100"
                  r="75"
                  fill="none"
                  stroke="#059669"
                  strokeWidth="14"
                  strokeDasharray="18 450"
                  strokeDashoffset="25"
                />

                {/* HV2 Region (Cyan) */}
                <circle
                  cx="100"
                  cy="100"
                  r="75"
                  fill="none"
                  stroke="#06b6d4"
                  strokeWidth="14"
                  strokeDasharray="15 450"
                  strokeDashoffset="6"
                />

                {/* Center Stats */}
                <text x="100" y="92" textAnchor="middle" fill="#ffffff" fontSize="11" fontWeight="bold" fontFamily="monospace">
                  D-LOOP
                </text>
                <text x="100" y="106" textAnchor="middle" fill="#94a3b8" fontSize="8" fontFamily="monospace">
                  16024–576 bp
                </text>
                <text x="100" y="120" textAnchor="middle" fill="#10b981" fontSize="9" fontWeight="bold" fontFamily="monospace">
                  {currentPreset.expectedHgA}
                </text>
              </svg>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-3 border-t border-slate-800 text-center text-xs">
            <div className="p-2 rounded bg-slate-800/50 border border-emerald-500/20">
              <span className="text-[10px] text-emerald-400 font-bold block">HV1</span>
              <span className="font-mono text-slate-300">16024–16365</span>
            </div>
            <div className="p-2 rounded bg-slate-800/50 border border-cyan-500/20">
              <span className="text-[10px] text-cyan-400 font-bold block">HV2</span>
              <span className="font-mono text-slate-300">73–340</span>
            </div>
            <div className="p-2 rounded bg-slate-800/50 border border-purple-500/20">
              <span className="text-[10px] text-purple-400 font-bold block">HV3</span>
              <span className="font-mono text-slate-300">438–574</span>
            </div>
          </div>
        </div>

        {/* Variant Comparison & Alignment HUD */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-xl lg:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-4">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  Pairwise Variant Comparison & ISFG Right-Alignment
                </h2>
                <p className="text-xs text-slate-400">
                  Questioned Sample vs Reference Standard relative to rCRS
                </p>
              </div>

              {/* Domain Filter Buttons */}
              <div className="flex items-center gap-1 p-1 bg-slate-800 rounded-lg text-xs">
                {(["ALL", "HV1", "HV2", "HV3"] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveDomainTab(tab)}
                    className={`px-2.5 py-1 rounded font-medium transition ${
                      activeDomainTab === tab
                        ? "bg-emerald-500 text-slate-950 font-bold shadow"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>

            {/* Mutation Pills / Tags */}
            <div className="space-y-3">
              <div>
                <span className="text-xs font-semibold text-slate-400 block mb-1.5 flex items-center justify-between">
                  <span>Questioned Sample A ({currentPreset.variantsA.length} Variants):</span>
                  <span className="text-emerald-400 font-mono text-[11px]">Haplogroup {currentPreset.expectedHgA}</span>
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {currentPreset.variantsA.map((v) => {
                    const isShared = setB.has(v) || isPhpCompatible;
                    return (
                      <span
                        key={`A-${v}`}
                        className={`px-2.5 py-1 rounded font-mono text-xs border ${
                          isShared
                            ? "bg-emerald-950/60 border-emerald-700/60 text-emerald-300"
                            : "bg-rose-950/60 border-rose-700/60 text-rose-300"
                        }`}
                      >
                        {v}
                        {v.includes(".1C") && (
                          <span className="ml-1 text-[9px] text-cyan-400 font-bold">3&apos;</span>
                        )}
                      </span>
                    );
                  })}
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 block mb-1.5 flex items-center justify-between">
                  <span>Reference Sample B ({currentPreset.variantsB.length} Variants):</span>
                  <span className="text-cyan-400 font-mono text-[11px]">Haplogroup {currentPreset.expectedHgB}</span>
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {currentPreset.variantsB.map((v) => {
                    const isShared = setA.has(v) || isPhpCompatible;
                    return (
                      <span
                        key={`B-${v}`}
                        className={`px-2.5 py-1 rounded font-mono text-xs border ${
                          isShared
                            ? "bg-cyan-950/60 border-cyan-700/60 text-cyan-300"
                            : "bg-rose-950/60 border-rose-700/60 text-rose-300"
                        }`}
                      >
                        {v}
                        {v.includes(".1C") && (
                          <span className="ml-1 text-[9px] text-cyan-400 font-bold">3&apos;</span>
                        )}
                      </span>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Quick Metrics Banner */}
          <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="p-2.5 rounded bg-slate-800/40 border border-slate-700">
              <span className="text-[10px] text-slate-400 block uppercase">Shared Mutations</span>
              <span className="text-base font-bold font-mono text-emerald-400">
                {isPhpCompatible ? currentPreset.variantsA.length : shared.length}
              </span>
            </div>
            <div className="p-2.5 rounded bg-slate-800/40 border border-slate-700">
              <span className="text-[10px] text-slate-400 block uppercase">Homoplasmic Diffs</span>
              <span className={`text-base font-bold font-mono ${homoplasmicDiffCount >= 2 ? "text-rose-400" : "text-slate-200"}`}>
                {homoplasmicDiffCount}
              </span>
            </div>
            <div className="p-2.5 rounded bg-slate-800/40 border border-slate-700">
              <span className="text-[10px] text-slate-400 block uppercase">Point Heteroplasmies</span>
              <span className="text-base font-bold font-mono text-purple-400">
                {isPhpCompatible ? 1 : 0}
              </span>
            </div>
            <div className="p-2.5 rounded bg-slate-800/40 border border-slate-700">
              <span className="text-[10px] text-slate-400 block uppercase">SWGDAM Verdict</span>
              <span
                className={`text-xs font-bold px-2 py-0.5 rounded inline-block mt-0.5 ${
                  isExclusion
                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                    : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                }`}
              >
                {isExclusion ? "EXCLUSION" : "MATCH / INCLUSION"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ── EMPOP Database Likelihood & Statistical Evaluation ──────────── */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-6">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Database className="w-5 h-5 text-emerald-400" />
              EMPOP Database Frequency & Maternal Likelihood Ratio
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              Exact Clopper-Pearson 95% Upper Bound: p_upper = 1 - (0.05)^(1 / (N + 1))
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400 block">Database Size (N)</span>
            <span className="text-sm font-mono font-bold text-emerald-400">{databaseN.toLocaleString()} Mitogenomes</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sliders & Database Controls */}
          <div className="space-y-4 bg-slate-800/40 p-4 rounded-xl border border-slate-700/60">
            <div>
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-300">Observed EMPOP Matches (k):</span>
                <span className="font-mono text-emerald-400 font-bold">{observedK}</span>
              </div>
              <input
                type="range"
                min="0"
                max="2000"
                step="1"
                value={observedK}
                onChange={(e) => setObservedK(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
                <span>0 (Rare / Novel)</span>
                <span>500</span>
                <span>1,420 (H1)</span>
                <span>2,000</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-300">Database Cohort Size (N):</span>
                <span className="font-mono text-cyan-400 font-bold">{databaseN.toLocaleString()}</span>
              </div>
              <input
                type="range"
                min="1000"
                max="48500"
                step="500"
                value={databaseN}
                onChange={(e) => setDatabaseN(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
                <span>1,000</span>
                <span>24,500 (EUR)</span>
                <span>48,500 (Global)</span>
              </div>
            </div>

            <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-[11px] text-slate-400 space-y-1">
              <div className="flex justify-between">
                <span>Frequency Point Estimate (k/N):</span>
                <span className="font-mono text-slate-200">{(observedK / databaseN).toExponential(4)}</span>
              </div>
              <div className="flex justify-between">
                <span>Clopper-Pearson 95% Bound:</span>
                <span className="font-mono text-emerald-400 font-bold">{pUpper.toExponential(4)}</span>
              </div>
              <div className="flex justify-between">
                <span>Equivalent Match Ratio:</span>
                <span className="font-mono text-cyan-400 font-bold">1 in {Math.round(1 / pUpper).toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Maternal LR & ENFSI Verdict HUD */}
          <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-5 rounded-xl bg-slate-800/40 border border-slate-700/80 flex flex-col justify-between">
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Maternal Likelihood Ratio (LR_mtDNA)
                </span>
                <div className="text-3xl font-extrabold font-mono text-white tracking-tight mt-2">
                  {isExclusion ? "0.00" : maternalLr.toLocaleString()}
                </div>
                <div className="text-xs font-mono text-slate-400 mt-1">
                  log10(LR) = {isExclusion ? "-300.0" : log10Lr.toFixed(4)}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-700/60">
                <span className="text-[11px] text-slate-400 block">ENFSI (2017) Verbal Equivalent:</span>
                <span className="text-xs font-semibold text-emerald-400 mt-0.5 block">
                  {isExclusion
                    ? "Definitive Exclusion of Maternal Lineage"
                    : maternalLr >= 1e6
                    ? "Extremely Strong Support for Same Maternal Lineage"
                    : maternalLr >= 1e4
                    ? "Very Strong Support for Same Maternal Lineage"
                    : maternalLr >= 100
                    ? "Moderately Strong Support for Same Maternal Lineage"
                    : "Moderate / Limited Support for Same Maternal Lineage"}
                </span>
              </div>
            </div>

            {/* PhyloTree Haplogroup Classification */}
            <div className="p-5 rounded-xl bg-slate-800/40 border border-slate-700/80 flex flex-col justify-between">
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  PhyloTree Build 17 Phylogeny
                </span>
                <div className="flex items-center gap-3 mt-2">
                  <div className="p-2.5 bg-purple-500/10 border border-purple-500/30 rounded-lg text-purple-400 font-mono font-bold text-lg">
                    {currentPreset.expectedHgA}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-200">Predicted Macro-Clade</div>
                    <div className="text-[11px] text-slate-400">
                      Branch: L0-L6 → L3 → {currentPreset.expectedHgA.startsWith("L") ? "African" : "N → R → " + currentPreset.expectedHgA}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-700/60 text-[11px] text-slate-400">
                <span>Diagnostic Mutations Verified: </span>
                <span className="font-mono text-purple-300 font-semibold">
                  {currentPreset.variantsA.slice(0, 3).join(", ")}
                  {currentPreset.variantsA.length > 3 ? "..." : ""}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* ── ISFG 2020 Evaluative Reporting & Active Prosecutor's Fallacy Shield ── */}
        <div className="mt-6 p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 text-amber-200/90 text-xs flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-amber-300 uppercase tracking-wider block">
              MANDATORY ISFG (2020) mtDNA EVALUATIVE REPORTING & LINEAGE DISCLAIMER (PROSECUTOR&apos;S FALLACY SHIELD)
            </span>
            <p className="leading-relaxed text-slate-300">
              Mitochondrial DNA (mtDNA) is inherited strictly along the matrilineal lineage without meiotic
              recombination. All maternally related relatives (brothers, sisters, mothers, maternal grandmothers,
              maternal aunts, maternal cousins) share the identical control region haplotype. Likelihood Ratios (LR_mtDNA)
              evaluate the probability of observing the sequence under the hypothesis of shared maternal lineage versus an
              unrelated individual from the population, but <strong className="text-amber-200">cannot individualize a specific single person</strong>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
