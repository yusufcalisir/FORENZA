import hashlib
import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

import importlib

# Safe dynamic Web3 import with graceful fallback to eliminate static IDE diagnostics
Web3: Any = None
geth_poa_middleware: Any = None
HAS_WEB3: bool = False

try:
    _web3_mod = importlib.import_module("web3")
    Web3 = getattr(_web3_mod, "Web3", None)
    try:
        _mw_mod = importlib.import_module("web3.middleware")
        geth_poa_middleware = getattr(_mw_mod, "geth_poa_middleware", None) or getattr(_mw_mod, "ExtraDataToPOAMiddleware", None)
    except Exception:
        geth_poa_middleware = None
    HAS_WEB3 = (Web3 is not None)
except Exception:
    Web3 = None
    geth_poa_middleware = None
    HAS_WEB3 = False

from app.core.config import settings

# Embedded ABI fallback for ForenzaAuditRegistry
FORENZA_AUDIT_REGISTRY_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_queryType", "type": "string"},
            {"internalType": "bytes32", "name": "_profileHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "_sessionToken", "type": "bytes32"}
        ],
        "name": "logQuery",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_investigator", "type": "address"},
            {"internalType": "bytes32", "name": "_sessionToken", "type": "bytes32"},
            {"internalType": "uint256", "name": "_durationSeconds", "type": "uint256"}
        ],
        "name": "grantSession",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "investigator", "type": "address"}],
        "name": "isInvestigatorAuthorized",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "investigator", "type": "address"}],
        "name": "profiles",
        "outputs": [
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "bool", "name": "isAuthorized", "type": "bool"},
            {"internalType": "uint256", "name": "createdAt", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "paused",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getLogCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class BlockchainError(Exception):
    """Custom exception raised for FORENZA on-chain smart contract errors."""
    def __init__(self, message: str, reason: str = "TRANSACTION_FAILED"):
        super().__init__(message)
        self.reason = reason

class ForenzaWeb3Service:
    """
    FORENZA High-Security Web3 Cryptographic Ledger Service.
    Interfaces with ForenzaAuditRegistry, ForensicMerkleLedger, and Groth16ZkpVerifier.
    """
    def __init__(self):
        if not HAS_WEB3 or Web3 is None:
            self.w3 = None
            self.contract = None
            self.account = None
            self.abi = FORENZA_AUDIT_REGISTRY_ABI
            return

        self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
        try:
            if geth_poa_middleware:
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except Exception:
            pass 
        
        self.contract_address = settings.FORENSIC_AUDIT_CONTRACT
        self.private_key = settings.DEPLOYER_PRIVATE_KEY
        self.account = self.w3.eth.account.from_key(self.private_key) if (self.private_key and self.w3) else None
        
        # Load ABI from artifacts or fallback
        self.abi = self._load_abi()
        
        if self.contract_address and self.abi and self.w3:
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
        else:
            self.contract = None

    def _load_abi(self) -> List[Dict[str, Any]]:
        candidate_paths = [
            os.path.join(os.path.dirname(__file__), "../../../../contracts/artifacts/src/ForenzaAuditRegistry.sol/ForenzaAuditRegistry.json"),
        ]
        for path in candidate_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                        return data.get("abi", FORENZA_AUDIT_REGISTRY_ABI)
                except Exception:
                    pass
        return FORENZA_AUDIT_REGISTRY_ABI

    def is_connected(self) -> bool:
        if not self.w3:
            return False
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    def is_investigator_authorized(self, investigator_address: str) -> bool:
        """
        Checks if the investigator is authorized and if the system is not paused.
        """
        if not self.contract or not self.is_connected():
            return False

        try:
            is_paused = self.contract.functions.paused().call()
            if is_paused:
                logger.warning("[ForenzaWeb3] System is in LOCKDOWN mode.")
                return False

            profile = self.contract.functions.profiles(investigator_address).call()
            return profile[1] # isAuthorized

        except Exception as e:
            logger.error(f"[ForenzaWeb3] Error checking authorization: {e}")
            return False

    def check_authorization(self, investigator_address: str) -> tuple[bool, str]:
        """
        Backward-compatible authorization check returning (is_authorized, status_code).
        """
        if self.is_investigator_authorized(investigator_address):
            return (True, "AUTHORIZED")
        return (False, "NO_TOKEN")

    def _check_gas_funds(self) -> bool:
        """Helper to ensure the deployer account has funds for gas."""
        if not self.account or not self.w3:
            return False
        try:
            balance = self.w3.eth.get_balance(self.account.address)
            if balance == 0:
                logger.error(f"[CRITICAL] Deployer account {self.account.address} has 0 gas funds!")
                return False
            return True
        except Exception as e:
            logger.warning(f"[WARN] Could not check balance: {e}")
            return True

    def grant_session(self, investigator_address: str, session_token: str) -> str:
        """
        Admin Action: Grants a session token to an investigator on-chain.
        """
        if not self.contract or not self.account or not self.w3:
            raise Exception("Contract or account not loaded")
        
        if not self._check_gas_funds():
            raise Exception("Deployer wallet has 0 funds for gas.")
            
        try:
            token_bytes = Web3.keccak(text=session_token) if not session_token.startswith("0x") else session_token
            func = self.contract.functions.grantSession(
                investigator_address,
                token_bytes,
                86400 # 24 hours
            )
            
            chain_id = self.w3.eth.chain_id
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            try:
                gas_estimate = func.estimate_gas({'from': self.account.address})
                gas_limit = int(gas_estimate * 1.2)
            except Exception:
                gas_limit = 2000000

            tx_data = func.build_transaction({
                'chainId': chain_id,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return self.w3.to_hex(tx_hash)
            else:
                raise Exception("Grant Session reverted on-chain")
                
        except Exception as e:
            logger.error(f"[ForenzaWeb3] Grant Session Error: {e}")
            raise e

    def log_query_to_blockchain(self, investigator_address: str, profile_hash: str, query_type: str, session_token: str) -> str:
        """
        Logs the forensic query to the blockchain. Returns transaction hash if successful.
        """
        if not self.contract or not self.account or not self.w3:
            raise Exception("Contract or account not loaded")

        if not self._check_gas_funds():
            raise Exception("Deployer wallet empty")

        try:
            hash_bytes = Web3.keccak(text=profile_hash) if not profile_hash.startswith("0x") else profile_hash
            token_bytes = Web3.keccak(text=session_token) if not session_token.startswith("0x") else session_token

            func = self.contract.functions.logQuery(
                query_type,
                hash_bytes,
                token_bytes
            )
            
            chain_id = self.w3.eth.chain_id
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            try:
                gas_estimate = func.estimate_gas({'from': self.account.address})
                gas_limit = int(gas_estimate * 1.2)
            except Exception:
                gas_limit = 2000000
            
            tx_data = func.build_transaction({
                'chainId': chain_id,
                'gas': gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return self.w3.to_hex(tx_hash)
            else:
                raise Exception("Transaction reverted on-chain")
                
        except Exception as e:
            logger.error(f"[ForenzaWeb3] Blockchain Logging Error: {e}")
            raise BlockchainError(str(e), "LOG_QUERY_FAILED")

    def log_query(self, investigator_address: str, query_type: str, profile_id: str, session_token: str = "") -> str:
        """
        Convenience alias for log_query_to_blockchain.
        """
        return self.log_query_to_blockchain(
            investigator_address=investigator_address,
            profile_hash=profile_id,
            query_type=query_type,
            session_token=session_token or "DEFAULT_SESSION"
        )

    def log_mpc_result(self, session_id: str, result_hash: str, relationship_type: str, kinship_percent: float) -> str:
        """
        Wrapper to log MPC-specific results using the forensic query logger.
        """
        query_type = f"MPC_KINSHIP:{relationship_type}:{int(kinship_percent * 100)}%"
        system_address = "0x0000000000000000000000000000000000000000"
        
        return self.log_query_to_blockchain(
            investigator_address=system_address,
            profile_hash=result_hash,
            query_type=query_type,
            session_token=session_id
        )


# Backward-compatible alias
VantageAuditService = ForenzaWeb3Service

# ── Singleton factory ──────────────────────────────────────────────────────────
_service_instance: ForenzaWeb3Service | None = None

def get_service() -> ForenzaWeb3Service | None:
    """
    Lazy singleton. Returns None when blockchain config is absent or web3 is not installed,
    allowing the rest of the backend to operate cleanly in all environments.
    """
    global _service_instance
    if _service_instance is not None:
        return _service_instance

    if not HAS_WEB3 or Web3 is None or not settings.WEB3_PROVIDER_URL or not settings.DEPLOYER_PRIVATE_KEY:
        return None

    try:
        _service_instance = ForenzaWeb3Service()
        return _service_instance
    except Exception as e:
        logger.warning(f"[web3_service] Could not initialise ForenzaWeb3Service: {e}")
        return None
