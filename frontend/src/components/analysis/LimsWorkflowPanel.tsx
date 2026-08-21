"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { PackageCheck, ShieldCheck, CheckCircle2, AlertTriangle, RefreshCw, FileText, User, Tag, Clock } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

interface WorkflowStep {
  step_name: string;
  step_index: number;
  operator: string;
  instrument_id: string;
  reagent_lot: string;
  protocol_version: string;
  timestamp: string;
  step_result: string;
  pass_qc: boolean;
  hmac_signature: string;
}

export default function LimsWorkflowPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [caseId, setCaseId] = useState("CASE-2026-LIMS-01");
  const [sampleId, setSampleId] = useState("SAMPLE-DNA-101");
  const [evidenceType, setEvidenceType] = useState("Blood Stain");
  const [operatorId, setOperatorId] = useState("OP-042");
  const [reagentLot, setReagentLot] = useState("LOT-EXT-2026-X42");

  const [loading, setLoading] = useState(false);
  const [auditChain, setAuditChain] = useState<WorkflowStep[]>([
    {
      step_name: "SAMPLE_ACCESSIONING",
      step_index: 2,
      operator: "Tech John",
      instrument_id: "ACCESSIONING_BENCH_01",
      reagent_lot: "LOT-ACC-2026-01",
      protocol_version: "ISO-SOP-ACC-v1.0",
      timestamp: "2026-08-12T13:40:00Z",
      step_result: "Accessioned successfully under CASE-2026-LIMS-01",
      pass_qc: true,
      hmac_signature: "e7f3b89a012c45de678f90ab12cd34ef567890ab12cd34ef567890ab12cd34ef"
    },
    {
      step_name: "DNA_EXTRACTION",
      step_index: 3,
      operator: "OP-042",
      instrument_id: "QIAGEN_EZ1_01",
      reagent_lot: "LOT-EXT-2026-X42",
      protocol_version: "ISO-SOP-EXT-v2.1",
      timestamp: "2026-08-12T13:42:15Z",
      step_result: "Extracted 150 uL DNA solution, yield 4.2 ng/uL",
      pass_qc: true,
      hmac_signature: "a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef"
    },
    {
      step_name: "QPCR_QUANTIFICATION",
      step_index: 4,
      operator: "OP-042",
      instrument_id: "QUANTSTUDIO_6_PRO",
      reagent_lot: "LOT-QT-2026-88",
      protocol_version: "ISO-SOP-QUANT-v3.0",
      timestamp: "2026-08-12T13:45:00Z",
      step_result: "SA conc: 0.85 ng/uL, LA conc: 0.80 ng/uL, DI: 1.06 (Intact)",
      pass_qc: true,
      hmac_signature: "c4d5e6f7a8b901234567890abcdef1234567890abcdef1234567890abcdef123"
    }
  ]);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const recordNextStep = async (stepName: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/lims/workflow/step`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sample_id: sampleId,
          step_name: stepName,
          operator_id: operatorId,
          instrument_id: "APPLIED_BIOSYSTEMS_3500XL",
          reagent_lot: reagentLot,
          protocol_version: "ISO-SOP-DNA-v4.2",
          step_result: `Execution of ${stepName} completed under ISO 17025 standard`,
          pass_qc: true
        })
      });
      if (res.ok) {
        const newStep = await res.json();
        setAuditChain((prev) => [...prev, newStep]);
      }
    } catch (e) {
      console.error("LIMS step recording failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const phases = [
    { en: "Case Reg", tr: "Vaka Kayıt" },
    { en: "Evidence", tr: "Delil Kabul" },
    { en: "Accession", tr: "Numune Kayıt" },
    { en: "Extraction", tr: "Ekstraksiyon" },
    { en: "Quant qPCR", tr: "Kant qPCR" },
    { en: "PCR Amp", tr: "PCR Çoğaltım" },
    { en: "CE / NGS", tr: "CE / NGS" },
    { en: "Biocomp", tr: "Biyohesap" },
    { en: "ISO Report", tr: "ISO Rapor" },
  ];

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300">
            <PackageCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                {isTr
                  ? "LIMS-Lite Numune Kabulü & İş Akışı Takibi"
                  : "LIMS-Lite Sample Accessioning & Workflow Tracking"}
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                {isTr ? "ISO 17025 ZİNCİRİ" : "ISO 17025 CHAIN"}
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              {isTr
                ? "9 Aşamalı Adli SOP Delil Zinciri & Reaktif Parti Denetim Kaydı"
                : "9-Step Forensic SOP Chain-of-Custody & Reagent Lot Audit Trail"}
            </p>
          </div>
        </div>
      </div>

      {/* ── 9-Step SOP Stepper ── */}
      <div className="p-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 space-y-3">
        <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
          {isTr
            ? "9 Aşamalı Standart Operasyon Prosedürü (SOP) İlerlemesi"
            : "9-Phase Standard Operating Protocol (SOP) Progression"}
        </span>
        <div className="grid grid-cols-3 sm:grid-cols-9 gap-2 text-center text-[9px] font-bold font-mono">
          {phases.map((phase, idx) => {
            const isDone = idx < auditChain.length + 1;
            return (
              <div
                key={phase.en}
                className={`p-2 rounded-lg border flex flex-col items-center justify-center gap-1 ${
                  isDone ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-300" : "border-tactical-border/40 bg-black/30 text-zinc-600"
                }`}
              >
                <span className="text-[8px] text-zinc-500">P{idx + 1}</span>
                <span>{isTr ? phase.tr : phase.en}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Audit Chain List ── */}
      <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            {isTr
              ? `HMAC-SHA256 Bağlantılı Delil Zinciri Günlüğü (${auditChain.length} Adım Kaydedildi)`
              : `HMAC-SHA256 Chained Chain-of-Custody Log (${auditChain.length} Steps Recorded)`}
          </span>
          <button
            onClick={() => recordNextStep("PCR_AMPLIFICATION")}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs uppercase tracking-wider flex items-center gap-1.5 transition-all cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
            {isTr ? "PCR Çoğaltım Adımını Kaydet" : "Record PCR Amplification Step"}
          </button>
        </div>

        <div className="space-y-3">
          {auditChain?.map((step, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-4 rounded-xl border border-emerald-500/20 bg-black/40 space-y-2 text-xs font-mono"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800 pb-2">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    {isTr ? `ADIM ${step?.step_index}: ${step?.step_name}` : `STEP ${step?.step_index}: ${step?.step_name}`}
                  </span>
                  <span className="text-zinc-400 text-[10px] flex items-center gap-1">
                    <User className="w-3 h-3 text-zinc-500" /> {step?.operator}
                  </span>
                </div>
                <span className="text-[10px] text-zinc-500 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-zinc-500" /> {step?.timestamp}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[10px] text-zinc-400">
                <div>{isTr ? "Cihaz:" : "Instrument:"} <span className="text-zinc-200 font-bold">{step.instrument_id}</span></div>
                <div>{isTr ? "Reaktif Partisi:" : "Reagent Lot:"} <span className="text-cyan-400 font-bold">{step.reagent_lot}</span></div>
                <div>{isTr ? "SOP Protokolü:" : "SOP Protocol:"} <span className="text-purple-300 font-bold">{step.protocol_version}</span></div>
              </div>

              <div className="text-zinc-300 text-[11px] pt-1">
                {isTr ? "Sonuç:" : "Result:"} <span className="text-emerald-300">{step.step_result}</span>
              </div>

              <div className="text-[8px] text-zinc-600 font-mono truncate pt-1 border-t border-zinc-900">
                HMAC SHA256 {isTr ? "İmzası" : "Signature"}: {step.hmac_signature}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
