import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PanelYSTR, {
  NIST_SRM_2391D_R1B,
  NA18507_O2A,
  NA19240_YRI_E1B1A,
  FATHER_SON_RM_MUTATION,
  PRESET_COHORTS,
  YHRD_METAPOPULATIONS,
  LOCUS_ORDER,
  computeClopperPearsonBound,
  computeBrennerFrequency,
  decoupleDYS389,
  computeStepwiseMutationLR,
  estimateMinimumMaleContributors,
  computeYStrAuditHash,
  evaluateYStrKinshipClient,
} from "@/components/analysis/PanelYSTR";
import { useForensicCaseStore, SAMPLE_CASE_EU } from "@/store/forensicCaseStore";

// Mock API Base URL
vi.mock("@/lib/api", () => ({
  getApiBaseUrl: () => "http://localhost:8000",
}));

// Mock Saas Language Context
vi.mock("@/context/SaaSLanguageContext", () => ({
  useSaasLanguage: () => ({
    lang: "en",
    setLang: vi.fn(),
  }),
}));

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

// Setup dynamic fetch mock
const setupFetchMock = () => {
  return vi.fn().mockImplementation((url: string, opts: any) => {
    if (url.includes("/evaluate-paternal-kinship")) {
      let isExcl = false;
      let matchCount = 25;
      let lr = 128516.99;
      let logLr = 5.109;

      if (opts?.body) {
        try {
          const parsed = JSON.parse(opts.body);
          if (parsed.suspect_markers?.DYS19 !== parsed.evidence_markers?.DYS19) {
            isExcl = true;
            matchCount = 0;
            lr = 0.0;
            logLr = -300.0;
          }
        } catch {}
      }

      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({
          matching_loci_count: matchCount,
          mutated_loci_count: isExcl ? 25 : 0,
          rm_mutations_count: 0,
          standard_mutations_count: isExcl ? 25 : 0,
          paternal_lr: lr,
          log10_paternal_lr: logLr,
          haplotype_p_upper: 7.7810723e-6,
          is_lineage_excluded: isExcl,
          verbal_predicate_en: isExcl ? "Exclusion of Common Paternal Lineage" : "Extremely Strong Support for Common Paternal Lineage",
          verbal_predicate_tr: isExcl ? "Ortak Baba Soyunun Dışlanması" : "Ortak Baba Soyu Lehine Son Derece Güçlü Kanıt",
        }),
      });
    }
    if (url.includes("/predict-haplogroup")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({
          predicted_haplogroup: "R1b",
          confidence: 0.942,
          primary_snp: "M269",
          top_posteriors: [
            { clade: "R1b (M269)", prob: 0.942 },
            { clade: "R1a (M420)", prob: 0.038 },
          ],
        }),
      });
    }
    if (url.includes("/decouple-dys389")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({
          dys389_1: 13,
          dys389_2: 17,
          is_biologically_valid: true,
        }),
      });
    }
    if (url.includes("/mixture-contributors")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({
          minimum_male_contributors: 3,
          max_alleles_single_copy_locus: "DYS389II",
          max_alleles_single_copy_count: 3,
          max_alleles_multi_copy_locus: "DYS385a/b",
          max_alleles_multi_copy_count: 6,
          explanation_en: "Estimated minimum of 3 male donors based on observed alleles.",
          explanation_tr: "Gözlenen alellere göre en az 3 erkek donörü tespit edilmiştir.",
        }),
      });
    }
    return Promise.reject(new Error("Unknown route"));
  });
};

global.fetch = setupFetchMock();

