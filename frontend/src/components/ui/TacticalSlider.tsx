"use client";

import React, { forwardRef } from "react";
import { cn } from "@/lib/utils";

export interface TacticalSliderProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange"> {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  accentColor?: "emerald" | "cyan" | "purple" | "amber";
  onChange: (value: number) => void;
  description?: string;
  formatValue?: (val: number) => string;
}

export const TacticalSlider = forwardRef<HTMLInputElement, TacticalSliderProps>(
  (
    {
      className,
      label,
      value,
      min,
      max,
      step = 0.01,
      unit = "",
      accentColor = "emerald",
      onChange,
      description,
      formatValue,
      disabled,
      ...props
    },
    ref
  ) => {
    const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));

    const colorConfig = {
      emerald: {
        track: "bg-emerald-500",
        thumb: "border-emerald-400 focus-visible:ring-emerald-400/50",
        badge: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
      },
      cyan: {
        track: "bg-cyan-500",
        thumb: "border-cyan-400 focus-visible:ring-cyan-400/50",
        badge: "bg-cyan-500/10 text-cyan-300 border-cyan-500/30",
      },
      purple: {
        track: "bg-purple-500",
        thumb: "border-purple-400 focus-visible:ring-purple-400/50",
        badge: "bg-purple-500/10 text-purple-300 border-purple-500/30",
      },
      amber: {
        track: "bg-amber-500",
        thumb: "border-amber-400 focus-visible:ring-amber-400/50",
        badge: "bg-amber-500/10 text-amber-300 border-amber-500/30",
      },
    }[accentColor];

    const displayVal = formatValue ? formatValue(value) : value.toString();

    return (
      <div className={cn("w-full space-y-2 text-left select-none", className)}>
        {/* Header: Label & Value Badge */}
        <div className="flex justify-between items-center">
          <label className="text-[11px] font-mono font-bold uppercase tracking-wider text-zinc-300">
            {label}
          </label>
          <span
            className={cn(
              "font-mono text-xs font-bold px-2 py-0.5 rounded-md border tabular-nums shadow-sm",
              colorConfig.badge
            )}
          >
            {displayVal} {unit}
          </span>
        </div>

        {description && (
          <p className="text-[10px] text-zinc-500 font-mono leading-relaxed">{description}</p>
        )}

        {/* Custom Range Slider Track */}
        <div className="relative flex items-center w-full h-6">
          {/* Base background bar */}
          <div className="absolute w-full h-1.5 rounded-full bg-zinc-800 border border-tactical-border/60" />

          {/* Filled progress bar */}
          <div
            className={cn("absolute h-1.5 rounded-full transition-all duration-75", colorConfig.track)}
            style={{ width: `${percentage}%` }}
          />

          {/* Native range input for accessible dragging */}
          <input
            ref={ref}
            type="range"
            min={min}
            max={max}
            step={step}
            value={value}
            disabled={disabled}
            aria-label={label}
            aria-valuenow={value}
            aria-valuemin={min}
            aria-valuemax={max}
            aria-valuetext={`${displayVal} ${unit}`}
            onChange={(e) => onChange(parseFloat(e.target.value))}
            className="absolute w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed z-10"
            {...props}
          />

          {/* Visual Custom Thumb Knob */}
          <div
            className={cn(
              "absolute w-4 h-4 rounded-full bg-black border-2 shadow-lg transition-transform duration-75 pointer-events-none -translate-x-1/2",
              colorConfig.thumb
            )}
            style={{ left: `${percentage}%` }}
          />
        </div>

        {/* Min / Max Labels */}
        <div className="flex justify-between text-[9px] font-mono text-zinc-600 tabular-nums">
          <span>{min} {unit}</span>
          <span>{max} {unit}</span>
        </div>
      </div>
    );
  }
);

TacticalSlider.displayName = "TacticalSlider";
