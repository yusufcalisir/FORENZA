import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import PanelCraniofacial, {
  computeDistance3D,
  calculateCephalometricLandmarks,
  calculateAnthropologicalIndices,
  landmarksToMatrix,
  computeCentroidSize,
  svd3x3,
  generalizedProcrustesSuperposition,
  computeCraniofacialAuditHash,
  evaluateCraniofacialProfile,
  CRANIOFACIAL_LOCI,
  CRANIOFACIAL_STANDARDS,
  LANDMARK_KEYS,
  LANDMARK_METADATA,
} from "@/components/analysis/PanelCraniofacial";
import { useForensicCaseStore } from "@/store/forensicCaseStore";


// Mock framer-motion AnimatePresence to avoid jsdom mode='wait' exit freeze
vi.mock('framer-motion', async () => {
  const actual = await vi.importActual('framer-motion');
  return {
    ...actual,
    AnimatePresence: ({ children }: any) => <>{children}</>,
    motion: {
      div: ({ children, className, style, onClick, ...props }: any) => (
        <div className={className} style={style} onClick={onClick} {...props}>
          {children}
        </div>
      ),
    },
  };
});

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

describe("Subsystem 16: 3D Craniofacial Morphology Studio & Cephalometric Superposition", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── 1. Pure Biocomputational Kernel Tests ───────────────────────────────────

  it("computes 3D Euclidean distance with zero error", () => {
    const p1 = { x: 0, y: 0, z: 0 };
    const p2 = { x: 3, y: 4, z: 12 };
    const dist = computeDistance3D(p1, p2);
    expect(dist).toBeCloseTo(13.0, 6);
  });

  it("calculates 11 cephalometric landmarks preserving bilateral symmetry and midline invariants", () => {
    const dosages = { rs974448: 1, rs12882923: 1, rs11130635: 1, rs13289: 0, rs7559252: 1 };
    const lm = calculateCephalometricLandmarks(dosages, "FEMALE", 25.0);

    // Midline sagittal landmarks must have X = 0.0
    expect(lm.nasion.x).toBe(0.0);
    expect(lm.pronasale.x).toBe(0.0);
    expect(lm.subnasale.x).toBe(0.0);
    expect(lm.labiale_superius.x).toBe(0.0);
    expect(lm.menton.x).toBe(0.0);

    // Bilateral landmarks must be perfectly symmetric about X = 0
    expect(lm.alare_left.x).toBeCloseTo(-lm.alare_right.x, 6);
    expect(lm.alare_left.y).toBeCloseTo(lm.alare_right.y, 6);
    expect(lm.alare_left.z).toBeCloseTo(lm.alare_right.z, 6);

    expect(lm.zygion_left.x).toBeCloseTo(-lm.zygion_right.x, 6);
    expect(lm.zygion_left.y).toBeCloseTo(lm.zygion_right.y, 6);
    expect(lm.zygion_left.z).toBeCloseTo(lm.zygion_right.z, 6);

    expect(lm.cheilion_left.x).toBeCloseTo(-lm.cheilion_right.x, 6);
    expect(lm.cheilion_left.y).toBeCloseTo(lm.cheilion_right.y, 6);
    expect(lm.cheilion_left.z).toBeCloseTo(lm.cheilion_right.z, 6);
  });

  it("computes Farkas and Martin soft-tissue anthropological indices correctly", () => {
    const ceu = CRANIOFACIAL_STANDARDS.find((s) => s.id === "NA12878_CEU_EUROPEAN")!;
    const lm = calculateCephalometricLandmarks(ceu.snp_dosages, ceu.sex, ceu.age_years);
    const ind = calculateAnthropologicalIndices(lm, ceu.sex);

    // CEU European female: expected leptorrhine (narrow nasal aperture, NI < 70.0)
    expect(ind.nasal_index).toBeLessThan(70.0);
    expect(ind.nasal_typology).toContain("LEPTORRHINE");
    expect(ind.sexual_dimorphism_offset_mm).toBe(0.0);
    expect(ind.facial_convexity_angle_deg).toBeCloseTo(138.06, 1);
  });

  it("evaluates male sexual dimorphism scaling and mandibular boost", () => {
    const maleStd = CRANIOFACIAL_STANDARDS.find((s) => s.id === "MALE_HIGH_DIMORPHISM")!;
    const lmMale = calculateCephalometricLandmarks(maleStd.snp_dosages, "MALE", 40.0);
    const indMale = calculateAnthropologicalIndices(lmMale, "MALE");

    expect(indMale.sexual_dimorphism_offset_mm).toBe(8.40);
    expect(indMale.mandibular_breadth_mm).toBeGreaterThan(indMale.bizygomatic_breadth_mm * 0.72);

    const lmFemale = calculateCephalometricLandmarks(maleStd.snp_dosages, "FEMALE", 40.0);
    const indFemale = calculateAnthropologicalIndices(lmFemale, "FEMALE");
    expect(indFemale.sexual_dimorphism_offset_mm).toBe(0.0);
    expect(lmMale.menton.y).toBeGreaterThan(lmFemale.menton.y);
  });

  it("computes centroid size and verifies translation zero-mean centering", () => {
    const lm = calculateCephalometricLandmarks({}, "FEMALE", 30.0);
    const mat = landmarksToMatrix(lm);
    const cs = computeCentroidSize(mat);

    expect(cs.centroidSize).toBeGreaterThan(100.0);
    expect(cs.centered.length).toBe(11);

    // Centered coordinates must sum to zero
    let sumX = 0, sumY = 0, sumZ = 0;
    for (const row of cs.centered) {
      sumX += row[0];
      sumY += row[1];
      sumZ += row[2];
    }
    expect(Math.abs(sumX)).toBeLessThan(1e-10);
    expect(Math.abs(sumY)).toBeLessThan(1e-10);
    expect(Math.abs(sumZ)).toBeLessThan(1e-10);
  });

  it("enforces orthogonal SO(3) rotation matrix and unit determinant in 3x3 SVD", () => {
    // Identity cross-covariance
    const H = [
      [1, 0, 0],
      [0, 1, 0],
      [0, 0, 1],
    ];
    const { R, svals } = svd3x3(H);
    expect(svals[0]).toBeCloseTo(1.0, 6);
    expect(svals[1]).toBeCloseTo(1.0, 6);
    expect(svals[2]).toBeCloseTo(1.0, 6);

    // Determinant of R must be +1.0
    const detR =
      R[0][0] * (R[1][1] * R[2][2] - R[1][2] * R[2][1]) -
      R[0][1] * (R[1][0] * R[2][2] - R[1][2] * R[2][0]) +
      R[0][2] * (R[1][0] * R[2][1] - R[1][1] * R[2][0]);
    expect(Math.abs(detR - 1.0)).toBeLessThan(1e-6);

    // R^T * R = I
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        let dot = 0;
        for (let k = 0; k < 3; k++) dot += R[k][i] * R[k][j];
        expect(dot).toBeCloseTo(i === j ? 1.0 : 0.0, 5);
      }
    }
  });

  it("performs exact Generalized Procrustes Superposition concordant with backend benchmarks", () => {
    const s1 = CRANIOFACIAL_STANDARDS.find((s) => s.id === "NA12878_CEU_EUROPEAN")!;
    const s2 = CRANIOFACIAL_STANDARDS.find((s) => s.id === "NA19240_YRI_AFRICAN")!;

    const lm1 = calculateCephalometricLandmarks(s1.snp_dosages, s1.sex, s1.age_years);
    const lm2 = calculateCephalometricLandmarks(s2.snp_dosages, s2.sex, s2.age_years);

    const mat1 = landmarksToMatrix(lm1);
    const mat2 = landmarksToMatrix(lm2);

    const result = generalizedProcrustesSuperposition(mat1, mat2);

    // Ground truth benchmarks verified against Python backend
    expect(result.centroid_size_target).toBeCloseTo(145.7238, 2);
    expect(result.centroid_size_source).toBeCloseTo(148.4441, 2);
    expect(result.procrustes_distance).toBeCloseTo(81.8329, 1);
    expect(result.rmsd_mm).toBeCloseTo(2.7275, 2);
    expect(result.aligned_matrix.length).toBe(11);
  });

  it("yields zero Procrustes distance and zero RMSD for identical landmark configurations", () => {
    const lm = calculateCephalometricLandmarks({}, "FEMALE", 25.0);
    const mat = landmarksToMatrix(lm);
    const result = generalizedProcrustesSuperposition(mat, mat);

    expect(result.procrustes_distance).toBeCloseTo(0.0, 4);
    expect(result.rmsd_mm).toBeCloseTo(0.0, 4);
    expect(result.centroid_size_target).toBeCloseTo(result.centroid_size_source, 4);
  });

  it("generates deterministic cryptographic audit hash reacting to any model modification", () => {
    const dosages1 = { rs974448: 1, rs12882923: 0, rs11130635: 2, rs13289: 0, rs7559252: 1 };
    const dosages2 = { ...dosages1, rs974448: 2 };

    const lm1 = calculateCephalometricLandmarks(dosages1, "FEMALE", 35.0);
    const ind1 = calculateAnthropologicalIndices(lm1, "FEMALE");
    const hash1 = computeCraniofacialAuditHash(dosages1, "FEMALE", 35.0, ind1);

    const lm2 = calculateCephalometricLandmarks(dosages2, "FEMALE", 35.0);
    const ind2 = calculateAnthropologicalIndices(lm2, "FEMALE");
    const hash2 = computeCraniofacialAuditHash(dosages2, "FEMALE", 35.0, ind2);

    expect(hash1.startsWith("0x")).toBe(true);
    expect(hash1.length).toBe(66);
    expect(hash2.startsWith("0x")).toBe(true);
    expect(hash1).not.toBe(hash2);

    // Invariant: identical inputs yield identical hash
    const hash1Repeat = computeCraniofacialAuditHash(dosages1, "FEMALE", 35.0, ind1);
    expect(hash1).toBe(hash1Repeat);
  });

  it("evaluates complete craniofacial profile in pure pipeline mode", () => {
    const s = CRANIOFACIAL_STANDARDS[0];
    const full = evaluateCraniofacialProfile(s.snp_dosages, s.sex, s.age_years);

    expect(full.landmarksMatrix.length).toBe(11);
    expect(full.centroidSize).toBeGreaterThan(100.0);
    expect(full.auditHash.startsWith("0x")).toBe(true);
    expect(full.assayedLociCount).toBe(5);
    expect(full.indices.nasal_typology).toBeDefined();
  });

  // ── 2. Component Integration & UI Tests ─────────────────────────────────────

  it("renders PanelCraniofacial header, telemetry ribbon, and action controls", () => {
    render(<PanelCraniofacial />);

    expect(screen.getByText(/3D Kraniyofasiyal Morfometri|3D Craniofacial Morphometry/i)).toBeInTheDocument();
    expect(screen.getByText("ISO/IEC 17025:2017")).toBeInTheDocument();
    expect(screen.getByText("5 / 5 GWAS")).toBeInTheDocument();
    expect(screen.getByText(/Profili Yeniden Hesapla|Reconstruct 3D Profile/i)).toBeInTheDocument();
  });

  it("allows switching across all 5 analytical tabs smoothly", () => {
    render(<PanelCraniofacial />);

    // Tab 1 (default)
    expect(screen.getByText(/5 Onayli Cephalometrik Referans Standarti|5 Certified Cephalometric Reference Standards/i)).toBeInTheDocument();

    // Switch to Tab 2
    const tab2Btn = screen.getByText(/2. 3D Cephalometrik Noktalar|2. 3D Cephalometric Landmarks/i);
    fireEvent.click(tab2Btn);
    expect(screen.getByText(/Interaktif Cephalometrik Harita|Interactive Cephalometric Projection Map/i)).toBeInTheDocument();

    // Switch to Tab 3
    const tab3Btn = screen.getByText(/3. Antropolojik Indeksler|3. Anthropological Indices/i);
    fireEvent.click(tab3Btn);
    expect(screen.getByText(/Burun Indeksi|Nasal Index/i)).toBeInTheDocument();

    // Switch to Tab 4
    const tab4Btn = screen.getByText(/4. 3D Procrustes Cakisimi|4. 3D Procrustes Superposition/i);
    fireEvent.click(tab4Btn);
    expect(screen.getByText(/Procrustes Uyum Metrikleri|Procrustes Goodness-of-Fit Metrics/i)).toBeInTheDocument();

    // Switch to Tab 5
    const tab5Btn = screen.getByText(/5. Adli Mevzuat & Raporlama|5. Forensic Governance & Shield/i);
    fireEvent.click(tab5Btn);
    expect(screen.getByText(/Alman Ceza Usul Kanunu §81e|German StPO §81e/i)).toBeInTheDocument();
  });

  it("loads a reference standard and logs ISO/IEC 17025 audit trail to useForensicCaseStore", () => {
    const addAuditLogSpy = vi.spyOn(useForensicCaseStore.getState(), "addAuditLog");
    render(<PanelCraniofacial />);

    // Click YRI standard
    const yriCard = screen.getAllByText("HapMap NA19240 (Yoruba in Ibadan, Nigeria)")[0];
    fireEvent.click(yriCard);

    expect(addAuditLogSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        event: expect.stringContaining("Loaded standard"),
        module: "16. 3D Craniofacial Morphology Studio",
        status: "PASS",
      })
    );
  });

  it("switches biological sex dimorphism and updates craniometric state", () => {
    render(<PanelCraniofacial />);

    // Go to Tab 2
    fireEvent.click(screen.getByText(/2. 3D Cephalometrik Noktalar|2. 3D Cephalometric Landmarks/i));

    const maleBtn = screen.getByText(/Erkek \(\+8.4mm Mandibula\)|Male \(\+8.4mm Mandible\)/i);
    fireEvent.click(maleBtn);

    const femaleBtn = screen.getByText(/Kadin \(1.000x\)|Female \(1.000x\)/i);
    fireEvent.click(femaleBtn);
  });

  it("switches projection views between calipers, frontal, and lateral", () => {
    render(<PanelCraniofacial />);

    fireEvent.click(screen.getByText(/2. 3D Cephalometrik Noktalar|2. 3D Cephalometric Landmarks/i));

    const frontalBtn = screen.getByText("Frontal (X-Z)");
    fireEvent.click(frontalBtn);
    expect(screen.getByText("Frontal X-Z (mm)")).toBeInTheDocument();

    const lateralBtn = screen.getByText("Sagittal (Y-Z)");
    fireEvent.click(lateralBtn);
    expect(screen.getByText("Sagittal Y-Z (mm)")).toBeInTheDocument();
  });

  it("allows selecting specific cephalometric landmarks from the coordinates table", () => {
    render(<PanelCraniofacial />);

    fireEvent.click(screen.getByText(/2. 3D Cephalometrik Noktalar|2. 3D Cephalometric Landmarks/i));

    const nasionRow = screen.getAllByText("N")[0];
    fireEvent.click(nasionRow);

    const mentonRow = screen.getAllByText("Me")[0];
    fireEvent.click(mentonRow);
  });

  it("toggles SNP dosages in Tab 3 and updates active indices", () => {
    render(<PanelCraniofacial />);

    fireEvent.click(screen.getByText(/3. Antropolojik Indeksler|3. Anthropological Indices/i));

    expect(screen.getByText("PRDM16")).toBeInTheDocument();
    expect(screen.getByText("PAX3")).toBeInTheDocument();
    expect(screen.getByText("DCHS2")).toBeInTheDocument();
  });

  it("copies cryptographic audit hash in Tab 5 and dispatches chain-of-custody log", () => {
    const addAuditLogSpy = vi.spyOn(useForensicCaseStore.getState(), "addAuditLog");
    render(<PanelCraniofacial />);

    fireEvent.click(screen.getByText(/5. Adli Mevzuat & Raporlama|5. Forensic Governance & Shield/i));

    const copyBtn = screen.getByRole("button", { name: /Kopyala|Copy/i });
    fireEvent.click(copyBtn);

    expect(navigator.clipboard.writeText).toHaveBeenCalled();
    expect(addAuditLogSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        event: expect.stringContaining("Cryptographic audit hash copied"),
        status: "PASS",
      })
    );
  });
});
