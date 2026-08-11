"""
FORENZA Federated Node Protocol & Peer Discovery Engine.
Manages sovereign forensic node identities, mTLS certificate metadata,
heartbeat pulse monitoring, and peer discovery registries across national laboratories.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class NodeRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    NATIONAL_LAB = "national_lab"
    FIELD_STATION = "field_station"


class NodeStatus(str, Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    SYNCHRONIZING = "synchronizing"


@dataclass
class NodeIdentity:
    """Unique identity and mTLS credentials for a federated node."""
    node_id: str                          # e.g. 'jandarma-tr', 'bka-de', 'fbi-us'
    country_code: str                     # ISO 3166-1 alpha-2 (e.g. 'TR', 'DE', 'US')
    city: str
    organization: str                     # e.g. 'Turkish Gendarmerie Forensic Dept'
    role: NodeRole = NodeRole.NATIONAL_LAB
    endpoint_url: str = "http://localhost:8101"
    mtls_cert_fingerprint: str = ""       # SHA256 fingerprint of mTLS public cert
    profile_count: int = 0
    last_heartbeat_timestamp: float = field(default_factory=time.time)
    status: NodeStatus = NodeStatus.ONLINE


class PeerRegistry:
    """
    In-memory registry tracking active federated peer nodes and their heartbeat states.
    Thread-safe and deterministic.
    """

    HEARTBEAT_TIMEOUT_SECONDS: float = 30.0

    def __init__(self, local_node_id: str = "local_node"):
        self.local_node_id = local_node_id
        self._nodes: Dict[str, NodeIdentity] = {}

    def register_node(self, node: NodeIdentity) -> bool:
        """Registers a new peer node or updates existing node metadata."""
        is_new = node.node_id not in self._nodes
        node.last_heartbeat_timestamp = time.time()
        node.status = NodeStatus.ONLINE
        self._nodes[node.node_id] = node
        return is_new

    def update_heartbeat(self, node_id: str, profile_count: Optional[int] = None) -> bool:
        """Updates heartbeat timestamp and optionally profile count for node_id."""
        if node_id not in self._nodes:
            return False
        node = self._nodes[node_id]
        node.last_heartbeat_timestamp = time.time()
        node.status = NodeStatus.ONLINE
        if profile_count is not None:
            node.profile_count = profile_count
        return True

    def get_active_nodes(self) -> List[NodeIdentity]:
        """Returns all peer nodes whose heartbeats are within timeout threshold."""
        now = time.time()
        active = []
        for node_id, node in self._nodes.items():
            if now - node.last_heartbeat_timestamp > self.HEARTBEAT_TIMEOUT_SECONDS:
                node.status = NodeStatus.OFFLINE
            else:
                active.append(node)
        return active

    def get_node(self, node_id: str) -> Optional[NodeIdentity]:
        return self._nodes.get(node_id)

    def to_dict(self) -> Dict:
        now = time.time()
        return {
            "total_registered_nodes": len(self._nodes),
            "active_online_nodes": len(self.get_active_nodes()),
            "nodes": [
                {
                    "node_id": n.node_id,
                    "country_code": n.country_code,
                    "city": n.city,
                    "organization": n.organization,
                    "role": n.role.value,
                    "status": (NodeStatus.OFFLINE.value if now - n.last_heartbeat_timestamp > self.HEARTBEAT_TIMEOUT_SECONDS else n.status.value),
                    "profile_count": n.profile_count,
                    "endpoint_url": n.endpoint_url,
                    "seconds_since_last_heartbeat": round(now - n.last_heartbeat_timestamp, 2),
                }
                for n in self._nodes.values()
            ]
        }
