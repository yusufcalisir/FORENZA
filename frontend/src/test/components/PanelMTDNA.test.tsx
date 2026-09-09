import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import PanelMTDNA, {
  computeClopperPearsonBound,
  isIupacCompatible,
  normalizeVariant3Prime,
  evaluateMtdnaMaternalMatchClient,
  MTDNA_PRESETS,
  EMPOP_METAPOPULATIONS,
  IUPAC_DEGENERATE_BASES,
} from "@/components/analysis/PanelMTDNA";

describe("Subsystem 10: Mitochondrial DNA rCRS/RSRS Alignment & EMPOP Lineage Engine", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── 1. Pure Mathematical & Biophysical Invariants ────────────────────────

  it("calculates exact Clopper-Pearson 95% upper confidence bound for k=0 unobserved haplotypes", () => {
    // Exact formula: p_upper = 1 - (0.05)^(1 / (N + 1))
    const n = 48500;
    const pUpper = computeClopperPearsonBound(0, n);

    // Analytical expectation: 1 - 0.05^(1/48501) ~= 6.1764e-5
    const expected = 1.0 - Math.pow(0.05, 1.0 / (n + 1.0));
    expect(Math.abs(pUpper - expected)).toBeLessThan(1e-9);
    expect(pUpper).toBeGreaterThan(6.0e-5);
    expect(pUpper).toBeLessThan(6.3e-5);

    // Corresponding maternal LR = 1 / pUpper ~= 16,190.7
    const lr = 1.0 / pUpper;
    expect(lr).toBeGreaterThan(16000);
    expect(lr).toBeLessThan(16500);
  });

  it("calculates Clopper-Pearson 95% upper bound for observed haplotypes k > 0 and enforces monotonicity", () => {
    const n = 48200;
    const k12 = 12;
    const pUp12 = computeClopperPearsonBound(k12, n);
    expect(pUp12).toBeGreaterThan(k12 / n);
    expect(pUp12).toBeLessThan(0.001);

    const k1420 = 1420;
    const pUp1420 = computeClopperPearsonBound(k1420, n);
    expect(pUp1420).toBeGreaterThan(k1420 / n);
    expect(pUp1420).toBeGreaterThan(pUp12);
    expect(pUp1420).toBeLessThan(0.04);

    // Boundary check: N <= 0 returns 1.0
    expect(computeClopperPearsonBound(0, 0)).toBe(1.0);
  });

  it("evaluates IUPAC degenerate base code compatibility for point heteroplasmy (PHP)", () => {
    // Homoplasmic identity
    expect(isIupacCompatible("C", "C")).toBe(true);
    expect(isIupacCompatible("T", "T")).toBe(true);
    expect(isIupacCompatible("C", "T")).toBe(false);

    // Point heteroplasmy Y (C/T)
    expect(isIupacCompatible("Y", "C")).toBe(true);
    expect(isIupacCompatible("Y", "T")).toBe(true);
    expect(isIupacCompatible("C", "Y")).toBe(true);
    expect(isIupacCompatible("Y", "A")).toBe(false);
    expect(isIupacCompatible("Y", "G")).toBe(false);

    // Transition/Transversion codes R (A/G), M (A/C), K (G/T), S (G/C), W (A/T)
    expect(isIupacCompatible("R", "A")).toBe(true);
    expect(isIupacCompatible("R", "G")).toBe(true);
    expect(isIupacCompatible("R", "C")).toBe(false);
    expect(isIupacCompatible("M", "C")).toBe(true);
    expect(isIupacCompatible("K", "T")).toBe(true);
    expect(isIupacCompatible("S", "G")).toBe(true);
    expect(isIupacCompatible("W", "T")).toBe(true);

    // Degenerate N matches any base
    expect(isIupacCompatible("N", "G")).toBe(true);
    expect(isIupacCompatible("N", "C")).toBe(true);
  });

  it("normalizes indels to highest genomic position via ISFG 3'-right-alignment protocol", () => {
    // HV2 Poly-C tract: 308.1C -> 309.1C, 314.1C -> 315.1C
    expect(normalizeVariant3Prime("308.1C")).toBe("309.1C");
    expect(normalizeVariant3Prime("307.1C")).toBe("309.1C");
    expect(normalizeVariant3Prime("314.1C")).toBe("315.1C");

    // HV1 Poly-C tract: 16188.1C -> 16189.1C
    expect(normalizeVariant3Prime("16188.1C")).toBe("16189.1C");
    expect(normalizeVariant3Prime("16185.1C")).toBe("16189.1C");

    // HV3 dinucleotide: 522.1AC -> 524.1AC
    expect(normalizeVariant3Prime("522.1AC")).toBe("524.1AC");
    expect(normalizeVariant3Prime("523.1AC")).toBe("524.1AC");

    // Standard substitutions remain unchanged
    expect(normalizeVariant3Prime("263G")).toBe("263G");
    expect(normalizeVariant3Prime("16519C")).toBe("16519C");
    expect(normalizeVariant3Prime("16189Y")).toBe("16189Y");
  });

  it("verifies IUPAC heteroplasmy resolution prevents false exclusion in questioned reference pairs", () => {
    // Questioned: 16189Y (C/T) vs Reference: 16189C
    const variantsA = ["263G", "315.1C", "16189Y", "16519C"];
    const variantsB = ["263G", "315.1C", "16189C", "16519C"];

    const res = evaluateMtdnaMaternalMatchClient(variantsA, variantsB, 48500, 0, true);

    expect(res.isExclusion).toBe(false);
    expect(res.isInconclusive).toBe(false);
    expect(res.verdict).toBe("MATCH");
    expect(res.homoplasmicDiffCount).toBe(0);
    expect(res.heteroplasmicSharedCount).toBe(1);
    expect(res.sharedCalls).toContain("16189Y/16189C");
    expect(res.maternalLr).toBeGreaterThan(16000);
  });

  it("demonstrates ISFG 3'-right-shift normalizer resolves alignment discrepancies across homopolymer tracts", () => {
    // Sample A reported at 308.1C (5'-biased), Sample B at 309.1C (3'-right aligned)
    const variantsA = ["263G", "308.1C", "750G"];
    const variantsB = ["263G", "309.1C", "750G"];

    // With 3'-right shift enabled: Both normalize to 309.1C -> MATCH
    const resShifted = evaluateMtdnaMaternalMatchClient(variantsA, variantsB, 48500, 0, true);
    expect(resShifted.homoplasmicDiffCount).toBe(0);
    expect(resShifted.verdict).toBe("MATCH");

    // Without 3'-right shift: 308.1C != 309.1C -> 2 differences -> EXCLUSION
    const resRaw = evaluateMtdnaMaternalMatchClient(variantsA, variantsB, 48500, 0, false);
    expect(resRaw.homoplasmicDiffCount).toBe(2);
    expect(resRaw.verdict).toBe("EXCLUSION");
  });

  it("evaluates Benchmark LINEAGE-A European reference pair with H1 haplogroup match", () => {
    const preset = MTDNA_PRESETS[0];
    const res = evaluateMtdnaMaternalMatchClient(
      preset.variantsA,
      preset.variantsB,
      preset.databaseN,
      preset.expectedK,
      true
    );

    expect(res.isExclusion).toBe(false);
    expect(res.verdict).toBe("MATCH");
    expect(res.homoplasmicDiffCount).toBe(0);
    expect(res.sharedCalls.length).toBe(4);
    expect(res.maternalLr).toBeGreaterThanOrEqual(preset.expectedMinLr);
    expect(res.log10Lr).toBeGreaterThan(1.0);
  });

  it("evaluates Benchmark LINEAGE-B African Diaspora reference pair with 13 control region mutations", () => {
    const preset = MTDNA_PRESETS[1];
    const res = evaluateMtdnaMaternalMatchClient(
      preset.variantsA,
      preset.variantsB,
      preset.databaseN,
      preset.expectedK,
      true
    );

    expect(res.isExclusion).toBe(false);
    expect(res.verdict).toBe("MATCH");
    expect(res.homoplasmicDiffCount).toBe(0);
    expect(res.sharedCalls.length).toBe(13);
    expect(res.maternalLr).toBeGreaterThanOrEqual(preset.expectedMinLr);
    expect(res.log10Lr).toBeGreaterThan(3.0);
  });

  it("evaluates Unrelated Non-Kin Exclusion cohort and returns decisive exclusion with LR = 0.0", () => {
    const preset = MTDNA_PRESETS[4]; // COHORT_UNRELATED_EXCLUSION
    const res = evaluateMtdnaMaternalMatchClient(
      preset.variantsA,
      preset.variantsB,
      preset.databaseN,
      preset.expectedK,
      true
    );

    expect(res.isExclusion).toBe(true);
    expect(res.verdict).toBe("EXCLUSION");
    expect(res.homoplasmicDiffCount).toBeGreaterThanOrEqual(2);
    expect(res.maternalLr).toBe(0.0);
    expect(res.log10Lr).toBe(-300.0);
  });

  it("evaluates 1 homoplasmic difference as SWGDAM INCONCLUSIVE result with LR = 1.0", () => {
    const variantsA = ["263G", "315.1C", "750G", "16519C"];
    const variantsB = ["263G", "315.1C", "750G", "16519T"]; // Single transversion C -> T

    const res = evaluateMtdnaMaternalMatchClient(variantsA, variantsB, 48500, 0, true);

    expect(res.isExclusion).toBe(false);
    expect(res.isInconclusive).toBe(true);
    expect(res.verdict).toBe("INCONCLUSIVE");
    expect(res.homoplasmicDiffCount).toBe(1);
    expect(res.maternalLr).toBe(1.0);
    expect(res.log10Lr).toBe(0.0);
  });

  // ── 2. Reference Standards & Panel Registry Invariants ───────────────────

  it("validates all 5 MTDNA_PRESETS have valid biostatistical metadata and variants", () => {
    expect(MTDNA_PRESETS.length).toBe(5);

    for (const preset of MTDNA_PRESETS) {
      expect(preset.id).toBeDefined();
      expect(preset.title).toBeDefined();
      expect(preset.titleTr).toBeDefined();
      expect(preset.variantsA.length).toBeGreaterThan(0);
      expect(preset.variantsB.length).toBeGreaterThan(0);
      expect(preset.databaseN).toBeGreaterThan(10000);
      expect(preset.expectedMinLr).toBeGreaterThanOrEqual(0.0);
      expect(["MATCH", "EXCLUSION"]).toContain(preset.expectedVerdict);
    }
  });

  it("validates EMPOP_METAPOPULATIONS registry covers all 6 geographic divisions with >90,000 total samples", () => {
    expect(EMPOP_METAPOPULATIONS.length).toBe(6);

    const totalSamples = EMPOP_METAPOPULATIONS.reduce((acc, p) => acc + p.sampleSize, 0);
    expect(totalSamples).toBeGreaterThan(90000);

    const codes = EMPOP_METAPOPULATIONS.map((p) => p.code);
    expect(codes).toContain("GLOBAL");
    expect(codes).toContain("WEST_EURASIAN");
    expect(codes).toContain("EAST_ASIAN");
    expect(codes).toContain("AFRICAN");
    expect(codes).toContain("NATIVE_AMERICAN");
    expect(codes).toContain("SOUTH_ASIAN");
  });

  // ── 3. Component Rendering & Interactive Tab Verification ────────────────

  it("renders PanelMTDNA header, haplogroup badges, and telemetry cards", () => {
    render(<PanelMTDNA />);

    expect(screen.getByText(/mtDNA rCRS\/RSRS Alignment/i)).toBeInTheDocument();
    expect(screen.getByText(/ISO\/IEC 17025/i)).toBeInTheDocument();
    expect(screen.getByText(/EMPOP N=48,500/i)).toBeInTheDocument();

    // Verify presence of 5 tab buttons
    expect(screen.getByText(/1\. Pairwise Match Evaluator|1\. Ikili Eslesme/i)).toBeInTheDocument();
    expect(screen.getByText(/2\. Mitogenome & Domains|2\. Mitogenom/i)).toBeInTheDocument();
    expect(screen.getByText(/3\. EMPOP Database & Bound|3\. EMPOP Veritabani/i)).toBeInTheDocument();
    expect(screen.getByText(/4\. PhyloTree B17 Phylogeny|4\. PhyloTree B17 Filogeni/i)).toBeInTheDocument();
    expect(screen.getByText(/5\. Custom Sequence Sandbox|5\. Ozel Dizi Kumhavuzu/i)).toBeInTheDocument();
  });

  it("allows switching between all 5 analysis tabs and updates viewport state", () => {
    render(<PanelMTDNA />);

    // Tab 2: Mitogenome & Domains
    const tab2Btn = screen.getByText(/2\. Mitogenome & Domains|2\. Mitogenom/i);
    fireEvent.click(tab2Btn);
    expect(screen.getByText(/Mitochondrial Genome & Control Region|Mitokondriyal Genom/i)).toBeInTheDocument();
    expect(screen.getByText(/HV1 \(Hypervariable 1\)/i)).toBeInTheDocument();

    // Tab 3: EMPOP Database & Bound
    const tab3Btn = screen.getByText(/3\. EMPOP Database & Bound|3\. EMPOP Veritabani/i);
    fireEvent.click(tab3Btn);
    expect(screen.getByText(/EMPOP Database Frequency & Upper Bound Engine|EMPOP Veri Tabani/i)).toBeInTheDocument();
    expect(screen.getByText(/EMPOP 15 Metapopulation Reference|EMPOP 15 Metapopulasyon/i)).toBeInTheDocument();

    // Tab 4: PhyloTree B17 Phylogeny
    const tab4Btn = screen.getByText(/4\. PhyloTree B17 Phylogeny|4\. PhyloTree B17 Filogeni/i);
    fireEvent.click(tab4Btn);
    expect(screen.getByText(/PhyloTree Build 17 Mitochondrial Phylogeny Tree|PhyloTree Build 17 Mitokondriyal/i)).toBeInTheDocument();

    // Tab 5: Custom Sequence Sandbox
    const tab5Btn = screen.getByText(/5\. Custom Sequence Sandbox|5\. Ozel Dizi Kumhavuzu/i);
    fireEvent.click(tab5Btn);
    expect(screen.getByText(/Custom Sequence & IUPAC Heteroplasmy Sandbox|Ozel Dizi & IUPAC Heteroplazmi/i)).toBeInTheDocument();
  });

  it("executes custom sequence sandbox and evaluates live point heteroplasmy and 3'-right shift", () => {
    render(<PanelMTDNA />);

    // Switch to Sandbox tab
    const sandboxTab = screen.getByText(/5\. Custom Sequence Sandbox|5\. Ozel Dizi Kumhavuzu/i);
    fireEvent.click(sandboxTab);

    // Initial state has 16189Y vs 16189C which should yield MATCH / INCLUSION
    expect(screen.getByText(/MATCH \/ INCLUSION|DAHIL ETME \/ ESLESME/i)).toBeInTheDocument();
    expect(screen.getByText(/Live Sandbox Evaluation Results|Canli Kumhavuzu Degerlendirme/i)).toBeInTheDocument();

    // Find textareas for Questioned Sample A and Reference Sample B
    const textareas = screen.getAllByRole("textbox");
    expect(textareas.length).toBe(2);

    // Enter 2 homoplasmic non-matching mutations into Sample A & B
    fireEvent.change(textareas[0], { target: { value: "263G, 750G, 16051G, 16129A" } });
    fireEvent.change(textareas[1], { target: { value: "263G, 750G, 16051C, 16129C" } });

    // Should immediately recalculate to DEFINITIVE EXCLUSION
    expect(screen.getByText(/DEFINITIVE EXCLUSION|KESIN DISLAMA/i)).toBeInTheDocument();
  });

  // ── 4. Master Rule 4 Compliance (Zero Em-Dashes) ─────────────────────────

  it("strictly complies with Master Rule 4: zero em-dashes across rendered DOM and metadata", () => {
    const { container } = render(<PanelMTDNA />);
    const text = container.textContent || "";

    // Test for em-dash (U+2014) and en-dash (U+2013)
    expect(text.includes("\u2014")).toBe(false);
    expect(text.includes("\u2013")).toBe(false);

    // Also check preset titles and descriptions
    for (const p of MTDNA_PRESETS) {
      expect(p.title.includes("\u2014")).toBe(false);
      expect(p.title.includes("\u2013")).toBe(false);
      expect(p.description.includes("\u2014")).toBe(false);
      expect(p.description.includes("\u2013")).toBe(false);
    }
  });
});
