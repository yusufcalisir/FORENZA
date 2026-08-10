"use client";

import { Lock, FileCheck, AlertOctagon, Cpu } from "lucide-react";

const SECURITY_PILLARS = [
    {
        icon: Lock,
        title: "Zero-Knowledge Privacy",
        desc: "Raw STR allele data never leaves the local processing environment. Circom/SnarkJS circuits generate Groth16 proofs that confirm a match condition cryptographically without transmitting any genetic profile data.",
        color: "#22C55E",
    },
    {
        icon: FileCheck,
        title: "Immutable Audit Trails",
        desc: "Every analysis event, report generation, and access request is SHA-256 hashed and anchored to a Polygon blockchain node. Each entry is independently verifiable via Etherscan without relying on the platform itself.",
        color: "#06B6D4",
    },
    {
        icon: AlertOctagon,
        title: "Data Isolation Architecture",
        desc: "Raw genetic samples are processed in isolated execution environments with no persistent storage of private allele data. Post-analysis, only aggregate statistics and the ZK proof artifact are retained.",
        color: "#8B5CF6",
    },
    {
        icon: Cpu,
        title: "Decentralized Computation",
        desc: "Forensic computation is distributed across the node network. No single node holds a complete dataset, and each node's participation in a computation job is cryptographically verifiable by the other participants.",
        color: "#22C55E",
    },
];

const SPECS = [
    { label: "STR Loci Support", value: "CODIS 20 Core + Custom Panels", color: "#22C55E" },
    { label: "SNP Panels", value: "IrisPlex, HIrisPlex-S, HolyPlex", color: "#06B6D4" },
    { label: "ZK Proof Latency", value: "< 12ms (Groth16 / SnarkJS)", color: "#8B5CF6" },
    { label: "Phenotype Accuracy", value: "99.4% (IrisPlex validation cohort)", color: "#22C55E" },
    { label: "Population Models", value: "NRC II Balding-Nichols (theta = 0.01, 0.03)", color: "#06B6D4" },
    { label: "GTEx Tissue References", value: "54 non-diseased tissue sites", color: "#8B5CF6" },
    { label: "Blockchain Networks", value: "Polygon Amoy Testnet / Ethereum Sepolia", color: "#22C55E" },
    { label: "Frontend Framework", value: "Next.js 14 App Router + Tailwind CSS v4", color: "#06B6D4" },
    { label: "Backend Stack", value: "FastAPI (Python 3.10+), PyTorch, Scikit-learn", color: "#8B5CF6" },
    { label: "Vector Database", value: "Milvus for embedding similarity search", color: "#22C55E" },
    { label: "Smart Contracts", value: "Solidity (Hardhat), Wagmi / Viem hooks", color: "#06B6D4" },
    { label: "Infrastructure", value: "Docker Compose, Supabase / PostgreSQL, Redis", color: "#8B5CF6" },
];

export default function LandingSecuritySpecs() {
    return (
        <section id="security-specs" className="py-24 px-4 bg-tactical-surface/30">
            <div className="mx-auto max-w-7xl">
                {/* Header */}
                <div className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 rounded-full border border-[#22C55E]/30 bg-[#22C55E]/5 px-4 py-2 mb-4">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E]" />
                        <span className="font-mono text-[10px] tracking-widest text-[#22C55E] uppercase font-medium">
                            Security and Specifications
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-4xl font-bold text-tactical-text mb-4">
                        Privacy by Design, Verified by Proof
                    </h2>
                    <p className="max-w-xl mx-auto text-tactical-text-muted text-sm leading-relaxed">
                        The platform is built on four non-negotiable security principles backed by cryptographic
                        guarantees rather than policy assurances.
                    </p>
                </div>

                {/* Security Pillars */}
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-16">
                    {SECURITY_PILLARS.map((pillar) => {
                        const Icon = pillar.icon;
                        return (
                            <div
                                key={pillar.title}
                                className="rounded-xl border border-tactical-border bg-tactical-surface p-6 hover:border-tactical-border/80 transition-colors"
                            >
                                <div
                                    className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg border"
                                    style={{
                                        background: `${pillar.color}15`,
                                        borderColor: `${pillar.color}30`,
                                        color: pillar.color,
                                    }}
                                >
                                    <Icon className="h-5 w-5" />
                                </div>
                                <h3 className="font-semibold text-tactical-text text-sm mb-2 leading-snug">
                                    {pillar.title}
                                </h3>
                                <p className="text-tactical-text-muted text-xs leading-relaxed">
                                    {pillar.desc}
                                </p>
                            </div>
                        );
                    })}
                </div>

                {/* Technical Specifications Table */}
                <div className="rounded-2xl border border-tactical-border bg-tactical-surface overflow-hidden">
                    <div className="flex items-center gap-3 border-b border-tactical-border px-6 py-4">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E] animate-pulse" />
                        <h3 className="font-mono text-xs tracking-widest text-tactical-text-dim uppercase">
                            Technical Specifications
                        </h3>
                    </div>
                    <div className="divide-y divide-tactical-border">
                        {SPECS.map((spec, i) => (
                            <div
                                key={spec.label}
                                className="grid grid-cols-2 gap-4 px-6 py-4 hover:bg-tactical-surface-elevated/50 transition-colors"
                            >
                                <span className="font-mono text-[11px] tracking-wide text-tactical-text-dim">
                                    {spec.label}
                                </span>
                                <span
                                    className="font-mono text-[11px] tracking-wide font-medium"
                                    style={{ color: spec.color }}
                                >
                                    {spec.value}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
