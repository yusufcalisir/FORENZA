"use client";

import { useEffect, useRef, useState } from "react";
import { Dna } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";
import NeonDnaScroll from "./NeonDnaScroll";

const METRICS = [
    { value: 20, suffix: " / 20", label: "CODIS Core Loci", color: "#22C55E" },
    { value: 12, prefix: "< ", suffix: "ms", label: "ZK Proof Generation", color: "#06B6D4" },
    { value: 99.4, suffix: "%", label: "Phenotype Accuracy", color: "#8B5CF6" },
    { value: 54, suffix: "", label: "GTEx Tissue eQTLs", color: "#22C55E" },
];

function CountUp({ target, prefix = "", suffix = "" }: { target: number; prefix?: string; suffix?: string }) {
    const [val, setVal] = useState(0);
    const ref = useRef<HTMLSpanElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (!entry.isIntersecting) return;
                observer.disconnect();
                let start = 0;
                const duration = 1600;
                const step = (timestamp: number) => {
                    if (!start) start = timestamp;
                    const progress = Math.min((timestamp - start) / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    setVal(parseFloat((eased * target).toFixed(1)));
                    if (progress < 1) requestAnimationFrame(step);
                };
                requestAnimationFrame(step);
            },
            { threshold: 0.5 }
        );
        if (ref.current) observer.observe(ref.current);
        return () => observer.disconnect();
    }, [target]);

    return (
        <span ref={ref} className="tabular-nums">
            {prefix}{Number.isInteger(target) ? Math.round(val) : val.toFixed(1)}{suffix}
        </span>
    );
}

export default function LandingHero() {
    const scrollToBioEngine = (e: React.MouseEvent) => {
        e.preventDefault();
        const el = document.getElementById("bio-engine");
        if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    return (
        <section className="relative min-h-[90vh] lg:min-h-screen flex flex-col items-center justify-between overflow-hidden px-4 pt-20 pb-8">
            {/* Background mesh / grid */}
            <div className="absolute inset-0 pointer-events-none select-none">
                {/* Gradient orbs */}
                <div className="absolute top-1/4 left-1/3 w-[600px] h-[600px] rounded-full bg-[#22C55E]/5 blur-[120px]" />
                <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full bg-[#06B6D4]/5 blur-[100px]" />
                <div className="absolute top-1/3 right-1/3 w-[400px] h-[400px] rounded-full bg-[#8B5CF6]/5 blur-[90px]" />
                {/* Grid overlay */}
                <div
                    className="absolute inset-0 opacity-[0.04]"
                    style={{
                        backgroundImage: `linear-gradient(#22C55E 1px, transparent 1px), linear-gradient(90deg, #22C55E 1px, transparent 1px)`,
                        backgroundSize: "60px 60px",
                    }}
                />
            </div>

            <div className="my-auto relative z-10 mx-auto max-w-5xl text-center flex flex-col items-center">
                {/* Eyebrow badge */}
                <div className="inline-flex items-center gap-2 rounded-full border border-[#06B6D4]/30 bg-[#06B6D4]/5 px-4 py-1.5 mb-6 shadow-[0_0_20px_rgba(6,182,212,0.1)]">
                    <Dna className="h-4 w-4 text-[#06B6D4]" />
                    <span className="font-mono text-[10px] tracking-widest text-[#06B6D4] font-medium uppercase">
                        ADVANCED FORENSIC DNA INTELLIGENCE PLATFORM
                    </span>
                </div>

                {/* Main headline */}
                <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight text-tactical-text mb-4 leading-tight">
                    Forensic DNA Profiling{" "}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#22C55E] via-[#06B6D4] to-[#8B5CF6]">
                        Redefined
                    </span>
                    <br />
                    <span className="text-2xl sm:text-3xl lg:text-5xl font-normal text-tactical-text-muted">
                        by Statistical Rigor
                    </span>
                </h1>

                {/* Subheading */}
                <p className="max-w-2xl mx-auto text-sm sm:text-base text-tactical-text-muted mb-6 sm:mb-8 leading-relaxed font-light">
                    VANTAGE-STR combines likelihood ratio STR analysis, generative phenotype reconstruction,
                    and zero-knowledge cryptographic verification with immutable blockchain chain of custody
                    into a single tactical intelligence platform.
                </p>

                {/* 4 Metrics Cards - Always ON TOP of the buttons on ALL screens */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-3 max-w-4xl w-full mx-auto mb-6 sm:mb-8">
                    {METRICS.map((m) => (
                        <div
                            key={m.label}
                            className="rounded-xl border border-tactical-border bg-tactical-surface/50 backdrop-blur-sm px-3 sm:px-5 py-3 sm:py-4 flex flex-col items-center justify-center gap-1 hover:border-tactical-border/80 transition-colors shadow-lg"
                        >
                            <span
                                className="font-mono text-xl sm:text-3xl font-bold tabular-nums"
                                style={{ color: m.color }}
                            >
                                {m.prefix && <span className="text-sm sm:text-base">{m.prefix}</span>}
                                <CountUp target={m.value} suffix={m.suffix} />
                            </span>
                            <span className="font-mono text-[8px] sm:text-[9px] tracking-widest text-tactical-text-dim uppercase text-center leading-tight">
                                {m.label}
                            </span>
                        </div>
                    ))}
                </div>

                {/* CTAs - Always BELOW the 4 cards with perfect height & alignment parity */}
                <div className="flex flex-row items-center justify-center gap-2.5 sm:gap-4 w-full max-w-sm sm:max-w-none">
                    <div className="flex-1 sm:flex-none">
                        <LaunchDemoButton size="md" className="w-full sm:w-auto hidden sm:inline-flex" />
                        <LaunchDemoButton size="sm" className="w-full sm:hidden" />
                    </div>
                    <a
                        href="#bio-engine"
                        onClick={scrollToBioEngine}
                        className="flex-1 sm:flex-none flex items-center justify-center rounded-xl border border-tactical-border bg-tactical-surface/80 backdrop-blur-md px-3.5 sm:px-6 py-2 sm:py-2.5 font-mono text-[10px] sm:text-xs font-medium tracking-wide text-tactical-text-muted hover:text-white hover:border-[#06B6D4]/50 hover:bg-tactical-surface-elevated transition-all duration-200 whitespace-nowrap"
                    >
                        <span>Explore Bio-Engine</span>
                    </a>
                </div>
            </div>

            {/* Neon Animated DNA Helix Scroll Indicator (Desktop Only) */}
            <div className="hidden sm:block pt-4 z-20">
                <NeonDnaScroll targetId="bio-engine" />
            </div>
        </section>
    );
}
