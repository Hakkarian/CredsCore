"""Simple synthetic data generator without CTGAN dependency."""
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SimpleSyntheticEngine:
    """Lightweight synthetic data generator using statistical sampling."""

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

    def __init__(self):
        self.is_trained = True  # Always ready
        self.created_at = datetime.now(timezone.utc)

    def generate(self, num_records: int, random_seed: int = None) -> pd.DataFrame:
        """Generate synthetic records using statistical distributions.
        
        Each call without a seed produces different data.
        Only specify a seed for reproducibility.
        """
        rng = np.random.default_rng(random_seed)

        data = {
            "RevolvingUtilizationOfUnsecuredLines": np.clip(
                rng.beta(2, 5, num_records), 0, 1
            ),
            "age": rng.integers(18, 65, num_records),
            "NumberOfTime30_59DaysPastDueNotWorse": rng.poisson(
                0.5, num_records
            ).clip(0, 10),
            "DebtRatio": np.clip(rng.gamma(2, 0.3, num_records), 0, 2),
            "MonthlyIncome": rng.lognormal(8, 0.5, num_records).clip(1000, 50000),
            "NumberOfOpenCreditLinesAndLoans": rng.poisson(8, num_records).clip(
                0, 30
            ),
            "NumberOfTimes90DaysLate": rng.poisson(0.1, num_records).clip(0, 10),
            "NumberRealEstateLoansOrLines": rng.poisson(1, num_records).clip(0, 10),
            "NumberOfTime60_89DaysPastDueNotWorse": rng.poisson(
                0.2, num_records
            ).clip(0, 10),
            "NumberOfDependents": rng.poisson(1, num_records).clip(0, 10),
        }

        logger.info(f"Generated {num_records} synthetic records (simple mode, seed={random_seed})")
        return pd.DataFrame(data)


def get_simple_engine() -> SimpleSyntheticEngine:
    """Get simple engine instance."""
    return SimpleSyntheticEngine()
