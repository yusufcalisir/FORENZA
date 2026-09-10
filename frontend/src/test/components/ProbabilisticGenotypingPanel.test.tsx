import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ProbabilisticGenotypingPanel, {
  computeDirichletSimplex,
  computeCurranGillDropout,
  computeEuroForMixGammaLogL,
  computeSTRmixLogNormalLogL,
  computeGelmanRubinDiagnostic,
  computeMCMCAuditHash,
  LOCUS_STUTTER_RATIOS,
  GOLDEN_MCMC_BENCHMARKS,
  CASEWORK_PRESETS,
} from "@/components/analysis/ProbabilisticGenotypingPanel";

// Mock central forensic case store
const mockAddAuditLog = vi.fn();
vi.mock("@/store/forensicCaseStore", () => ({
  useForensicCaseStore: () => ({
    activeCase: {
      metadata: { caseId: "CAS-TEST-2026", status: "ACTIVE", leadAnalyst: "Dr. H. C. Lee" },
      profile: {
        profileId: "EVD-TEST-MIX-01",
        strMarkers: {
          TH01: { allele1: 6.0, allele2: 9.3 },
          VWA: { allele1: 16.0, allele2: 17.0 },
          D18S51: { allele1: 12.0, allele2: 16.0 },
        },
      },
    },
    addAuditLog: mockAddAuditLog,
  }),
}));

// Mock SaaSLanguageContext
vi.mock("@/context/SaaSLanguageContext", () => ({
  useSaasLanguage: () => ({
    lang: "en",
    setLang: vi.fn(),
  }),
}));

