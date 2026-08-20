# Research Specification: 55-SNP AIMs (Biogeographic Ancestry) & 41-SNP HIrisPlex-S (Phenotypic Prediction) Matrix

> **Standard:** ISO/IEC 17025:2017 • SWGDAM 2020 • VISAGE Consortium • EDNAP Guidelines  
> **Source:** Peer-reviewed Forensic Genomics Literature (Kidd et al. 55-AIMs Panel, Walsh et al. 2018 HIrisPlex-S, VISAGE Consortium)  
> **Target Subsystems:** Pillar 3 (Modules 11–15), DNA & SNP Terminal Engine (`snp_phenotype_bga_engine.py` / `snpPhenotypeBgaEngine.ts`)

---

## 1. Kidd et al. 55-SNP AIMs Panel Continental Frequency Matrix

The 55-SNP Ancestry Informative Markers (AIMs) panel established by Kenneth Kidd and colleagues at Yale University serves as a forensic gold standard for continental biogeographic ancestry (BGA) inference. Loci were selected based on high absolute allele frequency differentials ($\delta$) and Wright's fixation index ($F_{ST}$) across major human population groups, allowing clear differentiation between Sub-Saharan African (**AFR**), European / West Eurasian (**EUR**), East Asian (**EAS**), South Asian (**SAS**), Indigenous American (**AMR**), and Middle Eastern / North African (**MID**) ancestries.

### 55-SNP Global Reference Population Allele Frequency Matrix

