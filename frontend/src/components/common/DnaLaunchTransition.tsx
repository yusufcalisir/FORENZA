"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, CheckCircle2 } from "lucide-react";
import ForenzaLogoIcon from "@/components/common/ForenzaLogoIcon";

interface DnaLaunchTransitionProps {
  onComplete?: () => void;
  autoStart?: boolean;
}

export default function DnaLaunchTransition({ onComplete, autoStart = true }: DnaLaunchTransitionProps) {
  const [isVisible, setIsVisible] = useState(autoStart);
  const [step, setStep] = useState(0);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const steps = [
    "INITIALIZING FORENZA BIOLOGICAL KERNEL...",
    "CALIBRATING 24 CODIS CORE STR LOCI...",
    "LOADING HIrisPlex-S & BGA POPULATION PRIORS...",
    "VERIFYING ISO-21043 CHAIN OF CUSTODY LEDGER...",
    "SYSTEM OPERATIONAL — FORENSIC WORKSPACE READY"
  ];

  useEffect(() => {
    if (!isVisible) return;

    const interval = setInterval(() => {
      setStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        }
        clearInterval(interval);
        setTimeout(() => {
          setIsVisible(false);
          if (onComplete) onComplete();
        }, 600);
        return prev;
      });
    }, 450);

    return () => clearInterval(interval);
  }, [isVisible, onComplete]);

  if (!isVisible || !mounted) return null;

  const content = (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
        className="fixed inset-0 z-[99999] flex flex-col items-center justify-center bg-[#030712] font-mono text-tactical-text selection:bg-cyan-500/30 overflow-hidden"
      >
        {/* Futuristic Background Grid */}
        <div
          className="absolute inset-0 opacity-20 pointer-events-none"
          style={{
            backgroundImage: `linear-gradient(#06B6D4 1px, transparent 1px), linear-gradient(90deg, #06B6D4 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />

        {/* Ambient Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none" />

        <div className="relative z-10 flex flex-col items-center max-w-md w-full px-6 text-center space-y-6">
          {/* Animated DNA Icon */}
          <div className="relative flex items-center justify-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
              className="w-24 h-24 rounded-full border border-dashed border-emerald-500/40 flex items-center justify-center"
            />
            <motion.div
              animate={{ scale: [0.95, 1.05, 0.95] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <ForenzaLogoIcon size={56} className="drop-shadow-[0_0_20px_rgba(16,185,129,0.8)]" />
            </motion.div>
          </div>

          {/* Branding Title */}
          <div className="space-y-1">
            <h1 className="text-xl font-black tracking-[0.3em] uppercase text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
              FORENZA OS
            </h1>
            <p className="text-[10px] text-zinc-400 uppercase tracking-widest font-bold">
              Forensic Biology &amp; DNA Intelligence Operating System
            </p>
          </div>

          {/* Progress Bar */}
          <div className="w-full space-y-2">
            <div className="w-full bg-black border border-tactical-border h-2.5 rounded-full overflow-hidden p-0.5">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 shadow-[0_0_12px_rgba(16,185,129,0.8)]"
                initial={{ width: "0%" }}
                animate={{ width: `${((step + 1) / steps.length) * 100}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>

            <div className="flex items-center justify-between text-[10px] text-zinc-400 font-mono">
              <span className="flex items-center gap-1.5 text-emerald-300 font-bold">
                <Activity className="w-3.5 h-3.5 animate-pulse text-emerald-400" />
                {steps[step]}
              </span>
              <span className="font-extrabold text-emerald-400">{Math.round(((step + 1) / steps.length) * 100)}%</span>
            </div>
          </div>

          {/* Subsystem Readiness Checklist */}
          <div className="grid grid-cols-2 gap-2.5 text-[10px] w-full text-left pt-3 border-t border-tactical-border/50">
            <div className="flex items-center gap-1.5 text-zinc-300 font-medium">
              <CheckCircle2 className={`w-3.5 h-3.5 ${step >= 0 ? "text-emerald-400" : "text-zinc-700"}`} />
              <span>Autosomal STR Engine</span>
            </div>
            <div className="flex items-center gap-1.5 text-zinc-300 font-medium">
              <CheckCircle2 className={`w-3.5 h-3.5 ${step >= 1 ? "text-emerald-400" : "text-zinc-700"}`} />
              <span>MCMC Genotyping</span>
            </div>
            <div className="flex items-center gap-1.5 text-zinc-300 font-medium">
              <CheckCircle2 className={`w-3.5 h-3.5 ${step >= 2 ? "text-emerald-400" : "text-zinc-700"}`} />
              <span>HIrisPlex-S EVC</span>
            </div>
            <div className="flex items-center gap-1.5 text-zinc-300 font-medium">
              <CheckCircle2 className={`w-3.5 h-3.5 ${step >= 3 ? "text-emerald-400" : "text-zinc-700"}`} />
              <span>ISO 21043 Ledger</span>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );

  return createPortal(content, document.body);
}
