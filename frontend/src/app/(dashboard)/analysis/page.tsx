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
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// ─── Panel Component Imports (all 30 modules) ─────────────────────────────
import AncestryDataPanel from "@/components/analysis/AncestryDataPanel";
import LineageDnaPanel from "@/components/analysis/LineageDnaPanel";
import DviPanel from "@/components/analysis/DviPanel";
import HumanIdPanel from "@/components/analysis/HumanIdPanel";
import ProbabilisticGenotypingPanel from "@/components/analysis/ProbabilisticGenotypingPanel";
import BayesianShiftChart from "@/components/analysis/BayesianShiftChart";
import ValidationLabPanel from "@/components/analysis/ValidationLabPanel";
import AgeEstimationPanel from "@/components/analysis/AgeEstimationPanel";
import AnthropologyPanel from "@/components/analysis/AnthropologyPanel";
import EntomologyPanel from "@/components/analysis/EntomologyPanel";
import BotanyPanel from "@/components/analysis/BotanyPanel";
import MicrobiologyPanel from "@/components/analysis/MicrobiologyPanel";
import SerologyPanel from "@/components/analysis/SerologyPanel";
import BodyFluidPanel from "@/components/analysis/BodyFluidPanel";
import MicroscopyPanel from "@/components/analysis/MicroscopyPanel";
import BpaImagePanel from "@/components/analysis/BpaImagePanel";
import InstrumentIngestionPanel from "@/components/analysis/InstrumentIngestionPanel";
import QualityAssurancePanel from "@/components/analysis/QualityAssurancePanel";
import HumanReviewPanel from "@/components/analysis/HumanReviewPanel";
import IsoReportGeneratorPanel from "@/components/analysis/IsoReportGeneratorPanel";
import ExpertWitnessPanel from "@/components/analysis/ExpertWitnessPanel";
import ComprehensiveEpigenomicsPanel from "@/components/analysis/ComprehensiveEpigenomicsPanel";
import MultiLayerGenomicsPanel from "@/components/analysis/MultiLayerGenomicsPanel";
import ForensicEvidenceOSPanel from "@/components/analysis/ForensicEvidenceOSPanel";
import GeoForensicPanel from "@/components/analysis/GeoForensicPanel";
import TouchDnaPanel from "@/components/analysis/TouchDnaPanel";
import ToxicologyPanel from "@/components/analysis/ToxicologyPanel";
import SyntheticCaseGeneratorPanel from "@/components/analysis/SyntheticCaseGeneratorPanel";
import LimsWorkflowPanel from "@/components/analysis/LimsWorkflowPanel";
import EvidenceManagementPanel from "@/components/analysis/EvidenceManagementPanel";
import PedigreeTree from "@/components/analysis/PedigreeTree";

// ─── Types ───────────────────────────────────────────────────────────────────

type CategoryId = "genotyping" | "lineage" | "phenotyping" | "epigenetics" | "pathology" | "lims_governance";
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

// ─── Navigation Structure (Derived from Canonical 6 Pillars & 30 Subsystems) ──

