"use client";

import { useState } from "react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import {
    Eye,
    Dna,
    ShieldCheck,
    Activity,
    Sliders,
    Sparkles,
    CheckCircle2,
    BarChart3,
    Terminal,
    Lock,
    Zap,
} from "lucide-react";

/* ── Types ── */
type TabId = "phenotype" | "str" | "zkp";

/* ═════════════════════════════════════════════════════════════════════════════
   1. PHENOTYPE PREDICTION TAB (Rich Biometric Trait Reconstruction)
   ═════════════════════════════════════════════════════════════════════════════ */
const EYE_COLORS_DATA = [
    {
        key: "blue" as const,
        color: "#38BDF8",
        glow: "rgba(56,189,248,0.3)",
        gene: "HERC2 rs12913832 (A/A)",
        prob: 94.2,
        secondary: "OCA2 rs1800407",
    },
    {
        key: "hazel" as const,
        color: "#D97706",
        glow: "rgba(217,119,6,0.3)",
        gene: "HERC2 / OCA2 Compound",
        prob: 78.4,
        secondary: "SLC45A2 rs16891982",
    },
    {
        key: "brown" as const,
        color: "#92400E",
        glow: "rgba(146,64,14,0.3)",
        gene: "HERC2 rs12913832 (G/G)",
        prob: 88.9,
        secondary: "TYR rs1042602",
    },
];

const SKIN_TYPES_DATA = [
    { type: "Type I", key: "vPale" as const, color: "#FDE68A", prob: 92 },
    { type: "Type II", key: "fair" as const, color: "#FCD34D", prob: 78 },
    { type: "Type III", key: "medium" as const, color: "#F59E0B", prob: 55 },
    { type: "Type IV", key: "olive" as const, color: "#D97706", prob: 36 },
    { type: "Type V", key: "dBrown" as const, color: "#92400E", prob: 20 },
    { type: "Type VI", key: "dBlack" as const, color: "#451A03", prob: 8 },
];

const HAIR_TYPES_DATA = [
    { key: "straight" as const, score: "88%", gene: "EDAR rs3827072 (T/T)" },
    { key: "wavy" as const, score: "12%", gene: "TCHH rs11803731" },
    { key: "curly" as const, score: "2%", gene: "WNT10A rs7349332" },
];

