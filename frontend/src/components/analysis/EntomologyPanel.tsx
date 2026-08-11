"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Bug, Thermometer, Clock, Activity, ChevronRight, AlertCircle, ShieldCheck } from "lucide-react";

export default function EntomologyPanel() {
  const [activeSubTab, setActiveSubTab] = useState<"pmi" | "succession">("pmi");

  // Interactive Form State
  const [species, setSpecies] = useState<string>("Calliphora vicina");
  const [stage, setStage] = useState<string>("INSTAR_3");
  const [ambientTemp, setAmbientTemp] = useState<number>(18.0);

  // ADH Species Constants
  const baseTemps: Record<string, number> = {
    "Calliphora vicina": 6.0,
    "Lucilia sericata": 9.0,
    "Sarcophaga carnaria": 8.0,
  };

  const reqAdhMap: Record<string, number> = {
    INSTAR_1: 350,
    INSTAR_2: 850,
    INSTAR_3: 2200,
    PUPA: 4500,
  };

  const baseTemp = baseTemps[species] || 6.0;
  const reqAdh = reqAdhMap[stage] || 2200;
  const effectiveTemp = Math.max(0.1, ambientTemp - baseTemp);
  const pmiHours = (reqAdh / effectiveTemp).toFixed(1);
  const pmiDays = (parseFloat(pmiHours) / 24.0).toFixed(1);
  const minDays = (parseFloat(pmiDays) * 0.9).toFixed(1);
  const maxDays = (parseFloat(pmiDays) * 1.1).toFixed(1);

  // Mock Succession Data
  const successionWaves = [
    { wave: "Fresh Stage Wave", period: "1–3 Days", families: ["Calliphoridae (Blowflies)", "Muscidae (Houseflies)"], status: "PRESENT" },
    { wave: "Bloated Stage Wave", period: "3–7 Days", families: ["Silphidae (Carrion Beetles)", "Histeridae (Clown Beetles)"], status: "ACTIVE" },
    { wave: "Active Decay Wave", period: "8–20 Days", families: ["Piophilidae (Cheese Skippers)", "Staphylinidae (Rove Beetles)"], status: "EMERGING" },
    { wave: "Advanced / Dry Decay", period: "25–50+ Days", families: ["Dermestidae (Skin Beetles)", "Tineidae (Moths)"], status: "ABSENT" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-lime-500/10 border border-lime-500/30 text-lime-400 shadow-[0_0_15px_rgba(132,204,22,0.15)]">
            <Bug className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Forensic Entomology & PMI_min Estimator Hub
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Accumulated Degree Hours (ADH) Thermal Models • Diptera Larval Development • Ecological Succession Waves
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("pmi")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "pmi" ? "bg-lime-500/20 text-lime-300 border border-lime-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            ADH PMI_min Estimator
          </button>
          <button
            onClick={() => setActiveSubTab("succession")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "succession" ? "bg-lime-500/20 text-lime-300 border border-lime-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Succession Waves
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: ADH PMI Estimator ── */}
      {activeSubTab === "pmi" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-5 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Insect Specimen & Thermal Data Input
              </span>
              <span className="text-[9px] text-lime-400 font-bold bg-lime-500/10 border border-lime-500/20 px-2 py-0.5 rounded">
                EAFE Standard Active
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Species Selector */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-zinc-400 uppercase">Diptera Species</label>
                <select
                  value={species}
                  onChange={(e) => setSpecies(e.target.value)}
                  className="w-full bg-black/50 border border-tactical-border/60 rounded-xl p-2 text-xs font-mono text-lime-400 focus:outline-none focus:border-lime-500"
                >
                  <option value="Calliphora vicina">Calliphora vicina (Blue Blowfly)</option>
                  <option value="Lucilia sericata">Lucilia sericata (Green Bottle Fly)</option>
                  <option value="Sarcophaga carnaria">Sarcophaga carnaria (Flesh Fly)</option>
                </select>
              </div>

              {/* Development Stage */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-zinc-400 uppercase">Development Stage</label>
                <select
                  value={stage}
                  onChange={(e) => setStage(e.target.value)}
                  className="w-full bg-black/50 border border-tactical-border/60 rounded-xl p-2 text-xs font-mono text-lime-400 focus:outline-none focus:border-lime-500"
                >
                  <option value="INSTAR_1">1st Instar Larva</option>
                  <option value="INSTAR_2">2nd Instar Larva</option>
                  <option value="INSTAR_3">3rd Instar Larva</option>
                  <option value="PUPA">Puparium Stage</option>
                </select>
              </div>

              {/* Ambient Temp Slider */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-zinc-400">Ambient Temp (°C):</span>
                  <span className="text-lime-400 font-bold">{ambientTemp}°C</span>
                </div>
                <input
                  type="range"
                  min={10.0}
                  max={35.0}
                  step={0.5}
                  value={ambientTemp}
                  onChange={(e) => setAmbientTemp(parseFloat(e.target.value))}
                  className="w-full accent-lime-500 bg-black/40 h-2 rounded-lg cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* PMI Output Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Required ADH</span>
              <p className="text-base font-bold text-lime-400 font-mono">{reqAdh} ADH</p>
              <p className="text-[9px] text-zinc-400">Threshold for {stage}</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Effective Temp (T_eff)</span>
              <p className="text-base font-bold text-tactical-text font-mono">{effectiveTemp.toFixed(1)} °C</p>
              <p className="text-[9px] text-zinc-400">T_ambient - T_base ({baseTemp}°C)</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Minimum PMI (Hours)</span>
              <p className="text-base font-bold text-amber-400 font-mono">{pmiHours} Hours</p>
              <p className="text-[9px] text-zinc-400">Elapsed colonization time</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">PMI_min Range (Days)</span>
              <p className="text-base font-bold text-emerald-400 font-mono">{minDays} – {maxDays} Days</p>
              <p className="text-[9px] text-zinc-400">90% – 110% thermal confidence interval</p>
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Succession Waves ── */}
      {activeSubTab === "succession" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Ecological Arthropod Succession Wave Audit
              </span>
              <span className="text-[9px] text-lime-400 font-bold bg-lime-500/10 border border-lime-500/20 px-2 py-0.5 rounded">
                Active Decay Stage Matched
              </span>
            </div>

            <div className="space-y-3">
              {successionWaves.map((w, idx) => (
                <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-black/20 border border-tactical-border/40 gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs font-bold font-mono">
                      <span className="text-lime-400">{w.wave}</span>
                      <span className="text-zinc-600">•</span>
                      <span className="text-amber-300">{w.period}</span>
                    </div>
                    <p className="text-[10px] text-zinc-400">Key Families: {w.families.join(", ")}</p>
                  </div>

                  <div>
                    <span className={`px-3 py-1 rounded text-[9px] font-bold uppercase font-mono ${
                      w.status === "ACTIVE"
                        ? "bg-lime-500/20 text-lime-400 border border-lime-500/30"
                        : w.status === "PRESENT"
                        ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                        : "bg-zinc-500/20 text-zinc-500 border border-zinc-500/30"
                    }`}>
                      {w.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
