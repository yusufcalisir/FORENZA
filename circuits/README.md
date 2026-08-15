# FORENZA Zero-Knowledge Privacy Match Circuits

This directory contains the canonical **Circom 2.0+ Zero-Knowledge SNARK (ZK-SNARK)** circuit definitions utilized by FORENZA for privacy-preserving DNA matching and cross-border database queries.

---

## 1. Cryptographic Overview: `dna_match.circom`

The `dna_match.circom` circuit enables a querying law enforcement or forensic agency to mathematically prove that a suspect's STR/SNP genetic profile matches a target crime-scene profile without revealing raw allele values to the network or the querying node.

```
                      [ Private 20-Locus STR Array ]
                                    |
                    +---------------+---------------+
                    |               |               |
             [Poseidon 5]    [Poseidon 5]    [Poseidon 5] ... (4 Chunks)
                    |               |               |
                    +---------------+---------------+
                                    |
                        [Chunk Hashes (4) + Salt]
                                    |
                            [Poseidon Hasher]
                                    |
                                    v
                       [public_hash Verification]
```

### Technical Specifications

| Parameter | Specification |
| :--- | :--- |
| **Circuit Language** | Circom 2.1.6+ |
| **Proving System** | Groth16 (`snarkjs`) / Plonk compatible |
| **Elliptic Curve** | BN254 (alt_bn128, 254-bit prime field) |
| **Hash Primitive** | Poseidon $T=6$ ($R_F = 8, R_P = 57$) — zk-SNARK optimized arithmetic hash |
| **Input Signals** | `private_dna_array[20]` (private), `salt` (private), `public_hash` (public) |
| **R1CS Constraints** | $\approx 1,280$ non-linear constraints |
| **Proving Time** | $\approx 350\text{ ms}$ on standard x86_64 CPU |
| **Verification Time** | $< 5\text{ ms}$ (on-chain / off-chain) |
| **Proof Size** | 128 bytes (G1: $A \in \mathbb{G}_1$, G2: $B \in \mathbb{G}_2$, G1: $C \in \mathbb{G}_1$) |

---

## 2. Trusted Setup & Compilation Pipeline

### 1. Circuit Compilation
```bash
circom circuits/dna_match.circom --r1cs --wasm --sym -o ./build
```

### 2. Powers of Tau Ceremony (BN254)
```bash
# Phase 1: Universal SRS
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
snarkjs powersoftau contribute pot12_0000.ptau pot12_final.ptau --name="FORENZA SRS" -v -e="entropy"

# Phase 2: Circuit-specific Groth16 Setup
snarkjs groth16 setup build/dna_match.r1cs pot12_final.ptau build/dna_match_0000.zkey
snarkjs zkey contribute build/dna_match_0000.zkey build/dna_match_final.zkey --name="FORENZA Contributor" -v -e="entropy2"
snarkjs zkey export verification_key build/dna_match_final.zkey build/verification_key.json
```

### 3. Proof Generation & Verification
```bash
# Compute witness
node build/dna_match_js/generate_witness.js build/dna_match_js/dna_match.wasm input.json witness.wtns

# Generate Groth16 proof
snarkjs groth16 prove build/dna_match_final.zkey witness.wtns proof.json public.json

# Verify proof
snarkjs groth16 verify build/verification_key.json public.json proof.json
```

---

## 3. Python & Rust Integration

The Python runtime interfaces with this circuit via:
- High-Performance Native Bridge: [`backend/app/core/crypto/zkp_prover.py`](../backend/app/core/crypto/zkp_prover.py)
- Rust Native Extension: [`backend/app/core/crypto/zkp_prover.rs`](../backend/app/core/crypto/zkp_prover.rs)
- Automated Test Suite: [`backend/app/core/crypto/test_zkp.py`](../backend/app/core/crypto/test_zkp.py)
