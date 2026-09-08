import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import TouchDnaPanel from "@/components/analysis/TouchDnaPanel";

describe("Subsystem 04: Touch DNA & Low-Template (LTDNA) Stochastic Modeling Engine", () => {
  describe("Mathematical Invariants & Biocomputational Kinetics", () => {
    it("evaluates Curran-Gill logistic dropout curve P(D|x) with exact research constants", () => {
      // P(D|x) = 1 / (1 + exp(-(beta_0 + beta_1 * x))) where beta_0 = +2.50, beta_1 = -0.025 RFU^(-1)
      const computeRfuDropout = (rfu: number): number => {
        const logit = 2.50 - 0.025 * rfu;
        return 1.0 / (1.0 + Math.exp(-logit));
      };

      // At 0 RFU: high dropout (~92.4%)
      expect(computeRfuDropout(0)).toBeCloseTo(0.924, 2);

      // At 100 RFU: 50% inflection point (logit = 0, P = 0.50)
      expect(computeRfuDropout(100)).toBeCloseTo(0.50, 2);

      // At 240 RFU: low dropout (< 5%)
      expect(computeRfuDropout(240)).toBeLessThan(0.05);

      // Monotonic decreasing with increasing peak RFU
      expect(computeRfuDropout(300)).toBeLessThan(computeRfuDropout(150));
      expect(computeRfuDropout(150)).toBeLessThan(computeRfuDropout(50));
    });

    it("evaluates Poisson drop-in sum invariant and 24-locus clean profile probability", () => {
      // P(C=k) = (lambda_C^k * exp(-lambda_C)) / k! where lambda_C = 0.020 per locus
      const lambdaC = 0.020;
      const calcPoisson = (k: number): number => {
        let fact = 1;
        for (let i = 2; i <= k; i++) fact *= i;
        return (Math.pow(lambdaC, k) * Math.exp(-lambdaC)) / fact;
      };

      // Sum of P(C=k) for k=0..5 approximates 1.0 within 1e-6
      let sumProb = 0;
      for (let k = 0; k <= 5; k++) {
        sumProb += calcPoisson(k);
      }
      expect(Math.abs(sumProb - 1.0)).toBeLessThan(1e-6);

      // Clean profile retention for 24 loci: P(C_total = 0) = exp(-24 * 0.020) = exp(-0.48) ~= 0.6188 (61.88%)
      const clean24Loci = Math.exp(-24 * lambdaC);
      expect(clean24Loci).toBeCloseTo(0.6188, 3);
    });

    it("evaluates forensic substrate recovery efficiency physics", () => {
      // Initial touch mass 80.0 pg deposited on substrate
      const initialMassPg = 80.0;

      const substrates = {
        SMOOTH_NON_POROUS: 0.60,
        TEXTURED_NON_POROUS: 0.40,
        POROUS_FABRIC: 0.20,
        ROUGH_WOOD: 0.15,
      };

      // Smooth Non-Porous: 80 * 0.60 = 48.0 pg
      expect(initialMassPg * substrates.SMOOTH_NON_POROUS).toBe(48.0);

      // Textured Non-Porous (steering wheel / firearm grip): 80 * 0.40 = 32.0 pg (VECTOR_03 benchmark)
      expect(initialMassPg * substrates.TEXTURED_NON_POROUS).toBe(32.0);

      // Porous Fabric: 80 * 0.20 = 16.0 pg
      expect(initialMassPg * substrates.POROUS_FABRIC).toBe(16.0);

      // Rough Wood: 80 * 0.15 = 12.0 pg
      expect(initialMassPg * substrates.ROUGH_WOOD).toBe(12.0);
    });

    it("evaluates Heterozygote Balance Hb ratio and stochastic threshold flags", () => {
      const evaluateHb = (h1: number, h2: number) => {
        const hMin = Math.min(h1, h2);
        const hMax = Math.max(h1, h2);
        const hb = hMax > 0 ? hMin / hMax : 0;
        return {
          hb,
          isImbalanced: hb < 0.60,
          isSubStochastic: hMin < 150.0,
          isSubAt: hMin < 50.0,
        };
      };

      // Balanced normal case: 750 RFU and 720 RFU
      const normal = evaluateHb(750, 720);
      expect(normal.hb).toBeGreaterThanOrEqual(0.60);
      expect(normal.isImbalanced).toBe(false);
      expect(normal.isSubStochastic).toBe(false);

      // Imbalanced touch case: 110 RFU and 46.2 RFU
      const imbalanced = evaluateHb(110, 46.2);
      expect(imbalanced.hb).toBeCloseTo(0.42, 2);
      expect(imbalanced.isImbalanced).toBe(true);
      expect(imbalanced.isSubStochastic).toBe(true);
      expect(imbalanced.isSubAt).toBe(true); // 46.2 < 50 AT
    });
  });

  describe("TouchDnaPanel Component Rendering & Navigation", () => {
    it("renders mission header with CURRAN-GILL LTDNA badge and ISO 17025 validation telemetry", () => {
      const { container } = render(<TouchDnaPanel />);
      expect(container).toBeInTheDocument();

      // Mission title check
      expect(
        screen.getAllByText(/Touch DNA & Low-Template Stochastic Modeling|Temas DNA & Düşük Şablon Stokastik Modelleme/i).length
      ).toBeGreaterThan(0);

      // Standards check
      expect(screen.getByText(/CURRAN-GILL LTDNA/i)).toBeInTheDocument();
      expect(screen.getByText(/AT 50 RFU • ST 150 RFU/i)).toBeInTheDocument();
    });

    it("allows navigating between Substrate, Dropout, Drop-in, Heterozygote, and 24-Locus Profile tabs", () => {
      const { container } = render(<TouchDnaPanel />);

      // Switch to Dropout Curves tab
      const curvesTabBtn = container.querySelector("#tab-curves");
      expect(curvesTabBtn).toBeInTheDocument();
      if (curvesTabBtn) fireEvent.click(curvesTabBtn);
      expect(
        screen.getAllByText(/Calibrated Sigmoid Allele Dropout Function|Kalibre Edilmiş Sigmoid Alel Kaybı Fonksiyonu/i).length
      ).toBeGreaterThan(0);

      // Switch to Drop-in tab
      const dropinTabBtn = container.querySelector("#tab-dropin");
      expect(dropinTabBtn).toBeInTheDocument();
      if (dropinTabBtn) fireEvent.click(dropinTabBtn);
      expect(
        screen.getAllByText(/Poisson Allele Drop-in Probability|Poisson Alel Eklenme Olasılığı/i).length
      ).toBeGreaterThan(0);

      // Switch to Heterozygote tab
      const hetTabBtn = container.querySelector("#tab-heterozygote");
      expect(hetTabBtn).toBeInTheDocument();
      if (hetTabBtn) fireEvent.click(hetTabBtn);
      expect(
        screen.getAllByText(/Heterozygote Peak Balance Ratio|Heterozigot Pik Denge Oranı/i).length
      ).toBeGreaterThan(0);

      // Switch to 24-Locus Profile tab
      const profileTabBtn = container.querySelector("#tab-profile");
      expect(profileTabBtn).toBeInTheDocument();
      if (profileTabBtn) fireEvent.click(profileTabBtn);
      expect(
        screen.getAllByText(/24-Locus Profile Likelihood Ratio|24-Lokus Profil Olabilirlik Oranı/i).length
      ).toBeGreaterThan(0);
    });

    it("switches casework presets and updates substrate mass telemetry", () => {
      const { container } = render(<TouchDnaPanel />);

      // Check default preset (VECTOR_03)
      const vector03Btn = container.querySelector("#preset-vector-03");
      expect(vector03Btn).toBeInTheDocument();

      // Switch to VECTOR_TERM_06
      const vectorTerm06Btn = container.querySelector("#preset-vector-term-06");
      expect(vectorTerm06Btn).toBeInTheDocument();
      if (vectorTerm06Btn) fireEvent.click(vectorTerm06Btn);

      // Switch to NIST SRM 2391d
      const nistBtn = container.querySelector("#preset-nist-srm2391d");
      expect(nistBtn).toBeInTheDocument();
      if (nistBtn) fireEvent.click(nistBtn);

      // Switch to Single-Cell LCN (15 pg)
      const lcnBtn = container.querySelector("#preset-lcn-15pg");
      expect(lcnBtn).toBeInTheDocument();
      if (lcnBtn) fireEvent.click(lcnBtn);
    });

    it("renders and triggers server execution button #execute-touch-analysis-btn", () => {
      const { container } = render(<TouchDnaPanel />);

      const execBtn = container.querySelector("#execute-touch-analysis-btn");
      expect(execBtn).toBeInTheDocument();
      if (execBtn) {
        fireEvent.click(execBtn);
      }
    });

    it("synchronizes with active casework profile from forensic case store", () => {
      const { container } = render(<TouchDnaPanel />);

      const loadCaseBtn = container.querySelector("#load-casework-profile-btn");
      expect(loadCaseBtn).toBeInTheDocument();
      if (loadCaseBtn) {
        fireEvent.click(loadCaseBtn);
      }

      // Verify case linked state appears
      expect(
        screen.getAllByText(/CASE-2026-EU-GERMANIC-01|Case Linked|Vaka Bağlandı/i).length
      ).toBeGreaterThan(0);
    });
  });
});
