"use client";

import { useEffect } from "react";
import { AlertOctagon, RotateCcw } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[FORENZA Global Fatal Exception]", error);
  }, [error]);

  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#070D18] text-white flex items-center justify-center p-4 font-sans">
        <div className="w-full max-w-lg p-6 sm:p-8 rounded-2xl bg-zinc-900 border border-rose-500/50 shadow-2xl flex flex-col items-center text-center space-y-5">
          <div className="w-14 h-14 rounded-2xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400">
            <AlertOctagon className="w-7 h-7" />
          </div>

          <div className="space-y-1.5">
            <h1 className="text-xl font-bold tracking-tight">FORENZA Kernel Fatal Halt</h1>
            <p className="text-xs text-zinc-400 leading-relaxed">
              A critical layout exception was caught. Emergency memory containment is active.
            </p>
          </div>

          <button
            type="button"
            onClick={() => reset()}
            className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-mono font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Restart Kernel Session</span>
          </button>
        </div>
      </body>
    </html>
  );
}
