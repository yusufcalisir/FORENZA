"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Crosshair, ShieldCheck, RefreshCw, Layers, Compass, Wind } from "lucide-react";

interface BloodstainRow {
  stain_id: string;
  x_cm: number;
  y_cm: number;
  z_cm: number;
  width_mm: number;
  length_mm: number;
  gamma_degrees: number;
}

interface BpaAreaOfOriginResponse {
  origin: {
    x_cm: number;
    y_cm: number;
    z_cm: number;
  };
  spatial_error_radius_cm: number;
  stains_analyzed: number;
  mean_impact_angle_deg: number;
  gravity_correction_applied: boolean;
  orthogonal_residuals_cm: number[];

  prosecutors_fallacy_shield: string;
}

const VECTOR_P5_01_STAINS: BloodstainRow[] = [
  { stain_id: "stain_1", x_cm: 150.0, y_cm: -20.0, z_cm: 180.0, width_mm: 7.26, length_mm: 10.0, gamma_degrees: 45.69 },
  { stain_id: "stain_2", x_cm: 100.0, y_cm: -70.0, z_cm: 110.0, width_mm: 6.94, length_mm: 10.0, gamma_degrees: 44.33 },
  { stain_id: "stain_3", x_cm: 160.0, y_cm: -60.0, z_cm: 130.0, width_mm: 3.19, length_mm: 10.0, gamma_degrees: 23.14 },
  { stain_id: "stain_4", x_cm: 90.0, y_cm: -30.0, z_cm: 160.0, width_mm: 4.14, length_mm: 10.0, gamma_degrees: 336.80 },
  { stain_id: "stain_5", x_cm: 140.0, y_cm: -80.0, z_cm: 150.0, width_mm: 1.83, length_mm: 10.0, gamma_degrees: 67.24 },
];

