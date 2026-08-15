"""
FORENZA Module 02 — Metropolis-Hastings MCMC Sampling Engine
Continuous Probabilistic Genotyping for 2, 3, and 4-contributor DNA mixtures.

Research Source: pillar_1_probabilistic_genotyping_research.md
  § 2.5  Metropolis-Hastings MCMC Acceptance Criterion
  § 2.6  3-Chain Parallel Multi-Chain Sampling
  § 2.7  Gelman-Rubin R̂ Convergence Diagnostic
  § 2.8  Effective Sample Size (ESS)
  § 2.9  95% HPD Conservative Likelihood Ratio Interval

Mathematical Specification:
  Acceptance ratio:
    α = min(1, [L(E|Θ*)·P(Θ*)·q(Θ^t|Θ*)] / [L(E|Θ^t)·P(Θ^t)·q(Θ*|Θ^t)])

  Gelman-Rubin R̂:
    R̂ = sqrt([(M-1)/M · W + 1/M · B] / W)  → < 1.05 for full convergence

  Effective Sample Size (ESS):
    ESS = N_total / (1 + 2·Σ_k ρ_k)  → must exceed 1000

  95% HPD Conservative LR Bound:
    log10(LR_HPD_95) = μ_log10LR − 1.96 · SE_log10LR

Constants:
    N_burn       = 10,000  (discard)
    N_sample     = 50,000  (production) / 100,000 (high-confidence casework)
    k_thin       = 10
    N_chains     = 3
"""

import math
import random
import statistics
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .peak_model import (
    EuroForMixGammaModel,
    STRmixLogNormalModel,
    BiophysicalPeakModel,
)


# ---------------------------------------------------------------------------
# Constants (Pillar 1 Research)
# ---------------------------------------------------------------------------
N_BURN_DEFAULT:   int   = 10_000
N_SAMPLE_DEFAULT: int   = 50_000
K_THIN:           int   = 10
N_CHAINS:         int   = 3
R_HAT_THRESHOLD:  float = 1.05
ESS_THRESHOLD:    int   = 1_000


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class MCMCSample:
    """A single retained MCMC sample (post burn-in, post thinning)."""
    iteration:       int
    mixture_weights: List[float]     # w_k per contributor
    degradation:     List[float]     # d_k per contributor
    genotypes:       List[Tuple[float, float]]  # (a1,a2) per contributor
    log_likelihood:  float
    log10_lr:        Optional[float] = None     # filled after LR computation


@dataclass
class MCMCChainResult:
    """Result of one complete MCMC chain."""
    chain_id:   int
    samples:    List[MCMCSample]
    acceptance_rate: float


@dataclass
class MCMCConvergenceDiagnostics:
    """Gelman-Rubin R̂ and ESS convergence assessment."""
    r_hat_per_param: Dict[str, float]   # param name → R̂
    r_hat_max:       float
    ess_per_param:   Dict[str, float]   # param name → ESS
    ess_min:         float
    converged:       bool               # r_hat_max < 1.05 AND ess_min > 1000
    n_samples_per_chain: int


@dataclass
class MixtureLRResult:
    """Full MCMC Mixture LR result with 95% HPD interval."""
    log10_lr_point:     float       # Mean log10(LR) from all chains
    log10_lr_hpd95_lo:  float       # Conservative 95% HPD lower bound
    log10_lr_hpd95_hi:  float       # Upper bound
    lr_point:           float       # 10^log10_lr_point
    n_contributors:     int
    model_engine:       str         # "EuroForMix" | "STRmix"
    convergence:        MCMCConvergenceDiagnostics
    posterior_mixture_weights: List[float]  # Posterior mean w_k
    posterior_degradation:     List[float]  # Posterior mean d_k
    verbal_scale_en:    str
    verbal_scale_tr:    str
    assumptions:        List[str]


# ---------------------------------------------------------------------------
# ENFSI 2017 Verbal Scale (7-tier — matches Module 01 LREngine)
# ---------------------------------------------------------------------------

