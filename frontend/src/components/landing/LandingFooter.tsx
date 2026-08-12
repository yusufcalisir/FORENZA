"use client";

import Link from "next/link";
import LaunchDemoButton from "./LaunchDemoButton";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";

const FOOTER_LINKS = [
    {
        heading: "Platform Subsystems",
        links: [
            { label: "30 Subsystems Matrix", href: "#subsystems" },
            { label: "Evidence OS DAG", href: "#architecture" },
            { label: "Multi-Omic Bio-Simulator", href: "#bio-simulator" },
            { label: "ISO 17025 Court Mode", href: "#subsystems" },
        ],
    },
    {
        heading: "Core Capabilities",
        links: [
            { label: "MCMC Probabilistic Genotyping", href: "#subsystems" },
            { label: "HIrisPlex-S Phenotyping", href: "#subsystems" },
            { label: "Horvath Epigenetic Clock", href: "#subsystems" },
            { label: "LIMS & Instrument Gateway", href: "#subsystems" },
        ],
    },
    {
        heading: "Admissibility & Standards",
        links: [
            { label: "ISO/IEC 17025:2017", href: "#security" },
            { label: "SWGDAM & ENFSI Rules", href: "#security" },
            { label: "Circom ZKP Privacy Auditor", href: "#security" },
            { label: "HMAC Chain of Custody", href: "#security" },
        ],
    },
];

const TECH_BADGES = [
    { label: "Next.js 16 Turbopack", color: "#06B6D4" },
    { label: "215/215 Pytest Suite", color: "#8B5CF6" },
    { label: "Circom zkSNARK", color: "#22C55E" },
    { label: "Polygon Ledger", color: "#06B6D4" },
];

export default function LandingFooter() {
    const scrollToSection = (targetId: string, e: React.MouseEvent) => {
        e.preventDefault();
        const cleanId = targetId.replace("#", "");
        const el = document.getElementById(cleanId);
        if (el) {
            const headerOffset = 70;
            const elementPosition = el.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        }
    };

    return (
        <footer id="footer" className="border-t border-tactical-border/60 bg-black font-mono relative overflow-hidden">
            {/* Ambient Background Glow */}
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[200px] bg-emerald-500/5 blur-[120px] rounded-full pointer-events-none" />

            {/* CTA Banner */}
            <div className="border-b border-tactical-border/60 bg-black/40">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 sm:py-10 flex flex-col sm:flex-row items-center justify-between gap-5 text-center sm:text-left">
                    <div>
                        <h2 className="text-xl sm:text-2xl font-extrabold text-white mb-1">
                            Ready to Launch FORENZA Evidence OS?
                        </h2>
                        <p className="text-zinc-400 text-xs sm:text-sm">
                            Access all 30 biocomputational forensic subsystems in the live SaaS dashboard.
                        </p>
                    </div>
                    <div>
                        <LaunchDemoButton size="lg" label="Launch Demo OS" />
                    </div>
                </div>
            </div>

            {/* Main Footer Content */}
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 sm:py-12">
                <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-12">
                    {/* Brand Column */}
                    <div className="lg:col-span-2 space-y-4">
                        <div className="flex items-center gap-3">
                            <ForenzaLogoIcon size={36} />
                            <div>
                                <p className="font-mono text-sm font-bold tracking-widest text-tactical-text">
                                    FORENZA
                                </p>
                                <p className="font-mono text-[9px] tracking-widest text-cyan-400">
                                    FORENSIC EVIDENCE OPERATING SYSTEM
                                </p>
                            </div>
                        </div>
                        <p className="text-zinc-400 text-xs leading-relaxed max-w-sm">
                            Enterprise multi-omic biocomputational intelligence platform unifying DNA profiling, kinship, phenotyping, epigenetics, pathology, LIMS, QA/QC, and court admissibility.
                        </p>

                        <div className="flex items-center gap-2 pt-1">
                            <div className="flex items-center gap-1.5 rounded-full border border-emerald-500/25 bg-emerald-500/5 px-3 py-1">
                                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                <span className="text-[10px] font-bold text-emerald-400 uppercase">
                                    30 Subsystems Active (v3.0.0-PROD)
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Footer Nav Links */}
                    <div className="lg:col-span-3 grid grid-cols-2 sm:grid-cols-3 gap-8">
                        {FOOTER_LINKS.map((col, idx) => (
                            <div key={idx} className="space-y-3">
                                <h3 className="text-xs font-bold text-zinc-200 uppercase tracking-wider">
                                    {col.heading}
                                </h3>
                                <ul className="space-y-2 text-xs">
                                    {col.links.map((link, lIdx) => (
                                        <li key={lIdx}>
                                            <button
                                                type="button"
                                                onClick={(e) => scrollToSection(link.href, e)}
                                                className="text-zinc-400 hover:text-emerald-400 transition-colors text-left bg-transparent border-0 p-0 cursor-pointer"
                                            >
                                                {link.label}
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Tech Stack Badges */}
                <div className="mt-8 pt-8 border-t border-tactical-border/60 flex flex-wrap items-center justify-between gap-4">
                    <p className="text-[10px] text-zinc-500">
                        &copy; 2026 FORENZA Forensic Systems. All Rights Reserved. ISO/IEC 17025:2017 Admissible.
                    </p>
                    <div className="flex flex-wrap gap-2">
                        {TECH_BADGES.map((b, bIdx) => (
                            <span key={bIdx} className="px-2 py-0.5 rounded bg-black/60 border border-tactical-border/60 text-[9px] font-bold text-zinc-300">
                                {b.label}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </footer>
    );
}
