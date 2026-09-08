import { describe, it, expect } from "vitest";
import {
  LIFESTYLE_PROBES,
  GOLDEN_LIFESTYLE_VECTORS,
} from "@/components/analysis/PanelLifestyle";

describe("PanelLifestyle Biophysical Models & Specifications (Pillar 4 Research)", () => {
  it("should define exactly 8 diagnostic environmental probes", () => {
    expect(LIFESTYLE_PROBES).toHaveLength(8);
    const probeGenes = LIFESTYLE_PROBES.map((p) => p.gene);
    expect(probeGenes).toContain("AHRR");
    expect(probeGenes).toContain("F2RL3");
    expect(probeGenes).toContain("ALPPL2");
    expect(probeGenes).toContain("ABCG1");
    expect(probeGenes).toContain("CPT1A");
    expect(probeGenes).toContain("SREBF1");
    expect(probeGenes).toContain("SLC6A3");
  });

  it("should define all 8 certified golden benchmark vectors (A through H)", () => {
    expect(GOLDEN_LIFESTYLE_VECTORS).toHaveLength(8);
    const codes = GOLDEN_LIFESTYLE_VECTORS.map((v) => v.code);
    expect(codes).toEqual([
      "VECTOR_18_LIFE_A",
      "VECTOR_18_LIFE_B",
      "VECTOR_18_LIFE_C",
      "VECTOR_18_LIFE_D",
      "VECTOR_18_LIFE_E",
      "VECTOR_18_LIFE_F",
      "VECTOR_18_LIFE_G",
      "VECTOR_18_LIFE_H",
    ]);
  });

  it("should accurately evaluate VECTOR_18_LIFE_A as never smoker baseline", () => {
    const v = GOLDEN_LIFESTYLE_VECTORS.find((x) => x.code === "VECTOR_18_LIFE_A")!;
    expect(v).toBeDefined();

    // Score_smoke = 10.50 - 9.80*AHRR - 2.50*F2RL3 - 1.80*ALPPL2
    const score = 10.50 - 9.80 * v.ahrrBeta - 2.50 * v.f2rl3Beta - 1.80 * v.alppl2Beta;
    expect(score).toBeLessThan(1.50);
    expect(v.expectedSmokingStatus).toBe("NON_SMOKER");
    expect(v.expectedPackYears).toBe(0.0);
    expect(v.expectedBmiCategory).toBe("NORMAL_WEIGHT");
  });

  it("should accurately evaluate VECTOR_18_LIFE_B as heavy smoker with high pack-years", () => {
    const v = GOLDEN_LIFESTYLE_VECTORS.find((x) => x.code === "VECTOR_18_LIFE_B")!;
    expect(v).toBeDefined();

    const score = 10.50 - 9.80 * v.ahrrBeta - 2.50 * v.f2rl3Beta - 1.80 * v.alppl2Beta;
    expect(score).toBeGreaterThan(6.00);
    const packYears = Math.max(0.0, (0.85 - v.ahrrBeta) / 0.012);
    expect(packYears).toBeGreaterThanOrEqual(40.0);
    expect(v.expectedSmokingStatus).toBe("CURRENT_HEAVY_SMOKER");
  });

  it("should accurately evaluate VECTOR_18_LIFE_D normal BMI calculation", () => {
    const v = GOLDEN_LIFESTYLE_VECTORS.find((x) => x.code === "VECTOR_18_LIFE_D")!;
    expect(v).toBeDefined();

    // BMI = 24.50 + 18.20*ABCG1 - 22.40*CPT1A + 12.10*SREBF1
    const rawBmi = 24.50 + 18.20 * v.abcg1Beta - 22.40 * v.cpt1aBeta + 12.10 * v.srebf1Beta;
    expect(rawBmi).toBeCloseTo(24.4, 1);
    expect(v.expectedBmiCategory).toBe("NORMAL_WEIGHT");
  });

  it("should accurately evaluate VECTOR_18_LIFE_E severe obesity calculation", () => {
    const v = GOLDEN_LIFESTYLE_VECTORS.find((x) => x.code === "VECTOR_18_LIFE_E")!;
    expect(v).toBeDefined();

    const rawBmi = 24.50 + 18.20 * v.abcg1Beta - 22.40 * v.cpt1aBeta + 12.10 * v.srebf1Beta;
    expect(rawBmi).toBeGreaterThanOrEqual(35.0);
    expect(v.expectedBmiCategory).toBe("OBESITY_CLASS_2_PLUS");
  });

  it("should accurately evaluate VECTOR_18_LIFE_F heavy alcohol exposure index", () => {
    const v = GOLDEN_LIFESTYLE_VECTORS.find((x) => x.code === "VECTOR_18_LIFE_F")!;
    expect(v).toBeDefined();

    const alcScore = Math.abs(0.50 - v.slc6a3Beta) * 200.0;
    expect(alcScore).toBe(80.0);
    expect(v.expectedAlcoholLevel).toBe("HEAVY_CHRONIC_EXPOSURE");
  });

  it("should accurately evaluate VECTOR_18_LIFE_G nocturnal circadian phase window", () => {
    const v = GOLDEN_LIFESTYLE_VECTORS.find((x) => x.code === "VECTOR_18_LIFE_G")!;
    expect(v).toBeDefined();

    const ratio = v.per2Beta / Math.max(0.01, v.bmal1Beta);
    expect(ratio).toBe(2.0);
    expect(ratio).toBeGreaterThan(1.2);
    expect(v.expectedCircadianPhase).toBe("NOCTURNAL_PEAK_NIGHT");
  });

  it("should accurately evaluate VECTOR_18_LIFE_H accelerated biological aging delta", () => {
    const v = GOLDEN_LIFESTYLE_VECTORS.find((x) => x.code === "VECTOR_18_LIFE_H")!;
    expect(v).toBeDefined();

    const delta = v.estimatedDnamAge - v.chronologicalAge;
    expect(delta).toBe(8.5);
    expect(delta).toBeGreaterThan(5.0);
    expect(v.expectedAgingStatus).toBe("ACCELERATED_BIOLOGICAL_AGING");
  });
});
