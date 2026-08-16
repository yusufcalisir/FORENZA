import { create } from "zustand";
import { GOLDEN_CASEWORK_PRESETS } from "@/utils/caseworkPresets";
import { calculateClientBgaPosterior, calculateClientHIrisPlex } from "@/utils/snpPhenotypeBgaEngine";

export interface StrLocusData {
  marker: string;
  allele1: number | string;
  allele2: number | string;
}

export interface SnpMarkerData {
  rsid: string;
  genotype: string;
  trait?: string;
  dosage?: number;
}

export interface ActiveProfileData {
  profileId: string;
  nodeId: string;
  markerCount: number;
  snpCount: number;
  sampleType: "EU" | "AA" | "EAS" | "SAS" | "DVI" | "TOUCH" | "CUSTOM";
  timestamp: string;
  strMarkers: Record<string, { allele1: number | string; allele2: number | string; rfu1?: number; rfu2?: number }>;
  snpMarkers: Record<string, { rsid: string; genotype: string; trait?: string; dosage?: number }>;
  phenotype: {
    eyeColor: string;
    eyeColorProb: number;
    skinType: string;
    skinTypeProb: number;
    hairType: string;
    hairTypeProb: number;
    freckling: string;
  };
  ancestry: {
    primary: string;
    primaryPct: number;
    secondary: string;
    secondaryPct: number;
    populationCluster: string;
  };
  geoLocation: {
    lat: number;
    lng: number;
    cityRegion: string;
    country: string;
    confidencePct: number;
  };
  kinshipLR: string;
  epigeneticAge: number;
  degradationIndex?: number;
}

function presetToActiveProfile(presetId: string): ActiveProfileData {
  const p = GOLDEN_CASEWORK_PRESETS.find(x => x.presetId === presetId) || GOLDEN_CASEWORK_PRESETS[0];

  const bga = calculateClientBgaPosterior(p.snpDosages);
  const hiris = calculateClientHIrisPlex(p.snpDosages);

  const snpMarkers: Record<string, { rsid: string; genotype: string; trait?: string; dosage?: number }> = {};
  for (const [rsid, dosage] of Object.entries(p.snpDosages)) {
    const gt = dosage === 2 ? "A/A" : dosage === 1 ? "A/G" : "G/G";
    snpMarkers[rsid] = { rsid, genotype: gt, trait: "Diagnostic AIM / Phenotype Marker", dosage };
  }

  const strMarkers: Record<string, { allele1: string | number; allele2: string | number; rfu1?: number; rfu2?: number }> = {};
  for (const [marker, call] of Object.entries(p.strProfile)) {
    strMarkers[marker] = {
      allele1: call.allele1,
      allele2: call.allele2 ?? call.allele1,
      rfu1: call.rfu1,
      rfu2: call.rfu2,
    };
  }

  const sampleTypeMap: Record<string, "EU" | "AA" | "EAS" | "SAS" | "DVI" | "TOUCH" | "CUSTOM"> = {
    VECTOR_TERM_01: "EU",
    VECTOR_TERM_02: "AA",
    VECTOR_TERM_03: "EAS",
    VECTOR_TERM_04: "SAS",
    VECTOR_TERM_05: "DVI",
    VECTOR_TERM_06: "TOUCH",
  };

  const sampleType = sampleTypeMap[p.presetId] || "CUSTOM";

  const sortedBreakdown = Object.entries(bga.continentalPosteriors)
    .map(([cluster, prob]) => ({
      cluster,
      label: cluster === 'EUR' ? 'European' : cluster === 'AFR' ? 'African' : cluster === 'EAS' ? 'East Asian' : cluster === 'SAS' ? 'South Asian' : cluster === 'AMR' ? 'Indigenous American' : cluster === 'OCE' ? 'Oceanian' : 'Middle Eastern',
      probability: prob,
    }))
    .sort((a, b) => b.probability - a.probability);

  const top1 = sortedBreakdown[0] || { label: "European", cluster: "EUR", probability: 0.95 };
  const top2 = sortedBreakdown[1] || { label: "Secondary", cluster: "MID", probability: 0.01 };

  return {
    profileId: p.presetId,
    nodeId: "FORENSIC-LAB-ALPHA",
    markerCount: Object.keys(p.strProfile).length,
    snpCount: Object.keys(p.snpDosages).length,
    sampleType,
    timestamp: "2026-08-16 19:30",
    strMarkers,
    snpMarkers,
    phenotype: {
      eyeColor: hiris.predictedEyeColor,
      eyeColorProb: Math.round(hiris.eyeColorProbabilities[hiris.predictedEyeColor as keyof typeof hiris.eyeColorProbabilities] * 1000) / 10,
      skinType: hiris.predictedSkinPhototype.replace(/_/g, " "),
      skinTypeProb: Math.round(hiris.skinPhototypeProbabilities[hiris.predictedSkinPhototype as keyof typeof hiris.skinPhototypeProbabilities] * 1000) / 10,
      hairType: hiris.predictedHairColor,
      hairTypeProb: Math.round(hiris.hairColorProbabilities[hiris.predictedHairColor as keyof typeof hiris.hairColorProbabilities] * 1000) / 10,
      freckling: hiris.mc1rRedHairEpistasisFlag ? "High Ephelides (MC1R High Risk)" : "Low / Moderate Ephelides",
    },
    ancestry: {
      primary: `${top1.label} (${top1.cluster})`,
      primaryPct: Math.round(top1.probability * 1000) / 10,
      secondary: `${top2.label} (${top2.cluster})`,
      secondaryPct: Math.round(top2.probability * 1000) / 10,
      populationCluster: `${top1.label} Continental Reference Cluster`,
    },
    geoLocation: {
      lat: bga.centroidLatitude,
      lng: bga.centroidLongitude,
      cityRegion: p.expectedCentroid,
      country: bga.dominantAncestryLabel,
      confidencePct: Math.round(bga.dominantProbability * 1000) / 10,
    },
    kinshipLR: "1.42e8",
    epigeneticAge: 32.4,
    degradationIndex: p.degradationIndex,
  };
}

