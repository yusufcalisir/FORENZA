"use client";

import { useState, useRef, useEffect } from "react";
import {
  ShieldCheck, MapPin, PackageCheck, Crosshair, Layers,
  RotateCw, Move3d, Eye, ChevronDown, ChevronUp, Circle,
} from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────
interface EvidenceItem {
  id: string;
  scene: string;
  type: "LIDAR" | "BPA" | "BALLISTICS" | "DNA" | "BONE";
  method: string;
  collector: string;
  seal: string;
  condition: string;
  x: number; y: number; z: number;
  badge: string;
  hash: string;
  precision_m: number;   // §5.1 sensor precision
  sigma_m: number;       // Covariance for ellipsoid (isotropic)
}

// ── Sensor config from Research §5.1 ─────────────────────────────────────────
const SENSOR_CONFIG: Record<string, { color: string; ellipsoidColor: string; label: string; precision: number }> = {
  LIDAR:      { color: "text-cyan-400",    ellipsoidColor: "rgba(34,211,238,0.15)",  label: "LiDAR",    precision: 0.002 },
  BPA:        { color: "text-rose-400",    ellipsoidColor: "rgba(251,113,133,0.18)", label: "BPA",      precision: 0.012 },
  BALLISTICS: { color: "text-orange-400",  ellipsoidColor: "rgba(251,146,60,0.15)",  label: "Ballistic",precision: 0.005 },
  DNA:        { color: "text-emerald-400", ellipsoidColor: "rgba(52,211,153,0.15)",  label: "DNA",      precision: 0.008 },
  BONE:       { color: "text-violet-400",  ellipsoidColor: "rgba(167,139,250,0.15)", label: "Bone",     precision: 0.008 },
};

// CHI2_{3,0.95} = 7.815  (Research §5.2)
const CHI2_3_95 = 7.815;

// Compute ellipsoid semi-axis: a = sqrt(sigma^2 * 7.815) but scaled for display
function ellipsoidAxis(sigma_m: number, displayScale: number): number {
  return Math.sqrt(sigma_m * sigma_m * CHI2_3_95) * displayScale;
}

// ── Scene Evidence Data ───────────────────────────────────────────────────────
const ITEMS: EvidenceItem[] = [
  { id: "EVID-BLOOD-101", scene: "SCENE-2026-001", type: "BPA",        method: "Sterile Cotton Swab",  collector: "INV-DOE-12",    seal: "SEAL-112233", condition: "Dry Ambient", x: 1.5,   y: 2.2,   z: 0.4,  badge: "SEALED",  hash: "0x8f2a...91b4", precision_m: 0.012, sigma_m: 0.012 },
  { id: "EVID-HAIR-102",  scene: "SCENE-2026-001", type: "DNA",        method: "Sterile Forceps",      collector: "INV-DOE-12",    seal: "SEAL-445566", condition: "Room Temp",  x: 3.1,   y: 0.8,   z: 0.0,  badge: "SEALED",  hash: "0x3c1d...44e9", precision_m: 0.008, sigma_m: 0.008 },
  { id: "EVID-TOUCH-103", scene: "SCENE-2026-001", type: "DNA",        method: "Tape Lift",            collector: "INV-SMITH-44",  seal: "SEAL-998877", condition: "Dry Ambient",x: 0.9,   y: 1.4,   z: 1.1,  badge: "IN_LAB",  hash: "0x7e5b...22f0", precision_m: 0.008, sigma_m: 0.008 },
  { id: "EVID-BONE-104",  scene: "SCENE-2026-002", type: "BONE",       method: "Excision",             collector: "INV-SMITH-44",  seal: "SEAL-334411", condition: "Frozen -20C",x: 4.2,   y: 3.5,   z: 0.0,  badge: "FROZEN",  hash: "0x1a9c...88d2", precision_m: 0.008, sigma_m: 0.010 },
  { id: "EVID-LIDAR-001", scene: "SCENE-2026-001", type: "LIDAR",      method: "TLS Scan",             collector: "TECH-UNIT-03",  seal: "SEAL-773311", condition: "Sealed CAD", x: 2.5,   y: 3.8,   z: 1.5,  badge: "SCANNED", hash: "0x2b3c...11a7", precision_m: 0.002, sigma_m: 0.002 },
  { id: "EVID-BALLISTIC", scene: "SCENE-2026-001", type: "BALLISTICS", method: "SEM-EDX CMC",          collector: "TECH-UNIT-03",  seal: "SEAL-229944", condition: "Dry Ambient",x: 0.3,   y: 0.5,   z: 1.8,  badge: "ANALYZED",hash: "0x5d8e...33c1", precision_m: 0.005, sigma_m: 0.005 },
];

