import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PanelFreckling, {
    computeMC1RDiplotype,
    computeFrecklingScore,
    computeUVSensitivity,
    evaluateFrecklingProfile,
    computeFrecklingAuditHash,
    MC1R_R_LOCI,
    MC1R_r_LOCI,
    MODIFIER_LOCI,
    FRECKLING_STANDARDS,
} from "@/components/analysis/PanelFreckling";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

// Mock framer-motion to prevent animation freezes in jsdom
vi.mock("framer-motion", () => {
    const createComponent = (tag: string) => {
        const Comp = ({ children, ...props }: any) => React.createElement(tag, props, children);
        Comp.displayName = `motion.${tag}`;
        return Comp;
    };
    return {
        motion: new Proxy({}, {
            get: (_, prop: string) => createComponent(prop),
        }),
        AnimatePresence: ({ children }: any) => <>{children}</>,
    };
});

// Mock clipboard API
Object.assign(navigator, {
    clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
    },
});

describe("Subsystem 18 (Pillar 3.5) MC1R Epistasis & Freckling - Pure Mathematical Kernels", () => {
    it("evaluates wild-type baseline profile with zero MC1R burden (Valverde 1995)", () => {
        const dosages = {};
        const diplotypeRes = computeMC1RDiplotype(dosages);
        expect(diplotypeRes.diplotype).toBe("wt/wt");
        expect(diplotypeRes.functional_classification).toBe("WILD_TYPE");
        expect(diplotypeRes.total_mc1r_loss_weight).toBe(0.0);
        expect(diplotypeRes.r_high_risk_alleles_count).toBe(0);
        expect(diplotypeRes.r_low_risk_alleles_count).toBe(0);

        const scoreRes = computeFrecklingScore(diplotypeRes.total_mc1r_loss_weight, 0, 0, false);
        // logit = -2.50, F_score = 100 / (1 + exp(2.50)) = 7.59%
        expect(scoreRes.freckling_score_pct).toBe(7.59);
        expect(scoreRes.freckling_intensity).toContain("MINIMAL");
    });

    it("evaluates R151C homozygous severe loss-of-function with dense ephelides", () => {
        const dosages = { rs1805007: 2 }; // R151C, weight = 2.85 * 2 = 5.70
        const diplotypeRes = computeMC1RDiplotype(dosages);
        expect(diplotypeRes.diplotype).toBe("R/R");
        expect(diplotypeRes.functional_classification).toBe("SEVERE_LOSS");
        expect(diplotypeRes.total_mc1r_loss_weight).toBe(5.7);
        expect(diplotypeRes.r_high_risk_alleles_count).toBe(2);

        const scoreRes = computeFrecklingScore(diplotypeRes.total_mc1r_loss_weight, 0, 0, false);
        // logit = -2.50 + 1.35 * 5.70 = 5.195, F_score = 99.45%
        expect(scoreRes.freckling_score_pct).toBe(99.45);
        expect(scoreRes.freckling_intensity).toContain("DENSE");
    });

    it("evaluates R151C and V60L compound heterozygous moderate loss (Sulem 2007)", () => {
        const dosages = { rs1805007: 1, rs1805005: 1 }; // R151C (2.85) + V60L (1.10) = 3.95
        const diplotypeRes = computeMC1RDiplotype(dosages);
        expect(diplotypeRes.diplotype).toBe("R/r");
        expect(diplotypeRes.functional_classification).toBe("MODERATE_LOSS");
        expect(diplotypeRes.total_mc1r_loss_weight).toBe(3.95);
        expect(diplotypeRes.r_high_risk_alleles_count).toBe(1);
        expect(diplotypeRes.r_low_risk_alleles_count).toBe(1);

        const scoreRes = computeFrecklingScore(diplotypeRes.total_mc1r_loss_weight, 0, 0, false);
        // logit = -2.50 + 1.35 * 3.95 = 2.8325, F_score = 94.44%
        expect(scoreRes.freckling_score_pct).toBe(94.44);
        expect(scoreRes.freckling_intensity).toContain("DENSE");
    });

    it("evaluates V60L homozygous mild loss-of-function (r/r)", () => {
        const dosages = { rs1805005: 2 }; // V60L (1.10 * 2 = 2.20)
        const diplotypeRes = computeMC1RDiplotype(dosages);
        expect(diplotypeRes.diplotype).toBe("r/r");
        expect(diplotypeRes.functional_classification).toBe("MILD_LOSS");
        expect(diplotypeRes.total_mc1r_loss_weight).toBe(2.2);

        const scoreRes = computeFrecklingScore(diplotypeRes.total_mc1r_loss_weight, 0, 0, false);
        // logit = -2.50 + 1.35 * 2.20 = 0.47, F_score = 61.54%
        expect(scoreRes.freckling_score_pct).toBe(61.54);
        expect(scoreRes.freckling_intensity).toContain("MODERATE");
    });

    it("evaluates epistatic boost from ASIP and BNC2 independently (Sulem 2008)", () => {
        // Zero MC1R burden, homozygous ASIP (+0.85*2) and BNC2 (+0.65*2)
        const scoreRes = computeFrecklingScore(0.0, 2, 2, false);
        // logit = -2.50 + 0 + 1.70 + 1.30 = 0.50, F_score = 62.25%
        expect(scoreRes.freckling_score_pct).toBe(62.25);
        expect(scoreRes.freckling_intensity).toContain("MODERATE");
        expect(scoreRes.epistatic_modifiers_applied.ASIP_rs1015362).toBe(2);
        expect(scoreRes.epistatic_modifiers_applied.BNC2_rs10756819).toBe(2);
    });

    it("maps diplotype tiers to exact Minimal Erythema Dose and tanning capacity", () => {
        const uvRR = computeUVSensitivity("R/R", false);
        expect(uvRR.minimal_erythema_dose_category).toContain("< 20 mJ/cm2");
        expect(uvRR.tanning_capacity).toBe("NEVER_TANS_ALWAYS_BURNS");

        const uvRr = computeUVSensitivity("R/r", false);
        expect(uvRr.minimal_erythema_dose_category).toContain("20 - 35 mJ/cm2");
        expect(uvRr.tanning_capacity).toBe("RARE_TAN_FREQUENT_BURN");

        const uv_rr = computeUVSensitivity("r/r", false);
        expect(uv_rr.minimal_erythema_dose_category).toContain("35 - 50 mJ/cm2");
        expect(uv_rr.tanning_capacity).toBe("MILD_TAN_OCCASIONAL_BURN");

        const uvWT = computeUVSensitivity("wt/wt", false);
        expect(uvWT.minimal_erythema_dose_category).toContain("> 50 mJ/cm2");
        expect(uvWT.tanning_capacity).toBe("NORMAL_TAN_RARE_BURN");
    });

    it("validates all 5 certified reference standards against published ground truth", () => {
        FRECKLING_STANDARDS.forEach(std => {
            const res = evaluateFrecklingProfile(std.snp_dosages, false);
            expect(res.mc1r.diplotype).toBe(std.expected_diplotype);
            expect(res.mc1r.functional_classification).toBe(std.expected_functional_class);
            expect(res.mc1r.total_mc1r_loss_weight).toBeCloseTo(std.expected_w_mc1r, 2);
            expect(res.freckling.freckling_score_pct).toBeCloseTo(std.expected_f_score, 1);
            expect(res.uv_sensitivity.minimal_erythema_dose_category).toContain(std.expected_med.replace(">", "").replace("<", "").trim().slice(0, 5));
        });
    });

    it("generates deterministic 64-hex SHA-256 state audit digest", async () => {
        const dosagesA = { rs1805007: 2 };
        const resA = evaluateFrecklingProfile(dosagesA, false);
        const hashA1 = await computeFrecklingAuditHash(dosagesA, resA);
        const hashA2 = await computeFrecklingAuditHash(dosagesA, resA);
        expect(hashA1).toBe(hashA2);
        expect(hashA1).toHaveLength(64);

        const dosagesB = { rs1805005: 2 };
        const resB = evaluateFrecklingProfile(dosagesB, false);
        const hashB = await computeFrecklingAuditHash(dosagesB, resB);
        expect(hashB).not.toBe(hashA1);
    });

    it("verifies mathematical invariants: score bounds and positive monotonicity", () => {
        // Freckling score must be strictly in [0.0, 100.0]
        const resMin = computeFrecklingScore(0.0, 0, 0, false);
        expect(resMin.freckling_score_pct).toBeGreaterThanOrEqual(0.0);
        expect(resMin.freckling_score_pct).toBeLessThanOrEqual(100.0);

        const resMax = computeFrecklingScore(10.0, 2, 2, false);
        expect(resMax.freckling_score_pct).toBeGreaterThanOrEqual(0.0);
        expect(resMax.freckling_score_pct).toBeLessThanOrEqual(100.0);

        // Strict monotonicity: dF/dW > 0
        const f0 = computeFrecklingScore(0.0, 0, 0).freckling_score_pct;
        const f1 = computeFrecklingScore(2.0, 0, 0).freckling_score_pct;
        const f2 = computeFrecklingScore(4.0, 0, 0).freckling_score_pct;
        expect(f1).toBeGreaterThan(f0);
        expect(f2).toBeGreaterThan(f1);

        // Modifier monotonicity: dF/dASIP > 0, dF/dBNC2 > 0
        const fAsip0 = computeFrecklingScore(0.0, 0, 0).freckling_score_pct;
        const fAsip1 = computeFrecklingScore(0.0, 1, 0).freckling_score_pct;
        const fBnc2_1 = computeFrecklingScore(0.0, 0, 1).freckling_score_pct;
        expect(fAsip1).toBeGreaterThan(fAsip0);
        expect(fBnc2_1).toBeGreaterThan(fAsip0);
    });
});

