"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  ShieldCheck,
  Dna,
  PackageCheck,
  Eye,
  Microscope,
  Fingerprint,
  Pill,
  Syringe,
  GitGraph,
  UserCheck,
  Activity,
  ArrowRight,
  Sparkles,
  FileCheck2,
  Sliders,
  CheckCircle2,
  ChevronRight
} from "lucide-react";
import Link from "next/link";
import { useIngestStore } from "@/store/ingestStore";

export default function ForensicDashboardPage() {
  const [activeCase, setActiveCase] = useState("CASE-2026-8891");
  
  // Interactive Card States
  // 1. BPA
  const [stainW, setStainW] = useState(5.2);
  const [stainL, setStainL] = useState(10.4);
  const bpaAlpha = Math.round(Math.asin(Math.min(1.0, stainW / stainL)) * (180 / Math.PI) * 100) / 100;

  // 2. Microscopy Hair
  const [hairD, setHairD] = useState(80.0);
  const [medullaD, setMedullaD] = useState(15.0);
  const medullaryIndex = Math.round((medullaD / hairD) * 1000) / 1000;
  const hairSpecies = medullaryIndex < 0.33 ? "HUMAN" : "NON_HUMAN_ANIMAL";

  // 3. Touch DNA
  const [inputMass, setInputMass] = useState(80.0);
  const [substrate, setSubstrate] = useState<"SMOOTH" | "TEXTURED" | "POROUS">("TEXTURED");
  const eff = substrate === "SMOOTH" ? 0.6 : substrate === "TEXTURED" ? 0.4 : 0.2;
  const recMass = Math.round(inputMass * eff * 10) / 10;
  const dropoutPd = Math.round(Math.exp(-0.05 * recMass) * 10000) / 100;

  // 4. Toxicology
  const [conc, setConc] = useState(0.85);
  const toxStatus = conc > 2.0 ? "FATAL" : conc > 0.5 ? "TOXIC / ELEVATED" : "THERAPEUTIC";

  return (
    <div className="p-4 sm:p-6 space-y-6 font-mono text-tactical-text bg-slate-950 min-h-screen">
      {/* ── Top Header & Case Controller Bar ── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/60 shadow-xl backdrop-blur-md">
        <div className="flex items-center gap-3.5">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.2)]">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-black tracking-widest uppercase text-tactical-text">
                FORENZA Operations Dashboard
              </h1>
              <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                ACTIVE CASE WORKSPACE
              </span>
            </div>
            <p className="text-[11px] text-tactical-text-muted mt-0.5">
              Live Forensic Intelligence Cards • Instant Subsystem Evaluation • Chain of Custody Verified
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <button
            onClick={() => {
              useIngestStore.getState().setLastIngested("test-profile-eu", "FORENSIC-LAB-ALPHA", 24);
              setActiveCase("CASE-2026-EU-01");
            }}
            className="px-3 py-1.5 rounded-xl font-mono text-xs font-bold bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/25 transition-all flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Load Sample Case EU
          </button>
          <button
            onClick={() => {
              useIngestStore.getState().setLastIngested("test-profile-aa", "DISTRICT-DNA-LAB-01", 24);
              setActiveCase("CASE-2026-AA-02");
            }}
            className="px-3 py-1.5 rounded-xl font-mono text-xs font-bold bg-purple-500/15 border border-purple-500/40 text-purple-300 hover:bg-purple-500/25 transition-all flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Load Sample Case AA
          </button>
        </div>
      </div>

      {/* ── Subsystem Biological Intelligence Cards Grid ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {/* Card 1: Crime Scene Biological Evidence (ISO 21043) */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/40 p-5 space-y-4 shadow-lg hover:border-tactical-border transition-all flex flex-col justify-between"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <PackageCheck className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  Crime Scene Evidence Ledger
                </span>
              </div>
              <span className="text-[9px] font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-2 py-0.5 rounded">
                ISO 21043
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded-xl bg-black/30 border border-tactical-border/40 space-y-1">
                <span className="text-zinc-500 text-[10px] block">Active Evidence Item</span>
                <p className="font-bold text-emerald-300 font-mono">EVID-2026-901 (Bloodstain Swab)</p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div className="p-2 rounded-lg bg-black/20 border border-tactical-border/30">
                  <span className="text-zinc-500 block">Spatial 3D</span>
                  <span className="font-bold text-zinc-300">X: 12.4m, Y: 8.2m</span>
                </div>
                <div className="p-2 rounded-lg bg-black/20 border border-tactical-border/30">
                  <span className="text-zinc-500 block">SHA-256 Custody</span>
                  <span className="font-bold text-emerald-400 font-mono truncate block">a7f9c21...e04b</span>
                </div>
              </div>
            </div>
          </div>

          <Link
            href="/analysis"
            className="mt-4 py-2 px-3 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-bold uppercase transition-all flex items-center justify-between group"
          >
            <span>Open Evidence Workspace</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </motion.div>

        {/* Card 2: Evidence Image Analysis (BPA) */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/40 p-5 space-y-4 shadow-lg hover:border-tactical-border transition-all flex flex-col justify-between"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  Image Analysis (BPA)
                </span>
              </div>
              <span className="text-[9px] font-bold bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 px-2 py-0.5 rounded">
                IABPA Standard
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[9px] text-zinc-500 block">Width W (mm)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={stainW}
                    onChange={(e) => setStainW(parseFloat(e.target.value) || 1.0)}
                    className="w-full bg-black/40 border border-tactical-border/60 rounded p-1.5 font-mono text-cyan-300 text-xs font-bold"
                  />
                </div>
                <div>
                  <label className="text-[9px] text-zinc-500 block">Length L (mm)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={stainL}
                    onChange={(e) => setStainL(parseFloat(e.target.value) || 1.0)}
                    className="w-full bg-black/40 border border-tactical-border/60 rounded p-1.5 font-mono text-cyan-300 text-xs font-bold"
                  />
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-black/30 border border-tactical-border/40 flex items-center justify-between">
                <div>
                  <span className="text-[9px] text-zinc-500 block">Impact Angle ($\alpha = \arcsin W/L$)</span>
                  <span className="text-sm font-bold text-emerald-400 font-mono">{bpaAlpha}°</span>
                </div>
                <span className="text-[9px] text-amber-300 font-bold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                  Pending Analyst Sign-Off
                </span>
              </div>
            </div>
          </div>

          <Link
            href="/analysis"
            className="mt-4 py-2 px-3 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-bold uppercase transition-all flex items-center justify-between group"
          >
            <span>Open BPA Workspace</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </motion.div>

        {/* Card 3: Microscopy Intelligence & Hair Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/40 p-5 space-y-4 shadow-lg hover:border-tactical-border transition-all flex flex-col justify-between"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Microscope className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  Microscopy Intelligence
                </span>
              </div>
              <span className="text-[9px] font-bold bg-purple-500/10 border border-purple-500/30 text-purple-400 px-2 py-0.5 rounded">
                SWGMAT Hair
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[9px] text-zinc-500 block">Hair Diam (µm)</label>
                  <input
                    type="number"
                    value={hairD}
                    onChange={(e) => setHairD(parseFloat(e.target.value) || 1.0)}
                    className="w-full bg-black/40 border border-tactical-border/60 rounded p-1.5 font-mono text-purple-300 text-xs font-bold"
                  />
                </div>
                <div>
                  <label className="text-[9px] text-zinc-500 block">Medulla Diam (µm)</label>
                  <input
                    type="number"
                    value={medullaD}
                    onChange={(e) => setMedullaD(parseFloat(e.target.value) || 0.0)}
                    className="w-full bg-black/40 border border-tactical-border/60 rounded p-1.5 font-mono text-purple-300 text-xs font-bold"
                  />
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-black/30 border border-tactical-border/40 flex items-center justify-between">
                <div>
                  <span className="text-[9px] text-zinc-500 block">Medullary Index ($I$)</span>
                  <span className="text-sm font-bold text-purple-300 font-mono">{medullaryIndex} ({hairSpecies})</span>
                </div>
                <span className="text-[9px] font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">
                  Nuclear STR Optimal
                </span>
              </div>
            </div>
          </div>

          <Link
            href="/analysis"
            className="mt-4 py-2 px-3 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-bold uppercase transition-all flex items-center justify-between group"
          >
            <span>Open Microscopy Workspace</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </motion.div>

        {/* Card 4: Touch DNA & Low-Template Genotyping */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/40 p-5 space-y-4 shadow-lg hover:border-tactical-border transition-all flex flex-col justify-between"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Fingerprint className="w-4 h-4 text-orange-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  Touch DNA & Low-Template
                </span>
              </div>
              <span className="text-[9px] font-bold bg-orange-500/10 border border-orange-500/30 text-orange-400 px-2 py-0.5 rounded">
                LTDNA MCMC
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[9px] text-zinc-500 block">Input DNA Mass (pg)</label>
                  <input
                    type="number"
                    value={inputMass}
                    onChange={(e) => setInputMass(parseFloat(e.target.value) || 1.0)}
                    className="w-full bg-black/40 border border-tactical-border/60 rounded p-1.5 font-mono text-orange-300 text-xs font-bold"
                  />
                </div>
                <div>
                  <label className="text-[9px] text-zinc-500 block">Substrate Type</label>
                  <select
                    value={substrate}
                    onChange={(e: any) => setSubstrate(e.target.value)}
                    className="w-full bg-black/40 border border-tactical-border/60 rounded p-1.5 font-mono text-orange-300 text-xs font-bold"
                  >
                    <option value="SMOOTH">Smooth Metal (60%)</option>
                    <option value="TEXTURED">Gun Grip (40%)</option>
                    <option value="POROUS">Fabric Collar (20%)</option>
                  </select>
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-black/30 border border-tactical-border/40 flex items-center justify-between">
                <div>
                  <span className="text-[9px] text-zinc-500 block">Recovered Mass / Dropout P(D)</span>
                  <span className="text-xs font-bold text-orange-300 font-mono">{recMass} pg • P(D)={dropoutPd}%</span>
                </div>
                <span className="text-[9px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
                  Log10(LR) +6.1
                </span>
              </div>
            </div>
          </div>

          <Link
            href="/analysis"
            className="mt-4 py-2 px-3 rounded-xl bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/30 text-orange-300 text-xs font-bold uppercase transition-all flex items-center justify-between group"
          >
            <span>Open Touch DNA Workspace</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </motion.div>

        {/* Card 5: Forensic Toxicology & Widmark BAC */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/40 p-5 space-y-4 shadow-lg hover:border-tactical-border transition-all flex flex-col justify-between"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Pill className="w-4 h-4 text-rose-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  Forensic Toxicology
                </span>
              </div>
              <span className="text-[9px] font-bold bg-rose-500/10 border border-rose-500/30 text-rose-400 px-2 py-0.5 rounded">
                ISO 17025 U95
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div>
                <label className="text-[9px] text-zinc-500 block">Morphine Blood Conc (mg/L)</label>
                <input
                  type="number"
                  step="0.05"
                  value={conc}
                  onChange={(e) => setConc(parseFloat(e.target.value) || 0.0)}
                  className="w-full bg-black/40 border border-tactical-border/60 rounded p-1.5 font-mono text-rose-300 text-xs font-bold"
                />
              </div>

              <div className="p-2.5 rounded-xl bg-black/30 border border-tactical-border/40 flex items-center justify-between">
                <div>
                  <span className="text-[9px] text-zinc-500 block">Threshold Evaluation</span>
                  <span className="text-xs font-bold text-rose-300 font-mono">{toxStatus}</span>
                </div>
                <span className="text-[9px] font-mono text-zinc-400">U95 = ±0.09 mg/L</span>
              </div>
            </div>
          </div>

          <Link
            href="/analysis"
            className="mt-4 py-2 px-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs font-bold uppercase transition-all flex items-center justify-between group"
          >
            <span>Open Toxicology Workspace</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </motion.div>

        {/* Card 6: Forensic Knowledge Graph */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/40 p-5 space-y-4 shadow-lg hover:border-tactical-border transition-all flex flex-col justify-between"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <GitGraph className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                  Forensic Knowledge Graph
                </span>
              </div>
              <span className="text-[9px] font-bold bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 px-2 py-0.5 rounded">
                Property Graph
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded-xl bg-black/30 border border-tactical-border/40 space-y-1">
                <span className="text-zinc-500 text-[10px] block">Case Relational Subgraph</span>
                <p className="font-bold text-indigo-300 font-mono">Case 2026-001 (14 Nodes, 18 Edges)</p>
              </div>
              <div className="p-2 rounded-lg bg-black/20 border border-tactical-border/30 flex items-center justify-between text-[10px]">
                <span className="text-zinc-500">Shortest Path d(u,v)</span>
                <span className="font-bold text-emerald-400 font-mono">2 Hops (Direct Link)</span>
              </div>
            </div>
          </div>

          <Link
            href="/investigation"
            className="mt-4 py-2 px-3 rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-bold uppercase transition-all flex items-center justify-between group"
          >
            <span>Open Graph Inspector</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </motion.div>

      </div>
    </div>
  );
}
