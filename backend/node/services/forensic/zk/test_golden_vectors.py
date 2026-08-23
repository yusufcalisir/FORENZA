"""
Unit tests for Certified Multi-Omic Golden Reference Standards in Zero-Knowledge Verifiable Proving.
"""

import pytest
from backend.node.services.forensic.zk.golden_vectors import (
    ALL_ZK_GOLDEN_VECTORS,
    VECTOR_ZK_CODIS_MATCH_INSTANCE,
    VECTOR_ZK_CODIS_MATCH_WITNESS,
    VECTOR_ZK_EXCLUSION_INSTANCE,
    VECTOR_ZK_EXCLUSION_WITNESS,
    VECTOR_ZK_MIXTURE_2P_INSTANCE,
    VECTOR_ZK_MIXTURE_2P_WITNESS,
    VECTOR_ZK_TRACE_LOW_TEMPLATE_INSTANCE,
    VECTOR_ZK_TRACE_LOW_TEMPLATE_WITNESS,
    VECTOR_ZK_INTERPOL_CROSS_BORDER_INSTANCE,
    VECTOR_ZK_INTERPOL_CROSS_BORDER_WITNESS,
)
from backend.node.services.forensic.zk.engines.groth16_engine import Groth16Engine
from backend.node.services.forensic.zk.engines.plonk_engine import PlonkEngine
from backend.node.services.forensic.zk.governance_engine import ZKForensicGovernanceEngine


def test_vector_zk_codis_match_groth16():
    engine = Groth16Engine()
    proof, _ = engine.synthesize_proof(VECTOR_ZK_CODIS_MATCH_INSTANCE, VECTOR_ZK_CODIS_MATCH_WITNESS)
    res = engine.verify_proof(VECTOR_ZK_CODIS_MATCH_INSTANCE, proof)

    assert res.is_valid is True
    assert res.pairing_residual_verified is True
    assert "Tier 6" in res.enfsi_tier


def test_vector_zk_exclusion_groth16():
    engine = Groth16Engine()
    proof, _ = engine.synthesize_proof(VECTOR_ZK_EXCLUSION_INSTANCE, VECTOR_ZK_EXCLUSION_WITNESS)
    res = engine.verify_proof(VECTOR_ZK_EXCLUSION_INSTANCE, proof)

    # Verification passes proving that true LR evaluated is consistent
    assert res.is_valid is True
    # Governance tier check on exclusion
    tier_num, tier_en, tier_tr = ZKForensicGovernanceEngine.get_enfsi_tier(VECTOR_ZK_EXCLUSION_WITNESS.true_likelihood_ratio)
    assert tier_num == 0
    assert "Exclusion" in tier_en or "Tier 0" in tier_en


def test_vector_zk_mixture_2p_plonk():
    engine = PlonkEngine()
    proof, _ = engine.synthesize_proof(VECTOR_ZK_MIXTURE_2P_INSTANCE, VECTOR_ZK_MIXTURE_2P_WITNESS)
    res = engine.verify_proof(VECTOR_ZK_MIXTURE_2P_INSTANCE, proof)

    assert res.is_valid is True
    assert res.pairing_residual_verified is True


def test_vector_zk_trace_low_template_groth16():
    engine = Groth16Engine()
    proof, _ = engine.synthesize_proof(VECTOR_ZK_TRACE_LOW_TEMPLATE_INSTANCE, VECTOR_ZK_TRACE_LOW_TEMPLATE_WITNESS)
    res = engine.verify_proof(VECTOR_ZK_TRACE_LOW_TEMPLATE_INSTANCE, proof)

    assert res.is_valid is True


def test_vector_zk_interpol_cross_border_groth16():
    engine = Groth16Engine()
    proof, _ = engine.synthesize_proof(VECTOR_ZK_INTERPOL_CROSS_BORDER_INSTANCE, VECTOR_ZK_INTERPOL_CROSS_BORDER_WITNESS)
    res = engine.verify_proof(VECTOR_ZK_INTERPOL_CROSS_BORDER_INSTANCE, proof)

    assert res.is_valid is True
    assert "Tier 6" in res.enfsi_tier
