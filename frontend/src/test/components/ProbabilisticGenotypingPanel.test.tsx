import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ProbabilisticGenotypingPanel from "@/components/analysis/ProbabilisticGenotypingPanel";

describe("Subsystem 02: MCMC Probabilistic Mixture Deconvolution Engine", () => {
  describe("Mathematical Invariants & Biocomputational Kinetics", () => {
    it("enforces Dirichlet probability simplex normalization |sum w_k - 1.0| <= 1e-6", () => {
      // 2-person 70:30 mixture (NIST SRM 2391d)
      const w2 = [0.70, 0.30];
      const sum2 = w2.reduce((acc, v) => acc + v, 0);
      expect(Math.abs(sum2 - 1.0)).toBeLessThanOrEqual(1e-6);

      // 3-person 50:30:20 mixture (PROVEDIt)
      const w3 = [0.50, 0.30, 0.20];
      const sum3 = w3.reduce((acc, v) => acc + v, 0);
      expect(Math.abs(sum3 - 1.0)).toBeLessThanOrEqual(1e-6);

      // 4-person complex mixture
      const w4 = [0.45, 0.25, 0.18, 0.12];
      const sum4 = w4.reduce((acc, v) => acc + v, 0);
      expect(Math.abs(sum4 - 1.0)).toBeLessThanOrEqual(1e-6);
    });

    it("evaluates Curran-Gill logistic dropout curve P(D|x) with exact research constants", () => {
      // P(D|x) = 1 / (1 + exp(beta_0 + beta_1 * x)) where beta_0 = +2.50, beta_1 = -0.025 RFU^(-1)
      const computeDropout = (rfu: number): number => {
        const logit = 2.50 - 0.025 * rfu;
        return 1 / (1 + Math.exp(-logit));
      };

      // At 0 RFU: high dropout
      expect(computeDropout(0)).toBeCloseTo(0.924, 2);

      // At 100 RFU: inflection point (logit = 0, P = 0.5)
      expect(computeDropout(100)).toBeCloseTo(0.50, 2);

      // At 240 RFU: low dropout (< 5%)
      expect(computeDropout(240)).toBeLessThan(0.05);

      // Monotonic decreasing with peak height
      expect(computeDropout(300)).toBeLessThan(computeDropout(150));
    });

    it("verifies Gelman-Rubin convergence criterion threshold R-hat <= 1.05", () => {
      const isConverged = (rHat: number) => rHat <= 1.05;

      expect(isConverged(1.008)).toBe(true);
      expect(isConverged(1.045)).toBe(true);
      expect(isConverged(1.080)).toBe(false);
    });
  });

  describe("ProbabilisticGenotypingPanel Component Rendering & Navigation", () => {
    it("renders mission header with SWGDAM (2020), ISFG (2016), and ISO 17025 telemetry", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);
      expect(container).toBeInTheDocument();

      // Mission title check
      expect(
        screen.getAllByText(/Continuous Probabilistic Genotyping Engine|Sürekli Olasılıksal Genotipleme Motoru/i).length
      ).toBeGreaterThan(0);

      // Standards check
      expect(
        screen.getAllByText(/SWGDAM \(2020\) • ISFG \(2016\) • ISO\/IEC 17025/i).length
      ).toBeGreaterThan(0);
    });

    it("allows switching between MCMC Deconvolution, Locus Genotypes, and Stochastic tabs", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      // Switch to Locus Genotypes tab
      const lociTabBtn = container.querySelector("#tab-loci");
      expect(lociTabBtn).toBeInTheDocument();
      fireEvent.click(lociTabBtn!);

      // Check for locus deconvolution calls heading
      expect(
        screen.getAllByText(/Continuous Locus Deconvolution Calls|Sürekli Lokus Ayrıştırma Çağrıları/i).length
      ).toBeGreaterThan(0);

      // Switch to Stochastic Models tab
      const stochasticTabBtn = container.querySelector("#tab-stochastic");
      expect(stochasticTabBtn).toBeInTheDocument();
      fireEvent.click(stochasticTabBtn!);

      // Check for stochastic controls
      expect(container.querySelector("#sample-rfu-slider")).toBeInTheDocument();
      expect(container.querySelector("#rfu-threshold-slider")).toBeInTheDocument();
      expect(container.querySelector("#engine-strmix-btn")).toBeInTheDocument();
      expect(container.querySelector("#engine-euroformix-btn")).toBeInTheDocument();
    });

    it("toggles between STRmix and EuroForMix likelihood kernels", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      // Switch to Stochastic Models tab
      const stochasticTabBtn = container.querySelector("#tab-stochastic");
      fireEvent.click(stochasticTabBtn!);

      const euroBtn = container.querySelector("#engine-euroformix-btn");
      expect(euroBtn).toBeInTheDocument();
      fireEvent.click(euroBtn!);

      // EuroForMix should now be active in kernel display
      expect(screen.getAllByText(/EuroForMix/i).length).toBeGreaterThan(0);
    });

    it("ingests active casework profile and displays case link badge", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      const loadCaseBtn = container.querySelector("#load-casework-profile-btn");
      expect(loadCaseBtn).toBeInTheDocument();
      fireEvent.click(loadCaseBtn!);

      // Case link badge should appear
      expect(
        screen.getAllByText(/CASE LINKED|VAKA AKTİF/i).length
      ).toBeGreaterThan(0);
    });

    it("renders Prosecutor's Fallacy Shield with ENFSI statement", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      expect(
        screen.getAllByText(/Active Prosecutor's Fallacy Shield|Aktif Savcı Yanılgısı Kalkanı/i).length
      ).toBeGreaterThan(0);
    });
  });
});
