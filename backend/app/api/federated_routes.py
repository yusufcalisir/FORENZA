"""
FORENZA Federated Node API Router.
Exposes endpoints for node registration, heartbeat, multi-node federated queries,
and network status monitoring under the /federated prefix.
"""

from fastapi import APIRouter, HTTPException, status

from node.federated.node_protocol import NodeIdentity, NodeRole, PeerRegistry
from node.federated.orchestrator import FederatedQueryOrchestrator
from node.services.forensic.models import STRGenotype, STRProfile
from .federated_schemas import (
    FederatedSearchRequest, FederatedSearchResponse,
    NetworkStatusResponse, NodeRegistrationRequest, NodeRegistrationResponse
)

router = APIRouter(prefix="/federated", tags=["Federated Multi-Node Network"])

# Global singleton in-memory registry for development node orchestrator
_registry = PeerRegistry(local_node_id="orchestrator_tr")
_orchestrator = FederatedQueryOrchestrator(registry=_registry)

# Seed default global nodes (5 simulated international nodes)
_registry.register_node(NodeIdentity(
    node_id="jandarma-tr", country_code="TR", city="Ankara",
    organization="Turkish Gendarmerie Forensic Dept", role=NodeRole.NATIONAL_LAB,
    endpoint_url="http://localhost:8101", profile_count=100
))
_registry.register_node(NodeIdentity(
    node_id="bka-de", country_code="DE", city="Wiesbaden",
    organization="Bundeskriminalamt Forensic DNA Unit", role=NodeRole.NATIONAL_LAB,
    endpoint_url="http://localhost:8102", profile_count=150
))
_registry.register_node(NodeIdentity(
    node_id="fbi-us", country_code="US", city="Quantico",
    organization="FBI Laboratory NDIS", role=NodeRole.NATIONAL_LAB,
    endpoint_url="http://localhost:8104", profile_count=200
))


@router.post(
    "/nodes/register",
    response_model=NodeRegistrationResponse,
    summary="Register Sovereign Node",
    description="Registers or updates a federated national laboratory peer node in the network.",
    status_code=status.HTTP_200_OK,
)
async def register_node(body: NodeRegistrationRequest) -> NodeRegistrationResponse:
    try:
        node = NodeIdentity(
            node_id=body.node_id,
            country_code=body.country_code,
            city=body.city,
            organization=body.organization,
            role=NodeRole(body.role),
            endpoint_url=body.endpoint_url,
            profile_count=body.profile_count,
            mtls_cert_fingerprint=body.mtls_cert_fingerprint or "",
        )
        is_new = _registry.register_node(node)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Node registration failed: {str(exc)}"
        )

    return NodeRegistrationResponse(
        registered=True,
        node_id=node.node_id,
        message="Node registered successfully" if is_new else "Node heartbeat/metadata updated",
        active_nodes_in_network=len(_registry.get_active_nodes())
    )


@router.get(
    "/nodes/status",
    response_model=NetworkStatusResponse,
    summary="Network Topology & Node Health",
    description="Returns lifecycle status, heartbeat timestamps, and profile counts for all registered nodes.",
    status_code=status.HTTP_200_OK,
)
async def get_network_status() -> NetworkStatusResponse:
    return NetworkStatusResponse(**_registry.to_dict())


@router.post(
    "/search",
    response_model=FederatedSearchResponse,
    summary="Cross-Node Federated STR Search",
    description=(
        "Dispatches an STR profile query across all active network nodes. "
        "Aggregates likelihood ratios and verifies ZKP proofs without centralizing raw DNA profiles."
    ),
    status_code=status.HTTP_200_OK,
)
async def execute_federated_search(body: FederatedSearchRequest) -> FederatedSearchResponse:
    try:
        # Convert ProfileInput schema to domain model
        loci = {}
        for l_in in body.query_profile.loci:
            lname = l_in.locus.upper()
            loci[lname] = STRGenotype(locus_name=lname, allele1=l_in.allele1, allele2=l_in.allele2)

        query_domain_profile = STRProfile(
            profile_id=body.query_profile.profile_id,
            loci=loci,
            population_group=body.query_profile.population_group
        )

        result = _orchestrator.execute_federated_search(
            query_profile=query_domain_profile,
            min_log10_lr_threshold=body.min_log10_lr_threshold,
            population=body.population
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Federated search failed: {str(exc)}"
        )

    return FederatedSearchResponse(
        query_id=result.query_id,
        target_profile_id=result.target_profile_id,
        total_nodes_queried=result.total_nodes_queried,
        responding_nodes_count=result.responding_nodes_count,
        matching_nodes_count=result.matching_nodes_count,
        top_lr_value=result.top_lr_value,
        top_log10_lr=result.top_log10_lr,
        top_matching_node_id=result.top_matching_node_id,
        node_responses=[r.__dict__ for r in result.node_responses],
        elapsed_seconds=result.elapsed_seconds
    )
