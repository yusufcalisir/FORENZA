"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    ScanFace,
    Download,
    Loader2,
    Dna,
    Eye,
    Palette,
    User,
    Globe,
    RefreshCw,
    ChevronRight,
    AlertTriangle,
    CheckCircle2,
} from "lucide-react";
import { toPng } from "html-to-image";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

interface TraitSummary {
    [key: string]: string;
}

interface ReconstructionData {
    profile_id: string;
    image_url?: string;
    seed?: number;
    prompt_hash?: string;
    generation_time_ms?: number;
    model_id?: string;
    trait_summary?: TraitSummary;
    positive_prompt?: string;
    negative_prompt?: string;
    coherence_score?: number;
    coherence_status?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// MOCK DATA (Mirrors backend test-profile-eu response)
// ═══════════════════════════════════════════════════════════════════════════════

const MOCK_RECONSTRUCTION: ReconstructionData = {
    profile_id: "test-profile-eu",
    image_url: "https://randomuser.me/api/portraits/men/42.jpg", // Stable mock placeholder for offline mode
    seed: 1847293650,
    prompt_hash: "a3f2c1b8e9d4",
    generation_time_ms: 142.7,
    model_id: "mock-sdxl-dev",
    trait_summary: {
        "Eye Color": "Blue (85%)",
        "Hair Color": "Blond (42%)",
        "Skin Tone": "Light (78%)",
        "Ancestry": "European (65%)",
        "Sex": "Male",
    },
    positive_prompt:
        "((adult male portrait)), single person, ((European facial morphology, moderate brow ridge, narrow nasal bridge, defined cheekbones, medium lip volume, angular jawline)), ((piercing ice-blue eyes, light iris with limbal ring)), (light blond hair, natural golden tones, straight texture), (light skin tone, subtle warm undertones, Type II-III Fitzpatrick)",
    negative_prompt:
        "cartoon, anime, illustration, painting, drawing, sketch...",
};

// ═══════════════════════════════════════════════════════════════════════════════
// TRAIT ICON MAPPING
// ═══════════════════════════════════════════════════════════════════════════════

const TRAIT_ICONS: Record<string, typeof Eye> = {
    "Eye Color": Eye,
    "Hair Color": Palette,
    "Skin Tone": User,
    "Ancestry": Globe,
    "Sex": User,
};

// ═══════════════════════════════════════════════════════════════════════════════
// FORENSIC OVERLAY GRID SVG
// ═══════════════════════════════════════════════════════════════════════════════

function ForensicOverlay({ active }: { active: boolean }) {
    return (
        <svg
            className={`absolute inset-0 w-full h-full pointer-events-none transition-opacity duration-700 ${active ? "opacity-40" : "opacity-0"}`}
            viewBox="0 0 400 560"
            preserveAspectRatio="none"
        >
            {/* Horizontal grid lines */}
            {Array.from({ length: 12 }, (_, i) => (
                <line
                    key={`h-${i}`}
                    x1="0"
                    y1={i * 48 + 20}
                    x2="400"
                    y2={i * 48 + 20}
                    stroke="#22C55E"
                    strokeWidth="0.5"
                    strokeDasharray="4 8"
                    opacity="0.3"
                />
            ))}
            {/* Vertical grid lines */}
            {Array.from({ length: 8 }, (_, i) => (
                <line
                    key={`v-${i}`}
                    x1={i * 52 + 20}
                    y1="0"
                    x2={i * 52 + 20}
                    y2="560"
                    stroke="#22C55E"
                    strokeWidth="0.5"
                    strokeDasharray="4 8"
                    opacity="0.3"
                />
            ))}
            {/* Center crosshair */}
            <line x1="180" y1="200" x2="220" y2="200" stroke="#22C55E" strokeWidth="1" opacity="0.6" />
            <line x1="200" y1="180" x2="200" y2="220" stroke="#22C55E" strokeWidth="1" opacity="0.6" />
            <circle cx="200" cy="200" r="60" fill="none" stroke="#22C55E" strokeWidth="0.5" strokeDasharray="3 6" opacity="0.3" />
            <circle cx="200" cy="200" r="120" fill="none" stroke="#22C55E" strokeWidth="0.5" strokeDasharray="3 6" opacity="0.2" />

            {/* Trait labels on overlay */}
            <text x="30" y="155" fill="#22C55E" fontSize="8" fontFamily="JetBrains Mono, monospace" opacity="0.7">IRIS_SCAN</text>
            <line x1="30" y1="158" x2="130" y2="200" stroke="#22C55E" strokeWidth="0.5" opacity="0.4" />

            <text x="280" y="120" fill="#22C55E" fontSize="8" fontFamily="JetBrains Mono, monospace" opacity="0.7">CRANIAL_STRUCT</text>
            <line x1="280" y1="123" x2="250" y2="165" stroke="#22C55E" strokeWidth="0.5" opacity="0.4" />

            <text x="290" y="280" fill="#22C55E" fontSize="8" fontFamily="JetBrains Mono, monospace" opacity="0.7">JAW_MORPH</text>
            <line x1="290" y1="275" x2="260" y2="310" stroke="#22C55E" strokeWidth="0.5" opacity="0.4" />

            <text x="20" y="310" fill="#22C55E" fontSize="8" fontFamily="JetBrains Mono, monospace" opacity="0.7">PIGMENT_IDX</text>
            <line x1="20" y1="305" x2="130" y2="250" stroke="#22C55E" strokeWidth="0.5" opacity="0.4" />

            {/* Corner brackets */}
            <path d="M10 10 L10 30 M10 10 L30 10" stroke="#22C55E" strokeWidth="1.5" fill="none" opacity="0.6" />
            <path d="M390 10 L390 30 M390 10 L370 10" stroke="#22C55E" strokeWidth="1.5" fill="none" opacity="0.6" />
            <path d="M10 550 L10 530 M10 550 L30 550" stroke="#22C55E" strokeWidth="1.5" fill="none" opacity="0.6" />
            <path d="M390 550 L390 530 M390 550 L370 550" stroke="#22C55E" strokeWidth="1.5" fill="none" opacity="0.6" />
        </svg>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCANNING ANIMATION
// ═══════════════════════════════════════════════════════════════════════════════

function ScanBeam({ active }: { active: boolean }) {
    if (!active) return null;
    return (
        <motion.div
            className="absolute left-0 right-0 h-[2px] z-20 pointer-events-none"
            style={{
                background: "linear-gradient(90deg, transparent, #22C55E, transparent)",
                boxShadow: "0 0 20px 4px rgba(34, 197, 94, 0.3)",
            }}
            animate={{ top: ["0%", "100%", "0%"] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        />
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// FORENSIC PLACEHOLDER (when no real image)
// ═══════════════════════════════════════════════════════════════════════════════

function ForensicPlaceholder() {
    return (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-tactical-surface via-[#0d0d10] to-tactical-surface">
            <svg viewBox="0 0 200 280" className="w-48 h-auto opacity-20">
                {/* Head outline */}
                <ellipse cx="100" cy="95" rx="60" ry="75" fill="none" stroke="#22C55E" strokeWidth="1" />
                {/* Eyes */}
                <ellipse cx="78" cy="85" rx="12" ry="6" fill="none" stroke="#22C55E" strokeWidth="0.8" />
                <ellipse cx="122" cy="85" rx="12" ry="6" fill="none" stroke="#22C55E" strokeWidth="0.8" />
                <circle cx="78" cy="85" r="3" fill="#22C55E" opacity="0.5" />
                <circle cx="122" cy="85" r="3" fill="#22C55E" opacity="0.5" />
                {/* Nose */}
                <path d="M100 92 L95 115 L105 115 Z" fill="none" stroke="#22C55E" strokeWidth="0.8" />
                {/* Mouth */}
                <path d="M85 130 Q100 140 115 130" fill="none" stroke="#22C55E" strokeWidth="0.8" />
                {/* Neck */}
                <line x1="85" y1="165" x2="85" y2="200" stroke="#22C55E" strokeWidth="0.8" />
                <line x1="115" y1="165" x2="115" y2="200" stroke="#22C55E" strokeWidth="0.8" />
                {/* Shoulders */}
                <path d="M85 200 Q50 210 30 240" fill="none" stroke="#22C55E" strokeWidth="0.8" />
                <path d="M115 200 Q150 210 170 240" fill="none" stroke="#22C55E" strokeWidth="0.8" />
                {/* Measurement lines */}
                <line x1="30" y1="20" x2="30" y2="170" stroke="#22C55E" strokeWidth="0.3" strokeDasharray="2 4" />
                <line x1="170" y1="20" x2="170" y2="170" stroke="#22C55E" strokeWidth="0.3" strokeDasharray="2 4" />
                <text x="100" y="270" fill="#22C55E" fontSize="7" fontFamily="JetBrains Mono, monospace" textAnchor="middle" opacity="0.6">AWAITING_GENAI_RENDER</text>
            </svg>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// GENERATION LOG LINE
// ═══════════════════════════════════════════════════════════════════════════════

const LOG_STEPS = [
    { msg: "Fetching SNP genotype data...", icon: Dna, delay: 0 },
    { msg: "Running HIrisPlex-S predictor...", icon: ScanFace, delay: 400 },
    { msg: "Composing SDXL prompt tokens...", icon: Palette, delay: 800 },
    { msg: "Generating facial reconstruction...", icon: RefreshCw, delay: 1200 },
    { msg: "Applying forensic overlay...", icon: CheckCircle2, delay: 1600 },
];

function GenerationLog({ isGenerating }: { isGenerating: boolean }) {
    const [visibleSteps, setVisibleSteps] = useState(0);

    useEffect(() => {
        if (!isGenerating) {
            setVisibleSteps(0);
            return;
        }
        const timers: NodeJS.Timeout[] = [];
        LOG_STEPS.forEach((step, idx) => {
            timers.push(setTimeout(() => setVisibleSteps(idx + 1), step.delay));
        });
        return () => timers.forEach(clearTimeout);
    }, [isGenerating]);

    if (!isGenerating) return null;

    return (
        <div className="space-y-1 min-h-[80px]">
            <AnimatePresence>
                {LOG_STEPS.slice(0, visibleSteps).map((step, idx) => {
                    const Icon = step.icon;
                    const isLast = idx === visibleSteps - 1;
                    return (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -8 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0 }}
                            className="flex items-center gap-2"
                        >
                            {isLast && isGenerating ? (
                                <Loader2 className="w-3 h-3 text-tactical-primary animate-spin" />
                            ) : (
                                <Icon className="w-3 h-3 text-tactical-primary" />
                            )}
                            <span className="font-mono text-[9px] text-zinc-500 tracking-wide">
                                {step.msg}
                            </span>
                            {!isLast && (
                                <CheckCircle2 className="w-2.5 h-2.5 text-tactical-primary/50 ml-auto" />
                            )}
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

interface ForensicIdentityCardProps {
    profileId?: string;
    hoveredRegion?: string | null;
    phenotypeReport?: {
        traits?: Record<string, string>;
        trait_sources?: Record<string, string[]>;
        reliability_score?: number;
        coherence_score?: number;
        coherence_status?: string;
        snps_analyzed?: string[];
    } | null;
    coherenceScore?: number;
    txHash?: string;
    ancestryRegion?: string;
    isLoading?: boolean;
    hideIfEmpty?: boolean;
}

export default function SuspectVisualizer({
    profileId,
    hoveredRegion,
    phenotypeReport,
    coherenceScore,
    txHash,
    ancestryRegion,
    isLoading: externalLoading,
    hideIfEmpty = false
}: ForensicIdentityCardProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [activeView, setActiveView] = useState<"overview" | "morphometrics" | "hair_balding">("overview");
    const [morphoSnps, setMorphoSnps] = useState<Record<string, number>>({
        rs974448: 2,
        rs12882923: 1,
        rs11130635: 2,
        rs13289: 0,
        rs7559252: 2,
    });
    const [hairSnps, setHairSnps] = useState<Record<string, number>>({
        rs3827072: 2,
        rs11803731: 0,
        rs7349332: 0,
        rs6152: 1,
        rs2180439: 1,
        rs1160312: 0,
        rs756853: 1,
    });

    const data = phenotypeReport;
    // Allow external control of loading state, fallback to heuristic if not provided
    const isLoading = externalLoading ?? (!data && !!profileId);

    // Safety check specific to phenotype data availability
    const hasData = data && data.traits && Object.keys(data.traits).length > 0;

    // If configured to hide when empty, and we are not loading and have no data, return null
    if (hideIfEmpty && !isLoading && !hasData) {
        return null;
    }

    // Reliability formatting and color logic
    const reliabilityValue = coherenceScore ? (coherenceScore * 100).toFixed(1) : "0.0";
    const reliabilityColor = coherenceScore
        ? coherenceScore > 0.8 ? "text-emerald-500"
            : coherenceScore > 0.6 ? "text-amber-500"
                : "text-red-500"
        : "text-zinc-500";
    const reliabilityLabel = coherenceScore ? `${reliabilityValue}%` : "CALCULATING...";

    // Helper: Determine if trait matches hovered region
    const isTraitRelevant = (trait: string, value: string) => {
        if (!hoveredRegion) return false;
        const region = hoveredRegion.toLowerCase();
        const val = value.toLowerCase();

        if (region.includes("africa")) return (val.includes("dark") || val.includes("black") || val.includes("curly"));
        if (region.includes("europe")) return (val.includes("blue") || val.includes("light") || val.includes("blond"));
        if (region.includes("asia")) return (val.includes("dark") || val.includes("straight"));
        return false;
    };

    // Mapping backend traits to requested display labels
    const displayTraits = [
        {
            label: "BIOLOGICAL_EYE_COLOR",
            value: data?.traits?.["Ocular Pigmentation"] || "Blue (P=0.85, U95=±0.07)",
            key: "Ocular Pigmentation"
        },
        {
            label: "DERMAL_PIGMENTATION",
            value: data?.traits?.["Dermal Classification"] || "Pale (P=0.70, U95=±0.09)",
            key: "Dermal Classification"
        },
        {
            label: "HAIR_STRUCTURE",
            value: data?.traits?.["Hair Morphology"] || "Blond / Straight (P=0.75)",
            key: "Hair Morphology"
        },
        {
            label: "EPHELIDES_FRECKLING_RISK",
            value: data?.traits?.["Freckling Risk"] || "High Risk (P=0.85, U95=±0.07)",
            key: "Freckling Risk"
        },
        {
            label: "ESTIMATED_CHRONOLOGICAL_AGE",
            value: data?.traits?.["Estimated Age"] || "31.2 Years [95% CI: 24.8 - 37.6]",
            key: "Estimated Age"
        },
        {
            label: "GENETIC_ANCESTRY_KEY",
            value: ancestryRegion || "Northern / Western European (P=0.92)",
            key: "Ancestry"
        }
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="rounded-lg border border-tactical-border bg-slate-950 overflow-hidden h-fit flex flex-col font-mono shadow-lg relative"
            ref={containerRef}
        >
            {/* ── Scanning Overlay Animation ── */}
            {isLoading && (
                <div className="absolute inset-0 z-20 pointer-events-none overflow-hidden">
                    <motion.div
                        className="w-full h-[2px] bg-cyan-400/80 shadow-[0_0_15px_rgba(34,211,238,0.8)]"
                        animate={{ top: ["0%", "100%", "0%"] }}
                        transition={{ duration: 3, ease: "linear", repeat: Infinity }}
                    />
                    <div className="absolute inset-0 bg-cyan-500/5 mix-blend-overlay" />
                </div>
            )}

            {/* ── Header ── */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800/50 shrink-0 bg-[#070709] relative z-10">
                <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-emerald-500" />
                    <h3 className="font-mono text-[10px] font-bold tracking-[0.2em] text-emerald-500 uppercase">
                        Forensic_Identity_Panel
                    </h3>
                </div>

                {hasData && (
                    <div className={`flex items-center gap-2 px-2 py-1 rounded-full border ${(coherenceScore || 0) > 0.85
                        ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                        : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                        }`}>
                        {(coherenceScore || 0) > 0.85 ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                        <span className="font-mono text-[8px] font-bold tracking-tighter uppercase whitespace-nowrap">
                            {(coherenceScore || 0) > 0.85 ? "VERIFIED" : "LOW SYNC"}
                        </span>
                    </div>
                )}
            </div>

            {/* ── Content Area ── */}
            <div className="flex-1 p-4 bg-slate-950 relative overflow-hidden flex flex-col">
                <div
                    className="absolute inset-0 opacity-10 pointer-events-none"
                    style={{
                        backgroundImage: `linear-gradient(#10B981 1px, transparent 1px), linear-gradient(90deg, #10B981 1px, transparent 1px)`,
                        backgroundSize: '30px 30px',
                    }}
                />

                {!hasData && !isLoading ? (
                    <div className="flex-1 flex flex-col items-center justify-center space-y-6 py-10 opacity-80">
                        {/* Empty State Illustration */}
                        <div className="relative w-32 h-32 opacity-50">
                            <div className="absolute inset-0 border border-zinc-800 rounded-full animate-pulse" />
                            <div className="absolute inset-4 border border-dashed border-zinc-700 rounded-full animate-[spin_10s_linear_infinite]" />
                            <div className="absolute inset-0 flex items-center justify-center">
                                <Dna className="w-12 h-12 text-zinc-700" />
                            </div>
                            {/* Cross lines */}
                            <div className="absolute top-1/2 left-0 w-full h-[1px] bg-zinc-800/50" />
                            <div className="absolute left-1/2 top-0 h-full w-[1px] bg-zinc-800/50" />
                        </div>

                        <div className="text-center space-y-2 max-w-[200px]">
                            <p className="font-mono text-[10px] text-zinc-400 tracking-[0.2em] uppercase font-bold">
                                AWAITING DNA SEQUENCE
                            </p>
                            <p className="font-mono text-[8px] text-zinc-600 leading-relaxed">
                                Upload a valid .fsa file or manually enter at least 13 STR loci to generate a forensic profile.
                            </p>
                        </div>
                    </div>
                ) : !hasData && isLoading ? (
                    <div className="flex-1 flex flex-col items-center justify-center space-y-3 py-10 opacity-60">
                        <div className="space-y-1 text-center">
                            <p className="font-mono text-[10px] text-cyan-400 tracking-[0.2em] uppercase animate-pulse">
                                ANALYZING PHENOTYPE...
                            </p>
                            <p className="font-mono text-[8px] text-zinc-500">
                                Constructing Forensic Profile
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 flex flex-col gap-5 relative z-10 animate-in fade-in duration-500">
                        {/* Summary Header */}
                        <div className="grid grid-cols-2 gap-4 pb-4 border-b border-zinc-900">
                            <div>
                                <p className="font-mono text-[7px] text-zinc-500 uppercase tracking-widest mb-1">Subject_Reference</p>
                                <p className="font-mono text-xs font-bold text-white truncate">{profileId}</p>
                            </div>
                            <div className="text-right">
                                <p className="font-mono text-[7px] text-zinc-500 uppercase tracking-widest mb-1">Reliability_Index</p>
                                <p className={`font-mono text-xs font-bold ${reliabilityColor}`}>
                                    {reliabilityLabel}
                                </p>
                            </div>
                        </div>

                        {/* Tab Selector */}
                        <div className="flex items-center gap-1 p-1 bg-black/40 rounded border border-tactical-border/50">
                            <button
                                onClick={() => setActiveView("overview")}
                                className={`flex-1 py-1 px-1.5 rounded text-[7.5px] font-mono font-bold uppercase transition-all ${
                                    activeView === "overview"
                                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                        : "text-zinc-500 hover:text-zinc-300"
                                }`}
                            >
                                Overview
                            </button>
                            <button
                                onClick={() => setActiveView("morphometrics")}
                                className={`flex-1 py-1 px-1.5 rounded text-[7.5px] font-mono font-bold uppercase transition-all ${
                                    activeView === "morphometrics"
                                        ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                                        : "text-zinc-500 hover:text-zinc-300"
                                }`}
                            >
                                3D Ceph (P3 §3)
                            </button>
                            <button
                                onClick={() => setActiveView("hair_balding")}
                                className={`flex-1 py-1 px-1.5 rounded text-[7.5px] font-mono font-bold uppercase transition-all ${
                                    activeView === "hair_balding"
                                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                                        : "text-zinc-500 hover:text-zinc-300"
                                }`}
                            >
                                Hair &amp; Balding (P3 §4)
                            </button>
                        </div>

                        {activeView === "overview" ? (
                            /* High-Fidelity Grid */
                            <div className="grid grid-cols-1 gap-3">
                                {displayTraits.map((trait) => {
                                    const highlight = isTraitRelevant(trait.key, trait.value);
                                    const sources = data?.trait_sources?.[trait.key] || [];

                                    return (
                                        <div
                                            key={trait.label}
                                            className={`relative group p-3 rounded bg-zinc-900/40 border transition-all duration-300 ${highlight
                                                ? "border-emerald-500/40 bg-emerald-500/5 shadow-[0_0_10px_rgba(16,185,129,0.1)]"
                                                : "border-zinc-800 hover:border-zinc-700"
                                                }`}
                                        >
                                            <div className="flex items-center justify-between mb-2">
                                                <span className={`font-mono text-[8px] uppercase tracking-[0.15em] ${highlight ? 'text-emerald-400 font-bold' : 'text-zinc-500'}`}>
                                                    {trait.label}
                                                </span>
                                                {highlight && (
                                                    <div className="flex items-center gap-1">
                                                        <div className="w-1 h-1 bg-emerald-500 animate-pulse" />
                                                        <span className="font-mono text-[7px] text-emerald-500 max-[280px]:hidden">MATCH</span>
                                                    </div>
                                                )}
                                            </div>
                                            <div className="flex justify-between items-end">
                                                <div className={`font-mono text-sm ${highlight ? 'text-white font-bold' : 'text-zinc-300'}`}>
                                                    {trait.value}
                                                </div>
                                                {/* Source Tag */}
                                                {sources.length > 0 && (
                                                    <div className="font-mono text-[8px] text-zinc-600 text-right">
                                                        Ref: {sources.map(s => s.split(' ')[0]).join(', ')}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : activeView === "morphometrics" ? (
                            /* 3D Craniofacial Morphometrics Tab (Module 13) */
                            <div className="space-y-3">
                                {/* Facial Index & Typology Badge */}
                                <div className="p-2.5 rounded bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-between">
                                    <div>
                                        <div className="font-mono text-[7px] text-zinc-400 uppercase">Facial Index (I_F)</div>
                                        <div className="font-mono text-xs font-bold text-cyan-300">
                                            {((Math.sqrt(Math.pow((12.4 + 1.25 * (morphoSnps.rs974448 || 0)) - (18.2 + 1.85 * (morphoSnps.rs7559252 || 0)), 2) + Math.pow((45.2 + 0.85 * (morphoSnps.rs974448 || 0)) - (-68.5 - 1.20 * (morphoSnps.rs7559252 || 0)), 2)) / (2 * (18.5 + 0.95 * (morphoSnps.rs12882923 || 0)))) * 100).toFixed(1)}
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-mono text-[7px] text-zinc-400 uppercase">Typology</div>
                                        <span className="font-mono text-[8px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold">
                                            MESOPROSOPIC
                                        </span>
                                    </div>
                                </div>

                                {/* 7 Landmarks Matrix */}
                                <div className="space-y-1.5">
                                    <div className="font-mono text-[8px] text-zinc-400 uppercase tracking-wider">
                                        Cephalometric Coordinates (mm)
                                    </div>
                                    <div className="grid grid-cols-2 gap-1.5 text-[8px] font-mono">
                                        <div className="p-1.5 rounded bg-black/40 border border-zinc-800 flex justify-between">
                                            <span className="text-zinc-400">Nasion (N):</span>
                                            <span className="text-cyan-300 font-bold">0.0, {(12.4 + 1.25 * (morphoSnps.rs974448 || 0)).toFixed(1)}, {(45.2 + 0.85 * (morphoSnps.rs974448 || 0)).toFixed(1)}</span>
                                        </div>
                                        <div className="p-1.5 rounded bg-black/40 border border-zinc-800 flex justify-between">
                                            <span className="text-zinc-400">Pronasale (Prn):</span>
                                            <span className="text-emerald-300 font-bold">0.0, {(48.5 + 2.10 * (morphoSnps.rs11130635 || 0) - 1.45 * (morphoSnps.rs13289 || 0)).toFixed(1)}, {(12.1 + 1.15 * (morphoSnps.rs11130635 || 0)).toFixed(1)}</span>
                                        </div>
                                        <div className="p-1.5 rounded bg-black/40 border border-zinc-800 flex justify-between">
                                            <span className="text-zinc-400">Subnasale (Sn):</span>
                                            <span className="text-zinc-300 font-bold">0.0, {(38.2 - 1.10 * (morphoSnps.rs13289 || 0)).toFixed(1)}, {(-2.5 - 0.65 * (morphoSnps.rs13289 || 0)).toFixed(1)}</span>
                                        </div>
                                        <div className="p-1.5 rounded bg-black/40 border border-zinc-800 flex justify-between">
                                            <span className="text-zinc-400">Alar Width:</span>
                                            <span className="text-pink-300 font-bold">{(2 * (18.5 + 0.95 * (morphoSnps.rs12882923 || 0))).toFixed(1)} mm</span>
                                        </div>
                                        <div className="p-1.5 rounded bg-black/40 border border-zinc-800 flex justify-between">
                                            <span className="text-zinc-400">Labiale Sup (Ls):</span>
                                            <span className="text-zinc-300 font-bold">0.0, {(34.5 + 0.60 * (morphoSnps.rs7559252 || 0)).toFixed(1)}, {(-12.4 - 0.40 * (morphoSnps.rs7559252 || 0)).toFixed(1)}</span>
                                        </div>
                                        <div className="p-1.5 rounded bg-black/40 border border-zinc-800 flex justify-between">
                                            <span className="text-zinc-400">Menton (Me):</span>
                                            <span className="text-amber-300 font-bold">0.0, {(18.2 + 1.85 * (morphoSnps.rs7559252 || 0)).toFixed(1)}, {(-68.5 - 1.20 * (morphoSnps.rs7559252 || 0)).toFixed(1)}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Morphometric SNP Dosage Toggles */}
                                <div className="space-y-1.5 pt-1">
                                    <div className="font-mono text-[8px] text-zinc-400 uppercase tracking-wider">
                                        Predictor Loci (Click to toggle dosage 0, 1, 2)
                                    </div>
                                    <div className="grid grid-cols-3 gap-1">
                                        {[
                                            { rs: "rs974448", gene: "PAX3" },
                                            { rs: "rs12882923", gene: "PAX9" },
                                            { rs: "rs11130635", gene: "PRDM16" },
                                            { rs: "rs13289", gene: "DCHS2" },
                                            { rs: "rs7559252", gene: "PCDH15" },
                                        ].map(({ rs, gene }) => {
                                            const d = morphoSnps[rs] || 0;
                                            return (
                                                <button
                                                    key={rs}
                                                    onClick={() => setMorphoSnps(p => ({ ...p, [rs]: ((p[rs] || 0) + 1) % 3 }))}
                                                    className="p-1 rounded bg-black/50 border border-zinc-800 hover:border-cyan-500/50 flex justify-between items-center text-[7px] font-mono"
                                                >
                                                    <span className="text-zinc-300 font-bold">{gene}</span>
                                                    <span className="px-1 py-0.2 rounded bg-cyan-500/20 text-cyan-300 font-bold">d={d}</span>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        ) : (
                            /* Hair Dynamics & Balding PRS Tab (Module 14) */
                            <div className="space-y-3">
                                {/* Fiber Cross-Section & Curl Index Summary */}
                                <div className="grid grid-cols-2 gap-2">
                                    <div className="p-2 rounded bg-amber-500/10 border border-amber-500/30">
                                        <div className="font-mono text-[7px] text-zinc-400 uppercase">Fiber Area</div>
                                        <div className="font-mono text-xs font-bold text-amber-300">
                                            {(3850.0 + 1420.0 * (hairSnps.rs3827072 || 0)).toFixed(0)} μm²
                                        </div>
                                        <div className="font-mono text-[7px] text-zinc-400">
                                            {(hairSnps.rs3827072 || 0) >= 2 ? "Thick Asian (EDAR)" : "Fine/Medium European"}
                                        </div>
                                    </div>
                                    <div className="p-2 rounded bg-purple-500/10 border border-purple-500/30">
                                        <div className="font-mono text-[7px] text-zinc-400 uppercase">Curl Index (C_curl)</div>
                                        <div className="font-mono text-xs font-bold text-purple-300">
                                            {Math.max(0, Math.min(10, 1.20 + 1.85 * (hairSnps.rs11803731 || 0) + 1.42 * (hairSnps.rs7349332 || 0) - 2.10 * (hairSnps.rs3827072 || 0))).toFixed(2)}
                                        </div>
                                        <div className="font-mono text-[7px] text-zinc-400">
                                            {Math.max(0, 1.20 + 1.85 * (hairSnps.rs11803731 || 0) + 1.42 * (hairSnps.rs7349332 || 0) - 2.10 * (hairSnps.rs3827072 || 0)) < 2 ? "STRAIGHT" : "WAVY / CURLY"}
                                        </div>
                                    </div>
                                </div>

                                {/* Androgenetic Alopecia Hamilton-Norwood Meter */}
                                <div className="p-2.5 rounded bg-black/40 border border-tactical-border/60 space-y-1.5">
                                    <div className="flex justify-between items-center text-[8px] font-mono">
                                        <span className="text-zinc-400">Balding PRS Score:</span>
                                        <span className="text-rose-400 font-bold">
                                            {(0.982 * (hairSnps.rs6152 || 0) + 0.541 * (hairSnps.rs2180439 || 0) + 0.485 * (hairSnps.rs1160312 || 0) + 0.362 * (hairSnps.rs756853 || 0)).toFixed(3)}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center text-[8px] font-mono">
                                        <span className="text-zinc-400">Hamilton-Norwood Scale:</span>
                                        <span className="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold">
                                            {(0.982 * (hairSnps.rs6152 || 0) + 0.541 * (hairSnps.rs2180439 || 0) + 0.485 * (hairSnps.rs1160312 || 0) + 0.362 * (hairSnps.rs756853 || 0)) < 0.50
                                                ? "GRADE I / II"
                                                : (0.982 * (hairSnps.rs6152 || 0) + 0.541 * (hairSnps.rs2180439 || 0) + 0.485 * (hairSnps.rs1160312 || 0) + 0.362 * (hairSnps.rs756853 || 0)) < 1.20
                                                ? "GRADE III"
                                                : (0.982 * (hairSnps.rs6152 || 0) + 0.541 * (hairSnps.rs2180439 || 0) + 0.485 * (hairSnps.rs1160312 || 0) + 0.362 * (hairSnps.rs756853 || 0)) < 2.10
                                                ? "GRADE IV / V"
                                                : "GRADE VI / VII"}
                                        </span>
                                    </div>
                                </div>

                                {/* Hair & Balding SNP Toggles */}
                                <div className="space-y-1.5 pt-1">
                                    <div className="font-mono text-[8px] text-zinc-400 uppercase tracking-wider">
                                        Hair &amp; Balding Loci (Click to toggle dosage)
                                    </div>
                                    <div className="grid grid-cols-4 gap-1">
                                        {[
                                            { rs: "rs3827072", gene: "EDAR" },
                                            { rs: "rs11803731", gene: "TCHH" },
                                            { rs: "rs7349332", gene: "WNT10" },
                                            { rs: "rs6152", gene: "AR" },
                                            { rs: "rs2180439", gene: "20p11" },
                                            { rs: "rs1160312", gene: "20p11b" },
                                            { rs: "rs756853", gene: "HDAC9" },
                                        ].map(({ rs, gene }) => {
                                            const d = hairSnps[rs] || 0;
                                            return (
                                                <button
                                                    key={rs}
                                                    onClick={() => setHairSnps(p => ({ ...p, [rs]: ((p[rs] || 0) + 1) % 3 }))}
                                                    className="p-1 rounded bg-black/50 border border-zinc-800 hover:border-amber-500/50 flex justify-between items-center text-[7px] font-mono"
                                                >
                                                    <span className="text-zinc-300 font-bold">{gene}</span>
                                                    <span className="px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 font-bold">d={d}</span>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        )}


                        {/* Footer Section with On-Chain Proof Button */}
                        <div className="mt-auto pt-4 border-t border-zinc-900 flex flex-col gap-3">
                            {txHash ? (
                                <a
                                    href={`https://sepolia.etherscan.io/tx/${txHash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="group flex items-center justify-center gap-2 w-full bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 hover:border-emerald-500/50 text-emerald-400 py-2.5 rounded transition-all active:scale-[0.98]"
                                >
                                    <CheckCircle2 className="w-3.5 h-3.5" />
                                    <span className="font-mono text-[9px] font-bold tracking-wider uppercase">
                                        View On-Chain Proof
                                    </span>
                                    <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                                </a>
                            ) : (
                                <div className="flex items-center justify-center gap-2 w-full bg-zinc-900/50 border border-zinc-800 border-dashed text-zinc-600 py-2.5 rounded cursor-not-allowed">
                                    <AlertTriangle className="w-3.5 h-3.5" />
                                    <span className="font-mono text-[9px] tracking-wider uppercase">
                                        Proof Not Finalized
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </motion.div>
    );
}

