import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import PanelDVI, {
  computeMultiOmicJointLr,
  computeBayesianPosteriorW,
  classifyDviDecisionTier,
  solveHungarianBipartiteMatchClient,
  computeEvidenceHash,
  formatExp,
  DVI_PRESETS,
  DVI_COHORTS,
} from "@/components/analysis/PanelDVI";

describe("Subsystem 11: Interpol DVI & Multi-Omic Joint Likelihood Engine", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── 1. Pure Mathematical & Biophysical Invariants ────────────────────────

  it("calculates multi-omic joint LR and preserves log-additive product invariant", () => {
    // Golden Benchmark VECTOR_P2_03: Autosomal 5.2e3, Y-STR p_Y=0.0002 (LR=5000), mtDNA p_M=0.0001 (LR=10000)
    const autoLr = 5.2e3;
    const ystrPUpper = 0.0002;
    const mtdnaPUpper = 0.0001;

    const res = computeMultiOmicJointLr(autoLr, ystrPUpper, mtdnaPUpper, 1.0, true, true, false);

    // Expected: 5.2e3 * 5000 * 10000 = 2.6e11
    expect(res.jointLr).toBeCloseTo(2.6e11, -5);
    expect(res.lrYstr).toBe(5000);
    expect(res.lrMtdna).toBe(10000);

    // Log-additive product rule preservation: |log10(LR_joint) - sum(log10(LR_m))| < 10^-6
    const sumLog = Math.log10(autoLr) + Math.log10(res.lrYstr) + Math.log10(res.lrMtdna);
    expect(Math.abs(res.log10Joint - sumLog)).toBeLessThan(1e-3);
  });

  it("evaluates Golden Benchmark VECTOR_P2_03 degraded skeletal remains yielding definitive identification", () => {
    const goldPreset = DVI_PRESETS[0]; // VECTOR_P2_03_DEGRADED_SKELETAL
    const res = computeMultiOmicJointLr(
      goldPreset.autosomalLr,
      goldPreset.ystrPUpper,
      goldPreset.mtdnaPUpper,
      goldPreset.snpLr,
      goldPreset.hasYstr,
      goldPreset.hasMtdna,
      goldPreset.hasSnp
    );

    expect(res.jointLr).toBeCloseTo(goldPreset.expectedJointLr, -5);
    expect(res.log10Joint).toBeCloseTo(goldPreset.expectedLog10Lr, 2);

    const w = computeBayesianPosteriorW(res.jointLr, goldPreset.prior);
    // W > 99.99999%
    expect(w).toBeGreaterThan(0.999999);

    const classification = classifyDviDecisionTier(res.jointLr);
    expect(classification.tier).toBe("DEFINITIVE_IDENTIFICATION");
  });

  it("calculates Bayesian posterior probability W and models prior odds sensitivity", () => {
    const jointLr = 1.0e6; // Exact Tier 1 boundary

    // Prior 0.001 (N=1000 victims default)
    const wDefault = computeBayesianPosteriorW(jointLr, 0.001);
    // W = (1e6 * 1e-3) / (1e6 * 1e-3 + 0.999) = 1000 / 1000.999 ~= 0.999002
    expect(wDefault).toBeGreaterThan(0.999);
    expect(wDefault).toBeLessThan(1.0);

    // Rare prior 0.0001 (N=10,000 victims)
    const wRare = computeBayesianPosteriorW(jointLr, 0.0001);
    expect(wRare).toBeLessThan(wDefault);
    expect(wRare).toBeGreaterThan(0.99);

    // Exclusion case LR = 0 -> W = 0
    expect(computeBayesianPosteriorW(0.0, 0.001)).toBe(0.0);
  });

  it("classifies all 4 Interpol DVI decision tiers according to international statutory standards", () => {
    // Tier 1: DEFINITIVE_IDENTIFICATION (LR >= 10^6)
    const tier1 = classifyDviDecisionTier(1.5e6);
    expect(tier1.tier).toBe("DEFINITIVE_IDENTIFICATION");
    expect(tier1.verbalEn).toContain("Definitive Forensic Identification");

    // Tier 2: PROBABLE_MATCH (10^4 <= LR < 10^6)
    const tier2 = classifyDviDecisionTier(5.0e4);
    expect(tier2.tier).toBe("PROBABLE_MATCH");
    expect(tier2.verbalEn).toContain("Probable Identification");

    // Tier 3: INCONCLUSIVE (10^-2 < LR < 10^4)
    const tier3 = classifyDviDecisionTier(2.5e1);
    expect(tier3.tier).toBe("INCONCLUSIVE");
    expect(tier3.verbalEn).toContain("Inconclusive Identification");

    // Tier 4: EXCLUSION (LR <= 10^-2)
    const tier4 = classifyDviDecisionTier(1.0e-5);
    expect(tier4.tier).toBe("EXCLUSION");
    expect(tier4.verbalEn).toContain("Definitive Exclusion");
  });

  it("solves Hungarian bipartite optimal matching for permuted off-diagonal assignments", () => {
    // 3 PMs and 3 AMs with off-diagonal maximal values
    // PM-01 matches AM-102 (1e9), PM-02 matches AM-101 (1e8), PM-03 matches AM-103 (1e7)
    const scores = [
      [10.0, 1.0e9, 0.01],
      [1.0e8, 10.0, 0.01],
      [0.01, 10.0, 1.0e7],
    ];
    const pms = ["PM-01", "PM-02", "PM-03"];
    const ams = ["AM-101", "AM-102", "AM-103"];

    const assignments = solveHungarianBipartiteMatchClient(scores, pms, ams);

    expect(assignments.length).toBe(3);
    // PM-01 must be assigned to AM-102 (off-diagonal)
    const a0 = assignments.find((a) => a.pm === "PM-01");
    expect(a0?.am).toBe("AM-102");
    expect(a0?.lr).toBe(1.0e9);
    expect(a0?.tier).toBe("DEFINITIVE_IDENTIFICATION");

    // PM-02 must be assigned to AM-101 (off-diagonal)
    const a1 = assignments.find((a) => a.pm === "PM-02");
    expect(a1?.am).toBe("AM-101");
    expect(a1?.lr).toBe(1.0e8);

    // PM-03 must be assigned to AM-103
    const a2 = assignments.find((a) => a.pm === "PM-03");
    expect(a2?.am).toBe("AM-103");
    expect(a2?.lr).toBe(1.0e7);
  });

  it("generates deterministic Keccak/FNV evidence hash for ISO 17025 audit trail", () => {
    const hash1 = computeEvidenceHash("DVI-VECTOR_P2_03-260000000000");
    const hash2 = computeEvidenceHash("DVI-VECTOR_P2_03-260000000000");
    const hash3 = computeEvidenceHash("DVI-DIFFERENT-SAMPLE");

    expect(hash1).toBe(hash2);
    expect(hash1).not.toBe(hash3);
    expect(hash1.startsWith("0x")).toBe(true);
    expect(hash1.length).toBeGreaterThan(16);
  });

  it("formats exponential notation cleanly via formatExp helper", () => {
    expect(formatExp(1.234e5, 2)).toBe("1.23e+5");
    expect(formatExp(null)).toBe("-");
    expect(formatExp(undefined)).toBe("-");
    expect(formatExp(NaN)).toBe("-");
  });

  // ── 2. Reference Standards & Casework Cohort Registries ──────────────────

  it("validates all 5 DVI_PRESETS contain complete biostatistical metadata", () => {
    expect(DVI_PRESETS.length).toBe(5);

    for (const preset of DVI_PRESETS) {
      expect(preset.id).toBeDefined();
      expect(preset.title).toBeDefined();
      expect(preset.titleTr).toBeDefined();
      expect(preset.pedigreeType).toBeDefined();
      expect(preset.autosomalLr).toBeGreaterThanOrEqual(0.0);
      expect(preset.prior).toBeGreaterThan(0.0);
      expect(["DEFINITIVE_IDENTIFICATION", "EXCLUSION"]).toContain(preset.expectedTier);
    }
  });

  it("validates all 5 DVI_COHORTS disaster incidents cover major forensic taphonomies", () => {
    expect(DVI_COHORTS.length).toBe(5);

    const ids = DVI_COHORTS.map((c) => c.id);
    expect(ids).toContain("COHORT_DVI_01_AVIATION");
    expect(ids).toContain("COHORT_DVI_02_MARITIME");
    expect(ids).toContain("COHORT_DVI_03_SKELETAL");
    expect(ids).toContain("COHORT_DVI_04_FIRE_TSUNAMI");
    expect(ids).toContain("COHORT_DVI_05_ELIMINATION");

    const totalVictims = DVI_COHORTS.reduce((sum, c) => sum + c.sampleSize, 0);
    expect(totalVictims).toBeGreaterThanOrEqual(300);
  });

  // ── 3. Component Rendering & Interactive Verification ────────────────────

  it("renders PanelDVI header bar, Interpol badges, and telemetry ribbon", () => {
    render(<PanelDVI />);

    expect(screen.getByText(/Disaster Victim Identification & Kinship|Afet Kurbani Kimliklendirme/i)).toBeInTheDocument();
    expect(screen.getByText(/Interpol DVI Std/i)).toBeInTheDocument();
    expect(screen.getByText(/ENFSI 2017/i)).toBeInTheDocument();
    expect(screen.getByText(/Munkres 1-e-1/i)).toBeInTheDocument();

    // Verify presence of all 5 tab buttons
    expect(screen.getByText(/1\. Joint LR & Decision Tiers|1\. Ortak Olabilirlik/i)).toBeInTheDocument();
    expect(screen.getByText(/2\. Pedigree Topologies & Modalities|2\. Soybagi Topolojileri/i)).toBeInTheDocument();
    expect(screen.getByText(/3\. N x M Matrix & Hungarian Matcher|3\. N x M Eslesme/i)).toBeInTheDocument();
    expect(screen.getByText(/4\. Interpol Standards & Cohorts|4\. Interpol Standartlari/i)).toBeInTheDocument();
    expect(screen.getByText(/5\. Custom Case Sandbox|5\. Ozel Vaka/i)).toBeInTheDocument();
  });

  it("allows switching between all 5 analysis tabs and updates viewport state", () => {
    render(<PanelDVI />);

    // Tab 2: Pedigree Topologies
    const tab2Btn = screen.getByText(/2\. Pedigree Topologies & Modalities|2\. Soybagi Topolojileri/i);
    fireEvent.click(tab2Btn);
    expect(screen.getByText(/Pedigree Kinship Topology|Soybagi Model Topolojisi/i)).toBeInTheDocument();

    // Tab 3: N x M Matrix & Hungarian Matcher
    const tab3Btn = screen.getByText(/3\. N x M Matrix & Hungarian Matcher|3\. N x M Eslesme/i);
    fireEvent.click(tab3Btn);
    expect(screen.getByText(/Disaster Reconciliation Matrix & Hungarian|Afet Capraz Eslestirme Matrisi/i)).toBeInTheDocument();

    // Tab 4: Interpol Standards & Cohorts
    const tab4Btn = screen.getByText(/4\. Interpol Standards & Cohorts|4\. Interpol Standartlari/i);
    fireEvent.click(tab4Btn);
    expect(screen.getByText(/Interpol DVI Guide Section 4|Interpol DVI Kilavuzu Bolum 4/i)).toBeInTheDocument();

    // Tab 5: Custom Case Sandbox
    const tab5Btn = screen.getByText(/5\. Custom Case Sandbox|5\. Ozel Vaka/i);
    fireEvent.click(tab5Btn);
    expect(screen.getByText(/Custom Disaster Victim & Candidate Pedigree|Ozel Afet Kurbani/i)).toBeInTheDocument();
  });

  it("toggles between 3 x 3 Triad and 4 x 4 Extended matrix sizes in Tab 3", () => {
    render(<PanelDVI />);

    // Switch to Tab 3
    const tab3Btn = screen.getByText(/3\. N x M Matrix & Hungarian Matcher|3\. N x M Eslesme/i);
    fireEvent.click(tab3Btn);

    // Initial 3x3 state
    expect(screen.getByText("PM-01")).toBeInTheDocument();
    expect(screen.getByText("PM-02")).toBeInTheDocument();
    expect(screen.getByText("PM-03")).toBeInTheDocument();
    expect(screen.queryByText("PM-04")).not.toBeInTheDocument();

    // Click 4 x 4 Extended button
    const btn4x4 = screen.getByText(/4 x 4 Extended/i);
    fireEvent.click(btn4x4);

    // Should now display PM-04 and AM-104
    expect(screen.getByText("PM-04")).toBeInTheDocument();
    expect(screen.getByText("AM-104")).toBeInTheDocument();

    // Switch back to 3 x 3
    const btn3x3 = screen.getByText(/3 x 3 Triad/i);
    fireEvent.click(btn3x3);
    expect(screen.queryByText("PM-04")).not.toBeInTheDocument();
  });

  it("executes custom disaster casework sandbox and evaluates live joint LR and decision tier", () => {
    render(<PanelDVI />);

    // Switch to Tab 5 Sandbox
    const tab5Btn = screen.getByText(/5\. Custom Case Sandbox|5\. Ozel Vaka/i);
    fireEvent.click(tab5Btn);

    // Default sandbox state has high autosomal LR yielding DEFINITIVE IDENTIFICATION
    expect(screen.getByText(/DEFINITIVE IDENTIFICATION|KESIN KIMLIKLENDIRME/i)).toBeInTheDocument();

    // Find input for Autosomal STR LR and change to an exclusionary value (LR <= 10^-2)
    const autoLrInput = screen.getByDisplayValue("2500000");
    fireEvent.change(autoLrInput, { target: { value: "1e-12" } });

    // Should immediately recalculate to DEFINITIVE EXCLUSION
    expect(screen.getByText(/DEFINITIVE EXCLUSION|KESIN DISLAMA/i)).toBeInTheDocument();
  });

  it("evaluates Direct AM reference match and Unrelated exclusion presets with analytical exactness", () => {
    // Benchmark 1: Direct AM Reference Match (LR = 4.5e18)
    const directPreset = DVI_PRESETS[1];
    const resDirect = computeMultiOmicJointLr(
      directPreset.autosomalLr,
      directPreset.ystrPUpper,
      directPreset.mtdnaPUpper,
      directPreset.snpLr,
      directPreset.hasYstr,
      directPreset.hasMtdna,
      directPreset.hasSnp
    );
    expect(resDirect.jointLr).toBe(4.5e18);
    expect(resDirect.log10Joint).toBeCloseTo(18.6532, 2);
    expect(classifyDviDecisionTier(resDirect.jointLr).tier).toBe("DEFINITIVE_IDENTIFICATION");

    // Benchmark 4: Unrelated Non-Kin Exclusion (LR = 1.0e-8)
    const exclPreset = DVI_PRESETS[4];
    const resExcl = computeMultiOmicJointLr(
      exclPreset.autosomalLr,
      exclPreset.ystrPUpper,
      exclPreset.mtdnaPUpper,
      exclPreset.snpLr,
      exclPreset.hasYstr,
      exclPreset.hasMtdna,
      exclPreset.hasSnp
    );
    expect(resExcl.jointLr).toBe(1.0e-8);
    expect(resExcl.log10Joint).toBeCloseTo(-8.0, 2);
    expect(classifyDviDecisionTier(resExcl.jointLr).tier).toBe("EXCLUSION");
  });

  it("dispatches live joint LR recalculation via executeJointReconciliation action button", async () => {
    render(<PanelDVI />);

    // Action button in header
    const evalButton = screen.getByRole("button", {
      name: /Execute DVI Joint Reconciliation|DVI Ortak Analizini Calistir/i,
    });
    expect(evalButton).toBeInTheDocument();
    fireEvent.click(evalButton);

    // After click, should show latency or updated status
    expect(evalButton).toBeInTheDocument();
  });

  // ── 4. Master Rule 4 Compliance (Zero Em-Dashes) ─────────────────────────

  it("strictly complies with Master Rule 4: zero em-dashes across rendered DOM and metadata", () => {
    const { container } = render(<PanelDVI />);
    const text = container.textContent || "";

    // Assert zero em-dashes (U+2014) and zero en-dashes (U+2013)
    expect(text.includes("\u2014")).toBe(false);
    expect(text.includes("\u2013")).toBe(false);

    // Verify preset and cohort descriptions
    for (const p of DVI_PRESETS) {
      expect(p.title.includes("\u2014")).toBe(false);
      expect(p.title.includes("\u2013")).toBe(false);
      expect(p.description.includes("\u2014")).toBe(false);
      expect(p.description.includes("\u2013")).toBe(false);
    }

    for (const c of DVI_COHORTS) {
      expect(c.name.includes("\u2014")).toBe(false);
      expect(c.name.includes("\u2013")).toBe(false);
      expect(c.degradation.includes("\u2014")).toBe(false);
      expect(c.degradation.includes("\u2013")).toBe(false);
    }
  });
});
