/**
 * FORENZA Forensic Evidence Operating System
 * Module: mtDNA Control Region (D-Loop), EMPOP 3'-Right Alignment & PhyloTree 17 Biocomputational Engine (TypeScript Client-Side Twin)
 * Standards Compliance: ISO/IEC 17025:2017, SWGDAM Lineage Guidelines (2020), EMPOP Forensic mtDNA Guidelines, ENFSI (2017)
 * Research Source: research/ystr_27_mtdna_empop_lineage_research.md
 */

export type MtdnaRegion =
  | 'HV1 (16024-16365)'
  | 'HV2 (73-340)'
  | 'HV3 (438-574)'
  | 'OHR (110-441)'
  | 'Control Region (16024-576)'
  | 'Coding Region (577-16023)';

export interface MtdnaVariant {
  position: number;
  refBase: string;
  altBase: string;
  observedBase: string;
  variantType: 'SNP' | 'INS' | 'DEL' | 'PHP' | 'LHP';
  mutationType: string;
  rawNotation: string;
  empopNormalizedNotation: string;
  normalizedNotation: string;
  minorAlleleFraction?: number;
  heteroplasmyFrequency?: number;
  isHeteroplasmy: boolean;
  region: MtdnaRegion;
  domain: string;
}

export interface MtdnaHaplogroupPrediction {
  predictedHaplogroup: string;
  macroHaplogroup: string;
  confidenceScore: number;
  matchedMotifs: string[];
  definingMotifMatches: number;
  missingMotifs: string[];
  privateMutations: string[];
  description: string;
  geographicOrigin: string;
}


export const IUPAC_BASES: Record<string, string[]> = {
  R: ['A', 'G'],
  Y: ['C', 'T'],
  M: ['A', 'C'],
  K: ['G', 'T'],
  S: ['C', 'G'],
  W: ['A', 'T'],
  A: ['A'],
  C: ['C'],
  G: ['G'],
  T: ['T'],
};

export const PHYLOTREE_17_MOTIFS: Record<
  string,
  { macro: string; description: string; geo: string; motifs: string[]; negativeMotifs?: string[] }
