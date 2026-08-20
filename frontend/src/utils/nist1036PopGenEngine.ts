/**
 * NIST 1036 Population Genetics & Dirichlet-Laplace Smoothing Engine
 * Compliant with ISO/IEC 17025:2017, SWGDAM 2020, ENFSI 2017, and NRC II Guidelines.
 * Derived verbatim from research specification: research/str_24_locus_microvariants_research.md
 */

export type NistPopulation = 'Caucasian' | 'African American' | 'Hispanic' | 'Asian' | 'Total';

export interface PopulationSampleInfo {
  n: number;
  twoN: number;
  pMin: number;
}

export const POPULATION_SAMPLE_SIZES: Record<NistPopulation, PopulationSampleInfo> = {
  Caucasian: { n: 361, twoN: 722, pMin: 5.0 / 722.0 },
  'African American': { n: 342, twoN: 684, pMin: 5.0 / 684.0 },
  Hispanic: { n: 236, twoN: 472, pMin: 5.0 / 472.0 },
  Asian: { n: 97, twoN: 194, pMin: 5.0 / 194.0 },
  Total: { n: 1036, twoN: 2072, pMin: 5.0 / 2072.0 },
};

export const NIST_1036_ALLELE_FREQUENCIES: Record<string, Record<string, Record<NistPopulation, number>>> = {
  D3S1358: {
    '14': { Caucasian: 0.1343, 'African American': 0.1067, Hispanic: 0.1038, Asian: 0.0825, Total: 0.1145 },
    '15': { Caucasian: 0.2479, 'African American': 0.2822, Hispanic: 0.3538, Asian: 0.3557, Total: 0.2934 },
    '16': { Caucasian: 0.2313, 'African American': 0.3012, Hispanic: 0.2288, Asian: 0.1701, Total: 0.2478 },
    '17': { Caucasian: 0.2119, 'African American': 0.2032, Hispanic: 0.1970, Asian: 0.2320, Total: 0.2075 },
    '18': { Caucasian: 0.1620, 'African American': 0.0819, Hispanic: 0.1017, Asian: 0.1443, Total: 0.1202 },
  },
  vWA: {
    '14': { Caucasian: 0.0873, 'African American': 0.0658, Hispanic: 0.0911, Asian: 0.0258, Total: 0.0753 },
    '15': { Caucasian: 0.1122, 'African American': 0.1988, Hispanic: 0.0826, Asian: 0.0825, Total: 0.1313 },
    '16': { Caucasian: 0.2008, 'African American': 0.1988, Hispanic: 0.2331, Asian: 0.1856, Total: 0.2061 },
    '17': { Caucasian: 0.2701, 'African American': 0.2398, Hispanic: 0.2034, Asian: 0.1495, Total: 0.2336 },
    '18': { Caucasian: 0.2091, 'African American': 0.1842, Hispanic: 0.1843, Asian: 0.2371, Total: 0.1979 },
    '19': { Caucasian: 0.1039, 'African American': 0.1608, Hispanic: 0.1377, Asian: 0.2165, Total: 0.1414 },
  },
  FGA: {
    '19': { Caucasian: 0.0609, 'African American': 0.0643, Hispanic: 0.0572, Asian: 0.1340, Total: 0.0681 },
    '20': { Caucasian: 0.1219, 'African American': 0.0687, Hispanic: 0.0572, Asian: 0.0825, Total: 0.0864 },
    '21': { Caucasian: 0.1745, 'African American': 0.1287, Hispanic: 0.1483, Asian: 0.1031, Total: 0.1467 },
    '22': { Caucasian: 0.1925, 'African American': 0.1901, Hispanic: 0.2013, Asian: 0.2268, Total: 0.1974 },
    '22.2': { Caucasian: 0.0125, 'African American': 0.0161, Hispanic: 0.0085, Asian: 0.0052, Total: 0.0121 },
    '23': { Caucasian: 0.1427, 'African American': 0.1433, Hispanic: 0.1377, Asian: 0.1856, Total: 0.1458 },
    '24': { Caucasian: 0.1510, 'African American': 0.1462, Hispanic: 0.1653, Asian: 0.1649, Total: 0.1539 },
    '25': { Caucasian: 0.1260, 'African American': 0.1257, Hispanic: 0.1165, Asian: 0.0825, Total: 0.1197 },
  },
  D8S1179: {
    '11': { Caucasian: 0.0679, 'African American': 0.0512, Hispanic: 0.0763, Asian: 0.0361, Total: 0.0613 },
    '12': { Caucasian: 0.1454, 'African American': 0.1170, Hispanic: 0.1271, Asian: 0.1186, Total: 0.1293 },
    '13': { Caucasian: 0.3393, 'African American': 0.1988, Hispanic: 0.3008, Asian: 0.2474, Total: 0.2756 },
    '14': { Caucasian: 0.2036, 'African American': 0.2807, Hispanic: 0.2648, Asian: 0.3299, Total: 0.2548 },
    '15': { Caucasian: 0.1136, 'African American': 0.2164, Hispanic: 0.1356, Asian: 0.1753, Total: 0.1583 },
  },
  D21S11: {
    '28': { Caucasian: 0.1634, 'African American': 0.2398, Hispanic: 0.1843, Asian: 0.1186, Total: 0.1892 },
    '29': { Caucasian: 0.1856, 'African American': 0.1769, Hispanic: 0.2140, Asian: 0.3763, Total: 0.2075 },
    '30': { Caucasian: 0.2327, 'African American': 0.1360, Hispanic: 0.2288, Asian: 0.2629, Total: 0.2027 },
    '30.2': { Caucasian: 0.0388, 'African American': 0.0468, Hispanic: 0.0297, Asian: 0.0155, Total: 0.0372 },
    '31.2': { Caucasian: 0.0706, 'African American': 0.1243, Hispanic: 0.0699, Asian: 0.0258, Total: 0.0839 },
  },
  D18S51: {
    '12': { Caucasian: 0.1427, 'African American': 0.1038, Hispanic: 0.1186, Asian: 0.0825, Total: 0.1187 },
    '13': { Caucasian: 0.1260, 'African American': 0.0746, Hispanic: 0.1144, Asian: 0.2010, Total: 0.1134 },
    '14': { Caucasian: 0.1704, 'African American': 0.1360, Hispanic: 0.1864, Asian: 0.2216, Total: 0.1675 },
    '15': { Caucasian: 0.1524, 'African American': 0.1725, Hispanic: 0.1504, Asian: 0.1443, Total: 0.1578 },
    '16': { Caucasian: 0.1371, 'African American': 0.1462, Hispanic: 0.1144, Asian: 0.1082, Total: 0.1322 },
    '17': { Caucasian: 0.0914, 'African American': 0.1287, Hispanic: 0.1102, Asian: 0.0876, Total: 0.1076 },
  },
  D5S818: {
    '10': { Caucasian: 0.0471, 'African American': 0.0833, Hispanic: 0.0551, Asian: 0.1392, Total: 0.0695 },
    '11': { Caucasian: 0.3601, 'African American': 0.2807, Hispanic: 0.3263, Asian: 0.2938, Total: 0.3200 },
    '12': { Caucasian: 0.3573, 'African American': 0.3421, Hispanic: 0.3729, Asian: 0.2526, Total: 0.3460 },
    '13': { Caucasian: 0.1413, 'African American': 0.2120, Hispanic: 0.1780, Asian: 0.2216, Total: 0.1805 },
  },
  D13S317: {
    '8': { Caucasian: 0.1150, 'African American': 0.0570, Hispanic: 0.1292, Asian: 0.1546, Total: 0.1028 },
    '11': { Caucasian: 0.3241, 'African American': 0.2646, Hispanic: 0.2881, Asian: 0.3247, Total: 0.2963 },
    '12': { Caucasian: 0.2742, 'African American': 0.4020, Hispanic: 0.2775, Asian: 0.2010, Total: 0.3103 },
    '13': { Caucasian: 0.1427, 'African American': 0.1871, Hispanic: 0.1483, Asian: 0.1289, Total: 0.1573 },
  },
  D7S820: {
    '9': { Caucasian: 0.1316, 'African American': 0.0936, Hispanic: 0.1123, Asian: 0.1392, Total: 0.1154 },
    '10': { Caucasian: 0.2867, 'African American': 0.3231, Hispanic: 0.2754, Asian: 0.1907, Total: 0.2872 },
    '11': { Caucasian: 0.2022, 'African American': 0.2120, Hispanic: 0.2627, Asian: 0.3454, Total: 0.2326 },
    '12': { Caucasian: 0.2216, 'African American': 0.1754, Hispanic: 0.2161, Asian: 0.1804, Total: 0.2013 },
  },
  D16S539: {
    '9': { Caucasian: 0.1136, 'African American': 0.1857, Hispanic: 0.0996, Asian: 0.2165, Total: 0.1438 },
    '11': { Caucasian: 0.2936, 'African American': 0.3056, Hispanic: 0.2987, Asian: 0.2938, Total: 0.2987 },
    '12': { Caucasian: 0.3172, 'African American': 0.1886, Hispanic: 0.2818, Asian: 0.2113, Total: 0.2669 },
    '13': { Caucasian: 0.1828, 'African American': 0.1725, Hispanic: 0.1992, Asian: 0.1495, Total: 0.1800 },
  },
  CSF1PO: {
    '10': { Caucasian: 0.2521, 'African American': 0.2222, Hispanic: 0.2288, Asian: 0.1598, Total: 0.2283 },
    '11': { Caucasian: 0.3019, 'African American': 0.2281, Hispanic: 0.2754, Asian: 0.2887, Total: 0.2703 },
    '12': { Caucasian: 0.3546, 'African American': 0.3684, Hispanic: 0.3432, Asian: 0.4227, Total: 0.3630 },
    '13': { Caucasian: 0.0637, 'African American': 0.1213, Hispanic: 0.1102, Asian: 0.0928, Total: 0.0956 },
  },
  TH01: {
    '6': { Caucasian: 0.2313, 'African American': 0.1170, Hispanic: 0.2585, Asian: 0.1856, Total: 0.1955 },
    '7': { Caucasian: 0.1911, 'African American': 0.4211, Hispanic: 0.2818, Asian: 0.2887, Total: 0.2968 },
    '8': { Caucasian: 0.0886, 'African American': 0.1886, Hispanic: 0.0932, Asian: 0.0825, Total: 0.1221 },
    '9': { Caucasian: 0.1136, 'African American': 0.1550, Hispanic: 0.1356, Asian: 0.3041, Total: 0.1501 },
    '9.3': { Caucasian: 0.3587, 'African American': 0.1067, Hispanic: 0.2140, Asian: 0.1340, Total: 0.2215 },
  },
  TPOX: {
    '8': { Caucasian: 0.5360, 'African American': 0.4225, Hispanic: 0.5042, Asian: 0.5103, Total: 0.4889 },
    '9': { Caucasian: 0.1094, 'African American': 0.2149, Hispanic: 0.1165, Asian: 0.1289, Total: 0.1477 },
    '11': { Caucasian: 0.2507, 'African American': 0.2295, Hispanic: 0.2818, Asian: 0.2371, Total: 0.2495 },
  },
  D1S1656: {
    '12': { Caucasian: 0.0859, 'African American': 0.0614, Hispanic: 0.0784, Asian: 0.0825, Total: 0.0758 },
    '14': { Caucasian: 0.1122, 'African American': 0.0906, Hispanic: 0.1271, Asian: 0.1907, Total: 0.1158 },
    '15': { Caucasian: 0.2687, 'African American': 0.1535, Hispanic: 0.2013, Asian: 0.2113, Total: 0.2099 },
    '16': { Caucasian: 0.1288, 'African American': 0.1418, Hispanic: 0.1335, Asian: 0.1186, Total: 0.1332 },
    '17.3': { Caucasian: 0.2064, 'African American': 0.1287, Hispanic: 0.1801, Asian: 0.0979, Total: 0.1646 },
  },
  D2S441: {
    '10': { Caucasian: 0.0762, 'African American': 0.2251, Hispanic: 0.1229, Asian: 0.1443, Total: 0.1322 },
    '11': { Caucasian: 0.3476, 'African American': 0.3728, Hispanic: 0.3199, Asian: 0.3763, Total: 0.3523 },
    '11.3': { Caucasian: 0.0623, 'African American': 0.0526, Hispanic: 0.0466, Asian: 0.0361, Total: 0.0531 },
    '12': { Caucasian: 0.0803, 'African American': 0.0643, Hispanic: 0.0847, Asian: 0.0722, Total: 0.0753 },
    '14': { Caucasian: 0.3296, 'African American': 0.1696, Hispanic: 0.3008, Asian: 0.2629, Total: 0.2640 },
  },
  D2S1338: {
    '17': { Caucasian: 0.2022, 'African American': 0.1170, Hispanic: 0.1631, Asian: 0.1340, Total: 0.1588 },
    '19': { Caucasian: 0.1316, 'African American': 0.2149, Hispanic: 0.1780, Asian: 0.0928, Total: 0.1660 },
    '20': { Caucasian: 0.1247, 'African American': 0.1067, Hispanic: 0.1377, Asian: 0.1753, Total: 0.1264 },
    '23': { Caucasian: 0.1011, 'African American': 0.1827, Hispanic: 0.1081, Asian: 0.1237, Total: 0.1318 },
    '25': { Caucasian: 0.0706, 'African American': 0.0526, Hispanic: 0.0699, Asian: 0.1082, Total: 0.0681 },
  },
  D10S1248: {
    '12': { Caucasian: 0.1094, 'African American': 0.0819, Hispanic: 0.1017, Asian: 0.1082, Total: 0.0985 },
    '13': { Caucasian: 0.3283, 'African American': 0.1550, Hispanic: 0.2797, Asian: 0.2165, Total: 0.2495 },
    '14': { Caucasian: 0.3047, 'African American': 0.3845, Hispanic: 0.3157, Asian: 0.3660, Total: 0.3393 },
    '15': { Caucasian: 0.1870, 'African American': 0.2705, Hispanic: 0.2140, Asian: 0.2268, Total: 0.2244 },
  },
  D12S391: {
    '17': { Caucasian: 0.1136, 'African American': 0.1813, Hispanic: 0.1292, Asian: 0.1082, Total: 0.1385 },
    '18': { Caucasian: 0.2119, 'African American': 0.1725, Hispanic: 0.1970, Asian: 0.2165, Total: 0.1959 },
    '18.3': { Caucasian: 0.0249, 'African American': 0.0117, Hispanic: 0.0212, Asian: 0.0052, Total: 0.0179 },
    '19': { Caucasian: 0.1427, 'African American': 0.1477, Hispanic: 0.1462, Asian: 0.1804, Total: 0.1486 },
    '20': { Caucasian: 0.1288, 'African American': 0.1023, Hispanic: 0.1186, Asian: 0.0979, Total: 0.1149 },
    '21': { Caucasian: 0.0817, 'African American': 0.1023, Hispanic: 0.0763, Asian: 0.0928, Total: 0.0883 },
  },
  D19S433: {
    '12': { Caucasian: 0.1094, 'African American': 0.1944, Hispanic: 0.1081, Asian: 0.0825, Total: 0.1347 },
    '13': { Caucasian: 0.2479, 'African American': 0.1944, Hispanic: 0.2606, Asian: 0.2887, Total: 0.2370 },
    '14': { Caucasian: 0.3393, 'African American': 0.2529, Hispanic: 0.2775, Asian: 0.2268, Total: 0.2862 },
    '14.2': { Caucasian: 0.0388, 'African American': 0.1287, Hispanic: 0.0763, Asian: 0.0258, Total: 0.0758 },
    '15': { Caucasian: 0.1454, 'African American': 0.1257, Hispanic: 0.1398, Asian: 0.1856, Total: 0.1414 },
  },
  D22S1045: {
    '11': { Caucasian: 0.0928, 'African American': 0.1769, Hispanic: 0.1081, Asian: 0.0515, Total: 0.1202 },
    '15': { Caucasian: 0.3449, 'African American': 0.2368, Hispanic: 0.3665, Asian: 0.4381, Total: 0.3238 },
    '16': { Caucasian: 0.2313, 'African American': 0.2222, Hispanic: 0.2203, Asian: 0.2165, Total: 0.2244 },
    '17': { Caucasian: 0.0817, 'African American': 0.1170, Hispanic: 0.0847, Asian: 0.0722, Total: 0.0931 },
  },
  SE33: {
    '18': { Caucasian: 0.0706, 'African American': 0.1023, Hispanic: 0.0699, Asian: 0.0515, Total: 0.0792 },
    '19': { Caucasian: 0.0623, 'African American': 0.0819, Hispanic: 0.0699, Asian: 0.0619, Total: 0.0705 },
    '22.2': { Caucasian: 0.0388, 'African American': 0.0322, Hispanic: 0.0297, Asian: 0.0206, Total: 0.0328 },
    '26.2': { Caucasian: 0.0582, 'African American': 0.0322, Hispanic: 0.0466, Asian: 0.0258, Total: 0.0439 },
    '27.2': { Caucasian: 0.0512, 'African American': 0.0380, Hispanic: 0.0466, Asian: 0.0309, Total: 0.0439 },
    '28.2': { Caucasian: 0.0789, 'African American': 0.0409, Hispanic: 0.0636, Asian: 0.0361, Total: 0.0589 },
  },
  'Penta D': {
    '9': { Caucasian: 0.2036, 'African American': 0.1725, Hispanic: 0.2140, Asian: 0.2526, Total: 0.2003 },
    '10': { Caucasian: 0.1524, 'African American': 0.1462, Hispanic: 0.1801, Asian: 0.1649, Total: 0.1578 },
    '11': { Caucasian: 0.1302, 'African American': 0.1842, Hispanic: 0.1462, Asian: 0.1134, Total: 0.1501 },
    '12': { Caucasian: 0.1731, 'African American': 0.1287, Hispanic: 0.1801, Asian: 0.1443, Total: 0.1573 },
  },
  'Penta E': {
    '7': { Caucasian: 0.0817, 'African American': 0.1711, Hispanic: 0.0996, Asian: 0.0619, Total: 0.1134 },
    '11': { Caucasian: 0.1219, 'African American': 0.1023, Hispanic: 0.0996, Asian: 0.1134, Total: 0.1096 },
    '12': { Caucasian: 0.1773, 'African American': 0.1257, Hispanic: 0.1483, Asian: 0.2113, Total: 0.1569 },
    '13': { Caucasian: 0.1427, 'African American': 0.0892, Hispanic: 0.1165, Asian: 0.1340, Total: 0.1182 },
    '14': { Caucasian: 0.1122, 'African American': 0.0819, Hispanic: 0.1165, Asian: 0.0928, Total: 0.1018 },
  },
  Amelogenin: {
    X: { Caucasian: 0.5000, 'African American': 0.5000, Hispanic: 0.5000, Asian: 0.5000, Total: 0.5000 },
    Y: { Caucasian: 0.5000, 'African American': 0.5000, Hispanic: 0.5000, Asian: 0.5000, Total: 0.5000 },
  },
};

