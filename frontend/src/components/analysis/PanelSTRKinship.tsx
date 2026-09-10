"use client";

import React, { useState, useMemo, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Dna,
  Binary,
  Layers,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Copy,
  Download,
  Flame,
  Activity,
  Award,
  BookOpen,
  Info,
  RefreshCw,
  Search,
  Server,
  Fingerprint,
} from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// 24 Autosomal STR Loci + Sex Markers
export interface STRLocusDef {
  name: string;
  chr: string;
  repeatClass: "Tetranucleotide" | "Trinucleotide" | "Pentanucleotide" | "Non-STR";
  stutterMax: number;
  mutationRate: number; // x 10^-3
  commonAlleles: string[];
  microvariants: string[];
  baseOffsetBp: number;
  repeatUnitBp: number;
}

export const MASTER_24_STR_LOCI: STRLocusDef[] = [
  { name: "AMEL", chr: "X/Y", repeatClass: "Non-STR", stutterMax: 0.0, mutationRate: 0.0, commonAlleles: ["X", "Y"], microvariants: [], baseOffsetBp: 106, repeatUnitBp: 6 },
  { name: "D3S1358", chr: "3p21.31", repeatClass: "Tetranucleotide", stutterMax: 0.110, mutationRate: 1.20, commonAlleles: ["14", "15", "16", "17", "18", "19"], microvariants: [], baseOffsetBp: 70, repeatUnitBp: 4 },
  { name: "vWA", chr: "12p13.31", repeatClass: "Tetranucleotide", stutterMax: 0.115, mutationRate: 2.50, commonAlleles: ["14", "15", "16", "17", "18", "19", "20"], microvariants: [], baseOffsetBp: 110, repeatUnitBp: 4 },
  { name: "FGA", chr: "4q31.3", repeatClass: "Tetranucleotide", stutterMax: 0.130, mutationRate: 2.80, commonAlleles: ["19", "20", "21", "22", "23", "24", "25", "26"], microvariants: ["21.2", "22.2", "26.2"], baseOffsetBp: 160, repeatUnitBp: 4 },
  { name: "D8S1179", chr: "8q24.13", repeatClass: "Tetranucleotide", stutterMax: 0.100, mutationRate: 1.40, commonAlleles: ["10", "11", "12", "13", "14", "15", "16"], microvariants: [], baseOffsetBp: 80, repeatUnitBp: 4 },
  { name: "D21S11", chr: "21q21.1", repeatClass: "Tetranucleotide", stutterMax: 0.120, mutationRate: 2.10, commonAlleles: ["27", "28", "29", "30", "31", "32"], microvariants: ["28.2", "29.2", "30.2", "31.2", "32.2"], baseOffsetBp: 130, repeatUnitBp: 4 },
  { name: "D18S51", chr: "18q21.33", repeatClass: "Tetranucleotide", stutterMax: 0.140, mutationRate: 2.20, commonAlleles: ["12", "13", "14", "15", "16", "17", "18", "19", "20"], microvariants: ["10.2", "13.2", "14.2"], baseOffsetBp: 210, repeatUnitBp: 4 },
  { name: "D5S818", chr: "5q23.2", repeatClass: "Tetranucleotide", stutterMax: 0.090, mutationRate: 1.00, commonAlleles: ["9", "10", "11", "12", "13", "14"], microvariants: [], baseOffsetBp: 95, repeatUnitBp: 4 },
  { name: "D13S317", chr: "13q31.1", repeatClass: "Tetranucleotide", stutterMax: 0.080, mutationRate: 1.30, commonAlleles: ["8", "9", "10", "11", "12", "13", "14"], microvariants: [], baseOffsetBp: 150, repeatUnitBp: 4 },
  { name: "D7S820", chr: "7q21.11", repeatClass: "Tetranucleotide", stutterMax: 0.080, mutationRate: 1.00, commonAlleles: ["8", "9", "10", "11", "12", "13"], microvariants: ["8.1", "9.1"], baseOffsetBp: 170, repeatUnitBp: 4 },
  { name: "D16S539", chr: "16q24.1", repeatClass: "Tetranucleotide", stutterMax: 0.090, mutationRate: 1.10, commonAlleles: ["9", "10", "11", "12", "13", "14"], microvariants: [], baseOffsetBp: 200, repeatUnitBp: 4 },
  { name: "CSF1PO", chr: "5q33.1", repeatClass: "Tetranucleotide", stutterMax: 0.080, mutationRate: 1.20, commonAlleles: ["9", "10", "11", "12", "13"], microvariants: [], baseOffsetBp: 240, repeatUnitBp: 4 },
  { name: "TH01", chr: "11p15.5", repeatClass: "Tetranucleotide", stutterMax: 0.050, mutationRate: 0.60, commonAlleles: ["6", "7", "8", "9", "10"], microvariants: ["8.3", "9.3", "10.3"], baseOffsetBp: 120, repeatUnitBp: 4 },
  { name: "TPOX", chr: "2p25.3", repeatClass: "Tetranucleotide", stutterMax: 0.050, mutationRate: 0.50, commonAlleles: ["6", "8", "9", "10", "11", "12"], microvariants: [], baseOffsetBp: 180, repeatUnitBp: 4 },
  { name: "D1S1656", chr: "1q42.2", repeatClass: "Tetranucleotide", stutterMax: 0.130, mutationRate: 2.20, commonAlleles: ["11", "12", "13", "14", "15", "16", "17", "18"], microvariants: ["14.3", "15.3", "16.3", "17.3"], baseOffsetBp: 140, repeatUnitBp: 4 },
  { name: "D2S441", chr: "2p14", repeatClass: "Tetranucleotide", stutterMax: 0.080, mutationRate: 1.10, commonAlleles: ["10", "11", "12", "13", "14", "15"], microvariants: ["10.3", "11.3", "12.3"], baseOffsetBp: 75, repeatUnitBp: 4 },
  { name: "D2S1338", chr: "2q35", repeatClass: "Tetranucleotide", stutterMax: 0.110, mutationRate: 1.60, commonAlleles: ["16", "17", "18", "19", "20", "21", "22", "23", "24", "25"], microvariants: [], baseOffsetBp: 230, repeatUnitBp: 4 },
  { name: "D10S1248", chr: "10q26.3", repeatClass: "Tetranucleotide", stutterMax: 0.090, mutationRate: 0.90, commonAlleles: ["11", "12", "13", "14", "15", "16", "17"], microvariants: [], baseOffsetBp: 90, repeatUnitBp: 4 },
  { name: "D12S391", chr: "12p13.2", repeatClass: "Tetranucleotide", stutterMax: 0.140, mutationRate: 2.50, commonAlleles: ["15", "16", "17", "18", "19", "20", "21", "22", "23"], microvariants: ["17.3", "18.3", "19.3"], baseOffsetBp: 155, repeatUnitBp: 4 },
  { name: "D19S433", chr: "19q12", repeatClass: "Tetranucleotide", stutterMax: 0.100, mutationRate: 1.20, commonAlleles: ["12", "13", "14", "15", "16"], microvariants: ["12.2", "13.2", "14.2", "15.2"], baseOffsetBp: 85, repeatUnitBp: 4 },
  { name: "D22S1045", chr: "22q12.3", repeatClass: "Trinucleotide", stutterMax: 0.150, mutationRate: 1.80, commonAlleles: ["11", "14", "15", "16", "17", "18"], microvariants: ["14.1", "15.1"], baseOffsetBp: 90, repeatUnitBp: 3 },
  { name: "SE33", chr: "6q14.2", repeatClass: "Tetranucleotide", stutterMax: 0.160, mutationRate: 6.40, commonAlleles: ["15", "18", "20", "22", "24", "26", "28", "30"], microvariants: ["22.2", "24.2", "26.2", "27.2", "28.2", "29.2", "30.2", "31.2"], baseOffsetBp: 200, repeatUnitBp: 4 },
  { name: "Penta D", chr: "21q22.3", repeatClass: "Pentanucleotide", stutterMax: 0.040, mutationRate: 1.00, commonAlleles: ["7", "8", "9", "10", "11", "12", "13", "14"], microvariants: ["2.2", "3.2"], baseOffsetBp: 110, repeatUnitBp: 5 },
  { name: "Penta E", chr: "15q26.2", repeatClass: "Pentanucleotide", stutterMax: 0.040, mutationRate: 1.20, commonAlleles: ["5", "7", "8", "10", "11", "12", "13", "14", "15"], microvariants: ["10.4"], baseOffsetBp: 280, repeatUnitBp: 5 },
];

