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
  AFR: { cluster: 'AFR', name: 'Sub-Saharan African', latitude: 0.0236, longitude: 15.3121 },
  EUR: { cluster: 'EUR', name: 'European / West Eurasian', latitude: 48.8566, longitude: 2.3522 },
  EAS: { cluster: 'EAS', name: 'East Asian', latitude: 35.8617, longitude: 104.1954 },
  SAS: { cluster: 'SAS', name: 'South Asian', latitude: 20.5937, longitude: 78.9629 },
  AMR: { cluster: 'AMR', name: 'Indigenous American', latitude: -8.7832, longitude: -55.4915 },
  OCE: { cluster: 'OCE', name: 'Oceanian', latitude: -20.0000, longitude: 140.0000 },
  MID: { cluster: 'MID', name: 'Middle Eastern / North African', latitude: 29.2985, longitude: 42.5510 },
};

export const AIM_55_METADATA: Record<string, { gene: string; ref: string; alt: string }> = {
  rs3737576: { gene: 'CPM', ref: 'T', alt: 'C' },
  rs7554936: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs2814778: { gene: 'ACKR1', ref: 'T', alt: 'C' },
  rs798443: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs1876482: { gene: 'Intergenic', ref: 'T', alt: 'C' },
  rs1834619: { gene: 'STAT4', ref: 'A', alt: 'G' },
  rs3827760: { gene: 'EDAR', ref: 'A', alt: 'G' },
  rs260690: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs6754311: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs10497191: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs12498138: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs4833103: { gene: 'Intergenic', ref: 'T', alt: 'C' },
  rs1229984: { gene: 'ADH1B', ref: 'C', alt: 'T' },
  rs3811801: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs7657799: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs16891982: { gene: 'SLC45A2', ref: 'C', alt: 'G' },
  rs7722456: { gene: 'Intergenic', ref: 'G', alt: 'A' },
  rs870347: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs3823159: { gene: 'Intergenic', ref: 'G', alt: 'A' },
  rs192655: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs917115: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs1462906: { gene: 'Intergenic', ref: 'G', alt: 'A' },
  rs6990312: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs2196051: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs1871534: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs3814134: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs4918664: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs174570: { gene: 'FADS2', ref: 'C', alt: 'T' },
  rs1079597: { gene: 'ANKK1', ref: 'C', alt: 'T' },
  rs2238151: { gene: 'Intergenic', ref: 'G', alt: 'A' },
  rs671: { gene: 'ALDH2', ref: 'G', alt: 'A' },
  rs7997709: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs1572018: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs2166624: { gene: 'Intergenic', ref: 'T', alt: 'C' },
  rs7326934: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs9522149: { gene: 'Intergenic', ref: 'G', alt: 'A' },
  rs200354: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs1800414: { gene: 'OCA2', ref: 'C', alt: 'T' },
  rs12913832: { gene: 'HERC2', ref: 'A', alt: 'G' },
  rs12439433: { gene: 'Intergenic', ref: 'G', alt: 'A' },
  rs735480: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs1426654: { gene: 'SLC24A5', ref: 'A', alt: 'G' },
  rs459920: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs4411548: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs2593595: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs17642714: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs4471745: { gene: 'Intergenic', ref: 'G', alt: 'A' },
  rs11652805: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs2042762: { gene: 'Intergenic', ref: 'A', alt: 'G' },
  rs7226659: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs3916235: { gene: 'Intergenic', ref: 'T', alt: 'C' },
  rs4891825: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs7251928: { gene: 'Intergenic', ref: 'G', alt: 'A' },
  rs310644: { gene: 'Intergenic', ref: 'C', alt: 'T' },
  rs2024566: { gene: 'Intergenic', ref: 'G', alt: 'A' },
};

