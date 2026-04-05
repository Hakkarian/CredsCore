"""
RGCN Training Pipeline for Credit Risk Assessment.

Trains the RGCN model in a semi-supervised manner using:
- Labeled applicants (SeriousDlqin2yrs target)
- Graph structure (relational patterns between applicants)

The trained model generates embeddings that augment LightGBM features.
"""

import torch
import torch.nn.functional as F
from torch_geometric.data import HeteroData
from torch_geometric.loader import NeighborLoader
import numpy as np
from typing import Optional, Dict, Any
import os

from .rgcn_model import RGCNCreditModel, get_relation_keys


class RGCNTrainer:
    """
    Trains RGCN model for semi-supervised credit risk learning.
    
    Training approach:
    1. Build graph from applicant data
    2. Train RGCN with BCE loss on labeled nodes
    3. Save trained model + graph for feature extraction
    """

    def __init__(
        self,
        in_channels: int,
        hidden_channels: int = 64,
        out_channels: int = 32,
        num_relations: int = 3,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-5,
        dropout: float = 0.3,
        epochs: int = 100,
        batch_size: int = 1024,
    ):
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels
        self.num_relations = num_relations
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.dropout = dropout
        self.epochs = epochs
        self.batch_size = batch_size

        self.model: Optional[RGCNCreditModel] = None
        self.optimizer = None
        self.training_history: Dict[str, list] = {"loss": [], "val_loss": [], "val_auc": []}

    def build_model(self) -> RGCNCreditModel:
        """Initialize the RGCN model."""
        self.model = RGCNCreditModel(
            in_channels=self.in_channels,
            hidden_channels=self.hidden_channels,
            out_channels=self.out_channels,
            num_relations=self.num_relations,
            num_bases=2,
            dropout=self.dropout,
        )
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay,
        )
        return self.model

    def train(
        self,
        data: HeteroData,
        val_ratio: float = 0.1,
        device: str = "cpu",
    ) -> Dict[str, list]:
        """
        Train the RGCN model.
        
        Args:
            data: HeteroData graph with node features and labels
            val_ratio: Fraction of nodes for validation
            device: Computation device
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()

        self.model = self.model.to(device)
        x = data["applicant"].x.to(device)
        y = data["applicant"].y.to(device)

        edge_index_dict = {}
        for rel_key in get_relation_keys(data):
            edge_index_dict[str(rel_key)] = data[rel_key].edge_index.to(device)

        edge_type_dict = {k: i for i, k in enumerate(edge_index_dict.keys())}

        num_nodes = x.size(0)
        val_size = int(num_nodes * val_ratio)
        indices = torch.randperm(num_nodes)
        train_idx = indices[val_size:]
        val_idx = indices[:val_size]

        best_val_loss = float("inf")
        patience = 10
        patience_counter = 0

        for epoch in range(self.epochs):
            self.model.train()
            self.optimizer.zero_grad()

            _, out = self.model(x, edge_index_dict, edge_type_dict)

            train_out = out[train_idx]
            train_y = y[train_idx]

            loss = F.binary_cross_entropy_with_logits(train_out, train_y)
            loss.backward()
            self.optimizer.step()

            self.model.eval()
            with torch.no_grad():
                _, val_out = self.model(x, edge_index_dict, edge_type_dict)
                val_loss = F.binary_cross_entropy_with_logits(
                    val_out[val_idx], y[val_idx]
                )

                val_pred = torch.sigmoid(val_out[val_idx])
                val_pred_binary = (val_pred > 0.5).float()
                val_correct = (val_pred_binary == y[val_idx]).sum().item()
                val_auc = val_correct / len(y[val_idx])

            self.training_history["loss"].append(loss.item())
            self.training_history["val_loss"].append(val_loss.item())
            self.training_history["val_auc"].append(val_auc)

            if (epoch + 1) % 10 == 0:
                print(
                    f"Epoch {epoch+1}/{self.epochs} - "
                    f"Loss: {loss.item():.4f} - "
                    f"Val Loss: {val_loss.item():.4f} - "
                    f"Val Acc: {val_auc:.4f}"
                )

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch+1}")
                    break

        return self.training_history

    def get_embeddings(self, data: HeteroData, device: str = "cpu") -> np.ndarray:
        """Get node embeddings after training."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        self.model.eval()
        x = data["applicant"].x.to(device)

        edge_index_dict = {}
        for rel_key in get_relation_keys(data):
            edge_index_dict[str(rel_key)] = data[rel_key].edge_index.to(device)

        with torch.no_grad():
            embeddings = self.model.get_embeddings(x, edge_index_dict)

        return embeddings.cpu().numpy()

    def save(self, save_dir: str, graph_builder=None, graph_data=None):
        """Save trained model and metadata."""
        os.makedirs(save_dir, exist_ok=True)

        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "in_channels": self.in_channels,
                "hidden_channels": self.hidden_channels,
                "out_channels": self.out_channels,
                "num_relations": self.num_relations,
                "training_history": self.training_history,
            },
            os.path.join(save_dir, "rgcn_checkpoint.pt"),
        )

        from .feature_factory import RGCNFeatureFactory

        factory = RGCNFeatureFactory()
        factory.initialize(self.model, graph_builder, graph_data)
        factory.save(save_dir)

        print(f"RGCN model saved to {save_dir}")