import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PanelFGG, {
  computeKinshipPhi,
  computeWrightR,
  computeKingPhi,
  computeDiscountedSharedCm,
  filterQualifyingSegments,
  computeTotalSharedCm,
  classifyRelationshipBySharedCm,
  evaluateLegalCompliance,
  generateSampleDestructionCertificate,
  computeEvidenceHash,
  AUTOSOME_MAP_LENGTHS,
  FGG_PRESETS,
  RELATIONSHIP_PRIOR_RANGES,
} from "@/components/analysis/PanelFGG";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

describe("Subsystem 13: Forensic Genetic Genealogy (FGG / IGG) & Bonsai Pedigree Studio", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── 1. Pure Biocomputational & Kinship Mathematical Invariants ───────────

  it("calculates exact Cotterman kinship coefficient Phi = k1 / 4 + k2 / 2 across relationship classes", () => {
    // Parent-Child: k0 = 0, k1 = 1, k2 = 0 => Phi = 0.25
    expect(computeKinshipPhi(0.0, 1.0, 0.0)).toBeCloseTo(0.25, 6);

    // Full Sibling: k0 = 0.25, k1 = 0.5, k2 = 0.25 => Phi = 0.125 + 0.125 = 0.25
    expect(computeKinshipPhi(0.25, 0.5, 0.25)).toBeCloseTo(0.25, 6);

    // Half Sibling / Avuncular: k0 = 0.5, k1 = 0.5, k2 = 0 => Phi = 0.125
    expect(computeKinshipPhi(0.5, 0.5, 0.0)).toBeCloseTo(0.125, 6);

    // Monozygotic Twins / Self: k0 = 0, k1 = 0, k2 = 1 => Phi = 0.5
    expect(computeKinshipPhi(0.0, 0.0, 1.0)).toBeCloseTo(0.5, 6);

    // Unrelated: k0 = 1, k1 = 0, k2 = 0 => Phi = 0.0
    expect(computeKinshipPhi(1.0, 0.0, 0.0)).toBeCloseTo(0.0, 6);
  });

  it("computes Wright coefficient of relationship r = 2 * Phi with non-negativity bound", () => {
    // Parent-Child: Phi = 0.25 => r = 0.5
    expect(computeWrightR(0.25)).toBeCloseTo(0.5, 6);

    // Monozygotic Twins: Phi = 0.5 => r = 1.0
    expect(computeWrightR(0.5)).toBeCloseTo(1.0, 6);

    // 1st Cousin: Phi = 0.0625 => r = 0.125
    expect(computeWrightR(0.0625)).toBeCloseTo(0.125, 6);

    // 3rd Cousin: Phi = 0.00390625 => r = 0.0078125
    expect(computeWrightR(0.00390625)).toBeCloseTo(0.0078125, 6);

    // Unrelated: Phi = 0 => r = 0
    expect(computeWrightR(0.0)).toBeCloseTo(0.0, 6);
  });

  it("computes KING-robust kinship coefficient with non-negative bounds and zero-denominator guard", () => {
    // Concordant parent-child: nAaAa=500, nAAaa=0, nAa1=1000, nAa2=1000, nTotal=10000
    const phi = computeKingPhi(500, 0, 1000, 1000, 10000);
    expect(phi).toBeGreaterThan(0.2);
    expect(phi).toBeLessThanOrEqual(0.5);

    // Discordant / unrelated: nAAaa = 500, nAaAa = 0
    const phiUnrelated = computeKingPhi(0, 500, 1000, 1000, 10000);
    expect(phiUnrelated).toBeLessThanOrEqual(0.0);

    // Zero-denominator fallback
    expect(computeKingPhi(0, 0, 0, 0, 0)).toBe(0.0);
  });

  it("discounts shared cM under elevated background homozygosity (F_ROH) to mitigate false-close cousin calls", () => {
    const rawCm = 1000.0;

    // Normal baseline population (F_ROH <= 0.02) => no discounting
    expect(computeDiscountedSharedCm(rawCm, 0.015)).toBe(rawCm);
    expect(computeDiscountedSharedCm(rawCm, 0.02)).toBe(rawCm);

    // Elevated endogamy (Ashkenazi / Amish: F_ROH = 0.05)
    // Factor = 1.0 - 4.5 * 0.05 = 0.775 => 775 cM
    const discounted = computeDiscountedSharedCm(rawCm, 0.05);
    expect(discounted).toBeCloseTo(775.0, 2);
    expect(discounted).toBeLessThan(rawCm);

    // Extreme inbreeding clamp floor (kappa * rawCm = 0.40 * rawCm = 400 cM)
    const severeDiscounted = computeDiscountedSharedCm(rawCm, 0.16);
    expect(severeDiscounted).toBeCloseTo(400.0, 2);
  });

  it("filters IBD segments below Centimorgan (L_min) and SNP count thresholds", () => {
    const testSegments = [
      { chr: "1", startBp: 100, endBp: 200, startCm: 0, endCm: 15.0, lengthCm: 15.0, snpCount: 800, type: "IBD1" as const },
      { chr: "2", startBp: 100, endBp: 200, startCm: 0, endCm: 5.5, lengthCm: 5.5, snpCount: 600, type: "IBD1" as const }, // Below 7 cM
      { chr: "3", startBp: 100, endBp: 200, startCm: 0, endCm: 12.0, lengthCm: 12.0, snpCount: 300, type: "IBD1" as const }, // Below 500 SNPs
      { chr: "4", startBp: 100, endBp: 200, startCm: 0, endCm: 25.0, lengthCm: 25.0, snpCount: 1500, type: "IBD1" as const },
    ];

    const qualified = filterQualifyingSegments(testSegments, 7.0, 500);
    expect(qualified.length).toBe(2);
    expect(qualified.map((s) => s.chr)).toEqual(["1", "4"]);
  });

  it("correctly computes total shared cM with zero-length edge case handling", () => {
    const segments = [
      { chr: "1", startBp: 0, endBp: 0, startCm: 0, endCm: 51.5, lengthCm: 51.5, snpCount: 2000, type: "IBD1" as const },
      { chr: "5", startBp: 0, endBp: 0, startCm: 0, endCm: 24.8, lengthCm: 24.8, snpCount: 1200, type: "IBD1" as const },
      { chr: "9", startBp: 0, endBp: 0, startCm: 0, endCm: 14.2, lengthCm: 14.2, snpCount: 800, type: "IBD1" as const },
    ];

    expect(computeTotalSharedCm(segments)).toBeCloseTo(90.5, 6);
    expect(computeTotalSharedCm([])).toBe(0.0);
  });

  // ── 2. Shared cM Kinship Classification & Gaussian Priors ────────────────

  it("classifies 1st-degree parent-child with full genome IBD1 transmission", () => {
    const candidates = classifyRelationshipBySharedCm(3450.0, true);
    expect(candidates.length).toBe(8);

    const top = candidates.find((c) => c.degree === "DEGREE_1_PARENT_CHILD");
    expect(top).toBeDefined();
    expect(top!.probability).toBeGreaterThan(0.99);
  });

  it("classifies 3rd cousin (GSK casework ~90.5 cM) with highest likelihood in 6th degree", () => {
    const candidates = classifyRelationshipBySharedCm(90.5, false);
    const sorted = [...candidates].sort((a, b) => b.probability - a.probability);

    // Top candidate must be 3rd Cousin (DEGREE_6_THIRD_COUSIN) ~83-84%
    expect(sorted[0].degree).toBe("DEGREE_6_THIRD_COUSIN");
    expect(sorted[0].probability).toBeGreaterThan(0.80);

    // Second candidate must be 2nd Cousin (DEGREE_5_SECOND_COUSIN) ~16%
    expect(sorted[1].degree).toBe("DEGREE_5_SECOND_COUSIN");
    expect(sorted[1].probability).toBeGreaterThan(0.10);

    // Distant or Parent-Child should be zero or negligible
    const pc = candidates.find((c) => c.degree === "DEGREE_1_PARENT_CHILD");
    expect(pc!.probability).toBe(0.0);
  });

  it("identifies distant or unrelated profiles when total cM is below 15 cM threshold", () => {
    const candidates = classifyRelationshipBySharedCm(8.0, false);
    const sorted = [...candidates].sort((a, b) => b.probability - a.probability);

    expect(sorted[0].degree).toBe("DEGREE_7_DISTANT");
    expect(sorted[0].probability).toBeGreaterThan(0.95);
  });

  // ── 3. Legal Governance & Sample Destruction Protocols ───────────────────

  it("evaluates statutory legal compliance across DOJ 2019 and Maryland Title 17 standards", () => {
    // Fully compliant homicide with CODIS exhausted
    const compliant = evaluateLegalCompliance("MARYLAND_TITLE_17", "HOMICIDE", true, true);
    expect(compliant.isCompliant).toBe(true);
    expect(compliant.violationReasons.length).toBe(0);
    expect(compliant.leadDisclaimerNotice).toContain("INVESTIGATIVE LEADS ONLY");

    // Non-exhausted CODIS violation
    const nonExhausted = evaluateLegalCompliance("MARYLAND_TITLE_17", "HOMICIDE", false, true);
    expect(nonExhausted.isCompliant).toBe(false);
    expect(nonExhausted.violationReasons.some((r) => r.includes("CODIS"))).toBe(true);

    // Disallowed petty offense violation
    const pettyCrime = evaluateLegalCompliance("US_DOJ_INTERIM_2019", "PETTY_LARCENY", true, true);
    expect(pettyCrime.isCompliant).toBe(false);
    expect(pettyCrime.violationReasons.some((r) => r.includes("Qualifying offense"))).toBe(true);
  });

  it("generates deterministic sample destruction certificate with Maryland Title 17 citation and SHA-256 seal", () => {
    const cert = generateSampleDestructionCertificate(
      "CASE_2026_COLD_FGG",
      ["MATCH_3RD_COUSIN", "REF_CONSENT_02"],
      "MARYLAND_TITLE_17",
      "Det. K. Vance (FGG-49102)"
    );

    expect(cert.orderId).toMatch(/^DEST_/);
    expect(cert.samplesToDestroy).toEqual(["MATCH_3RD_COUSIN", "REF_CONSENT_02"]);
    expect(cert.status).toBe("SCHEDULED_FOR_INCINERATION");
    expect(cert.statute).toContain("Maryland Title 17");
    expect(cert.certificateHash.length).toBe(64);
    expect(cert.certificateHash).toMatch(/^[0-9a-f]{64}$/);
  });

  it("computes deterministic FNV-1a hex digests for blockchain/audit verification", () => {
    const hash1 = computeEvidenceHash("FGG-VECTOR_01-7-0.012");
    const hash2 = computeEvidenceHash("FGG-VECTOR_01-7-0.012");
    const hash3 = computeEvidenceHash("FGG-VECTOR_02-7-0.052");

    expect(hash1).toBe(hash2);
    expect(hash1).not.toBe(hash3);
    expect(hash1.startsWith("0x")).toBe(true);
  });

  it("validates 22-autosome genetic map registry and casework golden presets", () => {
    // 22 autosomes must be present
    expect(Object.keys(AUTOSOME_MAP_LENGTHS).length).toBe(22);
    expect(AUTOSOME_MAP_LENGTHS["1"]).toBeCloseTo(286.3, 1);
    expect(AUTOSOME_MAP_LENGTHS["21"]).toBeCloseTo(62.8, 1);

    // 3 Golden Vector presets must be registered
    expect(FGG_PRESETS.length).toBe(3);
    expect(FGG_PRESETS.map((p) => p.id)).toEqual(["VECTOR_01", "VECTOR_02", "VECTOR_03"]);

    // Prior ranges must cover 8 categories
    expect(RELATIONSHIP_PRIOR_RANGES.length).toBe(8);
  });

  // ── 4. UI Component Rendering, Tab Switching & Benchmarks ────────────────

  it("renders mission header, tactical badges, and all 3 casework benchmark cards", () => {
    render(<PanelFGG />);

    // Header and badges
    expect(screen.getByText(/Adli Genetik Soybilim & Akrabalik Cozucusu|Forensic Genetic Genealogy & Bonsai Pedigree/i)).toBeInTheDocument();
    expect(screen.getByText("FGG / IGG ENGINE")).toBeInTheDocument();
    expect(screen.getByText("BONSAI DAG SOLVER")).toBeInTheDocument();
    expect(screen.getByText("ISO 17025")).toBeInTheDocument();

    // 3 Casework benchmark cards
    expect(screen.getByText(/NA12878/i)).toBeInTheDocument();
    expect(screen.getByText(/GIAB Askenaz|GIAB Ashkenazi/i)).toBeInTheDocument();
    expect(screen.getByText(/Golden State Killer/i)).toBeInTheDocument();

    // 5 Tab navigation buttons
    expect(screen.getByText(/1\. Altin Standartlar|1\. Golden Benchmarks/i)).toBeInTheDocument();
    expect(screen.getByText(/2\. Tum Genom IBD|2\. Whole-Genome IBD/i)).toBeInTheDocument();
    expect(screen.getByText(/3\. Akrabalik & Endogami|3\. Kinship & Endogamy/i)).toBeInTheDocument();
    expect(screen.getByText(/4\. Bonsai Soyağacı|4\. Bonsai Pedigree DAG/i)).toBeInTheDocument();
    expect(screen.getByText(/5\. Yasal Mevzuat|5\. Legal Governance/i)).toBeInTheDocument();
  });

  it("switches casework benchmark to Golden State Killer (GSK) and updates active metrics", () => {
    render(<PanelFGG />);

    const gskCard = screen.getByText(/Golden State Killer/i);
    fireEvent.click(gskCard);

    // Verify GSK details
    expect(screen.getByText("GSK_CRIME_SCENE_1978")).toBeInTheDocument();
    expect(screen.getByText("GSK_MATCH_3RD_COUSIN")).toBeInTheDocument();
    expect(screen.getByText(/3rd Cousin \(3C\) \/ 2C1R|3\. Derece Kuzen/i)).toBeInTheDocument();
  });

  it("navigates cleanly across all 5 forensic tabs and verifies contextual content", () => {
    render(<PanelFGG />);

    // Tab 2: Whole-Genome IBD Karyotype Map
    const tab2 = screen.getByText(/2\. Tum Genom IBD|2\. Whole-Genome IBD/i);
    fireEvent.click(tab2);
    expect(screen.getByText(/22-Otozom Tum Genom IBD Ideogrami|22-Autosome Whole-Genome IBD Ideogram/i)).toBeInTheDocument();
    expect(screen.getByText(/IBD1 \(Half-Identical\)/i)).toBeInTheDocument();

    // Tab 3: Kinship & Endogamy
    const tab3 = screen.getByText(/3\. Akrabalik & Endogami|3\. Kinship & Endogamy/i);
    fireEvent.click(tab3);
    expect(screen.getByText(/Shared cM Project Akrabalik Olasilik Dagilimi|Shared cM Project Likelihood Distribution/i)).toBeInTheDocument();
    expect(screen.getByText(/Endogami & F_ROH Indirimi|Endogamy & F_ROH Discounting/i)).toBeInTheDocument();

    // Tab 4: Bonsai Pedigree DAG
    const tab4 = screen.getByText(/4\. Bonsai Soyağacı|4\. Bonsai Pedigree DAG/i);
    fireEvent.click(tab4);
    expect(screen.getByText(/Bonsai Composite Pedigree|Bonsai Kompozit Soy Agaci/i)).toBeInTheDocument();

    // Tab 5: Legal Governance & Destruction
    const tab5 = screen.getByText(/5\. Yasal Mevzuat|5\. Legal Governance/i);
    fireEvent.click(tab5);
    expect(screen.getByText(/Yasal Uyum & Adli Surec Guvenceleri|Statutory Governance & Compliance Gates/i)).toBeInTheDocument();
    expect(screen.getByText(/Numune Imha Emri|Sample Destruction/i)).toBeInTheDocument();
  });

  // ── 5. End-to-End Live Actions & Audit Log Verifications ──────────────────

  it("executes FGG analysis and dispatches audit log to forensic store; generates sample destruction order", async () => {
    render(<PanelFGG />);

    // Click Run FGG Analysis button
    const runBtn = screen.getByRole("button", { name: /Analizi Calistir|Run FGG Analysis/i });
    fireEvent.click(runBtn);

    // Wait for analysis execution to complete and check store audit log
    await waitFor(() => {
      const logs = useForensicCaseStore.getState().auditTrail;
      expect(logs.some((l) => l.module === "Forensic Genetic Genealogy (FGG / IGG)")).toBe(true);
    });

    // Navigate to Legal Compliance Tab
    const tab5 = screen.getByText(/5\. Yasal Mevzuat|5\. Legal Governance/i);
    fireEvent.click(tab5);

    // Click Issue Destruction Order button
    const issueBtn = screen.getByRole("button", { name: /Imha Sertifikasi Uret|Issue Destruction Order/i });
    fireEvent.click(issueBtn);

    // Verify sealed destruction certificate rendered in DOM
    await waitFor(() => {
      expect(screen.getByText("SEALED")).toBeInTheDocument();
    });
    expect(screen.getByText(/Numuneler Imha Protokolune Alindi|Reference DNA Incineration Ordered/i)).toBeInTheDocument();

    // Check store audit trail contains destruction order log
    const auditLogs = useForensicCaseStore.getState().auditTrail;
    const destLog = auditLogs.find((l) => l.event.includes("Destruction Order Issued"));
    expect(destLog).toBeDefined();
    expect(destLog!.module).toBe("Forensic Genetic Genealogy (FGG / IGG)");
    expect(destLog!.standard).toContain("Maryland Title 17");
  });

  // ── 6. Master Rule 4 Compliance (Zero Em-Dashes) ─────────────────────────

  it("strictly complies with Master Rule 4: zero em-dashes across rendered DOM and preset metadata", () => {
    const { container } = render(<PanelFGG />);
    const text = container.textContent || "";

    // Test for em-dash (U+2014) and en-dash (U+2013)
    expect(text.includes("\u2014")).toBe(false);
    expect(text.includes("\u2013")).toBe(false);

    // Check presets
    for (const p of FGG_PRESETS) {
      expect(p.title.includes("\u2014")).toBe(false);
      expect(p.title.includes("\u2013")).toBe(false);
      expect(p.desc.includes("\u2014")).toBe(false);
      expect(p.desc.includes("\u2013")).toBe(false);
      expect(p.titleTr.includes("\u2014")).toBe(false);
      expect(p.titleTr.includes("\u2013")).toBe(false);
      expect(p.descTr.includes("\u2014")).toBe(false);
      expect(p.descTr.includes("\u2013")).toBe(false);
    }
  });
});
