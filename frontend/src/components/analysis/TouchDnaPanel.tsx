"use client";

import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Fingerprint,
  Dna,
  Activity,
  Layers,
  ShieldCheck,
  AlertTriangle,
  Sliders,
  BarChart3,
  TrendingDown,
  Info,
  CheckCircle2,
  RefreshCw,
  Zap,
  Sparkles,
  Search,
  Scale,
  FileSpreadsheet,
  AlertOctagon,
  Copy,
  Check,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

// ===========================================================================
// 1. Exact Biocomputational Research Constants (Pillar 1 §4 & Artifact D)
// ===========================================================================

const DROPOUT_BETA0_RFU = 2.50;
const DROPOUT_BETA1_RFU = -0.025; // RFU^-1

const DROPOUT_BETA0_MASS = 3.20;
const DROPOUT_BETA1_MASS = -0.080; // pg^-1
const DROPOUT_BETAS_BP = 0.008; // bp^-1

const DROPIN_LAMBDA_POISSON = 0.020; // per locus
const DROPIN_LAMBDA_HEIGHT = 0.015; // RFU^-1
const ANALYTICAL_THRESHOLD_RFU = 50.0;
const STOCHASTIC_THRESHOLD_RFU = 150.0;
const HB_FLAG_THRESHOLD = 0.60;

// Substrate recovery specifications
const SUBSTRATES = [
  {
    id: "SMOOTH_NON_POROUS",
    name: "Smooth Non-Porous",
    nameTr: "Düz Gözeneksiz",
    examples: "Glass, Polished Metal, Phone Screen",
    examplesTr: "Cam, Parlatılmış Metal, Telefon Ekranı",
    efficiency: 0.60,
    badgeColor: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
    porosity: "NON_POROUS",
    desc: "Optimal recovery substrate; minimal cellular entrapment.",
    descTr: "Optimal geri kazanım yüzeyi; minimum hücresel hapsolma.",
  },
  {
    id: "TEXTURED_NON_POROUS",
    name: "Textured Non-Porous",
    nameTr: "Dokulu Gözeneksiz",
    examples: "Firearm Grip, Steering Wheel, Tool Handle",
    examplesTr: "Silah Kabzası, Direksiyon Simidi, Alet Sapı",
    efficiency: 0.40,
    badgeColor: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    porosity: "TEXTURED",
    desc: "Standard forensic touch evidence; moderate cellular shearing.",
    descTr: "Standart adli temas delili; orta düzeyde hücresel sürtünme.",
  },
  {
    id: "POROUS_FABRIC",
    name: "Porous Fabric",
    nameTr: "Gözenekli Kumaş",
    examples: "Cotton T-Shirt, Denim Collar, Mask",
    examplesTr: "Pamuklu Tişört, Kot Yaka, Maske",
    efficiency: 0.20,
    badgeColor: "text-rose-400 bg-rose-500/10 border-rose-500/30",
    porosity: "POROUS",
    desc: "Severe entrapment; deep fiber absorption reduces recovery.",
    descTr: "Şiddetli hapsolma; derin lif emilimi geri kazanımı düşürür.",
  },
  {
    id: "ROUGH_WOOD",
    name: "Rough Wood / Brick",
    nameTr: "Pürüzlü Ahşap / Tuğla",
    examples: "Unfinished Timber, Concrete, Brick",
    examplesTr: "İşlenmemiş Kereste, Beton, Tuğla",
    efficiency: 0.15,
    badgeColor: "text-purple-400 bg-purple-500/10 border-purple-500/30",
    porosity: "HIGHLY_POROUS",
    desc: "Extreme cellular fragmentation and porous matrix trapping.",
    descTr: "Aşırı hücresel parçalanma ve gözenekli matris hapsolması.",
  },
];

// 24 Loci Registry with NIST Frequencies & Amplicon bp
const STR_LOCUS_SPECS: Record<
  string,
  {
    bp: number;
    dye: "BLUE" | "GREEN" | "YELLOW" | "RED" | "PURPLE";
    refAlleles: [number, number];
    popFreqs: Record<number, number>;
  }
> = {
  D3S1358: { bp: 125, dye: "BLUE", refAlleles: [15, 16], popFreqs: { 14: 0.125, 15: 0.282, 16: 0.231, 17: 0.205, 18: 0.143 } },
  vWA: { bp: 175, dye: "BLUE", refAlleles: [16, 17], popFreqs: { 14: 0.112, 15: 0.108, 16: 0.214, 17: 0.278, 18: 0.198, 19: 0.082 } },
  FGA: { bp: 235, dye: "BLUE", refAlleles: [21, 22], popFreqs: { 19: 0.065, 20: 0.134, 21: 0.183, 22: 0.191, 23: 0.143, 24: 0.152 } },
  D8S1179: { bp: 140, dye: "GREEN", refAlleles: [13, 14], popFreqs: { 12: 0.142, 13: 0.339, 14: 0.201, 15: 0.115 } },
  D21S11: { bp: 215, dye: "GREEN", refAlleles: [28, 30], popFreqs: { 28: 0.165, 29: 0.185, 30: 0.235, 31.2: 0.112 } },
  D18S51: { bp: 290, dye: "GREEN", refAlleles: [12, 15], popFreqs: { 12: 0.135, 13: 0.125, 14: 0.175, 15: 0.155, 16: 0.145 } },
  D5S818: { bp: 155, dye: "YELLOW", refAlleles: [11, 12], popFreqs: { 10: 0.062, 11: 0.355, 12: 0.362, 13: 0.142 } },
  D13S317: { bp: 220, dye: "YELLOW", refAlleles: [11, 13], popFreqs: { 9: 0.085, 11: 0.315, 12: 0.275, 13: 0.125 } },
  D7S820: { bp: 275, dye: "YELLOW", refAlleles: [9, 10], popFreqs: { 8: 0.152, 9: 0.165, 10: 0.285, 11: 0.205 } },
  TH01: { bp: 185, dye: "RED", refAlleles: [6, 9.3], popFreqs: { 6: 0.225, 7: 0.185, 8: 0.135, 9: 0.155, 9.3: 0.312 } },
  TPOX: { bp: 240, dye: "RED", refAlleles: [8, 11], popFreqs: { 8: 0.545, 9: 0.115, 10: 0.055, 11: 0.245 } },
  CSF1PO: { bp: 310, dye: "RED", refAlleles: [10, 11], popFreqs: { 10: 0.255, 11: 0.315, 12: 0.335 } },
  D1S1656: { bp: 160, dye: "PURPLE", refAlleles: [15, 17.3], popFreqs: { 14: 0.125, 15: 0.162, 16: 0.145, 17.3: 0.210 } },
  D2S1338: { bp: 330, dye: "BLUE", refAlleles: [17, 20], popFreqs: { 17: 0.185, 19: 0.165, 20: 0.135, 23: 0.145 } },
  D10S1248: { bp: 110, dye: "GREEN", refAlleles: [13, 14], popFreqs: { 13: 0.295, 14: 0.315, 15: 0.225 } },
  D12S391: { bp: 245, dye: "YELLOW", refAlleles: [18, 21], popFreqs: { 17: 0.145, 18: 0.205, 20: 0.135, 21: 0.125 } },
  D19S433: { bp: 130, dye: "RED", refAlleles: [13, 14], popFreqs: { 13: 0.265, 14: 0.345, 15: 0.155 } },
  D22S1045: { bp: 105, dye: "PURPLE", refAlleles: [15, 16], popFreqs: { 14: 0.095, 15: 0.365, 16: 0.385 } },
  D2S441: { bp: 95, dye: "BLUE", refAlleles: [11, 12], popFreqs: { 10: 0.185, 11: 0.325, 12: 0.315 } },
  D6S1043: { bp: 195, dye: "GREEN", refAlleles: [11, 12], popFreqs: { 11: 0.315, 12: 0.285, 18: 0.145 } },
  SE33: { bp: 360, dye: "PURPLE", refAlleles: [27.2, 28.2], popFreqs: { 19: 0.085, 27.2: 0.115, 28.2: 0.125 } },
  Penta_D: { bp: 380, dye: "YELLOW", refAlleles: [9, 12], popFreqs: { 9: 0.205, 11: 0.185, 12: 0.165 } },
  Penta_E: { bp: 420, dye: "RED", refAlleles: [7, 12], popFreqs: { 7: 0.175, 10: 0.145, 12: 0.195 } },
  Amelogenin: { bp: 106, dye: "BLUE", refAlleles: [1, 2], popFreqs: { 1: 0.500, 2: 0.500 } },
};

