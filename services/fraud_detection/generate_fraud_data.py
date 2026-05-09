"""Generate synthetic credit data with planted fraud rings for SNN detection.

Uses the statistical sampling approach (same as the synthetic-data service's
SimpleSyntheticEngine) to generate realistic credit application data, then
plants fraud rings by creating clusters of similar high-risk applicants.

This ensures the SNN fraud detector has meaningful structure to discover.
"""
import numpy as np
import pandas as pd
import os
import sys
from pathlib import Path


FEATURE_NAMES = [
    "RevolvingUtilizationOfUnsecuredLines",
    "age",
    "NumberOfTime30_59DaysPastDueNotWorse",
    "DebtRatio",
    "MonthlyIncome",
    "NumberOfOpenCreditLinesAndLoans",
    "NumberOfTimes90DaysLate",
    "NumberRealEstateLoansOrLines",
    "NumberOfTime60_89DaysPastDueNotWorse",
    "NumberOfDependents",
]


def generate_base_records(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Generate normal credit application records using statistical distributions."""
    data = {
        "RevolvingUtilizationOfUnsecuredLines": rng.beta(2, 5, n).clip(0, 1),
        "age": rng.integers(18, 65, n).astype(float),
        "NumberOfTime30_59DaysPastDueNotWorse": rng.poisson(0.5, n).clip(0, 10).astype(float),
        "DebtRatio": rng.gamma(2, 0.3, n).clip(0, 2),
        "MonthlyIncome": rng.lognormal(8, 0.5, n).clip(1000, 50000),
        "NumberOfOpenCreditLinesAndLoans": rng.poisson(8, n).clip(0, 30).astype(float),
        "NumberOfTimes90DaysLate": rng.poisson(0.1, n).clip(0, 10).astype(float),
        "NumberRealEstateLoansOrLines": rng.poisson(1, n).clip(0, 10).astype(float),
        "NumberOfTime60_89DaysPastDueNotWorse": rng.poisson(0.2, n).clip(0, 10).astype(float),
        "NumberOfDependents": rng.poisson(1, n).clip(0, 10).astype(float),
    }
    return pd.DataFrame(data)


def plant_fraud_rings(
    df: pd.DataFrame,
    labels: np.ndarray,
    n_rings: int = 5,
    ring_size_range: tuple = (4, 12),
    rng: np.random.Generator = None,
) -> tuple:
    """Plant fraud rings by modifying a subset of records to form tight clusters.

    Each fraud ring is created by picking a random "seed" applicant profile,
    then creating slight variations around it with high-risk features.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    n = len(df)
    features = df.values.copy()

    ring_start = 0
    rings_planted = 0

    for ring_idx in range(n_rings):
        ring_size = rng.integers(ring_size_range[0], ring_size_range[1] + 1)
        if ring_start + ring_size > n:
            break

        # Create a fraud ring template - high risk profile
        template = np.array([
            rng.uniform(0.7, 1.0),    # RevolvingUtilization - very high
            rng.integers(22, 35),      # age - younger
            rng.integers(3, 8),        # NumberOfTime30_59DaysPastDueNotWorse - many late payments
            rng.uniform(0.6, 1.5),     # DebtRatio - high
            rng.integers(1000, 4000),  # MonthlyIncome - low
            rng.integers(2, 8),        # NumberOfOpenCreditLinesAndLoans - few
            rng.integers(2, 6),        # NumberOfTimes90DaysLate - many
            rng.integers(0, 2),        # NumberRealEstateLoansOrLines - none/few
            rng.integers(2, 5),        # NumberOfTime60_89DaysPastDueNotWorse - many
            rng.integers(2, 5),        # NumberOfDependents - several
        ], dtype=float)

        # Create variations around the template with small noise
        for i in range(ring_size):
            noise = rng.normal(0, 0.05, len(template))
            member = template * (1 + noise)
            # Clip to valid ranges
            member[0] = np.clip(member[0], 0, 1)        # RevolvingUtilization
            member[1] = np.clip(member[1], 18, 100)      # age
            member[2] = np.clip(round(member[2]), 0, 10)  # 30-59 days late
            member[3] = np.clip(member[3], 0, 2)          # DebtRatio
            member[4] = np.clip(member[4], 1000, 50000)   # MonthlyIncome
            member[5] = np.clip(round(member[5]), 0, 30)  # Open credit lines
            member[6] = np.clip(round(member[6]), 0, 10)  # 90 days late
            member[7] = np.clip(round(member[7]), 0, 10)  # Real estate loans
            member[8] = np.clip(round(member[8]), 0, 10)  # 60-89 days late
            member[9] = np.clip(round(member[9]), 0, 10)  # Dependents

            idx = ring_start + i
            features[idx] = member
            labels[idx] = 1  # Mark as default/fraud

        ring_start += ring_size
        rings_planted += 1

    df_out = pd.DataFrame(features, columns=FEATURE_NAMES)
    return df_out, labels, rings_planted


def generate_fraud_dataset(
    n_records: int = 5000,
    n_fraud_rings: int = 8,
    fraud_rate: float = 0.07,
    random_seed: int = 42,
    output_path: str = None,
) -> str:
    """Generate a complete synthetic dataset with fraud rings for SNN detection.

    Args:
        n_records: Total number of records to generate
        n_fraud_rings: Number of fraud rings to plant
        fraud_rate: Target fraud/default rate (ring members + random defaults)
        random_seed: Random seed for reproducibility
        output_path: Path to save CSV. Defaults to data/cs-training.csv

    Returns:
        Path to the saved CSV file
    """
    rng = np.random.default_rng(random_seed)

    # Generate base records
    df = generate_base_records(n_records, rng)

    # Create labels - start with population-level default rate
    n_defaults = int(n_records * fraud_rate)
    labels = np.zeros(n_records, dtype=int)

    # Random defaults (non-ring)
    n_ring_defaults = n_fraud_rings * 8  # approximate ring member count
    n_random_defaults = max(0, n_defaults - n_ring_defaults)
    random_default_indices = rng.choice(
        np.arange(n_fraud_rings * 15, n_records),  # avoid ring zone
        size=min(n_random_defaults, n_records - n_fraud_rings * 15),
        replace=False,
    )
    labels[random_default_indices] = 1

    # Plant fraud rings in the first portion of the dataset
    df, labels, rings_planted = plant_fraud_rings(
        df, labels, n_rings=n_fraud_rings,
        ring_size_range=(4, 12), rng=rng
    )

    # Add target column
    df["SeriousDlqin2yrs"] = labels

    # Save
    if output_path is None:
        output_path = os.path.join(
            Path(__file__).parent, "data", "cs-training.csv"
        )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {n_records} records with {rings_planted} fraud rings "
          f"({labels.sum()} defaults, {labels.sum()/n_records:.1%} default rate)")
    print(f"Saved to {output_path}")
    return output_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic fraud data")
    parser.add_argument("--n-records", type=int, default=5000, help="Number of records")
    parser.add_argument("--n-rings", type=int, default=8, help="Number of fraud rings")
    parser.add_argument("--fraud-rate", type=float, default=0.07, help="Target fraud rate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path")
    args = parser.parse_args()

    generate_fraud_dataset(
        n_records=args.n_records,
        n_fraud_rings=args.n_rings,
        fraud_rate=args.fraud_rate,
        random_seed=args.seed,
        output_path=args.output,
    )
