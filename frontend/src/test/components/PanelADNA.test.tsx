import React from "react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PanelADNA, {
  ADNA_PRESETS,
  DEFAULT_SNP_LOCI,
  computeBriggsDeaminationRate,
  computeMapDamageProfile,
  computeExponentialFragmentation,
  subtractModernContamination,
  evaluatePurineExcess,
  computeDamageAwareSnpLikelihood,
  computeMultiLociSnpEvaluations,
  computeEvidenceHash,
} from "@/components/analysis/PanelADNA";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// Mock global fetch for backend endpoints
beforeEach(() => {
  vi.restoreAllMocks();
  global.fetch = vi.fn().mockImplementation((url: string) => {
    if (url.includes("/api/v1/forensic/adna/mapdamage-profile")) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          curve_5p_c_to_t: { "1": 0.385, "2": 0.334, "3": 0.291, "25": 0.016 },
          curve_3p_g_to_a: { "1": 0.377, "2": 0.327, "3": 0.285, "25": 0.015 },
          asymptotic_error: 0.005,
        }),
      });
    }
    if (url.includes("/api/v1/forensic/adna/fragmentation")) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          mean_length: 52.4,
          median_length: 45.5,
          fraction_below_100bp: 0.956,
          degradation_tier: "SEVERE",
        }),
      });
    }
    if (url.includes("/api/v1/forensic/adna/contamination-subtraction")) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          true_ancient_delta_0: 0.3999,
          contamination_fraction: 0.05,
        }),
      });
    }
    if (url.includes("/api/v1/forensic/adna/purine-excess")) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          purine_minus_1_frequency: 0.72,
          is_ancient_authentic: true,
        }),
      });
    }
    return Promise.resolve({
      ok: true,
      json: async () => ({}),
    });
  });
});

