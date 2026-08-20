/**
 * FORENZA VISAGE 5-CpG & Multi-Tissue Epigenetic Age Estimation Client-Side Engine
 * 
 * Verbatim from VISAGE Research Specification (research/visage_5_cpg_epigenetic_aging_research.md):
 * - Piecewise Log-Linear Elastic Net Model (Horvath Link, y0 = 20.0 pivot boundary)
 * - Direct Multiple Linear Regression (MLR) with ELOVL2 Power Transformation (Zbieć-Piekarska et al.)
 * - ISO/IEC 17025 Dynamic Mahalanobis Metrological Uncertainty with (X^T X)^-1 Covariance Matrix
 * - Standardized ENFSI Evaluative Reporting Court Statements (English & Turkish)
 */

export interface VisageCpgMarker {
  id: string;
  gene: string;
  chrom: string;
  posGrch38: number;
  ampliconBp: number;
  elasticNetWeight: number;
  mlrWeight: number;
  mlrPowerExp: number;
  meanCalibrationBeta: number;
  defaultBeta: number;
  legacyWeight?: number;
}

export const VISAGE_5CPG_MARKERS: Record<string, VisageCpgMarker> = {
  cg16867657: {
    id: "cg16867657",
    gene: "ELOVL2",
    chrom: "chr6",
    posGrch38: 11044634,
    ampliconBp: 267,
    elasticNetWeight: 2.850000,
    mlrWeight: 120.3520,
    mlrPowerExp: 2.366,
    meanCalibrationBeta: 0.3850,
    defaultBeta: 0.25,
    legacyWeight: 102.45,
  },
  cg06639320: {
    id: "cg06639320",
    gene: "FHL2",
    chrom: "chr2",
    posGrch38: 105399282,
    ampliconBp: 167,
    elasticNetWeight: 1.920000,
    mlrWeight: 38.2140,
    mlrPowerExp: 1.0,
    meanCalibrationBeta: 0.3120,
    defaultBeta: 0.20,
    legacyWeight: 74.30,
  },
  cg16419235: {
    id: "cg16419235",
    gene: "PENK",
    chrom: "chr8",
    posGrch38: 56419985,
    ampliconBp: 142,
    elasticNetWeight: 0.950000,
    mlrWeight: 21.8040,
    mlrPowerExp: 1.0,
    meanCalibrationBeta: 0.2450,
    defaultBeta: 0.30,
    legacyWeight: -45.20,
  },
  cg04523812: {
    id: "cg04523812",
    gene: "TRIM59",
    chrom: "chr3",
    posGrch38: 160450202,
    ampliconBp: 141,
    elasticNetWeight: 0.880000,
    mlrWeight: 18.9410,
    mlrPowerExp: 1.0,
    meanCalibrationBeta: 0.2810,
    defaultBeta: 0.25,
    legacyWeight: 56.80,
  },
  cg07955995: {
    id: "cg07955995",
    gene: "KLF14",
    chrom: "chr7",
    posGrch38: 130734375,
    ampliconBp: 128,
    elasticNetWeight: 1.150000,
    mlrWeight: 26.1030,
    mlrPowerExp: 1.0,
    meanCalibrationBeta: 0.2100,
    defaultBeta: 0.25,
    legacyWeight: 62.15,
  },
};

export const EXTENDED_10CPG_MARKERS: Record<string, { gene: string; legacyWeight: number; defaultBeta: number }> = {
  cg16867657: { gene: "ELOVL2", legacyWeight: 102.45, defaultBeta: 0.22 },
  cg21572722: { gene: "ELOVL2-2", legacyWeight: 88.12, defaultBeta: 0.20 },
  cg06639320: { gene: "FHL2", legacyWeight: 74.30, defaultBeta: 0.18 },
  cg16419235: { gene: "PENK", legacyWeight: -45.20, defaultBeta: 0.35 },
  cg04084157: { gene: "TRIM59", legacyWeight: 56.80, defaultBeta: 0.25 },
  cg08097417: { gene: "KLF14", legacyWeight: 62.15, defaultBeta: 0.22 },
  cg09809672: { gene: "EDARADD", legacyWeight: 41.90, defaultBeta: 0.20 },
  cg02088308: { gene: "MIR29B2CHG", legacyWeight: 38.75, defaultBeta: 0.21 },
  cg17861230: { gene: "PDE4C", legacyWeight: 49.10, defaultBeta: 0.22 },
  cg02228185: { gene: "ASPA", legacyWeight: -32.40, defaultBeta: 0.30 },
};

