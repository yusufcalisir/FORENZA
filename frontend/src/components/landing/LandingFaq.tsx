"use client";

import { useState } from "react";
import { ChevronDown, HelpCircle } from "lucide-react";

const FAQS = [
    {
        q: "What data inputs and instrument file formats does FORENZA accept?",
        a: "FORENZA features an automated Instrument Gateway ingesting CE GeneMapper peak height tables (.csv), qPCR Quantifiler Trio concentration Cq & Degradation Index (.csv), NGS MiSeq variant call files (.vcf), LIMS sample manifests, and raw autosomal STR profiles across 24 CODIS core loci.",
        color: "#22C55E",
    },
    {
        q: "How are Likelihood Ratios (LR) calculated for complex multi-person mixtures?",
        a: "Likelihood ratios are calculated using Metropolis-Hastings MCMC Probabilistic Genotyping evaluating 2-to-4 contributor mixtures with stochastic dropout (p_d), drop-in (p_i), and stutter parameters. Population frequencies are corrected under the Balding-Nichols Dirichlet model (NRC II Recommendation 4.1 & 4.2), and Tippett non-contributor calibration curves are generated automatically.",
        color: "#06B6D4",
    },
    {
        q: "What lineage forensics and kinship capabilities are included?",
        a: "FORENZA integrates Y-STR haplotype analysis (with Clopper-Pearson 95% binomial confidence intervals and Y-HRD lookup), X-STR linkage disequilibrium kinship indexing (KI_X), mtDNA control region (rCRS/RSRS) haplogroup alignment, and mass disaster (DVI) victim identification pedigree trees.",
        color: "#8B5CF6",
    },
    {
        q: "How does FORENZA handle Phenotyping and Epigenetic Aging?",
        a: "Phenotyping is powered by the extended HIrisPlex-S neural model predicting Eye Color, Hair Color & Morphology, Skin Tone, and Freckling risk. Epigenetics features the Horvath 5-CpG DNA methylation clock (with U_95% uncertainty estimation), tissue-specific tDMR body fluid deconvolution, and AHRR smoking environmental exposure scoring.",
        color: "#22C55E",
    },
    {
        q: "How does Zero-Knowledge Privacy & Chain of Custody work?",
        a: "Private DNA profiles remain local to secure enclaves. Circom/SnarkJS zkSNARK circuits generate Groth16 cryptographic proofs confirming match criteria without revealing allele values. All accessioning events, SOP workflow steps, QA/QC verdicts, and analyst sign-offs are SHA-256 hashed and anchored to a Polygon cryptographic ledger.",
        color: "#06B6D4",
    },
    {
        q: "How does FORENZA enforce ISO 17025 compliance and Analyst Governance?",
        a: "FORENZA features a 7-Point QA/QC Inspection Matrix (monitoring Hb balance, ST thresholds, NC/PC controls), a Dual Analyst Sign-Off workflow requiring written justifications for AI predicate overrides, and an 8-Section formal ISO 17025 Certificate Compiler.",
        color: "#8B5CF6",
    },
    {
        q: "What is Expert Witness Court Mode and the Fallacy Shield?",
        a: "Court Mode converts complex biocomputational traces into a 7-Point Judicial Testimony Framework covering tested items, observed peak heights, calculated LRs, assumptions, verbal predicate meanings, limitations, and a Prosecutor's Fallacy Shield guarding against Transposed Conditional Fallacy.",
        color: "#22C55E",
    },
    {
        q: "Can FORENZA run automated self-testing against ground truth?",
        a: "Yes. FORENZA includes a Synthetic Forensic Case Generator that synthesizes 100% known ground-truth cases (2-4 person mixtures, degradation, dropout) to run automated self-validation benchmark evaluation calculating ROC-AUC, Log10 LR RMSE, and False Inclusion Rate (FIR at 0%).",
        color: "#06B6D4",
    },
];

export default function LandingFaq() {
    const [openIdx, setOpenIdx] = useState<number | null>(0);

    return (
        <section id="faq" className="scroll-mt-20 py-16 px-4 font-mono border-b border-tactical-border/60">
            <div className="mx-auto max-w-3xl w-full space-y-10">
                
                {/* Header */}
                <div className="text-center space-y-3">
                    <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1.5 shadow-lg">
                        <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
                        <span className="font-mono text-xs font-bold text-cyan-300 uppercase tracking-wider">
                            Technical FAQ & Methodological Principles
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
                        Frequently Asked Questions
                    </h2>
                    <p className="max-w-xl mx-auto text-zinc-400 text-xs sm:text-sm leading-relaxed">
                        Detailed methodological, compliance, and biocomputational answers covering the FORENZA platform.
                    </p>
                </div>

                {/* Accordion */}
                <div className="space-y-3">
                    {FAQS.map((faq, i) => {
                        const isOpen = openIdx === i;
                        return (
                            <div
                                key={i}
                                className="rounded-2xl border border-tactical-border/80 bg-tactical-surface overflow-hidden transition-all duration-200 shadow-xl"
                                style={isOpen ? { borderColor: `${faq.color}60` } : {}}
                            >
                                <button
                                    onClick={() => setOpenIdx(isOpen ? null : i)}
                                    className="w-full flex items-center justify-between gap-4 px-6 py-4 text-left hover:bg-tactical-surface-elevated/50 transition-colors cursor-pointer"
                                >
                                    <span className="font-bold text-zinc-200 text-xs sm:text-sm leading-snug pr-2">
                                        {faq.q}
                                    </span>
                                    <ChevronDown
                                        className={`h-4 w-4 shrink-0 transition-transform duration-300 ${
                                            isOpen ? "rotate-180" : ""
                                        }`}
                                        style={{ color: isOpen ? faq.color : undefined }}
                                    />
                                </button>
                                {isOpen && (
                                    <div className="px-6 pb-5">
                                        <div
                                            className="h-px mb-3"
                                            style={{
                                                background: `linear-gradient(to right, ${faq.color}40, transparent)`,
                                            }}
                                        />
                                        <p className="text-zinc-400 text-xs sm:text-sm leading-relaxed">
                                            {faq.a}
                                        </p>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

            </div>
        </section>
    );
}
