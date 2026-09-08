"use client";

import React from "react";
import GeoForensicIntelligencePanel from "./GeoForensicIntelligencePanel";

/**
 * PanelRossmo - Subsystem 37: Rossmo Bayesian Geographic Profiling
 * Evaluates Rossmo Criminal Geographic Targeting (CGT) algorithms,
 * Canter circle hypothesis, Marauder vs. Commuter typologies, and Search Efficiency Index (SEI).
 */
export default function PanelRossmo({
    hideHeaderTabs = true,
}: {
    hideHeaderTabs?: boolean;
}) {
    return <GeoForensicIntelligencePanel initialMode="ROSSMO_GEO" hideHeaderTabs={hideHeaderTabs} />;
}
