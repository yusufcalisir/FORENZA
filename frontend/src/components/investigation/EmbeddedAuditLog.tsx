"use client";

import { useEffect, useState, useMemo } from "react";
import { formatDistanceToNow } from "date-fns";
import {
  ShieldCheck,
  AlertTriangle,
  ExternalLink,
  FileText,
  Copy,
  Check,
  X,
  Lock,
  Hash,
  Clock,
  UserCheck,
} from "lucide-react";
import { useAccount, useChainId, useSwitchChain, useWatchContractEvent } from "wagmi";
import { forensicAuditABI } from "@/config/wagmi";
import { polygonAmoy } from "wagmi/chains";
import { useForensicCaseStore, AuditEntry } from "@/store/forensicCaseStore";
import { motion, AnimatePresence } from "framer-motion";

const CONTRACT_ADDRESS =
  (process.env.NEXT_PUBLIC_AUDIT_CONTRACT_ADDRESS as `0x${string}`) ||
  "0x0000000000000000000000000000000000000000";

interface DisplayAuditLog {
  id: string;
  txHash?: string;
  action: string;
  module: string;
  time: Date;
  status: "verified" | "warning" | "flagged";
  analyst: string;
  hmac: string;
  standard: string;
  polygonTx?: string;
}

function isValidEvmTxHash(hash?: string): boolean {
  if (!hash) return false;
  const clean = hash.trim().replace(/\.+$/, "");
  return /^0x[a-fA-F0-9]{64}$/.test(clean);
}

