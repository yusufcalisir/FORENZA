"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { 
    Binary, Dna, Clock, Microscope, Scale, Globe, Eye,
    Layers, CheckCircle2, ChevronDown
} from "lucide-react";

const PILLAR_STYLES = [
    { icon: Binary, color: "cyan", accentBorder: "border-cyan-500/50", accentBg: "bg-cyan-500/10", accentText: "text-cyan-400", accentGlow: "shadow-cyan-500/20" },
    { icon: Dna, color: "purple", accentBorder: "border-purple-500/50", accentBg: "bg-purple-500/10", accentText: "text-purple-400", accentGlow: "shadow-purple-500/20" },
    { icon: Eye, color: "emerald", accentBorder: "border-emerald-500/50", accentBg: "bg-emerald-500/10", accentText: "text-emerald-400", accentGlow: "shadow-emerald-500/20" },
    { icon: Clock, color: "amber", accentBorder: "border-amber-500/50", accentBg: "bg-amber-500/10", accentText: "text-amber-400", accentGlow: "shadow-amber-500/20" },
    { icon: Microscope, color: "rose", accentBorder: "border-rose-500/50", accentBg: "bg-rose-500/10", accentText: "text-rose-400", accentGlow: "shadow-rose-500/20" },
    { icon: Scale, color: "cyan", accentBorder: "border-cyan-500/50", accentBg: "bg-cyan-500/10", accentText: "text-cyan-400", accentGlow: "shadow-cyan-500/20" },
    { icon: Globe, color: "emerald", accentBorder: "border-emerald-500/50", accentBg: "bg-emerald-500/10", accentText: "text-emerald-400", accentGlow: "shadow-emerald-500/20" },
];

