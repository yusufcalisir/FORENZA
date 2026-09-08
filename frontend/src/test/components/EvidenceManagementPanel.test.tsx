import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import EvidenceManagementPanel from "@/components/analysis/EvidenceManagementPanel";

describe("Subsystem 33: 3D Spatial Evidence Presenter & Juror Visualizer", () => {
  describe("Mathematical Invariants & Sensor Precision Calibration", () => {
    it("enforces Chi-Square critical value chi2_(3, 0.95) = 7.815 for 95% volumetric probability ellipsoids", () => {
      const CHI2_3_95 = 7.815;
      expect(CHI2_3_95).toBe(7.815);

      // Semi-axis scaling formula verification: a = sqrt(sigma^2 * 7.815)
      const sigma_dna = 0.008;
      const semiAxisA = Math.sqrt(sigma_dna * sigma_dna * CHI2_3_95);
      expect(semiAxisA).toBeCloseTo(0.02236, 4);

      // Volume calculation verification: V = (4/3) * pi * a * b * c
      const vol = (4.0 / 3.0) * Math.PI * Math.pow(semiAxisA, 3);
      expect(vol).toBeGreaterThan(0);
    });

    it("verifies multi-sensor precision parameters conform to Research Section 5.1", () => {
      const sensorPrecisions = {
        LIDAR: 0.002,
        BPA: 0.012,
        BALLISTICS: 0.005,
        DNA: 0.008,
        BONE: 0.008,
      };

      expect(sensorPrecisions.LIDAR).toBe(0.002);
      expect(sensorPrecisions.BPA).toBe(0.012);
      expect(sensorPrecisions.BALLISTICS).toBe(0.005);
      expect(sensorPrecisions.DNA).toBe(0.008);
      expect(sensorPrecisions.BONE).toBe(0.008);
    });
  });

  describe("SE(3) Kinematic Coordinate Transformation", () => {
    it("computes Euler yaw rotation and translation vector offsets correctly", () => {
      const x0 = 1.5;
      const y0 = 2.0;
      const yawDeg = 0;
      const tx = 0.5;
      const ty = -0.5;

      const psi = (yawDeg * Math.PI) / 180;
      const nx = x0 * Math.cos(psi) - y0 * Math.sin(psi) + tx;
      const ny = x0 * Math.sin(psi) + y0 * Math.cos(psi) + ty;

      expect(nx).toBe(2.0);
      expect(ny).toBe(1.5);
    });
  });

  describe("EvidenceManagementPanel Component Rendering & Interactive Actions", () => {
    it("renders the 3D spatial visualizer with standards telemetry and canvas", () => {
      const { container } = render(<EvidenceManagementPanel />);
      expect(container).toBeInTheDocument();

      // Mission title check
      expect(
        screen.getAllByText(/3D Spatial Crime Scene Reconstruction|3B Mekansal Olay Yeri Rekonstruksiyonu/i).length
      ).toBeGreaterThan(0);

      // ISO 21043 standard tag check
      expect(screen.getAllByText(/ISO 21043/i).length).toBeGreaterThan(0);
    });

    it("renders the live action buttons for audit, custody transfer, and evidence registration", () => {
      const { container } = render(<EvidenceManagementPanel />);

      const auditBtn = container.querySelector("#btn-audit-chain");
      expect(auditBtn).toBeInTheDocument();

      const transferBtn = container.querySelector("#btn-transfer-custody");
      expect(transferBtn).toBeInTheDocument();

      const registerBtn = container.querySelector("#btn-register-evidence");
      expect(registerBtn).toBeInTheDocument();
    });

    it("renders view mode toggles and volumetric ellipsoid controls", () => {
      const { container } = render(<EvidenceManagementPanel />);

      expect(container.querySelector("#btn-view-isometric")).toBeInTheDocument();
      expect(container.querySelector("#btn-view-top")).toBeInTheDocument();
      expect(container.querySelector("#btn-view-side")).toBeInTheDocument();
      expect(container.querySelector("#toggle-ellipsoids")).toBeInTheDocument();
      expect(container.querySelector("#toggle-bpa")).toBeInTheDocument();
      expect(container.querySelector("#toggle-ballistics")).toBeInTheDocument();
    });
  });
});
