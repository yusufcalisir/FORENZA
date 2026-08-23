"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Cpu,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import ActiveProfileBanner from "@/components/common/ActiveProfileBanner";
import { useIngestStore } from "@/store/ingestStore";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import {
  getSubsystemCategories,
  COLOR_CLASSES,
} from "@/config/subsystems";

export default function AnalysisPage() {
  const { setInspectorOpen } = useIngestStore();
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";
  const categories = getSubsystemCategories(lang);

  return (
    <div className="space-y-6 font-mono max-w-full overflow-hidden">
      {/* ── Active Case DNA Profile & GIS Map Telemetry (Only on main Hub) ── */}
      <ActiveProfileBanner />

      {/* ── Executive Biocomputational Suites Matrix ── */}
      <div className="space-y-4">
        <div className="p-4 rounded-2xl bg-black/40 border border-tactical-border/60">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <h2 className="text-xs sm:text-sm font-extrabold uppercase tracking-wider text-white">
              {isTr ? "Adli Biyobilişimsel Süitler" : "Forensic Biocomputational Suites"}
            </h2>
            <span className="text-[9px] font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 px-2 py-0.5 rounded uppercase">
              {isTr ? "Çıkarım Matrisi" : "Inference Matrix"}
            </span>
          </div>
          <p className="text-[10px] text-zinc-400 mt-1 font-sans">
            {isTr
              ? "Kalibre edilmiş çok lokuslu biyobilişimsel modellere, 3D uzamsal görselleştiricilere ve ISO 17025 doğrulama motorlarına erişmek için bir araştırma süiti seçin."
              : "Select a research suite to access calibrated multilocus biocomputational models, 3D spatial visualizers, and ISO 17025 validation engines."}
          </p>
        </div>

        {/* 7 Research Domain Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {categories.map((cat) => {
            const CatIcon = cat.icon;
            const cc = COLOR_CLASSES[cat.color] || COLOR_CLASSES.cyan;

            return (
              <motion.div
                key={cat.id}
                whileHover={{ y: -3 }}
                transition={{ duration: 0.15 }}
                className={`rounded-2xl border ${cc.border} bg-gradient-to-b from-white/[0.04] to-transparent bg-[#080D1A] p-4 sm:p-5 flex flex-col justify-between space-y-4 hover:shadow-2xl hover:${cc.glow} transition-all duration-200 group relative overflow-hidden min-w-0 shadow-md`}
              >
                <div className="space-y-3 min-w-0">
                  {/* Header */}
                  <div className="flex items-center justify-between gap-2 min-w-0">
                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                      <div className={`p-2.5 rounded-xl border ${cc.border} ${cc.bg} shrink-0 shadow-sm`}>
                        <CatIcon className={`w-4 h-4 ${cc.text}`} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <span className={`text-[8px] font-bold ${cc.text} uppercase tracking-widest block`}>
                          {isTr ? `Süit ${cat.pillarNumber}` : `Pillar ${cat.pillarNumber}`}
                        </span>
                        <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider group-hover:text-white transition-colors truncate">
                          {cat.label}
                        </h3>
                      </div>
                    </div>
                    <span className="text-[8px] font-bold px-2 py-0.5 rounded-md bg-black/60 text-zinc-300 border border-white/10 shrink-0 whitespace-nowrap">
                      {isTr ? "5 Modül" : "5 Modules"}
                    </span>
                  </div>

                  {/* Tagline & Description */}
                  <p className="text-[10px] text-zinc-200 font-medium leading-relaxed font-sans">
                    {cat.tagline}
                  </p>
                  <p className="text-[9px] text-zinc-400 line-clamp-2 leading-relaxed font-sans">
                    {cat.description}
                  </p>

                  {/* Sub-module Badges */}
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {cat.tabs.map((tab) => (
                      <span
                        key={tab.id}
                        className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-black/60 text-zinc-300 border border-white/10 hover:border-white/20 whitespace-nowrap shrink-0 transition-colors"
                      >
                        {tab.badge}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action Button */}
                <div className="pt-3.5 border-t border-white/[0.08] flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                  <span className="text-[8px] text-emerald-400 font-mono flex items-center gap-1 shrink-0 font-semibold">
                    <ShieldCheck className="w-3 h-3 text-emerald-400 shrink-0" />
                    {isTr ? "ISO/IEC 17025 Doğrulandı" : "ISO/IEC 17025 Validated"}
                  </span>

                  <Link
                    href={`/analysis/${cat.id}`}
                    className={`w-full sm:w-auto min-h-[40px] px-4 py-2 rounded-xl ${cc.bg} ${cc.border} border text-white font-mono text-[11px] font-extrabold uppercase tracking-wider transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer shadow-md hover:shadow-lg hover:brightness-125 hover:scale-[1.02] active:scale-95 shrink-0 group/btn`}
                  >
                    <span>{isTr ? "Süiti İncele" : "Explore Suite"}</span>
                    <ArrowRight className={`w-3.5 h-3.5 ${cc.text} group-hover/btn:translate-x-1 transition-transform`} />
                  </Link>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
