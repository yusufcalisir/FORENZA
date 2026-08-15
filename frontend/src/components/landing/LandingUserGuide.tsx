"use client";

import { useState } from "react";
import {
  BookOpen,
  Dna,
  Eye,
  Globe,
  ShieldCheck,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Activity,
  CheckCircle2
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function LandingUserGuide() {
  const { lang } = useSaasLanguage();
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  const isTr = lang === "tr";

  const guideCards = isTr
    ? [
        {
          id: "step-1",
          title: "Adım 1: Biyo-Adli Vaka Verisi Seçimi & İçe Aktarma",
          subtitle: "Örnek vakalar (EU / AA) veya CODIS 24 STR & 55 SNP alel verilerini elle tanımlama",
          icon: Sparkles,
          color: "text-cyan-400",
          border: "border-cyan-500/30",
          bg: "bg-cyan-500/5",
          details: [
            "FORENZA sisteminde sağ üstteki 'Open DNA & SNP Terminal' butonuna basarak vaka yönetim penceresini açın.",
            "'Sample EU' (Kuzey-Batı Avrupa) veya 'Sample AA' (Batı Afrika) hazır vaka butonlarına tıklayarak 24 CODIS aleli ve 55 AIM SNP mutasyonunu tek tıkla yükleyebilirsiniz.",
            "Kendi özel numunenizi analiz etmek isterseniz STR Alel ve SNP genotip kutucuklarını doldurup 'Apply & Recalculate Profile Features' butonuna basarak tüm adli tahminleri anında güncelleyebilirsiniz."
          ]
        },
        {
          id: "step-2",
          title: "Adım 2: HIrisPlex-S ile Tahmini Fenotip (Dış Görünüş)",
          subtitle: "Göz rengi, Fitzpatrick ten fotosensitivitesi ve saç morfolojisi kestirimi",
          icon: Eye,
          color: "text-emerald-400",
          border: "border-emerald-500/30",
          bg: "bg-emerald-500/5",
          details: [
            "Göz Rengi (Eye Color): HERC2 (rs12913832) ve OCA2 lokuslarındaki genotipe göre Mavi (%94.2), Elâ (%4.6) ve Kahverengi (%1.2) çok terimli olasılık dağılımını hesaplar.",
            "Ten Tipi (Skin Phototype): SLC45A2 ve SLC24A5 delesyon analizleri ile kişinin Fitzpatrick Type I/II (Açık Ten) veya Type V/VI (Koyu Ten) olduğunu modeller.",
            "Saç Yapısı (Hair Morphology): EDAR geni genotiplemesi ile Düz Saç (%88.0), Dalgalı (%10.0) veya Kıvırcık Saç (%2.0) tespiti gerçekleştirilir."
          ]
        },
        {
          id: "step-3",
          title: "Adım 3: Atasal Soy (BGA) & Canlı Adli GIS Haritası",
          subtitle: "55-SNP AIM paneli, nüfus kümeleri ve haritada canlı coğrafi konumlandırma",
          icon: Globe,
          color: "text-purple-400",
          border: "border-purple-500/30",
          bg: "bg-purple-500/5",
          details: [
            "Biogeographic Ancestry (55-SNP AIM): Numunenin atasal kökenini %98.4 Birincil (Primary) ve %1.6 İkincil (Secondary) popülasyon referansı olarak hesaplar.",
            "Canlı Adli GIS Haritası: Numunenin tahmin edilen Latitude/Longitude koordinatlarını (ör. Berlin, Almanya 52.5200° N, 13.4050° E veya Lagos, Nijerya 6.5244° N, 3.3792° E) dinamik Leaflet ısı haritası ve kilitlenme halkaları ile haritada gösterir."
          ]
        },
        {
          id: "step-4",
          title: "Adım 4: Likelihood Ratio (LR) & Adli Kanıt Standartları",
          subtitle: "2.51 × 10¹⁸ (10¹⁸·⁴⁰) seviyesinde astronomik olabilirlik oranları ve SWGDAM / ENFSI uyumu",
          icon: Dna,
          color: "text-amber-400",
          border: "border-amber-500/30",
          bg: "bg-amber-500/5",
          details: [
            "Genişletilmiş 24-Lokus Adli STR Tablosu: 20 FBI CODIS çekirdek lokusu ile SE33, Penta D/E ve Amelogenin belirteçlerinde şüpheli ile numunenin alel uyumunu listeler.",
            "Combined Likelihood Ratio (LR): 2.51 × 10¹⁸ (10¹⁸·⁴⁰) seviyesine ulaşan adli güç sunar. SWGDAM adli standartlarına göre 10⁶ üzeri değerler 'Kesin Kimlik Tespiti' (Conclusive Support) olarak kabul edilir."
          ]
        },
        {
          id: "step-5",
          title: "Adım 5: Epigenetik Yaş Saati & Sıfır Bilgi İspatı (ZKP)",
          subtitle: "Horvath 5-CpG metilasyon yaş saati ve Groth16 ZK-SNARK kriptografik doğrulama",
          icon: ShieldCheck,
          color: "text-rose-400",
          border: "border-rose-500/30",
          bg: "bg-rose-500/5",
          details: [
            "Epigenetic Age Clock: Biyolojik numunenin bırakıldığı andaki kronolojik yaşını 5 CpG metilasyon lokusunda ±2.1 yıl sapma ile hesaplar.",
            "Zero-Knowledge Proof (ZKP): Kriptografik Circom / Groth16 ispatları üreterek ham DNA verisini laboratuvar dışına sızdırmadan eşleşmeyi kriptografik olarak doğrular."
          ]
        }
      ]
    : [
        {
          id: "step-1",
          title: "Step 1: Data Ingestion & Profile Selection",
          subtitle: "Select sample cases or load custom 24-locus STR and 55 AIM SNP profiles",
          icon: Dna,
          color: "text-cyan-400",
          border: "border-cyan-500/30",
          bg: "bg-cyan-500/5",
          details: [
            "Click the top-right 'Open DNA & SNP Terminal' button in the FORENZA workstation header to open the case management console.",
            "Load pre-configured test profiles (Sample EU: Northern European profile / Sample AA: West African profile) with one click or enter custom STR alleles & SNP genotypes.",
            "Changes immediately propagate to all 30 biocomputational modules across the workstation."
          ]
        },
        {
          id: "step-2",
          title: "Step 2: HIrisPlex-S Inferred Phenotype Predictions",
          subtitle: "Eye color, Fitzpatrick skin phototype, and hair morphology inference",
          icon: Eye,
          color: "text-emerald-400",
          border: "border-emerald-500/30",
          bg: "bg-emerald-500/5",
          details: [
            "Eye Color: HERC2 (rs12913832) genotype predicts normalized multinomial probabilities for Blue (94.2%), Hazel (4.6%), or Brown (1.2%).",
            "Skin Phototype: SLC45A2 and SLC24A5 deletion markers calculate Fitzpatrick Skin Phototype from Type I/II (Fair Skin) to Type V/VI (Dark Phototype).",
            "Hair Morphology: EDAR and FGFR1 gene variants predict Straight Hair (88.0%), Wavy (10.0%), vs Curly/Coily Hair (2.0%)."
          ]
        },
        {
          id: "step-3",
          title: "Step 3: Biogeographic Ancestry (BGA) & Live GIS Map Engine",
          subtitle: "55-SNP AIM panel, population reference clusters, and coordinate pinpointing",
          icon: Globe,
          color: "text-purple-400",
          border: "border-purple-500/30",
          bg: "bg-purple-500/5",
          details: [
            "Biogeographic Ancestry (55-SNP AIM): Classifies genetic ancestry into Primary (98.4%) and Secondary (1.6%) population reference clusters.",
            "Live GIS Forensic Map Engine: Renders heatmap probability density circles and locked coordinate centroids (Latitude/Longitude, City, Country e.g. Berlin, Germany 52.5200° N, 13.4050° E or Lagos, Nigeria 6.5244° N, 3.3792° E) on an interactive dark GIS canvas."
          ]
        },
        {
          id: "step-4",
          title: "Step 4: Likelihood Ratio (LR) & Forensic Standards",
          subtitle: "Combined LRs reaching 2.51 × 10¹⁸ (10¹⁸·⁴⁰) under SWGDAM and ENFSI evidentiary verbal scales",
          icon: Dna,
          color: "text-amber-400",
          border: "border-amber-500/30",
          bg: "bg-amber-500/5",
          details: [
            "Expanded 24-Locus Forensic Multiplex: Compares suspect and crime scene profiles across 20 FBI CODIS core loci plus SE33, Penta D, Penta E, and Amelogenin.",
            "Combined Likelihood Ratio (LR): Computes combined LRs reaching 2.51 × 10¹⁸ (10¹⁸·⁴⁰). Values exceeding 10⁶ are classified under SWGDAM / ENFSI verbal scales as 'Conclusive Support for Identity'."
          ]
        },
        {
          id: "step-5",
          title: "Step 5: Epigenetic Age Clock & Zero-Knowledge Proofs (ZKP)",
          subtitle: "Horvath 5-CpG methylation clock and Groth16 ZK-SNARK cryptographic verification",
          icon: ShieldCheck,
          color: "text-rose-400",
          border: "border-rose-500/30",
          bg: "bg-rose-500/5",
          details: [
            "Epigenetic Age Clock: Estimates biological age at sample collection using 5-CpG methylation levels with ±2.1 years margin of error.",
            "Zero-Knowledge Proofs (ZKP): Generates cryptographic Groth16 SNARK proofs to verify profile matches without disclosing raw genomic data outside accredited ISO 17025 labs."
          ]
        }
      ];

  return (
    <section id="user-guide" className="py-16 sm:py-24 border-t border-tactical-border/60 bg-[#050B14] relative overflow-hidden font-mono">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-8 relative z-10">
        {/* Section Title */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-bold text-cyan-300">
            <BookOpen className="w-3.5 h-3.5" />
            <span>{isTr ? "KAPSAMLI KULLANIM KILAVUZU" : "PLATFORM USER GUIDE & MANUAL"}</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white uppercase">
            {isTr ? "FORENZA Projesini Nasıl Kullanırsınız?" : "How to Use FORENZA Evidence OS"}
          </h2>
          <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed">
            {isTr
              ? "Biyo-adli DNA analizi, fenotip kestirimi, olabilirlik oranları (LR) ve canlı GIS haritalama modüllerini adım adım keşfedin."
              : "Step-by-step documentation for biocomputational DNA analysis, phenotype prediction, likelihood ratios, and GIS mapping."}
          </p>
        </div>

        {/* Step Cards Grid / Accordion */}
        <div className="space-y-3.5 max-w-4xl mx-auto">
          {guideCards.map((card, idx) => {
            const Icon = card.icon;
            const isOpen = openIdx === idx;
            return (
              <div
                key={card.id}
                className={`rounded-2xl border transition-all duration-300 overflow-hidden ${
                  isOpen
                    ? `${card.border} ${card.bg} shadow-lg shadow-cyan-500/5`
                    : "border-tactical-border/70 bg-black/40 hover:border-zinc-700"
                }`}
              >
                {/* Header Toggle */}
                <button
                  type="button"
                  onClick={() => setOpenIdx(isOpen ? null : idx)}
                  className="w-full p-4 sm:p-5 flex items-center justify-between gap-4 text-left cursor-pointer"
                >
                  <div className="flex items-center gap-3.5 min-w-0">
                    <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-black/60 border ${card.border} ${card.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-xs sm:text-base font-bold text-white uppercase tracking-wider truncate">
                        {card.title}
                      </h3>
                      <p className="text-[10px] sm:text-xs text-zinc-400 mt-0.5 truncate">
                        {card.subtitle}
                      </p>
                    </div>
                  </div>

                  <div className={`p-1.5 rounded-lg border border-tactical-border/60 ${card.color} shrink-0`}>
                    {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </button>

                {/* Collapsible Details */}
                {isOpen && (
                  <div className="px-4 pb-5 sm:px-5 space-y-2.5 border-t border-tactical-border/40 pt-4">
                    {card.details.map((detail, dIdx) => (
                      <div
                        key={dIdx}
                        className="p-3 rounded-xl bg-black/60 border border-tactical-border/60 text-xs text-zinc-300 leading-relaxed font-mono flex items-start gap-2.5"
                      >
                        <CheckCircle2 className={`w-4 h-4 ${card.color} shrink-0 mt-0.5`} />
                        <p>{detail}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
