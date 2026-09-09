import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PanelHair, {
    computeHairTexture,
    computeBaldingPRS,
    calculateFiberDimensions,
    evaluateHairProfile,
    computeHairAuditHash,
    HAIR_STANDARDS,
    SNP_METADATA,
    TEXTURE_CONFIG,
    RISK_CONFIG,
} from "@/components/analysis/PanelHair";
import { useForensicCaseStore } from "@/store/forensicCaseStore";

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

describe("Subsystem 17 (Pillar 3.4) Hair Texture & Balding PRS - Pure Mathematical Kernels", () => {
    it("evaluates baseline zero-dosage profile correctly", () => {
        const dosages = { rs3827072: 0, rs11803731: 0, rs7349332: 0, rs6152: 0, rs2180439: 0, rs1160312: 0, rs756853: 0 };
        const res = computeHairTexture(dosages, false);
        expect(res.curl_density_index).toBe(1.2);
        expect(res.fiber_cross_sectional_area_um2).toBe(3850.0);
        expect(res.texture_category).toBe("STRAIGHT");
        expect(res.major_diameter_um).toBe(77.5);
        expect(res.minor_diameter_um).toBe(77.5);
    });

    it("evaluates EDAR Val370Ala homozygous coarsening and curl suppression (Medland et al. 2009)", () => {
        const dosages = { rs3827072: 2, rs11803731: 0, rs7349332: 0 };
        const res = computeHairTexture(dosages, false);
        // Area = 3850 + 1420 * 2 = 6690 um2
        expect(res.fiber_cross_sectional_area_um2).toBe(6690.0);
        // Raw curl = 1.20 - 2.10 * 2 = -3.00, clamped to 0.00
        expect(res.curl_density_index).toBe(0.0);
        expect(res.texture_category).toBe("STRAIGHT");
        expect(res.major_diameter_um).toBe(103.0);
        expect(res.minor_diameter_um).toBe(103.0);
    });

    it("evaluates African kinky/woolly hair with max TCHH and WNT10A curl induction (Adhikari et al. 2016)", () => {
        const dosages = { rs3827072: 0, rs11803731: 2, rs7349332: 2 };
        const res = computeHairTexture(dosages, false);
        // Curl = 1.20 + 1.85 * 2 + 1.42 * 2 = 1.20 + 3.70 + 2.84 = 7.74
        expect(res.curl_density_index).toBe(7.74);
        expect(res.texture_category).toBe("KINKY_WOOLLY");
        expect(res.major_diameter_um).toBe(68.0);
        expect(res.minor_diameter_um).toBe(38.0);
    });

    it("evaluates European wavy hair with TCHH heterozygous derived allele", () => {
        const dosages = { rs3827072: 0, rs11803731: 1, rs7349332: 0 };
        const res = computeHairTexture(dosages, false);
        // Curl = 1.20 + 1.85 = 3.05 -> WAVY
        expect(res.curl_density_index).toBe(3.05);
        expect(res.texture_category).toBe("WAVY");
        expect(res.major_diameter_um).toBe(78.0);
        expect(res.minor_diameter_um).toBe(64.0);
    });

    it("evaluates curly hair category threshold (4.5 <= C_curl < 7.0)", () => {
        const dosages = { rs3827072: 0, rs11803731: 2, rs7349332: 0 };
        const res = computeHairTexture(dosages, false);
        // Curl = 1.20 + 1.85 * 2 = 4.90 -> CURLY
        expect(res.curl_density_index).toBe(4.90);
        expect(res.texture_category).toBe("CURLY");
        expect(res.major_diameter_um).toBe(70.0);
        expect(res.minor_diameter_um).toBe(54.0);
    });

    it("evaluates balding PRS baseline with zero risk", () => {
        const dosages = { rs6152: 0, rs2180439: 0, rs1160312: 0, rs756853: 0 };
        const balding = computeBaldingPRS(dosages, false);
        expect(balding.prs_score).toBe(0.0);
        expect(balding.hamilton_norwood_grade).toBe("GRADE_I_II");
        expect(balding.risk_level).toBe("LOW_RISK");
        expect(balding.assayed_balding_snps).toBe(0);
    });

    it("evaluates AR homozygous balding risk (Hillmer et al. 2005)", () => {
        const dosages = { rs6152: 2, rs2180439: 0, rs1160312: 0, rs756853: 0 };
        const balding = computeBaldingPRS(dosages, false);
        // PRS = 0.982 * 2 = 1.964 -> GRADE_IV_V (1.20 <= PRS < 2.10)
        expect(balding.prs_score).toBe(1.964);
        expect(balding.hamilton_norwood_grade).toBe("GRADE_IV_V");
        expect(balding.risk_level).toBe("ELEVATED_RISK");
        expect(balding.assayed_balding_snps).toBe(1);
    });

    it("evaluates maximum theoretical balding PRS across all 4 risk loci (Li et al. 2022)", () => {
        const dosages = { rs6152: 2, rs2180439: 2, rs1160312: 2, rs756853: 2 };
        const balding = computeBaldingPRS(dosages, false);
        // Max PRS = 2 * (0.982 + 0.541 + 0.485 + 0.362) = 2 * 2.370 = 4.740
        expect(balding.prs_score).toBe(4.74);
        expect(balding.hamilton_norwood_grade).toBe("GRADE_VI_VII");
        expect(balding.risk_level).toBe("HIGH_RISK");
        expect(balding.assayed_balding_snps).toBe(4);
    });

    it("evaluates moderate balding risk boundary (0.50 <= PRS < 1.20)", () => {
        const dosages = { rs6152: 0, rs2180439: 1, rs1160312: 1, rs756853: 0 };
        const balding = computeBaldingPRS(dosages, false);
        // PRS = 0.541 + 0.485 = 1.026 -> GRADE_III
        expect(balding.prs_score).toBe(1.026);
        expect(balding.hamilton_norwood_grade).toBe("GRADE_III");
        expect(balding.risk_level).toBe("MODERATE_RISK");
    });

    it("computes fiber dimensions across all categories and languages", () => {
        const enStraight = calculateFiberDimensions("STRAIGHT", 0, false);
        const trStraightCoarse = calculateFiberDimensions("STRAIGHT", 2, true);
        expect(enStraight.major).toBe(77.5);
        expect(trStraightCoarse.major).toBe(103.0);
        expect(trStraightCoarse.diamStr).toContain("Kalin Duz");

        const wavy = calculateFiberDimensions("WAVY", 0, false);
        expect(wavy.major).toBe(78.0);
        expect(wavy.minor).toBe(64.0);

        const afro = calculateFiberDimensions("KINKY_WOOLLY", 0, true);
        expect(afro.major).toBe(68.0);
        expect(afro.minor).toBe(38.0);
        expect(afro.diamStr).toContain("Afro");
    });

    it("evaluates composite hair profile and attaches legal fallacy shield", () => {
        const dosages = { rs3827072: 2, rs11803731: 0, rs7349332: 0, rs6152: 0, rs2180439: 0, rs1160312: 0, rs756853: 0 };
        const profileEn = evaluateHairProfile(dosages, false);
        expect(profileEn.texture.texture_category).toBe("STRAIGHT");
        expect(profileEn.balding.hamilton_norwood_grade).toBe("GRADE_I_II");
        expect(profileEn.prosecutors_fallacy_shield).toContain("ISO/IEC 17025");

        const profileTr = evaluateHairProfile(dosages, true);
        expect(profileTr.prosecutors_fallacy_shield).toContain("istihbari");
    });

    it("generates deterministic 64-hex SHA-256 state audit digest", () => {
        const dosages = { rs3827072: 2, rs11803731: 0, rs7349332: 0, rs6152: 0, rs2180439: 0, rs1160312: 0, rs756853: 0 };
        const profile = evaluateHairProfile(dosages, false);
        const hash1 = computeHairAuditHash(dosages, profile);
        const hash2 = computeHairAuditHash(dosages, profile);
        expect(hash1).toBe(hash2);
        expect(hash1).toMatch(/^[0-9a-f]{64}$/);

        // Mutated dosage should produce a different digest
        const mutated = { ...dosages, rs6152: 2 };
        const mutatedProfile = evaluateHairProfile(mutated, false);
        const mutatedHash = computeHairAuditHash(mutated, mutatedProfile);
        expect(mutatedHash).not.toBe(hash1);
    });
});

