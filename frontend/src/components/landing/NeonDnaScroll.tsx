"use client";

import { Dna, ChevronDown } from "lucide-react";

export default function NeonDnaScroll({ targetId = "bio-engine" }: { targetId?: string }) {
    const handleScroll = (e: React.MouseEvent) => {
        e.preventDefault();
        const el = document.getElementById(targetId);
        if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    return (
        <button
            onClick={handleScroll}
            className="group relative inline-flex flex-col items-center justify-center p-3 rounded-full cursor-pointer transition-all duration-300 hover:scale-110 focus:outline-none"
            title="Scroll to next section"
        >
            {/* Outer Neon Glow Aura */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-[#22C55E]/30 via-[#06B6D4]/20 to-[#8B5CF6]/30 blur-md group-hover:blur-lg opacity-70 group-hover:opacity-100 transition-all duration-300 animate-pulse" />

            {/* Glass Ring Container */}
            <div className="relative flex h-12 w-12 items-center justify-center rounded-full bg-[#0A0A0B]/90 border border-[#22C55E]/50 group-hover:border-[#06B6D4] shadow-[0_0_20px_rgba(34,197,94,0.3)] group-hover:shadow-[0_0_30px_rgba(6,182,212,0.6)] transition-all duration-300 overflow-hidden">
                {/* Rotating Neon Backdrop Grid */}
                <div className="absolute inset-0 bg-gradient-to-tr from-[#22C55E]/20 to-[#06B6D4]/20 opacity-50 group-hover:opacity-100 transition-opacity" />

                {/* Animated DNA Double Helix */}
                <Dna className="relative h-6 w-6 text-[#22C55E] group-hover:text-[#06B6D4] transition-all duration-300 drop-shadow-[0_0_8px_rgba(34,197,94,0.8)] group-hover:drop-shadow-[0_0_12px_rgba(6,182,212,1)] animate-[spin_8s_linear_infinite]" />
            </div>

            {/* Micro Chevron indicator under helix */}
            <ChevronDown className="relative mt-1 h-3.5 w-3.5 text-[#22C55E] group-hover:text-[#06B6D4] animate-bounce drop-shadow-[0_0_6px_rgba(34,197,94,0.8)] transition-colors" />
        </button>
    );
}
