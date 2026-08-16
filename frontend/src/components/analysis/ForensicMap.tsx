"use client";

import { useMemo, useState, useEffect, useRef, useCallback } from "react";
import { MapContainer, TileLayer, Circle, CircleMarker, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export interface GeoProbability {
    region: string;
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
// HEATMAP LAYER
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
                radius: 45,
                blur: 30,
                maxZoom: 6,
                max: 1.0,
                minOpacity: 0.15,
                gradient: {
                    0.0: "rgba(0,0,0,0)",
                    0.2: "#1a1a4e",
                    0.4: "#3B82F6",
                    0.6: "#22C55E",
                    0.8: "#F59E0B",
                    1.0: "#EF4444",
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

    return (
        <>
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
                    fillOpacity: isLocked ? 0.15 : 0.08,
                    color: "#22C55E",
                    weight: isActive ? 2 : 1.5,
                    opacity: isActive ? 0.8 : 0.6,
                    dashArray: isActive ? "8 4" : undefined,
                }}
            />
            <CircleMarker
                center={[region.lat, region.lng]}
                radius={isLocked ? 7 : 5}
                pathOptions={{
                    fillColor: region.color || "#06b6d4",
                    fillOpacity: 1,
                    color: "#ffffff",
                    weight: isLocked ? 2 : 1,
                    opacity: 1,
                }}
            />
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

            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                maxZoom={19}
            />

            <HeatmapLayer data={data} />

            {topRegion && (
                <ScanController
                    target={topRegion}
                    onPhaseChange={handlePhaseChange}
                />
            )}

            {topRegion && (
                <ConfidenceRing
                    region={topRegion}
                    phase={phase}
                    onHover={onRegionHover}
                />
            )}

            {data.slice(1, 3).map((region) => (
                <CircleMarker
                    key={region.region}
                    center={[region.lat, region.lng]}
                    radius={6}
                    eventHandlers={{
                        mouseover: () => onRegionHover?.(region.region),
                        mouseout: () => onRegionHover?.(null),
                        click: () => onRegionHover?.(region.region),
                    }}
                    pathOptions={{
                        fillColor: region.color,
                        fillOpacity: 0.6,
                        color: region.color,
                        weight: 1.5,
                        opacity: 0.8,
                    }}
                />
            ))}
        </MapContainer>
    );
}
