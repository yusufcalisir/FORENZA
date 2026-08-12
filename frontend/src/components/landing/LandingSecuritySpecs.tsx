"use client";

import { Lock, FileCheck, AlertOctagon, Cpu } from "lucide-react";
import NeonDnaScroll from "./NeonDnaScroll";

const SECURITY_PILLARS = [
    {
        icon: Lock,
        title: "Zero-Knowledge Privacy Auditor",
        desc: "Raw STR allele profiles remain confined to isolated execution enclaves. Circom/SnarkJS zkSNARK circuits generate Groth16 cryptographic proofs confirming DNA match criteria without transmitting raw genomic profile data.",
        color: "#22C55E",
    },
    {
        icon: FileCheck,
        title: "Immutable Chain of Custody",
        desc: "Every LIMS accessioning event, workflow SOP step, QA/QC verdict, analyst sign-off, and ISO report is SHA-256 hashed and anchored to a Polygon cryptographic ledger with HMAC audit verification.",
        color: "#06B6D4",
    },
    {
        icon: AlertOctagon,
        title: "Data Isolation Architecture",
        desc: "Forensic evidence samples are processed in isolated memory enclaves with strict zero-persistence private profile bounds. Post-analysis, only anonymized aggregate statistics and ZK proof artifacts are retained.",
        color: "#8B5CF6",
    },
    {
        icon: Cpu,
        title: "Federated Peer Computation",
        desc: "Cross-jurisdiction forensic queries run across a decentralized peer registry. No single node accesses complete genetic databases, and inter-node matching tasks are cryptographically verified.",
        color: "#22C55E",
    },
];

const SPECS = [
    { label: "Autosomal STR Support", value: "CODIS 24 Core Loci (D3S1358, vWA, FGA, D8S1179, D21S11, D18S51, SE33, etc.)", color: "#22C55E" },
    { label: "Lineage Forensics", value: "Y-STR (Clopper-Pearson 95% CI), X-STR (KI_X Linkage), mtDNA rCRS Alignment", color: "#06B6D4" },
    { label: "Probabilistic Mixture MCMC", value: "Metropolis-Hastings 2-4 Contributor Deconvolution with Dropout (p_d) & Drop-in (p_i)", color: "#8B5CF6" },
    { label: "Phenotype & Epigenetics", value: "HIrisPlex-S Extended (Eye/Hair/Skin/Freckles) & Horvath 5-CpG Epigenetic Age Clock", color: "#22C55E" },
    { label: "Population Models", value: "NRC II Recommendation 4.1 & 4.2 Balding-Nichols Dirichlet Subpopulation Fst Correction", color: "#06B6D4" },
    { label: "Instrument Ingestion", value: "Automated Gateway for CE GeneMapper CSV, qPCR Quantifiler Trio Cq/DI & NGS MiSeq VCF", color: "#8B5CF6" },
    { label: "ISO 17025 Compliance", value: "8-Section Formal Certificate Compiler, 7-Point QA/QC Inspection & Expert Witness Court Mode", color: "#22C55E" },
    { label: "Verified Invariants", value: "215/215 Automated Pytest Execution Suite (100% Pass Rate)", color: "#06B6D4" },
    { label: "Frontend Stack", value: "Next.js 16 Turbopack App Router, React 19, Tailwind CSS, Framer Motion", color: "#8B5CF6" },
    { label: "Backend Stack", value: "FastAPI (Python 3.12), PyTorch, Scikit-learn, MCMC Metropolis-Hastings Engine", color: "#22C55E" },
    { label: "Privacy Auditor", value: "Circom zkSNARK Groth16 Proof Engine + Polygon Cryptographic Ledger", color: "#06B6D4" },
    { label: "Master Platform OS", value: "FORENZA Forensic Evidence OS 6-Layer Directed Acyclic Graph (DAG) v3.0.0-PROD", color: "#8B5CF6" },
];

export default function LandingSecuritySpecs() {
    return (
        <section id="security" className="scroll-mt-20 flex flex-col justify-between py-16 px-4 bg-tactical-surface/30 border-b border-tactical-border/60">
            <div className="mx-auto max-w-7xl w-full space-y-12">
                
                {/* Header */}
                <div className="text-center max-w-3xl mx-auto space-y-3">
                    <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 shadow-lg">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="font-mono text-xs font-bold text-emerald-300 uppercase tracking-wider">
                            Security, Specifications & ISO Standards
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-extrabold font-mono text-white tracking-tight">
                        Privacy by Design, Certified Admissibility
                    </h2>
                    <p className="max-w-2xl mx-auto text-zinc-400 font-mono text-xs sm:text-sm leading-relaxed">
                        Built on non-negotiable security principles and mathematical invariants ensuring complete compliance with ISO/IEC 17025:2017, SWGDAM, and ENFSI guidelines.
                    </p>
                </div>

                {/* Security Pillars */}
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                    {SECURITY_PILLARS.map((pillar) => {
                        const Icon = pillar.icon;
                        return (
                            <div
                                key={pillar.title}
                                className="rounded-2xl border border-tactical-border/80 bg-tactical-surface p-5 shadow-xl hover:border-emerald-500/40 transition-colors"
                            >
                                <div
                                    className="mb-3 inline-flex h-9 w-9 items-center justify-center rounded-xl border"
                                    style={{
                                        background: `${pillar.color}15`,
                                        borderColor: `${pillar.color}30`,
                                        color: pillar.color,
                                    }}
                                >
                                    <Icon className="h-4.5 w-4.5" />
                                </div>
                                <h3 className="font-mono font-bold text-zinc-200 text-sm mb-1.5 leading-snug">
                                    {pillar.title}
                                </h3>
                                <p className="font-mono text-zinc-400 text-xs leading-relaxed">
                                    {pillar.desc}
                                </p>
                            </div>
                        );
                    })}
                </div>

                {/* Technical Specifications Table */}
                <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface overflow-hidden shadow-2xl font-mono">
                    <div className="border-b border-tactical-border/60 bg-black/60 px-6 py-4 flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-zinc-200">
                            Technical Platform Specifications & Standards Matrix
                        </span>
                        <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[9px] font-bold uppercase">
                            215/215 PASSED
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-tactical-border/40">
                        <div className="divide-y divide-tactical-border/40">
                            {SPECS.slice(0, 6).map((spec, i) => (
                                <div key={i} className="px-6 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-1 hover:bg-black/20 transition-colors">
                                    <span className="text-xs font-bold text-zinc-400">{spec.label}</span>
                                    <span className="text-xs font-bold text-zinc-200 sm:text-right">{spec.value}</span>
                                </div>
                            ))}
                        </div>
                        <div className="divide-y divide-tactical-border/40">
                            {SPECS.slice(6).map((spec, i) => (
                                <div key={i} className="px-6 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-1 hover:bg-black/20 transition-colors">
                                    <span className="text-xs font-bold text-zinc-400">{spec.label}</span>
                                    <span className="text-xs font-bold text-zinc-200 sm:text-right">{spec.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <NeonDnaScroll targetId="faq" />
            </div>
        </section>
    );
}
