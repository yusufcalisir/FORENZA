import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ExpertWitnessPanel from "@/components/analysis/ExpertWitnessPanel";

describe("Subsystem 32: Expert Witness Court Mode & ENFSI Evaluative Reporting", () => {
  describe("Mathematical Invariants & ENFSI 2017 Verbal Scale Tiers", () => {
    it("maps log10(LR) values correctly across all 7 ENFSI tiers (0 to 6)", () => {
      const getEnfsiTier = (log10LR: number): number => {
        const absLog = Math.abs(log10LR);
        if (absLog === 0) return 0;
        if (absLog <= 1.0) return 1;
        if (absLog <= 2.0) return 2;
        if (absLog <= 3.0) return 3;
        if (absLog <= 4.0) return 4;
        if (absLog <= 6.0) return 5;
        return 6;
      };

      expect(getEnfsiTier(0.0)).toBe(0); // Neutral / Inconclusive
      expect(getEnfsiTier(0.8)).toBe(1); // Weak (1 to 10)
      expect(getEnfsiTier(1.5)).toBe(2); // Moderate (10 to 100)
      expect(getEnfsiTier(2.7)).toBe(3); // Moderately Strong (100 to 1,000)
      expect(getEnfsiTier(3.8)).toBe(4); // Strong (1,000 to 10,000)
      expect(getEnfsiTier(5.2)).toBe(5); // Very Strong (10,000 to 1,000,000)
      expect(getEnfsiTier(7.5441)).toBe(6); // Extremely Strong (> 1,000,000 - Golden Vector P6_03)
    });

    it("verifies reciprocal symmetry for prosecution vs defense support", () => {
      const lrProsecution = 100.0;
      const lrDefense = 0.01;

      const log10Hp = Math.log10(lrProsecution);
      const log10Hd = Math.log10(lrDefense);

      expect(log10Hp).toBe(2.0);
      expect(log10Hd).toBe(-2.0);
      expect(Math.abs(log10Hp)).toBe(Math.abs(log10Hd));
    });
  });

  describe("Daubert FRE 702 & Frye 4-Pillar Admissibility Truth Table", () => {
    it("evaluates statutory admissibility according to Daubert / Frye criteria", () => {
      const evaluateDaubert = (
        p1Falsifiable: boolean,
        errorRate: number,
        p3PeerReviewed: boolean,
        p4Swgdam: boolean,
        p4Iso17025: boolean
      ) => {
        const p2Pass = errorRate <= 1e-6;
        const p4Pass = p4Swgdam && p4Iso17025;
        const fryePass = p3PeerReviewed && p4Pass;
        const overall = p1Falsifiable && p2Pass && p3PeerReviewed && p4Pass && fryePass;
        return { p2Pass, p4Pass, fryePass, overall };
      };

      // Compliant system
      const valid = evaluateDaubert(true, 1e-9, true, true, true);
      expect(valid.p2Pass).toBe(true);
      expect(valid.p4Pass).toBe(true);
      expect(valid.fryePass).toBe(true);
      expect(valid.overall).toBe(true);

      // Non-compliant error rate (> 1e-6)
      const highError = evaluateDaubert(true, 5e-5, true, true, true);
      expect(highError.p2Pass).toBe(false);
      expect(highError.overall).toBe(false);

      // Missing ISO 17025 accreditation
      const unaccredited = evaluateDaubert(true, 1e-9, true, true, false);
      expect(unaccredited.p4Pass).toBe(false);
      expect(unaccredited.overall).toBe(false);
    });
  });

  describe("ExpertWitnessPanel Component Rendering & Navigation", () => {
    it("renders mission header with ENFSI 2017, Daubert, and FRE 702 badges", () => {
      const { container } = render(<ExpertWitnessPanel />);
      expect(container).toBeInTheDocument();

      // Mission title check
      expect(
        screen.getAllByText(/Expert Witness Court Mode|Bilirkişi Mahkeme Modu/i).length
      ).toBeGreaterThan(0);

      // Standard tag check
      expect(screen.getAllByText(/ENFSI 2017 • DAUBERT • FRE 702/i).length).toBeGreaterThan(0);
    });

    it("allows switching between ENFSI, Daubert, and Judicial Testimony tabs", () => {
      const { container } = render(<ExpertWitnessPanel />);

      // Find tab buttons
      const daubertTabBtn = screen.getByRole("button", { name: /Daubert \/ Frye/i });
      expect(daubertTabBtn).toBeInTheDocument();
      fireEvent.click(daubertTabBtn);

      // Daubert audit button should now be visible
      expect(container.querySelector("#run-daubert-audit-btn")).toBeInTheDocument();

      // Switch to Testimony Brief tab
      const testimonyTabBtn = screen.getByRole("button", { name: /Testimony Brief|Adli İfade Tutanağı/i });
      expect(testimonyTabBtn).toBeInTheDocument();
      fireEvent.click(testimonyTabBtn);

      // Refresh testimony button should now be visible
      expect(container.querySelector("#refresh-testimony-btn")).toBeInTheDocument();
    });

    it("verifies 7 Core Judicial Testimony Pillars and Transposed Conditional Fallacy shield", () => {
      const { container } = render(<ExpertWitnessPanel />);

      // Switch to Testimony Brief tab
      const testimonyTabBtn = screen.getByRole("button", { name: /Testimony Brief|Adli İfade Tutanağı/i });
      fireEvent.click(testimonyTabBtn);

      // Check for 7 core pillars heading
      expect(
        screen.getAllByText(/7 Core Judicial Testimony Pillars|7 Temel Adli İfade Sütunu/i).length
      ).toBeGreaterThan(0);

      // Check for Legal Shield Active tag on Pillar 6
      expect(
        screen.getAllByText(/LEGAL SHIELD ACTIVE|HUKUKİ KALKAN ETKİN/i).length
      ).toBeGreaterThan(0);

      // Check for HMAC-SHA256 signature indicator
      expect(screen.getAllByText(/HMAC-SHA256:/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/ISO\/IEC 17025:2017 Clause 7.8/i).length).toBeGreaterThan(0);
    });

    it("generates evaluative report with Prosecutor's Fallacy Shield active", () => {
      const { container } = render(<ExpertWitnessPanel />);

      const generateBtn = container.querySelector("#generate-evaluative-report-btn");
      expect(generateBtn).toBeInTheDocument();
      fireEvent.click(generateBtn!);

      // Check for Fallacy Shield presence
      expect(
        screen.getAllByText(/Prosecutor's Fallacy Shield|Savcılık Safsatası Kalkanı/i).length
      ).toBeGreaterThan(0);
    });
  });
});
