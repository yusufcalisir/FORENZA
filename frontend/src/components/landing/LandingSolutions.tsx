"use client";

import { useState } from "react";
import { Search, Heart, Shield, FlaskConical, CheckCircle2, FileText } from "lucide-react";
import NeonDnaScroll from "./NeonDnaScroll";

const SOLUTIONS = [
    {
        id: "law-enforcement",
        icon: Search,
        title: "State Crime Laboratories & Cold Cases",
        subtitle: "30-Subsystem Multi-Omic Intelligence & MCMC Mixture Deconvolution",
        description:
            "Forensic genetics units upload complex 2-4 person touch DNA mixtures, receiving automated MCMC deconvolution, HIrisPlex-S phenotype reconstruction, Horvath epigenetic age estimation, and ISO 17025 certified report output within seconds.",
        bulletPoints: [
            "MCMC Metropolis-Hastings 2-4 person mixture deconvolution",
            "CODIS 24 Autosomal STR + Y-STR + X-STR + mtDNA rCRS fusion",
            "HIrisPlex-S Extended eye, hair, skin & freckles phenotype render",
            "Horvath 5-CpG epigenetic clock & AHRR lifestyle biomarkers",
        ],
        sampleMetric: "1.0e28 Likelihood Ratio",
        sampleCode: "CASE_2026_COLD_09 — 3-Person Mixture Deconvolved",
        color: "#22C55E",
        label: "Crime Labs",
    },
    {
        id: "dvi",
        icon: Heart,
        title: "Disaster Victim Identification (DVI)",
        subtitle: "Mass Casualty Pedigree Rematch & Rapid Kinship Indexing",
        description:
            "In mass disaster events, FORENZA provides rapid kinship indexing and pedigree tree matching to identify remains against family reference samples. Supports multi-sample batch processing and Interpol DVI standard export.",
        bulletPoints: [
            "Concurrent multi-sample batch processing with worker semaphores",
            "Parent-child, full-sibling & half-sibling KI within seconds",
            "Sample degradation (d_k) and stochastic dropout (p_d) scoring",
            "Interpol DVI compatible 8-section certificate export",
        ],
        sampleMetric: "99.9999% Match Probability",
        sampleCode: "DVI_BATCH_402 — Interpol Section 4 Standard",
        color: "#06B6D4",
        label: "DVI Operations",
    },
    {
        id: "border-security",
        icon: Shield,
        title: "Court Testimony & Expert Witness Defense",
        subtitle: "7-Point Judicial Testimony Framework & Prosecutor Fallacy Shield",
        description:
            "Enables forensic experts and defense analysts to toggle between Research Mode and Court Mode. Generates a 7-point judicial testimony brief with explicit Transposed Conditional Fallacy protection.",
        bulletPoints: [
            "7-Point Judicial Testimony Framework brief exporter",
            "Prosecutor's Fallacy Prevention Shield guarding against P(H_p|E) transposition",
            "HMAC-SHA256 testimony hash ensuring court admissibility",
            "Dual-analyst sign-off governance & override rationale audit trail",
        ],
        sampleMetric: "Zero-Knowledge Admissibility",
        sampleCode: "COURT_TESTIMONY_882 — HMAC SHA-256 Certified",
        color: "#8B5CF6",
        label: "Court Mode",
    },
    {
        id: "research",
        icon: FlaskConical,
        title: "Academic & Clinical Genetics Research",
        subtitle: "Population Stratification & GTEx eQTL Integration",
        description:
            "Research institutions can leverage FORENZA as a validated computational framework for population genetics studies. The platform provides reproducible LR calculations, exportable allele frequency matrices, and GTEx eQTL cross-references for 54 tissue types, supporting peer-reviewed genomics research.",
        bulletPoints: [
            "Exportable allele frequency matrices and LR results",
            "GTEx eQTL data integration for 54 tissue types",
            "Reproducible and auditable computation pipeline",
            "Population stratification analysis and theta correction",
        ],
        sampleMetric: "54 Tissue eQTL Mapped",
        sampleCode: "GENOMICS_STUDY_V2 — Balding-Nichols theta=0.03",
        color: "#22C55E",
        label: "Research Labs",
    },
];

