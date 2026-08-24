"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
    Network, Server, Zap,
    CheckCircle, Globe, Radio, Shield,
    Database, Search,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export interface LabNode {
    id: string;
    name: string;
    type: string;
    typeTr: string;
    status: "ONLINE" | "SYNCING" | "DEGRADED";
    pingMs: number;
    profilesCount: number;
    location: string;
    locationTr: string;
    lastBlock: string;
    iso: boolean;
}

export const LAB_NODES: LabNode[] = [
    { id: "node-01", name: "FORENSIC-LAB-ALPHA", type: "Central Reference Laboratory", typeTr: "Merkezi Referans Laboratuvarı", status: "ONLINE", pingMs: 12, profilesCount: 14850, location: "Sector 1 Reference Hub", locationTr: "Sektör 1 Referans Merkezi", lastBlock: "0x89f2…c01a", iso: true },
    { id: "node-02", name: "DISTRICT-DNA-LAB-01", type: "Regional Pathology Node", typeTr: "Bölgesel Patoloji Düğümü", status: "ONLINE", pingMs: 18, profilesCount: 8920, location: "District Medical Registry", locationTr: "Bölge Tıbbi Sicil", lastBlock: "0x44a1…e9b2", iso: true },
    { id: "node-03", name: "CENTRAL-GENOMICS-NODE", type: "High-Throughput Sequencing", typeTr: "Yüksek Verimli Dizileme Düğümü", status: "ONLINE", pingMs: 9, profilesCount: 32100, location: "Genomics Intelligence Unit", locationTr: "Genomik İstihbarat Birimi", lastBlock: "0xf17d…771c", iso: true },
    { id: "node-04", name: "BORDER-FORENSICS-NODE", type: "Field Collection Point", typeTr: "Saha Örnek Toplama Noktası", status: "ONLINE", pingMs: 28, profilesCount: 3420, location: "Port Authority Lab", locationTr: "Liman Otoritesi Laboratuvarı", lastBlock: "0x2b91…4d7f", iso: false },
    { id: "node-05", name: "COLD-CASE-ARCHIVE-NODE", type: "Historical Evidence Archive", typeTr: "Tarihi Delil Arşivi", status: "SYNCING", pingMs: 45, profilesCount: 92500, location: "National Archive Vault", locationTr: "Ulusal Arşiv Kasası", lastBlock: "0xa3c2…9f1e", iso: true },
    { id: "node-06", name: "TOXICOLOGY-HUB-NODE", type: "Toxicology Reference Lab", typeTr: "Toksikoloji Referans Laboratuvarı", status: "ONLINE", pingMs: 14, profilesCount: 7200, location: "Forensic Chemistry Division", locationTr: "Adli Kimya Bölümü", lastBlock: "0x6e5b…c782", iso: true },
    { id: "node-07", name: "MOBILE-LAB-UNIT-01", type: "Rapid Deployment Kit", typeTr: "Hızlı Konuşlandırma Kiti", status: "DEGRADED", pingMs: 112, profilesCount: 180, location: "Field Operations  -  Active", locationTr: "Saha Operasyonları  -  Aktif", lastBlock: "0xb8d4…e043", iso: false },
];