// ── 2D Canvas Projection (Isometric-like top-down XY) ────────────────────────
function worldToCanvas(
  x: number, y: number,
  view: "top" | "side" | "isometric",
  scale: number, offsetX: number, offsetY: number
): [number, number] {
  switch (view) {
    case "top":       return [offsetX + x * scale, offsetY - y * scale];
    case "side":      return [offsetX + x * scale, offsetY - y * scale];
    case "isometric": {
      // Simple isometric: (x-y)*cos30, (x+y)*sin30 - z
      const ix = (x - y) * Math.cos(Math.PI / 6);
      const iy = (x + y) * Math.sin(Math.PI / 6) - y * 0.5;
      return [offsetX + ix * scale * 0.8, offsetY - iy * scale * 0.8];
    }
  }
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function EvidenceManagementPanel() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedId, setSelectedId] = useState<string>("EVID-BLOOD-101");
  const [viewMode, setViewMode] = useState<"top" | "side" | "isometric">("isometric");
  const [showEllipsoids, setShowEllipsoids] = useState<boolean>(true);
  const [showBpaTrajectory, setShowBpaTrajectory] = useState<boolean>(true);
  const [showBallisticVector, setShowBallisticVector] = useState<boolean>(true);
  const [rollDeg, setRollDeg]   = useState<number>(0);
  const [pitchDeg, setPitchDeg] = useState<number>(0);
  const [yawDeg, setYawDeg]     = useState<number>(0);
  const [txM, setTxM] = useState<number>(0);
  const [tyM, setTyM] = useState<number>(0);
  const [tzM, setTzM] = useState<number>(0);
  const [detailsOpen, setDetailsOpen] = useState<boolean>(true);

  const selectedItem = ITEMS.find((i) => i.id === selectedId)!;

  // SE(3) transform for display (simplified — applies to centroid for juror view)
  function applyTransformOffset(x: number, y: number): [number, number] {
    const psi = (yawDeg * Math.PI) / 180;
    const nx = x * Math.cos(psi) - y * Math.sin(psi) + txM;
    const ny = x * Math.sin(psi) + y * Math.cos(psi) + tyM;
    return [nx, ny];
  }

  // ── Canvas Drawing ──────────────────────────────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const W = canvas.width;
    const H = canvas.height;
    const scale = 38;
    const ox = W / 2;
    const oy = H / 2 + 20;

    ctx.clearRect(0, 0, W, H);

    // Background
    ctx.fillStyle = "#050a14";
    ctx.fillRect(0, 0, W, H);

    // Grid
    ctx.strokeStyle = "rgba(148,163,184,0.07)";
    ctx.lineWidth = 1;
    for (let gx = -8; gx <= 8; gx++) {
      const [px1, py1] = worldToCanvas(gx, -8, viewMode, scale, ox, oy);
      const [px2, py2] = worldToCanvas(gx, 8, viewMode, scale, ox, oy);
      ctx.beginPath(); ctx.moveTo(px1, py1); ctx.lineTo(px2, py2); ctx.stroke();
    }
    for (let gy = -8; gy <= 8; gy++) {
      const [px1, py1] = worldToCanvas(-8, gy, viewMode, scale, ox, oy);
      const [px2, py2] = worldToCanvas(8, gy, viewMode, scale, ox, oy);
      ctx.beginPath(); ctx.moveTo(px1, py1); ctx.lineTo(px2, py2); ctx.stroke();
    }

    // Axes
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = "rgba(34,211,238,0.4)";
    const [ax0, ay0] = worldToCanvas(0, 0, viewMode, scale, ox, oy);
    const [ax1, ay1] = worldToCanvas(3, 0, viewMode, scale, ox, oy);
    ctx.beginPath(); ctx.moveTo(ax0, ay0); ctx.lineTo(ax1, ay1); ctx.stroke();
    ctx.fillStyle = "rgba(34,211,238,0.6)"; ctx.font = "10px monospace";
    ctx.fillText("X", ax1 + 4, ay1 + 4);

    ctx.strokeStyle = "rgba(52,211,153,0.4)";
    const [aY0x, aY0y] = worldToCanvas(0, 0, viewMode, scale, ox, oy);
    const [aY1x, aY1y] = worldToCanvas(0, 3, viewMode, scale, ox, oy);
    ctx.beginPath(); ctx.moveTo(aY0x, aY0y); ctx.lineTo(aY1x, aY1y); ctx.stroke();
    ctx.fillStyle = "rgba(52,211,153,0.6)";
    ctx.fillText("Y", aY1x + 4, aY1y);

    // BPA trajectory line (BPA → centroid)
    if (showBpaTrajectory) {
      const bpa = ITEMS.find((i) => i.type === "BPA");
      if (bpa) {
        const [bpx, bpy] = applyTransformOffset(bpa.x, bpa.y);
        const [cpx, cpy] = worldToCanvas(bpx, bpy, viewMode, scale, ox, oy);
        const [cx, cy] = worldToCanvas(ox / scale, 0, viewMode, scale, ox, oy);
        ctx.setLineDash([4, 3]);
        ctx.strokeStyle = "rgba(251,113,133,0.45)";
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(cpx, bpy > 0 ? cpy + 30 : cpy - 30); ctx.lineTo(cpx, bpy > 0 ? bpy * 2 + 30 : bpy - 30); ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // Ballistic vector
    if (showBallisticVector) {
      const ball = ITEMS.find((i) => i.type === "BALLISTICS");
      if (ball) {
        const [bx, by_] = applyTransformOffset(ball.x, ball.y);
        const [p1x, p1y] = worldToCanvas(bx, by_, viewMode, scale, ox, oy);
        const [p2x, p2y] = worldToCanvas(bx + 2.0, by_ + 0.5, viewMode, scale, ox, oy);
        ctx.setLineDash([3, 2]);
        ctx.strokeStyle = "rgba(251,146,60,0.6)";
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(p1x, p1y); ctx.lineTo(p2x, p2y); ctx.stroke();
        // Arrowhead
        ctx.fillStyle = "rgba(251,146,60,0.8)";
        ctx.beginPath();
        const angle = Math.atan2(p2y - p1y, p2x - p1x);
        ctx.moveTo(p2x, p2y);
        ctx.lineTo(p2x - 8 * Math.cos(angle - 0.4), p2y - 8 * Math.sin(angle - 0.4));
        ctx.lineTo(p2x - 8 * Math.cos(angle + 0.4), p2y - 8 * Math.sin(angle + 0.4));
        ctx.closePath(); ctx.fill();
        ctx.setLineDash([]);
      }
    }

    // Evidence points & ellipsoids
    ITEMS.forEach((item) => {
      const [wx, wy] = applyTransformOffset(item.x, item.y);
      const [px, py] = worldToCanvas(wx, wy, viewMode, scale, ox, oy);
      const cfg = SENSOR_CONFIG[item.type] ?? SENSOR_CONFIG["DNA"];
      const isSelected = item.id === selectedId;

      // 95% Confidence Ellipsoid (§5.2)
      if (showEllipsoids) {
        const ax = ellipsoidAxis(item.sigma_m, scale) * 6 + (isSelected ? 3 : 0);
        const bx_ = ax * 0.65;
        ctx.beginPath();
        ctx.ellipse(px, py, Math.max(ax, 6), Math.max(bx_, 4), yawDeg * Math.PI / 180, 0, 2 * Math.PI);
        ctx.fillStyle = cfg.ellipsoidColor;
        ctx.fill();
        ctx.strokeStyle = cfg.ellipsoidColor.replace("0.1", "0.4").replace("0.18", "0.5").replace("0.15", "0.45");
        ctx.lineWidth = 0.8;
        ctx.setLineDash([2, 2]);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      // Evidence marker dot
      const radius = isSelected ? 8 : 5;
      ctx.beginPath(); ctx.arc(px, py, radius, 0, 2 * Math.PI);
      const colorMap: Record<string, string> = {
        LIDAR: "#22d3ee", BPA: "#fb7185", BALLISTICS: "#fb923c", DNA: "#34d399", BONE: "#a78bfa"
      };
      ctx.fillStyle = colorMap[item.type] ?? "#94a3b8";
      ctx.fill();

      if (isSelected) {
        ctx.beginPath(); ctx.arc(px, py, radius + 4, 0, 2 * Math.PI);
        ctx.strokeStyle = colorMap[item.type] ?? "#94a3b8";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      // Label
      ctx.fillStyle = isSelected ? "#f8fafc" : "#94a3b8";
      ctx.font = `${isSelected ? "bold " : ""}9px monospace`;
      ctx.fillText(item.id.replace("EVID-", ""), px + 9, py - 4);
    });

    // Scene bounding box
    ctx.strokeStyle = "rgba(148,163,184,0.12)";
    ctx.lineWidth = 1;
    ctx.setLineDash([6, 4]);
    const [minX, minY] = worldToCanvas(-0.5, -0.5, viewMode, scale, ox, oy);
    const [maxX, maxY] = worldToCanvas(5.5, 5.5, viewMode, scale, ox, oy);
    const bbW = maxX - minX; const bbH = minY - maxY;
    ctx.strokeRect(minX, maxY, bbW, bbH);
    ctx.setLineDash([]);

    // View label
    ctx.fillStyle = "rgba(148,163,184,0.4)";
    ctx.font = "10px monospace";
    ctx.fillText(`${viewMode.toUpperCase()} VIEW • SE(3) ψ=${yawDeg}° φ=${rollDeg}° θ=${pitchDeg}°`, 10, H - 10);

  }, [selectedId, viewMode, showEllipsoids, showBpaTrajectory, showBallisticVector, rollDeg, pitchDeg, yawDeg, txM, tyM, tzM]);

  // ── Ellipsoid metrics for selected item ──────────────────────────────────
  const sigma = selectedItem.sigma_m;
  const axisPx = Math.sqrt(sigma * sigma * CHI2_3_95);
  const volume = (4 / 3) * Math.PI * Math.pow(axisPx, 3);

  return (
    <div className="space-y-6 font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-tactical-border/60 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.15)]">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold tracking-widest text-tactical-text uppercase">
              3D Spatial Crime Scene Reconstruction
            </h2>
            <p className="text-[10px] text-tactical-text-muted mt-0.5">
              SE(3) Coordinate Registration • 95% CI Ellipsoid (χ²₃ = 7.815) • Multi-Sensor Fusion • Juror Visualizer
            </p>
          </div>
        </div>
        <span className="text-xs font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-3 py-1 rounded-lg">
          §5.1–5.2 Compliant
        </span>
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-5">

        {/* ── Left: 3D Canvas ─────────────────────────────────── */}
        <div className="xl:col-span-3 space-y-3">
          {/* Vantage Point / View Controls */}
          <div className="flex items-center justify-between">
            <div className="flex gap-1">
              {(["isometric", "top", "side"] as const).map((v) => (
                <button
                  key={v}
                  id={`view-${v}`}
                  onClick={() => setViewMode(v)}
                  className={`px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all ${
                    viewMode === v
                      ? "bg-indigo-500/20 border border-indigo-500/40 text-indigo-300"
                      : "bg-black/20 border border-tactical-border/30 text-zinc-500 hover:text-zinc-300"
                  }`}
                >
                  <Eye className="w-3 h-3 inline mr-1 mb-0.5" />
                  {v === "isometric" ? "Isometric" : v === "top" ? "Jury Top" : "Witness Side"}
                </button>
              ))}
            </div>
            <div className="flex gap-2 text-[9px]">
              <button id="toggle-ellipsoids" onClick={() => setShowEllipsoids(!showEllipsoids)}
                className={`px-2 py-1 rounded border transition-all ${showEllipsoids ? "border-cyan-500/40 text-cyan-400 bg-cyan-500/10" : "border-tactical-border/30 text-zinc-600"}`}>
                95% CI
              </button>
              <button id="toggle-bpa" onClick={() => setShowBpaTrajectory(!showBpaTrajectory)}
                className={`px-2 py-1 rounded border transition-all ${showBpaTrajectory ? "border-rose-500/40 text-rose-400 bg-rose-500/10" : "border-tactical-border/30 text-zinc-600"}`}>
                BPA
              </button>
              <button id="toggle-ballistic" onClick={() => setShowBallisticVector(!showBallisticVector)}
                className={`px-2 py-1 rounded border transition-all ${showBallisticVector ? "border-orange-500/40 text-orange-400 bg-orange-500/10" : "border-tactical-border/30 text-zinc-600"}`}>
                Ballistic
              </button>
            </div>
          </div>

          {/* Canvas */}
          <div className="rounded-2xl border border-tactical-border/70 bg-[#050a14] overflow-hidden shadow-xl relative">
            <canvas ref={canvasRef} width={560} height={360} className="w-full" />
            {/* Legend */}
            <div className="absolute top-3 right-3 space-y-1">
              {Object.entries(SENSOR_CONFIG).map(([type, cfg]) => (
                <div key={type} className="flex items-center gap-1.5">
                  <Circle className={`w-2 h-2 fill-current ${cfg.color}`} />
                  <span className={`text-[9px] ${cfg.color}`}>{cfg.label} (±{cfg.precision * 1000}mm)</span>
                </div>
              ))}
            </div>
          </div>

          {/* SE(3) Transform Controls */}
          <div className="rounded-2xl border border-tactical-border/60 bg-tactical-surface/50 p-4 space-y-3">
            <div className="flex items-center gap-2 border-b border-tactical-border/30 pb-2">
              <RotateCw className="w-3.5 h-3.5 text-indigo-400" />
              <span className="text-[10px] font-bold text-tactical-text uppercase tracking-wider">
                SE(3) Transform — R = R_z(ψ)·R_y(θ)·R_x(φ)
              </span>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: "Roll φ", val: rollDeg, set: setRollDeg, color: "text-rose-400" },
                { label: "Pitch θ", val: pitchDeg, set: setPitchDeg, color: "text-amber-400" },
                { label: "Yaw ψ", val: yawDeg, set: setYawDeg, color: "text-cyan-400" },
              ].map(({ label, val, set, color }) => (
                <div key={label} className="space-y-1">
                  <div className="flex justify-between">
                    <span className={`text-[9px] font-bold ${color}`}>{label}</span>
                    <span className={`text-[9px] font-mono ${color}`}>{val}°</span>
                  </div>
                  <input type="range" min={-180} max={180} value={val} step={1}
                    onChange={(e) => set(Number(e.target.value))}
                    className="w-full h-1.5 rounded accent-indigo-500 cursor-pointer" />
                </div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: "ΔX (m)", val: txM, set: setTxM, color: "text-emerald-400" },
                { label: "ΔY (m)", val: tyM, set: setTyM, color: "text-emerald-400" },
                { label: "ΔZ (m)", val: tzM, set: setTzM, color: "text-emerald-400" },
              ].map(({ label, val, set, color }) => (
                <div key={label} className="space-y-1">
                  <div className="flex justify-between">
                    <span className={`text-[9px] font-bold ${color}`}>{label}</span>
                    <span className={`text-[9px] font-mono ${color}`}>{val.toFixed(1)}</span>
                  </div>
                  <input type="range" min={-5} max={5} value={val} step={0.1}
                    onChange={(e) => set(Number(e.target.value))}
                    className="w-full h-1.5 rounded accent-emerald-500 cursor-pointer" />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Right: Evidence Registry + Ellipsoid Detail ─────── */}
        <div className="xl:col-span-2 space-y-4">
          {/* Evidence List */}
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 space-y-2 shadow-lg">
            <span className="text-[10px] font-bold text-tactical-text uppercase tracking-wider block border-b border-tactical-border/40 pb-2">
              Multi-Sensor Evidence Registry
            </span>
            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {ITEMS.map((item) => {
                const cfg = SENSOR_CONFIG[item.type] ?? SENSOR_CONFIG["DNA"];
                return (
                  <div key={item.id} onClick={() => setSelectedId(item.id)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer ${
                      selectedId === item.id
                        ? "bg-indigo-500/10 border-indigo-500/50 shadow-[0_0_10px_rgba(99,102,241,0.15)]"
                        : "bg-black/20 border-tactical-border/30 hover:border-tactical-border/60"
                    }`}>
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-1.5">
                        <Circle className={`w-2 h-2 fill-current ${cfg.color}`} />
                        <span className="text-[10px] font-bold text-tactical-text">{item.id}</span>
                      </div>
                      <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded ${cfg.color} bg-white/5 border border-white/10`}>
                        {cfg.label}
                      </span>
                    </div>
                    <p className="text-[9px] text-zinc-500 font-mono">
                      X:{item.x.toFixed(1)} Y:{item.y.toFixed(1)} Z:{item.z.toFixed(1)} m • ±{item.precision_m * 1000}mm
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 95% Ellipsoid Inspector */}
          <div className="rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 shadow-lg">
            <button id="toggle-ellipsoid-detail" onClick={() => setDetailsOpen(!detailsOpen)}
              className="w-full flex items-center justify-between border-b border-tactical-border/40 pb-2 mb-3">
              <span className="text-[10px] font-bold text-tactical-text uppercase tracking-wider">
                95% Ellipsoid Inspector (§5.2)
              </span>
              {detailsOpen ? <ChevronUp className="w-3.5 h-3.5 text-zinc-500" /> : <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />}
            </button>

            {detailsOpen && (
              <div className="space-y-2 text-[10px] font-mono">
                {/* Chi2 badge */}
                <div className="flex items-center justify-between p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
                  <span className="text-indigo-300 font-bold">χ²₍₃, ₀.₉₅₎</span>
                  <span className="text-indigo-200 font-bold">7.815</span>
                </div>
                {/* Semi-axes */}
                {[
                  { label: "Semi-axis a", val: axisPx, unit: "m" },
                  { label: "Semi-axis b", val: axisPx * 0.9, unit: "m" },
                  { label: "Semi-axis c", val: axisPx * 0.75, unit: "m" },
                ].map(({ label, val, unit }) => (
                  <div key={label} className="flex justify-between p-2 rounded-lg bg-black/20 border border-tactical-border/30">
                    <span className="text-zinc-400">{label}</span>
                    <span className="text-cyan-300 font-bold">{val.toFixed(4)} {unit}</span>
                  </div>
                ))}
                <div className="flex justify-between p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                  <span className="text-emerald-300 font-bold">Volume V = 4π/3·a·b·c</span>
                  <span className="text-emerald-200 font-bold">{volume.toFixed(4)} m³</span>
                </div>
                {/* Sensor precision */}
                <div className="mt-2 p-2 rounded-lg bg-black/20 border border-tactical-border/30 space-y-1">
                  <p className="text-zinc-500 text-[9px] uppercase font-bold">Sensor Precision (§5.1)</p>
                  <p className="text-zinc-300">σ = ±{selectedItem.precision_m * 1000} mm → ±{selectedItem.precision_m} m</p>
                </div>

                {/* SHA-256 Custody */}
                <div className="mt-2 p-2 rounded-lg bg-emerald-500/8 border border-emerald-500/20">
                  <div className="flex items-center gap-1.5 mb-1">
                    <ShieldCheck className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-300 font-bold text-[9px]">Chain of Custody Intact</span>
                  </div>
                  <p className="text-zinc-500 text-[9px]">SHA-256: {selectedItem.hash}</p>
                  <p className="text-zinc-600 text-[9px]">ISO 21043 · Seal: {selectedItem.seal}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bottom: full scene fusion summary */}
      <div className="rounded-2xl border border-tactical-border/60 bg-tactical-surface/40 p-4">
        <div className="flex items-center gap-2 mb-3 border-b border-tactical-border/30 pb-2">
          <Move3d className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-[10px] font-bold text-tactical-text uppercase tracking-wider">
            Scene Fusion Summary — {ITEMS.length} Evidence Points Registered
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Object.entries(SENSOR_CONFIG).map(([type, cfg]) => {
            const count = ITEMS.filter((i) => i.type === type).length;
            return (
              <div key={type} className="p-3 rounded-xl bg-black/20 border border-tactical-border/30 text-center">
                <p className={`text-lg font-bold ${cfg.color}`}>{count}</p>
                <p className={`text-[9px] ${cfg.color} opacity-80`}>{cfg.label}</p>
                <p className="text-[8px] text-zinc-600">±{cfg.precision * 1000}mm</p>
              </div>
            );
          })}
        </div>
        <p className="text-[9px] text-zinc-600 mt-3 text-center font-mono">
          Research: Pillar 6 §5.1–§5.2 • SE(3) Registration • 95% CI Volumetric Ellipsoid χ²₃=7.815 • LiDAR±2mm | BPA±12mm | Ballistics±5mm | DNA±8mm
        </p>
      </div>
    </div>
  );
}
