import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "@/components/ui/Button";

describe("Button Primitive UI Component", () => {
  it("renders with default props and text content", () => {
    render(<Button>Run MCMC Analysis</Button>);
    const btn = screen.getByRole("button", { name: /Run MCMC Analysis/i });
    expect(btn).toBeInTheDocument();
    expect(btn).toHaveClass("bg-emerald-500");
  });

  it("handles user click events", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Submit Evidence</Button>);
    const btn = screen.getByRole("button", { name: /Submit Evidence/i });
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("disables interaction when disabled prop is true", () => {
    const handleClick = vi.fn();
    render(<Button disabled onClick={handleClick}>Disabled Action</Button>);
    const btn = screen.getByRole("button", { name: /Disabled Action/i });
    expect(btn).toBeDisabled();
    fireEvent.click(btn);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it("displays loading spinner and sets aria-busy when loading", () => {
    render(<Button loading>Processing ZKP</Button>);
    const btn = screen.getByRole("button", { name: /Processing ZKP/i });
    expect(btn).toHaveAttribute("aria-busy", "true");
    expect(btn).toBeDisabled();
  });

  it("applies secondary and danger variant classes correctly", () => {
    const { rerender } = render(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-tactical-surface/90");

    rerender(<Button variant="danger">Emergency Panic</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-rose-500/20");
  });
});
