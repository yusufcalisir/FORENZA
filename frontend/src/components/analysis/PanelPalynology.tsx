"use client";

import React from "react";
import GeoForensicIntelligencePanel from "./GeoForensicIntelligencePanel";

/**
 * PanelPalynology - Subsystem 36: Forensic Palynology & Environmental eDNA Metagenomics
 * Computes Relative Pollen Frequency (RPF) normalization, Bray-Curtis dissimilarity,
 * 6-biome ecological habitat attribution, and eDNA spatial regression.
 */
export default function PanelPalynology({
    hideHeaderTabs = true,
}: {
    hideHeaderTabs?: boolean;
}) {
    return <GeoForensicIntelligencePanel initialMode="PALYNOLOGY_EDNA" hideHeaderTabs={hideHeaderTabs} />;
}
