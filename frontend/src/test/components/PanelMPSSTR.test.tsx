import { describe, it, expect } from "vitest";
import {
  MPS_GOLDEN_VECTOR_01,
  MPS_GOLDEN_VECTOR_02,
  MPS_GOLDEN_VECTOR_03,
  MPS_GOLDEN_VECTOR_04,
  MPS_GOLDEN_PRESETS,
  computeExpectedHeterozygosity,
  computePowerOfDiscrimination,
  computeSyntenicRecombinationLR,
  reconcileSE33FlankingDeletion,
  parseSequenceToLengthCall,
  computeIsoalleleInformationGain,
} from "@/components/analysis/PanelMPSSTR";

describe("Subsystem 23: Massively Parallel Sequencing (MPS/NGS) STR Analysis", () => {
  // ─── Golden Benchmark Vector Integrity Tests ─────────────────────────────────

  it("should define VECTOR_MPS_01 SE33 bimodal isoallele certified benchmark", () => {
    expect(MPS_GOLDEN_VECTOR_01.id).toBe("VECTOR_MPS_01");
    expect(MPS_GOLDEN_VECTOR_01.locus).toBe("SE33");
    expect(MPS_GOLDEN_VECTOR_01.population).toBe("CAUCASIAN");
    expect(MPS_GOLDEN_VECTOR_01.ceGenotype).toBe("18, 27.2");
    expect(MPS_GOLDEN_VECTOR_01.seqAlleles).toHaveLength(2);
    expect(MPS_GOLDEN_VECTOR_01.lrCe).toBe(74.2);
    expect(MPS_GOLDEN_VECTOR_01.lrMps).toBe(3086.4);
    expect(MPS_GOLDEN_VECTOR_01.gainBoost).toBe(41.6);
  });

  it("should define VECTOR_MPS_02 SE33 4-bp flanking deletion resolver benchmark", () => {
    expect(MPS_GOLDEN_VECTOR_02.id).toBe("VECTOR_MPS_02");
    expect(MPS_GOLDEN_VECTOR_02.locus).toBe("SE33");
    expect(MPS_GOLDEN_VECTOR_02.ceGenotype).toBe("16, 23.2");
    expect(MPS_GOLDEN_VECTOR_02.seqAlleles).toHaveLength(2);
    expect(MPS_GOLDEN_VECTOR_02.flankingNotes[0]).toContain("rs369314007");
    expect(MPS_GOLDEN_VECTOR_02.flankingNotes[1]).toContain("rs1371483225");
    expect(MPS_GOLDEN_VECTOR_02.gainBoost).toBe(15.2);
  });

  it("should define VECTOR_MPS_03 D3S1358 3-person mixture deconvolution benchmark", () => {
    expect(MPS_GOLDEN_VECTOR_03.id).toBe("VECTOR_MPS_03");
    expect(MPS_GOLDEN_VECTOR_03.locus).toBe("D3S1358");
    expect(MPS_GOLDEN_VECTOR_03.ceGenotype).toBe("15, 16");
    expect(MPS_GOLDEN_VECTOR_03.seqAlleles).toHaveLength(5);
    expect(MPS_GOLDEN_VECTOR_03.lrCe).toBe(400.0);
    expect(MPS_GOLDEN_VECTOR_03.lrMps).toBe(496000.0);
    expect(MPS_GOLDEN_VECTOR_03.gainBoost).toBe(1240.0);
  });

  it("should define VECTOR_MPS_04 vWA African primer mutation rescue benchmark", () => {
    expect(MPS_GOLDEN_VECTOR_04.id).toBe("VECTOR_MPS_04");
    expect(MPS_GOLDEN_VECTOR_04.locus).toBe("vWA");
    expect(MPS_GOLDEN_VECTOR_04.population).toBe("AFRICAN_AMERICAN");
    expect(MPS_GOLDEN_VECTOR_04.ceGenotype).toBe("14, 15");
    expect(MPS_GOLDEN_VECTOR_04.flankingNotes[0]).toContain("rs771794429");
    expect(MPS_GOLDEN_VECTOR_04.gainBoost).toBe(8.5);
    expect(MPS_GOLDEN_PRESETS).toHaveLength(4);
  });

  // ─── ISO/IEC 17025 Section 8 Edge Cases (EC-MPS-01 to EC-MPS-05) ─────────────

  it("EC-MPS-01: Backward CE Translation Invariant (|Delta L| = 0 for all ISFG sequences)", () => {
    // Small integer SE33 allele 18
    const parsed18 = parseSequenceToLengthCall("CTTC [CTTT]17_rs9362477[C>T]");
    expect(parsed18.lengthCall).toBe(18);
    expect(parsed18.isMicrovariant).toBe(false);

    // Large 0.2 microvariant SE33 allele 27.2
    const parsed27_2 = parseSequenceToLengthCall("CTTC [CTTT]10 TT [CTTT]16_rs1277875566[T>C]");
    expect(parsed27_2.lengthCall).toBe(27.2);
    expect(parsed27_2.isMicrovariant).toBe(true);

    // D3S1358 allele 15
    const parsed15 = parseSequenceToLengthCall("[TCTA]1 [TCTG]3 [TCTA]11");
    expect(parsed15.lengthCall).toBe(15);
    expect(parsed15.isMicrovariant).toBe(false);

    // TH01 0.3 microvariant 9.3
    const parsed9_3 = parseSequenceToLengthCall("[AATG]6 ATG [AATG]3");
    expect(parsed9_3.lengthCall).toBe(9.3);
    expect(parsed9_3.isMicrovariant).toBe(true);
  });

  it("EC-MPS-02: Simplex Normalization and Expected Heterozygosity Invariant", () => {
    // 10 equal frequency alleles (simplex: sum p_i = 1.0)
    const freqs10 = Array(10).fill(0.1);
    const hExp10 = computeExpectedHeterozygosity(freqs10);
    // H_exp = 1 - 10*(0.01) = 0.900000
    expect(hExp10).toBe(0.9);

    // Boundary: Single homozygous allele (p = 1.0) -> H_exp = 0.0
    const hExpHomo = computeExpectedHeterozygosity([1.0]);
    expect(hExpHomo).toBe(0.0);

    // High diversity locus (e.g. SE33 with 20 alleles each 0.05) -> H_exp = 1 - 20*(0.0025) = 0.95
    const freqs20 = Array(20).fill(0.05);
    const hExp20 = computeExpectedHeterozygosity(freqs20);
    expect(hExp20).toBe(0.95);
  });

  it("EC-MPS-03: 4-bp Flanking Deletion Auto-Reconciliation (rs369314007 and rs1371483225)", () => {
    // rs369314007 shifts raw MPS repeat call by +1 -> Reconciles from 17.0 to 16.0
    const rec1 = reconcileSE33FlankingDeletion("[CTTT]17_rs369314007[delTTTT]", 17.0);
    expect(rec1.has4bpDeletion).toBe(true);
    expect(rec1.deletionRsId).toBe("rs369314007");
    expect(rec1.reconciledCall).toBe(16.0);
    expect(rec1.concordanceStatus).toBe("100% RECONCILED");

    // rs1371483225 shifts raw MPS repeat call by +1 -> Reconciles from 24.2 to 23.2
    const rec2 = reconcileSE33FlankingDeletion("[CTTT]12 TT [CTTT]12_rs1371483225[delTCTT]", 24.2);
    expect(rec2.has4bpDeletion).toBe(true);
    expect(rec2.deletionRsId).toBe("rs1371483225");
    expect(rec2.reconciledCall).toBe(23.2);
    expect(rec2.concordanceStatus).toBe("100% RECONCILED");

    // Normal non-deletion sequence remains unchanged
    const recNormal = reconcileSE33FlankingDeletion("CTTC [CTTT]17_rs9362477[C>T]", 18.0);
    expect(recNormal.has4bpDeletion).toBe(false);
    expect(recNormal.deletionRsId).toBeNull();
    expect(recNormal.reconciledCall).toBe(18.0);
    expect(recNormal.concordanceStatus).toBe("CONCORDANT");
  });

  it("EC-MPS-04: Syntenic Linkage Guard (D6S1043 - SE33 recombination theta = 0.0440)", () => {
    const d6Lr = 150.0;
    const se33Lr = 3200.0;

    // Conservative standard: fallback to more informative locus
    const fallbackResult = computeSyntenicRecombinationLR(d6Lr, se33Lr, 0.044, true);
    expect(fallbackResult.isLinkageRisk).toBe(true);
    expect(fallbackResult.adjustedLr).toBe(3200.0);
    expect(fallbackResult.actionTaken).toContain("FALLBACK_TO_MORE_INFORMATIVE_LOCUS");

    // Recombination discount: (150 * 3200) * (1 - (0.5 - 0.044)) = 480,000 * 0.544 = 261,120.0
    const discountResult = computeSyntenicRecombinationLR(d6Lr, se33Lr, 0.044, false);
    expect(discountResult.isLinkageRisk).toBe(true);
    expect(discountResult.adjustedLr).toBe(261120.0);
    expect(discountResult.actionTaken).toContain("RECOMBINATION_DISCOUNT_APPLIED");
  });

  it("EC-MPS-05: Analytical Cutoff & Boundary Condition Filtering", () => {
    // Empty frequency array returns safe boundary values
    const emptyResult = computePowerOfDiscrimination([]);
    expect(emptyResult.matchProbability).toBe(1);
    expect(emptyResult.powerOfDiscrimination).toBe(0);

    // Empty array for expected heterozygosity returns 0
    expect(computeExpectedHeterozygosity([])).toBe(0);
  });

  // ─── Pure Biostatistical Mathematical Units ───────────────────────────────────

  it("should verify PD + PM = 1.000000 invariant across arbitrary allele frequency distributions", () => {
    const frequencies = [0.4, 0.25, 0.15, 0.12, 0.08];
    const { matchProbability, powerOfDiscrimination } = computePowerOfDiscrimination(frequencies);
    expect(matchProbability + powerOfDiscrimination).toBeCloseTo(1.0, 5);
  });

  it("should calculate exact PM and PD for a 5-allele uniform distribution", () => {
    // 5 alleles with p_i = 0.20:
    // sum(p_i^2) = 5 * 0.04 = 0.20
    // sum(p_i^4) = 5 * 0.0016 = 0.0080
    // PM = 2 * (0.20)^2 - 0.0080 = 2 * 0.04 - 0.0080 = 0.072000
    // PD = 1 - 0.072000 = 0.928000
    const uniform5 = Array(5).fill(0.2);
    const { matchProbability, powerOfDiscrimination } = computePowerOfDiscrimination(uniform5);
    expect(matchProbability).toBeCloseTo(0.072, 6);
    expect(powerOfDiscrimination).toBeCloseTo(0.928, 6);
  });

  it("should compute exact information gain boost for VECTOR_MPS_01 (41.6x)", () => {
    const gain = computeIsoalleleInformationGain(74.2, 3086.4);
    expect(gain).toBe(41.6);
  });

  it("should guard computeIsoalleleInformationGain against zero or negative CE LR", () => {
    expect(computeIsoalleleInformationGain(0, 1000)).toBe(1.0);
    expect(computeIsoalleleInformationGain(-50, 1000)).toBe(1.0);
  });

  it("should parse sequence repeat blocks and count total base pairs accurately", () => {
    const parsed = parseSequenceToLengthCall("[TCTA]1 [TCTG]3 [TCTA]11");
    expect(parsed.totalBp).toBe(60);
    expect(parsed.lengthCall).toBe(15);
    expect(parsed.motifBlocks).toHaveLength(3);
    expect(parsed.motifBlocks[0]).toEqual({ motif: "TCTA", count: 1 });
    expect(parsed.motifBlocks[1]).toEqual({ motif: "TCTG", count: 3 });
    expect(parsed.motifBlocks[2]).toEqual({ motif: "TCTA", count: 11 });
  });

  it("should compute Expected Heterozygosity for high-polymorphism SE33 benchmark (H_exp > 0.97)", () => {
    // 50 alleles with average p = 0.02 (sum p^2 = 50 * 0.0004 = 0.02) -> H_exp = 0.98
    const freqList = Array(50).fill(0.02);
    const hExp = computeExpectedHeterozygosity(freqList);
    expect(hExp).toBe(0.98);
    expect(hExp).toBeGreaterThan(0.97);
  });
});
