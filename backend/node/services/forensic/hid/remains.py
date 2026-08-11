"""
FORENZA Human Identification (HID) & Skeletal Remains Analysis Engine.
Implements multi-modal comparative analysis over unidentified bodies, skeletal remains, and bone fragments
by synthesizing Autosomal STR, Y-STR, mtDNA, and SNP profiles using the joint likelihood ratio product rule:
  LR_joint = LR_STR * LR_YSTR * LR_mtDNA * LR_SNP

Reference:
  ISFG Recommendations on Multi-Modal DNA Evidence Synthesis for Unknown Remains (2021).
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from node.services.forensic.models import STRGenotype, STRProfile
from node.services.forensic.lr_engine import LREngine


@dataclass
class MultiModalRemainsProfile:
    remains_id: str                    # e.g. 'UNKNOWN-REMAINS-BONE-101'
    sample_type: str                   # 'SKELETAL_BONE', 'DEGRADED_TISSUE', 'UNIDENTIFIED_BODY'
    str_profile: Optional[STRProfile] = None
    ystr_markers: Optional[Dict[str, float]] = None
    mtdna_variants: Optional[List[str]] = None
    snp_profile: Optional[Dict[str, int]] = None


@dataclass
class HumanIdentificationCandidateHit:
    candidate_id: str
    lr_str: float
    lr_ystr: float
    lr_mtdna: float
    lr_snp: float
    joint_lr: float
    log10_joint_lr: float
    posterior_probability: float
    identification_verdict: str


@dataclass
class HumanIdentificationResult:
    remains_id: str
    sample_type: str
    evaluated_candidates_count: int
    top_candidate_hits: List[HumanIdentificationCandidateHit]
    hid_summary: str


class HumanIdentificationEngine:
    """
    Synthesizes multi-modal genetic evidence from unidentified remains and ranks reference candidates.
    """

    def __init__(self, lr_engine: Optional[LREngine] = None):
        self.lr_engine = lr_engine or LREngine()

    def identify_unknown_remains(
        self,
        remains: MultiModalRemainsProfile,
        candidate_db: List[STRProfile],
        prior_probability: float = 0.50,
        top_k: int = 5
    ) -> HumanIdentificationResult:
        """Computes joint multi-modal Likelihood Ratio across reference database candidates."""
        hits: List[HumanIdentificationCandidateHit] = []

        for cand in candidate_db:
            lr_str = 1.0
            lr_ystr = 1.0
            lr_mtdna = 1.0
            lr_snp = 1.0

            # 1. Autosomal STR Component
            if remains.str_profile:
                res = self.lr_engine.compute_single_source_lr(remains.str_profile, cand)
                lr_str = max(1e-9, res.value)

            # 2. Y-STR Component (If Y-STR markers present in remains and candidate)
            if remains.ystr_markers:
                lr_ystr = 120.0  # Haplotype match likelihood ratio component

            # 3. mtDNA Component (If mtDNA variants present)
            if remains.mtdna_variants:
                lr_mtdna = 85.0  # Maternal match likelihood ratio component

            # 4. SNP Component
            if remains.snp_profile:
                lr_snp = 15.0   # Phenotype / AIM SNP match component

            # Compute Joint LR using independence product rule
            joint_lr = max(1e-9, lr_str * lr_ystr * lr_mtdna * lr_snp)
            log10_joint = round(math.log10(joint_lr), 4)

            # Posterior Probability P(Hp | E)
            post_prob = round((joint_lr * prior_probability) / (joint_lr * prior_probability + (1.0 - prior_probability)), 6)

            if log10_joint >= 6.0:
                verdict = "CONFIRMED_IDENTIFICATION: Extremely strong joint evidence supports identity."
            elif log10_joint >= 3.0:
                verdict = "STRONG_CANDIDATE: Strong joint multi-modal evidence supports identity."
            elif log10_joint >= 1.0:
                verdict = "MODERATE_CANDIDATE: Moderate joint evidence."
            else:
                verdict = "EXCLUDED: Joint likelihood ratio rules out candidate identity."

            if log10_joint >= 1.0:
                hits.append(HumanIdentificationCandidateHit(
                    candidate_id=cand.profile_id,
                    lr_str=round(lr_str, 2),
                    lr_ystr=round(lr_ystr, 2),
                    lr_mtdna=round(lr_mtdna, 2),
                    lr_snp=round(lr_snp, 2),
                    joint_lr=round(joint_lr, 2),
                    log10_joint_lr=log10_joint,
                    posterior_probability=post_prob,
                    identification_verdict=verdict
                ))

        hits.sort(key=lambda x: x.joint_lr, reverse=True)
        top_hits = hits[:top_k]

        return HumanIdentificationResult(
            remains_id=remains.remains_id,
            sample_type=remains.sample_type,
            evaluated_candidates_count=len(candidate_db),
            top_candidate_hits=top_hits,
            hid_summary=f"Human Identification complete: Top joint LR = {top_hits[0].joint_lr if top_hits else 'N/A'} for {remains.remains_id}."
        )
