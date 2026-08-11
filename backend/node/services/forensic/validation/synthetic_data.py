"""
Synthetic STR Profile Generator for FORENZA Validation Lab.
Produces deterministic, reproducible datasets of true-match, true-unrelated,
parent-child, full-sibling, 2-person mixture, and dropout profile pairs.
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from ..frequency_db import POPULATION_FREQUENCIES, FrequencyDatabase
from ..models import STRGenotype, STRProfile, SampleType
from ..str_engine import CODIS_20_LOCI


class PairType(str, Enum):
    TRUE_MATCH = "true_match"
    TRUE_UNRELATED = "true_unrelated"
    PARENT_CHILD = "parent_child"
    FULL_SIBLING = "full_sibling"
    HALF_SIBLING = "half_sibling"
    MIXTURE_2P = "mixture_2_person"
    DROPOUT_PARTIAL = "dropout_partial"


@dataclass
class SyntheticPair:
    """A generated profile pair with known ground-truth relationship label."""
    pair_id: str
    pair_type: PairType
    profile1: STRProfile
    profile2: STRProfile
    true_lr: Optional[float] = None  # Known LR from simulation


class SyntheticDataGenerator:
    """
    Generates synthetic forensic STR profile pairs for validation.
    All randomness is seeded for full reproducibility.
    """

    LOCI = [l for l in CODIS_20_LOCI if l != "AMEL"]

    def __init__(self, population: str = "Caucasian", seed: int = 42):
        self.population = population
        self.seed = seed
        self.freq_db = FrequencyDatabase(default_population=population)
        self._rng = random.Random(seed)
        self._build_allele_pools()

    def _build_allele_pools(self) -> None:
        """Builds weighted allele sampling pools per locus."""
        pop_db = POPULATION_FREQUENCIES.get(self.population, POPULATION_FREQUENCIES["Caucasian"])
        self._allele_pools: Dict[str, Tuple[List[float], List[float]]] = {}
        for locus, freq_map in pop_db.items():
            if locus == "AMEL":
                continue
            alleles = list(freq_map.keys())
            weights = list(freq_map.values())
            self._allele_pools[locus] = (alleles, weights)

    def _sample_allele(self, locus: str) -> float:
        """Samples a single allele from the locus frequency distribution."""
        alleles, weights = self._allele_pools[locus]
        return self._rng.choices(alleles, weights=weights, k=1)[0]

    def _sample_genotype(self, locus: str) -> STRGenotype:
        """Samples an independent genotype (Hardy-Weinberg) for a locus."""
        a1 = self._sample_allele(locus)
        a2 = self._sample_allele(locus)
        return STRGenotype(locus_name=locus, allele1=a1, allele2=a2)

    def _make_profile(self, profile_id: str, loci: Optional[List[str]] = None) -> STRProfile:
        """Generates a full random STR profile."""
        target_loci = loci or self.LOCI
        genotypes = {l: self._sample_genotype(l) for l in target_loci if l in self._allele_pools}
        return STRProfile(
            profile_id=profile_id,
            loci=genotypes,
            population_group=self.population
        )

    def generate_true_match_pair(self, pair_id: str) -> SyntheticPair:
        """Both profiles are identical (same person, replicate extraction)."""
        p1 = self._make_profile(f"{pair_id}_P1")
        p2 = STRProfile(
            profile_id=f"{pair_id}_P2",
            loci=dict(p1.loci),
            population_group=self.population
        )
        return SyntheticPair(pair_id=pair_id, pair_type=PairType.TRUE_MATCH, profile1=p1, profile2=p2)

    def generate_unrelated_pair(self, pair_id: str) -> SyntheticPair:
        """Both profiles are independently sampled (unrelated individuals)."""
        p1 = self._make_profile(f"{pair_id}_P1")
        p2 = self._make_profile(f"{pair_id}_P2")
        return SyntheticPair(pair_id=pair_id, pair_type=PairType.TRUE_UNRELATED, profile1=p1, profile2=p2)

    def generate_parent_child_pair(self, pair_id: str) -> SyntheticPair:
        """Child inherits one allele from parent at each locus."""
        parent = self._make_profile(f"{pair_id}_PARENT")
        child_loci: Dict[str, STRGenotype] = {}
        for locus, g in parent.loci.items():
            # Child gets one allele from parent (random), one from other random parent
            transmitted = self._rng.choice(g.alleles)
            other = self._sample_allele(locus)
            child_loci[locus] = STRGenotype(locus_name=locus, allele1=transmitted, allele2=other)
        child = STRProfile(
            profile_id=f"{pair_id}_CHILD",
            loci=child_loci,
            population_group=self.population
        )
        return SyntheticPair(pair_id=pair_id, pair_type=PairType.PARENT_CHILD, profile1=parent, profile2=child)

    def generate_full_sibling_pair(self, pair_id: str) -> SyntheticPair:
        """Both siblings inherit alleles from the same two parents."""
        profiles: List[STRProfile] = []
        # Build shared parents
        parent1 = self._make_profile(f"{pair_id}_DAD")
        parent2 = self._make_profile(f"{pair_id}_MOM")
        for sib_id in ["SIB1", "SIB2"]:
            sib_loci: Dict[str, STRGenotype] = {}
            for locus in parent1.loci:
                if locus not in parent2.loci:
                    continue
                from_dad = self._rng.choice(parent1.loci[locus].alleles)
                from_mom = self._rng.choice(parent2.loci[locus].alleles)
                sib_loci[locus] = STRGenotype(locus_name=locus, allele1=from_dad, allele2=from_mom)
            profiles.append(STRProfile(
                profile_id=f"{pair_id}_{sib_id}",
                loci=sib_loci,
                population_group=self.population
            ))
        return SyntheticPair(pair_id=pair_id, pair_type=PairType.FULL_SIBLING,
                             profile1=profiles[0], profile2=profiles[1])

    def generate_dropout_profile(self, pair_id: str, dropout_rate: float = 0.30) -> SyntheticPair:
        """
        Profile 2 has alleles randomly dropped from Profile 1 to simulate
        low-template PCR dropout. Only one allele remains at dropout loci.
        """
        p1 = self._make_profile(f"{pair_id}_FULL")
        dropout_loci: Dict[str, STRGenotype] = {}
        for locus, g in p1.loci.items():
            if self._rng.random() < dropout_rate and not g.is_homozygote:
                # Drop one allele — keep only one as apparent homozygote
                kept = self._rng.choice(g.alleles)
                dropout_loci[locus] = STRGenotype(locus_name=locus, allele1=kept, allele2=kept)
            else:
                dropout_loci[locus] = g
        p2 = STRProfile(
            profile_id=f"{pair_id}_DROPOUT",
            loci=dropout_loci,
            population_group=self.population
        )
        return SyntheticPair(pair_id=pair_id, pair_type=PairType.DROPOUT_PARTIAL, profile1=p1, profile2=p2)

    def generate_dataset(
        self,
        n_per_type: int = 1000
    ) -> Dict[str, List[SyntheticPair]]:
        """
        Generates a balanced synthetic validation dataset.
        Default: 1,000 pairs per type × 5 types = 5,000 pairs.
        Use n_per_type=2000 for a 10,000-pair dataset.
        """
        dataset: Dict[str, List[SyntheticPair]] = {
            PairType.TRUE_MATCH: [],
            PairType.TRUE_UNRELATED: [],
            PairType.PARENT_CHILD: [],
            PairType.FULL_SIBLING: [],
            PairType.DROPOUT_PARTIAL: [],
        }
        for i in range(n_per_type):
            dataset[PairType.TRUE_MATCH].append(
                self.generate_true_match_pair(f"TM_{i:05d}"))
            dataset[PairType.TRUE_UNRELATED].append(
                self.generate_unrelated_pair(f"UR_{i:05d}"))
            dataset[PairType.PARENT_CHILD].append(
                self.generate_parent_child_pair(f"PC_{i:05d}"))
            dataset[PairType.FULL_SIBLING].append(
                self.generate_full_sibling_pair(f"FS_{i:05d}"))
            dataset[PairType.DROPOUT_PARTIAL].append(
                self.generate_dropout_profile(f"DO_{i:05d}", dropout_rate=0.30))
        return dataset
