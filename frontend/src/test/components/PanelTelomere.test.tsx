import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PanelTelomere, {
  computeClientTelomereAge,
  computeClientPmiAdh,
  computeClientMosaicismIndex,
  computeTelomereAuditHash,
  GOLDEN_VECTORS,
  DIAGNOSTIC_LOCI,
  TELOMERE_INTERCEPT,
  TELOMERE_SLOPE,
  PMI_LAMBDA_DECAY,
  PMI_DEFAULT_BETA_0,
  PMI_BETA_FLOOR,
} from "@/components/analysis/PanelTelomere";
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
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

// Mock fetch for REST API routes
const mockApiSuccess = {
  telomere: {
    relative_ts_ratio: 1.2075,
    delta_delta_ct: -0.272,
    estimated_telomere_age_years: 25.0,
    telomere_age_group: "YOUNG_ADULT",
    annual_shortening_rate: 0.0085,
    ci_95_years: [20.8, 29.2],
    base_pair_loss_approx: 49,
  },
  pmi: {
    observed_residual_beta: 0.50,
    baseline_beta_0: 0.85,
    decay_constant_lambda: 0.00045,
    accumulated_degree_hours: 1413.3,
    ambient_temperature_celsius: 20.0,
    estimated_pmi_hours: 70.7,
    estimated_pmi_days: 2.9,
    pmi_confidence_bounds_hours: [60.1, 81.3],
  },
  mosaicism: {
    somatic_mosaicism_index_m: 0.0102,
    mosaicism_classification: "CLONAL_HOMOGENEITY",
    evaluated_loci_count: 8,
    divergent_loci: { cg16867657: 0.01 },
    max_divergence_locus: "cg16867657",
    max_divergence_value: 0.01,
  },
  prosecutors_fallacy_shield: "Results reflect biological wear only. Cross-validate with forensic entomology.",
  enfsi_evaluative_statement_en: "The estimated biological age is 25.0 years with 70.7 hours PMI.",
  enfsi_evaluative_statement_tr: "Tahmini biyolojik yas 25.0 yil ve 70.7 saat PMI olarak hesaplanmistir.",
};

global.fetch = vi.fn().mockImplementation((url: string) => {
  if (url.includes("/telomere-and-pmi")) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => mockApiSuccess,
    });
  }
  return Promise.reject(new Error("Unknown route"));
});