> = {
  H: {
    macro: 'H',
    description: 'European / Near Eastern Core Lineage (rCRS baseline)',
    geo: 'Europe, Near East, North Africa (40-50% in West Eurasia)',
    motifs: ['73A', '263G', '750G', '16519C'],
    negativeMotifs: ['16223T', '73G'],
  },
  H1: {
    macro: 'H',
    description: 'Western European Iberian / Franco-Cantabrian Lineage',
    geo: 'Western Europe (Basques, Iberia, Scandinavia)',
    motifs: ['73A', '263G', '750G', '3010A', '16519C'],
    negativeMotifs: ['16223T', '73G'],
  },
  H2: {
    macro: 'H',
    description: 'European Lineage with 16291C',
    geo: 'Central / Eastern Europe',
    motifs: ['73A', '263G', '750G', '16291C', '16519C'],
    negativeMotifs: ['16223T', '73G'],
  },
  U5: {
    macro: 'U',
    description: 'European Hunter-Gatherer / Mesolithic Ancient Lineage',
    geo: 'Europe (High in Saami, Finns, Basques)',
    motifs: ['73G', '263G', '750G', '16192T', '16270T', '16519C'],
  },
  U6: {
    macro: 'U',
    description: 'North African / Berber Lineage',
    geo: 'North Africa, Maghreb, Canary Islands',
    motifs: ['73G', '263G', '750G', '16172C', '16219G', '16519C'],
  },
  K: {
    macro: 'U',
    description: 'Western Eurasian / Ashkenazi & Alpine Lineage (Subclade of U8b)',
    geo: 'Europe, Near East, Ashkenazi Jewish',
    motifs: ['73G', '263G', '750G', '16224C', '16311C', '16519C'],
  },
  J1: {
    macro: 'J',
    description: 'Near Eastern / Neolithic Agricultural Expansion Lineage',
    geo: 'Near East, Anatolia, Southern Europe',
    motifs: ['73G', '263G', '295T', '462T', '750G', '16069T', '16126C', '16519C'],
  },
  T2: {
    macro: 'T',
    description: 'European / Mediterranean Lineage',
    geo: 'Europe, Near East',
    motifs: ['73G', '263G', '709A', '750G', '16126C', '16294T', '16296T', '16519C'],
  },
  V: {
    macro: 'HV',
    description: 'Western European / Saami & Basque Lineage',
    geo: 'Europe (Saami, Cantabria, Scandinavia)',
    motifs: ['72C', '73A', '263G', '750G', '16298C', '16519C'],
    negativeMotifs: ['16223T'],
  },
  W: {
    macro: 'N',
    description: 'Northern / Eastern European & South Asian Lineage',
    geo: 'Europe, South Asia',
    motifs: ['73G', '195C', '204C', '207A', '263G', '750G', '16223T', '16292T', '16519C'],
  },
  X2: {
    macro: 'N',
    description: 'Near Eastern, Mediterranean & Native American Lineage',
    geo: 'Near East, North America, Caucasus',
    motifs: ['73G', '153G', '195C', '225A', '263G', '750G', '16189C', '16223T', '16278T', '16519C'],
  },
  L0: {
    macro: 'L',
    description: 'Basal African Khoisan / Southern African Lineage',
    geo: 'Southern Africa (San, Khoisan)',
    motifs: ['73G', '146C', '152C', '182C', '186G', '247A', '263G', '750G', '16187T', '16189C', '16223T', '16230G', '16278T', '16311C'],
  },
  L1: {
    macro: 'L',
    description: 'Central African / Mbuti & Biaka Pygmy Lineage',
    geo: 'Central / West Africa',
    motifs: ['73G', '146C', '182C', '185T', '188G', '247A', '263G', '750G', '16187T', '16189C', '16223T', '16278T', '16293G', '16311C'],
  },
  L2a1: {
    macro: 'L',
    description: 'Sub-Saharan African / Bantu Expansion Lineage',
    geo: 'West / Central / South Africa, African Diaspora',
    motifs: ['73G', '146C', '152C', '182C', '185T', '195C', '247A', '263G', '315.1C', '750G', '16189C', '16209C', '16223T', '16278T', '16390A'],
  },
  L3: {
    macro: 'L',
    description: 'East African Ancestor of Out-of-Africa Lineages',
    geo: 'East Africa',
    motifs: ['73G', '150T', '195C', '263G', '750G', '16189C', '16223T', '16278T', '16362C'],
  },
  M: {
    macro: 'M',
    description: 'Eurasian Macro-Haplogroup M',
    geo: 'South Asia, East Asia, Indigenous Americans',
    motifs: ['73G', '263G', '489C', '750G', '16223T'],
  },
  A2: {
    macro: 'N',
    description: 'Indigenous American / Pan-American Founding Lineage',
    geo: 'Americas (Indigenous populations), East Asia',
    motifs: ['73G', '146C', '153G', '235G', '263G', '315.1C', '663G', '750G', '16111T', '16223T', '16290T', '16319A', '16362C'],
  },
  B2: {
    macro: 'R',
    description: 'Indigenous American / 9-bp Deletion Lineage',
    geo: 'Americas, East Asia, Polynesia',
    motifs: ['73G', '263G', '750G', '16183C', '16189C', '16217C', '16519C'],
  },
  C1: {
    macro: 'M',
    description: 'Indigenous American & Siberian Lineage',
    geo: 'Americas, North / East Asia (Siberia)',
    motifs: ['73G', '263G', '750G', '16223T', '16298C', '16327T'],
  },
  N: {
    macro: 'N',
    description: 'West & East Eurasian Macro-Lineage',
    geo: 'Eurasia, Americas, Oceania (Root of R, U, H, J, T, A, B, etc.)',
    motifs: ['73G', '263G', '750G', '16223T'],
  },
};

