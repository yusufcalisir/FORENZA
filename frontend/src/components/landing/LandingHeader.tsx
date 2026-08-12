"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Activity, Cpu, Layers, Menu, X, Sparkles, ArrowRight } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";
import SaaSLanguageToggle from "./SaaSLanguageToggle";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function LandingHeader() {
    const { t } = useSaasLanguage();
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    // Prevent body scrolling when full-screen mobile menu is open
    useEffect(() => {
        if (isMobileMenuOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }
        return () => {
            document.body.style.overflow = "";
        };
    }, [isMobileMenuOpen]);

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
        <>
            <header className="sticky top-0 z-40 border-b border-tactical-border/60 bg-black/90 backdrop-blur-xl transition-all w-full max-w-full overflow-x-clip">
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
                            onClick={() => setIsMobileMenuOpen(true)}
                            aria-label="Open mobile menu"
                            className="md:hidden flex items-center justify-center p-2 rounded-xl border border-tactical-border bg-tactical-surface text-zinc-300 hover:text-white hover:border-emerald-500/40 transition-all cursor-pointer"
                        >
                            <Menu className="h-4 w-4 text-emerald-400" />
                        </button>
                    </div>
                </div>
            </header>

            {/* ── Ultra-Modern Full-Screen Mobile Menu Overlay ── */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.96 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.96 }}
                        transition={{ duration: 0.25, ease: "easeOut" }}
                        className="fixed inset-0 z-50 flex flex-col justify-between bg-[#0A0A0B]/98 backdrop-blur-3xl px-4 py-5 font-mono overflow-y-auto"
                    >
                        {/* Overlay Header */}
                        <div className="flex items-center justify-between border-b border-tactical-border/60 pb-4">
                            <Link href="/" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2">
                                <ForenzaLogoIcon size={32} className="shadow-lg shadow-emerald-500/10" />
                                <span className="font-mono text-base font-extrabold tracking-wider text-white">
                                    FORENZA
                                </span>
                            </Link>

                            <div className="flex items-center gap-3">
                                <SaaSLanguageToggle />
                                <button
                                    type="button"
                                    onClick={() => setIsMobileMenuOpen(false)}
                                    aria-label="Close mobile menu"
                                    className="flex items-center justify-center p-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-all cursor-pointer"
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            </div>
                        </div>

                        {/* Centered Modern Navigation Items */}
                        <div className="my-auto py-8 space-y-3.5 flex flex-col items-center justify-center w-full max-w-sm mx-auto">
                            <motion.button
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.05 }}
                                type="button"
                                onClick={(e) => scrollToSection("bio-simulator", e)}
                                className="w-full py-3.5 px-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/90 hover:bg-emerald-500/10 hover:border-emerald-500/50 text-sm font-bold text-zinc-100 hover:text-emerald-300 transition-all duration-300 flex items-center justify-center gap-3 shadow-lg hover:shadow-[0_0_20px_rgba(16,185,129,0.2)] text-center cursor-pointer group"
                            >
                                <Activity className="w-4 h-4 text-cyan-400 shrink-0 group-hover:scale-110 transition-transform" />
                                <span>{t.header.bioSimulator}</span>
                            </motion.button>

                            <motion.button
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                                type="button"
                                onClick={(e) => scrollToSection("subsystems", e)}
                                className="w-full py-3.5 px-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/90 hover:bg-emerald-500/10 hover:border-emerald-500/50 text-sm font-bold text-zinc-100 hover:text-emerald-300 transition-all duration-300 flex items-center justify-center gap-3 shadow-lg hover:shadow-[0_0_20px_rgba(16,185,129,0.2)] text-center cursor-pointer group"
                            >
                                <Layers className="w-4 h-4 text-purple-400 shrink-0 group-hover:scale-110 transition-transform" />
                                <span>{t.header.subsystems}</span>
                            </motion.button>

                            <motion.button
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.15 }}
                                type="button"
                                onClick={(e) => scrollToSection("architecture", e)}
                                className="w-full py-3.5 px-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/90 hover:bg-emerald-500/10 hover:border-emerald-500/50 text-sm font-bold text-zinc-100 hover:text-emerald-300 transition-all duration-300 flex items-center justify-center gap-3 shadow-lg hover:shadow-[0_0_20px_rgba(16,185,129,0.2)] text-center cursor-pointer group"
                            >
                                <Cpu className="w-4 h-4 text-emerald-400 shrink-0 group-hover:scale-110 transition-transform" />
                                <span>{t.header.architecture}</span>
                            </motion.button>

                            <motion.button
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                                type="button"
                                onClick={(e) => scrollToSection("security", e)}
                                className="w-full py-3.5 px-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/90 hover:bg-emerald-500/10 hover:border-emerald-500/50 text-sm font-bold text-zinc-100 hover:text-emerald-300 transition-all duration-300 flex items-center justify-center gap-3 shadow-lg hover:shadow-[0_0_20px_rgba(16,185,129,0.2)] text-center cursor-pointer group"
                            >
                                <Shield className="w-4 h-4 text-amber-400 shrink-0 group-hover:scale-110 transition-transform" />
                                <span>{t.header.security}</span>
                            </motion.button>
                        </div>

                        {/* Overlay Footer Action */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.25 }}
                            className="pt-4 border-t border-tactical-border/60 flex flex-col items-center gap-3 w-full max-w-sm mx-auto"
                        >
                            <LaunchDemoButton size="lg" label={t.header.launchDemo} className="w-full py-3.5 text-xs font-bold" />
                            <span className="text-[10px] text-zinc-500 text-center font-mono">
                                VANTAGE v3.0 • ISO/IEC 17025 Certified Evidence OS
                            </span>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
