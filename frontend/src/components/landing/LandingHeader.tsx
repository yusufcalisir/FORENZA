"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Dna, Menu, X } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";

const NAV_LINKS = [
    { label: "Capabilities", href: "#features" },
    { label: "Bio-Engine", href: "#bio-engine" },
    { label: "Architecture", href: "#architecture" },
    { label: "Solutions", href: "#solutions" },
    { label: "Security & Specs", href: "#security-specs" },
];

export default function LandingHeader() {
    const [scrolled, setScrolled] = useState(false);
    const [mobileOpen, setMobileOpen] = useState(false);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener("scroll", onScroll, { passive: true });
        return () => window.removeEventListener("scroll", onScroll);
    }, []);

    const handleAnchorClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
        e.preventDefault();
        setMobileOpen(false);
        const id = href.replace("#", "");
        const el = document.getElementById(id);
        if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    return (
        <>
            <header
                className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
                    scrolled
                        ? "bg-[#0A0A0B]/90 backdrop-blur-2xl border-b border-tactical-border/80 shadow-[0_8px_32px_rgba(0,0,0,0.8)] py-3"
                        : "bg-transparent py-4"
                }`}
            >
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between">
                        {/* Brand */}
                        <a
                            href="#"
                            onClick={(e) => {
                                e.preventDefault();
                                window.scrollTo({ top: 0, behavior: "smooth" });
                            }}
                            className="group flex items-center gap-3 cursor-pointer"
                        >
                            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-tactical-surface border border-tactical-border group-hover:border-[#22C55E]/50 transition-all duration-300 overflow-hidden shadow-[0_0_15px_rgba(34,197,94,0.1)]">
                                <div className="absolute inset-0 bg-gradient-to-br from-[#22C55E]/20 via-[#06B6D4]/10 to-transparent opacity-60 group-hover:opacity-100 transition-opacity" />
                                <Dna className="relative h-5 w-5 text-[#22C55E] group-hover:rotate-12 transition-transform duration-300" />
                                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-[#22C55E] shadow-[0_0_6px_#22C55E]" />
                            </div>
                            <div className="flex flex-col">
                                <span className="font-mono text-base font-black tracking-[0.18em] text-tactical-text group-hover:text-[#22C55E] transition-colors">
                                    VANTAGE<span className="text-[#06B6D4]">-STR</span>
                                </span>
                                <span className="font-mono text-[9px] tracking-widest text-tactical-text-muted font-medium uppercase">
                                    Forensic Intelligence Core
                                </span>
                            </div>
                        </a>

                        {/* Desktop Nav */}
                        <nav className="hidden lg:flex items-center gap-1 rounded-full border border-tactical-border/60 bg-tactical-surface/60 backdrop-blur-md px-4 py-1.5 shadow-[0_4px_20px_rgba(0,0,0,0.4)]">
                            {NAV_LINKS.map((link) => (
                                <a
                                    key={link.href}
                                    href={link.href}
                                    onClick={(e) => handleAnchorClick(e, link.href)}
                                    className="px-3.5 py-1.5 rounded-full font-mono text-[11px] font-medium tracking-wide text-tactical-text-muted hover:text-white hover:bg-tactical-border/50 transition-all duration-200"
                                >
                                    {link.label}
                                </a>
                            ))}
                        </nav>

                        {/* Right Actions */}
                        <div className="flex items-center gap-3">
                            {/* System Status badge */}
                            <div className="hidden sm:flex items-center gap-2 rounded-full border border-[#22C55E]/30 bg-[#22C55E]/5 px-3 py-1.5 shadow-[0_0_12px_rgba(34,197,94,0.1)]">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#22C55E] opacity-75" />
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-[#22C55E]" />
                                </span>
                                <span className="font-mono text-[10px] tracking-widest text-[#22C55E] font-bold uppercase">
                                    System Online
                                </span>
                            </div>

                            {/* Reusable Launch Demo Button */}
                            <LaunchDemoButton size="md" />

                            {/* Mobile toggle */}
                            <button
                                onClick={() => setMobileOpen((v) => !v)}
                                className="lg:hidden p-2 text-tactical-text-dim hover:text-tactical-text transition-colors rounded-lg border border-tactical-border bg-tactical-surface"
                            >
                                {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Mobile Menu Overlay */}
            {mobileOpen && (
                <div className="fixed inset-0 z-40 lg:hidden">
                    <div
                        className="absolute inset-0 bg-black/80 backdrop-blur-md"
                        onClick={() => setMobileOpen(false)}
                    />
                    <div className="absolute top-20 left-4 right-4 bg-tactical-surface border border-tactical-border rounded-2xl p-5 shadow-2xl space-y-1.5">
                        {NAV_LINKS.map((link) => (
                            <a
                                key={link.href}
                                href={link.href}
                                onClick={(e) => handleAnchorClick(e, link.href)}
                                className="flex items-center px-4 py-3 rounded-xl border border-transparent hover:border-tactical-border hover:bg-tactical-surface-elevated font-mono text-sm tracking-wide text-tactical-text-muted hover:text-white transition-all"
                            >
                                {link.label}
                            </a>
                        ))}
                        <div className="pt-3 border-t border-tactical-border">
                            <a
                                href="/nodes"
                                className="flex items-center justify-center w-full rounded-xl bg-gradient-to-r from-[#22C55E] to-[#06B6D4] px-5 py-3.5 font-mono text-sm font-bold tracking-wide text-black hover:opacity-90 transition-opacity"
                            >
                                Launch Demo
                            </a>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
