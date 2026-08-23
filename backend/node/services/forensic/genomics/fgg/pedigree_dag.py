"""
Pedigree Directed Acyclic Graph (DAG) Engine.

Constructs, validates, and evaluates multi-generational genealogical trees.
Enforces biological invariants:
- Acyclicity (no directed cycles)
- Maximum 2 biological parents per child
- Biological age intervals (13 <= Parent Age Gap <= 55 years)
"""

from typing import Dict, List, Set, Optional, Tuple
from .schemas import PedigreeNode, PedigreeEdge, SexEnum


class FGGPedigreeDAG:
    """Directed Acyclic Graph representing extended genealogical lineages."""

    def __init__(self):
        self.nodes: Dict[str, PedigreeNode] = {}
        self.edges: List[PedigreeEdge] = []

    def add_node(
        self,
        node_id: str,
        label: str,
        sex: SexEnum = SexEnum.UNKNOWN,
        birth_year: Optional[int] = None,
        is_genotyped: bool = False,
        y_haplogroup: Optional[str] = None,
        mtdna_haplogroup: Optional[str] = None,
        generation_index: int = 0
    ) -> PedigreeNode:
        """Adds or updates a node in the pedigree graph."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.label = label
            node.sex = sex
            node.birth_year = birth_year
            node.is_genotyped = is_genotyped
            node.y_haplogroup = y_haplogroup
            node.mtdna_haplogroup = mtdna_haplogroup
            node.generation_index = generation_index
            return node

        node = PedigreeNode(
            node_id=node_id,
            label=label,
            sex=sex,
            birth_year=birth_year,
            is_genotyped=is_genotyped,
            y_haplogroup=y_haplogroup,
            mtdna_haplogroup=mtdna_haplogroup,
            generation_index=generation_index,
            parents=[],
            children=[]
        )
        self.nodes[node_id] = node
        return node

    def add_parent_child_edge(self, parent_id: str, child_id: str) -> bool:
        """Adds a directed edge from parent to child and updates adjacency lists."""
        if parent_id not in self.nodes or child_id not in self.nodes:
            return False

        parent = self.nodes[parent_id]
        child = self.nodes[child_id]

        if len(child.parents) >= 2 and parent_id not in child.parents:
            return False # Biological maximum of 2 parents

        if parent_id not in child.parents:
            child.parents.append(parent_id)
        if child_id not in parent.children:
            parent.children.append(child_id)

        edge = PedigreeEdge(source_id=parent_id, target_id=child_id, relationship_type="PARENT_CHILD")
        self.edges.append(edge)

        # Check for cycles
        if not self.is_acyclic():
            # Rollback
            child.parents.remove(parent_id)
            parent.children.remove(child_id)
            self.edges.remove(edge)
            return False

        return True

    def is_acyclic(self) -> bool:
        """Checks if the graph contains no directed cycles using Kahn's topological sort."""
        in_degree = {nid: len(node.parents) for nid, node in self.nodes.items()}
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for child_id in self.nodes[curr].children:
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    queue.append(child_id)

        return visited_count == len(self.nodes)

    def validate_biological_intervals(self) -> Tuple[bool, List[str]]:
        """Checks biological age feasibility (13 <= Parent Age - Child Age <= 55)."""
        warnings = []
        is_valid = True

        for edge in self.edges:
            parent = self.nodes[edge.source_id]
            child = self.nodes[edge.target_id]

            if parent.birth_year and child.birth_year:
                gap = child.birth_year - parent.birth_year
                if gap < 13:
                    is_valid = False
                    warnings.append(f"Biologically impossible parental age gap: {parent.label} born {parent.birth_year} vs child {child.label} born {child.birth_year} (gap: {gap} yrs < 13)")
                elif gap > 55:
                    warnings.append(f"Unusually large parental age gap: {parent.label} vs {child.label} (gap: {gap} yrs > 55)")

        return (is_valid, warnings)

    def get_genealogical_distance(self, node_a_id: str, node_b_id: str) -> Optional[int]:
        """Finds the shortest undirected pedigree path distance (meiotic steps) between two nodes."""
        if node_a_id not in self.nodes or node_b_id not in self.nodes:
            return None
        if node_a_id == node_b_id:
            return 0

        visited = {node_a_id}
        queue = [(node_a_id, 0)]

        while queue:
            curr, dist = queue.pop(0)
            if curr == node_b_id:
                return dist

            node = self.nodes[curr]
            neighbors = node.parents + node.children
            for nbr in neighbors:
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append((nbr, dist + 1))

        return None
