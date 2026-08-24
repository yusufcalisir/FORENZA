"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldCheck,
  MapPin,
  PackageCheck,
  Crosshair,
  Layers,
  RotateCw,
  Move3d,
  Eye,
  ChevronDown,
  ChevronUp,
  Circle,
  Sliders,
  Sparkles,
  Info,
  CheckCircle2,
  Box,
  Compass,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

// ── Types ─────────────────────────────────────────────────────────────────────
interface EvidenceItem {
  id: string;
  scene: string;
  type: "LIDAR" | "BPA" | "BALLISTICS" | "DNA" | "BONE";
  method: string;
  collector: string;
  seal: string;
  condition: string;
  x: number;
  y: number;
  z: number;
  badge: string;
  hash: string;
  precision_m: number; // §5.1 sensor precision
  sigma_m: number; // Covariance for ellipsoid (isotropic)
}

// ── Sensor config from Research §5.1 ─────────────────────────────────────────
const SENSOR_CONFIG: Record<
  string,
  { color: string; border: string; bg: string; ellipsoidColor: string; label: string; labelTr: string; precision: number }
> = {
  LIDAR: {
    color: "text-cyan-400",
    border: "border-cyan-500/40",
    bg: "bg-cyan-500/10",
    ellipsoidColor: "rgba(34,211,238,0.18)",
    label: "LiDAR TLS",
    labelTr: "LiDAR TLS",
    precision: 0.002,
  },
  BPA: {
    color: "text-rose-400",
    border: "border-rose-500/40",
    bg: "bg-rose-500/10",
    ellipsoidColor: "rgba(251,113,133,0.20)",
    label: "BPA Spatter",
    labelTr: "BPA Leke",
    precision: 0.012,
  },
  BALLISTICS: {
    color: "text-amber-400",
    border: "border-amber-500/40",
    bg: "bg-amber-500/10",
    ellipsoidColor: "rgba(251,146,60,0.18)",
    label: "Ballistics CMC",
    labelTr: "Balistik CMC",
    precision: 0.005,
  },
  DNA: {
    color: "text-emerald-400",
    border: "border-emerald-500/40",
    bg: "bg-emerald-500/10",
    ellipsoidColor: "rgba(52,211,153,0.18)",
    label: "STR Touch DNA",
    labelTr: "STR Temas DNA",
    precision: 0.008,
  },
  BONE: {
    color: "text-purple-400",
    border: "border-purple-500/40",
    bg: "bg-purple-500/10",
    ellipsoidColor: "rgba(167,139,250,0.18)",
    label: "Skeletal aDNA",
    labelTr: "İskelet aDNA",
    precision: 0.008,
  },
};

// CHI2_{3,0.95} = 7.815 (Research §5.2)
const CHI2_3_95 = 7.815;

// Compute ellipsoid semi-axis: a = sqrt(sigma^2 * 7.815) scaled for display
function ellipsoidAxis(sigma_m: number, displayScale: number): number {
  return Math.sqrt(sigma_m * sigma_m * CHI2_3_95) * displayScale;
}

// ── Scene Evidence Data ───────────────────────────────────────────────────────
const ITEMS: EvidenceItem[] = [
  {
    id: "EVID-BLOOD-101",
    scene: "SCENE-2026-001",
    type: "BPA",
    method: "Sterile Cotton Swab",
    collector: "INV-DOE-12",
    seal: "SEAL-112233",
    condition: "Dry Ambient",
    x: 1.5,
    y: 2.2,
    z: 0.4,
    badge: "SEALED",
    hash: "0x8f2a...91b4",
    precision_m: 0.012,
    sigma_m: 0.012,
  },
  {
    id: "EVID-HAIR-102",
    scene: "SCENE-2026-001",
    type: "DNA",
    method: "Sterile Forceps",
    collector: "INV-DOE-12",
    seal: "SEAL-445566",
    condition: "Room Temp",
    x: 3.1,
    y: 0.8,
    z: 0.0,
    badge: "SEALED",
    hash: "0x3c1d...44e9",
    precision_m: 0.008,
    sigma_m: 0.008,
  },
  {
    id: "EVID-TOUCH-103",
    scene: "SCENE-2026-001",
    type: "DNA",
    method: "Tape Lift",
    collector: "INV-SMITH-44",
    seal: "SEAL-998877",
    condition: "Dry Ambient",
    x: 0.9,
    y: 1.4,
    z: 1.1,
    badge: "IN_LAB",
    hash: "0x7e5b...22f0",
    precision_m: 0.008,
    sigma_m: 0.008,
  },
  {
    id: "EVID-BONE-104",
    scene: "SCENE-2026-002",
    type: "BONE",
    method: "Excision",
    collector: "INV-SMITH-44",
    seal: "SEAL-334411",
    condition: "Frozen -20C",
    x: 4.2,
    y: 3.5,
    z: 0.0,
    badge: "FROZEN",
    hash: "0x1a9c...88d2",
    precision_m: 0.008,
    sigma_m: 0.01,
  },
  {
    id: "EVID-LIDAR-001",
    scene: "SCENE-2026-001",
    type: "LIDAR",
    method: "TLS Scan",
    collector: "TECH-UNIT-03",
    seal: "SEAL-773311",
    condition: "Sealed CAD",
    x: 2.5,
    y: 3.8,
    z: 1.5,
    badge: "SCANNED",
    hash: "0x2b3c...11a7",
    precision_m: 0.002,
    sigma_m: 0.002,
  },
  {
    id: "EVID-BALLISTIC",
    scene: "SCENE-2026-001",
    type: "BALLISTICS",
    method: "SEM-EDX CMC",
    collector: "TECH-UNIT-03",
    seal: "SEAL-229944",
    condition: "Dry Ambient",
    x: 0.3,
    y: 0.5,
    z: 1.8,
    badge: "ANALYZED",
    hash: "0x5d8e...33c1",
    precision_m: 0.005,
    sigma_m: 0.005,
  },
];

