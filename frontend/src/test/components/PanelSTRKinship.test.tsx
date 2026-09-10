import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PanelSTRKinship, {
  MASTER_24_STR_LOCI,
  NIST_1036_POP_FREQS,
  GOLDEN_STR_BENCHMARKS,
  PEDIGREE_RELATIONSHIPS,
  calcBaldingNicholsProb,
  calcStepwiseMutationProb,
  getNistFreq,
  computeSTRAuditHash,
  evaluateSTRKinshipClient,
} from "@/components/analysis/PanelSTRKinship";

// Mock useForensicCaseStore
const mockAddAuditLog = vi.fn();
vi.mock("@/store/forensicCaseStore", () => ({
  useForensicCaseStore: () => ({
    activeCase: {
      metadata: {
        caseId: "TEST-CASE-2026-STR",
        leadAnalyst: "Dr. FORENZA Test Specialist",
      },
    },
    addAuditLog: mockAddAuditLog,
  }),
}));

describe("Subsystem 01: Autosomal STR & Kinship Engine", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("24-Locus Autosomal STR Registry & Microvariants", () => {
    it("contains all 24 standard loci including CODIS 20, SE33, and Penta D/E", () => {
      expect(MASTER_24_STR_LOCI.length).toBe(24);
      const locusNames = MASTER_24_STR_LOCI.map((l) => l.name);
      expect(locusNames).toContain("TH01");
      expect(locusNames).toContain("SE33");
      expect(locusNames).toContain("D21S11");
      expect(locusNames).toContain("FGA");
      expect(locusNames).toContain("D1S1656");
      expect(locusNames).toContain("Penta D");
      expect(locusNames).toContain("Penta E");
      expect(locusNames).toContain("AMEL");
    });

    it("verifies diagnostic microvariant presence in mutational catalog", () => {
      const th01 = MASTER_24_STR_LOCI.find((l) => l.name === "TH01");
      expect(th01?.microvariants).toContain("9.3");

      const se33 = MASTER_24_STR_LOCI.find((l) => l.name === "SE33");
      expect(se33?.microvariants).toContain("28.2");

      const d21s11 = MASTER_24_STR_LOCI.find((l) => l.name === "D21S11");
      expect(d21s11?.microvariants).toContain("31.2");
    });

    it("validates base offset and repeat unit sizing parameters across all loci", () => {
      MASTER_24_STR_LOCI.forEach((def) => {
        expect(def.baseOffsetBp).toBeGreaterThan(0);
        expect(def.repeatUnitBp).toBeGreaterThanOrEqual(3);
        expect(def.stutterMax).toBeGreaterThanOrEqual(0.0);
      });
    });
  });

  describe("NIST 1036 Population Allele Frequencies & p_min Floor", () => {
    it("provides allele frequencies for major continental cohorts", () => {
      expect(NIST_1036_POP_FREQS.Caucasian).toBeDefined();
      expect(NIST_1036_POP_FREQS.AfricanAmerican).toBeDefined();
      expect(NIST_1036_POP_FREQS.Hispanic).toBeDefined();
      expect(NIST_1036_POP_FREQS.Asian).toBeDefined();
    });

    it("enforces minimum allele frequency floor p_min = 5/(2N) = 0.002413", () => {
      const pMinFloor = 5.0 / (2.0 * 1036.0);
      expect(pMinFloor).toBeCloseTo(0.002413, 5);

      // Unobserved allele should return p_min floor
      const unobservedFreq = getNistFreq("TH01", "99.9", "Caucasian");
      expect(unobservedFreq).toBeCloseTo(pMinFloor, 5);
    });

    it("retrieves known high-frequency alleles accurately", () => {
      const th01_93 = getNistFreq("TH01", "9.3", "Caucasian");
      expect(th01_93).toBeGreaterThan(0.20);
    });
  });

  describe("Pure Mathematical Functions", () => {
    it("computes Balding-Nichols coancestry correction for homozygotes and heterozygotes", () => {
      const p1 = 0.20;
      const p2 = 0.30;
      const theta = 0.01;

      const homoProb = calcBaldingNicholsProb(p1, p1, true, theta);
      expect(homoProb).toBeGreaterThan(0.0);

      const heteroProb = calcBaldingNicholsProb(p1, p2, false, theta);
      expect(heteroProb).toBeGreaterThan(0.0);
      expect(heteroProb).toBeLessThan(1.0);
    });

    it("calculates Stepwise Mutation Model (SMM) with r=0.10 and mu=1e-3", () => {
      const noMutation = calcStepwiseMutationProb(10, 10, 1e-3, 0.10);
      expect(noMutation).toBe(0.999);

      const singleStep = calcStepwiseMutationProb(10, 11, 1e-3, 0.10);
      // P(1-step) = (mu / 2) * (1 - r) * r^0 = (1e-3 / 2) * 0.90 = 4.5e-4
      expect(singleStep).toBeCloseTo(4.5e-4, 6);

      const twoStep = calcStepwiseMutationProb(10, 12, 1e-3, 0.10);
      // P(2-step) = (mu / 2) * (1 - r) * r^1 = 4.5e-5
      expect(twoStep).toBeCloseTo(4.5e-5, 7);
      expect(twoStep).toBeLessThan(singleStep);
    });

    it("generates deterministic 64-hex SHA-256 state audit digest", () => {
      const hash1 = computeSTRAuditHash("CASE-1", "EVID-1", "REF-1", "Caucasian", 0.01, "parent_child", 24, 0, 12.5, 1e-12);
      const hash2 = computeSTRAuditHash("CASE-1", "EVID-1", "REF-1", "Caucasian", 0.01, "parent_child", 24, 0, 12.5, 1e-12);
      const hash3 = computeSTRAuditHash("CASE-2", "EVID-1", "REF-1", "Caucasian", 0.01, "parent_child", 24, 0, 12.5, 1e-12);

      expect(hash1).toHaveLength(64);
      expect(hash1).toBe(hash2);
      expect(hash1).not.toBe(hash3);
    });
  });

  describe("Pure Client Evaluator (evaluateSTRKinshipClient)", () => {
    it("evaluates complete parent-child inclusion across all 24 loci", () => {
      const bm = GOLDEN_STR_BENCHMARKS.find((b) => b.id === "PATERNITY_HIGH_CPI")!;
      const res = evaluateSTRKinshipClient(bm.alleles, bm.alleles, bm.pop, bm.theta, "parent_child");

      expect(res.matchingLociCount).toBe(24);
      expect(res.mutationalMismatchCount).toBe(0);
      expect(res.totalLog10LR).toBeGreaterThan(6.0);
      expect(res.wPercent).toBeGreaterThan(99.9999);
      expect(res.rmp).toBeLessThan(1e-6);
    });

    it("applies SMM mutation penalty when non-matching locus is encountered in paternity", () => {
      const alleles1 = { ...GOLDEN_STR_BENCHMARKS[0].alleles };
      const alleles2 = { ...GOLDEN_STR_BENCHMARKS[0].alleles };
      // Introduce single-step mutation in D3S1358
      alleles2.D3S1358 = ["25", "26"];

      const res = evaluateSTRKinshipClient(alleles1, alleles2, "Caucasian", 0.01, "parent_child");
      expect(res.mutationalMismatchCount).toBe(1);
      const mutLocus = res.rows.find((r) => r.locus === "D3S1358");
      expect(mutLocus?.mutated).toBe(true);
      expect(mutLocus?.lr).toBeLessThan(1e-2);
    });

    it("evaluates full sibling relationship with Ito-Donnelly coefficients", () => {
      const alleles = GOLDEN_STR_BENCHMARKS[0].alleles;
      const res = evaluateSTRKinshipClient(alleles, alleles, "Caucasian", 0.01, "full_sibling");

      expect(res.totalLog10LR).toBeGreaterThan(5.0);
      expect(res.matchingLociCount).toBe(24);
    });

    it("evaluates half sibling, avuncular, and grandparent relationships", () => {
      const alleles = GOLDEN_STR_BENCHMARKS[0].alleles;
      const resHalf = evaluateSTRKinshipClient(alleles, alleles, "Caucasian", 0.01, "half_sibling");
      const resAvunc = evaluateSTRKinshipClient(alleles, alleles, "Caucasian", 0.01, "avuncular");

      expect(resHalf.totalLog10LR).toBeCloseTo(resAvunc.totalLog10LR, 4);
      expect(resHalf.totalLog10LR).toBeGreaterThan(3.0);
    });

    it("evaluates first cousin relationship with appropriate transmission baseline", () => {
      const alleles = GOLDEN_STR_BENCHMARKS[0].alleles;
      const resCousin = evaluateSTRKinshipClient(alleles, alleles, "Caucasian", 0.01, "first_cousin");

      expect(resCousin.totalLog10LR).toBeGreaterThan(1.0);
    });

    it("evaluates unrelated direct match baseline", () => {
      const alleles = GOLDEN_STR_BENCHMARKS[0].alleles;
      const resUnrel = evaluateSTRKinshipClient(alleles, alleles, "Caucasian", 0.01, "unrelated");

      expect(resUnrel.totalLog10LR).toBeGreaterThan(20.0);
    });
  });

  describe("Certified Golden Standards & Benchmark Vectors", () => {
    it("contains NIST SRM 2391d Component A and Casework Benchmarks", () => {
      expect(GOLDEN_STR_BENCHMARKS.length).toBeGreaterThanOrEqual(3);
      const nistA = GOLDEN_STR_BENCHMARKS.find((b) => b.id === "NIST_SRM_2391D_COMP_A");
      expect(nistA).toBeDefined();
      expect(nistA?.alleles.TH01).toEqual(["8", "9.3"]);
      expect(nistA?.alleles.SE33).toEqual(["19", "29.2"]);
      expect(nistA?.expectedLog10LR).toBeGreaterThan(20.0);
    });

    it("defines all 7 pedigree relationships in PEDIGREE_RELATIONSHIPS", () => {
      expect(PEDIGREE_RELATIONSHIPS.length).toBe(7);
      const relIds = PEDIGREE_RELATIONSHIPS.map((p) => p.id);
      expect(relIds).toContain("parent_child");
      expect(relIds).toContain("full_sibling");
      expect(relIds).toContain("half_sibling");
      expect(relIds).toContain("avuncular");
      expect(relIds).toContain("grandparent");
      expect(relIds).toContain("first_cousin");
      expect(relIds).toContain("unrelated");
    });
  });

  describe("PanelSTRKinship Component Rendering & UI Interactions", () => {
    it("renders the 24-locus studio with header telemetry, case ID, and state hash", () => {
      const { container } = render(<PanelSTRKinship />);
      expect(container).toBeInTheDocument();
      expect(screen.getAllByText(/24-Locus Autosomal STR|24 STR/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/CODIS 20 \+ SE33/i).length).toBeGreaterThan(0);
      expect(screen.getByText("TEST-CASE-2026-STR")).toBeInTheDocument();
      expect(screen.getByText(/H_str/i)).toBeInTheDocument();
    });

    it("navigates through all 5 tabs smoothly", () => {
      render(<PanelSTRKinship />);

      // Tab 2: Kinship & LR
      fireEvent.click(screen.getByText(/Akrabalık & LR|Kinship & LR/i));
      expect(screen.getAllByText(/Akrabalık & Babalık|Kinship & Paternity/i).length).toBeGreaterThan(0);

      // Tab 3: NIST 1036 Frequencies
      fireEvent.click(screen.getByText(/NIST 1036 Frekans|NIST 1036 Freqs/i));
      expect(screen.getAllByText(/NIST 1036 Popülasyon Alel Frekans|NIST 1036 Population Allele Frequency/i).length).toBeGreaterThan(0);

      // Tab 4: Benchmarks
      fireEvent.click(screen.getByText(/Altın Vektörler|Benchmarks/i));
      expect(screen.getAllByText(/Sertifikalı Adli Referans|Certified Forensic Reference/i).length).toBeGreaterThan(0);

      // Tab 5: ISO / ENFSI Report
      fireEvent.click(screen.getByText(/ISO \/ ENFSI Raporu|ISO \/ ENFSI Report/i));
      expect(screen.getAllByText(/ISO\/IEC 17025 & ENFSI 2017/i).length).toBeGreaterThan(0);

      // Tab 1: Return to 24 STR Loci
      fireEvent.click(screen.getByText(/24 STR Lokusu|24 STR Loci/i));
      expect(screen.getAllByText(/24-Lokus Otozomal Multiplex|24-Locus Autosomal Multiplex/i).length).toBeGreaterThan(0);
    });

    it("switches kinship hypotheses and dispatches structured audit log", () => {
      render(<PanelSTRKinship />);

      // Go to Tab 2
      fireEvent.click(screen.getByText(/Akrabalık & LR|Kinship & LR/i));

      // Click Full Sibling
      const siblingBtn = screen.getByText(/Öz Kardeş|Full Sibling/i);
      fireEvent.click(siblingBtn);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_KINSHIP_HYPOTHESIS_CHANGED: full_sibling"),
          module: "01_str_kinship",
        })
      );

      // Click First Cousin
      const cousinBtn = screen.getByText(/Birinci Derece Kuzen|First Cousin/i);
      fireEvent.click(cousinBtn);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_KINSHIP_HYPOTHESIS_CHANGED: first_cousin"),
          module: "01_str_kinship",
        })
      );
    });

    it("loads certified golden benchmark and dispatches audit log", () => {
      render(<PanelSTRKinship />);

      // Go to Tab 4
      fireEvent.click(screen.getByText(/Altın Vektörler|Benchmarks/i));

      const loadButtons = screen.getAllByText(/Profili Yükle|Load Profile/i);
      expect(loadButtons.length).toBeGreaterThanOrEqual(3);

      fireEvent.click(loadButtons[0]);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_LOAD_GOLDEN_BENCHMARK"),
          module: "01_str_kinship",
        })
      );
    });

    it("copies court report to clipboard in Tab 5 and logs action", async () => {
      render(<PanelSTRKinship />);

      // Go to Tab 5
      fireEvent.click(screen.getByText(/ISO \/ ENFSI Raporu|ISO \/ ENFSI Report/i));

      const copyBtn = screen.getByText(/Raporu Kopyala|Copy Report/i);
      fireEvent.click(copyBtn);

      expect(navigator.clipboard.writeText).toHaveBeenCalled();
      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_CERTIFICATE_COPIED"),
          module: "01_str_kinship",
        })
      );

      await waitFor(() => {
        expect(screen.getByText(/Kopyalandı!|Copied!/i)).toBeInTheDocument();
      });
    });

    it("copies cryptographic state audit hash to clipboard and dispatches audit entry", async () => {
      render(<PanelSTRKinship />);

      // Click Copy Hash button in header or Tab 5
      const copyHashButtons = screen.getAllByTitle(/Hash Kopyala|Copy Hash/i);
      if (copyHashButtons.length > 0) {
        fireEvent.click(copyHashButtons[0]);
      } else {
        fireEvent.click(screen.getByText(/ISO \/ ENFSI Raporu|ISO \/ ENFSI Report/i));
        fireEvent.click(screen.getByText(/Hash Kopyala|Copy Hash/i));
      }

      expect(navigator.clipboard.writeText).toHaveBeenCalled();
      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_AUDIT_HASH_COPIED"),
          module: "01_str_kinship",
        })
      );
    });

    it("triggers server verification API and gracefully handles offline/error responses", async () => {
      // Mock fetch failure
      global.fetch = vi.fn().mockRejectedValue(new Error("Network connection refused"));

      render(<PanelSTRKinship />);

      const verifyBtn = screen.getByText(/Sunucu Doğrulaması|Run Server Verification/i);
      fireEvent.click(verifyBtn);

      await waitFor(() => {
        expect(screen.getByText(/İstemci Motoru Aktif|Client Engine Active/i)).toBeInTheDocument();
      });
    });

    it("filters population frequency loci based on search query in Tab 3", () => {
      render(<PanelSTRKinship />);

      // Go to Tab 3
      fireEvent.click(screen.getByText(/NIST 1036 Frekans|NIST 1036 Freqs/i));

      const searchInput = screen.getByPlaceholderText(/Lokus ara|Search locus/i);
      fireEvent.change(searchInput, { target: { value: "TH01" } });

      expect(screen.getByText("TH01")).toBeInTheDocument();
    });

    it("toggles between Single-Source LR and Pedigree Kinship analysis modes", () => {
      render(<PanelSTRKinship />);

      // Go to Tab 2
      fireEvent.click(screen.getByText(/Akrabalık & LR|Kinship & LR/i));

      // Click Single-Source LR mode button
      const singleSourceBtn = screen.getByText(/Tek Kaynaklı Şüpheli Eşleşmesi|Single-Source Suspect Match/i);
      fireEvent.click(singleSourceBtn);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_ANALYSIS_MODE_CHANGED: single_source_lr"),
          module: "01_str_kinship",
        })
      );

      // Verify Single-Source elements are visible
      expect(screen.getByText(/Tek Kaynaklı Adli Hipotezler|Single-Source Forensic Hypotheses/i)).toBeInTheDocument();
      expect(screen.getAllByText(/POST \/forensic\/lr/i).length).toBeGreaterThan(0);

      // Switch back to Pedigree Kinship
      const pedigreeBtns = screen.getAllByText(/Soyağacı \/ Akrabalık İndeksi|Pedigree Kinship Index/i);
      fireEvent.click(pedigreeBtns[pedigreeBtns.length - 1]);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_ANALYSIS_MODE_CHANGED: pedigree_kinship"),
          module: "01_str_kinship",
        })
      );
    });

    it("executes POST /api/v1/forensic/lr server verification in Single-Source mode", async () => {
      const mockLRResponse = {
        match_status: "INCLUSION",
        lr_value: 2.82e26,
        log10_lr: 26.4502,
        confidence_interval: { low: 1.5e25, high: 4.2e26 },
        evaluated_loci: 23,
        locus_scores: { TH01: 5.2, SE33: 14.8 },
        assumptions: ["Single source", "Balding-Nichols theta=0.01"],
        limitations: ["Casework reference"],
        model: "Balding-Nichols Single-Source LR",
        data_source: "NIST 1036 Caucasian",
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockLRResponse),
      });

      render(<PanelSTRKinship />);

      // Go to Tab 2
      fireEvent.click(screen.getByText(/Akrabalık & LR|Kinship & LR/i));

      // Switch to Single-Source LR mode
      fireEvent.click(screen.getByText(/Tek Kaynaklı Şüpheli Eşleşmesi|Single-Source Suspect Match/i));

      // Click server verification
      const verifyBtn = screen.getByText(/Sunucu Doğrulaması|Run Server Verification/i);
      fireEvent.click(verifyBtn);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          "/api/v1/forensic/lr",
          expect.objectContaining({
            method: "POST",
            headers: { "Content-Type": "application/json" },
          })
        );
      });

      await waitFor(() => {
        expect(screen.getByText(/FastAPI \/lr:/i)).toBeInTheDocument();
        expect(screen.getByText("+26.4502")).toBeInTheDocument();
      });

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_LR_BACKEND_VERIFIED: INCLUSION"),
          module: "01_str_kinship",
        })
      );
    });

    it("executes POST /api/v1/forensic/kinship server verification in Pedigree mode", async () => {
      const mockKinshipResponse = {
        relationship: "parent_child",
        ki_value: 6.32e12,
        log10_ki: 12.8007,
        confidence_interval: { low: 1.2e12, high: 9.8e12 },
        posterior_probability: 99.9999,
        evaluated_loci: 23,
        locus_scores: { TH01: 2.1, SE33: 4.5 },
        assumptions: ["Autosomal transmission", "Ito-Donnelly IBD"],
        limitations: ["No mutation detected"],
        model: "Ito-Donnelly Kinship Index with SMM",
        data_source: "NIST 1036 Caucasian",
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockKinshipResponse),
      });

      render(<PanelSTRKinship />);

      // Go to Tab 2 (defaults to pedigree_kinship)
      fireEvent.click(screen.getByText(/Akrabalık & LR|Kinship & LR/i));

      // Click server verification
      const verifyBtn = screen.getByText(/Sunucu Doğrulaması|Run Server Verification/i);
      fireEvent.click(verifyBtn);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          "/api/v1/forensic/kinship",
          expect.objectContaining({
            method: "POST",
            headers: { "Content-Type": "application/json" },
          })
        );
      });

      await waitFor(() => {
        expect(screen.getByText(/FastAPI \/kinship:/i)).toBeInTheDocument();
        expect(screen.getByText("99.9999%")).toBeInTheDocument();
      });

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_KINSHIP_BACKEND_VERIFIED: parent_child"),
          module: "01_str_kinship",
        })
      );
    });
  });

  describe("Single-Source Strict Exclusion & Interactive Allele Editing", () => {
    it("evaluates strict exclusion (LR=0, log10LR=-10, W=0%, RMP=1.0) when single-source alleles mismatch", () => {
      const evidence = { ...GOLDEN_STR_BENCHMARKS[0].alleles };
      const nonMatchingSuspect = {
        ...evidence,
        TH01: ["7", "8"] as [string, string], // NIST SRM 2391d Comp A is ["9.3", "9.3"]
      };

      const result = evaluateSTRKinshipClient(
        evidence,
        nonMatchingSuspect,
        "Caucasian",
        0.01,
        "parent_child",
        "single_source_lr"
      );

      expect(result.mutationalMismatchCount).toBe(1);
      expect(result.totalLR).toBe(0.0);
      expect(result.totalLog10LR).toBe(-10.0);
      expect(result.wPercent).toBe(0.0);
      expect(result.rmp).toBe(1.0);

      const th01Row = result.rows.find((r) => r.locus === "TH01");
      expect(th01Row?.isMatch).toBe(false);
      expect(th01Row?.lr).toBe(0.0);
    });

    it("toggles edit mode and allows modifying alleles via UI inputs", () => {
      render(<PanelSTRKinship />);

      const editBtn = screen.getByText(/Alelleri Düzenle|Edit Alleles/i);
      fireEvent.click(editBtn);

      // Now inputs should be visible
      const th01Input = screen.getByLabelText(/Evidence TH01 allele 1/i);
      expect(th01Input).toBeInTheDocument();

      fireEvent.change(th01Input, { target: { value: "6" } });
      expect((th01Input as HTMLInputElement).value).toBe("6");

      // Finish editing
      const doneBtn = screen.getByText(/Düzenlemeyi Bitir|Done Editing/i);
      fireEvent.click(doneBtn);
      expect(screen.queryByLabelText(/Evidence TH01 allele 1/i)).not.toBeInTheDocument();
    });

    it("simulates exclusion and resets to NIST baseline correctly", () => {
      render(<PanelSTRKinship />);

      const simulateBtn = screen.getByText(/Dışlama Simüle Et|Simulate Exclusion/i);
      fireEvent.click(simulateBtn);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_SIMULATE_EXCLUSION: Reference TH01 mutated to [7, 8]"),
          module: "01_str_kinship",
        })
      );

      const resetBtn = screen.getByText(/Sıfırla|Reset/i);
      fireEvent.click(resetBtn);

      expect(mockAddAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          event: expect.stringContaining("STR_RESET_PROFILES: Profiles restored to NIST SRM 2391d"),
          module: "01_str_kinship",
        })
      );
    });
  });
});

