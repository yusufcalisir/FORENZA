"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Clock, Dna, Activity, Sliders, Layers, RefreshCw, Flame, Sun, Droplets, ShieldCheck, CheckCircle2 } from "lucide-react";
import AgeEstimationPanel from "./AgeEstimationPanel";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

interface TissueDeconvResult {
  top_predicted_tissue: string;
  top_tissue_probability: number;
  tissue_probabilities: Record<string, number>;
  lr_tissue: number;
  log10_lr_tissue: number;
  tdmr_loci_evaluated: number;
  deconvolution_method: string;
}

interface LifestyleResult {
  ahrr_methylation_beta: number;
  f2rl3_methylation_beta?: number;
  alppl2_methylation_beta?: number;
  smoking_score?: number;
  smoking_status: string;
  smoking_probability: number;
  estimated_pack_years: number;
  abcg1_methylation_beta?: number;
  cpt1a_methylation_beta?: number;
  srebf1_methylation_beta?: number;
  estimated_bmi?: number;
  bmi_category?: string;
  alcohol_index_score: number;
  alcohol_exposure_level: string;
  circadian_phase: string;
  estimated_tod_window: string;
  biomarker_panel: string;
}

interface TelomerePmiApiResult {
  telomere?: {
    relative_ts_ratio: number;
    estimated_telomere_age_years: number;
    telomere_age_group: string;
    annual_shortening_rate: number;
  };
  pmi?: {
    observed_cpg_beta: number;
    baseline_beta_0: number;
    decay_constant_lambda: number;
    accumulated_degree_hours: number;
    ambient_temperature_celsius: number;
    estimated_pmi_hours: number;
    estimated_pmi_days: number;
    pmi_confidence_interval_hours: [number, number];
  };
  mosaicism?: {
    mosaicism_index_m: number;
    mosaicism_classification: string;
    loci_evaluated: number;
    locus_deltas: Record<string, number>;
  };
  prosecutors_fallacy_shield: string;
}

interface BisulfiteQcApiResult {
  bisulfite_conversion_qc?: {
    conversion_efficiency_percent: number;
    qc_status: string;
    non_cpg_probes_evaluated: number;
    unmethylated_sum: number;
    methylated_sum: number;
    threshold_percent: number;
  };
  probe_calibration?: {
    total_probes_evaluated: number;
    probes_passed_qc: number;
    probes_filtered_out: number;
    calibrated_probes: Array<{
      probe_id: string;
      raw_beta: number;
      calibrated_beta: number;
      m_value: number;
      detection_p_value: number;
      qc_filter_passed: boolean;
      probe_design_type: string;
    }>;
  };
  prosecutors_fallacy_shield: string;
}

export default function ComprehensiveEpigenomicsPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeResearchTab, setActiveResearchTab] = useState<"clock" | "tissue" | "lifestyle" | "telomere_pmi" | "bisulfite_qc">("clock");

  // Tissue Deconvolution State (12 Diagnostic tDMR CpG Markers)
  const [tdmrBetas, setTdmrBetas] = useState<Record<string, number>>({
    cg09652652: 0.12,
    cg19406367: 0.15,
    cg17610929: 0.91,
    cg23521140: 0.85,
    cg26763284: 0.89,
    cg23576855: 0.84,
    cg00399818: 0.82,
    cg04382942: 0.88,
    cg11624633: 0.86,
    cg00854446: 0.82,
    cg18063373: 0.80,
    cg07823520: 0.90,
  });

  const tdmrLabels: Record<string, string> = {
    cg09652652: isTr ? "Endotelyal (cg09652652)" : "Endothelial (cg09652652)",
    cg19406367: isTr ? "Hematopoietik (cg19406367)" : "Hematopoietic (cg19406367)",
    cg17610929: isTr ? "Germ Hücresi (cg17610929)" : "Germ Cell (cg17610929)",
    cg23521140: "DACT1 (cg23521140)",
    cg26763284: "PRMT12 (cg26763284)",
    cg23576855: isTr ? "Oral Epitelyal (cg23576855)" : "Oral Epithelial (cg23576855)",
    cg00399818: isTr ? "Tükürük Bezi (cg00399818)" : "Salivary Gland (cg00399818)",
    cg04382942: isTr ? "Servikovajinal (cg04382942)" : "Cervicovaginal (cg04382942)",
    cg11624633: "MYO1G (cg11624633)",
    cg00854446: isTr ? "Endometriyal (cg00854446)" : "Endometrial (cg00854446)",
    cg18063373: isTr ? "Endometriyal Stroma (cg18063373)" : "Endometrial Stroma (cg18063373)",
    cg07823520: isTr ? "Epidermis (cg07823520)" : "Epidermis (cg07823520)",
  };

  const [deconvLoading, setDeconvLoading] = useState(false);
  const [deconvResult, setDeconvResult] = useState<TissueDeconvResult | null>({
    top_predicted_tissue: "BLOOD",
    top_tissue_probability: 0.9998,
    tissue_probabilities: {
      BLOOD: 0.9998,
      MENSTRUAL: 0.0002,
      SALIVA: 0.0000,
      VAGINAL: 0.0000,
      SKIN: 0.0000,
      SEMEN: 0.0000,
    },
    lr_tissue: 4999.0,
    log10_lr_tissue: 3.70,
    tdmr_loci_evaluated: 12,
    deconvolution_method: "Bayesian Quadratic Discriminant Analysis (QDA 12-tDMR Gaussian Mixture)"
  });

  // Lifestyle & Epigenetic Biomarkers State
  const [ahrrBeta, setAhrrBeta] = useState<number>(0.32);
  const [f2rl3Beta, setF2rl3Beta] = useState<number>(0.28);
  const [alppl2Beta, setAlppl2Beta] = useState<number>(0.30);
  const [abcg1Beta, setAbcg1Beta] = useState<number>(0.35);
  const [cpt1aBeta, setCpt1aBeta] = useState<number>(0.45);
  const [srebf1Beta, setSrebf1Beta] = useState<number>(0.30);
  const [slc6a3Beta, setSlc6a3Beta] = useState<number>(0.50);
  const [per2Beta, setPer2Beta] = useState<number>(0.40);
  const [bmal1Beta, setBmal1Beta] = useState<number>(0.60);

  const [lifestyleLoading, setLifestyleLoading] = useState(false);
  const [lifestyleResult, setLifestyleResult] = useState<LifestyleResult | null>({
    ahrr_methylation_beta: 0.32,
    f2rl3_methylation_beta: 0.28,
    alppl2_methylation_beta: 0.30,
    smoking_score: 6.12,
    smoking_status: "CURRENT_HEAVY_SMOKER",
    smoking_probability: 0.95,
    estimated_pack_years: 44.2,
    abcg1_methylation_beta: 0.35,
    cpt1a_methylation_beta: 0.45,
    srebf1_methylation_beta: 0.30,
    estimated_bmi: 24.4,
    bmi_category: "NORMAL_WEIGHT",
    alcohol_index_score: 0.0,
    alcohol_exposure_level: "LOW_OR_ABSTAINER",
    circadian_phase: "MATUTINAL_PEAK_MORNING",
    estimated_tod_window: "04:00 - 10:00 UTC",
    biomarker_panel: "AHRR + F2RL3 + ALPPL2 + ABCG1 + CPT1A + SREBF1 + SLC6A3 + PER2/BMAL1"
  });

  // Telomere & Post-Mortem Epigenetic Decay State (Module 19)
  const [tsRatio, setTsRatio] = useState<number>(1.10);
  const [observedPmiBeta, setObservedPmiBeta] = useState<number>(0.50);
  const [ambientTemp, setAmbientTemp] = useState<number>(20.0);
  const [telomereLoading, setTelomereLoading] = useState(false);
  const [telomereResult, setTelomereResult] = useState<TelomerePmiApiResult | null>({
    telomere: {
      relative_ts_ratio: 1.10,
      estimated_telomere_age_years: 37.6,
      telomere_age_group: "MIDDLE_AGED",
      annual_shortening_rate: 0.0085
    },
    pmi: {
      observed_cpg_beta: 0.50,
      baseline_beta_0: 0.85,
      decay_constant_lambda: 0.00045,
      accumulated_degree_hours: 1412.3,
      ambient_temperature_celsius: 20.0,
      estimated_pmi_hours: 70.6,
      estimated_pmi_days: 2.9,
      pmi_confidence_interval_hours: [60.0, 81.2]
    },
    mosaicism: {
      mosaicism_index_m: 0.0141,
      mosaicism_classification: "CLONAL_HOMOGENEITY",
      loci_evaluated: 2,
      locus_deltas: { cg16867657: 0.01, cg21572722: -0.01 }
    },
    prosecutors_fallacy_shield: "Telomere and PMI estimates quantify physiological aging and post-mortem thermal exposure (ADH)."
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const runDeconvolution = async () => {
    setDeconvLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/epigenetics/deconvolve-tissue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tdmr_methylation: tdmrBetas })
      });
      if (res.ok) {
        const data = await res.json();
        setDeconvResult(data);
      }
    } catch (e) {
      console.error("Tissue deconvolution failed:", e);
    } finally {
      setDeconvLoading(false);
    }
  };

  const runLifestyleAnalysis = async () => {
    setLifestyleLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/epigenetics/lifestyle-profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ahrr_cg05575921_beta: ahrrBeta,
          f2rl3_beta: f2rl3Beta,
          alppl2_beta: alppl2Beta,
          abcg1_beta: abcg1Beta,
          cpt1a_beta: cpt1aBeta,
          srebf1_beta: srebf1Beta,
          slc6a3_beta: slc6a3Beta,
          per2_beta: per2Beta,
          bmal1_beta: bmal1Beta,
        })
      });
      if (res.ok) {
        const data = await res.json();
        setLifestyleResult(data);
      }
    } catch (e) {
      console.error("Lifestyle epigenetics analysis failed:", e);
    } finally {
      setLifestyleLoading(false);
    }
  };

  const runTelomerePmiAnalysis = async () => {
    setTelomereLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/epigenetics/telomere-and-pmi`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ts_ratio: tsRatio,
          observed_pmi_beta: observedPmiBeta,
          ambient_temperature_celsius: ambientTemp,
          tissue1_betas: { cg16867657: 0.22, cg21572722: 0.20 },
          tissue2_betas: { cg16867657: 0.23, cg21572722: 0.21 },
        })
      });
      if (res.ok) {
        const data = await res.json();
        setTelomereResult(data);
      }
    } catch (e) {
      console.error("Telomere & PMI analysis failed:", e);
    } finally {
      setTelomereLoading(false);
    }
  };

  // Bisulfite QC & Probe Calibration State (Module 20)
  const [nonCpgMethylated, setNonCpgMethylated] = useState<number>(1.5);
  const [nonCpgUnmethylated, setNonCpgUnmethylated] = useState<number>(398.5);
  const [qcRawBeta, setQcRawBeta] = useState<number>(0.22);
  const [qcProbeType, setQcProbeType] = useState<"TYPE_I" | "TYPE_II">("TYPE_II");
  const [bisulfiteLoading, setBisulfiteLoading] = useState(false);
  const [bisulfiteResult, setBisulfiteResult] = useState<BisulfiteQcApiResult | null>({
    bisulfite_conversion_qc: {
      conversion_efficiency_percent: 99.62,
      qc_status: "PASSED_QC",
      non_cpg_probes_evaluated: 10,
      unmethylated_sum: 3985.0,
      methylated_sum: 15.0,
      threshold_percent: 99.0
    },
    probe_calibration: {
      total_probes_evaluated: 3,
      probes_passed_qc: 3,
      probes_filtered_out: 0,
      calibrated_probes: [
        { probe_id: "cg16867657", raw_beta: 0.22, calibrated_beta: 0.22, m_value: -1.8242, detection_p_value: 0.0005, qc_filter_passed: true, probe_design_type: "TYPE_I" },
        { probe_id: "cg21572722", raw_beta: 0.85, calibrated_beta: 0.855, m_value: 2.5583, detection_p_value: 0.0010, qc_filter_passed: true, probe_design_type: "TYPE_II" },
        { probe_id: "cg06639320", raw_beta: 0.18, calibrated_beta: 0.162, m_value: -2.3707, detection_p_value: 0.0020, qc_filter_passed: true, probe_design_type: "TYPE_II" },
      ]
    },
    prosecutors_fallacy_shield: "Complete bisulfite conversion (C_conv >= 99.0%) and detection P-value filtering (P_det <= 0.01) are mandatory forensic quality controls under ISO/IEC 17025."
  });

  const runBisulfiteQcAnalysis = async () => {
    setBisulfiteLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/epigenetics/bisulfite-qc-and-calibrate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          non_cpg_signals: [
            { methylated: nonCpgMethylated, unmethylated: nonCpgUnmethylated }
          ],
          probes: [
            { probe_id: "cg_target_locus", raw_beta: qcRawBeta, detection_p_value: 0.001, probe_design_type: qcProbeType },
            { probe_id: "cg16867657", raw_beta: 0.22, detection_p_value: 0.0005, probe_design_type: "TYPE_I" },
            { probe_id: "cg21572722", raw_beta: 0.85, detection_p_value: 0.0010, probe_design_type: "TYPE_II" },
          ]
        })
      });
      if (res.ok) {
        const data = await res.json();
        setBisulfiteResult(data);
      }
    } catch (e) {
      console.error("Bisulfite QC analysis failed:", e);
    } finally {
      setBisulfiteLoading(false);
    }
  };

  const getTissueLabel = (tissue: string) => {
    if (!isTr) return tissue;
    switch (tissue) {
      case "BLOOD": return "KAN";
      case "MENSTRUAL": return "MENSTRÜEL";
      case "SALIVA": return "TÜKÜRÜK";
      case "VAGINAL": return "VAJİNAL";
      case "SKIN": return "DERİ";
      case "SEMEN": return "MENİ";
      default: return tissue;
    }
  };

  const getSmokingLabel = (status: string) => {
    if (!isTr) return status.replace(/_/g, " ");
    switch (status) {
      case "CURRENT_HEAVY_SMOKER": return "AKTİF AĞIR SİGARA KULLANICISI";
      case "CURRENT_MODERATE_SMOKER": return "AKTİF ORTA DÜZEY SİGARA KULLANICISI";
      case "FORMER_SMOKER": return "ESKİ SİGARA KULLANICISI";
      case "NEVER_SMOKER": return "HİÇ SİGARA KULLANMAMIŞ";
      default: return status.replace(/_/g, " ");
    }
  };

  const getBmiLabel = (cat?: string) => {
    if (!cat) return "NORMAL";
    if (!isTr) return cat;
    switch (cat) {
      case "NORMAL_WEIGHT": return "NORMAL KİLO";
      case "OVERWEIGHT": return "FAZLA KİLOLU";
      case "OBESE": return "OBEZ";
      case "UNDERWEIGHT": return "DÜŞÜK KİLO";
      default: return cat;
    }
  };

  const getAlcoholLabel = (level: string) => {
    if (!isTr) return level;
    switch (level) {
      case "LOW_OR_ABSTAINER": return "DÜŞÜK VEYA KULLANMAYAN";
      case "MODERATE": return "ORTA DÜZEY";
      case "HIGH_EXPOSURE": return "YÜKSEK MARUZİYET";
      default: return level;
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl border border-purple-500/30 bg-purple-500/10 shadow-lg overflow-hidden">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-300">
            <Dna className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xs sm:text-sm font-bold tracking-widest text-tactical-text uppercase">
                {isTr ? "Adli Epigenomik & Biyolojik Durum İstihbaratı" : "Forensic Epigenomics & Biological State Intelligence"}
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 whitespace-nowrap">
                {isTr ? "ÇOKLU OMİK EPİGENETİK" : "MULTI-OMICS EPIGENETICS"}
              </span>
            </div>
            <p className="text-[9px] sm:text-[10px] text-zinc-400 mt-0.5 truncate">
              {isTr
                ? "DNA Metilasyonu • Epigenetik Yaş Saati • Doku Dekonvolüsyonu • AHRR Yaşam Tarzı Profili"
                : "DNA Methylation • Epigenetic Clock • Tissue Deconvolution • AHRR Lifestyle Profiling"}
            </p>
          </div>
        </div>

        {/* Inner Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 p-1 rounded-xl bg-black/60 border border-tactical-border/60 shrink-0">
          <button
            onClick={() => setActiveResearchTab("clock")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
              activeResearchTab === "clock"
                ? "bg-purple-500 text-black shadow-md font-extrabold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {isTr ? "Epigenetik Yaş Saati" : "Epigenetic Clock"}
          </button>
          <button
            onClick={() => setActiveResearchTab("tissue")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
              activeResearchTab === "tissue"
                ? "bg-purple-500 text-black shadow-md font-extrabold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {isTr ? "Doku Dekonvolüsyonu" : "Tissue Deconvolution"}
          </button>
          <button
            onClick={() => setActiveResearchTab("lifestyle")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
              activeResearchTab === "lifestyle"
                ? "bg-purple-500 text-black shadow-md font-extrabold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {isTr ? "Yaşam Tarzı & Çevre" : "Lifestyle & Environment"}
          </button>
          <button
            onClick={() => setActiveResearchTab("telomere_pmi")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
              activeResearchTab === "telomere_pmi"
                ? "bg-purple-500 text-black shadow-md font-extrabold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {isTr ? "Telomer & PMI Bozunumu" : "Telomere & PMI Decay"}
          </button>
          <button
            onClick={() => setActiveResearchTab("bisulfite_qc")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
              activeResearchTab === "bisulfite_qc"
                ? "bg-purple-500 text-black shadow-md font-extrabold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {isTr ? "Bisülfit Kalite Kontrol" : "Bisulfite QC"}
          </button>
        </div>
      </div>

      {/* ── Tab Content ── */}
      {activeResearchTab === "clock" && <AgeEstimationPanel />}

      {activeResearchTab === "tissue" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr ? "tDMR Metilasyon Beta Değerleri" : "tDMR Methylation Beta Inputs"}
                </span>
              </div>
              <button
                onClick={runDeconvolution}
                disabled={deconvLoading}
                className="px-3 py-1 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 font-bold text-[10px] uppercase transition-all flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${deconvLoading ? "animate-spin" : ""}`} />
                {isTr ? "Dekonvolüe Et" : "Deconvolve"}
              </button>
            </div>

            <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
              {Object.entries(tdmrBetas).map(([locus, val]) => (
                <div key={locus} className="space-y-1">
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-bold text-zinc-300 truncate max-w-[170px]">{tdmrLabels[locus] || locus}</span>
                    <span className="font-mono text-purple-400 font-bold">β = {val.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.01"
                    value={val}
                    onChange={(e) => setTdmrBetas((prev) => ({ ...prev, [locus]: parseFloat(e.target.value) }))}
                    className="w-full accent-purple-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Results Display */}
          <div className="lg:col-span-2 space-y-6">
            {deconvResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                {/* Primary Verdict Card */}
                <div className="rounded-2xl border border-purple-500/40 bg-gradient-to-br from-purple-500/10 via-tactical-surface/60 to-black/80 p-6 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-purple-500/20 pb-4">
                    <div>
                      <span className="text-[10px] font-bold text-purple-300 uppercase tracking-widest block">
                        {isTr ? "TAHMİN EDİLEN DOKU KÖKENİ" : "PREDICTED TISSUE ORIGIN"}
                      </span>
                      <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-teal-300 to-emerald-300 font-mono">
                        {getTissueLabel(deconvResult.top_predicted_tissue)}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "Doku Olabilirlik Oranı (LR)" : "Tissue LR (LR_tissue)"}
                      </span>
                      <span className="text-xl font-bold text-emerald-400 font-mono">
                        {deconvResult.lr_tissue} (10^{deconvResult.log10_lr_tissue})
                      </span>
                    </div>
                  </div>

                  {/* Probability Distribution Bar */}
                  <div className="space-y-3 pt-2">
                    <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">
                      {isTr ? "Dirichlet Karışım Doku Dağılımı" : "Dirichlet Mixture Tissue Distribution"}
                    </span>
                    <div className="space-y-2">
                      {Object.entries(deconvResult.tissue_probabilities).map(([tissue, prob]) => (
                        <div key={tissue} className="space-y-1">
                          <div className="flex items-center justify-between text-xs font-mono">
                            <span className="font-bold text-zinc-300">{getTissueLabel(tissue)}</span>
                            <span className="text-purple-300 font-bold">{(prob * 100).toFixed(1)}%</span>
                          </div>
                          <div className="h-2 w-full rounded-full bg-black/60 overflow-hidden border border-tactical-border/40">
                            <div
                              className="h-full bg-gradient-to-r from-purple-500 to-teal-400 rounded-full transition-all duration-500"
                              style={{ width: `${prob * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {activeResearchTab === "lifestyle" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Flame className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr ? "Yaşam Tarzı & VKİ Biyobelirteçleri" : "Lifestyle & BMI Biomarkers"}
                </span>
              </div>
              <button
                onClick={runLifestyleAnalysis}
                disabled={lifestyleLoading}
                className="px-3 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-bold text-[10px] uppercase transition-all flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${lifestyleLoading ? "animate-spin" : ""}`} />
                {isTr ? "Analiz Et" : "Analyze"}
              </button>
            </div>

            <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
              {/* Smoking Section */}
              <div className="text-[10px] font-bold text-amber-400 uppercase border-b border-tactical-border/30 pb-1">
                {isTr ? "Sigara Belirteçleri (AHRR / F2RL3 / ALPPL2)" : "Smoking Markers (AHRR / F2RL3 / ALPPL2)"}
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">AHRR (cg05575921)</span>
                  <span className="font-mono text-amber-400 font-bold">β = {ahrrBeta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={ahrrBeta}
                  onChange={(e) => setAhrrBeta(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">F2RL3 (cg03636183)</span>
                  <span className="font-mono text-amber-400 font-bold">β = {f2rl3Beta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={f2rl3Beta}
                  onChange={(e) => setF2rl3Beta(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">ALPPL2 (cg01940273)</span>
                  <span className="font-mono text-amber-400 font-bold">β = {alppl2Beta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={alppl2Beta}
                  onChange={(e) => setAlppl2Beta(parseFloat(e.target.value))}
                  className="w-full accent-amber-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>

              {/* BMI Section */}
              <div className="text-[10px] font-bold text-teal-400 uppercase border-b border-tactical-border/30 pb-1 pt-2">
                {isTr ? "Epigenetik VKİ (ABCG1 / CPT1A / SREBF1)" : "Epigenetic BMI (ABCG1 / CPT1A / SREBF1)"}
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">ABCG1 (cg06500161)</span>
                  <span className="font-mono text-teal-400 font-bold">β = {abcg1Beta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={abcg1Beta}
                  onChange={(e) => setAbcg1Beta(parseFloat(e.target.value))}
                  className="w-full accent-teal-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">CPT1A (cg00574958)</span>
                  <span className="font-mono text-teal-400 font-bold">β = {cpt1aBeta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={cpt1aBeta}
                  onChange={(e) => setCpt1aBeta(parseFloat(e.target.value))}
                  className="w-full accent-teal-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">SREBF1 (cg11024682)</span>
                  <span className="font-mono text-teal-400 font-bold">β = {srebf1Beta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={srebf1Beta}
                  onChange={(e) => setSrebf1Beta(parseFloat(e.target.value))}
                  className="w-full accent-teal-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
            </div>
          </div>

          {/* Results Display */}
          <div className="lg:col-span-2 space-y-6">
            {lifestyleResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                <div className="rounded-2xl border border-amber-500/40 bg-gradient-to-br from-amber-500/10 via-tactical-surface/60 to-black/80 p-6 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-amber-500/20 pb-4">
                    <div>
                      <span className="text-[10px] font-bold text-amber-300 uppercase tracking-widest block">
                        {isTr ? "EPİGENETİK SİGARA BİYOBELİRTEÇ DURUMU" : "EPIGENETIC SMOKING BIOMARKER STATUS"}
                      </span>
                      <span className="text-2xl font-black text-amber-300 font-mono">
                        {getSmokingLabel(lifestyleResult.smoking_status)}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "Olasılık" : "Probability"}
                      </span>
                      <span className="text-lg font-bold text-emerald-400 font-mono">
                        {(lifestyleResult.smoking_probability * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-2">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Sigara Skoru" : "Smoking Score"}
                      </span>
                      <span className="font-bold text-amber-300 font-mono">{lifestyleResult.smoking_score ?? "N/A"}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Tahmini Paket-Yıl" : "Est. Pack Years"}
                      </span>
                      <span className="font-bold text-amber-300 font-mono">{lifestyleResult.estimated_pack_years} {isTr ? "Yıl" : "Yrs"}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Epigenetik VKİ" : "Epigenetic BMI"}
                      </span>
                      <span className="font-bold text-teal-300 font-mono">{lifestyleResult.estimated_bmi ?? 24.4} kg/m²</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "VKİ Kategorisi" : "BMI Category"}
                      </span>
                      <span className="font-bold text-teal-300 font-mono">{getBmiLabel(lifestyleResult.bmi_category)}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-2">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Alkol Maruziyet Düzeyi" : "Alcohol Exposure Level"}
                      </span>
                      <span className="font-bold text-cyan-300 font-mono">{getAlcoholLabel(lifestyleResult.alcohol_exposure_level)}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Sirkadiyen Zaman Penceresi" : "Circadian TOD Window"}
                      </span>
                      <span className="font-bold text-purple-300 font-mono">{lifestyleResult.estimated_tod_window}</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {activeResearchTab === "telomere_pmi" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr ? "Telomer & PMI Kinetiği" : "Telomere & PMI Kinetics"}
                </span>
              </div>
              <button
                onClick={runTelomerePmiAnalysis}
                disabled={telomereLoading}
                className="px-3 py-1 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 font-bold text-[10px] uppercase transition-all flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${telomereLoading ? "animate-spin" : ""}`} />
                {isTr ? "Analiz Et" : "Analyze"}
              </button>
            </div>

            <div className="space-y-4">
              {/* Telomere Section */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">
                    {isTr ? "Göreceli Telomer Uzunluğu (T/S)" : "Relative Telomere Length (T/S)"}
                  </span>
                  <span className="font-mono text-cyan-400 font-bold">{tsRatio.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.40"
                  max="1.60"
                  step="0.01"
                  value={tsRatio}
                  onChange={(e) => setTsRatio(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
                <span className="text-[9px] text-zinc-500 block">
                  {isTr
                    ? "T/S = 1.420 - 0.0085 • Yaş (Doğum: ~1.42, 50 Yaş: ~1.00)"
                    : "T/S = 1.420 - 0.0085 • Age (Birth: ~1.42, 50 Yrs: ~1.00)"}
                </span>
              </div>

              {/* PMI Section */}
              <div className="space-y-1 pt-2 border-t border-tactical-border/30">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">
                    {isTr ? "Artık CpG Metilasyonu (β)" : "Residual CpG Methylation (β)"}
                  </span>
                  <span className="font-mono text-cyan-400 font-bold">{observedPmiBeta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.85"
                  step="0.01"
                  value={observedPmiBeta}
                  onChange={(e) => setObservedPmiBeta(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>

              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">
                    {isTr ? "Ortam Sıcaklığı" : "Ambient Temperature"}
                  </span>
                  <span className="font-mono text-cyan-400 font-bold">{ambientTemp.toFixed(1)} °C</span>
                </div>
                <input
                  type="range"
                  min="4.0"
                  max="35.0"
                  step="0.5"
                  value={ambientTemp}
                  onChange={(e) => setAmbientTemp(parseFloat(e.target.value))}
                  className="w-full accent-cyan-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
            </div>
          </div>

          {/* Results Display */}
          <div className="lg:col-span-2 space-y-6">
            {telomereResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                <div className="rounded-2xl border border-cyan-500/40 bg-gradient-to-br from-cyan-500/10 via-tactical-surface/60 to-black/80 p-6 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-cyan-500/20 pb-4">
                    <div>
                      <span className="text-[10px] font-bold text-cyan-300 uppercase tracking-widest block">
                        {isTr ? "TAHMİN EDİLEN TELOMER BİYOLOJİK YAŞI" : "ESTIMATED TELOMERE BIOLOGICAL AGE"}
                      </span>
                      <span className="text-2xl font-black text-cyan-300 font-mono">
                        {telomereResult.telomere?.estimated_telomere_age_years.toFixed(1)} {isTr ? "Yaş" : "Years"}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "Yaş Grubu" : "Age Group"}
                      </span>
                      <span className="text-sm font-bold text-emerald-400 font-mono">
                        {isTr
                          ? (telomereResult.telomere?.telomere_age_group === "MIDDLE_AGED" ? "ORTA YAŞLI"
                            : telomereResult.telomere?.telomere_age_group === "YOUNG_ADULT" ? "GENÇ YETİŞKİN"
                            : telomereResult.telomere?.telomere_age_group === "ELDERLY" ? "YAŞLI"
                            : telomereResult.telomere?.telomere_age_group)
                          : telomereResult.telomere?.telomere_age_group}
                      </span>
                    </div>
                  </div>

                  {/* PMI Card */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-2">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Tahmini PMI" : "Est. PMI"}
                      </span>
                      <span className="font-bold text-cyan-300 font-mono">{telomereResult.pmi?.estimated_pmi_hours} {isTr ? "Saat" : "Hrs"}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "PMI (Gün)" : "PMI (Days)"}
                      </span>
                      <span className="font-bold text-cyan-300 font-mono">{telomereResult.pmi?.estimated_pmi_days} {isTr ? "Gün" : "Days"}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Birikmiş ADH" : "Accumulated ADH"}
                      </span>
                      <span className="font-bold text-amber-300 font-mono">{telomereResult.pmi?.accumulated_degree_hours} ADH</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">
                        {isTr ? "Somatik Mozaiklik" : "Somatic Mosaicism"}
                      </span>
                      <span className="font-bold text-purple-300 font-mono">
                        {isTr && telomereResult.mosaicism?.mosaicism_classification === "CLONAL_HOMOGENEITY"
                          ? "KLONAL HOMOJENLİK"
                          : telomereResult.mosaicism?.mosaicism_classification}
                      </span>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    {isTr
                      ? "Telomer ve PMI tahminleri fizyolojik yaşlanmayı ve ölüm sonrası termal maruziyeti (ADH) ölçer."
                      : telomereResult.prosecutors_fallacy_shield}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {activeResearchTab === "bisulfite_qc" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  {isTr ? "Bisülfit Kalite Kontrol & BMIQ Kontrolleri" : "Bisulfite QC & BMIQ Controls"}
                </span>
              </div>
              <button
                onClick={runBisulfiteQcAnalysis}
                disabled={bisulfiteLoading}
                className="px-3 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 font-bold text-[10px] uppercase transition-all flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${bisulfiteLoading ? "animate-spin" : ""}`} />
                {isTr ? "Kaliteyi Çalıştır" : "Run QC"}
              </button>
            </div>

            <div className="space-y-3">
              <div className="text-[10px] font-bold text-emerald-400 uppercase border-b border-tactical-border/30 pb-1">
                {isTr ? "CpG-Dışı Sitozin Kontrol Sinyalleri" : "Non-CpG Cytosine Control Signals"}
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">
                    {isTr ? "Metillenmemiş Şiddet (U)" : "Unmethylated Intensity (U)"}
                  </span>
                  <span className="font-mono text-emerald-400 font-bold">{nonCpgUnmethylated.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="100.0"
                  max="1000.0"
                  step="1.0"
                  value={nonCpgUnmethylated}
                  onChange={(e) => setNonCpgUnmethylated(parseFloat(e.target.value))}
                  className="w-full accent-emerald-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">
                    {isTr ? "Metillenmiş Şiddet (M - Dönüştürülmemiş)" : "Methylated Intensity (M - Unconverted)"}
                  </span>
                  <span className="font-mono text-rose-400 font-bold">{nonCpgMethylated.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="50.0"
                  step="0.5"
                  value={nonCpgMethylated}
                  onChange={(e) => setNonCpgMethylated(parseFloat(e.target.value))}
                  className="w-full accent-rose-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
                <span className="text-[9px] text-zinc-500 block">
                  C_conv = (1 - M/(M+U)) * 100% ({isTr ? "Adli eşik" : "Forensic threshold"} &ge; 99.0%)
                </span>
              </div>

              <div className="text-[10px] font-bold text-purple-400 uppercase border-b border-tactical-border/30 pb-1 pt-2">
                {isTr ? "Prob Kalibrasyonu & Prob Tasarım Türü" : "Probe Calibration & Probe Design Type"}
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-bold text-zinc-300">
                    {isTr ? "Örnek CpG Ham Beta" : "Sample CpG Raw Beta"}
                  </span>
                  <span className="font-mono text-purple-400 font-bold">{qcRawBeta.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  value={qcRawBeta}
                  onChange={(e) => setQcRawBeta(parseFloat(e.target.value))}
                  className="w-full accent-purple-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                />
              </div>
              <div className="flex items-center gap-2 pt-1">
                <button
                  onClick={() => setQcProbeType("TYPE_I")}
                  className={`flex-1 py-1 rounded text-[10px] font-bold cursor-pointer ${
                    qcProbeType === "TYPE_I" ? "bg-purple-500 text-black" : "bg-black/40 text-zinc-400 border border-tactical-border/40"
                  }`}
                >
                  {isTr ? "Tip I (Referans)" : "Type I (Reference)"}
                </button>
                <button
                  onClick={() => setQcProbeType("TYPE_II")}
                  className={`flex-1 py-1 rounded text-[10px] font-bold cursor-pointer ${
                    qcProbeType === "TYPE_II" ? "bg-purple-500 text-black" : "bg-black/40 text-zinc-400 border border-tactical-border/40"
                  }`}
                >
                  {isTr ? "Tip II (BMIQ Hedef)" : "Type II (BMIQ Target)"}
                </button>
              </div>
            </div>
          </div>

          {/* Results Display */}
          <div className="lg:col-span-2 space-y-6">
            {bisulfiteResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                <div className="rounded-2xl border border-emerald-500/40 bg-gradient-to-br from-emerald-500/10 via-tactical-surface/60 to-black/80 p-6 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-emerald-500/20 pb-4">
                    <div>
                      <span className="text-[10px] font-bold text-emerald-300 uppercase tracking-widest block">
                        {isTr ? "BİSÜLFİT DÖNÜŞÜM VERİMLİLİĞİ KALİTE KONTROLÜ" : "BISULFITE CONVERSION EFFICIENCY QUALITY CONTROL"}
                      </span>
                      <span className="text-2xl font-black text-emerald-300 font-mono">
                        {bisulfiteResult.bisulfite_conversion_qc?.conversion_efficiency_percent.toFixed(2)}%
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "Adli Kalite Kontrol Durumu" : "Forensic QC Status"}
                      </span>
                      <span className={`text-sm font-bold font-mono px-2 py-0.5 rounded border ${
                        bisulfiteResult.bisulfite_conversion_qc?.qc_status === "PASSED_QC"
                          ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                          : "bg-rose-500/20 text-rose-300 border-rose-500/40"
                      }`}>
                        {isTr && bisulfiteResult.bisulfite_conversion_qc?.qc_status === "PASSED_QC" ? "KK GEÇTİ" : bisulfiteResult.bisulfite_conversion_qc?.qc_status}
                      </span>
                    </div>
                  </div>

                  {/* Calibration Grid */}
                  <div className="space-y-2 pt-2">
                    <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">
                      {isTr ? "BMIQ Kalibre Edilmiş CpG Probları & M-Değeri Dönüşümleri" : "BMIQ Calibrated CpG Probes & M-Value Transformations"}
                    </span>
                    <div className="space-y-1.5 max-h-[160px] overflow-y-auto pr-1">
                      {bisulfiteResult.probe_calibration?.calibrated_probes.map((probe) => (
                        <div key={probe.probe_id} className="flex items-center justify-between p-2 rounded-lg bg-black/40 border border-tactical-border/40 text-[11px] font-mono">
                          <div>
                            <span className="font-bold text-zinc-200">{probe.probe_id}</span>
                            <span className="ml-2 text-[9px] text-zinc-500">{probe.probe_design_type}</span>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className="text-zinc-400">{isTr ? "Ham" : "Raw"} β: {probe.raw_beta.toFixed(2)}</span>
                            <span className="text-emerald-300 font-bold">{isTr ? "Kalibre" : "Calibrated"} β: {probe.calibrated_beta.toFixed(3)}</span>
                            <span className="text-purple-300">M: {probe.m_value.toFixed(2)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    {isTr
                      ? "Tam bisülfit dönüşümü (C_conv >= %99.0) ve saptama P-değeri filtrelemesi (P_det <= 0.01), ISO/IEC 17025 kapsamında zorunlu adli kalite kontrolleridir."
                      : bisulfiteResult.prosecutors_fallacy_shield}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