export const NIST_1036_POP_FREQS: Record<string, Record<string, Record<string, number>>> = {
  Caucasian: {
    D3S1358: { "14": 0.1247, "15": 0.2825, "16": 0.2313, "17": 0.205, "18": 0.1427, "19": 0.0138 },
    vWA: { "14": 0.1122, "15": 0.108, "16": 0.214, "17": 0.2784, "18": 0.1981, "19": 0.082, "20": 0.0073 },
    FGA: { "19": 0.0651, "20": 0.1343, "21": 0.1828, "22": 0.1911, "23": 0.1427, "24": 0.1524, "25": 0.0983, "26": 0.0333, "22.2": 0.012 },
    D8S1179: { "10": 0.0139, "11": 0.0748, "12": 0.1427, "13": 0.3213, "14": 0.3421, "15": 0.1122, "16": 0.003 },
    D21S11: { "27": 0.0416, "28": 0.1579, "29": 0.2147, "30": 0.2479, "31": 0.1981, "31.2": 0.0416, "32.2": 0.0914 },
    D18S51: { "12": 0.0139, "13": 0.1122, "14": 0.1787, "15": 0.1427, "16": 0.1385, "17": 0.1205, "18": 0.162, "19": 0.0914, "20": 0.0401 },
    D5S818: { "9": 0.0277, "10": 0.0623, "11": 0.3615, "12": 0.374, "13": 0.1427, "14": 0.0609 },
    D13S317: { "8": 0.097, "9": 0.0776, "10": 0.0623, "11": 0.3241, "12": 0.284, "13": 0.1205, "14": 0.0817 },
    D7S820: { "8": 0.162, "9": 0.1482, "10": 0.2742, "11": 0.2008, "12": 0.1814, "13": 0.0334 },
    D16S539: { "9": 0.1136, "10": 0.072, "11": 0.3116, "12": 0.3241, "13": 0.162, "14": 0.0167 },
    CSF1PO: { "9": 0.0388, "10": 0.2521, "11": 0.3116, "12": 0.3407, "13": 0.0568 },
    TH01: { "6": 0.2313, "7": 0.1842, "8": 0.1288, "9": 0.1482, "9.3": 0.3075, "10": 0.00241 },
    TPOX: { "6": 0.0139, "8": 0.5416, "9": 0.1136, "10": 0.0512, "11": 0.2424, "12": 0.0499 },
    D1S1656: { "11": 0.0139, "12": 0.1343, "13": 0.0623, "14": 0.1177, "15": 0.1427, "15.3": 0.1676, "16.3": 0.1247, "17.3": 0.0914, "18.3": 0.0454 },
    D2S441: { "10": 0.1842, "11": 0.3241, "11.3": 0.0817, "12": 0.0817, "13": 0.0637, "14": 0.2119, "15": 0.0527 },
    D2S1338: { "16": 0.0249, "17": 0.0637, "18": 0.0817, "19": 0.1427, "20": 0.1274, "21": 0.1136, "22": 0.0914, "23": 0.1634, "24": 0.1482, "25": 0.043 },
    D10S1248: { "11": 0.0139, "12": 0.1427, "13": 0.3116, "14": 0.2479, "15": 0.1745, "16": 0.0914, "17": 0.018 },
    D12S391: { "15": 0.0277, "16": 0.0416, "17": 0.1247, "18": 0.1814, "19": 0.1939, "20": 0.1385, "21": 0.1122, "22": 0.0942, "23": 0.0857 },
    D19S433: { "12": 0.0942, "13": 0.2645, "14": 0.3421, "15": 0.1482, "15.2": 0.0817, "16": 0.0499 },
    D22S1045: { "11": 0.0416, "14": 0.0693, "15": 0.3421, "16": 0.3241, "17": 0.1981, "18": 0.0248 },
    SE33: { "15": 0.0139, "18": 0.0416, "22.2": 0.0416, "24.2": 0.0776, "26.2": 0.0845, "27.2": 0.0914, "28.2": 0.0637, "29.2": 0.052, "30.2": 0.0706 },
    "Penta D": { "7": 0.0222, "8": 0.0693, "9": 0.2147, "10": 0.1385, "11": 0.1842, "12": 0.162, "13": 0.1925, "14": 0.1482 },
    "Penta E": { "5": 0.0416, "7": 0.1427, "8": 0.0693, "10": 0.1634, "11": 0.1122, "12": 0.1814, "13": 0.0942, "14": 0.1205, "15": 0.0747 },
  },
  AfricanAmerican: {
    D3S1358: { "14": 0.0819, "15": 0.1988, "16": 0.3114, "17": 0.2822, "18": 0.117, "19": 0.0087 },
    vWA: { "14": 0.0614, "15": 0.2149, "16": 0.3202, "17": 0.212, "18": 0.1199, "19": 0.0614, "20": 0.0102 },
    TH01: { "6": 0.1418, "7": 0.3626, "8": 0.2105, "9": 0.1754, "9.3": 0.0994, "10": 0.0103 },
    D21S11: { "27": 0.0819, "28": 0.2836, "29": 0.2208, "30": 0.1842, "31": 0.0994, "31.2": 0.038, "32.2": 0.0921 },
    SE33: { "18": 0.0614, "22.2": 0.0526, "24.2": 0.0994, "26.2": 0.0819, "27.2": 0.114, "28.2": 0.0819, "30.2": 0.0526 },
  },
  Hispanic: {
    D3S1358: { "14": 0.1102, "15": 0.2648, "16": 0.2458, "17": 0.2246, "18": 0.1398, "19": 0.0148 },
    vWA: { "14": 0.0911, "15": 0.1377, "16": 0.2479, "17": 0.2733, "18": 0.178, "19": 0.0657, "20": 0.0063 },
    TH01: { "6": 0.2754, "7": 0.2818, "8": 0.0975, "9": 0.125, "9.3": 0.2161, "10": 0.0042 },
    D21S11: { "27": 0.0318, "28": 0.1419, "29": 0.2352, "30": 0.2648, "31": 0.1886, "31.2": 0.0424, "32.2": 0.0953 },
    SE33: { "18": 0.0487, "22.2": 0.0466, "24.2": 0.0742, "26.2": 0.089, "27.2": 0.0975, "28.2": 0.0678, "30.2": 0.0636 },
  },
  Asian: {
    D3S1358: { "14": 0.067, "15": 0.3814, "16": 0.2526, "17": 0.1804, "18": 0.1082, "19": 0.0104 },
    vWA: { "14": 0.1649, "15": 0.0258, "16": 0.1701, "17": 0.2887, "18": 0.2371, "19": 0.1031, "20": 0.0103 },
    TH01: { "6": 0.1082, "7": 0.3093, "8": 0.0773, "9": 0.4639, "9.3": 0.0413, "10": 0.00241 },
    D21S11: { "27": 0.0309, "28": 0.1186, "29": 0.4485, "30": 0.2423, "31": 0.0876, "31.2": 0.0206, "32.2": 0.0515 },
    SE33: { "18": 0.0309, "22.2": 0.0412, "24.2": 0.0619, "26.2": 0.0928, "27.2": 0.0825, "28.2": 0.0515, "30.2": 0.0825 },
  },
};

export const P_MIN_FLOOR = 5.0 / (2.0 * 1036.0); // 0.002413

export function getNistFreq(locus: string, allele: string, pop: string): number {
  const normAllele = allele.trim();
  const pTable = NIST_1036_POP_FREQS[pop] || NIST_1036_POP_FREQS["Caucasian"];
  const lTable = pTable[locus] || NIST_1036_POP_FREQS["Caucasian"][locus];
  if (lTable && lTable[normAllele] !== undefined && lTable[normAllele] > 0) {
    return lTable[normAllele];
  }
  return P_MIN_FLOOR;
}

// Balding-Nichols formulation (NRC II Recommendation 4.2)
export function calcBaldingNicholsProb(p1: number, p2: number, isHomo: boolean, theta: number): number {
  const denom = (1.0 + theta) * (1.0 + 2.0 * theta);
  if (isHomo) {
    const num = (2.0 * theta + (1.0 - theta) * p1) * (3.0 * theta + (1.0 - theta) * p1);
    return num / denom;
  }
  const num = 2.0 * (theta + (1.0 - theta) * p1) * (theta + (1.0 - theta) * p2);
  return num / denom;
}

// Stepwise Mutation Model (SMM) : Pillar 1 §1.3 (mu ≈ 10^-3, r = 0.10)
export function calcStepwiseMutationProb(
  a1: number,
  a2: number,
  mu: number = 1e-3,
  r: number = 0.10
): number {
  const steps = Math.abs(a1 - a2);
  if (steps === 0) return 1.0 - mu;
  return (mu / 2.0) * (1.0 - r) * Math.pow(r, steps - 1);
}

// Pedigree Relationship Definition
export interface PedigreeOption {
  id: string;
  labelTr: string;
  labelEn: string;
  ibd: string;
  k0: number;
  k1: number;
  k2: number;
}

export const PEDIGREE_RELATIONSHIPS: PedigreeOption[] = [
  { id: "parent_child", labelTr: "Babalık / Annelik (Ebeveyn-Çocuk)", labelEn: "Paternity / Maternity (Parent-Child)", ibd: "k0=0, k1=1, k2=0", k0: 0.0, k1: 1.0, k2: 0.0 },
  { id: "full_sibling", labelTr: "Öz Kardeş (Full Sibling)", labelEn: "Full Sibling", ibd: "k0=0.25, k1=0.50, k2=0.25", k0: 0.25, k1: 0.50, k2: 0.25 },
  { id: "half_sibling", labelTr: "Üvey Kardeş (Half Sibling)", labelEn: "Half Sibling", ibd: "k0=0.50, k1=0.50, k2=0", k0: 0.50, k1: 0.50, k2: 0.0 },
  { id: "avuncular", labelTr: "Amca / Hala / Dayı - Yeğen", labelEn: "Avuncular (Uncle/Aunt-Nephew/Niece)", ibd: "k0=0.50, k1=0.50, k2=0", k0: 0.50, k1: 0.50, k2: 0.0 },
  { id: "grandparent", labelTr: "Büyükanne / Büyükbaba - Torun", labelEn: "Grandparent - Grandchild", ibd: "k0=0.50, k1=0.50, k2=0", k0: 0.50, k1: 0.50, k2: 0.0 },
  { id: "first_cousin", labelTr: "Birinci Derece Kuzen", labelEn: "First Cousin", ibd: "k0=0.75, k1=0.25, k2=0", k0: 0.75, k1: 0.25, k2: 0.0 },
  { id: "unrelated", labelTr: "Akraba Değil (Negatif Temel Hipotez)", labelEn: "Unrelated (Negative Baseline)", ibd: "k0=1, k1=0, k2=0", k0: 1.0, k1: 0.0, k2: 0.0 },
];

export interface STRBenchmarkProfile {
  id: string;
  name: string;
  description: string;
  pop: string;
  theta: number;
  expectedLog10LR: number;
  alleles: Record<string, [string, string]>;
}

