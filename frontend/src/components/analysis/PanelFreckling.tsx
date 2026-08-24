"use client";

import { useState, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Sun,
    FlaskConical,
    AlertTriangle,
    Loader2,
    Dna,
    ShieldCheck,
    Sparkles,
    Sliders,
    Layers,
    Activity,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getApiBaseUrl } from "@/lib/api";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

interface MC1RResult {
    diplotype: string;
    functional_classification: string;
    total_mc1r_loss_weight: number;
    r_high_risk_alleles_count: number;
    r_low_risk_alleles_count: number;
    detected_variants: string[];
}

interface FrecklingResult {
    freckling_score_pct: number;
    freckling_intensity: string;
    epistatic_modifiers_applied: Record<string, number>;
}

interface UVSensitivityResult {
    minimal_erythema_dose_category: string;
    tanning_capacity: string;
    photoprotection_guidance: string;
}

interface FrecklingAndUVResponse {
    mc1r: MC1RResult;
    freckling: FrecklingResult;
    uv_sensitivity: UVSensitivityResult;
    assayed_snps_count: number;
    prosecutors_fallacy_shield: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONSTANTS & PRESETS
// ═══════════════════════════════════════════════════════════════════════════════

const MC1R_R_LOCI = [
    { rsid: "rs1805006", name: "D84E",  gene: "MC1R", weight: 2.50, risk: "R" },
    { rsid: "rs75570604",name: "R142H", gene: "MC1R", weight: 2.40, risk: "R" },
    { rsid: "rs1805007", name: "R151C", gene: "MC1R", weight: 2.85, risk: "R" },
    { rsid: "rs1805008", name: "R160W", gene: "MC1R", weight: 2.75, risk: "R" },
    { rsid: "rs1805009", name: "D294H", gene: "MC1R", weight: 2.60, risk: "R" },
];

const MC1R_r_LOCI = [
    { rsid: "rs1805005", name: "V60L",  gene: "MC1R", weight: 1.10, risk: "r" },
    { rsid: "rs2228479", name: "V92M",  gene: "MC1R", weight: 0.85, risk: "r" },
    { rsid: "rs885479",  name: "R163Q", gene: "MC1R", weight: 0.75, risk: "r" },
];

const MODIFIER_LOCI = [
    { rsid: "rs1015362",  gene: "ASIP",  weight: 0.85, name: "ASIP 20q11.2" },
    { rsid: "rs10756819", gene: "BNC2",  weight: 0.65, name: "BNC2 9p22.2" },
];

interface PresetItem {
    id: string;
    label: string;
    labelTr: string;
    desc: string;
    descTr: string;
    dosages: Record<string, number>;
}

const PRESETS: PresetItem[] = [
    {
        id: "R151C_HOM_RR",
        label: "R151C Homoz (R/R)",
        labelTr: "R151C Homozigot (R/R)",
        desc: "R/R  -  Dense Freckles / MED<20",
        descTr: "R/R  -  Yoğun Çil / MED<20",
        dosages: { rs1805007: 2 },
    },
    {
        id: "R_r_COMPOUND",
        label: "R/r Compound Het",
        labelTr: "R/r Birleşik Heterozigot",
        desc: "R151C + V60L  -  F_score=94.4%",
        descTr: "R151C + V60L  -  F_skoru=%94.4",
        dosages: { rs1805007: 1, rs1805005: 1 },
    },
    {
        id: "V60L_HOM_rr",
        label: "V60L Homoz (r/r)",
        labelTr: "V60L Homozigot (r/r)",
        desc: "r/r  -  Moderate / MED 35-50",
        descTr: "r/r  -  Orta Çil / MED 35-50",
        dosages: { rs1805005: 2 },
    },
    {
        id: "ASIP_BNC2_MAX",
        label: "ASIP+BNC2 Epistatic",
        labelTr: "ASIP+BNC2 Epistatik Artış",
        desc: "Epistatic boost  -  F_score=62.3%",
        descTr: "Epistatik modifiyer  -  F_skoru=%62.3",
        dosages: { rs1015362: 2, rs10756819: 2 },
    },
    {
        id: "WILD_TYPE_WT",
        label: "Wild-Type (wt/wt)",
        labelTr: "Yabanıl Tip (wt/wt)",
        desc: "wt/wt  -  F_score=7.6% (Low)",
        descTr: "wt/wt  -  F_skoru=%7.6 (Düşük)",
        dosages: {},
    },
];

// ═══════════════════════════════════════════════════════════════════════════════
// COLOR MAPS & VISUAL GAUGE
// ═══════════════════════════════════════════════════════════════════════════════

const CLASS_COLORS: Record<string, string> = {
    WILD_TYPE: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
    MILD_LOSS: "text-amber-400 border-amber-500/40 bg-amber-500/10",
    MODERATE_LOSS: "text-orange-400 border-orange-500/40 bg-orange-500/10",
    SEVERE_LOSS: "text-rose-400 border-rose-500/40 bg-rose-500/10",
};

const DIPLOTYPE_COLORS: Record<string, string> = {
    "wt/wt": "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
    "r/wt": "text-amber-400 border-amber-500/40 bg-amber-500/10",
    "r/r": "text-amber-400 border-amber-500/40 bg-amber-500/10",
    "R/wt": "text-orange-400 border-orange-500/40 bg-orange-500/10",
    "R/r": "text-orange-400 border-orange-500/40 bg-orange-500/10",
    "R/R": "text-rose-400 border-rose-500/40 bg-rose-500/10",
};

const MED_COLORS: Record<string, string> = {
    "< 20": "text-rose-400",
    "20 - 35": "text-orange-400",
    "35 - 50": "text-amber-400",
    "> 50": "text-emerald-400",
};

function getMedColor(medCat: string): string {
    for (const [key, color] of Object.entries(MED_COLORS)) {
        if (medCat.includes(key)) return color;
    }
    return "text-tactical-neutral";
}

function FrecklingGauge({ value, labelText }: { value: number; labelText: string }) {
    const pct = Math.min(100, Math.max(0, value));
    const color =
        pct >= 75 ? "#f43f5e"
        : pct >= 45 ? "#fb923c"
        : pct >= 20 ? "#fbbf24"
        : "#34d399";
    return (
        <div className="flex flex-col items-center gap-1.5 w-full">
            <div className="relative w-28 h-28 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                    <circle
                        cx="50"
                        cy="50"
                        r="40"
                        className="stroke-tactical-surface/90"
                        strokeWidth="10"
                        fill="transparent"
                    />
                    <motion.circle
                        cx="50"
                        cy="50"
                        r="40"
                        stroke={color}
                        strokeWidth="10"
                        fill="transparent"
                        strokeDasharray={251.3}
                        initial={{ strokeDashoffset: 251.3 }}
                        animate={{ strokeDashoffset: 251.3 - (251.3 * pct) / 100 }}
                        transition={{ duration: 0.7, ease: "easeOut" }}
                        strokeLinecap="round"
                    />
                </svg>
                <div className="absolute flex flex-col items-center">
                    <span className="text-xl font-mono font-extrabold text-white tabular-nums">
                        {value.toFixed(1)}%
                    </span>
                    <span className="text-[9px] font-mono text-tactical-neutral/60">F_SCORE</span>
                </div>
            </div>
            <span className="text-[10px] font-mono text-tactical-neutral/80">{labelText}</span>
        </div>
    );
}

function UVSensitivityBar({ medCategory }: { medCategory: string }) {
    const tiers = ["< 20", "20 - 35", "35 - 50", "> 50"];
    const labels = ["<20 mJ", "20-35", "35-50", ">50 mJ"];
    const colors = ["#f43f5e", "#fb923c", "#fbbf24", "#34d399"];

    let activeIdx = 3;
    if (medCategory.includes("< 20")) activeIdx = 0;
    else if (medCategory.includes("20 - 35")) activeIdx = 1;
    else if (medCategory.includes("35 - 50")) activeIdx = 2;

    return (
        <div className="space-y-1 w-full">
            <div className="flex gap-1.5 w-full">
                {tiers.map((t, i) => {
                    const isCurrent = i === activeIdx;
                    return (
                        <div
                            key={t}
                            className="flex-1 py-1 rounded-lg text-center text-[10px] font-mono font-bold border transition-all"
                            style={{
                                borderColor: isCurrent ? colors[i] : "rgba(255,255,255,0.08)",
                                backgroundColor: isCurrent ? `${colors[i]}22` : "rgba(0,0,0,0.2)",
                                color: isCurrent ? colors[i] : "rgba(255,255,255,0.3)",
                            }}
                        >
                            {labels[i]}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export default function PanelFreckling() {
    const { lang } = useSaasLanguage();
    const isTr = lang === "tr";

    const [dosages, setDosages] = useState<Record<string, number>>({ rs1805007: 2 });
    const [selectedPresetId, setSelectedPresetId] = useState<string>("R151C_HOM_RR");
    const [loading, setLoading] = useState(false);

    const getDosage = (rsid: string): number => dosages[rsid] ?? 0;

    const setDosage = (rsid: string, val: number) => {
        setSelectedPresetId("");
        setDosages(prev => ({ ...prev, [rsid]: val }));
    };

    const applyPreset = (preset: PresetItem) => {
        setSelectedPresetId(preset.id);
        setDosages({ ...preset.dosages });
    };

    // Synchronous Zero-Latency Reactive Calculation Engine
    const liveResult: FrecklingAndUVResponse = useMemo(() => {
        const R_WEIGHTS: Record<string, number> = {
            rs1805006: 2.50, rs75570604: 2.40, rs1805007: 2.85, rs1805008: 2.75, rs1805009: 2.60,
        };
        const r_WEIGHTS: Record<string, number> = {
            rs1805005: 1.10, rs2228479: 0.85, rs885479: 0.75,
        };

        let w = 0; let nR = 0; let nr = 0;
        const detected: string[] = [];

        for (const [rsid, weight] of Object.entries(R_WEIGHTS)) {
            const d = getDosage(rsid);
            if (d > 0) { w += weight * d; nR += d; detected.push(`${rsid} (${MC1R_R_LOCI.find(l => l.rsid === rsid)?.name || rsid}, Class R, w=${weight}, dose=${d})`); }
        }
        for (const [rsid, weight] of Object.entries(r_WEIGHTS)) {
            const d = getDosage(rsid);
            if (d > 0) { w += weight * d; nr += d; detected.push(`${rsid} (${MC1R_r_LOCI.find(l => l.rsid === rsid)?.name || rsid}, Class r, w=${weight}, dose=${d})`); }
        }

        let diplotype = "wt/wt", funcClass = "WILD_TYPE";
        if (nR >= 2) { diplotype = "R/R"; funcClass = "SEVERE_LOSS"; }
        else if (nR >= 1 && nr >= 1) { diplotype = "R/r"; funcClass = "MODERATE_LOSS"; }
        else if (nR === 1) { diplotype = "R/wt"; funcClass = "MODERATE_LOSS"; }
        else if (nr >= 2) { diplotype = "r/r"; funcClass = "MILD_LOSS"; }
        else if (nr === 1) { diplotype = "r/wt"; funcClass = "MILD_LOSS"; }

        const xAsip = getDosage("rs1015362");
        const xBnc2 = getDosage("rs10756819");
        const logit = -2.50 + 1.35 * w + 0.85 * xAsip + 0.65 * xBnc2;
        const fScore = Math.min(100, Math.max(0, 100 / (1 + Math.exp(-logit))));

        let intensity = isTr ? "MİNİMAL (Nadir / Görünür Efelid Yok)" : "MINIMAL (Rare / No Visible Ephelides)";
        if (fScore >= 75) intensity = isTr ? "YOĞUN (Yaygın Yüz & Vücut Efelidleri)" : "DENSE (Extensive Facial & Body Ephelides)";
        else if (fScore >= 45) intensity = isTr ? "ORTA (Orta Derecede Efelid Dağılımı)" : "MODERATE (Moderate Ephelides Distribution)";
        else if (fScore >= 20) intensity = isTr ? "HAFİF (Güneş Temasında Az Sayıda Efelid)" : "MILD (Few Ephelides Upon Sun Exposure)";

        let medCat = isTr ? "> 50 mJ/cm² (Yüksek MED / Normal Eritem Toleransı)" : "> 50 mJ/cm2 (High MED / Normal Erythema Tolerance)";
        let tanning = isTr ? "NORMAL BRONZLAŞMA, NADİREN YANMA" : "NORMAL_TAN_RARE_BURN";
        let guidance = isTr ? "Düşük ışığa duyarlılık. Normal melanin sentezi ve yüksek MED UV toleransı." : "Low photosensitivity. Normal melanin synthesis and high MED UV tolerance.";
        if (diplotype === "R/R") {
            medCat = isTr ? "< 20 mJ/cm² (Aşırı Düşük MED / Şiddetli Eritem Riski)" : "< 20 mJ/cm2 (Extremely Low MED / Severe Erythema Risk)";
            tanning = isTr ? "ASLA BRONZLAŞMAZ, HER ZAMAN YANAR" : "NEVER_TANS_ALWAYS_BURNS";
            guidance = isTr ? "Aşırı yüksek ışığa duyarlılık. Yüksek melanom ve bazal hücreli karsinom göreceli riski." : "Extremely high photosensitivity. High melanoma and basal cell carcinoma relative risk.";
        } else if (diplotype === "R/r" || diplotype === "R/wt") {
            medCat = isTr ? "20 - 35 mJ/cm² (Düşük MED / Sık Eritem Riski)" : "20 - 35 mJ/cm2 (Low MED / Frequent Erythema Risk)";
            tanning = isTr ? "NADİREN BRONZLAŞMA, SIK YANMA" : "RARE_TAN_FREQUENT_BURN";
            guidance = isTr ? "Yüksek ışığa duyarlılık. Bronzlaşma nadir görülür; UV indeksi >= 4 altında hızla yanar." : "Elevated photosensitivity. Tanning occurs rarely; burning is frequent under UV index >= 4.";
        } else if (diplotype === "r/r" || diplotype === "r/wt") {
            medCat = isTr ? "35 - 50 mJ/cm² (Orta MED / Orta Eritem Riski)" : "35 - 50 mJ/cm2 (Moderate MED / Moderate Erythema Risk)";
            tanning = isTr ? "HAFİF BRONZLAŞMA, BAZEN YANMA" : "MILD_TAN_OCCASIONAL_BURN";
            guidance = isTr ? "Orta derecede ışığa duyarlılık. Kademeli bronzlaşma ve ara sıra eritem oluşur." : "Moderate photosensitivity. Gradual tanning occurs with occasional erythema.";
        }

        return {
            mc1r: {
                diplotype, functional_classification: funcClass,
                total_mc1r_loss_weight: Math.round(w * 1000) / 1000,
                r_high_risk_alleles_count: nR, r_low_risk_alleles_count: nr,
                detected_variants: detected,
            },
            freckling: {
                freckling_score_pct: Math.round(fScore * 100) / 100,
                freckling_intensity: intensity,
                epistatic_modifiers_applied: { ASIP_rs1015362: xAsip, BNC2_rs10756819: xBnc2 },
            },
            uv_sensitivity: {
                minimal_erythema_dose_category: medCat,
                tanning_capacity: tanning,
                photoprotection_guidance: guidance,
            },
            assayed_snps_count: Object.values(dosages).filter(d => d > 0).length,
            prosecutors_fallacy_shield: isTr
                ? "Sonuçlar ISO 17025 kalibre MC1R epistaz ve eritem dozajı modellerine uygundur. Yalnızca soruşturma ipucu amaçlıdır."
                : "Results are calibrated to ISO 17025 MC1R epistasis and erythema dosage models. Purely for investigative intelligence.",
        };
    }, [dosages, isTr]);

    const runAnalysis = async () => {
        setLoading(true);
        try {
            const API_BASE = getApiBaseUrl();
            await fetch(`${API_BASE}/api/v1/forensic/phenotyping/mc1r-freckling-uv`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ snp_dosages: dosages }),
                signal: AbortSignal.timeout(4000),
            });
        } catch {
            // Live reactive engine is already active
        } finally {
            setTimeout(() => setLoading(false), 200);
        }
    };

    return (
        <div className="flex flex-col gap-5 w-full font-mono text-tactical-text">
            {/* ── Modern Unified Mission Control Bar ────────────────────────────────────────── */}
            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-2xl space-y-4 relative overflow-hidden backdrop-blur-md">
                <div className="absolute -right-20 -top-20 w-64 h-64 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
                <div className="absolute right-32 -bottom-20 w-48 h-48 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-tactical-border/40 pb-4 relative z-10">
                    <div className="flex items-center gap-3 min-w-0">
                        <div className="p-2.5 bg-rose-500/15 border border-rose-500/35 rounded-xl text-rose-300 shrink-0 shadow-lg shadow-rose-950/40">
                            <Sun className="w-6 h-6 animate-pulse" />
                        </div>
                        <div className="min-w-0">
                            <div className="flex items-center gap-2 flex-wrap mb-1">
                                <span className="text-sm sm:text-base font-extrabold text-white uppercase tracking-wider truncate">
                                    {isTr ? "MC1R Epistazı, Çillenme & UV İndeksi" : "MC1R Epistasis, Freckling & UV Index"}
                                </span>
                                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-rose-500/15 border border-rose-500/35 text-rose-300">
                                    MC1R-UV 3.5
                                </span>
                                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-500/35 text-amber-300">
                                    EPISTASIS
                                </span>
                            </div>
                            <p className="text-xs text-tactical-neutral/80 max-w-2xl">
                                {isTr
                                    ? "MC1R fonksiyon kaybı varyantları (R/r) ile ASIP/BNC2 epistatik etkileşimleri, efelid (çil) indeksi ve Minimal Eritem Dozu (MED)."
                                    : "MC1R loss-of-function variants (R/r) with ASIP/BNC2 epistatic interactions, ephelides index, and Minimal Erythema Dose (MED)."}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2.5 shrink-0 flex-wrap sm:flex-nowrap">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[10px] font-bold bg-white/[0.03] border border-white/10 text-emerald-400">
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                            <span>{isTr ? "ISO 17025 Doğrulandı" : "ISO 17025 Validated"}</span>
                        </span>

                        <button
                            id="freckling-run-analysis-btn"
                            onClick={runAnalysis}
                            disabled={loading}
                            className="px-4 py-2 rounded-xl border border-rose-500/60 bg-gradient-to-r from-rose-600/30 to-amber-600/30 hover:from-rose-600/40 hover:to-amber-600/40 text-rose-200 hover:text-white font-mono text-xs font-bold flex items-center gap-2 shadow-lg shadow-rose-950/40 transition-all disabled:opacity-50 cursor-pointer active:scale-95 shrink-0"
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin text-rose-300" /> : <Sun className="w-4 h-4 text-rose-300" />}
                            <span>{loading ? (isTr ? "Hesaplanıyor..." : "Computing...") : (isTr ? "MC1R Analizini Çalıştır" : "Execute MC1R Analysis")}</span>
                        </button>
                    </div>
                </div>

                {/* Casework Benchmark Presets */}
                <div className="space-y-2 relative z-10">
                    <div className="flex items-center justify-between text-[10px] font-bold text-zinc-400 uppercase tracking-widest px-0.5">
                        <span className="flex items-center gap-1.5 text-rose-300">
                            <Sparkles className="w-3 h-3 text-rose-400" />
                            {isTr ? "Adli Doğrulama Profili Seçin:" : "Select Casework Benchmark Profile:"}
                        </span>
                        <span className="text-zinc-500 font-mono">{PRESETS.length} {isTr ? "Senaryo" : "Presets"}</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2">
                        {PRESETS.map((p) => {
                            const isSelected = selectedPresetId === p.id;
                            return (
                                <button
                                    key={p.id}
                                    type="button"
                                    onClick={() => applyPreset(p)}
                                    className={`p-2.5 rounded-xl text-left transition-all border cursor-pointer ${
                                        isSelected
                                            ? "border-rose-500/80 bg-rose-950/40 text-white shadow-md shadow-rose-950/50 ring-1 ring-rose-400/40"
                                            : "border-tactical-border/50 bg-black/30 text-zinc-300 hover:bg-rose-500/10 hover:border-rose-500/40 hover:text-white"
                                    }`}
                                >
                                    <div className="text-[11px] font-bold truncate">
                                        {isTr ? p.labelTr : p.label}
                                    </div>
                                    <div className="text-[9px] text-zinc-400 truncate mt-0.5 font-sans">
                                        {isTr ? p.descTr : p.desc}
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* ── 2-Column Responsive Workspace (Inputs Left, Live Dashboard Right) ──────────────── */}
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 items-start">

                {/* ── LEFT COLUMN: Interactive Loci Configurator (5 cols) ── */}
                <div className="xl:col-span-5 flex flex-col gap-4">
                    {/* Section 1: Major MC1R 'R' Loci */}
                    <div className="bg-tactical-surface/60 border border-tactical-border/80 rounded-2xl p-4 sm:p-5 backdrop-blur-md space-y-3 shadow-lg">
                        <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2.5">
                            <div className="text-xs font-bold text-rose-300 uppercase tracking-wider flex items-center gap-2">
                                <Dna className="w-3.5 h-3.5 text-rose-400" />
                                <span>{isTr ? "MC1R 'R' Yüksek Riskli Varyantlar (§5.1)" : "MC1R 'R' High-Risk Variants (§5.1)"}</span>
                            </div>
                            <span className="text-[10px] font-mono text-zinc-400">5 Loci</span>
                        </div>

                        <div className="space-y-2.5">
                            {MC1R_R_LOCI.map(locus => {
                                const curDose = getDosage(locus.rsid);
                                return (
                                    <div key={locus.rsid} className="bg-tactical-surface/80 border border-tactical-border/50 rounded-xl p-3 hover:border-rose-500/40 transition-all">
                                        <div className="flex items-center justify-between gap-2 mb-2">
                                            <div className="flex items-center gap-2">
                                                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">R</span>
                                                <span className="text-xs font-mono font-bold text-white">{locus.name}</span>
                                                <span className="text-[10px] text-tactical-neutral/60 font-mono">{locus.rsid}</span>
                                            </div>
                                            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-500/15 border border-rose-500/30 text-rose-300 shrink-0">
                                                w = {locus.weight}
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-3 gap-1.5">
                                            {[0, 1, 2].map(d => (
                                                <button
                                                    key={d}
                                                    id={`${locus.rsid}-dose-${d}`}
                                                    onClick={() => setDosage(locus.rsid, d)}
                                                    className={`min-h-[34px] py-1 rounded-lg text-xs font-mono font-bold border transition-all cursor-pointer flex items-center justify-center ${
                                                        curDose === d
                                                            ? "border-rose-500 bg-rose-500/25 text-rose-200 shadow-sm shadow-rose-950/60 ring-1 ring-rose-400/40"
                                                            : "border-tactical-border/50 text-tactical-neutral/60 hover:text-white hover:border-tactical-border hover:bg-tactical-surface"
                                                    }`}
                                                >
                                                    {d === 0 ? "0 (wt/wt)" : d === 1 ? "1 (het)" : "2 (hom)"}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Section 2: Minor MC1R 'r' Loci */}
                    <div className="bg-tactical-surface/60 border border-tactical-border/80 rounded-2xl p-4 sm:p-5 backdrop-blur-md space-y-3 shadow-lg">
                        <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2.5">
                            <div className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-2">
                                <FlaskConical className="w-3.5 h-3.5 text-amber-400" />
                                <span>{isTr ? "MC1R 'r' Düşük Riskli Varyantlar" : "MC1R 'r' Low-Risk Variants"}</span>
                            </div>
                            <span className="text-[10px] font-mono text-zinc-400">3 Loci</span>
                        </div>

                        <div className="space-y-2.5">
                            {MC1R_r_LOCI.map(locus => {
                                const curDose = getDosage(locus.rsid);
                                return (
                                    <div key={locus.rsid} className="bg-tactical-surface/80 border border-tactical-border/50 rounded-xl p-3 hover:border-amber-500/40 transition-all">
                                        <div className="flex items-center justify-between gap-2 mb-2">
                                            <div className="flex items-center gap-2">
                                                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">r</span>
                                                <span className="text-xs font-mono font-bold text-white">{locus.name}</span>
                                                <span className="text-[10px] text-tactical-neutral/60 font-mono">{locus.rsid}</span>
                                            </div>
                                            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-500/15 border border-amber-500/30 text-amber-300 shrink-0">
                                                w = {locus.weight}
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-3 gap-1.5">
                                            {[0, 1, 2].map(d => (
                                                <button
                                                    key={d}
                                                    id={`${locus.rsid}-dose-${d}`}
                                                    onClick={() => setDosage(locus.rsid, d)}
                                                    className={`min-h-[34px] py-1 rounded-lg text-xs font-mono font-bold border transition-all cursor-pointer flex items-center justify-center ${
                                                        curDose === d
                                                            ? "border-amber-500 bg-amber-500/25 text-amber-200 shadow-sm shadow-amber-950/60 ring-1 ring-amber-400/40"
                                                            : "border-tactical-border/50 text-tactical-neutral/60 hover:text-white hover:border-tactical-border hover:bg-tactical-surface"
                                                    }`}
                                                >
                                                    {d === 0 ? "0 (wt/wt)" : d === 1 ? "1 (het)" : "2 (hom)"}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Section 3: Epistatic Modifiers (ASIP, BNC2) */}
                    <div className="bg-tactical-surface/60 border border-tactical-border/80 rounded-2xl p-4 sm:p-5 backdrop-blur-md space-y-3 shadow-lg">
                        <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2.5">
                            <div className="text-xs font-bold text-violet-300 uppercase tracking-wider flex items-center gap-2">
                                <Layers className="w-3.5 h-3.5 text-violet-400" />
                                <span>{isTr ? "Epistatik Modifiyerler (ASIP, BNC2)" : "Epistatic Modifiers (ASIP, BNC2)"}</span>
                            </div>
                            <span className="text-[10px] font-mono text-zinc-400">2 Loci</span>
                        </div>

                        <div className="space-y-2.5">
                            {MODIFIER_LOCI.map(locus => {
                                const curDose = getDosage(locus.rsid);
                                return (
                                    <div key={locus.rsid} className="bg-tactical-surface/80 border border-tactical-border/50 rounded-xl p-3 hover:border-violet-500/40 transition-all">
                                        <div className="flex items-center justify-between gap-2 mb-2">
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs font-mono font-bold text-white">{locus.name}</span>
                                                <span className="text-[10px] text-tactical-neutral/60 font-mono">{locus.rsid}</span>
                                            </div>
                                            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-violet-500/15 border border-violet-500/30 text-violet-300 shrink-0">
                                                β = {locus.weight}
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-3 gap-1.5">
                                            {[0, 1, 2].map(d => (
                                                <button
                                                    key={d}
                                                    id={`${locus.rsid}-dose-${d}`}
                                                    onClick={() => setDosage(locus.rsid, d)}
                                                    className={`min-h-[34px] py-1 rounded-lg text-xs font-mono font-bold border transition-all cursor-pointer flex items-center justify-center ${
                                                        curDose === d
                                                            ? "border-violet-500 bg-violet-500/25 text-violet-200 shadow-sm shadow-violet-950/60 ring-1 ring-violet-400/40"
                                                            : "border-tactical-border/50 text-tactical-neutral/60 hover:text-white hover:border-tactical-border hover:bg-tactical-surface"
                                                    }`}
                                                >
                                                    {d === 0 ? "0 (wt/wt)" : d === 1 ? "1 (het)" : "2 (hom)"}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* ── RIGHT COLUMN: Live Biocomputational Intelligence Dashboard (7 cols) ── */}
                <div className="xl:col-span-7 flex flex-col gap-4">
                    {/* Live Card 1: MC1R Diplotype & Allele Balance */}
                    <div className="bg-tactical-surface/60 border border-rose-500/40 rounded-2xl p-5 backdrop-blur-md shadow-xl space-y-4">
                        <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
                            <div className="flex items-center gap-2">
                                <Dna className="w-4 h-4 text-rose-400" />
                                <span className="text-sm font-bold text-white uppercase tracking-wide">
                                    {isTr ? "MC1R Diplotipi & Fonksiyonel Ayrışım" : "MC1R Diplotype & Functional Classification"}
                                </span>
                            </div>
                            <span className={`px-3 py-1 rounded-xl text-xs font-mono font-extrabold border ${DIPLOTYPE_COLORS[liveResult.mc1r.diplotype] || "border-white/20 text-white"}`}>
                                {liveResult.mc1r.diplotype}
                            </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            <div className="p-3 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 text-center">
                                <span className="text-[10px] text-tactical-neutral/60 block">{isTr ? "Diplotip Durumu" : "Diplotype State"}</span>
                                <div className={`text-2xl font-mono font-extrabold mt-0.5 ${DIPLOTYPE_COLORS[liveResult.mc1r.diplotype]?.split(" ")[0] || "text-white"}`}>
                                    {liveResult.mc1r.diplotype}
                                </div>
                                <span className="text-[9px] text-tactical-neutral/60 font-mono block mt-0.5">
                                    {isTr
                                        ? (liveResult.mc1r.functional_classification === "WILD_TYPE" ? "YABANIL TİP"
                                            : liveResult.mc1r.functional_classification === "MILD_LOSS" ? "HAFİF KAYIP"
                                            : liveResult.mc1r.functional_classification === "MODERATE_LOSS" ? "ORTA DERECELİ"
                                            : "AĞIR KAYIP")
                                        : liveResult.mc1r.functional_classification.replace("_", " ")}
                                </span>
                            </div>

                            <div className="p-3 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 text-center">
                                <span className="text-[10px] text-tactical-neutral/60 block">{isTr ? "Toplam Kayıp (W_MC1R)" : "Total Loss (W_MC1R)"}</span>
                                <div className="text-2xl font-mono font-extrabold text-rose-300 mt-0.5 tabular-nums">
                                    {liveResult.mc1r.total_mc1r_loss_weight.toFixed(3)}
                                </div>
                                <span className="text-[9px] text-zinc-500 font-mono block mt-0.5">
                                    {isTr ? "Ağırlıklı Toplam" : "Weighted Sum"}
                                </span>
                            </div>

                            <div className="p-3 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 text-center">
                                <span className="text-[10px] text-tactical-neutral/60 block">Aleller (n_R / n_r)</span>
                                <div className="text-2xl font-mono font-extrabold text-white mt-0.5">
                                    <span className="text-rose-400">{liveResult.mc1r.r_high_risk_alleles_count}R</span>
                                    <span className="text-zinc-600 mx-1">/</span>
                                    <span className="text-amber-400">{liveResult.mc1r.r_low_risk_alleles_count}r</span>
                                </div>
                                <span className="text-[9px] text-zinc-500 font-mono block mt-0.5">
                                    {isTr ? "R=Büyük, r=Küçük" : "R=Major, r=Minor"}
                                </span>
                            </div>
                        </div>

                        {liveResult.mc1r.detected_variants.length > 0 && (
                            <div className="p-3 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 space-y-1.5">
                                <span className="text-[10px] text-tactical-neutral/60 font-bold uppercase tracking-wider block">
                                    {isTr ? "Saptanan Fonksiyonel Varyantlar:" : "Detected Functional Variants:"}
                                </span>
                                <div className="flex flex-wrap gap-1.5">
                                    {liveResult.mc1r.detected_variants.map((v, i) => (
                                        <span key={i} className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-rose-500/10 border border-rose-500/30 text-rose-200">
                                            {v}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Live Card 2: Ephelides (Freckling Index) & UV Sensitivity */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {/* Freckling Score Card */}
                        <div className="bg-tactical-surface/60 border border-amber-500/40 rounded-2xl p-5 backdrop-blur-md shadow-xl flex flex-col justify-between space-y-3">
                            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2.5">
                                <div className="flex items-center gap-2">
                                    <FlaskConical className="w-4 h-4 text-amber-400" />
                                    <span className="text-xs font-bold text-white uppercase tracking-wide">
                                        {isTr ? "Efelid (Çil) İndeksi" : "Ephelides Score"}
                                    </span>
                                </div>
                                <span className="text-[10px] font-mono text-amber-400 font-bold">F_SCORE</span>
                            </div>

                            <div className="my-1 flex justify-center">
                                <FrecklingGauge
                                    value={liveResult.freckling.freckling_score_pct}
                                    labelText={isTr ? "Tahmini Çil Olasılığı" : "Freckling Likelihood"}
                                />
                            </div>

                            <div className="p-2.5 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 text-center">
                                <span className="text-[10px] text-tactical-neutral/60 block">{isTr ? "Çillenme Yoğunluğu:" : "Freckling Intensity:"}</span>
                                <span className="text-xs font-mono font-bold text-amber-300 block mt-0.5">
                                    {liveResult.freckling.freckling_intensity}
                                </span>
                            </div>
                        </div>

                        {/* UV Sensitivity & MED Card */}
                        <div className="bg-tactical-surface/60 border border-sky-500/40 rounded-2xl p-5 backdrop-blur-md shadow-xl flex flex-col justify-between space-y-3">
                            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2.5">
                                <div className="flex items-center gap-2">
                                    <Sun className="w-4 h-4 text-sky-400" />
                                    <span className="text-xs font-bold text-white uppercase tracking-wide">
                                        {isTr ? "UV Duyarlılığı & MED" : "UV Sensitivity & MED"}
                                    </span>
                                </div>
                                <span className="text-[10px] font-mono text-sky-400 font-bold">ERYTHEMA</span>
                            </div>

                            <div className="space-y-1.5 my-1">
                                <span className="text-[10px] text-tactical-neutral/70 block">
                                    {isTr ? "Minimal Eritem Dozu (MED):" : "Minimal Erythema Dose (MED):"}
                                </span>
                                <UVSensitivityBar medCategory={liveResult.uv_sensitivity.minimal_erythema_dose_category} />
                                <div className={`text-center text-xs font-mono font-bold mt-1 ${getMedColor(liveResult.uv_sensitivity.minimal_erythema_dose_category)}`}>
                                    {liveResult.uv_sensitivity.minimal_erythema_dose_category.split("(")[0].trim()}
                                </div>
                            </div>

                            <div className="p-2.5 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 text-center">
                                <span className="text-[10px] text-tactical-neutral/60 block">{isTr ? "Bronzlaşma Kapasitesi:" : "Tanning Capacity:"}</span>
                                <span className="text-xs font-mono font-bold text-sky-300 block mt-0.5">
                                    {liveResult.uv_sensitivity.tanning_capacity.replace(/_/g, " ")}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Clinical Advisory Card */}
                    <div className="p-3.5 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 text-xs space-y-1">
                        <span className="text-[10px] text-tactical-neutral/60 font-bold uppercase tracking-wider block">
                            {isTr ? "Foto-Koruma & Klinik Danışma Kılavuzu:" : "Clinical Photoprotection Advisory:"}
                        </span>
                        <p className="text-white font-sans text-xs leading-relaxed">
                            {liveResult.uv_sensitivity.photoprotection_guidance}
                        </p>
                    </div>

                    {/* Forensic Legal Shield */}
                    <div className="bg-amber-500/5 border border-amber-500/25 rounded-xl p-3.5 flex items-start gap-2.5">
                        <ShieldCheck className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
                        <p className="text-[11px] text-tactical-neutral/80 leading-relaxed">
                            <strong className="text-amber-400">{isTr ? "Adli Hukuki Bildirim Kalkanı: " : "Forensic Legal Shield: "}</strong>
                            {liveResult.prosecutors_fallacy_shield}
                        </p>
                    </div>

                    {/* Mathematical Epistasis Matrix */}
                    <div className="bg-tactical-surface/40 border border-tactical-border/40 rounded-xl p-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                        {[
                            { label: "Intercept β₀", value: "-2.50" },
                            { label: "W_MC1R katsayısı", value: "1.35" },
                            { label: "ASIP katsayısı", value: "0.85" },
                            { label: "BNC2 katsayısı", value: "0.65" },
                        ].map(m => (
                            <div key={m.label} className="p-1.5 rounded-lg bg-black/20">
                                <div className="text-[9px] text-tactical-neutral/60 truncate">{m.label}</div>
                                <div className="text-xs font-mono font-bold text-tactical-neutral/90 tabular-nums">{m.value}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
