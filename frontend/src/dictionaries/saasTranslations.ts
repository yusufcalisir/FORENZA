export type SaasLanguage = "en" | "tr";

export interface SubsystemItem {
  id: string;
  name: string;
  badge: string;
  metrics: string;
  desc: string;
}

export interface PillarItem {
  name: string;
  shortName: string;
  badge: string;
  subsystems: SubsystemItem[];
}

export interface ArchitectureLayerItem {
  layer: string;
  badge: string;
  nodes: string[];
}

export interface SecurityPillarItem {
  title: string;
  desc: string;
}

export interface SecuritySpecItem {
  label: string;
  value: string;
}

export interface SolutionItem {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  bulletPoints: string[];
  sampleMetric: string;
  sampleCode: string;
  label: string;
}

export interface SaasTranslation {
  header: {
    bioSimulator: string;
    subsystems: string;
    architecture: string;
    security: string;
    launchDemo: string;
  };
  hero: {
    badge: string;
    titleMain: string;
    titleHighlight: string;
    subtitle: string;
    launchDemo: string;
    exploreSubsystems: string;
    subsystemsStat: string;
    invariantsStat: string;
    courtStat: string;
    privacyStat: string;
  };
  solutions: {
    badge: string;
    title: string;
    subtitle: string;
    domainInspection: string;
    activeStandard: string;
    primaryMetric: string;
    sessionTarget: string;
    verificationStatus: string;
    auditPassed: string;
    items: SolutionItem[];
  };
  bioSimulator: {
    badge: string;
    title: string;
    subtitle: string;
    tabs: {
      phenotype: string;
      str: string;
      zkp: string;
    };
    phenotypeTab: {
      eyeColors: { blue: string; hazel: string; brown: string };
      skinTypes: { vPale: string; fair: string; medium: string; olive: string; dBrown: string; dBlack: string };
      hairTypes: { straight: string; wavy: string; curly: string };
      irisTitle: string;
      irisSub: string;
      targetGenotype: string;
      secondaryMarker: string;
      posteriorProb: string;
      confidence: string;
      skinTitle: string;
      skinSub: string;
      hairTitle: string;
      hairSub: string;
      summaryTitle: string;
      synced: string;
      predictedIris: string;
      skinPhototypeLabel: string;
      hairScore: string;
      accuracy: string;
    };
    strTab: {
      electropherogramTitle: string;
      codisPanel: string;
      alleleLabel: string;
      rfuLabel: string;
      alleleCall: string;
      popFreq: string;
      locusLr: string;
    };
    zkpTab: {
      circuitId: string;
      provingScheme: string;
      privateWitness: string;
      publicSignal: string;
      executeBtn: string;
      computing: string;
      latency: string;
      proofSuccess: string;
      provenMsg: string;
      resetBtn: string;
      consoleTitle: string;
      initInfo: string;
      readingInfo: string;
      witnessInfo: string;
      successCreated: string;
      testnetReady: string;
      zeroLeakage: string;
      publicHash: string;
    };
  };
  subsystems: {
    badge: string;
    title: string;
    subtitle: string;
    searchPlaceholder: string;
    activeCount: string;
    operationalStatus: string;
    totalSubsystemsLabel: string;
    totalSubsystemsValue: string;
    archLayersLabel: string;
    archLayersValue: string;
    pytestInvariantsLabel: string;
    pytestInvariantsValue: string;
    standardComplianceLabel: string;
    standardComplianceValue: string;
    pillars: PillarItem[];
  };
  architecture: {
    badge: string;
    title: string;
    subtitle: string;
    layers: ArchitectureLayerItem[];
  };
  security: {
    badge: string;
    title: string;
    subtitle: string;
    matrixTitle: string;
    passedBadge: string;
    pillars: SecurityPillarItem[];
    specs: SecuritySpecItem[];
  };
  faq: {
    badge: string;
    title: string;
    subtitle: string;
    questions: {
      q1: string;
      a1: string;
      q2: string;
      a2: string;
      q3: string;
      a3: string;
      q4: string;
      a4: string;
      q5: string;
      a5: string;
    };
  };
  footer: {
    rights: string;
    tagline: string;
    brandSubtitle: string;
    status: string;
    columns: {
      col1Title: string;
      col1Links: string[];
      col2Title: string;
      col2Links: string[];
      col3Title: string;
      col3Links: string[];
    };
    disclaimer: {
      badge: string;
      title: string;
      text: string;
      isoNote: string;
    };
  };
}

