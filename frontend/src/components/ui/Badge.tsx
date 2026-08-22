"use client";

import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 font-mono font-bold uppercase tracking-wider rounded-md select-none transition-colors",
  {
    variants: {
      variant: {
        emerald: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30",
        cyan: "bg-cyan-500/10 text-cyan-300 border border-cyan-500/30",
        amber: "bg-amber-500/10 text-amber-300 border border-amber-500/30",
        rose: "bg-rose-500/10 text-rose-300 border border-rose-500/30",
        purple: "bg-purple-500/10 text-purple-300 border border-purple-500/30",
        zinc: "bg-zinc-800/80 text-zinc-400 border border-zinc-700/60",
      },
      size: {
        xs: "px-1.5 py-0.5 text-[8px]",
        sm: "px-2 py-0.5 text-[9px]",
        md: "px-2.5 py-1 text-[10px]",
      },
      glow: {
        true: "shadow-[0_0_10px_currentColor]",
        false: "",
      },
    },
    defaultVariants: {
      variant: "emerald",
      size: "sm",
      glow: false,
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean;
  pulse?: boolean;
  icon?: React.ReactNode;
}

export function Badge({
  className,
  variant,
  size,
  glow,
  dot = false,
  pulse = false,
  icon,
  children,
  ...props
}: BadgeProps) {
  const dotColor = {
    emerald: "bg-emerald-400",
    cyan: "bg-cyan-400",
    amber: "bg-amber-400",
    rose: "bg-rose-400",
    purple: "bg-purple-400",
    zinc: "bg-zinc-400",
  }[variant || "emerald"];

  return (
    <span className={cn(badgeVariants({ variant, size, glow, className }))} {...props}>
      {dot && (
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full shrink-0",
            dotColor,
            pulse && "animate-pulse"
          )}
        />
      )}
      {icon && <span className="shrink-0">{icon}</span>}
      <span className="truncate">{children}</span>
    </span>
  );
}
