/**
 * FORENZA Centralized Forensic Status & Metrics Utility Library
 * 
 * Standardized status calculation, loci completeness thresholds,
 * process integrity verification (PASS/WARN/FAIL), finding severities,
 * and node health definitions across all forensic modules.
 */

// ─── 1. Canonical Constants & STR Loci Thresholds ─────────────────────────────

export const CANONICAL_STR_LOCI_COUNT = 24;
export const COMPLETE_LOCI_THRESHOLD = 24;
export const PARTIAL_LOCI_THRESHOLD = 14;

export type ProfileQualityTier = "complete" | "partial" | "degraded";

/**
 * Standardized evaluation of DNA profile quality based on amplified loci count.
 * - 24 / 24 Loci: Complete Profile
 * - 14-23 Loci: Partial Profile
 * - < 14 Loci: Degraded / Low-Template DNA (LTDNA) Profile
 */
export function calculateLociQuality(
    lociCount: number,
    maxLoci: number = CANONICAL_STR_LOCI_COUNT
): ProfileQualityTier {
    if (lociCount >= maxLoci) return "complete";
    if (lociCount >= PARTIAL_LOCI_THRESHOLD) return "partial";
    return "degraded";
}

/**
 * Generates an accurate, non-misleading forensic badge label with exact ratio.
 * Example: "COMPLETE (24/24 LOCI)", "PARTIAL (18/24 LOCI)", "DEGRADED (11/24 LOCI)"
 */
export function getLociQualityBadgeLabel(
    lociCount: number,
    maxLoci: number = CANONICAL_STR_LOCI_COUNT
): string {
    const quality = calculateLociQuality(lociCount, maxLoci);
    switch (quality) {
        case "complete":
            return `COMPLETE (${lociCount}/${maxLoci} LOCI)`;
        case "partial":
            return `PARTIAL (${lociCount}/${maxLoci} LOCI)`;
        case "degraded":
            return `DEGRADED (${lociCount}/${maxLoci} LOCI)`;
    }
}

export const PROFILE_QUALITY_CONFIG: Record<
    ProfileQualityTier,
    {
        label: string;
        shortLabel: string;
        color: string;
        bg: string;
        border: string;
        textColor: string;
        badgeClass: string;
    }
> = {
    complete: {
        label: `COMPLETE (${COMPLETE_LOCI_THRESHOLD} LOCI)`,
        shortLabel: "COMPLETE",
        color: "#22C55E",
        bg: "rgba(34,197,94,0.12)",
        border: "rgba(34,197,94,0.3)",
        textColor: "text-emerald-400",
        badgeClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    },
    partial: {
        label: `PARTIAL (${PARTIAL_LOCI_THRESHOLD}-${COMPLETE_LOCI_THRESHOLD - 1} LOCI)`,
        shortLabel: "PARTIAL",
        color: "#06B6D4",
        bg: "rgba(6,182,212,0.12)",
        border: "rgba(6,182,212,0.3)",
        textColor: "text-cyan-400",
        badgeClass: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30",
    },
    degraded: {
        label: `DEGRADED (<${PARTIAL_LOCI_THRESHOLD} LOCI)`,
        shortLabel: "DEGRADED",
        color: "#EF4444",
        bg: "rgba(239,68,68,0.12)",
        border: "rgba(239,68,68,0.3)",
        textColor: "text-red-400",
        badgeClass: "bg-red-500/10 text-red-400 border-red-500/30",
    },
};

// ─── 2. Chain of Custody & Process Integrity (PASS / WARNING / FAIL) ──────────

export type ProcessIntegrityStatus = "PASS" | "WARNING" | "FAIL" | "PENDING";

export const PROCESS_INTEGRITY_CONFIG: Record<
    ProcessIntegrityStatus,
    {
        label: string;
        color: string;
        bg: string;
        border: string;
        dot: string;
        description: string;
    }
