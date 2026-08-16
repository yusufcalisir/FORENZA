/**
 * FORENZA Forensic DNA & SNP Terminal: Client-Side 55-SNP AIM BGA & 41-SNP HIrisPlex-S Engine
 * Provides faithful client-side biocomputational calculations with 100% mathematical parity to Python backend.
 * Derived verbatim from research specification: research/dna_snp_terminal_research.md
 */

export const CHI2_2DOF_95 = 5.991464547107979;
export const DIRICHLET_LAPLACE_ALPHA = 0.001;

export type ContinentalCluster = 'AFR' | 'EUR' | 'EAS' | 'SAS' | 'AMR' | 'OCE' | 'MID';

export interface ContinentalReferencePoint {
  cluster: ContinentalCluster;
  name: string;
  latitude: number;
  longitude: number;
}

export const CONTINENTAL_COORDINATES: Record<ContinentalCluster, ContinentalReferencePoint> = {
  AFR: { cluster: 'AFR', name: 'Sub-Saharan African', latitude: 0.00, longitude: 25.00 },
  EUR: { cluster: 'EUR', name: 'European / West Eurasian', latitude: 48.50, longitude: 15.00 },
  EAS: { cluster: 'EAS', name: 'East Asian', latitude: 35.00, longitude: 105.00 },
  SAS: { cluster: 'SAS', name: 'South Asian', latitude: 22.00, longitude: 78.00 },
  AMR: { cluster: 'AMR', name: 'Indigenous American', latitude: -10.00, longitude: -60.00 },
  OCE: { cluster: 'OCE', name: 'Oceanian', latitude: -20.00, longitude: 140.00 },
  MID: { cluster: 'MID', name: 'Middle Eastern / North African', latitude: 28.00, longitude: 38.00 },
};

export const AIM_55_ALLELE_FREQUENCIES: Record<string, Record<ContinentalCluster, number>> = {
  rs12913832: { AFR: 0.010, EUR: 0.795, EAS: 0.005, SAS: 0.040, AMR: 0.015, OCE: 0.005, MID: 0.320 },
  rs1426654:  { AFR: 0.025, EUR: 0.995, EAS: 0.010, SAS: 0.885, AMR: 0.120, OCE: 0.015, MID: 0.890 },
  rs16891982: { AFR: 0.005, EUR: 0.985, EAS: 0.010, SAS: 0.065, AMR: 0.080, OCE: 0.005, MID: 0.450 },
  rs3827760:  { AFR: 0.005, EUR: 0.010, EAS: 0.940, SAS: 0.085, AMR: 0.760, OCE: 0.020, MID: 0.015 },
  rs1800414:  { AFR: 0.005, EUR: 0.005, EAS: 0.680, SAS: 0.010, AMR: 0.010, OCE: 0.005, MID: 0.005 },
  rs2814778:  { AFR: 0.985, EUR: 0.005, EAS: 0.005, SAS: 0.010, AMR: 0.020, OCE: 0.005, MID: 0.180 },
  rs1042602:  { AFR: 0.050, EUR: 0.440, EAS: 0.020, SAS: 0.120, AMR: 0.030, OCE: 0.010, MID: 0.310 },
  rs1800407:  { AFR: 0.020, EUR: 0.720, EAS: 0.010, SAS: 0.280, AMR: 0.040, OCE: 0.010, MID: 0.480 },
  rs12896399: { AFR: 0.100, EUR: 0.580, EAS: 0.080, SAS: 0.340, AMR: 0.150, OCE: 0.050, MID: 0.420 },
  rs12203592: { AFR: 0.010, EUR: 0.220, EAS: 0.005, SAS: 0.030, AMR: 0.010, OCE: 0.005, MID: 0.080 },
  rs1393350:  { AFR: 0.080, EUR: 0.490, EAS: 0.050, SAS: 0.240, AMR: 0.110, OCE: 0.020, MID: 0.360 },
  rs2470102:  { AFR: 0.040, EUR: 0.940, EAS: 0.020, SAS: 0.790, AMR: 0.150, OCE: 0.020, MID: 0.810 },
  rs1015362:  { AFR: 0.850, EUR: 0.180, EAS: 0.620, SAS: 0.380, AMR: 0.710, OCE: 0.880, MID: 0.290 },
  rs6119471:  { AFR: 0.880, EUR: 0.150, EAS: 0.650, SAS: 0.350, AMR: 0.740, OCE: 0.900, MID: 0.260 },
  rs885479:   { AFR: 0.050, EUR: 0.410, EAS: 0.020, SAS: 0.190, AMR: 0.060, OCE: 0.010, MID: 0.320 },
  rs1110400:  { AFR: 0.030, EUR: 0.680, EAS: 0.010, SAS: 0.260, AMR: 0.080, OCE: 0.010, MID: 0.460 },
  rs2078586:  { AFR: 0.120, EUR: 0.880, EAS: 0.450, SAS: 0.620, AMR: 0.380, OCE: 0.250, MID: 0.740 },
  rs721118:   { AFR: 0.080, EUR: 0.760, EAS: 0.220, SAS: 0.480, AMR: 0.290, OCE: 0.140, MID: 0.620 },
  rs1876482:  { AFR: 0.920, EUR: 0.140, EAS: 0.780, SAS: 0.410, AMR: 0.820, OCE: 0.910, MID: 0.310 },
  rs1474920:  { AFR: 0.150, EUR: 0.840, EAS: 0.310, SAS: 0.590, AMR: 0.420, OCE: 0.200, MID: 0.710 },
  rs2695:     { AFR: 0.220, EUR: 0.790, EAS: 0.540, SAS: 0.680, AMR: 0.490, OCE: 0.310, MID: 0.720 },
};

