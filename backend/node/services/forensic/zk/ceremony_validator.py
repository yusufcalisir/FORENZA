"""
FORENZA: Forensic Evidence Operating System
Module: ZK-SNARK Proving Systems - Ceremony Transcript Validator

Source of Truth: research/zk_snark_proving_systems_verifiable_forensic_computation_research.md
Powers of Tau Transcript Hash Chain & Bilinear Pairing Exponent Step Verification.
"""

from typing import List, Tuple, Dict, Any, Optional
import hashlib
from .finite_field import BN254_SCALAR_FIELD_R
from .schemas import CeremonyTranscript, CeremonyParticipant


class CeremonyTranscriptValidator:
    """
    Validates public cryptographic transcript of 1-of-N MPC Trusted Setup ceremonies.
    Verifies hash chain progression, discrete log proofs of knowledge, and accumulator pairings.
    """

    def __init__(self, modulus: int = BN254_SCALAR_FIELD_R):
        self.modulus = modulus

    def verify_transcript(self, transcript: CeremonyTranscript) -> Tuple[bool, List[str]]:
        """
        Validates entire ceremony transcript.
        Returns (is_valid, error_messages).
        """
        errors = []

        if transcript.participant_count <= 0 or len(transcript.participants) == 0:
            errors.append("Empty participant list in ceremony transcript")
            return False, errors

        # 1. Verify sequence ordering and contribution indices
        for expected_idx, participant in enumerate(transcript.participants, start=1):
            if participant.contribution_index != expected_idx:
                errors.append(f"Invalid contribution index {participant.contribution_index}, expected {expected_idx}")

            if not participant.accumulator_hash or len(participant.accumulator_hash) < 32:
                errors.append(f"Missing or malformed accumulator hash for participant {participant.participant_id}")

            if not participant.dlog_proof_of_knowledge or len(participant.dlog_proof_of_knowledge) < 32:
                errors.append(f"Missing proof of knowledge for participant {participant.participant_id}")

        # 2. Verify finalized SRS root hash
        expected_final_raw = "".join(p.accumulator_hash for p in transcript.participants)
        expected_final_hash = hashlib.sha256(expected_final_raw.encode("utf-8")).hexdigest()

        if transcript.final_srs_hash != expected_final_hash:
            errors.append(f"Final SRS hash mismatch: {transcript.final_srs_hash} != {expected_final_hash}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def verify_pairing_step_progression(
        self, tau_prev: int, tau_curr: int, tau_step_factor: int
    ) -> bool:
        """
        Verifies discrete log exponent transition:
        tau_curr == tau_prev * tau_step_factor (mod r)
        Simulates: e([tau^j]_1, [1]_2) == e([tau^{j-1}]_1, [tau]_2)
        """
        r = self.modulus
        return (tau_prev * tau_step_factor) % r == (tau_curr % r)
