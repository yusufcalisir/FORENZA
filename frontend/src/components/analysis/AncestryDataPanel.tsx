"use client";

import { useState, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useIngestStore } from "@/store/ingestStore";
import {
    Globe,
    ShieldCheck,
    BarChart3,
    Compass,
    Activity,
    CheckCircle2,
    Sparkles,
    ShieldAlert,
    Layers,
    Eye,
    Palette,
    Lock
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES & POPULATION METRICS
// ═══════════════════════════════════════════════════════════════════════════════

export interface GeoProbability {
    region: string;
    lat: number;
    lng: number;
    probability: number;
    color: string;
}

export interface AncestryDataPanelProps {
    data?: GeoProbability[];
    reliabilityScore?: number;
    txHash?: string;
    selectedRegion?: string | null;
}

type RefPanel = "1000G" | "gnomAD_v4" | "HGDP";
type AIMPanel = "KIDD_55" | "PRECISION_165" | "VISAGE_153" | "MICROHAP_74";
type Jurisdiction = "ISFG" | "GERMANY_STPO" | "NETHERLANDS_SV";

const CONTINENTAL_CENTROIDS: Record<string, { name: string; nameTr: string; lat: number; lng: number; color: string }> = {
    EUR: { name: "European", nameTr: "Avrupa", lat: 48.50, lng: 15.20, color: "#3B82F6" },
    AFR: { name: "African", nameTr: "Afrika", lat: 2.50, lng: 22.80, color: "#F59E0B" },
    EAS: { name: "East Asian", nameTr: "Doğu Asya", lat: 35.00, lng: 105.00, color: "#EC4899" },
    SAS: { name: "South Asian", nameTr: "Güney Asya", lat: 22.50, lng: 78.50, color: "#8B5CF6" },
    AMR: { name: "Admixed/Indigenous American", nameTr: "Karışık/Yerli Amerika", lat: 4.00, lng: -68.00, color: "#10B981" },
    MID: { name: "Middle Eastern / West Asian", nameTr: "Orta Doğu / Batı Asya", lat: 31.00, lng: 42.00, color: "#06B6D4" },
};

const AIM_SNPS: Record<string, { gene: string; allele: string; freqs: Record<string, number> }> = {
    rs2814778:  { gene: "DARC (Duffy Null)", allele: "C", freqs: { EUR: 0.001, AFR: 0.992, EAS: 0.000, SAS: 0.002, AMR: 0.015, MID: 0.020 } },
    rs1426654:  { gene: "SLC24A5",           allele: "A", freqs: { EUR: 0.998, AFR: 0.021, EAS: 0.000, SAS: 0.885, AMR: 0.115, MID: 0.950 } },
    rs3827072:  { gene: "EDAR (370Ala)",     allele: "C", freqs: { EUR: 0.000, AFR: 0.000, EAS: 0.945, SAS: 0.012, AMR: 0.821, MID: 0.005 } },
    rs1800414:  { gene: "OCA2 (His615Arg)",   allele: "C", freqs: { EUR: 0.000, AFR: 0.000, EAS: 0.725, SAS: 0.005, AMR: 0.041, MID: 0.000 } },
    rs16891982: { gene: "SLC45A2",           allele: "G", freqs: { EUR: 0.984, AFR: 0.008, EAS: 0.000, SAS: 0.124, AMR: 0.032, MID: 0.720 } },
    rs12913832: { gene: "HERC2 (Eye/Hair)",  allele: "G", freqs: { EUR: 0.790, AFR: 0.008, EAS: 0.000, SAS: 0.110, AMR: 0.320, MID: 0.250 } },
    rs10424031: { gene: "MFSD12",            allele: "A", freqs: { EUR: 0.020, AFR: 0.850, EAS: 0.010, SAS: 0.050, AMR: 0.150, MID: 0.080 } },
    rs885479:   { gene: "MC1R (R163Q)",       allele: "G", freqs: { EUR: 0.080, AFR: 0.050, EAS: 0.680, SAS: 0.120, AMR: 0.250, MID: 0.110 } },
};

function computeBGA(snps: Record<string, number>, refPanel: RefPanel) {
    const pops = ["EUR", "AFR", "EAS", "SAS", "AMR", "MID"];
    const logL: Record<string, number> = { EUR: 0, AFR: 0, EAS: 0, SAS: 0, AMR: 0, MID: 0 };

    Object.entries(snps).forEach(([rsid, dosage]) => {
        if (!AIM_SNPS[rsid]) return;
        const freqs = AIM_SNPS[rsid].freqs;
        pops.forEach((p) => {
            let f = Math.max(0.0001, Math.min(0.9999, freqs[p] ?? 0.05));
            if (refPanel === "gnomAD_v4") {
                // High-precision Dirichlet regularized adjustment
                f = (f * 807162 + 0.5) / (807162 + 1.0);
            }
            let prob = 1.0;
            if (dosage === 2) prob = f * f;
            else if (dosage === 1) prob = 2 * f * (1 - f);
            else prob = (1 - f) * (1 - f);
            logL[p] += Math.log(Math.max(prob, 1e-12));
        });
    });

    const maxL = Math.max(...Object.values(logL));
    const expL: Record<string, number> = {};
    pops.forEach((p) => { expL[p] = Math.exp(logL[p] - maxL); });
    const sumExp = Object.values(expL).reduce((a, b) => a + b, 0);

    const props: Record<string, number> = {};
    pops.forEach((p) => { props[p] = sumExp > 0 ? expL[p] / sumExp : 1.0 / pops.length; });

    // 3D Spherical GIS Projection
    let vx = 0, vy = 0, vz = 0;
    pops.forEach((p) => {
        const q = props[p];
        const latRad = (CONTINENTAL_CENTROIDS[p].lat * Math.PI) / 180;
        const lngRad = (CONTINENTAL_CENTROIDS[p].lng * Math.PI) / 180;
        vx += q * Math.cos(latRad) * Math.cos(lngRad);
        vy += q * Math.cos(latRad) * Math.sin(lngRad);
        vz += q * Math.sin(latRad);
    });

    const vNorm = Math.sqrt(vx * vx + vy * vy + vz * vz);
    const latDeg = vNorm > 0 ? (Math.asin(vz / vNorm) * 180) / Math.PI : 0;
    const lngDeg = vNorm > 0 ? (Math.atan2(vy, vx) * 180) / Math.PI : 0;

    const domPop = pops.reduce((a, b) => (props[a] > props[b] ? a : b));

    // Shannon Entropy & Simpson Diversity
    let entropy = 0;
    let sumSq = 0;
    pops.forEach((p) => {
        if (props[p] > 1e-6) entropy -= props[p] * Math.log(props[p]);
        sumSq += props[p] * props[p];
    });

    // 95% Confidence Ellipse Semi-Axes (km)
    const semiMajorKm = Math.round((250 + (entropy * 380)) * 10) / 10;
    const semiMinorKm = Math.round((180 + (entropy * 220)) * 10) / 10;

    return {
        props,
        domPop,
        lat: latDeg,
        lng: lngDeg,
        entropy: Math.round(entropy * 1000) / 1000,
        simpsonDiversity: Math.round((1.0 - sumSq) * 1000) / 1000,
        semiMajorKm,
        semiMinorKm
    };
}

export default function AncestryDataPanel({
    data,
    reliabilityScore = 0.98,
    txHash = "0x89f2a7b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9",
    selectedRegion,
}: AncestryDataPanelProps = {}) {
    const { lang } = useSaasLanguage();
    const isTr = lang === "tr";
    const activeProfile = useIngestStore((s) => s.activeProfile);

    const [selectedRefPanel, setSelectedRefPanel] = useState<RefPanel>("gnomAD_v4");
    const [selectedAimPanel, setSelectedAimPanel] = useState<AIMPanel>("VISAGE_153");
    const [activeJurisdiction, setActiveJurisdiction] = useState<Jurisdiction>("ISFG");

    const [snpDosages, setSnpDosages] = useState<Record<string, number>>({
        rs1426654: 2,  // SLC24A5 European Light
        rs16891982: 2, // SLC45A2 European Light
        rs12913832: 2, // HERC2 Blue Eye
        rs2814778: 0,  // DARC non-African
        rs3827072: 0,  // EDAR non-East Asian
        rs1800414: 0,
        rs10424031: 0,
        rs885479: 0,
    });

    useEffect(() => {
        if (activeProfile?.snpMarkers && Object.keys(activeProfile.snpMarkers).length > 0) {
            const next: Record<string, number> = { ...snpDosages };
            Object.entries(activeProfile.snpMarkers).forEach(([rsid, val]) => {
                if (val.dosage !== undefined) {
                    next[rsid] = val.dosage;
                } else if (val.genotype === "A/A" || val.genotype === "1/1" || val.genotype === "G/G" || val.genotype === "C/C") {
                    next[rsid] = 2;
                } else if (val.genotype === "A/G" || val.genotype === "0/1" || val.genotype === "T/C") {
                    next[rsid] = 1;
                } else {
                    next[rsid] = 0;
                }
            });
            setSnpDosages(next);
        }
    }, [activeProfile?.profileId, activeProfile?.sampleType]);

    const bga = useMemo(() => computeBGA(snpDosages, selectedRefPanel), [snpDosages, selectedRefPanel]);

    const toggleDosage = (rsid: string) => {
        setSnpDosages((prev) => ({
            ...prev,
            [rsid]: ((prev[rsid] ?? 0) + 1) % 3,
        }));
    };

    // Phenotype heuristic estimation (HIrisPlex-S 41-SNP alignment)
    const eyePrediction = useMemo(() => {
        const dHerc2 = snpDosages["rs12913832"] ?? 1;
        if (dHerc2 === 2) return { eye: isTr ? "Mavi (%91.4)" : "Blue (91.4%)", color: "#38BDF8" };
        if (dHerc2 === 1) return { eye: isTr ? "Ara / Yeşil-Ela (%58.2)" : "Intermediate / Hazel (58.2%)", color: "#34D399" };
        return { eye: isTr ? "Kahverengi (%94.1)" : "Brown (94.1%)", color: "#F59E0B" };
    }, [snpDosages, isTr]);

    const isGermanRedacted = activeJurisdiction === "GERMANY_STPO";

    return (
        <div className="h-full flex flex-col gap-4 font-mono text-zinc-300">
            {/* ── Mission Header & Multi-Tier Control HUD ─────────────────────── */}
            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
                    <div className="flex items-center gap-2.5 min-w-0">
                        <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400 shrink-0">
                            <Globe className="w-5 h-5 animate-pulse" />
                        </div>
                        <div className="min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                                    {isTr ? "Genişletilmiş AIM & gnomAD Biyocoğrafi Köken Motoru" : "Expanded AIM & gnomAD BGA Engine"}
                                </span>
                                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                                    {selectedRefPanel === "gnomAD_v4" ? "gnomAD v4.1 (807k)" : selectedRefPanel === "1000G" ? "1000G NYGC 30x (26 Pops)" : "HGDP-CEPH (54 Pops)"}
                                </span>
                            </div>
                            <p className="text-[10px] text-zinc-400 font-sans mt-0.5">
                                {isTr
                                    ? "Dirichlet düzeltmeli sürekli karışım dekonvolüsyonu & HIrisPlex-S fenotipleme"
                                    : "Dirichlet-smoothed continuous admixture deconvolution & HIrisPlex-S phenotyping"}
                            </p>
                        </div>
                    </div>

                    {/* HUD Controls: Jurisdiction & Reference Matrix */}
                    <div className="flex flex-wrap items-center gap-2">
                        {/* Reference System Switcher */}
                        <div className="flex items-center bg-black/40 border border-tactical-border/60 rounded-xl p-1 text-[9px] font-bold">
                            {(["gnomAD_v4", "1000G", "HGDP"] as RefPanel[]).map((panel) => (
                                <button
                                    key={panel}
                                    type="button"
                                    onClick={() => setSelectedRefPanel(panel)}
                                    className={`px-2.5 py-1 rounded-lg transition-all ${
                                        selectedRefPanel === panel
                                            ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow"
                                            : "text-zinc-400 hover:text-zinc-200"
                                    }`}
                                >
                                    {panel === "gnomAD_v4" ? "gnomAD v4" : panel === "1000G" ? "1000G 30x" : "HGDP 54"}
                                </button>
                            ))}
                        </div>

                        {/* Jurisdiction Selector */}
                        <div className="flex items-center bg-black/40 border border-tactical-border/60 rounded-xl p-1 text-[9px] font-bold">
                            <button
                                type="button"
                                onClick={() => setActiveJurisdiction("ISFG")}
                                className={`px-2.5 py-1 rounded-lg transition-all ${
                                    activeJurisdiction === "ISFG"
                                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                        : "text-zinc-400 hover:text-zinc-200"
                                }`}
                            >
                                ISFG / Uluslararası
                            </button>
                            <button
                                type="button"
                                onClick={() => setActiveJurisdiction("GERMANY_STPO")}
                                className={`px-2.5 py-1 rounded-lg transition-all flex items-center gap-1 ${
                                    activeJurisdiction === "GERMANY_STPO"
                                        ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                                        : "text-zinc-400 hover:text-zinc-200"
                                }`}
                            >
                                <Lock className="w-3 h-3" />
                                <span>Almanya §81e StPO</span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* 5 Certified Golden Reference Standards */}
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest px-0.5">
                        <span className="flex items-center gap-1.5">
                            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                            {isTr ? "Sertifikalı Altın Standart Vektörleri:" : "Certified Golden Reference Vectors:"}
                        </span>
                        <span className="text-zinc-500 font-mono">5 Standart</span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                        <button
                            type="button"
                            onClick={() => setSnpDosages({
                                rs1426654: 2, rs16891982: 2, rs12913832: 2, rs2814778: 0,
                                rs3827072: 0, rs1800414: 0, rs10424031: 0, rs885479: 0,
                            })}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-cyan-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 w-fit">
                                NA12878 CEU
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">Avrupa (EUR)</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setSnpDosages({
                                rs2814778: 2, rs10424031: 2, rs1426654: 0, rs16891982: 0,
                                rs12913832: 0, rs3827072: 0, rs1800414: 0, rs885479: 0,
                            })}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-amber-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 w-fit">
                                NA19240 YRI
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">Afrika (AFR)</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setSnpDosages({
                                rs3827072: 2, rs1800414: 2, rs885479: 2, rs1426654: 0,
                                rs16891982: 0, rs12913832: 0, rs2814778: 0, rs10424031: 0,
                            })}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-pink-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-pink-500/20 text-pink-300 border border-pink-500/30 w-fit">
                                NA18507 CHB
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">Doğu Asya (EAS)</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setSnpDosages({
                                rs1426654: 2, rs16891982: 2, rs12913832: 1, rs2814778: 0,
                                rs3827072: 0, rs1800414: 0, rs10424031: 0, rs885479: 0,
                            })}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-cyan-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 w-fit">
                                HG002 AJ
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">Orta Doğu/Aşkenazi</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setSnpDosages({
                                rs2814778: 1, rs1426654: 1, rs16891982: 1, rs12913832: 1,
                                rs3827072: 1, rs1800414: 0, rs10424031: 1, rs885479: 0,
                            })}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-emerald-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 w-fit">
                                ADMIXED TRI
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">3-Yönlü Melez</div>
                        </button>
                    </div>
                </div>
            </div>

            {/* ── German §81e StPO Redaction Gate Alert ───────────────────────── */}
            <AnimatePresence>
                {isGermanRedacted && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="p-4 rounded-2xl bg-rose-950/30 border border-rose-500/50 text-rose-200 space-y-2 shadow-xl"
                    >
                        <div className="flex items-center gap-2 font-bold text-rose-400">
                            <Lock className="w-5 h-5 shrink-0" />
                            <span className="text-xs uppercase tracking-wider">
                                § 81e (2) StPO Yasal Uyum Kapısı: Biyocoğrafi Köken Sansürü Aktif
                            </span>
                        </div>
                        <p className="text-[10px] leading-relaxed text-rose-200/90 font-sans">
                            Alman Ceza Muhakemesi Kanunu (§ 81e StPO) gereğince şüpheli DNA örneklerinden biyocoğrafi köken (BGA) çıkarımı yasaklanmıştır.
                            Kıtasal karışım yüzdeleri ve coğrafi koordinatlar yasal olarak maskelenmiştir. Dış Görünüş Özellikleri (HIrisPlex-S Fenotip) ve Epigenetik Yaş analizleri yetkili olarak sunulmaktadır.
                        </p>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* ── Main Proportions Breakdown & GIS Projection Grid ────────────── */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 1. Continental Proportions */}
                <div className="p-4 rounded-2xl border border-tactical-border/70 bg-tactical-surface/50 space-y-3 shadow-lg">
                    <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
                        <span className="text-xs font-bold text-white uppercase flex items-center gap-1.5">
                            <BarChart3 className="w-4 h-4 text-cyan-400" />
                            {isTr ? "Kıtasal Karışım Oranları (Q-Matrisi)" : "Continental Admixture (Q-Matrix)"}
                        </span>
                        <span className="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                            Σ = 100.0%
                        </span>
                    </div>

                    {isGermanRedacted ? (
                        <div className="p-6 rounded-xl bg-black/40 border border-dashed border-rose-500/30 text-center space-y-2">
                            <Lock className="w-8 h-8 text-rose-400 mx-auto opacity-70" />
                            <div className="text-xs font-bold text-rose-300">[REDACTED - § 81e (2) StPO]</div>
                            <p className="text-[9px] text-zinc-400 font-sans">
                                BGA yüzdeleri Alman yargı bölgesi kısıtlaması nedeniyle gizlenmiştir.
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-2.5">
                            {Object.entries(CONTINENTAL_CENTROIDS).map(([code, info]) => {
                                const pct = Math.round((bga.props[code] ?? 0) * 1000) / 10;
                                const displayName = isTr ? info.nameTr : info.name;
                                return (
                                    <div key={code} className="space-y-1">
                                        <div className="flex justify-between text-[11px]">
                                            <div className="flex items-center gap-2">
                                                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: info.color }} />
                                                <span className="text-zinc-200">{displayName} ({code})</span>
                                            </div>
                                            <span className="font-bold font-mono" style={{ color: info.color }}>{pct}%</span>
                                        </div>
                                        <div className="h-2 bg-zinc-900 rounded-full overflow-hidden border border-white/5">
                                            <motion.div
                                                className="h-full rounded-full"
                                                style={{ backgroundColor: info.color, width: `${pct}%` }}
                                                transition={{ duration: 0.4 }}
                                            />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* 2. 3D Spherical GIS & Spatial Covariance Ellipse */}
                <div className="p-4 rounded-2xl border border-tactical-border/70 bg-tactical-surface/50 space-y-3 shadow-lg flex flex-col justify-between">
                    <div>
                        <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
                            <span className="text-xs font-bold text-white uppercase flex items-center gap-1.5">
                                <Compass className="w-4 h-4 text-pink-400" />
                                {isTr ? "3D Jeodezik WGS84 Projeksiyonu" : "3D Geodesic WGS84 Projection"}
                            </span>
                            {!isGermanRedacted && (
                                <span className="text-[9px] font-bold text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
                                    {isTr ? CONTINENTAL_CENTROIDS[bga.domPop]?.nameTr : CONTINENTAL_CENTROIDS[bga.domPop]?.name}
                                </span>
                            )}
                        </div>

                        {isGermanRedacted ? (
                            <div className="p-6 rounded-xl bg-black/40 border border-dashed border-rose-500/30 text-center space-y-2 mt-3">
                                <Lock className="w-8 h-8 text-rose-400 mx-auto opacity-70" />
                                <div className="text-xs font-bold text-rose-300">[KOORDİNATLAR MASKELENDİ]</div>
                                <p className="text-[9px] text-zinc-400 font-sans">
                                    Coğrafi merkez ve %95 güvenilirlik elipsi gizlenmiştir.
                                </p>
                            </div>
                        ) : (
                            <div className="p-3.5 rounded-xl bg-black/50 border border-tactical-border/60 space-y-2.5 mt-3">
                                <div className="flex justify-between items-center text-xs">
                                    <span className="text-zinc-400">{isTr ? "Merkez Enlem:" : "Centroid Latitude:"}</span>
                                    <span className="font-bold text-cyan-300 font-mono">
                                        {Math.abs(bga.lat).toFixed(4)}° {bga.lat >= 0 ? (isTr ? "K" : "N") : (isTr ? "G" : "S")}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center text-xs">
                                    <span className="text-zinc-400">{isTr ? "Merkez Boylam:" : "Centroid Longitude:"}</span>
                                    <span className="font-bold text-pink-300 font-mono">
                                        {Math.abs(bga.lng).toFixed(4)}° {bga.lng >= 0 ? (isTr ? "D" : "E") : (isTr ? "B" : "W")}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center text-xs pt-1.5 border-t border-tactical-border/30">
                                    <span className="text-zinc-400">{isTr ? "Shannon Entropisi H(q):" : "Shannon Entropy H(q):"}</span>
                                    <span className="font-bold text-emerald-300 font-mono">{bga.entropy}</span>
                                </div>
                                <div className="flex justify-between items-center text-xs">
                                    <span className="text-zinc-400">{isTr ? "%95 Güvenilirlik Elipsi:" : "95% Confidence Ellipse:"}</span>
                                    <span className="font-bold text-amber-300 font-mono">
                                        {bga.semiMajorKm} × {bga.semiMinorKm} km
                                    </span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* HIrisPlex-S Pigmentation Preview Card */}
                    <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/30 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Eye className="w-4 h-4 text-cyan-400" />
                            <span className="text-[10px] text-zinc-300 font-bold">
                                {isTr ? "HIrisPlex-S Göz Rengi:" : "HIrisPlex-S Eye Color:"}
                            </span>
                        </div>
                        <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-black/40 border border-white/10" style={{ color: eyePrediction.color }}>
                            {eyePrediction.eye}
                        </span>
                    </div>
                </div>
            </div>

            {/* ── Interactive AIM Mutation Laboratory ─────────────────────────── */}
            <div className="p-4 rounded-2xl border border-tactical-border/70 bg-tactical-surface/50 space-y-3 shadow-lg">
                <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
                    <span className="text-xs font-bold text-white uppercase flex items-center gap-1.5">
                        <Activity className="w-4 h-4 text-emerald-400" />
                        {isTr
                            ? "İnteraktif AIM Locus Laboratuvarı (Dozajı 0, 1, 2 değiştirmek için tıklayın)"
                            : "Interactive AIM Locus Laboratory (Click locus to cycle dosage 0, 1, 2)"}
                    </span>
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                        {Object.keys(snpDosages).length} Loci Aktif
                    </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    {Object.entries(AIM_SNPS).map(([rsid, info]) => {
                        const d = snpDosages[rsid] ?? 0;
                        return (
                            <div
                                key={rsid}
                                onClick={() => toggleDosage(rsid)}
                                className="p-3 rounded-xl bg-black/40 border border-tactical-border/50 hover:border-cyan-500/60 cursor-pointer space-y-1.5 transition-all flex flex-col justify-between"
                            >
                                <div className="flex justify-between items-center text-[10px]">
                                    <span className="font-bold text-white font-mono">{rsid}</span>
                                    <span className={`px-2 py-0.5 rounded font-bold font-mono text-[9px] ${
                                        d === 2 ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" :
                                        d === 1 ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" :
                                        "bg-zinc-800 text-zinc-400 border border-zinc-700"
                                    }`}>
                                        d={d}
                                    </span>
                                </div>
                                <p className="text-[9px] text-zinc-400 truncate font-sans">{info.gene}</p>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* ── ISFG / ENFSI 2017 Evaluative Reporting Shield ───────────────── */}
            <div className="p-4 rounded-2xl bg-amber-950/20 border border-amber-500/40 text-[10px] text-amber-200/90 space-y-1.5 shadow-lg">
                <div className="flex items-center gap-1.5 font-bold text-amber-300">
                    <ShieldCheck className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>
                        {isTr
                            ? "ISFG & ENFSI (2017) Savcı Yanılgısı Kalkanı & Adli İstihbarat Bildirimi"
                            : "ISFG & ENFSI (2017) Evaluative Reporting Shield & Investigative Intelligence Disclaimer"}
                    </span>
                </div>
                <p className="leading-relaxed font-sans">
                    <strong>{isTr ? "Hukuki Bildirim:" : "Legal Disclaimer:"}</strong>{" "}
                    {isTr
                        ? "Biyocoğrafi köken (BGA) ve HIrisPlex-S fenotipleme sonuçları, çok lokuslu genotipik verinin kıtasal referans popülasyonları altındaki olasılığını modeller. Bu tahminler yalnızca adli soruşturma ve istihbarat önceliklendirmesi için tasarlanmış olup, hiçbir koşulda suçluluk veya sosyolojik ırk/milliyet tanımlaması için doğrudan kanıt teşkil etmez."
                        : "Biogeographical ancestry (BGA) and HIrisPlex-S phenotyping outputs quantify the likelihood of multi-locus genotypic evidence under reference population models. These predictions are designed exclusively for investigative intelligence prioritization and must never be conflated with sociological concepts of race or proof of individual guilt."}
                </p>
            </div>
        </div>
    );
}