describe("Pillar 4 Telomere Chronometer & Epigenetic PMI Biocomputation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useForensicCaseStore.setState({
      activeCase: {
        ...SAMPLE_CASE_EU,
        profile: {
          ...SAMPLE_CASE_EU.profile,
          epigeneticAge: 25.0,
        },
      },
    });
  });

  // =========================================================================
  // 1. Analytical Mathematical Invariants (Pure Functions & Golden Vectors)
  // =========================================================================
  describe("Mathematical Invariants & Golden Benchmarks", () => {
    it("verifies Cawthon qPCR T/S decay constants and intercept", () => {
      expect(TELOMERE_INTERCEPT).toBe(1.420);
      expect(TELOMERE_SLOPE).toBe(0.0085);
      expect(PMI_LAMBDA_DECAY).toBe(0.00045);
      expect(PMI_DEFAULT_BETA_0).toBe(0.85);
      expect(PMI_BETA_FLOOR).toBe(0.05);
    });

    it("evaluates VECTOR_19_PMI_A (Newborn Infant Baseline, Age 0.0)", () => {
      const vec = GOLDEN_VECTORS.find((v) => v.id === "VECTOR_19_PMI_A")!;
      expect(vec).toBeDefined();

      const result = computeClientTelomereAge(vec.tsRatio, 0.0);
      expect(result.estimatedAge).toBe(0.0);
      expect(result.ageGroup).toBe("NEWBORN_INFANT");
      expect(result.ciLower).toBe(0.0);
      expect(result.ciUpper).toBe(4.2);
      expect(result.deltaCategory).toBe("CONCORDANT");
    });

    it("evaluates VECTOR_19_PMI_B (Young Adult Reference Donor, Age 25.0)", () => {
      const vec = GOLDEN_VECTORS.find((v) => v.id === "VECTOR_19_PMI_B")!;
      expect(vec).toBeDefined();

      const result = computeClientTelomereAge(vec.tsRatio, 25.0);
      expect(result.estimatedAge).toBe(25.0);
      expect(result.ageGroup).toBe("YOUNG_ADULT");
      expect(result.ciLower).toBe(20.8);
      expect(result.ciUpper).toBe(29.2);
      expect(result.deltaCategory).toBe("CONCORDANT");
    });

    it("evaluates VECTOR_19_PMI_C (Elderly Severe Telomeric Attrition, Age 75.0)", () => {
      const vec = GOLDEN_VECTORS.find((v) => v.id === "VECTOR_19_PMI_C")!;
      expect(vec).toBeDefined();

      const result = computeClientTelomereAge(vec.tsRatio, 75.0);
      expect(result.estimatedAge).toBe(75.0);
      expect(result.ageGroup).toBe("ELDERLY");
      expect(result.ciLower).toBe(70.8);
      expect(result.ciUpper).toBe(79.2);
      expect(result.deltaCategory).toBe("CONCORDANT");
    });

    it("detects accelerated biological aging when delta > 4.0 years", () => {
      // T/S = 1.050 -> estimated age ~ 43.5 years. If known age is 30.0 -> delta +13.5
      const result = computeClientTelomereAge(1.050, 30.0);
      expect(result.estimatedAge).toBe(43.5);
      expect(result.deltaAge).toBe(13.5);
      expect(result.deltaCategory).toBe("ACCELERATED");
    });

    it("detects decelerated biological aging when delta < -4.0 years", () => {
      // T/S = 1.250 -> estimated age ~ 20.0 years. If known age is 35.0 -> delta -15.0
      const result = computeClientTelomereAge(1.250, 35.0);
      expect(result.estimatedAge).toBe(20.0);
      expect(result.deltaAge).toBe(-15.0);
      expect(result.deltaCategory).toBe("DECELERATED");
    });

    it("verifies post-mortem ADH thermal kinetics for 72h decomposition at 20 C", () => {
      const vec = GOLDEN_VECTORS.find((v) => v.id === "VECTOR_19_PMI_D")!;
      expect(vec).toBeDefined();

      const pmi = computeClientPmiAdh(vec.pmiBeta, vec.ambientTemp);
      expect(pmi.accumulatedDegreeHours).toBeCloseTo(1413.3, 0);
      expect(pmi.pmiHours).toBeCloseTo(70.7, 0);
      expect(pmi.pmiDays).toBeCloseTo(2.9, 0);
      expect(pmi.ciLowerHours).toBeLessThan(pmi.pmiHours);
      expect(pmi.ciUpperHours).toBeGreaterThan(pmi.pmiHours);
    });

    it("verifies hypothermic retardation at 10 C chamber", () => {
      const vec = GOLDEN_VECTORS.find((v) => v.id === "VECTOR_19_PMI_E")!;
      expect(vec).toBeDefined();

      const pmi = computeClientPmiAdh(vec.pmiBeta, vec.ambientTemp);
      expect(pmi.ambientTemp).toBe(10.0);
      expect(pmi.pmiHours).toBeCloseTo(167.6, 0);
      // At 10 C, hours elapsed is twice that at 20 C for the same ADH
      expect(pmi.pmiAt10C).toBeCloseTo(pmi.pmiAt20C * 2, 0);
    });

    it("verifies somatic mosaicism index M and clonal classification boundaries", () => {
      // 1. Clonal homogeneity: M < 0.05
      const vecHomogeneity = GOLDEN_VECTORS.find((v) => v.id === "VECTOR_19_PMI_F")!;
      const resHomogeneity = computeClientMosaicismIndex(vecHomogeneity.tissue1, vecHomogeneity.tissue2);
      expect(resHomogeneity.mosaicismIndexM).toBeLessThan(0.05);
      expect(resHomogeneity.mosaicismClass).toBe("CLONAL_HOMOGENEITY");

      // 2. High somatic mosaicism anomaly: M > 0.15
      const vecChimerism = GOLDEN_VECTORS.find((v) => v.id === "VECTOR_19_PMI_G")!;
      const resChimerism = computeClientMosaicismIndex(vecChimerism.tissue1, vecChimerism.tissue2);
      expect(resChimerism.mosaicismIndexM).toBeGreaterThan(0.15);
      expect(resChimerism.mosaicismClass).toBe("HIGH_SOMATIC_MOSAICISM");
      expect(resChimerism.maxDelta).toBeGreaterThan(0.40);
    });

    it("verifies diagnostic CpG loci definitions", () => {
      expect(DIAGNOSTIC_LOCI).toHaveLength(8);
      expect(DIAGNOSTIC_LOCI.map((l) => l.gene)).toContain("ELOVL2");
      expect(DIAGNOSTIC_LOCI.map((l) => l.gene)).toContain("FHL2");
      expect(DIAGNOSTIC_LOCI.map((l) => l.gene)).toContain("PENK");
      expect(DIAGNOSTIC_LOCI.map((l) => l.gene)).toContain("AHRR");
    });

    it("generates deterministic 64-hex SHA-256 state audit digest", () => {
      const hash1 = computeTelomereAuditHash(
        1.2075,
        -0.272,
        0.50,
        20.0,
        { cg16867657: 0.22 },
        { cg16867657: 0.23 },
        { estimatedAge: 25.0, ciLower: 20.8, ciUpper: 29.2 },
        { pmiHours: 70.7, accumulatedDegreeHours: 1413.3 },
        { mosaicismIndexM: 0.01, mosaicismClass: "CLONAL_HOMOGENEITY" }
      );
      const hash2 = computeTelomereAuditHash(
        1.2075,
        -0.272,
        0.50,
        20.0,
        { cg16867657: 0.22 },
        { cg16867657: 0.23 },
        { estimatedAge: 25.0, ciLower: 20.8, ciUpper: 29.2 },
        { pmiHours: 70.7, accumulatedDegreeHours: 1413.3 },
        { mosaicismIndexM: 0.01, mosaicismClass: "CLONAL_HOMOGENEITY" }
      );
      expect(hash1).toHaveLength(64);
      expect(hash1).toBe(hash2);

      // Modified input produces divergent hash
      const hashModified = computeTelomereAuditHash(
        1.4200,
        -0.5059,
        0.85,
        20.0,
        { cg16867657: 0.22 },
        { cg16867657: 0.23 },
        { estimatedAge: 0.0, ciLower: 0.0, ciUpper: 4.2 },
        { pmiHours: 0.0, accumulatedDegreeHours: 0.0 },
        { mosaicismIndexM: 0.008, mosaicismClass: "CLONAL_HOMOGENEITY" }
      );
      expect(hashModified).not.toBe(hash1);
    });
  });

  // =========================================================================
  // 2. Component Integration & User Interactions
  // =========================================================================
  describe("Component Rendering & UI Interactions", () => {
    it("renders panel header, KPIs, and tab navigation buttons", () => {
      render(<PanelTelomere />);
      expect(screen.getByText(/Telomere Biological Chronometer|Adli Telomer Kronometresi/i)).toBeInTheDocument();
      expect(screen.getByText(/GORECELI T\/S ORANI|RELATIVE T\/S RATIO/i)).toBeInTheDocument();
      expect(screen.getByText(/1\. Telomer Bozunmasi|1\. Telomere Decay/i)).toBeInTheDocument();
      expect(screen.getByText(/2\. Olum Sonrasi PMI|2\. Post-Mortem PMI/i)).toBeInTheDocument();
      expect(screen.getByText(/3\. Somatik Mozaiklik|3\. Somatic Mosaicism/i)).toBeInTheDocument();
      expect(screen.getByText(/4\. Onayli Altin Vektorler|4\. Golden Benchmarks/i)).toBeInTheDocument();
      expect(screen.getByText(/5\. ISO 17025 Raporu|5\. ISO 17025 Reporting/i)).toBeInTheDocument();
    });

    it("navigates through all 5 tabs smoothly", () => {
      render(<PanelTelomere />);

      // Tab 2: PMI
      fireEvent.click(screen.getByText(/2\. Olum Sonrasi PMI|2\. Post-Mortem PMI/i));
      expect(screen.getByText(/PMI Thermal Summation Parameters|PMI Termal Parametreleri/i)).toBeInTheDocument();

      // Tab 3: Somatic Mosaicism
      fireEvent.click(screen.getByText(/3\. Somatik Mozaiklik|3\. Somatic Mosaicism/i));
      expect(screen.getByText(/MOZAIKLIK INDEKSI \(M\)|MOSAICISM INDEX \(M\)/i)).toBeInTheDocument();

      // Tab 4: Golden Benchmarks
      fireEvent.click(screen.getByText(/4\. Onayli Altin Vektorler|4\. Golden Benchmarks/i));
      expect(screen.getByText(/VECTOR_19_PMI_A/i)).toBeInTheDocument();

      // Tab 5: ISO Reporting
      fireEvent.click(screen.getByText(/5\. ISO 17025 Raporu|5\. ISO 17025 Reporting/i));
      expect(screen.getByText(/ISO\/IEC 17025:2017 SEC 7\.8/i)).toBeInTheDocument();
      expect(screen.getByText(/Kriptografik SHA-256 Durum Özeti|Cryptographic SHA-256 State Audit Digest/i)).toBeInTheDocument();
    });

    it("loads a golden benchmark vector and updates inputs", () => {
      render(<PanelTelomere />);

      // Go to Tab 4
      fireEvent.click(screen.getByText(/4\. Onayli Altin Vektorler|4\. Golden Benchmarks/i));

      // Click on VECTOR_19_PMI_C (Elderly)
      const loadBtn = screen.getByText(/VECTOR_19_PMI_C/i).closest("div");
      expect(loadBtn).toBeInTheDocument();
      fireEvent.click(loadBtn!);

      // Go back to Tab 1 and verify estimated age
      fireEvent.click(screen.getByText(/1\. Telomer Bozunmasi|1\. Telomere Decay/i));
      expect(screen.getAllByText(/75\.0/).length).toBeGreaterThanOrEqual(1);
    });

    it("executes chronometer analysis via REST API and handles server response", async () => {
      render(<PanelTelomere />);

      const executeBtn = screen.getByText(/Kronometreyi Calistir|Execute Chronometer/i);
      fireEvent.click(executeBtn);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining("/api/v1/forensic/epigenetics/telomere-and-pmi"),
          expect.objectContaining({
            method: "POST",
          })
        );
      });

      // Verify server verified badge appears
      await waitFor(() => {
        expect(screen.getByText(/Sunucu Doğrulamalı|Server Verified/i)).toBeInTheDocument();
      });
    });

    it("falls back to local model gracefully on API network failure", async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error("Network disconnect"));

      render(<PanelTelomere />);

      const executeBtn = screen.getByText(/Kronometreyi Calistir|Execute Chronometer/i);
      fireEvent.click(executeBtn);

      // Should complete without crashing and show fallback indicator
      await waitFor(() => {
        expect(screen.getByText(/Yerel Model|Local Engine/i)).toBeInTheDocument();
      });
    });

    it("copies cryptographic SHA-256 digest in Tab 5", async () => {
      render(<PanelTelomere />);

      // Switch to Tab 5
      fireEvent.click(screen.getByText(/5\. ISO 17025 Raporu|5\. ISO 17025 Reporting/i));

      // Find copy digest button
      const copyHashBtn = document.getElementById("copy-state-hash-btn");
      expect(copyHashBtn).toBeInTheDocument();
      fireEvent.click(copyHashBtn!);

      expect(navigator.clipboard.writeText).toHaveBeenCalled();
    });

    it("copies evaluative text report to clipboard and records case audit log", async () => {
      render(<PanelTelomere />);

      const copyReportBtn = screen.getByText(/Rapor Kopyala|Copy Report/i);
      fireEvent.click(copyReportBtn);

      expect(navigator.clipboard.writeText).toHaveBeenCalled();
      const caseStore = useForensicCaseStore.getState();
      expect(caseStore.auditTrail.length).toBeGreaterThan(0);
      expect(caseStore.auditTrail[0].module).toContain("22. Telomere Chronometer");
    });
  });
});
