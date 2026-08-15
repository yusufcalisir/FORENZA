"use client";

import TacticalPageHeader from "@/components/common/TacticalPageHeader";
import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
    Database,
    Network,
    Search,
    ChevronUp,
    ChevronDown,
    Dna,
    MapPin,
    Hash,
    Filter,
    Server,
    ShieldCheck,
    Eye,
} from "lucide-react";
import { useIngestStore, SAMPLE_CASE_EU, SAMPLE_CASE_AA } from "@/store/ingestStore";
import ActiveProfileBanner from "@/components/common/ActiveProfileBanner";
import FederatedNetworkPanel from "@/components/analysis/FederatedNetworkPanel";

// ─── Types ───────────────────────────────────────────────────────────────────

interface ProfileRecord {
    id: string;
    originNode: string;
    lociCount: number;
    insertedAt: string;
    quality: "complete" | "partial" | "degraded";
    vectorId: number;
    sampleType?: "EU" | "AA" | "CUSTOM";
}

// ─── Mock Data Generator ─────────────────────────────────────────────────────

const NODES = [
    "FORENSIC-LAB-ALPHA", "DISTRICT-DNA-LAB-01", "CENTRAL-GENOMICS-NODE",
    "MOBILE-EVIDENCE-UNIT-04", "CRIME-SCENE-UNIT-07", "NATIONAL-REFERENCE-LAB",
    "REGIONAL-GENOMICS-HUB", "PATHOLOGY-UNIT-03", "TRACE-EVIDENCE-LAB",
];

function seededRandom(seed: number): () => number {
    let s = seed;
    return () => {
        s = (s * 16807 + 0) % 2147483647;
        return s / 2147483647;
    };
}

function generateProfiles(count: number): ProfileRecord[] {
    const rand = seededRandom(42);
    const profiles: ProfileRecord[] = [];

    // Top Featured Sample Cases
    profiles.push({
        id: SAMPLE_CASE_EU.profileId,
        originNode: SAMPLE_CASE_EU.nodeId,
        lociCount: SAMPLE_CASE_EU.markerCount,
        insertedAt: "2026-08-12 18:30",
        quality: "complete",
        vectorId: 100001,
        sampleType: "EU",
    });

    profiles.push({
        id: SAMPLE_CASE_AA.profileId,
        originNode: SAMPLE_CASE_AA.nodeId,
        lociCount: SAMPLE_CASE_AA.markerCount,
        insertedAt: "2026-08-12 18:32",
        quality: "complete",
        vectorId: 100002,
        sampleType: "AA",
    });

    for (let i = 2; i < count; i++) {
        const loci = Math.floor(rand() * 15) + 10;
        const quality: ProfileRecord["quality"] =
            loci >= 18 ? "complete" : loci >= 14 ? "partial" : "degraded";
        const month = String(Math.floor(rand() * 12) + 1).padStart(2, "0");
        const day = String(Math.floor(rand() * 28) + 1).padStart(2, "0");
        const hour = String(Math.floor(rand() * 24)).padStart(2, "0");
        const min = String(Math.floor(rand() * 60)).padStart(2, "0");

        profiles.push({
            id: `PRF-${String(i + 1).padStart(6, "0")}`,
            originNode: NODES[Math.floor(rand() * NODES.length)],
            lociCount: loci,
            insertedAt: `2026-${month}-${day} ${hour}:${min}`,
            quality,
            vectorId: 100000 + i,
        });
    }
    return profiles;
}

const ALL_PROFILES = generateProfiles(24_847);

// ─── Quality Badge Config ────────────────────────────────────────────────────

const QUALITY_CONFIG = {
    complete: { label: "COMPLETE (24 LOCI)", color: "#22C55E", bg: "rgba(34,197,94,0.12)", border: "rgba(34,197,94,0.3)" },
    partial: { label: "PARTIAL (14+ LOCI)", color: "#06B6D4", bg: "rgba(6,182,212,0.12)", border: "rgba(6,182,212,0.3)" },
    degraded: { label: "DEGRADED (<14 LOCI)", color: "#EF4444", bg: "rgba(239,68,68,0.12)", border: "rgba(239,68,68,0.3)" },
} as const;

