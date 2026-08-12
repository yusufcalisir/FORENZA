"use client";

import { useState } from "react";
import Link from "next/link";
import { Shield, Activity, Cpu, Layers, Menu, X, Zap } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";
import SaaSLanguageToggle from "./SaaSLanguageToggle";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function LandingHeader() {
    const { t } = useSaasLanguage();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    const scrollToSection = (id: string, e: React.MouseEvent) => {
        e.preventDefault();
        setIsMobileMenuOpen(false);
        const cleanId = id.replace("#", "");
        const el = document.getElementById(cleanId) || (cleanId.includes("bio") ? document.getElementById("bio-simulator") : null);
        if (el) {
            const headerOffset = 70;
            const elementPosition = el.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        }
    };

    return (
        <header className="sticky top-0 z-50 border-b border-tactical-border/60 bg-black/90 backdrop-blur-xl transition-all w-full max-w-full overflow-x-clip">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-3 py-2.5 sm:px-6 lg:px-8 gap-2">
                {/* Brand Logo */}
                <Link href="/" className="flex items-center gap-1.5 sm:gap-2.5 group shrink-0 min-w-0">
                    <ForenzaLogoIcon size={30} className="sm:w-[34px] sm:h-[34px] group-hover:scale-105 transition-all duration-300 shadow-lg shadow-emerald-500/10 shrink-0" />
                    <div className="flex items-center gap-1.5 min-w-0">
                        <span className="font-mono text-sm sm:text-base font-extrabold tracking-wider text-white">
                            FORENZA
                        </span>
                        <span className="hidden lg:inline-flex rounded-full bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 text-[9px] font-mono font-bold text-emerald-400 whitespace-nowrap">
                            EVIDENCE OS
                        </span>
                    </div>
                </Link>

                {/* Navigation Links (Desktop) */}
                <nav className="hidden md:flex items-center gap-4 lg:gap-7 font-mono text-xs text-zinc-400">
                    <button 
                        type="button"
                        onClick={(e) => scrollToSection("bio-simulator", e)} 
                        className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium cursor-pointer bg-transparent border-0 p-0 whitespace-nowrap"
                    >
                        <Activity className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                        <span>{t.header.bioSimulator}</span>
                    </button>
                    <button 
                        type="button"
                        onClick={(e) => scrollToSection("subsystems", e)} 
                        className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium cursor-pointer bg-transparent border-0 p-0 whitespace-nowrap"
                    >
                        <Layers className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                        <span>{t.header.subsystems}</span>
                    </button>
                    <button 
                        type="button"
                        onClick={(e) => scrollToSection("architecture", e)} 
                        className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium cursor-pointer bg-transparent border-0 p-0 whitespace-nowrap"
                    >
                        <Cpu className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{t.header.architecture}</span>
                    </button>
                    <button 
                        type="button"
                        onClick={(e) => scrollToSection("security", e)} 
                        className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium cursor-pointer bg-transparent border-0 p-0 whitespace-nowrap"
                    >
                        <Shield className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                        <span>{t.header.security}</span>
                    </button>
                </nav>

                {/* Right Actions */}
                <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
                    <SaaSLanguageToggle />
                    
                    {/* Compact Mobile Demo Button (⚡ on mobile, full on desktop) */}
                    <LaunchDemoButton size="sm" label={t.header.launchDemo} compactMobile={true} />

                    {/* Mobile Hamburger Menu Toggle Button */}
                    <button
                        type="button"
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        aria-label="Toggle mobile menu"
                        className="md:hidden flex items-center justify-center p-2 rounded-xl border border-tactical-border bg-tactical-surface text-zinc-300 hover:text-white hover:border-emerald-500/40 transition-all cursor-pointer"
                    >
                        {isMobileMenuOpen ? (
                            <X className="h-4 w-4 text-emerald-400" />
                        ) : (
                            <Menu className="h-4 w-4 text-zinc-300" />
                        )}
                    </button>
                </div>
            </div>

            {/* Mobile Hamburger Drawer Menu */}
            {isMobileMenuOpen && (
                <div className="md:hidden border-t border-tactical-border/80 bg-black/95 backdrop-blur-2xl px-4 py-5 space-y-4 font-mono shadow-2xl animate-in slide-in-from-top-2 duration-200">
                    <nav className="flex flex-col space-y-2">
                        <button
                            type="button"
                            onClick={(e) => scrollToSection("bio-simulator", e)}
                            className="flex items-center justify-between p-3 rounded-xl border border-tactical-border/60 bg-tactical-surface/60 text-xs font-bold text-zinc-200 hover:text-emerald-400 hover:border-emerald-500/40 transition-all text-left"
                        >
                            <div className="flex items-center gap-2.5">
                                <Activity className="w-4 h-4 text-cyan-400" />
                                <span>{t.header.bioSimulator}</span>
                            </div>
                            <span className="text-[10px] text-zinc-500">#bio-simulator</span>
                        </button>

                        <button
                            type="button"
                            onClick={(e) => scrollToSection("subsystems", e)}
                            className="flex items-center justify-between p-3 rounded-xl border border-tactical-border/60 bg-tactical-surface/60 text-xs font-bold text-zinc-200 hover:text-emerald-400 hover:border-emerald-500/40 transition-all text-left"
                        >
                            <div className="flex items-center gap-2.5">
                                <Layers className="w-4 h-4 text-purple-400" />
                                <span>{t.header.subsystems}</span>
                            </div>
                            <span className="text-[10px] text-zinc-500">#subsystems</span>
                        </button>

                        <button
                            type="button"
                            onClick={(e) => scrollToSection("architecture", e)}
                            className="flex items-center justify-between p-3 rounded-xl border border-tactical-border/60 bg-tactical-surface/60 text-xs font-bold text-zinc-200 hover:text-emerald-400 hover:border-emerald-500/40 transition-all text-left"
                        >
                            <div className="flex items-center gap-2.5">
                                <Cpu className="w-4 h-4 text-emerald-400" />
                                <span>{t.header.architecture}</span>
                            </div>
                            <span className="text-[10px] text-zinc-500">#architecture</span>
                        </button>

                        <button
                            type="button"
                            onClick={(e) => scrollToSection("security", e)}
                            className="flex items-center justify-between p-3 rounded-xl border border-tactical-border/60 bg-tactical-surface/60 text-xs font-bold text-zinc-200 hover:text-emerald-400 hover:border-emerald-500/40 transition-all text-left"
                        >
                            <div className="flex items-center gap-2.5">
                                <Shield className="w-4 h-4 text-amber-400" />
                                <span>{t.header.security}</span>
                            </div>
                            <span className="text-[10px] text-zinc-500">#security</span>
                        </button>
                    </nav>

                    <div className="pt-2 border-t border-tactical-border/60 flex flex-col gap-3">
                        <LaunchDemoButton size="md" label={t.header.launchDemo} className="w-full py-3 text-xs" />
                    </div>
                </div>
            )}
        </header>
    );
}