export const VISAGE_5CPG_CENTROID = [0.3850, 0.3120, 0.2450, 0.2810, 0.2100];

export const VISAGE_XTX_INV_5CPG = [
  [ 0.01245, -0.00312, -0.00185, -0.00210, -0.00142],
  [-0.00312,  0.00892, -0.00115, -0.00154, -0.00098],
  [-0.00185, -0.00115,  0.01540, -0.00245, -0.00120],
  [-0.00210, -0.00154, -0.00245,  0.01120, -0.00085],
  [-0.00142, -0.00098, -0.00120, -0.00085,  0.00965]
];

export const VISAGE_TISSUE_CALIBRATION: Record<string, { deltaYears: number; sePred: number; pi95Bound: number }> = {
  BLOOD: { deltaYears: 0.00, sePred: 1.95, pi95Bound: 3.82 },
  WHOLE_BLOOD: { deltaYears: 0.00, sePred: 1.95, pi95Bound: 3.82 },
  SALIVA: { deltaYears: 2.45, sePred: 2.25, pi95Bound: 4.41 },
  BUCCAL: { deltaYears: 2.45, sePred: 2.25, pi95Bound: 4.41 },
  SALIVA_BUCCAL: { deltaYears: 2.45, sePred: 2.25, pi95Bound: 4.41 },
  SEMEN: { deltaYears: 18.60, sePred: 2.60, pi95Bound: 5.10 },
  SEMINAL_FLUID: { deltaYears: 18.60, sePred: 2.60, pi95Bound: 5.10 },
  BONE: { deltaYears: 1.15, sePred: 3.05, pi95Bound: 5.98 },
  TEETH: { deltaYears: 1.15, sePred: 3.05, pi95Bound: 5.98 },
  SKELETAL_BONE: { deltaYears: 1.15, sePred: 3.05, pi95Bound: 5.98 },
  TISSUE: { deltaYears: 0.50, sePred: 2.10, pi95Bound: 4.12 },
};

export const ENFSI_CATEGORY_TR: Record<string, string> = {
  "Child / Minor": "Çocuk / Reşit Olmayan",
  "Young Adult": "Genç Yetişkin",
  "Adult": "Yetişkin",
  "Middle-Aged Adult": "Orta Yaşlı Yetişkin",
  "Senior / Elderly": "Yaşlı",
  "Adult (Buccal Matrix)": "Yetişkin (Ağız Mukozası)",
};

export interface VisagePredictionResult {
  estimated_age_years: number;
  model_age_before_offset: number;
  linear_predictor_x: number;
  developmental_stage: string;
  prediction_interval_lower: number;
  prediction_interval_upper: number;
  standard_error_years: number;
  expanded_uncertainty_95: number;
  mahalanobis_distance_squared: number;
  tissue_type: string;
  tissue_offset_applied: number;
  age_acceleration_delta: number | null;
  aging_status: string;
  cpg_locus_contributions: Array<{
    locus: string;
    gene: string;
    methylation_beta: number;
    weight: number;
    contribution_years: number;
  }>;
  model_mode: string;
  model_provenance: string;
  enfsi_statement_en: string;
  enfsi_statement_tr: string;
  enfsi_demographic_category: string;
  prosecutors_fallacy_shield: string;
}

export function computeMahalanobisDistanceSq(betas5: number[]): number {
  const d = betas5.map((b, i) => b - VISAGE_5CPG_CENTROID[i]);
  let dSq = 0;
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 5; j++) {
      dSq += d[i] * VISAGE_XTX_INV_5CPG[i][j] * d[j];
    }
  }
  return Math.max(0, dSq);
}