const STATUS_CONFIG = {
    ONLINE: { color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/30", dot: "bg-emerald-400", label: "ONLINE", labelTr: "ÇEVRİMİÇİ" },
    SYNCING: { color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30", dot: "bg-amber-400 animate-pulse", label: "SYNCING", labelTr: "EŞİTLENİYOR" },
    DEGRADED: { color: "text-red-400", bg: "bg-red-500/10 border-red-500/30", dot: "bg-red-400", label: "DEGRADED", labelTr: "BOZULMUŞ" },
};

export default function FederatedNetworkPanel() {
    const { lang } = useSaasLanguage();
    const isTr = lang === "tr";

    const [searchTerm, setSearchTerm] = useState("");
    const [selectedNode, setSelectedNode] = useState<LabNode | null>(null);

    const filtered = LAB_NODES.filter((n) =>
        n.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        n.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (n.typeTr && n.typeTr.toLowerCase().includes(searchTerm.toLowerCase())) ||
        n.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (n.locationTr && n.locationTr.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const online = LAB_NODES.filter((n) => n.status === "ONLINE").length;
    const totalProfiles = LAB_NODES.reduce((s, n) => s + n.profilesCount, 0);

    return (
        <div className="space-y-4 font-mono max-w-full overflow-hidden">
            {/* Summary Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                {[
                    { label: isTr ? "Toplam Düğüm" : "Total Nodes", value: `${LAB_NODES.length}`, icon: Server, color: "text-purple-400" },
                    { label: isTr ? "Çevrimiçi Düğüm" : "Nodes Online", value: `${online}`, icon: CheckCircle, color: "text-emerald-400" },
                    { label: isTr ? "Toplam Profil" : "Total Profiles", value: totalProfiles.toLocaleString(), icon: Database, color: "text-cyan-400" },
                    { label: isTr ? "Ort. Gecikme" : "Avg Latency", value: "28ms", icon: Zap, color: "text-amber-400" },
                ].map((m, i) => {
                    const Icon = m.icon;
                    return (
                        <motion.div key={m.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                            className="rounded-xl border border-tactical-border/60 bg-tactical-surface/80 p-2.5 sm:p-3">
                            <div className="flex items-center gap-1.5 mb-1">
                                <Icon className={`w-3.5 h-3.5 ${m.color} shrink-0`} />
                                <span className="text-[9px] text-zinc-500 uppercase font-bold truncate">{m.label}</span>
                            </div>
                            <p className={`text-base sm:text-lg font-extrabold ${m.color} font-mono`}>{m.value}</p>
                        </motion.div>
                    );
                })}
            </div>

            {/* Search Input */}
            <div className="relative max-w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-500" />
                <input
                    type="text"
                    placeholder={isTr ? "Düğümleri isim, tür veya konuma göre ara…" : "Search nodes by name, type, or location…"}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full bg-tactical-surface/80 border border-tactical-border/70 rounded-xl pl-9 pr-4 py-2 text-xs text-zinc-200 placeholder:text-zinc-500 font-mono focus:outline-none focus:border-purple-500/50 transition-colors"
                />
            </div>

            {/* Node Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {filtered.map((node, i) => {
                    const sc = STATUS_CONFIG[node.status];
                    return (
                        <motion.div
                            key={node.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.04 * i }}
                            onClick={() => setSelectedNode(selectedNode?.id === node.id ? null : node)}
                            className={`rounded-xl border cursor-pointer transition-all p-3 sm:p-4 space-y-2.5 max-w-full ${selectedNode?.id === node.id
                                ? "border-purple-500/50 bg-purple-500/10 shadow-lg"
                                : "border-tactical-border/60 bg-tactical-surface/70 hover:border-tactical-border hover:bg-tactical-surface"
                                }`}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex items-center gap-2 min-w-0">
                                    <div className="p-1.5 sm:p-2 rounded-xl bg-purple-500/10 border border-purple-500/20 shrink-0">
                                        <Server className="w-3.5 h-3.5 text-purple-400" />
                                    </div>
                                    <div className="min-w-0">
                                        <p className="text-[10px] font-bold text-white truncate">{node.name}</p>
                                        <p className="text-[9px] text-zinc-400 truncate">{isTr ? node.typeTr : node.type}</p>
                                    </div>
                                </div>
                                <div className={`flex items-center gap-1 border rounded-md px-1.5 py-0.5 text-[8px] font-bold shrink-0 ${sc.bg} ${sc.color}`}>
                                    <span className={`h-1.5 w-1.5 rounded-full ${sc.dot}`} />
                                    {isTr ? sc.labelTr : sc.label}
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-1.5 text-[9px]">
                                <div className="p-1.5 rounded-lg bg-black/40 border border-tactical-border/40">
                                    <span className="text-zinc-500 block">{isTr ? "Gecikme" : "Latency"}</span>
                                    <span className={`font-bold font-mono ${node.pingMs < 30 ? "text-emerald-400" : node.pingMs < 60 ? "text-amber-400" : "text-red-400"}`}>{node.pingMs} ms</span>
                                </div>
                                <div className="p-1.5 rounded-lg bg-black/40 border border-tactical-border/40">
                                    <span className="text-zinc-500 block">{isTr ? "Profiller" : "Profiles"}</span>
                                    <span className="font-bold text-zinc-300 font-mono">{node.profilesCount.toLocaleString()}</span>
                                </div>
                                <div className="p-1.5 rounded-lg bg-black/40 border border-tactical-border/40 col-span-2">
                                    <span className="text-zinc-500 block">{isTr ? "Son Blok Hashi" : "Last Block Hash"}</span>
                                    <span className="font-bold text-cyan-400 font-mono truncate block">{node.lastBlock}</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-between text-[9px]">
                                <div className="flex items-center gap-1 min-w-0">
                                    <Globe className="w-3 h-3 text-zinc-500 shrink-0" />
                                    <span className="text-zinc-400 truncate">{isTr ? node.locationTr : node.location}</span>
                                </div>
                                {node.iso && (
                                    <span className="text-[8px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded px-1.5 py-0.5 shrink-0">ISO 17025</span>
                                )}
                            </div>

                            {selectedNode?.id === node.id && (
                                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
                                    className="border-t border-tactical-border/40 pt-2 space-y-1.5">
                                    <p className="text-[9px] text-zinc-400 uppercase font-bold tracking-wider">
                                        {isTr ? "Düğüm Yetenekleri" : "Node Capabilities"}
                                    </p>
                                    <div className="flex flex-wrap gap-1">
                                        {(isTr
                                            ? ["STR Profilleme", "Akrabalık Motoru", "MCMC Genotipleme", "ISO Raporu", "ZKP Denetimi"]
                                            : ["STR Profiling", "Kinship Engine", "MCMC Genotyping", "ISO Report", "ZKP Audit"]
                                        ).map((cap) => (
                                            <span key={cap} className="text-[8px] font-bold text-purple-300 bg-purple-500/10 border border-purple-500/20 rounded-md px-1.5 py-0.5">{cap}</span>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </motion.div>
                    );
                })}
            </div>

            {/* Network Health */}
            <div className="rounded-xl border border-purple-500/30 bg-purple-500/5 p-3.5 sm:p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 max-w-full overflow-hidden">
                <div className="flex items-center gap-2 shrink-0">
                    <Shield className="w-4 h-4 text-purple-400 shrink-0" />
                    <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">
                        {isTr ? "Ağ Bütünlüğü" : "Network Integrity"}
                    </span>
                </div>
                <div className="flex-1 min-w-0 max-w-full">
                    <p className="text-[9px] sm:text-[10px] text-zinc-400 font-mono leading-relaxed break-all sm:break-normal">
                        {isTr ? "Blokzincir konsensüsü: " : "Blockchain consensus: "}
                        <span className="text-purple-300 font-bold">Polygon zkEVM Block #1,847,291</span> •
                        {isTr ? " HMAC-SHA256 zinciri doğrulandı • " : " HMAC-SHA256 chain verified • "}
                        <span className="text-emerald-400 font-bold">
                            {isTr ? ` ${online}/7 Düğüm konsensüste ✓` : ` ${online}/7 Nodes in consensus ✓`}
                        </span>
                    </p>
                </div>
            </div>
        </div>
    );
}
