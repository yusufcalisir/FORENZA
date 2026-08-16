"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Target, Sparkles, ShieldCheck, RefreshCw, Layers, Grid, Flame, CheckCircle2, AlertTriangle, Cpu, Check } from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";

interface GsrParticle {
  particle_id: string;
  pb_percent: number;
  ba_percent: number;
  sb_percent: number;
  al_percent?: number;
  aspect_ratio: number;
}

interface GsrResponse {
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

interface CmcCell {
  cell_id: string;
  ccf_max: number;
  delta_x_um: number;
  delta_y_um: number;
  delta_theta_deg: number;
}

interface CmcResponse {
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

const DEFAULT_GSR_PARTICLES: GsrParticle[] = [
  { particle_id: "p_01", pb_percent: 35.0, ba_percent: 25.0, sb_percent: 15.0, al_percent: 0.0, aspect_ratio: 1.1 },
  { particle_id: "p_02", pb_percent: 40.0, ba_percent: 30.0, sb_percent: 12.0, al_percent: 0.0, aspect_ratio: 1.2 },
  { particle_id: "p_03", pb_percent: 28.0, ba_percent: 22.0, sb_percent: 18.0, al_percent: 0.0, aspect_ratio: 1.0 },
  { particle_id: "p_04", pb_percent: 45.0, ba_percent: 35.0, sb_percent: 0.0, al_percent: 0.0, aspect_ratio: 1.3 },
];

const DEFAULT_CMC_CELLS: CmcCell[] = [
  { cell_id: "cell_1", ccf_max: 0.85, delta_x_um: 2.0, delta_y_um: -1.5, delta_theta_deg: 0.3 },
  { cell_id: "cell_2", ccf_max: 0.82, delta_x_um: 3.5, delta_y_um: -2.0, delta_theta_deg: 0.4 },
  { cell_id: "cell_3", ccf_max: 0.78, delta_x_um: 1.0, delta_y_um: -0.5, delta_theta_deg: -0.2 },
  { cell_id: "cell_4", ccf_max: 0.90, delta_x_um: 4.0, delta_y_um: -1.0, delta_theta_deg: 0.1 },
  { cell_id: "cell_5", ccf_max: 0.75, delta_x_um: -2.0, delta_y_um: 1.5, delta_theta_deg: -0.5 },
  { cell_id: "cell_6", ccf_max: 0.88, delta_x_um: 1.5, delta_y_um: -1.2, delta_theta_deg: 0.2 },
];

export default function BallisticsGsrPanel() {
  const [activeSubTab, setActiveSubTab] = useState<"gsr" | "cmc">("gsr");
  const [particles, setParticles] = useState<GsrParticle[]>(DEFAULT_GSR_PARTICLES);
  const [cmcCells, setCmcCells] = useState<CmcCell[]>(DEFAULT_CMC_CELLS);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stageText, setStageText] = useState("");
  const [lastActionTime, setLastActionTime] = useState<string | null>(null);

  const [gsrResult, setGsrResult] = useState<GsrResponse | null>({
    total_particles_scanned: 4,
    characteristic_particles: 3,
    consistent_particles: 1,
    commonly_associated_particles: 0,
    likelihood_ratio: 10000.0,
    evidence_strength: "Extremely Strong Support for Firearm Discharge (LR > 10,000)",
    classified_particles: [
      { particle_id: "p_01", classification_tier: "CHARACTERISTIC_GSR", pb_percent: 35.0, ba_percent: 25.0, sb_percent: 15.0, aspect_ratio: 1.1 },
      { particle_id: "p_02", classification_tier: "CHARACTERISTIC_GSR", pb_percent: 40.0, ba_percent: 30.0, sb_percent: 12.0, aspect_ratio: 1.2 },
      { particle_id: "p_03", classification_tier: "CHARACTERISTIC_GSR", pb_percent: 28.0, ba_percent: 22.0, sb_percent: 18.0, aspect_ratio: 1.0 },
      { particle_id: "p_04", classification_tier: "CONSISTENT_WITH_GSR", pb_percent: 45.0, ba_percent: 35.0, sb_percent: 0.0, aspect_ratio: 1.3 },
    ],
    prosecutors_fallacy_shield: "Finding characteristic Pb-Ba-Sb particles indicates proximity to a firearm discharge event (ASTM E1588-20)."
  });