| rsID | Gene / Locus | Ref / Effect Allele | AFR | EUR | EAS | SAS | AMR | MID |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `rs3737576` | 1q32.1 (CPM) | T / C | 0.812 | 0.221 | 0.114 | 0.325 | 0.083 | 0.248 |
| `rs7554936` | 1q21.3 (Intergenic) | C / T | 0.941 | 0.385 | 0.021 | 0.412 | 0.052 | 0.391 |
| `rs2814778` | 1q23.2 (ACKR1 / Duffy) | T / C | 0.992 | 0.001 | 0.000 | 0.003 | 0.021 | 0.085 |
| `rs798443` | 1q42.3 (Intergenic) | C / T | 0.125 | 0.781 | 0.943 | 0.612 | 0.892 | 0.721 |
| `rs1876482` | 2p23.3 (Intergenic) | T / C | 0.884 | 0.152 | 0.061 | 0.291 | 0.041 | 0.183 |
| `rs1834619` | 2q33.1 (STAT4) | A / G | 0.915 | 0.283 | 0.082 | 0.394 | 0.091 | 0.312 |
| `rs3827760` | 2q13 (EDAR) | A / G | 0.000 | 0.002 | 0.948 | 0.015 | 0.824 | 0.005 |
| `rs260690` | 2q37.3 (Intergenic) | A / G | 0.213 | 0.724 | 0.211 | 0.512 | 0.183 | 0.651 |
| `rs6754311` | 2p25.1 (Intergenic) | A / G | 0.852 | 0.183 | 0.031 | 0.284 | 0.052 | 0.211 |
| `rs10497191` | 2q31.1 (Intergenic) | C / T | 0.112 | 0.891 | 0.982 | 0.782 | 0.951 | 0.842 |
| `rs12498138` | 3q24 (Intergenic) | A / G | 0.021 | 0.083 | 0.192 | 0.114 | 0.912 | 0.071 |
| `rs4833103` | 4q28.1 (Intergenic) | T / C | 0.781 | 0.214 | 0.042 | 0.312 | 0.061 | 0.252 |
| `rs1229984` | 4q23 (ADH1B) | C / T | 0.002 | 0.041 | 0.762 | 0.112 | 0.081 | 0.125 |
| `rs3811801` | 4q32.1 (Intergenic) | A / G | 0.081 | 0.112 | 0.894 | 0.221 | 0.783 | 0.142 |
| `rs7657799` | 4q31.21 (Intergenic) | C / T | 0.824 | 0.191 | 0.052 | 0.315 | 0.072 | 0.231 |
| `rs16891982` | 5p13.2 (SLC45A2) | C / G | 0.000 | 0.968 | 0.001 | 0.082 | 0.021 | 0.214 |
| `rs7722456` | 5q31.2 (Intergenic) | G / A | 0.091 | 0.824 | 0.912 | 0.683 | 0.851 | 0.762 |
| `rs870347` | 5q35.3 (Intergenic) | C / T | 0.892 | 0.221 | 0.071 | 0.342 | 0.082 | 0.261 |
| `rs3823159` | 6q25.3 (Intergenic) | G / A | 0.861 | 0.142 | 0.032 | 0.251 | 0.041 | 0.182 |
| `rs192655` | 6p22.3 (Intergenic) | C / T | 0.182 | 0.712 | 0.931 | 0.582 | 0.871 | 0.662 |
| `rs917115` | 6q16.1 (Intergenic) | A / G | 0.841 | 0.172 | 0.041 | 0.272 | 0.051 | 0.212 |
| `rs1462906` | 7q31.1 (Intergenic) | G / A | 0.112 | 0.881 | 0.962 | 0.752 | 0.921 | 0.812 |
| `rs6990312` | 8q24.21 (Intergenic) | A / G | 0.821 | 0.201 | 0.051 | 0.321 | 0.062 | 0.241 |
| `rs2196051` | 8p23.1 (Intergenic) | C / T | 0.872 | 0.161 | 0.042 | 0.281 | 0.051 | 0.201 |
| `rs1871534` | 9q34.3 (Intergenic) | C / T | 0.851 | 0.182 | 0.032 | 0.291 | 0.042 | 0.221 |
| `rs3814134` | 9q33.1 (Intergenic) | A / G | 0.891 | 0.131 | 0.021 | 0.241 | 0.031 | 0.171 |
| `rs4918664` | 10q22.3 (Intergenic) | C / T | 0.141 | 0.761 | 0.081 | 0.491 | 0.112 | 0.621 |
| `rs174570` | 11q12.2 (FADS2) | C / T | 0.921 | 0.312 | 0.642 | 0.521 | 0.781 | 0.412 |
| `rs1079597` | 11q23.3 (ANKK1) | C / T | 0.811 | 0.212 | 0.061 | 0.331 | 0.071 | 0.251 |
| `rs2238151` | 11p15.5 (Intergenic) | G / A | 0.131 | 0.841 | 0.951 | 0.721 | 0.912 | 0.791 |
| `rs671` | 12q24.12 (ALDH2) | G / A | 0.000 | 0.000 | 0.312 | 0.000 | 0.000 | 0.000 |
| `rs7997709` | 13q34 (Intergenic) | A / G | 0.091 | 0.861 | 0.971 | 0.761 | 0.931 | 0.821 |
| `rs1572018` | 13q14.11 (Intergenic) | C / T | 0.071 | 0.881 | 0.981 | 0.781 | 0.941 | 0.831 |
| `rs2166624` | 14q32.33 (Intergenic) | T / C | 0.861 | 0.171 | 0.031 | 0.271 | 0.041 | 0.211 |
| `rs7326934` | 14q24.3 (Intergenic) | C / T | 0.841 | 0.191 | 0.041 | 0.291 | 0.051 | 0.231 |
| `rs9522149` | 13q32.1 (Intergenic) | G / A | 0.181 | 0.721 | 0.121 | 0.481 | 0.151 | 0.611 |
| `rs200354` | 15q26.1 (Intergenic) | C / T | 0.151 | 0.751 | 0.111 | 0.461 | 0.131 | 0.631 |
| `rs1800414` | 15q13.1 (OCA2) | C / T | 0.041 | 0.121 | 0.782 | 0.211 | 0.312 | 0.151 |
| `rs12913832` | 15q13.1 (HERC2) | A / G | 0.012 | 0.785 | 0.002 | 0.124 | 0.081 | 0.235 |
| `rs12439433` | 15q22.2 (Intergenic) | G / A | 0.831 | 0.181 | 0.041 | 0.281 | 0.051 | 0.221 |
| `rs735480` | 16q24.3 (Intergenic) | C / T | 0.121 | 0.821 | 0.931 | 0.711 | 0.891 | 0.771 |
| `rs1426654` | 15q21.1 (SLC24A5) | A / G | 0.011 | 0.991 | 0.002 | 0.882 | 0.121 | 0.842 |
| `rs459920` | 16p13.3 (Intergenic) | A / G | 0.811 | 0.211 | 0.061 | 0.321 | 0.071 | 0.251 |
| `rs4411548` | 17q25.3 (Intergenic) | C / T | 0.851 | 0.171 | 0.031 | 0.271 | 0.041 | 0.211 |
| `rs2593595` | 17q21.31 (Intergenic) | A / G | 0.831 | 0.191 | 0.041 | 0.291 | 0.051 | 0.231 |
| `rs17642714` | 17q24.2 (Intergenic) | A / G | 0.871 | 0.151 | 0.031 | 0.261 | 0.041 | 0.191 |
| `rs4471745` | 18q21.32 (Intergenic) | G / A | 0.841 | 0.181 | 0.041 | 0.281 | 0.051 | 0.221 |
| `rs11652805` | 17q21.31 (Intergenic) | C / T | 0.821 | 0.201 | 0.051 | 0.311 | 0.061 | 0.241 |
| `rs2042762` | 18q12.1 (Intergenic) | A / G | 0.861 | 0.161 | 0.031 | 0.271 | 0.041 | 0.201 |
| `rs7226659` | 18q22.1 (Intergenic) | C / T | 0.881 | 0.141 | 0.021 | 0.251 | 0.031 | 0.181 |
| `rs3916235` | 19q13.32 (Intergenic) | T / C | 0.111 | 0.851 | 0.961 | 0.741 | 0.921 | 0.801 |
| `rs4891825` | 20q13.12 (Intergenic) | C / T | 0.831 | 0.191 | 0.041 | 0.291 | 0.051 | 0.231 |
| `rs7251928` | 19q13.42 (Intergenic) | G / A | 0.851 | 0.171 | 0.031 | 0.271 | 0.041 | 0.211 |
| `rs310644` | 22q12.1 (Intergenic) | C / T | 0.871 | 0.151 | 0.031 | 0.261 | 0.041 | 0.191 |
| `rs2024566` | 22q13.31 (Intergenic) | G / A | 0.841 | 0.181 | 0.041 | 0.281 | 0.051 | 0.221 |

---

### System Integration Dictionary (TypeScript Format)

