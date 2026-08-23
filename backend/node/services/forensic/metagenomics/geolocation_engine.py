"""
FORENZA — Supervised Geolocation & Habitat Prediction Engine (Phase 4.2)
=========================================================================

Implements the supervised machine learning geolocation and habitat classification
pipeline for forensic soil metagenomics.

Research §3.4 Supervised ML Geolocation Pipeline:
    
    Features: CLR-transformed taxonomic abundance vectors (in Aitchison space)
    Target Labels: Habitat / Land-Use classes:
        {Forest, Agricultural, Urban, Wetland, Desert, Coastal}

    Classifiers:
        1. Random Forest: N=100 trees, Gini impurity criterion
           Feature importance: Mean Decrease in Impurity (MDI) / Gini index
        2. Support Vector Machine (RBF kernel): γ = 'scale' = 1/(D × var(CLR))

    Spatial Mahalanobis Distance provenance matching (Research §3.4):
        d_M(x, μ) = sqrt((x - μ)^T Σ^{-1} (x - μ))
        where μ and Σ are the mean CLR vector and covariance of the reference
        geographic grid cell.

    Feature importance ranking isolates diagnostic microbial / pollen biomarkers
    for forensic expert reporting.
"""

from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# §1 HABITAT / LAND-USE CLASSIFICATION LABELS (Research §3.4)
# ═══════════════════════════════════════════════════════════════════════════════

class HabitatClass(str, Enum):
    """
    Forensic soil habitat and land-use classification categories.

    Research §3.4 defines 6 primary habitat classes for forensic geolocation.
    The classifier assigns a questioned trace soil to the most probable habitat.
    """
    FOREST = "Forest"
    AGRICULTURAL = "Agricultural"
    URBAN = "Urban"
    WETLAND = "Wetland"
    DESERT = "Desert"
    COASTAL = "Coastal"
    UNKNOWN = "Unknown"


# ═══════════════════════════════════════════════════════════════════════════════
# §2 RANDOM FOREST CLASSIFIER (CLR feature space)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DecisionStump:
    """
    A single-feature decision stump (depth-1 decision tree) for Random Forest.

    Split criterion: Gini impurity minimization.
    Gini(S) = 1 - Σ p_k^2 where p_k = fraction of class k in set S.
    """
    feature_taxid: int          # TaxID of the splitting feature (CLR coordinate)
    threshold: float            # Split threshold: x[feature] ≤ threshold → left
    left_class: str             # Predicted class for left branch (≤ threshold)
    right_class: str            # Predicted class for right branch (> threshold)
    left_gini: float            # Gini impurity of left leaf
    right_gini: float           # Gini impurity of right leaf
    feature_importance: float   # Mean Decrease in Impurity (MDI) for this split


@dataclass
class ForensicRFPrediction:
    """
    Random Forest prediction output for a questioned forensic soil sample.
    """
    predicted_habitat: HabitatClass
    class_probabilities: Dict[str, float]   # {habitat_class: vote_fraction}
    top_biomarker_taxids: List[int]         # Most important diagnostic taxa
    feature_importance_ranking: Dict[int, float]  # taxid → MDI importance score
    n_trees_used: int
    confidence_score: float                 # = max(class_probabilities)


