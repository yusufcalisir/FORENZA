"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
    ShieldCheck, Dna, FlaskConical, Network, Database, GitGraph,
    Activity, Cpu, Radio, Lock, ChevronRight, TrendingUp,
    Microscope, Fingerprint, Pill, Eye, Layers, Brain, Clock,
    FileText, Zap, BarChart3, Binary, Sparkles
} from "lucide-react";
import ActiveProfileBanner from "@/components/common/ActiveProfileBanner";

// ── Mock live metrics ──
const LIVE_METRICS = [
    { label: "Active Subsystems", value: "30 / 30", color: "text-emerald-400", icon: Layers, trend: "+0" },
    { label: "DNA Profiles Indexed", value: "1,847,291", color: "text-cyan-400", icon: Dna, trend: "+142" },
    { label: "LR Engine Throughput", value: "2,340 / s", color: "text-purple-400", icon: Cpu, trend: "+12%" },
    { label: "ZKP Proofs Verified", value: "48,931", color: "text-amber-400", icon: Lock, trend: "+89" },
    { label: "Federated Nodes", value: "7 Online", color: "text-blue-400", icon: Network, trend: "0" },
    { label: "ISO Compliance", value: "100%", color: "text-rose-400", icon: ShieldCheck, trend: "PASS" },
];

// ── 6 module category cards ──
const MODULE_CARDS = [
    {
        id: "dna",
        title: "DNA Profiling & Kinship",
        subtitle: "STR • SNP • mtDNA • Y-STR • Kinship • Ancestry",
        icon: Dna,
        color: "emerald",
        href: "/analysis",
        tab: "str",
        modules: 6,
        status: "OPERATIONAL",
        badge: "CODIS COMPLIANT",
        metrics: [
            { label: "Log10(LR)", value: "+18.4" },
            { label: "CODIS Loci", value: "20/20" },
        ],
        description: "SWGDAM STR analysis with population-specific allele frequencies, Y-STR haplogroup inference, and kinship coefficient computation.",
    },
    {
        id: "prob",
        title: "Probabilistic Genotyping",
        subtitle: "MCMC • Mixture Deconvolution • Bayesian",
        icon: BarChart3,
        color: "cyan",
        href: "/analysis",
        tab: "mcmc",
        modules: 4,
        status: "OPERATIONAL",
        badge: "MCMC ENGINE",
        metrics: [
            { label: "Contributors", value: "1–5" },
            { label: "Iterations", value: "50k" },
        ],
        description: "Continuous interpretation with Markov Chain Monte Carlo sampling. Full SWGDAM mixture guidelines compliance.",
    },
    {
        id: "phenotype",
        title: "Phenotype & Prediction",
        subtitle: "HIrisPlex-S • Horvath Clock • DVI • Human ID",
        icon: Brain,
        color: "purple",
        href: "/analysis",
        tab: "phenotype",
        modules: 6,
        status: "OPERATIONAL",
        badge: "AI POWERED",
        metrics: [
            { label: "Eye Colors", value: "5 class" },
            { label: "Age Δ", value: "±3.4 yr" },
        ],
        description: "HIrisPlex-S 41-SNP phenotyping system, Horvath epigenetic aging clock, anthropological trauma analysis.",
    },
    {
        id: "physical",
        title: "Physical Evidence",
        subtitle: "Touch DNA • Serology • Toxicology • Microscopy • BPA",
        icon: Microscope,
        color: "orange",
        href: "/analysis",
        tab: "touch",
        modules: 6,
        status: "OPERATIONAL",
        badge: "ISO 17025",
        metrics: [
            { label: "BAC Widmark", value: "U95 ±0.09" },
            { label: "LtDNA Thr.", value: "150 pg" },
        ],
        description: "Low-template DNA, serology blood group, forensic toxicology Widmark BAC, BPA impact angle, microscopy hair classification.",
    },
    {
        id: "lims",
        title: "LIMS & QA/QC",
        subtitle: "LIMS • Instrument Gateway • ISO Report • Human Review",
        icon: FileText,
        color: "blue",
        href: "/analysis",
        tab: "lims",
        modules: 6,
        status: "OPERATIONAL",
        badge: "DUAL SIGN-OFF",
        metrics: [
            { label: "Chain Custody", value: "HMAC-SHA256" },
            { label: "Batch QC", value: "± 2σ" },
        ],
        description: "Full laboratory information management, capillary electrophoresis instrument gateway, ISO 17025 court-admissible report generation.",
    },
    {
        id: "ai",
        title: "AI & Advanced Analytics",
        subtitle: "Epigenetics • Forensic Genomics • Synthetic Cases • Evidence OS",
        icon: Sparkles,
        color: "rose",
        href: "/analysis",
        tab: "epigenetics",
        modules: 5,
        status: "OPERATIONAL",
        badge: "FORENZA CORE",
        metrics: [
            { label: "Synthetic Gen.", value: "∞ Cases" },
            { label: "ZKP Privacy", value: "Circom" },
        ],
        description: "Horvath methylation epigenetics, multi-layer forensic genomics, synthetic case generator for academic validation, Evidence OS DAG orchestrator.",
    },
];

