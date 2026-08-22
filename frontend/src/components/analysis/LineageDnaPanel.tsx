"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Dna, ShieldCheck, GitCommit, Compass, RefreshCw, CheckCircle2, ChevronRight, Binary } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import PanelYSTR from "./PanelYSTR";

export default function LineageDnaPanel({
  initialTab = "ystr",
}: {
  initialTab?: "ystr" | "xstr" | "mtdna";
}) {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";
  const [selectedTab, setSelectedTab] = useState<"ystr" | "xstr" | "mtdna">(initialTab);

  useEffect(() => {
    if (initialTab) {
      setSelectedTab(initialTab);
    }
  }, [initialTab]);

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.15)]">
            <Dna className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <h2 className="text-xs sm:text-base font-bold tracking-widest text-tactical-text uppercase truncate">
              {isTr
                ? "Soybağı DNA Analiz Merkezi (Y-STR • X-STR • mtDNA)"
                : "Lineage DNA Analysis Hub (Y-STR • X-STR • mtDNA)"}
            </h2>
            <p className="text-[9px] sm:text-[10px] text-tactical-text-muted mt-0.5 truncate">
              {isTr
                ? "Baba Soyu Haplotip Takibi • Karmaşık X Akrabalığı • Anne Soyu rCRS Dizi Hizalaması"
                : "Paternal Haplotype Tracking • Complex X Kinship • Maternal rCRS Sequence Alignment"}
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex flex-wrap sm:flex-nowrap items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60 shrink-0">
          <button
            onClick={() => setSelectedTab("ystr")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all whitespace-nowrap cursor-pointer ${
              selectedTab === "ystr" ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 shadow-sm" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {isTr ? "Y-STR Baba Soyu" : "Y-STR Paternal"}
          </button>
          <button
            onClick={() => setSelectedTab("xstr")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all whitespace-nowrap cursor-pointer ${
              selectedTab === "xstr" ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 shadow-sm" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {isTr ? "X-STR Akrabalık" : "X-STR Kinship"}
          </button>
          <button
            onClick={() => setSelectedTab("mtdna")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all whitespace-nowrap cursor-pointer ${
              selectedTab === "mtdna" ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 shadow-sm" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {isTr ? "mtDNA Anne Soyu" : "mtDNA Maternal"}
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: Y-STR Paternal Haplotype ── */}
      {selectedTab === "ystr" && <PanelYSTR />}

      {/* ── Sub-tab 2: X-STR Kinship ── */}
      {selectedTab === "xstr" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Akrabalık Hipotezi" : "Relationship Hypothesis"}
              </span>
              <p className="text-sm font-bold text-indigo-300">
                {isTr ? "Baba Bir Üvey Kız Kardeşler (PHS)" : "Paternal Half-Sisters (PHS)"}
              </p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Rekombinasyonsuz paylaşılan baba X kromozomu" : "Shared paternal X without recombination"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Birleşik X-Akrabalık İndeksi" : "Combined X-Kinship Index"}
              </span>
              <p className="text-base sm:text-lg font-bold text-emerald-400 font-mono">KI_X = 1.854 × 10⁵</p>
              <p className="text-[9px] text-zinc-400">log₁₀(KI_X) = 5.268 ({isTr ? "ISFG Standardı" : "ISFG Standard"})</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Değerlendirilen Kümeler" : "Evaluated Clusters"}
              </span>
              <p className="text-base sm:text-lg font-bold text-cyan-400 font-mono">
                {isTr ? "4 / 4 Bağlantı Grubu" : "4 / 4 Linkage Groups"}
              </p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "12 Argus X-12 Lokusu Değerlendirildi" : "12 Argus X-12 Loci Evaluated"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "ENFSI Sözel Ölçeği" : "ENFSI Verbal Scale"}
              </span>
              <p className="text-sm font-bold text-emerald-400">
                {isTr ? "Son Derece Güçlü Destek" : "Extremely Strong Support"}
              </p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Ortak baba soyu lehine" : "For common paternal ancestry"}
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 space-y-4 shadow-lg overflow-hidden">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 sm:gap-4 border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider leading-snug">
                {isTr
                  ? "Investigator Argus X-12 Bağlantı Kümeleri & Grup İçi Rekombinasyon (r)"
                  : "Investigator Argus X-12 Linkage Clusters & Intra-Group Recombination (r)"}
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded shrink-0 whitespace-nowrap self-start sm:self-auto">
                {isTr ? "Kosambi Harita Düzeltmeli" : "Kosambi Map Corrected"}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              {[
                {
                  group: isTr ? "Bağlantı Grubu 1 (LG1 — Xp22.2)" : "Linkage Group 1 (LG1 — Xp22.2)",
                  loci: "DXS10148 (12.42 Mb) • DXS10135 (13.15 Mb) • DXS8378 (14.90 Mb)",
                  recomb: "r₁₋₂ = 0.003, r₂₋₃ = 0.022",
                  ki: "KI_LG1 = 20.75",
                  status: isTr ? "Baba X Paylaşıldı" : "Paternal X Shared",
                },
                {
                  group: isTr ? "Bağlantı Grubu 2 (LG2 — Xq12)" : "Linkage Group 2 (LG2 — Xq12)",
                  loci: "DXS7132 (68.10 Mb) • DXS10074 (70.80 Mb) • DXS10079 (71.35 Mb)",
                  recomb: "r₁₋₂ = 0.015, r₂₋₃ = 0.020",
                  ki: "KI_LG2 = 20.75",
                  status: isTr ? "Baba X Paylaşıldı" : "Paternal X Shared",
                },
                {
                  group: isTr ? "Bağlantı Grubu 3 (LG3 — Xq26)" : "Linkage Group 3 (LG3 — Xq26)",
                  loci: "DXS10103 (133.50 Mb) • HPRTB (133.90 Mb) • DXS10101 (134.60 Mb)",
                  recomb: "r₁₋₂ = 0.001, r₂₋₃ = 0.012",
                  ki: "KI_LG3 = 20.75",
                  status: isTr ? "Baba X Paylaşıldı" : "Paternal X Shared",
                },
                {
                  group: isTr ? "Bağlantı Grubu 4 (LG4 — Xq28)" : "Linkage Group 4 (LG4 — Xq28)",
                  loci: "DXS10146 (148.20 Mb) • DXS10134 (149.10 Mb) • DXS7423 (150.05 Mb)",
                  recomb: "r₁₋₂ = 0.005, r₂₋₃ = 0.008",
                  ki: "KI_LG4 = 20.75",
                  status: isTr ? "Baba X Paylaşıldı" : "Paternal X Shared",
                },
              ].map((item) => (
                <div key={item.group} className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-indigo-300 text-xs truncate">{item.group}</span>
                    <span className="text-emerald-400 font-mono shrink-0 ml-2">{item.ki}</span>
                  </div>
                  <p className="text-[10px] text-zinc-400">{item.loci}</p>
                  <div className="flex flex-wrap justify-between items-center text-[9px] gap-1 pt-1">
                    <span className="text-cyan-400 font-mono">{item.recomb}</span>
                    <span className="text-emerald-400 font-semibold">{item.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 3: mtDNA Sequence ── */}
      {selectedTab === "mtdna" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Anne Soyu Kararı" : "Maternal Lineage Verdict"}
              </span>
              <p className="text-sm font-bold text-emerald-400">
                {isTr ? "Dışlanamaz (Eşleşme)" : "Cannot Be Excluded"}
              </p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "HV1/HV2/HV3 genelinde 0 fark" : "0 differences across HV1/HV2/HV3"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "EMPOP Frekans Üst Sınırı" : "EMPOP Frequency Bound"}
              </span>
              <p className="text-base sm:text-lg font-bold text-cyan-400 font-mono">p̂_upper = 6.18 × 10⁻⁵</p>
              <p className="text-[9px] text-zinc-400">N = 48,500 ({isTr ? "k = 0 gözlenmedi" : "k = 0 unobserved"})</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Anne Soyu Olabilirlik Oranı" : "Maternal Likelihood Ratio"}
              </span>
              <p className="text-base sm:text-lg font-bold text-emerald-400 font-mono">LR = 16,191.7</p>
              <p className="text-[9px] text-zinc-400">log₁₀(LR_mtDNA) = 4.209</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Haplogrup Sınıflandırması" : "Haplogroup Classification"}
              </span>
              <p className="text-sm font-bold text-indigo-300">Phylotree H1a</p>
              <p className="text-[9px] text-zinc-400">rCRS (NC_012920.1) {isTr ? "hizalandı" : "aligned"}</p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 space-y-4 shadow-lg overflow-hidden">
            {/* Header Block */}
            <div className="flex flex-col gap-2.5 sm:gap-3 border-b border-tactical-border/40 pb-3.5">
              <span className="text-xs sm:text-sm font-bold text-tactical-text uppercase tracking-wider leading-snug">
                {isTr
                  ? "rCRS Referansına Göre Mitokondriyal Dizi Farkları (ISFG 3'-Sağa Hizalı)"
                  : "Mitochondrial Sequence Differences vs. rCRS Reference (ISFG 3' Right-Aligned)"}
              </span>
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-[9px] sm:text-[10px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-lg whitespace-nowrap">
                  {isTr ? "ISFG Sağa Hizalı" : "ISFG Right-Aligned"}
                </span>
                <span className="text-[9px] sm:text-[10px] text-cyan-400 font-bold bg-cyan-500/10 border border-cyan-500/20 px-2.5 py-1 rounded-lg whitespace-nowrap">
                  {isTr ? "0 Fark (Anne Soyu Eşleşmesi)" : "0 Differences (Maternal Match)"}
                </span>
              </div>
            </div>

            {/* Sequence Differences Card List */}
            <div className="space-y-2.5">
              {[
                { pos: 73, ref: "A", alt: "G", region: "HV2", empop: "73G", note: isTr ? "Geçiş (Tr)" : "Transition" },
                { pos: 263, ref: "A", alt: "G", region: "HV2", empop: "263G", note: isTr ? "Geçiş (Tr)" : "Transition" },
                { pos: 309.1, ref: "-", alt: "C", region: "HV2", empop: "309.1C", note: isTr ? "ISFG Poli-C İnsersiyonu" : "ISFG Poly-C Insertion" },
                { pos: 315.1, ref: "-", alt: "C", region: "HV2", empop: "315.1C", note: isTr ? "ISFG Poli-C İnsersiyonu" : "ISFG Poly-C Insertion" },
                { pos: 522, ref: "CA", alt: "del", region: "HV3", empop: "522del", note: isTr ? "Dinükleotid Delesyonu" : "Dinucleotide Deletion" },
                { pos: 16189, ref: "T", alt: "Y (C/T)", region: "HV1", empop: "16189Y", note: isTr ? "IUPAC Nokta Heteroplazmisi" : "IUPAC Point Heteroplasmy" },
                { pos: 16223, ref: "C", alt: "T", region: "HV1", empop: "16223T", note: isTr ? "Geçiş (Tr)" : "Transition" },
              ].map((v) => (
                <div
                  key={v.empop}
                  className="p-3 rounded-xl bg-black/30 border border-tactical-border/40 hover:border-indigo-500/40 transition-all space-y-2"
                >
                  {/* Primary Row: EMPOP code, region/position, and Ref -> Alt transition */}
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 sm:gap-3 min-w-0">
                      <span className="text-xs sm:text-sm font-bold text-cyan-400 font-mono shrink-0">
                        {v.empop}
                      </span>
                      <span className="text-[10px] sm:text-xs text-zinc-400 font-mono truncate">
                        [{v.region}] {isTr ? `Poz ${v.pos}` : `Pos ${v.pos}`}
                      </span>
                    </div>

                    {/* Transition Pill */}
                    <div className="flex items-center gap-1.5 text-xs font-bold font-mono px-2.5 py-0.5 rounded-lg bg-black/50 border border-tactical-border/50 shrink-0">
                      <span className="text-zinc-400">{v.ref}</span>
                      <ChevronRight className="w-3 h-3 text-zinc-600" />
                      <span className="text-cyan-300 font-bold">{v.alt}</span>
                    </div>
                  </div>

                  {/* Secondary Row: Mutation Classification Badge */}
                  <div className="flex items-center justify-between text-[9px] pt-1.5 border-t border-tactical-border/20">
                    <span className="text-zinc-500 font-mono">{isTr ? "Mutasyon Sınıfı" : "Mutation Class"}</span>
                    <span className="text-[9px] text-indigo-300 font-semibold bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded whitespace-nowrap">
                      {v.note}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
