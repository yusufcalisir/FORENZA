"use client";

import { useState, useEffect, useMemo, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  GitBranch,
  ShieldCheck,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Lock,
  ArrowRight,
  FileCheck,
  Layers,
  Hash,
  Cpu,
  Check,
  Database,
  ExternalLink,
} from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";
import { useForensicCaseStore } from "@/store/forensicCaseStore";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

// ─── Cryptographic FIPS 180-4 SHA-256 Synchronous Bitwise Engine ─────────────

function sha256Sync(ascii: string): string {
  function rightRotate(value: number, amount: number): number {
    return (value >>> amount) | (value << (32 - amount));
  }
  const maxWord = Math.pow(2, 32);
  const hash = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  ];
  const k = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ];

  const utf8: number[] = [];
  for (let i = 0; i < ascii.length; i++) {
    let charcode = ascii.charCodeAt(i);
    if (charcode < 0x80) {
      utf8.push(charcode);
    } else if (charcode < 0x800) {
      utf8.push(0xc0 | (charcode >> 6), 0x80 | (charcode & 0x3f));
    } else if (charcode < 0xd800 || charcode >= 0xe000) {
      utf8.push(0xe0 | (charcode >> 12), 0x80 | ((charcode >> 6) & 0x3f), 0x80 | (charcode & 0x3f));
    } else {
      i++;
      charcode = 0x10000 + (((charcode & 0x3ff) << 10) | (ascii.charCodeAt(i) & 0x3ff));
      utf8.push(
        0xf0 | (charcode >> 18),
        0x80 | ((charcode >> 12) & 0x3f),
        0x80 | ((charcode >> 6) & 0x3f),
        0x80 | (charcode & 0x3f)
      );
    }
  }

  const utf8BitLength = utf8.length * 8;
  utf8.push(0x80);
  while (utf8.length % 64 !== 56) {
    utf8.push(0);
  }
  const highBits = Math.floor(utf8BitLength / maxWord);
  const lowBits = utf8BitLength >>> 0;
  for (let b = 3; b >= 0; b--) utf8.push((highBits >>> (b * 8)) & 0xff);
  for (let b = 3; b >= 0; b--) utf8.push((lowBits >>> (b * 8)) & 0xff);

  for (let chunk = 0; chunk < utf8.length; chunk += 64) {
    const w: number[] = [];
    for (let i = 0; i < 16; i++) {
      w[i] =
        (utf8[chunk + i * 4] << 24) |
        (utf8[chunk + i * 4 + 1] << 16) |
        (utf8[chunk + i * 4 + 2] << 8) |
        utf8[chunk + i * 4 + 3];
    }
    for (let i = 16; i < 64; i++) {
      const s0 = rightRotate(w[i - 15], 7) ^ rightRotate(w[i - 15], 18) ^ (w[i - 15] >>> 3);
      const s1 = rightRotate(w[i - 2], 17) ^ rightRotate(w[i - 2], 19) ^ (w[i - 2] >>> 10);
      w[i] = (w[i - 16] + s0 + w[i - 7] + s1) >>> 0;
    }

    let a = hash[0],
      b = hash[1],
      c = hash[2],
      d = hash[3];
    let e = hash[4],
      f = hash[5],
      g = hash[6],
      h = hash[7];

    for (let i = 0; i < 64; i++) {
      const s1 = rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25);
      const ch = (e & f) ^ (~e & g);
      const temp1 = (h + s1 + ch + k[i] + w[i]) >>> 0;
      const s0 = rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (s0 + maj) >>> 0;

      h = g;
      g = f;
      f = e;
      e = (d + temp1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (temp1 + temp2) >>> 0;
    }

    hash[0] = (hash[0] + a) >>> 0;
    hash[1] = (hash[1] + b) >>> 0;
    hash[2] = (hash[2] + c) >>> 0;
    hash[3] = (hash[3] + d) >>> 0;
    hash[4] = (hash[4] + e) >>> 0;
    hash[5] = (hash[5] + f) >>> 0;
    hash[6] = (hash[6] + g) >>> 0;
    hash[7] = (hash[7] + h) >>> 0;
  }

  return hash.map((h) => (h >>> 0).toString(16).padStart(8, "0")).join("");
}

// ─── Interfaces & Protocol Types ──────────────────────────────────────────────