// ── 2D Canvas Projection (Isometric-like top-down XY) ────────────────────────
function worldToCanvas(
  x: number,
  y: number,
  view: "top" | "side" | "isometric",
  scale: number,
  offsetX: number,
  offsetY: number
): [number, number] {
  switch (view) {
    case "top":
      return [offsetX + x * scale, offsetY - y * scale];
    case "side":
      return [offsetX + x * scale, offsetY - y * scale];
    case "isometric": {
      const ix = (x - y) * Math.cos(Math.PI / 6);
      const iy = (x + y) * Math.sin(Math.PI / 6) - y * 0.5;
      return [offsetX + ix * scale * 0.8, offsetY - iy * scale * 0.8];
    }
  }
}

export default function EvidenceManagementPanel() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedId, setSelectedId] = useState<string>("EVID-BLOOD-101");
  const [viewMode, setViewMode] = useState<"top" | "side" | "isometric">("isometric");
  const [showEllipsoids, setShowEllipsoids] = useState<boolean>(true);
  const [showBpaTrajectory, setShowBpaTrajectory] = useState<boolean>(true);
  const [showBallisticVector, setShowBallisticVector] = useState<boolean>(true);
  const [rollDeg, setRollDeg] = useState<number>(0);
  const [pitchDeg, setPitchDeg] = useState<number>(0);
  const [yawDeg, setYawDeg] = useState<number>(0);
  const [txM, setTxM] = useState<number>(0);
  const [tyM, setTyM] = useState<number>(0);
  const [tzM, setTzM] = useState<number>(0);
  const [detailsOpen, setDetailsOpen] = useState<boolean>(true);

  const selectedItem = ITEMS.find((i) => i.id === selectedId) || ITEMS[0];

  const getLocalizedSensorLabel = (type: string) => {
    if (!isTr) return SENSOR_CONFIG[type]?.label || type;
    return SENSOR_CONFIG[type]?.labelTr || type;
  };

  const getLocalizedMethod = (method: string) => {
    if (!isTr) return method;
    switch (method) {
      case "Sterile Cotton Swab":
        return "Steril Pamuk Sürüntü";
      case "Sterile Forceps":
        return "Steril Pens";
      case "Tape Lift":
        return "Bantla Kaldırma";
      case "Excision":
        return "Kemik Eksizyonu";
      case "TLS Scan":
        return "TLS LiDAR Taraması";
      case "SEM-EDX CMC":
        return "SEM-EDX & 3D CMC";
      default:
        return method;
    }
  };

  const getLocalizedCondition = (cond: string) => {
    if (!isTr) return cond;
    switch (cond) {
      case "Dry Ambient":
        return "Kuru Ortam";
      case "Room Temp":
        return "Oda Sıcaklığı";
      case "Frozen -20C":
        return "Dondurulmuş (-20°C)";
      case "Sealed CAD":
        return "Mühürlü CAD Verisi";
      default:
        return cond;
    }
  };

  const getLocalizedBadge = (badge: string) => {
    if (!isTr) return badge;
    switch (badge) {
      case "SEALED":
        return "MÜHÜRLÜ";
      case "IN_LAB":
        return "LABORATUVARDA";
      case "FROZEN":
        return "DONDURULMUŞ";
      case "SCANNED":
        return "TARANDI";
      case "ANALYZED":
        return "ANALİZ EDİLDİ";
      default:
        return badge;
    }
  };

  // SE(3) transform for display
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
    const scale = 42;
    const ox = W / 2;
    const oy = H / 2 + 15;

    ctx.clearRect(0, 0, W, H);

    // Deep Tactical Background
    ctx.fillStyle = "#050914";
    ctx.fillRect(0, 0, W, H);

    // Grid Lines
    ctx.strokeStyle = "rgba(148,163,184,0.08)";
    ctx.lineWidth = 1;
    for (let gx = -8; gx <= 8; gx++) {
      const [px1, py1] = worldToCanvas(gx, -8, viewMode, scale, ox, oy);
      const [px2, py2] = worldToCanvas(gx, 8, viewMode, scale, ox, oy);
      ctx.beginPath();
      ctx.moveTo(px1, py1);
      ctx.lineTo(px2, py2);
      ctx.stroke();
    }
    for (let gy = -8; gy <= 8; gy++) {
      const [px1, py1] = worldToCanvas(-8, gy, viewMode, scale, ox, oy);
      const [px2, py2] = worldToCanvas(8, gy, viewMode, scale, ox, oy);
      ctx.beginPath();
      ctx.moveTo(px1, py1);
      ctx.lineTo(px2, py2);
      ctx.stroke();
    }

    // Origin Axes
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = "rgba(34,211,238,0.5)";
    const [ax0, ay0] = worldToCanvas(0, 0, viewMode, scale, ox, oy);
    const [ax1, ay1] = worldToCanvas(3.5, 0, viewMode, scale, ox, oy);
    ctx.beginPath();
    ctx.moveTo(ax0, ay0);
    ctx.lineTo(ax1, ay1);
    ctx.stroke();
    ctx.fillStyle = "rgba(34,211,238,0.8)";
    ctx.font = "bold 10px monospace";
    ctx.fillText("+X (3.5m)", ax1 + 4, ay1 + 4);

    ctx.strokeStyle = "rgba(52,211,153,0.5)";
    const [aY0x, aY0y] = worldToCanvas(0, 0, viewMode, scale, ox, oy);
    const [aY1x, aY1y] = worldToCanvas(0, 3.5, viewMode, scale, ox, oy);
    ctx.beginPath();
    ctx.moveTo(aY0x, aY0y);
    ctx.lineTo(aY1x, aY1y);
    ctx.stroke();
    ctx.fillStyle = "rgba(52,211,153,0.8)";
    ctx.fillText("+Y (3.5m)", aY1x + 4, aY1y);

    // BPA trajectory line (BPA → centroid)
    if (showBpaTrajectory) {
      const bpa = ITEMS.find((i) => i.type === "BPA");
      if (bpa) {
        const [bpx, bpy] = applyTransformOffset(bpa.x, bpa.y);
        const [cpx, cpy] = worldToCanvas(bpx, bpy, viewMode, scale, ox, oy);
        ctx.setLineDash([4, 3]);
        ctx.strokeStyle = "rgba(251,113,133,0.6)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(cpx, bpy > 0 ? cpy + 35 : cpy - 35);
        ctx.lineTo(cpx, bpy > 0 ? bpy * 2 + 35 : bpy - 35);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // Ballistic trajectory vector
    if (showBallisticVector) {
      const ball = ITEMS.find((i) => i.type === "BALLISTICS");
      if (ball) {
        const [bx, by_] = applyTransformOffset(ball.x, ball.y);
        const [p1x, p1y] = worldToCanvas(bx, by_, viewMode, scale, ox, oy);
        const [p2x, p2y] = worldToCanvas(bx + 2.2, by_ + 0.6, viewMode, scale, ox, oy);
        ctx.setLineDash([3, 2]);
        ctx.strokeStyle = "rgba(251,146,60,0.75)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(p1x, p1y);
        ctx.lineTo(p2x, p2y);
        ctx.stroke();
        // Arrowhead
        ctx.fillStyle = "rgba(251,146,60,0.9)";
        ctx.beginPath();
        const angle = Math.atan2(p2y - p1y, p2x - p1x);
        ctx.moveTo(p2x, p2y);
        ctx.lineTo(p2x - 9 * Math.cos(angle - 0.4), p2y - 9 * Math.sin(angle - 0.4));
        ctx.lineTo(p2x - 9 * Math.cos(angle + 0.4), p2y - 9 * Math.sin(angle + 0.4));
        ctx.closePath();
        ctx.fill();
        ctx.setLineDash([]);
      }
    }

    // Evidence points & ellipsoids
    ITEMS.forEach((item, index) => {
      const [wx, wy] = applyTransformOffset(item.x, item.y);
      const [px, py] = worldToCanvas(wx, wy, viewMode, scale, ox, oy);
      const cfg = SENSOR_CONFIG[item.type] ?? SENSOR_CONFIG["DNA"];
      const isSelected = item.id === selectedId;

      // 95% Confidence Ellipsoid (§5.2)
      if (showEllipsoids) {
        const ax = ellipsoidAxis(item.sigma_m, scale) * 5.5 + (isSelected ? 3 : 0);
        const bx_ = ax * 0.68;
        ctx.beginPath();
        ctx.ellipse(px, py, Math.max(ax, 7), Math.max(bx_, 5), ((yawDeg * Math.PI) / 180), 0, 2 * Math.PI);
        ctx.fillStyle = cfg.ellipsoidColor;
        ctx.fill();
        ctx.strokeStyle = isSelected ? "rgba(255,255,255,0.7)" : cfg.ellipsoidColor.replace("0.18", "0.55");
        ctx.lineWidth = isSelected ? 1.2 : 0.8;
        ctx.setLineDash([2, 2]);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      // Evidence marker dot
      const radius = isSelected ? 8 : 5;
      ctx.beginPath();
      ctx.arc(px, py, radius, 0, 2 * Math.PI);
      const colorMap: Record<string, string> = {
        LIDAR: "#22d3ee",
        BPA: "#fb7185",
        BALLISTICS: "#fb923c",
        DNA: "#34d399",
        BONE: "#a78bfa",
      };
      ctx.fillStyle = colorMap[item.type] ?? "#94a3b8";
      ctx.fill();

      if (isSelected) {
        ctx.beginPath();
        ctx.arc(px, py, radius + 4, 0, 2 * Math.PI);
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.8;
        ctx.stroke();
      }

      // Smart staggered label with high-contrast pill
      const labelText = item.id.replace("EVID-", "");
      ctx.font = `${isSelected ? "bold " : ""}10px monospace`;
      const textWidth = ctx.measureText(labelText).width;

      const labelYOffset = index % 2 === 0 ? -9 : 15;
      const labelXOffset = index % 3 === 2 ? -textWidth - 10 : 10;

      ctx.fillStyle = isSelected ? "rgba(15, 23, 42, 0.95)" : "rgba(3, 7, 18, 0.88)";
      ctx.fillRect(px + labelXOffset - 3, py + labelYOffset - 9, textWidth + 6, 13);
      ctx.strokeStyle = isSelected ? colorMap[item.type] : "rgba(255,255,255,0.2)";
      ctx.lineWidth = isSelected ? 1.2 : 0.6;
      ctx.strokeRect(px + labelXOffset - 3, py + labelYOffset - 9, textWidth + 6, 13);

      ctx.fillStyle = isSelected ? "#ffffff" : "#cbd5e1";
      ctx.fillText(labelText, px + labelXOffset, py + labelYOffset);
    });

    // Scene bounding box
    ctx.strokeStyle = "rgba(148,163,184,0.15)";
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 4]);
    const [minX, minY] = worldToCanvas(-0.5, -0.5, viewMode, scale, ox, oy);
    const [maxX, maxY] = worldToCanvas(5.5, 5.5, viewMode, scale, ox, oy);
    const bbW = maxX - minX;
    const bbH = minY - maxY;
    ctx.strokeRect(minX, maxY, bbW, bbH);
    ctx.setLineDash([]);

    // Viewport Telemetry Info
    ctx.fillStyle = "rgba(148,163,184,0.7)";
    ctx.font = "10px monospace";
    ctx.fillText(`${viewMode.toUpperCase()} VIEW • SE(3) ψ=${yawDeg}° φ=${rollDeg}° θ=${pitchDeg}° • Δ(${txM.toFixed(1)}, ${tyM.toFixed(1)}, ${tzM.toFixed(1)})m`, 12, H - 12);
  }, [selectedId, viewMode, showEllipsoids, showBpaTrajectory, showBallisticVector, rollDeg, pitchDeg, yawDeg, txM, tyM, tzM]);

  // ── Ellipsoid metrics for selected item ──────────────────────────────────
  const sigma = selectedItem.sigma_m;
  const axisPx = Math.sqrt(sigma * sigma * CHI2_3_95);
  const volume = (4 / 3) * Math.PI * Math.pow(axisPx, 3);

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* ── Top Unified Command & Standards Mission Bar ──────────────────────── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-2xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-3 min-w-0">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400 shrink-0 shadow-sm">
              <Move3d className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-sm sm:text-base font-bold text-white tracking-tight uppercase truncate">
                  {isTr ? "3B Mekânsal Olay Yeri Rekonstrüksiyonu & Jüri Görselleştiricisi" : "3D Spatial Crime Scene Reconstruction & Juror Visualizer"}
                </h2>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-indigo-500/10 border border-indigo-500/30 text-indigo-300">
                  ISO 21043 • SE(3) • χ²₃=7.815
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5 truncate">
                {isTr
                  ? "Pillar 6 §5 • Çok Sensörlü Füzyon (LiDAR, BPA, Balistik, DNA) • %95 Hacimsel Olasılık Elipsoidi • SE(3) Kinematik Tescil"
                  : "Pillar 6 §5 • Multi-Sensor Fusion (LiDAR, BPA, Ballistics, DNA) • 95% Volumetric Probability Ellipsoid • SE(3) Kinematic Registration"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <span className="text-[10px] font-bold px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-1.5 shadow-sm">
              <ShieldCheck className="w-3.5 h-3.5" />
              {isTr ? "6/6 Delil Noktası Tescilli" : "6/6 Registered Coordinates"}
            </span>
          </div>
        </div>

        {/* Sensor Spectrum Mini-Summary Row */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-1">
          {Object.entries(SENSOR_CONFIG).map(([type, cfg]) => {
            const count = ITEMS.filter((i) => i.type === type).length;
            return (
              <div
                key={type}
                className={`p-2.5 rounded-xl border ${cfg.border} ${cfg.bg} flex items-center justify-between shadow-sm`}
              >
                <div className="flex items-center gap-2">
                  <Circle className={`w-2.5 h-2.5 fill-current ${cfg.color} shrink-0`} />
                  <div>
                    <span className="text-[11px] font-bold text-white block leading-tight">
                      {isTr ? cfg.labelTr : cfg.label}
                    </span>
                    <span className="text-[9px] text-zinc-400 font-mono">±{cfg.precision * 1000}mm</span>
                  </div>
                </div>
                <span className={`text-xs font-black ${cfg.color} font-mono px-2 py-0.5 rounded bg-black/40 border border-white/10`}>
                  N={count}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Main Dual-Column Interactive Workspace (7 / 5 Layout) ──────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ── Left Column: 3D Viewport & SE(3) Transform Controls (7 Cols) ───── */}
        <div className="lg:col-span-7 space-y-4">
          {/* Viewport Card */}
          <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-2xl space-y-3.5">
            {/* Viewport Header Controls Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 border-b border-tactical-border/40 pb-3">
              {/* View Modes Selector */}
              <div className="flex items-center gap-1 bg-black/60 p-1 rounded-xl border border-tactical-border/60">
                {(["isometric", "top", "side"] as const).map((v) => (
                  <button
                    key={v}
                    id={`view-${v}`}
                    onClick={() => setViewMode(v)}
                    className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all flex items-center gap-1.5 cursor-pointer ${
                      viewMode === v
                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                        : "text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
                    }`}
                  >
                    <Eye className="w-3 h-3 shrink-0" />
                    <span>
                      {v === "isometric"
                        ? isTr
                          ? "İzometrik"
                          : "Isometric"
                        : v === "top"
                        ? isTr
                          ? "Jüri Üstten"
                          : "Jury Top"
                        : isTr
                        ? "Tanık Yandan"
                        : "Witness Side"}
                    </span>
                  </button>
                ))}
              </div>

              {/* Layer Display Toggles */}
              <div className="flex items-center gap-1.5 flex-wrap">
                <button
                  id="toggle-ellipsoids"
                  onClick={() => setShowEllipsoids(!showEllipsoids)}
                  className={`px-2.5 py-1.5 rounded-lg border text-[10px] font-bold transition-all flex items-center gap-1 cursor-pointer ${
                    showEllipsoids
                      ? "border-cyan-500/60 bg-cyan-500/20 text-cyan-300 shadow-sm"
                      : "border-tactical-border/50 bg-black/40 text-zinc-500"
                  }`}
                >
                  <Crosshair className="w-3 h-3 shrink-0" />
                  {isTr ? "%95 GA Elipsoit" : "95% CI Ellipsoids"}
                </button>
                <button
                  id="toggle-bpa"
                  onClick={() => setShowBpaTrajectory(!showBpaTrajectory)}
                  className={`px-2.5 py-1.5 rounded-lg border text-[10px] font-bold transition-all flex items-center gap-1 cursor-pointer ${
                    showBpaTrajectory
                      ? "border-rose-500/60 bg-rose-500/20 text-rose-300 shadow-sm"
                      : "border-tactical-border/50 bg-black/40 text-zinc-500"
                  }`}
                >
                  BPA
                </button>
                <button
                  id="toggle-ballistic"
                  onClick={() => setShowBallisticVector(!showBallisticVector)}
                  className={`px-2.5 py-1.5 rounded-lg border text-[10px] font-bold transition-all flex items-center gap-1 cursor-pointer ${
                    showBallisticVector
                      ? "border-amber-500/60 bg-amber-500/20 text-amber-300 shadow-sm"
                      : "border-tactical-border/50 bg-black/40 text-zinc-500"
                  }`}
                >
                  {isTr ? "Balistik" : "Ballistics"}
                </button>
              </div>
            </div>

            {/* 3D Canvas Box */}
            <div className="rounded-xl border border-tactical-border/70 bg-[#050914] overflow-hidden shadow-inner relative flex justify-center items-center">
              <canvas
                ref={canvasRef}
                width={640}
                height={380}
                className="w-full h-auto block max-h-[420px]"
              />
            </div>

            {/* Canvas Legend Bar */}
            <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-xl bg-black/50 border border-tactical-border/40 text-[10px] font-mono">
              <div className="flex items-center gap-3 flex-wrap">
                {Object.entries(SENSOR_CONFIG).map(([type, cfg]) => (
                  <div key={type} className="flex items-center gap-1.5">
                    <Circle className={`w-2.5 h-2.5 fill-current ${cfg.color} shrink-0`} />
                    <span className={`${cfg.color} font-medium`}>
                      {isTr ? cfg.labelTr : cfg.label}
                    </span>
                  </div>
                ))}
              </div>
              <span className="text-zinc-500 text-[9px]">
                {isTr ? "Tıklayarak delili seçin" : "Click registry item to inspect"}
              </span>
            </div>
          </div>

          {/* SE(3) Rigid Body Kinematics & Coordinate Transform Card */}
          <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2.5">
              <div className="flex items-center gap-2">
                <RotateCw className="w-4 h-4 text-indigo-400 shrink-0" />
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  {isTr
                    ? "SE(3) Kinematik Dönüşüm  -  R = R_z(ψ) · R_y(θ) · R_x(φ)"
                    : "SE(3) Kinematic Transform  -  R = R_z(ψ) · R_y(θ) · R_x(φ)"}
                </span>
              </div>
              <button
                onClick={() => {
                  setRollDeg(0);
                  setPitchDeg(0);
                  setYawDeg(0);
                  setTxM(0);
                  setTyM(0);
                  setTzM(0);
                }}
                className="text-[10px] font-bold text-zinc-400 hover:text-indigo-300 transition-colors uppercase cursor-pointer"
              >
                {isTr ? "Sıfırla" : "Reset Origin"}
              </button>
            </div>

            {/* Rotational DOF (Euler Angles) */}
            <div className="space-y-2">
              <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
                {isTr ? "3-Serbestlik Dereceli Rotasyon (Euler Açıları):" : "3-DOF Rotational Rigidity (Euler Angles):"}
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { label: isTr ? "Yalpalama φ (Roll)" : "Roll φ", val: rollDeg, set: setRollDeg, color: "text-rose-400", accent: "accent-rose-500" },
                  { label: isTr ? "Yunuslama θ (Pitch)" : "Pitch θ", val: pitchDeg, set: setPitchDeg, color: "text-amber-400", accent: "accent-amber-500" },
                  { label: isTr ? "Sapma ψ (Yaw)" : "Yaw ψ", val: yawDeg, set: setYawDeg, color: "text-cyan-400", accent: "accent-cyan-500" },
                ].map(({ label, val, set, color, accent }) => (
                  <div key={label} className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1.5">
                    <div className="flex justify-between items-center text-xs">
                      <span className={`font-bold ${color}`}>{label}</span>
                      <span className="font-mono font-black text-white bg-black/60 px-1.5 py-0.5 rounded border border-white/10">{val}°</span>
                    </div>
                    <input
                      type="range"
                      min={-180}
                      max={180}
                      value={val}
                      step={1}
                      onChange={(e) => set(Number(e.target.value))}
                      className={`w-full h-1.5 rounded cursor-pointer ${accent}`}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Translational DOF (Displacement Vector) */}
            <div className="space-y-2">
              <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
                {isTr ? "3-Serbestlik Dereceli Öteleme Vektörü (t_XYZ):" : "3-DOF Translation Displacement Vector (t_XYZ):"}
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { label: isTr ? "Öteleme ΔX" : "Shift ΔX", val: txM, set: setTxM },
                  { label: isTr ? "Öteleme ΔY" : "Shift ΔY", val: tyM, set: setTyM },
                  { label: isTr ? "Öteleme ΔZ" : "Shift ΔZ", val: tzM, set: setTzM },
                ].map(({ label, val, set }) => (
                  <div key={label} className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1.5">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-emerald-400">{label}</span>
                      <span className="font-mono font-black text-white bg-black/60 px-1.5 py-0.5 rounded border border-white/10">{val.toFixed(1)} m</span>
                    </div>
                    <input
                      type="range"
                      min={-5}
                      max={5}
                      value={val}
                      step={0.1}
                      onChange={(e) => set(Number(e.target.value))}
                      className="w-full h-1.5 rounded accent-emerald-500 cursor-pointer"
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* ── Right Column: Multi-Sensor Inventory & 95% Ellipsoid Detail (5 Cols) ─ */}
        <div className="lg:col-span-5 space-y-4">
          {/* Multi-Sensor Evidence Inventory */}
          <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-3">
            <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2.5">
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                {isTr ? "Çok Sensörlü Delil Envanteri" : "Multi-Sensor Evidence Registry"}
              </span>
              <span className="text-[10px] text-zinc-400 font-mono">N={ITEMS.length} Delil</span>
            </div>

            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
              {ITEMS.map((item) => {
                const cfg = SENSOR_CONFIG[item.type] ?? SENSOR_CONFIG["DNA"];
                const isSelected = selectedId === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setSelectedId(item.id)}
                    className={`w-full p-3 rounded-xl border text-left transition-all cursor-pointer ${
                      isSelected
                        ? "bg-indigo-600/15 border-indigo-500 text-white shadow-lg shadow-indigo-500/10"
                        : "bg-black/30 border-tactical-border/40 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <Circle className={`w-2.5 h-2.5 fill-current ${cfg.color} shrink-0`} />
                        <span className="text-xs font-bold text-white">{item.id}</span>
                      </div>
                      <span className={`text-[9px] font-bold px-2 py-0.5 rounded-md ${cfg.bg} ${cfg.color} border ${cfg.border}`}>
                        {getLocalizedSensorLabel(item.type)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] font-mono text-zinc-400 mt-1">
                      <span>X:{item.x.toFixed(1)}m · Y:{item.y.toFixed(1)}m · Z:{item.z.toFixed(1)}m</span>
                      <span className="text-zinc-500 font-bold">±{item.precision_m * 1000}mm</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 95% Volumetric Probability Ellipsoid Inspector (§5.2) */}
          <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-3.5">
            <button
              id="toggle-ellipsoid-detail"
              onClick={() => setDetailsOpen(!detailsOpen)}
              className="w-full flex items-center justify-between border-b border-tactical-border/40 pb-2.5 cursor-pointer text-left"
            >
              <div className="flex items-center gap-2">
                <Crosshair className="w-4 h-4 text-cyan-400 shrink-0" />
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  {isTr ? "%95 Hacimsel Elipsoit Denetçisi (§5.2)" : "95% Volumetric Ellipsoid Inspector (§5.2)"}
                </span>
              </div>
              {detailsOpen ? <ChevronUp className="w-4 h-4 text-zinc-400" /> : <ChevronDown className="w-4 h-4 text-zinc-400" />}
            </button>

            {detailsOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-3 text-xs font-mono"
              >
                {/* Chi-Square Invariant Badge */}
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    <span className="text-xs font-bold text-indigo-200">
                      {isTr ? "Ki-Kare Kritik Değeri χ²₍₃, ₀.₉₅₎:" : "Chi-Square Invariant χ²₍₃, ₀.₉₅₎:"}
                    </span>
                  </div>
                  <span className="text-xs font-black text-indigo-300 font-mono">7.815</span>
                </div>

                {/* Semi-Axes 3-Column Grid */}
                <div className="grid grid-cols-3 gap-2 text-center">
                  {[
                    { label: isTr ? "Yarı-eksen a" : "Semi-axis a", val: axisPx },
                    { label: isTr ? "Yarı-eksen b" : "Semi-axis b", val: axisPx * 0.9 },
                    { label: isTr ? "Yarı-eksen c" : "Semi-axis c", val: axisPx * 0.75 },
                  ].map(({ label, val }) => (
                    <div key={label} className="p-2 rounded-xl bg-black/40 border border-tactical-border/40">
                      <span className="text-[10px] text-zinc-400 block">{label}</span>
                      <span className="text-xs font-bold text-cyan-300 font-mono">{val.toFixed(4)} m</span>
                    </div>
                  ))}
                </div>

                {/* Total Ellipsoid Volume */}
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
                  <span className="text-xs font-bold text-emerald-300">
                    {isTr ? "Hacim V = (4/3)·π·a·b·c:" : "Volume V = (4/3)·π·a·b·c:"}
                  </span>
                  <span className="text-xs font-black text-emerald-200 font-mono">{volume.toFixed(5)} m³</span>
                </div>

                {/* Selected Item Sensor & Collection Specification */}
                <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1.5 text-[11px]">
                  <div className="flex items-center justify-between text-zinc-300 font-bold border-b border-tactical-border/30 pb-1">
                    <span>{selectedItem.id}</span>
                    <span className="text-cyan-400">σ = ±{selectedItem.precision_m * 1000} mm</span>
                  </div>
                  <div className="flex justify-between text-zinc-400">
                    <span>{isTr ? "Yöntem:" : "Method:"}</span>
                    <span className="text-zinc-200 font-medium">{getLocalizedMethod(selectedItem.method)}</span>
                  </div>
                  <div className="flex justify-between text-zinc-400">
                    <span>{isTr ? "Koşul:" : "Condition:"}</span>
                    <span className="text-zinc-200 font-medium">{getLocalizedCondition(selectedItem.condition)}</span>
                  </div>
                </div>

                {/* SHA-256 Chain of Custody Proof Card */}
                <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/40 space-y-1 text-[10px]">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>{isTr ? "Delil Zinciri Bozulmamış" : "Chain of Custody Intact"}</span>
                    </div>
                    <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                      {getLocalizedBadge(selectedItem.badge)}
                    </span>
                  </div>
                  <div className="text-zinc-400 flex justify-between pt-1">
                    <span>SHA-256:</span>
                    <span className="font-mono text-zinc-300">{selectedItem.hash}</span>
                  </div>
                  <div className="text-zinc-500 flex justify-between">
                    <span>{isTr ? "Mühür Kodu:" : "Custody Seal:"}</span>
                    <span className="font-mono text-zinc-400">ISO 21043 · {selectedItem.seal}</span>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>

      {/* ── Bottom Section: Complete Scene Fusion & Multi-Sensor Resolution ── */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-3">
        <div className="flex items-center gap-2 border-b border-tactical-border/40 pb-2.5">
          <Layers className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            {isTr
              ? `Olay Yeri Füzyon Özeti  -  ${ITEMS.length} Delil Noktası Kayıtlı (ISO 21043)`
              : `Scene Fusion Summary  -  ${ITEMS.length} Evidence Points Registered (ISO 21043)`}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {Object.entries(SENSOR_CONFIG).map(([type, cfg]) => {
            const count = ITEMS.filter((i) => i.type === type).length;
            return (
              <div
                key={type}
                className={`p-3.5 rounded-xl border ${cfg.border} bg-black/40 text-center space-y-1`}
              >
                <p className={`text-xl font-extrabold ${cfg.color} font-mono`}>{count}</p>
                <p className={`text-xs font-bold text-white`}>{isTr ? cfg.labelTr : cfg.label}</p>
                <p className="text-[10px] text-zinc-400 font-mono">±{cfg.precision * 1000}mm</p>
              </div>
            );
          })}
        </div>

        <div className="p-3 rounded-xl bg-black/30 border border-tactical-border/30 text-[10px] text-zinc-400 font-mono text-center">
          {isTr
            ? "Standart: ISO 21043 • SE(3) Koordinat Tescili • %95 GA Hacimsel Olasılık Elipsoidi χ²₃=7.815 • LiDAR (±2mm) | BPA (±12mm) | Balistik (±5mm) | DNA (±8mm)"
            : "Standard: ISO 21043 • SE(3) Registration • 95% CI Volumetric Probability Ellipsoid χ²₃=7.815 • LiDAR (±2mm) | BPA (±12mm) | Ballistics (±5mm) | DNA (±8mm)"}
        </div>
      </div>
    </div>
  );
}
