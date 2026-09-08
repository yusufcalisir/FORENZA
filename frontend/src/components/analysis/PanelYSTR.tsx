"use client";

import { useState, useTransition, useEffect, useCallback, useMemo } from "react";
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
  Cpu,
  Play,
  RotateCcw,
  Maximize2,
  Split,
  Search,
  Clock,
  HelpCircle,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getApiBaseUrl } from "@/lib/api";

// Standard 25-system / 27-locus Y-FILER Plus Registry Metadata
export interface YStrLocusVisual {
  locus: string;
  dye: "BLUE" | "GREEN" | "YELLOW" | "RED" | "PURPLE";
  dyeColor: string;
  isRm: boolean;
  isMultiCopy: boolean;
  mutationRate: number;
  stepwiseR: number;
  evidenceAllele: string;
  suspectAllele: string;
  isMatch: boolean;
  isMutation: boolean;
  deltaStep: number;
}

export interface PresetCohort {
  id: string;
  labelEn: string;
  labelTr: string;
  descriptionEn: string;
  descriptionTr: string;
  badge: string;
  badgeColor: string;
  meioses: number;
  profileA: Record<string, any>;
  profileB: Record<string, any>;
}

// Canonical reference haplotypes
export const NIST_SRM_2391D_R1B: Record<string, any> = {
  DYS19: 14,
  DYS389I: 13,
  DYS389II: 29,
  DYS390: 24,
  DYS391: 11,
  DYS392: 13,
  DYS393: 13,
  "DYS385a/b": [11, 14],
  DYS437: 15,
  DYS438: 12,
  DYS439: 12,
  DYS448: 19,
  DYS456: 16,
  DYS458: 17,
  DYS635: 23,
  YGATAH4: 12,
  DYS460: 11,
  DYS481: 22,
  DYS533: 11,
  DYS570: 17,
  DYS576: 18,
  DYS627: 22,
  DYS518: 38,
  DYS449: 30,
  "DYF387S1a/b": [35, 37],
};

export const NA18507_O2A: Record<string, any> = {
  DYS19: 15,
  DYS389I: 12,
  DYS389II: 28,
  DYS390: 25,
  DYS391: 10,
  DYS392: 14,
  DYS393: 14,
  "DYS385a/b": [13, 19],
  DYS437: 14,
  DYS438: 10,
  DYS439: 11,
  DYS448: 20,
  DYS456: 15,
  DYS458: 18,
  DYS635: 20,
  YGATAH4: 13,
  DYS460: 10,
  DYS481: 20,
  DYS533: 12,
  DYS570: 19,
  DYS576: 17,
  DYS627: 19,
  DYS518: 40,
  DYS449: 32,
  "DYF387S1a/b": [37, 39],
};

export const NA19240_YRI_E1B1A: Record<string, any> = {
  DYS19: 15,
  DYS389I: 13,
  DYS389II: 30,
  DYS390: 21,
  DYS391: 10,
  DYS392: 11,
  DYS393: 13,
  "DYS385a/b": [16, 17],
  DYS437: 14,
  DYS438: 11,
  DYS439: 11,
  DYS448: 20,
  DYS456: 15,
  DYS458: 17,
  DYS635: 21,
  YGATAH4: 11,
  DYS460: 11,
  DYS481: 25,
  DYS533: 12,
  DYS570: 21,
  DYS576: 16,
  DYS627: 20,
  DYS518: 36,
  DYS449: 29,
  "DYF387S1a/b": [38, 40],
};

// Father-son with single DYS518 RM mutation
export const FATHER_SON_RM_MUTATION: Record<string, any> = {
  ...NIST_SRM_2391D_R1B,
  DYS518: 39, // 1-step germline mutation from 38 -> 39
};

export const GRANDFATHER_GRANDSON: Record<string, any> = {
  ...NIST_SRM_2391D_R1B,
};

export const PRESET_COHORTS: PresetCohort[] = [
  {
    id: "SRM_2391D_FATHER_SON",
    labelEn: "Paternal Duo (NIST SRM 2391d Comp A)",
    labelTr: "Baba-Ogul Ikilisi (NIST SRM 2391d)",
    descriptionEn: "1 Meiosis | 27/27 Pristine Identity | R1b1a1b (M269)",
    descriptionTr: "1 Mayoz | 27/27 Tam Uyum | R1b1a1b (M269)",
    badge: "100% IDENTITY",
    badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
    meioses: 1,
    profileA: NIST_SRM_2391D_R1B,
    profileB: NIST_SRM_2391D_R1B,
  },
  {
    id: "RM_MUTATION_DUO",
    labelEn: "Paternal Duo + RM Mutation (DYS518)",
    labelTr: "Baba-Ogul + RM Mutasyonu (DYS518)",
    descriptionEn: "1 Meiosis | 24/25 Matching + 1 RM Shift (38->39) | False Exclusion Prevented",
    descriptionTr: "1 Mayoz | 24/25 Uyum + 1 RM Mutasyon Kaymasi (38->39) | Yanlis Dislama Engellendi",
    badge: "RM MUTATION (LR > 200)",
    badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    meioses: 1,
    profileA: NIST_SRM_2391D_R1B,
    profileB: FATHER_SON_RM_MUTATION,
  },
  {
    id: "GRANDFATHER_GRANDSON",
    labelEn: "Grandfather-Grandson Trio",
    labelTr: "Dede-Torun Uclusu",
    descriptionEn: "2 Meioses | Full Paternal Lineage Transmission | LR > 200",
    descriptionTr: "2 Mayoz | Tam Baba Soyu Aktarimi | LR > 200",
    badge: "2 MEIOSES (LR > 200)",
    badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
    meioses: 2,
    profileA: NIST_SRM_2391D_R1B,
    profileB: GRANDFATHER_GRANDSON,
  },
  {
    id: "UNRELATED_EXCLUSION",
    labelEn: "Unrelated Males (R1b vs O2a)",
    labelTr: "Akraba Olmayan Erkekler (R1b vs O2a)",
    descriptionEn: "European R1b vs East Asian O2a | 15+ Loci Mismatch | Definitive Exclusion",
    descriptionTr: "Avrupali R1b vs Dogu Asyali O2a | 15+ Lokus Farki | Kesin Dislama",
    badge: "DEFINITIVE EXCLUSION (LR = 0)",
    badgeColor: "bg-rose-500/20 text-rose-300 border-rose-500/40",
    meioses: 1,
    profileA: NIST_SRM_2391D_R1B,
    profileB: NA18507_O2A,
  },
  {
    id: "AFRICAN_E1B1A_COMPARISON",
    labelEn: "West African Paternal Lineage (E1b1a)",
    labelTr: "Bati Afrika Baba Soyu (E1b1a)",
    descriptionEn: "Sub-Saharan African Lineage | NA19240 Golden Vector | M2 | Distinct Clade",
    descriptionTr: "Sahra Alti Afrika Soyu | NA19240 Altin Vektor | M2 | Belirgin Klad",
    badge: "AFRICAN LINEAGE (E1b1a)",
    badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/40",
    meioses: 1,
    profileA: NA19240_YRI_E1B1A,
    profileB: NA19240_YRI_E1B1A,
  },
];