> = {
    PASS: {
        label: "VERIFIED",
        color: "text-emerald-400",
        bg: "bg-emerald-500/10",
        border: "border-emerald-500/30",
        dot: "bg-emerald-400",
        description: "Process execution and HMAC-SHA256 custody integrity verified.",
    },
    WARNING: {
        label: "FLAGGED",
        color: "text-amber-400",
        bg: "bg-amber-500/10",
        border: "border-amber-500/30",
        dot: "bg-amber-400",
        description: "Discrepancy or non-critical tolerance warning detected.",
    },
    FAIL: {
        label: "FAILED",
        color: "text-red-400",
        bg: "bg-red-500/10",
        border: "border-red-500/30",
        dot: "bg-red-400",
        description: "Integrity check failed or critical protocol violation.",
    },
    PENDING: {
        label: "PENDING",
        color: "text-zinc-400",
        bg: "bg-zinc-500/10",
        border: "border-zinc-500/30",
        dot: "bg-zinc-400",
        description: "Awaiting computational confirmation or laboratory accessioning.",
    },
};

// ─── 3. Biological & Analytical Finding Severity ──────────────────────────────

export type FindingSeverity = "NOMINAL" | "INFORMATIONAL" | "ELEVATED" | "CRITICAL_ALERT";

export const FINDING_SEVERITY_CONFIG: Record<
    FindingSeverity,
    {
        label: string;
        color: string;
        bg: string;
        border: string;
        badgeClass: string;
        description: string;
    }
> = {
    CRITICAL_ALERT: {
        label: "CRITICAL ALERT",
        color: "text-rose-400",
        bg: "bg-rose-500/15",
        border: "border-rose-500/40",
        badgeClass: "bg-rose-500/15 text-rose-300 border-rose-500/40",
        description: "Finding exceeds fatal threshold or indicates severe biological/toxicological anomaly.",
    },
    ELEVATED: {
        label: "ELEVATED",
        color: "text-amber-400",
        bg: "bg-amber-500/15",
        border: "border-amber-500/40",
        badgeClass: "bg-amber-500/15 text-amber-300 border-amber-500/40",
        description: "Elevated probability or biomarker deviation requiring analyst review.",
    },
    INFORMATIONAL: {
        label: "INFORMATIONAL",
        color: "text-cyan-400",
        bg: "bg-cyan-500/15",
        border: "border-cyan-500/40",
        badgeClass: "bg-cyan-500/15 text-cyan-300 border-cyan-500/40",
        description: "Routine analytical metric or lineage observation.",
    },
    NOMINAL: {
        label: "NOMINAL",
        color: "text-emerald-400",
        bg: "bg-emerald-500/10",
        border: "border-emerald-500/30",
        badgeClass: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
        description: "Baseline parameters within standard operating tolerances.",
    },
};

// ─── 4. Federated Laboratory Node Health Status ───────────────────────────────

export type NodeHealthStatus = "ONLINE" | "SYNCING" | "DEGRADED" | "OFFLINE";

export const NODE_HEALTH_CONFIG: Record<
    NodeHealthStatus,
    {
        label: string;
        color: string;
        bg: string;
        border: string;
        dot: string;
    }
> = {
    ONLINE: {
        label: "ONLINE",
        color: "text-emerald-400",
        bg: "bg-emerald-500/10",
        border: "border-emerald-500/30",
        dot: "bg-emerald-400",
    },
    SYNCING: {
        label: "SYNCING",
        color: "text-amber-400",
        bg: "bg-amber-500/10",
        border: "border-amber-500/30",
        dot: "bg-amber-400 animate-pulse",
    },
    DEGRADED: {
        label: "DEGRADED",
        color: "text-red-400",
        bg: "bg-red-500/10",
        border: "border-red-500/30",
        dot: "bg-red-400",
    },
    OFFLINE: {
        label: "OFFLINE",
        color: "text-zinc-500",
        bg: "bg-zinc-500/10",
        border: "border-zinc-500/30",
        dot: "bg-zinc-500",
    },
};
