"use client";

import React, { use } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import {
  SUBSYSTEM_CATEGORIES,
  COLOR_CLASSES,
  getSubsystemCategory,
  getMaturityConfig,
  CategoryId,
} from "@/config/subsystems";
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

  const CatIcon = category.icon;
  const cc = COLOR_CLASSES[category.color] || COLOR_CLASSES.cyan;

  return (
    <div className="space-y-6 font-mono max-w-full overflow-hidden">
      {/* ── Suite Header & Breadcrumb ── */}
      <div className={`rounded-2xl border ${cc.border} bg-gradient-to-b from-white/[0.04] to-transparent bg-[#070D18] p-4 sm:p-6 space-y-4 shadow-xl`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/60 pb-4 min-w-0">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div className={`p-3 rounded-2xl border ${cc.border} ${cc.bg} shrink-0 shadow-sm`}>
              <CatIcon className={`w-6 h-6 ${cc.text}`} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap min-w-0">
                <Link
                  href="/analysis"
                  className="min-h-[32px] px-2.5 py-1 rounded-lg bg-black/40 border border-tactical-border/60 text-[10px] text-zinc-300 hover:text-white hover:border-cyan-500/40 transition-all flex items-center gap-1 font-bold uppercase shrink-0"
                >
                  <ArrowLeft className="w-3 h-3" /> {isTr ? "İstasyon Merkezi" : "Workstation Hub"}
                </Link>
                <span className="text-zinc-600">/</span>
                <span className={`text-[10px] ${cc.text} font-bold uppercase tracking-widest truncate`}>
                  {isTr ? `Süit ${category.pillarNumber}` : `Pillar ${category.pillarNumber}`}
                </span>
              </div>
              <h1 className="text-base sm:text-xl font-extrabold text-white tracking-tight mt-1 truncate">
                {category.label}
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap shrink-0">
            <span className={`text-[9px] font-bold ${cc.text} ${cc.bg} border ${cc.border} px-3 py-1.5 rounded-xl uppercase whitespace-nowrap shadow-sm`}>
              {isTr ? "5 Kalibre Modül" : "5 Calibrated Modules"}
            </span>
          </div>
        </div>

        <p className="text-xs text-zinc-300 leading-relaxed font-sans">
          {category.description}
        </p>

        <div className="flex items-center gap-2 text-[9px] text-emerald-400 font-mono pt-1 font-semibold">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span>
            {isTr
              ? "ISO/IEC 17025 • ENFSI 2017 • NIST Standardı ile Doğrulanmış Motor"
              : "ISO/IEC 17025 • ENFSI 2017 • NIST Validated Engine"}
          </span>
        </div>
      </div>

      {/* ── Grid of 5 Module Cards ── */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 px-1">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-zinc-300">
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
                className={`rounded-2xl border ${cc.border} bg-gradient-to-b from-white/[0.04] to-transparent bg-[#080D1A] p-4 sm:p-5 flex flex-col justify-between space-y-4 hover:shadow-xl hover:${cc.glow} transition-all duration-200 group min-w-0 shadow-md`}
              >
                <div className="space-y-3 min-w-0">
                  {/* Module Header */}
                  <div className="flex items-start justify-between gap-2 min-w-0">
                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                      <div className={`p-2 rounded-xl ${cc.bg} border ${cc.border} shrink-0 group-hover:scale-105 transition-transform`}>
                        <TabIcon className={`w-4 h-4 ${cc.text}`} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <span className={`text-[8px] font-bold ${cc.text} uppercase tracking-widest block`}>
                          {isTr ? "Modül" : "Module"} {tab.badge}
                        </span>
                        <h3 className="text-xs sm:text-sm font-bold text-white group-hover:text-white transition-colors break-words">
                          {tab.label}
                        </h3>
                      </div>
                    </div>

                    <span
                      className={`text-[7px] font-bold px-2 py-0.5 rounded-full border shrink-0 whitespace-nowrap ${mat.tagBg} ${mat.tagText} ${mat.tagBorder}`}
                    >
                      {mat.shortLabel}
                    </span>
                  </div>

                  {/* Method & Standard */}
                  <div className="space-y-1.5 text-[9px] bg-black/50 p-2.5 rounded-xl border border-white/10 font-mono">
                    <div>
                      <span className="text-zinc-500 font-bold uppercase block text-[8px]">
                        {isTr ? "Algoritma / Model:" : "Algorithm / Model:"}
                      </span>
                      <span className={`${cc.text} font-semibold break-words`}>{tab.method}</span>
                    </div>
                    {tab.standard && (
                      <div className="pt-1 border-t border-white/10 flex items-center gap-1 text-zinc-400">
                        <ShieldCheck className="w-2.5 h-2.5 text-emerald-400 shrink-0" />
                        <span className="truncate">{tab.standard}</span>
                      </div>
                    )}
                  </div>

                  {/* Research Excerpt */}
                  <p className="text-[10px] text-zinc-400 leading-relaxed line-clamp-2 font-sans">
                    {tab.maturityNote}
                  </p>
                </div>

                {/* Launch Button with Dynamic Color & Hover Glow */}
                <Link
                  href={`/analysis/${category.id}/${tab.id}`}
                  className={`w-full min-h-[42px] py-2.5 px-4 rounded-xl ${cc.bg} ${cc.border} border text-white font-mono text-[11px] font-extrabold uppercase tracking-wider transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer shadow-md hover:shadow-lg hover:brightness-125 hover:scale-[1.01] active:scale-95 shrink-0 group/btn`}
                >
                  <span>{isTr ? "Modül Görünümünü Başlat" : "Launch Module Viewport"}</span>
                  <ArrowRight className={`w-3.5 h-3.5 ${cc.text} group-hover/btn:translate-x-1 transition-transform`} />
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
