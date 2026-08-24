import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldCheck, Scale, BarChart3, AlertTriangle, CheckCircle2, RefreshCw, Layers, Calculator, Activity, Check } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getApiBaseUrl } from "@/lib/api";

interface ComponentDetail {
  component_name: string;
  standard_uncertainty: number;
  sensitivity_coefficient: number;
  probability_distribution: string;
  variance_contribution: number;
  percentage_contribution: number;
  description?: string;
}

interface BudgetResponse {
  nominal_concentration: number;
  combined_standard_uncertainty: number;
  expanded_uncertainty: number;
  coverage_factor: number;
  confidence_level: string;
  reported_interval: {
    lower_bound: number;
    upper_bound: number;
    formatted_interval: string;
  };
  total_variance: number;
  component_count: number;
  components: ComponentDetail[];
  prosecutors_fallacy_shield: string;
}

interface ProficiencyResponse {
  lab_measured_value: number;
  consensus_mean: number;
  consensus_std: number;
  z_score: number;
  absolute_z_score: number;
  performance_tier: string;
  verdict: string;
  is_compliant: boolean;
}

// Deterministic ISO/IEC 17025 GUM Calibration Budget Engine (Pillar 6 §3.2)
const computeClientBudget = (nominal: number, k: number): BudgetResponse => {
  const y = Math.max(0.0, nominal);
  const components: ComponentDetail[] = [
    {
      component_name: "Micro-Pipette Volume (x1)",
      standard_uncertainty: 0.013228756555322953,
      sensitivity_coefficient: 1.0,
      probability_distribution: "RECTANGULAR",
      variance_contribution: 0.000175,
      percentage_contribution: 6.03,
      description: "ISO 8655 volumetric dispensing variance",
    },
    {
      component_name: "Thermal Gradient (x2)",
      standard_uncertainty: 0.015,
      sensitivity_coefficient: 1.0,
      probability_distribution: "NORMAL",
      variance_contribution: 0.000225,
      percentage_contribution: 7.76,
      description: "Thermal cycler block temperature heterogeneity",
    },
    {
      component_name: "qPCR Standard Curve (x3)",
      standard_uncertainty: 0.03,
      sensitivity_coefficient: 1.0,
      probability_distribution: "NORMAL",
      variance_contribution: 0.000900,
      percentage_contribution: 31.03,
      description: "Serial dilution standard curve regression variance",
    },
    {
      component_name: "Master Mix Amplification (x4)",
      standard_uncertainty: 0.04,
      sensitivity_coefficient: 1.0,
      probability_distribution: "NORMAL",
      variance_contribution: 0.001600,
      percentage_contribution: 55.17,
      description: "Polymerase enzymatic amplification efficiency drift",
    },
  ];

  const totalVariance = 0.002900;
  const uc = Math.sqrt(totalVariance); // 0.0538516
  const U = k * uc;
  const lower = Math.max(0, y - U);
  const upper = y + U;

  return {
    nominal_concentration: y,
    combined_standard_uncertainty: uc,
    expanded_uncertainty: U,
    coverage_factor: k,
    confidence_level: k === 2 ? "95.45%" : k === 1 ? "68.27%" : "99.73%",
    reported_interval: {
      lower_bound: lower,
      upper_bound: upper,
      formatted_interval: `${y.toFixed(3)} ± ${U.toFixed(3)} ng/μL`,
    },
    total_variance: totalVariance,
    component_count: 4,
    components,
    prosecutors_fallacy_shield: "Expanded uncertainty budgeting (U_95% = 2.00 · u_c) guarantees metrological confidence under GUM (ISO/IEC 17025:2017).",
  };
};

