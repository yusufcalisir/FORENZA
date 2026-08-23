"""
Maximum Likelihood & Bayesian Admixture Deconvolution Engines.

Implements:
- "Hard" Categorical Likelihood Ratio & Bayes Factor Discrete Population Classifier
- "Soft" Continuous Composite Admixture Deconvolution (ADMIXTURE / SLSQP / Dirichlet Solver)
- Multiallelic Microhaplotype (MH) Mixture & Lineage Resolver
- ENFSI (2017) Evaluative Verbal Statement Generator
"""

import math
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from scipy.optimize import minimize

from backend.node.services.forensic.genomics.bga.schemas import (
    IngestedBGASample,
    ReferenceSystemEnum,
    ContinentalSuperPopEnum,
    AdmixtureProportionResult,
    GenotypeCall
)
from backend.node.services.forensic.genomics.bga.reference_matrices import BGAReferenceMatrices
from backend.node.services.forensic.genomics.bga.frequency_smoother import BGAFrequencySmoother
from backend.node.services.forensic.genomics.bga.pca_procrustes_engine import BGAPCAProcrustesEngine


class BGAAdmixtureEngine:
    """Performs dual-mode discrete and continuous biogeographical ancestry deconvolution."""

    @classmethod
    def _compute_locus_genotype_likelihood(
        cls,
        call: GenotypeCall,
        ref_freq: float,
        alt_freq: float
    ) -> float:
        """
        Calculates Hardy-Weinberg genotypic likelihood P(g | p_ref, p_alt).
        """
        if call.allele_1 in ("-", "0", ".", "N"):
            return 1.0  # Missing data contributes neutral likelihood

        p = ref_freq
        q = alt_freq

        if call.dosage_alt == 0.0:
            # Homozygous REF (p^2)
            return max(1e-8, p * p)
        elif call.dosage_alt == 2.0:
            # Homozygous ALT (q^2)
            return max(1e-8, q * q)
        else:
            # Heterozygous (2 * p * q)
            return max(1e-8, 2.0 * p * q)

    @classmethod
    def compute_hard_assignment(
        cls,
        sample: IngestedBGASample,
        ref_system: ReferenceSystemEnum = ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26
    ) -> Dict[str, Any]:
        """
        Calculates discrete multi-population likelihoods, log10 LRs, and Bayes factors.
        """
        pops = BGAReferenceMatrices.get_population_list(ref_system)
        log_likelihoods: Dict[str, float] = {p: 0.0 for p in pops}

        for locus_id, call in sample.genotypes.items():
            if call.allele_1 in ("-", "0", ".", "N"):
                continue

            pop_freqs = BGAReferenceMatrices.get_allele_frequencies(locus_id, ref_system)
            for p in pops:
                raw_ref, raw_alt = pop_freqs.get(p, (0.50, 0.50))
                s_ref, s_alt = BGAFrequencySmoother.smooth_biallelic_frequencies(raw_ref, raw_alt, sample_size_n=100)
                locus_p = cls._compute_locus_genotype_likelihood(call, s_ref, s_alt)
                log_likelihoods[p] += math.log(max(1e-12, locus_p))

        # Log-sum-exp normalization for posterior probabilities
        max_log_lik = max(log_likelihoods.values()) if log_likelihoods else 0.0
        exp_weights = {p: math.exp(ll - max_log_lik) for p, ll in log_likelihoods.items()}
        total_exp = sum(exp_weights.values()) or 1.0
        posteriors = {p: round(w / total_exp, 8) for p, w in exp_weights.items()}

        # Sort populations by likelihood
        sorted_pops = sorted(log_likelihoods.items(), key=lambda x: x[1], reverse=True)
        top_pop = sorted_pops[0][0] if sorted_pops else "EUR"
        second_pop = sorted_pops[1][0] if len(sorted_pops) > 1 else top_pop

        log_diff = log_likelihoods[top_pop] - log_likelihoods[second_pop]
        bayes_factor = math.exp(min(50.0, log_diff))

        return {
            "top_assigned_population": top_pop,
            "runner_up_population": second_pop,
            "bayes_factor": round(bayes_factor, 2),
            "log_likelihoods": log_likelihoods,
            "posterior_probabilities": posteriors
        }

    @classmethod
    def compute_soft_admixture(
        cls,
        sample: IngestedBGASample,
        ref_system: ReferenceSystemEnum = ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26
    ) -> Dict[str, float]:
        """
        Performs continuous Q-matrix optimization (STRUCTURE / ADMIXTURE formulation).
        For an admixed individual with ancestry fractions Q = (q_1, ..., q_K),
        the expected individual ALT allele frequency is:
            p_i = sum_{k=1}^K q_k * p_k
        And the genotypic likelihood for diploid dosage d in {0, 1, 2} is:
            P(d=0 | Q) = (1 - p_i)^2
            P(d=1 | Q) = 2 * p_i * (1 - p_i)
            P(d=2 | Q) = p_i^2
        """
        pops = BGAReferenceMatrices.get_population_list(ref_system)
        k_pops = len(pops)
        if k_pops == 0:
            return {}

        valid_calls = [
            (loc, call) for loc, call in sample.genotypes.items()
            if call.allele_1 not in ("-", "0", ".", "N")
        ]

        if not valid_calls:
            # Equal uniform split when no data is available
            return {p: round(1.0 / k_pops, 6) for p in pops}

        # Pre-fetch smoothed ALT allele frequencies across all loci: shape (N_loci, K_pops)
        alt_freq_matrix: List[List[float]] = []
        dosages: List[float] = []

        for locus_id, call in valid_calls:
            pop_freqs = BGAReferenceMatrices.get_allele_frequencies(locus_id, ref_system)
            row: List[float] = []
            for p in pops:
                raw_ref, raw_alt = pop_freqs.get(p, (0.50, 0.50))
                _, s_alt = BGAFrequencySmoother.smooth_biallelic_frequencies(raw_ref, raw_alt, sample_size_n=100)
                row.append(s_alt)
            alt_freq_matrix.append(row)
            dosages.append(call.dosage_alt)

        P_alt = np.array(alt_freq_matrix)  # shape (N_loci, K_pops)
        D_arr = np.array(dosages)          # shape (N_loci,)

        # Objective function: Negative Log-Likelihood of composite genotype
        def objective(q: np.ndarray) -> float:
            # Individual expected ALT allele frequency per locus: p_ind = P_alt @ q
            p_ind = np.dot(P_alt, q)
            p_ind = np.clip(p_ind, 1e-6, 1.0 - 1e-6)

            # Vectorized genotypic log-likelihood
            # d == 0: 2 * ln(1 - p_ind)
            # d == 2: 2 * ln(p_ind)
            # d == 1: ln(2) + ln(p_ind) + ln(1 - p_ind)
            ll = np.zeros_like(p_ind)
            mask_0 = (D_arr == 0.0)
            mask_2 = (D_arr == 2.0)
            mask_1 = (D_arr == 1.0)

            ll[mask_0] = 2.0 * np.log(1.0 - p_ind[mask_0])
            ll[mask_2] = 2.0 * np.log(p_ind[mask_2])
            ll[mask_1] = np.log(2.0) + np.log(p_ind[mask_1]) + np.log(1.0 - p_ind[mask_1])

            # Regularization penalty to prevent degenerate corner cases
            entropy_penalty = 0.001 * np.sum(q * np.log(np.clip(q, 1e-9, 1.0)))

            return -np.sum(ll) + entropy_penalty

        # Constraints: sum(q) = 1.0, 0.0 <= q_k <= 1.0
        q0 = np.full(k_pops, 1.0 / k_pops)
        bounds = [(0.0, 1.0) for _ in range(k_pops)]
        constraints = ({'type': 'eq', 'fun': lambda q: np.sum(q) - 1.0})

        res = minimize(
            objective,
            q0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'maxiter': 300}
        )

        q_opt = res.x if res.success else q0
        q_opt = np.maximum(0.0, q_opt)
        q_opt /= np.sum(q_opt)

        q_dict = {pops[i]: round(float(q_opt[i]), 6) for i in range(k_pops)}

        # Strict sum-to-one simplex preservation
        diff = 1.0 - sum(q_dict.values())
        top_k = max(q_dict, key=q_dict.get)
        q_dict[top_k] = round(q_dict[top_k] + diff, 6)

        return q_dict

    @classmethod
    def compute_microhaplotype_admixture(
        cls,
        sample: IngestedBGASample,
        ref_system: ReferenceSystemEnum = ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26
    ) -> Dict[str, float]:
        """
        Deconvolutes admixture specifically utilizing multiallelic microhaplotype loci.
        """
        pops = BGAReferenceMatrices.get_population_list(ref_system)
        k_pops = len(pops)

        mh_calls = [
            (loc, call) for loc, call in sample.genotypes.items()
            if loc.startswith("mh") and call.allele_1 not in ("-", "0", ".", "N")
        ]

        if not mh_calls:
            return cls.compute_soft_admixture(sample, ref_system)

        lik_matrix: List[List[float]] = []
        for mh_id, call in mh_calls:
            mh_freqs = BGAReferenceMatrices.get_microhaplotype_frequencies(mh_id, ref_system)
            row: List[float] = []
            for p in pops:
                pop_dist = mh_freqs.get(p, {})
                s_dist = BGAFrequencySmoother.smooth_multiallelic_frequencies(pop_dist, sample_size_n=100)

                f1 = s_dist.get(call.allele_1, 0.01)
                f2 = s_dist.get(call.allele_2, 0.01)

                prob = (f1 * f1) if call.allele_1 == call.allele_2 else (2.0 * f1 * f2)
                row.append(max(1e-6, prob))
            lik_matrix.append(row)

        L_arr = np.array(lik_matrix)
        def objective(q: np.ndarray) -> float:
            dot_products = np.dot(L_arr, q)
            dot_products = np.clip(dot_products, 1e-12, None)
            return -np.sum(np.log(dot_products))

        q0 = np.full(k_pops, 1.0 / k_pops)
        bounds = [(0.0, 1.0) for _ in range(k_pops)]
        constraints = ({'type': 'eq', 'fun': lambda q: np.sum(q) - 1.0})

        res = minimize(objective, q0, method='SLSQP', bounds=bounds, constraints=constraints)
        q_opt = res.x if res.success else q0
        q_opt = np.maximum(0.0, q_opt)
        q_opt /= np.sum(q_opt)

        return {pops[i]: round(float(q_opt[i]), 6) for i in range(k_pops)}

    @classmethod
    def generate_enfsi_verbal_statement(
        cls,
        top_pop: str,
        bayes_factor: float,
        runner_up_pop: str
    ) -> str:
        """
        Maps numeric Bayes Factor to standardized ENFSI (2017) 7-Tier verbal evaluative statement.
        """
        if bayes_factor >= 1_000_000:
            tier = "extremely strong support"
        elif bayes_factor >= 10_000:
            tier = "very strong support"
        elif bayes_factor >= 1_000:
            tier = "strong support"
        elif bayes_factor >= 100:
            tier = "moderately strong support"
        elif bayes_factor >= 10:
            tier = "moderate support"
        elif bayes_factor >= 2:
            tier = "limited / weak support"
        else:
            tier = "inconclusive / uninformative"

        return (
            f"The genomic AIM profile provides {tier} (Bayes Factor: {bayes_factor:,.1f}) "
            f"for ancestry originating from {top_pop} relative to {runner_up_pop}. "
            "INVESTIGATIVE INTELLIGENCE ONLY: Do not use as deterministic proof of demographic identity."
        )

    @classmethod
    def generate_full_ancestry_report(
        cls,
        sample: IngestedBGASample,
        ref_system: ReferenceSystemEnum = ReferenceSystemEnum.ONE_THOUSAND_GENOMES_26
    ) -> AdmixtureProportionResult:
        """
        Synthesizes complete forensic BGA assessment combining Q-matrix, PCA, and 3D GIS mapping.
        """
        hard_res = cls.compute_hard_assignment(sample, ref_system)
        soft_q = cls.compute_soft_admixture(sample, ref_system)

        # Compute information diversity metrics
        q_values = [v for v in soft_q.values() if v > 0.0]
        shannon_h = -sum(v * math.log(v) for v in q_values)
        simpson_d = 1.0 - sum(v ** 2 for v in soft_q.values())

        # Map to ContinentalSuperPopEnum dictionary
        superpop_dict: Dict[ContinentalSuperPopEnum, float] = {}
        for p_code, val in soft_q.items():
            try:
                enum_key = ContinentalSuperPopEnum(p_code)
                superpop_dict[enum_key] = val
            except ValueError:
                superpop_dict[ContinentalSuperPopEnum.OTH] = superpop_dict.get(ContinentalSuperPopEnum.OTH, 0.0) + val

        # PCA and GIS Projections
        pca_res = BGAPCAProcrustesEngine.compute_pca_projection(sample, ref_system)
        gis_res = BGAPCAProcrustesEngine.project_procrustes_wgs84(pca_res, ref_system)

        top_pop_code = hard_res["top_assigned_population"]
        runner_up_code = hard_res["runner_up_population"]
        bf = hard_res["bayes_factor"]

        enfsi_statement = cls.generate_enfsi_verbal_statement(top_pop_code, bf, runner_up_code)

        try:
            top_enum = ContinentalSuperPopEnum(top_pop_code)
        except ValueError:
            top_enum = ContinentalSuperPopEnum.OTH

        return AdmixtureProportionResult(
            sample_id=sample.sample_id,
            panel_type=sample.primary_panel,
            superpop_proportions=superpop_dict,
            top_assigned_population=top_enum,
            bayes_factor_vs_second=bf,
            shannon_entropy=round(shannon_h, 4),
            simpson_diversity=round(simpson_d, 4),
            pca_coordinates=[pca_res.pc1, pca_res.pc2, pca_res.pc3],
            wgs84_centroid_lat=gis_res.centroid_latitude,
            wgs84_centroid_lng=gis_res.centroid_longitude,
            spatial_covariance_semi_major_km=gis_res.semi_major_axis_km,
            spatial_covariance_semi_minor_km=gis_res.semi_minor_axis_km,
            spatial_ellipse_tilt_deg=gis_res.ellipse_tilt_degrees,
            enfsi_verbal_statement=enfsi_statement
        )
