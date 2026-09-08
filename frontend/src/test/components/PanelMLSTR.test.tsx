import { describe, it, expect } from "vitest";
import {
  MLSTR_GOLDEN_VECTOR_01,
  MLSTR_GOLDEN_VECTOR_02,
  MLSTR_GOLDEN_VECTOR_03,
  MLSTR_GOLDEN_VECTOR_04,
  computeStutterRatio,
  computeGiniImpurity,
  computeShannonEntropy,
  computeATMargin,
  computeHeterozygoteBalance,
} from "@/components/analysis/PanelMLSTR";

describe("Subsystem 22: ML STR Calling & Artifact Filtering (Fragsifier RF Ensemble)", () => {
  // ─── Golden Vector Integrity Tests ────────────────────────────────────────────

  it("should define VECTOR_MLSTR_01 D21S11 severe back-stutter certified benchmark", () => {
    expect(MLSTR_GOLDEN_VECTOR_01.id).toBe("VECTOR_MLSTR_01");
    expect(MLSTR_GOLDEN_VECTOR_01.locus).toBe("D21S11");
    expect(MLSTR_GOLDEN_VECTOR_01.rawPeaks).toHaveLength(2);
    // Major allele: h = 2400 RFU at 214.0 bp
    expect(MLSTR_GOLDEN_VECTOR_01.rawPeaks[0].h).toBe(2400);
    expect(MLSTR_GOLDEN_VECTOR_01.rawPeaks[0].class).toBe("CLASS_TRUE_ALLELE");
    // Back-stutter: h = 444 RFU at 210.0 bp
    expect(MLSTR_GOLDEN_VECTOR_01.rawPeaks[1].h).toBe(444);
    expect(MLSTR_GOLDEN_VECTOR_01.rawPeaks[1].class).toBe("CLASS_BACK_STUTTER");
  });

  it("should define VECTOR_MLSTR_02 TH01 +A non-template adenylation certified benchmark", () => {
    expect(MLSTR_GOLDEN_VECTOR_02.id).toBe("VECTOR_MLSTR_02");
    expect(MLSTR_GOLDEN_VECTOR_02.locus).toBe("TH01");
    expect(MLSTR_GOLDEN_VECTOR_02.rawPeaks).toHaveLength(2);
    // Parent allele 9.3: h = 1800 RFU
    expect(MLSTR_GOLDEN_VECTOR_02.rawPeaks[0].h).toBe(1800);
    // Split +A artifact: h = 360 RFU
    expect(MLSTR_GOLDEN_VECTOR_02.rawPeaks[1].h).toBe(360);
    expect(MLSTR_GOLDEN_VECTOR_02.rawPeaks[1].class).toBe("CLASS_PLUS_A_ARTIFACT");
  });

  it("should define VECTOR_MLSTR_03 vWA high-RFU spectral pull-up certified benchmark", () => {
    expect(MLSTR_GOLDEN_VECTOR_03.id).toBe("VECTOR_MLSTR_03");
    expect(MLSTR_GOLDEN_VECTOR_03.locus).toBe("vWA");
    // Major allele: h = 6200 RFU (above 6000 RFU pull-up threshold)
    expect(MLSTR_GOLDEN_VECTOR_03.rawPeaks[0].h).toBe(6200);
    expect(MLSTR_GOLDEN_VECTOR_03.rawPeaks[1].class).toBe("CLASS_SPECTRAL_PULL_UP");
  });

  it("should define VECTOR_MLSTR_04 PROVEDIt 3-person mixture pre-filtering certified benchmark", () => {
    expect(MLSTR_GOLDEN_VECTOR_04.id).toBe("VECTOR_MLSTR_04");
    expect(MLSTR_GOLDEN_VECTOR_04.locus).toBe("D3S1358");
    expect(MLSTR_GOLDEN_VECTOR_04.rawPeaks).toHaveLength(5);
    // 3 true alleles
    const trueAlleles = MLSTR_GOLDEN_VECTOR_04.rawPeaks.filter(
      (p) => p.class === "CLASS_TRUE_ALLELE"
    );
    expect(trueAlleles).toHaveLength(3);
    // 1 stutter
    const stutters = MLSTR_GOLDEN_VECTOR_04.rawPeaks.filter(
      (p) => p.class === "CLASS_BACK_STUTTER"
    );
    expect(stutters).toHaveLength(1);
    // 1 sub-AT noise drop-in
    const noise = MLSTR_GOLDEN_VECTOR_04.rawPeaks.filter(
      (p) => p.class === "CLASS_BASE_NOISE_DROP_IN"
    );
    expect(noise).toHaveLength(1);
    // Noise peak must be below AT = 50.0 RFU
    expect(noise[0].h).toBeLessThan(50.0);
  });

  // ─── EC-MLSTR-02: Stutter Ratio (SR) ─────────────────────────────────────────

  it("EC-MLSTR-02: computeStutterRatio correctly identifies SR = 18.5% for VECTOR_MLSTR_01", () => {
    // SR_obs = h_candidate / h_major_allele = 444 / 2400 = 0.185
    const sr = computeStutterRatio(444, 2400);
    expect(sr).toBeCloseTo(0.185, 4);
  });

  it("EC-MLSTR-02: computeStutterRatio returns 0 when major allele height is zero (edge case)", () => {
    expect(computeStutterRatio(100, 0)).toBe(0);
    expect(computeStutterRatio(0, 0)).toBe(0);
  });

  // ─── EC-MLSTR: Gini Impurity ─────────────────────────────────────────────────

  it("EC-MLSTR: computeGiniImpurity = 0.0 for a pure node (single dominant class)", () => {
    // Pure node: all probability mass on CLASS_TRUE_ALLELE
    const pureNode = computeGiniImpurity([1, 0, 0, 0, 0, 0, 0]);
    expect(pureNode).toBe(0);
  });

  it("EC-MLSTR: computeGiniImpurity = 6/7 for a maximally impure 7-class uniform distribution", () => {
    // Uniform over 7 classes: I_G = 1 - 7*(1/7)^2 = 1 - 1/7 = 6/7 ~ 0.8571
    const uniformProbs = Array(7).fill(1 / 7);
    const impurity = computeGiniImpurity(uniformProbs);
    expect(impurity).toBeCloseTo(6 / 7, 5);
  });

  // ─── EC-MLSTR: Shannon Entropy ───────────────────────────────────────────────

  it("EC-MLSTR: computeShannonEntropy returns 0 for a homopolymer (AAAA)", () => {
    // All same base -> p_A=1, H(S)=-1*log2(1)=0
    expect(computeShannonEntropy("AAAA")).toBeCloseTo(0, 6);
  });

  it("EC-MLSTR: computeShannonEntropy returns 2.0 bits for balanced ACGT sequence", () => {
    // Equal A,C,G,T -> H(S) = -4*(0.25*log2(0.25)) = 2.0 bits
    const entropy = computeShannonEntropy("ACGT");
    expect(entropy).toBeCloseTo(2.0, 5);
  });

  it("EC-MLSTR: computeShannonEntropy returns 0 for empty string", () => {
    expect(computeShannonEntropy("")).toBe(0);
  });

  // ─── EC-MLSTR-01 / EC-MLSTR-04: AT Margin ───────────────────────────────────

  it("EC-MLSTR-04: computeATMargin = 0.0 at exactly AT = 50.0 RFU (boundary condition)", () => {
    // M_AT = (50 - 50) / 50 = 0.0 (at threshold)
    expect(computeATMargin(50.0)).toBe(0.0);
  });

  it("EC-MLSTR-01: all true alleles in VECTOR_MLSTR_04 have positive AT margin (must not be dropped)", () => {
    // M_AT >= 0 for all CLASS_TRUE_ALLELE peaks -> not misclassified as dropout
    MLSTR_GOLDEN_VECTOR_04.rawPeaks
      .filter((p) => p.class === "CLASS_TRUE_ALLELE")
      .forEach((p) => {
        expect(computeATMargin(p.h, 50.0)).toBeGreaterThan(0);
      });
    // Sub-AT noise peak (h=32) must have negative margin
    const noisePeak = MLSTR_GOLDEN_VECTOR_04.rawPeaks.find(
      (p) => p.class === "CLASS_BASE_NOISE_DROP_IN"
    )!;
    expect(computeATMargin(noisePeak.h, 50.0)).toBeLessThan(0);
  });

  // ─── EC-MLSTR-03: Heterozygote Balance ──────────────────────────────────────

  it("EC-MLSTR-03: computeHeterozygoteBalance for VECTOR_MLSTR_01 peak pair = 0.185", () => {
    // H_b = h_minor / h_major = 444 / 2400 = 0.185
    const hb = computeHeterozygoteBalance(444, 2400);
    expect(hb).toBeCloseTo(0.185, 4);
  });

  it("EC-MLSTR-03: computeHeterozygoteBalance is clamped to [0, 1] even for inverted inputs", () => {
    // If h_minor > h_major (inverted), must clamp to 1.0
    const clamped = computeHeterozygoteBalance(3000, 1000);
    expect(clamped).toBe(1.0);
    // Zero major -> returns 0
    expect(computeHeterozygoteBalance(500, 0)).toBe(0);
  });
});
