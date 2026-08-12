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
                className={`group relative inline-flex items-center justify-center font-extrabold tracking-wider transition-all duration-300 rounded-xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-black shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40 hover:scale-[1.02] active:scale-[0.98] cursor-pointer border border-emerald-400/50 ${
                    compactMobile
                        ? "p-2 sm:px-3.5 sm:py-1.5 font-mono text-[10px]"
                        : sizeClasses
                } ${className}`}
            >
                <Zap className="h-4 w-4 text-black fill-black shrink-0 transition-transform group-hover:scale-110" />
                <span className={`whitespace-nowrap uppercase tracking-wider ${compactMobile ? "hidden sm:inline" : ""}`}>
                    {label}
                </span>
            </button>
        </>
    );
}
