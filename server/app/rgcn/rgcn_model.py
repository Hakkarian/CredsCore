"""
RGCN Model for Credit Risk Assessment.

Implements a Relational Graph Convolutional Network for semi-supervised
learning on the heterogeneous applicant graph.

Separation of concerns: This model generates NODE EMBEDDINGS only.
These embeddings become features for the downstream prediction model.
"""

import torch
import torch.nn.functional as F
from torch_geometric.nn import RGCNConv
from torch_geometric.data import HeteroData
from typing import Optional


class RGCNCreditModel(torch.nn.Module):
    """
    RGCN model for semi-supervised credit risk learning.
    
    Learns node embeddings that capture both individual features
    and relational patterns from the credit applicant graph.
    """

    def __init__(
        self,
        in_channels: int,
        hidden_channels: int = 64,
        out_channels: int = 32,
        num_relations: int = 3,
        num_bases: int = 2,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.dropout = dropout

        self.conv1 = RGCNConv(
            in_channels=in_channels,
            out_channels=hidden_channels,
            num_relations=num_relations,
            num_bases=num_bases,
        )

        self.conv2 = RGCNConv(
            in_channels=hidden_channels,
            out_channels=out_channels,
            num_relations=num_relations,
            num_bases=num_bases,
        )

        self.classifier = torch.nn.Linear(out_channels, 1)

    def forward(
        self,
        x: torch.Tensor,
        edge_index_dict: dict,
        edge_type_dict: dict,
    ) -> torch.Tensor:
        """
        Forward pass to get node embeddings and predictions.
        
        Args:
            x: Node features
            edge_index_dict: Edge indices by relation type
            edge_type_dict: Edge type mapping
            
        Returns:
            Node embeddings and predictions
        """
        hetero_edge_index = self._build_hetero_edge_index(edge_index_dict)
        edge_type = self._build_edge_type(edge_index_dict, edge_type_dict)

        x = self.conv1(x, hetero_edge_index, edge_type)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)

        x = self.conv2(x, hetero_edge_index, edge_type)
        embeddings = F.relu(x)

        out = self.classifier(embeddings).squeeze(-1)

        return embeddings, out

    def _build_hetero_edge_index(self, edge_index_dict: dict) -> torch.Tensor:
        """Combine all relation edge indices into single tensor."""
        all_edges = []
        for edge_index in edge_index_dict.values():
            if edge_index.shape[1] > 0:
                all_edges.append(edge_index)
        if not all_edges:
            return torch.empty((2, 0), dtype=torch.long, device=list(edge_index_dict.values())[0].device)
        return torch.cat(all_edges, dim=1)

    def _build_edge_type(
        self, edge_index_dict: dict, edge_type_dict: dict
    ) -> torch.Tensor:
        """Build edge type tensor for combined edge index."""
        all_types = []
        for i, (rel_type, edge_index) in enumerate(edge_index_dict.items()):
            if edge_index.shape[1] > 0:
                rel_id = edge_type_dict.get(rel_type, i)
                all_types.append(torch.full((edge_index.shape[1],), rel_id, dtype=torch.long))
        if not all_types:
            return torch.empty(0, dtype=torch.long)
        return torch.cat(all_types, dim=0)

    def get_embeddings(
        self,
        x: torch.Tensor,
        edge_index_dict: dict,
    ) -> torch.Tensor:
        """
        Get node embeddings without training signal.
        
        This is the FEATURE FACTORY method - it produces features
        that will be concatenated with original features for LightGBM.
        
        Args:
            x: Node features
            edge_index_dict: Edge indices by relation type
            
        Returns:
            Node embeddings (numpy-ready)
        """
        self.eval()
        with torch.no_grad():
            hetero_edge_index = self._build_hetero_edge_index(edge_index_dict)
            edge_type_dict = {k: i for i, k in enumerate(edge_index_dict.keys())}
            edge_type = self._build_edge_type(edge_index_dict, edge_type_dict)

            x = self.conv1(x, hetero_edge_index, edge_type)
            x = F.relu(x)
            x = self.conv2(x, hetero_edge_index, edge_type)
            embeddings = F.relu(x)

        return embeddings


def count_relations(data: HeteroData) -> int:
    """Count the number of relation types in the graph."""
    count = 0
    for edge_type in data.edge_types:
        if edge_type[0] == edge_type[2]:
            count += 1
    return count


def get_relation_keys(data: HeteroData) -> list:
    """Get list of relation type keys from HeteroData."""
    return [
        et for et in data.edge_types
        if et[0] == et[2]
    ]