export class MtdnaEmpopEngine {
  public static getRegionForPosition(pos: number): MtdnaRegion {
    if (pos >= 16024 && pos <= 16365) return 'HV1 (16024-16365)';
    if (pos >= 73 && pos <= 340) return 'HV2 (73-340)';
    if (pos >= 438 && pos <= 574) return 'HV3 (438-574)';
    if (pos >= 110 && pos <= 441) return 'OHR (110-441)';
    if (pos >= 16024 || pos <= 576) return 'Control Region (16024-576)';
    return 'Coding Region (577-16023)';
  }

  public static parseVariant(rawNotation: string): MtdnaVariant | null {
    const raw = rawNotation.trim();
    if (!raw) return null;

    // Point Heteroplasmy (e.g. 16093Y, 16189Y, 73R)
    const phpMatch = raw.match(/^(\d+)([RYSWKM])$/i);
    if (phpMatch) {
      const pos = parseInt(phpMatch[1], 10);
      const code = phpMatch[2].toUpperCase();
      const region = this.getRegionForPosition(pos);
      return {
        position: pos,
        refBase: '',
        altBase: code,
        observedBase: code,
        variantType: 'PHP',
        mutationType: 'Point Heteroplasmy (PHP)',
        rawNotation: raw,
        empopNormalizedNotation: raw,
        normalizedNotation: raw,
        minorAlleleFraction: 0.25,
        heteroplasmyFrequency: 0.25,
        isHeteroplasmy: true,
        region,
        domain: region,
      };
    }

    // Insertion (e.g. 315.1C, 16193.1C, 524.1A)
    const insMatch = raw.match(/^(\d+)\.(\d+)([ACGTN]+)$/i);
    if (insMatch) {
      const pos = parseInt(insMatch[1], 10);
      const sub = parseInt(insMatch[2], 10);
      const alt = insMatch[3].toUpperCase();
      const norm = this.normalizeEmpopInsertion(pos, sub, alt);
      const region = this.getRegionForPosition(pos);
      return {
        position: pos,
        refBase: '',
        altBase: alt,
        observedBase: alt,
        variantType: sub === 1 ? 'INS' : 'LHP',
        mutationType: sub === 1 ? 'Insertion (INS)' : 'Length Heteroplasmy (LHP)',
        rawNotation: raw,
        empopNormalizedNotation: norm,
        normalizedNotation: norm,
        isHeteroplasmy: false,
        region,
        domain: region,
      };
    }

    // Deletion (e.g. 290del, 291del, 524del)
    const delMatch = raw.match(/^(\d+)del([ACGT]*)$/i);
    if (delMatch) {
      const pos = parseInt(delMatch[1], 10);
      const norm = this.normalizeEmpopDeletion(pos);
      const region = this.getRegionForPosition(pos);
      return {
        position: pos,
        refBase: '',
        altBase: 'del',
        observedBase: 'del',
        variantType: 'DEL',
        mutationType: 'Deletion (DEL)',
        rawNotation: raw,
        empopNormalizedNotation: norm,
        normalizedNotation: norm,
        isHeteroplasmy: false,
        region,
        domain: region,
      };
    }

    // Substitution SNP (e.g. 16519C, 73G, 263G)
    const snpMatch = raw.match(/^([ACGT]?)(\d+)([ACGT])$/i);
    if (snpMatch) {
      const ref = snpMatch[1].toUpperCase();
      const pos = parseInt(snpMatch[2], 10);
      const alt = snpMatch[3].toUpperCase();
      const norm = `${pos}${alt}`;
      const region = this.getRegionForPosition(pos);
      return {
        position: pos,
        refBase: ref,
        altBase: alt,
        observedBase: alt,
        variantType: 'SNP',
        mutationType: 'Substitution (SNP)',
        rawNotation: raw,
        empopNormalizedNotation: norm,
        normalizedNotation: norm,
        isHeteroplasmy: false,
        region,
        domain: region,
      };
    }

    return null;
  }