describe("PanelADNA - Subsystem 12 Biocomputational Engine & UI Suite", () => {
  // ── 1. Pure Mathematical Biocomputational Function Tests ─────────────────

  it("calculates exact Briggs terminal deamination rates D(k) with exponential decay", () => {
    const delta0 = 0.38;
    const alpha = 0.14;
    const beta = 0.005;

    // k = 1: D(1) = delta0 * exp(0) + beta = 0.38 + 0.005 = 0.385
    const rate1 = computeBriggsDeaminationRate(1, delta0, alpha, beta);
    expect(rate1).toBeCloseTo(0.385, 4);

    // k = 2: D(2) = 0.38 * exp(-0.14) + 0.005
    const rate2 = computeBriggsDeaminationRate(2, delta0, alpha, beta);
    const expectedRate2 = 0.38 * Math.exp(-0.14) + 0.005;
    expect(rate2).toBeCloseTo(expectedRate2, 4);

    // Monotonic decrease across positions: D(1) > D(2) > D(5) > D(25)
    const rate5 = computeBriggsDeaminationRate(5, delta0, alpha, beta);
    const rate25 = computeBriggsDeaminationRate(25, delta0, alpha, beta);
    expect(rate1).toBeGreaterThan(rate2);
    expect(rate2).toBeGreaterThan(rate5);
    expect(rate5).toBeGreaterThan(rate25);

    // Position 25 approaches asymptotic baseline beta (analytical value)
    expect(rate25).toBeCloseTo(0.38 * Math.exp(-0.14 * 24) + 0.005, 4);
  });

  it("computes complete 25-bp MapDamage profiles for 5' C->T and 3' G->A curves", () => {
    const profile = computeMapDamageProfile(0.38, 0.14, 0.005, 25, 0.98);
    expect(profile.curve5p).toHaveLength(25);
    expect(profile.curve3p).toHaveLength(25);

    // 3' curve is scaled by 0.98 relative to 5' curve
    expect(profile.curve3p[0]).toBeCloseTo(profile.curve5p[0] * 0.98, 4);
    expect(profile.curve5p[0]).toBeCloseTo(0.385, 3);
  });

  it("computes exponential fragmentation statistics and categorizes degradation tiers", () => {
    // Severe fragmentation: lambda = 0.0446, L_min = 30
    const severe = computeExponentialFragmentation(0.0446, 30.0);
    expect(severe.meanLength).toBeCloseTo(1.0 / 0.0446 + 30.0, 1);
    expect(severe.medianLength).toBeCloseTo(Math.log(2.0) / 0.0446 + 30.0, 1);
    expect(severe.fractionBelow100).toBeGreaterThan(0.90);
    expect(severe.degradationTier).toBe("SEVERE");

    // Moderate fragmentation: lambda = 0.02, mean = 50 + 30 = 80 bp
    const moderate = computeExponentialFragmentation(0.02, 30.0);
    expect(moderate.degradationTier).toBe("MODERATE");

    // Low fragmentation: lambda = 0.012, mean = 83.3 + 30 = 113.3 bp
    const low = computeExponentialFragmentation(0.012, 30.0);
    expect(low.degradationTier).toBe("LOW");

    // Pristine modern DNA: lambda = 0.0031, mean = 322 + 30 = 352.5 bp
    const pristine = computeExponentialFragmentation(0.0031, 30.0);
    expect(pristine.degradationTier).toBe("PRISTINE");
  });

  it("evaluates modern contamination subtraction with non-negative lower bound", () => {
    // Observed delta0 = 0.38, contamination = 0.05, modern error = 0.002
    const trueDelta = subtractModernContamination(0.38, 0.05, 0.002);
    // (0.38 - 0.05 * 0.002) / 0.95 = 0.3799 / 0.95 = 0.39989
    expect(trueDelta).toBeCloseTo(0.3999, 4);
    expect(trueDelta).toBeGreaterThan(0.38);

    // Zero contamination returns observed rate exactly
    const zeroContam = subtractModernContamination(0.25, 0.0, 0.002);
    expect(zeroContam).toBeCloseTo(0.25, 6);

    // High contamination clamping
    const clamped = subtractModernContamination(0.001, 0.80, 0.002);
    expect(clamped).toBe(0.0);
  });

  it("evaluates pre-break purine excess criterion for authentic ancient DNA", () => {
    // Columbus authentic specimen: purine -1 frequency = 0.72 >= 0.70 threshold
    const pass = evaluatePurineExcess(0.72, 0.70);
    expect(pass.isAuthentic).toBe(true);
    expect(pass.zScore).toBeCloseTo((0.72 - 0.50) / 0.05, 4);

    // Modern control: purine -1 frequency = 0.50 < 0.70 threshold
    const fail = evaluatePurineExcess(0.50, 0.70);
    expect(fail.isAuthentic).toBe(false);
  });

  it("performs damage-aware SNP genotype likelihood deconvolution and compensates false heterozygotes", () => {
    // rs12913832 at position 2 (high overhang deamination): 3 damage reads out of 6 coverage
    const res = computeDamageAwareSnpLikelihood(2, 6, 3, 0.38, 0.14, 0.005);
    expect(res.postCC + res.postCT + res.postTT).toBeCloseTo(1.0, 4);
    expect(res.postCC).toBeGreaterThan(0.70);
    expect(res.compensatedCall).toBe("C/C (True Homozygote)");
    expect(res.isCompensated).toBe(true);
    expect(res.lrCompensated).toBeGreaterThan(1.0);

    // Interior position 18 with zero damage reads: authentic homozygous
    const resInterior = computeDamageAwareSnpLikelihood(18, 8, 0, 0.38, 0.14, 0.005);
    expect(resInterior.isCompensated).toBe(false);
    expect(resInterior.postCC).toBeGreaterThan(0.90);
  });

  it("evaluates multi-loci SNP catalog dynamically based on damage kinetic parameters", () => {
    // Under high deamination (Columbus delta0 = 0.38)
    const severeLoci = computeMultiLociSnpEvaluations(DEFAULT_SNP_LOCI, 0.38, 0.14, 0.005);
    expect(severeLoci).toHaveLength(6);
    const rs12913832 = severeLoci.find((l) => l.locus === "rs12913832");
    expect(rs12913832?.status).toBe("COMPENSATED");
    expect(rs12913832?.compensatedCall).toBe("C/C (True Homozygote)");

    // Under modern pristine control (delta0 = 0.002)
    const pristineLoci = computeMultiLociSnpEvaluations(DEFAULT_SNP_LOCI, 0.002, 0.01, 0.002);
    const rs12913832Pristine = pristineLoci.find((l) => l.locus === "rs12913832");
    expect(rs12913832Pristine?.status).toBe("AUTHENTIC");
    expect(rs12913832Pristine?.compensatedCall).toBe("C/T (True Heterozygote)");
  });

  it("generates deterministic 64-bit evidence hashes for blockchain chain of custody", () => {
    const hashA = computeEvidenceHash("ADNA-BENCHMARK_COLUMBUS_SKELETAL-0.38-0.0446");
    const hashB = computeEvidenceHash("ADNA-BENCHMARK_COLUMBUS_SKELETAL-0.38-0.0446");
    const hashC = computeEvidenceHash("ADNA-BENCHMARK_BRIGGS_ANCIENT-0.28-0.0549");

    expect(hashA).toBe(hashB);
    expect(hashA).not.toBe(hashC);
    expect(hashA.startsWith("0x")).toBe(true);
    expect(hashA.length).toBe(18);
  });

  // ── 2. Master Registries Integrity Tests ─────────────────────────────────

  it("verifies certified reference standards and benchmark casework presets", () => {
    expect(ADNA_PRESETS).toHaveLength(5);
    const columbus = ADNA_PRESETS.find((p) => p.id === "BENCHMARK_COLUMBUS_SKELETAL");
    expect(columbus).toBeDefined();
    expect(columbus?.delta0).toBe(0.38);
    expect(columbus?.decayAlpha).toBe(0.14);
    expect(columbus?.tier).toBe("SEVERE");

    const briggs = ADNA_PRESETS.find((p) => p.id === "BENCHMARK_BRIGGS_ANCIENT");
    expect(briggs).toBeDefined();
    expect(briggs?.delta0).toBe(0.28);

    const modern = ADNA_PRESETS.find((p) => p.id === "BENCHMARK_MODERN_CONTROL_NEGATIVE");
    expect(modern).toBeDefined();
    expect(modern?.tier).toBe("PRISTINE");
    expect(modern?.delta0).toBe(0.002);
  });

  it("verifies default 6-locus damaged SNP catalog integrity", () => {
    expect(DEFAULT_SNP_LOCI).toHaveLength(6);
    for (const item of DEFAULT_SNP_LOCI) {
      expect(item.locus.startsWith("rs")).toBe(true);
      expect(item.coverage).toBeGreaterThan(0);
      expect(item.pos).toBeGreaterThanOrEqual(1);
    }
  });

  // ── 3. Component UI & Integration Tests ──────────────────────────────────

  it("renders PanelADNA header, standards badges, and scenario presets", () => {
    render(<PanelADNA />);

    expect(screen.getByText(/Ancient & Degraded DNA Damage Kinetics|Antik & Bozulmus DNA Hasar Kinetigi/i)).toBeInTheDocument();
    expect(screen.getByText("ISFG PALEOGENOMICS")).toBeInTheDocument();
    expect(screen.getByText("MAPDAMAGE 2.0")).toBeInTheDocument();
    expect(screen.getByText("ISO 17025")).toBeInTheDocument();

    // 5 Casework preset cards
    expect(screen.getByText(/Christopher Columbus Skeletal Remains Series|Kristof Kolomb Iskelet Kalintilari/i)).toBeInTheDocument();
    expect(screen.getByText(/Briggs Ancient Bone Reference Standard|Briggs Antik Kemik Referans Standarti/i)).toBeInTheDocument();
  });

  it("allows switching between all 5 analysis tabs and updates viewport state", () => {
    render(<PanelADNA />);

    // Tab 1: Kinetics (default)
    expect(screen.getByText(/25-bp Terminal Deamination Kinetic Gradient|25-bp Terminal Deaminasyon Kinetik Gradyani/i)).toBeInTheDocument();

    // Switch to Tab 2: Fragmentation
    const tabFrag = screen.getByRole("button", {
      name: /2\. Fragment Length Decay|2\. Parca Boyutu Bozunmasi/i,
    });
    fireEvent.click(tabFrag);
    expect(screen.getByText(/Exponential Fragmentation & Sizing|Ustel Parcalanma & Boyut Dagilimi/i)).toBeInTheDocument();

    // Switch to Tab 3: SNP Likelihood
    const tabSnp = screen.getByRole("button", {
      name: /3\. Damage-Compensated SNP LR|3\. Hasar-Telafili SNP Olabilirligi/i,
    });
    fireEvent.click(tabSnp);
    expect(screen.getByText(/Damage-Compensated SNP Calling Matrix|Hasar-Telafili SNP Genotip Çağrım Kataloğu/i)).toBeInTheDocument();

    // Switch to Tab 4: Contamination
    const tabContam = screen.getByRole("button", {
      name: /4\. Contamination & Depurination|4\. Kontaminasyon & Depurinasyon/i,
    });
    fireEvent.click(tabContam);
    expect(screen.getByText(/Modern DNA Contamination Subtraction|Modern DNA Kontaminasyon Arindirma/i)).toBeInTheDocument();

    // Switch to Tab 5: Sandbox
    const tabSandbox = screen.getByRole("button", {
      name: /5\. Custom Taphonomy Sandbox|5\. Ozel Tafonomi Sandbox/i,
    });
    fireEvent.click(tabSandbox);
    expect(screen.getByText(/Taphonomic Environment|Tafonomik Çevre/i)).toBeInTheDocument();
  });

  it("updates state and metrics when switching casework scenario presets", () => {
    render(<PanelADNA />);

    // Click Modern Negative Control preset card
    const modernCard = screen.getByText(/Modern Pristine Blood Reference|Modern Bozulmamis Kan Referansi/i);
    fireEvent.click(modernCard);

    // Mean length should reflect modern baseline (350 bp)
    expect(screen.getByText(/350 bp/i)).toBeInTheDocument();
  });

  it("dispatches genuine live kinetic sweep via action button and logs audit trail", async () => {
    const addAuditLogSpy = vi.spyOn(useForensicCaseStore.getState(), "addAuditLog");
    render(<PanelADNA />);

    const execButton = screen.getByRole("button", {
      name: /Execute Kinetics|Kinetigi Calistir/i,
    });
    expect(execButton).toBeInTheDocument();
    fireEvent.click(execButton);

    // Verify audit log dispatch
    await waitFor(() => {
      expect(addAuditLogSpy).toHaveBeenCalled();
    });
    const callArgs = addAuditLogSpy.mock.calls[0][0];
    expect(callArgs.module).toBe("Ancient & Degraded DNA Damage Kinetics");
    expect(callArgs.status).toBe("PASS");
    expect(callArgs.polygonTx?.startsWith("0x")).toBe(true);
  });

  it("renders dynamic SNP Table in Tab 3 reacting to active damage parameters", () => {
    render(<PanelADNA />);

    // Switch to Tab 3
    const tabSnp = screen.getByRole("button", {
      name: /3\. Damage-Compensated SNP LR|3\. Hasar-Telafili SNP Olabilirligi/i,
    });
    fireEvent.click(tabSnp);

    // Loci count badge rendered
    expect(screen.getByText(/6 Loci Verified|6 Lokus Doğrulandı/i)).toBeInTheDocument();

    // Check specific compensated call
    expect(screen.getByText("rs12913832")).toBeInTheDocument();
    expect(screen.getAllByText(/C\/C \(True Homozygote\)/i).length).toBeGreaterThan(0);
  });

  // ── 4. Master Rule 4 Compliance (Zero Em-Dashes) ─────────────────────────

  it("strictly complies with Master Rule 4: zero em-dashes across rendered DOM and metadata", () => {
    const { container } = render(<PanelADNA />);
    const text = container.textContent || "";

    // Assert zero em-dashes (U+2014) and zero en-dashes (U+2013)
    expect(text.includes("\u2014")).toBe(false);
    expect(text.includes("\u2013")).toBe(false);

    // Verify presets descriptions
    for (const p of ADNA_PRESETS) {
      expect(p.description.includes("\u2014")).toBe(false);
      expect(p.description.includes("\u2013")).toBe(false);
      expect(p.descriptionTr.includes("\u2014")).toBe(false);
      expect(p.descriptionTr.includes("\u2013")).toBe(false);
    }
  });
});
