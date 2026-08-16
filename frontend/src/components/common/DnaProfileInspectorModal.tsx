"use client";

import React, { useState, useEffect, useMemo, useRef } from "react";
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
  Download,
  Upload,
  FileCode,
  FileSpreadsheet,
  AlertTriangle,
  Flame,
  ChevronRight,
  SlidersHorizontal,
} from "lucide-react";
import { useIngestStore, ActiveProfileData } from "@/store/ingestStore";
import { useForensicCaseStore } from "@/store/forensicCaseStore";
import {
  GOLDEN_CASEWORK_PRESETS,
  exportToCodisXml,
  exportToLimsJson,
  exportToGeneMapperCsv,
  parseDroppedFileContent,
  ClientCaseworkPreset,
} from "@/utils/caseworkPresets";
import {
  calculateClientBgaPosterior,
  calculateClientHIrisPlex,
  AIM_55_SNPS_CATALOG,
  HIRISPLEX_41_SNPS_CATALOG,
  CONTINENTAL_COORDINATES,
  ContinentalCluster,
} from "@/utils/snpPhenotypeBgaEngine";
import type { GeoProbability } from "@/components/analysis/ForensicMap";
import {
  synthesizeClientEpg,
  EPG_DYE_COLORS,
  DyeChannelType,
  ClientEpgSynthesisResult,
} from "@/utils/epgSynthesisEngine";
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
  const {
    isInspectorOpen,
    setInspectorOpen,
    activeProfile,
    setActiveProfile,
    loadCaseworkPreset,
  } = useIngestStore();

  const [tab, setTab] = useState<"inferred" | "str" | "snp" | "epg">("inferred");
  const [profileId, setProfileId] = useState("");
  const [nodeId, setNodeId] = useState("");

  // STR List State
  const [strList, setStrList] = useState<
    { marker: string; a1: string; a2: string; rfu1: number; rfu2: number }[]
  >([]);

  // SNP Dosages State (rsID -> 0, 1, 2)
  const [snpDosages, setSnpDosages] = useState<Record<string, number>>({});

  // EPG Controls
  const [templateNg, setTemplateNg] = useState(1.0);
  const [degradationRate, setDegradationRate] = useState(0.0);
  const [includeStutter, setIncludeStutter] = useState(true);
  const [activeDyes, setActiveDyes] = useState<Record<DyeChannelType, boolean>>({
    BLUE: true,
    GREEN: true,
    YELLOW: true,
    RED: true,
    PURPLE: true,
    ORANGE: true,
  });

  // UI state
  const [strSearch, setStrSearch] = useState("");
  const [snpSearch, setSnpSearch] = useState("");
  const [recalculatedBanner, setRecalculatedBanner] = useState(false);
  const [bannerMessage, setBannerMessage] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);
  const [exportDropdownOpen, setExportDropdownOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sync state when modal opens or activeProfile changes
  useEffect(() => {
    if (!activeProfile) return;
    setProfileId(activeProfile.profileId);
    setNodeId(activeProfile.nodeId);

    const strs = Object.entries(activeProfile.strMarkers).map(([marker, val]) => ({
      marker,
      a1: String(val.allele1),
      a2: String(val.allele2),
      rfu1: val.rfu1 ?? 1500,
      rfu2: val.rfu2 ?? (val.allele2 ? val.rfu1 ?? 1500 : 0),
    }));
    setStrList(strs);

    const dosages: Record<string, number> = {};
    Object.entries(activeProfile.snpMarkers).forEach(([rsid, val]) => {
      dosages[rsid] = val.dosage ?? (val.genotype === "A/A" || val.genotype === "1/1" ? 2 : val.genotype === "A/G" || val.genotype === "0/1" ? 1 : 0);
    });
    setSnpDosages(dosages);
  }, [activeProfile?.profileId, activeProfile?.sampleType, isInspectorOpen]);

  // Live biocomputational calculations
  const bgaResult = useMemo(() => {
    return calculateClientBgaPosterior(snpDosages);
  }, [snpDosages]);

  const continentalBreakdown = useMemo(() => {
    return Object.entries(bgaResult.continentalPosteriors)
      .map(([cluster, prob]) => ({
        cluster,
        label: cluster === 'EUR' ? 'European' : cluster === 'AFR' ? 'African' : cluster === 'EAS' ? 'East Asian' : cluster === 'SAS' ? 'South Asian' : cluster === 'AMR' ? 'Indigenous American' : cluster === 'OCE' ? 'Oceanian' : 'Middle Eastern',
        probability: prob,
      }))
      .sort((a, b) => b.probability - a.probability);
  }, [bgaResult.continentalPosteriors]);

  // Dynamic WGS84 Centroid & Geographic Profiling Results
  const geoResults = useMemo<GeoProbability[]>(() => {
    const dominantColor =
      bgaResult.dominantAncestry === 'EUR' ? '#06B6D4' :
      bgaResult.dominantAncestry === 'AFR' ? '#22C55E' :
      bgaResult.dominantAncestry === 'EAS' ? '#EC4899' :
      bgaResult.dominantAncestry === 'SAS' ? '#F59E0B' :
      bgaResult.dominantAncestry === 'AMR' ? '#8B5CF6' :
      bgaResult.dominantAncestry === 'OCE' ? '#3B82F6' : '#14B8A6';

    // 1. Primary Inferred WGS84 Centroid
    const primaryRegion: GeoProbability = {
      region: `${bgaResult.dominantAncestryLabel} (Inferred WGS84 Centroid)`,
      lat: bgaResult.centroidLatitude,
      lng: bgaResult.centroidLongitude,
      probability: bgaResult.dominantProbability,
      color: dominantColor,
      initial_radius_km: Math.max(Math.round(bgaResult.r95ConfidenceRadiusKm * 1.5), 350),
      final_radius_km: Math.max(Math.round(bgaResult.r95ConfidenceRadiusKm), 60),
    };

    // 2. Continental Reference Clusters with Posteriors >= 1%
    const clusterRegions: GeoProbability[] = continentalBreakdown
      .filter((c) => c.probability >= 0.01 && c.cluster !== bgaResult.dominantAncestry)
      .map((c) => {
        const coords = CONTINENTAL_COORDINATES[c.cluster as ContinentalCluster] || { latitude: 0, longitude: 0 };
        const clusterColor =
          c.cluster === 'EUR' ? '#06B6D4' :
          c.cluster === 'AFR' ? '#22C55E' :
          c.cluster === 'EAS' ? '#EC4899' :
          c.cluster === 'SAS' ? '#F59E0B' :
          c.cluster === 'AMR' ? '#8B5CF6' :
          c.cluster === 'OCE' ? '#3B82F6' : '#14B8A6';

        return {
          region: `${c.label} (${c.cluster}) Reference Anchor`,
          lat: coords.latitude,
          lng: coords.longitude,
          probability: c.probability,
          color: clusterColor,
          initial_radius_km: 450,
          final_radius_km: 180,
        };
      });

    return [primaryRegion, ...clusterRegions];
  }, [bgaResult, continentalBreakdown]);

  const hirisResult = useMemo(() => {
    return calculateClientHIrisPlex(snpDosages);
  }, [snpDosages]);

  const strProfileMap = useMemo(() => {
    const map: Record<string, { allele1: string; allele2?: string; rfu1?: number; rfu2?: number }> = {};
    strList.forEach((s) => {
      if (s.marker) {
        map[s.marker] = {
          allele1: s.a1,
          allele2: s.a2,
          rfu1: s.rfu1,
          rfu2: s.rfu2,
        };
      }
    });
    return map;
  }, [strList]);

  const epgResult = useMemo<ClientEpgSynthesisResult>(() => {
    return synthesizeClientEpg(profileId || "CURRENT_SAMPLE", strProfileMap, {
      templateNg,
      degradationRate,
      includeStutter,
    });
  }, [profileId, strProfileMap, templateNg, degradationRate, includeStutter]);

  const filteredStrList = useMemo(() => {
    if (!strSearch) return strList;
    const q = strSearch.toLowerCase();
    return strList.filter((s) => s.marker.toLowerCase().includes(q));
  }, [strList, strSearch]);

  const allSnpsCatalog = useMemo(() => {
    const map: Record<string, { rsid: string; gene: string; trait: string }> = {};
    AIM_55_SNPS_CATALOG.forEach((s) => {
      map[s.rsid] = { rsid: s.rsid, gene: s.gene, trait: `AIM Continental Ancestry (${s.gene})` };
    });
    HIRISPLEX_41_SNPS_CATALOG.forEach((s) => {
      map[s.rsid] = { rsid: s.rsid, gene: s.gene, trait: `HIrisPlex-S ${s.trait}` };
    });
    return Object.values(map);
  }, []);

  const filteredSnpList = useMemo(() => {
    if (!snpSearch) return allSnpsCatalog;
    const q = snpSearch.toLowerCase();
    return allSnpsCatalog.filter(
      (s) => s.rsid.toLowerCase().includes(q) || s.gene.toLowerCase().includes(q) || s.trait.toLowerCase().includes(q)
    );
  }, [allSnpsCatalog, snpSearch]);

  if (!isInspectorOpen || !activeProfile) return null;

  // Handlers for Preset Loading
  const handleLoadPreset = (presetId: string) => {
    loadCaseworkPreset(presetId);
    const p = GOLDEN_CASEWORK_PRESETS.find((x) => x.presetId === presetId);
    if (p) {
      setBannerMessage(`✓ Casework Preset Loaded: ${p.sampleName}`);
      setRecalculatedBanner(true);
    }
  };

  // Drag and Drop Ingestion Handler
  const handleFileUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      if (!content) return;
      const parsed = parseDroppedFileContent(file.name, content);

      setProfileId(parsed.sampleId);
      const newStrs = Object.entries(parsed.strProfile).map(([m, c]) => ({
        marker: m,
        a1: c.allele1,
        a2: c.allele2 || c.allele1,
        rfu1: c.rfu1 ?? 1500,
        rfu2: c.rfu2 ?? 1500,
      }));
      setStrList(newStrs);

      if (Object.keys(parsed.snpDosages).length > 0) {
        setSnpDosages(parsed.snpDosages);
      }

      setBannerMessage(`✓ Ingested ${file.name} (${parsed.formatDetected}) with ${newStrs.length} STR Loci!`);
      setRecalculatedBanner(true);
    };
    reader.readAsText(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  // Export File Handlers
  const handleExport = (format: "CODIS_XML" | "LIMS_JSON" | "GENEMAPPER_CSV") => {
    let content = "";
    let filename = "";
    let mime = "";

    if (format === "CODIS_XML") {
      content = exportToCodisXml(profileId || "FORENZA_SAMPLE", strProfileMap);
      filename = `${profileId || "FORENZA_SAMPLE"}_CODIS_CMF3.2.xml`;
      mime = "application/xml";
    } else if (format === "LIMS_JSON") {
      content = exportToLimsJson(profileId || "FORENZA_SAMPLE", strProfileMap, snpDosages);
      filename = `${profileId || "FORENZA_SAMPLE"}_ISO17025_LIMS.json`;
      mime = "application/json";
    } else {
      content = exportToGeneMapperCsv(profileId || "FORENZA_SAMPLE", strProfileMap);
      filename = `${profileId || "FORENZA_SAMPLE"}_GeneMapper.csv`;
      mime = "text/csv";
    }

    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    setExportDropdownOpen(false);
  };

  // Save and Recalculate State
  const handleSaveAndCalculate = () => {
    const newStrMarkers: Record<string, { allele1: number | string; allele2: number | string; rfu1?: number; rfu2?: number }> = {};
    strList.forEach((item) => {
      if (item.marker) {
        newStrMarkers[item.marker] = {
          allele1: item.a1,
          allele2: item.a2 || item.a1,
          rfu1: item.rfu1,
          rfu2: item.rfu2,
        };
      }
    });

    const newSnpMarkers: Record<string, { rsid: string; genotype: string; trait: string; dosage: number }> = {};
    Object.entries(snpDosages).forEach(([rsid, dosage]) => {
      const gt = dosage === 2 ? "A/A" : dosage === 1 ? "A/G" : "G/G";
      newSnpMarkers[rsid] = {
        rsid,
        genotype: gt,
        trait: `Diagnostic Marker (${gt})`,
        dosage,
      };
    });

    const top1 = continentalBreakdown[0] || { label: "European", cluster: "EUR", probability: 0.95 };
    const top2 = continentalBreakdown[1] || { label: "Secondary", cluster: "MID", probability: 0.05 };

    const updatedProfile: ActiveProfileData = {
      ...activeProfile,
      profileId: profileId || "CUSTOM-PROFILE-01",
      nodeId: nodeId || "FORENSIC-NODE-ALPHA",
      markerCount: Object.keys(newStrMarkers).length,
      snpCount: Object.keys(newSnpMarkers).length,
      strMarkers: newStrMarkers,
      snpMarkers: newSnpMarkers,
      phenotype: {
        eyeColor: hirisResult.predictedEyeColor,
        eyeColorProb: Math.round((hirisResult.eyeColorProbabilities[hirisResult.predictedEyeColor as keyof typeof hirisResult.eyeColorProbabilities] || 0.9) * 1000) / 10,
        skinType: hirisResult.predictedSkinPhototype.replace(/_/g, " "),
        skinTypeProb: Math.round((hirisResult.skinPhototypeProbabilities[hirisResult.predictedSkinPhototype as keyof typeof hirisResult.skinPhototypeProbabilities] || 0.9) * 1000) / 10,
        hairType: hirisResult.predictedHairColor,
        hairTypeProb: Math.round((hirisResult.hairColorProbabilities[hirisResult.predictedHairColor as keyof typeof hirisResult.hairColorProbabilities] || 0.9) * 1000) / 10,
        freckling: hirisResult.mc1rRedHairEpistasisFlag ? "High Ephelides (MC1R High Risk)" : "Low / Moderate Ephelides",
      },
      ancestry: {
        primary: `${top1.label} (${top1.cluster})`,
        primaryPct: Math.round(top1.probability * 1000) / 10,
        secondary: `${top2.label} (${top2.cluster})`,
        secondaryPct: Math.round(top2.probability * 1000) / 10,
        populationCluster: `${top1.label} Continental Reference Cluster`,
      },
      geoLocation: {
        lat: bgaResult.centroidLatitude,
        lng: bgaResult.centroidLongitude,
        cityRegion: `${bgaResult.dominantAncestryLabel} Centroid`,
        country: bgaResult.dominantAncestryLabel,
        confidencePct: Math.round(bgaResult.dominantProbability * 1000) / 10,
      },
      degradationIndex: epgResult.degradationIndex,
    };

    setActiveProfile(updatedProfile);
    useForensicCaseStore.getState().updateActiveProfile({
      profileId: updatedProfile.profileId,
      nodeId: updatedProfile.nodeId,
      markerCount: updatedProfile.markerCount,
      snpCount: updatedProfile.snpCount,
      sampleType: updatedProfile.sampleType,
      strMarkers: updatedProfile.strMarkers as any,
      snpMarkers: updatedProfile.snpMarkers as any,
      phenotype: updatedProfile.phenotype,
      ancestry: updatedProfile.ancestry,
      geoLocation: updatedProfile.geoLocation,
    });

    setBannerMessage(`✓ Forensic Features & 35-Module DAG Recalculated for ${updatedProfile.profileId}!`);
    setRecalculatedBanner(true);
    setTab("inferred");
  };

  return (
    <AnimatePresence>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className="fixed inset-0 z-[100000] flex items-center justify-center p-2 sm:p-4 bg-black/85 backdrop-blur-md font-mono"
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              handleFileUpload(e.target.files[0]);
            }
          }}
          accept=".csv,.tsv,.xml,.vcf,.json"
          className="hidden"
        />

        <motion.div
          initial={{ opacity: 0, scale: 0.98, y: 8 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.98, y: 8 }}
          className="relative w-full h-[95vh] sm:h-auto sm:max-h-[94vh] sm:max-w-6xl flex flex-col rounded-2xl border border-tactical-border/80 bg-[#070D18] text-tactical-text shadow-[0_0_80px_rgba(0,0,0,0.9)] overflow-hidden"
        >
          {/* Drag Overlay */}
          {isDragOver && (
            <div className="absolute inset-0 z-50 bg-cyan-950/80 backdrop-blur-sm border-2 border-dashed border-cyan-400 flex flex-col items-center justify-center gap-3 text-cyan-300">
              <Upload className="w-12 h-12 animate-bounce" />
              <p className="text-sm font-bold uppercase tracking-wider">Drop Forensic File to Ingest</p>
              <p className="text-xs text-zinc-400">Supports GeneMapper CSV/TSV, CODIS XML, NGS VCF 4.2, and LIMS JSON</p>
            </div>
          )}

          {/* ── Top Bar / Header ── */}
          <div className="flex items-center justify-between px-3 sm:px-4 py-2.5 sm:py-3 border-b border-tactical-border/70 bg-[#0a1120] shrink-0">
            <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
              <div className="flex h-8 w-8 sm:h-9 sm:w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <Dna className="h-4 w-4 sm:h-5 sm:w-5 animate-pulse" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                  <h2 className="text-xs sm:text-sm font-extrabold tracking-wider uppercase text-white font-mono">
                    DNA &amp; SNP Terminal
                  </h2>
                  <span className="px-1.5 py-0.2 rounded text-[8px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                    ISO/IEC 17025
                  </span>
                  <span className="px-1.5 py-0.2 rounded text-[8px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                    CODIS CMF 3.2
                  </span>
                </div>
                <p className="text-[9px] sm:text-[10px] text-zinc-400 truncate">
                  24-STR Multiplex • 55-SNP AIM • 41-SNP HIrisPlex-S • 5-Dye EPG Spectrum
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
              {/* File Upload Button */}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-2.5 py-1.5 rounded-xl text-[10px] font-bold bg-zinc-800 border border-tactical-border/70 text-zinc-300 hover:text-white hover:bg-zinc-700 transition-all flex items-center gap-1.5 cursor-pointer"
                title="Import File (CSV, TSV, XML, VCF, JSON)"
              >
                <Upload className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden md:inline">Import File</span>
              </button>

              {/* Export Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setExportDropdownOpen(!exportDropdownOpen)}
                  className="px-2.5 py-1.5 rounded-xl text-[10px] font-bold bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/25 transition-all flex items-center gap-1.5 cursor-pointer"
                  title="Export Forensic Profile"
                >
                  <Download className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="hidden md:inline">Export</span>
                </button>

                {exportDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 rounded-xl bg-[#0c1425] border border-tactical-border/80 shadow-2xl p-1.5 z-50 text-[10px] space-y-1">
                    <button
                      onClick={() => handleExport("CODIS_XML")}
                      className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-white/5 text-zinc-200 flex items-center gap-2"
                    >
                      <FileCode className="w-3.5 h-3.5 text-cyan-400" />
                      <span>CODIS CMF 3.2 XML</span>
                    </button>
                    <button
                      onClick={() => handleExport("LIMS_JSON")}
                      className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-white/5 text-zinc-200 flex items-center gap-2"
                    >
                      <FileCode className="w-3.5 h-3.5 text-purple-400" />
                      <span>ISO 17025 LIMS JSON</span>
                    </button>
                    <button
                      onClick={() => handleExport("GENEMAPPER_CSV")}
                      className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-white/5 text-zinc-200 flex items-center gap-2"
                    >
                      <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                      <span>GeneMapper ID-X CSV</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Close Button */}
              <button
                onClick={() => setInspectorOpen(false)}
                className="p-1.5 rounded-xl text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer"
                title="Close Terminal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* ── Casework Presets Horizontal Toolbar (6 Golden Presets) ── */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 border-b border-tactical-border/60 bg-black/50 overflow-x-auto shrink-0 scrollbar-none">
            <span className="text-[8px] sm:text-[9px] text-zinc-500 uppercase font-bold tracking-wider shrink-0 px-1">
              Casework Presets:
            </span>
            {GOLDEN_CASEWORK_PRESETS.map((p) => {
              const isCurrent = profileId === p.presetId;
              return (
                <button
                  key={p.presetId}
                  onClick={() => handleLoadPreset(p.presetId)}
                  className={`px-2 py-1 rounded-lg text-[9px] sm:text-[10px] font-bold border transition-all flex items-center gap-1 cursor-pointer shrink-0 whitespace-nowrap ${
                    isCurrent
                      ? "bg-cyan-500/20 text-cyan-300 border-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.3)]"
                      : "bg-black/40 text-zinc-400 border-tactical-border/50 hover:text-white hover:bg-white/5"
                  }`}
                  title={p.description}
                >
                  <Sparkles className={`w-2.5 h-2.5 ${isCurrent ? "text-cyan-400" : "text-zinc-500"}`} />
                  <span>{p.sampleName.split(" ")[1]}</span>
                </button>
              );
            })}
          </div>

          {/* ── Navigation Tab Bar (4 Tabs) ── */}
          <div className="flex items-center justify-between px-3 sm:px-4 border-b border-tactical-border/70 bg-[#080d19] shrink-0 overflow-x-auto">
            <div className="flex items-center gap-1 sm:gap-2 shrink-0">
              {[
                { id: "inferred", label: "Inferred Telemetry & GIS", icon: Globe, badge: `${Math.round(bgaResult.dominantProbability * 100)}% BGA`, color: "text-emerald-400" },
                { id: "str", label: "24-STR Multiplex", icon: Dna, badge: `${strList.length} Loci`, color: "text-cyan-400" },
                { id: "snp", label: "55-SNP AIM Matrix", icon: Sliders, badge: `${Object.keys(snpDosages).length} SNPs`, color: "text-purple-400" },
                { id: "epg", label: "EPG Spectrum", icon: Activity, badge: `DI ${epgResult.degradationIndex.toFixed(2)}`, color: "text-amber-400" },
              ].map((tItem) => {
                const Icon = tItem.icon;
                const isActive = tab === tItem.id;
                return (
                  <button
                    key={tItem.id}
                    onClick={() => setTab(tItem.id as any)}
                    className={`flex items-center gap-1.5 py-2 sm:py-2.5 px-2.5 sm:px-3.5 font-mono text-[11px] sm:text-xs font-bold transition-all border-b-2 cursor-pointer whitespace-nowrap shrink-0 min-h-[44px] ${
                      isActive
                        ? "text-white border-cyan-400 bg-cyan-500/10"
                        : "text-zinc-400 border-transparent hover:text-zinc-200 hover:bg-white/5"
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? "text-cyan-400" : tItem.color}`} />
                    <span>{tItem.label}</span>
                    {tItem.badge && (
                      <span
                        className={`text-[8px] px-1.5 py-0.2 rounded border font-mono ${
                          isActive
                            ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                            : "bg-black/50 text-zinc-400 border-tactical-border/60"
                        }`}
                      >
                        {tItem.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            <div className="hidden lg:flex items-center gap-3 text-[10px] text-zinc-400">
              <span>Sample: <strong className="text-cyan-300">{profileId}</strong></span>
              <span className="h-3 w-px bg-tactical-border/60" />
              <span>DI: <strong className={epgResult.degradationIndex > 5.0 ? "text-rose-400" : "text-emerald-400"}>{epgResult.degradationIndex}</strong></span>
            </div>
          </div>

          {/* ── Recalculation Alert Toast ── */}
          {recalculatedBanner && (
            <div className="bg-emerald-500/10 border-b border-emerald-500/30 px-4 py-2 flex items-center justify-between gap-2 shrink-0">
              <div className="flex items-center gap-2 text-emerald-300 font-mono text-xs font-bold truncate">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 animate-pulse" />
                <span className="truncate">{bannerMessage || `Forensic features recalculated for ${profileId}`}</span>
              </div>
              <button
                onClick={() => setRecalculatedBanner(false)}
                className="text-zinc-400 hover:text-white p-0.5 cursor-pointer shrink-0"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* ── Main Content Area ── */}
          <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-4 font-mono">
            {/* ════════════════════════════════════════════════════════════════════
                TAB 1: INFERRED TELEMETRY & LIVE GIS MAP
               ════════════════════════════════════════════════════════════════════ */}
            {tab === "inferred" && (
              <div className="space-y-4">
                {/* HUD Strip */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 p-2.5 sm:p-3 rounded-xl border border-tactical-border/70 bg-black/40 text-xs">
                  <div className="space-y-0.5">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold tracking-wider">Dominant Ancestry</span>
                    <p className="font-bold text-cyan-400 text-xs truncate">
                      {bgaResult.dominantAncestryLabel} ({Math.round(bgaResult.dominantProbability * 100)}%)
                    </p>
                  </div>
                  <div className="space-y-0.5">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold tracking-wider">HIrisPlex-S Iris</span>
                    <p className="font-bold text-emerald-400 text-xs truncate">
                      {hirisResult.predictedEyeColor} Eye
                    </p>
                  </div>
                  <div className="space-y-0.5">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold tracking-wider">WGS84 Centroid</span>
                    <p className="font-bold text-amber-400 text-xs truncate">
                      {bgaResult.centroidLatitude.toFixed(2)}°N, {bgaResult.centroidLongitude.toFixed(2)}°E
                    </p>
                  </div>
                  <div className="space-y-0.5">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold tracking-wider">R95% Radius / DI</span>
                    <p className="font-bold text-purple-400 text-xs truncate">
                      {Math.round(bgaResult.r95ConfidenceRadiusKm)} km • DI {epgResult.degradationIndex}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                  {/* Left Column: BGA Continental Breakdown & HIrisPlex */}
                  <div className="lg:col-span-5 space-y-4">
                    {/* BGA Breakdown */}
                    <div className="rounded-xl border border-tactical-border/70 bg-tactical-surface/50 p-3 space-y-2.5">
                      <div className="flex items-center justify-between border-b border-tactical-border/60 pb-2">
                        <div className="flex items-center gap-2 text-xs font-bold text-cyan-400">
                          <Globe className="w-4 h-4 shrink-0" />
                          <span>7 Continental Ancestry (55-SNP AIM)</span>
                        </div>
                        <span className="text-[8px] px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-bold">
                          Bayesian Posterior
                        </span>
                      </div>

                      <div className="space-y-2">
                        {continentalBreakdown.map((item) => (
                          <div key={item.cluster} className="space-y-0.5">
                            <div className="flex justify-between text-[10px] font-bold">
                              <span className="text-zinc-300">{item.label} ({item.cluster})</span>
                              <span className="text-cyan-400">{Math.round(item.probability * 1000) / 10}%</span>
                            </div>
                            <div className="h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-cyan-500 to-teal-400 rounded-full transition-all duration-500"
                                style={{ width: `${item.probability * 100}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* HIrisPlex-S Phenotype */}
                    <div className="rounded-xl border border-tactical-border/70 bg-tactical-surface/50 p-3 space-y-2.5">
                      <div className="flex items-center justify-between border-b border-tactical-border/60 pb-2">
                        <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                          <Eye className="w-4 h-4 shrink-0" />
                          <span>HIrisPlex-S Pigmentation (41-SNP)</span>
                        </div>
                        <span className="text-[8px] px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-bold">
                          Softmax MLR
                        </span>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[10px]">
                        <div className="p-2 rounded-lg bg-black/40 border border-tactical-border/40 space-y-0.5">
                          <span className="text-zinc-500 block uppercase text-[8px] font-bold">Eye Color</span>
                          <span className="font-bold text-cyan-300">{hirisResult.predictedEyeColor}</span>
                        </div>
                        <div className="p-2 rounded-lg bg-black/40 border border-tactical-border/40 space-y-0.5">
                          <span className="text-zinc-500 block uppercase text-[8px] font-bold">Hair Color</span>
                          <span className="font-bold text-purple-300">{hirisResult.predictedHairColor}</span>
                        </div>
                        <div className="p-2 rounded-lg bg-black/40 border border-tactical-border/40 space-y-0.5">
                          <span className="text-zinc-500 block uppercase text-[8px] font-bold">Skin Phototype</span>
                          <span className="font-bold text-amber-300">{hirisResult.predictedSkinPhototype.replace(/_/g, " ")}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Right Column: GeoForensic Map */}
                  <div className="lg:col-span-7 space-y-3">
                    <div className="rounded-xl border border-tactical-border/70 bg-tactical-surface/50 p-3 space-y-2">
                      <div className="flex items-center justify-between text-xs font-bold text-cyan-400 pb-1">
                        <div className="flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                          <span>WGS84 Centroid &amp; Geographic Profiling</span>
                        </div>
                        <span className="text-[9px] text-zinc-400">
                          {bgaResult.centroidLatitude.toFixed(4)}° N, {bgaResult.centroidLongitude.toFixed(4)}° E
                        </span>
                      </div>

                      <div className="w-full h-64 sm:h-80 rounded-xl overflow-hidden border border-tactical-border/60">
                        <GeoForensicPanel
                          geoResults={geoResults}
                          reliabilityScore={bgaResult.dominantProbability}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ════════════════════════════════════════════════════════════════════
                TAB 2: 24-STR FORENSIC MULTIPLEX GRID
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
                      className="w-full bg-black/60 border border-tactical-border/70 rounded-xl pl-9 pr-3 py-2 text-xs text-white outline-none focus:border-cyan-500 font-mono min-h-[44px]"
                    />
                  </div>

                  <button
                    onClick={() => {
                      setStrList((prev) => [...prev, { marker: "NEW_LOCUS", a1: "12", a2: "14", rfu1: 1500, rfu2: 1500 }]);
                    }}
                    className="px-3.5 py-2 rounded-xl text-xs font-bold bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/25 transition-all flex items-center justify-center gap-1.5 cursor-pointer font-mono shrink-0 min-h-[44px]"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Custom Locus</span>
                  </button>
                </div>

                {/* Structured Table */}
                <div className="rounded-xl border border-tactical-border/70 bg-black/40 overflow-hidden">
                  <div className="max-h-[52vh] overflow-y-auto overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="sticky top-0 bg-[#0a101d] border-b border-tactical-border/80 text-zinc-400 text-[10px] uppercase tracking-wider select-none z-10">
                        <tr>
                          <th className="py-2.5 px-3 w-12 text-center">#</th>
                          <th className="py-2.5 px-3">Locus Marker</th>
                          <th className="py-2.5 px-3 w-28">Allele 1</th>
                          <th className="py-2.5 px-3 w-28">Allele 2</th>
                          <th className="py-2.5 px-3 w-24">RFU 1</th>
                          <th className="py-2.5 px-3 w-24">RFU 2</th>
                          <th className="py-2.5 px-3 w-24 text-center">Hb Balance</th>
                          <th className="py-2.5 px-3 w-16 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-tactical-border/40 text-zinc-200">
                        {filteredStrList.length === 0 ? (
                          <tr>
                            <td colSpan={8} className="py-8 text-center text-zinc-500 text-xs">
                              No STR loci matching "{strSearch}".
                            </td>
                          </tr>
                        ) : (
                          filteredStrList.map((item, idx) => {
                            const isHomo = item.a1 === item.a2 || !item.a2 || item.a2 === "[0]";
                            const isDropout = item.a1 === "[0]" || item.a2 === "[0]" || item.rfu1 < 50.0;
                            const hb = !isHomo && Math.max(item.rfu1, item.rfu2) > 0
                              ? Math.min(item.rfu1, item.rfu2) / Math.max(item.rfu1, item.rfu2)
                              : 1.0;
                            const hbWarning = !isHomo && hb < 0.60;

                            return (
                              <tr key={idx} className="hover:bg-white/5 transition-colors">
                                <td className="py-2 px-3 text-center text-zinc-500 text-[10px]">
                                  {idx + 1}
                                </td>
                                <td className="py-2 px-3 font-bold text-cyan-300">
                                  {item.marker}
                                </td>
                                <td className="py-2 px-3">
                                  <input
                                    type="text"
                                    value={item.a1}
                                    onChange={(e) => {
                                      const val = e.target.value;
                                      setStrList((prev) => prev.map((it, i) => (i === idx ? { ...it, a1: val } : it)));
                                    }}
                                    className="w-20 bg-tactical-surface/80 border border-tactical-border/60 rounded px-2 py-1 text-white font-mono outline-none focus:border-cyan-400 text-xs"
                                  />
                                </td>
                                <td className="py-2 px-3">
                                  <input
                                    type="text"
                                    value={item.a2}
                                    onChange={(e) => {
                                      const val = e.target.value;
                                      setStrList((prev) => prev.map((it, i) => (i === idx ? { ...it, a2: val } : it)));
                                    }}
                                    className="w-20 bg-tactical-surface/80 border border-tactical-border/60 rounded px-2 py-1 text-white font-mono outline-none focus:border-cyan-400 text-xs"
                                  />
                                </td>
                                <td className="py-2 px-3">
                                  <input
                                    type="number"
                                    value={item.rfu1}
                                    onChange={(e) => {
                                      const val = parseFloat(e.target.value) || 0;
                                      setStrList((prev) => prev.map((it, i) => (i === idx ? { ...it, rfu1: val } : it)));
                                    }}
                                    className="w-20 bg-tactical-surface/80 border border-tactical-border/60 rounded px-2 py-1 text-white font-mono outline-none focus:border-cyan-400 text-xs"
                                  />
                                </td>
                                <td className="py-2 px-3">
                                  <input
                                    type="number"
                                    value={item.rfu2}
                                    onChange={(e) => {
                                      const val = parseFloat(e.target.value) || 0;
                                      setStrList((prev) => prev.map((it, i) => (i === idx ? { ...it, rfu2: val } : it)));
                                    }}
                                    className="w-20 bg-tactical-surface/80 border border-tactical-border/60 rounded px-2 py-1 text-white font-mono outline-none focus:border-cyan-400 text-xs"
                                  />
                                </td>
                                <td className="py-2 px-3 text-center">
                                  {isDropout ? (
                                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold">
                                      Dropout
                                    </span>
                                  ) : isHomo ? (
                                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-bold">
                                      Homozygous
                                    </span>
                                  ) : hbWarning ? (
                                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">
                                      Hb {(hb * 100).toFixed(0)}%
                                    </span>
                                  ) : (
                                    <span className="text-[8px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-bold">
                                      Hb {(hb * 100).toFixed(0)}%
                                    </span>
                                  )}
                                </td>
                                <td className="py-2 px-3 text-right">
                                  <button
                                    onClick={() => setStrList((prev) => prev.filter((_, i) => i !== idx))}
                                    className="text-zinc-500 hover:text-red-400 p-1 rounded transition-colors cursor-pointer"
                                    title="Delete locus"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                </td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* ════════════════════════════════════════════════════════════════════
                TAB 3: 55-SNP AIM MATRIX
               ════════════════════════════════════════════════════════════════════ */}
            {tab === "snp" && (
              <div className="space-y-3">
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
                  <div className="relative flex-1 max-w-sm">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                    <input
                      type="text"
                      placeholder="Search rsID, gene, or trait..."
                      value={snpSearch}
                      onChange={(e) => setSnpSearch(e.target.value)}
                      className="w-full bg-black/60 border border-tactical-border/70 rounded-xl pl-9 pr-3 py-2 text-xs text-white outline-none focus:border-purple-500 font-mono min-h-[44px]"
                    />
                  </div>

                  <div className="text-[10px] text-zinc-400 flex items-center gap-2">
                    <span>Active Dosages: <strong className="text-purple-300">{Object.keys(snpDosages).length} SNPs</strong></span>
                  </div>
                </div>

                {/* Structured Table */}
                <div className="rounded-xl border border-tactical-border/70 bg-black/40 overflow-hidden">
                  <div className="max-h-[52vh] overflow-y-auto overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="sticky top-0 bg-[#0a101d] border-b border-tactical-border/80 text-zinc-400 text-[10px] uppercase tracking-wider select-none z-10">
                        <tr>
                          <th className="py-2.5 px-3 w-12 text-center">#</th>
                          <th className="py-2.5 px-3 w-32">rsID Marker</th>
                          <th className="py-2.5 px-3 w-28">Gene</th>
                          <th className="py-2.5 px-3">Phenotype / Ancestry Association</th>
                          <th className="py-2.5 px-3 w-36 text-center">Genotype Dosage</th>
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
                          filteredSnpList.map((item, idx) => {
                            const currentDosage = snpDosages[item.rsid] ?? 0;
                            return (
                              <tr key={item.rsid} className="hover:bg-white/5 transition-colors">
                                <td className="py-2 px-3 text-center text-zinc-500 text-[10px]">
                                  {idx + 1}
                                </td>
                                <td className="py-2 px-3 font-bold text-purple-300">
                                  {item.rsid}
                                </td>
                                <td className="py-2 px-3 text-cyan-400 font-bold">
                                  {item.gene}
                                </td>
                                <td className="py-2 px-3 text-zinc-300 text-[11px]">
                                  {item.trait}
                                </td>
                                <td className="py-2 px-3 text-center">
                                  <div className="inline-flex items-center gap-1 p-0.5 rounded-lg bg-black/60 border border-tactical-border/50">
                                    {[0, 1, 2].map((dVal) => {
                                      const isSel = currentDosage === dVal;
                                      return (
                                        <button
                                          key={dVal}
                                          onClick={() => {
                                            setSnpDosages((prev) => ({ ...prev, [item.rsid]: dVal }));
                                          }}
                                          className={`px-2 py-0.5 rounded text-[9px] font-bold transition-all cursor-pointer ${
                                            isSel
                                              ? "bg-purple-500 text-white shadow-[0_0_8px_rgba(168,85,247,0.5)]"
                                              : "text-zinc-500 hover:text-zinc-300"
                                          }`}
                                        >
                                          {dVal === 0 ? "0 (G/G)" : dVal === 1 ? "1 (A/G)" : "2 (A/A)"}
                                        </button>
                                      );
                                    })}
                                  </div>
                                </td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* ════════════════════════════════════════════════════════════════════
                TAB 4: INTERACTIVE EPG SPECTRUM VISUALIZER
               ════════════════════════════════════════════════════════════════════ */}
            {tab === "epg" && (
              <div className="space-y-4">
                {/* EPG Controls Bar */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3 rounded-xl border border-tactical-border/70 bg-black/40 text-xs">
                  {/* Template Slider */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-zinc-400 font-bold">
                      <span>Template DNA:</span>
                      <span className="text-cyan-300">{templateNg.toFixed(2)} ng</span>
                    </div>
                    <input
                      type="range"
                      min="0.03"
                      max="2.0"
                      step="0.05"
                      value={templateNg}
                      onChange={(e) => setTemplateNg(parseFloat(e.target.value))}
                      className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                    />
                  </div>

                  {/* Degradation Slider */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-zinc-400 font-bold">
                      <span>Degradation Rate (d):</span>
                      <span className={degradationRate > 0.005 ? "text-rose-400" : "text-amber-300"}>
                        {degradationRate.toFixed(4)}
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0.0"
                      max="0.012"
                      step="0.0005"
                      value={degradationRate}
                      onChange={(e) => setDegradationRate(parseFloat(e.target.value))}
                      className="w-full accent-amber-400 cursor-pointer h-1.5 bg-zinc-800 rounded-lg"
                    />
                  </div>

                  {/* Stutter & Artifact Toggles */}
                  <div className="flex items-center justify-between sm:justify-end gap-3 pt-2 sm:pt-0">
                    <button
                      onClick={() => setIncludeStutter(!includeStutter)}
                      className={`px-3 py-1.5 rounded-xl text-[10px] font-bold border transition-all cursor-pointer min-h-[44px] flex items-center gap-1.5 ${
                        includeStutter
                          ? "bg-purple-500/20 text-purple-300 border-purple-400"
                          : "bg-black/40 text-zinc-500 border-tactical-border/50"
                      }`}
                    >
                      <Activity className="w-3.5 h-3.5" />
                      <span>{includeStutter ? "Stutter Artifacts: ON" : "Stutter Artifacts: OFF"}</span>
                    </button>
                  </div>
                </div>

                {/* Dye Channel Selector Strip */}
                <div className="flex items-center gap-2 flex-wrap text-xs">
                  <span className="text-[9px] text-zinc-500 uppercase font-bold">Channels:</span>
                  {(["BLUE", "GREEN", "YELLOW", "RED", "PURPLE", "ORANGE"] as DyeChannelType[]).map((dye) => {
                    const active = activeDyes[dye];
                    const col = EPG_DYE_COLORS[dye];
                    return (
                      <button
                        key={dye}
                        onClick={() => setActiveDyes((prev) => ({ ...prev, [dye]: !prev[dye] }))}
                        className={`px-2.5 py-1 rounded-lg text-[10px] font-bold border transition-all cursor-pointer flex items-center gap-1.5 ${
                          active
                            ? "bg-white/10 text-white"
                            : "bg-black/40 text-zinc-600 border-tactical-border/40 line-through"
                        }`}
                        style={{ borderColor: active ? col : undefined }}
                      >
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: col }} />
                        <span>{dye}</span>
                      </button>
                    );
                  })}
                </div>

                {/* Continuous SVG Electropherogram Waveform */}
                <div className="rounded-xl border border-tactical-border/70 bg-[#040810] p-3 space-y-2 overflow-hidden">
                  <div className="flex items-center justify-between text-[10px] text-zinc-400 border-b border-tactical-border/50 pb-1.5">
                    <span className="font-bold text-white">Continuous RFU Electropherogram Waveform (50 bp – 500 bp)</span>
                    <span className="text-zinc-500 font-mono">AT: 50 RFU • ST: 200 RFU • SAT: 8000 RFU</span>
                  </div>

                  <div className="w-full h-56 sm:h-72 relative overflow-hidden bg-black/60 rounded-lg">
                    <svg viewBox="50 0 450 3000" className="w-full h-full" preserveAspectRatio="none">
                      {/* Grid Lines */}
                      {[500, 1000, 1500, 2000, 2500].map((rfu) => (
                        <line
                          key={rfu}
                          x1="50"
                          y1={3000 - rfu}
                          x2="500"
                          y2={3000 - rfu}
                          stroke="#1e293b"
                          strokeWidth="1"
                          strokeDasharray="2 2"
                        />
                      ))}

                      {/* Threshold Lines */}
                      {/* Analytical Threshold (50 RFU) */}
                      <line x1="50" y1={3000 - 50} x2="500" y2={3000 - 50} stroke="#ef4444" strokeWidth="1.5" strokeDasharray="4 4" />
                      {/* Stochastic Threshold (200 RFU) */}
                      <line x1="50" y1={3000 - 200} x2="500" y2={3000 - 200} stroke="#f59e0b" strokeWidth="1.5" strokeDasharray="4 4" />

                      {/* Traces */}
                      {(["BLUE", "GREEN", "YELLOW", "RED", "PURPLE", "ORANGE"] as DyeChannelType[]).map((dye) => {
                        if (!activeDyes[dye]) return null;
                        const trace = epgResult.traces[dye];
                        if (!trace || !trace.dataPoints.length) return null;

                        const pointsStr = trace.dataPoints
                          .map((pt) => `${pt.sizeBp},${3000 - Math.min(pt.rfu, 2950)}`)
                          .join(" ");

                        return (
                          <polyline
                            key={dye}
                            fill="none"
                            stroke={trace.colorHex}
                            strokeWidth="1.8"
                            points={pointsStr}
                            strokeLinejoin="round"
                          />
                        );
                      })}
                    </svg>

                    {/* Axis Labels */}
                    <div className="absolute left-2 top-2 text-[8px] text-zinc-500 font-mono">
                      RFU 3000
                    </div>
                    <div className="absolute left-2 bottom-6 text-[8px] text-zinc-500 font-mono">
                      RFU 0
                    </div>
                    <div className="absolute right-2 bottom-1 text-[8px] text-zinc-500 font-mono">
                      500 bp
                    </div>
                    <div className="absolute left-10 bottom-1 text-[8px] text-zinc-500 font-mono">
                      50 bp
                    </div>
                  </div>
                </div>

                {/* EPG Peak Annotation Summary */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60">
                    <span className="text-[8px] text-zinc-500 uppercase block font-bold">Degradation Index</span>
                    <p className={`font-bold text-xs ${epgResult.degradationIndex > 5.0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {epgResult.degradationIndex.toFixed(2)} ({epgResult.degradationSeverity})
                    </p>
                  </div>
                  <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60">
                    <span className="text-[8px] text-zinc-500 uppercase block font-bold">Total Analyzed Peaks</span>
                    <p className="font-bold text-cyan-300 text-xs">{epgResult.allPeaks.length} Peaks</p>
                  </div>
                  <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60">
                    <span className="text-[8px] text-zinc-500 uppercase block font-bold">QA/QC Status</span>
                    <p className={`font-bold text-xs ${epgResult.overallPassedQc ? "text-emerald-400" : "text-amber-400"}`}>
                      {epgResult.overallPassedQc ? "PASSED (ISO 17025)" : "STOCHASTIC WARNING"}
                    </p>
                  </div>
                  <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60">
                    <span className="text-[8px] text-zinc-500 uppercase block font-bold">Size Standard</span>
                    <p className="font-bold text-amber-300 text-xs">LIZ 600 (30 Frags)</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* ── Footer Actions ── */}
          <div className="flex items-center justify-between gap-3 px-3 sm:px-4 py-2.5 sm:py-3 border-t border-tactical-border/70 bg-[#0a1120] shrink-0">
            <button
              onClick={() => setInspectorOpen(false)}
              className="px-3 sm:px-4 py-2 rounded-xl text-xs font-bold text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer font-mono min-h-[44px]"
            >
              Close
            </button>

            <button
              onClick={handleSaveAndCalculate}
              className="px-4 sm:px-6 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-500 via-teal-400 to-emerald-400 text-black shadow-lg hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all flex items-center gap-2 cursor-pointer font-mono uppercase tracking-wider font-extrabold min-h-[44px]"
            >
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>Apply &amp; Recalculate 35 Modules</span>
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
