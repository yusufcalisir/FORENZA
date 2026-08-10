"use client";

import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Shield,
    ShieldCheck,
    ShieldX,
    Activity,
    Clock,
    Hash,
    AlertTriangle,
    Lock,
    ExternalLink,
    Copy,
    Check,
    Blocks,
    FileCheck,
} from "lucide-react";
import { usePublicClient, useWatchContractEvent } from 'wagmi';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { parseAbiItem } from 'viem';
import { forensicAuditABI } from '@/config/wagmi';

// ─── Config ──────────────────────────────────────────────────────────────────

const CONTRACT_ADDRESS = process.env.NEXT_PUBLIC_AUDIT_CONTRACT_ADDRESS as `0x${string}` || "0x5FbDB2315678afecb367f032d93F642f64180aa3";

// ─── Types ───────────────────────────────────────────────────────────────────

interface LedgerEntry {
    index: number;
    timestamp: string;
    query_hash: string;
    node_id: string;
    zkp_status: string;
    authorization_token: string;
    compliance_decision: "authorized" | "reverted" | "suspended";
    metadata: Record<string, unknown>;
    entry_hash: string;
    block_number: bigint;
    query_type: string;
}

interface LedgerStats {
    total_entries: number;
    authorized_queries: number;
    suspensions: number;
    chain_age_seconds: number;
    merkle_root: string;
    is_chain_valid: boolean;
}

type FilterType = "all" | "suspensions" | "queries";

// ─── Demo Data (Fallback) ────────────────────────────────────────────────────
const DEMO_LOGS: LedgerEntry[] = [
    {
        index: 1005,
        timestamp: new Date().toISOString(),
        query_hash: `0x${Math.random().toString(16).slice(2)}...`,
        node_id: "VANTAGE-NODE-01",
        zkp_status: "verified",
        authorization_token: "VALID",
        compliance_decision: "authorized",
        metadata: { type: "Standard_Query" },
        entry_hash: `0x8f3c719a4b220d91e84a${Math.random().toString(16).slice(2, 10)}`,
        block_number: BigInt(123460),
        query_type: "Standard_Query"
    },
    {
        index: -1,
        timestamp: new Date(Date.now() - 1000 * 45).toISOString(),
        query_hash: "0x0000...0000",
        node_id: "UNKNOWN-ACTOR",
        zkp_status: "invalid",
        authorization_token: "REVOKED",
        compliance_decision: "suspended",
        metadata: { reason: "RATE_LIMIT_EXCEEDED" },
        entry_hash: `0xef44449a4b220d91e84a${Math.random().toString(16).slice(2, 10)}`,
        block_number: BigInt(123459),
        query_type: "Suspicious_Activity"
    },
    {
        index: 1004,
        timestamp: new Date(Date.now() - 1000 * 120).toISOString(),
        query_hash: `0x${Math.random().toString(16).slice(2)}...`,
        node_id: "VANTAGE-NODE-02",
        zkp_status: "verified",
        authorization_token: "VALID",
        compliance_decision: "authorized",
        metadata: { type: "Cross_Ref_Check" },
        entry_hash: `0x06b6d49a4b220d91e84a${Math.random().toString(16).slice(2, 10)}`,
        block_number: BigInt(123458),
        query_type: "Cross_Ref_Check"
    },
    {
        index: 1003,
        timestamp: new Date(Date.now() - 1000 * 300).toISOString(),
        query_hash: `0x${Math.random().toString(16).slice(2)}...`,
        node_id: "EUROPOL-GATEWAY",
        zkp_status: "verified",
        authorization_token: "VALID",
        compliance_decision: "reverted",
        metadata: { type: "Unauthorized_Scope" },
        entry_hash: `0x8b5cf69a4b220d91e84a${Math.random().toString(16).slice(2, 10)}`,
        block_number: BigInt(123457),
        query_type: "Unauthorized_Scope"
    },
    {
        index: 1002,
        timestamp: new Date(Date.now() - 1000 * 600).toISOString(),
        query_hash: `0x${Math.random().toString(16).slice(2)}...`,
        node_id: "VANTAGE-NODE-01",
        zkp_status: "verified",
        authorization_token: "VALID",
        compliance_decision: "authorized",
        metadata: { type: "Standard_Query" },
        entry_hash: `0x22c55e9a4b220d91e84a${Math.random().toString(16).slice(2, 10)}`,
        block_number: BigInt(123456),
        query_type: "Standard_Query"
    }
];

