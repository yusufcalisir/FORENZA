"use client";

import { ReactNode } from "react";
import { ShieldCheck, Radio, Sparkles } from "lucide-react";
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
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/60 shadow-xl backdrop-blur-md">
      <div className="flex items-center gap-3.5 min-w-0">
        <div className={`flex h-10 w-10 sm:h-12 sm:w-12 shrink-0 items-center justify-center rounded-2xl ${style.bg} border ${style.border} ${style.text} ${style.shadow}`}>
          <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
        </div>
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-sm sm:text-base lg:text-lg font-black tracking-widest uppercase text-tactical-text truncate">
              {title}
            </h1>
            {badge && (
              <span className={`px-2 py-0.5 rounded text-[8px] sm:text-[9px] font-bold ${style.bg} border ${style.border} ${style.badgeText}`}>
                {badge}
              </span>
            )}
          </div>
          <p className="text-[10px] sm:text-[11px] text-tactical-text-muted mt-0.5 truncate">
            {subtitle}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-xs shrink-0">
        {actions ? (
          actions
        ) : (
          <>
            <button
              onClick={() => {
                useIngestStore.getState().setLastIngested("test-profile-eu", "FORENSIC-LAB-ALPHA", 24);
              }}
              className="px-2.5 sm:px-3 py-1.5 rounded-xl font-mono text-[10px] sm:text-xs font-bold bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/25 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <Sparkles className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
              Load Sample Case EU
            </button>
            <button
              onClick={() => {
                useIngestStore.getState().setLastIngested("test-profile-aa", "DISTRICT-DNA-LAB-01", 24);
              }}
              className="px-2.5 sm:px-3 py-1.5 rounded-xl font-mono text-[10px] sm:text-xs font-bold bg-purple-500/15 border border-purple-500/40 text-purple-300 hover:bg-purple-500/25 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <Sparkles className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
              Load Sample Case AA
            </button>
          </>
        )}
      </div>
    </div>
  );
}