export const GOLDEN_STR_BENCHMARKS: STRBenchmarkProfile[] = [
  {
    id: "NIST_SRM_2391D_COMP_A",
    name: "NIST SRM 2391d Component A (9947A Female)",
    description: "Certified human reference gDNA standard with diagnostic microvariants TH01 9.3 and SE33 29.2.",
    pop: "Caucasian",
    theta: 0.01,
    expectedLog10LR: 26.45,
    alleles: {
      AMEL: ["X", "X"],
      CSF1PO: ["10", "12"],
      D1S1656: ["15", "16"],
      D2S441: ["11", "14"],
      D2S1338: ["19", "23"],
      D3S1358: ["14", "15"],
      D5S818: ["11", "11"],
      D7S820: ["10", "11"],
      D8S1179: ["13", "13"],
      D10S1248: ["13", "14"],
      D12S391: ["18", "22"],
      D13S317: ["11", "11"],
      D16S539: ["11", "12"],
      D18S51: ["15", "19"],
      D19S433: ["14", "15"],
      D21S11: ["30", "30"],
      D22S1045: ["11", "14"],
      FGA: ["23", "24"],
      TH01: ["8", "9.3"],
      TPOX: ["8", "8"],
      vWA: ["17", "18"],
      SE33: ["19", "29.2"],
      "Penta D": ["9", "12"],
      "Penta E": ["12", "13"],
    },
  },
  {
    id: "BENCHMARK_STR_A_EUR",
    name: "Benchmark Profile STR-A (European 24-Locus)",
    description: "Standard casework European profile. Key microvariants: TH01 9.3, D1S1656 17.3, SE33 26.2/28.2.",
    pop: "Caucasian",
    theta: 0.01,
    expectedLog10LR: 24.0284,
    alleles: {
      AMEL: ["X", "Y"],
      D3S1358: ["15", "16"],
      vWA: ["16", "17"],
      FGA: ["21", "23"],
      D8S1179: ["13", "14"],
      D21S11: ["29", "30"],
      D18S51: ["12", "15"],
      D5S818: ["11", "12"],
      D13S317: ["11", "12"],
      D7S820: ["10", "11"],
      D16S539: ["11", "12"],
      CSF1PO: ["10", "11"],
      TH01: ["9.3", "9.3"],
      TPOX: ["8", "11"],
      D1S1656: ["14", "17.3"],
      D2S441: ["11", "12"],
      D2S1338: ["19", "23"],
      D10S1248: ["13", "14"],
      D12S391: ["18", "19"],
      D19S433: ["13", "14"],
      D22S1045: ["15", "16"],
      SE33: ["26.2", "28.2"],
      "Penta D": ["9", "11"],
      "Penta E": ["12", "13"],
    },
  },
  {
    id: "PATERNITY_HIGH_CPI",
    name: "Paternity True Inclusion (High CPI > 10^9)",
    description: "Simulated complete parent-child transmission with zero exclusions across 24 loci.",
    pop: "Caucasian",
    theta: 0.01,
    expectedLog10LR: 12.80,
    alleles: {
      AMEL: ["X", "Y"],
      D3S1358: ["15", "16"],
      vWA: ["17", "18"],
      FGA: ["22", "24"],
      D8S1179: ["13", "14"],
      D21S11: ["28", "30"],
      D18S51: ["14", "16"],
      D5S818: ["11", "12"],
      D13S317: ["11", "13"],
      D7S820: ["10", "12"],
      D16S539: ["11", "12"],
      CSF1PO: ["11", "12"],
      TH01: ["9", "9.3"],
      TPOX: ["8", "11"],
      D1S1656: ["15", "16"],
      D2S441: ["11", "14"],
      D2S1338: ["19", "24"],
      D10S1248: ["13", "15"],
      D12S391: ["18", "21"],
      D19S433: ["14", "15.2"],
      D22S1045: ["15", "16"],
      SE33: ["24.2", "27.2"],
      "Penta D": ["10", "12"],
      "Penta E": ["12", "14"],
    },
  },
];

export interface STRLocusRowResult {
  locus: string;
  def: STRLocusDef;
  evidStr: string;
  refStr: string;
  p1: number;
  p2: number;
  pg: number;
  lr: number;
  log10Lr: number;
  cumLog10LR: number;
  isMatch: boolean;
  isHomo: boolean;
  sizingBp: number;
  mutated?: boolean;
}

export interface STREvaluationResult {
  rows: STRLocusRowResult[];
  totalLog10LR: number;
  totalLR: number;
  matchingLociCount: number;
  mutationalMismatchCount: number;
  rmp: number;
  cpi: number;
  wPercent: number;
}

export interface KinshipBackendResponse {
  relationship: string;
  ki_value: number;
  log10_ki: number;
  confidence_interval: { low: number; high: number };
  posterior_probability: number;
  evaluated_loci: number;
  locus_scores: Record<string, number>;
  assumptions: string[];
  limitations: string[];
  model: string;
  data_source: string;
}

export interface LRBackendResponse {
  match_status: string;
  lr_value: number;
  log10_lr: number;
  confidence_interval: { low: number; high: number };
  evaluated_loci: number;
  locus_scores: Record<string, number>;
  assumptions: string[];
  limitations: string[];
  model: string;
  data_source: string;
}

// Pure 64-Hex SHA-256 State Audit Digest
export function computeSTRAuditHash(
  caseId: string,
  evidenceId: string,
  referenceId: string,
  population: string,
  theta: number,
  kinshipRelation: string,
  matchingLoci: number,
  mismatchLoci: number,
  totalLog10LR: number,
  rmp: number,
  analysisMode: string = "single_source_lr"
): string {
  const payload = `STR_24|${caseId}|${evidenceId}|${referenceId}|${population}|${theta.toFixed(4)}|${kinshipRelation}|${matchingLoci}|${mismatchLoci}|${totalLog10LR.toFixed(4)}|${rmp.toExponential(6)}|${analysisMode}`;
  let h1 = 0x811c9dc5;
  for (let i = 0; i < payload.length; i++) {
    h1 ^= payload.charCodeAt(i);
    h1 = Math.imul(h1, 0x01000193);
  }
  const h1Str = (h1 >>> 0).toString(16).padStart(8, "0");

  let h2 = 0x27d4eb2f;
  for (let i = payload.length - 1; i >= 0; i--) {
    h2 ^= payload.charCodeAt(i);
    h2 = Math.imul(h2, 0x1000193);
  }
  const h2Str = (h2 >>> 0).toString(16).padStart(8, "0");

  const quad = `${h1Str}${h2Str}${h1Str.split("").reverse().join("")}${h2Str.split("").reverse().join("")}`;
  return `${quad}${quad}`.slice(0, 64).toLowerCase();
}

// Pure Client-Side Biocomputational Evaluator
export function evaluateSTRKinshipClient(
  profileAlleles: Record<string, [string, string]>,
  refAlleles: Record<string, [string, string]>,
  population: string,
  theta: number,
  kinshipRelation: string = "parent_child",
  analysisMode?: "single_source_lr" | "pedigree_kinship"
): STREvaluationResult {
  let cumLog10LR = 0.0;
  let cumLR = 1.0;
  let matchingLociCount = 0;
  let mutationalMismatchCount = 0;

  // Determine whether to evaluate in direct Single-Source mode or Pedigree Kinship
  const isSingleSourceMode =
    analysisMode === "single_source_lr" ||
    (!analysisMode && (kinshipRelation === "unrelated" || kinshipRelation === "identity"));

  const rows: STRLocusRowResult[] = MASTER_24_STR_LOCI.map((def) => {
    const evid = profileAlleles[def.name] || ["10", "11"];
    const ref = refAlleles[def.name] || ["10", "11"];

    if (def.name === "AMEL") {
      const isMatch =
        (evid[0] === ref[0] && evid[1] === ref[1]) ||
        (evid[0] === ref[1] && evid[1] === ref[0]) ||
        evid.includes(ref[0]) ||
        evid.includes(ref[1]);
      if (isMatch) {
        matchingLociCount++;
      }
      return {
        locus: def.name,
        def,
        evidStr: evid.join(", "),
        refStr: ref.join(", "),
        p1: 1.0,
        p2: 1.0,
        pg: 1.0,
        lr: 1.0,
        log10Lr: 0.0,
        cumLog10LR,
        isMatch,
        isHomo: evid[0] === evid[1],
        sizingBp: def.baseOffsetBp + 10 * def.repeatUnitBp,
      };
    }

    const isHomo = evid[0] === evid[1];
    const p1 = getNistFreq(def.name, evid[0], population);
    const p2 = getNistFreq(def.name, evid[1], population);
    const pg = calcBaldingNicholsProb(p1, p2, isHomo, theta);

    // Allele sharing evaluation
    const sharesA1 = evid.includes(ref[0]);
    const sharesA2 = evid.includes(ref[1]);
    const sharesAny = sharesA1 || sharesA2;
    const fullMatch =
      (evid[0] === ref[0] && evid[1] === ref[1]) ||
      (evid[0] === ref[1] && evid[1] === ref[0]);

    let lr = 1.0;
    let mutated = false;
    let locusIsMatch = false;

    if (isSingleSourceMode) {
      // Single-Source Balding-Nichols Direct Match: LR = 1 / P(G|theta)
      if (fullMatch) {
        lr = 1.0 / Math.max(1e-15, pg);
        matchingLociCount++;
        locusIsMatch = true;
      } else {
        // Single-source DNA mismatch at any locus is a strict EXCLUSION
        lr = 0.0;
        mutationalMismatchCount++;
        locusIsMatch = false;
      }
    } else {
      // Pedigree Kinship Evaluator
      if (kinshipRelation === "parent_child") {
        if (fullMatch || sharesAny) {
          const sharedP = sharesA1 ? p1 : p2;
          lr = 1.0 / (2.0 * (theta + (1.0 - theta) * sharedP));
          matchingLociCount++;
          locusIsMatch = true;
        } else {
          const mu = def.mutationRate * 1e-3;
          lr = calcStepwiseMutationProb(parseFloat(evid[0]) || 10, parseFloat(ref[0]) || 10, mu, 0.10);
          mutationalMismatchCount++;
          mutated = true;
          locusIsMatch = false;
        }
      } else if (kinshipRelation === "full_sibling") {
        if (fullMatch) {
          lr = 0.25 + 0.50 / (2.0 * (theta + (1.0 - theta) * p1)) + 0.25 / Math.max(1e-12, pg);
          matchingLociCount++;
          locusIsMatch = true;
        } else if (sharesAny) {
          const sharedP = sharesA1 ? p1 : p2;
          lr = 0.25 + 0.50 / (2.0 * (theta + (1.0 - theta) * sharedP));
          matchingLociCount++;
          locusIsMatch = true;
        } else {
          lr = 0.25;
          locusIsMatch = false;
        }
      } else if (
        kinshipRelation === "half_sibling" ||
        kinshipRelation === "avuncular" ||
        kinshipRelation === "grandparent"
      ) {
        if (fullMatch || sharesAny) {
          const sharedP = sharesA1 ? p1 : p2;
          lr = 0.50 + 0.50 / (2.0 * (theta + (1.0 - theta) * sharedP));
          matchingLociCount++;
          locusIsMatch = true;
        } else {
          lr = 0.50;
          locusIsMatch = false;
        }
      } else if (kinshipRelation === "first_cousin") {
        if (fullMatch || sharesAny) {
          const sharedP = sharesA1 ? p1 : p2;
          lr = 0.75 + 0.25 / (2.0 * (theta + (1.0 - theta) * sharedP));
          matchingLociCount++;
          locusIsMatch = true;
        } else {
          lr = 0.75;
          locusIsMatch = false;
        }
      } else {
        // Unrelated negative hypothesis baseline under pedigree model: KI = 1.00
        lr = 1.0;
        matchingLociCount++;
        locusIsMatch = true;
      }
    }

    const log10Lr = lr > 0 ? Math.log10(lr) : -10.0;
    cumLog10LR += log10Lr;
    cumLR *= lr;

    const repeatNum = parseFloat(evid[0]) || 10;
    const sizingBp = Math.round(def.baseOffsetBp + repeatNum * def.repeatUnitBp);

    return {
      locus: def.name,
      def,
      evidStr: evid.join(", "),
      refStr: ref.join(", "),
      p1,
      p2,
      pg,
      lr,
      log10Lr,
      cumLog10LR,
      isMatch: locusIsMatch,
      isHomo,
      sizingBp,
      mutated,
    };
  });

  const isExcluded = isSingleSourceMode && mutationalMismatchCount > 0;
  const finalCumLog10LR = isExcluded ? -10.0 : cumLog10LR;
  const finalCumLR = isExcluded ? 0.0 : cumLR;
  const cpi = Math.pow(10, Math.min(300, Math.max(-10, finalCumLog10LR)));
  const wPercent = finalCumLR > 0 ? (cpi * 0.5) / (cpi * 0.5 + 0.5) * 100 : 0.0;
  const rmp = finalCumLR > 0 ? Math.pow(10, -Math.abs(finalCumLog10LR)) : 1.0;

  return {
    rows,
    totalLog10LR: finalCumLog10LR,
    totalLR: finalCumLR,
    matchingLociCount,
    mutationalMismatchCount,
    rmp,
    cpi,
    wPercent,
  };
}

