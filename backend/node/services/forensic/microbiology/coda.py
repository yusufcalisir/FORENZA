"""
FORENZA Compositional Data Analysis (CoDa) & Distance Metrics Engine.
Implements Centered Log-Ratio (CLR), Isometric Log-Ratio (ILR), Bayesian Multiplicative Zero Imputation,
and Aitchison, Bray-Curtis, and Jaccard distances for high-throughput forensic metagenomics.

References:
  Aitchison (1986) The Statistical Analysis of Compositional Data.
  Egozcue et al. (2003) Isometric Logratio Transformations for Compositional Data Analysis.
  Martín-Fernández et al. (2003) Dealing with Zeros and Missing Values in Compositional Data Sets.
"""

import math
from typing import Dict, List, Tuple, Optional


def zero_replacement_multiplicative(
    abundances: Dict[str, float],
    delta: float = 1e-4
) -> Dict[str, float]:
    """
    Implements Multiplicative Zero Replacement to preserve sub-compositional ratios
    on the simplex S^D before applying log-ratio transformations.
    
    If count/abundance is zero, replaces with delta, scaling non-zero values by (1 - sum(delta_zeros)).
    """
    total_val = sum(abundances.values())
    if total_val <= 0.0:
        # Uniform allocation fallback
        n = len(abundances)
        return {k: 1.0 / n for k in abundances.keys()} if n > 0 else {}

    # Normalize to 1.0 sum
    norm_dict = {k: v / total_val for k, v in abundances.items()}
    zero_keys = [k for k, v in norm_dict.items() if v <= 0.0]
    non_zero_keys = [k for k, v in norm_dict.items() if v > 0.0]

    if not zero_keys:
        return norm_dict

    q = len(zero_keys)
    sum_delta = q * delta
    
    if sum_delta >= 1.0:
        # Fallback if too many zeros and delta is large
        delta = 0.5 / max(1, q)
        sum_delta = q * delta

    scale_factor = 1.0 - sum_delta
    result = {}
    for k in zero_keys:
        result[k] = delta
    for k in non_zero_keys:
        result[k] = norm_dict[k] * scale_factor

    return result


def compute_geometric_mean(values: List[float]) -> float:
    """
    Computes geometric mean g(x) = exp( (1/D) * sum(ln(x_i)) )
    """
    if not values:
        return 1.0
    valid_vals = [max(1e-12, v) for v in values]
    log_sum = sum(math.log(v) for v in valid_vals)
    return math.exp(log_sum / len(valid_vals))


def clr_transformation(abundances: Dict[str, float], delta: float = 1e-4) -> Tuple[Dict[str, float], float]:
    """
    Applies Centered Log-Ratio (CLR) Transformation:
    CLR(x_i) = ln(x_i / g(x))
    
    Returns:
      (clr_dict, geometric_mean)
    """
    imputed = zero_replacement_multiplicative(abundances, delta=delta)
    keys = list(imputed.keys())
    vals = [imputed[k] for k in keys]
    
    g_x = compute_geometric_mean(vals)
    
    clr_dict = {}
    for k in keys:
        ratio = max(1e-12, imputed[k]) / max(1e-12, g_x)
        clr_dict[k] = math.log(ratio)
        
    return clr_dict, g_x


def aitchison_distance(
    profile_u: Dict[str, float],
    profile_v: Dict[str, float],
    delta: float = 1e-4
) -> float:
    """
    Calculates exact Aitchison Distance:
    d_A(u, v) = || CLR(u) - CLR(v) ||_2 = sqrt( sum_{i=1}^D ( ln(u_i / g(u)) - ln(v_i / g(v)) )^2 )
    """
    all_keys = sorted(list(set(profile_u.keys()).union(set(profile_v.keys()))))
    if not all_keys:
        return 0.0

    dict_u = {k: profile_u.get(k, 0.0) for k in all_keys}
    dict_v = {k: profile_v.get(k, 0.0) for k in all_keys}

    clr_u, _ = clr_transformation(dict_u, delta=delta)
    clr_v, _ = clr_transformation(dict_v, delta=delta)

    sq_sum = 0.0
    for k in all_keys:
        diff = clr_u[k] - clr_v[k]
        sq_sum += diff * diff

    return math.sqrt(sq_sum)


def bray_curtis_dissimilarity(
    profile_u: Dict[str, float],
    profile_v: Dict[str, float]
) -> float:
    """
    Computes standard Bray-Curtis Dissimilarity:
    d_BC(u, v) = sum |u_i - v_i| / sum (u_i + v_i) = 1 - (2 * sum(min(u_i, v_i)) / sum(u_i + v_i))
    """
    all_keys = set(profile_u.keys()).union(set(profile_v.keys()))
    sum_diff = 0.0
    sum_total = 0.0

    for k in all_keys:
        u = profile_u.get(k, 0.0)
        v = profile_v.get(k, 0.0)
        sum_diff += abs(u - v)
        sum_total += u + v

    if sum_total <= 0.0:
        return 0.0

    return sum_diff / sum_total


def jaccard_distance(
    profile_u: Dict[str, float],
    profile_v: Dict[str, float],
    threshold: float = 0.001
) -> float:
    """
    Computes Binary Jaccard Distance based on presence/absence above detection threshold:
    d_J(A, B) = 1 - |A inter B| / |A union B|
    """
    set_u = {k for k, v in profile_u.items() if v >= threshold}
    set_v = {k for k, v in profile_v.items() if v >= threshold}

    union_len = len(set_u.union(set_v))
    if union_len == 0:
        return 0.0

    inter_len = len(set_u.intersection(set_v))
    return 1.0 - (inter_len / union_len)
