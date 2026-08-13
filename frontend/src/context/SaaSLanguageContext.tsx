"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { SaasLanguage, saasTranslations, SaasTranslation } from "@/dictionaries/saasTranslations";

interface SaasLanguageContextType {
  lang: SaasLanguage;
  setLang: (lang: SaasLanguage) => void;
  t: SaasTranslation;
  /** True only after the first client render. Use to guard hydration-sensitive text. */
  mounted: boolean;
}

const SaasLanguageContext = createContext<SaasLanguageContextType | undefined>(undefined);

export function SaasLanguageProvider({
  children,
  initialLang = "en",
}: {
  children: React.ReactNode;
  initialLang?: SaasLanguage;
}) {
  // IMPORTANT: Must start with `initialLang` (not localStorage) so that the
  // first client render exactly matches the server-rendered HTML.
  // Reading localStorage here causes React Hydration Error #418 because the
  // server has no localStorage and renders with initialLang, but the client
  // synchronously reads a different value → SSR/CSR mismatch.
  const [lang, setLangState] = useState<SaasLanguage>(initialLang);

  // mounted flag — false on server / first render, true after hydration.
  // Expose this so every consumer can safely gate lang-dependent JSX output.
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Mark hydration complete — must run before any lang changes below.
    setMounted(true);

    // Phase 1: Respect saved user preference (highest priority).
    try {
      const saved = localStorage.getItem("forenza_saas_lang") as SaasLanguage | null;
      if (saved === "tr" || saved === "en") {
        setLangState(saved);
        return;
      }
    } catch (_) {}

    // Phase 2: SSR already detected language correctly → nothing to do.
    if (initialLang !== "en") return;

    // Phase 3: SSR headers unavailable (local dev, etc.) → browser fallback.
    try {
      const navLang = (navigator.language || "").toLowerCase();
      const navLangs = Array.from(navigator.languages || []).map((l) => l.toLowerCase());
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";

      const isTurkish =
        navLang.startsWith("tr") ||
        navLangs.some((l) => l.startsWith("tr")) ||
        tz.includes("Istanbul") ||
        tz.includes("Turkey");

      if (isTurkish) {
        setLangState("tr");
      }
    } catch (e) {
      console.warn("Language auto-detection error", e);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setLang = (newLang: SaasLanguage) => {
    setLangState(newLang);
    try {
      localStorage.setItem("forenza_saas_lang", newLang);
    } catch (e) {
      console.warn("Could not save language preference", e);
    }
  };

  // Dynamically synchronize browser tab title with active language
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.title =
        lang === "tr"
          ? "FORENZA | Çoklu-Omik Adli Delil İşletim Sistemi"
          : "FORENZA | Multi-Omic Forensic Evidence OS";
    }
  }, [lang]);

  const t = saasTranslations[lang];

  return (
    <SaasLanguageContext.Provider value={{ lang, setLang, t, mounted }}>
      {children}
    </SaasLanguageContext.Provider>
  );
}

export function useSaasLanguage() {
  const context = useContext(SaasLanguageContext);
  if (!context) {
    return {
      lang: "en" as SaasLanguage,
      setLang: () => {},
      t: saasTranslations.en,
      mounted: false,
    };
  }
  return context;
}
