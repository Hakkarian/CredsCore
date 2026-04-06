import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, field
import os
import pickle


@dataclass
class FraudRingMember:
    index: int
    risk_score: float
    anomaly_score: float
    shared_neighbor_count: int


@dataclass
class FraudRing:
    ring_id: str
    members: List[FraudRingMember]
    avg_risk_score: float
    avg_anomaly_score: float
    cohesiveness: float
    risk_factors: List[str]


@dataclass
class SNNStats:
    total_applicants: int
    total_rings_detected: int
    high_risk_rings: int
    medium_risk_rings: int
    low_risk_rings: int
    largest_ring_size: int
    avg_ring_size: float
    scan_timestamp: str


class SNNFraudDetector:
    """Shared Nearest Neighbors detector for finding fraud rings in the customer graph."""

    def __init__(
        self,
        k: int = 15,
        snn_threshold: int = 5,
        min_cluster_size: int = 3,
        eps: float = 0.6,
    ):
        self.k = k
        self.snn_threshold = snn_threshold
        self.min_cluster_size = min_cluster_size
        self.eps = eps
        self.snn_matrix = None
        self.fraud_rings: List[FraudRing] = []
        self.cluster_labels = None
        self.applicant_features = None
        self.applicant_labels = None

    def build_snn_graph(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        faiss_index=None,
    ) -> np.ndarray:
        """Build the Shared Nearest Neighbor similarity matrix."""
        self.applicant_features = features
        self.applicant_labels = labels
        n = len(features)

        if faiss_index and faiss_index.index_trained:
            all_distances = []
            all_indices = []
            batch_size = 500
            for start in range(0, n, batch_size):
                end = min(start + batch_size, n)
                batch = features[start:end].astype("float32")
                dists, idxs = faiss_index.search_similar(batch, k=self.k)
                all_distances.append(dists)
                all_indices.append(idxs)

            all_distances = np.vstack(all_distances)
            all_indices = np.vstack(all_indices)
        else:
            from sklearn.neighbors import NearestNeighbors
            nn = NearestNeighbors(n_neighbors=self.k, metric="l2", algorithm="brute")
            nn.fit(features)
            all_distances, all_indices = nn.kneighbors(features)

        knn_sets = []
        for i in range(n):
            knn_sets.append(set(all_indices[i]))

        snn = np.zeros((n, n), dtype=np.int32)
        for i in range(n):
            for j_idx in knn_sets[i]:
                if j_idx > i:
                    shared = len(knn_sets[i] & knn_sets[j_idx])
                    if shared >= self.snn_threshold:
                        snn[i, j_idx] = shared
                        snn[j_idx, i] = shared

        self.snn_matrix = snn
        return snn

    def detect_fraud_rings(
        self, features: Optional[np.ndarray] = None, labels: Optional[np.ndarray] = None, faiss_index=None
    ) -> List[FraudRing]:
        """Detect fraud rings using SNN-based clustering."""
        if features is not None:
            self.build_snn_graph(features, labels, faiss_index)

        if self.snn_matrix is None:
            raise ValueError("SNN graph not built. Call build_snn_graph first.")

        n = self.snn_matrix.shape[0]
        self.cluster_labels = np.full(n, -1, dtype=np.int32)
        cluster_id = 0
        visited = set()

        snn_normalized = self.snn_matrix / (self.k + 1e-8)

        for i in range(n):
            if i in visited:
                continue

            neighbors = self._get_eps_neighbors(snn_normalized, i)
            if len(neighbors) < self.min_cluster_size:
                continue

            cluster_members = {i}
            queue = list(neighbors)
            queue_set = set(neighbors)

            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue

                visited.add(current)
                cluster_members.add(current)

                current_neighbors = self._get_eps_neighbors(snn_normalized, current)
                if len(current_neighbors) >= self.min_cluster_size:
                    for nb in current_neighbors:
                        if nb not in visited and nb not in queue_set:
                            queue.append(nb)
                            queue_set.add(nb)

            if len(cluster_members) >= self.min_cluster_size:
                for idx in cluster_members:
                    self.cluster_labels[idx] = cluster_id

                ring = self._assess_ring_risk(cluster_members, cluster_id)
                if ring:
                    self.fraud_rings.append(ring)

                cluster_id += 1

        return self.fraud_rings

    def _get_eps_neighbors(self, snn_normalized: np.ndarray, node: int) -> set:
        similarities = snn_normalized[node]
        return set(np.where(similarities >= self.eps)[0]) - {node}

    def _assess_ring_risk(self, members: set, ring_id: int) -> Optional[FraudRing]:
        if self.applicant_labels is None or self.applicant_features is None:
            return None

        member_indices = list(members)
        labels = self.applicant_labels[member_indices]
        features = self.applicant_features[member_indices]

        default_rate = float(labels.mean())
        avg_anomaly = self._compute_cluster_anomaly(features)

        cohesiveness = self._compute_cohesiveness(member_indices)

        risk_score = 0.4 * default_rate + 0.3 * min(1.0, avg_anomaly / 3.0) + 0.3 * cohesiveness

        ring_members = []
        for i, idx in enumerate(member_indices):
            ring_members.append(
                FraudRingMember(
                    index=int(idx),
                    risk_score=float(labels[i]),
                    anomaly_score=float(self._point_anomaly(features[i], features)),
                    shared_neighbor_count=int(self._count_internal_neighbors(idx, member_indices)),
                )
            )

        risk_factors = self._identify_risk_factors(
            default_rate, avg_anomaly, cohesiveness, ring_members
        )

        return FraudRing(
            ring_id=f"fraud_ring_{ring_id}",
            members=ring_members,
            avg_risk_score=float(risk_score),
            avg_anomaly_score=float(avg_anomaly),
            cohesiveness=float(cohesiveness),
            risk_factors=risk_factors,
        )

    def _compute_cluster_anomaly(self, features: np.ndarray) -> float:
        centroid = features.mean(axis=0)
        distances = np.linalg.norm(features - centroid, axis=1)
        return float(distances.mean())

    def _point_anomaly(self, point: np.ndarray, cluster_features: np.ndarray) -> float:
        centroid = cluster_features.mean(axis=0)
        std = cluster_features.std(axis=0) + 1e-8
        return float(np.mean(np.abs((point - centroid) / std)))

    def _compute_cohesiveness(self, member_indices: List[int]) -> float:
        sub_matrix = self.snn_matrix[np.ix_(member_indices, member_indices)]
        np.fill_diagonal(sub_matrix, 0)
        max_possible = self.k * len(member_indices)
        actual = sub_matrix.sum()
        return float(actual / max_possible) if max_possible > 0 else 0.0

    def _count_internal_neighbors(self, idx: int, member_indices: List[int]) -> int:
        member_set = set(member_indices)
        neighbors = set(np.where(self.snn_matrix[idx] > 0)[0])
        return len(neighbors & member_set)

    def _identify_risk_factors(
        self,
        default_rate: float,
        avg_anomaly: float,
        cohesiveness: float,
        members: List[FraudRingMember],
    ) -> List[str]:
        factors = []
        if default_rate > 0.5:
            factors.append(f"High default rate in group ({default_rate:.0%})")
        if avg_anomaly > 2.0:
            factors.append(f"Group members have anomalous profiles (avg score: {avg_anomaly:.1f})")
        if cohesiveness > 0.7:
            factors.append(f"Tightly connected group (cohesiveness: {cohesiveness:.2f}) - possible coordinated fraud")
        if len(members) >= 5:
            factors.append(f"Large group detected ({len(members)} members)")

        high_anomaly_count = sum(1 for m in members if m.anomaly_score > 2.0)
        if high_anomaly_count >= 3:
            factors.append(f"Multiple anomalous members ({high_anomaly_count})")

        return factors if factors else ["Group detected but no strong fraud signals"]

    def get_stats(self, scan_timestamp: str = "") -> Dict[str, Any]:
        """Return statistics about detected fraud rings."""
        if not self.fraud_rings:
            return {
                "total_applicants": int(len(self.cluster_labels)) if self.cluster_labels is not None else 0,
                "total_rings_detected": 0,
                "high_risk_rings": 0,
                "medium_risk_rings": 0,
                "low_risk_rings": 0,
                "largest_ring_size": 0,
                "avg_ring_size": 0,
                "rings": [],
            }

        sizes = [len(r.members) for r in self.fraud_rings]
        high_risk = sum(1 for r in self.fraud_rings if r.avg_risk_score > 0.6)
        medium_risk = sum(1 for r in self.fraud_rings if 0.35 < r.avg_risk_score <= 0.6)
        low_risk = len(self.fraud_rings) - high_risk - medium_risk

        rings_data = []
        for ring in self.fraud_rings:
            rings_data.append(
                {
                    "ring_id": ring.ring_id,
                    "member_count": len(ring.members),
                    "avg_risk_score": round(ring.avg_risk_score, 4),
                    "avg_anomaly_score": round(ring.avg_anomaly_score, 4),
                    "cohesiveness": round(ring.cohesiveness, 4),
                    "risk_level": "high" if ring.avg_risk_score > 0.6 else "medium" if ring.avg_risk_score > 0.35 else "low",
                    "risk_factors": ring.risk_factors,
                    "top_members": sorted(
                        [
                            {
                                "index": m.index,
                                "risk_score": round(m.risk_score, 4),
                                "anomaly_score": round(m.anomaly_score, 4),
                                "shared_neighbors": m.shared_neighbor_count,
                            }
                            for m in ring.members
                        ],
                        key=lambda x: x["anomaly_score"],
                        reverse=True,
                    )[:10],
                }
            )

        return {
            "total_applicants": int(len(self.cluster_labels)) if self.cluster_labels is not None else 0,
            "total_rings_detected": len(self.fraud_rings),
            "high_risk_rings": high_risk,
            "medium_risk_rings": medium_risk,
            "low_risk_rings": low_risk,
            "largest_ring_size": max(sizes),
            "avg_ring_size": float(np.mean(sizes)),
            "rings": rings_data,
            "scan_timestamp": scan_timestamp,
        }

    def save_state(self, save_dir: str = "saved_models") -> None:
        os.makedirs(save_dir, exist_ok=True)
        state = {
            "snn_matrix": self.snn_matrix,
            "fraud_rings": self.fraud_rings,
            "cluster_labels": self.cluster_labels,
            "applicant_features": self.applicant_features,
            "applicant_labels": self.applicant_labels,
            "k": self.k,
            "snn_threshold": self.snn_threshold,
            "min_cluster_size": self.min_cluster_size,
            "eps": self.eps,
        }
        with open(os.path.join(save_dir, "snn_fraud_detector.pkl"), "wb") as f:
            pickle.dump(state, f)

    def load_state(self, save_dir: str = "saved_models") -> bool:
        path = os.path.join(save_dir, "snn_fraud_detector.pkl")
        if not os.path.exists(path):
            return False
        with open(path, "rb") as f:
            state = pickle.load(f)
        self.snn_matrix = state["snn_matrix"]
        self.fraud_rings = state["fraud_rings"]
        self.cluster_labels = state["cluster_labels"]
        self.applicant_features = state["applicant_features"]
        self.applicant_labels = state["applicant_labels"]
        self.k = state["k"]
        self.snn_threshold = state["snn_threshold"]
        self.min_cluster_size = state["min_cluster_size"]
        self.eps = state["eps"]
        return True

    def get_applicant_rings(self, applicant_index: int) -> List[Dict[str, Any]]:
        """Find all fraud rings that contain a specific applicant."""
        result = []
        for ring in self.fraud_rings:
            for member in ring.members:
                if member.index == applicant_index:
                    result.append(
                        {
                            "ring_id": ring.ring_id,
                            "risk_level": "high" if ring.avg_risk_score > 0.6 else "medium" if ring.avg_risk_score > 0.35 else "low",
                            "avg_risk_score": round(ring.avg_risk_score, 4),
                            "member_count": len(ring.members),
                            "risk_factors": ring.risk_factors,
                        }
                    )
                    break
        return result