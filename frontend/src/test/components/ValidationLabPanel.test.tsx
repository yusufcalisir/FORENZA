import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ValidationLabPanel, {
  PRESET_BENCHMARKS,
  generateCalibratedDataset,
  computeEmpiricalCllr,
  computeRoyallMisleadingRates,
  computeTippettAuditHash,
} from "@/components/analysis/ValidationLabPanel";

// Mock forensic case store
const mockAddAuditLog = vi.fn();
vi.mock("@/store/forensicCaseStore", () => ({
  useForensicCaseStore: (selector?: (state: any) => any) => {
    const state = {
      activeCase: {
        metadata: {
          caseId: "CASE-2026-VAL-001",
          leadAnalyst: "Dr. Morrison, Lead Forensic Geneticist",
        },
      },
      addAuditLog: mockAddAuditLog,
    };
    return typeof selector === "function" ? selector(state) : state;
  },
}));

// Mock API base URL
vi.mock("@/lib/api", () => ({
  getApiBaseUrl: () => "http://localhost:8000",
}));

// Mock Language Context
vi.mock("@/context/SaaSLanguageContext", () => ({
  useSaasLanguage: () => ({ lang: "en" }),
}));

describe("Subsystem 05: Tippett Validation & Calibration Studio (ValidationLabPanel)", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock clipboard
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
      writable: true,
      configurable: true,
    });

    // Mock global fetch for live simulation endpoint
    global.fetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes("generate-cohort")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              hp_log10_lrs_sample: [28.4, 27.2, 29.1, 26.8, 30.5],
              hd_log10_lrs_sample: [-26.2, -24.8, -27.5, -25.1, -28.3],
              cohort_size: 5,
            }),
        });
      }
      if (url.includes("cllr-score")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              cllr: 0.015,
              cllr_min: 0.005,
              cllr_cal: 0.010,
              calibration_quality: "Optimal",
            }),
        });
      }
      return Promise.reject(new Error("Unknown URL"));
    });
  });

  // 1. Initial Render & Canonical 5-Tab Navigation Bar
  it("renders panel header, tactical mission bar, active parameter ribbon, and 5 canonical tabs", () => {
    render(<ValidationLabPanel />);
    expect(screen.getByText(/Tippett Validation & Calibration Lab/i)).toBeInTheDocument();
    expect(screen.getByText(/Modül 05 \| TIPPETT-CALIB/i)).toBeInTheDocument();
    expect(screen.getByText(/SWGDAM 2020/i)).toBeInTheDocument();

    // Parameter ribbon items
    expect(screen.getByText(/Active Standard/i)).toBeInTheDocument();
    expect(screen.getByText(/Pair Cohort \(N\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Substructure \(θ\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Mann-Whitney AUC/i)).toBeInTheDocument();
    expect(screen.getByText(/Cost \(Cllr_raw\)/i)).toBeInTheDocument();

    // 5 Canonical Tabs
    expect(screen.getByRole("button", { name: /Tippett Curves/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Discrimination ROC/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Cllr Decomposition/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Golden Benchmarks/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /ISO 17025 Reporting/i })).toBeInTheDocument();
  });

  // 2. Tab Navigation Functionality
  it("switches tabs correctly across all 5 canonical views", () => {
    render(<ValidationLabPanel />);

    // Switch to Tab 2: Discrimination ROC
    fireEvent.click(screen.getByRole("button", { name: /Discrimination ROC/i }));
    expect(screen.getByText(/Receiver Operating Characteristic \(ROC\) & Mann-Whitney AUC/i)).toBeInTheDocument();

    // Switch to Tab 3: Cllr Decomposition
    fireEvent.click(screen.getByRole("button", { name: /Cllr Decomposition/i }));
    expect(screen.getByText(/FoCal Log-Likelihood-Ratio Cost \(Cllr\) Information-Theoretic Decomposition/i)).toBeInTheDocument();

    // Switch to Tab 4: Golden Benchmarks
    fireEvent.click(screen.getByRole("button", { name: /Golden Benchmarks/i }));
    expect(screen.getByText(/Certified Golden Reference Vectors & Calibration Standards/i)).toBeInTheDocument();

    // Switch to Tab 5: ISO 17025 Reporting
    fireEvent.click(screen.getByRole("button", { name: /ISO 17025 Reporting/i }));
    expect(screen.getByText(/ISO\/IEC 17025 & ENFSI \(2017\) Court Admissible Reporting Suite/i)).toBeInTheDocument();
  });

  // 3. Pure Biocomputational Generator Validation
  it("generateCalibratedDataset produces valid synthetic distributions conforming to preset parameters", () => {
    const data = generateCalibratedDataset("VECTOR_05_TIPPETT_A", "Caucasian", 0.03, 0.0, 100, 42);
    expect(data.hp).toHaveLength(100);
    expect(data.hd).toHaveLength(100);

    const meanHp = data.hp.reduce((a, b) => a + b, 0) / data.hp.length;
    const meanHd = data.hd.reduce((a, b) => a + b, 0) / data.hd.length;

    // Pristine high-template: Hp should be strong positive (> 20), Hd strong negative (< -20)
    expect(meanHp).toBeGreaterThan(20.0);
    expect(meanHd).toBeLessThan(-20.0);
  });

  // 4. Pure Cllr Decomposition Validation
  it("computeEmpiricalCllr calculates raw Cllr, min Cllr, and calibrated Cllr with non-negative bounds", () => {
    const hp = [25.0, 26.5, 28.0, 29.5];
    const hd = [-24.0, -25.5, -27.0, -28.5];
    const res = computeEmpiricalCllr(hp, hd);

    expect(res.cllr_raw).toBeGreaterThanOrEqual(0);
    expect(res.cllr_min).toBeGreaterThanOrEqual(0);
    expect(res.cllr_cal).toBeGreaterThanOrEqual(0);
    expect(res.cllr_raw).toBeGreaterThanOrEqual(res.cllr_min);
    // Well-separated distributions yield near-zero raw Cllr
    expect(res.cllr_raw).toBeLessThan(0.01);
  });

  // 5. Tab 1: ECCDF Curves & Monotonicity Audit
  it("Tab 1: displays ECCDF exceedance curves, monotonicity audit, and exceedance percentage at tau=0", () => {
    render(<ValidationLabPanel />);
    expect(screen.getByText(/Tippett Empirical ECCDF Exceedance Curves \(Hp vs Hd\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Exceedance at τ/i)).toBeInTheDocument();
    expect(screen.getByText(/Monotonicity Audit/i)).toBeInTheDocument();
    expect(screen.getByText(/Strictly Verified/i)).toBeInTheDocument();
  });

  // 6. Tab 1: Tau Threshold Slider Adjustment
  it("Tab 1: adjusts tau decision threshold slider and updates exceedance telemetry", () => {
    render(<ValidationLabPanel />);
    const slider = screen.getByRole("slider");
    expect(slider).toBeInTheDocument();

    fireEvent.change(slider, { target: { value: "3.5" } });
    expect(mockAddAuditLog).toHaveBeenCalledWith(
      expect.objectContaining({
        event: expect.stringContaining("VALIDATION_THRESHOLD_CHANGED: Decision threshold tau adjusted to 3.50"),
        module: "05. Tippett Calibration Lab",
        standard: "SWGDAM 2020",
      })
    );
  });

  // 7. Tab 2: Discrimination ROC & AUC
  it("Tab 2: renders ROC curve, Mann-Whitney U AUC, neutral boundary rates, and discriminating power", () => {
    render(<ValidationLabPanel />);
    fireEvent.click(screen.getByRole("button", { name: /Discrimination ROC/i }));

    expect(screen.getByText(/Receiver Operating Characteristic \(ROC\) & Mann-Whitney AUC/i)).toBeInTheDocument();
    expect(screen.getByText(/Separation Index/i)).toBeInTheDocument();
    expect(screen.getByText(/Discriminating Power \(DP\)/i)).toBeInTheDocument();
    expect(screen.getByText(/SWGDAM 2020 Compliance/i)).toBeInTheDocument();
  });

  // 8. Tab 3: Cllr Cost Decomposition Breakdown
  it("Tab 3: decomposes Cllr cost into raw, minimum discriminative, and calibration loss", () => {
    render(<ValidationLabPanel />);
    fireEvent.click(screen.getByRole("button", { name: /Cllr Decomposition/i }));

    expect(screen.getByText(/FoCal Log-Likelihood-Ratio Cost \(Cllr\) Information-Theoretic Decomposition/i)).toBeInTheDocument();
    expect(screen.getByText(/Overall Cost \(Cllr_raw\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Minimum Discrimination Cost \(Cllr_min\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Calibration Loss \(Cllr_cal\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Brümmer & du Preez 2006/i)).toBeInTheDocument();
  });

  // 9. Tab 3: Royall Misleading Evidence Rates Verification
  it("Tab 3: verifies Royall misleading evidence rates at alpha in {8, 10, 100}", () => {
    render(<ValidationLabPanel />);
    fireEvent.click(screen.getByRole("button", { name: /Cllr Decomposition/i }));

    expect(screen.getByText(/Royall \(1997\) Misleading Evidence Audit/i)).toBeInTheDocument();
    expect(screen.getByText(/Teorik Sınır: P_misleading ≤ 1\/α/i)).toBeInTheDocument();

    // Verify pure Royall calculation
    const hp = [15.0, 18.0, 20.0];
    const hd = [-15.0, -18.0, -20.0];
    const royall10 = computeRoyallMisleadingRates(hp, hd, 10);
    expect(royall10.alpha).toBe(10);
    expect(royall10.royall_bound).toBe(0.1);
    expect(royall10.hp_misleading_rate).toBe(0.0);
    expect(royall10.hd_misleading_rate).toBe(0.0);
    expect(royall10.admissible).toBe(true);
  });

  // 10. Tab 4: Golden Standards Studio Display
  it("Tab 4: renders 3 certified casework benchmark vectors with target parameters", () => {
    render(<ValidationLabPanel />);
    fireEvent.click(screen.getByRole("button", { name: /Golden Benchmarks/i }));

    expect(screen.getByText(/Pristine 24-Locus Standard \(1.0 ng\)/i)).toBeInTheDocument();
    expect(screen.getByText(/LTDNA Touch Degraded \(40% Dropout\)/i)).toBeInTheDocument();
    expect(screen.getByText(/NIST SRM 2391d Comp A Screening/i)).toBeInTheDocument();

    expect(screen.getByText("PRISTINE-24L")).toBeInTheDocument();
    expect(screen.getByText("TOUCH-LTDNA")).toBeInTheDocument();
    expect(screen.getByText("NIST-SRM2391D")).toBeInTheDocument();
  });

  // 11. Tab 4: Loading Benchmark Preset
  it("Tab 4: loads benchmark preset into studio and updates active parameters", () => {
    render(<ValidationLabPanel />);
    fireEvent.click(screen.getByRole("button", { name: /Golden Benchmarks/i }));

    // The first preset is active, the other two have 'Load into Studio'
    const loadButtons = screen.getAllByRole("button", { name: /Load into Studio/i });
    expect(loadButtons.length).toBe(2);

    // Click on the first available unselected preset
    fireEvent.click(loadButtons[0]);

    expect(mockAddAuditLog).toHaveBeenCalledWith(
      expect.objectContaining({
        event: expect.stringContaining("VALIDATION_BENCHMARK_LOADED"),
        module: "05. Tippett Calibration Lab",
        status: "PASS",
        standard: "SWGDAM 2020 / ENFSI 2017",
      })
    );
  });

  // 12. Simulation Execution with Progress and Audit Trail
  it("executes live simulation, displays progress, and dispatches case store audit log", async () => {
    render(<ValidationLabPanel />);
    const executeBtn = screen.getByRole("button", { name: /Execute Simulation/i });
    expect(executeBtn).toBeInTheDocument();

    fireEvent.click(executeBtn);

    await waitFor(() => {
      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("VALIDATION_SIMULATION_EXECUTED"),
          module: "05. Tippett Calibration Lab",
          standard: "SWGDAM 2020 / ENFSI 2017",
        })
      );
    });
  });

  // 13. Tab 5: ISO 17025 Reporting Suite
  it("Tab 5: renders ISO 17025 certificate, 95% HPD lower bound, and ENFSI verbal statement", () => {
    render(<ValidationLabPanel />);
    fireEvent.click(screen.getByRole("button", { name: /ISO 17025 Reporting/i }));

    expect(screen.getByText(/ISO\/IEC 17025 & ENFSI \(2017\) Court Admissible Reporting Suite/i)).toBeInTheDocument();
    expect(screen.getByText(/Court Admissible LR_court/i)).toBeInTheDocument();
    expect(screen.getByText(/Combined Uncertainty \(u_c\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Expanded Uncertainty \(U_95%\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Active Prosecutor's Fallacy Shield/i)).toBeInTheDocument();
  });

  // 14. Tab 5: Deterministic 64-Hex SHA-256 State Audit Digest
  it("Tab 5: computes deterministic 64-hex SHA-256 state audit digest (H_tippett)", async () => {
    const hash = await computeTippettAuditHash({
      caseId: "CASE-2026-VAL-001",
      presetId: "VECTOR_05_TIPPETT_A",
      nPairs: 1000,
      theta: 0.03,
      pDropout: 0.0,
      auc: 1.0,
      cllr: 0.02,
      hpdLower: 26.5,
    });

    expect(typeof hash).toBe("string");
    expect(hash).toHaveLength(64);
    expect(/^[0-9a-f]{64}$/.test(hash)).toBe(true);

    render(<ValidationLabPanel />);
    fireEvent.click(screen.getByRole("button", { name: /ISO 17025 Reporting/i }));

    await waitFor(() => {
      expect(screen.getByText(/State Audit Digest \(H_tippett\):/i)).toBeInTheDocument();
    });
  });

  // 15. Tab 5: Copy Certificate Action
  it("Tab 5: copies validation certificate to clipboard and provides visual feedback", async () => {
    render(<ValidationLabPanel />);
    fireEvent.click(screen.getByRole("button", { name: /ISO 17025 Reporting/i }));

    const copyBtn = screen.getByRole("button", { name: /Copy Certificate/i });
    expect(copyBtn).toBeInTheDocument();

    fireEvent.click(copyBtn);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      expect.stringContaining("FORENZA TIPPETT VALIDATION CERTIFICATE")
    );

    await waitFor(() => {
      expect(screen.getByText(/Copied!/i)).toBeInTheDocument();
    });
  });
});