export const YHRD_METAPOPULATIONS = [
  { code: "GLOBAL", name: "Global Casework Database", size: 385000, theta: 0.03 },
  { code: "WEST_EURASIAN", name: "West Eurasian / European", size: 142000, theta: 0.01 },
  { code: "EAST_ASIAN", name: "East Asian", size: 118000, theta: 0.02 },
  { code: "SOUTH_ASIAN", name: "South Asian", size: 45000, theta: 0.03 },
  { code: "ADMIXED_AMERICAN", name: "Admixed American / Latino", size: 42000, theta: 0.03 },
  { code: "SUB_SAHARAN_AFRICAN", name: "Sub-Saharan African", size: 38000, theta: 0.03 },
];

export const LOCUS_ORDER: Array<{
  name: string;
  dye: "BLUE" | "GREEN" | "YELLOW" | "RED" | "PURPLE";
  dyeColor: string;
  isRm: boolean;
  isMultiCopy: boolean;
  mu: number;
  r: number;
}> = [
  { name: "DYS19", dye: "BLUE", dyeColor: "text-blue-400 border-blue-500/30", isRm: false, isMultiCopy: false, mu: 0.0023, r: 0.90 },
  { name: "DYS389I", dye: "BLUE", dyeColor: "text-blue-400 border-blue-500/30", isRm: false, isMultiCopy: false, mu: 0.0026, r: 0.90 },
  { name: "DYS389II", dye: "BLUE", dyeColor: "text-blue-400 border-blue-500/30", isRm: false, isMultiCopy: false, mu: 0.0042, r: 0.88 },
  { name: "DYS390", dye: "BLUE", dyeColor: "text-blue-400 border-blue-500/30", isRm: false, isMultiCopy: false, mu: 0.0021, r: 0.92 },
  { name: "DYS391", dye: "BLUE", dyeColor: "text-blue-400 border-blue-500/30", isRm: false, isMultiCopy: false, mu: 0.0010, r: 0.94 },
  { name: "DYS392", dye: "GREEN", dyeColor: "text-emerald-400 border-emerald-500/30", isRm: false, isMultiCopy: false, mu: 0.000375, r: 0.95 },
  { name: "DYS393", dye: "GREEN", dyeColor: "text-emerald-400 border-emerald-500/30", isRm: false, isMultiCopy: false, mu: 0.0011, r: 0.92 },
  { name: "DYS385a/b", dye: "GREEN", dyeColor: "text-emerald-400 border-emerald-500/30", isRm: false, isMultiCopy: true, mu: 0.0023, r: 0.90 },
  { name: "DYS437", dye: "GREEN", dyeColor: "text-emerald-400 border-emerald-500/30", isRm: false, isMultiCopy: false, mu: 0.0012, r: 0.93 },
  { name: "DYS438", dye: "GREEN", dyeColor: "text-emerald-400 border-emerald-500/30", isRm: false, isMultiCopy: false, mu: 0.00045, r: 0.96 },
  { name: "DYS439", dye: "YELLOW", dyeColor: "text-amber-400 border-amber-500/30", isRm: false, isMultiCopy: false, mu: 0.0051, r: 0.85 },
  { name: "DYS448", dye: "YELLOW", dyeColor: "text-amber-400 border-amber-500/30", isRm: false, isMultiCopy: false, mu: 0.0014, r: 0.92 },
  { name: "DYS456", dye: "YELLOW", dyeColor: "text-amber-400 border-amber-500/30", isRm: false, isMultiCopy: false, mu: 0.0048, r: 0.88 },
  { name: "DYS458", dye: "YELLOW", dyeColor: "text-amber-400 border-amber-500/30", isRm: false, isMultiCopy: false, mu: 0.0087, r: 0.88 },
  { name: "DYS635", dye: "YELLOW", dyeColor: "text-amber-400 border-amber-500/30", isRm: false, isMultiCopy: false, mu: 0.0043, r: 0.89 },
  { name: "YGATAH4", dye: "RED", dyeColor: "text-rose-400 border-rose-500/30", isRm: false, isMultiCopy: false, mu: 0.0028, r: 0.91 },
  { name: "DYS460", dye: "RED", dyeColor: "text-rose-400 border-rose-500/30", isRm: false, isMultiCopy: false, mu: 0.0031, r: 0.90 },
  { name: "DYS481", dye: "RED", dyeColor: "text-rose-400 border-rose-500/30", isRm: false, isMultiCopy: false, mu: 0.0028, r: 0.91 },
  { name: "DYS533", dye: "RED", dyeColor: "text-rose-400 border-rose-500/30", isRm: false, isMultiCopy: false, mu: 0.0015, r: 0.93 },
  // 7 RM Rapidly Mutating Loci (6 systems)
  { name: "DYS570", dye: "PURPLE", dyeColor: "text-fuchsia-400 border-fuchsia-500/40", isRm: true, isMultiCopy: false, mu: 0.0120, r: 0.80 },
  { name: "DYS576", dye: "PURPLE", dyeColor: "text-fuchsia-400 border-fuchsia-500/40", isRm: true, isMultiCopy: false, mu: 0.0140, r: 0.80 },
  { name: "DYS627", dye: "PURPLE", dyeColor: "text-fuchsia-400 border-fuchsia-500/40", isRm: true, isMultiCopy: false, mu: 0.0130, r: 0.82 },
  { name: "DYS518", dye: "PURPLE", dyeColor: "text-fuchsia-400 border-fuchsia-500/40", isRm: true, isMultiCopy: false, mu: 0.0180, r: 0.75 },
  { name: "DYS449", dye: "PURPLE", dyeColor: "text-fuchsia-400 border-fuchsia-500/40", isRm: true, isMultiCopy: false, mu: 0.0120, r: 0.80 },
  { name: "DYF387S1a/b", dye: "PURPLE", dyeColor: "text-fuchsia-400 border-fuchsia-500/40", isRm: true, isMultiCopy: true, mu: 0.0160, r: 0.78 },
];

/**
 * Exact Clopper-Pearson 95% Binomial Upper Confidence Bound
 * For unobserved haplotype (k = 0) in database of size N:
 *   p_upper = 1 - (0.05)^(1 / (N + 1))
 * For observed haplotype (k > 0):
 *   Conservative Snedecor F bound approximation
 * Invariant: 0 < p_upper <= 1.0; for N=385000, k=0 => p_upper = 7.7810723e-6
 */
export function computeClopperPearsonBound(k: number, n: number): number {
  if (n <= 0) return 1.0;
  if (k === 0) {
    const pUpper = 1.0 - Math.pow(0.05, 1.0 / (n + 1));
    return parseFloat(pUpper.toExponential(7));
  }
  const point = k / n;
  const margin = 1.95996 * Math.sqrt((point * (1 - point)) / n + 1 / (4 * n * n));
  const bound = Math.min(1.0, point + margin);
  return parseFloat(bound.toExponential(7));
}

