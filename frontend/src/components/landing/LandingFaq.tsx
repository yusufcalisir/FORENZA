"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import NeonDnaScroll from "./NeonDnaScroll";

const FAQS = [
    {
        q: "What input formats does VANTAGE-STR accept?",
        a: "The platform accepts standard VCF (Variant Call Format), CODIS-compatible text profiles with 20 core STR loci, and raw FASTQ files for upstream processing. Custom SNP panel formats aligned to IrisPlex or HIrisPlex-S can also be provided in structured JSON format via the API.",
        color: "#22C55E",
    },
    {
        q: "How are likelihood ratios calculated?",
        a: "Likelihood ratios are computed using the Balding-Nichols NRC II model with configurable theta correction values (default: 0.01 for intragroup, 0.03 for cross-group). Each locus receives an individual LR score, and a combined product LR is calculated under the assumption of independence, with a correction applied when loci are known to be in linkage disequilibrium.",
        color: "#06B6D4",
    },
    {
        q: "How does Zero-Knowledge genetic verification work?",
        a: "The Circom circuit dna_match.circom encodes the DNA match condition as a mathematical constraint. A Groth16 proof is generated via SnarkJS using the private STR profile as a witness. The proof can be verified by any third party using only the public parameters and the proof hash. The raw allele data is never required for verification and is not transmitted.",
        color: "#8B5CF6",
    },
    {
        q: "Is raw genetic data stored on the blockchain?",
        a: "No. The blockchain stores only a SHA-256 hash of the final forensic report and the ZK proof reference identifier. Raw STR allele values, phenotype predictions, and geographic heatmap coordinates are never written to the chain. All sensitive data resides exclusively within the isolated local processing environment.",
        color: "#22C55E",
    },
    {
        q: "What are the hardware requirements for self-hosted deployment?",
        a: "A minimum configuration requires a 4-core CPU, 16 GB RAM, and 50 GB SSD for the backend processing stack. PyTorch phenotype inference benefits significantly from a CUDA-capable GPU (NVIDIA RTX 3060 or higher recommended). The Docker Compose stack covers all service dependencies including PostgreSQL, Redis, and Milvus.",
        color: "#06B6D4",
    },
    {
        q: "Is the platform compliant with forensic science standards?",
        a: "VANTAGE-STR implements the NRC II statistical framework as recommended by SWGDAM and OSAC guidelines. The blockchain audit trail is designed to satisfy chain of custody documentation requirements for court proceedings. Users are responsible for validating compliance with the specific statutory requirements of their jurisdiction before using outputs in legal contexts.",
        color: "#8B5CF6",
    },
    {
        q: "Can I use VANTAGE-STR for population genetics research?",
        a: "Yes. The platform provides exportable allele frequency matrices, combined LR tables, and phenotype posterior probability distributions in structured JSON and CSV formats. The GTEx eQTL integration provides cross-reference data across 54 non-diseased tissue types, supporting population-level genetic association analyses.",
        color: "#22C55E",
    },
];

export default function LandingFaq() {
    const [openIdx, setOpenIdx] = useState<number | null>(0);

    return (
        <section id="faq" className="min-h-[85vh] lg:min-h-screen flex flex-col justify-between py-12 px-4">
            <div className="my-auto mx-auto max-w-3xl w-full">
                {/* Header */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center gap-2 rounded-full border border-[#06B6D4]/30 bg-[#06B6D4]/5 px-4 py-1.5 mb-3 shadow-[0_0_15px_rgba(6,182,212,0.1)]">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#06B6D4] animate-pulse" />
                        <span className="font-mono text-[10px] tracking-widest text-[#06B6D4] uppercase font-bold">
                            Technical FAQ
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-bold text-tactical-text mb-3">
                        Frequently Asked Questions
                    </h2>
                    <p className="max-w-xl mx-auto text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                        Detailed answers to common questions about methodology, deployment, and compliance.
                    </p>
                </div>

                {/* Accordion */}
                <div className="space-y-2.5">
                    {FAQS.map((faq, i) => {
                        const isOpen = openIdx === i;
                        return (
                            <div
                                key={i}
                                className="rounded-xl border border-tactical-border bg-tactical-surface overflow-hidden transition-all duration-200 shadow-md"
                                style={isOpen ? { borderColor: `${faq.color}60` } : {}}
                            >
                                <button
                                    onClick={() => setOpenIdx(isOpen ? null : i)}
                                    className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left hover:bg-tactical-surface-elevated/50 transition-colors"
                                >
                                    <span className="font-medium text-tactical-text text-sm leading-snug pr-2">
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
                                    <div className="px-5 pb-4">
                                        <div
                                            className="h-px mb-3"
                                            style={{
                                                background: `linear-gradient(to right, ${faq.color}40, transparent)`,
                                            }}
                                        />
                                        <p className="text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                                            {faq.a}
                                        </p>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Neon Scroll to Footer (Desktop Only) */}
            <div className="hidden sm:flex pt-4 justify-center">
                <NeonDnaScroll targetId="footer" />
            </div>
        </section>
    );
}