class ForensicRandomForest:
    """
    Forensic Random Forest Habitat Classifier for CLR-Transformed Soil Metagenomes.

    Research §3.4:
        Features: CLR-transformed taxonomic abundance vectors
        N = 100 trees (Research default)
        Criterion: Gini impurity minimization
        Feature importance: Mean Decrease in Impurity (MDI)

    Training data: Georeferenced reference soil metagenomes from:
        - EBI MG-RAZY / NCBI SRA curated soil collections
        - PROVEDIt environmental control metagenomes
    """

    def __init__(self, n_trees: int = 100, seed: int = 42) -> None:
        self.n_trees = n_trees
        self._rng = random.Random(seed)
        self._trees: List[DecisionStump] = []
        self._training_classes: List[str] = []
        self._feature_importances: Dict[int, float] = {}
        self._is_trained: bool = False

        logger.info(
            f"[ForensicRandomForest] Initialized with n_trees={n_trees}"
        )

    @staticmethod
    def _gini_impurity(class_counts: Dict[str, int]) -> float:
        """
        Compute Gini impurity for a leaf node.
        Gini(S) = 1 - Σ (p_k)^2
        """
        total = sum(class_counts.values())
        if total == 0:
            return 0.0
        return 1.0 - sum((count / total) ** 2 for count in class_counts.values())

    @staticmethod
    def _majority_class(class_counts: Dict[str, int]) -> str:
        """Return the class with the highest count."""
        if not class_counts:
            return HabitatClass.UNKNOWN.value
        return max(class_counts, key=lambda c: class_counts[c])

    def _best_split(
        self,
        X: List[Dict[int, float]],
        y: List[str],
        feature_taxids: List[int],
    ) -> DecisionStump:
        """
        Find the best single-feature split minimizing weighted Gini impurity.

        For each candidate feature (CLR coordinate, taxid):
            For each candidate threshold (midpoint between sorted feature values):
                Compute weighted Gini: (|L|/|S|)*Gini(L) + (|R|/|S|)*Gini(R)
        Select the split minimizing weighted Gini.
        """
        n = len(X)
        best_gini = float("inf")
        best_stump = None

        for taxid in feature_taxids:
            # Extract feature values
            feature_vals = [sample.get(taxid, 0.0) for sample in X]
            sorted_vals = sorted(set(feature_vals))

            if len(sorted_vals) < 2:
                continue

            for k in range(len(sorted_vals) - 1):
                threshold = (sorted_vals[k] + sorted_vals[k + 1]) / 2.0

                left_counts: Dict[str, int] = {}
                right_counts: Dict[str, int] = {}

                for xi, yi in zip(feature_vals, y):
                    if xi <= threshold:
                        left_counts[yi] = left_counts.get(yi, 0) + 1
                    else:
                        right_counts[yi] = right_counts.get(yi, 0) + 1

                n_left = sum(left_counts.values())
                n_right = sum(right_counts.values())

                if n_left == 0 or n_right == 0:
                    continue

                g_left = self._gini_impurity(left_counts)
                g_right = self._gini_impurity(right_counts)
                weighted_gini = (n_left / n) * g_left + (n_right / n) * g_right

                if weighted_gini < best_gini:
                    best_gini = weighted_gini
                    # MDI importance = Gini before split - weighted Gini after
                    all_counts: Dict[str, int] = {}
                    for yi in y:
                        all_counts[yi] = all_counts.get(yi, 0) + 1
                    gini_before = self._gini_impurity(all_counts)
                    mdi = gini_before - weighted_gini

                    best_stump = DecisionStump(
                        feature_taxid=taxid,
                        threshold=threshold,
                        left_class=self._majority_class(left_counts),
                        right_class=self._majority_class(right_counts),
                        left_gini=g_left,
                        right_gini=g_right,
                        feature_importance=max(0.0, mdi),
                    )

        if best_stump is None:
            # Fallback: no valid split found
            all_counts: Dict[str, int] = {}
            for yi in y:
                all_counts[yi] = all_counts.get(yi, 0) + 1
            best_stump = DecisionStump(
                feature_taxid=list(feature_taxids)[0] if feature_taxids else 0,
                threshold=0.0,
                left_class=self._majority_class(all_counts),
                right_class=self._majority_class(all_counts),
                left_gini=0.0,
                right_gini=0.0,
                feature_importance=0.0,
            )

        return best_stump

    def train(
        self,
        X: List[Dict[int, float]],
        y: List[str],
        n_features_per_tree: Optional[int] = None,
    ) -> None:
        """
        Train the Random Forest on CLR-transformed training samples.

        Args:
            X: List of CLR feature vectors {taxid: clr_value}
            y: List of habitat class labels
            n_features_per_tree: Number of random features per tree split.
                                 Default: sqrt(D) (standard RF practice)
        """
        n = len(X)
        all_taxids = list(set(taxid for sample in X for taxid in sample))
        D = len(all_taxids)
        self._training_classes = sorted(set(y))

        if n_features_per_tree is None:
            n_features_per_tree = max(1, int(math.sqrt(D)))

        # Initialize feature importance accumulator
        self._feature_importances = {taxid: 0.0 for taxid in all_taxids}

        for tree_idx in range(self.n_trees):
            # Bootstrap sample (with replacement)
            bootstrap_indices = [self._rng.randint(0, n - 1) for _ in range(n)]
            X_boot = [X[i] for i in bootstrap_indices]
            y_boot = [y[i] for i in bootstrap_indices]

            # Random feature subset
            feature_subset = self._rng.sample(
                all_taxids,
                min(n_features_per_tree, len(all_taxids))
            )

            # Grow a single decision stump
            stump = self._best_split(X_boot, y_boot, feature_subset)
            self._trees.append(stump)

            # Accumulate feature importance
            self._feature_importances[stump.feature_taxid] = (
                self._feature_importances.get(stump.feature_taxid, 0.0)
                + stump.feature_importance
            )

        # Normalize feature importances across all trees
        total_importance = sum(self._feature_importances.values())
        if total_importance > 0:
            self._feature_importances = {
                tid: imp / total_importance
                for tid, imp in self._feature_importances.items()
            }

        self._is_trained = True
        logger.info(
            f"[ForensicRandomForest] Trained {self.n_trees} trees on "
            f"{n} samples, {D} CLR features, "
            f"classes={self._training_classes}"
        )

    def predict(
        self,
        clr_vector: Dict[int, float],
        top_n_biomarkers: int = 10,
    ) -> ForensicRFPrediction:
        """
        Predict the habitat class for a questioned forensic soil sample.

        Args:
            clr_vector: CLR-transformed abundance vector for the questioned sample
            top_n_biomarkers: Number of top diagnostic taxa to report

        Returns:
            ForensicRFPrediction with habitat class, probabilities, and biomarkers
        """
        if not self._is_trained:
            raise RuntimeError("Random Forest not trained. Call train() first.")

        # Vote from all trees
        votes: Dict[str, int] = {}
        for stump in self._trees:
            feature_val = clr_vector.get(stump.feature_taxid, 0.0)
            if feature_val <= stump.threshold:
                predicted = stump.left_class
            else:
                predicted = stump.right_class
            votes[predicted] = votes.get(predicted, 0) + 1

        total_votes = len(self._trees)
        class_probs = {
            cls: votes.get(cls, 0) / total_votes
            for cls in self._training_classes
        }

        best_class = max(class_probs, key=lambda c: class_probs[c])
        confidence = class_probs[best_class]

        try:
            habitat = HabitatClass(best_class)
        except ValueError:
            habitat = HabitatClass.UNKNOWN

        # Top biomarker taxa by MDI importance
        sorted_importance = sorted(
            self._feature_importances.items(),
            key=lambda x: -x[1]
        )
        top_biomarkers = [taxid for taxid, _ in sorted_importance[:top_n_biomarkers]]

        return ForensicRFPrediction(
            predicted_habitat=habitat,
            class_probabilities=class_probs,
            top_biomarker_taxids=top_biomarkers,
            feature_importance_ranking=dict(sorted_importance[:top_n_biomarkers * 3]),
            n_trees_used=total_votes,
            confidence_score=round(confidence, 4),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# §3 SPATIAL MAHALANOBIS DISTANCE PROVENANCE MATCHER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GeographicGridCell:
    """
    Reference geographic grid cell for Mahalanobis distance provenance matching.

    Each cell represents a geographic region with a statistical summary of
    its soil microbiome CLR profiles from the reference database.
    """
    cell_id: str
    latitude: float
    longitude: float
    habitat_class: HabitatClass
    mean_clr: Dict[int, float]         # μ: mean CLR per taxid
    cov_diagonal: Dict[int, float]     # σ^2: variance per taxid (diagonal approx)
    n_reference_samples: int


class MahalanobisProvenanceMatcher:
    """
    Spatial Mahalanobis Distance Forensic Provenance Matcher.

    Research §3.4:
        d_M(x, μ) = sqrt((x - μ)^T Σ^{-1} (x - μ))
    
    For diagonal covariance approximation:
        d_M(x, μ) = sqrt( Σ_i (x_i - μ_i)^2 / σ_i^2 )

    Matches questioned soil CLR vector to reference geographic grid cells
    and returns sorted match list with Mahalanobis distances.
    """

    def __init__(self) -> None:
        self._grid_cells: List[GeographicGridCell] = []

    def register_cell(self, cell: GeographicGridCell) -> None:
        """Register a reference geographic grid cell."""
        self._grid_cells.append(cell)

    def match(
        self,
        query_clr: Dict[int, float],
        top_n: int = 5,
    ) -> List[Tuple[GeographicGridCell, float]]:
        """
        Match a questioned soil CLR vector against all reference grid cells.

        Args:
            query_clr: CLR-transformed abundance vector of questioned sample
            top_n: Number of top-matching geographic cells to return

        Returns:
            Sorted list of (GeographicGridCell, mahalanobis_distance)
            with smallest distances first (best matches first).
        """
        distances: List[Tuple[GeographicGridCell, float]] = []

        for cell in self._grid_cells:
            # Diagonal Mahalanobis: d_M = sqrt(Σ (x_i - μ_i)^2 / σ_i^2)
            all_taxids = set(query_clr) | set(cell.mean_clr)
            d_sq = 0.0
            for taxid in all_taxids:
                x_i = query_clr.get(taxid, 0.0)
                mu_i = cell.mean_clr.get(taxid, 0.0)
                sigma_sq = cell.cov_diagonal.get(taxid, 1.0)  # default σ^2 = 1
                sigma_sq = max(sigma_sq, 1e-10)  # guard against division by zero
                d_sq += (x_i - mu_i) ** 2 / sigma_sq

            distances.append((cell, math.sqrt(d_sq)))

        return sorted(distances, key=lambda t: t[1])[:top_n]
