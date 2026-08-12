"use client";

import { useState } from "react";
import { ChevronDown, HelpCircle } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function LandingFaq() {
    const { t } = useSaasLanguage();
    const [openIdx, setOpenIdx] = useState<number | null>(0);

    const faqs = [
        { q: t.faq.questions.q1, a: t.faq.questions.a1, color: "#22C55E" },
        { q: t.faq.questions.q2, a: t.faq.questions.a2, color: "#06B6D4" },
        { q: t.faq.questions.q3, a: t.faq.questions.a3, color: "#8B5CF6" },
        { q: t.faq.questions.q4, a: t.faq.questions.a4, color: "#22C55E" },
        { q: t.faq.questions.q5, a: t.faq.questions.a5, color: "#06B6D4" },
    ];

    return (
        <section id="faq" className="scroll-mt-20 py-16 px-4 font-mono border-b border-tactical-border/60">
            <div className="mx-auto max-w-3xl w-full space-y-10">
                
                {/* Header */}
                <div className="text-center space-y-3">
                    <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1.5 shadow-lg">
                        <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
                        <span className="font-mono text-xs font-bold text-cyan-300 uppercase tracking-wider">
                            {t.faq.badge}
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                        {t.faq.title}
                    </h2>
                    <p className="text-xs sm:text-sm text-zinc-400 max-w-lg mx-auto">
                        {t.faq.subtitle}
                    </p>
                </div>

                {/* FAQ Accordions */}
                <div className="space-y-3">
                    {faqs.map((faq, i) => {
                        const isOpen = openIdx === i;
                        return (
                            <div
                                key={i}
                                className="rounded-2xl border border-tactical-border/80 bg-tactical-surface overflow-hidden transition-all duration-200 shadow-xl"
                                style={isOpen ? { borderColor: `${faq.color}60` } : {}}
                            >
                                <button
                                    onClick={() => setOpenIdx(isOpen ? null : i)}
                                    className="w-full flex items-center justify-between gap-4 px-6 py-4 text-left hover:bg-tactical-surface-elevated/50 transition-colors cursor-pointer"
                                >
                                    <span className="font-bold text-zinc-200 text-xs sm:text-sm leading-snug pr-2">
                                        {faq.q}
                                    </span>
                                    <ChevronDown
                                        className={`h-4 w-4 shrink-0 transition-transform duration-300 ${
                                            isOpen ? "rotate-180" : ""
                                        }`}
                                        style={{ color: isOpen ? faq.color : undefined }}
                                    />
                                </button>
                                {isOpen && (
                                    <div className="px-6 pb-5">
                                        <div
                                            className="h-px mb-3"
                                            style={{
                                                background: `linear-gradient(to right, ${faq.color}40, transparent)`,
                                            }}
                                        />
                                        <p className="text-zinc-400 text-xs sm:text-sm leading-relaxed">
                                            {faq.a}
                                        </p>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

            </div>
        </section>
    );
}
