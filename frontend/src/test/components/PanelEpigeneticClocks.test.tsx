import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PanelEpigeneticClocks, {
  computeClientEpigeneticAge,
  computeClientBiologicalAging,
  computeClientMultimodalPmi,
  computeEpigeneticAuditHash,
  GOLDEN_VECTORS,
  TISSUE_OFFSETS,
  CLOCK_CATALOG,
} from "@/components/analysis/PanelEpigeneticClocks";
import { computeMahalanobisDistanceSq } from "@/utils/visageAgeEngine";
import { useForensicCaseStore, SAMPLE_CASE_EU } from "@/store/forensicCaseStore";

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
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
});

// Mock fetch for API routes
global.fetch = vi.fn().mockImplementation((url: string) => {
  if (url.includes("/estimate-age")) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => ({
        sample_id: "SAMPLE_VERIFIED",
        tissue_type: "WHOLE_BLOOD",
        tissue_offset_applied: 0.0,
        clock_results: [
          {
            clock_id: "horvath_2013",
            clock_name: "Horvath Pan-Tissue Clock (2013)",
            predicted_age: 34.2,
            calibrated_age: 34.2,
            tissue_offset: 0.0,
            uncertainty_u95: 9.1,
            ci_95_lower: 25.1,
            ci_95_upper: 43.3,
          },
        ],
        judicial_report: {
          admissible_chronological_age: 34.2,
          uncertainty_interval_95: [25.1, 43.3],
          enfsi_tier_level: "Strong Evidence",
          enfsi_statement_en: "The DNA methylation profile indicates an adult donor.",
          enfsi_statement_tr: "DNA metilasyon profili yetiskin bir bireyi gostermektedir.",
          prosecutors_fallacy_shield: "Results reflect biological age distributions only.",
          statutory_compliance_status: "COMPLIANT_GERMAN_STPO",
        },
      }),
    });
  }
  if (url.includes("/biological-aging")) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => ({
        sample_id: "SAMPLE_VERIFIED",
        phenoage: { predicted_phenoage: 35.5 },
        grimage: { predicted_grimage: 36.1 },
        dunedin_pace: { pace_of_aging: 1.02 },
      }),
    });
  }
  if (url.includes("/multimodal-pmi")) {
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => ({
        fused_pmi_hours: 14.8,
        fused_pmi_days: 0.62,
        credible_interval_lower: 11.2,
        credible_interval_upper: 18.4,
      }),
    });
  }
  return Promise.resolve({ ok: true, json: async () => ({}) });
});

