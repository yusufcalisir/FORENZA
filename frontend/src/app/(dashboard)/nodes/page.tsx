"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
    Network, Activity, Server, Cpu, Lock, Search, Zap,
    CheckCircle, AlertTriangle, Globe, Radio, Shield,
    Database, GitGraph, ChevronRight
} from "lucide-react";

interface LabNode {
    id: string;
    name: string;
    type: string;
    status: "ONLINE" | "SYNCING" | "DEGRADED";
    pingMs: number;
    profilesCount: number;
    location: string;
    lastBlock: string;
    iso: boolean;
}

const LAB_NODES: LabNode[] = [
    { id: "node-01", name: "FORENSIC-LAB-ALPHA", type: "Central Reference Laboratory", status: "ONLINE", pingMs: 12, profilesCount: 14850, location: "Sector 1 Reference Hub", lastBlock: "0x89f2…c01a", iso: true },
    { id: "node-02", name: "DISTRICT-DNA-LAB-01", type: "Regional Pathology Node", status: "ONLINE", pingMs: 18, profilesCount: 8920, location: "District Medical Registry", lastBlock: "0x44a1…e9b2", iso: true },
    { id: "node-03", name: "CENTRAL-GENOMICS-NODE", type: "High-Throughput Sequencing", status: "ONLINE", pingMs: 9, profilesCount: 32100, location: "Genomics Intelligence Unit", lastBlock: "0xf17d…771c", iso: true },
    { id: "node-04", name: "BORDER-FORENSICS-NODE", type: "Field Collection Point", status: "ONLINE", pingMs: 28, profilesCount: 3420, location: "Port Authority Lab", lastBlock: "0x2b91…4d7f", iso: false },
    { id: "node-05", name: "COLD-CASE-ARCHIVE-NODE", type: "Historical Evidence Archive", status: "SYNCING", pingMs: 45, profilesCount: 92500, location: "National Archive Vault", lastBlock: "0xa3c2…9f1e", iso: true },
    { id: "node-06", name: "TOXICOLOGY-HUB-NODE", type: "Toxicology Reference Lab", status: "ONLINE", pingMs: 14, profilesCount: 7200, location: "Forensic Chemistry Division", lastBlock: "0x6e5b…c782", iso: true },
    { id: "node-07", name: "MOBILE-LAB-UNIT-01", type: "Rapid Deployment Kit", status: "DEGRADED", pingMs: 112, profilesCount: 180, location: "Field Operations — Active", lastBlock: "0xb8d4…e043", iso: false },
];

