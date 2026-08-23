"use client";

import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { useState, useMemo, useEffect, Suspense } from "react";
import {
  Database,
  FlaskConical,
  ShieldCheck,
  GitGraph,
  Menu,
  X,
  Home,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Activity,
  Radio,
  Search,
  Sliders,
  ArrowRight,
  Cpu,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";
import DnaProfileInspectorModal from "@/components/common/DnaProfileInspectorModal";
import SaaSLanguageToggle from "@/components/landing/SaaSLanguageToggle";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { useIngestStore } from "@/store/ingestStore";
import {
  SUBSYSTEM_CATEGORIES,
  getSubsystemCategories,
  getMaturityConfig,
  COLOR_CLASSES,
  MATURITY_CONFIG,
  SubsystemCategory,
} from "@/config/subsystems";

const EXECUTIVE_NAV = [
  {
    id: "analysis",
    label: "Workstation Hub",
    href: "/analysis",
    icon: FlaskConical,
    color: "text-cyan-400",
    bg: "bg-cyan-500/10",
    border: "border-cyan-500/25",
  },
  {
    id: "investigation",
    label: "Investigation Graph",
    href: "/investigation",
    icon: GitGraph,
    color: "text-purple-400",
    bg: "bg-purple-500/10",
    border: "border-purple-500/25",
  },
  {
    id: "database",
    label: "Network & Registry",
    href: "/database",
    icon: Database,
    color: "text-blue-400",
    bg: "bg-blue-500/10",
    border: "border-blue-500/25",
  },
  {
    id: "audit",
    label: "Compliance Ledger",
    href: "/audit",
    icon: ShieldCheck,
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/25",
  },
] as const;

function normalizeSearchText(text?: string | null): string {
  if (!text) return "";
  return text
    .toLocaleLowerCase("tr-TR")
    .replace(/ı/g, "i")
    .replace(/ğ/g, "g")
    .replace(/ü/g, "u")
    .replace(/ş/g, "s")
    .replace(/ö/g, "o")
    .replace(/ç/g, "c")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function SidebarContent({
  collapsed,
  onCloseMobile,
}: {
  collapsed: boolean;
  onCloseMobile?: () => void;
}) {
  const pathname = usePathname();
  const { t, lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const executiveNav = useMemo(() => [
    {
      id: "analysis",
      label: isTr ? "Çalışma Alanı" : "Workstation Hub",
      href: "/analysis",
      icon: FlaskConical,
      color: "text-cyan-400",
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/25",
    },
    {
      id: "investigation",
      label: isTr ? "Soruşturma Grafı" : "Investigation Graph",
      href: "/investigation",
      icon: GitGraph,
      color: "text-purple-400",
      bg: "bg-purple-500/10",
      border: "border-purple-500/25",
    },
    {
      id: "database",
      label: isTr ? "Ağ ve Kütük" : "Network & Registry",
      href: "/database",
      icon: Database,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
      border: "border-blue-500/25",
    },
    {
      id: "audit",
      label: isTr ? "Uyumluluk Defteri" : "Compliance Ledger",
      href: "/audit",
      icon: ShieldCheck,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/25",
    },
  ], [isTr]);

  // Extract active category and tab from URL path (e.g. /analysis/genotyping/str)
  const pathParts = pathname.split("/").filter(Boolean); // ["analysis", "genotyping", "str"]
  const currentCategory = pathParts[0] === "analysis" ? pathParts[1] : null;
  const currentTab = pathParts[0] === "analysis" ? pathParts[2] : null;

  const [searchQuery, setSearchQuery] = useState("");
  const [expandedPillars, setExpandedPillars] = useState<Record<string, boolean>>({
    [currentCategory || "genotyping"]: true,
  });

  // Auto-expand active pillar when navigating
  useEffect(() => {
    if (currentCategory) {
      setExpandedPillars((prev) => ({ ...prev, [currentCategory]: true }));
    }
  }, [currentCategory]);

  const togglePillarAccordion = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    setExpandedPillars((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const categories = useMemo(() => getSubsystemCategories(lang), [lang]);
  const maturityConfig = useMemo(() => getMaturityConfig(lang), [lang]);

  // High-precision bi-lingual, diacritic-insensitive, multi-token search
  const { filteredCategories, totalMatches } = useMemo(() => {
    const q = searchQuery.trim();
    if (!q) {
      return { filteredCategories: categories, totalMatches: 35 };
    }

    const tokens = q
      .split(/\s+/)
      .map((t) => normalizeSearchText(t))
      .filter(Boolean);

    if (tokens.length === 0) {
      return { filteredCategories: categories, totalMatches: 35 };
    }

    let matchCount = 0;

    const result = categories
      .map((cat, catIdx) => {
        const canonicalCat = SUBSYSTEM_CATEGORIES[catIdx] || cat;

        // Build category corpus across all TR + EN fields
        const catCorpus = [
          cat.id,
          cat.label,
          cat.labelTr,
          cat.shortLabel,
          cat.shortLabelTr,
          cat.tagline,
          cat.taglineTr,
          cat.description,
          cat.descriptionTr,
          canonicalCat.label,
          canonicalCat.labelTr,
          canonicalCat.tagline,
          canonicalCat.taglineTr,
          canonicalCat.description,
          canonicalCat.descriptionTr,
          `suit ${cat.pillarNumber}`,
          `pillar ${cat.pillarNumber}`,
          `kategori 0${cat.pillarNumber}`,
          `0${cat.pillarNumber}`,
        ]
          .filter(Boolean)
          .map((t) => normalizeSearchText(t))
          .join(" ");

        const catMatchesAllTokens = tokens.every((token) => catCorpus.includes(token));

        // Filter matching tabs within category across all TR + EN fields
        const matchingTabs = cat.tabs.filter((tab, tabIdx) => {
          const canonicalTab = canonicalCat.tabs?.[tabIdx] || tab;

          const tabCorpus = [
            tab.id,
            tab.label,
            tab.labelTr,
            tab.shortTitle,
            tab.shortTitleTr,
            tab.badge,
            tab.method,
            tab.methodTr,
            tab.standard,
            tab.standardTr,
            tab.maturityNote,
            tab.maturityNoteTr,
            canonicalTab.label,
            canonicalTab.labelTr,
            canonicalTab.shortTitle,
            canonicalTab.shortTitleTr,
            canonicalTab.method,
            canonicalTab.methodTr,
            canonicalTab.standard,
            canonicalTab.standardTr,
            canonicalTab.maturityNote,
            canonicalTab.maturityNoteTr,
          ]
            .filter(Boolean)
            .map((t) => normalizeSearchText(t))
            .join(" ");

          return tokens.every((token) => tabCorpus.includes(token));
        });

        if (matchingTabs.length > 0) {
          matchCount += matchingTabs.length;
          return { ...cat, tabs: matchingTabs };
        }

        if (catMatchesAllTokens) {
          matchCount += cat.tabs.length;
          return cat;
        }

        return null;
      })
      .filter(Boolean) as SubsystemCategory[];

    return { filteredCategories: result, totalMatches: matchCount };
  }, [searchQuery, categories]);

  // If searching, auto-expand all matched pillars
  useEffect(() => {
    if (searchQuery.trim()) {
      const allOpen: Record<string, boolean> = {};
      categories.forEach((c) => {
        allOpen[c.id] = true;
      });
      setExpandedPillars(allOpen);
    }
  }, [searchQuery, categories]);

  return (
    <div className="flex flex-col h-full overflow-hidden text-xs font-mono select-none">
      {/* ── Search Input (When expanded) ── */}
      {!collapsed && (
        <div className="p-3 border-b border-tactical-border/60 shrink-0">
          <div className="relative">
            <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2 shrink-0 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t.sidebarNav?.searchPlaceholder || "Search 35 Subsystems..."}
              className="w-full pl-9 pr-8 py-2 min-h-[40px] bg-black/50 border border-tactical-border/70 rounded-xl text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-cyan-500/60 transition-colors"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                aria-label={isTr ? "Aramayı Temizle" : "Clear Search"}
                className="absolute right-1 top-1/2 -translate-y-1/2 min-w-[36px] min-h-[36px] flex items-center justify-center text-zinc-400 hover:text-white cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* ── Scrollable Navigation Tree ── */}
      <div className="flex-1 overflow-y-auto p-2 space-y-4 scrollbar-thin scrollbar-thumb-zinc-800/80">
        {/* Section 1: Workspace Operations */}
        <div className="space-y-1">
          {!collapsed && (
            <div className="px-2.5 py-1 flex items-center justify-between text-[9px] font-extrabold uppercase tracking-widest text-zinc-400">
              <span>{t.sidebarNav?.operations || "Operations"}</span>
            </div>
          )}
          {executiveNav.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.id === "analysis"
                ? pathname === "/analysis"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.id}
                href={item.href}
                onClick={onCloseMobile}
                className={`group relative flex items-center gap-2.5 rounded-xl px-3 py-2.5 min-h-[42px] transition-all font-mono text-xs font-bold uppercase tracking-wider ${
                  isActive
                    ? `${item.bg} ${item.color} border ${item.border} shadow-sm`
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-white/5 border border-transparent"
                } ${collapsed ? "justify-center px-2" : ""}`}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 ${
                    isActive ? item.color : "text-zinc-500 group-hover:text-zinc-300"
                  }`}
                />
                {!collapsed && <span className="truncate">{item.label}</span>}
                {isActive && !collapsed && (
                  <span
                    className={`ml-auto h-1.5 w-1.5 rounded-full ${item.color.replace("text-", "bg-")} shrink-0`}
                  />
                )}
                {collapsed && (
                  <div className="pointer-events-none absolute left-full top-1/2 -translate-y-1/2 ml-3 whitespace-nowrap rounded-lg border border-tactical-border bg-zinc-900 px-3 py-1.5 text-[10px] font-bold text-zinc-200 opacity-0 shadow-xl transition-all group-hover:opacity-100 z-[200]">
                    {item.label}
                  </div>
                )}
              </Link>
            );
          })}
        </div>

        {/* Section 2: Biocomputational Suites (7 Domains) */}
        <div className="space-y-1.5">
          {!collapsed && (
            <div className="px-2.5 py-1 flex items-center justify-between text-[9px] font-extrabold uppercase tracking-widest text-zinc-400">
              <span>{t.sidebarNav?.biocomputationalSuites || "Biocomputational Suites"}</span>
              {searchQuery.trim() && (
                <span className="text-cyan-400 font-bold lowercase tracking-normal">
                  ({totalMatches} {isTr ? "eşleşme" : "matches"})
                </span>
              )}
            </div>
          )}

          {filteredCategories.length === 0 && !collapsed && (
            <div className="p-3.5 rounded-xl border border-dashed border-tactical-border/60 bg-black/40 text-center space-y-2 my-2">
              <Search className="w-4 h-4 text-zinc-500 mx-auto" />
              <p className="text-xs font-bold text-zinc-300">
                {isTr ? "Eşleşen modül bulunamadı" : "No matching modules"}
              </p>
              <p className="text-[10px] text-zinc-500 leading-normal font-sans">
                {isTr
                  ? `"${searchQuery}" için sonuç yok. STR, MCMC, Horvath, ZKP, BPA, İzotop gibi terimleri arayabilirsiniz.`
                  : `No results for "${searchQuery}". Try keywords like STR, MCMC, Horvath, ZKP, BPA, Isotope.`}
              </p>
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="text-[10px] text-cyan-400 hover:text-cyan-300 font-bold underline cursor-pointer inline-block mt-1 font-mono"
              >
                {isTr ? "Aramayı Temizle" : "Clear Search"}
              </button>
            </div>
          )}

          {filteredCategories.map((cat) => {
            const CatIcon = cat.icon;
            const cc = COLOR_CLASSES[cat.color] || COLOR_CLASSES.cyan;
            const isCategoryActive = currentCategory === cat.id;
            const isCategoryHubActive = isCategoryActive && !currentTab;
            const isExpanded = Boolean(expandedPillars[cat.id]);

            return (
              <div
                key={cat.id}
                className="rounded-xl overflow-hidden bg-black/20 border border-tactical-border/40"
              >
                {/* Pillar Header (Direct navigation to Pillar Domain Hub) */}
                <div
                  className={`w-full flex items-center justify-between gap-1.5 px-2.5 py-1.5 min-h-[42px] transition-colors ${
                    isCategoryHubActive
                      ? `${cc.bg} ${cc.text} border-b border-tactical-border/40 font-extrabold`
                      : isCategoryActive
                      ? `${cc.bg} text-white`
                      : "text-zinc-300 hover:bg-white/5"
                  } ${collapsed ? "justify-center px-1" : ""}`}
                >
                  <Link
                    href={`/analysis/${cat.id}`}
                    onClick={onCloseMobile}
                    className="flex items-center gap-2.5 min-w-0 flex-1 py-1"
                    title={cat.label}
                  >
                    <CatIcon
                      className={`w-4 h-4 shrink-0 ${
                        isCategoryActive ? cc.text : "text-zinc-400"
                      }`}
                    />
                    {!collapsed && (
                      <span className="font-bold text-[11px] uppercase tracking-wider truncate">
                        {cat.label}
                      </span>
                    )}
                  </Link>

                  {!collapsed && (
                    <button
                      onClick={(e) => togglePillarAccordion(e, cat.id)}
                      aria-label={isExpanded ? (isTr ? "Daralt" : "Collapse") : (isTr ? "Genişlet" : "Expand")}
                      className="min-h-[38px] min-w-[38px] flex items-center justify-center text-zinc-400 hover:text-white rounded-lg hover:bg-white/5 active:scale-95 transition-all cursor-pointer shrink-0"
                    >
                      <ChevronDown
                        className={`w-4 h-4 transition-transform duration-200 ${
                          isExpanded ? "rotate-180" : ""
                        }`}
                      />
                    </button>
                  )}
                </div>

                {/* Sub-Module List */}
                <AnimatePresence initial={false}>
                  {isExpanded && !collapsed && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="space-y-1 p-1 bg-black/40 border-t border-tactical-border/20"
                    >
                      {cat.tabs.map((tab) => {
                        const isTabActive =
                          currentCategory === cat.id && currentTab === tab.id;
                        const mat = maturityConfig[tab.maturity];

                        return (
                          <Link
                            key={tab.id}
                            href={`/analysis/${cat.id}/${tab.id}`}
                            onClick={onCloseMobile}
                            className={`group flex items-center justify-between gap-2 px-2.5 py-2 min-h-[38px] rounded-lg text-[10px] sm:text-[11px] transition-all cursor-pointer ${
                              isTabActive
                                ? `${cc.activeBg} ${cc.text} border ${cc.border} font-extrabold shadow-sm`
                                : "text-zinc-400 hover:text-zinc-100 hover:bg-white/5 border border-transparent font-medium"
                            }`}
                          >
                            <div className="flex items-center gap-2 min-w-0 flex-1">
                              <span
                                className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                                  isTabActive
                                    ? "bg-emerald-400 animate-pulse"
                                    : tab.maturity === "ACTIVE"
                                    ? "bg-emerald-500/70"
                                    : "bg-cyan-500/70"
                                }`}
                              />
                              <span className="truncate">{tab.shortTitle}</span>
                            </div>

                            <span
                              className={`text-[8px] font-bold px-1.5 py-0.5 rounded border whitespace-nowrap shrink-0 ${mat.tagBg} ${mat.tagText} ${mat.tagBorder}`}
                            >
                              {tab.badge}
                            </span>
                          </Link>
                        );
                      })}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Footer ── */}
      <div className="p-2.5 border-t border-tactical-border/60 shrink-0">
        <Link
          href="/"
          className={`group flex items-center gap-2.5 rounded-xl px-3 py-2.5 min-h-[40px] text-zinc-400 hover:text-white hover:bg-emerald-500/10 hover:border hover:border-emerald-500/20 transition-all font-mono text-[10px] font-bold uppercase tracking-wider border border-transparent ${
            collapsed ? "justify-center px-1" : ""
          }`}
        >
          <Home className="w-4 h-4 shrink-0 text-zinc-500 group-hover:text-emerald-400 transition-colors" />
          {!collapsed && (
            <span className="group-hover:text-emerald-300 transition-colors">
              {t.sidebarNav?.landingPage || "Landing Page"}
            </span>
          )}
        </Link>
      </div>
    </div>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { setInspectorOpen, activeProfile } = useIngestStore();
  const { t, lang } = useSaasLanguage();
  const isTr = lang === "tr";

  return (
    <div className="flex min-h-screen lg:h-screen lg:overflow-hidden bg-[#080c14] text-tactical-text">
      {/* ── WCAG 2.2 AA Skip to Main Content Link ── */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-[10000] focus:px-4 focus:py-2 focus:bg-emerald-500 focus:text-black focus:font-mono focus:font-bold focus:rounded-xl focus:shadow-[0_0_20px_rgba(16,185,129,0.5)] focus:outline-none focus:ring-2 focus:ring-black"
      >
        {isTr ? "Ana İçeriğe Atla" : "Skip to Main Content"}
      </a>
      {/* ── Mobile Overlay Drawer ── */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileMenuOpen(false)}
              className="fixed inset-0 z-[9990] bg-black/80 backdrop-blur-sm lg:hidden"
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 220 }}
              className="fixed inset-y-0 left-0 z-[9999] w-80 max-w-[88vw] h-[100dvh] bg-[#0a0f1a] border-r border-tactical-border lg:hidden flex flex-col shadow-2xl pb-[env(safe-area-inset-bottom,16px)]"
            >
              <div className="flex h-14 items-center justify-between px-4 border-b border-tactical-border/60 shrink-0">
                <div className="flex items-center gap-2.5">
                  <ForenzaLogoIcon size={28} />
                  <span className="font-mono text-xs font-extrabold tracking-widest text-white">
                    FORENZA OS
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <SaaSLanguageToggle />
                  <button
                    onClick={() => setMobileMenuOpen(false)}
                    aria-label={isTr ? "Menüyü Kapat" : "Close Menu"}
                    className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-hidden">
                <Suspense
                  fallback={<div className="p-4 text-xs text-zinc-500">Loading Navigation…</div>}
                >
                  <SidebarContent
                    collapsed={false}
                    onCloseMobile={() => setMobileMenuOpen(false)}
                  />
                </Suspense>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* ── Desktop Sleek Sidebar ── */}
      <motion.aside
        animate={{ width: sidebarCollapsed ? 64 : 272 }}
        transition={{ type: "spring", damping: 26, stiffness: 220 }}
        className="hidden lg:flex flex-col bg-[#0A0F1D] border-r border-tactical-border/70 overflow-hidden shrink-0 shadow-2xl relative z-40"
      >
        {/* Logo & Toggle Header */}
        <div
          className={`flex h-14 items-center border-b border-tactical-border/60 shrink-0 ${
            sidebarCollapsed ? "justify-center px-2" : "justify-between px-3.5"
          }`}
        >
          <div className="flex items-center gap-2.5 min-w-0">
            <ForenzaLogoIcon size={26} className="shrink-0" />
            {!sidebarCollapsed && (
              <div className="min-w-0">
                <p className="font-mono text-[11px] font-extrabold tracking-widest text-white truncate">
                  FORENZA
                </p>
                <p className="font-mono text-[8px] tracking-widest text-emerald-400 truncate">
                  EVIDENCE OS
                </p>
              </div>
            )}
          </div>

          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-1.5 rounded-lg text-zinc-500 hover:text-white hover:bg-white/5 transition-colors cursor-pointer shrink-0"
            title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="w-3.5 h-3.5" />
            ) : (
              <ChevronLeft className="w-3.5 h-3.5" />
            )}
          </button>
        </div>

        {/* Active Case Badge */}
        {!sidebarCollapsed && (
          <div className="mx-3 mt-3 px-3 py-2 rounded-xl bg-emerald-500/5 border border-emerald-500/20 shrink-0">
            <div className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0" />
              <span className="font-mono text-[9px] font-bold text-emerald-400 uppercase tracking-wider truncate">
                {t.dashboardTopBar?.activeCase || "CASE-2026-FORENZA"}
              </span>
            </div>
            <p className="font-mono text-[8px] text-zinc-400 mt-0.5 truncate">
              {t.dashboardTopBar?.subsystemsCount || "35 Subsystems"}
            </p>
          </div>
        )}

        {/* Navigation Content */}
        <div className="flex-1 overflow-hidden mt-1">
          <Suspense
            fallback={<div className="p-4 text-xs text-zinc-500">Loading Navigation…</div>}
          >
            <SidebarContent collapsed={sidebarCollapsed} />
          </Suspense>
        </div>
      </motion.aside>

      {/* ── Main Workspace Area ── */}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        {/* Mobile Topbar */}
        <header className="lg:hidden flex h-14 items-center justify-between px-3 sm:px-4 border-b border-tactical-border/50 bg-gradient-to-r from-[#08101e]/98 via-[#0a1220]/98 to-[#08101e]/98 backdrop-blur-xl shrink-0 pt-[env(safe-area-inset-top,0px)] shadow-[0_1px_20px_rgba(0,0,0,0.6)] relative overflow-hidden">
          {/* Subtle ambient glow stripe */}
          <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent pointer-events-none" />
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-48 h-8 bg-cyan-500/5 rounded-full blur-2xl pointer-events-none" />

          <button
            onClick={() => setMobileMenuOpen(true)}
            aria-label={isTr ? "Navigasyon Menüsünü Aç" : "Open Navigation Menu"}
            className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-xl bg-white/5 border border-tactical-border/60 text-zinc-300 hover:text-white hover:border-cyan-500/40 hover:bg-cyan-500/10 active:scale-95 transition-all cursor-pointer shadow-sm relative z-10"
          >
            <Menu className="w-5 h-5 text-zinc-400" />
          </button>

          <Link href="/analysis" className="flex items-center gap-2.5 min-w-0 relative z-10">
            <div className="relative shrink-0">
              <div className="absolute inset-0 bg-emerald-500/20 rounded-full blur-md" />
              <ForenzaLogoIcon size={26} className="relative" />
            </div>
            <div className="flex flex-col leading-none">
              <span className="font-mono text-[11px] font-extrabold tracking-[0.2em] text-white">
                FORENZA
              </span>
              <span className="font-mono text-[8px] font-bold tracking-[0.15em] text-emerald-400/90">
                EVIDENCE OS
              </span>
            </div>
          </Link>

          <div className="flex items-center gap-2 shrink-0 relative z-10">
            <SaaSLanguageToggle />
            <button
              onClick={() => setInspectorOpen(true)}
              aria-label={isTr ? "Aktif DNA Profilini İncele" : "Inspect Active DNA Profile"}
              className="min-h-[38px] px-2.5 py-1 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 active:scale-95 border border-emerald-500/25 hover:border-emerald-500/50 text-emerald-300 font-mono text-[9px] font-bold flex items-center gap-1.5 transition-all cursor-pointer shadow-sm shrink-0 group"
            >
              <span className="relative flex shrink-0">
                <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-emerald-400 opacity-50" />
                <Radio className="w-2.5 h-2.5 text-emerald-400 relative" />
              </span>
              <span className="truncate max-w-[72px] sm:max-w-[110px] group-hover:text-emerald-200 transition-colors">
                {activeProfile?.profileId ? activeProfile.profileId.replace("PROFILE-", "") : "CASE-2026"}
              </span>
            </button>
          </div>
        </header>

        {/* Mobile Compact Status Ribbon */}
        <div className="lg:hidden flex items-center gap-0 border-b border-tactical-border/30 bg-black/70 backdrop-blur-sm shrink-0 overflow-hidden">
          <div className="flex items-center gap-1.5 px-3 py-1.5 border-r border-tactical-border/30 shrink-0">
            <span className="relative flex">
              <span className="animate-ping absolute inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400 opacity-60" />
              <Activity className="w-2.5 h-2.5 text-emerald-400 relative shrink-0" />
            </span>
            <span className="font-mono text-[8px] text-zinc-500 tracking-wider whitespace-nowrap">{t.dashboardTopBar?.subsystemsCount || "35 Subsystems"}</span>
            <span className="font-mono text-[8px] text-emerald-400 font-extrabold tracking-widest whitespace-nowrap">{t.dashboardTopBar?.subsystemsOnline || "ONLINE"}</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 shrink-0">
            <ShieldCheck className="w-2.5 h-2.5 text-amber-400 shrink-0" />
            <span className="font-mono text-[8px] text-amber-400 font-bold tracking-wider whitespace-nowrap">{t.dashboardTopBar?.isoStandard || "ISO/IEC 17025:2017"}</span>
          </div>
          <div className="flex-1" />
          <div className="px-2 py-1 mr-1">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20 font-mono text-[7px] text-cyan-400 font-bold tracking-widest uppercase whitespace-nowrap">
              <Cpu className="w-2 h-2" />
              {t.dashboardTopBar?.engineName || "FORENZA OS"}
            </span>
          </div>
        </div>


        {/* Desktop Top Status Bar */}
        <div className="hidden lg:flex h-10 items-center justify-between px-5 border-b border-tactical-border/40 bg-black/40 shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <Activity className="w-3 h-3 text-emerald-400" />
              <span className="font-mono text-[9px] text-zinc-500 uppercase tracking-wider">
                {t.dashboardTopBar?.subsystemsCount || "35 Subsystems"}
              </span>
              <span className="font-mono text-[9px] text-emerald-400 font-bold">
                {t.dashboardTopBar?.subsystemsOnline || "ONLINE"}
              </span>
            </div>
            <div className="h-3 w-px bg-tactical-border/60" />
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-[9px] text-zinc-500">
                {t.dashboardTopBar?.biocompEngine || "Biocomputational Engine"}
              </span>
              <span className="font-mono text-[9px] text-cyan-400 font-bold">
                {t.dashboardTopBar?.engineName || "FORENZA OS"}
              </span>
            </div>
            <div className="h-3 w-px bg-tactical-border/60" />
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-3 h-3 text-amber-400" />
              <span className="font-mono text-[9px] text-zinc-500">
                {t.dashboardTopBar?.accreditation || "Accreditation"}
              </span>
              <span className="font-mono text-[9px] text-amber-400 font-bold">
                {t.dashboardTopBar?.isoStandard || "ISO/IEC 17025:2017"}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <SaaSLanguageToggle />
            <button
              onClick={() => setInspectorOpen(true)}
              className="flex items-center gap-2 px-3 py-1 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 active:scale-95 border border-emerald-500/30 text-emerald-300 font-mono text-[9px] font-bold transition-all cursor-pointer shadow-sm"
              title={isTr ? "Aktif DNA Profilini İncele" : "Inspect Active DNA Profile"}
            >
              <Radio className="w-3 h-3 text-emerald-400 animate-pulse shrink-0" />
              <span className="tracking-widest uppercase truncate max-w-[140px]">
                {activeProfile?.profileId || t.dashboardTopBar?.activeCase || "CASE-2026-FORENZA"}
              </span>
            </button>
          </div>
        </div>

        {/* Viewport Render Outlet */}
        <main id="main-content" className="flex-1 overflow-y-auto p-4 lg:p-6 bg-[#070D18]/70">
          {children}
        </main>
        <DnaProfileInspectorModal />
      </div>
    </div>
  );
}
