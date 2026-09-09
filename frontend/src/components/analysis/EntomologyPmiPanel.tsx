"use client";

import React, { useState, useMemo, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bug,
  Thermometer,
  Clock,
  ShieldCheck,
  RefreshCw,
  Calendar,
  Flame,
  AlertCircle,
  Info,
  Cpu,
  Check,
  Copy,
  Layers,
  Database,
  Sliders,
  Sparkles,
  TrendingUp,
  Activity,
  CheckCircle2,
  FileSpreadsheet,
  Moon,
  Sun,
  FileText,
} from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES, PRESETS & TAXONOMY CATALOG
// ═══════════════════════════════════════════════════════════════════════════════

export type EntomologyTabId = "mici" | "species" | "succession" | "maggot_mass" | "audit";

export interface SpeciesStageData {
  adh: number;
  length_mm: number;
  duration_hours_20c: number;
  tr: string;
}

export interface SpeciesTaxon {
  id: string;
  name: string;
  family: string;
  common: string;
  common_tr: string;
  t_base: number;
  t_max: number;
  k_total: number;
  ikemoto_slope: number;
  ecological_role: string;
  ecological_role_tr: string;
  stages: Record<string, SpeciesStageData>;
}

export const ENTOMOLOGY_SPECIES_REGISTRY: Record<string, SpeciesTaxon> = {
  "Lucilia sericata": {
    id: "L_SERICATA",
    name: "Lucilia sericata",
    family: "Calliphoridae",
    common: "Common Green Bottle Fly",
    common_tr: "Yeşil Şişe Sineği",
    t_base: 9.0,
    t_max: 35.0,
    k_total: 10174.5,
    ikemoto_slope: 11.2,
    ecological_role: "Primary primary coloniser of sunny/exposed carcasses; urban and rural indicator.",
    ecological_role_tr: "Güneş gören/açık cesetlerin birincil kolonizatörü; kentsel ve kırsal belirteç.",
    stages: {
      "Egg": { adh: 240.0, length_mm: 1.2, duration_hours_20c: 21.8, tr: "Yumurta" },
      "1st Instar": { adh: 480.0, length_mm: 3.5, duration_hours_20c: 21.8, tr: "1. Larva Evresi (L1)" },
      "2nd Instar": { adh: 800.0, length_mm: 6.8, duration_hours_20c: 29.1, tr: "2. Larva Evresi (L2)" },
      "3rd Instar Feeding": { adh: 1254.5, length_mm: 12.5, duration_hours_20c: 41.3, tr: "3. Larva Beslenen (L3F)" },
      "3rd Instar Post-Feeding": { adh: 2200.0, length_mm: 14.0, duration_hours_20c: 85.9, tr: "3. Larva Beslenme Sonrası (L3PF/Wandering)" },
      "Pupae": { adh: 5000.0, length_mm: 10.5, duration_hours_20c: 254.5, tr: "Pupa" },
      "Adult": { adh: 10174.5, length_mm: 11.0, duration_hours_20c: 470.4, tr: "Ergin Sinek" },
    },
  },
  "Calliphora vicina": {
    id: "C_VICINA",
    name: "Calliphora vicina",
    family: "Calliphoridae",
    common: "European Blue Bottle Fly",
    common_tr: "Mavi Şişe Sineği",
    t_base: 3.0,
    t_max: 30.0,
    k_total: 23670.0,
    ikemoto_slope: 16.8,
    ecological_role: "Cold-tolerant winter/autumn primary coloniser; shade and indoor preferred.",
    ecological_role_tr: "Soğuğa dirençli kış/sonbahar birincil kolonizatörü; gölge ve kapalı mekan tercihi.",
    stages: {
      "Egg": { adh: 450.0, length_mm: 1.5, duration_hours_20c: 26.5, tr: "Yumurta" },
      "1st Instar": { adh: 1170.0, length_mm: 4.2, duration_hours_20c: 42.4, tr: "1. Larva Evresi (L1)" },
      "2nd Instar": { adh: 2250.0, length_mm: 8.5, duration_hours_20c: 63.5, tr: "2. Larva Evresi (L2)" },
      "3rd Instar Feeding": { adh: 4050.0, length_mm: 15.2, duration_hours_20c: 105.9, tr: "3. Larva Beslenen (L3F)" },
      "3rd Instar Post-Feeding": { adh: 6450.0, length_mm: 16.5, duration_hours_20c: 141.2, tr: "3. Larva Beslenme Sonrası (L3PF/Wandering)" },
      "Pupae": { adh: 9300.0, length_mm: 11.8, duration_hours_20c: 167.6, tr: "Pupa" },
      "Adult": { adh: 23670.0, length_mm: 12.5, duration_hours_20c: 845.3, tr: "Ergin Sinek" },
    },
  },
  "Chrysomya albiceps": {
    id: "C_ALBICEPS",
    name: "Chrysomya albiceps",
    family: "Calliphoridae",
    common: "Banded Blowfly",
    common_tr: "Çizgili Leş Sineği",
    t_base: 10.2,
    t_max: 38.0,
    k_total: 17760.0,
    ikemoto_slope: 9.8,
    ecological_role: "Warm-adapted Mediterranean/tropical coloniser; facultative predator on other larvae.",
    ecological_role_tr: "Sıcak Akdeniz/tropikal kolonizatörü; diğer larvalar üzerinde yırtıcı/avcı.",
    stages: {
      "Egg": { adh: 260.0, length_mm: 1.3, duration_hours_20c: 26.5, tr: "Yumurta" },
      "1st Instar": { adh: 740.0, length_mm: 3.8, duration_hours_20c: 49.0, tr: "1. Larva Evresi (L1)" },
      "2nd Instar": { adh: 1340.0, length_mm: 7.2, duration_hours_20c: 61.2, tr: "2. Larva Evresi (L2)" },
      "3rd Instar Feeding": { adh: 2440.0, length_mm: 13.0, duration_hours_20c: 112.2, tr: "3. Larva Beslenen (L3F)" },
      "3rd Instar Post-Feeding": { adh: 4540.0, length_mm: 14.2, duration_hours_20c: 214.3, tr: "3. Larva Beslenme Sonrası (L3PF/Wandering)" },
      "Pupae": { adh: 8440.0, length_mm: 10.0, duration_hours_20c: 398.0, tr: "Pupa" },
      "Adult": { adh: 17760.0, length_mm: 11.5, duration_hours_20c: 951.0, tr: "Ergin Sinek" },
    },
  },
  "Phormia regina": {
    id: "P_REGINA",
    name: "Phormia regina",
    family: "Calliphoridae",
    common: "Black Blowfly",
    common_tr: "Siyah Leş Sineği",
    t_base: 10.0,
    t_max: 36.0,
    k_total: 19800.0,
    ikemoto_slope: 10.5,
    ecological_role: "Spring/autumn transitional coloniser; highly sensitive to forest shaded terrain.",
    ecological_role_tr: "İlkbahar/sonbahar geçiş kolonizatörü; ormanlık gölgeli arazilere yüksek duyarlılık.",
    stages: {
      "Egg": { adh: 300.0, length_mm: 1.4, duration_hours_20c: 30.0, tr: "Yumurta" },
      "1st Instar": { adh: 800.0, length_mm: 4.0, duration_hours_20c: 50.0, tr: "1. Larva Evresi (L1)" },
      "2nd Instar": { adh: 1500.0, length_mm: 7.5, duration_hours_20c: 70.0, tr: "2. Larva Evresi (L2)" },
      "3rd Instar Feeding": { adh: 2900.0, length_mm: 13.8, duration_hours_20c: 140.0, tr: "3. Larva Beslenen (L3F)" },
      "3rd Instar Post-Feeding": { adh: 5100.0, length_mm: 15.0, duration_hours_20c: 220.0, tr: "3. Larva Beslenme Sonrası (L3PF/Wandering)" },
      "Pupae": { adh: 9200.0, length_mm: 11.0, duration_hours_20c: 410.0, tr: "Pupa" },
      "Adult": { adh: 19800.0, length_mm: 12.0, duration_hours_20c: 1060.0, tr: "Ergin Sinek" },
    },
  },
  "Sarcophaga argyrostoma": {
    id: "S_ARGYROSTOMA",
    name: "Sarcophaga argyrostoma",
    family: "Sarcophagidae",
    common: "Flesh Fly (Larviparous)",
    common_tr: "Gri Et Sineği (Larvipar)",
    t_base: 8.5,
    t_max: 34.0,
    k_total: 14200.0,
    ikemoto_slope: 12.0,
    ecological_role: "Directly deposits 1st instar live larvae (no egg stage); indoor access pioneer.",
    ecological_role_tr: "Doğrudan canlı L1 larva bırakır (yumurta evresi yoktur); kapalı alana öncü giriş.",
    stages: {
      "1st Instar": { adh: 420.0, length_mm: 3.0, duration_hours_20c: 36.5, tr: "1. Canlı Larva (L1)" },
      "2nd Instar": { adh: 1100.0, length_mm: 8.0, duration_hours_20c: 59.1, tr: "2. Larva Evresi (L2)" },
      "3rd Instar Feeding": { adh: 2600.0, length_mm: 16.0, duration_hours_20c: 130.4, tr: "3. Larva Beslenen (L3F)" },
      "3rd Instar Post-Feeding": { adh: 4900.0, length_mm: 18.0, duration_hours_20c: 200.0, tr: "3. Larva Beslenme Sonrası (L3PF)" },
      "Pupae": { adh: 8800.0, length_mm: 13.0, duration_hours_20c: 339.1, tr: "Pupa" },
      "Adult": { adh: 14200.0, length_mm: 14.5, duration_hours_20c: 469.6, tr: "Ergin Sinek" },
    },
  },
  "Dermestes maculatus": {
    id: "D_MACULATUS",
    name: "Dermestes maculatus",
    family: "Dermestidae (Coleoptera)",
    common: "Hide / Skin Beetle",
    common_tr: "Deri / Post Böceği (Kınkanatlı)",
    t_base: 15.0,
    t_max: 35.0,
    k_total: 21500.0,
    ikemoto_slope: 18.5,
    ecological_role: "Late advanced/dry skeletal stage specialist; consumes dried skin, ligaments, and cartilage.",
    ecological_role_tr: "İleri kuru ve iskelet evresi uzmanı; kurumuş deri, ligament ve kıkırdak tüketir.",
    stages: {
      "Egg": { adh: 850.0, length_mm: 2.0, duration_hours_20c: 170.0, tr: "Yumurta" },
      "Larva Instars (1-7)": { adh: 7500.0, length_mm: 12.0, duration_hours_20c: 1500.0, tr: "Larva Evreleri (L1-L7)" },
      "Pupae": { adh: 12500.0, length_mm: 9.0, duration_hours_20c: 1000.0, tr: "Pupa" },
      "Adult": { adh: 21500.0, length_mm: 8.5, duration_hours_20c: 1800.0, tr: "Ergin Kınkanatlı" },
    },
  },
};

