import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Input } from "@/components/ui/Input";

describe("Input Primitive UI Component", () => {
  it("renders with label and placeholder", () => {
    render(<Input label="STR Locus TH01" placeholder="9.3" />);
    expect(screen.getByLabelText(/STR Locus TH01/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("9.3")).toBeInTheDocument();
  });

  it("handles text change inputs", () => {
    const handleChange = vi.fn();
    render(<Input label="Allele Call" onChange={handleChange} />);
    const input = screen.getByLabelText(/Allele Call/i);
    fireEvent.change(input, { target: { value: "14, 17" } });
    expect(handleChange).toHaveBeenCalled();
  });

  it("displays error message and styles when error prop is present", () => {
    render(<Input label="Peak Height" error="RFU below analytical threshold (50 RFU)" />);
    expect(screen.getByText(/RFU below analytical threshold/i)).toBeInTheDocument();
    const input = screen.getByLabelText(/Peak Height/i);
    expect(input).toHaveClass("border-rose-500/60");
  });

  it("renders clear button and calls onClear when clicked", () => {
    const handleClear = vi.fn();
    render(<Input label="Case ID" value="CASE-2026-001" onClear={handleClear} onChange={() => {}} />);
    const clearBtn = screen.getByRole("button", { name: /Clear input/i });
    expect(clearBtn).toBeInTheDocument();
    fireEvent.click(clearBtn);
    expect(handleClear).toHaveBeenCalledTimes(1);
  });
});
