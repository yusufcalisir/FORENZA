"use client";

import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { Globe } from "lucide-react";

export default function SaaSLanguageToggle() {
  const { lang, setLang } = useSaasLanguage();

  return (
    <div className="inline-flex items-center rounded-xl border border-tactical-border/80 bg-black/60 p-1 backdrop-blur-md">
      <div className="flex items-center gap-1 px-2 text-zinc-500">
        <Globe className="h-3.5 w-3.5 text-emerald-400" />
      </div>
      <button
        type="button"
        onClick={() => setLang("tr")}
        className={`rounded-lg px-2.5 py-1 font-mono text-[10px] font-bold tracking-wider transition-all duration-200 cursor-pointer ${
          lang === "tr"
            ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-[0_0_10px_rgba(16,185,129,0.2)]"
            : "text-zinc-400 hover:text-white hover:bg-white/5 border border-transparent"
        }`}
      >
        TR
      </button>
      <button
        type="button"
        onClick={() => setLang("en")}
        className={`rounded-lg px-2.5 py-1 font-mono text-[10px] font-bold tracking-wider transition-all duration-200 cursor-pointer ${
          lang === "en"
            ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-[0_0_10px_rgba(16,185,129,0.2)]"
            : "text-zinc-400 hover:text-white hover:bg-white/5 border border-transparent"
        }`}
      >
        EN
      </button>
    </div>
  );
}
