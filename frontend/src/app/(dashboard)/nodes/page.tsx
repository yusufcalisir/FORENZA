"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Network,
  Activity,
  Server,
  Cpu,
  Lock,
  Search,
  Zap,
  CheckCircle2
} from "lucide-react";
import TacticalPageHeader from "@/components/common/TacticalPageHeader";
import { useIngestStore } from "@/store/ingestStore";

interface LabNode {
  id: string;
  name: string;
  type: string;
  status: "ONLINE" | "ACTIVE_SYNC" | "DEGRADED";
  pingMs: number;
  profilesCount: number;
  location: string;
  lastBlock: string;
}

const LAB_NODES: LabNode[] = [
  {
    id: "node-01",
    name: "FORENSIC-LAB-ALPHA",
    type: "Central Reference Laboratory",
    status: "ONLINE",
    pingMs: 12,
    profilesCount: 14850,
    location: "Sector 1 Reference Hub",
    lastBlock: "0x89f2...c01a"
  },
  {
    id: "node-02",
    name: "DISTRICT-DNA-LAB-01",
    type: "Regional Pathology Node",
    status: "ONLINE",
    pingMs: 18,
    profilesCount: 8920,
    location: "District Medical Registry",
    lastBlock: "0x44a1...e9b2"
  },
  {
    id: "node-03",
    name: "CENTRAL-GENOMICS-NODE",
    type: "High-Throughput Sequencing",
    status: "ONLINE",
    pingMs: 9,
    profilesCount: 32100,
    location: "Genomics Intelligence Unit",
    lastBlock: "0xf17d...771c"
  },
  {
    id: "node-04",
    name: "MOBILE-EVIDENCE-UNIT-04",
    type: "Field Rapid STR Analyzer",
    status: "ACTIVE_SYNC",
    pingMs: 24,
    profilesCount: 1450,
    location: "Mobile Crime Scene Unit",
    lastBlock: "0x33b8...90ef"
  }
];

export default function NodesPage() {
  const [selectedNode, setSelectedNode] = useState<LabNode>(LAB_NODES[0]);
  const [queryInput, setQueryInput] = useState("");
  const [searchResult, setSearchResult] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const handleFederatedQuery = (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryInput) return;
    setIsSearching(true);
    setSearchResult(null);

    setTimeout(() => {
      setIsSearching(false);
      setSearchResult(`MATCH CONFIRMED (Log10 LR = +8.45) across 3 peer nodes (${selectedNode.name}, DISTRICT-DNA-LAB-01, CENTRAL-GENOMICS-NODE). ZKP Proof verified.`);
    }, 600);
  };

  return (
    <div className="p-3 sm:p-5 lg:p-6 space-y-6 font-mono text-tactical-text bg-slate-950 min-h-screen">
      {/* ── Unified Tactical Page Header ── */}
      <TacticalPageHeader
        title="Federated Forensic Network"
        subtitle="Decentralized Laboratory Peer Consensus • Zero-Knowledge STR Ledger • Multi-Node Search"
        badge="4/4 PEERS ONLINE"
        icon={Network}
        accentColor="cyan"
      />

      {/* ── Main Layout: Laboratory Nodes Grid + Federated Query Inspector ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left 2-Cols: Laboratory Node Cards */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-tactical-text-muted flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-400" />
            Active Laboratory Nodes ({LAB_NODES.length})
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {LAB_NODES.map((node) => {
              const isSelected = selectedNode.id === node.id;
              return (
                <motion.div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  whileHover={{ scale: 1.01 }}
                  className={`cursor-pointer rounded-2xl border p-5 transition-all space-y-3 ${
                    isSelected
                      ? "border-cyan-500/80 bg-cyan-500/10 shadow-[0_0_20px_rgba(6,182,212,0.15)]"
                      : "border-tactical-border/80 bg-tactical-surface/40 hover:border-tactical-border"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Cpu className={`w-4 h-4 ${isSelected ? "text-cyan-400" : "text-zinc-400"}`} />
                      <span className="text-xs font-bold font-mono text-tactical-text">{node.name}</span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      {node.status}
                    </span>
                  </div>

                  <p className="text-[10px] text-zinc-400">{node.type} • {node.location}</p>

                  <div className="pt-2 border-t border-tactical-border/40 grid grid-cols-2 gap-2 text-[10px]">
                    <div>
                      <span className="text-zinc-500 block">Profiles Indexed</span>
                      <span className="font-bold text-cyan-300 font-mono">{node.profilesCount.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500 block">Ping Latency</span>
                      <span className="font-bold text-emerald-400 font-mono">{node.pingMs} ms</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[9px] text-zinc-500 font-mono pt-1">
                    <span>Block: {node.lastBlock}</span>
                    <span className="flex items-center gap-1 text-cyan-400">
                      <Lock className="w-2.5 h-2.5" />
                      ZKP Verified
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Right 1-Col: Federated Query & Sample Ingest Terminal */}
        <div className="space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-tactical-text-muted flex items-center gap-2">
            <Search className="w-4 h-4 text-purple-400" />
            Distributed Query Terminal
          </h2>

          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-xl">
            <div className="space-y-1">
              <span className="text-xs font-bold text-tactical-text block">
                Target Node: {selectedNode.name}
              </span>
              <p className="text-[10px] text-zinc-400">
                Execute encrypted cross-node query with zero data leakage.
              </p>
            </div>

            <form onSubmit={handleFederatedQuery} className="space-y-3">
              <div>
                <label className="text-[9px] text-zinc-500 block mb-1">Enter Profile ID or STR Hash</label>
                <input
                  type="text"
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  placeholder="e.g. test-profile-eu or SHA-256 hash"
                  className="w-full bg-black/50 border border-tactical-border/70 rounded-xl p-2.5 font-mono text-xs text-cyan-300 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setQueryInput("test-profile-eu");
                    useIngestStore.getState().setLastIngested("test-profile-eu", selectedNode.name, 24);
                  }}
                  className="px-2.5 py-1 rounded-lg text-[9px] font-mono bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20 transition-all"
                >
                  Fill Sample EU
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setQueryInput("test-profile-aa");
                    useIngestStore.getState().setLastIngested("test-profile-aa", selectedNode.name, 24);
                  }}
                  className="px-2.5 py-1 rounded-lg text-[9px] font-mono bg-purple-500/10 border border-purple-500/30 text-purple-300 hover:bg-purple-500/20 transition-all"
                >
                  Fill Sample AA
                </button>
              </div>

              <button
                type="submit"
                disabled={isSearching || !queryInput}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-black font-bold text-xs uppercase tracking-wider transition-all disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isSearching ? (
                  <>
                    <Activity className="w-3.5 h-3.5 animate-spin" />
                    Executing Consensus Query...
                  </>
                ) : (
                  <>
                    <Zap className="w-3.5 h-3.5" />
                    Query Federated Network
                  </>
                )}
              </button>
            </form>

            {searchResult && (
              <motion.div
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-[10px] space-y-1 font-mono"
              >
                <div className="flex items-center gap-1.5 font-bold">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>CONSENSUS QUERY RESULT</span>
                </div>
                <p className="text-zinc-300 leading-relaxed">{searchResult}</p>
              </motion.div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
