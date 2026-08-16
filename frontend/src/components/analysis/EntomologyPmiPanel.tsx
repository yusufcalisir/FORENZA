"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Bug, Thermometer, Clock, ShieldCheck, RefreshCw, Calendar, Flame, AlertCircle, Info } from "lucide-react";

const SPECIES_CONFIG: Record<string, { common: string; t_base: number; stages: Record<string, number> }> = {
  "Lucilia sericata": {
    common: "Common Green Bottle Fly",
    t_base: 9.0,
    stages: {
      "Egg": 240.0,
      "1st Instar": 480.0,
      "2nd Instar": 800.0,
      "3rd Instar Feeding": 1254.5,
      "3rd Instar Post-Feeding": 2200.0,
      "Pupae": 5000.0,
      "Adult": 10174.5,
    }
  },
  "Calliphora vicina": {
    common: "European Blue Bottle Fly",
    t_base: 3.0,
    stages: {
      "Egg": 450.0,
      "1st Instar": 1170.0,
      "2nd Instar": 2250.0,
      "3rd Instar Feeding": 4050.0,
      "3rd Instar Post-Feeding": 6450.0,
      "Pupae": 9300.0,
      "Adult": 23670.0,
    }
  },
  "Chrysomya albiceps": {
    common: "Banded Blowfly",
    t_base: 10.2,
    stages: {
      "Egg": 260.0,
      "1st Instar": 740.0,
      "2nd Instar": 1340.0,
      "3rd Instar Feeding": 2440.0,
      "3rd Instar Post-Feeding": 4540.0,
      "Pupae": 8440.0,
      "Adult": 17760.0,
    }
  },
  "Phormia regina": {
    common: "Black Blowfly",
    t_base: 10.0,
    stages: {
      "Egg": 300.0,
      "1st Instar": 800.0,
      "2nd Instar": 1500.0,
      "3rd Instar Feeding": 2900.0,
      "3rd Instar Post-Feeding": 5100.0,
      "Pupae": 9200.0,
      "Adult": 19800.0,
    }
  }
};

interface PmiResponse {
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

  warning?: string;
  prosecutors_fallacy_shield: string;
}

