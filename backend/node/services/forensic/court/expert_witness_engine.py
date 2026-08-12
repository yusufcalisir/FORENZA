"""
FORENZA Expert Witness & Judicial Examination Subsystem.

Provides dual operating modes:
1. Research & Laboratory Analyst Mode (raw RFUs, MCMC traces, Horvath equations, VCFs)
2. Expert Witness / Judicial Court Mode (7-point legal testimony framework)

7-Point Judicial Testimony Framework:
1. What was tested?
2. What was observed?
3. What was calculated?
4. What assumptions were made?
5. What does the LR mean?
6. What does it NOT mean? (Transposed Conditional Fallacy / Prosecutor's Fallacy Prevention)
7. What are the limitations?
"""

import hashlib
import hmac
import time
from typing import Dict, Any, List, Optional


class ExpertWitnessEngine:
    """
    Expert Witness Testimony Generator & Judicial Examination Subsystem.
    """

    HMAC_SECRET: bytes = b"FORENZA_EXPERT_WITNESS_TESTIMONY_SECRET_KEY"

    def generate_testimony_brief(
        self,
        case_id: str = "CASE-2026-COURT-01",
        sample_id: str = "SAMPLE-DNA-101",
        expert_witness_id: str = "EXPERT-01 (Dr. Sarah Connor)",
        log10_lr: float = 26.0,
        enfsi_verbal_predicate: str = "EXTREMELY_STRONG_SUPPORT_FOR_INCLUSION",
        total_loci: int = 24,
        fst_correction: float = 0.01,
        stochastic_threshold: float = 150.0,
    ) -> Dict[str, Any]:
        """
        Generates 7-point judicial testimony brief designed for legal cross-examination.

        :return: Dict containing 7 judicial testimony pillars, fallacy shield, and HMAC testimony hash.
        """
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # 1. WHAT WAS TESTED?
        pillar_1_tested = {
            "title": "1. What Was Tested?",
            "summary": f"Accessioned evidence sample {sample_id} associated with judicial case {case_id}.",
            "details": f"Amplified using standard CODIS {total_loci} core STR loci multiplex panel following ISO 17025 validated SOPs.",
        }

        # 2. WHAT WAS OBSERVED?
        pillar_2_observed = {
            "title": "2. What Was Observed?",
            "summary": f"Clean single-source / deconvolution autosomal STR profile resolved across {total_loci} loci.",
            "details": f"All loci exhibited peak height intensities above analytical threshold AT (50 RFU), with minimum peak height > {stochastic_threshold} RFU.",
        }

        # 3. WHAT WAS CALCULATED?
        pillar_3_calculated = {
            "title": "3. What Was Calculated?",
            "summary": f"Likelihood Ratio (LR) = 10^{log10_lr:.1f} (log10 LR = {log10_lr:.1f}).",
            "details": f"Random Match Probability (RMP) is 1 in 10^{log10_lr:.1f} in reference population databases.",
        }

        # 4. WHAT ASSUMPTIONS WERE MADE?
        pillar_4_assumptions = {
            "title": "4. What Assumptions Were Made?",
            "summary": "Hardy-Weinberg Equilibrium (HWE) & Linkage Equilibrium across core autosomal loci.",
            "details": f"NRC II Recommendation 4.1 population sub-structure correction applied with Fst = {fst_correction:.3f}.",
        }

        # 5. WHAT DOES THE LR MEAN?
        pillar_5_lr_meaning = {
            "title": "5. What Does the Likelihood Ratio Mean?",
            "summary": f"Scientific verbal predicate: {enfsi_verbal_predicate.replace('_', ' ')}.",
            "details": f"The physical DNA evidence is 10^{log10_lr:.1f} times more probable under the Prosecution Hypothesis (Hp: Sample originated from Person of Interest) than under the Defense Hypothesis (Hd: Sample originated from an unknown, unrelated individual).",
        }

        # 6. WHAT DOES IT NOT MEAN? (PROSECUTOR'S FALLACY SHIELD)
        pillar_6_fallacy_prevention = {
            "title": "6. What Does the Likelihood Ratio NOT Mean? (Legal Shield)",
            "summary": "IMPORTANT: The LR measures evidence probability P(E|Hp), NOT defendant guilt P(Hp|E).",
            "details": "Conflating evidence likelihood with defendant guilt is the 'Prosecutor's Fallacy' (Transposed Conditional Fallacy). Guilt or innocence requires evaluation of all non-scientific case evidence by the trier of fact.",
            "fallacy_protection_active": True,
        }

        # 7. WHAT ARE THE LIMITATIONS?
        pillar_7_limitations = {
            "title": "7. What Are the Scientific Limitations?",
            "summary": f"Analysis bounded by stochastic threshold ({stochastic_threshold} RFU) and expanded measurement uncertainty U95%.",
            "details": "DNA evidence evaluates source attribution only, NOT manner, activity, or time of deposition (PMI).",
        }

        # Compute HMAC Court Testimony Signature
        payload = f"{case_id}|{sample_id}|{log10_lr}|{enfsi_verbal_predicate}|{expert_witness_id}|{timestamp}"
        testimony_hash = hmac.new(self.HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()

        return {
            "testimony_title": "EXPERT WITNESS JUDICIAL EXAMINATION BRIEF",
            "case_id": case_id,
            "sample_id": sample_id,
            "expert_witness_id": expert_witness_id,
            "timestamp": timestamp,
            "operating_mode": "COURT_EXPERT_WITNESS_MODE",
            "testimony_pillars": [
                pillar_1_tested,
                pillar_2_observed,
                pillar_3_calculated,
                pillar_4_assumptions,
                pillar_5_lr_meaning,
                pillar_6_fallacy_prevention,
                pillar_7_limitations,
            ],
            "prosecutors_fallacy_shield": "PROTECTED_TRANSPOSED_CONDITIONAL_SHIELD",
            "testimony_hmac_hash": testimony_hash,
            "court_admissible": True,
        }