export default function LandingSolutions() {
    const [activeIdx, setActiveIdx] = useState(0);
    const activeSolution = SOLUTIONS[activeIdx];
    const Icon = activeSolution.icon;

    return (
        <section id="solutions" className="scroll-mt-20 min-h-[85vh] lg:min-h-screen flex flex-col justify-between py-12 px-4 bg-tactical-surface/30">
            <div className="my-auto mx-auto max-w-6xl w-full">
                {/* Header */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center gap-2 rounded-full border border-[#06B6D4]/30 bg-[#06B6D4]/5 px-4 py-1.5 mb-3 shadow-[0_0_15px_rgba(6,182,212,0.1)]">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#06B6D4] animate-pulse" />
                        <span className="font-mono text-[10px] tracking-widest text-[#06B6D4] uppercase font-bold">
                            Application Domains
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-bold text-tactical-text mb-3">
                        Built for High-Stakes Environments
                    </h2>
                    <p className="max-w-xl mx-auto text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                        FORENZA addresses the specific operational demands of four distinct forensic and scientific disciplines.
                    </p>
                </div>

                {/* Interactive Solution Tabs */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
                    {SOLUTIONS.map((s, i) => {
                        const SIcon = s.icon;
                        const isActive = activeIdx === i;
                        return (
                            <button
                                key={s.id}
                                onClick={() => setActiveIdx(i)}
                                className={`flex items-center gap-3 p-3.5 rounded-xl border font-mono text-xs transition-all duration-300 text-left ${
                                    isActive
                                        ? "bg-tactical-surface-elevated text-white border-current shadow-lg"
                                        : "bg-tactical-surface/60 text-tactical-text-muted border-tactical-border/60 hover:border-tactical-border hover:text-white"
                                }`}
                                style={isActive ? { color: s.color, borderColor: s.color } : {}}
                            >
                                <SIcon className="h-4 w-4 shrink-0" style={{ color: s.color }} />
                                <span className="font-bold truncate">{s.label}</span>
                            </button>
                        );
                    })}
                </div>

                {/* Main Domain Inspector Card */}
                <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface p-5 sm:p-7 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                        {/* Left Info Column */}
                        <div className="lg:col-span-7 space-y-5">
                            <div className="flex items-center gap-3">
                                <div
                                    className="flex h-11 w-11 items-center justify-center rounded-xl border shrink-0"
                                    style={{
                                        background: `${activeSolution.color}15`,
                                        borderColor: `${activeSolution.color}35`,
                                        color: activeSolution.color,
                                    }}
                                >
                                    <Icon className="h-5 w-5" />
                                </div>
                                <div>
                                    <span
                                        className="font-mono text-[10px] tracking-widest uppercase font-bold"
                                        style={{ color: activeSolution.color }}
                                    >
                                        {activeSolution.label} Domain
                                    </span>
                                    <h3 className="text-xl sm:text-2xl font-bold text-white">
                                        {activeSolution.title}
                                    </h3>
                                </div>
                            </div>

                            <p className="text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                                {activeSolution.description}
                            </p>

                            {/* Checklist */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                                {activeSolution.bulletPoints.map((point) => (
                                    <div key={point} className="flex items-start gap-2.5">
                                        <CheckCircle2
                                            className="h-4 w-4 shrink-0 mt-0.5"
                                            style={{ color: activeSolution.color }}
                                        />
                                        <span className="text-tactical-text text-xs leading-snug">{point}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Right Interactive Mock Output Card */}
                        <div className="lg:col-span-5 rounded-xl border border-tactical-border bg-tactical-bg/90 p-5 space-y-4 shadow-xl font-mono">
                            <div className="flex items-center justify-between border-b border-tactical-border/80 pb-2.5">
                                <div className="flex items-center gap-2">
                                    <FileText className="h-4 w-4" style={{ color: activeSolution.color }} />
                                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                                        Domain Inspection
                                    </span>
                                </div>
                                <span className="text-[9px] text-[#22C55E] bg-[#22C55E]/10 border border-[#22C55E]/20 px-2 py-0.5 rounded">
                                    Active Standard
                                </span>
                            </div>

                            <div className="space-y-2.5">
                                <div>
                                    <span className="text-[9px] text-tactical-text-dim uppercase tracking-wider block">
                                        Primary Metric Output
                                    </span>
                                    <span
                                        className="text-base sm:text-lg font-bold text-white"
                                        style={{ color: activeSolution.color }}
                                    >
                                        {activeSolution.sampleMetric}
                                    </span>
                                </div>

                                <div className="p-2.5 rounded-lg border border-tactical-border/60 bg-black/60 text-[10px] text-tactical-text-muted break-all">
                                    <span className="text-tactical-text-dim block mb-0.5">Session Target Reference:</span>
                                    {activeSolution.sampleCode}
                                </div>
                            </div>

                            <div className="pt-2.5 border-t border-tactical-border/60 flex items-center justify-between text-[10px] text-tactical-text-dim">
                                <span>Verification Status</span>
                                <span className="text-[#22C55E] font-bold">Passed NRC II Audit</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Neon Scroll to Security & Specs (Desktop Only) */}
            <div className="hidden sm:flex pt-4 justify-center">
                <NeonDnaScroll targetId="security-specs" />
            </div>
        </section>
    );
}