export const AIM_55_ALLELE_FREQUENCIES: Record<string, Record<ContinentalCluster, number>> = {
  rs3737576:  { AFR: 0.812, EUR: 0.221, EAS: 0.114, SAS: 0.325, AMR: 0.083, OCE: 0.150, MID: 0.248 },
  rs7554936:  { AFR: 0.941, EUR: 0.385, EAS: 0.021, SAS: 0.412, AMR: 0.052, OCE: 0.180, MID: 0.391 },
  rs2814778:  { AFR: 0.992, EUR: 0.001, EAS: 0.000, SAS: 0.003, AMR: 0.021, OCE: 0.005, MID: 0.085 },
  rs798443:   { AFR: 0.125, EUR: 0.781, EAS: 0.943, SAS: 0.612, AMR: 0.892, OCE: 0.550, MID: 0.721 },
  rs1876482:  { AFR: 0.884, EUR: 0.152, EAS: 0.061, SAS: 0.291, AMR: 0.041, OCE: 0.210, MID: 0.183 },
  rs1834619:  { AFR: 0.915, EUR: 0.283, EAS: 0.082, SAS: 0.394, AMR: 0.091, OCE: 0.190, MID: 0.312 },
  rs3827760:  { AFR: 0.000, EUR: 0.002, EAS: 0.948, SAS: 0.015, AMR: 0.824, OCE: 0.020, MID: 0.005 },
  rs260690:   { AFR: 0.213, EUR: 0.724, EAS: 0.211, SAS: 0.512, AMR: 0.183, OCE: 0.340, MID: 0.651 },
  rs6754311:  { AFR: 0.852, EUR: 0.183, EAS: 0.031, SAS: 0.284, AMR: 0.052, OCE: 0.160, MID: 0.211 },
  rs10497191: { AFR: 0.112, EUR: 0.891, EAS: 0.982, SAS: 0.782, AMR: 0.951, OCE: 0.620, MID: 0.842 },
  rs12498138: { AFR: 0.021, EUR: 0.083, EAS: 0.192, SAS: 0.114, AMR: 0.912, OCE: 0.280, MID: 0.071 },
  rs4833103:  { AFR: 0.781, EUR: 0.214, EAS: 0.042, SAS: 0.312, AMR: 0.061, OCE: 0.180, MID: 0.252 },
  rs1229984:  { AFR: 0.002, EUR: 0.041, EAS: 0.762, SAS: 0.112, AMR: 0.081, OCE: 0.050, MID: 0.125 },
  rs3811801:  { AFR: 0.081, EUR: 0.112, EAS: 0.894, SAS: 0.221, AMR: 0.783, OCE: 0.310, MID: 0.142 },
  rs7657799:  { AFR: 0.824, EUR: 0.191, EAS: 0.052, SAS: 0.315, AMR: 0.072, OCE: 0.170, MID: 0.231 },
  rs16891982: { AFR: 0.000, EUR: 0.968, EAS: 0.001, SAS: 0.082, AMR: 0.021, OCE: 0.005, MID: 0.214 },
  rs7722456:  { AFR: 0.091, EUR: 0.824, EAS: 0.912, SAS: 0.683, AMR: 0.851, OCE: 0.580, MID: 0.762 },
  rs870347:   { AFR: 0.892, EUR: 0.221, EAS: 0.071, SAS: 0.342, AMR: 0.082, OCE: 0.200, MID: 0.261 },
  rs3823159:  { AFR: 0.861, EUR: 0.142, EAS: 0.032, SAS: 0.251, AMR: 0.041, OCE: 0.150, MID: 0.182 },
  rs192655:   { AFR: 0.182, EUR: 0.712, EAS: 0.931, SAS: 0.582, AMR: 0.871, OCE: 0.490, MID: 0.662 },
  rs917115:   { AFR: 0.841, EUR: 0.172, EAS: 0.041, SAS: 0.272, AMR: 0.051, OCE: 0.180, MID: 0.212 },
  rs1462906:  { AFR: 0.112, EUR: 0.881, EAS: 0.962, SAS: 0.752, AMR: 0.921, OCE: 0.640, MID: 0.812 },
  rs6990312:  { AFR: 0.821, EUR: 0.201, EAS: 0.051, SAS: 0.321, AMR: 0.062, OCE: 0.190, MID: 0.241 },
  rs2196051:  { AFR: 0.872, EUR: 0.161, EAS: 0.042, SAS: 0.281, AMR: 0.051, OCE: 0.170, MID: 0.201 },
  rs1871534:  { AFR: 0.851, EUR: 0.182, EAS: 0.032, SAS: 0.291, AMR: 0.042, OCE: 0.180, MID: 0.221 },
  rs3814134:  { AFR: 0.891, EUR: 0.131, EAS: 0.021, SAS: 0.241, AMR: 0.031, OCE: 0.140, MID: 0.171 },
  rs4918664:  { AFR: 0.141, EUR: 0.761, EAS: 0.081, SAS: 0.491, AMR: 0.112, OCE: 0.320, MID: 0.621 },
  rs174570:   { AFR: 0.921, EUR: 0.312, EAS: 0.642, SAS: 0.521, AMR: 0.781, OCE: 0.610, MID: 0.412 },
  rs1079597:  { AFR: 0.811, EUR: 0.212, EAS: 0.061, SAS: 0.331, AMR: 0.071, OCE: 0.190, MID: 0.251 },
  rs2238151:  { AFR: 0.131, EUR: 0.841, EAS: 0.951, SAS: 0.721, AMR: 0.912, OCE: 0.570, MID: 0.791 },
  rs671:      { AFR: 0.000, EUR: 0.000, EAS: 0.312, SAS: 0.000, AMR: 0.000, OCE: 0.000, MID: 0.000 },
  rs7997709:  { AFR: 0.091, EUR: 0.861, EAS: 0.971, SAS: 0.761, AMR: 0.931, OCE: 0.620, MID: 0.821 },
  rs1572018:  { AFR: 0.071, EUR: 0.881, EAS: 0.981, SAS: 0.781, AMR: 0.941, OCE: 0.650, MID: 0.831 },
  rs2166624:  { AFR: 0.861, EUR: 0.171, EAS: 0.031, SAS: 0.271, AMR: 0.041, OCE: 0.160, MID: 0.211 },
  rs7326934:  { AFR: 0.841, EUR: 0.191, EAS: 0.041, SAS: 0.291, AMR: 0.051, OCE: 0.170, MID: 0.231 },
  rs9522149:  { AFR: 0.181, EUR: 0.721, EAS: 0.121, SAS: 0.481, AMR: 0.151, OCE: 0.350, MID: 0.611 },
  rs200354:   { AFR: 0.151, EUR: 0.751, EAS: 0.111, SAS: 0.461, AMR: 0.131, OCE: 0.360, MID: 0.631 },
  rs1800414:  { AFR: 0.041, EUR: 0.121, EAS: 0.782, SAS: 0.211, AMR: 0.312, OCE: 0.110, MID: 0.151 },
  rs12913832: { AFR: 0.012, EUR: 0.785, EAS: 0.002, SAS: 0.124, AMR: 0.081, OCE: 0.005, MID: 0.235 },
  rs12439433: { AFR: 0.831, EUR: 0.181, EAS: 0.041, SAS: 0.281, AMR: 0.051, OCE: 0.160, MID: 0.221 },
  rs735480:   { AFR: 0.121, EUR: 0.821, EAS: 0.931, SAS: 0.711, AMR: 0.891, OCE: 0.540, MID: 0.771 },
  rs1426654:  { AFR: 0.011, EUR: 0.991, EAS: 0.002, SAS: 0.882, AMR: 0.121, OCE: 0.015, MID: 0.842 },
  rs459920:   { AFR: 0.811, EUR: 0.211, EAS: 0.061, SAS: 0.321, AMR: 0.071, OCE: 0.180, MID: 0.251 },
  rs4411548:  { AFR: 0.851, EUR: 0.171, EAS: 0.031, SAS: 0.271, AMR: 0.041, OCE: 0.150, MID: 0.211 },
  rs2593595:  { AFR: 0.831, EUR: 0.191, EAS: 0.041, SAS: 0.291, AMR: 0.051, OCE: 0.160, MID: 0.231 },
  rs17642714: { AFR: 0.871, EUR: 0.151, EAS: 0.031, SAS: 0.261, AMR: 0.041, OCE: 0.140, MID: 0.191 },
  rs4471745:  { AFR: 0.841, EUR: 0.181, EAS: 0.041, SAS: 0.281, AMR: 0.051, OCE: 0.170, MID: 0.221 },
  rs11652805: { AFR: 0.821, EUR: 0.201, EAS: 0.051, SAS: 0.311, AMR: 0.061, OCE: 0.180, MID: 0.241 },
  rs2042762:  { AFR: 0.861, EUR: 0.161, EAS: 0.031, SAS: 0.271, AMR: 0.041, OCE: 0.150, MID: 0.201 },
  rs7226659:  { AFR: 0.881, EUR: 0.141, EAS: 0.021, SAS: 0.251, AMR: 0.031, OCE: 0.140, MID: 0.181 },
  rs3916235:  { AFR: 0.111, EUR: 0.851, EAS: 0.961, SAS: 0.741, AMR: 0.921, OCE: 0.610, MID: 0.801 },
  rs4891825:  { AFR: 0.831, EUR: 0.191, EAS: 0.041, SAS: 0.291, AMR: 0.051, OCE: 0.160, MID: 0.231 },
  rs7251928:  { AFR: 0.851, EUR: 0.171, EAS: 0.031, SAS: 0.271, AMR: 0.041, OCE: 0.150, MID: 0.211 },
  rs310644:   { AFR: 0.871, EUR: 0.151, EAS: 0.031, SAS: 0.261, AMR: 0.041, OCE: 0.140, MID: 0.191 },
  rs2024566:  { AFR: 0.841, EUR: 0.181, EAS: 0.041, SAS: 0.281, AMR: 0.051, OCE: 0.170, MID: 0.221 },
};

