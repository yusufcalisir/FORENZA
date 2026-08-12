"use client";

import { ReactNode } from "react";
import { Sparkles, Dna, CheckCircle2, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useIngestStore } from "@/store/ingestStore";

interface TacticalPageHeaderProps {
  title: string;
  subtitle: string;
  badge?: string;
  icon: React.ComponentType<{ className?: string }>;
  accentColor?: "cyan" | "emerald" | "purple" | "amber";
  actions?: ReactNode;
}

export default function TacticalPageHeader({
  title,
  subtitle,
  badge = "ACTIVE WORKSPACE",
  icon: Icon,
  accentColor = "cyan",
  actions
}: TacticalPageHeaderProps) {
  const { loadSampleCaseEU, loadSampleCaseAA, setInspectorOpen, toastBanner, setToastBanner } = useIngestStore();

  const colorMap = {
    cyan: {
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/30",
      text: "text-cyan-400",
      badgeText: "text-cyan-300",
      shadow: "shadow-[0_0_20px_rgba(6,182,212,0.2)]"
    },
    emerald: {
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/30",
      text: "text-emerald-400",
      badgeText: "text-emerald-300",
      shadow: "shadow-[0_0_20px_rgba(16,185,129,0.2)]"
    },
    purple: {
      bg: "bg-purple-500/10",
      border: "border-purple-500/30",
      text: "text-purple-400",
      badgeText: "text-purple-300",
      shadow: "shadow-[0_0_20px_rgba(168,85,247,0.2)]"
    },
    amber: {
      bg: "bg-amber-500/10",
      border: "border-amber-500/30",
      text: "text-amber-400",
      badgeText: "text-amber-300",
      shadow: "shadow-[0_0_20px_rgba(245,158,11,0.2)]"
    }
  };

  const style = colorMap[accentColor];

  return (
    <div className="space-y-3 font-mono max-w-full">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/60 shadow-xl backdrop-blur-md">
        {/* Title & Icon & Subtitle Block */}
        <div className="flex items-start sm:items-center gap-3.5 min-w-0">
          <div className={`flex h-10 w-10 sm:h-12 sm:w-12 shrink-0 items-center justify-center rounded-2xl ${style.bg} border ${style.border} ${style.text} ${style.shadow} mt-0.5 sm:mt-0`}>
            <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <div className="min-w-0 space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-sm sm:text-base lg:text-lg font-black tracking-wider uppercase text-white leading-tight break-words">
                {title}
              </h1>
              {badge && (
                <span className={`px-2 py-0.5 rounded text-[8px] sm:text-[9px] font-bold ${style.bg} border ${style.border} ${style.badgeText} shrink-0`}>
                  {badge}
                </span>
              )}
            </div>
            <p className="text-[10px] sm:text-[11px] text-tactical-text-muted leading-relaxed break-words">
              {subtitle}
            </p>
          </div>
        </div>

        {/* Action Buttons Block */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 text-xs shrink-0 w-full lg:w-auto">
          {actions ? (
            actions
          ) : (
            <>
              {/* Presets Row: Side by Side on Mobile */}
              <div className="grid grid-cols-2 gap-2 w-full sm:w-auto">
                <button
                  onClick={loadSampleCaseEU}
                  className="px-2.5 sm:px-3 py-2 rounded-xl font-mono text-[9px] sm:text-xs font-bold bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/25 active:scale-95 transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-[0_0_12px_rgba(6,182,212,0.15)]"
                >
                  <Sparkles className="w-3 h-3 text-cyan-400 shrink-0" />
                  <span>Sample EU</span>
                </button>

                <button
                  onClick={loadSampleCaseAA}
                  className="px-2.5 sm:px-3 py-2 rounded-xl font-mono text-[9px] sm:text-xs font-bold bg-purple-500/15 border border-purple-500/40 text-purple-300 hover:bg-purple-500/25 active:scale-95 transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-[0_0_12px_rgba(168,85,247,0.15)]"
                >
                  <Sparkles className="w-3 h-3 text-purple-400 shrink-0" />
                  <span>Sample AA</span>
                </button>
              </div>

              {/* DNA Inspector Button */}
              <button
                onClick={() => setInspectorOpen(true)}
                className="w-full sm:w-auto px-3.5 py-2 rounded-xl font-mono text-[9px] sm:text-xs font-bold bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/25 active:scale-95 transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-[0_0_12px_rgba(16,185,129,0.15)]"
              >
                <Dna className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>DNA &amp; SNP Inspector</span>
              </button>
            </>
          )}
        </div>
      </div>

      {/* Active Toast Notification Banner */}
      <AnimatePresence>
        {toastBanner && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 p-3 rounded-xl border border-emerald-500/40 bg-emerald-950/40 text-emerald-300 text-xs shadow-lg backdrop-blur-md"
          >
            <div className="flex items-center gap-2 min-w-0">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 animate-bounce" />
              <span className="text-[10px] sm:text-xs font-mono leading-tight break-words">{toastBanner}</span>
            </div>
            <div className="flex items-center gap-2 shrink-0 self-end sm:self-auto">
              <button
                onClick={() => setInspectorOpen(true)}
                className="px-2 py-1 rounded text-[9px] sm:text-[10px] font-bold bg-emerald-400/20 text-emerald-200 border border-emerald-400/40 hover:bg-emerald-400/30 transition-all cursor-pointer font-mono"
              >
                Inspect Profile
              </button>
              <button
                onClick={() => setToastBanner(null)}
                className="text-emerald-400 hover:text-white p-1 rounded transition-colors cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
