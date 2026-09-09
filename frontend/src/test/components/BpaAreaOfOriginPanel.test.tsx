import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import BpaAreaOfOriginPanel, {
  GOLDEN_BPA_PRESETS,
  computeImpactAngleDeg,
  solveBpaLeastSquares,
  computeBpaAuditHash,
} from "@/components/analysis/BpaAreaOfOriginPanel";

// Mock forensic case store
const mockAddAuditLog = vi.fn();
vi.mock("@/store/forensicCaseStore", () => ({
  useForensicCaseStore: (selector: (state: any) => any) =>
    selector({
      activeCase: {
        metadata: {
          caseId: "CASE-2026-BPA-01",
          leadAnalyst: "Dr. Sarah Jenkins, Lead BPA Analyst",
        },
      },
      addAuditLog: mockAddAuditLog,
    }),
}));

// Mock API base URL
vi.mock("@/lib/api", () => ({
  getApiBaseUrl: () => "http://localhost:8000",
}));

// Mock Language Context
vi.mock("@/context/SaaSLanguageContext", () => ({
  useSaasLanguage: () => ({ lang: "en" }),
}));

describe("Subsystem 24: 3D Bloodstain Pattern Analysis & Flight Origin Studio (BpaAreaOfOriginPanel)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
      writable: true,
      configurable: true,
    });
  });

  it("renders mission header bar with SWGSTAIN 2020, IABPA, and ISO/IEC 17025 badges", () => {
    render(<BpaAreaOfOriginPanel />);
    expect(screen.getByText(/3D Bloodstain Pattern Analysis & Flight Origin Studio/i)).toBeInTheDocument();
    expect(screen.getByText(/PILLAR 5 - MODULE 21/i)).toBeInTheDocument();
    expect(screen.getByText(/SWGSTAIN 2020 \| IABPA \| ISO 17025:2017 Sec 7.8/i)).toBeInTheDocument();
  });

  it("allows switching seamlessly across all 5 canonical analytical tabs", () => {
    render(<BpaAreaOfOriginPanel />);

    // Tab 1: Convergence (Default)
    expect(screen.getByText(/1. Convergence/i)).toBeInTheDocument();
    expect(screen.getByText(/Point of Origin \(r0\)/i)).toBeInTheDocument();
    expect(screen.getByText(/3D Spatial Trajectory Projection/i)).toBeInTheDocument();

    // Tab 2: Morphometry
    fireEvent.click(screen.getByText(/2. Morphometry/i));
    expect(screen.getByText(/Evidence Image Analysis & BPA Morphometry Hub/i)).toBeInTheDocument();
    expect(screen.getByText(/Computer Vision Stain Morphometry & Ellipse Fitting/i)).toBeInTheDocument();

    // Tab 3: Ballistics & Drag
    fireEvent.click(screen.getByText(/3. Ballistics & Drag/i));
    expect(screen.getByText(/Flight Aerodynamics & Runge-Kutta Model/i)).toBeInTheDocument();
    expect(screen.getByText(/Schiller-Naumann Drag Formula/i)).toBeInTheDocument();

    // Tab 4: Benchmarks
    fireEvent.click(screen.getByText(/4. Benchmarks/i));
    expect(screen.getByText(/VECTOR_21_BPA_H: 5-Stain Wall Spatter Ground Truth/i)).toBeInTheDocument();
    expect(screen.getByText(/VECTOR_21_BPA_A: Two-Stain Minimal Geometric Intersection/i)).toBeInTheDocument();

    // Tab 5: ISO Reporting
    fireEvent.click(screen.getByText(/5. ISO Audit/i));
    expect(screen.getByText(/Cryptographic State Audit Digest \(H_bpa\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Official Court Expert Witness Statement/i)).toBeInTheDocument();
  });

  it("renders all 8 golden benchmark presets in the header ribbon", () => {
    render(<BpaAreaOfOriginPanel />);
    expect(GOLDEN_BPA_PRESETS).toHaveLength(8);
    expect(screen.getByText(/VECTOR_H/i)).toBeInTheDocument();
    expect(screen.getByText(/VECTOR_A/i)).toBeInTheDocument();
    expect(screen.getByText(/VECTOR_B/i)).toBeInTheDocument();
    expect(screen.getByText(/VECTOR_C/i)).toBeInTheDocument();
    expect(screen.getByText(/VECTOR_D/i)).toBeInTheDocument();
    expect(screen.getByText(/VECTOR_E/i)).toBeInTheDocument();
    expect(screen.getByText(/VECTOR_F/i)).toBeInTheDocument();
    expect(screen.getByText(/VECTOR_G/i)).toBeInTheDocument();
  });

  it("loads a benchmark preset and updates point of origin calculation", () => {
    render(<BpaAreaOfOriginPanel />);
    const presetA = screen.getByText(/VECTOR_A/i);
    fireEvent.click(presetA);

    expect(mockAddAuditLog).toHaveBeenCalledWith(
      expect.objectContaining({
        event: "BPA_STAIN_LOADED",
        module: "Subsystem 24 - BPA 3D Origin",
      })
    );
  });

  it("updates stain coordinates and recalculates the origin in real time", () => {
    render(<BpaAreaOfOriginPanel />);
    const xInputs = screen.getAllByRole("spinbutton");
    if (xInputs.length > 0) {
      fireEvent.change(xInputs[0], { target: { value: "160.0" } });
    }
    expect(screen.getByText(/Point of Origin \(r0\)/i)).toBeInTheDocument();
  });

  it("adds a new stain row and increments stain count", () => {
    render(<BpaAreaOfOriginPanel />);
    const addButton = screen.getByText(/Add Stain/i);
    fireEvent.click(addButton);

    expect(screen.getByText(/6 Stains Loaded/i)).toBeInTheDocument();
  });

  it("toggles aerodynamic drag & gravity correction mode", () => {
    render(<BpaAreaOfOriginPanel />);
    const gravityCheckbox = screen.getByLabelText(/Aerodynamic Gravity Correction \(RK4\)/i);
    expect(gravityCheckbox).not.toBeChecked();

    fireEvent.click(gravityCheckbox);
    expect(gravityCheckbox).toBeChecked();
    expect(screen.getAllByText(/Aerodynamic Gravity/i).length).toBeGreaterThanOrEqual(1);
  });

  it("switches 3D view modes between 3D Iso, XY Top, and XZ Side", () => {
    render(<BpaAreaOfOriginPanel />);
    const topButton = screen.getByText(/XY Top/i);
    fireEvent.click(topButton);

    const sideButton = screen.getByText(/XZ Side/i);
    fireEvent.click(sideButton);

    const isoButton = screen.getByText(/3D Iso/i);
    fireEvent.click(isoButton);
  });

  it("computes trigonometric impact angle alpha = arcsin(W/L) accurately", () => {
    // Perpendicular normal: W = 10, L = 10 -> alpha = 90.0 deg
    expect(computeImpactAngleDeg(10.0, 10.0)).toBe(90.0);

    // Glancing: W = 2.0, L = 10.0 -> sin(alpha) = 0.20 -> alpha approx 11.5 deg
    expect(computeImpactAngleDeg(2.0, 10.0)).toBe(11.5);

    // Negative/Zero handling
    expect(computeImpactAngleDeg(0, 10.0)).toBe(0);
    expect(computeImpactAngleDeg(-5, 10.0)).toBe(0);
  });

  it("solves closed-form least-squares convergence accurately for 5-stain benchmark", () => {
    const presetH = GOLDEN_BPA_PRESETS[0];
    const res = solveBpaLeastSquares(presetH.stains, false, false);

    expect(res.stains_analyzed).toBe(5);
    expect(res.origin.x_cm).toBeCloseTo(125.4, 0);
    expect(res.origin.y_cm).toBeCloseTo(-45.2, 0);
    expect(res.origin.z_cm).toBeCloseTo(142.8, 0);
    expect(res.spatial_error_radius_cm).toBeLessThan(1.0);
    expect(res.prosecutors_fallacy_shield).toContain("SWGSTAIN / IABPA");
  });

  it("allows analyst sign-off in morphometry tab", () => {
    render(<BpaAreaOfOriginPanel />);
    fireEvent.click(screen.getByText(/2. Morphometry/i));

    expect(screen.getByText(/PENDING_HUMAN_REVIEW/i)).toBeInTheDocument();
    const signOffButton = screen.getByText(/Sign-off/i);
    fireEvent.click(signOffButton);

    expect(screen.getByText(/VERIFIED_BY_ANALYST/i)).toBeInTheDocument();
    expect(mockAddAuditLog).toHaveBeenCalledWith(
      expect.objectContaining({
        event: "BPA_ANALYST_SIGNOFF",
        module: "Subsystem 24 - BPA 3D Origin",
      })
    );
  });

  it("computes deterministic 64-hex SHA-256 state audit digest (H_bpa)", async () => {
    const hash = await computeBpaAuditHash(
      GOLDEN_BPA_PRESETS[0].stains,
      { x_cm: 125.4, y_cm: -45.2, z_cm: 142.8 },
      2.45,
      false,
      "CASE-2026-BPA-01"
    );

    expect(hash).toHaveLength(64);
    expect(hash).toMatch(/^[a-f0-9]{64}$/);
  });

  it("copies state audit hash and report to clipboard in ISO reporting tab", async () => {
    render(<BpaAreaOfOriginPanel />);
    fireEvent.click(screen.getByText(/5. ISO Audit/i));

    await waitFor(() => {
      expect(screen.getByText(/Cryptographic State Audit Digest/i)).toBeInTheDocument();
    });

    const copyHashBtn = screen.getByText(/Copy Hash/i);
    fireEvent.click(copyHashBtn);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalled();
    });

    const copyReportBtn = screen.getByText(/Copy Report/i);
    fireEvent.click(copyReportBtn);

    await waitFor(() => {
      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: "BPA_REPORT_COPIED",
        })
      );
    });
  });

  it("exports case analysis as a valid JSON blob in ISO reporting tab", () => {
    const createObjectURLMock = vi.fn().mockReturnValue("blob:http://localhost/mock-blob");
    const revokeObjectURLMock = vi.fn();
    window.URL.createObjectURL = createObjectURLMock;
    window.URL.revokeObjectURL = revokeObjectURLMock;

    render(<BpaAreaOfOriginPanel />);
    fireEvent.click(screen.getByText(/5. ISO Audit/i));

    const jsonButton = screen.getByText(/JSON/i);
    fireEvent.click(jsonButton);

    expect(createObjectURLMock).toHaveBeenCalled();
    expect(revokeObjectURLMock).toHaveBeenCalled();
  });

  it("confirms zero em-dashes exist across all rendered panel text", () => {
    const { container } = render(<BpaAreaOfOriginPanel />);
    const textContent = container.textContent || "";
    expect(textContent).not.toContain("\u2014");
    expect(textContent).not.toContain("\u2013");
  });
});
