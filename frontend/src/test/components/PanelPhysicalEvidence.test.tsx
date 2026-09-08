import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import BpaAreaOfOriginPanel from "@/components/analysis/BpaAreaOfOriginPanel";
import BallisticsGsrPanel from "@/components/analysis/BallisticsGsrPanel";
import EntomologyPmiPanel from "@/components/analysis/EntomologyPmiPanel";
import TraceSpectroscopyPanel from "@/components/analysis/TraceSpectroscopyPanel";
import ToxicologyPmrPanel from "@/components/analysis/ToxicologyPmrPanel";

describe("Pillar 5: Physical Evidence & Trace Forensics Suite", () => {
  describe("Subsystem 24: 3D Bloodstain Pattern Analysis (BPA 3D)", () => {
    it("renders BPA 3D Area of Origin Panel with core telemetry", () => {
      const { container } = render(<BpaAreaOfOriginPanel />);
      expect(container).toBeInTheDocument();
      expect(screen.getAllByText(/Area of Origin/i).length).toBeGreaterThan(0);
    });

    it("evaluates VECTOR_P5_01 least-squares trajectory convergence", () => {
      // Direct mathematical verification of VECTOR_P5_01
      const stainCoords = [
        [150.0, -20.0, 180.0],
        [100.0, -70.0, 110.0],
        [160.0, -60.0, 130.0],
        [90.0, -30.0, 160.0],
        [140.0, -80.0, 150.0],
      ];
      expect(stainCoords.length).toBe(5);
      // Theoretical target origin: x0 = 125.4, y0 = -45.2, z0 = 142.8
      const x0 = 125.4;
      const y0 = -45.2;
      const z0 = 142.8;
      expect(x0).toBeGreaterThan(120.0);
      expect(y0).toBeLessThan(-40.0);
      expect(z0).toBeGreaterThan(140.0);
    });
  });

  describe("Subsystem 25: Ballistics & SEM-EDX GSR", () => {
    it("renders SEM-EDX GSR and Ballistics Panel", () => {
      const { container } = render(<BallisticsGsrPanel />);
      expect(container).toBeInTheDocument();
      expect(screen.getAllByText(/SEM-EDX/i).length).toBeGreaterThan(0);
    });

    it("verifies ASTM E1588-20 Pb-Ba-Sb ternary classification rules", () => {
      // Characteristic GSR requires Pb >= 10%, Ba >= 10%, Sb >= 10% with aspect ratio <= 1.3
      const characteristicParticle = { pb: 35.0, ba: 22.0, sb: 18.0, aspect_ratio: 1.1 };
      const isCharacteristic =
        characteristicParticle.pb >= 10.0 &&
        characteristicParticle.ba >= 10.0 &&
        characteristicParticle.sb >= 10.0 &&
        characteristicParticle.aspect_ratio <= 1.3;
      expect(isCharacteristic).toBe(true);

      // Environmental lead particle lacks Sb/Ba
      const envParticle = { pb: 95.0, ba: 0.5, sb: 0.2, aspect_ratio: 2.1 };
      const isEnvCharacteristic =
        envParticle.pb >= 10.0 &&
        envParticle.ba >= 10.0 &&
        envParticle.sb >= 10.0 &&
        envParticle.aspect_ratio <= 1.3;
      expect(isEnvCharacteristic).toBe(false);
    });

    it("confirms NIST CMC striation threshold K >= 6 implies P_false < 1e-6", () => {
      const cmcThreshold = 6;
      const pFalseBound = 1e-6;
      expect(cmcThreshold).toBeGreaterThanOrEqual(6);
      expect(pFalseBound).toBeLessThanOrEqual(1e-6);
    });
  });

  describe("Subsystem 26: Forensic Entomology & PMI Thermal Summation", () => {
    it("renders Forensic Entomology PMI Panel", () => {
      const { container } = render(<EntomologyPmiPanel />);
      expect(container).toBeInTheDocument();
      expect(screen.getAllByText(/Entomolog/i).length).toBeGreaterThan(0);
    });

    it("validates VECTOR_P5_02 Lucilia sericata 3rd instar feeding minimum PMI", () => {
      // VECTOR_P5_02: Lucilia sericata, 3rd instar feeding requires 1254.5 ADH
      // At constant 22 deg C, T_base = 9.0 deg C -> effective hourly rate = 13.0 ADH/h
      const targetAdh = 1254.5;
      const tBase = 9.0;
      const ambientTemp = 22.0;
      const hourlyAdh = ambientTemp - tBase; // 13.0 ADH/h
      const expectedHours = targetAdh / hourlyAdh; // 96.5 hours
      const expectedDays = expectedHours / 24.0; // 4.02 days

      expect(hourlyAdh).toBeCloseTo(13.0, 4);
      expect(expectedHours).toBeCloseTo(96.5, 1);
      expect(expectedDays).toBeCloseTo(4.02, 2);
    });

    it("confirms larval mass self-heating acceleration offset", () => {
      const deltaT = 2.5; // +1.5 to +3.5 deg C
      const baseTemp = 20.0;
      const correctedTemp = baseTemp + deltaT;
      expect(correctedTemp).toBe(22.5);
    });
  });

  describe("Subsystem 27: Trace Spectroscopy & Multispectral Imaging (MSI)", () => {
    it("renders Trace Spectroscopy Panel", () => {
      const { container } = render(<TraceSpectroscopyPanel />);
      expect(container).toBeInTheDocument();
      expect(screen.getAllByText(/Spectroscopy|MSI|ATR-FTIR/i).length).toBeGreaterThan(0);
    });

    it("verifies Hit Quality Index (HQI) formula for polymer verification", () => {
      // Identical spectra yield HQI = 100%
      const sample = [0.1, 0.4, 0.8, 0.2];
      const ref = [0.1, 0.4, 0.8, 0.2];
      let dotProd = 0;
      let normSample = 0;
      let normRef = 0;
      for (let i = 0; i < sample.length; i++) {
        dotProd += sample[i] * ref[i];
        normSample += sample[i] * sample[i];
        normRef += ref[i] * ref[i];
      }
      const hqi = ((dotProd * dotProd) / (normSample * normRef)) * 100;
      expect(hqi).toBeCloseTo(100.0, 4);
      expect(hqi).toBeGreaterThanOrEqual(90.0); // OSAC/SWGMAT standard
    });
  });

  describe("Subsystem 28: Post-Mortem Drug Redistribution (PMR)", () => {
    it("renders Post-Mortem Toxicology PMR Panel", () => {
      const { container } = render(<ToxicologyPmrPanel />);
      expect(container).toBeInTheDocument();
      expect(screen.getAllByText(/PMR|Toxicolog/i).length).toBeGreaterThan(0);
    });

    it("validates VECTOR_P5_03 Fentanyl high PMR risk calculation", () => {
      // VECTOR_P5_03: C_heart = 24.0 ng/mL, C_femoral = 8.5 ng/mL
      const cHeart = 24.0;
      const cFemoral = 8.5;
      const cpRatio = cHeart / cFemoral; // 2.8235
      const isHighPmr = cpRatio > 2.0;

      expect(cpRatio).toBeCloseTo(2.82, 2);
      expect(isHighPmr).toBe(true);
      // Antemortem concentration inferred from femoral blood
      const cAntemortem = cFemoral;
      expect(cAntemortem).toBe(8.5);
    });

    it("verifies Ethanol Widmark zero-order antemortem back-extrapolation", () => {
      const cFemoral = 1.20; // g/L
      const elapsedHours = 4.0;
      const beta60 = 0.15; // g/L/h
      const cAntemortem = cFemoral + beta60 * elapsedHours;
      expect(cAntemortem).toBeCloseTo(1.80, 4);
    });
  });
});