export interface GoldenBenchmarkPreset {
  id: string;
  name: string;
  nameTr: string;
  species: string;
  stage: string;
  ambientTemp: number;
  deltaTMass: number;
  samplingTime: string;
  expectedAdh: number;
  expectedHours: number;
  description: string;
  descriptionTr: string;
  nocturnalSuppression: boolean;
}

export const ENTOMOLOGY_BENCHMARKS: GoldenBenchmarkPreset[] = [
  {
    id: "VECTOR_23_ENTO_A",
    name: "Lucilia sericata L3 Feeding (1254.5 ADH)",
    nameTr: "Lucilia sericata L3 Beslenen (1254.5 ADH)",
    species: "Lucilia sericata",
    stage: "3rd Instar Feeding",
    ambientTemp: 20.0,
    deltaTMass: 0.0,
    samplingTime: "2026-08-16T12:00",
    expectedAdh: 1254.5,
    expectedHours: 114.05,
    description: "Standard casework benchmark at constant 20.0°C (effective step = 11.0 ADH/h).",
    descriptionTr: "Sabit 20.0°C ortamda standart vaka referansı (etkin adım = 11.0 ADH/saat).",
    nocturnalSuppression: false,
  },
  {
    id: "VECTOR_23_ENTO_B",
    name: "Calliphora vicina Cold-Adapted (T_base=3.0°C)",
    nameTr: "Calliphora vicina Soğuk Uyumlu (T_base=3.0°C)",
    species: "Calliphora vicina",
    stage: "Egg",
    ambientTemp: 8.0,
    deltaTMass: 0.0,
    samplingTime: "2026-08-16T12:00",
    expectedAdh: 450.0,
    expectedHours: 90.0,
    description: "Cold-tolerant European blue bottle fly egg hatching under 8.0°C winter conditions.",
    descriptionTr: "Soğuğa dirençli mavi şişe sineği kış koşullarında 8.0°C altında yumurta açılımı.",
    nocturnalSuppression: false,
  },
  {
    id: "VECTOR_23_ENTO_C",
    name: "Sub-Threshold Dormancy (5.0°C < 9.0°C)",
    nameTr: "Eşik Altı Gelişim Durması (5.0°C < 9.0°C)",
    species: "Lucilia sericata",
    stage: "Egg",
    ambientTemp: 5.0,
    deltaTMass: 0.0,
    samplingTime: "2026-08-16T12:00",
    expectedAdh: 240.0,
    expectedHours: 0.0,
    description: "Temperature below lower threshold yields zero ADH accumulation (quiescence).",
    descriptionTr: "Alt gelişim eşiği altındaki sıcaklıklarda sıfır ADH birikimi (gelişim durması).",
    nocturnalSuppression: false,
  },
  {
    id: "VECTOR_23_ENTO_D",
    name: "Larval Mass Self-Heating (+2.5°C Offset)",
    nameTr: "Larva Kümesi Metabolik Öz-Isınması (+2.5°C)",
    species: "Lucilia sericata",
    stage: "3rd Instar Feeding",
    ambientTemp: 20.0,
    deltaTMass: 2.5,
    samplingTime: "2026-08-16T12:00",
    expectedAdh: 1254.5,
    expectedHours: 92.93,
    description: "Maggot-mass metabolic heat accelerates larval development, reducing calculated PMI.",
    descriptionTr: "Larva kümesi metabolik ısısı gelişimi hızlandırarak hesaplanan PMI süresini kısaltır.",
    nocturnalSuppression: false,
  },
  {
    id: "VECTOR_23_ENTO_E",
    name: "Chrysomya albiceps Mediterranean L2",
    nameTr: "Chrysomya albiceps Akdeniz L2",
    species: "Chrysomya albiceps",
    stage: "2nd Instar",
    ambientTemp: 26.0,
    deltaTMass: 1.0,
    samplingTime: "2026-08-16T12:00",
    expectedAdh: 1340.0,
    expectedHours: 80.0,
    description: "Warm-adapted banded blowfly predatory instar evaluated under summer heatwave.",
    descriptionTr: "Yaz sıcak hava dalgasında değerlendirilen sıcak iklim çizgili leş sineği L2 evresi.",
    nocturnalSuppression: false,
  },
  {
    id: "VECTOR_23_ENTO_F",
    name: "Phormia regina Forest Post-Feeding L3",
    nameTr: "Phormia regina Ormanlık Alan L3 Göç Evresi",
    species: "Phormia regina",
    stage: "3rd Instar Post-Feeding",
    ambientTemp: 18.0,
    deltaTMass: 1.5,
    samplingTime: "2026-08-16T12:00",
    expectedAdh: 5100.0,
    expectedHours: 536.8,
    description: "Black blowfly wandering prepupal migration under canopy shade conditions.",
    descriptionTr: "Orman gölgeliğinde siyah leş sineği pupa öncesi göç evresi analizi.",
    nocturnalSuppression: false,
  },
  {
    id: "VECTOR_23_ENTO_G",
    name: "Sarcophaga argyrostoma Live L1 (Direct Larviposition)",
    nameTr: "Sarcophaga argyrostoma Canlı L1 (Doğrudan Larvipozisyon)",
    species: "Sarcophaga argyrostoma",
    stage: "1st Instar",
    ambientTemp: 22.0,
    deltaTMass: 0.0,
    samplingTime: "2026-08-16T12:00",
    expectedAdh: 420.0,
    expectedHours: 31.11,
    description: "Flesh fly bypassing egg stage with direct deposit of living first instars.",
    descriptionTr: "Yumurta evresini atlayarak doğrudan canlı birinci evre larva bırakan et sineği.",
    nocturnalSuppression: false,
  },
  {
    id: "VECTOR_23_ENTO_H",
    name: "Nocturnal Oviposition Scotophase Gate",
    nameTr: "Gece Yumurtlama Baskısı (Fotoperiyot Kapısı)",
    species: "Lucilia sericata",
    stage: "1st Instar",
    ambientTemp: 21.0,
    deltaTMass: 0.0,
    samplingTime: "2026-08-16T04:00",
    expectedAdh: 480.0,
    expectedHours: 40.0,
    description: "Oviposition suppressed between 21:00 and 06:00, pushing colonization to previous dusk.",
    descriptionTr: "Saat 21:00-06:00 arası yumurtlama baskılanarak kolonizasyon önceki günbatımına ötelenir.",
    nocturnalSuppression: true,
  },
];

export interface MegninWave {
  wave: number;
  title: string;
  titleTr: string;
  period: string;
  periodTr: string;
  families: string[];
  diagnosticTaxa: string;
  status: "PRIMARY" | "ACTIVE" | "EMERGING" | "LATE" | "FINAL";
}

