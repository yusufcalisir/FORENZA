"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Dna, Menu, X, Layers, Cpu, ShieldCheck, Briefcase, ChevronRight } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";

const NAV_LINKS = [
    { label: "Capabilities", href: "#features", icon: Layers },
    { label: "Bio-Engine", href: "#bio-engine", icon: Dna },
    { label: "Architecture", href: "#architecture", icon: Cpu },
    { label: "Solutions", href: "#solutions", icon: Briefcase },
    { label: "Security & Specs", href: "#security-specs", icon: ShieldCheck },
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
            const headerOffset = 70;
            const elementPosition = el.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            window.scrollTo({ top: offsetPosition, behavior: "smooth" });
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
                <div className="mx-auto max-w-7xl px-3 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between">
                        {/* Brand */}
                        <a
                            href="#"
                            onClick={(e) => {
                                e.preventDefault();
                                window.scrollTo({ top: 0, behavior: "smooth" });
                            }}
                            className="group flex items-center gap-2.5 cursor-pointer shrink-0"
                        >
                            <div className="relative flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-xl bg-tactical-surface border border-tactical-border group-hover:border-[#22C55E]/50 transition-all duration-300 overflow-hidden shadow-[0_0_15px_rgba(34,197,94,0.1)] shrink-0">
                                <div className="absolute inset-0 bg-gradient-to-br from-[#22C55E]/20 via-[#06B6D4]/10 to-transparent opacity-60 group-hover:opacity-100 transition-opacity" />
                                <Dna className="relative h-4 w-4 sm:h-5 sm:w-5 text-[#22C55E] group-hover:rotate-12 transition-transform duration-300" />
                                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-[#22C55E] shadow-[0_0_6px_#22C55E]" />
                            </div>
                            <div className="flex flex-col">
                                <span className="font-mono text-sm sm:text-base font-black tracking-[0.15em] sm:tracking-[0.18em] text-tactical-text group-hover:text-[#22C55E] transition-colors whitespace-nowrap">
                                    FOREN<span className="text-[#06B6D4]">ZA</span>
                                </span>
                                <span className="hidden sm:block font-mono text-[9px] tracking-widest text-tactical-text-muted font-medium uppercase whitespace-nowrap">
                                    Forensic Biology &amp; DNA Intelligence
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
                        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
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

                            {/* Launch Demo Button - Compact on Mobile Header */}
                            <div className="sm:hidden">
                                <LaunchDemoButton size="sm" />
                            </div>
                            <div className="hidden sm:block">
                                <LaunchDemoButton size="md" />
                            </div>

                            {/* Mobile toggle */}
                            <button
                                onClick={() => setMobileOpen((v) => !v)}
                                className="lg:hidden p-2 text-tactical-text-dim hover:text-tactical-text transition-colors rounded-lg border border-tactical-border bg-tactical-surface shrink-0"
                            >
                                {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Premium Mobile Menu Overlay */}
            {mobileOpen && (
                <div className="fixed inset-0 z-40 lg:hidden">
                    {/* Backdrop */}
                    <div
                        className="absolute inset-0 bg-black/85 backdrop-blur-xl animate-fade-in"
                        onClick={() => setMobileOpen(false)}
                    />

                    {/* Drawer Content Card */}
                    <div className="absolute top-20 left-3 right-3 bg-[#0A0A0B]/95 border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-[0_10px_40px_rgba(0,0,0,0.9)] space-y-4 max-h-[85vh] overflow-y-auto">
                        {/* Header Directory Badge */}
                        <div className="flex items-center justify-between border-b border-tactical-border/60 pb-3">
                            <span className="font-mono text-[10px] tracking-widest text-tactical-text-dim uppercase font-bold">
                                // Navigation Directory
                            </span>
                            <div className="flex items-center gap-1.5 rounded-full border border-[#22C55E]/30 bg-[#22C55E]/10 px-2.5 py-0.5">
                                <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E] animate-pulse" />
                                <span className="font-mono text-[9px] text-[#22C55E] font-semibold uppercase">Online</span>
                            </div>
                        </div>

                        {/* Navigation Items with Icons */}
                        <div className="space-y-1.5">
                            {NAV_LINKS.map((link) => {
                                const Icon = link.icon;
                                return (
                                    <a
                                        key={link.href}
                                        href={link.href}
                                        onClick={(e) => handleAnchorClick(e, link.href)}
                                        className="group flex items-center justify-between px-3.5 py-3 rounded-xl border border-tactical-border/40 bg-tactical-surface/50 hover:bg-tactical-surface-elevated hover:border-[#22C55E]/40 font-mono text-xs sm:text-sm tracking-wide text-tactical-text-muted hover:text-white transition-all duration-200"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-tactical-border/50 group-hover:bg-[#22C55E]/20 text-tactical-text-dim group-hover:text-[#22C55E] transition-colors">
                                                <Icon className="h-3.5 w-3.5" />
                                            </div>
                                            <span className="font-medium">{link.label}</span>
                                        </div>
                                        <ChevronRight className="h-4 w-4 text-tactical-text-dim group-hover:text-[#22C55E] group-hover:translate-x-0.5 transition-all" />
                                    </a>
                                );
                            })}
                        </div>

                        {/* Signature Launch Demo Button (Matches rest of site) */}
                        <div className="pt-3 border-t border-tactical-border/60 flex flex-col gap-2">
                            <LaunchDemoButton size="lg" className="w-full" />
                            <p className="text-center font-mono text-[9px] text-tactical-text-dim">
                                Instant Sandbox Access — Zero Setup Required
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
