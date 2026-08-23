"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Scale,
  ShieldCheck,
  AlertTriangle,
  Globe,
  Gavel,
  CheckCircle2,
  XCircle,
  BarChart3,
  RefreshCw,
  ChevronRight,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

// ── Types ──────────────────────────────────────────────────────────────────────

interface EvaluativeReportResponse {
  likelihood_ratio: number;
  log10_likelihood_ratio: number;
  effective_lr: number;
  is_prosecution_supported: boolean;
  supported_proposition: string;
  opposed_proposition: string;
  verbal_tier: number;
  log10_tier_min: number;
  log10_tier_max: number | null;
  phrase_en: string;
  phrase_tr: string;
  evaluative_statement: string;
  language: string;
  hp_proposition: string;
  hd_proposition: string;
  prosecutors_fallacy_shield: string;
  reporting_standard: string;
}

interface DaubertResponse {
  pillar_1_falsifiability: boolean;
  pillar_2_error_rate: boolean;
  pillar_3_peer_review: boolean;
  pillar_4_standards: boolean;
  frye_general_acceptance: boolean;
  overall_admissible: boolean;
  error_rate_bound: number;
  prosecutor_fallacy_shield: string;
}

// ── ENFSI tier metadata for visualization ─────────────────────────────────────

const TIER_CONFIG = [
  {
    tier: 0,
    label: "Neutral / Inconclusive",
    labelTr: "Nötr / Sonuçsuz",
    color: "text-zinc-400",
    bg: "bg-zinc-500/20",
    border: "border-zinc-500/40",
    dot: "bg-zinc-400",
    logRange: "log₁₀ LR = 0",
  },
  {
    tier: 1,
    label: "Weak Support",
    labelTr: "Zayıf Destek",
    color: "text-sky-400",
    bg: "bg-sky-500/20",
    border: "border-sky-500/40",
    dot: "bg-sky-400",
    logRange: "0 < log₁₀ LR ≤ 1",
  },
  {
    tier: 2,
    label: "Moderate Support",
    labelTr: "Orta Düzeyde Destek",
    color: "text-blue-400",
    bg: "bg-blue-500/20",
    border: "border-blue-500/40",
    dot: "bg-blue-400",
    logRange: "1 < log₁₀ LR ≤ 2",
  },
  {
    tier: 3,
    label: "Moderately Strong",
    labelTr: "Orta-Güçlü Destek",
    color: "text-violet-400",
    bg: "bg-violet-500/20",
    border: "border-violet-500/40",
    dot: "bg-violet-400",
    logRange: "2 < log₁₀ LR ≤ 3",
  },
  {
    tier: 4,
    label: "Strong Support",
    labelTr: "Güçlü Destek",
    color: "text-amber-400",
    bg: "bg-amber-500/20",
    border: "border-amber-500/40",
    dot: "bg-amber-400",
    logRange: "3 < log₁₀ LR ≤ 4",
  },
  {
    tier: 5,
    label: "Very Strong Support",
    labelTr: "Çok Güçlü Destek",
    color: "text-orange-400",
    bg: "bg-orange-500/20",
    border: "border-orange-500/40",
    dot: "bg-orange-400",
    logRange: "4 < log₁₀ LR ≤ 6",
  },
  {
    tier: 6,
    label: "Extremely Strong",
    labelTr: "Aşırı Güçlü Destek",
    color: "text-emerald-400",
    bg: "bg-emerald-500/20",
    border: "border-emerald-500/40",
    dot: "bg-emerald-400",
    logRange: "log₁₀ LR > 6",
  },
];

