"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { 
    Binary, Dna, Activity, Bone, Bug, Leaf, Droplet, Pill, Syringe, 
    PackageCheck, Eye, Microscope, Fingerprint, Clock, Cpu, FileText, Scale, Sparkles, Layers, CheckCircle2, ShieldCheck, Zap
} from "lucide-react";

export default function LandingFeatures() {
    const { t } = useSaasLanguage();
    const [selectedPillar, setSelectedPillar] = useState<number>(0);

    const pillars = [
        {
            name: "Probabilistic Genotyping & Population",
            shortName: "Probabilistic & Population",
            icon: Binary,
            color: "cyan",
            accentBorder: "border-cyan-500/50",
            accentBg: "bg-cyan-500/10",
            accentText: "text-cyan-400",
            accentGlow: "shadow-cyan-500/20",
            badge: "CORE ENGINE",
            subsystems: [
                { id: "01", name: "Autosomal STR & Kinship Engine", badge: "CODIS-24", metrics: "24 Core Loci • LR Inclusion • Kinship Index", desc: "Calculates Likelihood Ratios for inclusion/exclusion across 24 core CODIS loci and evaluates parent-child / sibling kinship indices." },
                { id: "02", name: "MCMC Probabilistic Genotyping", badge: "MCMC-MH", metrics: "Metropolis-Hastings • 2-4 Contributors • Deconvolution", desc: "Metropolis-Hastings Markov Chain Monte Carlo deconvolution for 2-to-4 person complex DNA mixtures with stochastic parameters." },
                { id: "03", name: "Dirichlet Fst Population Genetics", badge: "NRC-II", metrics: "Balding-Nichols • Fst Correction • Dirichlet Smooth", desc: "Implements NRC II Recommendations 4.1 & 4.2 with subpopulation coancestry (Fst = 0.01 / 0.03) Dirichlet smoothing." },
                { id: "04", name: "Touch DNA & Low-Template LTDNA", badge: "LTDNA-MOD", metrics: "Dropout p_d • Drop-in p_i • Smooth Substrates", desc: "Models stochastic allele dropout (p_d) and drop-in (p_i) for low-mass template touch DNA recovered from smooth & porous evidence." },
                { id: "05", name: "Tippett Calibration Engine", badge: "TIPPETT", metrics: "H_p vs H_d • Non-Contributor LR • Calibration", desc: "Generates Tippett calibration curves plotting log10(LR) probability distributions under true contributor (H_p) vs non-contributor (H_d) hypotheses." }
            ]
        },
        {
            name: "Lineage Forensics & Kinship Inference",
            shortName: "Lineage & Kinship",
            icon: Dna,
            color: "purple",
            accentBorder: "border-purple-500/50",
            accentBg: "bg-purple-500/10",
            accentText: "text-purple-400",
            accentGlow: "shadow-purple-500/20",
            badge: "HAPLOTYPE",
            subsystems: [
                { id: "06", name: "Y-STR Haplotype Forensics", badge: "Y-STR", metrics: "Clopper-Pearson 95% CI • Y-HRD Database • Haplotype", desc: "Computes Clopper-Pearson 95% binomial confidence intervals for Y-chromosome STR haplotypes with Y-HRD database matching." },
                { id: "07", name: "X-STR Linkage & Kinship Index", badge: "X-STR", metrics: "Linkage Equilibrium • Female Kinship KI_X", desc: "Evaluates X-chromosomal linked marker cluster transmission probabilities and female kinship likelihood ratios (KI_X)." },
                { id: "08", name: "mtDNA Control Region Forensics", badge: "mtDNA", metrics: "rCRS Alignment • RSRS • Haplogroup Tree", desc: "Aligns hypervariable regions (HV1/HV2/HV3) against revised Cambridge Reference Sequence (rCRS) for maternal lineage assignment." },
                { id: "09", name: "DVI Mass Disaster Kinship Trees", badge: "DVI-TREES", metrics: "Mass Casualty • Pedigree Matching • Interpol Sec 4", desc: "Automated victim identification pedigree tree matching for mass disaster response compliant with Interpol DVI Section 4 standards." },
                { id: "10", name: "Lineage Haplotype Fusion", badge: "FUSION-YXM", metrics: "Joint LR_joint • Y+X+mtDNA • Lineage Product", desc: "Synthesizes multi-lineage joint likelihood ratios combining Y-STR, X-STR, and mtDNA haplogroup evidence." }
            ]
        },
        {
            name: "Phenotyping, Epigenetics & Multi-Layer Genomics",
            shortName: "Phenotype & Epigenetics",
            icon: Eye,
            color: "emerald",
            accentBorder: "border-emerald-500/50",
            accentBg: "bg-emerald-500/10",
            accentText: "text-emerald-400",
            accentGlow: "shadow-emerald-500/20",
            badge: "BIOMETRIC",
            subsystems: [
                { id: "11", name: "HIrisPlex-S Phenotype Prediction", badge: "HIRISPLEX-S", metrics: "Eye / Hair / Skin Tone • Freckles • SNP Dosage", desc: "Predicts externally visible characteristics (Eye color, Hair color & morphology, Skin tone, Freckling risk) via SNP dosage multinomial regression." },
                { id: "12", name: "Horvath 5-CpG Epigenetic Clock", badge: "EPIGEN-AGE", metrics: "DNA Methylation • Horvath Clock • U_95% Bounds", desc: "Estimates chronological age from 5 target CpG methylation loci with 95% expanded measurement uncertainty bounds." },
                { id: "13", name: "Tissue Specific tDMR Epigenetics", badge: "tDMR-BODY", metrics: "Tissue Methylation • Body Fluid Deconvolution", desc: "Deconvolutes tissue-specific differentially methylated regions (tDMR) to identify origin body fluid from genomic DNA." },
                { id: "14", name: "AHRR Smoking Epigenetic Biomarker", badge: "AHRR-MARK", metrics: "Environmental Exposure • Lifestyle CpG Profile", desc: "Quantifies AHRR gene cg05575921 methylation levels to assess environmental tobacco smoke exposure and lifestyle biomarkers." },
                { id: "15", name: "Multi-Layer Evidence Fusion", badge: "5-TIER-FUSION", metrics: "Joint Likelihood • STR+SNP+mt+Y+Epigenetics", desc: "Combines 5 evidence layers (Autosomal STR, SNP Phenotype, mtDNA, Y-STR, and Epigenetics) into a single unified joint likelihood ratio (LR_joint)." }
            ]
        },
        {
            name: "Forensic Biology, Serology & Pathology",
            shortName: "Biology & Pathology",
            icon: Syringe,
            color: "rose",
            accentBorder: "border-rose-500/50",
            accentBg: "bg-rose-500/10",
            accentText: "text-rose-400",
            accentGlow: "shadow-rose-500/20",
            badge: "SEROLOGY",
            subsystems: [
                { id: "16", name: "ABO/Rh Blood Group Serology", badge: "ABO-RH", metrics: "Antigen Antigenicity • Secretor Status • Fusion", desc: "Evaluates serological blood group antigen compatibility and integrates serology with DNA profile evidence." },
                { id: "17", name: "Lewis Non-Secretor Assay", badge: "LEWIS-FUT", metrics: "FUT2 / FUT3 Secretor • Glycan Antigens", desc: "Analyzes FUT2/FUT3 gene mutations determining Lewis antigen secretor status in saliva, blood, and body fluids." },
                { id: "18", name: "Forensic Pathology & PMI Clock", badge: "PMI-CLOCK", metrics: "Post-Mortem Interval • Algor / Rigor / Livor Mortis", desc: "Estimates Post-Mortem Interval (PMI) combining body temperature cooling curves (Henssge nomogram) and decomposition stages." },
                { id: "19", name: "Toxicology Widmark BAC Engine", badge: "TOX-WIDMARK", metrics: "Blood Alcohol Clearance • Cardiac Redistribution", desc: "Calculates blood alcohol clearance via Widmark kinetics and adjusts for Post-Mortem Redistribution (PMR) cardiac elevation." },
                { id: "20", name: "Bloodstain Pattern Analysis BPA", badge: "BPA-SPATTER", metrics: "Impact Angle alpha • Area of Origin • Flight Physics", desc: "Reconstructs blood spatter trajectory physics, calculating impact angle alpha = arcsin(W/L) and 3D convergence Area of Origin." }
            ]
        },
        {
            name: "LIMS Workflow, Instrument Gateway & QA/QC",
            shortName: "LIMS & QA/QC Gateway",
            icon: PackageCheck,
            color: "amber",
            accentBorder: "border-amber-500/50",
            accentBg: "bg-amber-500/10",
            accentText: "text-amber-400",
            accentGlow: "shadow-amber-500/20",
            badge: "LIMS-SOP",
            subsystems: [
                { id: "21", name: "LIMS-Lite Workflow SOP Chain", badge: "LIMS-9STEP", metrics: "9-Step Accessioning • Operator ID • Reagent Lot", desc: "Enforces 9-step SOP chain (Case -> Evidence -> Accession -> Extract -> Quant -> PCR -> CE -> Analysis -> Report) with operator & lot tracking." },
                { id: "22", name: "Automated Instrument Gateway", badge: "PARSER-GW", metrics: "CE GeneMapper • qPCR Quantifiler Trio • NGS MiSeq", desc: "Direct parser gateway ingesting capillary electrophoresis FSA/CSV tables, Quantifiler Trio Cq/DI metrics, and NGS VCF files." },
                { id: "23", name: "QA/QC Gatekeeper Engine", badge: "QAQC-GATE", metrics: "7-Point Quality Matrix • Hb Ratio • NC/PC Controls", desc: "Evaluates 7-point quality inspection matrix checking heterozygote balance (Hb >= 0.60), negative controls, and stochastic thresholds." },
                { id: "24", name: "Human Analyst Governance", badge: "DUAL-SIG", metrics: "Dual Sign-Off • Override Rationale • Audit HMAC", desc: "Mandates primary analyst & technical reviewer dual sign-off with mandatory rationale logging for any AI recommendation overrides." },
                { id: "25", name: "Concurrent Batch Processing Engine", badge: "BATCH-PROC", metrics: "Worker Semaphore • Multi-Sample Aggregator", desc: "High-throughput concurrent worker pool executing batch deconvolution and matrix processing across thousands of forensic samples." }
            ]
        },
        {
            name: "ISO Certificate & Expert Witness Court Mode",
            shortName: "ISO Certificate & Court",
            icon: Scale,
            color: "indigo",
            accentBorder: "border-indigo-500/50",
            accentBg: "bg-indigo-500/10",
            accentText: "text-indigo-400",
            accentGlow: "shadow-indigo-500/20",
            badge: "COURT-READY",
            subsystems: [
                { id: "26", name: "ISO 17025 Certificate Compiler", badge: "ISO-17025", metrics: "8-Section Formal Report • Immutability Invariant", desc: "Compiles official 8-section ISO/IEC 17025 forensic genetics examination certificates with cryptographic HMAC signing." },
                { id: "27", name: "Court / Expert Witness Mode", badge: "COURT-7POINT", metrics: "7-Point Testimony Framework • Brief Exporter", desc: "Transforms analytical data into a structured 7-Point Judicial Testimony Framework tailored for cross-examination and court brief export." },
                { id: "28", name: "Transposed Conditional Fallacy Shield", badge: "FALLACY-SHIELD", metrics: "Prosecutor's Fallacy Shield • LR != P(Hp|E)", desc: "Legal protection shield ensuring Likelihood Ratios P(E|Hp)/P(E|Hd) are never transposed into defendant guilt probabilities P(Hp|E)." },
                { id: "29", name: "Synthetic Case & Benchmark Harness", badge: "SYNTH-BENCH", metrics: "100% Ground Truth • ROC-AUC • RMSE log10LR", desc: "Generates synthetic 2-4 person mixtures with 100% ground truth to run automated self-testing benchmark evaluation (ROC-AUC & RMSE)." },
                { id: "30", name: "Master Forensic Evidence OS DAG", badge: "MASTER-DAG", metrics: "6-Layer Directed Acyclic Graph • 30 Subsystems", desc: "Unified master operating system orchestrator managing end-to-end directed graph execution across all 30 forensic subsystems." }
            ]
        }
    ];

    const currentPillar = pillars[selectedPillar];

    return (
        <section id="subsystems" className="py-20 lg:py-28 border-b border-tactical-border/60 bg-black/60 font-mono relative overflow-hidden">
            {/* Background Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-gradient-to-tr from-emerald-500/5 via-cyan-500/10 to-purple-600/5 blur-[150px] rounded-full pointer-events-none" />

            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-12 relative z-10">
                
                {/* Section Header */}
                <div className="text-center max-w-3xl mx-auto space-y-4">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-emerald-500/40 bg-emerald-500/10 text-emerald-300 text-xs font-bold uppercase tracking-wider shadow-lg shadow-emerald-500/10">
                        <Sparkles className="w-4 h-4 text-emerald-400 animate-pulse" />
                        <span>{t.subsystems.badge}</span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
                        {t.subsystems.title}
                    </h2>
                    <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed max-w-2xl mx-auto">
                        {t.subsystems.subtitle}
                    </p>
                </div>

                {/* Architectural Pillar Selector Buttons */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                    {pillars.map((pillar, idx) => {
                        const Icon = pillar.icon;
                        const isSelected = selectedPillar === idx;
                        return (
                            <button
                                key={idx}
                                onClick={() => setSelectedPillar(idx)}
                                className={`p-4 rounded-2xl border text-left transition-all duration-300 flex flex-col justify-between gap-3 cursor-pointer relative overflow-hidden group ${
                                    isSelected
                                        ? `${pillar.accentBorder} ${pillar.accentBg} ${pillar.accentGlow} shadow-xl scale-[1.02]`
                                        : "border-tactical-border/70 bg-tactical-surface/60 hover:bg-tactical-surface hover:border-zinc-700 text-zinc-400"
                                }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className={`p-2 rounded-xl border ${isSelected ? `${pillar.accentBorder} bg-black/40 ${pillar.accentText}` : "border-tactical-border/60 bg-black/40 text-zinc-400"}`}>
                                        <Icon className="w-4 h-4" />
                                    </div>
                                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${isSelected ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40" : "bg-black/40 text-zinc-500"}`}>
                                        0{idx + 1}
                                    </span>
                                </div>
                                <div>
                                    <span className={`text-xs font-bold uppercase tracking-wider block leading-snug ${isSelected ? "text-white" : "text-zinc-300 group-hover:text-white"}`}>
                                        {pillar.shortName}
                                    </span>
                                    <span className="text-[9px] text-zinc-500 block pt-1 font-bold">5 ENGINES</span>
                                </div>
                            </button>
                        );
                    })}
                </div>

                {/* Subsystem Matrix Cards Display */}
                <div className={`rounded-3xl border ${currentPillar.accentBorder} bg-tactical-surface/80 p-6 sm:p-8 shadow-2xl space-y-6 backdrop-blur-xl transition-all duration-300`}>
                    
                    {/* Matrix Sub-Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-5">
                        <div className="flex items-center gap-3">
                            <div className={`p-2.5 rounded-xl border ${currentPillar.accentBorder} ${currentPillar.accentBg} ${currentPillar.accentText}`}>
                                <currentPillar.icon className="w-5 h-5" />
                            </div>
                            <div>
                                <h3 className="text-sm sm:text-base font-extrabold uppercase tracking-wider text-white">
                                    {currentPillar.name}
                                </h3>
                                <p className="text-[10px] text-zinc-400 mt-0.5">
                                    Pillar 0{selectedPillar + 1} • 5 Active Biocomputational Subsystems
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="px-3 py-1 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                                5 / 5 OPERATIONAL
                            </span>
                        </div>
                    </div>

                    {/* 5 Subsystem Cards Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {currentPillar.subsystems.map((sub, sIdx) => (
                            <motion.div
                                key={sub.id}
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3, delay: sIdx * 0.06 }}
                                className="p-5 rounded-2xl border border-tactical-border/80 bg-black/60 hover:border-emerald-500/40 transition-all duration-300 space-y-3.5 group relative shadow-lg hover:shadow-emerald-500/5 flex flex-col justify-between"
                            >
                                <div className="space-y-2.5">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-emerald-500/20 font-mono text-[10px] font-bold text-emerald-400 border border-emerald-500/30">
                                                {sub.id}
                                            </span>
                                            <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-zinc-800 text-zinc-300 border border-zinc-700">
                                                {sub.badge}
                                            </span>
                                        </div>
                                        <span className="text-[9px] font-bold text-emerald-400 flex items-center gap-1">
                                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                                            ACTIVE
                                        </span>
                                    </div>

                                    <h4 className="font-mono text-sm font-bold text-zinc-100 group-hover:text-emerald-400 transition-colors leading-snug">
                                        {sub.name}
                                    </h4>

                                    <p className="font-mono text-[11px] text-zinc-400 leading-relaxed">
                                        {sub.desc}
                                    </p>
                                </div>

                                <div className="pt-3 border-t border-tactical-border/40 flex items-center justify-between text-[9px] font-bold text-zinc-500">
                                    <span className="truncate text-zinc-400">{sub.metrics}</span>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* Subsystem Matrix Telemetry Footer */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-5 rounded-2xl border border-tactical-border/80 bg-tactical-surface/40 text-center font-mono text-xs">
                    <div>
                        <span className="text-zinc-500 text-[10px] uppercase font-bold block">Total Subsystems</span>
                        <span className="font-black text-emerald-400 text-lg">30 / 30 Active</span>
                    </div>
                    <div>
                        <span className="text-zinc-500 text-[10px] uppercase font-bold block">Architectural Layers</span>
                        <span className="font-black text-cyan-400 text-lg">6-Layer DAG</span>
                    </div>
                    <div>
                        <span className="text-zinc-500 text-[10px] uppercase font-bold block">Pytest Invariants</span>
                        <span className="font-black text-purple-400 text-lg">215/215 Passed</span>
                    </div>
                    <div>
                        <span className="text-zinc-500 text-[10px] uppercase font-bold block">Standard Compliance</span>
                        <span className="font-black text-amber-400 text-lg">ISO/IEC 17025</span>
                    </div>
                </div>
            </div>
        </section>
    );
}
