"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Cpu,
  ArrowRight,
  BookOpen,
  Sliders,
  Sparkles,
} from "lucide-react";
import ActiveProfileBanner from "@/components/common/ActiveProfileBanner";
import { useIngestStore } from "@/store/ingestStore";
import {
  SUBSYSTEM_CATEGORIES,
  COLOR_CLASSES,
} from "@/config/subsystems";

export default function AnalysisPage() {
  const { setInspectorOpen } = useIngestStore();

  return (
    <div className="space-y-6 font-mono max-w-full overflow-hidden">
      {/* ── Active Case DNA Profile & GIS Map Telemetry (Only on main Hub) ── */}
      <ActiveProfileBanner />

      {/* ── Executive Biocomputational Suites Matrix ── */}
      <div className="space-y-4">
        <div className="p-4 rounded-2xl bg-black/40 border border-tactical-border/60">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <h2 className="text-xs sm:text-sm font-extrabold uppercase tracking-wider text-white">
              Forensic Biocomputational Suites
            </h2>
            <span className="text-[9px] font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 px-2 py-0.5 rounded uppercase">
              Inference Matrix
            </span>
          </div>
          <p className="text-[10px] text-zinc-400 mt-1">
            Select a research suite to access calibrated multilocus biocomputational models, 3D spatial visualizers, and ISO 17025 validation engines.
          </p>
        </div>

        {/* 7 Research Domain Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {SUBSYSTEM_CATEGORIES.map((cat) => {
            const CatIcon = cat.icon;
            const cc = COLOR_CLASSES[cat.color] || COLOR_CLASSES.cyan;

            return (
              <motion.div
                key={cat.id}
                whileHover={{ y: -3 }}
                transition={{ duration: 0.15 }}
                className="rounded-2xl border border-tactical-border/70 bg-[#0A0F1E] p-4 sm:p-5 flex flex-col justify-between space-y-4 hover:border-cyan-500/40 transition-all shadow-lg group relative overflow-hidden"
              >
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className={`p-2.5 rounded-xl border ${cc.border} ${cc.bg}`}>
                        <CatIcon className={`w-4 h-4 ${cc.text}`} />
                      </div>
                      <div>
                        <span className="text-[8px] font-bold text-zinc-500 uppercase tracking-widest block">
                          Pillar {cat.pillarNumber}
                        </span>
                        <h3 className="text-xs font-bold text-white uppercase tracking-wider group-hover:text-cyan-300 transition-colors">
                          {cat.label}
                        </h3>
                      </div>
                    </div>
                    <span className="text-[8px] font-bold px-2 py-0.5 rounded-md bg-black/60 text-zinc-400 border border-tactical-border/60">
                      5 Modules
                    </span>
                  </div>

                  {/* Tagline & Description */}
                  <p className="text-[10px] text-zinc-300 font-medium leading-relaxed">
                    {cat.tagline}
                  </p>
                  <p className="text-[9px] text-zinc-500 line-clamp-2 leading-relaxed">
                    {cat.description}
                  </p>

                  {/* Sub-module Badges */}
                  <div className="flex flex-wrap gap-1 pt-1">
                    {cat.tabs.map((tab) => (
                      <span
                        key={tab.id}
                        className="text-[8px] font-bold px-1.5 py-0.5 rounded bg-black/50 text-zinc-400 border border-tactical-border/40"
                      >
                        {tab.badge}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action Button */}
                <div className="pt-3 border-t border-tactical-border/40 flex items-center justify-between">
                  <span className="text-[8px] text-zinc-500 font-mono flex items-center gap-1">
                    <BookOpen className="w-2.5 h-2.5 text-cyan-400" />
                    {cat.researchFile.replace("_research.md", "")}
                  </span>

                  <Link
                    href={`/analysis/${cat.id}`}
                    className="px-3 py-1.5 rounded-xl bg-zinc-800/80 hover:bg-cyan-500/20 text-zinc-300 hover:text-cyan-300 border border-zinc-700/60 hover:border-cyan-500/40 text-[9px] font-extrabold uppercase tracking-wider transition-all flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>Explore Suite</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
