"use client";

import Link from "next/link";
import { Shield, Activity, Cpu, Layers } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";

export default function LandingHeader() {
    return (
        <header className="sticky top-0 z-50 border-b border-tactical-border/60 bg-black/80 backdrop-blur-xl transition-all">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
                {/* Brand Logo */}
                <Link href="/" className="flex items-center gap-2.5 group shrink-0">
                    <ForenzaLogoIcon size={34} className="group-hover:scale-105 transition-all duration-300 shadow-lg shadow-emerald-500/10" />
                    <div className="flex items-center gap-2">
                        <span className="font-mono text-base font-extrabold tracking-wider text-white">
                            FORENZA
                        </span>
                        <span className="rounded-full bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 text-[9px] font-mono font-bold text-emerald-400">
                            EVIDENCE OS
                        </span>
                    </div>
                </Link>

                {/* Navigation Links */}
                <nav className="hidden md:flex items-center gap-6 lg:gap-8 font-mono text-xs text-zinc-400">
                    <a href="#bio-simulator" className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium">
                        <Activity className="w-3.5 h-3.5 text-cyan-400" />
                        Bio-Simulator
                    </a>
                    <a href="#subsystems" className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium">
                        <Layers className="w-3.5 h-3.5 text-purple-400" />
                        30 Subsystems
                    </a>
                    <a href="#architecture" className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium">
                        <Cpu className="w-3.5 h-3.5 text-emerald-400" />
                        Evidence OS DAG
                    </a>
                    <a href="#security" className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium">
                        <Shield className="w-3.5 h-3.5 text-amber-400" />
                        Security &amp; ISO
                    </a>
                </nav>

                {/* Actions */}
                <div className="flex items-center gap-3 shrink-0">
                    <LaunchDemoButton size="sm" label="Launch Demo OS" />
                </div>
            </div>
        </header>
    );
}
