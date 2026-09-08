"use client";

import React, { useState, useMemo, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Cigarette,
  Scale,
  Clock,
  Wine,
  Activity,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  Sliders,
  Layers,
  FileText,
  Check,
  Copy,
  Download,
  RefreshCw,
  Play,
  Award,
  AlertTriangle,
  Info,
  CheckCircle2,
  Cpu,
  Flame,
  User,
  BarChart3,
  Moon,
  Sun,
  Sunrise,
  HeartPulse,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getApiBaseUrl } from "@/lib/api";

// ===============================================================================
// TYPES & BIOPHYSICAL SPECIFICATIONS (Pillar 4 Research Section 3 & 6 Verbatim)
// ===============================================================================

export type LifestyleTabType =
  | "smoking"
  | "metabolic"
  | "circadian_alcohol"
  | "benchmarks"
  | "iso_reporting";

export type SmokingStatusType =
  | "NON_SMOKER"
  | "FORMER_OR_LIGHT_SMOKER"
  | "CURRENT_HEAVY_SMOKER";

export type BmiCategoryType =
  | "UNDERWEIGHT"
  | "NORMAL_WEIGHT"
  | "OVERWEIGHT"
  | "OBESITY_CLASS_1"
  | "OBESITY_CLASS_2_PLUS";

export type AlcoholLevelType =
  | "LOW_OR_ABSTAINER"
  | "MODERATE_EXPOSURE"
  | "HEAVY_CHRONIC_EXPOSURE";

export type CircadianPhaseType =
  | "NOCTURNAL_PEAK_NIGHT"
  | "MATUTINAL_PEAK_MORNING"
  | "DIURNAL_PEAK_DAYTIME";

export type AgingStatusType =
  | "NORMAL_AGING"
  | "ACCELERATED_BIOLOGICAL_AGING"
  | "DECELERATED_BIOLOGICAL_AGING";

export interface GoldenBenchmarkVector {
  id: string;
  code: string;
  name: string;
  nameTr: string;
  ahrrBeta: number;
  f2rl3Beta: number;
  alppl2Beta: number;
  abcg1Beta: number;
  cpt1aBeta: number;
  srebf1Beta: number;
  slc6a3Beta: number;
  per2Beta: number;
  bmal1Beta: number;
  chronologicalAge: number;
  estimatedDnamAge: number;
  expectedSmokingStatus: SmokingStatusType;
  expectedPackYears: number;
  expectedBmi: number;
  expectedBmiCategory: BmiCategoryType;
  expectedAlcoholLevel: AlcoholLevelType;
  expectedCircadianPhase: CircadianPhaseType;
  expectedAgingStatus: AgingStatusType;
  notes: string;
  notesTr: string;
}

// 8 Diagnostic Probes across Environmental Epigenomics
export interface LifestyleProbe {
  id: string;
  gene: string;
  chromosome: string;
  description: string;
  descriptionTr: string;
  baselineBeta: number;
}

export const LIFESTYLE_PROBES: LifestyleProbe[] = [
  {
    id: "cg05575921",
    gene: "AHRR",
    chromosome: "chr5:373,378",
    description: "Cigarette smoke hypomethylation driver (intron 1)",
    descriptionTr: "Sigara dumani hipometilasyon surucusu (intron 1)",
    baselineBeta: 0.85,
  },
  {
    id: "cg03636183",
    gene: "F2RL3",
    chromosome: "chr19:17,000,586",
    description: "Coagulation protease-activated receptor 4 marker",
    descriptionTr: "Koagulasyon proteaz-aktive reseptor 4 belirteci",
    baselineBeta: 0.82,
  },
  {
    id: "cg01940273",
    gene: "ALPPL2",
    chromosome: "chr2:233,250,110",
    description: "Alkaline phosphatase placental-like 2 locus",
    descriptionTr: "Alkali fosfataz plasental-benzeri 2 lokusu",
    baselineBeta: 0.84,
  },
  {
    id: "cg06500161",
    gene: "ABCG1",
    chromosome: "chr21:43,656,587",
    description: "Lipid metabolism and cholesterol efflux mediator",
    descriptionTr: "Lipit metabolizmasi ve kolesterol disari aktarim aracisi",
    baselineBeta: 0.35,
  },
  {
    id: "cg00574958",
    gene: "CPT1A",
    chromosome: "chr11:68,607,622",
    description: "Carnitine palmitoyltransferase fatty acid oxidation",
    descriptionTr: "Karnitin palmitoiltransferaz yag asidi oksidasyonu",
    baselineBeta: 0.45,
  },
  {
    id: "cg11024682",
    gene: "SREBF1",
    chromosome: "chr17:17,730,123",
    description: "Sterol regulatory element-binding adiposity regulator",
    descriptionTr: "Sterol duzenleyici eleman baglayici adipozite belirteci",
    baselineBeta: 0.30,
  },
  {
    id: "cg_SLC6A3",
    gene: "SLC6A3",
    chromosome: "chr5:1,392,900",
    description: "Dopamine transporter DAT1 alcohol exposure index",
    descriptionTr: "Dopamin tasiyici DAT1 alkol maruziyet indeksi",
    baselineBeta: 0.50,
  },
  {
    id: "cg_PER2_BMAL1",
    gene: "PER2 / BMAL1",
    chromosome: "chr2 / chr11",
    description: "Core circadian clock oscillatory ratio (TOD window)",
    descriptionTr: "Cekirdek sirkadiyen saat salinim orani (TOD penceresi)",
    baselineBeta: 0.67,
  },
];

// ===============================================================================
// CERTIFIED REFERENCE STANDARDS (GOLDEN BENCHMARK VECTORS A - H)
// ===============================================================================

