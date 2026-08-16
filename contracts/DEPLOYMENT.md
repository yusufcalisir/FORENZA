# FORENZA Cryptographic Smart Contracts — Deployment Guide

This guide details the compilation, unit testing, testnet deployment, and verification procedures for the **FORENZA: Forensic Evidence Operating System** on-chain layer.

---

## 📋 System Prerequisites

- **Node.js**: $\ge 18.18.0$
- **npm**: $\ge 9.0.0$
- **Hardhat**: $\ge 2.22.0$

---

## ⚙️ 1. Compilation & Test Verification

```bash
cd contracts
npm install
npm run compile
npm test
```

Expected output:
```
  20 passing (2s)
```

---

## 🌐 2. Network Configuration & Environment Variables

Create or update your `.env` file in the root workspace or in `contracts/`:

```env
# Polygon Amoy Testnet (Chain ID: 80002)
POLYGON_AMOY_RPC="https://rpc.ankr.com/polygon_amoy"

# Ethereum Sepolia Testnet (Chain ID: 11155111)
SEPOLIA_RPC_URL="https://rpc.ankr.com/eth_sepolia"

# Deployer Private Key (Must hold native testnet tokens MATIC/ETH for gas)
DEPLOYER_PRIVATE_KEY="0xYOUR_HEX_PRIVATE_KEY"
```

---

## 🚀 3. Deploying to Networks

### Local Hardhat Node
```bash
# Terminal 1
npx hardhat node

# Terminal 2
npm run deploy:local
```

### Polygon Amoy Testnet
```bash
npm run deploy:amoy
```

### Ethereum Sepolia Testnet
```bash
npm run deploy:sepolia
```

Deployment will emit contract addresses to `contracts/deployed_addresses.json`:
```json
{
  "network": "polygonAmoy",
  "contracts": {
    "ForenzaAuditRegistry": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "ForensicMerkleLedger": "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
    "Groth16ZkpVerifier": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
  }
}
```

---

## 🔗 4. Web3 & Frontend Integration

### FastAPI Backend Integration
Copy the deployed addresses into `backend/.env`:
```env
FORENZA_AUDIT_REGISTRY_CONTRACT="0x..."
FORENSIC_MERKLE_LEDGER_CONTRACT="0x..."
GROTH16_ZKP_VERIFIER_CONTRACT="0x..."
```

### Next.js Frontend Integration
Copy the deployed address into `frontend/.env.local`:
```env
NEXT_PUBLIC_AUDIT_CONTRACT_ADDRESS="0x..."
NEXT_PUBLIC_MERKLE_LEDGER_ADDRESS="0x..."
NEXT_PUBLIC_ZKP_VERIFIER_ADDRESS="0x..."
```

---

## 🛡️ 5. Post-Deployment Laboratory Onboarding

```javascript
const registry = await ethers.getContractAt("ForenzaAuditRegistry", auditRegistryAddress);

// 1. Enroll forensic analyst
const LAB_ANALYST_ROLE = await registry.LAB_ANALYST_ROLE();
await registry.enrollInvestigator(
    "0xAnalystWalletAddress",
    "Dr. Marcus Alvarez",
    "Forensic Science Ireland",
    "ISO/IEC 17025:2017",
    LAB_ANALYST_ROLE
);

// 2. Provision cryptographically bound session token
const sessionToken = ethers.keccak256(ethers.toUtf8Bytes("LAB_SESSION_TOKEN_01"));
await registry.grantSession("0xAnalystWalletAddress", sessionToken, 86400); // 24 hours
```
