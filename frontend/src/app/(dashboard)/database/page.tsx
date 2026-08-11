"use client";

import TacticalPageHeader from "@/components/common/TacticalPageHeader";

import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
    Database,
    Search,
    ChevronUp,
    ChevronDown,
    Dna,
    MapPin,
    Hash,
    Filter,
    Server,
    HardDrive,
    Sparkles,
    ShieldCheck,
    Cpu,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface ProfileRecord {
    id: string;
    originNode: string;
    lociCount: number;
    insertedAt: string;
    quality: "complete" | "partial" | "degraded";
    vectorId: number;
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
    for (let i = 0; i < count; i++) {
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
    complete: { label: "COMPLETE (20 LOCI)", color: "#22C55E", bg: "rgba(34,197,94,0.12)", border: "rgba(34,197,94,0.3)" },
    partial: { label: "PARTIAL (14+ LOCI)", color: "#06B6D4", bg: "rgba(6,182,212,0.12)", border: "rgba(6,182,212,0.3)" },
    degraded: { label: "DEGRADED (<14 LOCI)", color: "#EF4444", bg: "rgba(239,68,68,0.12)", border: "rgba(239,68,68,0.3)" },
} as const;

// ─── Sort Types ──────────────────────────────────────────────────────────────

type SortKey = "id" | "originNode" | "lociCount" | "insertedAt";
type SortDir = "asc" | "desc";

// ─── Page Component ──────────────────────────────────────────────────────────

export default function DatabasePage() {
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
                title="Forensic DNA Database"
                subtitle="Milvus Vector Profile Registry • 24 Core CODIS Loci Indexes • HMAC Hash Sealed"
                badge="COLLECTION: STR_PROFILES"
                icon={Database}
                accentColor="cyan"
            />

            {/* ── Bio-Forensic Stats Strip ── */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
                {[
                    { label: "Total Profiles", value: stats.total.toLocaleString(), color: "#FAFAFA", bg: "#111113", border: "#27272A" },
                    { label: "Complete (20 Loci)", value: stats.complete.toLocaleString(), color: "#22C55E", bg: "rgba(34,197,94,0.06)", border: "rgba(34,197,94,0.25)" },
                    { label: "Partial Profiles", value: stats.partial.toLocaleString(), color: "#06B6D4", bg: "rgba(6,182,212,0.06)", border: "rgba(6,182,212,0.25)" },
                    { label: "Degraded Profiles", value: stats.degraded.toLocaleString(), color: "#EF4444", bg: "rgba(239,68,68,0.06)", border: "rgba(239,68,68,0.25)" },
                    { label: "Active Network Nodes", value: stats.uniqueNodes.toString(), color: "#8B5CF6", bg: "rgba(139,92,246,0.06)", border: "rgba(139,92,246,0.25)" },
                ].map((s) => (
                    <div
                        key={s.label}
                        className="rounded-xl border p-4 text-center transition-all hover:scale-[1.02] shadow-md"
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
                        placeholder="Search by Profile ID (e.g. PRF-000100) or Node..."
                        className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-tactical-border bg-tactical-surface
                            text-xs text-tactical-text placeholder:text-tactical-text-dim outline-none transition-all
                            focus:border-[#06B6D4] focus:ring-1 focus:ring-[#06B6D4]/30 shadow-inner"
                    />
                </div>
                <div className="flex items-center gap-2 justify-end">
                    <Filter className="w-4 h-4 text-[#06B6D4]" />
                    <select
                        value={nodeFilter}
                        onChange={(e) => { setNodeFilter(e.target.value); setPage(0); }}
                        className="bg-tactical-surface border border-tactical-border rounded-xl px-3 py-2.5
                            text-xs text-tactical-text outline-none focus:border-[#06B6D4] cursor-pointer min-w-[140px] shadow-sm"
                    >
                        <option value="all">All Network Nodes</option>
                        {NODES.map((n) => (
                            <option key={n} value={n}>{n}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* ── Table ── */}
            <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.5)]">
                {/* Head */}
                <div className="grid grid-cols-[1fr_1fr_0.8fr] sm:grid-cols-[1.5fr_1.2fr_0.8fr_1.2fr_1fr_0.8fr] gap-0 bg-tactical-bg/80 border-b border-tactical-border">
                    {[
                        { key: "id" as SortKey, label: "Profile ID", mobile: true },
                        { key: "originNode" as SortKey, label: "Origin Node", mobile: true },
                        { key: "lociCount" as SortKey, label: "STR Loci", mobile: true },
                        { key: null, label: "Sample Quality", mobile: false },
                        { key: "insertedAt" as SortKey, label: "Indexed Timestamp", mobile: false },
                        { key: null, label: "Vector ID", mobile: false },
                    ].map((col) => (
                        <button
                            key={col.label}
                            onClick={() => col.key && toggleSort(col.key)}
                            disabled={!col.key}
                            className={`items-center gap-1.5 px-4 py-3.5 text-left
                                text-[9px] font-bold uppercase tracking-widest text-tactical-text-dim
                                ${col.key ? "hover:text-tactical-text cursor-pointer" : "cursor-default"}
                                ${col.mobile ? "flex" : "hidden sm:flex"}`}
                        >
                            {col.label}
                            {col.key && <SortIcon field={col.key} />}
                        </button>
                    ))}
                </div>

                {/* Body */}
                <div className="divide-y divide-tactical-border/50">
                    {pageData.map((profile, i) => {
                        const q = QUALITY_CONFIG[profile.quality];
                        return (
                            <motion.div
                                key={profile.id}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: i * 0.005 }}
                                className="grid grid-cols-[1fr_1fr_0.8fr] sm:grid-cols-[1.5fr_1.2fr_0.8fr_1.2fr_1fr_0.8fr] gap-0
                                    hover:bg-tactical-surface-elevated/60 transition-colors"
                            >
                                {/* Profile ID */}
                                <div className="flex items-center gap-2 px-4 py-3 min-w-0">
                                    <Dna className="w-3.5 h-3.5 text-[#22C55E] flex-shrink-0" />
                                    <span className="text-xs font-bold text-white truncate">
                                        {profile.id}
                                    </span>
                                </div>

                                {/* Origin Node */}
                                <div className="flex items-center gap-1.5 px-4 py-3 min-w-0">
                                    <MapPin className="w-3 h-3 text-[#06B6D4] flex-shrink-0" />
                                    <span className="text-xs text-tactical-text-muted truncate">
                                        {profile.originNode}
                                    </span>
                                </div>

                                {/* Loci Count */}
                                <div className="flex items-center px-4 py-3">
                                    <span className="text-xs font-bold tabular-nums text-[#22C55E]">
                                        {profile.lociCount}
                                    </span>
                                    <span className="text-[9px] text-tactical-text-dim ml-1">/ 20 Loci</span>
                                </div>

                                {/* Quality */}
                                <div className="hidden sm:flex items-center px-4 py-3">
                                    <span
                                        className="text-[9px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-lg border"
                                        style={{ color: q.color, background: q.bg, borderColor: q.border }}
                                    >
                                        {q.label}
                                    </span>
                                </div>

                                {/* Indexed At */}
                                <div className="hidden sm:flex items-center px-4 py-3">
                                    <span className="text-xs text-tactical-text-muted tabular-nums truncate">
                                        {profile.insertedAt}
                                    </span>
                                </div>

                                {/* Vector ID */}
                                <div className="hidden sm:flex items-center gap-1.5 px-4 py-3">
                                    <Hash className="w-3 h-3 text-[#8B5CF6] flex-shrink-0" />
                                    <span className="text-xs text-[#8B5CF6] font-bold tabular-nums">
                                        #{profile.vectorId}
                                    </span>
                                </div>
                            </motion.div>
                        );
                    })}
                </div>
            </div>

            {/* ── Pagination ── */}
            <div className="flex items-center justify-between pt-2">
                <span className="text-xs text-tactical-text-dim">
                    Showing <span className="text-tactical-text font-bold">{page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, sorted.length)}</span> of{" "}
                    <span className="text-[#06B6D4] font-bold">{sorted.length.toLocaleString()}</span> profiles
                </span>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setPage((p) => Math.max(0, p - 1))}
                        disabled={page === 0}
                        className="px-3.5 py-1.5 rounded-xl border border-tactical-border bg-tactical-surface text-xs text-tactical-text-muted
                            hover:text-white hover:border-[#06B6D4] transition-all
                            disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                        Prev
                    </button>
                    <span className="text-xs text-tactical-text-muted px-2 tabular-nums">
                        {page + 1} / {totalPages}
                    </span>
                    <button
                        onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                        disabled={page >= totalPages - 1}
                        className="px-3.5 py-1.5 rounded-xl border border-tactical-border bg-tactical-surface text-xs text-tactical-text-muted
                            hover:text-white hover:border-[#06B6D4] transition-all
                            disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                        Next
                    </button>
                </div>
            </div>

            {/* ── Footer ── */}
            <div className="flex items-center justify-between pt-3 border-t border-tactical-border/60 text-[10px] text-tactical-text-dim">
                <div className="flex items-center gap-2">
                    <Server className="w-3.5 h-3.5 text-[#06B6D4]" />
                    <span>Milvus v2.4 • IVF_FLAT Index • Dimension 384 • Distance: COSINE</span>
                </div>
                <div className="flex items-center gap-2 text-[#22C55E]">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Isolated Biometric Ledger</span>
                </div>
            </div>
        </motion.div>
    );
}
