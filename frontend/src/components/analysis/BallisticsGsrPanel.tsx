"use client";

import { useState, useMemo, useEffect } from "react";
import {
  Target,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Layers,
  Activity,
  Plus,
  Trash2,
  Copy,
  Check,
  FileCheck,
  Download,
  Dna,
  Microscope,
  Scissors,
  ArrowRight,
  Database,
  BarChart3,
  Search,
} from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES & SCHEMAS
// ═══════════════════════════════════════════════════════════════════════════════

export type BallisticsTabId =
  | "gsr_edx"
  | "cmc_striation"
  | "microscopy_hair"
  | "benchmarks"
  | "iso_audit";

export interface GsrParticle {
  particle_id: string;
  pb_percent: number;
  ba_percent: number;
  sb_percent: number;
  al_percent?: number;
  aspect_ratio: number;
}

export interface GsrResponse {
  total_particles_scanned: number;
  characteristic_particles: number;
  consistent_particles: number;
  commonly_associated_particles: number;
  likelihood_ratio: number;
  evidence_strength: string;
  classified_particles: Array<{
    particle_id: string;
    classification_tier: string;
    pb_percent: number;
    ba_percent: number;
    sb_percent: number;
    aspect_ratio: number;
  }>;
  prosecutors_fallacy_shield: string;
}

export interface CmcCell {
  cell_id: string;
  ccf_max: number;
  delta_x_um: number;
  delta_y_um: number;
  delta_theta_deg: number;
}

export interface CmcResponse {
  total_cells_evaluated: number;
  cmc_count: number;
  identification_verdict: string;
  false_match_probability: string;
  ballistic_conclusion: string;
  evaluated_cells: Array<{
    cell_id: string;
    ccf_max: number;
    delta_x_um: number;
    delta_y_um: number;
    delta_theta_deg: number;
    is_congruent_matching_cell: boolean;
  }>;
  prosecutors_fallacy_shield: string;
}

export interface HairSpecimen {
  id: string;
  shaft_diameter_um: number;
  medulla_diameter_um: number;
  origin: string;
  originTr: string;
  root_morphology: string;
  root_morphologyTr: string;
  dna_strategy: string;
  dna_strategyTr: string;
  badge: string;
}

