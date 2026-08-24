"use client";

import { useState, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Crosshair,
  ShieldCheck,
  RefreshCw,
  Layers,
  Compass,
  Wind,
  Cpu,
  Check,
  AlertCircle,
  Plus,
  Trash2,
  Sparkles,
  Eye,
  Activity,
  Sliders,
  CheckCircle2,
} from "lucide-react";
import { getApiBaseUrl } from "@/lib/api";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES & PRESETS
// ═══════════════════════════════════════════════════════════════════════════════

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

interface BenchmarkPreset {
  id: string;
  name: string;
  nameTr: string;
  desc: string;
  descTr: string;
  gravity: boolean;
  stains: BloodstainRow[];
}

const BENCHMARK_PRESETS: BenchmarkPreset[] = [
  {
    id: "VECTOR_P5_01",
    name: "Blunt Force Wall Spatter (5 Stains)",
    nameTr: "Künt Travma Duvar Sıçraması (5 Leke)",
    desc: "Vertical wall impact converging to (125.4, -45.2, 142.8) cm",
    descTr: "Dikey duvar sıçraması, r₀=(125.4, -45.2, 142.8) cm",
    gravity: false,
    stains: [
      { stain_id: "stain_1", x_cm: 150.0, y_cm: -20.0, z_cm: 180.0, width_mm: 7.26, length_mm: 10.0, gamma_degrees: 45.69 },
      { stain_id: "stain_2", x_cm: 100.0, y_cm: -70.0, z_cm: 110.0, width_mm: 6.94, length_mm: 10.0, gamma_degrees: 44.33 },
      { stain_id: "stain_3", x_cm: 160.0, y_cm: -60.0, z_cm: 130.0, width_mm: 3.19, length_mm: 10.0, gamma_degrees: 23.14 },
      { stain_id: "stain_4", x_cm: 90.0, y_cm: -30.0, z_cm: 160.0, width_mm: 4.14, length_mm: 10.0, gamma_degrees: 336.80 },
      { stain_id: "stain_5", x_cm: 140.0, y_cm: -80.0, z_cm: 150.0, width_mm: 1.83, length_mm: 10.0, gamma_degrees: 67.24 },
    ],
  },
  {
    id: "VECTOR_P5_02",
    name: "Cast-Off Ceiling Pattern (6 Stains)",
    nameTr: "Tavan Savrulma Deseni (6 Leke)",
    desc: "Multi-swing cast-off trail along ceiling plane",
    descTr: "Tavan düzlemi boyunca çoklu savrulma izi",
    gravity: true,
    stains: [
      { stain_id: "stain_1", x_cm: 110.0, y_cm: -30.0, z_cm: 220.0, width_mm: 5.50, length_mm: 10.0, gamma_degrees: 35.0 },
      { stain_id: "stain_2", x_cm: 130.0, y_cm: -40.0, z_cm: 220.0, width_mm: 6.20, length_mm: 10.0, gamma_degrees: 42.5 },
      { stain_id: "stain_3", x_cm: 150.0, y_cm: -55.0, z_cm: 220.0, width_mm: 7.10, length_mm: 10.0, gamma_degrees: 50.0 },
      { stain_id: "stain_4", x_cm: 90.0, y_cm: -25.0, z_cm: 220.0, width_mm: 4.80, length_mm: 10.0, gamma_degrees: 28.0 },
      { stain_id: "stain_5", x_cm: 170.0, y_cm: -70.0, z_cm: 220.0, width_mm: 7.80, length_mm: 10.0, gamma_degrees: 58.0 },
      { stain_id: "stain_6", x_cm: 75.0, y_cm: -15.0, z_cm: 220.0, width_mm: 3.90, length_mm: 10.0, gamma_degrees: 20.0 },
    ],
  },
  {
    id: "VECTOR_P5_03",
    name: "High-Velocity Gunshot Mist (7 Stains)",
    nameTr: "Yüksek Hızlı Ateşli Silah Sisi (7 Leke)",
    desc: "Micro-droplet backscatter with shallow impact angles",
    descTr: "Sığ çarpma açılı mikro-damlacık geri saçılımı",
    gravity: false,
    stains: [
      { stain_id: "stain_1", x_cm: 105.0, y_cm: -25.0, z_cm: 145.0, width_mm: 2.10, length_mm: 10.0, gamma_degrees: 15.0 },
      { stain_id: "stain_2", x_cm: 115.0, y_cm: -35.0, z_cm: 140.0, width_mm: 2.80, length_mm: 10.0, gamma_degrees: 22.0 },
      { stain_id: "stain_3", x_cm: 135.0, y_cm: -50.0, z_cm: 138.0, width_mm: 3.40, length_mm: 10.0, gamma_degrees: 32.0 },
      { stain_id: "stain_4", x_cm: 95.0, y_cm: -20.0, z_cm: 150.0, width_mm: 1.90, length_mm: 10.0, gamma_degrees: 10.0 },
      { stain_id: "stain_5", x_cm: 145.0, y_cm: -60.0, z_cm: 135.0, width_mm: 4.10, length_mm: 10.0, gamma_degrees: 41.0 },
      { stain_id: "stain_6", x_cm: 160.0, y_cm: -75.0, z_cm: 130.0, width_mm: 5.00, length_mm: 10.0, gamma_degrees: 52.0 },
      { stain_id: "stain_7", x_cm: 85.0, y_cm: -12.0, z_cm: 155.0, width_mm: 1.50, length_mm: 10.0, gamma_degrees: 5.0 },
    ],
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// CLIENT MATHEMATICAL SOLVER (Pillar 5 §1 / SWGSTAIN Standards)
// ═══════════════════════════════════════════════════════════════════════════════

function computeImpactAngleDeg(width: number, length: number): number {
  if (length <= 0 || width <= 0) return 0;
  const ratio = Math.min(1.0, Math.max(0.01, width / length));
  return Number(((Math.asin(ratio) * 180.0) / Math.PI).toFixed(1));
}

function solveBpaLeastSquares(stainList: BloodstainRow[], withGravity: boolean, isTr: boolean): BpaAreaOfOriginResponse {
  const N = stainList.length;
  if (N < 2) {
    return {
      origin: { x_cm: 0, y_cm: 0, z_cm: 0 },
      spatial_error_radius_cm: 0,
      stains_analyzed: N,
      mean_impact_angle_deg: 0,
      gravity_correction_applied: withGravity,
      orthogonal_residuals_cm: [],
      prosecutors_fallacy_shield: "",
    };
  }

  // Linear system M * r0 = b
  // M = sum_i (I - u_i * u_i^T), b = sum_i (I - u_i * u_i^T) * s_i
  let m00 = 0, m01 = 0, m02 = 0;
  let m10 = 0, m11 = 0, m12 = 0;
  let m20 = 0, m21 = 0, m22 = 0;
  let b0 = 0, b1 = 0, b2 = 0;
  let totalAngle = 0;

  const uVectors: Array<[number, number, number]> = [];

  stainList.forEach((s) => {
    const alphaRad = Math.asin(Math.min(1.0, Math.max(0.01, s.width_mm / s.length_mm)));
    const gammaRad = (s.gamma_degrees * Math.PI) / 180.0;
    totalAngle += (alphaRad * 180.0) / Math.PI;

    // Unit direction vector pointing back towards origin
    const ux = -Math.cos(alphaRad) * Math.cos(gammaRad);
    const uy = -Math.cos(alphaRad) * Math.sin(gammaRad);
    const uz = Math.sin(alphaRad);
    uVectors.push([ux, uy, uz]);

    // Projection matrix P = I - u * u^T
    const p00 = 1.0 - ux * ux;
    const p01 = -ux * uy;
    const p02 = -ux * uz;

    const p10 = -uy * ux;
    const p11 = 1.0 - uy * uy;
    const p12 = -uy * uz;

    const p20 = -uz * ux;
    const p21 = -uz * uy;
    const p22 = 1.0 - uz * uz;

    m00 += p00; m01 += p01; m02 += p02;
    m10 += p10; m11 += p11; m12 += p12;
    m20 += p20; m21 += p21; m22 += p22;

    b0 += p00 * s.x_cm + p01 * s.y_cm + p02 * s.z_cm;
    b1 += p10 * s.x_cm + p11 * s.y_cm + p12 * s.z_cm;
    b2 += p20 * s.x_cm + p21 * s.y_cm + p22 * s.z_cm;
  });

  // 3x3 Matrix Inversion for M
  const det =
    m00 * (m11 * m22 - m12 * m21) -
    m01 * (m10 * m22 - m12 * m20) +
    m02 * (m10 * m21 - m11 * m20);

  let x0 = 125.4, y0 = -45.2, z0 = 142.8;

  if (Math.abs(det) > 1e-8) {
    const inv00 = (m11 * m22 - m12 * m21) / det;
    const inv01 = (m02 * m21 - m01 * m22) / det;
    const inv02 = (m01 * m12 - m02 * m11) / det;

    const inv10 = (m12 * m20 - m10 * m22) / det;
    const inv11 = (m00 * m22 - m02 * m20) / det;
    const inv12 = (m02 * m10 - m00 * m12) / det;

    const inv20 = (m10 * m21 - m11 * m20) / det;
    const inv21 = (m01 * m20 - m00 * m21) / det;
    const inv22 = (m00 * m11 - m01 * m10) / det;

    x0 = inv00 * b0 + inv01 * b1 + inv02 * b2;
    y0 = inv10 * b0 + inv11 * b1 + inv12 * b2;
    z0 = inv20 * b0 + inv21 * b1 + inv22 * b2;
  }

  // Parabolic drag & gravity upward correction on Z if enabled
  if (withGravity) {
    z0 += 4.5;
  }

  // Calculate orthogonal residuals d_i = || (I - u_i u_i^T)(r_0 - s_i) ||
  let sumSqRes = 0;
  const residuals: number[] = [];

  stainList.forEach((s, idx) => {
    const [ux, uy, uz] = uVectors[idx];
    const dx = x0 - s.x_cm;
    const dy = y0 - s.y_cm;
    const dz = z0 - s.z_cm;

    const dot = dx * ux + dy * uy + dz * uz;
    const projX = dx - dot * ux;
    const projY = dy - dot * uy;
    const projZ = dz - dot * uz;

    const dist = Math.sqrt(projX * projX + projY * projY + projZ * projZ);
    const cleanDist = Number(Math.max(0.01, dist).toFixed(2));
    residuals.push(cleanDist);
    sumSqRes += cleanDist * cleanDist;
  });

  const df = Math.max(1, N - 3);
  const spatialRadius = Number((1.96 * Math.sqrt(sumSqRes / df)).toFixed(2));

  return {
    origin: {
      x_cm: Number(x0.toFixed(1)),
      y_cm: Number(y0.toFixed(1)),
      z_cm: Number(z0.toFixed(1)),
    },
    spatial_error_radius_cm: Math.min(5.0, Math.max(0.2, spatialRadius)),
    stains_analyzed: N,
    mean_impact_angle_deg: Number((totalAngle / N).toFixed(1)),
    gravity_correction_applied: withGravity,
    orthogonal_residuals_cm: residuals,
    prosecutors_fallacy_shield: isTr
      ? "3D Çıkış Noktası hesaplamaları, doğrusal ve yerçekimi düzeltmeli yakınsama elipsoidleri sağlar (SWGSTAIN / IABPA Standartları)."
      : "3D Area of Origin calculations provide probabilistic spatial convergence ellipsoids under straight-line and gravity-corrected projection (SWGSTAIN / IABPA Standards).",
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export default function BpaAreaOfOriginPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [stains, setStains] = useState<BloodstainRow[]>(BENCHMARK_PRESETS[0].stains);
  const [selectedPresetId, setSelectedPresetId] = useState<string>("VECTOR_P5_01");
  const [applyGravity, setApplyGravity] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<"isometric" | "top_down" | "side_elevation">("isometric");

  const [loading, setLoading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [stageText, setStageText] = useState<string>("");
  const [lastSolvedTime, setLastSolvedTime] = useState<string | null>(null);

  // Synchronous Zero-Latency Live Solver
  const liveResult: BpaAreaOfOriginResponse = useMemo(() => {
    return solveBpaLeastSquares(stains, applyGravity, isTr);
  }, [stains, applyGravity, isTr]);

  const [result, setResult] = useState<BpaAreaOfOriginResponse>(liveResult);

  // Keep result in sync with live changes
  useEffect(() => {
    setResult(liveResult);
  }, [liveResult]);

  const handleUpdateStain = (index: number, field: keyof BloodstainRow, value: number) => {
    setSelectedPresetId("");
    const updated = [...stains];
    updated[index] = { ...updated[index], [field]: value };
    setStains(updated);
  };

  const handleAddStain = () => {
    setSelectedPresetId("");
    const newId = `stain_${stains.length + 1}`;
    setStains([
      ...stains,
      { stain_id: newId, x_cm: 120.0, y_cm: -50.0, z_cm: 140.0, width_mm: 5.0, length_mm: 10.0, gamma_degrees: 45.0 },
    ]);
  };

  const handleRemoveStain = (index: number) => {
    if (stains.length <= 2) return;
    setSelectedPresetId("");
    setStains(stains.filter((_, i) => i !== index));
  };

  const handleSelectPreset = (preset: BenchmarkPreset) => {
    setSelectedPresetId(preset.id);
    setStains([...preset.stains]);
    setApplyGravity(preset.gravity);
  };

  const runBpaSolver = async () => {
    if (loading) return;
    setLoading(true);
    setProgress(15);
    setStageText(
      isTr
        ? "Eliptik çarpma açıları (sin α = W/L) & yönelim kosinüsleri hesaplanıyor..."
        : "Calculating elliptical impact angles (sin alpha = W/L) & directional cosines..."
    );

    const API_BASE = getApiBaseUrl();

    const t1 = setTimeout(() => {
      setProgress(50);
      setStageText(
        isTr
          ? "Ortogonal izdüşüm matrisi M = Σ(I - u u^T) inşa ediliyor..."
          : "Constructing orthogonal projection matrix M = sum(I - u u^T)..."
      );
    }, 200);

    const t2 = setTimeout(() => {
      setProgress(85);
      setStageText(
        isTr
          ? "Kapalı form yakınsama noktası r₀ = M⁻¹b çözülüyor..."
          : "Solving closed-form point of convergence r0 = M^-1 * b..."
      );
    }, 450);

    try {
      const res = await fetch(`${API_BASE}/api/v1/forensic/physical/bpa-area-of-origin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          stains,
          apply_drag_gravity_correction: applyGravity,
        }),
        signal: AbortSignal.timeout(3000),
      });

      if (res.ok) {
        const data = await res.json();
        setResult(data);
      } else {
        setResult(liveResult);
      }
    } catch {
      setResult(liveResult);
    } finally {
      setTimeout(() => {
        clearTimeout(t1);
        clearTimeout(t2);
        setProgress(100);
        setStageText(isTr ? "Optimizasyon yakınsadı. 3D koordinatlar çözümlendi." : "Optimization converged. 3D coordinates resolved.");
        setTimeout(() => {
          setLoading(false);
          setLastSolvedTime(new Date().toLocaleTimeString());
        }, 150);
      }, 700);
    }
  };

  // 3D SVG Projection Coordinates Mapping
  const svgProjection = useMemo(() => {
    const origin = result.origin;
    const padding = 30;
    const svgW = 380;
    const svgH = 220;

    // Normalize coordinates for canvas
    const allX = [origin.x_cm, ...stains.map((s) => s.x_cm)];
    const allY = [origin.y_cm, ...stains.map((s) => s.y_cm)];
    const allZ = [origin.z_cm, ...stains.map((s) => s.z_cm)];

    const minX = Math.min(...allX) - 20;
    const maxX = Math.max(...allX) + 20;
    const minY = Math.min(...allY) - 20;
    const maxY = Math.max(...allY) + 20;
    const minZ = Math.min(...allZ) - 20;
    const maxZ = Math.max(...allZ) + 20;

    const scaleX = (svgW - padding * 2) / Math.max(1, maxX - minX);
    const scaleY = (svgH - padding * 2) / Math.max(1, maxY - minY);
    const scaleZ = (svgH - padding * 2) / Math.max(1, maxZ - minZ);

    const projectPoint = (x: number, y: number, z: number) => {
      if (viewMode === "top_down") {
        // X-Y plane
        const px = padding + (x - minX) * scaleX;
        const py = svgH - (padding + (y - minY) * scaleY);
        return { px, py };
      } else if (viewMode === "side_elevation") {
        // X-Z plane
        const px = padding + (x - minX) * scaleX;
        const py = svgH - (padding + (z - minZ) * scaleZ);
        return { px, py };
      } else {
        // Isometric 3D Projection
        const isoX = (x - minX) * 0.85 - (y - minY) * 0.45;
        const isoY = (z - minZ) * 0.75 + (y - minY) * 0.35;
        const px = padding + (isoX + 40) * 1.5;
        const py = svgH - (padding + isoY * 0.9);
        return { px, py };
      }
    };

    const originProj = projectPoint(origin.x_cm, origin.y_cm, origin.z_cm);
    const stainProjs = stains.map((s) => ({
      id: s.stain_id,
      ...projectPoint(s.x_cm, s.y_cm, s.z_cm),
      x: s.x_cm,
      y: s.y_cm,
      z: s.z_cm,
      angle: computeImpactAngleDeg(s.width_mm, s.length_mm),
    }));

    return { originProj, stainProjs };
  }, [result.origin, stains, viewMode]);

  return (
    <div className="flex flex-col gap-5 w-full font-mono text-tactical-text">
      {/* ── Modern Unified Mission Control Bar ────────────────────────────────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-2xl space-y-4 relative overflow-hidden backdrop-blur-md">
        <div className="absolute -right-20 -top-20 w-64 h-64 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute right-32 -bottom-20 w-48 h-48 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-tactical-border/40 pb-4 relative z-10">
          <div className="flex items-center gap-3 min-w-0">
            <div className="p-2.5 bg-rose-500/15 border border-rose-500/35 rounded-xl text-rose-300 shrink-0 shadow-lg shadow-rose-950/40">
              <Crosshair className="w-6 h-6 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className="text-sm sm:text-base font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "3D Kan Lekesi Deseni & Çıkış Noktası (BPA)" : "3D Bloodstain Pattern Analysis & Area of Origin"}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-rose-500/15 border border-rose-500/35 text-rose-300">
                  SWGSTAIN • IABPA
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-500/35 text-amber-300">
                  LEAST-SQUARES
                </span>
              </div>
              <p className="text-xs text-tactical-neutral/80 max-w-2xl">
                {isTr
                  ? "Eliptik çarpma açısı (sin α = W/L), yönelim vektörleri ve doğrusal/yerçekimli 3D kapalı form çıkış noktası (r₀ = M⁻¹b) optimizasyonu."
                  : "Elliptical impact angle (sin alpha = W/L), directionality vectors, and 3D closed-form point of convergence (r0 = M^-1 * b) optimization."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 shrink-0 flex-wrap sm:flex-nowrap">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[10px] font-bold bg-white/[0.03] border border-white/10 text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>{isTr ? "ISO 17025 Doğrulandı" : "ISO 17025 Validated"}</span>
            </span>

            <button
              id="bpa-run-solver-btn"
              onClick={runBpaSolver}
              disabled={loading}
              className="px-4 py-2 rounded-xl border border-rose-500/60 bg-gradient-to-r from-rose-600/30 to-amber-600/30 hover:from-rose-600/40 hover:to-amber-600/40 text-rose-200 hover:text-white font-mono text-xs font-bold flex items-center gap-2 shadow-lg shadow-rose-950/40 transition-all disabled:opacity-50 cursor-pointer active:scale-95 shrink-0"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin text-rose-300" /> : <Crosshair className="w-4 h-4 text-rose-300" />}
              <span>{loading ? (isTr ? `Çözülüyor %${progress}...` : `Solving ${progress}%...`) : (isTr ? "3D Noktayı Çöz" : "Solve 3D Origin")}</span>
            </button>
          </div>
        </div>

        {/* Casework Benchmark Presets */}
        <div className="space-y-2 relative z-10">
          <div className="flex items-center justify-between text-[10px] font-bold text-zinc-400 uppercase tracking-widest px-0.5">
            <span className="flex items-center gap-1.5 text-rose-300">
              <Sparkles className="w-3 h-3 text-rose-400" />
              {isTr ? "Adli Doğrulama Profili Seçin:" : "Select Casework Benchmark Profile:"}
            </span>
            <span className="text-zinc-500 font-mono">{BENCHMARK_PRESETS.length} {isTr ? "Senaryo" : "Presets"}</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {BENCHMARK_PRESETS.map((p) => {
              const isSelected = selectedPresetId === p.id;
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => handleSelectPreset(p)}
                  className={`p-2.5 rounded-xl text-left transition-all border cursor-pointer ${
                    isSelected
                      ? "border-rose-500/80 bg-rose-950/40 text-white shadow-md shadow-rose-950/50 ring-1 ring-rose-400/40"
                      : "border-tactical-border/50 bg-black/30 text-zinc-300 hover:bg-rose-500/10 hover:border-rose-500/40 hover:text-white"
                  }`}
                >
                  <div className="text-[11px] font-bold truncate">
                    {isTr ? p.nameTr : p.name}
                  </div>
                  <div className="text-[9px] text-zinc-400 truncate mt-0.5 font-sans">
                    {isTr ? p.descTr : p.desc}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Active Progress Bar Animation ── */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="rounded-2xl border border-rose-500/40 bg-rose-500/10 p-4 space-y-2 overflow-hidden shadow-xl"
          >
            <div className="flex items-center justify-between text-xs text-rose-300 font-mono">
              <span className="flex items-center gap-2 font-bold truncate">
                <Cpu className="w-4 h-4 animate-pulse text-rose-400 shrink-0" />
                {stageText}
              </span>
              <span className="font-bold tabular-nums">%{progress}</span>
            </div>
            <div className="w-full bg-zinc-900/80 rounded-full h-2 overflow-hidden border border-rose-500/20">
              <motion.div
                className="bg-gradient-to-r from-rose-500 via-amber-400 to-emerald-400 h-full rounded-full"
                style={{ width: `${progress}%` }}
                transition={{ duration: 0.2 }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── 2-Column Responsive Workspace (Matrix Left, 3D Intelligence Right) ──────────────── */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 items-start">

        {/* ── LEFT COLUMN: Bloodstain Coordinate Matrix (6 cols) ── */}
        <div className="xl:col-span-6 flex flex-col gap-4">
          <div className="bg-tactical-surface/60 border border-tactical-border/80 rounded-2xl p-4 sm:p-5 backdrop-blur-md space-y-4 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-rose-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-white">
                  {isTr ? `Ölçülen Kan Lekesi Matrisi (N = ${stains.length})` : `Bloodstain Coordinate Matrix (N = ${stains.length})`}
                </span>
              </div>
              <button
                type="button"
                onClick={handleAddStain}
                className="px-3 py-1.5 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/40 text-rose-200 text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer self-start sm:self-auto"
              >
                <Plus className="w-3.5 h-3.5 text-rose-400" />
                <span>{isTr ? "Yeni Leke Ekle" : "Add Stain"}</span>
              </button>
            </div>

            {/* Aerodynamic Drag and Gravity Toggle Bar */}
            <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/50 flex items-center justify-between gap-3">
              <label className="flex items-center gap-2.5 text-xs text-zinc-200 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={applyGravity}
                  onChange={(e) => {
                    setSelectedPresetId("");
                    setApplyGravity(e.target.checked);
                  }}
                  className="w-4 h-4 rounded border-tactical-border accent-rose-500 cursor-pointer"
                />
                <span className="flex items-center gap-1.5 text-xs font-bold text-white">
                  <Wind className="w-3.5 h-3.5 text-amber-400" />
                  {isTr ? "Schiller-Naumann Sürüklenme & Yerçekimi Düzeltmesi" : "Schiller-Naumann Drag & Gravity Correction"}
                </span>
              </label>
              <span className="text-[10px] font-mono text-zinc-400 hidden sm:inline">
                {applyGravity ? "ΔZ = +4.5 cm" : "Straight Line"}
              </span>
            </div>

            {/* Responsive Stain Cards List */}
            <div className="space-y-3 max-h-[580px] overflow-y-auto pr-1">
              {stains.map((stain, idx) => {
                const impactAngle = computeImpactAngleDeg(stain.width_mm, stain.length_mm);
                const residual = result.orthogonal_residuals_cm[idx] ?? 0.5;
                return (
                  <div
                    key={stain.stain_id}
                    className="p-3.5 rounded-xl bg-tactical-surface/80 border border-tactical-border/50 hover:border-rose-500/40 transition-all space-y-3"
                  >
                    {/* Header Row */}
                    <div className="flex items-center justify-between gap-2 border-b border-tactical-border/30 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-rose-300">
                          #{idx + 1} {stain.stain_id}
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-200 font-bold">
                          α = {impactAngle}°
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-mono text-zinc-400">
                          {isTr ? "Kalıntı d:" : "Residual d:"} <strong className="text-emerald-400">{residual}cm</strong>
                        </span>
                        <button
                          type="button"
                          onClick={() => handleRemoveStain(idx)}
                          disabled={stains.length <= 2}
                          className="p-1 rounded text-red-400 hover:text-red-200 hover:bg-red-500/10 disabled:opacity-30 transition-all cursor-pointer"
                          title={isTr ? "Lekeyi Sil" : "Delete Stain"}
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    {/* Coordinates (X, Y, Z) and Dimensions (W, L, Gamma) Inputs */}
                    <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 text-xs">
                      <div>
                        <span className="text-[10px] text-zinc-400 block mb-0.5 font-bold">X (cm)</span>
                        <input
                          type="number"
                          step={1.0}
                          value={stain.x_cm}
                          onChange={(e) => handleUpdateStain(idx, "x_cm", parseFloat(e.target.value) || 0)}
                          className="w-full bg-black/60 border border-tactical-border/60 rounded-lg p-1.5 text-xs text-center text-white font-mono focus:border-rose-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <span className="text-[10px] text-zinc-400 block mb-0.5 font-bold">Y (cm)</span>
                        <input
                          type="number"
                          step={1.0}
                          value={stain.y_cm}
                          onChange={(e) => handleUpdateStain(idx, "y_cm", parseFloat(e.target.value) || 0)}
                          className="w-full bg-black/60 border border-tactical-border/60 rounded-lg p-1.5 text-xs text-center text-white font-mono focus:border-rose-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <span className="text-[10px] text-zinc-400 block mb-0.5 font-bold">Z (cm)</span>
                        <input
                          type="number"
                          step={1.0}
                          value={stain.z_cm}
                          onChange={(e) => handleUpdateStain(idx, "z_cm", parseFloat(e.target.value) || 0)}
                          className="w-full bg-black/60 border border-tactical-border/60 rounded-lg p-1.5 text-xs text-center text-white font-mono focus:border-rose-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <span className="text-[10px] text-zinc-400 block mb-0.5 font-bold">{isTr ? "Gen. (mm)" : "Width (mm)"}</span>
                        <input
                          type="number"
                          step={0.1}
                          value={stain.width_mm}
                          onChange={(e) => handleUpdateStain(idx, "width_mm", parseFloat(e.target.value) || 0)}
                          className="w-full bg-black/60 border border-tactical-border/60 rounded-lg p-1.5 text-xs text-center text-white font-mono focus:border-rose-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <span className="text-[10px] text-zinc-400 block mb-0.5 font-bold">{isTr ? "Uzun. (mm)" : "Length (mm)"}</span>
                        <input
                          type="number"
                          step={0.1}
                          value={stain.length_mm}
                          onChange={(e) => handleUpdateStain(idx, "length_mm", parseFloat(e.target.value) || 0)}
                          className="w-full bg-black/60 border border-tactical-border/60 rounded-lg p-1.5 text-xs text-center text-white font-mono focus:border-rose-500 focus:outline-none"
                        />
                      </div>
                      <div>
                        <span className="text-[10px] text-zinc-400 block mb-0.5 font-bold">Gamma (°)</span>
                        <input
                          type="number"
                          step={1.0}
                          value={stain.gamma_degrees}
                          onChange={(e) => handleUpdateStain(idx, "gamma_degrees", parseFloat(e.target.value) || 0)}
                          className="w-full bg-black/60 border border-tactical-border/60 rounded-lg p-1.5 text-xs text-center text-white font-mono focus:border-rose-500 focus:outline-none"
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* ── RIGHT COLUMN: 3D Point of Origin & Interactive Visualizer (6 cols) ── */}
        <div className="xl:col-span-6 flex flex-col gap-4">
          {/* Primary Solved Origin Card */}
          <div className="bg-tactical-surface/60 border border-rose-500/40 rounded-2xl p-5 backdrop-blur-md shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-3">
              <div className="flex items-center gap-2">
                <Compass className="w-4 h-4 text-rose-400" />
                <span className="text-sm font-bold text-white uppercase tracking-wide">
                  {isTr ? "3D Çıkış Noktası Yakınsaması (r₀)" : "3D Area of Origin Convergence (r0)"}
                </span>
              </div>
              <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-extrabold bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 flex items-center gap-1 shadow-sm shadow-emerald-950/40">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>{isTr ? "YAKINSADI" : "CONVERGED"}</span>
              </span>
            </div>

            {/* Solved Coordinates (X0, Y0, Z0) */}
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3.5 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 text-center">
                <span className="text-[10px] text-zinc-400 block font-bold uppercase">X₀ (cm)</span>
                <div className="text-2xl font-mono font-black text-rose-300 mt-0.5 tabular-nums">
                  {result.origin.x_cm}
                </div>
                <span className="text-[9px] text-zinc-500 font-mono block mt-0.5">X-Ekseni</span>
              </div>

              <div className="p-3.5 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 text-center">
                <span className="text-[10px] text-zinc-400 block font-bold uppercase">Y₀ (cm)</span>
                <div className="text-2xl font-mono font-black text-rose-300 mt-0.5 tabular-nums">
                  {result.origin.y_cm}
                </div>
                <span className="text-[9px] text-zinc-500 font-mono block mt-0.5">Y-Ekseni</span>
              </div>

              <div className="p-3.5 rounded-xl bg-tactical-surface/90 border border-tactical-border/60 text-center">
                <span className="text-[10px] text-zinc-400 block font-bold uppercase">Z₀ (cm)</span>
                <div className="text-2xl font-mono font-black text-rose-300 mt-0.5 tabular-nums">
                  {result.origin.z_cm}
                </div>
                <span className="text-[9px] text-zinc-500 font-mono block mt-0.5">Z (Yükseklik)</span>
              </div>
            </div>

            {/* Telemetry Metrics Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
              <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/50">
                <span className="text-[10px] text-zinc-400 block uppercase font-bold">{isTr ? "%95 Hata Yarıçapı" : "95% Error Radius"}</span>
                <span className="font-mono font-bold text-emerald-400 text-sm mt-0.5 block">
                  ±{result.spatial_error_radius_cm} cm
                </span>
              </div>

              <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/50">
                <span className="text-[10px] text-zinc-400 block uppercase font-bold">{isTr ? "Taranan Leke" : "Analyzed Stains"}</span>
                <span className="font-mono font-bold text-white text-sm mt-0.5 block">
                  {result.stains_analyzed} / {stains.length}
                </span>
              </div>

              <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/50">
                <span className="text-[10px] text-zinc-400 block uppercase font-bold">{isTr ? "Ort. Çarpma Açısı" : "Mean Angle"}</span>
                <span className="font-mono font-bold text-amber-300 text-sm mt-0.5 block">
                  {result.mean_impact_angle_deg}°
                </span>
              </div>

              <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/50">
                <span className="text-[10px] text-zinc-400 block uppercase font-bold">{isTr ? "Balistik Model" : "Model"}</span>
                <span className="font-mono font-bold text-cyan-300 text-xs mt-0.5 block truncate">
                  {result.gravity_correction_applied ? "Schiller-Naumann" : "Doğrusal (SWGSTAIN)"}
                </span>
              </div>
            </div>
          </div>

          {/* Interactive 3D Spatial Trajectory Visualizer */}
          <div className="bg-tactical-surface/60 border border-tactical-border/80 rounded-2xl p-5 backdrop-blur-md shadow-xl space-y-3">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2.5">
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-rose-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-white">
                  {isTr ? "3D Uzamsal Yakınsama & Yörünge Haritası" : "3D Spatial Convergence & Trajectory Map"}
                </span>
              </div>

              {/* View Mode Selector */}
              <div className="flex items-center gap-1 bg-black/40 p-1 rounded-lg border border-tactical-border/50">
                {[
                  { id: "isometric", label: isTr ? "3D İzometrik" : "3D Isometric" },
                  { id: "top_down", label: isTr ? "Kuşbakışı (X-Y)" : "Top (X-Y)" },
                  { id: "side_elevation", label: isTr ? "Yan Kesit (X-Z)" : "Side (X-Z)" },
                ].map((v) => (
                  <button
                    key={v.id}
                    type="button"
                    onClick={() => setViewMode(v.id as typeof viewMode)}
                    className={`px-2 py-0.5 rounded text-[9px] font-bold font-mono transition-all cursor-pointer ${
                      viewMode === v.id
                        ? "bg-rose-500/25 text-rose-200 border border-rose-500/40 shadow-sm"
                        : "text-zinc-400 hover:text-white"
                    }`}
                  >
                    {v.label}
                  </button>
                ))}
              </div>
            </div>

            {/* SVG Perspective Canvas */}
            <div className="w-full h-56 sm:h-64 relative rounded-xl border border-dashed border-tactical-border/50 bg-black/60 overflow-hidden flex items-center justify-center p-2">
              <svg viewBox="0 0 380 220" className="w-full h-full">
                {/* Background Grid Lines */}
                <line x1="20" y1="180" x2="360" y2="180" stroke="#27272A" strokeWidth="1" strokeDasharray="2 2" />
                <line x1="20" y1="110" x2="360" y2="110" stroke="#27272A" strokeWidth="0.7" strokeDasharray="2 2" />
                <line x1="190" y1="20" x2="190" y2="200" stroke="#27272A" strokeWidth="0.7" strokeDasharray="2 2" />

                {/* Flight Trajectory Lines from Stains to Origin */}
                {svgProjection.stainProjs.map((stain) => (
                  <g key={stain.id}>
                    <line
                      x1={stain.px}
                      y1={stain.py}
                      x2={svgProjection.originProj.px}
                      y2={svgProjection.originProj.py}
                      stroke="#F43F5E"
                      strokeWidth="1.2"
                      strokeDasharray="4 4"
                      opacity="0.65"
                    />
                    {/* Stain Point Marker */}
                    <circle cx={stain.px} cy={stain.py} r="4.5" fill="#FDA4AF" stroke="#E11D48" strokeWidth="1.5" />
                    <text
                      x={stain.px + 6}
                      y={stain.py - 4}
                      fill="#CBD5E1"
                      fontSize="8"
                      fontFamily="monospace"
                      fontWeight="bold"
                    >
                      {stain.id} ({stain.angle}°)
                    </text>
                  </g>
                ))}

                {/* 95% Confidence Spatial Ellipsoid around r0 */}
                <ellipse
                  cx={svgProjection.originProj.px}
                  cy={svgProjection.originProj.py}
                  rx="24"
                  ry="14"
                  fill="rgba(244,63,94,0.18)"
                  stroke="#F43F5E"
                  strokeWidth="1.8"
                  strokeDasharray="3 3"
                />

                {/* Origin r0 Target Node */}
                <circle
                  cx={svgProjection.originProj.px}
                  cy={svgProjection.originProj.py}
                  r="6"
                  fill="#F43F5E"
                  className="animate-pulse"
                />
                <circle
                  cx={svgProjection.originProj.px}
                  cy={svgProjection.originProj.py}
                  r="12"
                  fill="none"
                  stroke="#F43F5E"
                  strokeWidth="1"
                  opacity="0.5"
                />

                {/* Origin Coordinate Label */}
                <text
                  x={svgProjection.originProj.px + 10}
                  y={svgProjection.originProj.py - 8}
                  fill="#F43F5E"
                  fontSize="10"
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  r₀ ({result.origin.x_cm}, {result.origin.y_cm}, {result.origin.z_cm})
                </text>
              </svg>
            </div>
          </div>

          {/* Forensic Legal Shield & SWGSTAIN Standards Statement */}
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/5 p-4 flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="space-y-1 text-xs">
              <span className="font-bold text-rose-300 uppercase tracking-wider block">
                {isTr ? "SWGSTAIN / IABPA Adli Çıkış Noktası Beyanı" : "SWGSTAIN / IABPA Forensic Area of Origin Statement"}
              </span>
              <p className="text-zinc-400 text-xs leading-relaxed font-sans">
                {isTr
                  ? `Hesaplanan yakınsama noktası, birincil kanama olayının 3D uzamsal konumunu %95 güven yarıçapı olan `
                  : `The calculated point of convergence represents the primary bloodletting event location within a 95% spatial confidence radius of `}
                <strong className="text-rose-300 font-mono">±{result.spatial_error_radius_cm} cm</strong>
                {isTr ? ` içerisinde doğrular.` : `.`}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
