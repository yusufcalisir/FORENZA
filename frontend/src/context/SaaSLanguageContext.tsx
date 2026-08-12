"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
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
  const [lang, setLangState] = useState<SaasLanguage>(initialLang);

  useEffect(() => {
    // 1. If user previously manually toggled language, respect their choice
    const savedLang = localStorage.getItem("forenza_saas_lang") as SaasLanguage | null;
    if (savedLang === "tr" || savedLang === "en") {
      setLangState(savedLang);
      return;
    }

    // 2. Client-side auto-detection fallback (browser language & timezone)
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
