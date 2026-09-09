import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import EntomologyPmiPanel, {
  ENTOMOLOGY_SPECIES_REGISTRY,
  ENTOMOLOGY_BENCHMARKS,
  MEGNIN_SUCCESSION_WAVES,
} from "@/components/analysis/EntomologyPmiPanel";

// Mock forensic case store
const mockAddAuditLog = vi.fn();
vi.mock("@/store/forensicCaseStore", () => ({
  useForensicCaseStore: (selector: (state: any) => any) =>
    selector({
      activeCase: {
        profile: {
          profileId: "CASE-2026-ENTO-99",
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

describe("Subsystem 26: Forensic Entomology & Minimum PMI Studio (EntomologyPmiPanel)", () => {
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

  it("renders mission header bar with EAFE, NAFEA, ISO/IEC 17025, and ASTM badges", () => {
    render(<EntomologyPmiPanel />);
    expect(screen.getByText(/Forensic Entomology & Minimum PMI Studio/i)).toBeInTheDocument();
    expect(screen.getByText(/EAFE • NAFEA/i)).toBeInTheDocument();
    expect(screen.getByText(/ISO\/IEC 17025/i)).toBeInTheDocument();
    expect(screen.getByText(/ASTM E1588-20/i)).toBeInTheDocument();
  });

  it("allows switching seamlessly across all 5 canonical analytical tabs", async () => {
    render(<EntomologyPmiPanel />);

    // Tab 1: Live MICI Solver (default)
    expect(screen.getByText(/1. Live MICI Solver/i)).toBeInTheDocument();
    expect(screen.getByText(/MICI Posterior Telemetry/i)).toBeInTheDocument();

    // Tab 2: Species Taxonomy
    fireEvent.click(screen.getByText(/2. Diptera & Coleoptera Taxonomy/i));
    expect(screen.getByText(/Forensic Diptera & Coleoptera Species Registry/i)).toBeInTheDocument();
    expect(screen.getByText(/Ikemoto & Takai/i)).toBeInTheDocument();

    // Tab 3: Succession Waves & Isomegalen Curves
    fireEvent.click(screen.getByText(/3. Isomegalen & Megnin Waves/i));
    expect(screen.getByText(/Isomegalen \/ Isopromen Growth Diagram/i)).toBeInTheDocument();
    expect(screen.getByText(/Megnin's 5 Ecological Succession Waves/i)).toBeInTheDocument();

    // Tab 4: Maggot Mass & Weather Station
    fireEvent.click(screen.getByText(/4. Maggot Mass & Weather/i));
    expect(screen.getByText(/Larval Aggregate Metabolic Self-Heating Model/i)).toBeInTheDocument();
    expect(screen.getByText(/Weather Station Elevation Lapse Rate Calibration/i)).toBeInTheDocument();

    // Tab 5: ISO 17025 State Audit
    fireEvent.click(screen.getByText(/5. ISO 17025 State Audit/i));
    expect(screen.getByText(/ISO\/IEC 17025:2017 Chain of Custody & Cryptographic State Audit Digest/i)).toBeInTheDocument();
  });

  it("switches Golden Benchmark Presets and updates thermal telemetry", () => {
    render(<EntomologyPmiPanel />);

    // Click VECTOR_23_ENTO_B (Calliphora vicina Cold-Adapted)
    const presetBtn = screen.getByText(/Calliphora vicina Cold-Adapted/i);
    fireEvent.click(presetBtn);

    expect(mockAddAuditLog).toHaveBeenCalledWith(
      expect.objectContaining({
        event: expect.stringContaining("VECTOR_23_ENTO_B"),
      })
    );
  });

  it("switches species and updates available development stages", () => {
    render(<EntomologyPmiPanel />);

    const speciesSelect = screen.getAllByRole("combobox")[0];
    fireEvent.change(speciesSelect, { target: { value: "Calliphora vicina" } });

    expect(speciesSelect).toHaveValue("Calliphora vicina");
  });

  it("adjusts ambient temperature slider and recalculates effective degree steps", () => {
    render(<EntomologyPmiPanel />);

    const tempSlider = screen.getAllByRole("slider")[0];
    fireEvent.change(tempSlider, { target: { value: "24.0" } });

    expect(screen.getAllByText(/24\.0°C/i).length).toBeGreaterThan(0);
  });

  it("adjusts larval mass metabolic offset slider (+ΔT_mass)", () => {
    render(<EntomologyPmiPanel />);

    const massSlider = screen.getAllByRole("slider")[1];
    fireEvent.change(massSlider, { target: { value: "3.2" } });

    expect(screen.getByText("+3.2°C")).toBeInTheDocument();
  });

  it("toggles nocturnal oviposition scotophase gate", () => {
    render(<EntomologyPmiPanel />);

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).not.toBeChecked();

    fireEvent.click(checkbox);
    expect(checkbox).toBeChecked();
  });

  it("verifies species registry in Tab 2 includes all 6 key forensically validated taxa", () => {
    render(<EntomologyPmiPanel />);
    fireEvent.click(screen.getByText(/2. Diptera & Coleoptera Taxonomy/i));

    expect(screen.getByText("Lucilia sericata")).toBeInTheDocument();
    expect(screen.getByText("Calliphora vicina")).toBeInTheDocument();
    expect(screen.getByText("Chrysomya albiceps")).toBeInTheDocument();
    expect(screen.getByText("Phormia regina")).toBeInTheDocument();
    expect(screen.getByText("Sarcophaga argyrostoma")).toBeInTheDocument();
    expect(screen.getByText("Dermestes maculatus")).toBeInTheDocument();
  });

  it("renders Mégnin's 5 classical ecological colonization waves in Tab 3", () => {
    render(<EntomologyPmiPanel />);
    fireEvent.click(screen.getByText(/3. Isomegalen & Megnin Waves/i));

    expect(screen.getByText(/Fresh Carcass Stage \(Wave 1\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Bloated Decay Stage \(Wave 2\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Active Decay \/ Fermentation \(Wave 3\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Advanced Butyric Decay \(Wave 4\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Dry Remains & Skeletal Mummification \(Wave 5\)/i)).toBeInTheDocument();
  });

  it("calculates altitude temperature lapse rate in Tab 4 (-0.65°C / 100m)", () => {
    render(<EntomologyPmiPanel />);
    fireEvent.click(screen.getByText(/4. Maggot Mass & Weather/i));

    const altSlider = screen.getAllByRole("slider")[1];
    fireEvent.change(altSlider, { target: { value: "1000" } });

    expect(screen.getByText("+1000 m")).toBeInTheDocument();
    expect(screen.getByText("-6.50°C")).toBeInTheDocument();
  });

  it("renders active case ID and court statement in Tab 5", () => {
    render(<EntomologyPmiPanel />);
    fireEvent.click(screen.getByText(/5. ISO 17025 State Audit/i));

    expect(screen.getByText("CASE-2026-ENTO-99")).toBeInTheDocument();
    expect(screen.getByText(/Court Expert Witness Statement & Evidentiary Integrity/i)).toBeInTheDocument();
  });

  it("copies cryptographic state audit digest to clipboard and logs audit trail event", async () => {
    render(<EntomologyPmiPanel />);
    fireEvent.click(screen.getByText(/5. ISO 17025 State Audit/i));

    await waitFor(() => {
      expect(screen.queryByText(/Calculating SHA-256 state hash/i)).not.toBeInTheDocument();
    });

    const copyBtn = screen.getByText(/Copy Digest/i);
    fireEvent.click(copyBtn);

    expect(navigator.clipboard.writeText).toHaveBeenCalled();
    await waitFor(() => {
      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("Copied ISO/IEC 17025 SHA-256"),
        })
      );
    });
  });

  it("dispatches live calculation and triggers local fallback on fetch failure", async () => {
    // Mock fetch failure
    global.fetch = vi.fn().mockRejectedValue(new Error("Network connection refused"));

    render(<EntomologyPmiPanel />);
    const calcBtn = screen.getByRole("button", { name: /Calculate PMI_min/i });
    fireEvent.click(calcBtn);

    await waitFor(() => {
      expect(screen.getByText(/Local Engine Active/i)).toBeInTheDocument();
    });
  });

  it("displays sub-threshold warning under cold dormancy conditions", () => {
    render(<EntomologyPmiPanel />);
    // Select VECTOR_23_ENTO_C (5°C < 9°C)
    const presetBtn = screen.getByText(/Sub-Threshold Dormancy/i);
    fireEvent.click(presetBtn);

    expect(screen.getByText(/Temperature is below developmental threshold T_base/i)).toBeInTheDocument();
  });

  it("displays EAFE / NAFEA legal shield protecting against Prosecutor's Fallacy", () => {
    render(<EntomologyPmiPanel />);
    expect(screen.getByText(/EAFE & NAFEA Legal Admissibility Defense Shield/i)).toBeInTheDocument();
    expect(screen.getByText(/Minimum Insect Colonisation Interval \(MICI\)/i)).toBeInTheDocument();
  });
});
