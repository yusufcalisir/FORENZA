"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, Scale, BarChart3, AlertTriangle, CheckCircle2, RefreshCw, Layers, Calculator, Activity } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

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

export default function MeasurementUncertaintyPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeTab, setActiveTab] = useState<"budget" | "proficiency">("budget");
  const [nominalConc, setNominalConc] = useState<number>(1.45);
  const [coverageFactor, setCoverageFactor] = useState<number>(2.0);
  const [loading, setLoading] = useState<boolean>(false);

  // Proficiency inputs
  const [labValue, setLabValue] = useState<number>(1.47);
  const [consensusMean, setConsensusMean] = useState<number>(1.45);
  const [consensusStd, setConsensusStd] = useState<number>(0.05);

  const [budgetData, setBudgetData] = useState<BudgetResponse | null>(null);
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

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const handleCalculateBudget = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/qc/uncertainty/calculate-budget`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nominal_concentration: nominalConc,
          coverage_factor: coverageFactor,
        }),
      });
      if (res.ok) {
        const data: BudgetResponse = await res.json();
        setBudgetData(data);
      }
    } catch (e) {
      console.error("Uncertainty budget calculation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateProficiency = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/qc/uncertainty/proficiency-z-score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lab_measured_value: labValue,
          consensus_mean: consensusMean,
          consensus_std: consensusStd,
        }),
      });
      if (res.ok) {
        const data: ProficiencyResponse = await res.json();
        setProficiencyData(data);
      }
    } catch (e) {
      console.error("Proficiency evaluation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleCalculateBudget();
  }, [nominalConc, coverageFactor]);

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-sky-500/30 bg-sky-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sky-500/20 border border-sky-500/40 text-sky-300">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                {isTr
                  ? "ISO/IEC 17025:2017 Ölçüm Belirsizliği & Kalibrasyon (Pillar 6 §3)"
                  : "ISO/IEC 17025:2017 Measurement Uncertainty & Calibration (Pillar 6 §3)"}
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-sky-500/20 text-sky-300 border border-sky-500/30">
                GUM • JCGM 100:2008 • k=2.00
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              {isTr
                ? "Kantitatif DNA Konsantrasyonu Metrolojik Bütçesi • Birleşik Standart Belirsizlik u_c • Yeterlilik z-Skorları"
                : "Quantitative DNA Concentration Metrological Budget • Combined Standard Uncertainty u_c • Proficiency z-Scores"}
            </p>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1 p-1 rounded-xl bg-black/60 border border-tactical-border/60">
          <button
            onClick={() => setActiveTab("budget")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === "budget" ? "bg-sky-500 text-white shadow-md font-extrabold" : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {isTr ? "Belirsizlik Bütçesi" : "Uncertainty Budget"}
          </button>
          <button
            onClick={() => {
              setActiveTab("proficiency");
              if (!proficiencyData) handleEvaluateProficiency();
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeTab === "proficiency" ? "bg-sky-500 text-white shadow-md font-extrabold" : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {isTr ? "Yeterlilik z-Skoru" : "Proficiency z-Score"}
          </button>
        </div>
      </div>

      {/* ── SubTab 1: Calibration Uncertainty Budget ── */}
      {activeTab === "budget" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Input Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
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
                  className="w-full px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
                />
              </div>

              <div>
                <label className="text-zinc-400 block mb-1">
                  {isTr ? "Kapsama Faktörü k (%95.45 GA):" : "Coverage Factor k (95.45% CI):"}
                </label>
                <select
                  value={coverageFactor}
                  onChange={(e) => setCoverageFactor(parseFloat(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
                >
                  <option value={2.0}>{isTr ? "k = 2.00 (%95.45 Genişletilmiş Standart)" : "k = 2.00 (95.45% Expanded Standard)"}</option>
                  <option value={1.0}>{isTr ? "k = 1.00 (%68.27 Standart u_c)" : "k = 1.00 (68.27% Standard u_c)"}</option>
                  <option value={3.0}>{isTr ? "k = 3.00 (%99.73 Muhafazakar)" : "k = 3.00 (99.73% Conservative)"}</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleCalculateBudget}
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer"
            >
              <Calculator className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              {isTr ? "Bütçeyi Yeniden Hesapla" : "Recalculate Budget"}
            </button>
          </div>

          {/* Right: Budget Output & Interval Card */}
          <div className="lg:col-span-2 space-y-4">
            {budgetData && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
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
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
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
                  className="w-full px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
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
                  className="w-full px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
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
                  className="w-full px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
                />
              </div>
            </div>

            <button
              onClick={handleEvaluateProficiency}
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer"
            >
              <Activity className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              {isTr ? "z-Skorunu Değerlendir" : "Evaluate z-Score"}
            </button>
          </div>

          {/* Right: Proficiency Output */}
          <div className="lg:col-span-2 space-y-4">
            {proficiencyData && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
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
                              ? "Tatmin Edici Performans — ISO/IEC 17025 Uyumu Doğrulandı"
                              : proficiencyData.performance_tier === "QUESTIONABLE"
                              ? "Şüpheli Performans — Uyarı Bildirildi"
                              : "Yetersiz Performans — Düzeltici Faaliyet Gerekli")
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
