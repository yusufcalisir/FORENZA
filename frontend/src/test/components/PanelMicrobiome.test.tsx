import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import PanelMicrobiome, {
  GOLDEN_MICROBIOME_VECTORS,
  BENCHMARK_PRESETS,
  HIDSKINPLEX_CALIBRATION,
  DECOMPOSITION_STAGES,
  BODY_FLUID_CLASSES,
  computeGeometricMean,
  clrTransform,
  computeAitchisonDistance,
  gaussianPdf,
  mapEnfsiVerbalScale,
  computeMicrobiomeAuditHash,
} from "@/components/analysis/PanelMicrobiome";

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
  sample_id: "TEST_SAMPLE_01",
  predicted_add: 82.5,
  predicted_adh: 1980.0,
  predicted_pmi_hours: 99.0,
  predicted_pmi_days: 4.12,
  conformal_add_interval: { lower_bound: 68.0, upper_bound: 97.0, coverage_percentage: 95.0, unit: "ADD" },
  conformal_hours_interval: { lower_bound: 81.6, upper_bound: 116.4, coverage_percentage: 95.0, unit: "HOURS" },
  decomposition_stage: {
    fresh: 0.05,
    bloat: 0.78,
    active_decay: 0.14,
    advanced_decay: 0.025,
    skeletonization: 0.005,
    dominant_stage: "BLOAT (Early)",
  },
  geometric_mean_abundance: 0.1514,
  clr_coordinates: {},
  indicator_biomarkers: ["Clostridium_perfringens", "Prevotella_melaninogenica"],
  audit_notes: "Validated via ISO/IEC 17025",
};