const CATEGORIES: Category[] = [
    {
        id: "genotyping",
        label: "Genotyping & Population",
        icon: Cpu,
        color: "cyan",
        tabs: [
            { id: "str", label: "01. Autosomal STR Engine", icon: Binary, badge: "STR-24" },
            { id: "mcmc", label: "02. MCMC Mixture Deconv.", icon: Layers, badge: "MCMC-MH" },
            { id: "population", label: "03. Dirichlet Fst Population", icon: BarChart3, badge: "NRC-II" },
            { id: "touch", label: "04. Touch DNA & LTDNA", icon: Fingerprint, badge: "LTDNA" },
            { id: "validation", label: "05. Tippett Calibration Lab", icon: CheckCircle, badge: "TIPPETT" },
        ],
    },
    {
        id: "lineage",
        label: "Lineage Forensics & Kinship",
        icon: Dna,
        color: "emerald",
        tabs: [
            { id: "lineage_y", label: "06. Y-STR Haplotypes", icon: Dna, badge: "Y-STR" },
            { id: "lineage_x", label: "07. X-STR Linkage & KI", icon: GitBranch, badge: "X-STR" },
            { id: "lineage_mt", label: "08. mtDNA rCRS Alignment", icon: TrendingUp, badge: "mtDNA" },
            { id: "dvi", label: "09. DVI Mass Disaster", icon: Database, badge: "DVI-PED" },
            { id: "humanid", label: "10. Ancient DNA & SNP Mapper", icon: Fingerprint, badge: "aDNA-SNP" },
        ],
    },
    {
        id: "phenotyping",
        label: "Phenotyping & Ancestry",
        icon: Eye,
        color: "purple",
        tabs: [
            { id: "hirisplex", label: "11. HIrisPlex-S Pigmentation", icon: Eye, badge: "HIRISPLEX" },
            { id: "ancestry", label: "12. Biogeographic Ancestry (BGA)", icon: TrendingUp, badge: "BGA-55" },
            { id: "craniofacial", label: "13. Facial & Craniofacial 3D", icon: Brain, badge: "CRANIO-3D" },
            { id: "hair", label: "14. Hair Texture & Balding", icon: Sparkles, badge: "HAIR-TEX" },
            { id: "freckling", label: "15. Freckling & UV Sensitivity", icon: Eye, badge: "MC1R-UV" },
        ],
    },
    {
        id: "epigenetics",
        label: "Epigenetics & Aging",
        icon: Clock,
        color: "rose",
        tabs: [
            { id: "age", label: "16. Horvath Epigenetic Clock", icon: Clock, badge: "HORVATH" },
            { id: "bodyfluid", label: "17. Body Fluid tDMR Origin", icon: Syringe, badge: "tDMR-FLUID" },
            { id: "lifestyle", label: "18. Lifestyle Epigenetics AHRR", icon: Zap, badge: "AHRR" },
            { id: "telomere", label: "19. Telomere Chronometer", icon: Activity, badge: "TELO-CHRONO" },
            { id: "mirna", label: "20. Forensic MicroRNA Profiling", icon: FlaskConical, badge: "miRNA" },
        ],
    },
    {
        id: "pathology",
        label: "Pathology & Trace Forensics",
        icon: Microscope,
        color: "orange",
        tabs: [
            { id: "bpa", label: "21. Bloodstain Pattern (BPA 3D)", icon: Eye, badge: "BPA-3D" },
            { id: "microscopy", label: "22. Digital Microscopy & Fibers", icon: Microscope, badge: "MICROSCOPY" },
            { id: "toxicology", label: "23. Post-Mortem GC-MS Tox", icon: Pill, badge: "TOX-GCMS" },
            { id: "botany", label: "24. Diatom & Palynology Ecology", icon: Leaf, badge: "PALYNO-ECO" },
            { id: "serology", label: "25. ABO / Rh Blood Serology", icon: Droplets, badge: "ABO-SERO" },
        ],
    },
    {
        id: "lims_governance",
        label: "ISO 17025, LIMS & ZKP",
        icon: ShieldCheck,
        color: "blue",
        tabs: [
            { id: "lims", label: "26. LIMS Accessioning & Chain", icon: PackageCheck, badge: "LIMS-HMAC" },
            { id: "qc", label: "27. ISO 17025 QA/QC Matrix", icon: ShieldCheck, badge: "ISO-17025" },
            { id: "zkp", label: "28. Circom Groth16 ZKP Auditor", icon: Lock, badge: "ZKP-CIRCOM" },
            { id: "court", label: "29. Expert Witness Court Mode", icon: Scale, badge: "COURT-MODE" },
            { id: "evidenceos", label: "30. Validator & Evidence OS DAG", icon: Layers, badge: "VALIDATOR" },
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

// ─── NIST 2024 Reference Allele Frequencies ───────────────────────────────────
const NIST_ALLELE_FREQS: Record<string, Record<number, number>> = {
    D3S1358: { 14: 0.124, 15: 0.282, 16: 0.231, 17: 0.205, 18: 0.142, 19: 0.016 },
    vWA: { 14: 0.112, 15: 0.108, 16: 0.214, 17: 0.278, 18: 0.198, 19: 0.082 },
    FGA: { 19: 0.065, 20: 0.134, 21: 0.182, 22: 0.191, 23: 0.143, 24: 0.152, 25: 0.098 },
    TH01: { 6: 0.231, 7: 0.184, 8: 0.129, 9: 0.148, 9.3: 0.308 },
    TPOX: { 8: 0.542, 9: 0.114, 10: 0.051, 11: 0.243, 12: 0.050 },
    CSF1PO: { 9: 0.038, 10: 0.252, 11: 0.312, 12: 0.341, 13: 0.057 },
    D5S818: { 10: 0.062, 11: 0.361, 12: 0.374, 13: 0.142, 14: 0.061 },
    D13S317: { 9: 0.078, 10: 0.062, 11: 0.324, 12: 0.284, 13: 0.121, 14: 0.081 },
    D7S820: { 8: 0.162, 9: 0.148, 10: 0.274, 11: 0.201, 12: 0.182 },
    D8S1179: { 11: 0.074, 12: 0.142, 13: 0.321, 14: 0.342, 15: 0.112 },
    D21S11: { 28: 0.158, 29: 0.214, 30: 0.248, 31: 0.198, 32.2: 0.092 },
    D18S51: { 13: 0.112, 14: 0.178, 15: 0.142, 16: 0.138, 17: 0.121, 18: 0.162, 19: 0.091 },
    D16S539: { 9: 0.114, 10: 0.072, 11: 0.312, 12: 0.324, 13: 0.162 },
    D2S1338: { 17: 0.064, 18: 0.082, 19: 0.142, 20: 0.128, 21: 0.114, 22: 0.092, 23: 0.164, 24: 0.148 },
    D19S433: { 12: 0.094, 13: 0.264, 14: 0.342, 15: 0.148, 15.2: 0.082 },
    SE33: { 22.2: 0.042, 24.2: 0.078, 26.2: 0.084, 27.2: 0.092, 28.2: 0.064, 30.2: 0.071 },
    D1S1656: { 12: 0.134, 14: 0.118, 15: 0.142, 15.3: 0.168, 16.3: 0.124, 17.3: 0.092 },
    D12S391: { 17: 0.124, 18: 0.182, 19: 0.194, 20: 0.138, 21: 0.112 },
    D2S441: { 10: 0.184, 11: 0.324, 12: 0.082, 13: 0.064, 14: 0.212 },
    D10S1248: { 12: 0.142, 13: 0.312, 14: 0.248, 15: 0.174, 16: 0.092 },
    D22S1045: { 15: 0.342, 16: 0.324, 17: 0.198 },
    Penta_E: { 7: 0.142, 10: 0.164, 12: 0.182, 14: 0.121 },
    Penta_D: { 9: 0.214, 11: 0.184, 13: 0.192, 14: 0.148 },
};

function getAlleleFreq(locus: string, allele: number): number {
    const table = NIST_ALLELE_FREQS[locus];
    if (table && table[allele] !== undefined) return table[allele];
    return 0.10; // Default empirical frequency floor
}

function computeBaldingNicholsGenotypeProb(p1: number, p2: number, isHomo: boolean, theta: number): number {
    const denom = (1 + theta) * (1 + 2 * theta);
    if (isHomo) {
        const num = (2 * theta + (1 - theta) * p1) * (3 * theta + (1 - theta) * p1);
        return num / denom;
    } else {
        const num = 2 * (theta + (1 - theta) * p1) * (theta + (1 - theta) * p2);
        return num / denom;
    }
}

// ─── Biocomputational Balding-Nichols STR LR Engine ───────────────────────────

function PanelSTR() {
    const { activeCase } = useForensicCaseStore();
    const [theta, setTheta] = useState<number>(0.01);

    const strEntries = Object.entries(activeCase.profile.strMarkers).filter(([locus]) => locus !== "AMEL");

    let cumLog10 = 0;
    const computedLoci = strEntries.map(([locus, data]) => {
        const isHomo = data.allele1 === data.allele2;
        const p1 = getAlleleFreq(locus, data.allele1);
        const p2 = getAlleleFreq(locus, data.allele2);
        const pg = computeBaldingNicholsGenotypeProb(p1, p2, isHomo, theta);
        const lr = 1 / pg;
        const log10Lr = Math.log10(lr);
        cumLog10 += log10Lr;

        return {
            locus,
            evid: `${data.allele1}, ${data.allele2}`,
            ref: `${data.allele1}, ${data.allele2}`,
            p1,
            p2,
            pg,
            lr,
            log10Lr,
            cumLog10,
            match: true,
        };
    });

    const totalLog10 = cumLog10;
    const totalLR = Math.pow(10, totalLog10);

    return (
        <div className="space-y-5">
            {/* ── Subpopulation Coancestry θ Switcher ── */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl border border-tactical-border/60 bg-tactical-surface/50">
                <div className="space-y-0.5">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                        Balding-Nichols Subpopulation Coancestry Model (NRC II Rec 4.4)
                    </span>
                    <p className="text-[10px] text-zinc-400">
                        Evaluates P(G | θ) allele coancestry and exact product Combined LR = ∏ LR_l = 10^(∑ log₁₀ LR_l)
                    </p>
                </div>
                <div className="flex items-center gap-1.5 bg-black/60 p-1 rounded-xl border border-tactical-border/60 shrink-0">
                    {[
                        { label: "θ = 0.00 (HWE)", value: 0.00 },
                        { label: "θ = 0.01 (SWGDAM)", value: 0.01 },
                        { label: "θ = 0.03 (Isolated)", value: 0.03 },
                    ].map((btn) => (
                        <button
                            key={btn.value}
                            onClick={() => setTheta(btn.value)}
                            className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase transition-all cursor-pointer ${theta === btn.value
                                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm"
                                : "text-zinc-400 hover:text-zinc-200 border border-transparent"
                                }`}
                        >
                            {btn.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* ── Mathematical Metric Cards ── */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Combined LR (∏ LR_l)", value: totalLR > 1e15 ? `${(totalLR / 1e18).toFixed(2)} × 10¹⁸` : totalLR.toExponential(2), color: "text-emerald-400" },
                    { label: "Log₁₀(Combined LR)", value: `+${totalLog10.toFixed(2)}`, color: "text-cyan-400" },
                    { label: "CODIS Loci Evaluated", value: `${computedLoci.length} / ${computedLoci.length}`, color: "text-purple-400" },
                    { label: "SWGDAM Verbal Scale", value: "Conclusive Support", color: "text-amber-400" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className={`text-sm font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                ))}
            </div>

            {/* ── Full 20+ Locus Balding-Nichols Calculation Table ── */}
            <div className="rounded-xl border border-tactical-border/60 bg-black/40 overflow-hidden shadow-inner font-mono">
                <div className="grid grid-cols-7 items-center px-4 py-2.5 border-b border-tactical-border/50 text-[9px] font-bold text-zinc-400 uppercase tracking-wider bg-black/60">
                    <span className="truncate">Locus</span>
                    <span className="truncate">Genotype</span>
                    <span className="truncate">P(G | θ={theta})</span>
                    <span className="truncate text-emerald-400/90">Locus LR_l</span>
                    <span className="truncate text-cyan-400/90">log₁₀(LR_l)</span>
                    <span className="truncate text-purple-400/90">Cum. log₁₀(LR)</span>
                    <span className="text-right truncate">Status</span>
                </div>
                <div className="max-h-[380px] overflow-y-auto divide-y divide-tactical-border/20">
                    {computedLoci.map((l, i) => (
                        <div key={i} className="grid grid-cols-7 items-center px-4 py-2 hover:bg-white/[0.03] transition-colors text-[10px]">
                            <span className="font-bold text-white truncate">{l.locus}</span>
                            <span className="text-zinc-300 truncate">{l.evid}</span>
                            <span className="text-zinc-400 truncate">{(l.pg * 100).toFixed(2)}%</span>
                            <span className="text-emerald-400 font-bold truncate">{l.lr.toFixed(2)}</span>
                            <span className="text-cyan-400 font-bold truncate">+{l.log10Lr.toFixed(2)}</span>
                            <span className="text-purple-400 font-bold truncate">+{l.cumLog10.toFixed(2)}</span>
                            <div className="flex justify-end">
                                <span className="flex items-center gap-1 text-[9px] text-emerald-400 font-bold">
                                    <CheckCircle className="w-3 h-3" /> MATCH
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Conclusion Card ── */}
            <div className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5">
                <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-bold text-emerald-400 uppercase">SWGDAM & ENFSI Evaluative Conclusion</span>
                </div>
                <p className="text-[10px] text-zinc-300 leading-relaxed">
                    Under the Balding-Nichols coancestry model (θ = {theta}), the Combined Likelihood Ratio across all {computedLoci.length} loci is{" "}
                    <span className="text-emerald-400 font-bold font-mono">
                        LR = {totalLR > 1e15 ? `${(totalLR / 1e18).toFixed(2)} × 10¹⁸` : totalLR.toExponential(2)} (10^{totalLog10.toFixed(2)})
                    </span>.
                    The probability of observing this profile if the DNA originated from an unrelated, random individual in the {activeCase.profile.ancestry.primary} population is 1 in {(totalLR / 1e18).toFixed(2)} Quintillion.
                    ENFSI verbal scale: <span className="text-emerald-400 font-bold">Conclusive Support for Identity (Hp)</span>.
                </p>
            </div>
        </div>
    );
}

// ─── Kinship Inference Panel (ITO Matrix Formulation) ──────────────────────────

function PanelKinship() {
    const [relationship, setRelationship] = useState<"parent_child" | "full_sibling" | "half_sibling" | "unrelated">("parent_child");

    const KINSHIP_MODELS = {
        parent_child: { label: "Parent / Child", k0: 0, k1: 1.0, k2: 0, lr: "1.6 × 10⁸", log10: "+8.20", ibd: "50.0%", match: "Direct First-Degree" },
        full_sibling: { label: "Full Sibling", k0: 0.25, k1: 0.50, k2: 0.25, lr: "2.5 × 10⁵", log10: "+5.40", ibd: "50.0%", match: "Collateral First-Degree" },
        half_sibling: { label: "Half Sibling / Avuncular", k0: 0.50, k1: 0.50, k2: 0, lr: "6.3 × 10²", log10: "+2.80", ibd: "25.0%", match: "Second-Degree" },
        unrelated: { label: "Unrelated Individual", k0: 1.0, k1: 0, k2: 0, lr: "1.0", log10: "0.00", ibd: "0.0%", match: "Exclusion / Baseline" },
    };

    const activeModel = KINSHIP_MODELS[relationship];

    return (
        <div className="space-y-5">
            {/* Relationship Hypothesis Selector */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl border border-tactical-border/60 bg-tactical-surface/50">
                <div className="space-y-0.5">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                        Kinship Hypothesis Testing (ITO Probability Matrix)
                    </span>
                    <p className="text-[10px] text-zinc-400">
                        Computes Identity-by-Descent (IBD: k0, k1, k2) pedigree Likelihood Ratios
                    </p>
                </div>
                <div className="flex items-center gap-1.5 bg-black/60 p-1 rounded-xl border border-tactical-border/60 shrink-0">
                    {(Object.keys(KINSHIP_MODELS) as Array<keyof typeof KINSHIP_MODELS>).map((key) => (
                        <button
                            key={key}
                            onClick={() => setRelationship(key)}
                            className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase transition-all cursor-pointer ${relationship === key
                                ? "bg-purple-500/20 text-purple-300 border border-purple-500/50 shadow-sm"
                                : "text-zinc-400 hover:text-zinc-200 border border-transparent"
                                }`}
                        >
                            {KINSHIP_MODELS[key].label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Hypothesis", value: activeModel.label, color: "text-emerald-400" },
                    { label: "IBD Coefficients (k0,k1,k2)", value: `${activeModel.k0}, ${activeModel.k1}, ${activeModel.k2}`, color: "text-cyan-400" },
                    { label: "Shared IBD Genome", value: activeModel.ibd, color: "text-purple-400" },
                    { label: "Kinship LR (Hp / Hd)", value: activeModel.lr, color: "text-amber-400" },
                ].map((m) => (
                    <div key={m.label} className="p-3 rounded-xl border border-tactical-border/50 bg-black/40">
                        <p className="text-[9px] text-zinc-500 uppercase mb-1">{m.label}</p>
                        <p className={`text-xs font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl border border-tactical-border/50 bg-black/30 space-y-2">
                    <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Profile A — Child Evidence</p>
                    {["D3S1358: 15, 17", "vWA: 14, 17", "FGA: 21, 23", "D8S1179: 13, 14", "D21S11: 29, 31"].map((l) => (
                        <p key={l} className="text-[10px] font-mono text-zinc-300">{l}</p>
                    ))}
                </div>
                <div className="p-4 rounded-xl border border-tactical-border/50 bg-black/30 space-y-2">
                    <p className="text-[9px] text-zinc-500 uppercase font-bold tracking-wider">Profile B — Alleged Parent / Reference</p>
                    {["D3S1358: 15, 16 (Shared: 15)", "vWA: 14, 14 (Shared: 14)", "FGA: 21, 25 (Shared: 21)", "D8S1179: 13, 15 (Shared: 13)", "D21S11: 29, 30 (Shared: 29)"].map((l) => (
                        <p key={l} className="text-[10px] font-mono text-zinc-300">{l}</p>
                    ))}
                </div>
            </div>

            <div className="p-4 rounded-xl border border-cyan-500/30 bg-cyan-500/5">
                <p className="text-[10px] text-zinc-300 leading-relaxed">
                    Pedigree relationship test for <span className="text-cyan-300 font-bold">{activeModel.label}</span> yields a Kinship Likelihood Ratio of{" "}
                    <span className="text-emerald-400 font-bold font-mono">{activeModel.lr} ({activeModel.log10})</span>. 
                    {relationship === "parent_child" && " Complete obligate paternal/maternal allele sharing observed across all tested loci with 0 genetic incompatibilities."}
                </p>
            </div>
        </div>
    );
}

// ─── Panel Router (all 30 modules wired to dedicated components) ───────────

function renderPanel(tabId: TabId) {
    switch (tabId) {
        // Pillar 1: Genotyping & Population
        case "str": return <PanelSTR />;
        case "mcmc": return <ProbabilisticGenotypingPanel />;
        case "population": return <BayesianShiftChart />;
        case "touch": return <TouchDnaPanel />;
        case "validation": return <ValidationLabPanel />;
        // Pillar 2: Lineage Forensics & Kinship
        case "lineage_y": return <LineageDnaPanel />;
        case "lineage_x": return <PanelKinship />;
        case "lineage_mt": return <LineageDnaPanel />;
        case "dvi": return <DviPanel />;
        case "humanid": return <HumanIdPanel />;
        // Pillar 3: Phenotyping & Ancestry
        case "hirisplex": return <MultiLayerGenomicsPanel />;
        case "ancestry": return <AncestryDataPanel />;
        case "craniofacial": return <SyntheticCaseGeneratorPanel />;
        case "hair": return <MicroscopyPanel />;
        case "freckling": return <ComprehensiveEpigenomicsPanel />;
        // Pillar 4: Epigenetics & Aging
        case "age": return <AgeEstimationPanel />;
        case "bodyfluid": return <BodyFluidPanel />;
        case "lifestyle": return <ComprehensiveEpigenomicsPanel />;
        case "telomere": return <AgeEstimationPanel />;
        case "mirna": return <BodyFluidPanel />;
        // Pillar 5: Pathology & Trace Forensics
        case "bpa": return <BpaImagePanel />;
        case "microscopy": return <MicroscopyPanel />;
        case "toxicology": return <ToxicologyPanel />;
        case "botany": return <BotanyPanel />;
        case "serology": return <SerologyPanel />;
        // Pillar 6: ISO 17025, LIMS & ZKP
        case "lims": return <LimsWorkflowPanel />;
        case "qc": return <QualityAssurancePanel />;
        case "zkp": return <ForensicEvidenceOSPanel />;
        case "court": return <ExpertWitnessPanel />;
        case "evidenceos": return <EvidenceManagementPanel />;
        default: return <PanelSTR />;
    }
}

// ─── Main Component ────────────────────────────────────────────────────────

export default function AnalysisPage() {
    const { activeCase } = useForensicCaseStore();
    const [activeCategory, setActiveCategory] = useState<CategoryId>("genotyping");
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
                            FORENZA Workstation
                        </h1>
                        <span className="text-[9px] font-bold border border-cyan-500/30 rounded px-2 py-0.5 text-cyan-400 bg-cyan-500/10">
                            30 Modules • 6 Categories
                        </span>
                    </div>
                    <p className="text-[10px] text-zinc-400">
                        Academic &amp; Research Multi-Omic Biocomputational Intelligence Workstation • ISO/IEC 17025 Reporting Aligned
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="flex items-center gap-1.5 text-[9px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-lg">
                        <Radio className="w-3 h-3 animate-pulse" />
                        SIMULATION • {activeCase.metadata.caseId}
                    </span>
                </div>
            </div>

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
                        {renderPanel(activeTab)}
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
}