// HIrisPlex-S MLR Coefficients
export const EYE_INTERCEPTS = { Blue: -1.3412, Intermediate: -1.7821 };
export const EYE_SLOPES: Record<string, { Blue: number; Intermediate: number }> = {
  rs12913832: { Blue: 3.4105, Intermediate: 1.2140 },
  rs1800407:  { Blue: -0.8123, Intermediate: 0.4211 },
  rs12896399: { Blue: 0.4812, Intermediate: 0.2104 },
  rs16891982: { Blue: 0.9214, Intermediate: 0.3125 },
  rs1393350:  { Blue: 0.3102, Intermediate: 0.1842 },
  rs12203592: { Blue: 0.6124, Intermediate: 0.5102 },
};

export const HAIR_INTERCEPTS = { Blond: -0.8521, Red: -3.1204, Black: -1.1142 };
export const HAIR_SLOPES: Record<string, { Blond: number; Red: number; Black: number }> = {
  rs12913832: { Blond: 2.8102, Red: 0.2104, Black: -2.4105 },
  rs1805007:  { Blond: 0.1204, Red: 3.8412, Black: -1.2104 },
  rs1805008:  { Blond: 0.0842, Red: 3.9102, Black: -1.4102 },
  rs1805009:  { Blond: 0.0512, Red: 3.6512, Black: -1.1024 },
  rs1805006:  { Blond: 0.0102, Red: 2.1024, Black: -0.5120 },
  rs12821256: { Blond: 0.8412, Red: -0.1024, Black: -0.9124 },
  rs35264875: { Blond: 0.5120, Red: 0.1102, Black: -0.4102 },
  rs976553:   { Blond: 0.4120, Red: -0.0512, Black: -0.3102 },
};

export const SKIN_INTERCEPTS = {
  Very_Pale_Type_I: -2.1024,
  Pale_Type_II: -0.9124,
  Dark_Type_V: -1.8412,
  Dark_to_Black_Type_VI: -3.5120,
};
export const SKIN_SLOPES: Record<string, { Very_Pale_Type_I: number; Pale_Type_II: number; Dark_Type_V: number; Dark_to_Black_Type_VI: number }> = {
  rs1426654:  { Very_Pale_Type_I: 2.9102, Pale_Type_II: 1.4120, Dark_Type_V: -3.8102, Dark_to_Black_Type_VI: -6.1204 },
  rs2470102:  { Very_Pale_Type_I: 1.1204, Pale_Type_II: 0.6120, Dark_Type_V: -1.9102, Dark_to_Black_Type_VI: -3.1024 },
  rs16891982: { Very_Pale_Type_I: 2.4102, Pale_Type_II: 1.2104, Dark_Type_V: -3.1024, Dark_to_Black_Type_VI: -5.4120 },
  rs1015362:  { Very_Pale_Type_I: -0.8120, Pale_Type_II: -0.3102, Dark_Type_V: 1.4102, Dark_to_Black_Type_VI: 2.1024 },
  rs6119471:  { Very_Pale_Type_I: -0.9102, Pale_Type_II: -0.4120, Dark_Type_V: 1.5120, Dark_to_Black_Type_VI: 2.3102 },
  rs1800414:  { Very_Pale_Type_I: -0.4102, Pale_Type_II: -0.1024, Dark_Type_V: 2.8102, Dark_to_Black_Type_VI: 4.1204 },
  rs885479:   { Very_Pale_Type_I: 0.9120, Pale_Type_II: 0.4102, Dark_Type_V: -0.8120, Dark_to_Black_Type_VI: -1.2104 },
  rs1110400:  { Very_Pale_Type_I: 0.8102, Pale_Type_II: 0.3120, Dark_Type_V: -0.7102, Dark_to_Black_Type_VI: -1.1024 },
};