export default function EntomologyPmiPanel() {
  const [selectedSpecies, setSelectedSpecies] = useState<string>("Lucilia sericata");
  const [selectedStage, setSelectedStage] = useState<string>("3rd Instar Feeding");
  const [deltaTMass, setDeltaTMass] = useState<number>(0.0);
  const [avgAmbientTemp, setAvgAmbientTemp] = useState<number>(20.0);
  const [samplingTime, setSamplingTime] = useState<string>("2026-08-16T12:00");
  const [loading, setLoading] = useState<boolean>(false);

  const [pmiResult, setPmiResult] = useState<PmiResponse | null>({
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
    prosecutors_fallacy_shield: "The estimated minimum PMI (PMI_min) represents the Minimum Insect Colonisation Interval (MICI) according to EAFE / NAFEA guidelines."
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const runPmiEstimation = async () => {
    setLoading(true);
    try {
      // Generate 200 hours of ambient temperatures around avgAmbientTemp
      const hourlyTemps = Array.from({ length: 240 }, (_, i) => ({
        hour_index: i,
        temperature_c: avgAmbientTemp + Math.sin(i / 12 * Math.PI) * 3.0 // realistic diurnal variation
      }));

      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/entomology-pmi-estimation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          species_name: selectedSpecies,
          development_stage: selectedStage,
          hourly_temperatures: hourlyTemps,
          delta_t_mass: deltaTMass,
          sampling_time_iso: samplingTime ? `${samplingTime}:00Z` : null
        })
      });

      if (res.ok) {
        const data = await res.json();
        setPmiResult(data);
      }
    } catch (e) {
      console.error("Entomology PMI estimation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const speciesInfo = SPECIES_CONFIG[selectedSpecies] || SPECIES_CONFIG["Lucilia sericata"];
  const stagesList = Object.keys(speciesInfo.stages);

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300">
            <Bug className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Forensic Entomology & Minimum PMI (Pillar 5 §3)
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                EAFE • NAFEA • ADD/ADH
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              Calliphoridae Thermal Summation • Larval Mass Self-Heating • Minimum Insect Colonisation Interval (MICI)
            </p>
          </div>
        </div>

        <button
          onClick={runPmiEstimation}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs uppercase tracking-wider transition-all shadow-lg flex items-center gap-2 cursor-pointer shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Calculate PMI_min
        </button>
      </div>

      {/* ── Main Layout ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Species & Development Stage Inputs */}
        <div className="space-y-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
          {/* Species Selector */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
              <Bug className="w-4 h-4 text-emerald-400" />
              Dipteran Species
            </label>
            <div className="grid grid-cols-1 gap-1.5">
              {Object.keys(SPECIES_CONFIG).map((sp) => (
                <button
                  key={sp}
                  onClick={() => {
                    setSelectedSpecies(sp);
                    if (!SPECIES_CONFIG[sp].stages[selectedStage]) {
                      setSelectedStage(Object.keys(SPECIES_CONFIG[sp].stages)[0]);
                    }
                  }}
                  className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedSpecies === sp
                      ? "border-emerald-500/80 bg-emerald-500/20 text-emerald-300 font-bold"
                      : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="text-xs italic">{sp}</div>
                  <div className="text-[10px] text-zinc-500 font-normal">
                    {SPECIES_CONFIG[sp].common} (T_base = {SPECIES_CONFIG[sp].t_base}°C)
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Development Stage */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              Oldest Development Stage
            </label>
            <div className="grid grid-cols-2 gap-1.5 text-[11px]">
              {stagesList.map((st) => (
                <button
                  key={st}
                  onClick={() => setSelectedStage(st)}
                  className={`p-2 rounded-lg border text-left transition-all cursor-pointer ${
                    selectedStage === st
                      ? "border-emerald-500/80 bg-emerald-500/20 text-emerald-300 font-bold"
                      : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="truncate">{st}</div>
                  <div className="text-[9px] text-zinc-500">{speciesInfo.stages[st]} ADH</div>
                </button>
              ))}
            </div>
          </div>

          {/* Environmental Parameters */}
          <div className="space-y-3 border-t border-tactical-border/40 pt-4">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-zinc-400">Mean Ambient Temperature</span>
                <span className="text-emerald-400 font-bold">{avgAmbientTemp.toFixed(1)}°C</span>
              </div>
              <input
                type="range"
                min="5.0"
                max="35.0"
                step="0.5"
                value={avgAmbientTemp}
                onChange={(e) => setAvgAmbientTemp(parseFloat(e.target.value))}
                className="w-full accent-emerald-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-zinc-400">Larval Mass Self-Heating (ΔT)</span>
                <span className="text-amber-400 font-bold">+{deltaTMass.toFixed(1)}°C</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="3.5"
                step="0.5"
                value={deltaTMass}
                onChange={(e) => setDeltaTMass(parseFloat(e.target.value))}
                className="w-full accent-amber-500"
              />
            </div>

            <div>
              <label className="text-[10px] text-zinc-400 uppercase font-bold block mb-1">Sampling Timestamp (ISO)</label>
              <input
                type="datetime-local"
                value={samplingTime}
                onChange={(e) => setSamplingTime(e.target.value)}
                className="w-full px-3 py-1.5 rounded-lg bg-black/40 border border-tactical-border/60 text-xs text-zinc-200"
              />
            </div>
          </div>
        </div>

        {/* Right: Minimum PMI Results */}
        <div className="lg:col-span-2 space-y-4">
          {pmiResult && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              <div className="rounded-2xl border border-emerald-500/40 bg-gradient-to-br from-emerald-500/10 via-tactical-surface/60 to-black/80 p-5 space-y-4 shadow-2xl">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-emerald-500/20 pb-3 gap-2">
                  <div>
                    <span className="text-[10px] font-bold text-emerald-300 uppercase tracking-widest block">
                      MINIMUM POST-MORTEM INTERVAL (PMI_MIN)
                    </span>
                    <div className="flex items-baseline gap-3 mt-1">
                      <span className="text-3xl font-black text-emerald-300 font-mono">
                        {pmiResult.pmi_min_hours.toFixed(1)} <span className="text-sm font-bold text-zinc-400">hours</span>
                      </span>
                      <span className="text-xl font-bold text-emerald-400/80 font-mono">
                        ({pmiResult.pmi_min_days.toFixed(2)} days)
                      </span>
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <span className="text-[10px] text-zinc-400 block uppercase font-bold">Estimated Colonisation Time</span>
                    <span className="text-xs font-bold text-amber-300 font-mono">
                      {pmiResult.colonisation_timestamp || "N/A (Provide sampling time)"}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                    <span className="text-[10px] text-zinc-500 block">Thermal Baseline (T_base)</span>
                    <span className="font-bold text-emerald-300 font-mono">{pmiResult.t_base_c}°C</span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                    <span className="text-[10px] text-zinc-500 block">Target Threshold</span>
                    <span className="font-bold text-emerald-300 font-mono">{pmiResult.target_adh} ADH</span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                    <span className="text-[10px] text-zinc-500 block">Mass Self-Heating Applied</span>
                    <span className="font-bold text-amber-400 font-mono">+{pmiResult.delta_t_mass_applied_c}°C</span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[10px] text-zinc-400">
                    <span>Cumulative Thermal Summation Progress</span>
                    <span className="font-bold text-emerald-300">
                      {pmiResult.accumulated_adh.toFixed(1)} / {pmiResult.target_adh} ADH (100%)
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-black/60 overflow-hidden border border-emerald-500/20">
                    <div className="h-full bg-emerald-500 rounded-full transition-all duration-500" style={{ width: "100%" }} />
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                  <div className="flex items-center gap-1.5 text-emerald-400 font-bold mb-1">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    EAFE / NAFEA Evaluative Legal Shield
                  </div>
                  {pmiResult.prosecutors_fallacy_shield}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
