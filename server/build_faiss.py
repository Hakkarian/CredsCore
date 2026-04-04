"""
Standalone script to build FAISS index from training data.
Run this once to create the index files.
"""
import sys
import os

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.faiss_index import build_and_save_faiss_index

if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), 'app', 'data', 'cs-training.csv')
    save_dir = os.path.join(os.path.dirname(__file__), 'app', 'saved_models')
    
    print(f"Building FAISS index from: {data_path}")
    print(f"Saving to: {save_dir}")
    
    faiss_index = build_and_save_faiss_index(data_path, save_dir)
    
    print(f"\nFAISS index built successfully!")
    print(f"Index size: {faiss_index.index.ntotal} vectors")
    print(f"Features: {len(faiss_index.feature_names)}")