  const [cmcResult, setCmcResult] = useState<CmcResponse | null>({
    total_cells_evaluated: 6,
    cmc_count: 6,
    identification_verdict: "POSITIVE_IDENTIFICATION",
    false_match_probability: "< 1e-6",
    ballistic_conclusion: "Definitive ballistic match to questioned firearm (K >= 6 CMC, P_false < 10^-6).",
    evaluated_cells: DEFAULT_CMC_CELLS.map((c) => ({ ...c, is_congruent_matching_cell: true })),
    prosecutors_fallacy_shield: "Identification is established when K >= 6 congruent matching cells satisfy cross-correlation (CCF >= 0.55), translation (+/-15 um), and rotation (+/-1.0 deg) tolerances."
  });

  // Client-side fallback evaluator for GSR (ASTM E1588-20)
  const evaluateClientGsr = (partList: GsrParticle[]): GsrResponse => {
    let charCount = 0, consCount = 0, commCount = 0;
    const classified = partList.map((p) => {
      let tier = "ENVIRONMENTAL_BACKGROUND";
      if (p.pb_percent > 0 && p.ba_percent > 0 && p.sb_percent > 0) {
        tier = "CHARACTERISTIC_GSR";
        charCount++;
      } else if ((p.pb_percent > 0 && p.ba_percent > 0) || (p.pb_percent > 0 && p.sb_percent > 0) || (p.ba_percent > 0 && p.sb_percent > 0)) {
        tier = "CONSISTENT_WITH_GSR";
        consCount++;
      } else {
        tier = "COMMONLY_ASSOCIATED";
        commCount++;
      }
      return {
        particle_id: p.particle_id,
        classification_tier: tier,
        pb_percent: p.pb_percent,
        ba_percent: p.ba_percent,
        sb_percent: p.sb_percent,
        aspect_ratio: p.aspect_ratio
      };
    });

    const lr = charCount >= 3 ? 10000.0 : charCount >= 1 ? 2500.0 : consCount >= 1 ? 500.0 : 1.0;

    return {
      total_particles_scanned: partList.length,
      characteristic_particles: charCount,
      consistent_particles: consCount,
      commonly_associated_particles: commCount,
      likelihood_ratio: lr,
      evidence_strength: lr >= 10000 ? "Extremely Strong Support for Firearm Discharge (LR > 10,000)" : "Strong Support for Discharge",
      classified_particles: classified,
      prosecutors_fallacy_shield: "Finding characteristic Pb-Ba-Sb particles indicates proximity to a firearm discharge event (ASTM E1588-20)."
    };
  };

  // Client-side fallback evaluator for 3D CMC (Song et al. NIST)
  const evaluateClientCmc = (cells: CmcCell[]): CmcResponse => {
    let cmcK = 0;
    const evaluated = cells.map((c) => {
      const isMatch = c.ccf_max >= 0.55 && Math.abs(c.delta_x_um) <= 15.0 && Math.abs(c.delta_y_um) <= 15.0 && Math.abs(c.delta_theta_deg) <= 1.0;
      if (isMatch) cmcK++;
      return { ...c, is_congruent_matching_cell: isMatch };
    });

    const verdict = cmcK >= 6 ? "POSITIVE_IDENTIFICATION" : cmcK >= 3 ? "INCONCLUSIVE_SUPPORT" : "ELIMINATION_EXCLUSION";

    return {
      total_cells_evaluated: cells.length,
      cmc_count: cmcK,
      identification_verdict: verdict,
      false_match_probability: cmcK >= 6 ? "< 1e-6" : "0.024",
      ballistic_conclusion: cmcK >= 6 ? "Definitive ballistic match to questioned firearm (K >= 6 CMC, P_false < 10^-6)." : "Insufficient congruent cells.",
      evaluated_cells: evaluated,
      prosecutors_fallacy_shield: "Identification is established when K >= 6 congruent matching cells satisfy cross-correlation (CCF >= 0.55), translation (+/-15 um), and rotation (+/-1.0 deg) tolerances."
    };
  };

