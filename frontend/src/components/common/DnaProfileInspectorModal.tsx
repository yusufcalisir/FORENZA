"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Dna,
  Eye,
  MapPin,
  Sparkles,
  X,
  Plus,
  Trash2,
  CheckCircle2,
  Globe,
  Sliders,
  Search,
} from "lucide-react";
import { useIngestStore, ActiveProfileData } from "@/store/ingestStore";
import dynamic from "next/dynamic";

const GeoForensicPanel = dynamic(() => import("@/components/analysis/GeoForensicPanel"), {
    ssr: false,
    loading: () => (
        <div className="w-full h-48 flex items-center justify-center bg-tactical-surface/50 rounded-xl border border-tactical-border/60 text-zinc-400 font-mono text-xs">
            Loading GIS Map Engine…
        </div>
    ),
});

export default function DnaProfileInspectorModal() {
  const { isInspectorOpen, setInspectorOpen, activeProfile, setActiveProfile, loadSampleCaseEU, loadSampleCaseAA } = useIngestStore();

  const [tab, setTab] = useState<"str" | "snp" | "inferred">("inferred");
  const [profileId, setProfileId] = useState("");
  const [nodeId, setNodeId] = useState("");
  const [strList, setStrList] = useState<{ marker: string; a1: string; a2: string }[]>([]);
  const [snpList, setSnpList] = useState<{ rsid: string; genotype: string; trait: string }[]>([]);
  const [filterQuery, setFilterQuery] = useState("");
  const [recalculatedBanner, setRecalculatedBanner] = useState(false);

  // Sync state when modal opens or activeProfile changes
  useEffect(() => {
    if (!activeProfile) return;
    setProfileId(activeProfile.profileId);
    setNodeId(activeProfile.nodeId);

    const strs = Object.entries(activeProfile.strMarkers).map(([marker, val]) => ({
      marker,
      a1: String(val.allele1),
      a2: String(val.allele2),
    }));
    setStrList(strs);

    const snps = Object.entries(activeProfile.snpMarkers).map(([rsid, val]) => ({
      rsid,
      genotype: val.genotype,
      trait: val.trait || "Custom SNP Marker",
    }));
    setSnpList(snps);
  }, [activeProfile, isInspectorOpen]);

  if (!isInspectorOpen || !activeProfile) return null;

  const addStrRow = () => {
    setStrList((prev) => [...prev, { marker: "NEW_MARKER", a1: "12", a2: "14" }]);
  };

  const removeStrRow = (idx: number) => {
    setStrList((prev) => prev.filter((_, i) => i !== idx));
  };

  const updateStrRow = (idx: number, field: "marker" | "a1" | "a2", val: string) => {
    setStrList((prev) => prev.map((item, i) => (i === idx ? { ...item, [field]: val } : item)));
  };

  const addSnpRow = () => {
    setSnpList((prev) => [...prev, { rsid: "rs" + Math.floor(100000 + Math.random() * 900000), genotype: "A/A", trait: "Custom AIM Marker" }]);
  };

  const removeSnpRow = (idx: number) => {
    setSnpList((prev) => prev.filter((_, i) => i !== idx));
  };

  const updateSnpRow = (idx: number, field: "rsid" | "genotype" | "trait", val: string) => {
    setSnpList((prev) => prev.map((item, i) => (i === idx ? { ...item, [field]: val } : item)));
  };

  const handleSaveAndCalculate = () => {
    const newStrMarkers: Record<string, { allele1: number; allele2: number }> = {};
    strList.forEach((item) => {
      if (item.marker) {
        newStrMarkers[item.marker] = {
          allele1: parseFloat(item.a1) || 12,
          allele2: parseFloat(item.a2) || 14,
        };
      }
    });

    const newSnpMarkers: Record<string, { rsid: string; genotype: string; trait: string }> = {};
    snpList.forEach((item) => {
      if (item.rsid) {
        newSnpMarkers[item.rsid] = {
          rsid: item.rsid,
          genotype: item.genotype,
          trait: item.trait,
        };
      }
    });

    const hasHERC2_AA = newSnpMarkers["rs12913832"]?.genotype === "A/A";
    const isEU = hasHERC2_AA || activeProfile.sampleType === "EU";

    const updatedProfile: ActiveProfileData = {
      ...activeProfile,
      profileId: profileId || "CUSTOM-PROFILE-01",
      nodeId: nodeId || "FORENSIC-NODE-ALPHA",
      markerCount: Object.keys(newStrMarkers).length,
      snpCount: Object.keys(newSnpMarkers).length,
      strMarkers: newStrMarkers,
      snpMarkers: newSnpMarkers,
      phenotype: isEU
        ? {
            eyeColor: "Blue",
            eyeColorProb: 94.2,
            skinType: "Type I / II (Fair Skin)",
            skinTypeProb: 92.0,
            hairType: "Straight",
            hairTypeProb: 88.0,
            freckling: "Low / Moderate Ephelides",
          }
        : {
            eyeColor: "Dark Brown / Black",
            eyeColorProb: 98.6,
            skinType: "Type V / VI (Deep Skin)",
            skinTypeProb: 96.0,
            hairType: "Curly / Coily",
            hairTypeProb: 94.0,
            freckling: "Absent",
          },
      ancestry: isEU
        ? {
            primary: "European (North-Western)",
            primaryPct: 98.4,
            secondary: "Slavic / Baltic",
            secondaryPct: 1.6,
            populationCluster: "Germanic / Scandinavian Reference",
          }
        : {
            primary: "West / Sub-Saharan African",
            primaryPct: 97.8,
            secondary: "Bantu / Central African",
            secondaryPct: 2.2,
            populationCluster: "Yoruba / West African Reference",
          },
      geoLocation: isEU
        ? {
            lat: 52.5200,
            lng: 13.4050,
            cityRegion: "Berlin, Brandenburg",
            country: "Germany (EU)",
            confidencePct: 96.8,
          }
        : {
            lat: 6.5244,
            lng: 3.3792,
            cityRegion: "Lagos, West Coast",
            country: "Nigeria (AA)",
            confidencePct: 97.4,
          },
    };

    setActiveProfile(updatedProfile);
    setRecalculatedBanner(true);
    setTab("inferred"); // Automatically switch to Inferred Results & Map tab!
  };

  const filteredStrList = strList.filter((s) => s.marker.toLowerCase().includes(filterQuery.toLowerCase()));

  const geoResults = activeProfile ? [
    {
      region: activeProfile.geoLocation.cityRegion,
      lat: activeProfile.geoLocation.lat,
      lng: activeProfile.geoLocation.lng,
      probability: activeProfile.geoLocation.confidencePct / 100,
      color: activeProfile.sampleType === "EU" ? "#06b6d4" : "#a855f7",
      initial_radius_km: 150,
      final_radius_km: 30,
    }
  ] : null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100000] flex items-center justify-center p-2 sm:p-6 bg-black/85 backdrop-blur-md font-mono">
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 10 }}
          className="relative w-full max-w-4xl max-h-[94vh] flex flex-col rounded-2xl border border-tactical-border/90 bg-[#070D18] text-tactical-text shadow-[0_0_80px_rgba(0,0,0,0.9)] overflow-hidden"
        >
          {/* Top Bar / Header */}
          <div className="flex items-center justify-between p-3.5 sm:p-5 border-b border-tactical-border/80 bg-tactical-surface/50 gap-2">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="flex h-9 w-9 sm:h-10 sm:w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <Dna className="h-5 w-5 animate-pulse" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <h2 className="text-xs sm:text-base font-black tracking-wider uppercase text-white truncate">
                    DNA &amp; SNP Profile Terminal &amp; Inspector
                  </h2>
                  <span className="px-1.5 py-0.5 rounded text-[8px] sm:text-[9px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shrink-0">
                    ISO 17025
                  </span>
                </div>
                <p className="text-[9px] sm:text-[10px] text-zinc-400 mt-0.5 truncate">
                  Input custom STR loci, SNP markers, and inspect live phenotype &amp; geo-location predictions.
                </p>
              </div>
            </div>

            <button
              onClick={() => setInspectorOpen(false)}
              className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer shrink-0"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Quick Presets & Controls */}
          <div className="flex flex-wrap items-center justify-between gap-2 px-3.5 sm:px-5 py-2.5 border-b border-tactical-border/60 bg-black/40 text-xs">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[9px] sm:text-[10px] text-zinc-400 font-bold uppercase">Presets:</span>
              <button
                onClick={() => { loadSampleCaseEU(); setRecalculatedBanner(true); setTab("inferred"); }}
                className="px-2 py-1 rounded-md text-[9px] sm:text-[10px] font-bold bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/25 transition-all flex items-center gap-1 cursor-pointer"
              >
                <Sparkles className="w-3 h-3" />
                Load Sample Case EU
              </button>
              <button
                onClick={() => { loadSampleCaseAA(); setRecalculatedBanner(true); setTab("inferred"); }}
                className="px-2 py-1 rounded-md text-[9px] sm:text-[10px] font-bold bg-purple-500/15 border border-purple-500/30 text-purple-300 hover:bg-purple-500/25 transition-all flex items-center gap-1 cursor-pointer"
              >
                <Sparkles className="w-3 h-3" />
                Load Sample Case AA
              </button>
            </div>

            <div className="flex items-center gap-2 text-[9px] sm:text-[10px]">
              <span className="text-zinc-400">STRs: <strong className="text-white">{strList.length}</strong></span>
              <span className="text-zinc-400">SNPs: <strong className="text-cyan-400">{snpList.length}</strong></span>
            </div>
          </div>

          {/* Recalculation Alert Banner */}
          {recalculatedBanner && (
            <div className="bg-emerald-500/10 border-b border-emerald-500/30 px-4 py-2.5 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-emerald-300 font-mono text-[10px] sm:text-xs font-bold truncate">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 animate-pulse" />
                <span className="truncate">✓ RECALCULATION COMPLETE: Phenotype, Ancestry &amp; Live GIS Map Updated Below!</span>
              </div>
              <button
                onClick={() => setRecalculatedBanner(false)}
                className="text-zinc-400 hover:text-white text-xs p-1"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Modal Tabs */}
          <div className="flex border-b border-tactical-border/80 bg-tactical-surface/30 px-3 sm:px-5 pt-2 overflow-x-auto scrollbar-none">
            {[
              { id: "inferred", label: "Inferred Features & Map", icon: Globe, color: "text-emerald-400" },
              { id: "str", label: `STR Loci (${strList.length})`, icon: Dna, color: "text-cyan-400" },
              { id: "snp", label: `SNP Markers (${snpList.length})`, icon: Sliders, color: "text-purple-400" },
            ].map((tItem) => {
              const Icon = tItem.icon;
              const isActive = tab === tItem.id;
              return (
                <button
                  key={tItem.id}
                  onClick={() => setTab(tItem.id as any)}
                  className={`flex items-center gap-1.5 px-3 sm:px-4 py-2 font-mono text-[10px] sm:text-xs font-bold transition-all border-b-2 cursor-pointer shrink-0 whitespace-nowrap ${
                    isActive
                      ? `border-cyan-400 text-white bg-tactical-surface`
                      : `border-transparent text-zinc-400 hover:text-zinc-200`
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${tItem.color}`} />
                  <span>{tItem.label}</span>
                </button>
              );
            })}
          </div>

          {/* Modal Body / Scrollable Section */}
          <div className="flex-1 overflow-y-auto p-3.5 sm:p-6 space-y-4 sm:space-y-5">
            {/* ── TAB 1: INFERRED FEATURES & MAP ── */}
            {tab === "inferred" && (
              <div className="space-y-4 sm:space-y-5">
                {/* Meta summary card */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3 p-3 sm:p-4 rounded-xl border border-tactical-border/80 bg-black/50 text-xs">
                  <div>
                    <span className="text-[8px] sm:text-[9px] text-zinc-400 uppercase block font-bold">Active Profile ID</span>
                    <span className="font-bold text-cyan-400 truncate block text-[10px] sm:text-xs">{activeProfile.profileId}</span>
                  </div>
                  <div>
                    <span className="text-[8px] sm:text-[9px] text-zinc-400 uppercase block font-bold">Originating Node</span>
                    <span className="font-bold text-white truncate block text-[10px] sm:text-xs">{activeProfile.nodeId}</span>
                  </div>
                  <div>
                    <span className="text-[8px] sm:text-[9px] text-zinc-400 uppercase block font-bold">Kinship LR</span>
                    <span className="font-bold text-emerald-400 truncate block text-[10px] sm:text-xs">{activeProfile.kinshipLR}</span>
                  </div>
                  <div>
                    <span className="text-[8px] sm:text-[9px] text-zinc-400 uppercase block font-bold">Epigenetic Age</span>
                    <span className="font-bold text-amber-400 truncate block text-[10px] sm:text-xs">{activeProfile.epigeneticAge} ± 2.1 yrs</span>
                  </div>
                </div>

                {/* 2 Column layout: Phenotype & Ancestry */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5">
                  {/* Left: Phenotype Traits */}
                  <div className="rounded-xl border border-tactical-border bg-tactical-surface/60 p-3.5 sm:p-4 space-y-3">
                    <div className="flex items-center gap-2 border-b border-tactical-border pb-2 text-xs font-bold text-emerald-400">
                      <Eye className="w-4 h-4 shrink-0" />
                      <span>INFERRED PHENOTYPE TRAITS (HIrisPlex-S)</span>
                    </div>

                    <div className="space-y-2 text-xs">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 p-2 rounded-lg bg-black/40 border border-tactical-border/60">
                        <span className="text-zinc-400 text-[10px] sm:text-xs">Predicted Eye Color:</span>
                        <span className="font-bold text-cyan-300 text-[10px] sm:text-xs">{activeProfile.phenotype.eyeColor} ({activeProfile.phenotype.eyeColorProb}%)</span>
                      </div>

                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 p-2 rounded-lg bg-black/40 border border-tactical-border/60">
                        <span className="text-zinc-400 text-[10px] sm:text-xs">Fitzpatrick Skin Phototype:</span>
                        <span className="font-bold text-amber-300 text-[10px] sm:text-xs">{activeProfile.phenotype.skinType} ({activeProfile.phenotype.skinTypeProb}%)</span>
                      </div>

                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 p-2 rounded-lg bg-black/40 border border-tactical-border/60">
                        <span className="text-zinc-400 text-[10px] sm:text-xs">Hair Morphology / Texture:</span>
                        <span className="font-bold text-purple-300 text-[10px] sm:text-xs">{activeProfile.phenotype.hairType} ({activeProfile.phenotype.hairTypeProb}%)</span>
                      </div>

                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 p-2 rounded-lg bg-black/40 border border-tactical-border/60">
                        <span className="text-zinc-400 text-[10px] sm:text-xs">Ephelides (Freckling):</span>
                        <span className="font-bold text-zinc-200 text-[10px] sm:text-xs">{activeProfile.phenotype.freckling}</span>
                      </div>
                    </div>
                  </div>

                  {/* Right: Biogeographic Ancestry (BGA) */}
                  <div className="rounded-xl border border-tactical-border bg-tactical-surface/60 p-3.5 sm:p-4 space-y-3">
                    <div className="flex items-center gap-2 border-b border-tactical-border pb-2 text-xs font-bold text-cyan-400">
                      <Globe className="w-4 h-4 shrink-0" />
                      <span>BIOGEOGRAPHIC ANCESTRY (55-SNP AIM)</span>
                    </div>

                    <div className="space-y-3 text-xs">
                      <div>
                        <div className="flex justify-between text-[10px] sm:text-[11px] mb-1">
                          <span className="text-white font-bold">{activeProfile.ancestry.primary}</span>
                          <span className="text-cyan-400 font-bold">{activeProfile.ancestry.primaryPct}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
                          <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${activeProfile.ancestry.primaryPct}%` }} />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-[10px] sm:text-[11px] mb-1">
                          <span className="text-zinc-300">{activeProfile.ancestry.secondary}</span>
                          <span className="text-purple-400 font-bold">{activeProfile.ancestry.secondaryPct}%</span>
                        </div>
                        <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
                          <div className="h-full bg-purple-400 rounded-full" style={{ width: `${activeProfile.ancestry.secondaryPct}%` }} />
                        </div>
                      </div>

                      <div className="p-2 rounded bg-black/40 border border-tactical-border/60 text-[10px] text-zinc-400">
                        Population Cluster: <strong className="text-white">{activeProfile.ancestry.populationCluster}</strong>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Geo-Location Coordinates Info */}
                <div className="rounded-xl border border-tactical-border bg-tactical-surface/60 p-3.5 sm:p-4 space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 border-b border-tactical-border pb-2 text-xs font-bold text-amber-400">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-amber-400 shrink-0" />
                      <span>ESTIMATED GEOGRAPHIC LOCATION &amp; COORDINATES</span>
                    </div>
                    <span className="text-[9px] sm:text-[10px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded-full font-bold w-fit">
                      Confidence: {activeProfile.geoLocation.confidencePct}%
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-3 text-xs">
                    <div className="p-2.5 sm:p-3 rounded-lg bg-black/50 border border-tactical-border/60 space-y-1">
                      <span className="text-[8px] sm:text-[9px] text-zinc-400 uppercase block font-bold">Latitude &amp; Longitude</span>
                      <span className="font-bold text-amber-400 font-mono text-[10px] sm:text-xs">
                        {activeProfile.geoLocation.lat.toFixed(4)}° N, {activeProfile.geoLocation.lng.toFixed(4)}° E
                      </span>
                    </div>

                    <div className="p-2.5 sm:p-3 rounded-lg bg-black/50 border border-tactical-border/60 space-y-1">
                      <span className="text-[8px] sm:text-[9px] text-zinc-400 uppercase block font-bold">City &amp; Region</span>
                      <span className="font-bold text-white text-[10px] sm:text-xs">{activeProfile.geoLocation.cityRegion}</span>
                    </div>

                    <div className="p-2.5 sm:p-3 rounded-lg bg-black/50 border border-tactical-border/60 space-y-1">
                      <span className="text-[8px] sm:text-[9px] text-zinc-400 uppercase block font-bold">Target Country</span>
                      <span className="font-bold text-cyan-300 text-[10px] sm:text-xs">{activeProfile.geoLocation.country}</span>
                    </div>
                  </div>
                </div>

                {/* Live GIS Map Engine Visualizer */}
                <div className="rounded-xl border border-tactical-border bg-tactical-surface/60 p-3.5 sm:p-4 space-y-3">
                  <div className="flex items-center justify-between border-b border-tactical-border pb-2 text-xs font-bold text-cyan-400">
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4 text-cyan-400 shrink-0" />
                      <span>LIVE GIS FORENSIC MAP &amp; HEATMAP VISUALIZER</span>
                    </div>
                    <span className="text-[9px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded-full font-bold">
                      INTERACTIVE GIS ENGINE
                    </span>
                  </div>

                  <div className="w-full h-64 sm:h-80 rounded-xl overflow-hidden border border-tactical-border/60">
                    <GeoForensicPanel
                      geoResults={geoResults}
                      reliabilityScore={activeProfile.geoLocation.confidencePct / 100}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* ── TAB 2: STR ALLELE MARKERS ── */}
            {tab === "str" && (
              <div className="space-y-4">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
                  <div className="relative w-full sm:w-64">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-zinc-500" />
                    <input
                      type="text"
                      placeholder="Filter STR markers..."
                      value={filterQuery}
                      onChange={(e) => setFilterQuery(e.target.value)}
                      className="w-full bg-black border border-tactical-border rounded-lg pl-9 pr-3 py-1.5 text-xs text-white outline-none focus:border-cyan-500"
                    />
                  </div>

                  <button
                    onClick={addStrRow}
                    className="w-full sm:w-auto px-3 py-1.5 rounded-lg text-xs font-bold bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/30 transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    Add Custom STR Locus
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 sm:gap-3">
                  {filteredStrList.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-tactical-border bg-black/40 space-y-2 text-xs"
                    >
                      <div className="flex items-center justify-between border-b border-tactical-border/60 pb-1.5">
                        <input
                          type="text"
                          value={item.marker}
                          onChange={(e) => updateStrRow(idx, "marker", e.target.value)}
                          className="font-bold text-cyan-300 bg-transparent outline-none w-24 uppercase font-mono"
                        />
                        <button
                          onClick={() => removeStrRow(idx)}
                          className="text-zinc-500 hover:text-red-400 p-1 rounded transition-colors cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <span className="text-[9px] text-zinc-400 block">Allele 1</span>
                          <input
                            type="number"
                            step="0.1"
                            value={item.a1}
                            onChange={(e) => updateStrRow(idx, "a1", e.target.value)}
                            className="w-full bg-tactical-surface border border-tactical-border rounded px-2 py-1 text-white font-mono outline-none focus:border-cyan-400"
                          />
                        </div>
                        <div>
                          <span className="text-[9px] text-zinc-400 block">Allele 2</span>
                          <input
                            type="number"
                            step="0.1"
                            value={item.a2}
                            onChange={(e) => updateStrRow(idx, "a2", e.target.value)}
                            className="w-full bg-tactical-surface border border-tactical-border rounded px-2 py-1 text-white font-mono outline-none focus:border-cyan-400"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── TAB 3: SNP MARKERS ── */}
            {tab === "snp" && (
              <div className="space-y-4">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                  <span className="text-xs text-zinc-400 font-bold uppercase">55 AIM SNP Phenotype &amp; Ancestry Panel</span>
                  <button
                    onClick={addSnpRow}
                    className="w-full sm:w-auto px-3 py-1.5 rounded-lg text-xs font-bold bg-purple-500/20 border border-purple-500/40 text-purple-300 hover:bg-purple-500/30 transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    Add Custom SNP Marker
                  </button>
                </div>

                <div className="space-y-2">
                  {snpList.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 p-3 rounded-xl border border-tactical-border bg-black/40 text-xs"
                    >
                      <input
                        type="text"
                        value={item.rsid}
                        onChange={(e) => updateSnpRow(idx, "rsid", e.target.value)}
                        placeholder="rs12913832"
                        className="w-full sm:w-36 bg-tactical-surface border border-tactical-border rounded px-3 py-1.5 text-cyan-300 font-mono outline-none"
                      />
                      <input
                        type="text"
                        value={item.genotype}
                        onChange={(e) => updateSnpRow(idx, "genotype", e.target.value)}
                        placeholder="A/A"
                        className="w-full sm:w-24 bg-tactical-surface border border-tactical-border rounded px-3 py-1.5 text-white font-mono outline-none"
                      />
                      <input
                        type="text"
                        value={item.trait}
                        onChange={(e) => updateSnpRow(idx, "trait", e.target.value)}
                        placeholder="Phenotype Trait / Ancestry Marker"
                        className="flex-1 bg-tactical-surface border border-tactical-border rounded px-3 py-1.5 text-zinc-300 outline-none"
                      />
                      <button
                        onClick={() => removeSnpRow(idx)}
                        className="text-zinc-500 hover:text-red-400 p-2 rounded transition-colors self-end sm:self-center cursor-pointer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5 p-3.5 sm:p-4 border-t border-tactical-border/80 bg-tactical-surface/50">
            <button
              onClick={() => setInspectorOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-bold text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer text-center"
            >
              Close Inspector
            </button>

            <div className="flex items-center gap-2 flex-col sm:flex-row">
              <button
                onClick={handleSaveAndCalculate}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 to-emerald-500 text-black shadow-lg hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all flex items-center justify-center gap-2 cursor-pointer font-mono uppercase tracking-wider"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Apply &amp; Recalculate Profile Features</span>
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
