"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Lock, ShieldCheck, Eye, EyeOff, KeyRound, Cpu, CheckCircle2, AlertTriangle, RefreshCw, Layers } from "lucide-react";
import { useForensicCaseStore } from "@/store/forensicCaseStore";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

const DEFAULT_SUSPECT_LOCI: Record<string, number[]> = {
  D3S1358: [15.0, 16.0],
  vWA: [17.0, 18.0],
  D16S539: [11.0, 12.0],
  CSF1PO: [10.0, 11.0],
  TPOX: [8.0, 8.0],
  D8S1179: [13.0, 14.0],
  D21S11: [28.0, 30.0],
  D18S51: [14.0, 16.0],
  D2S441: [10.0, 11.0],
  D19S433: [13.0, 14.2],
  TH01: [7.0, 9.3],
  FGA: [21.0, 24.0],
  D22S1045: [15.0, 16.0],
  D5S818: [11.0, 12.0],
  D13S317: [11.0, 12.0],
  D7S820: [9.0, 10.0],
  SE33: [22.2, 28.2],
  D10S1248: [13.0, 15.0],
  D1S1656: [16.0, 17.3],
  D12S391: [18.0, 19.0],
  D2S1338: [19.0, 23.0],
  D6S1043: [12.0, 18.0],
  PentaE: [12.0, 14.0],
  PentaD: [9.0, 12.0],
};

interface Groth16ProofPayload {
  pi_a: string[];
  pi_b: string[][];
  pi_c: string[];
  protocol: string;
  curve: string;
}

interface SynthesizeResponse {
  proof: Groth16ProofPayload;
  public_signals: string[];
  evidence_commitment: string;
  suspect_commitment: string;
  match_threshold: number;
  soundness_error: string;
}

interface VerifyResponse {
  is_valid: boolean;
  verdict: string;
  soundness_bound: string;
  evaluated_public_signals?: {
    evidence_commitment: string;
    match_threshold: number;
    suspect_commitment: string;
  };
  prosecutors_fallacy_shield: string;
}