function PhenotypeTab() {
    const { t } = useSaasLanguage();
    const pTab = t.bioSimulator.phenotypeTab;

    const [selectedEye, setSelectedEye] = useState(0);
    const [selectedSkin, setSelectedSkin] = useState(0);
    const currentEye = EYE_COLORS_DATA[selectedEye];
    const currentSkin = SKIN_TYPES_DATA[selectedSkin];

    return (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 font-mono max-w-full overflow-hidden">
            {/* Left Col: Interactive Controls & Pigmentation Cards */}
            <div className="lg:col-span-7 space-y-3 sm:space-y-4">
                {/* Eye Pigmentation Panel */}
                <div className="rounded-xl border border-tactical-border bg-tactical-bg/70 p-3 sm:p-4 space-y-2.5 sm:space-y-3 shadow-md">
                    <div className="flex flex-wrap sm:flex-nowrap items-center justify-between gap-1.5 border-b border-tactical-border pb-2">
                        <div className="flex items-center gap-1.5 min-w-0">
                            <Eye className="h-4 w-4 text-[#38BDF8] shrink-0" />
                            <span className="font-mono text-[10px] sm:text-xs font-bold tracking-wider text-tactical-text uppercase leading-tight">
                                {pTab.irisTitle}
                            </span>
                        </div>
                        <span className="shrink-0 font-mono text-[8px] sm:text-[9px] tracking-widest text-[#22C55E] bg-[#22C55E]/10 border border-[#22C55E]/20 px-2 py-0.5 rounded-full font-bold">
                            {pTab.irisSub}
                        </span>
                    </div>

                    <div className="grid grid-cols-3 gap-1.5 sm:gap-2.5">
                        {EYE_COLORS_DATA.map((opt, i) => (
                            <button
                                key={opt.key}
                                onClick={() => setSelectedEye(i)}
                                className={`flex flex-col sm:flex-row items-center justify-center sm:justify-between gap-1 sm:gap-2 rounded-xl border p-1.5 sm:p-2.5 font-mono text-[10px] sm:text-xs transition-all duration-200 cursor-pointer ${
                                    selectedEye === i
                                        ? "border-[#38BDF8] bg-[#38BDF8]/10 text-white shadow-[0_0_15px_rgba(56,189,248,0.2)]"
                                        : "border-tactical-border bg-tactical-surface text-tactical-text-muted hover:border-tactical-border/80 hover:text-white"
                                }`}
                            >
                                <div className="flex items-center gap-1 min-w-0">
                                    <span
                                        className="h-2 w-2 sm:h-3 sm:w-3 rounded-full border border-white/30 shrink-0"
                                        style={{ background: opt.color, boxShadow: `0 0 8px ${opt.glow}` }}
                                    />
                                    <span className="font-semibold truncate">{pTab.eyeColors[opt.key]}</span>
                                </div>
                                <span className="text-[8px] sm:text-[10px] opacity-75 shrink-0">{opt.prob}%</span>
                            </button>
                        ))}
                    </div>

                    {/* Progress Bar & Details */}
                    <div className="rounded-lg border border-tactical-border bg-tactical-surface p-2.5 sm:p-3 space-y-1.5 sm:space-y-2">
                        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center text-[10px] sm:text-xs font-mono gap-0.5">
                            <span className="text-tactical-text-muted shrink-0">{pTab.targetGenotype}:</span>
                            <span className="font-bold text-[#38BDF8] break-all sm:truncate">{currentEye.gene}</span>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center text-[10px] sm:text-xs font-mono gap-0.5">
                            <span className="text-tactical-text-muted shrink-0">{pTab.secondaryMarker}:</span>
                            <span className="text-tactical-text break-all sm:truncate">{currentEye.secondary}</span>
                        </div>
                        <div className="space-y-1 pt-1 border-t border-tactical-border/60">
                            <div className="flex flex-col sm:flex-row sm:justify-between text-[9px] sm:text-[10px] font-mono gap-0.5">
                                <span className="text-tactical-text-dim">{pTab.posteriorProb}</span>
                                <span className="font-bold text-[#22C55E]">{currentEye.prob}% {pTab.confidence}</span>
                            </div>
                            <div className="h-1.5 sm:h-2 w-full rounded-full bg-tactical-border overflow-hidden">
                                <div
                                    className="h-full rounded-full bg-gradient-to-r from-[#22C55E] via-[#38BDF8] to-[#8B5CF6] transition-all duration-500"
                                    style={{ width: `${currentEye.prob}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Skin Tone Panel */}
                <div className="rounded-xl border border-tactical-border bg-tactical-bg/70 p-3 sm:p-4 space-y-2.5 sm:space-y-3 shadow-md">
                    <div className="flex flex-wrap sm:flex-nowrap items-center justify-between gap-1.5 border-b border-tactical-border pb-2">
                        <div className="flex items-center gap-1.5 min-w-0">
                            <Sliders className="h-4 w-4 text-[#F59E0B] shrink-0" />
                            <span className="font-mono text-[10px] sm:text-xs font-bold tracking-wider text-tactical-text uppercase leading-tight">
                                {pTab.skinTitle}
                            </span>
                        </div>
                        <span className="shrink-0 font-mono text-[8px] sm:text-[9px] text-[#F59E0B] bg-[#F59E0B]/10 border border-[#F59E0B]/20 px-2 py-0.5 rounded-full font-bold">
                            {pTab.skinSub}
                        </span>
                    </div>

                    <div className="grid grid-cols-3 sm:grid-cols-6 gap-1 sm:gap-2">
                        {SKIN_TYPES_DATA.map((st, i) => (
                            <button
                                key={st.type}
                                onClick={() => setSelectedSkin(i)}
                                className={`rounded-lg sm:rounded-xl border p-1.5 sm:p-2 font-mono text-[9px] sm:text-[10px] flex flex-col items-center gap-1 transition-all cursor-pointer ${
                                    selectedSkin === i
                                        ? "border-[#F59E0B] bg-[#F59E0B]/10 text-white shadow-[0_0_12px_rgba(245,158,11,0.25)]"
                                        : "border-tactical-border bg-tactical-surface text-tactical-text-muted hover:border-tactical-border/80"
                                }`}
                            >
                                <span
                                    className="h-2 w-full rounded border border-white/20"
                                    style={{ background: st.color }}
                                />
                                <span className="font-bold whitespace-nowrap">{st.type}</span>
                                <span className="text-[8px] text-tactical-text-dim text-center truncate w-full">{pTab.skinTypes[st.key]}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Right Col: Biometric Summary Card */}
            <div className="lg:col-span-5 flex flex-col justify-between rounded-xl border border-tactical-border bg-tactical-surface p-3.5 sm:p-5 shadow-xl space-y-3 sm:space-y-4 font-mono">
                <div>
                    <div className="flex items-center justify-between border-b border-tactical-border pb-2 mb-3">
                        <div className="flex items-center gap-1.5">
                            <Sparkles className="h-4 w-4 text-[#8B5CF6] shrink-0" />
                            <span className="font-mono text-xs font-bold tracking-wider text-tactical-text uppercase">
                                {pTab.summaryTitle}
                            </span>
                        </div>
                        <div className="flex items-center gap-1 text-[9px] font-mono text-[#22C55E] shrink-0">
                            <CheckCircle2 className="h-3 w-3" />
                            <span>{pTab.synced}</span>
                        </div>
                    </div>

                    {/* Simulated Biometric Visualizer */}
                    <div className="relative rounded-xl border border-tactical-border bg-tactical-bg/80 p-3 sm:p-4 overflow-hidden flex flex-col items-center justify-center text-center space-y-2.5">
                        {/* Simulated Iris Glow Circle */}
                        <div className="relative h-14 w-14 sm:h-16 sm:w-16 rounded-full flex items-center justify-center border-2 border-white/20 shadow-inner">
                            <div
                                className="absolute inset-1.5 rounded-full blur-[2px] transition-colors duration-500"
                                style={{ background: currentEye.color }}
                            />
                            <div className="relative h-4 w-4 sm:h-5 sm:w-5 rounded-full bg-black border border-white/40 shadow-2xl" />
                        </div>

                        <div>
                            <p className="font-mono text-xs font-bold text-white tracking-wider uppercase">
                                {pTab.predictedIris}: <span style={{ color: currentEye.color }}>{pTab.eyeColors[currentEye.key]}</span>
                            </p>
                            <p className="font-mono text-[9px] sm:text-[10px] text-tactical-text-muted mt-0.5">
                                {pTab.skinPhototypeLabel}: {currentSkin.type} ({pTab.skinTypes[currentSkin.key]})
                            </p>
                        </div>
                    </div>

                    {/* Hair Morphology breakdown */}
                    <div className="mt-3 space-y-1">
                        <span className="font-mono text-[9px] sm:text-[10px] text-tactical-text-dim uppercase tracking-wider block">
                            {pTab.hairScore}
                        </span>
                        <div className="space-y-1">
                            {HAIR_TYPES_DATA.map((h) => (
                                <div
                                    key={h.key}
                                    className="flex justify-between items-center rounded-lg border border-tactical-border/60 bg-tactical-bg/40 px-2.5 py-1.5 text-[10px] sm:text-xs font-mono"
                                >
                                    <span className="text-tactical-text-muted">{pTab.hairTypes[h.key]}</span>
                                    <span className="font-bold text-[#8B5CF6]">{h.score}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="pt-2 sm:pt-3 border-t border-tactical-border/60 flex justify-between items-center font-mono text-[9px] sm:text-[10px] text-tactical-text-dim">
                    <span>IrisPlex / HIrisPlex-S</span>
                    <span className="text-[#22C55E] font-bold">{pTab.accuracy} 99.4%</span>
                </div>
            </div>
        </div>
    );
}

/* ═════════════════════════════════════════════════════════════════════════════
   2. STR LOCUS ANALYSIS TAB (Capillary Electropherogram Simulation)
   ═════════════════════════════════════════════════════════════════════════════ */
const STR_DATA = [
    { name: "TH01", alleles: [6, 9.3], rfu: [3200, 2850], freq: "0.28 / 0.22", lr: "1.42e5", color: "#22C55E" },
    { name: "vWA", alleles: [17, 18], rfu: [4100, 3900], freq: "0.18 / 0.21", lr: "8.90e6", color: "#06B6D4" },
    { name: "TPOX", alleles: [8, 11], rfu: [2400, 2100], freq: "0.52 / 0.12", lr: "4.12e4", color: "#8B5CF6" },
    { name: "CSF1PO", alleles: [10, 12], rfu: [3800, 3650], freq: "0.29 / 0.33", lr: "9.34e5", color: "#22C55E" },
    { name: "D3S1358", alleles: [15, 16], rfu: [4500, 4200], freq: "0.26 / 0.28", lr: "2.10e7", color: "#06B6D4" },
];

function StrTab() {
    const { t } = useSaasLanguage();
    const sTab = t.bioSimulator.strTab;
    const [selectedIdx, setSelectedIdx] = useState(0);
    const currentStr = STR_DATA[selectedIdx];

    return (
        <div className="space-y-3 sm:space-y-4 font-mono max-w-full overflow-hidden">
            {/* Locus Tabs */}
            <div className="flex gap-1.5 sm:gap-2 overflow-x-auto pb-2 scrollbar-none border-b border-tactical-border max-w-full">
                {STR_DATA.map((str, i) => (
                    <button
                        key={str.name}
                        onClick={() => setSelectedIdx(i)}
                        className={`flex items-center gap-1 sm:gap-1.5 rounded-xl border px-2.5 sm:px-3.5 py-1.5 font-mono text-[10px] sm:text-xs font-bold tracking-wider transition-all cursor-pointer shrink-0 whitespace-nowrap ${
                            selectedIdx === i
                                ? "border-[#06B6D4] bg-[#06B6D4]/10 text-[#06B6D4] shadow-[0_0_15px_rgba(6,182,212,0.2)]"
                                : "border-tactical-border bg-tactical-surface text-tactical-text-muted hover:border-tactical-border/80"
                        }`}
                    >
                        <span>{str.name}</span>
                        <span className="text-[8px] sm:text-[10px] font-normal opacity-70">[{str.alleles.join(", ")}]</span>
                    </button>
                ))}
            </div>

            {/* Simulated Capillary Electropherogram Chart */}
            <div className="rounded-xl border border-tactical-border bg-tactical-bg/80 p-3 sm:p-5 space-y-3 shadow-xl max-w-full overflow-hidden">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-1 font-mono text-[10px] sm:text-xs border-b border-tactical-border/60 pb-2">
                    <div className="flex items-center gap-1.5 min-w-0">
                        <Activity className="h-4 w-4 text-[#06B6D4] shrink-0" />
                        <span className="font-bold text-white uppercase tracking-wider truncate">
                            {sTab.electropherogramTitle} — {currentStr.name}
                        </span>
                    </div>
                    <span className="text-tactical-text-dim text-[8px] sm:text-[10px] shrink-0">{sTab.codisPanel}</span>
                </div>

                {/* RFU Peak Plot Area */}
                <div className="relative h-48 sm:h-52 w-full rounded-lg border border-tactical-border bg-black/60 pt-7 pb-3 px-3 sm:pt-8 sm:pb-4 sm:px-6 flex items-end justify-around overflow-hidden">
                    {/* Background Grid Lines */}
                    <div
                        className="absolute inset-0 opacity-[0.1]"
                        style={{
                            backgroundImage: `linear-gradient(#06B6D4 1px, transparent 1px)`,
                            backgroundSize: "100% 20px",
                        }}
                    />

                    {/* RFU Scale on Y Axis */}
                    <div className="absolute left-2 top-2 bottom-3 flex flex-col justify-between font-mono text-[7px] sm:text-[8px] text-tactical-text-dim pointer-events-none">
                        <span>5000 RFU</span>
                        <span>2500 RFU</span>
                        <span>0 RFU</span>
                    </div>

                    {/* Peaks */}
                    {currentStr.alleles.map((allele, i) => {
                        const heightPct = (currentStr.rfu[i] / 5000) * 100;
                        return (
                            <div key={i} className="relative z-10 flex flex-col items-center gap-1.5 w-20 sm:w-24">
                                <span className="font-mono text-[10px] sm:text-xs font-bold text-white bg-tactical-surface/95 border border-tactical-border/90 px-2.5 py-0.5 rounded-md shadow-md whitespace-nowrap">
                                    {sTab.alleleLabel} {allele}
                                </span>
                                <div className="relative w-6 sm:w-8 h-28 sm:h-32 flex items-end">
                                    <div
                                        className="w-full rounded-t-md transition-all duration-500 shadow-[0_0_15px_rgba(6,182,212,0.4)]"
                                        style={{
                                            height: `${heightPct}%`,
                                            background: `linear-gradient(to top, ${currentStr.color}, ${currentStr.color}66)`,
                                        }}
                                    />
                                </div>
                                <span className="font-mono text-[9px] sm:text-[10px] text-[#06B6D4] font-semibold whitespace-nowrap">
                                    {currentStr.rfu[i]} {sTab.rfuLabel}
                                </span>
                            </div>
                        );
                    })}
                </div>

                {/* Statistical Details Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3 pt-1">
                    <div className="rounded-lg border border-tactical-border bg-tactical-surface p-2 sm:p-2.5 font-mono">
                        <span className="text-[8px] sm:text-[9px] text-tactical-text-dim block">{sTab.alleleCall}</span>
                        <span className="text-xs font-bold text-white">{currentStr.alleles.join(" / ")}</span>
                    </div>
                    <div className="rounded-lg border border-tactical-border bg-tactical-surface p-2 sm:p-2.5 font-mono">
                        <span className="text-[8px] sm:text-[9px] text-tactical-text-dim block">{sTab.popFreq}</span>
                        <span className="text-xs font-bold text-[#06B6D4]">{currentStr.freq}</span>
                    </div>
                    <div className="rounded-lg border border-tactical-border bg-tactical-surface p-2 sm:p-2.5 font-mono">
                        <span className="text-[8px] sm:text-[9px] text-tactical-text-dim block">{sTab.locusLr}</span>
                        <span className="text-xs font-bold text-[#22C55E]">{currentStr.lr}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

/* ═════════════════════════════════════════════════════════════════════════════
   3. ZK PROOF AUDITOR TAB (Groth16 SnarkJS Cryptographic Prover)
   ═════════════════════════════════════════════════════════════════════════════ */
function ZkpTab() {
    const { t } = useSaasLanguage();
    const zTab = t.bioSimulator.zkpTab;
    const [status, setStatus] = useState<"idle" | "computing" | "verified">("idle");
    const [proofHash, setProofHash] = useState("");

    const handleGenerate = () => {
        if (status !== "idle") return;
        setStatus("computing");
        setTimeout(() => {
            const mockHash = "0x" + Array.from({ length: 32 }, () => Math.floor(Math.random() * 256).toString(16).padStart(2, "0")).join("");
            setProofHash(mockHash);
            setStatus("verified");
        }, 1600);
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 font-mono max-w-full overflow-hidden">
            {/* Circuit Metadata Panel */}
            <div className="lg:col-span-6 space-y-3">
                <div className="rounded-xl border border-tactical-border bg-tactical-bg/80 p-3 sm:p-4 space-y-2 font-mono text-[10px] sm:text-xs shadow-md">
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-0.5 border-b border-tactical-border pb-1.5">
                        <span className="text-tactical-text-dim shrink-0">{zTab.circuitId}:</span>
                        <span className="font-bold text-[#8B5CF6] break-all sm:truncate">dna_match_20loci.circom</span>
                    </div>
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-0.5 border-b border-tactical-border pb-1.5">
                        <span className="text-tactical-text-dim shrink-0">{zTab.provingScheme}:</span>
                        <span className="font-bold text-[#06B6D4] break-all sm:truncate">Groth16 / SnarkJS v0.7</span>
                    </div>
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-0.5 border-b border-tactical-border pb-1.5">
                        <span className="text-tactical-text-dim shrink-0">{zTab.privateWitness}:</span>
                        <span className="text-tactical-text-muted break-all sm:truncate">raw_str_alleles[20] (isolated)</span>
                    </div>
                    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-0.5">
                        <span className="text-tactical-text-dim shrink-0">{zTab.publicSignal}:</span>
                        <span className="font-bold text-[#22C55E] break-all sm:truncate">match_score &gt;= threshold</span>
                    </div>
                </div>

                {status === "idle" && (
                    <button
                        onClick={handleGenerate}
                        className="w-full rounded-xl bg-gradient-to-r from-[#8B5CF6] to-[#06B6D4] p-3 sm:p-3.5 font-mono text-xs font-bold tracking-wider text-white shadow-lg hover:shadow-[0_0_25px_rgba(139,92,246,0.4)] transition-all flex items-center justify-center gap-2 cursor-pointer"
                    >
                        <Lock className="h-4 w-4 shrink-0" />
                        <span>{zTab.executeBtn}</span>
                    </button>
                )}

                {status === "computing" && (
                    <div className="rounded-xl border border-[#8B5CF6]/40 bg-[#8B5CF6]/10 p-3.5 font-mono text-xs text-center space-y-1.5 animate-pulse">
                        <Activity className="h-5 w-5 text-[#8B5CF6] mx-auto animate-spin" />
                        <p className="font-bold text-white text-[11px] sm:text-xs">{zTab.computing}</p>
                        <p className="text-[9px] sm:text-[10px] text-tactical-text-muted">{zTab.latency}</p>
                    </div>
                )}

                {status === "verified" && (
                    <div className="rounded-xl border border-[#22C55E]/40 bg-[#22C55E]/10 p-3.5 font-mono text-xs space-y-1.5 shadow-lg">
                        <div className="flex items-center gap-2 text-[#22C55E]">
                            <CheckCircle2 className="h-4 w-4 shrink-0" />
                            <span className="font-bold text-xs">{zTab.proofSuccess}</span>
                        </div>
                        <p className="text-[9px] sm:text-[10px] text-tactical-text-muted">
                            {zTab.provenMsg}
                        </p>
                        <button
                            onClick={() => setStatus("idle")}
                            className="text-[9px] sm:text-[10px] text-[#06B6D4] hover:underline cursor-pointer"
                        >
                            {zTab.resetBtn}
                        </button>
                    </div>
                )}
            </div>

            {/* Cryptographic Console Log Output */}
            <div className="lg:col-span-6 rounded-xl border border-tactical-border bg-black p-3.5 font-mono text-[9px] sm:text-[10px] space-y-2 shadow-2xl overflow-hidden flex flex-col justify-between">
                <div>
                    <div className="flex items-center gap-2 text-tactical-text-dim border-b border-tactical-border/60 pb-1.5 mb-2">
                        <Terminal className="h-3.5 w-3.5 text-[#8B5CF6] shrink-0" />
                        <span>{zTab.consoleTitle}</span>
                    </div>

                    <div className="space-y-1 text-tactical-text-muted">
                        <p className="text-[#22C55E]">{zTab.initInfo}</p>
                        <p className="break-all">{zTab.readingInfo}</p>
                        <p className="break-all">{zTab.witnessInfo}</p>
                        {status === "verified" && (
                            <>
                                <p className="text-[#06B6D4]">{zTab.successCreated}</p>
                                <p className="text-white break-all pt-1">
                                    <span className="text-tactical-text-dim block">{zTab.publicHash}:</span>
                                    {proofHash}
                                </p>
                            </>
                        )}
                    </div>
                </div>

                <div className="pt-2 border-t border-tactical-border/60 flex justify-between items-center text-tactical-text-dim text-[8px] sm:text-[9px]">
                    <span>{zTab.testnetReady}</span>
                    <span className="text-[#22C55E] font-bold">{zTab.zeroLeakage}</span>
                </div>
            </div>
        </div>
    );
}

/* ═════════════════════════════════════════════════════════════════════════════
   MAIN CONTAINER WITH RESPONSIVE TABS & MOBILE FIXES
   ═════════════════════════════════════════════════════════════════════════════ */
export default function LandingBioSimulator() {
    const [activeTab, setActiveTab] = useState<TabId>("phenotype");
    const { t, lang } = useSaasLanguage();

    const tabs = [
        {
            id: "phenotype" as TabId,
            label: t.bioSimulator.tabs.phenotype,
            shortLabel: lang === "tr" ? "Fenotip" : "Phenotype",
            icon: Eye,
            color: "#22C55E"
        },
        {
            id: "str" as TabId,
            label: t.bioSimulator.tabs.str,
            shortLabel: lang === "tr" ? "STR Analiz" : "STR Locus",
            icon: Dna,
            color: "#06B6D4"
        },
        {
            id: "zkp" as TabId,
            label: t.bioSimulator.tabs.zkp,
            shortLabel: lang === "tr" ? "ZKP İspat" : "ZK Auditor",
            icon: ShieldCheck,
            color: "#8B5CF6"
        },
    ];

    return (
        <section id="bio-simulator" className="scroll-mt-20 min-h-[85vh] lg:min-h-screen flex flex-col justify-between py-8 sm:py-12 px-3 sm:px-4 bg-tactical-surface/20 max-w-full overflow-hidden">
            <div className="my-auto mx-auto max-w-6xl w-full">
                {/* Section header */}
                <div className="text-center mb-6 sm:mb-8 px-2">
                    <div className="inline-flex items-start sm:items-center gap-2 rounded-full border border-[#06B6D4]/30 bg-[#06B6D4]/5 px-3 sm:px-4 py-1.5 mb-2.5 shadow-[0_0_15px_rgba(6,182,212,0.1)] max-w-full text-left sm:text-center">
                        <Dna className="h-3.5 w-3.5 text-[#06B6D4] shrink-0 mt-0.5 sm:mt-0" />
                        <span className="font-mono text-[9px] sm:text-[10px] tracking-widest text-[#06B6D4] uppercase font-bold leading-snug">
                            {t.bioSimulator.badge}
                        </span>
                    </div>
                    <h2 className="text-2xl sm:text-4xl font-bold text-tactical-text mb-2 sm:mb-3 leading-tight">
                        {t.bioSimulator.title}
                    </h2>
                    <p className="max-w-xl mx-auto text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                        {t.bioSimulator.subtitle}
                    </p>
                </div>

                {/* Main Card Shell */}
                <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface p-2.5 sm:p-5 shadow-[0_0_60px_rgba(0,0,0,0.6)] max-w-full overflow-hidden">
                    {/* Navigation Tabs - Responsive Grid with Short Labels on Mobile */}
                    <div className="grid grid-cols-3 gap-1 sm:gap-2 border-b border-tactical-border/80 pb-3 mb-4 sm:mb-5 max-w-full">
                        {tabs.map((tab) => {
                            const Icon = tab.icon;
                            const isActive = activeTab === tab.id;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center justify-center gap-1 sm:gap-2 px-1 sm:px-4 py-2 sm:py-2.5 rounded-xl font-mono text-[10px] sm:text-xs font-bold tracking-tight sm:tracking-wide transition-all duration-300 cursor-pointer overflow-hidden ${
                                        isActive
                                            ? "bg-tactical-surface-elevated text-white border border-tactical-border shadow-lg"
                                            : "text-tactical-text-muted hover:text-white hover:bg-tactical-surface-elevated/50 border border-transparent"
                                    }`}
                                    style={isActive ? { borderColor: `${tab.color}60` } : {}}
                                >
                                    <Icon className="h-3.5 w-3.5 shrink-0" style={{ color: tab.color }} />
                                    <span className="hidden sm:inline whitespace-nowrap">{tab.label}</span>
                                    <span className="sm:hidden whitespace-nowrap text-[10px]">{tab.shortLabel}</span>
                                </button>
                            );
                        })}
                    </div>

                    {/* Tab Body */}
                    <div className="p-0.5 sm:p-3">
                        {activeTab === "phenotype" && <PhenotypeTab />}
                        {activeTab === "str" && <StrTab />}
                        {activeTab === "zkp" && <ZkpTab />}
                    </div>
                </div>
            </div>
        </section>
    );
}
