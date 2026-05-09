"""Build and save SNN fraud detector from training data.

Usage:
    python build_snn.py [--data-path PATH] [--save-dir DIR]
"""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from app.snn_fraud_detector import SNNFraudDetector


def find_data_path() -> str:
    """Find the training data CSV file."""
    candidates = [
        os.path.join(Path(__file__).parent, "data", "cs-training.csv"),
        os.path.join(Path(__file__).parent.parent.parent, "data", "cs-training.csv"),
        "data/cs-training.csv",
    ]
    for path in candidates:
        if os.path.exists(path):
            return os.path.abspath(path)
    return candidates[0]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build SNN fraud detector")
    parser.add_argument("--data-path", type=str, default=None, help="Path to cs-training.csv")
    parser.add_argument("--save-dir", type=str, default=None, help="Directory to save model")
    parser.add_argument("--max-sample", type=int, default=5000, help="Max sample size for SNN graph")
    args = parser.parse_args()

    data_path = args.data_path or find_data_path()
    save_dir = args.save_dir or os.path.join(Path(__file__).parent, "saved_models")

    print(f"Building SNN fraud detector from {data_path}...")

    if not os.path.exists(data_path):
        print(f"Error: Data file {data_path} not found.")
        print(f"Generate synthetic data first: python -m generate_fraud_data")
        return 1

    try:
        df = pd.read_csv(data_path)
        if "Unnamed: 0" in df.columns:
            df = df.drop("Unnamed: 0", axis=1)

        X = df.drop(["SeriousDlqin2yrs"], axis=1).values.astype(np.float64)
        y = df["SeriousDlqin2yrs"].values

        # Handle NaN
        median = np.nanmedian(X, axis=0)
        X = np.where(np.isnan(X) | np.isinf(X), median, X)

        snn_detector = SNNFraudDetector(
            k=15,
            snn_threshold=5,
            min_cluster_size=3,
            eps=0.6,
            max_sample_size=args.max_sample,
        )

        print("Building SNN graph...")
        snn_detector.build_snn_graph(X, y)

        print("Detecting fraud rings...")
        rings = snn_detector.detect_fraud_rings()
        print(f"Detected {len(rings)} fraud rings")

        print(f"Saving SNN fraud detector to {save_dir}...")
        snn_detector.save_state(save_dir)

        stats = snn_detector.get_stats()
        print(f"Summary: {stats['total_rings_detected']} rings "
              f"({stats['high_risk_rings']} high, {stats['medium_risk_rings']} medium, {stats['low_risk_rings']} low)")
        return 0
    except Exception as e:
        print(f"Error building SNN fraud detector: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