  public static normalizeEmpopInsertion(pos: number, subIndex: number, insertedBase: string): string {
    const base = insertedBase.toUpperCase();
    if (pos >= 16184 && pos <= 16193 && base === 'C') {
      return `16193.${subIndex}C`;
    }
    if (pos >= 303 && pos <= 315 && base === 'C') {
      return `315.${subIndex}C`;
    }
    if (pos >= 522 && pos <= 524) {
      return `524.${subIndex}${base}`;
    }
    return `${pos}.${subIndex}${base}`;
  }

  public static normalizeEmpopDeletion(pos: number): string {
    if (pos === 290 || pos === 291) return '291del';
    if (pos >= 522 && pos <= 524) return '524del';
    return `${pos}del`;
  }

  public static normalizeProfile(rawMutations: string[]): string[] {
    const parsed: MtdnaVariant[] = [];
    for (const raw of rawMutations) {
      const v = this.parseVariant(raw);
      if (v) parsed.push(v);
    }

    parsed.sort((a, b) => a.position - b.position || a.rawNotation.localeCompare(b.rawNotation));

    const seen = new Set<string>();
    const normalizedList: string[] = [];

    for (const item of parsed) {
      const norm = item.empopNormalizedNotation;
      if (!seen.has(norm)) {
        seen.add(norm);
        normalizedList.push(norm);
      }
    }

    return normalizedList;
  }

  public static classifyHaplogroup(normalizedMutations: string[]): MtdnaHaplogroupPrediction {
    const mutSet = new Set(normalizedMutations);
    const scores: Record<string, number> = {};
    const matchesDict: Record<string, string[]> = {};
    const missingDict: Record<string, string[]> = {};
    const privateDict: Record<string, string[]> = {};

    for (const [hgName, hgData] of Object.entries(PHYLOTREE_17_MOTIFS)) {
      const motifs = hgData.motifs;
      const negMotifs = hgData.negativeMotifs || [];

      const matched = motifs.filter((m) => mutSet.has(m));
      const missing = motifs.filter((m) => !mutSet.has(m));
      const negativeHits = negMotifs.filter((m) => mutSet.has(m));
      const priv = normalizedMutations.filter((m) => !motifs.includes(m));

      const score = matched.length * 3.0 - missing.length * 1.5 - negativeHits.length * 5.0 - priv.length * 0.2;
      scores[hgName] = score;
      matchesDict[hgName] = matched;
      missingDict[hgName] = missing;
      privateDict[hgName] = priv;
    }

    const scoreVals = Object.values(scores);
    const maxScore = scoreVals.length > 0 ? Math.max(...scoreVals) : 0.0;
    let expSum = 0.0;
    for (const s of scoreVals) {
      expSum += Math.exp(Math.max(s - maxScore, -50.0));
    }

    const posteriors: Record<string, number> = {};
    for (const [k, v] of Object.entries(scores)) {
      posteriors[k] = expSum > 0 ? Math.exp(Math.max(v - maxScore, -50.0)) / expSum : 0.0;
    }

    let bestHg = 'H';
    let maxConf = -1;
    for (const [k, v] of Object.entries(posteriors)) {
      if (v > maxConf) {
        maxConf = v;
        bestHg = k;
      }
    }

    const bestData = PHYLOTREE_17_MOTIFS[bestHg];

    return {
      predictedHaplogroup: bestHg,
      macroHaplogroup: bestData.macro,
      confidenceScore: posteriors[bestHg] || 0.5,
      matchedMotifs: matchesDict[bestHg] || [],
      definingMotifMatches: (matchesDict[bestHg] || []).length,
      missingMotifs: missingDict[bestHg] || [],
      privateMutations: privateDict[bestHg] || [],
      description: bestData.description,
      geographicOrigin: bestData.geo,
    };
  }