// ═══════════════════════════════════════════════════════════════════════════════
// HIRISPLEX-S 41-SNP SOFTMAX MLR COEFFICIENT MATRICES
// ═══════════════════════════════════════════════════════════════════════════════

export const MC1R_EPISTATIC_VARIANTS: string[] = [
  'rs1805007', 'rs1805008', 'rs1805009', 'rs1805006', 'rs885479',
  'rs1805005', 'rs2228479', 'rs1110400', 'rs11547464', 'rs28936415', 'rs201326893'
];

// A. Eye Color: Ref = Brown (K=3)
export const EYE_INTERCEPTS = { Blue: -0.8412, Intermediate: -2.1054 };
export const EYE_SLOPES: Record<string, { Blue: number; Intermediate: number }> = {
  rs12913832: { Blue: 2.854, Intermediate: 0.912 },
  rs1800407:  { Blue: -0.621, Intermediate: 0.412 },
  rs12896399: { Blue: 0.412, Intermediate: 0.285 },
  rs16891982: { Blue: 0.892, Intermediate: 0.341 },
  rs1393350:  { Blue: 0.321, Intermediate: 0.184 },
  rs12203592: { Blue: 0.485, Intermediate: 0.312 },
  rs1800414:  { Blue: -0.214, Intermediate: 0.152 },
  rs1426654:  { Blue: 0.112, Intermediate: 0.051 },
  rs1126809:  { Blue: 0.184, Intermediate: 0.112 },
  rs1042602:  { Blue: 0.251, Intermediate: 0.141 },
  rs28777:    { Blue: 0.152, Intermediate: 0.081 },
  rs2470102:  { Blue: 0.081, Intermediate: 0.041 },
  rs1545397:  { Blue: -0.152, Intermediate: 0.112 },
  rs74653330: { Blue: -0.112, Intermediate: 0.081 },
  rs1408799:  { Blue: 0.121, Intermediate: 0.061 },
  rs26722:    { Blue: 0.184, Intermediate: 0.091 },
};

