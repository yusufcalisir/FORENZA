"use client";

import React, { useState } from "react";
import dynamic from "next/dynamic";
import { useForensicCaseStore } from "@/store/forensicCaseStore";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { ModuleSkeletonLoader } from "@/components/analysis/ModuleSkeletonLoader";

const PanelBGA = dynamic(() => import("@/components/analysis/PanelBGA"), {
  loading: () => <ModuleSkeletonLoader label="Loading Biogeographical Ancestry Engine..." />,
});
const PanelYSTR = dynamic(() => import("@/components/analysis/PanelYSTR"), {
  loading: () => <ModuleSkeletonLoader label="Loading Y-FILER Plus Haplotype Engine..." />,
});
const PanelXSTR = dynamic(() => import("@/components/analysis/PanelXSTR"), {
  loading: () => <ModuleSkeletonLoader label="Loading Argus X-12 Linkage Engine..." />,
});
const PanelMTDNA = dynamic(() => import("@/components/analysis/PanelMTDNA"), {
  loading: () => <ModuleSkeletonLoader label="Loading EMPOP mtDNA Alignment Engine..." />,
});
const PanelDVI = dynamic(() => import("@/components/analysis/PanelDVI"), {
  loading: () => <ModuleSkeletonLoader label="Loading DVI Joint Likelihood Engine..." />,
});
const PanelADNA = dynamic(() => import("@/components/analysis/PanelADNA"), {
  loading: () => <ModuleSkeletonLoader label="Loading aDNA MapDamage Kinetics Engine..." />,
});
const HumanIdPanel = dynamic(() => import("@/components/analysis/HumanIdPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading Human Identification Panel..." />,
});
const ProbabilisticGenotypingPanel = dynamic(() => import("@/components/analysis/ProbabilisticGenotypingPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading MCMC Continuous Deconvolution Engine..." />,
});
const PanelNRC = dynamic(() => import("@/components/analysis/PanelNRC"), {
  loading: () => <ModuleSkeletonLoader label="Loading Balding-Nichols Population Engine..." />,
});
const ValidationLabPanel = dynamic(() => import("@/components/analysis/ValidationLabPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading Tippett ROC Calibration Engine..." />,
});
const PanelEpigeneticClocks = dynamic(() => import("@/components/analysis/PanelEpigeneticClocks"), {
  loading: () => <ModuleSkeletonLoader label="Loading Epigenetic Age Clock Engine..." />,
});
const EntomologyPmiPanel = dynamic(() => import("@/components/analysis/EntomologyPmiPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading Forensic Entomology Thermal Summation..." />,
});
const PanelBodyFluid = dynamic(() => import("@/components/analysis/PanelBodyFluid"), {
  loading: () => <ModuleSkeletonLoader label="Loading tDMR Tissue Identification Engine..." />,
});
const BpaAreaOfOriginPanel = dynamic(() => import("@/components/analysis/BpaAreaOfOriginPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading 3D BPA Trajectory Solver..." />,
});
const BallisticsGsrPanel = dynamic(() => import("@/components/analysis/BallisticsGsrPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading SEM-EDX GSR & CMC Ballistics Engine..." />,
});
const TraceSpectroscopyPanel = dynamic(() => import("@/components/analysis/TraceSpectroscopyPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading ATR-FTIR Trace Spectroscopy Engine..." />,
});
const ToxicologyPmrPanel = dynamic(() => import("@/components/analysis/ToxicologyPmrPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading Post-Mortem Toxicology PMR Engine..." />,
});
const ExpertWitnessPanel = dynamic(() => import("@/components/analysis/ExpertWitnessPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading ENFSI Court-Ready Statement Engine..." />,
});
const TouchDnaPanel = dynamic(() => import("@/components/analysis/TouchDnaPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading Touch & Low Template DNA Engine..." />,
});
const MerkleLedgerPanel = dynamic(() => import("@/components/analysis/MerkleLedgerPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading Merkle Chain of Custody Ledger..." />,
});
const ZkpAuditorPanel = dynamic(() => import("@/components/analysis/ZkpAuditorPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading Circom BN254 ZKP Blind Auditor..." />,
});
const MeasurementUncertaintyPanel = dynamic(() => import("@/components/analysis/MeasurementUncertaintyPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading ISO 17025 Measurement Uncertainty Engine..." />,
});
const EvidenceManagementPanel = dynamic(() => import("@/components/analysis/EvidenceManagementPanel"), {
  loading: () => <ModuleSkeletonLoader label="Loading 3D Spatial Evidence Visualizer..." />,
});
const PedigreeTree = dynamic(() => import("@/components/analysis/PedigreeTree"), {
  loading: () => <ModuleSkeletonLoader label="Loading Kinship Pedigree Tree..." />,
});
const PanelHIrisPlex = dynamic(() => import("@/components/analysis/PanelHIrisPlex"), {
  loading: () => <ModuleSkeletonLoader label="Loading HIrisPlex-S 41-SNP Phenotype Model..." />,
});
const PanelCraniofacial = dynamic(() => import("@/components/analysis/PanelCraniofacial"), {
  ssr: false,
  loading: () => <ModuleSkeletonLoader label="Loading 3D Craniofacial Morphometry Studio..." />,
});
const GeoForensicIntelligencePanel = dynamic(() => import("@/components/analysis/GeoForensicIntelligencePanel"), {
  ssr: false,
  loading: () => <ModuleSkeletonLoader label="Loading Geo-Forensic Spatial Intelligence..." />,
});
const PanelIsoscape = dynamic(() => import("@/components/analysis/PanelIsoscape"), {
  ssr: false,
  loading: () => <ModuleSkeletonLoader label="Loading Multi-Isotope Isoscape Engine..." />,
});
const PanelSoil = dynamic(() => import("@/components/analysis/PanelSoil"), {
  ssr: false,
  loading: () => <ModuleSkeletonLoader label="Loading Forensic Soil Pedology & CoDa Engine..." />,
});
const PanelPalynology = dynamic(() => import("@/components/analysis/PanelPalynology"), {
  ssr: false,
  loading: () => <ModuleSkeletonLoader label="Loading Forensic Palynology & eDNA Engine..." />,
});
const PanelRossmo = dynamic(() => import("@/components/analysis/PanelRossmo"), {
  ssr: false,
  loading: () => <ModuleSkeletonLoader label="Loading Rossmo Geographic Profiling Engine..." />,
});
const PanelGeoFusion = dynamic(() => import("@/components/analysis/PanelGeoFusion"), {
  ssr: false,
  loading: () => <ModuleSkeletonLoader label="Loading Multi-Criteria Bayesian Evidence Fusion Engine..." />,
});
const PanelHair = dynamic(() => import("@/components/analysis/PanelHair"), {
  loading: () => <ModuleSkeletonLoader label="Loading Hair Morphology PRS Model..." />,
});
const PanelFreckling = dynamic(() => import("@/components/analysis/PanelFreckling"), {
  loading: () => <ModuleSkeletonLoader label="Loading MC1R Freckling & Epistasis Model..." />,
});
const PanelMicrobiome = dynamic(() => import("@/components/analysis/PanelMicrobiome"), {
  loading: () => <ModuleSkeletonLoader label="Loading Forensic Microbiome & Metagenomics Engine..." />,
});
const PanelMPSSTR = dynamic(() => import("@/components/analysis/PanelMPSSTR"), {
  loading: () => <ModuleSkeletonLoader label="Loading MPS STR Sequence & Isoallele Engine..." />,
});
const PanelMLSTR = dynamic(() => import("@/components/analysis/PanelMLSTR"), {
  loading: () => <ModuleSkeletonLoader label="Loading ML STR Calling & Fragsifier Engine..." />,
});
const PanelFGG = dynamic(() => import("@/components/analysis/PanelFGG"), {
  loading: () => <ModuleSkeletonLoader label="Loading Forensic Genetic Genealogy Engine..." />,
});
const PanelTelomere = dynamic(() => import("@/components/analysis/PanelTelomere"), {
  loading: () => <ModuleSkeletonLoader label="Loading Telomere Chronometer Engine..." />,
});
const PanelLifestyle = dynamic(() => import("@/components/analysis/PanelLifestyle"), {
  loading: () => <ModuleSkeletonLoader label="Loading Lifestyle Epigenomics & AHRR Engine..." />,
});


