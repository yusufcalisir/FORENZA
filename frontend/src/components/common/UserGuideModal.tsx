"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BookOpen,
  X,
  Dna,
  Eye,
  Globe,
  Sliders,
  ShieldCheck,
  Cpu,
  ChevronRight,
  FlaskConical,
  Scale,
  Sparkles
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function UserGuideModal({
  isOpen,
  onClose
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const { lang, t } = useSaasLanguage();
  const [activeTab, setActiveTab] = useState<number>(0);

  if (!isOpen) return null;

  const isTr = lang === "tr";

  const guideChapters = isTr ? [
    {
      id: "getting-started",
      title: "1. Hızlı Başlangıç & Vaka Yükleme",
      icon: Sparkles,
      color: "text-cyan-400",
      content: [
        "FORENZA Biyo-Adli DNA & İstatistiksel Genotipleme İstasyonu'na hoş geldiniz.",
        "Sağ üstteki 'Open DNA & SNP Terminal' butonunu kullanarak hazırdaki vaka örneklerini (Sample EU - Kuzey Avrupa / Sample AA - Batı Afrika) tek tıkla yükleyebilirsiniz.",
        "Dilerseniz kendi STR alel sayılarınızı (CODIS 20/24 Loci) ve SNP mutasyonlarınızı (HIrisPlex-S / 55-SNP AIM) elle girip 'Apply & Recalculate Profile Features' butonuna tıklayarak canlı biyolojik kestirimleri yeniden hesaplayabilirsiniz."
      ]
    },
    {
      id: "phenotype",
      title: "2. HIrisPlex-S Fenotip Tahmin Motoru",
      icon: Eye,
      color: "text-emerald-400",
      content: [
        "Tahmini Fenotip (Inferred Phenotype) paneli, DNA numunesinden kişinin dış görünüşünü yüksek olasılıkla hesaplar.",
        "Göz Rengi (Eye Color): HERC2 (rs12913832) ve OCA2 genlerindeki polimorfizmlere göre Mavi (%94.2), Elâ (%78.4) veya Koyu Kahverengi (%98.6) olasılıklarını verir.",
        "Ten Tipi (Skin Phototype): SLC45A2 ve SLC24A5 delesyonları incelenerek Fitzpatrick I/II (Açık Ten) ile V/VI (Esmer/Koyu Ten) aralığında derecelendirilir.",
        "Saç Yapısı (Hair Morphology): EDAR ve FGFR1 geni aracılığıyla Düz Saç (%88) veya Kıvırcık/Bukleli Saç (%94) tespiti yapılır."
      ]
    },
    {
      id: "ancestry-gis",
      title: "3. Atasal Soy (BGA) & Canlı Harita (GIS)",
      icon: Globe,
      color: "text-purple-400",
      content: [
        "Biogeographic Ancestry (55-SNP AIM) Paneli: Numunenin biyocoğrafi kökenini %98.4 Primary (Birincil) ve %1.6 Secondary (İkincil) atasal küme olarak sınıflandırır.",
        "Canlı Adli GIS Haritası (Forensic Map Engine): Numunenin muhtemel coğrafi koordinatlarını (Enlem/Boylam), şehir ve ülkeyi harita üzerinde ısı haritası (Heatmap) ve hedef halkaları (Confidence Rings) ile görselleştirir.",
        "Örnek: Berlin, Almanya (52.5200° N, 13.4050° E) veya Lagos, Nijerya (6.5244° N, 3.3792° E)."
      ]
    },
    {
      id: "str-lr",
      title: "4. STR Alel Eşleşmesi & Likelihood Ratio (LR)",
      icon: Dna,
      color: "text-amber-400",
      content: [
        "STR Locus Analysis Tablosu: D3S1358, vWA, FGA, TH01, TPOX vb. 24 CODIS lokusundaki şüpheli numune ile olay yeri numunesinin alel eşleşmelerini karşılaştırır.",
        "Likelihood Ratio (LR - Olabilirlik Oranı): 10¹⁸·⁴ gibi astronomik olasılık oranları hesaplar. ENFSI ve SWGDAM adli standartlarına göre 10⁶ üzeri değerler 'Conclusive Support for Identity' (Kesin Kimlik Tespiti) kabul edilir."
      ]
    },
    {
      id: "epigenetics-zkp",
      title: "5. Epigenetik Yaş & Sıfır Bilgi İspatı (ZKP)",
      icon: ShieldCheck,
      color: "text-rose-400",
      content: [
        "Epigenetic Age Clock: Biyolojik numunenin bırakıldığı andaki kronolojik yaşını 5 CpG metilasyon lokusunda ±2.1 yıl sapma payı ile hesaplar.",
        "Zero-Knowledge Proof (ZKP - Circom/Groth16): Kriptografik Groth16 ZK-SNARK ispatları üreterek ham DNA dizilimlerini laboratuvar dışına aktarmadan kimlik doğrulama yapılmasını sağlar."
      ]
    }
  ] : [
    {
      id: "getting-started",
      title: "1. Quick Start & Case Loading",
      icon: Sparkles,
      color: "text-cyan-400",
      content: [
        "Welcome to the FORENZA Biocomputational DNA & Statistical Genotyping Workstation.",
        "Click the top-right 'Open DNA & SNP Terminal' button to load pre-configured sample cases (Sample EU - Northern European / Sample AA - West African) with one click.",
        "You can manually adjust STR allele values (CODIS 20/24 Loci) and SNP markers (HIrisPlex-S / 55-SNP AIM), then click 'Apply & Recalculate Profile Features' to run live biocomputational predictions."
      ]
    },
    {
      id: "phenotype",
      title: "2. HIrisPlex-S Phenotype Engine",
      icon: Eye,
      color: "text-emerald-400",
      content: [
        "The Inferred Phenotype panel predicts physical appearance features directly from DNA markers with high statistical confidence.",
        "Eye Color: Based on HERC2 (rs12913832) and OCA2 polymorphisms, calculating posterior probabilities for Blue (94.2%), Hazel (78.4%), or Dark Brown (98.6%).",
        "Skin Phototype: SLC45A2 and SLC24A5 variants determine Fitzpatrick Skin Type from Type I/II (Fair Skin) to Type V/VI (Dark Phototype).",
        "Hair Morphology: EDAR and FGFR1 genes predict Straight Hair (88%) vs Curly/Coily Hair (94%)."
      ]
    },
    {
      id: "ancestry-gis",
      title: "3. Ancestry (BGA) & Live GIS Map Engine",
      icon: Globe,
      color: "text-purple-400",
      content: [
        "Biogeographic Ancestry (55-SNP AIM) Panel: Classifies genetic ancestry into Primary (98.4%) and Secondary (1.6%) population reference clusters.",
        "Live GIS Forensic Map Engine: Renders heatmap probability density circles and locked coordinate centroids (Latitude/Longitude, City, Country) on an interactive dark GIS canvas.",
        "Examples: Berlin, Germany (52.5200° N, 13.4050° E) or Lagos, Nigeria (6.5244° N, 3.3792° E)."
      ]
    },
    {
      id: "str-lr",
      title: "4. STR Allele Matching & Likelihood Ratio (LR)",
      icon: Dna,
      color: "text-amber-400",
      content: [
        "STR Locus Analysis Table: Compares suspect and crime scene profiles across 24 CODIS loci (D3S1358, vWA, FGA, TH01, TPOX, etc.).",
        "Likelihood Ratio (LR): Computes combined LRs reaching 10¹⁸·⁴. Values exceeding 10⁶ are classified under SWGDAM / ENFSI verbal scales as 'Conclusive Support for Identity'."
      ]
    },
    {
      id: "epigenetics-zkp",
      title: "5. Epigenetic Age Clock & Zero-Knowledge Proofs (ZKP)",
      icon: ShieldCheck,
      color: "text-rose-400",
      content: [
        "Epigenetic Age Clock: Estimates biological age at sample collection using 5-CpG methylation levels with ±2.1 years margin of error.",
        "Zero-Knowledge Proofs (ZKP - Groth16): Generates cryptographic Groth16 SNARK proofs to verify profile matches without disclosing raw genomic data outside accredited ISO 17025 labs."
      ]
    }
  ];

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100000] flex items-center justify-center p-2 sm:p-6 bg-black/85 backdrop-blur-md font-mono">
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 10 }}
          className="relative w-full max-w-4xl max-h-[92vh] flex flex-col rounded-2xl border border-cyan-500/40 bg-[#070D18] text-tactical-text shadow-[0_0_80px_rgba(6,182,212,0.2)] overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-tactical-border/80 bg-tactical-surface/60 shrink-0">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-300">
                <BookOpen className="h-5 w-5 animate-pulse" />
              </div>
              <div>
                <h2 className="text-sm sm:text-base font-extrabold uppercase text-white tracking-wider flex items-center gap-2">
                  <span>{isTr ? "FORENZA Proje Kullanım Kılavuzu" : "FORENZA SaaS Platform User Guide"}</span>
                  <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    ISO 17025
                  </span>
                </h2>
                <p className="text-[10px] text-zinc-400 mt-0.5">
                  {isTr
                    ? "Biyo-Adli DNA Veri Analizi, Fenotip Tahmini ve Likelihood Ratio (LR) Kullanım Rehberi"
                    : "Comprehensive Biocomputational Intelligence & Forensic DNA Workstation Guide"}
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer shrink-0"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Guide Body */}
          <div className="flex flex-col md:flex-row flex-1 min-h-0 overflow-hidden">
            {/* Sidebar Navigation */}
            <div className="w-full md:w-64 border-b md:border-b-0 md:border-r border-tactical-border/80 bg-black/40 p-2 sm:p-3 flex flex-row md:flex-col gap-1 overflow-x-auto md:overflow-y-auto shrink-0 scrollbar-none">
              {guideChapters.map((chap, idx) => {
                const Icon = chap.icon;
                const isActive = activeTab === idx;
                return (
                  <button
                    key={chap.id}
                    onClick={() => setActiveTab(idx)}
                    className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[10px] sm:text-xs font-bold text-left transition-all cursor-pointer shrink-0 ${
                      isActive
                        ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm"
                        : "text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
                    }`}
                  >
                    <Icon className={`w-4 h-4 shrink-0 ${chap.color}`} />
                    <span className="truncate">{chap.title}</span>
                  </button>
                );
              })}
            </div>

            {/* Chapter Content */}
            <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4 bg-[#081220]">
              <div className="flex items-center gap-2 border-b border-tactical-border/60 pb-3">
                {(() => {
                  const CurrentIcon = guideChapters[activeTab].icon;
                  return <CurrentIcon className={`w-5 h-5 ${guideChapters[activeTab].color}`} />;
                })()}
                <h3 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">
                  {guideChapters[activeTab].title}
                </h3>
              </div>

              <div className="space-y-3">
                {guideChapters[activeTab].content.map((paragraph, pIdx) => (
                  <div
                    key={pIdx}
                    className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/60 text-xs text-zinc-300 leading-relaxed font-mono flex items-start gap-2.5"
                  >
                    <div className="h-2 w-2 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
                    <p>{paragraph}</p>
                  </div>
                ))}
              </div>

              <div className="pt-3 border-t border-tactical-border/40 flex items-center justify-between text-[10px] text-zinc-500">
                <span>FORENZA Evidence OS v2.4</span>
                <span className="text-emerald-400 font-bold uppercase">SWGDAM &amp; ENFSI Compliant</span>
              </div>
            </div>
          </div>

          {/* Footer Action */}
          <div className="flex items-center justify-between p-3.5 sm:p-4 border-t border-tactical-border/80 bg-tactical-surface/60 shrink-0">
            <span className="text-[10px] text-zinc-400 font-mono hidden sm:inline">
              {isTr ? "İpucu: Üst gezinti çubuğundan dilediğiniz an TR | EN geçişi yapabilirsiniz." : "Tip: Toggle TR | EN in header to switch language instantly."}
            </span>
            <button
              onClick={onClose}
              className="ml-auto px-5 py-2 rounded-xl text-xs font-bold bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/30 transition-all cursor-pointer font-mono uppercase tracking-wider"
            >
              {isTr ? "Kılavuzu Kapat" : "Close Guide"}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
