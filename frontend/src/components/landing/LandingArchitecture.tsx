"use client";

import { motion } from "framer-motion";
import { Cpu, Network, CheckCircle2, ShieldCheck, Activity, Layers, ArrowRight } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function LandingArchitecture() {
    const { t } = useSaasLanguage();
    const layers = t.architecture.layers;

    return (
        <section id="architecture" className="py-16 lg:py-24 border-b border-tactical-border/60 w-full max-w-full overflow-hidden">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-12">
                
                {/* Header */}
                <div className="text-center max-w-3xl mx-auto space-y-3">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 font-mono text-xs font-bold uppercase">
                        <Cpu className="w-3.5 h-3.5" />
                        {t.architecture.badge}
                    </div>
                    <h2 className="text-2xl sm:text-4xl font-extrabold font-mono text-white tracking-tight">
                        {t.architecture.title}
                    </h2>
                    <p className="text-xs sm:text-sm text-zinc-400 font-mono">
                        {t.architecture.subtitle}
                    </p>
                </div>

                {/* DAG Layer Flow Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 font-mono">
                    {layers.map((item, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 15 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.4, delay: idx * 0.08 }}
                            className="p-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 space-y-4 shadow-xl hover:border-emerald-500/40 transition-all"
                        >
                            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                                <span className="text-xs font-bold uppercase text-zinc-200">{item.layer}</span>
                                <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                                    {item.badge}
                                </span>
                            </div>

                            <div className="space-y-2">
                                {item.nodes.map((node, nIdx) => (
                                    <div key={nIdx} className="flex items-center justify-between text-[10px] p-2 rounded-lg bg-black/40 border border-tactical-border/40">
                                        <span className="text-zinc-300 font-bold">{node}</span>
                                        <span className="flex items-center gap-1 text-emerald-400 font-bold">
                                            <CheckCircle2 className="w-3 h-3" />
                                            ACTIVE
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
