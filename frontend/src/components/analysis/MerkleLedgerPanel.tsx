"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { GitBranch, ShieldCheck, RefreshCw, AlertTriangle, CheckCircle2, Lock, ArrowRight, FileCheck, Layers, Hash } from "lucide-react";

interface CustodyEvent {
  event_id: string;
  timestamp_iso: string;
  officer_id: string;
  sample_barcode: string;
  location_id: string;
  action_type: string;
  notes?: string;
}

interface MerkleProofStep {
  sibling_hash: string;
  direction: string;
}

interface MerkleProofResponse {
  target_event_id: string;
  target_event_index: number;
  target_leaf_hash: string;
  merkle_root: string;
  proof_path: MerkleProofStep[];
  path_length: number;
}

interface VerificationResponse {
  is_valid: boolean;
  computed_root: string;
  expected_root: string;
  verdict: string;
  steps_evaluated: number;
  step_trace: string[];
  prosecutors_fallacy_shield: string;
}

const DEFAULT_EVENTS: CustodyEvent[] = [
  { event_id: "EVT-001", timestamp_iso: "2026-08-16T08:15:00Z", officer_id: "DET-MILLER-704", sample_barcode: "BC-DNA-99104", location_id: "CRIME_SCENE_SECTOR_A", action_type: "COLLECTION", notes: "Biological swab secured in sterile barcoded envelope." },
  { event_id: "EVT-002", timestamp_iso: "2026-08-16T09:30:00Z", officer_id: "OFFICER-CHEN-122", sample_barcode: "BC-DNA-99104", location_id: "EVIDENCE_TRANSPORT_VEHICLE", action_type: "TRANSFER", notes: "Chain of custody handoff to central logistics." },
  { event_id: "EVT-003", timestamp_iso: "2026-08-16T11:00:00Z", officer_id: "TECH-DAVIS-301", sample_barcode: "BC-DNA-99104", location_id: "CENTRAL_LAB_ACCESSIONING", action_type: "ACCESSION", notes: "Sample logged into LIMS with barcode verification." },
  { event_id: "EVT-004", timestamp_iso: "2026-08-16T13:45:00Z", officer_id: "DR-CONNOR-042", sample_barcode: "BC-DNA-99104", location_id: "EXTRACTION_SUITE_B", action_type: "EXTRACTION", notes: "Automated magnetic bead DNA extraction completed." },
];

