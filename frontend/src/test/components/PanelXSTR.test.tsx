import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import PanelXSTR, {
  computeKosambiRecombination,
  computeInverseKosambi,
  computeHaldaneRecombination,
  evaluateXStrKinshipClient,
  PRESET_COHORTS,
  LOCUS_METADATA,
  LINKAGE_GROUPS,
  TILLMAR_POPULATION_DATA,
  XSTR_POPULATION_FREQUENCIES,
} from "@/components/analysis/PanelXSTR";

describe("Subsystem 09: Argus X-12 Linkage & Kinship Engine", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── 1. Pure Mathematical & Biophysical Invariants ────────────────────────

  it("calculates Kosambi recombination fraction r from centimorgan distance d (interference model)", () => {
    expect(computeKosambiRecombination(0)).toBe(0);
    const r18_5 = computeKosambiRecombination(18.5);
    // r = 0.5 * tanh(0.37) ~= 0.1770
    expect(r18_5).toBeGreaterThan(0.17);
    expect(r18_5).toBeLessThan(0.185);

    // Extreme distance asymptote r -> 0.500
    const rLarge = computeKosambiRecombination(150.0);
    expect(rLarge).toBeGreaterThan(0.49);
    expect(rLarge).toBeLessThanOrEqual(0.50);
  });

  it("performs bijective roundtrip between Kosambi mapping and inverse Kosambi function", () => {
    const originalD = 18.5;
    const r = computeKosambiRecombination(originalD);
    const roundtripD = computeInverseKosambi(r);
    expect(Math.abs(roundtripD - originalD)).toBeLessThan(1e-4);

    expect(computeInverseKosambi(0)).toBe(0);
    const highD = computeInverseKosambi(0.499);
    expect(highD).toBeGreaterThan(80);
  });

  it("verifies Haldane recombination fraction is strictly less than or equal to Kosambi for intermediate distances", () => {
    const d = 18.5;
    const rKosambi = computeKosambiRecombination(d);
    const rHaldane = computeHaldaneRecombination(d);
    // Haldane (no interference) yields lower r than Kosambi at same d
    expect(rHaldane).toBeLessThan(rKosambi);
    expect(rHaldane).toBeGreaterThan(0.15);
    expect(computeHaldaneRecombination(0)).toBe(0);
  });

  it("evaluates GOLD VECTOR P2_02 Paternal Half-Sisters benchmark with target KI approx 1.854e5", () => {
    const goldCohort = PRESET_COHORTS[0]; // VECTOR_P2_02
    const res = evaluateXStrKinshipClient(
      goldCohort.profileA,
      goldCohort.profileB,
      goldCohort.sexA,
      goldCohort.sexB,
      goldCohort.relationship
    );

    expect(res.isExcluded).toBe(false);
    expect(res.matchingLociCount).toBe(12);
    // Combined KI should be on the order of 1.8e5
    expect(res.combinedKi).toBeGreaterThan(100000);
    expect(res.log10Ki).toBeGreaterThan(5.0);
    expect(res.verbalPredicateEn).toContain("Support for Paternal Kinship");
    expect(res.validationDetails.isMaleHemizygoteValid).toBe(true);

    // Multi-cluster product rule check: product of 4 groups equals combinedKi
    const groupProd =
      res.groupResults.LG1.ki *
      res.groupResults.LG2.ki *
      res.groupResults.LG3.ki *
      res.groupResults.LG4.ki;
    expect(Math.abs(groupProd - res.combinedKi)).toBeLessThan(1.0);
  });

  it("evaluates Father-Daughter Duo with obligate single-allele transmission and KI > 100,000", () => {
    const duo = PRESET_COHORTS[1]; // FATHER_DAUGHTER_DUO
    const res = evaluateXStrKinshipClient(
      duo.profileA,
      duo.profileB,
      duo.sexA,
      duo.sexB,
      duo.relationship
    );

    expect(res.isExcluded).toBe(false);
    expect(res.matchingLociCount).toBe(12);
    expect(res.combinedKi).toBeGreaterThan(100000);
    expect(res.verbalPredicateEn).toContain("Very Strong Support for Paternal Kinship");
    expect(res.validationDetails.isMaleHemizygoteValid).toBe(true);
  });

  it("evaluates Unrelated Non-Kin Exclusion Cohort and returns decisive exclusion KI = 0.0", () => {
    const unrel = PRESET_COHORTS[4]; // UNRELATED_EXCLUSION
    const res = evaluateXStrKinshipClient(
      unrel.profileA,
      unrel.profileB,
      unrel.sexA,
      unrel.sexB,
      unrel.relationship
    );

    expect(res.isExcluded).toBe(true);
    expect(res.combinedKi).toBe(0.0);
    expect(res.verbalPredicateEn).toContain("Decisive Support for Non-Kin Exclusion");
    expect(res.verbalPredicateTr).toContain("Kesin Dislama");
  });

  it("rejects diallelic heterozygous genotypes in hemizygous males (ISO/IEC 17025 validation guard)", () => {
    const invalidMaleProfile = {
      ...PRESET_COHORTS[1].profileA,
      DXS10148: [26.0, 28.0], // 2 alleles for 46,XY male!
    };
    const res = evaluateXStrKinshipClient(
      invalidMaleProfile,
      PRESET_COHORTS[1].profileB,
      "MALE",
      "FEMALE",
      "FATHER_DAUGHTER"
    );

    expect(res.validationDetails.isMaleHemizygoteValid).toBe(false);
    expect(res.validationDetails.rejectedLoci).toContain("Person A DXS10148");
    expect(res.isExcluded).toBe(true);
  });

  // ── 2. Component Rendering & UI Interactivity ────────────────────────────

  it("renders mission header bar with Argus X-12, Pillar 02, and ISFG 2012 / ENFSI 2017 standards", () => {
    render(<PanelXSTR />);

    expect(screen.getByText(/MODULE 09: X-STR LINKAGE/i)).toBeInTheDocument();
    expect(screen.getByText(/Pillar 02: Lineage & Kinship/i)).toBeInTheDocument();
    expect(screen.getByText(/ISFG 2012 \/ ENFSI 2017/i)).toBeInTheDocument();
    expect(screen.getByText(/Argus X-12 Linkage & Familial Kinship Engine/i)).toBeInTheDocument();
  });

  it("renders 4 Linkage Group telemetry cards (LG1 - LG4) with intra-cluster recombination rates", () => {
    render(<PanelXSTR />);

    expect(screen.getByText(/Linkage Group 1 \(Xp22.2\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Linkage Group 2 \(Xq12\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Linkage Group 3 \(Xq26\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Linkage Group 4 \(Xq28\)/i)).toBeInTheDocument();
    expect(screen.getByText(/r12=0.003/i)).toBeInTheDocument();
    expect(screen.getByText(/PROSECUTOR FALLACY SHIELD ACTIVE/i)).toBeInTheDocument();
  });

  it("switches casework presets and updates kinship evaluation telemetry cleanly", () => {
    render(<PanelXSTR />);

    // Click Unrelated Exclusion cohort button
    const unrelBtn = screen.getByText(/Unrelated Non-Kin Exclusion Cohort/i);
    fireEvent.click(unrelBtn);

    expect(screen.getByText(/EXCLUSION \(LR = 0\)/i)).toBeInTheDocument();
  });

  it("switches to Tab 2 (Argus X-12 Linkage Groups) and renders 12 loci physical and genetic map table", () => {
    render(<PanelXSTR />);

    const tab2Btn = screen.getByText(/2\. Argus X-12 Linkage Groups/i);
    fireEvent.click(tab2Btn);

    expect(screen.getByText(/Qiagen Investigator Argus X-12 Physical & Genetic Map/i)).toBeInTheDocument();
    expect(screen.getByText("DXS10148")).toBeInTheDocument();
    expect(screen.getByText("DXS10135")).toBeInTheDocument();
    expect(screen.getByText("DXS8378")).toBeInTheDocument();
    expect(screen.getByText("HPRTB")).toBeInTheDocument();
    expect(screen.getByText("DXS7423")).toBeInTheDocument();
  });

  it("switches to Tab 3 (Kosambi Recombination Studio) and allows interactive distance adjustment", () => {
    render(<PanelXSTR />);

    const tab3Btn = screen.getByText(/3\. Kosambi Recombination Studio/i);
    fireEvent.click(tab3Btn);

    expect(screen.getByText(/Kosambi Map Function & Recombination Fraction/i)).toBeInTheDocument();
    expect(screen.getByText(/Kosambi \(Interference\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Haldane \(No Interference\)/i)).toBeInTheDocument();

    // Click quick preset button
    const presetBtn = screen.getByText(/LG2 \(DXS7132 : DXS10074\): 2.5 cM/i);
    fireEvent.click(presetBtn);

    expect(screen.getByText(/d = 2.5 cM/i)).toBeInTheDocument();
  });

  it("switches to Tab 4 (Tillmar Population Frequencies) and displays genuine population diversity statistics", () => {
    render(<PanelXSTR />);

    const tab4Btn = screen.getByText(/4\. Tillmar Allele Frequencies/i);
    fireEvent.click(tab4Btn);

    expect(screen.getByText(/Tillmar et al\. \(2017\) X-STR Population Allele Frequencies/i)).toBeInTheDocument();

    // Verify Caucasian metrics for DXS10148
    const caucMetrics = TILLMAR_POPULATION_DATA.Caucasian.DXS10148;
    expect(screen.getByText(`PD_Female: ${caucMetrics.pdFemale.toFixed(3)}`)).toBeInTheDocument();

    // Switch to East Asian
    const eastAsianBtn = screen.getByRole("button", { name: "East Asian" });
    fireEvent.click(eastAsianBtn);

    const easMetrics = TILLMAR_POPULATION_DATA["East Asian"].DXS10148;
    expect(screen.getByText(`PD_Female: ${easMetrics.pdFemale.toFixed(3)}`)).toBeInTheDocument();
  });

  it("switches to Tab 5 (Interactive Sandbox), modifies alleles, and executes client-side simulation", () => {
    render(<PanelXSTR />);

    const tab5Btn = screen.getByText(/5\. Pedigree & Genotype Sandbox/i);
    fireEvent.click(tab5Btn);

    expect(screen.getByText(/Custom Kinship & Genotype Simulation Sandbox/i)).toBeInTheDocument();
    expect(screen.getByText(/Sandbox Computed Kinship Metrics/i)).toBeInTheDocument();

    // Click "Run Sandbox Evaluation"
    const runBtn = screen.getByText(/Run Sandbox Evaluation/i);
    fireEvent.click(runBtn);

    expect(screen.getByText(/KINSHIP SUPPORTED/i)).toBeInTheDocument();
  });

  it("verifies Master Rule 4 compliance with zero em-dashes and zero en-dashes in locus metadata and presets", () => {
    for (const cohort of PRESET_COHORTS) {
      expect(cohort.labelEn).not.toContain("\u2014");
      expect(cohort.labelEn).not.toContain("\u2013");
      expect(cohort.labelTr).not.toContain("\u2014");
      expect(cohort.labelTr).not.toContain("\u2013");
    }

    for (const [locus, meta] of Object.entries(LOCUS_METADATA)) {
      expect(meta.motif).not.toContain("\u2014");
      expect(meta.motif).not.toContain("\u2013");
    }
  });
});