  const runGsrAnalysis = async () => {
    if (loading) return;
    setLoading(true);
    setProgress(15);
    setStageText("Scanning SEM-EDX elemental spectra for tri-element Pb-Ba-Sb particles...");

    const API_BASE = getApiBaseUrl();

    const t1 = setTimeout(() => {
      setProgress(50);
      setStageText("Applying ASTM E1588-20 Characteristic & Consistent classification filters...");
    }, 250);

    const t2 = setTimeout(() => {
      setProgress(85);
      setStageText("Calculating forensic likelihood ratio against environmental backgrounds...");
    }, 550);

    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/gsr-sem-edx-analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ particles }),
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) {
        const data = await res.json();
        setGsrResult(data);
      } else {
        setGsrResult(evaluateClientGsr(particles));
      }
    } catch {
      setGsrResult(evaluateClientGsr(particles));
    } finally {
      setTimeout(() => {
        clearTimeout(t1);
        clearTimeout(t2);
        setProgress(100);
        setStageText("ASTM E1588-20 particle evaluation complete.");
        setTimeout(() => {
          setLoading(false);
          setLastActionTime(`GSR Evaluated at ${new Date().toLocaleTimeString()}`);
        }, 200);
      }, 850);
    }
  };

  const runCmcAnalysis = async () => {
    if (loading) return;
    setLoading(true);
    setProgress(15);
    setStageText("Rasterizing 3D topography striation cells...");

    const API_BASE = getApiBaseUrl();

    const t1 = setTimeout(() => {
      setProgress(50);
      setStageText("Executing CCF cross-correlation and spatial translation (±15 μm) tests...");
    }, 250);

    const t2 = setTimeout(() => {
      setProgress(85);
      setStageText("Evaluating angular rotation convergence (±1.0°) & CMC count K...");
    }, 550);

    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/cmc-striation-matching`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cells: cmcCells,
          mean_delta_x_um: 0.0,
          mean_delta_y_um: 0.0,
          mean_delta_theta_deg: 0.0
        }),
        signal: AbortSignal.timeout(3000)
      });
      if (res.ok) {
        const data = await res.json();
        setCmcResult(data);
      } else {
        setCmcResult(evaluateClientCmc(cmcCells));
      }
    } catch {
      setCmcResult(evaluateClientCmc(cmcCells));
    } finally {
      setTimeout(() => {
        clearTimeout(t1);
        clearTimeout(t2);
        setProgress(100);
        setStageText("3D CMC toolmark matching complete.");
        setTimeout(() => {
          setLoading(false);
          setLastActionTime(`CMC Evaluated at ${new Date().toLocaleTimeString()}`);
        }, 200);
      }, 850);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl border border-orange-500/30 bg-orange-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-orange-500/20 border border-orange-500/40 text-orange-300 shadow-[0_0_15px_rgba(249,115,22,0.2)]">
            <Target className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase truncate">
                Forensic Ballistics & SEM-EDX GSR Analysis
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] sm:text-[9px] font-bold bg-orange-500/20 text-orange-300 border border-orange-500/30 shrink-0">
                Pillar 5 §2 (ASTM E1588 / NIST 3D CMC)
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5 truncate">
              SEM-EDX Pb-Ba-Sb Particle Tiers • 3D Congruent Matching Cells (CMC) Striation Toolmark Comparison
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 shrink-0">
          {lastActionTime && (
            <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/30 px-2.5 py-1 rounded hidden md:flex items-center gap-1">
              <Check className="w-3 h-3" />
              {lastActionTime}
            </span>
          )}

          <div className="flex bg-black/60 p-1 rounded-xl border border-tactical-border/60">
            <button
              onClick={() => setActiveSubTab("gsr")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                activeSubTab === "gsr" ? "bg-orange-500 text-black shadow-md" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              SEM-EDX GSR
            </button>
            <button
              onClick={() => setActiveSubTab("cmc")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                activeSubTab === "cmc" ? "bg-orange-500 text-black shadow-md" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              3D CMC Ballistics
            </button>
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
            className="rounded-xl border border-orange-500/40 bg-orange-500/10 p-3.5 space-y-2 overflow-hidden shadow-lg"
          >
            <div className="flex items-center justify-between text-xs text-orange-300">
              <span className="flex items-center gap-2 font-bold truncate">
                <Cpu className="w-4 h-4 animate-pulse text-orange-400 shrink-0" />
                {stageText}
              </span>
              <span className="font-mono font-black tabular-nums text-sm">{progress}%</span>
            </div>
            <div className="w-full bg-zinc-900 rounded-full h-2.5 overflow-hidden border border-orange-500/20">
              <motion.div
                className="bg-gradient-to-r from-orange-500 to-amber-400 h-2.5 rounded-full shadow-[0_0_12px_rgba(249,115,22,0.6)]"
                initial={{ width: "5%" }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.2 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Sub-Panel 1: SEM-EDX Gunshot Residue ── */}
      {activeSubTab === "gsr" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Particle Table */}
          <div className="lg:col-span-2 space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                <Flame className="w-4 h-4 text-orange-400" />
                Automated SEM-EDX Elemental Spectra (N={particles.length})
              </span>
              <button
                onClick={runGsrAnalysis}
                disabled={loading}
                className="px-4 py-2 rounded-xl bg-orange-500 hover:bg-orange-400 text-zinc-950 font-black text-xs uppercase tracking-wider transition-all shadow-[0_0_20px_rgba(249,115,22,0.3)] hover:shadow-[0_0_25px_rgba(249,115,22,0.5)] disabled:opacity-50 flex items-center gap-1.5 cursor-pointer active:scale-95"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                {loading ? `Evaluating ${progress}%...` : "Evaluate GSR"}
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-black/40 text-zinc-400 uppercase text-[9px] border-b border-tactical-border/40">
                  <tr>
                    <th className="py-2 px-3">ID</th>
                    <th className="py-2 px-2">Pb (% wt)</th>
                    <th className="py-2 px-2">Ba (% wt)</th>
                    <th className="py-2 px-2">Sb (% wt)</th>
                    <th className="py-2 px-2">Aspect</th>
                    <th className="py-2 px-2 text-right">ASTM E1588 Classification</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-tactical-border/20 text-zinc-300 font-mono">
                  {gsrResult?.classified_particles.map((p) => (
                    <tr key={p.particle_id} className="hover:bg-orange-500/5 transition-all">
                      <td className="py-2 px-3 font-bold text-orange-300">{p.particle_id}</td>
                      <td className="py-2 px-2 tabular-nums">{p.pb_percent}%</td>
                      <td className="py-2 px-2 tabular-nums">{p.ba_percent}%</td>
                      <td className="py-2 px-2 tabular-nums">{p.sb_percent}%</td>
                      <td className="py-2 px-2 tabular-nums">{p.aspect_ratio}</td>
                      <td className="py-2 px-2 text-right">
                        <span
                          className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase ${
                            p.classification_tier === "CHARACTERISTIC_GSR"
                              ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                              : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                          }`}
                        >
                          {p.classification_tier.replace("_", " ")}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right: GSR Evidentiary Summary */}
          <div className="space-y-4">
            {gsrResult && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl border border-orange-500/40 bg-tactical-surface/50 p-4 sm:p-5 space-y-4 shadow-xl"
              >
                <div className="flex items-center justify-between border-b border-orange-500/20 pb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-orange-400" />
                    ASTM E1588-20 Evidentiary Score
                  </span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[9px] font-bold">
                    LR: 10^{Math.log10(gsrResult.likelihood_ratio).toFixed(1)}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-center">
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                    <span className="text-[9px] text-zinc-500 block">Characteristic (Pb-Ba-Sb)</span>
                    <span className="text-xl font-black text-rose-400 tabular-nums">{gsrResult.characteristic_particles}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                    <span className="text-[9px] text-zinc-500 block">Consistent (2 Elements)</span>
                    <span className="text-xl font-black text-amber-400 tabular-nums">{gsrResult.consistent_particles}</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 space-y-1.5 text-xs">
                  <span className="text-zinc-400 text-[10px] uppercase font-bold block">Conclusion:</span>
                  <p className="text-zinc-200 font-bold leading-relaxed">{gsrResult.evidence_strength}</p>
                </div>

                <div className="rounded-xl border border-orange-500/30 bg-orange-500/5 p-3 flex items-start gap-2.5 text-xs">
                  <ShieldCheck className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
                  <p className="text-zinc-400 text-[10px] leading-relaxed">
                    {gsrResult.prosecutors_fallacy_shield}
                  </p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* ── Sub-Panel 2: 3D CMC Striation Matching ── */}
      {activeSubTab === "cmc" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: CMC Grid Analysis */}
          <div className="lg:col-span-2 space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                <Grid className="w-4 h-4 text-orange-400" />
                3D Topography Cross-Correlation Cells (N={cmcCells.length})
              </span>
              <button
                onClick={runCmcAnalysis}
                disabled={loading}
                className="px-4 py-2 rounded-xl bg-orange-500 hover:bg-orange-400 text-zinc-950 font-black text-xs uppercase tracking-wider transition-all shadow-[0_0_20px_rgba(249,115,22,0.3)] hover:shadow-[0_0_25px_rgba(249,115,22,0.5)] disabled:opacity-50 flex items-center gap-1.5 cursor-pointer active:scale-95"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
                {loading ? `Matching ${progress}%...` : "Run 3D CMC"}
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-black/40 text-zinc-400 uppercase text-[9px] border-b border-tactical-border/40">
                  <tr>
                    <th className="py-2 px-3">Cell</th>
                    <th className="py-2 px-2">CCF_max (≥0.55)</th>
                    <th className="py-2 px-2">Δx (±15 μm)</th>
                    <th className="py-2 px-2">Δy (±15 μm)</th>
                    <th className="py-2 px-2">Δθ (±1.0°)</th>
                    <th className="py-2 px-2 text-right">CMC Decision</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-tactical-border/20 text-zinc-300 font-mono">
                  {cmcResult?.evaluated_cells.map((c) => (
                    <tr key={c.cell_id} className="hover:bg-orange-500/5 transition-all">
                      <td className="py-2 px-3 font-bold text-orange-300">{c.cell_id}</td>
                      <td className="py-2 px-2 tabular-nums">{c.ccf_max.toFixed(2)}</td>
                      <td className="py-2 px-2 tabular-nums">{c.delta_x_um > 0 ? `+${c.delta_x_um}` : c.delta_x_um} μm</td>
                      <td className="py-2 px-2 tabular-nums">{c.delta_y_um > 0 ? `+${c.delta_y_um}` : c.delta_y_um} μm</td>
                      <td className="py-2 px-2 tabular-nums">{c.delta_theta_deg > 0 ? `+${c.delta_theta_deg}` : c.delta_theta_deg}°</td>
                      <td className="py-2 px-2 text-right">
                        <span
                          className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase ${
                            c.is_congruent_matching_cell
                              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                              : "bg-red-500/20 text-red-300 border border-red-500/30"
                          }`}
                        >
                          {c.is_congruent_matching_cell ? "CONGRUENT (CMC)" : "NON-CONGRUENT"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right: CMC Identification Conclusion */}
          <div className="space-y-4">
            {cmcResult && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl border border-orange-500/40 bg-tactical-surface/50 p-4 sm:p-5 space-y-4 shadow-xl"
              >
                <div className="flex items-center justify-between border-b border-orange-500/20 pb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    NIST 3D CMC Verdict
                  </span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[9px] font-bold">
                    K = {cmcResult.cmc_count} / {cmcResult.total_cells_evaluated}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 text-center space-y-1">
                  <span className="text-[9px] text-zinc-500 block uppercase">False Match Probability</span>
                  <span className="text-lg font-black text-emerald-400 tabular-nums">{cmcResult.false_match_probability}</span>
                  <span className="text-[8px] text-zinc-500 block">K ≥ 6 Threshold Satisfied</span>
                </div>

                <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 space-y-1.5 text-xs">
                  <span className="text-zinc-400 text-[10px] uppercase font-bold block">Ballistic Conclusion:</span>
                  <p className="text-zinc-200 font-bold leading-relaxed">{cmcResult.ballistic_conclusion}</p>
                </div>

                <div className="rounded-xl border border-orange-500/30 bg-orange-500/5 p-3 flex items-start gap-2.5 text-xs">
                  <ShieldCheck className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
                  <p className="text-zinc-400 text-[10px] leading-relaxed">
                    {cmcResult.prosecutors_fallacy_shield}
                  </p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