export const GOLDEN_LIFESTYLE_VECTORS: GoldenBenchmarkVector[] = [
  {
    id: "vector_18_life_a",
    code: "VECTOR_18_LIFE_A",
    name: "Never-Smoker Healthy Baseline",
    nameTr: "Hic Sigara Icmemis Saglikli Referans",
    ahrrBeta: 0.88,
    f2rl3Beta: 0.82,
    alppl2Beta: 0.84,
    abcg1Beta: 0.35,
    cpt1aBeta: 0.45,
    srebf1Beta: 0.30,
    slc6a3Beta: 0.50,
    per2Beta: 0.50,
    bmal1Beta: 0.50,
    chronologicalAge: 35.0,
    estimatedDnamAge: 35.0,
    expectedSmokingStatus: "NON_SMOKER",
    expectedPackYears: 0.0,
    expectedBmi: 24.4,
    expectedBmiCategory: "NORMAL_WEIGHT",
    expectedAlcoholLevel: "LOW_OR_ABSTAINER",
    expectedCircadianPhase: "DIURNAL_PEAK_DAYTIME",
    expectedAgingStatus: "NORMAL_AGING",
    notes: "Baseline never-smoker norm (AHRR >= 0.80), normal epigenetic BMI 24.4 kg/m2, low alcohol, and diurnal TOD.",
    notesTr: "Hic sigara icmemis temel norm (AHRR >= 0.80), normal epigenetik BMI 24.4 kg/m2, dusuk alkol ve gunduz TOD.",
  },
  {
    id: "vector_18_life_b",
    code: "VECTOR_18_LIFE_B",
    name: "Active Heavy Smoker (>40 Pack-Years)",
    nameTr: "Aktif Agir Sigara Bagimlisi (>40 Paket-Yil)",
    ahrrBeta: 0.32,
    f2rl3Beta: 0.28,
    alppl2Beta: 0.30,
    abcg1Beta: 0.42,
    cpt1aBeta: 0.40,
    srebf1Beta: 0.35,
    slc6a3Beta: 0.40,
    per2Beta: 0.55,
    bmal1Beta: 0.50,
    chronologicalAge: 48.0,
    estimatedDnamAge: 56.0,
    expectedSmokingStatus: "CURRENT_HEAVY_SMOKER",
    expectedPackYears: 44.2,
    expectedBmi: 27.4,
    expectedBmiCategory: "OVERWEIGHT",
    expectedAlcoholLevel: "LOW_OR_ABSTAINER",
    expectedCircadianPhase: "DIURNAL_PEAK_DAYTIME",
    expectedAgingStatus: "ACCELERATED_BIOLOGICAL_AGING",
    notes: "Profound AHRR hypomethylation (0.32), smoking score > 6.0, 44.2 pack-years, and +8.0 yrs accelerated aging.",
    notesTr: "Belirgin AHRR hipometilasyonu (0.32), sigara skoru > 6.0, 44.2 paket-yil ve +8.0 yil hizlanmis yaslanma.",
  },
  {
    id: "vector_18_life_c",
    code: "VECTOR_18_LIFE_C",
    name: "Former / Light Smoker Profile",
    nameTr: "Eski / Hafif Sigara Icen Profili",
    ahrrBeta: 0.65,
    f2rl3Beta: 0.50,
    alppl2Beta: 0.55,
    abcg1Beta: 0.36,
    cpt1aBeta: 0.44,
    srebf1Beta: 0.31,
    slc6a3Beta: 0.52,
    per2Beta: 0.45,
    bmal1Beta: 0.50,
    chronologicalAge: 52.0,
    estimatedDnamAge: 53.0,
    expectedSmokingStatus: "FORMER_OR_LIGHT_SMOKER",
    expectedPackYears: 16.7,
    expectedBmi: 25.0,
    expectedBmiCategory: "OVERWEIGHT",
    expectedAlcoholLevel: "LOW_OR_ABSTAINER",
    expectedCircadianPhase: "DIURNAL_PEAK_DAYTIME",
    expectedAgingStatus: "NORMAL_AGING",
    notes: "Partial AHRR re-methylation (0.65), score 2.89, 16.7 pack-years, reflecting smoking cessation history.",
    notesTr: "Kismi AHRR yeniden metillenmesi (0.65), skor 2.89, 16.7 paket-yil, sigarayi birakma gecmisini yansitir.",
  },
  {
    id: "vector_18_life_d",
    code: "VECTOR_18_LIFE_D",
    name: "Epigenetic BMI Normal Weight",
    nameTr: "Epigenetik BMI Normal Kilo",
    ahrrBeta: 0.85,
    f2rl3Beta: 0.82,
    alppl2Beta: 0.84,
    abcg1Beta: 0.35,
    cpt1aBeta: 0.45,
    srebf1Beta: 0.30,
    slc6a3Beta: 0.50,
    per2Beta: 0.50,
    bmal1Beta: 0.50,
    chronologicalAge: 29.0,
    estimatedDnamAge: 29.2,
    expectedSmokingStatus: "NON_SMOKER",
    expectedPackYears: 0.0,
    expectedBmi: 24.4,
    expectedBmiCategory: "NORMAL_WEIGHT",
    expectedAlcoholLevel: "LOW_OR_ABSTAINER",
    expectedCircadianPhase: "DIURNAL_PEAK_DAYTIME",
    expectedAgingStatus: "NORMAL_AGING",
    notes: "Normative ABCG1 (0.35), CPT1A (0.45), SREBF1 (0.30) predicting BMI 24.4 kg/m2 in normal weight window.",
    notesTr: "Normal kilo araliginda 24.4 kg/m2 BMI tahmin eden standart ABCG1 (0.35), CPT1A (0.45), SREBF1 (0.30).",
  },
  {
    id: "vector_18_life_e",
    code: "VECTOR_18_LIFE_E",
    name: "Epigenetic BMI Severe Obesity (Class II+)",
    nameTr: "Epigenetik BMI Ileri Derece Obezite (Sinif II+)",
    ahrrBeta: 0.80,
    f2rl3Beta: 0.78,
    alppl2Beta: 0.80,
    abcg1Beta: 0.75,
    cpt1aBeta: 0.15,
    srebf1Beta: 0.65,
    slc6a3Beta: 0.50,
    per2Beta: 0.50,
    bmal1Beta: 0.50,
    chronologicalAge: 44.0,
    estimatedDnamAge: 46.0,
    expectedSmokingStatus: "NON_SMOKER",
    expectedPackYears: 0.0,
    expectedBmi: 42.7,
    expectedBmiCategory: "OBESITY_CLASS_2_PLUS",
    expectedAlcoholLevel: "LOW_OR_ABSTAINER",
    expectedCircadianPhase: "DIURNAL_PEAK_DAYTIME",
    expectedAgingStatus: "NORMAL_AGING",
    notes: "Elevated ABCG1 (0.75) and SREBF1 (0.65) with suppressed CPT1A (0.15), predicting BMI 42.7 kg/m2.",
    notesTr: "Baskilanmis CPT1A (0.15) ile yuksek ABCG1 (0.75) ve SREBF1 (0.65), 42.7 kg/m2 BMI ongormektedir.",
  },
  {
    id: "vector_18_life_f",
    code: "VECTOR_18_LIFE_F",
    name: "Heavy Chronic Alcohol Exposure (SLC6A3)",
    nameTr: "Agir Kronik Alkol Maruziyeti (SLC6A3)",
    ahrrBeta: 0.75,
    f2rl3Beta: 0.70,
    alppl2Beta: 0.72,
    abcg1Beta: 0.40,
    cpt1aBeta: 0.40,
    srebf1Beta: 0.35,
    slc6a3Beta: 0.10,
    per2Beta: 0.50,
    bmal1Beta: 0.50,
    chronologicalAge: 41.0,
    estimatedDnamAge: 43.5,
    expectedSmokingStatus: "FORMER_OR_LIGHT_SMOKER",
    expectedPackYears: 8.3,
    expectedBmi: 27.0,
    expectedBmiCategory: "OVERWEIGHT",
    expectedAlcoholLevel: "HEAVY_CHRONIC_EXPOSURE",
    expectedCircadianPhase: "DIURNAL_PEAK_DAYTIME",
    expectedAgingStatus: "NORMAL_AGING",
    notes: "SLC6A3 beta 0.10 yielding alcohol index score 80.0, classified as Heavy Chronic Exposure.",
    notesTr: "SLC6A3 beta 0.10 ile 80.0 alkol indeks skoru, Agir Kronik Maruziyet olarak siniflandirilir.",
  },
  {
    id: "vector_18_life_g",
    code: "VECTOR_18_LIFE_G",
    name: "Nocturnal Crime Scene TOD (PER2/BMAL1)",
    nameTr: "Gece Olay Yeri TOD Penceresi (PER2/BMAL1)",
    ahrrBeta: 0.85,
    f2rl3Beta: 0.82,
    alppl2Beta: 0.84,
    abcg1Beta: 0.35,
    cpt1aBeta: 0.45,
    srebf1Beta: 0.30,
    slc6a3Beta: 0.50,
    per2Beta: 0.80,
    bmal1Beta: 0.40,
    chronologicalAge: 32.0,
    estimatedDnamAge: 32.0,
    expectedSmokingStatus: "NON_SMOKER",
    expectedPackYears: 0.0,
    expectedBmi: 24.4,
    expectedBmiCategory: "NORMAL_WEIGHT",
    expectedAlcoholLevel: "LOW_OR_ABSTAINER",
    expectedCircadianPhase: "NOCTURNAL_PEAK_NIGHT",
    expectedAgingStatus: "NORMAL_AGING",
    notes: "PER2/BMAL1 ratio 2.0 > 1.2, confirming nocturnal sample deposition (22:00 - 04:00 UTC).",
    notesTr: "PER2/BMAL1 orani 2.0 > 1.2, gece ornek birikimini dogrular (22:00 - 04:00 UTC).",
  },
  {
    id: "vector_18_life_h",
    code: "VECTOR_18_LIFE_H",
    name: "Accelerated Biological Aging (+8.5 Years)",
    nameTr: "Hizlanmis Biyolojik Yaslanma (+8.5 Yil)",
    ahrrBeta: 0.35,
    f2rl3Beta: 0.30,
    alppl2Beta: 0.32,
    abcg1Beta: 0.50,
    cpt1aBeta: 0.30,
    srebf1Beta: 0.40,
    slc6a3Beta: 0.25,
    per2Beta: 0.70,
    bmal1Beta: 0.30,
    chronologicalAge: 30.0,
    estimatedDnamAge: 38.5,
    expectedSmokingStatus: "CURRENT_HEAVY_SMOKER",
    expectedPackYears: 41.7,
    expectedBmi: 31.7,
    expectedBmiCategory: "OBESITY_CLASS_1",
    expectedAlcoholLevel: "HEAVY_CHRONIC_EXPOSURE",
    expectedCircadianPhase: "NOCTURNAL_PEAK_NIGHT",
    expectedAgingStatus: "ACCELERATED_BIOLOGICAL_AGING",
    notes: "Multimodal chronic insult: heavy smoking, obesity, high alcohol, resulting in +8.5 yrs epigenetic age acceleration.",
    notesTr: "Cok modlu kronik etki: agir sigara, obezite, yuksek alkol sonucu +8.5 yil epigenetik yas ivmelenmesi.",
  },
];

// ===============================================================================
// CANONICAL COMPONENT: PanelLifestyle
// ===============================================================================

