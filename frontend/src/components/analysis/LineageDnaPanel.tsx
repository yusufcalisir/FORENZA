"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Dna, ShieldCheck, GitCommit, Compass, RefreshCw, CheckCircle2, ChevronRight, Binary } from "lucide-react";

export default function LineageDnaPanel() {
  const [selectedTab, setSelectedTab] = useState<"ystr" | "xstr" | "mtdna">("ystr");

  // Complete 27-locus Y-FILER Plus Multiplex Panel with mutation classification
  const ystrLoci = [
    { locus: "DYS19", allele: "14.0", freq: "0.0032", rm: false, rate: "2.1e-3" },
    { locus: "DYS389I", allele: "13.0", freq: "0.0450", rm: false, rate: "2.4e-3" },
    { locus: "DYS389II", allele: "29.0", freq: "0.0180", rm: false, rate: "4.6e-3" },
    { locus: "DYS390", allele: "24.0", freq: "0.0620", rm: false, rate: "2.0e-3" },
    { locus: "DYS391", allele: "10.0", freq: "0.1200", rm: false, rate: "2.4e-3" },
    { locus: "DYS392", allele: "13.0", freq: "0.0850", rm: false, rate: "5.2e-4" },
    { locus: "DYS393", allele: "13.0", freq: "0.0910", rm: false, rate: "1.2e-3" },
    { locus: "DYS385a", allele: "11.0", freq: "0.0120", rm: false, rate: "2.3e-3", multicopy: true },
    { locus: "DYS385b", allele: "14.0", freq: "0.0084", rm: false, rate: "2.3e-3", multicopy: true },
    { locus: "DYS437", allele: "15.0", freq: "0.1100", rm: false, rate: "1.3e-3" },
    { locus: "DYS438", allele: "12.0", freq: "0.0780", rm: false, rate: "3.5e-4" },
    { locus: "DYS439", allele: "12.0", freq: "0.0540", rm: false, rate: "5.1e-3" },
    { locus: "DYS448", allele: "19.0", freq: "0.0340", rm: false, rate: "1.4e-3" },
    { locus: "DYS456", allele: "16.0", freq: "0.0670", rm: false, rate: "4.8e-3" },
    { locus: "DYS458", allele: "17.0", freq: "0.0430", rm: false, rate: "6.2e-3" },
    { locus: "DYS635", allele: "23.0", freq: "0.0510", rm: false, rate: "4.3e-3" },
    { locus: "YGATAH4", allele: "12.0", freq: "0.0890", rm: false, rate: "2.8e-3" },
    { locus: "DYS460", allele: "11.0", freq: "0.0610", rm: false, rate: "3.1e-3" },
    { locus: "DYS481", allele: "22.0", freq: "0.0290", rm: false, rate: "2.2e-3" },
    { locus: "DYS533", allele: "12.0", freq: "0.0740", rm: false, rate: "2.5e-3" },
    // 6 Rapidly Mutating (RM) Loci (7 targets)
    { locus: "DYS570", allele: "17.0", freq: "0.0150", rm: true, rate: "1.2e-2" },
    { locus: "DYS576", allele: "18.0", freq: "0.0110", rm: true, rate: "1.4e-2" },
    { locus: "DYS627", allele: "21.0", freq: "0.0090", rm: true, rate: "1.1e-2" },
    { locus: "DYS518", allele: "39.0", freq: "0.0060", rm: true, rate: "1.8e-2" },
    { locus: "DYS449", allele: "29.0", freq: "0.0080", rm: true, rate: "1.2e-2" },
    { locus: "DYF387S1a", allele: "37.0", freq: "0.0070", rm: true, rate: "1.6e-2", multicopy: true },
    { locus: "DYF387S1b", allele: "38.0", freq: "0.0050", rm: true, rate: "1.6e-2", multicopy: true },
  ];

  const [dbK, setDbK] = useState<number>(0);
  const [dbN, setDbN] = useState<number>(25000);
  const [theta, setTheta] = useState<number>(0.03);

  // Compute exact Clopper-Pearson for k=0 or normal approx for k>0
  const cpUpper = dbK === 0 ? 1.0 - Math.pow(0.05, 1.0 / (dbN + 1)) : (dbK + 1.96 * Math.sqrt((dbK * (1 - dbK / dbN)) / dbN)) / dbN;
  const cpLR = 1.0 / Math.max(cpUpper, 1e-12);
  const cpLogLR = Math.log10(cpLR);
  const brennerProb = (dbK + theta) / (dbN + theta);
  const brennerLR = 1.0 / brennerProb;


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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Lineage Status</span>
              <p className="text-lg font-bold text-emerald-400">PATERNAL MATCH (INCLUSION)</p>
              <p className="text-[9px] text-zinc-400">27-Locus Y-FILER Plus identical haplotype shared</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Clopper-Pearson 95% Bound</span>
              <p className="text-lg font-bold text-indigo-400 font-mono">p &lt; {cpUpper.toFixed(6)}</p>
              <p className="text-[9px] text-zinc-400">LR = {cpLR.toFixed(1)} (log₁₀ = {cpLogLR.toFixed(2)})</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Brenner Subpopulation (θ={theta})</span>
              <p className="text-lg font-bold text-cyan-400 font-mono">p = {brennerProb.toFixed(6)}</p>
              <p className="text-[9px] text-zinc-400">LR = {brennerLR.toFixed(1)} (k={dbK}, N={dbN})</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Mixture Deconvolution</span>
              <p className="text-lg font-bold text-purple-400 font-mono">N_male = 1 (Single Source)</p>
              <p className="text-[9px] text-zinc-400">Max 1 allele per single-copy locus</p>
            </div>
          </div>

          {/* Database Parameters Control Strip */}
          <div className="flex flex-wrap items-center justify-between gap-4 p-3 rounded-xl bg-black/30 border border-tactical-border/50 text-xs">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-zinc-500 font-bold">Observed Count (k):</span>
                <input
                  type="number"
                  min={0}
                  max={dbN}
                  value={dbK}
                  onChange={(e) => setDbK(Math.max(0, parseInt(e.target.value) || 0))}
                  className="w-16 px-2 py-1 rounded bg-black/60 border border-tactical-border text-indigo-300 font-mono font-bold text-center"
                />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-zinc-500 font-bold">Database Size (N):</span>
                <input
                  type="number"
                  min={100}
                  step={1000}
                  value={dbN}
                  onChange={(e) => setDbN(Math.max(100, parseInt(e.target.value) || 25000))}
                  className="w-24 px-2 py-1 rounded bg-black/60 border border-tactical-border text-indigo-300 font-mono font-bold text-center"
                />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-zinc-500 font-bold">Theta (θ):</span>
                <select
                  value={theta}
                  onChange={(e) => setTheta(parseFloat(e.target.value))}
                  className="px-2 py-1 rounded bg-black/60 border border-tactical-border text-cyan-300 font-mono font-bold"
                >
                  <option value={0.01}>0.01 (General)</option>
                  <option value={0.03}>0.03 (SWGDAM / NRC-II)</option>
                  <option value={0.05}>0.05 (Isolated)</option>
                </select>
              </div>
            </div>
            <div className="text-[10px] text-zinc-400 font-bold">
              SWGDAM (2020) & Y-HRD Counting Standard
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Y-FILER Plus 27-Locus Multiplex Haplotype Profile
              </span>
              <div className="flex items-center gap-2">
                <span className="text-[9px] text-pink-400 font-bold bg-pink-500/10 border border-pink-500/20 px-2 py-0.5 rounded">
                  6 RM Loci (Rapidly Mutating)
                </span>
                <span className="text-[9px] text-indigo-400 font-bold bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded">
                  27 Targets Evaluated
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-7 gap-3">
              {ystrLoci.map((item) => (
                <div
                  key={item.locus}
                  className={`rounded-lg border p-3 text-center space-y-1 ${
                    item.rm
                      ? "border-pink-500/40 bg-pink-500/5 shadow-[0_0_10px_rgba(236,72,153,0.08)]"
                      : "border-tactical-border/40 bg-black/20"
                  }`}
                >
                  <div className="flex items-center justify-center gap-1">
                    <p className="text-[9px] text-zinc-400 font-bold truncate">{item.locus}</p>
                    {item.rm && (
                      <span className="text-[7px] font-bold text-pink-400 bg-pink-500/20 px-1 py-0.2 rounded">
                        RM
                      </span>
                    )}
                  </div>
                  <p className={`text-sm font-bold font-mono ${item.rm ? "text-pink-300" : "text-indigo-400"}`}>
                    {item.allele}
                  </p>
                  <p className="text-[8px] text-zinc-500">μ = {item.rate}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}


      {/* ── Sub-tab 2: X-STR Kinship ── */}
      {selectedTab === "xstr" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Relationship Hypothesis</span>
              <p className="text-sm font-bold text-indigo-300">Paternal Half-Sisters (PHS)</p>
              <p className="text-[9px] text-zinc-400">Shared paternal X without recombination</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Combined X-Kinship Index</span>
              <p className="text-lg font-bold text-emerald-400 font-mono">KI_X = 1.854 × 10⁵</p>
              <p className="text-[9px] text-zinc-400">log₁₀(KI_X) = 5.268 (ISFG Standard)</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Evaluated Clusters</span>
              <p className="text-lg font-bold text-cyan-400 font-mono">4 / 4 Linkage Groups</p>
              <p className="text-[9px] text-zinc-400">12 Argus X-12 Loci Evaluated</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">ENFSI Verbal Scale</span>
              <p className="text-sm font-bold text-emerald-400">Extremely Strong Support</p>
              <p className="text-[9px] text-zinc-400">For common paternal ancestry</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Investigator Argus X-12 Linkage Clusters & Intra-Group Recombination (r)
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                Kosambi Map Corrected
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              {[
                {
                  group: "Linkage Group 1 (LG1 — Xp22.2)",
                  loci: "DXS10148 (12.42 Mb) • DXS10135 (13.15 Mb) • DXS8378 (14.90 Mb)",
                  recomb: "r₁₋₂ = 0.003, r₂₋₃ = 0.022",
                  ki: "KI_LG1 = 20.75",
                  status: "Paternal X Shared",
                },
                {
                  group: "Linkage Group 2 (LG2 — Xq12)",
                  loci: "DXS7132 (68.10 Mb) • DXS10074 (70.80 Mb) • DXS10079 (71.35 Mb)",
                  recomb: "r₁₋₂ = 0.015, r₂₋₃ = 0.020",
                  ki: "KI_LG2 = 20.75",
                  status: "Paternal X Shared",
                },
                {
                  group: "Linkage Group 3 (LG3 — Xq26)",
                  loci: "DXS10103 (133.50 Mb) • HPRTB (133.90 Mb) • DXS10101 (134.60 Mb)",
                  recomb: "r₁₋₂ = 0.001, r₂₋₃ = 0.012",
                  ki: "KI_LG3 = 20.75",
                  status: "Paternal X Shared",
                },
                {
                  group: "Linkage Group 4 (LG4 — Xq28)",
                  loci: "DXS10146 (148.20 Mb) • DXS10134 (149.10 Mb) • DXS7423 (150.05 Mb)",
                  recomb: "r₁₋₂ = 0.005, r₂₋₃ = 0.008",
                  ki: "KI_LG4 = 20.75",
                  status: "Paternal X Shared",
                },
              ].map((item) => (
                <div key={item.group} className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                  <div className="flex justify-between font-bold">
                    <span className="text-indigo-300">{item.group}</span>
                    <span className="text-emerald-400 font-mono">{item.ki}</span>
                  </div>
                  <p className="text-[10px] text-zinc-400">{item.loci}</p>
                  <div className="flex justify-between items-center text-[9px]">
                    <span className="text-cyan-400 font-mono">{item.recomb}</span>
                    <span className="text-emerald-400 font-semibold">{item.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}


      {/* ── Sub-tab 3: mtDNA Sequence ── */}
      {selectedTab === "mtdna" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Maternal Lineage Verdict</span>
              <p className="text-sm font-bold text-emerald-400">Cannot Be Excluded</p>
              <p className="text-[9px] text-zinc-400">0 differences across HV1/HV2/HV3</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">EMPOP Frequency Bound</span>
              <p className="text-lg font-bold text-cyan-400 font-mono">p̂_upper = 6.18 × 10⁻⁵</p>
              <p className="text-[9px] text-zinc-400">N = 48,500 (k = 0 unobserved)</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Maternal Likelihood Ratio</span>
              <p className="text-lg font-bold text-emerald-400 font-mono">LR = 16,191.7</p>
              <p className="text-[9px] text-zinc-400">log₁₀(LR_mtDNA) = 4.209</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Haplogroup Classification</span>
              <p className="text-sm font-bold text-indigo-300">Phylotree H1a</p>
              <p className="text-[9px] text-zinc-400">rCRS (NC_012920.1) aligned</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Mitochondrial Sequence Differences vs. rCRS Reference (ISFG 3' Right-Aligned)
              </span>
              <div className="flex items-center gap-2">
                <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                  ISFG Right-Aligned
                </span>
                <span className="text-[9px] text-cyan-400 font-bold bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded">
                  0 Differences (Maternal Match)
                </span>
              </div>
            </div>

            <div className="space-y-3">
              {[
                { pos: 73, ref: "A", alt: "G", region: "HV2", empop: "73G", note: "Transition" },
                { pos: 263, ref: "A", alt: "G", region: "HV2", empop: "263G", note: "Transition" },
                { pos: 309.1, ref: "-", alt: "C", region: "HV2", empop: "309.1C", note: "ISFG Poly-C Insertion" },
                { pos: 315.1, ref: "-", alt: "C", region: "HV2", empop: "315.1C", note: "ISFG Poly-C Insertion" },
                { pos: 522, ref: "CA", alt: "del", region: "HV3", empop: "522del", note: "Dinucleotide Deletion" },
                { pos: 16189, ref: "T", alt: "Y (C/T)", region: "HV1", empop: "16189Y", note: "IUPAC Point Heteroplasmy" },
                { pos: 16223, ref: "C", alt: "T", region: "HV1", empop: "16223T", note: "Transition" },
              ].map((v) => (
                <div key={v.empop} className="flex items-center justify-between p-3 rounded-xl bg-black/20 border border-tactical-border/40">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-bold text-cyan-400 font-mono">{v.empop}</span>
                    <span className="text-[10px] text-zinc-500 font-semibold">[{v.region}] Position {v.pos}</span>
                    <span className="text-[9px] text-indigo-400 font-bold bg-indigo-500/10 px-2 py-0.5 rounded">{v.note}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-bold font-mono">
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
