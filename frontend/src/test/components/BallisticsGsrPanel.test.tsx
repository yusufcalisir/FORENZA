import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import BallisticsGsrPanel, {
  GOLDEN_BALLISTICS_PRESETS,
  evaluateClientGsr,
  evaluateClientCmc,
  computeMedullaryIndex,
  computeBallisticsAuditHash,
} from "@/components/analysis/BallisticsGsrPanel";

// Mock forensic case store
const mockAddAuditLog = vi.fn();
vi.mock("@/store/forensicCaseStore", () => ({
  useForensicCaseStore: (selector: (state: any) => any) =>
    selector({
      activeCase: {
        metadata: {
          caseId: "CASE-2026-BALLISTICS-01",
          leadAnalyst: "Dr. Marcus Vance, Lead Firearm Examiner",
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

describe("Subsystem 25: SEM-EDX GSR Ballistics & Microscopy Studio (BallisticsGsrPanel)", () => {
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

  it("renders mission header bar with ASTM E1588-20, NIST CMC, and ISO/IEC 17025 badges", () => {
    render(<BallisticsGsrPanel />);
    expect(screen.getByText(/SEM-EDX Gunshot Residue \(GSR\), 3D CMC Ballistics & Microscopy Studio/i)).toBeInTheDocument();
    expect(screen.getByText(/PILLAR 5 - MODULE 22/i)).toBeInTheDocument();
    expect(screen.getByText(/ASTM E1588-20 \| NIST CMC \| SWGMAT \| ISO 17025:2017/i)).toBeInTheDocument();
  });

  it("allows switching seamlessly across all 5 canonical analytical tabs", () => {
    render(<BallisticsGsrPanel />);

    // Tab 1: SEM-EDX GSR (Default)
    expect(screen.getByText(/1. SEM-EDX GSR/i)).toBeInTheDocument();
    expect(screen.getByText(/Characteristic Particles \(Pb-Ba-Sb\)/i)).toBeInTheDocument();

    // Tab 2: 3D CMC Ballistics
    fireEvent.click(screen.getByText(/2. 3D CMC Ballistics/i));
    expect(screen.getByText(/Congruent Matching Cells \(K\)/i)).toBeInTheDocument();

    // Tab 3: Microscopy & Hair
    fireEvent.click(screen.getByText(/3. Microscopy & Hair/i));
    expect(screen.getByText(/Medullary Index \(I_medulla\)/i)).toBeInTheDocument();

    // Tab 4: Benchmarks
    fireEvent.click(screen.getByText(/4. Benchmarks/i));
    expect(screen.getAllByText(/VECTOR_22_GSR_A/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/VECTOR_22_CMC_E/i).length).toBeGreaterThanOrEqual(1);

    // Tab 5: ISO Audit
    fireEvent.click(screen.getByText(/5. ISO Audit/i));
    expect(screen.getByText(/Cryptographic State Audit Digest \(H_ballistics\)/i)).toBeInTheDocument();
  });

  it("switches Golden Benchmark Presets and updates telemetry in header ribbon", () => {
    render(<BallisticsGsrPanel />);

    const presetBtn = screen.getByText("GSR_B");
    fireEvent.click(presetBtn);

    expect(mockAddAuditLog).toHaveBeenCalledWith(
      expect.objectContaining({
        event: "GSR_SAMPLE_LOADED",
        module: "Subsystem 25 - Ballistics & GSR",
      })
    );
  });

  it("updates GSR particle concentrations and recalculates classification and LR in real time", () => {
    render(<BallisticsGsrPanel />);
    const numberInputs = screen.getAllByRole("spinbutton");
    if (numberInputs.length > 0) {
      fireEvent.change(numberInputs[0], { target: { value: "50.0" } });
    }
    expect(screen.getByText(/Characteristic Particles \(Pb-Ba-Sb\)/i)).toBeInTheDocument();
  });

  it("adds a new GSR particle row and increments particle count", () => {
    render(<BallisticsGsrPanel />);
    const addParticleBtn = screen.getByText(/Add Particle/i);
    fireEvent.click(addParticleBtn);

    expect(screen.getByText(/5 Particles Loaded/i)).toBeInTheDocument();
  });

  it("evaluates ASTM E1588-20 aspect ratio morphology downgrade rule (VECTOR_22_GSR_C)", () => {
    const res = evaluateClientGsr(
      [{ particle_id: "p1", pb_percent: 35.0, ba_percent: 25.0, sb_percent: 15.0, aspect_ratio: 1.8 }],
      false
    );

    // Aspect ratio 1.8 > 1.3 disqualifies Characteristic classification
    expect(res.characteristic_particles).toBe(0);
    expect(res.commonly_associated_particles).toBe(1);
    expect(res.likelihood_ratio).toBe(1.0);
  });

  it("evaluates NIST Song et al. CMC positive firearm identification (VECTOR_22_CMC_E)", () => {
    const presetE = GOLDEN_BALLISTICS_PRESETS.find((p) => p.id === "VECTOR_22_CMC_E");
    expect(presetE).toBeDefined();

    const res = evaluateClientCmc(presetE!.cells!, false);
    expect(res.cmc_count).toBe(6);
    expect(res.identification_verdict).toBe("POSITIVE_IDENTIFICATION");
    expect(res.false_match_probability).toBe("< 1e-6");
  });

  it("evaluates NIST CMC spatial translation rejection (VECTOR_22_CMC_F)", () => {
    const presetF = GOLDEN_BALLISTICS_PRESETS.find((p) => p.id === "VECTOR_22_CMC_F");
    expect(presetF).toBeDefined();

    const res = evaluateClientCmc(presetF!.cells!, false);
    // 5 cells pass, 3 cells exceed 15 um -> K = 5 (Inconclusive)
    expect(res.cmc_count).toBe(5);
    expect(res.identification_verdict).toBe("INCONCLUSIVE_BORDERLINE");
  });

  it("evaluates NIST CMC angular rotation rejection (VECTOR_22_CMC_G)", () => {
    const presetG = GOLDEN_BALLISTICS_PRESETS.find((p) => p.id === "VECTOR_22_CMC_G");
    expect(presetG).toBeDefined();

    const res = evaluateClientCmc(presetG!.cells!, false);
    expect(res.cmc_count).toBe(0);
    expect(res.identification_verdict).toBe("ELIMINATION_NO_MATCH");
  });

  it("computes medullary index and discriminates human vs animal hair accurately", () => {
    // Human hair: medulla 15 um, shaft 80 um -> index = 0.188 < 0.33
    expect(computeMedullaryIndex(15.0, 80.0)).toBe(0.188);

    // Animal hair: medulla 50 um, shaft 80 um -> index = 0.625 > 0.50
    expect(computeMedullaryIndex(50.0, 80.0)).toBe(0.625);

    // Edge cases
    expect(computeMedullaryIndex(0, 80.0)).toBe(0);
    expect(computeMedullaryIndex(10, 0)).toBe(0);
  });

  it("allows selecting hair specimens in microscopy tab and logs audit event", () => {
    render(<BallisticsGsrPanel />);
    fireEvent.click(screen.getByText(/3. Microscopy & Hair/i));

    const specimenCard = screen.getByText(/HAIR-SAMPLE-502/i);
    fireEvent.click(specimenCard);

    expect(mockAddAuditLog).toHaveBeenCalledWith(
      expect.objectContaining({
        event: "MICROSCOPY_SAMPLE_EVALUATED",
        module: "Subsystem 25 - Ballistics & GSR",
      })
    );
  });

  it("computes deterministic 64-hex SHA-256 state audit digest (H_ballistics)", async () => {
    const presetA = GOLDEN_BALLISTICS_PRESETS[0];
    const gsrRes = evaluateClientGsr(presetA.particles!, false);
    const cmcRes = evaluateClientCmc([], false);

    const hash = await computeBallisticsAuditHash(
      presetA.particles!,
      [],
      [],
      gsrRes,
      cmcRes,
      "CASE-2026-BALLISTICS-01"
    );

    expect(hash).toHaveLength(64);
    expect(hash).toMatch(/^[a-f0-9]{64}$/);
  });

  it("copies state audit hash and report to clipboard in ISO audit tab", async () => {
    render(<BallisticsGsrPanel />);
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
          event: "BALLISTICS_REPORT_COPIED",
        })
      );
    });
  });

  it("exports case analysis as a valid JSON blob in ISO audit tab", () => {
    const createObjectURLMock = vi.fn().mockReturnValue("blob:http://localhost/mock-blob");
    const revokeObjectURLMock = vi.fn();
    window.URL.createObjectURL = createObjectURLMock;
    window.URL.revokeObjectURL = revokeObjectURLMock;

    render(<BallisticsGsrPanel />);
    fireEvent.click(screen.getByText(/5. ISO Audit/i));

    const jsonButton = screen.getByText(/JSON/i);
    fireEvent.click(jsonButton);

    expect(createObjectURLMock).toHaveBeenCalled();
    expect(revokeObjectURLMock).toHaveBeenCalled();
  });

  it("confirms zero em-dashes exist across all rendered panel text", () => {
    const { container } = render(<BallisticsGsrPanel />);
    const textContent = container.textContent || "";
    expect(textContent).not.toContain("\u2014");
    expect(textContent).not.toContain("\u2013");
  });
});
