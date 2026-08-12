"use client";

import { motion } from "framer-motion";
import { Dna, ShieldCheck, Activity, Cpu, Sparkles, Scale, Lock, Layers } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function LandingHero() {
    const { t } = useSaasLanguage();

    return (
        <section className="relative overflow-hidden pt-12 pb-16 lg:pt-20 lg:pb-24 border-b border-tactical-border/60">
            {/* Background Glow Overlay */}
            <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-cyan-500/10 via-tactical-accent/20 to-purple-600/10 blur-[120px] rounded-full pointer-events-none" />

            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="text-center max-w-4xl mx-auto space-y-6">
                    
                    {/* Top Announcement Badge */}
                    <motion.div
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-tactical-accent/40 bg-tactical-accent/10 backdrop-blur-md"
                    >
                        <Sparkles className="w-4 h-4 text-tactical-accent animate-pulse" />
                        <span className="font-mono text-xs font-bold text-tactical-accent uppercase tracking-wider">
                            {t.hero.badge}
                        </span>
                    </motion.div>

                    {/* Main Headline */}
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="text-3xl sm:text-5xl lg:text-6xl font-extrabold font-mono tracking-tight text-white leading-tight"
                    >
                        {t.hero.titleMain}{" "}
                        <span className="bg-gradient-to-r from-emerald-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent">
                            {t.hero.titleHighlight}
                        </span>
                    </motion.h1>

                    {/* Subtitle */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="text-sm sm:text-base text-zinc-300 font-mono leading-relaxed max-w-3xl mx-auto"
                    >
                        {t.hero.subtitle}
                    </motion.p>

                    {/* CTA Actions */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4"
                    >
                        <LaunchDemoButton label={t.hero.launchDemo} className="w-full sm:w-auto text-sm py-3.5 px-8" />
                        <button
                            type="button"
                            onClick={(e) => {
                                e.preventDefault();
                                const el = document.getElementById("subsystems");
                                if (el) {
                                    const headerOffset = 70;
                                    const elementPosition = el.getBoundingClientRect().top;
                                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                                    window.scrollTo({ top: offsetPosition, behavior: "smooth" });
                                }
                            }}
                            className="w-full sm:w-auto px-6 py-3.5 rounded-xl border border-tactical-border/80 bg-tactical-surface hover:bg-tactical-surface-elevated font-mono text-xs font-bold text-zinc-200 uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer"
                        >
                            <Layers className="w-4 h-4 text-purple-400" />
                            {t.hero.exploreSubsystems}
                        </button>
                    </motion.div>

                    {/* Key Executive Telemetry Grid */}
                    <motion.div
                        initial={{ opacity: 0, y: 25 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.4 }}
                        className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-10 border-t border-tactical-border/50 font-mono"
                    >
                        <div className="p-4 rounded-2xl bg-black/40 border border-tactical-border/60 backdrop-blur-md">
                            <div className="text-2xl font-black text-tactical-accent">30</div>
                            <div className="text-[10px] text-zinc-400 uppercase tracking-wider mt-1 font-bold">Forensic Subsystems</div>
                        </div>

                        <div className="p-4 rounded-2xl bg-black/40 border border-tactical-border/60 backdrop-blur-md">
                            <div className="text-2xl font-black text-emerald-400">215/215</div>
                            <div className="text-[10px] text-zinc-400 uppercase tracking-wider mt-1 font-bold">Verified Invariants</div>
                        </div>

                        <div className="p-4 rounded-2xl bg-black/40 border border-tactical-border/60 backdrop-blur-md">
                            <div className="text-2xl font-black text-cyan-400">ISO 17025</div>
                            <div className="text-[10px] text-zinc-400 uppercase tracking-wider mt-1 font-bold">Court Admissible</div>
                        </div>

                        <div className="p-4 rounded-2xl bg-black/40 border border-tactical-border/60 backdrop-blur-md">
                            <div className="text-2xl font-black text-amber-400">zkSNARK</div>
                            <div className="text-[10px] text-zinc-400 uppercase tracking-wider mt-1 font-bold">Privacy Auditor</div>
                        </div>
                    </motion.div>

                </div>
            </div>
        </section>
    );
}
