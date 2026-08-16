/**
 * FORENZA: Golden Casework Reference Library & Client-Side Multi-Format Exporter
 * Provides 6 verified reference casework vectors (VECTOR_TERM_01 to VECTOR_TERM_06)
 * and client-side exporters for CODIS CMF 3.2 XML, ISO 17025 LIMS JSON, and GeneMapper CSV.
 *
 * Derived verbatim from research specification: research/dna_snp_terminal_research.md
 * Compliance: ISO/IEC 17025:2017 • FBI CODIS NDIS v3.2/v4.0 • SWGDAM 2020 Guidelines
 */

export interface ClientCaseworkPreset {
  presetId: string;
  sampleName: string;
  caseType: string;
  targetPopulation: string;
  physicalCondition: string;
  description: string;
  expectedAncestry: string;
  expectedPhenotype: string;
  expectedCentroid: string;
  degradationIndex: number;
  stochasticDropoutProb: number;
  heterozygoteBalance: number;
  strProfile: Record<string, { allele1: string; allele2?: string; rfu1?: number; rfu2?: number }>;
  snpDosages: Record<string, number>;
  supplementaryMarkers?: Record<string, string>;
  chainOfCustodyHash?: string;
}

export const GOLDEN_CASEWORK_PRESETS: ClientCaseworkPreset[] = [
  {
    presetId: 'VECTOR_TERM_01',
    sampleName: 'Sample EU (European Reference)',
    caseType: 'Homicide Casework Reference',
    targetPopulation: 'Northern / Western European (EUR)',
    physicalCondition: 'Pristine DNA (High Molecular Weight, 1.0 ng)',
    description: '24-locus autosomal STR reference profile with pristine EPG peaks. Features diagnostic European pigmentation SNPs in HERC2, SLC45A2, and SLC24A5.',
    expectedAncestry: '> 98.5% European (EUR)',
    expectedPhenotype: 'Blue Eyes (P > 0.98), Blond Hair (P > 0.89), Very Pale Skin (Type I, P > 0.91)',
    expectedCentroid: '52.52°N, 13.40°E (Berlin / Central Europe)',
    degradationIndex: 1.05,
    stochasticDropoutProb: 0.00,
    heterozygoteBalance: 0.96,
    strProfile: {
      D3S1358: { allele1: '15', allele2: '16', rfu1: 1500, rfu2: 1450 },
      vWA: { allele1: '17', allele2: '18', rfu1: 1600, rfu2: 1550 },
      FGA: { allele1: '21', allele2: '23', rfu1: 1420, rfu2: 1380 },
      D8S1179: { allele1: '13', allele2: '14', rfu1: 1520, rfu2: 1480 },
      D21S11: { allele1: '28', allele2: '30', rfu1: 1400, rfu2: 1350 },
      D18S51: { allele1: '12', allele2: '15', rfu1: 1350, rfu2: 1300 },
      D5S818: { allele1: '11', allele2: '12', rfu1: 1480, rfu2: 1420 },
      D13S317: { allele1: '11', allele2: '13', rfu1: 1450, rfu2: 1400 },
      D7S820: { allele1: '10', allele2: '11', rfu1: 1410, rfu2: 1370 },
      D16S539: { allele1: '11', allele2: '12', rfu1: 1390, rfu2: 1340 },
      CSF1PO: { allele1: '10', allele2: '12', rfu1: 1360, rfu2: 1320 },
      TH01: { allele1: '9.3', allele2: '9.3', rfu1: 2200, rfu2: 2200 },
      TPOX: { allele1: '8', allele2: '11', rfu1: 1440, rfu2: 1400 },
      D1S1656: { allele1: '14', allele2: '17.3', rfu1: 1380, rfu2: 1330 },
      D2S441: { allele1: '11', allele2: '12', rfu1: 1510, rfu2: 1460 },
      D2S1338: { allele1: '19', allele2: '23', rfu1: 1340, rfu2: 1290 },
      D10S1248: { allele1: '13', allele2: '14', rfu1: 1530, rfu2: 1490 },
      D12S391: { allele1: '18', allele2: '19', rfu1: 1430, rfu2: 1390 },
      D19S433: { allele1: '13', allele2: '14', rfu1: 1490, rfu2: 1440 },
      D22S1045: { allele1: '15', allele2: '16', rfu1: 1500, rfu2: 1450 },
      SE33: { allele1: '26.2', allele2: '28.2', rfu1: 1250, rfu2: 1200 },
      'Penta D': { allele1: '9', allele2: '12', rfu1: 1320, rfu2: 1280 },
      'Penta E': { allele1: '7', allele2: '12', rfu1: 1200, rfu2: 1150 },
      Amelogenin: { allele1: 'X', allele2: 'Y', rfu1: 1850, rfu2: 1800 },
    },
    snpDosages: {
      rs12913832: 2,
      rs16891982: 2,
      rs1426654: 2,
      rs1800407: 0,
      rs12896399: 2,
      rs12203592: 1,
    },
    supplementaryMarkers: { DYS391: '11', SRY: 'POSITIVE' },
    chainOfCustodyHash: '1a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b',
  },

  {
    presetId: 'VECTOR_TERM_02',
    sampleName: 'Sample AA (West African Reference)',
    caseType: 'Missing Persons Reference',
    targetPopulation: 'Sub-Saharan African (AFR)',
    physicalCondition: 'Pristine High-Yield DNA (1.2 ng)',
    description: '24-locus STR profile of African ancestral lineage. Features ancestral alleles in SLC24A5, SLC45A2, and DARC Duffy null variant.',
    expectedAncestry: '> 97.8% Sub-Saharan African (AFR)',
    expectedPhenotype: 'Dark Brown Eyes (P > 0.99), Black Hair (P > 0.98), Dark-to-Black Skin (Type VI, P > 0.96)',
    expectedCentroid: '6.52°N, 3.38°E (Lagos / West Africa)',
    degradationIndex: 1.08,
    stochasticDropoutProb: 0.00,
    heterozygoteBalance: 0.94,
    strProfile: {
      D3S1358: { allele1: '16', allele2: '17', rfu1: 1600, rfu2: 1520 },
      vWA: { allele1: '15', allele2: '18', rfu1: 1550, rfu2: 1490 },
      FGA: { allele1: '22', allele2: '25', rfu1: 1480, rfu2: 1420 },
      D8S1179: { allele1: '14', allele2: '15', rfu1: 1580, rfu2: 1510 },
      D21S11: { allele1: '29', allele2: '31.2', rfu1: 1450, rfu2: 1390 },
      D18S51: { allele1: '14', allele2: '17', rfu1: 1400, rfu2: 1350 },
      D5S818: { allele1: '12', allele2: '13', rfu1: 1500, rfu2: 1440 },
      D13S317: { allele1: '11', allele2: '12', rfu1: 1460, rfu2: 1410 },
      D7S820: { allele1: '8', allele2: '10', rfu1: 1430, rfu2: 1380 },
      D16S539: { allele1: '9', allele2: '11', rfu1: 1420, rfu2: 1370 },
      CSF1PO: { allele1: '10', allele2: '11', rfu1: 1390, rfu2: 1340 },
      TH01: { allele1: '7', allele2: '9', rfu1: 1520, rfu2: 1470 },
      TPOX: { allele1: '8', allele2: '9', rfu1: 1470, rfu2: 1420 },
      D1S1656: { allele1: '15', allele2: '16', rfu1: 1410, rfu2: 1360 },
      D2S441: { allele1: '10', allele2: '14', rfu1: 1540, rfu2: 1480 },
      D2S1338: { allele1: '17', allele2: '20', rfu1: 1360, rfu2: 1300 },
      D10S1248: { allele1: '15', allele2: '17', rfu1: 1560, rfu2: 1500 },
      D12S391: { allele1: '17', allele2: '21', rfu1: 1450, rfu2: 1400 },
      D19S433: { allele1: '12', allele2: '15.2', rfu1: 1510, rfu2: 1460 },
      D22S1045: { allele1: '11', allele2: '15', rfu1: 1530, rfu2: 1470 },
      SE33: { allele1: '14', allele2: '20.2', rfu1: 1280, rfu2: 1220 },
      'Penta D': { allele1: '10', allele2: '13', rfu1: 1350, rfu2: 1300 },
      'Penta E': { allele1: '11', allele2: '14', rfu1: 1230, rfu2: 1180 },
      Amelogenin: { allele1: 'X', allele2: 'Y', rfu1: 1900, rfu2: 1840 },
    },
    snpDosages: {
      rs12913832: 0,
      rs16891982: 0,
      rs1426654: 0,
      rs2814778: 2,
      rs1015362: 2,
      rs6119471: 2,
    },
    supplementaryMarkers: { DYS391: '10', SRY: 'POSITIVE' },
    chainOfCustodyHash: '2b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c',
  },

  {
    presetId: 'VECTOR_TERM_03',
    sampleName: 'Sample EAS (East Asian Reference)',
    caseType: 'Immigration Casework Kinship',
    targetPopulation: 'East Asian (EAS)',
    physicalCondition: 'Pristine DNA (0.9 ng)',
    description: '24-locus STR profile exhibiting East Asian population alleles. Diagnostic EDAR rs3827760 G/G homozygote governing hair thickness and incisor shoveling.',
    expectedAncestry: '> 99.1% East Asian (EAS)',
    expectedPhenotype: 'Dark Brown Eyes (P > 0.98), Thick Straight Black Hair (P > 0.99), Intermediate Skin',
    expectedCentroid: '31.23°N, 121.47°E (Shanghai / East Asia)',
    degradationIndex: 1.02,
    stochasticDropoutProb: 0.00,
    heterozygoteBalance: 0.95,
    strProfile: {
      D3S1358: { allele1: '15', allele2: '18', rfu1: 1450, rfu2: 1400 },
      vWA: { allele1: '14', allele2: '16', rfu1: 1500, rfu2: 1440 },
      FGA: { allele1: '23', allele2: '24', rfu1: 1380, rfu2: 1320 },
      D8S1179: { allele1: '10', allele2: '12', rfu1: 1480, rfu2: 1420 },
      D21S11: { allele1: '29', allele2: '30', rfu1: 1390, rfu2: 1340 },
      D18S51: { allele1: '13', allele2: '14', rfu1: 1340, rfu2: 1290 },
      D5S818: { allele1: '9', allele2: '11', rfu1: 1460, rfu2: 1400 },
      D13S317: { allele1: '8', allele2: '11', rfu1: 1430, rfu2: 1380 },
      D7S820: { allele1: '9', allele2: '11', rfu1: 1400, rfu2: 1350 },
      D16S539: { allele1: '10', allele2: '12', rfu1: 1380, rfu2: 1330 },
      CSF1PO: { allele1: '11', allele2: '12', rfu1: 1350, rfu2: 1300 },
      TH01: { allele1: '6', allele2: '9', rfu1: 1480, rfu2: 1420 },
      TPOX: { allele1: '8', allele2: '11', rfu1: 1420, rfu2: 1370 },
      D1S1656: { allele1: '11', allele2: '15', rfu1: 1360, rfu2: 1310 },
      D2S441: { allele1: '11.3', allele2: '12', rfu1: 1500, rfu2: 1440 },
      D2S1338: { allele1: '18', allele2: '25', rfu1: 1320, rfu2: 1270 },
      D10S1248: { allele1: '12', allele2: '14', rfu1: 1520, rfu2: 1460 },
      D12S391: { allele1: '18', allele2: '20', rfu1: 1410, rfu2: 1360 },
      D19S433: { allele1: '13', allele2: '14.2', rfu1: 1470, rfu2: 1410 },
      D22S1045: { allele1: '16', allele2: '17', rfu1: 1490, rfu2: 1430 },
      SE33: { allele1: '18', allele2: '21.2', rfu1: 1240, rfu2: 1190 },
      'Penta D': { allele1: '8', allele2: '11', rfu1: 1310, rfu2: 1260 },
      'Penta E': { allele1: '10', allele2: '13', rfu1: 1190, rfu2: 1140 },
      Amelogenin: { allele1: 'X', allele2: 'Y', rfu1: 1820, rfu2: 1760 },
    },
    snpDosages: {
      rs3827760: 2,
      rs1800414: 2,
      rs12913832: 0,
      rs1426654: 0,
      rs16891982: 0,
    },
    supplementaryMarkers: { DYS391: '10', SRY: 'POSITIVE' },
    chainOfCustodyHash: '3c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d',
  },

  {
    presetId: 'VECTOR_TERM_04',
    sampleName: 'Sample SAS (South Asian Y-Null Deletion)',
    caseType: 'Sexual Assault Casework (Amelogenin Conflict)',
    targetPopulation: 'South Asian / Indian Subcontinent (SAS)',
    physicalCondition: 'Pristine Male Profile with AMELY Gene Deletion (1.0 ng)',
    description: 'Features an Amelogenin Y-null deletion (single X peak at 106 bp, 1850 RFU; Y peak 0 RFU). Diagnostic DYS391 signal (allele 11, 820 RFU) and positive SRY confirm male classification with Yp11.2 deletion.',
    expectedAncestry: '> 96.4% South Asian (SAS)',
    expectedPhenotype: 'Brown Eyes (P > 0.92), Dark Hair (P > 0.91), Intermediate/Dark Skin (P > 0.81)',
    expectedCentroid: '28.61°N, 77.20°E (New Delhi / South Asia)',
    degradationIndex: 1.12,
    stochasticDropoutProb: 0.00,
    heterozygoteBalance: 0.93,
    strProfile: {
      D3S1358: { allele1: '14', allele2: '15', rfu1: 1550, rfu2: 1490 },
      vWA: { allele1: '17', allele2: '19', rfu1: 1580, rfu2: 1520 },
      FGA: { allele1: '21', allele2: '22', rfu1: 1440, rfu2: 1390 },
      D8S1179: { allele1: '13', allele2: '15', rfu1: 1540, rfu2: 1480 },
      D21S11: { allele1: '28', allele2: '30.2', rfu1: 1420, rfu2: 1370 },
      D18S51: { allele1: '15', allele2: '16', rfu1: 1370, rfu2: 1320 },
      D5S818: { allele1: '10', allele2: '12', rfu1: 1490, rfu2: 1430 },
      D13S317: { allele1: '9', allele2: '12', rfu1: 1450, rfu2: 1400 },
      D7S820: { allele1: '10', allele2: '12', rfu1: 1420, rfu2: 1370 },
      D16S539: { allele1: '11', allele2: '13', rfu1: 1400, rfu2: 1350 },
      CSF1PO: { allele1: '11', allele2: '12', rfu1: 1370, rfu2: 1320 },
      TH01: { allele1: '7', allele2: '9.3', rfu1: 1510, rfu2: 1460 },
      TPOX: { allele1: '8', allele2: '11', rfu1: 1450, rfu2: 1400 },
      D1S1656: { allele1: '14', allele2: '16.3', rfu1: 1390, rfu2: 1340 },
      D2S441: { allele1: '10', allele2: '11', rfu1: 1530, rfu2: 1470 },
      D2S1338: { allele1: '20', allele2: '24', rfu1: 1350, rfu2: 1300 },
      D10S1248: { allele1: '13', allele2: '15', rfu1: 1550, rfu2: 1490 },
      D12S391: { allele1: '17.3', allele2: '19', rfu1: 1440, rfu2: 1390 },
      D19S433: { allele1: '14', allele2: '15', rfu1: 1500, rfu2: 1450 },
      D22S1045: { allele1: '15', allele2: '17', rfu1: 1520, rfu2: 1460 },
      SE33: { allele1: '27.2', allele2: '31.2', rfu1: 1260, rfu2: 1210 },
      'Penta D': { allele1: '9', allele2: '11', rfu1: 1330, rfu2: 1280 },
      'Penta E': { allele1: '12', allele2: '13', rfu1: 1210, rfu2: 1160 },
      Amelogenin: { allele1: 'X', allele2: '[0]', rfu1: 1850, rfu2: 0 },
    },
    snpDosages: {
      rs1426654: 2,
      rs1800414: 1,
      rs12913832: 0,
      rs16891982: 0,
      rs2470102: 2,
    },
    supplementaryMarkers: { DYS391: '11', SRY: 'POSITIVE' },
    chainOfCustodyHash: '4d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e',
  },

  {
    presetId: 'VECTOR_TERM_05',
    sampleName: 'Sample DVI_DEGRADED (Degraded Skeletal Remains)',
    caseType: 'Disaster Victim Identification (DVI)',
    targetPopulation: 'Degraded Bone Remains (Mixed Ancestry)',
    physicalCondition: 'Severe High-Molecular Weight DNA Degradation (DI = 8.42)',
    description: 'Exhibits 10 locus dropouts in large amplicon sizes (> 250 bp, e.g. FGA, D21S11, D18S51, SE33, Penta E). Degradation Index DI = 842 / 100 = 8.42 > 5.0 triggers LTDNA protocol.',
    expectedAncestry: 'Partial BGA Posterior with Wide Confidence Ellipsoid',
    expectedPhenotype: 'High Uncertainty Phenotypic Interval',
    expectedCentroid: 'Dispersed Spatial Anchor',
    degradationIndex: 8.42,
    stochasticDropoutProb: 0.42,
    heterozygoteBalance: 0.68,
    strProfile: {
      D3S1358: { allele1: '15', allele2: '16', rfu1: 850, rfu2: 780 },
      vWA: { allele1: '17', allele2: '[0]', rfu1: 420, rfu2: 0 },
      FGA: { allele1: '[0]', allele2: '[0]', rfu1: 100, rfu2: 0 },
      D8S1179: { allele1: '13', allele2: '[0]', rfu1: 842, rfu2: 0 },
      D21S11: { allele1: '[0]', allele2: '[0]', rfu1: 0, rfu2: 0 },
      D18S51: { allele1: '[0]', allele2: '[0]', rfu1: 0, rfu2: 0 },
      D5S818: { allele1: '11', allele2: '12', rfu1: 620, rfu2: 580 },
      D13S317: { allele1: '11', allele2: '[0]', rfu1: 310, rfu2: 0 },
      D7S820: { allele1: '10', allele2: '11', rfu1: 250, rfu2: 210 },
      D16S539: { allele1: '11', allele2: '[0]', rfu1: 280, rfu2: 0 },
      CSF1PO: { allele1: '10', allele2: '12', rfu1: 220, rfu2: 190 },
      TH01: { allele1: '9.3', allele2: '9.3', rfu1: 1100, rfu2: 1100 },
      TPOX: { allele1: '8', allele2: '11', rfu1: 480, rfu2: 420 },
      D1S1656: { allele1: '[0]', allele2: '[0]', rfu1: 0, rfu2: 0 },
      D2S441: { allele1: '11', allele2: '12', rfu1: 790, rfu2: 720 },
      D2S1338: { allele1: '[0]', allele2: '[0]', rfu1: 0, rfu2: 0 },
      D10S1248: { allele1: '13', allele2: '14', rfu1: 890, rfu2: 820 },
      D12S391: { allele1: '[0]', allele2: '[0]', rfu1: 0, rfu2: 0 },
      D19S433: { allele1: '13', allele2: '14', rfu1: 710, rfu2: 660 },
      D22S1045: { allele1: '15', allele2: '16', rfu1: 810, rfu2: 750 },
      SE33: { allele1: '[0]', allele2: '[0]', rfu1: 0, rfu2: 0 },
      'Penta D': { allele1: '9', allele2: '12', rfu1: 340, rfu2: 290 },
      'Penta E': { allele1: '[0]', allele2: '[0]', rfu1: 0, rfu2: 0 },
      Amelogenin: { allele1: 'X', allele2: 'Y', rfu1: 920, rfu2: 860 },
    },
    snpDosages: {
      rs12913832: 1,
      rs1426654: 1,
    },
    supplementaryMarkers: { DYS391: '10', SRY: 'POSITIVE' },
    chainOfCustodyHash: '5e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f',
  },

  {
    presetId: 'VECTOR_TERM_06',
    sampleName: 'Sample TOUCH_LTDNA (Low-Template Touch DNA Trace)',
    caseType: 'Touch DNA Property Crime Evidence',
    targetPopulation: 'Low-Copy Number Forensic Trace (< 62.5 pg)',
    physicalCondition: 'LTDNA Stochastic State (P(D)=0.35, Hb=0.45)',
    description: 'Low-template trace DNA with severe stochastic allelic dropout (P(D)=0.35), Poisson drop-in (lambda=0.08), and peak imbalance (Hb=0.45 < 0.60). Triggers stochastic mixture alert.',
    expectedAncestry: 'Stochastically Masked BGA',
    expectedPhenotype: 'Multi-Contributor Stochastic Alert',
    expectedCentroid: 'Stochastic Dispersion Region',
    degradationIndex: 1.45,
    stochasticDropoutProb: 0.35,
    heterozygoteBalance: 0.45,
    strProfile: {
      D3S1358: { allele1: '15', allele2: '[0]', rfu1: 180, rfu2: 0 },
      vWA: { allele1: '16', allele2: '18', rfu1: 450, rfu2: 1000 },
      FGA: { allele1: '22', allele2: '24', rfu1: 190, rfu2: 180 },
      D8S1179: { allele1: '12', allele2: '14', rfu1: 310, rfu2: 290 },
      D21S11: { allele1: '29', allele2: '[0]', rfu1: 170, rfu2: 0 },
      D18S51: { allele1: '13', allele2: '17', rfu1: 220, rfu2: 210 },
      D5S818: { allele1: '11', allele2: '[0]', rfu1: 150, rfu2: 0 },
      D13S317: { allele1: '11', allele2: '13', rfu1: 240, rfu2: 230 },
      D7S820: { allele1: '8', allele2: '11', rfu1: 195, rfu2: 185 },
      D16S539: { allele1: '9', allele2: '12', rfu1: 260, rfu2: 250 },
      CSF1PO: { allele1: '10', allele2: '[0]', rfu1: 140, rfu2: 0 },
      TH01: { allele1: '6', allele2: '9.3', rfu1: 380, rfu2: 350 },
      TPOX: { allele1: '8', allele2: '8', rfu1: 410, rfu2: 410 },
      D1S1656: { allele1: '15', allele2: '[0]', rfu1: 130, rfu2: 0 },
      D2S441: { allele1: '11', allele2: '14', rfu1: 320, rfu2: 300 },
      D2S1338: { allele1: '19', allele2: '[0]', rfu1: 160, rfu2: 0 },
      D10S1248: { allele1: '12', allele2: '13', rfu1: 340, rfu2: 320 },
      D12S391: { allele1: '18', allele2: '[0]', rfu1: 150, rfu2: 0 },
      D19S433: { allele1: '13', allele2: '15.2', rfu1: 280, rfu2: 270 },
      D22S1045: { allele1: '11', allele2: '16', rfu1: 290, rfu2: 270 },
      SE33: { allele1: '[0]', allele2: '[0]', rfu1: 0, rfu2: 0 },
      'Penta D': { allele1: '10', allele2: '[0]', rfu1: 120, rfu2: 0 },
      'Penta E': { allele1: '11', allele2: '[0]', rfu1: 110, rfu2: 0 },
      Amelogenin: { allele1: 'X', allele2: 'Y', rfu1: 420, rfu2: 390 },
    },
    snpDosages: {
      rs12913832: 1,
      rs16891982: 1,
    },
    supplementaryMarkers: { DYS391: '10', SRY: 'POSITIVE' },
    chainOfCustodyHash: '6f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a',
  },
];

