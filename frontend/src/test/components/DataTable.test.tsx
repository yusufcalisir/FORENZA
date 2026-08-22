import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DataTable, Column } from "@/components/ui/DataTable";

interface ForensicRecord extends Record<string, any> {
  id: string;
  locus: string;
  allele: string;
  rfu: number;
}

const mockColumns: Column<ForensicRecord>[] = [
  { key: "id", header: "ID", sortable: true },
  { key: "locus", header: "Locus", sortable: true },
  { key: "allele", header: "Allele" },
  { key: "rfu", header: "Peak Height (RFU)", sortable: true, align: "right" },
];

const mockData: ForensicRecord[] = [
  { id: "REC-01", locus: "D3S1358", allele: "15, 16", rfu: 1420 },
  { id: "REC-02", locus: "vWA", allele: "17, 18", rfu: 2150 },
  { id: "REC-03", locus: "FGA", allele: "21, 24", rfu: 890 },
];

describe("DataTable Primitive UI Component", () => {
  it("renders table headers and rows correctly", () => {
    render(<DataTable columns={mockColumns} data={mockData} />);
    expect(screen.getByText("D3S1358")).toBeInTheDocument();
    expect(screen.getByText("vWA")).toBeInTheDocument();
    expect(screen.getByText("FGA")).toBeInTheDocument();
  });

  it("filters rows based on search input", () => {
    render(<DataTable columns={mockColumns} data={mockData} />);
    const searchInput = screen.getByPlaceholderText(/Search records/i);
    fireEvent.change(searchInput, { target: { value: "vWA" } });

    expect(screen.getByText("vWA")).toBeInTheDocument();
    expect(screen.queryByText("D3S1358")).not.toBeInTheDocument();
  });

  it("shows empty message when no rows match query", () => {
    render(<DataTable columns={mockColumns} data={mockData} emptyMessage="No loci found." />);
    const searchInput = screen.getByPlaceholderText(/Search records/i);
    fireEvent.change(searchInput, { target: { value: "NON_EXISTENT_LOCUS" } });

    expect(screen.getByText("No loci found.")).toBeInTheDocument();
  });
});
