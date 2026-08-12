"use client";

import { useIngestStore } from "@/store/ingestStore";
import { Dna, Eye, Globe, MapPin, Sliders, ArrowRight, CheckCircle2 } from "lucide-react";
import dynamic from "next/dynamic";

const GeoForensicPanel = dynamic(() => import("@/components/analysis/GeoForensicPanel"), {
    ssr: false,
    loading: () => (
        <div className="w-full h-48 flex items-center justify-center bg-tactical-surface/50 rounded-xl border border-tactical-border/60 text-zinc-400 font-mono text-xs">
            Loading GIS Map Engine…
        </div>
    ),
});

export default function ActiveProfileBanner() {
    const { activeProfile, setInspectorOpen } = useIngestStore();

    if (!activeProfile) return null;

    const geoResults = [
        {
            region: activeProfile.geoLocation.cityRegion,
            lat: activeProfile.geoLocation.lat,
            lng: activeProfile.geoLocation.lng,
            probability: activeProfile.geoLocation.confidencePct / 100,
            color: activeProfile.sampleType === "EU" ? "#06b6d4" : "#a855f7",
            initial_radius_km: 150,
            final_radius_km: 30,
        }
    ];

    return (
        <div className="rounded-2xl border border-cyan-500/40 bg-[#081220] p-4 sm:p-5 space-y-4 shadow-[0_0_40px_rgba(6,182,212,0.15)] relative overflow-hidden font-mono">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/80 pb-3">
                <div className="flex items-center gap-3 min-w-0">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-300">
                        <Dna className="w-5 h-5 animate-pulse" />
                    </div>
                    <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                            <h3 className="text-xs sm:text-base font-extrabold text-white tracking-wider truncate">
                                ACTIVE CASE: {activeProfile.profileId}
                            </h3>
                            <span className="px-2 py-0.5 rounded text-[8px] sm:text-[9px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                                {activeProfile.sampleType} CASE
                            </span>
                        </div>
                        <p className="text-[9px] sm:text-[10px] text-zinc-400 mt-0.5 truncate">
                            Node: <span className="text-cyan-300 font-bold">{activeProfile.nodeId}</span> • {activeProfile.markerCount} CODIS Loci • {activeProfile.snpCount} AIM SNPs
                        </p>
                    </div>
                </div>

                <button
                    onClick={() => setInspectorOpen(true)}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500/20 border border-cyan-500/40 text-cyan-200 hover:bg-cyan-500/30 transition-all flex items-center justify-center gap-2 cursor-pointer shadow-[0_0_15px_rgba(6,182,212,0.2)] shrink-0"
                >
                    <Sliders className="w-4 h-4 text-cyan-400" />
                    <span>Open DNA &amp; SNP Terminal</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                </button>
            </div>

            {/* Feature Highlights Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                {/* Phenotype */}
                <div className="p-3 rounded-xl bg-black/50 border border-tactical-border/80 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-[11px]">
                        <Eye className="w-3.5 h-3.5 shrink-0" />
                        <span>Inferred Phenotype</span>
                    </div>
                    <div className="space-y-1 text-[10px]">
                        <p className="flex justify-between">
                            <span className="text-zinc-400">Eye Color:</span>
                            <strong className="text-cyan-300">{activeProfile.phenotype.eyeColor} ({activeProfile.phenotype.eyeColorProb}%)</strong>
                        </p>
                        <p className="flex justify-between">
                            <span className="text-zinc-400">Skin Phototype:</span>
                            <strong className="text-amber-300">{activeProfile.phenotype.skinType}</strong>
                        </p>
                        <p className="flex justify-between">
                            <span className="text-zinc-400">Hair Morphology:</span>
                            <strong className="text-purple-300">{activeProfile.phenotype.hairType}</strong>
                        </p>
                    </div>
                </div>

                {/* Ancestry */}
                <div className="p-3 rounded-xl bg-black/50 border border-tactical-border/80 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-cyan-400 font-bold text-[11px]">
                        <Globe className="w-3.5 h-3.5 shrink-0" />
                        <span>Biogeographic Ancestry</span>
                    </div>
                    <div className="space-y-1 text-[10px]">
                        <p className="flex justify-between">
                            <span className="text-zinc-400">Primary:</span>
                            <strong className="text-cyan-300">{activeProfile.ancestry.primary} ({activeProfile.ancestry.primaryPct}%)</strong>
                        </p>
                        <p className="flex justify-between">
                            <span className="text-zinc-400">Secondary:</span>
                            <span className="text-purple-300 font-bold">{activeProfile.ancestry.secondary} ({activeProfile.ancestry.secondaryPct}%)</span>
                        </p>
                        <p className="text-[9px] text-zinc-400 truncate mt-1">
                            Cluster: <span className="text-white font-bold">{activeProfile.ancestry.populationCluster}</span>
                        </p>
                    </div>
                </div>

                {/* Geo Location & Map */}
                <div className="p-3 rounded-xl bg-black/50 border border-tactical-border/80 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-amber-400 font-bold text-[11px]">
                        <MapPin className="w-3.5 h-3.5 shrink-0" />
                        <span>Estimated Geo-Location</span>
                    </div>
                    <div className="space-y-1 text-[10px]">
                        <p className="flex justify-between">
                            <span className="text-zinc-400">Coords:</span>
                            <strong className="text-amber-300 font-mono">{activeProfile.geoLocation.lat.toFixed(4)}° N, {activeProfile.geoLocation.lng.toFixed(4)}° E</strong>
                        </p>
                        <p className="flex justify-between">
                            <span className="text-zinc-400">Location:</span>
                            <span className="text-white font-bold truncate">{activeProfile.geoLocation.cityRegion}</span>
                        </p>
                        <p className="flex justify-between">
                            <span className="text-zinc-400">Country:</span>
                            <span className="text-cyan-300 font-bold">{activeProfile.geoLocation.country}</span>
                        </p>
                    </div>
                </div>
            </div>

            {/* Live GIS Map Visualizer */}
            <div className="w-full h-56 rounded-xl overflow-hidden border border-tactical-border/60">
                <GeoForensicPanel
                    geoResults={geoResults}
                    reliabilityScore={activeProfile.geoLocation.confidencePct / 100}
                />
            </div>
        </div>
    );
}
