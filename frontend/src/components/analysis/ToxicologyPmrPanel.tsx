"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Pill, Activity, ShieldCheck, RefreshCw, AlertTriangle, CheckCircle2, Clock, Zap, ArrowRight, Info, Cpu, Check } from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

interface PmrResponse {
  compound_name: string;
  c_heart: number;
  c_femoral: number;
  unit: string;
  cp_observed: number;
  cp_literature_mean: number;
  vd_l_kg: number;
  pmr_risk_tier: string;
  is_cardiac_overestimated: boolean;
  overestimation_percentage: number;
  clinical_guideline: string;
  alert_message: string;
  prosecutors_fallacy_shield: string;
}

interface ExtrapolationResponse {
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
}

const DRUG_PRESETS = [
  { name: "Fentanyl", cHeart: 14.0, cFem: 5.0, unit: "µg/L", vd: 5.0, tHalf: 7.0, risk: "High / Severe", risk_tr: "Yüksek / Şiddetli" },
  { name: "Ethanol", cHeart: 0.85, cFem: 0.80, unit: "g/L", vd: 0.6, tHalf: null, risk: "Low / Minimal", risk_tr: "Düşük / Minimal" },
  { name: "Morphine", cHeart: 0.36, cFem: 0.20, unit: "mg/L", vd: 3.5, tHalf: 3.0, risk: "Moderate", risk_tr: "Orta Düzey" },
  { name: "Methamphetamine", cHeart: 0.84, cFem: 0.40, unit: "mg/L", vd: 4.0, tHalf: 10.0, risk: "High", risk_tr: "Yüksek" },
  { name: "Amitriptyline", cHeart: 4.50, cFem: 1.00, unit: "mg/L", vd: 20.0, tHalf: 21.0, risk: "Very High", risk_tr: "Çok Yüksek" },
  { name: "Acetaminophen", cHeart: 10.5, cFem: 10.0, unit: "mg/L", vd: 0.9, tHalf: 2.5, risk: "Low", risk_tr: "Düşük" },
];