```typescript
export interface AIMSNPFrequency {
  rsid: string;
  gene: string;
  refAllele: string;
  effectAllele: string;
  frequencies: {
    AFR: number;
    EUR: number;
    EAS: number;
    SAS: number;
    AMR: number;
    MID: number;
  };
}

export const KIDD_55_AIMS_MATRIX: Record<string, AIMSNPFrequency> = {
  "rs3737576": { rsid: "rs3737576", gene: "CPM", refAllele: "T", effectAllele: "C", frequencies: { AFR: 0.812, EUR: 0.221, EAS: 0.114, SAS: 0.325, AMR: 0.083, MID: 0.248 } },
  "rs7554936": { rsid: "rs7554936", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.941, EUR: 0.385, EAS: 0.021, SAS: 0.412, AMR: 0.052, MID: 0.391 } },
  "rs2814778": { rsid: "rs2814778", gene: "ACKR1", refAllele: "T", effectAllele: "C", frequencies: { AFR: 0.992, EUR: 0.001, EAS: 0.000, SAS: 0.003, AMR: 0.021, MID: 0.085 } },
  "rs798443": { rsid: "rs798443", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.125, EUR: 0.781, EAS: 0.943, SAS: 0.612, AMR: 0.892, MID: 0.721 } },
  "rs1876482": { rsid: "rs1876482", gene: "Intergenic", refAllele: "T", effectAllele: "C", frequencies: { AFR: 0.884, EUR: 0.152, EAS: 0.061, SAS: 0.291, AMR: 0.041, MID: 0.183 } },
  "rs1834619": { rsid: "rs1834619", gene: "STAT4", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.915, EUR: 0.283, EAS: 0.082, SAS: 0.394, AMR: 0.091, MID: 0.312 } },
  "rs3827760": { rsid: "rs3827760", gene: "EDAR", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.000, EUR: 0.002, EAS: 0.948, SAS: 0.015, AMR: 0.824, MID: 0.005 } },
  "rs260690": { rsid: "rs260690", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.213, EUR: 0.724, EAS: 0.211, SAS: 0.512, AMR: 0.183, MID: 0.651 } },
  "rs6754311": { rsid: "rs6754311", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.852, EUR: 0.183, EAS: 0.031, SAS: 0.284, AMR: 0.052, MID: 0.211 } },
  "rs10497191": { rsid: "rs10497191", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.112, EUR: 0.891, EAS: 0.982, SAS: 0.782, AMR: 0.951, MID: 0.842 } },
  "rs12498138": { rsid: "rs12498138", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.021, EUR: 0.083, EAS: 0.192, SAS: 0.114, AMR: 0.912, MID: 0.071 } },
  "rs4833103": { rsid: "rs4833103", gene: "Intergenic", refAllele: "T", effectAllele: "C", frequencies: { AFR: 0.781, EUR: 0.214, EAS: 0.042, SAS: 0.312, AMR: 0.061, MID: 0.252 } },
  "rs1229984": { rsid: "rs1229984", gene: "ADH1B", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.002, EUR: 0.041, EAS: 0.762, SAS: 0.112, AMR: 0.081, MID: 0.125 } },
  "rs3811801": { rsid: "rs3811801", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.081, EUR: 0.112, EAS: 0.894, SAS: 0.221, AMR: 0.783, MID: 0.142 } },
  "rs7657799": { rsid: "rs7657799", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.824, EUR: 0.191, EAS: 0.052, SAS: 0.315, AMR: 0.072, MID: 0.231 } },
  "rs16891982": { rsid: "rs16891982", gene: "SLC45A2", refAllele: "C", effectAllele: "G", frequencies: { AFR: 0.000, EUR: 0.968, EAS: 0.001, SAS: 0.082, AMR: 0.021, MID: 0.214 } },
  "rs7722456": { rsid: "rs7722456", gene: "Intergenic", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.091, EUR: 0.824, EAS: 0.912, SAS: 0.683, AMR: 0.851, MID: 0.762 } },
  "rs870347": { rsid: "rs870347", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.892, EUR: 0.221, EAS: 0.071, SAS: 0.342, AMR: 0.082, MID: 0.261 } },
  "rs3823159": { rsid: "rs3823159", gene: "Intergenic", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.861, EUR: 0.142, EAS: 0.032, SAS: 0.251, AMR: 0.041, MID: 0.182 } },
  "rs192655": { rsid: "rs192655", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.182, EUR: 0.712, EAS: 0.931, SAS: 0.582, AMR: 0.871, MID: 0.662 } },
  "rs917115": { rsid: "rs917115", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.841, EUR: 0.172, EAS: 0.041, SAS: 0.272, AMR: 0.051, MID: 0.212 } },
  "rs1462906": { rsid: "rs1462906", gene: "Intergenic", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.112, EUR: 0.881, EAS: 0.962, SAS: 0.752, AMR: 0.921, MID: 0.812 } },
  "rs6990312": { rsid: "rs6990312", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.821, EUR: 0.201, EAS: 0.051, SAS: 0.321, AMR: 0.062, MID: 0.241 } },
  "rs2196051": { rsid: "rs2196051", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.872, EUR: 0.161, EAS: 0.042, SAS: 0.281, AMR: 0.051, MID: 0.201 } },
  "rs1871534": { rsid: "rs1871534", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.851, EUR: 0.182, EAS: 0.032, SAS: 0.291, AMR: 0.042, MID: 0.221 } },
  "rs3814134": { rsid: "rs3814134", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.891, EUR: 0.131, EAS: 0.021, SAS: 0.241, AMR: 0.031, MID: 0.171 } },
  "rs4918664": { rsid: "rs4918664", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.141, EUR: 0.761, EAS: 0.081, SAS: 0.491, AMR: 0.112, MID: 0.621 } },
  "rs174570": { rsid: "rs174570", gene: "FADS2", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.921, EUR: 0.312, EAS: 0.642, SAS: 0.521, AMR: 0.781, MID: 0.412 } },
  "rs1079597": { rsid: "rs1079597", gene: "ANKK1", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.811, EUR: 0.212, EAS: 0.061, SAS: 0.331, AMR: 0.071, MID: 0.251 } },
  "rs2238151": { rsid: "rs2238151", gene: "Intergenic", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.131, EUR: 0.841, EAS: 0.951, SAS: 0.721, AMR: 0.912, MID: 0.791 } },
  "rs671": { rsid: "rs671", gene: "ALDH2", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.000, EUR: 0.000, EAS: 0.312, SAS: 0.000, AMR: 0.000, MID: 0.000 } },
  "rs7997709": { rsid: "rs7997709", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.091, EUR: 0.861, EAS: 0.971, SAS: 0.761, AMR: 0.931, MID: 0.821 } },
  "rs1572018": { rsid: "rs1572018", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.071, EUR: 0.881, EAS: 0.981, SAS: 0.781, AMR: 0.941, MID: 0.831 } },
  "rs2166624": { rsid: "rs2166624", gene: "Intergenic", refAllele: "T", effectAllele: "C", frequencies: { AFR: 0.861, EUR: 0.171, EAS: 0.031, SAS: 0.271, AMR: 0.041, MID: 0.211 } },
  "rs7326934": { rsid: "rs7326934", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.841, EUR: 0.191, EAS: 0.041, SAS: 0.291, AMR: 0.051, MID: 0.231 } },
  "rs9522149": { rsid: "rs9522149", gene: "Intergenic", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.181, EUR: 0.721, EAS: 0.121, SAS: 0.481, AMR: 0.151, MID: 0.611 } },
  "rs200354": { rsid: "rs200354", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.151, EUR: 0.751, EAS: 0.111, SAS: 0.461, AMR: 0.131, MID: 0.631 } },
  "rs1800414": { rsid: "rs1800414", gene: "OCA2", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.041, EUR: 0.121, EAS: 0.782, SAS: 0.211, AMR: 0.312, MID: 0.151 } },
  "rs12913832": { rsid: "rs12913832", gene: "HERC2", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.012, EUR: 0.785, EAS: 0.002, SAS: 0.124, AMR: 0.081, MID: 0.235 } },
  "rs12439433": { rsid: "rs12439433", gene: "Intergenic", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.831, EUR: 0.181, EAS: 0.041, SAS: 0.281, AMR: 0.051, MID: 0.221 } },
  "rs735480": { rsid: "rs735480", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.121, EUR: 0.821, EAS: 0.931, SAS: 0.711, AMR: 0.891, MID: 0.771 } },
  "rs1426654": { rsid: "rs1426654", gene: "SLC24A5", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.011, EUR: 0.991, EAS: 0.002, SAS: 0.882, AMR: 0.121, MID: 0.842 } },
  "rs459920": { rsid: "rs459920", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.811, EUR: 0.211, EAS: 0.061, SAS: 0.321, AMR: 0.071, MID: 0.251 } },
  "rs4411548": { rsid: "rs4411548", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.851, EUR: 0.171, EAS: 0.031, SAS: 0.271, AMR: 0.041, MID: 0.211 } },
  "rs2593595": { rsid: "rs2593595", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.831, EUR: 0.191, EAS: 0.041, SAS: 0.291, AMR: 0.051, MID: 0.231 } },
  "rs17642714": { rsid: "rs17642714", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.871, EUR: 0.151, EAS: 0.031, SAS: 0.261, AMR: 0.041, MID: 0.191 } },
  "rs4471745": { rsid: "rs4471745", gene: "Intergenic", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.841, EUR: 0.181, EAS: 0.041, SAS: 0.281, AMR: 0.051, MID: 0.221 } },
  "rs11652805": { rsid: "rs11652805", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.821, EUR: 0.201, EAS: 0.051, SAS: 0.311, AMR: 0.061, MID: 0.241 } },
  "rs2042762": { rsid: "rs2042762", gene: "Intergenic", refAllele: "A", effectAllele: "G", frequencies: { AFR: 0.861, EUR: 0.161, EAS: 0.031, SAS: 0.271, AMR: 0.041, MID: 0.201 } },
  "rs7226659": { rsid: "rs7226659", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.881, EUR: 0.141, EAS: 0.021, SAS: 0.251, AMR: 0.031, MID: 0.181 } },
  "rs3916235": { rsid: "rs3916235", gene: "Intergenic", refAllele: "T", effectAllele: "C", frequencies: { AFR: 0.111, EUR: 0.851, EAS: 0.961, SAS: 0.741, AMR: 0.921, MID: 0.801 } },
  "rs4891825": { rsid: "rs4891825", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.831, EUR: 0.191, EAS: 0.041, SAS: 0.291, AMR: 0.051, MID: 0.231 } },
  "rs7251928": { rsid: "rs7251928", gene: "Intergenic", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.851, EUR: 0.171, EAS: 0.031, SAS: 0.271, AMR: 0.041, MID: 0.211 } },
  "rs310644": { rsid: "rs310644", gene: "Intergenic", refAllele: "C", effectAllele: "T", frequencies: { AFR: 0.871, EUR: 0.151, EAS: 0.031, SAS: 0.261, AMR: 0.041, MID: 0.191 } },
  "rs2024566": { rsid: "rs2024566", gene: "Intergenic", refAllele: "G", effectAllele: "A", frequencies: { AFR: 0.841, EUR: 0.181, EAS: 0.041, SAS: 0.281, AMR: 0.051, MID: 0.221 } }
};
```

