import { describe, it, expect } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useBioMathWorker } from "@/hooks/useBioMathWorker";
import { GOLDEN_CASEWORK_PRESETS } from "@/utils/caseworkPresets";

describe("useBioMathWorker Hook", () => {
  it("calculates SNP BGA and HIrisPlex traits asynchronously with fallback parity", async () => {
    const { result } = renderHook(() => useBioMathWorker());
    const preset = GOLDEN_CASEWORK_PRESETS[0];

    let output: any;
    await act(async () => {
      output = await result.current.calculateSnpTraitsAsync(preset.snpDosages);
    });

    expect(output).toBeDefined();
    expect(output.bga).toHaveProperty("dominantAncestryLabel");
    expect(output.bga).toHaveProperty("dominantProbability");
    expect(output.bga.dominantProbability).toBeGreaterThan(0.5);

    expect(output.hiris).toHaveProperty("predictedEyeColor");
    expect(output.hiris).toHaveProperty("predictedHairColor");
    expect(output.hiris).toHaveProperty("predictedSkinPhototype");
  });

  it("calculates Y-STR haplogroup and match stats asynchronously", async () => {
    const { result } = renderHook(() => useBioMathWorker());
    const preset = GOLDEN_CASEWORK_PRESETS[0];

    if (preset.ystrProfile) {
      let output: any;
      await act(async () => {
        output = await result.current.calculateYstrMetricsAsync(preset.ystrProfile!);
      });

      expect(output).toBeDefined();
      expect(output.haplogroup).toHaveProperty("predictedHaplogroup");
      expect(output.clopper).toHaveProperty("upperBound");
      expect(output.clopper).toHaveProperty("likelihoodRatio");
    }
  });

  it("calculates mtDNA EMPOP alignments asynchronously", async () => {
    const { result } = renderHook(() => useBioMathWorker());
    const rawMutations = ["263G", "315.1C", "16519C"];

    let output: any;
    await act(async () => {
      output = await result.current.calculateMtdnaAlignmentAsync(rawMutations);
    });

    expect(output).toBeDefined();
    expect(output.aligned.length).toBeGreaterThan(0);
    expect(output.haplogroup).toHaveProperty("predictedHaplogroup");
    expect(output.matchStats).toHaveProperty("likelihoodRatio");
  });
});
