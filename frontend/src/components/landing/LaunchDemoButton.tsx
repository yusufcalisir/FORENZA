"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Zap } from "lucide-react";
import DnaLaunchTransition from "@/components/common/DnaLaunchTransition";

export default function LaunchDemoButton({
    size = "md",
    className = "",
    label = "Launch Demo OS",
    compactMobile = false,
}: {
    size?: "sm" | "md" | "lg";
    className?: string;
    label?: string;
    compactMobile?: boolean;
}) {
    const router = useRouter();
    const [isTransitioning, setIsTransitioning] = useState(false);

    const sizeClasses = {
        sm: "px-3.5 py-1.5 font-mono text-[10px]",
        md: "px-5 py-2.5 font-mono text-xs",
        lg: "px-7 py-3.5 font-mono text-sm",
    }[size];

    const handleClick = () => {
        setIsTransitioning(true);
        router.prefetch("/dashboard");
    };

    const handleTransitionComplete = () => {
        router.push("/dashboard");
    };

    return (
        <>
            {isTransitioning && (
                <DnaLaunchTransition onComplete={handleTransitionComplete} autoStart={true} />
            )}

            <button
                type="button"
                onClick={handleClick}
                aria-label={label}
                title={label}
                className={`group relative inline-flex items-center justify-center gap-1.5 sm:gap-2 font-mono font-bold tracking-wider transition-all duration-300 rounded-xl bg-tactical-surface/90 hover:bg-emerald-500/10 text-emerald-400 border border-emerald-500/40 hover:border-emerald-400/80 shadow-[0_0_15px_rgba(16,185,129,0.15)] hover:shadow-[0_0_25px_rgba(16,185,129,0.3)] hover:scale-[1.02] active:scale-[0.98] cursor-pointer ${
                    compactMobile
                        ? "p-2 sm:px-3.5 sm:py-1.5 font-mono text-[10px]"
                        : sizeClasses
                } ${className}`}
            >
                <Zap className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-emerald-400 fill-emerald-400/20 shrink-0 transition-transform group-hover:scale-110" />
                <span className={`whitespace-nowrap uppercase tracking-wider ${compactMobile ? "hidden sm:inline" : ""}`}>
                    {label}
                </span>
            </button>
        </>
    );
}
