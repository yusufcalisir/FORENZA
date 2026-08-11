"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Leaf, MapPin, Binary, Activity, ChevronRight, Compass, ShieldCheck } from "lucide-react";

export default function BotanyPanel() {
  const [activeSubTab, setActiveSubTab] = useState<"species" | "habitat">("species");

  // Mock Botany Species Match
  const speciesHits = [
    { species: "Pinus sylvestris (Scots Pine)", family: "Pinaceae", dna_score: "99.8%", morph: "BISACCATE / RETICULATE", verdict: "CONFIRMED_SPECIES_IDENTIFICATION" },
    { species: "Quercus robur (Pedunculate Oak)", family: "Fagaceae", dna_score: "87.4%", morph: "TRICOLPATE / PSILATE", verdict: "PROBABLE_GENUS_MATCH" },
    { species: "Taraxacum officinale (Dandelion)", family: "Asteraceae", dna_score: "74.1%", morph: "TRIPORATE / ECHINATE", verdict: "MODERATE_FAMILY_MATCH" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
            <Leaf className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Forensic Botany & Palynology Hub
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Plant DNA Barcoding (rbcL • matK • trnL-trnF) • Pollen Exine Morphology • Geolocation Origin Inference
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("species")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "species" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            DNA Barcoding & Species ID
          </button>
          <button
            onClick={() => setActiveSubTab("habitat")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "habitat" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Habitat & Geolocation
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: DNA Barcoding & Species ID ── */}
      {activeSubTab === "species" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Botanical Specimen ID</span>
              <p className="text-base font-bold text-emerald-400 font-mono">BOT-SAMPLE-501</p>
              <p className="text-[9px] text-zinc-400">Pollen grain recovered from mud trace</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">DNA Barcode Markers</span>
              <p className="text-base font-bold text-tactical-text font-mono">rbcL + matK Spacer</p>
              <p className="text-[9px] text-zinc-400">CBOL land plant barcoding standard</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Top Species Match</span>
              <p className="text-base font-bold text-emerald-400 font-mono">Pinus sylvestris (99.8%)</p>
              <p className="text-[9px] text-zinc-400">Bisaccate pollen exine confirmed</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Ranked Botanical Species Match Candidates
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                CBOL Reference Database Active
              </span>
            </div>

            <div className="space-y-3">
              {speciesHits.map((h, i) => (
                <div key={i} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-black/20 border border-tactical-border/40 gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs font-bold font-mono">
                      <span className="text-emerald-300">{h.species}</span>
                      <span className="text-zinc-600">•</span>
                      <span className="text-indigo-400">{h.family}</span>
                    </div>
                    <p className="text-[10px] text-zinc-400">Pollen Exine Morphology: {h.morph}</p>
                  </div>

                  <div className="flex items-center gap-4 text-xs font-mono">
                    <div className="text-right">
                      <p className="text-[9px] text-zinc-500">DNA Similarity</p>
                      <p className="font-bold text-emerald-400">{h.dna_score}</p>
                    </div>
                    <span className="px-3 py-1 rounded text-[9px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {h.verdict.split(":")[0]}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Habitat & Geolocation ── */}
      {activeSubTab === "habitat" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Outdoor Crime Scene Geographic Origin & Ecological Habitat Inference
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                LR_habitat = 240.00
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Inferred Ecological Habitat</span>
                <p className="text-base font-bold text-emerald-400 font-mono">MONTANE_CONIFEROUS</p>
                <p className="text-[10px] text-zinc-400">Dominant pinus assemblage</p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Geographic Association</span>
                <p className="text-sm font-bold text-indigo-300 font-mono">Boreal / Subalpine Coniferous Forest</p>
                <p className="text-[10px] text-zinc-400">High elevation mountain woodland zone</p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">Seasonal Bloom Window</span>
                <p className="text-sm font-bold text-amber-300 font-mono">May – July (Late Spring / Early Summer)</p>
                <p className="text-[10px] text-zinc-400">Peak palynological dissemination</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