export class Nist1036PopGenEngine {
  public static normalizePopulation(popStr: string): NistPopulation {
    const clean = popStr.trim().toLowerCase();
    if (['caucasian', 'eur', 'european', 'white'].includes(clean)) return 'Caucasian';
    if (['african american', 'african-american', 'afr', 'african', 'black'].includes(clean)) return 'African American';
    if (['hispanic', 'his', 'latino'].includes(clean)) return 'Hispanic';
    if (['asian', 'eas', 'east asian', 'east-asian'].includes(clean)) return 'Asian';
    if (['total', 'all'].includes(clean)) return 'Total';
    return 'Caucasian';
  }

  public static getPopulationPMin(population: string): number {
    const pop = this.normalizePopulation(population);
    return POPULATION_SAMPLE_SIZES[pop]?.pMin || 5.0 / 2072.0;
  }

  public static getAlleleFrequency(
    locus: string,
    alleleStr: string,
    population: string = 'Caucasian',
    applyFloor: boolean = true
  ): number {
    const pop = this.normalizePopulation(population);
    const clean = alleleStr.trim().replace(/[[\]]/g, '');
    const locusData = NIST_1036_ALLELE_FREQUENCIES[locus];

    if (locusData && locusData[clean]) {
      const freq = locusData[clean][pop];
      if (freq && freq > 0) {
        return applyFloor ? Math.max(freq, this.getPopulationPMin(pop)) : freq;
      }
    }

    // Dirichlet-Laplace fallback
    const info = POPULATION_SAMPLE_SIZES[pop];
    const smoothed = 1.0 / (info.twoN + 10.0);
    return Math.max(smoothed, info.pMin);
  }