// ─── Sort Types ──────────────────────────────────────────────────────────────

type SortKey = "id" | "originNode" | "lociCount" | "insertedAt";
type SortDir = "asc" | "desc";

export default function DatabasePage() {
    const { activeProfile, setInspectorOpen, loadSampleCaseEU, loadSampleCaseAA } = useIngestStore();

    const [activeView, setActiveView] = useState<"database" | "network">("database");
    const [search, setSearch] = useState("");
    const [nodeFilter, setNodeFilter] = useState<string>("all");
    const [sortKey, setSortKey] = useState<SortKey>("id");
    const [sortDir, setSortDir] = useState<SortDir>("desc");
    const [page, setPage] = useState(0);
    const PAGE_SIZE = 15;

    const filtered = useMemo(() => {
        let data = ALL_PROFILES;
        if (search) {
            const q = search.toLowerCase();
            data = data.filter(
                (p) =>
                    p.id.toLowerCase().includes(q) ||
                    p.originNode.toLowerCase().includes(q)
            );
        }
        if (nodeFilter !== "all") {
            data = data.filter((p) => p.originNode === nodeFilter);
        }
        return data;
    }, [search, nodeFilter]);

    const sorted = useMemo(() => {
        const copy = [...filtered];
        copy.sort((a, b) => {
            const aVal = a[sortKey];
            const bVal = b[sortKey];
            if (typeof aVal === "number" && typeof bVal === "number") {
                return sortDir === "asc" ? aVal - bVal : bVal - aVal;
            }
            const aStr = String(aVal);
            const bStr = String(bVal);
            return sortDir === "asc"
                ? aStr.localeCompare(bStr)
                : bStr.localeCompare(aStr);
        });
        return copy;
    }, [filtered, sortKey, sortDir]);

    const totalPages = Math.ceil(sorted.length / PAGE_SIZE);
    const pageData = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

    const toggleSort = (key: SortKey) => {
        if (sortKey === key) {
            setSortDir((d) => (d === "asc" ? "desc" : "asc"));
        } else {
            setSortKey(key);
            setSortDir("desc");
        }
        setPage(0);
    };

    const SortIcon = ({ field }: { field: SortKey }) => {
        if (sortKey !== field) return <ChevronDown className="w-3 h-3 text-tactical-text-dim" />;
        return sortDir === "asc"
            ? <ChevronUp className="w-3 h-3 text-[#22C55E]" />
            : <ChevronDown className="w-3 h-3 text-[#22C55E]" />;
    };

    // Stats
    const stats = useMemo(() => {
        const complete = ALL_PROFILES.filter((p) => p.quality === "complete").length;
        const partial = ALL_PROFILES.filter((p) => p.quality === "partial").length;
        const degraded = ALL_PROFILES.filter((p) => p.quality === "degraded").length;
        const uniqueNodes = new Set(ALL_PROFILES.map((p) => p.originNode)).size;
        return { total: ALL_PROFILES.length, complete, partial, degraded, uniqueNodes };
    }, []);

    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6 py-4 overflow-x-hidden font-mono"
        >
            {/* ── Unified Tactical Page Header ── */}
            <TacticalPageHeader
                title={activeView === "database" ? "Forensic DNA Database" : "Federated Evidence Network"}
                subtitle={
                    activeView === "database"
                        ? "Milvus Vector Profile Registry • 24 Extended Forensic STR Loci & 55 AIM SNPs • HMAC Hash Sealed"
                        : "Polygon zkEVM Distributed Node Registry • Peer-to-Peer Consensus • Homomorphic Query"
                }
                badge={activeView === "database" ? "COLLECTION: STR_PROFILES" : "FEDERATION: ACTIVE"}
                icon={activeView === "database" ? Database : Network}
                accentColor={activeView === "database" ? "cyan" : "purple"}
            />

            {/* ── Subsystem View Toggle Tabs ── */}
            <div className="flex flex-wrap items-center gap-2 border-b border-tactical-border/60 pb-3">
                <button
                    onClick={() => setActiveView("database")}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl font-mono text-xs font-bold uppercase tracking-wider transition-all cursor-pointer ${
                        activeView === "database"
                            ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-sm"
                            : "bg-tactical-surface/60 text-zinc-400 border border-tactical-border/60 hover:text-zinc-200"
                    }`}
                >
                    <Database className="w-3.5 h-3.5" />
                    <span>DNA Database Registry</span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                        {stats.total.toLocaleString()}
                    </span>
                </button>

                <button
                    onClick={() => setActiveView("network")}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl font-mono text-xs font-bold uppercase tracking-wider transition-all cursor-pointer ${
                        activeView === "network"
                            ? "bg-purple-500/15 text-purple-400 border border-purple-500/30 shadow-sm"
                            : "bg-tactical-surface/60 text-zinc-400 border border-tactical-border/60 hover:text-zinc-200"
                    }`}
                >
                    <Network className="w-3.5 h-3.5" />
                    <span>Federated Lab Network</span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                        7 Nodes
                    </span>
                </button>
            </div>

            {activeView === "network" ? (
                <FederatedNetworkPanel />
            ) : (
                <>
                    {/* ── ACTIVE DNA PROFILE BANNER & FEATURE INSPECTOR ── */}
                    <ActiveProfileBanner />

                    {/* ── Bio-Forensic Stats Strip ── */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                        {[
                            { label: "Total Profiles", value: stats.total.toLocaleString(), color: "#FAFAFA", bg: "#111113", border: "#27272A" },
                            { label: "Complete (24 Loci)", value: stats.complete.toLocaleString(), color: "#22C55E", bg: "rgba(34,197,94,0.06)", border: "rgba(34,197,94,0.25)" },
                            { label: "Partial Profiles", value: stats.partial.toLocaleString(), color: "#06B6D4", bg: "rgba(6,182,212,0.06)", border: "rgba(6,182,212,0.25)" },
                            { label: "Degraded Profiles", value: stats.degraded.toLocaleString(), color: "#EF4444", bg: "rgba(239,68,68,0.06)", border: "rgba(239,68,68,0.25)" },
                            { label: "Active Network Nodes", value: stats.uniqueNodes.toString(), color: "#8B5CF6", bg: "rgba(139,92,246,0.06)", border: "rgba(139,92,246,0.25)" },
                        ].map((s) => (
                            <div
                                key={s.label}
                                className="rounded-xl border p-4 text-center transition-all hover:scale-[1.02] shadow-md last:col-span-2 sm:last:col-span-1"
                                style={{ background: s.bg, borderColor: s.border }}
                            >
                                <p className="text-xl sm:text-2xl font-bold tabular-nums" style={{ color: s.color }}>
                                    {s.value}
                                </p>
                                <p className="text-[9px] uppercase tracking-widest text-tactical-text-dim mt-1 font-semibold">
                                    {s.label}
                                </p>
                            </div>
                        ))}
                    </div>

                    {/* ── Toolbar ── */}
                    <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-tactical-text-dim" />
                            <input
                                type="text"
                                value={search}
                                onChange={(e) => { setSearch(e.target.value); setPage(0); }}
                                placeholder="Search by Profile ID (e.g. CASE-2026-EU) or Node..."
                                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-tactical-border bg-tactical-surface
                                    text-xs text-tactical-text placeholder:text-tactical-text-dim outline-none transition-all
                                    focus:border-[#06B6D4] focus:ring-1 focus:ring-[#06B6D4]/30 shadow-inner font-mono"
                            />
                        </div>
                        <div className="flex items-center gap-2 w-full sm:w-auto">
                            <div className="flex items-center gap-2 w-full bg-[#070D18] border border-tactical-border rounded-xl px-3 py-1.5 focus-within:border-[#06B6D4]">
                                <Filter className="w-4 h-4 text-[#06B6D4] shrink-0" />
                                <select
                                    value={nodeFilter}
                                    onChange={(e) => { setNodeFilter(e.target.value); setPage(0); }}
                                    className="w-full bg-[#070D18] text-white text-xs outline-none cursor-pointer py-1 font-mono"
                                >
                                    <option value="all">ALL ORIGIN NODES ({stats.uniqueNodes})</option>
                                    {NODES.map((n) => (
                                        <option key={n} value={n}>{n}</option>
                                    ))}
                                </select>
                            </div>

                            <button
                                onClick={() => {
                                    setSearch("");
                                    setNodeFilter("all");
                                    setSortKey("id");
                                    setSortDir("desc");
                                    setPage(0);
                                }}
                                className="px-3.5 py-2.5 rounded-xl border border-tactical-border bg-tactical-surface text-xs text-tactical-text-muted
                                    hover:text-white hover:border-[#06B6D4] transition-all font-mono whitespace-nowrap cursor-pointer"
                            >
                                Reset
                            </button>
                        </div>
                    </div>

                    {/* ── Table Container ── */}
                    <div className="rounded-xl border border-tactical-border bg-tactical-surface overflow-hidden shadow-2xl">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-xs font-mono">
                                <thead>
                                    <tr className="border-b border-tactical-border bg-tactical-surface-dark/90 text-tactical-text-dim uppercase text-[10px] tracking-wider select-none">
                                        <th className="py-3 px-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("id")}>
                                            <div className="flex items-center gap-1.5">
                                                <span>Profile ID</span>
                                                <SortIcon field="id" />
                                            </div>
                                        </th>
                                        <th className="py-3 px-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("originNode")}>
                                            <div className="flex items-center gap-1.5">
                                                <span>Origin Node</span>
                                                <SortIcon field="originNode" />
                                            </div>
                                        </th>
                                        <th className="py-3 px-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("lociCount")}>
                                            <div className="flex items-center gap-1.5">
                                                <span>Loci Count</span>
                                                <SortIcon field="lociCount" />
                                            </div>
                                        </th>
                                        <th className="py-3 px-4">Quality Status</th>
                                        <th className="py-3 px-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("insertedAt")}>
                                            <div className="flex items-center gap-1.5">
                                                <span>Timestamp</span>
                                                <SortIcon field="insertedAt" />
                                            </div>
                                        </th>
                                        <th className="py-3 px-4 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-tactical-border/50 text-tactical-text">
                                    {pageData.length === 0 ? (
                                        <tr>
                                            <td colSpan={6} className="py-12 text-center text-tactical-text-dim">
                                                <Dna className="w-8 h-8 mx-auto mb-2 text-tactical-text-dim opacity-30" />
                                                <p className="text-xs">No matching DNA profiles found.</p>
                                                <p className="text-[10px] text-tactical-text-dim mt-1">Try clearing filters or search queries.</p>
                                            </td>
                                        </tr>
                                    ) : (
                                        pageData.map((p) => {
                                            const q = QUALITY_CONFIG[p.quality];
                                            const isActive = activeProfile?.profileId === p.id;
                                            return (
                                                <tr
                                                    key={p.id}
                                                    className={`transition-colors font-mono ${
                                                        isActive
                                                            ? "bg-[#06B6D4]/10 hover:bg-[#06B6D4]/15"
                                                            : "hover:bg-tactical-surface-dark/50"
                                                    }`}
                                                >
                                                    <td className="py-3 px-4 font-semibold text-white">
                                                        <div className="flex items-center gap-2">
                                                            <div className={`w-1.5 h-1.5 rounded-full ${isActive ? "bg-[#06B6D4] animate-pulse" : "bg-zinc-600"}`} />
                                                            <span>{p.id}</span>
                                                            {p.sampleType && (
                                                                <span className={`text-[8px] font-bold px-1.5 py-0.2 rounded border ${
                                                                    p.sampleType === "EU"
                                                                        ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                                                                        : "bg-purple-500/20 text-purple-300 border-purple-500/40"
                                                                }`}>
                                                                    {p.sampleType}
                                                                </span>
                                                            )}
                                                        </div>
                                                    </td>
                                                    <td className="py-3 px-4 text-tactical-text-muted">
                                                        <div className="flex items-center gap-1.5">
                                                            <MapPin className="w-3 h-3 text-tactical-text-dim shrink-0" />
                                                            <span className="truncate max-w-[180px]">{p.originNode}</span>
                                                        </div>
                                                    </td>
                                                    <td className="py-3 px-4 text-tactical-text font-bold">
                                                        {p.lociCount} / 24
                                                    </td>
                                                    <td className="py-3 px-4">
                                                        <span
                                                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-bold tracking-wider uppercase border"
                                                            style={{ color: q.color, background: q.bg, borderColor: q.border }}
                                                        >
                                                            {q.label}
                                                        </span>
                                                    </td>
                                                    <td className="py-3 px-4 text-tactical-text-dim text-[11px]">
                                                        {p.insertedAt}
                                                    </td>
                                                    <td className="py-3 px-4 text-right">
                                                        <div className="flex items-center justify-end gap-1.5">
                                                            {p.sampleType === "EU" ? (
                                                                <button
                                                                    onClick={loadSampleCaseEU}
                                                                    className="px-2 py-1 rounded bg-[#06B6D4]/15 border border-[#06B6D4]/30 text-[#06B6D4] hover:bg-[#06B6D4]/25 text-[10px] font-bold transition-all cursor-pointer"
                                                                >
                                                                    Load EU
                                                                </button>
                                                            ) : p.sampleType === "AA" ? (
                                                                <button
                                                                    onClick={loadSampleCaseAA}
                                                                    className="px-2 py-1 rounded bg-purple-500/15 border border-purple-500/30 text-purple-400 hover:bg-purple-500/25 text-[10px] font-bold transition-all cursor-pointer"
                                                                >
                                                                    Load AA
                                                                </button>
                                                            ) : null}
                                                            <button
                                                                onClick={() => setInspectorOpen(true)}
                                                                className="px-2 py-1 rounded bg-tactical-surface-dark border border-tactical-border hover:border-[#06B6D4] text-tactical-text-muted hover:text-white text-[10px] transition-all flex items-center gap-1 cursor-pointer"
                                                                title="Inspect Invariant Vectors"
                                                            >
                                                                <Eye className="w-3 h-3" />
                                                                <span>Inspect</span>
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            );
                                        })
                                    )}
                                </tbody>
                            </table>
                        </div>

                        {/* ── Pagination ── */}
                        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3.5 border-t border-tactical-border bg-tactical-surface-dark/60 text-xs text-tactical-text-dim font-mono">
                            <div>
                                Showing <span className="text-white font-bold">{filtered.length === 0 ? 0 : page * PAGE_SIZE + 1}</span> to{" "}
                                <span className="text-white font-bold">{Math.min((page + 1) * PAGE_SIZE, filtered.length)}</span> of{" "}
                                <span className="text-white font-bold">{filtered.length.toLocaleString()}</span> entries
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                                    disabled={page === 0}
                                    className="px-3.5 py-1.5 rounded-xl border border-tactical-border bg-tactical-surface text-xs text-tactical-text-muted
                                        hover:text-white hover:border-[#06B6D4] transition-all
                                        disabled:opacity-30 disabled:cursor-not-allowed font-mono cursor-pointer"
                                >
                                    Previous
                                </button>
                                <span className="px-2 text-tactical-text">
                                    Page {page + 1} of {Math.max(1, totalPages)}
                                </span>
                                <button
                                    onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                                    disabled={page >= totalPages - 1}
                                    className="px-3.5 py-1.5 rounded-xl border border-tactical-border bg-tactical-surface text-xs text-tactical-text-muted
                                        hover:text-white hover:border-[#06B6D4] transition-all
                                        disabled:opacity-30 disabled:cursor-not-allowed font-mono cursor-pointer"
                                >
                                    Next
                                </button>
                            </div>
                        </div>

                        {/* ── Footer ── */}
                        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 pt-3 border-t border-tactical-border/60 text-[10px] text-tactical-text-dim font-mono p-3">
                            <div className="flex items-center gap-2 min-w-0">
                                <Server className="w-3.5 h-3.5 text-[#06B6D4] shrink-0" />
                                <span className="truncate">Milvus v2.4 • IVF_FLAT Index • Dimension 384 • Distance: COSINE</span>
                            </div>
                            <div className="flex items-center gap-1.5 text-[#22C55E] shrink-0">
                                <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                                <span className="font-bold uppercase tracking-wider whitespace-nowrap">Isolated Biometric Ledger</span>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </motion.div>
    );
}