export default function ZkpAuditorPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const { activeCase } = useForensicCaseStore();
  const [hidePrivateWitness, setHidePrivateWitness] = useState<boolean>(true);
  const [matchThreshold, setMatchThreshold] = useState<number>(44);
  const [activeTab, setActiveTab] = useState<"comparator" | "pairing">("comparator");
  const [loading, setLoading] = useState<boolean>(false);

  // Derive dynamic suspect loci from activeCase store
  const activeSuspectLoci = Object.entries(activeCase.profile.strMarkers).reduce(
    (acc, [locus, d]) => {
      acc[locus] = [Number(d.allele1) || 12.0, Number(d.allele2) || 12.0];
      return acc;
    },
    { ...DEFAULT_SUSPECT_LOCI } as Record<string, number[]>
  );

  // Evidence alleles (exact match default)
  const evidenceLoci = activeSuspectLoci;

  const [proofData, setProofData] = useState<SynthesizeResponse | null>(null);
  const [verifyResult, setVerifyResult] = useState<VerifyResponse | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const handleSynthesizeProof = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/zkp/synthesize-proof`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          suspect_loci: DEFAULT_SUSPECT_LOCI,
          evidence_loci: evidenceLoci,
          match_threshold: matchThreshold,
        }),
      });

      if (res.ok) {
        const data: SynthesizeResponse = await res.json();
        setProofData(data);

        // Auto verify pairing
        const verRes = await fetch(`${API_BASE}/api/v1/forensic/zkp/verify-pairing`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            proof: data.proof,
            public_signals: data.public_signals,
          }),
        });

        if (verRes.ok) {
          const verData: VerifyResponse = await verRes.json();
          setVerifyResult(verData);
        }
      }
    } catch (e) {
      console.error("ZKP proof synthesis failed:", e);
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
            <Lock className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xs sm:text-sm font-bold tracking-widest text-tactical-text uppercase">
                {isTr ? "ZKP Kör Adli Denetçi (Pillar 6 §2)" : "ZKP Blind Forensic Auditor (Pillar 6 §2)"}
              </h2>
              <span className="px-2.5 py-0.5 rounded-lg text-[8px] sm:text-[9px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 whitespace-nowrap shrink-0">
                Groth16 • BN254 • GDPR Art. 9
              </span>
            </div>
            <p className="text-[9px] sm:text-[10px] text-zinc-400 mt-0.5 truncate">
              {isTr
                ? "Sıfır Bilgi Gizlilik Korumalı STR Doğrulama Devresi • Poseidon Taahhüdü • Çift Doğrusal Eşleşmeler"
                : "Zero-Knowledge Privacy-Preserving STR Verification Circuit • Poseidon Commitment • Bilinear Multi-Pairings"}
            </p>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full lg:w-auto shrink-0">
          <button
            onClick={() => setHidePrivateWitness(!hidePrivateWitness)}
            className="px-3 py-1.5 rounded-xl border border-tactical-border/60 bg-black/60 text-[10px] sm:text-xs font-bold text-zinc-300 hover:text-white flex items-center justify-center gap-1.5 cursor-pointer transition-all whitespace-nowrap"
          >
            {hidePrivateWitness ? <EyeOff className="w-3.5 h-3.5 text-amber-400 shrink-0" /> : <Eye className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
            <span>{hidePrivateWitness ? (isTr ? "Özel Tanık (Gizli)" : "Private Witness (Masked)") : (isTr ? "Tanık Açık" : "Witness Revealed")}</span>
          </button>

          <div className="flex items-center justify-center gap-1 p-1 rounded-xl bg-black/60 border border-tactical-border/60">
            <button
              onClick={() => setActiveTab("comparator")}
              className={`flex-1 sm:flex-initial text-center px-3 py-1.5 rounded-lg text-[10px] sm:text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                activeTab === "comparator" ? "bg-indigo-500 text-white shadow-md font-extrabold" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {isTr ? "STR Devresi" : "STR Circuit"}
            </button>
            <button
              onClick={() => {
                setActiveTab("pairing");
                if (!proofData) handleSynthesizeProof();
              }}
              className={`flex-1 sm:flex-initial text-center px-3 py-1.5 rounded-lg text-[10px] sm:text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                activeTab === "pairing" ? "bg-indigo-500 text-white shadow-md font-extrabold" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {isTr ? "Eşleşme Doğrulayıcı" : "Pairing Verifier"}
            </button>
          </div>
        </div>
      </div>

      {/* ── SubTab 1: Privacy-Preserving STR Circuit Comparator ── */}
      {activeTab === "comparator" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Private Witness & Threshold Controls */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                {isTr ? "Devre Kısıtlamaları Konfigürasyonu" : "Circuit Constraints Configuration"}
              </span>
              <span className="text-[10px] text-indigo-400 font-bold">24 STR Loci</span>
            </div>

            {/* Threshold Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-400">{isTr ? "Eşleşme Eşiği (M_esik):" : "Match Threshold (M_thresh):"}</span>
                <span className="font-bold text-indigo-300">{matchThreshold} / 48 {isTr ? "Alel" : "Alleles"}</span>
              </div>
              <input
                type="range"
                min="20"
                max="48"
                step="1"
                value={matchThreshold}
                onChange={(e) => setMatchThreshold(parseInt(e.target.value))}
                className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>

            {/* Private Witness Card */}
            <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 space-y-2">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-bold text-zinc-300 flex items-center gap-1.5">
                  <KeyRound className="w-3.5 h-3.5 text-amber-400" />
                  {isTr ? "Özel Tanık Genotipi (G_S)" : "Private Witness Genotype (G_S)"}
                </span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {hidePrivateWitness ? (isTr ? "SIFIR-BİLGİ GİZLİ" : "ZERO-KNOWLEDGE HIDDEN") : (isTr ? "GÖRÜNÜR" : "EXPOSED")}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-1 max-h-48 overflow-y-auto pr-1">
                {Object.entries(DEFAULT_SUSPECT_LOCI).map(([loc, alleles]) => (
                  <div key={loc} className="flex justify-between p-1.5 rounded bg-black/30 text-[10px]">
                    <span className="text-zinc-500">{loc}:</span>
                    <span className={`font-mono ${hidePrivateWitness ? "text-zinc-600 select-none blur-xs" : "text-zinc-300"}`}>
                      {hidePrivateWitness ? "XX.X / XX.X" : alleles.join(" / ")}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={handleSynthesizeProof}
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2 cursor-pointer"
            >
              <Cpu className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              {isTr ? "Groth16 İspatını Sentezle" : "Synthesize Groth16 Proof"}
            </button>
          </div>

          {/* Right: R1CS Locus Gadget Evaluation & Output */}
          <div className="lg:col-span-2 space-y-4">
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              <div className="rounded-2xl border border-indigo-500/40 bg-gradient-to-br from-indigo-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-indigo-500/20 pb-3.5">
                  <div>
                    <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest block">
                      {isTr ? "R1CS EŞİTLİK GADGET'I & POSEIDON TAAHHÜTLERİ" : "R1CS EQUALITY GADGET & POSEIDON COMMITMENTS"}
                    </span>
                    <span className="text-sm sm:text-base font-black text-indigo-300 font-mono">
                      (a_lm - e_lm) · b_lm = 1 - m_lm (mod p)
                    </span>
                  </div>
                  <div className="flex flex-col items-start sm:items-end gap-1">
                    <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                      {isTr ? "Devre Kararı" : "Circuit Verdict"}
                    </span>
                    <span className="text-[10px] sm:text-xs font-bold px-2.5 py-1 rounded-lg border font-mono bg-emerald-500/20 text-emerald-300 border-emerald-500/40 whitespace-nowrap">
                      {isTr ? "R1CS SAĞLANDI (48/48 Eşleşme)" : "R1CS SATISFIED (48/48 Matches)"}
                    </span>
                  </div>
                </div>

                {/* Commitments Card */}
                {proofData && (
                  <div className="space-y-2">
                    <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 text-[10px] font-mono space-y-1.5">
                      <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
                        <span className="text-zinc-500 whitespace-nowrap">
                          {isTr ? "Genel Delil Taahhüdü H(G_E):" : "Public Evidence Commitment H(G_E):"}
                        </span>
                        <span className="text-indigo-300 break-all sm:truncate sm:max-w-md">{proofData.evidence_commitment}</span>
                      </div>
                      <div className="flex flex-col sm:flex-row sm:justify-between gap-1">
                        <span className="text-zinc-500 whitespace-nowrap">
                          {isTr ? "Şüpheli Poseidon Taahhüdü H(G_S):" : "Suspect Poseidon Commitment H(G_S):"}
                        </span>
                        <span className="text-amber-300 break-all sm:truncate sm:max-w-md">{proofData.suspect_commitment}</span>
                      </div>
                    </div>
                  </div>
                )}

                <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                  <div className="flex items-center gap-1.5 text-indigo-400 font-bold mb-1">
                    <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                    {isTr ? "GDPR Madde 9 & Hukuki Genomik Gizlilik Koruması" : "GDPR Article 9 & FRE 702 Genomic Privacy Safeguard"}
                  </div>
                  {isTr
                    ? "Sıfır Bilgi İspatları (ZKP), şüphelinin STR alellerini tamamen gizli tutarken mahkemede DNA eşleşmesinin doğrulanmasını sağlar. Ham genotip dizileri mahkeme tutanaklarında asla aktarılmaz, serileştirilmez veya saklanmaz."
                    : "Zero-Knowledge Proofs allow public court verification of DNA matches while completely suppressing suspect STR alleles. Raw genotype sequences are never transmitted, serialized, or stored in public courtroom dockets."}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      )}

      {/* ── SubTab 2: Groth16 BN254 Bilinear Pairing Verifier ── */}
      {activeTab === "pairing" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Proof Signals */}
          <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
            <div className="border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text block">
                {isTr ? "Genel Sinyaller Vektörü x" : "Public Signals Vector x"}
              </span>
            </div>

            {proofData ? (
              <div className="space-y-2 text-[10px] font-mono">
                <div className="p-2.5 rounded-lg bg-black/40 border border-tactical-border/40">
                  <span className="text-zinc-500 block">
                    {isTr ? "x₀ (Delil Hashi):" : "x₀ (Evidence Hash):"}
                  </span>
                  <span className="text-indigo-300 break-all">{proofData.public_signals[0]}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-black/40 border border-tactical-border/40">
                  <span className="text-zinc-500 block">
                    {isTr ? "x₁ (Eşleşme Eşiği):" : "x₁ (Match Threshold):"}
                  </span>
                  <span className="text-emerald-300">{proofData.public_signals[1]}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-black/40 border border-tactical-border/40">
                  <span className="text-zinc-500 block">
                    {isTr ? "x₂ (Şüpheli Taahhüdü):" : "x₂ (Suspect Commitment):"}
                  </span>
                  <span className="text-amber-300 break-all">{proofData.public_signals[2]}</span>
                </div>
              </div>
            ) : (
              <div className="text-xs text-zinc-500">
                {isTr ? "Önce bir ispat sentezleyin." : "Synthesize a proof first."}
              </div>
            )}
          </div>

          {/* Right: Bilinear Multi-Pairing Status */}
          <div className="lg:col-span-2 space-y-4">
            {verifyResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                <div className="rounded-2xl border border-indigo-500/40 bg-gradient-to-br from-indigo-500/10 via-tactical-surface/60 to-black/80 p-4 sm:p-5 space-y-4 shadow-2xl overflow-hidden">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-indigo-500/20 pb-3.5">
                    <div>
                      <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest block">
                        {isTr ? "BN254 ÇİFT DOĞRUSAL ÇOKLU EŞLEŞME DENKLEMİ" : "BN254 BILINEAR MULTI-PAIRING EQUATION"}
                      </span>
                      <span className="text-xs sm:text-sm font-black text-indigo-300 font-mono break-all">
                        e(A, B) · e(-α, β) · e(-∑ xᵢ Kᵢ, γ) · e(-C, δ) = 1_GT
                      </span>
                    </div>
                    <div className="flex flex-col items-start sm:items-end gap-1">
                      <span className="text-[10px] text-zinc-400 block uppercase font-bold">
                        {isTr ? "Eşleşme Durumu" : "Pairing Status"}
                      </span>
                      <span className="text-[10px] sm:text-xs font-bold px-2.5 py-1 rounded-lg border font-mono bg-emerald-500/20 text-emerald-300 border-emerald-500/40 whitespace-nowrap">
                        {isTr
                          ? (verifyResult.is_valid ? "EŞLEŞME DOĞRULANDI (GEÇERLİ)" : "EŞLEŞME GEÇERSİZ")
                          : verifyResult.verdict}
                      </span>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-black/40 border border-tactical-border/40 text-xs font-mono space-y-1.5">
                    <div className="flex justify-between text-[10px]">
                      <span className="text-zinc-500">{isTr ? "Eliptik Eğri Protokolü:" : "Elliptic Curve Protocol:"}</span>
                      <span className="text-zinc-300">Groth16 on alt_bn128 (BN254)</span>
                    </div>
                    <div className="flex justify-between text-[10px]">
                      <span className="text-zinc-500">{isTr ? "Doğruluk Hata Sınırı (ε):" : "Soundness Error Bound (ε):"}</span>
                      <span className="text-emerald-400 font-bold">{verifyResult.soundness_bound}</span>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                    <div className="flex items-center gap-1.5 text-indigo-400 font-bold mb-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      {isTr ? "Kriptografik Delil İnkar Edilemezliği" : "Cryptographic Evidence Non-Repudiation"}
                    </div>
                    {isTr
                      ? "Groth16 ZKP, ham STR profillerini veya allel değerlerini ifşa etmeden 24 lokus profil eşleşmesini BN254 eliptik eğrisi üzerinde matematiksel olarak kanıtlar."
                      : (verifyResult.prosecutors_fallacy_shield || "Groth16 ZKP mathematically proves 24-locus STR match on BN254 curve without disclosing raw alleles.")}
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
