"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { 
    Binary, Dna, Activity, Bone, Bug, Leaf, Droplet, Pill, Syringe, 
    PackageCheck, Eye, Microscope, Fingerprint, Clock, Cpu, FileText, Scale, Sparkles, Layers 
} from "lucide-react";

export default function LandingFeatures() {
    const [selectedPillar, setSelectedPillar] = useState<number>(0);

    const pillars = [
        {
            name: "Probabilistic Genotyping & Population",
            icon: Binary,
            color: "text-cyan-400 border-cyan-500/40 bg-cyan-500/10",
            subsystems: [
                { name: "Autosomal STR & Kinship Engine", desc: "CODIS 24 loci inclusion/exclusion LR calculation & kinship index." },
                { name: "MCMC Probabilistic Genotyping", desc: "Metropolis-Hastings MCMC 2-4 person mixture deconvolution." },
                { name: "Dirichlet Fst Population Genetics", desc: "NRC II Recommendation 4.1 & 4.2 subpopulation Fst correction." },
                { name: "Touch DNA & Low-Template LTDNA", desc: "Stochastic dropout (p_d) & drop-in (p_i) recovery model." },
                { name: "Tippett Calibration Engine", desc: "Log10 LR calibration under H_p vs H_d non-contributor distributions." }
            ]
        },
        {
            name: "Lineage Forensics & Kinship",
            icon: Dna,
            color: "text-purple-400 border-purple-500/40 bg-purple-500/10",
            subsystems: [
                { name: "Y-STR Haplotype Forensics", desc: "Clopper-Pearson 95% binomial confidence intervals & Y-HRD lookup." },
                { name: "X-STR Linkage & Kinship Index", desc: "Linked marker transmission probabilities & female kinship KIX." },
                { name: "mtDNA Control Region Forensics", desc: "rCRS / RSRS revised Cambridge reference alignment & haplogroups." },
                { name: "DVI Mass Disaster Kinship Trees", desc: "Automated victim identification pedigree tree matching." },
                { name: "Lineage Haplotype Fusion", desc: "Integrated Y/X/mtDNA joint likelihood ratio synthesis." }
            ]
        },
        {
            name: "Phenotyping, Epigenetics & Genomics",
            icon: Eye,
            color: "text-emerald-400 border-emerald-500/40 bg-emerald-500/10",
            subsystems: [
                { name: "HIrisPlex-S Phenotype Prediction", desc: "Extended Eye, Hair, Skin Tone & Freckling risk probability." },
                { name: "Horvath 5-CpG Epigenetic Clock", desc: "DNA methylation age prediction with U_95% uncertainty." },
                { name: "Tissue Specific tDMR Epigenetics", desc: "Body fluid tissue deconvolution via CpG methylation." },
                { name: "AHRR Smoking Epigenetic Biomarker", desc: "Environmental exposure & lifestyle methylation profile." },
                { name: "Multi-Layer Evidence Fusion", desc: "5-Tier joint evidence LR synthesis (STR+SNP+mt+Y+Epigenetics)." }
            ]
        },
        {
            name: "Biology, Serology & Pathology",
            icon: Syringe,
            color: "text-rose-400 border-rose-500/40 bg-rose-500/10",
            subsystems: [
                { name: "ABO/Rh Blood Group Serology", desc: "Serological antigen phenotype matching & secretor status." },
                { name: "Lewis Non-Secretor Assay", desc: "FUT2/FUT3 gene secretor status & serology-DNA fusion." },
                { name: "Forensic Pathology & PMI Clock", desc: "Algor, Rigor & Livor mortis Post-Mortem Interval estimation." },
                { name: "Toxicology Widmark BAC Engine", desc: "Widmark clearance rate & PMR cardiac redistribution." },
                { name: "Bloodstain Pattern Analysis BPA", desc: "Directional impact angle, Area of Origin & spatter physics." }
            ]
        },
        {
            name: "LIMS Workflow, Gateway & QA/QC",
            icon: PackageCheck,
            color: "text-amber-400 border-amber-500/40 bg-amber-500/10",
            subsystems: [
                { name: "LIMS-Lite Workflow SOP Chain", desc: "9-Step SOP accessioning, operator ID, reagent lot HMAC." },
                { name: "Automated Instrument Gateway", desc: "CE GeneMapper, qPCR Quantifiler Trio Cq & NGS MiSeq VCF." },
                { name: "QA/QC Gatekeeper Engine", desc: "7-Point quality inspection matrix, Hb ratio, NC/PC controls." },
                { name: "Human Analyst Review & Governance", desc: "Dual sign-off governance, override rationale logging, HMAC hash." },
                { name: "Concurrent Batch Engine", desc: "Multi-sample worker semaphore concurrency & job aggregator." }
            ]
        },
        {
            name: "ISO Certificate & Court Mode",
            icon: Scale,
            color: "text-indigo-400 border-indigo-500/40 bg-indigo-500/10",
            subsystems: [
                { name: "ISO 17025 Certificate Compiler", desc: "8-Section formal certificate compilation with HMAC signing." },
                { name: "Court / Expert Witness Mode", desc: "7-Point judicial testimony framework & brief exporter." },
                { name: "Transposed Conditional Fallacy Shield", desc: "Prosecutor's Fallacy protection guarding against LR misinterpretation." },
                { name: "Synthetic Case & Benchmark Harness", desc: "100% ground-truth mixture generator & ROC-AUC validation." },
                { name: "Master Forensic Evidence OS DAG", desc: "6-Layer Directed Acyclic Graph orchestrator for all 30 subsystems." }
            ]
        }
    ];

    return (
        <section id="subsystems" className="py-16 lg:py-24 border-b border-tactical-border/60 bg-black/40">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-12">
                
                {/* Header */}
                <div className="text-center max-w-3xl mx-auto space-y-3">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-300 font-mono text-xs font-bold uppercase">
                        <Layers className="w-3.5 h-3.5" />
                        Complete 30-Subsystem Taxonomy Matrix
                    </div>
                    <h2 className="text-2xl sm:text-4xl font-extrabold font-mono text-white tracking-tight">
                        30 Biocomputational & Forensic Subsystems
                    </h2>
                    <p className="text-xs sm:text-sm text-zinc-400 font-mono">
                        Grouped into 6 core architectural pillars covering every domain of forensic biology, genetics, and courtroom testimony.
                    </p>
                </div>

                {/* Pillar Selector Buttons */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5 font-mono text-xs">
                    {pillars.map((pillar, idx) => {
                        const Icon = pillar.icon;
                        const isSelected = selectedPillar === idx;
                        return (
                            <button
                                key={idx}
                                onClick={() => setSelectedPillar(idx)}
                                className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between gap-2 cursor-pointer ${
                                    isSelected
                                        ? `${pillar.color} font-bold shadow-lg scale-[1.02]`
                                        : "border-tactical-border/60 bg-tactical-surface/40 hover:bg-tactical-surface text-zinc-400"
                                }`}
                            >
                                <Icon className="w-4 h-4" />
                                <span className="text-[10px] uppercase tracking-wider block font-bold leading-snug">
                                    {pillar.name}
                                </span>
                            </button>
                        );
                    })}
                </div>

                {/* Selected Pillar Subsystems Display */}
                <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-6 shadow-2xl space-y-6">
                    <div className="flex items-center justify-between border-b border-tactical-border/40 pb-4">
                        <div className="flex items-center gap-3">
                            <span className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-200">
                                {pillars[selectedPillar].name} Subsystem Matrix
                            </span>
                        </div>
                        <span className="px-2.5 py-1 rounded bg-black/60 border border-tactical-border/60 text-tactical-accent font-mono text-[9px] font-bold uppercase">
                            5 Integrated Engines
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {pillars[selectedPillar].subsystems.map((sub, sIdx) => (
                            <motion.div
                                key={sIdx}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3, delay: sIdx * 0.05 }}
                                className="p-4 rounded-xl border border-tactical-border/60 bg-black/40 hover:border-tactical-accent/40 transition-all space-y-2 group"
                            >
                                <div className="flex items-center gap-2">
                                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-tactical-accent/20 font-mono text-[9px] font-bold text-tactical-accent">
                                        {sIdx + 1}
                                    </span>
                                    <h3 className="font-mono text-xs font-bold text-zinc-200 group-hover:text-tactical-accent transition-colors">
                                        {sub.name}
                                    </h3>
                                </div>
                                <p className="font-mono text-[10px] text-zinc-400 leading-relaxed">
                                    {sub.desc}
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>

            </div>
        </section>
    );
}
