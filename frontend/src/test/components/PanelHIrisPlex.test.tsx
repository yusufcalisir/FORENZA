import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import PanelHIrisPlex, {
  computeHIrisPlexEye,
  computeHIrisPlexHair,
  computeHIrisPlexSkin,
  computeHIrisPlexMorphology,
  evaluateFullHIrisPlex,
  HIRISPLEX_41_REGISTRY,
  GOLDEN_STANDARDS,
} from "@/components/analysis/PanelHIrisPlex";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

describe("Subsystem 14: HIrisPlex-S 41-SNP Forensic DNA Pigmentation & Phenotyping Studio", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── 1. Pure Biocomputational Formulation & Simplex Invariants ───────────────

  it("enforces multinomial probability simplex sum-to-one invariant for eye color", () => {
    const testCases: Record<string, number>[] = [
      {},
      { rs12913832: 2, rs16891982: 2, rs1426654: 2 },
      { rs12913832: 0, rs1800407: 0, rs1800414: 2 },
      { rs12913832: 1, rs1800407: 1, rs12896399: 1, rs1393350: 1 },
    ];

    for (const snps of testCases) {
      const res = computeHIrisPlexEye(snps);
      const sumP = res.blue + res.intermediate + res.brown;
      expect(Math.abs(sumP - 100.0)).toBeLessThan(1e-4);
      expect(res.blue).toBeGreaterThanOrEqual(0.0);
      expect(res.intermediate).toBeGreaterThanOrEqual(0.0);
      expect(res.brown).toBeGreaterThanOrEqual(0.0);
    }
  });

  it("verifies monotonic Blue eye probability increase with HERC2 rs12913832 effect allele dosage", () => {
    const d0 = computeHIrisPlexEye({ rs12913832: 0 });
    const d1 = computeHIrisPlexEye({ rs12913832: 1 });
    const d2 = computeHIrisPlexEye({ rs12913832: 2 });

    expect(d0.blue).toBeLessThan(10.0);
    expect(d1.blue).toBeGreaterThan(d0.blue);
    expect(d2.blue).toBeGreaterThan(85.0);
    expect(d0.brown).toBeGreaterThan(d2.brown);
  });

  it("enforces hair color 4-category simplex invariant and responds to MC1R loss-of-function variants", () => {
    const base = computeHIrisPlexHair({});
    const sumBase = base.blond + base.brown + base.red + base.black;
    expect(Math.abs(sumBase - 100.0)).toBeLessThan(1e-4);

    // Primary MC1R R151C (rs1805007) loss-of-function drives red hair
    const redHet = computeHIrisPlexHair({ rs1805007: 1 });
    const redHom = computeHIrisPlexHair({ rs1805007: 2 });
    expect(redHet.red).toBeGreaterThan(base.red);
    expect(redHom.red).toBeGreaterThan(85.0);

    // Secondary MC1R alleles (rs1805006 R142H and rs885479 I155T) also increase red hair
    const r142h = computeHIrisPlexHair({ rs1805006: 2 });
    expect(r142h.red).toBeGreaterThan(base.red);

    const i155t = computeHIrisPlexHair({ rs885479: 2 });
    expect(i155t.red).toBeGreaterThan(base.red);

    // Nonsense null allele Y152X (rs28936415)
    const y152x = computeHIrisPlexHair({ rs28936415: 2 });
    expect(y152x.red).toBeGreaterThan(base.red);

    // Hair shade binomial invariant: Light + Dark = 100%
    expect(Math.abs(base.pLightShade + base.pDarkShade - 100.0)).toBeLessThan(1e-4);
    expect(Math.abs(redHom.pLightShade + redHom.pDarkShade - 100.0)).toBeLessThan(1e-4);
  });

  it("enforces skin phototype 5-category simplex invariant across light and dark genetic profiles", () => {
    // Fair European phototype (SLC24A5 + SLC45A2 dosage 2)
    const fair = computeHIrisPlexSkin({ rs1426654: 2, rs16891982: 2, rs12913832: 2 });
    const sumFair = fair.veryPale + fair.pale + fair.intermediate + fair.dark + fair.darkToBlack;
    expect(Math.abs(sumFair - 100.0)).toBeLessThan(1e-4);
    expect(fair.veryPale + fair.pale).toBeGreaterThan(80.0);

    // Dark African phototype (MFSD12 + ACKR1 dosage 2)
    const dark = computeHIrisPlexSkin({ rs10424031: 2, rs2814778: 2 });
    const sumDark = dark.veryPale + dark.pale + dark.intermediate + dark.dark + dark.darkToBlack;
    expect(Math.abs(sumDark - 100.0)).toBeLessThan(1e-4);
    expect(dark.dark + dark.darkToBlack).toBeGreaterThan(80.0);
  });

  it("evaluates hair morphology with multinomial logistic regression based on EDAR, TCHH, and ACKR1", () => {
    // Ancestral profile
    const ancestral = computeHIrisPlexMorphology({});
    const sumAncestral = ancestral.straight + ancestral.wavy + ancestral.curly;
    expect(Math.abs(sumAncestral - 100.0)).toBeLessThan(1e-4);

    // East Asian EDAR 370A homozygous (rs3827760: 2) -> Thick Straight
    const asianStraight = computeHIrisPlexMorphology({ rs3827760: 2 });
    expect(asianStraight.straight).toBeGreaterThan(95.0);
    expect(asianStraight.curly).toBeLessThan(2.0);

    // Sub-Saharan African TCHH (rs11803731: 2) + ACKR1 (rs2814778: 2) -> Curly/Coily
    const africanCurly = computeHIrisPlexMorphology({ rs11803731: 2, rs2814778: 2 });
    expect(africanCurly.curly).toBeGreaterThan(90.0);
    expect(africanCurly.straight).toBeLessThan(2.0);
  });

  it("evaluates full composite HIrisPlex pipeline through evaluateFullHIrisPlex", () => {
    const full = evaluateFullHIrisPlex({
      rs12913832: 2,
      rs16891982: 2,
      rs1426654: 2,
      rs3827760: 0,
      rs11803731: 0,
    });

    expect(full.eye.blue).toBeGreaterThan(85.0);
    expect(full.hair.blond).toBeGreaterThan(50.0);
    expect(full.skin.veryPale + full.skin.pale).toBeGreaterThan(70.0);
    expect(full.morph.straight).toBeGreaterThan(45.0);
  });

  // ── 2. Certified Golden Standards Concordance ───────────────────────────────

  it("verifies NA12878 Utah European fair phototype golden standard concordance", () => {
    const na12878 = GOLDEN_STANDARDS.find((s) => s.id === "NA12878_CEU_EUROPEAN")!;
    expect(na12878).toBeDefined();

    const pred = evaluateFullHIrisPlex(na12878.genotypes);
    expect(pred.eye.blue).toBeGreaterThan(85.0);
    expect(pred.hair.blond).toBeGreaterThan(60.0);
    expect(pred.skin.veryPale + pred.skin.pale).toBeGreaterThan(75.0);
  });

  it("verifies NA19240 Sub-Saharan African ancestral dark phototype standard concordance", () => {
    const na19240 = GOLDEN_STANDARDS.find((s) => s.id === "NA19240_YRI_AFRICAN")!;
    expect(na19240).toBeDefined();

    const pred = evaluateFullHIrisPlex(na19240.genotypes);
    expect(pred.eye.brown).toBeGreaterThan(70.0);
    expect(pred.hair.black).toBeGreaterThan(70.0);
    expect(pred.skin.dark + pred.skin.darkToBlack).toBeGreaterThan(80.0);
    expect(pred.morph.curly).toBeGreaterThan(85.0);
  });

  it("verifies Celtic red hair reference standard concordance with compound MC1R loss-of-function", () => {
    const celtic = GOLDEN_STANDARDS.find((s) => s.id === "CELTIC_RED_HAIR_STANDARD")!;
    expect(celtic).toBeDefined();

    const pred = evaluateFullHIrisPlex(celtic.genotypes);
    expect(pred.eye.blue).toBeGreaterThan(80.0);
    expect(pred.hair.red).toBeGreaterThan(85.0);
    expect(pred.skin.veryPale).toBeGreaterThan(60.0);
  });

  it("verifies HG005 East Asian ancestral phototype standard concordance", () => {
    const hg005 = GOLDEN_STANDARDS.find((s) => s.id === "HG005_CHB_EAST_ASIAN")!;
    expect(hg005).toBeDefined();

    const pred = evaluateFullHIrisPlex(hg005.genotypes);
    expect(pred.eye.brown).toBeGreaterThan(60.0);
    expect(pred.hair.black).toBeGreaterThan(50.0);
    expect(pred.morph.straight).toBeGreaterThan(95.0);
  });

  // ── 3. Component UI & Interactive State Tests ───────────────────────────────

  it("renders the tactical command header, badge, and default tab contents", () => {
    render(<PanelHIrisPlex />);

    expect(screen.getByText(/HIrisPlex-S 41-SNP/i)).toBeDefined();
    expect(screen.getAllByText(/WALSH ET AL. \(2018\)/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/ISO 17025 VALIDATED/i)).toBeDefined();
    expect(screen.getByText(/5 GLOBAL STANDARDS LOADED/i)).toBeDefined();
  });

  it("switches across all 5 navigation tabs cleanly", () => {
    render(<PanelHIrisPlex />);

    // Switch to Eye tab
    const eyeTabBtn = screen.getByRole("button", { name: /İris Rengi|Eye Pigment/i });
    fireEvent.click(eyeTabBtn);
    expect(screen.getByText(/IrisPlex 6-Lokus Çok Terimli|IrisPlex 6-Loci/i)).toBeDefined();

    // Switch to Hair tab
    const hairTabBtn = screen.getByRole("button", { name: /Saç & Ton|Hair & Shade/i });
    fireEvent.click(hairTabBtn);
    expect(screen.getByText(/HIrisPlex 22-Lokus Saç Rengi|HIrisPlex 22-Loci/i)).toBeDefined();

    // Switch to Skin tab
    const skinTabBtn = screen.getByRole("button", { name: /Ten Fototipi|Skin Phototype/i });
    fireEvent.click(skinTabBtn);
    expect(screen.getByText(/HIrisPlex-S Fitzpatrick|Fitzpatrick Skin/i)).toBeDefined();

    // Switch to Compliance tab
    const compTabBtn = screen.getByRole("button", { name: /41-SNP & Hukuk|41-SNP & Shield/i });
    fireEvent.click(compTabBtn);
    expect(screen.getByText(/41-SNP Genotip Dozaj Matrisi|41-SNP Genotype Dosage Matrix/i)).toBeDefined();

    // Switch back to Benchmarks tab
    const benchTabBtn = screen.getByRole("button", { name: /Altın Standartlar|Golden Standards/i });
    fireEvent.click(benchTabBtn);
    expect(screen.getByText(/5 GLOBAL STANDARDS LOADED/i)).toBeDefined();
  });

  it("loads a golden reference standard and dispatches audit log to forensicCaseStore", () => {
    render(<PanelHIrisPlex />);

    // Click African standard
    const yriCard = screen.getByText(/1000G NA19240/i);
    fireEvent.click(yriCard);

    // Verify audit log dispatch
    const state = useForensicCaseStore.getState();
    const auditLogs = state.auditTrail;
    const hasLog = auditLogs.some((l) => l.event.includes("Loaded standard reference profile"));
    expect(hasLog).toBe(true);
  });

  it("toggles SNP dosage in compliance tab, recalculates probabilities, and logs mutation", () => {
    render(<PanelHIrisPlex />);

    // Go to compliance tab
    const compTabBtn = screen.getByRole("button", { name: /41-SNP & Hukuk|41-SNP & Shield/i });
    fireEvent.click(compTabBtn);

    // Find HERC2 rs12913832 card and click it
    const herc2Card = screen.getByText("rs12913832");
    fireEvent.click(herc2Card);

    // Verify audit log has mutated SNP record
    const state = useForensicCaseStore.getState();
    const auditLogs = state.auditTrail;
    const hasMutationLog = auditLogs.some((l) => l.event.includes("Mutated SNP rs12913832 dosage"));
    expect(hasMutationLog).toBe(true);
  });

  it("filters the 41-SNP registry by search query and domain filter", () => {
    render(<PanelHIrisPlex />);

    // Go to compliance tab
    const compTabBtn = screen.getByRole("button", { name: /41-SNP & Hukuk|41-SNP & Shield/i });
    fireEvent.click(compTabBtn);

    const searchInput = screen.getByPlaceholderText(/rsID veya Gen ara|Search rsID or Gene/i);
    fireEvent.change(searchInput, { target: { value: "MC1R" } });

    // Should see MC1R entries and not unrelated genes
    expect(screen.getAllByText(/MC1R/i).length).toBeGreaterThan(0);

    // Filter by Eye domain button
    const eyeFilterBtn = screen.getByRole("button", { name: /^Eye$/i });
    fireEvent.click(eyeFilterBtn);

    // MC1R is Hair domain, so with Eye filter + MC1R search, it should be empty
    expect(screen.queryByText("rs1805007")).toBeNull();

    // Reset search
    fireEvent.change(searchInput, { target: { value: "" } });
    expect(screen.getByText("rs12913832")).toBeDefined();
  });

  it("copies evaluative reporting shield and logs audit trail event", () => {
    render(<PanelHIrisPlex />);

    // Go to compliance tab
    const compTabBtn = screen.getByRole("button", { name: /41-SNP & Hukuk|41-SNP & Shield/i });
    fireEvent.click(compTabBtn);

    const copyBtn = screen.getByRole("button", { name: /Raporu Kopyala|Copy Statement/i });
    fireEvent.click(copyBtn);

    expect(navigator.clipboard.writeText).toHaveBeenCalled();
    const state = useForensicCaseStore.getState();
    const auditLogs = state.auditTrail;
    const hasCopyLog = auditLogs.some((l) => l.event.includes("Copied ISFG/VISAGE"));
    expect(hasCopyLog).toBe(true);
  });

  it("contains all 41 SNPs in HIRISPLEX_41_REGISTRY with valid annotations", () => {
    expect(HIRISPLEX_41_REGISTRY.length).toBe(41);
    for (const snp of HIRISPLEX_41_REGISTRY) {
      expect(snp.rsid).toMatch(/^rs\d+$/);
      expect(snp.gene.length).toBeGreaterThan(0);
      expect(["Eye", "Hair", "Skin", "Morphology", "Modifier"]).toContain(snp.primaryDomain);
      expect(snp.effectAllele.length).toBeGreaterThan(0);
      expect(snp.roleEn.length).toBeGreaterThan(0);
      expect(snp.roleTr.length).toBeGreaterThan(0);
    }
  });
});