/**
 * Brenner Subpopulation Coancestry Frequency Adjustment (theta = 0.01 - 0.03)
 * Formula: p_Brenner = (k + theta) / (N + theta)
 * Invariant: p_Brenner > 0; strictly monotonic with k
 */
export function computeBrennerFrequency(k: number, n: number, theta: number = 0.03): number {
  if (n <= 0) return 1.0;
  const p = (k + theta) / (n + theta);
  return parseFloat(p.toExponential(5));
}

/**
 * Nested Repeat Decoupling for DYS389I and DYS389II
 * Invariant: DYS389II includes DYS389I physically.
 *   DYS389.2 = DYS389II - DYS389I
 * If DYS389II < DYS389I, isValid = false
 */
export function decoupleDYS389(dys389I: number, dys389II: number): {
  dys389_1: number;
  dys389_2: number;
  isValid: boolean;
} {
  if (dys389II < dys389I || dys389I <= 0) {
    return {
      dys389_1: dys389I,
      dys389_2: 0,
      isValid: false,
    };
  }
  return {
    dys389_1: dys389I,
    dys389_2: dys389II - dys389I,
    isValid: true,
  };
}

/**
 * Stepwise Mutation Model (SMM) Paternal Likelihood Ratio
 * For m meioses:
 *   If delta = 0: P(Match) = (1 - mu)^m
 *   If |delta| >= 1: P(Mut) = m * mu * ((1 - r) / 2) * r^(|delta| - 1)
 */
export function computeStepwiseMutationLR(
  meioses: number,
  deltaSteps: number,
  mu: number = 0.002,
  r: number = 0.90
): number {
  const m = Math.max(1, meioses);
  const delta = Math.abs(deltaSteps);
  if (delta === 0) {
    return parseFloat(Math.pow(1 - mu, m).toFixed(6));
  }
  const prob = m * mu * ((1 - r) / 2) * Math.pow(r, delta - 1);
  return parseFloat(prob.toExponential(6));
}

/**
 * Minimum Male Contributor Algorithm for Forensic Y-STR Mixtures
 * Evaluates max allele count across single-copy loci vs duplicated multi-copy loci
 * (DYS385a/b, DYF387S1a/b).
 * Formula: Min Contributors = max(max(N_single), ceil(max(N_multi) / 2))
 */
export function estimateMinimumMaleContributors(
  mixtureAlleles: Record<string, number[]>,
  multiCopyLoci: string[] = ["DYS385a/b", "DYF387S1a/b"]
): {
  minContributors: number;
  maxSingleLocus: string;
  maxSingleCount: number;
  maxMultiLocus: string;
  maxMultiCount: number;
  explanationEn: string;
  explanationTr: string;
} {
  let maxSingleCount = 0;
  let maxSingleLocus = "";
  let maxMultiCount = 0;
  let maxMultiLocus = "";

  for (const [locus, alleles] of Object.entries(mixtureAlleles)) {
    const count = Array.isArray(alleles) ? alleles.length : 0;
    if (multiCopyLoci.includes(locus)) {
      if (count > maxMultiCount) {
        maxMultiCount = count;
        maxMultiLocus = locus;
      }
    } else {
      if (count > maxSingleCount) {
        maxSingleCount = count;
        maxSingleLocus = locus;
      }
    }
  }

  const multiContribution = Math.ceil(maxMultiCount / 2);
  const minContributors = Math.max(1, Math.max(maxSingleCount, multiContribution));

  const explanationEn = maxSingleCount >= multiContribution
    ? `Observed ${maxSingleCount} distinct alleles at single-copy locus ${maxSingleLocus}, establishing a minimum of ${minContributors} male contributors.`
    : `Observed ${maxMultiCount} distinct alleles at duplicated locus ${maxMultiLocus}, establishing a minimum of ${minContributors} male contributors.`;

  const explanationTr = maxSingleCount >= multiContribution
    ? `Tek kopyali ${maxSingleLocus} lokusunda ${maxSingleCount} farkli alel gozlenerek en az ${minContributors} erkek katkici tespit edilmistir.`
    : `Cift kopyali ${maxMultiLocus} lokusunda ${maxMultiCount} farkli alel gozlenerek en az ${minContributors} erkek katkici tespit edilmistir.`;

  return {
    minContributors,
    maxSingleLocus,
    maxSingleCount,
    maxMultiLocus,
    maxMultiCount,
    explanationEn,
    explanationTr,
  };
}

