"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import TacticalPageHeader from "@/components/common/TacticalPageHeader";
import { GitGraph, ShieldAlert, Lock, Search, RefreshCw, Upload, CheckCircle } from "lucide-react";
import { useIngestStore } from "@/store/ingestStore";

import SystemPulse from "@/components/investigation/SystemPulse";
import CryptographicShield from "@/components/investigation/CryptographicShield";
import EmbeddedAuditLog from "@/components/investigation/EmbeddedAuditLog";
import InvestigatorSidebar from "@/components/investigation/InvestigatorSidebar";
import { MatchResultCardDemo } from "@/components/analysis/MatchResultCard";
import GeoForensicPanel from "@/components/analysis/GeoForensicPanel";
import ForensicGraphPanel from "@/components/investigation/ForensicGraphPanel";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function fetchAnalysis(profileId: string, population: string) {
    const res = await fetch(`${API_BASE}/profile/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile_id: profileId, population }),
    });
    if (!res.ok) throw new Error(`Analysis failed: ${res.status}`);
    return res.json();
}

export default function InvestigationDashboard() {
    // Session State
    const [panicMode, setPanicMode] = useState(false);

    // Analysis State
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [shieldActive, setShieldActive] = useState(false);
    const [zkpStatus, setZkpStatus] = useState<'idle' | 'generating' | 'verified' | 'failed'>('idle');
    const [analysisResult, setAnalysisResult] = useState<any | null>(null);
    const [activeProfileId, setActiveProfileId] = useState("test-profile-eu");

    const { setLastIngested } = useIngestStore();

    // ─── HANDLERS ─────────────────────────────────────────────────────────────

    const handlePanic = () => {
        setPanicMode(true);
        console.log("PANIC: Session Revoked, Token Purged, WebSocket Closed.");
    };

    const runInvestigation = useCallback(async () => {
        if (isAnalyzing) return;
        setIsAnalyzing(true);
        setShieldActive(true); // Trigger ZKP Animation
        setZkpStatus('generating');

        try {
            await new Promise(resolve => setTimeout(resolve, 2500));

            setZkpStatus('verified');
            setShieldActive(false);

            const data = await fetchAnalysis(activeProfileId, "European");
            setAnalysisResult(data);

            setLastIngested(activeProfileId, "FORENZA-NODE-01", 24);

        } catch (error) {
            console.error("Investigation Failed:", error);
            setZkpStatus('failed');
            setShieldActive(false);
        } finally {
            setIsAnalyzing(false);
        }
    }, [isAnalyzing, activeProfileId, setLastIngested]);

    const resetInvestigation = () => {
        setAnalysisResult(null);
        setZkpStatus('idle');
    };

    // ─── RENDER ───────────────────────────────────────────────────────────────

    if (panicMode) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-red-500 space-y-4 font-mono">
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="p-6 bg-red-500/10 rounded-full border border-red-500/20"
                >
                    <Lock className="w-12 h-12 animate-pulse" />
                </motion.div>
                <h1 className="text-xl font-bold tracking-[0.2em] uppercase">Session Terminated</h1>
                <div className="flex flex-col items-center space-y-1 text-zinc-500 font-mono text-xs">
                    <p>Blockchain Access Token Revoked</p>
                    <p>Local Key Material Shredded</p>
                    <p>Audit Log: <span className="text-red-400">EMERGENCY_EXIT_0x9F2A</span></p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col xl:flex-row gap-6 w-full max-w-full font-mono relative">
            {/* Main Content Area (Natural Page Flow - No inner scrollbar) */}
            <div className="flex-1 space-y-6 min-w-0">

                {/* ZKP Shield Overlay */}
                <AnimatePresence>
                    {shieldActive && <CryptographicShield active={shieldActive} />}
                </AnimatePresence>

                {/* Header & Panic */}
                <TacticalPageHeader
                    title="Forensic Investigation & Knowledge Graph"
                    subtitle="Relational Case Subgraph • Pedigree Kinship Traversal • Level 4 Cryptographic Clearance"
                    badge="PROPERTY GRAPH INSPECTOR"
                    icon={GitGraph}
                    accentColor="purple"
                    actions={
                        <button
                            onClick={handlePanic}
                            className="group flex items-center gap-2 px-3 py-1.5 bg-red-950/40 hover:bg-red-900/60 text-red-400 border border-red-900/60 rounded-xl transition-all font-mono text-xs font-bold uppercase tracking-wider cursor-pointer"
                        >
                            <ShieldAlert className="w-3.5 h-3.5 group-hover:animate-pulse" />
                            <span>Revoke Access</span>
                        </button>
                    }
                />

                {/* Module 1: System Pulse */}
                <SystemPulse />

                {/* Module 2: The Forensic Vault (Search vs Result) */}
                <div className="w-full">
                    <AnimatePresence mode="wait">
                        {!analysisResult ? (
                            <motion.div
                                key="search-mode"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="bg-tactical-surface/60 border border-tactical-border/70 rounded-2xl p-6 sm:p-10 flex flex-col items-center justify-center relative overflow-hidden group"
                            >
                                <div className="relative z-10 text-center space-y-6 max-w-lg">
                                    <div className="mx-auto w-16 h-16 bg-purple-500/10 rounded-2xl flex items-center justify-center border border-purple-500/30 shadow-xl group-hover:border-purple-500/60 transition-colors">
                                        <Search className="w-8 h-8 text-purple-400" />
                                    </div>

                                    <div className="space-y-2">
                                        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Forensic Vault Search</h2>
                                        <p className="text-zinc-400 text-xs leading-relaxed">
                                            Upload raw `.fsa` files or enter STR profile manually.
                                            <span className="text-emerald-400 block mt-2 font-mono text-[10px] font-bold border border-emerald-500/30 bg-emerald-500/10 py-1 px-2.5 rounded-lg inline-block">
                                                <Lock className="w-3 h-3 inline mr-1 mb-0.5" />
                                                Zero-Knowledge Proof Enabled
                                            </span>
                                        </p>
                                    </div>

                                    <div className="flex gap-4 justify-center">
                                        <button
                                            onClick={runInvestigation}
                                            disabled={isAnalyzing}
                                            className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-black font-extrabold rounded-xl transition-all flex items-center gap-2 text-xs font-mono uppercase tracking-wider cursor-pointer shadow-lg shadow-emerald-500/20"
                                        >
                                            {isAnalyzing ? (
                                                <>
                                                    <RefreshCw className="w-4 h-4 animate-spin" />
                                                    Processing Cryptography...
                                                </>
                                            ) : (
                                                <>
                                                    <Upload className="w-4 h-4" />
                                                    Upload DNA Profile
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="result-mode"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="flex flex-col lg:flex-row gap-6 w-full"
                            >
                                {/* Left: Match Stats */}
                                <div className="flex-1 space-y-4 min-w-0">
                                    <div className="flex justify-between items-center bg-tactical-surface/80 p-3 rounded-xl border border-tactical-border/70">
                                        <div className="flex items-center gap-2.5">
                                            <div className="w-8 h-8 rounded-xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/30">
                                                <CheckCircle className="w-4 h-4 text-emerald-400" />
                                            </div>
                                            <div>
                                                <h3 className="text-xs font-bold text-white">Match Verified</h3>
                                                <p className="text-[9px] text-zinc-400 font-mono">ZKP Hash: 0x9a7...3b2</p>
                                            </div>
                                        </div>
                                        <button
                                            onClick={resetInvestigation}
                                            className="text-xs text-zinc-400 hover:text-emerald-300 font-mono underline cursor-pointer"
                                        >
                                            New Search
                                        </button>
                                    </div>

                                    <div className="w-full max-w-full overflow-hidden">
                                        <MatchResultCardDemo />
                                    </div>
                                </div>

                                {/* Right: Geo-Forensic Intelligence */}
                                <div className="w-full lg:w-1/2 min-h-[450px]">
                                    <GeoForensicPanel
                                        geoResults={analysisResult?.geo_analysis_results || null}
                                        reliabilityScore={analysisResult?.geo_reliability_score || 0}
                                    />
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Forensic Knowledge Graph Subsystem */}
                <div className="pt-4 border-t border-tactical-border/60">
                    <ForensicGraphPanel />
                </div>

                {/* The Live Ledger */}
                <div className="pt-4 border-t border-tactical-border/60">
                    <EmbeddedAuditLog />
                </div>
            </div>

            {/* Sidebar: Agentic Intelligence */}
            <div className="w-full xl:w-80 shrink-0 border border-tactical-border/60 rounded-2xl bg-tactical-surface/60 overflow-hidden h-fit xl:sticky xl:top-20">
                <InvestigatorSidebar />
            </div>
        </div>
    );
}
