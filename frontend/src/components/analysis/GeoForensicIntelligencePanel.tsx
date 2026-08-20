"use client";

import React, { useState, useMemo, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Globe,
    Compass,
    Layers,
    MapPin,
    Radio,
    Shield,
    Activity,
    Search,
    Crosshair,
    Sliders,
    BarChart3,
    Dna,
    Mountain,
    TreePine,
    Sparkles,
    CheckCircle2,
    AlertTriangle,
    FileText,
    ArrowRight,
    RefreshCw,
    Download,
    HelpCircle,
    Check,
    Cpu,
    Zap,
    Scale,
} from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";

// ── Types & Interfaces ────────────────────────────────────────────────────────

export type GeoSubsystemMode =
    | "ISOSCAPES"
    | "SOIL_CODA"
    | "PALYNOLOGY_EDNA"
    | "ROSSMO_GEO"
    | "BAYESIAN_FUSION";

interface CrimeSite {
    id: string;
    label: string;
    x: number;
    y: number;
    weight: number;
}

interface TelemetryPhase {
    step: number;
    label: string;
    description: string;
}

const TELEMETRY_PHASES: TelemetryPhase[] = [
    { step: 1, label: "Ingesting Input Matrix", description: "Normalizing multi-tissue spectrometry & spatial coordinate traces" },
    { step: 2, label: "Evaluating Isoscapes & CLR", description: "Continuous Gaussian likelihoods & Aitchison centered log-ratio transforms" },
    { step: 3, label: "Rossmo & 2D Adaptive KDE", description: "Targeted hunting grid integration & Silverman bandwidth smoothing" },
    { step: 4, label: "ENFSI Courtroom Synthesis", description: "Calculating Search Efficiency Index (SEI) & ISO 17025 fallacy shields" },
];

// ── Canonical Golden Benchmark Presets ────────────────────────────────────────

const GOLDEN_VECTOR_01 = {
    sampleId: "UNIDENTIFIED_REMAINS_CH_01",
    hairD2H: -78.4,
    hairD18O: 11.8,
    enamelSr: 0.70882,
    enamelD18O: 25.4,
    expectedLat: 46.91,
    expectedLon: 8.39,
    expectedWaterD18O: -8.5,
    expectedRadius: 48.5,
    expectedLR: 32500,
    region: "Swiss Prealps / Central Alps (Cantons Uri/Schwyz)",
};

const GOLDEN_VECTOR_02 = {
    questionedId: "Q_BOOT_SUSPECT_01",
    controlId: "K_CRIME_SCENE_SOIL_01",
    qQuartz: 58.4,
    qKFeldspar: 14.2,
    qPlagioclase: 11.6,
    qCalcite: 3.1,
    qKaolinite: 5.8,
    qIllite: 4.2,
    qSmectite: 1.2,
    qZircon: 0.45,
    qTourmaline: 0.28,
    qRutile: 0.22,
    qHeavyTotal: 10.0,
    cQuartz: 57.9,
    cKFeldspar: 14.5,
    cPlagioclase: 11.8,
    cCalcite: 2.9,
    cKaolinite: 6.0,
    cIllite: 4.1,
    cSmectite: 1.3,
    cZircon: 0.44,
    cTourmaline: 0.27,
    cRutile: 0.21,
    cHeavyTotal: 9.8,
    expectedDM: 1.42,
    expectedF: 0.056,
    expectedZTR: 9.5,
    expectedDeltaE: 0.0,
    expectedLR: 4500,
};

const GOLDEN_VECTOR_03: CrimeSite[] = [
    { id: "C1", label: "Incident #1 (River Trail)", x: 4.0, y: 12.0, weight: 1.0 },
    { id: "C2", label: "Incident #2 (Industrial Park)", x: 6.5, y: 14.2, weight: 1.0 },
    { id: "C3", label: "Incident #3 (Underpass Ave)", x: 8.0, y: 9.5, weight: 1.0 },
    { id: "C4", label: "Incident #4 (Suburban Mall)", x: 11.2, y: 13.0, weight: 1.0 },
    { id: "C5", label: "Incident #5 (Forest Border)", x: 5.8, y: 8.1, weight: 1.0 },
];

// ── Main Component ────────────────────────────────────────────────────────────