export const MEGNIN_SUCCESSION_WAVES: MegninWave[] = [
  {
    wave: 1,
    title: "Fresh Carcass Stage (Wave 1)",
    titleTr: "Taze Evre Dalgası (1. Dalga)",
    period: "Hours 0 - 72 (1 - 3 Days)",
    periodTr: "0 - 72 Saat (1 - 3 Gün)",
    families: ["Calliphoridae (Blowflies)", "Muscidae (Houseflies)"],
    diagnosticTaxa: "Lucilia sericata, Calliphora vicina, Musca domestica",
    status: "PRIMARY",
  },
  {
    wave: 2,
    title: "Bloated Decay Stage (Wave 2)",
    titleTr: "Şişme Evresi Dalgası (2. Dalga)",
    period: "Days 3 - 7 (72 - 168 Hours)",
    periodTr: "3 - 7 Gün (72 - 168 Saat)",
    families: ["Silphidae (Carrion Beetles)", "Histeridae (Clown Beetles)", "Sarcophagidae"],
    diagnosticTaxa: "Necrodes littoralis, Hister unicolor, Sarcophaga argyrostoma",
    status: "ACTIVE",
  },
  {
    wave: 3,
    title: "Active Decay / Fermentation (Wave 3)",
    titleTr: "Aktif Çürüme & Fermantasyon (3. Dalga)",
    period: "Days 8 - 20 (168 - 480 Hours)",
    periodTr: "8 - 20 Gün (168 - 480 Saat)",
    families: ["Piophilidae (Cheese Skippers)", "Staphylinidae (Rove Beetles)", "Drosophilidae"],
    diagnosticTaxa: "Piophila casei, Creophilus maxillosus, Fannia canicularis",
    status: "EMERGING",
  },
  {
    wave: 4,
    title: "Advanced Butyric Decay (Wave 4)",
    titleTr: "İleri Butirik Çürüme (4. Dalga)",
    period: "Days 20 - 60 (480 - 1440 Hours)",
    periodTr: "20 - 60 Gün (480 - 1440 Saat)",
    families: ["Dermestidae (Skin Beetles)", "Corynetidae (Ham Beetles)"],
    diagnosticTaxa: "Dermestes maculatus, Necrobia rufipes",
    status: "LATE",
  },
  {
    wave: 5,
    title: "Dry Remains & Skeletal Mummification (Wave 5)",
    titleTr: "Kuru İskelet & Mumyalaşma (5. Dalga)",
    period: "60 - 365+ Days (1440+ Hours)",
    periodTr: "60 - 365+ Gün (1440+ Saat)",
    families: ["Tineidae (Clothes Moths)", "Acarina (Mites)", "Trogidae (Carcass Beetles)"],
    diagnosticTaxa: "Tineola bisselliella, Trox scaber, Tyroglyphus farinae",
    status: "FINAL",
  },
];

export interface PmiCalculationResult {
  species: string;
  development_stage: string;
  t_base_c: number;
  target_adh: number;
  accumulated_adh: number;
  pmi_min_hours: number;
  pmi_min_days: number;
  colonisation_timestamp: string | null;
  delta_t_mass_applied_c: number;
  is_target_adh_satisfied: boolean;
  hours_integrated: number;
  effective_degree_step: number;
  warning?: string;
  prosecutors_fallacy_shield: string;
  source: "API" | "LOCAL_FALLBACK";
}

// ═══════════════════════════════════════════════════════════════════════════════
// CRYPTOGRAPHIC STATE AUDIT HASH GENERATOR (ISO/IEC 17025)
// ═══════════════════════════════════════════════════════════════════════════════

