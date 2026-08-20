/**
 * FORENZA Forensic Evidence Operating System
 * Module: Y-STR 27-Locus (Yfiler Plus) & RM Y-STR Lineage Biocomputational Engine (TypeScript Client-Side Twin)
 * Standards Compliance: ISO/IEC 17025:2017, SWGDAM Lineage Guidelines (2020), ENFSI Evaluative Reporting (2017)
 * Research Source: research/ystr_27_mtdna_empop_lineage_research.md
 */

export type YStrDye = '6-FAM' | 'VIC' | 'NED' | 'TAZ' | 'SID' | 'LIZ';

export type YStrMutationClass = 'Standard' | 'Multi-Copy' | 'Rapidly Mutating' | 'RM / Multi-Copy';

export interface YStrLocusMetadata {
  locusName: string;
  cytogeneticBand: string;
  grch38Start: number;
  grch38End: number;
  repeatUnitBp: number;
  canonicalMotif: string;
  ceDye: YStrDye;
  ampliconMinBp: number;
  ampliconMaxBp: number;
  mutationRate: number;
  stepwiseParamR: number;
  mutationClass: YStrMutationClass;
  isRapidlyMutating: boolean;
  isMultiCopy: boolean;
}

export interface YStrLocusResult {
  locusName: string;
  alleles: string[];
  rfuValues?: number[];
  peakHeightRatio?: number;
  isMicrovariant?: boolean;
  isOffLadder?: boolean;
  flags?: string[];
}

export type YStrProfileMap = Record<string, YStrLocusResult>;

export interface YStrHaplogroupPrediction {
  predictedHaplogroup: string;
  confidenceScore: number;
  bayesianPosteriors: Record<string, number>;
  distanceToModal: number;
  primarySnpMarker: string;
  description: string;
}

export interface YStrKinshipComparison {
  comparedLociCount: number;
  totalLociCompared: number;
  meioses: number;
  transmissionProbability: number;
  unrelatedMatchProbability: number;
  combinedKinshipIndex: number;
  kinshipLikelihoodRatio: number;
  mutatedLoci: Array<{ locus: string; steps: number; mutationRate: number; isRapidlyMutating: boolean }>;
  mutationCount: number;
  totalMutationsObserved: number;
  isKinshipSupported: boolean;
  enfsiVerbalScale: string;
}


