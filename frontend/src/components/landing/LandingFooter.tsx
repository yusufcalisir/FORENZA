"use client";

import Link from "next/link";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

const TECH_BADGES = [
    { label: "ISO/IEC 17025" },
    { label: "1,147 Doğrulanmış Test" },
    { label: "zk-SNARK Gizlilik" },
    { label: "Merkle Delil Zinciri" },
];

export default function LandingFooter() {
    const { t } = useSaasLanguage();

    const footerColumns = [
        {
            heading: t.footer.columns.col1Title,
            links: t.footer.columns.col1Links.map((label, i) => ({ 
                label, 
                href: ["#subsystems", "#architecture", "#bio-simulator", "#subsystems"][i] || "#subsystems" 
            })),
        },
        {
            heading: t.footer.columns.col2Title,
            links: t.footer.columns.col2Links.map((label, i) => ({ 
                label, 
                href: ["#subsystems", "#subsystems", "#subsystems", "#subsystems"][i] || "#subsystems" 
            })),
        },
        {
            heading: t.footer.columns.col3Title,
            links: t.footer.columns.col3Links.map((label, i) => ({ 
                label, 
                href: ["#security", "#security", "#security", "#security"][i] || "#security" 
            })),
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
        <footer id="footer" className="border-t border-tactical-border/60 bg-[#07090E] relative overflow-hidden w-full max-w-full font-sans">
            {/* Subtle Ambient Glow */}
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[500px] h-[150px] bg-emerald-500/5 blur-[120px] rounded-full pointer-events-none" />

            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 sm:py-14 relative z-10 space-y-8">
                
                {/* Main Grid: Brand + 3 Link Columns */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-8 sm:gap-10">
                    
                    {/* Brand Info (2 cols on lg) */}
                    <div className="sm:col-span-2 space-y-3.5">
                        <div className="flex items-center gap-2.5">
                            <ForenzaLogoIcon size={32} className="shrink-0" />
                            <div className="flex items-center gap-2">
                                <span className="font-mono text-lg font-extrabold tracking-wider text-white">
                                    FORENZA
                                </span>
                                <span className="rounded-full bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 text-[8px] font-mono font-bold text-emerald-400">
                                    EVIDENCE OS
                                </span>
                            </div>
                        </div>

                        <p className="text-xs text-zinc-400 leading-relaxed max-w-sm">
                            {t.footer.tagline}
                        </p>

                        <div className="pt-1">
                            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-[10px] font-mono font-bold text-emerald-300">
                                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                <span>{t.footer.status}</span>
                            </div>
                        </div>
                    </div>

                    {/* 3 Nav Columns */}
                    {footerColumns.map((col, idx) => (
                        <div key={idx} className="space-y-3">
                            <h4 className="text-xs font-mono font-bold text-zinc-200 uppercase tracking-wider">
                                {col.heading}
                            </h4>
                            <ul className="space-y-2 text-xs">
                                {col.links.map((link, lIdx) => (
                                    <li key={lIdx}>
                                        <button
                                            type="button"
                                            onClick={(e) => scrollToSection(link.href, e)}
                                            className="text-zinc-400 hover:text-white transition-colors text-left bg-transparent border-0 p-0 cursor-pointer block leading-normal"
                                        >
                                            {link.label}
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                {/* Clean Muted Disclaimer (No Yellow Boxes or Oval Badges) */}
                <div className="pt-6 border-t border-tactical-border/40 text-[11px] text-zinc-500 leading-relaxed space-y-1">
                    <p>{t.footer.disclaimer.text}</p>
                    <p className="text-[10px] text-zinc-600 italic">* {t.footer.disclaimer.isoNote}</p>
                </div>

                {/* Bottom Bar: Copyright & Tech Badges */}
                <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-zinc-500">
                    <p>&copy; 2026 FORENZA Evidence OS. {t.footer.rights}</p>
                    
                    <div className="flex flex-wrap items-center justify-center gap-1.5">
                        {TECH_BADGES.map((b, bIdx) => (
                            <span 
                                key={bIdx} 
                                className="px-2.5 py-0.5 rounded-md bg-white/[0.03] border border-white/8 text-[10px] font-mono font-medium text-zinc-400"
                            >
                                {b.label}
                            </span>
                        ))}
                    </div>
                </div>

            </div>
        </footer>
    );
}