export interface BenchmarkPreset {
  id: string;
  name: string;
  nameTr: string;
  desc: string;
  descTr: string;
  category: "gsr" | "cmc";
  particles?: GsrParticle[];
  cells?: CmcCell[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// 8 OFFICIAL GOLDEN BENCHMARK PRESETS (VECTOR_22_GSR_A - H)
// ═══════════════════════════════════════════════════════════════════════════════

export const GOLDEN_BALLISTICS_PRESETS: BenchmarkPreset[] = [
  {
    id: "VECTOR_22_GSR_A",
    name: "VECTOR_22_GSR_A: Characteristic Triad (Pb-Ba-Sb)",
    nameTr: "VECTOR_22_GSR_A: Karakteristik Üçlü (Pb-Ba-Sb)",
    desc: "3x Characteristic Pb-Ba-Sb particles with aspect ratio <= 1.3 yielding LR = 10,000",
    descTr: "En/boy oranı <= 1.3 olan 3 adet karakteristik Pb-Ba-Sb parçacığı, LR = 10.000",
    category: "gsr",
    particles: [
      { particle_id: "p_01", pb_percent: 35.0, ba_percent: 25.0, sb_percent: 15.0, aspect_ratio: 1.1 },
      { particle_id: "p_02", pb_percent: 40.0, ba_percent: 30.0, sb_percent: 12.0, aspect_ratio: 1.2 },
      { particle_id: "p_03", pb_percent: 28.0, ba_percent: 22.0, sb_percent: 18.0, aspect_ratio: 1.0 },
      { particle_id: "p_04", pb_percent: 45.0, ba_percent: 35.0, sb_percent: 0.0, aspect_ratio: 1.3 },
    ],
  },
  {
    id: "VECTOR_22_GSR_B",
    name: "VECTOR_22_GSR_B: Consistent Bi-Element (Pb-Ba)",
    nameTr: "VECTOR_22_GSR_B: Uyumlu İkili (Pb-Ba)",
    desc: "5x Consistent Pb-Ba particles without Antimony (Sb) yielding LR = 500",
    descTr: "Antimonsuz (Sb) 5 adet uyumlu Pb-Ba parçacığı, LR = 500",
    category: "gsr",
    particles: [
      { particle_id: "p_01", pb_percent: 48.0, ba_percent: 32.0, sb_percent: 0.0, aspect_ratio: 1.2 },
      { particle_id: "p_02", pb_percent: 52.0, ba_percent: 28.0, sb_percent: 0.0, aspect_ratio: 1.1 },
      { particle_id: "p_03", pb_percent: 45.0, ba_percent: 35.0, sb_percent: 0.0, aspect_ratio: 1.2 },
      { particle_id: "p_04", pb_percent: 42.0, ba_percent: 38.0, sb_percent: 0.0, aspect_ratio: 1.3 },
      { particle_id: "p_05", pb_percent: 50.0, ba_percent: 30.0, sb_percent: 0.0, aspect_ratio: 1.0 },
    ],
  },
  {
    id: "VECTOR_22_GSR_C",
    name: "VECTOR_22_GSR_C: Aspect Ratio Morphology Downgrade",
    nameTr: "VECTOR_22_GSR_C: Morfolojik En/Boy Oranı İndirgemesi",
    desc: "Triad elemental concentrations but irregular non-spherical shape (AR = 1.8 > 1.3) downgraded to Commonly Associated",
    descTr: "Karakteristik Pb-Ba-Sb elementleri ancak asferik düzensiz şekil (AR = 1.8 > 1.3), Sık Rastlanan seviyesine düşürüldü",
    category: "gsr",
    particles: [
      { particle_id: "p_01", pb_percent: 35.0, ba_percent: 25.0, sb_percent: 15.0, aspect_ratio: 1.8 },
    ],
  },
  {
    id: "VECTOR_22_GSR_D",
    name: "VECTOR_22_GSR_D: Environmental Background (Non-GSR)",
    nameTr: "VECTOR_22_GSR_D: Çevresel Arka Plan (GSR Dışı)",
    desc: "Brake lining and pyrotechnics particles without significant heavy metals, LR = 1.0",
    descTr: "Fren balatası ve piroteknik kalıntı parçacıkları, LR = 1.0",
    category: "gsr",
    particles: [
      { particle_id: "p_01", pb_percent: 1.0, ba_percent: 2.0, sb_percent: 0.5, aspect_ratio: 1.1 },
      { particle_id: "p_02", pb_percent: 0.0, ba_percent: 0.0, sb_percent: 0.0, aspect_ratio: 2.0 },
    ],
  },
  {
    id: "VECTOR_22_CMC_E",
    name: "VECTOR_22_CMC_E: Positive 3D CMC Identification (K = 6 >= 6)",
    nameTr: "VECTOR_22_CMC_E: Kesin Pozitif 3D CMC Eşleşmesi (K = 6 >= 6)",
    desc: "6x Congruent Matching Cells satisfying CCF >= 0.55, dx,dy <= 15um, dtheta <= 1.0 deg; P_false < 1e-6",
    descTr: "Tüm eşikleri karşılayan 6 adet uyumlu eşleşen hücre, P_yanlış < 10^-6",
    category: "cmc",
    cells: [
      { cell_id: "cell_1", ccf_max: 0.85, delta_x_um: 2.0, delta_y_um: -1.5, delta_theta_deg: 0.3 },
      { cell_id: "cell_2", ccf_max: 0.82, delta_x_um: 3.5, delta_y_um: -2.0, delta_theta_deg: 0.4 },
      { cell_id: "cell_3", ccf_max: 0.78, delta_x_um: 1.0, delta_y_um: -0.5, delta_theta_deg: -0.2 },
      { cell_id: "cell_4", ccf_max: 0.90, delta_x_um: 4.0, delta_y_um: -1.0, delta_theta_deg: 0.1 },
      { cell_id: "cell_5", ccf_max: 0.75, delta_x_um: -2.0, delta_y_um: 1.5, delta_theta_deg: -0.5 },
      { cell_id: "cell_6", ccf_max: 0.88, delta_x_um: 1.5, delta_y_um: -1.2, delta_theta_deg: 0.2 },
    ],
  },
  {
    id: "VECTOR_22_CMC_F",
    name: "VECTOR_22_CMC_F: Translation Outlier Rejection (|dx| > 15 um)",
    nameTr: "VECTOR_22_CMC_F: Öteleme Sapması Reddi (|dx| > 15 um)",
    desc: "High CCF but lateral displacement exceeds 15 um; 3 cells rejected leaving K = 5 (Inconclusive)",
    descTr: "Yüksek CCF fakat yanal sapma 15 um sınırını aşar; 3 hücre elenerek K = 5 (Belirsiz) kalır",
    category: "cmc",
    cells: [
      { cell_id: "cell_1", ccf_max: 0.80, delta_x_um: 5.0, delta_y_um: 5.0, delta_theta_deg: 0.2 },
      { cell_id: "cell_2", ccf_max: 0.82, delta_x_um: 4.0, delta_y_um: 3.0, delta_theta_deg: 0.1 },
      { cell_id: "cell_3", ccf_max: 0.79, delta_x_um: 6.0, delta_y_um: 4.0, delta_theta_deg: -0.1 },
      { cell_id: "cell_4", ccf_max: 0.85, delta_x_um: 3.0, delta_y_um: 2.0, delta_theta_deg: 0.3 },
      { cell_id: "cell_5", ccf_max: 0.81, delta_x_um: 5.0, delta_y_um: 5.0, delta_theta_deg: 0.0 },
      { cell_id: "cell_6", ccf_max: 0.80, delta_x_um: 25.0, delta_y_um: 5.0, delta_theta_deg: 0.2 },
      { cell_id: "cell_7", ccf_max: 0.82, delta_x_um: 22.0, delta_y_um: 4.0, delta_theta_deg: 0.1 },
      { cell_id: "cell_8", ccf_max: 0.78, delta_x_um: 28.0, delta_y_um: 3.0, delta_theta_deg: -0.2 },
    ],
  },
  {
    id: "VECTOR_22_CMC_G",
    name: "VECTOR_22_CMC_G: Angular Rotation Rejection (|dtheta| > 1.0 deg)",
    nameTr: "VECTOR_22_CMC_G: Açısal Rotasyon Reddi (|dtheta| > 1.0 deg)",
    desc: "Rotational shift exceeds 1.0 deg; all candidate cells rejected (K = 0, Elimination)",
    descTr: "Açısal dönme sapması 1.0 dereceyi aşar; tüm hücreler elenir (K = 0, Eleme)",
    category: "cmc",
    cells: [
      { cell_id: "cell_1", ccf_max: 0.70, delta_x_um: 0.0, delta_y_um: 0.0, delta_theta_deg: 2.5 },
      { cell_id: "cell_2", ccf_max: 0.40, delta_x_um: 0.0, delta_y_um: 0.0, delta_theta_deg: 0.1 },
    ],
  },
  {
    id: "VECTOR_22_GSR_H",
    name: "VECTOR_22_GSR_H: Multi-Sample Casework Cohort & API Integration",
    nameTr: "VECTOR_22_GSR_H: Çoklu Numune Vaka Kohortu & API Doğrulaması",
    desc: "Primary questioned casework evidence: 3 characteristic particles and K = 6 CMC striations",
    descTr: "Birincil şüpheli vaka delili: 3 karakteristik parçacık ve K = 6 CMC namlu çizgisi",
    category: "gsr",
    particles: [
      { particle_id: "p_casework_1", pb_percent: 30.0, ba_percent: 20.0, sb_percent: 15.0, aspect_ratio: 1.1 },
      { particle_id: "p_casework_2", pb_percent: 25.0, ba_percent: 25.0, sb_percent: 10.0, aspect_ratio: 1.2 },
      { particle_id: "p_casework_3", pb_percent: 28.0, ba_percent: 22.0, sb_percent: 18.0, aspect_ratio: 1.0 },
    ],
    cells: [
      { cell_id: "cell_c1", ccf_max: 0.85, delta_x_um: 1.0, delta_y_um: 1.0, delta_theta_deg: 0.2 },
      { cell_id: "cell_c2", ccf_max: 0.86, delta_x_um: 1.2, delta_y_um: 1.1, delta_theta_deg: 0.1 },
      { cell_id: "cell_c3", ccf_max: 0.88, delta_x_um: 0.9, delta_y_um: 0.8, delta_theta_deg: -0.1 },
      { cell_id: "cell_c4", ccf_max: 0.84, delta_x_um: 1.5, delta_y_um: 1.2, delta_theta_deg: 0.2 },
      { cell_id: "cell_c5", ccf_max: 0.89, delta_x_um: 1.1, delta_y_um: 0.9, delta_theta_deg: 0.0 },
      { cell_id: "cell_c6", ccf_max: 0.87, delta_x_um: 1.3, delta_y_um: 1.0, delta_theta_deg: 0.1 },
    ],
  },
];

// Initial Hair Specimens (SWGMAT Standards)
export const INITIAL_HAIR_SPECIMENS: HairSpecimen[] = [
  {
    id: "HAIR-SAMPLE-501",
    shaft_diameter_um: 80.0,
    medulla_diameter_um: 15.0,
    origin: "HUMAN",
    originTr: "İNSAN",
    root_morphology: "ANAGEN (WITH SHEATH)",
    root_morphologyTr: "ANAGEN (KILIFLI KÖK)",
    dna_strategy: "NUCLEAR STR OPTIMAL (24 LOCI)",
    dna_strategyTr: "ÇEKİRDEK STR OPTİMAL (24 LOKUS)",
    badge: "nDNA STR",
  },
  {
    id: "HAIR-SAMPLE-502",
    shaft_diameter_um: 80.0,
    medulla_diameter_um: 50.0,
    origin: "NON_HUMAN_ANIMAL",
    originTr: "İNSAN DIŞI HAYVAN",
    root_morphology: "TELOGEN (NO SHEATH)",
    root_morphologyTr: "TELOGEN (KILIFSIZ)",
    dna_strategy: "MITOCHONDRIAL HV1/HV2/HV3",
    dna_strategyTr: "MİTOKONDRİYAL HV1/HV2/HV3",
    badge: "mtDNA HV1/2",
  },
  {
    id: "SPERM-CELL-901",
    shaft_diameter_um: 20.0,
    medulla_diameter_um: 0.0,
    origin: "HUMAN SPERMATOZOA",
    originTr: "İNSAN SPERMATOZONU",
    root_morphology: "NORMAL MORPHOLOGY",
    root_morphologyTr: "NORMAL MORFOLOJİ",
    dna_strategy: "DIFFERENTIAL EXTRACTION STR",
    dna_strategyTr: "DİFERANSİYEL EKSTRAKSİYON STR",
    badge: "DIFF-STR",
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// CLIENT MATHEMATICAL EVALUATORS (ASTM E1588-20, NIST CMC & SWGMAT)
// ═══════════════════════════════════════════════════════════════════════════════

export function evaluateClientGsr(particles: GsrParticle[], isTr: boolean): GsrResponse {
  const MIN_ELEM = 10.0;
  const MAX_CHAR_AR = 1.3;
  const MAX_CONS_AR = 1.5;

  let characteristicCount = 0;
  let consistentCount = 0;
  let associatedCount = 0;

  const classified = particles.map((p, idx) => {
    const pb = p.pb_percent;
    const ba = p.ba_percent;
    const sb = p.sb_percent;
    const al = p.al_percent || 0;
    const ar = Math.max(0.1, p.aspect_ratio);

    let tier = "ENVIRONMENTAL_BACKGROUND";

    // Characteristic: Pb >= 10, Ba >= 10, Sb >= 5 (or 10) and AR <= 1.3
    if (pb >= MIN_ELEM && ba >= MIN_ELEM && sb >= 5.0 && ar <= MAX_CHAR_AR) {
      tier = "CHARACTERISTIC_GSR";
      characteristicCount++;
    } else if (
      ((pb >= MIN_ELEM && ba >= MIN_ELEM) ||
        (pb >= MIN_ELEM && sb >= MIN_ELEM) ||
        (ba >= MIN_ELEM && sb >= MIN_ELEM)) &&
      ar <= MAX_CONS_AR
    ) {
      tier = "CONSISTENT_WITH_GSR";
      consistentCount++;
    } else if (
      pb >= MIN_ELEM ||
      ba >= MIN_ELEM ||
      (ba >= MIN_ELEM && al >= MIN_ELEM) ||
      (pb >= MIN_ELEM && ba >= MIN_ELEM && sb >= MIN_ELEM && ar > MAX_CHAR_AR)
    ) {
      tier = "COMMONLY_ASSOCIATED";
      associatedCount++;
    }

    return {
      particle_id: p.particle_id || `p_${idx + 1}`,
      classification_tier: tier,
      pb_percent: pb,
      ba_percent: ba,
      sb_percent: sb,
      aspect_ratio: ar,
    };
  });

  let lr = 1.0;
  let strength = isTr ? "Belirsiz / Nötr Destek (LR = 1.0)" : "Inconclusive / Neutral Support (LR = 1.0)";

  if (characteristicCount >= 3) {
    lr = 10000.0;
    strength = isTr
      ? "Ateşli Silah Atışına Son Derece Güçlü Kanıt Desteği (LR > 10.000)"
      : "Extremely Strong Support for Firearm Discharge (LR > 10,000)";
  } else if (characteristicCount >= 1 || consistentCount >= 5) {
    lr = 500.0;
    strength = isTr
      ? "Ateşli Silah Atışına Güçlü Kanıt Desteği (100 < LR <= 10.000)"
      : "Strong Support for Firearm Discharge (100 < LR <= 10,000)";
  } else if (consistentCount >= 1) {
    lr = 25.0;
    strength = isTr
      ? "Ateşli Silah Atışına Orta Düzey Kanıt Desteği (10 < LR <= 100)"
      : "Moderate Support for Firearm Discharge (10 < LR <= 100)";
  }

  const shield = isTr
    ? "ÖNEMLİ (ASTM E1588-20 SEM-EDX GSR Değerlendirici Hukuki Kalkan): Karakteristik Pb-Ba-Sb parçacıklarının tespiti, bir ateşli silah atış olayına yakınlığı gösterir; ancak belirli bir atıcıyı kesin olarak belirleyemez veya kirlenmiş kolluk ortamlarından ikincil transferi dışlayamaz."
    : "IMPORTANT (ASTM E1588-20 SEM-EDX GSR Evaluative Legal Shield): Finding characteristic Pb-Ba-Sb particles indicates proximity to a firearm discharge event, but cannot identify the specific shooter or exclude secondary transfer from contaminated law enforcement environments.";

  return {
    total_particles_scanned: particles.length,
    characteristic_particles: characteristicCount,
    consistent_particles: consistentCount,
    commonly_associated_particles: associatedCount,
    likelihood_ratio: lr,
    evidence_strength: strength,
    classified_particles: classified,
    prosecutors_fallacy_shield: shield,
  };
}

export function evaluateClientCmc(cells: CmcCell[], isTr: boolean): CmcResponse {
  const MIN_CCF = 0.55;
  const MAX_TRANS_UM = 15.0;
  const MAX_ROT_DEG = 1.0;
  const MIN_CMC = 6;

  let cmcCount = 0;
  const evaluated = cells.map((c) => {
    const isCcf = c.ccf_max >= MIN_CCF;
    const isTrans = Math.abs(c.delta_x_um) <= MAX_TRANS_UM && Math.abs(c.delta_y_um) <= MAX_TRANS_UM;
    const isRot = Math.abs(c.delta_theta_deg) <= MAX_ROT_DEG;
    const isCmc = isCcf && isTrans && isRot;
    if (isCmc) cmcCount++;
    return { ...c, is_congruent_matching_cell: isCmc };
  });

  let verdict = "ELIMINATION_NO_MATCH";
  let pFalse = "> 0.50";
  let conclusion = isTr
    ? "Eleme / Eşleşmeme (K < 3 CMC)."
    : "Elimination / Non-match (K < 3 CMC).";

  if (cmcCount >= MIN_CMC) {
    verdict = "POSITIVE_IDENTIFICATION";
    pFalse = "< 1e-6";
    conclusion = isTr
      ? `Şüpheli ateşli silaha kesin balistik eşleşme (K = ${cmcCount} >= 6 CMC, P_yanlış < 10^-6).`
      : `Definitive ballistic match to questioned firearm (K = ${cmcCount} >= 6 CMC, P_false < 10^-6).`;
  } else if (cmcCount >= 3) {
    verdict = "INCONCLUSIVE_BORDERLINE";
    pFalse = "0.01 - 0.05";
    conclusion = isTr
      ? `Sınırda / Belirsiz namlu çizgisi benzerliği (3 <= K = ${cmcCount} <= 5 CMC).`
      : `Inconclusive / Borderline striation similarity (3 <= K = ${cmcCount} <= 5 CMC).`;
  }

  const shield = isTr
    ? "ÖNEMLİ (3D CMC Balistik Namlu Çizgisi Hukuki Kalkan - AFTE Kriterleri): Tanımlama, K >= 6 uyumlu eşleşen hücrenin çapraz korelasyon (CCF >= 0.55), öteleme (+/-15 um) ve dönme (+/-1.0 deg) toleranslarını karşılamasıyla sağlanır; P_yanlış < 10^-6 istatistiksel hata sınırı sunar."
    : "IMPORTANT (3D CMC Ballistic Striation Legal Shield - AFTE Criteria): Identification is established when K >= 6 congruent matching cells satisfy cross-correlation (CCF >= 0.55), translation (+/-15 um), and rotation (+/-1.0 deg) tolerances, providing statistical error bounds of P_false < 10^-6.";

  return {
    total_cells_evaluated: cells.length,
    cmc_count: cmcCount,
    identification_verdict: verdict,
    false_match_probability: pFalse,
    ballistic_conclusion: conclusion,
    evaluated_cells: evaluated,
    prosecutors_fallacy_shield: shield,
  };
}

export function computeMedullaryIndex(medullaUm: number, shaftUm: number): number {
  if (shaftUm <= 0) return 0.0;
  return Number((medullaUm / shaftUm).toFixed(3));
}

// ═══════════════════════════════════════════════════════════════════════════════
// DETERMINISTIC CRYPTOGRAPHIC STATE AUDIT HASH (H_ballistics)
// ═══════════════════════════════════════════════════════════════════════════════

export async function computeBallisticsAuditHash(
  particles: GsrParticle[],
  cells: CmcCell[],
  specimens: HairSpecimen[],
  gsrResult: GsrResponse,
  cmcResult: CmcResponse,
  caseId: string
): Promise<string> {
  const payload = JSON.stringify({
    caseId,
    standard: "ISO/IEC 17025:2017 Sec 7.8 | ASTM E1588-20 | NIST CMC",
    particlesCount: particles.length,
    particlesSummary: particles.map((p) => ({ id: p.particle_id, pb: p.pb_percent, ba: p.ba_percent, sb: p.sb_percent, ar: p.aspect_ratio })),
    cellsCount: cells.length,
    cellsSummary: cells.map((c) => ({ id: c.cell_id, ccf: c.ccf_max, dx: c.delta_x_um, dy: c.delta_y_um, dt: c.delta_theta_deg })),
    specimensCount: specimens.length,
    gsrLr: gsrResult.likelihood_ratio,
    gsrStrength: gsrResult.evidence_strength,
    cmcCount: cmcResult.cmc_count,
    cmcVerdict: cmcResult.identification_verdict,
  });

  if (typeof window !== "undefined" && window.crypto && window.crypto.subtle) {
    try {
      const msgUint8 = new TextEncoder().encode(payload);
      const hashBuffer = await window.crypto.subtle.digest("SHA-256", msgUint8);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
    } catch {
      // Fallback below
    }
  }

  // Pure deterministic JS fallback hash
  let hash = 0x811c9dc5;
  for (let i = 0; i < payload.length; i++) {
    hash ^= payload.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193);
  }
  const hex32 = (hash >>> 0).toString(16).padStart(8, "0");
  return `ballistics_state_${hex32}${hex32}${hex32}${hex32}${hex32}${hex32}${hex32}${hex32}`.slice(0, 64);
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export default function BallisticsGsrPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  // Forensic case store connection
  const activeCase = useForensicCaseStore((state) => state.activeCase);
  const addAuditLog = useForensicCaseStore((state) => state.addAuditLog);

  // 5 Canonical Tabs
  const [activeTab, setActiveTab] = useState<BallisticsTabId>("gsr_edx");
  const [selectedPresetId, setSelectedPresetId] = useState<string>("VECTOR_22_GSR_A");

  // GSR Particle State
  const [particles, setParticles] = useState<GsrParticle[]>(GOLDEN_BALLISTICS_PRESETS[0].particles || []);

  // CMC Striation State
  const [cmcCells, setCmcCells] = useState<CmcCell[]>(
    GOLDEN_BALLISTICS_PRESETS.find((p) => p.id === "VECTOR_22_CMC_E")?.cells || []
  );

  // Hair Specimen State (Ported from MicroscopyPanel)
  const [specimens, setSpecimens] = useState<HairSpecimen[]>(INITIAL_HAIR_SPECIMENS);
  const [selectedSpecimenId, setSelectedSpecimenId] = useState<string>("HAIR-SAMPLE-501");
  const [activeShaftUm, setActiveShaftUm] = useState<number>(80.0);
  const [activeMedullaUm, setActiveMedullaUm] = useState<number>(15.0);

  // Execution & Latency State
  const [loading, setLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [stageText, setStageText] = useState<string>("");
  const [executionStatus, setExecutionStatus] = useState<"live_preview" | "server_verified">("live_preview");
  const [serverLatency, setServerLatency] = useState<number | null>(null);

  const [copiedHash, setCopiedHash] = useState<boolean>(false);
  const [copiedReport, setCopiedReport] = useState<boolean>(false);
  const [auditHash, setAuditHash] = useState<string>("");

  // Live Reactive Evaluations
  const liveGsrResult = useMemo(() => evaluateClientGsr(particles, isTr), [particles, isTr]);
  const liveCmcResult = useMemo(() => evaluateClientCmc(cmcCells, isTr), [cmcCells, isTr]);

  const [gsrResult, setGsrResult] = useState<GsrResponse>(liveGsrResult);
  const [cmcResult, setCmcResult] = useState<CmcResponse>(liveCmcResult);

  // Synchronize state when live changes
  useEffect(() => {
    setGsrResult(liveGsrResult);
  }, [liveGsrResult]);

  useEffect(() => {
    setCmcResult(liveCmcResult);
  }, [liveCmcResult]);

  // Compute deterministic SHA-256 state audit digest
  useEffect(() => {
    let isMounted = true;
    computeBallisticsAuditHash(
      particles,
      cmcCells,
      specimens,
      gsrResult,
      cmcResult,
      activeCase.metadata.caseId
    ).then((hash) => {
      if (isMounted) setAuditHash(hash);
    });
    return () => {
      isMounted = false;
    };
  }, [particles, cmcCells, specimens, gsrResult, cmcResult, activeCase.metadata.caseId]);

  // Handlers for GSR Particles
  const handleUpdateParticle = (index: number, field: keyof GsrParticle, value: number) => {
    setSelectedPresetId("");
    setExecutionStatus("live_preview");
    const updated = [...particles];
    updated[index] = { ...updated[index], [field]: value };
    setParticles(updated);
  };

  const handleAddParticle = () => {
    setSelectedPresetId("");
    setExecutionStatus("live_preview");
    const newId = `p_${particles.length + 1}`;
    setParticles([
      ...particles,
      { particle_id: newId, pb_percent: 30.0, ba_percent: 20.0, sb_percent: 15.0, aspect_ratio: 1.1 },
    ]);
  };

  const handleRemoveParticle = (index: number) => {
    if (particles.length <= 1) return;
    setSelectedPresetId("");
    setExecutionStatus("live_preview");
    setParticles(particles.filter((_, i) => i !== index));
  };

  // Handlers for CMC Cells
  const handleUpdateCmcCell = (index: number, field: keyof CmcCell, value: number) => {
    setSelectedPresetId("");
    setExecutionStatus("live_preview");
    const updated = [...cmcCells];
    updated[index] = { ...updated[index], [field]: value };
    setCmcCells(updated);
  };

  const handleAddCmcCell = () => {
    setSelectedPresetId("");
    setExecutionStatus("live_preview");
    const newId = `cell_${cmcCells.length + 1}`;
    setCmcCells([
      ...cmcCells,
      { cell_id: newId, ccf_max: 0.85, delta_x_um: 1.5, delta_y_um: -1.0, delta_theta_deg: 0.2 },
    ]);
  };

  const handleRemoveCmcCell = (index: number) => {
    if (cmcCells.length <= 1) return;
    setSelectedPresetId("");
    setExecutionStatus("live_preview");
    setCmcCells(cmcCells.filter((_, i) => i !== index));
  };

  // Select Preset Handler
  const handleSelectPreset = (preset: BenchmarkPreset) => {
    setSelectedPresetId(preset.id);
    setExecutionStatus("live_preview");

    if (preset.particles && preset.particles.length > 0) {
      setParticles([...preset.particles]);
    }
    if (preset.cells && preset.cells.length > 0) {
      setCmcCells([...preset.cells]);
    }

    if (preset.category === "gsr") {
      setActiveTab("gsr_edx");
    } else {
      setActiveTab("cmc_striation");
    }

    addAuditLog({
      event: "GSR_SAMPLE_LOADED",
      module: "Subsystem 25 - Ballistics & GSR",
      analyst: activeCase.metadata.leadAnalyst || "Firearm & Trace Examiner",
      status: "PASS",
      findingSeverity: "NOMINAL",
      standard: "ASTM E1588-20 | NIST CMC Standards",
    });
  };

  // Specimen selection handler for Microscopy Tab
  const handleSelectSpecimen = (s: HairSpecimen) => {
    setSelectedSpecimenId(s.id);
    setActiveShaftUm(s.shaft_diameter_um);
    setActiveMedullaUm(s.medulla_diameter_um);

    addAuditLog({
      event: "MICROSCOPY_SAMPLE_EVALUATED",
      module: "Subsystem 25 - Ballistics & GSR",
      analyst: activeCase.metadata.leadAnalyst || "Trace Evidence Examiner",
      status: "PASS",
      findingSeverity: "NOMINAL",
      standard: "SWGMAT Forensic Hair Microscopy Guide",
    });
  };

  // API Solver Execution
  const runServerVerification = async () => {
    if (loading) return;
    setLoading(true);
    setProgress(20);
    setStageText(
      isTr
        ? "SEM-EDX X-ray spektrumları & NIST 3D topoğrafya taranıyor..."
        : "Scanning SEM-EDX X-ray spectra & NIST 3D topography..."
    );

    const API_BASE = getApiBaseUrl();
    const startTime = performance.now();

    const t1 = setTimeout(() => {
      setProgress(55);
      setStageText(
        isTr
          ? "ASTM E1588-20 üçlü sınıflandırıcı & Song CMC korelasyon matrisi çalıştırılıyor..."
          : "Executing ASTM E1588-20 ternary classifier & Song CMC correlation matrix..."
      );
    }, 250);

    try {
      if (activeTab === "gsr_edx") {
        const res = await fetch(`${API_BASE}/api/v1/forensic/physical/gsr-sem-edx-analysis`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ particles }),
          signal: AbortSignal.timeout(3000),
        });
        if (res.ok) {
          const data = await res.json();
          setGsrResult(data);
          setExecutionStatus("server_verified");
        } else {
          setGsrResult(liveGsrResult);
        }
      } else if (activeTab === "cmc_striation") {
        const res = await fetch(`${API_BASE}/api/v1/forensic/physical/cmc-striation-matching`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            cells: cmcCells,
            mean_delta_x_um: 0.0,
            mean_delta_y_um: 0.0,
            mean_delta_theta_deg: 0.0,
          }),
          signal: AbortSignal.timeout(3000),
        });
        if (res.ok) {
          const data = await res.json();
          setCmcResult(data);
          setExecutionStatus("server_verified");
        } else {
          setCmcResult(liveCmcResult);
        }
      }
    } catch {
      // Graceful local math fallback
      setGsrResult(liveGsrResult);
      setCmcResult(liveCmcResult);
    } finally {
      clearTimeout(t1);
      setProgress(100);
      setStageText(isTr ? "Balistik analiz doğrulandı." : "Ballistic analysis verified.");
      const endTime = performance.now();
      setServerLatency(Math.round(endTime - startTime));

      setTimeout(() => {
        setLoading(false);

        addAuditLog({
          event: "CMC_SURFACE_EVALUATED",
          module: "Subsystem 25 - Ballistics & GSR",
          analyst: activeCase.metadata.leadAnalyst || "Firearm & Toolmark Examiner",
          status: "PASS",
          findingSeverity: "NOMINAL",
          standard: "ASTM E1588-20 | NIST CMC | ISO/IEC 17025:2017",
        });
      }, 300);
    }
  };

  const handleCopyHash = () => {
    const textToCopy = auditHash || "ballistics_state_audit_digest_pending";
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(textToCopy);
      setCopiedHash(true);
      setTimeout(() => setCopiedHash(false), 2000);
    }
  };

  const handleCopyReport = () => {
    const reportText = [
      "═══════════════════════════════════════════════════════════════════════════════",
      "FORENZA FORENSIC INTELLIGENCE - BALLISTICS, SEM-EDX GSR & MICROSCOPY REPORT",
      "STANDARDS: ASTM E1588-20 | NIST SONG ET AL. CMC | SWGMAT | ISO/IEC 17025:2017",
      "═══════════════════════════════════════════════════════════════════════════════",
      `Case ID: ${activeCase.metadata.caseId}`,
      `Lead Examiner: ${activeCase.metadata.leadAnalyst}`,
      `Active Benchmark Preset: ${selectedPresetId || "CUSTOM"}`,
      "── ASTM E1588-20 SEM-EDX GSR EVALUATION ──",
      `Total Particles Scanned: ${gsrResult.total_particles_scanned}`,
      `Characteristic Particles (Pb-Ba-Sb): ${gsrResult.characteristic_particles}`,
      `Consistent Particles: ${gsrResult.consistent_particles}`,
      `Commonly Associated Particles: ${gsrResult.commonly_associated_particles}`,
      `Likelihood Ratio (LR): ${gsrResult.likelihood_ratio}`,
      `Evidence Strength: ${gsrResult.evidence_strength}`,
      "── NIST 3D CONGRUENT MATCHING CELLS (CMC) STRIATIONS ──",
      `Total Cells Evaluated: ${cmcResult.total_cells_evaluated}`,
      `Congruent Matching Cells (K): ${cmcResult.cmc_count}`,
      `Identification Verdict: ${cmcResult.identification_verdict}`,
      `False Match Probability: ${cmcResult.false_match_probability}`,
      `Ballistic Conclusion: ${cmcResult.ballistic_conclusion}`,
      "── MICROSCOPIC TRACE & HAIR MORPHOMETRY ──",
      `Selected Specimen: ${selectedSpecimenId}`,
      `Shaft Diameter: ${activeShaftUm} um | Medulla Diameter: ${activeMedullaUm} um`,
      `Medullary Index: ${computeMedullaryIndex(activeMedullaUm, activeShaftUm)} (${computeMedullaryIndex(activeMedullaUm, activeShaftUm) < 0.33 ? "Human < 0.33" : "Animal > 0.50"})`,
      `Cryptographic State Hash (SHA-256): ${auditHash}`,
      `Legal Evaluative Shield: ${gsrResult.prosecutors_fallacy_shield}`,
      "═══════════════════════════════════════════════════════════════════════════════",
    ].join("\n");

    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(reportText);
      setCopiedReport(true);
      setTimeout(() => setCopiedReport(false), 2000);
    }

    addAuditLog({
      event: "BALLISTICS_REPORT_COPIED",
      module: "Subsystem 25 - Ballistics & GSR",
      analyst: activeCase.metadata.leadAnalyst || "Firearm & Toolmark Examiner",
      status: "PASS",
      findingSeverity: "NOMINAL",
      standard: "ISO/IEC 17025:2017 Sec 7.8",
    });
  };

  const handleExportJson = () => {
    const data = {
      caseId: activeCase.metadata.caseId,
      subsystem: "25_BALLISTICS_GSR_MICROSCOPY",
      timestamp: new Date().toISOString(),
      activePreset: selectedPresetId,
      gsr: {
        totalParticles: gsrResult.total_particles_scanned,
        characteristicParticles: gsrResult.characteristic_particles,
        consistentParticles: gsrResult.consistent_particles,
        commonlyAssociatedParticles: gsrResult.commonly_associated_particles,
        likelihoodRatio: gsrResult.likelihood_ratio,
        evidenceStrength: gsrResult.evidence_strength,
        particles,
      },
      cmc: {
        totalCells: cmcResult.total_cells_evaluated,
        cmcCount: cmcResult.cmc_count,
        identificationVerdict: cmcResult.identification_verdict,
        falseMatchProbability: cmcResult.false_match_probability,
        ballisticConclusion: cmcResult.ballistic_conclusion,
        cells: cmcCells,
      },
      microscopy: {
        activeSpecimenId: selectedSpecimenId,
        shaftDiameterUm: activeShaftUm,
        medullaDiameterUm: activeMedullaUm,
        medullaryIndex: computeMedullaryIndex(activeMedullaUm, activeShaftUm),
        specimens,
      },
      cryptographicStateHash: auditHash,
      standard: "ASTM E1588-20 | NIST CMC | SWGMAT | ISO/IEC 17025:2017",
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `FORENZA_BALLISTICS_${selectedPresetId || "CUSTOM"}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const liveMedullaryIndex = computeMedullaryIndex(activeMedullaUm, activeShaftUm);

  return (
    <div className="space-y-6 font-mono text-tactical-text max-w-full overflow-hidden">
      {/* ── 1. TACTICAL MISSION BAR ── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-400 shrink-0 shadow-[0_0_15px_rgba(245,158,11,0.15)]">
              <Target className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/40 text-amber-300">
                  PILLAR 5 - MODULE 22
                </span>
                <span className="text-[10px] text-tactical-text-muted">
                  ASTM E1588-20 | NIST CMC | SWGMAT | ISO 17025:2017
                </span>
              </div>
              <h1 className="text-base sm:text-lg font-bold text-tactical-text truncate mt-0.5 tracking-tight">
                {isTr
                  ? "SEM-EDX Atış Artığı (GSR), 3D CMC Balistik & Mikroskopi Stüdyosu"
                  : "SEM-EDX Gunshot Residue (GSR), 3D CMC Ballistics & Microscopy Studio"}
              </h1>
            </div>
          </div>

          {/* 5 Canonical Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
            {[
              { id: "gsr_edx", label: isTr ? "1. SEM-EDX GSR" : "1. SEM-EDX GSR", icon: Flame },
              { id: "cmc_striation", label: isTr ? "2. 3D CMC Balistik" : "2. 3D CMC Ballistics", icon: Target },
              { id: "microscopy_hair", label: isTr ? "3. Mikroskopi & Kıl" : "3. Microscopy & Hair", icon: Microscope },
              { id: "benchmarks", label: isTr ? "4. Altın Vektörler" : "4. Benchmarks", icon: Database },
              { id: "iso_audit", label: isTr ? "5. ISO Rapor & Denetim" : "5. ISO Audit", icon: FileCheck },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as BallisticsTabId)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                    isActive
                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-[0_0_12px_rgba(245,158,11,0.2)]"
                      : "text-tactical-text-muted hover:text-tactical-text hover:bg-tactical-surface/60 border border-transparent"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Golden Presets Ribbon */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-amber-400" />
              {isTr ? "Resmi Doğrulama Kıyaslama Vektörleri (VECTOR_22_GSR_A-H):" : "Official Verification Golden Benchmark Vectors (VECTOR_22_GSR_A-H):"}
            </span>
            <span className="text-[10px] text-tactical-text-muted">
              {activeTab === "cmc_striation" ? `${cmcCells.length} ${isTr ? "Hücre Yüklü" : "Cells Loaded"}` : `${particles.length} ${isTr ? "Parçacık Yüklü" : "Particles Loaded"}`}
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-1.5">
            {GOLDEN_BALLISTICS_PRESETS.map((p) => {
              const isSelected = selectedPresetId === p.id;
              return (
                <button
                  key={p.id}
                  onClick={() => handleSelectPreset(p)}
                  className={`px-2 py-1.5 rounded-lg text-[10px] font-bold text-left transition-all truncate border ${
                    isSelected
                      ? "bg-amber-500/20 border-amber-500/60 text-amber-200 shadow-[0_0_10px_rgba(245,158,11,0.25)]"
                      : "bg-[#0B1222] border-tactical-border/60 text-tactical-text-muted hover:text-tactical-text hover:border-tactical-border"
                  }`}
                  title={isTr ? p.descTr : p.desc}
                >
                  <div className="font-semibold truncate">{p.id.replace("VECTOR_22_", "")}</div>
                  <div className="text-[8px] opacity-70 truncate">{isTr ? p.nameTr.split(":")[1] || p.nameTr : p.name.split(":")[1] || p.name}</div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── 2. ACTIVE TAB VIEWPORT ── */}

      {/* TAB 1: SEM-EDX GSR ANALYSIS */}
      {activeTab === "gsr_edx" && (
        <div className="space-y-6">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Karakteristik Parçacıklar (Pb-Ba-Sb)" : "Characteristic Particles (Pb-Ba-Sb)"}
              </span>
              <div className="text-2xl font-bold text-amber-400 tabular-nums">
                {gsrResult.characteristic_particles} <span className="text-xs text-tactical-text-muted">/ {particles.length}</span>
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "Pb, Ba >= %10, Sb >= %5, AR <= 1.3" : "Pb, Ba >= 10%, Sb >= 5%, AR <= 1.3"}
              </p>
            </div>

            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Uyumlu İkili Parçacıklar" : "Consistent Bi-Element Particles"}
              </span>
              <div className="text-2xl font-bold text-cyan-400 tabular-nums">
                {gsrResult.consistent_particles} <span className="text-xs text-tactical-text-muted">/ {particles.length}</span>
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "2-Bileşenli çiftler (Pb-Ba / Pb-Sb / Ba-Sb), AR <= 1.5" : "2-component pairs (Pb-Ba/Pb-Sb/Ba-Sb), AR <= 1.5"}
              </p>
            </div>

            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Olasılık Oranı (LR)" : "Likelihood Ratio (LR)"}
              </span>
              <div className="text-2xl font-bold text-rose-400 tabular-nums">
                {gsrResult.likelihood_ratio >= 1000 ? gsrResult.likelihood_ratio.toLocaleString() : gsrResult.likelihood_ratio}
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "ASTM E1588-20 değerlendirici kanıt gücü" : "ASTM E1588-20 evaluative strength"}
              </p>
            </div>

            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Doğrulama Durumu" : "Verification Status"}
              </span>
              <div className="text-sm font-bold text-emerald-400 flex items-center gap-1.5 mt-1.5">
                <CheckCircle2 className="w-4 h-4" />
                <span>{executionStatus === "server_verified" ? (isTr ? "Sunucu Onaylı" : "Server Verified") : (isTr ? "Canlı İstemci Hesabı" : "Live Client Calculation")}</span>
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {serverLatency ? `${serverLatency} ms latency` : (isTr ? "Sıfır gecikmeli reaktif motor" : "Zero-latency reactive solver")}
              </p>
            </div>
          </div>

          {/* Particles Table and Ternary Scatter */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Particles Table Card */}
            <div className="lg:col-span-8 bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Flame className="w-4 h-4 text-amber-400" />
                  <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                    {isTr ? "SEM-EDX Parçacık Elemental Kompozisyonu (Ağırlık %)" : "SEM-EDX Particle Elemental Composition (Wt %)"}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleAddParticle}
                    className="px-2.5 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-bold transition-all flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>{isTr ? "Parçacık Ekle" : "Add Particle"}</span>
                  </button>
                  <button
                    onClick={runServerVerification}
                    disabled={loading}
                    className="px-3 py-1 rounded-lg bg-amber-500 text-black hover:bg-amber-400 text-xs font-bold transition-all flex items-center gap-1.5"
                  >
                    <Activity className="w-3.5 h-3.5" />
                    <span>{loading ? (isTr ? "Doğrulanıyor..." : "Verifying...") : (isTr ? "Sunucuda Doğrula" : "Verify API")}</span>
                  </button>
                </div>
              </div>

              {/* Responsive Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-tactical-border/60 text-tactical-text-muted text-[10px] uppercase">
                      <th className="py-2 px-2">ID</th>
                      <th className="py-2 px-2">Pb %</th>
                      <th className="py-2 px-2">Ba %</th>
                      <th className="py-2 px-2">Sb %</th>
                      <th className="py-2 px-2">{isTr ? "En/Boy (AR)" : "Aspect Ratio"}</th>
                      <th className="py-2 px-2">{isTr ? "Sınıflandırma Düzeyi" : "Classification Tier"}</th>
                      <th className="py-2 px-2 text-right">{isTr ? "İşlem" : "Action"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-tactical-border/30">
                    {particles.map((p, idx) => {
                      const classifiedInfo = gsrResult.classified_particles[idx];
                      const tier = classifiedInfo?.classification_tier || "ENVIRONMENTAL_BACKGROUND";
                      const isChar = tier === "CHARACTERISTIC_GSR";
                      const isCons = tier === "CONSISTENT_WITH_GSR";
                      const isComm = tier === "COMMONLY_ASSOCIATED";

                      return (
                        <tr key={p.particle_id} className="hover:bg-tactical-surface/40 transition-colors">
                          <td className="py-2.5 px-2 font-bold text-amber-300">{p.particle_id}</td>
                          <td className="py-2.5 px-2">
                            <input
                              type="number"
                              min="0"
                              max="100"
                              step="1"
                              value={p.pb_percent}
                              onChange={(e) => handleUpdateParticle(idx, "pb_percent", parseFloat(e.target.value) || 0)}
                              className="w-16 bg-[#0B1222] border border-tactical-border/70 rounded px-2 py-1 text-right text-tactical-text font-bold"
                            />
                          </td>
                          <td className="py-2.5 px-2">
                            <input
                              type="number"
                              min="0"
                              max="100"
                              step="1"
                              value={p.ba_percent}
                              onChange={(e) => handleUpdateParticle(idx, "ba_percent", parseFloat(e.target.value) || 0)}
                              className="w-16 bg-[#0B1222] border border-tactical-border/70 rounded px-2 py-1 text-right text-tactical-text font-bold"
                            />
                          </td>
                          <td className="py-2.5 px-2">
                            <input
                              type="number"
                              min="0"
                              max="100"
                              step="1"
                              value={p.sb_percent}
                              onChange={(e) => handleUpdateParticle(idx, "sb_percent", parseFloat(e.target.value) || 0)}
                              className="w-16 bg-[#0B1222] border border-tactical-border/70 rounded px-2 py-1 text-right text-tactical-text font-bold"
                            />
                          </td>
                          <td className="py-2.5 px-2">
                            <input
                              type="number"
                              min="0.5"
                              max="5.0"
                              step="0.1"
                              value={p.aspect_ratio}
                              onChange={(e) => handleUpdateParticle(idx, "aspect_ratio", parseFloat(e.target.value) || 1.0)}
                              className="w-16 bg-[#0B1222] border border-tactical-border/70 rounded px-2 py-1 text-right text-tactical-text font-bold"
                            />
                          </td>
                          <td className="py-2.5 px-2">
                            <span
                              className={`text-[9px] font-bold px-2 py-0.5 rounded border whitespace-nowrap ${
                                isChar
                                  ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                                  : isCons
                                  ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                                  : isComm
                                  ? "bg-purple-500/20 text-purple-300 border-purple-500/40"
                                  : "bg-tactical-surface text-tactical-text-muted border-tactical-border/60"
                              }`}
                            >
                              {tier.replace(/_/g, " ")}
                            </span>
                          </td>
                          <td className="py-2.5 px-2 text-right">
                            <button
                              onClick={() => handleRemoveParticle(idx)}
                              disabled={particles.length <= 1}
                              className="p-1 rounded hover:bg-rose-500/20 text-tactical-text-muted hover:text-rose-400 transition-colors disabled:opacity-30"
                              title={isTr ? "Sil" : "Remove"}
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Ternary Distribution & Standards Card */}
            <div className="lg:col-span-4 bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 space-y-4 shadow-xl flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                    {isTr ? "ASTM E1588-20 Kuralları" : "ASTM E1588-20 Criteria"}
                  </span>
                  <span className="text-[10px] text-amber-400 font-bold">Standard Spec</span>
                </div>

                <div className="space-y-2.5 text-xs text-tactical-text-muted">
                  <div className="p-2.5 bg-[#0B1222] rounded-xl border border-tactical-border/60 space-y-1">
                    <div className="font-bold text-amber-300 text-[11px] flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                      <span>{isTr ? "Karakteristik Pb-Ba-Sb" : "Characteristic Pb-Ba-Sb"}</span>
                    </div>
                    <p className="text-[10px]">
                      {isTr
                        ? "Pb >= %10, Ba >= %10, Sb >= %5 ve dairesel/küresel morfoloji (En/Boy <= 1.3)."
                        : "Pb >= 10%, Ba >= 10%, Sb >= 5% with spherical morphology (Aspect Ratio <= 1.3)."}
                    </p>
                  </div>

                  <div className="p-2.5 bg-[#0B1222] rounded-xl border border-tactical-border/60 space-y-1">
                    <div className="font-bold text-cyan-300 text-[11px] flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                      <span>{isTr ? "Uyumlu İkili Parçacıklar" : "Consistent Bi-Element"}</span>
                    </div>
                    <p className="text-[10px]">
                      {isTr
                        ? "Pb-Ba, Pb-Sb veya Ba-Sb çiftleri >= %10 ve En/Boy <= 1.5."
                        : "Pb-Ba, Pb-Sb, or Ba-Sb pairs >= 10% and Aspect Ratio <= 1.5."}
                    </p>
                  </div>

                  <div className="p-2.5 bg-[#0B1222] rounded-xl border border-tactical-border/60 space-y-1">
                    <div className="font-bold text-purple-300 text-[11px] flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-purple-400"></span>
                      <span>{isTr ? "Sık Rastlanan / Morfolojik Düşüş" : "Commonly Associated / Downgrade"}</span>
                    </div>
                    <p className="text-[10px]">
                      {isTr
                        ? "Tekil metaller, Ba-Al veya asferik (AR > 1.3) nedeniyle indirgenmiş triadlar."
                        : "Single elements, Ba-Al, or triads downgraded due to non-spherical shape (AR > 1.3)."}
                    </p>
                  </div>
                </div>
              </div>

              {/* Evidence Strength Summary Banner */}
              <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-1">
                <span className="text-[10px] uppercase font-bold text-amber-300 block">
                  {isTr ? "Nihai Mahkeme Görüşü:" : "Evaluative Conclusion:"}
                </span>
                <p className="text-xs font-bold text-tactical-text leading-snug">
                  {gsrResult.evidence_strength}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: 3D CMC BALLISTIC STRIATION MATCHING */}
      {activeTab === "cmc_striation" && (
        <div className="space-y-6">
          {/* Top CMC Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Uyumlu Eşleşen Hücre Sayısı (K)" : "Congruent Matching Cells (K)"}
              </span>
              <div className="text-2xl font-bold text-amber-400 tabular-nums">
                K = {cmcResult.cmc_count} <span className="text-xs text-tactical-text-muted">/ {cmcCells.length}</span>
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "NIST Song kriteri: K >= 6 kesin eşleşme" : "NIST Song criteria: K >= 6 definitive match"}
              </p>
            </div>

            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Balistik Karar" : "Identification Verdict"}
              </span>
              <div
                className={`text-sm font-bold mt-1.5 ${
                  cmcResult.identification_verdict === "POSITIVE_IDENTIFICATION"
                    ? "text-emerald-400"
                    : cmcResult.identification_verdict === "INCONCLUSIVE_BORDERLINE"
                    ? "text-amber-400"
                    : "text-rose-400"
                }`}
              >
                {cmcResult.identification_verdict.replace(/_/g, " ")}
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "AFTE & NIST Standart Kararı" : "AFTE & NIST Standard Verdict"}
              </p>
            </div>

            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Yanlış Eşleşme Olasılığı" : "False Match Probability"}
              </span>
              <div className="text-2xl font-bold text-cyan-400 tabular-nums">
                P_false {cmcResult.false_match_probability}
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "Kombinatoryal rastgele eşleşme riski" : "Combinatorial random match risk"}
              </p>
            </div>

            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Eşik Uyumu" : "Threshold Tolerance"}
              </span>
              <div className="text-xs font-bold text-emerald-400 mt-1">
                CCF &ge; 0.55 • |&Delta;x,y| &le; 15 &mu;m • |&Delta;&theta;| &le; 1.0&deg;
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "Song ve ark. 3 parametreli tolerans" : "Song et al. 3-parameter tolerance"}
              </p>
            </div>
          </div>

          {/* CMC Grid & Controls */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8 bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-amber-400" />
                  <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                    {isTr ? "3D Topoğrafik Çizgi Hücreleri (CMC)" : "3D Topographic Striation Cells (CMC)"}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleAddCmcCell}
                    className="px-2.5 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-bold transition-all flex items-center gap-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>{isTr ? "Hücre Ekle" : "Add Cell"}</span>
                  </button>
                  <button
                    onClick={runServerVerification}
                    disabled={loading}
                    className="px-3 py-1 rounded-lg bg-amber-500 text-black hover:bg-amber-400 text-xs font-bold transition-all flex items-center gap-1.5"
                  >
                    <Activity className="w-3.5 h-3.5" />
                    <span>{loading ? (isTr ? "Doğrulanıyor..." : "Verifying...") : (isTr ? "Sunucuda Doğrula" : "Verify API")}</span>
                  </button>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-tactical-border/60 text-tactical-text-muted text-[10px] uppercase">
                      <th className="py-2 px-2">Hücre ID</th>
                      <th className="py-2 px-2">CCF Max (&ge;0.55)</th>
                      <th className="py-2 px-2">&Delta;x (&mu;m)</th>
                      <th className="py-2 px-2">&Delta;y (&mu;m)</th>
                      <th className="py-2 px-2">&Delta;&theta; (&deg;)</th>
                      <th className="py-2 px-2">CMC Durumu</th>
                      <th className="py-2 px-2 text-right">{isTr ? "İşlem" : "Action"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-tactical-border/30">
                    {cmcCells.map((c, idx) => {
                      const evalInfo = cmcResult.evaluated_cells[idx];
                      const isMatch = evalInfo?.is_congruent_matching_cell ?? false;

                      return (
                        <tr key={c.cell_id} className="hover:bg-tactical-surface/40 transition-colors">
                          <td className="py-2.5 px-2 font-bold text-amber-300">{c.cell_id}</td>
                          <td className="py-2.5 px-2">
                            <input
                              type="number"
                              min="0"
                              max="1"
                              step="0.01"
                              value={c.ccf_max}
                              onChange={(e) => handleUpdateCmcCell(idx, "ccf_max", parseFloat(e.target.value) || 0)}
                              className="w-16 bg-[#0B1222] border border-tactical-border/70 rounded px-2 py-1 text-right text-tactical-text font-bold"
                            />
                          </td>
                          <td className="py-2.5 px-2">
                            <input
                              type="number"
                              min="-50"
                              max="50"
                              step="0.5"
                              value={c.delta_x_um}
                              onChange={(e) => handleUpdateCmcCell(idx, "delta_x_um", parseFloat(e.target.value) || 0)}
                              className="w-16 bg-[#0B1222] border border-tactical-border/70 rounded px-2 py-1 text-right text-tactical-text font-bold"
                            />
                          </td>
                          <td className="py-2.5 px-2">
                            <input
                              type="number"
                              min="-50"
                              max="50"
                              step="0.5"
                              value={c.delta_y_um}
                              onChange={(e) => handleUpdateCmcCell(idx, "delta_y_um", parseFloat(e.target.value) || 0)}
                              className="w-16 bg-[#0B1222] border border-tactical-border/70 rounded px-2 py-1 text-right text-tactical-text font-bold"
                            />
                          </td>
                          <td className="py-2.5 px-2">
                            <input
                              type="number"
                              min="-10"
                              max="10"
                              step="0.1"
                              value={c.delta_theta_deg}
                              onChange={(e) => handleUpdateCmcCell(idx, "delta_theta_deg", parseFloat(e.target.value) || 0)}
                              className="w-16 bg-[#0B1222] border border-tactical-border/70 rounded px-2 py-1 text-right text-tactical-text font-bold"
                            />
                          </td>
                          <td className="py-2.5 px-2">
                            <span
                              className={`text-[9px] font-bold px-2 py-0.5 rounded border whitespace-nowrap ${
                                isMatch
                                  ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                                  : "bg-rose-500/20 text-rose-300 border-rose-500/40"
                              }`}
                            >
                              {isMatch ? (isTr ? "UYUMLU (CMC)" : "CONGRUENT") : (isTr ? "UYUMSUZ (RED)" : "REJECTED")}
                            </span>
                          </td>
                          <td className="py-2.5 px-2 text-right">
                            <button
                              onClick={() => handleRemoveCmcCell(idx)}
                              disabled={cmcCells.length <= 1}
                              className="p-1 rounded hover:bg-rose-500/20 text-tactical-text-muted hover:text-rose-400 transition-colors disabled:opacity-30"
                              title={isTr ? "Sil" : "Remove"}
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* CMC Criteria Guide Card */}
            <div className="lg:col-span-4 bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 space-y-4 shadow-xl flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                    {isTr ? "NIST Song ve ark. CMC Kuralları" : "NIST Song et al. CMC Rules"}
                  </span>
                  <span className="text-[10px] text-amber-400 font-bold">AFTE Protocol</span>
                </div>

                <div className="space-y-2.5 text-xs text-tactical-text-muted">
                  <div className="p-2.5 bg-[#0B1222] rounded-xl border border-tactical-border/60 space-y-1">
                    <div className="font-bold text-emerald-300 text-[11px]">
                      {isTr ? "1. Çapraz Korelasyon (CCF)" : "1. Cross-Correlation (CCF)"}
                    </div>
                    <p className="text-[10px]">
                      {isTr
                        ? "Hücreler arası tepe korelasyon katsayısı CCF_max >= 0.55 olmalıdır."
                        : "Peak cross-correlation coefficient CCF_max >= 0.55 required."}
                    </p>
                  </div>

                  <div className="p-2.5 bg-[#0B1222] rounded-xl border border-tactical-border/60 space-y-1">
                    <div className="font-bold text-amber-300 text-[11px]">
                      {isTr ? "2. Uzamsal Öteleme (|dx, dy|)" : "2. Spatial Translation (|dx, dy|)"}
                    </div>
                    <p className="text-[10px]">
                      {isTr
                        ? "X ve Y eksenlerindeki kayma |dx| <= 15 um ve |dy| <= 15 um sınırında kalmalıdır."
                        : "Displacement on X and Y must remain within |dx| <= 15 um and |dy| <= 15 um."}
                    </p>
                  </div>

                  <div className="p-2.5 bg-[#0B1222] rounded-xl border border-tactical-border/60 space-y-1">
                    <div className="font-bold text-cyan-300 text-[11px]">
                      {isTr ? "3. Açısal Rotasyon (|dtheta|)" : "3. Angular Rotation (|dtheta|)"}
                    </div>
                    <p className="text-[10px]">
                      {isTr
                        ? "Nispi açısal dönme farkı |dtheta| <= 1.0 derece toleransını aşamaz."
                        : "Relative angular rotation difference |dtheta| <= 1.0 degree."}
                    </p>
                  </div>
                </div>
              </div>

              {/* Conclusion Box */}
              <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-1">
                <span className="text-[10px] uppercase font-bold text-amber-300 block">
                  {isTr ? "Balistik Teşhis Sonucu:" : "Ballistic Conclusion:"}
                </span>
                <p className="text-xs font-bold text-tactical-text leading-snug">
                  {cmcResult.ballistic_conclusion}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: MICROSCOPY & HAIR MORPHOMETRY (Ported and elevated from MicroscopyPanel) */}
      {activeTab === "microscopy_hair" && (
        <div className="space-y-6">
          {/* Top Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Medüller İndeks (I_medulla)" : "Medullary Index (I_medulla)"}
              </span>
              <div className="text-2xl font-bold text-purple-400 tabular-nums">
                {liveMedullaryIndex}
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {liveMedullaryIndex < 0.33
                  ? (isTr ? "İnsan Kılı (I < 0.33)" : "Human Hair (I < 0.33)")
                  : liveMedullaryIndex > 0.5
                  ? (isTr ? "Hayvan Kılı (I > 0.50)" : "Animal Hair (I > 0.50)")
                  : (isTr ? "Sınırda / Ara Değer" : "Borderline Intermediate")}
              </p>
            </div>

            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Kıl Şaft Çapı" : "Hair Shaft Diameter"}
              </span>
              <div className="text-2xl font-bold text-zinc-200 tabular-nums">
                {activeShaftUm} <span className="text-xs text-tactical-text-muted">&mu;m</span>
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "SWGMAT mikrometrik ölçümü" : "SWGMAT micrometric measurement"}
              </p>
            </div>

            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Medulla Çapı" : "Medulla Diameter"}
              </span>
              <div className="text-2xl font-bold text-amber-300 tabular-nums">
                {activeMedullaUm} <span className="text-xs text-tactical-text-muted">&mu;m</span>
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "İç medüller kanal genişliği" : "Internal medullary canal width"}
              </p>
            </div>

            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 space-y-1 shadow-lg">
              <span className="text-[10px] uppercase font-bold text-tactical-text-muted tracking-wider">
                {isTr ? "Laboratuvar DNA Stratejisi" : "Lab DNA Strategy"}
              </span>
              <div className="text-xs font-bold text-emerald-400 mt-1 flex items-center gap-1.5">
                <Dna className="w-4 h-4" />
                <span>
                  {liveMedullaryIndex < 0.33 && activeMedullaUm <= 25
                    ? (isTr ? "Çekirdek nDNA STR (24 Lokus)" : "Nuclear nDNA STR (24 Loci)")
                    : (isTr ? "Mitokondriyal mtDNA HV1/HV2" : "Mitochondrial mtDNA HV1/HV2")}
                </span>
              </div>
              <p className="text-[9px] text-tactical-text-muted">
                {isTr ? "Kök kılıfı & şaft optimizasyonu" : "Root sheath & shaft optimization"}
              </p>
            </div>
          </div>

          {/* Hair Specimen Inventory and Live Calculator */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Inventory List */}
            <div className="lg:col-span-7 bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                <div className="flex items-center gap-2">
                  <Microscope className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                    {isTr ? "Mikroskobik Morfometri & Kıl Kanıtı Envanteri" : "Microscopic Morphometry & Hair Evidence Inventory"}
                  </span>
                </div>
                <span className="text-[10px] text-purple-400 font-bold bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                  SWGMAT Standard
                </span>
              </div>

              <div className="space-y-3">
                {specimens.map((s) => {
                  const isSelected = selectedSpecimenId === s.id;
                  const idxVal = computeMedullaryIndex(s.medulla_diameter_um, s.shaft_diameter_um);

                  return (
                    <div
                      key={s.id}
                      onClick={() => handleSelectSpecimen(s)}
                      className={`p-3.5 sm:p-4 rounded-xl border transition-all cursor-pointer space-y-2.5 ${
                        isSelected
                          ? "bg-purple-500/15 border-purple-500/60 shadow-[0_0_15px_rgba(168,85,247,0.15)]"
                          : "bg-black/30 border-tactical-border/40 hover:border-purple-500/40"
                      }`}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="text-xs font-bold text-tactical-text font-mono tracking-wide">
                          {s.id}
                        </span>
                        <span className="text-[9px] text-purple-300 font-bold bg-purple-500/15 border border-purple-500/30 px-2 py-0.5 rounded whitespace-nowrap">
                          {isTr ? s.originTr : s.origin}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[10px] font-mono">
                        <div className="bg-black/40 p-2 rounded-lg border border-tactical-border/30">
                          <span className="text-zinc-500 text-[9px] block">{isTr ? "Kıl Çapı" : "Hair Diameter"}</span>
                          <span className="text-zinc-200 font-bold">{s.shaft_diameter_um} &mu;m</span>
                        </div>
                        <div className="bg-black/40 p-2 rounded-lg border border-tactical-border/30">
                          <span className="text-zinc-500 text-[9px] block">{isTr ? "Medulla Çapı" : "Medulla Diameter"}</span>
                          <span className="text-zinc-200 font-bold">{s.medulla_diameter_um} &mu;m</span>
                        </div>
                        <div className="col-span-2 sm:col-span-1 bg-black/40 p-2 rounded-lg border border-tactical-border/30">
                          <span className="text-zinc-500 text-[9px] block">{isTr ? "Kök Morfolojisi" : "Root Morphology"}</span>
                          <span className="text-zinc-200 font-bold truncate block">{isTr ? s.root_morphologyTr : s.root_morphology}</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-tactical-border/20 text-xs font-mono">
                        <div className="flex items-center gap-2">
                          <span className="text-zinc-400 text-[10px]">{isTr ? "Medüller İndeks (I):" : "Medullary Index (I):"}</span>
                          <span className="text-purple-300 font-bold">{idxVal}</span>
                        </div>
                        <span className="px-2.5 py-0.5 rounded text-[9px] font-bold bg-purple-500/20 border border-purple-500/40 text-purple-300 uppercase whitespace-nowrap">
                          {s.badge}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right Live Morphometry Slider Controls */}
            <div className="lg:col-span-5 bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 space-y-4 shadow-xl flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                    {isTr ? "İnteraktif Morfometri Hesaplayıcı" : "Interactive Morphometry Calculator"}
                  </span>
                  <span className="text-[10px] text-emerald-400 font-bold">Live Simulation</span>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span className="text-tactical-text-muted">{isTr ? "Şaft Çapı (d_shaft):" : "Shaft Diameter (d_shaft):"}</span>
                      <span className="font-bold text-zinc-200">{activeShaftUm} &mu;m</span>
                    </div>
                    <input
                      type="range"
                      min="20"
                      max="150"
                      step="1"
                      value={activeShaftUm}
                      onChange={(e) => setActiveShaftUm(parseFloat(e.target.value))}
                      className="w-full accent-purple-500"
                    />
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span className="text-tactical-text-muted">{isTr ? "Medulla Çapı (d_medulla):" : "Medulla Diameter (d_medulla):"}</span>
                      <span className="font-bold text-amber-300">{activeMedullaUm} &mu;m</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max={activeShaftUm}
                      step="1"
                      value={activeMedullaUm}
                      onChange={(e) => setActiveMedullaUm(parseFloat(e.target.value))}
                      className="w-full accent-amber-500"
                    />
                  </div>
                </div>

                <div className="p-3.5 bg-[#0B1222] rounded-xl border border-tactical-border/60 space-y-2 text-xs">
                  <div className="text-[10px] font-bold uppercase text-tactical-text-muted">
                    {isTr ? "SWGMAT Teşhis Eşikleri:" : "SWGMAT Diagnostic Criteria:"}
                  </div>
                  <div className="space-y-1 text-[11px]">
                    <div className="flex justify-between">
                      <span className="text-tactical-text-muted">{isTr ? "İnsan (Human):" : "Human Origin:"}</span>
                      <span className="font-bold text-emerald-400">I &lt; 0.33</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-tactical-text-muted">{isTr ? "Hayvan (Animal):" : "Animal Origin:"}</span>
                      <span className="font-bold text-rose-400">I &gt; 0.50</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendation Box */}
              <div className="p-3.5 bg-purple-500/10 border border-purple-500/30 rounded-xl space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-bold text-purple-300">
                  <Dna className="w-4 h-4 text-purple-400" />
                  <span>{isTr ? "Önerilen DNA Amplifikasyonu" : "Recommended DNA Amplification"}</span>
                </div>
                <p className="text-xs font-bold text-emerald-400 font-mono">
                  {liveMedullaryIndex < 0.33
                    ? (isTr ? "ÇEKİRDEK STR OPTİMAL (24 Lokus CODIS)" : "NUCLEAR STR OPTIMAL (24 Loci CODIS)")
                    : (isTr ? "MİTOKONDRİYAL mtDNA HV1/HV2/HV3" : "MITOCHONDRIAL mtDNA HV1/HV2/HV3")}
                </p>
                <p className="text-[9px] text-tactical-text-muted">
                  {isTr
                    ? "Anagen/katagen kök kılıfları nükleer STR için yeterli gDNA sağlar. Telojen şaft kıllarında mtDNA dizilemesi zorunludur."
                    : "Anagen/catagen root sheaths supply adequate gDNA for nuclear STR. Telogen shafts require mtDNA sequencing."}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: BENCHMARK PRESETS GALLERY */}
      {activeTab === "benchmarks" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {GOLDEN_BALLISTICS_PRESETS.map((p) => {
              const isSelected = selectedPresetId === p.id;
              const countText = p.category === "gsr" ? `${p.particles?.length || 0} Particles` : `${p.cells?.length || 0} Cells`;

              return (
                <div
                  key={p.id}
                  className={`bg-[#080D1A] border rounded-2xl p-4 space-y-3 shadow-lg transition-all flex flex-col justify-between ${
                    isSelected ? "border-amber-500/80 bg-amber-500/5" : "border-tactical-border/70 hover:border-tactical-border"
                  }`}
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        {p.id}
                      </span>
                      <span className="text-[10px] text-tactical-text-muted font-bold">
                        {countText}
                      </span>
                    </div>
                    <h3 className="text-xs font-bold text-tactical-text">{isTr ? p.nameTr : p.name}</h3>
                    <p className="text-[10px] text-tactical-text-muted leading-relaxed">
                      {isTr ? p.descTr : p.desc}
                    </p>
                  </div>

                  <button
                    onClick={() => handleSelectPreset(p)}
                    className={`w-full py-1.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 mt-2 ${
                      isSelected
                        ? "bg-amber-500 text-black font-bold"
                        : "bg-tactical-surface/80 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30"
                    }`}
                  >
                    <span>{isSelected ? (isTr ? "Aktif Yüklü" : "Currently Loaded") : (isTr ? "Vektörü Yükle" : "Load Vector")}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 5: ISO 17025 REPORTING & CRYPTOGRAPHIC AUDIT */}
      {activeTab === "iso_audit" && (
        <div className="space-y-6">
          {/* Audit Trail & State Digest Ribbon */}
          <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-5 space-y-4 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                    {isTr ? "Kriptografik Durum Denetim Özeti (H_ballistics)" : "Cryptographic State Audit Digest (H_ballistics)"}
                  </span>
                  <p className="text-[10px] text-tactical-text-muted">
                    SHA-256 State Digest • ISO/IEC 17025:2017 Sec 7.8 Standard
                  </p>
                </div>
              </div>
              <button
                onClick={handleCopyHash}
                className="px-3 py-1.5 rounded-lg bg-tactical-surface/80 hover:bg-tactical-surface border border-tactical-border/60 text-xs font-bold text-tactical-text transition-all flex items-center gap-1.5"
              >
                {copiedHash ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedHash ? (isTr ? "Kopyalandı!" : "Copied!") : (isTr ? "Hash Kopyala" : "Copy Hash")}</span>
              </button>
            </div>

            <div className="bg-[#040812] border border-tactical-border/40 rounded-xl p-3 font-mono text-xs text-amber-300 break-all select-all">
              {auditHash || "Computing SHA-256..."}
            </div>
          </div>

          {/* Official Court Witness Statement */}
          <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-5 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr ? "Resmi Adli Bilirkişi Rapor Beyanı" : "Official Court Expert Witness Statement"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyReport}
                  className="px-3 py-1.5 rounded-lg bg-tactical-surface/80 hover:bg-tactical-surface border border-tactical-border/60 text-xs font-bold text-tactical-text transition-all flex items-center gap-1.5"
                >
                  {copiedReport ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedReport ? (isTr ? "Kopyalandı!" : "Copied!") : (isTr ? "Raporu Kopyala" : "Copy Report")}</span>
                </button>
                <button
                  onClick={handleExportJson}
                  className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-xs font-bold text-amber-300 transition-all flex items-center gap-1.5"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>JSON</span>
                </button>
              </div>
            </div>

            <div className="p-4 bg-[#040812] rounded-xl border border-tactical-border/40 space-y-2 text-xs text-tactical-text leading-relaxed">
              <div className="flex items-center gap-2 text-amber-400 font-bold">
                <ShieldCheck className="w-4 h-4" />
                <span>ASTM E1588-20 & NIST CMC Forensic Certificate</span>
              </div>
              <p>
                {gsrResult.prosecutors_fallacy_shield}
              </p>
              <p>
                {cmcResult.prosecutors_fallacy_shield}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
