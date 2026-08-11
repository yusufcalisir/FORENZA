"use client";

import { useState } from "react";
import { Eye, UserCheck, ShieldAlert, Target, Compass, FileCheck } from "lucide-react";

export default function BpaImagePanel() {
  const [reviewStatus, setReviewStatus] = useState<"PENDING_HUMAN_REVIEW" | "VERIFIED_BY_ANALYST">("PENDING_HUMAN_REVIEW");

  const handleSignOff = () => {
    setReviewStatus("VERIFIED_BY_ANALYST");
  };

  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.15)]">
            <Eye className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Evidence Image Analysis & BPA Morphometry Hub
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Bloodstain Ellipse Fitting • Trigonometric Impact Angle ($\arcsin(W/L)$) • Human-in-the-Loop Analyst Review Protocol
            </p>
          </div>
        </div>

        <span className={`text-xs font-bold px-3 py-1 rounded-lg border uppercase ${
          reviewStatus === "VERIFIED_BY_ANALYST"
            ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
            : "bg-amber-500/10 border-amber-500/30 text-amber-400"
        }`}>
          {reviewStatus}
        </span>
      </div>

      {/* Grid: Morphometry & Analyst Sign-off */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left 2 Cols: Stain Morphometry & Trigonometric Diagram */}
        <div className="md:col-span-2 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
            <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
              Computer Vision Stain Morphometry & Ellipse Fitting
            </span>
            <span className="text-[9px] text-cyan-400 font-bold bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded">
              IABPA Standard Morphometry
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Stain Minor Axis (W)</span>
              <p className="text-base font-bold text-cyan-300 font-mono">5.20 mm</p>
            </div>

            <div className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Stain Major Axis (L)</span>
              <p className="text-base font-bold text-indigo-300 font-mono">10.40 mm</p>
            </div>

            <div className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Impact Angle ($\alpha$)</span>
              <p className="text-base font-bold text-emerald-400 font-mono">30.00°</p>
              <p className="text-[9px] text-zinc-400">$\alpha = \arcsin(5.2 / 10.4)$</p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-black/30 border border-tactical-border/40 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-zinc-500 uppercase block font-bold">Computer Vision Pattern Classification</span>
              <p className="text-sm font-bold text-amber-300 font-mono mt-0.5">MEDIUM / HIGH VELOCITY SPATTER</p>
            </div>
            <span className="text-[10px] text-zinc-400 bg-black/40 px-3 py-1.5 rounded-lg border border-tactical-border/60">
              Aspect Ratio W/L = 0.50
            </span>
          </div>
        </div>

        {/* Right Col: Human-in-the-Loop Analyst Verification Drawer */}
        <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Human Analyst Review Protocol
          </span>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Assigned Analyst</span>
              <p className="font-bold text-tactical-text font-mono">ANALYST-BPA-09 (IABPA Certified)</p>
            </div>

            <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Mandatory Guideline Notice</span>
              <p className="text-[10px] text-zinc-300">
                AI morphometry measurements serve as advisory quantitative aids. Final reconstruction requires certified human analyst sign-off.
              </p>
            </div>

            {reviewStatus === "PENDING_HUMAN_REVIEW" ? (
              <button
                onClick={handleSignOff}
                className="w-full py-2.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 font-bold uppercase text-xs transition-all flex items-center justify-center gap-2"
              >
                <UserCheck className="w-4 h-4" />
                Sign-Off & Certify Analysis
              </button>
            ) : (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 space-y-1">
                <div className="flex items-center gap-1.5 font-bold">
                  <FileCheck className="w-4 h-4 text-emerald-400" />
                  <span>Certified by Analyst ANALYST-BPA-09</span>
                </div>
                <p className="text-[10px] text-zinc-300">Digital signature & timestamp recorded.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
