"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Dna, BarChart3, Brain, Microscope, FileText, Sparkles,
    ChevronRight, Activity, ShieldCheck, Fingerprint,
    FlaskConical, Layers, Cpu, Lock, Radio, AlertTriangle,
    CheckCircle, Clock, TrendingUp, GitBranch, Binary,
    Droplets, Pill, Eye, Bug, Leaf, Bone, Syringe,
    PackageCheck, Scale, Zap, Database,
} from "lucide-react";
import ActiveProfileBanner from "@/components/common/ActiveProfileBanner";
import ModuleAiBanner from "@/components/common/ModuleAiBanner";

// ─── Types ───────────────────────────────────────────────────────────────────

type CategoryId = "dna" | "probabilistic" | "phenotype" | "physical" | "lims" | "ai";
type TabId = string;

interface Category {
    id: CategoryId;
    label: string;
    icon: typeof Dna;
    color: string;
    tabs: Tab[];
}

interface Tab {
    id: TabId;
    label: string;
    icon: typeof Dna;
    badge?: string;
}

// ─── Navigation Structure ──────────────────────────────────────────────────

const CATEGORIES: Category[] = [
    {
        id: "dna",
        label: "DNA & Kinship",
        icon: Dna,
        color: "emerald",
        tabs: [
            { id: "str", label: "STR Locus Analysis", icon: Binary, badge: "CODIS 20" },
            { id: "kinship", label: "Kinship & Relatedness", icon: GitBranch },
            { id: "ancestry", label: "Ancestry Inference", icon: TrendingUp },
            { id: "lineage", label: "Lineage DNA (Y/mt)", icon: Dna },
            { id: "dvi", label: "DVI / Mass Disaster", icon: Database },
            { id: "humanid", label: "Human ID Panel", icon: Fingerprint },
        ],
    },
    {
        id: "probabilistic",
        label: "Probabilistic",
        icon: BarChart3,
        color: "cyan",
        tabs: [
            { id: "mcmc", label: "MCMC Genotyping", icon: Cpu, badge: "50k iter" },
            { id: "mixture", label: "Mixture Deconvolution", icon: Layers },
            { id: "bayesian", label: "Bayesian Framework", icon: BarChart3 },
            { id: "validation", label: "Validation Lab", icon: CheckCircle },
        ],
    },
    {
        id: "phenotype",
        label: "Phenotype",
        icon: Brain,
        color: "purple",
        tabs: [
            { id: "hirisplex", label: "HIrisPlex-S", icon: Eye, badge: "41-SNP" },
            { id: "age", label: "Epigenetic Age Clock", icon: Clock },
            { id: "anthropology", label: "Anthropology", icon: Bone },
            { id: "entomology", label: "Forensic Entomology", icon: Bug },
            { id: "botany", label: "Forensic Botany", icon: Leaf },
            { id: "microbiology", label: "Microbiology", icon: FlaskConical },
        ],
    },
    {
        id: "physical",
        label: "Physical Evidence",
        icon: Microscope,
        color: "orange",
        tabs: [
            { id: "touch", label: "Touch DNA / LtDNA", icon: Fingerprint, badge: "MCMC" },
            { id: "serology", label: "Serology & Blood Group", icon: Droplets },
            { id: "bodyfluid", label: "Body Fluid ID", icon: Syringe },
            { id: "toxicology", label: "Forensic Toxicology", icon: Pill },
            { id: "microscopy", label: "Microscopy & Hair", icon: Microscope },
            { id: "bpa", label: "BPA / Bloodstain Pattern", icon: Eye },
        ],
    },
    {
        id: "lims",
        label: "LIMS & QA/QC",
        icon: FileText,
        color: "blue",
        tabs: [
            { id: "lims", label: "LIMS Workflow", icon: PackageCheck },
            { id: "instrument", label: "Instrument Gateway", icon: Activity },
            { id: "qc", label: "QA / QC Monitor", icon: ShieldCheck },
            { id: "review", label: "Human Review", icon: Scale },
            { id: "isoreport", label: "ISO Report Generator", icon: FileText, badge: "17025" },
            { id: "court", label: "Expert Witness", icon: Scale },
        ],
    },
    {
        id: "ai",
        label: "AI & Advanced",
        icon: Sparkles,
        color: "rose",
        tabs: [
            { id: "epigenetics", label: "Forensic Epigenomics", icon: Zap, badge: "353 CpG" },
            { id: "genomics", label: "Multi-Layer Genomics", icon: Layers },
            { id: "synthetic", label: "Synthetic Case Generator", icon: Sparkles },
            { id: "evidenceos", label: "Evidence OS DAG", icon: Cpu },
            { id: "geo", label: "Geo-Forensic Intel", icon: TrendingUp },
        ],
    },
];

