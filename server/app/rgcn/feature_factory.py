"""
RGCN Feature Factory - Extracts graph-based features for credit risk prediction.

This is the core integration layer that:
1. Takes applicant data as input
2. Uses the trained RGCN model to generate embeddings
3. Extracts graph-based features
4. Returns augmented feature vectors for the downstream LightGBM model

Separation of concerns:
- This module ONLY generates features
- It does NOT make predictions or decisions
- Features are consumed by LightGBM (which predicts risk)
- Policy engine remains unchanged
"""

import numpy as np
import pandas as pd
import torch
import joblib
import os
from typing import Dict, Any, Optional, Tuple
from torch_geometric.data import HeteroData

from .graph_builder import GraphBuilder
from .rgcn_model import RGCNCreditModel, get_relation_keys


class RGCNFeatureFactory:
    """
    Feature factory that extracts RGCN-based features for credit applicants.
    
    This augments traditional credit features with graph-based intelligence:
    - Node embeddings capture relational patterns
    - Neighborhood statistics (mean/default risk of similar applicants)
    - Graph centrality measures
    
    These features are concatenated with original features and passed to LightGBM.
    """

    def __init__(self):
        self.model: Optional[RGCNCreditModel] = None
        self.graph_builder: Optional[GraphBuilder] = None
        self.graph_data: Optional[HeteroData] = None
        self.feature_names: Optional[list] = None
        self.embedding_dim: int = 32
        self.is_loaded = False

    def initialize(
        self,
        model: RGCNCreditModel,
        graph_builder: GraphBuilder,
        graph_data: HeteroData,
    ):
        """Initialize with trained model and pre-built graph."""
        self.model = model
        self.graph_builder = graph_builder
        self.graph_data = graph_data
        self.feature_names = graph_builder.feature_names
        self.is_loaded = True

    def extract_features(
        self, applicant_data: pd.DataFrame
    ) -> Tuple[np.ndarray, list]:
        """
        Extract RGCN-augmented features for one or more applicants.
        
        Args:
            applicant_data: DataFrame with applicant features
            
        Returns:
            Tuple of (augmented_features, feature_names)
            - augmented_features: Original features + RGCN embeddings + graph stats
            - feature_names: Names of all features (original + rgcn_*)
        """
        if not self.is_loaded:
            raise ValueError("Feature factory not initialized. Call load() first.")

        processed = self._prepare_features(applicant_data)
        embeddings = self._get_embeddings(processed)
        graph_stats = self._compute_graph_statistics(processed)

        original_features = processed.values
        combined = np.hstack([original_features, embeddings, graph_stats])

        rgcn_feature_names = self._build_feature_names()
        all_feature_names = list(self.feature_names) + rgcn_feature_names

        return combined, all_feature_names

    def get_embedding_only(self, applicant_data: pd.DataFrame) -> np.ndarray:
        """Get just the RGCN embeddings without other features."""
        if not self.is_loaded:
            raise ValueError("Feature factory not initialized.")

        processed = self._prepare_features(applicant_data)
        return self._get_embeddings(processed)

    def _prepare_features(self, applicant_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare applicant features for graph integration."""
        if self.graph_builder.scaler is not None:
            if isinstance(applicant_data, pd.DataFrame):
                feature_cols = [
                    c
                    for c in applicant_data.columns
                    if c in self.feature_names
                ]
                df = applicant_data[feature_cols].copy()
                median_vals = df.median()
                df = df.fillna(median_vals).replace([np.inf, -np.inf], np.nan).fillna(median_vals)
                scaled = self.graph_builder.scaler.transform(df)
                return pd.DataFrame(scaled, columns=feature_cols)
        return applicant_data

    def _get_embeddings(self, processed_data: pd.DataFrame) -> np.ndarray:
        """Run RGCN inference to get node embeddings."""
        self.model.eval()
        x = torch.FloatTensor(processed_data.values)

        edge_index_dict = {}
        relation_keys = get_relation_keys(self.graph_data)
        for rel_key in relation_keys:
            edge_index_dict[str(rel_key)] = self.graph_data[rel_key].edge_index

        with torch.no_grad():
            hetero_edge_index = self.model._build_hetero_edge_index(edge_index_dict)
            edge_type_dict = {k: i for i, k in enumerate(edge_index_dict.keys())}
            edge_type = self.model._build_edge_type(edge_index_dict, edge_type_dict)

            x_full = self.graph_data["applicant"].x
            combined_x = torch.cat([x_full, x], dim=0)

            h = self.model.conv1(combined_x, hetero_edge_index, edge_type)
            h = torch.relu(h)
            h = self.model.conv2(h, hetero_edge_index, edge_type)
            h = torch.relu(h)

            new_node_indices = range(len(x_full), len(combined_x))
            embeddings = h[list(new_node_indices)]

        return embeddings.numpy()

    def _compute_graph_statistics(self, processed_data: pd.DataFrame) -> np.ndarray:
        """Compute graph-based statistics for new applicants."""
        stats = []
        for _, row in processed_data.iterrows():
            node_similarities = self._compute_neighbor_similarity(row)
            stats.append(node_similarities)
        return np.array(stats)

    def _compute_neighbor_similarity(self, node_features: pd.Series) -> np.ndarray:
        """Compute similarity of a new node to existing graph nodes."""
        x_full = self.graph_data["applicant"].x.numpy()
        node_vec = node_features.values.reshape(1, -1)

        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(node_vec, x_full).flatten()

        return np.array(
            [
                float(similarities.mean()),
                float(similarities.max()),
                float(similarities.min()),
                float(similarities.std()),
            ]
        )

    def _build_feature_names(self) -> list:
        """Build names for RGCN-augmented features."""
        names = []
        for i in range(self.embedding_dim):
            names.append(f"rgcn_embedding_{i}")
        names.extend(
            [
                "rgcn_neighbor_similarity_mean",
                "rgcn_neighbor_similarity_max",
                "rgcn_neighbor_similarity_min",
                "rgcn_neighbor_similarity_std",
            ]
        )
        return names

    def save(self, save_dir: str):
        """Save the feature factory state."""
        os.makedirs(save_dir, exist_ok=True)
        torch.save(
            self.model.state_dict(),
            os.path.join(save_dir, "rgcn_model.pt"),
        )
        joblib.dump(
            {
                "graph_builder": self.graph_builder,
                "graph_data": self.graph_data,
                "feature_names": self.feature_names,
                "embedding_dim": self.embedding_dim,
            },
            os.path.join(save_dir, "rgcn_meta.pkl"),
        )

    def load(self, save_dir: str):
        """Load the feature factory state."""
        meta = joblib.load(os.path.join(save_dir, "rgcn_meta.pkl"))
        self.graph_builder = meta["graph_builder"]
        self.graph_data = meta["graph_data"]
        self.feature_names = meta["feature_names"]
        self.embedding_dim = meta["embedding_dim"]

        model_path = os.path.join(save_dir, "rgcn_model.pt")
        in_channels = len(self.feature_names)

        relation_keys = get_relation_keys(self.graph_data)
        num_relations = len(relation_keys) if relation_keys else 3

        self.model = RGCNCreditModel(
            in_channels=in_channels,
            hidden_channels=64,
            out_channels=self.embedding_dim,
            num_relations=num_relations,
            num_bases=2,
        )
        self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
        self.model.eval()
        self.is_loaded = True