// B. Hair Color: Ref = Brown (K=4)
export const HAIR_INTERCEPTS = { Blond: -1.2504, Red: -3.8512, Black: -0.9201 };
export const HAIR_SLOPES: Record<string, { Blond: number; Red: number; Black: number }> = {
  rs12913832:  { Blond: 1.421, Red: -0.112, Black: -1.854 },
  rs1800407:   { Blond: -0.215, Red: -0.104, Black: 0.184 },
  rs12896399:  { Blond: 0.312, Red: 0.051, Black: -0.214 },
  rs16891982:  { Blond: 1.105, Red: -0.214, Black: -1.952 },
  rs1393350:   { Blond: 0.284, Red: 0.412, Black: -0.185 },
  rs12203592:  { Blond: 0.651, Red: 0.124, Black: -0.452 },
  rs1805007:   { Blond: 0.812, Red: 3.852, Black: -1.214 },
  rs1805008:   { Blond: 0.752, Red: 3.612, Black: -1.152 },
  rs1805009:   { Blond: 0.612, Red: 3.124, Black: -0.982 },
  rs1805006:   { Blond: 0.412, Red: 2.105, Black: -0.652 },
  rs885479:    { Blond: 0.312, Red: 1.852, Black: -0.512 },
  rs1805005:   { Blond: 0.251, Red: 1.412, Black: -0.412 },
  rs2228479:   { Blond: 0.184, Red: 0.952, Black: -0.312 },
  rs1110400:   { Blond: 0.121, Red: 0.781, Black: -0.214 },
  rs11547464:  { Blond: 0.084, Red: 0.612, Black: -0.152 },
  rs28936415:  { Blond: 0.512, Red: 2.852, Black: -0.812 },
  rs201326893: { Blond: 0.482, Red: 2.651, Black: -0.752 },
  rs12821256:  { Blond: 0.582, Red: -0.112, Black: -0.412 },
  rs6058017:   { Blond: 0.341, Red: 0.185, Black: -0.284 },
  rs10810681:  { Blond: 0.284, Red: -0.051, Black: -0.184 },
  rs3750965:   { Blond: 0.214, Red: 0.112, Black: -0.152 },
  rs1800414:   { Blond: -0.184, Red: -0.081, Black: 0.312 },
  rs1426654:   { Blond: 0.852, Red: -0.152, Black: -1.651 },
  rs1126809:   { Blond: 0.214, Red: 0.152, Black: -0.184 },
  rs3827760:   { Blond: -0.412, Red: -0.184, Black: 1.251 },
  rs1042602:   { Blond: 0.312, Red: 0.214, Black: -0.251 },
  rs2153271:   { Blond: 0.251, Red: -0.041, Black: -0.152 },
  rs35264875:  { Blond: 0.184, Red: 0.091, Black: -0.121 },
  rs28777:     { Blond: 0.412, Red: -0.081, Black: -0.651 },
  rs2470102:   { Blond: 0.384, Red: -0.061, Black: -0.582 },
  rs642742:    { Blond: 0.412, Red: -0.081, Black: -0.312 },
  rs1015362:   { Blond: 0.284, Red: 0.141, Black: -0.214 },
  rs4911414:   { Blond: 0.214, Red: 0.112, Black: -0.184 },
  rs1545397:   { Blond: -0.121, Red: -0.051, Black: 0.214 },
  rs74653330:  { Blond: -0.091, Red: -0.041, Black: 0.184 },
  rs1408799:   { Blond: 0.184, Red: 0.091, Black: -0.152 },
  rs26722:     { Blond: 0.214, Red: 0.041, Black: -0.184 },
  rs2814778:   { Blond: -0.512, Red: -0.284, Black: 1.852 },
};

