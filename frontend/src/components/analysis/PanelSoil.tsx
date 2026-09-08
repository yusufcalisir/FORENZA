"use client";

import React from "react";
import GeoForensicIntelligencePanel from "./GeoForensicIntelligencePanel";

/**
 * PanelSoil - Subsystem 35: Forensic Soil Pedology, QXRD Mineralogy & Geochemical CoDa
 * Evaluates QXRD Rietveld mineral weight percentages, ZTR maturity index,
 * Hotelling T2 / Mahalanobis distance, and Centered Log-Ratio (CLR) transforms.
 */
export default function PanelSoil({
    hideHeaderTabs = true,
}: {
    hideHeaderTabs?: boolean;
}) {
    return <GeoForensicIntelligencePanel initialMode="SOIL_CODA" hideHeaderTabs={hideHeaderTabs} />;
}
