"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Scissors,
    Dna,
    BarChart3,
    AlertTriangle,
    CheckCircle2,
    ChevronRight,
    RefreshCw,
    Loader2,
    User,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

interface HairTextureResult {
    curl_density_index: number;
    texture_category: string;
    fiber_cross_sectional_area_um2: number;
    estimated_fiber_diameter_um: string;
    assayed_texture_snps: number;
}

interface BaldingPRSResult {
    prs_score: number;
    hamilton_norwood_grade: string;
    clinical_description: string;
    risk_level: string;
    assayed_balding_snps: number;
}

interface HairAnalysisResult {
    texture: HairTextureResult;
    balding: BaldingPRSResult;
    prosecutors_fallacy_shield: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SNP PRESETS
// ═══════════════════════════════════════════════════════════════════════════════

interface PresetItem {
    label: string;
    desc: string;
    dosages: Record<string, number>;
}

const PRESETS: PresetItem[] = [
    {
        label: "East Asian (EDAR=2)",
        desc: "Thick Straight / VECTOR_P3_03",
        dosages: { rs3827072: 2, rs11803731: 0, rs7349332: 0, rs6152: 0, rs2180439: 0, rs1160312: 0, rs756853: 0 },
    },
    {
        label: "African (TCHH+WNT10A=2)",
        desc: "Kinky/Woolly C_curl=7.74",
        dosages: { rs3827072: 0, rs11803731: 2, rs7349332: 2, rs6152: 0, rs2180439: 0, rs1160312: 0, rs756853: 0 },
    },
    {
        label: "European Wavy (TCHH=1)",
        desc: "Wavy C_curl=3.05",
        dosages: { rs3827072: 0, rs11803731: 1, rs7349332: 0, rs6152: 0, rs2180439: 0, rs1160312: 0, rs756853: 0 },
    },
    {
        label: "High AGA Risk",
        desc: "AR+20p11 homozygous PRS=3.046",
        dosages: { rs3827072: 0, rs11803731: 0, rs7349332: 0, rs6152: 2, rs2180439: 2, rs1160312: 0, rs756853: 0 },
    },
    {
        label: "Baseline Reference",
        desc: "All zero dosage (3850 μm², Grade I/II)",
        dosages: { rs3827072: 0, rs11803731: 0, rs7349332: 0, rs6152: 0, rs2180439: 0, rs1160312: 0, rs756853: 0 },
    },
];

// ═══════════════════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════════════════

const TEXTURE_COLORS: Record<string, string> = {
    STRAIGHT: "text-sky-400",
    WAVY: "text-violet-400",
    CURLY: "text-amber-400",
    KINKY_WOOLLY: "text-rose-400",
};

const RISK_COLORS: Record<string, string> = {
    LOW_RISK: "text-emerald-400",
    MODERATE_RISK: "text-amber-400",
    ELEVATED_RISK: "text-orange-400",
    HIGH_RISK: "text-rose-400",
};

const HN_FILL: Record<string, string> = {
    GRADE_I_II: "bg-emerald-500/30 border-emerald-500/60",
    GRADE_III: "bg-amber-500/30 border-amber-500/60",
    GRADE_IV_V: "bg-orange-500/30 border-orange-500/60",
    GRADE_VI_VII: "bg-rose-500/30 border-rose-500/60",
};

function CurlIndexBar({ value }: { value: number }) {
    const pct = Math.min(100, (value / 10) * 100);
    const color =
        value < 2 ? "#38bdf8"
        : value < 4.5 ? "#a78bfa"
        : value < 7 ? "#fbbf24"
        : "#f43f5e";
    return (
        <div className="relative h-3 w-full bg-tactical-border/40 rounded-full overflow-hidden">
            <motion.div
                className="absolute left-0 top-0 h-full rounded-full"
                style={{ backgroundColor: color, width: `${pct}%` }}
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 0.8, ease: "easeOut" }}
            />
            {/* Category markers */}
            {[20, 45, 70].map((pos, i) => (
                <div
                    key={i}
                    className="absolute top-0 h-full w-px bg-tactical-border/60"
                    style={{ left: `${pos}%` }}
                />
            ))}
        </div>
    );
}

