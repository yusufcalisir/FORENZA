/**
 * Forensic DNA STR Locus Master Registry & Micro-Variant Engine
 * Compliant with ISO/IEC 17025:2017, SWGDAM 2020, ENFSI 2017, and ISFG Guidelines.
 * Derived verbatim from research specification: research/str_24_locus_microvariants_research.md
 */

export type StrRepeatUnitClass = 'Tetranucleotide' | 'Pentanucleotide' | 'Trinucleotide' | 'Non-STR Indel';
export type StrMotifClass = 'Simple' | 'Compound' | 'Complex' | 'Dimorphic' | 'Monomorphic';

export type MicrovariantEtiologyClass =
  | 'Single-base deletion in core repeat unit'
  | 'Single-base insertion'
  | 'Dinucleotide insertion/deletion'
  | 'Trinucleotide motif insertion'
  | 'Partial repeat collapse / residual unit'
  | 'Complex array hypervariable frameshift'
  | 'Intronic Insertion/Deletion';

export interface StrLocusMetadata {
  locusName: string;
  cytogeneticBand: string;
  grch38Coords: string;
  repeatUnitClass: StrRepeatUnitClass;
  repeatUnitSizeBp: number;
  motifClass: StrMotifClass;
  canonicalMotifSequence: string;
  observedAlleleSpectrum: string[];
  documentedMicrovariants: string[];
  maxReverseStutterRatio: number; // SR_max
  germlineMutationRate10k: number; // mu * 10^-3
  stepwiseMutationR: number; // r parameter in SMM
  isCodisCore: boolean;
  dyeChannelDefault: string;
}

export interface MicrovariantDetail {
  locusName: string;
  fractionalAllele: string;
  integerBaseRepeat: number;
  fractionalOffset: number;
  deltaBp: number;
  alternateDeltaBp: number | null;
  sequenceRepresentation: string;
  etiologyDescription: string;
  etiologyClass: MicrovariantEtiologyClass;
}

