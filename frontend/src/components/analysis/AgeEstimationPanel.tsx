"use client";

import { useState, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Clock,
  Dna,
  Activity,
  Sliders,
  AlertCircle,
  CheckCircle2,
  ShieldCheck,
  RefreshCw,
  Scale,
  Compass,
  FileText,
  Layers,
  Sparkles,
  ChevronRight,
  Info
} from "lucide-react";
import {
  VISAGE_5CPG_MARKERS,
  EXTENDED_10CPG_MARKERS,
  VISAGE_PRESETS,
  predictAgeClientSide,
  VisagePredictionResult
} from "@/utils/visageAgeEngine";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

type ModelMode = "VISAGE_5CPG_ELASTIC_NET" | "VISAGE_5CPG_MLR_POWER" | "EXTENDED_10CPG_CLOCK";

export default function AgeEstimationPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [modelMode, setModelMode] = useState<ModelMode>("VISAGE_5CPG_ELASTIC_NET");
  const [tissueType, setTissueType] = useState<string>("BLOOD");
  const [knownAge, setKnownAge] = useState<string>("25.0");
  const [activePreset, setActivePreset] = useState<string>("VECTOR_VISAGE_02");
  const [langTab, setLangTab] = useState<"en" | "tr">(isTr ? "tr" : "en");

  useEffect(() => {
    setLangTab(isTr ? "tr" : "en");
  }, [isTr]);

  // State for CpG Beta values
  const [cpgBetas, setCpgBetas] = useState<Record<string, number>>({
    cg16867657: 0.200,
    cg06639320: 0.190,
    cg16419235: 0.150,
    cg04523812: 0.160,
    cg07955995: 0.140,
    cg21572722: 0.200,
    cg04084157: 0.250,
    cg08097417: 0.220,
    cg09809672: 0.200,
    cg02088308: 0.210,
    cg17861230: 0.220,
    cg02228185: 0.300,
  });

  const [loading, setLoading] = useState(false);

  // Client-side initial evaluation
  const initialResult = useMemo(() => {
    return predictAgeClientSide(cpgBetas, tissueType, knownAge ? parseFloat(knownAge) : null, modelMode);
  }, []);

  const [result, setResult] = useState<VisagePredictionResult>(initialResult);

  const handleSliderChange = (locus: string, val: number) => {
    const updated = { ...cpgBetas, [locus]: val };
    setCpgBetas(updated);
    // Real-time dynamic reactive update
    const res = predictAgeClientSide(updated, tissueType, knownAge ? parseFloat(knownAge) : null, modelMode);
    setResult(res);
  };

  const handlePresetSelect = (presetId: string) => {
    setActivePreset(presetId);
    const preset = VISAGE_PRESETS.find((p) => p.id === presetId);
    if (!preset) return;

    const newBetas: Record<string, number> = { ...cpgBetas, ...preset.betas };
    setCpgBetas(newBetas);
    setTissueType(preset.tissue);
    setModelMode(preset.modelMode);
    setKnownAge(preset.knownAge ? preset.knownAge.toString() : "");

    const res = predictAgeClientSide(
      newBetas,
      preset.tissue,
      preset.knownAge ?? null,
      preset.modelMode
    );
    setResult(res);
  };

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const runPrediction = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/epigenetics/predict-age`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cpg_methylation: cpgBetas,
          tissue_type: tissueType,
          chronological_age_known: knownAge ? parseFloat(knownAge) : null,
          model_mode: modelMode,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      } else {
        // Fallback to mathematical client engine
        const clientRes = predictAgeClientSide(cpgBetas, tissueType, knownAge ? parseFloat(knownAge) : null, modelMode);
        setResult(clientRes);
      }
    } catch (e) {
      console.warn("Using offline client-side biocomputational engine:", e);
      const clientRes = predictAgeClientSide(cpgBetas, tissueType, knownAge ? parseFloat(knownAge) : null, modelMode);
      setResult(clientRes);
    } finally {
      setLoading(false);
    }
  };

  // Determine active CpG list based on selected model
  const activeMarkers = useMemo(() => {
    if (modelMode === "EXTENDED_10CPG_CLOCK") {
      return Object.entries(EXTENDED_10CPG_MARKERS).map(([id, meta]) => ({
        id,
        gene: meta.gene,
        desc: isTr ? `Eski ağırlık: ${meta.legacyWeight}` : `Legacy weight: ${meta.legacyWeight}`,
        weight: meta.legacyWeight,
      }));
    }
    return Object.entries(VISAGE_5CPG_MARKERS).map(([id, meta]) => ({
      id,
      gene: meta.gene,
      desc: `${meta.chrom} | ${meta.ampliconBp}bp | w=${modelMode === "VISAGE_5CPG_MLR_POWER" ? meta.mlrWeight : meta.elasticNetWeight}`,
      weight: modelMode === "VISAGE_5CPG_MLR_POWER" ? meta.mlrWeight : meta.elasticNetWeight,
    }));
  }, [modelMode, isTr]);

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header Banner ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl border border-purple-500/30 bg-purple-500/10 shadow-lg overflow-hidden backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-300 shadow-inner">
            <Clock className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xs sm:text-sm font-bold tracking-widest text-tactical-text uppercase leading-snug">
                {isTr ? "VISAGE 5-CpG & Epigenetik Yaşlandırma Motoru (Modül 16)" : "VISAGE 5-CpG & Epigenetic Aging Engine (Module 16)"}
              </h2>
              <span className="px-2.5 py-0.5 rounded-lg text-[9px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40 whitespace-nowrap shrink-0">
                VISAGE KONSORSİYUMU / HORVATH BAĞI
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              {isTr
                ? "ISO/IEC 17025 metrolojik belirsizlik bütçesi ile çoklu doku DNA metilasyon yaşı dekonvolüsyonu"
                : "Multi-tissue DNA methylation age deconvolution with ISO/IEC 17025 metrological uncertainty budget"}
            </p>
          </div>
        </div>

        <button
          onClick={runPrediction}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 active:scale-95 text-white font-bold text-xs transition-all shadow-lg shadow-purple-500/25 disabled:opacity-50 shrink-0 whitespace-nowrap cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>
            {loading
              ? (isTr ? "Model Sentezleniyor..." : "Synthesizing Model...")
              : (isTr ? "Epigenetik Tahmini Çalıştır" : "Run Epigenetic Estimation")}
          </span>
        </button>
      </div>

      {/* ── Model Architecture Selector & Golden Benchmark Presets ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Architecture Mode Tabs */}
        <div className="rounded-xl border border-tactical-border/70 bg-tactical-surface/50 p-3 space-y-2">
          <label className="text-[10px] font-bold uppercase text-zinc-400 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            {isTr ? "Model Mimarisi" : "Model Architecture"}
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-1.5">
            {[
              { id: "VISAGE_5CPG_ELASTIC_NET", label: "5-CpG Elastic Net", sub: isTr ? "Horvath Bağı (y0=20)" : "Horvath Link (y0=20)" },
              { id: "VISAGE_5CPG_MLR_POWER", label: "5-CpG MLR Kuvvet", sub: "ELOVL2^2.366" },
              { id: "EXTENDED_10CPG_CLOCK", label: isTr ? "Genişletilmiş 10-CpG" : "Extended 10-CpG", sub: isTr ? "Pan-Doku Saati" : "Pan-Tissue Clock" },
            ].map((m) => (
              <button
                key={m.id}
                onClick={() => {
                  setModelMode(m.id as ModelMode);
                  const res = predictAgeClientSide(cpgBetas, tissueType, knownAge ? parseFloat(knownAge) : null, m.id as ModelMode);
                  setResult(res);
                }}
                className={`p-2 rounded-lg text-left transition-all border cursor-pointer ${
                  modelMode === m.id
                    ? "bg-purple-500/20 border-purple-500/60 text-purple-200 shadow-md"
                    : "bg-black/30 border-tactical-border/40 text-zinc-400 hover:border-purple-500/30"
                }`}
              >
                <div className="text-[10px] font-bold leading-tight">{m.label}</div>
                <div className="text-[8px] text-zinc-500">{m.sub}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Golden Benchmark Presets */}
        <div className="lg:col-span-2 rounded-xl border border-tactical-border/70 bg-tactical-surface/50 p-3 space-y-2">
          <label className="text-[10px] font-bold uppercase text-zinc-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            {isTr ? "Altın Standart Kalibrasyon Vektörleri" : "Golden Benchmark Calibration Vectors"}
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-1.5">
            {VISAGE_PRESETS.map((p) => (
              <button
                key={p.id}
                onClick={() => handlePresetSelect(p.id)}
                className={`p-2 rounded-lg text-left transition-all border cursor-pointer ${
                  activePreset === p.id
                    ? "bg-amber-500/20 border-amber-500/60 text-amber-200 shadow-md"
                    : "bg-black/30 border-tactical-border/40 text-zinc-400 hover:border-amber-500/30"
                }`}
              >
                <div className="text-[9px] font-bold truncate">{p.id}</div>
                <div className="text-[8px] text-zinc-500 truncate">{p.name.split("(")[1]?.replace(")", "") || ""}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Main Engine Workstation ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Col: CpG Controls & Tissue Matrix Settings */}
        <div className="rounded-2xl border border-tactical-border/70 bg-tactical-surface/40 p-5 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-tactical-border/50 pb-3">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-purple-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                {isTr ? "CpG Metilasyon Oranları (Beta)" : "CpG Methylation Ratios (Beta)"}
              </span>
            </div>
            <span className="text-[9px] text-purple-300 font-bold px-2 py-0.5 rounded bg-purple-500/20">
              {activeMarkers.length} {isTr ? "Aktif Lokus" : "Loci Active"}
            </span>
          </div>

          {/* Tissue Type Selection */}
          <div className="space-y-1.5">
            <label className="text-[10px] text-zinc-400 block font-bold uppercase">
              {isTr ? "Biyolojik Matris Kalibrasyonu" : "Biological Matrix Calibration"}
            </label>
            <select
              value={tissueType}
              onChange={(e) => {
                setTissueType(e.target.value);
                const res = predictAgeClientSide(cpgBetas, e.target.value, knownAge ? parseFloat(knownAge) : null, modelMode);
                setResult(res);
              }}
              className="w-full bg-black/60 border border-tactical-border/70 rounded-xl p-2.5 font-mono text-xs text-purple-300 font-bold focus:outline-none focus:border-purple-500 shadow-inner cursor-pointer"
            >
              <option value="BLOOD">
                {isTr ? "Tam Kan / Kan Lekesi (Öteleme: 0.00 yıl | RSE ±1.95)" : "Whole Blood / Bloodstain (Offset: 0.00 yrs | RSE ±1.95)"}
              </option>
              <option value="SALIVA_BUCCAL">
                {isTr ? "Tükürük / Bukkal Sürüntü (Öteleme: +2.45 yıl | RSE ±2.25)" : "Oral Saliva / Buccal Swab (Offset: +2.45 yrs | RSE ±2.25)"}
              </option>
              <option value="SEMEN">
                {isTr ? "Seminal Sıvı / Meni (Öteleme: +18.60 yıl | RSE ±2.60)" : "Seminal Fluid / Semen (Offset: +18.60 yrs | RSE ±2.60)"}
              </option>
              <option value="BONE">
                {isTr ? "İskelet Kalıntısı / Kemik / Diş (Öteleme: +1.15 yıl | RSE ±3.05)" : "Skeletal Remains / Bone / Teeth (Offset: +1.15 yrs | RSE ±3.05)"}
              </option>
            </select>
          </div>

          {/* Known Age Input for Acceleration Delta */}
          <div className="space-y-1.5 pt-2 border-t border-tactical-border/30">
            <label className="text-[10px] text-zinc-400 block font-bold uppercase">
              {isTr ? "Özneden Bilinen Kronolojik Yaş (Opsiyonel Fark)" : "Chronological Age of Subject (Optional Delta)"}
            </label>
            <input
              type="number"
              placeholder="e.g. 25.0"
              value={knownAge}
              onChange={(e) => {
                setKnownAge(e.target.value);
                const res = predictAgeClientSide(cpgBetas, tissueType, e.target.value ? parseFloat(e.target.value) : null, modelMode);
                setResult(res);
              }}
              className="w-full bg-black/60 border border-tactical-border/70 rounded-xl p-2.5 font-mono text-xs text-purple-300 font-bold focus:outline-none focus:border-purple-500 shadow-inner"
            />
          </div>

          {/* Interactive CpG Sliders */}
          <div className="space-y-3.5 pt-3 border-t border-tactical-border/30 max-h-[380px] overflow-y-auto pr-1.5">
            {activeMarkers.map((m) => {
              const betaVal = cpgBetas[m.id] ?? 0.25;
              return (
                <div key={m.id} className="p-2.5 rounded-xl bg-black/30 border border-tactical-border/40 space-y-1.5">
                  <div className="flex items-center justify-between text-[10px]">
                    <div>
                      <span className="font-bold text-zinc-200 mr-2">{m.gene}</span>
                      <span className="text-zinc-500 font-mono text-[9px]">({m.id})</span>
                    </div>
                    <span className="font-mono text-purple-400 font-bold bg-purple-500/10 px-1.5 py-0.5 rounded border border-purple-500/20">
                      β = {betaVal.toFixed(3)}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.005"
                    value={betaVal}
                    onChange={(e) => handleSliderChange(m.id, parseFloat(e.target.value))}
                    className="w-full accent-purple-500 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                  />
                  <div className="text-[8px] text-zinc-500 font-mono truncate">{m.desc}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right 2-Cols: Prediction Output, Metrology & Evaluative Statements */}
        <div className="lg:col-span-2 space-y-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={`${modelMode}-${tissueType}-${result.estimated_age_years}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="space-y-6"
            >
              {/* Estimated Age Primary Metric Card */}
              <div className="rounded-2xl border border-purple-500/40 bg-gradient-to-br from-purple-500/15 via-tactical-surface/70 to-black/90 p-6 space-y-5 shadow-2xl relative overflow-hidden backdrop-blur-lg">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-purple-500/20 pb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold text-purple-300 uppercase tracking-widest">
                        {isTr ? "TAHMİN EDİLEN KRONOLOJİK YAŞ" : "PREDICTED CHRONOLOGICAL AGE"}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        {isTr
                          ? (result.developmental_stage === "ADULT" ? "YETİŞKİN"
                            : result.developmental_stage === "JUVENILE / ADOLESCENT" ? "GENÇ / ERGEN"
                            : result.developmental_stage === "SENIOR / ELDERLY" ? "YAŞLI"
                            : result.developmental_stage)
                          : result.developmental_stage}
                      </span>
                    </div>
                    <div className="flex items-baseline gap-3 mt-1">
                      <span className="text-4xl sm:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-200 via-teal-200 to-emerald-200 font-mono">
                        {result.estimated_age_years.toFixed(2)}
                      </span>
                      <span className="text-sm font-bold text-zinc-400 uppercase">
                        {isTr ? "Yaş" : "Years"}
                      </span>
                    </div>
                  </div>

                  <div className="sm:text-right p-3 rounded-xl bg-black/40 border border-purple-500/20">
                    <span className="text-[9px] text-zinc-400 block uppercase font-bold">
                      {isTr ? "ISO/IEC 17025 %95 Tahmin Aralığı" : "ISO/IEC 17025 95% Prediction Interval"}
                    </span>
                    <span className="text-base sm:text-lg font-bold text-emerald-400 font-mono">
                      [{result.prediction_interval_lower.toFixed(2)} – {result.prediction_interval_upper.toFixed(2)} {isTr ? "yaş" : "yrs"}]
                    </span>
                    <span className="text-[9px] text-zinc-500 block mt-0.5">
                      {isTr ? "Genişletilmiş Belirsizlik" : "Expanded Uncertainty"} U95% = ±{result.expanded_uncertainty_95.toFixed(2)} {isTr ? "yaş" : "yrs"}
                    </span>
                  </div>
                </div>

                {/* Telemetry Metrics Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1">
                  <div className="p-3 rounded-xl bg-black/50 border border-tactical-border/50">
                    <span className="text-[9px] text-zinc-400 block font-bold uppercase">
                      {isTr ? "Doğrusal Skor (x)" : "Linear Score (x)"}
                    </span>
                    <span className="font-bold text-purple-300 font-mono text-xs">
                      x = {result.linear_predictor_x.toFixed(4)}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/50 border border-tactical-border/50">
                    <span className="text-[9px] text-zinc-400 block font-bold uppercase">
                      {isTr ? "Doku Ötelemesi" : "Tissue Offset"}
                    </span>
                    <span className="font-bold text-cyan-300 font-mono text-xs">
                      {result.tissue_offset_applied >= 0 ? "+" : ""}{result.tissue_offset_applied.toFixed(2)} {isTr ? "yaş" : "yrs"}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/50 border border-tactical-border/50">
                    <span className="text-[9px] text-zinc-400 block font-bold uppercase">Mahalanobis D²</span>
                    <span className="font-bold text-indigo-300 font-mono text-xs">
                      {result.mahalanobis_distance_squared.toFixed(6)}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/50 border border-tactical-border/50">
                    <span className="text-[9px] text-zinc-400 block font-bold uppercase">
                      {isTr ? "Yaşlanma İvmesi" : "Acceleration Delta"}
                    </span>
                    <span className={`font-bold font-mono text-xs ${
                      result.age_acceleration_delta !== null
                        ? result.age_acceleration_delta > 5
                          ? "text-rose-400"
                          : result.age_acceleration_delta < -5
                          ? "text-cyan-400"
                          : "text-emerald-400"
                        : "text-zinc-500"
                    }`}>
                      {result.age_acceleration_delta !== null
                        ? `${result.age_acceleration_delta > 0 ? "+" : ""}${result.age_acceleration_delta.toFixed(2)} ${isTr ? "yaş" : "yrs"}`
                        : "N/A"}
                    </span>
                  </div>
                </div>
              </div>

              {/* CpG Contributions Decomposition Table */}
              <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-3 shadow-xl">
                <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    {isTr ? "CpG Lokus Katkı Ayrıştırması" : "CpG Locus Deconvolution Breakdown"}
                  </h3>
                  <span className="text-[9px] text-zinc-400">
                    {isTr ? "Horvath Çarpanı = 21.0 | Pivot y0 = 20.0" : "Horvath Multiplier = 21.0 | Pivot y0 = 20.0"}
                  </span>
                </div>

                <div className="divide-y divide-tactical-border/30 max-h-[220px] overflow-y-auto">
                  {result.cpg_locus_contributions.map((c) => (
                    <div key={c.locus} className="py-2 flex items-center justify-between text-xs font-mono">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-zinc-200">{c.gene}</span>
                        <span className="text-[9px] text-zinc-500">({c.locus})</span>
                      </div>
                      <div className="flex items-center gap-4 text-right">
                        <span className="text-zinc-400 text-[10px]">β = {c.methylation_beta.toFixed(4)}</span>
                        <span className="text-zinc-500 text-[10px]">w = {c.weight.toFixed(2)}</span>
                        <span className={`font-bold min-w-[70px] ${c.contribution_years >= 0 ? "text-emerald-400" : "text-amber-400"}`}>
                          {c.contribution_years >= 0 ? "+" : ""}{c.contribution_years.toFixed(2)} {isTr ? "yaş" : "yrs"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bilingual ENFSI Evaluative Court Statement */}
              <div className="rounded-2xl border border-indigo-500/40 bg-indigo-500/5 p-5 space-y-3 shadow-xl">
                <div className="flex items-center justify-between border-b border-indigo-500/20 pb-3">
                  <div className="flex items-center gap-2">
                    <Scale className="w-4 h-4 text-indigo-400" />
                    <span className="text-xs font-bold uppercase tracking-wider text-indigo-200">
                      {isTr ? "Standart ENFSI Değerlendirici Mahkeme İfadesi" : "Standardized ENFSI Evaluative Court Statement"}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 bg-black/40 p-1 rounded-lg border border-indigo-500/30">
                    <button
                      onClick={() => setLangTab("en")}
                      className={`px-2.5 py-0.5 rounded text-[9px] font-bold transition-all cursor-pointer ${
                        langTab === "en" ? "bg-indigo-500 text-white" : "text-zinc-400 hover:text-white"
                      }`}
                    >
                      English
                    </button>
                    <button
                      onClick={() => setLangTab("tr")}
                      className={`px-2.5 py-0.5 rounded text-[9px] font-bold transition-all cursor-pointer ${
                        langTab === "tr" ? "bg-indigo-500 text-white" : "text-zinc-400 hover:text-white"
                      }`}
                    >
                      Türkçe
                    </button>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-black/50 border border-indigo-500/20 text-xs text-zinc-300 font-sans leading-relaxed">
                  {langTab === "en" ? result.enfsi_statement_en : result.enfsi_statement_tr}
                </div>

                {/* Legal Fallacy Shield */}
                <div className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-[10px] text-amber-200/90 leading-normal">
                  <ShieldCheck className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-amber-300 uppercase block mb-0.5">
                      {isTr ? "Adli Değerlendirici Raporlama Kalkanı:" : "Forensic Evaluative Reporting Shield:"}
                    </span>
                    {isTr
                      ? `Epigenetik tahminler biyolojik yaşlanmayı (%95 güven aralığı: ±${result.expanded_uncertainty_95 || 4.24} yıl) temsil eder ve kronolojik yaştan doku maruziyetine göre sapabilir.`
                      : result.prosecutors_fallacy_shield}
                  </div>
                </div>
              </div>

            </motion.div>
          </AnimatePresence>
        </div>

      </div>
    </div>
  );
}
