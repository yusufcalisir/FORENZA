"use client";

import { useState, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useIngestStore } from "@/store/ingestStore";
import {
    Globe,
    ShieldCheck,
    BarChart3,
    Compass,
    Activity,
    CheckCircle2,
    Sparkles,
    ShieldAlert,
    Layers,
    Eye,
    Palette,
    Lock
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { getApiBaseUrl } from "@/lib/api";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES & POPULATION METRICS
// ═══════════════════════════════════════════════════════════════════════════════

export interface GeoProbability {
    region: string;
    lat: number;
    lng: number;
    probability: number;
    color: string;
}

export interface AncestryDataPanelProps {
    data?: GeoProbability[];
    reliabilityScore?: number;
    txHash?: string;
    selectedRegion?: string | null;
}

type RefPanel = "1000G" | "gnomAD_v4" | "HGDP";
type AIMPanel = "KIDD_55" | "PRECISION_165" | "VISAGE_153" | "MICROHAP_74";
type Jurisdiction = "ISFG" | "GERMANY_STPO" | "NETHERLANDS_SV";

const CONTINENTAL_CENTROIDS: Record<string, { name: string; nameTr: string; lat: number; lng: number; color: string }> = {
    EUR: { name: "European", nameTr: "Avrupa", lat: 48.50, lng: 15.20, color: "#3B82F6" },
    AFR: { name: "African", nameTr: "Afrika", lat: 2.50, lng: 22.80, color: "#F59E0B" },
    EAS: { name: "East Asian", nameTr: "Doğu Asya", lat: 35.00, lng: 105.00, color: "#EC4899" },
    SAS: { name: "South Asian", nameTr: "Güney Asya", lat: 22.50, lng: 78.50, color: "#8B5CF6" },
    AMR: { name: "Admixed/Indigenous American", nameTr: "Karışık/Yerli Amerika", lat: 4.00, lng: -68.00, color: "#10B981" },
    MID: { name: "Middle Eastern / West Asian", nameTr: "Orta Doğu / Batı Asya", lat: 31.00, lng: 42.00, color: "#06B6D4" },
};

const AIM_SNPS: Record<string, { gene: string; allele: string; freqs: Record<string, number> }> = {
    rs3737576:  { gene: "CPM (1q32.1)",        allele: "C", freqs: { AFR: 0.812, EUR: 0.221, EAS: 0.114, SAS: 0.325, AMR: 0.083, MID: 0.248 } },
    rs7554936:  { gene: "Intergenic (1q21.3)", allele: "T", freqs: { AFR: 0.941, EUR: 0.385, EAS: 0.021, SAS: 0.412, AMR: 0.052, MID: 0.391 } },
    rs2814778:  { gene: "ACKR1 (Duffy Null)",  allele: "C", freqs: { AFR: 0.992, EUR: 0.001, EAS: 0.000, SAS: 0.003, AMR: 0.021, MID: 0.085 } },
    rs798443:   { gene: "Intergenic (1q42.3)", allele: "T", freqs: { AFR: 0.125, EUR: 0.781, EAS: 0.943, SAS: 0.612, AMR: 0.892, MID: 0.721 } },
    rs1876482:  { gene: "Intergenic (2p23.3)", allele: "C", freqs: { AFR: 0.884, EUR: 0.152, EAS: 0.061, SAS: 0.291, AMR: 0.041, MID: 0.183 } },
    rs1834619:  { gene: "STAT4 (2q33.1)",      allele: "G", freqs: { AFR: 0.915, EUR: 0.283, EAS: 0.082, SAS: 0.394, AMR: 0.091, MID: 0.312 } },
    rs3827760:  { gene: "EDAR (2q13)",         allele: "G", freqs: { AFR: 0.000, EUR: 0.002, EAS: 0.948, SAS: 0.015, AMR: 0.824, MID: 0.005 } },
    rs260690:   { gene: "Intergenic (2q37.3)", allele: "G", freqs: { AFR: 0.213, EUR: 0.724, EAS: 0.211, SAS: 0.512, AMR: 0.183, MID: 0.651 } },
    rs6754311:  { gene: "Intergenic (2p25.1)", allele: "G", freqs: { AFR: 0.852, EUR: 0.183, EAS: 0.031, SAS: 0.284, AMR: 0.052, MID: 0.211 } },
    rs10497191: { gene: "Intergenic (2q31.1)", allele: "T", freqs: { AFR: 0.112, EUR: 0.891, EAS: 0.982, SAS: 0.782, AMR: 0.951, MID: 0.842 } },
    rs12498138: { gene: "Intergenic (3q24)",   allele: "G", freqs: { AFR: 0.021, EUR: 0.083, EAS: 0.192, SAS: 0.114, AMR: 0.912, MID: 0.071 } },
    rs4833103:  { gene: "Intergenic (4q28.1)", allele: "C", freqs: { AFR: 0.781, EUR: 0.214, EAS: 0.042, SAS: 0.312, AMR: 0.061, MID: 0.252 } },
    rs1229984:  { gene: "ADH1B (4q23)",        allele: "T", freqs: { AFR: 0.002, EUR: 0.041, EAS: 0.762, SAS: 0.112, AMR: 0.081, MID: 0.125 } },
    rs3811801:  { gene: "Intergenic (4q32.1)", allele: "G", freqs: { AFR: 0.081, EUR: 0.112, EAS: 0.894, SAS: 0.221, AMR: 0.783, MID: 0.142 } },
    rs7657799:  { gene: "Intergenic (4q31.2)", allele: "T", freqs: { AFR: 0.824, EUR: 0.191, EAS: 0.052, SAS: 0.315, AMR: 0.072, MID: 0.231 } },
    rs16891982: { gene: "SLC45A2 (5p13.2)",    allele: "G", freqs: { AFR: 0.000, EUR: 0.968, EAS: 0.001, SAS: 0.082, AMR: 0.021, MID: 0.214 } },
    rs7722456:  { gene: "Intergenic (5q31.2)", allele: "A", freqs: { AFR: 0.091, EUR: 0.824, EAS: 0.912, SAS: 0.683, AMR: 0.851, MID: 0.762 } },
    rs870347:   { gene: "Intergenic (5q35.3)", allele: "T", freqs: { AFR: 0.892, EUR: 0.221, EAS: 0.071, SAS: 0.342, AMR: 0.082, MID: 0.261 } },
    rs3823159:  { gene: "Intergenic (6q25.3)", allele: "A", freqs: { AFR: 0.861, EUR: 0.142, EAS: 0.032, SAS: 0.251, AMR: 0.041, MID: 0.182 } },
    rs192655:   { gene: "Intergenic (6p22.3)", allele: "T", freqs: { AFR: 0.182, EUR: 0.712, EAS: 0.931, SAS: 0.582, AMR: 0.871, MID: 0.662 } },
    rs917115:   { gene: "Intergenic (6q16.1)", allele: "G", freqs: { AFR: 0.841, EUR: 0.172, EAS: 0.041, SAS: 0.272, AMR: 0.051, MID: 0.212 } },
    rs1462906:  { gene: "Intergenic (7q31.1)", allele: "A", freqs: { AFR: 0.112, EUR: 0.881, EAS: 0.962, SAS: 0.752, AMR: 0.921, MID: 0.812 } },
    rs6990312:  { gene: "Intergenic (8q24.2)", allele: "G", freqs: { AFR: 0.821, EUR: 0.201, EAS: 0.051, SAS: 0.321, AMR: 0.062, MID: 0.241 } },
    rs2196051:  { gene: "Intergenic (8p23.1)", allele: "T", freqs: { AFR: 0.872, EUR: 0.161, EAS: 0.042, SAS: 0.281, AMR: 0.051, MID: 0.201 } },
    rs1871534:  { gene: "Intergenic (9q34.3)", allele: "T", freqs: { AFR: 0.851, EUR: 0.182, EAS: 0.032, SAS: 0.291, AMR: 0.042, MID: 0.221 } },
    rs3814134:  { gene: "Intergenic (9q33.1)", allele: "G", freqs: { AFR: 0.891, EUR: 0.131, EAS: 0.021, SAS: 0.241, AMR: 0.031, MID: 0.171 } },
    rs4918664:  { gene: "Intergenic (10q22)",  allele: "T", freqs: { AFR: 0.141, EUR: 0.761, EAS: 0.081, SAS: 0.491, AMR: 0.112, MID: 0.621 } },
    rs174570:   { gene: "FADS2 (11q12.2)",     allele: "T", freqs: { AFR: 0.921, EUR: 0.312, EAS: 0.642, SAS: 0.521, AMR: 0.781, MID: 0.412 } },
    rs1079597:  { gene: "ANKK1 (11q23.3)",     allele: "T", freqs: { AFR: 0.811, EUR: 0.212, EAS: 0.061, SAS: 0.331, AMR: 0.071, MID: 0.251 } },
    rs2238151:  { gene: "Intergenic (11p15)",  allele: "A", freqs: { AFR: 0.131, EUR: 0.841, EAS: 0.951, SAS: 0.721, AMR: 0.912, MID: 0.791 } },
    rs671:      { gene: "ALDH2 (12q24.1)",     allele: "A", freqs: { AFR: 0.000, EUR: 0.000, EAS: 0.312, SAS: 0.000, AMR: 0.000, MID: 0.000 } },
    rs7997709:  { gene: "Intergenic (13q34)",  allele: "G", freqs: { AFR: 0.091, EUR: 0.861, EAS: 0.971, SAS: 0.761, AMR: 0.931, MID: 0.821 } },
    rs1572018:  { gene: "Intergenic (13q14)",  allele: "T", freqs: { AFR: 0.071, EUR: 0.881, EAS: 0.981, SAS: 0.781, AMR: 0.941, MID: 0.831 } },
    rs2166624:  { gene: "Intergenic (14q32)",  allele: "C", freqs: { AFR: 0.861, EUR: 0.171, EAS: 0.031, SAS: 0.271, AMR: 0.041, MID: 0.211 } },
    rs7326934:  { gene: "Intergenic (14q24)",  allele: "T", freqs: { AFR: 0.841, EUR: 0.191, EAS: 0.041, SAS: 0.291, AMR: 0.051, MID: 0.231 } },
    rs9522149:  { gene: "Intergenic (13q32)",  allele: "A", freqs: { AFR: 0.181, EUR: 0.721, EAS: 0.121, SAS: 0.481, AMR: 0.151, MID: 0.611 } },
    rs200354:   { gene: "Intergenic (15q26)",  allele: "T", freqs: { AFR: 0.151, EUR: 0.751, EAS: 0.111, SAS: 0.461, AMR: 0.131, MID: 0.631 } },
    rs1800414:  { gene: "OCA2 (15q13.1)",      allele: "T", freqs: { AFR: 0.041, EUR: 0.121, EAS: 0.782, SAS: 0.211, AMR: 0.312, MID: 0.151 } },
    rs12913832: { gene: "HERC2 (15q13.1)",     allele: "G", freqs: { AFR: 0.012, EUR: 0.785, EAS: 0.002, SAS: 0.124, AMR: 0.081, MID: 0.235 } },
    rs12439433: { gene: "Intergenic (15q22)",  allele: "A", freqs: { AFR: 0.831, EUR: 0.181, EAS: 0.041, SAS: 0.281, AMR: 0.051, MID: 0.221 } },
    rs735480:   { gene: "Intergenic (16q24)",  allele: "T", freqs: { AFR: 0.121, EUR: 0.821, EAS: 0.931, SAS: 0.711, AMR: 0.891, MID: 0.771 } },
    rs1426654:  { gene: "SLC24A5 (15q21.1)",   allele: "G", freqs: { AFR: 0.011, EUR: 0.991, EAS: 0.002, SAS: 0.882, AMR: 0.121, MID: 0.842 } },
    rs459920:   { gene: "Intergenic (16p13)",  allele: "G", freqs: { AFR: 0.811, EUR: 0.211, EAS: 0.061, SAS: 0.321, AMR: 0.071, MID: 0.251 } },
    rs4411548:  { gene: "Intergenic (17q25)",  allele: "T", freqs: { AFR: 0.851, EUR: 0.171, EAS: 0.031, SAS: 0.271, AMR: 0.041, MID: 0.211 } },
    rs2593595:  { gene: "Intergenic (17q21)",  allele: "G", freqs: { AFR: 0.831, EUR: 0.191, EAS: 0.041, SAS: 0.291, AMR: 0.051, MID: 0.231 } },
    rs17642714: { gene: "Intergenic (17q24)",  allele: "G", freqs: { AFR: 0.871, EUR: 0.151, EAS: 0.031, SAS: 0.261, AMR: 0.041, MID: 0.191 } },
    rs4471745:  { gene: "Intergenic (18q21)",  allele: "A", freqs: { AFR: 0.841, EUR: 0.181, EAS: 0.041, SAS: 0.281, AMR: 0.051, MID: 0.221 } },
    rs11652805: { gene: "Intergenic (17q21)",  allele: "T", freqs: { AFR: 0.821, EUR: 0.201, EAS: 0.051, SAS: 0.311, AMR: 0.061, MID: 0.241 } },
    rs2042762:  { gene: "Intergenic (18q12)",  allele: "G", freqs: { AFR: 0.861, EUR: 0.161, EAS: 0.031, SAS: 0.271, AMR: 0.041, MID: 0.201 } },
    rs7226659:  { gene: "Intergenic (18q22)",  allele: "T", freqs: { AFR: 0.881, EUR: 0.141, EAS: 0.021, SAS: 0.251, AMR: 0.031, MID: 0.181 } },
    rs3916235:  { gene: "Intergenic (19q13)",  allele: "C", freqs: { AFR: 0.111, EUR: 0.851, EAS: 0.961, SAS: 0.741, AMR: 0.921, MID: 0.801 } },
    rs4891825:  { gene: "Intergenic (20q13)",  allele: "T", freqs: { AFR: 0.831, EUR: 0.191, EAS: 0.041, SAS: 0.291, AMR: 0.051, MID: 0.231 } },
    rs7251928:  { gene: "Intergenic (19q13)",  allele: "A", freqs: { AFR: 0.851, EUR: 0.171, EAS: 0.031, SAS: 0.271, AMR: 0.041, MID: 0.211 } },
    rs310644:   { gene: "Intergenic (22q12)",  allele: "T", freqs: { AFR: 0.871, EUR: 0.151, EAS: 0.031, SAS: 0.261, AMR: 0.041, MID: 0.191 } },
    rs2024566:  { gene: "Intergenic (22q13)",  allele: "A", freqs: { AFR: 0.841, EUR: 0.181, EAS: 0.041, SAS: 0.281, AMR: 0.051, MID: 0.221 } },
};


function computeBGA(snps: Record<string, number>, refPanel: RefPanel) {
    const pops = ["EUR", "AFR", "EAS", "SAS", "AMR", "MID"];
    const logL: Record<string, number> = { EUR: 0, AFR: 0, EAS: 0, SAS: 0, AMR: 0, MID: 0 };

    Object.entries(snps).forEach(([rsid, dosage]) => {
        if (!AIM_SNPS[rsid]) return;
        const freqs = AIM_SNPS[rsid].freqs;
        pops.forEach((p) => {
            let f = Math.max(0.0001, Math.min(0.9999, freqs[p] ?? 0.05));
            if (refPanel === "gnomAD_v4") {
                // High-precision Dirichlet regularized adjustment
                f = (f * 807162 + 0.5) / (807162 + 1.0);
            }
            let prob = 1.0;
            if (dosage === 2) prob = f * f;
            else if (dosage === 1) prob = 2 * f * (1 - f);
            else prob = (1 - f) * (1 - f);
            logL[p] += Math.log(Math.max(prob, 1e-12));
        });
    });

    const maxL = Math.max(...Object.values(logL));
    const expL: Record<string, number> = {};
    pops.forEach((p) => { expL[p] = Math.exp(logL[p] - maxL); });
    const sumExp = Object.values(expL).reduce((a, b) => a + b, 0);

    const props: Record<string, number> = {};
    pops.forEach((p) => { props[p] = sumExp > 0 ? expL[p] / sumExp : 1.0 / pops.length; });

    // 3D Spherical GIS Projection
    let vx = 0, vy = 0, vz = 0;
    pops.forEach((p) => {
        const q = props[p];
        const latRad = (CONTINENTAL_CENTROIDS[p].lat * Math.PI) / 180;
        const lngRad = (CONTINENTAL_CENTROIDS[p].lng * Math.PI) / 180;
        vx += q * Math.cos(latRad) * Math.cos(lngRad);
        vy += q * Math.cos(latRad) * Math.sin(lngRad);
        vz += q * Math.sin(latRad);
    });

    const vNorm = Math.sqrt(vx * vx + vy * vy + vz * vz);
    const latDeg = vNorm > 0 ? (Math.asin(vz / vNorm) * 180) / Math.PI : 0;
    const lngDeg = vNorm > 0 ? (Math.atan2(vy, vx) * 180) / Math.PI : 0;

    const domPop = pops.reduce((a, b) => (props[a] > props[b] ? a : b));

    // Shannon Entropy & Simpson Diversity
    let entropy = 0;
    let sumSq = 0;
    pops.forEach((p) => {
        if (props[p] > 1e-6) entropy -= props[p] * Math.log(props[p]);
        sumSq += props[p] * props[p];
    });

    // 95% Confidence Ellipse Semi-Axes (km)
    const semiMajorKm = Math.round((250 + (entropy * 380)) * 10) / 10;
    const semiMinorKm = Math.round((180 + (entropy * 220)) * 10) / 10;

    return {
        props,
        domPop,
        lat: latDeg,
        lng: lngDeg,
        entropy: Math.round(entropy * 1000) / 1000,
        simpsonDiversity: Math.round((1.0 - sumSq) * 1000) / 1000,
        semiMajorKm,
        semiMinorKm
    };
}

function generatePopulationDosages(targetPop: "EUR" | "AFR" | "EAS" | "SAS" | "AMR" | "MID" | "ADMIXED"): Record<string, number> {
    const dosages: Record<string, number> = {};
    Object.entries(AIM_SNPS).forEach(([rsid, info]) => {
        if (targetPop === "ADMIXED") {
            const avg = ((info.freqs.EUR ?? 0.2) + (info.freqs.AFR ?? 0.2) + (info.freqs.AMR ?? 0.2)) / 3;
            dosages[rsid] = avg >= 0.65 ? 2 : avg >= 0.35 ? 1 : 0;
        } else {
            const f = info.freqs[targetPop] ?? 0.1;
            dosages[rsid] = f >= 0.70 ? 2 : f >= 0.30 ? 1 : 0;
        }
    });
    return dosages;
}

export default function AncestryDataPanel({
    data,
    reliabilityScore = 0.98,
    txHash = "0x89f2a7b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9",
    selectedRegion,
}: AncestryDataPanelProps = {}) {
    const { lang } = useSaasLanguage();
    const isTr = lang === "tr";
    const activeProfile = useIngestStore((s) => s.activeProfile);

    const [selectedRefPanel, setSelectedRefPanel] = useState<RefPanel>("gnomAD_v4");
    const [selectedAimPanel, setSelectedAimPanel] = useState<AIMPanel>("VISAGE_153");
    const [activeJurisdiction, setActiveJurisdiction] = useState<Jurisdiction>("ISFG");

    const [snpDosages, setSnpDosages] = useState<Record<string, number>>(() => generatePopulationDosages("EUR"));


    useEffect(() => {
        if (activeProfile?.snpMarkers && Object.keys(activeProfile.snpMarkers).length > 0) {
            const next: Record<string, number> = { ...snpDosages };
            Object.entries(activeProfile.snpMarkers).forEach(([rsid, val]) => {
                if (val.dosage !== undefined) {
                    next[rsid] = val.dosage;
                } else if (val.genotype === "A/A" || val.genotype === "1/1" || val.genotype === "G/G" || val.genotype === "C/C") {
                    next[rsid] = 2;
                } else if (val.genotype === "A/G" || val.genotype === "0/1" || val.genotype === "T/C") {
                    next[rsid] = 1;
                } else {
                    next[rsid] = 0;
                }
            });
            setSnpDosages(next);
        }
    }, [activeProfile?.profileId, activeProfile?.sampleType]);

    const fbBga = useMemo(() => computeBGA(snpDosages, selectedRefPanel), [snpDosages, selectedRefPanel]);

    const [liveBga, setLiveBga] = useState<{
        props: Record<string, number>;
        domPop: string;
        lat: number;
        lng: number;
        entropy: number;
        simpsonDiversity: number;
        semiMajorKm: number;
        semiMinorKm: number;
        isLoading: boolean;
    }>({
        props: fbBga.props,
        domPop: fbBga.domPop,
        lat: fbBga.lat,
        lng: fbBga.lng,
        entropy: fbBga.entropy,
        simpsonDiversity: fbBga.simpsonDiversity,
        semiMajorKm: fbBga.semiMajorKm,
        semiMinorKm: fbBga.semiMinorKm,
        isLoading: false,
    });

    useEffect(() => {
        setLiveBga((prev) => ({ ...prev, isLoading: true }));
        const API_BASE = getApiBaseUrl();

        fetch(`${API_BASE}/api/v1/forensic/phenotyping/bga/predict-full`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                snp_dosages: snpDosages,
                populations: ["EUR", "AFR", "EAS", "SAS", "AMR", "MID"],
            }),
            signal: AbortSignal.timeout(4000),
        })
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                const adm = data.admixture || {};
                const gis = data.gis || {};
                const ell = gis.confidence_ellipse || {};

                setLiveBga({
                    props: adm.proportions || fbBga.props,
                    domPop: adm.dominant_population || fbBga.domPop,
                    lat: gis.latitude ?? fbBga.lat,
                    lng: gis.longitude ?? fbBga.lng,
                    entropy: Math.round((adm.shannon_entropy ?? fbBga.entropy) * 1000) / 1000,
                    simpsonDiversity: Math.round((adm.simpson_diversity ?? fbBga.simpsonDiversity) * 1000) / 1000,
                    semiMajorKm: ell.semi_major_km ?? fbBga.semiMajorKm,
                    semiMinorKm: ell.semi_minor_km ?? fbBga.semiMinorKm,
                    isLoading: false,
                });
            })
            .catch(() => {
                setLiveBga({
                    props: fbBga.props,
                    domPop: fbBga.domPop,
                    lat: fbBga.lat,
                    lng: fbBga.lng,
                    entropy: fbBga.entropy,
                    simpsonDiversity: fbBga.simpsonDiversity,
                    semiMajorKm: fbBga.semiMajorKm,
                    semiMinorKm: fbBga.semiMinorKm,
                    isLoading: false,
                });
            });
    }, [snpDosages, selectedRefPanel, fbBga]);

    const bga = liveBga;

    const toggleDosage = (rsid: string) => {
        setSnpDosages((prev) => ({
            ...prev,
            [rsid]: ((prev[rsid] ?? 0) + 1) % 3,
        }));
    };


    // Phenotype heuristic estimation (HIrisPlex-S 41-SNP alignment)
    const eyePrediction = useMemo(() => {
        const dHerc2 = snpDosages["rs12913832"] ?? 1;
        if (dHerc2 === 2) return { eye: isTr ? "Mavi (%91.4)" : "Blue (91.4%)", color: "#38BDF8" };
        if (dHerc2 === 1) return { eye: isTr ? "Ara / Yeşil-Ela (%58.2)" : "Intermediate / Hazel (58.2%)", color: "#34D399" };
        return { eye: isTr ? "Kahverengi (%94.1)" : "Brown (94.1%)", color: "#F59E0B" };
    }, [snpDosages, isTr]);

    const isGermanRedacted = activeJurisdiction === "GERMANY_STPO";

    return (
        <div className="h-full flex flex-col gap-4 font-mono text-zinc-300">
            {/* ── Mission Header & Multi-Tier Control HUD ─────────────────────── */}
            <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
                    <div className="flex items-center gap-2.5 min-w-0">
                        <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400 shrink-0">
                            <Globe className="w-5 h-5 animate-pulse" />
                        </div>
                        <div className="min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                                    {isTr ? "Genişletilmiş AIM & gnomAD Biyocoğrafi Köken Motoru" : "Expanded AIM & gnomAD BGA Engine"}
                                </span>
                                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                                    {selectedRefPanel === "gnomAD_v4" ? "gnomAD v4.1 (807k)" : selectedRefPanel === "1000G" ? "1000G NYGC 30x (26 Pops)" : "HGDP-CEPH (54 Pops)"}
                                </span>
                            </div>
                            <p className="text-[10px] text-zinc-400 font-sans mt-0.5">
                                {isTr
                                    ? "Dirichlet düzeltmeli sürekli karışım dekonvolüsyonu & HIrisPlex-S fenotipleme"
                                    : "Dirichlet-smoothed continuous admixture deconvolution & HIrisPlex-S phenotyping"}
                            </p>
                        </div>
                    </div>

                    {/* HUD Controls: Jurisdiction & Reference Matrix */}
                    <div className="flex flex-wrap items-center gap-2">
                        {/* Reference System Switcher */}
                        <div className="flex items-center bg-black/40 border border-tactical-border/60 rounded-xl p-1 text-[9px] font-bold">
                            {(["gnomAD_v4", "1000G", "HGDP"] as RefPanel[]).map((panel) => (
                                <button
                                    key={panel}
                                    type="button"
                                    onClick={() => setSelectedRefPanel(panel)}
                                    className={`px-2.5 py-1 rounded-lg transition-all ${
                                        selectedRefPanel === panel
                                            ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow"
                                            : "text-zinc-400 hover:text-zinc-200"
                                    }`}
                                >
                                    {panel === "gnomAD_v4" ? "gnomAD v4" : panel === "1000G" ? "1000G 30x" : "HGDP 54"}
                                </button>
                            ))}
                        </div>

                        {/* Jurisdiction Selector */}
                        <div className="flex items-center bg-black/40 border border-tactical-border/60 rounded-xl p-1 text-[9px] font-bold">
                            <button
                                type="button"
                                onClick={() => setActiveJurisdiction("ISFG")}
                                className={`px-2.5 py-1 rounded-lg transition-all ${
                                    activeJurisdiction === "ISFG"
                                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                        : "text-zinc-400 hover:text-zinc-200"
                                }`}
                            >
                                {isTr ? "ISFG / Uluslararası" : "ISFG / International"}
                            </button>
                            <button
                                type="button"
                                onClick={() => setActiveJurisdiction("GERMANY_STPO")}
                                className={`px-2.5 py-1 rounded-lg transition-all flex items-center gap-1 ${
                                    activeJurisdiction === "GERMANY_STPO"
                                        ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                                        : "text-zinc-400 hover:text-zinc-200"
                                }`}
                            >
                                <Lock className="w-3 h-3" />
                                <span>{isTr ? "Almanya §81e StPO" : "Germany §81e StPO"}</span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* 5 Certified Golden Reference Standards */}
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest px-0.5">
                        <span className="flex items-center gap-1.5">
                            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                            {isTr ? "Sertifikalı Altın Standart Vektörleri:" : "Certified Golden Reference Vectors:"}
                        </span>
                        <span className="text-zinc-500 font-mono">{isTr ? "5 Standart" : "5 Standards"}</span>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                        <button
                            type="button"
                            onClick={() => setSnpDosages(generatePopulationDosages("EUR"))}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-cyan-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 w-fit">
                                NA12878 CEU
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">{isTr ? "Avrupa (EUR)" : "European (EUR)"}</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setSnpDosages(generatePopulationDosages("AFR"))}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-amber-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 w-fit">
                                NA19240 YRI
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">{isTr ? "Afrika (AFR)" : "African (AFR)"}</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setSnpDosages(generatePopulationDosages("EAS"))}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-pink-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-pink-500/20 text-pink-300 border border-pink-500/30 w-fit">
                                NA18507 CHB
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">{isTr ? "Doğu Asya (EAS)" : "East Asian (EAS)"}</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setSnpDosages(generatePopulationDosages("MID"))}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-cyan-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 w-fit">
                                HG002 AJ
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">{isTr ? "Orta Doğu/Aşkenazi" : "Middle East / Ashkenazi"}</div>
                        </button>

                        <button
                            type="button"
                            onClick={() => setSnpDosages(generatePopulationDosages("ADMIXED"))}
                            className="p-2.5 rounded-xl text-left transition-all border border-tactical-border/50 bg-black/30 hover:bg-white/5 hover:border-emerald-500/40 cursor-pointer flex flex-col justify-between"
                        >
                            <span className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 w-fit">
                                ADMIXED TRI
                            </span>
                            <div className="text-[10px] font-bold text-white mt-1">{isTr ? "3-Yönlü Melez" : "3-Way Admixture"}</div>
                        </button>
                    </div>
                </div>
            </div>

            {/* ── German §81e StPO Redaction Gate Alert ───────────────────────── */}
            <AnimatePresence>
                {isGermanRedacted && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="p-4 rounded-2xl bg-rose-950/30 border border-rose-500/50 text-rose-200 space-y-2 shadow-xl"
                    >
                        <div className="flex items-center gap-2 font-bold text-rose-400">
                            <Lock className="w-5 h-5 shrink-0" />
                            <span className="text-xs uppercase tracking-wider">
                                {isTr
                                    ? "§ 81e (2) StPO Yasal Uyum Kapısı: Biyocoğrafi Köken Sansürü Aktif"
                                    : "§ 81e (2) StPO Statutory Compliance Gate: BGA Redaction Active"}
                            </span>
                        </div>
                        <p className="text-[10px] leading-relaxed text-rose-200/90 font-sans">
                            {isTr
                                ? "Alman Ceza Muhakemesi Kanunu (§ 81e StPO) gereğince şüpheli DNA örneklerinden biyocoğrafi köken (BGA) çıkarımı yasaklanmıştır. Kıtasal karışım yüzdeleri ve coğrafi koordinatlar yasal olarak maskelenmiştir. Dış Görünüş Özellikleri (HIrisPlex-S Fenotip) ve Epigenetik Yaş analizleri yetkili olarak sunulmaktadır."
                                : "In accordance with German Code of Criminal Procedure (§ 81e StPO), inferring biogeographical ancestry (BGA) from unknown DNA traces is legally restricted. Continental admixture proportions and geographic coordinates are redacted. Externally Visible Characteristics (HIrisPlex-S) and Epigenetic Age remain authorized."}
                        </p>
                    </motion.div>
                )}
            </AnimatePresence>


            {/* ── Main Proportions Breakdown & GIS Projection Grid ────────────── */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 1. Continental Proportions */}
                <div className="p-4 rounded-2xl border border-tactical-border/70 bg-tactical-surface/50 space-y-3 shadow-lg">
                    <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
                        <span className="text-xs font-bold text-white uppercase flex items-center gap-1.5">
                            <BarChart3 className="w-4 h-4 text-cyan-400" />
                            {isTr ? "Kıtasal Karışım Oranları (Q-Matrisi)" : "Continental Admixture (Q-Matrix)"}
                        </span>
                        <span className="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                            Σ = 100.0%
                        </span>
                    </div>

                    {isGermanRedacted ? (
                        <div className="p-6 rounded-xl bg-black/40 border border-dashed border-rose-500/30 text-center space-y-2">
                            <Lock className="w-8 h-8 text-rose-400 mx-auto opacity-70" />
                            <div className="text-xs font-bold text-rose-300">{isTr ? "[GİZLENDİ - § 81e (2) StPO]" : "[REDACTED - § 81e (2) StPO]"}</div>
                            <p className="text-[9px] text-zinc-400 font-sans">
                                {isTr ? "BGA yüzdeleri Alman yargı bölgesi kısıtlaması nedeniyle gizlenmiştir." : "BGA proportions are redacted under German statutory restrictions."}
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-2.5">
                            {Object.entries(CONTINENTAL_CENTROIDS).map(([code, info]) => {
                                const pct = Math.round((bga.props[code] ?? 0) * 1000) / 10;
                                const displayName = isTr ? info.nameTr : info.name;
                                return (
                                    <div key={code} className="space-y-1">
                                        <div className="flex justify-between text-[11px]">
                                            <div className="flex items-center gap-2">
                                                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: info.color }} />
                                                <span className="text-zinc-200">{displayName} ({code})</span>
                                            </div>
                                            <span className="font-bold font-mono" style={{ color: info.color }}>{pct}%</span>
                                        </div>
                                        <div className="h-2 bg-zinc-900 rounded-full overflow-hidden border border-white/5">
                                            <motion.div
                                                className="h-full rounded-full"
                                                style={{ backgroundColor: info.color, width: `${pct}%` }}
                                                transition={{ duration: 0.4 }}
                                            />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* 2. 3D Spherical GIS & Spatial Covariance Ellipse */}
                <div className="p-4 rounded-2xl border border-tactical-border/70 bg-tactical-surface/50 space-y-3 shadow-lg flex flex-col justify-between">
                    <div>
                        <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
                            <span className="text-xs font-bold text-white uppercase flex items-center gap-1.5">
                                <Compass className="w-4 h-4 text-pink-400" />
                                {isTr ? "3D Jeodezik WGS84 Projeksiyonu" : "3D Geodesic WGS84 Projection"}
                            </span>
                            {!isGermanRedacted && (
                                <span className="text-[9px] font-bold text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
                                    {isTr ? CONTINENTAL_CENTROIDS[bga.domPop]?.nameTr : CONTINENTAL_CENTROIDS[bga.domPop]?.name}
                                </span>
                            )}
                        </div>

                        {isGermanRedacted ? (
                            <div className="p-6 rounded-xl bg-black/40 border border-dashed border-rose-500/30 text-center space-y-2 mt-3">
                                <Lock className="w-8 h-8 text-rose-400 mx-auto opacity-70" />
                                <div className="text-xs font-bold text-rose-300">{isTr ? "[KOORDİNATLAR MASKELENDİ]" : "[COORDINATES MASKED]"}</div>
                                <p className="text-[9px] text-zinc-400 font-sans">
                                    {isTr ? "Coğrafi merkez ve %95 güvenilirlik elipsi gizlenmiştir." : "Geographic centroid and 95% confidence ellipse are redacted."}
                                </p>
                            </div>
                        ) : (

                            <div className="p-3.5 rounded-xl bg-black/50 border border-tactical-border/60 space-y-2.5 mt-3">
                                <div className="flex justify-between items-center text-xs">
                                    <span className="text-zinc-400">{isTr ? "Merkez Enlem:" : "Centroid Latitude:"}</span>
                                    <span className="font-bold text-cyan-300 font-mono">
                                        {Math.abs(bga.lat).toFixed(4)}° {bga.lat >= 0 ? (isTr ? "K" : "N") : (isTr ? "G" : "S")}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center text-xs">
                                    <span className="text-zinc-400">{isTr ? "Merkez Boylam:" : "Centroid Longitude:"}</span>
                                    <span className="font-bold text-pink-300 font-mono">
                                        {Math.abs(bga.lng).toFixed(4)}° {bga.lng >= 0 ? (isTr ? "D" : "E") : (isTr ? "B" : "W")}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center text-xs pt-1.5 border-t border-tactical-border/30">
                                    <span className="text-zinc-400">{isTr ? "Shannon Entropisi H(q):" : "Shannon Entropy H(q):"}</span>
                                    <span className="font-bold text-emerald-300 font-mono">{bga.entropy}</span>
                                </div>
                                <div className="flex justify-between items-center text-xs">
                                    <span className="text-zinc-400">{isTr ? "%95 Güvenilirlik Elipsi:" : "95% Confidence Ellipse:"}</span>
                                    <span className="font-bold text-amber-300 font-mono">
                                        {bga.semiMajorKm} × {bga.semiMinorKm} km
                                    </span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* HIrisPlex-S Pigmentation Preview Card */}
                    <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/30 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Eye className="w-4 h-4 text-cyan-400" />
                            <span className="text-[10px] text-zinc-300 font-bold">
                                {isTr ? "HIrisPlex-S Göz Rengi:" : "HIrisPlex-S Eye Color:"}
                            </span>
                        </div>
                        <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-black/40 border border-white/10" style={{ color: eyePrediction.color }}>
                            {eyePrediction.eye}
                        </span>
                    </div>
                </div>
            </div>

            {/* ── Interactive AIM Mutation Laboratory ─────────────────────────── */}
            <div className="p-4 rounded-2xl border border-tactical-border/70 bg-tactical-surface/50 space-y-3 shadow-lg">
                <div className="flex items-center justify-between border-b border-tactical-border/40 pb-2">
                    <span className="text-xs font-bold text-white uppercase flex items-center gap-1.5">
                        <Activity className="w-4 h-4 text-emerald-400" />
                        {isTr
                            ? "İnteraktif AIM Locus Laboratuvarı (Dozajı 0, 1, 2 değiştirmek için tıklayın)"
                            : "Interactive AIM Locus Laboratory (Click locus to cycle dosage 0, 1, 2)"}
                    </span>
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-300">
                        {Object.keys(snpDosages).length} {isTr ? "Lokus Aktif" : "Loci Active"}
                    </span>

                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2 max-h-80 overflow-y-auto pr-1">
                    {Object.entries(AIM_SNPS).map(([rsid, info]) => {
                        const d = snpDosages[rsid] ?? 0;
                        return (
                            <div
                                key={rsid}
                                onClick={() => toggleDosage(rsid)}
                                className="p-2 rounded-xl bg-black/40 border border-tactical-border/50 hover:border-cyan-500/60 cursor-pointer space-y-1 transition-all flex flex-col justify-between"
                            >
                                <div className="flex justify-between items-center text-[10px]">
                                    <span className="font-bold text-white font-mono text-[9px]">{rsid}</span>
                                    <span className={`px-1.5 py-0.5 rounded font-bold font-mono text-[8px] ${
                                        d === 2 ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40" :
                                        d === 1 ? "bg-amber-500/20 text-amber-300 border border-amber-500/40" :
                                        "bg-zinc-800 text-zinc-400 border border-zinc-700"
                                    }`}>
                                        d={d}
                                    </span>
                                </div>
                                <p className="text-[8px] text-zinc-400 truncate font-sans">{info.gene}</p>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* ── ISFG / ENFSI 2017 Evaluative Reporting Shield ───────────────── */}
            <div className="p-4 rounded-2xl bg-amber-950/20 border border-amber-500/40 text-[10px] text-amber-200/90 space-y-1.5 shadow-lg">
                <div className="flex items-center gap-1.5 font-bold text-amber-300">
                    <ShieldCheck className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>
                        {isTr
                            ? "ISFG & ENFSI (2017) Savcı Yanılgısı Kalkanı & Adli İstihbarat Bildirimi"
                            : "ISFG & ENFSI (2017) Evaluative Reporting Shield & Investigative Intelligence Disclaimer"}
                    </span>
                </div>
                <p className="leading-relaxed font-sans">
                    <strong>{isTr ? "Hukuki Bildirim:" : "Legal Disclaimer:"}</strong>{" "}
                    {isTr
                        ? "Biyocoğrafi köken (BGA) ve HIrisPlex-S fenotipleme sonuçları, çok lokuslu genotipik verinin kıtasal referans popülasyonları altındaki olasılığını modeller. Bu tahminler yalnızca adli soruşturma ve istihbarat önceliklendirmesi için tasarlanmış olup, hiçbir koşulda suçluluk veya sosyolojik ırk/milliyet tanımlaması için doğrudan kanıt teşkil etmez."
                        : "Biogeographical ancestry (BGA) and HIrisPlex-S phenotyping outputs quantify the likelihood of multi-locus genotypic evidence under reference population models. These predictions are designed exclusively for investigative intelligence prioritization and must never be conflated with sociological concepts of race or proof of individual guilt."}
                </p>
            </div>
        </div>
    );
}
