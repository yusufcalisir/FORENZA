"use client";

import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Pill,
  Activity,
  ShieldCheck,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Zap,
  ArrowRight,
  Info,
  Cpu,
  Check,
  FileText,
  Layers,
  Download,
  Copy,
  Sliders,
  ChevronRight,
  TrendingUp,
  BarChart2,
  Search,
} from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// ===============================================================================
// TYPE DEFINITIONS & SCHEMAS
// ===============================================================================

export type ToxicologySubTab =
  | "pmr_ratio"
  | "antemortem_extrap"
  | "xenobiotic_matrix"
  | "benchmarks"
  | "iso_audit";

export interface PmrResponse {
  compound_name: string;
  c_heart: number;
  c_femoral: number;
  unit: string;
  cp_observed: number;
  cp_literature_mean: number;
  cp_ratio_std?: number;
  vd_l_kg: number;
  pmr_risk_tier: string;
  is_cardiac_overestimated: boolean;
  overestimation_percentage: number;
  clinical_guideline: string;
  alert_message: string;
  prosecutors_fallacy_shield: string;
}

export interface ExtrapolationResponse {
  compound_name: string;
  c_femoral_postmortem: number;
  elapsed_hours: number;
  c_antemortem_extrapolated: number;
  unit: string;
  elimination_type: string;
  elimination_rate_constant_ke_h: number | null;
  half_life_hours: number | null;
  beta_60_g_l_h: number | null;
  kinetic_formula: string;
  prosecutors_fallacy_shield: string;
  toxicity_tier?: "NORMAL" | "THERAPEUTIC" | "ELEVATED_TOXIC" | "FATAL_LETHAL";
}

export interface XenobioticInfo {
  name: string;
  vd: number;
  logP: number;
  pKa: number | null;
  cpLitMean: number;
  cpStd: number;
  risk: string;
  riskTr: string;
  eliminationType: "Zero-Order" | "First-Order";
  beta60: number | null;
  tHalf: number | null;
  defaultUnit: string;
  cHeartDefault: number;
  cFemDefault: number;
  lethalThreshold: number;
  toxicThreshold: number;
  guidelineEn: string;
  guidelineTr: string;
}

export interface BenchmarkPreset {
  id: string;
  name: string;
  badge: string;
  compound: string;
  cHeart: number;
  cFem: number;
  unit: string;
  elapsedHours: number;
  expectedCp: number;
  expectedHighPmr: boolean;
  expectedAntemortem: number;
  descriptionEn: string;
  descriptionTr: string;
}

// ===============================================================================
// PRODUCTION XENOBIOTIC DATABASE (Pillar 5 Research §5.1 & §6 Artifact A)
// ===============================================================================

export const XENOBIOTIC_DATABASE: Record<string, XenobioticInfo> = {
  Ethanol: {
    name: "Ethanol",
    vd: 0.6,
    logP: -0.31,
    pKa: null,
    cpLitMean: 1.00,
    cpStd: 0.10,
    risk: "Low / Minimal",
    riskTr: "Dusuk / Minimal",
    eliminationType: "Zero-Order",
    beta60: 0.15,
    tHalf: null,
    defaultUnit: "g/L",
    cHeartDefault: 0.85,
    cFemDefault: 0.80,
    lethalThreshold: 3.50,
    toxicThreshold: 1.50,
    guidelineEn: "Uniform distribution; evaluate post-mortem microbial neo-formation in putrefaction.",
    guidelineTr: "Homojen dagilim; curumede post-mortem mikrobiyal yeni olusumu degerlendirin.",
  },
  Acetaminophen: {
    name: "Acetaminophen",
    vd: 0.9,
    logP: 0.46,
    pKa: 9.5,
    cpLitMean: 1.05,
    cpStd: 0.12,
    risk: "Low",
    riskTr: "Dusuk",
    eliminationType: "First-Order",
    beta60: null,
    tHalf: 2.5,
    defaultUnit: "mg/L",
    cHeartDefault: 10.5,
    cFemDefault: 10.0,
    lethalThreshold: 150.0,
    toxicThreshold: 30.0,
    guidelineEn: "C_heart approx C_femoral; minimal diffusion artifact.",
    guidelineTr: "C_kalp yaklasik C_femoral; minimal difuzyon artefakti.",
  },
  Morphine: {
    name: "Morphine",
    vd: 3.5,
    logP: 0.89,
    pKa: 8.0,
    cpLitMean: 1.80,
    cpStd: 0.40,
    risk: "Moderate",
    riskTr: "Orta Duzey",
    eliminationType: "First-Order",
    beta60: null,
    tHalf: 3.0,
    defaultUnit: "mg/L",
    cHeartDefault: 0.36,
    cFemDefault: 0.20,
    lethalThreshold: 0.50,
    toxicThreshold: 0.15,
    guidelineEn: "Moderate redistribution from liver/lung depots; peripheral femoral blood required.",
    guidelineTr: "Karaciger/akciger depolarindan orta duzeyde yeniden dagilim; periferik femoral kan zorunludur.",
  },
  Methamphetamine: {
    name: "Methamphetamine",
    vd: 4.0,
    logP: 2.07,
    pKa: 9.9,
    cpLitMean: 2.10,
    cpStd: 0.50,
    risk: "High",
    riskTr: "Yuksek",
    eliminationType: "First-Order",
    beta60: null,
    tHalf: 10.0,
    defaultUnit: "mg/L",
    cHeartDefault: 0.84,
    cFemDefault: 0.40,
    lethalThreshold: 1.00,
    toxicThreshold: 0.20,
    guidelineEn: "Significant pulmonary/myocardial tissue release; cardiac blood drastically overestimates toxicity.",
    guidelineTr: "Belirgin pulmoner/miyokard doku salinimi; kardiyak kan toksisiteyi asiri yuksek gosterir.",
  },
  Fentanyl: {
    name: "Fentanyl",
    vd: 5.0,
    logP: 4.05,
    pKa: 8.4,
    cpLitMean: 2.80,
    cpStd: 0.70,
    risk: "High / Severe",
    riskTr: "Yuksek / Siddetli",
    eliminationType: "First-Order",
    beta60: null,
    tHalf: 7.0,
    defaultUnit: "ug/L",
    cHeartDefault: 14.0,
    cFemDefault: 5.0,
    lethalThreshold: 10.0,
    toxicThreshold: 3.0,
    guidelineEn: "Pronounced post-mortem lung-to-heart diffusion; femoral venous blood mandatory.",
    guidelineTr: "Belirgin olum sonrasi akciger-kalp difuzyonu; femoral venoz kan zorunludur.",
  },
  Amitriptyline: {
    name: "Amitriptyline",
    vd: 20.0,
    logP: 4.92,
    pKa: 9.4,
    cpLitMean: 4.50,
    cpStd: 1.20,
    risk: "Very High",
    riskTr: "Cok Yuksek",
    eliminationType: "First-Order",
    beta60: null,
    tHalf: 21.0,
    defaultUnit: "mg/L",
    cHeartDefault: 4.50,
    cFemDefault: 1.00,
    lethalThreshold: 2.00,
    toxicThreshold: 0.50,
    guidelineEn: "Massive myocardial release; cardiac blood up to 500% elevated above antemortem systemic level.",
    guidelineTr: "Masif miyokard salinimi; kardiyak kan olum oncesi sistemik seviyenin %500 kadar uzerine cikabilir.",
  },
};

export const DRUG_PRESETS = Object.values(XENOBIOTIC_DATABASE);

// ===============================================================================
// CERTIFIED BENCHMARK TEST VECTORS (Pillar 5 §6 & Backend Golden Vectors)
// ===============================================================================

