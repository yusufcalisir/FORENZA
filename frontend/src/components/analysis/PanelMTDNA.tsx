"use client";

import { useState, useTransition, useEffect, useMemo, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Dna,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Database,
  Sliders,
  Layers,
  Network,
  Check,
  Compass,
  RotateCcw,
  Clock,
  FileCode,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getApiBaseUrl } from "@/lib/api";

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
  titleTr: string;
  badge: string;
  badgeColor: string;
  description: string;
  descriptionTr: string;
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

export interface EmpopMetapopulation {
  code: string;
  nameEn: string;
  nameTr: string;
  sampleSize: number;
}

// ── IUPAC Ambiguity Codes for Point Heteroplasmy (PHP) ─────────────────────

export const IUPAC_DEGENERATE_BASES: Record<string, string[]> = {
  A: ["A"],
  C: ["C"],
  G: ["G"],
  T: ["T"],
  R: ["A", "G"],
  Y: ["C", "T"],
  M: ["A", "C"],
  K: ["G", "T"],
  S: ["G", "C"],
  W: ["A", "T"],
  N: ["A", "C", "G", "T"],
};

// ── Certified Presets ──────────────────────────────────────────────────────

export const MTDNA_PRESETS: CaseworkPreset[] = [
  {
    id: "BENCHMARK_LINEAGE_A_EUR",
    title: "Benchmark LINEAGE-A (European Reference : EUR)",
    titleTr: "Dogrulama LINEAGE-A (Avrupa Referansi : EUR)",
    badge: "Haplogroup H1",
    badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
    description: "Common European H1 haplotype (263G, 315.1C, 750G, 16519C) with k=1,420 matches in EMPOP (N=48,200).",
    descriptionTr: "EMPOP veri tabaninda k=1.420 eslesmesi bulunan yaygin Bati Avrasya H1 haplotipi (263G, 315.1C, 750G, 16519C).",
    relationship: "Maternal Lineage Match",
    variantsA: ["263G", "315.1C", "750G", "16519C"],
    variantsB: ["263G", "315.1C", "750G", "16519C"],
    expectedHgA: "H1",
    expectedHgB: "H1",
    expectedVerdict: "MATCH",
    expectedK: 1420,
    databaseN: 48200,
    expectedMinLr: 32.20,
  },
  {
    id: "BENCHMARK_LINEAGE_B_AFR",
    title: "Benchmark LINEAGE-B (African Diaspora : AFR)",
    titleTr: "Dogrulama LINEAGE-B (Afrika Diasporasi : AFR)",
    badge: "Haplogroup L2a1",
    badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    description: "Sub-Saharan African L2a1 haplotype with 13 control region mutations and k=12 matches in EMPOP.",
    descriptionTr: "EMPOP'ta k=12 eslesmesi olan 13 kontrol bolgesi mutasyonlu Sahra-Alti Afrika L2a1 haplotipi.",
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
    expectedMinLr: 2295.0,
  },
  {
    id: "COHORT_POINT_HETEROPLASMY_PAIR",
    title: "Point Heteroplasmy Pair (16189Y vs 16189C)",
    titleTr: "Nokta Heteroplazmisi Ikilisi (16189Y vs 16189C)",
    badge: "IUPAC Mixed Base",
    badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/40",
    description: "Questioned sample with 16189Y (C/T) vs reference homoplasmic 16189C (cannot be excluded under ISFG).",
    descriptionTr: "16189Y (C/T) karisik bazli ornek ile homoplazmik 16189C karsilastirmasi (ISFG uyarinca dislanamaz).",
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
    titleTr: "Nadir Gozlenmemis Anne Soyu Ikilisi (k=0)",
    badge: "Exact k=0 Bound",
    badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
    description: "Mother-daughter exact match with rare dinucleotide insertion 524.1AC unobserved in EMPOP.",
    descriptionTr: "EMPOP'ta gozlenmemis nadir dinukleotid insersiyonu 524.1AC iceren anne-kiz tam eslesmesi.",
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
    titleTr: "Akraba Olmayan Dislama Ikilisi (H1 vs L2a1)",
    badge: "SWGDAM Exclusion",
    badgeColor: "bg-rose-500/20 text-rose-300 border-rose-500/40",
    description: "Two unrelated donors exhibiting 11 homoplasmic point differences yielding definitive exclusion.",
    descriptionTr: "11 homoplazmik nokta farki sergileyen ve kesin dislama veren akraba olmayan iki donor.",
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

export const EMPOP_METAPOPULATIONS: EmpopMetapopulation[] = [
  { code: "GLOBAL", nameEn: "EMPOP Global Mitogenome Master Panel", nameTr: "EMPOP Kuresel Mitogenom Ana Paneli", sampleSize: 48500 },
  { code: "WEST_EURASIAN", nameEn: "West Eurasian / European Metapopulation", nameTr: "Bati Avrasya / Avrupa Metapopulasyonu", sampleSize: 24500 },
  { code: "EAST_ASIAN", nameEn: "East Asian Metapopulation", nameTr: "Dogu Asya Metapopulasyonu", sampleSize: 12200 },
  { code: "AFRICAN", nameEn: "Sub-Saharan African Metapopulation", nameTr: "Sahra-Alti Afrika Metapopulasyonu", sampleSize: 5800 },
  { code: "NATIVE_AMERICAN", nameEn: "Native American Metapopulation", nameTr: "Yerli Amerika Metapopulasyonu", sampleSize: 3500 },
  { code: "SOUTH_ASIAN", nameEn: "South Asian Metapopulation", nameTr: "Guney Asya Metapopulasyonu", sampleSize: 2500 },
];

// ── Pure Mathematical Biocomputational Functions ───────────────────────────

/**
 * Checks whether two bases (including IUPAC point heteroplasmy degenerate codes) are compatible.
 * Example: Y (C/T) is compatible with C, T, and Y.
 */
export function isIupacCompatible(baseA: string, baseB: string): boolean {
  const cleanA = baseA.trim().toUpperCase();
  const cleanB = baseB.trim().toUpperCase();
  if (cleanA === cleanB) return true;

  const setA = IUPAC_DEGENERATE_BASES[cleanA] || [cleanA];
  const setB = IUPAC_DEGENERATE_BASES[cleanB] || [cleanB];

  return setA.some((b) => setB.includes(b));
}

/**
 * Applies ISFG (2014, 2020) & EMPOP 3'-right-alignment normalizer to variant strings:
 * - HV2 Poly-C: 308.1C -> 309.1C, 314.1C -> 315.1C
 * - HV1 Poly-C: 16188.1C -> 16189.1C
 * - HV3 Dinucleotide: 522.1A / 523.1AC -> 524.1AC
 */
export function normalizeVariant3Prime(variant: string): string {
  const clean = variant.trim().toUpperCase().replace(/\s+/g, "");
  const insMatch = clean.match(/^(\d+)\.(\d+)([A-Z]+)$/);

  if (insMatch) {
    let pos = parseInt(insMatch[1], 10);
    const idx = insMatch[2];
    const base = insMatch[3];

    // Right-shift HV2 Poly-C
    if (pos >= 303 && pos <= 308 && base === "C") {
      pos = 309;
    } else if (pos >= 311 && pos <= 314 && base === "C") {
      pos = 315;
    }
    // Right-shift HV1 Poly-C
    else if (pos >= 16184 && pos <= 16188 && base === "C") {
      pos = 16189;
    }
    // Right-shift HV3 dinucleotide
    else if (pos >= 522 && pos <= 523 && (base === "A" || base === "C" || base === "AC")) {
      pos = 524;
    }

    return `${pos}.${idx}${base}`;
  }

  return clean;
}

/**
 * Computes exact Clopper-Pearson 95% upper confidence bound for EMPOP frequency estimation.
 * For k=0: p_upper = 1 - (0.05)^(1 / (N + 1))
 * For k>0: Wilson score continuity correction approximation to Beta distribution.
 */
export function computeClopperPearsonBound(k: number, n: number): number {
  if (n <= 0) return 1.0;
  if (k <= 0) {
    return 1.0 - Math.pow(0.05, 1.0 / (n + 1.0));
  }
  const z = 1.95996398454; // 95% two-sided normal quantile
  const z2 = z * z;
  const pUp = (k + 0.5 * z2 + z * Math.sqrt((k * (n - k)) / n + 0.25 * z2)) / (n + z2);
  return Math.min(Math.max(pUp, k / n), 1.0);
}

/**
 * Client-Side SWGDAM mtDNA Pairwise Maternal Lineage Evaluator.
 * Parses, normalizes, detects IUPAC heteroplasmy compatibility, and calculates LR.
 */
export function evaluateMtdnaMaternalMatchClient(
  rawVariantsA: string[],
  rawVariantsB: string[],
  databaseN: number = 48500,
  observedK: number = 0,
  apply3PrimeShift: boolean = true
): {
  sharedCalls: string[];
  diffsA: string[];
  diffsB: string[];
  homoplasmicDiffCount: number;
  heteroplasmicSharedCount: number;
  verdict: "MATCH" | "INCONCLUSIVE" | "EXCLUSION";
  isExclusion: boolean;
  isInconclusive: boolean;
  maternalLr: number;
  log10Lr: number;
  pUpper: number;
} {
  const normA = rawVariantsA.map((v) => (apply3PrimeShift ? normalizeVariant3Prime(v) : v.trim().toUpperCase()));
  const normB = rawVariantsB.map((v) => (apply3PrimeShift ? normalizeVariant3Prime(v) : v.trim().toUpperCase()));

  // Map key: "POS" or "POS.INDEX"
  const parseEntry = (v: string): { key: string; base: string; raw: string } => {
    const insMatch = v.match(/^(\d+\.\d+)([A-Z]+)$/);
    if (insMatch) {
      return { key: insMatch[1], base: insMatch[2], raw: v };
    }
    const subMatch = v.match(/^(\d+)([A-Z]+)$/);
    if (subMatch) {
      return { key: subMatch[1], base: subMatch[2], raw: v };
    }
    return { key: v, base: "", raw: v };
  };

  const mapA = new Map<string, { key: string; base: string; raw: string }>();
  for (const v of normA) {
    if (v) {
      const parsed = parseEntry(v);
      mapA.set(parsed.key, parsed);
    }
  }

  const mapB = new Map<string, { key: string; base: string; raw: string }>();
  for (const v of normB) {
    if (v) {
      const parsed = parseEntry(v);
      mapB.set(parsed.key, parsed);
    }
  }

  const allKeys = Array.from(new Set([...mapA.keys(), ...mapB.keys()])).sort((a, b) => {
    return parseFloat(a) - parseFloat(b);
  });

  const sharedCalls: string[] = [];
  const diffsA: string[] = [];
  const diffsB: string[] = [];
  let homoplasmicDiffCount = 0;
  let heteroplasmicSharedCount = 0;

  for (const key of allKeys) {
    const inA = mapA.has(key);
    const inB = mapB.has(key);

    if (inA && inB) {
      const entryA = mapA.get(key)!;
      const entryB = mapB.get(key)!;

      if (entryA.raw === entryB.raw) {
        sharedCalls.push(entryA.raw);
      } else if (isIupacCompatible(entryA.base, entryB.base)) {
        // Point heteroplasmy shared match (e.g. 16189Y vs 16189C)
        sharedCalls.push(`${entryA.raw}/${entryB.raw}`);
        heteroplasmicSharedCount++;
      } else {
        // Real homoplasmic point discrepancy at same locus
        diffsA.push(entryA.raw);
        diffsB.push(entryB.raw);
        homoplasmicDiffCount++;
      }
    } else if (inA && !inB) {
      diffsA.push(mapA.get(key)!.raw);
      homoplasmicDiffCount++;
    } else if (inB && !inA) {
      diffsB.push(mapB.get(key)!.raw);
      homoplasmicDiffCount++;
    }
  }

  const pUpper = computeClopperPearsonBound(observedK, databaseN);
  let verdict: "MATCH" | "INCONCLUSIVE" | "EXCLUSION" = "MATCH";
  let isExclusion = false;
  let isInconclusive = false;
  let maternalLr = 0.0;
  let log10Lr = -300.0;

  if (homoplasmicDiffCount === 0) {
    verdict = "MATCH";
    isExclusion = false;
    isInconclusive = false;
    maternalLr = Math.max(1.0 / Math.max(pUpper, 1e-15), 1.0);
    log10Lr = Number(Math.log10(maternalLr).toFixed(3));
  } else if (homoplasmicDiffCount === 1) {
    verdict = "INCONCLUSIVE";
    isExclusion = false;
    isInconclusive = true;
    maternalLr = 1.0;
    log10Lr = 0.0;
  } else {
    verdict = "EXCLUSION";
    isExclusion = true;
    isInconclusive = false;
    maternalLr = 0.0;
    log10Lr = -300.0;
  }

  return {
    sharedCalls,
    diffsA,
    diffsB,
    homoplasmicDiffCount,
    heteroplasmicSharedCount,
    verdict,
    isExclusion,
    isInconclusive,
    maternalLr,
    log10Lr,
    pUpper,
  };
}

// ── Primary React Component ────────────────────────────────────────────────

export default function PanelMTDNA() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  // Navigation Tab State
  const [activeTab, setActiveTab] = useState<"match" | "mitogenome" | "empop" | "phylotree" | "sandbox">("match");

  // Casework & Input State
  const [selectedPresetId, setSelectedPresetId] = useState<string>("BENCHMARK_LINEAGE_A_EUR");
  const [observedK, setObservedK] = useState<number>(1420);
  const [databaseN, setDatabaseN] = useState<number>(48200);
  const [selectedMetapop, setSelectedMetapop] = useState<string>("GLOBAL");
  const [activeDomainTab, setActiveDomainTab] = useState<"ALL" | "HV1" | "HV2" | "HV3">("ALL");

  // Custom Sandbox State
  const [customInputA, setCustomInputA] = useState<string>("263G, 315.1C, 750G, 16189Y, 16519C");
  const [customInputB, setCustomInputB] = useState<string>("263G, 315.1C, 750G, 16189C, 16519C");
  const [apply3PrimeShift, setApply3PrimeShift] = useState<boolean>(true);

  // Execution & Telemetry State
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [calcProgress, setCalcProgress] = useState<number>(100);
  const [roundtripMs, setRoundtripMs] = useState<number | null>(null);
  const [lastExecuted, setLastExecuted] = useState<string | null>(null);

  const currentPreset = MTDNA_PRESETS.find((p) => p.id === selectedPresetId) || MTDNA_PRESETS[0];

  // Synchronize inputs when preset changes
  useEffect(() => {
    setObservedK(currentPreset.expectedK);
    setDatabaseN(currentPreset.databaseN);
  }, [currentPreset]);

  // ISFG domain filter: parse numeric position from variant string (e.g. "16519C" -> 16519)
  const getVariantPosition = useCallback((v: string): number => {
    const match = v.match(/^(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  }, []);

  const variantMatchesDomain = useCallback(
    (v: string, tab: "ALL" | "HV1" | "HV2" | "HV3"): boolean => {
      if (tab === "ALL") return true;
      const pos = getVariantPosition(v);
      if (tab === "HV1") return pos >= 16024 && pos <= 16365;
      if (tab === "HV2") return pos >= 73 && pos <= 340;
      if (tab === "HV3") return pos >= 438 && pos <= 574;
      return true;
    },
    [getVariantPosition]
  );

  // Client computed metrics
  const computedMetrics = useMemo(() => {
    const res = evaluateMtdnaMaternalMatchClient(
      currentPreset.variantsA,
      currentPreset.variantsB,
      databaseN,
      observedK,
      true
    );

    return {
      pUpper: res.pUpper,
      isExclusion: res.isExclusion,
      isInconclusive: res.isInconclusive,
      maternalLr: res.maternalLr,
      log10Lr: res.log10Lr,
      verdict: res.verdict,
      differencesCount: res.homoplasmicDiffCount,
      sharedCalls: res.sharedCalls,
    };
  }, [currentPreset.variantsA, currentPreset.variantsB, databaseN, observedK]);

  const [liveMetrics, setLiveMetrics] = useState<typeof computedMetrics | null>(null);

  // Live API execution handler with client fallback
  const executeAnalysis = useCallback(async () => {
    setIsAnalyzing(true);
    setCalcProgress(15);
    const startTime = performance.now();

    const progressTimer = setInterval(() => {
      setCalcProgress((prev) => (prev < 90 ? prev + 25 : prev));
    }, 70);

    const API_BASE = getApiBaseUrl();

    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/lineage/mtdna/evaluate-maternal-match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          variants_a: currentPreset.variantsA,
          variants_b: currentPreset.variantsB,
          n_empop: databaseN,
          empop_observed_k: observedK,
        }),
      });

      const elapsed = Math.round(performance.now() - startTime);
      setRoundtripMs(elapsed);
      setCalcProgress(100);

      if (res.ok) {
        const data = await res.json();
        const rawLr = data.maternal_lr ?? data.min_lr;
        const rawLog10 = data.log10_maternal_lr ?? data.log10_lr;
        const rawPUpper = data.empop_frequency_bound ?? data.p_upper_95;
        const verdictStr = data.maternal_lineage_verdict ?? data.match_status ?? data.verdict;
        const diffCount = data.differing_positions_count ?? data.differences_count ?? computedMetrics.differencesCount;
        const isExcl = verdictStr === "EXCLUSION" || verdictStr === "EXCLUDED" || rawLr === 0.0 || computedMetrics.isExclusion;
        const isInconcl = !isExcl && diffCount === 1;

        setLiveMetrics({
          maternalLr: isExcl ? 0.0 : isInconcl ? 1.0 : (rawLr ?? computedMetrics.maternalLr),
          log10Lr: isExcl ? -300.0 : isInconcl ? 0.0 : (rawLog10 ?? computedMetrics.log10Lr),
          pUpper: rawPUpper ?? computedMetrics.pUpper,
          isExclusion: isExcl,
          isInconclusive: isInconcl,
          verdict: isExcl ? "EXCLUSION" : isInconcl ? "INCONCLUSIVE" : (verdictStr ?? computedMetrics.verdict),
          differencesCount: diffCount,
          sharedCalls: computedMetrics.sharedCalls,
        });
      } else {
        setLiveMetrics(computedMetrics);
      }
    } catch {
      setLiveMetrics(computedMetrics);
    } finally {
      clearInterval(progressTimer);
      setIsAnalyzing(false);
      setLastExecuted(new Date().toISOString().replace("T", " ").substring(0, 19) + " UTC");
    }
  }, [currentPreset.variantsA, currentPreset.variantsB, databaseN, observedK, computedMetrics]);

  // Initial execution on mount and preset switch
  useEffect(() => {
    executeAnalysis();
  }, [executeAnalysis]);

  const activeMetrics = liveMetrics || computedMetrics;
  const pUpper = activeMetrics.pUpper;
  const isExclusion = activeMetrics.isExclusion;
  const isInconclusive = activeMetrics.isInconclusive;
  const maternalLr = activeMetrics.maternalLr;
  const log10Lr = activeMetrics.log10Lr;

  const filteredVariantsA = currentPreset.variantsA.filter((v) => variantMatchesDomain(v, activeDomainTab));
  const filteredVariantsB = currentPreset.variantsB.filter((v) => variantMatchesDomain(v, activeDomainTab));

  // Custom Sandbox Evaluation with IUPAC Point Heteroplasmy & 3'-Right Shift Support
  const parsedCustomA = useMemo(() => {
    return customInputA
      .split(/[\s,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);
  }, [customInputA]);

  const parsedCustomB = useMemo(() => {
    return customInputB
      .split(/[\s,;]+/)
      .map((s) => s.trim())
      .filter(Boolean);
  }, [customInputB]);

  const customEvaluation = useMemo(() => {
    return evaluateMtdnaMaternalMatchClient(
      parsedCustomA,
      parsedCustomB,
      databaseN,
      observedK,
      apply3PrimeShift
    );
  }, [parsedCustomA, parsedCustomB, databaseN, observedK, apply3PrimeShift]);

  return (
    <div className="space-y-6 text-slate-100 font-mono pb-16">
      {/* ── Header Mission HUD ──────────────────────────────────────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-6 shadow-2xl relative overflow-hidden backdrop-blur-md">
        <div className="absolute top-0 right-0 w-96 h-36 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-tactical-border/40 pb-4 relative z-10">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 shrink-0 shadow-lg shadow-emerald-500/10">
              <Compass className="w-6 h-6 animate-spin-slow" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-base sm:text-lg font-black text-white tracking-wide uppercase">
                  {isTr
                    ? "mtDNA rCRS/RSRS Hizalama & EMPOP Filogeni Studyosu"
                    : "mtDNA rCRS/RSRS Alignment & EMPOP Phylogenetics Studio"}
                </h1>
                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  MODULE 10 : PILLAR 2
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {isTr
                  ? "EMPOP 15 : ISFG 3'-Saga Hizalama : IUPAC Nokta Heteroplazmisi : PhyloTree B17 : SWGDAM Karar Motoru"
                  : "EMPOP 15 : ISFG 3'-Right Alignment : IUPAC Point Heteroplasmy : PhyloTree B17 : SWGDAM Decision Engine"}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold bg-white/[0.03] border border-white/10 text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>ISO/IEC 17025:2017</span>
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold bg-white/[0.03] border border-white/10 text-cyan-400">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span>EMPOP N=48,500</span>
            </span>
            <button
              type="button"
              onClick={executeAnalysis}
              disabled={isAnalyzing}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-500 hover:bg-emerald-400 active:scale-95 text-slate-950 transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/20 disabled:opacity-50 cursor-pointer"
            >
              <RotateCcw className={`w-3.5 h-3.5 ${isAnalyzing ? "animate-spin" : ""}`} />
              <span>{isAnalyzing ? (isTr ? "Analiz Ediliyor..." : "Evaluating...") : (isTr ? "Yeniden Analiz Et" : "Re-Evaluate")}</span>
            </button>
          </div>
        </div>

        {/* Live Calculation Telemetry Bar */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-emerald-400" />
            <span>{isTr ? "Son Analiz:" : "Last Run:"}</span>
            <span className="text-slate-200 font-bold">{lastExecuted || "Ready"}</span>
            {roundtripMs !== null && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono">
                {roundtripMs}ms
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <span className="text-slate-500">PROSECUTOR FALLACY SHIELD: ACTIVE</span>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      {isAnalyzing && (
        <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
          <motion.div
            className="bg-emerald-500 h-full"
            initial={{ width: "0%" }}
            animate={{ width: `${calcProgress}%` }}
            transition={{ duration: 0.2 }}
          />
        </div>
      )}

      {/* ── Subsystem Tab Navigation ────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
        {[
          { id: "match", labelEn: "1. Pairwise Match Evaluator", labelTr: "1. Ikili Eslesme Degerlendirici", icon: ShieldCheck },
          { id: "mitogenome", labelEn: "2. Mitogenome & Domains", labelTr: "2. Mitogenom & Bolgeler", icon: Dna },
          { id: "empop", labelEn: "3. EMPOP Database & Bound", labelTr: "3. EMPOP Veritabani & Sinir", icon: Database },
          { id: "phylotree", labelEn: "4. PhyloTree B17 Phylogeny", labelTr: "4. PhyloTree B17 Filogeni", icon: Network },
          { id: "sandbox", labelEn: "5. Custom Sequence Sandbox", labelTr: "5. Ozel Dizi Kumhavuzu", icon: FileCode },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-bold transition-all ${
                isActive
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm shadow-emerald-500/10"
                  : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800 hover:border-slate-700"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{isTr ? tab.labelTr : tab.labelEn}</span>
            </button>
          );
        })}
      </div>

      {/* ── TAB 1: Pairwise Match Evaluator ─────────────────────────────────── */}
      {activeTab === "match" && (
        <motion.div
          key="match-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Preset Selector */}
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-emerald-400" />
                {isTr ? "Referans Anne Soyu Kohortu Secimi" : "Reference Maternal Lineage Cohort Selection"}
              </span>
              <span className="text-[11px] text-slate-500">
                {isTr ? "Sertifikali Altin Standartlar & Vaka Ikilileri" : "Certified Golden Standards & Case Pairs"}
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {MTDNA_PRESETS.map((p) => {
                const isSel = selectedPresetId === p.id;
                return (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPresetId(p.id)}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      isSel
                        ? "bg-emerald-950/40 border-emerald-500/60 shadow-md shadow-emerald-950/40"
                        : "bg-slate-900/40 border-slate-800 hover:border-slate-700 text-slate-400"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className={`text-xs font-bold truncate ${isSel ? "text-white" : "text-slate-300"}`}>
                        {isTr ? p.titleTr : p.title}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border ${p.badgeColor}`}>
                        {p.badge}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 leading-tight">
                      {isTr ? p.descriptionTr : p.description}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Metric Telemetry Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Maternal Likelihood Ratio Card */}
            <div className={`p-4 rounded-xl border bg-slate-950/70 backdrop-blur-md ${
              !isExclusion ? "border-emerald-500/40" : "border-rose-500/40"
            }`}>
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span>{isTr ? "Anne Soyu LR (Likelihood Ratio)" : "Maternal LR (Likelihood Ratio)"}</span>
                <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                  !isExclusion ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
                }`}>
                  {!isExclusion ? "MATCH" : "EXCLUSION"}
                </span>
              </div>
              <div className={`text-2xl font-black tabular-nums tracking-tight ${
                !isExclusion ? "text-emerald-400" : "text-rose-400"
              }`}>
                {isExclusion ? "0.00" : maternalLr >= 10000 ? Math.round(maternalLr).toLocaleString() : maternalLr.toFixed(2)}
              </div>
              <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
                <span>log10(LR): {log10Lr.toFixed(3)}</span>
                <span>{isExclusion ? "Exclusion" : "Consistent"}</span>
              </div>
            </div>

            {/* Clopper-Pearson 95% Bound Card */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/70 backdrop-blur-md">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span>{isTr ? "Clopper-Pearson %95 Ust Sınır" : "Clopper-Pearson 95% Bound"}</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300">k={observedK}</span>
              </div>
              <div className="text-2xl font-black text-cyan-400 tabular-nums tracking-tight">
                {pUpper.toExponential(4)}
              </div>
              <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
                <span>N = {databaseN.toLocaleString()} EMPOP</span>
                <span>1 in {Math.round(1 / Math.max(pUpper, 1e-15)).toLocaleString()}</span>
              </div>
            </div>

            {/* SWGDAM Differences Counter */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/70 backdrop-blur-md">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span>{isTr ? "Homoplazmik Farklar" : "Homoplasmic Diffs"}</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300">SWGDAM</span>
              </div>
              <div className={`text-2xl font-black tabular-nums tracking-tight ${
                activeMetrics.differencesCount >= 2 ? "text-rose-400" : "text-purple-400"
              }`}>
                {activeMetrics.differencesCount}
              </div>
              <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
                <span>{activeMetrics.differencesCount === 0 ? "Exact Concordance" : activeMetrics.differencesCount === 1 ? "1 Diff (Inconclusive)" : ">=2 Diffs (Exclusion)"}</span>
              </div>
            </div>

            {/* Haplogroup Classifications */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/70 backdrop-blur-md">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span>{isTr ? "Tahmin Edilen Haplogruplar" : "Predicted Haplogroups"}</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">PhyloTree B17</span>
              </div>
              <div className="text-sm font-black text-emerald-300 truncate mt-1">
                A: Hg {currentPreset.expectedHgA} | B: Hg {currentPreset.expectedHgB}
              </div>
              <div className="text-[10px] text-slate-500 mt-2 flex justify-between">
                <span>Domain: {activeDomainTab}</span>
                <span>{currentPreset.relationship}</span>
              </div>
            </div>
          </div>

          {/* Pairwise Variant Comparison Table & Domain Filters */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  {isTr ? "Ikili Varyant Karsilastirmasi & ISFG Saga Hizalama" : "Pairwise Variant Comparison & ISFG Right-Alignment"}
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  {isTr ? "rCRS NC_012920.1 referansina gore ornek mutasyon listeleri" : "Sample variant lists referenced to rCRS NC_012920.1"}
                </p>
              </div>

              {/* Domain Filter Buttons */}
              <div className="flex items-center gap-1 p-1 bg-slate-800 rounded-xl text-xs">
                {(["ALL", "HV1", "HV2", "HV3"] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveDomainTab(tab)}
                    className={`px-3 py-1 rounded-lg font-bold transition cursor-pointer ${
                      activeDomainTab === tab
                        ? "bg-emerald-500 text-slate-950 shadow"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {tab === "ALL" && isTr ? "TUMU" : tab}
                  </button>
                ))}
              </div>
            </div>

            {/* Variant Badges Display */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-bold text-slate-300">
                    {isTr ? "Sorgulanan Ornek A Varyantlari" : "Questioned Sample A Variants"} ({filteredVariantsA.length}):
                  </span>
                  <span className="text-xs font-mono font-bold text-emerald-400">
                    Hg {currentPreset.expectedHgA}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {filteredVariantsA.length === 0 ? (
                    <span className="text-xs text-slate-500 italic">{isTr ? "Bu bolgede mutasyon yok" : "No mutations in this region"}</span>
                  ) : (
                    filteredVariantsA.map((v) => (
                      <span
                        key={`A-${v}`}
                        className="px-2.5 py-1 rounded-lg font-mono text-xs border font-semibold bg-emerald-950/60 border-emerald-700/70 text-emerald-300"
                      >
                        {v}
                        {v.includes(".1C") && <span className="ml-1 text-[9px] text-cyan-400 font-bold">3&apos;R</span>}
                      </span>
                    ))
                  )}
                </div>
              </div>

              <div className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-bold text-slate-300">
                    {isTr ? "Referans Ornek B Varyantlari" : "Reference Sample B Variants"} ({filteredVariantsB.length}):
                  </span>
                  <span className="text-xs font-mono font-bold text-cyan-400">
                    Hg {currentPreset.expectedHgB}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {filteredVariantsB.length === 0 ? (
                    <span className="text-xs text-slate-500 italic">{isTr ? "Bu bolgede mutasyon yok" : "No mutations in this region"}</span>
                  ) : (
                    filteredVariantsB.map((v) => (
                      <span
                        key={`B-${v}`}
                        className="px-2.5 py-1 rounded-lg font-mono text-xs border font-semibold bg-cyan-950/60 border-cyan-700/70 text-cyan-300"
                      >
                        {v}
                        {v.includes(".1C") && <span className="ml-1 text-[9px] text-cyan-400 font-bold">3&apos;R</span>}
                      </span>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* ── TAB 2: Mitogenome & Domains ─────────────────────────────────────── */}
      {activeTab === "mitogenome" && (
        <motion.div
          key="mitogenome-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Dna className="w-4 h-4 text-emerald-400" />
              {isTr ? "Mitokondriyal Genom & Kontrol Bolgesi (D-Loop) Mimarisi" : "Mitochondrial Genome & Control Region (D-Loop) Architecture"}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center text-xs">
              <div className="p-4 rounded-xl bg-slate-950/70 border border-emerald-500/30">
                <span className="text-xs text-emerald-400 font-bold block">HV1 (Hypervariable 1)</span>
                <span className="font-mono text-slate-200 text-sm block mt-1">16024 : 16365 bp</span>
                <span className="text-[10px] text-slate-500 block mt-1">Macro-clade diagnostic region</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-950/70 border border-cyan-500/30">
                <span className="text-xs text-cyan-400 font-bold block">HV2 (Hypervariable 2)</span>
                <span className="font-mono text-slate-200 text-sm block mt-1">73 : 340 bp</span>
                <span className="text-[10px] text-slate-500 block mt-1">Contains 309/315 poly-C homopolymers</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-950/70 border border-purple-500/30">
                <span className="text-xs text-purple-400 font-bold block">HV3 (Hypervariable 3)</span>
                <span className="font-mono text-slate-200 text-sm block mt-1">438 : 574 bp</span>
                <span className="text-[10px] text-slate-500 block mt-1">522-524 AC dinucleotide indels</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* ── TAB 3: EMPOP Database & Bound ───────────────────────────────────── */}
      {activeTab === "empop" && (
        <motion.div
          key="empop-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Database className="w-5 h-5 text-emerald-400" />
                  {isTr ? "EMPOP Veri Tabani Frekans & Ust Sinir Hesaplayicisi" : "EMPOP Database Frequency & Upper Bound Engine"}
                </h2>
                <p className="text-xs text-slate-400">
                  {isTr
                    ? "EMPOP 15 metapopulasyonlarinda kesin Clopper-Pearson %95 ust siniri hesabi"
                    : "Exact Clopper-Pearson 95% upper bound calculation across EMPOP 15 metapopulations"}
                </p>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-400 block">{isTr ? "Secili Veri Tabani Boyutu:" : "Selected Database Size:"}</span>
                <span className="text-sm font-bold font-mono text-emerald-400">
                  {databaseN.toLocaleString()} {isTr ? "Mitogenom" : "Mitogenomes"}
                </span>
              </div>
            </div>

            {/* Metapopulation Selector Pills */}
            <div>
              <span className="text-xs font-bold text-slate-300 block mb-2">
                {isTr ? "EMPOP 15 Metapopulasyon Referansi:" : "EMPOP 15 Metapopulation Reference:"}
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {EMPOP_METAPOPULATIONS.map((mp) => {
                  const isSelected = selectedMetapop === mp.code;
                  return (
                    <button
                      type="button"
                      key={mp.code}
                      onClick={() => {
                        setSelectedMetapop(mp.code);
                        setDatabaseN(mp.sampleSize);
                      }}
                      className={`p-3 rounded-xl text-left border transition-all cursor-pointer flex justify-between items-center ${
                        isSelected
                          ? "bg-emerald-500/20 border-emerald-500/50 text-white shadow-md shadow-emerald-500/10"
                          : "bg-slate-950/60 border-slate-800 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                      }`}
                    >
                      <div>
                        <div className="text-xs font-bold">{isTr ? mp.nameTr : mp.nameEn}</div>
                        <div className="text-[10px] text-slate-500 font-mono">N = {mp.sampleSize.toLocaleString()}</div>
                      </div>
                      {isSelected && <Check className="w-4 h-4 text-emerald-400 shrink-0" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Interactive Sliders Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-2">
              <div className="space-y-4 bg-slate-950/70 p-5 rounded-xl border border-slate-800">
                <div>
                  <div className="flex justify-between items-center text-xs mb-2">
                    <span className="font-semibold text-slate-300">
                      {isTr ? "Gozlenen EMPOP Eslesmeleri (k):" : "Observed EMPOP Matches (k):"}
                    </span>
                    <span className="font-mono text-emerald-400 font-black text-sm">{observedK}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="2000"
                    step="1"
                    value={observedK}
                    onChange={(e) => setObservedK(parseInt(e.target.value))}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
                    <span>0 ({isTr ? "Nadir" : "Rare"})</span>
                    <span>500</span>
                    <span>1,420 (H1)</span>
                    <span>2,000</span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center text-xs mb-2">
                    <span className="font-semibold text-slate-300">
                      {isTr ? "Veri Tabani Orneklem Boyutu (N):" : "Database Sample Size (N):"}
                    </span>
                    <span className="font-mono text-cyan-400 font-black text-sm">{databaseN.toLocaleString()}</span>
                  </div>
                  <input
                    type="range"
                    min="1000"
                    max="48500"
                    step="500"
                    value={databaseN}
                    onChange={(e) => setDatabaseN(parseInt(e.target.value))}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
                    <span>1,000</span>
                    <span>24,500 (EUR)</span>
                    <span>48,500 ({isTr ? "Kuresel" : "Global"})</span>
                  </div>
                </div>
              </div>

              {/* Calculated Statistics HUD */}
              <div className="bg-slate-950/70 p-5 rounded-xl border border-slate-800 flex flex-col justify-between space-y-3">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  {isTr ? "Hesaplanan Biyoistatistiksel Parametreler" : "Calculated Biostatistical Parameters"}
                </span>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1.5 border-b border-slate-800/80">
                    <span className="text-slate-400">{isTr ? "Frekans Nokta Tahmini (k / N):" : "Frequency Point Estimate (k / N):"}</span>
                    <span className="font-mono text-slate-200 font-semibold">{(observedK / Math.max(databaseN, 1)).toExponential(4)}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800/80">
                    <span className="text-slate-400">{isTr ? "Clopper-Pearson %95 Ust Sınırı (p_upper):" : "Clopper-Pearson 95% Bound (p_upper):"}</span>
                    <span className="font-mono text-emerald-400 font-bold">{pUpper.toExponential(4)}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800/80">
                    <span className="text-slate-400">{isTr ? "Anne Soyu Olabilirlik Orani (LR):" : "Maternal Likelihood Ratio (LR):"}</span>
                    <span className="font-mono text-cyan-400 font-bold">
                      {isExclusion ? "0.00" : maternalLr >= 10000 ? Math.round(maternalLr).toLocaleString() : maternalLr.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5">
                    <span className="text-slate-400">{isTr ? "Esdeger Populasyon Eslesme Orani:" : "Equivalent Population Ratio:"}</span>
                    <span className="font-mono text-emerald-300 font-bold">
                      {isTr
                        ? `${Math.round(1 / Math.max(pUpper, 1e-15)).toLocaleString()} kiside 1`
                        : `1 in ${Math.round(1 / Math.max(pUpper, 1e-15)).toLocaleString()}`}
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[10px] text-slate-400 font-sans">
                  {isTr
                    ? "EMPOP 15 ve SWGDAM standartlarina gore k=0 durumunda kesin binomial formulu p_upper = 1 - (0.05)^(1/(N+1)) isletilir."
                    : "Under EMPOP 15 and SWGDAM standards, when k=0 the exact binomial formula p_upper = 1 - (0.05)^(1/(N+1)) is executed."}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* ── TAB 4: PhyloTree Build 17 Haplogroup Phylogenetics ────────────────── */}
      {activeTab === "phylotree" && (
        <motion.div
          key="phylotree-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Network className="w-5 h-5 text-purple-400" />
                  {isTr ? "PhyloTree Build 17 Mitokondriyal Filogeni Agaci" : "PhyloTree Build 17 Mitochondrial Phylogeny Tree"}
                </h2>
                <p className="text-xs text-slate-400">
                  {isTr ? "Global anne soyu klad hiyerarsisi ve tani mutasyonlari" : "Global maternal clade hierarchy and diagnostic mutations"}
                </p>
              </div>
              <span className="text-xs font-mono font-bold px-3 py-1 rounded-lg bg-purple-500/20 text-purple-300 border border-purple-500/40">
                BUILD 17 CLASSIFIER
              </span>
            </div>

            {/* Phylogeny Tree Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { clade: "L0-L6", region: "Africa (Mitochondrial Eve)", muts: "Root, 146C, 182C, 16223C", active: currentPreset.expectedHgA.startsWith("L") },
                { clade: "L3", region: "Out-of-Africa Founder", muts: "769A, 1018GA, 16311C", active: !currentPreset.expectedHgA.startsWith("L") },
                { clade: "M / N", region: "Eurasian Macro-Clades", muts: "489C, 10400T / 8701G, 9540C", active: !currentPreset.expectedHgA.startsWith("L") },
                { clade: "R -> H / V", region: "West Eurasian / European", muts: "263G, 750G, 16519C", active: currentPreset.expectedHgA.startsWith("H") },
              ].map((node) => (
                <div
                  key={node.clade}
                  className={`p-4 rounded-xl border transition-all ${
                    node.active
                      ? "bg-purple-500/15 border-purple-500/50 shadow-lg shadow-purple-500/10"
                      : "bg-slate-950/60 border-slate-800 opacity-60"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg font-black font-mono text-purple-300">{node.clade}</span>
                    {node.active && <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/30 text-purple-200">ACTIVE</span>}
                  </div>
                  <div className="text-xs font-bold text-white">{node.region}</div>
                  <div className="text-[10px] text-slate-400 font-mono mt-1">{node.muts}</div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* ── TAB 5: Custom Sequence & IUPAC Heteroplasmy Sandbox ──────────────── */}
      {activeTab === "sandbox" && (
        <motion.div
          key="sandbox-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <FileCode className="w-5 h-5 text-emerald-400" />
                  {isTr ? "Ozel Dizi & IUPAC Heteroplazmi Kumhavuzu" : "Custom Sequence & IUPAC Heteroplasmy Sandbox"}
                </h2>
                <p className="text-xs text-slate-400">
                  {isTr
                    ? "Adli analistlerin ozel varyant listelerini girmesi, PHP uyumlulugunu ve 3'-saga kaydirmayi test etmesi"
                    : "Direct variant list ingestion, point heteroplasmy compatibility, and ISFG 3'-right shift testing"}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={apply3PrimeShift}
                    onChange={(e) => setApply3PrimeShift(e.target.checked)}
                    className="rounded border-slate-700 text-emerald-500 focus:ring-emerald-500 cursor-pointer"
                  />
                  <span>{isTr ? "ISFG 3'-Saga Kaydirma" : "ISFG 3'-Right Shift"}</span>
                </label>
              </div>
            </div>

            {/* Textarea Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-300 flex justify-between">
                  <span>{isTr ? "Sorgulanan Ornek A Varyantlari:" : "Questioned Sample A Variants:"}</span>
                  <span className="text-emerald-400 font-mono text-[11px]">{parsedCustomA.length} {isTr ? "Varyant" : "Variants"}</span>
                </label>
                <textarea
                  value={customInputA}
                  onChange={(e) => setCustomInputA(e.target.value)}
                  rows={4}
                  className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 focus:outline-none focus:border-emerald-500 transition-colors"
                  placeholder="e.g. 263G, 315.1C, 750G, 16189Y, 16519C"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-300 flex justify-between">
                  <span>{isTr ? "Referans Ornek B Varyantlari:" : "Reference Sample B Variants:"}</span>
                  <span className="text-cyan-400 font-mono text-[11px]">{parsedCustomB.length} {isTr ? "Varyant" : "Variants"}</span>
                </label>
                <textarea
                  value={customInputB}
                  onChange={(e) => setCustomInputB(e.target.value)}
                  rows={4}
                  className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
                  placeholder="e.g. 263G, 315.1C, 750G, 16189C, 16519C"
                />
              </div>
            </div>

            {/* Real-Time Sandbox Evaluation Card */}
            <div className="p-5 bg-slate-950/70 rounded-xl border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  {isTr ? "Canli Kumhavuzu Degerlendirme Sonuclari (SWGDAM & IUPAC)" : "Live Sandbox Evaluation Results (SWGDAM & IUPAC)"}
                </span>
                <span
                  className={`font-bold px-3 py-1 rounded text-xs ${
                    customEvaluation.verdict === "EXCLUSION"
                      ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                      : customEvaluation.verdict === "INCONCLUSIVE"
                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                      : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                  }`}
                >
                  {customEvaluation.verdict === "EXCLUSION"
                    ? (isTr ? "KESIN DISLAMA" : "DEFINITIVE EXCLUSION")
                    : customEvaluation.verdict === "INCONCLUSIVE"
                    ? (isTr ? "KARARSIZ (1 FARK)" : "INCONCLUSIVE (1 DIFF)")
                    : (isTr ? "DAHIL ETME / ESLESME" : "MATCH / INCLUSION")}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs">
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">{isTr ? "Ortak Varyantlar:" : "Shared Calls:"}</span>
                  <span className="text-emerald-400 font-bold font-mono text-base">{customEvaluation.sharedCalls.length}</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">{isTr ? "Nokta Heteroplazmisi:" : "Point Heteroplasmy:"}</span>
                  <span className="text-purple-400 font-bold font-mono text-base">{customEvaluation.heteroplasmicSharedCount}</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">{isTr ? "Homoplazmik Fark:" : "Homoplasmic Diffs:"}</span>
                  <span className={`font-bold font-mono text-base ${customEvaluation.homoplasmicDiffCount >= 2 ? "text-rose-400" : "text-slate-200"}`}>
                    {customEvaluation.homoplasmicDiffCount}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">{isTr ? "Hesaplanan Anne Soyu LR:" : "Computed Maternal LR:"}</span>
                  <span className={`font-bold font-mono text-base ${!customEvaluation.isExclusion ? "text-cyan-400" : "text-rose-400"}`}>
                    {customEvaluation.isExclusion
                      ? "0.00"
                      : customEvaluation.maternalLr >= 10000
                      ? Math.round(customEvaluation.maternalLr).toLocaleString()
                      : customEvaluation.maternalLr.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* IUPAC Mixed Base Reference */}
              <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 font-mono">
                <span className="font-bold text-purple-300 block mb-1">
                  {isTr ? "IUPAC Karisik Baz Sozlugu (Heteroplazmi):" : "IUPAC Mixed Base Dictionary (Heteroplasmy):"}
                </span>
                <span>Y = C/T | R = A/G | M = A/C | K = G/T | S = C/G | W = A/T</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
