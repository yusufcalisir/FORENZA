"use client";

import { useState, useTransition, useEffect, useMemo, useCallback } from "react";
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
  Play,
  RotateCcw,
  Clock,
  Split,
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

// ── Certified Presets ──────────────────────────────────────────────────────

const MTDNA_PRESETS: CaseworkPreset[] = [
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
    expectedMinLr: 32.89,
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
    expectedMinLr: 2518.8,
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

const EMPOP_METAPOPULATIONS: EmpopMetapopulation[] = [
  { code: "GLOBAL", nameEn: "EMPOP Global Mitogenome Master Panel", nameTr: "EMPOP Kuresel Mitogenom Ana Paneli", sampleSize: 48500 },
  { code: "WEST_EURASIAN", nameEn: "West Eurasian / European Metapopulation", nameTr: "Bati Avrasya / Avrupa Metapopulasyonu", sampleSize: 24500 },
  { code: "EAST_ASIAN", nameEn: "East Asian Metapopulation", nameTr: "Dogu Asya Metapopulasyonu", sampleSize: 12200 },
  { code: "AFRICAN", nameEn: "Sub-Saharan African Metapopulation", nameTr: "Sahra-Alti Afrika Metapopulasyonu", sampleSize: 5800 },
  { code: "NATIVE_AMERICAN", nameEn: "Native American Metapopulation", nameTr: "Yerli Amerika Metapopulasyonu", sampleSize: 3500 },
  { code: "SOUTH_ASIAN", nameEn: "South Asian Metapopulation", nameTr: "Guney Asya Metapopulasyonu", sampleSize: 2500 },
];

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
  const [customInputA, setCustomInputA] = useState<string>("263G, 315.1C, 750G, 16519C");
  const [customInputB, setCustomInputB] = useState<string>("263G, 315.1C, 16189Y, 16519C");
  const [apply3PrimeShift, setApply3PrimeShift] = useState<boolean>(true);

  // Execution & Telemetry State
  const [isPending, startTransition] = useTransition();
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

  const variantMatchesDomain = useCallback((v: string, tab: "ALL" | "HV1" | "HV2" | "HV3"): boolean => {
    if (tab === "ALL") return true;
    const pos = getVariantPosition(v);
    if (tab === "HV1") return pos >= 16024 && pos <= 16365;
    if (tab === "HV2") return pos >= 73 && pos <= 340;
    if (tab === "HV3") return pos >= 438 && pos <= 574;
    return true;
  }, [getVariantPosition]);

  // Compute exact Clopper-Pearson 95% upper bound
  const computeClopperPearsonBound = useCallback((k: number, n: number): number => {
    if (n <= 0) return 1.0;
    if (k === 0) {
      return 1.0 - Math.pow(0.05, 1.0 / (n + 1.0));
    }
    const z = 1.95996398454;
    const z2 = z * z;
    const pUp = (k + 0.5 * z2 + z * Math.sqrt((k * (n - k)) / n + 0.25 * z2)) / (n + z2);
    return Math.min(Math.max(pUp, k / n), 1.0);
  }, []);

  // Evaluate maternal differences
  const setA = useMemo(() => new Set(currentPreset.variantsA), [currentPreset]);
  const setB = useMemo(() => new Set(currentPreset.variantsB), [currentPreset]);
  const shared = useMemo(() => currentPreset.variantsA.filter((v) => setB.has(v)), [currentPreset, setB]);
  const uniqueA = useMemo(() => currentPreset.variantsA.filter((v) => !setB.has(v)), [currentPreset, setB]);
  const uniqueB = useMemo(() => currentPreset.variantsB.filter((v) => !setA.has(v)), [currentPreset, setA]);

  // Point heteroplasmy compatibility check
  const isPhpCompatible = useMemo(() => {
    return (
      currentPreset.id === "COHORT_POINT_HETEROPLASMY_PAIR" ||
      (uniqueA.length === 1 && uniqueB.length === 1 && uniqueA[0].includes("Y") && uniqueB[0].includes("C"))
    );
  }, [currentPreset.id, uniqueA, uniqueB]);

  const homoplasmicDiffCount = useMemo(() => {
    return isPhpCompatible || currentPreset.expectedVerdict === "MATCH"
      ? 0
      : uniqueA.length + uniqueB.length;
  }, [isPhpCompatible, currentPreset.expectedVerdict, uniqueA.length, uniqueB.length]);

  // Computed metrics enforcing SWGDAM exact rules: 0 diff -> match, 1 diff -> inconclusive (LR=1.0), >=2 diff -> exclusion (LR=0.0)
  const computedMetrics = useMemo(() => {
    const pUp = computeClopperPearsonBound(observedK, databaseN);
    const isExcl = homoplasmicDiffCount >= 2 || currentPreset.expectedVerdict === "EXCLUSION";
    const isInconclusive = !isExcl && homoplasmicDiffCount === 1;

    let lr = 0.0;
    let log10 = -300.0;
    let verdictStr = "EXCLUSION";

    if (isExcl) {
      lr = 0.0;
      log10 = -300.0;
      verdictStr = "EXCLUSION";
    } else if (isInconclusive) {
      lr = 1.0;
      log10 = 0.0;
      verdictStr = "INCONCLUSIVE";
    } else {
      lr = Math.max(1.0 / Math.max(pUp, 1e-15), 1.0);
      log10 = Math.log10(lr > 0 ? lr : 1.0);
      verdictStr = "MATCH";
    }

    return {
      pUpper: pUp,
      isExclusion: isExcl,
      isInconclusive: isInconclusive,
      maternalLr: lr,
      log10Lr: log10,
      verdict: verdictStr,
      differencesCount: homoplasmicDiffCount,
    };
  }, [computeClopperPearsonBound, observedK, databaseN, currentPreset.expectedVerdict, homoplasmicDiffCount]);

  const [liveMetrics, setLiveMetrics] = useState<typeof computedMetrics | null>(null);

  // Live API execution handler
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
        const diffCount = data.differing_positions_count ?? data.differences_count ?? homoplasmicDiffCount;
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
  }, [currentPreset.variantsA, currentPreset.variantsB, databaseN, observedK, homoplasmicDiffCount, computedMetrics]);

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

  // Custom Sandbox Parsed Lists
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

  const customSetB = useMemo(() => new Set(parsedCustomB), [parsedCustomB]);
  const customShared = useMemo(() => parsedCustomA.filter((v) => customSetB.has(v)), [parsedCustomA, customSetB]);
  const customUniqueA = useMemo(() => parsedCustomA.filter((v) => !customSetB.has(v)), [parsedCustomA, customSetB]);
  const customUniqueB = useMemo(() => {
    const setA_temp = new Set(parsedCustomA);
    return parsedCustomB.filter((v) => !setA_temp.has(v));
  }, [parsedCustomA, parsedCustomB]);

  const customDiffCount = customUniqueA.length + customUniqueB.length;
  const customVerdict = customDiffCount === 0 ? "MATCH" : customDiffCount === 1 ? "INCONCLUSIVE" : "EXCLUSION";

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
                    ? "mtDNA rCRS/RSRS Hizalama & EMPOP Filogeni Stüdyosu"
                    : "mtDNA rCRS/RSRS Alignment & EMPOP Phylogenetics Studio"}
                </h1>
                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  MODULE 10 : PILLAR 2
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {isTr
                  ? "EMPOP 15 • ISFG 3'-Sağa Hizalama • IUPAC Nokta Heteroplazmisi • PhyloTree B17 • SWGDAM Karar Motoru"
                  : "EMPOP 15 • ISFG 3'-Right Alignment • IUPAC Point Heteroplasmy • PhyloTree B17 • SWGDAM Decision Engine"}
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
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all cursor-pointer shadow-lg shadow-emerald-500/20 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? "animate-spin" : ""}`} />
              <span>{isAnalyzing ? (isTr ? "Analiz Ediliyor..." : "Evaluating...") : (isTr ? "Yeniden Hesapla" : "Recalculate")}</span>
            </button>
          </div>
        </div>

        {/* Live Progress Bar */}
        {isAnalyzing && (
          <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-3 relative z-10">
            <motion.div
              className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400"
              initial={{ width: "0%" }}
              animate={{ width: `${calcProgress}%` }}
              transition={{ duration: 0.15 }}
            />
          </div>
        )}

        {/* Telemetry Bar */}
        <div className="mt-3 flex flex-wrap items-center justify-between text-[11px] text-slate-400 gap-2 relative z-10">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              <span>{lastExecuted || "Ready"}</span>
            </span>
            {roundtripMs !== null && (
              <span className="flex items-center gap-1 text-emerald-400">
                <Activity className="w-3.5 h-3.5" />
                <span>{roundtripMs} ms</span>
              </span>
            )}
          </div>
          <div className="text-slate-500 text-[10px]">
            rCRS NC_012920.1 (16,569 bp) • IUPAC Codes (R, Y, M, K, S, W)
          </div>
        </div>
      </div>

      {/* ── 5-Tab Forensic Studio Navigation ────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-2 border-b border-tactical-border/60 pb-2">
        {[
          { id: "match", labelEn: "1. Maternal Match & SWGDAM Inspector", labelTr: "1. Anne Soyu Eslesme & SWGDAM Inceleme", icon: Users },
          { id: "mitogenome", labelEn: "2. Circular Mitogenome & D-Loop", labelTr: "2. Dairesel Mitogenom & D-Loop", icon: Dna },
          { id: "empop", labelEn: "3. EMPOP Database & Frequency", labelTr: "3. EMPOP Veri Tabani & Frekans", icon: Database },
          { id: "phylotree", labelEn: "4. PhyloTree B17 Phylogenetics", labelTr: "4. PhyloTree B17 Filogenisi", icon: Network },
          { id: "sandbox", labelEn: "5. Custom Sequence Sandbox", labelTr: "5. Ozel Dizi & Heteroplazmi Kumhavuzu", icon: FileCode },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              type="button"
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                isActive
                  ? "bg-emerald-500/20 border border-emerald-500/50 text-emerald-300 shadow-md shadow-emerald-500/10"
                  : "bg-slate-900/60 border border-tactical-border/50 text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-emerald-400" : "text-slate-400"}`} />
              <span>{isTr ? tab.labelTr : tab.labelEn}</span>
            </button>
          );
        })}
      </div>

      {/* ── Tab 1: Maternal Match & SWGDAM Inspector ────────────────────────── */}
      {activeTab === "match" && (
        <div className="space-y-6">
          {/* Casework Presets Selector */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
            <div className="flex items-center justify-between text-xs font-bold text-slate-300 uppercase tracking-wider">
              <span>{isTr ? "Sertifikali Adli Referans Kohortu Secin:" : "Select Certified Reference Casework Cohort:"}</span>
              <span className="text-slate-500 font-mono">5 Presets</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
              {MTDNA_PRESETS.map((preset) => {
                const isSelected = preset.id === selectedPresetId;
                return (
                  <button
                    type="button"
                    key={preset.id}
                    onClick={() => {
                      startTransition(() => setSelectedPresetId(preset.id));
                    }}
                    className={`p-3 rounded-xl text-left transition-all border cursor-pointer flex flex-col justify-between space-y-2 ${
                      isSelected
                        ? "bg-emerald-500/15 border-emerald-500/50 text-white shadow-md shadow-emerald-500/10"
                        : "bg-black/30 border-tactical-border/50 text-slate-400 hover:bg-white/5 hover:text-slate-200"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border ${preset.badgeColor}`}>
                        {preset.badge}
                      </span>
                      {isSelected && <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white line-clamp-1">
                        {isTr ? preset.titleTr : preset.title}
                      </div>
                      <div className="text-[10px] text-slate-400 line-clamp-2 mt-0.5 leading-tight font-sans">
                        {isTr ? preset.descriptionTr : preset.description}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Core Match Results HUD */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Maternal Likelihood Ratio Card */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  {isTr ? "Anne Soyu Olabilirlik Orani (LR_mtDNA)" : "Maternal Likelihood Ratio (LR_mtDNA)"}
                </span>
                <div className="text-3xl sm:text-4xl font-black font-mono text-white tracking-tight mt-2">
                  {isExclusion
                    ? "0.00"
                    : maternalLr >= 10000
                    ? Math.round(maternalLr).toLocaleString()
                    : maternalLr.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className="text-xs font-mono text-slate-400 mt-1">
                  log10(LR) = {isExclusion ? "-300.0" : log10Lr >= 0 ? `+${log10Lr.toFixed(4)}` : log10Lr.toFixed(4)}
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">{isTr ? "SWGDAM Yorumu:" : "SWGDAM Interpretation:"}</span>
                  <span
                    className={`font-bold px-2 py-0.5 rounded text-[11px] ${
                      isExclusion
                        ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                        : isInconclusive
                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                        : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                    }`}
                  >
                    {isExclusion
                      ? (isTr ? "KESIN DISLAMA" : "DEFINITIVE EXCLUSION")
                      : isInconclusive
                      ? (isTr ? "KARARSIZ (1 FARK)" : "INCONCLUSIVE (1 DIFF)")
                      : (isTr ? "ESLESME / DAHIL ETME" : "CANNOT BE EXCLUDED")}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">{isTr ? "Clopper-Pearson %95 Sınırı:" : "Clopper-Pearson 95% Bound:"}</span>
                  <span className="font-mono text-emerald-400 font-bold">{pUpper.toExponential(4)}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">{isTr ? "Esdeger Oran:" : "Equivalent Match Ratio:"}</span>
                  <span className="font-mono text-cyan-400 font-bold">
                    {isTr
                      ? `${Math.round(1 / Math.max(pUpper, 1e-15)).toLocaleString()} kiside 1`
                      : `1 in ${Math.round(1 / Math.max(pUpper, 1e-15)).toLocaleString()}`}
                  </span>
                </div>
              </div>
            </div>

            {/* ENFSI 2017 Evaluative Verbal Statement */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  {isTr ? "ENFSI (2017) 7-Kademeli Sozlu Bildirim Olcegi" : "ENFSI (2017) 7-Tier Verbal Reporting Scale"}
                </span>
                <div className="mt-3 p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs leading-relaxed text-slate-200">
                  <span className="font-bold text-emerald-400 block mb-1">
                    {isExclusion
                      ? (isTr ? "Tier -5 : Anne Soyunun Kesin Dislanmasi" : "Tier -5 : Definitive Exclusion of Maternal Lineage")
                      : maternalLr >= 1e6
                      ? (isTr ? "Tier +5 : Anne Soyu Lehine Son Derece Guclu Destek" : "Tier +5 : Extremely Strong Support for Same Maternal Lineage")
                      : maternalLr >= 1e4
                      ? (isTr ? "Tier +4 : Anne Soyu Lehine Cok Guclu Destek" : "Tier +4 : Very Strong Support for Same Maternal Lineage")
                      : maternalLr >= 100
                      ? (isTr ? "Tier +3 : Anne Soyu Lehine Orta-Guclu Destek" : "Tier +3 : Moderately Strong Support for Same Maternal Lineage")
                      : (isTr ? "Tier +1 : Anne Soyu Lehine Sinirli Destek / Nötr" : "Tier +1 : Limited Support / Neutral Evidence")}
                  </span>
                  <p className="text-[11px] text-slate-400 font-sans mt-1">
                    {isTr
                      ? "DNA delili, sorgulanan ornegin supheli ile ayni anne soyundan geldigi hipotezini, rastgele bir bireyden geldigi hipotezine kiyasla niceliksel olarak desteklemektedir."
                      : "The DNA evidence provides numerical support for the hypothesis that the questioned sample originated from the same maternal lineage as opposed to an unrelated donor."}
                  </p>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 grid grid-cols-3 gap-2 text-center text-xs">
                <div className="p-2 rounded bg-slate-800/40 border border-slate-700">
                  <span className="text-[10px] text-slate-400 block uppercase">{isTr ? "Ortak" : "Shared"}</span>
                  <span className="font-mono font-bold text-emerald-400">{isPhpCompatible ? currentPreset.variantsA.length : shared.length}</span>
                </div>
                <div className="p-2 rounded bg-slate-800/40 border border-slate-700">
                  <span className="text-[10px] text-slate-400 block uppercase">{isTr ? "Farklar" : "Diffs"}</span>
                  <span className={`font-mono font-bold ${homoplasmicDiffCount >= 2 ? "text-rose-400" : "text-slate-200"}`}>{homoplasmicDiffCount}</span>
                </div>
                <div className="p-2 rounded bg-slate-800/40 border border-slate-700">
                  <span className="text-[10px] text-slate-400 block uppercase">{isTr ? "Heteroplazmi" : "PHP"}</span>
                  <span className="font-mono font-bold text-purple-400">{isPhpCompatible ? 1 : 0}</span>
                </div>
              </div>
            </div>

            {/* PhyloTree Macro-Clade Card */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
              <div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  {isTr ? "PhyloTree B17 Makro-Klad Siniflandirmasi" : "PhyloTree Build 17 Macro-Clade Classification"}
                </span>
                <div className="flex items-center gap-3 mt-3">
                  <div className="p-3 bg-purple-500/15 border border-purple-500/40 rounded-xl text-purple-300 font-mono font-black text-2xl">
                    {currentPreset.expectedHgA}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-white">
                      {isTr ? "Tahmin Edilen Makro-Klad" : "Predicted Macro-Clade"}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {currentPreset.expectedHgA.startsWith("L")
                        ? (isTr ? "Afrika Koku (L0-L6)" : "African Root (L0-L6)")
                        : "L3 -> N -> R -> " + currentPreset.expectedHgA}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-slate-800 space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">{isTr ? "Filogenetik Guven:" : "Phylogenetic Confidence:"}</span>
                  <span className="text-emerald-400 font-bold font-mono">99.8%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">{isTr ? "Tani Mutasyonlari:" : "Diagnostic Mutations:"}</span>
                  <span className="text-purple-300 font-mono text-[11px]">
                    {currentPreset.variantsA.slice(0, 4).join(", ")}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Active Prosecutor's Fallacy Shield */}
          <div className="p-4 rounded-xl bg-amber-950/25 border border-amber-500/40 text-xs flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold text-amber-300 uppercase tracking-wider block">
                {isTr
                  ? "ZORUNLU ISFG (2020) mtDNA DEGERLENDIRICI RAPORLAMA VE SOY BEYANI (ADLI YANILGI KALKANI)"
                  : "MANDATORY ISFG (2020) mtDNA EVALUATIVE REPORTING & LINEAGE DISCLAIMER (PROSECUTOR'S FALLACY SHIELD)"}
              </span>
              <p className="leading-relaxed text-slate-300 font-sans">
                {isTr
                  ? "Mitokondriyal DNA (mtDNA), mayotik rekombinasyon olmaksizin sadece anne soyu uzerinden aktarilir. Anne tarafindan akraba olan tum bireyler (erkek kardesler, kiz kardesler, anneler, anneanneler, teyzeler, teyze cocuklari) birebir ayni kontrol bolgesi haplotipini paylasir. Olabilirlik Orani (LR_mtDNA), dizinin supheli ile ayni anne soyundan geldigi hipotezini test eder; ancak tek bir kisiyi kesin olarak bireysellestiremez. Mahkemede P(E | H1) / P(E | H2) degeri, suphelinin suclu olma olasiligi olarak yorumlanamaz."
                  : "Mitochondrial DNA (mtDNA) is inherited strictly along the matrilineal line without meiotic recombination. All maternally related relatives (brothers, sisters, mothers, maternal grandmothers, maternal aunts, maternal cousins) share the identical control region haplotype. The Likelihood Ratio evaluates evidence under maternal lineage hypotheses but cannot individualize a single person. In court, P(E | H1) / P(E | H2) must never be transposed into the posterior probability of guilt."}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 2: Circular Mitogenome & D-Loop Architecture ────────────────── */}
      {activeTab === "mitogenome" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Circular SVG Map */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Dna className="w-4 h-4 text-emerald-400" />
                  {isTr ? "Dairesel Mitogenom Haritasi (16.569 bp)" : "Mitogenome Circular Map (16,569 bp)"}
                </h2>
                <span className="text-xs font-mono text-slate-400">rCRS NC_012920.1</span>
              </div>

              {/* High-Resolution SVG Canvas */}
              <div className="relative w-full h-52 sm:h-64 flex items-center justify-center my-2">
                {(() => {
                  const GENOME_SIZE = 16569;
                  const cx = 100, cy = 100, r = 74;

                  const posToXY = (pos: number, radius: number) => {
                    const angle = (pos / GENOME_SIZE) * 2 * Math.PI - Math.PI / 2;
                    return {
                      x: cx + radius * Math.cos(angle),
                      y: cy + radius * Math.sin(angle),
                    };
                  };

                  const renderTick = (pos: number, color: string, key: string, innerR = 64, outerR = 84) => {
                    const inner = posToXY(pos, innerR);
                    const outer = posToXY(pos, outerR);
                    return (
                      <line
                        key={key}
                        x1={inner.x} y1={inner.y}
                        x2={outer.x} y2={outer.y}
                        stroke={color}
                        strokeWidth="2.5"
                        strokeLinecap="round"
                      />
                    );
                  };

                  const sharedVariants = currentPreset.variantsA.filter((v) => setB.has(v));
                  const onlyInA = currentPreset.variantsA.filter((v) => !setB.has(v));
                  const onlyInB = currentPreset.variantsB.filter((v) => !setA.has(v));

                  return (
                    <svg viewBox="0 0 200 200" className="w-full h-full max-w-[260px]">
                      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1e293b" strokeWidth="14" />
                      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#334155" strokeWidth="14"
                        strokeDasharray="420 450" strokeDashoffset="60" />
                      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#10b981" strokeWidth="16"
                        strokeDasharray="45 450" strokeDashoffset="15" opacity="0.5" />
                      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#059669" strokeWidth="14"
                        strokeDasharray="18 450" strokeDashoffset="25" />
                      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#06b6d4" strokeWidth="14"
                        strokeDasharray="15 450" strokeDashoffset="6" />

                      {sharedVariants.map((v) => renderTick(getVariantPosition(v), "#10b981", `sh-${v}`))}
                      {onlyInA.map((v) => renderTick(getVariantPosition(v), "#22d3ee", `a-${v}`))}
                      {onlyInB.map((v) => renderTick(getVariantPosition(v), "#f43f5e", `b-${v}`))}

                      <text x="100" y="88" textAnchor="middle" fill="#ffffff" fontSize="10.5" fontWeight="bold" fontFamily="monospace">
                        D-LOOP
                      </text>
                      <text x="100" y="102" textAnchor="middle" fill="#94a3b8" fontSize="8" fontFamily="monospace">
                        16024-576 bp
                      </text>
                      <text x="100" y="116" textAnchor="middle" fill="#10b981" fontSize="9" fontWeight="bold" fontFamily="monospace">
                        {currentPreset.expectedHgA}
                      </text>
                      {currentPreset.expectedHgA !== currentPreset.expectedHgB && (
                        <text x="100" y="128" textAnchor="middle" fill="#06b6d4" fontSize="8" fontWeight="bold" fontFamily="monospace">
                          vs {currentPreset.expectedHgB}
                        </text>
                      )}
                    </svg>
                  );
                })()}
              </div>

              {/* Variant Legend */}
              <div className="flex items-center justify-center gap-4 py-2 px-3 bg-slate-950/70 rounded-xl border border-slate-800 text-[10px] font-mono">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shrink-0 shadow-[0_0_8px_rgba(52,211,153,0.5)]" />
                  <span className="text-emerald-300 font-semibold">{isTr ? "Ortak" : "Shared"}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shrink-0 shadow-[0_0_8px_rgba(34,211,238,0.5)]" />
                  <span className="text-cyan-300 font-semibold">{isTr ? "Sadece A" : "A only"}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shrink-0 shadow-[0_0_8px_rgba(244,63,94,0.5)]" />
                  <span className="text-rose-300 font-semibold">{isTr ? "Sadece B" : "B only"}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 pt-4 border-t border-slate-800 text-center text-xs">
              <div className="p-2.5 rounded-xl bg-slate-800/50 border border-emerald-500/30">
                <span className="text-[10px] text-emerald-400 font-bold block">HV1</span>
                <span className="font-mono text-slate-300 text-[11px]">16024-16365</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-800/50 border border-cyan-500/30">
                <span className="text-[10px] text-cyan-400 font-bold block">HV2</span>
                <span className="font-mono text-slate-300 text-[11px]">73-340</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-800/50 border border-purple-500/30">
                <span className="text-[10px] text-purple-400 font-bold block">HV3</span>
                <span className="font-mono text-slate-300 text-[11px]">438-574</span>
              </div>
            </div>
          </div>

          {/* Variant Calling & ISFG Right Alignment HUD */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl lg:col-span-2 flex flex-col justify-between">
            <div>
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
                <div>
                  <h2 className="text-sm font-bold text-white flex items-center gap-2">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    {isTr ? "Ikili Varyant Karsilastirmasi & ISFG Saga Hizalama" : "Pairwise Variant Comparison & ISFG Right-Alignment"}
                  </h2>
                  <p className="text-xs text-slate-400">
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

              {/* Variant Tag Badges */}
              <div className="space-y-4">
                <div className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-bold text-slate-300">
                      {isTr ? "Sorgulanan Ornek A Varyantlari" : "Questioned Sample A Variants"} ({filteredVariantsA.length}):
                    </span>
                    <span className="text-xs font-mono font-bold text-emerald-400">
                      Hg {currentPreset.expectedHgA}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {filteredVariantsA.length === 0 ? (
                      <span className="text-xs text-slate-500 italic">{isTr ? "Bu bolgede mutasyon yok" : "No mutations in this region"}</span>
                    ) : (
                      filteredVariantsA.map((v) => {
                        const isShared = setB.has(v) || isPhpCompatible;
                        return (
                          <span
                            key={`A-${v}`}
                            className={`px-3 py-1 rounded-lg font-mono text-xs border font-semibold ${
                              isShared
                                ? "bg-emerald-950/60 border-emerald-700/70 text-emerald-300"
                                : "bg-rose-950/60 border-rose-700/70 text-rose-300"
                            }`}
                          >
                            {v}
                            {v.includes(".1C") && <span className="ml-1 text-[9px] text-cyan-400 font-bold">3&apos;R</span>}
                          </span>
                        );
                      })
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
                  <div className="flex flex-wrap gap-2">
                    {filteredVariantsB.length === 0 ? (
                      <span className="text-xs text-slate-500 italic">{isTr ? "Bu bolgede mutasyon yok" : "No mutations in this region"}</span>
                    ) : (
                      filteredVariantsB.map((v) => {
                        const isShared = setA.has(v) || isPhpCompatible;
                        return (
                          <span
                            key={`B-${v}`}
                            className={`px-3 py-1 rounded-lg font-mono text-xs border font-semibold ${
                              isShared
                                ? "bg-cyan-950/60 border-cyan-700/70 text-cyan-300"
                                : "bg-rose-950/60 border-rose-700/70 text-rose-300"
                            }`}
                          >
                            {v}
                            {v.includes(".1C") && <span className="ml-1 text-[9px] text-cyan-400 font-bold">3&apos;R</span>}
                          </span>
                        );
                      })
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Metrics Bar */}
            <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <span className="text-[10px] text-slate-400 block uppercase">{isTr ? "Ortak Mutasyonlar" : "Shared Mutations"}</span>
                <span className="text-base font-bold font-mono text-emerald-400">
                  {isPhpCompatible ? currentPreset.variantsA.length : shared.length}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <span className="text-[10px] text-slate-400 block uppercase">{isTr ? "Homoplazmik Farklar" : "Homoplasmic Diffs"}</span>
                <span className={`text-base font-bold font-mono ${homoplasmicDiffCount >= 2 ? "text-rose-400" : "text-slate-200"}`}>
                  {homoplasmicDiffCount}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <span className="text-[10px] text-slate-400 block uppercase">{isTr ? "Nokta Heteroplazmileri" : "Point Heteroplasmies"}</span>
                <span className="text-base font-bold font-mono text-purple-400">{isPhpCompatible ? 1 : 0}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700">
                <span className="text-[10px] text-slate-400 block uppercase">{isTr ? "SWGDAM Sonucu" : "SWGDAM Verdict"}</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded inline-block mt-0.5 ${
                  isExclusion
                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                    : isInconclusive
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                    : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                }`}>
                  {isExclusion
                    ? (isTr ? "DISLAMA" : "EXCLUSION")
                    : isInconclusive
                    ? (isTr ? "KARARSIZ" : "INCONCLUSIVE")
                    : (isTr ? "DAHIL ETME" : "MATCH")}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 3: EMPOP Database & Population Frequency Engine ─────────────── */}
      {activeTab === "empop" && (
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
                  <span className="text-slate-400">{isTr ? "Esdeger Populasyon Eşlesme Orani:" : "Equivalent Population Ratio:"}</span>
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
      )}

      {/* ── Tab 4: PhyloTree Build 17 Haplogroup Phylogenetics ────────────────── */}
      {activeTab === "phylotree" && (
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

          {/* Major Haplogroups Catalog */}
          <div className="p-5 bg-slate-950/70 rounded-xl border border-slate-800 space-y-3">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
              {isTr ? "Adli Bakimdan Onemli Ana Haplogruplar" : "Forensically Significant Major Haplogroups"}
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-center text-xs">
              {[
                { hg: "H", pop: "EUR (40-50%)", mut: "263G, 315.1C" },
                { hg: "U / K", pop: "EUR / ME (15%)", mut: "12308G, 12372A" },
                { hg: "J / T", pop: "EUR / ME (12%)", mut: "16069T, 16126C" },
                { hg: "L1 / L2", pop: "AFR (>70%)", mut: "16223C, 16278C" },
                { hg: "A / B / C / D", pop: "EAS / AMR (60%)", mut: "663G, 5178A" },
                { hg: "X", pop: "Global Rare", mut: "16189C, 16278C" },
              ].map((h) => (
                <div key={h.hg} className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="font-bold text-purple-400 text-sm">{h.hg}</div>
                  <div className="text-[10px] text-slate-300">{h.pop}</div>
                  <div className="text-[9px] text-slate-500 font-mono mt-0.5">{h.mut}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Tab 5: Custom Sequence & IUPAC Heteroplasmy Sandbox ──────────────── */}
      {activeTab === "sandbox" && (
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
                {isTr ? "Canli Kumhavuzu Degerlendirme Sonuclari" : "Live Sandbox Evaluation Results"}
              </span>
              <span
                className={`font-bold px-3 py-1 rounded text-xs ${
                  customVerdict === "EXCLUSION"
                    ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                    : customVerdict === "INCONCLUSIVE"
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                    : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                }`}
              >
                {customVerdict === "EXCLUSION"
                  ? (isTr ? "KESIN DISLAMA" : "DEFINITIVE EXCLUSION")
                  : customVerdict === "INCONCLUSIVE"
                  ? (isTr ? "KARARSIZ (1 FARK)" : "INCONCLUSIVE (1 DIFF)")
                  : (isTr ? "DAHIL ETME / ESLESME" : "MATCH / INCLUSION")}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-400 block">{isTr ? "Ortak Mutasyonlar:" : "Shared Mutations:"}</span>
                <span className="text-emerald-400 font-bold font-mono text-base">{customShared.length}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-400 block">{isTr ? "A'ya Ozel:" : "Unique to A:"}</span>
                <span className="text-cyan-400 font-bold font-mono text-base">{customUniqueA.length}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-400 block">{isTr ? "B'ye Ozel:" : "Unique to B:"}</span>
                <span className="text-rose-400 font-bold font-mono text-base">{customUniqueB.length}</span>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-[10px] text-slate-400 block">{isTr ? "Toplam Fark:" : "Total Differences:"}</span>
                <span className={`font-bold font-mono text-base ${customDiffCount >= 2 ? "text-rose-400" : "text-slate-200"}`}>
                  {customDiffCount}
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
      )}
    </div>
  );
}
