import os
import sys
import pandas as pd
import numpy as np
import argparse

sys.path.append(os.path.dirname(__file__))

from app.faiss_index import FAISSCreditIndex
from app.batch_processor import BatchFraudProcessor


def build_snn_fraud_detector(data_path: str = "data/cs-training.csv", save_dir: str = "saved_models", k: int = 15, snn_threshold: int = 5, min_cluster_size: int = 3, eps: float = 0.6, run_scan: bool = True):
    os.makedirs(save_dir, exist_ok=True)
    
    print("Loading data...")
    df = pd.read_csv(data_path)
    if "Unnamed: 0" in df.columns:
        df = df.drop("Unnamed: 0", axis=1)
    
    target = "SeriousDlqin2yrs"
    feature_cols = [c for c in df.columns if c != target]
    features = df[feature_cols].values.astype(np.float64)
    labels = df[target].values
    
    median = np.nanmedian(features, axis=0)
    features = np.where(np.isnan(features) | np.isinf(features), median, features)
    
    print(f"Data: {features.shape[0]} applicants, {features.shape[1]} features")
    print(f"Default rate: {labels.mean():.2%}")
    
    print("\nBuilding FAISS index...")
    faiss_idx = FAISSCreditIndex()
    training_data = df[feature_cols].copy()
    training_labels = df[target].copy()
    faiss_idx.build_index(training_data, training_labels)
    faiss_idx.save_index(save_dir)
    print(f"FAISS index built: {faiss_idx.index.ntotal} vectors")
    
    if run_scan:
        print("\nRunning SNN fraud ring detection...")
        processor = BatchFraudProcessor(
            data_path=data_path,
            save_dir=save_dir,
        )
        processor.initialize()
        processor.snn_detector = processor.snn_detector.__class__(
            k=k,
            snn_threshold=snn_threshold,
            min_cluster_size=min_cluster_size,
            eps=eps,
        )
        
        result = processor.run_scan()
        
        if result.get("status") == "completed":
            print(f"\nScan completed in {result.get('scan_duration_seconds', 0):.1f}s")
            print(f"Total fraud rings detected: {result.get('total_rings_detected', 0)}")
            print(f"  High risk: {result.get('high_risk_rings', 0)}")
            print(f"  Medium risk: {result.get('medium_risk_rings', 0)}")
            print(f"  Low risk: {result.get('low_risk_rings', 0)}")
            print(f"Largest ring size: {result.get('largest_ring_size', 0)}")
            print(f"Average ring size: {result.get('avg_ring_size', 0):.1f}")
            
            for ring_data in result.get("rings", [])[:5]:
                print(f"\n  Ring: {ring_data['ring_id']} (risk: {ring_data['risk_level']})")
                print(f"    Members: {ring_data['member_count']}")
                print(f"    Avg risk score: {ring_data['avg_risk_score']:.3f}")
                print(f"    Cohesiveness: {ring_data['cohesiveness']:.3f}")
                for factor in ring_data.get("risk_factors", [])[:3]:
                    print(f"    - {factor}")
        else:
            print(f"Scan failed or was skipped: {result.get('message', 'Unknown error')}")
    
    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build SNN fraud detector")
    parser.add_argument("--data", default="data/cs-training.csv", help="Path to training data")
    parser.add_argument("--save-dir", default="saved_models", help="Directory to save models")
    parser.add_argument("--k", type=int, default=15, help="Number of nearest neighbors")
    parser.add_argument("--snn-threshold", type=int, default=5, help="SNN shared neighbor threshold")
    parser.add_argument("--min-cluster-size", type=int, default=3, help="Minimum cluster size")
    parser.add_argument("--eps", type=float, default=0.6, help="SNN similarity threshold")
    parser.add_argument("--no-scan", action="store_true", help="Skip fraud ring detection scan")
    args = parser.parse_args()
    
    build_snn_fraud_detector(
        data_path=args.data,
        save_dir=args.save_dir,
        k=args.k,
        snn_threshold=args.snn_threshold,
        min_cluster_size=args.min_cluster_size,
        eps=args.eps,
        run_scan=not args.no_scan,
    )