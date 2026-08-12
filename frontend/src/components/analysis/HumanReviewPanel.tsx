"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { UserCheck, ShieldCheck, CheckCircle2, AlertTriangle, RefreshCw, FileText, User, Lock } from "lucide-react";

interface ReviewRecord {
  review_id: string;
  sample_id: string;
  ai_recommendation: string;
  human_decision: string;
  is_override: boolean;
  override_reason?: string;
  final_verdict: string;
  primary_analyst_id: string;
  technical_reviewer_id: string;
  dual_sign_off_verified: boolean;
  timestamp: string;
  court_admissibility_status: string;
  hmac_signature: string;
}

export default function HumanReviewPanel() {
  const [decisionType, setDecisionType] = useState<string>("APPROVE_AI_PREDICATE");
  const [primaryAnalyst, setPrimaryAnalyst] = useState<string>("ANALYST-01 (Dr. Sarah Connor)");
  const [technicalReviewer, setTechnicalReviewer] = useState<string>("PEER-REVIEWER-02 (Dr. James Vance)");
  const [overrideReason, setOverrideReason] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const [reviewResult, setReviewResult] = useState<ReviewRecord | null>({
    review_id: "REV-1786480000",
    sample_id: "SAMPLE-DNA-01",
    ai_recommendation: "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION (LR = 10^26)",
    human_decision: "APPROVE_AI_PREDICATE",
    is_override: false,
    final_verdict: "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION",
    primary_analyst_id: "ANALYST-01 (Dr. Sarah Connor)",
    technical_reviewer_id: "PEER-REVIEWER-02 (Dr. James Vance)",
    dual_sign_off_verified: true,
    timestamp: "2026-08-12T13:51:00Z",
    court_admissibility_status: "CERTIFIED_COURT_ADMISSIBLE",
    hmac_signature: "7f8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b"
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const submitDecision = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/review/submit-decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sample_id: "SAMPLE-DNA-01",
          ai_recommendation: "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION (LR = 10^26)",
          human_decision: decisionType,
          primary_analyst_id: primaryAnalyst,
          technical_reviewer_id: technicalReviewer,
          override_reason: decisionType === "OVERRIDE_MODIFIED_PREDICATE" ? overrideReason : null,
          final_verdict: decisionType === "APPROVE_AI_PREDICATE" ? "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION" : "OVERRIDDEN_BY_ANALYST"
        })
      });
      if (res.ok) {
        const data = await res.json();
        setReviewResult(data);
      }
    } catch (e) {
      console.error("Human review submission failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-amber-500/30 bg-amber-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-300">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Human Analyst Review & Dual-Sign-Off Decision Governance
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                COURT ADMISSIBLE
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              Strict Human-in-the-Loop Dual Sign-Off & Analyst Override Audit Logging
            </p>
          </div>
        </div>

        <button
          onClick={submitDecision}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Sign & Authorize Verdict
        </button>
      </div>

      {/* ── AI Recommendation vs Human Decision Layout ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left: Computational Recommendation & Analyst Decision Controls */}
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
          <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block border-b border-tactical-border/40 pb-3">
            Primary Analyst & Secondary Reviewer Sign-Off Form
          </span>

          <div className="p-3 rounded-xl border border-cyan-500/30 bg-cyan-500/10 space-y-1">
            <span className="text-[9px] text-cyan-300 font-bold uppercase">Automated AI Recommendation</span>
            <p className="text-xs font-bold text-zinc-200">
              EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION (LR = 10^26)
            </p>
          </div>

          <div className="space-y-2">
            <span className="text-[10px] text-zinc-400 uppercase font-bold">Select Analyst Verdict</span>
            <div className="grid grid-cols-1 gap-2">
              {[
                { id: "APPROVE_AI_PREDICATE", label: "Approve AI Predicate (Concordant)", desc: "Accept computational LR & verdict" },
                { id: "OVERRIDE_MODIFIED_PREDICATE", label: "Override & Modify Predicate", desc: "Requires mandatory technical justification" },
                { id: "REJECT_RE_ANALYSIS", label: "Reject & Request Re-Analysis", desc: "Sends sample back for re-extraction" },
              ].map((d) => (
                <button
                  key={d.id}
                  onClick={() => setDecisionType(d.id)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    decisionType === d.id
                      ? "border-amber-400 bg-amber-500/20 text-amber-300"
                      : "border-tactical-border/40 bg-black/30 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <div className="font-bold text-xs">{d.label}</div>
                  <div className="text-[9px] text-zinc-500">{d.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {decisionType === "OVERRIDE_MODIFIED_PREDICATE" && (
            <div className="space-y-1">
              <span className="text-[10px] text-amber-400 font-bold uppercase">Mandatory Analyst Override Justification</span>
              <textarea
                rows={3}
                placeholder="Document technical reasoning (e.g. primer binding site mutation, stutter threshold anomaly)..."
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                className="w-full p-2.5 rounded-xl border border-amber-500/40 bg-black/60 font-mono text-xs text-zinc-200 focus:outline-none"
              />
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <div className="space-y-1">
              <span className="text-[9px] text-zinc-400 uppercase font-bold">Primary Forensic Analyst</span>
              <input
                type="text"
                value={primaryAnalyst}
                onChange={(e) => setPrimaryAnalyst(e.target.value)}
                className="w-full p-2 rounded-lg border border-tactical-border/60 bg-black/60 text-xs text-zinc-200"
              />
            </div>
            <div className="space-y-1">
              <span className="text-[9px] text-zinc-400 uppercase font-bold">Secondary Peer Reviewer</span>
              <input
                type="text"
                value={technicalReviewer}
                onChange={(e) => setTechnicalReviewer(e.target.value)}
                className="w-full p-2 rounded-lg border border-tactical-border/60 bg-black/60 text-xs text-zinc-200"
              />
            </div>
          </div>
        </div>

        {/* Right: Certified Court-Admissible Output Banner */}
        <div className="space-y-4">
          {reviewResult && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4 rounded-2xl border border-amber-500/40 bg-tactical-surface/50 p-5 shadow-xl"
            >
              <div className="flex items-center justify-between border-b border-amber-500/20 pb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  Dual Sign-Off Certification Audit
                </span>
                <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold text-[9px] uppercase">
                  {reviewResult.court_admissibility_status}
                </span>
              </div>

              <div className="space-y-2 text-xs font-mono">
                <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1">
                  <span className="text-[9px] text-zinc-500 block">Final Authorized Verdict</span>
                  <span className="font-bold text-amber-300 text-sm">{reviewResult.final_verdict}</span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[10px]">
                  <div className="p-2.5 rounded-lg bg-black/30 border border-zinc-800">
                    <span className="text-zinc-500 block">Primary Analyst</span>
                    <span className="font-bold text-zinc-200">{reviewResult.primary_analyst_id}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-black/30 border border-zinc-800">
                    <span className="text-zinc-500 block">Technical Reviewer</span>
                    <span className="font-bold text-zinc-200">{reviewResult.technical_reviewer_id}</span>
                  </div>
                </div>

                {reviewResult.is_override && (
                  <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px]">
                    <span className="font-bold block text-[9px] uppercase">Analyst Override Rationale</span>
                    {reviewResult.override_reason}
                  </div>
                )}

                <div className="p-2.5 rounded-lg bg-black/60 border border-zinc-900 text-[8px] text-zinc-500 truncate">
                  HMAC Court Admissibility Hash: {reviewResult.hmac_signature}
                </div>
              </div>
            </motion.div>
          )}
        </div>

      </div>
    </div>
  );
}