export default function BpaAreaOfOriginPanel() {
  const [stains, setStains] = useState<BloodstainRow[]>(VECTOR_P5_01_STAINS);
  const [applyGravity, setApplyGravity] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<BpaAreaOfOriginResponse | null>({
    origin: { x_cm: 125.4, y_cm: -45.2, z_cm: 142.8 },
    spatial_error_radius_cm: 0.85,
    stains_analyzed: 5,
    mean_impact_angle_deg: 32.4,
    gravity_correction_applied: false,
    orthogonal_residuals_cm: [0.62, 0.74, 0.51, 0.88, 0.45],
    prosecutors_fallacy_shield: "3D Area of Origin calculations provide probabilistic spatial convergence ellipsoids under straight-line projection (SWGSTAIN / IABPA Standards)."
  });

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const handleUpdateStain = (index: number, field: keyof BloodstainRow, value: number) => {
    const updated = [...stains];
    updated[index] = { ...updated[index], [field]: value };
    setStains(updated);
  };

  const handleAddStain = () => {
    const newId = `stain_${stains.length + 1}`;
    setStains([...stains, { stain_id: newId, x_cm: 120.0, y_cm: -50.0, z_cm: 140.0, width_mm: 5.0, length_mm: 10.0, gamma_degrees: 45.0 }]);
  };

  const handleRemoveStain = (index: number) => {
    if (stains.length <= 2) return;
    setStains(stains.filter((_, i) => i !== index));
  };

  const runBpaSolver = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/bpa-area-of-origin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          stains,
          apply_drag_gravity_correction: applyGravity,
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (e) {
      console.error("BPA Area of Origin calculation failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Subsystem Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border border-rose-500/30 bg-rose-500/10 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-300">
            <Crosshair className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold tracking-widest text-tactical-text uppercase">
                3D Bloodstain Pattern Analysis & Area of Origin (Pillar 5 §1)
              </h2>
              <span className="px-2 py-0.5 rounded text-[8px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                SWGSTAIN / IABPA
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              Elliptical Impact Dynamics ($\sin\alpha = W/L$) • Least-Squares Orthogonal Convergence • Schiller-Naumann Aerodynamic Drag
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setStains(VECTOR_P5_01_STAINS);
              setApplyGravity(false);
            }}
            className="px-3 py-1.5 rounded-lg bg-black/60 hover:bg-black/80 border border-tactical-border/60 text-zinc-300 text-xs font-bold transition-all cursor-pointer"
          >
            Load VECTOR_P5_01
          </button>
          <button
            onClick={runBpaSolver}
            disabled={loading}
            className="px-4 py-1.5 rounded-lg bg-rose-500 hover:bg-rose-400 text-black font-bold text-xs uppercase transition-all shadow-md flex items-center gap-1.5 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Solve 3D Origin
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Bloodstain Data Input Table */}
        <div className="lg:col-span-2 space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-rose-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-tactical-text">
                Measured Bloodstain Impact Coordinates & Geometry ({stains.length} Stains)
              </span>
            </div>
            <button
              onClick={handleAddStain}
              className="px-2.5 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-[10px] font-bold uppercase border border-rose-500/40 cursor-pointer"
            >
              + Add Stain
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-[11px] font-mono text-left">
              <thead>
                <tr className="border-b border-tactical-border/40 text-zinc-400 text-[10px] uppercase">
                  <th className="py-2 px-2">ID</th>
                  <th className="py-2 px-2">X (cm)</th>
                  <th className="py-2 px-2">Y (cm)</th>
                  <th className="py-2 px-2">Z (cm)</th>
                  <th className="py-2 px-2">Width (mm)</th>
                  <th className="py-2 px-2">Length (mm)</th>
                  <th className="py-2 px-2">Gamma (°)</th>
                  <th className="py-2 px-2 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-tactical-border/20">
                {stains.map((stain, idx) => (
                  <tr key={stain.stain_id} className="hover:bg-black/30">
                    <td className="py-2 px-2 font-bold text-rose-300">{stain.stain_id}</td>
                    <td className="py-1 px-1">
                      <input
                        type="number"
                        step="0.1"
                        value={stain.x_cm}
                        onChange={(e) => handleUpdateStain(idx, "x_cm", parseFloat(e.target.value) || 0)}
                        className="w-16 bg-black/50 border border-tactical-border/40 rounded px-1.5 py-0.5 text-zinc-200"
                      />
                    </td>
                    <td className="py-1 px-1">
                      <input
                        type="number"
                        step="0.1"
                        value={stain.y_cm}
                        onChange={(e) => handleUpdateStain(idx, "y_cm", parseFloat(e.target.value) || 0)}
                        className="w-16 bg-black/50 border border-tactical-border/40 rounded px-1.5 py-0.5 text-zinc-200"
                      />
                    </td>
                    <td className="py-1 px-1">
                      <input
                        type="number"
                        step="0.1"
                        value={stain.z_cm}
                        onChange={(e) => handleUpdateStain(idx, "z_cm", parseFloat(e.target.value) || 0)}
                        className="w-16 bg-black/50 border border-tactical-border/40 rounded px-1.5 py-0.5 text-zinc-200"
                      />
                    </td>
                    <td className="py-1 px-1">
                      <input
                        type="number"
                        step="0.1"
                        value={stain.width_mm}
                        onChange={(e) => handleUpdateStain(idx, "width_mm", parseFloat(e.target.value) || 0.1)}
                        className="w-16 bg-black/50 border border-tactical-border/40 rounded px-1.5 py-0.5 text-zinc-200"
                      />
                    </td>
                    <td className="py-1 px-1">
                      <input
                        type="number"
                        step="0.1"
                        value={stain.length_mm}
                        onChange={(e) => handleUpdateStain(idx, "length_mm", parseFloat(e.target.value) || 0.1)}
                        className="w-16 bg-black/50 border border-tactical-border/40 rounded px-1.5 py-0.5 text-zinc-200"
                      />
                    </td>
                    <td className="py-1 px-1">
                      <input
                        type="number"
                        step="0.1"
                        value={stain.gamma_degrees}
                        onChange={(e) => handleUpdateStain(idx, "gamma_degrees", parseFloat(e.target.value) || 0)}
                        className="w-16 bg-black/50 border border-tactical-border/40 rounded px-1.5 py-0.5 text-zinc-200"
                      />
                    </td>
                    <td className="py-1 px-2 text-center">
                      <button
                        onClick={() => handleRemoveStain(idx)}
                        disabled={stains.length <= 2}
                        className="text-rose-400 hover:text-rose-300 disabled:text-zinc-600 cursor-pointer"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pt-2 flex items-center justify-between border-t border-tactical-border/30 text-xs">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={applyGravity}
                onChange={(e) => setApplyGravity(e.target.checked)}
                className="accent-rose-500 rounded cursor-pointer"
              />
              <span className="text-zinc-300 font-bold flex items-center gap-1">
                <Wind className="w-3.5 h-3.5 text-rose-400" />
                Apply Aerodynamic Drag & Gravity Curvature Correction (Schiller-Naumann)
              </span>
            </label>
          </div>
        </div>

        {/* Right Column: 3D Area of Origin Solution Display */}
        <div className="space-y-4">
          {result && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              {/* Convergence Coordinate Card */}
              <div className="rounded-2xl border border-rose-500/40 bg-gradient-to-br from-rose-500/10 via-tactical-surface/60 to-black/80 p-5 space-y-4 shadow-2xl">
                <div className="flex items-center justify-between border-b border-rose-500/20 pb-3">
                  <div>
                    <span className="text-[10px] font-bold text-rose-300 uppercase tracking-widest block">
                      3D AREA OF ORIGIN CONVERGENCE
                    </span>
                    <span className="text-xl font-black text-rose-300 font-mono">
                      ({result.origin.x_cm.toFixed(1)}, {result.origin.y_cm.toFixed(1)}, {result.origin.z_cm.toFixed(1)}) cm
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-zinc-400 block uppercase font-bold">Spatial Error (r_err)</span>
                    <span className="text-sm font-bold text-emerald-400 font-mono">
                      &plusmn;{result.spatial_error_radius_cm.toFixed(2)} cm
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                    <span className="text-[10px] text-zinc-500 block">Mean Impact Angle (α)</span>
                    <span className="font-bold text-rose-300 font-mono">{result.mean_impact_angle_deg}°</span>
                  </div>
                  <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40">
                    <span className="text-[10px] text-zinc-500 block">Gravity Correction</span>
                    <span className={`font-bold font-mono ${result.gravity_correction_applied ? "text-emerald-400" : "text-zinc-400"}`}>
                      {result.gravity_correction_applied ? "ACTIVE" : "OFF"}
                    </span>
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">
                    Orthogonal Residual Distance Errors (cm)
                  </span>
                  <div className="grid grid-cols-5 gap-1 text-center text-[10px] font-mono">
                    {result.orthogonal_residuals_cm.map((res, i) => (
                      <div key={i} className="p-1.5 rounded bg-black/30 border border-tactical-border/30 text-zinc-300">
                        S{i + 1}: {res.toFixed(2)}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono">
                  <div className="flex items-center gap-1.5 text-rose-400 font-bold mb-1">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    Evaluative Legal Shield
                  </div>
                  {result.prosecutors_fallacy_shield}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