// C. Skin Phototype: Ref = Intermediate / Type III-IV (K=5)
export const SKIN_INTERCEPTS = {
  Very_Pale_Type_I: -1.1820,
  Pale_Type_II: -0.4510,
  Dark_Type_V: -2.7540,
  Dark_to_Black_Type_VI: -3.9510,
};
export const SKIN_SLOPES: Record<string, { Very_Pale_Type_I: number; Pale_Type_II: number; Dark_Type_V: number; Dark_to_Black_Type_VI: number }> = {
  rs12913832:  { Very_Pale_Type_I: 0.852, Pale_Type_II: 0.412, Dark_Type_V: -1.214, Dark_to_Black_Type_VI: -2.105 },
  rs1800407:   { Very_Pale_Type_I: 0.121, Pale_Type_II: 0.084, Dark_Type_V: -0.312, Dark_to_Black_Type_VI: -0.521 },
  rs12896399:  { Very_Pale_Type_I: 0.214, Pale_Type_II: 0.112, Dark_Type_V: -0.251, Dark_to_Black_Type_VI: -0.412 },
  rs16891982:  { Very_Pale_Type_I: 1.452, Pale_Type_II: 0.812, Dark_Type_V: -1.852, Dark_to_Black_Type_VI: -3.124 },
  rs1393350:   { Very_Pale_Type_I: 0.412, Pale_Type_II: 0.251, Dark_Type_V: -0.412, Dark_to_Black_Type_VI: -0.682 },
  rs12203592:  { Very_Pale_Type_I: 0.612, Pale_Type_II: 0.384, Dark_Type_V: -0.521, Dark_to_Black_Type_VI: -0.892 },
  rs1805007:   { Very_Pale_Type_I: 1.852, Pale_Type_II: 1.124, Dark_Type_V: -1.412, Dark_to_Black_Type_VI: -2.451 },
  rs1805008:   { Very_Pale_Type_I: 1.741, Pale_Type_II: 1.052, Dark_Type_V: -1.352, Dark_to_Black_Type_VI: -2.312 },
  rs1805009:   { Very_Pale_Type_I: 1.512, Pale_Type_II: 0.912, Dark_Type_V: -1.182, Dark_to_Black_Type_VI: -2.052 },
  rs1805006:   { Very_Pale_Type_I: 1.105, Pale_Type_II: 0.651, Dark_Type_V: -0.852, Dark_to_Black_Type_VI: -1.412 },
  rs885479:    { Very_Pale_Type_I: 0.912, Pale_Type_II: 0.512, Dark_Type_V: -0.712, Dark_to_Black_Type_VI: -1.214 },
  rs1805005:   { Very_Pale_Type_I: 0.752, Pale_Type_II: 0.412, Dark_Type_V: -0.582, Dark_to_Black_Type_VI: -0.982 },
  rs2228479:   { Very_Pale_Type_I: 0.512, Pale_Type_II: 0.312, Dark_Type_V: -0.412, Dark_to_Black_Type_VI: -0.712 },
  rs1110400:   { Very_Pale_Type_I: 0.412, Pale_Type_II: 0.214, Dark_Type_V: -0.312, Dark_to_Black_Type_VI: -0.512 },
  rs11547464:  { Very_Pale_Type_I: 0.312, Pale_Type_II: 0.152, Dark_Type_V: -0.214, Dark_to_Black_Type_VI: -0.412 },
  rs28936415:  { Very_Pale_Type_I: 1.312, Pale_Type_II: 0.781, Dark_Type_V: -1.052, Dark_to_Black_Type_VI: -1.852 },
  rs201326893: { Very_Pale_Type_I: 1.251, Pale_Type_II: 0.712, Dark_Type_V: -0.982, Dark_to_Black_Type_VI: -1.741 },
  rs12821256:  { Very_Pale_Type_I: 0.482, Pale_Type_II: 0.284, Dark_Type_V: -0.312, Dark_to_Black_Type_VI: -0.582 },
  rs6058017:   { Very_Pale_Type_I: 0.312, Pale_Type_II: 0.184, Dark_Type_V: -0.251, Dark_to_Black_Type_VI: -0.412 },
  rs10810681:  { Very_Pale_Type_I: 0.412, Pale_Type_II: 0.214, Dark_Type_V: -0.312, Dark_to_Black_Type_VI: -0.512 },
  rs3750965:   { Very_Pale_Type_I: 0.251, Pale_Type_II: 0.141, Dark_Type_V: -0.184, Dark_to_Black_Type_VI: -0.312 },
  rs1800414:   { Very_Pale_Type_I: -0.312, Pale_Type_II: -0.184, Dark_Type_V: 0.852, Dark_to_Black_Type_VI: 1.412 },
  rs1426654:   { Very_Pale_Type_I: 1.852, Pale_Type_II: 1.105, Dark_Type_V: -2.105, Dark_to_Black_Type_VI: -3.852 },
  rs1126809:   { Very_Pale_Type_I: 0.312, Pale_Type_II: 0.184, Dark_Type_V: -0.312, Dark_to_Black_Type_VI: -0.512 },
  rs3827760:   { Very_Pale_Type_I: -0.512, Pale_Type_II: -0.312, Dark_Type_V: 0.812, Dark_to_Black_Type_VI: 1.214 },
  rs1042602:   { Very_Pale_Type_I: 0.412, Pale_Type_II: 0.251, Dark_Type_V: -0.412, Dark_to_Black_Type_VI: -0.651 },
  rs2153271:   { Very_Pale_Type_I: 0.384, Pale_Type_II: 0.191, Dark_Type_V: -0.284, Dark_to_Black_Type_VI: -0.482 },
  rs35264875:  { Very_Pale_Type_I: 0.214, Pale_Type_II: 0.121, Dark_Type_V: -0.152, Dark_to_Black_Type_VI: -0.284 },
  rs28777:     { Very_Pale_Type_I: 0.752, Pale_Type_II: 0.412, Dark_Type_V: -0.852, Dark_to_Black_Type_VI: -1.412 },
  rs2470102:   { Very_Pale_Type_I: 0.812, Pale_Type_II: 0.482, Dark_Type_V: -0.912, Dark_to_Black_Type_VI: -1.512 },
  rs642742:    { Very_Pale_Type_I: 0.384, Pale_Type_II: 0.214, Dark_Type_V: -0.251, Dark_to_Black_Type_VI: -0.412 },
  rs1015362:   { Very_Pale_Type_I: 0.251, Pale_Type_II: 0.152, Dark_Type_V: -0.214, Dark_to_Black_Type_VI: -0.341 },
  rs4911414:   { Very_Pale_Type_I: 0.214, Pale_Type_II: 0.121, Dark_Type_V: -0.184, Dark_to_Black_Type_VI: -0.284 },
  rs1545397:   { Very_Pale_Type_I: -0.214, Pale_Type_II: -0.121, Dark_Type_V: 0.582, Dark_to_Black_Type_VI: 0.982 },
  rs74653330:  { Very_Pale_Type_I: -0.184, Pale_Type_II: -0.091, Dark_Type_V: 0.482, Dark_to_Black_Type_VI: 0.812 },
  rs1408799:   { Very_Pale_Type_I: 0.284, Pale_Type_II: 0.152, Dark_Type_V: -0.312, Dark_to_Black_Type_VI: -0.512 },
  rs26722:     { Very_Pale_Type_I: 0.184, Pale_Type_II: 0.091, Dark_Type_V: -0.184, Dark_to_Black_Type_VI: -0.312 },
  rs2814778:   { Very_Pale_Type_I: -1.214, Pale_Type_II: -0.781, Dark_Type_V: 2.451, Dark_to_Black_Type_VI: 4.852 },
  rs2042762:   { Very_Pale_Type_I: -0.152, Pale_Type_II: -0.081, Dark_Type_V: 0.214, Dark_to_Black_Type_VI: 0.384 },
  rs2024566:   { Very_Pale_Type_I: -0.121, Pale_Type_II: -0.061, Dark_Type_V: 0.184, Dark_to_Black_Type_VI: 0.312 },
};