export interface CustodyEvent {
  event_id: string;
  timestamp_iso: string;
  officer_id: string;
  sample_barcode: string;
  location_id: string;
  action_type: string;
  notes?: string;
}

export interface MerkleProofStep {
  sibling_hash: string;
  direction: string;
}

export interface MerkleProofResponse {
  target_event_id: string;
  target_event_index: number;
  target_leaf_hash: string;
  merkle_root: string;
  proof_path: MerkleProofStep[];
  path_length: number;
}

export interface VerificationResponse {
  is_valid: boolean;
  computed_root: string;
  expected_root: string;
  verdict: string;
  steps_evaluated: number;
  step_trace: string[];
  prosecutors_fallacy_shield: string;
}

export interface MerkleTreeResult {
  merkle_root: string;
  total_events: number;
  tree_depth: number;
  leaf_hashes: string[];
  layers: string[][];
}

const GENESIS_PRIOR_HASH = "0".repeat(64);

// Canonical string serialization matching backend ForensicMerkleLedgerEngine
export function canonicalString(ev: CustodyEvent, priorHash: string): string {
  return `${ev.event_id}|${ev.timestamp_iso}|${ev.officer_id}|${ev.sample_barcode}|${ev.location_id}|${priorHash}`;
}

// Client-side deterministic Merkle tree builder matching backend verbatim
export function buildClientMerkleTree(events: CustodyEvent[]): MerkleTreeResult {
  if (!events || events.length === 0) {
    throw new Error("Events list must not be empty.");
  }

  const leafHashes: string[] = [];
  let priorHash = GENESIS_PRIOR_HASH;
  for (const ev of events) {
    const canon = canonicalString(ev, priorHash);
    const h = sha256Sync(canon);
    leafHashes.push(h);
    priorHash = h;
  }

  const layers: string[][] = [leafHashes];
  let currentLayer = leafHashes;

  while (currentLayer.length > 1) {
    const nextLayer: string[] = [];
    const n = currentLayer.length;
    for (let i = 0; i < n; i += 2) {
      const left = currentLayer[i];
      const right = i + 1 < n ? currentLayer[i + 1] : left;
      const parent = sha256Sync(left + right);
      nextLayer.push(parent);
    }
    layers.push(nextLayer);
    currentLayer = nextLayer;
  }

  return {
    merkle_root: currentLayer[0],
    total_events: events.length,
    tree_depth: layers.length - 1,
    leaf_hashes: leafHashes,
    layers,
  };
}

// Client-side inclusion proof generator matching backend verbatim
export function generateClientInclusionProof(
  events: CustodyEvent[],
  targetEventIndex: number
): MerkleProofResponse {
  if (targetEventIndex < 0 || targetEventIndex >= events.length) {
    throw new Error(`Target index ${targetEventIndex} out of range.`);
  }

  const treeInfo = buildClientMerkleTree(events);
  const layers = treeInfo.layers;
  const proofPath: MerkleProofStep[] = [];
  let currentIdx = targetEventIndex;

  for (let d = 0; d < layers.length - 1; d++) {
    const layer = layers[d];
    const n = layer.length;
    if (currentIdx % 2 === 0) {
      const siblingIdx = currentIdx + 1 < n ? currentIdx + 1 : currentIdx;
      proofPath.push({ sibling_hash: layer[siblingIdx], direction: "RIGHT" });
    } else {
      const siblingIdx = currentIdx - 1;
      proofPath.push({ sibling_hash: layer[siblingIdx], direction: "LEFT" });
    }
    currentIdx = Math.floor(currentIdx / 2);
  }

  const targetEvent = events[targetEventIndex];
  const targetLeafHash = treeInfo.leaf_hashes[targetEventIndex];

  return {
    target_event_id: targetEvent.event_id,
    target_event_index: targetEventIndex,
    target_leaf_hash: targetLeafHash,
    merkle_root: treeInfo.merkle_root,
    proof_path: proofPath,
    path_length: proofPath.length,
  };
}