export function getEnfsiCategory(age: number): string {
  if (age < 15) return "Child / Minor";
  if (age <= 28) return "Young Adult";
  if (age <= 45) return "Adult";
  if (age <= 65) return "Middle-Aged Adult";
  return "Senior / Elderly";
}

export function predictAgeClientSide(
  cpgBetas: Record<string, number>,
  tissueType = "BLOOD",
  knownAge: number | null = null,
  modelMode: "VISAGE_5CPG_ELASTIC_NET" | "VISAGE_5CPG_MLR_POWER" | "EXTENDED_10CPG_CLOCK" = "VISAGE_5CPG_ELASTIC_NET"
): VisagePredictionResult {
  const tissueClean = tissueType.trim().toUpperCase();

  if (modelMode === "VISAGE_5CPG_ELASTIC_NET") {
    const bElovl2 = cpgBetas.cg16867657 ?? 0.25;
    const bFhl2 = cpgBetas.cg06639320 ?? 0.20;
    const bPenk = cpgBetas.cg16419235 ?? 0.30;
    const bTrim59 = cpgBetas.cg04523812 ?? cpgBetas.cg04084157 ?? 0.25;
    const bKlf14 = cpgBetas.cg07955995 ?? cpgBetas.cg08097417 ?? 0.25;

    const betaVec = [bElovl2, bFhl2, bPenk, bTrim59, bKlf14];
    const scoreX = -1.250000 + 2.85 * bElovl2 + 1.92 * bFhl2 + 0.95 * bPenk + 0.88 * bTrim59 + 1.15 * bKlf14;

    const mult = 21.0;
    const y0 = 20.0;
    let modelAge = 0;
    let devStage = "";
    if (scoreX < 0) {
      modelAge = mult * Math.exp(scoreX) - 1.0;
      devStage = "PEDIATRIC (<20 yrs)";
    } else {
      modelAge = mult * scoreX + y0;
      devStage = "ADULT (>=20 yrs)";
    }

    const tInfo = VISAGE_TISSUE_CALIBRATION[tissueClean] || VISAGE_TISSUE_CALIBRATION.BLOOD;
    const deltaTissue = tInfo.deltaYears;
    const finalAge = Math.max(0, modelAge + deltaTissue);

    const dSq = computeMahalanobisDistanceSq(betaVec);
    let sePred = tInfo.sePred;
    let piHalf = 0;
    if (scoreX < 0 && (tissueClean === "BLOOD" || tissueClean === "WHOLE_BLOOD")) {
      sePred = 3.10;
      piHalf = 6.08;
    } else {
      const uMult = Math.sqrt(1.0 + 1.0 / 650.0 + dSq);
      piHalf = 1.96366 * sePred * uMult;
    }

    const piLower = Math.max(0, Number((finalAge - piHalf).toFixed(2)));
    const piUpper = Number((finalAge + piHalf).toFixed(2));

    let category = getEnfsiCategory(finalAge);
    if (tissueClean === "SALIVA" || tissueClean === "BUCCAL" || tissueClean === "SALIVA_BUCCAL") {
      category = "Adult (Buccal Matrix)";
    }
    const categoryTr = ENFSI_CATEGORY_TR[category] || category;

    const deltaAge = knownAge !== null ? Number((finalAge - knownAge).toFixed(2)) : null;
    let agingStatus = "NORMAL_AGING";
    if (deltaAge !== null) {
      if (deltaAge > 5) agingStatus = "ACCELERATED_BIOLOGICAL_AGING";
      else if (deltaAge < -5) agingStatus = "DECELERATED_BIOLOGICAL_AGING";
    }

    const contributions = [
      { locus: "cg16867657", gene: "ELOVL2", methylation_beta: Number(bElovl2.toFixed(4)), weight: 2.85, contribution_years: Number((2.85 * bElovl2 * mult).toFixed(2)) },
      { locus: "cg06639320", gene: "FHL2", methylation_beta: Number(bFhl2.toFixed(4)), weight: 1.92, contribution_years: Number((1.92 * bFhl2 * mult).toFixed(2)) },
      { locus: "cg16419235", gene: "PENK", methylation_beta: Number(bPenk.toFixed(4)), weight: 0.95, contribution_years: Number((0.95 * bPenk * mult).toFixed(2)) },
      { locus: "cg04523812", gene: "TRIM59", methylation_beta: Number(bTrim59.toFixed(4)), weight: 0.88, contribution_years: Number((0.88 * bTrim59 * mult).toFixed(2)) },
      { locus: "cg07955995", gene: "KLF14", methylation_beta: Number(bKlf14.toFixed(4)), weight: 1.15, contribution_years: Number((1.15 * bKlf14 * mult).toFixed(2)) },
    ];

    return {
      estimated_age_years: Number(finalAge.toFixed(2)),
      model_age_before_offset: Number(modelAge.toFixed(2)),
      linear_predictor_x: Number(scoreX.toFixed(4)),
      developmental_stage: devStage,
      prediction_interval_lower: piLower,
      prediction_interval_upper: piUpper,
      standard_error_years: Number(sePred.toFixed(2)),
      expanded_uncertainty_95: Number(piHalf.toFixed(2)),
      mahalanobis_distance_squared: Number(dSq.toFixed(6)),
      tissue_type: tissueClean,
      tissue_offset_applied: deltaTissue,
      age_acceleration_delta: deltaAge,
      aging_status: agingStatus,
      cpg_locus_contributions: contributions,
      model_mode: "VISAGE_5CPG_ELASTIC_NET",
      model_provenance: "VISAGE 5-CpG Elastic Net Piecewise Log-Linear Epigenetic Age Clock (Horvath Link)",
      enfsi_statement_en: `The DNA methylation profile (${tissueClean}) indicates a predicted chronological age of ${finalAge.toFixed(2)} years (95% PI: ${piLower.toFixed(2)} to ${piUpper.toFixed(2)} years). The physical evidence strongly supports the proposition that the donor belonged to the ${category} demographic group.`,
      enfsi_statement_tr: `DNA metilasyon profili (${tissueClean}), ${finalAge.toFixed(2)} yıllık bir tahmini kronolojik yaşa işaret etmektedir (%95 GB: ${piLower.toFixed(2)} ila ${piUpper.toFixed(2)} yıl). Elde edilen deliller, vericinin ${categoryTr} demografik grubunda yer aldığı hipotezini güçlü bir şekilde desteklemektedir.`,
      enfsi_demographic_category: category,
      prosecutors_fallacy_shield: "IMPORTANT (Forensic Epigenetics Legal Shield): Epigenetic DNA methylation age estimates reflect biological and chronological aging trajectories subject to multi-tissue variance (MAE ±3.15 to 3.68 years). Predictions must always be presented with the 95% prediction interval (ISO/IEC 17025:2017) and must NOT be interpreted as exact date-of-birth determinations.",
    };
  }

  if (modelMode === "VISAGE_5CPG_MLR_POWER") {
    const bElovl2 = cpgBetas.cg16867657 ?? 0.25;
    const bFhl2 = cpgBetas.cg06639320 ?? 0.20;
    const bPenk = cpgBetas.cg16419235 ?? 0.30;
    const bTrim59 = cpgBetas.cg04523812 ?? cpgBetas.cg04084157 ?? 0.25;
    const bKlf14 = cpgBetas.cg07955995 ?? cpgBetas.cg08097417 ?? 0.25;

    const elovl2Pow = Math.pow(bElovl2, 2.366);
    const rawAge = -14.2815 + 120.3520 * elovl2Pow + 38.2140 * bFhl2 + 21.8040 * bPenk + 18.9410 * bTrim59 + 26.1030 * bKlf14;
    const tInfo = VISAGE_TISSUE_CALIBRATION[tissueClean] || VISAGE_TISSUE_CALIBRATION.BLOOD;
    const deltaTissue = tInfo.deltaYears;
    const finalAge = Math.max(0, rawAge + deltaTissue);
    const piBound = tInfo.pi95Bound;
    const piLower = Math.max(0, Number((finalAge - piBound).toFixed(2)));
    const piUpper = Number((finalAge + piBound).toFixed(2));
    const category = getEnfsiCategory(finalAge);
    const categoryTr = ENFSI_CATEGORY_TR[category] || category;

    return {
      estimated_age_years: Number(finalAge.toFixed(2)),
      model_age_before_offset: Number(rawAge.toFixed(2)),
      linear_predictor_x: Number(rawAge.toFixed(4)),
      developmental_stage: finalAge >= 20 ? "ADULT (>=20 yrs)" : "PEDIATRIC (<20 yrs)",
      prediction_interval_lower: piLower,
      prediction_interval_upper: piUpper,
      standard_error_years: tInfo.sePred,
      expanded_uncertainty_95: piBound,
      mahalanobis_distance_squared: 0,
      tissue_type: tissueClean,
      tissue_offset_applied: deltaTissue,
      age_acceleration_delta: knownAge !== null ? Number((finalAge - knownAge).toFixed(2)) : null,
      aging_status: "NORMAL_AGING",
      cpg_locus_contributions: [
        { locus: "cg16867657", gene: "ELOVL2 (Power 2.366)", methylation_beta: Number(bElovl2.toFixed(4)), weight: 120.3520, contribution_years: Number((120.3520 * elovl2Pow).toFixed(2)) },
        { locus: "cg06639320", gene: "FHL2", methylation_beta: Number(bFhl2.toFixed(4)), weight: 38.2140, contribution_years: Number((38.2140 * bFhl2).toFixed(2)) },
        { locus: "cg16419235", gene: "PENK", methylation_beta: Number(bPenk.toFixed(4)), weight: 21.8040, contribution_years: Number((21.8040 * bPenk).toFixed(2)) },
        { locus: "cg04523812", gene: "TRIM59", methylation_beta: Number(bTrim59.toFixed(4)), weight: 18.9410, contribution_years: Number((18.9410 * bTrim59).toFixed(2)) },
        { locus: "cg07955995", gene: "KLF14", methylation_beta: Number(bKlf14.toFixed(4)), weight: 26.1030, contribution_years: Number((26.1030 * bKlf14).toFixed(2)) },
      ],
      model_mode: "VISAGE_5CPG_MLR_POWER",
      model_provenance: "VISAGE 5-CpG Direct MLR Model with ELOVL2 Power Transformation (Zbieć-Piekarska et al.)",
      enfsi_statement_en: `The DNA methylation profile (${tissueClean}) indicates a predicted chronological age of ${finalAge.toFixed(2)} years (95% PI: ${piLower.toFixed(2)} to ${piUpper.toFixed(2)} years). The physical evidence strongly supports the proposition that the donor belonged to the ${category} demographic group.`,
      enfsi_statement_tr: `DNA metilasyon profili (${tissueClean}), ${finalAge.toFixed(2)} yıllık bir tahmini kronolojik yaşa işaret etmektedir (%95 GB: ${piLower.toFixed(2)} ila ${piUpper.toFixed(2)} yıl). Elde edilen deliller, vericinin ${categoryTr} demografik grubunda yer aldığı hipotezini güçlü bir şekilde desteklemektedir.`,
      enfsi_demographic_category: category,
      prosecutors_fallacy_shield: "IMPORTANT (Forensic Epigenetics Legal Shield): Direct MLR age estimates reflect standard linear regression calibrated for blood traces (MAE ±3.15 years). Results must be interpreted with ISO 17025 prediction bounds.",
    };
  }

  // EXTENDED_10CPG_CLOCK
  const legacyOffsets: Record<string, { intercept: number; offset: number; ci95: number }> = {
    BLOOD: { intercept: -0.6542, offset: 0.00, ci95: 7.64 },
    SALIVA: { intercept: -0.6137, offset: 0.85, ci95: 8.62 },
    BUCCAL: { intercept: -0.6137, offset: 0.85, ci95: 8.62 },
    SEMEN: { intercept: -0.8541, offset: -4.20, ci95: 8.23 },
    BONE: { intercept: -0.6018, offset: 1.10, ci95: 8.04 },
  };
  const lInfo = legacyOffsets[tissueClean] || legacyOffsets.BLOOD;
  let weightedSum = 0;
  const contributions = Object.entries(EXTENDED_10CPG_MARKERS).map(([cgid, meta]) => {
    const beta = cpgBetas[cgid] ?? meta.defaultBeta;
    const contrib = meta.legacyWeight * beta;
    weightedSum += contrib;
    return {
      locus: cgid,
      gene: meta.gene,
      methylation_beta: Number(beta.toFixed(4)),
      weight: meta.legacyWeight,
      contribution_years: Number(contrib.toFixed(2)),
    };
  });

  const linearX = lInfo.intercept + weightedSum / 100.0;
  let modelAge = 0;
  let devStage = "";
  if (linearX < 0) {
    modelAge = 21.0 * Math.exp(linearX) - 1.0;
    devStage = "PEDIATRIC (<20 yrs)";
  } else {
    modelAge = 21.0 * linearX + 20.0;
    devStage = "ADULT (>=20 yrs)";
  }
  const finalAge = Math.max(0, modelAge + lInfo.offset);
  const piLower = Math.max(0, Number((finalAge - lInfo.ci95).toFixed(1)));
  const piUpper = Number((finalAge + lInfo.ci95).toFixed(1));
  const category = getEnfsiCategory(finalAge);
  const categoryTr = ENFSI_CATEGORY_TR[category] || category;

  return {
    estimated_age_years: Number(finalAge.toFixed(1)),
    model_age_before_offset: Number(modelAge.toFixed(1)),
    linear_predictor_x: Number(linearX.toFixed(4)),
    developmental_stage: devStage,
    prediction_interval_lower: piLower,
    prediction_interval_upper: piUpper,
    standard_error_years: 3.9,
    expanded_uncertainty_95: lInfo.ci95,
    mahalanobis_distance_squared: 0,
    tissue_type: tissueClean,
    tissue_offset_applied: lInfo.offset,
    age_acceleration_delta: knownAge !== null ? Number((finalAge - knownAge).toFixed(1)) : null,
    aging_status: "NORMAL_AGING",
    cpg_locus_contributions: contributions,
    model_mode: "EXTENDED_10CPG_CLOCK",
    model_provenance: "Horvath / VISAGE Multi-Tissue Elastic Net Epigenetic Clock (10-CpG Standard)",
    enfsi_statement_en: `The DNA methylation profile (${tissueClean}) indicates a predicted chronological age of ${finalAge.toFixed(1)} years (95% PI: ${piLower.toFixed(1)} to ${piUpper.toFixed(1)} years). The physical evidence strongly supports the proposition that the donor belonged to the ${category} demographic group.`,
    enfsi_statement_tr: `DNA metilasyon profili (${tissueClean}), ${finalAge.toFixed(1)} yıllık bir tahmini kronolojik yaşa işaret etmektedir (%95 GB: ${piLower.toFixed(1)} ila ${piUpper.toFixed(1)} yıl). Elde edilen deliller, vericinin ${categoryTr} demografik grubunda yer aldığı hipotezini güçlü bir şekilde desteklemektedir.`,
    enfsi_demographic_category: category,
    prosecutors_fallacy_shield: "IMPORTANT (Forensic Epigenetics Legal Shield): Epigenetic DNA methylation age estimates reflect biological and chronological aging trajectories subject to multi-tissue variance. Predictions must always be presented with the 95% prediction interval (ISO/IEC 17025:2017).",
  };
}