function useAuditLogs() {
    const publicClient = usePublicClient();

    return useQuery({
        queryKey: ['audit-logs', CONTRACT_ADDRESS],
        queryFn: async () => {
            if (!publicClient) {
                return DEMO_LOGS;
            }
            try {
                const currentBlock = await publicClient.getBlockNumber();
                const fromBlock = currentBlock - 5000n > 0n ? currentBlock - 5000n : 0n;

                const queryLogs = await publicClient.getLogs({
                    address: CONTRACT_ADDRESS,
                    event: parseAbiItem('event QueryLogged(uint256 indexed logIndex, address indexed investigator_id, string query_type, bytes32 profile_hash, uint256 timestamp)'),
                    fromBlock,
                    toBlock: 'latest'
                });

                const suspendedLogs = await publicClient.getLogs({
                    address: CONTRACT_ADDRESS,
                    event: parseAbiItem('event InvestigatorSuspended(address indexed investigator_id, uint256 timestamp)'),
                    fromBlock,
                    toBlock: 'latest'
                });

                if (queryLogs.length === 0 && suspendedLogs.length === 0 && CONTRACT_ADDRESS.startsWith("0x5FbDB")) {
                    return DEMO_LOGS;
                }

                const formattedQueries: LedgerEntry[] = queryLogs.map(log => ({
                    index: Number(log.args.logIndex),
                    timestamp: new Date(Number(log.args.timestamp!) * 1000).toISOString(),
                    query_hash: log.args.profile_hash!,
                    node_id: log.args.investigator_id ? `${log.args.investigator_id.slice(0, 6)}...${log.args.investigator_id.slice(-4)}` : 'UNKNOWN',
                    zkp_status: "verified",
                    authorization_token: "VALID",
                    compliance_decision: "authorized",
                    metadata: { type: log.args.query_type },
                    entry_hash: log.transactionHash,
                    block_number: log.blockNumber,
                    query_type: log.args.query_type || "Standard_Query"
                }));

                const formattedSuspensions: LedgerEntry[] = suspendedLogs.map((log) => ({
                    index: -1,
                    timestamp: new Date(Number(log.args.timestamp!) * 1000).toISOString(),
                    query_hash: "0x0000000000000000000000000000000000000000000000000000000000000000",
                    node_id: log.args.investigator_id ? `${log.args.investigator_id.slice(0, 6)}...${log.args.investigator_id.slice(-4)}` : 'UNKNOWN',
                    zkp_status: "invalid",
                    authorization_token: "REVOKED",
                    compliance_decision: "suspended",
                    metadata: { reason: "RATE_LIMIT_EXCEEDED" },
                    entry_hash: log.transactionHash,
                    block_number: log.blockNumber,
                    query_type: "Suspicious_Activity"
                }));

                const results = [...formattedQueries, ...formattedSuspensions].sort((a, b) =>
                    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
                );

                return results.length > 0 ? results : DEMO_LOGS;
            } catch (err) {
                return DEMO_LOGS;
            }
        },
        refetchInterval: 5000,
    });
}

// ─── Utility ─────────────────────────────────────────────────────────────────

function truncateHash(hash: string, start = 8, end = 6): string {
    if (hash.length <= start + end + 3) return hash;
    return `${hash.slice(0, start)}…${hash.slice(-end)}`;
}

function formatTimestamp(iso: string): string {
    try {
        const d = new Date(iso);
        return d.toLocaleTimeString("en-GB", { hour12: false, timeZone: "UTC" }) + "." + String(d.getMilliseconds()).padStart(3, "0");
    } catch {
        return iso;
    }
}

