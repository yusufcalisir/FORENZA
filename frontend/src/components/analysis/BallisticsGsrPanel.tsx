"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Target, Sparkles, ShieldCheck, RefreshCw, Layers, Grid, Flame, CheckCircle2, AlertTriangle } from "lucide-react";

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

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const runGsrAnalysis = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/gsr-sem-edx-analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ particles })
      });
      if (res.ok) {
        const data = await res.json();
        setGsrResult(data);
      }
    } catch (e) {
      console.error("GSR SEM-EDX analysis failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const runCmcAnalysis = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/cmc-striation-matching`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cells: cmcCells,
          mean_delta_x_um: 0.0,
          mean_delta_y_um: 0.0,
          mean_delta_theta_deg: 0.0
        })
      });
      if (res.ok) {
        const data = await res.json();
        setCmcResult(data);
      }
    } catch (e) {
      console.error("CMC striation matching failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-orange-500/30 bg-orange-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-orange-500/20 border border-orange-500/40 text-orange-300">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Forensic Ballistics & SEM-EDX GSR Analysis (Pillar 5 §2)
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-orange-500/20 text-orange-300 border border-orange-500/30">
                ASTM E1588-20 • AFTE
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              SEM-EDX Pb-Ba-Sb Gunshot Residue Triad • 3D Congruent Matching Cells (CMC) Striation Matching
            </p>
          </div>
        </div>

        {/* Inner Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/60 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("gsr")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeSubTab === "gsr"
                ? "bg-orange-500 text-black shadow-md"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            SEM-EDX GSR (ASTM)
          </button>
          <button
            onClick={() => setActiveSubTab("cmc")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              activeSubTab === "cmc"
                ? "bg-orange-500 text-black shadow-md"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            3D CMC Striations (AFTE)
          </button>
        </div>
      </div>

      {/* ── SubTab 1: SEM-EDX GSR ── */}
      {activeSubTab === "gsr" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Input Particles */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Flame className="w-4 h-4 text-orange-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  Scanned Particles ({particles.length})
                </span>
              </div>
              <button
                onClick={runGsrAnalysis}
                disabled={loading}
                className="px-3 py-1 rounded-lg bg-orange-500 hover:bg-orange-400 text-black font-bold text-[10px] uppercase transition-all shadow-md flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
                Evaluate GSR
              </button>
            </div>

            <div className="space-y-3">
              {particles.map((p, idx) => (
                <div key={p.particle_id} className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-2 text-xs">
                  <div className="flex items-center justify-between font-bold text-orange-300 text-[11px]">
                    <span>{p.particle_id}</span>
                    <span className="text-[10px] text-zinc-400">Aspect Ratio: {p.aspect_ratio}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-[10px]">
                    <div>
                      <span className="text-zinc-500 block">Pb (Lead)</span>
                      <span className="font-bold text-zinc-200">{p.pb_percent}%</span>
                    </div>
                    <div>
                      <span className="text-zinc-500 block">Ba (Barium)</span>
                      <span className="font-bold text-zinc-200">{p.ba_percent}%</span>
                    </div>
                    <div>
                      <span className="text-zinc-500 block">Sb (Antimony)</span>
                      <span className="font-bold text-zinc-200">{p.sb_percent}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: GSR Evaluation Results */}
          <div className="lg:col-span-2 space-y-4">
            {gsrResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-orange-500/40 bg-gradient-to-br from-orange-500/10 via-tactical-surface/60 to-black/80 p-5 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-orange-500/20 pb-3">
                    <div>
                      <span className="text-[10px] font-bold text-orange-300 uppercase tracking-widest block">
                        GSR EVIDENTIARY LIKELIHOOD RATIO
                      </span>
                      <span className="text-2xl font-black text-orange-300 font-mono">
                        LR = {gsrResult.likelihood_ratio.toLocaleString()}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">ASTM E1588-20 Strength</span>
                      <span className="text-xs font-bold text-emerald-400 font-mono">
                        {gsrResult.evidence_strength}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3 text-xs">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">Characteristic (Pb-Ba-Sb)</span>
                      <span className="font-bold text-orange-300 font-mono">{gsrResult.characteristic_particles}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">Consistent (2-Element)</span>
                      <span className="font-bold text-amber-300 font-mono">{gsrResult.consistent_particles}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">Commonly Associated</span>
                      <span className="font-bold text-zinc-400 font-mono">{gsrResult.commonly_associated_particles}</span>
                    </div>
                  </div>

                  <div className="space-y-1.5 max-h-[160px] overflow-y-auto pr-1">
                    {gsrResult.classified_particles.map((cp) => (
                      <div key={cp.particle_id} className="flex items-center justify-between p-2 rounded-lg bg-black/40 border border-tactical-border/40 text-[11px] font-mono">
                        <span className="font-bold text-zinc-200">{cp.particle_id}</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                          cp.classification_tier === "CHARACTERISTIC_GSR"
                            ? "bg-orange-500/20 text-orange-300 border-orange-500/40"
                            : "bg-amber-500/20 text-amber-300 border-amber-500/40"
                        }`}>
                          {cp.classification_tier}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-orange-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Evaluative Legal Shield
                    </div>
                    {gsrResult.prosecutors_fallacy_shield}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* ── SubTab 2: 3D CMC Striations ── */}
      {activeSubTab === "cmc" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: CMC Grid Cells */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Grid className="w-4 h-4 text-orange-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  LEA Striation Cells ({cmcCells.length})
                </span>
              </div>
              <button
                onClick={runCmcAnalysis}
                disabled={loading}
                className="px-3 py-1 rounded-lg bg-orange-500 hover:bg-orange-400 text-black font-bold text-[10px] uppercase transition-all shadow-md flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
                Run 3D CMC
              </button>
            </div>

            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
              {cmcCells.map((c) => (
                <div key={c.cell_id} className="p-2.5 rounded-lg bg-black/40 border border-tactical-border/40 text-[11px] font-mono space-y-1">
                  <div className="flex items-center justify-between font-bold text-zinc-300">
                    <span>{c.cell_id}</span>
                    <span className="text-orange-400">CCF: {c.ccf_max.toFixed(2)}</span>
                  </div>
                  <div className="text-[10px] text-zinc-500 flex justify-between">
                    <span>Δx: {c.delta_x_um} µm</span>
                    <span>Δy: {c.delta_y_um} µm</span>
                    <span>Δθ: {c.delta_theta_deg}°</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: CMC Identification Verdict */}
          <div className="lg:col-span-2 space-y-4">
            {cmcResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-orange-500/40 bg-gradient-to-br from-orange-500/10 via-tactical-surface/60 to-black/80 p-5 space-y-4 shadow-2xl">
                  <div className="flex items-center justify-between border-b border-orange-500/20 pb-3">
                    <div>
                      <span className="text-[10px] font-bold text-orange-300 uppercase tracking-widest block">
                        3D CMC IDENTIFICATION VERDICT
                      </span>
                      <span className="text-xl font-black text-orange-300 font-mono">
                        {cmcResult.identification_verdict}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">Congruent Cells (K)</span>
                      <span className="text-2xl font-black text-emerald-400 font-mono">
                        {cmcResult.cmc_count} / {cmcResult.total_cells_evaluated}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">False Match Probability</span>
                      <span className="font-bold text-emerald-400 font-mono">P_false {cmcResult.false_match_probability}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-500 block">Conclusion</span>
                      <span className="font-bold text-zinc-200 text-[10px]">{cmcResult.ballistic_conclusion}</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-orange-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      AFTE Criteria Legal Shield
                    </div>
                    {cmcResult.prosecutors_fallacy_shield}
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
