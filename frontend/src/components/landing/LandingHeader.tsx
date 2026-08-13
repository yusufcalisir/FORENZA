"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Shield, Activity, Cpu, Layers, Menu, X, BookOpen, KeyRound } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";
import SaaSLanguageToggle from "./SaaSLanguageToggle";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import UserGuideModal from "@/components/common/UserGuideModal";
import ApiKeySettingsModal from "@/components/common/ApiKeySettingsModal";
import { getActiveModeLabel, hasLiveApiKeys } from "@/services/apiClient";

export default function LandingHeader() {
    const { lang, t } = useSaasLanguage();
    const isTr = lang === "tr";
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isGuideOpen, setIsGuideOpen] = useState(false);
    const [isApiModalOpen, setIsApiModalOpen] = useState(false);
    const [modeInfo, setModeInfo] = useState({ label: "DEMO SİMÜLASYON MODU", isLive: false });

    useEffect(() => {
        const updateMode = () => setModeInfo(getActiveModeLabel(isTr));
        updateMode();
        window.addEventListener("forenza-apikeys-updated", updateMode);
        return () => window.removeEventListener("forenza-apikeys-updated", updateMode);
    }, [isTr]);

    // Prevent body scrolling when mobile menu overlay is open
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

    const guideLabel = lang === "tr" ? "Kullanım Kılavuzu" : "User Guide";

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
                        {/* Compact Key Icon Launcher with Live Status Indicator Dot */}
                        <button
                            type="button"
                            onClick={() => setIsApiModalOpen(true)}
                            aria-label="API Credentials Settings"
                            className={`relative p-2 rounded-xl border transition-all flex items-center justify-center cursor-pointer ${
                                modeInfo.isLive
                                    ? "bg-emerald-500/15 border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/25 shadow-[0_0_12px_rgba(16,185,129,0.2)]"
                                    : "bg-purple-500/15 border-purple-500/40 text-purple-300 hover:bg-purple-500/25"
                            }`}
                            title={modeInfo.isLive ? (isTr ? "API Anahtarları Aktif (Canlı Mod)" : "API Keys Active (Live Production)") : (isTr ? "API Anahtarlarını Yönet (Demo Modu)" : "Manage API Keys (Demo Mode)")}
                        >
                            <KeyRound className={`w-4 h-4 ${modeInfo.isLive ? "text-emerald-400" : "text-purple-400"}`} />
                            {modeInfo.isLive && (
                                <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 animate-pulse border border-black" />
                            )}
                        </button>

                        <button
                            type="button"
                            onClick={() => setIsGuideOpen(true)}
                            className="px-2.5 py-1.5 rounded-xl font-mono text-[10px] sm:text-xs font-bold bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/25 transition-all flex items-center gap-1.5 cursor-pointer shadow-[0_0_12px_rgba(6,182,212,0.15)]"
                            title={guideLabel}
                        >
                            <BookOpen className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                            <span className="hidden sm:inline">{guideLabel}</span>
                        </button>
                        
                        {/* Compact Mobile Demo Button */}
                        <LaunchDemoButton size="sm" label={t.header.launchDemo} compactMobile={true} />

                        {/* Global Language Toggle (Positioned on the far right) */}
                        <SaaSLanguageToggle />

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

            {/* User Guide Interactive Modal */}
            <UserGuideModal isOpen={isGuideOpen} onClose={() => setIsGuideOpen(false)} />

            {/* API Credentials Settings Modal */}
            <ApiKeySettingsModal isOpen={isApiModalOpen} onClose={() => setIsApiModalOpen(false)} />

            {/* ── Ultra-Fast 60FPS Mobile Menu Overlay (Pure CSS GPU Accelerated) ── */}
            <div
                className={`fixed inset-0 z-50 flex flex-col justify-between bg-[#0A0A0B] px-4 py-5 font-mono transition-all duration-150 ease-out ${
                    isMobileMenuOpen
                        ? "opacity-100 pointer-events-auto translate-y-0"
                        : "opacity-0 pointer-events-none -translate-y-2"
                }`}
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
                            className="flex items-center justify-center p-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-colors cursor-pointer"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>
                </div>

                {/* Centered Modern Navigation Items */}
                <div className="my-auto py-8 space-y-3 flex flex-col items-center justify-center w-full max-w-sm mx-auto">
                    <button
                        type="button"
                        onClick={(e) => scrollToSection("bio-simulator", e)}
                        className="w-full py-3.5 px-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface text-sm font-bold text-zinc-100 hover:text-emerald-300 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-all duration-150 flex items-center justify-center gap-3 shadow-md text-center cursor-pointer group"
                    >
                        <Activity className="w-4 h-4 text-cyan-400 shrink-0 group-hover:scale-110 transition-transform" />
                        <span>{t.header.bioSimulator}</span>
                    </button>

                    <button
                        type="button"
                        onClick={(e) => scrollToSection("subsystems", e)}
                        className="w-full py-3.5 px-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface text-sm font-bold text-zinc-100 hover:text-emerald-300 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-all duration-150 flex items-center justify-center gap-3 shadow-md text-center cursor-pointer group"
                    >
                        <Layers className="w-4 h-4 text-purple-400 shrink-0 group-hover:scale-110 transition-transform" />
                        <span>{t.header.subsystems}</span>
                    </button>

                    <button
                        type="button"
                        onClick={(e) => scrollToSection("architecture", e)}
                        className="w-full py-3.5 px-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface text-sm font-bold text-zinc-100 hover:text-emerald-300 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-all duration-150 flex items-center justify-center gap-3 shadow-md text-center cursor-pointer group"
                    >
                        <Cpu className="w-4 h-4 text-emerald-400 shrink-0 group-hover:scale-110 transition-transform" />
                        <span>{t.header.architecture}</span>
                    </button>

                    <button
                        type="button"
                        onClick={(e) => scrollToSection("security", e)}
                        className="w-full py-3.5 px-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface text-sm font-bold text-zinc-100 hover:text-emerald-300 hover:border-emerald-500/50 hover:bg-emerald-500/10 transition-all duration-150 flex items-center justify-center gap-3 shadow-md text-center cursor-pointer group"
                    >
                        <Shield className="w-4 h-4 text-amber-400 shrink-0 group-hover:scale-110 transition-transform" />
                        <span>{t.header.security}</span>
                    </button>

                    <button
                        type="button"
                        onClick={() => {
                            setIsMobileMenuOpen(false);
                            setIsGuideOpen(true);
                        }}
                        className="w-full py-3.5 px-5 rounded-2xl border border-cyan-500/40 bg-cyan-500/10 text-sm font-bold text-cyan-300 hover:bg-cyan-500/20 transition-all duration-150 flex items-center justify-center gap-3 shadow-md text-center cursor-pointer group"
                    >
                        <BookOpen className="w-4 h-4 text-cyan-400 shrink-0 group-hover:scale-110 transition-transform" />
                        <span>{guideLabel}</span>
                    </button>
                </div>

                {/* Overlay Footer Action */}
                <div className="pt-4 border-t border-tactical-border/60 flex flex-col items-center gap-3 w-full max-w-sm mx-auto">
                    <LaunchDemoButton size="lg" label={t.header.launchDemo} className="w-full py-3.5 text-xs font-bold" />
                    <span className="text-[10px] text-zinc-500 text-center font-mono">
                        FORENZA • ISO/IEC 17025 Certified Evidence OS
                    </span>
                </div>
            </div>
        </>
    );
}
