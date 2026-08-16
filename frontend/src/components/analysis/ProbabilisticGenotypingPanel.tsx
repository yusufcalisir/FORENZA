"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Activity, Flame, Sliders, TrendingUp, RefreshCw, BarChart2, ShieldCheck, Zap } from "lucide-react";

export default function ProbabilisticGenotypingPanel() {
  const [rfuThreshold, setRfuThreshold] = useState(50);
  const [sampleRfu, setSampleRfu] = useState(150);
  const [mixtureRatio, setMixtureRatio] = useState(0.70);
  const [mcmcSteps, setMcmcSteps] = useState(10000);
  const [isSampling, setIsSampling] = useState(false);

  // Compute stochastic models dynamically
  // P(D|x) = 1 / (1 + exp(-3.5 + 0.015 * x))
  const dropoutProb = 1 / (1 + Math.exp(-3.5 + 0.015 * sampleRfu));
  // P(Drop-in)
  const dropinRate = 0.05;

  // Simulate MCMC sampler trigger
  const runMCMC = () => {
    setIsSampling(true);
    setTimeout(() => {
      setIsSampling(false);
    }, 800);
  };

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Continuous Probabilistic Genotyping Engine
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Metropolis-Hastings MCMC • Logistic Dropout P(D|RFU) • Poisson Drop-in • Log-Normal Peak Heights
            </p>
          </div>
        </div>

        <button
          onClick={runMCMC}
          disabled={isSampling}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-bold uppercase tracking-wider transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isSampling ? "animate-spin" : ""}`} />
          {isSampling ? "Running MCMC..." : "Execute MCMC Sampler"}
        </button>
      </div>

      {/* ── Model Parameter Controls ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Dropout Calculator Card */}
        <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">Logistic Dropout P(D)</span>
            <span className="text-[10px] text-zinc-500">β0=-3.5, β1=0.015</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-[11px]">
              <span className="text-zinc-400">Peak Height (RFU):</span>
              <span className="text-amber-400 font-bold tabular-nums">{sampleRfu} RFU</span>
            </div>
            <input
              type="range"
              min="10"
              max="500"
              value={sampleRfu}
              onChange={(e) => setSampleRfu(Number(e.target.value))}
              className="w-full accent-amber-500 cursor-pointer"
            />
            <div className="flex justify-between items-center pt-2 border-t border-tactical-border/20">
              <span className="text-[10px] text-zinc-400">Predicted P(Dropout):</span>
              <span className={`text-xs font-bold tabular-nums ${dropoutProb > 0.5 ? "text-red-400" : "text-emerald-400"}`}>
                {(dropoutProb * 100).toFixed(2)}%
              </span>
            </div>
          </div>
        </div>

        {/* Drop-in & Stutter Model Card */}
        <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Poisson Drop-in & Stutter</span>
            <span className="text-[10px] text-zinc-500">AT Threshold</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-[11px]">
              <span className="text-zinc-400">Analytical Cutoff (AT):</span>
              <span className="text-cyan-400 font-bold tabular-nums">{rfuThreshold} RFU</span>
            </div>
            <input
              type="range"
              min="30"
              max="150"
              value={rfuThreshold}
              onChange={(e) => setRfuThreshold(Number(e.target.value))}
              className="w-full accent-cyan-500 cursor-pointer"
            />
            <div className="flex justify-between items-center pt-2 border-t border-tactical-border/20">
              <span className="text-[10px] text-zinc-400">Drop-in Rate λ_c:</span>
              <span className="text-xs font-bold text-cyan-400 tabular-nums">{dropinRate} / locus</span>
            </div>
          </div>
        </div>

        {/* MCMC Mixture Ratio Card */}
        <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
            <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">2-Person Mixture Ratio (w1)</span>
            <span className="text-[10px] text-zinc-500">w1 : w2</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-[11px]">
              <span className="text-zinc-400">Major Contributor:</span>
              <span className="text-purple-400 font-bold tabular-nums">{(mixtureRatio * 100).toFixed(0)}% : {((1 - mixtureRatio) * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.90"
              step="0.05"
              value={mixtureRatio}
              onChange={(e) => setMixtureRatio(Number(e.target.value))}
              className="w-full accent-purple-500 cursor-pointer"
            />
            <div className="flex justify-between items-center pt-2 border-t border-tactical-border/20">
              <span className="text-[10px] text-zinc-400">MCMC Iterations:</span>
              <span className="text-xs font-bold text-purple-400 tabular-nums">{mcmcSteps.toLocaleString()} steps</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── MCMC Posterior & Tippett Calibration Curves ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* MCMC Posterior Histogram Simulation */}
        <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
            <div className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-purple-400" />
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                MCMC Mixture Ratio Posterior P(w1 | Data)
              </span>
            </div>
            <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
              Converged (R-hat = 1.01)
            </span>
          </div>

          <div className="h-48 flex items-end justify-between gap-1 pt-6 px-2 border-b border-tactical-border/30">
            {[5, 12, 28, 45, 82, 135, 220, 380, 510, 420, 260, 140, 65, 30, 12, 4].map((count, i) => {
              const maxVal = 510;
              const pct = (count / maxVal) * 100;
              const isPeak = count === maxVal;
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1 group relative">
                  <div
                    style={{ height: `${pct}%` }}
                    className={`w-full rounded-t transition-all duration-500 ${isPeak ? "bg-purple-400 shadow-[0_0_12px_rgba(192,132,252,0.6)]" : "bg-purple-500/30 group-hover:bg-purple-500/60"}`}
                  />
                  <div className="absolute -top-6 hidden group-hover:block bg-zinc-900 text-purple-300 text-[8px] px-1.5 py-0.5 rounded border border-purple-500/30 z-10 whitespace-nowrap">
                    {count} samples
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex justify-between text-[9px] text-zinc-500 font-semibold">
            <span>w1 = 0.40</span>
            <span>w1 = 0.55</span>
            <span className="text-purple-400 font-bold">Mode w1 = 0.70</span>
            <span>w1 = 0.85</span>
          </div>
        </div>

        {/* Tippett Plot Calibration Curve Simulation */}
        <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 space-y-3 sm:space-y-4 shadow-lg overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
            <div className="flex items-center gap-2 min-w-0">
              <TrendingUp className="w-4 h-4 text-amber-400 shrink-0" />
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider truncate">
                Tippett Plot (Empirical Calibration Curve)
              </span>
            </div>
            <span className="text-[9px] text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded shrink-0">
              Hp vs Hd Distributions
            </span>
          </div>

          {/* Legend Badges */}
          <div className="flex flex-wrap items-center justify-between gap-2 text-[9px] sm:text-[10px] font-mono">
            <div className="text-emerald-400 font-bold flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
              <span className="w-2.5 h-0.5 bg-emerald-400 inline-block" /> True Donors P(log₁₀ LR &gt; x | Hp)
            </div>
            <div className="text-red-400 font-bold flex items-center gap-1.5 bg-red-500/10 border border-red-500/20 px-2 py-0.5 rounded">
              <span className="w-2.5 h-0.5 bg-red-400 inline-block" /> Non-Donors P(log₁₀ LR &gt; x | Hd)
            </div>
          </div>

          <div className="h-44 sm:h-48 relative flex items-center justify-center border border-dashed border-tactical-border/40 rounded-xl p-2 sm:p-4 bg-black/40 overflow-hidden">
            <svg viewBox="0 0 400 180" preserveAspectRatio="none" className="w-full h-full">
              {/* Grid Lines */}
              <line x1="20" y1="20" x2="380" y2="20" stroke="#27272A" strokeWidth="0.8" strokeDasharray="3 3" />
              <line x1="20" y1="90" x2="380" y2="90" stroke="#27272A" strokeWidth="0.8" strokeDasharray="3 3" />
              <line x1="20" y1="160" x2="380" y2="160" stroke="#27272A" strokeWidth="0.8" strokeDasharray="3 3" />
              
              <line x1="20" y1="20" x2="20" y2="160" stroke="#27272A" strokeWidth="0.8" strokeDasharray="3 3" />
              <line x1="140" y1="20" x2="140" y2="160" stroke="#27272A" strokeWidth="0.8" strokeDasharray="3 3" />
              <line x1="260" y1="20" x2="260" y2="160" stroke="#27272A" strokeWidth="0.8" strokeDasharray="3 3" />
              <line x1="380" y1="20" x2="380" y2="160" stroke="#27272A" strokeWidth="0.8" strokeDasharray="3 3" />

              {/* Threshold Invariant Indicator at LR=0 */}
              <line x1="140" y1="20" x2="140" y2="160" stroke="#F59E0B" strokeWidth="1" strokeDasharray="4 2" opacity="0.6" />

              {/* Donor Curve (Hp) - Green Dashed */}
              <path
                d="M 20 155 Q 100 145 180 85 T 380 20"
                fill="none"
                stroke="#10B981"
                strokeWidth="2.5"
                strokeDasharray="5 3"
              />
              {/* Non-Donor Curve (Hd) - Red Solid */}
              <path
                d="M 20 20 Q 140 135 260 152 T 380 158"
                fill="none"
                stroke="#EF4444"
                strokeWidth="2.5"
              />
            </svg>
          </div>

          <div className="flex justify-between text-[8px] sm:text-[9px] text-zinc-500 font-mono px-1">
            <span>log₁₀(LR) = -6.0</span>
            <span>log₁₀(LR) = 0.0</span>
            <span className="text-emerald-400 font-bold">log₁₀(LR) = +6.0</span>
            <span>log₁₀(LR) = +12.0</span>
          </div>
        </div>
      </div>
    </div>
  );
}
