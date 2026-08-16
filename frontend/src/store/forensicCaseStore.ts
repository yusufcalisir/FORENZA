import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface StrLocusData {
  allele1: number;
  allele2: number;
}

export interface SnpMarkerData {
  rsid: string;
  genotype: string;
  trait?: string;
}

export interface PhenotypeData {
  eyeColor: string;
  eyeColorProb: number;
  skinType: string;
  skinTypeProb: number;
  hairType: string;
  hairTypeProb: number;
  freckling: string;
}

export interface AncestryData {
  primary: string;
  primaryPct: number;
  secondary: string;
  secondaryPct: number;
  populationCluster: string;
}

export interface GeoLocationData {
  lat: number;
  lng: number;
  cityRegion: string;
  country: string;
  confidencePct: number;
}

export interface ForensicProfile {
  profileId: string;
  nodeId: string;
  sampleType: "EU" | "AA" | "EAS" | "SAS" | "DVI" | "TOUCH" | "MIX" | "CUSTOM";
  markerCount: number;
  snpCount: number;
  timestamp: string;
  strMarkers: Record<string, StrLocusData>;
  snpMarkers: Record<string, SnpMarkerData>;
  phenotype: PhenotypeData;
  ancestry: AncestryData;
  geoLocation: GeoLocationData;
  kinshipLR: string;
  epigeneticAge: number;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  event: string;
  module: string;
  analyst: string;
  hmac: string;
  status: "PASS" | "WARNING" | "FAIL"; // Execution & chain of custody integrity
  findingSeverity?: "NOMINAL" | "INFORMATIONAL" | "ELEVATED" | "CRITICAL_ALERT"; // Clinical/Forensic Finding Result
  standard: string;
  polygonTx?: string;
}

export interface ForensicCaseMetadata {
  caseId: string;
  caseTitle: string;
  jurisdiction: string;
  leadAnalyst: string;
  status: "ACTIVE_PROCESSING" | "PEER_REVIEW" | "COURT_READY" | "ARCHIVED";
  openedAt: string;
  classification: string;
}

export interface ForensicCase {
  metadata: ForensicCaseMetadata;
  profile: ForensicProfile;
}

// ─── CANONICAL GROUND-TRUTH CASES ───────────────────────────────────────────

export const SAMPLE_CASE_EU: ForensicCase = {
  metadata: {
    caseId: "CASE-2026-EU-GERMANIC-01",
    caseTitle: "Central European High-LR Identification",
    jurisdiction: "EU-BKA / INTERPOL",
    leadAnalyst: "Dr. Morrison, Lead Forensic Geneticist",
    status: "COURT_READY",
    openedAt: "2026-08-12 09:15:00 UTC",
    classification: "CONFIDENTIAL // ISO 17025 CASEWORK",
  },
  profile: {
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
      AMEL: { allele1: 1, allele2: 2 },
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
      skinTypeProb: 92.8,
      hairType: "Straight",
      hairTypeProb: 88.0,
      freckling: "Low / Moderate Ephelides",
    },
    ancestry: {
      primary: "North-Western European",
      primaryPct: 86.4,
      secondary: "Baltic / Slavic",
      secondaryPct: 11.2,
      populationCluster: "EUR-G01 (Germanic-Alpine)",
    },
    geoLocation: {
      lat: 48.1351,
      lng: 11.582,
      cityRegion: "Munich / Bavaria",
      country: "Germany (DE)",
      confidencePct: 91.5,
    },
    kinshipLR: "2.51e18",
    epigeneticAge: 38.2,
  },
};

