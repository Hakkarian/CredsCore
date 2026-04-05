"""
Build and train RGCN model for credit risk feature extraction.

This script:
1. Loads training data
2. Builds the heterogeneous graph
3. Trains the RGCN model (semi-supervised)
4. Saves the model and graph for feature factory use

Run this once to create the RGCN artifacts in saved_models/
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from app.rgcn.graph_builder import GraphBuilder
from app.rgcn.rgcn_model import RGCNCreditModel, get_relation_keys
from app.rgcn.trainer import RGCNTrainer
from app.rgcn.feature_factory import RGCNFeatureFactory


def build_rgcn(
    data_path: str = "data/cs-training.csv",
    save_dir: str = "app/saved_models",
    epochs: int = 100,
    embedding_dim: int = 32,
):
    """Build and train RGCN model."""

    print(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    if "Unnamed: 0" in df.columns:
        df = df.drop("Unnamed: 0", axis=1)

    feature_cols = [c for c in df.columns if c != "SeriousDlqin2yrs"]
    in_channels = len(feature_cols)
    print(f"Features: {in_channels}, Samples: {len(df)}")

    print("Building graph...")
    graph_builder = GraphBuilder(
        income_threshold=0.1,
        age_threshold=5,
        credit_similarity_threshold=0.3,
    )
    graph_data = graph_builder.build_graph(df, target_col="SeriousDlqin2yrs")

    relation_keys = get_relation_keys(graph_data)
    num_relations = len(relation_keys)
    print(f"Relations: {num_relations} - {[str(k) for k in relation_keys]}")

    print(f"Training RGCN (embed_dim={embedding_dim}, epochs={epochs})...")
    trainer = RGCNTrainer(
        in_channels=in_channels,
        hidden_channels=64,
        out_channels=embedding_dim,
        num_relations=num_relations,
        epochs=epochs,
        batch_size=2048,
    )
    trainer.build_model()

    history = trainer.train(graph_data, val_ratio=0.1, device="cpu")

    final_loss = history["loss"][-1]
    final_val_auc = history["val_auc"][-1]
    print(f"Training complete - Final Loss: {final_loss:.4f}, Val Acc: {final_val_auc:.4f}")

    os.makedirs(save_dir, exist_ok=True)
    trainer.save(save_dir, graph_builder=graph_builder, graph_data=graph_data)

    factory = RGCNFeatureFactory()
    factory.initialize(trainer.model, graph_builder, graph_data)
    factory.save(save_dir)

    print(f"\nRGCN artifacts saved to: {save_dir}")
    print(f"  - rgcn_checkpoint.pt (training state)")
    print(f"  - rgcn_model.pt (model weights)")
    print(f"  - rgcn_meta.pkl (graph + metadata)")

    return trainer, factory


if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "cs-training.csv")
    save_dir = os.path.join(os.path.dirname(__file__), "app", "saved_models")
    build_rgcn(data_path=data_path, save_dir=save_dir)