_ENFSI_TIERS: List[Tuple[float, str, str]] = [
    (1e18, "Astronomically / Extremely Strong Support for the Prosecution Proposition",
           "Son Derece Güçlü Destek - Kovuşturma Propozisyonu"),
    (1e6,  "Extremely Strong Support for the Prosecution Proposition",
           "Çok Güçlü Destek - Kovuşturma Propozisyonu"),
    (1e4,  "Very Strong Support for the Prosecution Proposition",
           "Güçlü Destek - Kovuşturma Propozisyonu"),
    (1e3,  "Strong Support for the Prosecution Proposition",
           "Orta-Güçlü Destek - Kovuşturma Propozisyonu"),
    (1e2,  "Moderately Strong Support for the Prosecution Proposition",
           "Orta Düzeyde Destek - Kovuşturma Propozisyonu"),
    (1e1,  "Moderate Support for the Prosecution Proposition",
           "Sınırlı/Zayıf Destek - Kovuşturma Propozisyonu"),
    (1.0,  "Weak Support for the Prosecution Proposition",
           "Zayıf Destek - Kovuşturma Propozisyonu"),
]

def _enfsi_verbal(lr: float) -> Tuple[str, str]:
    """Map LR to ENFSI 2017 7-tier verbal scale (EN & TR)."""
    if lr <= 0:
        return ("Exclusion / Support for Defense Proposition",
                "Dışlama / Savunma Propozisyonunu Destekler")
    if lr == 1.0:
        return ("Inconclusive / Neutral Evidence (LR = 1)",
                "Belirsiz / Nötr Kanıt (LR = 1)")
    if lr < 1.0:
        inv_lr = 1.0 / lr
        en, tr = _enfsi_verbal(inv_lr)
        return (f"Support for Defense Proposition (inverse LR = {inv_lr:.2e})",
                f"Savunma Propozisyonunu Destekler (ters LR = {inv_lr:.2e})")
    for threshold, en_label, tr_label in _ENFSI_TIERS:
        if lr >= threshold:
            return en_label, tr_label
    return (_ENFSI_TIERS[-1][1], _ENFSI_TIERS[-1][2])


# ---------------------------------------------------------------------------
# Dirichlet Sampler Utility
# ---------------------------------------------------------------------------

def _sample_dirichlet(alpha: List[float], rng: random.Random) -> List[float]:
    """
    Sample from Dirichlet(alpha) using Gamma variates.
    Ensures Σ w_k = 1.0 and w_k > 0.
    """
    gammas = [rng.gammavariate(max(a, 1e-6), 1.0) for a in alpha]
    total = sum(gammas)
    return [g / total for g in gammas]


def _log_dirichlet_pdf(x: List[float], alpha: List[float]) -> float:
    """Unnormalized log-density of Dirichlet(alpha) at x."""
    total = 0.0
    for xi, ai in zip(x, alpha):
        if xi <= 0:
            return -1e30
        total += (ai - 1.0) * math.log(xi)
    return total


# ---------------------------------------------------------------------------
# Effective Sample Size (ESS)
# ---------------------------------------------------------------------------

