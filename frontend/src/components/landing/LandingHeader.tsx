"use client";

import Link from "next/link";
import { Dna, ArrowRight, Shield, Activity, Sparkles, Cpu, Layers } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";

export default function LandingHeader() {
    return (
        <header className="sticky top-0 z-50 border-b border-tactical-border/60 bg-black/80 backdrop-blur-xl transition-all">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3.5 sm:px-6 lg:px-8">
                {/* Brand Logo */}
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-tactical-accent via-cyan-500 to-blue-600 p-0.5 shadow-lg shadow-tactical-accent/20 group-hover:scale-105 transition-all duration-300">
                        <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-black">
                            <Dna className="h-5 w-5 text-tactical-accent animate-pulse" />
                        </div>
                    </div>
                    <div className="flex flex-col">
                        <div className="flex items-center gap-2">
                            <span className="font-mono text-base font-extrabold tracking-wider text-white">
                                FORENZA
                            </span>
                            <span className="rounded-full bg-tactical-accent/20 border border-tactical-accent/40 px-2 py-0.5 text-[9px] font-mono font-bold text-tactical-accent">
                                EVIDENCE OS
                            </span>
                        </div>
                        <span className="font-mono text-[10px] tracking-tight text-zinc-400">
                            Biocomputational Forensic Intelligence
                        </span>
                    </div>
                </Link>

                {/* Navigation Links */}
                <nav className="hidden md:flex items-center gap-6 font-mono text-xs text-zinc-400">
                    <a href="#bio-simulator" className="hover:text-tactical-accent transition-colors flex items-center gap-1.5">
                        <Activity className="w-3.5 h-3.5 text-cyan-400" />
                        Bio-Simulator
                    </a>
                    <a href="#subsystems" className="hover:text-tactical-accent transition-colors flex items-center gap-1.5">
                        <Layers className="w-3.5 h-3.5 text-purple-400" />
                        30 Subsystems
                    </a>
                    <a href="#architecture" className="hover:text-tactical-accent transition-colors flex items-center gap-1.5">
                        <Cpu className="w-3.5 h-3.5 text-emerald-400" />
                        Evidence OS DAG
                    </a>
                    <a href="#security" className="hover:text-tactical-accent transition-colors flex items-center gap-1.5">
                        <Shield className="w-3.5 h-3.5 text-amber-400" />
                        ISO 17025 & ZKP
                    </a>
                </nav>

                {/* Actions */}
                <div className="flex items-center gap-3">
                    <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-tactical-surface border border-tactical-border/60 text-[10px] font-mono text-zinc-300">
                        <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                        <span>30 Subsystems Operational</span>
                    </div>
                    <LaunchDemoButton label="Launch Demo OS" />
                </div>
            </div>
        </header>
    );
}
