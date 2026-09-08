import { describe, it, expect } from "vitest";
import {
  GOLDEN_VECTOR_01,
  GOLDEN_VECTOR_02,
  GOLDEN_VECTOR_03,
  computeInferredWaterD18O,
  computeInferredWaterD2H,
  computeDeuteriumExcess,
  computeZtrIndex,
  computeBrayCurtis,
  computeCanterDiameter,
  computeFusedGeoLR,
} from "@/components/analysis/GeoForensicIntelligencePanel";

describe("Pillar 7: Geo-Forensic Intelligence & Spatial Biogeochemistry (Subsystems 34-38)", () => {
  it("should define certified Golden Vector 01 for Multi-Isotope Isoscape Provenance", () => {
    expect(GOLDEN_VECTOR_01.sampleId).toBe("UNIDENTIFIED_REMAINS_CH_01");
    expect(GOLDEN_VECTOR_01.enamelD18O).toBe(25.4);
    expect(GOLDEN_VECTOR_01.enamelSr).toBe(0.70882);
    expect(GOLDEN_VECTOR_01.hairD2H).toBe(-78.4);
    expect(GOLDEN_VECTOR_01.expectedLat).toBe(46.91);
    expect(GOLDEN_VECTOR_01.expectedLon).toBe(8.39);
    expect(GOLDEN_VECTOR_01.expectedLR).toBe(32500);
  });

  it("should define certified Golden Vector 02 for Forensic Soil QXRD Pedology", () => {
    expect(GOLDEN_VECTOR_02.questionedId).toBe("Q_BOOT_SUSPECT_01");
    expect(GOLDEN_VECTOR_02.controlId).toBe("K_CRIME_SCENE_SOIL_01");
    expect(GOLDEN_VECTOR_02.qQuartz).toBe(58.4);
    expect(GOLDEN_VECTOR_02.qCalcite).toBe(3.1);
    expect(GOLDEN_VECTOR_02.expectedDM).toBe(1.42);
    expect(GOLDEN_VECTOR_02.expectedF).toBe(0.056);
    expect(GOLDEN_VECTOR_02.expectedZTR).toBe(9.5);
    expect(GOLDEN_VECTOR_02.expectedLR).toBe(4500);
  });

  it("should define certified Golden Vector 03 for Rossmo CGT Geographic Profiling", () => {
    expect(GOLDEN_VECTOR_03).toHaveLength(5);
    const ids = GOLDEN_VECTOR_03.map((s) => s.id);
    expect(ids).toEqual(["C1", "C2", "C3", "C4", "C5"]);
    expect(GOLDEN_VECTOR_03[0].x).toBe(4.0);
    expect(GOLDEN_VECTOR_03[0].y).toBe(12.0);
  });

  it("should accurately compute tooth enamel structural carbonate to drinking water d18O", () => {
    // Equation: d18O_water = 1.590 * d18O_carbonate - 48.634
    const d18o = computeInferredWaterD18O(25.4);
    // 1.59 * 25.4 - 48.634 = 40.386 - 48.634 = -8.248 -> -8.25
    expect(d18o).toBeCloseTo(-8.25, 2);
  });

  it("should accurately compute scalp hair keratin d2H to drinking water equivalent", () => {
    // Equation: d2H_water = (d2H_hair + 26.0) / 0.91
    const d2h = computeInferredWaterD2H(-78.4);
    // (-78.4 + 26.0) / 0.91 = -52.4 / 0.91 = -57.582 -> -57.58
    expect(d2h).toBeCloseTo(-57.58, 2);
  });

  it("should accurately calculate Deuterium Excess (d) based on Craig GMWL", () => {
    // Equation: d = d2H_water - 8.0 * d18O_water
    const excess = computeDeuteriumExcess(-57.58, -8.25);
    // -57.58 - 8.0 * (-8.25) = -57.58 + 66.0 = +8.42
    expect(excess).toBeCloseTo(8.42, 2);
  });

  it("should accurately calculate ZTR heavy mineral maturity index", () => {
    // Equation: ZTR = (Zircon + Tourmaline + Rutile) / TotalHeavy * 100
    const ztr = computeZtrIndex(0.45, 0.28, 0.22, 10.0);
    // (0.45 + 0.28 + 0.22) / 10.0 * 100 = 0.95 / 10 * 100 = 9.5%
    expect(ztr).toBeCloseTo(9.5, 1);
  });

  it("should evaluate Bray-Curtis ecological dissimilarity for palynological assemblages", () => {
    // Identical assemblages must yield BC = 0.0
    const bcIdentical = computeBrayCurtis([160, 90, 30], [160, 90, 30]);
    expect(bcIdentical).toBe(0.0);

    // Completely disjoint assemblages must yield BC = 1.0
    const bcDisjoint = computeBrayCurtis([100, 0], [0, 100]);
    expect(bcDisjoint).toBe(1.0);
  });

  it("should calculate Canter diameter as maximum pairwise Euclidean distance between crime sites", () => {
    const diameter = computeCanterDiameter(GOLDEN_VECTOR_03);
    // Sites span across grid [4.0, 12.0] to [11.2, 13.0] and [5.8, 8.1]
    // Max distance is between C4(11.2, 13.0) and C5(5.8, 8.1): sqrt(5.4^2 + 4.9^2) = sqrt(29.16 + 24.01) = sqrt(53.17) = 7.29
    expect(diameter).toBeGreaterThan(7.0);
    expect(diameter).toBeLessThan(10.0);
  });

  it("should compute multi-criteria Bayesian fusion composite LR with layer weights", () => {
    const fused = computeFusedGeoLR(32500, 4500, 9770, 28.2, {
      iso: 1.0,
      soil: 1.0,
      palyno: 1.0,
      rossmo: 1.0,
    });
    // 32500 * 4500 * 9770 * 28.2 = 4.03e13 -> clamped at upper bound 1e12
    expect(fused).toBe(1e12);

    const fusedUnit = computeFusedGeoLR(10, 10, 10, 10, {
      iso: 0.5,
      soil: 0.5,
      palyno: 0.5,
      rossmo: 0.5,
    });
    // sqrt(10) * sqrt(10) * sqrt(10) * sqrt(10) = 100
    expect(fusedUnit).toBeCloseTo(100, 1);
  });
});
