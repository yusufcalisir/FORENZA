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
    // Only override if the user manually selected a preference in a previous session
    const savedLang = localStorage.getItem("forenza_saas_lang") as SaasLanguage | null;
    if (savedLang === "tr" || savedLang === "en") {
      setLangState(savedLang);
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
