"use client";

import NeonDnaScroll from "./NeonDnaScroll";

const PIPELINE_STEPS = [
    {
        step: "01",
        title: "Multi-Omic Ingestion",
        desc: "Raw electropherogram RFU data, CODIS 24 loci, Y-STR, mtDNA, serology & mRNA ingestion.",
        tech: ["STR / SNP", "SEROLOGY", "MRNA"],
        color: "#22C55E",
    },
    {
        step: "02",
        title: "Inference Engine",
        desc: "MCMC mixture deconvolution, kinship index, HIrisPlex-S phenotype & Horvath epigenetic clock.",
        tech: ["MCMC MCMC", "HIRISPLEX-S", "HORVATH"],
        color: "#06B6D4",
    },
    {
        step: "03",
        title: "Case Graph & Ledger",
        desc: "Directed Acyclic Graph case linking, 9-step LIMS SOP accessioning & HMAC custody.",
        tech: ["CASE DAG", "LIMS SOP", "HMAC SHA-256"],
        color: "#8B5CF6",
    },
    {
        step: "04",
        title: "ISO 17025 QA/QC",
        desc: "7-Point quality inspection matrix, heterozygote balance Hb, stochastic threshold ST & controls.",
        tech: ["7-POINT QC", "HB BALANCE", "NC/PC GATE"],
        color: "#22C55E",
    },
    {
        step: "05",
        title: "Human Governance",
        desc: "Analyst dual sign-off review, override rationale logging, and Prosecutor's Fallacy shield.",
        tech: ["DUAL SIG", "OVERRIDE AUDIT", "FALLACY SHIELD"],
        color: "#06B6D4",
    },
    {
        step: "06",
        title: "Court Reporting",
        desc: "8-Section formal ISO 17025 certificate compilation, PDF export, and Expert Witness Court Brief.",
        tech: ["ISO 17025 CERT", "PDF EXPORT", "COURT BRIEF"],
        color: "#8B5CF6",
    },
];

export default function LandingArchitecture() {
    return (
        <section id="architecture" className="scroll-mt-20 min-h-[85vh] lg:min-h-screen flex flex-col justify-between py-12 px-4">
            <div className="my-auto mx-auto max-w-7xl w-full">
                {/* Section header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 rounded-full border border-[#8B5CF6]/30 bg-[#8B5CF6]/5 px-4 py-1.5 mb-3 shadow-[0_0_15px_rgba(139,92,246,0.1)]">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#8B5CF6] animate-pulse" />
                        <span className="font-mono text-[10px] tracking-widest text-[#8B5CF6] uppercase font-bold">
                            Forensic Evidence OS Architecture
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-bold text-tactical-text mb-3">
                        6-Layer Directed Acyclic Pipeline
                    </h2>
                    <p className="max-w-xl mx-auto text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                        From raw multi-omic input to certified court admissibility in six deterministic stages.
                        Every transition is logged, validated, and cryptographically auditable.
                    </p>
                </div>

                {/* Desktop horizontal pipeline */}
                <div className="hidden lg:block relative mb-10">
                    {/* Connecting line */}
                    <div className="absolute top-[48px] left-0 right-0 h-px bg-gradient-to-r from-[#22C55E]/20 via-[#8B5CF6]/40 to-[#8B5CF6]/20" />

                    <div className="grid grid-cols-6 gap-3">
                        {PIPELINE_STEPS.map((step) => (
                            <div key={step.step} className="flex flex-col items-center">
                                {/* Step number node */}
                                <div
                                    className="relative z-10 flex h-[48px] w-[48px] mb-5 items-center justify-center rounded-full border-2 font-mono text-xs font-bold transition-all"
                                    style={{
                                        borderColor: step.color,
                                        background: `${step.color}15`,
                                        color: step.color,
                                        boxShadow: `0 0 20px ${step.color}30`,
                                    }}
                                >
                                    {step.step}
                                </div>

                                {/* Card */}
                                <div className="rounded-xl border border-tactical-border bg-tactical-surface p-3.5 w-full h-full hover:border-tactical-border/80 transition-colors shadow-md flex flex-col justify-between">
                                    <div>
                                        <h3 className="font-semibold text-tactical-text text-xs mb-1.5 leading-snug">{step.title}</h3>
                                        <p className="text-tactical-text-dim text-[10px] leading-relaxed mb-3">{step.desc}</p>
                                    </div>
                                    <div className="flex flex-wrap gap-1 mt-auto">
                                        {step.tech.map((t) => (
                                            <span
                                                key={t}
                                                className="font-mono text-[9px] tracking-wider rounded px-1.5 py-0.5"
                                                style={{ color: step.color, background: `${step.color}10` }}
                                            >
                                                {t}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Mobile vertical pipeline */}
                <div className="lg:hidden space-y-3 mb-8">
                    {PIPELINE_STEPS.map((step, idx) => (
                        <div key={step.step} className="flex gap-3">
                            {/* Left: step number + connector */}
                            <div className="flex flex-col items-center">
                                <div
                                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border-2 font-mono text-xs font-bold"
                                    style={{
                                        borderColor: step.color,
                                        background: `${step.color}15`,
                                        color: step.color,
                                    }}
                                >
                                    {step.step}
                                </div>
                                {idx < PIPELINE_STEPS.length - 1 && (
                                    <div
                                        className="mt-1 w-px flex-1 min-h-[20px]"
                                        style={{ background: `${step.color}40` }}
                                    />
                                )}
                            </div>
                            {/* Right: content */}
                            <div className="rounded-xl border border-tactical-border bg-tactical-surface p-3.5 flex-1 mb-3">
                                <h3 className="font-semibold text-tactical-text text-xs mb-1">{step.title}</h3>
                                <p className="text-tactical-text-muted text-[11px] leading-relaxed mb-2.5">{step.desc}</p>
                                <div className="flex flex-wrap gap-1.5">
                                    {step.tech.map((t) => (
                                        <span
                                            key={t}
                                            className="font-mono text-[9px] tracking-wider rounded px-2 py-0.5"
                                            style={{ color: step.color, background: `${step.color}10` }}
                                        >
                                            {t}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Full Technology Stack */}
                <div className="rounded-2xl border border-tactical-border bg-tactical-surface p-6 shadow-xl">
                    <h3 className="font-mono text-xs tracking-widest text-tactical-text-dim uppercase mb-4 text-center">
                        Full Technology Stack & Platform Invariants
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                        {[
                            { label: "FastAPI 3.12", sub: "Python Backend Core", color: "#22C55E" },
                            { label: "Next.js 16", sub: "Turbopack Frontend", color: "#06B6D4" },
                            { label: "215 Test Invariants", sub: "Pytest Suite (100%)", color: "#8B5CF6" },
                            { label: "Circom ZKP", sub: "Groth16 SnarkJS", color: "#22C55E" },
                            { label: "Polygon Anchor", sub: "Blockchain Ledger", color: "#06B6D4" },
                            { label: "ISO/IEC 17025", sub: "Court Admissible", color: "#8B5CF6" },
                        ].map((t) => (
                            <div
                                key={t.label}
                                className="rounded-lg border border-tactical-border bg-tactical-bg/40 p-3 text-center"
                            >
                                <p className="font-mono text-xs font-bold mb-0.5" style={{ color: t.color }}>
                                    {t.label}
                                </p>
                                <p className="font-mono text-[9px] tracking-widest text-tactical-text-dim uppercase">
                                    {t.sub}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Neon Scroll to Solutions (Desktop Only) */}
            <div className="hidden sm:flex pt-4 justify-center">
                <NeonDnaScroll targetId="solutions" />
            </div>
        </section>
    );
}
