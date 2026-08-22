"use client";

import React, { forwardRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center font-mono font-bold tracking-wider rounded-xl transition-all duration-200 cursor-pointer select-none disabled:opacity-50 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/80 focus-visible:ring-offset-2 focus-visible:ring-offset-black",
  {
    variants: {
      variant: {
        primary:
          "bg-emerald-500 hover:bg-emerald-400 text-black border border-emerald-400/50 shadow-[0_0_15px_rgba(16,185,129,0.25)] hover:shadow-[0_0_25px_rgba(16,185,129,0.4)] active:scale-[0.98]",
        secondary:
          "bg-tactical-surface/90 hover:bg-zinc-800 text-zinc-200 border border-tactical-border/80 hover:border-zinc-500 shadow-sm active:scale-[0.98]",
        cyan:
          "bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/50 shadow-[0_0_15px_rgba(6,182,212,0.2)] active:scale-[0.98]",
        danger:
          "bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/50 shadow-[0_0_15px_rgba(244,63,94,0.2)] active:scale-[0.98]",
        ghost:
          "bg-transparent hover:bg-white/5 text-zinc-400 hover:text-zinc-200 border border-transparent active:scale-[0.98]",
        glass:
          "bg-black/40 hover:bg-black/60 text-zinc-300 border border-tactical-border/60 backdrop-blur-md active:scale-[0.98]",
      },
      size: {
        xs: "px-2.5 py-1 text-[10px] gap-1",
        sm: "px-3.5 py-1.5 text-xs gap-1.5",
        md: "px-4 py-2.5 text-xs gap-2 min-h-[38px]",
        lg: "px-6 py-3.5 text-sm gap-2.5 min-h-[44px]",
        icon: "p-2 min-h-[36px] min-w-[36px]",
      },
      fullWidth: {
        true: "w-full",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
      fullWidth: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      fullWidth,
      loading = false,
      disabled,
      leftIcon,
      rightIcon,
      children,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        aria-busy={loading}
        className={cn(buttonVariants({ variant, size, fullWidth, className }))}
        {...props}
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin shrink-0" />
        ) : (
          leftIcon && <span className="shrink-0">{leftIcon}</span>
        )}
        {children && <span className="truncate">{children}</span>}
        {!loading && rightIcon && <span className="shrink-0">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = "Button";