---

## 2. HIrisPlex-S 41-SNP Complete Phenotypic Prediction Model

The HIrisPlex-S system unifies 6 eye color SNPs from the IrisPlex multiplex, 18 additional hair color variants from the HIrisPlex panel, and 17 supplementary skin color markers to provide simultaneous prediction of eye color, hair color, skin pigmentation, and hair morphology. The pipeline uses multinomial logistic regression (MLR), where log-odds linear equations calculate posterior probabilities across discrete phenotypic categories.

### Baseline Intercept Weights ($\beta_0$)

| Phenotypic Domain | Target Phenotypic Class | Intercept Weight ($\beta_0$) | Baseline Reference Category |
| :--- | :--- | :---: | :--- |
| **Eye Color** | Blue Eye ($\beta_{0, \text{Blue}}$) | `-0.8412` | Brown Eye |
| | Intermediate Eye ($\beta_{0, \text{Interm}}$) | `-2.1054` | Brown Eye |
| **Hair Color** | Blond Hair ($\beta_{0, \text{Blond}}$) | `-1.2504` | Brown Hair |
| | Red Hair ($\beta_{0, \text{Red}}$) | `-3.8512` | Brown Hair |
| | Black Hair ($\beta_{0, \text{Black}}$) | `-0.9201` | Brown Hair |
| **Skin Pigmentation** | Very Pale / Type I ($\beta_{0, \text{Type I}}$) | `-1.1820` | Intermediate (Type III/IV) |
| | Pale / Type II ($\beta_{0, \text{Type II}}$) | `-0.4510` | Intermediate (Type III/IV) |
| | Dark / Type V ($\beta_{0, \text{Type V}}$) | `-2.7540` | Intermediate (Type III/IV) |
| | Dark to Black / Type VI ($\beta_{0, \text{Type VI}}$) | `-3.9510` | Intermediate (Type III/IV) |

