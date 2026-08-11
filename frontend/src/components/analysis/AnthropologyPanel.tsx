"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Bone, UserCheck, ShieldAlert, FileText, CheckCircle2, ChevronRight, Activity, Cpu, Compass } from "lucide-react";

export default function AnthropologyPanel() {
  const [activeSubTab, setActiveSubTab] = useState<"profile" | "trauma">("profile");

  // Mock Morphometrics & Profile Data
  const [femurLength, setFemurLength] = useState<number>(445.0);
  const [subpubicAngle, setSubpubicAngle] = useState<number>(95.0);
  const [symphysisPhase, setSymphysisPhase] = useState<number>(3);

  // Trotter-Gleser Calculation: Stature = 2.38 * (femur_mm / 10) + 61.41 +/- 3.27 cm
  const femurCm = femurLength / 10.0;
  const estimatedStature = (2.38 * femurCm + 61.41).toFixed(1);
  const minStature = (parseFloat(estimatedStature) - 3.27).toFixed(1);
  const maxStature = (parseFloat(estimatedStature) + 3.27).toFixed(1);

  const estimatedSex = subpubicAngle > 85.0 ? "FEMALE (Subpubic Angle > 85°)" : "MALE (Subpubic Angle < 75°)";
  const ageRange = symphysisPhase === 1 ? "15–19 yrs" : symphysisPhase === 2 ? "20–24 yrs" : symphysisPhase === 3 ? "25–34 yrs" : symphysisPhase === 4 ? "35–45 yrs" : "46+ yrs";

  // Mock Trauma Observations
  const traumaList = [
    { element: "Left Femur", mechanism: "BLUNT_FORCE", timing: "PERIMORTEM", desc: "Radiating linear fracture on distal shaft with sharp unhealed margins" },
    { element: "Right Tibia", mechanism: "TAPHONOMIC", timing: "POSTMORTEM", desc: "Sun bleaching, cortical flaking, and soil mineral staining" },
    { element: "Frontal Bone", mechanism: "BALLISTIC", timing: "PERIMORTEM", desc: "Circular entry defect with internal beveling" },
  ];

  return (
    <div className="space-y-6 font-mono">
      {/* ── Top Header Strip ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.15)]">
            <Bone className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              Forensic Anthropology & Biological Profiling Hub
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              Osteological Morphometrics • Trotter-Gleser Stature • Suchey-Brooks Age • Perimortem Trauma Audit
            </p>
          </div>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-tactical-border/60">
          <button
            onClick={() => setActiveSubTab("profile")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "profile" ? "bg-purple-500/20 text-purple-300 border border-purple-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Biological Profile
          </button>
          <button
            onClick={() => setActiveSubTab("trauma")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-all ${
              activeSubTab === "trauma" ? "bg-purple-500/20 text-purple-300 border border-purple-500/40" : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Trauma & Taphonomy
          </button>
        </div>
      </div>

      {/* ── Sub-tab 1: Biological Profile ── */}
      {activeSubTab === "profile" && (
        <div className="space-y-6">
          {/* Controls & Interactive Sliders */}
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-5 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Osteological Morphometrics Input Panel
              </span>
              <span className="text-[9px] text-purple-400 font-bold bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                Trotter-Gleser Active
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Femur Slider */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-zinc-400">Femur Length (mm):</span>
                  <span className="text-purple-400 font-bold">{femurLength} mm</span>
                </div>
                <input
                  type="range"
                  min={350}
                  max={520}
                  step={1}
                  value={femurLength}
                  onChange={(e) => setFemurLength(parseFloat(e.target.value))}
                  className="w-full accent-purple-500 bg-black/40 h-2 rounded-lg cursor-pointer"
                />
              </div>

              {/* Subpubic Angle Slider */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-zinc-400">Subpubic Angle (°):</span>
                  <span className="text-purple-400 font-bold">{subpubicAngle}°</span>
                </div>
                <input
                  type="range"
                  min={60}
                  max={120}
                  step={1}
                  value={subpubicAngle}
                  onChange={(e) => setSubpubicAngle(parseFloat(e.target.value))}
                  className="w-full accent-purple-500 bg-black/40 h-2 rounded-lg cursor-pointer"
                />
              </div>

              {/* Pubic Symphysis Phase */}
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-zinc-400">Suchey-Brooks Phase:</span>
                  <span className="text-purple-400 font-bold">Phase {symphysisPhase}</span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={5}
                  step={1}
                  value={symphysisPhase}
                  onChange={(e) => setSymphysisPhase(parseInt(e.target.value))}
                  className="w-full accent-purple-500 bg-black/40 h-2 rounded-lg cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Biological Profile Summary Result Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Sex Estimation</span>
              <p className="text-sm font-bold text-purple-400 font-mono">{estimatedSex}</p>
              <p className="text-[9px] text-zinc-400">Morphometric pelvic metric</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Suchey-Brooks Age</span>
              <p className="text-sm font-bold text-amber-400 font-mono">{ageRange}</p>
              <p className="text-[9px] text-zinc-400">Pubic symphysis metamorphology</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Estimated Stature</span>
              <p className="text-sm font-bold text-emerald-400 font-mono">{estimatedStature} cm</p>
              <p className="text-[9px] text-zinc-400">Range: {minStature} – {maxStature} cm (95% CI)</p>
            </div>
            <div className="rounded-xl border border-tactical-border/60 bg-tactical-surface/40 p-4 space-y-1">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">Population Affinity</span>
              <p className="text-sm font-bold text-cyan-400 font-mono">European / Mesocephalic</p>
              <p className="text-[9px] text-zinc-400">Craniometric Index: 76.5</p>
            </div>
          </div>
        </div>
      )}

      {/* ── Sub-tab 2: Trauma & Taphonomy ── */}
      {activeSubTab === "trauma" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 space-y-4 shadow-lg">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <span className="text-xs font-bold text-tactical-text uppercase tracking-wider">
                Skeletal Trauma & Perimortem Lesion Audit Log
              </span>
              <span className="text-[9px] text-red-400 font-bold bg-red-500/10 border border-red-500/20 px-2 py-0.5 rounded">
                2 Perimortem Fractures Documented
              </span>
            </div>

            <div className="space-y-3">
              {traumaList.map((t, idx) => (
                <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-black/20 border border-tactical-border/40 gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs font-bold font-mono">
                      <span className="text-purple-300">{t.element}</span>
                      <span className="text-zinc-600">•</span>
                      <span className="text-amber-400">{t.mechanism}</span>
                    </div>
                    <p className="text-[10px] text-zinc-400">{t.desc}</p>
                  </div>

                  <div>
                    <span className={`px-3 py-1 rounded text-[9px] font-bold uppercase font-mono ${
                      t.timing === "PERIMORTEM"
                        ? "bg-red-500/20 text-red-400 border border-red-500/30"
                        : "bg-zinc-500/20 text-zinc-400 border border-zinc-500/30"
                    }`}>
                      {t.timing}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