export default function MerkleLedgerPanel() {
  const [activeTab, setActiveTab] = useState<"tree" | "proof">("tree");
  const [events, setEvents] = useState<CustodyEvent[]>(DEFAULT_EVENTS);
  const [isTampered, setIsTampered] = useState<boolean>(false);
  const [selectedEventIndex, setSelectedEventIndex] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);

  const [merkleRoot, setMerkleRoot] = useState<string>("8f9e1c2b3a4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f");
  const [leafHashes, setLeafHashes] = useState<string[]>([
    "a1b2c3d4e5f60718293a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e",
    "b2c3d4e5f60718293a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f",
    "c3d4e5f60718293a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a",
    "d4e5f60718293a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b"
  ]);

  const [proofData, setProofData] = useState<MerkleProofResponse | null>(null);
  const [verifyResult, setVerifyResult] = useState<VerificationResponse | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const fetchTree = async (currentEvents: CustodyEvent[]) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/lims/merkle/build-tree`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events: currentEvents })
      });
      if (res.ok) {
        const data = await res.json();
        setMerkleRoot(data.merkle_root);
        setLeafHashes(data.leaf_hashes);
      }
    } catch (e) {
      console.error("Merkle tree build failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleTamperToggle = () => {
    const nextTamper = !isTampered;
    setIsTampered(nextTamper);

    if (nextTamper) {
      // Alter event 1 timestamp by 1 second
      const tampered = [...DEFAULT_EVENTS];
      tampered[1] = {
        ...tampered[1],
        timestamp_iso: "2026-08-16T09:30:01Z", // 1-second shift!
      };
      setEvents(tampered);
      fetchTree(tampered);
    } else {
      setEvents(DEFAULT_EVENTS);
      fetchTree(DEFAULT_EVENTS);
    }
  };

  const generateProof = async (idx: number) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/lims/merkle/generate-proof`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          events: events,
          target_event_index: idx
        })
      });
      if (res.ok) {
        const data: MerkleProofResponse = await res.json();
        setProofData(data);

        // Auto verify against current root
        const verRes = await fetch(`${API_BASE}/api/v1/forensic/lims/merkle/verify-proof`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            leaf_hash: data.target_leaf_hash,
            proof_path: data.proof_path,
            expected_root: merkleRoot
          })
        });
        if (verRes.ok) {
          const verData = await verRes.json();
          setVerifyResult(verData);
        }
      }
    } catch (e) {
      console.error("Proof generation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl border border-indigo-500/30 bg-indigo-500/10 shadow-lg overflow-hidden">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-500/20 border border-indigo-500/40 text-indigo-300">
            <GitBranch className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xs sm:text-sm font-bold tracking-widest text-tactical-text uppercase">
                Tamper-Evident Merkle Tree Chain-of-Custody Ledger
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 whitespace-nowrap">
                ISO/IEC 17025 • SHA-256
              </span>
            </div>
            <p className="text-[9px] sm:text-[10px] text-zinc-400 mt-0.5 truncate">
              Chained SHA-256 Leaf Custody Events • Binary Balanced Merkle Reduction • Tamper-Evident Proof of Inclusion
            </p>
          </div>
        </div>

        {/* Inner Tabs & Tamper Switch */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 shrink-0">
          <button
            onClick={handleTamperToggle}
            className={`px-2.5 sm:px-3 py-1.5 rounded-xl border text-[10px] sm:text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer whitespace-nowrap shrink-0 ${
              isTampered
                ? "bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse"
                : "bg-black/60 text-zinc-400 border-tactical-border/60 hover:text-zinc-200"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
            {isTampered ? "Tampered (+1s)" : "Simulate Tampering"}
          </button>

          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/60 border border-tactical-border/60 overflow-x-auto max-w-full shrink-0">
            <button
              onClick={() => setActiveTab("tree")}
              className={`px-3 py-1.5 rounded-lg text-[10px] sm:text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                activeTab === "tree"
                  ? "bg-indigo-500 text-white shadow-md font-extrabold"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Custody Tree
            </button>
            <button
              onClick={() => {
                setActiveTab("proof");
                generateProof(selectedEventIndex);
              }}
              className={`px-3 py-1.5 rounded-lg text-[10px] sm:text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                activeTab === "proof"
                  ? "bg-indigo-500 text-white shadow-md font-extrabold"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              Inclusion Proof
            </button>
          </div>
        </div>
      </div>

      {/* ── SubTab 1: Custody Event Timeline & Merkle Tree ── */}
      {activeTab === "tree" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Custody Event Stream */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                Chained Custody Events (N={events.length})
              </span>
              <button
                onClick={() => fetchTree(events)}
                disabled={loading}
                className="px-3 py-1 rounded-lg bg-indigo-500 hover:bg-indigo-400 text-white font-bold text-[10px] uppercase transition-all shadow-md flex items-center gap-1 cursor-pointer"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
                Rehash Tree
              </button>
            </div>

            <div className="space-y-2">
              {events.map((ev, idx) => (
                <div
                  key={ev.event_id}
                  onClick={() => {
                    setSelectedEventIndex(idx);
                    generateProof(idx);
                  }}
                  className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedEventIndex === idx
                      ? "border-indigo-500/80 bg-indigo-500/20 text-indigo-200 font-bold"
                      : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-bold text-zinc-200">{ev.event_id} ({ev.action_type})</span>
                    <span className="text-[10px] text-zinc-500 font-mono">{ev.timestamp_iso.slice(11, 19)} UTC</span>
                  </div>
                  <div className="text-[10px] text-zinc-400">{ev.officer_id} • {ev.location_id}</div>
                  <div className="text-[9px] text-zinc-500 mt-1 truncate">{ev.notes}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Merkle Tree Cryptographic Anchor */}
          <div className="lg:col-span-2 space-y-4">
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              <div className="rounded-2xl border border-indigo-500/40 bg-gradient-to-br from-indigo-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-indigo-500/20 pb-3.5">
                  <div className="min-w-0">
                    <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest block">
                      IMMUTABLE MERKLE ROOT COMMITMENT (R_MERKLE)
                    </span>
                    <span className="text-xs sm:text-sm md:text-base font-black text-indigo-300 font-mono break-all block mt-0.5">
                      {merkleRoot}
                    </span>
                  </div>
                  <div className="flex flex-col items-start sm:items-end gap-1 shrink-0">
                    <span className="text-[10px] text-zinc-400 block uppercase font-bold">Tree Status</span>
                    <span className={`text-[10px] sm:text-xs font-bold px-2.5 py-1 rounded-lg border font-mono whitespace-nowrap ${
                      isTampered
                        ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                        : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                    }`}>
                      {isTampered ? "DIVERGENT ROOT" : "ROOT ANCHORED"}
                    </span>
                  </div>
                </div>

                {/* Leaf Hashes Display */}
                <div className="space-y-2">
                  <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
                    Layer 0: Chained SHA-256 Leaf Nodes:
                  </span>
                  <div className="space-y-1.5">
                    {leafHashes.map((lh, idx) => (
                      <div
                        key={idx}
                        className="flex flex-col sm:flex-row sm:items-center justify-between p-2.5 rounded-lg bg-black/40 border border-tactical-border/40 text-[10px] font-mono gap-1.5 sm:gap-3 hover:border-indigo-500/40 transition-colors"
                      >
                        <div className="flex items-center gap-1.5 shrink-0">
                          <span className="text-indigo-400 font-bold whitespace-nowrap bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
                            H_{idx + 1} (EVT-{idx + 1}):
                          </span>
                        </div>
                        <span className="text-zinc-300 font-mono break-all sm:truncate sm:max-w-md text-[9px] sm:text-[10px]">
                          {lh}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                  <div className="flex items-center gap-1.5 text-indigo-400 font-bold mb-1">
                    <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                    ISO/IEC 17025:2017 &amp; FRE 702 Legal Evaluative Shield
                  </div>
                  Cryptographic Merkle tree structures guarantee temporal non-repudiation in LIMS case files. 
                  Any single-character alteration to event timestamps, handlers, or locations yields an entirely divergent root with probability 1 - 2⁻²⁵⁶.
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      )}

      {/* ── SubTab 2: Merkle Proof Auditor ── */}
      {activeTab === "proof" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Select Target Event */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
                Select Event for Audit Path
              </span>
            </div>

            <div className="space-y-2">
              {events.map((ev, idx) => (
                <button
                  key={ev.event_id}
                  onClick={() => {
                    setSelectedEventIndex(idx);
                    generateProof(idx);
                  }}
                  className={`p-3 rounded-xl border text-left w-full transition-all cursor-pointer ${
                    selectedEventIndex === idx
                      ? "border-indigo-500/80 bg-indigo-500/20 text-indigo-300 font-bold"
                      : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="text-xs font-bold">{ev.event_id} — {ev.action_type}</div>
                  <div className="text-[10px] text-zinc-400">{ev.officer_id}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Right: Proof Details & Verification */}
          <div className="lg:col-span-2 space-y-4">
            {proofData && verifyResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-indigo-500/40 bg-gradient-to-br from-indigo-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-indigo-500/20 pb-3.5">
                    <div>
                      <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest block">
                        MERKLE INCLUSION PROOF (AUDIT PATH π_{proofData.target_event_index + 1})
                      </span>
                      <span className="text-sm sm:text-base md:text-xl font-black text-indigo-300 font-mono">
                        {proofData.target_event_id} (Path Length: {proofData.path_length} Sibling Hashes)
                      </span>
                    </div>
                    <div className="flex flex-col items-start sm:items-end gap-1">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">Courtroom Admissibility</span>
                      <span className={`text-[10px] sm:text-xs font-bold px-2.5 py-1 rounded-lg border font-mono whitespace-nowrap ${
                        verifyResult.is_valid
                          ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                          : "bg-rose-500/20 text-rose-300 border-rose-500/40"
                      }`}>
                        {verifyResult.verdict}
                      </span>
                    </div>
                  </div>

                  {/* Sibling Path Sequence */}
                  <div className="space-y-2">
                    <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
                      O(log₂ N) Sibling Hash Traversal:
                    </span>
                    {proofData.proof_path.map((step, idx) => (
                      <div key={idx} className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
                        <span className="text-zinc-400 font-bold whitespace-nowrap text-[10px]">Step {idx + 1} ({step.direction}):</span>
                        <span className="text-indigo-300 text-[9px] sm:text-[10px] break-all sm:truncate sm:max-w-[280px]">{step.sibling_hash}</span>
                      </div>
                    ))}
                  </div>

                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1.5">
                    <div className="flex flex-col sm:flex-row sm:justify-between text-[10px] gap-0.5">
                      <span className="text-zinc-500 whitespace-nowrap">Target Leaf Hash:</span>
                      <span className="text-zinc-300 break-all sm:truncate sm:max-w-[260px]">{proofData.target_leaf_hash}</span>
                    </div>
                    <div className="flex flex-col sm:flex-row sm:justify-between text-[10px] gap-0.5">
                      <span className="text-zinc-500 whitespace-nowrap">Reconstructed Root:</span>
                      <span className="text-emerald-400 break-all sm:truncate sm:max-w-[260px]">{verifyResult.computed_root}</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-indigo-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Cryptographic Evidence Non-Repudiation
                    </div>
                    {verifyResult.prosecutors_fallacy_shield}
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
