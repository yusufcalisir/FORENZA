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
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";
import DnaProfileInspectorModal from "@/components/common/DnaProfileInspectorModal";
import { useIngestStore } from "@/store/ingestStore";
import {
  SUBSYSTEM_CATEGORIES,
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

function SidebarContent({
  collapsed,
  onCloseMobile,
}: {
  collapsed: boolean;
  onCloseMobile?: () => void;
}) {
  const pathname = usePathname();

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

  // Filtered subsystems based on search
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return SUBSYSTEM_CATEGORIES;
    const q = searchQuery.toLowerCase().trim();

    return SUBSYSTEM_CATEGORIES.map((cat) => {
      const matchCat =
        cat.label.toLowerCase().includes(q) ||
        cat.description.toLowerCase().includes(q) ||
        cat.tagline.toLowerCase().includes(q);

      const matchingTabs = cat.tabs.filter(
        (tab) =>
          tab.label.toLowerCase().includes(q) ||
          tab.shortTitle.toLowerCase().includes(q) ||
          tab.badge.toLowerCase().includes(q) ||
          tab.method.toLowerCase().includes(q)
      );

      if (matchCat) return cat;
      if (matchingTabs.length > 0) {
        return { ...cat, tabs: matchingTabs };
      }
      return null;
    }).filter(Boolean) as SubsystemCategory[];
  }, [searchQuery]);

  // If searching, expand all
  useEffect(() => {
    if (searchQuery.trim()) {
      const allOpen: Record<string, boolean> = {};
      SUBSYSTEM_CATEGORIES.forEach((c) => {
        allOpen[c.id] = true;
      });
      setExpandedPillars(allOpen);
    }
  }, [searchQuery]);

  return (
    <div className="flex flex-col h-full overflow-hidden text-xs font-mono select-none">
      {/* ── Search Input (When expanded) ── */}
      {!collapsed && (
        <div className="p-3 border-b border-tactical-border/60 shrink-0">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search 35 Subsystems..."
              className="w-full pl-8 pr-7 py-1.5 bg-black/50 border border-tactical-border/70 rounded-xl text-[11px] text-white placeholder-zinc-500 focus:outline-none focus:border-cyan-500/60 transition-colors"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white cursor-pointer"
              >
                <X className="w-3 h-3" />
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
            <div className="px-2 py-1 flex items-center justify-between text-[9px] font-extrabold uppercase tracking-widest text-zinc-400">
              <span>Operations</span>
            </div>
          )}
          {EXECUTIVE_NAV.map((item) => {
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
                className={`group relative flex items-center gap-2.5 rounded-xl px-2.5 py-2 transition-all font-mono text-[11px] font-bold uppercase tracking-wider ${
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
        <div className="space-y-1">
          {!collapsed && (
            <div className="px-2 py-1 flex items-center justify-between text-[9px] font-extrabold uppercase tracking-widest text-zinc-400">
              <span>Biocomputational Suites</span>
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
                  className={`w-full flex items-center justify-between gap-2 px-2.5 py-2 transition-colors ${
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
                    className="flex items-center gap-2 min-w-0 flex-1"
                    title={cat.label}
                  >
                    <CatIcon
                      className={`w-3.5 h-3.5 shrink-0 ${
                        isCategoryActive ? cc.text : "text-zinc-400"
                      }`}
                    />
                    {!collapsed && (
                      <span className="font-bold text-[10px] uppercase tracking-wider truncate">
                        {cat.label}
                      </span>
                    )}
                  </Link>

                  {!collapsed && (
                    <button
                      onClick={(e) => togglePillarAccordion(e, cat.id)}
                      className="p-1 text-zinc-500 hover:text-white rounded transition-colors cursor-pointer shrink-0"
                      title={isExpanded ? "Collapse" : "Expand"}
                    >
                      <ChevronDown
                        className={`w-3.5 h-3.5 transition-transform duration-200 ${
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
                      className="space-y-0.5 p-1 bg-black/40 border-t border-tactical-border/20"
                    >
                      {cat.tabs.map((tab) => {
                        const isTabActive =
                          currentCategory === cat.id && currentTab === tab.id;
                        const mat = MATURITY_CONFIG[tab.maturity];

                        return (
                          <Link
                            key={tab.id}
                            href={`/analysis/${cat.id}/${tab.id}`}
                            onClick={onCloseMobile}
                            className={`group flex items-center justify-between gap-2 px-2 py-1.5 rounded-lg text-[10px] transition-all cursor-pointer ${
                              isTabActive
                                ? `${cc.activeBg} ${cc.text} border ${cc.border} font-extrabold shadow-sm`
                                : "text-zinc-400 hover:text-zinc-100 hover:bg-white/5 border border-transparent font-medium"
                            }`}
                          >
                            <div className="flex items-center gap-2 min-w-0">
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
                              className={`text-[7px] font-bold px-1 py-0.2 rounded border shrink-0 ${mat.tagBg} ${mat.tagText} ${mat.tagBorder}`}
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
      <div className="p-2 border-t border-tactical-border/60 shrink-0">
        <Link
          href="/"
          className={`group flex items-center gap-2.5 rounded-xl px-2.5 py-2 text-zinc-400 hover:text-white hover:bg-emerald-500/10 hover:border hover:border-emerald-500/20 transition-all font-mono text-[9px] font-bold uppercase tracking-wider border border-transparent ${
            collapsed ? "justify-center px-1" : ""
          }`}
        >
          <Home className="w-3.5 h-3.5 shrink-0 text-zinc-500 group-hover:text-emerald-400 transition-colors" />
          {!collapsed && (
            <span className="group-hover:text-emerald-300 transition-colors">Landing Page</span>
          )}
        </Link>
      </div>
    </div>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { setInspectorOpen } = useIngestStore();

  return (
    <div className="flex min-h-screen lg:h-screen lg:overflow-hidden bg-[#080c14] text-tactical-text">
      {/* ── Mobile Overlay Drawer ── */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileMenuOpen(false)}
              className="fixed inset-0 z-[60] bg-black/75 backdrop-blur-sm lg:hidden"
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 220 }}
              className="fixed inset-y-0 left-0 z-[70] w-72 max-w-[85vw] bg-[#0a0f1a] border-r border-tactical-border lg:hidden flex flex-col"
            >
              <div className="flex h-14 items-center justify-between px-4 border-b border-tactical-border/60 shrink-0">
                <div className="flex items-center gap-2.5">
                  <ForenzaLogoIcon size={28} />
                  <span className="font-mono text-xs font-extrabold tracking-widest text-white">
                    FORENZA OS
                  </span>
                </div>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
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
        className="hidden lg:flex flex-col bg-[#0A0F1D] border-r border-tactical-border/70 overflow-hidden shrink-0 shadow-2xl relative z-30"
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
                CASE-2026-FORENZA
              </span>
            </div>
            <p className="font-mono text-[8px] text-zinc-400 mt-0.5 truncate">
              35 Biocomputational Modules
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
        <header className="lg:hidden flex h-12 items-center justify-between px-3 border-b border-tactical-border/60 bg-[#0a0f1a] shrink-0">
          <button onClick={() => setMobileMenuOpen(true)}>
            <Menu className="w-5 h-5 text-zinc-400" />
          </button>
          <div className="flex items-center gap-2">
            <ForenzaLogoIcon size={22} />
            <span className="font-mono text-xs font-extrabold tracking-widest text-white">
              FORENZA
            </span>
          </div>
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-[8px] font-bold uppercase tracking-wider">
            <Radio className="w-2.5 h-2.5 text-emerald-400 animate-pulse" />
            <span>ONLINE</span>
          </div>
        </header>

        {/* Desktop Top Status Bar */}
        <div className="hidden lg:flex h-10 items-center justify-between px-5 border-b border-tactical-border/40 bg-black/40 shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <Activity className="w-3 h-3 text-emerald-400" />
              <span className="font-mono text-[9px] text-zinc-500 uppercase tracking-wider">
                35 Subsystems
              </span>
              <span className="font-mono text-[9px] text-emerald-400 font-bold">ONLINE</span>
            </div>
            <div className="h-3 w-px bg-tactical-border/60" />
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-[9px] text-zinc-500">Biocomputational Engine</span>
              <span className="font-mono text-[9px] text-cyan-400 font-bold">FORENZA OS</span>
            </div>
            <div className="h-3 w-px bg-tactical-border/60" />
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-3 h-3 text-amber-400" />
              <span className="font-mono text-[9px] text-zinc-500">Accreditation</span>
              <span className="font-mono text-[9px] text-amber-400 font-bold">
                ISO/IEC 17025:2017
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 pl-2">
              <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
              <span className="font-mono text-[9px] text-emerald-400 font-bold uppercase tracking-widest">
                CASE-2026-FORENZA
              </span>
            </div>
          </div>
        </div>

        {/* Viewport Render Outlet */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 bg-[#070D18]/70">
          {children}
        </main>
        <DnaProfileInspectorModal />
      </div>
    </div>
  );
}
