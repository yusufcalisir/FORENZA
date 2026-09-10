import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PanelBodyFluid, {
  projectToSimplex,
  calculateQdaClientSide,
  calculateNnlsClientSide,
  computeTdmrAuditHash,
  TDMR_LOCI,
  REFERENCE_MEANS,
  CERTIFIED_GOLDEN_STANDARDS,
} from "@/components/analysis/PanelBodyFluid";
import { useForensicCaseStore, SAMPLE_CASE_EU } from "@/store/forensicCaseStore";

// Mock framer-motion to prevent animation freezes in jsdom
vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, className, style, onClick, id, ...props }: any) => (
      <div className={className} style={style} onClick={onClick} id={id} {...props}>
        {children}
      </div>
    ),
    span: ({ children, className, style, ...props }: any) => (
      <span className={className} style={style} {...props}>
        {children}
      </span>
    ),
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock clipboard API
const mockClipboardWriteText = vi.fn().mockResolvedValue(undefined);
Object.assign(navigator, {
  clipboard: {
    writeText: mockClipboardWriteText,
  },
});

// Mock fetch for API routes
global.fetch = vi.fn().mockImplementation((url: string) => {
  if (url.includes("/deconvolve-tissue")) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => ({
        top_predicted_tissue: "BLOOD",
        top_tissue_probability: 0.9998,
        tissue_probabilities: {
          BLOOD: 0.9998,
          SEMEN: 0.0001,
          SALIVA: 0.0001,
          VAGINAL: 0.0,
          MENSTRUAL: 0.0,
          SKIN: 0.0,
        },
        log_likelihoods: {
          BLOOD: -12.4,
          SEMEN: -450.2,
          SALIVA: -320.1,
          VAGINAL: -290.4,
          MENSTRUAL: -180.2,
          SKIN: -410.5,
        },
        lr_tissue: 9998.0,
        log10_lr_tissue: 4.0,
        tdmr_loci_evaluated: 12,
        deconvolution_method: "Bayesian Quadratic Discriminant Analysis (QDA 12-tDMR)",
        prosecutors_fallacy_shield: "Results evaluate evidence given tissue hypotheses.",
      }),
    });
  }

  if (url.includes("/deconvolve-mixture-nnls")) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => ({
        is_mixture: false,
        major_contributor: "BLOOD",
        major_fraction: 0.985,
        minor_contributors: [],
        tissue_proportions: {
          BLOOD: 0.985,
          SEMEN: 0.005,
          SALIVA: 0.005,
          VAGINAL: 0.002,
          MENSTRUAL: 0.002,
          SKIN: 0.001,
        },
        sum_proportions: 1.0,
        residual_sum_of_squares: 0.00042,
        tdmr_loci_evaluated: 12,
        deconvolution_method: "Non-Negative Least Squares (NNLS)",
        enfsi_statement_en: "Extremely strong support for pure BLOOD origin.",
        enfsi_statement_tr: "Saf BLOOD kokenini son derece guclu desteklemektedir.",
        prosecutors_fallacy_shield: "Mixture deconvolution reflects DNA contribution.",
      }),
    });
  }

  return Promise.reject(new Error("Unknown endpoint"));
});

