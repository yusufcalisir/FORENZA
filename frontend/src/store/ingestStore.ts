import { create } from "zustand";

export interface StrLocusData {
  marker: string;
  allele1: number;
  allele2: number;
}

export interface SnpMarkerData {
  rsid: string;
  genotype: string;
  trait?: string;
}

export interface ActiveProfileData {
  profileId: string;
  nodeId: string;
  markerCount: number;
  snpCount: number;
  sampleType: "EU" | "AA" | "CUSTOM";
  timestamp: string;
  strMarkers: Record<string, { allele1: number; allele2: number }>;
  snpMarkers: Record<string, { rsid: string; genotype: string; trait?: string }>;
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
}

export const SAMPLE_CASE_EU: ActiveProfileData = {
  profileId: "CASE-2026-EU-GERMANIC-01",
  nodeId: "FORENSIC-LAB-ALPHA",
  markerCount: 24,
  snpCount: 55,
  sampleType: "EU",
  timestamp: "2026-08-12 18:30",
  strMarkers: {
    D3S1358: { allele1: 15, allele2: 17 },
    vWA: { allele1: 14, allele2: 17 },
    FGA: { allele1: 21, allele2: 23 },
    TH01: { allele1: 6, allele2: 9.3 },
    TPOX: { allele1: 8, allele2: 11 },
    CSF1PO: { allele1: 10, allele2: 12 },
    D5S818: { allele1: 11, allele2: 13 },
    D13S317: { allele1: 11, allele2: 14 },
    D7S820: { allele1: 8, allele2: 10 },
    D8S1179: { allele1: 13, allele2: 14 },
    D21S11: { allele1: 29, allele2: 31 },
    D18S51: { allele1: 14, allele2: 18 },
    D16S539: { allele1: 9, allele2: 12 },
    D2S1338: { allele1: 19, allele2: 23 },
    D19S433: { allele1: 13, allele2: 14 },
    SE33: { allele1: 24.2, allele2: 27.2 },
    AMEL: { allele1: 1, allele2: 2 }, // X, Y
    D1S1656: { allele1: 12, allele2: 15.3 },
    D12S391: { allele1: 17, allele2: 19 },
    D2S441: { allele1: 10, allele2: 14 },
    D10S1248: { allele1: 12, allele2: 15 },
    D22S1045: { allele1: 15, allele2: 16 },
    Penta_E: { allele1: 7, allele2: 12 },
    Penta_D: { allele1: 9, allele2: 13 },
  },
  snpMarkers: {
    rs12913832: { rsid: "rs12913832", genotype: "A/A", trait: "HERC2 - Blue Eyes" },
    rs1800407: { rsid: "rs1800407", genotype: "C/T", trait: "OCA2 Secondary Modifier" },
    rs16891982: { rsid: "rs16891982", genotype: "C/C", trait: "SLC45A2 Light Pigment" },
    rs3827072: { rsid: "rs3827072", genotype: "T/T", trait: "EDAR Straight Hair" },
    rs1426654: { rsid: "rs1426654", genotype: "A/A", trait: "SLC24A5 European Phototype" },
  },
  phenotype: {
    eyeColor: "Blue",
    eyeColorProb: 94.2,
    skinType: "Type I / II (Fair Skin)",
    skinTypeProb: 92.0,
    hairType: "Straight",
    hairTypeProb: 88.0,
    freckling: "Low / Moderate Ephelides",
  },
  ancestry: {
    primary: "European (North-Western)",
    primaryPct: 98.4,
    secondary: "Slavic / Baltic",
    secondaryPct: 1.6,
    populationCluster: "Germanic / Scandinavian Reference",
  },
  geoLocation: {
    lat: 52.5200,
    lng: 13.4050,
    cityRegion: "Berlin, Brandenburg",
    country: "Germany (EU)",
    confidencePct: 96.8,
  },
  kinshipLR: "1.42e8",
  epigeneticAge: 34.2,
};

