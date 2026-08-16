# FORENZA On-Chain Cryptographic Subsystem (`contracts/`)

This directory contains the Solidity smart contracts, hardhat testing harness, and automated deployment pipelines for the **FORENZA: Forensic Evidence Operating System**.

---

## 🏛️ Smart Contract Architecture

| Contract | Module | Purpose | Standards |
| :--- | :--- | :--- | :--- |
| **`ForensicMerkleLedger.sol`** | **Module 26** | Binary Merkle Tree Case Root Commitments & $O(\log_2 N)$ Inclusion Proofs | ISO/IEC 17025:2017 §7.6, NIST SP 800-106 |
| **`Groth16ZkpVerifier.sol`** | **Module 27** | On-Chain zk-SNARK BN254 Multi-Pairing Blind DNA Match Verification | Circom 2.1+, BN254 / alt_bn128 |
| **`ForenzaAuditRegistry.sol`** | **Pillar 6 Governance** | Enterprise RBAC (`LAB_ANALYST`, `LEGAL_AUDITOR`, `COURT_OFFICER`), Session Tokens, Sliding Rate-Limiting & Lockdown Circuit Breaker | ISO/IEC 17025:2017 §8.3, FRE Rule 702 |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Compile Contracts
```bash
npm run compile
```

### 3. Run Automated Unit Tests (100% Passing)
```bash
npm test
```

### 4. Deploy Contracts
- **Local Hardhat Network:**
  ```bash
  npm run deploy:local
  ```
- **Polygon Amoy Testnet:**
  ```bash
  npm run deploy:amoy
  ```
- **Ethereum Sepolia Testnet:**
  ```bash
  npm run deploy:sepolia
  ```

---

## 📂 Directory Layout

```
contracts/
├── src/
│   ├── ForenzaAuditRegistry.sol   # ISO 17025 RBAC & Query Audit Trail
│   ├── ForensicMerkleLedger.sol   # Module 26 Merkle Chain of Custody
│   └── Groth16ZkpVerifier.sol     # Module 27 BN254 Pairing Verifier
├── test/
│   ├── ForenzaAuditRegistry.test.js
│   ├── ForensicMerkleLedger.test.js
│   └── Groth16ZkpVerifier.test.js
├── scripts/
│   └── deploy.js                  # Multi-contract deployment pipeline
├── hardhat.config.js              # Solidity 0.8.24, viaIR, optimizer config
├── DEPLOYMENT.md                  # Comprehensive deployment manual
└── package.json
```
