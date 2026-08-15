"use client";

import { useState, useEffect, useMemo } from "react";
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
  Activity,
  Layers,
  ShieldCheck,
  Check,
  RefreshCw,
} from "lucide-react";
import { useIngestStore, ActiveProfileData } from "@/store/ingestStore";
import { useForensicCaseStore } from "@/store/forensicCaseStore";
import dynamic from "next/dynamic";

const GeoForensicPanel = dynamic(() => import("@/components/analysis/GeoForensicPanel"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-64 flex flex-col items-center justify-center bg-tactical-surface/50 rounded-xl border border-tactical-border/60 text-zinc-400 font-mono text-xs gap-2">
      <RefreshCw className="w-5 h-5 text-cyan-400 animate-spin" />
      <span>Loading Interactive GIS Map Engine…</span>
    </div>
  ),
});

export default function DnaProfileInspectorModal() {
  const { isInspectorOpen, setInspectorOpen, activeProfile, setActiveProfile, loadSampleCaseEU, loadSampleCaseAA } = useIngestStore();

  const [tab, setTab] = useState<"inferred" | "str" | "snp">("inferred");
  const [profileId, setProfileId] = useState("");
  const [nodeId, setNodeId] = useState("");
  const [strList, setStrList] = useState<{ marker: string; a1: string; a2: string }[]>([]);
  const [snpList, setSnpList] = useState<{ rsid: string; genotype: string; trait: string }[]>([]);
  const [strSearch, setStrSearch] = useState("");
  const [snpSearch, setSnpSearch] = useState("");
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
  }, [activeProfile?.profileId, activeProfile?.sampleType, isInspectorOpen]);

  const filteredStrList = useMemo(() => {
    if (!strSearch) return strList;
    const q = strSearch.toLowerCase();
    return strList.filter((s) => s.marker.toLowerCase().includes(q));
  }, [strList, strSearch]);

  const filteredSnpList = useMemo(() => {
    if (!snpSearch) return snpList;
    const q = snpSearch.toLowerCase();
    return snpList.filter((s) => s.rsid.toLowerCase().includes(q) || s.trait.toLowerCase().includes(q) || s.genotype.toLowerCase().includes(q));
  }, [snpList, snpSearch]);

  if (!isInspectorOpen || !activeProfile) return null;

  const addStrRow = () => {
    setStrList((prev) => [...prev, { marker: "NEW_LOCUS", a1: "12", a2: "14" }]);
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
    useForensicCaseStore.getState().updateActiveProfile({
      profileId: updatedProfile.profileId,
      nodeId: updatedProfile.nodeId,
      markerCount: updatedProfile.markerCount,
      snpCount: updatedProfile.snpCount,
      sampleType: updatedProfile.sampleType,
      strMarkers: updatedProfile.strMarkers,
      snpMarkers: updatedProfile.snpMarkers,
      phenotype: updatedProfile.phenotype,
      ancestry: updatedProfile.ancestry,
      geoLocation: updatedProfile.geoLocation,
    });
    setRecalculatedBanner(true);
    setTab("inferred");
  };

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
      <div className="fixed inset-0 z-[100000] flex items-center justify-center p-2 sm:p-4 bg-black/85 backdrop-blur-md font-mono">
        <motion.div
          initial={{ opacity: 0, scale: 0.98, y: 8 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.98, y: 8 }}
          className="relative w-full h-[95vh] sm:h-auto sm:max-h-[92vh] sm:max-w-5xl flex flex-col rounded-2xl border border-tactical-border/80 bg-[#070D18] text-tactical-text shadow-[0_0_80px_rgba(0,0,0,0.9)] overflow-hidden"
        >
          {/* ── Top Bar / Header ── */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-tactical-border/70 bg-[#0a1120] shrink-0">
            <div className="flex items-center gap-3 min-w-0">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <Dna className="h-5 w-5 animate-pulse" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-xs sm:text-sm font-extrabold tracking-wider uppercase text-white font-mono">
                    DNA &amp; SNP Terminal
                  </h2>
                  <span className="px-1.5 py-0.2 rounded text-[8px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                    ISO/IEC 17025
                  </span>
                  <span className="px-1.5 py-0.2 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Active Profile
                  </span>
                </div>
                <p className="text-[10px] text-zinc-400 truncate">
                  Forensic Profile Management • STR Loci • AIM SNPs • Biogeographic Inference
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {/* Presets Button Pill */}
              <div className="hidden sm:flex items-center gap-1.5 p-1 rounded-xl bg-black/50 border border-tactical-border/60">
                <span className="text-[9px] text-zinc-500 uppercase px-1 font-bold">Presets:</span>
                <button
                  onClick={() => { loadSampleCaseEU(); setRecalculatedBanner(true); setTab("inferred"); }}
                  className="px-2 py-1 rounded-lg text-[9px] font-bold bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/25 transition-all flex items-center gap-1 cursor-pointer"
                  title="Load Northern European Benchmark Profile"
                >
                  <Sparkles className="w-2.5 h-2.5 text-cyan-400" />
                  <span>Sample EU</span>
                </button>
                <button
                  onClick={() => { loadSampleCaseAA(); setRecalculatedBanner(true); setTab("inferred"); }}
                  className="px-2 py-1 rounded-lg text-[9px] font-bold bg-purple-500/15 border border-purple-500/30 text-purple-300 hover:bg-purple-500/25 transition-all flex items-center gap-1 cursor-pointer"
                  title="Load West African Benchmark Profile"
                >
                  <Sparkles className="w-2.5 h-2.5 text-purple-400" />
                  <span>Sample AA</span>
                </button>
              </div>

              <button
                onClick={() => setInspectorOpen(false)}
                className="p-1.5 rounded-xl text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer"
                title="Close Terminal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* ── Mobile Presets Strip ── */}
          <div className="sm:hidden flex items-center justify-between px-3 py-1.5 border-b border-tactical-border/60 bg-black/40 text-[10px]">
            <span className="text-zinc-500 font-bold uppercase text-[9px]">Load Case Preset:</span>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => { loadSampleCaseEU(); setRecalculatedBanner(true); setTab("inferred"); }}
                className="px-2 py-0.5 rounded text-[9px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
              >
                Sample EU
              </button>
              <button
                onClick={() => { loadSampleCaseAA(); setRecalculatedBanner(true); setTab("inferred"); }}
                className="px-2 py-0.5 rounded text-[9px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30"
              >
                Sample AA
              </button>
            </div>
          </div>

          {/* ── Navigation Tab Bar ── */}
          <div className="flex items-center justify-between px-3 sm:px-4 border-b border-tactical-border/70 bg-[#080d19] shrink-0 overflow-x-auto">
            <div className="flex items-center gap-1 sm:gap-2 shrink-0">
              {[
                { id: "inferred", label: "Predictions & GIS Map", icon: Globe, badge: null, color: "text-emerald-400" },
                { id: "str", label: "STR Alleles", icon: Dna, badge: `${strList.length} Loci`, color: "text-cyan-400" },
                { id: "snp", label: "AIM SNPs", icon: Sliders, badge: `${snpList.length} SNPs`, color: "text-purple-400" },
              ].map((tItem) => {
                const Icon = tItem.icon;
                const isActive = tab === tItem.id;
                return (
                  <button
                    key={tItem.id}
                    onClick={() => setTab(tItem.id as any)}
                    className={`flex items-center gap-1.5 py-2.5 px-2.5 sm:px-3 font-mono text-[11px] sm:text-xs font-bold transition-all border-b-2 cursor-pointer whitespace-nowrap shrink-0 ${
                      isActive
                        ? "text-white border-cyan-400 bg-cyan-500/10"
                        : "text-zinc-400 border-transparent hover:text-zinc-200 hover:bg-white/5"
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? "text-cyan-400" : tItem.color}`} />
                    <span>{tItem.label}</span>
                    {tItem.badge && (
                      <span className={`text-[8px] px-1.5 py-0.2 rounded border font-mono ${
                        isActive
                          ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                          : "bg-black/50 text-zinc-400 border-tactical-border/60"
                      }`}>
                        {tItem.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            <div className="hidden md:flex items-center gap-3 text-[10px] text-zinc-400">
              <span>Node: <strong className="text-zinc-200">{activeProfile.nodeId}</strong></span>
              <span className="h-3 w-px bg-tactical-border/60" />
              <span>ID: <strong className="text-cyan-300">{activeProfile.profileId}</strong></span>
            </div>
          </div>

          {/* ── Recalculation Alert Toast ── */}
          {recalculatedBanner && (
            <div className="bg-emerald-500/10 border-b border-emerald-500/30 px-4 py-2 flex items-center justify-between gap-2 shrink-0">
              <div className="flex items-center gap-2 text-emerald-300 font-mono text-xs font-bold">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 animate-pulse" />
                <span>Forensic Features &amp; GIS Map Recalculated for {activeProfile.profileId}</span>
              </div>
              <button
                onClick={() => setRecalculatedBanner(false)}
                className="text-zinc-400 hover:text-white p-0.5 cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* ── Main Content Area ── */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono">
            {/* ════════════════════════════════════════════════════════════════════
                TAB 1: INFERRED FEATURES & GIS MAP
               ════════════════════════════════════════════════════════════════════ */}
            {tab === "inferred" && (
              <div className="space-y-4">
                {/* Profile Meta HUD Strip */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-3 rounded-xl border border-tactical-border/70 bg-black/40 text-xs">
                  <div className="space-y-0.5">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold tracking-wider">Active Case ID</span>
                    <p className="font-bold text-cyan-400 text-xs truncate">{activeProfile.profileId}</p>
                  </div>
                  <div className="space-y-0.5">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold tracking-wider">Originating Node</span>
                    <p className="font-bold text-white text-xs truncate">{activeProfile.nodeId}</p>
                  </div>
                  <div className="space-y-0.5">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold tracking-wider">Kinship LR Score</span>
                    <p className="font-bold text-emerald-400 text-xs truncate">{activeProfile.kinshipLR}</p>
                  </div>
                  <div className="space-y-0.5">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold tracking-wider">Epigenetic Horvath Age</span>
                    <p className="font-bold text-amber-400 text-xs truncate">{activeProfile.epigeneticAge} ± 2.1 yrs</p>
                  </div>
                </div>

                {/* 2-Column Balanced Dashboard */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                  {/* Left Column: Phenotype & Ancestry (5 cols) */}
                  <div className="lg:col-span-5 space-y-4">
                    {/* Phenotype Card */}
                    <div className="rounded-xl border border-tactical-border/70 bg-tactical-surface/50 p-3.5 space-y-2.5">
                      <div className="flex items-center justify-between border-b border-tactical-border/60 pb-2">
                        <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                          <Eye className="w-4 h-4 shrink-0" />
                          <span>HIrisPlex-S Phenotype</span>
                        </div>
                        <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-bold">
                          41-SNP Model
                        </span>
                      </div>

                      <div className="space-y-1.5 text-xs">
                        <div className="flex items-center justify-between p-2 rounded-lg bg-black/40 border border-tactical-border/40">
                          <span className="text-zinc-400 text-[10px]">Eye Color:</span>
                          <span className="font-bold text-cyan-300 text-[10px]">
                            {activeProfile.phenotype.eyeColor} ({activeProfile.phenotype.eyeColorProb}%)
                          </span>
                        </div>

                        <div className="flex items-center justify-between p-2 rounded-lg bg-black/40 border border-tactical-border/40">
                          <span className="text-zinc-400 text-[10px]">Skin Phototype:</span>
                          <span className="font-bold text-amber-300 text-[10px]">
                            {activeProfile.phenotype.skinType} ({activeProfile.phenotype.skinTypeProb}%)
                          </span>
                        </div>

                        <div className="flex items-center justify-between p-2 rounded-lg bg-black/40 border border-tactical-border/40">
                          <span className="text-zinc-400 text-[10px]">Hair Texture:</span>
                          <span className="font-bold text-purple-300 text-[10px]">
                            {activeProfile.phenotype.hairType} ({activeProfile.phenotype.hairTypeProb}%)
                          </span>
                        </div>

                        <div className="flex items-center justify-between p-2 rounded-lg bg-black/40 border border-tactical-border/40">
                          <span className="text-zinc-400 text-[10px]">Freckling:</span>
                          <span className="font-bold text-zinc-200 text-[10px]">
                            {activeProfile.phenotype.freckling}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Biogeographic Ancestry Card */}
                    <div className="rounded-xl border border-tactical-border/70 bg-tactical-surface/50 p-3.5 space-y-2.5">
                      <div className="flex items-center justify-between border-b border-tactical-border/60 pb-2">
                        <div className="flex items-center gap-2 text-xs font-bold text-cyan-400">
                          <Globe className="w-4 h-4 shrink-0" />
                          <span>Biogeographic Ancestry (BGA)</span>
                        </div>
                        <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-bold">
                          55-AIM SNPs
                        </span>
                      </div>

                      <div className="space-y-2.5 text-xs">
                        <div>
                          <div className="flex justify-between text-[10px] mb-1 font-bold">
                            <span className="text-white">{activeProfile.ancestry.primary}</span>
                            <span className="text-cyan-400">{activeProfile.ancestry.primaryPct}%</span>
                          </div>
                          <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                            <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${activeProfile.ancestry.primaryPct}%` }} />
                          </div>
                        </div>

                        <div>
                          <div className="flex justify-between text-[10px] mb-1 font-bold">
                            <span className="text-zinc-300">{activeProfile.ancestry.secondary}</span>
                            <span className="text-purple-400">{activeProfile.ancestry.secondaryPct}%</span>
                          </div>
                          <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                            <div className="h-full bg-purple-400 rounded-full" style={{ width: `${activeProfile.ancestry.secondaryPct}%` }} />
                          </div>
                        </div>

                        <div className="p-2 rounded-lg bg-black/40 border border-tactical-border/40 text-[10px] text-zinc-400">
                          Cluster: <strong className="text-white">{activeProfile.ancestry.populationCluster}</strong>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Geo Coordinates & Interactive Map (7 cols) */}
                  <div className="lg:col-span-7 space-y-4">
                    {/* Coordinates Strip */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                      <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60">
                        <span className="text-[8px] text-zinc-500 uppercase block font-bold">Coordinates</span>
                        <p className="font-bold text-amber-400 text-xs">
                          {activeProfile.geoLocation.lat.toFixed(4)}° N, {activeProfile.geoLocation.lng.toFixed(4)}° E
                        </p>
                      </div>

                      <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60">
                        <span className="text-[8px] text-zinc-500 uppercase block font-bold">City &amp; Region</span>
                        <p className="font-bold text-white text-xs truncate">{activeProfile.geoLocation.cityRegion}</p>
                      </div>

                      <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60">
                        <span className="text-[8px] text-zinc-500 uppercase block font-bold">Confidence</span>
                        <p className="font-bold text-emerald-400 text-xs">{activeProfile.geoLocation.confidencePct}% Match</p>
                      </div>
                    </div>

                    {/* Live GIS Map Visualizer */}
                    <div className="rounded-xl border border-tactical-border/70 bg-tactical-surface/50 p-3 space-y-2">
                      <div className="flex items-center justify-between text-xs font-bold text-cyan-400 pb-1">
                        <div className="flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                          <span>Forensic Geographic Mapping</span>
                        </div>
                        <span className="text-[9px] text-zinc-400">Target: {activeProfile.geoLocation.country}</span>
                      </div>

                      <div className="w-full h-64 sm:h-72 rounded-xl overflow-hidden border border-tactical-border/60">
                        <GeoForensicPanel
                          geoResults={geoResults}
                          reliabilityScore={activeProfile.geoLocation.confidencePct / 100}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ════════════════════════════════════════════════════════════════════
                TAB 2: STR ALLELE MARKERS (Structured Lab Table)
               ════════════════════════════════════════════════════════════════════ */}
            {tab === "str" && (
              <div className="space-y-3">
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
                  <div className="relative flex-1 max-w-sm">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                    <input
                      type="text"
                      placeholder="Search locus name (e.g. D3S1358, vWA)..."
                      value={strSearch}
                      onChange={(e) => setStrSearch(e.target.value)}
                      className="w-full bg-black/60 border border-tactical-border/70 rounded-xl pl-9 pr-3 py-2 text-xs text-white outline-none focus:border-cyan-500 font-mono"
                    />
                  </div>

                  <button
                    onClick={addStrRow}
                    className="px-3.5 py-2 rounded-xl text-xs font-bold bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/25 transition-all flex items-center justify-center gap-1.5 cursor-pointer font-mono shrink-0"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Custom STR Locus</span>
                  </button>
                </div>

                {/* Structured Table */}
                <div className="rounded-xl border border-tactical-border/70 bg-black/40 overflow-hidden">
                  <div className="max-h-[50vh] overflow-y-auto overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="sticky top-0 bg-[#0a101d] border-b border-tactical-border/80 text-zinc-400 text-[10px] uppercase tracking-wider select-none z-10">
                        <tr>
                          <th className="py-2.5 px-3 w-12 text-center">#</th>
                          <th className="py-2.5 px-3">Locus Marker</th>
                          <th className="py-2.5 px-3 w-32">Allele 1</th>
                          <th className="py-2.5 px-3 w-32">Allele 2</th>
                          <th className="py-2.5 px-3 w-28 text-center">Classification</th>
                          <th className="py-2.5 px-3 w-16 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-tactical-border/40 text-zinc-200">
                        {filteredStrList.length === 0 ? (
                          <tr>
                            <td colSpan={6} className="py-8 text-center text-zinc-500 text-xs">
                              No STR loci matching "{strSearch}".
                            </td>
                          </tr>
                        ) : (
                          filteredStrList.map((item, idx) => (
                            <tr key={idx} className="hover:bg-white/5 transition-colors">
                              <td className="py-2 px-3 text-center text-zinc-500 text-[10px]">
                                {idx + 1}
                              </td>
                              <td className="py-2 px-3">
                                <input
                                  type="text"
                                  value={item.marker}
                                  onChange={(e) => updateStrRow(idx, "marker", e.target.value)}
                                  className="font-bold text-cyan-300 bg-transparent outline-none w-32 uppercase font-mono px-1.5 py-0.5 rounded border border-transparent focus:border-cyan-500/50"
                                />
                              </td>
                              <td className="py-2 px-3">
                                <input
                                  type="number"
                                  step="0.1"
                                  value={item.a1}
                                  onChange={(e) => updateStrRow(idx, "a1", e.target.value)}
                                  className="w-24 bg-tactical-surface/80 border border-tactical-border/60 rounded px-2.5 py-1 text-white font-mono outline-none focus:border-cyan-400 text-xs"
                                />
                              </td>
                              <td className="py-2 px-3">
                                <input
                                  type="number"
                                  step="0.1"
                                  value={item.a2}
                                  onChange={(e) => updateStrRow(idx, "a2", e.target.value)}
                                  className="w-24 bg-tactical-surface/80 border border-tactical-border/60 rounded px-2.5 py-1 text-white font-mono outline-none focus:border-cyan-400 text-xs"
                                />
                              </td>
                              <td className="py-2 px-3 text-center">
                                <span className="text-[8px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-bold">
                                  CODIS 20
                                </span>
                              </td>
                              <td className="py-2 px-3 text-right">
                                <button
                                  onClick={() => removeStrRow(idx)}
                                  className="text-zinc-500 hover:text-red-400 p-1 rounded transition-colors cursor-pointer"
                                  title="Delete locus"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* ════════════════════════════════════════════════════════════════════
                TAB 3: SNP MARKERS (Structured AIM Table)
               ════════════════════════════════════════════════════════════════════ */}
            {tab === "snp" && (
              <div className="space-y-3">
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
                  <div className="relative flex-1 max-w-sm">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                    <input
                      type="text"
                      placeholder="Search rsID or trait (e.g. HERC2, EDAR)..."
                      value={snpSearch}
                      onChange={(e) => setSnpSearch(e.target.value)}
                      className="w-full bg-black/60 border border-tactical-border/70 rounded-xl pl-9 pr-3 py-2 text-xs text-white outline-none focus:border-purple-500 font-mono"
                    />
                  </div>

                  <button
                    onClick={addSnpRow}
                    className="px-3.5 py-2 rounded-xl text-xs font-bold bg-purple-500/15 border border-purple-500/30 text-purple-300 hover:bg-purple-500/25 transition-all flex items-center justify-center gap-1.5 cursor-pointer font-mono shrink-0"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Custom SNP Marker</span>
                  </button>
                </div>

                {/* Structured Table */}
                <div className="rounded-xl border border-tactical-border/70 bg-black/40 overflow-hidden">
                  <div className="max-h-[50vh] overflow-y-auto overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="sticky top-0 bg-[#0a101d] border-b border-tactical-border/80 text-zinc-400 text-[10px] uppercase tracking-wider select-none z-10">
                        <tr>
                          <th className="py-2.5 px-3 w-12 text-center">#</th>
                          <th className="py-2.5 px-3 w-36">rsID Marker</th>
                          <th className="py-2.5 px-3 w-28">Genotype</th>
                          <th className="py-2.5 px-3">Phenotype / Ancestry Trait Association</th>
                          <th className="py-2.5 px-3 w-16 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-tactical-border/40 text-zinc-200">
                        {filteredSnpList.length === 0 ? (
                          <tr>
                            <td colSpan={5} className="py-8 text-center text-zinc-500 text-xs">
                              No SNP markers matching "{snpSearch}".
                            </td>
                          </tr>
                        ) : (
                          filteredSnpList.map((item, idx) => (
                            <tr key={idx} className="hover:bg-white/5 transition-colors">
                              <td className="py-2 px-3 text-center text-zinc-500 text-[10px]">
                                {idx + 1}
                              </td>
                              <td className="py-2 px-3">
                                <input
                                  type="text"
                                  value={item.rsid}
                                  onChange={(e) => updateSnpRow(idx, "rsid", e.target.value)}
                                  placeholder="rs12913832"
                                  className="w-32 bg-tactical-surface/80 border border-tactical-border/60 rounded px-2.5 py-1 text-cyan-300 font-mono outline-none focus:border-cyan-400 text-xs"
                                />
                              </td>
                              <td className="py-2 px-3">
                                <input
                                  type="text"
                                  value={item.genotype}
                                  onChange={(e) => updateSnpRow(idx, "genotype", e.target.value)}
                                  placeholder="A/A"
                                  className="w-20 bg-tactical-surface/80 border border-tactical-border/60 rounded px-2.5 py-1 text-white font-mono outline-none focus:border-cyan-400 text-xs text-center font-bold"
                                />
                              </td>
                              <td className="py-2 px-3">
                                <input
                                  type="text"
                                  value={item.trait}
                                  onChange={(e) => updateSnpRow(idx, "trait", e.target.value)}
                                  placeholder="Phenotype Trait / Ancestry Marker"
                                  className="w-full bg-tactical-surface/80 border border-tactical-border/60 rounded px-2.5 py-1 text-zinc-300 outline-none focus:border-purple-400 text-xs"
                                />
                              </td>
                              <td className="py-2 px-3 text-right">
                                <button
                                  onClick={() => removeSnpRow(idx)}
                                  className="text-zinc-500 hover:text-red-400 p-1 rounded transition-colors cursor-pointer"
                                  title="Delete SNP"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* ── Footer Actions ── */}
          <div className="flex items-center justify-between gap-3 px-4 py-3 border-t border-tactical-border/70 bg-[#0a1120] shrink-0">
            <button
              onClick={() => setInspectorOpen(false)}
              className="px-4 py-2 rounded-xl text-xs font-bold text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer font-mono"
            >
              Close
            </button>

            <button
              onClick={handleSaveAndCalculate}
              className="px-5 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 via-teal-400 to-emerald-400 text-black shadow-lg hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all flex items-center gap-2 cursor-pointer font-mono uppercase tracking-wider font-extrabold"
            >
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>Apply &amp; Recalculate Features</span>
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