// ── Presets (log10 LR values) ─────────────────────────────────────────────────
const PRESETS = [
  { label: "1.0 (Neutral)", labelTr: "1.0 (Nötr)", log10: 0 },
  { label: "10 (Weak)", labelTr: "10 (Zayıf)", log10: 1 },
  { label: "500 (Mod. Strong)", labelTr: "500 (Orta-Güçlü)", log10: 2.699 },
  { label: "5,000 (Strong)", labelTr: "5.000 (Güçlü)", log10: 3.699 },
  { label: "3.5×10⁷ (P6_03)", labelTr: "3.5×10⁷ (P6_03)", log10: 7.5441 },
];

export default function ExpertWitnessPanel() {
  const { lang, setLang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeTab, setActiveTab] = useState<"enfsi" | "daubert">("enfsi");
  const [log10LR, setLog10LR] = useState<number>(7.5441); // VECTOR_P6_03 default
  const [hp, setHp] = useState(
    isTr ? "DNA profili şüpheli şahıstan kaynaklanmaktadır." : "The DNA evidence originates from the named suspect."
  );
  const [hd, setHd] = useState(
    isTr ? "DNA profili toplumdan rastgele, akraba olmayan bir şahıstan kaynaklanmaktadır." : "The DNA evidence originates from an unknown unrelated person."
  );
  const [loading, setLoading] = useState(false);

  // Daubert inputs
  const [errorRate, setErrorRate] = useState<number>(1e-9);
  const [peerReviewed, setPeerReviewed] = useState(true);
  const [swgdam, setSwgdam] = useState(true);
  const [iso17025, setIso17025] = useState(true);

  const [reportData, setReportData] = useState<EvaluativeReportResponse | null>(null);
  const [daubertData, setDaubertData] = useState<DaubertResponse | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const computedLR = Math.pow(10, log10LR);

  const fetchReport = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/court/evaluative-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          likelihood_ratio: computedLR,
          hp_proposition: hp,
          hd_proposition: hd,
          language: lang,
        }),
      });
      if (res.ok) setReportData(await res.json());
    } catch (e) {
      console.error("Evaluative report error:", e);
    } finally {
      setLoading(false);
    }
  }, [computedLR, hp, hd, lang, API_BASE]);

  const fetchDaubert = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/court/daubert-compliance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          error_rate: errorRate,
          has_peer_reviewed_algorithms: peerReviewed,
          swgdam_compliant: swgdam,
          iso17025_compliant: iso17025,
        }),
      });
      if (res.ok) setDaubertData(await res.json());
    } catch (e) {
      console.error("Daubert audit error:", e);
    } finally {
      setLoading(false);
    }
  }, [errorRate, peerReviewed, swgdam, iso17025, API_BASE]);

  // Auto-fetch on mount & lang change
  useEffect(() => {
    fetchReport();
  }, [lang]);

  const activeTier = reportData ? TIER_CONFIG[reportData.verbal_tier] : null;

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Modern Unified Benchmark & Standards Mission Bar ────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        {/* Top: Engine Identity & Technical Verification Badges */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-400 shrink-0">
              <Gavel className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "ENFSI Değerlendirici Raporlama & Sözlü Ölçek" : "ENFSI Evaluative Reporting & Verbal Scale"}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-300">
                  ENFSI 2017 • DAUBERT
                </span>
              </div>
            </div>
          </div>

          <div className="flex bg-black/60 p-1 rounded-xl border border-tactical-border/60 shrink-0">
            <button
              type="button"
              onClick={() => { setActiveTab("enfsi"); if (!reportData) fetchReport(); }}
              className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                activeTab === "enfsi" ? "bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow-sm" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {isTr ? "ENFSI Sözlü Ölçek" : "ENFSI Verbal Scale"}
            </button>
            <button
              type="button"
              onClick={() => { setActiveTab("daubert"); if (!daubertData) fetchDaubert(); }}
              className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                activeTab === "daubert" ? "bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow-sm" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Daubert / Frye
            </button>
          </div>
        </div>
      </div>

      {/* ── Tab 1: ENFSI Verbal Scale ── */}
      {activeTab === "enfsi" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Inputs */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="border-b border-tactical-border/40 pb-3 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                {isTr ? "Değerlendirici Parametreler" : "Evaluative Parameters"}
              </span>
              {/* Language Toggle */}
              <button
                onClick={() => setLang(lang === "tr" ? "en" : "tr")}
                className="flex items-center gap-1 px-2 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[10px] font-bold cursor-pointer hover:bg-amber-500/20 transition-all"
              >
                <Globe className="w-3 h-3" />
                {lang === "tr" ? "🇹🇷 TR" : "🇬🇧 EN"}
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-zinc-400 block mb-1">
                  log₁₀(LR) = <span className="text-amber-300 font-bold">{log10LR.toFixed(4)}</span>
                  <span className="text-zinc-500 ml-2">(LR ≈ {computedLR >= 1e6 ? computedLR.toExponential(2) : computedLR.toLocaleString()})</span>
                </label>
                <input
                  type="range"
                  min={-6}
                  max={10}
                  step={0.1}
                  value={log10LR}
                  onChange={e => setLog10LR(parseFloat(e.target.value))}
                  className="w-full accent-amber-400"
                />
                <div className="flex justify-between text-[9px] text-zinc-600 mt-0.5">
                  <span>10⁻⁶</span>
                  <span>1 ({isTr ? "Nötr" : "Neutral"})</span>
                  <span>10¹⁰</span>
                </div>
              </div>

              {/* Presets */}
              <div>
                <label className="text-zinc-400 block mb-1.5">{isTr ? "Hızlı Hazır Ayarlar:" : "Quick Presets:"}</label>
                <div className="flex flex-wrap gap-1">
                  {PRESETS.map(p => (
                    <button
                      key={p.label}
                      onClick={() => setLog10LR(p.log10)}
                      className={`px-2 py-1 rounded-lg text-[10px] font-bold cursor-pointer transition-all border ${
                        Math.abs(log10LR - p.log10) < 0.001
                          ? "bg-amber-500 text-black border-amber-500"
                          : "bg-black/40 text-zinc-400 border-tactical-border/40 hover:border-amber-500/40 hover:text-amber-300"
                      }`}
                    >
                      {isTr ? p.labelTr : p.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-zinc-400 block mb-1">
                  {isTr ? "H_p (İddia Makamı Hipotezi):" : "H_p (Prosecution Proposition):"}
                </label>
                <textarea
                  rows={2}
                  value={hp}
                  onChange={e => setHp(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono text-[11px] resize-none"
                />
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">
                  {isTr ? "H_d (Savunma Hipotezi):" : "H_d (Defense Proposition):"}
                </label>
                <textarea
                  rows={2}
                  value={hd}
                  onChange={e => setHd(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono text-[11px] resize-none"
                />
              </div>
            </div>

            <button
              onClick={fetchReport}
              disabled={loading}
              className="w-full min-h-[42px] py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer active:scale-95"
            >
              <Scale className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              {isTr ? "Değerlendirici Raporu Oluştur" : "Generate Evaluative Report"}
            </button>
          </div>

          {/* Right: ENFSI Output */}
          <div className="lg:col-span-2 space-y-4">
            {reportData && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                {/* Active Tier Banner */}
                <div className={`rounded-2xl border p-5 space-y-3 shadow-2xl bg-gradient-to-br from-black/80 to-tactical-surface/50 ${activeTier?.border}`}>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <span className={`text-[10px] font-bold uppercase tracking-widest block mb-1 ${activeTier?.color}`}>
                        {isTr
                          ? `ENFSI 2017 — DÜZEY ${reportData.verbal_tier} / 6 • ${reportData.reporting_standard}`
                          : `ENFSI 2017 — TIER ${reportData.verbal_tier} OF 6 • ${reportData.reporting_standard}`}
                      </span>
                      <span className={`text-2xl font-black font-mono ${activeTier?.color}`}>
                        {isTr ? activeTier?.labelTr : activeTier?.label}
                      </span>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-zinc-400">
                          {reportData.is_prosecution_supported
                            ? (isTr ? "→ İddia H_p Destekleniyor" : "→ Prosecution H_p supported")
                            : (isTr ? "→ Savunma H_d Destekleniyor" : "→ Defense H_d supported")}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${reportData.is_prosecution_supported ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30" : "bg-sky-500/10 text-sky-300 border-sky-500/30"}`}>
                          {reportData.supported_proposition}
                        </span>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <span className="text-[10px] text-zinc-500 block">log₁₀(LR)</span>
                      <span className={`text-lg font-black font-mono ${activeTier?.color}`}>
                        {reportData.log10_likelihood_ratio >= 0 ? "+" : ""}{reportData.log10_likelihood_ratio.toFixed(4)}
                      </span>
                      <span className="text-[9px] text-zinc-500 block">{activeTier?.logRange}</span>
                    </div>
                  </div>

                  {/* Evaluative Statement */}
                  <div className="p-4 rounded-xl bg-black/50 border border-tactical-border/40">
                    <div className="text-[10px] text-zinc-500 uppercase font-bold mb-2 flex items-center gap-1">
                      <Gavel className="w-3 h-3" />
                      {isTr ? "Standart Mahkeme Değerlendirici İfadesi (Türkçe)" : "Standardized Courtroom Evaluative Statement (English)"}
                    </div>
                    <p className="text-sm text-zinc-100 font-mono leading-relaxed italic">
                      "{reportData.evaluative_statement}"
                    </p>
                  </div>

                  {/* Dual Language Side-by-Side */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/30">
                      <div className="text-[9px] text-zinc-500 uppercase font-bold mb-1">🇬🇧 English</div>
                      <p className="text-[11px] text-zinc-300 leading-relaxed">{reportData.phrase_en}</p>
                    </div>
                    <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/30">
                      <div className="text-[9px] text-zinc-500 uppercase font-bold mb-1">🇹🇷 Türkçe</div>
                      <p className="text-[11px] text-zinc-300 leading-relaxed">{reportData.phrase_tr}</p>
                    </div>
                  </div>
                </div>

                {/* 7-Tier Stepladder Visual */}
                <div className="rounded-2xl border border-tactical-border/60 bg-black/40 p-4 space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 block mb-3">
                    {isTr ? "ENFSI 2017 Yedi Düzeyli Sözlü Güç Ölçeği" : "ENFSI 2017 Seven-Tier Verbal Strength Scale"}
                  </span>
                  <div className="space-y-1.5">
                    {[...TIER_CONFIG].reverse().map(tc => (
                      <div
                        key={tc.tier}
                        className={`flex items-center gap-3 px-3 py-2 rounded-xl border transition-all ${
                          tc.tier === reportData.verbal_tier
                            ? `${tc.bg} ${tc.border} ring-1 ${tc.border}`
                            : "border-transparent bg-black/20 opacity-40"
                        }`}
                      >
                        {tc.tier === reportData.verbal_tier && (
                          <ChevronRight className={`w-3.5 h-3.5 shrink-0 ${tc.color}`} />
                        )}
                        {tc.tier !== reportData.verbal_tier && (
                          <div className={`w-3.5 h-3.5 shrink-0 rounded-full ${tc.dot} opacity-40`} />
                        )}
                        <span className={`text-[11px] font-bold w-6 ${tc.color}`}>{tc.tier}</span>
                        <span className={`text-[11px] font-bold flex-1 ${tc.tier === reportData.verbal_tier ? tc.color : "text-zinc-500"}`}>
                          {isTr ? tc.labelTr : tc.label}
                        </span>
                        <span className="text-[9px] text-zinc-600 font-mono">{tc.logRange}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Fallacy Shield */}
                <div className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/20 text-[10px] font-mono text-zinc-400">
                  <div className="flex items-center gap-1.5 text-rose-400 font-bold mb-1">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    {isTr ? "Savcılık Safsatası Kalkanı (Prosecutor's Fallacy Shield)" : "Prosecutor's Fallacy Shield"}
                  </div>
                  <p className="leading-relaxed">
                    {isTr
                      ? (reportData.language === "tr"
                          ? reportData.prosecutors_fallacy_shield.substring(0, 320)
                          : "Savcılık Safsatası Kalkanı: LR değeri şüphelinin suçlu olma olasılığı değil; delilin hipotezler altındaki bağıl olasılığıdır (ENFSI 2017).")
                      : reportData.prosecutors_fallacy_shield.substring(0, 320)}…
                  </p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* ── Tab 2: Daubert / Frye ── */}
      {activeTab === "daubert" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Daubert Inputs */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
                {isTr ? "Daubert FRE 702 Denetim Parametreleri" : "Daubert FRE 702 Audit Parameters"}
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-zinc-400 block mb-1">
                  {isTr ? "Gözlemlenen Sistem Hata Oranı (P_error):" : "Observed System Error Rate (P_error):"}
                </label>
                <select
                  value={errorRate}
                  onChange={e => setErrorRate(parseFloat(e.target.value))}
                  className="w-full min-h-[40px] px-3 py-2 rounded-xl bg-black/50 border border-tactical-border/60 text-tactical-text font-mono"
                >
                  <option value={1e-9}>{isTr ? "1×10⁻⁹ (Geçerli: ≤ 1×10⁻⁶)" : "1×10⁻⁹ (Pass: ≤ 1×10⁻⁶)"}</option>
                  <option value={1e-6}>{isTr ? "1×10⁻⁶ (Sınır)" : "1×10⁻⁶ (Boundary)"}</option>
                  <option value={5e-5}>{isTr ? "5×10⁻⁵ (Başarısız: > 1×10⁻⁶)" : "5×10⁻⁵ (Fail: > 1×10⁻⁶)"}</option>
                </select>
              </div>

              {[
                {
                  label: isTr ? "Hakemli Algoritmalar (Daubert Kriteri 3)" : "Peer-Reviewed Algorithms (Daubert Prong 3)",
                  value: peerReviewed,
                  setter: setPeerReviewed
                },
                {
                  label: isTr ? "SWGDAM (2020) QAS Uyumluluğu (Daubert Kriteri 4)" : "SWGDAM (2020) QAS Compliant (Daubert Prong 4)",
                  value: swgdam,
                  setter: setSwgdam
                },
                {
                  label: isTr ? "ISO/IEC 17025:2017 Akreditasyonu (Daubert Kriteri 4)" : "ISO/IEC 17025:2017 Accreditation (Daubert Prong 4)",
                  value: iso17025,
                  setter: setIso17025
                },
              ].map(({ label, value, setter }) => (
                <label key={label} className="flex items-center justify-between gap-2 cursor-pointer">
                  <span className="text-zinc-400 text-[11px] leading-snug">{label}:</span>
                  <button
                    onClick={() => setter(v => !v)}
                    className={`min-h-[36px] px-3.5 py-1 rounded-lg text-xs font-bold border transition-all cursor-pointer shrink-0 ${
                      value
                        ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                        : "bg-rose-500/20 text-rose-300 border-rose-500/40"
                    }`}
                  >
                    {value ? (isTr ? "✓ EVET" : "✓ YES") : (isTr ? "✗ HAYIR" : "✗ NO")}
                  </button>
                </label>
              ))}
            </div>

            <button
              onClick={fetchDaubert}
              disabled={loading}
              className="w-full min-h-[42px] py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer active:scale-95"
            >
              <Gavel className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              {isTr ? "Daubert Denetimini Çalıştır" : "Run Daubert Audit"}
            </button>
          </div>

          {/* Right: Daubert Output */}
          <div className="lg:col-span-2 space-y-4">
            {daubertData && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                {/* Overall Verdict */}
                <div className={`rounded-2xl border p-5 shadow-2xl ${daubertData.overall_admissible ? "border-emerald-500/40 bg-emerald-500/5" : "border-rose-500/40 bg-rose-500/5"}`}>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <span className={`text-[10px] font-bold uppercase tracking-widest block ${daubertData.overall_admissible ? "text-emerald-300" : "text-rose-300"}`}>
                        {isTr ? "YASAL KABUL EDİLEBİLİRLİK KARARI" : "STATUTORY LEGAL ADMISSIBILITY VERDICT"}
                      </span>
                      <span className={`text-2xl font-black font-mono ${daubertData.overall_admissible ? "text-emerald-300" : "text-rose-300"}`}>
                        {daubertData.overall_admissible
                          ? (isTr ? "MAHKEMEDE KABUL EDİLEBİLİR" : "COURT ADMISSIBLE")
                          : (isTr ? "KABUL EDİLEMEZ" : "INADMISSIBLE")}
                      </span>
                    </div>
                    {daubertData.overall_admissible
                      ? <CheckCircle2 className="w-12 h-12 text-emerald-400 shrink-0" />
                      : <XCircle className="w-12 h-12 text-rose-400 shrink-0" />
                    }
                  </div>

                  {/* Daubert Criteria Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {[
                      {
                        label: isTr ? "Kriter 1: Yanlışlanabilirlik & Test Edilebilirlik" : "Prong 1: Falsifiability & Testability",
                        sub: isTr ? "Otomatik deterministik birim test paketleri" : "Automated deterministic unit test suites",
                        pass: daubertData.pillar_1_falsifiability
                      },
                      {
                        label: isTr ? "Kriter 2: Bilinen Hata Oranı" : "Prong 2: Known Error Rate",
                        sub: `P_error ≤ ${daubertData.error_rate_bound.toExponential(0)} (Daubert FRE 702)`,
                        pass: daubertData.pillar_2_error_rate
                      },
                      {
                        label: isTr ? "Kriter 3: Hakemli Bilimsel Literatür" : "Prong 3: Peer-Reviewed Literature",
                        sub: isTr ? "Yayınlanmış algoritmalar ve hakemli doğrulama" : "Published algorithms & peer-reviewed validation",
                        pass: daubertData.pillar_3_peer_review
                      },
                      {
                        label: isTr ? "Kriter 4: Standartlar ve Kalite Kontrol" : "Prong 4: Standards Control",
                        sub: "SWGDAM (2020) & ISO/IEC 17025:2017",
                        pass: daubertData.pillar_4_standards
                      },
                    ].map(({ label, sub, pass }) => (
                      <div key={label} className={`p-3 rounded-xl border ${pass ? "border-emerald-500/30 bg-emerald-500/10" : "border-rose-500/30 bg-rose-500/10"}`}>
                        <div className="flex items-center gap-2 mb-1">
                          {pass
                            ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                            : <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                          }
                          <span className={`text-[11px] font-bold ${pass ? "text-emerald-300" : "text-rose-300"}`}>{label}</span>
                        </div>
                        <p className="text-[10px] text-zinc-500 leading-relaxed">{sub}</p>
                      </div>
                    ))}
                  </div>

                  <div className={`mt-3 p-2.5 rounded-xl border text-center text-xs font-bold ${daubertData.frye_general_acceptance ? "border-sky-500/30 bg-sky-500/10 text-sky-300" : "border-rose-500/30 bg-rose-500/10 text-rose-300"}`}>
                    {isTr ? "Frye Standardı — Genel Bilimsel Kabul:" : "Frye Standard — General Scientific Acceptance:"}{" "}
                    {daubertData.frye_general_acceptance
                      ? (isTr ? "✓ SAĞLANDI" : "✓ ESTABLISHED")
                      : (isTr ? "✗ SAĞLANMADI" : "✗ NOT ESTABLISHED")}
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