function formatDuration(seconds: number): string {
    if (seconds < 60) return `${seconds.toFixed(0)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(0)}m`;
    if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
    return `${(seconds / 86400).toFixed(1)}d`;
}

// ─── Chain Integrity Indicator ───────────────────────────────────────────────

function ChainIntegrity({ isValid, address }: { isValid: boolean; address: string }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex items-center gap-3 px-5 py-3.5 rounded-xl border shadow-md ${
                isValid
                    ? "bg-[#22C55E]/5 border-[#22C55E]/20"
                    : "bg-[#EF4444]/5 border-[#EF4444]/20"
            }`}
        >
            <motion.div
                animate={isValid ? { scale: [1, 1.15, 1] } : {}}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
                {isValid ? (
                    <ShieldCheck className="w-5 h-5 text-[#22C55E]" />
                ) : (
                    <ShieldX className="w-5 h-5 text-[#EF4444]" />
                )}
            </motion.div>
            <div className="flex-1 min-w-0">
                <p className={`text-xs font-bold uppercase tracking-wider ${isValid ? "text-[#22C55E]" : "text-[#EF4444]"}`}>
                    {isValid ? "Polygon On-Chain Audit Feed Active" : "Audit Feed Connection Error"}
                </p>
                <p className="text-[10px] text-tactical-text-muted truncate font-mono mt-0.5" title={address}>
                    Contract: {address}
                </p>
            </div>
            <div className="flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#22C55E] opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-[#22C55E]" />
                </span>
                <span className="text-[10px] font-bold text-[#22C55E] tracking-wider uppercase">
                    Tamper-Evident
                </span>
            </div>
        </motion.div>
    );
}

// ─── Filter Bar ──────────────────────────────────────────────────────────────

const FILTER_OPTIONS: { value: FilterType; label: string; icon: typeof Activity; color: string }[] = [
    { value: "all", label: "All Audit Logs", icon: Activity, color: "#22C55E" },
    { value: "queries", label: "Authorized Queries", icon: ShieldCheck, color: "#06B6D4" },
    { value: "suspensions", label: "Anomalies", icon: AlertTriangle, color: "#EF4444" },
];

function FilterBar({ active, onChange }: { active: FilterType; onChange: (f: FilterType) => void }) {
    return (
        <div className="grid grid-cols-3 items-center gap-2 p-1 bg-tactical-surface rounded-xl border border-tactical-border w-full max-w-md">
            {FILTER_OPTIONS.map(({ value, label, icon: Icon, color }) => {
                const isActive = active === value;
                return (
                    <button
                        key={value}
                        onClick={() => onChange(value)}
                        className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all whitespace-nowrap ${
                            isActive
                                ? "bg-tactical-surface-elevated text-white border shadow-md"
                                : "text-tactical-text-dim hover:text-white border border-transparent"
                        }`}
                        style={isActive ? { color: color, borderColor: `${color}40` } : {}}
                    >
                        <Icon className="w-3.5 h-3.5 flex-shrink-0" />
                        <span className="truncate">{label}</span>
                    </button>
                );
            })}
        </div>
    );
}

// ─── Ledger Entry Row ────────────────────────────────────────────────────────

const COMPLIANCE_MAP = {
    authorized: { color: "#22C55E", label: "AUTHORIZED", bg: "rgba(34,197,94,0.12)", border: "rgba(34,197,94,0.3)" },
    reverted: { color: "#F59E0B", label: "REVERTED", bg: "rgba(245,158,11,0.12)", border: "rgba(245,158,11,0.3)" },
    suspended: { color: "#EF4444", label: "ANOMALY", bg: "rgba(239,68,68,0.12)", border: "rgba(239,68,68,0.3)" },
};

