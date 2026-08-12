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
      hairScore: string;
      accuracy: string;
    };
    strTab: {
      mixtureTitle: string;
      mixtureSub: string;
      contributors: string;
      deconvolution: string;
      peakHeight: string;
      alleleCall: string;
      logLr: string;
    };
    zkpTab: {
      proofTitle: string;
      proofSub: string;
      verifyButton: string;
      statusVerified: string;
      hashLabel: string;
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
      architecture: "Evidence OS DAG",
      security: "Security & ISO",
      launchDemo: "Launch Demo OS",
    },
    hero: {
      badge: "30 Integrated Subsystems • Multi-Omic Forensic OS",
      titleMain: "Integrated Biocomputational",
      titleHighlight: "Forensic Evidence OS",
      subtitle: "Enterprise multi-omic biocomputational platform integrating Autosomal & Lineage STRs, MCMC Probabilistic Genotyping, HIrisPlex-S Phenotyping, Horvath Epigenetic Aging, LIMS Workflow, QA/QC Gatekeeping, Analyst Governance, and ISO 17025 Court Reporting.",
      launchDemo: "Launch Live Evidence OS",
      exploreSubsystems: "Explore 30 Subsystems",
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
        irisTitle: "Ocular Iris Pigmentation (HERC2 / OCA2)",
        irisSub: "IrisPlex v2",
        targetGenotype: "Target Genotype",
        secondaryMarker: "Secondary Marker",
        posteriorProb: "Posterior Probability",
        confidence: "Confidence",
        skinTitle: "Fitzpatrick Skin Phototype (SLC24A5 / TYRP1)",
        skinSub: "HIrisPlex-S",
        hairTitle: "Hair Texture & Morphology (EDAR / FGFR2)",
        hairSub: "HairPlex",
        summaryTitle: "BIOMETRIC SUMMARY",
        synced: "100% Synced",
        predictedIris: "PREDICTED IRIS",
        hairScore: "HAIR TEXTURE SCORE",
        accuracy: "Accuracy",
      },
      strTab: {
        mixtureTitle: "DNA Mixture Deconvolution (Metropolis-Hastings MCMC)",
        mixtureSub: "2-4 Contributors",
        contributors: "Contributors Detected",
        deconvolution: "Deconvolution Likelihood Ratio (LR)",
        peakHeight: "Electropherogram Peak Height (RFU)",
        alleleCall: "CODIS Allele Calls",
        logLr: "Log10 LR Inclusion Score",
      },
      zkpTab: {
        proofTitle: "Zero-Knowledge Cryptographic Proof Auditor",
        proofSub: "Circom / Groth16",
        verifyButton: "Verify ZK Proof",
        statusVerified: "VERIFIED INVARIANT",
        hashLabel: "Public Proof Hash",
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
      status: "30 Subsystems Active",
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
      subsystems: "30 Biyobilişim Modülü",
      architecture: "Delil İşleme Mimarisi (DAG)",
      security: "Güvenlik & Hukuki Uyum",
      launchDemo: "Canlı Platformu Başlat",
    },
    hero: {
      badge: "30 Entegre Biyobilişim Modülü • Multi-Omik Adli OS",
      titleMain: "Entegre Biyobilişimsel",
      titleHighlight: "Adli Delil İşletim Sistemi",
      subtitle: "Otozomal ve Soy STR Profilleri, MCMC Olasılıksal Genotipleme, HIrisPlex-S Fenotipleme, Horvath Epigenetik Yaş Tayini, LIMS İş Akışları ve ISO/IEC 17025 Adli Raporlamasını Tek Çatıda Toplayan Kurumsal Adli İstihbarat Platformu.",
      launchDemo: "Canlı Delil İşletim Sistemini Başlat",
      exploreSubsystems: "30 Biyobilişim Modülünü İncele",
    },
    solutions: {
      badge: "Uygulama Alanları",
      title: "Kritik ve Yüksek Riskli Operasyonlar İçin Tasarlandı",
      subtitle: "FORENZA; adli tıp, kolluk kuvvetleri, afet kimliklendirme ve genetik araştırmaların karmaşık operasyonel gereksinimlerini karşılar.",
      domainInspection: "ALAN İNCELEMESİ VE VERİ AKIŞI",
      activeStandard: "Aktif Standart",
      primaryMetric: "BİRİNCİL ANALİTİK ÇIKTI",
      sessionTarget: "Oturum Hedef Referansı",
      verificationStatus: "Doğrulama Durumu",
      auditPassed: "NRC II Denetimi Onaylandı",
      items: [
        {
          id: "law-enforcement",
          title: "Kolluk Kuvvetleri ve Faili Meçhul Dosyalar",
          subtitle: "Soybağı Taraması ve Bozunmuş Örneklerde Olabilirlik Oranı (LR) Analizi",
          description: "Olay yerinden elde edilen kısmi veya bozunmuş STR profillerini analiz eder. Doğrudan eşleşme bulunamadığında soybağı motoru aracılığıyla akrabalık derecelerini belirleyerek faili meçhul dosyalar için akraba bazlı tarama (familial searching) imkanı sunar.",
          bulletPoints: [
            "Kayıp lokus içerikli eksik profillerde olabilirlik oranı (LR) hesaplaması",
            "Çok kuşaklı soyağaçlarında akraba bazlı tarama (familial search)",
            "Soruşturma coğrafyasına yönelik atasal köken ısı haritası",
            "Mahkeme delil kabul edilebilirliğine uygun değişmez adli raporlama",
          ],
          sampleMetric: "1.42e8 Olabilirlik Oranı (LR)",
          sampleCode: "CASE_2026_COLD_09 — CODIS 20 Lokus Eşleşti",
          label: "Kolluk Kuvvetleri",
        },
        {
          id: "dvi",
          title: "Afet Kurbanlarının Kimlik Tespiti (DVI)",
          subtitle: "Kitlesel Kayıplarda Hızlı Akrabalık İndeksi ve Kimliklendirme",
          description: "Toplu ölümlerde ve afet durumlarında kurban naaşlarını referans aile örnekleriyle hızlı akrabalık indeksleri üzerinden eşleştirir. Interpol DVI Bölüm 4 standartlarına uygun yüksek hacimli eşleşme raporları üretir.",
          bulletPoints: [
            "Eşzamanlı çoklu numune toplu işleme altyapısı",
            "Dakikalar içinde anne-baba ve kardeş akrabalık indeksi (KI)",
            "Numune kalite ve DNA bozunma puanlaması",
            "Interpol DVI Standart 4 ile tam uyumlu rapor çıktısı",
          ],
          sampleMetric: "%99.999 Eşleşme Olasılığı",
          sampleCode: "DVI_BATCH_402 — Interpol Bölüm 4 Standardı",
          label: "DVI Operasyonları",
        },
        {
          id: "border-security",
          title: "Sınır Güvenliği ve Akrabalık Doğrulaması",
          subtitle: "NRC II Standartlarında İstatistiksel Analiz ve Sıfır Bilgi İspatı (ZKP)",
          description: "Sınır geçişlerinde ve kimlik kontrol merkezlerinde beyan edilen akrabalık bağlarını istatistiksel kesinlikle doğrular. NRC II kuralları çerçevesinde hesaplanan olabilirlik oranları objektif adli delil sunar.",
          bulletPoints: [
            "Beyan edilen akrabalıklar için NRC II uyumlu LR hesaplaması",
            "Merkezi veri riski olmaksızın Sıfır Bilgi İspatlı (ZKP) doğrulama",
            "Belge doğrulaması için atasal coğrafya çapraz kontrolü",
            "Dağıtık düğüm hesaplamasıyla gerçek zamanlı doğrulama",
          ],
          sampleMetric: "Sıfır Veri Açığı (ZKP)",
          sampleCode: "BORDER_CHECK_882 — Groth16 Doğrulandı",
          label: "Sınır Güvenliği",
        },
        {
          id: "research",
          title: "Akademik ve Klinik Genetik Araştırmaları",
          subtitle: "Popülasyon Genetiği, Dirichlet Fst Düzeltmesi ve GTEx eQTL Entegrasyonu",
          description: "Araştırma kurumları için tekrarlanabilir olabilirlik oranı hesaplamaları, dışa aktarılabilir alel frekans matrisleri ve 54 doku tipi için GTEx eQTL çapraz referansları sağlayan doğrulanmış biyobilişim altyapısı.",
          bulletPoints: [
            "Dışa aktarılabilir alel frekans matrisleri ve LR analiz çıktıları",
            "54 doku tipi için GTEx eQTL veri entegrasyonu",
            "Tekrarlanabilir ve denetlenebilir biyobilişim boru hattı",
            "Popülasyon stratifikasyonu analizi ve Fst (theta) düzeltmesi",
          ],
          sampleMetric: "54 Doku eQTL Haritalandı",
          sampleCode: "GENOMICS_STUDY_V2 — Balding-Nichols theta=0.03",
          label: "Araştırma Laboratuvarları",
        },
      ],
    },
    bioSimulator: {
      badge: "Canlı Etkileşimli Biyobilişim Test Alanı",
      title: "Gerçek Zamanlı Bio-Simülatör ve Test Ekranı",
      subtitle: "Çoklu örnek STR alel dekonvolüsyonunu, akrabalık olasılık oranlarını ve HIrisPlex-S fenotiplemesini gerçek zamanlı simüle edin.",
      tabs: {
        phenotype: "Fenotip Tahmini",
        str: "STR Lokus Analizi",
        zkp: "ZKP İspat Denetçisi",
      },
      phenotypeTab: {
        irisTitle: "Göz İris Pigmentasyonu (HERC2 / OCA2)",
        irisSub: "IrisPlex v2",
        targetGenotype: "Hedef Genotip",
        secondaryMarker: "İkincil Markör",
        posteriorProb: "Sonralı Olasılık (Posterior Probability)",
        confidence: "Güven Seviyesi",
        skinTitle: "Fitzpatrick Ten Fototipi (SLC24A5 / TYRP1)",
        skinSub: "HIrisPlex-S",
        hairTitle: "Saç Dokusu ve Morfolojisi (EDAR / FGFR2)",
        hairSub: "HairPlex",
        summaryTitle: "BİYOMETRİK ÖZET",
        synced: "%100 Senkronize",
        predictedIris: "TAHMİN EDİLEN İRİS",
        hairScore: "SAÇ DOKUSU SKORU",
        accuracy: "Doğruluk Oranı",
      },
      strTab: {
        mixtureTitle: "DNA Karışım Dekonvolüsyonu (Metropolis-Hastings MCMC)",
        mixtureSub: "2-4 Katkıda Bulunan",
        contributors: "Tespit Edilen Katkıcı Sayısı",
        deconvolution: "Dekonvolüsyon Olabilirlik Oranı (LR)",
        peakHeight: "Elektroferogram Pik Yüksekliği (RFU)",
        alleleCall: "CODIS Alel Eşleşmeleri",
        logLr: "Log10 LR Dahil Olma Skoru",
      },
      zkpTab: {
        proofTitle: "Sıfır Bilgi Kriptografik İspat Denetçisi (ZKP)",
        proofSub: "Circom / Groth16",
        verifyButton: "ZK İspatını Doğrula",
        statusVerified: "DOĞRULANMIŞ İNVARİYANT",
        hashLabel: "Genel İspat Özeti (Public Proof Hash)",
      },
    },
    subsystems: {
      badge: "Modül Kayıt Defteri",
      title: "30 Uzmanlaşmış Biyobilişim Modülü",
      subtitle: "Adli biyoloji, olasılıksal genotipleme, epigenetik, patoloji, LIMS iş akışları ve mahkeme delil niteliğini kapsayan 6 ana mimari sütunda organize edilmiştir.",
      searchPlaceholder: "Modülleri filtreleyin...",
      activeCount: "5 Aktif Biyobilişim Modülü",
      operationalStatus: "5 / 5 FAAL",
      pillars: [
        {
          name: "Olasılıksal Genotipleme ve Popülasyon Genetiği",
          shortName: "Olasılıksal Genotipleme",
          badge: "TEMEL MOTOR",
          subsystems: [
            { id: "01", name: "Otozomal STR ve Akrabalık Motoru", badge: "CODIS-24", metrics: "24 Çekirdek Lokus • LR Analizi • Akrabalık İndeksi", desc: "24 CODIS çekirdek lokusunda dahil etme/dışlama olabilirlik oranlarını (LR) ve akrabalık indekslerini hesaplar." },
            { id: "02", name: "MCMC Olasılıksal Genotipleme", badge: "MCMC-MH", metrics: "Metropolis-Hastings • 2-4 Katkıcı • Dekonvolüsyon", desc: "Stokastik parametrelerle 2 ila 4 kişilik karmaşık DNA karışımları için Metropolis-Hastings MCMC dekonvolüsyonu yürütür." },
            { id: "03", name: "Dirichlet Fst Popülasyon Genetiği", badge: "NRC-II", metrics: "Balding-Nichols • Fst Düzeltmesi • Dirichlet Yumuşatma", desc: "Alt popülasyon akrabalığı (Fst = 0.01 / 0.03) ile NRC II Tavsiye 4.1 ve 4.2 standartlarında Dirichlet yumuşatması uygular." },
            { id: "04", name: "Temas DNA'sı ve Düşük Miktarlı LTDNA", badge: "LTDNA-MOD", metrics: "Alel Düşmesi p_d • Alel Eklenmesi p_i • Yüzey Tespiti", desc: "Pürüzsüz ve gözenekli delillerden elde edilen düşük miktarlı temas DNA'ları için stokastik alel düşmesi (p_d) ve eklenmesini (p_i) modeller." },
            { id: "05", name: "Tippett Kalibrasyon Motoru", badge: "TIPPETT", metrics: "H_p vs H_d • Katkıda Bulunmayan LR • Kalibrasyon", desc: "Gerçek katkıda bulunan (H_p) ile katkıda bulunmayan (H_d) hipotezleri altında log10(LR) olasılık dağılımlarını Tippett eğrileriyle raporlar." }
          ]
        },
        {
          name: "Soy Analizi ve Akrabalık Çıkarımı",
          shortName: "Soy & Akrabalık",
          badge: "HAPLOTİP",
          subsystems: [
            { id: "06", name: "Y-STR Haplotip Adli Analizi", badge: "Y-STR", metrics: "Clopper-Pearson %95 Güven • Y-HRD Veri Tabanı", desc: "Y-kromozomu STR haplotipleri için Clopper-Pearson %95 binom güven aralıklarını hesaplar ve Y-HRD veri tabanıyla eşleştirir." },
            { id: "07", name: "X-STR Bağlantı ve Akrabalık İndeksi", badge: "X-STR", metrics: "Bağlantı Dengesi • Kadın Akrabalık KI_X", desc: "X-kromozomal bağlantılı markör kümelerinin aktarım olasılıklarını ve kadın akrabalık olabilirlik oranlarını (KI_X) değerlendirir." },
            { id: "08", name: "mtDNA Kontrol Bölgesi Adli Analizi", badge: "mtDNA", metrics: "rCRS Hizalaması • RSRS • Haplogrup Ağacı", desc: "Anne soyu tespiti için hiperdeğişken bölgeleri (HV1/HV2/HV3) revize edilmiş Cambridge Referans Dizisi (rCRS) ile hizalar." },
            { id: "09", name: "DVI Toplu Afet & Kimlik Tespiti", badge: "DVI-PED", metrics: "Soyağacı Ağaçları • Akrabalık Aşamaları • DVI", desc: "Toplu ölümler ve felaket kurbanlarının kimlik tespiti (DVI) için referans akrabalarla soyağacı olabilirlik değerlendirmesi yapar." },
            { id: "10", name: "Antik ve Adli SNP Eşleştirici", badge: "aDNA-SNP", metrics: "Hasar Desenleri C->T • Düşük Kapsama • SNP", desc: "Düşük kapsamlı adli SNP dizilimlerini ve antik DNA C->T deaminasyon hasar desenlerini haritalandırır." }
          ]
        },
        {
          name: "Fenotipleme ve Coğrafi Soy Tahmini",
          shortName: "Fenotipleme & Soy",
          badge: "HIRISPLEX-S",
          subsystems: [
            { id: "11", name: "HIrisPlex-S Pigmentasyon Motoru", badge: "HIRISPLEX", metrics: "Göz Rengi • Saç Rengi • Ten Fototipi", desc: "Göz rengi, saç pigmentasyonu/morfolojisi ve Fitzpatrick ten fototipini tahmin eden 24-SNP HIrisPlex-S yapay zeka modeli." },
            { id: "12", name: "Coğrafi Soy Tahmini (BGA)", badge: "BGA-55", metrics: "55-SNP Paneli • 7 Küresel Popülasyon • PCA", desc: "55 atasal bilgi markörü (AIM) kullanarak 7 küresel coğrafi popülasyon için sonralı olasılıkları hesaplar." },
            { id: "13", name: "Yüz Morfolojisi ve Kafatası Tahmini", badge: "CRANIO-3D", metrics: "3D Nirengi Noktaları • Morfolojik Tahmin", desc: "Genomik SNP markörlerinden kraniyofasiyal yapısal oranları ve yüz nirengi noktalarını tahmin eder." },
            { id: "14", name: "Saç Dokusu ve Kellik Riski", badge: "HAIR-TEX", metrics: "EDAR V370A • Erkek Tipi Kellik • Saç Şekli", desc: "Saç morfolojisini (düz/dalgalı/kıvırcık) ve androgenetik alopesi yatkınlığını tahmin eder." },
            { id: "15", name: "Çil Tespiti ve UV Hassasiyeti", badge: "MC1R-UV", metrics: "MC1R Varyantları • Çil Skoru • UV Hassasiyeti", desc: "Çil yoğunluğunu ve güneşe hassasiyet derecesini MC1R geni varyant kombinasyonları üzerinden puanlar." }
          ]
        },
        {
          name: "Epigenetik ve Çevresel Yaş Tayini",
          shortName: "Epigenetik & Yaş",
          badge: "EPİGENETİK",
          subsystems: [
            { id: "16", name: "Horvath Epigenetik Yaş Saati", badge: "HORVATH", metrics: "5-CpG Metilasyonu • Epigenetik Yaş ±2.8 Yıl", desc: "Delil bırakma anındaki kronolojik yaşı ±2.8 yıl hassasiyetle tahmin etmek için temel CpG lokuslarındaki metilasyon seviyelerini ölçer." },
            { id: "17", name: "Vücut Sıvısı Tespiti (tDMR)", badge: "tDMR-FLUID", metrics: "Kan • Tükürük • Meni • Vajinal Sıvı", desc: "Dokuya özgü farklı metillenen bölgeleri (tDMR) çözümleyerek adli vücut sıvısı türünü tespit eder." },
            { id: "18", name: "Çevresel Yaşam Tarzı Epigenetiği", badge: "AHRR-LIFESTYLE", metrics: "AHRR Sigara Skoru • Alkol • Epigenetik", desc: "Kronik tütün kullanımı ve çevresel yaşam tarzı izlerini belirlemek için AHRR geni hipometilasyonunu analiz eder." },
            { id: "19", name: "Telomer Uzunluğu Kronometresi", badge: "TELO-CHRONO", metrics: "T/S Oranı • Hücresel Yaşlanma Hızı", desc: "İkincil biyolojik yaş doğrulaması için göreceli telomer/tek kopya gen (T/S) uzunluk oranını ölçer." },
            { id: "20", name: "Adli MicroRNA Profili", badge: "miRNA", metrics: "miR-451a • miR-205 • Vücut Sıvısı ID", desc: "Bozunmuş örneklerde adli tespit için dokuya özgü microRNA ifade profillerini niceliksel olarak ölçer." }
          ]
        },
        {
          name: "Adli Patoloji, Toksikoloji ve Seroloji",
          shortName: "Patoloji & Toksikoloji",
          badge: "PATOLOJİ",
          subsystems: [
            { id: "21", name: "Kan Lekesi Deseni Analizi (BPA)", badge: "BPA-3D", metrics: "Yönelim • Çıkış Alanı • Darbe Açısı", desc: "Kan lekesi delilleri için darbe açısını, leke yönelim vektörlerini ve 3D çıkış noktasını hesaplar." },
            { id: "22", name: "Yüksek Çözünürlüklü Dijital Mikroskopi", badge: "MICROSCOPY", metrics: "Sperm Başlığı • Lif • Diyatom Sayımı", desc: "Spermatozoa tespiti, tekstil lifi morfolojisi ve diyatom sayımları için bilgisayarlı görü sınıflandırması." },
            { id: "23", name: "Otopsi Toksikolojisi ve GC-MS", badge: "TOX-GCMS", metrics: "GC-MS Spektrumu • Kanda Alkol Oranı", desc: "Toksikolojik tarama için Gaz Kromatografisi-Kütle Spektrometresi (GC-MS) pik spektrumlarını analiz eder." },
            { id: "24", name: "Diyatom ve Adli Palinoloji (Polen)", badge: "PALYNO-ECO", metrics: "Diyatom Oranı • Polen Konumu", desc: "Olay yeri coğrafi konumunu belirlemek için suda boğulma diyatom topluluklarını ve toprak polen izlerini ilişkilendirir." },
            { id: "25", name: "ABO / Rh Kan Serolojisi", badge: "ABO-SERO", metrics: "ABO Glikosiltransferaz • Rh Faktörü", desc: "ABO geni ekzon 6/7 diziliminden klasik ABO ve Rh kan grubu antijenlerini tahmin eder." }
          ]
        },
        {
          name: "LIMS, ISO 17025 Kalite Kontrol ve Yönetişim",
          shortName: "LIMS & Hukuki Uyum",
          badge: "UYUMLULUK",
          subsystems: [
            { id: "26", name: "LIMS Kabul ve Delil Zinciri Takibi", badge: "LIMS-HMAC", metrics: "SHA-256 Delil Defteri • Barkod Takibi", desc: "LIMS numune kabulünü, delil zinciri kayıtlarını, saklama sıcaklıklarını ve analist onaylarını yönetir." },
            { id: "27", name: "ISO 17025 Kalite Kontrol Denetim Matrisi", badge: "ISO-17025", metrics: "7 Noktalı Kalite Kontrol • Stutter Eşikleri", desc: "Heterozigot pik yüksekliği oranı (Hb), analitik eşikler ve kontroller dahil 7 noktalı kalite denetim kurallarını uygular." },
            { id: "28", name: "Sıfır Bilgi İspatlı (ZKP) Gizlilik Denetçisi", badge: "ZKP-CIRCOM", metrics: "Groth16 İspatları • Polygon Blokzincir", desc: "Ham genetik verileri açık etmeden DNA profil eşleşme kriterlerini doğrulayan Circom ZKP ispatları üretir." },
            { id: "29", name: "Uzman Tanık Mahkeme Modu Çerçevesi", badge: "COURT-MODE", metrics: "7 Noktalı Çerçeve • İddia Kalkanı", desc: "Eksiksiz adli ifade paketleri, sözlü LR çevirisi ve Savcı Yanılgısına karşı koruma kalkanları derler." },
            { id: "30", name: "Doğrulama ve Benchmark Test Motoru", badge: "VALIDATOR", metrics: "Sentetik Vaka Üretimi • ROC-AUC • 215 Test", desc: "Hattın doğruluğunu onaylamak için sentetik vakalar üzerinden otomatik doğrulama testleri yürütür." }
          ]
        }
      ],
    },
    architecture: {
      badge: "Sistem Mimarisi",
      title: "Yönlü Yönsüz Çizge (DAG) Delil İşleme Hattı",
      subtitle: "Ham FASTQ/FSA elektroferogram verilerinin ISO 17025 mahkeme onaylı delil paketlerine dönüşüm süreci.",
      layers: [
        {
          layer: "Katman 1: Multi-Omik Delil Kabulü",
          badge: "KABUL",
          nodes: ["Otozomal STR", "Adli SNP", "mtDNA rCRS", "Y-STR", "ABO/Rh Seroloji", "mRNA Vücut Sıvısı", "16S Mikrobiyoloji"]
        },
        {
          layer: "Katman 2: Biyobilişimsel Çıkarım Motoru",
          badge: "ÇIKARIM",
          nodes: ["MCMC Karışım Dekonvolüsyonu", "Akrabalık İndeksi", "HIrisPlex-S Fenotip", "Dirichlet Fst Popülasyon"]
        },
        {
          layer: "Katman 3: Yönlü Vaka Çizgesi ve Kayıt Defteri",
          badge: "DEFTER",
          nodes: ["Vaka Çizge Motoru", "LIMS Kabul İşlemi", "HMAC Delil Zinciri"]
        },
        {
          layer: "Katman 4: ISO 17025 Kalite Kontrol Muhafızı",
          badge: "KALİTE KONTROL",
          nodes: ["ISO 17025 Denetimi", "Heterozigot Dengesi Hb", "Stokastik Eşik ST", "Kontrol Doğrulaması"]
        },
        {
          layer: "Katman 5: İnsan Analist Yönetişimi",
          badge: "YÖNETİŞİM",
          nodes: ["Çift Analist Onay İncelemesi", "Gerekçe Kayıt Defteri", "Savcı Yanılgısı Kalkanı"]
        },
        {
          layer: "Katman 6: Mahkeme Onaylı Raporlama",
          badge: "RAPORLAMA",
          nodes: ["ISO 17025 Sertifika Derleyicisi", "PDF Dışa Aktarma", "Uzman Tanık Mahkeme Modu"]
        }
      ]
    },
    security: {
      badge: "Kurumsal Güvenlik ve Hukuki Uyum",
      title: "Kriptografik Delil Zinciri ve ISO 17025 Uyumluluğu",
      subtitle: "Müdahaleye karşı korumalı denetim izi, sıfır bilgi kanıtlı delil doğrulaması ve katı zincir takibi.",
      pillars: [
        {
          title: "Sıfır Bilgi İspatlı Gizlilik Denetçisi (ZKP)",
          desc: "Ham STR alel profilleri izole kalır. Circom/SnarkJS zkSNARK devreleri, ham genomik verileri iletmeden DNA eşleşme kriterlerini doğrulayan Groth16 kriptografik ispatları üretir."
        },
        {
          title: "Değiştirilemez Delil Zinciri",
          desc: "Tüm LIMS işlemleri, kalite kontrol kararları, analist onayları ve ISO raporları SHA-256 ile özetlenip HMAC denetimiyle Polygon kriptografik kayıt defterine sabitlenir."
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
        { label: "Otozomal STR Desteği", value: "CODIS 24 Çekirdek Lokus (D3S1358, vWA, FGA, D8S1179, D21S11, D18S51, SE33, vb.)" },
        { label: "Soy Adli Analizi", value: "Y-STR (Clopper-Pearson %95 Güven), X-STR (KI_X Bağlantısı), mtDNA rCRS Hizalaması" },
        { label: "Olasılıksal Karışım MCMC", value: "Metropolis-Hastings 2-4 Katkıda Bulunan Dekonvolüsyonu (p_d Alel Düşmesi & p_i Alel Eklenmesi)" },
        { label: "Fenotip ve Epigenetik", value: "Genişletilmiş HIrisPlex-S (Göz/Saç/Ten/Çil) ve Horvath 5-CpG Epigenetik Yaş Saati" },
        { label: "Popülasyon Modelleri", value: "NRC II Tavsiye 4.1 ve 4.2 Balding-Nichols Dirichlet Alt Popülasyon Fst Düzeltmesi" },
        { label: "Cihaz Veri Kabulü", value: "CE GeneMapper CSV, qPCR Quantifiler Trio Cq/DI ve NGS MiSeq VCF Otomatik Geçidi" },
        { label: "ISO 17025 Uyumluluğu", value: "8 Bölümlü Resmi Sertifika Derleyici, 7 Noktalı Kalite Kontrol ve Uzman Tanık Mahkeme Modu" },
        { label: "Doğrulanmış İnvarantlar", value: "215/215 Otomatik Pytest Test Paketi (%100 Başarı Oranı)" },
        { label: "Ön Yüz Teknolojisi", value: "Next.js 16 Turbopack App Router, React 19, Tailwind CSS, Framer Motion" },
        { label: "Arka Yüz Teknolojisi", value: "FastAPI (Python 3.12), PyTorch, Scikit-learn, MCMC Metropolis-Hastings Motoru" },
        { label: "Gizlilik Denetçisi", value: "Circom zkSNARK Groth16 İspat Motoru + Polygon Kriptografik Kayıt Defteri" },
        { label: "Ana Platform OS", value: "FORENZA Adli Delil OS 6 Katmanlı Yönlü Yönsüz Çizge (DAG) PROD" }
      ]
    },
    faq: {
      badge: "Sıkça Sorulan Sorular",
      title: "Adli Delil OS SSS",
      subtitle: "Sistem yetenekleri, mahkeme delil niteliği, LIMS entegrasyonu ve kurulum süreçleri hakkında sık sorulanlar.",
      questions: {
        q1: "FORENZA düşük miktarlı karmaşık DNA karışımlarını nasıl işler?",
        a1: "FORENZA, pik yüksekliği değişimlerini, stutter oranlarını, alel düşmesi (drop-out) ve alel eklenmesini (drop-in) modelleyen Metropolis-Hastings MCMC olasılıksal genotipleme algoritmaları ile olabilirlik oranlarını (Likelihood Ratio) hesaplar.",
        q2: "Platform ISO/IEC 17025:2017 standartlarına uygun mudur?",
        a2: "Evet. Tüm biyobilişimsel süreçler, analitik eşik değerlerini ve eksiksiz delil zincirini içeren standart mahkeme raporları üretir.",
        q3: "FORENZA mevcut laboratuvar LIMS sistemleriyle entegre olabilir mi?",
        a3: "FORENZA, genetik analiz cihazlarından ve LIMS yazılımlarından FSA/HID elektroferogram ile FASTQ dosyalarını doğrudan aktaran çift yönlü RESTful API ve HL7/FHIR arayüzlerine sahiptir.",
        q4: "Hangi fenotipleme ve soy (ancestry) modelleri desteklenmektedir?",
        a4: "FORENZA, göz, saç ve ten rengi tahmini için HIrisPlex-S modelini ve popülasyon kökeni tespiti için 55-SNP Coğrafi Soy (BGA) modellerini destekler.",
        q5: "Veri gizliliği ve Sıfır Bilgi İspatı (ZKP) nasıl sağlanır?",
        a5: "Platform, ham genetik verileri riske atmadan veri tabanları arasında profil eşleşmesini doğrulayan Circom tabanlı Sıfır Bilgi İspatı (ZKP) teknolojisini barındırır.",
      },
    },
    footer: {
      rights: "FORENZA Forensic Systems. Tüm hakları saklıdır.",
      tagline: "Kurumsal Biyobilişimsel Adli İstihbarat ve Delil İşletim Sistemi.",
      status: "30 Biyobilişim Modülü Faal",
      columns: {
        col1Title: "Platform Modülleri",
        col1Links: ["30 Biyobilişim Modülü", "Delil İşleme Mimarisi (DAG)", "Multi-Omik Bio-Simülatör", "ISO 17025 Mahkeme Modu"],
        col2Title: "Temel Yetenekler",
        col2Links: ["MCMC Olasılıksal Genotipleme", "HIrisPlex-S Fenotipleme", "Horvath Epigenetik Yaş Saati", "LIMS ve Cihaz Geçidi"],
        col3Title: "Delil Niteliği ve Standartlar",
        col3Links: ["ISO/IEC 17025:2017", "SWGDAM ve ENFSI Kuralları", "Circom ZKP Gizlilik Denetçisi", "HMAC Delil Zinciri"],
      }
    },
  },
};
