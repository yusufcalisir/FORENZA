"use client";

import { Dna } from "lucide-react";

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
            className="group relative inline-flex flex-col items-center justify-center p-2 cursor-pointer transition-all duration-300 hover:scale-110 focus:outline-none"
            title="Scroll to next section"
        >
            {/* Soft Ambient Neon Glow Behind Helix */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-b from-[#22C55E]/30 via-[#06B6D4]/20 to-transparent blur-lg opacity-60 group-hover:opacity-100 group-hover:blur-xl transition-all duration-300" />

            {/* Standalone Vertical Neon Animated DNA Double Helix */}
            <div className="relative flex items-center justify-center p-1.5 animate-bounce">
                <Dna className="h-8 w-8 text-[#22C55E] group-hover:text-[#06B6D4] transition-colors duration-300 drop-shadow-[0_0_10px_rgba(34,197,94,0.9)] group-hover:drop-shadow-[0_0_18px_rgba(6,182,212,1)]" />
            </div>
        </button>
    );
}