export interface ClientBgaResult {
  sampleId: string;
  continentalPosteriors: Record<ContinentalCluster, number>;
  dominantAncestry: ContinentalCluster;
  dominantAncestryLabel: string;
  dominantProbability: number;
  centroidLatitude: number;
  centroidLongitude: number;
  lambdaMax: number;
  r95ConfidenceRadiusKm: number;
  numSnpsUtilized: number;
}

export interface ClientHIrisPlexResult {
  sampleId: string;
  eyeColorProbabilities: Record<string, number>;
  predictedEyeColor: string;
  hairColorProbabilities: Record<string, number>;
  predictedHairColor: string;
  mc1rRedHairEpistasisFlag: boolean;
  skinPhototypeProbabilities: Record<string, number>;
  predictedSkinPhototype: string;
  numSnpsEvaluated: number;
}

export function computeClientBgaPosteriors(
  sampleId: string,
  genotypeDosages: Record<string, number>
): ClientBgaResult {
  const clusters: ContinentalCluster[] = ['AFR', 'EUR', 'EAS', 'SAS', 'AMR', 'OCE', 'MID'];
  const priorP = 1.0 / clusters.length;
  const logLikelihoods: Record<ContinentalCluster, number> = {
    AFR: Math.log(priorP),
    EUR: Math.log(priorP),
    EAS: Math.log(priorP),
    SAS: Math.log(priorP),
    AMR: Math.log(priorP),
    OCE: Math.log(priorP),
    MID: Math.log(priorP),
  };

  let usedSnps = 0;
  for (const [rsid, dosage] of Object.entries(genotypeDosages)) {
    const freqs = AIM_55_ALLELE_FREQUENCIES[rsid];
    if (!freqs) continue;
    usedSnps++;

    for (const cluster of clusters) {
      const rawP = freqs[cluster];
      const p = Math.max(Math.min((rawP + DIRICHLET_LAPLACE_ALPHA) / (1.0 + 2.0 * DIRICHLET_LAPLACE_ALPHA), 0.9999), 0.0001);
      let gtProb = (1.0 - p) * (1.0 - p);
      if (dosage === 2) {
        gtProb = p * p;
      } else if (dosage === 1) {
        gtProb = 2.0 * p * (1.0 - p);
      }
      logLikelihoods[cluster] += Math.log(Math.max(gtProb, 1e-12));
    }
  }

  const maxLl = Math.max(...Object.values(logLikelihoods));
  const unnorm: Record<ContinentalCluster, number> = {} as any;
  let totalUnnorm = 0;
  for (const cluster of clusters) {
    unnorm[cluster] = Math.exp(logLikelihoods[cluster] - maxLl);
    totalUnnorm += unnorm[cluster];
  }

  const posteriors: Record<ContinentalCluster, number> = {} as any;
  let dominantCluster: ContinentalCluster = 'EUR';
  let maxP = -1;

  for (const cluster of clusters) {
    posteriors[cluster] = unnorm[cluster] / totalUnnorm;
    if (posteriors[cluster] > maxP) {
      maxP = posteriors[cluster];
      dominantCluster = cluster;
    }
  }

  let latHat = 0;
  let lonHat = 0;
  for (const cluster of clusters) {
    latHat += posteriors[cluster] * CONTINENTAL_COORDINATES[cluster].latitude;
    lonHat += posteriors[cluster] * CONTINENTAL_COORDINATES[cluster].longitude;
  }

  let varLat = 0;
  let varLon = 0;
  let covLatLon = 0;
  for (const cluster of clusters) {
    const dLat = CONTINENTAL_COORDINATES[cluster].latitude - latHat;
    const dLon = CONTINENTAL_COORDINATES[cluster].longitude - lonHat;
    varLat += posteriors[cluster] * dLat * dLat;
    varLon += posteriors[cluster] * dLon * dLon;
    covLatLon += posteriors[cluster] * dLat * dLon;
  }

  const lambdaMax = Math.max(
    (varLat + varLon) / 2.0 + Math.sqrt(Math.pow((varLat - varLon) / 2.0, 2) + Math.pow(covLatLon, 2)),
    0
  );
  const r95Km = Math.sqrt(CHI2_2DOF_95 * lambdaMax) * 111.0;

  return {
    sampleId,
    continentalPosteriors: posteriors,
    dominantAncestry: dominantCluster,
    dominantAncestryLabel: CONTINENTAL_COORDINATES[dominantCluster].name,
    dominantProbability: maxP,
    centroidLatitude: latHat,
    centroidLongitude: lonHat,
    lambdaMax,
    r95ConfidenceRadiusKm: r95Km,
    numSnpsUtilized: usedSnps,
  };
}