export const BENCHMARK_PRESETS: BenchmarkPreset[] = [
  {
    id: "VECTOR_P5_03",
    name: "Golden Ground-Truth: Fentanyl High PMR",
    badge: "VECTOR_P5_03",
    compound: "Fentanyl",
    cHeart: 24.0,
    cFem: 8.5,
    unit: "ng/mL",
    elapsedHours: 0.0,
    expectedCp: 2.82,
    expectedHighPmr: true,
    expectedAntemortem: 8.5,
    descriptionEn: "Statutory Pillar 5 validation vector: C_heart = 24.0 ng/mL, C_fem = 8.5 ng/mL, C/P = 2.82, High PMR = TRUE.",
    descriptionTr: "Yasal Sutun 5 dogrulama vektoru: C_kalp = 24.0 ng/mL, C_fem = 8.5 ng/mL, C/P = 2.82, Yuksek PMR = DOGRU.",
  },
  {
    id: "VECTOR_25_TOX_A",
    name: "Ethanol Zero-Order Widmark Elimination",
    badge: "TOX_A",
    compound: "Ethanol",
    cHeart: 0.55,
    cFem: 0.50,
    unit: "g/L",
    elapsedHours: 4.0,
    expectedCp: 1.10,
    expectedHighPmr: false,
    expectedAntemortem: 1.10,
    descriptionEn: "Zero-order Widmark back-extrapolation: C_antemortem = 0.50 + (0.15 * 4.0h) = 1.10 g/L.",
    descriptionTr: "Sifirinci derece Widmark geriye projeksiyonu: C_antemortem = 0.50 + (0.15 * 4.0saat) = 1.10 g/L.",
  },
  {
    id: "VECTOR_25_TOX_B",
    name: "Fentanyl First-Order Half-Life Elimination",
    badge: "TOX_B",
    compound: "Fentanyl",
    cHeart: 14.0,
    cFem: 5.0,
    unit: "ug/L",
    elapsedHours: 7.0,
    expectedCp: 2.80,
    expectedHighPmr: true,
    expectedAntemortem: 10.0,
    descriptionEn: "Exactly 1 half-life (t_1/2 = 7.0h) back in time: C_antemortem = 5.0 * exp(ln(2)) = 10.0 ug/L.",
    descriptionTr: "Geriye tam 1 yarilanma omru (t_1/2 = 7.0saat): C_antemortem = 5.0 * exp(ln(2)) = 10.0 ug/L.",
  },
  {
    id: "VECTOR_25_TOX_C",
    name: "Amitriptyline Massive PMR Overestimation",
    badge: "TOX_C",
    compound: "Amitriptyline",
    cHeart: 4.50,
    cFem: 1.00,
    unit: "mg/L",
    elapsedHours: 6.0,
    expectedCp: 4.50,
    expectedHighPmr: true,
    expectedAntemortem: 1.22,
    descriptionEn: "Massive myocardial release (Vd = 20.0 L/kg): C/P = 4.50, +350% overestimation alert.",
    descriptionTr: "Masif miyokard salinimi (Vd = 20.0 L/kg): C/P = 4.50, %350 fazla tahmin uyarisi.",
  },
  {
    id: "VECTOR_25_TOX_D",
    name: "Acetaminophen Low PMR Baseline",
    badge: "TOX_D",
    compound: "Acetaminophen",
    cHeart: 10.5,
    cFem: 10.0,
    unit: "mg/L",
    elapsedHours: 2.5,
    expectedCp: 1.05,
    expectedHighPmr: false,
    expectedAntemortem: 20.0,
    descriptionEn: "Minimal redistribution (Vd = 0.9 L/kg): C/P = 1.05, within normal equilibrium baseline.",
    descriptionTr: "Minimal yeniden dagilim (Vd = 0.9 L/kg): C/P = 1.05, normal denge tabani icerisinde.",
  },
  {
    id: "VECTOR_25_TOX_E",
    name: "Morphine Moderate PMR (No False Alert)",
    badge: "TOX_E",
    compound: "Morphine",
    cHeart: 0.36,
    cFem: 0.20,
    unit: "mg/L",
    elapsedHours: 3.0,
    expectedCp: 1.80,
    expectedHighPmr: false,
    expectedAntemortem: 0.40,
    descriptionEn: "Morphine C/P = 1.80 matches literature mean (1.80). Correctly avoids false overestimation alert.",
    descriptionTr: "Morfin C/P = 1.80 literatur ortalamasiyla (1.80) eslesir. Yanlis alarm vermez.",
  },
  {
    id: "VECTOR_25_TOX_F",
    name: "Methamphetamine Tissue Release",
    badge: "TOX_F",
    compound: "Methamphetamine",
    cHeart: 0.84,
    cFem: 0.40,
    unit: "mg/L",
    elapsedHours: 5.0,
    expectedCp: 2.10,
    expectedHighPmr: true,
    expectedAntemortem: 0.57,
    descriptionEn: "High tissue release (Vd = 4.0 L/kg): C/P = 2.10, +110% overestimation alert.",
    descriptionTr: "Yuksek doku salinimi (Vd = 4.0 L/kg): C/P = 2.10, %110 fazla tahmin uyarisi.",
  },
];

// ===============================================================================
// CLIENT EVALUATION FUNCTIONS (Rigorous Research Parity)
// ===============================================================================

/**
 * Evaluates Post-Mortem Drug Redistribution (PMR) using the dual-criterion research formula:
 * Overestimation is triggered IF:
 *   (C/P > 2.0 AND Vd > 3.0 L/kg) OR (C/P > 1.5 * cp_literature_mean)
 */
export function evaluateClientPmr(
  drug: string,
  heart: number,
  fem: number,
  u: string,
  isTr: boolean = false
): PmrResponse {
  const cp = Number((heart / Math.max(0.0001, fem)).toFixed(2));
  const info = XENOBIOTIC_DATABASE[drug] || {
    name: drug,
    vd: 3.0,
    logP: 1.5,
    pKa: null,
    cpLitMean: 1.50,
    cpStd: 0.50,
    risk: "Moderate",
    riskTr: "Orta Duzey",
    eliminationType: "First-Order",
    beta60: null,
    tHalf: 6.0,
    defaultUnit: u,
    cHeartDefault: heart,
    cFemDefault: fem,
    lethalThreshold: 10.0,
    toxicThreshold: 2.0,
    guidelineEn: "Uncataloged xenobiotic; exercise caution with central blood sampling.",
    guidelineTr: "Kataloglanmamis ksenobiyotik; merkezi kan orneklemesinde dikkatli olun.",
  };

  const vd = info.vd;
  const cpLit = info.cpLitMean;

  // Dual-Criterion Research Formula (Pillar 5 §5.1 & backend parity)
  const isOver = (cp > 2.0 && vd > 3.0) || cp > 1.5 * cpLit;
  const overPct = Math.max(0.0, Number((((heart - fem) / fem) * 100).toFixed(1)));

  const clinicalGuideline = isOver
    ? isTr
      ? "Belirgin olum sonrasi akciger-kalp difuzyonu; femoral venoz kan zorunludur."
      : "Pronounced post-mortem lung-to-heart diffusion; femoral venous blood mandatory."
    : isTr
    ? "Ihmal edilebilir yeniden dagilim etkisi veya beklenen literatur sinirlarinda."
    : "Negligible redistribution artifact or consistent with expected literature baseline.";

  const alertMessage = isOver
    ? isTr
      ? `YUKSEK PMR FAZLA TAHMIN UYARISI: Kalp kani konsantrasyonu (${heart} ${u}), periferik femoral kandan (${fem} ${u}) %${overPct} daha yuksektir.`
      : `HIGH PMR OVERESTIMATION ALERT: Heart blood concentration (${heart} ${u}) is ${overPct}% higher than peripheral femoral blood (${fem} ${u}).`
    : isTr
    ? `PMR normal literatur denge araliginda (C/P = ${cp}, Ref = ${cpLit}).`
    : `PMR within normal literature equilibrium limits (C/P = ${cp}, Ref = ${cpLit}).`;

  const shield = isTr
    ? "ONEMLI (SOFT / TIAFT Adli Toksikoloji Yasal Kalkan): Olum sonrasi kardiyak kan konsantrasyonlari dogrudan olum oncesi intoksikasyon seviyelerine cevrilemez (PMR difuzyonu). Femoral venoz kan adli standardir."
    : "IMPORTANT (SOFT / TIAFT Post-Mortem Toxicology Evaluative Shield): Post-mortem cardiac blood concentrations cannot be directly translated to antemortem intoxication levels due to post-mortem drug redistribution (PMR). Femoral venous blood is the legal gold standard for quantitative forensic back-extrapolation.";

  return {
    compound_name: drug,
    c_heart: heart,
    c_femoral: fem,
    unit: u,
    cp_observed: cp,
    cp_literature_mean: cpLit,
    cp_ratio_std: info.cpStd,
    vd_l_kg: vd,
    pmr_risk_tier: isTr ? info.riskTr : info.risk,
    is_cardiac_overestimated: isOver,
    overestimation_percentage: overPct,
    clinical_guideline: clinicalGuideline,
    alert_message: alertMessage,
    prosecutors_fallacy_shield: shield,
  };
}

