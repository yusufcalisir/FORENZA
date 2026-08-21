"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Activity, ShieldCheck, ChevronRight, Dna, GitMerge, Syringe } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function SerologyPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [activeSubTab, setActiveSubTab] = useState<"phenotype" | "fusion">("phenotype");

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 shadow-[0_0_15px_rgba(244,63,94,0.15)]">
            <Syringe className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              {isTr ? "Adli Seroloji & İkili DNA Entegrasyon Merkezi" : "Forensic Serology & Dual DNA Integration Hub"}
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              {isTr
                ? "Klasik ABO / Rh Kan Grubu Fenotiplemesi • Lewis Salgılayıcı Durumu • Çok Modlu Seroloji + DNA LR Füzyonu"
                : "Classical ABO / Rh Blood Group Phenotyping • Lewis Secretor Status • Multi-Modal Serology + DNA LR Fusion"}
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("phenotype")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "phenotype" ? "bg-rose-500/20 text-rose-300 border border-rose-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {isTr ? "ABO / Rh Fenotip & Salgılayıcı" : "ABO / Rh Phenotype & Secretor"}
          </button>
          <button
            onClick={() => setActiveSubTab("fusion")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "fusion" ? "bg-rose-500/20 text-rose-300 border border-rose-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            {isTr ? "Seroloji + DNA LR Füzyonu" : "Serology + DNA LR Fusion"}
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: ABO / Rh Phenotype & Secretor ── */}
      {activeSubTab === "phenotype" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Seroloji Numune No" : "Serology Sample ID"}
              </span>
              <p className="text-base font-bold text-rose-400 font-mono">SER-SAMPLE-701</p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Eritrosit ve çözünür antijen testi" : "Erythrocyte & soluble antigen assay"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "ABO / Rh Kan Grubu" : "ABO / Rh Blood Group"}
              </span>
              <p className="text-base font-bold text-tactical-text font-mono">
                {isTr ? "Grup A (Rh D+)" : "Group A (Rh D+)"}
              </p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "ISBT standart antijen profili" : "ISBT standard antigen profile"}
              </p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">
                {isTr ? "Lewis Salgılayıcı Durumu" : "Lewis Secretor Status"}
              </span>
              <p className="text-base font-bold text-emerald-400 font-mono">
                {isTr ? "SALGILAYICI (Le a-b+)" : "SECRETOR (Le a-b+)"}
              </p>
              <p className="text-[9px] text-zinc-400">
                {isTr ? "Vücut sıvılarında çözünür antijenler mevcut" : "Soluble antigens present in body fluids"}
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                {isTr ? "Klasik Kan Grubu Antijen Profilleri & Popülasyon Fenotip Frekansı" : "Classical Blood Group Antigen Profiles & Population Phenotype Frequency"}
              </span>
              <span className="text-[9px] text-rose-400 font-bold bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded">
                LR_serology = 3.23
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                <span className="text-[10px] text-zinc-500">
                  {isTr ? "ABO Sistemi" : "ABO System"}
                </span>
                <p className="text-sm font-bold text-rose-300">
                  {isTr ? "Grup A (%40.0)" : "Group A (40.0%)"}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                <span className="text-[10px] text-zinc-500">
                  {isTr ? "Rh D Sistemi" : "Rh D System"}
                </span>
                <p className="text-sm font-bold text-indigo-300">
                  {isTr ? "D Pozitif (%85.0)" : "D Positive (85.0%)"}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                <span className="text-[10px] text-zinc-500">
                  {isTr ? "Kell Sistemi" : "Kell System"}
                </span>
                <p className="text-sm font-bold text-emerald-300">
                  {isTr ? "K Negatif (%91.0)" : "K Negative (91.0%)"}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
                <span className="text-[10px] text-zinc-500">
                  {isTr ? "Bileşik Frekans" : "Combined Frequency"}
                </span>
                <p className="text-sm font-bold text-amber-300">f = 30.94%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Serology + DNA LR Fusion ── */}
      {activeSubTab === "fusion" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                {isTr ? "Çok Modlu İkili Seroloji + Otozomal STR Olasılık Oranı Entegrasyonu" : "Multi-Modal Dual Serology + Autosomal STR Likelihood Ratio Integration"}
              </span>
              <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">
                {isTr ? "Çarpım Kuralı Aktif" : "Product Rule Active"}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">
                  {isTr ? "Seroloji Olasılık Oranı" : "Serology Likelihood Ratio"}
                </span>
                <p className="text-base font-bold text-rose-400 font-mono">LR_serology = 3.23</p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Klasik antijen eşleşme çarpanı" : "Classical antigen match multiplier"}
                </p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">
                  {isTr ? "Otozomal STR Olasılık Oranı" : "Autosomal STR Likelihood Ratio"}
                </span>
                <p className="text-base font-bold text-indigo-400 font-mono">LR_STR = 1.00e+06</p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "24 lokuslu CODIS genetik kanıtı" : "24-locus CODIS genetic evidence"}
                </p>
              </div>

              <div className="rounded-xl border border-tactical-border/50 bg-black/20 p-4 space-y-2">
                <span className="text-zinc-500 block">
                  {isTr ? "Bileşik Çok Modlu LR" : "Combined Multi-Modal LR"}
                </span>
                <p className="text-base font-bold text-emerald-400 font-mono">3.23e+06 (log10 = 6.51)</p>
                <p className="text-[10px] text-zinc-400">
                  {isTr ? "Hp hipotezine son derece güçlü destek" : "Extremely strong support for Hp"}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
