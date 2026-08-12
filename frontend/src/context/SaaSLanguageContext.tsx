"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { SaasLanguage, saasTranslations, SaasTranslation } from "@/dictionaries/saasTranslations";

interface SaasLanguageContextType {
  lang: SaasLanguage;
  setLang: (lang: SaasLanguage) => void;
  t: SaasTranslation;
}

const SaasLanguageContext = createContext<SaasLanguageContextType | undefined>(undefined);

export function SaasLanguageProvider({
  children,
  initialLang = "en",
}: {
  children: React.ReactNode;
  initialLang?: SaasLanguage;
}) {
  // Synchronous init: localStorage preference takes highest priority,
  // then SSR-detected initialLang. No flash, no double-render.
  const getInitialLang = (): SaasLanguage => {
    if (typeof window !== "undefined") {
      try {
        const saved = localStorage.getItem("forenza_saas_lang") as SaasLanguage | null;
        if (saved === "tr" || saved === "en") return saved;
      } catch (_) {}
    }
    return initialLang;
  };

  const [lang, setLangState] = useState<SaasLanguage>(getInitialLang);

  // Client-side timezone/browser fallback — ONLY runs when:
  // 1. SSR headers were unavailable (initialLang stayed "en"), AND
  // 2. No localStorage preference was saved by the user.
  // This prevents flash when SSR already correctly detected TR.
  useEffect(() => {
    try {
      const saved = localStorage.getItem("forenza_saas_lang") as SaasLanguage | null;
      if (saved === "tr" || saved === "en") return; // user preference already applied
      if (initialLang !== "en") return;             // SSR already detected correctly, no need to re-detect

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

  const t = saasTranslations[lang];

  return (
    <SaasLanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </SaasLanguageContext.Provider>
  );
}

export function useSaasLanguage() {
  const context = useContext(SaasLanguageContext);
  if (!context) {
    // Fallback if rendered outside provider
    return {
      lang: "en" as SaasLanguage,
      setLang: () => {},
      t: saasTranslations.en,
    };
  }
  return context;
}
