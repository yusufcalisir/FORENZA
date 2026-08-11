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
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.15)]">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Forensic Knowledge Graph Engine
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Multi-Relational Property Graph • Case-Person-Evidence Intelligence Network • Shortest Path Traversal
            </p>
          </div>
        </div>

        <span className="text-xs font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-3 py-1 rounded-lg">
          5 Nodes • 4 Directed Edges
        </span>
      </div>

      {/* Graph Visualizer Area */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Node Explorer */}
        <div className="md:col-span-2 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Case Adjacency Network Graph (CASE-2026-001)
          </span>

          <div className="space-y-3">
            {nodes.map((n) => (
              <div
                key={n.id}
                onClick={() => setSelectedNode(n.id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                  selectedNode === n.id
                    ? "bg-indigo-500/15 border-indigo-500/60 shadow-[0_0_15px_rgba(99,102,241,0.15)]"
                    : "bg-black/20 border-tactical-border/40 hover:border-tactical-border/80"
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-tactical-text">{n.label}</span>
                    <span className="text-[9px] text-zinc-500">({n.id})</span>
                  </div>
                  <p className="text-[10px] text-zinc-400">Entity Type: {n.type}</p>
                </div>
                <span className={`px-2.5 py-1 rounded text-[9px] font-bold border uppercase ${n.color}`}>
                  {n.badge}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Path & Relationship Traversal Inspector */}
        <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Graph Traversal Inspector
          </span>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Selected Entity ID</span>
              <p className="font-bold text-indigo-400 font-mono">{selectedNode}</p>
            </div>

            <div className="space-y-2">
              <span className="text-zinc-500 block text-[10px] font-bold uppercase">Relational Edges</span>
              {edges
                .filter((e) => e.from === selectedNode || e.to === selectedNode)
                .map((e, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-black/30 border border-tactical-border/40 space-y-1">
                    <div className="flex items-center gap-1.5 text-zinc-300 font-mono text-[10px]">
                      <span>{e.from}</span>
                      <ArrowRight className="w-3 h-3 text-indigo-400" />
                      <span>{e.to}</span>
                    </div>
                    <span className="text-emerald-400 font-bold text-[9px] block">
                      Relation: {e.relation}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
