"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { useState } from "react";
import {
    Network,
    Database,
    FlaskConical,
    ShieldCheck,
    GitGraph,
    LayoutDashboard,
    Menu,
    X,
    Home,
    ChevronLeft,
    ChevronRight,
    Dna,
    Activity,
    Radio,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";
import DnaProfileInspectorModal from "@/components/common/DnaProfileInspectorModal";

const NAV_ITEMS = [
    { id: "analysis", label: "Workstation", href: "/analysis", icon: FlaskConical, color: "text-cyan-400", bg: "bg-cyan-500/10", border: "border-cyan-500/25" },
    { id: "investigation", label: "Investigation", href: "/investigation", icon: GitGraph, color: "text-purple-400", bg: "bg-purple-500/10", border: "border-purple-500/25" },
    { id: "database", label: "Network & Database", href: "/database", icon: Database, color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/25" },
    { id: "audit", label: "Compliance & Audit", href: "/audit", icon: ShieldCheck, color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/25" },
] as const;

function NavItem({
    item,
    isActive,
    collapsed,
}: {
    item: typeof NAV_ITEMS[number];
    isActive: boolean;
    collapsed: boolean;
}) {
    const Icon = item.icon;
    return (
        <Link
            href={item.href}
            className={`group relative flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all duration-200 font-mono text-xs font-bold tracking-wider uppercase
                ${isActive
                    ? `${item.bg} ${item.color} border ${item.border} shadow-sm`
                    : "text-zinc-500 hover:text-zinc-200 hover:bg-white/5"
                }`}
        >
            <Icon className={`w-4 h-4 shrink-0 ${isActive ? item.color : "text-zinc-600 group-hover:text-zinc-400"}`} />
            {!collapsed && (
                <span className="truncate leading-none">{item.label}</span>
            )}
            {isActive && !collapsed && (
                <span className={`ml-auto h-1.5 w-1.5 rounded-full ${item.color.replace("text-", "bg-")} shrink-0`} />
            )}
            {collapsed && (
                <div className="pointer-events-none absolute left-full top-1/2 -translate-y-1/2 ml-3 whitespace-nowrap rounded-lg border border-tactical-border bg-zinc-900 px-3 py-1.5 text-[10px] font-bold text-zinc-200 opacity-0 shadow-xl transition-all group-hover:opacity-100 z-[200]">
                    {item.label}
                </div>
            )}
        </Link>
    );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const activeId = NAV_ITEMS.find((item) => pathname.startsWith(item.href))?.id ?? "analysis";

    return (
        <div className="flex min-h-screen lg:h-screen lg:overflow-hidden bg-[#080c14] text-tactical-text">
            {/* ── Mobile Overlay ── */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setMobileMenuOpen(false)}
                            className="fixed inset-0 z-[60] bg-black/70 backdrop-blur-sm lg:hidden"
                        />
                        <motion.aside
                            initial={{ x: "-100%" }}
                            animate={{ x: 0 }}
                            exit={{ x: "-100%" }}
                            transition={{ type: "spring", damping: 25, stiffness: 220 }}
                            className="fixed inset-y-0 left-0 z-[70] w-64 bg-[#0a0f1a] border-r border-tactical-border lg:hidden flex flex-col"
                        >
                            <div className="flex h-14 items-center justify-between px-4 border-b border-tactical-border/60">
                                <div className="flex items-center gap-2.5">
                                    <ForenzaLogoIcon size={28} />
                                    <span className="font-mono text-xs font-extrabold tracking-widest text-white">FORENZA</span>
                                </div>
                                <button onClick={() => setMobileMenuOpen(false)}>
                                    <X className="w-4 h-4 text-zinc-400" />
                                </button>
                            </div>
                            <nav className="flex-1 overflow-y-auto p-3 space-y-1">
                                {NAV_ITEMS.map((item) => (
                                    <NavItem key={item.id} item={item} isActive={activeId === item.id} collapsed={false} />
                                ))}
                            </nav>
                            <div className="p-3 border-t border-tactical-border/60">
                                <Link href="/" className="flex items-center gap-2 px-3 py-2 rounded-xl text-zinc-500 hover:text-zinc-300 font-mono text-[10px] font-bold uppercase tracking-wider transition-colors">
                                    <Home className="w-3.5 h-3.5" />
                                    Back to Landing
                                </Link>
                            </div>
                        </motion.aside>
                    </>
                )}
            </AnimatePresence>

            {/* ── Desktop Sidebar ── */}
            <motion.aside
                animate={{ width: sidebarCollapsed ? 60 : 220 }}
                transition={{ type: "spring", damping: 25, stiffness: 200 }}
                className="hidden lg:flex flex-col bg-[#0a0f1a] border-r border-tactical-border/60 overflow-hidden shrink-0"
            >
                {/* Logo */}
                <div className={`flex h-14 items-center border-b border-tactical-border/60 ${sidebarCollapsed ? "justify-center px-2" : "px-4 gap-2.5"}`}>
                    <ForenzaLogoIcon size={28} className="shrink-0" />
                    {!sidebarCollapsed && (
                        <div className="min-w-0">
                            <p className="font-mono text-[11px] font-extrabold tracking-widest text-white truncate">FORENZA</p>
                            <p className="font-mono text-[8px] tracking-widest text-emerald-500/70 truncate">EVIDENCE OS</p>
                        </div>
                    )}
                </div>

                {/* Case Badge */}
                {!sidebarCollapsed && (
                    <div className="mx-3 mt-3 px-3 py-2 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                        <div className="flex items-center gap-1.5">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0" />
                            <span className="font-mono text-[9px] font-bold text-emerald-400 uppercase tracking-wider truncate">CASE-2026-FORENZA</span>
                        </div>
                        <p className="font-mono text-[8px] text-zinc-500 mt-0.5 truncate">30 Subsystems Active</p>
                    </div>
                )}

                {/* Nav */}
                <nav className="flex-1 overflow-y-auto p-2 space-y-0.5 mt-2">
                    {NAV_ITEMS.map((item) => (
                        <NavItem key={item.id} item={item} isActive={activeId === item.id} collapsed={sidebarCollapsed} />
                    ))}
                </nav>

                {/* Bottom */}
                <div className="p-2 border-t border-tactical-border/60">
                    <Link
                        href="/"
                        className="group flex items-center gap-2.5 rounded-xl px-3 py-2 text-zinc-400 hover:text-white hover:bg-emerald-500/10 hover:border hover:border-emerald-500/20 transition-all font-mono text-[9px] font-bold uppercase tracking-wider border border-transparent"
                    >
                        <Home className="w-4 h-4 shrink-0 text-zinc-500 group-hover:text-emerald-400 transition-colors" />
                        {!sidebarCollapsed && <span className="group-hover:text-emerald-300 transition-colors">Back to Site</span>}
                    </Link>
                </div>
            </motion.aside>

            {/* ── Main Content ── */}
            <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
                {/* Mobile topbar */}
                <header className="lg:hidden flex h-12 items-center justify-between px-4 border-b border-tactical-border/60 bg-[#0a0f1a] shrink-0">
                    <button onClick={() => setMobileMenuOpen(true)}>
                        <Menu className="w-5 h-5 text-zinc-400" />
                    </button>
                    <div className="flex items-center gap-2">
                        <ForenzaLogoIcon size={24} />
                        <span className="font-mono text-xs font-extrabold tracking-widest text-white">FORENZA</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <Radio className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="font-mono text-[9px] text-emerald-400 font-bold">LIVE</span>
                    </div>
                </header>

                {/* Top Status Bar */}
                <div className="hidden lg:flex h-9 items-center justify-between px-5 border-b border-tactical-border/40 bg-black/40 shrink-0">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5">
                            <Activity className="w-3 h-3 text-emerald-400" />
                            <span className="font-mono text-[9px] text-zinc-500 uppercase tracking-wider">30 Subsystems</span>
                            <span className="font-mono text-[9px] text-emerald-400 font-bold">ONLINE</span>
                        </div>
                        <div className="h-3 w-px bg-tactical-border/60" />
                        <div className="flex items-center gap-1.5">
                            <Dna className="w-3 h-3 text-cyan-400" />
                            <span className="font-mono text-[9px] text-zinc-500">Engine</span>
                            <span className="font-mono text-[9px] text-cyan-400 font-bold">FORENZA OS</span>
                        </div>
                        <div className="h-3 w-px bg-tactical-border/60" />
                        <div className="flex items-center gap-1.5">
                            <ShieldCheck className="w-3 h-3 text-amber-400" />
                            <span className="font-mono text-[9px] text-zinc-500">ISO/IEC 17025:2017</span>
                            <span className="font-mono text-[9px] text-amber-400 font-bold">CERTIFIED</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
                        <span className="font-mono text-[9px] text-emerald-400 font-bold uppercase tracking-widest">CASE-2026-FORENZA • ACTIVE</span>
                    </div>
                </div>

                <main className="flex-1 overflow-y-auto p-4 lg:p-5">
                    {children}
                </main>
                <DnaProfileInspectorModal />
            </div>
        </div>
    );
}