  public static calculateEmpop95Upper(k: number, n: number = 48500, alpha: number = 0.05): number {
    if (n <= 0) return 1.0;
    if (k === 0) {
      return 1.0 - Math.pow(alpha, 1.0 / (n + 1.0));
    }
    const z = 1.95996398454;
    const p = k / n;
    const denominator = 1 + (z * z) / n;
    const center = p + (z * z) / (2 * n);
    const spread = z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n));
    const upperWilson = (center + spread) / denominator;
    return Math.min(1.0, Math.max(upperWilson, (k + 1) / (n + 1)));
  }

  public static evaluateLineageMatch(
    mutationsA: string[],
    mutationsB: string[],
    options: { empopCountK?: number; empopDatabaseSize?: number } = {}
  ): {
    normalizedProfileA: string[];
    normalizedProfileB: string[];
    sharedMutations: string[];
    profileASpecific: string[];
    profileBSpecific: string[];
    isExclusion: boolean;
    isMatch: boolean;
    empopCountK: number;
    empopDatabaseSize: number;
    pUpper95: number;
    lrMtdna: number;
    log10Lr: number;
    enfsiVerbalScale: string;
    haplogroupA: MtdnaHaplogroupPrediction;
    haplogroupB: MtdnaHaplogroupPrediction;
  } {
    const k = options.empopCountK || 0;
    const n = options.empopDatabaseSize || 48500;

    const normA = this.normalizeProfile(mutationsA);
    const normB = this.normalizeProfile(mutationsB);

    const setA = new Set(normA);
    const setB = new Set(normB);

    const shared = normA.filter((x) => setB.has(x));
    const diffA = normA.filter((x) => !setB.has(x));
    const diffB = normB.filter((x) => !setA.has(x));

    let phpCompatible = true;
    for (const d of diffA) {
      const vA = this.parseVariant(d);
      if (vA && vA.variantType === 'PHP') {
        const bMatch = normB.map((x) => this.parseVariant(x)).filter((x) => x && x.position === vA.position);
        if (bMatch.length > 0 && bMatch[0]) {
          const altB = bMatch[0].altBase;
          const allowed = IUPAC_BASES[vA.altBase] || [];
          if (!allowed.includes(altB)) {
            phpCompatible = false;
          }
        }
      }
    }

    const isExclusion = (diffA.length > 0 || diffB.length > 0) && !phpCompatible;
    const pUpper = this.calculateEmpop95Upper(k, n);
    const lr = !isExclusion && pUpper > 0 ? 1.0 / pUpper : 0.0;
    const log10Lr = lr > 0 ? Math.log10(lr) : -99.0;

    let enfsiVerbal = 'Inconclusive / Neutral Evidence';
    if (isExclusion || lr === 0.0) {
      enfsiVerbal = 'Exclusion / Complete Discordance with Maternal Lineage';
    } else if (log10Lr >= 6.0) {
      enfsiVerbal = 'Extremely Strong Support for Same Maternal Lineage (Hp)';
    } else if (log10Lr >= 4.0) {
      enfsiVerbal = 'Strong Support for Same Maternal Lineage (Hp)';
    } else if (log10Lr >= 3.0) {
      enfsiVerbal = 'Moderately Strong Support for Same Maternal Lineage (Hp)';
    } else if (log10Lr >= 2.0) {
      enfsiVerbal = 'Moderate Support for Same Maternal Lineage (Hp)';
    } else if (log10Lr >= 1.0) {
      enfsiVerbal = 'Limited / Weak Support for Same Maternal Lineage (Hp)';
    }

    const hgA = this.classifyHaplogroup(normA);
    const hgB = this.classifyHaplogroup(normB);

    return {
      normalizedProfileA: normA,
      normalizedProfileB: normB,
      sharedMutations: shared,
      profileASpecific: diffA,
      profileBSpecific: diffB,
      isExclusion,
      isMatch: !isExclusion,
      empopCountK: k,
      empopDatabaseSize: n,
      pUpper95: pUpper,
      lrMtdna: lr,
      log10Lr,
      enfsiVerbalScale: enfsiVerbal,
      haplogroupA: hgA,
      haplogroupB: hgB,
    };
  }

  public static alignMutations(rawMutations: string[], applyEmpopRules: boolean = true): MtdnaVariant[] {
    const parsed: MtdnaVariant[] = [];
    for (const raw of rawMutations) {
      const v = this.parseVariant(raw);
      if (v) parsed.push(v);
    }
    parsed.sort((a, b) => a.position - b.position || a.rawNotation.localeCompare(b.rawNotation));
    return parsed;
  }

  public static calculateEmpopMatchProbability(k: number, n: number = 48200) {
    const upper = this.calculateEmpop95Upper(k, n);
    const lr = upper > 0 ? 1.0 / upper : 0.0;
    const log10Lr = lr > 0 ? Math.log10(lr) : 0.0;
    let enfsiVerbal = 'Extremely Strong Support for Same Maternal Lineage (Hp)';
    if (log10Lr < 1.0) enfsiVerbal = 'Inconclusive / Neutral Evidence';
    else if (log10Lr < 2.0) enfsiVerbal = 'Limited / Weak Support for Same Maternal Lineage (Hp)';
    else if (log10Lr < 3.0) enfsiVerbal = 'Moderate Support for Same Maternal Lineage (Hp)';
    else if (log10Lr < 4.0) enfsiVerbal = 'Moderately Strong Support for Same Maternal Lineage (Hp)';
    else if (log10Lr < 6.0) enfsiVerbal = 'Strong Support for Same Maternal Lineage (Hp)';
    return {
      kMatches: k,
      observedMatches: k,
      databaseSize: n,
      upperBound: upper,
      likelihoodRatio: lr,
      log10Lr,
      enfsiVerbalScale: enfsiVerbal,
    };
  }
}