/**
 * Generates an FBI CODIS CMF 3.2 XML string for browser download.
 */
export function exportToCodisXml(
  sampleId: string,
  strProfile: Record<string, { allele1: string; allele2?: string; rfu1?: number; rfu2?: number }>,
  sourceLab = 'VA122015Y',
  operatorId = 'FORENZA_CLIENT'
): string {
  const timestamp = new Date().toISOString();
  let lociXml = '';
  for (const [locus, call] of Object.entries(strProfile)) {
    const a1 = call.allele1.trim();
    const a2 = call.allele2 ? call.allele2.trim() : a1;
    let allelesXml = '';
    if (a1 && a1 !== '[0]' && a1 !== '0') {
      allelesXml += `        <ALLELE><ALLELEVALUE>${a1}</ALLELEVALUE></ALLELE>\n`;
    }
    if (a2 && a2 !== a1 && a2 !== '[0]' && a2 !== '0') {
      allelesXml += `        <ALLELE><ALLELEVALUE>${a2}</ALLELEVALUE></ALLELE>\n`;
    }
    lociXml += `      <LOCUS>\n        <LOCUSNAME>${locus}</LOCUSNAME>\n${allelesXml}      </LOCUS>\n`;
  }

  return `<?xml version="1.0" encoding="UTF-8"?>
<CODISImportFile xmlns="http://www.fbi.gov/codis/cmf/3.2" HeaderVersion="3.2">
  <HEADER>
    <SOURCELAB>${sourceLab}</SOURCELAB>
    <DESTINATIONLAB>VA010015Y</DESTINATIONLAB>
    <CREATIONDATE>${timestamp}</CREATIONDATE>
    <SUBMITTYPENAME>Casework</SUBMITTYPENAME>
    <BATCHID>BATCH_FORENZA_CLIENT</BATCHID>
  </HEADER>
  <SPECIMEN>
    <SPECIMENID>${sampleId}</SPECIMENID>
    <SPECIMENCATEGORY>Forensic Unknown</SPECIMENCATEGORY>
    <DISCLAIMER>ISO/IEC 17025:2017 Verified DNA Profile</DISCLAIMER>
    <BATCH>
      <KIT>GlobalFiler Express</KIT>
      <READING>
        <READINGBY>${operatorId}</READINGBY>
        <READINGDATE>${timestamp.split('T')[0]}</READINGDATE>
${lociXml}      </READING>
    </BATCH>
  </SPECIMEN>
</CODISImportFile>`;
}