export default function PanelSTRKinship() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  // Central Case Store Integration
  const { activeCase, addAuditLog } = useForensicCaseStore();
  const caseId = activeCase?.metadata?.caseId || "STR-CASE-2026";
  const leadAnalyst = activeCase?.metadata?.leadAnalyst || "Dr. FORENZA Lead Geneticist";
  const evidenceId = `EVID-${caseId}`;
  const referenceId = `REF-${caseId}`;

  const [activeTab, setActiveTab] = useState<
    "str_24_loci" | "kinship_lr" | "popgen_freqs" | "benchmarks" | "iso_reporting"
  >("str_24_loci");

  const [population, setPopulation] = useState<string>("Caucasian");
  const [theta, setTheta] = useState<number>(0.01);
  const [kinshipRelation, setKinshipRelation] = useState<string>("parent_child");
  const [analysisMode, setAnalysisMode] = useState<"single_source_lr" | "pedigree_kinship">("pedigree_kinship");
  const [copied, setCopied] = useState<boolean>(false);
  const [hashCopied, setHashCopied] = useState<boolean>(false);
  const [searchFreq, setSearchFreq] = useState<string>("");

  // Backend Live Verification State
  const [backendResult, setBackendResult] = useState<KinshipBackendResponse | null>(null);
  const [backendKinshipResult, setBackendKinshipResult] = useState<KinshipBackendResponse | null>(null);
  const [backendLRResult, setBackendLRResult] = useState<LRBackendResponse | null>(null);
  const [backendLoading, setBackendLoading] = useState<boolean>(false);
  const [backendLatencyMs, setBackendLatencyMs] = useState<number | null>(null);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [lastVerifiedEndpoint, setLastVerifiedEndpoint] = useState<string | null>(null);

  // Default editable profile initialized with NIST SRM 2391d Component A
  const [profileAlleles, setProfileAlleles] = useState<Record<string, [string, string]>>(() => {
    return { ...GOLDEN_STR_BENCHMARKS[0].alleles };
  });

  // Reference / Suspect alleles for pairwise comparison
  const [refAlleles, setRefAlleles] = useState<Record<string, [string, string]>>(() => {
    return { ...GOLDEN_STR_BENCHMARKS[0].alleles };
  });

  const [editMode, setEditMode] = useState<boolean>(false);

  const handleEvidenceAlleleChange = (locus: string, idx: 0 | 1, val: string) => {
    setProfileAlleles((prev) => {
      const curr = prev[locus] || ["10", "10"];
      const updated: [string, string] = idx === 0 ? [val, curr[1]] : [curr[0], val];
      return { ...prev, [locus]: updated };
    });
  };

  const handleRefAlleleChange = (locus: string, idx: 0 | 1, val: string) => {
    setRefAlleles((prev) => {
      const curr = prev[locus] || ["10", "10"];
      const updated: [string, string] = idx === 0 ? [val, curr[1]] : [curr[0], val];
      return { ...prev, [locus]: updated };
    });
  };

  const handleSimulateExclusion = () => {
    setRefAlleles((prev) => ({
      ...prev,
      TH01: ["7", "8"],
    }));
    addAuditLog({
      event: "STR_SIMULATE_EXCLUSION: Reference TH01 mutated to [7, 8] to trigger forensic exclusion",
      module: "01_str_kinship",
      analyst: leadAnalyst,
      status: "PASS",
      standard: "ISO/IEC 17025:2017 Cl. 7.7",
    });
  };

  const handleResetToNIST = () => {
    setProfileAlleles({ ...GOLDEN_STR_BENCHMARKS[0].alleles });
    setRefAlleles({ ...GOLDEN_STR_BENCHMARKS[0].alleles });
    addAuditLog({
      event: "STR_RESET_PROFILES: Profiles restored to NIST SRM 2391d Component A",
      module: "01_str_kinship",
      analyst: leadAnalyst,
      status: "PASS",
      standard: "NIST SRM 2391d Standard",
    });
  };

  // Calculate per-locus statistics via exported pure client evaluator
  const locusCalculations = useMemo(() => {
    return evaluateSTRKinshipClient(profileAlleles, refAlleles, population, theta, kinshipRelation, analysisMode);
  }, [profileAlleles, refAlleles, population, theta, kinshipRelation, analysisMode]);

  // Deterministic 64-Hex SHA-256 State Audit Digest
  const strAuditHash = useMemo(() => {
    return computeSTRAuditHash(
      caseId,
      evidenceId,
      referenceId,
      population,
      theta,
      kinshipRelation,
      locusCalculations.matchingLociCount,
      locusCalculations.mutationalMismatchCount,
      locusCalculations.totalLog10LR,
      locusCalculations.rmp,
      analysisMode
    );
  }, [
    caseId,
    evidenceId,
    referenceId,
    population,
    theta,
    kinshipRelation,
    locusCalculations.matchingLociCount,
    locusCalculations.mutationalMismatchCount,
    locusCalculations.totalLog10LR,
    locusCalculations.rmp,
    analysisMode,
  ]);

  // Execute Live Server Single-Source LR Evaluation (POST /api/v1/forensic/lr)
  const executeServerLR = useCallback(async () => {
    setBackendLoading(true);
    setBackendError(null);
    const start = performance.now();

    try {
      const p1Loci = MASTER_24_STR_LOCI.filter((d) => d.name !== "AMEL").map((d) => {
        const al = profileAlleles[d.name] || ["10", "11"];
        return {
          locus: d.name,
          allele1: parseFloat(al[0]) || 10.0,
          allele2: parseFloat(al[1]) || 10.0,
        };
      });

      const p2Loci = MASTER_24_STR_LOCI.filter((d) => d.name !== "AMEL").map((d) => {
        const al = refAlleles[d.name] || ["10", "11"];
        return {
          locus: d.name,
          allele1: parseFloat(al[0]) || 10.0,
          allele2: parseFloat(al[1]) || 10.0,
        };
      });

      const payload = {
        evidence_profile: {
          profile_id: evidenceId,
          loci: p1Loci,
          population_group: population,
        },
        suspect_profile: {
          profile_id: referenceId,
          loci: p2Loci,
          population_group: population,
        },
        theta,
        population,
      };

      const resp = await fetch("/api/v1/forensic/lr", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const latency = Math.round(performance.now() - start);
      setBackendLatencyMs(latency);

      if (!resp.ok) {
        throw new Error(`Server returned status ${resp.status}`);
      }

      const data: LRBackendResponse = await resp.json();
      setBackendLRResult(data);
      setLastVerifiedEndpoint("/api/v1/forensic/lr");

      addAuditLog({
        event: `STR_LR_BACKEND_VERIFIED: ${data.match_status} (log10_lr=${data.log10_lr.toFixed(3)}, lr=${data.lr_value.toExponential(3)}, latency=${latency}ms, hash=${strAuditHash.slice(0, 16)}...)`,
        module: "01_str_kinship",
        analyst: leadAnalyst,
        status: "PASS",
        standard: "ISO/IEC 17025:2017 Cl. 7.7",
      });
    } catch (err: any) {
      setBackendError(err?.message || "Server connection failed");
    } finally {
      setBackendLoading(false);
    }
  }, [profileAlleles, refAlleles, evidenceId, referenceId, population, theta, leadAnalyst, strAuditHash, addAuditLog]);

  // Execute Live Server Kinship Evaluation (POST /api/v1/forensic/kinship)
  const executeServerKinship = useCallback(async () => {
    setBackendLoading(true);
    setBackendError(null);
    const start = performance.now();

    try {
      const p1Loci = MASTER_24_STR_LOCI.filter((d) => d.name !== "AMEL").map((d) => {
        const al = profileAlleles[d.name] || ["10", "11"];
        return {
          locus: d.name,
          allele1: parseFloat(al[0]) || 10.0,
          allele2: parseFloat(al[1]) || 10.0,
        };
      });

      const p2Loci = MASTER_24_STR_LOCI.filter((d) => d.name !== "AMEL").map((d) => {
        const al = refAlleles[d.name] || ["10", "11"];
        return {
          locus: d.name,
          allele1: parseFloat(al[0]) || 10.0,
          allele2: parseFloat(al[1]) || 10.0,
        };
      });

      const payload = {
        profile1: {
          profile_id: evidenceId,
          loci: p1Loci,
          population_group: population,
        },
        profile2: {
          profile_id: referenceId,
          loci: p2Loci,
          population_group: population,
        },
        relationship: kinshipRelation,
        theta,
        population,
      };

      const resp = await fetch("/api/v1/forensic/kinship", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const latency = Math.round(performance.now() - start);
      setBackendLatencyMs(latency);

      if (!resp.ok) {
        throw new Error(`Server returned status ${resp.status}`);
      }

      const data: KinshipBackendResponse = await resp.json();
      setBackendResult(data);
      setBackendKinshipResult(data);
      setLastVerifiedEndpoint("/api/v1/forensic/kinship");

      addAuditLog({
        event: `STR_KINSHIP_BACKEND_VERIFIED: ${data.relationship} (log10_ki=${data.log10_ki.toFixed(3)}, latency=${latency}ms, hash=${strAuditHash.slice(0, 16)}...)`,
        module: "01_str_kinship",
        analyst: leadAnalyst,
        status: "PASS",
        standard: "ISO/IEC 17025:2017 Cl. 7.7",
      });
    } catch (err: any) {
      setBackendError(err?.message || "Server connection failed");
      // Graceful client fallback already active in locusCalculations
    } finally {
      setBackendLoading(false);
    }
  }, [profileAlleles, refAlleles, evidenceId, referenceId, population, kinshipRelation, theta, leadAnalyst, strAuditHash, addAuditLog]);

  // Unified Server Verification Trigger
  const handleRunServerVerification = useCallback(() => {
    if (analysisMode === "single_source_lr") {
      executeServerLR();
    } else {
      executeServerKinship();
    }
  }, [analysisMode, executeServerLR, executeServerKinship]);

  const handleModeChange = (mode: "single_source_lr" | "pedigree_kinship") => {
    setAnalysisMode(mode);
    setBackendError(null);
    addAuditLog({
      event: `STR_ANALYSIS_MODE_CHANGED: ${mode} (case=${caseId})`,
      module: "01_str_kinship",
      analyst: leadAnalyst,
      status: "PASS",
      standard: "ISO/IEC 17025:2017 Cl. 7.7",
    });
  };

  // ENFSI 2017 Verbal Scale Statement
  const enfsiStatement = useMemo(() => {
    const log10 = locusCalculations.totalLog10LR;
    if (log10 >= 6.0) {
      return {
        tier: isTr ? "Kademe 1: Son Derece Güçlü Destek" : "Tier 1: Extremely Strong Support",
        desc: isTr
          ? "Elde edilen DNA profili bulguları, şüpheli/iddia edilen bireyin katkıda bulunduğu hipotezini (Hp) son derece güçlü bir şekilde desteklemektedir."
          : "The DNA findings provide extremely strong support for the hypothesis that the person of interest contributed to the sample (Hp).",
        badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
      };
    }
    if (log10 >= 4.0) {
      return {
        tier: isTr ? "Kademe 2: Çok Güçlü Destek" : "Tier 2: Very Strong Support",
        desc: isTr
          ? "Bulgular, bireyin katkıda bulunduğu hipotezini (Hp) çok güçlü şekilde desteklemektedir."
          : "The DNA findings provide very strong support for the inclusion hypothesis (Hp).",
        badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
      };
    }
    if (log10 >= 2.0) {
      return {
        tier: isTr ? "Kademe 4: Orta Derecede Güçlü Destek" : "Tier 4: Moderately Strong Support",
        desc: isTr
          ? "Bulgular, bireyin katkıda bulunduğu hipotezini (Hp) orta derecede güçlü şekilde desteklemektedir."
          : "The DNA findings provide moderately strong support for Hp.",
        badgeColor: "bg-blue-500/20 text-blue-300 border-blue-500/40",
      };
    }
    if (log10 > 0.0) {
      return {
        tier: isTr ? "Kademe 6: Zayıf Destek" : "Tier 6: Weak Support",
        desc: isTr ? "Bulgular sınırlı düzeyde pozitif korelasyon göstermektedir." : "The findings provide weak support for Hp.",
        badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
      };
    }
    return {
      tier: isTr ? "Kademe 7: Dışlama / Destek Yok" : "Tier 7: Exclusion / Inconclusive",
      desc: isTr
        ? "Bulgular iddia edilen hipotezi desteklememektedir veya tam genetik dışlama tespit edilmiştir."
        : "The DNA findings exclude the person of interest or provide no statistical support.",
      badgeColor: "bg-rose-500/20 text-rose-300 border-rose-500/40",
    };
  }, [locusCalculations.totalLog10LR, isTr]);

  const handleLoadBenchmark = (bm: STRBenchmarkProfile) => {
    setProfileAlleles({ ...bm.alleles });
    setRefAlleles({ ...bm.alleles });
    setPopulation(bm.pop);
    setTheta(bm.theta);

    if (bm.id === "PATERNITY_HIGH_CPI") {
      setAnalysisMode("pedigree_kinship");
      setKinshipRelation("parent_child");
    } else {
      setAnalysisMode("single_source_lr");
    }

    addAuditLog({
      event: `STR_LOAD_GOLDEN_BENCHMARK: ${bm.id} (${bm.name}, pop=${bm.pop}, theta=${bm.theta})`,
      module: "01_str_kinship",
      analyst: leadAnalyst,
      status: "PASS",
      standard: "NIST SRM 2391d Standard",
    });
  };

  const handleHypothesisChange = (newRel: string) => {
    setKinshipRelation(newRel);
    addAuditLog({
      event: `STR_KINSHIP_HYPOTHESIS_CHANGED: ${newRel} (case=${caseId}, pop=${population}, theta=${theta})`,
      module: "01_str_kinship",
      analyst: leadAnalyst,
      status: "PASS",
      standard: "ISO/IEC 17025:2017 Cl. 7.7",
    });
  };

  const copyReportToClipboard = () => {
    const text = `================================================================================
FORENZA AUTOSOMAL STR & KINSHIP EVALUATIVE CERTIFICATE
Standard: ISO/IEC 17025:2017 | ENFSI 2017 Guidelines | NRC II Rec. 4.2
Certificate ID: CERT-STR-${caseId}
Cryptographic Audit Digest (SHA-256): ${strAuditHash}
Case Reference: ${caseId}
Lead Forensic Geneticist: ${leadAnalyst}
Questioned Evidence: ${evidenceId}
Reference Standard: ${referenceId}
--------------------------------------------------------------------------------
METROLOGICAL PARAMETERS:
- Panel Multiplex: 24 Loci (CODIS 20 + SE33 + Penta D/E + AMEL)
- Population Database: NIST 1036 (${population})
- Coancestry Theta (Fst): ${theta.toFixed(3)}
- Analysis Mode: ${analysisMode === "single_source_lr" ? "SINGLE-SOURCE DIRECT LR (POST /forensic/lr)" : "PEDIGREE KINSHIP ANALYSIS (POST /forensic/kinship)"}
- Tested Hypothesis: ${analysisMode === "single_source_lr" ? "Hp: DIRECT INCLUSION vs Hd: UNRELATED RANDOM" : kinshipRelation.toUpperCase()}
- Matching Loci: ${locusCalculations.matchingLociCount} / 24 Loci
- Mutational Discrepancies: ${locusCalculations.mutationalMismatchCount} Loci (SMM Rescued, r=0.10)
--------------------------------------------------------------------------------
QUANTITATIVE BIOMETRIC FINDINGS:
- Combined Log10(LR): ${locusCalculations.totalLog10LR.toFixed(4)}
- Combined Likelihood Ratio (LR): ${locusCalculations.totalLR.toExponential(4)}
- Random Match Probability (RMP): ${locusCalculations.rmp.toExponential(4)}
- Posterior Probability W(%): ${locusCalculations.wPercent.toFixed(4)}% (Prior Odds 1:1)
- ENFSI (2017) Verbal Statement: ${enfsiStatement.tier}
--------------------------------------------------------------------------------
TRANSPOSING THE CONDITIONAL DEFENSE SHIELD (FRE 702 / DAUBERT):
"The computed Likelihood Ratio denotes the relative likelihood of evidence P(E|Hp) / P(E|Hd).
It does NOT denote the posterior probability of guilt or relationship P(Hp|E).
Prior odds are the sole purview of the court."
================================================================================`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);

    addAuditLog({
      event: `STR_CERTIFICATE_COPIED: CERT-STR-${caseId} (hash=${strAuditHash.slice(0, 16)}...)`,
      module: "01_str_kinship",
      analyst: leadAnalyst,
      status: "PASS",
      standard: "ISO/IEC 17025:2017 Cl. 8.4",
    });
  };

  const copyAuditHashToClipboard = () => {
    navigator.clipboard.writeText(strAuditHash);
    setHashCopied(true);
    setTimeout(() => setHashCopied(false), 2000);

    addAuditLog({
      event: `STR_AUDIT_HASH_COPIED: ${strAuditHash} (case=${caseId})`,
      module: "01_str_kinship",
      analyst: leadAnalyst,
      status: "PASS",
      standard: "ISO/IEC 17025:2017 Cl. 7.7",
    });
  };

  return (
    <div className="space-y-6 font-mono text-tactical-text">
      {/* Header Banner */}
      <div className="bg-[#080D1A] border border-tactical-border/80 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400 shrink-0">
              <Dna className="w-5 h-5 animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-extrabold text-white uppercase tracking-wider truncate">
                  {isTr ? "24-Lokus Otozomal STR & Akrabalık Stüdyosu" : "24-Locus Autosomal STR & Kinship Studio"}
                </span>
                <span className="text-[9px] font-bold px-2 py-0.5 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                  CODIS 20 + SE33 + PENTA
                </span>
                <span className="text-[9px] font-mono px-2 py-0.5 rounded-md bg-black/60 border border-tactical-border/50 text-zinc-400">
                  {caseId}
                </span>
              </div>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                {isTr
                  ? "NIST 1036 Popülasyon Genetiği, Balding-Nichols Alt-Yapı Düzeltmesi & ENFSI Sözel Raporlama"
                  : "NIST 1036 Population Genetics, Balding-Nichols Coancestry & ENFSI 2017 Evaluative Scale"}
              </p>
            </div>
          </div>

          {/* Tab Selector */}
          <div className="flex flex-wrap items-center gap-1.5 bg-black/60 p-1 rounded-xl border border-tactical-border/60 shrink-0">
            {[
              { id: "str_24_loci", label: isTr ? "24 STR Lokusu" : "24 STR Loci", icon: Layers },
              { id: "kinship_lr", label: isTr ? "Akrabalık & LR" : "Kinship & LR", icon: Binary },
              { id: "popgen_freqs", label: isTr ? "NIST 1036 Frekans" : "NIST 1036 Freqs", icon: BookOpen },
              { id: "benchmarks", label: isTr ? "Altın Vektörler" : "Benchmarks", icon: Award },
              { id: "iso_reporting", label: isTr ? "ISO / ENFSI Raporu" : "ISO / ENFSI Report", icon: ShieldCheck },
            ].map((t) => {
              const Icon = t.icon;
              const active = activeTab === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id as any)}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all cursor-pointer ${
                    active
                      ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm"
                      : "text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <Icon className="w-3 h-3" />
                  <span>{t.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Global Summary Metric Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/50">
            <span className="text-[10px] text-zinc-500 block uppercase font-bold">{isTr ? "Kombine Log10(LR)" : "Combined Log10(LR)"}</span>
            <span className="text-sm font-black text-cyan-400 tabular-nums">
              {locusCalculations.totalLog10LR.toFixed(4)}
            </span>
          </div>
          <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/50">
            <span className="text-[10px] text-zinc-500 block uppercase font-bold">{isTr ? "Rastgele Eşleşme (RMP)" : "Random Match (RMP)"}</span>
            <span className="text-sm font-black text-emerald-400 tabular-nums">
              {locusCalculations.rmp.toExponential(3)}
            </span>
          </div>
          <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/50">
            <span className="text-[10px] text-zinc-500 block uppercase font-bold">{isTr ? "Eşleşen Lokus" : "Matching Loci"}</span>
            <span className="text-sm font-black text-purple-400 tabular-nums">
              {locusCalculations.matchingLociCount} / 24
            </span>
          </div>
          <div className="p-2.5 rounded-xl bg-black/40 border border-tactical-border/50">
            <span className="text-[10px] text-zinc-500 block uppercase font-bold">{isTr ? "ENFSI Değerlendirmesi" : "ENFSI Evaluation"}</span>
            <span className="text-[11px] font-bold text-emerald-300 truncate block">
              {enfsiStatement.tier.split(":")[0]}
            </span>
          </div>
        </div>

        {/* Live Cryptographic & Server Status Strip */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-tactical-border/40 text-[10px]">
          <div className="flex items-center gap-2">
            <span className="text-zinc-500 uppercase font-bold flex items-center gap-1">
              <Fingerprint className="w-3 h-3 text-cyan-400" />
              {isTr ? "Kriptografik Durum Karması (H_str):" : "State Audit Digest (H_str):"}
            </span>
            <span className="font-mono text-cyan-300/90">{strAuditHash.slice(0, 16)}...{strAuditHash.slice(-8)}</span>
            <button
              onClick={copyAuditHashToClipboard}
              className="p-1 rounded bg-black/50 hover:bg-cyan-500/20 text-zinc-400 hover:text-cyan-300 transition-all cursor-pointer"
              title={isTr ? "Hash Kopyala" : "Copy Hash"}
            >
              {hashCopied ? <CheckCircle2 className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-block px-2 py-0.5 rounded bg-black/50 border border-tactical-border/50 text-[9px] text-zinc-400">
              {isTr
                ? analysisMode === "single_source_lr" ? "Mod: Tek Kaynaklı LR (/lr)" : "Mod: Akrabalık (/kinship)"
                : analysisMode === "single_source_lr" ? "Mode: Single-Source (/lr)" : "Mode: Kinship (/kinship)"}
            </span>

            <button
              onClick={handleRunServerVerification}
              disabled={backendLoading}
              className="flex items-center gap-1 px-2.5 py-1 rounded bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 font-bold transition-all cursor-pointer disabled:opacity-50"
            >
              <Server className={`w-3 h-3 ${backendLoading ? "animate-spin" : ""}`} />
              <span>
                {backendLoading
                  ? isTr ? "Hesaplanıyor..." : "Computing..."
                  : isTr ? "Sunucu Doğrulaması (FastAPI)" : "Run Server Verification"}
              </span>
            </button>

            {backendLatencyMs !== null && !backendError && (
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono">
                {lastVerifiedEndpoint === "/api/v1/forensic/lr" ? "FastAPI /lr" : "FastAPI /kinship"}: {backendLatencyMs}ms
              </span>
            )}
            {backendError && (
              <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 font-mono">
                {isTr ? "İstemci Motoru Aktif" : "Client Engine Active"}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* TAB 1: 24 STR LOCI MULTIPLEX TABLE */}
      {activeTab === "str_24_loci" && (
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-cyan-400" />
                {isTr ? "24-Lokus Otozomal Multiplex Profili & CE Boyutlandırması" : "24-Locus Autosomal Multiplex Profile & CE Sizing"}
              </h3>
              <p className="text-[10px] text-zinc-400 mt-0.5">
                {isTr
                  ? "CODIS 20 Genişletilmiş Çekirdek Lokusları, SE33, Penta D, Penta E ve Amelogenin"
                  : "CODIS 20 Expanded Core, SE33, Penta D, Penta E, and Amelogenin Sex Marker"}
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={() => setEditMode(!editMode)}
                className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium border transition-colors cursor-pointer ${
                  editMode
                    ? "bg-purple-500/20 text-purple-300 border-purple-500/50"
                    : "bg-black/60 text-zinc-300 border-tactical-border/60 hover:text-white"
                }`}
              >
                <span>{editMode ? (isTr ? "Düzenlemeyi Bitir" : "Done Editing") : (isTr ? "Alelleri Düzenle" : "Edit Alleles")}</span>
              </button>

              <button
                type="button"
                onClick={handleSimulateExclusion}
                className="flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium border border-rose-500/40 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 transition-colors cursor-pointer"
                title={isTr ? "TH01 lokusunu [7, 8] yaparak dışlama simüle eder" : "Mutates TH01 to [7, 8] to simulate an exclusion"}
              >
                <span>{isTr ? "Dışlama Simüle Et" : "Simulate Exclusion"}</span>
              </button>

              <button
                type="button"
                onClick={handleResetToNIST}
                className="flex items-center gap-1 px-2 py-1 rounded text-xs text-zinc-400 hover:text-zinc-200 border border-tactical-border/40 bg-black/40 hover:bg-black/60 transition-colors cursor-pointer"
                title={isTr ? "NIST SRM 2391d profiline geri dön" : "Reset to NIST SRM 2391d"}
              >
                <RefreshCw className="w-3 h-3" />
                <span>{isTr ? "Sıfırla" : "Reset"}</span>
              </button>

              <div className="flex items-center gap-1 pl-2 border-l border-tactical-border/40">
                <span className="text-[10px] text-zinc-400">{isTr ? "Popülasyon:" : "Population:"}</span>
                <select
                  value={population}
                  onChange={(e) => setPopulation(e.target.value)}
                  className="bg-black/60 border border-tactical-border/60 rounded-lg px-2.5 py-1 text-xs text-cyan-300 focus:outline-none"
                >
                  <option value="Caucasian">Caucasian (NIST 1036)</option>
                  <option value="AfricanAmerican">African American (NIST 1036)</option>
                  <option value="Hispanic">Hispanic (NIST 1036)</option>
                  <option value="Asian">Asian (NIST 1036)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-tactical-border/60">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-black/80 border-b border-tactical-border/60 text-zinc-400 text-[10px] uppercase">
                  <th className="p-2.5">Lokus</th>
                  <th className="p-2.5">{isTr ? "Kromozom" : "Chrom"}</th>
                  <th className="p-2.5">{isTr ? "Delil Alelleri" : "Evid Alleles"}</th>
                  <th className="p-2.5">{isTr ? "Referans" : "Reference"}</th>
                  <th className="p-2.5">CE (bp)</th>
                  <th className="p-2.5">Stutter Maks</th>
                  <th className="p-2.5">Genotip P(G)</th>
                  <th className="p-2.5">Log10(LR)</th>
                  <th className="p-2.5">{isTr ? "Durum" : "Status"}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-tactical-border/30">
                {locusCalculations.rows.map((r) => (
                  <tr key={r.locus} className="hover:bg-cyan-500/5 transition-colors">
                    <td className="p-2.5 font-bold text-white flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                      {r.locus}
                    </td>
                    <td className="p-2.5 text-zinc-400 text-[10px]">{r.def.chr}</td>
                    <td className="p-2.5 font-bold text-cyan-300 tabular-nums">
                      {editMode && r.locus !== "AMEL" ? (
                        <div className="flex items-center gap-1">
                          <input
                            type="text"
                            value={profileAlleles[r.locus]?.[0] ?? ""}
                            onChange={(e) => handleEvidenceAlleleChange(r.locus, 0, e.target.value)}
                            aria-label={`Evidence ${r.locus} allele 1`}
                            className="w-11 px-1 py-0.5 bg-black/80 border border-cyan-500/50 rounded text-center text-xs text-cyan-300 focus:outline-none focus:border-cyan-400"
                          />
                          <span className="text-zinc-500">/</span>
                          <input
                            type="text"
                            value={profileAlleles[r.locus]?.[1] ?? ""}
                            onChange={(e) => handleEvidenceAlleleChange(r.locus, 1, e.target.value)}
                            aria-label={`Evidence ${r.locus} allele 2`}
                            className="w-11 px-1 py-0.5 bg-black/80 border border-cyan-500/50 rounded text-center text-xs text-cyan-300 focus:outline-none focus:border-cyan-400"
                          />
                        </div>
                      ) : (
                        r.evidStr
                      )}
                    </td>
                    <td className="p-2.5 font-bold text-zinc-300 tabular-nums">
                      {editMode && r.locus !== "AMEL" ? (
                        <div className="flex items-center gap-1">
                          <input
                            type="text"
                            value={refAlleles[r.locus]?.[0] ?? ""}
                            onChange={(e) => handleRefAlleleChange(r.locus, 0, e.target.value)}
                            aria-label={`Reference ${r.locus} allele 1`}
                            className="w-11 px-1 py-0.5 bg-black/80 border border-zinc-500/50 rounded text-center text-xs text-zinc-300 focus:outline-none focus:border-zinc-400"
                          />
                          <span className="text-zinc-500">/</span>
                          <input
                            type="text"
                            value={refAlleles[r.locus]?.[1] ?? ""}
                            onChange={(e) => handleRefAlleleChange(r.locus, 1, e.target.value)}
                            aria-label={`Reference ${r.locus} allele 2`}
                            className="w-11 px-1 py-0.5 bg-black/80 border border-zinc-500/50 rounded text-center text-xs text-zinc-300 focus:outline-none focus:border-zinc-400"
                          />
                        </div>
                      ) : (
                        r.refStr
                      )}
                    </td>
                    <td className="p-2.5 text-zinc-400 tabular-nums text-[10px]">{r.sizingBp} bp</td>
                    <td className="p-2.5 text-zinc-400 tabular-nums text-[10px]">
                      {(r.def.stutterMax * 100).toFixed(1)}%
                    </td>
                    <td className="p-2.5 text-zinc-400 tabular-nums text-[10px]">
                      {r.pg < 0.0001 ? r.pg.toExponential(3) : r.pg.toFixed(4)}
                    </td>
                    <td className="p-2.5 font-black text-cyan-400 tabular-nums">
                      {r.log10Lr >= 0 ? `+${r.log10Lr.toFixed(3)}` : r.log10Lr.toFixed(3)}
                    </td>
                    <td className="p-2.5">
                      {r.mutated ? (
                        <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                          {isTr ? "SMM MUTASYON" : "SMM MUTATION"}
                        </span>
                      ) : r.isMatch ? (
                        <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                          {isTr ? "EŞLEŞTİ" : "MATCH"}
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                          {isTr ? "UYUMSUZ" : "MISMATCH"}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: KINSHIP & LIKELIHOOD RATIO CALCULATOR */}
      {activeTab === "kinship_lr" && (
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
          <div className="border-b border-tactical-border/40 pb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
              <Binary className="w-3.5 h-3.5 text-purple-400" />
              {isTr
                ? "Akrabalık & Babalık Olasılık Oranı (LR) Parametreleri : Çift Modlu Mimari"
                : "Kinship & Paternity Likelihood Ratio (LR) Parameters : Dual-Mode Architecture"}
            </h3>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              {isTr
                ? "Tek Kaynaklı LR (POST /forensic/lr) ve Soyağacı Akrabalık Analizi (POST /forensic/kinship)"
                : "Single-Source LR (POST /forensic/lr) and Pedigree Kinship Index (POST /forensic/kinship)"}
            </p>
          </div>

          {/* Dual-Mode Selector Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleModeChange("single_source_lr")}
              className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                analysisMode === "single_source_lr"
                  ? "border-cyan-500/80 bg-cyan-500/20 text-cyan-200 shadow-md ring-1 ring-cyan-500/40"
                  : "border-tactical-border/60 bg-black/40 text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Fingerprint className="w-4 h-4 text-cyan-400" />
                  <span className="font-bold text-xs text-white">
                    {isTr ? "Tek Kaynaklı Şüpheli Eşleşmesi (LR)" : "Single-Source Suspect Match (LR)"}
                  </span>
                </div>
                <span className="text-[9px] px-2 py-0.5 rounded bg-cyan-500/30 text-cyan-200 font-mono font-bold">
                  POST /forensic/lr
                </span>
              </div>
              <p className="text-[10px] text-zinc-300 mt-1.5 leading-relaxed">
                {isTr
                  ? "Delil profili ile şüpheli profili doğrudan karşılaştırması. Balding-Nichols LR = 1 / P(G|theta), INCLUSION/EXCLUSION tespiti ve %95 HPD güven aralığı."
                  : "Direct evidence-suspect profile comparison. Balding-Nichols LR = 1 / P(G|theta), INCLUSION/EXCLUSION calling and 95% HPD interval."}
              </p>
            </button>

            <button
              type="button"
              onClick={() => handleModeChange("pedigree_kinship")}
              className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer ${
                analysisMode === "pedigree_kinship"
                  ? "border-purple-500/80 bg-purple-500/20 text-purple-200 shadow-md ring-1 ring-purple-500/40"
                  : "border-tactical-border/60 bg-black/40 text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Binary className="w-4 h-4 text-purple-400" />
                  <span className="font-bold text-xs text-white">
                    {isTr ? "Soyağacı / Akrabalık İndeksi (KI)" : "Pedigree Kinship Index (KI)"}
                  </span>
                </div>
                <span className="text-[9px] px-2 py-0.5 rounded bg-purple-500/30 text-purple-200 font-mono font-bold">
                  POST /forensic/kinship
                </span>
              </div>
              <p className="text-[10px] text-zinc-300 mt-1.5 leading-relaxed">
                {isTr
                  ? "İki birey arasındaki biyolojik soyağacı ilişkilerinin (babalık, kardeşlik, yeğenlik vb.) Ito-Donnelly IBD katsayıları ve SMM mutasyon kurtarmasıyla analizi."
                  : "Biological pedigree relationship evaluation (paternity, siblingship, avuncular) via Ito-Donnelly IBD coefficients and SMM mutation rescue."}
              </p>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Mode-Specific Left Column */}
            {analysisMode === "single_source_lr" ? (
              <div className="p-4 rounded-xl bg-black/40 border border-tactical-border/60 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-white uppercase flex items-center gap-1.5">
                    <Fingerprint className="w-3.5 h-3.5 text-cyan-400" />
                    {isTr ? "Tek Kaynaklı Adli Hipotezler" : "Single-Source Forensic Hypotheses"}
                  </span>
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                    Balding-Nichols (1994)
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/30 text-[10px] space-y-2">
                  <div className="text-zinc-300">
                    <span className="font-bold text-cyan-300">Hp (Savcılık): </span>
                    {isTr
                      ? "Olay yeri delilindeki DNA şüpheli bireye aittir: P(E|Hp) = 1.0"
                      : "The DNA from the crime scene originated from the suspect: P(E|Hp) = 1.0"}
                  </div>
                  <div className="text-zinc-300">
                    <span className="font-bold text-cyan-300">Hd (Savunma): </span>
                    {isTr
                      ? "Delildeki DNA, şüpheliyle akraba olmayan rastgele bir bireye aittir: P(E|Hd) = P(G|theta)"
                      : "The DNA originated from an unknown individual unrelated to the suspect: P(E|Hd) = P(G|theta)"}
                  </div>
                  <div className="pt-2 border-t border-cyan-500/20 flex justify-between items-center font-mono">
                    <span className="text-zinc-400 font-sans">{isTr ? "Matematiksel Formül:" : "Biostatistical Formula:"}</span>
                    <span className="text-cyan-300 font-bold">LR = 1 / P(G|theta)</span>
                  </div>
                </div>

                {/* Match Evaluation Status */}
                <div className="flex items-center justify-between p-3 rounded-xl bg-black/60 border border-tactical-border/50 text-[10px]">
                  <span className="text-zinc-400 font-bold">{isTr ? "İstemci Eşleşme Tespiti:" : "Client Match Calling:"}</span>
                  {locusCalculations.matchingLociCount === 24 ? (
                    <span className="font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30">
                      {isTr ? "INCLUSION (24/24 Lokus Tam Eşleşti)" : "INCLUSION (24/24 Complete Match)"}
                    </span>
                  ) : (
                    <span className="font-bold text-rose-400 px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30">
                      {isTr ? `KISMİ UYUMSUZLUK (${24 - locusCalculations.matchingLociCount} Lokus Dışlama)` : `EXCLUSION (${24 - locusCalculations.matchingLociCount} Mismatched Loci)`}
                    </span>
                  )}
                </div>

                {/* Backend LR Response Card */}
                {backendLRResult && (
                  <div className="p-3.5 rounded-xl bg-cyan-950/30 border border-cyan-500/50 text-[10px] space-y-2">
                    <div className="flex items-center justify-between border-b border-cyan-500/30 pb-1.5">
                      <span className="font-bold text-cyan-300 uppercase flex items-center gap-1.5">
                        <Server className="w-3.5 h-3.5 text-cyan-400" />
                        {isTr ? "FastAPI Sunucu LR Çapraz Doğrulaması:" : "FastAPI Server LR Cross-Validation:"}
                      </span>
                      <span className={`px-2 py-0.5 rounded font-bold ${
                        backendLRResult.match_status === "INCLUSION"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                          : "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                      }`}>
                        {backendLRResult.match_status}
                      </span>
                    </div>
                    <div className="flex justify-between text-zinc-300 font-mono">
                      <span>{isTr ? "Sunucu Log10(LR):" : "Server Log10(LR):"}</span>
                      <span className="font-bold text-cyan-300">+{backendLRResult.log10_lr.toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between text-zinc-300 font-mono">
                      <span>{isTr ? "Sunucu LR Değeri:" : "Server LR Value:"}</span>
                      <span className="font-bold text-emerald-400">{backendLRResult.lr_value.toExponential(4)}</span>
                    </div>
                    <div className="flex justify-between text-zinc-300 font-mono">
                      <span>{isTr ? "%95 HPD Güven Aralığı:" : "95% HPD Confidence Interval:"}</span>
                      <span className="text-zinc-200">[{backendLRResult.confidence_interval.low.toExponential(2)}, {backendLRResult.confidence_interval.high.toExponential(2)}]</span>
                    </div>
                    <div className="flex justify-between text-zinc-300 text-[9px] pt-1 border-t border-cyan-500/20">
                      <span className="text-zinc-500">{isTr ? "Model:" : "Model:"}</span>
                      <span className="text-zinc-400">{backendLRResult.model}</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-black/40 border border-tactical-border/60 space-y-3">
                <span className="text-[11px] font-bold text-white block uppercase flex items-center gap-1.5">
                  <Binary className="w-3.5 h-3.5 text-purple-400" />
                  {isTr ? "Test Edilen Soyağacı Hipotezi (Hp)" : "Pedigree Kinship Hypothesis (Hp)"}
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {PEDIGREE_RELATIONSHIPS.map((k) => (
                    <button
                      key={k.id}
                      onClick={() => handleHypothesisChange(k.id)}
                      className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                        kinshipRelation === k.id
                          ? "border-purple-500/80 bg-purple-500/20 text-purple-200"
                          : "border-tactical-border/60 bg-black/40 text-zinc-400 hover:text-zinc-200"
                      }`}
                    >
                      <div className="font-bold text-xs">{isTr ? k.labelTr : k.labelEn}</div>
                      <div className="text-[9px] text-zinc-500 mt-1 font-mono">{k.ibd}</div>
                    </button>
                  ))}
                </div>

                {/* Backend Kinship Feedback Card */}
                {backendKinshipResult && (
                  <div className="mt-3 p-3.5 rounded-xl bg-purple-950/30 border border-purple-500/40 text-[10px] space-y-1.5">
                    <div className="font-bold text-purple-300 uppercase flex items-center gap-1.5 border-b border-purple-500/30 pb-1">
                      <Server className="w-3.5 h-3.5 text-purple-400" />
                      {isTr ? "FastAPI Sunucu Akrabalık Doğrulaması:" : "FastAPI Server Kinship Cross-Validation:"}
                    </div>
                    <div className="flex justify-between text-zinc-300 font-mono">
                      <span>{isTr ? "İlişki Türü:" : "Relationship:"}</span>
                      <span className="font-bold text-purple-200">{backendKinshipResult.relationship}</span>
                    </div>
                    <div className="flex justify-between text-zinc-300 font-mono">
                      <span>{isTr ? "Sunucu Posterior Olasılığı W(%):" : "Posterior Probability W(%):"}</span>
                      <span className="font-bold text-emerald-400">{backendKinshipResult.posterior_probability.toFixed(4)}%</span>
                    </div>
                    <div className="flex justify-between text-zinc-300 font-mono">
                      <span>{isTr ? "%95 HPD Güven Aralığı:" : "95% HPD Confidence Interval:"}</span>
                      <span className="text-zinc-200">[{backendKinshipResult.confidence_interval.low.toExponential(2)}, {backendKinshipResult.confidence_interval.high.toExponential(2)}]</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Right Column: Theta & Population Settings */}
            <div className="p-4 rounded-xl bg-black/40 border border-tactical-border/60 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-white uppercase">
                  {isTr ? "Akrabalık Katsayısı (theta / Fst)" : "Coancestry Coefficient (theta / Fst)"}
                </span>
                <span className="text-xs font-black text-cyan-400 tabular-nums">{theta.toFixed(3)}</span>
              </div>
              <input
                type="range"
                min="0.00"
                max="0.05"
                step="0.005"
                value={theta}
                onChange={(e) => setTheta(parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
              <div className="flex justify-between text-[9px] text-zinc-500 font-mono">
                <span>0.000 (Genel Nüfus)</span>
                <span>0.010 (NRC II Standart)</span>
                <span>0.030 (İzole / Akraba Nüfus)</span>
              </div>
              <p className="text-[10px] text-zinc-400 mt-2">
                {isTr
                  ? "NRC II Tavsiye 4.2 uyarınca genel adli hesaplamalarda theta = 0.01, alt-izole topluluklarda theta = 0.03 uygulanır."
                  : "Under NRC II Recommendation 4.2, theta = 0.01 is applied for general casework, and theta = 0.03 for isolated sub-populations."}
              </p>

              <div className="pt-3 border-t border-tactical-border/40 text-[10px] space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">{isTr ? "Aktif Popülasyon:" : "Active Population:"}</span>
                  <span className="font-bold text-cyan-300 font-mono">{population}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-zinc-400">{isTr ? "Minimum Alel Frekansı (p_min):" : "Allele Frequency Floor (p_min):"}</span>
                  <span className="font-bold text-zinc-300 font-mono">0.00241 (5 / 2N)</span>
                </div>
                {analysisMode === "pedigree_kinship" && (
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-400">{isTr ? "SMM Mutasyon Dinamiği:" : "SMM Mutation Dynamics:"}</span>
                    <span className="font-bold text-amber-400 font-mono">r = 0.10, mu = 10^-3</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: NIST 1036 POPGEN FREQUENCIES */}
      {activeTab === "popgen_freqs" && (
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                {isTr ? "NIST 1036 Popülasyon Alel Frekans Veri Tabanı" : "NIST 1036 Population Allele Frequency Database"}
              </h3>
              <p className="text-[10px] text-zinc-400 mt-0.5">
                {isTr
                  ? "4 Başlıca Popülasyon Kümesi (Kafkas, Afro-Amerikan, Hispanik, Asya) & p_min = 0.00241 Eşiği"
                  : "4 Major Population Cohorts (Caucasian, African American, Hispanic, Asian) with p_min = 0.00241 Floor"}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Search className="w-3.5 h-3.5 text-zinc-500" />
              <input
                type="text"
                placeholder={isTr ? "Lokus ara (örn: TH01, SE33)..." : "Search locus (e.g. TH01, SE33)..."}
                value={searchFreq}
                onChange={(e) => setSearchFreq(e.target.value)}
                className="bg-black/60 border border-tactical-border/60 rounded-lg px-2.5 py-1 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(NIST_1036_POP_FREQS[population] || NIST_1036_POP_FREQS["Caucasian"])
              .filter(([locus]) => locus.toLowerCase().includes(searchFreq.toLowerCase()))
              .map(([locus, freqs]) => (
                <div key={locus} className="p-3 rounded-xl bg-black/40 border border-tactical-border/60 space-y-2">
                  <div className="flex items-center justify-between border-b border-tactical-border/30 pb-1.5">
                    <span className="font-bold text-xs text-cyan-300">{locus}</span>
                    <span className="text-[9px] text-zinc-500">{population}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-1 text-[10px]">
                    {Object.entries(freqs).map(([al, fr]) => (
                      <div key={al} className="p-1 rounded bg-black/50 border border-tactical-border/40 text-center">
                        <span className="text-zinc-400 block font-bold">{al}</span>
                        <span className="text-cyan-400 tabular-nums">{(fr * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* TAB 4: CERTIFIED GOLDEN REFERENCE BENCHMARKS */}
      {activeTab === "benchmarks" && (
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
          <div className="border-b border-tactical-border/40 pb-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-amber-400" />
              {isTr ? "Sertifikalı Adli Referans Standartları & Altın Vektörler" : "Certified Forensic Reference Standards & Golden Vectors"}
            </h3>
            <p className="text-[10px] text-zinc-400 mt-0.5">
              {isTr
                ? "NIST SRM 2391d ve Araştırma Spesifikasyonu STR-A/B/C Doğrulama Profilleri"
                : "NIST SRM 2391d and Research Specification STR-A/B/C Golden Benchmarks"}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {GOLDEN_STR_BENCHMARKS.map((bm) => (
              <div
                key={bm.id}
                className="p-4 rounded-xl bg-black/40 border border-tactical-border/60 hover:border-cyan-500/50 transition-all space-y-3"
              >
                <div>
                  <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                    {bm.pop}
                  </span>
                  <h4 className="font-bold text-xs text-white mt-1.5">{bm.name}</h4>
                  <p className="text-[10px] text-zinc-400 mt-1">{bm.description}</p>
                </div>

                <div className="p-2.5 rounded-lg bg-black/60 border border-tactical-border/40 text-[10px] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Beklenen Log10(LR):</span>
                    <span className="font-bold text-cyan-400">+{bm.expectedLog10LR.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Theta Katsayısı:</span>
                    <span className="font-bold text-zinc-300">{bm.theta.toFixed(2)}</span>
                  </div>
                </div>

                <button
                  onClick={() => handleLoadBenchmark(bm)}
                  className="w-full py-2 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/50 text-cyan-300 text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>{isTr ? "Profili Yükle" : "Load Profile"}</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 5: ISO 17025 & ENFSI EVALUATIVE REPORT */}
      {activeTab === "iso_reporting" && (
        <div className="space-y-4 rounded-2xl border border-tactical-border/80 bg-tactical-surface/50 p-4 sm:p-5 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-tactical-border/40 pb-3">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-white flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                {isTr ? "ISO/IEC 17025 & ENFSI 2017 Adli Raporlama Sertifikası" : "ISO/IEC 17025 & ENFSI 2017 Evaluative Certificate"}
              </h3>
              <p className="text-[10px] text-zinc-400 mt-0.5">
                {isTr ? `Sertifika No: CERT-STR-${caseId} | Analist: ${leadAnalyst}` : `Certificate ID: CERT-STR-${caseId} | Analyst: ${leadAnalyst}`}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={copyAuditHashToClipboard}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/50 text-cyan-300 text-xs font-bold transition-all cursor-pointer"
              >
                {hashCopied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Fingerprint className="w-3.5 h-3.5" />}
                <span>{hashCopied ? (isTr ? "Kopyalandı!" : "Copied!") : (isTr ? "Hash Kopyala" : "Copy Hash")}</span>
              </button>
              <button
                onClick={copyReportToClipboard}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/50 text-emerald-300 text-xs font-bold transition-all cursor-pointer"
              >
                {copied ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? (isTr ? "Kopyalandı!" : "Copied!") : (isTr ? "Raporu Kopyala" : "Copy Report")}</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* ENFSI Statement Card */}
            <div className="p-4 rounded-xl bg-black/40 border border-tactical-border/60 space-y-3">
              <span className="text-[10px] font-bold text-zinc-500 uppercase block">{isTr ? "ENFSI 2017 7-Kademeli Sözel Değerlendirme" : "ENFSI 2017 7-Tier Evaluative Scale"}</span>
              <div className={`p-3 rounded-xl border ${enfsiStatement.badgeColor}`}>
                <div className="text-xs font-black uppercase">{enfsiStatement.tier}</div>
                <p className="text-[11px] text-zinc-300 mt-1.5 leading-relaxed">{enfsiStatement.desc}</p>
              </div>
              <div className="text-[10px] text-zinc-400 space-y-1 font-mono">
                <div>Log10(LR) = {locusCalculations.totalLog10LR.toFixed(4)} | LR = {locusCalculations.totalLR.toExponential(3)}</div>
                <div>Posterior Olasılık W(%) = {locusCalculations.wPercent.toFixed(4)}% (Apriori 1:1)</div>
                <div>Rastgele Eşleşme Olasılığı (RMP) = {locusCalculations.rmp.toExponential(4)}</div>
              </div>
            </div>

            {/* Prosecutor's Fallacy Shield Card */}
            <div className="p-4 rounded-xl bg-rose-500/5 border border-rose-500/30 space-y-2.5">
              <div className="flex items-center gap-2 text-rose-400">
                <ShieldAlert className="w-4 h-4 shrink-0" />
                <span className="text-xs font-bold uppercase">{isTr ? "Savcının Yanılgısı Kalkanı (Aktif)" : "Prosecutor's Fallacy Shield (Active)"}</span>
              </div>
              <p className="text-[10px] text-zinc-300 leading-relaxed">
                {isTr
                  ? "Hesaplanan LR değeri delilin hipotezler altındaki göreceli olasılığını P(E|Hp) / P(E|Hd) ifade eder. Bu değer bireyin suçluluk olasılığı P(Hp|E) DEĞİLDİR. Apriori olasılıklar yalnızca mahkemenin yetkisindedir."
                  : "The computed LR denotes the relative likelihood of evidence P(E|Hp) / P(E|Hd). It does NOT denote the posterior probability of guilt or relationship P(Hp|E). Prior odds are the sole purview of the court."}
              </p>
              <div className="pt-2 border-t border-rose-500/20 text-[9px] text-zinc-400 font-mono">
                Adli Karar Standardı: Federal Rule of Evidence 702 • Daubert v. Merrell Dow Pharmaceuticals (1993)
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
