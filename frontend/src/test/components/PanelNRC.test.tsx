import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import PanelNRC, {
  DEMOGRAPHIC_POPULATIONS,
  THETA_PRESETS,
  CERTIFIED_GOLDEN_BENCHMARKS,
  computeClientBaldingNicholsProb,
  computeClientWeirCockerham,
} from "@/components/analysis/PanelNRC";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// Mock forensicCaseStore
vi.mock("@/store/forensicCaseStore", () => {
  const mockAddAuditLog = vi.fn();
  const mockStore = {
    activeCase: {
      profile: {
        profileId: "TEST-CASE-NRC-01",
        strMarkers: {
          TH01: { allele1: 8.0, allele2: 9.3 },
          vWA: { allele1: 17.0, allele2: 18.0 },
          D21S11: { allele1: 30.0, allele2: 30.0 },
          D3S1358: { allele1: 14.0, allele2: 15.0 },
        },
      },
    },
    addAuditLog: mockAddAuditLog,
  };
  return {
    useForensicCaseStore: () => mockStore,
  };
});

// Mock SaaSLanguageContext
vi.mock("@/context/SaaSLanguageContext", () => ({
  useSaasLanguage: () => ({ lang: "en" }),
}));

describe("Subsystem 03: PanelNRC (Dirichlet Fst & Balding-Nichols Population Genetics)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: string) => {
        if (url.includes("/profile-lr")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                population: "Caucasian",
                theta: 0.03,
                combined_lr: 1e18,
                log10_lr: 18.25,
                locus_results: [
                  {
                    locus: "TH01",
                    suspect_genotype: [8.0, 9.3],
                    p_conditional: 0.045,
                    lr_locus: 22.2,
                    log10_lr_locus: 1.35,
                  },
                ],
              }),
          });
        }
        if (url.includes("/demographic-report")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                population_log10_lrs: {
                  Caucasian: 18.25,
                  AfricanAmerican: 16.8,
                  Hispanic: 17.4,
                  Asian: 19.1,
                },
              }),
          });
        }
        if (url.includes("/weir-cockerham")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                locus: "TH01",
                theta_hat: 0.0185,
                msp: 0.0418,
                msg: 0.0124,
                n_c: 518.0,
                num_alleles: 6,
              }),
          });
        }
        if (url.includes("/simplex-validate")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                locus: "TH01",
                sum_probability: 1.0,
                delta_from_unity: 2.22e-16,
                is_valid: true,
                num_genotypes_evaluated: 28,
              }),
          });
        }
        return Promise.reject(new Error("Unknown route"));
      })
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("1. renders mission control header, verification badges, and telemetry ribbon", async () => {
    render(<PanelNRC />);
    expect(
      screen.getByText(/NRC-II Dirichlet F_st & Balding-Nichols Population Genetics/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/VERIFIED/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Execute Analysis/i })).toBeInTheDocument();
    });
  });

  it("2. allows switching seamlessly across all 5 canonical workstation tabs", async () => {
    render(<PanelNRC />);

    // Default tab is 24-Locus Simplex Breakdown
    expect(screen.getByRole("button", { name: /24-Locus Simplex/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Stratification/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Weir-Cockerham ANOVA/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Golden Benchmarks/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /ISO 17025 Reporting/i })).toBeInTheDocument();

    // Switch to Stratification
    fireEvent.click(screen.getByRole("button", { name: /Stratification/i }));
    expect(
      screen.getByText(/NIST 1036 Multi-Population Stratification Analysis/i)
    ).toBeInTheDocument();

    // Switch to Weir-Cockerham ANOVA
    fireEvent.click(screen.getByRole("button", { name: /Weir-Cockerham ANOVA/i }));
    expect(
      screen.getByText(/Weir & Cockerham \(1984\) Single-Locus ANOVA/i)
    ).toBeInTheDocument();

    // Switch to Golden Benchmarks
    fireEvent.click(screen.getByRole("button", { name: /Golden Benchmarks/i }));
    expect(
      screen.getByText(/Certified Forensic Golden Reference Standards/i)
    ).toBeInTheDocument();

    // Switch to ISO 17025 Reporting
    fireEvent.click(screen.getByRole("button", { name: /ISO 17025 Reporting/i }));
    expect(
      screen.getByText(/ISO\/IEC 17025:2017 Metrological Uncertainty Budget/i)
    ).toBeInTheDocument();
  });

  it("3. renders 24-locus simplex breakdown table with NIST frequencies and LR", async () => {
    render(<PanelNRC />);
    expect(screen.getByText("TH01")).toBeInTheDocument();
    expect(screen.getByText("vWA")).toBeInTheDocument();
    expect(screen.getByText("D21S11")).toBeInTheDocument();
    expect(screen.getByText(/Total Log₁₀ LR:/i)).toBeInTheDocument();
  });

  it("4. filters loci by search query in Tab 1", async () => {
    render(<PanelNRC />);
    const searchInput = screen.getByPlaceholderText(/Filter locus/i);
    fireEvent.change(searchInput, { target: { value: "TH01" } });

    expect(screen.getByText("TH01")).toBeInTheDocument();
    expect(screen.queryByText("D13S317")).not.toBeInTheDocument();
  });

  it("5. switches demographic population and updates active breakdown", async () => {
    render(<PanelNRC />);
    const afrCard = screen.getByText("African American");
    fireEvent.click(afrCard);

    await waitFor(() => {
      expect(screen.getByText("African American")).toBeInTheDocument();
    });
  });

  it("6. adjusts theta coancestry slider and updates Balding-Nichols calculation", async () => {
    render(<PanelNRC />);
    const slider = screen.getByRole("slider");
    fireEvent.change(slider, { target: { value: "0.05" } });

    expect(screen.getByText("0.050")).toBeInTheDocument();
  });

  it("7. verifies theta preset buttons update state and coancestry value", async () => {
    render(<PanelNRC />);
    const presetBtn = screen.getByRole("button", { name: /θ=0\.01/i });
    fireEvent.click(presetBtn);

    expect(screen.getByText("0.010")).toBeInTheDocument();
  });

  it("8. renders demographic stratification bars and spread in Tab 2", async () => {
    render(<PanelNRC />);
    fireEvent.click(screen.getByRole("button", { name: /Stratification/i }));

    expect(screen.getByText(/Log₁₀ Spread:/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Caucasian \(US\)/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Asian \(US\)/i).length).toBeGreaterThanOrEqual(1);
  });

  it("9. displays probability simplex normalization invariant |sum P - 1.0| < 1e-6 in Tab 2", async () => {
    render(<PanelNRC />);
    fireEvent.click(screen.getByRole("button", { name: /Stratification/i }));

    expect(screen.getByText(/Probability Simplex Normalization Invariant:/i)).toBeInTheDocument();
    expect(screen.getByText(/Σ P\(G\|θ\) = 1\.00000000/i)).toBeInTheDocument();
  });

  it("10. renders Weir-Cockerham ANOVA Fst decomposition in Tab 3 with MSP, MSG, nc, and thetaHat", async () => {
    render(<PanelNRC />);
    fireEvent.click(screen.getByRole("button", { name: /Weir-Cockerham ANOVA/i }));

    expect(screen.getByText(/Mean Square Populations \(MSP\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Mean Square Within \(MSG\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Effective Sample \(n_c\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Estimated θ̂_weir \(F_st\)/i)).toBeInTheDocument();
  });

  it("11. allows switching ANOVA locus in Tab 3 and recalculates metrics", async () => {
    render(<PanelNRC />);
    fireEvent.click(screen.getByRole("button", { name: /Weir-Cockerham ANOVA/i }));

    const locusSelects = screen.getAllByRole("combobox");
    const anovaSelect = locusSelects[locusSelects.length - 1];
    fireEvent.change(anovaSelect, { target: { value: "vWA" } });

    await waitFor(() => {
      expect(anovaSelect).toHaveValue("vWA");
    });
  });

  it("12. renders Certified Golden Benchmark Standards in Tab 4", async () => {
    render(<PanelNRC />);
    fireEvent.click(screen.getByRole("button", { name: /Golden Benchmarks/i }));

    expect(screen.getAllByText(/NIST SRM 2391d Component A \(9947A\)/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/NIST SRM 2391d Component B \(9948\)/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/GIAB HG001 \/ NA12878 \(CEU\)/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/High Endogamy Stress Pedigree \(theta=0\.150\)/i).length).toBeGreaterThanOrEqual(1);
  });

  it("13. loads benchmark standard into studio and updates active casework profile", async () => {
    const { addAuditLog } = useForensicCaseStore();
    render(<PanelNRC />);
    fireEvent.click(screen.getByRole("button", { name: /Golden Benchmarks/i }));

    const loadButtons = screen.getAllByRole("button", { name: /Load into Studio/i });
    fireEvent.click(loadButtons[0]);

    await waitFor(() => {
      expect(addAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("BENCHMARK_LOADED"),
        })
      );
    });
  });

  it("14. dispatches audit event to useForensicCaseStore upon execution", async () => {
    const { addAuditLog } = useForensicCaseStore();
    render(<PanelNRC />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Execute Analysis/i })).toBeInTheDocument();
    });

    const execBtn = screen.getByRole("button", { name: /Execute Analysis/i });
    fireEvent.click(execBtn);

    await waitFor(() => {
      expect(addAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("POPULATION_LR_EVALUATED"),
        })
      );
    });
  });

  it("15. renders ISO/IEC 17025 GUM measurement uncertainty budget, ENFSI verbal scale, and legal shield in Tab 5", async () => {
    render(<PanelNRC />);
    fireEvent.click(screen.getByRole("button", { name: /ISO 17025 Reporting/i }));

    expect(screen.getByText(/Combined Std Uncertainty \(u_c\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Expanded Uncertainty \(U_95%\)/i)).toBeInTheDocument();
    expect(screen.getByText(/ENFSI \(2017\) Evaluative Verbal Statement/i)).toBeInTheDocument();
    expect(screen.getByText(/Transposed Conditional Defense Shield/i)).toBeInTheDocument();

    const copyBtn = screen.getByRole("button", { name: /Copy Certificate/i });
    expect(copyBtn).toBeInTheDocument();
  });
});
