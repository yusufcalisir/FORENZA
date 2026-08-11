"use client";

import { useState } from "react";
import { Sparkles, Dna, ShieldCheck, Microscope, ArrowUpRight, Scissors } from "lucide-react";

export default function MicroscopyPanel() {
  const [selectedSample, setSelectedSample] = useState<string>("HAIR-SAMPLE-501");

  const samples = [
    { id: "HAIR-SAMPLE-501", diameter: "80.0 µm", medulla: "15.0 µm", index: "0.188", origin: "HUMAN", root: "ANAGEN (WITH SHEATH)", routing: "NUCLEAR STR OPTIMAL", badge: "nDNA STR" },
    { id: "HAIR-SAMPLE-502", diameter: "80.0 µm", medulla: "50.0 µm", index: "0.625", origin: "NON_HUMAN_ANIMAL", root: "TELOGEN (NO SHEATH)", routing: "MITOCHONDRIAL HV1/HV2", badge: "mtDNA HV1/2" },
    { id: "SPERM-CELL-901", diameter: "4.5 x 2.8 µm", medulla: "N/A", index: "N/A", origin: "HUMAN SPERMATOZOA", root: "NORMAL MORPHOLOGY", routing: "DIFFERENTIAL EXTRACTION STR", badge: "DIFF-STR" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.15)]">
            <Microscope className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Microscopy Intelligence & Hair Analysis Hub
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Microscopic Cell Morphometry • Hair Medullary Index (I_medulla) • Follicular Root nDNA vs. mtDNA Routing
            </p>
          </div>
        </div>

        <span className="text-xs font-bold text-purple-400 bg-purple-500/10 border border-purple-500/20 px-3 py-1 rounded-lg">
          SWGMAT Standard Microscopy
        </span>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left 2 Cols: Sample Inventory */}
        <div className="md:col-span-2 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Microscopic Morphometry & Hair Evidence Inventory
          </span>

          <div className="space-y-3">
            {samples.map((s) => (
              <div
                key={s.id}
                onClick={() => setSelectedSample(s.id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                  selectedSample === s.id
                    ? "bg-purple-500/15 border-purple-500/60 shadow-[0_0_15px_rgba(168,85,247,0.15)]"
                    : "bg-black/20 border-tactical-border/40 hover:border-tactical-border/80"
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-tactical-text">{s.id}</span>
                    <span className="text-[9px] text-purple-300 font-bold bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                      {s.origin}
                    </span>
                  </div>
                  <p className="text-[10px] text-zinc-400">
                    Hair Diam: {s.diameter} • Medulla Diam: {s.medulla} • Root: {s.root}
                  </p>
                </div>

                <div className="flex items-center gap-3 text-xs font-mono">
                  <div className="text-right">
                    <p className="text-[9px] text-zinc-500">Medullary Index (I)</p>
                    <p className="text-purple-300 font-bold text-xs">{s.index}</p>
                  </div>
                  <span className="px-2.5 py-1 rounded text-[9px] font-bold bg-purple-500/20 border border-purple-500/40 text-purple-300 uppercase">
                    {s.badge}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Col: DNA Extraction Routing Inspector */}
        <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            DNA Strategy Decision Engine
          </span>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Selected Specimen</span>
              <p className="font-bold text-purple-300 font-mono">{selectedSample}</p>
            </div>

            <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-300 space-y-1">
              <div className="flex items-center gap-1.5 font-bold">
                <Dna className="w-4 h-4 text-purple-400" />
                <span>Recommended DNA Strategy</span>
              </div>
              <p className="text-[11px] font-bold text-emerald-400 font-mono">
                {samples.find((s) => s.id === selectedSample)?.routing || "NUCLEAR STR OPTIMAL"}
              </p>
            </div>

            <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/40 space-y-1 text-[10px] text-zinc-400">
              <p className="font-bold text-zinc-300">Routing Rationale:</p>
              <p>
                Anagen/Catagen follicular root sheath presence provides high-yield nuclear genomic DNA suitable for 24-locus CODIS STR amplification. Telogen/shaft hair relies on mtDNA HV1/HV2.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
