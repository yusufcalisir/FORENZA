"""
FORENZA Forensic Knowledge Graph & Genetics Database Engine.
Models multi-relational property graphs across Case, Person, Evidence, Sample, DnaProfile, Reference, Scene, and Report nodes.
Executes Adjacency Matrix traversal (A^k), BFS shortest path discovery, and Case subgraph extraction.

References:
  Needham & Hodler (2019) Graph Algorithms: Practical Examples in Apache Spark and Neo4j.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class GraphNode:
    node_id: str
    node_type: str                     # 'Case', 'Person', 'Evidence', 'Sample', 'DnaProfile', 'Reference', 'Scene', 'Report'
    label: str
    properties: Dict[str, str] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relation_type: str                 # 'BIOLOGICAL_PARENT', 'DNA_CONTRIBUTOR', 'COLLECTED_FROM', 'MATCHED_TO', 'ASSOCIATED_CASE', 'SCENE_LOCATION'
    weight: float = 1.0


@dataclass
class PathTraversalResult:
    source_id: str
    target_id: str
    path_found: bool
    path_nodes: List[str]
    path_relations: List[str]
    distance: int


class ForensicKnowledgeGraph:
    """
    In-memory directed property graph engine for forensic intelligence.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.adjacency: Dict[str, List[GraphEdge]] = {}
        self.reverse_adjacency: Dict[str, List[GraphEdge]] = {}

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.node_id] = node
        if node.node_id not in self.adjacency:
            self.adjacency[node.node_id] = []
        if node.node_id not in self.reverse_adjacency:
            self.reverse_adjacency[node.node_id] = []

    def add_edge(self, edge: GraphEdge) -> None:
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            raise ValueError(f"Cannot add edge {edge.source_id} -> {edge.target_id}: Nodes must exist first.")

        self.adjacency[edge.source_id].append(edge)
        self.reverse_adjacency[edge.target_id].append(edge)

    def traverse_shortest_path(self, source_id: str, target_id: str) -> PathTraversalResult:
        """BFS shortest path discovery across directed relations."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return PathTraversalResult(source_id, target_id, False, [], [], -1)

        visited: Set[str] = {source_id}
        queue: deque = deque([(source_id, [source_id], [])])

        while queue:
            curr_id, path_nodes, path_rels = queue.popleft()
            if curr_id == target_id:
                return PathTraversalResult(
                    source_id=source_id,
                    target_id=target_id,
                    path_found=True,
                    path_nodes=path_nodes,
                    path_relations=path_rels,
                    distance=len(path_nodes) - 1
                )

            for edge in self.adjacency.get(curr_id, []):
                nxt = edge.target_id
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path_nodes + [nxt], path_rels + [edge.relation_type]))

        return PathTraversalResult(source_id, target_id, False, [], [], -1)

    def extract_case_subgraph(self, case_id: str) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Extracts all nodes and directed edges associated with a specific case."""
        subgraph_nodes: List[GraphNode] = []
        subgraph_edges: List[GraphEdge] = []
        visited_nodes: Set[str] = set()

        if case_id in self.nodes:
            visited_nodes.add(case_id)
            subgraph_nodes.append(self.nodes[case_id])

        # Traverse edges connected to case_id or related entities
        for src, edges in self.adjacency.items():
            for e in edges:
                if e.source_id == case_id or e.target_id == case_id:
                    subgraph_edges.append(e)
                    if e.source_id not in visited_nodes:
                        visited_nodes.add(e.source_id)
                        subgraph_nodes.append(self.nodes[e.source_id])
                    if e.target_id not in visited_nodes:
                        visited_nodes.add(e.target_id)
                        subgraph_nodes.append(self.nodes[e.target_id])

        return subgraph_nodes, subgraph_edges
