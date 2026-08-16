"use client";

import { useState } from "react";
import { Network, GitBranch, ArrowRight, ShieldCheck, Database, Layers, Search, Filter } from "lucide-react";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

export default function ForensicGraphPanel() {
  const { activeCase } = useForensicCaseStore();
  const [selectedNode, setSelectedNode] = useState<string>("EVID-STAIN-101");
  const [edgeViewMode, setEdgeViewMode] = useState<"connected" | "all">("connected");

  const nodes = [
    { id: "CASE-2026-001", type: "Case", label: "Homicide Investigation 001", badge: "ACTIVE_CASE", color: "border-amber-500/40 text-amber-300" },
    { id: "EVID-STAIN-101", type: "Evidence", label: "Bloodstain on Door Handle", badge: "BIOLOGICAL_STAIN", color: "border-red-500/40 text-red-300" },
    { id: "PERSON-SUSPECT-A", type: "Person", label: "Suspect John Doe", badge: "SUSPECT_MATCH", color: "border-indigo-500/40 text-indigo-300" },
    { id: "PERSON-VICTIM-B", type: "Person", label: "Victim Jane Smith", badge: "VICTIM_REFERENCE", color: "border-rose-500/40 text-rose-300" },
    { id: "SCENE-LOCATION-9", type: "Scene", label: "342 Harbor Street Crime Scene", badge: "CRIME_SCENE", color: "border-emerald-500/40 text-emerald-300" },
  ];

  const edges = [
    { from: "CASE-2026-001", to: "EVID-STAIN-101", relation: "ASSOCIATED_EVIDENCE", confidence: "100%" },
    { from: "EVID-STAIN-101", to: "PERSON-SUSPECT-A", relation: `DNA_CONTRIBUTOR (LR=${activeCase.profile.kinshipLR})`, confidence: "99.99%" },
    { from: "EVID-STAIN-101", to: "SCENE-LOCATION-9", relation: "COLLECTED_FROM", confidence: "100%" },
    { from: "PERSON-VICTIM-B", to: "SCENE-LOCATION-9", relation: "FOUND_AT_LOCATION", confidence: "100%" },
  ];

  const connectedEdges = edges.filter((e) => e.from === selectedNode || e.to === selectedNode);
  const displayedEdges = edgeViewMode === "connected" ? connectedEdges : edges;

  return (
    <div className="space-y-4 font-mono max-w-full overflow-hidden">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/60 pb-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 shrink-0">
            <Network className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xs sm:text-sm md:text-base font-bold tracking-wider text-white uppercase">
                Forensic Knowledge Graph Engine
              </h2>
              <span className="text-[8px] sm:text-[9px] font-bold text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded-md shrink-0 whitespace-nowrap">
                {nodes.length} Nodes • {edges.length} Directed Edges
              </span>
            </div>
            <p className="text-[9px] sm:text-[10px] text-zinc-400 mt-0.5 leading-relaxed">
              Multi-Relational Property Graph • Case-Person-Evidence Intelligence Network
            </p>
          </div>
        </div>
      </div>

      {/* Graph Visualizer Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column: Node Explorer */}
        <div className="lg:col-span-2 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Case Adjacency Network Entities ({nodes.length})
            </span>
            <span className="text-[9px] text-zinc-400">Click node to inspect connected edges</span>
          </div>

          <div className="space-y-2">
            {nodes.map((n) => {
              const nodeEdgeCount = edges.filter((e) => e.from === n.id || e.to === n.id).length;
              return (
                <div
                  key={n.id}
                  onClick={() => setSelectedNode(n.id)}
                  className={`p-3 rounded-xl border transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-2 ${
                    selectedNode === n.id
                      ? "bg-indigo-500/15 border-indigo-500/60 shadow-[0_0_15px_rgba(99,102,241,0.15)]"
                      : "bg-black/30 border-tactical-border/40 hover:border-tactical-border/80"
                  }`}
                >
                  <div className="space-y-0.5 min-w-0">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="text-xs font-bold text-white">{n.label}</span>
                      <span className="text-[9px] text-zinc-400 font-mono">({n.id})</span>
                    </div>
                    <p className="text-[9px] text-zinc-400 font-mono">Entity Type: {n.type} • {nodeEdgeCount} Degree Connection{nodeEdgeCount !== 1 ? "s" : ""}</p>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[8px] sm:text-[9px] font-bold border uppercase shrink-0 w-fit ${n.color}`}>
                    {n.badge}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Path & Relationship Traversal Inspector */}
        <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Graph Traversal Inspector
            </span>
            <div className="flex items-center gap-1 p-0.5 rounded-lg bg-black/40 border border-tactical-border/60 text-[8px] font-bold">
              <button
                onClick={() => setEdgeViewMode("connected")}
                className={`px-1.5 py-0.5 rounded transition-all ${edgeViewMode === "connected" ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40" : "text-zinc-500 hover:text-zinc-300"}`}
              >
                Connected ({connectedEdges.length})
              </button>
              <button
                onClick={() => setEdgeViewMode("all")}
                className={`px-1.5 py-0.5 rounded transition-all ${edgeViewMode === "all" ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40" : "text-zinc-500 hover:text-zinc-300"}`}
              >
                All ({edges.length})
              </button>
            </div>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40 space-y-0.5">
              <span className="text-zinc-500 text-[9px] block uppercase font-bold">Inspecting Focus Node</span>
              <p className="font-bold text-indigo-400 font-mono text-xs truncate">{selectedNode}</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-[9px] font-bold text-zinc-400 uppercase">
                <span>{edgeViewMode === "connected" ? `Connected Edges (${connectedEdges.length} of ${edges.length})` : `All Network Edges (${edges.length})`}</span>
              </div>

              {displayedEdges.map((e, idx) => {
                const isConnected = e.from === selectedNode || e.to === selectedNode;
                return (
                  <div
                    key={idx}
                    className={`p-2.5 rounded-xl border space-y-1 transition-all ${
                      isConnected
                        ? "bg-black/40 border-indigo-500/40 text-indigo-300"
                        : "bg-black/20 border-tactical-border/30 opacity-60 text-zinc-400"
                    }`}
                  >
                    <div className="flex items-center gap-1.5 font-mono text-[9px] flex-wrap justify-between">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className={`font-bold ${e.from === selectedNode ? "text-cyan-300" : "text-zinc-400"}`}>{e.from}</span>
                        <ArrowRight className="w-3 h-3 text-indigo-400 shrink-0" />
                        <span className={`font-bold ${e.to === selectedNode ? "text-cyan-300" : "text-zinc-400"}`}>{e.to}</span>
                      </div>
                      <span className="text-[8px] px-1 py-0.2 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">{e.confidence}</span>
                    </div>
                    <p className="text-[9px] font-bold font-mono break-all">{e.relation}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

