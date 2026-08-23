"""
Unit Tests for Genealogical Directed Acyclic Graph (DAG) Operations.
"""

import pytest
from backend.node.services.forensic.genomics.fgg.schemas import SexEnum
from backend.node.services.forensic.genomics.fgg.pedigree_dag import FGGPedigreeDAG


class TestFGGPedigreeDAG:
    """Tests DAG construction, cycle detection, and biological age gap validation."""

    def test_dag_creation_and_topology(self):
        dag = FGGPedigreeDAG()
        gfather = dag.add_node("GF", "Grandfather", SexEnum.MALE, 1940)
        gmother = dag.add_node("GM", "Grandmother", SexEnum.FEMALE, 1942)
        father = dag.add_node("F", "Father", SexEnum.MALE, 1970)
        child = dag.add_node("C", "Child", SexEnum.FEMALE, 2000)

        assert dag.add_parent_child_edge("GF", "F") is True
        assert dag.add_parent_child_edge("GM", "F") is True
        assert dag.add_parent_child_edge("F", "C") is True
        assert dag.is_acyclic() is True
        assert len(dag.nodes) == 4
        assert len(dag.edges) == 3

    def test_cycle_rejection(self):
        dag = FGGPedigreeDAG()
        dag.add_node("A", "Person A")
        dag.add_node("B", "Person B")
        dag.add_node("C", "Person C")

        assert dag.add_parent_child_edge("A", "B") is True
        assert dag.add_parent_child_edge("B", "C") is True
        # Adding C -> A would create a cycle (C is ancestor of A)
        assert dag.add_parent_child_edge("C", "A") is False
        assert dag.is_acyclic() is True

    def test_biological_interval_validation(self):
        # Valid intervals: Father (1970) -> Child (2000) gap=30 yrs (Valid in [13, 55])
        dag = FGGPedigreeDAG()
        dag.add_node("F", "Father", SexEnum.MALE, 1970)
        dag.add_node("C", "Child", SexEnum.MALE, 2000)
        dag.add_parent_child_edge("F", "C")
        is_valid, warnings = dag.validate_biological_intervals()
        assert is_valid is True
        assert len(warnings) == 0

        # Invalid interval: Father (1995) -> Child (2000) gap=5 yrs (Impossible < 13)
        dag_invalid = FGGPedigreeDAG()
        dag_invalid.add_node("F_young", "Too Young", SexEnum.MALE, 1995)
        dag_invalid.add_node("C_child", "Child", SexEnum.MALE, 2000)
        dag_invalid.add_parent_child_edge("F_young", "C_child")
        is_valid_inv, warnings_inv = dag_invalid.validate_biological_intervals()
        assert is_valid_inv is False
        assert len(warnings_inv) >= 1

    def test_genealogical_distance(self):
        dag = FGGPedigreeDAG()
        dag.add_node("GF", "Grandfather")
        dag.add_node("F", "Father")
        dag.add_node("C", "Child")
        dag.add_parent_child_edge("GF", "F")
        dag.add_parent_child_edge("F", "C")

        assert dag.get_genealogical_distance("GF", "C") == 2
        assert dag.get_genealogical_distance("F", "C") == 1
        assert dag.get_genealogical_distance("C", "C") == 0