// ===========================================================================
// 2. Mathematical Evaluation Helpers
// ===========================================================================

function calcDropoutProbMass(massPg: number, ampliconBp?: number): number {
  if (massPg <= 0) return 1.0;
  let logit = DROPOUT_BETA0_MASS + DROPOUT_BETA1_MASS * massPg;
  if (ampliconBp && ampliconBp > 100) {
    logit += DROPOUT_BETAS_BP * (ampliconBp - 100);
  }
  if (logit > 40) return 1.0 - Math.exp(-logit);
  if (logit < -40) return Math.exp(logit);
  return 1.0 / (1.0 + Math.exp(-logit));
}

function calcDropoutProbRfu(rfu: number): number {
  if (rfu <= 0) return 1.0;
  const logit = DROPOUT_BETA0_RFU + DROPOUT_BETA1_RFU * rfu;
  if (logit > 40) return 1.0 - Math.exp(-logit);
  if (logit < -40) return Math.exp(logit);
  return 1.0 / (1.0 + Math.exp(-logit));
}

function calcPoissonDropin(k: number, lambdaC: number = DROPIN_LAMBDA_POISSON): number {
  let fact = 1;
  for (let i = 2; i <= k; i++) fact *= i;
  return (Math.pow(lambdaC, k) * Math.exp(-lambdaC)) / fact;
}

function calcDropinHeightDensity(
  h: number,
  at: number = ANALYTICAL_THRESHOLD_RFU,
  lambdaH: number = DROPIN_LAMBDA_HEIGHT
): number {
  if (h < at) return 0.0;
  return lambdaH * Math.exp(-lambdaH * (h - at));
}

function calcHeterozygoteBalance(h1: number, h2: number) {
  const hMin = Math.min(h1, h2);
  const hMax = Math.max(h1, h2);
  const hb = hMax > 0 ? hMin / hMax : 0;
  const isImbalanced = hb < HB_FLAG_THRESHOLD;
  const isSubStochastic = hMin < STOCHASTIC_THRESHOLD_RFU;
  const isSubAt = hMin < ANALYTICAL_THRESHOLD_RFU;
  return {
    hMin,
    hMax,
    hb,
    isImbalanced,
    isSubStochastic,
    isSubAt,
    isFlagged: isImbalanced || isSubStochastic || isSubAt,
  };
}

function calcSingleLocusLR(
  suspectGeno: [number, number],
  observedPeaks: Record<number, number>,
  pD: number,
  popFreqs: Record<number, number>,
  theta: number = 0.03,
  lambdaC: number = DROPIN_LAMBDA_POISSON
) {
  const [a1, a2] = suspectGeno;
  const p1 = popFreqs[a1] || 0.05;
  const p2 = popFreqs[a2] || 0.05;

  const observedAlleles = Object.keys(observedPeaks).map(Number);
  const suspectSet = new Set([a1, a2]);
  const missing = [a1, a2].filter((a) => !observedAlleles.includes(a));
  const extras = observedAlleles.filter((a) => !suspectSet.has(a));

  const surviveDropin = 1.0 - lambdaC;
  let likHp = 0.0;
  let state = "BOTH_PRESENT";

  if (a1 !== a2) {
    if (missing.length === 0) {
      likHp = (1.0 - pD) * (1.0 - pD) * surviveDropin;
      state = "BOTH_PRESENT";
    } else if (missing.length === 1) {
      likHp = 2.0 * pD * (1.0 - pD) * surviveDropin;
      state = "SINGLE_DROPOUT";
    } else {
      likHp = pD * pD * surviveDropin;
      state = "DOUBLE_DROPOUT";
    }
  } else {
    if (missing.length === 0) {
      likHp = (1.0 - pD * pD) * surviveDropin;
      state = "BOTH_PRESENT";
    } else {
      likHp = pD * pD * surviveDropin;
      state = "DOUBLE_DROPOUT";
    }
  }

  if (extras.length > 0) {
    state = "DROPIN";
    for (const extraA of extras) {
      const hExtra = observedPeaks[extraA] || 50.0;
      const pdf = calcDropinHeightDensity(hExtra);
      likHp *= Math.max(1e-6, lambdaC * pdf);
    }
  }

  let pGeno = 0;
  if (a1 === a2) {
    pGeno =
      ((2.0 * theta + (1.0 - theta) * p1) * (3.0 * theta + (1.0 - theta) * p1)) /
      ((1.0 + theta) * (1.0 + 2.0 * theta));
  } else {
    pGeno =
      (2.0 * (theta + (1.0 - theta) * p1) * (theta + (1.0 - theta) * p2)) /
      ((1.0 + theta) * (1.0 + 2.0 * theta));
  }

  const likHd = Math.max(1e-12, pGeno);
  const lr = Math.max(1e-50, likHp / likHd);
  const log10Lr = Math.log10(lr);

  return {
    state,
    likHp,
    likHd,
    lr,
    log10Lr: Number(log10Lr.toFixed(4)),
    missingCount: missing.length,
    extraCount: extras.length,
  };
}

// ===========================================================================
// 3. Golden Benchmark Preset Definitions
// ===========================================================================

type PresetKey = "VECTOR_03" | "VECTOR_TERM_06" | "NIST_SRM2391D" | "LCN_15PG";

interface GoldenPreset {
  id: PresetKey;
  name: string;
  badge: string;
  badgeColor: string;
  substrateId: string;
  initialMassPg: number;
  description: string;
  locusProfiles: Record<string, { suspect: [number, number]; observed: Record<number, number> }>;
}

