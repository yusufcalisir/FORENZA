"use client";

import { Binary, Dna, Eye, Syringe, PackageCheck, Scale } from "lucide-react";
import NeonDnaScroll from "./NeonDnaScroll";

const FEATURES = [
    {
        icon: Binary,
        title: "Probabilistic Genotyping & Population",
        description:
            "MCMC Metropolis-Hastings 2-4 person mixture deconvolution with Dirichlet Fst subpopulation correction, Tippett calibration, and low-template touch LTDNA dropout recovery.",
        tags: ["MCMC MIXTURE", "DIRICHLET FST", "TIPPETT CALIBRATION", "LTDNA TOUCH"],
        color: "#22C55E",
        glow: "rgba(34,197,94,0.12)",
    },
    {
        icon: Dna,
        title: "Lineage Forensics & Kinship Indexing",
        description:
            "Y-STR Clopper-Pearson 95% binomial confidence intervals, X-STR linkage kinship KIX, mtDNA rCRS alignment, and Interpol DVI mass casualty pedigree trees.",
        tags: ["Y-STR HAPLOTYPE", "X-STR LINKAGE", "MTDNA RCRS", "DVI PEDIGREE"],
        color: "#06B6D4",
        glow: "rgba(6,182,212,0.12)",
    },
    {
        icon: Eye,
        title: "Phenotyping, Epigenetics & Genomics",
        description:
            "HIrisPlex-S Extended phenotype prediction for eye, hair, skin tone and freckles, Horvath 5-CpG epigenetic clock, tDMR tissue deconvolution, and 5-tier joint evidence fusion.",
        tags: ["HIRISPLEX-S", "HORVATH CLOCK", "TDMR TISSUE", "5-TIER FUSION"],
        color: "#8B5CF6",
        glow: "rgba(139,92,246,0.12)",
    },
    {
        icon: Syringe,
        title: "Biology, Serology & Pathology Engines",
        description:
            "ABO/Rh blood group serology, FUT2/FUT3 secretor status, Forensic Pathology PMI Algor mortis clock, Widmark BAC clearance, and impact angle bloodstain BPA physics.",
        tags: ["ABO/RH SEROLOGY", "FUT2 SECRETOR", "TOXICOLOGY BAC", "BPA SPATTER"],
        color: "#22C55E",
        glow: "rgba(34,197,94,0.12)",
    },
    {
        icon: PackageCheck,
        title: "LIMS Workflow, Gateway & QA/QC",
        description:
            "9-Step SOP accessioning chain, automated CE GeneMapper/qPCR/NGS parsers, 7-point QA/QC inspection matrix, and dual-analyst sign-off governance with HMAC audit trail.",
        tags: ["LIMS 9-STEP SOP", "INSTRUMENT PARSER", "7-POINT QC", "DUAL SIGN-OFF"],
        color: "#06B6D4",
        glow: "rgba(6,182,212,0.12)",
    },
    {
        icon: Scale,
        title: "ISO Certificate & Expert Witness Court Mode",
        description:
            "8-Section ISO 17025 certified report compiler, 7-Point Judicial Testimony Framework, Prosecutor's Fallacy Prevention Shield, and Master Evidence OS DAG orchestrator.",
        tags: ["ISO 17025 CERT", "COURT MODE", "PROSECUTOR SHIELD", "EVIDENCE OS DAG"],
        color: "#8B5CF6",
        glow: "rgba(139,92,246,0.12)",
    },
];

export default function LandingFeatures() {
    return (
        <section id="features" className="scroll-mt-20 min-h-[85vh] lg:min-h-screen flex flex-col justify-between py-12 px-4">
            <div className="my-auto mx-auto max-w-7xl w-full">
                {/* Section header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 rounded-full border border-[#22C55E]/30 bg-[#22C55E]/5 px-4 py-1.5 mb-3 shadow-[0_0_15px_rgba(34,197,94,0.1)]">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E] animate-pulse" />
                        <span className="font-mono text-[10px] tracking-widest text-[#22C55E] uppercase font-bold">
                            30 Subsystems • 6 Core Pillars
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-bold text-tactical-text mb-3">
                        Six Core Analytical Pillars
                    </h2>
                    <p className="max-w-xl mx-auto text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                        From raw STR profile ingestion to cryptographically anchored forensic reports, each module
                        is engineered for precision at the intersection of genetics and intelligence.
                    </p>
                </div>

                {/* Feature Grid with Fixed Bottom Tag Divider Baseline */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                    {FEATURES.map((feature) => {
                        const Icon = feature.icon;
                        return (
                            <div
                                key={feature.title}
                                className="group flex flex-col justify-between h-full rounded-2xl border border-tactical-border bg-tactical-surface p-6 hover:border-tactical-border/80 transition-all duration-300 hover:-translate-y-1 shadow-lg"
                                onMouseEnter={(e) => {
                                    (e.currentTarget as HTMLDivElement).style.boxShadow = `0 0 40px ${feature.glow}`;
                                }}
                                onMouseLeave={(e) => {
                                    (e.currentTarget as HTMLDivElement).style.boxShadow = "none";
                                }}
                            >
                                {/* Top Content Area */}
                                <div className="flex-1">
                                    {/* Icon */}
                                    <div
                                        className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl border transition-transform duration-300 group-hover:scale-110"
                                        style={{
                                            background: `${feature.color}15`,
                                            borderColor: `${feature.color}35`,
                                            color: feature.color,
                                            boxShadow: `0 0 20px ${feature.color}20`,
                                        }}
                                    >
                                        <Icon className="h-5 w-5" />
                                    </div>

                                    {/* Title */}
                                    <h3 className="font-bold text-tactical-text text-base mb-2 leading-snug">
                                        {feature.title}
                                    </h3>

                                    {/* Description */}
                                    <p className="text-tactical-text-muted text-xs leading-relaxed mb-5">
                                        {feature.description}
                                    </p>
                                </div>

                                {/* Bottom Tag Chips Area */}
                                <div className="mt-auto pt-4 border-t border-tactical-border/50 min-h-[72px] flex flex-wrap content-start gap-2">
                                    {feature.tags.map((tag) => (
                                        <span
                                            key={tag}
                                            className="rounded-lg border px-2 py-0.5 font-mono text-[9px] font-bold tracking-widest uppercase transition-all"
                                            style={{
                                                borderColor: `${feature.color}35`,
                                                color: feature.color,
                                                background: `${feature.color}0D`,
                                            }}
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Neon Scroll to Architecture (Desktop Only) */}
            <div className="hidden sm:flex pt-4 justify-center">
                <NeonDnaScroll targetId="architecture" />
            </div>
        </section>
    );
}
