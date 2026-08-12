"use client";

import Link from "next/link";
import { Shield, Activity, Cpu, Layers } from "lucide-react";
import LaunchDemoButton from "./LaunchDemoButton";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";

export default function LandingHeader() {
    const scrollToSection = (id: string, e: React.MouseEvent) => {
        e.preventDefault();
        const el = document.getElementById(id);
        if (el) {
            const headerOffset = 70;
            const elementPosition = el.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        }
    };

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
                    <button 
                        type="button"
                        onClick={(e) => scrollToSection("bio-simulator", e)} 
                        className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium cursor-pointer bg-transparent border-0 p-0"
                    >
                        <Activity className="w-3.5 h-3.5 text-cyan-400" />
                        Bio-Simulator
                    </button>
                    <button 
                        type="button"
                        onClick={(e) => scrollToSection("subsystems", e)} 
                        className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium cursor-pointer bg-transparent border-0 p-0"
                    >
                        <Layers className="w-3.5 h-3.5 text-purple-400" />
                        30 Subsystems
                    </button>
                    <button 
                        type="button"
                        onClick={(e) => scrollToSection("architecture", e)} 
                        className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium cursor-pointer bg-transparent border-0 p-0"
                    >
                        <Cpu className="w-3.5 h-3.5 text-emerald-400" />
                        Evidence OS DAG
                    </button>
                    <button 
                        type="button"
                        onClick={(e) => scrollToSection("security", e)} 
                        className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 font-medium cursor-pointer bg-transparent border-0 p-0"
                    >
                        <Shield className="w-3.5 h-3.5 text-amber-400" />
                        Security &amp; ISO
                    </button>
                </nav>

                {/* Actions */}
                <div className="flex items-center gap-3 shrink-0">
                    <LaunchDemoButton size="sm" label="Launch Demo OS" />
                </div>
            </div>
        </header>
    );
}
