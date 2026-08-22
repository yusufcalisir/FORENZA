"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { SaasLanguage, saasTranslations, SaasTranslation } from "@/dictionaries/saasTranslations";

interface SaasLanguageContextType {
  lang: SaasLanguage;
  setLang: (lang: SaasLanguage) => void;
  t: SaasTranslation;
  /** True only after the first client render. Use to guard hydration-sensitive text. */
  mounted: boolean;
}

const SaasLanguageContext = createContext<SaasLanguageContextType | undefined>(undefined);

const COOKIE_NAME = "forenza_saas_lang_user"; // Only written on explicit user toggle
const STORAGE_KEY = "forenza_saas_lang_user";  // Same — never auto-set

function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp("(^|;\\s*)" + name + "=([^;]+)"));
  return match ? decodeURIComponent(match[2]) : null;
}

function setCookie(name: string, value: string, days = 365) {
  if (typeof document === "undefined") return;
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

export function SaasLanguageProvider({
  children,
  initialLang = "en",
}: {
  children: React.ReactNode;
  initialLang?: SaasLanguage;
}) {
  const [lang, setLangState] = useState<SaasLanguage>(initialLang);
  const [mounted, setMounted] = useState(false);

  const applyLang = useCallback((newLang: SaasLanguage, persist = true) => {
    setLangState(newLang);
    if (persist) {
      try {
        localStorage.setItem(STORAGE_KEY, newLang);
        setCookie(COOKIE_NAME, newLang);
        window.dispatchEvent(new CustomEvent("forenza-lang-changed", { detail: newLang }));
      } catch (e) {
        console.warn("Language persistence error", e);
      }
    }
  }, []);

  useEffect(() => {
    setMounted(true);

    // Phase 1: Check if user made an EXPLICIT manual selection (localStorage or cookie).
    // Auto-detected values are NEVER written to localStorage, so if something is here
    // it was definitely set by the user via the toggle button.
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as SaasLanguage | null;
      if (stored === "tr" || stored === "en") {
        setLangState(stored);
        // Keep cookie in sync but don't touch localStorage again
        setCookie(COOKIE_NAME, stored);
        return;
      }
      // Check cookie as fallback (e.g. localStorage cleared but cookie still there)
      const cookieVal = getCookie(COOKIE_NAME) as SaasLanguage | null;
      if (cookieVal === "tr" || cookieVal === "en") {
        setLangState(cookieVal);
        // Restore localStorage so Phase 1 catches it next time
        localStorage.setItem(STORAGE_KEY, cookieVal);
        return;
      }
    } catch (_) {}

    // Phase 2: No explicit user preference found.
    // Use server-detected initialLang (from IP / Accept-Language header) — state only,
    // do NOT persist to localStorage/cookie so other users / future sessions start fresh.
    if (initialLang === "tr" || initialLang === "en") {
      setLangState(initialLang);
      // Intentionally NOT writing to localStorage or cookie here.
      return;
    }

    // Phase 3: Client-side browser fallback (no cookie, no server hint).
    // Apply to state only — no persistence.
    try {
      const navLang = (navigator.language || "").toLowerCase();
      const navLangs = Array.from(navigator.languages || []).map((l) => l.toLowerCase());
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";

      const isTurkish =
        navLang.startsWith("tr") ||
        navLangs.some((l) => l.startsWith("tr")) ||
        tz.includes("Istanbul") ||
        tz.includes("Turkey");

      setLangState(isTurkish ? "tr" : "en");
      // Still no persistence — only explicit user action persists.
    } catch (e) {
      console.warn("Language detection fallback error", e);
    }
  }, [initialLang]);

  // Synchronize across multiple components, frames, or tabs
  useEffect(() => {
    const handleStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && (e.newValue === "tr" || e.newValue === "en")) {
        setLangState(e.newValue as SaasLanguage);
      }
    };

    const handleCustomChange = (e: Event) => {
      const customEvent = e as CustomEvent<SaasLanguage>;
      if (customEvent.detail === "tr" || customEvent.detail === "en") {
        setLangState(customEvent.detail);
      }
    };

    window.addEventListener("storage", handleStorage);
    window.addEventListener("forenza-lang-changed", handleCustomChange);
    return () => {
      window.removeEventListener("storage", handleStorage);
      window.removeEventListener("forenza-lang-changed", handleCustomChange);
    };
  }, []);

  const setLang = (newLang: SaasLanguage) => {
    applyLang(newLang, true);
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
