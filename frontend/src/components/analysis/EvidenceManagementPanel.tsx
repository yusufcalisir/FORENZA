"use client";

import { useState } from "react";
import { ShieldCheck, MapPin, PackageCheck, History, FileText, Lock } from "lucide-react";

export default function EvidenceManagementPanel() {
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string>("EVID-BLOOD-101");

  const items = [
    { id: "EVID-BLOOD-101", scene: "SCENE-2026-001", type: "Bloodstain", method: "Sterile Cotton Swab", collector: "INV-DOE-12", seal: "SEAL-112233", condition: "Dry Ambient", coords: "X: 1.5, Y: 2.2, Z: 0.4", badge: "SEALED", hash: "0x8f2a...91b4" },
    { id: "EVID-HAIR-102", scene: "SCENE-2026-001", type: "Hair", method: "Sterile Forceps", collector: "INV-DOE-12", seal: "SEAL-445566", condition: "Room Temp", coords: "X: 3.1, Y: 0.8, Z: 0.0", badge: "SEALED", hash: "0x3c1d...44e9" },
    { id: "EVID-TOUCH-103", scene: "SCENE-2026-001", type: "Touch DNA", method: "Tape Lift", collector: "INV-SMITH-44", seal: "SEAL-998877", condition: "Dry Ambient", coords: "X: 0.9, Y: 1.4, Z: 1.1", badge: "IN_LAB", hash: "0x7e5b...22f0" },
    { id: "EVID-BONE-104", scene: "SCENE-2026-002", type: "Bone Fragment", method: "Excision", collector: "INV-SMITH-44", seal: "SEAL-334411", condition: "Frozen -20C", coords: "Lat: 52.3676, Lon: 4.9041", badge: "FROZEN", hash: "0x1a9c...88d2" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <PackageCheck className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Crime Scene Biological Evidence Registry
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              ISO 21043 Evidence Management • Tamper-Evident Container Seals • SHA-256 Chain of Custody Audit
            </p>
          </div>
        </div>

        <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-3 py-1 rounded-lg">
          ISO 21043 Verified
        </span>
      </div>

      {/* Grid: Registry & Chain Audit */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left 2 Cols: Evidence Item Registry */}
        <div className="md:col-span-2 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Biological Evidence Inventory
          </span>

          <div className="space-y-3">
            {items.map((item) => (
              <div
                key={item.id}
                onClick={() => setSelectedEvidenceId(item.id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                  selectedEvidenceId === item.id
                    ? "bg-amber-500/15 border-amber-500/60 shadow-[0_0_15px_rgba(245,158,11,0.15)]"
                    : "bg-black/20 border-tactical-border/40 hover:border-tactical-border/80"
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-tactical-text">{item.id}</span>
                    <span className="text-[9px] text-amber-400 font-bold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
                      {item.type}
                    </span>
                    <span className="text-zinc-600">•</span>
                    <span className="text-zinc-400 text-[10px]">{item.scene}</span>
                  </div>
                  <p className="text-[10px] text-zinc-400">
                    Method: {item.method} • Seal: {item.seal} • Collector: {item.collector}
                  </p>
                </div>

                <div className="flex items-center gap-3 text-xs font-mono">
                  <div className="text-right">
                    <p className="text-[9px] text-zinc-500">Spatial Position</p>
                    <p className="text-emerald-400 font-bold text-[10px]">{item.coords}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Col: SHA-256 Custody Audit Log */}
        <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
          <span className="text-xs font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
            Cryptographic Custody Ledger
          </span>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-black/20 border border-tactical-border/40 space-y-1">
              <span className="text-zinc-500 block">Audited Item ID</span>
              <p className="font-bold text-amber-400 font-mono">{selectedEvidenceId}</p>
            </div>

            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 space-y-1">
              <div className="flex items-center gap-1.5 font-bold">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Chain of Custody Intact</span>
              </div>
              <p className="text-[10px] text-zinc-300">SHA-256 Hash Continuity Verified</p>
            </div>

            <div className="space-y-2">
              <span className="text-zinc-500 block text-[10px] font-bold uppercase">Custody History Log</span>
              <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/40 space-y-1 font-mono text-[9px]">
                <p className="text-zinc-400 font-bold">TR-1: CRIME_SCENE → INV-DOE-12</p>
                <p className="text-zinc-500">Hash: 0x8f2a91b4c3d2e1f0</p>
              </div>
              <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/40 space-y-1 font-mono text-[9px]">
                <p className="text-zinc-400 font-bold">TR-2: INV-DOE-12 → LAB-DNA-EXTRACTION</p>
                <p className="text-zinc-500">Hash: 0x4e9b8a7c2d1e0f3a</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
