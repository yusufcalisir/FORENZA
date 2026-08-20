"use client";

import { useForensicCaseStore } from "@/store/forensicCaseStore";
import { useIngestStore } from "@/store/ingestStore";
import { Dna, Eye, Globe, MapPin, Sliders, ArrowRight } from "lucide-react";
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
    const { activeCase } = useForensicCaseStore();
    const { activeProfile: storeProfile, setInspectorOpen } = useIngestStore();

    const activeProfile = storeProfile || activeCase?.profile;
    if (!activeProfile) return null;

    const dominantColor =
        activeProfile.sampleType === "EU" ? "#06B6D4" :
        activeProfile.sampleType === "AA" ? "#22C55E" :
        activeProfile.sampleType === "EAS" ? "#EC4899" :
        activeProfile.sampleType === "SAS" ? "#F59E0B" :
        activeProfile.sampleType === "DVI" ? "#8B5CF6" :
        activeProfile.sampleType === "TOUCH" ? "#F43F5E" : "#A855F7";

    const geoResults = [
        {
            region: `${activeProfile.geoLocation.country} (${activeProfile.geoLocation.cityRegion})`,
            lat: activeProfile.geoLocation.lat,
            lng: activeProfile.geoLocation.lng,
            probability: activeProfile.geoLocation.confidencePct / 100,
            color: dominantColor,
            initial_radius_km: 300,
            final_radius_km: 75,
        }
    ];

    return (
        <div className="rounded-2xl border border-cyan-500/40 bg-[#081220] p-3.5 sm:p-5 space-y-4 shadow-[0_0_40px_rgba(6,182,212,0.15)] relative overflow-hidden font-mono w-full max-w-full">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/80 pb-3">
                <div className="flex items-center gap-3 min-w-0">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-300">
                        <Dna className="w-5 h-5 animate-pulse" />
                    </div>
                    <div className="min-w-0 space-y-1">
                        <div className="flex items-center gap-2 flex-wrap">
                            <h3 className="text-xs sm:text-base font-extrabold text-white tracking-wider font-mono leading-tight break-words">
                                ACTIVE CASE: {activeProfile.profileId}
                            </h3>
                            <span className="px-2 py-0.5 rounded text-[8px] sm:text-[9px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shrink-0">
                                {activeProfile.sampleType} CASE
                            </span>
                        </div>
                        <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[9px] sm:text-[10px] text-zinc-400 font-mono">
                            <span>Node: <strong className="text-cyan-300">{activeProfile.nodeId}</strong></span>
                            <span className="text-zinc-600">•</span>
                            <span className="text-zinc-300 font-bold">{activeProfile.markerCount} Autosomal STR Loci (20 FBI Expanded CODIS + 4 Extended)</span>
                            <span className="text-zinc-600">•</span>
                            <span className="text-zinc-300 font-bold">55-SNP AIM Panel (Kidd et al. 2014)</span>
                        </div>
                    </div>
                </div>

                <button
                    onClick={() => setInspectorOpen(true)}
                    className="w-full sm:w-auto px-4 py-2 rounded-xl text-xs font-bold bg-cyan-500/20 border border-cyan-500/40 text-cyan-200 hover:bg-cyan-500/30 transition-all flex items-center justify-center gap-2 cursor-pointer shadow-[0_0_15px_rgba(6,182,212,0.2)] shrink-0 font-mono uppercase tracking-wider"
                >
                    <Sliders className="w-4 h-4 text-cyan-400" />
                    <span>Open DNA &amp; SNP Terminal</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                </button>
            </div>

            {/* Feature Highlights Grid (Strict Left-Aligned Fixed Key-Value Columns) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                {/* Card 1: Phenotype */}
                <div className="p-3.5 rounded-xl bg-black/50 border border-tactical-border/80 space-y-2">
                    <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-[11px] border-b border-tactical-border/50 pb-1.5">
                        <Eye className="w-3.5 h-3.5 shrink-0" />
                        <span>Inferred Phenotype</span>
                    </div>
                    <div className="grid grid-cols-[100px_1fr] items-center gap-y-1.5 gap-x-2 text-[10px]">
                        <span className="text-zinc-400 font-mono">Eye Color:</span>
                        <span className="font-bold text-cyan-300 font-mono truncate">{activeProfile.phenotype.eyeColor} ({activeProfile.phenotype.eyeColorProb}%)</span>

                        <span className="text-zinc-400 font-mono">Skin Phototype:</span>
                        <span className="font-bold text-amber-300 font-mono truncate">{activeProfile.phenotype.skinType}</span>

                        <span className="text-zinc-400 font-mono">Hair Texture:</span>
                        <span className="font-bold text-purple-300 font-mono truncate">{activeProfile.phenotype.hairType}</span>
                    </div>
                </div>

                {/* Card 2: Ancestry */}
                <div className="p-3.5 rounded-xl bg-black/50 border border-tactical-border/80 space-y-2">
                    <div className="flex items-center gap-1.5 text-cyan-400 font-bold text-[11px] border-b border-tactical-border/50 pb-1.5">
                        <Globe className="w-3.5 h-3.5 shrink-0" />
                        <span>Biogeographic Ancestry</span>
                    </div>
                    <div className="grid grid-cols-[100px_1fr] items-center gap-y-1.5 gap-x-2 text-[10px]">
                        <span className="text-zinc-400 font-mono">Primary:</span>
                        <span className="font-bold text-cyan-300 font-mono truncate">{activeProfile.ancestry.primary} ({activeProfile.ancestry.primaryPct}%)</span>

                        <span className="text-zinc-400 font-mono">Secondary:</span>
                        <span className="font-bold text-purple-300 font-mono truncate">{activeProfile.ancestry.secondary} ({activeProfile.ancestry.secondaryPct}%)</span>

                        <span className="text-zinc-400 font-mono">Cluster:</span>
                        <span className="font-bold text-white font-mono truncate">{activeProfile.ancestry.populationCluster}</span>
                    </div>
                </div>

                {/* Card 3: Geo Location */}
                <div className="p-3.5 rounded-xl bg-black/50 border border-tactical-border/80 space-y-2">
                    <div className="flex items-center gap-1.5 text-amber-400 font-bold text-[11px] border-b border-tactical-border/50 pb-1.5">
                        <MapPin className="w-3.5 h-3.5 shrink-0" />
                        <span>Estimated Geo-Location</span>
                    </div>
                    <div className="grid grid-cols-[100px_1fr] items-center gap-y-1.5 gap-x-2 text-[10px]">
                        <span className="text-zinc-400 font-mono">Coords:</span>
                        <span className="font-bold text-amber-300 font-mono truncate">{activeProfile.geoLocation.lat.toFixed(4)}° N, {activeProfile.geoLocation.lng.toFixed(4)}° E</span>

                        <span className="text-zinc-400 font-mono">Location:</span>
                        <span className="font-bold text-white font-mono truncate">{activeProfile.geoLocation.cityRegion}</span>

                        <span className="text-zinc-400 font-mono">Country:</span>
                        <span className="font-bold text-cyan-300 font-mono truncate">{activeProfile.geoLocation.country}</span>
                    </div>
                </div>
            </div>

            {/* Live GIS Map Visualizer (Isolated stacking context to prevent z-index bleed) */}
            <div className="w-full h-64 sm:h-72 rounded-xl overflow-hidden border border-tactical-border/60 relative z-0 isolate">
                <GeoForensicPanel
                    geoResults={geoResults}
                    reliabilityScore={activeProfile.geoLocation.confidencePct / 100}
                />
            </div>
        </div>
    );
}
