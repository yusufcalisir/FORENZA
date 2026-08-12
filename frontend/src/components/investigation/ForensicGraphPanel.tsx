"use client";

import { useState } from "react";
import { Network, GitBranch, ArrowRight, ShieldCheck, Database, Layers, Search } from "lucide-react";

export default function ForensicGraphPanel() {
  const [selectedNode, setSelectedNode] = useState<string>("EVID-STAIN-101");

  const nodes = [
    { id: "CASE-2026-001", type: "Case", label: "Homicide Investigation 001", badge: "ACTIVE_CASE", color: "border-amber-500/40 text-amber-300" },
    { id: "EVID-STAIN-101", type: "Evidence", label: "Bloodstain on Door Handle", badge: "BIOLOGICAL_STAIN", color: "border-red-500/40 text-red-300" },
    { id: "PERSON-SUSPECT-A", type: "Person", label: "Suspect John Doe", badge: "SUSPECT_MATCH", color: "border-indigo-500/40 text-indigo-300" },
    { id: "PERSON-VICTIM-B", type: "Person", label: "Victim Jane Smith", badge: "VICTIM_REFERENCE", color: "border-rose-500/40 text-rose-300" },
    { id: "SCENE-LOCATION-9", type: "Scene", label: "342 Harbor Street Crime Scene", badge: "CRIME_SCENE", color: "border-emerald-500/40 text-emerald-300" },
  ];

  const edges = [
    { from: "CASE-2026-001", to: "EVID-STAIN-101", relation: "ASSOCIATED_EVIDENCE" },
    { from: "EVID-STAIN-101", to: "PERSON-SUSPECT-A", relation: "DNA_CONTRIBUTOR (P=0.999)" },
    { from: "EVID-STAIN-101", to: "SCENE-LOCATION-9", relation: "COLLECTED_FROM" },
    { from: "PERSON-VICTIM-B", to: "SCENE-LOCATION-9", relation: "FOUND_AT_LOCATION" },
  ];

  return (
    <div className="space-y-4 font-mono max-w-full overflow-hidden">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 border-b border-tactical-border/60 pb-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 shrink-0">
            <Network className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h2 className="text-xs sm:text-base font-bold tracking-wider text-white uppercase truncate">
              Forensic Knowledge Graph Engine
            </h2>
            <p className="text-[9px] sm:text-[10px] text-zinc-400 mt-0.5 truncate">
              Multi-Relational Property Graph • Case-Person-Evidence Intelligence Network
            </p>
          </div>
        </div>

        <span className="text-[9px] sm:text-xs font-bold text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-1 rounded-lg shrink-0 w-fit">
          5 Nodes • 4 Directed Edges
        </span>
      </div>

      {/* Graph Visualizer Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column: Node Explorer */}
        <div className="lg:col-span-2 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 space-y-3 shadow-lg">
          <span className="text-xs font-bold text-white uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Case Adjacency Network Graph (CASE-2026-001)
          </span>

          <div className="space-y-2">
            {nodes.map((n) => (
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
                  <p className="text-[9px] text-zinc-400 font-mono">Entity Type: {n.type}</p>
                </div>
                <span className={`px-2 py-0.5 rounded text-[8px] sm:text-[9px] font-bold border uppercase shrink-0 w-fit ${n.color}`}>
                  {n.badge}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Path & Relationship Traversal Inspector */}
        <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 space-y-3 shadow-lg">
          <span className="text-xs font-bold text-white uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Graph Traversal Inspector
          </span>

          <div className="space-y-3 text-xs">
            <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40 space-y-0.5">
              <span className="text-zinc-500 text-[9px] block uppercase font-bold">Selected Entity ID</span>
              <p className="font-bold text-indigo-400 font-mono text-xs">{selectedNode}</p>
            </div>

            <div className="space-y-2">
              <span className="text-zinc-400 block text-[9px] font-bold uppercase">Relational Edges</span>
              {edges
                .filter((e) => e.from === selectedNode || e.to === selectedNode)
                .map((e, idx) => (
                  <div key={idx} className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                    <div className="flex items-center gap-1.5 text-zinc-300 font-mono text-[9px] flex-wrap">
                      <span className="text-zinc-400 font-bold">{e.from}</span>
                      <ArrowRight className="w-3 h-3 text-indigo-400 shrink-0" />
                      <span className="text-zinc-400 font-bold">{e.to}</span>
                    </div>
                    <p className="text-[9px] font-bold text-indigo-300 font-mono break-all">{e.relation}</p>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
