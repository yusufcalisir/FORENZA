import { http, createConfig } from 'wagmi'
import { mainnet, sepolia, polygonAmoy } from 'wagmi/chains'
import { injected } from 'wagmi/connectors'

// Use stable public RPC endpoints to avoid ERR_NAME_NOT_RESOLVED errors
// and the infinite requestAnimationFrame retry loop that follows.
const POLYGON_AMOY_RPC = 'https://rpc.ankr.com/polygon_amoy'
const SEPOLIA_RPC = 'https://rpc.ankr.com/eth_sepolia'
const MAINNET_RPC = 'https://rpc.ankr.com/eth'

export const config = createConfig({
    chains: [polygonAmoy, sepolia, mainnet],
    connectors: [
        injected(),
    ],
    ssr: true,
    // Increase polling interval from default 4s to 30s to avoid console spam
    // when wallet is not connected or RPC is unreachable.
    pollingInterval: 30_000,
    transports: {
        [polygonAmoy.id]: http(POLYGON_AMOY_RPC),
        [sepolia.id]: http(SEPOLIA_RPC),
        [mainnet.id]: http(MAINNET_RPC),
    },
})

// ForensicAudit ABI (Events + View Functions)
export const forensicAuditABI = [
    {
        "anonymous": false,
        "inputs": [
            { "indexed": true, "internalType": "uint256", "name": "logIndex", "type": "uint256" },
            { "indexed": true, "internalType": "address", "name": "investigator_id", "type": "address" },
            { "indexed": false, "internalType": "string", "name": "query_type", "type": "string" },
            { "indexed": false, "internalType": "bytes32", "name": "profile_hash", "type": "bytes32" },
            { "indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256" }
        ],
        "name": "QueryLogged",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            { "indexed": true, "internalType": "address", "name": "investigator_id", "type": "address" },
            { "indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256" }
        ],
        "name": "InvestigatorSuspended",
        "type": "event"
    }
] as const