export const STR_LOCUS_24_MASTER_REGISTRY: Record<string, StrLocusMetadata> = {
  D3S1358: {
    locusName: 'D3S1358',
    cytogeneticBand: '3p21.31',
    grch38Coords: 'chr3:45,540,056-45,540,210',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Compound',
    canonicalMotifSequence: 'TCTA [TCTG]n [TCTA]m',
    observedAlleleSpectrum: ['8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.110,
    germlineMutationRate10k: 1.20,
    stepwiseMutationR: 0.850,
    isCodisCore: true,
    dyeChannelDefault: 'BLUE',
  },
  vWA: {
    locusName: 'vWA',
    cytogeneticBand: '12p13.31',
    grch38Coords: 'chr12:5,983,161-5,983,350',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Compound',
    canonicalMotifSequence: 'TCTA [TCTG]n [TCTA]m',
    observedAlleleSpectrum: ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.115,
    germlineMutationRate10k: 2.50,
    stepwiseMutationR: 0.880,
    isCodisCore: true,
    dyeChannelDefault: 'GREEN',
  },
  FGA: {
    locusName: 'FGA',
    cytogeneticBand: '4q31.3',
    grch38Coords: 'chr4:154,582,650-154,582,980',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Complex',
    canonicalMotifSequence: '[GGAA]2 GGAG [AAAG]n AGAA AAAA [GAAA]m',
    observedAlleleSpectrum: [
      '15', '16', '16.2', '17', '18', '19', '20', '21', '21.2', '22', '22.2', '23',
      '24', '25', '25.2', '26', '26.2', '27', '28', '29', '30', '30.2', '31', '32',
      '33', '42.2', '43.2', '44.2', '45.2', '46.2', '47.2', '48.2', '49.2', '50.2', '51.2',
    ],
    documentedMicrovariants: ['16.2', '21.2', '22.2', '25.2', '26.2', '30.2', '42.2', '43.2', '44.2', '45.2', '46.2', '47.2', '48.2', '49.2', '50.2', '51.2'],
    maxReverseStutterRatio: 0.130,
    germlineMutationRate10k: 2.80,
    stepwiseMutationR: 0.820,
    isCodisCore: true,
    dyeChannelDefault: 'BLUE',
  },
  D8S1179: {
    locusName: 'D8S1179',
    cytogeneticBand: '8q24.13',
    grch38Coords: 'chr8:124,892,010-124,892,210',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Compound',
    canonicalMotifSequence: '[TCTA]n [TCTG]m',
    observedAlleleSpectrum: ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.100,
    germlineMutationRate10k: 1.40,
    stepwiseMutationR: 0.860,
    isCodisCore: true,
    dyeChannelDefault: 'GREEN',
  },
  D21S11: {
    locusName: 'D21S11',
    cytogeneticBand: '21q21.1',
    grch38Coords: 'chr21:19,182,000-19,182,400',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Complex',
    canonicalMotifSequence: '[TCTA]n [TCTG]m [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCTA [TCTG]p [TCTA]q',
    observedAlleleSpectrum: [
      '24', '24.2', '25', '26', '27', '28', '28.2', '29', '29.2', '30', '30.2',
      '31', '31.2', '32', '32.2', '33', '33.2', '34', '34.2', '35', '36', '37', '38',
    ],
    documentedMicrovariants: ['24.2', '28.2', '29.2', '30.2', '31.2', '32.2', '33.2', '34.2'],
    maxReverseStutterRatio: 0.120,
    germlineMutationRate10k: 2.10,
    stepwiseMutationR: 0.800,
    isCodisCore: true,
    dyeChannelDefault: 'YELLOW',
  },
  D18S51: {
    locusName: 'D18S51',
    cytogeneticBand: '18q21.33',
    grch38Coords: 'chr18:61,431,200-61,431,600',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[AGAA]n',
    observedAlleleSpectrum: [
      '7', '8', '9', '10', '10.2', '11', '12', '13', '13.2', '14', '14.2', '15',
      '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27',
    ],
    documentedMicrovariants: ['10.2', '13.2', '14.2'],
    maxReverseStutterRatio: 0.140,
    germlineMutationRate10k: 2.20,
    stepwiseMutationR: 0.900,
    isCodisCore: true,
    dyeChannelDefault: 'BLUE',
  },
  D5S818: {
    locusName: 'D5S818',
    cytogeneticBand: '5q23.2',
    grch38Coords: 'chr5:123,774,100-123,774,350',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[AGAT]n',
    observedAlleleSpectrum: ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.090,
    germlineMutationRate10k: 1.00,
    stepwiseMutationR: 0.920,
    isCodisCore: true,
    dyeChannelDefault: 'YELLOW',
  },
  D13S317: {
    locusName: 'D13S317',
    cytogeneticBand: '13q31.1',
    grch38Coords: 'chr13:82,147,100-82,147,350',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[TATC]n',
    observedAlleleSpectrum: ['5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.080,
    germlineMutationRate10k: 1.30,
    stepwiseMutationR: 0.910,
    isCodisCore: true,
    dyeChannelDefault: 'GREEN',
  },
  D7S820: {
    locusName: 'D7S820',
    cytogeneticBand: '7q21.11',
    grch38Coords: 'chr7:83,789,100-83,789,350',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[GATA]n',
    observedAlleleSpectrum: ['6', '7', '8', '8.1', '9', '9.1', '10', '11', '12', '13', '14', '15'],
    documentedMicrovariants: ['8.1', '9.1'],
    maxReverseStutterRatio: 0.080,
    germlineMutationRate10k: 1.00,
    stepwiseMutationR: 0.920,
    isCodisCore: true,
    dyeChannelDefault: 'GREEN',
  },
  D16S539: {
    locusName: 'D16S539',
    cytogeneticBand: '16q24.1',
    grch38Coords: 'chr16:84,947,100-84,947,350',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[GATA]n',
    observedAlleleSpectrum: ['5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.090,
    germlineMutationRate10k: 1.10,
    stepwiseMutationR: 0.910,
    isCodisCore: true,
    dyeChannelDefault: 'RED',
  },
  CSF1PO: {
    locusName: 'CSF1PO',
    cytogeneticBand: '5q33.1',
    grch38Coords: 'chr5:150,076,200-150,076,450',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[ATCT]n',
    observedAlleleSpectrum: ['6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.080,
    germlineMutationRate10k: 1.20,
    stepwiseMutationR: 0.930,
    isCodisCore: true,
    dyeChannelDefault: 'GREEN',
  },
  TH01: {
    locusName: 'TH01',
    cytogeneticBand: '11p15.5',
    grch38Coords: 'chr11:2,171,050-2,171,250',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[AATG]n',
    observedAlleleSpectrum: ['3', '4', '5', '6', '7', '8', '8.3', '9', '9.3', '10', '10.3', '11', '12', '13.3', '14'],
    documentedMicrovariants: ['8.3', '9.3', '10.3', '13.3'],
    maxReverseStutterRatio: 0.050,
    germlineMutationRate10k: 0.60,
    stepwiseMutationR: 0.950,
    isCodisCore: true,
    dyeChannelDefault: 'YELLOW',
  },
  TPOX: {
    locusName: 'TPOX',
    cytogeneticBand: '2p25.3',
    grch38Coords: 'chr2:1,489,000-1,489,200',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[AATG]n',
    observedAlleleSpectrum: ['4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.050,
    germlineMutationRate10k: 0.50,
    stepwiseMutationR: 0.960,
    isCodisCore: true,
    dyeChannelDefault: 'YELLOW',
  },
  D1S1656: {
    locusName: 'D1S1656',
    cytogeneticBand: '1q42.2',
    grch38Coords: 'chr1:230,784,100-230,784,400',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Complex',
    canonicalMotifSequence: 'CCTA [TCTA]n TCA [TCTA]m',
    observedAlleleSpectrum: [
      '9', '10', '11', '12', '13', '14', '14.3', '15', '15.3', '16', '16.3', '17',
      '17.3', '18', '18.3', '19', '19.3', '20.3',
    ],
    documentedMicrovariants: ['14.3', '15.3', '16.3', '17.3', '18.3', '19.3', '20.3'],
    maxReverseStutterRatio: 0.130,
    germlineMutationRate10k: 2.20,
    stepwiseMutationR: 0.830,
    isCodisCore: true,
    dyeChannelDefault: 'BLUE',
  },
  D2S441: {
    locusName: 'D2S441',
    cytogeneticBand: '2p14',
    grch38Coords: 'chr2:68,011,200-68,011,450',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Compound',
    canonicalMotifSequence: '[TCTA]n TCA [TCTA]m',
    observedAlleleSpectrum: ['8', '9', '10', '10.3', '11', '11.3', '12', '12.3', '13', '13.3', '14', '15', '16', '17'],
    documentedMicrovariants: ['10.3', '11.3', '12.3', '13.3'],
    maxReverseStutterRatio: 0.080,
    germlineMutationRate10k: 1.10,
    stepwiseMutationR: 0.890,
    isCodisCore: true,
    dyeChannelDefault: 'RED',
  },
  D2S1338: {
    locusName: 'D2S1338',
    cytogeneticBand: '2q35',
    grch38Coords: 'chr2:218,058,100-218,058,450',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Compound',
    canonicalMotifSequence: '[GGAA]n [GGCA]m',
    observedAlleleSpectrum: ['15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.110,
    germlineMutationRate10k: 1.60,
    stepwiseMutationR: 0.870,
    isCodisCore: true,
    dyeChannelDefault: 'BLUE',
  },
  D10S1248: {
    locusName: 'D10S1248',
    cytogeneticBand: '10q26.3',
    grch38Coords: 'chr10:130,562,100-130,562,350',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[GGAA]n',
    observedAlleleSpectrum: ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.090,
    germlineMutationRate10k: 0.90,
    stepwiseMutationR: 0.930,
    isCodisCore: true,
    dyeChannelDefault: 'RED',
  },
  D12S391: {
    locusName: 'D12S391',
    cytogeneticBand: '12p13.2',
    grch38Coords: 'chr12:12,341,200-12,341,550',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Compound',
    canonicalMotifSequence: '[AGAT]n [AGAC]m',
    observedAlleleSpectrum: [
      '14', '15', '16', '17', '17.3', '18', '18.3', '19', '19.3', '20', '20.3',
      '21', '22', '23', '24', '25', '26', '27',
    ],
    documentedMicrovariants: ['17.3', '18.3', '19.3', '20.3'],
    maxReverseStutterRatio: 0.140,
    germlineMutationRate10k: 2.50,
    stepwiseMutationR: 0.810,
    isCodisCore: true,
    dyeChannelDefault: 'GREEN',
  },
  D19S433: {
    locusName: 'D19S433',
    cytogeneticBand: '19q12',
    grch38Coords: 'chr19:30,417,100-30,417,350',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Compound',
    canonicalMotifSequence: '[AAGG]n [TAGG]m',
    observedAlleleSpectrum: ['9', '10', '11', '12', '12.2', '13', '13.2', '14', '14.2', '15', '15.2', '16', '16.2', '17.2'],
    documentedMicrovariants: ['12.2', '13.2', '14.2', '15.2', '16.2', '17.2'],
    maxReverseStutterRatio: 0.100,
    germlineMutationRate10k: 1.20,
    stepwiseMutationR: 0.880,
    isCodisCore: true,
    dyeChannelDefault: 'YELLOW',
  },
  D22S1045: {
    locusName: 'D22S1045',
    cytogeneticBand: '22q12.3',
    grch38Coords: 'chr22:35,789,100-35,789,300',
    repeatUnitClass: 'Trinucleotide',
    repeatUnitSizeBp: 3,
    motifClass: 'Simple',
    canonicalMotifSequence: '[ATT]n',
    observedAlleleSpectrum: ['7', '8', '9', '10', '11', '12', '13', '14', '14.1', '15', '15.1', '16', '17', '18', '19', '20'],
    documentedMicrovariants: ['14.1', '15.1'],
    maxReverseStutterRatio: 0.150,
    germlineMutationRate10k: 1.80,
    stepwiseMutationR: 0.780,
    isCodisCore: true,
    dyeChannelDefault: 'RED',
  },
  SE33: {
    locusName: 'SE33',
    cytogeneticBand: '6q14.2',
    grch38Coords: 'chr6:88,270,100-88,270,850',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Complex',
    canonicalMotifSequence: '[AAAG]n AG [AAAG]m',
    observedAlleleSpectrum: [
      '4.2', '9', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22',
      '22.2', '23.2', '24.2', '25.2', '26.2', '27.2', '28.2', '29.2', '30.2', '31.2',
      '32.2', '33.2', '34.2', '35.2', '36.2', '37',
    ],
    documentedMicrovariants: ['4.2', '22.2', '23.2', '24.2', '25.2', '26.2', '27.2', '28.2', '29.2', '30.2', '31.2', '32.2', '33.2', '34.2', '35.2', '36.2'],
    maxReverseStutterRatio: 0.160,
    germlineMutationRate10k: 6.40,
    stepwiseMutationR: 0.700,
    isCodisCore: false,
    dyeChannelDefault: 'PURPLE',
  },
  'Penta D': {
    locusName: 'Penta D',
    cytogeneticBand: '21q22.3',
    grch38Coords: 'chr21:43,780,100-43,780,450',
    repeatUnitClass: 'Pentanucleotide',
    repeatUnitSizeBp: 5,
    motifClass: 'Simple',
    canonicalMotifSequence: '[AAAGA]n',
    observedAlleleSpectrum: ['2.2', '3.2', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17'],
    documentedMicrovariants: ['2.2', '3.2'],
    maxReverseStutterRatio: 0.040,
    germlineMutationRate10k: 1.00,
    stepwiseMutationR: 0.940,
    isCodisCore: false,
    dyeChannelDefault: 'PURPLE',
  },
  'Penta E': {
    locusName: 'Penta E',
    cytogeneticBand: '15q26.2',
    grch38Coords: 'chr15:96,732,100-96,732,550',
    repeatUnitClass: 'Pentanucleotide',
    repeatUnitSizeBp: 5,
    motifClass: 'Simple',
    canonicalMotifSequence: '[AAAGA]n',
    observedAlleleSpectrum: [
      '5', '6', '7', '8', '9', '10', '10.4', '11', '12', '13', '14', '15', '16', '17',
      '18', '19', '20', '21', '22', '23', '24',
    ],
    documentedMicrovariants: ['10.4'],
    maxReverseStutterRatio: 0.040,
    germlineMutationRate10k: 1.20,
    stepwiseMutationR: 0.930,
    isCodisCore: false,
    dyeChannelDefault: 'PURPLE',
  },
  Amelogenin: {
    locusName: 'Amelogenin',
    cytogeneticBand: 'Xp22.2 / Yp11.2',
    grch38Coords: 'X:11,210,100-11,210,210 / Y:6,710,100-6,710,220',
    repeatUnitClass: 'Non-STR Indel',
    repeatUnitSizeBp: 6,
    motifClass: 'Dimorphic',
    canonicalMotifSequence: 'Intron 1 Indel (6-bp Y insertion)',
    observedAlleleSpectrum: ['X', 'Y'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.000,
    germlineMutationRate10k: 0.00,
    stepwiseMutationR: 1.000,
    isCodisCore: true,
    dyeChannelDefault: 'RED',
  },
  DYS391: {
    locusName: 'DYS391',
    cytogeneticBand: 'Yq11.22',
    grch38Coords: 'chrY:14,130,000-14,130,200',
    repeatUnitClass: 'Tetranucleotide',
    repeatUnitSizeBp: 4,
    motifClass: 'Simple',
    canonicalMotifSequence: '[GATA]n',
    observedAlleleSpectrum: ['7', '8', '9', '10', '11', '12', '13'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.080,
    germlineMutationRate10k: 2.40,
    stepwiseMutationR: 0.880,
    isCodisCore: false,
    dyeChannelDefault: 'RED',
  },
  SRY: {
    locusName: 'SRY',
    cytogeneticBand: 'Yp11.2',
    grch38Coords: 'chrY:2,780,000-2,780,500',
    repeatUnitClass: 'Non-STR Indel',
    repeatUnitSizeBp: 0,
    motifClass: 'Monomorphic',
    canonicalMotifSequence: 'Single-copy Y gene confirmation',
    observedAlleleSpectrum: ['Present', 'Absent'],
    documentedMicrovariants: [],
    maxReverseStutterRatio: 0.000,
    germlineMutationRate10k: 0.00,
    stepwiseMutationR: 1.000,
    isCodisCore: false,
    dyeChannelDefault: 'RED',
  },
};

export const MICROVARIANT_MUTATIONAL_CATALOG: Record<string, MicrovariantDetail[]> = {
  TH01: [
    {
      locusName: 'TH01',
      fractionalAllele: '9.3',
      integerBaseRepeat: 9,
      fractionalOffset: 0.3,
      deltaBp: 3,
      alternateDeltaBp: -1,
      sequenceRepresentation: '[AATG]6 ATG [AATG]3',
      etiologyDescription: 'Single-base deletion of Adenine in 7th unit of [AATG]10, creating an ATG trinucleotide insert',
      etiologyClass: 'Single-base deletion in core repeat unit',
    },
    {
      locusName: 'TH01',
      fractionalAllele: '8.3',
      integerBaseRepeat: 8,
      fractionalOffset: 0.3,
      deltaBp: 3,
      alternateDeltaBp: -1,
      sequenceRepresentation: '[AATG]5 ATG [AATG]3',
      etiologyDescription: 'Single-base deletion within 9-repeat array',
      etiologyClass: 'Single-base deletion in core repeat unit',
    },
  ],
  FGA: [
    {
      locusName: 'FGA',
      fractionalAllele: '21.2',
      integerBaseRepeat: 21,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[GGAA]2 GGAG [AAAG]n AG [AAAG]m AGAA AAAA [GAAA]3',
      etiologyDescription: 'Dinucleotide AG insertion/deletion within the variable AAAG repeat block',
      etiologyClass: 'Dinucleotide insertion/deletion',
    },
    {
      locusName: 'FGA',
      fractionalAllele: '22.2',
      integerBaseRepeat: 22,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[GGAA]2 GGAG [AAAG]n AG [AAAG]m AGAA AAAA [GAAA]3',
      etiologyDescription: 'Slipped-strand mispairing inducing a 2-bp AG deletion within AAAG array',
      etiologyClass: 'Dinucleotide insertion/deletion',
    },
    {
      locusName: 'FGA',
      fractionalAllele: '26.2',
      integerBaseRepeat: 26,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[GGAA]2 GGAG [AAAG]n AG [AAAG]m AGAA AAAA [GAAA]3',
      etiologyDescription: 'Internal AG dinucleotide unit insertion in high-molecular weight FGA allele',
      etiologyClass: 'Dinucleotide insertion/deletion',
    },
  ],
  D21S11: [
    {
      locusName: 'D21S11',
      fractionalAllele: '28.2',
      integerBaseRepeat: 28,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[TCTA]n [TCTG]m [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCTA [TCTG]p [TCTA]q',
      etiologyDescription: 'Retention of an internal non-repeating TA dinucleotide invariant block',
      etiologyClass: 'Dinucleotide insertion/deletion',
    },
    {
      locusName: 'D21S11',
      fractionalAllele: '29.2',
      integerBaseRepeat: 29,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[TCTA]n [TCTG]m [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCTA [TCTG]p [TCTA]q',
      etiologyDescription: 'Complex motif shift with internal TA insert adjacent to TCA linker',
      etiologyClass: 'Dinucleotide insertion/deletion',
    },
    {
      locusName: 'D21S11',
      fractionalAllele: '31.2',
      integerBaseRepeat: 31,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[TCTA]n [TCTG]m [TCTA]3 TA [TCTA]3 TCA [TCTA]2 TCTA [TCTG]p [TCTA]q',
      etiologyDescription: 'Common European/African 31.2 allele with TA dinucleotide insertion',
      etiologyClass: 'Dinucleotide insertion/deletion',
    },
  ],
  D1S1656: [
    {
      locusName: 'D1S1656',
      fractionalAllele: '14.3',
      integerBaseRepeat: 14,
      fractionalOffset: 0.3,
      deltaBp: 3,
      alternateDeltaBp: -1,
      sequenceRepresentation: 'CCTA [TCTA]n TCA [TCTA]m',
      etiologyDescription: 'Inclusion of a 3-bp TCA trinucleotide unit situated between CCTA and TCTA blocks',
      etiologyClass: 'Trinucleotide motif insertion',
    },
    {
      locusName: 'D1S1656',
      fractionalAllele: '17.3',
      integerBaseRepeat: 17,
      fractionalOffset: 0.3,
      deltaBp: 3,
      alternateDeltaBp: -1,
      sequenceRepresentation: 'CCTA [TCTA]n TCA [TCTA]m',
      etiologyDescription: 'High-frequency European 17.3 allele with TCA linker insertion',
      etiologyClass: 'Trinucleotide motif insertion',
    },
  ],
  D2S441: [
    {
      locusName: 'D2S441',
      fractionalAllele: '11.3',
      integerBaseRepeat: 11,
      fractionalOffset: 0.3,
      deltaBp: 3,
      alternateDeltaBp: -1,
      sequenceRepresentation: '[TCTA]n TCA [TCTA]m',
      etiologyDescription: 'Diagnostic 11.3 microvariant with internal TCA trinucleotide insertion',
      etiologyClass: 'Trinucleotide motif insertion',
    },
  ],
  D19S433: [
    {
      locusName: 'D19S433',
      fractionalAllele: '13.2',
      integerBaseRepeat: 13,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[AAGG]n AG [TAGG]m',
      etiologyDescription: 'Compound dinucleotide AG bridge retention in 13-repeat allele',
      etiologyClass: 'Dinucleotide insertion/deletion',
    },
    {
      locusName: 'D19S433',
      fractionalAllele: '14.2',
      integerBaseRepeat: 14,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[AAGG]n AG [TAGG]m',
      etiologyDescription: 'High-frequency African American 14.2 allele with AG dinucleotide bridge',
      etiologyClass: 'Dinucleotide insertion/deletion',
    },
  ],
  SE33: [
    {
      locusName: 'SE33',
      fractionalAllele: '26.2',
      integerBaseRepeat: 26,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[AAAG]n AG [AAAG]m',
      etiologyDescription: 'Complex AAAG array with dinucleotide AG insert',
      etiologyClass: 'Complex array hypervariable frameshift',
    },
    {
      locusName: 'SE33',
      fractionalAllele: '28.2',
      integerBaseRepeat: 28,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[AAAG]n AG [AAAG]m',
      etiologyDescription: 'High-frequency European 28.2 allele with complex dinucleotide frameshift',
      etiologyClass: 'Complex array hypervariable frameshift',
    },
  ],
  D12S391: [
    {
      locusName: 'D12S391',
      fractionalAllele: '18.3',
      integerBaseRepeat: 18,
      fractionalOffset: 0.3,
      deltaBp: 3,
      alternateDeltaBp: -1,
      sequenceRepresentation: '[AGAT]n AGA [AGAC]m',
      etiologyDescription: 'Single-base deletion boundary linker in 18-repeat allele',
      etiologyClass: 'Single-base deletion in core repeat unit',
    },
  ],
  'Penta D': [
    {
      locusName: 'Penta D',
      fractionalAllele: '2.2',
      integerBaseRepeat: 2,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: -3,
      sequenceRepresentation: '[AAAGA]n AA',
      etiologyDescription: 'Partial pentanucleotide repeat collapse resulting in a residual AA dinucleotide unit',
      etiologyClass: 'Partial repeat collapse / residual unit',
    },
  ],
  D22S1045: [
    {
      locusName: 'D22S1045',
      fractionalAllele: '14.1',
      integerBaseRepeat: 14,
      fractionalOffset: 0.1,
      deltaBp: 1,
      alternateDeltaBp: -2,
      sequenceRepresentation: '[ATT]n A',
      etiologyDescription: 'Single-base insertion following a trinucleotide array yielding a fractional +1 bp displacement',
      etiologyClass: 'Single-base insertion',
    },
  ],
  D7S820: [
    {
      locusName: 'D7S820',
      fractionalAllele: '9.1',
      integerBaseRepeat: 9,
      fractionalOffset: 0.1,
      deltaBp: 1,
      alternateDeltaBp: null,
      sequenceRepresentation: '[GATA]n T',
      etiologyDescription: 'Flanking single-base insertion in 9-repeat allele',
      etiologyClass: 'Single-base insertion',
    },
  ],
  D18S51: [
    {
      locusName: 'D18S51',
      fractionalAllele: '10.2',
      integerBaseRepeat: 10,
      fractionalOffset: 0.2,
      deltaBp: 2,
      alternateDeltaBp: null,
      sequenceRepresentation: '[AGAA]n AG',
      etiologyDescription: 'Dinucleotide AG addition within simple tetranucleotide repeat structure',
      etiologyClass: 'Dinucleotide insertion/deletion',
    },
  ],
  'Penta E': [
    {
      locusName: 'Penta E',
      fractionalAllele: '10.4',
      integerBaseRepeat: 10,
      fractionalOffset: 0.4,
      deltaBp: 4,
      alternateDeltaBp: -1,
      sequenceRepresentation: '[AAAGA]n AAAG',
      etiologyDescription: 'Single base deletion from pentanucleotide unit resulting in a 4-bp residual fragment',
      etiologyClass: 'Single-base deletion in core repeat unit',
    },
  ],
};

export class StrLocusRegistryEngine {
  public static getLocusMetadata(locusName: string): StrLocusMetadata | null {
    const trimmed = locusName.trim();
    if (STR_LOCUS_24_MASTER_REGISTRY[trimmed]) {
      return STR_LOCUS_24_MASTER_REGISTRY[trimmed];
    }
    const lower = trimmed.toLowerCase();
    for (const [key, val] of Object.entries(STR_LOCUS_24_MASTER_REGISTRY)) {
      if (key.toLowerCase() === lower) {
        return val;
      }
    }
    return null;
  }

  public static isMicrovariant(arg1: string, arg2?: string): any {
    if (arg2 !== undefined) {
      // Called with (locusName, alleleStr) -> returns MicrovariantDetail | null
      return this.getMicrovariantDetails(arg1, arg2);
    }
    // Called with (alleleStr) -> returns boolean
    const clean = arg1.trim().replace(/[[\]]/g, '');
    if (['X', 'Y', '0', 'Present', 'Absent', '?', 'OL'].includes(clean)) return false;
    const val = parseFloat(clean);
    return !isNaN(val) && !Number.isInteger(val);
  }

  public static parseRepeatAndFraction(alleleStr: string): { integerPart: number; fractionPart: number } {
    const clean = alleleStr.trim().replace(/[[\]]/g, '');
    const val = parseFloat(clean);
    if (isNaN(val)) return { integerPart: 0, fractionPart: 0 };
    const integerPart = Math.floor(val);
    const fractionPart = Math.round((val - integerPart) * 10) / 10;
    return { integerPart, fractionPart };
  }

  public static getMicrovariantDetails(locusName: string, alleleStr: string): MicrovariantDetail | null {
    const meta = this.getLocusMetadata(locusName);
    if (!meta) return null;
    const clean = alleleStr.trim().replace(/[[\]]/g, '');
    const variants = MICROVARIANT_MUTATIONAL_CATALOG[meta.locusName] || [];
    const found = variants.find((v) => v.fractionalAllele === clean);
    if (found) return found;

    if (this.isMicrovariant(clean)) {
      const { integerPart, fractionPart } = this.parseRepeatAndFraction(clean);
      const deltaBp = Math.round(fractionPart * 10);
      return {
        locusName: meta.locusName,
        fractionalAllele: clean,
        integerBaseRepeat: integerPart,
        fractionalOffset: fractionPart,
        deltaBp,
        alternateDeltaBp: meta.repeatUnitSizeBp > 0 ? deltaBp - meta.repeatUnitSizeBp : null,
        sequenceRepresentation: `${meta.canonicalMotifSequence} (+${deltaBp}bp)`,
        etiologyDescription: `Fractional repeat allele with +${deltaBp} bp insertion relative to repeat ${integerPart}`,
        etiologyClass: deltaBp === 1 ? 'Single-base insertion' : 'Dinucleotide insertion/deletion',
      };
    }
    return null;
  }

  public static calculateAlleleSizeBp(locusName: string, alleleStr: string, baseOffset: number = 60.0): number {
    const meta = this.getLocusMetadata(locusName);
    const clean = alleleStr.trim().replace(/[[\]]/g, '');
    if (locusName.toLowerCase() === 'amelogenin' || (meta && meta.repeatUnitClass === 'Non-STR Indel')) {
      if (clean.toUpperCase() === 'X') return 106.0;
      if (clean.toUpperCase() === 'Y') return 112.0;
      if (clean.toLowerCase() === 'present') return 517.0;
      return baseOffset;
    }

    if (!meta) return baseOffset;

    const mv = this.getMicrovariantDetails(locusName, clean);
    if (mv) {
      return baseOffset + mv.integerBaseRepeat * meta.repeatUnitSizeBp + mv.deltaBp;
    }

    const num = parseFloat(clean);
    if (!isNaN(num)) {
      return baseOffset + num * meta.repeatUnitSizeBp;
    }
    return baseOffset;
  }

  public static calculateCeBasePairSize(locusName: string, alleleStr: string, baseOffset: number = 60.0): number {
    return this.calculateAlleleSizeBp(locusName, alleleStr, baseOffset);
  }

  public static getAllLociNames(): string[] {
    return Object.keys(STR_LOCUS_24_MASTER_REGISTRY);
  }

  public static getCodisCoreLociNames(): string[] {
    return Object.entries(STR_LOCUS_24_MASTER_REGISTRY)
      .filter(([_, v]) => v.isCodisCore && v.repeatUnitClass !== 'Non-STR Indel')
      .map(([k]) => k);
  }

  public static getMicrovariantLociNames(): string[] {
    return Object.keys(MICROVARIANT_MUTATIONAL_CATALOG);
  }
}
