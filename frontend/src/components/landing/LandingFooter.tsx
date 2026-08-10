"use client";

import Link from "next/link";
import { Dna } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";

const FOOTER_LINKS = [
    {
        heading: "Platform",
        links: [
            { label: "Capabilities", href: "#features" },
            { label: "Bio-Engine", href: "#bio-engine" },
            { label: "Architecture", href: "#architecture" },
        ],
    },
    {
        heading: "Use Cases",
        links: [
            { label: "Law Enforcement", href: "#solutions" },
            { label: "DVI Operations", href: "#solutions" },
            { label: "Research Labs", href: "#solutions" },
        ],
    },
    {
        heading: "Technical",
        links: [
            { label: "Security", href: "#security-specs" },
            { label: "Specifications", href: "#security-specs" },
            { label: "FAQ", href: "#faq" },
        ],
    },
];

const TECH_BADGES = [
    { label: "Next.js 14", color: "#22C55E" },
    { label: "FastAPI", color: "#06B6D4" },
    { label: "PyTorch", color: "#8B5CF6" },
    { label: "Circom ZKP", color: "#22C55E" },
    { label: "Polygon", color: "#06B6D4" },
    { label: "Solidity", color: "#8B5CF6" },
];

export default function LandingFooter() {
    const handleAnchorClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
        if (!href.startsWith("#")) return;
        e.preventDefault();
        const id = href.replace("#", "");
        document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    };

    return (
        <footer id="footer" className="border-t border-tactical-border bg-tactical-surface/50">
            {/* CTA Banner */}
            <div className="border-b border-tactical-border">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 flex flex-col sm:flex-row items-center justify-between gap-6">
                    <div>
                        <h2 className="text-xl sm:text-2xl font-bold text-tactical-text mb-1">
                            Ready to enter the platform?
                        </h2>
                        <p className="text-tactical-text-muted text-xs sm:text-sm">
                            Access the live dashboard and begin forensic analysis immediately.
                        </p>
                    </div>
                    <LaunchDemoButton size="lg" />
                </div>
            </div>

            {/* Main Footer Content */}
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
                <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                    {/* Brand column */}
                    <div className="lg:col-span-2 space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-[#22C55E]/20 to-[#06B6D4]/10 border border-[#22C55E]/30">
                                <Dna className="h-5 w-5 text-[#22C55E]" />
                            </div>
                            <div>
                                <p className="font-mono text-sm font-bold tracking-widest text-tactical-text">
                                    VANTAGE-STR
                                </p>
                                <p className="font-mono text-[9px] tracking-widest text-[#06B6D4]">
                                    FORENSIC DNA INTELLIGENCE PLATFORM
                                </p>
                            </div>
                        </div>
                        <p className="text-tactical-text-muted text-xs leading-relaxed max-w-xs">
                            A tactical forensic intelligence system for high-stakes DNA profiling, kinship analytics, and biometric reconstruction with cryptographic auditability.
                        </p>
                        {/* Live Status */}
                        <div className="flex items-center gap-2.5">
                            <div className="flex items-center gap-1.5 rounded-full border border-[#22C55E]/25 bg-[#22C55E]/5 px-3 py-1">
                                <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E] animate-pulse" />
                                <span className="font-mono text-[9px] tracking-widest text-[#22C55E] uppercase font-semibold">
                                    All Systems Online
                                </span>
                            </div>
                        </div>
                        {/* Tech Badges */}
                        <div className="flex flex-wrap gap-1.5">
                            {TECH_BADGES.map((b) => (
                                <span
                                    key={b.label}
                                    className="rounded-md border px-2 py-0.5 font-mono text-[9px] tracking-wider"
                                    style={{
                                        borderColor: `${b.color}30`,
                                        color: b.color,
                                        background: `${b.color}08`,
                                    }}
                                >
                                    {b.label}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Link columns */}
                    <div className="grid grid-cols-3 lg:col-span-3 gap-4">
                        {FOOTER_LINKS.map((col) => (
                            <div key={col.heading} className="space-y-3">
                                <h3 className="font-mono text-[10px] tracking-widest text-tactical-text-dim uppercase font-bold">
                                    {col.heading}
                                </h3>
                                <ul className="space-y-2">
                                    {col.links.map((link) => (
                                        <li key={link.label}>
                                            <a
                                                href={link.href}
                                                onClick={(e) => handleAnchorClick(e, link.href)}
                                                className="font-mono text-xs text-tactical-text-muted hover:text-tactical-text transition-colors"
                                            >
                                                {link.label}
                                            </a>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Bottom bar */}
                <div className="mt-10 pt-5 border-t border-tactical-border flex flex-col sm:flex-row items-center justify-between gap-3">
                    <p className="font-mono text-[10px] tracking-wider text-tactical-text-dim">
                        VANTAGE-STR v2.0.0 — MIT License — Open Source
                    </p>
                    <p className="font-mono text-[10px] tracking-wider text-tactical-text-dim">
                        Built for forensic precision. Use responsibly within applicable legal jurisdiction.
                    </p>
                </div>
            </div>
        </footer>
    );
}
