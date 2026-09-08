"use client";

import React from "react";
import GeoForensicIntelligencePanel from "./GeoForensicIntelligencePanel";

/**
 * PanelGeoFusion - Subsystem 38: Multi-Criteria Bayesian GIS Evidence Fusion
 * Synthesizes multi-layer geospatial evidence surfaces with 2D adaptive KDE,
 * composite log-likelihood ratios, and ISO 17025 / ENFSI 2017 evaluative reporting.
 */
export default function PanelGeoFusion({
    hideHeaderTabs = false,
}: {
    hideHeaderTabs?: boolean;
}) {
    return <GeoForensicIntelligencePanel initialMode="BAYESIAN_FUSION" hideHeaderTabs={hideHeaderTabs} />;
}