const COLOR_CLASSES: Record<string, { text: string; bg: string; border: string; activeBg: string }> = {
    emerald: { text: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/30", activeBg: "bg-emerald-500/15" },
    cyan: { text: "text-cyan-400", bg: "bg-cyan-500/10", border: "border-cyan-500/30", activeBg: "bg-cyan-500/15" },
    purple: { text: "text-purple-400", bg: "bg-purple-500/10", border: "border-purple-500/30", activeBg: "bg-purple-500/15" },
    orange: { text: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/30", activeBg: "bg-orange-500/15" },
    blue: { text: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/30", activeBg: "bg-blue-500/15" },
    rose: { text: "text-rose-400", bg: "bg-rose-500/10", border: "border-rose-500/30", activeBg: "bg-rose-500/15" },
};

// ─── Panel Placeholders ──────────────────────────────────────────────────────
// Each panel is a self-contained demo with mock data

function PanelSTR() {
    const loci = [
        { locus: "D3S1358", evid: "15, 17", ref: "15, 17", lr: "1.2×10⁸", match: true },
        { locus: "vWA", evid: "14, 17", ref: "14, 17", lr: "8.4×10⁷", match: true },
        { locus: "D16S539", evid: "9, 12", ref: "9, 12", lr: "3.1×10⁷", match: true },
        { locus: "CSF1PO", evid: "10, 11", ref: "10, 11", lr: "2.8×10⁷", match: true },
        { locus: "TPOX", evid: "8, 11", ref: "8, 11", lr: "5.2×10⁶", match: true },
        { locus: "D8S1179", evid: "13, 14", ref: "13, 14", lr: "4.9×10⁷", match: true },
        { locus: "D21S11", evid: "29, 31", ref: "29, 31", lr: "9.1×10⁶", match: true },
        { locus: "D18S51", evid: "14, 18", ref: "14, 18", lr: "2.2×10⁷", match: true },
    ];
    return (
        <div className="space-y-5">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Combined LR", value: "10¹⁸·⁴", color: "text-emerald-400" },
                    { label: "CODIS Loci", value: "20 / 20", color: "text-cyan-400" },
                    { label: "Population", value: "European", color: "text-purple-400" },
                    { label: "Verbal Scale", value: "Conclusive", color: "text-amber-400" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className={`text-sm font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                ))}
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-black/40 overflow-hidden shadow-inner font-mono">
                <div className="grid grid-cols-5 items-center px-4 py-2.5 border-b border-tactical-border/50 text-[9px] font-bold text-zinc-400 uppercase tracking-wider bg-black/60">
                    <span className="truncate">Locus</span>
                    <span className="truncate">Evidence</span>
                    <span className="truncate">Reference</span>
                    <span className="truncate whitespace-nowrap text-emerald-400/90">LR Score</span>
                    <span className="text-right truncate">Status</span>
                </div>
                {loci.map((l, i) => (
                    <div key={i} className="grid grid-cols-5 items-center px-4 py-2 border-b border-tactical-border/20 last:border-0 hover:bg-white/[0.03] transition-colors">
                        <span className="text-[10px] font-bold text-white truncate">{l.locus}</span>
                        <span className="text-[10px] text-zinc-300 truncate">{l.evid}</span>
                        <span className="text-[10px] text-zinc-300 truncate">{l.ref}</span>
                        <span className="text-[10px] text-emerald-400 font-bold truncate">{l.lr}</span>
                        <div className="flex justify-end">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        </div>
                    </div>
                ))}
            </div>
            <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5">
                <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-bold text-emerald-400 uppercase">SWGDAM Conclusion</span>
                </div>
                <p className="text-[10px] text-zinc-300 leading-relaxed">
                    Conclusive inclusion. The probability of a random match in the European population is 1 in 2.51 × 10¹⁸. 
                    This evidence is extremely strong support for the prosecution hypothesis (Hp). 
                    ENFSI verbal scale: <span className="text-emerald-400 font-bold">Conclusive Support for Identity</span>.
                </p>
            </div>
        </div>
    );
}

function PanelKinship() {
    return (
        <div className="space-y-5">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Relationship", value: "Parent/Child", color: "text-emerald-400" },
                    { label: "Kinship Coeff (κ)", value: "0.4897", color: "text-cyan-400" },
                    { label: "IBD Probability", value: "0.9812", color: "text-purple-400" },
                    { label: "LR Kinship", value: "10⁸·²", color: "text-amber-400" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className={`text-sm font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                ))}
            </div>
            <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl border border-tactical-border/50 bg-black/30 space-y-2">
                    <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Profile A — Evidence</p>
                    {["D3S1358: 15,17", "vWA: 14,17", "D16S539: 9,12", "CSF1PO: 10,11"].map((l) => (
                        <p key={l} className="text-[10px] font-mono text-zinc-300">{l}</p>
                    ))}
                </div>
                <div className="p-4 rounded-xl border border-tactical-border/50 bg-black/30 space-y-2">
                    <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Profile B — Reference</p>
                    {["D3S1358: 15,16", "vWA: 14,14", "D16S539: 9,13", "CSF1PO: 10,12"].map((l) => (
                        <p key={l} className="text-[10px] font-mono text-zinc-300">{l}</p>
                    ))}
                </div>
            </div>
            <div className="p-4 rounded-xl border border-cyan-500/30 bg-cyan-500/5">
                <p className="text-[10px] text-zinc-300 leading-relaxed">
                    Kinship coefficient κ = 0.4897 is consistent with a first-degree biological relationship (parent-child: expected κ = 0.5). 
                    IBD segments: 48.97% of genome shared identical-by-descent.
                    <span className="text-cyan-400 font-bold"> Familial match confirmed.</span>
                </p>
            </div>
        </div>
    );
}

function PanelMCMC() {
    const [contributors, setContributors] = useState(2);
    const [iterations, setIterations] = useState(50000);
    return (
        <div className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="text-[9px] text-zinc-500 uppercase font-bold block mb-1">Number of Contributors</label>
                    <input type="range" min={1} max={5} value={contributors}
                        onChange={(e) => setContributors(+e.target.value)}
                        className="w-full accent-cyan-400" />
                    <div className="flex justify-between text-[9px] text-zinc-600 mt-1">
                        <span>1</span><span className="text-cyan-400 font-bold">{contributors}</span><span>5</span>
                    </div>
                </div>
                <div>
                    <label className="text-[9px] text-zinc-500 uppercase font-bold block mb-1">MCMC Iterations</label>
                    <input type="range" min={10000} max={100000} step={10000} value={iterations}
                        onChange={(e) => setIterations(+e.target.value)}
                        className="w-full accent-cyan-400" />
                    <div className="flex justify-between text-[9px] text-zinc-600 mt-1">
                        <span>10k</span><span className="text-cyan-400 font-bold">{(iterations / 1000).toFixed(0)}k</span><span>100k</span>
                    </div>
                </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Mixture Ratio", value: contributors === 1 ? "100%" : contributors === 2 ? "70:30" : "60:25:15", color: "text-cyan-400" },
                    { label: "Deconv. LR (A)", value: contributors === 1 ? "10¹⁸·⁴" : "10⁶·²", color: "text-emerald-400" },
                    { label: "Burn-in Steps", value: `${Math.round(iterations * 0.1 / 1000)}k`, color: "text-purple-400" },
                    { label: "Convergence", value: "PASS (R̂<1.01)", color: "text-amber-400" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className={`text-xs font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                ))}
            </div>
            <div className="p-4 rounded-xl border border-cyan-500/30 bg-black/20 space-y-2">
                <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">MCMC Trace Summary</p>
                <div className="space-y-1">
                    {Array.from({ length: contributors }, (_, i) => (
                        <div key={i} className="flex items-center gap-3">
                            <span className="text-[10px] text-zinc-400 w-20 shrink-0">Contributor {String.fromCharCode(65 + i)}</span>
                            <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-cyan-500 to-cyan-400 rounded-full"
                                    style={{ width: `${i === 0 ? 70 : i === 1 ? 30 : 15}%` }}
                                />
                            </div>
                            <span className="text-[10px] text-cyan-400 font-mono w-12 text-right">
                                {i === 0 ? "70%" : i === 1 ? "30%" : "15%"}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function PanelHIrisPlex() {
    const [snpCount] = useState(41);
    const phenotypes = [
        { trait: "Eye Color", prediction: "Blue", confidence: 92.1, color: "text-blue-400" },
        { trait: "Hair Color", prediction: "Brown", confidence: 87.4, color: "text-amber-400" },
        { trait: "Skin Tone", prediction: "Fair (I-II)", confidence: 89.3, color: "text-orange-400" },
        { trait: "Freckling", prediction: "None / Minimal", confidence: 76.2, color: "text-pink-400" },
    ];
    return (
        <div className="space-y-5">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "SNPs Analyzed", value: `${snpCount}/41`, color: "text-purple-400" },
                    { label: "Model", value: "HIrisPlex-S", color: "text-emerald-400" },
                    { label: "Population", value: "European", color: "text-cyan-400" },
                    { label: "Quality Pass", value: "PASS", color: "text-amber-400" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className={`text-sm font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                ))}
            </div>
            <div className="space-y-3">
                {phenotypes.map((p) => (
                    <div key={p.trait} className="p-4 rounded-xl border border-tactical-border/50 bg-black/30">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-bold text-zinc-300 uppercase tracking-wider">{p.trait}</span>
                            <span className={`text-sm font-bold ${p.color}`}>{p.prediction}</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full rounded-full bg-gradient-to-r ${p.color.replace("text-", "from-").replace("-400", "-600")} to-${p.color.replace("text-", "").replace("-400", "-400")}`}
                                    style={{ width: `${p.confidence}%` }}
                                />
                            </div>
                            <span className={`text-[10px] font-bold ${p.color} w-12 text-right`}>{p.confidence}%</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function PanelTouchDNA() {
    const [mass, setMass] = useState(80);
    const [substrate, setSubstrate] = useState("TEXTURED");
    const eff = substrate === "SMOOTH" ? 0.6 : substrate === "TEXTURED" ? 0.4 : 0.2;
    const recMass = Math.round(mass * eff * 10) / 10;
    const dropoutPd = Math.round(Math.exp(-0.05 * recMass) * 10000) / 100;
    const isLT = recMass < 150;
    return (
        <div className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="text-[9px] text-zinc-500 uppercase font-bold block mb-1.5">Input DNA Mass (pg)</label>
                    <input type="range" min={10} max={500} value={mass} onChange={(e) => setMass(+e.target.value)} className="w-full accent-orange-400" />
                    <div className="flex justify-between text-[9px] text-zinc-600 mt-1"><span>10 pg</span><span className="text-orange-400 font-bold">{mass} pg</span><span>500 pg</span></div>
                </div>
                <div>
                    <label className="text-[9px] text-zinc-500 uppercase font-bold block mb-1.5">Substrate</label>
                    <select value={substrate} onChange={(e) => setSubstrate(e.target.value)} className="w-full bg-black/40 border border-tactical-border/60 rounded-lg p-2 text-[10px] font-mono text-orange-300 font-bold">
                        <option value="SMOOTH">Smooth Metal (60%)</option>
                        <option value="TEXTURED">Textured / Gun Grip (40%)</option>
                        <option value="POROUS">Porous / Fabric (20%)</option>
                    </select>
                </div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Recovered Mass", value: `${recMass} pg`, color: "text-orange-400" },
                    { label: "Dropout P(D)", value: `${dropoutPd}%`, color: isLT ? "text-red-400" : "text-emerald-400" },
                    { label: "Classification", value: isLT ? "LtDNA" : "Standard", color: isLT ? "text-amber-400" : "text-emerald-400" },
                    { label: "Log10(LR)", value: isLT ? "+4.2" : "+6.8", color: "text-cyan-400" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className={`text-sm font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                ))}
            </div>
            {isLT && (
                <div className="p-3 rounded-xl border border-amber-500/30 bg-amber-500/5 flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <p className="text-[10px] text-zinc-300">Low-template classification triggered ({"<"}150 pg). Stochastic effects probable. MCMC deconvolution recommended. Replicate interpretation required per SWGDAM guidelines.</p>
                </div>
            )}
        </div>
    );
}

function PanelToxicology() {
    const [conc, setConc] = useState(0.85);
    const status = conc > 2.0 ? "FATAL" : conc > 0.5 ? "TOXIC / ELEVATED" : "THERAPEUTIC";
    const statusColor = conc > 2.0 ? "text-red-400" : conc > 0.5 ? "text-amber-400" : "text-emerald-400";
    return (
        <div className="space-y-5">
            <div>
                <label className="text-[9px] text-zinc-500 uppercase font-bold block mb-1.5">Morphine Blood Concentration (mg/L)</label>
                <input type="range" min={0} max={5} step={0.05} value={conc} onChange={(e) => setConc(+e.target.value)} className="w-full accent-rose-400" />
                <div className="flex justify-between text-[9px] text-zinc-600 mt-1"><span>0</span><span className={`font-bold ${statusColor}`}>{conc.toFixed(2)} mg/L</span><span>5.0</span></div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Classification", value: status, color: statusColor },
                    { label: "Uncertainty U95", value: "±0.09 mg/L", color: "text-zinc-300" },
                    { label: "Widmark Threshold", value: ">0.5 mg/L", color: "text-rose-400" },
                    { label: "PMR Effect", value: conc > 1 ? "+15% cardiac" : "N/A", color: "text-orange-400" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className={`text-sm font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                ))}
            </div>
            <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/5">
                <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider mb-2">ISO 17025 Measurement Uncertainty</p>
                <p className="text-[10px] text-zinc-300 leading-relaxed">
                    Reported value: {conc.toFixed(2)} mg/L ± 0.09 mg/L (k=2, 95% CL). 
                    Classification: <span className={`font-bold ${statusColor}`}>{status}</span>. 
                    Post-mortem redistribution coefficient applied (cardiac:peripheral ratio 1.15:1).
                </p>
            </div>
        </div>
    );
}

function PanelLIMS() {
    const items = [
        { id: "EVID-2026-901", type: "Bloodstain Swab", location: "Crime Scene A", custodian: "Det. Morrison", status: "IN ANALYSIS", color: "amber" },
        { id: "EVID-2026-902", type: "Buccal Reference", location: "Intake Lab", custodian: "Lab Tech B", status: "COMPLETE", color: "emerald" },
        { id: "EVID-2026-903", type: "Hair Sample", location: "Storage Bay 3", custodian: "Lab Tech C", status: "PENDING", color: "blue" },
        { id: "EVID-2026-904", type: "Touch DNA Swab", location: "Crime Scene B", custodian: "Det. Morrison", status: "QC REVIEW", color: "purple" },
    ];
    return (
        <div className="space-y-5">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Active Batches", value: "4", color: "text-blue-400" },
                    { label: "QC Pass Rate", value: "97.2%", color: "text-emerald-400" },
                    { label: "Pending Review", value: "1", color: "text-amber-400" },
                    { label: "HMAC Verified", value: "4 / 4", color: "text-cyan-400" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className={`text-sm font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                ))}
            </div>
            <div className="rounded-xl border border-tactical-border/50 bg-black/20 overflow-hidden">
                <div className="grid grid-cols-5 px-4 py-2 border-b border-tactical-border/40 text-[8px] font-bold text-zinc-600 uppercase">
                    <span>Evidence ID</span><span>Type</span><span>Location</span><span>Custodian</span><span className="text-right">Status</span>
                </div>
                {items.map((item, i) => {
                    const c: Record<string, string> = { emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20", amber: "text-amber-400 bg-amber-500/10 border-amber-500/20", blue: "text-blue-400 bg-blue-500/10 border-blue-500/20", purple: "text-purple-400 bg-purple-500/10 border-purple-500/20" };
                    return (
                        <div key={i} className="grid grid-cols-5 items-center px-4 py-2 border-b border-tactical-border/20 last:border-0 hover:bg-white/2 transition-colors">
                            <span className="text-[10px] font-bold text-white font-mono">{item.id}</span>
                            <span className="text-[10px] text-zinc-400">{item.type}</span>
                            <span className="text-[10px] text-zinc-500">{item.location}</span>
                            <span className="text-[10px] text-zinc-500">{item.custodian}</span>
                            <div className="flex justify-end"><span className={`text-[8px] font-bold border rounded px-1.5 py-0.5 ${c[item.color]}`}>{item.status}</span></div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function PanelSyntheticCase() {
    const [generated, setGenerated] = useState(false);
    const [loading, setLoading] = useState(false);
    const generate = () => {
        setLoading(true);
        setTimeout(() => { setLoading(false); setGenerated(true); }, 1500);
    };
    return (
        <div className="space-y-5">
            <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/5">
                <p className="text-xs font-bold text-rose-400 mb-1">Synthetic Forensic Case Generator</p>
                <p className="text-[10px] text-zinc-400 leading-relaxed">
                    Generates fully synthetic forensic cases with DNA profiles, mixture proportions, ground truth data, 
                    and benchmark evaluation metrics. Used for FORENZA academic validation and LR engine testing.
                </p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                    { label: "Contributors", value: "1–5" },
                    { label: "Loci", value: "CODIS 20" },
                    { label: "Relatives", value: "Parent/Child" },
                    { label: "Dropout Sim.", value: "Yes" },
                    { label: "Stutter Sim.", value: "Yes" },
                    { label: "Ground Truth", value: "Included" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className="text-xs font-bold text-rose-400 font-mono">{m.value}</p>
                    </div>
                ))}
            </div>
            <button
                onClick={generate}
                disabled={loading}
                className="w-full py-3 rounded-xl border border-rose-500/40 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 font-bold text-xs font-mono uppercase tracking-widest transition-all flex items-center justify-center gap-2"
            >
                {loading ? <><Sparkles className="w-4 h-4 animate-spin" />Generating Case...</> : <><Sparkles className="w-4 h-4" />Generate Synthetic Case</>}
            </button>
            {generated && (
                <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
                    <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5">
                        <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider mb-2">Generated Case — SYNTH-2026-001</p>
                        <div className="grid grid-cols-2 gap-2 text-[10px]">
                            {[
                                ["Contributors", "3 (A: 60%, B: 30%, C: 10%)"],
                                ["True LR (Contributor A)", "Log10(LR) = +8.41"],
                                ["FORENZA LR Estimate", "Log10(LR) = +8.39"],
                                ["RMSE Error", "0.02 (Excellent)"],
                                ["Dropout Events", "2 at D13S317"],
                                ["Ground Truth Hash", "a7f9c2e…"],
                            ].map(([k, v]) => (
                                <div key={k}>
                                    <span className="text-zinc-500 block">{k}</span>
                                    <span className="text-emerald-300 font-bold font-mono">{v}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    );
}

function PanelGenericPlaceholder({ tab, category }: { tab: Tab; category: Category }) {
    const c = COLOR_CLASSES[category.color];
    const Icon = tab.icon;
    return (
        <div className="space-y-5">
            <div className={`p-6 rounded-xl border ${c.border} ${c.bg} flex flex-col items-center justify-center gap-4 text-center`}>
                <Icon className={`w-8 h-8 ${c.text}`} />
                <div>
                    <p className={`text-sm font-bold ${c.text} mb-1`}>{tab.label}</p>
                    <p className="text-[10px] text-zinc-500 max-w-sm leading-relaxed">
                        This module provides {tab.label} capabilities as part of the FORENZA Evidence OS. 
                        Live demo data is loaded automatically when the FORENZA backend is active.
                    </p>
                </div>
                <div className="grid grid-cols-2 gap-3 w-full max-w-xs">
                    <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/40">
                        <p className="text-[9px] text-zinc-600 uppercase mb-1">Module Status</p>
                        <p className="text-xs font-bold text-emerald-400">OPERATIONAL</p>
                    </div>
                    <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/40">
                        <p className="text-[9px] text-zinc-600 uppercase mb-1">ISO 17025 Status</p>
                        <p className="text-xs font-bold text-cyan-400">VERIFIED</p>
                    </div>
                </div>
            </div>
            <div className="p-4 rounded-xl border border-tactical-border/40 bg-black/20 space-y-2">
                <p className="text-[9px] text-zinc-600 uppercase font-bold tracking-wider">Live metrics stream</p>
                {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center gap-3">
                        <div className={`w-1.5 h-1.5 rounded-full ${c.text.replace("text-", "bg-")} animate-pulse`} style={{ animationDelay: `${i * 200}ms` }} />
                        <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                            <div className={`h-full ${c.text.replace("text-", "bg-")} rounded-full`} style={{ width: `${Math.round(60 + i * 10)}%`, opacity: 0.7 }} />
                        </div>
                        <span className="text-[9px] text-zinc-600">{Math.round(60 + i * 10)}%</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ─── Panel Router ──────────────────────────────────────────────────────────

function renderPanel(tabId: TabId, category: Category) {
    const tab = category.tabs.find((t) => t.id === tabId) ?? category.tabs[0];
    switch (tabId) {
        case "str": return <PanelSTR />;
        case "kinship": return <PanelKinship />;
        case "mcmc": return <PanelMCMC />;
        case "hirisplex": return <PanelHIrisPlex />;
        case "touch": return <PanelTouchDNA />;
        case "toxicology": return <PanelToxicology />;
        case "lims": return <PanelLIMS />;
        case "synthetic": return <PanelSyntheticCase />;
        default: return <PanelGenericPlaceholder tab={tab} category={category} />;
    }
}

// ─── Main Component ────────────────────────────────────────────────────────

export default function AnalysisPage() {
    const [activeCategory, setActiveCategory] = useState<CategoryId>("dna");
    const [activeTab, setActiveTab] = useState<TabId>("str");

    const category = CATEGORIES.find((c) => c.id === activeCategory) ?? CATEGORIES[0];
    const c = COLOR_CLASSES[category.color];
    const CatIcon = category.icon;

    const handleCategoryClick = (catId: CategoryId) => {
        const cat = CATEGORIES.find((c) => c.id === catId);
        if (cat) {
            setActiveCategory(catId);
            setActiveTab(cat.tabs[0].id);
        }
    };

    return (
        <div className="flex flex-col gap-5 font-mono max-w-full overflow-hidden">
            {/* ── Page Header ── */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/60 pb-3">
                <div>
                    <div className="flex items-center gap-2 mb-0.5">
                        <FlaskConical className="w-4 h-4 text-cyan-400" />
                        <h1 className="text-sm sm:text-base font-extrabold text-white tracking-tight uppercase">
                            FORENZA Analysis Hub
                        </h1>
                        <span className="text-[9px] font-bold border border-cyan-500/30 rounded px-2 py-0.5 text-cyan-400 bg-cyan-500/10">
                            30 Modules • 6 Categories
                        </span>
                    </div>
                    <p className="text-[10px] text-zinc-400">
                        Comprehensive Biocomputational Intelligence &amp; Forensic DNA Workstation
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="flex items-center gap-1.5 text-[9px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-lg">
                        <Radio className="w-3 h-3 animate-pulse" />
                        LIVE • CASE-2026-FORENZA
                    </span>
                </div>
            </div>

            {/* ── Live AI Control Banner ── */}
            <ModuleAiBanner moduleName="FORENZA Multi-Omic Analysis Workstation" moduleType="full_multiomic" />

            {/* ── Active Case DNA Profile & GIS Map Banner ── */}
            <ActiveProfileBanner />

            {/* ── Level 1: Category Selector Bar ── */}
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">
                        Step 1: Select Subsystem Category
                    </span>
                    <span className="text-[9px] text-zinc-500">6 Categories Available</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                    {CATEGORIES.map((cat) => {
                        const CIcon = cat.icon;
                        const cc = COLOR_CLASSES[cat.color];
                        const isActive = activeCategory === cat.id;
                        return (
                            <button
                                key={cat.id}
                                onClick={() => handleCategoryClick(cat.id)}
                                className={`flex items-center gap-2 p-2.5 rounded-xl text-xs font-bold transition-all text-left cursor-pointer border ${
                                    isActive
                                        ? `${cc.activeBg} border ${cc.border} ${cc.text} shadow-[0_0_15px_rgba(6,182,212,0.15)]`
                                        : "bg-tactical-surface/80 text-zinc-400 border-tactical-border/70 hover:border-zinc-700 hover:text-zinc-200"
                                }`}
                            >
                                <CIcon className={`w-4 h-4 shrink-0 ${isActive ? cc.text : "text-zinc-500"}`} />
                                <span className="truncate text-[10px] uppercase tracking-wider">{cat.label}</span>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* ── Level 2: Selected Category Workspace & Sub-Module Nav ── */}
            <div className="rounded-2xl border border-tactical-border/80 bg-[#070D18] p-4 sm:p-6 space-y-4 shadow-xl">
                {/* Category Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/60 pb-3">
                    <div className="flex items-center gap-2.5 min-w-0">
                        <div className={`p-2 rounded-xl border ${c.border} ${c.bg} shrink-0`}>
                            <CatIcon className={`w-4 h-4 ${c.text}`} />
                        </div>
                        <div className="min-w-0">
                            <h2 className={`text-xs sm:text-sm font-bold ${c.text} uppercase tracking-wider`}>
                                {category.label}
                            </h2>
                            <p className="text-[10px] text-zinc-400">
                                {category.tabs.length} Specialized Sub-Modules • ISO/IEC 17025 Compliant
                            </p>
                        </div>
                    </div>

                    <span className="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-lg shrink-0 w-fit">
                        ALL MODULES OPERATIONAL
                    </span>
                </div>

                {/* Sub-Module Tabs Bar (Responsive Grid on Mobile, Flex on Desktop) */}
                <div className="grid grid-cols-1 min-[420px]:grid-cols-2 md:flex md:flex-wrap items-center gap-1.5 pb-1">
                    {category.tabs.map((tab) => {
                        const TabIcon = tab.icon;
                        const isActive = activeTab === tab.id;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center justify-between sm:justify-start gap-1.5 px-3 py-2 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer ${
                                    isActive
                                        ? `${c.activeBg} border ${c.border} ${c.text} shadow-sm`
                                        : "bg-black/40 text-zinc-400 border border-tactical-border/50 hover:text-zinc-200 hover:border-zinc-700"
                                }`}
                            >
                                <div className="flex items-center gap-1.5 min-w-0">
                                    <TabIcon className="w-3.5 h-3.5 shrink-0" />
                                    <span className="truncate">{tab.label}</span>
                                </div>
                                {tab.badge && (
                                    <span className="px-1.5 py-0.5 rounded text-[8px] bg-amber-500/20 text-amber-300 border border-amber-500/30 shrink-0">
                                        {tab.badge}
                                    </span>
                                )}
                            </button>
                        );
                    })}
                </div>

                {/* Panel Content */}
                <AnimatePresence mode="wait">
                    <motion.div
                        key={`${activeCategory}-${activeTab}`}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -6 }}
                        transition={{ duration: 0.18 }}
                        className="pt-2"
                    >
                        {renderPanel(activeTab, category)}
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
}
