# FORENZA Protocol Buffer Schemas (`@forenza/proto`)

This package contains the canonical Protocol Buffer (v3) schemas for the **FORENZA Multi-Omic Biocomputational Intelligence Platform**. These definitions enable low-latency, strongly-typed gRPC communication and serialization across federated nodes, microservices, and storage layers.

---

## 1. Schema Catalog

| Schema File | Package | Description |
| :--- | :--- | :--- |
| [`genomic_profile.proto`](./genomic_profile.proto) | `forenza.genomics` | 24-Locus STR profiles, SNP markers, mtDNA rCRS alignments, and vector representations. |
| [`evidence_audit.proto`](./evidence_audit.proto) | `forenza.audit` | ISO 17025 HMAC-SHA256 audit log transactions, chain-of-custody ledgers, and Merkle verification. |
| [`forensic_case.proto`](./forensic_case.proto) | `forenza.cases` | Case lifecycle management, DVI mass fatality references, and court admissibility metadata. |
| [`zkp_proof.proto`](./zkp_proof.proto) | `forenza.zkp` | Circom Groth16 zero-knowledge proof interchange payloads over BN254 elliptic curves. |

---

## 2. Compilation & Stub Generation

### TypeScript / JavaScript Stubs
```bash
npm run build:ts
```

### Python Stubs
```bash
npm run build:py
```
