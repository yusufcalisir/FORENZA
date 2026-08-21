"use client";

import { useMemo, useState, useEffect, useRef, useCallback } from "react";
import { MapContainer, TileLayer, Circle, CircleMarker, Tooltip, Pane, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

export interface GeoProbability {
    region: string;
    regionTr?: string;
    lat: number;
    lng: number;
    probability: number;
    color: string;
    initial_radius_km?: number;
    final_radius_km?: number;
}

export type ScanPhase = "idle" | "scanning" | "calculating" | "locked";

// ═══════════════════════════════════════════════════════════════════════════════
// MAP INITIALIZER & RESIZER (Fixes Leaflet gray tiles & wrong 0,0 center)
// ═══════════════════════════════════════════════════════════════════════════════

function MapInitializer({ lat, lng, zoom }: { lat: number; lng: number; zoom: number }) {
    const map = useMap();

    useEffect(() => {
        if (!map) return;

        // Force Leaflet to recalculate container dimensions immediately and after 200ms
        map.invalidateSize();
        map.setView([lat, lng], zoom, { animate: false });

        const timer = setTimeout(() => {
            map.invalidateSize();
            map.setView([lat, lng], zoom, { animate: true });
        }, 200);

        return () => clearTimeout(timer);
    }, [map, lat, lng, zoom]);

    return null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// HEATMAP LAYER (Modern Translucent Luminescent Density Gradient)
// ═══════════════════════════════════════════════════════════════════════════════

function HeatmapLayer({ data }: { data: GeoProbability[] }) {
    const map = useMap();
    const isMounted = useRef(true);
    const layerRef = useRef<L.Layer | null>(null);

    useEffect(() => {
        const original = HTMLCanvasElement.prototype.getContext;
        // @ts-ignore
        HTMLCanvasElement.prototype.getContext = function (type: string, attrs?: Record<string, unknown>) {
            if (type === "2d") {
                attrs = { willReadFrequently: true, ...attrs };
            }
            // @ts-ignore
            return original.call(this, type, attrs);
        };
        return () => {
            HTMLCanvasElement.prototype.getContext = original;
        };
    }, []);

    useEffect(() => {
        isMounted.current = true;
        return () => { isMounted.current = false; };
    }, []);

    useEffect(() => {
        if (!data || data.length === 0) return;

        import("leaflet.heat").then(() => {
            if (!isMounted.current || !map) return;

            if (layerRef.current) {
                map.removeLayer(layerRef.current);
                layerRef.current = null;
            }

            const points: [number, number, number][] = data.map((d) => [
                d.lat,
                d.lng,
                d.probability,
            ]);

            // @ts-ignore
            const layer = L.heatLayer(points, {
                radius: 40,
                blur: 28,
                maxZoom: 7,
                max: 1.0,
                minOpacity: 0.05,
                gradient: {
                    0.0: "rgba(0, 0, 0, 0)",
                    0.25: "rgba(6, 182, 212, 0.18)",   // Electric Cyan
                    0.50: "rgba(59, 130, 246, 0.32)",  // Deep Cobalt
                    0.75: "rgba(139, 92, 246, 0.45)",  // Ultraviolet
                    0.90: "rgba(236, 72, 153, 0.55)",  // Neon Magenta
                    1.00: "rgba(244, 63, 94, 0.65)",   // Soft Rose Core
                },
            });

            layer.addTo(map);
            layerRef.current = layer;
        });

        return () => {
            if (layerRef.current) {
                map.removeLayer(layerRef.current);
                layerRef.current = null;
            }
        };
    }, [data, map]);

    return null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCAN CONTROLLER
// ═══════════════════════════════════════════════════════════════════════════════

function ScanController({
    target,
    onPhaseChange,
}: {
    target: GeoProbability;
    onPhaseChange: (phase: ScanPhase) => void;
}) {
    const map = useMap();
    const currentTargetRef = useRef<string | null>(null);

    useEffect(() => {
        if (!target || typeof target.lat !== "number" || typeof target.lng !== "number") return;
        const targetKey = `${target.region}_${target.lat.toFixed(3)}_${target.lng.toFixed(3)}`;
        if (targetKey === currentTargetRef.current) return;
        currentTargetRef.current = targetKey;

        onPhaseChange("scanning");

        const t1 = setTimeout(() => {
            map.flyTo([target.lat, target.lng], 5, { duration: 1.6 });
            onPhaseChange("calculating");
        }, 300);

        const t2 = setTimeout(() => {
            map.flyTo([target.lat, target.lng], 6, { duration: 1.0 });
            onPhaseChange("locked");
        }, 1800);

        return () => {
            clearTimeout(t1);
            clearTimeout(t2);
        };
    }, [target?.region, target?.lat, target?.lng, map, onPhaseChange]);

    return null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIDENCE RING
// ═══════════════════════════════════════════════════════════════════════════════

function ConfidenceRing({
    region,
    phase,
    onHover,
}: {
    region: GeoProbability;
    phase: ScanPhase;
    onHover?: (region: string | null) => void;
}) {
    const initialR = (region.initial_radius_km || 300) * 1000;
    const finalR = (region.final_radius_km || 50) * 1000;
    const [currentRadius, setCurrentRadius] = useState(initialR);
    const animRef = useRef<number | null>(null);
    const startTimeRef = useRef<number | null>(null);

    const ANIMATION_DURATION = 2000;

    useEffect(() => {
        if (phase === "idle") {
            setCurrentRadius(initialR);
            startTimeRef.current = null;
            return;
        }

        if (phase === "scanning" && !startTimeRef.current) {
            startTimeRef.current = performance.now();
        }

        if (phase !== "locked" && startTimeRef.current) {
            const animate = (now: number) => {
                const elapsed = now - (startTimeRef.current || now);
                const progress = Math.min(elapsed / ANIMATION_DURATION, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                const r = initialR + (finalR - initialR) * eased;
                setCurrentRadius(Math.max(r, finalR));
                if (progress < 1) animRef.current = requestAnimationFrame(animate);
            };
            animRef.current = requestAnimationFrame(animate);
        }

        if (phase === "locked") {
            setCurrentRadius(finalR);
            startTimeRef.current = null;
        }

        return () => {
            if (animRef.current) cancelAnimationFrame(animRef.current);
        };
    }, [phase, initialR, finalR]);

    const isLocked = phase === "locked";
    const isActive = phase === "scanning" || phase === "calculating";
    const { lang } = useSaasLanguage();
    const isTr = lang === "tr";

    // Clean region display name (e.g. "East Asian" or "Sub-Saharan African")
    const rawRegionName = isTr && region.regionTr ? region.regionTr : region.region;
    const cleanRegionName = rawRegionName.replace(/\s*\(.*?\)\s*/g, "").trim() || rawRegionName;

    return (
        <>
            {/* Outer 95% Confidence Spatial Zone */}
            <Circle
                center={[region.lat, region.lng]}
                radius={currentRadius}
                eventHandlers={{
                    mouseover: () => onHover?.(region.region),
                    mouseout: () => onHover?.(null),
                    click: () => onHover?.(region.region),
                }}
                pathOptions={{
                    fillColor: "#22C55E",
                    fillOpacity: isLocked ? 0.08 : 0.04,
                    color: "#22C55E",
                    weight: isActive ? 2 : 1.4,
                    opacity: isActive ? 0.9 : 0.65,
                    dashArray: isActive ? "8 4" : undefined,
                }}
            />

            {/* Inner 50% High-Density Core Contour */}
            <Circle
                center={[region.lat, region.lng]}
                radius={Math.max(currentRadius * 0.45, 20000)}
                pathOptions={{
                    fillColor: "#06B6D4",
                    fillOpacity: isLocked ? 0.05 : 0.02,
                    color: "#06B6D4",
                    weight: 1,
                    opacity: 0.5,
                    dashArray: "4 4",
                }}
            />

            {/* Centroid Precision Reticle Marker */}
            <CircleMarker
                center={[region.lat, region.lng]}
                radius={isLocked ? 7 : 5}
                pathOptions={{
                    fillColor: region.color || "#06b6d4",
                    fillOpacity: 0.95,
                    color: "#ffffff",
                    weight: isLocked ? 2 : 1.5,
                    opacity: 1,
                }}
            >
                <Tooltip
                    permanent={isLocked}
                    direction="top"
                    offset={[0, -10]}
                    className="tactical-centroid-tooltip"
                >
                    <div className="bg-[#080d14]/90 backdrop-blur-md border border-cyan-500/60 text-cyan-300 font-mono text-[9px] px-2 py-0.5 rounded shadow-[0_0_15px_rgba(6,182,212,0.4)] whitespace-nowrap flex items-center gap-1.5 pointer-events-none">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0" />
                        <span className="font-bold text-white tracking-wide">{cleanRegionName}</span>
                        <span className="text-cyan-400 font-bold">{(region.probability * 100).toFixed(0)}%</span>
                    </div>
                </Tooltip>
            </CircleMarker>
        </>
    );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN MAP COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export default function ForensicMap({
    data,
    onScanPhaseChange,
    onRegionHover,
}: {
    data: GeoProbability[];
    kinshipMatches?: any[];
    onScanPhaseChange?: (phase: ScanPhase) => void;
    onRegionHover?: (region: string | null) => void;
}) {
    const { lang } = useSaasLanguage();
    const isTr = lang === "tr";
    const [phase, setPhase] = useState<ScanPhase>("idle");

    const center = useMemo<[number, number]>(() => {
        if (data && data.length > 0 && data[0].lat && data[0].lng) {
            return [data[0].lat, data[0].lng];
        }
        return [52.5200, 13.4050]; // Default Berlin, Germany
    }, [data]);

    const topRegion = data && data.length > 0 ? data[0] : null;

    const handlePhaseChange = useCallback(
        (newPhase: ScanPhase) => {
            setPhase(newPhase);
            onScanPhaseChange?.(newPhase);
        },
        [onScanPhaseChange]
    );

    return (
        <MapContainer
            center={center}
            zoom={5}
            scrollWheelZoom={true}
            zoomControl={false}
            attributionControl={false}
            style={{
                width: "100%",
                height: "100%",
                borderRadius: "0",
                background: "#0A0A0B",
            }}
        >
            <MapInitializer lat={center[0]} lng={center[1]} zoom={5} />

            {/* 1. Dark Base Map (Terrain & Geometry without text labels) */}
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png"
                maxZoom={19}
            />

            {/* 2. Middle Layer: Luminescent Tactical Heatmap */}
            <HeatmapLayer data={data} />

            {/* 3. Top Layer: High-Contrast Crisp Map Labels (Rendered ABOVE heatmap via zIndex: 650) */}
            <Pane name="labels" style={{ zIndex: 650, pointerEvents: "none" }}>
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}{r}.png"
                    maxZoom={19}
                    opacity={0.92}
                />
            </Pane>

            {/* 4. Scanning Controller */}
            {topRegion && (
                <ScanController
                    target={topRegion}
                    onPhaseChange={handlePhaseChange}
                />
            )}

            {/* 5. Precision Confidence Ring & Reticle */}
            {topRegion && (
                <ConfidenceRing
                    region={topRegion}
                    phase={phase}
                    onHover={onRegionHover}
                />
            )}

            {/* 6. Secondary Continental Reference Anchors */}
            {data.slice(1, 4).map((region) => {
                const markerLabel = isTr && region.regionTr ? region.regionTr : region.region;
                return (
                    <CircleMarker
                        key={region.region}
                        center={[region.lat, region.lng]}
                        radius={5}
                        eventHandlers={{
                            mouseover: () => onRegionHover?.(region.region),
                            mouseout: () => onRegionHover?.(null),
                            click: () => onRegionHover?.(region.region),
                        }}
                        pathOptions={{
                            fillColor: region.color,
                            fillOpacity: 0.7,
                            color: "#ffffff",
                            weight: 1,
                            opacity: 0.85,
                        }}
                    >
                        <Tooltip direction="bottom" offset={[0, 8]} className="tactical-centroid-tooltip">
                            <div className="bg-[#080d14]/90 backdrop-blur-md border border-zinc-700/80 text-zinc-300 font-mono text-[8px] px-1.5 py-0.5 rounded whitespace-nowrap">
                                {markerLabel.split("(")[0].trim()} ({(region.probability * 100).toFixed(0)}%)
                            </div>
                        </Tooltip>
                    </CircleMarker>
                );
            })}
        </MapContainer>
    );
}