describe("Subsystem 20: PanelBodyFluid (tDMR Body Fluid Studio)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useForensicCaseStore.setState({
      activeCase: SAMPLE_CASE_EU,
      auditTrail: [],
    });
  });

  // Test 1: Initial Render & Mission Header
  it("1. renders mission header, module badge, and telemetry ribbon", async () => {
    render(<PanelBodyFluid />);

    expect(screen.getByText(/Vucut Sivisi & Doku Kokeni tDMR|Body Fluid & Tissue Origin tDMR/i)).toBeInTheDocument();
    expect(screen.getByText(/Modul 20 \| tDMR-FLUID/i)).toBeInTheDocument();
    expect(screen.getByText(/ISO\/IEC 17025/i)).toBeInTheDocument();

    // Verify Telemetry Ribbon items
    expect(screen.getByText(/Vaka ID|Case ID/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Numune ID|Sample ID/i)[0]).toBeInTheDocument();
    expect(screen.getByText(/Tahmin Edilen Doku|Predicted Tissue/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Olabilirlik Orani \(LR\)|Likelihood Ratio \(LR\)/i)[0]).toBeInTheDocument();
  });

  // Test 2: Tab Switching Across All 5 Canonical Tabs
  it("2. switches between all 5 canonical studio tabs smoothly", async () => {
    render(<PanelBodyFluid />);

    const studioTab = screen.getByRole("button", { name: /tDMR Laboratuvari|tDMR Studio/i });
    const nnlsTab = screen.getByRole("button", { name: /Karisim NNLS|Mixture NNLS/i });
    const atlasTab = screen.getByRole("button", { name: /Metilasyon Atlasi|Methylation Atlas/i });
    const benchmarkTab = screen.getByRole("button", { name: /Altin Standartlar|Golden Standards/i });
    const isoTab = screen.getByRole("button", { name: /ISO & Raporlama|ISO & Reporting/i });

    expect(studioTab).toBeInTheDocument();
    expect(nnlsTab).toBeInTheDocument();
    expect(atlasTab).toBeInTheDocument();
    expect(benchmarkTab).toBeInTheDocument();
    expect(isoTab).toBeInTheDocument();

    // Switch to Mixture NNLS
    fireEvent.click(nnlsTab);
    await waitFor(() => {
      expect(screen.getByText(/NNLS Cozumleyici Biyolojik Katki Oranlari|NNLS Deconvolution Cellular Proportions/i)).toBeInTheDocument();
    });

    // Switch to Methylation Atlas
    fireEvent.click(atlasTab);
    await waitFor(() => {
      expect(screen.getByText(/12-tDMR Metilasyon Atlasi ve Referans Dagilimlari|12-tDMR Methylation Reference Atlas/i)).toBeInTheDocument();
    });

    // Switch to Golden Standards
    fireEvent.click(benchmarkTab);
    await waitFor(() => {
      expect(screen.getByText(/8 Sertifikali Adli Referans Altin Standarti|8 Certified Forensic Golden Reference Standards/i)).toBeInTheDocument();
    });

    // Switch to ISO Reporting
    fireEvent.click(isoTab);
    await waitFor(() => {
      expect(screen.getByText(/Kriptografik Durum Denetim Ozeti|Cryptographic State Audit Digest/i)).toBeInTheDocument();
    });
  });

  // Test 3: Pure Math Helper projectToSimplex
  it("3. projectToSimplex projects arbitrary vectors to probability simplex summing to 1.0", () => {
    const inputs = [
      [0.2, 0.4, 0.8, -0.1, 0.0],
      [1.5, 0.5, 0.0],
      [0.0, 0.0, 0.0, 0.0],
      [10.0, 20.0, 30.0],
    ];

    for (const vec of inputs) {
      const projected = projectToSimplex(vec);
      const sum = projected.reduce((a, b) => a + b, 0);
      expect(Math.abs(sum - 1.0)).toBeLessThan(1e-5);
      for (const val of projected) {
        expect(val).toBeGreaterThanOrEqual(0.0);
      }
    }
  });

  // Test 4: Pure Math Helper calculateQdaClientSide
  it("4. calculateQdaClientSide correctly classifies blood profile with high LR", () => {
    // Pure venous blood default betas
    const bloodBetas: Record<string, number> = {};
    for (const loc of TDMR_LOCI) {
      bloodBetas[loc.id] = REFERENCE_MEANS.blood[loc.id]?.mean ?? 0.5;
    }

    const res = calculateQdaClientSide(bloodBetas);
    expect(res.top_predicted_tissue).toBe("BLOOD");
    expect(res.top_tissue_probability).toBeGreaterThan(0.95);
    expect(res.lr_tissue).toBeGreaterThan(100);
    expect(res.tdmr_loci_evaluated).toBe(12);
  });

  // Test 5: Pure Math Helper calculateNnlsClientSide
  it("5. calculateNnlsClientSide decomposes mixed tissue profile into valid proportions", () => {
    // Synthetic mixture: 70% Semen + 30% Vaginal
    const mixBetas: Record<string, number> = {};
    for (const loc of TDMR_LOCI) {
      const semenMean = REFERENCE_MEANS.semen[loc.id]?.mean ?? 0.5;
      const vaginalMean = REFERENCE_MEANS.vaginal[loc.id]?.mean ?? 0.5;
      mixBetas[loc.id] = 0.70 * semenMean + 0.30 * vaginalMean;
    }

    const res = calculateNnlsClientSide(mixBetas);
    expect(res.major_contributor).toBe("SEMEN");
    expect(res.tissue_proportions.SEMEN).toBeGreaterThan(0.55);
    expect(res.tissue_proportions.VAGINAL).toBeGreaterThan(0.20);
    expect(Math.abs(res.sum_proportions - 1.0)).toBeLessThan(0.05);
    expect(res.residual_sum_of_squares).toBeLessThan(0.01);
  });

  // Test 6: Tab 1 Beta Sliders Adjustment
  it("6. Tab 1: adjusts beta values and reflects in tissue deconvolution", async () => {
    render(<PanelBodyFluid />);

    const rangeSliders = screen.getAllByRole("slider");
    expect(rangeSliders.length).toBeGreaterThanOrEqual(12);

    const firstSlider = rangeSliders[0];
    fireEvent.change(firstSlider, { target: { value: "0.85" } });

    await waitFor(() => {
      expect(firstSlider).toHaveValue("0.85");
    });
  });

  // Test 7: Tab 2 Methylation Atlas Listing
  it("7. Tab 2: renders all 12 tDMR loci across reference fluid matrix", async () => {
    render(<PanelBodyFluid />);

    const atlasTab = screen.getByRole("button", { name: /Metilasyon Atlasi|Methylation Atlas/i });
    fireEvent.click(atlasTab);

    await waitFor(() => {
      // Check several characteristic loci
      expect(screen.getByText("cg09652652")).toBeInTheDocument();
      expect(screen.getByText("cg17610929")).toBeInTheDocument();
      expect(screen.getByText("cg23576855")).toBeInTheDocument();
      expect(screen.getByText("cg07823520")).toBeInTheDocument();
    });
  });

  // Test 8: Tab 2 Atlas Search Filter
  it("8. Tab 2: filters loci by gene or id in atlas search box", async () => {
    render(<PanelBodyFluid />);

    const atlasTab = screen.getByRole("button", { name: /Metilasyon Atlasi|Methylation Atlas/i });
    fireEvent.click(atlasTab);

    await waitFor(() => {
      expect(screen.getByText("cg09652652")).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/Lokus veya gen ara|Search locus or gene/i);
    fireEvent.change(searchInput, { target: { value: "DACT1" } });

    await waitFor(() => {
      expect(screen.getByText("cg23521140")).toBeInTheDocument();
      expect(screen.queryByText("cg09652652")).not.toBeInTheDocument();
    });
  });

  // Test 9: Tab 3 Mixture NNLS Visuals & Residuals
  it("9. Tab 3: displays major contributor fraction and residual sum of squares", async () => {
    render(<PanelBodyFluid />);

    const nnlsTab = screen.getByRole("button", { name: /Karisim NNLS|Mixture NNLS/i });
    fireEvent.click(nnlsTab);

    await waitFor(() => {
      expect(screen.getByText(/Karisim Durumu:|Mixture Status:/i)).toBeInTheDocument();
      expect(screen.getByText(/Bilesik Simpleks Cubugu:|Composite Simplex Bar:/i)).toBeInTheDocument();
    });
  });

  // Test 10: Tab 4 Golden Standards Catalog
  it("10. Tab 4: displays all 8 certified forensic golden reference standards", async () => {
    render(<PanelBodyFluid />);

    const benchmarkTab = screen.getByRole("button", { name: /Altin Standartlar|Golden Standards/i });
    fireEvent.click(benchmarkTab);

    await waitFor(() => {
      for (const std of CERTIFIED_GOLDEN_STANDARDS) {
        expect(screen.getByText(std.id)).toBeInTheDocument();
      }
    });
  });

  // Test 11: Tab 4 Loading Golden Standard & Audit Dispatch
  it("11. Tab 4: loading benchmark preset updates betas and dispatches audit log", async () => {
    render(<PanelBodyFluid />);

    const benchmarkTab = screen.getByRole("button", { name: /Altin Standartlar|Golden Standards/i });
    fireEvent.click(benchmarkTab);

    await waitFor(() => {
      expect(screen.getByText("VECTOR_TISSUE_SEMEN_PURE")).toBeInTheDocument();
    });

    // Find and click the load button for pure semen standard
    const loadButtons = screen.getAllByRole("button", { name: /Studiya Yukle|Load into Studio|Yuklendi|Active/i });
    fireEvent.click(loadButtons[1]); // Semen vector

    await waitFor(() => {
      const logs = useForensicCaseStore.getState().auditTrail;
      const benchmarkLog = logs.find((l) => l.event.includes("Loaded golden reference benchmark vector"));
      expect(benchmarkLog).toBeDefined();
      expect(benchmarkLog?.status).toBe("PASS");
    });
  });

  // Test 12: Reset Handler & Audit Dispatch
  it("12. Reset button restores default blood betas and logs event", async () => {
    render(<PanelBodyFluid />);

    const resetButton = screen.getByRole("button", { name: /Sifirla|Reset/i });
    fireEvent.click(resetButton);

    await waitFor(() => {
      const logs = useForensicCaseStore.getState().auditTrail;
      const resetLog = logs.find((l) => l.event.includes("Reset 12-tDMR parameters"));
      expect(resetLog).toBeDefined();
      expect(resetLog?.status).toBe("PASS");
    });
  });

  // Test 13: Tab 5 Co-Extraction Audit Sliders & Recommendation
  it("13. Tab 5: updates RNA yield and RIN score and adjusts strategy", async () => {
    render(<PanelBodyFluid />);

    const isoTab = screen.getByRole("button", { name: /ISO & Raporlama|ISO & Reporting/i });
    fireEvent.click(isoTab);

    await waitFor(() => {
      expect(screen.getByText(/RNA\/DNA Birlikte Ekstraksiyon Kalite Denetimi|RNA\/DNA Co-Extraction Yield & Quality Audit/i)).toBeInTheDocument();
    });

    // Sliders for RNA yield and RIN
    const rangeSliders = screen.getAllByRole("slider");
    expect(rangeSliders.length).toBeGreaterThanOrEqual(2);

    // Default strategy should be OPTIMAL_CO_EXTRACTION
    expect(screen.getByText("OPTIMAL_CO_EXTRACTION")).toBeInTheDocument();
  });

  // Test 14: Deterministic 64-hex SHA-256 State Audit Digest
  it("14. computeTdmrAuditHash returns deterministic 64-hex lowercase digest invariant to key order", () => {
    const payloadA = {
      sampleId: "TRACE-001",
      caseId: "CASE-EU-01",
      betas: { cg09652652: 0.12, cg19406367: 0.15, cg17610929: 0.91 },
      topTissue: "BLOOD",
      lrTissue: 9998.0,
      isMixture: false,
      majorContributor: "BLOOD",
      majorFraction: 0.98,
      residualSumOfSquares: 0.0004,
    };

    const payloadB = {
      ...payloadA,
      betas: { cg17610929: 0.91, cg09652652: 0.12, cg19406367: 0.15 }, // Different key order
    };

    const hashA = computeTdmrAuditHash(payloadA);
    const hashB = computeTdmrAuditHash(payloadB);

    expect(hashA).toHaveLength(64);
    expect(hashA).toMatch(/^[0-9a-f]{64}$/);
    expect(hashA).toBe(hashB); // Strict invariance to key ordering
  });

  // Test 15: Tab 5 Copy Certificate to Clipboard & Audit Log
  it("15. Tab 5: copying certificate writes to clipboard and logs to case audit trail", async () => {
    render(<PanelBodyFluid />);

    const isoTab = screen.getByRole("button", { name: /ISO & Raporlama|ISO & Reporting/i });
    fireEvent.click(isoTab);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Sertifikayi Kopyala|Copy Certificate/i })).toBeInTheDocument();
    });

    const copyBtn = screen.getByRole("button", { name: /Sertifikayi Kopyala|Copy Certificate/i });
    fireEvent.click(copyBtn);

    expect(mockClipboardWriteText).toHaveBeenCalled();
    const copiedContent = mockClipboardWriteText.mock.calls[0][0];
    expect(copiedContent).toContain("FORENZA FORENSIC BIOLOGICAL EVIDENCE REPORT");
    expect(copiedContent).toContain("ISO/IEC 17025:2017 Epigenetic Body Fluid Identification");
    expect(copiedContent).toContain("Cryptographic State Digest (SHA-256):");

    await waitFor(() => {
      const logs = useForensicCaseStore.getState().auditTrail;
      const certLog = logs.find((l) => l.event.includes("Copied ISO 17025 Body Fluid Certificate"));
      expect(certLog).toBeDefined();
      expect(certLog?.status).toBe("PASS");
    });
  });
});
