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
    status: string;
    columns: {
      col1Title: string;
      col1Links: string[];
      col2Title: string;
      col2Links: string[];
      col3Title: string;
      col3Links: string[];
    };
  };
}

export const saasTranslations: Record<SaasLanguage, SaasTranslation> = {
  en: {
    header: {
      bioSimulator: "Bio-Simulator",
      subsystems: "30 Subsystems",
      architecture: "Evidence DAG",
      security: "Security & ISO",
      launchDemo: "Launch Demo",
    },
    hero: {
      badge: "30 Integrated Subsystems • Multi-Omic Forensic OS",
      titleMain: "Integrated Biocomputational",
      titleHighlight: "Forensic Evidence OS",
      subtitle: "Enterprise multi-omic biocomputational platform integrating Autosomal & Lineage STRs, MCMC Probabilistic Genotyping, HIrisPlex-S Phenotyping, Horvath Epigenetic Aging, LIMS Workflow, QA/QC Gatekeeping, Analyst Governance, and ISO 17025 Court Reporting.",
      launchDemo: "Launch Live Evidence OS",
      exploreSubsystems: "Explore 30 Subsystems",
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
          sampleCode: "CASE_2026_COLD_09 — CODIS 20 Loci Matched",
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
        codisPanel: "CODIS Core 20 Panel",
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
        witnessInfo: "[INFO] Witness signals generated (20 loci constraints satisfied)",
        successCreated: "[SUCCESS] Proof proof.json created cleanly.",
        testnetReady: "Polygon Testnet Ready",
        zeroLeakage: "Zero Data Leakage Guaranteed",
        publicHash: "Public Proof Hash",
      },
    },
    subsystems: {
      badge: "Subsystem Registry",
      title: "30 Specialized Forensic Subsystems",
      subtitle: "Organized into 6 core architectural pillars covering every domain of forensic biology, probabilistic genotyping, epigenetics, pathology, LIMS SOP chains, and court testimony.",
      searchPlaceholder: "Filter subsystems...",
      activeCount: "5 Active Biocomputational Subsystems",
      operationalStatus: "5 / 5 OPERATIONAL",
      pillars: [
        {
          name: "Probabilistic Genotyping & Population",
          shortName: "Probabilistic & Population",
          badge: "CORE ENGINE",
          subsystems: [
            { id: "01", name: "Autosomal STR & Kinship Engine", badge: "CODIS-24", metrics: "24 Core Loci • LR Inclusion • Kinship Index", desc: "Calculates Likelihood Ratios for inclusion/exclusion across 24 core CODIS loci and evaluates parent-child / sibling kinship indices." },
            { id: "02", name: "MCMC Probabilistic Genotyping", badge: "MCMC-MH", metrics: "Metropolis-Hastings • 2-4 Contributors • Deconvolution", desc: "Metropolis-Hastings Markov Chain Monte Carlo deconvolution for 2-to-4 person complex DNA mixtures with stochastic parameters." },
            { id: "03", name: "Dirichlet Fst Population Genetics", badge: "NRC-II", metrics: "Balding-Nichols • Fst Correction • Dirichlet Smooth", desc: "Implements NRC II Recommendations 4.1 & 4.2 with subpopulation coancestry (Fst = 0.01 / 0.03) Dirichlet smoothing." },
            { id: "04", name: "Touch DNA & Low-Template LTDNA", badge: "LTDNA-MOD", metrics: "Dropout p_d • Drop-in p_i • Smooth Substrates", desc: "Models stochastic allele dropout (p_d) and drop-in (p_i) for low-mass template touch DNA recovered from smooth & porous evidence." },
            { id: "05", name: "Tippett Calibration Engine", badge: "TIPPETT", metrics: "H_p vs H_d • Non-Contributor LR • Calibration", desc: "Generates Tippett calibration curves plotting log10(LR) probability distributions under true contributor (H_p) vs non-contributor (H_d) hypotheses." }
          ]
        },
        {
          name: "Lineage Forensics & Kinship Inference",
          shortName: "Lineage & Kinship",
          badge: "HAPLOTYPE",
          subsystems: [
            { id: "06", name: "Y-STR Haplotype Forensics", badge: "Y-STR", metrics: "Clopper-Pearson 95% CI • Y-HRD Database • Haplotype", desc: "Computes Clopper-Pearson 95% binomial confidence intervals for Y-chromosome STR haplotypes with Y-HRD database matching." },
            { id: "07", name: "X-STR Linkage & Kinship Index", badge: "X-STR", metrics: "Linkage Equilibrium • Female Kinship KI_X", desc: "Evaluates X-chromosomal linked marker cluster transmission probabilities and female kinship likelihood ratios (KI_X)." },
            { id: "08", name: "mtDNA Control Region Forensics", badge: "mtDNA", metrics: "rCRS Alignment • RSRS • Haplogroup Tree", desc: "Aligns hypervariable regions (HV1/HV2/HV3) against revised Cambridge Reference Sequence (rCRS) for maternal lineage assignment." },
            { id: "09", name: "DVI Mass Disaster Identification", badge: "DVI-PED", metrics: "Pedigree Trees • Kinship Search • Disaster Victim", desc: "Pedigree likelihood evaluation for Mass Fatality / Disaster Victim Identification (DVI) matching reference kin." },
            { id: "10", name: "Ancient & Forensic SNP Mapper", badge: "aDNA-SNP", metrics: "Damage Patterns C->T • Low-Coverage • Map", desc: "Maps low-coverage forensic SNP arrays and ancient DNA C->T deamination damage patterns." }
          ]
        },
        {
          name: "Phenotyping & Biogeographic Ancestry",
          shortName: "Phenotyping & Ancestry",
          badge: "HIRISPLEX-S",
          subsystems: [
            { id: "11", name: "HIrisPlex-S Pigmentation Engine", badge: "HIRISPLEX", metrics: "Eye Color • Hair Color • Skin Tone", desc: "24-SNP HIrisPlex-S neural network model predicting iris color, hair pigmentation/morphology, and Fitzpatrick skin phototype." },
            { id: "12", name: "Biogeographic Ancestry (BGA)", badge: "BGA-55", metrics: "55-SNP Panel • 7 Global Populations • PCA", desc: "Calculates posterior probabilities for 7 global biogeographic populations using 55 ancestral informative markers (AIMs)." },
            { id: "13", name: "Facial Morphology & Craniofacial", badge: "CRANIO-3D", metrics: "3D Landmarks • Morphological Predictions", desc: "Predicts craniofacial structural proportions and facial landmark distances from genomic SNP markers." },
            { id: "14", name: "Hair Texture & Balding Risk", badge: "HAIR-TEX", metrics: "EDAR V370A • Male Pattern Baldness • Curl", desc: "Predicts hair morphology (straight/wavy/curly) and androgenetic alopecia predisposition." },
            { id: "15", name: "Freckling & UV Sensitivity", badge: "MC1R-UV", metrics: "MC1R Variants • Freckling Score • UV Sensitivity", desc: "Evaluates MC1R gene variant combinations to score ephelides (freckling) density and sun sensitivity." }
          ]
        },
        {
          name: "Epigenetics & Environmental Aging",
          shortName: "Epigenetics & Aging",
          badge: "EPIGENETICS",
          subsystems: [
            { id: "16", name: "Horvath Epigenetic Age Clock", badge: "HORVATH", metrics: "5-CpG Methylation • Epigenetic Age ±2.8 yr", desc: "Quantifies DNA methylation levels at key CpG loci to estimate chronological age at time of deposition with ±2.8 year precision." },
            { id: "17", name: "Tissue-Specific Body Fluid tDMR", badge: "tDMR-FLUID", metrics: "Blood • Saliva • Semen • Vaginal Fluid", desc: "Deconvolutes tissue-specific differentially methylated regions (tDMRs) to identify body fluid origin." },
            { id: "18", name: "Environmental Lifestyle Epigenetics", badge: "AHRR-LIFESTYLE", metrics: "AHRR Smoking Score • Alcohol • Epigenetics", desc: "Analyzes AHRR gene hypomethylation to infer chronic tobacco smoke exposure and environmental lifestyle signatures." },
            { id: "19", name: "Telomere Length Chronometer", badge: "TELO-CHRONO", metrics: "T/S Ratio • Cellular Senescence Rate", desc: "Measures relative telomere-to-single-copy-gene (T/S) length ratio for secondary biological age confirmation." },
            { id: "20", name: "Forensic MicroRNA Profiling", badge: "miRNA", metrics: "miR-451a • miR-205 • Body Fluid ID", desc: "Quantifies body-fluid-specific microRNA expression profiles for forensic identification of degraded samples." }
          ]
        },
        {
          name: "Pathology, Toxicology & Serology",
          shortName: "Pathology & Toxicology",
          badge: "PATHOLOGY",
          subsystems: [
            { id: "21", name: "Bloodstain Pattern Analysis (BPA)", badge: "BPA-3D", metrics: "Directionality • Area of Origin • Impact Angle", desc: "Calculates impact angle, stain directionality vectors, and 3D point-of-origin for bloodstain evidence." },
            { id: "22", name: "High-Resolution Digital Microscopy", badge: "MICROSCOPY", metrics: "Spermatozoa Head • Fiber • Diatom Counts", desc: "Computer vision classification for spermatozoa identification, textile fiber morphology, and diatom counts." },
            { id: "23", name: "Post-Mortem Toxicology & GC-MS", badge: "TOX-GCMS", metrics: "GC-MS Spectra • Blood Alcohol Concentration", desc: "Analyzes Gas Chromatography-Mass Spectrometry (GC-MS) spectral peaks for toxicological screening." },
            { id: "24", name: "Diatom & Forensic Palynology", badge: "PALYNO-ECO", metrics: "Diatom Ratio • Soil Pollen Geolocation", desc: "Correlates drowning site diatom assemblages and soil pollen signatures to pinpoint geographical crime scene origins." },
            { id: "25", name: "ABO / Rh Blood Serology", badge: "ABO-SERO", metrics: "ABO Glycosyltransferase • Rh Factor", desc: "Predicts classical ABO and Rh blood group antigens from ABO gene exon 6/7 sequencing." }
          ]
        },
        {
          name: "LIMS, ISO 17025 QA/QC & Governance",
          shortName: "LIMS & ISO 17025",
          badge: "COMPLIANCE",
          subsystems: [
            { id: "26", name: "LIMS Accessioning & Chain of Custody", badge: "LIMS-HMAC", metrics: "SHA-256 Custody Ledger • Barcode Tracking", desc: "Manages LIMS sample accessioning, chain-of-custody ledgers, storage temperatures, and analyst sign-offs." },
            { id: "27", name: "ISO 17025 QA/QC Inspection Matrix", badge: "ISO-17025", metrics: "7-Point QA Check • Stutter Thresholds", desc: "Enforces 7-point QA/QC inspection rules including heterozygote peak height ratio (Hb), analytical thresholds, and controls." },
            { id: "28", name: "Zero-Knowledge Privacy Auditor", badge: "ZKP-CIRCOM", metrics: "Groth16 Proofs • Polygon Ledger", desc: "Generates Circom zero-knowledge proofs confirming DNA profile match criteria without revealing raw genomic data." },
            { id: "29", name: "Expert Witness Court Mode Framework", badge: "COURT-MODE", metrics: "7-Point Framework • Prosecutor Shield", desc: "Compiles complete judicial testimony packages, verbal LR translation, and Prosecutor's Fallacy defense shields." },
            { id: "30", name: "Benchmark & Ground Truth Validator", badge: "VALIDATOR", metrics: "Synthetic Case Gen • ROC-AUC • 215 Tests", desc: "Runs automated validation benchmarks against synthetic ground-truth cases to verify pipeline accuracy." }
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
          nodes: ["Autosomal STR", "Forensic SNP", "mtDNA rCRS", "Y-STR", "ABO/Rh Serology", "mRNA Body Fluid", "16S Microbiology"]
        },
        {
          layer: "Layer 2: Biocomputational Inference Engine",
          badge: "INFERENCE",
          nodes: ["MCMC Mixture Deconvolution", "Kinship Index", "HIrisPlex-S Phenotype", "Dirichlet Fst Population"]
        },
        {
          layer: "Layer 3: Directed Case Graph & Ledger",
          badge: "LEDGER",
          nodes: ["Case Graph Engine", "LIMS Accessioning", "HMAC Chain of Custody"]
        },
        {
          layer: "Layer 4: ISO 17025 QA/QC Gatekeeper",
          badge: "QA/QC",
          nodes: ["ISO 17025 Inspection", "Heterozygote Balance Hb", "Stochastic ST", "Control Verification"]
        },
        {
          layer: "Layer 5: Human Analyst Governance",
          badge: "GOVERNANCE",
          nodes: ["Dual Sign-Off Review", "Override Rationale Logger", "Prosecutor Fallacy Shield"]
        },
        {
          layer: "Layer 6: Court-Admissible Reporting",
          badge: "REPORTING",
          nodes: ["ISO 17025 Certificate Compiler", "PDF Exporter", "Expert Witness Court Mode"]
        }
      ]
    },
    security: {
      badge: "Enterprise Security & Admissibility",
      title: "Cryptographic Evidence Custody & ISO 17025 Compliance",
      subtitle: "Tamper-evident audit logging, zero-knowledge evidence verification, and strict chain of custody.",
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
        { label: "Autosomal STR Support", value: "CODIS 24 Core Loci (D3S1358, vWA, FGA, D8S1179, D21S11, D18S51, SE33, etc.)" },
        { label: "Lineage Forensics", value: "Y-STR (Clopper-Pearson 95% CI), X-STR (KI_X Linkage), mtDNA rCRS Alignment" },
        { label: "Probabilistic Mixture MCMC", value: "Metropolis-Hastings 2-4 Contributor Deconvolution with Dropout (p_d) & Drop-in (p_i)" },
        { label: "Phenotype & Epigenetics", value: "HIrisPlex-S Extended (Eye/Hair/Skin/Freckles) & Horvath 5-CpG Epigenetic Age Clock" },
        { label: "Population Models", value: "NRC II Recommendation 4.1 & 4.2 Balding-Nichols Dirichlet Subpopulation Fst Correction" },
        { label: "Instrument Ingestion", value: "Automated Gateway for CE GeneMapper CSV, qPCR Quantifiler Trio Cq/DI & NGS MiSeq VCF" },
        { label: "ISO 17025 Compliance", value: "8-Section Formal Certificate Compiler, 7-Point QA/QC Inspection & Expert Witness Court Mode" },
        { label: "Verified Invariants", value: "215/215 Automated Pytest Execution Suite (100% Pass Rate)" },
        { label: "Frontend Stack", value: "Next.js 16 Turbopack App Router, React 19, Tailwind CSS, Framer Motion" },
        { label: "Backend Stack", value: "FastAPI (Python 3.12), PyTorch, Scikit-learn, MCMC Metropolis-Hastings Engine" },
        { label: "Privacy Auditor", value: "Circom zkSNARK Groth16 Proof Engine + Polygon Cryptographic Ledger" },
        { label: "Master Platform OS", value: "FORENZA Forensic Evidence OS 6-Layer Directed Acyclic Graph (DAG) PROD" }
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
      status: "30 Active Subsystems",
      columns: {
        col1Title: "Platform Subsystems",
        col1Links: ["30 Subsystems Matrix", "Evidence OS DAG", "Multi-Omic Bio-Simulator", "ISO 17025 Court Mode"],
        col2Title: "Core Capabilities",
        col2Links: ["MCMC Probabilistic Genotyping", "HIrisPlex-S Phenotyping", "Horvath Epigenetic Clock", "LIMS & Instrument Gateway"],
        col3Title: "Admissibility & Standards",
        col3Links: ["ISO/IEC 17025:2017", "SWGDAM & ENFSI Rules", "Circom ZKP Privacy Auditor", "HMAC Chain of Custody"],
      }
    },
  },
  tr: {
    header: {
      bioSimulator: "Bio-Simülatör",
      subsystems: "30 Subsystem",
      architecture: "DAG Mimarisi",
      security: "Güvenlik & ISO",
      launchDemo: "Demo Platform",
    },
    hero: {
      badge: "30 Entegre Adli Analiz Modülü • Çok Katmanlı Adli Biyoloji Platformu",
      titleMain: "Biyobilişimsel ve İstatistiksel",
      titleHighlight: "Adli Genetik Delil Platformu",
      subtitle: "Otozomal ve soy STR analizleri, MCMC olasılıksal genotipleme, HIrisPlex-S fenotip tahmini, Horvath epigenetik yaş saati, LIMS veri zinciri ve ISO/IEC 17025 adli rapor standartlarını tek bir işlem hattında birleştiren adli biyoloji platformu.",
      launchDemo: "Canlı Platformu Başlat",
      exploreSubsystems: "30 Modülü İncele",
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
          sampleCode: "CASE_2026_COLD_09 — CODIS 20 Lokus Eşleşti",
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
        skinTypes: { vPale: "Çok Açık Ten", fair: "Açık Ten", medium: "Buğday", olive: "Kumral", dBrown: "Esmer", dBlack: "Koyu Esmer" },
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
        codisPanel: "CODIS Çekirdek 20 Paneli",
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
        witnessInfo: "[BİLGİ] Girdi sinyalleri üretildi (20 lokus doğrulandı)",
        successCreated: "[BAŞARI] proof.json ispat dosyası üretildi.",
        testnetReady: "Polygon Testnet Hazır",
        zeroLeakage: "Sıfır Veri Sızıntısı Garantili",
        publicHash: "Genel İspat Özeti",
      },
    },
    subsystems: {
      badge: "Modüler Analiz Dizini",
      title: "30 Adli Genetik ve Biyobilişim Modülü",
      subtitle: "Adli biyoloji, olasılıksal genotipleme, epigenetik, patoloji, LIMS iş akışları ve adli rapor standartlarını kapsayan 6 temel mimari kategoride sunulmaktadır.",
      searchPlaceholder: "Modülleri filtreleyin...",
      activeCount: "5 Aktif Adli Analiz Modülü",
      operationalStatus: "5 / 5 FAAL",
      pillars: [
        {
          name: "Olasılıksal Genotipleme ve Popülasyon Analizleri",
          shortName: "Olasılıksal Genotipleme",
          badge: "TEMEL MOTOR",
          subsystems: [
            { id: "01", name: "Otozomal STR ve Akrabalık Motoru", badge: "CODIS-24", metrics: "24 Çekirdek Lokus • LR Analizi • Akrabalık İndeksi", desc: "24 CODIS çekirdek lokusunda dahil etme/dışlama olabilirlik oranlarını (LR) ve akrabalık indekslerini hesaplar." },
            { id: "02", name: "MCMC Karışım Dekonvolüsyonu", badge: "MCMC-MH", metrics: "Metropolis-Hastings • 2-4 Katkıcı • Karışım Analizi", desc: "Stokastik parametrelerle 2 ila 4 kişilik karmaşık DNA karışımları için Metropolis-Hastings MCMC ayrıştırması yürütür." },
            { id: "03", name: "Dirichlet Fst Popülasyon Genetiği", badge: "NRC-II", metrics: "Balding-Nichols • Fst Düzeltmesi • Dirichlet Modeli", desc: "Alt popülasyon akrabalığı (Fst = 0.01 / 0.03) ile NRC II Tavsiye 4.1 ve 4.2 standartlarında Dirichlet yumuşatması uygular." },
            { id: "04", name: "Temas DNA'sı ve LTDNA Analizi", badge: "LTDNA-MOD", metrics: "Alel Kaybolması p_d • Alel Eklenmesi p_i • Yüzey Tespiti", desc: "Düşük kütleli iz DNA örneklerinde stokastik alel kaybolması (p_d) ve alel eklenmesini (p_i) modeller." },
            { id: "05", name: "Tippett Kalibrasyon Analizi", badge: "TIPPETT", metrics: "H_p vs H_d • LR Dağılımı • Tippett Eğrisi", desc: "Gerçek katkıda bulunan (H_p) ile katkıda bulunmayan (H_d) hipotezleri için olabilirlik oranı kalibrasyon eğrilerini raporlar." }
          ]
        },
        {
          name: "Soy Analizleri ve Akrabalık Çıkarımı",
          shortName: "Soy & Akrabalık",
          badge: "HAPLOTİP",
          subsystems: [
            { id: "06", name: "Y-STR Haplotip Analizi", badge: "Y-STR", metrics: "Clopper-Pearson %95 Güven • Y-HRD Veri Tabanı", desc: "Y-kromozomu STR haplotipleri için Clopper-Pearson %95 binom güven aralıklarını hesaplar ve Y-HRD veri tabanıyla eşleştirir." },
            { id: "07", name: "X-STR Bağlantılı Markör Analizi", badge: "X-STR", metrics: "Bağlantı Dengesi • Kadın Soy Akrabalığı (KI_X)", desc: "X-kromozomu bağlantılı markör kümelerinin aktarım olasılıklarını ve kadın soy akrabalık indekslerini değerlendirir." },
            { id: "08", name: "mtDNA Kontrol Bölgesi Analizi", badge: "mtDNA", metrics: "rCRS Hizalaması • RSRS • Anne Soyu Haplogrubu", desc: "Anne soyu tespiti için hiperdeğişken bölgeleri (HV1/HV2/HV3) revize edilmiş Cambridge Referans Dizisi (rCRS) ile hizalar." },
            { id: "09", name: "DVI ve Afet Kurbanı Kimliklendirme", badge: "DVI-PED", metrics: "Soyağacı Analizi • Profil Eşleştirme • Interpol DVI", desc: "Toplu ölümler ve felaket kurbanlarının kimlik tespiti (DVI) için referans akrabalarla soyağacı olabilirlik değerlendirmesi yapar." },
            { id: "10", name: "Antik DNA ve Adli SNP Haritalama", badge: "aDNA-SNP", metrics: "C->T Deaminasyon Hasarı • Düşük Kapsama • SNP", desc: "Düşük kapsamlı adli SNP dizilimlerini ve antik DNA C->T deaminasyon hasar desenlerini haritalandırır." }
          ]
        },
        {
          name: "Fenotipleme ve Atasal Soy Tahmini",
          shortName: "Fenotipleme & Soy",
          badge: "HIRISPLEX-S",
          subsystems: [
            { id: "11", name: "HIrisPlex-S Pigmentasyon Analizi", badge: "HIRISPLEX", metrics: "Göz Rengi • Saç Rengi • Ten Fototipi", desc: "Göz rengi, saç pigmentasyonu/morfolojisi ve Fitzpatrick ten fototipini tahmin eden 24-SNP HIrisPlex-S yapay zeka modeli." },
            { id: "12", name: "Coğrafi Atasal Soy Tahmini (BGA)", badge: "BGA-55", metrics: "55-SNP Paneli • 7 Atasal Popülasyon • PCA", desc: "55 atasal bilgi markörü (AIM) kullanarak 7 küresel coğrafi popülasyon için sonralı olasılıkları hesaplar." },
            { id: "13", name: "Kraniyofasiyal Yüz Morfolojisi", badge: "CRANIO-3D", metrics: "3D Nirengi Noktaları • Morfolojik Tahmin", desc: "Genetik markörlerden kraniyofasiyal yapısal oranları ve yüz nirengi noktalarını tahmin eder." },
            { id: "14", name: "Saç Yapısı ve Kellik Riski", badge: "HAIR-TEX", metrics: "EDAR V370A • Erkek Tipi Kellik • Saç Şekli", desc: "Saç morfolojisini (düz/dalgalı/kıvırcık) ve androgenetik alopesi yatkınlığını tahmin eder." },
            { id: "15", name: "Çil Yoğunluğu ve UV Hassasiyeti", badge: "MC1R-UV", metrics: "MC1R Varyantları • Çil Skoru • Güneş Hassasiyeti", desc: "Çil yoğunluğunu ve güneşe hassasiyet derecesini MC1R geni varyant kombinasyonları üzerinden puanlar." }
          ]
        },
        {
          name: "Epigenetik ve Yaş Tayini",
          shortName: "Epigenetik & Yaş",
          badge: "EPİGENETİK",
          subsystems: [
            { id: "16", name: "Horvath Epigenetik Yaş Saati", badge: "HORVATH", metrics: "5-CpG Metilasyonu • Epigenetik Yaş ±2.8 Yıl", desc: "Delil bırakma anındaki kronolojik yaşı ±2.8 yıl hassasiyetle tahmin etmek için temel CpG lokuslarındaki metilasyon seviyelerini ölçer." },
            { id: "17", name: "Dokuya Özgü Vücut Sıvısı Tespiti (tDMR)", badge: "tDMR-FLUID", metrics: "Kan • Tükürük • Meni • Vajinal Sıvı", desc: "Dokuya özgü farklı metillenen bölgeleri (tDMR) çözümleyerek adli vücut sıvısı türünü tespit eder." },
            { id: "18", name: "Çevresel Yaşam Tarzı Epigenetiği", badge: "AHRR-LIFESTYLE", metrics: "AHRR Sigara Skoru • Alkol • Epigenetik", desc: "Kronik tütün kullanımı ve çevresel yaşam tarzı izlerini belirlemek için AHRR geni hipometilasyonunu analiz eder." },
            { id: "19", name: "Telomer Uzunluğu Analizi", badge: "TELO-CHRONO", metrics: "T/S Oranı • Hücresel Yaşlanma Hızı", desc: "İkincil biyolojik yaş doğrulaması için göreceli telomer/tek kopya gen (T/S) uzunluk oranını ölçer." },
            { id: "20", name: "Adli MicroRNA Profili", badge: "miRNA", metrics: "miR-451a • miR-205 • Vücut Sıvısı Tespiti", desc: "Bozunmuş örneklerde adli tespit için dokuya özgü microRNA ifade profillerini niceliksel olarak ölçer." }
          ]
        },
        {
          name: "Adli Patoloji, Toksikoloji ve Seroloji",
          shortName: "Patoloji & Toksikoloji",
          badge: "PATOLOJİ",
          subsystems: [
            { id: "21", name: "Kan Lekesi Deseni Analizi (BPA)", badge: "BPA-3D", metrics: "Yönelim • Çıkış Açısı • Darbe Açısı", desc: "Kan lekesi delilleri için darbe açısını, leke yönelim vektörlerini ve 3D çıkış noktasını hesaplar." },
            { id: "22", name: "Yüksek Çözünürlüklü Dijital Mikroskopi", badge: "MICROSCOPY", metrics: "Sperm Başlığı • Lif • Diyatom Sayımı", desc: "Spermatozoa tespiti, tekstil lifi morfolojisi ve diyatom sayımları için bilgisayarlı görü sınıflandırması." },
            { id: "23", name: "Otopsi Toksikolojisi ve GC-MS", badge: "TOX-GCMS", metrics: "GC-MS Spektrumu • Kanda Alkol Oranı", desc: "Toksikolojik tarama için Gaz Kromatografisi-Kütle Spektrometresi (GC-MS) pik spektrumlarını analiz eder." },
            { id: "24", name: "Diyatom ve Adli Palinoloji", badge: "PALYNO-ECO", metrics: "Diyatom Oranı • Polen Konumu", desc: "Olay yeri coğrafi konumunu belirlemek için suda boğulma diyatom topluluklarını ve toprak polen izlerini ilişkilendirir." },
            { id: "25", name: "ABO / Rh Kan Serolojisi", badge: "ABO-SERO", metrics: "ABO Glikosiltransferaz • Rh Faktörü", desc: "ABO geni ekzon 6/7 diziliminden klasik ABO ve Rh kan grubu antijenlerini tahmin eder." }
          ]
        },
        {
          name: "LIMS, ISO 17025 Kalite Kontrol ve Yönetişim",
          shortName: "LIMS & Akreditasyon",
          badge: "UYUMLULUK",
          subsystems: [
            { id: "26", name: "LIMS Kayıt ve Delil Zinciri Takibi", badge: "LIMS-HMAC", metrics: "SHA-256 Delil Kaydı • Barkodlu Takip", desc: "LIMS numune kabulünü, delil zinciri kayıtlarını, saklama sıcaklıklarını ve analist onaylarını yönetir." },
            { id: "27", name: "ISO 17025 Kalite Kontrol Denetim Matrisi", badge: "ISO-17025", metrics: "7 Noktalı Kalite Kontrol • Stutter Eşikleri", desc: "Heterozigot pik yüksekliği oranı (Hb), analitik eşikler ve kontroller dahil 7 noktalı kalite denetim kurallarını uygular." },
            { id: "28", name: "Sıfır Bilgi İspatlı Gizlilik Denetçisi (ZKP)", badge: "ZKP-CIRCOM", metrics: "Groth16 İspatları • Blokzincir Kaydı", desc: "Ham genetik verileri açık etmeden DNA profil eşleşme kriterlerini doğrulayan Circom ZKP ispatları üretir." },
            { id: "29", name: "Uzman Tanık Mahkeme İfade Modu", badge: "COURT-MODE", metrics: "7 Noktalı Adli Çerçeve • Savcı Kalkanı", desc: "Eksiksiz adli ifade paketleri, sözlü LR çevirisi ve Savcı Yanılgısına karşı koruma kalkanları derler." },
            { id: "30", name: "Doğrulama ve Sentetik Vaka Motoru", badge: "VALIDATOR", metrics: "Sentetik Vaka Üretimi • ROC-AUC • 215 Test", desc: "Hattın doğruluğunu onaylamak için sentetik vakalar üzerinden otomatik doğrulama testleri yürütür." }
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
          nodes: ["Otozomal STR", "Adli SNP", "mtDNA rCRS", "Y-STR", "ABO/Rh Seroloji", "mRNA Sıvı Analizi", "16S Mikrobiyom"]
        },
        {
          layer: "Katman 2: Biyobilişimsel Çıkarım ve İstatistiksel Analiz",
          badge: "ÇIKARIM",
          nodes: ["MCMC Karışım Dekonvolüsyonu", "Akrabalık İndeksi", "HIrisPlex-S Fenotipleme", "Dirichlet Popülasyon Modeli"]
        },
        {
          layer: "Katman 3: Yönlü Vaka Çizgesi ve Delil Defteri",
          badge: "DEFTER",
          nodes: ["Vaka Çizge Motoru", "LIMS Numune Kaydı", "HMAC Delil Zinciri"]
        },
        {
          layer: "Katman 4: ISO 17025 Kalite Kontrol Denetimi",
          badge: "KALİTE KONTROL",
          nodes: ["ISO 17025 Denetimi", "Heterozigot Dengesi Hb", "Stokastik Eşik ST", "Kontrol Numuneleri"]
        },
        {
          layer: "Katman 5: Uzman Analist İnceleme ve Yönetişimi",
          badge: "YÖNETİŞİM",
          nodes: ["Çift Analist Onay Süreci", "Gerekçeli Müdahale Kaydı", "Savcı Yanılgısı Kalkanı"]
        },
        {
          layer: "Katman 6: Mahkeme Onaylı Adli Raporlama",
          badge: "RAPORLAMA",
          nodes: ["ISO 17025 Sertifika Derleyicisi", "PDF Rapor Aktarımı", "Uzman Tanık İfade Modu"]
        }
      ]
    },
    security: {
      badge: "Kurumsal Güvenlik ve ISO 17025 Standartları",
      title: "Kriptografik Delil Zinciri ve ISO 17025 Akreditasyonu",
      subtitle: "Müdahaleye karşı korumalı denetim izi, sıfır bilgi kanıtlı delil doğrulaması ve katı delil zinciri takibi.",
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
        { label: "Otozomal STR Desteği", value: "CODIS 24 Çekirdek Lokus Analizi (D3S1358, vWA, FGA, D8S1179, D21S11, D18S51, SE33 vb.)" },
        { label: "Soy Analizleri", value: "Y-STR (%95 Güven Aralığı), X-STR (KI_X Akrabalık Bağlantısı), mtDNA rCRS Hizalaması" },
        { label: "Olasılıksal Karışım MCMC", value: "Metropolis-Hastings 2-4 Katkıcılı Karışım Ayrıştırması (p_d Alel Kaybolması & p_i Alel Eklenmesi)" },
        { label: "Fenotip ve Epigenetik", value: "Genişletilmiş HIrisPlex-S ve Horvath 5-CpG Epigenetik Yaş Saati" },
        { label: "Popülasyon Modelleri", value: "NRC II Tavsiye 4.1 & 4.2 Balding-Nichols Dirichlet Alt Popülasyon Fst Düzeltmesi" },
        { label: "Cihaz Veri Kabulü", value: "CE GeneMapper CSV, qPCR Quantifiler Trio Cq/DI ve NGS MiSeq VCF Otomatik Geçidi" },
        { label: "ISO 17025 Uyumluluğu", value: "8 Bölümlü Adli Sertifika Derleyicisi, 7 Noktalı Kalite Kontrol ve Uzman Tanık İfade Modu" },
        { label: "Yazılım Test Doğrulaması", value: "215/215 Otomatik Pytest Test Paketi (%100 Başarı Oranı)" },
        { label: "Ön Yüz Teknolojisi", value: "Next.js 16 Turbopack App Router, React 19, Tailwind CSS, Framer Motion" },
        { label: "Arka Yüz Teknolojisi", value: "FastAPI (Python 3.12), PyTorch, Scikit-learn, MCMC Metropolis-Hastings Motoru" },
        { label: "Gizlilik Denetçisi", value: "Circom zkSNARK Groth16 İspat Motoru + Polygon Kriptografik Kayıt Defteri" },
        { label: "Ana Platform OS", value: "FORENZA Adli Delil OS 6 Katmanlı Yönlü Yönsüz Çizge (DAG) PROD" }
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
      status: "30 Modül Aktif",
      columns: {
        col1Title: "Platform Modülleri",
        col1Links: ["30 Subsystem Matrix", "Delil İşleme Mimarisi (DAG)", "Bio-Simülatör", "ISO 17025 İfade Modu"],
        col2Title: "Temel Yetenekler",
        col2Links: ["MCMC Olasılıksal Genotipleme", "HIrisPlex-S Fenotipleme", "Horvath Epigenetik Yaş Saati", "LIMS ve Cihaz Geçidi"],
        col3Title: "Adli Standartlar ve Akreditasyon",
        col3Links: ["ISO/IEC 17025:2017", "SWGDAM ve ENFSI Kuralları", "Circom ZKP Gizlilik Denetçisi", "HMAC Delil Zinciri"],
      }
    },
  },
};
