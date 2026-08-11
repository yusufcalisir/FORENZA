"use client";

import { useState } from "react";
import { Fingerprint, Dna, Activity, Layers, ShieldCheck, AlertCircle } from "lucide-react";

export default function TouchDnaPanel() {
  const [selectedSubstrate, setSelectedSubstrate] = useState<string>("TEXTURED_NON_POROUS");

  const substrates = [
    { type: "SMOOTH_NON_POROUS", label: "Smooth Non-Porous (Glass/Metal)", efficiency: "60%", recovery: "48.0 pg", dropout: "9.07%", status: "OPTIMAL TEMPLATE" },
    { type: "TEXTURED_NON_POROUS", label: "Textured Non-Porous (Gun Grip/Steering Wheel)", efficiency: "40%", recovery: "32.0 pg", dropout: "20.19%", status: "LOW-TEMPLATE DNA (LTDNA)" },
    { type: "POROUS_FABRIC", label: "Porous Fabric (Clothing Collar)", efficiency: "20%", recovery: "16.0 pg", dropout: "44.93%", status: "SEVERE LTDNA / HIGH DROPOUT" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-500/10 border border-orange-500/30 text-orange-400 shadow-[0_0_15px_rgba(249,115,22,0.15)]">
            <Fingerprint className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Touch DNA & Low-Template Probabilistic Genotyping
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Substrate Efficiency • Stochastic Allele Dropout P(D) = exp(-lambda * m) • MCMC Contributor Deconvolution
            </p>
          </div>
        </div>

        <span className="text-xs font-bold text-orange-400 bg-orange-500/10 border border-orange-500/20 px-3 py-1 rounded-lg">
          LTDNA SWGDAM Standard
        </span>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left 2 Cols: Substrates & Stochastic Dropout Model */}
        <div className="md:col-span-2 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Substrate Physical Transfer & Recovery Efficiency
          </span>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            {substrates.map((sub) => (
              <div
                key={sub.type}
                onClick={() => setSelectedSubstrate(sub.type)}
                className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2 ${
                  selectedSubstrate === sub.type
                    ? "bg-orange-500/15 border-orange-500/60 shadow-[0_0_15px_rgba(249,115,22,0.15)]"
                    : "bg-black/20 border-tactical-border/40 hover:border-tactical-border/80"
                }`}
              >
                <span className="text-[10px] text-zinc-400 block font-bold truncate">{sub.label}</span>
                <div className="flex items-baseline justify-between">
                  <span className="text-base font-bold text-orange-300 font-mono">{sub.efficiency}</span>
                  <span className="text-[10px] text-zinc-500">Rec: {sub.recovery}</span>
                </div>
                <p className="text-[9px] text-zinc-400">Dropout P(D): {sub.dropout}</p>
              </div>
            ))}
          </div>

          <div className="p-4 rounded-xl bg-black/30 border border-tactical-border/40 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-zinc-500 uppercase font-bold">Stochastic Dropout Curve Modeling</span>
              <span className="text-[10px] text-orange-400 font-mono">P(D | m = 32pg) = 20.19%</span>
            </div>
            <div className="w-full bg-black/50 h-2 rounded-full overflow-hidden border border-tactical-border/40">
              <div className="bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 h-full w-[20%]" />
            </div>
          </div>
        </div>

        {/* Right Col: MCMC Mixture Deconvolution Breakdown */}
        <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Metropolis-Hastings MCMC Deconvolution
          </span>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Deconvolution Status</span>
              <p className="font-bold text-emerald-400 font-mono flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                CONVERGED (10,000 Iterations)
              </p>
            </div>

            <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Contributor Mixture Proportions</span>
              <div className="space-y-1 pt-1 text-[11px] font-mono">
                <div className="flex justify-between">
                  <span className="text-orange-300">Major Contributor (K1):</span>
                  <span className="font-bold text-tactical-text">75.0%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-400">Minor Contributor (K2):</span>
                  <span className="font-bold text-tactical-text">25.0%</span>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/30 text-orange-300 space-y-1">
              <span className="text-[10px] text-zinc-400 uppercase block font-bold">Touch DNA Likelihood Ratio</span>
              <p className="text-base font-bold text-emerald-400 font-mono">log10(LR) = +6.10</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