export const SAMPLE_CASE_EU: ActiveProfileData = presetToActiveProfile("VECTOR_TERM_01");
export const SAMPLE_CASE_AA: ActiveProfileData = presetToActiveProfile("VECTOR_TERM_02");

interface IngestState {
  lastIngestedProfileId: string | null;
  lastIngestedNodeId: string | null;
  markerCount: number;
  isValid: boolean;

  // Active Profile & Feedback state
  activeProfile: ActiveProfileData | null;
  toastBanner: string | null;
  isInspectorOpen: boolean;

  setLastIngested: (profileId: string, nodeId: string, markerCount: number) => void;
  loadSampleCaseEU: () => void;
  loadSampleCaseAA: () => void;
  loadCaseworkPreset: (presetId: string) => void;
  setActiveProfile: (profile: ActiveProfileData) => void;
  setToastBanner: (msg: string | null) => void;
  setInspectorOpen: (open: boolean) => void;
  clear: () => void;
}

export const useIngestStore = create<IngestState>((set) => ({
  lastIngestedProfileId: "VECTOR_TERM_01",
  lastIngestedNodeId: "FORENSIC-LAB-ALPHA",
  markerCount: 24,
  isValid: true,
  activeProfile: SAMPLE_CASE_EU,
  toastBanner: null,
  isInspectorOpen: false,

  setLastIngested: (profileId, nodeId, markerCount) =>
    set({
      lastIngestedProfileId: profileId,
      lastIngestedNodeId: nodeId,
      markerCount,
      isValid: markerCount >= 1,
    }),

  loadSampleCaseEU: () => {
    const prof = presetToActiveProfile("VECTOR_TERM_01");
    set({
      activeProfile: prof,
      lastIngestedProfileId: prof.profileId,
      lastIngestedNodeId: prof.nodeId,
      markerCount: prof.markerCount,
      isValid: true,
      toastBanner: `✓ Sample EU Loaded: ${prof.profileId} (24 STR Loci, 55 SNPs). Inferred: ${prof.phenotype.eyeColor} (${prof.phenotype.eyeColorProb}%), ${prof.ancestry.primary}, ${prof.geoLocation.lat.toFixed(2)}°N, ${prof.geoLocation.lng.toFixed(2)}°E`,
    });
  },

  loadSampleCaseAA: () => {
    const prof = presetToActiveProfile("VECTOR_TERM_02");
    set({
      activeProfile: prof,
      lastIngestedProfileId: prof.profileId,
      lastIngestedNodeId: prof.nodeId,
      markerCount: prof.markerCount,
      isValid: true,
      toastBanner: `✓ Sample AA Loaded: ${prof.profileId} (24 STR Loci, 55 SNPs). Inferred: ${prof.phenotype.eyeColor} (${prof.phenotype.eyeColorProb}%), ${prof.ancestry.primary}, ${prof.geoLocation.lat.toFixed(2)}°N, ${prof.geoLocation.lng.toFixed(2)}°E`,
    });
  },

  loadCaseworkPreset: (presetId: string) => {
    const prof = presetToActiveProfile(presetId);
    set({
      activeProfile: prof,
      lastIngestedProfileId: prof.profileId,
      lastIngestedNodeId: prof.nodeId,
      markerCount: prof.markerCount,
      isValid: true,
      toastBanner: `✓ Casework Preset Loaded: ${prof.profileId} (${prof.markerCount} STRs, ${prof.snpCount} SNPs) • ${prof.phenotype.eyeColor} Eye • ${prof.ancestry.primary}`,
    });
  },

  setActiveProfile: (profile) =>
    set({
      activeProfile: profile,
      lastIngestedProfileId: profile.profileId,
      lastIngestedNodeId: profile.nodeId,
      markerCount: profile.markerCount,
      isValid: true,
      toastBanner: `✓ DNA Profile Updated: ${profile.profileId} (${profile.markerCount} STRs, ${profile.snpCount} SNPs)`,
    }),

  setToastBanner: (msg) => set({ toastBanner: msg }),
  setInspectorOpen: (open) => set({ isInspectorOpen: open }),

  clear: () =>
    set({
      lastIngestedProfileId: null,
      lastIngestedNodeId: null,
      markerCount: 0,
      isValid: false,
      activeProfile: null,
      toastBanner: null,
      isInspectorOpen: false,
    }),
}));
