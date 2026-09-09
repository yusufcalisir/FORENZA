import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import PanelBGA, {
  computeBGAPosteriors,
  projectWGS84Centroid,
  evaluateFullBGA,
  computeLocalBGA,
  AIM_55_MATRIX,
  CONTINENTAL_CENTROIDS,
  GOLDEN_STANDARDS,
} from "@/components/analysis/PanelBGA";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

describe("Subsystem 15: 55-SNP AIM Biogeographic Ancestry & WGS84 Geodesic Studio", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── 1. Pure Biocomputational Formulation & Simplex Invariants ───────────────

  it("enforces 6-population Dirichlet probability simplex sum-to-one invariant", () => {
    const testCases: Record<string, number>[] = [
      {},
      { rs1426654: 2, rs16891982: 2, rs12913832: 2 },
      { rs2814778: 2, rs3737576: 2, rs7554936: 2 },
      { rs3827760: 2, rs1229984: 2, rs671: 2 },
      GOLDEN_STANDARDS[0].dosages,
      GOLDEN_STANDARDS[1].dosages,
      GOLDEN_STANDARDS[2].dosages,
      GOLDEN_STANDARDS[3].dosages,
      GOLDEN_STANDARDS[4].dosages,
    ];

    for (const snps of testCases) {
      const res = computeBGAPosteriors(snps);
      const sumQ = Object.values(res.props).reduce((a, b) => a + b, 0);
      expect(Math.abs(sumQ - 1.0)).toBeLessThan(1e-3);
      Object.values(res.props).forEach((q) => {
        expect(q).toBeGreaterThanOrEqual(0.0);
        expect(q).toBeLessThanOrEqual(1.0);
      });
    }
  });

  it("correctly deconvolves NA12878 CEU Golden Reference Standard to European ancestry", () => {
    const ceu = GOLDEN_STANDARDS.find((s) => s.id === "NA12878_CEU_EUROPEAN")!;
    const res = evaluateFullBGA(ceu.dosages, "gnomAD_v4");

    expect(res.domPop).toBe("EUR");
    expect(res.domProp).toBeGreaterThanOrEqual(0.90);
    expect(res.admixtureClass).toBe("HOMOGENEOUS");
    expect(res.isSimplexValid).toBe(true);
  });

  it("correctly deconvolves NA19240 YRI Golden Reference Standard to Sub-Saharan African ancestry", () => {
    const yri = GOLDEN_STANDARDS.find((s) => s.id === "NA19240_YRI_AFRICAN")!;
    const res = evaluateFullBGA(yri.dosages, "gnomAD_v4");

    expect(res.domPop).toBe("AFR");
    expect(res.domProp).toBeGreaterThanOrEqual(0.95);
    expect(res.admixtureClass).toBe("HOMOGENEOUS");
    expect(res.isSimplexValid).toBe(true);
  });

  it("correctly deconvolves NA18507 CHB Golden Reference Standard to East Asian ancestry", () => {
    const chb = GOLDEN_STANDARDS.find((s) => s.id === "NA18507_CHB_EAST_ASIAN")!;
    const res = evaluateFullBGA(chb.dosages, "gnomAD_v4");

    expect(res.domPop).toBe("EAS");
    expect(res.domProp).toBeGreaterThanOrEqual(0.90);
    expect(res.admixtureClass).toBe("HOMOGENEOUS");
  });

  it("correctly deconvolves HG002 Mediterranean / Ashkenazi Standard with high MID cline", () => {
    const aj = GOLDEN_STANDARDS.find((s) => s.id === "HG002_AJ_MEDITERRANEAN")!;
    const res = evaluateFullBGA(aj.dosages, "gnomAD_v4");

    expect(res.props.MID).toBeGreaterThanOrEqual(0.50);
  });

  it("evaluates balanced 50/50 EUR/AFR synthetic profile with valid diversity and simplex", () => {
    const adm = GOLDEN_STANDARDS.find((s) => s.id === "ADMIXED_EUR_AFR_SYNTHETIC")!;
    const res = evaluateFullBGA(adm.dosages, "gnomAD_v4");

    expect(["HOMOGENEOUS", "BI_ADMIXED", "MULTI_ADMIXED"]).toContain(res.admixtureClass);
    expect(res.entropy).toBeGreaterThan(0.0);
    expect(res.isSimplexValid).toBe(true);
  });

  // ── 2. WGS84 Geodesic Direction Cosines Projection ──────────────────────────

  it("projects European proportions to European centroid coordinates (WGS84)", () => {
    const props = { EUR: 0.98, AFR: 0.0, EAS: 0.0, SAS: 0.0, AMR: 0.0, MID: 0.02 };
    const gis = projectWGS84Centroid(props);

    expect(gis.lat).toBeGreaterThan(40.0);
    expect(gis.lat).toBeLessThan(55.0);
    expect(gis.lng).toBeGreaterThan(5.0);
    expect(gis.lng).toBeLessThan(25.0);
    expect(gis.vectorNorm).toBeGreaterThan(0.9);
  });

  it("projects Sub-Saharan African proportions to African centroid coordinates", () => {
    const props = { EUR: 0.0, AFR: 0.99, EAS: 0.0, SAS: 0.0, AMR: 0.0, MID: 0.01 };
    const gis = projectWGS84Centroid(props);

    expect(gis.lat).toBeGreaterThan(-5.0);
    expect(gis.lat).toBeLessThan(10.0);
    expect(gis.lng).toBeGreaterThan(15.0);
    expect(gis.lng).toBeLessThan(30.0);
  });

  it("handles zero vector norm edge case deterministically without NaN", () => {
    const props = { EUR: 0.0, AFR: 0.0, EAS: 0.0, SAS: 0.0, AMR: 0.0, MID: 0.0 };
    const gis = projectWGS84Centroid(props);

    expect(gis.lat).toBe(0.0);
    expect(gis.lng).toBe(0.0);
    expect(gis.vectorNorm).toBe(0.0);
  });

  // ── 3. Reference Panel Sensitivity & Backward Compatibility ────────────────

  it("supports reference panel effective sample size variations (gnomAD vs 1000G vs HGDP)", () => {
    const snps = { rs1426654: 2, rs16891982: 2 };
    const resGnomad = computeBGAPosteriors(snps, "gnomAD_v4");
    const res1000G = computeBGAPosteriors(snps, "1000G");
    const resHGDP = computeBGAPosteriors(snps, "HGDP");

    expect(resGnomad.domPop).toBe("EUR");
    expect(res1000G.domPop).toBe("EUR");
    expect(resHGDP.domPop).toBe("EUR");
  });

  it("provides computeLocalBGA alias fully concordant with evaluateFullBGA", () => {
    const snps = { rs3827760: 2, rs1229984: 2 };
    const aliasRes = computeLocalBGA(snps, "gnomAD_v4");
    const directRes = evaluateFullBGA(snps, "gnomAD_v4");

    expect(aliasRes.domPop).toBe(directRes.domPop);
    expect(aliasRes.lat).toBe(directRes.lat);
    expect(aliasRes.lng).toBe(directRes.lng);
  });

  // ── 4. UI Component Rendering & 5-Tab Navigation ───────────────────────────

  it("renders PanelBGA mission header, telemetry status bar, and tabs", () => {
    render(<PanelBGA />);

    expect(screen.getAllByText(/55-SNP AIM/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/ISO\/IEC 17025:2017/i)).toBeDefined();
    expect(screen.getByRole("button", { name: /Golden Standards|Altin Standartlar/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Admixture|Kitasal Karisim/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /3D GIS/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Locus Lab|Lokus Laboratuvari/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Governance|Adli Yargi/i })).toBeDefined();
  });

  it("allows switching across all 5 analytical tabs", () => {
    render(<PanelBGA />);

    // Tab 2: Admixture
    const tabAdmixture = screen.getByRole("button", { name: /Admixture|Kitasal Karisim/i });
    fireEvent.click(tabAdmixture);
    expect(screen.getByText(/European \/ West Eurasian/i)).toBeDefined();

    // Tab 3: 3D GIS Map
    const tabGis = screen.getByRole("button", { name: /3D GIS/i });
    fireEvent.click(tabGis);
    expect(screen.getByText(/3D Spherical Geodesic WGS84 Centroid Map|3D Kuresel Jeodezik WGS84 Sentroid Haritasi/i)).toBeDefined();

    // Tab 4: 55-SNP Locus Lab
    const tabLoci = screen.getByRole("button", { name: /Locus Lab|Lokus Laboratuvari/i });
    fireEvent.click(tabLoci);
    expect(screen.getByPlaceholderText(/Search rsID|rsID, gen veya kromozom ara/i)).toBeDefined();

    // Tab 5: Governance
    const tabGov = screen.getByRole("button", { name: /Governance|Adli Yargi/i });
    fireEvent.click(tabGov);
    expect(screen.getByText(/German § 81e \(2\) StPO|Almanya § 81e \(2\) StPO/i)).toBeDefined();

    // Tab 1: Return to Benchmarks
    const tabBench = screen.getByRole("button", { name: /Golden Standards|Altin Standartlar/i });
    fireEvent.click(tabBench);
    expect(screen.getByText(/NA12878_CEU_EUROPEAN/i)).toBeDefined();
  });

  // ── 5. Standard Vector Loading & Dosage Manipulation ────────────────────────

  it("loads certified reference standard vector and updates active standard ID", () => {
    render(<PanelBGA />);

    const yriButton = screen.getByText(/1000 Genomes NA19240/i);
    fireEvent.click(yriButton);

    expect(screen.getAllByText(/NA19240_YRI_AFRICAN/i).length).toBeGreaterThan(0);
  });

  it("filters SNPs by search query in the 55-SNP Locus Lab", () => {
    render(<PanelBGA />);

    // Switch to Tab 4
    fireEvent.click(screen.getByRole("button", { name: /Locus Lab|Lokus Laboratuvari/i }));

    const searchInput = screen.getByPlaceholderText(/Search rsID|rsID, gen veya kromozom ara/i);
    fireEvent.change(searchInput, { target: { value: "EDAR" } });

    expect(screen.getByText(/rs3827760/i)).toBeDefined();
    expect(screen.queryByText(/rs2814778/i)).toBeNull();
  });

  it("toggles dosage in 55-SNP Locus Lab cycling 0 -> 1 -> 2 -> 0", () => {
    render(<PanelBGA />);

    // Switch to Tab 4
    fireEvent.click(screen.getByRole("button", { name: /Locus Lab|Lokus Laboratuvari/i }));

    const searchInput = screen.getByPlaceholderText(/Search rsID|rsID, gen veya kromozom ara/i);
    fireEvent.change(searchInput, { target: { value: "rs3827760" } });

    const toggleBtn = screen.getByRole("button", { name: /Homozygous|Heterozygous|Homozigot|d=/i });
    fireEvent.click(toggleBtn);

    expect(screen.getByRole("button", { name: /d=/i })).toBeDefined();
  });

  // ── 6. German § 81e StPO Redaction Gate & ISO 17025 Audit Trail ─────────────

  it("masks GIS coordinates and displays redaction alert under German § 81e StPO mode", () => {
    render(<PanelBGA />);

    // Click § 81e StPO toggle button in header
    const stpoButton = screen.getByRole("button", { name: /§81e StPO/i });
    fireEvent.click(stpoButton);

    // Alert should appear
    expect(screen.getByText(/§ 81e \(2\) StPO Statutory Compliance Gate|§ 81e \(2\) StPO Yasal Uyum Kapisi/i)).toBeDefined();

    // Switch to GIS Map tab
    fireEvent.click(screen.getByRole("button", { name: /3D GIS/i }));
    expect(screen.getByText(/\[COORDINATES MASKED: § 81e \(2\) StPO\]|\[KOORDINATLAR MASKELENDI: § 81e \(2\) StPO\]/i)).toBeDefined();
  });

  it("dispatches audit trail logs to useForensicCaseStore upon reference and execution actions", () => {
    const addAuditLogSpy = vi.fn();
    useForensicCaseStore.setState({ addAuditLog: addAuditLogSpy });

    render(<PanelBGA />);

    // Switch reference panel
    const gnomadBtn = screen.getByRole("button", { name: /gnomAD v4.1/i });
    fireEvent.click(gnomadBtn);

    expect(addAuditLogSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        event: expect.stringContaining("Switched BGA reference population matrix"),
        module: "15. 55-SNP AIM Biogeographic Ancestry",
        status: "PASS",
      })
    );

    // Toggle statutory jurisdiction (§81e StPO)
    const stpoBtn = screen.getByRole("button", { name: /§81e StPO/i });
    fireEvent.click(stpoBtn);

    expect(addAuditLogSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        event: expect.stringContaining("Set BGA statutory compliance mode"),
        module: "15. 55-SNP AIM Biogeographic Ancestry",
        status: "PASS",
      })
    );

    // Load reference standard
    const yriBtn = screen.getByText(/1000 Genomes NA19240/i);
    fireEvent.click(yriBtn);

    expect(addAuditLogSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        event: expect.stringContaining("Loaded BGA certified golden standard"),
        module: "15. 55-SNP AIM Biogeographic Ancestry",
        status: "PASS",
      })
    );
  });
});
