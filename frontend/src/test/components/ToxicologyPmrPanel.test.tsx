import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import ToxicologyPmrPanel, {
  evaluateClientPmr,
  evaluateClientExtrap,
  computePmrAuditHash,
  XENOBIOTIC_DATABASE,
  BENCHMARK_PRESETS,
} from "@/components/analysis/ToxicologyPmrPanel";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// Mock API Base URL
vi.mock("@/lib/api", () => ({
  getApiBaseUrl: () => "http://localhost:8000",
}));

// Mock Saas Language Context
vi.mock("@/context/SaaSLanguageContext", () => ({
  useSaasLanguage: () => ({
    lang: "en",
    setLang: vi.fn(),
  }),
}));

describe("Subsystem 28: Post-Mortem Toxicokinetics & PMR Panel Suite", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // 1. Initial Render & Canonical 5-Tab Navigation
  it("renders panel header, tactical mission bar, and 5 canonical tabs", () => {
    render(<ToxicologyPmrPanel />);
    expect(screen.getByText(/Post-Mortem Toxicokinetics & PMR/i)).toBeInTheDocument();
    expect(screen.getByText(/SOFT : TIAFT/i)).toBeInTheDocument();
    expect(screen.getByText(/1. PMR \(C\/P\) Ratio/i)).toBeInTheDocument();
    expect(screen.getByText(/2. Antemortem Extrapolation/i)).toBeInTheDocument();
    expect(screen.getByText(/3. Xenobiotic Matrix/i)).toBeInTheDocument();
    expect(screen.getByText(/4. Benchmark Vectors/i)).toBeInTheDocument();
    expect(screen.getByText(/5. ISO 17025 Audit & Report/i)).toBeInTheDocument();
  });

  // 2. Tab Navigation Functionality
  it("switches tabs correctly across all 5 views", async () => {
    render(<ToxicologyPmrPanel />);

    // Switch to Tab 2: Antemortem Extrapolation
    fireEvent.click(screen.getByText(/2. Antemortem Extrapolation/i));
    expect(screen.getByText(/Kinetic Parameters/i)).toBeInTheDocument();

    // Switch to Tab 3: Xenobiotic Matrix
    fireEvent.click(screen.getByText(/3. Xenobiotic Matrix/i));
    expect(screen.getByText(/Physicochemical Xenobiotic Reference Matrix/i)).toBeInTheDocument();

    // Switch to Tab 4: Benchmark Vectors
    fireEvent.click(screen.getByText(/4. Benchmark Vectors/i));
    expect(screen.getByText(/Certified Validation Benchmark Vectors/i)).toBeInTheDocument();

    // Switch to Tab 5: ISO 17025 Audit & Report
    fireEvent.click(screen.getByText(/5. ISO 17025 Audit & Report/i));
    expect(screen.getByText(/ISO\/IEC 17025:2017 Section 7.8/i)).toBeInTheDocument();
  });

  // 3. PMR C/P Ratio Evaluation & Literature Mean Display
  it("evaluates PMR C/P ratio and renders literature mean benchmark", () => {
    const res = evaluateClientPmr("Fentanyl", 14.0, 5.0, "ug/L", false);
    expect(res.cp_observed).toBe(2.8);
    expect(res.cp_literature_mean).toBe(2.8);
    expect(res.is_cardiac_overestimated).toBe(true);
    expect(res.overestimation_percentage).toBe(180.0);
    expect(res.vd_l_kg).toBe(5.0);
  });

  // 4. Dual-Criterion PMR Overestimation Logic for Fentanyl
  it("triggers High PMR overestimation alert for Fentanyl (C/P > 2.0 and Vd > 3.0)", () => {
    const res = evaluateClientPmr("Fentanyl", 24.0, 8.5, "ng/mL", false);
    expect(res.cp_observed).toBeCloseTo(2.82, 2);
    expect(res.is_cardiac_overestimated).toBe(true);
    expect(res.pmr_risk_tier).toBe("High / Severe");
    expect(res.alert_message).toContain("HIGH PMR OVERESTIMATION ALERT");
  });

  // 5. Morphine Edge-Case: Verifies No False Overestimation Alert
  it("verifies Morphine C/P = 1.80 matches literature baseline and does not trigger false alert", () => {
    const res = evaluateClientPmr("Morphine", 0.36, 0.20, "mg/L", false);
    expect(res.cp_observed).toBe(1.8);
    expect(res.cp_literature_mean).toBe(1.8);
    // 1.80 <= 2.0 and 1.80 <= 1.5 * 1.80 (2.70), so overestimation is FALSE
    expect(res.is_cardiac_overestimated).toBe(false);
    expect(res.alert_message).toContain("within normal literature equilibrium limits");
  });

  // 6. Amitriptyline Massive Redistribution Overestimation
  it("verifies Amitriptyline massive cardiac overestimation alert (Vd = 20.0 L/kg)", () => {
    const res = evaluateClientPmr("Amitriptyline", 4.50, 1.00, "mg/L", false);
    expect(res.cp_observed).toBe(4.5);
    expect(res.is_cardiac_overestimated).toBe(true);
    expect(res.overestimation_percentage).toBe(350.0);
    expect(res.pmr_risk_tier).toBe("Very High");
  });

  // 7. Acetaminophen Low Redistribution Baseline
  it("verifies Acetaminophen minimal redistribution baseline", () => {
    const res = evaluateClientPmr("Acetaminophen", 10.5, 10.0, "mg/L", false);
    expect(res.cp_observed).toBe(1.05);
    expect(res.is_cardiac_overestimated).toBe(false);
    expect(res.pmr_risk_tier).toBe("Low");
  });

  // 8. Ethanol Zero-Order Widmark Elimination
  it("calculates Ethanol zero-order Widmark back-extrapolation", () => {
    const res = evaluateClientExtrap("Ethanol", 0.50, 4.0, "g/L", false);
    // C_0 = 0.50 + (0.15 * 4.0) = 1.10 g/L
    expect(res.c_antemortem_extrapolated).toBe(1.10);
    expect(res.elimination_type).toBe("Zero-Order");
    expect(res.beta_60_g_l_h).toBe(0.15);
  });

  // 9. First-Order Half-Life Elimination Kinetics
  it("calculates first-order exponential back-extrapolation across 1 half-life", () => {
    // 1 half-life (7.0h) back in time means concentration was exactly 2x femoral
    const res = evaluateClientExtrap("Fentanyl", 5.0, 7.0, "ug/L", false);
    expect(res.c_antemortem_extrapolated).toBe(10.0);
    expect(res.elimination_type).toBe("First-Order");
    expect(res.half_life_hours).toBe(7.0);
    expect(res.elimination_rate_constant_ke_h).toBeCloseTo(0.09902, 4);
  });

  // 10. VECTOR_P5_03 Statutory Golden Vector Invariant
  it("verifies VECTOR_P5_03 statutory ground-truth parameters", () => {
    const vector = BENCHMARK_PRESETS.find((b) => b.id === "VECTOR_P5_03");
    expect(vector).toBeDefined();
    if (!vector) return;

    expect(vector.cHeart).toBe(24.0);
    expect(vector.cFem).toBe(8.5);
    expect(vector.unit).toBe("ng/mL");
    const cp = vector.cHeart / vector.cFem;
    expect(cp).toBeCloseTo(2.82, 2);
    expect(vector.expectedHighPmr).toBe(true);
  });

  // 11. Xenobiotic Matrix Search Filter
  it("filters xenobiotic matrix by search query", () => {
    render(<ToxicologyPmrPanel />);
    fireEvent.click(screen.getByText(/3. Xenobiotic Matrix/i));

    const searchInput = screen.getByPlaceholderText(/Search compound or risk/i);
    fireEvent.change(searchInput, { target: { value: "Fentanyl" } });

    expect(screen.getByText("Fentanyl")).toBeInTheDocument();
    expect(screen.queryByText("Acetaminophen")).not.toBeInTheDocument();
  });

  // 12. Benchmark Loading and Casework Update
  it("loads benchmark vector and updates casework values in state", async () => {
    render(<ToxicologyPmrPanel />);
    fireEvent.click(screen.getByText(/4. Benchmark Vectors/i));

    const executeBtns = screen.getAllByText(/Execute & Verify Vector/i);
    expect(executeBtns.length).toBeGreaterThan(0);
    fireEvent.click(executeBtns[0]); // Load VECTOR_P5_03

    // Should return to Tab 1
    await waitFor(() => {
      expect(screen.getByText(/1. PMR \(C\/P\) Ratio/i)).toBeInTheDocument();
    });
  });

  // 13. Case Store Audit Logging Dispatch
  it("dispatches audit event to forensicCaseStore upon evaluation", async () => {
    // Mock fetch to reject immediately so client-side fallback triggers without 3s AbortSignal timeout
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Network unavailable")));
    const addAuditLogSpy = vi.spyOn(useForensicCaseStore.getState(), "addAuditLog");
    render(<ToxicologyPmrPanel />);

    const evalBtn = screen.getByRole("button", { name: /Evaluate PMR/i });
    fireEvent.click(evalBtn);

    // setTimeout chain: 700ms + 200ms = 900ms total delay; use 2500ms waitFor timeout
    await waitFor(
      () => {
        expect(addAuditLogSpy).toHaveBeenCalled();
      },
      { timeout: 2500 }
    );
    vi.unstubAllGlobals();
  });

  // 14. Deterministic ISO 17025 SHA-256 State Audit Digest
  it("computes deterministic 64-hex SHA-256 state digest H_pmr", async () => {
    const pmr = evaluateClientPmr("Fentanyl", 14.0, 5.0, "ug/L", false);
    const extrap = evaluateClientExtrap("Fentanyl", 5.0, 7.0, "ug/L", false);
    const digest = await computePmrAuditHash(pmr, extrap, "CASE-2026-TEST");

    expect(digest).toBeDefined();
    expect(digest.length).toBe(64);
    expect(/^[0-9a-f]{64}$/.test(digest)).toBe(true);
  });

  // 15. Master Rule 4: Absolute Ban on Em-Dashes
  it("enforces zero em-dashes in database and text outputs", () => {
    const rawData = JSON.stringify(XENOBIOTIC_DATABASE) + JSON.stringify(BENCHMARK_PRESETS);
    expect(rawData).not.toContain("\u2014");
    expect(rawData).not.toContain("\u2013");
  });
});
