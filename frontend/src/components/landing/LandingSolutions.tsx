"use client";

import { useState } from "react";
import { Search, Heart, Shield, FlaskConical, CheckCircle2, FileText } from "lucide-react";

const SOLUTIONS = [
    {
        id: "law-enforcement",
        icon: Search,
        title: "Law Enforcement and Cold Cases",
        subtitle: "Familial Searching & Degraded Sample LR Matching",
        description:
            "Forensic units can upload partial or degraded STR profiles recovered from crime scenes and receive rapid likelihood ratio assessments against reference samples. The kinship engine identifies probable family relations when a direct match is unavailable, enabling familial searching workflows for unresolved cold cases.",
        bulletPoints: [
            "Partial profile LR calculation with missing loci handling",
            "Familial search across multi-generational pedigrees",
            "Geo-ancestry heatmap targeting for investigative geography",
            "Immutable blockchain report for court admissibility",
        ],
        sampleMetric: "1.42e8 Likelihood Ratio",
        sampleCode: "CASE_2026_COLD_09 — CODIS 20 Loci Matched",
        color: "#22C55E",
        label: "Law Enforcement",
    },
    {
        id: "dvi",
        icon: Heart,
        title: "Disaster Victim Identification (DVI)",
        subtitle: "Mass Casualty Rematch & Rapid Kinship Indexing",
        description:
            "In mass casualty events, FORENZA provides rapid kinship indexing to match unidentified remains against family reference samples. The platform supports concurrent multi-sample processing with quality scoring, allowing identification teams to prioritize high-confidence matches under operational pressure.",
        bulletPoints: [
            "Concurrent multi-sample batch processing",
            "Parent-child and sibling KI within minutes",
            "Sample quality and degradation scoring",
            "Interpol DVI compatible report export",
        ],
        sampleMetric: "99.999% Match Probability",
        sampleCode: "DVI_BATCH_402 — Interpol Section 4 Standard",
        color: "#06B6D4",
        label: "DVI Operations",
    },
    {
        id: "border-security",
        icon: Shield,
        title: "Border Security & Kinship Verification",
        subtitle: "NRC II Framework & Zero-Knowledge Identity Check",
        description:
            "Verify declared kinship relationships at processing centers with statistical rigor. Likelihood ratios computed under the NRC II framework provide objective evidence that is resistant to interpretation bias. ZK verification allows identity confirmation without centralizing sensitive genetic data.",
        bulletPoints: [
            "NRC II LR computation for claimed relationships",
            "ZK verification without central data exposure",
            "Geo-ancestry cross-reference for documentation verification",
            "Real-time processing with node-distributed computation",
        ],
        sampleMetric: "Zero Data Exposure (ZKP)",
        sampleCode: "BORDER_CHECK_882 — Groth16 Verified",
        color: "#8B5CF6",
        label: "Border Security",
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
        </section>
    );
}
