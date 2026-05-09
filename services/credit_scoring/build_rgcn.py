import os
import sys
import pandas as pd
from pathlib import Path
import torch
from torch_geometric.data import HeteroData
from torch_geometric.loader import NeighborLoader

# Add the current directory to Python path to allow imports from sibling directories
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.credit_scoring.app.rgcn.graph_builder import build_hetero_graph
from services.credit_scoring.app.rgcn.trainer import RGCNTrainer


def main():
    """Build and save RGCN model for credit scoring."""
    data_path = "data/cs-training.csv"
    save_dir = "saved_models"
    
    print(f"Building RGCN model from {data_path}...")
    
    # Ensure data directory exists
    if not os.path.exists(data_path):
        print(f"Error: Data file {data_path} not found.")
        return 1
    
    try:
        # Load data
        df = pd.read_csv(data_path)
        if "Unnamed: 0" in df.columns:
            df = df.drop("Unnamed: 0", axis=1)
        
        # Build hetero graph
        print("Building hetero graph...")
        graph_data = build_hetero_graph(df)
        
        # Initialize trainer
        print("Initializing RGCN trainer...")
        trainer = RGCNTrainer(
            in_channels=graph_data["applicant"].x.size(1),
            hidden_channels=64,
            out_channels=32,
            num_relations=len(graph_data.edge_types),
            epochs=50,
        )
        
        # Train model
        print("Training RGCN model...")
        history = trainer.train(graph_data, val_ratio=0.1, device="cpu")
        
        # Save model
        print(f"Saving RGCN model to {save_dir}...")
        trainer.save(save_dir, graph_builder=None, graph_data=graph_data)
        
        print(f"RGCN model built successfully and saved to {save_dir}")
        return 0
    except Exception as e:
        print(f"Error building RGCN model: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)