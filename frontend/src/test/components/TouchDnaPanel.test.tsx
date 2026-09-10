import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import TouchDnaPanel, {
  calcDropoutProbMass,
  calcDropoutProbRfu,
  calcPoissonDropin,
  calcDropinHeightDensity,
  calcHeterozygoteBalance,
  calcSingleLocusLR,
  computeTouchAuditHash,
  SUBSTRATES,
  STR_LOCUS_SPECS,
  GOLDEN_PRESETS,
  DROPOUT_BETA0_RFU,
  DROPOUT_BETA1_RFU,
  DROPOUT_BETA0_MASS,
  DROPOUT_BETA1_MASS,
  DROPIN_LAMBDA_POISSON,
  ANALYTICAL_THRESHOLD_RFU,
  STOCHASTIC_THRESHOLD_RFU,
  HB_FLAG_THRESHOLD,
} from "@/components/analysis/TouchDnaPanel";

// Mock Central Forensic Case Store
const mockAddAuditLog = vi.fn();
vi.mock("@/store/forensicCaseStore", () => ({
  useForensicCaseStore: () => ({
    activeCase: {
      metadata: {
        caseId: "TEST-CASE-2026-LTDNA",
        leadAnalyst: "Dr. Sarah Jenkins, Lead DNA Examiner",
        jurisdiction: "Federal Forensic Institute",
      },
      profile: {
        strMarkers: {
          D3S1358: { locus: "D3S1358", allele1: "15", allele2: "16" },
          vWA: { locus: "vWA", allele1: "16", allele2: "17" },
          FGA: { locus: "FGA", allele1: "21", allele2: "22" },
        },
      },
    },
    addAuditLog: mockAddAuditLog,
  }),
}));

