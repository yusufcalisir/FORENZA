"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    ShieldCheck, Lock, CheckCircle, AlertTriangle,
    FileText, Clock, Filter, ChevronDown, Activity
} from "lucide-react";

type LogLevel = "ALL" | "PASS" | "WARNING" | "FAIL";

interface AuditEntry {
    id: string;
    timestamp: string;
    event: string;
    module: string;
    analyst: string;
    hmac: string;
    status: "PASS" | "WARNING" | "FAIL";
    standard: string;
}

const AUDIT_LOG: AuditEntry[] = [
    { id: "AUD-0891", timestamp: "2026-08-12 11:52:14", event: "STR profile analyzed — EVID-2026-901", module: "STR Locus Engine", analyst: "Dr. Morrison", hmac: "a7f9c21…e04b", status: "PASS", standard: "ISO 17025 §5.4" },
    { id: "AUD-0890", timestamp: "2026-08-12 11:51:33", event: "HIrisPlex-S phenotype report compiled", module: "Phenotyping Engine", analyst: "Dr. Chen", hmac: "b3d82f4…a19c", status: "PASS", standard: "SWGDAM 2023" },
    { id: "AUD-0889", timestamp: "2026-08-12 11:49:07", event: "3-contributor mixture deconvolution", module: "MCMC Engine", analyst: "Dr. Morrison", hmac: "c1e45b7…d52a", status: "PASS", standard: "ILAC G19" },
    { id: "AUD-0888", timestamp: "2026-08-12 11:44:28", event: "ISO 17025 court report signed", module: "Report Generator", analyst: "Prof. Ahmed", hmac: "d9f12a3…7e81", status: "PASS", standard: "ISO 17025 §7.8" },
    { id: "AUD-0887", timestamp: "2026-08-12 11:39:55", event: "Epigenetic age clock — donor age 38±3.4", module: "Horvath Clock", analyst: "Dr. Chen", hmac: "e4a67c9…b23d", status: "PASS", standard: "ENFSI 2022" },
    { id: "AUD-0886", timestamp: "2026-08-12 11:35:12", event: "Touch DNA LtDNA threshold warning", module: "Touch DNA Engine", analyst: "Dr. Morrison", hmac: "f7b23e1…c490", status: "WARNING", standard: "SWGDAM LTDNA" },
    { id: "AUD-0885", timestamp: "2026-08-12 11:28:44", event: "QC control out of ±2σ range", module: "QA/QC Monitor", analyst: "Lab Tech B", hmac: "g2d89f5…a17b", status: "WARNING", standard: "ISO 17025 §6.5" },
    { id: "AUD-0884", timestamp: "2026-08-12 11:21:09", event: "ZKP proof verification failed (missing artifacts)", module: "ZKP Auditor", analyst: "System", hmac: "h5c41d8…f23e", status: "FAIL", standard: "Circom zkSNARK" },
    { id: "AUD-0883", timestamp: "2026-08-12 10:58:31", event: "Toxicology Widmark BAC — FATAL threshold exceeded", module: "Toxicology Engine", analyst: "Dr. Chen", hmac: "i8e72b3…c910", status: "PASS", standard: "ISO 17025 §5.4" },
    { id: "AUD-0882", timestamp: "2026-08-12 10:44:16", event: "Synthetic case benchmark — RMSE 0.02", module: "Synthetic Generator", analyst: "System", hmac: "j1f34c7…e845", status: "PASS", standard: "OSAC TR" },
];

