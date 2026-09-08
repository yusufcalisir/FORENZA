import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import ZkpAuditorPanel from "@/components/analysis/ZkpAuditorPanel";
import { SaasLanguageProvider } from "@/context/SaaSLanguageContext";

describe("ZkpAuditorPanel Component (Subsystem 30 / Pillar 6.2)", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders mission bar, multi-prover architecture selector, and default Groth16 profile", () => {
    render(
      <SaasLanguageProvider>
        <ZkpAuditorPanel />
      </SaasLanguageProvider>
    );

    expect(
      screen.getByText(/ZK-SNARK Verifiable Computation & Blind Auditor|ZK-SNARK Doğrulanabilir Hesaplama & Kör Adli Denetçi/i)
    ).toBeInTheDocument();
    expect(screen.getByText(/Pillar 6.2 • Multi-Prover/i)).toBeInTheDocument();
    expect(screen.getByText(/ISO\/IEC 17025 §7.8.2/i)).toBeInTheDocument();
    expect(screen.getByText(/VERIFIED 38\/38/i)).toBeInTheDocument();
  });

  it("switches between proving systems and updates architecture specifications", () => {
    render(
      <SaasLanguageProvider>
        <ZkpAuditorPanel />
      </SaasLanguageProvider>
    );

    // Initial Groth16
    expect(screen.getAllByText(/Groth16/i)[0]).toBeInTheDocument();

    // Switch to PLONK
    const plonkBtn = screen.getByRole("button", { name: /^PLONK/i });
    fireEvent.click(plonkBtn);
    expect(screen.getByText(/Plonkish Custom Gates|Plonkish Özel Kapılar/i)).toBeInTheDocument();

    // Switch to Halo2
    const haloBtn = screen.getByRole("button", { name: /Halo2/i });
    fireEvent.click(haloBtn);
    expect(screen.getByText(/UltraPLONK Custom Gates|UltraPLONK Özel Kapıları/i)).toBeInTheDocument();

    // Switch to VOLE
    const voleBtn = screen.getByRole("button", { name: /VOLE/i });
    fireEvent.click(voleBtn);
    expect(screen.getByText(/Vector Oblivious Linear Evaluation|Vektör İhmalkar Lineer Değerlendirme/i)).toBeInTheDocument();
  });

  it("switches golden reference vectors and updates blind match threshold", () => {
    render(
      <SaasLanguageProvider>
        <ZkpAuditorPanel />
      </SaasLanguageProvider>
    );

    const interpolBtn = screen.getByRole("button", {
      name: /Interpol Red Notice|Interpol Kırmızı Bülten/i,
    });
    fireEvent.click(interpolBtn);

    expect(screen.getAllByText(/INTERPOL-QUERY/i)[0]).toBeInTheDocument();
  });

  it("toggles secret witness masking", () => {
    render(
      <SaasLanguageProvider>
        <ZkpAuditorPanel />
      </SaasLanguageProvider>
    );

    const maskBtn = screen.getByRole("button", { name: /UNMASK|GÖSTER/i });
    expect(maskBtn).toBeInTheDocument();

    fireEvent.click(maskBtn);
    expect(screen.getByRole("button", { name: /MASK|GİZLE/i })).toBeInTheDocument();
  });

  it("switches tabs between Prover, Group Elements, SMT Soundness, and MPC Ceremony", () => {
    render(
      <SaasLanguageProvider>
        <ZkpAuditorPanel />
      </SaasLanguageProvider>
    );

    // 1. Group Elements / Pairings tab
    const pairingsTab = screen.getByRole("button", {
      name: /Group Elements & Pairings|Eşleşme & Grup Elemanları/i,
    });
    fireEvent.click(pairingsTab);
    expect(
      screen.getByText(/Cryptographic Proof Data & Pairing Equation|Kriptografik İspat Verileri & Eşleşme Denklemi/i)
    ).toBeInTheDocument();

    // 2. SMT Soundness tab
    const smtTab = screen.getByRole("button", {
      name: /SMT Soundness Audit|SMT Formel Soundness/i,
    });
    fireEvent.click(smtTab);
    expect(screen.getByText(/Z3 \/ QED2 Engine/i)).toBeInTheDocument();
    expect(
      screen.getByText(/All Intermediate Advice Signals Fully Constrained|Tüm Ara Tavsiye Sinyalleri Kesin Kısıtlanmıştır/i)
    ).toBeInTheDocument();

    // 3. MPC Ceremony tab
    const ceremonyTab = screen.getByRole("button", {
      name: /1-of-N MPC Ceremony|1-of-N MPC Powers of Tau/i,
    });
    fireEvent.click(ceremonyTab);
    expect(screen.getByText(/Hermez \/ BGM17 Setup/i)).toBeInTheDocument();
    expect(screen.getByText(/16 Independent Accredited Labs/i)).toBeInTheDocument();
  });

  it("executes proof synthesis and displays verified courtroom admissibility verdict", async () => {
    render(
      <SaasLanguageProvider>
        <ZkpAuditorPanel />
      </SaasLanguageProvider>
    );

    const synthBtn = screen.getByRole("button", {
      name: /Synthesize & Verify ZK Proof|ZK İspatını Sentezle ve Doğrula/i,
    });
    fireEvent.click(synthBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/CRYPTOGRAPHIC MATCH PROOF VERIFIED|KRİPTOGRAFİK EŞLEŞME İSPATI DOĞRULANDI/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/ENFSI \(2017\) Evaluative Statement|ENFSI \(2017\) Standart Sözel Değerlendirme/i)
      ).toBeInTheDocument();
      expect(screen.getByText(/ISO\/IEC 17025 Compliant/i)).toBeInTheDocument();
    });
  });
});
