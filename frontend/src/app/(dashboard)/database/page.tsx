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
    FlaskConical,
} from "lucide-react";
import { useIngestStore, SAMPLE_CASE_EU, SAMPLE_CASE_AA } from "@/store/ingestStore";
import { useForensicCaseStore } from "@/store/forensicCaseStore";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import ActiveProfileBanner from "@/components/common/ActiveProfileBanner";
import FederatedNetworkPanel, { LAB_NODES } from "@/components/analysis/FederatedNetworkPanel";
import {
    calculateLociQuality,
    getLociQualityBadgeLabel,
    PROFILE_QUALITY_CONFIG,
    ProfileQualityTier,
} from "@/lib/forensicStatusUtils";

// ─── Types ───────────────────────────────────────────────────────────────────

interface ProfileRecord {
    id: string;
    originNode: string;
    lociCount: number;
    insertedAt: string;
    quality: ProfileQualityTier;
    vectorId: number;
    sampleType?: "EU" | "AA" | "CUSTOM";
}

// ─── Shared Federated Node Registry (Single Source of Truth) ──────────────────

const NODES = LAB_NODES.map((n) => n.name);

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
        quality: calculateLociQuality(SAMPLE_CASE_EU.markerCount),
        vectorId: 100001,
        sampleType: "EU",
    });

    profiles.push({
        id: SAMPLE_CASE_AA.profileId,
        originNode: SAMPLE_CASE_AA.nodeId,
        lociCount: SAMPLE_CASE_AA.markerCount,
        insertedAt: "2026-08-12 18:32",
        quality: calculateLociQuality(SAMPLE_CASE_AA.markerCount),
        vectorId: 100002,
        sampleType: "AA",
    });

    for (let i = 2; i < count; i++) {
        const loci = Math.floor(rand() * 15) + 10;
        const quality = calculateLociQuality(loci);
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

// ─── Sort Types ──────────────────────────────────────────────────────────────

type SortKey = "id" | "originNode" | "lociCount" | "insertedAt";
type SortDir = "asc" | "desc";

export default function DatabasePage() {
    const { activeProfile, setInspectorOpen, loadSampleCaseEU, loadSampleCaseAA } = useIngestStore();
    const { lang } = useSaasLanguage();
    const isTr = lang === "tr";

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
                title={
                    activeView === "database"
                        ? (isTr ? "Adli DNA Veritabanı" : "Forensic DNA Database")
                        : (isTr ? "Federe Delil Ağı" : "Federated Evidence Network")
                }
                subtitle={
                    activeView === "database"
                        ? (isTr
                            ? "Milvus Vektör Profil Kayıt Defteri • 24 Genişletilmiş STR Lokusu & 55 AIM SNP • HMAC İmzalı"
                            : "Milvus Vector Profile Registry • 24 Extended Forensic STR Loci & 55 AIM SNPs • HMAC Hash Sealed")
                        : (isTr
                            ? "Polygon zkEVM Dağıtık Düğüm Defteri • Uçtan Uca Fikir Birliği • Homomorfik Sorgulama"
                            : "Polygon zkEVM Distributed Node Registry • Peer-to-Peer Consensus • Homomorphic Query")
                }
                badge={
                    activeView === "database"
                        ? (isTr ? "KOLEKSİYON: STR_PROFİLLERİ" : "COLLECTION: STR_PROFILES")
                        : (isTr ? "FEDERASYON: FAAL" : "FEDERATION: ACTIVE")
                }
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
                    <span>{isTr ? "DNA Veritabanı Kayıt Defteri" : "DNA Database Registry"}</span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                        {(stats?.total ?? 0).toLocaleString()}
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
                    <span>{isTr ? "Federe Laboratuvar Ağı" : "Federated Lab Network"}</span>
                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                        {stats?.uniqueNodes ?? 0} {isTr ? "Düğüm" : "Nodes"}
                    </span>
                </button>
            </div>

            {activeView === "network" ? (
                <FederatedNetworkPanel />
            ) : (
                <>
                    {/* ── ACTIVE DNA PROFILE BANNER & FEATURE INSPECTOR ── */}
                    <ActiveProfileBanner />

                    {/* ── DEMO DATA Transparency Banner ── */}
                    <div className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 py-3 rounded-xl border border-amber-500/30 bg-amber-500/5 text-[10px] font-mono">
                        <div className="flex items-center gap-2.5">
                            <FlaskConical className="w-4 h-4 text-amber-400 shrink-0" />
                            <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 shrink-0 uppercase tracking-wider">
                                {isTr ? "DEMO VERİSİ" : "DEMO DATA"}
                            </span>
                            <p className="text-zinc-400 leading-relaxed">
                                {isTr ? (
                                    <>
                                        Bu kayıt defteri, eğitim ve simülasyon amacıyla oluşturulmuş{" "}
                                        <strong className="text-amber-300">{(stats?.total ?? 0).toLocaleString()} sentetik profili</strong>{" "}
                                        içerir. Öne çıkan 2 vaka (EU, AA) gerçek kalibrasyon ölçütleridir. Hiçbir gerçek adli DNA verisi saklanmaz veya iletilmez.
                                    </>
                                ) : (
                                    <>
                                        This registry displays{" "}
                                        <strong className="text-amber-300">{(stats?.total ?? 0).toLocaleString()} deterministically seeded synthetic profiles</strong>{" "}
                                        generated for demonstration and training purposes. The 2 featured cases (EU, AA) are real calibration benchmarks.
                                        No actual forensic DNA records are stored or transmitted.
                                    </>
                                )}
                            </p>
                        </div>
                        <span className="text-[9px] font-bold text-amber-400/70 shrink-0 whitespace-nowrap hidden lg:inline-block">
                            {isTr ? "Sentetik RNG • Adli Olarak İnert" : "Seeded RNG • Forensically Inert"}
                        </span>
                    </div>

                    {/* ── Bio-Forensic Stats Strip ── */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                        {[
                            { label: isTr ? "Toplam Profil" : "Total Profiles", value: (stats?.total ?? 0).toLocaleString(), color: "#FAFAFA", bg: "#111113", border: "#27272A" },
                            { label: isTr ? "Tam Profil (24 Lokus)" : "Complete (24 Loci)", value: (stats?.complete ?? 0).toLocaleString(), color: "#22C55E", bg: "rgba(34,197,94,0.06)", border: "rgba(34,197,94,0.25)" },
                            { label: isTr ? "Kısmi Profil (14-23 Lokus)" : "Partial (14-23 Loci)", value: (stats?.partial ?? 0).toLocaleString(), color: "#06B6D4", bg: "rgba(6,182,212,0.06)", border: "rgba(6,182,212,0.25)" },
                            { label: isTr ? "Bozulmuş Profil (<14 Lokus)" : "Degraded (<14 Loci)", value: (stats?.degraded ?? 0).toLocaleString(), color: "#EF4444", bg: "rgba(239,68,68,0.06)", border: "rgba(239,68,68,0.25)" },
                            { label: isTr ? "Aktif Ağ Düğümleri" : "Active Network Nodes", value: (stats?.uniqueNodes ?? 0).toString(), color: "#8B5CF6", bg: "rgba(139,92,246,0.06)", border: "rgba(139,92,246,0.25)" },
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
                                placeholder={isTr ? "Profil Kimliği (örn. CASE-2026-EU) veya Düğüme göre ara..." : "Search by Profile ID (e.g. CASE-2026-EU) or Node..."}
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
                                    <option value="all">{isTr ? `TÜM KAYNAK DÜĞÜMLERİ (${stats.uniqueNodes})` : `ALL ORIGIN NODES (${stats.uniqueNodes})`}</option>
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
                                {isTr ? "Sıfırla" : "Reset"}
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
                                                <span>{isTr ? "Profil Kimliği" : "Profile ID"}</span>
                                                <SortIcon field="id" />
                                            </div>
                                        </th>
                                        <th className="py-3 px-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("originNode")}>
                                            <div className="flex items-center gap-1.5">
                                                <span>{isTr ? "Kaynak Düğüm" : "Origin Node"}</span>
                                                <SortIcon field="originNode" />
                                            </div>
                                        </th>
                                        <th className="py-3 px-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("lociCount")}>
                                            <div className="flex items-center gap-1.5">
                                                <span>{isTr ? "Lokus Sayısı" : "Loci Count"}</span>
                                                <SortIcon field="lociCount" />
                                            </div>
                                        </th>
                                        <th className="py-3 px-4">{isTr ? "Kalite Durumu" : "Quality Status"}</th>
                                        <th className="py-3 px-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("insertedAt")}>
                                            <div className="flex items-center gap-1.5">
                                                <span>{isTr ? "Zaman Damgası" : "Timestamp"}</span>
                                                <SortIcon field="insertedAt" />
                                            </div>
                                        </th>
                                        <th className="py-3 px-4 text-right">{isTr ? "İşlemler" : "Actions"}</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-tactical-border/50 text-tactical-text">
                                    {pageData.length === 0 ? (
                                        <tr>
                                            <td colSpan={6} className="py-12 text-center text-tactical-text-dim">
                                                <Dna className="w-8 h-8 mx-auto mb-2 text-tactical-text-dim opacity-30" />
                                                <p className="text-xs">{isTr ? "Eşleşen DNA profili bulunamadı." : "No matching DNA profiles found."}</p>
                                                <p className="text-[10px] text-tactical-text-dim mt-1">{isTr ? "Filtreleri veya arama terimlerini sıfırlamayı deneyin." : "Try clearing filters or search queries."}</p>
                                            </td>
                                        </tr>
                                    ) : (
                                        pageData.map((p) => {
                                            const q = PROFILE_QUALITY_CONFIG[p.quality];
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
                                                            {getLociQualityBadgeLabel(p.lociCount, 24)}
                                                        </span>
                                                    </td>
                                                    <td className="py-3 px-4 text-tactical-text-dim text-[11px]">
                                                        {p.insertedAt}
                                                    </td>
                                                    <td className="py-3 px-4 text-right">
                                                        <div className="flex items-center justify-end gap-1.5">
                                                            {p.sampleType === "EU" ? (
                                                                <button
                                                                    onClick={() => {
                                                                        loadSampleCaseEU();
                                                                        useForensicCaseStore.getState().selectCase(SAMPLE_CASE_EU.profileId);
                                                                    }}
                                                                    className="px-2 py-1 rounded bg-[#06B6D4]/15 border border-[#06B6D4]/30 text-[#06B6D4] hover:bg-[#06B6D4]/25 text-[10px] font-bold transition-all cursor-pointer"
                                                                >
                                                                    {isTr ? "EU Yükle" : "Load EU"}
                                                                </button>
                                                            ) : p.sampleType === "AA" ? (
                                                                <button
                                                                    onClick={() => {
                                                                        loadSampleCaseAA();
                                                                        useForensicCaseStore.getState().selectCase(SAMPLE_CASE_AA.profileId);
                                                                    }}
                                                                    className="px-2 py-1 rounded bg-purple-500/15 border border-purple-500/30 text-purple-400 hover:bg-purple-500/25 text-[10px] font-bold transition-all cursor-pointer"
                                                                >
                                                                    {isTr ? "AA Yükle" : "Load AA"}
                                                                </button>
                                                            ) : null}
                                                            <button
                                                                onClick={() => setInspectorOpen(true)}
                                                                className="px-2 py-1 rounded bg-tactical-surface-dark border border-tactical-border hover:border-[#06B6D4] text-tactical-text-muted hover:text-white text-[10px] transition-all flex items-center gap-1 cursor-pointer"
                                                                title={isTr ? "Değişmez Vektörleri İncele" : "Inspect Invariant Vectors"}
                                                            >
                                                                <Eye className="w-3 h-3" />
                                                                <span>{isTr ? "İncele" : "Inspect"}</span>
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
                                {isTr ? (
                                    <>
                                        Toplam <span className="text-white font-bold">{(filtered?.length ?? 0).toLocaleString()}</span> kayıttan{" "}
                                        <span className="text-white font-bold">{filtered?.length === 0 ? 0 : page * PAGE_SIZE + 1}</span> -{" "}
                                        <span className="text-white font-bold">{Math.min((page + 1) * PAGE_SIZE, filtered?.length ?? 0)}</span> arası gösteriliyor
                                    </>
                                ) : (
                                    <>
                                        Showing <span className="text-white font-bold">{filtered?.length === 0 ? 0 : page * PAGE_SIZE + 1}</span> to{" "}
                                        <span className="text-white font-bold">{Math.min((page + 1) * PAGE_SIZE, filtered?.length ?? 0)}</span> of{" "}
                                        <span className="text-white font-bold">{(filtered?.length ?? 0).toLocaleString()}</span> entries
                                    </>
                                )}
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                                    disabled={page === 0}
                                    className="px-3.5 py-1.5 rounded-xl border border-tactical-border bg-tactical-surface text-xs text-tactical-text-muted
                                        hover:text-white hover:border-[#06B6D4] transition-all
                                        disabled:opacity-30 disabled:cursor-not-allowed font-mono cursor-pointer"
                                >
                                    {isTr ? "Önceki" : "Previous"}
                                </button>
                                <span className="px-2 text-tactical-text">
                                    {isTr ? `Sayfa ${page + 1} / ${Math.max(1, totalPages)}` : `Page ${page + 1} of ${Math.max(1, totalPages)}`}
                                </span>
                                <button
                                    onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                                    disabled={page >= totalPages - 1}
                                    className="px-3.5 py-1.5 rounded-xl border border-tactical-border bg-tactical-surface text-xs text-tactical-text-muted
                                        hover:text-white hover:border-[#06B6D4] transition-all
                                        disabled:opacity-30 disabled:cursor-not-allowed font-mono cursor-pointer"
                                >
                                    {isTr ? "Sonraki" : "Next"}
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
                                <span className="font-bold uppercase tracking-wider whitespace-nowrap">
                                    {isTr ? "İzole Biyometrik Defter" : "Isolated Biometric Ledger"}
                                </span>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </motion.div>
    );
}