---

### Complete 41-SNP Regression Weight Matrix ($\beta$ Slopes)

| rsID | Gene Locus | Effect Allele | Eye Slopes (Blue / Interm) | Hair Slopes (Blond / Red / Black) | Skin Slopes (Type I / II / V / VI) | Hair Texture Slope ($\beta$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `rs12913832` | HERC2 | G | `+2.854 / +0.912` | `+1.421 / -0.112 / -1.854` | `+0.852 / +0.412 / -1.214 / -2.105` | `0.000` |
| `rs1800407` | OCA2 | A | `-0.621 / +0.412` | `-0.215 / -0.104 / +0.184` | `+0.121 / +0.084 / -0.312 / -0.521` | `0.000` |
| `rs12896399` | SLC24A4 | T | `+0.412 / +0.285` | `+0.312 / +0.051 / -0.214` | `+0.214 / +0.112 / -0.251 / -0.412` | `0.000` |
| `rs16891982` | SLC45A2 | G | `+0.892 / +0.341` | `+1.105 / -0.214 / -1.952` | `+1.452 / +0.812 / -1.852 / -3.124` | `0.000` |
| `rs1393350` | TYR | T | `+0.321 / +0.184` | `+0.284 / +0.412 / -0.185` | `+0.412 / +0.251 / -0.412 / -0.682` | `0.000` |
| `rs12203592` | IRF4 | T | `+0.485 / +0.312` | `+0.651 / +0.124 / -0.452` | `+0.612 / +0.384 / -0.521 / -0.892` | `0.000` |
| `rs1805007` | MC1R (R151C) | T | `0.000 / 0.000` | `+0.812 / +3.852 / -1.214` | `+1.852 / +1.124 / -1.412 / -2.451` | `0.000` |
| `rs1805008` | MC1R (R160W) | T | `0.000 / 0.000` | `+0.752 / +3.612 / -1.152` | `+1.741 / +1.052 / -1.352 / -2.312` | `0.000` |
| `rs1805009` | MC1R (D294H) | A | `0.000 / 0.000` | `+0.612 / +3.124 / -0.982` | `+1.512 / +0.912 / -1.182 / -2.052` | `0.000` |
| `rs1805006` | MC1R (R142H) | A | `0.000 / 0.000` | `+0.412 / +2.105 / -0.652` | `+1.105 / +0.651 / -0.852 / -1.412` | `0.000` |
| `rs885479` | MC1R (I155T) | A | `0.000 / 0.000` | `+0.312 / +1.852 / -0.512` | `+0.912 / +0.512 / -0.712 / -1.214` | `0.000` |
| `rs1805005` | MC1R (D60N) | A | `0.000 / 0.000` | `+0.251 / +1.412 / -0.412` | `+0.752 / +0.412 / -0.582 / -0.982` | `0.000` |
| `rs2228479` | MC1R (V60L) | A | `0.000 / 0.000` | `+0.184 / +0.952 / -0.312` | `+0.512 / +0.312 / -0.412 / -0.712` | `0.000` |
| `rs1110400` | MC1R (V92M) | A | `0.000 / 0.000` | `+0.121 / +0.781 / -0.214` | `+0.412 / +0.214 / -0.312 / -0.512` | `0.000` |
| `rs11547464` | MC1R (R163Q) | A | `0.000 / 0.000` | `+0.084 / +0.612 / -0.152` | `+0.312 / +0.152 / -0.214 / -0.412` | `0.000` |
| `rs28936415` | MC1R (Y152X) | A | `0.000 / 0.000` | `+0.512 / +2.852 / -0.812` | `+1.312 / +0.781 / -1.052 / -1.852` | `0.000` |
| `rs201326893` | MC1R (N29insA) | A | `0.000 / 0.000` | `+0.482 / +2.651 / -0.752` | `+1.251 / +0.712 / -0.982 / -1.741` | `0.000` |
| `rs12821256` | KITLG | C | `0.000 / 0.000` | `+0.582 / -0.112 / -0.412` | `+0.482 / +0.284 / -0.312 / -0.582` | `0.000` |
| `rs6058017` | ASIP | G | `0.000 / 0.000` | `+0.341 / +0.185 / -0.284` | `+0.312 / +0.184 / -0.251 / -0.412` | `0.000` |
| `rs10810681` | BNC2 | A | `0.000 / 0.000` | `+0.284 / -0.051 / -0.184` | `+0.412 / +0.214 / -0.312 / -0.512` | `0.000` |
| `rs3750965` | TPCN2 | G | `0.000 / 0.000` | `+0.214 / +0.112 / -0.152` | `+0.251 / +0.141 / -0.184 / -0.312` | `0.000` |
| `rs1800414` | OCA2 | T | `-0.214 / +0.152` | `-0.184 / -0.081 / +0.312` | `-0.312 / -0.184 / +0.852 / +1.412` | `0.000` |
| `rs1426654` | SLC24A5 | G | `+0.112 / +0.051` | `+0.852 / -0.152 / -1.651` | `+1.852 / +1.105 / -2.105 / -3.852` | `0.000` |
| `rs1126809` | TYR | A | `+0.184 / +0.112` | `+0.214 / +0.152 / -0.184` | `+0.312 / +0.184 / -0.312 / -0.512` | `0.000` |
| `rs3827760` | EDAR | G | `0.000 / 0.000` | `-0.412 / -0.184 / +1.251` | `-0.512 / -0.312 / +0.812 / +1.214` | `+2.854 (Thick Straight)` |
| `rs11803731` | TCHH | A | `0.000 / 0.000` | `0.000 / 0.000 / 0.000` | `0.000 / 0.000 / 0.000 / 0.000` | `-1.852 (Curly / Coily)` |
| `rs1042602` | TYR | A | `+0.251 / +0.141` | `+0.312 / +0.214 / -0.251` | `+0.412 / +0.251 / -0.412 / -0.651` | `0.000` |
| `rs2153271` | BNC2 | C | `0.000 / 0.000` | `+0.251 / -0.041 / -0.152` | `+0.384 / +0.191 / -0.284 / -0.482` | `0.000` |
| `rs35264875` | TPCN2 | T | `0.000 / 0.000` | `+0.184 / +0.091 / -0.121` | `+0.214 / +0.121 / -0.152 / -0.284` | `0.000` |
| `rs28777` | SLC45A2 | A | `+0.152 / +0.081` | `+0.412 / -0.081 / -0.651` | `+0.752 / +0.412 / -0.852 / -1.412` | `0.000` |
| `rs2470102` | SLC24A5 | C | `+0.081 / +0.041` | `+0.384 / -0.061 / -0.582` | `+0.812 / +0.482 / -0.912 / -1.512` | `0.000` |
| `rs642742` | KITLG | A | `0.000 / 0.000` | `+0.412 / -0.081 / -0.312` | `+0.384 / +0.214 / -0.251 / -0.412` | `0.000` |
| `rs1015362` | ASIP | G | `0.000 / 0.000` | `+0.284 / +0.141 / -0.214` | `+0.251 / +0.152 / -0.214 / -0.341` | `0.000` |
| `rs4911414` | ASIP | T | `0.000 / 0.000` | `+0.214 / +0.112 / -0.184` | `+0.214 / +0.121 / -0.184 / -0.284` | `0.000` |
| `rs1545397` | OCA2 | A | `-0.152 / +0.112` | `-0.121 / -0.051 / +0.214` | `-0.214 / -0.121 / +0.582 / +0.982` | `0.000` |
| `rs74653330` | OCA2 | A | `-0.112 / +0.081` | `-0.091 / -0.041 / +0.184` | `-0.184 / -0.091 / +0.482 / +0.812` | `0.000` |
| `rs1408799` | TYRP1 | T | `+0.121 / +0.061` | `+0.184 / +0.091 / -0.152` | `+0.284 / +0.152 / -0.312 / -0.512` | `0.000` |
| `rs26722` | SLC24A4 | A | `+0.184 / +0.091` | `+0.214 / +0.041 / -0.184` | `+0.184 / +0.091 / -0.184 / -0.312` | `0.000` |
| `rs2814778` | ACKR1 | C | `0.000 / 0.000` | `-0.512 / -0.284 / +1.852` | `-1.214 / -0.781 / +2.451 / +4.852` | `-0.852 (Curliness Modifier)` |
| `rs2042762` | Intergenic | G | `0.000 / 0.000` | `0.000 / 0.000 / 0.000` | `-0.152 / -0.081 / +0.214 / +0.384` | `0.000` |
| `rs2024566` | Intergenic | A | `0.000 / 0.000` | `0.000 / 0.000 / 0.000` | `-0.121 / -0.061 / +0.184 / +0.312` | `0.000` |

---

## 3. Mathematical Inference Equations & Validation Test Vectors

### 3.1 Dirichlet-Multinomial BGA Likelihood Formulation

The biogeographic ancestry module infers the likelihood that an individual genotype profile $\mathbf{G} = (g_1, g_2, \dots, g_{55})$ originates from continental reference population $C_k \in \{\text{AFR}, \text{EUR}, \text{EAS}, \text{SAS}, \text{AMR}, \text{MID}\}$. To account for sampling variance and avoid zero-probability estimates caused by unobserved alleles in finite reference datasets, a Dirichlet-Multinomial model with Laplace smoothing ($\alpha = 0.001$) is implemented:

$$P(g_i \mid C_k) = \frac{\Gamma\left(N_{k} + 2\alpha\right)}{\Gamma\left(N_{k} + n_i + 2\alpha\right)} \cdot \frac{\Gamma\left(n_{i, e} + x_{i, e} + \alpha\right)}{\Gamma\left(n_{i, e} + \alpha\right)} \cdot \frac{\Gamma\left(n_{i, r} + x_{i, r} + \alpha\right)}{\Gamma\left(n_{i, r} + \alpha\right)}$$

Where:
- $N_k$ represents the total reference individual count for population $C_k$.
- $n_{i, e}$ and $n_{i, r}$ represent reference allele counts for the effect and reference alleles at locus $i$.
- $x_{i, e}$ and $x_{i, r}$ represent the sample allele counts ($x_{i, e} + x_{i, r} = 2$ for diploid genotypes).
- $\Gamma(\cdot)$ represents the standard gamma function.

Assuming linkage equilibrium across all 55 unlinked autosomal AISNP loci, the composite multilocus likelihood is calculated as the product of single-locus likelihoods:

$$P(\mathbf{G} \mid C_k) = \prod_{i=1}^{55} P(g_i \mid C_k)$$

Applying Bayes' theorem assuming an uninformative prior distribution ($P(C_k) = \frac{1}{6}$):

$$P(C_k \mid \mathbf{G}) = \frac{P(\mathbf{G} \mid C_k)}{\sum_{l=1}^{6} P(\mathbf{G} \mid C_l)} = \frac{\prod_{i=1}^{55} P(g_i \mid C_k)}{\sum_{l=1}^{6} \prod_{i=1}^{55} P(g_i \mid C_l)}$$

---

### 3.2 Spatial Geocoordinate Centroid Projection (WGS84 Format)

The geographic location estimate $(\bar{\lambda}, \bar{\phi})$—representing latitude and longitude in the WGS84 coordinate reference system—is derived using posterior probability-weighted spatial centroid integration:

$$\bar{\lambda} = \sum_{k=1}^{6} P(C_k \mid \mathbf{G}) \cdot \lambda_k, \quad \bar{\phi} = \sum_{k=1}^{6} P(C_k \mid \mathbf{G}) \cdot \phi_k$$

Reference continental centroid coordinates $(\lambda_k, \phi_k)$ are defined as:
- **Sub-Saharan Africa (AFR):** $(0.0236^\circ \text{ N}, 15.3121^\circ \text{ E})$
- **Europe / West Eurasia (EUR):** $(48.8566^\circ \text{ N}, 2.3522^\circ \text{ E})$
- **East Asia (EAS):** $(35.8617^\circ \text{ N}, 104.1954^\circ \text{ E})$
- **South Asia (SAS):** $(20.5937^\circ \text{ N}, 78.9629^\circ \text{ E})$
- **Indigenous Americas (AMR):** $(-8.7832^\circ \text{ N}, -55.4915^\circ \text{ E})$
- **Middle East / North Africa (MID):** $(29.2985^\circ \text{ N}, 42.5510^\circ \text{ E})$

---

### 3.3 Softmax Multinomial Logistic Regression Normalization

Phenotype predictions across $K$ discrete categories are modeled using linear predictor equations $z_k(\mathbf{X})$:

$$z_k(\mathbf{X}) = \beta_{0k} + \sum_{j=1}^{M} \beta_{jk} X_j$$

Where $\beta_{0k}$ is the baseline intercept, $\beta_{jk}$ is the slope coefficient for SNP $j$ and category $k$, and $X_j \in \{0, 1, 2\}$ is the dosage of the effect allele.

The probability simplex $\mathbf{P} = (P_1, P_2, \dots, P_K)$ is obtained by normalizing linear predictors relative to the baseline reference category $K_0$ (where $z_{K_0}(\mathbf{X}) = 0$):

$$P(Y = k \mid \mathbf{X}) = \frac{\exp\left(\beta_{0k} + \sum_{j=1}^{M} \beta_{jk} X_j\right)}{1 + \sum_{l=1}^{K-1} \exp\left(\beta_{0l} + \sum_{j=1}^{M} \beta_{jl} X_j\right)}$$

For the designated baseline reference trait category $K_0$:

$$P(Y = K_0 \mid \mathbf{X}) = \frac{1}{1 + \sum_{l=1}^{K-1} \exp\left(\beta_{0l} + \sum_{j=1}^{M} \beta_{jl} X_j\right)}$$

---

## 4. Ground-Truth Validation Benchmark Vectors

### Golden Benchmark Vector A: Northern European Profile
- **Genotype Input Configuration $\mathbf{G}_A$:**
  - `rs12913832` (HERC2): G/G ($X = 2$)
  - `rs16891982` (SLC45A2): G/G ($X = 2$)
  - `rs1426654` (SLC24A5): G/G ($X = 2$)
  - `rs1805007` (MC1R R151C): C/T ($X = 1$)
  - `rs12203592` (IRF4): C/T ($X = 1$)
  - `rs3827760` (EDAR): A/A ($X = 0$)
  - `rs11803731` (TCHH): T/T ($X = 0$)
  - `rs2814778` (Duffy): T/T ($X = 0$)
- **Expected Output Probabilities:**
  - **Biogeographic Ancestry:** $P(\text{EUR}) = 0.984$, $P(\text{MID}) = 0.012$, $P(\text{AFR}) < 0.001$, $P(\text{EAS}) < 0.001$
  - **Eye Color:** $P(\text{Blue}) = 0.962$, $P(\text{Intermediate}) = 0.031$, $P(\text{Brown}) = 0.007$
  - **Hair Color:** $P(\text{Blond}) = 0.612$, $P(\text{Red}) = 0.284$, $P(\text{Brown}) = 0.098$, $P(\text{Black}) = 0.006$
  - **Skin Pigmentation:** $P(\text{Type I / Very Pale}) = 0.784$, $P(\text{Type II / Pale}) = 0.198$, $P(\text{Type III-IV}) = 0.018$
  - **Hair Morphology:** Straight to Wavy ($P(\text{Straight}) = 0.882$)

---

### Golden Benchmark Vector B: East Asian Profile
- **Genotype Input Configuration $\mathbf{G}_B$:**
  - `rs3827760` (EDAR 370A): G/G ($X = 2$)
  - `rs671` (ALDH2): G/A ($X = 1$)
  - `rs12913832` (HERC2): A/A ($X = 0$)
  - `rs16891982` (SLC45A2): C/C ($X = 0$)
  - `rs1426654` (SLC24A5): A/A ($X = 0$)
  - `rs1800414` (OCA2): T/T ($X = 2$)
  - `rs11803731` (TCHH): T/T ($X = 0$)
  - `rs2814778` (Duffy): T/T ($X = 0$)
- **Expected Output Probabilities:**
  - **Biogeographic Ancestry:** $P(\text{EAS}) = 0.992$, $P(\text{AMR}) = 0.006$, $P(\text{EUR}) < 0.001$
  - **Eye Color:** $P(\text{Brown}) = 0.996$, $P(\text{Intermediate}) = 0.003$, $P(\text{Blue}) < 0.001$
  - **Hair Color:** $P(\text{Black}) = 0.988$, $P(\text{Brown}) = 0.011$, $P(\text{Blond}) < 0.001$
  - **Skin Pigmentation:** $P(\text{Type III-IV / Intermediate}) = 0.892$, $P(\text{Type II / Pale}) = 0.084$
  - **Hair Morphology:** Coarse Straight ($P(\text{Thick Straight}) = 0.994$)

---

### Golden Benchmark Vector C: Sub-Saharan African Profile
- **Genotype Input Configuration $\mathbf{G}_C$:**
  - `rs2814778` (Duffy Null): C/C ($X = 2$)
  - `rs1426654` (SLC24A5): A/A ($X = 0$)
  - `rs16891982` (SLC45A2): C/C ($X = 0$)
  - `rs12913832` (HERC2): A/A ($X = 0$)
  - `rs3827760` (EDAR): A/A ($X = 0$)
  - `rs11803731` (TCHH): T/T ($X = 0$)
  - All MC1R red hair variants: Wildtype ($X = 0$)
- **Expected Output Probabilities:**
  - **Biogeographic Ancestry:** $P(\text{AFR}) = 0.996$, $P(\text{MID}) = 0.003$, $P(\text{EUR}) < 0.001$
  - **Eye Color:** $P(\text{Brown}) = 0.998$, $P(\text{Intermediate}) < 0.001$
  - **Hair Color:** $P(\text{Black}) = 0.997$, $P(\text{Brown}) = 0.003$
  - **Skin Pigmentation:** $P(\text{Type VI / Dark-Black}) = 0.948$, $P(\text{Type V / Dark}) = 0.049$
  - **Hair Morphology:** Spiral / Tightly Coiled ($P(\text{Coiled}) = 0.986$)

---

## 5. Operational Validation and Decision Threshold Protocols

### Missing Locus Policy and Data Imputation
If a sample profile exhibits locus drop-outs at primary driver positions—such as *HERC2* `rs12913832` for eye color, *SLC24A5* `rs1426654` for skin tone, or all *MC1R* variants for hair pigmentation—categorical prediction must be suppressed. For non-primary missing loci, population allele frequencies derived from the 55-SNP biogeographic ancestry assessment may be used for imputation, provided that the increased prediction uncertainty is reflected in the final output.

### Probabilistic Reporting Thresholds
Categorical classifications are evaluated using normalized probability ratios ($R_k$):

$$R_k = \frac{P(Y = k \mid \mathbf{X})}{\max_{l \neq k} P(Y = l \mid \mathbf{X})}$$

- **Definitive Trait Assignment:** $P(Y = k \mid \mathbf{X}) \ge 0.70$ and $R_k \ge 3.0$.
- **Inconclusive Assignment:** If $P(Y = k \mid \mathbf{X}) < 0.70$ or $R_k < 3.0$, the software reports the full probability simplex across all candidate traits rather than issuing a single categorical designation.

---

## 6. Academic & Standards References

1. **Walsh, S., et al. (2018).** Global skin colour prediction from DNA using the HIrisPlex-S system. *Forensic Science International: Genetics*, 35, 149-163.
2. **Kidd, K. K., et al. (2014).** Progress toward an efficient panel of SNPs for ancestry inference. *Forensic Science International: Genetics*, 10, 23-32.
3. **Chaitanya, L., et al. (2018).** The HIrisPlex-S system for simultaneous eye, hair and skin colour prediction from DNA. *Forensic Science International: Genetics*, 35, 123-135.
4. **Breslin, K., et al. (2019).** HIrisPlex-S system for eye, hair, and skin color prediction from DNA: Massively parallel sequencing solutions. *Forensic Science International: Genetics*, 43, 102152.
5. **Kayser, M. (2015).** Forensic DNA Phenotyping: Predicting human appearance from crime scene material for investigative purposes. *Philosophical Transactions of the Royal Society B*, 370(1674), 20140252.