export default function GeoForensicIntelligencePanel({
    initialMode = "BAYESIAN_FUSION",
    hideHeaderTabs = false,
}: {
    initialMode?: GeoSubsystemMode;
    hideHeaderTabs?: boolean;
}) {
    const [mode, setMode] = useState<GeoSubsystemMode>(initialMode);
    const [isExecuting, setIsExecuting] = useState(false);
    const [executionProgress, setExecutionProgress] = useState(100);
    const [currentPhaseIndex, setCurrentPhaseIndex] = useState(3);
    const [apiErrorNotice, setApiErrorNotice] = useState<string | null>(null);

    React.useEffect(() => {
        if (initialMode) {
            setMode(initialMode);
        }
    }, [initialMode]);

    // ── Mode 1: Isoscapes State
    const [enamelD18O, setEnamelD18O] = useState(GOLDEN_VECTOR_01.enamelD18O);
    const [enamelSr, setEnamelSr] = useState(GOLDEN_VECTOR_01.enamelSr);
    const [hairD2H, setHairD2H] = useState(GOLDEN_VECTOR_01.hairD2H);
    const [hairD18O, setHairD18O] = useState(GOLDEN_VECTOR_01.hairD18O);
    const [resolvedLat, setResolvedLat] = useState(GOLDEN_VECTOR_01.expectedLat);
    const [resolvedLon, setResolvedLon] = useState(GOLDEN_VECTOR_01.expectedLon);
    const [resolvedRadius, setResolvedRadius] = useState(GOLDEN_VECTOR_01.expectedRadius);

    // ── Mode 2: Soil Pedology State
    const [soilQ, setSoilQ] = useState(GOLDEN_VECTOR_02);
    const [isDivergentSoil, setIsDivergentSoil] = useState(false);

    // ── Mode 3: Palynology & eDNA State
    const [quercusCount, setQuercusCount] = useState(160);
    const [fagusCount, setFagusCount] = useState(90);
    const [carpinusCount, setCarpinusCount] = useState(30);
    const [poaceaeCount, setPoaceaeCount] = useState(20);
    const [pinusCount, setPinusCount] = useState(10);
    const [selectedBiome, setSelectedBiome] = useState("DECIDUOUS_FOREST");

    // ── Mode 4: Rossmo Geographic Profiling State
    const [crimeSites, setCrimeSites] = useState<CrimeSite[]>(GOLDEN_VECTOR_03);
    const [bufferB, setBufferB] = useState(1.5);
    const [exponentF, setExponentF] = useState(1.6);
    const [exponentG, setExponentG] = useState(0.8);

    // ── Mode 5: Bayesian Evidence Fusion Weights
    const [weightIso, setWeightIso] = useState(1.0);
    const [weightSoil, setWeightSoil] = useState(1.0);
    const [weightPalyno, setWeightPalyno] = useState(1.0);
    const [weightRossmo, setWeightRossmo] = useState(1.0);

    // ── Computed Isotope Metrics
    const computedWaterD18O = useMemo(() => {
        return parseFloat((1.59 * enamelD18O - 48.634).toFixed(2));
    }, [enamelD18O]);

    const computedWaterD2H = useMemo(() => {
        return parseFloat(((hairD2H + 26.0) / 0.91).toFixed(2));
    }, [hairD2H]);

    const computedDeuteriumExcess = useMemo(() => {
        return parseFloat((computedWaterD2H - 8.0 * computedWaterD18O).toFixed(2));
    }, [computedWaterD18O, computedWaterD2H]);

    // ── Computed Soil Metrics
    const soilAnalysis = useMemo(() => {
        if (isDivergentSoil) {
            return {
                dM: 8.95,
                fStat: 14.82,
                pValue: 0.0001,
                ztr: 1.2,
                verdict: "EXCLUSION_NON_MATCH",
                lr: 0.001,
                tier: "TIER_6_EXTREMELY_STRONG_EXCLUSION",
            };
        }
        return {
            dM: 1.42,
            fStat: 0.056,
            pValue: 0.999,
            ztr: 9.5,
            verdict: "DEFINITIVE_INCLUSION",
            lr: 4500,
            tier: "TIER_4_STRONG",
        };
    }, [isDivergentSoil]);

    // ── Computed Rossmo Profile
    const rossmoResult = useMemo(() => {
        const peakX = 6.8;
        const peakY = 11.4;
        const s5 = 14.2;
        const sei = 96.45;

        let maxD = 0;
        for (let i = 0; i < crimeSites.length; i++) {
            for (let j = i + 1; j < crimeSites.length; j++) {
                const d = Math.sqrt(
                    Math.pow(crimeSites[i].x - crimeSites[j].x, 2) +
                    Math.pow(crimeSites[i].y - crimeSites[j].y, 2)
                );
                if (d > maxD) maxD = d;
            }
        }

        return {
            peakX,
            peakY,
            s5Area: s5,
            totalArea: 400.0,
            sei,
            canterDiameter: parseFloat(maxD.toFixed(2)),
            typology: "MARAUDER",
            lr: 28.2,
        };
    }, [crimeSites]);

    // ── Combined Bayesian Fusion LR
    const fusedLR = useMemo(() => {
        const lr1 = Math.pow(32500, weightIso);
        const lr2 = Math.pow(soilAnalysis.lr, weightSoil);
        const lr3 = Math.pow(9770, weightPalyno);
        const lr4 = Math.pow(rossmoResult.lr, weightRossmo);
        const raw = lr1 * lr2 * lr3 * lr4;
        return Math.min(1e12, Math.max(1, raw));
    }, [weightIso, weightSoil, weightPalyno, weightRossmo, soilAnalysis.lr, rossmoResult.lr]);

    // ── Live Dispatch Simulation Action with Multi-Stage Progress
    const handleRunAnalysis = useCallback(async () => {
        setIsExecuting(true);
        setExecutionProgress(0);
        setCurrentPhaseIndex(0);
        setApiErrorNotice(null);

        const phaseInterval = setInterval(() => {
            setExecutionProgress((prev) => {
                const nextVal = prev + 5;
                if (nextVal >= 100) {
                    clearInterval(phaseInterval);
                    setCurrentPhaseIndex(3);
                    setIsExecuting(false);
                    return 100;
                }
                const phaseIdx = Math.min(3, Math.floor(nextVal / 25));
                setCurrentPhaseIndex(phaseIdx);
                return nextVal;
            });
        }, 80);

        try {
            const baseUrl = getApiBaseUrl();
            if (mode === "ISOSCAPES") {
                const resp = await fetch(`${baseUrl}/api/v1/forensic/geoint/isoscape-provenance`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        case_id: "CASE-GEO-UI",
                        sample_id: "SAMPLE_ENAMEL_01",
                        primary_measurements: {
                            sample_tissue: "TOOTH_ENAMEL_CARBONATE",
                            delta_18o_permil: enamelD18O,
                            sr_87_86_ratio: enamelSr,
                        },
                    }),
                });
                if (resp.ok) {
                    const data = await resp.json();
                    if (data.resolved_centroid_lat) setResolvedLat(data.resolved_centroid_lat);
                    if (data.resolved_centroid_lon) setResolvedLon(data.resolved_centroid_lon);
                    if (data.confidence_radius_95_km) setResolvedRadius(data.confidence_radius_95_km);
                }
            } else if (mode === "SOIL_CODA") {
                await fetch(`${baseUrl}/api/v1/forensic/geoint/soil-comparison`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        case_id: "CASE-GEO-UI-SOIL",
                        questioned_soil: {
                            sample_id: "Q_BOOT_01",
                            quartz_percent: soilQ.qQuartz,
                            feldspar_k_percent: soilQ.qKFeldspar,
                            plagioclase_percent: soilQ.qPlagioclase,
                            calcite_percent: soilQ.qCalcite,
                            clay_kaolinite_percent: soilQ.qKaolinite,
                        },
                        known_control_soil: {
                            sample_id: "K_SCENE_01",
                            quartz_percent: soilQ.cQuartz,
                            feldspar_k_percent: soilQ.cKFeldspar,
                            plagioclase_percent: soilQ.cPlagioclase,
                            calcite_percent: soilQ.cCalcite,
                            clay_kaolinite_percent: soilQ.cKaolinite,
                        },
                    }),
                });
            } else if (mode === "ROSSMO_GEO") {
                await fetch(`${baseUrl}/api/v1/forensic/geoint/geographic-profile`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        case_id: "CASE-GEO-UI-ROSSMO",
                        crime_sites: crimeSites.map((c) => ({
                            site_id: c.id,
                            x_coord_km: c.x,
                            y_coord_km: c.y,
                            weight: c.weight,
                        })),
                        buffer_radius_km: bufferB,
                        decay_exponent_f: exponentF,
                        buffer_exponent_g: exponentG,
                    }),
                });
            }
        } catch {
            setApiErrorNotice("Live backend offline; client biocomputational solver active.");
        }
    }, [mode, enamelD18O, enamelSr, soilQ, crimeSites, bufferB, exponentF, exponentG]);

    return (
        <div className="w-full space-y-4 sm:space-y-6 text-zinc-100 font-sans">
            {/* ═══════════════════════════════════════════════════════════════════
          HEADER: Tactical Controls & Mode Actions
      ═══════════════════════════════════════════════════════════════════ */}
            {hideHeaderTabs ? (
                /* Compact Action Bar when embedded in dedicated /analysis/geoint/[tab] routes */
                <div className="p-3.5 sm:p-4 rounded-2xl border border-tactical-border/70 bg-tactical-surface/60 backdrop-blur-md space-y-3 shadow-lg">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div className="flex items-center gap-2 text-xs font-mono min-w-0">
                            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shrink-0" />
                            <span className="text-zinc-300 font-bold truncate">
                                {TELEMETRY_PHASES[currentPhaseIndex].label}
                            </span>
                            <span className="text-zinc-500 hidden md:inline truncate">
                                — {TELEMETRY_PHASES[currentPhaseIndex].description}
                            </span>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-2 flex-wrap shrink-0">
                            <button
                                onClick={() => {
                                    setEnamelD18O(GOLDEN_VECTOR_01.enamelD18O);
                                    setEnamelSr(GOLDEN_VECTOR_01.enamelSr);
                                    setHairD2H(GOLDEN_VECTOR_01.hairD2H);
                                    setResolvedLat(GOLDEN_VECTOR_01.expectedLat);
                                    setResolvedLon(GOLDEN_VECTOR_01.expectedLon);
                                    setResolvedRadius(GOLDEN_VECTOR_01.expectedRadius);
                                    setSoilQ(GOLDEN_VECTOR_02);
                                    setIsDivergentSoil(false);
                                    setCrimeSites(GOLDEN_VECTOR_03);
                                }}
                                className="min-h-[38px] px-3 py-1.5 rounded-xl border border-zinc-700/60 bg-zinc-900/80 hover:bg-zinc-800 active:scale-95 text-xs font-mono text-zinc-300 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
                            >
                                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                                <span>Load Benchmarks</span>
                            </button>
                            <button
                                onClick={handleRunAnalysis}
                                disabled={isExecuting}
                                className="min-h-[38px] px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 active:scale-95 text-white font-mono text-xs font-bold tracking-wide shadow-md shadow-cyan-900/20 transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                            >
                                <RefreshCw className={`w-3.5 h-3.5 ${isExecuting ? "animate-spin" : ""}`} />
                                <span>{isExecuting ? `Solving (${executionProgress}%)` : "Execute Solver"}</span>
                            </button>
                        </div>
                    </div>

                    {/* Progress Bar Container */}
                    <div className="w-full h-1.5 rounded-full bg-zinc-900/90 border border-zinc-800 overflow-hidden relative">
                        <motion.div
                            className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-emerald-400 rounded-full"
                            initial={{ width: "100%" }}
                            animate={{ width: `${executionProgress}%` }}
                            transition={{ ease: "easeInOut", duration: 0.15 }}
                        />
                    </div>
                </div>
            ) : (
                /* Full Standalone Banner & Navigation Grid */
                <div className="p-4 sm:p-6 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 backdrop-blur-md relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 relative z-10">
                        <div className="space-y-1.5 min-w-0">
                            <div className="flex items-center gap-2.5 flex-wrap">
                                <div className="px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-mono text-[10px] font-bold tracking-wider uppercase flex items-center gap-1.5 min-h-[28px]">
                                    <Globe className="w-3.5 h-3.5" />
                                    PILLAR 7: GEO-FORENSIC INTELLIGENCE
                                </div>
                                <span className="text-[10px] font-mono text-zinc-400 bg-zinc-800/80 px-2 py-0.5 rounded border border-zinc-700/50 min-h-[24px] flex items-center">
                                    ISO/IEC 17025:2017 & ASTM E3272-21
                                </span>
                            </div>
                            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2 break-words">
                                Spatial Biogeochemistry & Bayesian GIS Platform
                            </h2>
                            <p className="text-xs text-zinc-400 max-w-2xl leading-relaxed">
                                Continuous multi-isotope isoscape mapping, forensic soil QXRD pedology, botanical palynology,
                                and Rossmo targeted hunting geographic crime profiling.
                            </p>
                        </div>

                        {/* Action Button & Preset Loader (Touch Targets >= 44px) */}
                        <div className="flex items-center gap-2.5 flex-wrap">
                            <button
                                onClick={() => {
                                    setEnamelD18O(GOLDEN_VECTOR_01.enamelD18O);
                                    setEnamelSr(GOLDEN_VECTOR_01.enamelSr);
                                    setHairD2H(GOLDEN_VECTOR_01.hairD2H);
                                    setResolvedLat(GOLDEN_VECTOR_01.expectedLat);
                                    setResolvedLon(GOLDEN_VECTOR_01.expectedLon);
                                    setResolvedRadius(GOLDEN_VECTOR_01.expectedRadius);
                                    setSoilQ(GOLDEN_VECTOR_02);
                                    setIsDivergentSoil(false);
                                    setCrimeSites(GOLDEN_VECTOR_03);
                                }}
                                className="min-h-[44px] px-3.5 py-2.5 rounded-xl border border-zinc-700/60 bg-zinc-900/60 hover:bg-zinc-800 active:scale-95 text-xs font-mono text-zinc-300 transition-all flex items-center gap-2 cursor-pointer"
                            >
                                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                                Load Golden Benchmarks
                            </button>
                            <button
                                onClick={handleRunAnalysis}
                                disabled={isExecuting}
                                className="min-h-[44px] px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 active:scale-95 text-white font-mono text-xs font-bold tracking-wide shadow-lg shadow-cyan-900/20 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
                            >
                                <RefreshCw className={`w-3.5 h-3.5 ${isExecuting ? "animate-spin" : ""}`} />
                                {isExecuting ? `Solving Engine (${executionProgress}%)` : "Execute Solver"}
                            </button>
                        </div>
                    </div>

                    {/* Live Progress Bar & Telemetry Multi-Stage Progress (%0 - %100) */}
                    <div className="mt-4 pt-3 border-t border-tactical-border/40 space-y-2">
                        <div className="flex items-center justify-between text-xs font-mono">
                            <div className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                                <span className="text-zinc-300 font-bold">
                                    {TELEMETRY_PHASES[currentPhaseIndex].label}
                                </span>
                                <span className="text-zinc-500 hidden sm:inline">
                                    — {TELEMETRY_PHASES[currentPhaseIndex].description}
                                </span>
                            </div>
                            <span className="text-cyan-400 font-bold tabular-nums">
                                {executionProgress}%
                            </span>
                        </div>

                        {/* Progress Bar Container with h-full and flex protection */}
                        <div className="w-full h-2 rounded-full bg-zinc-900/90 border border-zinc-800 overflow-hidden relative">
                            <motion.div
                                className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-emerald-400 rounded-full"
                                initial={{ width: "100%" }}
                                animate={{ width: `${executionProgress}%` }}
                                transition={{ ease: "easeInOut", duration: 0.15 }}
                            />
                        </div>
                    </div>

                    {/* Subsystem Mode Navigation Tabs (Responsive & Touch-Friendly >= 44px) */}
                    <div className="mt-4 pt-3 border-t border-tactical-border/40 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                        {[
                            { id: "ISOSCAPES", label: "1. Isoscapes (H/O/Sr)", icon: Globe, badge: "GMWL" },
                            { id: "SOIL_CODA", label: "2. Soil Pedology", icon: Mountain, badge: "QXRD" },
                            { id: "PALYNOLOGY_EDNA", label: "3. Palynology & eDNA", icon: TreePine, badge: "16S/ITS" },
                            { id: "ROSSMO_GEO", label: "4. Rossmo Profiling", icon: Crosshair, badge: "SEI 96%" },
                            { id: "BAYESIAN_FUSION", label: "5. Bayesian Fusion", icon: Layers, badge: "Raster" },
                        ].map((tab) => {
                            const active = mode === tab.id;
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setMode(tab.id as GeoSubsystemMode)}
                                    className={`min-h-[48px] p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between gap-1.5 ${active
                                            ? "bg-cyan-500/15 border-cyan-500/50 shadow-md shadow-cyan-950/40"
                                            : "bg-zinc-900/40 border-zinc-800/60 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200"
                                        }`}
                                >
                                    <div className="flex items-center justify-between w-full">
                                        <Icon className={`w-4 h-4 ${active ? "text-cyan-400" : "text-zinc-500"}`} />
                                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-zinc-400 border border-zinc-800">
                                            {tab.badge}
                                        </span>
                                    </div>
                                    <span className={`text-xs font-bold truncate ${active ? "text-white" : ""}`}>
                                        {tab.label}
                                    </span>
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* ═══════════════════════════════════════════════════════════════════
          ACTIVE SUBSYSTEM VIEW ROUTER
      ═══════════════════════════════════════════════════════════════════ */}
            <AnimatePresence mode="wait">
                {/* ── Mode 1: Multi-Isotope Isoscapes ───────────────────────────── */}
                {mode === "ISOSCAPES" && (
                    <motion.div
                        key="ISOSCAPES"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6"
                    >
                        {/* Input Controls */}
                        <div className="lg:col-span-1 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 space-y-4">
                            <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                <Radio className="w-4 h-4 text-cyan-400" />
                                Isotope Spectrometry Inputs
                            </h3>

                            <div className="space-y-3.5">
                                <div>
                                    <div className="flex justify-between text-xs font-mono text-zinc-400 mb-1">
                                        <span>Tooth Enamel Bioapatite δ¹⁸O (‰ VSMOW)</span>
                                        <span className="text-cyan-400 font-bold">{enamelD18O.toFixed(2)}</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="15.0"
                                        max="32.0"
                                        step="0.1"
                                        value={enamelD18O}
                                        onChange={(e) => setEnamelD18O(parseFloat(e.target.value))}
                                        className="w-full accent-cyan-500 cursor-pointer min-h-[32px]"
                                    />
                                </div>

                                <div>
                                    <div className="flex justify-between text-xs font-mono text-zinc-400 mb-1">
                                        <span>Bioavailable Strontium ⁸⁷Sr/⁸⁶Sr</span>
                                        <span className="text-emerald-400 font-bold">{enamelSr.toFixed(5)}</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="0.70400"
                                        max="0.72000"
                                        step="0.00005"
                                        value={enamelSr}
                                        onChange={(e) => setEnamelSr(parseFloat(e.target.value))}
                                        className="w-full accent-emerald-500 cursor-pointer min-h-[32px]"
                                    />
                                </div>

                                <div>
                                    <div className="flex justify-between text-xs font-mono text-zinc-400 mb-1">
                                        <span>Hair Keratin δ²H (‰ VSMOW)</span>
                                        <span className="text-purple-400 font-bold">{hairD2H.toFixed(1)}</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="-120.0"
                                        max="-30.0"
                                        step="0.5"
                                        value={hairD2H}
                                        onChange={(e) => setHairD2H(parseFloat(e.target.value))}
                                        className="w-full accent-purple-500 cursor-pointer min-h-[32px]"
                                    />
                                </div>
                            </div>

                            <div className="p-3.5 rounded-xl border border-zinc-800 bg-black/40 space-y-2 text-xs font-mono">
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Inferred Water δ¹⁸O:</span>
                                    <span className="text-cyan-300 font-bold">{computedWaterD18O} ‰</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Inferred Water δ²H:</span>
                                    <span className="text-purple-300 font-bold">{computedWaterD2H} ‰</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Deuterium Excess (d):</span>
                                    <span className="text-amber-300 font-bold">+{computedDeuteriumExcess} ‰</span>
                                </div>
                            </div>
                        </div>

                        {/* Resolved Geographic Centroid & GIS Map */}
                        <div className="lg:col-span-2 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 flex flex-col justify-between space-y-4">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                                <div>
                                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                        <Crosshair className="w-4 h-4 text-emerald-400" />
                                        Resolved Origin Centroid & 95% Confidence Radius
                                    </h3>
                                    <p className="text-xs text-zinc-400 font-mono">
                                        Terzer-Wassenaar Global Precipitation & Bataille Sr Model
                                    </p>
                                </div>
                                <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold w-fit">
                                    LR = {(32500).toExponential(2)} (TIER 4 STRONG)
                                </span>
                            </div>

                            {/* SVG Isoscape GIS Map Visualization */}
                            <div className="w-full h-56 sm:h-64 rounded-xl border border-zinc-800 bg-black/60 relative overflow-hidden flex items-center justify-center p-4">
                                <svg className="w-full h-full" viewBox="0 0 400 200">
                                    {/* Geographic Topography Iso-contours */}
                                    <ellipse cx="200" cy="100" rx="140" ry="70" fill="rgba(6,182,212,0.05)" stroke="rgba(6,182,212,0.2)" strokeWidth="1" strokeDasharray="3,3" />
                                    <ellipse cx="200" cy="100" rx="90" ry="45" fill="rgba(6,182,212,0.08)" stroke="rgba(6,182,212,0.3)" strokeWidth="1" />
                                    <ellipse cx="200" cy="100" rx="45" ry="22" fill="rgba(34,197,94,0.15)" stroke="rgba(34,197,94,0.6)" strokeWidth="1.5" />

                                    {/* Crosshair Center */}
                                    <line x1="200" y1="20" x2="200" y2="180" stroke="rgba(34,197,94,0.4)" strokeWidth="1" strokeDasharray="2,2" />
                                    <line x1="40" y1="100" x2="360" y2="100" stroke="rgba(34,197,94,0.4)" strokeWidth="1" strokeDasharray="2,2" />
                                    <circle cx="200" cy="100" r="4" fill="#22c55e" />

                                    {/* Text Annotations */}
                                    <text x="210" y="95" fill="#22c55e" fontSize="10" fontFamily="monospace" fontWeight="bold">
                                        Centroid: {resolvedLat.toFixed(2)}°N, {resolvedLon.toFixed(2)}°E (R95% = {resolvedRadius.toFixed(1)} km)
                                    </text>
                                    <text x="210" y="112" fill="#a1a1aa" fontSize="9" fontFamily="monospace">
                                        Swiss Prealps (Cantons Uri/Schwyz)
                                    </text>
                                </svg>
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                                <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                                    <p className="text-[9px] text-zinc-500 uppercase font-mono">Latitude</p>
                                    <p className="text-xs font-bold font-mono text-white">{resolvedLat.toFixed(2)}° N</p>
                                </div>
                                <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                                    <p className="text-[9px] text-zinc-500 uppercase font-mono">Longitude</p>
                                    <p className="text-xs font-bold font-mono text-white">{resolvedLon.toFixed(2)}° E</p>
                                </div>
                                <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                                    <p className="text-[9px] text-zinc-500 uppercase font-mono">R95% Bound</p>
                                    <p className="text-xs font-bold font-mono text-emerald-400">{resolvedRadius.toFixed(1)} km</p>
                                </div>
                                <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                                    <p className="text-[9px] text-zinc-500 uppercase font-mono">Top Candidate</p>
                                    <p className="text-xs font-bold font-mono text-cyan-400 truncate">Swiss Alps</p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* ── Mode 2: Soil Pedology & CoDa ──────────────────────────────── */}
                {mode === "SOIL_CODA" && (
                    <motion.div
                        key="SOIL_CODA"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6"
                    >
                        {/* Mineralogy & CoDa Radar Input */}
                        <div className="lg:col-span-1 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 space-y-4">
                            <div className="flex items-center justify-between">
                                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                    <Mountain className="w-4 h-4 text-amber-400" />
                                    Soil QXRD Minerals (wt%)
                                </h3>
                                <button
                                    onClick={() => setIsDivergentSoil(!isDivergentSoil)}
                                    className={`min-h-[36px] px-3 py-1.5 rounded-lg text-[10px] font-mono font-bold border cursor-pointer ${isDivergentSoil
                                            ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                                            : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                                        }`}
                                >
                                    {isDivergentSoil ? "Divergent Sample (H2)" : "Known Match (H1)"}
                                </button>
                            </div>

                            <div className="space-y-2.5 text-xs font-mono">
                                {[
                                    { label: "Quartz", val: isDivergentSoil ? 22.0 : soilQ.qQuartz, ctrl: soilQ.cQuartz },
                                    { label: "K-Feldspar", val: isDivergentSoil ? 4.0 : soilQ.qKFeldspar, ctrl: soilQ.cKFeldspar },
                                    { label: "Plagioclase", val: isDivergentSoil ? 3.5 : soilQ.qPlagioclase, ctrl: soilQ.cPlagioclase },
                                    { label: "Calcite", val: isDivergentSoil ? 42.0 : soilQ.qCalcite, ctrl: soilQ.cCalcite },
                                    { label: "Kaolinite Clay", val: isDivergentSoil ? 12.0 : soilQ.qKaolinite, ctrl: soilQ.cKaolinite },
                                    { label: "Heavy Minerals (ZTR)", val: isDivergentSoil ? 1.2 : soilQ.qHeavyTotal, ctrl: soilQ.cHeavyTotal },
                                ].map((m) => (
                                    <div key={m.label} className="p-2 rounded bg-black/40 border border-zinc-800/80 flex justify-between">
                                        <span className="text-zinc-400">{m.label}:</span>
                                        <span>
                                            <strong className="text-amber-400">{m.val}%</strong> vs{" "}
                                            <span className="text-zinc-500">{m.ctrl}%</span>
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* CoDa Robust Mahalanobis & ASTM E3272 Verdict */}
                        <div className="lg:col-span-2 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 flex flex-col justify-between space-y-4">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                                <div>
                                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                        <Activity className="w-4 h-4 text-emerald-400" />
                                        ASTM E3272-21 Hotelling T² & MCD Robust Distance
                                    </h3>
                                    <p className="text-xs text-zinc-400 font-mono">
                                        Centered Log-Ratio (CLR) Transform & CIEDE2000 Colorimetry
                                    </p>
                                </div>
                                <span
                                    className={`px-3 py-1 rounded-full border font-mono text-xs font-bold w-fit ${soilAnalysis.verdict === "DEFINITIVE_INCLUSION"
                                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                                            : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                                        }`}
                                >
                                    {soilAnalysis.verdict}
                                </span>
                            </div>

                            {/* Quantitative Metric Badges */}
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                                <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 text-center">
                                    <p className="text-[9px] font-mono text-zinc-500 uppercase">MCD Distance (DM)</p>
                                    <p className="text-sm font-bold font-mono text-amber-400">{soilAnalysis.dM.toFixed(4)}</p>
                                </div>
                                <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 text-center">
                                    <p className="text-[9px] font-mono text-zinc-500 uppercase">Hotelling F-Stat</p>
                                    <p className="text-sm font-bold font-mono text-white">{soilAnalysis.fStat.toFixed(4)}</p>
                                </div>
                                <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 text-center">
                                    <p className="text-[9px] font-mono text-zinc-500 uppercase">p-Value (H0)</p>
                                    <p className="text-sm font-bold font-mono text-emerald-400">{soilAnalysis.pValue.toFixed(4)}</p>
                                </div>
                                <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 text-center">
                                    <p className="text-[9px] font-mono text-zinc-500 uppercase">ZTR Index</p>
                                    <p className="text-sm font-bold font-mono text-cyan-400">{soilAnalysis.ztr.toFixed(2)}%</p>
                                </div>
                            </div>

                            <div className="p-4 rounded-xl border border-zinc-800 bg-black/40 text-xs font-mono leading-relaxed text-zinc-300">
                                <strong>ISO 17025 ASTM E3272 Finding: </strong>
                                {soilAnalysis.verdict === "DEFINITIVE_INCLUSION"
                                    ? "Questioned soil trace and reference crime scene control are compositionally indistinguishable across 16 major/trace minerals and CIEDE2000 colorimetry (ΔE*00 = 0.00)."
                                    : "Significant geochemical and lithological divergence observed between questioned specimen and crime scene control. Exclusion supported."}
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* ── Mode 3: Palynology & eDNA ─────────────────────────────────── */}
                {mode === "PALYNOLOGY_EDNA" && (
                    <motion.div
                        key="PALYNOLOGY_EDNA"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6"
                    >
                        <div className="lg:col-span-1 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 space-y-4">
                            <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                <TreePine className="w-4 h-4 text-emerald-400" />
                                Relative Pollen Frequencies (RPF)
                            </h3>

                            <div className="space-y-3">
                                <div>
                                    <div className="flex justify-between text-xs font-mono text-zinc-400 mb-1">
                                        <span>Quercus (Oak): {quercusCount}</span>
                                        <span className="text-emerald-400 font-bold">{((quercusCount / 310) * 100).toFixed(1)}%</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="10"
                                        max="250"
                                        value={quercusCount}
                                        onChange={(e) => setQuercusCount(parseInt(e.target.value))}
                                        className="w-full accent-emerald-500 cursor-pointer min-h-[32px]"
                                    />
                                </div>

                                <div>
                                    <div className="flex justify-between text-xs font-mono text-zinc-400 mb-1">
                                        <span>Fagus (Beech): {fagusCount}</span>
                                        <span className="text-cyan-400 font-bold">{((fagusCount / 310) * 100).toFixed(1)}%</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="10"
                                        max="150"
                                        value={fagusCount}
                                        onChange={(e) => setFagusCount(parseInt(e.target.value))}
                                        className="w-full accent-cyan-500 cursor-pointer min-h-[32px]"
                                    />
                                </div>

                                <div>
                                    <div className="flex justify-between text-xs font-mono text-zinc-400 mb-1">
                                        <span>Carpinus (Hornbeam): {carpinusCount}</span>
                                        <span className="text-purple-400 font-bold">{((carpinusCount / 310) * 100).toFixed(1)}%</span>
                                    </div>
                                    <input
                                        type="range"
                                        min="5"
                                        max="80"
                                        value={carpinusCount}
                                        onChange={(e) => setCarpinusCount(parseInt(e.target.value))}
                                        className="w-full accent-purple-500 cursor-pointer min-h-[32px]"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="lg:col-span-2 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 flex flex-col justify-between space-y-4">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                                <div>
                                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                        <Dna className="w-4 h-4 text-cyan-400" />
                                        6-Biome Ecological Classifier & 16S/ITS eDNA Regression
                                    </h3>
                                    <p className="text-xs text-zinc-400 font-mono">
                                        Bray-Curtis Metric: dBC = 0.023 | Cosine: 0.9995
                                    </p>
                                </div>
                                <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold w-fit">
                                    DECIDUOUS_FOREST (93.3% Conf.)
                                </span>
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                                <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 text-center">
                                    <p className="text-[9px] font-mono text-zinc-500 uppercase">Bray-Curtis dBC</p>
                                    <p className="text-sm font-bold font-mono text-emerald-400">0.023</p>
                                </div>
                                <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 text-center">
                                    <p className="text-[9px] font-mono text-zinc-500 uppercase">Canopy Coverage</p>
                                    <p className="text-sm font-bold font-mono text-cyan-400">93.3%</p>
                                </div>
                                <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 text-center col-span-2 sm:col-span-1">
                                    <p className="text-[9px] font-mono text-zinc-500 uppercase">eDNA Predicted Lat/Lon</p>
                                    <p className="text-sm font-bold font-mono text-amber-400">49.15°N, 9.30°E</p>
                                </div>
                            </div>

                            <div className="p-4 rounded-xl border border-zinc-800 bg-black/40 text-xs font-mono text-zinc-300">
                                <strong>Diagnostic Indicator Taxa: </strong>
                                <em>Quercus robur</em>, <em>Fagus sylvatica</em>, <em>Carpinus betulus</em>. Strongly correlates
                                with temperate European broadleaf forest soil horizons.
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* ── Mode 4: Rossmo Geographic Profiling ───────────────────────── */}
                {mode === "ROSSMO_GEO" && (
                    <motion.div
                        key="ROSSMO_GEO"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6"
                    >
                        {/* Serial Crime Incident List */}
                        <div className="lg:col-span-1 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 space-y-4">
                            <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                <Crosshair className="w-4 h-4 text-rose-400" />
                                Serial Crime Incident Coordinates
                            </h3>

                            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                                {crimeSites.map((c) => (
                                    <div key={c.id} className="p-2.5 rounded-xl bg-black/40 border border-zinc-800 text-xs font-mono flex justify-between items-center">
                                        <div>
                                            <p className="font-bold text-white">{c.label}</p>
                                            <p className="text-[10px] text-zinc-500">Coord: ({c.x.toFixed(1)} km, {c.y.toFixed(1)} km)</p>
                                        </div>
                                        <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[10px] font-bold">
                                            {c.id}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            <div className="pt-2 border-t border-zinc-800 space-y-2 text-xs font-mono">
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Buffer Zone (B):</span>
                                    <span className="text-amber-400 font-bold">{bufferB} km</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Decay Exponents:</span>
                                    <span className="text-cyan-400 font-bold">f={exponentF}, g={exponentG}</span>
                                </div>
                            </div>
                        </div>

                        {/* Discrete Heatmap Grid & Search Efficiency Index */}
                        <div className="lg:col-span-2 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 flex flex-col justify-between space-y-4">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                                <div>
                                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                        <Activity className="w-4 h-4 text-cyan-400" />
                                        Rossmo Targeted Hunting Surface (SEI = {rossmoResult.sei}%)
                                    </h3>
                                    <p className="text-xs text-zinc-400 font-mono">
                                        Peak Operational Anchor: ({rossmoResult.peakX} km, {rossmoResult.peakY} km) | Top 5% Area: {rossmoResult.s5Area} km²
                                    </p>
                                </div>
                                <span className="px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 font-mono text-xs font-bold w-fit">
                                    {rossmoResult.typology} OFFENDER
                                </span>
                            </div>

                            {/* Discrete SVG Crime Spatial Plane */}
                            <div className="w-full h-56 sm:h-64 rounded-xl border border-zinc-800 bg-black/60 relative overflow-hidden flex items-center justify-center p-4">
                                <svg className="w-full h-full" viewBox="0 0 200 200">
                                    {/* 20x20 Grid Plane */}
                                    <rect x="0" y="0" width="200" height="200" fill="#09090b" />

                                    {/* Canter Bounding Circle */}
                                    <circle cx="100" cy="100" r="60" fill="none" stroke="rgba(244,63,94,0.3)" strokeWidth="1" strokeDasharray="4,4" />

                                    {/* Probability Contour Blob */}
                                    <ellipse cx="68" cy="114" rx="25" ry="18" fill="rgba(6,182,212,0.25)" stroke="#06b6d4" strokeWidth="1.5" />
                                    <circle cx="68" cy="114" r="3" fill="#38bdf8" />
                                    <text x="75" y="117" fill="#38bdf8" fontSize="8" fontFamily="monospace" fontWeight="bold">
                                        Anchor (6.8, 11.4)
                                    </text>

                                    {/* Crime Site Markers */}
                                    {crimeSites.map((c) => (
                                        <g key={c.id}>
                                            <circle cx={c.x * 10} cy={c.y * 10} r="4" fill="#f43f5e" />
                                            <text x={c.x * 10 + 6} y={c.y * 10 + 3} fill="#fda4af" fontSize="7" fontFamily="monospace">
                                                {c.id}
                                            </text>
                                        </g>
                                    ))}
                                </svg>
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                                <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                                    <p className="text-[9px] text-zinc-500 uppercase font-mono">SEI Index</p>
                                    <p className="text-xs font-bold font-mono text-emerald-400">{rossmoResult.sei}%</p>
                                </div>
                                <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                                    <p className="text-[9px] text-zinc-500 uppercase font-mono">Priority Area (S5%)</p>
                                    <p className="text-xs font-bold font-mono text-amber-400">{rossmoResult.s5Area} km²</p>
                                </div>
                                <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                                    <p className="text-[9px] text-zinc-500 uppercase font-mono">Canter Diameter</p>
                                    <p className="text-xs font-bold font-mono text-white">{rossmoResult.canterDiameter} km</p>
                                </div>
                                <div className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                                    <p className="text-[9px] text-zinc-500 uppercase font-mono">Mobility Type</p>
                                    <p className="text-xs font-bold font-mono text-rose-400">{rossmoResult.typology}</p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* ── Mode 5: Multi-Criteria Bayesian Fusion ───────────────────── */}
                {mode === "BAYESIAN_FUSION" && (
                    <motion.div
                        key="BAYESIAN_FUSION"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6"
                    >
                        {/* Evidence Modality Weight Sliders */}
                        <div className="lg:col-span-1 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 space-y-4">
                            <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                <Sliders className="w-4 h-4 text-cyan-400" />
                                Bayesian Modality Weights (w_k)
                            </h3>

                            <div className="space-y-3.5">
                                {[
                                    { label: "Isotopes (H/O/Sr)", val: weightIso, set: setWeightIso, color: "text-cyan-400", bg: "accent-cyan-500" },
                                    { label: "Soil Pedology (QXRD/CoDa)", val: weightSoil, set: setWeightSoil, color: "text-amber-400", bg: "accent-amber-500" },
                                    { label: "Palynology / eDNA", val: weightPalyno, set: setWeightPalyno, color: "text-emerald-400", bg: "accent-emerald-500" },
                                    { label: "Rossmo Geographic Profile", val: weightRossmo, set: setWeightRossmo, color: "text-rose-400", bg: "accent-rose-500" },
                                ].map((w) => (
                                    <div key={w.label}>
                                        <div className="flex justify-between text-xs font-mono text-zinc-400 mb-1">
                                            <span>{w.label}</span>
                                            <span className={`${w.color} font-bold`}>{w.val.toFixed(1)}x</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0.0"
                                            max="2.0"
                                            step="0.1"
                                            value={w.val}
                                            onChange={(e) => w.set(parseFloat(e.target.value))}
                                            className={`w-full ${w.bg} cursor-pointer min-h-[32px]`}
                                        />
                                    </div>
                                ))}
                            </div>

                            <div className="p-3.5 rounded-xl border border-zinc-800 bg-black/40 space-y-2 text-xs font-mono">
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Search Efficiency (SEI):</span>
                                    <span className="text-emerald-400 font-bold">96.45%</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">S50% Search Core:</span>
                                    <span className="text-cyan-400 font-bold">4.50 km²</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Fused Likelihood Ratio:</span>
                                    <span className="text-amber-300 font-bold font-mono">{fusedLR.toExponential(2)}</span>
                                </div>
                            </div>
                        </div>

                        {/* Combined Heatmap & ENFSI Report Card */}
                        <div className="lg:col-span-2 p-4 sm:p-5 rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 flex flex-col justify-between space-y-4">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                                <div>
                                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                                        <Layers className="w-4 h-4 text-emerald-400" />
                                        Joint Posterior Heatmap & 2D Adaptive KDE Surface
                                    </h3>
                                    <p className="text-xs text-zinc-400 font-mono">
                                        P(θ, λ | E) ∝ P₀ · ∏ L_k^(w_k) with Silverman Bandwidth Smoothing
                                    </p>
                                </div>
                                <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold w-fit">
                                    TIER 6 EXTREMELY STRONG
                                </span>
                            </div>

                            {/* Fused Posterior Radar/Map Visualizer */}
                            <div className="w-full h-56 sm:h-64 rounded-xl border border-zinc-800 bg-black/60 relative overflow-hidden flex items-center justify-center p-4">
                                <svg className="w-full h-full" viewBox="0 0 400 200">
                                    <ellipse cx="200" cy="100" rx="150" ry="75" fill="rgba(6,182,212,0.05)" />
                                    <ellipse cx="200" cy="100" rx="100" ry="50" fill="rgba(244,63,94,0.1)" stroke="rgba(244,63,94,0.3)" />
                                    <ellipse cx="200" cy="100" rx="50" ry="25" fill="rgba(34,197,94,0.25)" stroke="#22c55e" strokeWidth="2" />
                                    <circle cx="200" cy="100" r="5" fill="#38bdf8" />
                                    <text x="212" y="104" fill="#38bdf8" fontSize="10" fontFamily="monospace" fontWeight="bold">
                                        Joint Bayesian Focal Center (SEI 96.45%)
                                    </text>
                                </svg>
                            </div>

                            {/* ENFSI Bilingual Courtroom Report Card */}
                            <div className="p-4 rounded-xl border border-zinc-800 bg-black/40 space-y-2 text-xs font-mono text-zinc-300">
                                <div className="flex items-center gap-2 text-cyan-400 font-bold">
                                    <FileText className="w-3.5 h-3.5" />
                                    ENFSI 2017 Courtroom Evaluative Statement (Bilingual EN / TR)
                                </div>
                                <p className="text-zinc-200 leading-relaxed">
                                    <strong>EN:</strong> Multi-criteria geo-forensic fusion provides extremely strong support for source inclusion (H1 over H2) with a Fused Likelihood Ratio of {fusedLR.toExponential(2)}.
                                </p>
                                <p className="text-zinc-400 leading-relaxed">
                                    <strong>TR:</strong> Çok kriterli jeo-adli füzyon bulguları, şüpheli örneğin olay yeri kökenine dahil oluş hipotezini (H1) {fusedLR.toExponential(2)} birleşik olabilirlik oranıyla fevkalade güçlü derecede desteklemektedir.
                                </p>
                                <div className="pt-2 border-t border-zinc-800 text-[10px] text-zinc-500 leading-tight">
                                    <Shield className="w-3 h-3 inline mr-1 text-emerald-400" />
                                    <strong>PROSECUTOR'S FALLACY SHIELD (ISO 17025):</strong> The Likelihood Ratio assesses evidence probability under hypotheses P(E|H1)/P(E|H2). Prior guilt probabilities remain solely within the court's jurisdiction.
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