export interface VisagePreset {
  id: string;
  name: string;
  tissue: string;
  modelMode: "VISAGE_5CPG_ELASTIC_NET" | "VISAGE_5CPG_MLR_POWER" | "EXTENDED_10CPG_CLOCK";
  knownAge: number;
  betas: Record<string, number>;
}

export const VISAGE_PRESETS: VisagePreset[] = [
  {
    id: "VECTOR_VISAGE_01",
    name: "VECTOR_VISAGE_01 (Pediatric Sample, Age 8.09 yrs)",
    tissue: "BLOOD",
    modelMode: "VISAGE_5CPG_ELASTIC_NET" as const,
    knownAge: 8.0,
    betas: {
      cg16867657: 0.050,
      cg06639320: 0.080,
      cg16419235: 0.040,
      cg04523812: 0.050,
      cg07955995: 0.030,
    },
  },
  {
    id: "VECTOR_VISAGE_02",
    name: "VECTOR_VISAGE_02 (Young Adult Dried Bloodstain, Age 22.71 yrs)",
    tissue: "BLOOD",
    modelMode: "VISAGE_5CPG_ELASTIC_NET" as const,
    knownAge: 22.5,
    betas: {
      cg16867657: 0.200,
      cg06639320: 0.190,
      cg16419235: 0.150,
      cg04523812: 0.160,
      cg07955995: 0.140,
    },
  },
  {
    id: "VECTOR_VISAGE_03",
    name: "VECTOR_VISAGE_03 (Middle-Aged Adult Blood, Age 53.25 yrs)",
    tissue: "BLOOD",
    modelMode: "VISAGE_5CPG_ELASTIC_NET" as const,
    knownAge: 53.0,
    betas: {
      cg16867657: 0.420,
      cg06639320: 0.380,
      cg16419235: 0.310,
      cg04523812: 0.330,
      cg07955995: 0.280,
    },
  },
  {
    id: "VECTOR_VISAGE_04",
    name: "VECTOR_VISAGE_04 (Elderly Adult Blood, Age 94.35 yrs)",
    tissue: "BLOOD",
    modelMode: "VISAGE_5CPG_ELASTIC_NET" as const,
    knownAge: 90.0,
    betas: {
      cg16867657: 0.720,
      cg06639320: 0.620,
      cg16419235: 0.530,
      cg04523812: 0.560,
      cg07955995: 0.480,
    },
  },
  {
    id: "VECTOR_VISAGE_05",
    name: "VECTOR_VISAGE_05 (Oral Epithelial Buccal Swab, Age 35.68 yrs)",
    tissue: "SALIVA_BUCCAL",
    modelMode: "VISAGE_5CPG_ELASTIC_NET" as const,
    knownAge: 35.0,
    betas: {
      cg16867657: 0.280,
      cg06639320: 0.250,
      cg16419235: 0.200,
      cg04523812: 0.220,
      cg07955995: 0.190,
    },
  },
  {
    id: "VECTOR_P4_01",
    name: "VECTOR_P4_01 (Young Adult Blood Donor 10-CpG, Age 25 yrs)",
    tissue: "BLOOD",
    modelMode: "EXTENDED_10CPG_CLOCK" as const,
    knownAge: 25.0,
    betas: {
      cg16867657: 0.22,
      cg21572722: 0.20,
      cg06639320: 0.18,
      cg16419235: 0.35,
      cg04084157: 0.25,
      cg08097417: 0.22,
      cg09809672: 0.20,
      cg02088308: 0.21,
      cg17861230: 0.22,
      cg02228185: 0.30,
    },
  },
  {
    id: "VECTOR_P4_02",
    name: "VECTOR_P4_02 (Elderly Active Heavy Smoker 10-CpG, Age 68 yrs)",
    tissue: "BLOOD",
    modelMode: "EXTENDED_10CPG_CLOCK" as const,
    knownAge: 68.0,
    betas: {
      cg16867657: 0.74,
      cg21572722: 0.71,
      cg06639320: 0.69,
      cg16419235: 0.20,
      cg04084157: 0.65,
      cg08097417: 0.62,
      cg09809672: 0.58,
      cg02088308: 0.60,
      cg17861230: 0.61,
      cg02228185: 0.15,
    },
  },
];
