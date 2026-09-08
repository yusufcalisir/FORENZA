import { describe, it, expect } from "vitest";
import {
  NIST_SRM_2391D_R1B,
  NA18507_O2A,
  NA19240_YRI_E1B1A,
  FATHER_SON_RM_MUTATION,
  PRESET_COHORTS,
  YHRD_METAPOPULATIONS,
  LOCUS_ORDER,
  computeClopperPearsonBound,
  computeBrennerFrequency,
  decoupleDYS389,
  computeStepwiseMutationLR,
  estimateMinimumMaleContributors,
} from "@/components/analysis/PanelYSTR";

describe("Subsystem 08: Y-Chromosome 27-Locus Lineage & Haplotype Engine", () => {
  // ─── Golden Benchmark Vector Integrity Tests ─────────────────────────────────

  it("should define NIST SRM 2391d Component A (R1b-M269) pristine golden vector", () => {
    expect(NIST_SRM_2391D_R1B.DYS19).toBe(14);
    expect(NIST_SRM_2391D_R1B.DYS389I).toBe(13);
    expect(NIST_SRM_2391D_R1B.DYS389II).toBe(29);
    expect(NIST_SRM_2391D_R1B.DYS390).toBe(24);
    expect(NIST_SRM_2391D_R1B["DYS385a/b"]).toEqual([11, 14]);
    expect(NIST_SRM_2391D_R1B.DYS518).toBe(38);
    expect(NIST_SRM_2391D_R1B["DYF387S1a/b"]).toEqual([35, 37]);
  });

  it("should define NA18507 (East Asian O2a) lineage exclusion reference standard", () => {
    expect(NA18507_O2A.DYS19).toBe(15);
    expect(NA18507_O2A.DYS389I).toBe(12);
    expect(NA18507_O2A.DYS389II).toBe(28);
    expect(NA18507_O2A.DYS390).toBe(25);
    expect(NA18507_O2A["DYS385a/b"]).toEqual([13, 19]);
    expect(NA18507_O2A.DYS518).toBe(40);
  });

  it("should define NA19240 (Sub-Saharan African E1b1a) reference standard", () => {
    expect(NA19240_YRI_E1B1A.DYS19).toBe(15);
    expect(NA19240_YRI_E1B1A.DYS389I).toBe(13);
    expect(NA19240_YRI_E1B1A.DYS389II).toBe(30);
    expect(NA19240_YRI_E1B1A.DYS390).toBe(21);
    expect(NA19240_YRI_E1B1A["DYS385a/b"]).toEqual([16, 17]);
    expect(NA19240_YRI_E1B1A.DYS518).toBe(36);
  });

  it("should define Father-Son RM Mutation pair and all 5 standard preset cohorts", () => {
    expect(FATHER_SON_RM_MUTATION.DYS518).toBe(39);
    expect(FATHER_SON_RM_MUTATION.DYS19).toBe(NIST_SRM_2391D_R1B.DYS19);
    expect(PRESET_COHORTS).toHaveLength(5);
    expect(YHRD_METAPOPULATIONS).toHaveLength(6);
    expect(LOCUS_ORDER).toHaveLength(25);
  });

  // ─── ISO/IEC 17025 Section 8 Edge Cases (EC-YSTR-01 to EC-YSTR-05) ───────────

  it("EC-YSTR-01: DYS389 Decoupling Invariant (DYS389.2 = DYS389II - DYS389I)", () => {
    // Standard Caucasian SRM 2391d: DYS389I=13, DYS389II=29 -> DYS389.2=16
    const decoupled = decoupleDYS389(13, 29);
    expect(decoupled.isValid).toBe(true);
    expect(decoupled.dys389_1).toBe(13);
    expect(decoupled.dys389_2).toBe(16);

    // East Asian NA18507: DYS389I=12, DYS389II=28 -> DYS389.2=16
    const decoupledEas = decoupleDYS389(12, 28);
    expect(decoupledEas.isValid).toBe(true);
    expect(decoupledEas.dys389_2).toBe(16);

    // Biologically impossible artifact: DYS389II < DYS389I
    const invalidDecouple = decoupleDYS389(15, 12);
    expect(invalidDecouple.isValid).toBe(false);
    expect(invalidDecouple.dys389_2).toBe(0);
  });

  it("EC-YSTR-02: Clopper-Pearson Zero-Observation Bound Asymptote (k = 0, N = 385000)", () => {
    // For N = 385,000 unobserved haplotype (k = 0):
    // p_upper = 1 - 0.05^(1 / 385001) ~ 7.7810723e-6
    const pUpper = computeClopperPearsonBound(0, 385000);
    expect(pUpper).toBeCloseTo(7.7810723e-6, 9);
    expect(1 / pUpper).toBeGreaterThan(128000);
    expect(1 / pUpper).toBeLessThan(129000);
  });

  it("EC-YSTR-03: Brenner Coancestry Adjustment (theta = 0.03, N = 385000)", () => {
    // p_Brenner = (0 + 0.03) / (385000 + 0.03) = 7.7922e-8
    const pBrenner = computeBrennerFrequency(0, 385000, 0.03);
    expect(pBrenner).toBeCloseTo(7.7922e-8, 10);

    // Monotonicity: as observed matches k increase, frequency strictly increases
    const pBrenner1 = computeBrennerFrequency(1, 385000, 0.03);
    const pBrenner5 = computeBrennerFrequency(5, 385000, 0.03);
    expect(pBrenner1).toBeGreaterThan(pBrenner);
    expect(pBrenner5).toBeGreaterThan(pBrenner1);
  });

  it("EC-YSTR-04: Minimum Male Contributor Algorithm for Forensic Y-STR Mixtures", () => {
    // Mixture containing single-copy DYS390 with 3 alleles: establishes min 3 contributors
    const mixture3 = {
      DYS19: [14, 15],
      DYS389I: [12, 13],
      DYS390: [22, 24, 25], // 3 alleles at single-copy locus
      "DYS385a/b": [11, 14, 15, 17], // 4 alleles at duplicated locus -> 4/2 = 2
    };
    const res3 = estimateMinimumMaleContributors(mixture3);
    expect(res3.minContributors).toBe(3);
    expect(res3.maxSingleLocus).toBe("DYS390");
    expect(res3.maxSingleCount).toBe(3);
    expect(res3.explanationEn).toContain("minimum of 3 male contributors");
  });

  it("EC-YSTR-05: RM Mutation Stepwise Likelihood Tolerance (Prevent False Exclusion)", () => {
    // Father-son transmission with 1 meiosis, 1-step mutation on RM locus DYS518 (mu = 0.018, r = 0.75)
    // SMM probability: 1 * 0.018 * ((1 - 0.75) / 2) * (0.75)^0 = 0.018 * 0.125 = 0.00225
    const lrMut = computeStepwiseMutationLR(1, 1, 0.018, 0.75);
    expect(lrMut).toBeCloseTo(0.00225, 5);
    expect(lrMut).toBeGreaterThan(0);

    // Exact match on standard locus (mu = 0.002, delta = 0) -> (1 - 0.002)^1 = 0.998000
    const lrMatch = computeStepwiseMutationLR(1, 0, 0.002, 0.90);
    expect(lrMatch).toBe(0.998);
  });

  // ─── Pure Biostatistical Mathematical Units ───────────────────────────────────

  it("should calculate Clopper-Pearson upper bound for observed haplotypes (k > 0)", () => {
    // k = 5 in N = 35000
    const bound = computeClopperPearsonBound(5, 35000);
    const point = 5 / 35000;
    expect(bound).toBeGreaterThan(point);
    expect(bound).toBeLessThan(0.001);
  });

  it("should verify Brenner frequency sensitivity across regional subpopulation thetas", () => {
    // theta = 0.01 (European/Caucasian outbred) vs theta = 0.03 (isolated/endogamous)
    const pTheta01 = computeBrennerFrequency(0, 385000, 0.01);
    const pTheta03 = computeBrennerFrequency(0, 385000, 0.03);
    expect(pTheta03).toBeGreaterThan(pTheta01);
  });

  it("should evaluate Stepwise Mutation Model for multi-step mutations and 2 meioses", () => {
    // 2 meioses (Grandfather-Grandson), 2-step mutation:
    // P = 2 * 0.002 * ((1 - 0.90) / 2) * (0.90)^1 = 0.004 * 0.05 * 0.90 = 0.00018
    const lr2Steps = computeStepwiseMutationLR(2, 2, 0.002, 0.90);
    expect(lr2Steps).toBeCloseTo(0.00018, 6);
  });

  it("should evaluate duplicated multi-copy locus driving contributor count in mixtures", () => {
    // 6 alleles observed at DYS385a/b -> ceil(6 / 2) = 3 male contributors
    const mixtureMulti = {
      DYS19: [14, 15],
      "DYS385a/b": [11, 13, 14, 15, 17, 18], // 6 alleles at duplicated locus
    };
    const resMulti = estimateMinimumMaleContributors(mixtureMulti);
    expect(resMulti.minContributors).toBe(3);
    expect(resMulti.maxMultiLocus).toBe("DYS385a/b");
    expect(resMulti.maxMultiCount).toBe(6);
    expect(resMulti.explanationTr).toContain("Cift kopyali DYS385a/b");
  });

  it("should reject non-positive DYS389I alleles during decoupling", () => {
    const invalidZero = decoupleDYS389(0, 29);
    expect(invalidZero.isValid).toBe(false);

    const invalidNegative = decoupleDYS389(-5, 20);
    expect(invalidNegative.isValid).toBe(false);
  });

  it("should handle boundary conditions for database size N <= 0 safely", () => {
    expect(computeClopperPearsonBound(0, 0)).toBe(1.0);
    expect(computeClopperPearsonBound(0, -100)).toBe(1.0);
    expect(computeBrennerFrequency(0, 0)).toBe(1.0);
  });
});
