"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Cpu, Upload, FileCode, CheckCircle2, AlertTriangle, RefreshCw, Layers } from "lucide-react";

interface ParsedPeak {
  sample_id: string;
  locus: string;
  alleles: string[];
  peak_heights_rfu: number[];
  mean_rfu: number;
}

interface IngestResult {
  status: string;
  instrument_type: string;
  parsed_data: {
    parsed_peaks?: ParsedPeak[];
    total_loci_parsed?: number;
    degradation_index_di?: number;
    degradation_assessment?: string;
    small_autosomal_conc_ng_ul?: number;
    large_autosomal_conc_ng_ul?: number;
    recommended_pcr_input_pg?: number;
  };
  ingestion_provenance: string;
}

export default function InstrumentIngestionPanel() {
  const [instType, setInstType] = useState<string>("CE");
  const [rawText, setRawText] = useState<string>(
    "Sample Name,Locus,Allele 1,Allele 2,Height 1,Height 2\nSAMPLE-01,D3S1358,15,16,1200,1150\nSAMPLE-01,vWA,16,17,950,980\nSAMPLE-01,FGA,21,24,1400,1380"
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IngestResult | null>({
    status: "SUCCESS",
    instrument_type: "CE",
    parsed_data: {
      total_loci_parsed: 3,
      parsed_peaks: [
        { sample_id: "SAMPLE-01", locus: "D3S1358", alleles: ["15", "16"], peak_heights_rfu: [1200, 1150], mean_rfu: 1175 },
        { sample_id: "SAMPLE-01", locus: "VWA", alleles: ["16", "17"], peak_heights_rfu: [950, 980], mean_rfu: 965 },
        { sample_id: "SAMPLE-01", locus: "FGA", alleles: ["21", "24"], peak_heights_rfu: [1400, 1380], mean_rfu: 1390 },
      ]
    },
    ingestion_provenance: "FORENZA Automated Analytical Instrument Gateway v1.0"
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const handleIngest = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/instruments/ingest-output`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          instrument_type: instType,
          raw_content: rawText,
          small_autosomal_conc_ng_ul: 0.85,
          large_autosomal_conc_ng_ul: 0.80,
          male_y_conc_ng_ul: 0.82
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (e) {
      console.error("Instrument output ingestion failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-indigo-500/30 bg-indigo-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-500/20 border border-indigo-500/40 text-indigo-300">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                Automated Analytical Instrument Gateway
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                RAW FILE INGESTION
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              Direct Parsers for CE GeneMapper, qPCR Quantifiler, NGS MiSeq VCF, LC-MS/MS & Microscopy
            </p>
          </div>
        </div>

        <button
          onClick={handleIngest}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-black font-bold text-xs uppercase tracking-wider transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Parse Instrument Output
        </button>
      </div>

      {/* ── Layout: Config & Input vs Output ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left: Input Selector & Textarea */}
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
          <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block border-b border-tactical-border/40 pb-3">
            Select Analytical Instrument Source
          </span>

          <div className="grid grid-cols-3 gap-2">
            {[
              { id: "CE", label: "CE GeneMapper" },
              { id: "QPCR", label: "qPCR Quantifiler" },
              { id: "NGS", label: "NGS MiSeq VCF" },
            ].map((t) => (
              <button
                key={t.id}
                onClick={() => setInstType(t.id)}
                className={`p-2.5 rounded-xl border text-center font-bold text-xs transition-all ${
                  instType === t.id
                    ? "border-indigo-400 bg-indigo-500/20 text-indigo-300"
                    : "border-tactical-border/40 bg-black/30 text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          <div className="space-y-1">
            <span className="text-[10px] text-zinc-400 uppercase font-bold">Raw Output File Content (CSV / VCF)</span>
            <textarea
              rows={8}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full p-3 rounded-xl border border-tactical-border/60 bg-black/60 font-mono text-xs text-zinc-200 focus:border-indigo-400 focus:outline-none"
            />
          </div>
        </div>

        {/* Right: Parsed Result Output */}
        <div className="space-y-4">
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4 rounded-2xl border border-indigo-500/40 bg-tactical-surface/50 p-5 shadow-xl"
            >
              <div className="flex items-center justify-between border-b border-indigo-500/20 pb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-tactical-text flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  Parsed Normalized Evidence Output ({result.instrument_type})
                </span>
                <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  INGESTED
                </span>
              </div>

              {result.parsed_data.parsed_peaks && (
                <div className="space-y-2">
                  <span className="text-[10px] text-zinc-400 uppercase font-bold">Extracted Allelic Peak Table</span>
                  <div className="divide-y divide-tactical-border/30 rounded-xl border border-tactical-border/40 bg-black/40 overflow-hidden">
                    {result.parsed_data.parsed_peaks.map((p, i) => (
                      <div key={i} className="p-3 flex items-center justify-between text-xs font-mono">
                        <div>
                          <span className="font-bold text-indigo-300">{p.locus}</span>
                          <span className="text-zinc-500 text-[10px] ml-2">Sample: {p.sample_id}</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-emerald-400 font-bold">Alleles: [{p.alleles.join(", ")}]</span>
                          <span className="text-cyan-400 text-[10px]">RFU: {p.mean_rfu}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>

      </div>
    </div>
  );
}
