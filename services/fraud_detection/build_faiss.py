import os
import sys
import pandas as pd
from pathlib import Path

# Add the current directory to Python path to allow imports from sibling directories
sys.path.insert(0, str(Path(__file__).parent.parent))

from .app.faiss_index import build_and_save_faiss_index


def main():
    """Build and save FAISS index for fraud detection."""
    data_path = "data/cs-training.csv"
    save_dir = "saved_models"
    
    print(f"Building FAISS index from {data_path}...")
    
    # Ensure data directory exists
    if not os.path.exists(data_path):
        print(f"Error: Data file {data_path} not found.")
        return 1
    
    try:
        # Build and save FAISS index
        faiss_index = build_and_save_faiss_index(data_path=data_path, save_dir=save_dir)
        print(f"FAISS index built successfully and saved to {save_dir}")
        return 0
    except Exception as e:
        print(f"Error building FAISS index: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)