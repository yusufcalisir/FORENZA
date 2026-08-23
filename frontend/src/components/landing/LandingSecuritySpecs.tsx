"use client";

import { Lock, FileCheck, AlertOctagon, Cpu, CheckCircle2, ShieldCheck } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

const SECURITY_ICONS = [Lock, FileCheck, AlertOctagon, Cpu];
const SECURITY_COLORS = ["#22C55E", "#06B6D4", "#8B5CF6", "#22C55E"];

export default function LandingSecuritySpecs() {
    const { t } = useSaasLanguage();

    const securityPillars = t.security.pillars.map((item, idx) => ({
        ...item,
        icon: SECURITY_ICONS[idx % SECURITY_ICONS.length],
        color: SECURITY_COLORS[idx % SECURITY_COLORS.length],
    }));

    const specs = t.security.specs;

    return (
        <section id="security" className="scroll-mt-20 flex flex-col justify-between py-12 sm:py-16 lg:py-20 px-3 sm:px-6 lg:px-8 bg-tactical-surface/30 border-b border-tactical-border/60 w-full max-w-full overflow-hidden font-mono">
            <div className="mx-auto max-w-7xl w-full space-y-10 sm:space-y-12">
                
                {/* Section Header */}
                <div className="text-center max-w-3xl mx-auto space-y-3 px-2">
                    <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3.5 py-1.5 shadow-lg shadow-emerald-500/10">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span className="font-mono text-[10px] sm:text-xs font-bold text-emerald-300 uppercase tracking-wider">
                            {t.security.badge}
                        </span>
                    </div>
                    <h2 className="text-2xl sm:text-4xl lg:text-5xl font-extrabold font-mono text-white tracking-tight leading-tight">
                        {t.security.title}
                    </h2>
                    <p className="max-w-2xl mx-auto text-zinc-400 font-mono text-xs sm:text-sm leading-relaxed">
                        {t.security.subtitle}
                    </p>
                </div>

                {/* 4 Security Pillars Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3.5 sm:gap-4">
                    {securityPillars.map((pillar) => {
                        const Icon = pillar.icon;
                        return (
                            <div
                                key={pillar.title}
                                className="rounded-2xl border border-tactical-border/80 bg-tactical-surface p-5 shadow-xl hover:border-emerald-500/40 transition-all duration-200 space-y-3 group"
                            >
                                <div
                                    className="inline-flex h-10 w-10 items-center justify-center rounded-xl border shrink-0 transition-transform group-hover:scale-105"
                                    style={{
                                        background: `${pillar.color}15`,
                                        borderColor: `${pillar.color}35`,
                                        color: pillar.color,
                                    }}
                                >
                                    <Icon className="h-5 w-5" />
                                </div>
                                <div>
                                    <h3 className="font-mono font-bold text-zinc-100 text-sm sm:text-base leading-snug mb-1.5">
                                        {pillar.title}
                                    </h3>
                                    <p className="font-mono text-zinc-400 text-xs leading-relaxed">
                                        {pillar.desc}
                                    </p>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Technical Specifications Table */}
                <div className="rounded-2xl sm:rounded-3xl border border-tactical-border/80 bg-tactical-surface overflow-hidden shadow-2xl font-mono">
                    {/* Responsive Header: Stacks cleanly on mobile, side-by-side on tablet/desktop */}
                    <div className="border-b border-tactical-border/70 bg-black/60 px-4 sm:px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                        <span className="text-xs sm:text-sm font-bold uppercase tracking-wider text-white">
                            {t.security.matrixTitle}
                        </span>
                        <span className="self-start sm:self-auto shrink-0 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[10px] sm:text-xs font-bold uppercase whitespace-nowrap shadow-sm">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                            {t.security.passedBadge}
                        </span>
                    </div>

                    {/* Matrix Rows with Generous Padding & Clear Visual Hierarchy */}
                    <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-tactical-border/50">
                        {/* Column 1 */}
                        <div className="divide-y divide-tactical-border/50">
                            {specs.slice(0, Math.ceil(specs.length / 2)).map((spec, i) => (
                                <div
                                    key={i}
                                    className="px-4 sm:px-6 py-4 sm:py-4.5 flex flex-col gap-1.5 hover:bg-white/[0.02] transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400/80 shrink-0" />
                                        <span className="text-xs font-mono font-bold text-emerald-400 tracking-wide">
                                            {spec.label}
                                        </span>
                                    </div>
                                    <p className="text-xs sm:text-sm font-sans font-medium text-zinc-200 leading-relaxed pl-3.5">
                                        {spec.value}
                                    </p>
                                </div>
                            ))}
                        </div>

                        {/* Column 2 */}
                        <div className="divide-y divide-tactical-border/50">
                            {specs.slice(Math.ceil(specs.length / 2)).map((spec, i) => (
                                <div
                                    key={i}
                                    className="px-4 sm:px-6 py-4 sm:py-4.5 flex flex-col gap-1.5 hover:bg-white/[0.02] transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400/80 shrink-0" />
                                        <span className="text-xs font-mono font-bold text-cyan-400 tracking-wide">
                                            {spec.label}
                                        </span>
                                    </div>
                                    <p className="text-xs sm:text-sm font-sans font-medium text-zinc-200 leading-relaxed pl-3.5">
                                        {spec.value}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

            </div>
        </section>
    );
}
