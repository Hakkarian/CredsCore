"""Core network analysis module for Social Capital Scoring.

Implements social network graph analysis using NetworkX, including:
- Centrality calculations (degree, betweenness, eigenvector)
- Community detection using Louvain algorithm
- Influence scoring (PageRank)
- Trust propagation calculations
- Anomaly detection for fraud indicators
"""

import logging
import random
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any

import numpy as np

logger = logging.getLogger(__name__)


class NetworkGraph:
    """Social network graph representation and analysis.

    This class wraps network analysis functionality with both
    manual implementation and optional NetworkX backend.
    """

    def __init__(self, use_networkx: bool = True) -> None:
        """Initialize the network graph.

        Args:
            use_networkx: Whether to use NetworkX for advanced algorithms.
                        Falls back to manual implementations if False.
        """
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Tuple[str, str, Dict[str, Any]]] = []
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.edge_weights: Dict[Tuple[str, str], float] = {}
        self._use_networkx = use_networkx
        self._nx = None

        if use_networkx:
            try:
                import networkx as nx
                self._nx = nx
                self._graph = nx.Graph()
                logger.info("NetworkX backend initialized")
            except ImportError:
                logger.warning("NetworkX not available, using manual implementations")
                self._use_networkx = False
                self._nx = None

    def add_node(self, node_id: str, **attributes) -> None:
        """Add a node to the graph.

        Args:
            node_id: Unique identifier for the node
            **attributes: Additional node attributes
        """
        self.nodes[node_id] = {
            'id': node_id,
            'added_at': datetime.now().isoformat(),
            **attributes
        }
        if self.adjacency[node_id] is None:
            self.adjacency[node_id] = set()

        if self._use_networkx and self._nx:
            self._graph.add_node(node_id, **attributes)

    def add_edge(self, source: str, target: str, weight: float = 1.0,
                 relationship: str = "friend", **attributes) -> None:
        """Add an edge between two nodes.

        Args:
            source: Source node ID
            target: Target node ID
            weight: Edge weight (default 1.0)
            relationship: Type of relationship
            **attributes: Additional edge attributes
        """
        # Ensure both nodes exist
        if source not in self.nodes:
            self.add_node(source)
        if target not in self.nodes:
            self.add_node(target)

        edge_data = {
            'weight': weight,
            'relationship': relationship,
            **attributes
        }

        self.edges.append((source, target, edge_data))
        self.adjacency[source].add(target)
        self.adjacency[target].add(source)

        # Store weight in both directions
        self.edge_weights[(source, target)] = weight
        self.edge_weights[(target, source)] = weight

        if self._use_networkx and self._nx:
            self._graph.add_edge(source, target, **edge_data)

    def get_neighbors(self, node_id: str) -> Set[str]:
        """Get all neighbors of a node.

        Args:
            node_id: Node to get neighbors for

        Returns:
            Set of neighbor node IDs
        """
        return self.adjacency.get(node_id, set())

    def get_degree(self, node_id: str) -> int:
        """Get the degree of a node.

        Args:
            node_id: Node to get degree for

        Returns:
            Number of connections
        """
        return len(self.adjacency.get(node_id, set()))

    def get_edge_weight(self, source: str, target: str) -> float:
        """Get the weight of an edge.

        Args:
            source: Source node ID
            target: Target node ID

        Returns:
            Edge weight or 0 if not found
        """
        return self.edge_weights.get((source, target), 0.0)

    def calculate_centrality(self, node_id: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """Calculate centrality metrics for nodes.

        Computes degree, betweenness, closeness, and eigenvector centrality.

        Args:
            node_id: Specific node to calculate for (None for all)

        Returns:
            Dictionary mapping node IDs to centrality metrics
        """
        if self._use_networkx and self._nx:
            return self._calculate_centrality_networkx(node_id)
        return self._calculate_centrality_manual(node_id)

    def _calculate_centrality_networkx(self, node_id: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """Calculate centrality using NetworkX."""
        result: Dict[str, Dict[str, float]] = {}

        try:
            # Degree centrality
            dc = self._nx.degree_centrality(self._graph)
            # Betweenness centrality
            bc = self._nx.betweenness_centrality(self._graph, weight='weight')
            # Closeness centrality
            cc = self._nx.closeness_centrality(self._graph)
            # Eigenvector centrality
            ec = self._nx.eigenvector_centrality(self._graph, weight='weight', max_iter=100)

            nodes = [node_id] if node_id else self.nodes.keys()
            for nid in nodes:
                if nid in self.nodes:
                    result[nid] = {
                        'degree': dc.get(nid, 0.0),
                        'betweenness': bc.get(nid, 0.0),
                        'closeness': cc.get(nid, 0.0),
                        'eigenvector': ec.get(nid, 0.0),
                        'normalized': True
                    }
        except Exception as e:
            logger.warning(f"NetworkX centrality failed: {e}, falling back to manual")
            return self._calculate_centrality_manual(node_id)

        return result

    def _calculate_centrality_manual(self, node_id: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """Calculate centrality using manual implementations."""
        result: Dict[str, Dict[str, float]] = {}

        nodes = [node_id] if node_id else list(self.nodes.keys())
        if not nodes:
            return result

        n = len(self.nodes)
        if n < 2:
            return {nid: {'degree': 0.0, 'betweenness': 0.0, 'closeness': 0.0,
                         'eigenvector': 0.0, 'normalized': True} for nid in nodes}

        # Degree centrality (normalized)
        max_degree = max(len(self.adjacency.get(nid, set())) for nid in self.nodes.keys())
        max_degree = max(max_degree, 1)

        for nid in nodes:
            if nid not in self.nodes:
                continue

            degree = len(self.adjacency.get(nid, set()))
            degree_cent = degree / (n - 1) if n > 1 else 0.0

            # Approximate betweenness using local clustering
            # Full betweenness requires all-pairs shortest paths (expensive)
            betweenness = self._approximate_betweenness(nid)

            # Approximate closeness using average distance to neighbors
            closeness = self._approximate_closeness(nid)

            # Simple eigenvector approximation
            eigenvector = degree_cent * 0.5  # Simplified

            result[nid] = {
                'degree': degree_cent,
                'betweenness': betweenness,
                'closeness': closeness,
                'eigenvector': eigenvector,
                'normalized': True
            }

        return result

    def _approximate_betweenness(self, node_id: str, sample_size: int = 50) -> float:
        """Approximate betweenness centrality."""
        if node_id not in self.nodes:
            return 0.0

        # Sample of paths this node might be on
        betweenness = 0.0
        other_nodes = [n for n in self.nodes.keys() if n != node_id]

        if len(other_nodes) < 2:
            return 0.0

        sample = random.sample(other_nodes, min(sample_size, len(other_nodes) // 2 + 1))

        # Count how often this node appears in shortest paths
        for source in sample[:len(sample)//2]:
            for target in sample[len(sample)//2:]:
                if self._is_on_shortest_path(source, target, node_id):
                    betweenness += 1.0

        total_pairs = len(other_nodes) * (len(other_nodes) - 1) / 2
        return betweenness / max(total_pairs, 1) * 2  # Normalize

    def _is_on_shortest_path(self, source: str, target: str, node: str, max_depth: int = 4) -> bool:
        """Check if node lies on a shortest path between source and target."""
        if node == source or node == target:
            return False

        # BFS from source
        distances: Dict[str, int] = {source: 0}
        queue = [source]
        visited = {source}

        while queue:
            current = queue.pop(0)
            if current == target:
                break
            if distances[current] >= max_depth:
                continue

            for neighbor in self.adjacency.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)

        if target not in distances:
            return False

        # Check if going through node gives same distance
        if node not in distances:
            return False

        # Check distance from node to target
        distances2: Dict[str, int] = {node: 0}
        queue = [node]
        visited2 = {node}

        while queue:
            current = queue.pop(0)
            if current == target:
                break
            if distances2[current] >= max_depth:
                continue

            for neighbor in self.adjacency.get(current, set()):
                if neighbor not in visited2:
                    visited2.add(neighbor)
                    distances2[neighbor] = distances2[current] + 1
                    queue.append(neighbor)

        if target not in distances2:
            return False

        # Node is on shortest path if distances match
        return distances[target] == distances[node] + distances2[target]

    def _approximate_closeness(self, node_id: str) -> float:
        """Approximate closeness centrality."""
        if node_id not in self.nodes or len(self.nodes) < 2:
            return 0.0

        # BFS to get distances
        visited: Dict[str, int] = {node_id: 0}
        queue = [node_id]
        total_distance = 0
        reachable = 0

        while queue:
            current = queue.pop(0)
            current_dist = visited[current]

            if current_dist > 0:
                total_distance += current_dist
                reachable += 1

            if current_dist < 4:  # Depth limit
                for neighbor in self.adjacency.get(current, set()):
                    if neighbor not in visited:
                        visited[neighbor] = current_dist + 1
                        queue.append(neighbor)

        if reachable == 0:
            return 0.0

        # Closeness = (reachable / (n-1)) * (n-1) / total_distance
        n = len(self.nodes)
        return (reachable / (n - 1)) * (reachable / total_distance)

    def detect_communities(self) -> Dict[str, int]:
        """Detect communities in the network using Louvain algorithm.

        Returns:
            Dictionary mapping node IDs to community IDs
        """
        if self._use_networkx and self._nx:
            try:
                import community as community_louvain
                partition = community_louvain.best_partition(self._graph)
                return partition
            except ImportError:
                logger.warning("python-louvain not available, using manual community detection")
            except Exception as e:
                logger.warning(f"Louvain detection failed: {e}")

        return self._detect_communities_manual()

    def _detect_communities_manual(self) -> Dict[str, int]:
        """Manual community detection using label propagation."""
        if len(self.nodes) == 0:
            return {}

        # Label propagation algorithm
        labels: Dict[str, int] = {nid: i for i, nid in enumerate(self.nodes.keys())}

        changed = True
        iterations = 0
        max_iterations = 100

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            node_order = list(self.nodes.keys())
            random.shuffle(node_order)

            for node in node_order:
                neighbors = self.adjacency.get(node, set())
                if not neighbors:
                    continue

                # Count labels in neighborhood
                label_counts: Dict[int, int] = defaultdict(int)
                for neighbor in neighbors:
                    label_counts[labels[neighbor]] += 1

                if label_counts:
                    # Find most common label
                    new_label = max(label_counts.items(), key=lambda x: x[1])[0]
                    if new_label != labels[node]:
                        labels[node] = new_label
                        changed = True

        # Renumber communities to be 0-indexed and contiguous
        unique_labels = sorted(set(labels.values()))
        label_map = {old: new for new, old in enumerate(unique_labels)}

        return {nid: label_map[labels[nid]] for nid in labels}

    def calculate_influence(self) -> Dict[str, float]:
        """Calculate influence scores using PageRank-like algorithm.

        Returns:
            Dictionary mapping node IDs to influence scores
        """
        if self._use_networkx and self._nx:
            try:
                pr = self._nx.pagerank(self._graph, weight='weight')
                return pr
            except Exception as e:
                logger.warning(f"NetworkX PageRank failed: {e}")

        return self._calculate_pagerank_manual()

    def _calculate_pagerank_manual(self, damping: float = 0.85,
                                   max_iterations: int = 100,
                                   tolerance: float = 1e-6) -> Dict[str, float]:
        """Manual PageRank implementation."""
        if len(self.nodes) == 0:
            return {}

        n = len(self.nodes)
        # Initialize uniformly
        ranks: Dict[str, float] = {nid: 1.0 / n for nid in self.nodes}

        for iteration in range(max_iterations):
            new_ranks: Dict[str, float] = {}
            max_diff = 0.0

            for node in self.nodes:
                neighbors = self.adjacency.get(node, set())

                # Calculate contribution from neighbors
                contribution = 0.0
                for neighbor in neighbors:
                    neighbor_degree = len(self.adjacency.get(neighbor, set()))
                    if neighbor_degree > 0:
                        weight = self.edge_weights.get((neighbor, node), 1.0)
                        contribution += ranks[neighbor] * weight / neighbor_degree

                # PageRank formula
                new_rank = (1 - damping) / n + damping * contribution
                new_ranks[node] = new_rank

                max_diff = max(max_diff, abs(new_rank - ranks[node]))

            ranks = new_ranks

            if max_diff < tolerance:
                logger.debug(f"PageRank converged after {iteration + 1} iterations")
                break

        # Normalize to [0, 1]
        max_rank = max(ranks.values()) if ranks else 1.0
        if max_rank > 0:
            ranks = {k: v / max_rank for k, v in ranks.items()}

        return ranks

    def calculate_trust(self, max_depth: int = 3) -> Dict[str, float]:
        """Calculate trust scores through network propagation.

        Trust propagates from trusted nodes through the network,
        decaying with distance.

        Args:
            max_depth: Maximum propagation depth

        Returns:
            Dictionary mapping node IDs to trust scores
        """
        trust: Dict[str, float] = {}

        for node_id in self.nodes:
            # Start with base trust from direct connections
            base_trust = self._calculate_base_trust(node_id)

            # Add propagated trust from network
            propagated_trust = self._propagate_trust(node_id, max_depth)

            # Combine (weighted average)
            trust[node_id] = 0.6 * base_trust + 0.4 * propagated_trust

        return trust

    def _calculate_base_trust(self, node_id: str) -> float:
        """Calculate base trust from direct connections."""
        neighbors = self.adjacency.get(node_id, set())
        if not neighbors:
            return 0.5  # Neutral trust for isolated nodes

        # Trust is based on number of connections and edge weights
        total_weight = sum(self.edge_weights.get((node_id, neighbor), 1.0)
                          for neighbor in neighbors)

        # Normalize: more connections with higher weights = more trust
        avg_weight = total_weight / len(neighbors)
        connection_factor = min(len(neighbors) / 10, 1.0)  # Cap at 10 connections

        return min(0.3 + 0.5 * avg_weight + 0.2 * connection_factor, 1.0)

    def _propagate_trust(self, node_id: str, max_depth: int) -> float:
        """Propagate trust through network."""
        # BFS to collect nodes at each depth
        trust_sum = 0.0
        total_weight = 0.0

        visited: Dict[str, int] = {node_id: 0}
        queue = [node_id]

        while queue:
            current = queue.pop(0)
            current_depth = visited[current]

            if current_depth >= max_depth:
                continue

            for neighbor in self.adjacency.get(current, set()):
                if neighbor not in visited:
                    visited[neighbor] = current_depth + 1
                    queue.append(neighbor)

                    # Add trust contribution (decays with distance)
                    decay = 0.7 ** visited[neighbor]
                    edge_weight = self.edge_weights.get((current, neighbor), 1.0)
                    trust_sum += edge_weight * decay
                    total_weight += decay

        if total_weight == 0:
            return 0.5

        return min(trust_sum / total_weight, 1.0)

    def detect_anomalies(self) -> Dict[str, Any]:
        """Detect anomalous network patterns that may indicate fraud.

        Returns:
            Dictionary with anomaly detection results
        """
        anomalies = {
            'suspicious_nodes': [],
            'suspicious_patterns': [],
            'anomaly_count': 0,
            'risk_level': 'low',
            'details': {}
        }

        # Check for star patterns (one node connected to many fraudsters)
        star_patterns = self._detect_star_patterns()
        if star_patterns:
            anomalies['suspicious_patterns'].extend(['star_pattern'] * len(star_patterns))
            anomalies['suspicious_nodes'].extend(star_patterns)

        # Check for clique patterns (tight groups with identical connections)
        clique_patterns = self._detect_cliques()
        if clique_patterns:
            anomalies['suspicious_patterns'].extend(['clique_pattern'] * len(clique_patterns))

        # Check for bridge nodes (connecting otherwise disconnected groups)
        bridge_nodes = self._detect_bridge_nodes()
        if bridge_nodes:
            anomalies['suspicious_patterns'].append('unusual_bridges')
            anomalies['suspicious_nodes'].extend(bridge_nodes[:3])

        # Calculate anomaly score based on findings
        anomalies['anomaly_count'] = len(anomalies['suspicious_nodes'])

        if anomalies['anomaly_count'] > 5:
            anomalies['risk_level'] = 'high'
        elif anomalies['anomaly_count'] > 2:
            anomalies['risk_level'] = 'medium'

        anomalies['anomalies_detected'] = anomalies['anomaly_count'] > 0

        return anomalies

    def _detect_star_patterns(self, threshold: float = 0.8) -> List[str]:
        """Detect star patterns (hub nodes with high clustering neighbors)."""
        suspicious = []

        for node in self.nodes:
            neighbors = self.adjacency.get(node, set())
            if len(neighbors) < 3:
                continue

            # Check if neighbors are well-connected (clique-like)
            neighbor_edges = 0
            for n1 in neighbors:
                for n2 in neighbors:
                    if n1 != n2 and n2 in self.adjacency.get(n1, set()):
                        neighbor_edges += 1

            possible_edges = len(neighbors) * (len(neighbors) - 1)
            if possible_edges > 0:
                clustering = neighbor_edges / possible_edges
                if clustering > threshold:
                    suspicious.append(node)

        return suspicious

    def _detect_cliques(self, size: int = 4) -> List[List[str]]:
        """Detect suspicious cliques."""
        cliques = []

        # Find potential cliques (simplified)
        for node in self.nodes:
            neighbors = self.adjacency.get(node, set())
            if len(neighbors) >= size - 1:
                # Check if neighbors form a clique
                potential_clique = {node} | neighbors
                if len(potential_clique) >= size:
                    cliques.append(list(potential_clique)[:size])

        return cliques[:5]  # Limit results

    def _detect_bridge_nodes(self) -> List[str]:
        """Detect nodes that bridge otherwise disconnected communities."""
        bridges = []

        centrality = self.calculate_centrality()

        for node_id, metrics in centrality.items():
            # High betweenness, relatively low degree = suspicious bridge
            betweenness = metrics.get('betweenness', 0)
            degree = metrics.get('degree', 0)

            if betweenness > 0.3 and degree < 0.3:
                bridges.append(node_id)

        return bridges

    def get_network_stats(self) -> Dict[str, Any]:
        """Get basic network statistics.

        Returns:
            Dictionary with network statistics
        """
        n = len(self.nodes)
        m = len(self.edges)

        if n < 2:
            return {
                'node_count': n,
                'edge_count': m,
                'density': 0.0,
                'average_degree': 0.0
            }

        # Calculate density
        max_edges = n * (n - 1) / 2
        density = m / max_edges if max_edges > 0 else 0.0

        # Calculate average degree
        total_degree = sum(len(self.adjacency.get(node, set())) for node in self.nodes)
        avg_degree = total_degree / n

        return {
            'node_count': n,
            'edge_count': m,
            'density': density,
            'average_degree': avg_degree
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            'nodes': [
                {'id': nid, **self.nodes[nid]}
                for nid in self.nodes
            ],
            'edges': [
                {'source': s, 'target': t, **data}
                for s, t, data in self.edges
            ],
            'stats': self.get_network_stats()
        }


class NetworkAnalyzer:
    """High-level network analysis interface."""

    def __init__(self, use_networkx: bool = True):
        """Initialize analyzer.

        Args:
            use_networkx: Whether to use NetworkX backend
        """
        self.graph = NetworkGraph(use_networkx=use_networkx)
        self._cache: Dict[str, Any] = {}

    def load_from_nodes_edges(self, nodes: List[Dict], edges: List[Dict]) -> None:
        """Load network from node and edge lists.

        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries
        """
        # Clear existing
        self.graph = NetworkGraph(use_networkx=self.graph._use_networkx)

        # Add nodes
        for node in nodes:
            node_id = node.get('id')
            if node_id:
                self.graph.add_node(node_id, **{
                    k: v for k, v in node.items() if k != 'id'
                })

        # Add edges
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            if source and target:
                self.graph.add_edge(
                    source, target,
                    weight=edge.get('weight', 1.0),
                    relationship=edge.get('relationship', 'friend'),
                    **{k: v for k, v in edge.items()
                       if k not in ['source', 'target', 'weight', 'relationship']}
                )

    def full_analysis(self) -> Dict[str, Any]:
        """Perform full network analysis.

        Returns:
            Dictionary with all analysis results
        """
        return {
            'centrality': self.graph.calculate_centrality(),
            'communities': self.graph.detect_communities(),
            'influence': self.graph.calculate_influence(),
            'trust': self.graph.calculate_trust(),
            'anomalies': self.graph.detect_anomalies(),
            'stats': self.graph.get_network_stats()
        }


def create_sample_network(size: int = 100, fraud_ring: bool = True) -> Tuple[List[Dict], List[Dict]]:
    """Create a sample social network for testing.

    Args:
        size: Number of nodes to create
        fraud_ring: Whether to include a synthetic fraud ring

    Returns:
        Tuple of (nodes, edges) lists
    """
    import uuid

    nodes = []
    edges = []

    node_types = ['individual', 'business', 'organization', 'influencer']
    relationships = ['friend', 'colleague', 'family', 'business']

    # Create nodes
    for i in range(size):
        node_type = random.choice(node_types)
        if i < 5:
            node_type = 'influencer'  # First 5 are influencers

        nodes.append({
            'id': f"entity_{i:04d}",
            'label': f"Entity {i}",
            'type': node_type,
            'created_at': datetime.now().isoformat()
        })

    # Create edges (small-world network structure)
    for i in range(size):
        # Each node connects to a few neighbors
        num_connections = random.randint(2, 8)
        for _ in range(num_connections):
            target = random.randint(0, size - 1)
            if target != i:
                edges.append({
                    'source': f"entity_{i:04d}",
                    'target': f"entity_{target:04d}",
                    'weight': random.uniform(0.5, 1.0),
                    'relationship': random.choice(relationships)
                })

    # Add fraud ring if requested
    if fraud_ring:
        ring_size = random.randint(5, 10)
        ring_start = size - ring_size

        # Create tight connections within ring
        for i in range(ring_start, size):
            for j in range(i + 1, size):
                edges.append({
                    'source': f"entity_{i:04d}",
                    'target': f"entity_{j:04d}",
                    'weight': 0.95,  # High weight (trust)
                    'relationship': 'business'
                })

        # Ring connects to one target (the victim)
        if ring_start > 0:
            target_id = random.randint(0, ring_start - 1)
            for i in range(ring_start, size):
                edges.append({
                    'source': f"entity_{i:04d}",
                    'target': f"entity_{target_id:04d}",
                    'weight': 0.8,
                    'relationship': 'business'
                })

    return nodes, edges
