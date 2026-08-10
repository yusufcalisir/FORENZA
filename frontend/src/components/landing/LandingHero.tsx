"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown, Dna } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";

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
        <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden px-4 pt-24 pb-16">
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

            <div className="relative z-10 mx-auto max-w-5xl text-center">
                {/* Eyebrow badge */}
                <div className="inline-flex items-center gap-2 rounded-full border border-[#06B6D4]/30 bg-[#06B6D4]/5 px-4 py-2 mb-8 shadow-[0_0_20px_rgba(6,182,212,0.1)]">
                    <Dna className="h-4 w-4 text-[#06B6D4]" />
                    <span className="font-mono text-[11px] tracking-widest text-[#06B6D4] font-medium uppercase">
                        ADVANCED FORENSIC DNA INTELLIGENCE PLATFORM
                    </span>
                </div>

                {/* Main headline */}
                <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight text-tactical-text mb-6 leading-tight">
                    Forensic DNA Profiling{" "}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#22C55E] via-[#06B6D4] to-[#8B5CF6]">
                        Redefined
                    </span>
                    <br />
                    <span className="text-3xl sm:text-4xl lg:text-5xl font-normal text-tactical-text-muted">
                        by Statistical Rigor
                    </span>
                </h1>

                {/* Subheading */}
                <p className="max-w-2xl mx-auto text-base sm:text-lg text-tactical-text-muted mb-10 leading-relaxed font-light">
                    VANTAGE-STR combines likelihood ratio STR analysis, generative phenotype reconstruction,
                    and zero-knowledge cryptographic verification with immutable blockchain chain of custody
                    into a single tactical intelligence platform.
                </p>

                {/* CTAs */}
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
                    <LaunchDemoButton size="lg" />
                    <a
                        href="#bio-engine"
                        onClick={scrollToBioEngine}
                        className="flex items-center gap-2 rounded-xl border border-tactical-border bg-tactical-surface/80 backdrop-blur-md px-8 py-4 font-mono text-sm font-medium tracking-wide text-tactical-text-muted hover:text-white hover:border-[#06B6D4]/50 hover:bg-tactical-surface-elevated transition-all duration-200"
                    >
                        <span>Explore Bio-Engine</span>
                        <ChevronDown className="h-4 w-4 text-[#06B6D4]" />
                    </a>
                </div>

                {/* Metrics Bar */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
                    {METRICS.map((m) => (
                        <div
                            key={m.label}
                            className="rounded-xl border border-tactical-border bg-tactical-surface/50 backdrop-blur-sm px-6 py-5 flex flex-col items-center gap-2 hover:border-tactical-border/80 transition-colors shadow-lg"
                        >
                            <span
                                className="font-mono text-3xl font-bold tabular-nums"
                                style={{ color: m.color }}
                            >
                                {m.prefix && <span className="text-lg">{m.prefix}</span>}
                                <CountUp target={m.value} suffix={m.suffix} />
                            </span>
                            <span className="font-mono text-[10px] tracking-widest text-tactical-text-dim uppercase text-center leading-tight">
                                {m.label}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Clickable Scroll Indicator */}
            <button
                onClick={scrollToBioEngine}
                className="mt-16 flex flex-col items-center gap-2 group cursor-pointer border border-tactical-border/50 hover:border-[#22C55E]/50 rounded-full px-5 py-2.5 bg-tactical-surface/40 backdrop-blur-md transition-all duration-300 hover:shadow-[0_0_20px_rgba(34,197,94,0.15)]"
                title="Scroll to Bio-Engine"
            >
                <span className="font-mono text-[10px] font-bold tracking-[0.2em] text-tactical-text-dim group-hover:text-[#22C55E] uppercase transition-colors">
                    SCROLL DOWN
                </span>
                <ChevronDown className="h-4 w-4 text-[#22C55E] group-hover:translate-y-0.5 transition-transform animate-bounce" />
            </button>
        </section>
    );
}