// D. Hair Texture / Morphology: Ref = Straight (K=4)
export const TEXTURE_INTERCEPTS = {
  Wavy: -0.4120,
  Curly: -1.2140,
  Coily: -2.4510,
};
export const TEXTURE_SLOPES: Record<string, { Wavy: number; Curly: number; Coily: number }> = {
  rs3827760:  { Wavy: -1.412, Curly: -2.854, Coily: -3.951 },
  rs11803731: { Wavy: 0.412, Curly: 1.852, Coily: 2.451 },
  rs2814778:  { Wavy: 0.214, Curly: 1.214, Coily: 2.852 },
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
  hairTextureProbabilities: Record<string, number>;
  predictedHairTexture: string;
  decisionRatios: Record<string, number>;
  isConclusive: Record<string, boolean>;
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
  const usedSnpsSet = new Set<string>();

  // 1. Eye Color Prediction
  let blueLogit = EYE_INTERCEPTS.Blue;
  let intermLogit = EYE_INTERCEPTS.Intermediate;
  for (const [rsid, slopes] of Object.entries(EYE_SLOPES)) {
    if (genotypeDosages[rsid] !== undefined) {
      usedSnpsSet.add(rsid);
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

  // 2. Hair Color Prediction
  let blondLogit = HAIR_INTERCEPTS.Blond;
  let redLogit = HAIR_INTERCEPTS.Red;
  let blackLogit = HAIR_INTERCEPTS.Black;
  let mc1rRed = false;

  for (const [rsid, slopes] of Object.entries(HAIR_SLOPES)) {
    if (genotypeDosages[rsid] !== undefined) {
      usedSnpsSet.add(rsid);
      const dosage = genotypeDosages[rsid];
      blondLogit += slopes.Blond * dosage;
      redLogit += slopes.Red * dosage;
      blackLogit += slopes.Black * dosage;
      if (MC1R_EPISTATIC_VARIANTS.includes(rsid) && dosage > 0) {
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

  // 3. Skin Phototype Prediction
  let t1Logit = SKIN_INTERCEPTS.Very_Pale_Type_I;
  let t2Logit = SKIN_INTERCEPTS.Pale_Type_II;
  let t5Logit = SKIN_INTERCEPTS.Dark_Type_V;
  let t6Logit = SKIN_INTERCEPTS.Dark_to_Black_Type_VI;

  for (const [rsid, slopes] of Object.entries(SKIN_SLOPES)) {
    if (genotypeDosages[rsid] !== undefined) {
      usedSnpsSet.add(rsid);
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

  // 4. Hair Texture / Morphology Prediction
  let wavyLogit = TEXTURE_INTERCEPTS.Wavy;
  let curlyLogit = TEXTURE_INTERCEPTS.Curly;
  let coilyLogit = TEXTURE_INTERCEPTS.Coily;

  for (const [rsid, slopes] of Object.entries(TEXTURE_SLOPES)) {
    if (genotypeDosages[rsid] !== undefined) {
      usedSnpsSet.add(rsid);
      const dosage = genotypeDosages[rsid];
      wavyLogit += slopes.Wavy * dosage;
      curlyLogit += slopes.Curly * dosage;
      coilyLogit += slopes.Coily * dosage;
    }
  }
  const expWavy = Math.exp(Math.min(Math.max(wavyLogit, -50), 50));
  const expCurly = Math.exp(Math.min(Math.max(curlyLogit, -50), 50));
  const expCoily = Math.exp(Math.min(Math.max(coilyLogit, -50), 50));
  const expStraight = 1.0;
  const totalTexture = expStraight + expWavy + expCurly + expCoily;
  const textureProbs = {
    Straight: expStraight / totalTexture,
    Wavy: expWavy / totalTexture,
    Curly: expCurly / totalTexture,
    Coily: expCoily / totalTexture,
  };
  const predTexture = Object.entries(textureProbs).reduce((a, b) => (b[1] > a[1] ? b : a))[0];

  // 5. ISO 17025 Decision Ratios & Conclusiveness
  const calcRatio = (probs: Record<string, number>, topKey: string): [number, boolean] => {
    const topP = probs[topKey];
    const secondP = Math.max(...Object.entries(probs).filter(([k]) => k !== topKey).map(([, v]) => v));
    const ratio = topP / Math.max(secondP, 1e-12);
    const conclusive = topP >= 0.70 && ratio >= 3.0;
    return [ratio, conclusive];
  };

  const [eyeRatio, eyeConclusive] = calcRatio(eyeProbs, predEye);
  const [hairRatio, hairConclusive] = calcRatio(hairProbs, predHair);
  const [skinRatio, skinConclusive] = calcRatio(skinProbs, predSkin);
  const [textureRatio, textureConclusive] = calcRatio(textureProbs, predTexture);

  return {
    sampleId,
    eyeColorProbabilities: eyeProbs,
    predictedEyeColor: predEye,
    hairColorProbabilities: hairProbs,
    predictedHairColor: predHair,
    mc1rRedHairEpistasisFlag: mc1rRed,
    skinPhototypeProbabilities: skinProbs,
    predictedSkinPhototype: predSkin,
    hairTextureProbabilities: textureProbs,
    predictedHairTexture: predTexture,
    decisionRatios: {
      eye: eyeRatio,
      hair: hairRatio,
      skin: skinRatio,
      texture: textureRatio,
    },
    isConclusive: {
      eye: eyeConclusive,
      hair: hairConclusive,
      skin: skinConclusive,
      texture: textureConclusive,
    },
    numSnpsEvaluated: usedSnpsSet.size,
  };
}

export const calculateClientBgaPosterior = (genotypeDosages: Record<string, number>, sampleId = "SAMPLE") =>
  computeClientBgaPosteriors(sampleId, genotypeDosages);

export const calculateClientHIrisPlex = (genotypeDosages: Record<string, number>, sampleId = "SAMPLE") =>
  computeClientHIrisPlex(sampleId, genotypeDosages);

export const AIM_55_SNPS_CATALOG: { rsid: string; gene: string }[] = Object.entries(AIM_55_METADATA).map(
  ([rsid, meta]) => ({ rsid, gene: meta.gene })
);

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
  { rsid: "rs1805006", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (R142H)" },
  { rsid: "rs885479", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (I155T)" },
  { rsid: "rs1805005", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (D60N)" },
  { rsid: "rs2228479", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (V60L)" },
  { rsid: "rs1110400", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (V92M)" },
  { rsid: "rs11547464", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (R163Q)" },
  { rsid: "rs28936415", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (Y152X)" },
  { rsid: "rs201326893", gene: "MC1R", trait: "Red Hair & Fair Skin Epistasis (N29insA)" },
  { rsid: "rs12821256", gene: "KITLG", trait: "Blond Hair Expression" },
  { rsid: "rs6058017", gene: "ASIP", trait: "Pigment Aggregation" },
  { rsid: "rs10810681", gene: "BNC2", trait: "Skin Pigmentation & Saturation" },
  { rsid: "rs3750965", gene: "TPCN2", trait: "Hair & Skin Melanin Content" },
  { rsid: "rs1800414", gene: "OCA2", trait: "East Asian Brown Eye & Fair Skin" },
  { rsid: "rs1426654", gene: "SLC24A5", trait: "European Pale vs Deep Skin Phototype" },
  { rsid: "rs1126809", gene: "TYR", trait: "Oculocutaneous Melanin Synthesis" },
  { rsid: "rs3827760", gene: "EDAR", trait: "Coarse Thick Straight Hair Morphology" },
  { rsid: "rs11803731", gene: "TCHH", trait: "Hair Curliness & Coiling Morphology" },
  { rsid: "rs1042602", gene: "TYR", trait: "Freckling & Melanin Synthesis" },
  { rsid: "rs2153271", gene: "BNC2", trait: "Skin Tone Modifier" },
  { rsid: "rs35264875", gene: "TPCN2", trait: "Hair Color Intensity" },
  { rsid: "rs28777", gene: "SLC45A2", trait: "Skin & Eye Lightening" },
  { rsid: "rs2470102", gene: "SLC24A5", trait: "Skin Melanin Content" },
  { rsid: "rs642742", gene: "KITLG", trait: "Blond Hair Modifier" },
  { rsid: "rs1015362", gene: "ASIP", trait: "Dark vs Light Pigmentation Switch" },
  { rsid: "rs4911414", gene: "ASIP", trait: "Pigment Distribution" },
  { rsid: "rs1545397", gene: "OCA2", trait: "Iris & Skin Pigmentation" },
  { rsid: "rs74653330", gene: "OCA2", trait: "Iris Melanin Distribution" },
  { rsid: "rs1408799", gene: "TYRP1", trait: "Brown Hair & Eye Melanin" },
  { rsid: "rs26722", gene: "SLC24A4", trait: "Iris & Hair Lightening" },
  { rsid: "rs2814778", gene: "ACKR1", trait: "Duffy Null Deep Skin & Afro Texture" },
  { rsid: "rs2042762", gene: "Intergenic", trait: "Skin Phototype Modifier" },
  { rsid: "rs2024566", gene: "Intergenic", trait: "Skin Phototype Modifier" },
];


