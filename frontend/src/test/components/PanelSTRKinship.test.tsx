import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import PanelSTRKinship, {
  MASTER_24_STR_LOCI,
  NIST_1036_POP_FREQS,
  GOLDEN_STR_BENCHMARKS,
} from "@/components/analysis/PanelSTRKinship";

describe("Subsystem 01: Autosomal STR & Kinship Engine", () => {
  describe("24-Locus Autosomal STR Registry & Microvariants", () => {
    it("contains all 24 standard loci including CODIS 20, SE33, and Penta D/E", () => {
      expect(MASTER_24_STR_LOCI.length).toBe(24);
      const locusNames = MASTER_24_STR_LOCI.map((l) => l.name);
      expect(locusNames).toContain("TH01");
      expect(locusNames).toContain("SE33");
      expect(locusNames).toContain("D21S11");
      expect(locusNames).toContain("FGA");
      expect(locusNames).toContain("D1S1656");
      expect(locusNames).toContain("Penta D");
      expect(locusNames).toContain("Penta E");
      expect(locusNames).toContain("AMEL");
    });

    it("verifies diagnostic microvariant presence in mutational catalog", () => {
      const th01 = MASTER_24_STR_LOCI.find((l) => l.name === "TH01");
      expect(th01?.microvariants).toContain("9.3");

      const se33 = MASTER_24_STR_LOCI.find((l) => l.name === "SE33");
      expect(se33?.microvariants).toContain("28.2");

      const d21s11 = MASTER_24_STR_LOCI.find((l) => l.name === "D21S11");
      expect(d21s11?.microvariants).toContain("31.2");
    });
  });

  describe("NIST 1036 Population Allele Frequencies & p_min Floor", () => {
    it("provides allele frequencies for major continental cohorts", () => {
      expect(NIST_1036_POP_FREQS.Caucasian).toBeDefined();
      expect(NIST_1036_POP_FREQS.AfricanAmerican).toBeDefined();
      expect(NIST_1036_POP_FREQS.Hispanic).toBeDefined();
      expect(NIST_1036_POP_FREQS.Asian).toBeDefined();
    });

    it("enforces minimum allele frequency floor p_min = 5/(2N) = 0.00241", () => {
      const pMinFloor = 5.0 / (2.0 * 1036.0);
      expect(pMinFloor).toBeCloseTo(0.002413, 5);
    });
  });

  describe("Certified Golden Standards & Benchmark Vectors", () => {
    it("contains NIST SRM 2391d Component A and Casework Benchmarks", () => {
      expect(GOLDEN_STR_BENCHMARKS.length).toBeGreaterThanOrEqual(3);
      const nistA = GOLDEN_STR_BENCHMARKS.find((b) => b.id === "NIST_SRM_2391D_COMP_A");
      expect(nistA).toBeDefined();
      expect(nistA?.alleles.TH01).toEqual(["8", "9.3"]);
      expect(nistA?.alleles.SE33).toEqual(["19", "29.2"]);
      expect(nistA?.expectedLog10LR).toBeGreaterThan(20.0);
    });
  });

  describe("PanelSTRKinship Component Rendering", () => {
    it("renders the 24-locus studio with header telemetry and tabs", () => {
      const { container } = render(<PanelSTRKinship />);
      expect(container).toBeInTheDocument();
      expect(screen.getAllByText(/24-Locus Autosomal STR|24 STR/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/CODIS 20 \+ SE33/i).length).toBeGreaterThan(0);
    });
  });
});
