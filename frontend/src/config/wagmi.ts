import { http, createConfig } from 'wagmi'
import { mainnet, sepolia, polygonAmoy } from 'wagmi/chains'
import { injected } from 'wagmi/connectors'

// Stable public RPC endpoints
const POLYGON_AMOY_RPC = 'https://rpc.ankr.com/polygon_amoy'
const SEPOLIA_RPC = 'https://rpc.ankr.com/eth_sepolia'
const MAINNET_RPC = 'https://rpc.ankr.com/eth'

export const config = createConfig({
    chains: [polygonAmoy, sepolia, mainnet],
    connectors: [
        injected(),
    ],
    ssr: true,
    pollingInterval: 30_000,
    transports: {
        [polygonAmoy.id]: http(POLYGON_AMOY_RPC),
        [sepolia.id]: http(SEPOLIA_RPC),
        [mainnet.id]: http(MAINNET_RPC),
    },
})

// ========================= FORENZA Smart Contract ABIs =========================

/// 1. ForenzaAuditRegistry ABI (Pillar 6 Governance & ISO 17025 RBAC)
export const forenzaAuditRegistryABI = [
    {
        "anonymous": false,
        "inputs": [
            { "indexed": true, "internalType": "uint256", "name": "logIndex", "type": "uint256" },
            { "indexed": true, "internalType": "address", "name": "investigator", "type": "address" },
            { "indexed": false, "internalType": "string", "name": "queryType", "type": "string" },
            { "indexed": false, "internalType": "bytes32", "name": "profileHash", "type": "bytes32" },
            { "indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256" }
        ],
        "name": "QueryLogged",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            { "indexed": true, "internalType": "address", "name": "investigator", "type": "address" },
            { "indexed": false, "internalType": "uint8", "name": "status", "type": "uint8" }
        ],
        "name": "InvestigatorStatusUpdated",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            { "indexed": true, "internalType": "address", "name": "investigator", "type": "address" },
            { "indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256" }
        ],
        "name": "RateLimitExceeded",
        "type": "event"
    },
    {
        "inputs": [
            { "internalType": "string", "name": "_queryType", "type": "string" },
            { "internalType": "bytes32", "name": "_profileHash", "type": "bytes32" },
            { "internalType": "bytes32", "name": "_sessionToken", "type": "bytes32" }
        ],
        "name": "logQuery",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            { "internalType": "address", "name": "investigator", "type": "address" }
        ],
        "name": "isInvestigatorAuthorized",
        "outputs": [{ "internalType": "bool", "name": "", "type": "bool" }],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getLogCount",
        "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
        "stateMutability": "view",
        "type": "function"
    }
] as const

/// 2. ForensicMerkleLedger ABI (Module 26 Merkle Chain of Custody)
export const forensicMerkleLedgerABI = [
    {
        "anonymous": false,
        "inputs": [
            { "indexed": true, "internalType": "bytes32", "name": "caseId", "type": "bytes32" },
            { "indexed": true, "internalType": "bytes32", "name": "merkleRoot", "type": "bytes32" },
            { "indexed": false, "internalType": "uint256", "name": "leafCount", "type": "uint256" },
            { "indexed": true, "internalType": "address", "name": "registeredBy", "type": "address" },
            { "indexed": false, "internalType": "string", "name": "metadataUri", "type": "string" },
            { "indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256" }
        ],
        "name": "CaseMerkleRootCommitted",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            { "indexed": true, "internalType": "bytes32", "name": "caseId", "type": "bytes32" },
            { "indexed": true, "internalType": "bytes32", "name": "eventId", "type": "bytes32" },
            { "indexed": true, "internalType": "bytes32", "name": "leafHash", "type": "bytes32" },
            { "indexed": false, "internalType": "address", "name": "officer", "type": "address" },
            { "indexed": false, "internalType": "string", "name": "officerId", "type": "string" },
            { "indexed": false, "internalType": "string", "name": "sampleBarcode", "type": "string" },
            { "indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256" }
        ],
        "name": "CustodyEventAnchored",
        "type": "event"
    },
    {
        "inputs": [
            { "internalType": "bytes32", "name": "caseId", "type": "bytes32" },
            { "internalType": "bytes32", "name": "merkleRoot", "type": "bytes32" },
            { "internalType": "uint256", "name": "leafCount", "type": "uint256" },
            { "internalType": "string", "name": "metadataUri", "type": "string" }
        ],
        "name": "commitCaseMerkleRoot",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            { "internalType": "bytes32", "name": "leafHash", "type": "bytes32" },
            { "internalType": "bytes32[]", "name": "siblings", "type": "bytes32[]" },
            { "internalType": "uint256", "name": "pathBits", "type": "uint256" },
            { "internalType": "bytes32", "name": "expectedRoot", "type": "bytes32" }
        ],
        "name": "verifyInclusionProof",
        "outputs": [{ "internalType": "bool", "name": "isValid", "type": "bool" }],
        "stateMutability": "pure",
        "type": "function"
    }
] as const

/// 3. Groth16ZkpVerifier ABI (Module 27 BN254 Pairings Verifier)
export const groth16ZkpVerifierABI = [
    {
        "anonymous": false,
        "inputs": [
            { "indexed": true, "internalType": "bytes32", "name": "evidenceHash", "type": "bytes32" },
            { "indexed": false, "internalType": "uint256", "name": "matchThreshold", "type": "uint256" },
            { "indexed": true, "internalType": "bytes32", "name": "suspectCommitment", "type": "bytes32" },
            { "indexed": false, "internalType": "bool", "name": "isValid", "type": "bool" },
            { "indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256" }
        ],
        "name": "BlindMatchVerified",
        "type": "event"
    },
    {
        "inputs": [
            { "internalType": "bytes32", "name": "evidenceHash", "type": "bytes32" },
            { "internalType": "uint256", "name": "matchThreshold", "type": "uint256" },
            { "internalType": "bytes32", "name": "suspectCommitment", "type": "bytes32" },
            { "internalType": "uint256[2]", "name": "a", "type": "uint256[2]" },
            { "internalType": "uint256[2][2]", "name": "b", "type": "uint256[2][2]" },
            { "internalType": "uint256[2]", "name": "c", "type": "uint256[2]" }
        ],
        "name": "verifyDnaMatchProof",
        "outputs": [{ "internalType": "bool", "name": "isValid", "type": "bool" }],
        "stateMutability": "nonpayable",
        "type": "function"
    }
] as const

// Backward-compatible alias
export const forensicAuditABI = forenzaAuditRegistryABI;
