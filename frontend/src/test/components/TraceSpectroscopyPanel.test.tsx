import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import TraceSpectroscopyPanel, {
  GOLDEN_SPECTRO_PRESETS,
  FIBER_REFERENCE_LIBRARY,
  MSI_WAVELENGTH_BANDS,
  generateReferenceSpectrum,
  computeClientHqi,
  classifyHqi,
  matchTraceSpectrumLocally,
  simulateMsiOpticalLocally,
  generateDefaultSpatialGrid,
  computeSpectroAuditHash,
} from "@/components/analysis/TraceSpectroscopyPanel";

// Mock forensic case store
const mockAddAuditLog = vi.fn();
vi.mock("@/store/forensicCaseStore", () => ({
  useForensicCaseStore: (selector: (state: any) => any) =>
    selector({
      activeCase: {
        metadata: {
          caseId: "CASE-2026-TRACE-01",
          leadAnalyst: "Dr. Evelyn Reed, Senior Trace Evidence Chemist",
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

describe("Subsystem 27: Trace Micro-Spectroscopy & MSI Studio (TraceSpectroscopyPanel)", () => {
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

  it("renders mission header bar with ASTM E2224, SWGMAT, and ISO/IEC 17025 badges", () => {
    render(<TraceSpectroscopyPanel />);
    expect(
      screen.getByText(/Trace Micro-Spectroscopy & Multispectral Imaging \(MSI\)/i)
    ).toBeInTheDocument();
    expect(screen.getAllByText(/PILLAR 5 - MODULE 24/i).length).toBeGreaterThanOrEqual(1);
    expect(
      screen.getByText(/ASTM E2224-19 \| ASTM E2228 \| SWGMAT \| ISO\/IEC 17025:2017 Sec 7.8/i)
    ).toBeInTheDocument();
  });

  it("allows switching seamlessly across all 5 canonical analytical tabs", () => {
    render(<TraceSpectroscopyPanel />);

    // Tab 1: ATR-FTIR & Raman (Default)
    expect(screen.getByText(/1. ATR-FTIR & Raman/i)).toBeInTheDocument();
    expect(screen.getByText(/Questioned Trace Specimen/i)).toBeInTheDocument();

    // Tab 2: Multispectral MSI
    fireEvent.click(screen.getByText(/2. Multispectral MSI/i));
    expect(screen.getByText(/Targeted Optical Wavelength Bands/i)).toBeInTheDocument();
    expect(screen.getByText(/OPTICAL CONTRAST & FILTERING SIMULATION/i)).toBeInTheDocument();

    // Tab 3: 2D Chemical Map
    fireEvent.click(screen.getByText(/3. 2D Chemical Map/i));
    expect(screen.getByText(/2D FPA Micro-Spectroscopy Map/i)).toBeInTheDocument();
    expect(screen.getByText(/64 Pixel FPA/i)).toBeInTheDocument();

    // Tab 4: Benchmarks
    fireEvent.click(screen.getByText(/4. Benchmarks/i));
    expect(screen.getByText(/Official Golden Benchmark Validation Vectors/i)).toBeInTheDocument();
    expect(screen.getAllByText(/SPEC_A/i).length).toBeGreaterThanOrEqual(1);

    // Tab 5: ISO Audit
    fireEvent.click(screen.getByText(/5. ISO Audit/i));
    expect(screen.getByText(/ISO\/IEC 17025:2017 Sec 7.8 Forensic Spectroscopy Report/i)).toBeInTheDocument();
    expect(screen.getByText(/Cryptographic State Audit Digest \(H_spectro\):/i)).toBeInTheDocument();
  });

  it("switches Golden Benchmark Presets and dispatches audit log to store", () => {
    render(<TraceSpectroscopyPanel />);

    const presetBtn = screen.getByText("SPEC_B");
    fireEvent.click(presetBtn);

    expect(mockAddAuditLog).toHaveBeenCalledWith(
      expect.objectContaining({
        event: "TRACE_SPECTRUM_LOADED",
        module: "Subsystem 27 - Trace Spectroscopy & MSI",
      })
    );
  });

  it("computes exact normalized squared dot product Hit Quality Index (HQI)", () => {
    const petRef = generateReferenceSpectrum("Polyester", 100);
    const petIdentical = [...petRef];
    const hqiIdentical = computeClientHqi(petIdentical, petRef);
    expect(hqiIdentical).toBe(100.0);

    const petSlightNoise = petRef.map((v) => v + 0.01);
    const hqiNoise = computeClientHqi(petSlightNoise, petRef);
    expect(hqiNoise).toBeGreaterThanOrEqual(95.0);
  });

  it("correctly implements 3-tier classification thresholds according to ASTM E2224", () => {
    // 1. Positive Spectral Match (HQI >= 90%)
    const matchTier = classifyHqi(98.4);
    expect(matchTier.classification).toBe("POSITIVE_SPECTRAL_MATCH");
    expect(matchTier.color).toBe("text-emerald-400");

    // 2. Probable Match Degraded (75% <= HQI < 90%)
    const degradedTier = classifyHqi(82.5);
    expect(degradedTier.classification).toBe("PROBABLE_MATCH_DEGRADED");
    expect(degradedTier.color).toBe("text-amber-400");

    // 3. Non-Match Exclusion (HQI < 75%)
    const excludedTier = classifyHqi(42.1);
    expect(excludedTier.classification).toBe("NON_MATCH_EXCLUSION");
    expect(excludedTier.color).toBe("text-rose-400");
  });

  it("evaluates degraded VECTOR_24_SPEC_D and renders PROBABLE_MATCH_DEGRADED classification", () => {
    render(<TraceSpectroscopyPanel />);

    const presetD = screen.getByText("SPEC_D");
    fireEvent.click(presetD);

    expect(screen.getAllByText(/PROBABLE MATCH \(DEGRADED\)/i).length).toBeGreaterThanOrEqual(1);
  });

  it("evaluates VECTOR_24_SPEC_E and validates dissimilar material exclusion", () => {
    const acrylicVec = generateReferenceSpectrum("Acrylic", 100);
    const woolVec = generateReferenceSpectrum("Wool", 100);
    const hqi = computeClientHqi(acrylicVec, woolVec);
    expect(hqi).toBeLessThan(50.0);

    const classification = classifyHqi(hqi);
    expect(classification.classification).toBe("NON_MATCH_EXCLUSION");
  });

  it("throws expected validation errors for zero-energy vectors and dimension mismatches", () => {
    const zeroVec = new Array(50).fill(0.0);
    const refVec = new Array(50).fill(1.0);
    expect(() => computeClientHqi(zeroVec, refVec)).toThrow(/Zero-energy spectrum/i);

    const shortVec = new Array(40).fill(1.0);
    expect(() => computeClientHqi(shortVec, refVec)).toThrow(/Dimension mismatch/i);
  });

  it("simulates multispectral MSI optical contrast across UV-A, Soret, Blue, and NIR", () => {
    // Soret 415nm for blood
    const soretRes = simulateMsiOpticalLocally("Latent Bloodstain", 415);
    expect(soretRes.predicted_contrast_index).toBe(0.98);
    expect(soretRes.is_optimal_forensic_band).toBe(true);
    expect(soretRes.band_info.band_name).toContain("Soret");

    // UV-A 365nm for semen/saliva
    const uvaRes = simulateMsiOpticalLocally("Semen Stain", 365);
    expect(uvaRes.predicted_contrast_index).toBe(0.95);
    expect(uvaRes.band_info.optimal_barrier_filter).toBe("420 nm Long-Pass");

    // NIR 850nm for dark fabric
    const nirRes = simulateMsiOpticalLocally("Blood on Dark Denim", 850);
    expect(nirRes.predicted_contrast_index).toBe(0.92);
    expect(nirRes.band_info.phenomenon).toBe("Substrate Transmission");
  });

  it("renders 2D spatial chemical map and updates pixel inspection upon click", () => {
    render(<TraceSpectroscopyPanel />);

    // Switch to 2D chemical map
    fireEvent.click(screen.getByText(/3. 2D Chemical Map/i));

    const pixelButtons = screen.getAllByRole("button").filter((b) => b.title && b.title.includes("("));
    expect(pixelButtons.length).toBe(64);

    // Click another pixel
    if (pixelButtons.length > 5) {
      fireEvent.click(pixelButtons[5]);
      expect(screen.getByText(/SEÇİLEN PİKSEL MİKRO-SPEKTROSKOPİSİ|SELECTED PIXEL MICRO-SPECTROSCOPY/i)).toBeInTheDocument();
    }
  });

  it("computes deterministic 64-hex SHA-256 state audit digest (H_spectro)", async () => {
    const petRef = generateReferenceSpectrum("Polyester", 100);
    const topMatch = {
      material_name: "Polyester",
      hqi_score_percent: 98.4,
      classification: "POSITIVE_SPECTRAL_MATCH" as const,
      evidence_strength: "Definitive",
      polymer_name: "PET",
      fiber_type: "Synthetic",
      diagnostic_peaks_cm_1: [1715.0, 1240.0],
    };

    const hash1 = await computeSpectroAuditHash(petRef, topMatch, 415, "CASE-2026-TEST");
    const hash2 = await computeSpectroAuditHash(petRef, topMatch, 415, "CASE-2026-TEST");

    expect(hash1).toBe(hash2);
    expect(hash1.length).toBe(64);
  });

  it("copies state audit hash to clipboard and dispatches audit log", async () => {
    render(<TraceSpectroscopyPanel />);

    // Switch to ISO Audit tab
    fireEvent.click(screen.getByText(/5. ISO Audit/i));

    const copyBtn = screen.getByRole("button", { name: /Copy Hash|Özeti Kopyala/i });
    fireEvent.click(copyBtn);

    expect(navigator.clipboard.writeText).toHaveBeenCalled();
    await waitFor(() => {
      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: "SPECTROSCOPY_REPORT_COPIED",
          module: "Subsystem 27 - Trace Spectroscopy & MSI",
        })
      );
    });
  });

  it("exports Section 7.8 courtroom report with active SWGMAT Prosecutor's Fallacy shield", async () => {
    render(<TraceSpectroscopyPanel />);

    // Switch to ISO Audit tab
    fireEvent.click(screen.getByText(/5. ISO Audit/i));

    const exportBtn = screen.getByRole("button", { name: /Export Full Report|Tam Raporu Dışa Aktar/i });
    fireEvent.click(exportBtn);

    expect(navigator.clipboard.writeText).toHaveBeenCalled();
    expect(screen.getByText(/ENFSI 2017 & SWGMAT/i)).toBeInTheDocument();
  });

  it("allows switching target reference polymer in Tab 1 and updates reference curve", () => {
    render(<TraceSpectroscopyPanel />);

    const nylonBtns = screen.getAllByRole("button", { name: /Nylon-6,6/i });
    fireEvent.click(nylonBtns[nylonBtns.length - 1]);

    expect(screen.getAllByText(/Nylon-6,6/i).length).toBeGreaterThanOrEqual(1);
  });

  it("strictly contains zero em-dashes across all rendered tab interfaces", () => {
    const { container } = render(<TraceSpectroscopyPanel />);
    const text = container.textContent || "";
    expect(text).not.toContain("\u2014");
    expect(text).not.toContain("\u2013");
  });
});
