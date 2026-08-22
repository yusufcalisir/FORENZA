"use client";

import React, { use } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
  BookOpen,
  Cpu,
  Sliders,
} from "lucide-react";
import {
  SUBSYSTEM_CATEGORIES,
  COLOR_CLASSES,
  MATURITY_CONFIG,
  getSubsystemCategory,
  getMaturityConfig,
  CategoryId,
} from "@/config/subsystems";
import { useIngestStore } from "@/store/ingestStore";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function CategoryPage({
  params,
}: {
  params: Promise<{ category: string }>;
}) {
  const resolvedParams = use(params);
  const categoryId = resolvedParams.category as CategoryId;
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";
  const category = getSubsystemCategory(categoryId, lang) || SUBSYSTEM_CATEGORIES[0];
  const maturityConfig = getMaturityConfig(lang);
  const { setInspectorOpen } = useIngestStore();

  const CatIcon = category.icon;
  const cc = COLOR_CLASSES[category.color] || COLOR_CLASSES.cyan;

  return (
    <div className="space-y-6 font-mono max-w-full overflow-hidden">
      {/* ── Suite Header & Breadcrumb (NO global map banner) ── */}
      <div className="rounded-2xl border border-tactical-border/80 bg-[#070D18] p-4 sm:p-6 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/60 pb-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className={`p-3 rounded-2xl border ${cc.border} ${cc.bg} shrink-0`}>
              <CatIcon className={`w-6 h-6 ${cc.text}`} />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <Link
                  href="/analysis"
                  className="text-[10px] text-zinc-400 hover:text-cyan-300 transition-colors flex items-center gap-1 font-bold uppercase"
                >
                  <ArrowLeft className="w-3 h-3" /> {isTr ? "İstasyon Merkezi" : "Workstation Hub"}
                </Link>
                <span className="text-zinc-600">/</span>
                <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest">
                  {isTr ? `Süit ${category.pillarNumber}` : `Pillar ${category.pillarNumber}`}
                </span>
              </div>
              <h1 className="text-base sm:text-xl font-extrabold text-white tracking-tight mt-0.5">
                {category.label}
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap shrink-0">
            <span className="text-[9px] font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 px-3 py-1.5 rounded-xl uppercase">
              {isTr ? "5 Kalibre Modül" : "5 Calibrated Modules"}
            </span>
          </div>
        </div>

        <p className="text-xs text-zinc-300 leading-relaxed font-mono">
          {category.description}
        </p>

        <div className="flex items-center gap-2 text-[9px] text-emerald-400/90 font-mono pt-1">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span>
            {isTr
              ? "ISO/IEC 17025 • ENFSI 2017 • NIST Standardı ile Doğrulanmış Motor"
              : "ISO/IEC 17025 • ENFSI 2017 • NIST Validated Engine"}
          </span>
        </div>
      </div>

      {/* ── Grid of 5 Module Cards (Kart kart görünüm) ── */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-zinc-400">
            {isTr ? "Bu Süitteki Mevcut Modüller" : "Available Modules in this Suite"}
          </span>
          <span className="text-[9px] text-zinc-500">
            {isTr ? "Özel çalışma alanını başlatmak için tıklayın" : "Click to launch dedicated viewport"}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {category.tabs.map((tab) => {
            const TabIcon = tab.icon;
            const mat = maturityConfig[tab.maturity];

            return (
              <motion.div
                key={tab.id}
                whileHover={{ y: -2 }}
                className="rounded-2xl border border-tactical-border/70 bg-[#0A0F1E] p-4 sm:p-5 flex flex-col justify-between space-y-4 hover:border-cyan-500/40 transition-all shadow-md group"
              >
                <div className="space-y-3">
                  {/* Module Header */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="p-2 rounded-xl bg-black/60 border border-tactical-border/60 shrink-0 group-hover:border-cyan-500/40">
                        <TabIcon className="w-4 h-4 text-cyan-400" />
                      </div>
                      <div className="min-w-0">
                        <span className="text-[8px] font-bold text-zinc-500 uppercase tracking-widest block">
                          {isTr ? "Modül" : "Module"} {tab.badge}
                        </span>
                        <h3 className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors truncate">
                          {tab.label}
                        </h3>
                      </div>
                    </div>

                    <span
                      className={`text-[7px] font-bold px-1.5 py-0.5 rounded border shrink-0 ${mat.tagBg} ${mat.tagText} ${mat.tagBorder}`}
                    >
                      {mat.shortLabel}
                    </span>
                  </div>

                  {/* Method & Standard */}
                  <div className="space-y-1.5 text-[9px] bg-black/40 p-2.5 rounded-xl border border-tactical-border/40 font-mono">
                    <div>
                      <span className="text-zinc-500 font-bold uppercase block text-[8px]">
                        {isTr ? "Algoritma / Model:" : "Algorithm / Model:"}
                      </span>
                      <span className="text-cyan-300 font-semibold">{tab.method}</span>
                    </div>
                    {tab.standard && (
                      <div className="pt-1 border-t border-tactical-border/30 flex items-center gap-1 text-zinc-400">
                        <ShieldCheck className="w-2.5 h-2.5 text-emerald-400 shrink-0" />
                        <span className="truncate">{tab.standard}</span>
                      </div>
                    )}
                  </div>

                  {/* Research Excerpt */}
                  <p className="text-[9px] text-zinc-400 leading-relaxed line-clamp-2">
                    {tab.maturityNote}
                  </p>
                </div>

                {/* Launch Button */}
                <Link
                  href={`/analysis/${category.id}/${tab.id}`}
                  className="w-full py-2 bg-gradient-to-r from-zinc-800 to-zinc-800/80 hover:from-cyan-500/20 hover:to-teal-500/20 text-zinc-200 hover:text-cyan-300 border border-zinc-700/60 hover:border-cyan-500/40 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer shadow-sm"
                >
                  <span>{isTr ? "Modül Görünümünü Başlat" : "Launch Module Viewport"}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