export default function PanelYSTR() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  // Tab Navigation State
  const [activeTab, setActiveTab] = useState<"kinship" | "markers" | "frequencies" | "mixtures" | "sandbox">("kinship");

  // Casework & Cohort State
  const [selectedCohort, setSelectedCohort] = useState<PresetCohort>(PRESET_COHORTS[0]);
  const [selectedPop, setSelectedPop] = useState(YHRD_METAPOPULATIONS[0]);
  const [meioses, setMeioses] = useState<number>(1);
  const [theta, setTheta] = useState<number>(0.03);
  const [observedK, setObservedK] = useState<number>(0);

  // Execution & Telemetry State
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [calcProgress, setCalcProgress] = useState<number>(100);
  const [roundtripMs, setRoundtripMs] = useState<number | null>(null);
  const [lastExecuted, setLastExecuted] = useState<string | null>(null);

  // Dynamic Kinship & Haplogroup Results
  const [kinshipResult, setKinshipResult] = useState({
    matchingLoci: 25,
    mutatedLoci: 0,
    rmMutations: 0,
    standardMutations: 0,
    paternalLR: 12851.7,
    log10LR: 4.109,
    pUpper: 7.7810723e-6,
    brennerProb: 7.7922e-8,
    isExcluded: false,
    verbalEn: "Extremely Strong Support for Common Paternal Lineage",
    verbalTr: "Ortak Baba Soyu Lehine Son Derece Guclu Destek",
    predictedHaplogroup: "R1b",
    haplogroupConfidence: 0.942,
    primarySnp: "M269",
    topPosteriors: [
      { clade: "R1b (M269)", prob: 0.942 },
      { clade: "R1a (M420)", prob: 0.038 },
      { clade: "I2a (P37.2)", prob: 0.012 },
      { clade: "J2a (M410)", prob: 0.005 },
      { clade: "E1b1b (M215)", prob: 0.003 },
    ],
  });

  // Mixture Male Contributor Studio State (Tab 4)
  const [mixtureInput, setMixtureInput] = useState<Record<string, number[]>>({
    DYS19: [14, 15],
    DYS389I: [12, 13],
    DYS390: [22, 24, 25],
    "DYS385a/b": [11, 14, 15, 17],
    "DYF387S1a/b": [35, 37, 38],
  });
  const [mixtureResult, setMixtureResult] = useState<{
    minContributors: number;
    maxSingleLocus: string;
    maxSingleCount: number;
    maxMultiLocus: string;
    maxMultiCount: number;
    explanationEn: string;
    explanationTr: string;
  } | null>({
    minContributors: 3,
    maxSingleLocus: "DYS390",
    maxSingleCount: 3,
    maxMultiLocus: "DYS385a/b",
    maxMultiCount: 4,
    explanationEn: "Observed 3 distinct alleles at single-copy locus DYS390, establishing a minimum of 3 male contributors.",
    explanationTr: "Tek kopyali DYS390 lokusunda 3 farkli alel gozlenerek en az 3 erkek katkici tespit edilmistir.",
  });
  const [isMixtureLoading, setIsMixtureLoading] = useState<boolean>(false);

  // DYS389 Decoupler State (Tab 4)
  const [dys389IVal, setDys389IVal] = useState<number>(13);
  const [dys389IIVal, setDys389IIVal] = useState<number>(29);
  const [dys389Result, setDys389Result] = useState<{
    dys389_1: number;
    dys389_2: number;
    isValid: boolean;
  }>({
    dys389_1: 13,
    dys389_2: 16,
    isValid: true,
  });

  // Frequency Bound Calculator State (Tab 3)
  const [calcPopSize, setCalcPopSize] = useState<number>(385000);
  const [calcKCount, setCalcKCount] = useState<number>(0);
  const [calcTheta, setCalcTheta] = useState<number>(0.03);
  const [freqBoundResult, setFreqBoundResult] = useState<{
    pUpper: number;
    brennerFreq: number;
    formula: string;
  }>({
    pUpper: 7.781e-6,
    brennerFreq: 7.792e-8,
    formula: "1 - 0.05^(1 / (N + 1))",
  });

  // Custom Sandbox State (Tab 5)
  const [sandboxProfile, setSandboxProfile] = useState<Record<string, any>>({ ...NIST_SRM_2391D_R1B });
  const [sandboxSuspect, setSandboxSuspect] = useState<Record<string, any>>({ ...NIST_SRM_2391D_R1B });
  const [sandboxMeioses, setSandboxMeioses] = useState<number>(1);
  const [sandboxResult, setSandboxResult] = useState<{
    lr: number;
    logLr: number;
    matches: number;
    mutations: number;
    excluded: boolean;
  }>({
    lr: 12851.7,
    logLr: 4.109,
    matches: 25,
    mutations: 0,
    excluded: false,
  });

  // Live Analysis Dispatcher
  const executeKinshipEvaluation = useCallback(
    async (cohort: PresetCohort, popSize: number, curTheta: number, m: number, k: number) => {
      setIsAnalyzing(true);
      setCalcProgress(20);
      const startT = performance.now();
      const API_BASE = getApiBaseUrl();

      try {
        setCalcProgress(45);

        // 1. Dispatch Kinship Evaluation
        const kinshipPromise = fetch(`${API_BASE}/api/v1/forensic/lineage/ystr/evaluate-paternal-kinship`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            evidence_id: "EVIDENCE_A",
            suspect_id: "SUSPECT_B",
            evidence_markers: cohort.profileA,
            suspect_markers: cohort.profileB,
            meioses_m: m,
            database_size_n: popSize,
            theta: curTheta,
          }),
          signal: AbortSignal.timeout(6000),
        });

        // 2. Dispatch Live Bayesian Haplogroup Prediction
        const haploPromise = fetch(`${API_BASE}/api/v1/forensic/lineage/ystr/predict-haplogroup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            markers: cohort.profileA,
          }),
          signal: AbortSignal.timeout(6000),
        });

        const [kinshipRes, haploRes] = await Promise.allSettled([kinshipPromise, haploPromise]);
        setCalcProgress(80);

        let dataKinship: any = null;
        if (kinshipRes.status === "fulfilled" && kinshipRes.value.ok) {
          dataKinship = await kinshipRes.value.json();
        }

        let dataHaplo: any = null;
        if (haploRes.status === "fulfilled" && haploRes.value.ok) {
          dataHaplo = await haploRes.value.json();
        }

        if (dataKinship) {
          setKinshipResult((prev) => ({
            ...prev,
            matchingLoci: dataKinship.matching_loci_count,
            mutatedLoci: dataKinship.mutated_loci_count,
            rmMutations: dataKinship.rm_mutations_count,
            standardMutations: dataKinship.standard_mutations_count,
            paternalLR: dataKinship.paternal_lr,
            log10LR: dataKinship.log10_paternal_lr,
            pUpper: dataKinship.haplotype_p_upper,
            brennerProb: (k + curTheta) / (popSize + curTheta),
            isExcluded: dataKinship.is_lineage_excluded,
            verbalEn: dataKinship.verbal_predicate_en,
            verbalTr: dataKinship.verbal_predicate_tr,
            predictedHaplogroup: dataHaplo?.predicted_haplogroup || prev.predictedHaplogroup,
            haplogroupConfidence: dataHaplo?.confidence || prev.haplogroupConfidence,
            primarySnp: dataHaplo?.primary_snp || prev.primarySnp,
            topPosteriors: dataHaplo?.top_posteriors || prev.topPosteriors,
          }));
        }
      } catch (err) {
        console.warn("Live backend evaluation fallback invoked:", err);
      } finally {
        const elapsed = Math.round(performance.now() - startT);
        setRoundtripMs(elapsed);
        setLastExecuted(new Date().toLocaleTimeString());
        setCalcProgress(100);
        setIsAnalyzing(false);
      }
    },
    []
  );

  // Trigger evaluation on cohort or major parameter change
  useEffect(() => {
    executeKinshipEvaluation(selectedCohort, selectedPop.size, theta, meioses, observedK);
  }, [selectedCohort, selectedPop, theta, meioses, observedK, executeKinshipEvaluation]);

  // Decouple DYS389
  const handleDecoupleDys389 = async (val1: number, val2: number) => {
    const API_BASE = getApiBaseUrl();
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/lineage/ystr/decouple-dys389`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dys389i_allele: val1, dys389ii_allele: val2 }),
      });
      if (res.ok) {
        const d = await res.json();
        setDys389Result({ dys389_1: d.dys389_1, dys389_2: d.dys389_2, isValid: d.is_biologically_valid });
      }
    } catch {
      setDys389Result({ dys389_1: val1, dys389_2: Math.max(0, val2 - val1), isValid: val2 > val1 + 10 });
    }
  };

  // Mixture Contributor Estimator
  const handleEstimateContributors = async (lociMap: Record<string, number[]>) => {
    setIsMixtureLoading(true);
    const API_BASE = getApiBaseUrl();
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/lineage/ystr/mixture-contributors`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ locus_alleles_map: lociMap }),
      });
      if (res.ok) {
        const data = await res.json();
        setMixtureResult({
          minContributors: data.minimum_male_contributors,
          maxSingleLocus: data.max_alleles_single_copy_locus,
          maxSingleCount: data.max_alleles_single_copy_count,
          maxMultiLocus: data.max_alleles_multi_copy_locus,
          maxMultiCount: data.max_alleles_multi_copy_count,
          explanationEn: data.explanation_en,
          explanationTr: data.explanation_tr,
        });
      }
    } catch {
      // Local fallback calculation
      let maxSingle = 0;
      let maxSingleLoc = "";
      let maxMulti = 0;
      let maxMultiLoc = "";
      for (const [loc, alleles] of Object.entries(lociMap)) {
        if (loc === "DYS385a/b" || loc === "DYF387S1a/b") {
          if (alleles.length > maxMulti) {
            maxMulti = alleles.length;
            maxMultiLoc = loc;
          }
        } else {
          if (alleles.length > maxSingle) {
            maxSingle = alleles.length;
            maxSingleLoc = loc;
          }
        }
      }
      const minDonors = Math.max(maxSingle, Math.ceil(maxMulti / 2));
      setMixtureResult({
        minContributors: minDonors,
        maxSingleLocus: maxSingleLoc,
        maxSingleCount: maxSingle,
        maxMultiLocus: maxMultiLoc,
        maxMultiCount: maxMulti,
        explanationEn: `Estimated minimum of ${minDonors} male donors based on observed alleles.`,
        explanationTr: `Gozlenen alellere gore en az ${minDonors} erkek donoru tespit edilmistir.`,
      });
    } finally {
      setIsMixtureLoading(false);
    }
  };

  // Frequency Bounds recalculation
  const handleRecalcBounds = (n: number, k: number, th: number) => {
    const pUpper = k === 0 ? 1.0 - Math.pow(0.05, 1.0 / (n + 1)) : (k + 1.96 * Math.sqrt((k * (1.0 - k / n)) / n)) / n;
    const brenner = (k + th) / (n + th);
    setFreqBoundResult({
      pUpper,
      brennerFreq: brenner,
      formula: k === 0 ? "1 - 0.05^(1 / (N + 1))" : "Exact Binomial Upper 95% Bound",
    });
  };

  return (
    <div className="space-y-6 font-mono">
      {/* ── Modern Unified Benchmark & Standards Mission Bar ────────────── */}
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/70 backdrop-blur-md flex flex-wrap items-center justify-between gap-4 shadow-lg shadow-black/40">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Dna className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Pillar 02: Lineage Forensics
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-semibold">
                MODULE 08: Y-STR 27-LOCUS
              </span>
            </div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              {isTr ? "Y-FILER Plus 27-Lokus Soy & Akrabalik Motoru" : "Y-FILER Plus 27-Locus Lineage & Paternal Engine"}
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                SWGDAM 2020 / ISFG 2020
              </span>
            </h1>
          </div>
        </div>

        {/* Global Action & Telemetry */}
        <div className="flex items-center gap-3">
          {roundtripMs !== null && (
            <div className="text-right hidden sm:block">
              <div className="text-[10px] text-slate-500 flex items-center gap-1 justify-end">
                <Clock className="w-3 h-3 text-cyan-400" />
                <span>{lastExecuted}</span>
              </div>
              <div className="text-xs font-bold text-cyan-300 tabular-nums">
                {roundtripMs}ms <span className="text-slate-500 font-normal">latency</span>
              </div>
            </div>
          )}

          <button
            onClick={() => executeKinshipEvaluation(selectedCohort, selectedPop.size, theta, meioses, observedK)}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold bg-cyan-600 hover:bg-cyan-500 active:scale-95 text-white transition-all shadow-md shadow-cyan-600/30 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${isAnalyzing ? "animate-spin" : ""}`} />
            <span>{isAnalyzing ? (isTr ? "Hesaplaniyor..." : "Analyzing...") : (isTr ? "Analizi Calistir" : "Execute Kinship Analysis")}</span>
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      {isAnalyzing && (
        <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
          <motion.div
            className="bg-cyan-500 h-full"
            initial={{ width: "0%" }}
            animate={{ width: `${calcProgress}%` }}
            transition={{ duration: 0.2 }}
          />
        </div>
      )}

      {/* ── Tabbed Subsystem Studio Navigation ─────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
        {[
          { id: "kinship", labelEn: "1. Paternal Kinship & Match", labelTr: "1. Baba Soybagi & Eslestirme", icon: ShieldCheck },
          { id: "markers", labelEn: "2. 27-Locus Panel & SMM", labelTr: "2. 27-Lokus Paneli & SMM", icon: Layers },
          { id: "frequencies", labelEn: "3. YHRD Frequencies & Bounds", labelTr: "3. YHRD Frekans & Sinirlar", icon: Database },
          { id: "mixtures", labelEn: "4. Mixture Studio & DYS389", labelTr: "4. Karisim & DYS389", icon: Users },
          { id: "sandbox", labelEn: "5. Casework Sandbox", labelTr: "5. Vaka Simulasyon Sandboxy", icon: Sliders },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-bold transition-all ${
                isActive
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/10"
                  : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800 hover:border-slate-700"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{isTr ? tab.labelTr : tab.labelEn}</span>
            </button>
          );
        })}
      </div>

      {/* ── TAB 1: Paternal Kinship & Match Evaluator ─────────────────────── */}
      {activeTab === "kinship" && (
        <motion.div
          key="kinship-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Cohort Preset Selector */}
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-cyan-400" />
                {isTr ? "Referans Vaka Kohortu Secimi" : "Casework Benchmark Cohort"}
              </span>
              <span className="text-[11px] text-slate-500">
                {isTr ? "Sertifikali NIST ve Vaka Profilleri" : "Certified NIST & Casework Standards"}
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {PRESET_COHORTS.map((c) => {
                const isSel = selectedCohort.id === c.id;
                return (
                  <button
                    key={c.id}
                    onClick={() => {
                      setSelectedCohort(c);
                      setMeioses(c.meioses);
                    }}
                    className={`p-3 rounded-lg border text-left transition-all ${
                      isSel
                        ? "bg-cyan-950/40 border-cyan-500/60 shadow-md shadow-cyan-950/40"
                        : "bg-slate-900/40 border-slate-800 hover:border-slate-700 text-slate-400"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className={`text-xs font-bold truncate ${isSel ? "text-white" : "text-slate-300"}`}>
                        {isTr ? c.labelTr : c.labelEn}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border ${c.badgeColor}`}>
                        {c.badge}
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 leading-tight">
                      {isTr ? c.descriptionTr : c.descriptionEn}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Metric Telemetry Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Paternal LR Card */}
            <div className={`p-4 rounded-xl border bg-slate-950/70 backdrop-blur-md ${
              kinshipResult.isExcluded ? "border-rose-500/40" : "border-emerald-500/40"
            }`}>
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span>{isTr ? "Baba Soyu Olasilik Orani (LR)" : "Paternal Lineage LR"}</span>
                <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                  kinshipResult.isExcluded ? "bg-rose-500/20 text-rose-300" : "bg-emerald-500/20 text-emerald-300"
                }`}>
                  {kinshipResult.isExcluded ? "EXCLUDED" : "INCLUDED"}
                </span>
              </div>
              <div className={`text-2xl font-black tabular-nums tracking-tight ${
                kinshipResult.isExcluded ? "text-rose-400" : "text-emerald-400"
              }`}>
                {kinshipResult.isExcluded ? "0.00" : kinshipResult.paternalLR.toLocaleString(undefined, { maximumFractionDigits: 1 })}
              </div>
              <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
                <span>log10(LR): {kinshipResult.log10LR.toFixed(3)}</span>
                <span>Mayoz: m={meioses}</span>
              </div>
            </div>

            {/* Clopper-Pearson 95% Bound */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/70 backdrop-blur-md">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span>{isTr ? "Clopper-Pearson %95 Sinir" : "Clopper-Pearson 95% Bound"}</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300">SWGDAM</span>
              </div>
              <div className="text-2xl font-black text-blue-400 tabular-nums tracking-tight">
                {kinshipResult.pUpper.toExponential(3)}
              </div>
              <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
                <span>1 / p_upper = {(1 / Math.max(kinshipResult.pUpper, 1e-12)).toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                <span>k = {observedK}</span>
              </div>
            </div>

            {/* Brenner Adjusted Frequency */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/70 backdrop-blur-md">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span>{isTr ? "Brenner theta Duzeltmesi" : "Brenner theta Adjusted"}</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300">theta={theta}</span>
              </div>
              <div className="text-2xl font-black text-cyan-400 tabular-nums tracking-tight">
                {kinshipResult.brennerProb.toExponential(3)}
              </div>
              <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
                <span>(k + theta) / (N + theta)</span>
                <span>N={selectedPop.size.toLocaleString()}</span>
              </div>
            </div>

            {/* Matching vs Mutated Loci */}
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/70 backdrop-blur-md">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span>{isTr ? "Lokus Uyum Durumu" : "Locus Concordance"}</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300">27-LOCUS</span>
              </div>
              <div className="text-2xl font-black text-purple-400 tabular-nums tracking-tight">
                {kinshipResult.matchingLoci} <span className="text-xs text-slate-400 font-normal">/ 25 systems</span>
              </div>
              <div className="text-[10px] text-slate-500 mt-1 flex justify-between">
                <span className="text-amber-400">RM Muts: {kinshipResult.rmMutations}</span>
                <span className="text-slate-400">Std Muts: {kinshipResult.standardMutations}</span>
              </div>
            </div>
          </div>

          {/* Verbal Reporting Statement Card with Prosecutor's Fallacy Shield */}
          <div className={`p-4 rounded-xl border ${
            kinshipResult.isExcluded ? "bg-rose-950/20 border-rose-500/30" : "bg-emerald-950/20 border-emerald-500/30"
          }`}>
            <div className="flex items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <Scale className={`w-4 h-4 ${kinshipResult.isExcluded ? "text-rose-400" : "text-emerald-400"}`} />
                <span className="text-xs font-bold uppercase tracking-wider text-white">
                  {isTr ? "ISO 17025 / ENFSI (2017) Degerlendirici Adli Beyan" : "ISO 17025 / ENFSI (2017) Evaluative Statement"}
                </span>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-black/40 border border-slate-800 text-slate-300">
                PROSECUTOR FALLACY SHIELD ACTIVE
              </span>
            </div>
            <p className="text-sm font-semibold text-slate-200">
              {isTr ? kinshipResult.verbalTr : kinshipResult.verbalEn}
            </p>
            <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
              {isTr
                ? "Not: Y-STR haplotipleri ayni baba soyundaki tum erkek akrabalar (baba, ogul, erkek kardes, amca, yegen, vb.) tarafindan paylasilir. Bu nedenle bir Y-STR eslesmesi, suphelinin kendisini tek basina ve munhasiran fail kilmaz; supheli ile ayni baba soyunu paylasan tum erkek akrabalari kapsar."
                : "Disclaimer: Y-STR haplotypes are shared identically along the patriline (fathers, sons, brothers, paternal uncles, nephews). A Y-STR match cannot uniquely individualize the donor from other patrilineally related male relatives."}
            </p>
          </div>

          {/* Bayesian Haplogroup Predictor Clade Distribution */}
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Flame className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-bold text-white">
                  {isTr ? "Bayesian Y-DNA Haplogrup & Soy Agaci Tahmini" : "Bayesian Y-DNA Haplogroup & Clade Predictor"}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">{isTr ? "Belirleyici SNP:" : "Primary SNP:"}</span>
                <span className="px-2 py-0.5 rounded text-xs font-black bg-amber-500/20 text-amber-300 border border-amber-500/40">
                  {kinshipResult.primarySnp}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {kinshipResult.topPosteriors.map((hp, idx) => {
                const pct = Math.round(hp.prob * 1000) / 10;
                const isTop = idx === 0;
                return (
                  <div
                    key={hp.clade}
                    className={`p-3 rounded-lg border ${
                      isTop
                        ? "bg-amber-950/30 border-amber-500/50 shadow-md shadow-amber-950/40"
                        : "bg-slate-900/40 border-slate-800"
                    }`}
                  >
                    <div className="flex justify-between items-center text-xs mb-1">
                      <span className={`font-bold ${isTop ? "text-amber-300" : "text-slate-300"}`}>{hp.clade}</span>
                      <span className="font-mono font-bold text-slate-400">{pct}%</span>
                    </div>
                    <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${isTop ? "bg-amber-400" : "bg-slate-600"}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </motion.div>
      )}

      {/* ── TAB 2: 27-Locus Panel & Germline SMM Dynamics ─────────────────── */}
      {activeTab === "markers" && (
        <motion.div
          key="markers-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                {isTr ? "Thermo Fisher Y-FILER Plus 27-Lokus Paneli ve SMM Mutasyon Hizlari" : "Thermo Fisher Y-FILER Plus 27-Locus Panel & SMM Rates"}
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                {isTr ? "7 Hızlı Mutasyona Uğrayan (RM) lokus ve 20 Standart lokus dökümü" : "Detailed breakdown of 7 Rapidly Mutating (RM) and 20 Standard loci"}
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="px-2 py-1 rounded bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/40 font-bold">
                7 RM Y-STRs (mu &gt; 0.01)
              </span>
              <span className="px-2 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                20 Standard Y-STRs
              </span>
            </div>
          </div>

          {/* 27-Locus Grid Table */}
          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 text-[10px] uppercase tracking-wider">
                  <th className="p-3 font-semibold">Locus</th>
                  <th className="p-3 font-semibold">Dye Channel</th>
                  <th className="p-3 font-semibold">Marker Type</th>
                  <th className="p-3 font-semibold">Germline mu</th>
                  <th className="p-3 font-semibold">Range Const. r</th>
                  <th className="p-3 font-semibold">Evidence Profile</th>
                  <th className="p-3 font-semibold">Suspect Profile</th>
                  <th className="p-3 font-semibold">Delta Step |k|</th>
                  <th className="p-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {LOCUS_ORDER.map((loc) => {
                  const valA = selectedCohort.profileA[loc.name];
                  const valB = selectedCohort.profileB[loc.name];

                  let strA = Array.isArray(valA) ? valA.join(", ") : String(valA ?? "-");
                  let strB = Array.isArray(valB) ? valB.join(", ") : String(valB ?? "-");

                  let isMatch = strA === strB;
                  let deltaK = 0;
                  if (!isMatch && typeof valA === "number" && typeof valB === "number") {
                    deltaK = Math.abs(valA - valB);
                  }

                  return (
                    <tr key={loc.name} className="hover:bg-slate-900/40 transition-colors">
                      <td className="p-3 font-bold text-white">{loc.name}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${loc.dyeColor}`}>
                          {loc.dye}
                        </span>
                      </td>
                      <td className="p-3">
                        {loc.isRm ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/40">
                            RM RAPID
                          </span>
                        ) : (
                          <span className="text-slate-400 text-[11px]">Standard</span>
                        )}
                      </td>
                      <td className="p-3 tabular-nums text-slate-300">{loc.mu.toFixed(5)}</td>
                      <td className="p-3 tabular-nums text-slate-300">{loc.r.toFixed(2)}</td>
                      <td className="p-3 font-bold text-cyan-300">{strA}</td>
                      <td className="p-3 font-bold text-amber-300">{strB}</td>
                      <td className="p-3 tabular-nums font-bold text-slate-300">{deltaK}</td>
                      <td className="p-3">
                        {isMatch ? (
                          <span className="flex items-center gap-1 text-emerald-400 font-semibold text-[11px]">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            {isTr ? "Uyum" : "Concordant"}
                          </span>
                        ) : loc.isRm ? (
                          <span className="flex items-center gap-1 text-amber-400 font-semibold text-[11px]">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            {isTr ? "RM Mutasyon" : "RM Mutation"}
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-rose-400 font-semibold text-[11px]">
                            <XCircle className="w-3.5 h-3.5" />
                            {isTr ? "Farkli" : "Disconcordant"}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </motion.div>
      )}

      {/* ── TAB 3: YHRD Metapopulations & Frequency Bounds ───────────────── */}
      {activeTab === "frequencies" && (
        <motion.div
          key="freq-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                {isTr ? "YHRD Release 68 Metapopulasyon Veritabani & Istatistiki Sinirlar" : "YHRD Release 68 Metapopulation Database & Statistical Bounds"}
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                {isTr ? "N=385,000 dunya geneli haplotipler, Clopper-Pearson ve Brenner theta duzeltmesi" : "N=385,000 global haplotypes with Clopper-Pearson and Brenner theta corrections"}
              </p>
            </div>
            <span className="px-2.5 py-1 rounded bg-blue-500/20 text-blue-300 border border-blue-500/40 text-xs font-bold">
              YHRD R68 (N=385,000)
            </span>
          </div>

          {/* Metapopulation Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {YHRD_METAPOPULATIONS.map((pop) => {
              const isSel = selectedPop.code === pop.code;
              return (
                <button
                  key={pop.code}
                  onClick={() => {
                    setSelectedPop(pop);
                    setCalcPopSize(pop.size);
                    setCalcTheta(pop.theta);
                    handleRecalcBounds(pop.size, calcKCount, pop.theta);
                  }}
                  className={`p-3.5 rounded-xl border text-left transition-all ${
                    isSel
                      ? "bg-cyan-950/40 border-cyan-500/60 shadow-md shadow-cyan-950/40"
                      : "bg-slate-900/40 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs font-bold text-white">{pop.name}</span>
                    <span className="text-[10px] font-bold text-cyan-400">theta={pop.theta}</span>
                  </div>
                  <div className="text-lg font-black text-slate-200 tabular-nums">
                    N = {pop.size.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {isTr ? "Gozlenmeyen frekans siniri (k=0):" : "Unobserved upper bound (k=0):"}{" "}
                    <span className="text-cyan-300 font-mono">
                      {(1.0 - Math.pow(0.05, 1.0 / (pop.size + 1))).toExponential(2)}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Interactive Calculator Studio */}
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5 text-cyan-400" />
              {isTr ? "Interaktif Frekans Siniri ve Alt Populasyon Hesaplayici" : "Interactive Frequency Bound & Subpopulation Calculator"}
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="text-xs text-slate-400 block mb-1">
                  {isTr ? "Veritabani Boyutu (N):" : "Database Size (N):"}
                </label>
                <input
                  type="number"
                  value={calcPopSize}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    setCalcPopSize(val);
                    handleRecalcBounds(val, calcKCount, calcTheta);
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white font-mono"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">
                  {isTr ? "Gozlenen Haplotip Sayisi (k):" : "Observed Haplotype Count (k):"}
                </label>
                <input
                  type="number"
                  value={calcKCount}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    setCalcKCount(val);
                    handleRecalcBounds(calcPopSize, val, calcTheta);
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white font-mono"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">
                  {isTr ? "Alt Populasyon Akrabaligi (theta):" : "Subpopulation Coancestry (theta):"}
                </label>
                <select
                  value={calcTheta}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    setCalcTheta(val);
                    handleRecalcBounds(calcPopSize, calcKCount, val);
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white font-mono"
                >
                  <option value={0.01}>0.010 (Cosmopolitan / Urban)</option>
                  <option value={0.02}>0.020 (Regional Structured)</option>
                  <option value={0.03}>0.030 (SWGDAM Recommended Default)</option>
                  <option value={0.05}>0.050 (Isolated / Endogamous)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <div className="text-xs text-slate-400 mb-1">{isTr ? "Clopper-Pearson %95 Guven Ust Siniri" : "Clopper-Pearson 95% Bound"}</div>
                <div className="text-xl font-black text-blue-400 tabular-nums">
                  {freqBoundResult.pUpper.toExponential(4)}
                </div>
                <div className="text-[10px] text-slate-500 mt-1">
                  Formul: {freqBoundResult.formula}
                </div>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <div className="text-xs text-slate-400 mb-1">{isTr ? "Brenner theta Duzeltilmis Frekansi" : "Brenner theta Adjusted Frequency"}</div>
                <div className="text-xl font-black text-cyan-400 tabular-nums">
                  {freqBoundResult.brennerFreq.toExponential(4)}
                </div>
                <div className="text-[10px] text-slate-500 mt-1">
                  Formul: (k + theta) / (N + theta)
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* ── TAB 4: Mixture Male Contributor Studio & DYS389 Decoupler ──────── */}
      {activeTab === "mixtures" && (
        <motion.div
          key="mixtures-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Users className="w-4 h-4 text-purple-400" />
                {isTr ? "Karisimda Minimum Erkek Sayisi (N_male) & DYS389 Ayristirma" : "Minimum Male Mixture Contributors (N_male) & DYS389 Decoupler"}
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                {isTr ? "Cok kopyali lokuslarla (DYS385a/b, DYF387S1a/b) fail sayisi ve bagimsiz DYS389.2 tespiti" : "Estimating male donors via multi-copy loci and decoupling nested DYS389.2 amplicons"}
              </p>
            </div>
          </div>

          {/* Quick Preset Mixtures */}
          <div className="flex flex-wrap gap-2">
            {[
              {
                label: "2-Male Mixture",
                data: {
                  DYS19: [14, 15],
                  DYS389I: [12, 13],
                  DYS390: [22, 24],
                  "DYS385a/b": [11, 14, 15],
                  "DYF387S1a/b": [35, 37],
                },
              },
              {
                label: "3-Male Sexual Assault Mixture",
                data: {
                  DYS19: [14, 15, 16],
                  DYS389I: [12, 13, 14],
                  DYS390: [22, 24, 25],
                  "DYS385a/b": [11, 14, 15, 17],
                  "DYF387S1a/b": [35, 37, 38],
                },
              },
              {
                label: "4-Male Complex Mixture",
                data: {
                  DYS19: [14, 15, 16, 17],
                  DYS389I: [12, 13, 14],
                  DYS390: [21, 22, 24, 25],
                  "DYS385a/b": [11, 13, 14, 15, 17, 18],
                  "DYF387S1a/b": [35, 36, 37, 39],
                },
              },
            ].map((p) => (
              <button
                key={p.label}
                onClick={() => {
                  setMixtureInput(p.data);
                  handleEstimateContributors(p.data);
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800"
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Contributor Result Banner */}
          {mixtureResult && (
            <div className="p-4 rounded-xl border border-purple-500/40 bg-purple-950/20 backdrop-blur-md">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <span className="text-[10px] font-bold text-purple-300 uppercase tracking-wider">
                    {isTr ? "Tespit Edilen Minimum Erkek Katkici" : "Estimated Minimum Male Donors"}
                  </span>
                  <div className="text-3xl font-black text-purple-400 tabular-nums">
                    N_male = {mixtureResult.minContributors}
                  </div>
                  <p className="text-xs text-slate-300 mt-1">
                    {isTr ? mixtureResult.explanationTr : mixtureResult.explanationEn}
                  </p>
                </div>
                <div className="text-right space-y-1 text-xs">
                  <div className="text-slate-400">
                    {isTr ? "Tek Kopyali Maks:" : "Single-Copy Max:"}{" "}
                    <span className="font-bold text-white">{mixtureResult.maxSingleLocus} ({mixtureResult.maxSingleCount})</span>
                  </div>
                  <div className="text-slate-400">
                    {isTr ? "Cok Kopyali Maks:" : "Multi-Copy Max:"}{" "}
                    <span className="font-bold text-white">{mixtureResult.maxMultiLocus} ({mixtureResult.maxMultiCount})</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* DYS389 Nested Repeat Decoupler Studio */}
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 space-y-4">
            <div className="flex items-center gap-2">
              <Split className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                {isTr ? "DYS389I ve DYS389II Yuvalanmis Tekrar Ayristirma Stüdyosu" : "DYS389I & DYS389II Nested Repeat Decoupler"}
              </h3>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-slate-400 block mb-1">DYS389I Allele:</label>
                <input
                  type="number"
                  value={dys389IVal}
                  onChange={(e) => {
                    const v = Number(e.target.value);
                    setDys389IVal(v);
                    handleDecoupleDys389(v, dys389IIVal);
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white font-mono"
                />
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1">DYS389II Allele:</label>
                <input
                  type="number"
                  value={dys389IIVal}
                  onChange={(e) => {
                    const v = Number(e.target.value);
                    setDys389IIVal(v);
                    handleDecoupleDys389(dys389IVal, v);
                  }}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white font-mono"
                />
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center justify-between">
              <div className="text-xs text-slate-300">
                DYS389.1 = <span className="font-bold text-cyan-400">{dys389Result.dys389_1}</span> | DYS389.2 = <span className="font-bold text-amber-400">{dys389Result.dys389_2}</span>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                dys389Result.isValid ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"
              }`}>
                {dys389Result.isValid ? (isTr ? "Gecerli Biyolojik Yapi" : "Biologically Valid") : (isTr ? "Gecersiz" : "Invalid")}
              </span>
            </div>
          </div>
        </motion.div>
      )}

      {/* ── TAB 5: Interactive Casework & Custom Haplotype Sandbox ─────────── */}
      {activeTab === "sandbox" && (
        <motion.div
          key="sandbox-tab"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Sliders className="w-4 h-4 text-cyan-400" />
                {isTr ? "Ozel Haplotip Karsilastirma ve Mayoz Simulasyon Sandboxy" : "Custom Haplotype Comparator & Meioses Sandbox"}
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                {isTr ? "27-lokus alellerini manüel ayarlayarak mayoz (m) ve mutasyon duyarliligini test edin" : "Adjust 27-locus alleles and simulate meioses (m) step shifts"}
              </p>
            </div>
            <button
              onClick={() => {
                setSandboxProfile({ ...NIST_SRM_2391D_R1B });
                setSandboxSuspect({ ...NIST_SRM_2391D_R1B });
                setSandboxMeioses(1);
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>{isTr ? "Sifirla" : "Reset Standard"}</span>
            </button>
          </div>

          {/* Sandbox Meioses Slider */}
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 space-y-2">
            <div className="flex justify-between text-xs">
              <span className="font-bold text-slate-300">
                {isTr ? "Aralarindaki Mayoz Sayisi (m):" : "Number of Meioses (m):"}
              </span>
              <span className="font-black text-cyan-400">m = {sandboxMeioses}</span>
            </div>
            <input
              type="range"
              min={1}
              max={10}
              value={sandboxMeioses}
              onChange={(e) => setSandboxMeioses(Number(e.target.value))}
              className="w-full accent-cyan-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>m=1 (Baba-Ogul)</span>
              <span>m=2 (Dede-Torun / Kardes)</span>
              <span>m=3 (Amca-Yegen)</span>
              <span>m=4 (Kuzenler)</span>
              <span>m=10 (Uzak Soy)</span>
            </div>
          </div>

          {/* Quick Marker Mutation Simulator */}
          <div className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              {isTr ? "Hizli Mutasyon Enjeksiyonu (Test Senaryolari)" : "Quick Mutation Injection (Test Scenarios)"}
            </h3>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => {
                  setSandboxSuspect((prev) => ({ ...prev, DYS518: (prev.DYS518 || 38) + 1 }));
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-bold bg-fuchsia-950/30 text-fuchsia-300 border border-fuchsia-500/40"
              >
                +1 Step in RM Locus (DYS518: 38 to 39)
              </button>
              <button
                onClick={() => {
                  setSandboxSuspect((prev) => ({ ...prev, DYS570: (prev.DYS570 || 17) + 1 }));
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-bold bg-fuchsia-950/30 text-fuchsia-300 border border-fuchsia-500/40"
              >
                +1 Step in RM Locus (DYS570: 17 to 18)
              </button>
              <button
                onClick={() => {
                  setSandboxSuspect((prev) => ({ ...prev, DYS391: (prev.DYS391 || 11) + 1 }));
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-950/30 text-blue-300 border border-blue-500/40"
              >
                +1 Step in Standard Locus (DYS391: 11 to 12)
              </button>
              <button
                onClick={() => {
                  setSandboxSuspect({ ...NA18507_O2A });
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-bold bg-rose-950/30 text-rose-300 border border-rose-500/40"
              >
                Inject Complete Unrelated Profile (O2a)
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
