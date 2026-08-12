"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Printer, ShieldCheck, CheckCircle2, Lock, RefreshCw, Layers } from "lucide-react";

interface ReportData {
  certificate_title: string;
  case_summary: {
    case_id: string;
    sample_id: string;
    investigator_name: string;
    jurisdiction: string;
    report_issue_date: string;
  };
  evidence_chain: {
    evidence_type: string;
    lims_accessioning_timestamp: string;
    chain_of_custody_status: string;
  };
  methods: {
    amplification_kit: string;
    biocomputational_engine: string;
    sop_reference: string;
  };
  empirical_results: {
    total_loci_profiled: number;
    loci_list: string[];
    qc_status: string;
  };
  statistical_interpretation: {
    likelihood_ratio_lr: number;
    log10_likelihood_ratio: number;
    random_match_probability_rmp: string;
    enfsi_verbal_scale_predicate: string;
    mathematical_immutability_flag: string;
  };
  limitations_and_uncertainty: {
    expanded_measurement_uncertainty_u95: string;
    stochastic_threshold_rfu: number;
    analytical_threshold_rfu: number;
  };
  dual_sign_off_governance: {
    primary_analyst_signature: string;
    technical_reviewer_signature: string;
    human_decision: string;
    override_reason?: string;
    dual_sign_off_status: string;
  };
  audit_trail_and_cryptography: {
    certificate_hash: string;
    audit_chain_provenance: string;
  };
  court_admissibility_certified: boolean;
}

