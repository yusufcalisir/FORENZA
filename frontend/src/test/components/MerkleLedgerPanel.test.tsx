import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import MerkleLedgerPanel, {
  buildClientMerkleTree,
  generateClientInclusionProof,
  verifyClientInclusionProof,
  CustodyEvent,
} from "@/components/analysis/MerkleLedgerPanel";
import { SaasLanguageProvider } from "@/context/SaaSLanguageContext";

const MOCK_EVENTS: CustodyEvent[] = [
  {
    event_id: "EVT-001",
    timestamp_iso: "2026-08-16T08:15:00Z",
    officer_id: "DET-MILLER-704",
    sample_barcode: "BC-DNA-99104",
    location_id: "CRIME_SCENE_SECTOR_A",
    action_type: "COLLECTION",
    notes: "Biological swab secured in sterile envelope.",
  },
  {
    event_id: "EVT-002",
    timestamp_iso: "2026-08-16T09:30:00Z",
    officer_id: "OFFICER-CHEN-122",
    sample_barcode: "BC-DNA-99104",
    location_id: "EVIDENCE_TRANSPORT_VEHICLE",
    action_type: "TRANSFER",
    notes: "Chain of custody handoff.",
  },
  {
    event_id: "EVT-003",
    timestamp_iso: "2026-08-16T11:00:00Z",
    officer_id: "TECH-DAVIS-301",
    sample_barcode: "BC-DNA-99104",
    location_id: "CENTRAL_LAB_ACCESSIONING",
    action_type: "ACCESSION",
    notes: "Sample logged into LIMS.",
  },
  {
    event_id: "EVT-004",
    timestamp_iso: "2026-08-16T13:45:00Z",
    officer_id: "DR-CONNOR-042",
    sample_barcode: "BC-DNA-99104",
    location_id: "EXTRACTION_SUITE_B",
    action_type: "EXTRACTION",
    notes: "Magnetic bead DNA extraction.",
  },
];

describe("MerkleLedgerPanel Component (Subsystem 29 / Pillar 6.1)", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("computes deterministic client-side Merkle tree matching Python engine verbatim", () => {
    const tree = buildClientMerkleTree(MOCK_EVENTS);
    expect(tree.merkle_root).toBeDefined();
    expect(tree.merkle_root).toHaveLength(64);
    expect(tree.leaf_hashes).toHaveLength(4);
    expect(tree.total_events).toBe(4);
    expect(tree.tree_depth).toBe(2);

    // Exact expected hash from Python ForensicMerkleLedgerEngine for these 4 events
    expect(tree.merkle_root).toBe("b8a858763e53e99a7a47ee63146e54bfe396eed7867f6ef08ffea7d3dc8f48e5");
  });

  it("generates and verifies valid inclusion proofs across all leaves", () => {
    const tree = buildClientMerkleTree(MOCK_EVENTS);

    for (let i = 0; i < MOCK_EVENTS.length; i++) {
      const proof = generateClientInclusionProof(MOCK_EVENTS, i);
      expect(proof.target_event_index).toBe(i);
      expect(proof.merkle_root).toBe(tree.merkle_root);
      expect(proof.proof_path.length).toBe(2);

      const verification = verifyClientInclusionProof(
        proof.target_leaf_hash,
        proof.proof_path,
        tree.merkle_root
      );
      expect(verification.is_valid).toBe(true);
      expect(verification.computed_root).toBe(tree.merkle_root);
      expect(verification.verdict).toContain("VALID");
    }
  });

  it("detects single-character tampering in leaf verification path", () => {
    const tree = buildClientMerkleTree(MOCK_EVENTS);
    const proof = generateClientInclusionProof(MOCK_EVENTS, 0);

    // Corrupted leaf hash
    const corruptedLeaf = proof.target_leaf_hash.replace(/^[0-9a-f]/, (c) => (c === "a" ? "b" : "a"));
    const verification = verifyClientInclusionProof(corruptedLeaf, proof.proof_path, tree.merkle_root);

    expect(verification.is_valid).toBe(false);
    expect(verification.verdict).toContain("INVALID");
    expect(verification.computed_root).not.toBe(tree.merkle_root);
  });

  it("renders mission bar, custody events timeline, and anchored root commitment", () => {
    render(
      <SaasLanguageProvider>
        <MerkleLedgerPanel />
      </SaasLanguageProvider>
    );

    expect(screen.getByText(/Merkle Tree Chain-of-Custody|Merkle Agaci Delil Zinciri Defteri/i)).toBeInTheDocument();
    expect(screen.getByText(/ISO 17025 • SHA-256 • O\(log2 N\)/i)).toBeInTheDocument();
    expect(screen.getByText(/IMMUTABLE MERKLE ROOT COMMITMENT|DEGISMEZ MERKLE KOK TAAHHUDU/i)).toBeInTheDocument();
    expect(screen.getByText(/ROOT ANCHORED|KOK DOGRULANDI/i)).toBeInTheDocument();
  });

  it("toggles tamper simulation, detecting root divergence and restoring cleanly", async () => {
    render(
      <SaasLanguageProvider>
        <MerkleLedgerPanel />
      </SaasLanguageProvider>
    );

    const tamperBtn = screen.getByRole("button", {
      name: /Simulate Tamper|Mudahale Simule Et/i,
    });
    expect(tamperBtn).toBeInTheDocument();

    // Trigger tamper
    fireEvent.click(tamperBtn);

    await waitFor(() => {
      expect(screen.getAllByText(/DIVERGENT ROOT|BOZULMUS KOK/i)[0]).toBeInTheDocument();
    });

    // Untamper / restore
    const untamperBtn = screen.getByRole("button", {
      name: /Tampered \(\+1s\)|Mudahale Edildi \(\+1s\)/i,
    });
    fireEvent.click(untamperBtn);

    await waitFor(() => {
      expect(screen.getAllByText(/ROOT ANCHORED|KOK DOGRULANDI/i)[0]).toBeInTheDocument();
    });
  });

  it("switches to inclusion proof tab and synthesizes verifiable audit path", async () => {
    render(
      <SaasLanguageProvider>
        <MerkleLedgerPanel />
      </SaasLanguageProvider>
    );

    const proofTabBtn = screen.getByRole("button", {
      name: /Inclusion Proof|Kapsama Ispati/i,
    });
    fireEvent.click(proofTabBtn);

    await waitFor(() => {
      expect(screen.getAllByText(/MERKLE INCLUSION PROOF|MERKLE KAPSAMA ISPATI/i)[0]).toBeInTheDocument();
      expect(
        screen.getByText(/Courtroom Admissibility|Mahkeme Kabul Edilebilirligi/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/VALID \(Admissible Evidence\)|GECERLI: INKAR EDILEMEZ ISPAT/i)
      ).toBeInTheDocument();
    });
  });
});
