#!/usr/bin/env python3
"""Build FAISS index with real training data."""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

import pandas as pd
import numpy as np
import faiss
import pickle
from sklearn.preprocessing import StandardScaler

def main():
    # Find data file
    possible_paths = [
        '../../../data/cs-training.csv',
        '../../data/cs-training.csv',
        '../data/cs-training.csv',
        'data/cs-training.csv',
        'D:\\GitHUB\\CredsCore\\data\\cs-training.csv',
    ]

    data_path = None
    for p in possible_paths:
        if os.path.exists(p):
            data_path = p
            break

    if not data_path:
        print("Error: Could not find cs-training.csv")
        return 1

    print(f"Loading data from {data_path}...")

    # Load data
    df = pd.read_csv(data_path)
    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)

    X = df.drop(['SeriousDlqin2yrs'], axis=1)
    y = df['SeriousDlqin2yrs']

    print(f'Loaded {len(X)} records with {X.shape[1]} features')
    print(f'Feature names: {X.columns.tolist()}')

    # Preprocess - handle NaN values
    scaler = StandardScaler()
    median_vals = X.median()
    X_clean = X.fillna(median_vals).replace([np.inf, -np.inf], np.nan).fillna(median_vals)
    X_scaled = scaler.fit_transform(X_clean).astype('float32')

    print(f'Scaled data shape: {X_scaled.shape}')
    print(f'Default rate: {y.mean():.2%}')

    # Build FAISS index using IVF for efficient search
    d = X_scaled.shape[1]
    nlist = min(100, max(10, len(X) // 1000))  # Adaptive cluster count

    print(f'Building FAISS IVF index: d={d}, nlist={nlist}...')

    quantizer = faiss.IndexFlatL2(d)
    index = faiss.IndexIVFFlat(quantizer, d, nlist)
    index.train(X_scaled)
    index.add(X_scaled)

    print(f'Built index with {index.ntotal} vectors')

    # Save
    save_dir = 'saved_models'
    os.makedirs(save_dir, exist_ok=True)

    index_path = os.path.join(save_dir, 'faiss_index.index')
    meta_path = os.path.join(save_dir, 'faiss_meta.pkl')

    faiss.write_index(index, index_path)
    with open(meta_path, 'wb') as f:
        pickle.dump({
            'scaler': scaler,
            'feature_names': X.columns.tolist(),
            'labels': y.values,
            'training_data': X_scaled
        }, f)

    print(f'Saved FAISS index to {save_dir}/')
    print(f'  - Index: {index_path}')
    print(f'  - Metadata: {meta_path}')

    # Test search
    print('\nTesting search with first record...')
    test_query = X_scaled[0:1]
    distances, indices = index.search(test_query, 5)
    print(f'Top 5 similar indices: {indices[0]}')
    print(f'Distances: {distances[0]}')

    return 0

if __name__ == "__main__":
    exit(main())
