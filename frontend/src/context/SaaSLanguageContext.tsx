"use client";

import React, { createContext, useContext, useState } from "react";
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
  // Determine the correct starting language once, before first render.
  // Priority: 1) localStorage saved user choice, 2) SSR-detected initialLang.
  // This runs synchronously on the client to avoid any post-render flash.
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