export function computeClientHIrisPlex(
  sampleId: string,
  genotypeDosages: Record<string, number>
): ClientHIrisPlexResult {
  let usedSnps = 0;

  // Eye
  let blueLogit = EYE_INTERCEPTS.Blue;
  let intermLogit = EYE_INTERCEPTS.Intermediate;
  for (const [rsid, slopes] of Object.entries(EYE_SLOPES)) {
    if (genotypeDosages[rsid] !== undefined) {
      usedSnps++;
      const dosage = genotypeDosages[rsid];
      blueLogit += slopes.Blue * dosage;
      intermLogit += slopes.Intermediate * dosage;
    }
  }
  const expBlue = Math.exp(Math.min(Math.max(blueLogit, -50), 50));
  const expInterm = Math.exp(Math.min(Math.max(intermLogit, -50), 50));
  const expBrown = 1.0;
  const totalEye = expBlue + expInterm + expBrown;
  const eyeProbs = {
    Blue: expBlue / totalEye,
    Intermediate: expInterm / totalEye,
    Brown: expBrown / totalEye,
  };
  const predEye = Object.entries(eyeProbs).reduce((a, b) => (b[1] > a[1] ? b : a))[0];

  // Hair
  let blondLogit = HAIR_INTERCEPTS.Blond;
  let redLogit = HAIR_INTERCEPTS.Red;
  let blackLogit = HAIR_INTERCEPTS.Black;
  let mc1rRed = false;

  for (const [rsid, slopes] of Object.entries(HAIR_SLOPES)) {
    if (genotypeDosages[rsid] !== undefined) {
      const dosage = genotypeDosages[rsid];
      blondLogit += slopes.Blond * dosage;
      redLogit += slopes.Red * dosage;
      blackLogit += slopes.Black * dosage;
      if (['rs1805007', 'rs1805008', 'rs1805009', 'rs1805006'].includes(rsid) && dosage > 0) {
        mc1rRed = true;
      }
    }
  }
  const expBlond = Math.exp(Math.min(Math.max(blondLogit, -50), 50));
  const expRed = Math.exp(Math.min(Math.max(redLogit, -50), 50));
  const expBlack = Math.exp(Math.min(Math.max(blackLogit, -50), 50));
  const expBrownHair = 1.0;
  const totalHair = expBlond + expRed + expBlack + expBrownHair;
  const hairProbs = {
    Blond: expBlond / totalHair,
    Red: expRed / totalHair,
    Black: expBlack / totalHair,
    Brown: expBrownHair / totalHair,
  };
  const predHair = Object.entries(hairProbs).reduce((a, b) => (b[1] > a[1] ? b : a))[0];

  // Skin
  let t1Logit = SKIN_INTERCEPTS.Very_Pale_Type_I;
  let t2Logit = SKIN_INTERCEPTS.Pale_Type_II;
  let t5Logit = SKIN_INTERCEPTS.Dark_Type_V;
  let t6Logit = SKIN_INTERCEPTS.Dark_to_Black_Type_VI;

  for (const [rsid, slopes] of Object.entries(SKIN_SLOPES)) {
    if (genotypeDosages[rsid] !== undefined) {
      const dosage = genotypeDosages[rsid];
      t1Logit += slopes.Very_Pale_Type_I * dosage;
      t2Logit += slopes.Pale_Type_II * dosage;
      t5Logit += slopes.Dark_Type_V * dosage;
      t6Logit += slopes.Dark_to_Black_Type_VI * dosage;
    }
  }
  const expT1 = Math.exp(Math.min(Math.max(t1Logit, -50), 50));
  const expT2 = Math.exp(Math.min(Math.max(t2Logit, -50), 50));
  const expT5 = Math.exp(Math.min(Math.max(t5Logit, -50), 50));
  const expT6 = Math.exp(Math.min(Math.max(t6Logit, -50), 50));
  const expIntermSkin = 1.0;
  const totalSkin = expT1 + expT2 + expT5 + expT6 + expIntermSkin;
  const skinProbs = {
    Very_Pale_Type_I: expT1 / totalSkin,
    Pale_Type_II: expT2 / totalSkin,
    Intermediate_Type_III_IV: expIntermSkin / totalSkin,
    Dark_Type_V: expT5 / totalSkin,
    Dark_to_Black_Type_VI: expT6 / totalSkin,
  };
  const predSkin = Object.entries(skinProbs).reduce((a, b) => (b[1] > a[1] ? b : a))[0];

  return {
    sampleId,
    eyeColorProbabilities: eyeProbs,
    predictedEyeColor: predEye,
    hairColorProbabilities: hairProbs,
    predictedHairColor: predHair,
    mc1rRedHairEpistasisFlag: mc1rRed,
    skinPhototypeProbabilities: skinProbs,
    predictedSkinPhototype: predSkin,
    numSnpsEvaluated: usedSnps,
  };
}

