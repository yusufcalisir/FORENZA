"use client";

import React, { use } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  ChevronRight,
  ShieldCheck,
  Zap,
  Sliders,
  ArrowRight,
} from "lucide-react";
import {
  SUBSYSTEM_CATEGORIES,
  COLOR_CLASSES,
  MATURITY_CONFIG,
  getSubsystemCategory,
  CategoryId,
} from "@/config/subsystems";
import { renderPanel } from "@/components/analysis/PanelRouter";
import { useIngestStore } from "@/store/ingestStore";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export default function ModulePage({
  params,
}: {
  params: Promise<{ category: string; tab: string }>;
}) {
  const resolvedParams = use(params);
  const categoryId = resolvedParams.category as CategoryId;
  const tabId = resolvedParams.tab;
  const { setInspectorOpen } = useIngestStore();
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const category = getSubsystemCategory(categoryId) || SUBSYSTEM_CATEGORIES[0];
  const currentTab = category.tabs.find((t) => t.id === tabId) || category.tabs[0];

  const CatIcon = category.icon;
  const cc = COLOR_CLASSES[category.color] || COLOR_CLASSES.cyan;
  const currentMat = MATURITY_CONFIG[currentTab?.maturity || "ACTIVE"];

  return (
    <div className="space-y-4 font-mono max-w-full overflow-hidden">
      {/* ── Dedicated Viewport Command Card (NO global map banner) ── */}
      <div className="rounded-2xl border border-tactical-border/80 bg-[#070D18] p-4 sm:p-6 space-y-4 shadow-2xl">
        {/* Module Header & Breadcrumb Bar */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-tactical-border/60 pb-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className={`p-2.5 rounded-xl border ${cc.border} ${cc.bg} shrink-0`}>
              <CatIcon className={`w-5 h-5 ${cc.text}`} />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <Link
                  href="/analysis"
                  className="text-[10px] text-zinc-500 hover:text-zinc-300 font-bold uppercase tracking-wider transition-colors"
                >
                  {isTr ? "İstasyon Merkezi" : "Workstation Hub"}
                </Link>
                <span className="text-zinc-600">/</span>
                <Link
                  href={`/analysis/${category.id}`}
                  className="text-[10px] text-zinc-400 hover:text-cyan-300 font-bold uppercase tracking-wider transition-colors"
                >
                  {category.label}
                </Link>
                <span className="text-zinc-600">/</span>
                <span className={`text-[10px] font-extrabold ${cc.text} uppercase tracking-wider`}>
                  {currentTab.shortTitle}
                </span>
              </div>
              <h1 className="text-base sm:text-lg font-bold text-white tracking-tight mt-0.5 truncate">
                {currentTab.label}
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap shrink-0">
            <span
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[9px] font-extrabold border ${currentMat.tagBg} ${currentMat.tagText} ${currentMat.tagBorder} uppercase tracking-wider shadow-sm`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${currentMat.dot}`} />
              {currentMat.label}
            </span>
            <span className="text-[9px] font-bold text-zinc-300 bg-black/60 border border-tactical-border/60 px-2.5 py-1 rounded-lg uppercase tracking-wider">
              {currentTab.badge}
            </span>
          </div>
        </div>

        {/* Sibling Tabs Switcher Cards (Non-scrolling responsive grid) */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 pt-1">
          {category.tabs.map((tab) => {
            const TabIcon = tab.icon;
            const isActive = currentTab.id === tab.id;
            const tMat = MATURITY_CONFIG[tab.maturity];

            return (
              <Link
                key={tab.id}
                href={`/analysis/${category.id}/${tab.id}`}
                className={`flex items-center justify-between gap-1.5 px-3 py-2 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer min-w-0 ${
                  isActive
                    ? `${cc.activeBg} border ${cc.border} ${cc.text} shadow-sm font-extrabold`
                    : "bg-black/40 text-zinc-400 border border-tactical-border/50 hover:text-zinc-200 hover:border-zinc-700"
                }`}
              >
                <div className="flex items-center gap-1.5 min-w-0 truncate">
                  <TabIcon className="w-3.5 h-3.5 shrink-0" />
                  <span className="truncate">{tab.shortTitle}</span>
                </div>
                <span
                  className={`px-1 py-0.2 rounded text-[7px] font-bold border shrink-0 ${tMat.tagBg} ${tMat.tagText} ${tMat.tagBorder}`}
                >
                  {tab.badge}
                </span>
              </Link>
            );
          })}
        </div>

        {/* Operational Status & Scientific Boundary Banner */}
        <div
          className={`p-3 rounded-xl border ${currentMat.bg} ${currentMat.border} flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs shadow-md`}
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <span
              className={`flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[9px] font-bold border ${currentMat.tagBg} ${currentMat.tagText} ${currentMat.tagBorder} shrink-0 uppercase`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${currentMat.dot}`} />
              {currentMat.shortLabel}
            </span>
            <p className="text-[10px] text-zinc-300 min-w-0 break-words">
              <strong className="text-white">{currentTab.label}:</strong> {currentTab.maturityNote}
            </p>
          </div>
          <span className="text-[9px] text-zinc-400 shrink-0 font-bold hidden xl:inline-block">
            {currentMat.desc}
          </span>
        </div>

        {/* Full-Viewport Computational Canvas */}
        <div className="pt-2">
          <AnimatePresence mode="wait">
            <motion.div
              key={`${category.id}-${currentTab.id}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.18 }}
              className="w-full max-w-full overflow-hidden"
            >
              {renderPanel(currentTab.id)}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