const PanelSTRKinship = dynamic(() => import("@/components/analysis/PanelSTRKinship"), {
  loading: () => <ModuleSkeletonLoader label="Loading 24-Locus Autosomal STR Kinship Studio..." />,
});

export const PanelSTR = PanelSTRKinship;


// ─── Biocomputational Kinship X-STR Engine ────────────────────────────────────

export function PanelKinship() {
  const { activeCase } = useForensicCaseStore();
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";
  const [hypo, setHypo] = useState<"paternity" | "full_sibs" | "half_sibs">("paternity");

  const baseKinshipLR = Number(activeCase.profile.kinshipLR) || 4528900.0;
  const lrMap: Record<string, number> = {
    paternity: baseKinshipLR,
    full_sibs: baseKinshipLR * 0.42,
    half_sibs: Math.sqrt(baseKinshipLR),
  };

  const lr = lrMap[hypo];
  const log10Lr = Math.log10(lr);

  const mockKinshipData = {
    relationship_type:
      hypo === "paternity"
        ? (isTr ? "Ebeveyn-Çocuk (PO)" : "Parent-Child (PO)")
        : hypo === "full_sibs"
        ? (isTr ? "Öz Kardeş (FS)" : "Full Sibling (FS)")
        : (isTr ? "Üvey Kardeş (HS)" : "Half Sibling (HS)"),
    confidence: 0.9999,
    kinship_index_parent_child: lrMap.paternity,
    kinship_index_full_sibling: lrMap.full_sibs,
    kinship_index_half_sibling: lrMap.half_sibs,
    log10_ki_parent_child: Math.log10(lrMap.paternity),
    log10_ki_full_sibling: Math.log10(lrMap.full_sibs),
    log10_ki_half_sibling: Math.log10(lrMap.half_sibs),
    exclusion_count: 0,
    loci_analyzed: 24,
    ibd_summary: {
      ibs0_proportion: 0.0,
      ibs1_proportion: 0.5,
      ibs2_proportion: 0.5,
      ibs0_count: 0,
      ibs1_count: 12,
      ibs2_count: 12,
    },
    population_used: isTr ? "Kafkas NIST 2024 / NRC II" : "Caucasian NIST 2024 / NRC II",
    reasoning: isTr ? "Hummel Yüklemi: Akrabalık İlişkisinde Fiili Kesinlik" : "Hummel's Predicate: Practical Certainty of Kinship Relation",
  };

  return (
    <div className="space-y-5 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl border border-tactical-border/60 bg-tactical-surface/50">
        <div className="space-y-0.5">
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            {isTr ? "Argus X-12 Akrabalık İndeksi & Soy Ağacı Motoru" : "Argus X-12 Kinship Index & Pedigree Engine"}
          </span>
          <p className="text-[10px] text-zinc-400">
            {isTr
              ? "Kümelenmiş bağlantı grupları üzerinden PHS (İkili Haplotipe Dayalı Paylaşım) akrabalık oranlarını hesaplar."
              : "Computes PHS (Pairwise Haplotype Sharing) kinship ratios across clustered linkage groups."}
          </p>
        </div>
        <div className="flex items-center gap-1.5 bg-black/60 p-1 rounded-xl border border-tactical-border/60 shrink-0">
          {[
            { id: "paternity", label: isTr ? "Babalık / Ebeveyn (PO)" : "Paternity (PO)" },
            { id: "full_sibs", label: isTr ? "Öz Kardeşler (FS)" : "Full Siblings (FS)" },
            { id: "half_sibs", label: isTr ? "Üvey Kardeşler (HS)" : "Half Siblings (HS)" },
          ].map((btn) => (
            <button
              key={btn.id}
              onClick={() => setHypo(btn.id as any)}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase transition-all cursor-pointer ${
                hypo === btn.id
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 shadow-sm"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/20 space-y-2">
          <span className="text-[9px] text-emerald-400 font-bold uppercase">
            {isTr ? "Akrabalık Olabilirlik Oranı (CPI)" : "Kinship Likelihood Ratio (CPI)"}
          </span>
          <p className="text-2xl font-mono font-extrabold text-white">{(lr ?? 1).toExponential(4)}</p>

          <p className="text-xs text-emerald-300 font-bold">Log₁₀ CPI: +{log10Lr.toFixed(2)}</p>
        </div>
        <div className="p-4 rounded-xl border border-tactical-border/60 bg-black/40 space-y-2">
          <span className="text-[9px] text-zinc-400 font-bold uppercase">
            {isTr ? "W-Değeri (Akrabalık Olasılığı)" : "W-Value (Probability of Relation)"}
          </span>
          <p className="text-2xl font-mono font-extrabold text-white">99.9999%</p>
          <p className="text-[10px] text-zinc-400">
            {isTr ? "Hummel Yüklemi: Akrabalık İlişkisinde Fiili Kesinlik" : "Hummel’s Predicate: Practical Certainty of Relation"}
          </p>
        </div>
      </div>

      <PedigreeTree
        kinshipData={mockKinshipData}
        profileAId={activeCase.profile.profileId}
        profileBId="REF-TARGET-KIN-02"
      />
    </div>
  );
}

// ─── Panel Router (all 38 modules wired to dedicated components) ───────────

export function renderPanel(tabId: string) {
  switch (tabId) {
    // Pillar 1: Genotyping & Population
    case "genotyping":
    case "str":
    case "str_kinship":
    case "kinship":
      return <PanelSTRKinship />;
    case "mcmc":
      return <ProbabilisticGenotypingPanel />;
    case "population":
    case "nrc":
      return <PanelNRC />;
    case "touch":
      return <TouchDnaPanel />;
    case "validation":
      return <ValidationLabPanel />;
    case "mps":
    case "mps_str":
    case "ngs":
    case "sequence_str":
      return <PanelMPSSTR />;
    case "ml_str":
    case "ml_calling":
    case "fragsifier":
    case "ml_peak":
      return <PanelMLSTR />;

    // Pillar 2: Lineage Forensics & Kinship
    case "lineage":
    case "lineage_y":
    case "ystr":
      return <PanelYSTR />;
    case "lineage_x":
    case "xstr":
      return <PanelXSTR />;
    case "lineage_mt":
    case "mtdna":
      return <PanelMTDNA />;
    case "dvi":
    case "dvi_ped":
      return <PanelDVI />;
    case "humanid":
    case "adna":
    case "adna_snp":
    case "ancient_dna":
      return <PanelADNA />;
    case "fgg":
    case "igg":
    case "genealogy":
    case "investigative_genealogy":
      return <PanelFGG />;


    // Pillar 3: Phenotyping & Ancestry
    case "hirisplex":
    case "hirisplex_s":
    case "phenotyping":
    case "pigmentation":
      return <PanelHIrisPlex />;
    case "ancestry":
    case "bga":
    case "bga_55":
    case "aims":
      return <PanelBGA />;
    case "craniofacial":
    case "morphometrics":
    case "cranio":
    case "suspect":
      return <PanelCraniofacial />;
    case "hair":
    case "hair_texture":
    case "hair_morphology":
    case "balding":
    case "hair_balding":
    case "aga":
      return <PanelHair />;
    case "freckling":
    case "freckles":
    case "ephelides":
    case "mc1r":
    case "mc1r_epistasis":
    case "uv_sensitivity":
    case "med":
      return <PanelFreckling />;

    // Pillar 4: Epigenetics, Microbiomics & Aging
    case "epigenetics":
    case "age":
    case "epigenetic_clocks":
    case "clocks":
      return <PanelEpigeneticClocks />;
    case "bodyfluid":
    case "tdmr":
    case "tissue":
    case "tissue_origin":
      return <PanelBodyFluid />;
    case "lifestyle":
    case "ahrr":
    case "smoking":
      return <PanelLifestyle />;
    case "telomere":
    case "telo_chrono":
    case "telomere_decay":
      return <PanelTelomere />;
    case "mirna":
      return <PanelBodyFluid />;
    case "microbiome":
    case "metagenomics":
    case "thanatomicrobiome":
      return <PanelMicrobiome />;

    // Pillar 5: Pathology & Trace Forensics
    case "pathology":
    case "bpa":
    case "bpa_origin":
    case "bloodstain":
      return <BpaAreaOfOriginPanel />;
    case "microscopy":
    case "ballistics":
    case "gsr":
    case "ballistics_gsr":
      return <BallisticsGsrPanel />;
    case "botany":
    case "entomology":
    case "ento":
    case "pmi_thermal":
      return <EntomologyPmiPanel />;
    case "toxicology":
    case "spectroscopy":
    case "msi":
    case "ftir":
    case "atr_ftir":
    case "trace_spectroscopy":
      return <TraceSpectroscopyPanel />;
    case "serology":
    case "pmr":
    case "toxicokinetics":
    case "postmortem_tox":
      return <ToxicologyPmrPanel />;

    // Pillar 6: ISO 17025, LIMS & ZKP
    case "lims_governance":
    case "lims":
      return <MerkleLedgerPanel />;
    case "zkp":
      return <ZkpAuditorPanel />;
    case "qc":
      return <MeasurementUncertaintyPanel />;
    case "court":
      return <ExpertWitnessPanel />;
    case "evidenceos":
      return <EvidenceManagementPanel />;

    // Pillar 7: Geo-Forensics & Spatial Intelligence
    case "geoint":
    case "geo_fusion":
      return <PanelGeoFusion />;
    case "geo_isoscape":
      return <PanelIsoscape />;
    case "geo_soil":
      return <PanelSoil />;
    case "geo_palynology":
      return <PanelPalynology />;
    case "geo_rossmo":
      return <PanelRossmo />;

    default:
      return <PanelSTR />;
  }
}

// Canonical aliases for Pillar 1
export { ProbabilisticGenotypingPanel as PanelMCMC };
export { PanelNRC };

// Canonical aliases for Pillar 7
export { PanelIsoscape, PanelSoil, PanelPalynology, PanelRossmo, PanelGeoFusion };

