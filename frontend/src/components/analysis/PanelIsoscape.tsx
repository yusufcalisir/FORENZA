"use client";

import React from "react";
import GeoForensicIntelligencePanel from "./GeoForensicIntelligencePanel";

/**
 * PanelIsoscape - Subsystem 34: Multi-Isotope Spatial Isoscapes & Provenancing
 * Evaluates tooth enamel structural carbonate d18O, strontium 87Sr/86Sr,
 * and scalp hair keratin d2H/d18O with Daux-Chenery calibrations and Craig GMWL.
 */
export default function PanelIsoscape({
    hideHeaderTabs = true,
}: {
    hideHeaderTabs?: boolean;
}) {
    return <GeoForensicIntelligencePanel initialMode="ISOSCAPES" hideHeaderTabs={hideHeaderTabs} />;
}
