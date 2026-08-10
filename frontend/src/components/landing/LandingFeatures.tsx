"use client";

import {
    Eye,
    Globe,
    GitMerge,
    ShieldCheck,
    Blocks,
    Network,
} from "lucide-react";
import NeonDnaScroll from "./NeonDnaScroll";

const FEATURES = [
    {
        icon: Eye,
        title: "Biometric Trait Reconstruction",
        description:
            "Deterministic mapping of SNP markers from the HERC2, MC1R, and SLC24A5 gene panels to ocular pigmentation, Fitzpatrick skin type, and hair morphology scores. Each prediction is reported with posterior probability intervals.",
        tags: ["HERC2", "MC1R", "SLC24A5", "PHENOTYPE LR"],
        color: "#22C55E",
        glow: "rgba(34,197,94,0.12)",
    },
    {
        icon: Globe,
        title: "Geo-Forensic Heatmaps",
        description:
            "Spatial centroid estimation uses k-NN ancestry classifiers and Random Forest weighting to generate interactive global heatmaps with 95% confidence interval rings. Auto-flyTo targets high-probability geographic clusters.",
        tags: ["K-NN", "RANDOM FOREST", "95% CI", "LEAFLET.JS"],
        color: "#06B6D4",
        glow: "rgba(6,182,212,0.12)",
    },
    {
        icon: GitMerge,
        title: "Kinship and Pedigree Indexing",
        description:
            "Multi-generational family link detection using Kinship Indices (KI) formulated under the Balding-Nichols NRC II model. Graph-based pedigree tree renders Parent-Child, Sibling, and Half-Sibling relationship chains.",
        tags: ["KINSHIP INDEX", "BALDING-NICHOLS", "NRC II", "GRAPH RENDER"],
        color: "#8B5CF6",
        glow: "rgba(139,92,246,0.12)",
    },
    {
        icon: ShieldCheck,
        title: "Zero-Knowledge Genetic Verification",
        description:
            "Circom-defined arithmetic circuits compiled with SnarkJS (Groth16) enable cryptographic proof of DNA profile match without exposing any raw STR allele data. Verification is fully auditable from the public proof hash alone.",
        tags: ["CIRCOM", "SNARKJS", "GROTH16", "ZKP"],
        color: "#22C55E",
        glow: "rgba(34,197,94,0.12)",
    },
    {
        icon: Blocks,
        title: "Blockchain Chain of Custody",
        description:
            "Every forensic analysis session is SHA-256 hashed and anchored to the Polygon Amoy (testnet) or Ethereum Sepolia blockchain via on-chain Solidity smart contracts. Report immutability is independently verifiable via Etherscan.",
        tags: ["SOLIDITY", "POLYGON", "ETHERSCAN", "WAGMI/VIEM"],
        color: "#06B6D4",
        glow: "rgba(6,182,212,0.12)",
    },
    {
        icon: Network,
        title: "Decentralized Node Infrastructure",
        description:
            "Distributed processing nodes with real-time health monitoring, latency scoring, and secure peer validation. Each node participates in decentralized job routing for high-availability forensic computation.",
        tags: ["NODE GRAPH", "P2P", "JOB ROUTING", "FASTAPI"],
        color: "#8B5CF6",
        glow: "rgba(139,92,246,0.12)",
    },
];

export default function LandingFeatures() {
    return (
        <section id="features" className="min-h-[85vh] lg:min-h-screen flex flex-col justify-between py-12 px-4">
            <div className="my-auto mx-auto max-w-7xl w-full">
                {/* Section header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 rounded-full border border-[#22C55E]/30 bg-[#22C55E]/5 px-4 py-1.5 mb-3 shadow-[0_0_15px_rgba(34,197,94,0.1)]">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E] animate-pulse" />
                        <span className="font-mono text-[10px] tracking-widest text-[#22C55E] uppercase font-bold">
                            Platform Capabilities
                        </span>
                    </div>
                    <h2 className="text-3xl sm:text-5xl font-bold text-tactical-text mb-3">
                        Six Core Analytical Modules
                    </h2>
                    <p className="max-w-xl mx-auto text-tactical-text-muted text-xs sm:text-sm leading-relaxed">
                        From raw STR profile ingestion to cryptographically anchored forensic reports, each module
                        is engineered for precision at the intersection of genetics and intelligence.
                    </p>
                </div>

                {/* Feature Grid with Fixed Bottom Tag Divider Baseline */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                    {FEATURES.map((feature) => {
                        const Icon = feature.icon;
                        return (
                            <div
                                key={feature.title}
                                className="group flex flex-col justify-between h-full rounded-2xl border border-tactical-border bg-tactical-surface p-6 hover:border-tactical-border/80 transition-all duration-300 hover:-translate-y-1 shadow-lg"
                                onMouseEnter={(e) => {
                                    (e.currentTarget as HTMLDivElement).style.boxShadow = `0 0 40px ${feature.glow}`;
                                }}
                                onMouseLeave={(e) => {
                                    (e.currentTarget as HTMLDivElement).style.boxShadow = "none";
                                }}
                            >
                                {/* Top Content Area */}
                                <div className="flex-1">
                                    {/* Icon */}
                                    <div
                                        className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl border transition-transform duration-300 group-hover:scale-110"
                                        style={{
                                            background: `${feature.color}15`,
                                            borderColor: `${feature.color}35`,
                                            color: feature.color,
                                            boxShadow: `0 0 20px ${feature.color}20`,
                                        }}
                                    >
                                        <Icon className="h-5 w-5" />
                                    </div>

                                    {/* Title */}
                                    <h3 className="font-bold text-tactical-text text-base mb-2 leading-snug">
                                        {feature.title}
                                    </h3>

                                    {/* Description */}
                                    <p className="text-tactical-text-muted text-xs leading-relaxed mb-5">
                                        {feature.description}
                                    </p>
                                </div>

                                {/* Bottom Tag Chips Area with Fixed Minimum Height so the Divider Line is Perfectly Aligned Across All Cards */}
                                <div className="mt-auto pt-4 border-t border-tactical-border/50 min-h-[72px] flex flex-wrap content-start gap-2">
                                    {feature.tags.map((tag) => (
                                        <span
                                            key={tag}
                                            className="rounded-lg border px-2 py-0.5 font-mono text-[9px] font-bold tracking-widest uppercase transition-all"
                                            style={{
                                                borderColor: `${feature.color}35`,
                                                color: feature.color,
                                                background: `${feature.color}0D`,
                                            }}
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Neon Scroll to Architecture */}
            <div className="pt-4 flex justify-center">
                <NeonDnaScroll targetId="architecture" />
            </div>
        </section>
    );
}