export const saasTranslations: Record<SaasLanguage, SaasTranslation> = {
  en: {
    header: {
      bioSimulator: "Bio-Simulator",
      subsystems: "35 Subsystems",
      architecture: "Evidence DAG",
      security: "Security & ISO",
      launchDemo: "Launch FORENZA OS",
    },
    hero: {
      badge: "Multi-Omic Forensic Evidence OS",
      titleMain: "Integrated Biocomputational",
      titleHighlight: "Forensic Evidence OS",
      subtitle: "Enterprise multi-omic biocomputational platform integrating Autosomal & Lineage STRs, MCMC Probabilistic Genotyping, HIrisPlex-S Phenotyping, Horvath Epigenetics, Physical Ballistics & BPA, Geo-Forensic GIS Intelligence, LIMS Workflow, and ISO 17025 Court Reporting.",
      launchDemo: "Launch FORENZA OS",
      exploreSubsystems: "Explore 35 Modules",
      subsystemsStat: "Forensic Subsystems",
      invariantsStat: "Verified Invariants",
      courtStat: "Court Admissible",
      privacyStat: "Privacy Auditor",
    },
    solutions: {
      badge: "Application Domains",
      title: "Built for High-Stakes Environments",
      subtitle: "FORENZA addresses the specific operational demands of four distinct forensic and scientific disciplines.",
      domainInspection: "DOMAIN INSPECTION",
      activeStandard: "Active Standard",
      primaryMetric: "PRIMARY METRIC OUTPUT",
      sessionTarget: "Session Target Reference",
      verificationStatus: "Verification Status",
      auditPassed: "Passed NRC II Audit",
      items: [
        {
          id: "law-enforcement",
          title: "Law Enforcement and Cold Cases",
          subtitle: "Familial Searching & Degraded Sample LR Matching",
          description: "Forensic units can upload partial or degraded STR profiles recovered from crime scenes and receive rapid likelihood ratio assessments against reference samples. The kinship engine identifies probable family relations when a direct match is unavailable, enabling familial searching workflows for unresolved cold cases.",
          bulletPoints: [
            "Partial profile LR calculation with missing loci handling",
            "Familial search across multi-generational pedigrees",
            "Geo-ancestry heatmap targeting for investigative geography",
            "Immutable blockchain report for court admissibility",
          ],
          sampleMetric: "1.42e8 Likelihood Ratio",
          sampleCode: "CASE_2026_COLD_09 — NDIS CODIS Core 20 Loci Database Hit",
          label: "Law Enforcement",
        },
        {
          id: "dvi",
          title: "Disaster Victim Identification (DVI)",
          subtitle: "Mass Casualty Rematch & Rapid Kinship Indexing",
          description: "In mass casualty events, FORENZA provides rapid kinship indexing to match unidentified remains against family reference samples. The platform supports concurrent multi-sample processing with quality scoring, allowing identification teams to prioritize high-confidence matches under operational pressure.",
          bulletPoints: [
            "Concurrent multi-sample batch processing",
            "Parent-child and sibling KI within minutes",
            "Sample quality and degradation scoring",
            "Interpol DVI compatible report export",
          ],
          sampleMetric: "99.999% Match Probability",
          sampleCode: "DVI_BATCH_402 — Interpol Section 4 Standard",
          label: "DVI Operations",
        },
        {
          id: "border-security",
          title: "Border Security & Kinship Verification",
          subtitle: "NRC II Framework & Zero-Knowledge Identity Check",
          description: "Verify declared kinship relationships at processing centers with statistical rigor. Likelihood ratios computed under the NRC II framework provide objective evidence that is resistant to interpretation bias. ZK verification allows identity confirmation without centralizing sensitive genetic data.",
          bulletPoints: [
            "NRC II LR computation for claimed relationships",
            "ZK verification without central data exposure",
            "Geo-ancestry cross-reference for documentation verification",
            "Real-time processing with node-distributed computation",
          ],
          sampleMetric: "Zero Data Exposure (ZKP)",
          sampleCode: "BORDER_CHECK_882 — Groth16 Verified",
          label: "Border Security",
        },
        {
          id: "research",
          title: "Academic & Clinical Genetics Research",
          subtitle: "Population Stratification & GTEx eQTL Integration",
          description: "Research institutions can leverage FORENZA as a validated computational framework for population genetics studies. The platform provides reproducible LR calculations, exportable allele frequency matrices, and GTEx eQTL cross-references for 54 tissue types, supporting peer-reviewed genomics research.",
          bulletPoints: [
            "Exportable allele frequency matrices and LR results",
            "GTEx eQTL data integration for 54 tissue types",
            "Reproducible and auditable computation pipeline",
            "Population stratification analysis and theta correction",
          ],
          sampleMetric: "54 Tissue eQTL Mapped",
          sampleCode: "GENOMICS_STUDY_V2 — Balding-Nichols theta=0.03",
          label: "Research Labs",
        },
      ],
    },
    bioSimulator: {
      badge: "Live Interactive Engine Sandbox",
      title: "Real-Time Bio-Simulator & Pipeline Testbench",
      subtitle: "Simulate multi-sample STR allele deconvolution, kinship likelihood ratios, and HIrisPlex-S phenotyping in real time.",
      tabs: {
        phenotype: "Phenotype Prediction",
        str: "STR Locus Analysis",
        zkp: "ZK Proof Auditor",
      },
      phenotypeTab: {
        eyeColors: { blue: "Blue", hazel: "Hazel", brown: "Brown" },
        skinTypes: { vPale: "Very Pale", fair: "Fair", medium: "Medium", olive: "Olive", dBrown: "Dark Brown", dBlack: "Deep Black" },
        hairTypes: { straight: "Straight", wavy: "Wavy", curly: "Curly" },
        irisTitle: "Ocular Iris Pigmentation (HERC2 / OCA2)",
        irisSub: "IrisPlex v2",
        targetGenotype: "Target Genotype",
        secondaryMarker: "Secondary Marker",
        posteriorProb: "Posterior Probability",
        confidence: "Confidence",
        skinTitle: "Fitzpatrick Phototype (SLC24A5 / TYRP1)",
        skinSub: "HIrisPlex-S",
        hairTitle: "Hair Texture & Morphology (EDAR / FGFR2)",
        hairSub: "HairPlex",
        summaryTitle: "BIOMETRIC SUMMARY",
        synced: "100% Synced",
        predictedIris: "PREDICTED IRIS",
        skinPhototypeLabel: "Skin phototype",
        hairScore: "HAIR TEXTURE SCORE",
        accuracy: "Accuracy",
      },
      strTab: {
        electropherogramTitle: "Fluorescent Electropherogram",
        codisPanel: "Expanded 24-Locus Forensic Panel",
        alleleLabel: "Allele",
        rfuLabel: "RFU",
        alleleCall: "Allele Call",
        popFreq: "Population Frequency",
        locusLr: "Locus Likelihood Ratio",
      },
      zkpTab: {
        circuitId: "Circuit Identifier",
        provingScheme: "Proving Scheme",
        privateWitness: "Private Witness",
        publicSignal: "Public Verification Signal",
        executeBtn: "Execute ZK Circuit Prover",
        computing: "Computing R1CS Witness Constraints...",
        latency: "Groth16 Prover Latency: <12ms",
        proofSuccess: "ZK Match Proof Generated",
        provenMsg: "The match condition was proven cryptographically without revealing any raw STR profile data.",
        resetBtn: "Reset Prover",
        consoleTitle: "ZKP Execution Console",
        initInfo: "[INFO] Initializing Circom constraints...",
        readingInfo: "[INFO] Reading setup parameter file: powersOfTau28_ezkl.ptau",
        witnessInfo: "[INFO] Witness signals generated (24 loci constraints satisfied)",
        successCreated: "[SUCCESS] Proof proof.json created cleanly.",
        testnetReady: "Polygon Testnet Ready",
        zeroLeakage: "Zero Data Leakage Guaranteed",
        publicHash: "Public Proof Hash",
      },
    },
    subsystems: {
      badge: "Subsystem Registry",
      title: "35 Specialized Forensic Subsystems",
      subtitle: "Organized into 7 core architectural pillars covering every domain of forensic biology, probabilistic genotyping, epigenetics, physical traces, geo-forensic spatial intelligence, LIMS Merkle custody, and court visualizers.",
      searchPlaceholder: "Filter subsystems...",
      activeCount: "5 Active Biocomputational Subsystems",
      operationalStatus: "Operational Status",
      totalSubsystemsLabel: "Total Subsystems",
      totalSubsystemsValue: "35 / 35 Active",
      archLayersLabel: "Architectural Layers",
      archLayersValue: "7-Layer DAG",
      pytestInvariantsLabel: "Automated Test Suite",
      pytestInvariantsValue: "829 / 829 Verified",
      standardComplianceLabel: "Standard Compliance",
      standardComplianceValue: "ISO/IEC 17025",
      pillars: [
        {
          name: "Probabilistic Genotyping & Population Genetics",
          shortName: "Genotyping",
          badge: "CORE ENGINE",
          subsystems: [
            { id: "01", name: "Autosomal STR & Kinship Engine", badge: "STR-24", metrics: "24 Extended Loci • NIST 1036 • Balding-Nichols θ", desc: "Calculates Likelihood Ratios across expanded 24-locus multiplex (CODIS 20 + SE33, Penta D/E, Amelogenin) calibrated with NIST 1036 allele frequency matrices and SMM mutation models." },
            { id: "02", name: "MCMC Probabilistic Mixture Deconvoluter", badge: "MCMC-MH", metrics: "EuroForMix & STRmix • 3-Chain MCMC • 95% HPD", desc: "Continuous Gamma/Log-Normal mixture deconvolution for 2-to-4 contributors with Gelman-Rubin R̂ < 1.05 and ESS > 1000 convergence diagnostics." },
            { id: "03", name: "Dirichlet Fst Population Genetics", badge: "POPGEN-FST", metrics: "Balding-Nichols • Fst Correction • Dirichlet Smooth", desc: "Implements NRC II Recommendations 4.1 & 4.2 with subpopulation coancestry (Fst = 0.01 / 0.03) Dirichlet smoothing." },
            { id: "04", name: "Touch DNA & Low-Template LTDNA", badge: "LTDNA-MOD", metrics: "Dropout p_d • Drop-in p_i • Imbalance (<100 pg)", desc: "Models stochastic allele dropout (p_d) and Poisson drop-in (p_i) for low-template touch DNA recovered from porous and non-porous evidence." },
            { id: "05", name: "Tippett Calibration & Validation Lab", badge: "TIPPETT", metrics: "H_p vs H_d • ROC-AUC • Cllr Metric", desc: "Generates empirical Tippett calibration curves plotting log10(LR) probability distributions under true contributor (H_p) vs non-contributor (H_d) hypotheses." }
          ]
        },
        {
          name: "Lineage Forensics & Kinship Inference",
          shortName: "Lineage DNA",
          badge: "HAPLOTYPE",
          subsystems: [
            { id: "06", name: "Y-STR Haplotype Forensics", badge: "Y-STR", metrics: "Y-FILER Plus 27 • Clopper-Pearson 95% • Y-HRD", desc: "Computes Clopper-Pearson 95% binomial confidence intervals for Y-chromosome STR haplotypes (Y-FILER Plus 27 loci) with Y-HRD database matching." },
            { id: "07", name: "X-STR Linkage & Kinship Index", badge: "X-STR", metrics: "Argus X-12 • LG1-LG4 Linkage • KI_X Kinship", desc: "Evaluates Argus X-12 4 linkage clusters with Kosambi map distance corrections and female kinship likelihood ratios (KI_X)." },
            { id: "08", name: "mtDNA Control Region rCRS/RSRS", badge: "mtDNA-rCRS", metrics: "EMPOP rCRS/RSRS • HV1-HV3 • Phylotree", desc: "Aligns hypervariable regions against revised Cambridge Reference Sequence (rCRS) and RSRS for maternal lineage assignment." },
            { id: "09", name: "Interpol DVI Mass Disaster Engine", badge: "DVI-PED", metrics: "Interpol Joint LR • N x M Matrix • 4 Tiers", desc: "Multi-omic joint likelihood ratio evaluation (LR_Joint = LR_Auto · LR_Y · LR_mt · LR_SNP) and N x M cross-reconciliation matrix." },
            { id: "10", name: "Ancient DNA & Degraded Forensic SNP", badge: "aDNA-SNP", metrics: "MapDamage Kinetics • C->T • Fragmentation", desc: "Models Briggs deamination damage kinetics (C->T transitions) and exponential fragmentation length distributions for degraded skeletal remains." }
          ]
        },
        {
          name: "Phenotyping & Biogeographic Ancestry",
          shortName: "Phenotyping",
          badge: "HIRISPLEX-S",
          subsystems: [
            { id: "11", name: "HIrisPlex-S 41-SNP Pigmentation", badge: "HIRISPLEX", metrics: "Iris 6 • Hair 22 • Fitzpatrick Skin 36", desc: "Multinomial logistic regression neural model predicting eye, hair, and 5-class Fitzpatrick skin phototypes with Softmax sum-to-one invariant." },
            { id: "12", name: "55-SNP AIM Ancestry & Live GIS", badge: "BGA-55", metrics: "55 AIMs • 7 Populations • 3D Spherical GIS", desc: "Calculates posterior probabilities for 7 continental biogeographic populations and projects 3D Cartesian spherical GIS coordinates." },
            { id: "13", name: "Craniofacial 3D Morphology", badge: "CRANIO-3D", metrics: "Claes 3D Landmarks • Midline Symmetry • I_F", desc: "Reconstructs 3D craniofacial morphology landmarks, bizygomatic breadth, and clinical Facial Index (I_F) with strict vertical Z-monotonicity." },
            { id: "14", name: "Hair Texture & Balding Risk PRS", badge: "HAIR-TEX", metrics: "EDAR Fiber Area • Curl Index • Hamilton-Norwood", desc: "Predicts hair cross-sectional fiber area, curl density index (straight/wavy/curly/kinky), and polygenic androgenetic alopecia risk." },
            { id: "15", name: "Ephelides, MC1R Epistasis & UV", badge: "MC1R-UV", metrics: "MC1R R/r Weights • Freckling Score • MED mJ/cm²", desc: "Evaluates MC1R loss-of-function variants with epistatic ASIP/BNC2 interactions to score freckling density and Minimal Erythema Dose (MED)." }
          ]
        },
        {
          name: "Epigenetics & Environmental Aging",
          shortName: "Epigenetics",
          badge: "EPIGENETICS",
          subsystems: [
            { id: "16", name: "Horvath / VISAGE Epigenetic Clock", badge: "HORVATH", metrics: "Piecewise Elastic Net • 5-CpG • Multi-Tissue", desc: "Quantifies DNA methylation levels at key CpG loci using Horvath piecewise linear/exponential link function to estimate chronological age." },
            { id: "17", name: "Body Fluid & Tissue Origin tDMR", badge: "tDMR-FLUID", metrics: "6-Tissue QDA/NNLS • Semen • Blood • Saliva", desc: "Deconvolutes tissue-specific differentially methylated regions (tDMRs) to identify 6 forensic body fluids with Sum-to-One invariant." },
            { id: "18", name: "Lifestyle Epigenomics & AHRR", badge: "AHRR-LIFE", metrics: "AHRR Smoking • Pack-Years • Epigenetic BMI", desc: "Analyzes AHRR hypomethylation to quantify tobacco smoke pack-years, alcohol exposure indices, and epigenetic BMI." },
            { id: "19", name: "Telomere Length Decay & PMI", badge: "TELO-PMI", metrics: "qPCR T/S Decay • ADH Thermal Summation", desc: "Measures relative telomere-to-single-copy-gene (T/S) length ratio and calculates inverse Post-Mortem Interval (PMI) under ADH." },
            { id: "20", name: "Bisulfite QC & Probe Calibration Lab", badge: "BISULFITE-QC", metrics: "Conversion ≥99.0% • Logit M-Value • BMIQ", desc: "Validates bisulfite conversion efficiency (C_conv ≥ 99.0%), computes bijective Beta ↔ M logit transforms, and applies BMIQ normalization." }
          ]
        },
        {
          name: "Physical Evidence, Pathology & Trace Forensics",
          shortName: "Pathology",
          badge: "PHYSICAL",
          subsystems: [
            { id: "21", name: "Bloodstain Pattern Analysis (BPA 3D)", badge: "BPA-3D", metrics: "Least-Squares Point of Origin • Drag • Angle", desc: "Calculates impact angle, stain directionality vectors, and closed-form least-squares 3D flight convergence with 95% confidence ellipsoids." },
            { id: "22", name: "SEM-EDX GSR & CMC 3D Ballistics", badge: "BALLISTICS-GSR", metrics: "ASTM E1588 Pb-Ba-Sb • 3D CMC Striations", desc: "Automated characteristic gunshot residue triad scoring and 3D Congruent Matching Cells striation surface topography matching." },
            { id: "23", name: "Forensic Entomology & Minimum PMI", badge: "ENTO-PMI", metrics: "Accumulated Degree Days • T_base • Species", desc: "Calculates minimum PMI based on Accumulated Degree Days (ADD/ADH) thermal constants (K) and lower developmental thresholds (T_base)." },
            { id: "24", name: "Multispectral Imaging (MSI) & ATR-FTIR", badge: "SPEC-MSI", metrics: "4-Band MSI • ATR-FTIR • HQI ≥ 85.0%", desc: "Trace evidence and synthetic fiber identification using 4-band multispectral reflectance and Hit Quality Index (HQI ≥ 85.0%) spectral matching." },
            { id: "25", name: "Post-Mortem Toxicokinetics & PMR", badge: "TOX-PMR", metrics: "Central/Peripheral C/P • Widmark • Opioids", desc: "Quantifies Central-to-Peripheral (C/P) post-mortem drug redistribution ratios and zero/first-order metabolic clearance models." }
          ]
        },
        {
          name: "LIMS, ISO 17025 QA/QC & Cryptographic Governance",
          shortName: "ISO & LIMS",
          badge: "GOVERNANCE",
          subsystems: [
            { id: "26", name: "Chain of Custody Merkle Tree Ledger", badge: "LIMS-MERKLE", metrics: "SHA-256 / Blake3 • O(log₂ N) Proofs • Append-Only", desc: "Binary append-only cryptographic Merkle tree recording evidence handling transitions with O(log₂ N) courtroom inclusion proofs." },
            { id: "27", name: "Zero-Knowledge Proof Blind Forensic Auditor", badge: "ZKP-GROTH16", metrics: "Circom Groth16 • BN254 Pairings • Zero Leakage", desc: "Privacy-preserving matching engine proving suspect inclusion (LR ≥ M_thresh) over BN254 bilinear pairing without exposing raw STR/SNP sequences." },
            { id: "28", name: "ISO/IEC 17025:2017 Metrological Uncertainty Budget", badge: "ISO-17025-GUM", metrics: "GUM Uncertainty • U_95% = 2.00 · u_c • z-Score", desc: "Combined and expanded measurement uncertainty (U_95% = 2.00 · u_c) for qPCR DNA yields and laboratory z-score proficiency validation." },
            { id: "29", name: "Dynamic ENFSI Evaluative Reporting Scaler", badge: "ENFSI-2017", metrics: "7-Tier Verbal Scale • Daubert FRE 702 • Frye Audit", desc: "Translates continuous Likelihood Ratios into standardized 7-tier ENFSI verbal scale statements with Daubert FRE 702 and Frye statutory admissibility audits." },
            { id: "30", name: "3D Spatial Evidence Presenter & Juror Visualizer", badge: "SPATIAL-3D", metrics: "SE(3) Registration • 95% Ellipsoids • Multi-Sensor", desc: "Special Euclidean SE(3) multi-sensor spatial registration (LiDAR, BPA, Ballistics, DNA) and 95% volumetric probability ellipsoid rendering (χ²₃ = 7.815)." }
          ]
        },
        {
          name: "Geo-Forensic Intelligence & Spatial Biogeochemistry",
          shortName: "Geo-Forensics",
          badge: "GEOINT",
          subsystems: [
            { id: "31", name: "Multi-Isotope Isoscape Provenance", badge: "ISOSCAPES", metrics: "Harmon Craig GMWL • Terzer-Wassenaar • Bataille Sr", desc: "Resolves geographic origin centroids and 95% spatial confidence radii via continuous multivariate Gaussian isoscape matching (H, O, Sr) with bioapatite and keratin calibration." },
            { id: "32", name: "Soil Pedology & Geochemical CoDa", badge: "SOIL-CODA", metrics: "QXRD Rietveld • ZTR Index • CLR • ASTM E3272-21", desc: "Compares questioned and known control soils using Centered Log-Ratio (CLR) compositional transformations, MCD Robust Mahalanobis Distance, and Hotelling F-tests." },
            { id: "33", name: "Forensic Palynology & Environmental eDNA", badge: "PALYNOLOGY", metrics: "RPF Normalizer • 6-Biome Classifier • 16S/ITS eDNA", desc: "Quantifies Relative Pollen Frequencies (RPF), computes multivariate Bray-Curtis dissimilarities, classifies terrestrial biomes, and predicts origin coordinates via microbial eDNA spatial regression." },
            { id: "34", name: "Rossmo Bayesian Geographic Profiling", badge: "ROSSMO-GEO", metrics: "Targeted Hunting B=1.5km • SEI ≥ 90% • Canter Circle", desc: "Evaluates Rossmo's targeted hunting formula over serial crime locations to determine peak anchor coordinates, prioritize search areas (S_5%), and classify offender mobility (Marauder vs Commuter)." },
            { id: "35", name: "Multi-Criteria Bayesian GIS Evidence Fusion", badge: "GIS-FUSION", metrics: "Joint Raster Multiplier • 2D Adaptive KDE • ISO 17025", desc: "Fuses independent isoscape, soil, palynological, and behavioral layers into a unified spatial posterior probability surface with 2D adaptive KDE smoothing and ENFSI evaluative reporting." }
          ]
        }
      ],
    },

    architecture: {
      badge: "System Architecture",
      title: "Directed Acyclic Graph (DAG) Evidence Pipeline",
      subtitle: "How raw FASTQ/FSA electropherogram files transition into ISO 17025 court-admissible forensic evidence packages.",
      layers: [
        {
          layer: "Layer 1: Multi-Omic Evidence Ingestion",
          badge: "INGESTION",
          nodes: ["Autosomal STR", "Forensic SNP", "mtDNA rCRS", "Y-STR", "ABO/Rh Serology", "mRNA Body Fluid", "16S Microbiology", "Stable Isotopes", "Soil QXRD"]
        },
        {
          layer: "Layer 2: Biocomputational Inference Engine",
          badge: "INFERENCE",
          nodes: ["MCMC Mixture Deconvolution", "Kinship Index", "HIrisPlex-S Phenotype", "Dirichlet Fst Population", "Horvath Clock", "BPA 3D"]
        },
        {
          layer: "Layer 3: Geo-Forensic & Spatial Intelligence",
          badge: "GEOINT",
          nodes: ["Multi-Isotope Isoscapes", "Soil CoDa CLR", "Palynology 6-Biome", "Rossmo Targeted Hunting", "2D Adaptive KDE Fusion"]
        },
        {
          layer: "Layer 4: Directed Case Graph & Ledger",
          badge: "LEDGER",
          nodes: ["Case Graph Engine", "LIMS Accessioning", "HMAC Chain of Custody", "Merkle Tree Inclusion Proofs"]
        },
        {
          layer: "Layer 5: ISO 17025 QA/QC Gatekeeper",
          badge: "QA/QC",
          nodes: ["ISO 17025 Inspection", "Heterozygote Balance Hb", "Stochastic ST", "GUM Uncertainty Budget", "Control Verification"]
        },
        {
          layer: "Layer 6: Human Analyst Governance",
          badge: "GOVERNANCE",
          nodes: ["Dual Sign-Off Review", "Override Rationale Logger", "Prosecutor Fallacy Shield", "Circom ZKP Privacy Auditor"]
        },
        {
          layer: "Layer 7: Court-Admissible Reporting",
          badge: "REPORTING",
          nodes: ["ISO 17025 Certificate Compiler", "PDF Exporter", "Expert Witness Court Mode", "3D Juror Spatial Visualizer"]
        }
      ]
    },
    security: {
      badge: "Enterprise Security & Admissibility",
      title: "Cryptographic Evidence Custody & ISO 17025 Compliance",
      subtitle: "Tamper-evident audit logging, zero-knowledge evidence verification, and strict chain of custody.",
      matrixTitle: "Technical Platform Specifications & Standards Matrix",
      passedBadge: "829 TESTS VERIFIED",
      pillars: [
        {
          title: "Zero-Knowledge Privacy Auditor",
          desc: "Raw STR allele profiles remain confined to isolated execution enclaves. Circom/SnarkJS zkSNARK circuits generate Groth16 cryptographic proofs confirming DNA match criteria without transmitting raw genomic profile data."
        },
        {
          title: "Immutable Chain of Custody",
          desc: "Every LIMS accessioning event, workflow SOP step, QA/QC verdict, analyst sign-off, and ISO report is SHA-256 hashed and anchored to a Polygon cryptographic ledger with HMAC audit verification."
        },
        {
          title: "Data Isolation Architecture",
          desc: "Forensic evidence samples are processed in isolated memory enclaves with strict zero-persistence private profile bounds. Post-analysis, only anonymized aggregate statistics and ZK proof artifacts are retained."
        },
        {
          title: "Federated Peer Computation",
          desc: "Cross-jurisdiction forensic queries run across a decentralized peer registry. No single node accesses complete genetic databases, and inter-node matching tasks are cryptographically verified."
        }
      ],
      specs: [
        { label: "Autosomal STR Multiplex", value: "Expanded 24-Locus Forensic Panel (20 FBI CODIS Core + ESS SE33, Penta D, Penta E, Amelogenin)" },
        { label: "Lineage Forensics", value: "Y-STR 27 Loci (Clopper-Pearson 95% CI), X-STR 4 Clusters (Argus X-12), mtDNA rCRS/RSRS" },
        { label: "Probabilistic Mixture MCMC", value: "EuroForMix Gamma & STRmix Log-Normal 2-4 Contributors (Dropout p_d & Drop-in p_i)" },
        { label: "Phenotype & Epigenetics", value: "HIrisPlex-S 41-SNP (Eye/Hair/Skin), 55-SNP AIM GIS & Horvath 5-CpG Epigenetic Age Clock" },
        { label: "Physical & Trace Evidence", value: "3D BPA Least-Squares Origin, SEM-EDX GSR (Pb-Ba-Sb), CMC Ballistics & Entomology ADD/ADH" },
        { label: "Geo-Forensic Intelligence", value: "Multi-Isotope Isoscapes (H/O/Sr), Soil QXRD CoDa, Palynology eDNA & Rossmo Profiling" },
        { label: "Population Models", value: "NRC II Recommendations 4.1 & 4.2 Balding-Nichols Dirichlet Subpopulation Fst Correction" },
        { label: "Instrument Ingestion", value: "Automated Gateway for CE GeneMapper CSV, qPCR Quantifiler Trio Cq/DI & NGS MiSeq VCF" },
        { label: "ISO 17025 Compliance", value: "8-Section Formal Certificate Compiler, GUM Uncertainty (k=2.00) & 7-Tier ENFSI Scaler" },
        { label: "Automated Test Suite", value: "829 / 829 Automated Tests Passed (100% Invariant Validation)" },
        { label: "Frontend Stack", value: "Next.js 16 Turbopack App Router, React 19, Tailwind CSS, Framer Motion" },
        { label: "Backend Stack", value: "FastAPI (Python 3.12), NumPy, SciPy, Scikit-learn, MCMC Metropolis-Hastings Engine" },
        { label: "Privacy & Ledger", value: "Circom zk-SNARK Groth16 (BN254 Pairings) + Binary Merkle Tree O(log₂ N) Custody Ledger" }
      ]
    },
    faq: {
      badge: "Frequently Asked Questions",
      title: "Forensic Intelligence OS FAQ",
      subtitle: "Common inquiries regarding system capabilities, court admissibility, LIMS integration, and deployment.",
      questions: {
        q1: "How does FORENZA handle low-template complex DNA mixtures?",
        a1: "FORENZA employs Metropolis-Hastings Markov Chain Monte Carlo (MCMC) probabilistic genotyping algorithms that model peak height variation, stutter ratios, allele drop-out, and drop-in to calculate true Likelihood Ratios (LR).",
        q2: "Is the platform ISO/IEC 17025:2017 compliant?",
        a2: "Yes. All biocomputational pipelines generate standardized, court-admissible audit reports detailing analytical thresholds, validation metrics, and complete chain of custody ledger entries.",
        q3: "Can FORENZA integrate with existing laboratory LIMS software?",
        a3: "FORENZA features a bidirectional RESTful API and HL7/FHIR interface designed to seamlessly ingest electropherogram (FSA/HID) and FASTQ files directly from genetic analyzers and existing LIMS systems.",
        q4: "What phenotyping and ancestry models are supported?",
        a4: "FORENZA integrates HIrisPlex-S for eye, hair, and skin color prediction, alongside 55-SNP Biogeographic Ancestry (BGA) models for population origin estimation.",
        q5: "How is data privacy and zero-knowledge evidence verification handled?",
        a5: "The platform incorporates Circom-based Zero-Knowledge Proofs (ZKP), allowing investigators to verify profile matches against databases without revealing raw sensitive genomic sequence data.",
      },
    },
    footer: {
      rights: "FORENZA Forensic Systems. All rights reserved.",
      tagline: "Enterprise Biocomputational Forensic Intelligence & Evidence Operating System.",
      brandSubtitle: "FORENSIC EVIDENCE OPERATING SYSTEM",
      status: "35 Active Subsystems",
      columns: {
        col1Title: "Platform Subsystems",
        col1Links: ["35 Subsystems Matrix", "Evidence OS DAG", "Multi-Omic Bio-Simulator", "ISO 17025 Court Mode"],
        col2Title: "Core Capabilities",
        col2Links: ["MCMC Probabilistic Genotyping", "HIrisPlex-S Phenotyping", "Horvath Epigenetic Clock", "Geo-Forensic Intelligence", "LIMS & Instrument Gateway"],
        col3Title: "Admissibility & Standards",
        col3Links: ["ISO/IEC 17025:2017 Format", "SWGDAM & ENFSI Rules", "Circom ZKP Privacy Auditor", "HMAC Chain of Custody"],
      },
      disclaimer: {
        badge: "Academic & Demonstration Disclaimer",
        title: "Research & Simulation Environment Notice",
        text: "FORENZA is an academic research, algorithmic verification, and simulation demonstration platform. Analytical results, likelihood ratios (LR), phenotype predictions, and simulated court certificates generated herein are intended solely for computational validation, educational demonstration, and research benchmarking. This software is not a replacement for an accredited forensic DNA laboratory and must not be used as the sole basis for live judicial prosecution, criminal sentencing, or active casework without accredited laboratory validation.",
        isoNote: "ISO/IEC 17025 alignment denotes compliance with SWGDAM/ENFSI biostatistical reporting format guidelines and does not constitute formal laboratory accreditation."
      }
    },
  },
  tr: {
    header: {
      bioSimulator: "Bio-Simülatör",
      subsystems: "35 Alt Sistem",
      architecture: "DAG Mimarisi",
      security: "Güvenlik & ISO",
      launchDemo: "Demoyu Başlat",
    },
    hero: {
      badge: "Çoklu-Omik Adli Delil İşletim Sistemi",
      titleMain: "Entegre Biyobilişimsel",
      titleHighlight: "Adli Delil İşletim Sistemi",
      subtitle: "Otozomal ve soy STR analizleri, MCMC olasılıksal genotipleme, HIrisPlex-S fenotip tahmini, Horvath epigenetik yaş saati, fiziksel balistik ve BPA, Jeo-Adli CBS istihbaratı, LIMS veri zinciri ve ISO/IEC 17025 adli rapor standartlarını tek bir işlem hattında birleştiren çoklu-omik adli biyoloji platformu.",
      launchDemo: "Demoyu Başlat",
      exploreSubsystems: "35 Modülü İncele",
      subsystemsStat: "Adli Alt Sistem",
      invariantsStat: "Doğrulanmış İnvaryant",
      courtStat: "Mahkeme Uyumlu",
      privacyStat: "Gizlilik Denetçisi",
    },
    solutions: {
      badge: "Kullanım Alanları",
      title: "Yüksek Güvenilirlik Gerektiren Sahalar İçin Tasarlandı",
      subtitle: "FORENZA; adli genetik laboratuvarları, olay yeri inceleme birimleri, afet kurbanlarını kimliklendirme (DVI) ve genomik araştırma merkezlerinin operasyonel ihtiyaçlarını karşılar.",
      domainInspection: "ALAN ANALİZİ VE VERİ ÇIKTISI",
      activeStandard: "Aktif Standart",
      primaryMetric: "BİRİNCİL ANALİTİK PARAMETRE",
      sessionTarget: "Oturum Referans Kodu",
      verificationStatus: "Doğrulama Durumu",
      auditPassed: "NRC II Denetimini Geçti",
      items: [
        {
          id: "law-enforcement",
          title: "Kolluk Kuvvetleri ve Faili Meçhul Olaylar",
          subtitle: "Soybağı Araştırması ve Bozunmuş DNA Örneklerinde LR Analizi",
          description: "Olay yerinden elde edilen eksik veya biyolojik olarak bozunmuş STR profillerini referans örneklerle karşılaştırarak olabilirlik oranı (Likelihood Ratio - LR) hesaplar. Doğrudan profil eşleşmesi olmadığında, soybağı motoru ailevi akrabalık bağlarını belirleyerek faili meçhul dosyalar için akraba bazlı tarama (familial searching) imkanı sunar.",
          bulletPoints: [
            "Eksik lokus içeren profillerde istatistiksel LR hesaplaması",
            "Çok kuşaklı soyağaçlarında ailevi DNA taraması (Familial Searching)",
            "Soruşturma coğrafyasına yönelik atasal soy haritalandırması",
            "Mahkeme delil standartlarına uygun adli raporlama",
          ],
          sampleMetric: "1.42e8 Olabilirlik Oranı (LR)",
          sampleCode: "CASE_2026_COLD_09 — NDIS CODIS Çekirdek 20 Lokus Veritabanı Eşleşmesi",
          label: "Kolluk Kuvvetleri",
        },
        {
          id: "dvi",
          title: "Afet Kurbanlarının Kimliklendirilmesi (DVI)",
          subtitle: "Kitlesel Kayıplarda Hızlı Akrabalık Tespiti ve Profil Eşleştirme",
          description: "Toplu ölümlerde ve afet durumlarında, kimliği belirsiz naaşları aile referans örnekleriyle akrabalık indeksleri üzerinden eşleştirir. Interpol DVI Bölüm 4 adli tıp standartlarında yüksek hacimli veri işleme olanağı sunar.",
          bulletPoints: [
            "Eşzamanlı çoklu numune analiz boru hattı",
            "Ebeveyn-çocuk ve kardeş akrabalık indeksi (KI) hesabı",
            "Numune kalitesi ve DNA degradasyon değerlendirmesi",
            "Interpol DVI Bölüm 4 standartlarında adli rapor çıktısı",
          ],
          sampleMetric: "%99.999 Eşleşme Olasılığı",
          sampleCode: "DVI_BATCH_402 — Interpol Bölüm 4 Standardı",
          label: "DVI Operasyonları",
        },
        {
          id: "border-security",
          title: "Sınır Güvenliği ve Akrabalık Doğrulaması",
          subtitle: "NRC II Çerçevesinde İstatistiksel Akrabalık Analizi",
          description: "Sınır geçişleri ve iltica başvuru merkezlerinde beyan edilen biyolojik akrabalık bağlarını istatistiksel yöntemlerle doğrular. NRC II ilkeleri doğrultusunda hesaplanan olabilirlik oranları tarafsız adli veri sunar.",
          bulletPoints: [
            "Beyan edilen akrabalıklar için NRC II uyumlu LR analizi",
            "Genetik verileri riske atmayan Sıfır Bilgi İspatı (ZKP)",
            "Belge doğrulaması için atasal soy çapraz kontrolü",
            "Dağıtık bilişim mimarisiyle gerçek zamanlı analiz",
          ],
          sampleMetric: "Sıfır Veri Açığı (ZKP)",
          sampleCode: "BORDER_CHECK_882 — Groth16 Doğrulandı",
          label: "Sınır Güvenliği",
        },
        {
          id: "research",
          title: "Akademik ve Klinik Genetik Araştırmaları",
          subtitle: "Popülasyon Yapısı, Dirichlet Fst Düzeltmesi ve GTEx eQTL Entegrasyonu",
          description: "Araştırma enstitüleri için tekrarlanabilir olabilirlik oranı hesaplamaları, dışa aktarılabilir alel frekansı veri tabanları ve 54 doku tipi için GTEx eQTL referansları sağlayan doğrulanmış biyobilişim altyapısı.",
          bulletPoints: [
            "Dışa aktarılabilir alel frekansı veri tabanları ve LR sonuçları",
            "54 doku tipi için GTEx eQTL veri entegrasyonu",
            "Tekrarlanabilir ve denetlenebilir biyobilişim boru hattı",
            "Popülasyon yapısı analizi ve Fst (theta) düzeltmesi",
          ],
          sampleMetric: "54 Doku eQTL Haritalandı",
          sampleCode: "GENOMICS_STUDY_V2 — Balding-Nichols theta=0.03",
          label: "Araştırma Laboratuvarları",
        },
      ],
    },
    bioSimulator: {
      badge: "Etkileşimli Biyobilişim Simülatörü",
      title: "Gerçek Zamanlı Adli Analiz Simülatörü",
      subtitle: "Karmaşık DNA karışımı dekonvolüsyonunu, akrabalık olabilirlik oranlarını ve HIrisPlex-S fenotip tahminlerini canlı olarak deneyimleyin.",
      tabs: {
        phenotype: "Fenotipik Özellik Tahmini",
        str: "STR Lokus ve Karışım Analizi",
        zkp: "Kriptografik ZKP Denetimi",
      },
      phenotypeTab: {
        eyeColors: { blue: "Mavi", hazel: "Ela", brown: "Kahverengi" },
        skinTypes: { vPale: "Çok Açık Ten", fair: "Açık Ten", medium: "Buğday Ten", olive: "Kumral / Buğday", dBrown: "Koyu Esmer", dBlack: "Çok Koyu Ten" },
        hairTypes: { straight: "Düz", wavy: "Dalgalı", curly: "Kıvırcık" },
        irisTitle: "İris Pigmentasyon Tespiti (HERC2 / OCA2)",
        irisSub: "IrisPlex v2",
        targetGenotype: "Hedef Genotip",
        secondaryMarker: "İkincil Markör",
        posteriorProb: "Sonralı Olasılık (Posterior Probability)",
        confidence: "Güven Seviyesi",
        skinTitle: "Fitzpatrick Ten Fototipi (SLC24A5 / TYRP1)",
        skinSub: "HIrisPlex-S",
        hairTitle: "Saç Yapısı ve Morfolojisi (EDAR / FGFR2)",
        hairSub: "HairPlex",
        summaryTitle: "BİYOMETRİK ÖZET",
        synced: "%100 Senkronize",
        predictedIris: "TAHMİN EDİLEN İRİS",
        skinPhototypeLabel: "Ten fototipi",
        hairScore: "SAÇ YAPISI PUANI",
        accuracy: "Doğruluk Oranı",
      },
      strTab: {
        electropherogramTitle: "Flüoresan Elektroferogram",
        codisPanel: "Genişletilmiş 24-Lokus Adli Panel",
        alleleLabel: "Alel",
        rfuLabel: "RFU",
        alleleCall: "Alel Tespiti",
        popFreq: "Popülasyon Frekansı",
        locusLr: "Lokus Olabilirlik Oranı (LR)",
      },
      zkpTab: {
        circuitId: "Devre Kimliği",
        provingScheme: "İspat Şeması",
        privateWitness: "Gizli Girdi (Witness)",
        publicSignal: "Açık Sinyal",
        executeBtn: "ZK İspat Motorunu Çalıştır",
        computing: "R1CS Sınırları Hesaplanıyor...",
        latency: "Groth16 Gecikmesi: <12ms",
        proofSuccess: "ZK Eşleşme İspatı Üretildi",
        provenMsg: "Eşleşme koşulu ham STR verisi açık edilmeden kriptografik olarak doğrulandı.",
        resetBtn: "Sıfırla",
        consoleTitle: "ZKP Konsolu",
        initInfo: "[BİLGİ] Circom sınırları başlatılıyor...",
        readingInfo: "[BİLGİ] Kurulum parametreleri okunuyor: powersOfTau28_ezkl.ptau",
        witnessInfo: "[BİLGİ] Girdi sinyalleri üretildi (24 lokus doğrulandı)",
        successCreated: "[BAŞARI] proof.json ispat dosyası üretildi.",
        testnetReady: "Polygon Testnet Hazır",
        zeroLeakage: "Sıfır Veri Sızıntısı Garantili",
        publicHash: "Genel İspat Özeti",
      },
    },
    subsystems: {
      badge: "Modüler Analiz Dizini",
      title: "35 Adli Biyobilgisayar ve Kanıt Modülü",
      subtitle: "Adli biyoloji, olasılıksal genotipleme, epigenetik, fiziksel izler, jeo-adli CBS istihbaratı, LIMS Merkle delil zinciri ve jüri görselleştiricilerini kapsayan 7 temel mimari sütunda sunulmaktadır.",
      searchPlaceholder: "Modülleri filtreleyin...",
      activeCount: "5 Aktif Adli Analiz Modülü",
      operationalStatus: "Operasyonel Durum",
      totalSubsystemsLabel: "Toplam Alt Sistem",
      totalSubsystemsValue: "35 / 35 Aktif",
      archLayersLabel: "Mimari Katmanlar",
      archLayersValue: "7 Katmanlı DAG",
      pytestInvariantsLabel: "Doğrulanmış Test Paketi",
      pytestInvariantsValue: "829 / 829 Doğrulandı",
      standardComplianceLabel: "Standart Uyumluluk",
      standardComplianceValue: "ISO/IEC 17025",
      pillars: [
        {
          name: "Olasılıksal Genotipleme ve Popülasyon Genetiği",
          shortName: "Olasılıksal",
          badge: "TEMEL MOTOR",
          subsystems: [
            { id: "01", name: "Otozomal STR ve Soybağı Analiz Motoru", badge: "STR-24", metrics: "24 Genişletilmiş Lokus • NIST 1036 • Balding-Nichols θ", desc: "Genişletilmiş 24 lokuslu adli panelde (CODIS 20 + SE33, Penta D/E, Amelogenin) NIST 1036 frekans matrisleri ve SMM mutasyon modeliyle olabilirlik oranı (LR) hesaplar." },
            { id: "02", name: "MCMC Olasılıksal Karışım Dekonvolüsyonu", badge: "MCMC-MH", metrics: "EuroForMix & STRmix • 3 Zincirli MCMC • %95 HPD", desc: "2 ila 4 kişilik karmaşık DNA karışımları için Gelman-Rubin R̂ < 1.05 ve ESS > 1000 yakınsama denetimli sürekli Gamma/Log-Normal dekonvolüsyon yürütür." },
            { id: "03", name: "Dirichlet Fst Popülasyon Genetiği", badge: "POPGEN-FST", metrics: "Balding-Nichols • Fst Düzeltmesi • Dirichlet Modeli", desc: "Alt popülasyon akrabalığı (Fst = 0.01 / 0.03) ile NRC II Tavsiye 4.1 ve 4.2 standartlarında Dirichlet yumuşatması uygular." },
            { id: "04", name: "Temas DNA'sı ve LTDNA Analizi", badge: "LTDNA-MOD", metrics: "Alel Kaybolması p_d • Alel Eklenmesi p_i • Dengesizlik (<100 pg)", desc: "Gözenekli ve gözeneksiz delil yüzeylerinden elde edilen düşük şablonlu iz DNA'larda stokastik alel kaybolması (p_d) ve Poisson alel eklenmesini (p_i) modeller." },
            { id: "05", name: "Tippett Kalibrasyon ve Doğrulama Laboratuvarı", badge: "TIPPETT", metrics: "H_p vs H_d • ROC-AUC • Cllr Metriği", desc: "Gerçek katkıda bulunan (H_p) ile katkıda bulunmayan (H_d) hipotezleri için ampirik Tippett kalibrasyon eğrilerini ve Cllr maliyet metriklerini raporlar." }
          ]
        },
        {
          name: "Soy Analizleri ve Akrabalık Çıkarımı",
          shortName: "Soy Analizi",
          badge: "HAPLOTİP",
          subsystems: [
            { id: "06", name: "Y-STR Haplotip Analizi", badge: "Y-STR", metrics: "Y-FILER Plus 27 • Clopper-Pearson %95 • Y-HRD", desc: "Y-kromozomu STR haplotipleri (Y-FILER Plus 27 lokus) için Clopper-Pearson %95 binom güven aralıklarını hesaplar ve Y-HRD veri tabanıyla eşleştirir." },
            { id: "07", name: "X-STR Bağlantılı Markör Analizi", badge: "X-STR", metrics: "Argus X-12 • LG1-LG4 Bağlantısı • KI_X Soybağı", desc: "Argus X-12 4 bağlantı kümesini Kosambi harita mesafesi düzeltmeleriyle değerlendirir ve kadın soybağı olabilirlik oranlarını (KI_X) hesaplar." },
            { id: "08", name: "mtDNA Kontrol Bölgesi rCRS/RSRS", badge: "mtDNA-rCRS", metrics: "EMPOP rCRS/RSRS • HV1-HV3 • Filotree", desc: "Anne soyu tespiti için hiperdeğişken bölgeleri revize edilmiş Cambridge Referans Dizisi (rCRS) ve RSRS ile hizalar." },
            { id: "09", name: "Interpol DVI ve Afet Kurbanı Kimliklendirme", badge: "DVI-PED", metrics: "Interpol Birleşik LR • N x M Matris • 4 Kademe", desc: "Çoklu-omik birleşik olabilirlik oranı (LR_Birleşik = LR_Oto · LR_Y · LR_mt · LR_SNP) ve N x M afet çapraz mutabakat matrisi hesaplar." },
            { id: "10", name: "Antik DNA ve Adli SNP Deaminasyon Motoru", badge: "aDNA-SNP", metrics: "MapDamage Kinetiği • C->T • Fragmantasyon", desc: "Bozunmuş iskelet kalıntıları için Briggs deaminasyon hasar kinetiğini (C->T geçişleri) ve üstel fragmantasyon uzunluk dağılımını modeller." }
          ]
        },
        {
          name: "Fenotipleme ve Atasal Soy Tahmini",
          shortName: "Fenotipleme",
          badge: "HIRISPLEX-S",
          subsystems: [
            { id: "11", name: "HIrisPlex-S 41-SNP Pigmentasyon Analizi", badge: "HIRISPLEX", metrics: "İris 6 • Saç 22 • Fitzpatrick Ten 36", desc: "Göz rengi, saç pigmentasyonu ve 5 sınıflı Fitzpatrick ten fototipini Softmax toplamı bire eşitlik değişmeziyle tahmin eden çok terimli lojistik regresyon modeli." },
            { id: "12", name: "55-SNP AIM Atasal Soy ve Canlı GIS Haritası", badge: "BGA-55", metrics: "55 AIM • 7 Popülasyon • 3D Küresel GIS", desc: "55 atasal bilgi markörü (AIM) kullanarak 7 küresel coğrafi popülasyon için sonralı olasılıkları hesaplar ve 3D Kartezyen küresel GIS koordinatlarına izdüşürür." },
            { id: "13", name: "Kraniyofasiyal 3D Yüz Morfolojisi", badge: "CRANIO-3D", metrics: "Claes 3D Nirengi • Simetri • I_F İndeksi", desc: "Genetik markörlerden kraniyofasiyal yapısal oranları, yüz nirengi noktalarını ve klinik Yüz İndeksini (I_F) dikey Z-monotonluk garantisiyle yeniden üretir." },
            { id: "14", name: "Saç Yapısı ve Kellik Riski PRS", badge: "HAIR-TEX", metrics: "EDAR Lif Alanı • Kıvrım İndeksi • Hamilton-Norwood", desc: "Saç lifi enine kesit alanını, kıvrım yoğunluğu indeksini (düz/dalgalı/kıvırcık) ve poligenik androgenetik alopesi kellik riskini tahmin eder." },
            { id: "15", name: "Çil Yoğunluğu, MC1R Epistazı ve UV Hassasiyeti", badge: "MC1R-UV", metrics: "MC1R R/r Ağırlıkları • Çil Skoru • MED mJ/cm²", desc: "Çil yoğunluğunu ve Minimal Eritem Dozunu (MED) ASIP/BNC2 epistatik etkileşimleriyle birlikte MC1R geni varyant kombinasyonları üzerinden puanlar." }
          ]
        },
        {
          name: "Epigenetik ve Çevresel Yaşlanma",
          shortName: "Epigenetik",
          badge: "EPİGENETİK",
          subsystems: [
            { id: "16", name: "Horvath / VISAGE Çoklu-Doku Yaş Saati", badge: "HORVATH", metrics: "Parçalı Elastik Net • 5-CpG • Çoklu-Doku", desc: "Delil bırakma anındaki kronolojik yaşı tahmin etmek için temel CpG lokuslarındaki metilasyon seviyelerini Horvath parçalı doğrusal/üstel bağlantı fonksiyonuyla ölçer." },
            { id: "17", name: "Dokuya Özgü Vücut Sıvısı tDMR Ayrıştırması", badge: "tDMR-FLUID", metrics: "6-Doku QDA/NNLS • Meni • Kan • Tükürük", desc: "Dokuya özgü farklı metillenen bölgeleri (tDMR) çözümleyerek 6 adli vücut sıvısı türünü Toplam-1 olasılık değişmeziyle tespit eder." },
            { id: "18", name: "Çevresel Yaşam Tarzı Epigenetiği ve AHRR", badge: "AHRR-LIFE", metrics: "AHRR Sigara Skoru • Paket-Yıl • Epigenetik BMI", desc: "Kronik tütün kullanım paket-yılını, alkol maruziyet indeksini ve epigenetik vücut kitle indeksini belirlemek için AHRR geni hipometilasyonunu analiz eder." },
            { id: "19", name: "Telomer Uzunluğu Azalması ve PMI", badge: "TELO-PMI", metrics: "qPCR T/S Azalması • ADH Termal Toplamı", desc: "Göreceli telomer/tek kopya gen (T/S) uzunluk oranını ölçer ve ADH termal toplamı altında ters Ölüm Sonrası Zaman Aralığını (PMI) hesaplar." },
            { id: "20", name: "Bisülfit Kalite Kontrol ve Prob Kalibrasyon Laboratuvarı", badge: "BISULFITE-QC", metrics: "Dönüşüm ≥%99.0 • Logit M-Değeri • BMIQ", desc: "Bisülfit dönüşüm verimliliğini doğrular (C_conv ≥ %99.0), bijektif Beta ↔ M logit dönüşümlerini hesaplar ve BMIQ Tip II prob normalizasyonu uygular." }
          ]
        },
        {
          name: "Fiziksel Kanıtlar, Adli Patoloji ve İz İnceleme",
          shortName: "Patoloji",
          badge: "FİZİKSEL",
          subsystems: [
            { id: "21", name: "Kan Lekesi Deseni Analizi (BPA 3D)", badge: "BPA-3D", metrics: "En Küçük Kareler Çıkış Noktası • Sürtünme • Açı", desc: "Kan lekesi delilleri için darbe açısını, leke yönelim vektörlerini ve %95 güven elipsoitleriyle 3D kapalı form uçuş yakınsama noktasını hesaplar." },
            { id: "22", name: "SEM-EDX GSR ve CMC 3D Balistik Yiv-Set", badge: "BALLISTICS-GSR", metrics: "ASTM E1588 Pb-Ba-Sb • 3D CMC Çizgileri", desc: "Otomatik karakteristik atış artığı üçlüsü (Pb-Ba-Sb) puanlaması ve 3D Uyumlu Eşleşen Hücreler (CMC) yiv-set yüzey topoğrafyası eşleştirmesi." },
            { id: "23", name: "Adli Entomoloji ve Minimum PMI", badge: "ENTO-PMI", metrics: "Birikimli Derece Gün (ADD/ADH) • T_base • Türler", desc: "Birikimli Derece Gün (ADD/ADH) termal sabitleri (K) ve alt gelişim eşikleri (T_base) üzerinden minimum ölüm zamanını (PMI) hesaplar." },
            { id: "24", name: "Çok Bantlı Görüntüleme (MSI) ve ATR-FTIR HQI", badge: "SPEC-MSI", metrics: "4-Bant MSI • ATR-FTIR • HQI ≥ %85.0", desc: "4 bantlı multispektral yansıma ve Vuruş Kalite İndeksi (HQI ≥ %85.0) spektral eşleştirmesi ile kimyasal iz ve sentetik lif tespiti." },
            { id: "25", name: "Otopsi Toksikokinetiği ve PMR Yeniden Dağılımı", badge: "TOX-PMR", metrics: "Santral/Periferik C/P • Widmark • Opioidler", desc: "Santral-Periferik (C/P) ölüm sonrası ilaç yeniden dağılım oranlarını ve sıfır/birinci derece metabolik eliminasyon modellerini niceliklendirir." }
          ]
        },
        {
          name: "LIMS, ISO 17025 Kalite Kontrol ve Kriptografik Yönetişim",
          shortName: "LIMS & ISO",
          badge: "YÖNETİŞİM",
          subsystems: [
            { id: "26", name: "Kriptografik Merkle Delil Zinciri Defteri", badge: "LIMS-MERKLE", metrics: "SHA-256 / Blake3 • O(log₂ N) İspatlar • Yalnızca Ekleme", desc: "Tüm numune ve delil transferlerini O(log₂ N) mahkeme onaylı Merkle dahil etme ispatlarıyla kaydeden kriptografik ikili defter." },
            { id: "27", name: "Sıfır Bilgi İspatlı Kör Adli Denetçi (ZKP)", badge: "ZKP-GROTH16", metrics: "Circom Groth16 • BN254 Eşlemeleri • Sıfır Sızıntı", desc: "Ham STR/SNP sekanslarını ve kişisel verileri ifşa etmeden şüpheli eşleşme eşiğini (LR ≥ M_thresh) BN254 eşlemeleriyle kanıtlar." },
            { id: "28", name: "ISO/IEC 17025:2017 Metrolojik Ölçüm Belirsizliği Bütçesi", badge: "ISO-17025-GUM", metrics: "GUM Belirsizliği • U_%95 = 2.00 · u_c • z-Skoru", desc: "Kantitatif qPCR DNA verimleri için GUM birleşik ve genişletilmiş ölçüm belirsizliği (U_%95 = 2.00 · u_c) ile laboratuvar z-skoru yeterlilik denetimi." },
            { id: "29", name: "Dinamik ENFSI Değerlendirici Raporlama ve Sözlü Ölçek", badge: "ENFSI-2017", metrics: "7 Kademeli Sözlü Ölçek • Daubert FRE 702 • Frye Denetimi", desc: "Sürekli Likelihood Ratio (LR) değerlerini ENFSI (2017) 7 kademeli adli sözlü ifadelere çevirir; Daubert FRE 702 ve Frye kabul edilebilirlik denetimi uygular." },
            { id: "30", name: "3D Uzamsal Olay Yeri Rekonstrüksiyonu ve Jüri Görselleştirici", badge: "SPATIAL-3D", metrics: "SE(3) Dönüşümü • %95 Güven Elipsoidi • Çoklu-Sensör", desc: "Çoklu-sensör (LiDAR, BPA, Balistik, DNA) verilerini SE(3) katı cisim dönüşümü ve %95 hacimsel güven elipsoitleriyle (χ²₃ = 7.815) 3D olarak görselleştirir." }
          ]
        },
        {
          name: "Jeo-Adli İstihbarat & Uzamsal Biyojeokimya",
          shortName: "Jeo-Adli",
          badge: "GEOINT",
          subsystems: [
            { id: "31", name: "Çoklu İzotop İzoskap Köken Motoru", badge: "İZOSKAP", metrics: "Harmon Craig GMWL • Terzer-Wassenaar • Bataille Sr", desc: "Biyopatit ve keratin kalibrasyonlu çok değişkenli Gauss izoskap eşleştirmesi (H, O, Sr) ile coğrafi köken centroidi ve %95 güven yarıçapını belirler." },
            { id: "32", name: "Adli Toprak Pedolojisi & Jeokimyasal CoDa", badge: "TOPRAK-CODA", metrics: "QXRD Rietveld • ZTR İndeksi • CLR • ASTM E3272-21", desc: "Merkezlenmiş Log-Oran (CLR) dönüşümü, MCD Robust Mahalanobis Mesafesi ve Hotelling F-testi ile şüpheli ve kontrol topraklarını ASTM E3272 standartlarında karşılaştırır." },
            { id: "33", name: "Adli Palinoloji & Çevresel eDNA", badge: "PALİNOLOJİ", metrics: "RPF Normalizasyonu • 6-Biyom • 16S/ITS eDNA", desc: "Bağıl Polen Frekansını (RPF) hesaplar, Bray-Curtis ayrışmasını ölçer, 6 karasal biyomu sınıflandırır ve mikrobiyal eDNA uzamsal regresyonu ile koordinat kestirir." },
            { id: "34", name: "Rossmo Bayesian Coğrafi Profil Çıkarma", badge: "ROSSMO-GEO", metrics: "Hedefli Avlanma B=1.5km • SEI ≥ %90 • Canter Çemberi", desc: "Seri suç mahallerinde Rossmo avlanma formülüyle tepe çapa noktasını hesaplar, arama alanını (%5) daraltır ve fail hareketliliğini (Marauder vs Commuter) sınıflandırır." },
            { id: "35", name: "Çok Kriterli Bayesian CBS Delil Füzyonu", badge: "CBS-FÜZYON", metrics: "Ortak Raster Çarpımı • 2B Adaptif KDE • ISO 17025", desc: "İzotop, toprak, palinoloji ve suç profili katmanlarını 2B adaptif Gaussian KDE ile birleşik uzamsal sonsal yüzeyde birleştirerek ENFSI adli raporu üretir." }
          ]
        }
      ],
    },

    architecture: {
      badge: "Sistem Mimarisi",
      title: "Delil İşleme Mimarisi (DAG)",
      subtitle: "Ham FASTQ/FSA elektroferogram verilerinin ISO 17025 mahkeme onaylı adli delil paketlerine dönüşüm süreci.",
      layers: [
        {
          layer: "Katman 1: Biyolojik Örnek ve Veri Girişi",
          badge: "KABUL",
          nodes: ["Otozomal STR", "Adli SNP", "mtDNA rCRS", "Y-STR", "ABO/Rh Seroloji", "mRNA Sıvı Analizi", "16S Mikrobiyom", "Kararlı İzotoplar", "Toprak QXRD"]
        },
        {
          layer: "Katman 2: Biyobilişimsel Çıkarım ve İstatistiksel Analiz",
          badge: "ÇIKARIM",
          nodes: ["MCMC Karışım Dekonvolüsyonu", "Akrabalık İndeksi", "HIrisPlex-S Fenotipleme", "Dirichlet Popülasyon Modeli", "Horvath Yaş Saati", "BPA 3D"]
        },
        {
          layer: "Katman 3: Jeo-Adli & Uzamsal İstihbarat",
          badge: "GEOINT",
          nodes: ["Çoklu İzotop İzoskapları", "Toprak CoDa CLR", "Palinoloji 6-Biyom", "Rossmo Hedefli Avlanma", "2B Adaptif KDE Füzyonu"]
        },
        {
          layer: "Katman 4: Yönlü Vaka Çizgesi ve Delil Defteri",
          badge: "DEFTER",
          nodes: ["Vaka Çizge Motoru", "LIMS Numune Kaydı", "HMAC Delil Zinciri", "Merkle Ağacı İspatları"]
        },
        {
          layer: "Katman 5: ISO 17025 Kalite Kontrol Denetimi",
          badge: "KALİTE KONTROL",
          nodes: ["ISO 17025 Denetimi", "Heterozigot Dengesi Hb", "Stokastik Eşik ST", "GUM Belirsizlik Bütçesi", "Kontrol Numuneleri"]
        },
        {
          layer: "Katman 6: Uzman Analist İnceleme ve Yönetişimi",
          badge: "YÖNETİŞİM",
          nodes: ["Çift Analist Onay Süreci", "Gerekçeli Müdahale Kaydı", "Savcı Yanılgısı Kalkanı", "Circom ZKP Gizlilik Denetçisi"]
        },
        {
          layer: "Katman 7: Mahkeme Onaylı Adli Raporlama",
          badge: "RAPORLAMA",
          nodes: ["ISO 17025 Sertifika Derleyicisi", "PDF Rapor Aktarımı", "Uzman Tanık İfade Modu", "3D Jüri Görselleştirici"]
        }
      ]
    },
    security: {
      badge: "Kurumsal Güvenlik ve ISO 17025 Standartları",
      title: "Kriptografik Delil Zinciri ve ISO 17025 Akreditasyonu",
      subtitle: "Müdahaleye karşı korumalı denetim izi, sıfır bilgi kanıtlı delil doğrulaması ve katı delil zinciri takibi.",
      matrixTitle: "Teknik Platform Özellikleri ve Standartlar Matrisi",
      passedBadge: "%100 DOĞRULANMIŞ (829 TEST)",
      pillars: [
        {
          title: "Sıfır Bilgi İspatlı Gizlilik Denetçisi (ZKP)",
          desc: "Ham STR alel profilleri izole bellek alanlarında kalır. Circom/SnarkJS zkSNARK devreleri, ham genomik verileri iletmeden DNA eşleşme kriterlerini doğrulayan Groth16 kriptografik ispatları üretir."
        },
        {
          title: "Değiştirilemez Delil Zinciri",
          desc: "Tüm LIMS işlemleri, kalite kontrol kararları, analist onayları ve ISO raporları SHA-256 ile özetlenip HMAC denetimiyle kriptografik kayıt defterine sabitlenir."
        },
        {
          title: "Veri İzolasyon Mimarisi",
          desc: "Adli delil örnekleri, sıfır kalıcılıklı özel profil sınırlarına sahip izole belleklerde işlenir. Analiz sonrasında yalnızca anonimleştirilmiş istatistikler saklanır."
        },
        {
          title: "Dağıtık Düğüm Hesaplaması",
          desc: "Bölgeler arası adli sorgular dağıtık bir düğüm ağı üzerinden çalışır. Hiçbir tekil düğüm genomik veri tabanının tamamına erişemez."
        }
      ],
      specs: [
        { label: "Otozomal STR Multiplex Desteği", value: "Genişletilmiş 24-Lokus Adli Panel (20 FBI CODIS Çekirdek + ESS SE33, Penta D, Penta E, Amelogenin)" },
        { label: "Soy Analizleri", value: "Y-STR 27 Lokus (Clopper-Pearson %95 GA), X-STR 4 Bağlantı Kümesi (Argus X-12), mtDNA rCRS/RSRS" },
        { label: "Olasılıksal Karışım MCMC", value: "EuroForMix Gamma & STRmix Log-Normal 2-4 Katkıcı (Alel Kaybolması p_d & Eklenmesi p_i)" },
        { label: "Fenotip ve Epigenetik", value: "HIrisPlex-S 41-SNP (Göz/Saç/Ten), 55-SNP AIM GIS ve Horvath 5-CpG Epigenetik Yaş Saati" },
        { label: "Fiziksel ve İz İnceleme", value: "3D BPA En Küçük Kareler Çıkış Noktası, SEM-EDX GSR (Pb-Ba-Sb), CMC Balistik & Entomoloji ADD/ADH" },
        { label: "Jeo-Adli İstihbarat", value: "Çoklu İzotop İzoskapları (H/O/Sr), Toprak QXRD CoDa, Palinoloji eDNA & Rossmo Profilleme" },
        { label: "Popülasyon Modelleri", value: "NRC II Tavsiye 4.1 & 4.2 Balding-Nichols Dirichlet Alt Popülasyon Fst Düzeltmesi" },
        { label: "Cihaz Veri Kabulü", value: "CE GeneMapper CSV, qPCR Quantifiler Trio Cq/DI ve NGS MiSeq VCF Otomatik Geçidi" },
        { label: "ISO 17025 Uyumluluğu", value: "8 Bölümlü Adli Sertifika Derleyicisi, GUM Ölçüm Belirsizliği (k=2.00) ve 7 Kademeli ENFSI Ölçeği" },
        { label: "Doğrulanmış Test Paketi", value: "829 / 829 Otomatik Test Başarılı (%100 İnvaryant Doğrulaması)" },
        { label: "Ön Yüz Teknolojisi", value: "Next.js 16 Turbopack App Router, React 19, Tailwind CSS, Framer Motion" },
        { label: "Arka Yüz Teknolojisi", value: "FastAPI (Python 3.12), NumPy, SciPy, Scikit-learn, MCMC Metropolis-Hastings Motoru" },
        { label: "Gizlilik ve Delil Kütüğü", value: "Circom zk-SNARK Groth16 (BN254 Eşlemeleri) + İkili Merkle Ağacı O(log₂ N) Delil Kütüğü" }
      ]
    },
    faq: {
      badge: "Sıkça Sorulan Sorular",
      title: "Adli Genetik Platformu SSS",
      subtitle: "Sistem yetenekleri, mahkeme delil niteliği, LIMS entegrasyonu ve kurulum süreçleri hakkında teknik yanıtlar.",
      questions: {
        q1: "FORENZA düşük miktarlı karmaşık DNA karışımlarını nasıl işler?",
        a1: "FORENZA, pik yüksekliği değişimlerini, stutter oranlarını, alel kaybolmasını (drop-out) ve alel eklenmesini (drop-in) modelleyen Metropolis-Hastings MCMC olasılıksal genotipleme algoritmaları ile olabilirlik oranlarını (Likelihood Ratio) hesaplar.",
        q2: "Platform ISO/IEC 17025:2017 standartlarına uygun mudur?",
        a2: "Evet. Tüm biyobilişimsel süreçler, analitik eşik değerlerini ve eksiksiz delil zincirini içeren standart mahkeme raporları üretir.",
        q3: "FORENZA mevcut laboratuvar LIMS sistemleriyle entegre olabilir mi?",
        a3: "FORENZA, genetik analiz cihazlarından ve LIMS yazılımlarından FSA/HID elektroferogram ile FASTQ dosyalarını doğrudan aktaran çift yönlü RESTful API ve HL7/FHIR arayüzlerine sahiptir.",
        q4: "Hangi fenotipleme ve atasal soy modelleri desteklenmektedir?",
        a4: "FORENZA, göz, saç ve ten rengi tahmini için HIrisPlex-S modelini ve popülasyon kökeni tespiti için 55-SNP Coğrafi Atasal Soy (BGA) modellerini destekler.",
        q5: "Veri gizliliği ve Sıfır Bilgi İspatı (ZKP) nasıl sağlanır?",
        a5: "Platform, ham genetik verileri riske atmadan veri tabanları arasında profil eşleşmesini doğrulayan Circom tabanlı Sıfır Bilgi İspatı (ZKP) teknolojisini barındırır.",
      },
    },
    footer: {
      rights: "FORENZA Forensic Systems. Tüm hakları saklıdır.",
      tagline: "Kurumsal Biyobilişimsel Adli İstihbarat ve Delil İşletim Sistemi.",
      brandSubtitle: "ADLİ DELİL İŞLETİM SİSTEMİ",
      status: "35 Modül Aktif",
      columns: {
        col1Title: "Platform Modülleri",
        col1Links: ["35 Alt Sistem Matrisi", "Delil İşleme Mimarisi (DAG)", "Bio-Simülatör", "ISO 17025 İfade Modu"],
        col2Title: "Temel Yetenekler",
        col2Links: ["MCMC Olasılıksal Genotipleme", "HIrisPlex-S Fenotipleme", "Horvath Epigenetik Yaş Saati", "Jeo-Adli İstihbarat", "LIMS ve Cihaz Geçidi"],
        col3Title: "Adli Standartlar ve Uyumluluk",
        col3Links: ["ISO/IEC 17025:2017 Formatı", "SWGDAM ve ENFSI Kuralları", "Circom ZKP Gizlilik Denetçisi", "HMAC Delil Zinciri"],
      },
      disclaimer: {
        badge: "Akademik ve Simülasyon Sorumluluk Reddi",
        title: "Araştırma ve Simülasyon Ortamı Bildirimi",
        text: "FORENZA, akademik araştırma, algoritmik doğrulama ve simülasyon demonstrasyon platformudur. Burada üretilen analitik çıktılar, olabilirlik oranları (LR), fenotip tahminleri ve simüle edilmiş mahkeme raporları yalnızca algoritmik doğrulama, eğitim ve araştırma kıyaslaması amacıyla tasarlanmıştır. Bu yazılım akredite bir adli DNA laboratuvarının yerini almaz; deneysel laboratuvar doğrulaması olmaksızın gerçek adli kovuşturma, cezai hüküm veya aktif vaka süreçlerinde tek başına karar mercii olarak kullanılamaz.",
        isoNote: "ISO/IEC 17025 uyumluluğu, SWGDAM/ENFSI biyoistatistiksel raporlama standartlarına uygunluk anlamına gelir ve laboratuvarın kurumsal akreditasyonu yerine geçmez."
      }
    },
  },
};