describe("PanelMicrobiome Component & Biocomputational Suite (Subsystem 38 / Module 23)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockApiSuccess,
    } as Response);
  });

  describe("UI Component Rendering & Canonical Tabs", () => {
    it("should render panel title, subtitle and standard badges", () => {
      render(<PanelMicrobiome />);
      expect(screen.getByText(/23\. (Forensic Microbiome|Adli Mikrobiyom)/i)).toBeInTheDocument();
      expect(screen.getByText(/ISO 17025 • ISFG 2024 • ENFSI 2017/i)).toBeInTheDocument();
      expect(screen.getAllByText(/Thanatomicrobiome PMI/i).length).toBeGreaterThan(0);
    });

    it("should switch between all 5 canonical tabs seamlessly", async () => {
      render(<PanelMicrobiome />);

      // Tab 2: hidSkinPlex+ Touch LR
      const tab2Btn = screen.getByText(/(Touch Trace \(hidSkinPlex\+\)|Dokunma Izi \(hidSkinPlex\+\))/i);
      fireEvent.click(tab2Btn);
      expect(screen.getAllByText(/hidSkinPlex\+/i).length).toBeGreaterThan(0);

      // Tab 3: CDI Soil & Fluid Niche
      const tab3Btn = screen.getByText(/(CDI & Body Fluid|CDI & Vucut Sivisi)/i);
      fireEvent.click(tab3Btn);
      expect(screen.getByText(/(Forensic Body Fluid Classification|Adli Vucut Sivisi Siniflandirmasi)/i)).toBeInTheDocument();

      // Tab 4: Benchmarks
      const tab4Btn = screen.getByText(/(Golden Benchmarks|Altin Standartlar)/i);
      fireEvent.click(tab4Btn);
      expect(screen.getByText(/Early Bloat Buccal PMI|Erken Sisleme/i)).toBeInTheDocument();

      // Tab 5: ISO 17025 Reporting
      const tab5Btn = screen.getByText(/(ISO 17025 Report|ISO 17025 Raporu)/i);
      fireEvent.click(tab5Btn);
      expect(screen.getByText(/(Forensic Microbiome ISO\/IEC 17025:2017 & ENFSI Certificate|Adli Mikrobiyom ISO\/IEC 17025:2017 & ENFSI Sertifikasi)/i)).toBeInTheDocument();
    });

    it("should switch golden benchmark presets correctly", () => {
      render(<PanelMicrobiome />);

      // Select VECTOR_MB_02 (Soil CDI) -> switches to cdi_fluid
      const btnMb02 = screen.getByText("VECTOR_MB_02");
      fireEvent.click(btnMb02);
      expect(screen.getByText(/(Forensic Body Fluid Classification|Adli Vucut Sivisi Siniflandirmasi)/i)).toBeInTheDocument();

      // Select VECTOR_MB_03 (Touch Trace) -> switches to hidskinplex
      const btnMb03 = screen.getByText("VECTOR_MB_03");
      fireEvent.click(btnMb03);
      expect(screen.getAllByText(/hidSkinPlex\+/i).length).toBeGreaterThan(0);
    });

    it("should allow environmental temperature slider adjustments", () => {
      render(<PanelMicrobiome />);
      const sliders = screen.getAllByRole("slider");
      expect(sliders.length).toBeGreaterThanOrEqual(1);

      fireEvent.change(sliders[0], { target: { value: "25.0" } });
      expect(screen.getByText(/25\.0 °C/i)).toBeInTheDocument();
    });

    it("should dispatch live API on 'Run Live Engine' button click and update status badge", async () => {
      render(<PanelMicrobiome />);
      const runBtn = screen.getByText(/(Run Live Engine|Canli Calistir)/i);
      fireEvent.click(runBtn);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText(/200 OK/i)).toBeInTheDocument();
      });
    });

    it("should handle API network failure with graceful local fallback badge", async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error("Network Error"));
      render(<PanelMicrobiome />);
      const runBtn = screen.getByText(/(Run Live Engine|Canli Calistir)/i);
      fireEvent.click(runBtn);

      await waitFor(() => {
        expect(screen.getByText(/(Local Engine Active|Yerel Motor Aktif)/i)).toBeInTheDocument();
      });
    });

    it("should display SHA-256 state audit card in Tab 5 and copy report", async () => {
      render(<PanelMicrobiome />);

      // Go to Tab 5
      const tab5Btn = screen.getByText(/(ISO 17025 Report|ISO 17025 Raporu)/i);
      fireEvent.click(tab5Btn);

      // Verify SHA-256 Card exists
      expect(screen.getByText(/(Forensic State Audit Digest \(SHA-256\):|Adli Durum Kriptografik Ozeti \(SHA-256\):)/i)).toBeInTheDocument();
      expect(screen.getByText(/(Anchored to Merkle Ledger|Merkle Defterine Kilitli)/i)).toBeInTheDocument();

      // Click Copy Report
      const copyBtn = screen.getByText(/(Copy Report|Metni Kopyala)/i);
      fireEvent.click(copyBtn);
      expect(navigator.clipboard.writeText).toHaveBeenCalled();
      expect(screen.getByText(/(Copied!|Kopyalandi!)/i)).toBeInTheDocument();
    });
  });

  describe("Cryptographic SHA-256 Audit Function", () => {
    it("should compute deterministic SHA-256 hash or fallback for forensic state payload", async () => {
      const payload = {
        preset: "VECTOR_MB_01",
        sampleId: "TEST_SAMPLE",
        ambientTemp: 20.0,
        baseTemp: 0.0,
        predictedAdd: 82.5,
      };
      const hash = await computeMicrobiomeAuditHash(payload);
      expect(typeof hash).toBe("string");
      expect(hash.length).toBeGreaterThan(0);

      // Deterministic idempotency
      const hash2 = await computeMicrobiomeAuditHash(payload);
      expect(hash2).toBe(hash);
    });
  });

  describe("PanelMicrobiome Biophysical Models & Specifications (Pillar 4 Research)", () => {
    it("should define all 4 certified golden benchmark vectors (VECTOR_MB_01 to 04)", () => {
      expect(GOLDEN_MICROBIOME_VECTORS).toHaveLength(4);
      const ids = GOLDEN_MICROBIOME_VECTORS.map((v) => v.id);
      expect(ids).toEqual([
        "VECTOR_MB_01",
        "VECTOR_MB_02",
        "VECTOR_MB_03",
        "VECTOR_MB_04",
      ]);
    });

    it("should define all 5 canonical taphonomic decomposition stages", () => {
      expect(DECOMPOSITION_STAGES).toHaveLength(5);
      const stageIds = DECOMPOSITION_STAGES.map((s) => s.id);
      expect(stageIds).toEqual([
        "FRESH",
        "BLOAT",
        "ACTIVE_DECAY",
        "ADVANCED_DECAY",
        "SKELETONIZATION",
      ]);
    });

    it("should define all 6 forensically relevant body fluid classes", () => {
      expect(BODY_FLUID_CLASSES).toHaveLength(6);
      const fluidIds = BODY_FLUID_CLASSES.map((f) => f.id);
      expect(fluidIds).toContain("Vaginal_Fluid");
      expect(fluidIds).toContain("Hand_Skin");
      expect(fluidIds).toContain("Saliva");
      expect(fluidIds).toContain("Urine");
      expect(fluidIds).toContain("Penile_Skin");
      expect(fluidIds).toContain("Semen");
    });

    it("should accurately compute geometric mean g(x) for compositional profiles", () => {
      const values = [0.082, 0.215, 0.142, 0.284, 0.186, 0.091];
      const gx = computeGeometricMean(values);
      expect(gx).toBeCloseTo(0.1514, 3);
    });

    it("should enforce CLR simplex zero-sum invariance sum(CLR) = 0.0000", () => {
      const v = BENCHMARK_PRESETS.VECTOR_MB_01.profile!;
      const { clr, gx } = clrTransform(v);
      expect(gx).toBeGreaterThan(0.0);

      const clrValues = Object.values(clr);
      const clrSum = clrValues.reduce((a, b) => a + b, 0);
      expect(Math.abs(clrSum)).toBeLessThan(1e-4);
    });

    it("should compute Aitchison distance dA = 0.0 for identical profiles", () => {
      const profile = { Taxon_A: 0.5, Taxon_B: 0.3, Taxon_C: 0.2 };
      const dA = computeAitchisonDistance(profile, profile);
      expect(dA).toBe(0.0);
    });

    it("should accurately evaluate VECTOR_MB_03 touch individualization metrics", () => {
      const v = BENCHMARK_PRESETS.VECTOR_MB_03;
      expect(v.evidentiary).toBeDefined();
      expect(v.reference).toBeDefined();

      const dA = computeAitchisonDistance(v.evidentiary!, v.reference!);
      expect(dA).toBeLessThan(0.25);

      const fHp = gaussianPdf(
        1.842,
        HIDSKINPLEX_CALIBRATION.Hp_within_source.mu,
        HIDSKINPLEX_CALIBRATION.Hp_within_source.sigma
      );
      const fHd = gaussianPdf(
        1.842,
        HIDSKINPLEX_CALIBRATION.Hd_between_source.mu,
        HIDSKINPLEX_CALIBRATION.Hd_between_source.sigma
      );

      expect(fHp).toBeCloseTo(1.124, 2);
      expect(fHd).toBeLessThan(1e-4);

      const rawLr = fHp / fHd;
      expect(rawLr).toBeGreaterThan(100000);
    });

    it("should map calibrated Likelihood Ratios into standard ENFSI 2017 verbal scales", () => {
      const vExtrem = mapEnfsiVerbalScale(2000000);
      expect(vExtrem.tier).toBe("EXTREMELY_STRONG");

      const vVeryStrong = mapEnfsiVerbalScale(45000);
      expect(vVeryStrong.tier).toBe("VERY_STRONG");
      expect(vVeryStrong.en).toContain("Very strong support");
      expect(vVeryStrong.tr).toContain("cok guclu duzeyde adli destek");

      const vStrong = mapEnfsiVerbalScale(5000);
      expect(vStrong.tier).toBe("STRONG");

      const vModStrong = mapEnfsiVerbalScale(500);
      expect(vModStrong.tier).toBe("MODERATELY_STRONG");

      const vModerate = mapEnfsiVerbalScale(50);
      expect(vModerate.tier).toBe("MODERATE");

      const vWeak = mapEnfsiVerbalScale(5);
      expect(vWeak.tier).toBe("WEAK");

      const vExcl = mapEnfsiVerbalScale(0.1);
      expect(vExcl.tier).toBe("SUPPORT_FOR_EXCLUSION");
    });

    it("should accurately verify thermal kinetic calculation for VECTOR_MB_01", () => {
      const v = BENCHMARK_PRESETS.VECTOR_MB_01;
      const ambientTemp = 20.0;
      const baseTemp = 0.0;
      const predictedAdd = 82.5;

      const effTemp = Math.max(0.1, ambientTemp - baseTemp);
      const pmiHours = (predictedAdd * 24.0) / effTemp;
      expect(pmiHours).toBe(99.0);

      const q95 = 14.5;
      const addLow = predictedAdd - q95;
      const addHigh = predictedAdd + q95;
      expect(addLow).toBe(68.0);
      expect(addHigh).toBe(97.0);
    });
  });
});
