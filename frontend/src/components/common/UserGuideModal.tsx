"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BookOpen,
  X,
  Dna,
  Eye,
  Globe,
  ShieldCheck,
  Sparkles,
  ChevronDown,
  KeyRound
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import SaaSLanguageToggle from "@/components/landing/SaaSLanguageToggle";

export default function UserGuideModal({
  isOpen,
  onClose
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const { lang } = useSaasLanguage();
  // Desktop: active tab index. Mobile: open accordion index (null = all closed except default)
  const [activeTab, setActiveTab] = useState<number>(0);
  const [mobileOpen, setMobileOpen] = useState<number>(0); // first open by default

  if (!isOpen) return null;

  const isTr = lang === "tr";

  const guideChapters = isTr ? [
    {
      id: "getting-started",
      title: "1. Hızlı Başlangıç & Vaka Yükleme",
      icon: Sparkles,
      color: "text-cyan-400",
      border: "border-cyan-500/40",
      bg: "bg-cyan-500/15",
      content: [
        "FORENZA Biyo-Adli DNA & İstatistiksel Genotipleme İstasyonu'na hoş geldiniz.",
        "Sağ üstteki 'Open DNA & SNP Terminal' butonunu kullanarak hazır vaka örneklerini (Sample EU - Kuzey Avrupa / Sample AA - Batı Afrika) tek tıkla yükleyebilirsiniz.",
        "Kendi STR alel sayılarınızı (CODIS 20/24 Loci) ve SNP mutasyonlarınızı (HIrisPlex-S / 55-SNP AIM) elle girip 'Apply & Recalculate Profile Features' butonuna tıklayarak canlı biyolojik kestirimleri anında yeniden hesaplayabilirsiniz."
      ]
    },
    {
      id: "phenotype",
      title: "2. HIrisPlex-S Fenotip Tahmin Motoru",
      icon: Eye,
      color: "text-emerald-400",
      border: "border-emerald-500/40",
      bg: "bg-emerald-500/15",
      content: [
        "Tahmini Fenotip paneli, DNA numunesinden kişinin dış görünüşünü yüksek olasılıkla hesaplar.",
        "Göz Rengi: HERC2 (rs12913832) ve OCA2 genlerindeki polimorfizmlere göre Mavi (%94.2), Elâ (%78.4) veya Koyu Kahverengi (%98.6) olasılıklarını verir.",
        "Ten Tipi: SLC45A2 ve SLC24A5 delesyonları incelenerek Fitzpatrick I/II (Açık Ten) ile V/VI (Esmer/Koyu Ten) aralığında derecelendirilir.",
        "Saç Yapısı: EDAR ve FGFR1 geni aracılığıyla Düz Saç (%88) veya Kıvırcık/Bukleli Saç (%94) tespiti yapılır."
      ]
    },
    {
      id: "ancestry-gis",
      title: "3. Atasal Soy (BGA) & Canlı GIS Harita",
      icon: Globe,
      color: "text-purple-400",
      border: "border-purple-500/40",
      bg: "bg-purple-500/15",
      content: [
        "Biogeographic Ancestry (55-SNP AIM) Paneli: Numunenin biyocoğrafi kökenini %98.4 Birincil ve %1.6 İkincil atasal küme olarak sınıflandırır.",
        "Canlı Adli GIS Haritası: Numunenin muhtemel koordinatlarını (Enlem/Boylam), şehir ve ülkeyi ısı haritası ve hedef halkaları ile görselleştirir.",
        "Örnek: Berlin, Almanya (52.5200° N, 13.4050° E) veya Lagos, Nijerya (6.5244° N, 3.3792° E)."
      ]
    },
    {
      id: "str-lr",
      title: "4. STR Alel Eşleşmesi & Likelihood Ratio",
      icon: Dna,
      color: "text-amber-400",
      border: "border-amber-500/40",
      bg: "bg-amber-500/15",
      content: [
        "STR Locus Analysis Tablosu: D3S1358, vWA, FGA, TH01, TPOX vb. 24 CODIS lokusundaki şüpheli numune ile olay yeri numunesinin alel eşleşmelerini karşılaştırır.",
        "Likelihood Ratio (LR): 10¹⁸·⁴ seviyesinde adli güç hesaplar. SWGDAM ve ENFSI standartlarına göre 10⁶ üzeri değerler 'Kesin Kimlik Tespiti' kabul edilir."
      ]
    },
    {
      id: "epigenetics-zkp",
      title: "5. Epigenetik Yaş & Sıfır Bilgi İspatı",
      icon: ShieldCheck,
      color: "text-rose-400",
      border: "border-rose-500/40",
      bg: "bg-rose-500/15",
      content: [
        "Epigenetic Age Clock: Biyolojik numunenin bırakıldığı andaki kronolojik yaşını 5 CpG metilasyon lokusunda ±2.1 yıl sapma payı ile hesaplar.",
        "Zero-Knowledge Proof (Circom/Groth16): Kriptografik ZK-SNARK ispatları üreterek ham DNA dizilimlerini laboratuvar dışına aktarmadan kimlik doğrulama yapılmasını sağlar."
      ]
    },
    {
      id: "byo-key-mode",
      title: "6. Çift Motorlu Mimari & Kendi API Anahtarını Getir (BYO-Key)",
      icon: KeyRound,
      color: "text-purple-400",
      border: "border-purple-500/40",
      bg: "bg-purple-500/15",
      content: [
        "Demo Simülasyon Modu: Ücretsiz, anında çalışan ve yüksek gerçeklikteki biyo-hesaplamalı model motorudur.",
        "Canlı Üretim Modu (BYO-Key): Header'daki 'DEMO SİMÜLASYON MODU' rozetine tıklayarak kendi Google Gemini, OpenAI, Groq, NCBI veya FastAPI backend uç noktalarınızı tanımlayabilirsiniz.",
        "Sıfır Veri Sızıntısı: Girdiğiniz API anahtarları yalnızca tarayıcınızın yerel depolamasında (localStorage) saklanır ve doğrudan ilgili AI sunucusuna iletilir."
      ]
    }
  ] : [
    {
      id: "getting-started",
      title: "1. Quick Start & Case Loading",
      icon: Sparkles,
      color: "text-cyan-400",
      border: "border-cyan-500/40",
      bg: "bg-cyan-500/15",
      content: [
        "Welcome to the FORENZA Biocomputational DNA & Statistical Genotyping Workstation.",
        "Click the top-right 'Open DNA & SNP Terminal' button to load pre-configured sample cases (Sample EU - Northern European / Sample AA - West African) with one click.",
        "Manually adjust STR allele values (CODIS 20/24 Loci) and SNP markers (HIrisPlex-S / 55-SNP AIM), then click 'Apply & Recalculate Profile Features' to run live predictions."
      ]
    },
    {
      id: "phenotype",
      title: "2. HIrisPlex-S Phenotype Engine",
      icon: Eye,
      color: "text-emerald-400",
      border: "border-emerald-500/40",
      bg: "bg-emerald-500/15",
      content: [
        "The Inferred Phenotype panel predicts physical appearance features directly from DNA markers with high statistical confidence.",
        "Eye Color: HERC2 (rs12913832) and OCA2 polymorphisms calculate posterior probabilities for Blue (94.2%), Hazel (78.4%), or Dark Brown (98.6%).",
        "Skin Phototype: SLC45A2 and SLC24A5 variants determine Fitzpatrick Skin Type from I/II (Fair) to V/VI (Dark).",
        "Hair Morphology: EDAR and FGFR1 genes predict Straight Hair (88%) vs Curly/Coily Hair (94%)."
      ]
    },
    {
      id: "ancestry-gis",
      title: "3. Ancestry (BGA) & Live GIS Map",
      icon: Globe,
      color: "text-purple-400",
      border: "border-purple-500/40",
      bg: "bg-purple-500/15",
      content: [
        "Biogeographic Ancestry (55-SNP AIM) Panel: Classifies genetic ancestry into Primary (98.4%) and Secondary (1.6%) population reference clusters.",
        "Live GIS Forensic Map Engine: Renders heatmap probability density circles and coordinate centroids on an interactive dark GIS canvas.",
        "Examples: Berlin, Germany (52.5200° N, 13.4050° E) or Lagos, Nigeria (6.5244° N, 3.3792° E)."
      ]
    },
    {
      id: "str-lr",
      title: "4. STR Allele Matching & Likelihood Ratio",
      icon: Dna,
      color: "text-amber-400",
      border: "border-amber-500/40",
      bg: "bg-amber-500/15",
      content: [
        "STR Locus Analysis Table: Compares suspect and crime scene profiles across 24 CODIS loci (D3S1358, vWA, FGA, TH01, TPOX, etc.).",
        "Likelihood Ratio (LR): Computes combined LRs reaching 10¹⁸·⁴. Values exceeding 10⁶ are classified as 'Conclusive Support for Identity' under SWGDAM / ENFSI standards."
      ]
    },
    {
      id: "epigenetics-zkp",
      title: "5. Epigenetic Age Clock & ZKP",
      icon: ShieldCheck,
      color: "text-rose-400",
      border: "border-rose-500/40",
      bg: "bg-rose-500/15",
      content: [
        "Epigenetic Age Clock: Estimates biological age at sample collection using 5-CpG methylation levels with ±2.1 years margin of error.",
        "Zero-Knowledge Proofs (Groth16): Generates cryptographic SNARK proofs to verify profile matches without disclosing raw genomic data outside accredited ISO 17025 labs."
      ]
    },
    {
      id: "byo-key-mode",
      title: "6. Dual-Engine Architecture & BYO-API Key Setup",
      icon: KeyRound,
      color: "text-purple-400",
      border: "border-purple-500/40",
      bg: "bg-purple-500/15",
      content: [
        "Demo Simulation Mode: Free, instant, high-fidelity out-of-the-box biocomputational model engine.",
        "Live Production Mode (BYO-Key): Click the '[DEMO SIMULATION]' badge in the header to enter custom Google Gemini, OpenAI, Groq, NCBI, or FastAPI backend endpoints.",
        "Zero Data Leakage: All entered API keys reside exclusively in your browser's local storage and are transmitted directly to destination AI models."
      ]
    }
  ];

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100000] flex items-center justify-center p-2 sm:p-6 bg-black/85 backdrop-blur-md font-mono overflow-hidden">
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 10 }}
          className="relative w-full max-w-4xl max-h-[92vh] flex flex-col rounded-2xl border border-cyan-500/40 bg-[#070D18] text-tactical-text shadow-[0_0_80px_rgba(6,182,212,0.2)] overflow-hidden"
        >
          {/* ── Header ── */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-tactical-border/80 bg-tactical-surface/60 shrink-0 gap-2">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-300">
                <BookOpen className="h-4 w-4" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <h2 className="text-xs sm:text-sm font-extrabold uppercase text-white tracking-wider font-mono leading-tight">
                    {isTr ? "FORENZA Kullanım Kılavuzu" : "FORENZA Platform User Guide"}
                  </h2>
                  <span className="px-1.5 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shrink-0">
                    ISO 17025
                  </span>
                </div>
                <p className="text-[9px] text-zinc-500 mt-0.5 leading-tight hidden sm:block">
                  {isTr
                    ? "Biyo-Adli DNA Analizi, Fenotip Tahmini ve Likelihood Ratio Rehberi"
                    : "Biocomputational DNA Analysis, Phenotype Prediction & Likelihood Ratio Guide"}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <SaaSLanguageToggle />
              <button
                onClick={onClose}
                className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* ── Body ── */}
          <div className="flex-1 overflow-hidden flex flex-col md:flex-row min-h-0">

            {/* ── MOBILE: Full Vertical Accordion ── */}
            <div className="md:hidden flex-1 overflow-y-auto p-3 space-y-2">
              {guideChapters.map((chap, idx) => {
                const Icon = chap.icon;
                const isOpen = mobileOpen === idx;
                return (
                  <div
                    key={chap.id}
                    className={`rounded-xl border overflow-hidden transition-all duration-200 ${
                      isOpen ? `${chap.border} ${chap.bg}` : "border-tactical-border/60 bg-black/40"
                    }`}
                  >
                    {/* Accordion Header */}
                    <button
                      type="button"
                      onClick={() => setMobileOpen(isOpen ? -1 : idx)}
                      className="w-full flex items-center justify-between gap-3 px-4 py-3.5 text-left cursor-pointer"
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <Icon className={`w-4 h-4 shrink-0 ${chap.color}`} />
                        <span className={`text-xs font-bold font-mono ${isOpen ? "text-white" : "text-zinc-300"}`}>
                          {chap.title}
                        </span>
                      </div>
                      <ChevronDown className={`w-4 h-4 shrink-0 transition-transform duration-200 ${isOpen ? `rotate-180 ${chap.color}` : "text-zinc-500"}`} />
                    </button>

                    {/* Accordion Body */}
                    {isOpen && (
                      <div className="px-4 pb-4 space-y-2 border-t border-tactical-border/40 pt-3">
                        {chap.content.map((paragraph, pIdx) => (
                          <div key={pIdx} className="flex items-start gap-2.5 text-xs text-zinc-300 leading-relaxed">
                            <div className={`h-1.5 w-1.5 rounded-full mt-1.5 shrink-0 bg-current ${chap.color}`} />
                            <p>{paragraph}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}

              <div className="pt-1 pb-2 flex items-center justify-between text-[9px] text-zinc-600">
                <span>FORENZA Evidence OS v2.4</span>
                <span className="text-emerald-500 font-bold uppercase">
                  {isTr ? "SWGDAM & ENFSI Uyumlu" : "SWGDAM & ENFSI Compliant"}
                </span>
              </div>
            </div>

            {/* ── DESKTOP: Sidebar + Content ── */}
            <div className="hidden md:flex flex-row flex-1 min-h-0 overflow-hidden">
              {/* Sidebar */}
              <div className="w-72 border-r border-tactical-border/80 bg-black/40 p-3 flex flex-col gap-1.5 overflow-y-auto shrink-0">
                {guideChapters.map((chap, idx) => {
                  const Icon = chap.icon;
                  const isActive = activeTab === idx;
                  return (
                    <button
                      key={chap.id}
                      onClick={() => setActiveTab(idx)}
                      className={`flex items-center gap-2.5 px-3 py-3 rounded-xl text-left transition-all cursor-pointer w-full border ${
                        isActive
                          ? `${chap.bg} ${chap.border} text-white shadow-sm`
                          : "border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
                      }`}
                    >
                      <Icon className={`w-4 h-4 shrink-0 ${chap.color}`} />
                      <span className="font-mono text-xs font-bold leading-snug">{chap.title}</span>
                    </button>
                  );
                })}
              </div>

              {/* Chapter Content */}
              <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-[#081220]">
                <div className="flex items-center gap-2.5 border-b border-tactical-border/60 pb-3">
                  {(() => {
                    const CurrentIcon = guideChapters[activeTab].icon;
                    return <CurrentIcon className={`w-5 h-5 shrink-0 ${guideChapters[activeTab].color}`} />;
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
                      <div className={`h-2 w-2 rounded-full mt-1.5 shrink-0 bg-current ${guideChapters[activeTab].color}`} />
                      <p>{paragraph}</p>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-tactical-border/40 flex items-center justify-between text-[10px] text-zinc-500 font-mono">
                  <span>FORENZA Evidence OS v2.4</span>
                  <span className="text-emerald-400 font-bold uppercase">
                    {isTr ? "SWGDAM & ENFSI UYUMLU" : "SWGDAM & ENFSI COMPLIANT"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* ── Footer ── */}
          <div className="flex items-center justify-end px-4 py-3 border-t border-tactical-border/80 bg-tactical-surface/60 shrink-0">
            <button
              onClick={onClose}
              className="px-5 py-2 rounded-xl text-xs font-bold bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/30 transition-all cursor-pointer font-mono uppercase tracking-wider"
            >
              {isTr ? "Kılavuzu Kapat" : "Close Guide"}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
