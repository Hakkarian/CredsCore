"""
Graph Builder for RGCN Feature Factory.

Constructs a heterogeneous graph from applicant data where:
- Nodes: Individual applicants
- Edges: Multiple relation types based on shared attributes
- Node Features: Credit risk features from the training data
- Node Labels: Default status (SeriousDlqin2yrs)
"""

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import HeteroData
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Optional


class GraphBuilder:
    """Builds heterogeneous graph for RGCN training and inference."""

    RELATION_TYPES = [
        "income_similarity",
        "age_proximity",
        "credit_profile_similarity",
    ]

    def __init__(
        self,
        income_threshold: float = 0.1,
        age_threshold: int = 5,
        credit_similarity_threshold: float = 0.3,
        random_seed: int = 42,
    ):
        self.income_threshold = income_threshold
        self.age_threshold = age_threshold
        self.credit_similarity_threshold = credit_similarity_threshold
        self.random_seed = random_seed
        self.rng = np.random.default_rng(random_seed)
        self.scaler = StandardScaler()
        self.feature_names = None
        self.node_features = None
        self.node_labels = None

    def build_graph(
        self, df: pd.DataFrame, target_col: str = "SeriousDlqin2yrs"
    ) -> HeteroData:
        """
        Build heterogeneous graph from applicant data.

        Args:
            df: DataFrame with applicant features and target
            target_col: Name of the target column

        Returns:
            PyTorch Geometric HeteroData object
        """
        feature_cols = [c for c in df.columns if c != target_col and c != "Unnamed: 0"]
        self.feature_names = feature_cols

        X = df[feature_cols].copy()

        median_vals = X.median()
        X = X.fillna(median_vals).replace([np.inf, -np.inf], np.nan).fillna(median_vals)

        X_scaled = self.scaler.fit_transform(X)
        self.node_features = torch.FloatTensor(X_scaled)
        self.node_labels = torch.FloatTensor(df[target_col].values)

        data = HeteroData()
        data["applicant"].x = self.node_features
        data["applicant"].y = self.node_labels

        for relation in self.RELATION_TYPES:
            edge_index = self._build_relation_edges(X, relation)
            if edge_index.shape[1] > 0:
                data["applicant", relation, "applicant"].edge_index = edge_index

        train_mask = torch.ones(len(df), dtype=torch.bool)
        data["applicant"].train_mask = train_mask

        return data

    def _build_relation_edges(self, X: pd.DataFrame, relation: str) -> torch.Tensor:
        """Build edge index for a specific relation type."""
        if relation == "income_similarity":
            return self._income_similarity_edges(X)
        elif relation == "age_proximity":
            return self._age_proximity_edges(X)
        elif relation == "credit_profile_similarity":
            return self._credit_profile_similarity_edges(X)
        return torch.empty((2, 0), dtype=torch.long)

    def _income_similarity_edges(self, X: pd.DataFrame) -> torch.Tensor:
        """Connect applicants with similar income levels using bucket approach for scalability."""
        if "MonthlyIncome" not in X.columns:
            return torch.empty((2, 0), dtype=torch.long)

        income = X["MonthlyIncome"].values
        n = len(income)

        if n > 10000:
            income_quantiles = pd.qcut(income, q=100, duplicates="drop")
            groups = income_quantiles.codes
        else:
            bucket_size = income.max() * self.income_threshold
            groups = (income / max(bucket_size, 1e-8)).astype(int)

        rows, cols = [], []
        unique_groups = np.unique(groups)
        for g in unique_groups:
            mask = groups == g
            indices = np.where(mask)[0]
            if len(indices) > 1:
                sample_size = min(len(indices), 50)
                sampled = self.rng.choice(indices, size=sample_size, replace=False)
                gi, gj = np.meshgrid(sampled, sampled)
                mask_diag = gi != gj
                rows.append(gi[mask_diag])
                cols.append(gj[mask_diag])

        if not rows:
            return torch.empty((2, 0), dtype=torch.long)

        return torch.tensor([np.concatenate(rows), np.concatenate(cols)], dtype=torch.long)

    def _age_proximity_edges(self, X: pd.DataFrame) -> torch.Tensor:
        """Connect applicants in similar age groups using bucket approach."""
        if "age" not in X.columns:
            return torch.empty((2, 0), dtype=torch.long)

        age = X["age"].values
        age_buckets = (age // self.age_threshold).astype(int)

        rows, cols = [], []
        unique_buckets = np.unique(age_buckets)
        for b in unique_buckets:
            mask = age_buckets == b
            indices = np.where(mask)[0]
            if len(indices) > 1:
                sample_size = min(len(indices), 50)
                sampled = self.rng.choice(indices, size=sample_size, replace=False)
                gi, gj = np.meshgrid(sampled, sampled)
                mask_diag = gi != gj
                rows.append(gi[mask_diag])
                cols.append(gj[mask_diag])

        for b in unique_buckets:
            lower_mask = age_buckets == b - 1
            upper_mask = age_buckets == b
            lower_idx = np.where(lower_mask)[0]
            upper_idx = np.where(upper_mask)[0]
            if len(lower_idx) > 0 and len(upper_idx) > 0:
                n_links = min(len(lower_idx), len(upper_idx), 20)
                lower_sample = self.rng.choice(lower_idx, size=n_links, replace=len(lower_idx) < n_links)
                upper_sample = self.rng.choice(upper_idx, size=n_links, replace=len(upper_idx) < n_links)
                rows.append(lower_sample)
                cols.append(upper_sample)

        if not rows:
            return torch.empty((2, 0), dtype=torch.long)

        return torch.tensor([np.concatenate(rows), np.concatenate(cols)], dtype=torch.long)

    def _credit_profile_similarity_edges(self, X: pd.DataFrame) -> torch.Tensor:
        """Connect applicants with similar credit profiles using k-NN approximation."""
        credit_cols = [
            "RevolvingUtilizationOfUnsecuredLines",
            "DebtRatio",
            "NumberOfTime30-59DaysPastDueNotWorse",
            "NumberOfTimes90DaysLate",
        ]
        available_cols = [c for c in credit_cols if c in X.columns]
        if not available_cols:
            return torch.empty((2, 0), dtype=torch.long)

        credit_data = X[available_cols].values
        credit_normalized = credit_data / (credit_data.max(axis=0) + 1e-8)

        n = len(credit_data)
        k = 5

        if n <= 10000:
            diff = np.abs(
                credit_normalized[:, np.newaxis, :] - credit_normalized[np.newaxis, :, :]
            ).mean(axis=2)
            mask = (diff < self.credit_similarity_threshold) & (diff > 0)
            rows, cols = np.where(mask)
        else:
            from sklearn.neighbors import NearestNeighbors
            nn = NearestNeighbors(n_neighbors=min(k + 1, n), metric="minkowski", p=2)
            nn.fit(credit_normalized)
            distances, indices = nn.kneighbors(credit_normalized)
            rows, cols = [], []
            for i in range(n):
                neighbors = indices[i][1:]
                close = neighbors[distances[i][1:] < self.credit_similarity_threshold]
                if len(close) > 0:
                    rows.extend([i] * len(close))
                    cols.extend(close)

        if not rows or len(rows) == 0:
            return torch.empty((2, 0), dtype=torch.long)

        return torch.tensor([np.array(rows), np.array(cols)], dtype=torch.long)

    def add_node_to_graph(self, node_features: np.ndarray) -> Tuple[HeteroData, int]:
        """
        Add a new node to the existing graph for inference.

        Args:
            node_features: Features for the new node

        Returns:
            Updated HeteroData and new node index
        """
        if self.node_features is None:
            raise ValueError("No graph built yet. Call build_graph first.")

        new_features = torch.FloatTensor(node_features.reshape(1, -1))
        self.node_features = torch.cat([self.node_features, new_features], dim=0)

        data = HeteroData()
        data["applicant"].x = self.node_features

        if self.node_labels is not None:
            new_label = torch.zeros(1, dtype=torch.float)
            data["applicant"].y = torch.cat([self.node_labels, new_label], dim=0)

        return data, len(self.node_features) - 1