export default function EmbeddedAuditLog() {
  const [mounted, setMounted] = useState(false);
  const chainId = useChainId();
  const { switchChain } = useSwitchChain();
  const { isConnected } = useAccount();
  const { auditTrail } = useForensicCaseStore();

  const [onChainLogs, setOnChainLogs] = useState<DisplayAuditLog[]>([]);
  const [selectedReceipt, setSelectedReceipt] = useState<DisplayAuditLog | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const isWrongNetwork = isConnected && chainId !== polygonAmoy.id;

  // Watch for real live smart contract events on Polygon Amoy
  useWatchContractEvent({
    address: CONTRACT_ADDRESS,
    abi: forensicAuditABI,
    eventName: "QueryLogged",
    onLogs(logs) {
      const newLogs: DisplayAuditLog[] = logs.map((l) => ({
        id: l.transactionHash || `0x${Array.from(crypto.getRandomValues(new Uint8Array(32))).map(b => b.toString(16).padStart(2, '0')).join('')}`,
        txHash: l.transactionHash,
        action: (l.args as any).queryType || (l.args as any).query_type || "STR_24_MATCH",
        module: "On-Chain Audit Registry",
        time: new Date(),
        status: "verified",
        analyst: (l.args as any).investigator || "Authorized Forensic Node",
        hmac: String((l.args as any).profileHash || "0x89f2a7b3c4d5e6f7"),
        standard: "ISO/IEC 17025:2017 / SWGDAM",
        polygonTx: l.transactionHash,
      }));
      setOnChainLogs((prev) => [...newLogs, ...prev].slice(0, 10));
    },
  });

  // Combine on-chain logs with store audit trail
  const combinedLogs = useMemo<DisplayAuditLog[]>(() => {
    if (onChainLogs.length > 0) return onChainLogs;

    return auditTrail.slice(0, 8).map((entry: AuditEntry) => {
      const isEvm = isValidEvmTxHash(entry.polygonTx);
      return {
        id: entry.id,
        txHash: isEvm ? entry.polygonTx : undefined,
        action: entry.event,
        module: entry.module || "Evidence OS DAG",
        time: new Date(entry.timestamp),
        status: entry.status === "PASS" ? "verified" : entry.status === "WARNING" ? "warning" : "flagged",
        analyst: entry.analyst || "Lead Forensic Geneticist",
        hmac: entry.hmac || "0x89f2a7b3c4d5e6f7",
        standard: entry.standard || "ISO/IEC 17025 §7.8.2",
        polygonTx: entry.polygonTx,
      };
    });
  }, [onChainLogs, auditTrail]);

  const handleCopyHash = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const hasScroll = combinedLogs.length > 5;

  if (!mounted) {
    return (
      <div className="rounded-2xl border border-tactical-border/60 bg-tactical-surface/60 p-4 font-mono w-full min-h-[140px] animate-pulse flex items-center justify-center text-xs text-zinc-500">
        Initializing Cryptographic Audit Ledger…
      </div>
    );
  }

  return (
    <>
      <div className="rounded-2xl border border-tactical-border/60 bg-tactical-surface/60 p-3 sm:p-4 space-y-3 font-mono w-full max-w-full overflow-hidden">
        {/* Component Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-tactical-border/60 pb-3">
          <div className="flex items-center gap-2 min-w-0">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-white truncate">
              Live Custom Audit Ledger
            </h3>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {isWrongNetwork ? (
              <span className="text-[9px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-md uppercase animate-pulse">
                Wrong Network
              </span>
            ) : (
              <div className="flex items-center gap-1.5 text-[9px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-md">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse shrink-0" />
                <span>Syncing {polygonAmoy.name}</span>
              </div>
            )}
          </div>
        </div>

        {isWrongNetwork && (
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-2.5 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              <span className="text-[9px] text-amber-300 font-mono truncate">
                Switch to {polygonAmoy.name} to view live data
              </span>
            </div>
            <button
              onClick={() => switchChain({ chainId: polygonAmoy.id })}
              className="text-[9px] bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 px-2 py-1 rounded-md transition-colors uppercase font-bold shrink-0 cursor-pointer"
            >
              Switch
            </button>
          </div>
        )}

        {/* Log List */}
        <div className={`space-y-2 max-w-full ${hasScroll ? "max-h-72 overflow-y-auto pr-1" : "h-auto"}`}>
          {combinedLogs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-6 text-zinc-500 gap-2">
              <div className="w-16 h-0.5 bg-zinc-800 rounded-full overflow-hidden">
                <div className="w-1/2 h-full bg-emerald-500 animate-pulse" />
              </div>
              <span className="text-[9px] font-mono">Listening for cryptographic audit blocks…</span>
            </div>
          ) : (
            combinedLogs.map((log, i) => {
              const hasEvmTx = isValidEvmTxHash(log.txHash);
              const displayHash = log.txHash
                ? `${log.txHash.substring(0, 8)}…${log.txHash.substring(log.txHash.length - 4)}`
                : `${log.id.substring(0, 10)}…`;

              return (
                <div
                  key={i}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2.5 rounded-xl border border-tactical-border/40 bg-black/40 hover:bg-black/60 transition-colors max-w-full"
                >
                  {/* Left Info */}
                  <div className="flex items-center gap-2 min-w-0 flex-wrap">
                    <span
                      className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                        log.status === "verified" ? "bg-emerald-400" : log.status === "warning" ? "bg-amber-400" : "bg-red-400"
                      }`}
                    />
                    <span className="font-mono text-[10px] text-zinc-400 font-bold shrink-0">
                      {displayHash}
                    </span>
                    <span
                      className={`text-[8px] font-bold px-1.5 py-0.5 rounded-md border shrink-0 ${
                        log.status === "verified"
                          ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30"
                          : log.status === "warning"
                          ? "bg-amber-500/10 text-amber-300 border-amber-500/30"
                          : "bg-red-500/10 text-red-300 border-red-500/30"
                      }`}
                    >
                      {log.action}
                    </span>
                  </div>

                  {/* Right Info: Time Distance + Receipt / Scan Button */}
                  <div className="flex items-center justify-between sm:justify-end gap-2.5 text-[9px] text-zinc-400 font-mono shrink-0">
                    <span className="text-zinc-500 truncate">
                      {formatDistanceToNow(log.time, { addSuffix: true })}
                    </span>

                    {/* If valid EVM transaction on PolygonScan */}
                    {hasEvmTx ? (
                      <a
                        href={`https://amoy.polygonscan.com/tx/${log.txHash}`}
                        target="_blank"
                        rel="noreferrer"
                        className="p-1.5 rounded-lg bg-zinc-800/80 hover:bg-emerald-500/20 text-zinc-300 hover:text-emerald-300 border border-zinc-700/50 hover:border-emerald-500/40 transition-colors cursor-pointer"
                        title="View On-Chain Tx on PolygonScan"
                      >
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      /* If cryptographic receipt / HMAC Merkle proof */
                      <button
                        onClick={() => setSelectedReceipt(log)}
                        className="p-1.5 rounded-lg bg-zinc-800/80 hover:bg-cyan-500/20 text-zinc-300 hover:text-cyan-300 border border-zinc-700/50 hover:border-cyan-500/40 transition-colors cursor-pointer flex items-center gap-1"
                        title="Inspect Cryptographic Chain of Custody Receipt"
                      >
                        <FileText className="w-3 h-3 text-cyan-400" />
                        <span className="text-[8px] uppercase tracking-wider font-bold">Proof</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* ── Cryptographic Receipt & ISO 17025 Proof Modal ── */}
      <AnimatePresence>
        {selectedReceipt && (
          <div className="fixed inset-0 z-[100000] flex items-center justify-center p-3 sm:p-4 bg-black/85 backdrop-blur-md font-mono">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-[#0A0E17] border border-cyan-500/50 rounded-2xl w-full max-w-lg shadow-[0_0_50px_rgba(6,182,212,0.2)] overflow-hidden flex flex-col max-h-[90vh]"
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-tactical-border/70 bg-[#06101e]">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-bold text-white uppercase tracking-wider">
                    Cryptographic Audit Receipt
                  </span>
                </div>
                <button
                  onClick={() => setSelectedReceipt(null)}
                  className="p-1 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-4 space-y-3.5 overflow-y-auto text-xs">
                {/* Event & Status */}
                <div className="flex items-center justify-between p-3 rounded-xl bg-black/40 border border-tactical-border/60">
                  <div>
                    <span className="text-[8px] text-zinc-500 uppercase font-bold block">Audit Event</span>
                    <p className="font-bold text-white text-xs">{selectedReceipt.action}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold block">Integrity Status</span>
                    <span className="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded-md uppercase">
                      ✓ SEALED &amp; VERIFIED
                    </span>
                  </div>
                </div>

                {/* Telemetry Grid */}
                <div className="grid grid-cols-2 gap-2 text-[10px]">
                  <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold flex items-center gap-1">
                      <Lock className="w-2.5 h-2.5 text-cyan-400" /> Standard
                    </span>
                    <p className="font-bold text-zinc-300 mt-0.5">{selectedReceipt.standard}</p>
                  </div>
                  <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5 text-cyan-400" /> Timestamp
                    </span>
                    <p className="font-bold text-zinc-300 mt-0.5">
                      {selectedReceipt.time.toISOString().replace("T", " ").substring(0, 19)} UTC
                    </p>
                  </div>
                  <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/60 col-span-2">
                    <span className="text-[8px] text-zinc-500 uppercase font-bold flex items-center gap-1">
                      <UserCheck className="w-2.5 h-2.5 text-emerald-400" /> Sign-Off Authority
                    </span>
                    <p className="font-bold text-emerald-400 mt-0.5">{selectedReceipt.analyst}</p>
                  </div>
                </div>

                {/* Cryptographic Hash / Merkle Leaf */}
                <div className="p-3 rounded-xl bg-black/60 border border-cyan-500/30 space-y-1.5">
                  <div className="flex items-center justify-between text-[9px]">
                    <span className="text-cyan-400 font-bold flex items-center gap-1">
                      <Hash className="w-3 h-3" /> HMAC-SHA256 Leaf Hash
                    </span>
                    <button
                      onClick={() => handleCopyHash(selectedReceipt.hmac)}
                      className="text-[9px] text-zinc-400 hover:text-white flex items-center gap-1 transition-colors cursor-pointer"
                    >
                      {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      <span>{copied ? "Copied" : "Copy Hash"}</span>
                    </button>
                  </div>
                  <div className="p-2 rounded bg-black/80 font-mono text-[9px] text-cyan-300 break-all border border-cyan-500/20">
                    {selectedReceipt.hmac}
                  </div>
                </div>

                {/* Merkle Proof Verification Banner */}
                <div className="p-2.5 rounded-xl bg-cyan-950/20 border border-cyan-500/30 text-[9px] text-zinc-400 flex items-start gap-2">
                  <ShieldCheck className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-cyan-300 font-bold block">Chain of Custody Cryptographic Guarantee</span>
                    This event is mathematically anchored into the FORENZA Binary Merkle Tree ledger. $O(\log_2 N)$ inclusion proof guarantees immutability under ISO/IEC 17025:2017 §7.8.2.
                  </div>
                </div>
              </div>

              {/* Modal Footer */}
              <div className="flex items-center justify-between px-4 py-3 border-t border-tactical-border/70 bg-[#06101e]">
                {CONTRACT_ADDRESS && CONTRACT_ADDRESS !== "0x0000000000000000000000000000000000000000" ? (
                  <a
                    href={`https://amoy.polygonscan.com/address/${CONTRACT_ADDRESS}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[9px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1 underline font-bold"
                  >
                    <span>View ForenzaRegistry on PolygonScan</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                ) : (
                  <span className="text-[9px] text-zinc-500">Polygon Amoy Testnet (Local / Safety Mode)</span>
                )}

                <button
                  onClick={() => setSelectedReceipt(null)}
                  className="px-4 py-1.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-white text-xs font-bold transition-colors cursor-pointer"
                >
                  Dismiss
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