export const SAMPLE_CASE_AA: ActiveProfileData = {
  profileId: "CASE-2026-AA-WESTAFR-02",
  nodeId: "DISTRICT-DNA-LAB-01",
  markerCount: 24,
  snpCount: 55,
  sampleType: "AA",
  timestamp: "2026-08-12 18:32",
  strMarkers: {
    D3S1358: { allele1: 16, allele2: 18 },
    vWA: { allele1: 15, allele2: 19 },
    FGA: { allele1: 22, allele2: 25 },
    TH01: { allele1: 7, allele2: 9 },
    TPOX: { allele1: 6, allele2: 8 },
    CSF1PO: { allele1: 11, allele2: 13 },
    D5S818: { allele1: 12, allele2: 14 },
    D13S317: { allele1: 10, allele2: 12 },
    D7S820: { allele1: 9, allele2: 11 },
    D8S1179: { allele1: 14, allele2: 15 },
    D21S11: { allele1: 28, allele2: 30 },
    D18S51: { allele1: 13, allele2: 17 },
    D16S539: { allele1: 11, allele2: 13 },
    D2S1338: { allele1: 17, allele2: 20 },
    D19S433: { allele1: 14, allele2: 15.2 },
    SE33: { allele1: 22, allele2: 26 },
    AMEL: { allele1: 1, allele2: 2 },
    D1S1656: { allele1: 14, allele2: 16 },
    D12S391: { allele1: 18, allele2: 20 },
    D2S441: { allele1: 11, allele2: 13 },
    D10S1248: { allele1: 13, allele2: 14 },
    D22S1045: { allele1: 11, allele2: 15 },
    Penta_E: { allele1: 11, allele2: 14 },
    Penta_D: { allele1: 10, allele2: 12 },
  },
  snpMarkers: {
    rs12913832: { rsid: "rs12913832", genotype: "G/G", trait: "HERC2 - Dark Iris" },
    rs1426654: { rsid: "rs1426654", genotype: "G/G", trait: "SLC24A5 Deep Skin Phototype" },
    rs3827072: { rsid: "rs3827072", genotype: "C/C", trait: "EDAR Non-Asian Variant" },
    rs7349332: { rsid: "rs7349332", genotype: "T/T", trait: "WNT10A Curly Hair" },
  },
  phenotype: {
    eyeColor: "Dark Brown / Black",
    eyeColorProb: 98.6,
    skinType: "Type V / VI (Deep Skin)",
    skinTypeProb: 96.0,
    hairType: "Curly / Coily",
    hairTypeProb: 94.0,
    freckling: "Absent",
  },
  ancestry: {
    primary: "West / Sub-Saharan African",
    primaryPct: 97.8,
    secondary: "Bantu / Central African",
    secondaryPct: 2.2,
    populationCluster: "Yoruba / West African Reference",
  },
  geoLocation: {
    lat: 6.5244,
    lng: 3.3792,
    cityRegion: "Lagos, West Coast",
    country: "Nigeria (AA)",
    confidencePct: 97.4,
  },
  kinshipLR: "9.84e7",
  epigeneticAge: 29.5,
};

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
  setActiveProfile: (profile: ActiveProfileData) => void;
  setToastBanner: (msg: string | null) => void;
  setInspectorOpen: (open: boolean) => void;
  clear: () => void;
}

export const useIngestStore = create<IngestState>((set) => ({
  lastIngestedProfileId: "CASE-2026-EU-GERMANIC-01",
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
    set({
      activeProfile: SAMPLE_CASE_EU,
      lastIngestedProfileId: SAMPLE_CASE_EU.profileId,
      lastIngestedNodeId: SAMPLE_CASE_EU.nodeId,
      markerCount: 24,
      isValid: true,
      toastBanner: `✓ Sample Case EU Loaded: ${SAMPLE_CASE_EU.profileId} (24 Extended STR Loci, 55 SNPs). Inferred: Blue Eyes (94.2%), European Ancestry (98.4%), Berlin, Germany (52.5200° N, 13.4050° E)`,
    });
  },

  loadSampleCaseAA: () => {
    set({
      activeProfile: SAMPLE_CASE_AA,
      lastIngestedProfileId: SAMPLE_CASE_AA.profileId,
      lastIngestedNodeId: SAMPLE_CASE_AA.nodeId,
      markerCount: 24,
      isValid: true,
      toastBanner: `✓ Sample Case AA Loaded: ${SAMPLE_CASE_AA.profileId} (24 Extended STR Loci, 55 SNPs). Inferred: Dark Eyes (98.6%), West African Ancestry (97.8%), Lagos, Nigeria (6.5244° N, 3.3792° E)`,
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