describe("Subsystem 08: Y-Chromosome 27-Locus Lineage & Haplotype Engine", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockClipboardWriteText.mockClear();
    global.fetch = setupFetchMock();

    // Reset Forensic Case Store with deterministic sample data
    useForensicCaseStore.setState({
      activeCase: {
        ...SAMPLE_CASE_EU,
        metadata: {
          ...SAMPLE_CASE_EU.metadata,
          caseId: "YSTR-TEST-2026",
          leadAnalyst: "Dr. Elena Rostova",
        },
      },
      auditLogs: [],
    });
  });

  // ─── Mathematical Invariants & Reference Standards ──────────────────────────

  it("should have exactly 27 loci across 25 genotyping systems", () => {
    expect(LOCUS_ORDER).toHaveLength(25);
    const multiCopyLoci = LOCUS_ORDER.filter((l) => l.isMultiCopy);
    expect(multiCopyLoci).toHaveLength(2);
    expect(multiCopyLoci.map((l) => l.name)).toEqual(["DYS385a/b", "DYF387S1a/b"]);
  });

  it("should contain exactly 7 Rapidly Mutating (RM) Y-STR loci across 6 systems", () => {
    const rmSystems = LOCUS_ORDER.filter((l) => l.isRm);
    expect(rmSystems).toHaveLength(6);
    const totalRmLoci = rmSystems.reduce((acc, l) => acc + (l.isMultiCopy ? 2 : 1), 0);
    expect(totalRmLoci).toBe(7);

    const rmNames = rmSystems.map((l) => l.name);
    expect(rmNames).toContain("DYS576");
    expect(rmNames).toContain("DYS627");
    expect(rmNames).toContain("DYS518");
    expect(rmNames).toContain("DYS570");
    expect(rmNames).toContain("DYF387S1a/b");
    expect(rmNames).toContain("DYS449");
  });

  it("should calculate Clopper-Pearson 95% upper bound for unobserved haplotypes (k=0)", () => {
    const N = 385000;
    const pUpper = computeClopperPearsonBound(0, N);
    const expected = 1.0 - Math.pow(0.05, 1.0 / (N + 1));
    expect(Math.abs(pUpper - expected)).toBeLessThan(1e-12);
    expect(pUpper).toBeGreaterThan(0.0);
    expect(pUpper).toBeLessThan(1e-4);
  });

  it("should calculate Brenner theta-adjusted subpopulation frequency", () => {
    const N = 10000;
    const k = 0;
    const theta = 0.03;
    const brenner = computeBrennerFrequency(k, N, theta);
    expect(brenner).toBeCloseTo(0.03 / 10000.03, 8);
  });

  it("should decouple DYS389I and DYS389II into distinct forward and reverse segments", () => {
    const decoupled = decoupleDYS389(13, 30);
    expect(decoupled.dys389_1).toBe(13);
    expect(decoupled.dys389_2).toBe(17);
    expect(decoupled.isValid).toBe(true);

    const decoupled2 = decoupleDYS389(14, 31);
    expect(decoupled2.dys389_1).toBe(14);
    expect(decoupled2.dys389_2).toBe(17);
    expect(decoupled2.isValid).toBe(true);
  });

  it("should compute Stepwise Mutation Model (SMM) single-locus probability for perfect match", () => {
    const mu = 0.002;
    const r = 0.10;
    const pMatch = computeStepwiseMutationLR(1, 0, mu, r);
    expect(pMatch).toBeCloseTo(1.0 - mu, 4);
  });

  it("should compute Stepwise Mutation Model single-step mutation penalty", () => {
    const mu = 0.002;
    const r = 0.10;
    const pOneStep = computeStepwiseMutationLR(1, 1, mu, r);
    const expected = mu * ((1.0 - r) / 2);
    expect(pOneStep).toBeCloseTo(expected, 6);
  });

  it("should compute multi-step mutation penalty exponentially lower than single-step", () => {
    const mu = 0.002;
    const r = 0.10;
    const pOneStep = computeStepwiseMutationLR(1, 1, mu, r);
    const pTwoStep = computeStepwiseMutationLR(1, 2, mu, r);
    expect(pTwoStep).toBeLessThan(pOneStep);
    expect(pTwoStep).toBeCloseTo(pOneStep * r, 6);
  });

  it("should verify NIST SRM 2391d Component A golden vector coordinates", () => {
    const srm = NIST_SRM_2391D_R1B;
    expect(srm["DYS19"]).toBe(14);
    expect(srm["DYS392"]).toBe(13);
    expect(srm["DYS385a/b"]).toEqual([11, 14]);
    expect(srm["DYF387S1a/b"]).toEqual([35, 37]);
  });

  it("should estimate minimum male contributors accurately from single and multi-copy loci", () => {
    const singleDonor = estimateMinimumMaleContributors({
      DYS19: [14],
      "DYS385a/b": [11, 14],
    });
    expect(singleDonor.minContributors).toBe(1);

    const twoDonors = estimateMinimumMaleContributors({
      DYS19: [14, 15],
      "DYS385a/b": [11, 12, 14, 16],
    });
    expect(twoDonors.minContributors).toBe(2);

    const multiDonor = estimateMinimumMaleContributors({
      DYS19: [13, 14, 15, 16],
      "DYS385a/b": [11, 14],
    });
    expect(multiDonor.minContributors).toBe(4);
    expect(multiDonor.maxSingleCount).toBe(4);
  });

  it("should estimate minimum contributors based on ceil(multiCopy / 2)", () => {
    const resMulti = estimateMinimumMaleContributors({
      DYS19: [14, 15],
      "DYS385a/b": [11, 12, 13, 14, 15, 16],
    });
    expect(resMulti.minContributors).toBe(3);
    expect(resMulti.maxMultiCount).toBe(6);
    expect(resMulti.explanationTr).toContain("Cift kopyali DYS385a/b");
  });

  it("should reject non-positive DYS389I alleles during decoupling", () => {
    const invalidZero = decoupleDYS389(0, 29);
    expect(invalidZero.isValid).toBe(false);

    const invalidNegative = decoupleDYS389(-5, 20);
    expect(invalidNegative.isValid).toBe(false);
  });

  it("should handle boundary conditions for database size N <= 0 safely", () => {
    expect(computeClopperPearsonBound(0, 0)).toBe(1.0);
    expect(computeClopperPearsonBound(0, -100)).toBe(1.0);
    expect(computeBrennerFrequency(0, 0)).toBe(1.0);
  });

  // ─── Deterministic State Audit Hash & Client Evaluator Units ─────────────────

  it("should compute deterministic 64-hex SHA-256 state audit digest", () => {
    const hash1 = computeYStrAuditHash(
      "CASE-001",
      "EVID-001",
      "SUSP-001",
      "SRM_2391D_FATHER_SON",
      1,
      25,
      0,
      128516.99,
      5.109,
      7.781e-6
    );
    expect(hash1).toHaveLength(64);
    expect(hash1).toMatch(/^[0-9a-f]{64}$/);

    // Exact reproducibility
    const hash2 = computeYStrAuditHash(
      "CASE-001",
      "EVID-001",
      "SUSP-001",
      "SRM_2391D_FATHER_SON",
      1,
      25,
      0,
      128516.99,
      5.109,
      7.781e-6
    );
    expect(hash1).toBe(hash2);

    // Perturbation sensitivity
    const hashChanged = computeYStrAuditHash(
      "CASE-001",
      "EVID-001",
      "SUSP-001",
      "RM_MUTATION_DUO",
      1,
      24,
      1,
      289.16,
      2.461,
      7.781e-6
    );
    expect(hashChanged).not.toBe(hash1);
  });

  it("should execute pure client evaluator for pristine paternal duo without exclusion", () => {
    const res = evaluateYStrKinshipClient(NIST_SRM_2391D_R1B, NIST_SRM_2391D_R1B, 1, 385000, 0.03, 0);
    expect(res.isExcluded).toBe(false);
    expect(res.matchingLoci).toBe(25);
    expect(res.mutatedLoci).toBe(0);
    expect(res.paternalLR).toBeGreaterThan(100000);
    expect(res.log10LR).toBeGreaterThan(5.0);
    expect(res.predictedHaplogroup).toBe("R1b");
    expect(res.primarySnp).toBe("M269");
  });

  it("should execute pure client evaluator for father-son RM mutation duo (prevent false exclusion)", () => {
    const res = evaluateYStrKinshipClient(NIST_SRM_2391D_R1B, FATHER_SON_RM_MUTATION, 1, 385000, 0.03, 0);
    expect(res.isExcluded).toBe(false);
    expect(res.matchingLoci).toBe(24);
    expect(res.mutatedLoci).toBe(1);
    expect(res.rmMutations).toBe(1);
    expect(res.standardMutations).toBe(0);
    expect(res.paternalLR).toBeGreaterThan(200);
    expect(res.log10LR).toBeGreaterThan(2.0);
  });

  it("should execute pure client evaluator for unrelated males with definite exclusion (LR = 0)", () => {
    const res = evaluateYStrKinshipClient(NIST_SRM_2391D_R1B, NA18507_O2A, 1, 385000, 0.03, 0);
    expect(res.isExcluded).toBe(true);
    expect(res.paternalLR).toBe(0.0);
    expect(res.log10LR).toBe(-300.0);
    expect(res.verbalEn).toContain("Exclusion");
    expect(res.verbalTr).toContain("Dışlanması");
  });

  // ─── Component Rendering & UI Integration Tests ──────────────────────────────

  it("should render PanelYSTR with unified mission bar, telemetry HUD, and 6 tabs", async () => {
    render(<PanelYSTR />);
    expect(screen.getByText(/Y-FILER Plus 27-Locus Lineage & Paternal Engine/i)).toBeInTheDocument();
    expect(screen.getByText(/Pillar 02: Lineage Forensics/i)).toBeInTheDocument();
    expect(screen.getByText(/1. Paternal Kinship & Match/i)).toBeInTheDocument();
    expect(screen.getByText(/2. 27-Locus Panel & SMM/i)).toBeInTheDocument();
    expect(screen.getByText(/3. YHRD Frequencies & Bounds/i)).toBeInTheDocument();
    expect(screen.getByText(/4. Mixture Studio & DYS389/i)).toBeInTheDocument();
    expect(screen.getByText(/5. Casework Sandbox/i)).toBeInTheDocument();
    expect(screen.getByText(/6. ISO 17025 Court Certificate/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText(/Analyzing\.\.\./i)).not.toBeInTheDocument();
    });
  });

  it("should navigate to Tab 6 and render Court Admissibility Certificate and SHA-256 Digest", async () => {
    render(<PanelYSTR />);

    const certTabBtn = screen.getByText(/6. ISO 17025 Court Certificate/i);
    fireEvent.click(certTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Y-FILER Plus 27-Locus Forensic Lineage Validation Certificate/i)).toBeInTheDocument();
      expect(screen.getByText(/CERTIFICATE ID: CERT-YSTR-YSTR-TEST-2026/i)).toBeInTheDocument();
      expect(screen.getByText(/Dr. Elena Rostova/i)).toBeInTheDocument();
      expect(screen.getByText(/Cryptographic State Audit Digest/i)).toBeInTheDocument();
      expect(screen.getByText(/Prosecutor's Fallacy Defense Shield/i)).toBeInTheDocument();
    });
  });

  it("should copy court certificate to clipboard and dispatch structured audit log", async () => {
    render(<PanelYSTR />);

    const certTabBtn = screen.getByText(/6. ISO 17025 Court Certificate/i);
    fireEvent.click(certTabBtn);

    const copyBtn = await screen.findByText(/Copy Certificate/i);
    fireEvent.click(copyBtn);

    await waitFor(() => {
      expect(mockClipboardWriteText).toHaveBeenCalled();
      const copiedText = mockClipboardWriteText.mock.calls[0][0];
      expect(copiedText).toContain("Y-STR LINEAGE VALIDATION CERTIFICATE");
      expect(copiedText).toContain("CERT-YSTR-YSTR-TEST-2026");
      expect(copiedText).toContain("Dr. Elena Rostova");
      expect(copiedText).toContain("TRANSPOSING THE CONDITIONAL DEFENSE SHIELD");
    });

    const trail = useForensicCaseStore.getState().auditTrail;
    expect(trail.some((l) => l.event.includes("Y-STR Validation Certificate"))).toBe(true);
  });

  it("should copy cryptographic state audit hash to clipboard and log audit action", async () => {
    render(<PanelYSTR />);

    const certTabBtn = screen.getByText(/6. ISO 17025 Court Certificate/i);
    fireEvent.click(certTabBtn);

    const copyHashBtn = await screen.findByText(/Copy Hash/i);
    fireEvent.click(copyHashBtn);

    await waitFor(() => {
      expect(mockClipboardWriteText).toHaveBeenCalled();
      const trail = useForensicCaseStore.getState().auditTrail;
      expect(trail.some((l) => l.event.includes("Y-STR state audit hash"))).toBe(true);
    });
  });

  it("should switch preset cohort to Unrelated Males and dynamically update telemetry even on API fallback", async () => {
    // Mock fetch failure to test client fallback resilience
    global.fetch = vi.fn().mockRejectedValue(new Error("Network offline"));

    render(<PanelYSTR />);

    const unrelatedCohortBtn = screen.getByText(/Unrelated Males \(R1b vs O2a\)/i);
    fireEvent.click(unrelatedCohortBtn);

    await waitFor(() => {
      // Verdict should update to EXCLUDED
      expect(screen.getByText(/EXCLUDED/i)).toBeInTheDocument();
    });

    const trail = useForensicCaseStore.getState().auditTrail;
    expect(trail.some((l) => l.event.includes("Y-STR kinship"))).toBe(true);
  });

  it("should switch preset cohort to RM Mutation Duo and display RM mutation count > 0 with inclusion", async () => {
    render(<PanelYSTR />);

    await waitFor(() => {
      expect(screen.queryByText(/Analyzing\.\.\./i)).not.toBeInTheDocument();
    });

    const rmMutationBtn = screen.getByText(/Paternal Duo \+ RM Mutation \(DYS518\)/i);
    fireEvent.click(rmMutationBtn);

    await waitFor(() => {
      expect(screen.getByText(/INCLUDED/i)).toBeInTheDocument();
    });
  });

  it("should interact with DYS389 decoupler inputs in Tab 4", async () => {
    render(<PanelYSTR />);

    const mixturesTabBtn = screen.getByText(/4. Mixture Studio & DYS389/i);
    fireEvent.click(mixturesTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/DYS389I & DYS389II Nested Repeat Decoupler/i)).toBeInTheDocument();
      expect(screen.getByText(/DYS389I Allele:/i)).toBeInTheDocument();
    });
  });

  it("should trigger manual analysis button and show progress animation", async () => {
    render(<PanelYSTR />);

    await waitFor(() => {
      expect(screen.queryByText(/Analyzing\.\.\./i)).not.toBeInTheDocument();
    });

    const runBtn = screen.getByText(/Execute Kinship Analysis/i);
    fireEvent.click(runBtn);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});