const GOLDEN_PRESETS: Record<PresetKey, GoldenPreset> = {
  VECTOR_03: {
    id: "VECTOR_03",
    name: "VECTOR_03 — vWA Single Dropout (Touch DNA)",
    badge: "LTDNA Benchmark",
    badgeColor: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    substrateId: "TEXTURED_NON_POROUS",
    initialMassPg: 80.0, // recovers 32.0 pg
    description: "Single allele dropout benchmark (vWA 16@80RFU, allele 17 dropped) under stochastic penalty.",
    locusProfiles: {
      vWA: { suspect: [16, 17], observed: { 16: 80 } },
      D3S1358: { suspect: [15, 16], observed: { 15: 110, 16: 95 } },
      FGA: { suspect: [21, 22], observed: { 21: 75 } },
      D8S1179: { suspect: [13, 14], observed: { 13: 100, 14: 80 } },
    },
  },
  VECTOR_TERM_06: {
    id: "VECTOR_TERM_06",
    name: "VECTOR_TERM_06 — 24-Locus Touch Profile (31.25 pg)",
    badge: "Severe LTDNA Touch",
    badgeColor: "text-rose-400 bg-rose-500/10 border-rose-500/30",
    substrateId: "TEXTURED_NON_POROUS",
    initialMassPg: 78.125, // recovers ~31.25 pg
    description: "Full 24-locus touch evidence from steering wheel swab with 7 masked dropouts and Hb=0.455 imbalance.",
    locusProfiles: {
      D3S1358: { suspect: [15, 16], observed: { 15: 80 } }, // 16 dropped
      vWA: { suspect: [16, 18], observed: { 16: 110, 18: 50 } }, // Hb = 0.455
      FGA: { suspect: [21, 22], observed: { 21: 75 } },
      D8S1179: { suspect: [13, 14], observed: { 13: 95, 14: 80 } },
      D21S11: { suspect: [28, 30], observed: { 28: 65 } }, // 30 dropped
      D18S51: { suspect: [12, 15], observed: { 12: 60 } },
      D5S818: { suspect: [11, 12], observed: { 11: 85 } }, // 12 dropped
      D13S317: { suspect: [11, 13], observed: { 11: 75, 13: 60 } },
      D7S820: { suspect: [9, 10], observed: { 9: 65, 10: 55 } },
      TH01: { suspect: [6, 9.3], observed: { 6: 90, 9.3: 80 } },
      TPOX: { suspect: [8, 11], observed: { 8: 75, 11: 60 } },
      CSF1PO: { suspect: [10, 11], observed: { 10: 55 } },
      D1S1656: { suspect: [15, 17.3], observed: { 15: 100, 17.3: 85 } },
      D2S1338: { suspect: [17, 20], observed: { 17: 55 } }, // 20 dropped
      D10S1248: { suspect: [13, 14], observed: { 13: 110, 14: 95 } },
      D12S391: { suspect: [18, 21], observed: { 18: 70, 21: 55 } },
      D19S433: { suspect: [13, 14], observed: { 13: 105, 14: 90 } },
      D22S1045: { suspect: [15, 16], observed: { 15: 115, 16: 100 } },
      D2S441: { suspect: [11, 12], observed: { 11: 120, 12: 105 } },
      D6S1043: { suspect: [11, 12], observed: { 11: 85, 12: 70 } },
      SE33: { suspect: [27.2, 28.2], observed: { 27.2: 55 } }, // 28.2 dropped
      Penta_D: { suspect: [9, 12], observed: { 9: 55 } }, // 12 dropped
      Penta_E: { suspect: [7, 12], observed: {} }, // both dropped
      Amelogenin: { suspect: [1, 2], observed: { 1: 95, 2: 80 } },
    },
  },
  NIST_SRM2391D: {
    id: "NIST_SRM2391D",
    name: "NIST SRM 2391d Component A (Pristine Control)",
    badge: "Positive Control (1.0 ng)",
    badgeColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
    substrateId: "SMOOTH_NON_POROUS",
    initialMassPg: 1000.0, // recovers 600.0 pg
    description: "Standard high-template casework control profile with complete allele retention and Hb >= 0.88.",
    locusProfiles: Object.fromEntries(
      Object.entries(STR_LOCUS_SPECS).map(([locus, spec]) => [
        locus,
        {
          suspect: spec.refAlleles,
          observed: { [spec.refAlleles[0]]: 750, [spec.refAlleles[1]]: 720 },
        },
      ])
    ),
  },
  LCN_15PG: {
    id: "LCN_15PG",
    name: "LCN 15 pg — Single-Cell Physical Limit",
    badge: "Single-Cell (2.2 Cells)",
    badgeColor: "text-purple-400 bg-purple-500/10 border-purple-500/30",
    substrateId: "POROUS_FABRIC",
    initialMassPg: 75.0, // recovers 15.0 pg
    description: "Peter Gill ultralow dilution standard (15 pg) demonstrating 88.08% dropout risk and locus masking.",
    locusProfiles: {
      D3S1358: { suspect: [15, 16], observed: { 15: 55 } },
      vWA: { suspect: [16, 17], observed: {} },
      FGA: { suspect: [21, 22], observed: {} },
      D8S1179: { suspect: [13, 14], observed: { 13: 60 } },
      D21S11: { suspect: [28, 30], observed: {} },
      TH01: { suspect: [6, 9.3], observed: { 6: 55 } },
      Amelogenin: { suspect: [1, 2], observed: { 1: 65 } },
    },
  },
};

// ===========================================================================
// 4. Main React Component
// ===========================================================================

