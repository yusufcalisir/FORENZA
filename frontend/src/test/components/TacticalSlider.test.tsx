import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TacticalSlider } from "@/components/ui/TacticalSlider";

describe("TacticalSlider Primitive UI Component", () => {
  it("renders with label, current value badge, and min/max limits", () => {
    render(
      <TacticalSlider
        label="Theta Subpopulation (Fst)"
        value={0.03}
        min={0.0}
        max={0.05}
        step={0.005}
        unit=""
        onChange={() => {}}
      />
    );
    expect(screen.getByText(/Theta Subpopulation/i)).toBeInTheDocument();
    expect(screen.getByText("0.03")).toBeInTheDocument();
    expect(screen.getByText("0")).toBeInTheDocument();
    expect(screen.getByText("0.05")).toBeInTheDocument();
  });

  it("calls onChange callback when slider value changes", () => {
    const handleChange = vi.fn();
    render(
      <TacticalSlider
        label="Dropout Rate"
        value={0.2}
        min={0.0}
        max={1.0}
        step={0.05}
        onChange={handleChange}
      />
    );
    const slider = screen.getByRole("slider", { name: /Dropout Rate/i });
    fireEvent.change(slider, { target: { value: "0.45" } });
    expect(handleChange).toHaveBeenCalledWith(0.45);
  });
});