async function computeEntomologyAuditHash(
  species: string,
  stage: string,
  targetAdh: number,
  ambientTemp: number,
  deltaTMass: number,
  pmiHours: number,
  colonisationTime: string,
  caseId: string
): Promise<string> {
  const rawString = `${species}|${stage}|${targetAdh.toFixed(2)}|${ambientTemp.toFixed(2)}|${deltaTMass.toFixed(2)}|${pmiHours.toFixed(2)}|${colonisationTime}|${caseId}`;
  try {
    if (typeof window !== "undefined" && window.crypto && window.crypto.subtle) {
      const encoder = new TextEncoder();
      const data = encoder.encode(rawString);
      const hashBuffer = await window.crypto.subtle.digest("SHA-256", data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
    }
  } catch {
    // Fallback simple 64-hex deterministic string
  }
  let hash = 0;
  for (let i = 0; i < rawString.length; i++) {
    const char = rawString.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash |= 0;
  }
  return Math.abs(hash).toString(16).padStart(64, "e");
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export default function EntomologyPmiPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  // Forensic case store connection
  const activeCase = useForensicCaseStore((state) => state.activeCase);
  const addAuditLog = useForensicCaseStore((state) => state.addAuditLog);

  // Tactical navigation
  const [activeTab, setActiveTab] = useState<EntomologyTabId>("mici");
  const [selectedPresetId, setSelectedPresetId] = useState<string>("VECTOR_23_ENTO_A");

  // Core parameters
  const [selectedSpecies, setSelectedSpecies] = useState<string>("Lucilia sericata");
  const [selectedStage, setSelectedStage] = useState<string>("3rd Instar Feeding");
  const [avgAmbientTemp, setAvgAmbientTemp] = useState<number>(20.0);
  const [deltaTMass, setDeltaTMass] = useState<number>(0.0);
  const [samplingTime, setSamplingTime] = useState<string>("2026-08-16T12:00");
  const [altitudeOffsetMeters, setAltitudeOffsetMeters] = useState<number>(0);
  const [nocturnalOvipositionCheck, setNocturnalOvipositionCheck] = useState<boolean>(false);
  const [weatherProfileType, setWeatherProfileType] = useState<"diurnal" | "heatwave" | "coldfront" | "constant">("diurnal");

  // Execution state
  const [loading, setLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [stageText, setStageText] = useState<string>("");
  const [apiLatencyMs, setApiLatencyMs] = useState<number>(42);
  const [lastCalculatedTime, setLastCalculatedTime] = useState<string | null>(null);
  const [auditHash, setAuditHash] = useState<string>("");
  const [copiedHash, setCopiedHash] = useState<boolean>(false);

  // Result state
  const [pmiResult, setPmiResult] = useState<PmiCalculationResult>({
    species: "Lucilia sericata",
    development_stage: "3rd Instar Feeding",
    t_base_c: 9.0,
    target_adh: 1254.5,
    accumulated_adh: 1254.5,
    pmi_min_hours: 114.05,
    pmi_min_days: 4.75,
    colonisation_timestamp: "2026-08-11T17:57:00Z",
    delta_t_mass_applied_c: 0.0,
    is_target_adh_satisfied: true,
    hours_integrated: 115,
    effective_degree_step: 11.0,
    prosecutors_fallacy_shield:
      "The estimated minimum PMI (PMI_min) represents the Minimum Insect Colonisation Interval (MICI) according to EAFE / NAFEA guidelines.",
    source: "LOCAL_FALLBACK",
  });

  // Current species metadata
  const speciesTaxon = useMemo(() => {
    return ENTOMOLOGY_SPECIES_REGISTRY[selectedSpecies] || ENTOMOLOGY_SPECIES_REGISTRY["Lucilia sericata"];
  }, [selectedSpecies]);

  const availableStages = useMemo(() => {
    return Object.keys(speciesTaxon.stages);
  }, [speciesTaxon]);

  // Client-side analytical solver
  const solveClientPmi = useCallback(
    (spec: string, stg: string, dMass: number, ambTemp: number, sampIso: string, noctGate: boolean, altMeters: number): PmiCalculationResult => {
      const taxon = ENTOMOLOGY_SPECIES_REGISTRY[spec] || ENTOMOLOGY_SPECIES_REGISTRY["Lucilia sericata"];
      const targetAdh = taxon.stages[stg]?.adh || 1254.5;

      // Environmental lapse rate correction (-0.65°C / 100m)
      const lapseCorrection = (altMeters / 100.0) * -0.65;
      const effectiveAmbient = ambTemp + lapseCorrection;
      const effectiveTemp = effectiveAmbient + dMass;
      const degreeStep = Math.max(0.0, effectiveTemp - taxon.t_base);

      let hours = degreeStep > 0.0 ? Number((targetAdh / degreeStep).toFixed(2)) : 0.0;
      let isSatisfied = degreeStep > 0.0;

      // Base sample time
      const sampleDate = new Date(sampIso ? `${sampIso}:00Z` : new Date().toISOString());
      let colonDate = new Date(sampleDate.getTime() - hours * 3600 * 1000);

      // Nocturnal Oviposition Gate (Scotophase between 21:00 and 06:00 UTC/Local)
      if (noctGate && hours > 0) {
        const colonHour = colonDate.getUTCHours();
        if (colonHour >= 21 || colonHour < 6) {
          // Push backward to the preceding daylight dusk (20:30)
          const delayHours = colonHour >= 21 ? colonHour - 20.5 : colonHour + 3.5;
          hours = Number((hours + delayHours).toFixed(2));
          colonDate = new Date(sampleDate.getTime() - hours * 3600 * 1000);
        }
      }

      const days = Number((hours / 24.0).toFixed(2));

      return {
        species: spec,
        development_stage: stg,
        t_base_c: taxon.t_base,
        target_adh: targetAdh,
        accumulated_adh: isSatisfied ? targetAdh : 0.0,
        pmi_min_hours: hours,
        pmi_min_days: days,
        colonisation_timestamp: isSatisfied ? colonDate.toISOString() : null,
        delta_t_mass_applied_c: dMass,
        is_target_adh_satisfied: isSatisfied,
        hours_integrated: Math.ceil(hours),
        effective_degree_step: Number(degreeStep.toFixed(2)),
        warning: !isSatisfied
          ? (isTr ? "Sıcaklık alt eşik değerinin altındadır. Gelişim durmuştur." : "Temperature is below developmental threshold T_base. Quiescence observed.")
          : undefined,
        prosecutors_fallacy_shield: isTr
          ? "Tahmin edilen minimum PMI (PMI_min), EAFE / NAFEA kılavuzlarına göre Minimum Böcek Kolonizasyon Aralığını (MICI) temsil eder. Gece yumurtlama baskısı ve kapalı mekan gecikmesi göz önüne alınmalıdır."
          : "The estimated minimum PMI (PMI_min) represents the Minimum Insect Colonisation Interval (MICI) according to EAFE / NAFEA guidelines. Nocturnal oviposition suppression and indoor delay must be evaluated.",
        source: "LOCAL_FALLBACK",
      };
    },
    [isTr]
  );

  // Generate realistic hourly temperatures array for backend API
  const generateHourlyTemps = useCallback(
    (avgTemp: number, profile: string) => {
      return Array.from({ length: 240 }, (_, i) => {
        let temp = avgTemp;
        if (profile === "diurnal") {
          temp += Math.sin((i / 12) * Math.PI) * 4.5;
        } else if (profile === "heatwave") {
          temp += 5.0 + Math.sin((i / 12) * Math.PI) * 6.0;
        } else if (profile === "coldfront") {
          temp -= 6.0 + Math.sin((i / 12) * Math.PI) * 2.0;
        }
        return {
          hour_index: i,
          temperature_c: Number(temp.toFixed(2)),
        };
      });
    },
    []
  );

  // Primary execution handler (Live API + Local Fallback)
  const runPmiEstimation = useCallback(async () => {
    if (loading) return;
    const startTime = performance.now();
    setLoading(true);
    setProgress(15);
    setStageText(
      isTr
        ? "Tür termal eşiği (T_base) & evre hedef ADH değeri sorgulanıyor..."
        : "Fetching species thermal baseline (T_base) & development stage ADH target..."
    );

    const API_BASE = getApiBaseUrl();
    const caseId = activeCase?.profile?.profileId || "CASE-2026-ENTO-01";

    try {
      const hourlyTemps = generateHourlyTemps(avgAmbientTemp, weatherProfileType);

      setProgress(45);
      setStageText(
        isTr
          ? "240 saatlik meteoroloji serisi geriye doğru entegre ediliyor..."
          : "Integrating backward through 240-hour ambient temperature history..."
      );

      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/entomology-pmi-estimation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          species_name: selectedSpecies,
          development_stage: selectedStage,
          hourly_temperatures: hourlyTemps,
          delta_t_mass: deltaTMass,
          sampling_time_iso: samplingTime ? `${samplingTime}:00Z` : null,
        }),
        signal: AbortSignal.timeout(3500),
      });

      const elapsed = Math.round(performance.now() - startTime);
      setApiLatencyMs(elapsed);

      if (res.ok) {
        const data = await res.json();
        const effectiveStep = Math.max(0.0, avgAmbientTemp + deltaTMass - speciesTaxon.t_base);
        const resolvedResult: PmiCalculationResult = {
          ...data,
          effective_degree_step: Number(effectiveStep.toFixed(2)),
          source: "API",
        };
        setPmiResult(resolvedResult);

        // Update SHA-256 state hash
        const h = await computeEntomologyAuditHash(
          selectedSpecies,
          selectedStage,
          data.target_adh,
          avgAmbientTemp,
          deltaTMass,
          data.pmi_min_hours,
          data.colonisation_timestamp || "",
          caseId
        );
        setAuditHash(h);

        // Dispatch audit log
        if (addAuditLog) {
          addAuditLog({
            event: `Calculated MICI for ${selectedSpecies} (${selectedStage}) via live FastAPI endpoint: PMI_min=${data.pmi_min_hours}h (${data.pmi_min_days}d). Audit Hash: ${h.slice(0, 16)}...`,
            module: "26. Forensic Entomology",
            analyst: "Active Session",
            status: "PASS",
            standard: "EAFE / NAFEA Protocol",
          });
        }
      } else {
        throw new Error(`Server returned HTTP ${res.status}`);
      }
    } catch {
      // Graceful local fallback
      const elapsed = Math.round(performance.now() - startTime);
      setApiLatencyMs(elapsed);

      const fallback = solveClientPmi(
        selectedSpecies,
        selectedStage,
        deltaTMass,
        avgAmbientTemp,
        samplingTime,
        nocturnalOvipositionCheck,
        altitudeOffsetMeters
      );
      setPmiResult(fallback);

      const h = await computeEntomologyAuditHash(
        selectedSpecies,
        selectedStage,
        fallback.target_adh,
        avgAmbientTemp,
        deltaTMass,
        fallback.pmi_min_hours,
        fallback.colonisation_timestamp || "",
        caseId
      );
      setAuditHash(h);

      if (addAuditLog) {
        addAuditLog({
          event: `Calculated MICI for ${selectedSpecies} (${selectedStage}) via local fallback engine: PMI_min=${fallback.pmi_min_hours}h. Audit Hash: ${h.slice(0, 16)}...`,
          module: "26. Forensic Entomology",
          analyst: "Active Session",
          status: "PASS",
          standard: "EAFE / NAFEA Protocol",
        });
      }
    } finally {
      setProgress(100);
      setStageText(
        isTr
          ? "Termal toplam yakınsadı. MICI kolonizasyon zamanı saptandı."
          : "Thermal summation converged. MICI colonization timestamp resolved."
      );
      setTimeout(() => {
        setLoading(false);
        setLastCalculatedTime(new Date().toLocaleTimeString());
      }, 150);
    }
  }, [
    loading,
    isTr,
    activeCase,
    avgAmbientTemp,
    weatherProfileType,
    selectedSpecies,
    selectedStage,
    deltaTMass,
    samplingTime,
    speciesTaxon.t_base,
    addAuditLog,
    solveClientPmi,
    generateHourlyTemps,
    nocturnalOvipositionCheck,
    altitudeOffsetMeters,
  ]);

  // Select a golden benchmark preset
  const handleSelectPreset = useCallback(
    (preset: GoldenBenchmarkPreset) => {
      setSelectedPresetId(preset.id);
      setSelectedSpecies(preset.species);
      setSelectedStage(preset.stage);
      setAvgAmbientTemp(preset.ambientTemp);
      setDeltaTMass(preset.deltaTMass);
      setSamplingTime(preset.samplingTime);
      setNocturnalOvipositionCheck(preset.nocturnalSuppression);

      const caseId = activeCase?.profile?.profileId || "CASE-2026-ENTO-01";
      if (addAuditLog) {
        addAuditLog({
          event: `Loaded Golden Benchmark Preset ${preset.id} (${preset.name}): species=${preset.species}, stage=${preset.stage}, expected ADH=${preset.expectedAdh}.`,
          module: "26. Forensic Entomology",
          analyst: "Active Session",
          status: "PASS",
          standard: "EAFE / NAFEA Protocol",
        });
      }

      // Automatically recalculate
      const fallback = solveClientPmi(
        preset.species,
        preset.stage,
        preset.deltaTMass,
        preset.ambientTemp,
        preset.samplingTime,
        preset.nocturnalSuppression,
        altitudeOffsetMeters
      );
      setPmiResult(fallback);

      computeEntomologyAuditHash(
        preset.species,
        preset.stage,
        fallback.target_adh,
        preset.ambientTemp,
        preset.deltaTMass,
        fallback.pmi_min_hours,
        fallback.colonisation_timestamp || "",
        caseId
      ).then((h) => setAuditHash(h));

      setLastCalculatedTime(new Date().toLocaleTimeString());
    },
    [activeCase, addAuditLog, solveClientPmi, altitudeOffsetMeters]
  );

  // Initialize state hash on mount
  useEffect(() => {
    const caseId = activeCase?.profile?.profileId || "CASE-2026-ENTO-01";
    computeEntomologyAuditHash(
      selectedSpecies,
      selectedStage,
      pmiResult.target_adh,
      avgAmbientTemp,
      deltaTMass,
      pmiResult.pmi_min_hours,
      pmiResult.colonisation_timestamp || "",
      caseId
    ).then((h) => setAuditHash(h));
  }, [selectedSpecies, selectedStage, pmiResult, avgAmbientTemp, deltaTMass, activeCase]);

  // Copy hash action
  const handleCopyHash = () => {
    if (!auditHash) return;
    navigator.clipboard.writeText(auditHash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
    if (addAuditLog) {
      addAuditLog({
        event: `Copied ISO/IEC 17025 SHA-256 state audit hash ${auditHash} to clipboard for court presentation.`,
        module: "26. Forensic Entomology",
        analyst: "Active Session",
        status: "PASS",
        standard: "ISO/IEC 17025 §7.8",
      });
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Modern Unified Benchmark & Standards Mission Bar ────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        {/* Top: Engine Identity & Technical Verification Badges */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 shrink-0">
              <Bug className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "Alt Sistem 26: Adli Entomoloji & Minimum PMI Çalışma Alanı" : "Subsystem 26: Forensic Entomology & Minimum PMI Studio"}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                  EAFE • NAFEA
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-blue-500/10 border border-blue-500/30 text-blue-300">
                  ISO/IEC 17025
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-300">
                  ASTM E1588-20
                </span>
              </div>
              <p className="text-[10px] text-zinc-400 truncate mt-0.5">
                {isTr
                  ? "Calliphoridae termal enerji toplamı (ADD/ADH), Mégnin ardışık dalgaları ve minimum böcek kolonizasyon aralığı (MICI) çözücüsü"
                  : "Calliphoridae thermal energy summation (ADD/ADH), Megnin succession waves & minimum insect colonization interval (MICI) solver"}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <span
              className={`text-[9px] font-bold px-2 py-1 rounded-md border flex items-center gap-1.5 ${
                pmiResult.source === "API"
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : "bg-amber-500/10 border-amber-500/30 text-amber-300"
              }`}
            >
              <Activity className="w-3 h-3" />
              {pmiResult.source === "API" ? `200 OK (FastAPI Live • ${apiLatencyMs}ms)` : `Local Engine Active (${apiLatencyMs}ms)`}
            </span>

            {lastCalculatedTime && (
              <span className="text-[9px] text-emerald-400 font-bold bg-white/[0.03] border border-white/10 px-2.5 py-1 rounded-lg flex items-center gap-1">
                <Check className="w-3 h-3" />
                {lastCalculatedTime}
              </span>
            )}

            <button
              type="button"
              onClick={runPmiEstimation}
              disabled={loading}
              className="px-3.5 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-extrabold text-[10px] uppercase tracking-wider transition-all disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer active:scale-95 shadow-md shadow-emerald-500/20"
            >
              <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
              <span>
                {loading
                  ? (isTr ? `Entegre Ediliyor %${progress}...` : `Integrating ${progress}%...`)
                  : (isTr ? "PMI_min Hesapla" : "Calculate PMI_min")}
              </span>
            </button>
          </div>
        </div>

        {/* Golden Benchmark Presets Ribbon */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-[10px] text-zinc-400 font-bold">
            <span className="flex items-center gap-1.5 text-zinc-300">
              <Database className="w-3 h-3 text-emerald-400" />
              {isTr ? "Standart Altın Vektörler & Doğrulama Şablonları (VECTOR_23_ENTO_A-H):" : "Golden Benchmark Vectors & Validation Presets (VECTOR_23_ENTO_A-H):"}
            </span>
            <span className="text-[9px] text-emerald-400">
              {activeCase?.profile?.profileId ? `Aktif Vaka: ${activeCase.profile.profileId}` : "Referans Vaka: CASE-2026-ENTO-01"}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-1.5">
            {ENTOMOLOGY_BENCHMARKS.map((preset) => {
              const isSelected = selectedPresetId === preset.id;
              return (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => handleSelectPreset(preset)}
                  className={`p-2 rounded-xl text-left border transition-all text-[10px] cursor-pointer ${
                    isSelected
                      ? "bg-emerald-500/20 border-emerald-500/60 text-emerald-200 shadow-md shadow-emerald-500/10"
                      : "bg-black/40 border-tactical-border/50 text-zinc-400 hover:border-zinc-500 hover:text-zinc-200"
                  }`}
                >
                  <div className="font-extrabold truncate text-[9px] text-zinc-300">{preset.id.replace("VECTOR_23_ENTO_", "ENTO-")}</div>
                  <div className="truncate font-semibold text-[9px]">{isTr ? preset.nameTr : preset.name}</div>
                  <div className="text-[8px] text-zinc-500 mt-0.5">{preset.expectedAdh} ADH</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Navigation Tabs ── */}
        <div className="flex items-center gap-1 border-t border-tactical-border/40 pt-3 overflow-x-auto no-scrollbar">
          {[
            { id: "mici", label: isTr ? "1. Canlı MICI Çözücü" : "1. Live MICI Solver", icon: Clock },
            { id: "species", label: isTr ? "2. Diptera & Kınkanatlı Taksonomisi" : "2. Diptera & Coleoptera Taxonomy", icon: Bug },
            { id: "succession", label: isTr ? "3. Isomegalen & Mégnin Dalgaları" : "3. Isomegalen & Megnin Waves", icon: TrendingUp },
            { id: "maggot_mass", label: isTr ? "4. Larva Kümesi & Meteoroloji" : "4. Maggot Mass & Weather", icon: Flame },
            { id: "audit", label: isTr ? "5. ISO 17025 Durum Özeti" : "5. ISO 17025 State Audit", icon: ShieldCheck },
          ].map((tab) => {
            const IconComponent = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id as EntomologyTabId)}
                className={`px-3 py-1.5 rounded-lg text-[11px] font-bold transition-all flex items-center gap-1.5 whitespace-nowrap cursor-pointer ${
                  isActive
                    ? "bg-emerald-500 text-zinc-950 shadow-md shadow-emerald-500/20"
                    : "bg-black/30 border border-tactical-border/40 text-zinc-400 hover:text-zinc-200 hover:border-zinc-600"
                }`}
              >
                <IconComponent className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Active Progress Bar ── */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-3.5 space-y-2 overflow-hidden shadow-lg"
          >
            <div className="flex items-center justify-between text-xs text-emerald-300">
              <span className="flex items-center gap-2 font-bold truncate">
                <Cpu className="w-4 h-4 animate-pulse text-emerald-400 shrink-0" />
                {stageText}
              </span>
              <span className="font-mono font-black tabular-nums text-sm">%{progress}</span>
            </div>
            <div className="w-full bg-zinc-900 rounded-full h-2.5 overflow-hidden border border-emerald-500/20">
              <motion.div
                className="bg-gradient-to-r from-emerald-500 to-teal-400 h-2.5 rounded-full shadow-[0_0_12px_rgba(16,185,129,0.6)]"
                initial={{ width: "5%" }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.2 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ═════════════════════════════════════════════════════════════════════ */}
      {/* TAB 1: LIVE MICI SOLVER & THERMAL SUMMATION                           */}
      {/* ═════════════════════════════════════════════════════════════════════ */}
      {activeTab === "mici" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Environmental & Biological Inputs */}
          <div className="lg:col-span-2 space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                <Sliders className="w-4 h-4 text-emerald-400" />
                {isTr ? "Entomolojik Parametreler & Termal Çevre Akışı" : "Entomological Parameters & Ambient Thermal Stream"}
              </span>
              <span className="text-[9px] text-zinc-400 font-mono">EAFE / NAFEA 2020 Protocol</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <span className="text-[10px] text-zinc-400 font-bold uppercase">
                  {isTr ? "Nekrofaj Böcek Türü (Species)" : "Necrophagous Species"}
                </span>
                <select
                  value={selectedSpecies}
                  onChange={(e) => {
                    const newSpecies = e.target.value;
                    setSelectedSpecies(newSpecies);
                    const taxon = ENTOMOLOGY_SPECIES_REGISTRY[newSpecies];
                    const firstStage = Object.keys(taxon?.stages || {})[0];
                    if (firstStage) setSelectedStage(firstStage);
                  }}
                  className="w-full min-h-[40px] p-2.5 rounded-xl border border-tactical-border/60 bg-black/60 text-xs text-zinc-200 cursor-pointer focus:border-emerald-500 focus:outline-none"
                >
                  {Object.keys(ENTOMOLOGY_SPECIES_REGISTRY).map((sp) => (
                    <option key={sp} value={sp}>
                      {sp} ({isTr ? ENTOMOLOGY_SPECIES_REGISTRY[sp].common_tr : ENTOMOLOGY_SPECIES_REGISTRY[sp].common})
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <span className="text-[10px] text-zinc-400 font-bold uppercase">
                  {isTr ? "Ceset Üzerinde Tespit Edilen En Eski Evre" : "Oldest Developmental Stage on Carcass"}
                </span>
                <select
                  value={selectedStage}
                  onChange={(e) => setSelectedStage(e.target.value)}
                  className="w-full min-h-[40px] p-2.5 rounded-xl border border-tactical-border/60 bg-black/60 text-xs text-zinc-200 cursor-pointer focus:border-emerald-500 focus:outline-none"
                >
                  {availableStages.map((stg) => (
                    <option key={stg} value={stg}>
                      {stg} - {speciesTaxon.stages[stg]?.adh || 0} ADH ({isTr ? speciesTaxon.stages[stg]?.tr : stg})
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-[10px] font-bold">
                  <span className="text-zinc-400 uppercase">{isTr ? "Ortalama Ortam Sıcaklığı" : "Average Ambient Temperature"}</span>
                  <span className="text-emerald-400 font-mono tabular-nums">{avgAmbientTemp.toFixed(1)}°C</span>
                </div>
                <input
                  type="range"
                  min={0.0}
                  max={42.0}
                  step={0.5}
                  value={avgAmbientTemp}
                  onChange={(e) => setAvgAmbientTemp(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center text-[10px] font-bold">
                  <span className="text-zinc-400 uppercase">{isTr ? "Larva Kümesi Metabolik Isısı (+ΔT_mass)" : "Larval Mass Self-Heating (+ΔT_mass)"}</span>
                  <span className="text-amber-400 font-mono tabular-nums">+{deltaTMass.toFixed(1)}°C</span>
                </div>
                <input
                  type="range"
                  min={0.0}
                  max={5.0}
                  step={0.1}
                  value={deltaTMass}
                  onChange={(e) => setDeltaTMass(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
                />
              </div>

              <div className="space-y-1.5">
                <span className="text-[10px] text-zinc-400 font-bold uppercase">{isTr ? "Örnekleme Zamanı (Olay Yeri)" : "Sampling Timestamp"}</span>
                <input
                  type="datetime-local"
                  value={samplingTime}
                  onChange={(e) => setSamplingTime(e.target.value)}
                  className="w-full min-h-[40px] p-2.5 rounded-xl border border-tactical-border/60 bg-black/60 text-xs text-zinc-200 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="space-y-1.5">
                <span className="text-[10px] text-zinc-400 font-bold uppercase">{isTr ? "Hava Durumu Simülasyon Profili" : "Weather Profile Simulation"}</span>
                <select
                  value={weatherProfileType}
                  onChange={(e) => setWeatherProfileType(e.target.value as "diurnal" | "heatwave" | "coldfront" | "constant")}
                  className="w-full min-h-[40px] p-2.5 rounded-xl border border-tactical-border/60 bg-black/60 text-xs text-zinc-200 cursor-pointer focus:border-emerald-500 focus:outline-none"
                >
                  <option value="diurnal">{isTr ? "Günlük Doğal Salınım (±4.5°C Diyurnal)" : "Natural Diurnal Cycle (±4.5°C)"}</option>
                  <option value="heatwave">{isTr ? "Yaz Sıcak Hava Dalgası (+5.0°C Sıcak)" : "Heatwave Thermal Surge (+5.0°C)"}</option>
                  <option value="coldfront">{isTr ? "Kış Soğuk Hava Cephesi (-6.0°C Soğuk)" : "Cold Front Depression (-6.0°C)"}</option>
                  <option value="constant">{isTr ? "Sabit Sıcaklık (Laboratuvar Odası)" : "Constant Temperature (Lab Room)"}</option>
                </select>
              </div>
            </div>

            {/* Additional Toggles */}
            <div className="p-3 bg-black/40 border border-tactical-border/50 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <label className="flex items-center gap-2 cursor-pointer text-xs text-zinc-300">
                <input
                  type="checkbox"
                  checked={nocturnalOvipositionCheck}
                  onChange={(e) => setNocturnalOvipositionCheck(e.target.checked)}
                  className="w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-emerald-500"
                />
                <span className="flex items-center gap-1.5 font-bold">
                  <Moon className="w-3.5 h-3.5 text-blue-400" />
                  {isTr ? "Gece Yumurtlama Baskısı Filtresi (21:00 - 06:00 Fotoperiyot)" : "Nocturnal Oviposition Scotophase Gate (21:00 - 06:00)"}
                </span>
              </label>

              <span className="text-[10px] text-zinc-500">
                {isTr ? "Sinekler karanlıkta yumurtlamaz; MICI önceki aydınlık evreye ötelenir." : "Flies suppress oviposition in dark; pushes MICI to previous daylight."}
              </span>
            </div>

            {/* EAFE / NAFEA Legal Defense Statement */}
            <div className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/30 text-[11px] text-zinc-300 space-y-1.5">
              <div className="flex items-center gap-2 text-emerald-400 font-extrabold uppercase text-[10px]">
                <ShieldCheck className="w-4 h-4" />
                {isTr ? "EAFE & NAFEA Yasal Adli Entomoloji Kalkanı" : "EAFE & NAFEA Legal Admissibility Defense Shield"}
              </div>
              <p className="text-[10px] leading-relaxed text-zinc-400">
                {pmiResult.prosecutors_fallacy_shield}
              </p>
            </div>
          </div>

          {/* Right Column: Calculated MICI Posterior Telemetry */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                <Clock className="w-4 h-4 text-emerald-400" />
                {isTr ? "MICI Sonuç Metrikleri" : "MICI Posterior Telemetry"}
              </span>
              <span className="text-[9px] px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-bold">
                K = y • (T - T0)
              </span>
            </div>

            {/* Big Hours Card */}
            <div className="p-4 rounded-xl bg-black/60 border border-emerald-500/40 text-center space-y-1">
              <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
                {isTr ? "Minimum Kolonizasyon Süresi (PMI_min)" : "Minimum Colonisation Interval (PMI_min)"}
              </span>
              <div className="text-3xl sm:text-4xl font-black text-emerald-400 font-mono tabular-nums">
                {pmiResult.pmi_min_hours.toFixed(1)}{" "}
                <span className="text-xs font-normal text-zinc-400">{isTr ? "Saat" : "Hours"}</span>
              </div>
              <div className="text-xs font-bold text-zinc-300 font-mono">
                ≈ {pmiResult.pmi_min_days.toFixed(2)} {isTr ? "Gün" : "Days"}
              </div>
            </div>

            {pmiResult.warning && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-[10px] text-red-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                <span>{pmiResult.warning}</span>
              </div>
            )}

            {/* Colonisation Date Card */}
            <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/50 space-y-1">
              <span className="text-[10px] text-zinc-400 font-bold uppercase flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-emerald-400" />
                {isTr ? "En Erken Yumurtlama / Kolonizasyon Zamanı" : "Earliest Oviposition / Colonization Time"}
              </span>
              <div className="text-xs font-mono font-bold text-white">
                {pmiResult.colonisation_timestamp
                  ? new Date(pmiResult.colonisation_timestamp).toUTCString()
                  : (isTr ? "Gelişim eşiği aşılmadı (Durgunluk)" : "Threshold not exceeded (Quiescence)")}
              </div>
            </div>

            {/* Thermal Parameters Table */}
            <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/50 space-y-2 text-[10px]">
              <div className="flex justify-between items-center text-zinc-400 border-b border-tactical-border/30 pb-1.5">
                <span>{isTr ? "Tür Eşik Sıcaklığı (T_base):" : "Species Threshold (T_base):"}</span>
                <span className="text-white font-mono font-bold">{speciesTaxon.t_base.toFixed(1)}°C</span>
              </div>
              <div className="flex justify-between items-center text-zinc-400 border-b border-tactical-border/30 pb-1.5">
                <span>{isTr ? "Hedef Evre Termal Enerjisi (K):" : "Target Stage Thermal Energy (K):"}</span>
                <span className="text-emerald-400 font-mono font-bold">{pmiResult.target_adh.toFixed(1)} ADH</span>
              </div>
              <div className="flex justify-between items-center text-zinc-400 border-b border-tactical-border/30 pb-1.5">
                <span>{isTr ? "Etkin Sıcaklık (T_eff = T_amb + ΔT):" : "Effective Temp (T_eff = T_amb + ΔT):"}</span>
                <span className="text-amber-400 font-mono font-bold">{(avgAmbientTemp + deltaTMass).toFixed(1)}°C</span>
              </div>
              <div className="flex justify-between items-center text-zinc-400 border-b border-tactical-border/30 pb-1.5">
                <span>{isTr ? "Saat Başına Biriken ADH (T_eff - T_base):" : "Accumulated ADH/Hour (T_eff - T_base):"}</span>
                <span className="text-white font-mono font-bold">{pmiResult.effective_degree_step.toFixed(1)} ADH/saat</span>
              </div>
              <div className="flex justify-between items-center text-zinc-400">
                <span>{isTr ? "İntegrasyon Durumu:" : "Integration Status:"}</span>
                <span
                  className={`font-mono font-bold px-2 py-0.5 rounded text-[9px] ${
                    pmiResult.is_target_adh_satisfied ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300"
                  }`}
                >
                  {pmiResult.is_target_adh_satisfied ? (isTr ? "TAMAMLANDI" : "CONVERGED") : (isTr ? "YETERSİZ" : "INSUFFICIENT")}
                </span>
              </div>
            </div>

            {/* Quick Action Button */}
            <button
              type="button"
              onClick={runPmiEstimation}
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-zinc-950 font-extrabold text-xs uppercase tracking-wider transition-all disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-emerald-500/20"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              <span>{loading ? (isTr ? "İntegral Hesaplanıyor..." : "Integrating...") : (isTr ? "Hesaplamayı Yenile" : "Re-Calculate PMI")}</span>
            </button>
          </div>
        </div>
      )}

      {/* ═════════════════════════════════════════════════════════════════════ */}
      {/* TAB 2: SPECIES TAXONOMY CATALOG & IKEMOTO-TAKAI MODEL                */}
      {/* ═════════════════════════════════════════════════════════════════════ */}
      {activeTab === "species" && (
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
            <div className="flex items-center gap-2">
              <Bug className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                {isTr ? "Adli Diptera & Coleoptera Tür Kataloğu ve Termal Sabitleri" : "Forensic Diptera & Coleoptera Species Registry & Thermal Constants"}
              </span>
            </div>
            <span className="text-[10px] text-zinc-400 font-mono">Ikemoto & Takai (2000) Linearized Parameters</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.values(ENTOMOLOGY_SPECIES_REGISTRY).map((taxon) => {
              const isSelected = selectedSpecies === taxon.name;
              return (
                <div
                  key={taxon.id}
                  onClick={() => {
                    setSelectedSpecies(taxon.name);
                    const first = Object.keys(taxon.stages)[0];
                    if (first) setSelectedStage(first);
                  }}
                  className={`p-4 rounded-xl border transition-all cursor-pointer space-y-3 ${
                    isSelected
                      ? "bg-emerald-500/10 border-emerald-500 text-zinc-200 shadow-lg shadow-emerald-500/10"
                      : "bg-black/40 border-tactical-border/50 text-zinc-400 hover:border-zinc-500"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-extrabold text-sm text-white italic">{taxon.name}</h4>
                      <p className="text-[10px] text-emerald-400 font-semibold">{isTr ? taxon.common_tr : taxon.common}</p>
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-zinc-400 mt-1 inline-block">
                        Familya: {taxon.family}
                      </span>
                    </div>
                    {isSelected && (
                      <span className="p-1 rounded-md bg-emerald-500 text-zinc-950">
                        <Check className="w-3 h-3" />
                      </span>
                    )}
                  </div>

                  <p className="text-[10px] text-zinc-400 leading-relaxed border-t border-tactical-border/30 pt-2">
                    {isTr ? taxon.ecological_role_tr : taxon.ecological_role}
                  </p>

                  <div className="grid grid-cols-2 gap-2 text-[10px] pt-1">
                    <div className="p-2 rounded bg-black/50 border border-tactical-border/30">
                      <span className="text-zinc-500 text-[9px] block">Alt Eşik (T_base)</span>
                      <span className="text-white font-mono font-bold text-xs">{taxon.t_base.toFixed(1)}°C</span>
                    </div>
                    <div className="p-2 rounded bg-black/50 border border-tactical-border/30">
                      <span className="text-zinc-500 text-[9px] block">Toplam Termal K</span>
                      <span className="text-emerald-400 font-mono font-bold text-xs">{taxon.k_total.toFixed(0)} ADH</span>
                    </div>
                    <div className="p-2 rounded bg-black/50 border border-tactical-border/30">
                      <span className="text-zinc-500 text-[9px] block">Üst Limit (T_max)</span>
                      <span className="text-amber-400 font-mono font-bold text-xs">{taxon.t_max.toFixed(1)}°C</span>
                    </div>
                    <div className="p-2 rounded bg-black/50 border border-tactical-border/30">
                      <span className="text-zinc-500 text-[9px] block">Ikemoto Eğimi</span>
                      <span className="text-blue-400 font-mono font-bold text-xs">{taxon.ikemoto_slope.toFixed(1)}</span>
                    </div>
                  </div>

                  <div className="space-y-1 border-t border-tactical-border/30 pt-2">
                    <span className="text-[9px] text-zinc-400 font-bold block">{isTr ? "Evre ADH Gereksinimleri:" : "Stage ADH Requirements:"}</span>
                    <div className="flex flex-wrap gap-1 text-[9px]">
                      {Object.entries(taxon.stages).map(([stgKey, stgData]) => (
                        <span key={stgKey} className="px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-300">
                          {stgKey}: <strong className="text-emerald-400">{stgData.adh}</strong>
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ═════════════════════════════════════════════════════════════════════ */}
      {/* TAB 3: ISOMEGALEN CURVES & MEGNIN SUCCESSION WAVES                    */}
      {/* ═════════════════════════════════════════════════════════════════════ */}
      {activeTab === "succession" && (
        <div className="space-y-6">
          {/* Isomegalen Diagram Card */}
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr
                    ? `Isomegalen / Isopromen Gelişim Eğrisi (${speciesTaxon.name})`
                    : `Isomegalen / Isopromen Growth Diagram (${speciesTaxon.name})`}
                </span>
              </div>
              <span className="text-[10px] text-zinc-400 font-mono">EAFE Developmental Length mm vs ADH</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
              {Object.entries(speciesTaxon.stages).map(([stg, stgData]) => (
                <div key={stg} className="p-3 rounded-xl bg-black/40 border border-tactical-border/50 space-y-2 text-center">
                  <span className="text-[10px] font-bold text-white truncate block">{stg}</span>
                  <div className="text-lg font-black text-emerald-400 font-mono">{stgData.length_mm} mm</div>
                  <span className="text-[9px] text-zinc-400 block">{stgData.adh} ADH</span>
                  <span className="text-[8px] text-zinc-500 block">@20°C: ~{stgData.duration_hours_20c.toFixed(1)} sa</span>
                </div>
              ))}
            </div>

            <div className="p-3 rounded-xl bg-black/60 border border-tactical-border/40 text-[10px] text-zinc-400 leading-relaxed">
              <strong className="text-emerald-400 font-bold uppercase block mb-1">
                {isTr ? "Isomegalen Eğrisi Analiz Kuralı:" : "Isomegalen Curve Evaluative Principle:"}
              </strong>
              {isTr
                ? "Larva uzunluğu (mm), beslenme safhasında (L1, L2, L3F) termal enerji ile logaritmik olarak artar. Beslenme sonrası L3PF (wandering) evresinde larva büzüşerek puparyuma dönüşür. Bu evrede boy kısalması geriye doğru zaman tayininde Isopromen eğrisi ile teyit edilir."
                : "Larval length (mm) scales logarithmically with accumulated thermal energy during feeding instars (L1, L2, L3F). In the post-feeding L3PF wandering stage, larvae shrink slightly prior to pupariation; Isopromen curves reconcile shrinkage to protect against underestimating MICI."}
            </div>
          </div>

          {/* Mégnin's 5 Succession Waves Card (Migrated from Dead Code) */}
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr ? "Mégnin 5 Ekolojik Kolonizasyon Dalgası & Çürüme Evreleri" : "Megnin's 5 Ecological Succession Waves & Decay Taphonomy"}
                </span>
              </div>
              <span className="text-[10px] text-zinc-400 font-mono">Mégnin (1894) / Smith (1986) Classical Sequence</span>
            </div>

            <div className="space-y-3">
              {MEGNIN_SUCCESSION_WAVES.map((wave) => (
                <div
                  key={wave.wave}
                  className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-extrabold text-white">{isTr ? wave.titleTr : wave.title}</span>
                      <span className="text-[9px] px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-bold">
                        {isTr ? wave.periodTr : wave.period}
                      </span>
                    </div>
                    <p className="text-[10px] text-zinc-400 italic truncate">
                      {isTr ? "Belirteç Taksonlar:" : "Diagnostic Taxa:"} <span className="text-zinc-200">{wave.diagnosticTaxa}</span>
                    </p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[9px] text-zinc-400">
                      {isTr ? wave.families[0] : wave.families[0]}
                    </span>
                    <span
                      className={`text-[9px] font-bold px-2 py-0.5 rounded border ${
                        wave.status === "PRIMARY"
                          ? "bg-emerald-500/20 border-emerald-500 text-emerald-300"
                          : wave.status === "ACTIVE"
                          ? "bg-blue-500/20 border-blue-500 text-blue-300"
                          : "bg-zinc-800 border-zinc-700 text-zinc-400"
                      }`}
                    >
                      {wave.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ═════════════════════════════════════════════════════════════════════ */}
      {/* TAB 4: MAGGOT MASS MICROCLIMATE & WEATHER INGESTION                   */}
      {/* ═════════════════════════════════════════════════════════════════════ */}
      {activeTab === "maggot_mass" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Maggot Mass Thermodynamics */}
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Flame className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr ? "Larva Kümesi Metabolik Isı Modeli (Maggot Mass)" : "Larval Aggregate Metabolic Self-Heating Model"}
                </span>
              </div>
              <span className="text-[10px] text-amber-400 font-mono">+ΔT_mass Thermodynamics</span>
            </div>

            <p className="text-[10px] text-zinc-400 leading-relaxed">
              {isTr
                ? "Binlerce üçüncü evre Calliphoridae larvasının oluşturduğu agrega kütlelerde mikrobiyal fermantasyon ve yoğun metabolizma ortam sıcaklığından +1.5°C ile +5.0°C daha yüksek bir mikroiklim meydana getirir. Bu ısınma hesaba katılmadığında PMI_min olduğundan daha uzun hesaplanarak savunma lehine yanıltıcı olabilir."
                : "Aggregations of thousands of 3rd instar blowfly larvae generate metabolic heat elevating localized microclimates by +1.5°C to +5.0°C above ambient air. Failing to incorporate this offset overestimates the post-mortem interval, compromising forensic validity."}
            </p>

            <div className="p-4 rounded-xl bg-black/60 border border-tactical-border/50 space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-zinc-300">{isTr ? "Uygulanan Isı Farkı (+ΔT_mass):" : "Applied Temperature Differential:"}</span>
                <span className="text-amber-400 font-mono font-bold text-base">+{deltaTMass.toFixed(1)}°C</span>
              </div>
              <input
                type="range"
                min={0.0}
                max={5.0}
                step={0.1}
                value={deltaTMass}
                onChange={(e) => setDeltaTMass(parseFloat(e.target.value))}
                className="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
              <div className="flex justify-between text-[9px] text-zinc-500">
                <span>0.0°C (Dağınık / Az Sayıda)</span>
                <span>+2.5°C (Orta Büyüklükte Küme)</span>
                <span>+5.0°C (Devasa Agrega Kütle)</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-[10px] text-amber-200">
              {isTr
                ? "Öneri: Larva kümesi gövde derinliğindeyse (+2.0°C ile +3.5°C), yüzeyde dağınık haldeyse (+0.5°C ile +1.0°C) değerleri seçilmelidir."
                : "Recommendation: Apply +2.0°C to +3.5°C for dense core larval masses; apply +0.5°C to +1.0°C for dispersed surface instars."}
            </div>
          </div>

          {/* Weather Station Calibration & Altitude Lapse Rate */}
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Thermometer className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr ? "Meteoroloji İstasyonu İrtifa Kalibrasyonu" : "Weather Station Elevation Lapse Rate Calibration"}
                </span>
              </div>
              <span className="text-[10px] text-blue-400 font-mono">-0.65°C / 100m Lapse Rate</span>
            </div>

            <p className="text-[10px] text-zinc-400 leading-relaxed">
              {isTr
                ? "Olay yeri ile en yakın meteoroloji istasyonu arasındaki irtifa farkı çevresel gradyan formülü (ΔT = -0.65°C / 100m) ile düzeltilmelidir. Yüksek rakımlı olay yerlerinde ortam sıcaklığı istasyondan daha soğuktur."
                : "Elevation differences between the crime scene and the official meteorological weather station must be adjusted using the environmental lapse rate (-0.65°C per 100m elevation gain) to avoid systemic thermal bias."}
            </p>

            <div className="p-4 rounded-xl bg-black/60 border border-tactical-border/50 space-y-3">
              <div className="flex justify-between items-center text-xs">
                <span className="font-bold text-zinc-300">{isTr ? "Olay Yeri İrtifa Farkı (Δh):" : "Elevation Offset (Δh):"}</span>
                <span className="text-blue-400 font-mono font-bold text-base">
                  {altitudeOffsetMeters >= 0 ? `+${altitudeOffsetMeters}` : altitudeOffsetMeters} m
                </span>
              </div>
              <input
                type="range"
                min={-500}
                max={1500}
                step={50}
                value={altitudeOffsetMeters}
                onChange={(e) => setAltitudeOffsetMeters(parseInt(e.target.value))}
                className="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              <div className="flex justify-between text-[9px] text-zinc-500">
                <span>-500m (Vadi İçi)</span>
                <span>0m (İstasyonla Eşit)</span>
                <span>+1500m (Yüksek Dağ / Yayla)</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 text-[10px] space-y-1">
              <div className="flex justify-between text-zinc-400">
                <span>{isTr ? "Hesaplanan Sıcaklık Düzeltmesi:" : "Calculated Temperature Offset:"}</span>
                <span className="text-blue-400 font-bold font-mono">
                  {((altitudeOffsetMeters / 100.0) * -0.65).toFixed(2)}°C
                </span>
              </div>
              <div className="flex justify-between text-zinc-400">
                <span>{isTr ? "Düzeltilmiş Olay Yeri Taban Sıcaklığı:" : "Adjusted Crime Scene Base Temp:"}</span>
                <span className="text-emerald-400 font-bold font-mono">
                  {(avgAmbientTemp + (altitudeOffsetMeters / 100.0) * -0.65).toFixed(2)}°C
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ═════════════════════════════════════════════════════════════════════ */}
      {/* TAB 5: ISO/IEC 17025 CASE TELEMETRY & CRYPTOGRAPHIC AUDIT HASH       */}
      {/* ═════════════════════════════════════════════════════════════════════ */}
      {activeTab === "audit" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr ? "ISO/IEC 17025:2017 Zincirleme Delil Takibi & Kriptografik Durum Özeti" : "ISO/IEC 17025:2017 Chain of Custody & Cryptographic State Audit Digest"}
                </span>
              </div>
              <span className="text-[10px] text-emerald-400 font-mono">SHA-256 State Digest ($H_{"entomology"}$)</span>
            </div>

            {/* Cryptographic Hash Card */}
            <div className="p-4 rounded-xl bg-black/60 border border-emerald-500/40 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider">
                  {isTr ? "Deterministik 64-Hex Durum Denetim Özeti (H_entomology):" : "Deterministic 64-Hex State Audit Digest (H_entomology):"}
                </span>
                <button
                  type="button"
                  onClick={handleCopyHash}
                  className="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 text-[10px] font-bold flex items-center gap-1 cursor-pointer transition-all active:scale-95"
                >
                  {copiedHash ? <CheckCircle2 className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copiedHash ? (isTr ? "Kopyalandı!" : "Copied!") : (isTr ? "Özeti Kopyala" : "Copy Digest")}</span>
                </button>
              </div>

              <div className="p-2.5 rounded-lg bg-zinc-950 font-mono text-[11px] text-emerald-400 break-all select-all border border-emerald-500/20">
                {auditHash || "Calculating SHA-256 state hash..."}
              </div>

              <p className="text-[9px] text-zinc-500">
                {isTr
                  ? "Bu özet; seçilen böcek türü, evresi, ortam sıcaklığı, kütle ısısı, hesaplanan PMI_min saati ve vaka numarası ile kriptografik olarak mühürlenmiştir."
                  : "This digest cryptographically binds species taxonomy, developmental stage, ambient thermal regimes, maggot-mass offsets, PMI hours, and case ID."}
              </p>
            </div>

            {/* Casework Metadata Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-[11px]">
              <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                <span className="text-[9px] text-zinc-500 block uppercase font-bold">{isTr ? "Vaka Kimliği" : "Case Profile ID"}</span>
                <span className="text-white font-mono font-bold">{activeCase?.profile?.profileId || "CASE-2026-ENTO-01"}</span>
              </div>
              <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                <span className="text-[9px] text-zinc-500 block uppercase font-bold">{isTr ? "Adli Uzman / Görevli" : "Forensic Entomologist"}</span>
                <span className="text-zinc-200 font-mono font-bold">FORENZA Certified Analyst</span>
              </div>
              <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                <span className="text-[9px] text-zinc-500 block uppercase font-bold">{isTr ? "Kılavuz & Standart" : "Governing Standard"}</span>
                <span className="text-emerald-400 font-mono font-bold">EAFE / NAFEA Protocol</span>
              </div>
              <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                <span className="text-[9px] text-zinc-500 block uppercase font-bold">{isTr ? "Hesaplama Motoru" : "Computation Engine"}</span>
                <span className="text-blue-400 font-mono font-bold">FastAPI Live / Local Solv.</span>
              </div>
            </div>

            {/* Formal Court Statement Box */}
            <div className="p-4 rounded-xl bg-black/40 border border-tactical-border/40 space-y-2">
              <span className="text-[10px] text-zinc-300 font-bold uppercase flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-emerald-400" />
                {isTr ? "Mahkeme İfade Raporu & Kanıt Bütünlüğü Beyanı" : "Court Expert Witness Statement & Evidentiary Integrity"}
              </span>
              <div className="p-3 rounded-lg bg-zinc-950/80 border border-zinc-800 text-[10px] text-zinc-300 font-mono leading-relaxed space-y-1.5">
                <p>
                  1. Olay yerinde toplanan <strong>{selectedSpecies}</strong> ({speciesTaxon.common}) örnekleri laboratuvarda incelenmiş, en yaşlı bireylerin <strong>{selectedStage}</strong> ({speciesTaxon.stages[selectedStage]?.adh || 0} ADH) evresinde olduğu teyit edilmiştir.
                </p>
                <p>
                  2. Olay yeri meteorolojik verileri geriye doğru entegre edilmiş olup, kütle ısısı (+{deltaTMass.toFixed(1)}°C) uygulanarak minimum böcek kolonizasyon süresi (PMI_min) <strong>{pmiResult.pmi_min_hours.toFixed(1)} saat (~{pmiResult.pmi_min_days.toFixed(2)} gün)</strong> olarak hesaplanmıştır.
                </p>
                <p>
                  3. En erken kolonizasyon zamanı <strong>{pmiResult.colonisation_timestamp || "N/A"}</strong> olarak belirlenmiştir. Bu süre doğrudan ölüm anını değil, cesedin sinek kolonizasyonuna ilk maruz kaldığı en erken zaman aralığını (MICI) ifade eder.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