describe("Subsystem 17 (Pillar 3.4) PanelHair Component & Case Store Integration", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Reset case store state
        useForensicCaseStore.setState({
            activeCase: {
                metadata: {
                    caseId: "CASE-HAIR-2026-001",
                    caseTitle: "Forensic Hair Phenotyping Investigation",
                    jurisdiction: "DE-BKA-WIESBADEN",
                    leadAnalyst: "Dr. Elena Rostova",
                },
                profile: {
                    snpMarkers: {
                        rs3827072: 2,
                        rs11803731: 0,
                        rs7349332: 0,
                        rs6152: 0,
                        rs2180439: 0,
                        rs1160312: 0,
                        rs756853: 0,
                    },
                },
                auditTrail: [],
            } as any,
            auditTrail: [],
        });
    });

    it("renders mission control header, ISO/IEC 17025 validation badge, and telemetry bar", () => {
        render(<PanelHair />);
        expect(screen.getByText(/Hair Morphology, Fiber Dynamics & Balding PRS Studio/i)).toBeInTheDocument();
        expect(screen.getByText(/ISO\/IEC 17025:2017 VALIDATED/i)).toBeInTheDocument();
        expect(screen.getAllByText(/Curl Density Index/i)[0]).toBeInTheDocument();
        expect(screen.getByText(/Balding PRS Score/i)).toBeInTheDocument();
    });

    it("allows switching seamlessly across all 5 analytical tabs", () => {
        render(<PanelHair />);
        // Tab 1: Texture & Fiber Morphology (default)
        expect(screen.getByText(/Microscopic Hair Fiber Cross-Section/i)).toBeInTheDocument();

        // Switch to Tab 2: Balding PRS
        fireEvent.click(screen.getByText(/2\. Balding PRS & Scalp Stages/i));
        expect(screen.getByText(/Hamilton-Norwood Scalp Progression Studio/i)).toBeInTheDocument();

        // Switch to Tab 3: Certified Standards
        fireEvent.click(screen.getByText(/3\. Certified Standards \(5\)/i));
        expect(screen.getByText(/Certified Forensic Reference Standards & Golden Vectors/i)).toBeInTheDocument();
        expect(screen.getByText(/STD-HAIR-01/i)).toBeInTheDocument();

        // Switch to Tab 4: Cross-Validation
        fireEvent.click(screen.getByText(/4\. Cross-Validation Matrix/i));
        expect(screen.getByText(/CV-HAIR-01: EDAR Area Scaling/i)).toBeInTheDocument();
        expect(screen.getByText(/100% CONCORDANT/i)).toBeInTheDocument();

        // Switch to Tab 5: Legal Reporting
        fireEvent.click(screen.getByText(/5\. Legal Reporting \(§ 81e StPO\)/i));
        expect(screen.getByText(/German StPO § 81e Statutory Scope Analysis/i)).toBeInTheDocument();
        expect(screen.getByText(/Active Prosecutor's Fallacy Defense Shield/i)).toBeInTheDocument();
        expect(screen.getByText(/ISO\/IEC 17025 State Audit Digest & Chain of Custody/i)).toBeInTheDocument();
    });

    it("loads a certified reference standard and dispatches audit log to useForensicCaseStore", () => {
        const addAuditLogSpy = vi.spyOn(useForensicCaseStore.getState(), "addAuditLog");
        render(<PanelHair />);
        // Switch to Tab 3
        fireEvent.click(screen.getByText(/3\. Certified Standards \(5\)/i));

        // Load STD-HAIR-02 (African Kinky/Woolly)
        const loadBtn = document.getElementById("load-std-STD-HAIR-02");
        expect(loadBtn).not.toBeNull();
        fireEvent.click(loadBtn!);

        // Verify audit log dispatch
        expect(addAuditLogSpy).toHaveBeenCalledWith(
            expect.objectContaining({
                module: "17. Hair Morphology & Balding PRS Studio",
                status: "PASS",
                event: expect.stringContaining("Loaded certified reference standard"),
            })
        );
    });

    it("toggles SNP dosage and recalculates live biophysical telemetry", () => {
        const addAuditLogSpy = vi.spyOn(useForensicCaseStore.getState(), "addAuditLog");
        render(<PanelHair />);
        // Switch to Tab 2 (Balding PRS)
        fireEvent.click(screen.getByText(/2\. Balding PRS & Scalp Stages/i));

        // Toggle rs6152 to dosage 2 (homozygous risk)
        const dose2Btn = document.getElementById("rs6152-dose-2");
        expect(dose2Btn).not.toBeNull();
        fireEvent.click(dose2Btn!);

        // Verify audit log dispatch for dosage change
        expect(addAuditLogSpy).toHaveBeenCalledWith(
            expect.objectContaining({
                module: "17. Hair Morphology & Balding PRS Studio",
                status: "PASS",
                event: expect.stringContaining("rs6152"),
            })
        );
    });

    it("executes simulation analysis via action button and logs audit trail", async () => {
        const addAuditLogSpy = vi.spyOn(useForensicCaseStore.getState(), "addAuditLog");
        // Mock global fetch to return verified server response
        const mockFetch = vi.fn().mockResolvedValue({
            ok: true,
            json: async () => ({
                texture: {
                    curl_density_index: 0.0,
                    texture_category: "STRAIGHT",
                    fiber_cross_sectional_area_um2: 6690.0,
                    estimated_fiber_diameter_um: "85.0 - 110.0 um",
                    assayed_texture_snps: 1,
                },
                balding: {
                    prs_score: 0.0,
                    hamilton_norwood_grade: "GRADE_I_II",
                    clinical_description: "Hamilton-Norwood Grade I / II",
                    risk_level: "LOW_RISK",
                    assayed_balding_snps: 0,
                },
                prosecutors_fallacy_shield: "Verified Shield",
            }),
        });
        global.fetch = mockFetch;

        render(<PanelHair />);
        const executeBtn = document.getElementById("hair-run-analysis-btn");
        expect(executeBtn).not.toBeNull();
        fireEvent.click(executeBtn!);

        await waitFor(() => {
            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringContaining("/api/v1/phenotyping/hair/morphology-and-balding"),
                expect.objectContaining({ method: "POST" })
            );
        });

        expect(addAuditLogSpy).toHaveBeenCalledWith(
            expect.objectContaining({
                module: "17. Hair Morphology & Balding PRS Studio",
                status: "PASS",
            })
        );
    });

    it("copies cryptographic audit hash in Tab 5 and dispatches chain-of-custody log", () => {
        const addAuditLogSpy = vi.spyOn(useForensicCaseStore.getState(), "addAuditLog");
        render(<PanelHair />);
        // Switch to Tab 5
        fireEvent.click(screen.getByText(/5\. Legal Reporting \(§ 81e StPO\)/i));

        const copyHashBtn = document.getElementById("copy-audit-hash-btn");
        expect(copyHashBtn).not.toBeNull();
        fireEvent.click(copyHashBtn!);

        expect(navigator.clipboard.writeText).toHaveBeenCalled();
        expect(addAuditLogSpy).toHaveBeenCalledWith(
            expect.objectContaining({
                module: "17. Hair Morphology & Balding PRS Studio",
                status: "PASS",
                event: expect.stringContaining("64-hex SHA-256 state audit digest"),
            })
        );
    });
});
