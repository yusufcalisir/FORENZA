"use client";

import { motion } from "framer-motion";
import { ShieldCheck, Lock, Binary, Cpu } from "lucide-react";

export default function CryptographicShield({ active }: { active: boolean }) {
  if (!active) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[99999] bg-black/85 backdrop-blur-md flex items-center justify-center p-4 font-mono select-none"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="flex flex-col items-center justify-center max-w-md w-full text-center p-6 sm:p-8 rounded-2xl bg-[#070D18]/90 border border-emerald-500/40 shadow-[0_0_50px_rgba(16,185,129,0.2)]"
      >
        {/* Animated Gyroscope Rings */}
        <div className="relative w-36 h-36 flex items-center justify-center mb-6">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
            className="w-36 h-36 rounded-full border-2 border-dashed border-emerald-500/30 border-t-emerald-400 absolute"
          />

          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 6, repeat: Infinity, ease: "linear" }}
            className="w-28 h-28 rounded-full border border-emerald-400/20 border-b-cyan-400 absolute"
          />

          <motion.div
            animate={{ scale: [1, 1.08, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/40 flex items-center justify-center shadow-lg shadow-emerald-500/20 z-10"
          >
            <ShieldCheck className="w-8 h-8 text-emerald-400" />
          </motion.div>
        </div>

        {/* Title */}
        <h3 className="text-base sm:text-lg font-extrabold tracking-widest text-emerald-400 uppercase">
          Zero-Knowledge Proof Active
        </h3>

        {/* Description */}
        <p className="mt-2 text-zinc-400 text-xs leading-relaxed max-w-sm">
          Synthesizing Circom / Groth16 BN254 mathematical witness. Raw DNA STR/SNP markers remain encrypted client-side.
        </p>

        {/* Live Cryptographic Status Badges */}
        <div className="mt-5 w-full grid grid-cols-2 gap-2 text-[10px]">
          <div className="p-2 rounded-xl bg-black/60 border border-tactical-border/60 flex items-center justify-center gap-1.5 text-zinc-300">
            <Binary className="w-3 h-3 text-cyan-400" />
            <span>BN254 Pairings</span>
          </div>
          <div className="p-2 rounded-xl bg-black/60 border border-tactical-border/60 flex items-center justify-center gap-1.5 text-zinc-300">
            <Cpu className="w-3 h-3 text-emerald-400" />
            <span>Client-Side Prover</span>
          </div>
        </div>

        {/* Bottom Tag */}
        <div className="mt-4 flex items-center justify-center gap-1.5 text-[9px] text-zinc-500 font-bold uppercase tracking-wider">
          <Lock className="w-3 h-3 text-emerald-400" />
          <span>ISO/IEC 17025:2017 Cryptographic Isolation</span>
        </div>
      </motion.div>
    </motion.div>
  );
}