export const YSTR_27_MASTER_REGISTRY: Record<string, YStrLocusMetadata> = {
  DYS19: {
    locusName: 'DYS19',
    cytogeneticBand: 'Yp11.2',
    grch38Start: 9471048,
    grch38End: 9471430,
    repeatUnitBp: 4,
    canonicalMotif: '[TAGA]',
    ceDye: '6-FAM',
    ampliconMinBp: 170,
    ampliconMaxBp: 210,
    mutationRate: 2.3e-3,
    stepwiseParamR: 0.95,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS389I: {
    locusName: 'DYS389I',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 12423733,
    grch38End: 12424100,
    repeatUnitBp: 4,
    canonicalMotif: '[TCTG] [TCTA]',
    ceDye: 'VIC',
    ampliconMinBp: 140,
    ampliconMaxBp: 180,
    mutationRate: 2.6e-3,
    stepwiseParamR: 0.94,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS389II: {
    locusName: 'DYS389II',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 12423600,
    grch38End: 12424100,
    repeatUnitBp: 4,
    canonicalMotif: '[TCTG] [TCTA] ... [TCTG] [TCTA]',
    ceDye: 'VIC',
    ampliconMinBp: 250,
    ampliconMaxBp: 310,
    mutationRate: 4.2e-3,
    stepwiseParamR: 0.92,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS390: {
    locusName: 'DYS390',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 17281230,
    grch38End: 17281600,
    repeatUnitBp: 4,
    canonicalMotif: '[TCTG] [TCTA]',
    ceDye: 'NED',
    ampliconMinBp: 190,
    ampliconMaxBp: 240,
    mutationRate: 2.1e-3,
    stepwiseParamR: 0.95,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS391: {
    locusName: 'DYS391',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 13887400,
    grch38End: 13887700,
    repeatUnitBp: 4,
    canonicalMotif: '[TCTA]',
    ceDye: 'NED',
    ampliconMinBp: 95,
    ampliconMaxBp: 135,
    mutationRate: 1.0e-3,
    stepwiseParamR: 0.98,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS392: {
    locusName: 'DYS392',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 22589100,
    grch38End: 22589450,
    repeatUnitBp: 3,
    canonicalMotif: '[TAT]',
    ceDye: 'TAZ',
    ampliconMinBp: 280,
    ampliconMaxBp: 340,
    mutationRate: 3.75e-4,
    stepwiseParamR: 0.99,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS393: {
    locusName: 'DYS393',
    cytogeneticBand: 'Yp11.2',
    grch38Start: 3110200,
    grch38End: 3110500,
    repeatUnitBp: 4,
    canonicalMotif: '[AGAT]',
    ceDye: '6-FAM',
    ampliconMinBp: 110,
    ampliconMaxBp: 150,
    mutationRate: 1.1e-3,
    stepwiseParamR: 0.97,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  'DYS385a/b': {
    locusName: 'DYS385a/b',
    cytogeneticBand: 'Yq11.223',
    grch38Start: 20850100,
    grch38End: 20851200,
    repeatUnitBp: 4,
    canonicalMotif: '[GAAA]',
    ceDye: 'VIC',
    ampliconMinBp: 240,
    ampliconMaxBp: 330,
    mutationRate: 2.2e-3,
    stepwiseParamR: 0.93,
    mutationClass: 'Multi-Copy',
    isRapidlyMutating: false,
    isMultiCopy: true,
  },
  DYS437: {
    locusName: 'DYS437',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 14451100,
    grch38End: 14451400,
    repeatUnitBp: 4,
    canonicalMotif: '[TATC]',
    ceDye: 'VIC',
    ampliconMinBp: 180,
    ampliconMaxBp: 220,
    mutationRate: 1.2e-3,
    stepwiseParamR: 0.96,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS438: {
    locusName: 'DYS438',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 14910200,
    grch38End: 14910500,
    repeatUnitBp: 5,
    canonicalMotif: '[TTTTC]',
    ceDye: 'TAZ',
    ampliconMinBp: 200,
    ampliconMaxBp: 250,
    mutationRate: 3.75e-4,
    stepwiseParamR: 0.99,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS439: {
    locusName: 'DYS439',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 14352100,
    grch38End: 14352450,
    repeatUnitBp: 4,
    canonicalMotif: '[AGAT]',
    ceDye: '6-FAM',
    ampliconMinBp: 210,
    ampliconMaxBp: 250,
    mutationRate: 2.4e-3,
    stepwiseParamR: 0.94,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS448: {
    locusName: 'DYS448',
    cytogeneticBand: 'Yq11.223',
    grch38Start: 24420100,
    grch38End: 24420600,
    repeatUnitBp: 6,
    canonicalMotif: '[AGAGAT]',
    ceDye: 'VIC',
    ampliconMinBp: 280,
    ampliconMaxBp: 350,
    mutationRate: 1.4e-3,
    stepwiseParamR: 0.96,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS456: {
    locusName: 'DYS456',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 16112000,
    grch38End: 16112350,
    repeatUnitBp: 4,
    canonicalMotif: '[AGAT]',
    ceDye: '6-FAM',
    ampliconMinBp: 130,
    ampliconMaxBp: 170,
    mutationRate: 3.8e-3,
    stepwiseParamR: 0.91,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS458: {
    locusName: 'DYS458',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 7901100,
    grch38End: 7901500,
    repeatUnitBp: 4,
    canonicalMotif: '[GAAA]',
    ceDye: 'NED',
    ampliconMinBp: 130,
    ampliconMaxBp: 180,
    mutationRate: 8.7e-3,
    stepwiseParamR: 0.88,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS635: {
    locusName: 'DYS635',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 14212100,
    grch38End: 14212500,
    repeatUnitBp: 4,
    canonicalMotif: '[TCTA] [TCTG]',
    ceDye: 'TAZ',
    ampliconMinBp: 200,
    ampliconMaxBp: 260,
    mutationRate: 2.5e-3,
    stepwiseParamR: 0.94,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  YGATAH4: {
    locusName: 'YGATAH4',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 18720100,
    grch38End: 18720400,
    repeatUnitBp: 4,
    canonicalMotif: '[AGAT]',
    ceDye: 'TAZ',
    ampliconMinBp: 120,
    ampliconMaxBp: 160,
    mutationRate: 1.8e-3,
    stepwiseParamR: 0.96,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS460: {
    locusName: 'DYS460',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 11811200,
    grch38End: 11811500,
    repeatUnitBp: 4,
    canonicalMotif: '[ATAG]',
    ceDye: 'VIC',
    ampliconMinBp: 100,
    ampliconMaxBp: 140,
    mutationRate: 2.1e-3,
    stepwiseParamR: 0.95,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS481: {
    locusName: 'DYS481',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 8502100,
    grch38End: 8502500,
    repeatUnitBp: 3,
    canonicalMotif: '[CTT]',
    ceDye: 'SID',
    ampliconMinBp: 100,
    ampliconMaxBp: 150,
    mutationRate: 2.8e-3,
    stepwiseParamR: 0.93,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS533: {
    locusName: 'DYS533',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 15201100,
    grch38End: 15201400,
    repeatUnitBp: 4,
    canonicalMotif: '[ATCT]',
    ceDye: 'SID',
    ampliconMinBp: 160,
    ampliconMaxBp: 200,
    mutationRate: 1.5e-3,
    stepwiseParamR: 0.96,
    mutationClass: 'Standard',
    isRapidlyMutating: false,
    isMultiCopy: false,
  },
  DYS570: {
    locusName: 'DYS570',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 6812100,
    grch38End: 6812500,
    repeatUnitBp: 4,
    canonicalMotif: '[TTTC]',
    ceDye: 'SID',
    ampliconMinBp: 210,
    ampliconMaxBp: 260,
    mutationRate: 1.2e-2,
    stepwiseParamR: 0.82,
    mutationClass: 'Rapidly Mutating',
    isRapidlyMutating: true,
    isMultiCopy: false,
  },
  DYS576: {
    locusName: 'DYS576',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 6911200,
    grch38End: 6911600,
    repeatUnitBp: 4,
    canonicalMotif: '[AAAG]',
    ceDye: 'SID',
    ampliconMinBp: 270,
    ampliconMaxBp: 330,
    mutationRate: 1.4e-2,
    stepwiseParamR: 0.80,
    mutationClass: 'Rapidly Mutating',
    isRapidlyMutating: true,
    isMultiCopy: false,
  },
  DYS627: {
    locusName: 'DYS627',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 21210100,
    grch38End: 21210600,
    repeatUnitBp: 4,
    canonicalMotif: '[AAAG] [AGAG]',
    ceDye: 'SID',
    ampliconMinBp: 340,
    ampliconMaxBp: 410,
    mutationRate: 1.3e-2,
    stepwiseParamR: 0.81,
    mutationClass: 'Rapidly Mutating',
    isRapidlyMutating: true,
    isMultiCopy: false,
  },
  DYS518: {
    locusName: 'DYS518',
    cytogeneticBand: 'Yq11.223',
    grch38Start: 20410200,
    grch38End: 20410800,
    repeatUnitBp: 4,
    canonicalMotif: '[AAAG]',
    ceDye: 'TAZ',
    ampliconMinBp: 360,
    ampliconMaxBp: 440,
    mutationRate: 1.8e-2,
    stepwiseParamR: 0.75,
    mutationClass: 'Rapidly Mutating',
    isRapidlyMutating: true,
    isMultiCopy: false,
  },
  DYS449: {
    locusName: 'DYS449',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 11210100,
    grch38End: 11210600,
    repeatUnitBp: 4,
    canonicalMotif: '[TTTC]',
    ceDye: 'NED',
    ampliconMinBp: 290,
    ampliconMaxBp: 370,
    mutationRate: 1.2e-2,
    stepwiseParamR: 0.83,
    mutationClass: 'Rapidly Mutating',
    isRapidlyMutating: true,
    isMultiCopy: false,
  },
  'DYF387S1a/b': {
    locusName: 'DYF387S1a/b',
    cytogeneticBand: 'Yq11.221',
    grch38Start: 22100100,
    grch38End: 22102500,
    repeatUnitBp: 4,
    canonicalMotif: '[AAAG]',
    ceDye: '6-FAM',
    ampliconMinBp: 280,
    ampliconMaxBp: 360,
    mutationRate: 1.6e-2,
    stepwiseParamR: 0.78,
    mutationClass: 'RM / Multi-Copy',
    isRapidlyMutating: true,
    isMultiCopy: true,
  },
};

export const YSTR_27_LOCI_ORDER: string[] = Object.keys(YSTR_27_MASTER_REGISTRY);

export const RM_YSTR_LOCI_SET = new Set([
  'DYS570', 'DYS576', 'DYS627', 'DYS518', 'DYS449', 'DYF387S1a/b'
]);

export const Y_HAPLOGROUP_MODAL_PROFILES: Record<string, { primarySnp: string; description: string; modals: Record<string, any> }> = {
  'R1b-M269': {
    primarySnp: 'M269 / P312 / U106',
    description: 'Western European / Atlantic Modal Haplotype',
    modals: {
      DYS393: 13, DYS390: 24, DYS19: 14, DYS391: 11,
      'DYS385a/b': [11, 14], DYS438: 12, DYS439: 12, DYS437: 15,
      DYS481: 22, DYS533: 12, DYS458: 17, DYS456: 15,
      DYS635: 23, YGATAH4: 12, DYS389I: 13, DYS389II: 29,
      DYS448: 19, DYS460: 11, DYS392: 13, DYS570: 17,
      DYS576: 18, DYS627: 15, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [35, 37],
    },
  },
  'R1a-M198': {
    primarySnp: 'M198 / M417',
    description: 'Eastern European / South Asian Lineage',
    modals: {
      DYS393: 13, DYS390: 25, DYS19: 16, DYS391: 10,
      'DYS385a/b': [11, 14], DYS438: 11, DYS439: 10, DYS437: 14,
      DYS481: 22, DYS533: 12, DYS458: 15, DYS456: 15,
      DYS635: 23, YGATAH4: 11, DYS389I: 13, DYS389II: 30,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 17,
      DYS576: 17, DYS627: 17, DYS518: 38, DYS449: 32,
      'DYF387S1a/b': [36, 38],
    },
  },
  'I1-M253': {
    primarySnp: 'M253',
    description: 'Northern European / Scandinavian Lineage',
    modals: {
      DYS393: 13, DYS390: 22, DYS19: 14, DYS391: 10,
      'DYS385a/b': [14, 14], DYS438: 10, DYS439: 11, DYS437: 16,
      DYS481: 28, DYS533: 12, DYS458: 15, DYS456: 14,
      DYS635: 21, YGATAH4: 10, DYS389I: 13, DYS389II: 28,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 19,
      DYS576: 15, DYS627: 18, DYS518: 39, DYS449: 29,
      'DYF387S1a/b': [37, 37],
    },
  },
  'I2-M438': {
    primarySnp: 'M438 / L621',
    description: 'Balkans / Dinaric & Western European Lineage',
    modals: {
      DYS393: 15, DYS390: 24, DYS19: 16, DYS391: 10,
      'DYS385a/b': [14, 15], DYS438: 10, DYS439: 11, DYS437: 15,
      DYS481: 21, DYS533: 13, DYS458: 15, DYS456: 15,
      DYS635: 24, YGATAH4: 11, DYS389I: 13, DYS389II: 31,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 17,
      DYS576: 17, DYS627: 17, DYS518: 39, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
  'J1-M267': {
    primarySnp: 'M267',
    description: 'Middle Eastern / Semitic Lineage',
    modals: {
      DYS393: 12, DYS390: 23, DYS19: 14, DYS391: 10,
      'DYS385a/b': [14, 17], DYS438: 10, DYS439: 11, DYS437: 14,
      DYS481: 22, DYS533: 12, DYS458: 18, DYS456: 15,
      DYS635: 21, YGATAH4: 11, DYS389I: 13, DYS389II: 29,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 18,
      DYS576: 17, DYS627: 20, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [37, 38],
    },
  },
  'J2-M172': {
    primarySnp: 'M172',
    description: 'Anatolian / Mediterranean / Caucasian Lineage',
    modals: {
      DYS393: 12, DYS390: 23, DYS19: 15, DYS391: 10,
      'DYS385a/b': [13, 15], DYS438: 10, DYS439: 12, DYS437: 15,
      DYS481: 23, DYS533: 12, DYS458: 17, DYS456: 15,
      DYS635: 22, YGATAH4: 11, DYS389I: 13, DYS389II: 29,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 17,
      DYS576: 16, DYS627: 18, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
  'E1b1b-M215': {
    primarySnp: 'M215 / M35',
    description: 'North / East African & Southern European Lineage',
    modals: {
      DYS393: 13, DYS390: 24, DYS19: 13, DYS391: 10,
      'DYS385a/b': [11, 12], DYS438: 10, DYS439: 12, DYS437: 15,
      DYS481: 22, DYS533: 12, DYS458: 16, DYS456: 16,
      DYS635: 21, YGATAH4: 11, DYS389I: 13, DYS389II: 30,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 17,
      DYS576: 18, DYS627: 18, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
  'E1b1a-V38': {
    primarySnp: 'V38 / M2',
    description: 'Sub-Saharan African / Bantu Expansion Lineage',
    modals: {
      DYS393: 15, DYS390: 21, DYS19: 15, DYS391: 10,
      'DYS385a/b': [15, 16], DYS438: 10, DYS439: 11, DYS437: 16,
      DYS481: 25, DYS533: 13, DYS458: 16, DYS456: 15,
      DYS635: 21, YGATAH4: 11, DYS389I: 14, DYS389II: 31,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 19,
      DYS576: 16, DYS627: 18, DYS518: 40, DYS449: 34,
      'DYF387S1a/b': [38, 39],
    },
  },
  'G2a-P15': {
    primarySnp: 'P15 / L30',
    description: 'Caucasian / Early European Neolithic Farmer Lineage',
    modals: {
      DYS393: 14, DYS390: 22, DYS19: 15, DYS391: 10,
      'DYS385a/b': [13, 15], DYS438: 10, DYS439: 11, DYS437: 15,
      DYS481: 22, DYS533: 12, DYS458: 17, DYS456: 15,
      DYS635: 21, YGATAH4: 11, DYS389I: 12, DYS389II: 29,
      DYS448: 21, DYS460: 11, DYS392: 11, DYS570: 17,
      DYS576: 17, DYS627: 18, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
  'N-M231': {
    primarySnp: 'M231 / Tat',
    description: 'North Eurasian / Uralic & Siberian Lineage',
    modals: {
      DYS393: 14, DYS390: 23, DYS19: 14, DYS391: 11,
      'DYS385a/b': [11, 13], DYS438: 10, DYS439: 11, DYS437: 14,
      DYS481: 22, DYS533: 12, DYS458: 17, DYS456: 14,
      DYS635: 22, YGATAH4: 11, DYS389I: 13, DYS389II: 30,
      DYS448: 19, DYS460: 11, DYS392: 14, DYS570: 17,
      DYS576: 17, DYS627: 18, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
  'O-M175': {
    primarySnp: 'M175',
    description: 'East Asian / Southeast Asian Lineage',
    modals: {
      DYS393: 12, DYS390: 24, DYS19: 15, DYS391: 10,
      'DYS385a/b': [12, 18], DYS438: 11, DYS439: 11, DYS437: 14,
      DYS481: 22, DYS533: 12, DYS458: 18, DYS456: 15,
      DYS635: 21, YGATAH4: 11, DYS389I: 12, DYS389II: 29,
      DYS448: 20, DYS460: 11, DYS392: 13, DYS570: 17,
      DYS576: 18, DYS627: 18, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
  'Q-M3': {
    primarySnp: 'M242 / M3',
    description: 'Indigenous American / North & Central Asian Lineage',
    modals: {
      DYS393: 13, DYS390: 24, DYS19: 13, DYS391: 10,
      'DYS385a/b': [12, 13], DYS438: 10, DYS439: 12, DYS437: 14,
      DYS481: 22, DYS533: 11, DYS458: 17.2, DYS456: 15,
      DYS635: 23, YGATAH4: 11, DYS389I: 13, DYS389II: 30,
      DYS448: 20, DYS460: 10, DYS392: 14, DYS570: 16,
      DYS576: 17, DYS627: 20.2, DYS518: 36, DYS449: 28,
      'DYF387S1a/b': [36, 37],
    },
  },
  'T-M184': {
    primarySnp: 'M184',
    description: 'Horn of Africa / South Asian Lineage',
    modals: {
      DYS393: 13, DYS390: 24, DYS19: 15, DYS391: 10,
      'DYS385a/b': [11, 14], DYS438: 11, DYS439: 12, DYS437: 15,
      DYS481: 22, DYS533: 12, DYS458: 16, DYS456: 15,
      DYS635: 21, YGATAH4: 11, DYS389I: 13, DYS389II: 30,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 17,
      DYS576: 17, DYS627: 18, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
  'L-M20': {
    primarySnp: 'M20',
    description: 'South Asian / Indus Valley Lineage',
    modals: {
      DYS393: 12, DYS390: 23, DYS19: 14, DYS391: 10,
      'DYS385a/b': [13, 14], DYS438: 10, DYS439: 11, DYS437: 14,
      DYS481: 22, DYS533: 12, DYS458: 17, DYS456: 15,
      DYS635: 21, YGATAH4: 11, DYS389I: 13, DYS389II: 30,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 17,
      DYS576: 17, DYS627: 18, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
  'C-M130': {
    primarySnp: 'M130 / P39',
    description: 'Oceanian / Mongolian / Indigenous American Lineage',
    modals: {
      DYS393: 13, DYS390: 25, DYS19: 15, DYS391: 10,
      'DYS385a/b': [12, 13], DYS438: 10, DYS439: 11, DYS437: 14,
      DYS481: 22, DYS533: 12, DYS458: 17, DYS456: 15,
      DYS635: 22, YGATAH4: 11, DYS389I: 13, DYS389II: 30,
      DYS448: 20, DYS460: 11, DYS392: 11, DYS570: 17,
      DYS576: 17, DYS627: 18, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
  'D-CTS11577': {
    primarySnp: 'CTS11577',
    description: 'Tibetan / Japanese (Jomon) / Andaman Lineage',
    modals: {
      DYS393: 14, DYS390: 23, DYS19: 16, DYS391: 10,
      'DYS385a/b': [13, 14], DYS438: 10, DYS439: 11, DYS437: 14,
      DYS481: 22, DYS533: 12, DYS458: 17, DYS456: 15,
      DYS635: 21, YGATAH4: 11, DYS389I: 14, DYS389II: 31,
      DYS448: 20, DYS460: 11, DYS392: 12, DYS570: 17,
      DYS576: 17, DYS627: 18, DYS518: 38, DYS449: 30,
      'DYF387S1a/b': [36, 38],
    },
  },
};

export class YStr27LocusEngine {
  public static getLocusMetadata(locusName: string): YStrLocusMetadata | null {
    const trimmed = locusName.trim();
    if (YSTR_27_MASTER_REGISTRY[trimmed]) return YSTR_27_MASTER_REGISTRY[trimmed];
    const lower = trimmed.toLowerCase();
    for (const [name, meta] of Object.entries(YSTR_27_MASTER_REGISTRY)) {
      if (name.toLowerCase() === lower) return meta;
    }
    return null;
  }

  public static decoupleDys389(dys389i: number, dys389iiTotal: number): [number, number] {
    const dys389_2_pure = dys389iiTotal - dys389i;
    return [dys389i, dys389_2_pure];
  }

  public static evaluateMultiCopyPhr(
    locusName: string,
    rfuValues: number[],
    threshold: number = 0.50
  ): { phr: number; isBalanced: boolean; warningFlag: string | null } {
    if (!rfuValues || rfuValues.length < 2) {
      return { phr: 1.0, isBalanced: true, warningFlag: null };
    }
    const rfu1 = rfuValues[0];
    const rfu2 = rfuValues[1];
    const maxRfu = Math.max(rfu1, rfu2);
    if (maxRfu <= 0) {
      return { phr: 1.0, isBalanced: true, warningFlag: null };
    }
    const phr = Math.min(rfu1, rfu2) / maxRfu;
    if (phr < threshold) {
      const warning = `Imbalance warning: PHR (${phr.toFixed(2)}) < ${threshold.toFixed(2)} at ${locusName}`;
      return { phr, isBalanced: false, warningFlag: warning };
    }
    return { phr, isBalanced: true, warningFlag: null };
  }

  public static calculateClopperPearson95Upper(k: number, n: number, alpha: number = 0.05): number {
    if (n <= 0) return 1.0;
    if (k === 0) {
      return 1.0 - Math.pow(alpha, 1.0 / (n + 1.0));
    }
    // Approximation for Clopper-Pearson upper bound using Beta / Wilson inversion
    const z = 1.95996398454; // standard 95% two-sided normal quantile
    const p = k / n;
    const denominator = 1 + (z * z) / n;
    const center = p + (z * z) / (2 * n);
    const spread = z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n));
    const upperWilson = (center + spread) / denominator;
    return Math.min(1.0, Math.max(upperWilson, (k + 1) / (n + 1)));
  }

  public static calculateBrennerFrequency(k: number, n: number, theta: number = 0.02): number {
    if (n <= 0) return 1.0;
    return (k + theta) / (n + theta);
  }

  public static calculateDiscreteLaplaceLocusProb(
    observedAllele: number,
    modalAllele: number,
    dispersionLambda: number = 0.65
  ): number {
    const diff = Math.abs(observedAllele - modalAllele);
    const coeff = (1.0 - dispersionLambda) / (1.0 + dispersionLambda);
    return coeff * Math.pow(dispersionLambda, diff);
  }

  public static predictYDnaHaplogroup(ystrProfile: Record<string, any>): YStrHaplogroupPrediction {
    const scores: Record<string, number> = {};
    const distances: Record<string, number> = {};

    for (const [hgName, hgData] of Object.entries(Y_HAPLOGROUP_MODAL_PROFILES)) {
      const modals = hgData.modals;
      let logProb = 0.0;
      let distSum = 0.0;
      let evaluatedLoci = 0;

      for (const [locus, modalVal] of Object.entries(modals)) {
        if (!ystrProfile[locus]) continue;
        const rawVal = ystrProfile[locus];

        if (Array.isArray(rawVal)) {
          const obsVals = rawVal.map((v) => parseFloat(String(v))).filter((v) => !isNaN(v));
          if (Array.isArray(modalVal)) {
            const modalList = modalVal.map((m) => parseFloat(String(m)));
            if (obsVals.length > 0 && modalList.length > 0) {
              const d = Math.abs(obsVals[0] - modalList[0]) + (obsVals.length > 1 && modalList.length > 1 ? Math.abs(obsVals[1] - modalList[1]) : 0);
              distSum += d;
              const pLoc = this.calculateDiscreteLaplaceLocusProb(obsVals[0], modalList[0]);
              logProb += Math.log(Math.max(pLoc, 1e-12));
              evaluatedLoci++;
            }
          } else if (obsVals.length > 0) {
            const d = Math.abs(obsVals[0] - Number(modalVal));
            distSum += d;
            const pLoc = this.calculateDiscreteLaplaceLocusProb(obsVals[0], Number(modalVal));
            logProb += Math.log(Math.max(pLoc, 1e-12));
            evaluatedLoci++;
          }
        } else {
          const cleanStr = String(rawVal).replace(/[[\]]/g, '').trim();
          const obsNum = parseFloat(cleanStr);
          if (!isNaN(obsNum)) {
            const modalNum = Array.isArray(modalVal) ? Number(modalVal[0]) : Number(modalVal);
            const d = Math.abs(obsNum - modalNum);
            distSum += d;
            const pLoc = this.calculateDiscreteLaplaceLocusProb(obsNum, modalNum);
            logProb += Math.log(Math.max(pLoc, 1e-12));
            evaluatedLoci++;
          }
        }
      }

      if (evaluatedLoci > 0) {
        scores[hgName] = logProb;
        distances[hgName] = distSum / evaluatedLoci;
      } else {
        scores[hgName] = -999.0;
        distances[hgName] = 99.0;
      }
    }

    const scoreVals = Object.values(scores);
    const maxLog = scoreVals.length > 0 ? Math.max(...scoreVals) : 0.0;
    let expSum = 0.0;
    for (const s of scoreVals) {
      expSum += Math.exp(s - maxLog);
    }

    const posteriors: Record<string, number> = {};
    for (const [k, v] of Object.entries(scores)) {
      posteriors[k] = expSum > 0 ? Math.exp(v - maxLog) / expSum : 0.0;
    }

    let bestHg = 'R1b-M269';
    let maxConf = -1;
    for (const [k, v] of Object.entries(posteriors)) {
      if (v > maxConf) {
        maxConf = v;
        bestHg = k;
      }
    }

    const bestData = Y_HAPLOGROUP_MODAL_PROFILES[bestHg] || {
      primarySnp: 'M269',
      description: 'Western European Lineage',
    };

    return {
      predictedHaplogroup: bestHg,
      confidenceScore: maxConf,
      bayesianPosteriors: posteriors,
      distanceToModal: distances[bestHg] || 0.0,
      primarySnpMarker: bestData.primarySnp,
      description: bestData.description,
    };
  }

  public static calculateSmmKinshipIndex(
    profileA: Record<string, any>,
    profileB: Record<string, any>,
    options: { meioses?: number; databaseSize?: number; unrelatedMatchProb?: number } | number = {}
  ): {
    comparedLociCount: number;
    totalLociCompared: number;
    meioses: number;
    transmissionProbability: number;
    unrelatedMatchProbability: number;
    combinedKinshipIndex: number;
    kinshipLikelihoodRatio: number;
    mutatedLoci: Array<{ locus: string; steps: number; mutationRate: number; isRapidlyMutating: boolean }>;
    mutationCount: number;
    totalMutationsObserved: number;
    isKinshipSupported: boolean;
    enfsiVerbalScale: string;
  } {
    const opts = typeof options === 'number' ? { meioses: options } : (options || {});
    const m = opts.meioses || 1;
    const dbSize = opts.databaseSize || 35000;
    let probTransmission = 1.0;
    let comparedLociCount = 0;
    const mutatedLoci: Array<{ locus: string; steps: number; mutationRate: number; isRapidlyMutating: boolean }> = [];

    for (const [locusName, meta] of Object.entries(YSTR_27_MASTER_REGISTRY)) {
      if (!profileA[locusName] || !profileB[locusName]) continue;

      const valA = profileA[locusName];
      const valB = profileB[locusName];

      let diff = 0;
      if (Array.isArray(valA) && Array.isArray(valB)) {
        const aNums = valA.map((x) => parseFloat(String(x))).filter((x) => !isNaN(x));
        const bNums = valB.map((x) => parseFloat(String(x))).filter((x) => !isNaN(x));
        if (aNums.length === 0 || bNums.length === 0) continue;
        diff = Math.abs(aNums[0] - bNums[0]);
      } else {
        const strA = String(valA).replace(/[[\]]/g, '').trim();
        const strB = String(valB).replace(/[[\]]/g, '').trim();
        const numA = parseFloat(strA);
        const numB = parseFloat(strB);
        if (isNaN(numA) || isNaN(numB)) continue;
        diff = Math.abs(numA - numB);
      }

      const mu = meta.mutationRate;
      const steps = Math.round(diff);
      let pLoc = 1.0;

      if (steps === 0) {
        pLoc = Math.pow(1.0 - mu, m);
      } else if (steps === 1) {
        pLoc = (m * mu * Math.pow(1.0 - mu, m - 1)) / 2.0;
        mutatedLoci.push({
          locus: locusName,
          steps: 1,
          mutationRate: mu,
          isRapidlyMutating: meta.isRapidlyMutating,
        });
      } else if (steps === 2) {
        const combM2 = m >= 2 ? (m * (m - 1)) / 2.0 : 0.5;
        pLoc = (combM2 * Math.pow(mu, 2) * Math.pow(1.0 - mu, Math.max(m - 2, 0))) / 4.0;
        mutatedLoci.push({
          locus: locusName,
          steps: 2,
          mutationRate: mu,
          isRapidlyMutating: meta.isRapidlyMutating,
        });
      } else {
        pLoc = Math.pow(mu, steps) / Math.pow(2.0, steps);
        mutatedLoci.push({
          locus: locusName,
          steps,
          mutationRate: mu,
          isRapidlyMutating: meta.isRapidlyMutating,
        });
      }

      probTransmission *= Math.max(pLoc, 1e-18);
      comparedLociCount++;
    }

    const pUnrelated = (typeof opts === 'object' && opts.unrelatedMatchProb) || this.calculateClopperPearson95Upper(0, dbSize);
    const cpi = pUnrelated > 0 ? probTransmission / pUnrelated : 1.0;
    const log10Cpi = cpi > 0 ? Math.log10(cpi) : -99.0;

    let enfsiVerbal = 'Inconclusive Kinship Evidence';
    if (log10Cpi >= 6.0) enfsiVerbal = 'Extremely Strong Support for Paternal Lineage Kinship (Hp)';
    else if (log10Cpi >= 4.0) enfsiVerbal = 'Strong Support for Paternal Lineage Kinship (Hp)';
    else if (log10Cpi >= 3.0) enfsiVerbal = 'Moderately Strong Support for Paternal Lineage Kinship (Hp)';
    else if (log10Cpi >= 2.0) enfsiVerbal = 'Moderate Support for Paternal Lineage Kinship (Hp)';
    else if (log10Cpi >= 1.0) enfsiVerbal = 'Limited / Weak Support for Paternal Lineage Kinship (Hp)';

    return {
      comparedLociCount,
      totalLociCompared: comparedLociCount,
      meioses: m,
      transmissionProbability: probTransmission,
      unrelatedMatchProbability: pUnrelated,
      combinedKinshipIndex: cpi,
      kinshipLikelihoodRatio: cpi,
      mutatedLoci,
      mutationCount: mutatedLoci.length,
      totalMutationsObserved: mutatedLoci.length,
      isKinshipSupported: cpi > 1.0,
      enfsiVerbalScale: enfsiVerbal,
    };
  }


  public static calculateBrennerSubpopCorrection(pUpper: number, theta: number = 0.02): number {
    return (pUpper + theta) / (1.0 + theta);
  }


  public static deconvoluteMaleMixture(profileAlleles: Record<string, any>, phrThreshold: number = 0.50): {
    nMaleMin: number;
    minimumMaleContributors: number;
    isMixture: boolean;
    maxSingleCopyAlleles: number;
    maxSingleLocusAlleles: number;
    maxMultiCopyAlleles: number;
    locusCounts: Record<string, number>;
  } {
    let maxSingle = 1;
    let maxMulti = 1;
    const locusCounts: Record<string, number> = {};

    for (const [locusName, val] of Object.entries(profileAlleles)) {
      const meta = this.getLocusMetadata(locusName);
      let count = 1;
      if (Array.isArray(val)) {
        count = val.length;
      } else if (val && typeof val === 'object' && Array.isArray(val.alleles)) {
        count = val.alleles.length;
      }
      locusCounts[locusName] = count;

      if (meta && meta.isMultiCopy) {
        const nContr = Math.ceil(count / 2.0);
        if (nContr > maxMulti) maxMulti = nContr;
      } else {
        if (count > maxSingle) maxSingle = count;
      }
    }

    const nMaleMin = Math.max(maxSingle, maxMulti);
    return {
      nMaleMin,
      minimumMaleContributors: nMaleMin,
      isMixture: nMaleMin > 1,
      maxSingleCopyAlleles: maxSingle,
      maxSingleLocusAlleles: maxSingle,
      maxMultiCopyAlleles: maxMulti * 2,
      locusCounts,
    };
  }



  public static predictHaplogroup(profile: any): YStrHaplogroupPrediction {
    return this.predictYDnaHaplogroup(profile);
  }

  public static compareHaplotypesForKinship(
    profileA: Record<string, any>,
    profileB: Record<string, any>,
    options?: { meioses?: number; databaseSize?: number; unrelatedMatchProb?: number } | number
  ) {
    return this.calculateSmmKinshipIndex(profileA, profileB, options);
  }


  public static calculateMatchProbabilityClopperPearson(k: number = 0, n: number = 35000) {
    const upper = this.calculateClopperPearson95Upper(k, n);
    const lr = upper > 0 ? 1.0 / upper : 0.0;
    const log10Lr = lr > 0 ? Math.log10(lr) : 0.0;
    let enfsiVerbal = 'Extremely Strong Support for Paternal Lineage Match (Hp)';
    if (log10Lr < 1.0) enfsiVerbal = 'Inconclusive Evidence';
    else if (log10Lr < 2.0) enfsiVerbal = 'Limited / Weak Support for Lineage Match (Hp)';
    else if (log10Lr < 3.0) enfsiVerbal = 'Moderate Support for Lineage Match (Hp)';
    else if (log10Lr < 4.0) enfsiVerbal = 'Moderately Strong Support for Lineage Match (Hp)';
    else if (log10Lr < 6.0) enfsiVerbal = 'Strong Support for Lineage Match (Hp)';
    return {
      kMatches: k,
      databaseSize: n,
      upperBound: upper,
      likelihoodRatio: lr,
      log10Lr,
      enfsiVerbalScale: enfsiVerbal,
    };
  }
}



// Aliases for naming compatibility
export const Ystr27LocusEngine = YStr27LocusEngine;
export const YSTR_HAPLOGROUP_MODALS = Y_HAPLOGROUP_MODAL_PROFILES;
export type YstrLocusMetadata = YStrLocusMetadata;
export type YstrLocusResult = YStrLocusResult;
export type YstrProfileMap = YStrProfileMap;
export type YstrHaplogroupPrediction = YStrHaplogroupPrediction;
export type YstrKinshipComparison = YStrKinshipComparison;


