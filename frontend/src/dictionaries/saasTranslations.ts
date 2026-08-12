export type SaasLanguage = "en" | "tr";

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
  bioSimulator: {
    badge: string;
    title: string;
    subtitle: string;
    sampleType: string;
    runSimulation: string;
    runningSim: string;
    resultsTitle: string;
    matchProb: string;
    kinshipIndex: string;
    ancestryPred: string;
    qualStatus: string;
  };
  subsystems: {
    badge: string;
    title: string;
    subtitle: string;
    searchPlaceholder: string;
    categories: {
      all: string;
      dna: string;
      pheno: string;
      epigenetics: string;
      lims: string;
      audit: string;
    };
  };
  architecture: {
    badge: string;
    title: string;
    subtitle: string;
    flowTitle: string;
    pipelineTag: string;
  };
  bioEngine: {
    badge: string;
    title: string;
    subtitle: string;
    metrics: {
      loci: string;
      lociSub: string;
      mcmc: string;
      mcmcSub: string;
      accuracy: string;
      accuracySub: string;
      iso: string;
      isoSub: string;
    };
  };
  security: {
    badge: string;
    title: string;
    subtitle: string;
    isoTitle: string;
    isoDesc: string;
    zkpTitle: string;
    zkpDesc: string;
    auditTitle: string;
    auditDesc: string;
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
    privacy: string;
    terms: string;
    security: string;
    status: string;
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
    bioSimulator: {
      badge: "Live Interactive Engine Sandbox",
      title: "Real-Time Bio-Simulator & Pipeline Testbench",
      subtitle: "Simulate multi-sample STR allele deconvolution, kinship likelihood ratios, and HIrisPlex-S phenotyping in real time.",
      sampleType: "Select Forensic Sample Type",
      runSimulation: "Run Biocomputational Pipeline",
      runningSim: "Executing MCMC Deconvolution...",
      resultsTitle: "Biocomputational Execution Results",
      matchProb: "Deconvolution Match Probability",
      kinshipIndex: "Combined Kinship Index (CPI)",
      ancestryPred: "HIrisPlex-S Phenotype & Ancestry",
      qualStatus: "ISO 17025 Quality Control Status",
    },
    subsystems: {
      badge: "Subsystem Registry",
      title: "30 Specialized Forensic Subsystems",
      subtitle: "Unified computational modules spanning DNA profiling, probabilistic genotyping, phenotyping, epigenetics, LIMS, and court admissibility.",
      searchPlaceholder: "Filter subsystems (e.g. STR, MCMC, Epigenetics, LIMS)...",
      categories: {
        all: "All Subsystems (30)",
        dna: "STR & Kinship",
        pheno: "Phenotyping & Ancestry",
        epigenetics: "Epigenetics & Aging",
        lims: "LIMS & Chain of Custody",
        audit: "Audit & ISO Compliance",
      },
    },
    architecture: {
      badge: "System Architecture",
      title: "Directed Acyclic Graph (DAG) Evidence Pipeline",
      subtitle: "How raw FASTQ/FSA electropherogram files transition into ISO 17025 court-admissible forensic evidence packages.",
      flowTitle: "Biocomputational Data Pipeline Flow",
      pipelineTag: "Automated End-to-End Pipeline",
    },
    bioEngine: {
      badge: "Engine Performance & Admissibility",
      title: "Admissibility & Verification Benchmarks",
      subtitle: "Rigorous computational metrics designed for high-throughput forensic laboratories and legal standards.",
      metrics: {
        loci: "CODIS Loci Tested",
        lociSub: "Autosomal & Y-STR Loci",
        mcmc: "MCMC Iterations",
        mcmcSub: "Per Mixture Deconvolution",
        accuracy: "Concordance Accuracy",
        accuracySub: "NIST Standard Profiles",
        iso: "ISO/IEC 17025",
        isoSub: "Court Admissible Reports",
      },
    },
    security: {
      badge: "Enterprise Security & Admissibility",
      title: "Cryptographic Evidence Custody & ISO 17025 Compliance",
      subtitle: "Tamper-evident audit logging, zero-knowledge evidence verification, and strict chain of custody.",
      isoTitle: "ISO/IEC 17025:2017 Admissibility Engine",
      isoDesc: "Automated generation of defense-ready court reports with full error rate reporting, stutter ratio validation, and analytical threshold compliance.",
      zkpTitle: "Zero-Knowledge Evidence Verification",
      zkpDesc: "Cryptographic proof of evidence integrity and profile match validation without exposing sensitive genomic raw data.",
      auditTitle: "Immutability & Analyst Governance",
      auditDesc: "Immutable audit trail registering every analyst interaction, parameter override, and algorithm invocation with cryptographic timestamps.",
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
      privacy: "Privacy Policy",
      terms: "Terms of Service",
      security: "Security & Admissibility",
      status: "System Operational",
    },
  },
  tr: {
    header: {
      bioSimulator: "Bio-Simülatör",
      subsystems: "30 Alt Sistem",
      architecture: "Delil Sistem DAG'ı",
      security: "Güvenlik & ISO",
      launchDemo: "Demo OS Başlat",
    },
    hero: {
      badge: "30 Entegre Alt Sistem • Multi-Omik Adli OS",
      titleMain: "Entegre Biyobilişimsel",
      titleHighlight: "Adli Delil İşletim Sistemi",
      subtitle: "Otozomal ve Soy STR'ları, MCMC Olasılıksal Genotipleme, HIrisPlex-S Fenotipleme, Horvath Epigenetik Yaş Tayini, LIMS İş Akışı, Kalite Kontrol ve ISO 17025 Mahkeme Raporlamasını birleştiren kurumsal adli platform.",
      launchDemo: "Canlı Delil İşletim Sistemini Başlat",
      exploreSubsystems: "30 Alt Sistemi İncele",
    },
    bioSimulator: {
      badge: "Canlı Etkileşimli Motor Test Alanı",
      title: "Gerçek Zamanlı Bio-Simülatör ve Test Ekranı",
      subtitle: "Çoklu örnek STR alel dekonvolüsyonunu, akrabalık olasılık oranlarını ve HIrisPlex-S fenotiplemesini gerçek zamanlı simüle edin.",
      sampleType: "Adli Örnek Tipini Seçin",
      runSimulation: "Biyobilişimsel Hattı Çalıştır",
      runningSim: "MCMC Dekonvolüsyonu Yürütülüyor...",
      resultsTitle: "Biyobilişimsel Çalıştırma Sonuçları",
      matchProb: "Dekonvolüsyon Eşleşme Olasılığı",
      kinshipIndex: "Kombine Akrabalık İndeksi (CPI)",
      ancestryPred: "HIrisPlex-S Fenotip ve Soy Tahmini",
      qualStatus: "ISO 17025 Kalite Kontrol Durumu",
    },
    subsystems: {
      badge: "Alt Sistem Kayıt Defteri",
      title: "30 Uzmanlaşmış Adli Alt Sistem",
      subtitle: "DNA profilleme, olasılıksal genotipleme, fenotipleme, epigenetik, LIMS ve mahkeme delil kabul edilebilirliğini kapsayan entegre adli modüller.",
      searchPlaceholder: "Alt sistemleri filtreleyin (ör. STR, MCMC, Epigenetik, LIMS)...",
      categories: {
        all: "Tüm Alt Sistemler (30)",
        dna: "STR ve Akrabalık",
        pheno: "Fenotipleme ve Soy",
        epigenetics: "Epigenetik ve Yaş Tayini",
        lims: "LIMS ve Delil Zinciri",
        audit: "Denetim ve ISO Uyum",
      },
    },
    architecture: {
      badge: "Sistem Mimarisi",
      title: "Yönlü Yönsüz Çizge (DAG) Delil İşleme Hattı",
      subtitle: "Ham FASTQ/FSA elektroferogram verilerinin ISO 17025 mahkeme onaylı delil paketlerine dönüşüm süreci.",
      flowTitle: "Biyobilişimsel Veri Akış Mimarisi",
      pipelineTag: "Otomatik Uçtan Uca Boru Hattı",
    },
    bioEngine: {
      badge: "Motor Performansı ve Delil Niteliği",
      title: "Kabul Edilebilirlik ve Doğrulama Ölçütleri",
      subtitle: "Yüksek hacimli adli laboratuvarlar ve hukuki standartlar için tasarlanmış biyobilişimsel metrikler.",
      metrics: {
        loci: "Test Edilen CODIS Lokusu",
        lociSub: "Otozomal ve Y-STR Lolusları",
        mcmc: "MCMC İterasyon Sayısı",
        mcmcSub: "Karışım Dekonvolüsyonu Başına",
        accuracy: "Uyum Doğruluğu",
        accuracySub: "NIST Standart Profilleri",
        iso: "ISO/IEC 17025",
        isoSub: "Mahkeme Onaylı Raporlar",
      },
    },
    security: {
      badge: "Kurumsal Güvenlik ve Hukuki Uyum",
      title: "Kriptografik Delil Zinciri ve ISO 17025 Uyumluluğu",
      subtitle: "Müdahaleye karşı korumalı denetim izi, sıfır bilgi kanıtlı delil doğrulaması ve katı zincir takibi.",
      isoTitle: "ISO/IEC 17025:2017 Mahkeme Uygunluk Motoru",
      isoDesc: "Analitik eşik değerleri, kekemelik (stutter) oranı doğrulaması ve hata oranı istatistikleri içeren mahkemeye hazır adli raporlar.",
      zkpTitle: "Sıfır Bilgi İspatlı (ZKP) Delil Doğrulaması",
      zkpDesc: "Hassas genetik verileri açık etmeden profil eşleşmelerini doğrulayan kriptografik ZKP altyapısı.",
      auditTitle: "Değiştirilemezlik ve Analist Yönetişimi",
      auditDesc: "Tüm analist müdahalelerini, parametre değişikliklerini ve algoritma adımlarını kriptografik zaman damgasıyla kaydeden denetim izi.",
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
      privacy: "Gizlilik Politikası",
      terms: "Kullanım Koşulları",
      security: "Güvenlik ve Delil Kabul Edilebilirliği",
      status: "Sistem Faal",
    },
  },
};