export default function PanelLifestyle() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  // Tab State
  const [activeTab, setActiveTab] = useState<LifestyleTabType>("smoking");

  // Biomarker Input States
  const [ahrrBeta, setAhrrBeta] = useState<number>(0.85);
  const [f2rl3Beta, setF2rl3Beta] = useState<number>(0.82);
  const [alppl2Beta, setAlppl2Beta] = useState<number>(0.84);

  const [abcg1Beta, setAbcg1Beta] = useState<number>(0.35);
  const [cpt1aBeta, setCpt1aBeta] = useState<number>(0.45);
  const [srebf1Beta, setSrebf1Beta] = useState<number>(0.30);

  const [slc6a3Beta, setSlc6a3Beta] = useState<number>(0.50);
  const [per2Beta, setPer2Beta] = useState<number>(0.50);
  const [bmal1Beta, setBmal1Beta] = useState<number>(0.50);

  const [chronologicalAge, setChronologicalAge] = useState<number>(35.0);
  const [estimatedDnamAge, setEstimatedDnamAge] = useState<number>(35.0);

  // Execution & Live API States
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [selectedVectorId, setSelectedVectorId] = useState<string>("vector_18_life_a");
  const [apiError, setApiError] = useState<string | null>(null);

  // ─────────────────────────────────────────────────────────────────────────────
  // MATHEMATICAL INFERENCE (Pillar 4 Research Verbatim Formulation)
  // ─────────────────────────────────────────────────────────────────────────────

  const calculatedProfile = useMemo(() => {
    // 1. Smoking Model
    // Score_smoke = 10.50 - 9.80*AHRR - 2.50*F2RL3 - 1.80*ALPPL2
    const rawSmokingScore = 10.50 - 9.80 * ahrrBeta - 2.50 * f2rl3Beta - 1.80 * alppl2Beta;
    const smokingScore = Math.round(rawSmokingScore * 100) / 100;

    let packYearsEst = Math.max(0.0, Math.round(((0.85 - ahrrBeta) / 0.012) * 10) / 10);
    let smokingStatus: SmokingStatusType = "NON_SMOKER";
    let smokingProbability = 0.05;

    if (ahrrBeta < 0.55 || smokingScore > 4.50) {
      smokingStatus = "CURRENT_HEAVY_SMOKER";
      const pRaw = 0.75 + Math.max(0.0, smokingScore - 4.50) * 0.12;
      smokingProbability = Math.min(0.99, Math.max(0.85, Math.round(pRaw * 100) / 100));
    } else if (ahrrBeta < 0.80 || smokingScore >= 1.50) {
      smokingStatus = "FORMER_OR_LIGHT_SMOKER";
      smokingProbability = 0.75;
    } else {
      smokingStatus = "NON_SMOKER";
      smokingProbability = Math.min(0.95, Math.max(0.05, Math.round(ahrrBeta * 0.98 * 100) / 100));
      packYearsEst = 0.0;
    }

    // 2. Epigenetic BMI Model
    // BMI = 24.50 + 18.20*ABCG1 - 22.40*CPT1A + 12.10*SREBF1
    const rawBmi = 24.50 + 18.20 * abcg1Beta - 22.40 * cpt1aBeta + 12.10 * srebf1Beta;
    const estimatedBmi = Math.round(rawBmi * 10) / 10;

    let bmiCategory: BmiCategoryType = "NORMAL_WEIGHT";
    if (estimatedBmi < 18.5) {
      bmiCategory = "UNDERWEIGHT";
    } else if (estimatedBmi < 25.0) {
      bmiCategory = "NORMAL_WEIGHT";
    } else if (estimatedBmi < 30.0) {
      bmiCategory = "OVERWEIGHT";
    } else if (estimatedBmi < 35.0) {
      bmiCategory = "OBESITY_CLASS_1";
    } else {
      bmiCategory = "OBESITY_CLASS_2_PLUS";
    }

    // 3. Alcohol Exposure Index (SLC6A3)
    // Score = |0.50 - SLC6A3| * 200.0
    const alcoholScore = Math.round(Math.abs(0.50 - slc6a3Beta) * 200.0 * 10) / 10;
    let alcoholLevel: AlcoholLevelType = "LOW_OR_ABSTAINER";
    if (alcoholScore > 40.0) {
      alcoholLevel = "HEAVY_CHRONIC_EXPOSURE";
    } else if (alcoholScore > 20.0) {
      alcoholLevel = "MODERATE_EXPOSURE";
    }

    // 4. Circadian Phase Shift (PER2 vs BMAL1)
    // Ratio = PER2 / max(0.01, BMAL1)
    const circadianRatio = per2Beta / Math.max(0.01, bmal1Beta);
    let circadianPhase: CircadianPhaseType = "DIURNAL_PEAK_DAYTIME";
    let todWindow = "10:00 - 16:00 UTC";

    if (circadianRatio > 1.2) {
      circadianPhase = "NOCTURNAL_PEAK_NIGHT";
      todWindow = "22:00 - 04:00 UTC";
    } else if (circadianRatio < 0.8) {
      circadianPhase = "MATUTINAL_PEAK_MORNING";
      todWindow = "04:00 - 10:00 UTC";
    }

    // 5. Epigenetic Age Acceleration Delta
    const ageDelta = Math.round((estimatedDnamAge - chronologicalAge) * 10) / 10;
    let agingStatus: AgingStatusType = "NORMAL_AGING";
    if (ageDelta > 5.0) {
      agingStatus = "ACCELERATED_BIOLOGICAL_AGING";
    } else if (ageDelta < -5.0) {
      agingStatus = "DECELERATED_BIOLOGICAL_AGING";
    }

    return {
      smokingScore,
      smokingStatus,
      smokingProbability,
      packYearsEst,
      estimatedBmi,
      bmiCategory,
      alcoholScore,
      alcoholLevel,
      circadianRatio: Math.round(circadianRatio * 100) / 100,
      circadianPhase,
      todWindow,
      ageDelta,
      agingStatus,
    };
  }, [
    ahrrBeta,
    f2rl3Beta,
    alppl2Beta,
    abcg1Beta,
    cpt1aBeta,
    srebf1Beta,
    slc6a3Beta,
    per2Beta,
    bmal1Beta,
    chronologicalAge,
    estimatedDnamAge,
  ]);

  // Handle Loading Certified Golden Benchmark Vector
  const handleLoadVector = useCallback((v: GoldenBenchmarkVector) => {
    setSelectedVectorId(v.id);
    setAhrrBeta(v.ahrrBeta);
    setF2rl3Beta(v.f2rl3Beta);
    setAlppl2Beta(v.alppl2Beta);
    setAbcg1Beta(v.abcg1Beta);
    setCpt1aBeta(v.cpt1aBeta);
    setSrebf1Beta(v.srebf1Beta);
    setSlc6a3Beta(v.slc6a3Beta);
    setPer2Beta(v.per2Beta);
    setBmal1Beta(v.bmal1Beta);
    setChronologicalAge(v.chronologicalAge);
    setEstimatedDnamAge(v.estimatedDnamAge);
  }, []);

  // Live Backend API Trigger
  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    setApiError(null);
    try {
      const baseUrl = getApiBaseUrl();
      const payload = {
        ahrr_cg05575921_beta: ahrrBeta,
        f2rl3_beta: f2rl3Beta,
        alppl2_beta: alppl2Beta,
        abcg1_beta: abcg1Beta,
        cpt1a_beta: cpt1aBeta,
        srebf1_beta: srebf1Beta,
        slc6a3_beta: slc6a3Beta,
        per2_beta: per2Beta,
        bmal1_beta: bmal1Beta,
        chronological_age: chronologicalAge,
        estimated_dnam_age: estimatedDnamAge,
      };
      const res = await fetch(`${baseUrl}/api/v1/forensic/epigenetics/lifestyle-profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        throw new Error(`API error: ${res.statusText}`);
      }
      await res.json();
    } catch (err: unknown) {
      // Client simulation provides instant fallback
      const msg = err instanceof Error ? err.message : String(err);
      setApiError(msg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // ─────────────────────────────────────────────────────────────────────────────
  // RENDER HELPERS
  // ─────────────────────────────────────────────────────────────────────────────

  const getSmokingBadge = (status: SmokingStatusType) => {
    switch (status) {
      case "NON_SMOKER":
        return {
          label: isTr ? "Sigara Icmeyen" : "Non-Smoker",
          bg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
        };
      case "FORMER_OR_LIGHT_SMOKER":
        return {
          label: isTr ? "Eski / Hafif Icen" : "Former / Light Smoker",
          bg: "bg-amber-500/10 text-amber-400 border-amber-500/30",
        };
      case "CURRENT_HEAVY_SMOKER":
        return {
          label: isTr ? "Aktif Agir Icen" : "Current Heavy Smoker",
          bg: "bg-rose-500/10 text-rose-400 border-rose-500/30",
        };
    }
  };

  const getBmiBadge = (cat: BmiCategoryType) => {
    switch (cat) {
      case "UNDERWEIGHT":
        return {
          label: isTr ? "Zayif (<18.5)" : "Underweight (<18.5)",
          color: "text-cyan-400 border-cyan-500/30 bg-cyan-500/10",
        };
      case "NORMAL_WEIGHT":
        return {
          label: isTr ? "Normal Kilo (18.5 - 24.9)" : "Normal Weight (18.5 - 24.9)",
          color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
        };
      case "OVERWEIGHT":
        return {
          label: isTr ? "Fazla Kilolu (25.0 - 29.9)" : "Overweight (25.0 - 29.9)",
          color: "text-amber-400 border-amber-500/30 bg-amber-500/10",
        };
      case "OBESITY_CLASS_1":
        return {
          label: isTr ? "Obezite Sinif I (30.0 - 34.9)" : "Obesity Class I (30.0 - 34.9)",
          color: "text-rose-400 border-rose-500/30 bg-rose-500/10",
        };
      case "OBESITY_CLASS_2_PLUS":
        return {
          label: isTr ? "Ileri Obezite Sinif II+ (>=35.0)" : "Severe Obesity Class II+ (>=35.0)",
          color: "text-purple-400 border-purple-500/30 bg-purple-500/10",
        };
    }
  };

  const getCircadianBadge = (phase: CircadianPhaseType) => {
    switch (phase) {
      case "NOCTURNAL_PEAK_NIGHT":
        return {
          icon: Moon,
          label: isTr ? "Gece Pik (22:00 - 04:00 UTC)" : "Nocturnal Peak (22:00 - 04:00 UTC)",
          color: "text-indigo-400 border-indigo-500/30 bg-indigo-500/10",
        };
      case "MATUTINAL_PEAK_MORNING":
        return {
          icon: Sunrise,
          label: isTr ? "Sabah Pik (04:00 - 10:00 UTC)" : "Matutinal Peak (04:00 - 10:00 UTC)",
          color: "text-amber-400 border-amber-500/30 bg-amber-500/10",
        };
      case "DIURNAL_PEAK_DAYTIME":
        return {
          icon: Sun,
          label: isTr ? "Gunduz Pik (10:00 - 16:00 UTC)" : "Diurnal Peak (10:00 - 16:00 UTC)",
          color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
        };
    }
  };

  return (
    <div className="w-full space-y-6 pb-12">
      {/* ── HEADER TELEMETRY STRIP ── */}
      <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/50 p-5 backdrop-blur-md">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-md border border-rose-500/40 bg-rose-500/10 px-2 py-0.5 font-mono text-xs font-semibold text-rose-400">
                PILLAR 4 • MOD 21
              </span>
              <span className="rounded-md border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 font-mono text-xs text-emerald-400">
                ISO/IEC 17025:2017
              </span>
              <span className="rounded-md border border-amber-500/40 bg-amber-500/10 px-2 py-0.5 font-mono text-xs text-amber-400">
                AHRR • ABCG1 • SLC6A3 • PER2
              </span>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white sm:text-2xl">
              {isTr
                ? "Yasam Tarzi Epigenetigi & AHRR Biyobelirtecleri"
                : "Lifestyle Epigenomics & AHRR Biomarkers"}
            </h1>
            <p className="text-xs text-slate-400 sm:text-sm">
              {isTr
                ? "Kantitatif sigara hipometilasyon modeli, paket-yil regresyonu, epigenetik BMI, dopamin alkol indeksi ve sirkadiyen birikim zamani (TOD)."
                : "Quantitative smoking hypomethylation model, pack-years regression, epigenetic BMI, dopamine alcohol index, and circadian deposition window (TOD)."}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleRunAnalysis}
              disabled={isAnalyzing}
              className="flex min-h-[44px] items-center gap-2 rounded-lg border border-rose-500/40 bg-rose-500/20 px-4 py-2 text-xs font-medium text-rose-300 transition-all hover:bg-rose-500/30 active:scale-95 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${isAnalyzing ? "animate-spin" : ""}`} />
              <span>
                {isAnalyzing
                  ? isTr
                    ? "Hesaplaniyor..."
                    : "Calculating..."
                  : isTr
                  ? "Analizi Calistir"
                  : "Execute Analysis"}
              </span>
            </button>
          </div>
        </div>

        {/* Global Metric Cards */}
        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/60 p-3">
            <div className="text-[11px] text-slate-400">
              {isTr ? "Sigara Durumu" : "Smoking Status"}
            </div>
            <div className="mt-1 flex items-center gap-1.5 font-mono text-sm font-bold">
              <span
                className={`inline-block rounded border px-1.5 py-0.5 text-xs ${
                  getSmokingBadge(calculatedProfile.smokingStatus).bg
                }`}
              >
                {getSmokingBadge(calculatedProfile.smokingStatus).label}
              </span>
            </div>
            <div className="mt-1 font-mono text-[11px] text-slate-400">
              {calculatedProfile.packYearsEst}{" "}
              <span className="text-[10px]">{isTr ? "Paket-Yil" : "Pack-Years"}</span>
            </div>
          </div>

          <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/60 p-3">
            <div className="text-[11px] text-slate-400">
              {isTr ? "Epigenetik BMI" : "Epigenetic BMI"}
            </div>
            <div className="mt-1 font-mono text-base font-bold text-white tabular-nums">
              {calculatedProfile.estimatedBmi}{" "}
              <span className="text-xs font-normal text-slate-400">kg/m²</span>
            </div>
            <div className="mt-1 truncate font-mono text-[10px] text-slate-300">
              {getBmiBadge(calculatedProfile.bmiCategory).label}
            </div>
          </div>

          <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/60 p-3">
            <div className="text-[11px] text-slate-400">
              {isTr ? "Alkol Indeksi (SLC6A3)" : "Alcohol Index (SLC6A3)"}
            </div>
            <div className="mt-1 font-mono text-base font-bold text-white tabular-nums">
              {calculatedProfile.alcoholScore}
            </div>
            <div className="mt-1 font-mono text-[10px] text-amber-400">
              {calculatedProfile.alcoholLevel === "HEAVY_CHRONIC_EXPOSURE"
                ? isTr
                  ? "Agir Kronik"
                  : "Heavy Chronic"
                : calculatedProfile.alcoholLevel === "MODERATE_EXPOSURE"
                ? isTr
                  ? "Orta Duzey"
                  : "Moderate"
                : isTr
                ? "Dusuk / Tuketmeyen"
                : "Low / Abstainer"}
            </div>
          </div>

          <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/60 p-3">
            <div className="text-[11px] text-slate-400">
              {isTr ? "Sirkadiyen Faz (TOD)" : "Circadian Phase (TOD)"}
            </div>
            <div className="mt-1 font-mono text-xs font-bold text-white">
              {calculatedProfile.circadianRatio} <span className="text-[10px] text-slate-400">P2/B1</span>
            </div>
            <div className="mt-1 truncate font-mono text-[10px] text-indigo-400">
              {calculatedProfile.todWindow}
            </div>
          </div>

          <div className="col-span-2 rounded-lg border border-tactical-border/40 bg-tactical-bg/60 p-3 sm:col-span-2 lg:col-span-1">
            <div className="text-[11px] text-slate-400">
              {isTr ? "Biyolojik Yas Sapmasi" : "Age Acceleration Delta"}
            </div>
            <div className="mt-1 font-mono text-base font-bold tabular-nums">
              <span
                className={
                  calculatedProfile.ageDelta > 5
                    ? "text-rose-400"
                    : calculatedProfile.ageDelta < -5
                    ? "text-cyan-400"
                    : "text-emerald-400"
                }
              >
                {calculatedProfile.ageDelta > 0 ? `+${calculatedProfile.ageDelta}` : calculatedProfile.ageDelta} yrs
              </span>
            </div>
            <div className="mt-1 font-mono text-[10px] text-slate-400">
              {calculatedProfile.agingStatus === "ACCELERATED_BIOLOGICAL_AGING"
                ? isTr
                  ? "Hizlanmis Yaslanma"
                  : "Accelerated Aging"
                : calculatedProfile.agingStatus === "DECELERATED_BIOLOGICAL_AGING"
                ? isTr
                  ? "Yavaslamis Yaslanma"
                  : "Decelerated Aging"
                : isTr
                ? "Normal Yaslanma"
                : "Normal Aging"}
            </div>
          </div>
        </div>
      </div>

      {/* ── CANONICAL 5-TAB NAVIGATION ── */}
      <div className="flex border-b border-tactical-border/60 overflow-x-auto no-scrollbar">
        {[
          {
            id: "smoking",
            label: isTr ? "1. Sigara & AHRR" : "1. Smoking & AHRR",
            icon: Cigarette,
          },
          {
            id: "metabolic",
            label: isTr ? "2. Epigenetik BMI" : "2. Epigenetic BMI",
            icon: Scale,
          },
          {
            id: "circadian_alcohol",
            label: isTr ? "3. Alkol & Sirkadiyen TOD" : "3. Alcohol & Circadian TOD",
            icon: Clock,
          },
          {
            id: "benchmarks",
            label: isTr ? "4. Referans Vektorler" : "4. Reference Vectors",
            icon: Award,
          },
          {
            id: "iso_reporting",
            label: isTr ? "5. ISO 17025 Raporu" : "5. ISO 17025 Report",
            icon: FileText,
          },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as LifestyleTabType)}
              className={`flex min-h-[44px] items-center gap-2 whitespace-nowrap border-b-2 px-4 py-2.5 text-xs font-semibold transition-all sm:text-sm ${
                isActive
                  ? "border-rose-400 text-rose-400 bg-rose-500/5"
                  : "border-transparent text-slate-400 hover:border-slate-600 hover:text-slate-200"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ── TAB CONTENT CONTAINERS ── */}
      <div className="space-y-6">
        {/* ========================================================================= */}
        {/* TAB 1: SMOKING & AHRR BIOMARKER MODEL                                    */}
        {/* ========================================================================= */}
        {activeTab === "smoking" && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 gap-6 lg:grid-cols-12"
          >
            {/* Left Column: Probe Controls */}
            <div className="space-y-4 rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-5 lg:col-span-6">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Cigarette className="h-4 w-4 text-rose-400" />
                  <h3 className="font-semibold text-white text-sm">
                    {isTr ? "Tütün Biyobelirteç Probları (DNAm β)" : "Tobacco Biomarker Probes (DNAm β)"}
                  </h3>
                </div>
                <span className="font-mono text-xs text-rose-400">Pillar 4 §3.1</span>
              </div>

              {/* AHRR cg05575921 */}
              <div className="space-y-2 rounded-lg border border-tactical-border/30 bg-tactical-bg/40 p-3.5">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-white">
                      <span>AHRR</span>
                      <span className="rounded bg-slate-800 px-1 text-[10px] text-slate-400">
                        cg05575921
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {isTr
                        ? "Birincil tütün hipometilasyon lokusu (intron 1)"
                        : "Primary tobacco hypomethylation driver (intron 1)"}
                    </div>
                  </div>
                  <div className="font-mono text-base font-bold text-rose-400 tabular-nums">
                    {ahrrBeta.toFixed(2)}
                  </div>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.95"
                  step="0.01"
                  value={ahrrBeta}
                  onChange={(e) => setAhrrBeta(parseFloat(e.target.value))}
                  className="w-full accent-rose-500"
                />
                <div className="flex justify-between font-mono text-[10px] text-slate-400">
                  <span>0.10 ({isTr ? "Ağır İçiçi" : "Heavy Smoker"})</span>
                  <span>0.55 (Eşik)</span>
                  <span>0.80 (İçmeyen)</span>
                  <span>0.95</span>
                </div>
              </div>

              {/* F2RL3 cg03636183 */}
              <div className="space-y-2 rounded-lg border border-tactical-border/30 bg-tactical-bg/40 p-3.5">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-white">
                      <span>F2RL3</span>
                      <span className="rounded bg-slate-800 px-1 text-[10px] text-slate-400">
                        cg03636183
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {isTr
                        ? "Koagülasyon proteaz-aktive reseptör 4 lokusu"
                        : "Protease-activated receptor 4 locus"}
                    </div>
                  </div>
                  <div className="font-mono text-base font-bold text-rose-400 tabular-nums">
                    {f2rl3Beta.toFixed(2)}
                  </div>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.95"
                  step="0.01"
                  value={f2rl3Beta}
                  onChange={(e) => setF2rl3Beta(parseFloat(e.target.value))}
                  className="w-full accent-rose-500"
                />
                <div className="flex justify-between font-mono text-[10px] text-slate-400">
                  <span>0.10</span>
                  <span>0.82 (Referans)</span>
                  <span>0.95</span>
                </div>
              </div>

              {/* ALPPL2 cg01940273 */}
              <div className="space-y-2 rounded-lg border border-tactical-border/30 bg-tactical-bg/40 p-3.5">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-white">
                      <span>ALPPL2</span>
                      <span className="rounded bg-slate-800 px-1 text-[10px] text-slate-400">
                        cg01940273
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {isTr
                        ? "Plasental-benzeri alkali fosfataz 2 lokusu"
                        : "Alkaline phosphatase placental-like 2 locus"}
                    </div>
                  </div>
                  <div className="font-mono text-base font-bold text-rose-400 tabular-nums">
                    {alppl2Beta.toFixed(2)}
                  </div>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.95"
                  step="0.01"
                  value={alppl2Beta}
                  onChange={(e) => setAlppl2Beta(parseFloat(e.target.value))}
                  className="w-full accent-rose-500"
                />
                <div className="flex justify-between font-mono text-[10px] text-slate-400">
                  <span>0.10</span>
                  <span>0.84 (Referans)</span>
                  <span>0.95</span>
                </div>
              </div>
            </div>

            {/* Right Column: Model Formula & Sigmoid Probability Curve */}
            <div className="space-y-4 rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-5 lg:col-span-6">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <h3 className="font-semibold text-white text-sm">
                  {isTr ? "Kantitatif Tütün Skoru & Sigmoid Eğrisi" : "Smoking Score & Sigmoid Response Curve"}
                </h3>
                <span className="font-mono text-xs text-slate-400">Score = 10.50 - 9.80β - 2.50β - 1.80β</span>
              </div>

              {/* Dynamic Telemetry Banner */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/50 p-3">
                  <div className="text-[11px] text-slate-400">{isTr ? "Tütün Skoru" : "Smoking Score"}</div>
                  <div className="mt-1 font-mono text-xl font-bold text-white tabular-nums">
                    {calculatedProfile.smokingScore}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    {calculatedProfile.smokingScore > 4.5 ? "> 4.5 (Ağır)" : "< 1.5 (İçmeyen)"}
                  </div>
                </div>

                <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/50 p-3">
                  <div className="text-[11px] text-slate-400">{isTr ? "Tahmini Paket-Yıl" : "Est. Pack-Years"}</div>
                  <div className="mt-1 font-mono text-xl font-bold text-rose-400 tabular-nums">
                    {calculatedProfile.packYearsEst}
                  </div>
                  <div className="text-[10px] text-slate-400">
                    max(0, (0.85 - β)/0.012)
                  </div>
                </div>

                <div className="col-span-2 sm:col-span-1 rounded-lg border border-tactical-border/40 bg-tactical-bg/50 p-3">
                  <div className="text-[11px] text-slate-400">{isTr ? "İçicilik Olasılığı" : "Smoking Probability"}</div>
                  <div className="mt-1 font-mono text-xl font-bold text-emerald-400 tabular-nums">
                    {(calculatedProfile.smokingProbability * 100).toFixed(0)}%
                  </div>
                  <div className="text-[10px] text-slate-400">P(Smoker | β)</div>
                </div>
              </div>

              {/* Interactive SVG Sigmoid Response Curve */}
              <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/60 p-4">
                <div className="mb-2 flex items-center justify-between text-xs text-slate-400 font-mono">
                  <span>{isTr ? "P(Aktif İçici) Sigmoid Tepki Eğrisi" : "P(Current Smoker) Response Curve"}</span>
                  <span>AHRR cg05575921 [0.10 - 0.95]</span>
                </div>

                <div className="relative h-44 w-full">
                  <svg className="h-full w-full overflow-visible" viewBox="0 0 400 160">
                    {/* Grid Lines */}
                    <line x1="40" y1="20" x2="380" y2="20" stroke="#334155" strokeDasharray="3 3" strokeWidth="0.8" />
                    <line x1="40" y1="80" x2="380" y2="80" stroke="#334155" strokeDasharray="3 3" strokeWidth="0.8" />
                    <line x1="40" y1="140" x2="380" y2="140" stroke="#475569" strokeWidth="1" />
                    <line x1="40" y1="20" x2="40" y2="140" stroke="#475569" strokeWidth="1" />

                    {/* Y-Axis Labels */}
                    <text x="32" y="24" fill="#94a3b8" fontSize="10" textAnchor="end" fontFamily="monospace">1.0</text>
                    <text x="32" y="84" fill="#94a3b8" fontSize="10" textAnchor="end" fontFamily="monospace">0.5</text>
                    <text x="32" y="144" fill="#94a3b8" fontSize="10" textAnchor="end" fontFamily="monospace">0.0</text>

                    {/* Threshold Vertical Lines */}
                    {/* Beta = 0.55 -> X = 40 + (0.55 - 0.10) / (0.95 - 0.10) * 340 = 40 + 0.45/0.85 * 340 = 40 + 180 = 220 */}
                    <line x1="220" y1="20" x2="220" y2="140" stroke="#f43f5e" strokeDasharray="4 2" strokeWidth="1.2" opacity="0.6" />
                    <text x="220" y="15" fill="#f43f5e" fontSize="9" textAnchor="middle" fontFamily="monospace">β=0.55</text>

                    {/* Beta = 0.80 -> X = 40 + 0.70/0.85 * 340 = 40 + 280 = 320 */}
                    <line x1="320" y1="20" x2="320" y2="140" stroke="#10b981" strokeDasharray="4 2" strokeWidth="1.2" opacity="0.6" />
                    <text x="320" y="15" fill="#10b981" fontSize="9" textAnchor="middle" fontFamily="monospace">β=0.80</text>

                    {/* Sigmoid Theoretical Path */}
                    {/* P(smoker) = 1 / (1 + exp(12 * (beta - 0.65))) */}
                    <path
                      d={(() => {
                        let path = "";
                        for (let xPx = 40; xPx <= 380; xPx += 4) {
                          const betaNorm = 0.10 + ((xPx - 40) / 340) * 0.85;
                          const p = 1.0 / (1.0 + Math.exp(12.0 * (betaNorm - 0.65)));
                          const yPx = 140 - p * 120;
                          path += `${xPx === 40 ? "M" : "L"} ${xPx} ${yPx.toFixed(1)} `;
                        }
                        return path;
                      })()}
                      fill="none"
                      stroke="#f43f5e"
                      strokeWidth="2.5"
                    />

                    {/* Active Subject Marker */}
                    {(() => {
                      const subjectX = Math.min(380, Math.max(40, 40 + ((ahrrBeta - 0.10) / 0.85) * 340));
                      const pSub = 1.0 / (1.0 + Math.exp(12.0 * (ahrrBeta - 0.65)));
                      const subjectY = 140 - pSub * 120;
                      return (
                        <g>
                          <circle cx={subjectX} cy={subjectY} r="6" fill="#f43f5e" className="animate-pulse" />
                          <circle cx={subjectX} cy={subjectY} r="10" fill="none" stroke="#f43f5e" strokeWidth="1.5" opacity="0.7" />
                          <text x={subjectX} y={subjectY - 12} fill="#ffffff" fontSize="10" textAnchor="middle" fontFamily="monospace" fontWeight="bold">
                            β={ahrrBeta.toFixed(2)}
                          </text>
                        </g>
                      );
                    })()}
                  </svg>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: METABOLIC AXIS & EPIGENETIC BODY MASS INDEX (BMI)                 */}
        {/* ========================================================================= */}
        {activeTab === "metabolic" && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 gap-6 lg:grid-cols-12"
          >
            {/* Left Column: Metabolic Probes */}
            <div className="space-y-4 rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-5 lg:col-span-6">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Scale className="h-4 w-4 text-cyan-400" />
                  <h3 className="font-semibold text-white text-sm">
                    {isTr ? "Lipit & Metabolizma Probları" : "Lipid & Metabolic Probes"}
                  </h3>
                </div>
                <span className="font-mono text-xs text-cyan-400">Pillar 4 §3.2</span>
              </div>

              {/* ABCG1 cg06500161 */}
              <div className="space-y-2 rounded-lg border border-tactical-border/30 bg-tactical-bg/40 p-3.5">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-white">
                      <span>ABCG1</span>
                      <span className="rounded bg-slate-800 px-1 text-[10px] text-slate-400">cg06500161</span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {isTr ? "Kolesterol akış düzenleyicisi (+18.20 katsayı)" : "Cholesterol efflux mediator (+18.20 coeff)"}
                    </div>
                  </div>
                  <div className="font-mono text-base font-bold text-cyan-400 tabular-nums">
                    {abcg1Beta.toFixed(2)}
                  </div>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.90"
                  step="0.01"
                  value={abcg1Beta}
                  onChange={(e) => setAbcg1Beta(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500"
                />
                <div className="flex justify-between font-mono text-[10px] text-slate-400">
                  <span>0.10</span>
                  <span>0.35 (Referans)</span>
                  <span>0.90</span>
                </div>
              </div>

              {/* CPT1A cg00574958 */}
              <div className="space-y-2 rounded-lg border border-tactical-border/30 bg-tactical-bg/40 p-3.5">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-white">
                      <span>CPT1A</span>
                      <span className="rounded bg-slate-800 px-1 text-[10px] text-slate-400">cg00574958</span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {isTr ? "Yağ asidi oksidasyonu (-22.40 katsayı)" : "Fatty acid oxidation (-22.40 coeff)"}
                    </div>
                  </div>
                  <div className="font-mono text-base font-bold text-cyan-400 tabular-nums">
                    {cpt1aBeta.toFixed(2)}
                  </div>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.90"
                  step="0.01"
                  value={cpt1aBeta}
                  onChange={(e) => setCpt1aBeta(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500"
                />
                <div className="flex justify-between font-mono text-[10px] text-slate-400">
                  <span>0.10</span>
                  <span>0.45 (Referans)</span>
                  <span>0.90</span>
                </div>
              </div>

              {/* SREBF1 cg11024682 */}
              <div className="space-y-2 rounded-lg border border-tactical-border/30 bg-tactical-bg/40 p-3.5">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-white">
                      <span>SREBF1</span>
                      <span className="rounded bg-slate-800 px-1 text-[10px] text-slate-400">cg11024682</span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {isTr ? "Sterol düzenleyici eleman (+12.10 katsayı)" : "Sterol regulatory element (+12.10 coeff)"}
                    </div>
                  </div>
                  <div className="font-mono text-base font-bold text-cyan-400 tabular-nums">
                    {srebf1Beta.toFixed(2)}
                  </div>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.90"
                  step="0.01"
                  value={srebf1Beta}
                  onChange={(e) => setSrebf1Beta(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500"
                />
                <div className="flex justify-between font-mono text-[10px] text-slate-400">
                  <span>0.10</span>
                  <span>0.30 (Referans)</span>
                  <span>0.90</span>
                </div>
              </div>
            </div>

            {/* Right Column: Epigenetic BMI Dial Gauge & Delta Age Acceleration */}
            <div className="space-y-4 rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-5 lg:col-span-6">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <h3 className="font-semibold text-white text-sm">
                  {isTr ? "Epigenetik Vücut Kitle İndeksi (BMI) Çizelgesi" : "Epigenetic Body Mass Index (BMI) Dial"}
                </h3>
                <span className="font-mono text-xs text-slate-400">BMI = 24.50 + 18.20β - 22.40β + 12.10β</span>
              </div>

              {/* BMI Gauge Display */}
              <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/60 p-5 flex flex-col items-center justify-center">
                <div className="relative flex flex-col items-center">
                  <div className="font-mono text-4xl font-bold text-white tabular-nums tracking-tight">
                    {calculatedProfile.estimatedBmi}
                  </div>
                  <div className="text-xs text-slate-400">kg/m² (WHO Standard)</div>

                  <div className="mt-3">
                    <span className={`inline-block rounded-full border px-3 py-1 text-xs font-semibold ${getBmiBadge(calculatedProfile.bmiCategory).color}`}>
                      {getBmiBadge(calculatedProfile.bmiCategory).label}
                    </span>
                  </div>
                </div>

                {/* Horizontal Spectrum Bar */}
                <div className="mt-6 w-full space-y-1.5">
                  <div className="relative h-3 w-full rounded-full bg-slate-800 overflow-hidden flex">
                    <div className="h-full bg-cyan-500" style={{ width: "18.5%" }} title="Underweight <18.5" />
                    <div className="h-full bg-emerald-500" style={{ width: "25.0%" }} title="Normal 18.5-24.9" />
                    <div className="h-full bg-amber-500" style={{ width: "20.0%" }} title="Overweight 25.0-29.9" />
                    <div className="h-full bg-rose-500" style={{ width: "18.5%" }} title="Obese I 30.0-34.9" />
                    <div className="h-full bg-purple-500" style={{ width: "18.0%" }} title="Obese II+ >=35.0" />
                  </div>
                  <div className="flex justify-between font-mono text-[10px] text-slate-400">
                    <span>15</span>
                    <span>18.5</span>
                    <span>25.0</span>
                    <span>30.0</span>
                    <span>35.0</span>
                    <span>45+</span>
                  </div>
                </div>
              </div>

              {/* Biological Age Acceleration Delta Box */}
              <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/50 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <HeartPulse className="h-4 w-4 text-rose-400" />
                    <span className="font-semibold text-white text-xs">
                      {isTr ? "Biyolojik Yaş İvmelenmesi (Δ Age)" : "Biological Age Acceleration (Δ Age)"}
                    </span>
                  </div>
                  <span className="font-mono text-xs text-slate-400">Δ = DNAmAge - Kronolojik</span>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-[11px] text-slate-400">
                      {isTr ? "Kronolojik Yaş" : "Chronological Age"}
                    </label>
                    <input
                      type="number"
                      step="0.5"
                      min="18"
                      max="100"
                      value={chronologicalAge}
                      onChange={(e) => setChronologicalAge(parseFloat(e.target.value) || 35)}
                      className="mt-1 w-full rounded border border-tactical-border bg-tactical-bg p-1.5 font-mono text-xs text-white"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400">
                      {isTr ? "Tahmini DNAm Yaşı" : "Estimated DNAm Age"}
                    </label>
                    <input
                      type="number"
                      step="0.5"
                      min="18"
                      max="100"
                      value={estimatedDnamAge}
                      onChange={(e) => setEstimatedDnamAge(parseFloat(e.target.value) || 35)}
                      className="mt-1 w-full rounded border border-tactical-border bg-tactical-bg p-1.5 font-mono text-xs text-white"
                    />
                  </div>
                </div>

                <div className="rounded border border-tactical-border/40 bg-tactical-bg p-2.5 flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">{isTr ? "Sapma Durumu:" : "Drift Classification:"}</span>
                  <span
                    className={
                      calculatedProfile.ageDelta > 5
                        ? "text-rose-400 font-bold"
                        : calculatedProfile.ageDelta < -5
                        ? "text-cyan-400 font-bold"
                        : "text-emerald-400 font-bold"
                    }
                  >
                    {calculatedProfile.ageDelta > 0 ? `+${calculatedProfile.ageDelta}` : calculatedProfile.ageDelta} yrs (
                    {calculatedProfile.agingStatus})
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: ALCOHOL EXPOSURE & CIRCADIAN TIME-OF-DEPOSITION (TOD)              */}
        {/* ========================================================================= */}
        {activeTab === "circadian_alcohol" && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 gap-6 lg:grid-cols-12"
          >
            {/* Left Column: Alcohol Exposure (SLC6A3) */}
            <div className="space-y-4 rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-5 lg:col-span-6">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Wine className="h-4 w-4 text-amber-400" />
                  <h3 className="font-semibold text-white text-sm">
                    {isTr ? "Alkol Maruziyet İndeksi (SLC6A3 DAT1)" : "Alcohol Exposure Index (SLC6A3 DAT1)"}
                  </h3>
                </div>
                <span className="font-mono text-xs text-amber-400">Score = |0.50 - β| × 200</span>
              </div>

              <div className="space-y-2 rounded-lg border border-tactical-border/30 bg-tactical-bg/40 p-3.5">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-1.5 font-mono text-xs font-bold text-white">
                      <span>SLC6A3</span>
                      <span className="rounded bg-slate-800 px-1 text-[10px] text-slate-400">chr5:1.39M</span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {isTr
                        ? "Dopamin taşıyıcı promotor metilasyon kayması"
                        : "Dopamine transporter promoter methylation shift"}
                    </div>
                  </div>
                  <div className="font-mono text-base font-bold text-amber-400 tabular-nums">
                    {slc6a3Beta.toFixed(2)}
                  </div>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.95"
                  step="0.01"
                  value={slc6a3Beta}
                  onChange={(e) => setSlc6a3Beta(parseFloat(e.target.value))}
                  className="w-full accent-amber-500"
                />
                <div className="flex justify-between font-mono text-[10px] text-slate-400">
                  <span>0.05 (Ağır)</span>
                  <span>0.50 (Referans/Tüketmeyen)</span>
                  <span>0.95 (Ağır)</span>
                </div>
              </div>

              {/* Alcohol Classification Display */}
              <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/50 p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">{isTr ? "Hesaplanan Alkol Skoru:" : "Computed Alcohol Score:"}</span>
                  <span className="font-mono text-lg font-bold text-white">{calculatedProfile.alcoholScore}</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden flex">
                  <div className="bg-emerald-500 h-full" style={{ width: "25%" }} />
                  <div className="bg-amber-500 h-full" style={{ width: "25%" }} />
                  <div className="bg-rose-500 h-full" style={{ width: "50%" }} />
                </div>
                <div className="rounded border border-tactical-border/30 bg-tactical-bg p-2 text-center">
                  <span className="font-mono text-xs font-semibold text-amber-400">
                    {calculatedProfile.alcoholLevel === "HEAVY_CHRONIC_EXPOSURE"
                      ? isTr
                        ? "AĞIR KRONİK ALKOL MARUZİYETİ (>40.0)"
                        : "HEAVY CHRONIC ALCOHOL EXPOSURE (>40.0)"
                      : calculatedProfile.alcoholLevel === "MODERATE_EXPOSURE"
                      ? isTr
                        ? "ORTA DÜZEY MARUZİYET (20.0 - 40.0)"
                        : "MODERATE EXPOSURE (20.0 - 40.0)"
                      : isTr
                      ? "DÜŞÜK / TÜKETMEYEN REFERANS (<=20.0)"
                      : "LOW / ABSTAINER REFERENCE (<=20.0)"}
                  </span>
                </div>
              </div>
            </div>

            {/* Right Column: Circadian TOD Window (PER2 / BMAL1) */}
            <div className="space-y-4 rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-5 lg:col-span-6">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-indigo-400" />
                  <h3 className="font-semibold text-white text-sm">
                    {isTr ? "Sirkadiyen Olay Yeri Birikim Zamanı (TOD)" : "Circadian Deposition Window (TOD)"}
                  </h3>
                </div>
                <span className="font-mono text-xs text-indigo-400">Ratio = PER2 / BMAL1</span>
              </div>

              {/* PER2 and BMAL1 Sliders */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1 rounded-lg border border-tactical-border/30 bg-tactical-bg/40 p-3">
                  <div className="flex justify-between text-xs font-mono font-bold text-white">
                    <span>PER2 β</span>
                    <span className="text-indigo-400">{per2Beta.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.10"
                    max="0.90"
                    step="0.01"
                    value={per2Beta}
                    onChange={(e) => setPer2Beta(parseFloat(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                </div>

                <div className="space-y-1 rounded-lg border border-tactical-border/30 bg-tactical-bg/40 p-3">
                  <div className="flex justify-between text-xs font-mono font-bold text-white">
                    <span>BMAL1 β</span>
                    <span className="text-indigo-400">{bmal1Beta.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.10"
                    max="0.90"
                    step="0.01"
                    value={bmal1Beta}
                    onChange={(e) => setBmal1Beta(parseFloat(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                </div>
              </div>

              {/* Circadian 24-Hour Dial Visualization */}
              <div className="rounded-lg border border-tactical-border/40 bg-tactical-bg/60 p-4 flex flex-col items-center justify-center">
                <div className="flex items-center gap-2">
                  {React.createElement(getCircadianBadge(calculatedProfile.circadianPhase).icon, {
                    className: "h-5 w-5 text-indigo-400",
                  })}
                  <span className="font-mono text-base font-bold text-white">
                    {calculatedProfile.todWindow}
                  </span>
                </div>

                <div className="mt-2 text-xs text-slate-400 font-mono text-center">
                  {getCircadianBadge(calculatedProfile.circadianPhase).label}
                </div>

                {/* 24-Hour Sector Diagram */}
                <div className="mt-4 grid grid-cols-3 gap-2 w-full text-center font-mono text-[10px]">
                  <div className={`p-2 rounded border ${calculatedProfile.circadianPhase === "MATUTINAL_PEAK_MORNING" ? "border-amber-500/50 bg-amber-500/20 text-amber-300 font-bold" : "border-tactical-border/40 bg-tactical-bg/40 text-slate-400"}`}>
                    <div>04:00 - 10:00</div>
                    <div>{isTr ? "Sabah" : "Morning"} (Ratio &lt; 0.8)</div>
                  </div>
                  <div className={`p-2 rounded border ${calculatedProfile.circadianPhase === "DIURNAL_PEAK_DAYTIME" ? "border-emerald-500/50 bg-emerald-500/20 text-emerald-300 font-bold" : "border-tactical-border/40 bg-tactical-bg/40 text-slate-400"}`}>
                    <div>10:00 - 16:00</div>
                    <div>{isTr ? "Gündüz" : "Daytime"} (0.8 - 1.2)</div>
                  </div>
                  <div className={`p-2 rounded border ${calculatedProfile.circadianPhase === "NOCTURNAL_PEAK_NIGHT" ? "border-indigo-500/50 bg-indigo-500/20 text-indigo-300 font-bold" : "border-tactical-border/40 bg-tactical-bg/40 text-slate-400"}`}>
                    <div>22:00 - 04:00</div>
                    <div>{isTr ? "Gece" : "Night"} (Ratio &gt; 1.2)</div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: CERTIFIED GOLDEN BENCHMARK VECTORS (VECTORS A - H)                 */}
        {/* ========================================================================= */}
        {activeTab === "benchmarks" && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-5">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-tactical-border/40 pb-3">
                <div>
                  <h3 className="font-semibold text-white text-sm sm:text-base">
                    {isTr ? "Sertifikalı Altın Referans Standartları (Modül 18 / Pillar 4 §6)" : "Certified Golden Benchmark Vectors (Module 18 / Pillar 4 §6)"}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {isTr
                      ? "Pillar 4 Araştırma Şartnamesi Bölüm 6'dan 8 adet standart doğrulanmış referans vektörü."
                      : "8 validated golden benchmark reference profiles from Pillar 4 Research Specification Section 6."}
                  </p>
                </div>
                <span className="font-mono text-xs text-rose-400">VECTOR_18_LIFE_A - H</span>
              </div>

              <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {GOLDEN_LIFESTYLE_VECTORS.map((v) => {
                  const isSelected = selectedVectorId === v.id;
                  return (
                    <div
                      key={v.id}
                      className={`relative flex flex-col justify-between rounded-lg border p-4 transition-all ${
                        isSelected
                          ? "border-rose-500/60 bg-rose-500/10 shadow-[0_0_15px_rgba(244,63,94,0.15)]"
                          : "border-tactical-border/40 bg-tactical-bg/40 hover:border-slate-600"
                      }`}
                    >
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs font-bold text-rose-400">{v.code}</span>
                          {isSelected && <CheckCircle2 className="h-4 w-4 text-rose-400" />}
                        </div>
                        <div className="font-medium text-white text-xs sm:text-sm">
                          {isTr ? v.nameTr : v.name}
                        </div>
                        <p className="text-[11px] text-slate-400 line-clamp-2">
                          {isTr ? v.notesTr : v.notes}
                        </p>

                        <div className="space-y-1 font-mono text-[10px] text-slate-300 border-t border-tactical-border/30 pt-2">
                          <div>AHRR β: {v.ahrrBeta} | F2RL3: {v.f2rl3Beta}</div>
                          <div>ABCG1: {v.abcg1Beta} | CPT1A: {v.cpt1aBeta}</div>
                          <div>SLC6A3: {v.slc6a3Beta} | PER2/BMAL1: {v.per2Beta}/{v.bmal1Beta}</div>
                        </div>
                      </div>

                      <button
                        onClick={() => handleLoadVector(v)}
                        className={`mt-3 w-full min-h-[44px] rounded border py-1.5 text-xs font-semibold transition-all ${
                          isSelected
                            ? "border-rose-400 bg-rose-500/30 text-white"
                            : "border-tactical-border/60 bg-tactical-surface/50 text-slate-300 hover:bg-slate-700"
                        }`}
                      >
                        {isSelected ? (isTr ? "Yüklendi" : "Loaded") : isTr ? "Vektörü Yükle" : "Load Vector"}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}

        {/* ========================================================================= */}
        {/* TAB 5: ISO/IEC 17025 EVALUATIVE REPORTING & LEGAL SHIELD                  */}
        {/* ========================================================================= */}
        {activeTab === "iso_reporting" && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-5 space-y-4">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-tactical-border/40 pb-3">
                <div>
                  <h3 className="font-semibold text-white text-sm sm:text-base">
                    {isTr ? "ISO/IEC 17025 Değerlendirici Adli Rapor" : "ISO/IEC 17025 Evaluative Forensic Report"}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {isTr
                      ? "ENFSI (2017) ve ISO/IEC 17025:2017 standartlarına uygun çevresel epigenetik uzman beyanı."
                      : "Environmental epigenomics expert witness evaluative statement in accordance with ENFSI (2017) and ISO/IEC 17025:2017."}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      const reportText = `FORENZA ADLI EPIGENETIK RAPORU
Sigara Durumu: ${calculatedProfile.smokingStatus} (${calculatedProfile.packYearsEst} Paket-Yil)
Epigenetik BMI: ${calculatedProfile.estimatedBmi} kg/m2 (${calculatedProfile.bmiCategory})
Alkol Indeksi: ${calculatedProfile.alcoholScore} (${calculatedProfile.alcoholLevel})
Sirkadiyen Faz: ${calculatedProfile.circadianPhase} (${calculatedProfile.todWindow})
Yas Sapmasi: ${calculatedProfile.ageDelta} yil (${calculatedProfile.agingStatus})`;
                      handleCopy(reportText, "report");
                    }}
                    className="flex min-h-[44px] items-center gap-1.5 rounded border border-tactical-border bg-tactical-bg px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-700"
                  >
                    {copiedKey === "report" ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>{isTr ? "Raporu Kopyala" : "Copy Report"}</span>
                  </button>
                </div>
              </div>

              {/* Mandatory Prosecutor's Fallacy Shield */}
              <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-4 space-y-1.5">
                <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs sm:text-sm">
                  <ShieldAlert className="h-4 w-4" />
                  <span>
                    {isTr
                      ? "Savcılık Yanılgısı Kalkanı & Adli Yasal Uyarı"
                      : "Prosecutor's Fallacy Shield & Forensic Disclaimer"}
                  </span>
                </div>
                <p className="text-xs text-amber-200/90 leading-relaxed">
                  {isTr
                    ? "ÖNEMLİ (Yaşam Tarzı & Çevresel Epigenetik Yasal Kalkanı): Epigenetik biyobelirteçler fizyolojik maruziyet imzalarını yansıtır (AHRR tütün dumanı, ABCG1/CPT1A metabolik BMI, SLC6A3 alkol ve PER2/BMAL1 sirkadiyen ritim). Bu modeller olasılıksal yaşam tarzı çıkarımları sağlar ve kesin tıbbi teşhis olarak KULLANILAMAZ."
                    : "IMPORTANT (Lifestyle & Environmental Epigenetics Legal Shield): Epigenetic biomarkers reflect physiological exposure signatures (AHRR tobacco smoke, ABCG1/CPT1A metabolic BMI, SLC6A3 alcohol, and PER2/BMAL1 circadian rhythm). These models provide probabilistic lifestyle inferences and must NOT be used as medical diagnoses."}
                </p>
              </div>

              {/* Multi-Metric Evaluative Summary Table */}
              <div className="overflow-x-auto rounded-lg border border-tactical-border/40 bg-tactical-bg/40">
                <table className="w-full text-left font-mono text-xs">
                  <thead className="border-b border-tactical-border/60 bg-tactical-surface/50 text-[11px] text-slate-400">
                    <tr>
                      <th className="p-3">{isTr ? "Biyobelirteç Ekseni" : "Biomarker Axis"}</th>
                      <th className="p-3">{isTr ? "Birincil Prob" : "Primary Probe"}</th>
                      <th className="p-3">{isTr ? "Ölçülen Metilasyon β" : "Measured Methylation β"}</th>
                      <th className="p-3">{isTr ? "Tahmin / Skor" : "Prediction / Score"}</th>
                      <th className="p-3">{isTr ? "Adli Sınıflandırma" : "Forensic Classification"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-tactical-border/30 text-slate-300">
                    <tr>
                      <td className="p-3 font-semibold text-white">{isTr ? "Tütün Dumanı" : "Tobacco Smoke"}</td>
                      <td className="p-3 text-rose-400">AHRR cg05575921</td>
                      <td className="p-3">{ahrrBeta.toFixed(2)}</td>
                      <td className="p-3">{calculatedProfile.packYearsEst} {isTr ? "Paket-Yıl" : "Pack-Years"}</td>
                      <td className="p-3">
                        <span className={`rounded border px-1.5 py-0.5 text-[10px] ${getSmokingBadge(calculatedProfile.smokingStatus).bg}`}>
                          {getSmokingBadge(calculatedProfile.smokingStatus).label}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td className="p-3 font-semibold text-white">{isTr ? "Metabolik BMI" : "Metabolic BMI"}</td>
                      <td className="p-3 text-cyan-400">ABCG1 / CPT1A / SREBF1</td>
                      <td className="p-3">{abcg1Beta.toFixed(2)} / {cpt1aBeta.toFixed(2)} / {srebf1Beta.toFixed(2)}</td>
                      <td className="p-3">{calculatedProfile.estimatedBmi} kg/m²</td>
                      <td className="p-3">
                        <span className={`rounded border px-1.5 py-0.5 text-[10px] ${getBmiBadge(calculatedProfile.bmiCategory).color}`}>
                          {getBmiBadge(calculatedProfile.bmiCategory).label}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td className="p-3 font-semibold text-white">{isTr ? "Alkol Maruziyeti" : "Alcohol Exposure"}</td>
                      <td className="p-3 text-amber-400">SLC6A3 DAT1</td>
                      <td className="p-3">{slc6a3Beta.toFixed(2)}</td>
                      <td className="p-3">{calculatedProfile.alcoholScore} ({isTr ? "İndeks" : "Index"})</td>
                      <td className="p-3 font-semibold text-amber-300">{calculatedProfile.alcoholLevel}</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-semibold text-white">{isTr ? "Sirkadiyen TOD" : "Circadian TOD"}</td>
                      <td className="p-3 text-indigo-400">PER2 / BMAL1</td>
                      <td className="p-3">{per2Beta.toFixed(2)} / {bmal1Beta.toFixed(2)}</td>
                      <td className="p-3">{calculatedProfile.circadianRatio} ({isTr ? "Oran" : "Ratio"})</td>
                      <td className="p-3 font-semibold text-indigo-300">{calculatedProfile.todWindow}</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-semibold text-white">{isTr ? "Biyolojik Yaş Sapması" : "Age Acceleration"}</td>
                      <td className="p-3 text-emerald-400">Δ Age (DNAm - Chrono)</td>
                      <td className="p-3">{estimatedDnamAge} - {chronologicalAge}</td>
                      <td className="p-3">{calculatedProfile.ageDelta > 0 ? `+${calculatedProfile.ageDelta}` : calculatedProfile.ageDelta} yrs</td>
                      <td className="p-3 font-semibold text-emerald-300">{calculatedProfile.agingStatus}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
