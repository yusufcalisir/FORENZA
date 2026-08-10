"use client";

import { Lock, FileCheck, AlertOctagon, Cpu } from "lucide-react";
import NeonDnaScroll from "./NeonDnaScroll";

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
        <section id="security-specs" className="min-h-[85vh] lg:min-h-screen flex flex-col justify-between py-12 px-4 bg-tactical-surface/30">
            <div className="my-auto mx-auto max-w-7xl w-full">
                {/* Header */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center gap-2 rounded-full border border-[#22C55E]/30 bg-[#22C55E]/5 px-4 py-1.5 mb-3 shadow-[0_0_15px_rgba(34,197,94,0.1)]">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E] animate-pulse" />
                        <span className="font-mono text-[10px] tracking-widest text-[#22C55E] uppercase font-bold">
                            Security and Specifications
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-bold text-tactical-text mb-3">
                        Privacy by Design, Verified by Proof
                    </h2>
                    <p className="max-w-xl mx-auto text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                        The platform is built on four non-negotiable security principles backed by cryptographic
                        guarantees rather than policy assurances.
                    </p>
                </div>

                {/* Security Pillars */}
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-10">
                    {SECURITY_PILLARS.map((pillar) => {
                        const Icon = pillar.icon;
                        return (
                            <div
                                key={pillar.title}
                                className="rounded-xl border border-tactical-border bg-tactical-surface p-5 hover:border-tactical-border/80 transition-colors shadow-md"
                            >
                                <div
                                    className="mb-3 inline-flex h-9 w-9 items-center justify-center rounded-lg border"
                                    style={{
                                        background: `${pillar.color}15`,
                                        borderColor: `${pillar.color}30`,
                                        color: pillar.color,
                                    }}
                                >
                                    <Icon className="h-4 w-4" />
                                </div>
                                <h3 className="font-bold text-tactical-text text-sm mb-1.5 leading-snug">
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
                <div className="rounded-2xl border border-tactical-border bg-tactical-surface overflow-hidden shadow-xl">
                    <div className="flex items-center gap-3 border-b border-tactical-border px-5 py-3.5">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E] animate-pulse" />
                        <h3 className="font-mono text-xs tracking-widest text-tactical-text-dim uppercase font-bold">
                            Technical Specifications
                        </h3>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-tactical-border">
                    <div className="divide-y divide-tactical-border">
                            {SPECS.slice(0, 6).map((spec) => (
                                <div
                                    key={spec.label}
                                    className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-1 px-4 py-3 hover:bg-tactical-surface-elevated/50 transition-colors font-mono text-xs"
                                >
                                    <span className="text-tactical-text-dim">{spec.label}</span>
                                    <span className="font-bold sm:text-right" style={{ color: spec.color }}>
                                        {spec.value}
                                    </span>
                                </div>
                            ))}
                        </div>
                        <div className="divide-y divide-tactical-border">
                            {SPECS.slice(6, 12).map((spec) => (
                                <div
                                    key={spec.label}
                                    className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-1 px-4 py-3 hover:bg-tactical-surface-elevated/50 transition-colors font-mono text-xs"
                                >
                                    <span className="text-tactical-text-dim">{spec.label}</span>
                                    <span className="font-bold sm:text-right" style={{ color: spec.color }}>
                                        {spec.value}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Neon Scroll to FAQ */}
            <div className="pt-4 flex justify-center">
                <NeonDnaScroll targetId="faq" />
            </div>
        </section>
    );
}
