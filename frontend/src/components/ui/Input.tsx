"use client";

import React, { forwardRef } from "react";
import { X, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  prefixElement?: React.ReactNode;
  suffixElement?: React.ReactNode;
  onClear?: () => void;
  monospace?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = "text",
      label,
      error,
      helperText,
      prefixElement,
      suffixElement,
      onClear,
      value,
      disabled,
      monospace = true,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || (label ? `input-${label.toLowerCase().replace(/\s+/g, "-")}` : undefined);
    const hasValue = value !== undefined && value !== "" && value !== null;

    return (
      <div className="w-full space-y-1.5 text-left">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-[11px] font-mono font-bold uppercase tracking-wider text-zinc-400"
          >
            {label}
          </label>
        )}

        <div className="relative flex items-center w-full">
          {prefixElement && (
            <div className="absolute left-3 flex items-center text-zinc-500 pointer-events-none text-xs font-mono">
              {prefixElement}
            </div>
          )}

          <input
            id={inputId}
            ref={ref}
            type={type}
            value={value}
            disabled={disabled}
            className={cn(
              "w-full rounded-xl bg-black/50 border text-xs text-white placeholder-zinc-600 transition-all duration-200 focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed",
              monospace ? "font-mono tabular-nums" : "font-sans",
              prefixElement ? "pl-9" : "pl-3.5",
              suffixElement || onClear ? "pr-9" : "pr-3.5",
              "py-2.5",
              error
                ? "border-rose-500/60 focus:border-rose-400 focus:ring-rose-500/30 text-rose-200"
                : "border-tactical-border/70 focus:border-emerald-500/60 focus:ring-emerald-500/20",
              className
            )}
            {...props}
          />

          <div className="absolute right-3 flex items-center gap-1.5">
            {onClear && hasValue && !disabled && (
              <button
                type="button"
                onClick={onClear}
                aria-label="Clear input"
                className="text-zinc-500 hover:text-zinc-300 p-0.5 rounded transition-colors cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}

            {suffixElement && (
              <div className="text-zinc-500 text-xs font-mono pointer-events-none">
                {suffixElement}
              </div>
            )}
          </div>
        </div>

        {error ? (
          <div className="flex items-center gap-1 text-[10px] text-rose-400 font-mono">
            <AlertCircle className="w-3 h-3 shrink-0" />
            <span>{error}</span>
          </div>
        ) : helperText ? (
          <p className="text-[10px] text-zinc-500 font-mono">{helperText}</p>
        ) : null}
      </div>
    );
  }
);

Input.displayName = "Input";
