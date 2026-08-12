"use client";

import { LucideIcon } from "lucide-react";

interface SectionBadgeProps {
    icon: LucideIcon;
    label: string;
    color?: "emerald" | "cyan" | "purple" | "amber";
    className?: string;
}

export default function SectionBadge({
    icon: Icon,
    label,
    color = "emerald",
    className = "",
}: SectionBadgeProps) {
    const colorStyles = {
        emerald: "border-emerald-500/35 bg-emerald-500/10 text-emerald-300 shadow-emerald-500/10",
        cyan: "border-cyan-500/35 bg-cyan-500/10 text-cyan-300 shadow-cyan-500/10",
        purple: "border-purple-500/35 bg-purple-500/10 text-purple-300 shadow-purple-500/10",
        amber: "border-amber-500/35 bg-amber-500/10 text-amber-300 shadow-amber-500/10",
    }[color];

    const iconColors = {
        emerald: "text-emerald-400",
        cyan: "text-cyan-400",
        purple: "text-purple-400",
        amber: "text-amber-400",
    }[color];

    return (
        <div className={`inline-flex items-center justify-center gap-2 px-3.5 py-1.5 rounded-full border backdrop-blur-md shadow-md max-w-full ${colorStyles} ${className}`}>
            <Icon className={`w-3.5 h-3.5 shrink-0 ${iconColors}`} />
            <span className="font-mono text-[10px] sm:text-xs font-bold uppercase tracking-wider leading-none text-center">
                {label}
            </span>
        </div>
    );
}