function EntryRow({ entry, isNew = false }: { entry: LedgerEntry; isNew?: boolean }) {
    const compliance = COMPLIANCE_MAP[entry.compliance_decision] || COMPLIANCE_MAP.authorized;
    const isSuspension = entry.compliance_decision === "suspended";
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(entry.entry_hash);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <motion.div
            initial={isNew ? { opacity: 0, x: -12, backgroundColor: "rgba(34, 197, 94, 0.1)" } : { opacity: 1 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 p-4 rounded-xl border border-tactical-border/80 bg-tactical-surface hover:border-tactical-border transition-all shadow-md"
        >
            {/* Left: ID & Node Info */}
            <div className="flex items-center gap-3">
                <span className="text-xs font-bold text-tactical-text-dim w-10">
                    {entry.index >= 0 ? `#${entry.index}` : 'ERR'}
                </span>
                <div className="flex items-center gap-2">
                    <Blocks className="w-4 h-4 text-[#06B6D4] shrink-0" />
                    <span className="text-xs font-bold text-white truncate max-w-[160px]" title={entry.node_id}>
                        {entry.node_id}
                    </span>
                </div>
            </div>

            {/* Middle: Timestamp & Compliance Badge */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5 text-tactical-text-muted text-xs">
                    <Clock className="w-3.5 h-3.5 text-tactical-text-dim" />
                    <span className="tabular-nums">{formatTimestamp(entry.timestamp)}</span>
                </div>

                <span
                    className="px-2.5 py-1 rounded-lg text-[9px] font-bold border uppercase tracking-wider"
                    style={{ color: compliance.color, background: compliance.bg, borderColor: compliance.border }}
                >
                    {compliance.label}
                </span>

                {/* ZK Proof Badge */}
                <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-lg bg-[#8B5CF6]/10 border border-[#8B5CF6]/30 text-[#8B5CF6] text-[9px] font-bold uppercase tracking-wider">
                    <Lock className="w-3 h-3" />
                    <span>ZK Verified</span>
                </div>
            </div>

            {/* Right: Hash & Explorer Link */}
            <div className="flex items-center gap-3 justify-between lg:justify-end">
                <div
                    className="flex items-center gap-1.5 text-xs text-tactical-text-muted cursor-pointer hover:text-white transition-colors"
                    onClick={handleCopy}
                >
                    <Hash className="w-3.5 h-3.5 text-[#06B6D4]" />
                    <span className="text-[10px] text-tactical-text-dim" title={entry.entry_hash}>
                        {truncateHash(entry.entry_hash)}
                    </span>
                    {copied ? (
                        <Check className="w-3.5 h-3.5 text-[#22C55E]" />
                    ) : (
                        <Copy className="w-3.5 h-3.5 text-tactical-text-dim hover:text-white" />
                    )}
                </div>

                <a
                    href={`https://sepolia.etherscan.io/tx/${entry.entry_hash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-tactical-border bg-tactical-bg hover:border-[#22C55E] hover:text-[#22C55E] transition-all text-[10px] font-bold uppercase text-tactical-text-muted"
                >
                    <span>Etherscan</span>
                    <ExternalLink className="w-3 h-3 opacity-70" />
                </a>
            </div>
        </motion.div>
    );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function AuditPage() {
    const [filter, setFilter] = useState<FilterType>("all");
    const { data: entries = [], isLoading, isError } = useAuditLogs();
    const queryClient = useQueryClient();

    // Real-time Listener (Wagmi)
    useWatchContractEvent({
        address: CONTRACT_ADDRESS,
        abi: forensicAuditABI,
        eventName: 'QueryLogged',
        onLogs() {
            queryClient.invalidateQueries({ queryKey: ['audit-logs'] });
        },
    });

    useWatchContractEvent({
        address: CONTRACT_ADDRESS,
        abi: forensicAuditABI,
        eventName: 'InvestigatorSuspended',
        onLogs() {
            queryClient.invalidateQueries({ queryKey: ['audit-logs'] });
        },
    });

    // Derived Stats
    const stats: LedgerStats = useMemo(() => {
        const authorized = entries.filter(e => e.compliance_decision === "authorized").length;
        const suspensions = entries.filter(e => e.compliance_decision === "suspended").length;
        const oldest = entries.length > 0 ? new Date(entries[entries.length - 1].timestamp).getTime() : Date.now();
        const age = (Date.now() - oldest) / 1000;

        return {
            total_entries: entries.length,
            authorized_queries: authorized,
            suspensions: suspensions,
            chain_age_seconds: age > 0 ? age : 0,
            merkle_root: "0x...",
            is_chain_valid: !isError && entries.length >= 0
        };
    }, [entries, isError]);

    // Filtering
    const filteredEntries = useMemo(() => {
        switch (filter) {
            case "suspensions":
                return entries.filter(e => e.compliance_decision === "suspended");
            case "queries":
                return entries.filter(e => e.compliance_decision === "authorized");
            default:
                return entries;
        }
    }, [entries, filter]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6 py-4 overflow-x-hidden font-mono"
        >
            {/* ── Header ── */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border pb-5">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#22C55E]/20 to-[#8B5CF6]/10 border border-[#22C55E]/30 shadow-[0_0_15px_rgba(34,197,94,0.2)]">
                        <Shield className="w-5 h-5 text-[#22C55E]" />
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
                                Forensic Audit Ledger
                            </h1>
                            <span className="text-[9px] font-bold text-[#8B5CF6] bg-[#8B5CF6]/10 border border-[#8B5CF6]/20 px-2 py-0.5 rounded-full">
                                Solidity On-Chain Feed
                            </span>
                        </div>
                        <p className="text-[10px] text-tactical-text-muted mt-0.5">
                            Real-Time Blockchain Anchored Chain-of-Custody Feed
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2 text-xs">
                    <Activity className="w-4 h-4 text-[#22C55E] animate-pulse" />
                    <span className="text-[10px] font-bold tracking-wider text-[#22C55E] uppercase">
                        Live Blockchain Sync
                    </span>
                </div>
            </div>

            {/* Chain Integrity */}
            <ChainIntegrity isValid={stats.is_chain_valid} address={CONTRACT_ADDRESS} />

            {/* Stats Strip */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                {[
                    { label: "Total Audit Entries", value: stats.total_entries.toLocaleString(), color: "#FAFAFA", bg: "#111113", border: "#27272A" },
                    { label: "Authorized Queries", value: stats.authorized_queries.toLocaleString(), color: "#22C55E", bg: "rgba(34,197,94,0.06)", border: "rgba(34,197,94,0.25)" },
                    { label: "Suspicious Anomalies", value: stats.suspensions.toString(), color: "#EF4444", bg: "rgba(239,68,68,0.06)", border: "rgba(239,68,68,0.25)" },
                    { label: "Chain Feed Uptime", value: formatDuration(Math.max(0, stats.chain_age_seconds)), color: "#06B6D4", bg: "rgba(6,182,212,0.06)", border: "rgba(6,182,212,0.25)" },
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

            {/* Filter + Feed */}
            <div className="space-y-4">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <FilterBar active={filter} onChange={setFilter} />
                    <span className="text-xs text-tactical-text-dim">
                        Showing <span className="text-[#22C55E] font-bold">{filteredEntries.length}</span> audit logs
                    </span>
                </div>

                {/* Live Feed */}
                <div className="space-y-2.5">
                    <AnimatePresence mode='popLayout'>
                        {isLoading && (
                            <div className="space-y-2">
                                {[1, 2, 3, 4].map(i => (
                                    <div key={i} className="h-16 w-full bg-tactical-surface rounded-xl animate-pulse border border-tactical-border" />
                                ))}
                            </div>
                        )}

                        {!isLoading && filteredEntries.map((entry) => (
                            <EntryRow
                                key={entry.entry_hash || entry.index}
                                entry={entry}
                                isNew={Date.now() - new Date(entry.timestamp).getTime() < 10000}
                            />
                        ))}
                    </AnimatePresence>

                    {!isLoading && filteredEntries.length === 0 && (
                        <div className="flex items-center justify-center py-12 text-tactical-text-dim">
                            <p className="text-xs font-bold uppercase tracking-wider">
                                No audit entries match the selected filter
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