describe("Subsystem 02: MCMC Probabilistic Mixture Deconvolution Engine", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("1. Mathematical Invariants & Biocomputational Kinetics", () => {
    it("enforces Dirichlet probability simplex normalization |sum w_k - 1.0| <= 1e-5", () => {
      // 2-person 70:30 mixture (NIST SRM 2391d)
      expect(computeDirichletSimplex([0.70, 0.30])).toBe(true);

      // 3-person 50:30:20 mixture (PROVEDIt)
      expect(computeDirichletSimplex([0.50, 0.30, 0.20])).toBe(true);

      // 4-person complex mixture
      expect(computeDirichletSimplex([0.45, 0.25, 0.18, 0.12])).toBe(true);

      // Invalid simplex (sum > 1.0)
      expect(computeDirichletSimplex([0.70, 0.40])).toBe(false);

      // Invalid simplex (negative weight)
      expect(computeDirichletSimplex([1.20, -0.20])).toBe(false);

      // Empty array
      expect(computeDirichletSimplex([])).toBe(false);
    });

    it("evaluates Curran-Gill logistic dropout curve P(D|x) with exact research constants", () => {
      // At 0 RFU: high dropout (~92.4%)
      expect(computeCurranGillDropout(0)).toBeCloseTo(0.924, 2);

      // At 100 RFU: inflection point (logit = 2.50 - 0.025 * 100 = 0 -> P = 0.50)
      expect(computeCurranGillDropout(100)).toBeCloseTo(0.50, 2);

      // At 240 RFU: low dropout (< 5%)
      expect(computeCurranGillDropout(240)).toBeLessThan(0.05);

      // Monotonic decreasing with peak height
      expect(computeCurranGillDropout(300)).toBeLessThan(computeCurranGillDropout(150));
    });

    it("computes EuroForMix Gamma log-likelihood for observed and expected peak heights", () => {
      const logL = computeEuroForMixGammaLogL(195, 200, 0.15);
      expect(logL).toBeCloseTo(-4.31, 1);

      // Edge cases: non-positive heights return -999.0
      expect(computeEuroForMixGammaLogL(0, 200, 0.15)).toBe(-999.0);
      expect(computeEuroForMixGammaLogL(195, -10, 0.15)).toBe(-999.0);
      expect(computeEuroForMixGammaLogL(195, 200, 0)).toBe(-999.0);
    });

    it("computes STRmix Log-Normal log-likelihood with power variance scaling", () => {
      const logL = computeSTRmixLogNormalLogL(195, 200, 0.12, 1.0);
      expect(logL).toBeCloseTo(-0.60, 1);

      // Edge cases: non-positive heights return -999.0
      expect(computeSTRmixLogNormalLogL(0, 200, 0.12)).toBe(-999.0);
      expect(computeSTRmixLogNormalLogL(195, 0, 0.12)).toBe(-999.0);
      expect(computeSTRmixLogNormalLogL(195, 200, 0)).toBe(-999.0);
    });

    it("verifies Gelman-Rubin convergence criterion threshold R-hat <= 1.05", () => {
      // Equal between and within chain variances: converged
      const rHat1 = computeGelmanRubinDiagnostic([1.0, 1.0, 1.0], 0.01);
      expect(rHat1).toBeLessThanOrEqual(1.05);

      // Divergent chain variances: between-chain variance is high -> not converged
      const rHat2 = computeGelmanRubinDiagnostic([1.0, 1.0, 1.0], 3.0);
      expect(rHat2).toBeGreaterThan(1.05);

      // Empty chains return 1.0 default
      expect(computeGelmanRubinDiagnostic([], 0)).toBe(1.0);
    });

    it("computes reproducible 64-hex SHA-256 state audit digest (H_mcmc)", async () => {
      const params = {
        caseId: "CAS-TEST-2026",
        sampleId: "EVD-TEST-MIX-01",
        modelEngine: "STRmix",
        numContributors: 2,
        sampleRfu: 240,
        mixtureRatio: 0.70,
        mcmcSteps: 6000,
        log10Lr: 8.74,
        rHatMax: 1.008,
        essMin: 3420,
      };

      const hash1 = await computeMCMCAuditHash(params);
      const hash2 = await computeMCMCAuditHash(params);

      expect(hash1).toHaveLength(64);
      expect(hash1).toBe(hash2);
      expect(/^[0-9a-f]{64}$/.test(hash1)).toBe(true);

      // Changing parameter yields different hash
      const hash3 = await computeMCMCAuditHash({ ...params, mixtureRatio: 0.75 });
      expect(hash3).not.toBe(hash1);
    });

    it("defines 24-locus back-stutter reference ratios conforming to SWGDAM 2020", () => {
      expect(Object.keys(LOCUS_STUTTER_RATIOS)).toHaveLength(24);
      expect(LOCUS_STUTTER_RATIOS["TH01"]).toBe(0.025);
      expect(LOCUS_STUTTER_RATIOS["VWA"]).toBe(0.078);
      expect(LOCUS_STUTTER_RATIOS["D18S51"]).toBe(0.092);
      expect(LOCUS_STUTTER_RATIOS["SE33"]).toBe(0.110);
      expect(LOCUS_STUTTER_RATIOS["D12S391"]).toBe(0.112);
    });

    it("verifies certified Golden MCMC Benchmarks catalog", () => {
      expect(GOLDEN_MCMC_BENCHMARKS).toHaveLength(3);
      expect(GOLDEN_MCMC_BENCHMARKS[0].id).toBe("VECTOR_01_SRM2391D");
      expect(GOLDEN_MCMC_BENCHMARKS[0].nominalWeights).toEqual([0.70, 0.30]);
      expect(GOLDEN_MCMC_BENCHMARKS[1].id).toBe("VECTOR_02_IMBALANCE");
      expect(GOLDEN_MCMC_BENCHMARKS[2].id).toBe("VECTOR_03_PROVEDIT_3P");
    });
  });

  describe("2. Component Rendering & Canonical 5-Tab Navigation", () => {
    it("renders mission header with SWGDAM (2020), ISFG (2016), and ISO 17025 telemetry", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);
      expect(container).toBeInTheDocument();

      // Mission title check
      expect(
        screen.getAllByText(/Continuous Probabilistic Genotyping Engine|Sürekli Olasılıksal Genotipleme Motoru/i).length
      ).toBeGreaterThan(0);

      // Standards check
      expect(
        screen.getAllByText(/SWGDAM \(2020\) • ISFG \(2016\) • ISO\/IEC 17025/i).length
      ).toBeGreaterThan(0);
    });

    it("allows switching between all 5 canonical tabs (Deconvolution, Loci, Stochastic, Models, Court)", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      // 1. Switch to Locus Genotypes tab
      const lociTabBtn = container.querySelector("#tab-loci");
      expect(lociTabBtn).toBeInTheDocument();
      fireEvent.click(lociTabBtn!);
      expect(
        screen.getAllByText(/Continuous Locus Deconvolution Calls|Sürekli Lokus Ayrıştırma Çağrıları/i).length
      ).toBeGreaterThan(0);

      // 2. Switch to Stochastic Models tab
      const stochasticTabBtn = container.querySelector("#tab-stochastic");
      expect(stochasticTabBtn).toBeInTheDocument();
      fireEvent.click(stochasticTabBtn!);
      expect(container.querySelector("#sample-rfu-slider")).toBeInTheDocument();
      expect(container.querySelector("#rfu-threshold-slider")).toBeInTheDocument();

      // 3. Switch to Biophysical Models tab
      const modelsTabBtn = container.querySelector("#tab-models");
      expect(modelsTabBtn).toBeInTheDocument();
      fireEvent.click(modelsTabBtn!);
      expect(
        screen.getAllByText(/Continuous Likelihood Kernel|Sürekli Olabilirlik Çekirdeği/i).length
      ).toBeGreaterThan(0);
      expect(
        screen.getAllByText(/24-Locus Back-Stutter Reference Matrix|24-Lokus Geri Kekemelik Referans Matrisi/i).length
      ).toBeGreaterThan(0);

      // 4. Switch to Court Admissibility & Audit tab
      const courtTabBtn = container.querySelector("#tab-court");
      expect(courtTabBtn).toBeInTheDocument();
      fireEvent.click(courtTabBtn!);
      expect(
        screen.getAllByText(/ISO\/IEC 17025:2017.*Evaluative Certificate|ISO\/IEC 17025:2017.*Değerlendirme Sertifikası/i).length
      ).toBeGreaterThan(0);

      // 5. Switch back to MCMC Deconvolution tab
      const deconvTabBtn = container.querySelector("#tab-deconvolution");
      expect(deconvTabBtn).toBeInTheDocument();
      fireEvent.click(deconvTabBtn!);
      expect(
        screen.getAllByText(/Combined Likelihood Ratio|Birleşik Olabilirlik Oranı/i).length
      ).toBeGreaterThan(0);
    });

    it("renders locus deconvolution table in Loci tab", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);
      const lociTabBtn = container.querySelector("#tab-loci");
      fireEvent.click(lociTabBtn!);

      expect(screen.getByText("TH01")).toBeInTheDocument();
      expect(screen.getByText("VWA")).toBeInTheDocument();
      expect(screen.getByText("D18S51")).toBeInTheDocument();
    });

    it("toggles between STRmix and EuroForMix engines and updates kernel display", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);
      const stochasticTabBtn = container.querySelector("#tab-stochastic");
      fireEvent.click(stochasticTabBtn!);

      const euroBtn = container.querySelector("#engine-euroformix-btn");
      expect(euroBtn).toBeInTheDocument();
      fireEvent.click(euroBtn!);

      expect(screen.getAllByText(/EuroForMix/i).length).toBeGreaterThan(0);
      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("EuroForMix"),
          module: "MCMC Probabilistic Genotyping",
        })
      );
    });

    it("renders 24-locus back-stutter reference table and multi-chain traces in Models tab", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);
      const modelsTabBtn = container.querySelector("#tab-models");
      fireEvent.click(modelsTabBtn!);

      expect(screen.getByText("D3S1358")).toBeInTheDocument();
      expect(screen.getByText("SE33")).toBeInTheDocument();
      expect(screen.getByText("TH01")).toBeInTheDocument();
      expect(
        screen.getAllByText(/Multi-Chain MCMC Convergence Traces|Çok Zincirli MCMC Yakınsama İzleri/i).length
      ).toBeGreaterThan(0);
    });

    it("renders official ISO/IEC 17025 Courtroom Certificate and ENFSI 7-tier verbal scale in Court tab", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);
      const courtTabBtn = container.querySelector("#tab-court");
      fireEvent.click(courtTabBtn!);

      expect(screen.getByText(/CERT-MCMC-CAS-TEST-2026/i)).toBeInTheDocument();
      expect(screen.getByText("Dr. H. C. Lee")).toBeInTheDocument();
      expect(
        screen.getAllByText(/Extremely strong support for inclusion \(Hp\)|Dahil olma lehine son derece güçlü delil \(Hp\)/i).length
      ).toBeGreaterThan(0);
    });

    it("computes and displays 64-hex SHA-256 state audit digest in Court tab with copy button", async () => {
      // Mock navigator.clipboard before render
      const writeTextMock = vi.fn().mockResolvedValue(undefined);
      Object.assign(navigator, {
        clipboard: { writeText: writeTextMock },
      });

      const { container } = render(<ProbabilisticGenotypingPanel />);
      const courtTabBtn = container.querySelector("#tab-court");
      fireEvent.click(courtTabBtn!);

      const copyHashBtn = container.querySelector("#copy-mcmc-hash-btn");
      expect(copyHashBtn).toBeInTheDocument();

      fireEvent.click(copyHashBtn!);
      await waitFor(() => {
        expect(writeTextMock).toHaveBeenCalled();
        expect(mockAddAuditLog).toHaveBeenCalledWith(
          expect.objectContaining({
            event: expect.stringContaining("State Audit Hash Copied"),
            module: "MCMC Probabilistic Genotyping",
          })
        );
      });
    });

    it("dispatches audit log event when copying courtroom certificate", async () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);
      const courtTabBtn = container.querySelector("#tab-court");
      fireEvent.click(courtTabBtn!);

      const copyCertBtn = container.querySelector("#copy-mcmc-cert-btn");
      expect(copyCertBtn).toBeInTheDocument();

      const writeTextMock = vi.fn().mockResolvedValue(undefined);
      Object.assign(navigator, {
        clipboard: { writeText: writeTextMock },
      });

      fireEvent.click(copyCertBtn!);
      await waitFor(() => {
        expect(writeTextMock).toHaveBeenCalled();
        expect(mockAddAuditLog).toHaveBeenCalledWith(
          expect.objectContaining({
            event: expect.stringContaining("Court Certificate Copied"),
            module: "MCMC Probabilistic Genotyping",
          })
        );
      });
    });

    it("dispatches audit log event when exporting JSON report", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);
      const courtTabBtn = container.querySelector("#tab-court");
      fireEvent.click(courtTabBtn!);

      const exportBtn = container.querySelector("#export-mcmc-json-btn");
      expect(exportBtn).toBeInTheDocument();

      // Mock createObjectURL and click
      const originalCreateObjectURL = window.URL.createObjectURL;
      const originalRevokeObjectURL = window.URL.revokeObjectURL;
      window.URL.createObjectURL = vi.fn().mockReturnValue("blob:mock-url");
      window.URL.revokeObjectURL = vi.fn();

      fireEvent.click(exportBtn!);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("JSON Forensic Report Exported"),
          module: "MCMC Probabilistic Genotyping",
        })
      );

      window.URL.createObjectURL = originalCreateObjectURL;
      window.URL.revokeObjectURL = originalRevokeObjectURL;
    });

    it("adjusts contributor count K (K=2, K=3, K=4) and dispatches audit event", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);
      const stochasticTabBtn = container.querySelector("#tab-stochastic");
      fireEvent.click(stochasticTabBtn!);

      const k3Btn = container.querySelector("#btn-contributor-k3");
      expect(k3Btn).toBeInTheDocument();
      fireEvent.click(k3Btn!);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: "MCMC Contributor Count Set to K=3",
          module: "MCMC Probabilistic Genotyping",
        })
      );
    });

    it("switches casework presets and updates nominal mixture weights", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      const touchPresetBtn = container.querySelector("#preset-btn-imbalance_touch");
      expect(touchPresetBtn).toBeInTheDocument();
      fireEvent.click(touchPresetBtn!);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("High-Imbalance Touch"),
          module: "MCMC Probabilistic Genotyping",
        })
      );
    });

    it("ingests active casework profile and displays case link badge", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      const loadCaseBtn = container.querySelector("#load-casework-profile-btn");
      expect(loadCaseBtn).toBeInTheDocument();
      fireEvent.click(loadCaseBtn!);

      // Case link badge should appear
      expect(
        screen.getAllByText(/CASE LINKED|VAKA AKTİF/i).length
      ).toBeGreaterThan(0);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("Active Casework STR Profile Linked"),
          module: "MCMC Probabilistic Genotyping",
        })
      );
    });

    it("executes MCMC sampling and updates progress bar and state diagnostics", async () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      const runBtn = container.querySelector("#run-mcmc-btn");
      expect(runBtn).toBeInTheDocument();

      fireEvent.click(runBtn!);

      // Should dispatch audit entry
      await waitFor(() => {
        expect(mockAddAuditLog).toHaveBeenCalledWith(
          expect.objectContaining({
            event: expect.stringContaining("MCMC Mixture Deconvolution Executed"),
            module: "MCMC Probabilistic Genotyping",
          })
        );
      });
    });

    it("dynamically updates locus deconvolution without locus loss when casework profile is linked", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      const loadCaseBtn = container.querySelector("#load-casework-profile-btn");
      expect(loadCaseBtn).toBeInTheDocument();
      fireEvent.click(loadCaseBtn!);

      // Switch to Loci tab to view deconvoluted loci
      const tabLociBtn = container.querySelector("#tab-loci");
      expect(tabLociBtn).toBeInTheDocument();
      fireEvent.click(tabLociBtn!);

      // Casework has TH01, VWA, D18S51: all must be rendered
      expect(screen.getAllByText(/TH01/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/VWA/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/D18S51/i).length).toBeGreaterThan(0);
    });

    it("displays FastAPI Live badge on successful API deconvolution response", async () => {
      const originalFetch = global.fetch;
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          n_contributors: 2,
          model_engine: "STRmix",
          log10_lr_point: 8.92,
          posterior_mixture_weights: [0.72, 0.28],
          convergence: { r_hat_max: 1.006, converged: true },
        }),
      } as Response);

      try {
        const { container } = render(<ProbabilisticGenotypingPanel />);
        const runBtn = container.querySelector("#run-mcmc-btn");
        expect(runBtn).toBeInTheDocument();
        fireEvent.click(runBtn!);

        await waitFor(() => {
          const liveBadge = container.querySelector("#mcmc-backend-live-badge");
          expect(liveBadge).toBeInTheDocument();
          expect(liveBadge?.textContent).toContain("FastAPI Live");
        });
      } finally {
        global.fetch = originalFetch;
      }
    });

    it("displays Client Engine Active badge on network error fallback", async () => {
      const originalFetch = global.fetch;
      global.fetch = vi.fn().mockRejectedValue(new Error("Network connection error"));

      try {
        const { container } = render(<ProbabilisticGenotypingPanel />);
        const runBtn = container.querySelector("#run-mcmc-btn");
        expect(runBtn).toBeInTheDocument();
        fireEvent.click(runBtn!);

        await waitFor(() => {
          const simBadge = container.querySelector("#mcmc-backend-sim-badge");
          expect(simBadge).toBeInTheDocument();
          expect(simBadge?.textContent).toContain("Client Engine Active");
        });
      } finally {
        global.fetch = originalFetch;
      }
    });

    it("renders Prosecutor's Fallacy Shield with transposed conditional defense", () => {
      const { container } = render(<ProbabilisticGenotypingPanel />);

      expect(
        screen.getAllByText(/Active Prosecutor's Fallacy Shield|Aktif Savcı Yanılgısı Kalkanı/i).length
      ).toBeGreaterThan(0);
    });
  });
});