const COLOR_MAP: Record<string, { border: string; bg: string; text: string; badge: string; button: string }> = {
    emerald: { border: "border-emerald-500/30", bg: "bg-emerald-500/5 hover:bg-emerald-500/10", text: "text-emerald-400", badge: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400", button: "bg-emerald-500/10 hover:bg-emerald-500/20 border-emerald-500/30 text-emerald-300" },
    cyan: { border: "border-cyan-500/30", bg: "bg-cyan-500/5 hover:bg-cyan-500/10", text: "text-cyan-400", badge: "bg-cyan-500/10 border-cyan-500/30 text-cyan-400", button: "bg-cyan-500/10 hover:bg-cyan-500/20 border-cyan-500/30 text-cyan-300" },
    purple: { border: "border-purple-500/30", bg: "bg-purple-500/5 hover:bg-purple-500/10", text: "text-purple-400", badge: "bg-purple-500/10 border-purple-500/30 text-purple-400", button: "bg-purple-500/10 hover:bg-purple-500/20 border-purple-500/30 text-purple-300" },
    orange: { border: "border-orange-500/30", bg: "bg-orange-500/5 hover:bg-orange-500/10", text: "text-orange-400", badge: "bg-orange-500/10 border-orange-500/30 text-orange-400", button: "bg-orange-500/10 hover:bg-orange-500/20 border-orange-500/30 text-orange-300" },
    blue: { border: "border-blue-500/30", bg: "bg-blue-500/5 hover:bg-blue-500/10", text: "text-blue-400", badge: "bg-blue-500/10 border-blue-500/30 text-blue-400", button: "bg-blue-500/10 hover:bg-blue-500/20 border-blue-500/30 text-blue-300" },
    rose: { border: "border-rose-500/30", bg: "bg-rose-500/5 hover:bg-rose-500/10", text: "text-rose-400", badge: "bg-rose-500/10 border-rose-500/30 text-rose-400", button: "bg-rose-500/10 hover:bg-rose-500/20 border-rose-500/30 text-rose-300" },
};

const RECENT_ACTIVITY = [
    { time: "11:52:14", event: "STR profile EVID-2026-901 analyzed", lr: "Log10(LR) = +18.4", status: "MATCH", color: "emerald" },
    { time: "11:51:33", event: "HIrisPlex-S phenotype report compiled", lr: "Blue eyes, 92.1% conf.", status: "COMPLETE", color: "purple" },
    { time: "11:49:07", event: "3-person mixture deconvolved via MCMC", lr: "Contributor A: LR +6.2", status: "REVIEW", color: "amber" },
    { time: "11:44:28", event: "ISO 17025 court report generated", lr: "HMAC: a7f9c21…e04b", status: "SIGNED", color: "blue" },
    { time: "11:39:55", event: "Horvath epigenetic clock: Age 38±3.4 yr", lr: "Methylation sites: 353", status: "COMPLETE", color: "rose" },
];

export default function ForenzaDashboardPage() {
    const [hoveredCard, setHoveredCard] = useState<string | null>(null);

    return (
        <div className="space-y-6 font-mono">
            {/* ── Page Header ── */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">FORENZA Evidence OS</span>
                    </div>
                    <h1 className="text-base font-extrabold text-white tracking-tight">Operations Command Center</h1>
                    <p className="text-[10px] text-zinc-500 mt-0.5">FORENZA OS • 30 Biocomputational Subsystems • ISO/IEC 17025:2017</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                    <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/5 text-[9px] font-bold text-emerald-400 uppercase">
                        <Radio className="w-3 h-3 animate-pulse" />
                        Live • CASE-2026-FORENZA
                    </span>
                </div>
            </div>

            {/* ── Active Case DNA Profile & Live GIS Map Banner ── */}
            <ActiveProfileBanner />

            {/* ── Live Metrics Strip ── */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                {LIVE_METRICS.map((m, i) => {
                    const Icon = m.icon;
                    return (
                        <motion.div
                            key={m.label}
                            initial={{ opacity: 0, y: 8 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.04 }}
                            className="rounded-xl border border-tactical-border/60 bg-black/40 p-3 space-y-1.5"
                        >
                            <div className="flex items-center justify-between">
                                <Icon className={`w-3.5 h-3.5 ${m.color}`} />
                                <span className="text-[8px] font-bold text-zinc-600 bg-zinc-800/60 px-1.5 py-0.5 rounded">{m.trend}</span>
                            </div>
                            <p className={`text-sm font-extrabold ${m.color} leading-none`}>{m.value}</p>
                            <p className="text-[9px] text-zinc-500 leading-tight">{m.label}</p>
                        </motion.div>
                    );
                })}
            </div>

            {/* ── Module Category Cards ── */}
            <div>
                <div className="flex items-center gap-2 mb-3">
                    <Layers className="w-3.5 h-3.5 text-zinc-400" />
                    <h2 className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Biocomputational Subsystem Categories</h2>
                    <span className="text-[9px] text-zinc-600 border border-zinc-800 rounded px-2 py-0.5">30 Modules • 6 Categories</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {MODULE_CARDS.map((card, i) => {
                        const Icon = card.icon;
                        const c = COLOR_MAP[card.color];
                        return (
                            <motion.div
                                key={card.id}
                                initial={{ opacity: 0, y: 12 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 + i * 0.06 }}
                                onMouseEnter={() => setHoveredCard(card.id)}
                                onMouseLeave={() => setHoveredCard(null)}
                                className={`rounded-2xl border ${c.border} ${c.bg} p-5 flex flex-col gap-4 transition-all duration-200 cursor-pointer`}
                            >
                                {/* Card Header */}
                                <div className="space-y-2">
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex items-center gap-2.5 min-w-0">
                                            <div className={`p-2 rounded-xl border ${c.border} bg-black/40 shrink-0`}>
                                                <Icon className={`w-4 h-4 ${c.text}`} />
                                            </div>
                                            <h3 className="text-xs sm:text-sm font-extrabold text-white leading-tight break-words">
                                                {card.title}
                                            </h3>
                                        </div>
                                        <div className="flex flex-col sm:flex-row items-end sm:items-center gap-1 shrink-0">
                                            <span className={`text-[8px] font-bold border rounded px-1.5 py-0.5 ${c.badge}`}>{card.badge}</span>
                                            <span className="text-[8px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded px-1.5 py-0.5">{card.status}</span>
                                        </div>
                                    </div>

                                    {/* Subtitle Tags (Responsive Wrap - No Truncation) */}
                                    <div className="flex flex-wrap gap-1 pt-0.5">
                                        {card.subtitle.split(' • ').map((tag) => (
                                            <span key={tag} className="text-[8px] sm:text-[9px] font-mono font-medium text-zinc-300 bg-black/40 border border-tactical-border/50 rounded-md px-1.5 py-0.5">
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {/* Description */}
                                <p className="text-[10px] text-zinc-500 leading-relaxed flex-1">{card.description}</p>

                                {/* Mini Metrics */}
                                <div className="grid grid-cols-2 gap-2">
                                    {card.metrics.map((m) => (
                                        <div key={m.label} className="p-2 rounded-lg bg-black/30 border border-tactical-border/40">
                                            <span className="text-[8px] text-zinc-600 block">{m.label}</span>
                                            <span className={`text-[11px] font-bold ${c.text}`}>{m.value}</span>
                                        </div>
                                    ))}
                                </div>

                                {/* CTA */}
                                <Link
                                    href={card.href}
                                    className={`flex items-center justify-between px-3 py-2 rounded-xl border font-bold text-[10px] uppercase tracking-wider transition-all ${c.button}`}
                                >
                                    <span>Open {card.modules} Modules</span>
                                    <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                                </Link>
                            </motion.div>
                        );
                    })}
                </div>
            </div>

            {/* ── Recent Activity ── */}
            <div>
                <div className="flex items-center gap-2 mb-3">
                    <Activity className="w-3.5 h-3.5 text-zinc-400" />
                    <h2 className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">Recent Pipeline Activity</h2>
                </div>
                <div className="rounded-2xl border border-tactical-border/60 bg-black/30 overflow-hidden">
                    <div className="hidden sm:grid grid-cols-12 px-4 py-2 border-b border-tactical-border/40 text-[8px] font-bold text-zinc-600 uppercase tracking-wider">
                        <span className="col-span-2">Time</span>
                        <span className="col-span-6">Event</span>
                        <span className="col-span-3">Result</span>
                        <span className="col-span-1 text-right">Status</span>
                    </div>
                    {RECENT_ACTIVITY.map((a, i) => {
                        const statusColors: Record<string, string> = {
                            emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
                            purple: "text-purple-400 bg-purple-500/10 border-purple-500/20",
                            amber: "text-amber-400 bg-amber-500/10 border-amber-500/20",
                            blue: "text-blue-400 bg-blue-500/10 border-blue-500/20",
                            rose: "text-rose-400 bg-rose-500/10 border-rose-500/20",
                        };
                        return (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 0.4 + i * 0.04 }}
                                className="grid grid-cols-1 sm:grid-cols-12 items-center gap-1 sm:gap-0 px-4 py-3 border-b border-tactical-border/20 last:border-0 hover:bg-white/2 transition-colors"
                            >
                                <span className="col-span-2 text-[9px] text-zinc-600 font-mono">{a.time}</span>
                                <span className="col-span-6 text-[10px] text-zinc-300 font-medium">{a.event}</span>
                                <span className="col-span-3 text-[9px] text-zinc-500 font-mono">{a.lr}</span>
                                <div className="col-span-1 flex justify-end">
                                    <span className={`text-[8px] font-bold border rounded px-1.5 py-0.5 ${statusColors[a.color]}`}>{a.status}</span>
                                </div>
                            </motion.div>
                        );
                    })}
                </div>
            </div>

            {/* ── HMAC Chain of Custody ── */}
            <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-3.5 sm:p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 sm:gap-3 max-w-full overflow-hidden">
                <div className="flex items-center gap-2 shrink-0">
                    <Lock className="w-4 h-4 text-amber-400 shrink-0" />
                    <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">Chain of Custody</span>
                </div>
                <div className="flex-1 min-w-0 max-w-full">
                    <p className="text-[9px] sm:text-[10px] text-zinc-400 font-mono leading-relaxed break-all sm:break-normal">
                        HMAC-SHA256: <span className="text-amber-300 font-bold">a7f9c21e…e04b</span> →
                        Block #1847291 → Polygon zkEVM →
                        <span className="text-emerald-400 font-bold"> VERIFIED ✓</span>
                    </p>
                </div>
                <Link href="/audit" className="shrink-0 text-[9px] sm:text-[10px] font-bold text-amber-400 hover:text-amber-300 border border-amber-500/30 rounded-lg px-2.5 py-1.5 transition-colors uppercase tracking-wider whitespace-nowrap">
                    View ISO Audit Log →
                </Link>
            </div>
        </div>
    );
}