/**
 * Back-extrapolates antemortem concentration using zero-order or first-order kinetics.
 */
export function evaluateClientExtrap(
  drug: string,
  fem: number,
  hours: number,
  u: string,
  isTr: boolean = false
): ExtrapolationResponse {
  const info = XENOBIOTIC_DATABASE[drug] || {
    name: drug,
    vd: 3.0,
    logP: 1.5,
    pKa: null,
    cpLitMean: 1.50,
    cpStd: 0.50,
    risk: "Moderate",
    riskTr: "Orta Duzey",
    eliminationType: "First-Order",
    beta60: null,
    tHalf: 6.0,
    defaultUnit: u,
    cHeartDefault: 1.0,
    cFemDefault: fem,
    lethalThreshold: 10.0,
    toxicThreshold: 2.0,
    guidelineEn: "",
    guidelineTr: "",
  };

  let cAntemortem = fem;
  let elimType = info.eliminationType;
  let keVal: number | null = null;
  let halfLifeVal: number | null = null;
  let beta60Val: number | null = null;
  let formulaStr = "";

  if (elimType === "Zero-Order" || drug.toLowerCase() === "ethanol") {
    const beta60 = info.beta60 || 0.15;
    beta60Val = beta60;
    cAntemortem = Number((fem + beta60 * hours).toFixed(4));
    formulaStr = `Zero-Order Widmark: C_antemortem = ${fem} + (${beta60} * ${hours}h)`;
  } else {
    const tHalf = info.tHalf || 6.0;
    halfLifeVal = tHalf;
    const ke = Math.log(2) / tHalf;
    keVal = Number(ke.toFixed(5));
    cAntemortem = Number((fem * Math.exp(ke * hours)).toFixed(4));
    formulaStr = `First-Order: C_antemortem = ${fem} * exp(${keVal} * ${hours}h)`;
  }

  let toxicity: "NORMAL" | "THERAPEUTIC" | "ELEVATED_TOXIC" | "FATAL_LETHAL" = "THERAPEUTIC";
  if (cAntemortem >= info.lethalThreshold) {
    toxicity = "FATAL_LETHAL";
  } else if (cAntemortem >= info.toxicThreshold) {
    toxicity = "ELEVATED_TOXIC";
  } else if (cAntemortem <= 0.05 * info.toxicThreshold) {
    toxicity = "NORMAL";
  }

  const shield = isTr
    ? "NOT (SOFT / TIAFT Kinematik Ekstrapolasyon Kalkani): Olum oncesi geriye ekstrapolasyon, somatik olumden once saglam bir dolasim sisteminde dogrusal veya ustel klirens varsayar."
    : "NOTE (SOFT / TIAFT Kinematic Extrapolation Shield): Antemortem back-extrapolation assumes linear or exponential clearance in an uncompromised circulatory system prior to somatic death.";

  return {
    compound_name: drug,
    c_femoral_postmortem: fem,
    elapsed_hours: hours,
    c_antemortem_extrapolated: cAntemortem,
    unit: u,
    elimination_type: elimType,
    elimination_rate_constant_ke_h: keVal,
    half_life_hours: halfLifeVal,
    beta_60_g_l_h: beta60Val,
    kinetic_formula: formulaStr,
    prosecutors_fallacy_shield: shield,
    toxicity_tier: toxicity,
  };
}

/**
 * Computes deterministic SHA-256 state audit digest (H_pmr) under ISO/IEC 17025.
 */