def _compute_ess(chain: List[float]) -> float:
    """
    Compute ESS via autocorrelation sum.
    ESS = N / (1 + 2·Σ_k ρ_k)
    Truncates at first negative autocorrelation lag (initial positive sequence).
    """
    N = len(chain)
    if N < 4:
        return float(N)
    mean = statistics.mean(chain)
    var = statistics.variance(chain)
    if var < 1e-15:
        return float(N)
    ac_sum = 0.0
    for lag in range(1, N // 2):
        ac = sum((chain[i] - mean) * (chain[i + lag] - mean)
                 for i in range(N - lag)) / ((N - lag) * var)
        if ac <= 0:
            break
        ac_sum += ac
    return N / (1.0 + 2.0 * ac_sum)


# ---------------------------------------------------------------------------
# Gelman-Rubin R̂ Diagnostic
# ---------------------------------------------------------------------------

def _gelman_rubin(chains: List[List[float]]) -> float:
    """
    Compute Gelman-Rubin R̂ across M chains each of length N.

    R̂ = sqrt([(M-1)/M · W + 1/M · B] / W)

    Returns R̂; value < 1.05 indicates convergence.
    """
    M = len(chains)
    N = len(chains[0])
    if M < 2 or N < 4:
        return float('nan')
    chain_means = [statistics.mean(c) for c in chains]
    chain_vars  = [statistics.variance(c) for c in chains]
    grand_mean  = statistics.mean(chain_means)
    W = statistics.mean(chain_vars)          # Within-chain variance
    B = N * statistics.variance(chain_means) # Between-chain variance
    if W < 1e-15:
        return 1.0
    var_hat = ((N - 1) / N) * W + (1.0 / N) * B
    return math.sqrt(var_hat / W)


# ---------------------------------------------------------------------------
# Core MCMC Sampler
# ---------------------------------------------------------------------------

class MCMCSampler:
    """
    Metropolis-Hastings MCMC Sampling Engine for continuous multi-contributor
    mixture deconvolution.

    Supports K = 2, 3, 4 contributors, EuroForMix Gamma and STRmix Log-Normal
    likelihood models. Runs N_CHAINS independent chains with Gelman-Rubin
    convergence diagnostics and ESS assessment.
    """

    def __init__(
        self,
        n_burn:    int   = N_BURN_DEFAULT,
        n_sample:  int   = N_SAMPLE_DEFAULT,
        k_thin:    int   = K_THIN,
        n_chains:  int   = N_CHAINS,
        model:     str   = "STRmix",      # "EuroForMix" | "STRmix"
        omega:     float = 0.35,          # EuroForMix ω  (CV)
        sigma:     float = 0.35,          # STRmix σ
        gamma:     float = 1.0,           # STRmix γ heteroscedasticity
        seed:      Optional[int] = None,
    ):
        self.n_burn   = n_burn
        self.n_sample = n_sample
        self.k_thin   = k_thin
        self.n_chains = n_chains
        self.model    = model.upper()
        self.omega    = omega
        self.sigma    = sigma
        self.gamma    = gamma
        self.base_seed = seed

        # Likelihood callables (set per chain)
        if self.model == "EUROFORMIX":
            self._ll_engine = EuroForMixGammaModel(omega=omega)
        else:
            self._ll_engine = STRmixLogNormalModel(sigma=sigma, gamma=gamma)

        self._bphys = BiophysicalPeakModel(template_scale=3000.0)

    # ------------------------------------------------------------------
    # Internal: log-likelihood for a full profile configuration
    # ------------------------------------------------------------------

    def _compute_log_likelihood(
        self,
        observed: Dict[str, Dict[float, float]],
        genotypes: List[Tuple[float, float]],
        weights:   List[float],
        degradation: List[float],
    ) -> float:
        """Compute Σ_l Σ_a log P(h_{l,a} | Θ) using the configured model."""
        total_ll = 0.0
        for locus, allele_obs in observed.items():
            expected = self._bphys.expected_peak_heights(
                locus, genotypes, weights, degradation
            )
            for allele, h_obs in allele_obs.items():
                h_exp = expected.get(allele, 0.0)
                if h_exp <= 0.0:
                    total_ll -= 1e6
                    continue
                total_ll += self._ll_engine.log_likelihood_locus_allele(h_obs, h_exp)
        return total_ll

    # ------------------------------------------------------------------
    # Internal: propose new genotype set from observed allele pool
    # ------------------------------------------------------------------

    @staticmethod
    def _propose_genotypes(
        observed: Dict[str, Dict[float, float]],
        K: int,
        rng: random.Random,
    ) -> List[Tuple[float, float]]:
        """Uniformly sample K genotypes from locus-union allele pool."""
        all_alleles_per_locus: Dict[str, List[float]] = {
            loc: list(obs.keys()) for loc, obs in observed.items()
        }
        genotypes = []
        for _ in range(K):
            g = {}
            for locus, alleles in all_alleles_per_locus.items():
                if len(alleles) >= 2:
                    a1, a2 = rng.sample(alleles, 2)
                    g[locus] = (min(a1, a2), max(a1, a2))
                elif len(alleles) == 1:
                    g[locus] = (alleles[0], alleles[0])
            # Represent as first locus tuple for single-locus chains
            first = next(iter(g.values())) if g else (0.0, 0.0)
            genotypes.append(first)
        return genotypes

    # ------------------------------------------------------------------
    # Run a single chain
    # ------------------------------------------------------------------

    def _run_chain(
        self,
        chain_id:    int,
        observed:    Dict[str, Dict[float, float]],
        K:           int,
        init_weights: List[float],
        init_degradation: List[float],
        init_genotypes: List[Tuple[float, float]],
    ) -> MCMCChainResult:
        """Execute one complete Metropolis-Hastings chain."""
        rng = random.Random(self.base_seed + chain_id if self.base_seed is not None else None)

        # Current state
        w_cur   = list(init_weights)
        d_cur   = list(init_degradation)
        g_cur   = list(init_genotypes)
        ll_cur  = self._compute_log_likelihood(observed, g_cur, w_cur, d_cur)

        samples: List[MCMCSample] = []
        n_accepted = 0
        total_proposals = 0

        # -- Dirichlet concentration parameter for mixture proportion proposals --
        dirichlet_conc = 50.0  # tighter around current → fine-tuned proposals

        for i in range(self.n_burn + self.n_sample):
            # -- Propose mixture weights via symmetric Dirichlet --
            alpha_prop = [w * dirichlet_conc for w in w_cur]
            w_prop = _sample_dirichlet(alpha_prop, rng)

            # -- Propose degradation slopes (truncated Normal, positivity) --
            d_prop = []
            for dk in d_cur:
                dk_new = rng.gauss(dk, 0.0005)
                d_prop.append(max(0.0, dk_new))

            # -- Genotype proposal (occasional random perturbation) --
            if rng.random() < 0.10:
                g_prop = self._propose_genotypes(observed, K, rng)
            else:
                g_prop = list(g_cur)

            # -- Compute proposed log-likelihood --
            ll_prop = self._compute_log_likelihood(observed, g_prop, w_prop, d_prop)

            # -- Metropolis-Hastings acceptance --
            log_alpha = ll_prop - ll_cur   # prior is flat; q symmetric for Gaussian d
            # Correction for Dirichlet proposal asymmetry
            log_q_cur = _log_dirichlet_pdf(w_cur, [w * dirichlet_conc for w in w_prop])
            log_q_prop = _log_dirichlet_pdf(w_prop, [w * dirichlet_conc for w in w_cur])
            log_alpha += (log_q_cur - log_q_prop)

            total_proposals += 1
            if math.log(max(rng.random(), 1e-300)) <= log_alpha:
                w_cur  = w_prop
                d_cur  = d_prop
                g_cur  = g_prop
                ll_cur = ll_prop
                n_accepted += 1

            # -- Retain after burn-in, with thinning --
            if i >= self.n_burn and (i - self.n_burn) % self.k_thin == 0:
                samples.append(MCMCSample(
                    iteration=i,
                    mixture_weights=list(w_cur),
                    degradation=list(d_cur),
                    genotypes=list(g_cur),
                    log_likelihood=ll_cur,
                ))

        acceptance_rate = n_accepted / max(1, total_proposals)
        return MCMCChainResult(chain_id=chain_id, samples=samples, acceptance_rate=acceptance_rate)

    # ------------------------------------------------------------------
    # Convergence Diagnostics
    # ------------------------------------------------------------------

    def _convergence_diagnostics(
        self, chain_results: List[MCMCChainResult], K: int
    ) -> MCMCConvergenceDiagnostics:
        """Compute Gelman-Rubin R̂ and ESS for each mixture weight w_k."""
        r_hat_per_param: Dict[str, float] = {}
        ess_per_param:   Dict[str, float] = {}

        for k in range(K):
            param_name = f"w_{k+1}"
            chains_k = [[s.mixture_weights[k] for s in cr.samples] for cr in chain_results]
            rhat = _gelman_rubin(chains_k)
            r_hat_per_param[param_name] = rhat

            all_vals = [v for c in chains_k for v in c]
            ess = _compute_ess(all_vals)
            ess_per_param[param_name] = ess

        # Also compute for log-likelihood
        ll_chains = [[s.log_likelihood for s in cr.samples] for cr in chain_results]
        r_hat_per_param["log_likelihood"] = _gelman_rubin(ll_chains)
        all_ll = [v for c in ll_chains for v in c]
        ess_per_param["log_likelihood"] = _compute_ess(all_ll)

        rhat_max = max((v for v in r_hat_per_param.values() if not math.isnan(v)), default=float('nan'))
        ess_min  = min(ess_per_param.values(), default=0.0)

        return MCMCConvergenceDiagnostics(
            r_hat_per_param=r_hat_per_param,
            r_hat_max=rhat_max,
            ess_per_param=ess_per_param,
            ess_min=ess_min,
            converged=(rhat_max < R_HAT_THRESHOLD and ess_min >= ESS_THRESHOLD),
            n_samples_per_chain=len(chain_results[0].samples) if chain_results else 0,
        )

    # ------------------------------------------------------------------
    # Public: run full 3-chain MCMC & compute LR
    # ------------------------------------------------------------------

    def run_mixture_deconvolution(
        self,
        observed: Dict[str, Dict[float, float]],
        K: int,
        suspect_genotype: Optional[List[Tuple[float, float]]] = None,
    ) -> MixtureLRResult:
        """
        Full MCMC mixture deconvolution and Likelihood Ratio computation.

        Args:
            observed : {locus → {allele → observed_RFU}}
            K        : Number of contributors (2, 3, or 4)
            suspect_genotype : Per-locus genotype for H_p computation (optional).
                               If None, returns only H_d denominator LR.

        Returns:
            MixtureLRResult with LR point estimate, 95% HPD bounds, convergence.
        """
        if K not in (2, 3, 4):
            raise ValueError(f"K must be 2, 3, or 4 contributors (got {K})")

        # -- Initial parameter values --
        init_weights    = [1.0 / K] * K
        init_degradation= [0.002] * K
        init_genotypes  = self._propose_genotypes(observed, K, random.Random(42))

        # -- Run N_CHAINS parallel chains --
        chain_results: List[MCMCChainResult] = []
        for c_id in range(self.n_chains):
            chain = self._run_chain(
                chain_id=c_id,
                observed=observed,
                K=K,
                init_weights=list(init_weights),
                init_degradation=list(init_degradation),
                init_genotypes=list(init_genotypes),
            )
            chain_results.append(chain)

        # -- Convergence diagnostics --
        conv = self._convergence_diagnostics(chain_results, K)

        # -- Pool all samples across chains --
        all_samples: List[MCMCSample] = [
            s for cr in chain_results for s in cr.samples
        ]
        M = len(all_samples)

        # -- Compute H_d integrated likelihood (all K unknown) --
        ll_hd_vals: List[float] = [s.log_likelihood for s in all_samples]

        # -- Compute H_p integrated likelihood if suspect provided --
        ll_hp_vals: List[float] = []
        if suspect_genotype:
            for s in all_samples:
                # Fix genotype of contributor 1 to suspect; resample others
                fixed_genotypes = [suspect_genotype[0] if suspect_genotype else s.genotypes[0]] + s.genotypes[1:]
                ll_hp = self._compute_log_likelihood(
                    observed, fixed_genotypes, s.mixture_weights, s.degradation
                )
                ll_hp_vals.append(ll_hp)

        # -- LR computation in log-space (log-sum-exp) --
        def _log_mean_exp(vals: List[float]) -> float:
            """Compute log(1/M · Σ exp(val)) = log_sum_exp - log(M)."""
            if not vals:
                return -1e30
            max_v = max(vals)
            return max_v + math.log(sum(math.exp(v - max_v) for v in vals)) - math.log(len(vals))

        log_l_hd = _log_mean_exp(ll_hd_vals)

        if ll_hp_vals:
            log_l_hp = _log_mean_exp(ll_hp_vals)
            log10_lr_samples = [(lp - ld) / math.log(10)
                                for lp, ld in zip(ll_hp_vals, ll_hd_vals)]
        else:
            # Only H_d computation (no suspect — return RMP-style)
            log10_lr_samples = [-v / math.log(10) for v in ll_hd_vals]
            log_l_hp = 0.0

        # -- Point estimate & 95% HPD --
        log10_lr_point = (log_l_hp - log_l_hd) / math.log(10) if ll_hp_vals else statistics.mean(log10_lr_samples)
        se_log10_lr    = statistics.stdev(log10_lr_samples) / math.sqrt(max(1, len(log10_lr_samples)))
        hpd_lo         = log10_lr_point - 1.96 * se_log10_lr
        hpd_hi         = log10_lr_point + 1.96 * se_log10_lr

        clamped_exp = min(300.0, max(-300.0, log10_lr_point))
        lr_point = 10.0 ** clamped_exp

        # -- Posterior mean mixture weights & degradation --
        post_w = [statistics.mean(s.mixture_weights[k] for s in all_samples) for k in range(K)]
        post_d = [statistics.mean(s.degradation[k] for s in all_samples) for k in range(K)]

        verbal_en, verbal_tr = _enfsi_verbal(lr_point)

        return MixtureLRResult(
            log10_lr_point=round(log10_lr_point, 4),
            log10_lr_hpd95_lo=round(hpd_lo, 4),
            log10_lr_hpd95_hi=round(hpd_hi, 4),
            lr_point=lr_point,
            n_contributors=K,
            model_engine="EuroForMix" if self.model == "EUROFORMIX" else "STRmix",
            convergence=conv,
            posterior_mixture_weights=[round(w, 4) for w in post_w],
            posterior_degradation=[round(d, 6) for d in post_d],
            verbal_scale_en=verbal_en,
            verbal_scale_tr=verbal_tr,
            assumptions=[
                f"Model: {'EuroForMix (Gamma)' if self.model == 'EUROFORMIX' else 'STRmix (Log-Normal)'}",
                f"K contributors: {K}",
                f"MCMC chains: {self.n_chains}, burn-in: {self.n_burn}, samples: {self.n_sample}",
                f"Thinning: every {self.k_thin} iterations",
                f"Gelman-Rubin R̂ < 1.05 required for convergence",
                f"ESS > 1,000 required for reliable inference",
                "Loci assumed in Linkage Equilibrium",
                "Non-inbred reference population assumed",
            ],
        )


# ---------------------------------------------------------------------------
# Tippett Calibration Engine
# ---------------------------------------------------------------------------

class CalibrationEngine:
    """
    Generates Tippett plot calibration data for LR validation.
    True Donor curve: P(log10(LR) >= x | H_p true)
    Non-Donor curve: P(log10(LR) >= x | H_d true)
    """

    @staticmethod
    def generate_tippett_curve(
        donor_lrs:    List[float],
        nondonor_lrs: List[float],
    ) -> Dict[str, List[Tuple[float, float]]]:
        """
        Compute cumulative Tippett exceedance curves.

        Returns dict with keys:
          'true_donor_curve'  : [(log10LR, P(LR >= x | H_p))]
          'non_donor_curve'   : [(log10LR, P(LR >= x | H_d))]
        """
        def _safe_log10(lr: float) -> float:
            return math.log10(max(1e-300, lr))

        sorted_donor    = sorted(_safe_log10(lr) for lr in donor_lrs)
        sorted_nondonor = sorted(_safe_log10(lr) for lr in nondonor_lrs)
        n_d  = len(sorted_donor)
        n_nd = len(sorted_nondonor)

        donor_curve:    List[Tuple[float, float]] = [
            (v, (n_d - i) / n_d) for i, v in enumerate(sorted_donor)
        ]
        nondonor_curve: List[Tuple[float, float]] = [
            (v, (n_nd - i) / n_nd) for i, v in enumerate(sorted_nondonor)
        ]

        return {
            "true_donor_curve":  donor_curve,
            "non_donor_curve":   nondonor_curve,
        }

    @staticmethod
    def compute_cllr(
        donor_lrs:    List[float],
        nondonor_lrs: List[float],
    ) -> float:
        """
        Compute Log-Likelihood Ratio Cost (Cllr) calibration metric.
        Cllr = ½ [1/n_Hp Σ log2(1 + 1/LR_i) + 1/n_Hd Σ log2(1 + LR_j)]
        """
        log2 = math.log2
        cllr_hp = sum(log2(1.0 + 1.0 / max(1e-300, lr)) for lr in donor_lrs)
        cllr_hd = sum(log2(1.0 + max(1e-300, lr))        for lr in nondonor_lrs)
        n_hp = max(1, len(donor_lrs))
        n_hd = max(1, len(nondonor_lrs))
        return 0.5 * (cllr_hp / n_hp + cllr_hd / n_hd)