describe("Subsystem 18 (Pillar 3.5) PanelFreckling Component & Case Store Integration", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useForensicCaseStore.setState({
            activeCase: undefined as any,
            auditTrail: [],
        });
    });

    it("renders mission control header, ISO/IEC 17025 validation badge, and diplotype telemetry bar", () => {
        render(<PanelFreckling />);
        expect(screen.getByText(/Module 18 : Pillar 3 #5/i)).toBeInTheDocument();
        expect(screen.getByText(/ISO\/IEC 17025 VERIFIED/i)).toBeInTheDocument();
        expect(screen.getByText(/Ephelides \(Freckling\), MC1R Epistasis & UV Sensitivity/i)).toBeInTheDocument();
        expect(screen.getByText(/Diplotype \/ Loss/i)).toBeInTheDocument();
    });

    it("allows switching seamlessly across all 5 analytical tabs", () => {
        render(<PanelFreckling />);
        expect(screen.getByText(/1. Standards & Calibration/i)).toBeInTheDocument();

        // Switch to Tab 2
        fireEvent.click(screen.getByText(/2. MC1R Diplotype & Dosage/i));
        expect(screen.getByText(/High-Risk 'R' Loss-of-Function Alleles/i)).toBeInTheDocument();

        // Switch to Tab 3
        fireEvent.click(screen.getByText(/3. Ephelides Facial Map/i));
        expect(screen.getByText(/Logistic Formulation & Mathematical Invariant/i)).toBeInTheDocument();

        // Switch to Tab 4
        fireEvent.click(screen.getByText(/4. UV MED & Phototype/i));
        expect(screen.getByText(/Clinical Photoprotection & Erythema Guidance/i)).toBeInTheDocument();

        // Switch to Tab 5
        fireEvent.click(screen.getByText(/5. Cross-Validation & Legal/i));
        expect(screen.getByText(/Independent Tool Cross-Validation/i)).toBeInTheDocument();
    });

    it("loads certified standard STD-MC1R-01 and dispatches STANDARD_LOADED audit log", () => {
        render(<PanelFreckling />);
        const stdCard = document.getElementById("load-std-STD-MC1R-01");
        expect(stdCard).toBeInTheDocument();
        fireEvent.click(stdCard!);

        const logs = useForensicCaseStore.getState().auditTrail;
        expect(logs.length).toBeGreaterThanOrEqual(1);
        expect(logs[0].event).toBe("STANDARD_LOADED");
        expect(logs[0].module).toBe("Subsystem 18 (Ephelides & MC1R)");
        expect(logs[0].status).toBe("PASS");
    });

    it("toggles dosage in Tab 2 and updates reactive calculation state", () => {
        render(<PanelFreckling />);
        // Switch to Tab 2
        fireEvent.click(screen.getByText(/2. MC1R Diplotype & Dosage/i));

        // Click dosage 0 for R151C (rs1805007)
        const dose0Btn = document.getElementById("rs1805007-dose-0");
        if (dose0Btn) {
            fireEvent.click(dose0Btn);
        }

        // Click dosage 2 for V60L (rs1805005)
        const dose2Btn = document.getElementById("rs1805005-dose-2");
        if (dose2Btn) {
            fireEvent.click(dose2Btn);
        }

        // Diplotype should update to r/r
        expect(screen.getByText(/r\/r \(MILD_LOSS\)/i)).toBeInTheDocument();
    });

    it("executes live analysis API call and dispatches INFERENCE_EXECUTED audit log", async () => {
        const mockResponse = {
            mc1r: {
                diplotype: "R/R",
                functional_classification: "SEVERE_LOSS",
                total_mc1r_loss_weight: 5.70,
                r_high_risk_alleles_count: 2,
                r_low_risk_alleles_count: 0,
                detected_variants: ["rs1805007 (R151C)"],
            },
            freckling: {
                freckling_score_pct: 99.45,
                freckling_intensity: "DENSE",
                epistatic_modifiers_applied: { ASIP_rs1015362: 0, BNC2_rs10756819: 0 },
            },
            uv_sensitivity: {
                minimal_erythema_dose_category: "< 20 mJ/cm2",
                tanning_capacity: "NEVER_TANS_ALWAYS_BURNS",
                photoprotection_guidance: "Extremely high photosensitivity.",
            },
            assayed_snps_count: 1,
            prosecutors_fallacy_shield: "Results calibrated.",
        };

        global.fetch = vi.fn().mockResolvedValue({
            ok: true,
            json: vi.fn().mockResolvedValue(mockResponse),
        });

        render(<PanelFreckling />);
        const runBtn = document.getElementById("freckle-run-analysis-btn");
        expect(runBtn).toBeInTheDocument();
        fireEvent.click(runBtn!);

        await waitFor(() => {
            const logs = useForensicCaseStore.getState().auditTrail;
            const infLog = logs.find(l => l.event === "INFERENCE_EXECUTED");
            expect(infLog).toBeDefined();
            expect(infLog?.module).toBe("Subsystem 18 (Ephelides & MC1R)");
            expect(infLog?.status).toBe("PASS");
        });
    });

    it("auto-ingests activeCase profile SNP markers and logs CASE_PROFILE_INGESTED", () => {
        useForensicCaseStore.setState({
            activeCase: {
                metadata: {
                    caseId: "CASE-2026-MC1R",
                    leadAnalyst: "Dr. Freckle Specialist",
                },
                profile: {
                    snpMarkers: {
                        rs1805007: 1, // R151C
                        rs1805005: 1, // V60L
                        rs1015362: 2, // ASIP
                    },
                },
            } as any,
            auditTrail: [],
        });

        render(<PanelFreckling />);
        const logs = useForensicCaseStore.getState().auditTrail;
        const ingestLog = logs.find(l => l.event === "CASE_PROFILE_INGESTED");
        expect(ingestLog).toBeDefined();
        expect(ingestLog?.analyst).toBe("Dr. Freckle Specialist");
    });

    it("copies evaluative reporting statement to clipboard", () => {
        render(<PanelFreckling />);
        // Switch to Tab 5
        fireEvent.click(screen.getByText(/5. Cross-Validation & Legal/i));

        const copyBtn = document.getElementById("copy-reporting-shield-btn");
        expect(copyBtn).toBeInTheDocument();
        fireEvent.click(copyBtn!);

        expect(navigator.clipboard.writeText).toHaveBeenCalled();
    });

    it("renders cryptographic state audit digest card and copies hash with AUDIT_DIGEST_COPIED log", async () => {
        render(<PanelFreckling />);
        // Switch to Tab 5
        fireEvent.click(screen.getByText(/5. Cross-Validation & Legal/i));

        expect(screen.getByText(/Cryptographic State Audit Digest \(SHA-256\)/i)).toBeInTheDocument();
        const copyHashBtn = document.getElementById("copy-audit-hash-btn");
        expect(copyHashBtn).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.queryByText(/Generating state digest/i)).not.toBeInTheDocument();
        });

        fireEvent.click(copyHashBtn!);
        expect(navigator.clipboard.writeText).toHaveBeenCalled();

        await waitFor(() => {
            const logs = useForensicCaseStore.getState().auditTrail;
            const hashLog = logs.find(l => l.event === "AUDIT_DIGEST_COPIED");
            expect(hashLog).toBeDefined();
            expect(hashLog?.module).toBe("Subsystem 18 (Ephelides & MC1R)");
            expect(hashLog?.findingSeverity).toBe("NOMINAL");
        });
    });

    it("renders German § 81e StPO and EU AI Act Prosecutor's Fallacy evaluative reporting safeguard", () => {
        render(<PanelFreckling />);
        // Switch to Tab 5
        fireEvent.click(screen.getByText(/5. Cross-Validation & Legal/i));

        expect(screen.getByText(/German § 81e StPO & EU AI Act Biometric Compliance/i)).toBeInTheDocument();
        expect(screen.getByText(/IMPORTANT LEGAL SHIELD \(Prosecutor's Fallacy Defense\):/i)).toBeInTheDocument();
    });
});
