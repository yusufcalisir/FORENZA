"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Dna, ShieldCheck, GitCommit, Compass, RefreshCw, CheckCircle2, ChevronRight, Binary } from "lucide-react";

export default function LineageDnaPanel() {
  const [selectedTab, setSelectedTab] = useState<"ystr" | "xstr" | "mtdna">("ystr");

  // Mock Y-STR Haplotype Data (Y-FILER 23 loci)
  const ystrLoci = [
    { locus: "DYS19", allele: "14.0", freq: "0.0032" },
    { locus: "DYS385A", allele: "11.0", freq: "0.0120" },
    { locus: "DYS385B", allele: "14.0", freq: "0.0084" },
    { locus: "DYS389I", allele: "13.0", freq: "0.0450" },
    { locus: "DYS389II", allele: "29.0", freq: "0.0180" },
    { locus: "DYS390", allele: "24.0", freq: "0.0620" },
    { locus: "DYS391", allele: "10.0", freq: "0.1200" },
    { locus: "DYS392", allele: "13.0", freq: "0.0850" },
    { locus: "DYS393", allele: "13.0", freq: "0.0910" },
    { locus: "DYS437", allele: "15.0", freq: "0.1100" },
    { locus: "DYS438", allele: "12.0", freq: "0.0780" },
    { locus: "DYS439", allele: "12.0", freq: "0.0540" },
  ];

  // Mock mtDNA rCRS Variants (HV1/HV2)
  const mtdnaVariants = [
    { pos: 16189, ref: "C", alt: "T", region: "HV1", empop: "16189T" },
    { pos: 16223, ref: "C", alt: "T", region: "HV1", empop: "16223T" },
    { pos: 263, ref: "A", alt: "G", region: "HV2", empop: "263G" },
    { pos: 315.1, ref: "-", alt: "C", region: "HV2", empop: "315.1C" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.15)]">
            <Dna className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Lineage DNA Analysis Hub (Y-STR • X-STR • mtDNA)
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Paternal Haplotype Tracking • Complex X Kinship • Maternal rCRS HV1/HV2/HV3 Sequence Alignment
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setSelectedTab("ystr")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              selectedTab === "ystr" ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Y-STR Paternal
          </button>
          <button
            onClick={() => setSelectedTab("xstr")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              selectedTab === "xstr" ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            X-STR Kinship
          </button>
          <button
            onClick={() => setSelectedTab("mtdna")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              selectedTab === "mtdna" ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            mtDNA Maternal
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: Y-STR Paternal Haplotype ── */}
      {selectedTab === "ystr" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Lineage Status</span>
              <p className="text-lg font-bold text-emerald-400">PATERNAL MATCH (INCLUSION)</p>
              <p className="text-[9px] text-zinc-400">Identical 23-locus Y-FILER haplotype shared</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">SWGDAM 95% Upper Bound CI</span>
              <p className="text-lg font-bold text-indigo-400 font-mono">p &lt; 0.001198</p>
              <p className="text-[9px] text-zinc-400">Clopper-Pearson (x=0, N=2,500 database)</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Y-Haplogroup Prediction</span>
              <p className="text-lg font-bold text-cyan-400">R1b1a1b (R-M269)</p>
              <p className="text-[9px] text-zinc-400">Western European Paternal Lineage</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Y-FILER 23 Core Marker Haplotype Profile
              </span>
              <span className="text-[9px] text-indigo-400 font-bold bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded">
                23 Loci Evaluated
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {ystrLoci.map((item) => (
                <div key={item.locus} className="rounded-lg border border-tactical-border/40 bg-black/20 p-3 text-center space-y-1">
                  <p className="text-[9px] text-zinc-500 font-bold">{item.locus}</p>
                  <p className="text-sm font-bold text-indigo-400 font-mono">{item.allele}</p>
                  <p className="text-[8px] text-zinc-600">p = {item.freq}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: X-STR Kinship ── */}
      {selectedTab === "xstr" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Investigator Argus X-12 Linkage Group Kinship Analysis
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                Father-Daughter Confirmed
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              {[
                { group: "Linkage Group 1 (LG1)", loci: "DXS10148 • DXS10135 • DXS8378", ki: "KI_X = 142.50", status: "Matching Paternal X" },
                { group: "Linkage Group 2 (LG2)", loci: "DXS7132 • DXS10079 • DXS10074", ki: "KI_X = 89.20", status: "Matching Paternal X" },
                { group: "Linkage Group 3 (LG3)", loci: "DXS10101 • DXS10103 • DXS10108", ki: "KI_X = 312.80", status: "Matching Paternal X" },
                { group: "Linkage Group 4 (LG4)", loci: "DXS10146 • DXS10134 • DXS10147", ki: "KI_X = 195.40", status: "Matching Paternal X" },
              ].map((item) => (
                <div key={item.group} className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                  <div className="flex justify-between font-bold">
                    <span className="text-indigo-300">{item.group}</span>
                    <span className="text-emerald-400">{item.ki}</span>
                  </div>
                  <p className="text-[10px] text-zinc-500">{item.loci}</p>
                  <p className="text-[9px] text-zinc-400 font-semibold">{item.status}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 3: mtDNA Sequence ── */}
      {selectedTab === "mtdna" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Mitochondrial Sequence Differences vs. rCRS Reference (HV1 / HV2 / HV3)
              </span>
              <span className="text-[9px] text-cyan-400 font-bold bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded">
                0 Differences (Maternal Match)
              </span>
            </div>

            <div className="space-y-3">
              {mtdnaVariants.map((v) => (
                <div key={v.pos} className="flex items-center justify-between p-3 rounded-xl bg-black/20 border border-tactical-border/40">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold text-cyan-400 font-mono">{v.empop}</span>
                    <span className="text-[10px] text-zinc-500 font-semibold">[{v.region}] Position {v.pos}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-bold">
                    <span className="text-zinc-500">{v.ref}</span>
                    <ChevronRight className="w-3 h-3 text-zinc-600" />
                    <span className="text-cyan-300">{v.alt}</span>
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