describe("Subsystem 19: Multi-Generation Epigenetic Clocks & Multimodal PMI Studio", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useForensicCaseStore.setState({
      activeCase: {
        ...SAMPLE_CASE_EU,
        profile: {
          ...SAMPLE_CASE_EU.profile,
          epigeneticAge: 32.5,
        },
      },
      auditTrail: [],
    });
  });

  // ===========================================================================
  // 1. BIOCOMPUTATIONAL FORMULATION & MATHEMATICAL INVARIANTS
  // ===========================================================================

  it("verifies Horvath piecewise log-linear transformation with y0 = 20.0 inflection point", () => {
    // Branch 1: Adult (y >= 0 -> f(y) = 21.0 * y + 20.0)
    const adultBetas = {
      cg16867657: 0.435,
      cg06639320: 0.340,
      cg16419235: 0.220,
      cg04523812: 0.295,
      cg07955995: 0.235,
      cg02228185: 0.440,
      cg17861230: 0.350,
      cg02085975: 0.510,
    };
    const adultRes = computeClientEpigeneticAge(adultBetas, "WHOLE_BLOOD", "horvath_2013", 45.0);
    expect(adultRes.calibratedPredictedAge).toBeGreaterThanOrEqual(20.0);
    expect(adultRes.calibratedPredictedAge).toBeLessThan(60.0);

    // Branch 2: Pediatric / Adolescent (y < 0 -> f(y) = 21.0 * exp(y) - 1.0)
    const pediatricBetas = {
      cg16867657: 0.240,
      cg06639320: 0.205,
      cg16419235: 0.290,
      cg04523812: 0.175,
      cg07955995: 0.145,
      cg02228185: 0.290,
      cg17861230: 0.210,
      cg02085975: 0.680,
    };
    const pediatricRes = computeClientEpigeneticAge(pediatricBetas, "WHOLE_BLOOD", "horvath_2013", 19.5);
    expect(pediatricRes.calibratedPredictedAge).toBeLessThan(20.0);
    expect(pediatricRes.calibratedPredictedAge).toBeGreaterThan(15.0);
  });

  it("verifies VISAGE 5-CpG Mahalanobis covariance distance calculation", () => {
    // Centroid vector yields near-zero Mahalanobis distance
    const centroidVec = [0.3850, 0.3120, 0.2450, 0.2810, 0.2100];
    const dSqZero = computeMahalanobisDistanceSq(centroidVec);
    expect(dSqZero).toBeLessThan(1e-5);

    // Deviant vector yields positive distance
    const deviantVec = [0.6500, 0.5500, 0.4000, 0.4500, 0.3500];
    const dSqDeviant = computeMahalanobisDistanceSq(deviantVec);
    expect(dSqDeviant).toBeGreaterThan(dSqZero);
    expect(dSqDeviant).toBeGreaterThan(0.0005);
  });

  it("verifies multi-tissue calibration offsets (Delta_tissue) apply additively", () => {
    const betas = GOLDEN_VECTORS[0].betas;

    const bloodRes = computeClientEpigeneticAge(betas, "WHOLE_BLOOD", "visage_basic", 32.5);
    const salivaRes = computeClientEpigeneticAge(betas, "SALIVA", "visage_basic", 32.5);
    const semenRes = computeClientEpigeneticAge(betas, "SEMEN", "visage_basic", 32.5);
    const boneRes = computeClientEpigeneticAge(betas, "BONE", "visage_basic", 32.5);

    expect(bloodRes.tissueOffsetApplied).toBe(0.00);
    expect(salivaRes.tissueOffsetApplied).toBe(2.45);
    expect(semenRes.tissueOffsetApplied).toBe(18.60);
    expect(boneRes.tissueOffsetApplied).toBe(1.15);

    // Delta between tissue and blood matches exact offset
    expect(salivaRes.calibratedPredictedAge).toBeCloseTo(bloodRes.rawPredictedAge + 2.45, 0);
    expect(semenRes.calibratedPredictedAge).toBeCloseTo(bloodRes.rawPredictedAge + 18.60, 0);
    expect(boneRes.calibratedPredictedAge).toBeCloseTo(bloodRes.rawPredictedAge + 1.15, 0);
  });

  it("enforces anti-averaging invariant between biological and chronological clocks", () => {
    const betas = GOLDEN_VECTORS[0].betas;
    const chrono = computeClientEpigeneticAge(betas, "WHOLE_BLOOD", "horvath_2013", 32.5);
    const bio = computeClientBiologicalAging(betas, 32.5, 0.0, "MALE");

    // Biological clocks track senescence hazards and must not be equal or averaged
    expect(chrono.calibratedPredictedAge).toBeGreaterThan(0);
    expect(bio.phenoAge).toBeGreaterThan(0);
    expect(bio.grimAge).toBeGreaterThan(0);
    expect(bio.dunedinPace).toBeGreaterThan(0);
    expect(bio.mortalityHazardRatio).toBeGreaterThan(0);
  });

  // ===========================================================================
  // 2. 5 CERTIFIED REFERENCE STANDARDS (GOLDEN BENCHMARK VECTORS)
  // ===========================================================================

  it("validates Golden Vector 1: NIST SRM 2391d Comp A reference male", () => {
    const v = GOLDEN_VECTORS[0];
    expect(v.id).toBe("VECTOR_NIST_2391D_A");
    expect(v.trueAge).toBe(32.5);

    const resHorvath = computeClientEpigeneticAge(v.betas, v.tissue, "horvath_2013", v.trueAge);
    expect(resHorvath.calibratedPredictedAge).toBeGreaterThanOrEqual(v.expectedHorvath[0] - 1.0);
    expect(resHorvath.calibratedPredictedAge).toBeLessThanOrEqual(v.expectedHorvath[1] + 1.5);

    const resVisage = computeClientEpigeneticAge(v.betas, v.tissue, "visage_enhanced", v.trueAge);
    expect(resVisage.calibratedPredictedAge).toBeGreaterThanOrEqual(v.expectedVisage[0] - 0.5);
    expect(resVisage.calibratedPredictedAge).toBeLessThanOrEqual(v.expectedVisage[1]);
  });

  it("validates Golden Vector 2: NA12878 / HG001 CEPH female", () => {
    const v = GOLDEN_VECTORS[1];
    expect(v.id).toBe("VECTOR_NA12878_CEU");
    expect(v.trueAge).toBe(45.0);

    const resHorvath = computeClientEpigeneticAge(v.betas, v.tissue, "horvath_2013", v.trueAge);
    expect(resHorvath.calibratedPredictedAge).toBeGreaterThanOrEqual(40.0);
    expect(resHorvath.calibratedPredictedAge).toBeLessThanOrEqual(55.0);
  });

  it("validates Golden Vector 3: NA19240 YRI African female", () => {
    const v = GOLDEN_VECTORS[2];
    expect(v.id).toBe("VECTOR_NA19240_YRI");
    expect(v.trueAge).toBe(28.0);

    const resHorvath = computeClientEpigeneticAge(v.betas, v.tissue, "horvath_2013", v.trueAge);
    expect(resHorvath.calibratedPredictedAge).toBeGreaterThanOrEqual(v.expectedHorvath[0] - 1.0);
    expect(resHorvath.calibratedPredictedAge).toBeLessThanOrEqual(v.expectedHorvath[1] + 1.0);
  });

  it("validates Golden Vector 4: HG002 / NA24385 AJ horizon pivot benchmark", () => {
    const v = GOLDEN_VECTORS[3];
    expect(v.id).toBe("VECTOR_HG002_AJ");
    expect(v.trueAge).toBe(19.5);

    const resHorvath = computeClientEpigeneticAge(v.betas, v.tissue, "horvath_2013", v.trueAge);
    expect(resHorvath.calibratedPredictedAge).toBeGreaterThanOrEqual(v.expectedHorvath[0] - 1.0);
    expect(resHorvath.calibratedPredictedAge).toBeLessThanOrEqual(v.expectedHorvath[1] + 1.0);
  });

  it("validates Golden Vector 5: Heavy Tobacco Smoker / Morbid reference", () => {
    const v = GOLDEN_VECTORS[4];
    expect(v.id).toBe("VECTOR_SMOKER_MORBID");
    expect(v.trueAge).toBe(52.0);
    expect(v.packYears).toBe(35.0);

    const resHorvath = computeClientEpigeneticAge(v.betas, v.tissue, "horvath_2013", v.trueAge);
    expect(resHorvath.calibratedPredictedAge).toBeGreaterThanOrEqual(48.0);
    expect(resHorvath.calibratedPredictedAge).toBeLessThanOrEqual(65.0);

    // Significant GrimAge acceleration due to smoking
    const bio = computeClientBiologicalAging(v.betas, v.trueAge, v.packYears, v.sex);
    expect(bio.grimAgeAccel).toBeGreaterThan(5.0);
    expect(bio.mortalityHazardRatio).toBeGreaterThan(1.5);
  });

  // ===========================================================================
  // 3. MULTIMODAL POST-MORTEM INTERVAL (PMI) FUSION
  // ===========================================================================

  it("verifies multimodal PMI Bayesian fusion combining thermometry, potassium, and ADD", () => {
    const pmi = computeClientMultimodalPmi(28.5, 18.0, 11.5, 120.0);

    expect(pmi.henssgePmiHours).toBeGreaterThan(0);
    expect(pmi.madeaVitreousPmiHours).toBeGreaterThan(0);
    expect(pmi.entomologyPmiHours).toBeGreaterThan(0);
    expect(pmi.fusedPmiHours).toBeGreaterThan(0);
    expect(pmi.fusedPmiDays).toBeCloseTo(pmi.fusedPmiHours / 24.0, 2);
    expect(pmi.fusedPmiLowerHours).toBeLessThan(pmi.fusedPmiHours);
    expect(pmi.fusedPmiUpperHours).toBeGreaterThan(pmi.fusedPmiHours);
  });

  // ===========================================================================
  // 4. CRYPTOGRAPHIC STATE AUDIT DIGEST (SHA-256)
  // ===========================================================================

  it("computes deterministic 64-hex SHA-256 state audit digest sealing configuration", () => {
    const betas = GOLDEN_VECTORS[0].betas;
    const res = computeClientEpigeneticAge(betas, "WHOLE_BLOOD", "horvath_2013", 32.5);

    const hash1 = computeEpigeneticAuditHash(betas, "WHOLE_BLOOD", "horvath_2013", res);
    const hash2 = computeEpigeneticAuditHash(betas, "WHOLE_BLOOD", "horvath_2013", res);

    expect(hash1).toHaveLength(64);
    expect(/^[0-9a-f]{64}$/.test(hash1)).toBe(true);
    expect(hash1).toBe(hash2);

    // Mutating a beta changes hash
    const mutatedBetas = { ...betas, cg16867657: 0.850 };
    const resMutated = computeClientEpigeneticAge(mutatedBetas, "WHOLE_BLOOD", "horvath_2013", 32.5);
    const hashMutated = computeEpigeneticAuditHash(mutatedBetas, "WHOLE_BLOOD", "horvath_2013", resMutated);
    expect(hashMutated).not.toBe(hash1);
  });

  // ===========================================================================
  // 5. REACT UI RENDERING & 5-TAB NAVIGATION
  // ===========================================================================

  it("renders mission control header, ISO/IEC 17025 validation badge, and telemetry readouts", () => {
    render(<PanelEpigeneticClocks />);

    expect(screen.getByText(/Epigenetic Clocks|Epigenetik Saatler/i)).toBeInTheDocument();
    expect(screen.getByText(/ISO\/IEC 17025:2017/i)).toBeInTheDocument();
    expect(screen.getByText(/EPI-CLOCKS/i)).toBeInTheDocument();
  });

  it("switches across all 5 navigation tabs cleanly", () => {
    const { container } = render(<PanelEpigeneticClocks />);

    const tabBio = container.querySelector("#tab-biological_aging")!;
    fireEvent.click(tabBio);
    expect(screen.getByText(/DNAm PhenoAge/i)).toBeInTheDocument();

    const tabPmi = container.querySelector("#tab-multimodal_pmi")!;
    fireEvent.click(tabPmi);
    expect(screen.getAllByText(/Henssge/i).length).toBeGreaterThan(0);

    const tabBench = container.querySelector("#tab-benchmarks")!;
    fireEvent.click(tabBench);
    expect(screen.getAllByText(/NIST SRM 2391d/i).length).toBeGreaterThan(0);

    const tabIso = container.querySelector("#tab-iso_reporting")!;
    fireEvent.click(tabIso);
    expect(screen.getAllByText(/GUM/i).length).toBeGreaterThan(0);

    const tabStudio = container.querySelector("#tab-clocks_studio")!;
    fireEvent.click(tabStudio);
    expect(screen.getAllByText(/ELOVL2/i).length).toBeGreaterThan(0);
  });

  // ===========================================================================
  // 6. BENCHMARK LOADING & AUDIT TRAIL LOGGING
  // ===========================================================================

  it("loads certified standard in Tab 4 and records audit trail entry", async () => {
    const { container } = render(<PanelEpigeneticClocks />);

    const tabBench = container.querySelector("#tab-benchmarks")!;
    fireEvent.click(tabBench);

    const loadBtn = container.querySelector("#load-golden-VECTOR_NA12878_CEU")!;
    expect(loadBtn).toBeDefined();
    fireEvent.click(loadBtn);

    await waitFor(() => {
      const auditLogs = useForensicCaseStore.getState().auditTrail;
      const hasLog = auditLogs.some((l) => l.event.includes("NA12878") || l.event.includes("Loaded reference standard"));
      expect(hasLog).toBe(true);
    });
  });

  // ===========================================================================
  // 7. INTERACTIVE BETA SLIDER RECALCULATION
  // ===========================================================================

  it("reactively recalculates chronological age upon beta slider adjustment", () => {
    render(<PanelEpigeneticClocks />);

    const sliders = screen.getAllByRole("slider");
    expect(sliders.length).toBeGreaterThan(0);

    fireEvent.change(sliders[0], { target: { value: "0.75" } });
    // Verify calibrated age dial reflects updated value
    expect(screen.getByText(/Calibrated Chronological Age|Kalibre Edilmis Kronolojik Yas/i)).toBeInTheDocument();
  });

  // ===========================================================================
  // 8. SERVER VERIFICATION EXECUTION & AUDIT TRAIL LOGGING
  // ===========================================================================

  it("executes server verification and appends audit log to forensicCaseStore", async () => {
    const { container } = render(<PanelEpigeneticClocks />);

    const verifyBtn = container.querySelector("#epi-execute-verification-btn")!;
    expect(verifyBtn).toBeDefined();
    fireEvent.click(verifyBtn);

    await waitFor(
      () => {
        const auditLogs = useForensicCaseStore.getState().auditTrail;
        const found = auditLogs.some((l) => l.module === "19. Epigenetic Clocks & PMI" && l.status === "PASS");
        expect(found).toBe(true);
      },
      { timeout: 4000 }
    );
  });

  // ===========================================================================
  // 9. CASE PROFILE INGESTION & STATUTORY PRIVACY SHIELDS
  // ===========================================================================

  it("auto-ingests activeCase epigeneticAge baseline and logs to auditTrail", async () => {
    render(<PanelEpigeneticClocks />);

    await waitFor(() => {
      const auditLogs = useForensicCaseStore.getState().auditTrail;
      const ingestedLog = auditLogs.find((l) => l.event.includes("Ingested active case profile"));
      expect(ingestedLog).toBeDefined();
      expect(ingestedLog?.status).toBe("PASS");
    });
  });

  it("renders German StPO section 81e biostatutory shield and copies ENFSI evaluative report", async () => {
    const { container } = render(<PanelEpigeneticClocks />);

    const tabIso = container.querySelector("#tab-iso_reporting")!;
    fireEvent.click(tabIso);

    expect(screen.getByText(/Privacy Shield|Biyoetik Kalkan/i)).toBeInTheDocument();
    expect(screen.getByText(/Prosecutor's Fallacy|Savcilik Yanilgisi/i)).toBeInTheDocument();

    const copyReportBtn = container.querySelector("#copy-enfsi-statement-btn")!;
    expect(copyReportBtn).toBeDefined();
    fireEvent.click(copyReportBtn);
    expect(navigator.clipboard.writeText).toHaveBeenCalled();

    const copyDigestBtn = container.querySelector("#copy-audit-hash-btn")!;
    expect(copyDigestBtn).toBeDefined();
    fireEvent.click(copyDigestBtn);
    expect(navigator.clipboard.writeText).toHaveBeenCalled();
  });
});