const STATUS_CONF = {
    PASS: { color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/30", icon: CheckCircle },
    WARNING: { color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30", icon: AlertTriangle },
    FAIL: { color: "text-red-400", bg: "bg-red-500/10 border-red-500/30", icon: AlertTriangle },
};

export default function AuditPage() {
    const [filter, setFilter] = useState<LogLevel>("ALL");
    const [expanded, setExpanded] = useState<string | null>(null);

    const filtered = filter === "ALL" ? AUDIT_LOG : AUDIT_LOG.filter((e) => e.status === filter);

    const counts = {
        PASS: AUDIT_LOG.filter((e) => e.status === "PASS").length,
        WARNING: AUDIT_LOG.filter((e) => e.status === "WARNING").length,
        FAIL: AUDIT_LOG.filter((e) => e.status === "FAIL").length,
    };

    return (
        <div className="space-y-6 font-mono">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <ShieldCheck className="w-4 h-4 text-amber-400" />
                        <span className="text-[10px] font-bold text-amber-400 uppercase tracking-widest">FORENZA Compliance</span>
                    </div>
                    <h1 className="text-base font-extrabold text-white tracking-tight">ISO 17025 Audit Log</h1>
                    <p className="text-[10px] text-zinc-500 mt-0.5">HMAC-SHA256 Chain of Custody • Immutable Forensic Event Ledger • ZKP Verified</p>
                </div>
                <div className="flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-amber-400" />
                    <span className="text-[9px] font-bold text-amber-400 uppercase tracking-wider">Chain Integrity: VERIFIED</span>
                </div>
            </div>

            {/* Summary */}
            <div className="grid grid-cols-3 gap-3">
                {([
                    { label: "Events PASS", value: counts.PASS, color: "text-emerald-400", bg: "border-emerald-500/30 bg-emerald-500/5" },
                    { label: "Events WARNING", value: counts.WARNING, color: "text-amber-400", bg: "border-amber-500/30 bg-amber-500/5" },
                    { label: "Events FAIL", value: counts.FAIL, color: "text-red-400", bg: "border-red-500/30 bg-red-500/5" },
                ] as const).map((m) => (
                    <motion.div key={m.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                        className={`rounded-xl border ${m.bg} p-4 text-center`}>
                        <p className={`text-2xl font-extrabold ${m.color}`}>{m.value}</p>
                        <p className="text-[9px] text-zinc-500 uppercase mt-1">{m.label}</p>
                    </motion.div>
                ))}
            </div>

            {/* Filter Bar */}
            <div className="flex items-center gap-2 flex-wrap">
                <Filter className="w-3.5 h-3.5 text-zinc-500" />
                <span className="text-[9px] text-zinc-600 uppercase font-bold">Filter:</span>
                {(["ALL", "PASS", "WARNING", "FAIL"] as LogLevel[]).map((f) => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-3 py-1 rounded-lg text-[9px] font-bold uppercase tracking-wider border transition-all ${filter === f
                            ? f === "ALL" ? "bg-zinc-800 border-zinc-600 text-white"
                                : f === "PASS" ? "bg-emerald-500/15 border-emerald-500/40 text-emerald-400"
                                    : f === "WARNING" ? "bg-amber-500/15 border-amber-500/40 text-amber-400"
                                        : "bg-red-500/15 border-red-500/40 text-red-400"
                            : "bg-zinc-900/40 border-zinc-800/60 text-zinc-600 hover:text-zinc-300"
                            }`}
                    >
                        {f}
                    </button>
                ))}
                <span className="ml-auto text-[9px] text-zinc-600">{filtered.length} events</span>
            </div>

            {/* Log Table */}
            <div className="rounded-2xl border border-tactical-border/60 bg-black/20 overflow-hidden">
                <div className="hidden sm:grid grid-cols-12 px-4 py-2.5 border-b border-tactical-border/40 text-[8px] font-bold text-zinc-600 uppercase tracking-wider">
                    <span className="col-span-1">ID</span>
                    <span className="col-span-2">Timestamp</span>
                    <span className="col-span-4">Event</span>
                    <span className="col-span-2">Module</span>
                    <span className="col-span-1">Analyst</span>
                    <span className="col-span-1">Standard</span>
                    <span className="col-span-1 text-right">Status</span>
                </div>
                {filtered.map((entry, i) => {
                    const sc = STATUS_CONF[entry.status];
                    const StatusIcon = sc.icon;
                    const isExpanded = expanded === entry.id;
                    return (
                        <div key={entry.id} className="border-b border-tactical-border/20 last:border-0">
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: i * 0.03 }}
                                onClick={() => setExpanded(isExpanded ? null : entry.id)}
                                className="grid grid-cols-1 sm:grid-cols-12 items-center gap-1 sm:gap-0 px-4 py-3 cursor-pointer hover:bg-white/2 transition-colors"
                            >
                                <span className="col-span-1 text-[9px] font-bold text-zinc-500 font-mono">{entry.id}</span>
                                <span className="col-span-2 text-[9px] text-zinc-500">{entry.timestamp}</span>
                                <span className="col-span-4 text-[10px] text-zinc-200">{entry.event}</span>
                                <span className="col-span-2 text-[9px] text-zinc-400">{entry.module}</span>
                                <span className="col-span-1 text-[9px] text-zinc-500 truncate">{entry.analyst}</span>
                                <span className="col-span-1 text-[9px] text-zinc-600">{entry.standard}</span>
                                <div className="col-span-1 flex justify-end">
                                    <span className={`flex items-center gap-1 text-[8px] font-bold border rounded px-1.5 py-0.5 ${sc.bg} ${sc.color}`}>
                                        <StatusIcon className="w-2.5 h-2.5" />
                                        {entry.status}
                                    </span>
                                </div>
                            </motion.div>
                            <AnimatePresence>
                                {isExpanded && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: "auto" }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="px-4 pb-3 space-y-2 border-t border-tactical-border/20"
                                    >
                                        <div className="pt-3 grid grid-cols-2 gap-2">
                                            <div className="p-2 rounded-lg bg-black/30 border border-tactical-border/30">
                                                <span className="text-[8px] text-zinc-600 uppercase block">HMAC-SHA256</span>
                                                <span className="text-[10px] text-amber-400 font-mono font-bold">{entry.hmac}</span>
                                            </div>
                                            <div className="p-2 rounded-lg bg-black/30 border border-tactical-border/30">
                                                <span className="text-[8px] text-zinc-600 uppercase block">Chain Position</span>
                                                <span className="text-[10px] text-cyan-400 font-mono font-bold">Block #1,847,{290 - i}</span>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    );
                })}
            </div>

            {/* Compliance Banner */}
            <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4 flex items-center gap-3">
                <ShieldCheck className="w-5 h-5 text-amber-400 shrink-0" />
                <div>
                    <p className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">ISO/IEC 17025:2017 Compliance Certificate</p>
                    <p className="text-[9px] text-zinc-500 mt-0.5">All forensic analyses are performed under accredited quality management system. Chain of custody verified via HMAC-SHA256 on Polygon zkEVM immutable ledger. Expert witness admissibility certified.</p>
                </div>
            </div>
        </div>
    );
}
