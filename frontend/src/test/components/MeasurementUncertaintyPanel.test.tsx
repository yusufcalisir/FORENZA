import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import MeasurementUncertaintyPanel from "@/components/analysis/MeasurementUncertaintyPanel";
import { SaasLanguageProvider } from "@/context/SaaSLanguageContext";

describe("MeasurementUncertaintyPanel Component (Subsystem 31 / Pillar 6.3)", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders mission control bar, ISO 17025 validation badge, and default GUM budget telemetry", () => {
    render(
      <SaasLanguageProvider>
        <MeasurementUncertaintyPanel />
      </SaasLanguageProvider>
    );

    expect(
      screen.getByText(/ISO 17025 Ölçüm Belirsizliği & Kalibrasyon|ISO 17025 Measurement Uncertainty & Calibration/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/GUM JCGM 100 • k=2.00/i)).toBeInTheDocument();
    expect(screen.getByText(/ISO\/IEC 17025 Doğrulandı|ISO\/IEC 17025 Validated/i)).toBeInTheDocument();
    expect(screen.getByText(/GUM JCGM 100:2008 GENİŞLETİLMİŞ BELİRSİZLİK ARALIĞI|GUM JCGM 100:2008 EXPANDED UNCERTAINTY INTERVAL/i)).toBeInTheDocument();
    expect(screen.getByText(/1.450 ± 0.108 ng\/μL/i)).toBeInTheDocument();
  });

  it("calculates uncertainty budget across presets and verifies VECTOR_P6_02 ground truth", () => {
    render(
      <SaasLanguageProvider>
        <MeasurementUncertaintyPanel />
      </SaasLanguageProvider>
    );

    // Initial VECTOR_P6_02 values
    expect(screen.getByText(/1.450 ± 0.108 ng\/μL/i)).toBeInTheDocument();
    expect(screen.getByText(/0.05385 ng\/μL/i)).toBeInTheDocument();
    expect(screen.getByText(/± 0.10770 ng\/μL/i)).toBeInTheDocument();

    // Switch to LTDNA preset
    const ltdnaBtn = screen.getByRole("button", { name: /18pg Touch DNA Specimen|18pg Temas DNA Örneği/i });
    fireEvent.click(ltdnaBtn);

    expect(screen.getByText(/0.036 ± 0.108 ng\/μL/i)).toBeInTheDocument();
  });

  it("supports manual concentration input and coverage factor adjustments", () => {
    render(
      <SaasLanguageProvider>
        <MeasurementUncertaintyPanel />
      </SaasLanguageProvider>
    );

    const concInput = screen.getByRole("spinbutton");
    fireEvent.change(concInput, { target: { value: "2.50" } });

    expect(screen.getByText(/2.500 ± 0.108 ng\/μL/i)).toBeInTheDocument();

    const selectEl = screen.getByRole("combobox");
    fireEvent.change(selectEl, { target: { value: "1" } });

    // k=1.00 -> expanded U = 0.054 ng/μL
    expect(screen.getByText(/2.500 ± 0.054 ng\/μL/i)).toBeInTheDocument();
  });

  it("evaluates proficiency testing z-scores across Satisfactory, Questionable, and Unsatisfactory tiers", () => {
    render(
      <SaasLanguageProvider>
        <MeasurementUncertaintyPanel />
      </SaasLanguageProvider>
    );

    // Switch to Proficiency sub-tab
    const profTabBtn = screen.getByRole("button", { name: /Yeterlilik z-Skoru|Proficiency z-Score/i });
    fireEvent.click(profTabBtn);

    expect(screen.getByText(/YETERLİLİK TESTİ KONSENSÜS z-SKORU|PROFICIENCY TESTING CONSENSUS z-SCORE/i)).toBeInTheDocument();
    expect(screen.getByText(/z = \+0.400/i)).toBeInTheDocument();
    expect(screen.getAllByText(/^SATISFACTORY$|^TATMIN EDİCİ$/i)[0]).toBeInTheDocument();

    // Select Questionable preset (z = +2.40)
    const questBtn = screen.getByRole("button", { name: /Questionable Bias|Şüpheli Sapma/i });
    fireEvent.click(questBtn);

    expect(screen.getByText(/z = \+2.400/i)).toBeInTheDocument();
    expect(screen.getAllByText(/^QUESTIONABLE$|^ŞÜPHELİ \/ UYARI$/i)[0]).toBeInTheDocument();

    // Select Unsatisfactory preset (z = +4.00)
    const unsatBtn = screen.getByRole("button", { name: /Unsatisfactory Action|Yetersiz Eylem/i });
    fireEvent.click(unsatBtn);

    expect(screen.getByText(/z = \+4.000/i)).toBeInTheDocument();
    expect(screen.getAllByText(/^UNSATISFACTORY$|^YETERSİZ \/ DÜZELTİCİ FAALİYET$/i)[0]).toBeInTheDocument();
  });

  it("evaluates Casework Profile QA/QC Matrix and detects negative control contamination", () => {
    render(
      <SaasLanguageProvider>
        <MeasurementUncertaintyPanel />
      </SaasLanguageProvider>
    );

    // Switch to Profile QA/QC sub-tab
    const profileTabBtn = screen.getByRole("button", { name: /Profil KG\/KK Matrisi|Profile QA\/QC Matrix/i });
    fireEvent.click(profileTabBtn);

    expect(screen.getByText(/GENETİK PROFİL KG\/KK DENETİM KARARI|GENETIC PROFILE QA\/QC AUDIT VERDICT/i)).toBeInTheDocument();
    expect(screen.getAllByText(/QC DOĞRULANDI|QC PASSED/i)[0]).toBeInTheDocument();

    // Check inspection dimensions
    expect(screen.getByText(/NEGATİF_KONTROL_BÜTÜNLÜĞÜ|NEGATIVE_CONTROL_INTEGRITY/i)).toBeInTheDocument();
    expect(screen.getByText(/POZİTİF_KONTROL_UYUMU|POSITIVE_CONTROL_CONCORDANCE/i)).toBeInTheDocument();
    expect(screen.getByText(/HETEROZİGOT_ALEL_DENGESİ|HETEROZYGOTE_ALLELE_BALANCE/i)).toBeInTheDocument();

    // Select Contaminated Blank preset (NC = 72.5 RFU)
    const contamPresetBtn = screen.getByRole("button", { name: /Contaminated Negative Control|Kontamine Negatif Kontrol/i });
    fireEvent.click(contamPresetBtn);

    expect(screen.getByText(/QC BAŞARISIZ: TEKRAR GEREKLİ|QC FAILED/i)).toBeInTheDocument();
    expect(screen.getByText(/YENİDEN_EKSTRAKSİYON_VEYA_YENİDEN_ÇOĞALTIM_ZORUNLU|RE_EXTRACTION_OR_RE_AMPLIFICATION_REQUIRED/i)).toBeInTheDocument();
  });

  it("displays Prosecutor's Fallacy and FRE 702 metrological uncertainty shield", () => {
    render(
      <SaasLanguageProvider>
        <MeasurementUncertaintyPanel />
      </SaasLanguageProvider>
    );

    expect(
      screen.getByText(/ISO\/IEC 17025:2017 Madde 7.6 Metrolojik Belirsizlik Kalkanı|ISO\/IEC 17025:2017 Clause 7.6 Metrological Uncertainty Shield/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/Expanded uncertainty budgeting|GUM kılavuzuna göre genişletilmiş belirsizlik bütçesi/i)).toBeInTheDocument();
  });
});