export const RCRS_CONTROL_REGION_FASTA = `>rCRS (NC_012920.1) Mitochondrial Control Region (16024-576)
GATCACAGGTCTATCACCCTATTAACCACTCACGGGAGCTCTCCATGCATTTGGTATTTTCGTCTGGGGGGTATGCACGC
GATAGCATTGCGAGACGCTGGAGCCGGAGCACCCTATGTCGCAGTATCTGTCTTTGATTCCTGCCTCATCCTATTATTTA
TCGCACCTACGTTCAATATTACAGGCGAACATACTTACTAAAGTGTGTTAATTAATTAATGCTTGTAGGACATAATAATA
ACAATTGAATGTCTGCACAGCCACTTTCCACACAGACATCATAACAAAAAATTTCCACCAAACCCCCCCTCCCCCGCTTC
TGGCCACAGCACTTAAACACATCTCTGCCAAACCCCAAAAACAAAGAACCCTAACACCAGCCTAACCAGATTTCAAATT
TTATCTTTTGGCGGTATGCACTTTTAACAGTCACCCCCCAACTAACACATTATTTTCCCCTCCCACTCCCATACTACTA
ATCTCATCAATACAACCCCCGCCCATCCTACCCAGCACACACACACCGCTGCTAACCCCATACCCCGAACCAACCAAAC
CCCAAAGACACCCCCCACAGTTTATGTAGCTTACCTCCTCAAAGCAATACACTGAAAATGTTTAGACGGGCTCACATCA
CCCCATAAACAAATAGGTTTGGTCCTAGCCTTTCTATTAGCTCTTAGTAAGATTACACATGCAAGCATCCCCGTTCCAG
TGAGTTCACCCTCTAAATCACCACGATCAAAAGGAACAAGCATCAAGCACGCAGCAATGCAGCTCAAAACGCTTAGCCT
AGCCACACCCCCACGGGAAACAGCAGTGATTAACCTTTAGCAATAAACGAAAGTTTAACTAAGCTATACTAACCCCAGG
GTTGGTCAATTTCGTGCCAGCCACCGCGGTCACACGATTAACCCAAGTCAATAGAAGCCGGCGTAAAGAGTGTTTTAGA
TCACCCCCTCCCCAATAAAGCTAAAACTCACCTGAGTTGTAAAAAACTCCAGTTGACACAAAATAGACTACGAAAGTGG
CTTTAACATATCTGAACACACAATAGCTAAGACCCAAACTGGGATTAGATACCCCACTATGCTTAGCCCTAAACCTCAA
CAGTTAAATCAACAAAACTGCTCGCCAGAACACTACGAGCCACAGCTTAAAACTCAAAGGACCTGGCGGTGCTTCATAT
CCCTCTAGAGGAGCCTGTTCTGTAATCGATAAACCCCGATCAACCTCACCACCTCTTGCTCAGCCTATATACCGCCATC
TTCAGCAAACCCTGATGAAGGCTACAAAGTAAGCGCAAGTACCCACGTAAAGACGTTAGGTCAAGGTGTAGCCCATGAG
GTGGCAAGAAATGGGCTACATTTTCTACCCCAGAAAACTACGATAGCCCTTATGAAACTTAAGGGTCGAAGGTGGATTT
AGCAGTAAACTAAGAGTAGAGTGCTTAGTTGAACAGGGCCCTGAAGCGCGTACACACCGCCCGTCACCCTCCTCAAGTA
TACTTCAAAGGACATTTAACTAAAACCCCTACGCATTTATATAGAGGAGACAAGTCGTAACATGGTAAGTGTACTGGAA
AGTGCACTTGGACGAACCAGAGTGTAGCTTAACACAAAGCACCCAACTTACACTTAGGAGATTTCAACTTAACTTGACC
GCTCTGAGCTAAACCTAGCCCCAAACCCACTCCACCTTACTACCAGACAACCTTAGCCAAACCATTTACCCAAATAAAG
TATAGGCGATAGAAATTGAAACCTGGCGCAATAGATATAGTACCGCAAGGGAAAGATGAAAAATTATAACCAAGCATAA
TATAGCAAGGACTAACCCCTATACCTTCTGCATAATGAATTAACTAGAAATAACTTTGCAAGGAGAGCCAAAGCTAAGA
CCCCCGAAACCAGACGAGCTACCTAAGAACAGCTAAAAGAGCACACCCGTCTATGTAGCAAAATAGTGGGAAGATTTAT
AGGTAGAGGCGACAAACCTACCGAGCCTGGTGATAGCTGGTTGTCCAAGATAGAATCTTAGTTCAACTTTAAATTTGCC
CACAGAACCCTCTAAATCCCCTTGTAAATTTAACTGTTAGTCCAAAGAGGAACAGCTCTTTGGACACTAGGAAAAAACC
TTGTAGAGAGAGTAAAAAATTTAACACCCATAGTAGGCCTAAAAGCAGCCACCAATTAAGAAAGCGTTCAAGCTCAACA
CCCACTACCTAAAAAATCCCAAACATCACAACTGAACTCCTCACACCCAATTGGACCAATCTATCACCCTATAGAAGAA
CTAATGTTAGTATAAGTAACATGAAAACATTCTCCTCCGCATAAGCCTGCGTCAGATTAAAACACTGAACTGACAATTA
ACAGCCCAATATCTACAATCAACCAACAAGTCATTATTACCCTCACTGTCAACCCAACACAGGCATGCTCATAAGGAAA
GGTTAAAAAAGTAAAAGGAACTCCTCACACTCAAGAGAATCAGATTACCATAAAAGTCCTCACACACCACGCTTAGTGT
CACATCCCACCTACTTACTCTTTCTTAGTTAAATTAAAGAACCCTTAATCCAAATAACAGACTTGCCATTATAGTCACAC`;

// Aliases for naming compatibility
export type MtDnaMutationCall = MtdnaVariant;
export type MtdnaMutationCall = MtdnaVariant;
export type MtDnaHaplogroupResult = MtdnaHaplogroupPrediction;
export type MtdnaHaplogroupResult = MtdnaHaplogroupPrediction;