export default function ToxicologyPmrPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeTab, setActiveTab] = useState<"pmr" | "extrap">("pmr");
  const [selectedDrug, setSelectedDrug] = useState<string>("Fentanyl");
  const [cHeart, setCHeart] = useState<number>(14.0);
  const [cFemoral, setCFemoral] = useState<number>(5.0);
  const [unit, setUnit] = useState<string>("µg/L");
  const [elapsedHours, setElapsedHours] = useState<number>(7.0);
  const [loading, setLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [stageText, setStageText] = useState<string>("");
  const [lastActionTime, setLastActionTime] = useState<string | null>(null);

  const [pmrResult, setPmrResult] = useState<PmrResponse | null>({
    compound_name: "Fentanyl",
    c_heart: 14.0,
    c_femoral: 5.0,
    unit: "µg/L",
    cp_observed: 2.8,
    cp_literature_mean: 2.8,
    vd_l_kg: 5.0,
    pmr_risk_tier: "High / Severe",
    is_cardiac_overestimated: true,
    overestimation_percentage: 180.0,
    clinical_guideline: "Pronounced post-mortem lung-to-heart diffusion; femoral venous blood mandatory.",
    alert_message: "HIGH PMR OVERESTIMATION ALERT: Heart blood concentration (14.0 µg/L) is 180.0% higher than peripheral femoral blood (5.0 µg/L).",
    prosecutors_fallacy_shield: "Post-mortem cardiac blood concentrations cannot be directly translated to antemortem intoxication levels (SOFT / TIAFT Guidelines)."
  });

  const [extrapResult, setExtrapResult] = useState<ExtrapolationResponse | null>({
    compound_name: "Fentanyl",
    c_femoral_postmortem: 5.0,
    elapsed_hours: 7.0,
    c_antemortem_extrapolated: 10.0,
    unit: "µg/L",
    elimination_type: "First-Order",
    elimination_rate_constant_ke_h: 0.09902,
    half_life_hours: 7.0,
    beta_60_g_l_h: null,
    kinetic_formula: "First-Order: C_antemortem = C_femoral * exp(0.09902 * 7.0h)",
    prosecutors_fallacy_shield: "Antemortem back-extrapolation assumes linear or exponential clearance in an uncompromised circulatory system (SOFT / TIAFT)."
  });

  // Client-side fallback for PMR Evaluation
  const evaluateClientPmr = (drug: string, heart: number, fem: number, u: string): PmrResponse => {
    const cp = Number((heart / Math.max(0.001, fem)).toFixed(2));
    const isOver = cp > 1.2;
    const overPct = Number((((heart - fem) / fem) * 100).toFixed(1));
    const preset = DRUG_PRESETS.find((d) => d.name === drug) || DRUG_PRESETS[0];

    return {
      compound_name: drug,
      c_heart: heart,
      c_femoral: fem,
      unit: u,
      cp_observed: cp,
      cp_literature_mean: cp,
      vd_l_kg: preset.vd,
      pmr_risk_tier: isTr ? preset.risk_tr : preset.risk,
      is_cardiac_overestimated: isOver,
      overestimation_percentage: Math.max(0, overPct),
      clinical_guideline: isOver
        ? (isTr ? "Belirgin ölüm sonrası akciğer-kalp difüzyonu; femoral periferik kan zorunludur." : "Pronounced post-mortem lung-to-heart diffusion; femoral venous blood mandatory.")
        : (isTr ? "İhmal edilebilir yeniden dağılım etkisi." : "Negligible redistribution artifact."),
      alert_message: isOver
        ? (isTr
            ? `YÜKSEK PMR FAZLA TAHMİN UYARISI: Kalp kanı konsantrasyonu (${heart} ${u}), periferik femoral kandan (${fem} ${u}) %${overPct} daha yüksektir.`
            : `PMR OVERESTIMATION ALERT: Heart blood concentration (${heart} ${u}) is ${overPct}% higher than peripheral femoral blood (${fem} ${u}).`)
        : (isTr ? `PMR normal denge sınırları içerisinde (C/P = ${cp}).` : `PMR within normal equilibrium limits (C/P = ${cp}).`),
      prosecutors_fallacy_shield: isTr
        ? "Ölüm sonrası kardiyak kan konsantrasyonları doğrudan ölüm öncesi intoksikasyon seviyelerine çevrilemez (SOFT / TIAFT Kılavuzları)."
        : "Post-mortem cardiac blood concentrations cannot be directly translated to antemortem intoxication levels (SOFT / TIAFT Guidelines)."
    };
  };

  // Client-side fallback for Antemortem Extrapolation
  const evaluateClientExtrap = (drug: string, fem: number, hours: number, u: string): ExtrapolationResponse => {
    const preset = DRUG_PRESETS.find((d) => d.name === drug) || DRUG_PRESETS[0];
    if (drug === "Ethanol") {
      const beta60 = 0.15; // g/L/h
      const cAntemortem = Number((fem + beta60 * hours).toFixed(2));
      return {
        compound_name: drug,
        c_femoral_postmortem: fem,
        elapsed_hours: hours,
        c_antemortem_extrapolated: cAntemortem,
        unit: u,
        elimination_type: isTr ? "Sıfırıncı Derece (Widmark)" : "Zero-Order (Widmark)",
        elimination_rate_constant_ke_h: null,
        half_life_hours: null,
        beta_60_g_l_h: beta60,
        kinetic_formula: `Zero-Order: C_0 = ${fem} + (${beta60} × ${hours}h)`,
        prosecutors_fallacy_shield: isTr
          ? "Ölüm öncesi geriye ekstrapolasyon, sağlam bir dolaşım sisteminde doğrusal atılım varsayar (SOFT / TIAFT)."
          : "Antemortem back-extrapolation assumes linear clearance in an uncompromised circulatory system (SOFT / TIAFT)."
      };
    } else {
      const tHalf = preset.tHalf || 6.0;
      const ke = Math.log(2) / tHalf;
      const cAntemortem = Number((fem * Math.exp(ke * hours)).toFixed(2));
      return {
        compound_name: drug,
        c_femoral_postmortem: fem,
        elapsed_hours: hours,
        c_antemortem_extrapolated: cAntemortem,
        unit: u,
        elimination_type: isTr ? "Birinci Derece Eliminasyon" : "First-Order Elimination",
        elimination_rate_constant_ke_h: Number(ke.toFixed(5)),
        half_life_hours: tHalf,
        beta_60_g_l_h: null,
        kinetic_formula: `First-Order: C_0 = ${fem} × exp(${ke.toFixed(4)} × ${hours}h)`,
        prosecutors_fallacy_shield: isTr
          ? "Ölüm öncesi geriye ekstrapolasyon birinci derece üstel atılım varsayar (SOFT / TIAFT)."
          : "Antemortem back-extrapolation assumes first-order exponential clearance (SOFT / TIAFT)."
      };
    }
  };

  const loadPreset = (preset: typeof DRUG_PRESETS[0]) => {
    setSelectedDrug(preset.name);
    setCHeart(preset.cHeart);
    setCFemoral(preset.cFem);
    setUnit(preset.unit);
    runPmrEvaluation(preset.name, preset.cHeart, preset.cFem, preset.unit);
    runExtrapolation(preset.name, preset.cFem, elapsedHours, preset.unit);
  };

  const runPmrEvaluation = async (drug: string, heart: number, fem: number, u: string) => {
    if (loading) return;
    setLoading(true);
    setProgress(15);
    setStageText(
      isTr
        ? `Kardiyak (${heart}) ile femoral (${fem}) konsantrasyonları karşılaştırılıyor...`
        : `Comparing cardiac (${heart}) vs femoral (${fem}) concentrations...`
    );

    const API_BASE = getApiBaseUrl();

    const t1 = setTimeout(() => {
      setProgress(50);
      setStageText(
        isTr
          ? "Merkezi-periferik oranı (C_heart / C_femoral) hesaplanıyor..."
          : "Calculating central-to-peripheral ratio (C_heart / C_femoral)..."
      );
    }, 250);

    const t2 = setTimeout(() => {
      setProgress(85);
      setStageText(
        isTr
          ? "Görünür dağılım hacmi V_d karşısında ölüm sonrası yeniden dağılım riski değerlendiriliyor..."
          : "Evaluating post-mortem redistribution risk against apparent volume of distribution V_d..."
      );
    }, 550);

    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/toxicology-pmr-evaluation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          compound_name: drug,
          c_heart: heart,
          c_femoral: fem,
          unit: u
        }),
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) {
        const data = await res.json();
        setPmrResult(data);
      } else {
        setPmrResult(evaluateClientPmr(drug, heart, fem, u));
      }
    } catch {
      setPmrResult(evaluateClientPmr(drug, heart, fem, u));
    } finally {
      setTimeout(() => {
        clearTimeout(t1);
        clearTimeout(t2);
        setProgress(100);
        setStageText(isTr ? "PMR yeniden dağılım değerlendirmesi tamamlandı." : "PMR redistribution evaluation complete.");
        setTimeout(() => {
          setLoading(false);
          setLastActionTime(isTr ? `PMR ${new Date().toLocaleTimeString()} değerlendirildi` : `PMR Evaluated at ${new Date().toLocaleTimeString()}`);
        }, 200);
      }, 850);
    }
  };

  const runExtrapolation = async (drug: string, fem: number, hours: number, u: string) => {
    if (loading) return;
    setLoading(true);
    setProgress(15);
    setStageText(
      isTr
        ? "Toksikokinetik klirens modeli seçiliyor (Sıfırıncı Derece Widmark veya Birinci Derece)..."
        : "Selecting toxicokinetic clearance model (Zero-Order Widmark vs First-Order)..."
    );

    const API_BASE = getApiBaseUrl();

    const t1 = setTimeout(() => {
      setProgress(50);
      setStageText(
        isTr
          ? "Geçen süre boyunca atılım hız sabiti (k_e = ln(2)/t_1/2) entegre ediliyor..."
          : "Integrating elimination rate constant (k_e = ln(2)/t_1/2) over elapsed hours..."
      );
    }, 250);

    const t2 = setTimeout(() => {
      setProgress(85);
      setStageText(
        isTr
          ? "Ölüm anındaki antemortem konsantrasyon C_0 hesaplanıyor..."
          : "Calculating antemortem concentration at time of death C_0..."
      );
    }, 550);

    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/toxicology-antemortem-extrapolation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          compound_name: drug,
          c_femoral: fem,
          elapsed_hours: hours,
          unit: u
        }),
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) {
        const data = await res.json();
        setExtrapResult(data);
      } else {
        setExtrapResult(evaluateClientExtrap(drug, fem, hours, u));
      }
    } catch {
      setExtrapResult(evaluateClientExtrap(drug, fem, hours, u));
    } finally {
      setTimeout(() => {
        clearTimeout(t1);
        clearTimeout(t2);
        setProgress(100);
        setStageText(isTr ? "Antemortem toksikokinetik ekstrapolasyon tamamlandı." : "Antemortem toxicokinetic extrapolation complete.");
        setTimeout(() => {
          setLoading(false);
          setLastActionTime(isTr ? `${new Date().toLocaleTimeString()} ekstrapole edildi` : `Extrapolated at ${new Date().toLocaleTimeString()}`);
        }, 200);
      }, 850);
    }
  };

  const getPmrRiskLabel = (tier: string) => {
    if (!isTr) return tier;
    if (tier.includes("High / Severe") || tier.includes("Yüksek / Şiddetli")) return "Yüksek / Şiddetli";
    if (tier.includes("Low / Minimal") || tier.includes("Düşük / Minimal")) return "Düşük / Minimal";
    if (tier.includes("Very High") || tier.includes("Çok Yüksek")) return "Çok Yüksek";
    if (tier.includes("Moderate") || tier.includes("Orta")) return "Orta Düzey";
    if (tier.includes("High") || tier.includes("Yüksek")) return "Yüksek";
    if (tier.includes("Low") || tier.includes("Düşük")) return "Düşük";
    return tier;
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Modern Unified Benchmark & Standards Mission Bar ────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        {/* Top: Engine Identity & Technical Verification Badges */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 shrink-0">
              <Pill className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "Ölüm Sonrası Toksikokinetik & PMR" : "Post-Mortem Toxicokinetics & PMR"}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-rose-500/10 border border-rose-500/30 text-rose-300">
                  SOFT • TIAFT
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {lastActionTime && (
              <span className="text-[9px] text-emerald-400 font-bold bg-white/[0.03] border border-white/10 px-2.5 py-1 rounded-lg flex items-center gap-1">
                <Check className="w-3 h-3" />
                {lastActionTime}
              </span>
            )}

            <div className="flex bg-black/60 p-1 rounded-xl border border-tactical-border/60">
              <button
                type="button"
                onClick={() => setActiveTab("pmr")}
                className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                  activeTab === "pmr" ? "bg-rose-500/20 text-rose-300 border border-rose-500/50 shadow-sm" : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {isTr ? "PMR (C/P) Oranı" : "PMR (C/P) Ratio"}
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("extrap")}
                className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                  activeTab === "extrap" ? "bg-rose-500/20 text-rose-300 border border-rose-500/50 shadow-sm" : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {isTr ? "Antemortem Ekstrapolasyon" : "Antemortem Extrapolation"}
              </button>
            </div>
          </div>
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

      {/* ── SubTab 1: PMR (C/P) Evaluation ── */}
      {activeTab === "pmr" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Xenobiotic Presets & Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                {isTr ? "Ksenobiyotik Hazır Şablonları" : "Xenobiotic Presets"}
              </span>
              <button
                onClick={() => runPmrEvaluation(selectedDrug, cHeart, cFemoral, unit)}
                disabled={loading}
                className="min-h-[36px] px-4 py-2 rounded-xl bg-rose-500 hover:bg-rose-400 text-zinc-950 font-black text-xs uppercase tracking-wider transition-all shadow-[0_0_20px_rgba(244,63,94,0.3)] hover:shadow-[0_0_25px_rgba(244,63,94,0.5)] disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer active:scale-95"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                {loading
                  ? (isTr ? `Değerlendiriliyor %${progress}...` : `Evaluating ${progress}%...`)
                  : (isTr ? "PMR Değerlendir" : "Evaluate PMR")}
              </button>
            </div>

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
                  <div className="text-[10px] text-zinc-500">{isTr ? p.risk_tr : p.risk}</div>
                </button>
              ))}
            </div>

            <div className="space-y-3 pt-2 text-xs">
              <div className="space-y-1">
                <label className="text-[10px] text-zinc-400 block font-bold uppercase">
                  {isTr ? `Kardiyak Kalp Kanı (C_heart) [${unit}]` : `Cardiac Heart Blood (C_heart) [${unit}]`}
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
                  {isTr ? `Periferik Femoral Kan (C_femoral) [${unit}]` : `Peripheral Femoral Blood (C_femoral) [${unit}]`}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={cFemoral}
                  onChange={(e) => setCFemoral(parseFloat(e.target.value) || 0)}
                  className="w-full min-h-[40px] bg-black/50 border border-tactical-border/70 rounded-xl p-2 font-mono text-xs text-tactical-text focus:outline-none focus:border-rose-500"
                />
              </div>
            </div>
          </div>

          {/* Right: PMR Results */}
          <div className="lg:col-span-2 space-y-4">
            {pmrResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-rose-500/40 bg-gradient-to-br from-rose-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-rose-500/20 pb-3.5">
                    <div>
                      <span className="text-[10px] font-bold text-rose-300 uppercase tracking-widest block">
                        {isTr ? "ÖLÜM SONRASI YENİDEN DAĞILIM (PMR) SKOR KARTI" : "POST-MORTEM REDISTRIBUTION (PMR) SCORECARD"}
                      </span>
                      <span className="text-2xl sm:text-3xl font-black text-rose-300 font-mono">
                        C/P = {pmrResult.cp_observed}
                      </span>
                      <span className="text-[9px] sm:text-[10px] text-zinc-400 block mt-0.5">
                        {isTr ? "Madde:" : "Compound:"} {pmrResult.compound_name} • {isTr ? "Görünür V_d:" : "Apparent V_d:"} {pmrResult.vd_l_kg} L/kg
                      </span>
                    </div>
                    <div className="flex flex-col items-start sm:items-end gap-1">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "PMR Risk Düzeyi" : "PMR Risk Tier"}
                      </span>
                      <span className={`text-[10px] sm:text-xs font-bold px-2.5 py-1 rounded-lg border font-mono whitespace-nowrap ${
                        pmrResult.is_cardiac_overestimated
                          ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                          : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                      }`}>
                        {getPmrRiskLabel(pmrResult.pmr_risk_tier)}
                      </span>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1">
                    <span className="text-[10px] text-zinc-500 block uppercase">
                      {isTr ? "Toksikolojik Kılavuz:" : "Toxicology Guideline:"}
                    </span>
                    <p className="text-zinc-200 leading-relaxed font-bold">
                      {isTr
                        ? (pmrResult.is_cardiac_overestimated
                            ? "Belirgin ölüm sonrası akciğer-kalp difüzyonu; femoral venöz kan zorunludur."
                            : "İhmal edilebilir yeniden dağılım etkisi.")
                        : pmrResult.clinical_guideline}
                    </p>
                    <p className="text-rose-300 text-[11px] mt-1">
                      {isTr
                        ? (pmrResult.is_cardiac_overestimated
                            ? `YÜKSEK PMR FAZLA TAHMİN UYARISI: Kalp kanı konsantrasyonu (${pmrResult.c_heart} ${pmrResult.unit}), periferik femoral kandan (${pmrResult.c_femoral} ${pmrResult.unit}) %${pmrResult.overestimation_percentage.toFixed(1)} daha yüksektir.`
                            : `PMR normal denge sınırları içerisinde (C/P = ${pmrResult.cp_observed}).`)
                        : pmrResult.alert_message}
                    </p>
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-rose-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                      {isTr ? "SOFT / TIAFT Yasal Değerlendirme Kalkanı" : "SOFT / TIAFT Legal Evaluative Shield"}
                    </div>
                    {isTr
                      ? "Ölüm sonrası kardiyak kan konsantrasyonları doğrudan ölüm öncesi intoksikasyon seviyelerine çevrilemez (SOFT / TIAFT Kılavuzları)."
                      : pmrResult.prosecutors_fallacy_shield}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* ── SubTab 2: Antemortem Back-Extrapolation ── */}
      {activeTab === "extrap" && (
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
                  ? (isTr ? `Ekstrapole Ediliyor %${progress}...` : `Extrapolating ${progress}%...`)
                  : (isTr ? "Ekstrapole Et" : "Extrapolate")}
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
                    const preset = DRUG_PRESETS.find((d) => d.name === e.target.value);
                    if (preset) {
                      setCFemoral(preset.cFem);
                      setUnit(preset.unit);
                    }
                  }}
                  className="w-full min-h-[40px] bg-black/50 border border-tactical-border/70 rounded-xl p-2 font-mono text-xs text-rose-300 font-bold focus:outline-none focus:border-rose-500"
                >
                  {DRUG_PRESETS.map((d) => (
                    <option key={d.name} value={d.name}>
                      {d.name} ({isTr ? d.risk_tr : d.risk})
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-zinc-400 block font-bold uppercase">
                  {isTr ? `Ölüm Sonrası Femoral Kan (C_femoral) [${unit}]` : `Post-Mortem Femoral Blood (C_femoral) [${unit}]`}
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
                <div className="flex justify-between text-[10px]">
                  <span className="text-zinc-400 uppercase font-bold">
                    {isTr ? "Geçen Ölüm Sonrası Süre:" : "Elapsed PM Interval:"}
                  </span>
                  <span className="text-rose-300 font-mono font-bold">{elapsedHours.toFixed(1)} {isTr ? "saat" : "h"}</span>
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
                  <span className="text-rose-400 font-bold">{elapsedHours.toFixed(1)} {isTr ? "Saat Geçti" : "Hours Elapsed"}</span>
                  <span>48.0 h</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-zinc-500">{isTr ? "Madde:" : "Compound:"}</span>
                  <span className="font-bold text-zinc-200">{selectedDrug}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">C_femoral (t_0):</span>
                  <span className="font-bold text-zinc-200">{cFemoral} {unit}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">{isTr ? "Eliminasyon:" : "Elimination:"}</span>
                  <span className="font-bold text-rose-300">
                    {selectedDrug === "Ethanol"
                      ? (isTr ? "Sıfırıncı Derece Widmark" : "Zero-Order Widmark")
                      : (isTr ? "Birinci Derece Yarılanma Ömrü" : "First-Order Half-Life")}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Extrapolation Results */}
          <div className="lg:col-span-2 space-y-4">
            {extrapResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-rose-500/40 bg-gradient-to-br from-rose-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-rose-500/20 pb-3.5">
                    <div>
                      <span className="text-[10px] font-bold text-rose-300 uppercase tracking-widest block">
                        {isTr ? `ÖLÜM ÖNCESİ HESAPLANAN KONSANTRASYON (t - ${extrapResult.elapsed_hours} saat)` : `ANTEMORTEM EXTRAPOLATED CONCENTRATION (t - ${extrapResult.elapsed_hours}h)`}
                      </span>
                      <span className="text-2xl sm:text-3xl font-black text-rose-300 font-mono">
                        {extrapResult.c_antemortem_extrapolated} {extrapResult.unit}
                      </span>
                      <span className="text-[9px] sm:text-[10px] text-zinc-400 block mt-0.5">
                        {isTr ? "Ölüm Sonrası Femoral Taban Değeri:" : "Post-Mortem Femoral Baseline:"} {extrapResult.c_femoral_postmortem} {extrapResult.unit}
                      </span>
                    </div>
                    <div className="flex flex-col items-start sm:items-end gap-1">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "Kinetik Formül" : "Kinetic Formula"}
                      </span>
                      <span className="text-[10px] sm:text-xs font-bold px-2.5 py-1 rounded-lg bg-black/60 border border-tactical-border/60 text-zinc-300 font-mono whitespace-nowrap">
                        {extrapResult.elimination_type}
                      </span>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1">
                    <span className="text-[10px] text-zinc-500 block uppercase">
                      {isTr ? "Kinematik Geriye Projeksiyon Formülü:" : "Kinematic Back-Projection Formula:"}
                    </span>
                    <p className="text-rose-300 font-bold">{extrapResult.kinetic_formula}</p>
                    {extrapResult.elimination_rate_constant_ke_h && (
                      <p className="text-[10px] text-zinc-400">
                        {isTr ? "Eliminasyon Hız Sabiti (k_e):" : "Elimination Rate Constant (k_e):"} {extrapResult.elimination_rate_constant_ke_h} h⁻¹ (t_1/2 = {extrapResult.half_life_hours}h)
                      </p>
                    )}
                    {extrapResult.beta_60_g_l_h && (
                      <p className="text-[10px] text-zinc-400">
                        {isTr ? "Widmark Saatlik Hız (β_60):" : "Widmark Hourly Rate (β_60):"} {extrapResult.beta_60_g_l_h} g/L/h
                      </p>
                    )}
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-rose-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      {isTr ? "SOFT / TIAFT Yasal Değerlendirme Kalkanı" : "SOFT / TIAFT Legal Evaluative Shield"}
                    </div>
                    {isTr
                      ? "Ölüm öncesi geriye ekstrapolasyon, sağlam bir dolaşım sisteminde doğrusal veya üstel atılım varsayar (SOFT / TIAFT)."
                      : extrapResult.prosecutors_fallacy_shield}
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