export const SAMPLE_CASE_AA: ForensicCase = {
  metadata: {
    caseId: "CASE-2026-AA-SOUTHERN-02",
    caseTitle: "Sub-Saharan Lineage Reference Case",
    jurisdiction: "AFRIPOL / INTERPOL",
    leadAnalyst: "Dr. Chen, Senior Genomics Examiner",
    status: "ACTIVE_PROCESSING",
    openedAt: "2026-08-14 14:20:00 UTC",
    classification: "RESTRICTED // MULTI-OMIC COMPARISON",
  },
  profile: {
    profileId: "CASE-2026-AA-SOUTHERN-02",
    nodeId: "CENTRAL-GENOMICS-NODE",
    markerCount: 24,
    snpCount: 55,
    sampleType: "AA",
    timestamp: "2026-08-14 14:45",
    strMarkers: {
      D3S1358: { allele1: 16, allele2: 18 },
      vWA: { allele1: 15, allele2: 19 },
      FGA: { allele1: 22, allele2: 25 },
      TH01: { allele1: 7, allele2: 9 },
      TPOX: { allele1: 9, allele2: 12 },
      CSF1PO: { allele1: 11, allele2: 13 },
      D5S818: { allele1: 12, allele2: 14 },
      D13S317: { allele1: 10, allele2: 12 },
      D7S820: { allele1: 10, allele2: 11 },
      D8S1179: { allele1: 14, allele2: 15 },
      D21S11: { allele1: 28, allele2: 30 },
      D18S51: { allele1: 15, allele2: 19 },
      D16S539: { allele1: 11, allele2: 13 },
      D2S1338: { allele1: 21, allele2: 24 },
      D19S433: { allele1: 14, allele2: 15.2 },
      SE33: { allele1: 26.2, allele2: 30.2 },
      AMEL: { allele1: 1, allele2: 2 },
      D1S1656: { allele1: 14, allele2: 16.3 },
      D12S391: { allele1: 18, allele2: 21 },
      D2S441: { allele1: 11, allele2: 13 },
      D10S1248: { allele1: 13, allele2: 16 },
      D22S1045: { allele1: 16, allele2: 17 },
      Penta_E: { allele1: 10, allele2: 14 },
      Penta_D: { allele1: 11, allele2: 14 },
    },
    snpMarkers: {
      rs12913832: { rsid: "rs12913832", genotype: "G/G", trait: "HERC2 - Brown Eyes" },
      rs1800407: { rsid: "rs1800407", genotype: "C/C", trait: "OCA2 Dark Modifier" },
      rs16891982: { rsid: "rs16891982", genotype: "G/G", trait: "SLC45A2 Dark Pigment" },
      rs3827072: { rsid: "rs3827072", genotype: "C/C", trait: "EDAR Curly/Coarse Hair" },
      rs1426654: { rsid: "rs1426654", genotype: "G/G", trait: "SLC24A5 African Phototype" },
    },
    phenotype: {
      eyeColor: "Brown",
      eyeColorProb: 91.4,
      skinType: "Type V / VI (Deep Dark)",
      skinTypeProb: 94.5,
      hairType: "Curly / Coarse",
      hairTypeProb: 96.0,
      freckling: "Absent",
    },
    ancestry: {
      primary: "West African / Sub-Saharan",
      primaryPct: 92.1,
      secondary: "East African Pastoralist",
      secondaryPct: 6.4,
      populationCluster: "AFR-W02 (Yoruba-Bantu)",
    },
    geoLocation: {
      lat: 6.5244,
      lng: 3.3792,
      cityRegion: "Lagos Maritime District",
      country: "Nigeria (NG)",
      confidencePct: 88.0,
    },
    kinshipLR: "1.74e17",
    epigeneticAge: 29.5,
  },
};

