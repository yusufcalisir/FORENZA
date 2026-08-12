"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Scale, ShieldAlert, CheckCircle2, FileText, Lock, RefreshCw, Cpu, Layers } from "lucide-react";

interface Pillar {
  title: string;
  summary: string;
  details: string;
  fallacy_protection_active?: boolean;
}

interface TestimonyData {
  testimony_title: string;
  case_id: string;
  sample_id: string;
  expert_witness_id: string;
  timestamp: string;
  operating_mode: string;
  testimony_pillars: Pillar[];
  prosecutors_fallacy_shield: string;
  testimony_hmac_hash: string;
  court_admissible: boolean;
}

export default function ExpertWitnessPanel() {
  const [activeMode, setActiveMode] = useState<"RESEARCH" | "COURT">("COURT");
  const [loading, setLoading] = useState(false);
  const [testimony, setTestimony] = useState<TestimonyData | null>({
    testimony_title: "EXPERT WITNESS JUDICIAL EXAMINATION BRIEF",
    case_id: "CASE-2026-COURT-01",
    sample_id: "SAMPLE-DNA-101",
    expert_witness_id: "EXPERT-01 (Dr. Sarah Connor)",
    timestamp: "2026-08-12T13:59:00Z",
    operating_mode: "COURT_EXPERT_WITNESS_MODE",
    testimony_pillars: [
      {
        title: "1. What Was Tested?",
        summary: "Accessioned evidence sample SAMPLE-DNA-101 associated with judicial case CASE-2026-COURT-01.",
        details: "Amplified using standard CODIS 24 core STR loci multiplex panel following ISO 17025 validated SOPs."
      },
      {
        title: "2. What Was Observed?",
        summary: "Clean single-source / deconvolution autosomal STR profile resolved across 24 loci.",
        details: "All loci exhibited peak height intensities above analytical threshold AT (50 RFU), with minimum peak height > 150 RFU."
      },
      {
        title: "3. What Was Calculated?",
        summary: "Likelihood Ratio (LR) = 10^26.0 (log10 LR = 26.0).",
        details: "Random Match Probability (RMP) is 1 in 10^26.0 in reference population databases."
      },
      {
        title: "4. What Assumptions Were Made?",
        summary: "Hardy-Weinberg Equilibrium (HWE) & Linkage Equilibrium across core autosomal loci.",
        details: "NRC II Recommendation 4.1 population sub-structure correction applied with Fst = 0.010."
      },
      {
        title: "5. What Does the Likelihood Ratio Mean?",
        summary: "Scientific verbal predicate: EXTREMELY STRONG SUPPORT FOR INCLUSION.",
        details: "The physical DNA evidence is 10^26.0 times more probable under the Prosecution Hypothesis (Hp) than under the Defense Hypothesis (Hd)."
      },
      {
        title: "6. What Does the Likelihood Ratio NOT Mean? (Legal Shield)",
        summary: "IMPORTANT: The LR measures evidence probability P(E|Hp), NOT defendant guilt P(Hp|E).",
        details: "Conflating evidence likelihood with defendant guilt is the 'Prosecutor's Fallacy' (Transposed Conditional Fallacy). Guilt or innocence requires evaluation of all non-scientific case evidence by the trier of fact.",
        fallacy_protection_active: true
      },
      {
        title: "7. What Are the Scientific Limitations?",
        summary: "Analysis bounded by stochastic threshold (150 RFU) and expanded measurement uncertainty U95%.",
        details: "DNA evidence evaluates source attribution only, NOT manner, activity, or time of deposition (PMI)."
      }
    ],
    prosecutors_fallacy_shield: "PROTECTED_TRANSPOSED_CONDITIONAL_SHIELD",
    testimony_hmac_hash: "b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
    court_admissible: true
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const handleGenerateBrief = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/court/generate-testimony-brief`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          case_id: "CASE-2026-COURT-01",
          sample_id: "SAMPLE-DNA-101",
          log10_lr: 26.0,
          enfsi_verbal_predicate: "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION"
        })
      });
      if (res.ok) {
        const data = await res.json();
        setTestimony(data);
      }
    } catch (e) {
      console.error("Court testimony generation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Header with Mode Toggle ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-sky-500/30 bg-sky-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sky-500/20 border border-sky-500/40 text-sky-300">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Expert Witness & Judicial Examination Subsystem
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-sky-500/20 text-sky-300 border border-sky-500/30">
                7-POINT TESTIMONY
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              Dual Operating Perspectives: Research Analyst Mode vs Expert Witness Court Mode
            </p>
          </div>
        </div>

        {/* Dual Mode Selector */}
        <div className="flex items-center gap-2 p-1 rounded-xl bg-black/60 border border-tactical-border/60">
          <button
            onClick={() => setActiveMode("RESEARCH")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeMode === "RESEARCH"
                ? "bg-zinc-800 text-zinc-200 shadow"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Research Mode
          </button>
          <button
            onClick={() => setActiveMode("COURT")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeMode === "COURT"
                ? "bg-sky-500 text-black shadow"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Court Mode (Witness)
          </button>
        </div>
      </div>

      {/* ── Mode Content Rendering ── */}
      {activeMode === "RESEARCH" ? (
        <div className="p-6 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 space-y-4 text-xs">
          <span className="text-xs font-bold uppercase tracking-wider text-sky-300 block border-b border-tactical-border/40 pb-3">
            Research & Laboratory Analyst Mode (Raw Bioinformatics)
          </span>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono">
            <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
              <span className="text-[9px] text-zinc-500 block">Raw RFU Peak Intensities</span>
              <span className="font-bold text-zinc-200">D3S1358: 1400 / 1520 RFU</span>
            </div>
            <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
              <span className="text-[9px] text-zinc-500 block">MCMC Metropolis-Hastings</span>
              <span className="font-bold text-zinc-200">100,000 Iterations (p_d = 0.02)</span>
            </div>
            <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
              <span className="text-[9px] text-zinc-500 block">Dirichlet Population Parameters</span>
              <span className="font-bold text-zinc-200">Theta Fst = 0.010 (NRC II 4.1)</span>
            </div>
          </div>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Prosecutor Fallacy Shield Warning */}
          <div className="p-4 rounded-2xl border border-amber-500/40 bg-amber-500/10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
              <div>
                <span className="text-xs font-bold text-amber-300 uppercase block">
                  Transposed Conditional Fallacy Shield Active
                </span>
                <span className="text-[10px] text-zinc-400">
                  Prevents legal misinterpretation of evidence probability P(E|Hp) as defendant guilt P(Hp|E).
                </span>
              </div>
            </div>
            <button
              onClick={handleGenerateBrief}
              disabled={loading}
              className="px-3.5 py-1.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-black font-bold text-xs uppercase flex items-center gap-2 cursor-pointer transition-all shrink-0"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh Testimony Brief
            </button>
          </div>

          {/* 7-Point Judicial Testimony Pillars Grid */}
          {testimony && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {testimony.testimony_pillars.map((pillar, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-2xl border ${
                    pillar.fallacy_protection_active
                      ? "border-amber-500/40 bg-amber-500/10 md:col-span-2"
                      : "border-tactical-border/80 bg-tactical-surface/50"
                  } space-y-2 text-xs font-mono shadow-lg`}
                >
                  <span className={`text-[10px] font-bold uppercase tracking-wider block ${
                    pillar.fallacy_protection_active ? "text-amber-300" : "text-sky-300"
                  }`}>
                    {pillar.title}
                  </span>
                  <div className="font-bold text-zinc-100">{pillar.summary}</div>
                  <div className="text-[10px] text-zinc-400 leading-relaxed">{pillar.details}</div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
