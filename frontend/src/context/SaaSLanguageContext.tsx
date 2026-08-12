"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { SaasLanguage, saasTranslations, SaasTranslation } from "@/dictionaries/saasTranslations";

interface SaasLanguageContextType {
  lang: SaasLanguage;
  setLang: (lang: SaasLanguage) => void;
  t: SaasTranslation;
}

const SaasLanguageContext = createContext<SaasLanguageContextType | undefined>(undefined);

export function SaasLanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<SaasLanguage>("en");
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    // 1. Check local storage preference
    const savedLang = localStorage.getItem("forenza_saas_lang") as SaasLanguage | null;
    if (savedLang === "tr" || savedLang === "en") {
      setLangState(savedLang);
      setInitialized(true);
      return;
    }

    // 2. Check Browser Locale & Timezone / IP hint
    try {
      const userLang = navigator.language || (navigator.languages && navigator.languages[0]) || "";
      const isTurkishLocale = userLang.toLowerCase().includes("tr");
      const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
      const isIstanbulTimezone = userTimezone.includes("Istanbul");

      if (isTurkishLocale || isIstanbulTimezone) {
        setLangState("tr");
      } else {
        setLangState("en");
      }
    } catch {
      setLangState("en");
    }

    setInitialized(true);
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