export const INITIAL_AUDIT_LOGS: AuditEntry[] = [
  { id: "AUD-0896", timestamp: "2026-08-15 16:32:05", event: "Toxicology LC-MS/MS & Widmark BAC: Morphine 0.85 mg/L — FATAL threshold exceeded", module: "23. Post-Mortem GC-MS Tox", analyst: "Dr. Alvarez", hmac: "f9d12a8…b41e", status: "PASS", findingSeverity: "CRITICAL_ALERT", standard: "ISO 17025 / SOFT", polygonTx: "0x7c99...11fe" },
  { id: "AUD-0895", timestamp: "2026-08-15 16:30:12", event: "STR 24-locus profile verified — CASE-2026-EU-GERMANIC-01", module: "01. Autosomal STR Engine", analyst: "Dr. Morrison", hmac: "a7f9c21…e04b", status: "PASS", findingSeverity: "NOMINAL", standard: "ISO 17025 §5.4", polygonTx: "0x3a8f...4e19" },
  { id: "AUD-0894", timestamp: "2026-08-15 16:28:44", event: "HIrisPlex-S 24-SNP phenotype report compiled", module: "11. HIrisPlex-S Pigmentation", analyst: "Dr. Chen", hmac: "b3d82f4…a19c", status: "PASS", findingSeverity: "INFORMATIONAL", standard: "SWGDAM 2023", polygonTx: "0x8e21...12ab" },
  { id: "AUD-0893", timestamp: "2026-08-15 16:22:15", event: "Metropolis-Hastings 3-contributor mixture deconvolution", module: "02. MCMC Mixture Deconvolution", analyst: "Dr. Morrison", hmac: "c1e45b7…d52a", status: "PASS", findingSeverity: "ELEVATED", standard: "ILAC G19", polygonTx: "0x91d4...f7c2" },
  { id: "AUD-0892", timestamp: "2026-08-15 16:15:30", event: "Horvath 5-CpG epigenetic age clock (38.2 ± 2.8 yr)", module: "16. Horvath Epigenetic Clock", analyst: "Dr. Chen", hmac: "e4a67c9…b23d", status: "PASS", findingSeverity: "NOMINAL", standard: "ENFSI 2022", polygonTx: "0x4b77...8811" },
  { id: "AUD-0891", timestamp: "2026-08-15 16:05:19", event: "Circom Groth16 ZKP proof generated & verified", module: "28. Circom ZKP Auditor", analyst: "System Enclave", hmac: "h5c41d8…f23e", status: "PASS", findingSeverity: "NOMINAL", standard: "Circom BN254", polygonTx: "0x6f31...cc44" },
];

export interface ForensicCaseStore {
  activeCase: ForensicCase;
  availableCases: ForensicCase[];
  auditTrail: AuditEntry[];
  
  // Actions
  selectCase: (caseId: string) => void;
  updateActiveProfile: (updates: Partial<ForensicProfile>) => void;
  addAuditLog: (entry: Omit<AuditEntry, "id" | "timestamp" | "hmac">) => void;
  resetToDefault: () => void;
}

export const useForensicCaseStore = create<ForensicCaseStore>()(
  persist(
    (set, get) => ({
      activeCase: SAMPLE_CASE_EU,
      availableCases: [SAMPLE_CASE_EU, SAMPLE_CASE_AA],
      auditTrail: INITIAL_AUDIT_LOGS,

      selectCase: (caseId: string) => {
        const found = get().availableCases.find((c) => c.metadata.caseId === caseId);
        if (found) {
          const timestamp = new Date().toISOString().replace("T", " ").substring(0, 19);
          const newAudit: AuditEntry = {
            id: `AUD-${Math.floor(1000 + Math.random() * 9000)}`,
            timestamp,
            event: `Switched active case to ${found.metadata.caseId}`,
            module: "Case Manager",
            analyst: "Active Session",
            hmac: Math.random().toString(36).substring(2, 10) + "…" + Math.random().toString(36).substring(2, 6),
            status: "PASS",
            standard: "ISO 17025 §5.4",
            polygonTx: "0x" + Array.from({ length: 8 }, () => Math.floor(Math.random() * 16).toString(16)).join("") + "...",
          };

          set((state) => ({
            activeCase: found,
            auditTrail: [newAudit, ...state.auditTrail],
          }));
        }
      },

      updateActiveProfile: (updates: Partial<ForensicProfile>) => {
        set((state) => ({
          activeCase: {
            ...state.activeCase,
            profile: {
              ...state.activeCase.profile,
              ...updates,
            },
          },
        }));
      },

      addAuditLog: (entry) => {
        const timestamp = new Date().toISOString().replace("T", " ").substring(0, 19);
        const newEntry: AuditEntry = {
          ...entry,
          id: `AUD-${Math.floor(1000 + Math.random() * 9000)}`,
          timestamp,
          hmac: Math.random().toString(36).substring(2, 10) + "…" + Math.random().toString(36).substring(2, 6),
          polygonTx: "0x" + Array.from({ length: 8 }, () => Math.floor(Math.random() * 16).toString(16)).join("") + "...",
        };
        set((state) => ({
          auditTrail: [newEntry, ...state.auditTrail],
        }));
      },

      resetToDefault: () => {
        set({
          activeCase: SAMPLE_CASE_EU,
          availableCases: [SAMPLE_CASE_EU, SAMPLE_CASE_AA],
          auditTrail: INITIAL_AUDIT_LOGS,
        });
      },
    }),
    {
      name: "forenza-case-state-v2",
    }
  )
);
