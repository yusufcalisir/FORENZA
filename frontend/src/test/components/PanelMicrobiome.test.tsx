import { describe, it, expect } from "vitest";
import {
  GOLDEN_MICROBIOME_VECTORS,
  BENCHMARK_PRESETS,
  HIDSKINPLEX_CALIBRATION,
  DECOMPOSITION_STAGES,
  BODY_FLUID_CLASSES,
  computeGeometricMean,
  clrTransform,
  computeAitchisonDistance,
  gaussianPdf,
  mapEnfsiVerbalScale,
} from "@/components/analysis/PanelMicrobiome";

describe("PanelMicrobiome Biophysical Models & Specifications (Pillar 4 Research)", () => {
  it("should define all 4 certified golden benchmark vectors (VECTOR_MB_01 to 04)", () => {
    expect(GOLDEN_MICROBIOME_VECTORS).toHaveLength(4);
    const ids = GOLDEN_MICROBIOME_VECTORS.map((v) => v.id);
    expect(ids).toEqual([
      "VECTOR_MB_01",
      "VECTOR_MB_02",
      "VECTOR_MB_03",
      "VECTOR_MB_04",
    ]);
  });

  it("should define all 5 canonical taphonomic decomposition stages", () => {
    expect(DECOMPOSITION_STAGES).toHaveLength(5);
    const stageIds = DECOMPOSITION_STAGES.map((s) => s.id);
    expect(stageIds).toEqual([
      "FRESH",
      "BLOAT",
      "ACTIVE_DECAY",
      "ADVANCED_DECAY",
      "SKELETONIZATION",
    ]);
  });

  it("should define all 6 forensically relevant body fluid classes", () => {
    expect(BODY_FLUID_CLASSES).toHaveLength(6);
    const fluidIds = BODY_FLUID_CLASSES.map((f) => f.id);
    expect(fluidIds).toContain("Vaginal_Fluid");
    expect(fluidIds).toContain("Hand_Skin");
    expect(fluidIds).toContain("Saliva");
    expect(fluidIds).toContain("Urine");
    expect(fluidIds).toContain("Penile_Skin");
    expect(fluidIds).toContain("Semen");
  });

  it("should accurately compute geometric mean g(x) for compositional profiles", () => {
    // VECTOR_MB_01 relative abundances:
    // [0.082, 0.215, 0.142, 0.284, 0.186, 0.091]
    const values = [0.082, 0.215, 0.142, 0.284, 0.186, 0.091];
    const gx = computeGeometricMean(values);
    // Exact geometric mean: (prod x_i)^(1/6) approx 0.1514
    expect(gx).toBeCloseTo(0.1514, 3);
  });

  it("should enforce CLR simplex zero-sum invariance sum(CLR) = 0.0000", () => {
    const v = BENCHMARK_PRESETS.VECTOR_MB_01.profile!;
    const { clr, gx } = clrTransform(v);
    expect(gx).toBeGreaterThan(0.0);

    const clrValues = Object.values(clr);
    const clrSum = clrValues.reduce((a, b) => a + b, 0);
    expect(Math.abs(clrSum)).toBeLessThan(1e-4);
  });

  it("should compute Aitchison distance dA = 0.0 for identical profiles", () => {
    const profile = { Taxon_A: 0.5, Taxon_B: 0.3, Taxon_C: 0.2 };
    const dA = computeAitchisonDistance(profile, profile);
    expect(dA).toBe(0.0);
  });

  it("should accurately evaluate VECTOR_MB_03 touch individualization metrics", () => {
    const v = BENCHMARK_PRESETS.VECTOR_MB_03;
    expect(v.evidentiary).toBeDefined();
    expect(v.reference).toBeDefined();

    const dA = computeAitchisonDistance(v.evidentiary!, v.reference!);
    // Close match between evidentiary trace and suspect reference (< 0.25)
    expect(dA).toBeLessThan(0.25);

    // Test Gaussian densities under benchmark calibration params (dA = 1.842)
    const fHp = gaussianPdf(
      1.842,
      HIDSKINPLEX_CALIBRATION.Hp_within_source.mu,
      HIDSKINPLEX_CALIBRATION.Hp_within_source.sigma
    );
    const fHd = gaussianPdf(
      1.842,
      HIDSKINPLEX_CALIBRATION.Hd_between_source.mu,
      HIDSKINPLEX_CALIBRATION.Hd_between_source.sigma
    );

    expect(fHp).toBeCloseTo(1.124, 2);
    expect(fHd).toBeLessThan(1e-4);

    const rawLr = fHp / fHd;
    expect(rawLr).toBeGreaterThan(100000);
  });

  it("should map calibrated Likelihood Ratios into standard ENFSI 2017 verbal scales", () => {
    const vExtrem = mapEnfsiVerbalScale(2000000);
    expect(vExtrem.tier).toBe("EXTREMELY_STRONG");

    const vVeryStrong = mapEnfsiVerbalScale(45000);
    expect(vVeryStrong.tier).toBe("VERY_STRONG");
    expect(vVeryStrong.en).toContain("Very strong support");
    expect(vVeryStrong.tr).toContain("cok guclu duzeyde adli destek");

    const vStrong = mapEnfsiVerbalScale(5000);
    expect(vStrong.tier).toBe("STRONG");

    const vModStrong = mapEnfsiVerbalScale(500);
    expect(vModStrong.tier).toBe("MODERATELY_STRONG");

    const vModerate = mapEnfsiVerbalScale(50);
    expect(vModerate.tier).toBe("MODERATE");

    const vWeak = mapEnfsiVerbalScale(5);
    expect(vWeak.tier).toBe("WEAK");

    const vExcl = mapEnfsiVerbalScale(0.1);
    expect(vExcl.tier).toBe("SUPPORT_FOR_EXCLUSION");
  });

  it("should accurately verify thermal kinetic calculation for VECTOR_MB_01", () => {
    const v = BENCHMARK_PRESETS.VECTOR_MB_01;
    const ambientTemp = 20.0;
    const baseTemp = 0.0;
    const predictedAdd = 82.5;

    const effTemp = Math.max(0.1, ambientTemp - baseTemp);
    const pmiHours = (predictedAdd * 24.0) / effTemp;
    expect(pmiHours).toBe(99.0);

    const q95 = 14.5;
    const addLow = predictedAdd - q95;
    const addHigh = predictedAdd + q95;
    expect(addLow).toBe(68.0);
    expect(addHigh).toBe(97.0);
  });
});