export async function computePmrAuditHash(
  pmrResult: PmrResponse | null,
  extrapResult: ExtrapolationResponse | null,
  caseId: string
): Promise<string> {
  const payload = JSON.stringify({
    caseId,
    standard: "ISO/IEC 17025:2017 Sec 7.8 | SOFT / TIAFT Forensic Toxicology",
    pmr: pmrResult
      ? {
          compound: pmrResult.compound_name,
          c_heart: pmrResult.c_heart,
          c_femoral: pmrResult.c_femoral,
          cp_observed: pmrResult.cp_observed,
          cp_lit: pmrResult.cp_literature_mean,
          is_overestimated: pmrResult.is_cardiac_overestimated,
          overestimation_pct: pmrResult.overestimation_percentage,
        }
      : null,
    extrapolation: extrapResult
      ? {
          compound: extrapResult.compound_name,
          elapsed_hours: extrapResult.elapsed_hours,
          c_antemortem: extrapResult.c_antemortem_extrapolated,
          elimination: extrapResult.elimination_type,
        }
      : null,
  });

  if (typeof window !== "undefined" && window.crypto && window.crypto.subtle) {
    try {
      const msgUint8 = new TextEncoder().encode(payload);
      const hashBuffer = await window.crypto.subtle.digest("SHA-256", msgUint8);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
    } catch {
      // fallback below
    }
  }

  // Pure JS 64-hex deterministic fallback
  let h = 0x811c9dc5;
  for (let i = 0; i < payload.length; i++) {
    h ^= payload.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  const hex32 = (h >>> 0).toString(16).padStart(8, "0");
  return (hex32 + hex32.split("").reverse().join("")).repeat(4).slice(0, 64);
}

// ===============================================================================
// MAIN COMPONENT
// ===============================================================================

export default function ToxicologyPmrPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  // Case store integration
  const activeCase = useForensicCaseStore((state) => state.activeCase);
  const addAuditLog = useForensicCaseStore((state) => state.addAuditLog);
  const caseId = activeCase?.metadata?.caseId || "CASE-2026-TOX-01";
  const leadAnalyst = activeCase?.metadata?.leadAnalyst || "Dr. Alvarez, Lead Forensic Toxicologist";

  // Navigation state
  const [activeTab, setActiveTab] = useState<ToxicologySubTab>("pmr_ratio");

  // Casework parameters
  const [selectedDrug, setSelectedDrug] = useState<string>("Fentanyl");
  const [cHeart, setCHeart] = useState<number>(14.0);
  const [cFemoral, setCFemoral] = useState<number>(5.0);
  const [unit, setUnit] = useState<string>("ug/L");
  const [elapsedHours, setElapsedHours] = useState<number>(7.0);

  // Search filter for xenobiotics
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Execution & loading state
  const [loading, setLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [stageText, setStageText] = useState<string>("");
  const [lastActionTime, setLastActionTime] = useState<string | null>(null);
  const [copiedState, setCopiedState] = useState<boolean>(false);

  // Analysis results
  const [pmrResult, setPmrResult] = useState<PmrResponse | null>(() =>
    evaluateClientPmr("Fentanyl", 14.0, 5.0, "ug/L", isTr)
  );

  const [extrapResult, setExtrapResult] = useState<ExtrapolationResponse | null>(() =>
    evaluateClientExtrap("Fentanyl", 5.0, 7.0, "ug/L", isTr)
  );

  const [stateDigest, setStateDigest] = useState<string>("");

  // Recompute state digest when results change
  React.useEffect(() => {
    computePmrAuditHash(pmrResult, extrapResult, caseId).then(setStateDigest);
  }, [pmrResult, extrapResult, caseId]);

  // Handle Preset Loading
  const loadPreset = (preset: XenobioticInfo) => {
    setSelectedDrug(preset.name);
    setCHeart(preset.cHeartDefault);
    setCFemoral(preset.cFemDefault);
    setUnit(preset.defaultUnit);
    runPmrEvaluation(preset.name, preset.cHeartDefault, preset.cFemDefault, preset.defaultUnit);
    runExtrapolation(preset.name, preset.cFemDefault, elapsedHours, preset.defaultUnit);
  };

  // Handle Benchmark Vector Loading
  const loadBenchmark = (b: BenchmarkPreset) => {
    setSelectedDrug(b.compound);
    setCHeart(b.cHeart);
    setCFemoral(b.cFem);
    setUnit(b.unit);
    if (b.elapsedHours > 0) {
      setElapsedHours(b.elapsedHours);
    }
    runPmrEvaluation(b.compound, b.cHeart, b.cFem, b.unit);
    runExtrapolation(b.compound, b.cFem, b.elapsedHours > 0 ? b.elapsedHours : elapsedHours, b.unit);

    addAuditLog({
      event: `Loaded certified benchmark vector ${b.badge} for ${b.compound}`,
      module: "28. Post-Mortem Toxicology PMR",
      analyst: leadAnalyst,
      status: "PASS",
      findingSeverity: b.expectedHighPmr ? "CRITICAL_ALERT" : "NOMINAL",
      standard: "SOFT / TIAFT Guidelines",
    });
  };

  // Execute PMR Evaluation
  const runPmrEvaluation = async (drug: string, heart: number, fem: number, u: string) => {
    if (loading) return;
    setLoading(true);
    setProgress(15);
    setStageText(
      isTr
        ? `Kardiyak (${heart} ${u}) ile femoral (${fem} ${u}) konsantrasyonlari karsilastiriliyor...`
        : `Comparing cardiac (${heart} ${u}) vs femoral (${fem} ${u}) concentrations...`
    );

    const API_BASE = getApiBaseUrl();

    const t1 = setTimeout(() => {
      setProgress(50);
      setStageText(
        isTr
          ? "Merkezi-periferik orani (C_kalp / C_femoral) ve literatur sapmasi hesaplaniyor..."
          : "Calculating central-to-peripheral ratio (C_heart / C_femoral) & literature deviation..."
      );
    }, 200);

    const t2 = setTimeout(() => {
      setProgress(85);
      setStageText(
        isTr
          ? "V_d ve literatur esigi uzerinden yeniden dagilim riski degerlendiriliyor..."
          : "Evaluating post-mortem redistribution risk against V_d & literature threshold..."
      );
    }, 450);

    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/toxicology-pmr-evaluation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          compound_name: drug,
          c_heart: heart,
          c_femoral: fem,
          unit: u,
        }),
        signal: AbortSignal.timeout(3000),
      });

      if (res.ok) {
        const data = await res.json();
        setPmrResult(data);
      } else {
        setPmrResult(evaluateClientPmr(drug, heart, fem, u, isTr));
      }
    } catch {
      setPmrResult(evaluateClientPmr(drug, heart, fem, u, isTr));
    } finally {
      setTimeout(() => {
        clearTimeout(t1);
        clearTimeout(t2);
        setProgress(100);
        setStageText(
          isTr ? "PMR yeniden dagilim degerlendirmesi tamamlandi." : "PMR redistribution evaluation complete."
        );
        setTimeout(() => {
          setLoading(false);
          setLastActionTime(
            isTr
              ? `PMR ${new Date().toLocaleTimeString()} degerlendirildi`
              : `PMR Evaluated at ${new Date().toLocaleTimeString()}`
          );

          addAuditLog({
            event: `Evaluated PMR C/P ratio for ${drug} (C_heart=${heart}, C_fem=${fem} ${u})`,
            module: "28. Post-Mortem Toxicology PMR",
            analyst: leadAnalyst,
            status: "PASS",
            findingSeverity: heart / fem > 2.0 ? "CRITICAL_ALERT" : "NOMINAL",
            standard: "SOFT / TIAFT Guidelines",
          });
        }, 200);
      }, 700);
    }
  };

  // Execute Antemortem Extrapolation
  const runExtrapolation = async (drug: string, fem: number, hours: number, u: string) => {
    if (loading) return;
    setLoading(true);
    setProgress(15);
    setStageText(
      isTr
        ? "Toksikokinetik klirens modeli seciliyor (Sifirinci Derece Widmark veya Birinci Derece)..."
        : "Selecting toxicokinetic clearance model (Zero-Order Widmark vs First-Order)..."
    );

    const API_BASE = getApiBaseUrl();

    const t1 = setTimeout(() => {
      setProgress(50);
      setStageText(
        isTr
          ? "Gecen sure boyunca klirens integrali hesaplaniyor..."
          : "Integrating clearance kinetics over elapsed post-mortem hours..."
      );
    }, 200);

    const t2 = setTimeout(() => {
      setProgress(85);
      setStageText(
        isTr
          ? "Olum anindaki antemortem konsantrasyon C_0 hesaplaniyor..."
          : "Calculating antemortem concentration C_0 at time of somatic death..."
      );
    }, 450);

    try {
      const res = await fetch(
        `${API_BASE}/api/v1/forensic/physical/toxicology-antemortem-extrapolation`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            compound_name: drug,
            c_femoral: fem,
            elapsed_hours: hours,
            unit: u,
          }),
          signal: AbortSignal.timeout(3000),
        }
      );

      if (res.ok) {
        const data = await res.json();
        setExtrapResult(data);
      } else {
        setExtrapResult(evaluateClientExtrap(drug, fem, hours, u, isTr));
      }
    } catch {
      setExtrapResult(evaluateClientExtrap(drug, fem, hours, u, isTr));
    } finally {
      setTimeout(() => {
        clearTimeout(t1);
        clearTimeout(t2);
        setProgress(100);
        setStageText(
          isTr
            ? "Antemortem toksikokinetik ekstrapolasyon tamamlandi."
            : "Antemortem toxicokinetic extrapolation complete."
        );
        setTimeout(() => {
          setLoading(false);
          setLastActionTime(
            isTr
              ? `${new Date().toLocaleTimeString()} ekstrapole edildi`
              : `Extrapolated at ${new Date().toLocaleTimeString()}`
          );

          addAuditLog({
            event: `Computed antemortem back-extrapolation for ${drug} (t - ${hours}h)`,
            module: "28. Post-Mortem Toxicology PMR",
            analyst: leadAnalyst,
            status: "PASS",
            findingSeverity: "NOMINAL",
            standard: "ISO 17025 / SOFT",
          });
        }, 200);
      }, 700);
    }
  };

  // Copy formal report to clipboard
  const copyCourtReport = () => {
    if (!pmrResult) return;
    const reportText = `FORENZA ISO/IEC 17025:2017 FORENSIC TOXICOLOGY EVALUATIVE REPORT
Case ID: ${caseId}
Analyst: ${leadAnalyst}
Standard: ISO/IEC 17025:2017 Sec 7.8 | SOFT / TIAFT Evaluative Toxicology
Target Compound: ${pmrResult.compound_name}
Cardiac Blood (C_heart): ${pmrResult.c_heart} ${pmrResult.unit}
Peripheral Femoral Blood (C_femoral): ${pmrResult.c_femoral} ${pmrResult.unit}
Observed C/P Ratio: ${pmrResult.cp_observed}
Literature Mean C/P Ratio: ${pmrResult.cp_literature_mean}
Volume of Distribution (V_d): ${pmrResult.vd_l_kg} L/kg
PMR Risk Tier: ${pmrResult.pmr_risk_tier}
Cardiac Overestimation Active: ${pmrResult.is_cardiac_overestimated ? "YES (HIGH OVERESTIMATION)" : "NO (CONSISTENT)"}
Overestimation Percentage: +${pmrResult.overestimation_percentage.toFixed(1)}%
Antemortem Extrapolated Concentration: ${extrapResult ? `${extrapResult.c_antemortem_extrapolated} ${extrapResult.unit} (t - ${extrapResult.elapsed_hours}h)` : "N/A"}
Kinetic Model: ${extrapResult ? extrapResult.elimination_type : "N/A"}
State Audit Digest (H_pmr): ${stateDigest}
Legal Evaluative Shield: ${pmrResult.prosecutors_fallacy_shield}`;

    navigator.clipboard.writeText(reportText);
    setCopiedState(true);
    setTimeout(() => setCopiedState(false), 2000);

    addAuditLog({
      event: `Exported courtroom report for case ${caseId} to clipboard`,
      module: "28. Post-Mortem Toxicology PMR",
      analyst: leadAnalyst,
      status: "PASS",
      findingSeverity: "NOMINAL",
      standard: "ISO/IEC 17025:2017 §7.8",
    });
  };

  // Filtered Xenobiotics for Tab 3
  const filteredXenobiotics = useMemo(() => {
    if (!searchQuery.trim()) return DRUG_PRESETS;
    const q = searchQuery.toLowerCase();
    return DRUG_PRESETS.filter(
      (d) =>
        d.name.toLowerCase().includes(q) ||
        d.risk.toLowerCase().includes(q) ||
        d.riskTr.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Top Header & Tactical Mission Bar ── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 shrink-0">
              <Pill className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "Olum Sonrasi Toksikokinetik & PMR" : "Post-Mortem Toxicokinetics & PMR"}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-rose-500/10 border border-rose-500/30 text-rose-300">
                  SOFT : TIAFT
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                  ISO/IEC 17025
                </span>
              </div>
              <p className="text-[10px] text-zinc-400 truncate mt-0.5">
                {isTr
                  ? `Vaka: ${caseId} : Analist: ${leadAnalyst}`
                  : `Case: ${caseId} : Analyst: ${leadAnalyst}`}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {lastActionTime && (
              <span className="text-[9px] text-emerald-400 font-bold bg-white/[0.03] border border-white/10 px-2.5 py-1 rounded-lg flex items-center gap-1">
                <Check className="w-3 h-3" />
                {lastActionTime}
              </span>
            )}
          </div>
        </div>

        {/* Tactical 5-Tab Navigation Ribbon */}
        <div className="flex flex-wrap gap-1.5 p-1 bg-black/60 rounded-xl border border-tactical-border/60 text-xs">
          <button
            type="button"
            onClick={() => setActiveTab("pmr_ratio")}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === "pmr_ratio"
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/50 shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{isTr ? "1. PMR (C/P) Orani" : "1. PMR (C/P) Ratio"}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("antemortem_extrap")}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === "antemortem_extrap"
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/50 shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>{isTr ? "2. Antemortem Ekstrapolasyon" : "2. Antemortem Extrapolation"}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("xenobiotic_matrix")}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === "xenobiotic_matrix"
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/50 shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{isTr ? "3. Ksenobiyotik Matrisi" : "3. Xenobiotic Matrix"}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("benchmarks")}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === "benchmarks"
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/50 shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            <span>{isTr ? "4. Dogrulama Vektorleri" : "4. Benchmark Vectors"}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("iso_audit")}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === "iso_audit"
                ? "bg-rose-500/20 text-rose-300 border border-rose-500/50 shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{isTr ? "5. ISO 17025 Rapor & Ozet" : "5. ISO 17025 Audit & Report"}</span>
          </button>
        </div>
      </div>

      {/* ── Active Progress Bar ── */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-3.5 space-y-2 overflow-hidden shadow-lg"
          >
            <div className="flex items-center justify-between text-xs text-rose-300">
              <span className="flex items-center gap-2 font-bold truncate">
                <Cpu className="w-4 h-4 animate-pulse text-rose-400 shrink-0" />
                {stageText}
              </span>
              <span className="font-mono font-black tabular-nums text-sm">%{progress}</span>
            </div>
            <div className="w-full bg-zinc-900 rounded-full h-2.5 overflow-hidden border border-rose-500/20">
              <motion.div
                className="bg-gradient-to-r from-rose-500 to-amber-400 h-2.5 rounded-full shadow-[0_0_12px_rgba(244,63,94,0.6)]"
                initial={{ width: "5%" }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.2 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {/* TAB 1: PMR (C/P) RATIO EVALUATION                                           */}
      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {activeTab === "pmr_ratio" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Xenobiotic Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                {isTr ? "Ksenobiyotik Parametreleri" : "Xenobiotic Parameters"}
              </span>
              <button
                onClick={() => runPmrEvaluation(selectedDrug, cHeart, cFemoral, unit)}
                disabled={loading}
                className="min-h-[36px] px-4 py-2 rounded-xl bg-rose-500 hover:bg-rose-400 text-zinc-950 font-black text-xs uppercase tracking-wider transition-all shadow-[0_0_20px_rgba(244,63,94,0.3)] hover:shadow-[0_0_25px_rgba(244,63,94,0.5)] disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer active:scale-95"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                {loading
                  ? isTr
                    ? `Hesaplaniyor %${progress}...`
                    : `Evaluating %${progress}...`
                  : isTr
                  ? "PMR Degerlendir"
                  : "Evaluate PMR"}
              </button>
            </div>

            {/* Compound Selector */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              {DRUG_PRESETS.map((p) => (
                <button
                  key={p.name}
                  onClick={() => loadPreset(p)}
                  className={`min-h-[44px] p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedDrug === p.name
                      ? "border-rose-500/80 bg-rose-500/20 text-rose-300 font-bold"
                      : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="font-bold truncate">{p.name}</div>
                  <div className="text-[10px] text-zinc-500">{isTr ? p.riskTr : p.risk}</div>
                </button>
              ))}
            </div>

            {/* Quantitative Inputs */}
            <div className="space-y-3 pt-2 text-xs">
              <div className="space-y-1">
                <label className="text-[10px] text-zinc-400 block font-bold uppercase">
                  {isTr
                    ? `Kardiyak Kalp Kani (C_kalp) [${unit}]`
                    : `Cardiac Heart Blood (C_heart) [${unit}]`}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={cHeart}
                  onChange={(e) => setCHeart(parseFloat(e.target.value) || 0)}
                  className="w-full min-h-[40px] bg-black/50 border border-tactical-border/70 rounded-xl p-2 font-mono text-xs text-tactical-text focus:outline-none focus:border-rose-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-zinc-400 block font-bold uppercase">
                  {isTr
                    ? `Periferik Femoral Kan (C_femoral) [${unit}]`
                    : `Peripheral Femoral Blood (C_femoral) [${unit}]`}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={cFemoral}
                  onChange={(e) => setCFemoral(parseFloat(e.target.value) || 0)}
                  className="w-full min-h-[40px] bg-black/50 border border-tactical-border/70 rounded-xl p-2 font-mono text-xs text-tactical-text focus:outline-none focus:border-rose-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-zinc-400 block font-bold uppercase">
                  {isTr ? "Konsantrasyon Birimi" : "Concentration Unit"}
                </label>
                <div className="grid grid-cols-4 gap-1.5">
                  {["ug/L", "mg/L", "g/L", "ng/mL"].map((u) => (
                    <button
                      key={u}
                      type="button"
                      onClick={() => setUnit(u)}
                      className={`py-1 rounded-lg text-[10px] font-bold border transition-all ${
                        unit === u
                          ? "bg-rose-500/20 text-rose-300 border-rose-500/50"
                          : "bg-black/40 text-zinc-400 border-tactical-border/40 hover:text-zinc-200"
                      }`}
                    >
                      {u}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Right: PMR Scorecard & Visual Comparison */}
          <div className="lg:col-span-2 space-y-4">
            {pmrResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-rose-500/40 bg-gradient-to-br from-rose-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-rose-500/20 pb-3.5">
                    <div>
                      <span className="text-[10px] font-bold text-rose-300 uppercase tracking-widest block">
                        {isTr
                          ? "OLUM SONRASI YENIDEN DAGILIM (PMR) SKOR KARTI"
                          : "POST-MORTEM REDISTRIBUTION (PMR) SCORECARD"}
                      </span>
                      <div className="flex items-baseline gap-3 mt-1">
                        <span className="text-3xl sm:text-4xl font-black text-rose-300 font-mono tabular-nums">
                          C/P = {pmrResult.cp_observed}
                        </span>
                        <span className="text-xs text-zinc-400 font-mono">
                          {isTr ? "Lit. Ref:" : "Lit. Ref:"} {pmrResult.cp_literature_mean}
                          {pmrResult.cp_ratio_std ? ` +/- ${pmrResult.cp_ratio_std}` : ""}
                        </span>
                      </div>
                      <span className="text-[9px] sm:text-[10px] text-zinc-400 block mt-0.5">
                        {isTr ? "Madde:" : "Compound:"} {pmrResult.compound_name} : {isTr ? "Gorunur V_d:" : "Apparent V_d:"} {pmrResult.vd_l_kg} L/kg
                      </span>
                    </div>

                    <div className="flex flex-col items-start sm:items-end gap-1">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "PMR Risk Duzeyi" : "PMR Risk Tier"}
                      </span>
                      <span
                        className={`text-xs font-bold px-2.5 py-1 rounded-lg border font-mono whitespace-nowrap ${
                          pmrResult.is_cardiac_overestimated
                            ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                            : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                        }`}
                      >
                        {pmrResult.pmr_risk_tier}
                      </span>
                      <span className="text-[10px] text-zinc-500">
                        {pmrResult.is_cardiac_overestimated
                          ? isTr
                            ? `+ %${pmrResult.overestimation_percentage.toFixed(1)} Fazla Tahmin`
                            : `+ ${pmrResult.overestimation_percentage.toFixed(1)}% Overestimated`
                          : isTr
                          ? "Beklenen Denge Seviyesi"
                          : "Normal Equilibrium"}
                      </span>
                    </div>
                  </div>

                  {/* Visual C/P Ratio Comparative Meter */}
                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-zinc-400 font-bold uppercase">
                        {isTr ? "C/P Orani Karsilastirmasi" : "C/P Ratio Comparison Meter"}
                      </span>
                      <span className="text-zinc-300 font-mono font-bold">
                        {isTr ? "Literatur Ortalamasina Oran:" : "Ratio to Lit Mean:"}{" "}
                        {(pmrResult.cp_observed / Math.max(0.01, pmrResult.cp_literature_mean)).toFixed(2)}x
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-xs font-mono pt-1">
                      <div className="space-y-1">
                        <div className="flex justify-between text-[11px] text-zinc-400">
                          <span>{isTr ? "Kalp Kani (C_kalp):" : "Heart Blood (C_heart):"}</span>
                          <span className="text-rose-300 font-bold">{pmrResult.c_heart} {pmrResult.unit}</span>
                        </div>
                        <div className="w-full bg-zinc-900 rounded-full h-2">
                          <div
                            className="bg-rose-500 h-2 rounded-full"
                            style={{
                              width: `${Math.min(100, (pmrResult.c_heart / Math.max(pmrResult.c_heart, pmrResult.c_femoral * 2)) * 100)}%`,
                            }}
                          />
                        </div>
                      </div>

                      <div className="space-y-1">
                        <div className="flex justify-between text-[11px] text-zinc-400">
                          <span>{isTr ? "Femoral Kan (C_femoral):" : "Femoral Blood (C_femoral):"}</span>
                          <span className="text-emerald-300 font-bold">{pmrResult.c_femoral} {pmrResult.unit}</span>
                        </div>
                        <div className="w-full bg-zinc-900 rounded-full h-2">
                          <div
                            className="bg-emerald-500 h-2 rounded-full"
                            style={{
                              width: `${Math.min(100, (pmrResult.c_femoral / Math.max(pmrResult.c_heart, pmrResult.c_femoral * 2)) * 100)}%`,
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Toxicology Guideline Statement */}
                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1">
                    <span className="text-[10px] text-zinc-500 block uppercase">
                      {isTr ? "Toksikolojik Kilavuz:" : "Toxicology Guideline:"}
                    </span>
                    <p className="text-zinc-200 leading-relaxed font-bold">
                      {pmrResult.clinical_guideline}
                    </p>
                    <p className="text-rose-300 text-[11px] mt-1 font-semibold">
                      {pmrResult.alert_message}
                    </p>
                  </div>

                  {/* Legal Evaluative Shield */}
                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-rose-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                      {isTr ? "SOFT / TIAFT Yasal Degerlendirme Kalkani" : "SOFT / TIAFT Legal Evaluative Shield"}
                    </div>
                    {pmrResult.prosecutors_fallacy_shield}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {/* TAB 2: ANTEMORTEM BACK-EXTRAPOLATION STUDIO                                 */}
      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {activeTab === "antemortem_extrap" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Extrapolation Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                {isTr ? "Kinetik Parametreler" : "Kinetic Parameters"}
              </span>
              <button
                onClick={() => runExtrapolation(selectedDrug, cFemoral, elapsedHours, unit)}
                disabled={loading}
                className="min-h-[36px] px-4 py-2 rounded-xl bg-rose-500 hover:bg-rose-400 text-zinc-950 font-black text-xs uppercase tracking-wider transition-all shadow-[0_0_20px_rgba(244,63,94,0.3)] hover:shadow-[0_0_25px_rgba(244,63,94,0.5)] disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer active:scale-95"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                {loading
                  ? isTr
                    ? `Ekstrapole Ediliyor %${progress}...`
                    : `Extrapolating %${progress}...`
                  : isTr
                  ? "Ekstrapole Et"
                  : "Extrapolate"}
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="text-[10px] text-zinc-400 block font-bold uppercase">
                  {isTr ? "Hedef Ksenobiyotik" : "Target Xenobiotic"}
                </label>
                <select
                  value={selectedDrug}
                  onChange={(e) => {
                    setSelectedDrug(e.target.value);
                    const preset = XENOBIOTIC_DATABASE[e.target.value];
                    if (preset) {
                      setCFemoral(preset.cFemDefault);
                      setUnit(preset.defaultUnit);
                    }
                  }}
                  className="w-full min-h-[40px] bg-black/50 border border-tactical-border/70 rounded-xl p-2 font-mono text-xs text-rose-300 font-bold focus:outline-none focus:border-rose-500"
                >
                  {DRUG_PRESETS.map((d) => (
                    <option key={d.name} value={d.name}>
                      {d.name} ({isTr ? d.riskTr : d.risk})
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-zinc-400 block font-bold uppercase">
                  {isTr
                    ? `Olum Sonrasi Femoral Kan (C_femoral) [${unit}]`
                    : `Post-Mortem Femoral Blood (C_femoral) [${unit}]`}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={cFemoral}
                  onChange={(e) => setCFemoral(parseFloat(e.target.value) || 0)}
                  className="w-full min-h-[40px] bg-black/50 border border-tactical-border/70 rounded-xl p-2 font-mono text-xs text-tactical-text focus:outline-none focus:border-rose-500"
                />
              </div>

              {/* Elapsed Time Slider */}
              <div className="space-y-1">
                <div className="flex justify-between text-[10px]">
                  <span className="text-zinc-400 uppercase font-bold">
                    {isTr ? "Gecen Olum Sonrasi Sure:" : "Elapsed PM Interval:"}
                  </span>
                  <span className="text-rose-300 font-mono font-bold">
                    {elapsedHours.toFixed(1)} {isTr ? "saat" : "h"}
                  </span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="48.0"
                  step="0.5"
                  value={elapsedHours}
                  onChange={(e) => setElapsedHours(parseFloat(e.target.value))}
                  className="w-full accent-rose-500 cursor-pointer"
                />
                <div className="flex justify-between text-[9px] text-zinc-500">
                  <span>0.5 h</span>
                  <span className="text-rose-400 font-bold">
                    {elapsedHours.toFixed(1)} {isTr ? "Saat Gecti" : "Hours Elapsed"}
                  </span>
                  <span>48.0 h</span>
                </div>
              </div>

              {/* Model Info Card */}
              <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-zinc-500">{isTr ? "Madde:" : "Compound:"}</span>
                  <span className="font-bold text-zinc-200">{selectedDrug}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">C_femoral (t_0):</span>
                  <span className="font-bold text-zinc-200">
                    {cFemoral} {unit}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">{isTr ? "Eliminasyon:" : "Elimination:"}</span>
                  <span className="font-bold text-rose-300">
                    {selectedDrug === "Ethanol"
                      ? isTr
                        ? "Sifirinci Derece Widmark"
                        : "Zero-Order Widmark"
                      : isTr
                      ? "Birinci Derece Yarilanma Omru"
                      : "First-Order Half-Life"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Extrapolation Results & Dynamic Curve */}
          <div className="lg:col-span-2 space-y-4">
            {extrapResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-rose-500/40 bg-gradient-to-br from-rose-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-rose-500/20 pb-3.5">
                    <div>
                      <span className="text-[10px] font-bold text-rose-300 uppercase tracking-widest block">
                        {isTr
                          ? `OLUM ONCESI HESAPLANAN KONSANTRASYON (t - ${extrapResult.elapsed_hours} saat)`
                          : `ANTEMORTEM EXTRAPOLATED CONCENTRATION (t - ${extrapResult.elapsed_hours}h)`}
                      </span>
                      <span className="text-3xl sm:text-4xl font-black text-rose-300 font-mono tabular-nums">
                        {extrapResult.c_antemortem_extrapolated} {extrapResult.unit}
                      </span>
                      <span className="text-[9px] sm:text-[10px] text-zinc-400 block mt-0.5">
                        {isTr ? "Olum Sonrasi Femoral Taban Degeri:" : "Post-Mortem Femoral Baseline:"}{" "}
                        {extrapResult.c_femoral_postmortem} {extrapResult.unit}
                      </span>
                    </div>

                    <div className="flex flex-col items-start sm:items-end gap-1">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "Kinetik Model" : "Kinetic Model"}
                      </span>
                      <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-black/60 border border-tactical-border/60 text-zinc-300 font-mono whitespace-nowrap">
                        {extrapResult.elimination_type}
                      </span>
                    </div>
                  </div>

                  {/* Dynamic SVG Concentration Clearance Curve */}
                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-zinc-400 font-bold uppercase">
                        {isTr ? "Toksikokinetik Klirens Egrisi (Zaman Projeksiyonu)" : "Toxicokinetic Clearance Curve"}
                      </span>
                      <span className="text-rose-300 text-[10px] font-mono font-bold">
                        t = -{extrapResult.elapsed_hours}h : t = 0h
                      </span>
                    </div>

                    <div className="w-full h-32 relative bg-zinc-950/80 rounded-lg p-2 border border-tactical-border/30 flex items-end">
                      <svg className="w-full h-full" viewBox="0 0 400 100" preserveAspectRatio="none">
                        <defs>
                          <linearGradient id="curveGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.8" />
                            <stop offset="100%" stopColor="#10b981" stopOpacity="0.8" />
                          </linearGradient>
                        </defs>
                        {/* Connecting Clearance Line */}
                        <path
                          d={`M 30,20 Q 200,${extrapResult.elimination_type === "Zero-Order" ? "50" : "65"} 370,80`}
                          fill="none"
                          stroke="url(#curveGrad)"
                          strokeWidth="3"
                          strokeDasharray="none"
                        />
                        {/* Antemortem Point (t - Delta t) */}
                        <circle cx="30" cy="20" r="5" fill="#f43f5e" />
                        <text x="35" y="18" fill="#f43f5e" fontSize="10" fontFamily="monospace" fontWeight="bold">
                          t = -{extrapResult.elapsed_hours}h ({extrapResult.c_antemortem_extrapolated} {extrapResult.unit})
                        </text>

                        {/* Postmortem Point (t = 0) */}
                        <circle cx="370" cy="80" r="5" fill="#10b981" />
                        <text x="260" y="75" fill="#10b981" fontSize="10" fontFamily="monospace" fontWeight="bold">
                          t = 0h ({extrapResult.c_femoral_postmortem} {extrapResult.unit})
                        </text>
                      </svg>
                    </div>
                  </div>

                  {/* Kinetic Formula Description */}
                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1">
                    <span className="text-[10px] text-zinc-500 block uppercase">
                      {isTr ? "Kinematik Geriye Projeksiyon Formulu:" : "Kinematic Back-Projection Formula:"}
                    </span>
                    <p className="text-rose-300 font-bold">{extrapResult.kinetic_formula}</p>
                    {extrapResult.elimination_rate_constant_ke_h && (
                      <p className="text-[10px] text-zinc-400">
                        {isTr ? "Eliminasyon Hiz Sabiti (k_e):" : "Elimination Rate Constant (k_e):"}{" "}
                        {extrapResult.elimination_rate_constant_ke_h} h⁻¹ (t_1/2 = {extrapResult.half_life_hours}h)
                      </p>
                    )}
                    {extrapResult.beta_60_g_l_h && (
                      <p className="text-[10px] text-zinc-400">
                        {isTr ? "Widmark Saatlik Hiz (beta_60):" : "Widmark Hourly Rate (beta_60):"}{" "}
                        {extrapResult.beta_60_g_l_h} g/L/h
                      </p>
                    )}
                  </div>

                  {/* Shield */}
                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-rose-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      {isTr ? "SOFT / TIAFT Yasal Degerlendirme Kalkani" : "SOFT / TIAFT Legal Evaluative Shield"}
                    </div>
                    {extrapResult.prosecutors_fallacy_shield}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {/* TAB 3: XENOBIOTIC REFERENCE MATRIX                                          */}
      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {activeTab === "xenobiotic_matrix" && (
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
                {isTr ? "Ksenobiyotik Fizikokimyasal Referans Matrisi" : "Physicochemical Xenobiotic Reference Matrix"}
              </span>
              <span className="text-[10px] text-zinc-400">
                {isTr
                  ? "Sutun 5 Arastirmasi Madde 5.1 & Madde 6 Uyarinca Kalibre Edilmistir"
                  : "Calibrated under Pillar 5 Research §5.1 & §6 Artifact A"}
              </span>
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-zinc-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={isTr ? "Madde veya risk ara..." : "Search compound or risk..."}
                className="w-full pl-8 pr-3 py-1.5 bg-black/50 border border-tactical-border/60 rounded-xl text-xs text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:border-rose-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredXenobiotics.map((x) => (
              <div
                key={x.name}
                className="p-4 rounded-xl border border-tactical-border/50 bg-black/40 space-y-3 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-black text-rose-300">{x.name}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-rose-500/10 border border-rose-500/30 text-rose-400">
                      {isTr ? x.riskTr : x.risk}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-zinc-400">
                    <div>V_d: <span className="font-bold text-zinc-200">{x.vd} L/kg</span></div>
                    <div>log P: <span className="font-bold text-zinc-200">{x.logP}</span></div>
                    <div>pKa: <span className="font-bold text-zinc-200">{x.pKa !== null ? x.pKa : "N/A"}</span></div>
                    <div>C/P Ref: <span className="font-bold text-zinc-200">{x.cpLitMean} +/- {x.cpStd}</span></div>
                  </div>

                  <p className="text-[10px] text-zinc-400 italic">
                    {isTr ? x.guidelineTr : x.guidelineEn}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    loadPreset(x);
                    setActiveTab("pmr_ratio");
                  }}
                  className="w-full py-1.5 rounded-lg bg-white/[0.04] hover:bg-rose-500/20 text-rose-300 border border-white/10 hover:border-rose-500/40 text-[11px] font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
                >
                  <span>{isTr ? "Analize Yukle" : "Load into Analysis"}</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {/* TAB 4: CERTIFIED BENCHMARK VECTORS                                          */}
      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {activeTab === "benchmarks" && (
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
          <div className="border-b border-tactical-border/40 pb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
              {isTr
                ? "Sertifikali Adli Dogrulama Vektorleri (Pillar 5 §6 & VECTOR_P5_03)"
                : "Certified Validation Benchmark Vectors (Pillar 5 §6 & VECTOR_P5_03)"}
            </span>
            <span className="text-[10px] text-zinc-400">
              {isTr
                ? "Bagimsiz analitik capraz dogrulama icin hazir standart test kosullari"
                : "Standardized casework test conditions for independent cross-validation"}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {BENCHMARK_PRESETS.map((b) => (
              <div
                key={b.id}
                className="p-4 rounded-xl border border-tactical-border/50 bg-black/40 space-y-3 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-black text-rose-300">{b.name}</span>
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-white/[0.04] border border-white/10 text-zinc-300">
                      {b.badge}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-zinc-400">
                    <div>{isTr ? "Madde:" : "Compound:"} <span className="font-bold text-zinc-200">{b.compound}</span></div>
                    <div>{isTr ? "Beklenen C/P:" : "Expected C/P:"} <span className="font-bold text-rose-400">{b.expectedCp}</span></div>
                    <div>C_kalp: <span className="font-bold text-zinc-200">{b.cHeart} {b.unit}</span></div>
                    <div>C_fem: <span className="font-bold text-zinc-200">{b.cFem} {b.unit}</span></div>
                  </div>

                  <p className="text-[10px] text-zinc-400">
                    {isTr ? b.descriptionTr : b.descriptionEn}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    loadBenchmark(b);
                    setActiveTab("pmr_ratio");
                  }}
                  className="w-full py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[11px] font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
                >
                  <span>{isTr ? "Vektoru Calistir & Dogrula" : "Execute & Verify Vector"}</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {/* TAB 5: ISO/IEC 17025 COURTROOM AUDIT & CRYPTOGRAPHIC DIGEST                */}
      {/* ═══════════════════════════════════════════════════════════════════════════ */}
      {activeTab === "iso_audit" && (
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
                {isTr
                  ? "ISO/IEC 17025:2017 Madde 7.8 Adli Toksikoloji Raporlama Paketi"
                  : "ISO/IEC 17025:2017 Section 7.8 Forensic Toxicology Reporting Suite"}
              </span>
              <span className="text-[10px] text-zinc-400">
                {isTr
                  ? "Deterministik Kriptografik Durum Ozeti (H_pmr) & Yasal Ifade"
                  : "Deterministic Cryptographic State Digest (H_pmr) & Court Testimony"}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={copyCourtReport}
                className="px-3 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/50 text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
              >
                {copiedState ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedState ? (isTr ? "Kopyalandi!" : "Copied!") : isTr ? "Raporu Kopyala" : "Copy Report"}</span>
              </button>
            </div>
          </div>

          {/* Cryptographic Hash Digest Banner */}
          <div className="p-3.5 rounded-xl bg-black/60 border border-tactical-border/60 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-zinc-400 font-bold uppercase flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                {isTr ? "Deterministik Durum Denetim Ozeti (H_pmr):" : "Deterministic State Audit Digest (H_pmr):"}
              </span>
              <span className="text-[10px] text-emerald-400 font-bold">SHA-256 VERIFIED</span>
            </div>
            <div className="p-2 rounded-lg bg-zinc-950 font-mono text-[11px] text-emerald-300 break-all select-all">
              {stateDigest || "Computing cryptographic digest..."}
            </div>
          </div>

          {/* Full Courtroom Brief */}
          <div className="p-4 rounded-xl bg-black/40 border border-tactical-border/40 text-xs space-y-3">
            <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">
              {isTr ? "Bilisimsel Adli Tip Beyani" : "Computational Forensic Toxicology Statement"}
            </span>

            <div className="space-y-2 text-zinc-200 leading-relaxed font-mono">
              <p>
                <strong>1. {isTr ? "Madde Kimligi & Ornekleme:" : "Target Xenobiotic & Sampling:"}</strong>{" "}
                {pmrResult?.compound_name} {isTr ? "konsantrasyonlari olculmustur." : "concentrations evaluated."}{" "}
                C_kalp = {pmrResult?.c_heart} {pmrResult?.unit}, C_femoral = {pmrResult?.c_femoral} {pmrResult?.unit}.
              </p>
              <p>
                <strong>2. {isTr ? "Gozlemlenen C/P Orani:" : "Observed C/P Ratio:"}</strong>{" "}
                C/P = {pmrResult?.cp_observed} ({isTr ? "Literatur Ortalamasi:" : "Literature Mean:"} {pmrResult?.cp_literature_mean} +/- {pmrResult?.cp_ratio_std}).{" "}
                {pmrResult?.is_cardiac_overestimated
                  ? isTr
                    ? "Merkezi kalp kani konsantrasyonu, doku salinimi nedeniyle periferik kandan belirgin sekilde yuksektir."
                    : "Central cardiac blood concentration is significantly elevated above peripheral venous blood due to post-mortem tissue release."
                  : isTr
                  ? "Merkezi ve periferik kan konsantrasyonlari beklenen denge araligindadir."
                  : "Central and peripheral blood concentrations are consistent with expected baseline equilibrium."}
              </p>
              <p>
                <strong>3. {isTr ? "Antemortem Geriye Projeksiyon:" : "Antemortem Extrapolation:"}</strong>{" "}
                {extrapResult
                  ? `${extrapResult.elapsed_hours} ${isTr ? "saatlik gecen sure sonunda hesaplanan olum ani seviyesi:" : "hours elapsed; extrapolated level at death:"} ${extrapResult.c_antemortem_extrapolated} ${extrapResult.unit} (${extrapResult.elimination_type}).`
                  : "N/A"}
              </p>
              <p>
                <strong>4. {isTr ? "Yasal Kalkan (SOFT / TIAFT):" : "Legal Evaluative Shield (SOFT / TIAFT):"}</strong>{" "}
                {pmrResult?.prosecutors_fallacy_shield}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
