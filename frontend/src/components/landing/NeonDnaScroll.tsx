"use client";

import { ChevronDown } from "lucide-react";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";

export default function NeonDnaScroll({ targetId }: { targetId: string }) {
    const handleClick = (e: React.MouseEvent) => {
        e.preventDefault();
        const el = document.getElementById(targetId);
        if (el) {
            const headerOffset = 70;
            const elementPosition = el.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        }
    };

    return (
        <button
            onClick={handleClick}
            type="button"
            aria-label="Scroll to next section"
            className="hidden sm:flex flex-col items-center justify-center cursor-pointer group py-4 transition-all duration-300 hover:scale-105 focus:outline-none mx-auto"
        >
            <div className="relative flex flex-col items-center gap-1.5 p-2 rounded-2xl bg-black/40 border border-emerald-500/20 hover:border-emerald-500/50 hover:bg-black/60 shadow-lg shadow-emerald-500/5 transition-all">
                <ForenzaLogoIcon size={24} className="group-hover:rotate-12 transition-transform duration-300" />
                <ChevronDown className="w-4 h-4 text-emerald-400 animate-bounce" />
            </div>
        </button>
    );
}
