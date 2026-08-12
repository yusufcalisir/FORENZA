"use client";

import Link from "next/link";
import LaunchDemoButton from "./LaunchDemoButton";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

const TECH_BADGES = [
    { label: "Next.js 16 Turbopack", color: "#06B6D4" },
    { label: "215/215 Pytest Suite", color: "#8B5CF6" },
    { label: "Circom zkSNARK", color: "#22C55E" },
    { label: "Polygon Ledger", color: "#06B6D4" },
];

export default function LandingFooter() {
    const { t } = useSaasLanguage();

    const footerLinks = [
        {
            heading: t.footer.columns.col1Title,
            links: t.footer.columns.col1Links.map((label, i) => ({ label, href: ["#subsystems", "#architecture", "#bio-simulator", "#subsystems"][i] })),
        },
        {
            heading: t.footer.columns.col2Title,
            links: t.footer.columns.col2Links.map((label, i) => ({ label, href: ["#subsystems", "#subsystems", "#subsystems", "#subsystems"][i] })),
        },
        {
            heading: t.footer.columns.col3Title,
            links: t.footer.columns.col3Links.map((label, i) => ({ label, href: ["#security", "#security", "#security", "#security"][i] })),
        },
    ];

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

            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 relative z-10">
                <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 pb-8 border-b border-tactical-border/60">
                    
                    {/* Brand Info */}
                    <div className="lg:col-span-2 space-y-4">
                        <div className="flex items-center gap-3">
                            <ForenzaLogoIcon size={38} className="shadow-lg shadow-emerald-500/10" />
                            <div>
                                <span className="font-mono text-xl font-extrabold tracking-wider text-white">
                                    FORENZA
                                </span>
                                <p className="font-mono text-[9px] tracking-widest text-cyan-400">
                                    FORENSIC EVIDENCE OPERATING SYSTEM
                                </p>
                            </div>
                        </div>
                        <p className="text-zinc-400 text-xs leading-relaxed max-w-sm">
                            {t.footer.tagline}
                        </p>

                        <div className="flex items-center gap-2 pt-1">
                            <div className="flex items-center gap-1.5 rounded-full border border-emerald-500/25 bg-emerald-500/5 px-3 py-1">
                                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                <span className="text-[10px] font-bold text-emerald-400 uppercase">
                                    {t.footer.status}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Footer Nav Links */}
                    <div className="lg:col-span-3 grid grid-cols-2 sm:grid-cols-3 gap-8">
                        {footerLinks.map((col, idx) => (
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
                        &copy; 2026 {t.footer.rights}
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