const STATUS_CONFIG = {
    ONLINE: { color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/30", dot: "bg-emerald-400", label: "ONLINE" },
    SYNCING: { color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30", dot: "bg-amber-400 animate-pulse", label: "SYNCING" },
    DEGRADED: { color: "text-red-400", bg: "bg-red-500/10 border-red-500/30", dot: "bg-red-400", label: "DEGRADED" },
};

export default function NodesPage() {
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedNode, setSelectedNode] = useState<LabNode | null>(null);

    const filtered = LAB_NODES.filter((n) =>
        n.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        n.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        n.location.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const online = LAB_NODES.filter((n) => n.status === "ONLINE").length;
    const totalProfiles = LAB_NODES.reduce((s, n) => s + n.profilesCount, 0);

    return (
        <div className="space-y-6 font-mono">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <Network className="w-4 h-4 text-purple-400" />
                        <span className="text-[10px] font-bold text-purple-400 uppercase tracking-widest">FORENZA Federated Network</span>
                    </div>
                    <h1 className="text-base font-extrabold text-white tracking-tight">Distributed Forensic Node Registry</h1>
                    <p className="text-[10px] text-zinc-500 mt-0.5">Polygon zkEVM • Peer-to-Peer Evidence Sync • Homomorphic Query</p>
                </div>
                <div className="flex items-center gap-2">
                    <Radio className="w-3.5 h-3.5 text-purple-400 animate-pulse" />
                    <span className="text-[9px] font-bold text-purple-400">{online}/7 Nodes Online</span>
                </div>
            </div>

            {/* Summary Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Total Nodes", value: "7", icon: Server, color: "text-purple-400" },
                    { label: "Nodes Online", value: `${online}`, icon: CheckCircle, color: "text-emerald-400" },
                    { label: "Total Profiles", value: totalProfiles.toLocaleString(), icon: Database, color: "text-cyan-400" },
                    { label: "Avg Latency", value: "28ms", icon: Zap, color: "text-amber-400" },
                ].map((m, i) => {
                    const Icon = m.icon;
                    return (
                        <motion.div key={m.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                            className="rounded-xl border border-tactical-border/60 bg-black/40 p-3">
                            <div className="flex items-center gap-1.5 mb-1.5">
                                <Icon className={`w-3.5 h-3.5 ${m.color}`} />
                                <span className="text-[9px] text-zinc-600 uppercase">{m.label}</span>
                            </div>
                            <p className={`text-lg font-extrabold ${m.color} font-mono`}>{m.value}</p>
                        </motion.div>
                    );
                })}
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600" />
                <input
                    type="text"
                    placeholder="Search nodes by name, type, or location…"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full bg-black/40 border border-tactical-border/60 rounded-xl pl-9 pr-4 py-2.5 text-xs text-zinc-200 placeholder:text-zinc-700 font-mono focus:outline-none focus:border-purple-500/40"
                />
            </div>

            {/* Node Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {filtered.map((node, i) => {
                    const sc = STATUS_CONFIG[node.status];
                    return (
                        <motion.div
                            key={node.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.05 * i }}
                            onClick={() => setSelectedNode(selectedNode?.id === node.id ? null : node)}
                            className={`rounded-2xl border cursor-pointer transition-all p-4 space-y-3 ${selectedNode?.id === node.id
                                ? "border-purple-500/50 bg-purple-500/5"
                                : "border-tactical-border/60 bg-black/30 hover:border-tactical-border hover:bg-black/50"
                                }`}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex items-center gap-2.5 min-w-0">
                                    <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20 shrink-0">
                                        <Server className="w-3.5 h-3.5 text-purple-400" />
                                    </div>
                                    <div className="min-w-0">
                                        <p className="text-[10px] font-bold text-white truncate">{node.name}</p>
                                        <p className="text-[9px] text-zinc-500 truncate">{node.type}</p>
                                    </div>
                                </div>
                                <div className={`flex items-center gap-1 border rounded px-1.5 py-0.5 text-[8px] font-bold shrink-0 ${sc.bg} ${sc.color}`}>
                                    <span className={`h-1.5 w-1.5 rounded-full ${sc.dot}`} />
                                    {sc.label}
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-2 text-[9px]">
                                <div className="p-2 rounded-lg bg-black/30 border border-tactical-border/30">
                                    <span className="text-zinc-600 block">Latency</span>
                                    <span className={`font-bold font-mono ${node.pingMs < 30 ? "text-emerald-400" : node.pingMs < 60 ? "text-amber-400" : "text-red-400"}`}>{node.pingMs} ms</span>
                                </div>
                                <div className="p-2 rounded-lg bg-black/30 border border-tactical-border/30">
                                    <span className="text-zinc-600 block">Profiles</span>
                                    <span className="font-bold text-zinc-300 font-mono">{node.profilesCount.toLocaleString()}</span>
                                </div>
                                <div className="p-2 rounded-lg bg-black/30 border border-tactical-border/30 col-span-2">
                                    <span className="text-zinc-600 block">Last Block Hash</span>
                                    <span className="font-bold text-cyan-400 font-mono">{node.lastBlock}</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-1">
                                    <Globe className="w-3 h-3 text-zinc-600" />
                                    <span className="text-[9px] text-zinc-500">{node.location}</span>
                                </div>
                                {node.iso && (
                                    <span className="text-[8px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded px-1.5 py-0.5">ISO 17025</span>
                                )}
                            </div>

                            {selectedNode?.id === node.id && (
                                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
                                    className="border-t border-tactical-border/40 pt-3 space-y-2">
                                    <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Node Capabilities</p>
                                    <div className="flex flex-wrap gap-1.5">
                                        {["STR Profiling", "Kinship Engine", "MCMC Genotyping", "ISO Report", "ZKP Audit"].map((cap) => (
                                            <span key={cap} className="text-[8px] font-bold text-purple-300 bg-purple-500/10 border border-purple-500/20 rounded px-2 py-0.5">{cap}</span>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </motion.div>
                    );
                })}
            </div>

            {/* Network Health */}
            <div className="rounded-2xl border border-purple-500/20 bg-purple-500/5 p-4 flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <div className="flex items-center gap-2 shrink-0">
                    <Shield className="w-4 h-4 text-purple-400" />
                    <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">Network Integrity</span>
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-[9px] text-zinc-400 font-mono">
                        Blockchain consensus: <span className="text-purple-300">Polygon zkEVM Block #1,847,291</span> •
                        HMAC-SHA256 chain verified •
                        <span className="text-emerald-400"> {online}/7 Nodes in consensus ✓</span>
                    </p>
                </div>
            </div>
        </div>
    );
}