// Client-side proof verification matching backend verbatim
export function verifyClientInclusionProof(
  leafHash: string,
  proofPath: MerkleProofStep[],
  expectedRoot: string,
  isTr: boolean = false
): VerificationResponse {
  let currentHash = leafHash;
  const stepTrace = [currentHash];

  for (const step of proofPath) {
    const sibling = step.sibling_hash;
    const direction = (step.direction || "RIGHT").toUpperCase();
    if (direction === "RIGHT") {
      currentHash = sha256Sync(currentHash + sibling);
    } else {
      currentHash = sha256Sync(sibling + currentHash);
    }
    stepTrace.push(currentHash);
  }

  const isValid = currentHash.toLowerCase() === expectedRoot.toLowerCase();
  const shieldStatement = isTr
    ? "ISO/IEC 17025:2017 & FRE 702 Delil Zinciri Bütünlük Güvencesi: Kriptografik Merkle dahiliyet ispatları, delil durum geçişlerinin değiştirilmemiş bir sırada gerçekleştiğini matematiksel olarak garanti eder. Olay zaman damgasındaki veya barkoddaki tek bir karakterlik oynama bile kök hash'i 1 - 2^-256 olasılıkla bozar."
    : "ISO/IEC 17025:2017 & FRE 702 Chain of Custody Integrity Shield: Cryptographic Merkle inclusion proofs mathematically guarantee that evidence transitions occurred in an unaltered sequence. Any tampering with event timestamps, barcodes, or handler IDs alters the root hash with probability 1 - 2^-256.";

  return {
    is_valid: isValid,
    computed_root: currentHash,
    expected_root: expectedRoot,
    verdict: isValid
      ? isTr
        ? "GEÇERLİ (Kabul Edilebilir Delil)"
        : "VALID (Admissible Evidence)"
      : isTr
      ? "GEÇERSİZ (Müdahale Edilmiş / Bozulmuş Zincir)"
      : "INVALID (Tampered / Corrupted Chain)",
    steps_evaluated: proofPath.length,
    step_trace: stepTrace,
    prosecutors_fallacy_shield: shieldStatement,
  };
}

const DEFAULT_EVENTS: CustodyEvent[] = [
  {
    event_id: "EVT-001",
    timestamp_iso: "2026-08-16T08:15:00Z",
    officer_id: "DET-MILLER-704",
    sample_barcode: "BC-DNA-99104",
    location_id: "CRIME_SCENE_SECTOR_A",
    action_type: "COLLECTION",
    notes: "Biological swab secured in sterile barcoded envelope.",
  },
  {
    event_id: "EVT-002",
    timestamp_iso: "2026-08-16T09:30:00Z",
    officer_id: "OFFICER-CHEN-122",
    sample_barcode: "BC-DNA-99104",
    location_id: "EVIDENCE_TRANSPORT_VEHICLE",
    action_type: "TRANSFER",
    notes: "Chain of custody handoff to central logistics.",
  },
  {
    event_id: "EVT-003",
    timestamp_iso: "2026-08-16T11:00:00Z",
    officer_id: "TECH-DAVIS-301",
    sample_barcode: "BC-DNA-99104",
    location_id: "CENTRAL_LAB_ACCESSIONING",
    action_type: "ACCESSION",
    notes: "Sample logged into LIMS with barcode verification.",
  },
  {
    event_id: "EVT-004",
    timestamp_iso: "2026-08-16T13:45:00Z",
    officer_id: "DR-CONNOR-042",
    sample_barcode: "BC-DNA-99104",
    location_id: "EXTRACTION_SUITE_B",
    action_type: "EXTRACTION",
    notes: "Automated magnetic bead DNA extraction completed.",
  },
];

