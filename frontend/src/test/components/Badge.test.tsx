import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Badge } from "@/components/ui/Badge";

describe("Badge Primitive UI Component", () => {
  it("renders with children text", () => {
    render(<Badge>ISO/IEC 17025</Badge>);
    expect(screen.getByText(/ISO\/IEC 17025/i)).toBeInTheDocument();
  });

  it("renders with dot indicator", () => {
    const { container } = render(<Badge dot variant="emerald">ONLINE</Badge>);
    const dot = container.querySelector(".rounded-full");
    expect(dot).toBeInTheDocument();
    expect(dot).toHaveClass("bg-emerald-400");
  });
});