export default function LandingFeatures() {
    const { t, lang } = useSaasLanguage();
    const isTr = lang === "tr";
    const [selectedPillar, setSelectedPillar] = useState<number>(0);
    // Mobile accordion: first pillar open by default (0)
    const [mobileOpenPillar, setMobileOpenPillar] = useState<number | null>(0);

    const pillars = t.subsystems.pillars.map((p, idx) => ({
        ...p,
        ...PILLAR_STYLES[idx % PILLAR_STYLES.length],
    }));

    const currentPillar = pillars[selectedPillar] || pillars[0];

    const toggleMobilePillar = (idx: number) => {
        setMobileOpenPillar((prev) => (prev === idx ? null : idx));
        setSelectedPillar(idx);
    };

    return (
        <section id="subsystems" className="scroll-mt-20 py-12 lg:py-28 border-b border-tactical-border/60 bg-black/60 font-mono relative overflow-hidden max-w-full">
            {/* Background Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-gradient-to-tr from-emerald-500/5 via-cyan-500/10 to-purple-600/5 blur-[150px] rounded-full pointer-events-none" />

            <div className="mx-auto max-w-7xl px-3 sm:px-6 lg:px-8 space-y-8 sm:space-y-12 relative z-10">
                
                {/* Section Header */}
                <div className="text-center max-w-3xl mx-auto space-y-3 sm:space-y-4 px-2">
                    <div className="inline-flex items-center gap-2 px-3 sm:px-4 py-1.5 rounded-full border border-emerald-500/40 bg-emerald-500/10 text-emerald-300 text-[10px] sm:text-xs font-bold uppercase tracking-wider shadow-lg shadow-emerald-500/10">
                        <Layers className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{t.subsystems.badge}</span>
                    </div>
                    <h2 className="text-xl sm:text-3xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
                        {t.subsystems.title}
                    </h2>
                    <p className="text-xs sm:text-sm text-zinc-400 max-w-2xl mx-auto leading-relaxed">
                        {t.subsystems.subtitle}
                    </p>
                </div>

                {/* ── MOBILE ACCORDION (lg:hidden) — Titles expand inline with downward arrow ── */}
                <div className="lg:hidden space-y-3">
                    {pillars.map((p, idx) => {
                        const isOpen = mobileOpenPillar === idx;
                        const PIcon = p.icon;
                        return (
                            <div
                                key={p.shortName}
                                className={`rounded-2xl border transition-all duration-300 overflow-hidden ${
                                    isOpen
                                        ? `${p.accentBorder} bg-tactical-surface shadow-xl`
                                        : "border-tactical-border/70 bg-tactical-surface/50 hover:border-tactical-border"
                                }`}
                            >
                                {/* Pillar Accordion Header Button with Downward Arrow */}
                                <button
                                    type="button"
                                    onClick={() => toggleMobilePillar(idx)}
                                    aria-expanded={isOpen}
                                    className="w-full p-4 flex items-center justify-between gap-3 text-left cursor-pointer transition-colors"
                                >
                                    <div className="flex items-center gap-3 min-w-0">
                                        <div className={`p-2.5 rounded-xl border shrink-0 ${
                                            isOpen
                                                ? `${p.accentBorder} ${p.accentBg} ${p.accentText}`
                                                : "border-tactical-border/80 bg-black/40 text-zinc-400"
                                        }`}>
                                            <PIcon className="w-5 h-5" />
                                        </div>
                                        <div className="min-w-0 space-y-0.5">
                                            <div className="flex items-center gap-2">
                                                <span className="text-[9px] text-zinc-400 font-bold uppercase">
                                                    {isTr ? `KATEGORİ 0${idx + 1}` : `PILLAR 0${idx + 1}`}
                                                </span>
                                                <span className="px-1.5 py-0.2 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                                                    5/5
                                                </span>
                                            </div>
                                            <h3 className={`text-xs sm:text-sm font-bold truncate ${
                                                isOpen ? "text-white" : "text-zinc-300"
                                            }`}>
                                                {p.name}
                                            </h3>
                                        </div>
                                    </div>

                                    {/* Downward Arrow Icon (Rotates when open) */}
                                    <div className={`p-1.5 rounded-lg border transition-all duration-300 shrink-0 ${
                                        isOpen
                                            ? `${p.accentBorder} ${p.accentText} rotate-180 bg-black/40`
                                            : "border-tactical-border text-zinc-400 bg-black/20"
                                    }`}>
                                        <ChevronDown className="w-4 h-4" />
                                    </div>
                                </button>

                                {/* Inline Expanded Subsystems Content for this Pillar */}
                                {isOpen && (
                                    <div className="px-3 pb-4 pt-2 border-t border-tactical-border/60 space-y-3 bg-black/30">
                                        <div className="grid grid-cols-1 gap-2.5">
                                            {p.subsystems.map((sub) => (
                                                <div
                                                    key={sub.id}
                                                    className="p-3.5 rounded-xl border border-tactical-border/80 bg-black/70 space-y-2 relative shadow-md"
                                                >
                                                    <div className="flex items-center justify-between">
                                                        <div className="flex items-center gap-1.5">
                                                            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-lg bg-emerald-500/20 font-mono text-[9px] font-bold text-emerald-400 border border-emerald-500/30">
                                                                {sub.id}
                                                            </span>
                                                            <span className="px-1.5 py-0.5 rounded text-[8px] font-bold bg-zinc-800 text-zinc-300 border border-zinc-700">
                                                                {sub.badge}
                                                            </span>
                                                        </div>
                                                        <span className="text-[8px] font-bold text-emerald-400 flex items-center gap-1">
                                                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                                            {isTr ? "AKTİF" : "ACTIVE"}
                                                        </span>
                                                    </div>

                                                    <h4 className="font-mono text-xs font-bold text-zinc-100 leading-snug">
                                                        {sub.name}
                                                    </h4>

                                                    <p className="text-[10px] text-zinc-400 leading-relaxed">
                                                        {sub.desc}
                                                    </p>

                                                    <div className="pt-2 border-t border-tactical-border/40 flex items-center justify-between text-[9px] text-zinc-400 font-mono">
                                                        <span className="text-zinc-500">{t.subsystems.operationalStatus}</span>
                                                        <span className="text-emerald-400 font-bold">{sub.metrics}</span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* ── DESKTOP TABS (hidden on mobile, visible on lg+) ── */}
                <div className="hidden lg:block space-y-8">
                    {/* 7 Category Selection Tabs */}
                    <div className="grid grid-cols-7 gap-3">
                        {pillars.map((p, idx) => {
                            const isSelected = selectedPillar === idx;
                            return (
                                <button
                                    key={p.shortName}
                                    type="button"
                                    onClick={() => setSelectedPillar(idx)}
                                    className={`p-4 rounded-2xl border transition-all duration-300 flex flex-col items-center text-center gap-2 cursor-pointer relative overflow-hidden group ${
                                        isSelected
                                            ? `${p.accentBorder} ${p.accentBg} shadow-lg ${p.accentGlow}`
                                            : "border-tactical-border/60 bg-tactical-surface/40 hover:border-tactical-border hover:bg-tactical-surface/80 text-zinc-400 hover:text-zinc-200"
                                    }`}
                                >
                                    <div className={`p-2 rounded-lg border transition-all ${
                                        isSelected 
                                            ? `${p.accentBorder} bg-black/40 ${p.accentText}` 
                                            : "border-transparent bg-zinc-800/40 text-zinc-400 group-hover:text-zinc-200"
                                    }`}>
                                        <p.icon className="w-5 h-5" />
                                    </div>
                                    <div className="space-y-0.5 min-w-0 w-full">
                                        <span className="text-[10px] text-zinc-400 font-bold block">
                                            {isTr ? `KATEGORİ 0${idx + 1}` : `PILLAR 0${idx + 1}`}
                                        </span>
                                        <span className={`text-xs font-bold block truncate ${
                                            isSelected ? "text-white" : ""
                                        }`}>
                                            {p.shortName}
                                        </span>
                                    </div>
                                </button>
                            );
                        })}
                    </div>

                    {/* Subsystem Matrix Cards Display for Desktop */}
                    <div className={`rounded-3xl border ${currentPillar.accentBorder} bg-tactical-surface/80 p-8 shadow-2xl space-y-6 backdrop-blur-xl transition-all duration-300 max-w-full overflow-hidden`}>
                        
                        {/* Matrix Sub-Header */}
                        <div className="flex items-center justify-between gap-3 border-b border-tactical-border/60 pb-5">
                            <div className="flex items-center gap-3.5 min-w-0">
                                <div className={`p-3 rounded-xl border shrink-0 ${currentPillar.accentBorder} ${currentPillar.accentBg} ${currentPillar.accentText}`}>
                                    <currentPillar.icon className="w-6 h-6" />
                                </div>
                                <div className="min-w-0">
                                    <h3 className="text-base font-extrabold uppercase tracking-wider text-white leading-snug break-words">
                                        {currentPillar.name}
                                    </h3>
                                    <p className="text-[10px] text-zinc-400 mt-0.5 truncate">
                                        {isTr ? `Kategori 0${selectedPillar + 1} • ${t.subsystems.activeCount}` : `Pillar 0${selectedPillar + 1} • ${t.subsystems.activeCount}`}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center gap-2 shrink-0">
                                <span className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                                    {isTr ? "5 / 5 AKTİF & OPERASYONEL" : "5 / 5 OPERATIONAL"}
                                </span>
                            </div>
                        </div>

                        {/* 5 Subsystem Cards Grid */}
                        <div className="grid grid-cols-3 gap-5">
                            {currentPillar.subsystems.map((sub, sIdx) => (
                                <motion.div
                                    key={sub.id}
                                    initial={{ opacity: 0, y: 15 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3, delay: sIdx * 0.06 }}
                                    className="p-5 rounded-2xl border border-tactical-border/80 bg-black/60 hover:border-emerald-500/40 transition-all duration-300 space-y-3.5 group relative shadow-lg flex flex-col justify-between"
                                >
                                    <div className="space-y-2.5">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-1.5">
                                                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-emerald-500/20 font-mono text-[10px] font-bold text-emerald-400 border border-emerald-500/30">
                                                    {sub.id}
                                                </span>
                                                <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-zinc-800 text-zinc-300 border border-zinc-700">
                                                    {sub.badge}
                                                </span>
                                            </div>
                                            <span className="text-[9px] font-bold text-emerald-400 flex items-center gap-1">
                                                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                                {isTr ? "AKTİF" : "ACTIVE"}
                                            </span>
                                        </div>

                                        <h4 className="font-mono text-sm font-bold text-zinc-100 group-hover:text-emerald-400 transition-colors leading-snug">
                                            {sub.name}
                                        </h4>

                                        <p className="text-xs text-zinc-400 leading-relaxed">
                                            {sub.desc}
                                        </p>
                                    </div>

                                    <div className="pt-3 border-t border-tactical-border/40 flex items-center justify-between text-[10px] text-zinc-400 font-mono">
                                        <span className="text-zinc-500">{t.subsystems.operationalStatus}</span>
                                        <span className="text-emerald-400 font-bold">{sub.metrics}</span>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Subsystem Matrix Telemetry Footer */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 sm:gap-4 p-3.5 sm:p-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/40 text-center font-mono text-xs">
                    <div>
                        <span className="text-zinc-500 text-[9px] sm:text-[10px] uppercase font-bold block">{t.subsystems.totalSubsystemsLabel}</span>
                        <span className="font-black text-emerald-400 text-sm sm:text-lg">{t.subsystems.totalSubsystemsValue}</span>
                    </div>
                    <div>
                        <span className="text-zinc-500 text-[9px] sm:text-[10px] uppercase font-bold block">{t.subsystems.archLayersLabel}</span>
                        <span className="font-black text-cyan-400 text-sm sm:text-lg">{t.subsystems.archLayersValue}</span>
                    </div>
                    <div>
                        <span className="text-zinc-500 text-[9px] sm:text-[10px] uppercase font-bold block">{t.subsystems.pytestInvariantsLabel}</span>
                        <span className="font-black text-purple-400 text-sm sm:text-lg">{t.subsystems.pytestInvariantsValue}</span>
                    </div>
                    <div>
                        <span className="text-zinc-500 text-[9px] sm:text-[10px] uppercase font-bold block">{t.subsystems.standardComplianceLabel}</span>
                        <span className="font-black text-amber-400 text-sm sm:text-lg">{t.subsystems.standardComplianceValue}</span>
                    </div>
                </div>
            </div>
        </section>
    );
}
