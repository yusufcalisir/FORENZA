"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Leaf, MapPin, Binary, Activity, ChevronRight, Compass, ShieldCheck } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function BotanyPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeSubTab, setActiveSubTab] = useState<"species" | "habitat">("species");

  // Botany Species Match
  const speciesHits = [
    {
      species: "Pinus sylvestris (Sarıçam / Scots Pine)",
      family: "Pinaceae",
      dna_score: "99.8%",
      morph: isTr ? "ÇİFT KESELİ / RETİKÜLAT" : "BISACCATE / RETICULATE",
      verdict: isTr ? "KESİN_TÜR_TANIMLAMASI" : "CONFIRMED_SPECIES_IDENTIFICATION"
    },
    {
      species: "Quercus robur (Saplı Meşe / English Oak)",
      family: "Fagaceae",
      dna_score: "87.4%",
      morph: isTr ? "ÜÇ YARIKLI / DÜZ" : "TRICOLPATE / PSILATE",
      verdict: isTr ? "OLASI_CİNS_EŞLEŞMESİ" : "PROBABLE_GENUS_MATCH"
    },
    {
      species: "Taraxacum officinale (Karahindiba / Dandelion)",
      family: "Asteraceae",
      dna_score: "74.1%",
      morph: isTr ? "ÜÇ GÖZENEKLİ / DİKENLİ" : "TRIPORATE / ECHINATE",
      verdict: isTr ? "ORTA_AİLE_EŞLEŞMESİ" : "MODERATE_FAMILY_MATCH"
    },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
            <Leaf className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              {isTr ? "Adli Botanik & Palinoloji Merkezi" : "Forensic Botany & Palynology Hub"}
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              {isTr
                ? "Bitki DNA Barkodlama (rbcL • matK • trnL-trnF) • Polen Ekzin Morfolojisi • Coğrafi Köken Çıkarımı"
                : "Plant DNA Barcoding (rbcL • matK • trnL-trnF) • Pollen Exine Morphology • Geolocation Origin Inference"}
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("species")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "species" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {isTr ? "DNA Barkod & Tür Tanımı" : "DNA Barcoding & Species ID"}
          </button>
          <button
            onClick={() => setActiveSubTab("habitat")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "habitat" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {isTr ? "Habitat & Coğrafi Konum" : "Habitat & Geolocation"}
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: DNA Barcoding & Species ID ── */}
      {activeSubTab === "species" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Botanik Numune No" : "Botanical Specimen ID"}
              </span>
              <p className="text-base font-bold text-emerald-400 font-mono">BOT-SAMPLE-501</p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Çamur izinden elde edilen polen tanesi" : "Pollen grain recovered from mud trace"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "DNA Barkod Belirteçleri" : "DNA Barcode Markers"}
              </span>
              <p className="text-base font-bold text-tactical-text font-mono">rbcL + matK Spacer</p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "CBOL kara bitkileri barkodlama standardı" : "CBOL land plant barcoding standard"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "En İyi Tür Eşleşmesi" : "Top Species Match"}
              </span>
              <p className="text-base font-bold text-emerald-400 font-mono">Pinus sylvestris (%99.8)</p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Çift keseli polen ekzini doğrulandı" : "Bisaccate pollen exine confirmed"}
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                {isTr ? "Sıralı Botanik Tür Eşleşme Adayları" : "Ranked Botanical Species Match Candidates"}
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                {isTr ? "CBOL Referans Veritabanı Aktif" : "CBOL Reference Database Active"}
              </span>
            </div>

            <div className="space-y-3">
              {speciesHits.map((h, i) => (
                <div key={i} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-black/20 border border-tactical-border/40 gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs font-bold font-mono">
                      <span className="text-emerald-300">{h.species}</span>
                      <span className="text-zinc-600">•</span>
                      <span className="text-indigo-400">{h.family}</span>
                    </div>
                    <p className="text-[10px] text-zinc-400">
                      {isTr ? "Polen Ekzin Morfolojisi:" : "Pollen Exine Morphology:"} {h.morph}
                    </p>
                  </div>

                  <div className="flex items-center gap-4 text-xs font-mono">
                    <div className="text-right">
                      <p className="text-[9px] text-zinc-500">{isTr ? "DNA Benzerliği" : "DNA Similarity"}</p>
                      <p className="font-bold text-emerald-400">{h.dna_score}</p>
                    </div>
                    <span className="px-3 py-1 rounded text-[9px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {h.verdict.replace(/_/g, " ")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Habitat & Geolocation ── */}
      {activeSubTab === "habitat" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                {isTr ? "Dış Mekan Olay Yeri Coğrafi Köken & Ekolojik Habitat Çıkarımı" : "Outdoor Crime Scene Geographic Origin & Ecological Habitat Inference"}
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                LR_habitat = 240.00
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">
                  {isTr ? "Çıkarılan Ekolojik Habitat" : "Inferred Ecological Habitat"}
                </span>
                <p className="text-base font-bold text-emerald-400 font-mono">
                  {isTr ? "DAĞLIK_İĞNE_YAPRAKLI" : "MONTANE_CONIFEROUS"}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Baskın çam (pinus) topluluğu" : "Dominant pinus assemblage"}
                </p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">
                  {isTr ? "Coğrafi İlişkilendirme" : "Geographic Association"}
                </span>
                <p className="text-sm font-bold text-indigo-300 font-mono">
                  {isTr ? "Boreal / Subalpin İğne Yapraklı Orman" : "Boreal / Subalpine Coniferous Forest"}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Yüksek rakımlı dağlık orman zonu" : "High elevation mountain woodland zone"}
                </p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">
                  {isTr ? "Mevsimsel Çiçeklenme Penceresi" : "Seasonal Bloom Window"}
                </span>
                <p className="text-sm font-bold text-amber-300 font-mono">
                  {isTr ? "Mayıs - Temmuz (İlkbahar Sonu / Yaz Başı)" : "May - July (Late Spring / Early Summer)"}
                </p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Zirve palinolojik yayılım dönemi" : "Peak palynological dissemination"}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