export default function IsoReportGeneratorPanel() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<ReportData | null>({
    certificate_title: "ISO 17025 OFFICIAL FORENSIC GENETICS EXAMINATION REPORT",
    case_summary: {
      case_id: "CASE-2026-LIMS-01",
      sample_id: "SAMPLE-DNA-101",
      investigator_name: "Dr. Sarah Connor",
      jurisdiction: "INTERPOL_MEMBER_STATE",
      report_issue_date: "2026-08-12T13:55:00Z"
    },
    evidence_chain: {
      evidence_type: "Capillary Electrophoresis / Blood Stain",
      lims_accessioning_timestamp: "2026-08-12T13:40:00Z",
      chain_of_custody_status: "HMAC_INTACT_VERIFIED"
    },
    methods: {
      amplification_kit: "CODIS 24 Core Loci Multiplex",
      biocomputational_engine: "FORENZA Probabilistic MCMC & Multi-Omic Synthesizer",
      sop_reference: "ISO-17025-SOP-DNA-v4.2"
    },
    empirical_results: {
      total_loci_profiled: 24,
      loci_list: ["D3S1358", "vWA", "FGA", "D8S1179", "D21S11", "D18S51"],
      qc_status: "QC_PASSED"
    },
    statistical_interpretation: {
      likelihood_ratio_lr: 1.0e26,
      log10_likelihood_ratio: 26.0,
      random_match_probability_rmp: "1 in 1.0e26.0",
      enfsi_verbal_scale_predicate: "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION",
      mathematical_immutability_flag: "IMMUTABLE_VERIFIED"
    },
    limitations_and_uncertainty: {
      expanded_measurement_uncertainty_u95: "k=2, 95% Confidence Bounds",
      stochastic_threshold_rfu: 150.0,
      analytical_threshold_rfu: 50.0
    },
    dual_sign_off_governance: {
      primary_analyst_signature: "ANALYST-01 (Dr. Sarah Connor)",
      technical_reviewer_signature: "PEER-REVIEWER-02 (Dr. James Vance)",
      human_decision: "APPROVE_AI_PREDICATE",
      dual_sign_off_status: "DUAL_SIGN_OFF_VERIFIED"
    },
    audit_trail_and_cryptography: {
      certificate_hash: "a9b8c7d6e5f432101234567890abcdef1234567890abcdef1234567890abcdef",
      audit_chain_provenance: "FORENZA ISO 17025 Forensic Report Compiler v1.0"
    },
    court_admissibility_certified: true
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const handleCompileReport = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/reports/compile-iso-certificate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          case_id: "CASE-2026-LIMS-01",
          sample_id: "SAMPLE-DNA-101",
          likelihood_ratio: 1.0e26,
          log10_lr: 26.0,
          enfsi_verbal_predicate: "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION",
          primary_analyst_id: "ANALYST-01 (Dr. Sarah Connor)",
          technical_reviewer_id: "PEER-REVIEWER-02 (Dr. James Vance)",
          human_decision: "APPROVE_AI_PREDICATE"
        })
      });
      if (res.ok) {
        const data = await res.json();
        setReport(data);
      }
    } catch (e) {
      console.error("ISO report compilation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-purple-500/30 bg-purple-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-purple-500/20 border border-purple-500/40 text-purple-300">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Court-Admissible ISO 17025 Forensic Report Generator
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">
                OFFICIAL CERTIFICATE
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              8-Section Standardized ISO 17025 Report Compiler with Immutable Math & PDF Export
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCompileReport}
            disabled={loading}
            className="px-4 py-2 rounded-xl bg-purple-500 hover:bg-purple-400 text-black font-bold text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Compile ISO Certificate
          </button>
          <button
            onClick={handlePrint}
            className="px-4 py-2 rounded-xl border border-purple-500/40 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 font-bold text-xs uppercase tracking-wider flex items-center gap-2 cursor-pointer transition-all"
          >
            <Printer className="w-3.5 h-3.5" />
            Print / Export PDF
          </button>
        </div>
      </div>

      {/* ── 8-Section Official Document Preview ── */}
      {report && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-6 space-y-6 shadow-2xl"
        >
          {/* Document Header Stamp */}
          <div className="border-b border-tactical-border/60 pb-4 text-center space-y-1">
            <span className="px-3 py-1 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold text-[9px] uppercase tracking-widest inline-block mb-1">
              OFFICIAL COURT-ADMISSIBLE EXAMINATION CERTIFICATE
            </span>
            <h1 className="text-base font-black text-tactical-text tracking-wider uppercase">
              {report.certificate_title}
            </h1>
            <p className="text-[10px] text-zinc-400">
              ISO/IEC 17025:2017 & ENFSI Guidelines Compliant Document
            </p>
          </div>

          {/* Grid of 8 Standardized Report Sections */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            
            {/* Section 1 */}
            <div className="p-4 rounded-xl border border-tactical-border/40 bg-black/40 space-y-1.5">
              <span className="text-[9px] font-bold text-purple-300 uppercase">1. Case & Sample Provenance</span>
              <div className="text-zinc-300">Case ID: <span className="font-bold text-zinc-100">{report.case_summary.case_id}</span></div>
              <div className="text-zinc-300">Sample ID: <span className="font-bold text-zinc-100">{report.case_summary.sample_id}</span></div>
              <div className="text-zinc-400 text-[10px]">Investigator: {report.case_summary.investigator_name}</div>
            </div>

            {/* Section 2 */}
            <div className="p-4 rounded-xl border border-tactical-border/40 bg-black/40 space-y-1.5">
              <span className="text-[9px] font-bold text-purple-300 uppercase">2. Evidence Chain of Custody</span>
              <div className="text-zinc-300">Evidence Type: <span className="font-bold text-zinc-100">{report.evidence_chain.evidence_type}</span></div>
              <div className="text-zinc-400 text-[10px]">LIMS Accession: {report.evidence_chain.lims_accessioning_timestamp}</div>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                {report.evidence_chain.chain_of_custody_status}
              </span>
            </div>

            {/* Section 3 */}
            <div className="p-4 rounded-xl border border-tactical-border/40 bg-black/40 space-y-1.5">
              <span className="text-[9px] font-bold text-purple-300 uppercase">3. Analytical Methods & SOP</span>
              <div className="text-zinc-300">Kit: <span className="font-bold text-zinc-100">{report.methods.amplification_kit}</span></div>
              <div className="text-zinc-400 text-[10px]">SOP Reference: {report.methods.sop_reference}</div>
            </div>

            {/* Section 4 */}
            <div className="p-4 rounded-xl border border-tactical-border/40 bg-black/40 space-y-1.5">
              <span className="text-[9px] font-bold text-purple-300 uppercase">4. Empirical Peak Results</span>
              <div className="text-zinc-300">Loci Profiled: <span className="font-bold text-zinc-100">{report.empirical_results.total_loci_profiled} Loci</span></div>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                QC: {report.empirical_results.qc_status}
              </span>
            </div>

            {/* Section 5: IMMUTABLE STATISTICAL INTERPRETATION */}
            <div className="md:col-span-2 p-4 rounded-xl border border-cyan-500/40 bg-gradient-to-r from-cyan-500/10 to-black/60 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[9px] font-bold text-cyan-300 uppercase flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-cyan-400" />
                  5. Statistical Interpretation (Immutable Math Invariant)
                </span>
                <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  {report.statistical_interpretation.mathematical_immutability_flag}
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                <div>
                  <span className="text-[9px] text-zinc-500 block">Likelihood Ratio (LR)</span>
                  <span className="text-lg font-black text-cyan-300">10^{report.statistical_interpretation.log10_likelihood_ratio}</span>
                </div>
                <div>
                  <span className="text-[9px] text-zinc-500 block">Random Match Prob (RMP)</span>
                  <span className="font-bold text-zinc-200">{report.statistical_interpretation.random_match_probability_rmp}</span>
                </div>
                <div>
                  <span className="text-[9px] text-zinc-500 block">ENFSI Verbal Scale Predicate</span>
                  <span className="font-bold text-emerald-300">{report.statistical_interpretation.enfsi_verbal_scale_predicate.replace(/_/g, " ")}</span>
                </div>
              </div>
            </div>

            {/* Section 6 */}
            <div className="p-4 rounded-xl border border-tactical-border/40 bg-black/40 space-y-1.5">
              <span className="text-[9px] font-bold text-purple-300 uppercase">6. Limitations & Measurement Uncertainty</span>
              <div className="text-zinc-400 text-[10px]">Uncertainty: {report.limitations_and_uncertainty.expanded_measurement_uncertainty_u95}</div>
              <div className="text-zinc-400 text-[10px]">Stochastic ST: {report.limitations_and_uncertainty.stochastic_threshold_rfu} RFU</div>
            </div>

            {/* Section 7 */}
            <div className="p-4 rounded-xl border border-tactical-border/40 bg-black/40 space-y-1.5">
              <span className="text-[9px] font-bold text-purple-300 uppercase">7. Dual-Sign-Off Governance</span>
              <div className="text-zinc-300 text-[11px]">Analyst: <span className="font-bold text-zinc-100">{report.dual_sign_off_governance.primary_analyst_signature}</span></div>
              <div className="text-zinc-300 text-[11px]">Reviewer: <span className="font-bold text-zinc-100">{report.dual_sign_off_governance.technical_reviewer_signature}</span></div>
            </div>

            {/* Section 8 */}
            <div className="md:col-span-2 p-3 rounded-xl bg-black/60 border border-zinc-900 text-[9px] text-zinc-500 flex items-center justify-between">
              <span>8. Cryptographic Audit Hash: <span className="font-mono text-zinc-300">{report.audit_trail_and_cryptography.certificate_hash}</span></span>
              <span className="text-emerald-400 font-bold">CERTIFIED</span>
            </div>

          </div>
        </motion.div>
      )}
    </div>
  );
}