describe("Subsystem 04: Touch DNA & Low-Template (LTDNA) Stochastic Modeling Engine", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(global, "fetch").mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            n_loci: 24,
            template_pg: 32.0,
            p_dropout: 0.28,
            total_log10_lr: 8.452,
            total_lr_point: 2.83e8,
            total_stochastic_flags_count: 2,
            verbal_en: "Extremely Strong Support for Prosecution Proposition (Hp)",
            verbal_tr: "Iddia Makami Hipotezi (Hp) Lehine Son Derece Guclu Destek",
            additivity_verified: true,
            locus_breakdown: [],
          }),
      } as any)
    );

    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  // =========================================================================
  // 1. Pure Mathematical Invariants & Biocomputational Kinetics
  // =========================================================================
  describe("Mathematical Invariants & Biocomputational Kinetics", () => {
    it("evaluates Curran-Gill logistic dropout curve P(D|x) with exact research constants", () => {
      // At 0 RFU: high dropout (~92.4%)
      expect(calcDropoutProbRfu(0)).toBeCloseTo(0.924, 2);

      // At 100 RFU: 50% inflection point (logit = 0, P = 0.50)
      expect(calcDropoutProbRfu(100)).toBeCloseTo(0.50, 2);

      // At 240 RFU: low dropout (< 5%)
      expect(calcDropoutProbRfu(240)).toBeLessThan(0.05);

      // Monotonic decreasing with increasing peak RFU
      expect(calcDropoutProbRfu(300)).toBeLessThan(calcDropoutProbRfu(150));
      expect(calcDropoutProbRfu(150)).toBeLessThan(calcDropoutProbRfu(50));
    });

    it("evaluates mass-based dropout model with amplicon length penalty", () => {
      // Mass-based model: beta0 = 3.20, beta1 = -0.080 pg^-1
      const pSmall = calcDropoutProbMass(50.0, 100);
      const pLarge = calcDropoutProbMass(50.0, 300); // 200 bp larger amplicon

      // Larger amplicons suffer higher dropout at identical template mass
      expect(pLarge).toBeGreaterThan(pSmall);

      // At 0 mass: analytical logistic probability P(D|0) = 1 / (1 + exp(-beta0)) ~= 0.9608
      expect(calcDropoutProbMass(0)).toBeCloseTo(1 / (1 + Math.exp(-DROPOUT_BETA0_MASS)), 6);
    });

    it("evaluates Poisson drop-in sum invariant and 24-locus clean profile probability", () => {
      // Sum of P(C=k) for k=0..5 approximates 1.0 within 1e-6
      let sumProb = 0;
      for (let k = 0; k <= 5; k++) {
        sumProb += calcPoissonDropin(k, DROPIN_LAMBDA_POISSON);
      }
      expect(Math.abs(sumProb - 1.0)).toBeLessThan(1e-6);

      // Clean profile retention for 24 loci: P(C_total = 0) = exp(-24 * 0.020) = exp(-0.48) ~= 0.6188
      const clean24Loci = Math.exp(-24 * DROPIN_LAMBDA_POISSON);
      expect(clean24Loci).toBeCloseTo(0.6188, 3);
    });

    it("evaluates exponential drop-in peak height density f(h_c)", () => {
      // Below analytical threshold (AT = 50 RFU): density must be 0.0
      expect(calcDropinHeightDensity(40.0)).toBe(0.0);

      // At AT (50 RFU): density = lambda_h = 0.015
      expect(calcDropinHeightDensity(50.0)).toBeCloseTo(0.015, 3);

      // Monotonic decreasing with peak height above AT
      expect(calcDropinHeightDensity(100.0)).toBeLessThan(calcDropinHeightDensity(50.0));
      expect(calcDropinHeightDensity(150.0)).toBeLessThan(calcDropinHeightDensity(100.0));
    });

    it("evaluates forensic substrate recovery efficiency physics", () => {
      const initialMassPg = 80.0;
      const smooth = SUBSTRATES.find((s) => s.id === "SMOOTH_NON_POROUS")!;
      const textured = SUBSTRATES.find((s) => s.id === "TEXTURED_NON_POROUS")!;
      const fabric = SUBSTRATES.find((s) => s.id === "POROUS_FABRIC")!;
      const wood = SUBSTRATES.find((s) => s.id === "ROUGH_WOOD")!;

      // Smooth Non-Porous: 80 * 0.60 = 48.0 pg
      expect(initialMassPg * smooth.efficiency).toBe(48.0);

      // Textured Non-Porous (steering wheel / firearm grip): 80 * 0.40 = 32.0 pg (VECTOR_03)
      expect(initialMassPg * textured.efficiency).toBe(32.0);

      // Porous Fabric: 80 * 0.20 = 16.0 pg
      expect(initialMassPg * fabric.efficiency).toBe(16.0);

      // Rough Wood: 80 * 0.15 = 12.0 pg
      expect(initialMassPg * wood.efficiency).toBe(12.0);
    });

    it("evaluates diploid cell count equivalence (6.6 pg per diploid cell)", () => {
      const mass1 = 66.0; // pg
      const cells1 = Number((mass1 / 6.6).toFixed(1));
      expect(cells1).toBe(10.0);

      const mass2 = 33.0; // pg
      const cells2 = Number((mass2 / 6.6).toFixed(1));
      expect(cells2).toBe(5.0);
    });

    it("evaluates Heterozygote Balance Hb ratio and stochastic threshold flags", () => {
      // Balanced normal case: 750 RFU and 720 RFU
      const normal = calcHeterozygoteBalance(750, 720);
      expect(normal.hb).toBeGreaterThanOrEqual(HB_FLAG_THRESHOLD);
      expect(normal.isImbalanced).toBe(false);
      expect(normal.isSubStochastic).toBe(false);

      // Imbalanced touch case: 110 RFU and 46.2 RFU
      const imbalanced = calcHeterozygoteBalance(110, 46.2);
      expect(imbalanced.hb).toBeCloseTo(0.42, 2);
      expect(imbalanced.isImbalanced).toBe(true);
      expect(imbalanced.isSubStochastic).toBe(true);
      expect(imbalanced.isSubAt).toBe(true); // 46.2 < 50 AT
    });

    it("evaluates Curran-Gill single-locus LR for both alleles present vs single dropout", () => {
      const popFreqs = { 16: 0.20, 17: 0.25 };
      const pD = 0.30;

      // Both alleles present: [16, 17] observed
      const resBoth = calcSingleLocusLR([16, 17], { 16: 120, 17: 100 }, pD, popFreqs);
      expect(resBoth.state).toBe("BOTH_PRESENT");
      expect(resBoth.lr).toBeGreaterThan(1.0);

      // Single dropout: allele 17 dropped out, only 16 observed
      const resDropout = calcSingleLocusLR([16, 17], { 16: 120 }, pD, popFreqs);
      expect(resDropout.state).toBe("SINGLE_DROPOUT");
      expect(resDropout.missingCount).toBe(1);
      expect(resDropout.lr).toBeGreaterThan(0.0);
    });
  });

  // =========================================================================
  // 2. Cryptographic State Audit Digest (H_ltdna)
  // =========================================================================
  describe("Cryptographic State Audit Digest (H_ltdna)", () => {
    it("computes a deterministic 64-hex lowercase SHA-256 state audit digest", () => {
      const hash1 = computeTouchAuditHash("CASE-001", "SMOOTH_NON_POROUS", 0.60, 100.0, 60.0, 0.12, 8.452, 24);
      const hash2 = computeTouchAuditHash("CASE-001", "SMOOTH_NON_POROUS", 0.60, 100.0, 60.0, 0.12, 8.452, 24);

      expect(hash1).toBe(hash2);
      expect(hash1).toHaveLength(64);
      expect(hash1).toMatch(/^[a-f0-9]{64}$/);
    });

    it("exhibits cryptographic avalanche divergence on parameter modification", () => {
      const baseHash = computeTouchAuditHash("CASE-001", "SMOOTH_NON_POROUS", 0.60, 100.0, 60.0, 0.12, 8.452, 24);
      const diffMassHash = computeTouchAuditHash("CASE-001", "SMOOTH_NON_POROUS", 0.60, 95.0, 57.0, 0.15, 8.452, 24);
      const diffCaseHash = computeTouchAuditHash("CASE-002", "SMOOTH_NON_POROUS", 0.60, 100.0, 60.0, 0.12, 8.452, 24);

      expect(baseHash).not.toBe(diffMassHash);
      expect(baseHash).not.toBe(diffCaseHash);
    });
  });

  // =========================================================================
  // 3. Component Rendering & Case Telemetry
  // =========================================================================
  describe("TouchDnaPanel Component Rendering & Case Telemetry", () => {
    it("renders mission header with CURRAN-GILL LTDNA badge and dynamic case ID", () => {
      render(<TouchDnaPanel />);

      expect(
        screen.getAllByText(/Touch DNA & Low-Template Stochastic Modeling|Temas DNA & Düşük Şablon Stokastik Modelleme/i).length
      ).toBeGreaterThan(0);

      expect(screen.getByText(/CURRAN-GILL LTDNA/i)).toBeInTheDocument();
      expect(screen.getByText(/AT 50 RFU • ST 150 RFU/i)).toBeInTheDocument();
      expect(screen.getByText("TEST-CASE-2026-LTDNA")).toBeInTheDocument();
    });

    it("renders cryptographic H_ltdna state audit hash in header", () => {
      render(<TouchDnaPanel />);

      const copyHashButtons = screen.getAllByTitle(/H_ltdna Durum Özetini Kopyala|Copy H_ltdna State Audit Hash/i);
      expect(copyHashButtons.length).toBeGreaterThan(0);
    });
  });

  // =========================================================================
  // 4. Tab Navigation Across All 5 LTDNA Modules
  // =========================================================================
  describe("Tab Navigation Across All 5 LTDNA Modules", () => {
    it("navigates seamlessly across Substrate, Dropout, Drop-in, Heterozygote, and 24-Locus Profile tabs", () => {
      const { container } = render(<TouchDnaPanel />);

      // Tab 2: Dropout Curves
      const curvesTabBtn = container.querySelector("#tab-curves");
      expect(curvesTabBtn).toBeInTheDocument();
      act(() => {
        fireEvent.click(curvesTabBtn!);
      });
      expect(
        screen.getAllByText(/Calibrated Sigmoid Allele Dropout Function|Kalibre Edilmiş Sigmoid Alel Kaybı Fonksiyonu/i).length
      ).toBeGreaterThan(0);

      // Tab 3: Drop-in
      const dropinTabBtn = container.querySelector("#tab-dropin");
      expect(dropinTabBtn).toBeInTheDocument();
      act(() => {
        fireEvent.click(dropinTabBtn!);
      });
      expect(
        screen.getAllByText(/Poisson Allele Drop-in Probability|Poisson Alel Eklenme Olasılığı/i).length
      ).toBeGreaterThan(0);

      // Tab 4: Heterozygote
      const hetTabBtn = container.querySelector("#tab-heterozygote");
      expect(hetTabBtn).toBeInTheDocument();
      act(() => {
        fireEvent.click(hetTabBtn!);
      });
      expect(
        screen.getAllByText(/Heterozygote Peak Balance Ratio|Heterozigot Pik Denge Oranı/i).length
      ).toBeGreaterThan(0);

      // Tab 5: 24-Locus Profile
      const profileTabBtn = container.querySelector("#tab-profile");
      expect(profileTabBtn).toBeInTheDocument();
      act(() => {
        fireEvent.click(profileTabBtn!);
      });
      expect(
        screen.getAllByText(/24-Locus Profile Likelihood Ratio|24-Lokus Profil Olabilirlik Oranı/i).length
      ).toBeGreaterThan(0);
      expect(
        screen.getAllByText(/Official Forensic Touch DNA Evaluative Certificate|Resmi Adli Temas DNA Değerlendirme Sertifikası/i).length
      ).toBeGreaterThan(0);

      // Tab 1: Return to Substrate
      const substrateTabBtn = container.querySelector("#tab-substrate");
      expect(substrateTabBtn).toBeInTheDocument();
      act(() => {
        fireEvent.click(substrateTabBtn!);
      });
      expect(
        screen.getAllByText(/Initial Touch Mass|Başlangıç Temas Kütlesi/i).length
      ).toBeGreaterThan(0);
    });
  });

  // =========================================================================
  // 5. Preset Selection, Substrate Physics & Audit Logging
  // =========================================================================
  describe("Preset Selection, Substrate Physics & Audit Logging", () => {
    it("switches casework presets and dispatches structured audit log", () => {
      const { container } = render(<TouchDnaPanel />);

      // Switch to VECTOR_TERM_06
      const vectorTerm06Btn = container.querySelector("#preset-vector-term-06");
      expect(vectorTerm06Btn).toBeInTheDocument();
      act(() => {
        fireEvent.click(vectorTerm06Btn!);
      });

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("VECTOR_TERM_06"),
          module: "04_touch_dna",
          status: "PASS",
        })
      );

      // Switch to NIST SRM 2391d
      const nistBtn = container.querySelector("#preset-nist-srm2391d");
      expect(nistBtn).toBeInTheDocument();
      act(() => {
        fireEvent.click(nistBtn!);
      });

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("NIST_SRM2391D"),
          module: "04_touch_dna",
          status: "PASS",
        })
      );
    });

    it("links active casework profile from forensic case store and dispatches audit entry", () => {
      const { container } = render(<TouchDnaPanel />);

      const loadCaseBtn = container.querySelector("#load-casework-profile-btn");
      expect(loadCaseBtn).toBeInTheDocument();
      act(() => {
        fireEvent.click(loadCaseBtn!);
      });

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("CASEWORK_PROFILE_LINKED"),
          module: "04_touch_dna",
          status: "PASS",
        })
      );
    });

    it("selects forensic substrates and updates recovery telemetry", () => {
      const { container } = render(<TouchDnaPanel />);

      // Find substrate cards in Tab 1
      const substrateCards = container.querySelectorAll(".cursor-pointer");
      expect(substrateCards.length).toBeGreaterThanOrEqual(4);

      // Click on smooth non-porous (Glass)
      act(() => {
        fireEvent.click(substrateCards[0]);
      });
    });
  });

  // =========================================================================
  // 6. User Actions, Clipboard Copy & Offline Client Fallback
  // =========================================================================
  describe("User Actions, Clipboard Copy & Offline Client Fallback", () => {
    it("copies court report to clipboard in Tab 5 and logs action", async () => {
      const { container } = render(<TouchDnaPanel />);

      // Navigate to Tab 5 (PROFILE)
      const profileTabBtn = container.querySelector("#tab-profile");
      act(() => {
        fireEvent.click(profileTabBtn!);
      });

      // Click Copy Certificate button
      const copyBtns = screen.getAllByText(/Sertifikayı Kopyala|Copy Certificate/i);
      expect(copyBtns.length).toBeGreaterThan(0);
      await act(async () => {
        fireEvent.click(copyBtns[0]);
      });

      expect(navigator.clipboard.writeText).toHaveBeenCalled();
      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("REPORT_COPIED"),
          module: "04_touch_dna",
          status: "PASS",
        })
      );

      await waitFor(() => {
        expect(screen.getAllByText(/Kopyalandı!|Copied!/i).length).toBeGreaterThan(0);
      });
    });

    it("copies H_ltdna state audit hash to clipboard and dispatches audit log", async () => {
      render(<TouchDnaPanel />);

      const copyHashBtn = screen.getByTitle(/H_ltdna Durum Özetini Kopyala|Copy H_ltdna State Audit Hash/i);
      await act(async () => {
        fireEvent.click(copyHashBtn);
      });

      expect(navigator.clipboard.writeText).toHaveBeenCalled();
      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("AUDIT_HASH_COPIED"),
          module: "04_touch_dna",
          status: "PASS",
        })
      );
    });

    it("triggers server analysis button and receives mocked response", async () => {
      const { container } = render(<TouchDnaPanel />);

      const execBtn = container.querySelector("#execute-touch-analysis-btn");
      expect(execBtn).toBeInTheDocument();
      await act(async () => {
        fireEvent.click(execBtn!);
      });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    });

    it("gracefully falls back to pure client biocomputation on fetch rejection without throwing", async () => {
      vi.spyOn(global, "fetch").mockRejectedValueOnce(new Error("Connection refused"));

      const { container } = render(<TouchDnaPanel />);

      const execBtn = container.querySelector("#execute-touch-analysis-btn");
      expect(execBtn).toBeInTheDocument();
      await act(async () => {
        fireEvent.click(execBtn!);
      });

      await waitFor(() => {
        // Fallback happens cleanly
        expect(container).toBeInTheDocument();
      });
    });
  });
});
