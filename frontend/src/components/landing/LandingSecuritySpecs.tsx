"use client";

import { Lock, FileCheck, AlertOctagon, Cpu } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

const SECURITY_ICONS = [Lock, FileCheck, AlertOctagon, Cpu];
const SECURITY_COLORS = ["#22C55E", "#06B6D4", "#8B5CF6", "#22C55E"];
const SPEC_COLORS = ["#22C55E", "#06B6D4", "#8B5CF6", "#22C55E", "#06B6D4", "#8B5CF6", "#22C55E", "#06B6D4", "#8B5CF6", "#22C55E", "#06B6D4", "#8B5CF6"];

export default function LandingSecuritySpecs() {
    const { t } = useSaasLanguage();

    const securityPillars = t.security.pillars.map((item, idx) => ({
        ...item,
        icon: SECURITY_ICONS[idx % SECURITY_ICONS.length],
        color: SECURITY_COLORS[idx % SECURITY_COLORS.length],
    }));

    const specs = t.security.specs.map((item, idx) => ({
        ...item,
        color: SPEC_COLORS[idx % SPEC_COLORS.length],
    }));

    return (
        <section id="security" className="scroll-mt-20 flex flex-col justify-between py-16 px-4 bg-tactical-surface/30 border-b border-tactical-border/60 w-full max-w-full overflow-hidden">
            <div className="mx-auto max-w-7xl w-full space-y-12">
                
                {/* Header */}
                <div className="text-center max-w-3xl mx-auto space-y-3">
                    <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 shadow-lg">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="font-mono text-xs font-bold text-emerald-300 uppercase tracking-wider">
                            {t.security.badge}
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-extrabold font-mono text-white tracking-tight">
                        {t.security.title}
                    </h2>
                    <p className="max-w-2xl mx-auto text-zinc-400 font-mono text-xs sm:text-sm leading-relaxed">
                        {t.security.subtitle}
                    </p>
                </div>

                {/* Security Pillars Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                    {securityPillars.map((pillar) => {
                        const Icon = pillar.icon;
                        return (
                            <div
                                key={pillar.title}
                                className="rounded-2xl border border-tactical-border/80 bg-tactical-surface p-5 shadow-xl hover:border-emerald-500/40 transition-colors"
                            >
                                <div
                                    className="mb-3 inline-flex h-9 w-9 items-center justify-center rounded-xl border"
                                    style={{
                                        background: `${pillar.color}15`,
                                        borderColor: `${pillar.color}30`,
                                        color: pillar.color,
                                    }}
                                >
                                    <Icon className="h-4.5 w-4.5" />
                                </div>
                                <h3 className="font-mono font-bold text-zinc-200 text-sm mb-1.5 leading-snug">
                                    {pillar.title}
                                </h3>
                                <p className="font-mono text-zinc-400 text-xs leading-relaxed">
                                    {pillar.desc}
                                </p>
                            </div>
                        );
                    })}
                </div>

                {/* Technical Specifications Table */}
                <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface overflow-hidden shadow-2xl font-mono">
                    <div className="border-b border-tactical-border/60 bg-black/60 px-6 py-4 flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-zinc-200">
                            {t.security.matrixTitle}
                        </span>
                        <span className="px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-[9px] font-bold uppercase">
                            {t.security.passedBadge}
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-tactical-border/40">
                        <div className="divide-y divide-tactical-border/40">
                            {specs.slice(0, 6).map((spec, i) => (
                                <div key={i} className="px-6 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-1 hover:bg-black/20 transition-colors">
                                    <span className="text-xs font-bold text-zinc-400">{spec.label}</span>
                                    <span className="text-xs font-bold text-zinc-200 sm:text-right">{spec.value}</span>
                                </div>
                            ))}
                        </div>
                        <div className="divide-y divide-tactical-border/40">
                            {specs.slice(6).map((spec, i) => (
                                <div key={i} className="px-6 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-1 hover:bg-black/20 transition-colors">
                                    <span className="text-xs font-bold text-zinc-400">{spec.label}</span>
                                    <span className="text-xs font-bold text-zinc-200 sm:text-right">{spec.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