  public static calculateGenotypeProbability(
    locus: string,
    allele1: string,
    allele2?: string,
    population: string = 'Caucasian',
    theta: number = 0.01
  ): { genotypeProb: number; locusLr: number; formula: string } {
    if (locus.toLowerCase() === 'amelogenin') {
      return { genotypeProb: 1.0, locusLr: 1.0, formula: 'Amelogenin Sex Node' };
    }
    const clean1 = allele1.trim().replace(/[[\]]/g, '');
    const clean2 = allele2 ? allele2.trim().replace(/[[\]]/g, '') : clean1;

    const p1 = this.getAlleleFrequency(locus, clean1, population);

    if (clean1 === clean2) {
      // Homozygous
      const pG = p1 * p1 + p1 * (1.0 - p1) * theta;
      const lr = pG > 0 ? 1.0 / pG : 1.0;
      return {
        genotypeProb: pG,
        locusLr: lr,
        formula: `p1^2 + p1*(1-p1)*theta = ${p1.toFixed(4)}^2 + ${p1.toFixed(4)}*(1-${p1.toFixed(4)})*${theta} = ${pG.toFixed(6)}`,
      };
    }

    // Heterozygous
    const p2 = this.getAlleleFrequency(locus, clean2, population);
    const pG = 2.0 * p1 * p2;
    const lr = pG > 0 ? 1.0 / pG : 1.0;
    return {
      genotypeProb: pG,
      locusLr: lr,
      formula: `2*p1*p2 = 2*(${p1.toFixed(4)})*(${p2.toFixed(4)}) = ${pG.toFixed(6)}`,
    };
  }
}