export default function TouchDnaPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  // State
  const [activeTab, setActiveTab] = useState<"SUBSTRATE" | "CURVES" | "DROPIN" | "HETEROZYGOTE" | "PROFILE">("SUBSTRATE");
  const [selectedPreset, setSelectedPreset] = useState<PresetKey>("VECTOR_03");

  const [selectedSubstrateId, setSelectedSubstrateId] = useState<string>("TEXTURED_NON_POROUS");
  const [initialMassPg, setInitialMassPg] = useState<number>(80.0);

  const [curveMode, setCurveMode] = useState<"MASS" | "RFU" | "FRAGMENT">("MASS");
  const [curveMassHover, setCurveMassHover] = useState<number>(32.0);

  const [h1Rfu, setH1Rfu] = useState<number>(110.0);
  const [h2Rfu, setH2Rfu] = useState<number>(46.2);

  const [copiedReport, setCopiedReport] = useState(false);

  // Selected substrate
  const activeSubstrate = useMemo(() => {
    return SUBSTRATES.find((s) => s.id === selectedSubstrateId) || SUBSTRATES[1];
  }, [selectedSubstrateId]);

  // Recovered mass & general metrics
  const recoveredMassPg = useMemo(() => {
    return initialMassPg * activeSubstrate.efficiency;
  }, [initialMassPg, activeSubstrate]);

  const pDropoutTemplate = useMemo(() => {
    return calcDropoutProbMass(recoveredMassPg);
  }, [recoveredMassPg]);

  const cellCountEquivalent = useMemo(() => {
    return (recoveredMassPg / 6.6).toFixed(1);
  }, [recoveredMassPg]);

  const isLtdnaRegime = recoveredMassPg < 100.0;

  // Active preset profile data
  const currentProfile = useMemo(() => {
    return GOLDEN_PRESETS[selectedPreset].locusProfiles;
  }, [selectedPreset]);

  // Load Preset
  const handleLoadPreset = (presetKey: PresetKey) => {
    const preset = GOLDEN_PRESETS[presetKey];
    setSelectedPreset(presetKey);
    setSelectedSubstrateId(preset.substrateId);
    setInitialMassPg(preset.initialMassPg);
  };

  // Evaluate multi-locus profile LR
  const multiLocusAnalysis = useMemo(() => {
    const locusResults = Object.entries(currentProfile).map(([locus, data]) => {
      const spec = STR_LOCUS_SPECS[locus] || { bp: 200, popFreqs: { 15: 0.25, 16: 0.25 } };
      const locusPd = calcDropoutProbMass(recoveredMassPg, spec.bp);
      const evalRes = calcSingleLocusLR(data.suspect, data.observed, locusPd, spec.popFreqs);
      return {
        locus,
        bp: spec.bp,
        dye: spec.dye,
        suspect: data.suspect,
        observed: data.observed,
        locusPd,
        ...evalRes,
      };
    });

    const sumLog10 = locusResults.reduce((acc, r) => acc + r.log10Lr, 0);
    const totalLog10 = Number(sumLog10.toFixed(4));
    const totalLr = Math.pow(10, Math.min(300, totalLog10));

    // Verbal predicate (ENFSI 2017)
    let verbalEn = "Extremely Strong Support for Prosecution Proposition (Hp)";
    let verbalTr = "İddia Makamı Hipotezi (Hp) Lehine Son Derece Güçlü Destek";
    if (totalLog10 < 0) {
      verbalEn = "Exclusion / Support for Defense Proposition (Hd)";
      verbalTr = "Dışlama / Savunma Hipotezi (Hd) Lehine Destek";
    } else if (totalLog10 === 0) {
      verbalEn = "Inconclusive / Neutral Evidence";
      verbalTr = "Sonuçsuz / Nötr Delil";
    } else if (totalLog10 < 2) {
      verbalEn = "Weak / Limited Support for Prosecution Proposition";
      verbalTr = "İddia Makamı Lehine Zayıf / Sınırlı Destek";
    } else if (totalLog10 < 4) {
      verbalEn = "Moderate Support for Prosecution Proposition";
      verbalTr = "İddia Makamı Lehine Orta Düzeyde Destek";
    } else if (totalLog10 < 6) {
      verbalEn = "Strong Support for Prosecution Proposition";
      verbalTr = "İddia Makamı Lehine Güçlü Destek";
    }

    return {
      locusResults,
      totalLog10,
      totalLr,
      verbalEn,
      verbalTr,
      dropoutsCount: locusResults.filter((r) => r.state === "SINGLE_DROPOUT" || r.state === "DOUBLE_DROPOUT").length,
    };
  }, [currentProfile, recoveredMassPg]);

  // Heterozygote Balance live evaluation
  const hbAnalysis = useMemo(() => {
    return calcHeterozygoteBalance(h1Rfu, h2Rfu);
  }, [h1Rfu, h2Rfu]);

  // Copy Juror Report
  const copyJurorReport = () => {
    const reportText = `
FORENZA FORENSIC EVIDENCE OS — TOUCH DNA & LTDNA REPORT
============================================================
Case Protocol: Module 1.4 Low-Template Stochastic Modeling
Reference Preset: ${GOLDEN_PRESETS[selectedPreset].name}
Substrate: ${isTr ? activeSubstrate.nameTr : activeSubstrate.name} (Efficiency η = ${activeSubstrate.efficiency * 100}%)
Initial Deposition Mass: ${initialMassPg.toFixed(1)} pg
Recovered DNA Mass: ${recoveredMassPg.toFixed(1)} pg (~${cellCountEquivalent} diploid cells)
Stochastic Allele Dropout Risk P(D): ${(pDropoutTemplate * 100).toFixed(2)}%
Operational Zone: ${isLtdnaRegime ? (isTr ? "DÜŞÜK ŞABLON DNA (LTDNA) STOKASTİK REJİMİ" : "LOW-TEMPLATE DNA (LTDNA) STOCHASTIC REGIME") : (isTr ? "STANDART VAKA REJİMİ" : "STANDARD CASE REGIME")}

MULTI-LOCUS STOCHASTIC LIKELIHOOD RATIO:
------------------------------------------------------------
Evaluated Loci Count: ${multiLocusAnalysis.locusResults.length}
Observed Dropout Loci: ${multiLocusAnalysis.dropoutsCount}
Total Combined log10(LR): ${multiLocusAnalysis.totalLog10 >= 0 ? "+" : ""}${multiLocusAnalysis.totalLog10}
Total Likelihood Ratio: ${multiLocusAnalysis.totalLr.toExponential(4)}

ENFSI 2017 VERBAL STATEMENT:
"${isTr ? multiLocusAnalysis.verbalTr : multiLocusAnalysis.verbalEn}"

PROSECUTOR'S FALLACY SHIELD:
${isTr ? "Olabilirlik Oranı (LR), yarışan hipotezler (Hp ve Hd) altında düşük şablonlu DNA profilinin gözlenme olasılığını ölçer. Şüphelinin suçu işlediği veya temas izini bıraktığı yönünde doğrudan bir sonsal suçluluk olasılığı değildir." : "The Likelihood Ratio measures the probability of the low-template DNA profile under competing propositions (Hp vs Hd). It is NOT the posterior probability that the suspect committed the crime or deposited the touch trace."}
============================================================
`.trim();

    navigator.clipboard.writeText(reportText);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2500);
  };

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Banner ───────────────────────────────────────────────── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-tactical-border/60 pb-5">
        <div className="flex items-center gap-3.5">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-orange-500/10 border border-orange-500/30 text-orange-400 shadow-[0_0_20px_rgba(249,115,22,0.2)]">
            <Fingerprint className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-black tracking-widest text-tactical-text uppercase">
                {isTr ? "Temas DNA & Düşük Şablon Stokastik Modelleme" : "Touch DNA & Low-Template Stochastic Modeling"}
              </h1>
              <span className="text-[10px] font-bold text-orange-400 bg-orange-500/10 border border-orange-500/20 px-2 py-0.5 rounded-full">
                MOD-04
              </span>
            </div>
            <p className="text-xs text-tactical-text-muted mt-0.5">
              {isTr
                ? "Pillar 1 §4 • Yüzey Geri Kazanımı (η) • Lojistik Alel Kaybı P(D) • Poisson Eklenmesi P(C) • Curran-Gill LTDNA LR"
                : "Pillar 1 §4 • Substrate Recovery (η) • Logistic Dropout P(D) • Poisson Drop-in P(C) • Curran-Gill LTDNA LR"}
            </p>
          </div>
        </div>

        {/* Golden Preset Selector */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] text-tactical-text-muted uppercase font-bold mr-1 flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" /> {isTr ? "Hazır Ayarlar:" : "Presets:"}
          </span>
          {(Object.keys(GOLDEN_PRESETS) as PresetKey[]).map((key) => {
            const p = GOLDEN_PRESETS[key];
            const isSelected = selectedPreset === key;
            return (
              <button
                key={key}
                onClick={() => handleLoadPreset(key)}
                className={`min-h-[38px] px-3 py-1.5 rounded-xl text-xs font-bold transition-all border cursor-pointer ${
                  isSelected
                    ? "bg-orange-500/20 border-orange-500/60 text-orange-300 shadow-[0_0_12px_rgba(249,115,22,0.25)]"
                    : "bg-tactical-surface/50 border-tactical-border/50 text-tactical-text-muted hover:border-tactical-border"
                }`}
              >
                {key}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Navigation Tabs ─────────────────────────────────────────────────── */}
      <div className="flex flex-wrap gap-2 border-b border-tactical-border/40 pb-3">
        {[
          { id: "SUBSTRATE", label: isTr ? "1. Yüzey Transferi & Geri Kazanım" : "1. Substrate Transfer & Recovery", icon: Layers },
          { id: "CURVES", label: isTr ? "2. Lojistik Alel Kaybı Eğrileri P(D)" : "2. Logistic Dropout Curves P(D)", icon: TrendingDown },
          { id: "DROPIN", label: isTr ? "3. Poisson Eklenmesi & Yükseklik PDF" : "3. Poisson Drop-in & Height PDF", icon: BarChart3 },
          { id: "HETEROZYGOTE", label: isTr ? "4. Heterozigot Dengesi & LR" : "4. Heterozygote Balance & LR", icon: Scale },
          { id: "PROFILE", label: isTr ? "5. 24-Lokus Profil EPG & Rapor" : "5. 24-Locus Profile EPG & Report", icon: Dna },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`min-h-[44px] px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition-all border cursor-pointer ${
                isActive
                  ? "bg-orange-500/15 border-orange-500/50 text-orange-300 shadow-[0_0_15px_rgba(249,115,22,0.15)]"
                  : "bg-tactical-surface/30 border-tactical-border/40 text-tactical-text-muted hover:border-tactical-border/70 hover:text-tactical-text"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* ── Tab Content ─────────────────────────────────────────────────────── */}
      <AnimatePresence mode="wait">
        {/* TAB 1: SUBSTRATE TRANSFER & RECOVERY SIMULATION */}
        {activeTab === "SUBSTRATE" && (
          <motion.div
            key="tab-substrate"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
            className="space-y-6"
          >
            {/* Live Telemetry Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 space-y-1 shadow-md">
                <span className="text-[10px] text-tactical-text-muted uppercase font-bold tracking-wider">
                  {isTr ? "Başlangıç Temas Kütlesi" : "Initial Touch Mass"}
                </span>
                <p className="text-xl font-bold font-mono text-tactical-text tabular-nums">{initialMassPg.toFixed(1)} pg</p>
                <span className="text-[10px] text-zinc-500 block">{isTr ? "Yüzeye temas birikimi" : "Deposition on substrate"}</span>
              </div>

              <div className="rounded-2xl border border-orange-500/30 bg-orange-500/5 p-4 space-y-1 shadow-md">
                <span className="text-[10px] text-orange-400 uppercase font-bold tracking-wider">
                  {isTr ? "Geri Kazanılan DNA Kütlesi" : "Recovered DNA Mass"}
                </span>
                <p className="text-xl font-bold font-mono text-orange-300 tabular-nums">{recoveredMassPg.toFixed(1)} pg</p>
                <span className="text-[10px] text-orange-400/80 block">
                  ~{cellCountEquivalent} {isTr ? "diploit hücre eşdeğeri" : "diploid cell equivalents"}
                </span>
              </div>

              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 space-y-1 shadow-md">
                <span className="text-[10px] text-tactical-text-muted uppercase font-bold tracking-wider">
                  {isTr ? "Lojistik Alel Kaybı Riski P(D)" : "Logistic Dropout Risk P(D)"}
                </span>
                <p className={`text-xl font-bold font-mono tabular-nums ${pDropoutTemplate > 0.5 ? "text-rose-400" : pDropoutTemplate > 0.1 ? "text-amber-400" : "text-emerald-400"}`}>
                  {(pDropoutTemplate * 100).toFixed(2)}%
                </p>
                <span className="text-[10px] text-zinc-500 block">β₀=+3.20, β₁=-0.080 pg⁻¹</span>
              </div>

              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 space-y-1 shadow-md">
                <span className="text-[10px] text-tactical-text-muted uppercase font-bold tracking-wider">
                  {isTr ? "Adli Operasyonel Rejim" : "Forensic Operational Regime"}
                </span>
                <p className="text-sm font-bold font-mono flex items-center gap-1.5 mt-1 text-tactical-text">
                  {isLtdnaRegime ? (
                    <span className="text-rose-400 flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4 text-rose-400" /> {isTr ? "LTDNA (< 100 pg)" : "LTDNA (< 100 pg)"}
                    </span>
                  ) : (
                    <span className="text-emerald-400 flex items-center gap-1">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" /> {isTr ? "Standart Vaka Rejimi" : "Standard Casework"}
                    </span>
                  )}
                </p>
                <span className="text-[10px] text-zinc-500 block">{isTr ? "SWGDAM Stokastik Eşiği" : "SWGDAM Stochastic Threshold"}</span>
              </div>
            </div>

            {/* Substrate Selector & Slider */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left 2 Cols: Substrate Cards */}
              <div className="lg:col-span-2 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-5 shadow-lg">
                <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                  <span className="text-xs font-bold text-tactical-text uppercase tracking-wider flex items-center gap-2">
                    <Layers className="w-4 h-4 text-orange-400" />
                    {isTr
                      ? "Adli Yüzey Fiziksel Geri Kazanım Matrisi (4 Malzeme)"
                      : "Forensic Substrate Physical Recovery Matrix (4 Materials)"}
                  </span>
                  <span className="text-[10px] text-tactical-text-muted">{isTr ? "Referans Verim Katsayısı (η)" : "Reference Yield Factor (η)"}</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  {SUBSTRATES.map((sub) => {
                    const isSelected = selectedSubstrateId === sub.id;
                    const rec = initialMassPg * sub.efficiency;
                    const pd = calcDropoutProbMass(rec);
                    return (
                      <div
                        key={sub.id}
                        onClick={() => setSelectedSubstrateId(sub.id)}
                        className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2.5 ${
                          isSelected
                            ? "bg-orange-500/15 border-orange-500/60 shadow-[0_0_15px_rgba(249,115,22,0.2)]"
                            : "bg-black/20 border-tactical-border/40 hover:border-tactical-border/80"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-tactical-text">{isTr ? sub.nameTr : sub.name}</span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${sub.badgeColor}`}>
                            η = {(sub.efficiency * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p className="text-[10px] text-zinc-400 line-clamp-1">{isTr ? sub.examplesTr : sub.examples}</p>
                        <div className="pt-1.5 border-t border-tactical-border/30 flex items-center justify-between text-[11px] font-mono">
                          <span className="text-zinc-500">
                            {isTr ? "Verim:" : "Yield:"} <strong className="text-tactical-text">{rec.toFixed(1)} pg</strong>
                          </span>
                          <span className={pd > 0.5 ? "text-rose-400" : pd > 0.2 ? "text-amber-400" : "text-emerald-400"}>
                            P(D) = {(pd * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Input Mass Slider */}
                <div className="p-4 rounded-xl bg-black/30 border border-tactical-border/40 space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-tactical-text flex items-center gap-1.5">
                      <Sliders className="w-3.5 h-3.5 text-orange-400" />
                      {isTr ? "Başlangıç Temas Kütlesini Ayarlayın (pg):" : "Adjust Initial Touch Deposition Mass (pg):"}
                    </span>
                    <span className="font-mono font-bold text-orange-400 tabular-nums text-sm">
                      {initialMassPg.toFixed(1)} pg
                    </span>
                  </div>
                  <input
                    type="range"
                    min="5"
                    max="1000"
                    step="5"
                    value={initialMassPg}
                    onChange={(e) => setInitialMassPg(parseFloat(e.target.value))}
                    className="w-full accent-orange-500 bg-black/40 h-2 rounded-lg cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-zinc-500 font-mono">
                    <span>5 pg ({isTr ? "Tek Hücre" : "Single-Cell"})</span>
                    <span>100 pg ({isTr ? "SWGDAM Eşiği" : "SWGDAM Threshold"})</span>
                    <span>500 pg ({isTr ? "Vaka Düzeyi" : "Casework"})</span>
                    <span>1000 pg (1.0 ng {isTr ? "Standart" : "Standard"})</span>
                  </div>
                </div>
              </div>

              {/* Right Col: Recovery Breakdown & Physical Details */}
              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg flex flex-col justify-between">
                <div className="space-y-4">
                  <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
                    {isTr ? "Transfer Fiziği & Sürüntü Protokolü" : "Transfer Physics & Swabbing Protocol"}
                  </span>

                  <div className="p-3.5 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1.5 text-xs">
                    <span className="text-zinc-500 block text-[10px] uppercase font-bold">
                      {isTr ? "Aktif Yüzey" : "Active Substrate"}
                    </span>
                    <p className="font-bold text-orange-300">{isTr ? activeSubstrate.nameTr : activeSubstrate.name}</p>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">{isTr ? activeSubstrate.descTr : activeSubstrate.desc}</p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-black/20 border border-tactical-border/40 space-y-2 text-xs">
                    <span className="text-zinc-500 block text-[10px] uppercase font-bold">
                      {isTr ? "Matematiksel Geri Kazanım Hesabı" : "Mathematical Recovery Calculation"}
                    </span>
                    <div className="space-y-1 text-[11px] font-mono">
                      <div className="flex justify-between">
                        <span className="text-zinc-400">{isTr ? "Başlangıç Kütlesi (m_in):" : "Initial Deposition (m_in):"}</span>
                        <span className="text-tactical-text font-bold">{initialMassPg.toFixed(1)} pg</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-zinc-400">{isTr ? "Geri Kazanım Katsayısı (η):" : "Recovery Coefficient (η):"}</span>
                        <span className="text-orange-400 font-bold">{(activeSubstrate.efficiency * 100).toFixed(0)}%</span>
                      </div>
                      <div className="flex justify-between pt-1 border-t border-tactical-border/30">
                        <span className="text-zinc-300 font-bold">{isTr ? "Geri Kazanılan Kalıp (m_rec):" : "Recovered Template (m_rec):"}</span>
                        <span className="text-orange-300 font-bold">{recoveredMassPg.toFixed(1)} pg</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className={`p-3.5 rounded-xl border space-y-1 text-xs ${isLtdnaRegime ? "bg-rose-500/10 border-rose-500/30 text-rose-300" : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"}`}>
                  <span className="text-[10px] uppercase font-bold block">
                    {isLtdnaRegime ? (isTr ? "⚠️ Şiddetli Stokastik Uyarı" : "⚠️ Severe Stochastic Warning") : (isTr ? "✅ Standart Kalitede Profil" : "✅ Standard Quality Profile")}
                  </span>
                  <p className="text-[11px] leading-relaxed">
                    {isLtdnaRegime
                      ? (isTr
                          ? "Geri kazanılan DNA kalıbı 100 pg altındadır. Alel kaybı P(D) ve yalancı homozigotluk riski sürekli MCMC olasılıksal yorumlama gerektirir."
                          : "Recovered template is under 100 pg. Allele dropout P(D) and false homozygosity risk require continuous MCMC probabilistic interpretation.")
                      : (isTr
                          ? "Geri kazanılan kütle, lokus kaybı beklenmeksizin standart STR sınıflandırması için yeterlidir."
                          : "Recovered mass is sufficient for standard STR binning with zero locus dropouts expected.")}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* TAB 2: LOGISTIC DROPOUT CURVES VISUALIZER (INTERACTIVE SVG) */}
        {activeTab === "CURVES" && (
          <motion.div
            key="tab-curves"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
            className="space-y-6"
          >
            <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-5 shadow-lg">
              {/* Curve Controls */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/40 pb-3">
                <span className="text-xs font-bold text-tactical-text uppercase tracking-wider flex items-center gap-2">
                  <TrendingDown className="w-4 h-4 text-orange-400" />
                  {isTr
                    ? "Kalibre Edilmiş Sigmoid Alel Kaybı Fonksiyonu P(D | x)"
                    : "Calibrated Sigmoid Allele Dropout Function P(D | x)"}
                </span>

                <div className="flex items-center gap-2">
                  {[
                    { id: "MASS", label: isTr ? "Kalıp Kütlesi (pg)" : "Template Mass (pg)" },
                    { id: "RFU", label: isTr ? "Pik Yüksekliği (RFU)" : "Peak Height (RFU)" },
                    { id: "FRAGMENT", label: isTr ? "Amplikon Bozunması (bp)" : "Amplicon Decay (bp)" },
                  ].map((m) => (
                    <button
                      key={m.id}
                      onClick={() => setCurveMode(m.id as any)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all border cursor-pointer ${
                        curveMode === m.id
                          ? "bg-orange-500/20 border-orange-500/50 text-orange-300 shadow-[0_0_10px_rgba(249,115,22,0.2)]"
                          : "bg-black/20 border-tactical-border/40 text-tactical-text-muted hover:border-tactical-border"
                      }`}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Interactive SVG Chart Container */}
              <div className="relative h-64 sm:h-72 w-full bg-black/40 rounded-xl border border-tactical-border/50 p-4 flex flex-col justify-end">
                {/* SVG Visualizer */}
                <svg className="w-full h-full" viewBox="0 0 500 200" preserveAspectRatio="none">
                  {/* Grid Lines */}
                  <line x1="0" y1="20" x2="500" y2="20" stroke="#334155" strokeDasharray="3 3" strokeWidth="1" />
                  <line x1="0" y1="100" x2="500" y2="100" stroke="#334155" strokeDasharray="3 3" strokeWidth="1" />
                  <line x1="0" y1="180" x2="500" y2="180" stroke="#334155" strokeDasharray="3 3" strokeWidth="1" />

                  {/* 100 pg / 150 RFU Stochastic Threshold Line */}
                  <line
                    x1={curveMode === "MASS" ? (100 / 300) * 500 : (150 / 600) * 500}
                    y1="0"
                    x2={curveMode === "MASS" ? (100 / 300) * 500 : (150 / 600) * 500}
                    y2="200"
                    stroke="#f59e0b"
                    strokeDasharray="4 4"
                    strokeWidth="1.5"
                  />

                  {/* Sigmoid Curve Path */}
                  <path
                    d={Array.from({ length: 50 }).reduce<string>((acc, _, i) => {
                      const xVal = curveMode === "MASS" ? (i / 49) * 300 : curveMode === "RFU" ? (i / 49) * 600 : (i / 49) * 450;
                      const pd = curveMode === "MASS" ? calcDropoutProbMass(xVal) : curveMode === "RFU" ? calcDropoutProbRfu(xVal) : calcDropoutProbMass(30, xVal);
                      const px = (i / 49) * 500;
                      const py = 180 - pd * 160;
                      return acc + `${i === 0 ? "M" : "L"} ${px} ${py} `;
                    }, "")}
                    fill="none"
                    stroke="#f97316"
                    strokeWidth="3"
                  />

                  {/* Active Point Crosshair */}
                  {curveMode === "MASS" && (
                    <>
                      <circle
                        cx={(Math.min(300, recoveredMassPg) / 300) * 500}
                        cy={180 - calcDropoutProbMass(recoveredMassPg) * 160}
                        r="6"
                        fill="#ef4444"
                        stroke="#ffffff"
                        strokeWidth="2"
                      />
                    </>
                  )}
                </svg>

                {/* SVG Labels */}
                <div className="absolute top-3 left-4 text-[10px] font-mono text-zinc-400 flex items-center gap-4 flex-wrap">
                  <span className="text-orange-400 font-bold">● P(D | x) {isTr ? "Lojistik Sigmoid" : "Logistic Sigmoid"}</span>
                  <span className="text-amber-400">┆ {isTr ? "Stokastik Eşik" : "Stochastic Threshold"} ({curveMode === "MASS" ? "100 pg" : "150 RFU"})</span>
                  {curveMode === "MASS" && (
                    <span className="text-rose-400 font-bold">
                      ◆ {isTr ? "Mevcut Nokta:" : "Current Point:"} {recoveredMassPg.toFixed(1)} pg → P(D) = {(pDropoutTemplate * 100).toFixed(1)}%
                    </span>
                  )}
                </div>

                <div className="flex justify-between text-[10px] font-mono text-zinc-500 pt-2 border-t border-tactical-border/40">
                  <span>0 {curveMode === "MASS" ? "pg" : curveMode === "RFU" ? "RFU" : "bp"} (P(D) → 1.0)</span>
                  <span>{curveMode === "MASS" ? "150 pg (P(D) < 1%)" : curveMode === "RFU" ? "300 RFU" : "250 bp"}</span>
                  <span>{curveMode === "MASS" ? "300 pg (P(D) ≈ 0.0)" : curveMode === "RFU" ? "600 RFU" : "450 bp"}</span>
                </div>
              </div>

              {/* Research Formulas & Acceptance Boundaries */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
                <div className="p-3.5 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                  <span className="text-zinc-500 text-[10px] block font-bold">{isTr ? "RFU Model Denklemi" : "RFU Model Equation"}</span>
                  <p className="text-orange-300 font-bold">P(D | RFU) = 1 / (1 + e^(-(2.50 - 0.025·RFU)))</p>
                  <span className="text-[10px] text-zinc-500 block">{isTr ? "Kritik %1 Eşiği = 283.81 RFU" : "Critical 1% Threshold = 283.81 RFU"}</span>
                </div>

                <div className="p-3.5 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                  <span className="text-zinc-500 text-[10px] block font-bold">{isTr ? "Kütle Model Denklemi" : "Mass Model Equation"}</span>
                  <p className="text-orange-300 font-bold">P(D | pg) = 1 / (1 + e^(-(3.20 - 0.080·pg)))</p>
                  <span className="text-[10px] text-zinc-500 block">{isTr ? "Kritik %1 Eşiği = 97.44 pg" : "Critical 1% Threshold = 97.44 pg"}</span>
                </div>

                <div className="p-3.5 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                  <span className="text-zinc-500 text-[10px] block font-bold">{isTr ? "Amplikon Bozunma Cezası" : "Amplicon Decay Penalty"}</span>
                  <p className="text-orange-300 font-bold">+0.008·(bp - 100) on Logit Scale</p>
                  <span className="text-[10px] text-zinc-500 block">{isTr ? "Bozunmuş temas DNA boyut hiyerarşisi" : "Degraded touch DNA size hierarchy"}</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* TAB 3: POISSON DROP-IN & EXPONENTIAL HEIGHT PDF */}
        {activeTab === "DROPIN" && (
          <motion.div
            key="tab-dropin"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Col: Discrete Poisson PMF */}
              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
                <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
                  {isTr
                    ? "Poisson Alel Eklenme Olasılığı P(C = k) (λ_C = 0.020)"
                    : "Poisson Allele Drop-in Probability P(C = k) (λ_C = 0.020)"}
                </span>

                <div className="space-y-3">
                  {[0, 1, 2, 3].map((k) => {
                    const prob = calcPoissonDropin(k, DROPIN_LAMBDA_POISSON);
                    const pct = (prob * 100).toFixed(4);
                    return (
                      <div key={k} className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1 text-xs">
                        <div className="flex justify-between items-center">
                          <span className="font-bold text-tactical-text">
                            k = {k} {isTr ? "Eklenen Alel" : `Drop-in Allele${k === 1 ? "" : "s"}`}
                          </span>
                          <span className="font-mono font-bold text-orange-400">{pct}%</span>
                        </div>
                        <div className="w-full bg-black/40 h-2 rounded-full overflow-hidden border border-tactical-border/30">
                          <div className="bg-orange-500 h-full rounded-full" style={{ width: `${Math.min(100, Math.max(1, prob * 100))}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs space-y-1 font-mono">
                  <span className="text-[10px] uppercase font-bold block">
                    {isTr ? "24-Lokus Temiz Profil Birleşik İnvaryantı" : "24-Locus Clean Profile Composite Invariant"}
                  </span>
                  <p className="text-sm font-bold">P(C_total = 0) = e^(-24 · 0.020) = 61.88%</p>
                  <p className="text-[10px] text-emerald-400/80">
                    {isTr
                      ? "24 lokus genelinde en az 1 rastlantısal eklenme piki gözlenme olasılığı: %38.12."
                      : "38.12% probability of observing ≥ 1 sporadic drop-in peak across 24 loci."}
                  </p>
                </div>
              </div>

              {/* Right Col: Truncated Exponential Peak Height PDF */}
              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg flex flex-col justify-between">
                <div className="space-y-4">
                  <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
                    {isTr ? "Kesilmiş Üstel Pik Yüksekliği Yoğunluğu f(h_C)" : "Truncated Exponential Height Density f(h_C)"}
                  </span>

                  <div className="space-y-2 text-xs font-mono">
                    <p className="text-zinc-400 text-[11px] leading-relaxed">
                      {isTr
                        ? "Eklenme floresan sinyalleri, Analitik Eşik (AT = 50.0 RFU) üzerindeki düşük RFU bölgesiyle sınırlıdır:"
                        : "Drop-in fluorescence signals are constrained to the low-RFU region above Analytical Threshold (AT = 50.0 RFU):"}
                    </p>
                    <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/40 space-y-1.5">
                      <span className="text-orange-300 font-bold block">f(h_C) = λ_h · exp(-λ_h · (h_C - AT))   for h_C ≥ 50 RFU</span>
                      <span className="text-zinc-500 text-[10px] block">
                        λ_h = 0.015 RFU⁻¹ • {isTr ? "Teorik Ortalama E[h_C] = 116.67 RFU" : "Theoretical Mean E[h_C] = 116.67 RFU"}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-xs font-mono text-center">
                    {[50, 75, 120].map((h) => {
                      const dens = calcDropinHeightDensity(h);
                      return (
                        <div key={h} className="p-2.5 rounded-xl bg-black/20 border border-tactical-border/40 space-y-0.5">
                          <span className="text-zinc-500 text-[10px] block">{h} RFU</span>
                          <span className="text-orange-400 font-bold text-[11px]">f(h)={dens.toFixed(4)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1 text-xs">
                  <span className="text-zinc-500 block text-[10px] uppercase font-bold">
                    {isTr ? "Eşik Altı Ayıklama (Culling)" : "Sub-Threshold Culling"}
                  </span>
                  <p className="text-[11px] text-zinc-400">
                    {isTr
                      ? "AT = 50.0 RFU altındaki herhangi bir pik f(h) = 0.0000 yoğunluğuna sahiptir ve olabilirlik değerlendirmesinden çıkarılır."
                      : "Any peak below AT = 50.0 RFU has density f(h) = 0.0000 and is culled from likelihood evaluation."}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* TAB 4: HETEROZYGOTE BALANCE & CURRAN-GILL LR CALCULATOR */}
        {activeTab === "HETEROZYGOTE" && (
          <motion.div
            key="tab-hb"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Col: Heterozygote Balance Interactive Sliders */}
              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-5 shadow-lg">
                <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
                  {isTr ? "Heterozigot Pik Denge Oranı H_b = h_min / h_max" : "Heterozygote Peak Balance Ratio H_b = h_min / h_max"}
                </span>

                {/* h1 Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-zinc-400 font-bold">{isTr ? "Alel 1 Pik Yüksekliği (h₁):" : "Allele 1 Peak Height (h₁):"}</span>
                    <span className="text-orange-400 font-bold">{h1Rfu.toFixed(0)} RFU</span>
                  </div>
                  <input
                    type="range"
                    min="20"
                    max="1000"
                    step="5"
                    value={h1Rfu}
                    onChange={(e) => setH1Rfu(parseFloat(e.target.value))}
                    className="w-full accent-orange-500 bg-black/40 h-2 rounded-lg cursor-pointer"
                  />
                </div>

                {/* h2 Slider */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-zinc-400 font-bold">{isTr ? "Alel 2 Pik Yüksekliği (h₂):" : "Allele 2 Peak Height (h₂):"}</span>
                    <span className="text-orange-400 font-bold">{h2Rfu.toFixed(0)} RFU</span>
                  </div>
                  <input
                    type="range"
                    min="20"
                    max="1000"
                    step="5"
                    value={h2Rfu}
                    onChange={(e) => setH2Rfu(parseFloat(e.target.value))}
                    className="w-full accent-orange-500 bg-black/40 h-2 rounded-lg cursor-pointer"
                  />
                </div>

                {/* Status Badges */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 pt-2 text-xs font-mono">
                  <div className={`p-2.5 rounded-xl border text-center ${hbAnalysis.isImbalanced ? "bg-rose-500/10 border-rose-500/30 text-rose-300" : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"}`}>
                    <span className="text-[10px] block text-zinc-500">{isTr ? "H_b Oranı" : "H_b Ratio"}</span>
                    <strong className="text-sm">{hbAnalysis.hb.toFixed(3)}</strong>
                    <span className="text-[9px] block">
                      {hbAnalysis.isImbalanced ? (isTr ? "< 0.60 (Dengesiz)" : "< 0.60 (Imbalanced)") : (isTr ? ">= 0.60 (Normal)" : ">= 0.60 (Normal)")}
                    </span>
                  </div>

                  <div className={`p-2.5 rounded-xl border text-center ${hbAnalysis.isSubStochastic ? "bg-amber-500/10 border-amber-500/30 text-amber-300" : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"}`}>
                    <span className="text-[10px] block text-zinc-500">{isTr ? "Stokastik (ST)" : "Stochastic (ST)"}</span>
                    <strong className="text-sm">{hbAnalysis.hMin.toFixed(0)} RFU</strong>
                    <span className="text-[9px] block">
                      {hbAnalysis.isSubStochastic ? (isTr ? "< 150 RFU (Riskli)" : "< 150 RFU (Active)") : (isTr ? ">= 150 RFU (Geçti)" : ">= 150 RFU (Passed)")}
                    </span>
                  </div>

                  <div className={`p-2.5 rounded-xl border text-center ${hbAnalysis.isSubAt ? "bg-rose-500/10 border-rose-500/30 text-rose-300" : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"}`}>
                    <span className="text-[10px] block text-zinc-500">{isTr ? "Analitik (AT)" : "Analytical (AT)"}</span>
                    <strong className="text-sm">50.0 RFU</strong>
                    <span className="text-[9px] block">
                      {hbAnalysis.isSubAt ? (isTr ? "Eşik Altı (Yok)" : "Sub-AT Culled") : (isTr ? "Eşik Üstü" : "Above AT")}
                    </span>
                  </div>
                </div>
              </div>

              {/* Right Col: Curran-Gill 4-State Markov Evaluation */}
              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg flex flex-col justify-between">
                <div className="space-y-3">
                  <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
                    {isTr ? "Curran-Gill 4-Durumlu Markov Gözlem Modeli" : "Curran-Gill 4-State Markov Observation Model"}
                  </span>

                  <div className="space-y-2 text-xs font-mono">
                    <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                      <div className="flex justify-between text-zinc-300">
                        <span>{isTr ? "Senaryo A (Her İkisi Mevcut):" : "Scenario A (Both Present):"}</span>
                        <strong className="text-emerald-400 font-bold">(1 - P(D))² · (1 - λ_C)</strong>
                      </div>
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Hp altında tam profil korunumu" : "Full profile retention under Hp"}
                      </span>
                    </div>

                    <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                      <div className="flex justify-between text-zinc-300">
                        <span>{isTr ? "Senaryo B (Tek Alel Kaybı):" : "Scenario B (Single Dropout):"}</span>
                        <strong className="text-amber-400 font-bold">2·P(D)·(1 - P(D)) · (1 - λ_C)</strong>
                      </div>
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Bir kardeş alel kayboldu (VECTOR_03)" : "One sister allele dropped (VECTOR_03)"}
                      </span>
                    </div>

                    <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                      <div className="flex justify-between text-zinc-300">
                        <span>{isTr ? "Senaryo C (Çift Alel Kaybı):" : "Scenario C (Double Dropout):"}</span>
                        <strong className="text-rose-400 font-bold">P(D)² · (1 - λ_C)</strong>
                      </div>
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Hp altında tam lokus kaybı" : "Complete locus dropout under Hp"}
                      </span>
                    </div>

                    <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                      <div className="flex justify-between text-zinc-300">
                        <span>{isTr ? "Senaryo D (Rastlantısal Eklenme):" : "Scenario D (Sporadic Drop-in):"}</span>
                        <strong className="text-purple-400 font-bold">2·P(D)·(1 - P(D)) · λ_C·f(h_C)</strong>
                      </div>
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Yapay pik cezalandırması" : "Artifact peak penalization"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-orange-500/10 border border-orange-500/30 text-orange-300 text-xs font-mono flex items-center justify-between">
                  <span>{isTr ? "VECTOR_03 vWA Tek Kayıp LR:" : "VECTOR_03 vWA Single Dropout LR:"}</span>
                  <strong className="text-base text-emerald-400 font-bold">log10(LR) = +0.5604</strong>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* TAB 5: 24-LOCUS MULTI-MARKER STOCHASTIC EPG & JUROR REPORT */}
        {activeTab === "PROFILE" && (
          <motion.div
            key="tab-profile"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
            className="space-y-6"
          >
            {/* Total Likelihood Ratio & Verbal Summary */}
            <div className="rounded-2xl border border-orange-500/40 bg-gradient-to-r from-orange-500/10 via-tactical-surface/80 to-black/60 p-5 space-y-4 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Dna className="w-5 h-5 text-orange-400" />
                  <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                    {isTr ? "24-Lokus Profil Olabilirlik Oranı (ENFSI 2017 & SWGDAM)" : "24-Locus Profile Likelihood Ratio (ENFSI 2017 & SWGDAM)"}
                  </span>
                </div>
                <button
                  onClick={copyJurorReport}
                  className="px-3.5 py-1.5 rounded-xl bg-orange-500/20 hover:bg-orange-500/30 border border-orange-500/40 text-orange-300 text-xs font-bold flex items-center gap-1.5 transition-all self-start sm:self-auto cursor-pointer"
                >
                  {copiedReport ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  {copiedReport ? (isTr ? "Rapor Kopyalandı!" : "Report Copied!") : (isTr ? "Jüri Raporunu Kopyala" : "Copy Juror Report")}
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
                <div>
                  <span className="text-[10px] text-zinc-500 uppercase block">{isTr ? "Birleşik log10(LR)" : "Composite log10(LR)"}</span>
                  <p className="text-2xl font-black text-emerald-400 tabular-nums">
                    {multiLocusAnalysis.totalLog10 >= 0 ? "+" : ""}{multiLocusAnalysis.totalLog10}
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-zinc-500 uppercase block">{isTr ? "Toplam Nokta Olabilirlik Oranı" : "Total Point Likelihood Ratio"}</span>
                  <p className="text-lg font-bold text-tactical-text tabular-nums mt-0.5">
                    {multiLocusAnalysis.totalLr.toExponential(4)}
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-zinc-500 uppercase block">{isTr ? "ENFSI (2017) Sözlü İfade" : "ENFSI (2017) Verbal Predicate"}</span>
                  <p className="text-xs font-bold text-orange-300 mt-1 leading-snug">
                    {isTr ? multiLocusAnalysis.verbalTr : multiLocusAnalysis.verbalEn}
                  </p>
                </div>
              </div>
            </div>

            {/* 24-Locus Table */}
            <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg overflow-x-auto">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
                <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                  {isTr
                    ? "24-Belirteçli Elektroferogram Pik Dağılımı & Stokastik Durumlar"
                    : "24-Marker Electropherogram Peak Breakdown & Stochastic States"}
                </span>
                <span className="text-[10px] text-zinc-500">
                  {isTr
                    ? `${multiLocusAnalysis.locusResults.length} lokus gösteriliyor (${multiLocusAnalysis.dropoutsCount} kayıp)`
                    : `Showing ${multiLocusAnalysis.locusResults.length} loci (${multiLocusAnalysis.dropoutsCount} dropouts)`}
                </span>
              </div>

              <table className="w-full text-left text-xs font-mono border-collapse">
                <thead>
                  <tr className="border-b border-tactical-border/40 text-[10px] text-zinc-400 uppercase">
                    <th className="py-2.5 px-3">{isTr ? "STR Lokusu" : "Locus"}</th>
                    <th className="py-2.5 px-3">{isTr ? "Boyut (bp)" : "Size (bp)"}</th>
                    <th className="py-2.5 px-3">{isTr ? "Şüpheli" : "Suspect"}</th>
                    <th className="py-2.5 px-3">{isTr ? "Gözlenen EPG Pikleri (RFU)" : "Observed EPG Peaks (RFU)"}</th>
                    <th className="py-2.5 px-3">{isTr ? "Durum" : "State"}</th>
                    <th className="py-2.5 px-3">P(D)</th>
                    <th className="py-2.5 px-3 text-right">log10(LR_l)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-tactical-border/30 text-[11px]">
                  {multiLocusAnalysis.locusResults.map((row) => {
                    const isDropped = row.state === "SINGLE_DROPOUT" || row.state === "DOUBLE_DROPOUT";
                    const stateLabelTr =
                      row.state === "BOTH_PRESENT" ? "HER İKİSİ MEVCUT" :
                      row.state === "SINGLE_DROPOUT" ? "TEK ALEL KAYBI" :
                      row.state === "DOUBLE_DROPOUT" ? "ÇİFT ALEL KAYBI" : row.state;

                    return (
                      <tr key={row.locus} className="hover:bg-white/5 transition-colors">
                        <td className="py-2.5 px-3 font-bold text-tactical-text">{row.locus}</td>
                        <td className="py-2.5 px-3 text-zinc-500">{row.bp} bp</td>
                        <td className="py-2.5 px-3 text-orange-300 font-bold">
                          [{row.suspect[0]}, {row.suspect[1]}]
                        </td>
                        <td className="py-2.5 px-3">
                          {Object.keys(row.observed).length === 0 ? (
                            <span className="text-rose-400 italic">
                              {isTr ? "[0] Pik Yok (Kayıp)" : "[0] No Peak (Dropout)"}
                            </span>
                          ) : (
                            Object.entries(row.observed).map(([al, h]) => (
                              <span key={al} className="inline-block mr-2 px-2 py-0.5 rounded bg-black/40 border border-tactical-border/40 text-[10px]">
                                <strong>{al}</strong> @ {h} RFU
                              </span>
                            ))
                          )}
                        </td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
                              row.state === "BOTH_PRESENT"
                                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                                : row.state === "SINGLE_DROPOUT"
                                ? "bg-amber-500/10 border-amber-500/30 text-amber-400"
                                : "bg-rose-500/10 border-rose-500/30 text-rose-400"
                            }`}
                          >
                            {isTr ? stateLabelTr : row.state}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-zinc-400">{(row.locusPd * 100).toFixed(1)}%</td>
                        <td className={`py-2.5 px-3 text-right font-bold tabular-nums ${row.log10Lr >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                          {row.log10Lr >= 0 ? "+" : ""}{row.log10Lr.toFixed(4)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
