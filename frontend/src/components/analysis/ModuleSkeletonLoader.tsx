"use client";

import React from "react";
import { Loader2 } from "lucide-react";

export function ModuleSkeletonLoader({ label = "Loading Biocomputational Module..." }: { label?: string }) {
  return (
    <div className="w-full space-y-5 animate-pulse font-mono">
      {/* Top Banner Skeleton */}
      <div className="h-16 w-full rounded-2xl bg-tactical-surface/70 border border-tactical-border/60 p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center">
            <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />
          </div>
          <div className="space-y-1.5">
            <div className="h-4 w-48 rounded bg-zinc-800" />
            <div className="h-2.5 w-64 rounded bg-zinc-800/60" />
          </div>
        </div>
        <div className="h-8 w-28 rounded-lg bg-zinc-800 hidden sm:block" />
      </div>

      {/* Primary KPI Grid Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-24 rounded-xl bg-tactical-surface/50 border border-tactical-border/50 p-3.5 space-y-2"
          >
            <div className="h-3 w-20 rounded bg-zinc-800/60" />
            <div className="h-6 w-32 rounded bg-zinc-800" />
            <div className="h-2.5 w-16 rounded bg-zinc-800/40" />
          </div>
        ))}
      </div>

      {/* Main Computational Viewport Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 h-96 rounded-2xl bg-black/40 border border-tactical-border/60 p-6 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="h-4 w-1/3 rounded bg-zinc-800" />
            <div className="h-3 w-1/2 rounded bg-zinc-800/60" />
          </div>
          <div className="flex items-center justify-center text-xs text-zinc-500">
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />
              <span>{label}</span>
            </div>
          </div>
          <div className="h-3 w-1/4 rounded bg-zinc-800/40" />
        </div>

        <div className="h-96 rounded-2xl bg-tactical-surface/40 border border-tactical-border/60 p-5 space-y-4">
          <div className="h-4 w-1/2 rounded bg-zinc-800" />
          <div className="space-y-2.5 pt-2">
            {[1, 2, 3, 4, 5].map((j) => (
              <div key={j} className="h-10 rounded-lg bg-zinc-800/40" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ModuleSkeletonLoader;