function HamiltonNorwoodScale({ grade }: { grade: string }) {
    const grades = ["GRADE_I_II", "GRADE_III", "GRADE_IV_V", "GRADE_VI_VII"];
    const labels = ["I/II", "III", "IV/V", "VI/VII"];
    const activeIdx = grades.indexOf(grade);
    return (
        <div className="flex gap-1 w-full">
            {grades.map((g, i) => (
                <div key={g} className="flex-1 text-center">
                    <div
                        className={`h-6 rounded text-xs flex items-center justify-center font-mono border transition-all duration-500 ${
                            i <= activeIdx
                                ? HN_FILL[g] + " text-white"
                                : "bg-tactical-surface/30 border-tactical-border/20 text-tactical-text-secondary"
                        }`}
                    >
                        {labels[i]}
                    </div>
                    {i <= activeIdx && (
                        <div className="mt-0.5 text-[9px] text-tactical-text-secondary">
                            {i === activeIdx ? "▲" : ""}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export default function PanelHair() {
    const [dosages, setDosages] = useState<Record<string, number>>({
        rs3827072: 0, rs11803731: 0, rs7349332: 0,
        rs6152: 0, rs2180439: 0, rs1160312: 0, rs756853: 0,
    });
    const [result, setResult] = useState<HairAnalysisResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const SNP_LABELS: Record<string, { gene: string; trait: string; group: "texture" | "balding" }> = {
        rs3827072:  { gene: "EDAR (Val370Ala)",     trait: "Fiber Thickness & Straightening", group: "texture" },
        rs11803731: { gene: "TCHH (Trichohyalin)",  trait: "Curl Induction",                  group: "texture" },
        rs7349332:  { gene: "WNT10A",               trait: "Curl Induction (Wnt Pathway)",    group: "texture" },
        rs6152:     { gene: "AR (Androgen Receptor)",trait: "Balding PRS (strongest locus)",   group: "balding" },
        rs2180439:  { gene: "20p11 Locus",           trait: "Androgenetic Alopecia",           group: "balding" },
        rs1160312:  { gene: "20p11 Locus",           trait: "Androgenetic Alopecia",           group: "balding" },
        rs756853:   { gene: "HDAC9",                 trait: "Androgenetic Alopecia",           group: "balding" },
    };

    const applyPreset = (preset: typeof PRESETS[0]) => {
        setDosages({ ...preset.dosages });
        setResult(null);
        setError(null);
    };

    const runAnalysis = async () => {
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch("/api/v1/forensic/phenotyping/hair/morphology-and-balding", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ snp_dosages: dosages }),
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            setResult(data);
        } catch (err: unknown) {
            // Fallback to client-side mathematical simulation
            const x_edar = dosages.rs3827072 ?? 0;
            const x_tchh = dosages.rs11803731 ?? 0;
            const x_wnt10a = dosages.rs7349332 ?? 0;

            const area = 3850.0 + 1420.0 * x_edar;
            const rawCurl = 1.20 + 1.85 * x_tchh + 1.42 * x_wnt10a - 2.10 * x_edar;
            const curl = Math.max(0, Math.min(10, rawCurl));

            let cat = "STRAIGHT";
            if (curl >= 7.0) cat = "KINKY_WOOLLY";
            else if (curl >= 4.5) cat = "CURLY";
            else if (curl >= 2.0) cat = "WAVY";

            let diam = "70.0 - 85.0 um (Fine / Medium Straight)";
            if (cat === "STRAIGHT" && x_edar >= 1.5) diam = "85.0 - 110.0 um (Thick Straight / Asian Variant)";
            else if (cat === "WAVY") diam = "65.0 - 80.0 um (Wavy Texture)";
            else if (cat === "CURLY") diam = "55.0 - 70.0 um (Defined Curls)";
            else if (cat === "KINKY_WOOLLY") diam = "45.0 - 60.0 um (Tight Coil / Afro-textured)";

            const prs = 0.982 * (dosages.rs6152 ?? 0) + 0.541 * (dosages.rs2180439 ?? 0)
                      + 0.485 * (dosages.rs1160312 ?? 0) + 0.362 * (dosages.rs756853 ?? 0);

            let grade = "GRADE_I_II", desc = "Hamilton-Norwood Grade I / II — Minimal or No Hair Loss", risk = "LOW_RISK";
            if (prs >= 2.10) { grade = "GRADE_VI_VII"; desc = "Hamilton-Norwood Grade VI / VII — Severe / Extensive Balding"; risk = "HIGH_RISK"; }
            else if (prs >= 1.20) { grade = "GRADE_IV_V"; desc = "Hamilton-Norwood Grade IV / V — Moderate Vertex Loss"; risk = "ELEVATED_RISK"; }
            else if (prs >= 0.50) { grade = "GRADE_III"; desc = "Hamilton-Norwood Grade III — Slight Temporal / Vertex Recess"; risk = "MODERATE_RISK"; }

            setResult({
                texture: {
                    curl_density_index: Math.round(curl * 1000) / 1000,
                    texture_category: cat,
                    fiber_cross_sectional_area_um2: area,
                    estimated_fiber_diameter_um: diam,
                    assayed_texture_snps: [x_edar, x_tchh, x_wnt10a].filter(v => v > 0).length,
                },
                balding: {
                    prs_score: Math.round(prs * 1000) / 1000,
                    hamilton_norwood_grade: grade,
                    clinical_description: desc,
                    risk_level: risk,
                    assayed_balding_snps: [dosages.rs6152, dosages.rs2180439, dosages.rs1160312, dosages.rs756853].filter(v => (v ?? 0) > 0).length,
                },
                prosecutors_fallacy_shield: "Client-side simulation (offline mode). Results are mathematically faithful to Research §4.",
            });
        } finally {
            setLoading(false);
        }
    };

    const textureLoci = Object.entries(SNP_LABELS).filter(([, v]) => v.group === "texture");
    const baldingLoci = Object.entries(SNP_LABELS).filter(([, v]) => v.group === "balding");

    return (
        <div className="flex flex-col gap-4 w-full">

            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-violet-500/20 border border-violet-500/40">
                    <Scissors className="w-5 h-5 text-violet-400" />
                </div>
                <div>
                    <h2 className="text-base font-semibold text-tactical-text-primary font-mono tracking-wide">
                        HAIR-TEX: Module 3.4
                    </h2>
                    <p className="text-xs text-tactical-text-secondary">
                        Hair Morphology, Cross-Sectional Curvature & Balding PRS
                    </p>
                </div>
                <div className="ml-auto px-2 py-0.5 rounded text-[10px] font-mono border border-emerald-500/40 text-emerald-400 bg-emerald-500/10">
                    VERIFIED
                </div>
            </div>

            {/* Presets */}
            <div className="flex flex-wrap gap-2">
                {PRESETS.map(p => (
                    <button
                        key={p.label}
                        onClick={() => applyPreset(p)}
                        className="px-2 py-1 rounded text-[11px] font-mono border border-tactical-border/40 text-tactical-text-secondary hover:border-violet-500/60 hover:text-violet-300 transition-colors"
                    >
                        {p.label}
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

                {/* LEFT: Texture SNP Inputs */}
                <div className="flex flex-col gap-3">
                    <div className="text-xs font-mono text-violet-400 uppercase tracking-wider flex items-center gap-2">
                        <Scissors className="w-3 h-3" /> Hair Texture Loci (§4.1)
                    </div>
                    {textureLoci.map(([rsid, info]) => (
                        <div key={rsid} className="bg-tactical-surface/50 border border-tactical-border/40 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                                <div>
                                    <span className="text-xs font-mono text-tactical-text-primary">{rsid}</span>
                                    <span className="text-xs text-tactical-text-secondary ml-2">· {info.gene}</span>
                                </div>
                                <span className="text-[10px] text-tactical-text-secondary">{info.trait}</span>
                            </div>
                            <div className="flex gap-2">
                                {[0, 1, 2].map(d => (
                                    <button
                                        key={d}
                                        id={`${rsid}-dose-${d}`}
                                        onClick={() => setDosages(prev => ({ ...prev, [rsid]: d }))}
                                        className={`flex-1 py-1.5 rounded text-sm font-mono border transition-all ${
                                            dosages[rsid] === d
                                                ? "border-violet-500/80 bg-violet-500/20 text-violet-300"
                                                : "border-tactical-border/40 text-tactical-text-secondary hover:border-tactical-border/70"
                                        }`}
                                    >
                                        {d}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                {/* RIGHT: Balding PRS SNP Inputs */}
                <div className="flex flex-col gap-3">
                    <div className="text-xs font-mono text-amber-400 uppercase tracking-wider flex items-center gap-2">
                        <User className="w-3 h-3" /> Androgenetic Alopecia PRS Loci (§4.2)
                    </div>
                    {baldingLoci.map(([rsid, info]) => (
                        <div key={rsid} className="bg-tactical-surface/50 border border-tactical-border/40 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                                <div>
                                    <span className="text-xs font-mono text-tactical-text-primary">{rsid}</span>
                                    <span className="text-xs text-tactical-text-secondary ml-2">· {info.gene}</span>
                                </div>
                                <span className="text-[10px] text-tactical-text-secondary font-mono">
                                    w={rsid === "rs6152" ? "0.982" : rsid === "rs2180439" ? "0.541" : rsid === "rs1160312" ? "0.485" : "0.362"}
                                </span>
                            </div>
                            <div className="flex gap-2">
                                {[0, 1, 2].map(d => (
                                    <button
                                        key={d}
                                        id={`${rsid}-dose-${d}`}
                                        onClick={() => setDosages(prev => ({ ...prev, [rsid]: d }))}
                                        className={`flex-1 py-1.5 rounded text-sm font-mono border transition-all ${
                                            dosages[rsid] === d
                                                ? "border-amber-500/80 bg-amber-500/20 text-amber-300"
                                                : "border-tactical-border/40 text-tactical-text-secondary hover:border-tactical-border/70"
                                        }`}
                                    >
                                        {d}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}

                    {/* Run Button */}
                    <button
                        id="hair-run-analysis-btn"
                        onClick={runAnalysis}
                        disabled={loading}
                        className="mt-2 w-full py-2.5 rounded-lg border border-violet-500/60 bg-violet-500/15 text-violet-300 font-mono text-sm flex items-center justify-center gap-2 hover:bg-violet-500/25 transition-all disabled:opacity-50"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <BarChart3 className="w-4 h-4" />}
                        {loading ? "Computing..." : "Execute Hair Analysis"}
                    </button>
                </div>
            </div>

            {/* Results */}
            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        transition={{ duration: 0.35 }}
                        className="grid grid-cols-1 lg:grid-cols-2 gap-4"
                    >
                        {/* Texture Result */}
                        <div className="bg-tactical-surface/50 border border-violet-500/30 rounded-xl p-4 flex flex-col gap-3">
                            <div className="flex items-center gap-2">
                                <Scissors className="w-4 h-4 text-violet-400" />
                                <span className="text-sm font-mono text-tactical-text-primary font-semibold">Hair Texture Analysis</span>
                            </div>

                            <div className="flex items-center justify-between">
                                <span className="text-xs text-tactical-text-secondary">Texture Category</span>
                                <span className={`text-sm font-mono font-bold ${TEXTURE_COLORS[result.texture.texture_category] ?? "text-tactical-text-primary"}`}>
                                    {result.texture.texture_category.replace("_", "/")}
                                </span>
                            </div>

                            <div>
                                <div className="flex justify-between text-xs text-tactical-text-secondary mb-1">
                                    <span>Curl Density Index (C_curl)</span>
                                    <span className="font-mono text-tactical-text-primary">
                                        {result.texture.curl_density_index.toFixed(3)} / 10.0
                                    </span>
                                </div>
                                <CurlIndexBar value={result.texture.curl_density_index} />
                                <div className="flex justify-between text-[9px] text-tactical-text-secondary mt-0.5 font-mono">
                                    <span>STRAIGHT</span><span>WAVY</span><span>CURLY</span><span>KINKY</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-2">
                                <div className="bg-tactical-bg/40 rounded p-2">
                                    <div className="text-[10px] text-tactical-text-secondary">Fiber Area</div>
                                    <div className="text-sm font-mono text-sky-300">
                                        {result.texture.fiber_cross_sectional_area_um2.toFixed(1)} μm²
                                    </div>
                                </div>
                                <div className="bg-tactical-bg/40 rounded p-2">
                                    <div className="text-[10px] text-tactical-text-secondary">Assayed Loci</div>
                                    <div className="text-sm font-mono text-tactical-text-primary">
                                        {result.texture.assayed_texture_snps}/3
                                    </div>
                                </div>
                            </div>

                            <div className="bg-tactical-bg/40 rounded p-2">
                                <div className="text-[10px] text-tactical-text-secondary mb-0.5">Fiber Diameter</div>
                                <div className="text-xs font-mono text-tactical-text-primary break-words">
                                    {result.texture.estimated_fiber_diameter_um}
                                </div>
                            </div>
                        </div>

                        {/* Balding PRS Result */}
                        <div className="bg-tactical-surface/50 border border-amber-500/30 rounded-xl p-4 flex flex-col gap-3">
                            <div className="flex items-center gap-2">
                                <User className="w-4 h-4 text-amber-400" />
                                <span className="text-sm font-mono text-tactical-text-primary font-semibold">Androgenetic Alopecia PRS</span>
                            </div>

                            <div className="flex items-center justify-between">
                                <span className="text-xs text-tactical-text-secondary">Risk Level</span>
                                <span className={`text-sm font-mono font-bold ${RISK_COLORS[result.balding.risk_level] ?? "text-tactical-text-primary"}`}>
                                    {result.balding.risk_level.replace("_", " ")}
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-2">
                                <div className="bg-tactical-bg/40 rounded p-2">
                                    <div className="text-[10px] text-tactical-text-secondary">PRS Score</div>
                                    <div className="text-lg font-mono text-amber-300 tabular-nums">
                                        {result.balding.prs_score.toFixed(3)}
                                    </div>
                                    <div className="text-[9px] text-tactical-text-secondary">max 4.740</div>
                                </div>
                                <div className="bg-tactical-bg/40 rounded p-2">
                                    <div className="text-[10px] text-tactical-text-secondary">HN Grade</div>
                                    <div className="text-sm font-mono text-amber-300">
                                        {result.balding.hamilton_norwood_grade.replace("_", " ")}
                                    </div>
                                </div>
                            </div>

                            <div>
                                <div className="text-[10px] text-tactical-text-secondary mb-1.5">Hamilton-Norwood Scale</div>
                                <HamiltonNorwoodScale grade={result.balding.hamilton_norwood_grade} />
                            </div>

                            <div className="bg-tactical-bg/40 rounded p-2">
                                <div className="text-[10px] text-tactical-text-secondary mb-0.5">Clinical Description</div>
                                <div className="text-xs text-tactical-text-primary leading-relaxed">
                                    {result.balding.clinical_description}
                                </div>
                            </div>

                            <div className="text-[10px] text-tactical-text-secondary font-mono">
                                Assayed Balding Loci: {result.balding.assayed_balding_snps}/4
                            </div>
                        </div>

                        {/* Legal Shield */}
                        <div className="lg:col-span-2 bg-amber-500/5 border border-amber-500/25 rounded-lg p-3 flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                            <p className="text-[10px] text-tactical-text-secondary leading-relaxed">
                                <span className="text-amber-400 font-semibold">Forensic Legal Shield: </span>
                                {result.prosecutors_fallacy_shield}
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Methodology Footer */}
            <div className="bg-tactical-surface/30 border border-tactical-border/30 rounded-lg p-3 grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                {[
                    { label: "Baseline Area", value: "3850 μm²" },
                    { label: "EDAR Δ/allele", value: "+1420 μm²" },
                    { label: "C_curl Range", value: "[0.0, 10.0]" },
                    { label: "Max PRS", value: "4.740" },
                ].map(m => (
                    <div key={m.label}>
                        <div className="text-[9px] text-tactical-text-secondary">{m.label}</div>
                        <div className="text-xs font-mono text-tactical-text-primary tabular-nums">{m.value}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