export default function MerkleLedgerPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const { auditTrail, activeCase } = useForensicCaseStore();
  const [activeTab, setActiveTab] = useState<"tree" | "proof">("tree");

  // Synchronize active case audit trail into custody events
  const dynamicEvents: CustodyEvent[] = useMemo(() => {
    return auditTrail && auditTrail.length > 0
      ? auditTrail.slice(0, 8).map((log, idx) => ({
          event_id: log.id || `EVT-00${idx + 1}`,
          timestamp_iso: log.timestamp || "2026-08-16T12:00:00Z",
          officer_id: log.analyst || (isTr ? "KIDEMLI-ADLI-UZMAN" : "LEAD-FORENSIC-ANALYST"),
          sample_barcode: activeCase.profile.profileId || "BC-DNA-99104",
          location_id: log.module || "EVIDENCE_LEDGER",
          action_type: log.status || "COLLECTION",
          notes: log.event || (isTr ? "Kriptografik denetim kaydı işlendi." : "Audit log cryptographic event recorded."),
        }))
      : DEFAULT_EVENTS;
  }, [auditTrail, activeCase.profile.profileId, isTr]);

  const [baselineEvents, setBaselineEvents] = useState<CustodyEvent[]>(dynamicEvents);
  const [events, setEvents] = useState<CustodyEvent[]>(dynamicEvents);
  const [isTampered, setIsTampered] = useState<boolean>(false);
  const [selectedEventIndex, setSelectedEventIndex] = useState<number>(0);
  const [isRehashing, setIsRehashing] = useState<boolean>(false);
  const [proofLoading, setProofLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [stageText, setStageText] = useState<string>("");
  const [lastActionTime, setLastActionTime] = useState<string | null>(null);

  // Compute deterministic initial tree immediately on render
  const initialTree = useMemo(() => buildClientMerkleTree(dynamicEvents), [dynamicEvents]);
  const [merkleRoot, setMerkleRoot] = useState<string>(initialTree.merkle_root);
  const [leafHashes, setLeafHashes] = useState<string[]>(initialTree.leaf_hashes);

  const initialProof = useMemo(() => {
    try {
      return generateClientInclusionProof(dynamicEvents, 0);
    } catch {
      return null;
    }
  }, [dynamicEvents]);

  const initialVerify = useMemo(() => {
    if (!initialProof) return null;
    return verifyClientInclusionProof(
      initialProof.target_leaf_hash,
      initialProof.proof_path,
      initialTree.merkle_root,
      isTr
    );
  }, [initialProof, initialTree.merkle_root, isTr]);

  const [proofData, setProofData] = useState<MerkleProofResponse | null>(initialProof);
  const [verifyResult, setVerifyResult] = useState<VerificationResponse | null>(initialVerify);

  // Keep baseline synchronized with dynamic events when not in tampered state
  useEffect(() => {
    if (!isTampered) {
      setBaselineEvents(dynamicEvents);
      setEvents(dynamicEvents);
      const computed = buildClientMerkleTree(dynamicEvents);
      setMerkleRoot(computed.merkle_root);
      setLeafHashes(computed.leaf_hashes);
      const p = generateClientInclusionProof(dynamicEvents, selectedEventIndex < dynamicEvents.length ? selectedEventIndex : 0);
      setProofData(p);
      setVerifyResult(verifyClientInclusionProof(p.target_leaf_hash, p.proof_path, computed.merkle_root, isTr));
    }
  }, [dynamicEvents, isTampered, selectedEventIndex, isTr]);

  const getLocalizedActionType = (action: string) => {
    if (!isTr) return action;
    switch (action) {
      case "PASS":
        return "DOGRULANDI";
      case "FAIL":
        return "BASARISIZ";
      case "WARNING":
        return "UYARI";
      case "COLLECTION":
        return "DELIL TOPLAMA";
      case "TRANSFER":
        return "SEVKIYAT / NAKIL";
      case "ACCESSION":
        return "LIMS KABUL";
      case "EXTRACTION":
        return "DNA EKSTRAKSIYONU";
      case "SEALED":
        return "MUHURLENDI";
      default:
        return action;
    }
  };

  const getLocalizedLocation = (loc: string) => {
    if (!isTr) return loc;
    if (loc.includes("Post-Mortem")) return "25. Olum Sonrasi Toksikokinetik";
    if (loc.includes("Circom")) return "27. Circom ZKP Denetcisi";
    if (loc === "CRIME_SCENE_SECTOR_A") return "OLAY_YERI_SEKTOR_A";
    if (loc === "EVIDENCE_TRANSPORT_VEHICLE") return "DELIL_NAKIL_ARACI";
    if (loc === "CENTRAL_LAB_ACCESSIONING") return "MERKEZ_LAB_NUMUNE_KABUL";
    if (loc === "EXTRACTION_SUITE_B") return "EKSTRAKSIYON_LAB_B";
    if (loc === "EVIDENCE_LEDGER") return "DELIL_DEFTERI";
    return loc;
  };

  const getLocalizedNotes = (notes?: string) => {
    if (!notes) return "";
    if (!isTr) return notes;
    if (notes.includes("Biological swab secured in sterile barcoded envelope.")) {
      return "Biyolojik suruntu steril barkodlu zarfa alindi.";
    }
    if (notes.includes("Chain of custody handoff to central logistics.")) {
      return "Delil zinciri merkezi lojistik birimine teslim edildi.";
    }
    if (notes.includes("Sample logged into LIMS with barcode verification.")) {
      return "Numune barkod dogrulamasi ile LIMS sistemine islendi.";
    }
    if (notes.includes("Automated magnetic bead DNA extraction completed.")) {
      return "Manyetik boncuk tabanli otomatik DNA ekstraksiyonu tamamlandi.";
    }
    return notes;
  };

  const fetchTree = async (currentEvents: CustodyEvent[]) => {
    if (isRehashing) return;
    setIsRehashing(true);
    setProgress(20);
    setStageText(
      isTr
        ? "N delil zinciri yaprak taahhutleri hashleniyor (h_i = SHA-256(olay_i))..."
        : "Hashing N custody event leaf commitments (h_i = SHA-256(event_i))..."
    );

    const API_BASE = getApiBaseUrl();

    // Fallback deterministic client computation immediately available
    const localTree = buildClientMerkleTree(currentEvents);

    const t1 = setTimeout(() => {
      setProgress(55);
      setStageText(
        isTr
          ? "Ikili dengeli Merkle agaci ebeveyn katmanlari H(h_L || h_R) insa ediliyor..."
          : "Building binary balanced Merkle tree parent layers H(h_L || h_R)..."
      );
    }, 200);

    const t2 = setTimeout(() => {
      setProgress(85);
      setStageText(
        isTr
          ? "256-bit degismez kok taahhudu R_Merkle hesaplaniyor..."
          : "Computing 256-bit immutable root commitment R_Merkle..."
      );
    }, 450);

    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/lims/merkle/build-tree`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events: currentEvents }),
        signal: AbortSignal.timeout(3000),
      });
      if (res.ok) {
        const data = await res.json();
        setMerkleRoot(data.merkle_root);
        setLeafHashes(data.leaf_hashes);
      } else {
        setMerkleRoot(localTree.merkle_root);
        setLeafHashes(localTree.leaf_hashes);
      }
    } catch {
      setMerkleRoot(localTree.merkle_root);
      setLeafHashes(localTree.leaf_hashes);
    } finally {
      setTimeout(() => {
        clearTimeout(t1);
        clearTimeout(t2);
        setProgress(100);
        setStageText(
          isTr
            ? "Merkle agaci degismez kok taahhudune baglandi."
            : "Merkle tree anchored to immutable root commitment."
        );
        setTimeout(() => {
          setIsRehashing(false);
          setLastActionTime(
            isTr
              ? `Yeniden hashleme ${new Date().toLocaleTimeString()}`
              : `Rehashed at ${new Date().toLocaleTimeString()}`
          );
        }, 200);
      }, 650);
    }
  };

  const handleTamperToggle = () => {
    const nextTamper = !isTampered;
    setIsTampered(nextTamper);

    if (nextTamper) {
      // Alter event 1 timestamp by 1 second on top of current baseline
      const tampered = [...baselineEvents];
      if (tampered.length > 1) {
        tampered[1] = {
          ...tampered[1],
          timestamp_iso: "2026-08-16T09:30:01Z",
        };
      } else if (tampered.length > 0) {
        tampered[0] = {
          ...tampered[0],
          timestamp_iso: "2026-08-16T08:15:01Z",
        };
      }
      setEvents(tampered);
      const comp = buildClientMerkleTree(tampered);
      setMerkleRoot(comp.merkle_root);
      setLeafHashes(comp.leaf_hashes);
      fetchTree(tampered);
    } else {
      // Cleanly restore exact original baseline events
      setEvents(baselineEvents);
      const comp = buildClientMerkleTree(baselineEvents);
      setMerkleRoot(comp.merkle_root);
      setLeafHashes(comp.leaf_hashes);
      fetchTree(baselineEvents);
    }
  };

  const generateProof = async (idx: number) => {
    // Instant deterministic client proof calculation
    const localProof = generateClientInclusionProof(events, idx);
    const localVerify = verifyClientInclusionProof(
      localProof.target_leaf_hash,
      localProof.proof_path,
      merkleRoot,
      isTr
    );
    setProofData(localProof);
    setVerifyResult(localVerify);
    setProofLoading(true);

    const API_BASE = getApiBaseUrl();
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/lims/merkle/generate-proof`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          events,
          target_event_index: idx,
        }),
        signal: AbortSignal.timeout(3000),
      });
      if (res.ok) {
        const data: MerkleProofResponse = await res.json();
        setProofData(data);

        // Auto verify against current root via API
        const verRes = await fetch(`${API_BASE}/api/v1/forensic/lims/merkle/verify-proof`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            leaf_hash: data.target_leaf_hash,
            proof_path: data.proof_path,
            expected_root: merkleRoot,
          }),
          signal: AbortSignal.timeout(3000),
        });
        if (verRes.ok) {
          const verData = await verRes.json();
          setVerifyResult(verData);
        }
      }
    } catch {
      // Retain localProof and localVerify
    } finally {
      setProofLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Modern Unified Benchmark & Standards Mission Bar ────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        {/* Top: Engine Identity & Technical Verification Badges */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400 shrink-0">
              <GitBranch className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "Merkle Agaci Delil Zinciri Defteri" : "Merkle Tree Chain-of-Custody"}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/30 text-indigo-300">
                  ISO 17025 • SHA-256 • O(log2 N)
                </span>
              </div>
              <p className="text-[10px] text-zinc-400 mt-0.5">
                {isTr
                  ? "Kriptografik SHA-256 yaprak baglama ve ikili agac taahhudu ile degismez delil zinciri denetimi"
                  : "Cryptographic SHA-256 leaf chaining and binary tree commitment for immutable custody audit"}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {lastActionTime && (
              <span className="text-[9px] text-emerald-400 font-bold bg-white/[0.03] border border-white/10 px-2.5 py-1 rounded-lg flex items-center gap-1">
                <Check className="w-3 h-3" />
                {lastActionTime}
              </span>
            )}

            <button
              type="button"
              onClick={handleTamperToggle}
              className={`px-3 py-1.5 rounded-xl border text-[10px] font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer whitespace-nowrap ${
                isTampered
                  ? "bg-rose-500/20 text-rose-300 border-rose-500/50 animate-pulse font-extrabold"
                  : "bg-black/50 text-zinc-400 border-tactical-border/60 hover:text-zinc-200"
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              {isTampered
                ? isTr
                  ? "Mudahale Edildi (+1s)"
                  : "Tampered (+1s)"
                : isTr
                ? "Mudahale Simule Et"
                : "Simulate Tamper"}
            </button>

            <div className="flex bg-black/60 p-1 rounded-xl border border-tactical-border/60">
              <button
                type="button"
                onClick={() => setActiveTab("tree")}
                className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                  activeTab === "tree"
                    ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/50 shadow-sm"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {isTr ? "Delil Agaci" : "Custody Tree"}
              </button>
              <button
                type="button"
                onClick={() => {
                  setActiveTab("proof");
                  generateProof(selectedEventIndex);
                }}
                className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                  activeTab === "proof"
                    ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/50 shadow-sm"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {isTr ? "Kapsama Ispati" : "Inclusion Proof"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ── Active Progress Bar (Only during explicit tree rehash) ── */}
      <AnimatePresence>
        {isRehashing && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="rounded-xl border border-indigo-500/40 bg-indigo-500/10 p-3.5 space-y-2 overflow-hidden shadow-lg"
          >
            <div className="flex items-center justify-between text-xs text-indigo-300">
              <span className="flex items-center gap-2 font-bold truncate">
                <Cpu className="w-4 h-4 animate-pulse text-indigo-400 shrink-0" />
                {stageText}
              </span>
              <span className="font-mono font-black tabular-nums text-sm">%{progress}</span>
            </div>
            <div className="w-full bg-zinc-900 rounded-full h-2.5 overflow-hidden border border-indigo-500/20">
              <motion.div
                className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-2.5 rounded-full shadow-[0_0_12px_rgba(99,102,241,0.6)]"
                initial={{ width: "5%" }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.2 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── SubTab 1: Custody Event Timeline & Merkle Tree ── */}
      {activeTab === "tree" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Custody Event Stream */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                {isTr
                  ? `Zincirlenmis Delil Olaylari (N=${events.length})`
                  : `Chained Custody Events (N=${events.length})`}
              </span>
              <button
                onClick={() => fetchTree(events)}
                disabled={isRehashing}
                className="min-h-[36px] px-3.5 py-1.5 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-black text-xs uppercase tracking-wider transition-all shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_25px_rgba(99,102,241,0.5)] disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer active:scale-95"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isRehashing ? "animate-spin" : ""}`} />
                {isRehashing
                  ? isTr
                    ? `Hesaplaniyor %${progress}...`
                    : `Rehashing ${progress}%...`
                  : isTr
                  ? "Agaci Yeniden Hesapla"
                  : "Rehash Tree"}
              </button>
            </div>

            <div className="space-y-2">
              {events.map((ev, idx) => (
                <div
                  key={ev.event_id}
                  onClick={() => {
                    setSelectedEventIndex(idx);
                  }}
                  className={`min-h-[56px] p-3 rounded-xl border text-left transition-all cursor-pointer ${
                    selectedEventIndex === idx
                      ? "border-indigo-500/80 bg-indigo-500/20 text-indigo-200 font-bold"
                      : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-bold text-zinc-200">
                      {ev.event_id} ({getLocalizedActionType(ev.action_type)})
                    </span>
                    <span className="text-[10px] text-zinc-500 font-mono">
                      {ev.timestamp_iso.slice(11, 19)} UTC
                    </span>
                  </div>
                  <div className="text-[10px] text-zinc-400">
                    {ev.officer_id} • {getLocalizedLocation(ev.location_id)}
                  </div>
                  <div className="text-[9px] text-zinc-500 mt-1 truncate">
                    {getLocalizedNotes(ev.notes)}
                  </div>
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
                      {isTr
                        ? "DEGISMEZ MERKLE KOK TAAHHUDU (R_MERKLE)"
                        : "IMMUTABLE MERKLE ROOT COMMITMENT (R_MERKLE)"}
                    </span>
                    <span className="text-xs sm:text-sm md:text-base font-black text-indigo-300 font-mono break-all block mt-0.5">
                      {merkleRoot}
                    </span>
                  </div>
                  <div className="flex flex-col items-start sm:items-end gap-1 shrink-0">
                    <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                      {isTr ? "Agac Durumu" : "Tree Status"}
                    </span>
                    <span
                      className={`text-[10px] sm:text-xs font-bold px-2.5 py-1 rounded-lg border font-mono whitespace-nowrap ${
                        isTampered
                          ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
                          : "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                      }`}
                    >
                      {isTampered
                        ? isTr
                          ? "BOZULMUS KOK"
                          : "DIVERGENT ROOT"
                        : isTr
                        ? "KOK DOGRULANDI"
                        : "ROOT ANCHORED"}
                    </span>
                  </div>
                </div>

                {/* Leaf Hashes Display */}
                <div className="space-y-2">
                  <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
                    {isTr
                      ? "Katman 0: Zincirleme SHA-256 Yaprak Dugumleri (h_i = SHA-256(event_i || h_{i-1})):"
                      : "Layer 0: Chained SHA-256 Leaf Nodes (h_i = SHA-256(event_i || h_{i-1})):"}
                  </span>
                  <div className="space-y-1.5">
                    {leafHashes.map((lh, idx) => (
                      <div
                        key={idx}
                        className="flex flex-col sm:flex-row sm:items-center justify-between p-2.5 rounded-lg bg-black/40 border border-tactical-border/40 text-[10px] font-mono gap-1.5 sm:gap-3 hover:border-indigo-500/40 transition-colors"
                      >
                        <div className="flex items-center gap-1.5 shrink-0">
                          <span className="text-indigo-400 font-bold whitespace-nowrap bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
                            H_{idx + 1} ({events[idx]?.event_id || `EVT-${idx + 1}`}):
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
                    {isTr
                      ? "ISO/IEC 17025:2017 & Hukuki Delil Guvencesi Kalkani"
                      : "ISO/IEC 17025:2017 & FRE 702 Legal Evaluative Shield"}
                  </div>
                  {isTr
                    ? "Kriptografik Merkle agaci yapilari, LIMS vaka dosyalarinda zamansal inkar edilemezligi garanti eder. Olay zaman damgalarinda, gorevlilerde veya konumlarda yapilacak tek bir karakterlik degisiklik bile 1 - 2^-256 olasilikla tamamen farkli bir kok hash uretir."
                    : "Cryptographic Merkle tree structures guarantee temporal non-repudiation in LIMS case files. Any single-character alteration to event timestamps, handlers, or locations yields an entirely divergent root with probability 1 - 2^-256."}
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
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
            <div className="border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
                {isTr ? "Denetim Yolu Icin Olay Secin" : "Select Event for Audit Path"}
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
                  className={`min-h-[48px] p-3 rounded-xl border text-left w-full transition-all cursor-pointer ${
                    selectedEventIndex === idx
                      ? "border-indigo-500/80 bg-indigo-500/20 text-indigo-300 font-bold"
                      : "border-tactical-border/40 bg-black/40 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="text-xs font-bold">
                    {ev.event_id} - {getLocalizedActionType(ev.action_type)}
                  </div>
                  <div className="text-[10px] text-zinc-400">{ev.officer_id}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Right: Proof Details & Verification */}
          <div className="lg:col-span-2 space-y-4">
            {proofLoading && (
              <div className="p-8 rounded-2xl border border-tactical-border/60 bg-tactical-surface/40 flex items-center justify-center gap-2 text-indigo-300 text-xs">
                <RefreshCw className="w-4 h-4 animate-spin" />
                {isTr ? "Kapsama ispati sentezleniyor..." : "Synthesizing inclusion proof..."}
              </div>
            )}

            {proofData && verifyResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-indigo-500/40 bg-gradient-to-br from-indigo-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-indigo-500/20 pb-3.5">
                    <div>
                      <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest block">
                        {isTr
                          ? `MERKLE KAPSAMA ISPATI (DENETIM YOLU pi_${proofData.target_event_index + 1})`
                          : `MERKLE INCLUSION PROOF (AUDIT PATH pi_${proofData.target_event_index + 1})`}
                      </span>
                      <span className="text-sm sm:text-base md:text-xl font-black text-indigo-300 font-mono">
                        {proofData.target_event_id} (
                        {isTr
                          ? `Yol Uzunlugu: ${proofData.path_length} Kardes Hash`
                          : `Path Length: ${proofData.path_length} Sibling Hashes`}
                        )
                      </span>
                    </div>
                    <div className="flex flex-col items-start sm:items-end gap-1">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "Mahkeme Kabul Edilebilirligi" : "Courtroom Admissibility"}
                      </span>
                      <span
                        className={`text-[10px] sm:text-xs font-bold px-2.5 py-1 rounded-lg border font-mono whitespace-nowrap ${
                          verifyResult.is_valid
                            ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                            : "bg-rose-500/20 text-rose-300 border-rose-500/40"
                        }`}
                      >
                        {isTr
                          ? verifyResult.is_valid
                            ? "GECERLI: INKAR EDILEMEZ ISPAT"
                            : "GECERSIZ: BOZULMUS KOK"
                          : verifyResult.verdict}
                      </span>
                    </div>
                  </div>

                  {/* Sibling Path Sequence */}
                  <div className="space-y-2">
                    <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
                      {isTr ? "O(log2 N) Kardes Hash Dolasimi:" : "O(log2 N) Sibling Hash Traversal:"}
                    </span>
                    {proofData.proof_path.map((step, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono flex flex-col sm:flex-row sm:items-center justify-between gap-1.5"
                      >
                        <span className="text-zinc-400 font-bold whitespace-nowrap text-[10px]">
                          {isTr
                            ? `Adim ${idx + 1} (${step.direction.toLowerCase() === "left" ? "Sol" : "Sag"}):`
                            : `Step ${idx + 1} (${step.direction}):`}
                        </span>
                        <span className="text-indigo-300 text-[9px] sm:text-[10px] break-all sm:truncate sm:max-w-[280px]">
                          {step.sibling_hash}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1.5">
                    <div className="flex flex-col sm:flex-row sm:justify-between text-[10px] gap-0.5">
                      <span className="text-zinc-500 whitespace-nowrap">
                        {isTr ? "Hedef Yaprak Hashi:" : "Target Leaf Hash:"}
                      </span>
                      <span className="text-zinc-300 break-all sm:truncate sm:max-w-[260px]">
                        {proofData.target_leaf_hash}
                      </span>
                    </div>
                    <div className="flex flex-col sm:flex-row sm:justify-between text-[10px] gap-0.5">
                      <span className="text-zinc-500 whitespace-nowrap">
                        {isTr ? "Yeniden Uretilen Kok:" : "Reconstructed Root:"}
                      </span>
                      <span className="text-emerald-400 break-all sm:truncate sm:max-w-[260px]">
                        {verifyResult.computed_root}
                      </span>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-indigo-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      {isTr ? "Kriptografik Delil Inkar Edilemezligi" : "Cryptographic Evidence Non-Repudiation"}
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