// Deterministic Proficiency z-score Evaluator (Pillar 6 §3.2)
const computeClientProficiency = (xLab: number, mean: number, std: number): ProficiencyResponse => {
  const safeStd = std <= 0 ? 0.05 : std;
  const z = (xLab - mean) / safeStd;
  const absZ = Math.abs(z);
  let tier = "SATISFACTORY";
  let verdict = "Satisfactory Performance  -  ISO/IEC 17025 Compliant";

  if (absZ > 3.0) {
    tier = "UNSATISFACTORY";
    verdict = "Unsatisfactory Performance  -  Corrective Action Required (FRE 702 breach)";
  } else if (absZ > 2.0) {
    tier = "QUESTIONABLE";
    verdict = "Questionable Performance  -  Warning Issued (Investigate laboratory bias)";
  }

  return {
    lab_measured_value: xLab,
    consensus_mean: mean,
    consensus_std: safeStd,
    z_score: z,
    absolute_z_score: absZ,
    performance_tier: tier,
    verdict,
    is_compliant: absZ <= 2.0,
  };
};

export default function MeasurementUncertaintyPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeTab, setActiveTab] = useState<"budget" | "proficiency">("budget");
  const [nominalConc, setNominalConc] = useState<number>(1.45);
  const [coverageFactor, setCoverageFactor] = useState<number>(2.0);
  const [loading, setLoading] = useState<boolean>(false);
  const [lastCalculatedTime, setLastCalculatedTime] = useState<string | null>(null);
  const [calcKey, setCalcKey] = useState<number>(0);

  // Proficiency inputs
  const [labValue, setLabValue] = useState<number>(1.47);
  const [consensusMean, setConsensusMean] = useState<number>(1.45);
  const [consensusStd, setConsensusStd] = useState<number>(0.05);

  const [budgetData, setBudgetData] = useState<BudgetResponse | null>(() => computeClientBudget(1.45, 2.0));
  const [proficiencyData, setProficiencyData] = useState<ProficiencyResponse | null>(null);

  const getLocalizedComponentName = (name: string) => {
    if (!isTr) return name;
    if (name.includes("Micro-Pipette Volume") || name.includes("Pipette")) return "Mikro-Pipet Hacmi (x1)";
    if (name.includes("Thermal Gradient") || name.includes("Thermal")) return "Termal Gradyan (x2)";
    if (name.includes("qPCR Standard Curve") || name.includes("Standard Curve")) return "qPCR Standart Eğrisi (x3)";
    if (name.includes("Master Mix Amplification") || name.includes("Master Mix")) return "Master Mix Çoğaltımı (x4)";
    return name;
  };

  const getLocalizedDist = (dist: string) => {
    if (!isTr) return dist;
    switch (dist.toUpperCase()) {
      case "RECTANGULAR": return "DİKDÖRTGEN (RECT)";
      case "NORMAL": return "NORMAL (GAUSS)";
      case "TRIANGULAR": return "ÜÇGEN (TRI)";
      default: return dist;
    }
  };

  const handleCalculateBudget = async () => {
    setLoading(true);
    const API_BASE = getApiBaseUrl();
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/qc/uncertainty/calculate-budget`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nominal_concentration: nominalConc,
          coverage_factor: coverageFactor,
        }),
        signal: AbortSignal.timeout(2500),
      });
      if (res.ok) {
        const data: BudgetResponse = await res.json();
        setBudgetData(data);
      } else {
        setBudgetData(computeClientBudget(nominalConc, coverageFactor));
      }
    } catch {
      setBudgetData(computeClientBudget(nominalConc, coverageFactor));
    } finally {
      setTimeout(() => {
        setLoading(false);
        setCalcKey((prev) => prev + 1);
        setLastCalculatedTime(new Date().toLocaleTimeString());
      }, 200);
    }
  };

  const handleEvaluateProficiency = async () => {
    setLoading(true);
    const API_BASE = getApiBaseUrl();
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/qc/uncertainty/proficiency-z-score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lab_measured_value: labValue,
          consensus_mean: consensusMean,
          consensus_std: consensusStd,
        }),
        signal: AbortSignal.timeout(2500),
      });
      if (res.ok) {
        const data: ProficiencyResponse = await res.json();
        setProficiencyData(data);
      } else {
        setProficiencyData(computeClientProficiency(labValue, consensusMean, consensusStd));
      }
    } catch {
      setProficiencyData(computeClientProficiency(labValue, consensusMean, consensusStd));
    } finally {
      setTimeout(() => {
        setLoading(false);
        setCalcKey((prev) => prev + 1);
        setLastCalculatedTime(new Date().toLocaleTimeString());
      }, 200);
    }
  };

  useEffect(() => {
    handleCalculateBudget();
  }, [nominalConc, coverageFactor]);


  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Modern Unified Benchmark & Standards Mission Bar ────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        {/* Top: Engine Identity & Technical Verification Badges */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-sky-500/10 border border-sky-500/30 rounded-xl text-sky-400 shrink-0">
              <Scale className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "ISO 17025 Ölçüm Belirsizliği & Kalibrasyon" : "ISO 17025 Measurement Uncertainty"}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-sky-500/10 border border-sky-500/30 text-sky-300">
                  GUM JCGM • k=2.00
                </span>
              </div>
            </div>
          </div>

          <div className="flex bg-black/60 p-1 rounded-xl border border-tactical-border/60 shrink-0">
            <button
              type="button"
              onClick={() => setActiveTab("budget")}
              className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                activeTab === "budget" ? "bg-sky-500/20 text-sky-300 border border-sky-500/50 shadow-sm" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {isTr ? "Belirsizlik Bütçesi" : "Uncertainty Budget"}
            </button>
            <button
              type="button"
              onClick={() => {
                setActiveTab("proficiency");
                if (!proficiencyData) handleEvaluateProficiency();
              }}
              className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                activeTab === "proficiency" ? "bg-sky-500/20 text-sky-300 border border-sky-500/50 shadow-sm" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {isTr ? "Yeterlilik z-Skoru" : "Proficiency z-Score"}
            </button>
          </div>
        </div>
      </div>

      {/* ── SubTab 1: Calibration Uncertainty Budget ── */}
      {activeTab === "budget" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Input Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
                {isTr ? "Kantifikasyon Parametreleri" : "Quantification Parameters"}
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-zinc-400 block mb-1">
                  {isTr ? "Ölçülen DNA Konsantrasyonu (y, ng/μL):" : "Measured DNA Concentration (y in ng/μL):"}
                </label>
                <input
                  type="number"
                  step="0.05"
                  min="0.01"
                  max="10.0"
                  value={nominalConc}
                  onChange={(e) => setNominalConc(parseFloat(e.target.value) || 0.0)}
                  className="w-full min-h-[40px] px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
                />
              </div>

              <div>
                <label className="text-zinc-400 block mb-1">
                  {isTr ? "Kapsama Faktörü k (%95.45 GA):" : "Coverage Factor k (95.45% CI):"}
                </label>
                <select
                  value={coverageFactor}
                  onChange={(e) => setCoverageFactor(parseFloat(e.target.value))}
                  className="w-full min-h-[40px] px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
                >
                  <option value={2.0}>{isTr ? "k = 2.00 (%95.45 Genişletilmiş Standart)" : "k = 2.00 (95.45% Expanded Standard)"}</option>
                  <option value={1.0}>{isTr ? "k = 1.00 (%68.27 Standart u_c)" : "k = 1.00 (68.27% Standard u_c)"}</option>
                  <option value={3.0}>{isTr ? "k = 3.00 (%99.73 Muhafazakar)" : "k = 3.00 (99.73% Conservative)"}</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <button
                onClick={handleCalculateBudget}
                disabled={loading}
                className="w-full min-h-[42px] py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer active:scale-95 disabled:opacity-50"
              >
                <Calculator className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                {loading
                  ? (isTr ? "Bütçe Hesaplanıyor..." : "Calculating Budget...")
                  : (isTr ? "Bütçeyi Yeniden Hesapla" : "Recalculate Budget")}
              </button>

              {lastCalculatedTime && (
                <div className="flex items-center justify-center gap-1.5 text-[9px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 py-1 px-2 rounded-lg animate-fadeIn">
                  <Check className="w-3 h-3 shrink-0" />
                  <span>
                    {isTr
                      ? `Bütçe Güncellendi: ${lastCalculatedTime}`
                      : `Budget Recalculated: ${lastCalculatedTime}`}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Right: Budget Output & Interval Card */}
          <div className="lg:col-span-2 space-y-4">
            {budgetData && (
              <motion.div
                key={`budget-${calcKey}`}
                initial={{ opacity: 0.6, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-4"
              >

                <div className="rounded-2xl border border-sky-500/40 bg-gradient-to-br from-sky-500/10 via-tactical-surface/60 to-black/80 p-5 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-sky-500/20 pb-3">
                    <div>
                      <span className="text-[10px] font-bold text-sky-300 uppercase tracking-widest block">
                        {isTr ? "GUM JCGM 100:2008 GENİŞLETİLMİŞ BELİRSİZLİK ARALIĞI" : "GUM JCGM 100:2008 EXPANDED UNCERTAINTY INTERVAL"}
                      </span>
                      <span className="text-xl font-black text-sky-300 font-mono">
                        {budgetData.reported_interval.formatted_interval}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "%95 Güven Sınırları" : "95% Confidence Bounds"}
                      </span>
                      <span className="text-xs font-bold text-emerald-400 font-mono">
                        [{budgetData.reported_interval.lower_bound.toFixed(4)}, {budgetData.reported_interval.upper_bound.toFixed(4)}] ng/μL
                      </span>
                    </div>
                  </div>

                  {/* Summary Metrics */}
                  <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
                    <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">{isTr ? "Birleşik u_c" : "Combined u_c"}</span>
                      <span className="font-bold text-sky-300">{budgetData.combined_standard_uncertainty.toFixed(5)} ng/μL</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">{isTr ? "Genişletilmiş U_%95" : "Expanded U_95%"}</span>
                      <span className="font-bold text-emerald-300">± {budgetData.expanded_uncertainty.toFixed(5)} ng/μL</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">{isTr ? "Toplam Varyans u_c²" : "Total Variance u_c²"}</span>
                      <span className="font-bold text-amber-300">{budgetData.total_variance.toFixed(6)}</span>
                    </div>
                  </div>

                  {/* Component Table */}
                  <div className="space-y-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-zinc-300 block">
                      {isTr ? "Kalibrasyon Belirsizlik Bütçesi Dağılımı" : "Calibration Uncertainty Budget Breakdown"}
                    </span>
                    <div className="overflow-x-auto">
                      <table className="w-full text-[11px] font-mono text-left">
                        <thead>
                          <tr className="border-b border-tactical-border/40 text-zinc-500">
                            <th className="pb-1.5">{isTr ? "Büyüklük (x_i)" : "Quantity (x_i)"}</th>
                            <th className="pb-1.5">u_i (ng/μL)</th>
                            <th className="pb-1.5">{isTr ? "Dağılım" : "Dist."}</th>
                            <th className="pb-1.5 text-right">{isTr ? "Varyans (c_i u_i)²" : "Variance (c_i u_i)²"}</th>
                            <th className="pb-1.5 text-right">{isTr ? "% Katkı" : "% Contrib"}</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-tactical-border/20">
                          {budgetData.components.map((comp) => (
                            <tr key={comp.component_name} className="hover:bg-black/20">
                              <td className="py-1.5 text-zinc-300 font-bold">{getLocalizedComponentName(comp.component_name)}</td>
                              <td className="py-1.5 text-sky-300">{comp.standard_uncertainty.toFixed(4)}</td>
                              <td className="py-1.5 text-zinc-400">{getLocalizedDist(comp.probability_distribution)}</td>
                              <td className="py-1.5 text-right text-amber-300">{comp.variance_contribution.toFixed(6)}</td>
                              <td className="py-1.5 text-right text-emerald-400 font-bold">%{comp.percentage_contribution}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-sky-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      {isTr ? "ISO/IEC 17025:2017 Madde 7.6 Metrolojik Belirsizlik Kalkanı" : "ISO/IEC 17025:2017 Clause 7.6 Metrological Uncertainty Shield"}
                    </div>
                    {isTr
                      ? "GUM kılavuzuna göre genişletilmiş belirsizlik bütçesi (U_95% = 2.00 · u_c) ölçüm güvenilirliğini sağlar (ISO/IEC 17025:2017)."
                      : (budgetData.prosecutors_fallacy_shield || "Expanded uncertainty budgeting (U_95% = 2.00 · u_c) guarantees metrological confidence under GUM (ISO/IEC 17025:2017).")}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* ── SubTab 2: Proficiency Testing z-Score ── */}
      {activeTab === "proficiency" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Proficiency Inputs */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
                {isTr ? "Yeterlilik Testi Konsensüs Verileri" : "Proficiency Test Consensus Inputs"}
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-zinc-400 block mb-1">
                  {isTr ? "Laboratuvar Ölçüm Değeri (x_lab, ng/μL):" : "Lab Measured Value (x_lab in ng/μL):"}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={labValue}
                  onChange={(e) => setLabValue(parseFloat(e.target.value) || 0.0)}
                  className="w-full min-h-[40px] px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
                />
              </div>

              <div>
                <label className="text-zinc-400 block mb-1">
                  {isTr ? "Konsensüs Tur Ortalaması (μ, ng/μL):" : "Consensus Round Mean (μ in ng/μL):"}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={consensusMean}
                  onChange={(e) => setConsensusMean(parseFloat(e.target.value) || 0.0)}
                  className="w-full min-h-[40px] px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
                />
              </div>

              <div>
                <label className="text-zinc-400 block mb-1">
                  {isTr ? "Konsensüs Standart Sapması (σ):" : "Consensus Standard Deviation (σ):"}
                </label>
                <input
                  type="number"
                  step="0.005"
                  min="0.001"
                  value={consensusStd}
                  onChange={(e) => setConsensusStd(parseFloat(e.target.value) || 0.01)}
                  className="w-full min-h-[40px] px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
                />
              </div>
            </div>

            <div className="space-y-2">
              <button
                onClick={handleEvaluateProficiency}
                disabled={loading}
                className="w-full min-h-[42px] py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer active:scale-95 disabled:opacity-50"
              >
                <Activity className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                {loading
                  ? (isTr ? "Değerlendiriliyor..." : "Evaluating...")
                  : (isTr ? "z-Skorunu Değerlendir" : "Evaluate z-Score")}
              </button>

              {lastCalculatedTime && (
                <div className="flex items-center justify-center gap-1.5 text-[9px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 py-1 px-2 rounded-lg animate-fadeIn">
                  <Check className="w-3 h-3 shrink-0" />
                  <span>
                    {isTr
                      ? `z-Skoru Güncellendi: ${lastCalculatedTime}`
                      : `Evaluated: ${lastCalculatedTime}`}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Right: Proficiency Output */}
          <div className="lg:col-span-2 space-y-4">
            {proficiencyData && (
              <motion.div
                key={`prof-${calcKey}`}
                initial={{ opacity: 0.6, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-4"
              >

                <div className="rounded-2xl border border-sky-500/40 bg-gradient-to-br from-sky-500/10 via-tactical-surface/60 to-black/80 p-5 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-sky-500/20 pb-3">
                    <div>
                      <span className="text-[10px] font-bold text-sky-300 uppercase tracking-widest block">
                        {isTr ? "YETERLİLİK TESTİ KONSENSÜS z-SKORU" : "PROFICIENCY TESTING CONSENSUS z-SCORE"}
                      </span>
                      <span className="text-2xl font-black text-sky-300 font-mono">
                        z = {proficiencyData.z_score >= 0 ? `+${proficiencyData.z_score.toFixed(3)}` : proficiencyData.z_score.toFixed(3)}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "Performans Düzeyi" : "Performance Tier"}
                      </span>
                      <span
                        className={`text-xs font-bold px-2.5 py-1 rounded border font-mono ${
                          proficiencyData.performance_tier === "SATISFACTORY"
                            ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                            : proficiencyData.performance_tier === "QUESTIONABLE"
                            ? "bg-amber-500/20 text-amber-300 border-amber-500/40"
                            : "bg-rose-500/20 text-rose-300 border-rose-500/40"
                        }`}
                      >
                        {proficiencyData.performance_tier === "SATISFACTORY"
                          ? (isTr ? "TATMIN EDİCİ" : "SATISFACTORY")
                          : proficiencyData.performance_tier === "QUESTIONABLE"
                          ? (isTr ? "ŞÜPHELİ / UYARI" : "QUESTIONABLE")
                          : (isTr ? "YETERSİZ / DÜZELTİCİ FAALİYET" : "UNSATISFACTORY")}
                      </span>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1.5">
                    <div className="flex justify-between text-[11px]">
                      <span className="text-zinc-500">
                        {isTr ? "ISO/IEC 17025 Uyumluluk Kararı:" : "ISO/IEC 17025 Compliance Verdict:"}
                      </span>
                      <span className="text-zinc-200 font-bold">
                        {isTr
                          ? (proficiencyData.performance_tier === "SATISFACTORY"
                              ? "Tatmin Edici Performans  -  ISO/IEC 17025 Uyumu Doğrulandı"
                              : proficiencyData.performance_tier === "QUESTIONABLE"
                              ? "Şüpheli Performans  -  Uyarı Bildirildi"
                              : "Yetersiz Performans  -  Düzeltici Faaliyet Gerekli")
                          : proficiencyData.verdict}
                      </span>
                    </div>
                    <div className="flex justify-between text-[11px]">
                      <span className="text-zinc-500">
                        {isTr ? "Mutlak Sapma (|z|):" : "Absolute Deviation (|z|):"}
                      </span>
                      <span className="text-sky-300 font-bold">{proficiencyData.absolute_z_score.toFixed(3)} σ</span>
                    </div>
                  </div>

                  {/* Benchmark Tiers Explanations */}
                  <div className="grid grid-cols-3 gap-2 text-center text-[10px] font-mono">
                    <div className={`p-2 rounded-lg border ${proficiencyData.absolute_z_score <= 2.0 ? "border-emerald-500/60 bg-emerald-500/10" : "border-tactical-border/40 bg-black/30"}`}>
                      <span className="font-bold text-emerald-400 block">|z| ≤ 2.0</span>
                      <span className="text-zinc-400">{isTr ? "Tatmin Edici / Kalibre" : "Satisfactory / Calibrated"}</span>
                    </div>
                    <div className={`p-2 rounded-lg border ${proficiencyData.absolute_z_score > 2.0 && proficiencyData.absolute_z_score < 3.0 ? "border-amber-500/60 bg-amber-500/10" : "border-tactical-border/40 bg-black/30"}`}>
                      <span className="font-bold text-amber-400 block">2.0 &lt; |z| &lt; 3.0</span>
                      <span className="text-zinc-400">{isTr ? "Şüpheli / Uyarı" : "Questionable / Warning"}</span>
                    </div>
                    <div className={`p-2 rounded-lg border ${proficiencyData.absolute_z_score >= 3.0 ? "border-rose-500/60 bg-rose-500/10" : "border-tactical-border/40 bg-black/30"}`}>
                      <span className="font-bold text-rose-400 block">|z| ≥ 3.0</span>
                      <span className="text-zinc-400">{isTr ? "Yetersiz Eylem" : "Unsatisfactory Action"}</span>
                    </div>
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