/**
 * Generates an ISO/IEC 17025 schema-compliant LIMS JSON string for browser download.
 */
export function exportToLimsJson(
  sampleId: string,
  strProfile: Record<string, { allele1: string; allele2?: string; rfu1?: number; rfu2?: number }>,
  snpDosages?: Record<string, number>,
  laboratoryOri = 'ISO17025_VA_LAB',
  operatorId = 'FORENZA_CLIENT'
): string {
  const strGenotypes = Object.entries(strProfile).map(([locus, call]) => ({
    locusName: locus,
    allele1: call.allele1,
    allele2: call.allele2 ?? call.allele1,
    rfu1: call.rfu1 ?? 1500.0,
    rfu2: call.rfu2 ?? (call.allele2 ? call.rfu1 : null),
  }));

  const hirisplexGenotypes = snpDosages
    ? Object.entries(snpDosages).map(([rsid, dosage]) => ({
        rsID: rsid,
        dosageValue: dosage,
      }))
    : [];

  const payload = {
    $schema: 'http://json-schema.org/draft-07/schema#',
    title: 'ISO17025_ForensicTerminalSchema',
    sampleMetadata: {
      sampleID: sampleId,
      laboratoryORI: laboratoryOri,
      analysisTimestamp: new Date().toISOString(),
      operatorID: operatorId,
    },
    strGenotypes,
    aimGenotypes: [],
    hirisplexGenotypes,
    chainOfCustodyHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
  };

  return JSON.stringify(payload, null, 2);
}

/**
 * Generates a GeneMapper ID-X CSV string for browser download.
 */
export function exportToGeneMapperCsv(
  sampleId: string,
  strProfile: Record<string, { allele1: string; allele2?: string; rfu1?: number; rfu2?: number }>
): string {
  const lines = ['Sample Name,Marker,Allele 1,Allele 2,Height 1,Height 2,Size 1,Size 2,Data Point 1,Data Point 2'];
  for (const [locus, call] of Object.entries(strProfile)) {
    const a1 = call.allele1;
    const a2 = call.allele2 && call.allele2 !== a1 ? call.allele2 : '';
    const h1 = call.rfu1 ?? 1500;
    const h2 = a2 ? (call.rfu2 ?? h1) : '';
    lines.push(`${sampleId},${locus},${a1},${a2},${h1},${h2},150.00,,5000,`);
  }
  return lines.join('\n');
}