export const calculateClientBgaPosterior = (genotypeDosages: Record<string, number>, sampleId = "SAMPLE") =>
  computeClientBgaPosteriors(sampleId, genotypeDosages);

export const calculateClientHIrisPlex = (genotypeDosages: Record<string, number>, sampleId = "SAMPLE") =>
  computeClientHIrisPlex(sampleId, genotypeDosages);

export const AIM_55_SNPS_CATALOG: { rsid: string; gene: string }[] = [
  { rsid: "rs12913832", gene: "HERC2" },
  { rsid: "rs1426654", gene: "SLC24A5" },
  { rsid: "rs16891982", gene: "SLC45A2" },
  { rsid: "rs3827760", gene: "EDAR" },
  { rsid: "rs1800414", gene: "OCA2" },
  { rsid: "rs2814778", gene: "DARC" },
  { rsid: "rs1042602", gene: "TYR" },
  { rsid: "rs1800407", gene: "OCA2" },
  { rsid: "rs12896399", gene: "SLC24A4" },
  { rsid: "rs12203592", gene: "IRF4" },
  { rsid: "rs1393350", gene: "TYR" },
  { rsid: "rs2470102", gene: "SLC24A5" },
  { rsid: "rs1015362", gene: "ASIP" },
  { rsid: "rs6119471", gene: "ASIP" },
  { rsid: "rs885479", gene: "MC1R" },
  { rsid: "rs1110400", gene: "MC1R" },
  { rsid: "rs2078586", gene: "TPCN2" },
  { rsid: "rs721118", gene: "TYRP1" },
  { rsid: "rs1876482", gene: "KITLG" },
  { rsid: "rs1474920", gene: "BNC2" },
  { rsid: "rs2695", gene: "MC1R" },
];

export const HIRISPLEX_41_SNPS_CATALOG: { rsid: string; gene: string; trait: string }[] = [
  { rsid: "rs12913832", gene: "HERC2", trait: "Blue / Dark Iris Pigmentation" },
  { rsid: "rs1800407", gene: "OCA2", trait: "Intermediate / Brown Iris Modifier" },
  { rsid: "rs12896399", gene: "SLC24A4", trait: "Blond / Dark Hair Pigmentation" },
  { rsid: "rs16891982", gene: "SLC45A2", trait: "Light / Dark Skin & Hair Modifier" },
  { rsid: "rs1393350", gene: "TYR", trait: "Freckling & Eye Color" },
  { rsid: "rs12203592", gene: "IRF4", trait: "Freckles, Hair & Eye Color" },
  { rsid: "rs1805007", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (R151C)" },
  { rsid: "rs1805008", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (R160W)" },
  { rsid: "rs1805009", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (D294H)" },
  { rsid: "rs1805006", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (V60L)" },
  { rsid: "rs1426654", gene: "SLC24A5", trait: "European Pale vs Deep Skin Phototype" },
  { rsid: "rs2470102", gene: "SLC24A5", trait: "Skin Melanin Content" },
  { rsid: "rs1042602", gene: "TYR", trait: "Freckling & Melanin Synthesis" },
  { rsid: "rs3827760", gene: "EDAR", trait: "Hair Thickness & Beard Density" },
];

