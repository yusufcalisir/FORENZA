"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Zap } from "lucide-react";
import DnaLaunchTransition from "@/components/common/DnaLaunchTransition";

export default function LaunchDemoButton({
    size = "md",
    className = "",
    label = "Launch Demo",
}: {
    size?: "sm" | "md" | "lg";
    className?: string;
    label?: string;
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
                className={`group relative inline-flex items-center justify-center p-0.5 overflow-hidden rounded-xl font-bold tracking-wider transition-all duration-300 shadow-[0_0_25px_rgba(34,197,94,0.25)] hover:shadow-[0_0_35px_rgba(34,197,94,0.5)] hover:scale-[1.02] cursor-pointer ${className}`}
            >
                {/* Gradient Border Ring */}
                <span className="absolute inset-0 bg-gradient-to-r from-[#22C55E] via-[#06B6D4] to-[#8B5CF6] group-hover:opacity-100 transition-opacity duration-300" />

                {/* Inner Button Container */}
                <span
                    className={`relative flex items-center justify-center gap-2.5 rounded-[10px] bg-[#0A0A0B] group-hover:bg-[#22C55E] ${sizeClasses} text-white group-hover:text-black transition-all duration-300 w-full h-full`}
                >
                    <Zap className="h-4 w-4 text-[#22C55E] group-hover:text-black transition-colors shrink-0" />
                    <span className="whitespace-nowrap">{label}</span>
                </span>
            </button>
        </>
    );
}
