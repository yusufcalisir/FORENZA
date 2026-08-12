"use client";

import { useState } from "react";
import { Search, Heart, Shield, FlaskConical, CheckCircle2, FileText } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

const SOLUTION_ICONS = [Search, Heart, Shield, FlaskConical];
const SOLUTION_COLORS = ["#22C55E", "#06B6D4", "#8B5CF6", "#22C55E"];

export default function LandingSolutions() {
    const { t } = useSaasLanguage();
    const [activeIdx, setActiveIdx] = useState(0);

    const solutions = t.solutions.items.map((item, idx) => ({
        ...item,
        icon: SOLUTION_ICONS[idx % SOLUTION_ICONS.length],
        color: SOLUTION_COLORS[idx % SOLUTION_COLORS.length],
    }));

    const activeSolution = solutions[activeIdx] || solutions[0];
    const Icon = activeSolution.icon;

    return (
        <section id="solutions" className="scroll-mt-20 min-h-[85vh] lg:min-h-screen flex flex-col justify-between py-12 px-4 bg-tactical-surface/30 w-full max-w-full overflow-hidden">
            <div className="my-auto mx-auto max-w-6xl w-full">
                {/* Header */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center gap-2 rounded-full border border-[#06B6D4]/30 bg-[#06B6D4]/5 px-4 py-1.5 mb-3 shadow-[0_0_15px_rgba(6,182,212,0.1)]">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#06B6D4] animate-pulse" />
                        <span className="font-mono text-[10px] tracking-widest text-[#06B6D4] uppercase font-bold">
                            {t.solutions.badge}
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-bold text-tactical-text mb-3">
                        {t.solutions.title}
                    </h2>
                    <p className="max-w-xl mx-auto text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                        {t.solutions.subtitle}
                    </p>
                </div>

                {/* Interactive Solution Tabs */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
                    {solutions.map((s, i) => {
                        const SIcon = s.icon;
                        const isActive = activeIdx === i;
                        return (
                            <button
                                key={s.id}
                                onClick={() => setActiveIdx(i)}
                                className={`flex items-center gap-3 p-3.5 rounded-xl border font-mono text-xs transition-all duration-300 text-left cursor-pointer ${
                                    isActive
                                        ? "bg-tactical-surface-elevated text-white border-current shadow-lg"
                                        : "bg-tactical-surface/60 text-tactical-text-muted border-tactical-border/60 hover:border-tactical-border hover:text-white"
                                }`}
                                style={isActive ? { color: s.color, borderColor: s.color } : {}}
                            >
                                <SIcon className="h-4 w-4 shrink-0" style={{ color: s.color }} />
                                <span className="font-bold truncate">{s.label}</span>
                            </button>
                        );
                    })}
                </div>

                {/* Main Domain Inspector Card */}
                <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface p-5 sm:p-7 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                        {/* Left Info Column */}
                        <div className="lg:col-span-7 space-y-5">
                            <div className="flex items-center gap-3">
                                <div
                                    className="flex h-11 w-11 items-center justify-center rounded-xl border shrink-0"
                                    style={{
                                        background: `${activeSolution.color}15`,
                                        borderColor: `${activeSolution.color}35`,
                                        color: activeSolution.color,
                                    }}
                                >
                                    <Icon className="h-5 w-5" />
                                </div>
                                <div>
                                    <span
                                        className="font-mono text-[10px] tracking-widest uppercase font-bold"
                                        style={{ color: activeSolution.color }}
                                    >
                                        {activeSolution.label}
                                    </span>
                                    <h3 className="text-xl sm:text-2xl font-bold text-white">
                                        {activeSolution.title}
                                    </h3>
                                </div>
                            </div>

                            <p className="text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                                {activeSolution.description}
                            </p>

                            {/* Checklist */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
                                {activeSolution.bulletPoints.map((point) => (
                                    <div key={point} className="flex items-start gap-2.5">
                                        <CheckCircle2
                                            className="h-4 w-4 shrink-0 mt-0.5"
                                            style={{ color: activeSolution.color }}
                                        />
                                        <span className="text-tactical-text text-xs leading-snug">{point}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Right Interactive Mock Output Card */}
                        <div className="lg:col-span-5 rounded-xl border border-tactical-border bg-tactical-bg/90 p-5 space-y-4 shadow-xl font-mono">
                            <div className="flex items-center justify-between border-b border-tactical-border/80 pb-2.5">
                                <div className="flex items-center gap-2">
                                    <FileText className="h-4 w-4" style={{ color: activeSolution.color }} />
                                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                                        {t.solutions.domainInspection}
                                    </span>
                                </div>
                                <span className="text-[9px] text-[#22C55E] bg-[#22C55E]/10 border border-[#22C55E]/20 px-2 py-0.5 rounded font-bold">
                                    {t.solutions.activeStandard}
                                </span>
                            </div>

                            <div className="space-y-2.5">
                                <div>
                                    <span className="text-[9px] text-tactical-text-dim uppercase tracking-wider block font-bold">
                                        {t.solutions.primaryMetric}
                                    </span>
                                    <span
                                        className="text-base sm:text-lg font-bold text-white"
                                        style={{ color: activeSolution.color }}
                                    >
                                        {activeSolution.sampleMetric}
                                    </span>
                                </div>

                                <div className="rounded-lg border border-tactical-border bg-tactical-surface p-3 space-y-1">
                                    <span className="text-[9px] text-tactical-text-dim block font-bold">
                                        {t.solutions.sessionTarget}:
                                    </span>
                                    <span className="text-xs text-tactical-text break-all font-semibold">
                                        {activeSolution.sampleCode}
                                    </span>
                                </div>

                                <div className="flex items-center justify-between text-[10px] pt-1">
                                    <span className="text-tactical-text-dim font-bold">{t.solutions.verificationStatus}</span>
                                    <span className="font-bold text-[#22C55E]">{t.solutions.auditPassed}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
